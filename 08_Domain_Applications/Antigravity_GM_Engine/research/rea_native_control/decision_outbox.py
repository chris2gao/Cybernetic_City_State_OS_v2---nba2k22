"""Standardized Decision Outbox for NBA2K22 REA.
Lightweight SQLite-backed append-only decision container supporting incremental submissions,
superseding, dependency/collision detection, immutable sealing, and closed-loop receipt feedback.
"""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

_RESEARCH_DIR = Path(__file__).resolve().parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

from role_batches import (
    ActionIntent,
    BatchContext,
    RoleActionBatch,
    digest,
    encode
)
from role_capabilities import RoleCapabilityProfile, RoleCapabilityService


def _derive_resource_key(action_id: str, parameters: Dict[str, Any]) -> str:
    """Derives canonical target resource key to detect resource collisions."""
    if "team_id" in parameters and "player_id" in parameters and "field_id" in parameters:
        return f"team/{parameters['team_id']}/player/{parameters['player_id']}/{parameters['field_id']}"
    if "player_id" in parameters and "field_id" in parameters:
        return f"player/{parameters['player_id']}/{parameters['field_id']}"
    if "player_id" in parameters and "slot_values" in parameters:
        return f"player/{parameters['player_id']}/playtypes"
    if "team_id" in parameters and "field_name" in parameters:
        return f"team/{parameters['team_id']}/coach/{parameters['field_name']}"
    if "team_id" in parameters and "coach_id" in parameters:
        return f"team/{parameters['team_id']}/coach/{parameters['coach_id']}"
    if "team_id" in parameters and "date" in parameters:
        return f"team/{parameters['team_id']}/training/{parameters['date']}"
    if "team_a" in parameters and "team_b" in parameters:
        p_all = sorted(parameters.get("players_a", []) + parameters.get("players_b", []))
        return f"trade/{parameters['team_a']}_{parameters['team_b']}/{','.join(str(x) for x in p_all)}"
    # Generic fallback
    ident = parameters.get("player_id") or parameters.get("player_uid") or parameters.get("team_id") or "global"
    return f"{action_id}/{ident}"


class DecisionOutbox:
    """SQLite-backed Decision Outbox container."""

    def __init__(self, db_path: Path | str, capability_service: Optional[RoleCapabilityService] = None):
        self.db_path = Path(db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.capability_service = capability_service
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS decision_cycles (
                cycle_id TEXT PRIMARY KEY,
                context_json TEXT NOT NULL,
                context_digest TEXT NOT NULL,
                status TEXT NOT NULL,
                revision INTEGER NOT NULL DEFAULT 0,
                sealed_batch_id TEXT,
                sealed_digest TEXT,
                created_at TEXT NOT NULL,
                sealed_at TEXT,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS decision_intents (
                intent_id TEXT PRIMARY KEY,
                cycle_id TEXT NOT NULL,
                issuer_uid TEXT NOT NULL,
                role_type TEXT NOT NULL,
                action_id TEXT NOT NULL,
                parameters_json TEXT NOT NULL,
                dependencies_json TEXT NOT NULL DEFAULT '[]',
                agreement_ref TEXT,
                source_evidence_ref TEXT NOT NULL DEFAULT '',
                decision_reason TEXT NOT NULL DEFAULT '',
                target_resource_key TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'DRAFT',
                supersedes_intent_id TEXT,
                outcome_reason TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(cycle_id) REFERENCES decision_cycles(cycle_id)
            );

            CREATE TABLE IF NOT EXISTS outbox_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id TEXT NOT NULL,
                intent_id TEXT,
                event_type TEXT NOT NULL,
                prev_state TEXT,
                new_state TEXT,
                revision INTEGER NOT NULL,
                payload_json TEXT NOT NULL DEFAULT '{}',
                timestamp TEXT NOT NULL,
                FOREIGN KEY(cycle_id) REFERENCES decision_cycles(cycle_id)
            );

            CREATE INDEX IF NOT EXISTS idx_intents_cycle ON decision_intents(cycle_id);
            CREATE INDEX IF NOT EXISTS idx_intents_resource ON decision_intents(cycle_id, target_resource_key);
            CREATE INDEX IF NOT EXISTS idx_intents_status ON decision_intents(cycle_id, status);
            CREATE INDEX IF NOT EXISTS idx_events_cycle ON outbox_events(cycle_id);
            """)

    def open_cycle(self, cycle_id: str, context: BatchContext) -> Dict[str, Any]:
        """Opens a new decision cycle bound to an immutable BatchContext."""
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        ctx_dict = asdict(context)
        ctx_json = encode(ctx_dict)
        ctx_digest = digest(ctx_dict)

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM decision_cycles WHERE cycle_id = ?", (cycle_id,))
            row = cur.fetchone()
            if row:
                if row["context_digest"] != ctx_digest:
                    raise ValueError(f"CYCLE_ALREADY_EXISTS_WITH_DIFFERENT_CONTEXT: {cycle_id}")
                return dict(row)

            cur.execute("""
            INSERT INTO decision_cycles (
                cycle_id, context_json, context_digest, status, revision, created_at, updated_at
            ) VALUES (?, ?, ?, 'COLLECTING', 1, ?, ?)
            """, (cycle_id, ctx_json, ctx_digest, now, now))

            cur.execute("""
            INSERT INTO outbox_events (
                cycle_id, intent_id, event_type, prev_state, new_state, revision, payload_json, timestamp
            ) VALUES (?, NULL, 'CYCLE_OPENED', NULL, 'COLLECTING', 1, ?, ?)
            """, (cycle_id, ctx_json, now))
            conn.commit()

        return {
            "cycle_id": cycle_id,
            "context_digest": ctx_digest,
            "status": "COLLECTING",
            "revision": 1,
            "created_at": now
        }

    def get_cycle(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM decision_cycles WHERE cycle_id = ?", (cycle_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def add_intent(
        self,
        cycle_id: str,
        intent: ActionIntent,
        profile: RoleCapabilityProfile,
        phase_grants: Set[Tuple[str, str]],
        *,
        source_evidence_ref: str = "",
        decision_reason: str = ""
    ) -> ActionIntent:
        """Adds an ActionIntent submitted by an authenticated host profile to the outbox."""
        # 1. Host identity verification
        if intent.issuer_uid != profile.actor_uid:
            raise PermissionError(f"SUBMISSION_ISSUER_DOES_NOT_MATCH_AUTHENTICATED_PROFILE: {intent.issuer_uid} != {profile.actor_uid}")

        cycle = self.get_cycle(cycle_id)
        if not cycle:
            raise ValueError(f"CYCLE_NOT_FOUND: {cycle_id}")
        if cycle["status"] not in ("COLLECTING", "CONFLICTED"):
            raise ValueError(f"CANNOT_ADD_INTENT_TO_SEALED_CYCLE: cycle {cycle_id} is {cycle['status']}")

        # 2. Context binding verification
        ctx = json.loads(cycle["context_json"])
        for k in ("world_id", "save_instance_id", "generation_id", "season_id", "phase", "snapshot_ref"):
            if getattr(profile, k) != ctx.get(k):
                raise ValueError(f"ROLE_CONTEXT_MISMATCH: profile {k} '{getattr(profile, k)}' != cycle context '{ctx.get(k)}'")

        # 3. Role capability verification (if service provided)
        if self.capability_service:
            if intent.action_id not in profile.allowed_actions:
                raise PermissionError(f"ROLE_ACTION_NOT_GRANTED: {intent.action_id} not in profile allowed actions")
            allowed_roles = self.capability_service.allowed_roles(intent.action_id)
            if profile.role_type not in allowed_roles:
                raise PermissionError(f"ROLE_TYPE_NOT_ALLOWED: {profile.role_type} not in {allowed_roles}")

        # 4. Phase applicability verification
        if (intent.issuer_uid, intent.action_id) not in phase_grants:
            raise PermissionError(f"PHASE_APPLICABILITY_NOT_ATTESTED: {(intent.issuer_uid, intent.action_id)} not in phase grants")

        # 5. Scope verification (team / player)
        params = intent.parameters
        if "team_id" in params and params["team_id"] not in profile.team_scope and profile.role_type != "WORLD_ADMIN":
            raise PermissionError(f"TEAM_SCOPE_VIOLATION: team {params['team_id']} not in profile scope {profile.team_scope}")
        if profile.player_scope:
            target_pid = params.get("player_id") or params.get("player_uid")
            if target_pid is not None and target_pid not in profile.player_scope and profile.role_type != "WORLD_ADMIN":
                raise PermissionError(f"PLAYER_SCOPE_VIOLATION: player {target_pid} not in profile scope {profile.player_scope}")

        resource_key = _derive_resource_key(intent.action_id, params)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        with self._get_connection() as conn:
            cur = conn.cursor()
            # Check for duplicate intent_id
            cur.execute("SELECT * FROM decision_intents WHERE intent_id = ?", (intent.intent_id,))
            existing = cur.fetchone()
            if existing:
                if existing["parameters_json"] == intent.parameters_json and existing["action_id"] == intent.action_id:
                    # Idempotent re-submission
                    return intent
                raise ValueError(f"INTENT_ID_REUSED_WITH_DIFFERENT_PAYLOAD: {intent.intent_id}")

            new_rev = cycle["revision"] + 1
            cur.execute("""
            INSERT INTO decision_intents (
                intent_id, cycle_id, issuer_uid, role_type, action_id, parameters_json,
                dependencies_json, agreement_ref, source_evidence_ref, decision_reason,
                target_resource_key, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DRAFT', ?, ?)
            """, (
                intent.intent_id,
                cycle_id,
                intent.issuer_uid,
                profile.role_type,
                intent.action_id,
                intent.parameters_json,
                json.dumps(list(intent.dependencies)),
                intent.agreement_ref,
                source_evidence_ref,
                decision_reason,
                resource_key,
                now,
                now
            ))

            cur.execute("""
            UPDATE decision_cycles SET revision = ?, status = 'COLLECTING', updated_at = ? WHERE cycle_id = ?
            """, (new_rev, now, cycle_id))

            cur.execute("""
            INSERT INTO outbox_events (
                cycle_id, intent_id, event_type, prev_state, new_state, revision, payload_json, timestamp
            ) VALUES (?, ?, 'INTENT_ADDED', NULL, 'DRAFT', ?, ?, ?)
            """, (
                cycle_id,
                intent.intent_id,
                new_rev,
                json.dumps({
                    "action_id": intent.action_id,
                    "target_resource_key": resource_key,
                    "issuer_uid": intent.issuer_uid
                }),
                now
            ))
            conn.commit()

        return intent

    def supersede_intent(
        self,
        cycle_id: str,
        old_intent_id: str,
        new_intent: ActionIntent,
        profile: RoleCapabilityProfile,
        phase_grants: Set[Tuple[str, str]],
        *,
        decision_reason: str = ""
    ) -> ActionIntent:
        """Supersedes an existing DRAFT intent with a new one in the same unsealed cycle."""
        cycle = self.get_cycle(cycle_id)
        if not cycle:
            raise ValueError(f"CYCLE_NOT_FOUND: {cycle_id}")
        if cycle["status"] not in ("COLLECTING", "CONFLICTED"):
            raise ValueError(f"CANNOT_SUPERSEDE_IN_SEALED_CYCLE: cycle {cycle_id} is {cycle['status']}")

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM decision_intents WHERE intent_id = ? AND cycle_id = ?", (old_intent_id, cycle_id))
            old_row = cur.fetchone()
            if not old_row:
                raise ValueError(f"OLD_INTENT_NOT_FOUND: {old_intent_id}")
            if old_row["status"] != "DRAFT":
                raise ValueError(f"CANNOT_SUPERSEDE_NON_DRAFT_INTENT: intent {old_intent_id} has status {old_row['status']}")

            # Issuer check
            if old_row["issuer_uid"] != profile.actor_uid and profile.role_type != "WORLD_ADMIN":
                raise PermissionError("CANNOT_SUPERSEDE_ANOTHER_ISSUERS_INTENT")

            # Validate and add new intent
            new_rev = cycle["revision"] + 1
            resource_key = _derive_resource_key(new_intent.action_id, new_intent.parameters)

            cur.execute("""
            UPDATE decision_intents SET status = 'SUPERSEDED', updated_at = ? WHERE intent_id = ?
            """, (now, old_intent_id))

            cur.execute("""
            INSERT INTO decision_intents (
                intent_id, cycle_id, issuer_uid, role_type, action_id, parameters_json,
                dependencies_json, agreement_ref, source_evidence_ref, decision_reason,
                target_resource_key, status, supersedes_intent_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DRAFT', ?, ?, ?)
            """, (
                new_intent.intent_id,
                cycle_id,
                new_intent.issuer_uid,
                profile.role_type,
                new_intent.action_id,
                new_intent.parameters_json,
                json.dumps(list(new_intent.dependencies)),
                new_intent.agreement_ref,
                old_row["source_evidence_ref"],
                decision_reason or f"Supersedes {old_intent_id}",
                resource_key,
                old_intent_id,
                now,
                now
            ))

            cur.execute("UPDATE decision_cycles SET revision = ?, status = 'COLLECTING', updated_at = ? WHERE cycle_id = ?", (new_rev, now, cycle_id))

            cur.execute("""
            INSERT INTO outbox_events (
                cycle_id, intent_id, event_type, prev_state, new_state, revision, payload_json, timestamp
            ) VALUES (?, ?, 'INTENT_SUPERSEDED', 'DRAFT', 'SUPERSEDED', ?, ?, ?)
            """, (cycle_id, old_intent_id, new_rev, json.dumps({"superseded_by": new_intent.intent_id}), now))

            cur.execute("""
            INSERT INTO outbox_events (
                cycle_id, intent_id, event_type, prev_state, new_state, revision, payload_json, timestamp
            ) VALUES (?, ?, 'INTENT_ADDED', NULL, 'DRAFT', ?, ?, ?)
            """, (cycle_id, new_intent.intent_id, new_rev, json.dumps({"supersedes": old_intent_id}), now))

            conn.commit()

        return new_intent

    def cancel_intent(
        self,
        cycle_id: str,
        intent_id: str,
        profile: RoleCapabilityProfile,
        *,
        reason: str = ""
    ):
        """Cancels a DRAFT intent prior to sealing."""
        cycle = self.get_cycle(cycle_id)
        if not cycle:
            raise ValueError(f"CYCLE_NOT_FOUND: {cycle_id}")
        if cycle["status"] not in ("COLLECTING", "CONFLICTED"):
            raise ValueError(f"CANNOT_CANCEL_IN_SEALED_CYCLE: cycle {cycle_id} is {cycle['status']}")

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM decision_intents WHERE intent_id = ? AND cycle_id = ?", (intent_id, cycle_id))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"INTENT_NOT_FOUND: {intent_id}")
            if row["status"] != "DRAFT":
                raise ValueError(f"CANNOT_CANCEL_NON_DRAFT_INTENT: intent {intent_id} has status {row['status']}")
            if row["issuer_uid"] != profile.actor_uid and profile.role_type != "WORLD_ADMIN":
                raise PermissionError("CANNOT_CANCEL_ANOTHER_ISSUERS_INTENT")

            new_rev = cycle["revision"] + 1
            cur.execute("UPDATE decision_intents SET status = 'CANCELLED', updated_at = ?, outcome_reason = ? WHERE intent_id = ?", (now, reason, intent_id))
            cur.execute("UPDATE decision_cycles SET revision = ?, status = 'COLLECTING', updated_at = ? WHERE cycle_id = ?", (new_rev, now, cycle_id))
            cur.execute("""
            INSERT INTO outbox_events (
                cycle_id, intent_id, event_type, prev_state, new_state, revision, payload_json, timestamp
            ) VALUES (?, ?, 'INTENT_CANCELLED', 'DRAFT', 'CANCELLED', ?, ?, ?)
            """, (cycle_id, intent_id, new_rev, json.dumps({"reason": reason}), now))
            conn.commit()

    def list_intents(self, cycle_id: str, *, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            if status:
                cur.execute("SELECT * FROM decision_intents WHERE cycle_id = ? AND status = ? ORDER BY created_at ASC", (cycle_id, status))
            else:
                cur.execute("SELECT * FROM decision_intents WHERE cycle_id = ? ORDER BY created_at ASC", (cycle_id,))
            return [dict(r) for r in cur.fetchall()]

    def inspect_conflicts_and_dependencies(self, cycle_id: str) -> Dict[str, Any]:
        """Detects resource target collisions, missing dependencies, and dependency cycles."""
        intents = self.list_intents(cycle_id, status="DRAFT")
        active_ids = {it["intent_id"] for it in intents}

        # 1. Resource collision detection
        resource_map: Dict[str, List[Dict[str, Any]]] = {}
        for it in intents:
            rkey = it["target_resource_key"]
            if not rkey:
                continue
            resource_map.setdefault(rkey, []).append(it)

        conflicts = []
        aliases = []
        for rkey, group in resource_map.items():
            if len(group) > 1:
                # Compare requested values
                values = set()
                for it in group:
                    p = json.loads(it["parameters_json"])
                    val = p.get("value") or p.get("target_value") or p.get("target_tendency") or p.get("target_minutes") or p.get("setting_value")
                    values.add(str(val))
                if len(values) > 1:
                    conflicts.append({
                        "resource_key": rkey,
                        "conflict_type": "CONTRADICTORY_VALUES",
                        "intent_ids": [it["intent_id"] for it in group],
                        "values": list(values)
                    })
                else:
                    aliases.append({
                        "resource_key": rkey,
                        "intent_ids": [it["intent_id"] for it in group]
                    })

        # 2. Dependency validation & cycle detection
        missing_deps = []
        dep_graph: Dict[str, List[str]] = {}
        for it in intents:
            iid = it["intent_id"]
            deps = json.loads(it["dependencies_json"])
            dep_graph[iid] = deps
            for d in deps:
                if d not in active_ids:
                    missing_deps.append({"intent_id": iid, "missing_dependency": d})

        # Topological cycle check
        visited: Dict[str, int] = {}  # 0: visiting, 1: visited
        cycles = []

        def dfs(node: str, path: List[str]):
            visited[node] = 0
            path.append(node)
            for neighbor in dep_graph.get(node, []):
                if neighbor in dep_graph:
                    if visited.get(neighbor) == 0:
                        cycle_path = path[path.index(neighbor):] + [neighbor]
                        cycles.append(cycle_path)
                    elif visited.get(neighbor) is None:
                        dfs(neighbor, path)
            path.pop()
            visited[node] = 1

        for iid in list(dep_graph.keys()):
            if visited.get(iid) is None:
                dfs(iid, [])

        has_blocking = (len(conflicts) > 0 or len(missing_deps) > 0 or len(cycles) > 0)
        return {
            "has_blocking_issues": has_blocking,
            "conflicts": conflicts,
            "aliases": aliases,
            "missing_dependencies": missing_deps,
            "dependency_cycles": cycles
        }

    def seal_cycle(
        self,
        cycle_id: str,
        *,
        aggregate_batch_id: str,
        expected_revision: Optional[int] = None
    ) -> RoleActionBatch:
        """Seals the active decision cycle into an immutable RoleActionBatch."""
        cycle = self.get_cycle(cycle_id)
        if not cycle:
            raise ValueError(f"CYCLE_NOT_FOUND: {cycle_id}")

        # Idempotent seal check
        if cycle["status"] == "SEALED":
            if cycle["sealed_batch_id"] == aggregate_batch_id:
                # Reconstruct and return existing sealed batch
                ctx = BatchContext(**json.loads(cycle["context_json"]))
                intents_rows = self.list_intents(cycle_id, status="SEALED")
                action_intents = tuple(
                    ActionIntent.decided(
                        r["intent_id"],
                        r["issuer_uid"],
                        r["action_id"],
                        json.loads(r["parameters_json"]),
                        dependencies=tuple(json.loads(r["dependencies_json"])),
                        agreement_ref=r["agreement_ref"]
                    )
                    for r in intents_rows
                )
                return RoleActionBatch(aggregate_batch_id, ctx, action_intents)
            raise ValueError(f"CYCLE_ALREADY_SEALED_WITH_DIFFERENT_BATCH_ID: {cycle['sealed_batch_id']} != {aggregate_batch_id}")

        if cycle["status"] != "COLLECTING":
            raise ValueError(f"CANNOT_SEAL_CYCLE_IN_STATE: {cycle['status']}")

        if expected_revision is not None and cycle["revision"] != expected_revision:
            raise ValueError(f"REVISION_CAS_MISMATCH: expected {expected_revision}, got {cycle['revision']}")

        # Inspect conflicts
        analysis = self.inspect_conflicts_and_dependencies(cycle_id)
        if analysis["has_blocking_issues"]:
            with self._get_connection() as conn:
                conn.execute("UPDATE decision_cycles SET status = 'CONFLICTED' WHERE cycle_id = ?", (cycle_id,))
                conn.commit()
            raise ValueError(f"CYCLE_HAS_BLOCKING_CONFLICTS: {analysis}")

        draft_rows = self.list_intents(cycle_id, status="DRAFT")
        if not draft_rows:
            raise ValueError(f"CANNOT_SEAL_EMPTY_CYCLE: no active DRAFT intents in {cycle_id}")

        ctx = BatchContext(**json.loads(cycle["context_json"]))
        action_intents = tuple(
            ActionIntent.decided(
                r["intent_id"],
                r["issuer_uid"],
                r["action_id"],
                json.loads(r["parameters_json"]),
                dependencies=tuple(json.loads(r["dependencies_json"])),
                agreement_ref=r["agreement_ref"]
            )
            for r in draft_rows
        )
        sealed_batch = RoleActionBatch(aggregate_batch_id, ctx, action_intents)
        sealed_digest_str = digest({
            "batch_id": aggregate_batch_id,
            "context": asdict(ctx),
            "intents": [asdict(i) for i in action_intents]
        })

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        new_rev = cycle["revision"] + 1

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            UPDATE decision_cycles SET
                status = 'SEALED',
                sealed_batch_id = ?,
                sealed_digest = ?,
                sealed_at = ?,
                revision = ?,
                updated_at = ?
            WHERE cycle_id = ?
            """, (aggregate_batch_id, sealed_digest_str, now, new_rev, now, cycle_id))

            cur.execute("""
            UPDATE decision_intents SET status = 'SEALED', updated_at = ? WHERE cycle_id = ? AND status = 'DRAFT'
            """, (now, cycle_id))

            cur.execute("""
            INSERT INTO outbox_events (
                cycle_id, intent_id, event_type, prev_state, new_state, revision, payload_json, timestamp
            ) VALUES (?, NULL, 'CYCLE_SEALED', 'COLLECTING', 'SEALED', ?, ?, ?)
            """, (
                cycle_id,
                new_rev,
                json.dumps({
                    "sealed_batch_id": aggregate_batch_id,
                    "sealed_digest": sealed_digest_str,
                    "sealed_intents_count": len(action_intents)
                }),
                now
            ))
            conn.commit()

        return sealed_batch

    def record_execution_receipts(
        self,
        cycle_id: str,
        receipts: List[Dict[str, Any]],
        *,
        evidence_ref: str = ""
    ) -> Dict[str, Any]:
        """Updates decision outbox items with execution receipts and sets cycle completion."""
        cycle = self.get_cycle(cycle_id)
        if not cycle:
            raise ValueError(f"CYCLE_NOT_FOUND: {cycle_id}")

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        updated_count = 0
        has_unknown = False
        has_failure = False

        with self._get_connection() as conn:
            cur = conn.cursor()
            for r in receipts:
                iid = r.get("intent_id")
                outcome = r.get("outcome", "UNKNOWN")
                reason = r.get("reason", "")

                # Map outcome
                if outcome in ("SUCCESS", "SUCCESS_APPLIED"):
                    status = "SUCCESS"
                elif outcome in ("UNCHANGED_ALREADY_TARGET", "NOOP", "REUSED_HISTORICAL_RECEIPT"):
                    status = "NOOP"
                elif "UNKNOWN" in outcome:
                    status = "UNKNOWN"
                    has_unknown = True
                elif outcome in ("NOT_EXECUTED", "BLOCKED_BY_PRIOR_UNKNOWN_CLAIM", "UNSUPPORTED_OR_EXTERNAL"):
                    status = "NOT_EXECUTED"
                else:
                    status = "FAILED"
                    has_failure = True

                cur.execute("""
                UPDATE decision_intents SET
                    status = ?,
                    outcome_reason = ?,
                    updated_at = ?
                WHERE cycle_id = ? AND intent_id = ?
                """, (status, reason or outcome, now, cycle_id, iid))
                if cur.rowcount > 0:
                    updated_count += 1

            new_rev = cycle["revision"] + 1
            new_cycle_status = (
                "UNKNOWN_LOCKED" if has_unknown
                else "STOPPED_PARTIAL" if has_failure
                else "COMPLETED"
            )
            cur.execute("""
            UPDATE decision_cycles SET status = ?, revision = ?, updated_at = ? WHERE cycle_id = ?
            """, (new_cycle_status, new_rev, now, cycle_id))

            cur.execute("""
            INSERT INTO outbox_events (
                cycle_id, intent_id, event_type, prev_state, new_state, revision, payload_json, timestamp
            ) VALUES (?, NULL, 'RECEIPTS_ATTACHED', 'SEALED', ?, ?, ?, ?)
            """, (
                cycle_id,
                new_cycle_status,
                new_rev,
                json.dumps({
                    "receipts_processed": len(receipts),
                    "intents_updated": updated_count,
                    "evidence_ref": evidence_ref,
                    "has_unknown": has_unknown,
                    "has_failure": has_failure
                }),
                now
            ))
            conn.commit()

        return {
            "cycle_id": cycle_id,
            "status": new_cycle_status,
            "receipts_processed": len(receipts),
            "intents_updated": updated_count
        }

    def get_outcome_summary(self, cycle_id: str) -> Dict[str, Any]:
        """Provides concise outcome summary and exception list for next round of decision making."""
        cycle = self.get_cycle(cycle_id)
        if not cycle:
            raise ValueError(f"CYCLE_NOT_FOUND: {cycle_id}")

        intents = self.list_intents(cycle_id)
        status_counts: Dict[str, int] = {}
        exceptions = []

        for it in intents:
            st = it["status"]
            status_counts[st] = status_counts.get(st, 0) + 1
            if st in ("FAILED", "UNKNOWN", "NOT_EXECUTED", "CANCELLED"):
                exceptions.append({
                    "intent_id": it["intent_id"],
                    "issuer_uid": it["issuer_uid"],
                    "action_id": it["action_id"],
                    "status": st,
                    "reason": it["outcome_reason"]
                })

        return {
            "cycle_id": cycle_id,
            "cycle_status": cycle["status"],
            "sealed_batch_id": cycle["sealed_batch_id"],
            "sealed_digest": cycle["sealed_digest"],
            "total_intents": len(intents),
            "status_breakdown": status_counts,
            "all_succeeded_or_noop": (status_counts.get("SUCCESS", 0) + status_counts.get("NOOP", 0) == len(intents)),
            "exception_count": len(exceptions),
            "exceptions": exceptions
        }
