"""Standardized Decision Outbox for NBA2K22 REA.
Lightweight SQLite-backed append-only decision container supporting incremental submissions,
superseding, dependency/collision detection, immutable sealing, and closed-loop receipt feedback.
"""
from dataclasses import asdict
from contextlib import closing
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


_PLAYER_STAT_ACTIONS = {
    "PLAYER.EDIT.TENDENCY_BATCH", "PLAYER_PATCH_TENDENCIES",
    "PLAYER.EDIT.ATTR_BATCH", "PLAYER_PATCH_ATTRIBUTES",
}


def _native_player_field(uid, field):
    if type(uid) is str and uid.isascii() and uid.isdecimal() and len(uid) <= 5:
        uid = int(uid)
    if (type(uid) is not int or not 0 < uid < 65535 or not isinstance(field, str)
            or not field.isascii() or not field.replace("_", "").isalnum()):
        raise ValueError("Invalid Native player UID or field")
    return ("native-player-field", uid, field.upper())


def _execution_resources(row):
    """Decode physical targets from the immutable intent, including legacy rows."""
    if row["action_id"].upper() not in _PLAYER_STAT_ACTIONS:
        return {("outbox", row["target_resource_key"])}
    params = json.loads(row["parameters_json"])
    if not isinstance(params, dict):
        raise ValueError("Missing Native player parameters")
    uid = params.get("player_id", params.get("player_uid"))
    if "player_id" in params and "player_uid" in params:
        if _native_player_field(uid, "ID") != _native_player_field(params["player_uid"], "ID"):
            raise ValueError("Conflicting Native player identifiers")
    maps = [params[key] for key in ("values", "tendency_map", "attribute_map") if key in params]
    if "field_id" in params and "value" in params:
        if maps:
            raise ValueError("Mixed direct and map Native field encodings")
        fields = [params["field_id"]]
    elif len(maps) == 1 and isinstance(maps[0], dict) and maps[0]:
        fields = list(maps[0])
    else:
        raise ValueError("Ambiguous Native player field encoding")
    resources = {_native_player_field(uid, field) for field in fields}
    if len(resources) != len(fields):
        raise ValueError("Duplicate Native player fields")
    return resources


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
        with closing(self._get_connection()) as conn, conn:
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

            CREATE TABLE IF NOT EXISTS test_calendar_claims (
                plan_digest TEXT PRIMARY KEY,
                world_id TEXT NOT NULL,
                save_instance_id TEXT NOT NULL,
                epoch TEXT NOT NULL,
                start_day TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('CLAIMED','UNKNOWN','VERIFIED_IN_MEMORY','NOT_EXECUTED')),
                receipt_ref TEXT
            );
            CREATE TABLE IF NOT EXISTS test_calendar_reconciliations (
                plan_digest TEXT PRIMARY KEY REFERENCES test_calendar_claims(plan_digest),
                prior_receipt_ref TEXT NOT NULL,
                proof_ref TEXT NOT NULL,
                disposition TEXT NOT NULL CHECK(disposition IN
                    ('INTERRUPTED_NO_CALENDAR_EFFECT','HUMAN_ADVANCED_PAST_REQUEST'))
            );
            DROP INDEX IF EXISTS idx_calendar_scene_once;
            CREATE UNIQUE INDEX IF NOT EXISTS idx_calendar_active_scene_once
                ON test_calendar_claims(save_instance_id, epoch, start_day)
                WHERE status IN ('CLAIMED','VERIFIED_IN_MEMORY');
            """)

    def claim_test_calendar(self, plan_digest, world_id, save_instance_id, epoch, start_day):
        """Fence one test-only calendar attempt against both calendar and S4 work."""
        with closing(self._get_connection()) as conn, conn:
            conn.execute("BEGIN IMMEDIATE")
            if conn.execute("""
                SELECT 1 FROM test_calendar_claims c
                 WHERE (world_id = ? OR save_instance_id = ?) AND status IN ('CLAIMED','UNKNOWN')
                   AND NOT EXISTS (SELECT 1 FROM test_calendar_reconciliations r WHERE r.plan_digest=c.plan_digest)
            """, (world_id, save_instance_id)).fetchone():
                raise ValueError("TEST_CALENDAR_UNRESOLVED_NO_REPLAY")
            if conn.execute("""
                SELECT 1 FROM decision_cycles c
                 WHERE (json_extract(c.context_json, '$.world_id') = ?
                        OR json_extract(c.context_json, '$.save_instance_id') = ?)
                   AND (EXISTS (SELECT 1 FROM decision_intents i WHERE i.cycle_id = c.cycle_id
                                AND i.status = 'UNKNOWN')
                        OR (c.status = 'SEALED' AND EXISTS (
                            SELECT 1 FROM outbox_events e WHERE e.cycle_id = c.cycle_id
                              AND e.event_type = 'EXECUTION_CLAIMED')))
            """, (world_id, save_instance_id)).fetchone():
                raise ValueError("S4_EXECUTION_UNRESOLVED")
            conn.execute("""
                INSERT INTO test_calendar_claims (plan_digest, world_id, save_instance_id, epoch, start_day, status)
                VALUES (?, ?, ?, ?, ?, 'CLAIMED')
            """, (plan_digest, world_id, save_instance_id, epoch, start_day))

    def finish_test_calendar(self, plan_digest, status, receipt_ref):
        """Record a terminal observation. UNKNOWN still fences the native scene."""
        if status not in {"UNKNOWN", "VERIFIED_IN_MEMORY", "NOT_EXECUTED"} or not receipt_ref:
            raise ValueError("TEST_CALENDAR_RECEIPT_REQUIRED")
        with closing(self._get_connection()) as conn, conn:
            if conn.execute("""
                UPDATE test_calendar_claims SET status = ?, receipt_ref = ?
                 WHERE plan_digest = ? AND status = 'CLAIMED'
            """, (status, receipt_ref, plan_digest)).rowcount != 1:
                raise ValueError("TEST_CALENDAR_CLAIM_NOT_OPEN")

    def record_test_calendar_no_effect(self, plan_digest, prior_receipt_ref, proof_ref):
        """Keep the consumed request locked and record verified interruption without calendar effect."""
        self._record_test_calendar_reconciliation(plan_digest, prior_receipt_ref, proof_ref,
                                                  "INTERRUPTED_NO_CALENDAR_EFFECT")

    def record_test_calendar_human_advance(self, plan_digest, prior_receipt_ref, proof_ref):
        """Keep the consumed request and separately record Human progression past it."""
        self._record_test_calendar_reconciliation(plan_digest, prior_receipt_ref, proof_ref,
                                                  "HUMAN_ADVANCED_PAST_REQUEST")

    def _record_test_calendar_reconciliation(self, plan_digest, prior_receipt_ref, proof_ref, disposition):
        if not proof_ref or not prior_receipt_ref:
            raise ValueError("TEST_CALENDAR_RECONCILIATION_EVIDENCE_REQUIRED")
        with closing(self._get_connection()) as conn, conn:
            conn.execute("BEGIN IMMEDIATE")
            schema = conn.execute("SELECT sql FROM sqlite_master WHERE name='test_calendar_reconciliations'").fetchone()[0]
            if "HUMAN_ADVANCED_PAST_REQUEST" not in schema:
                conn.execute("""
                    CREATE TABLE test_calendar_reconciliations_v2 (
                        plan_digest TEXT PRIMARY KEY REFERENCES test_calendar_claims(plan_digest),
                        prior_receipt_ref TEXT NOT NULL, proof_ref TEXT NOT NULL,
                        disposition TEXT NOT NULL CHECK(disposition IN
                            ('INTERRUPTED_NO_CALENDAR_EFFECT','HUMAN_ADVANCED_PAST_REQUEST'))
                    )
                """)
                conn.execute("INSERT INTO test_calendar_reconciliations_v2 SELECT * FROM test_calendar_reconciliations")
                conn.execute("DROP TABLE test_calendar_reconciliations")
                conn.execute("ALTER TABLE test_calendar_reconciliations_v2 RENAME TO test_calendar_reconciliations")
            if conn.execute("""
                INSERT INTO test_calendar_reconciliations
                SELECT plan_digest, receipt_ref, ?, ?
                FROM test_calendar_claims WHERE plan_digest=? AND status='UNKNOWN' AND receipt_ref=?
            """, (proof_ref, disposition, plan_digest, prior_receipt_ref)).rowcount != 1:
                raise ValueError("TEST_CALENDAR_UNKNOWN_RECEIPT_CHANGED")

    @staticmethod
    def inspect_test_calendar(db_path, plan_digest):
        """Read a claim without initializing or mutating the Outbox."""
        with closing(sqlite3.connect(Path(db_path).resolve().as_uri() + "?mode=ro", uri=True)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM test_calendar_claims WHERE plan_digest = ?",
                               (plan_digest,)).fetchone()
            return dict(row) if row else None

    def reconcile_rejected_research_setter(self, cycle_id, plan_digest, proof_ref):
        """Retain the execution claim and attach a proved pre-dispatch rejection."""
        if not proof_ref:
            raise ValueError("RESEARCH_SETTER_PROOF_REQUIRED")
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with closing(self._get_connection()) as conn, conn:
            conn.execute("BEGIN IMMEDIATE")
            cycle = conn.execute("SELECT status, revision FROM decision_cycles WHERE cycle_id=?", (cycle_id,)).fetchone()
            claims = conn.execute("""
                SELECT json_extract(payload_json,'$.plan_digest') FROM outbox_events
                WHERE cycle_id=? AND event_type='EXECUTION_CLAIMED'
            """, (cycle_id,)).fetchall()
            intents = conn.execute("SELECT intent_id,status FROM decision_intents WHERE cycle_id=?", (cycle_id,)).fetchall()
            if (not cycle or cycle["status"] != "UNKNOWN_LOCKED" or len(claims) != 1 or claims[0][0] != plan_digest
                    or len(intents) != 1 or intents[0]["status"] != "UNKNOWN"):
                raise ValueError("RESEARCH_SETTER_UNKNOWN_CLAIM_MISMATCH")
            conn.execute("""
                UPDATE decision_intents SET status='NOT_EXECUTED', outcome_reason=?, updated_at=? WHERE cycle_id=?
            """, ("RECONCILED_PLANNER_REJECTED_BEFORE_NATIVE_DISPATCH", now, cycle_id))
            revision = cycle["revision"] + 1
            conn.execute("""
                UPDATE decision_cycles SET status='STOPPED_PARTIAL', revision=?, updated_at=? WHERE cycle_id=?
            """, (revision, now, cycle_id))
            conn.execute("""
                INSERT INTO outbox_events (cycle_id, intent_id, event_type, prev_state, new_state, revision, payload_json, timestamp)
                VALUES (?, ?, 'RECONCILED_NO_NATIVE_DISPATCH', 'UNKNOWN_LOCKED', 'STOPPED_PARTIAL', ?, ?, ?)
            """, (cycle_id, intents[0]["intent_id"], revision,
                  json.dumps({"plan_digest": plan_digest, "proof_ref": proof_ref}), now))

    def open_cycle(self, cycle_id: str, context: BatchContext) -> Dict[str, Any]:
        """Opens a new decision cycle bound to an immutable BatchContext."""
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        ctx_dict = asdict(context)
        ctx_json = encode(ctx_dict)
        ctx_digest = digest(ctx_dict)

        with closing(self._get_connection()) as conn, conn:
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

    def _validate_intent_submission(
        self,
        cycle: Dict[str, Any],
        intent: ActionIntent,
        profile: RoleCapabilityProfile,
        phase_grants: Set[Tuple[str, str]]
    ):
        """Unified host authenticated profile, capability, phase grant, and scope validation."""
        # 1. Host identity verification
        if intent.issuer_uid != profile.actor_uid and profile.role_type != "WORLD_ADMIN":
            raise PermissionError(f"SUBMISSION_ISSUER_DOES_NOT_MATCH_AUTHENTICATED_PROFILE: {intent.issuer_uid} != {profile.actor_uid}")

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
        cycle = self.get_cycle(cycle_id)
        if not cycle:
            raise ValueError(f"CYCLE_NOT_FOUND: {cycle_id}")
        if cycle["status"] not in ("COLLECTING", "CONFLICTED"):
            raise ValueError(f"CANNOT_ADD_INTENT_TO_SEALED_CYCLE: cycle {cycle_id} is {cycle['status']}")

        self._validate_intent_submission(cycle, intent, profile, phase_grants)

        resource_key = _derive_resource_key(intent.action_id, intent.parameters)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("BEGIN IMMEDIATE")
            cur.execute("SELECT revision, status FROM decision_cycles WHERE cycle_id = ?", (cycle_id,))
            c_row = cur.fetchone()
            if not c_row or c_row["status"] not in ("COLLECTING", "CONFLICTED"):
                raise ValueError(f"CANNOT_ADD_INTENT_TO_SEALED_CYCLE: cycle {cycle_id} status changed concurrently")

            # Check for duplicate intent_id
            cur.execute("SELECT * FROM decision_intents WHERE intent_id = ?", (intent.intent_id,))
            existing = cur.fetchone()
            if existing:
                if existing["parameters_json"] == intent.parameters_json and existing["action_id"] == intent.action_id:
                    # Idempotent re-submission
                    return intent
                raise ValueError(f"INTENT_ID_REUSED_WITH_DIFFERENT_PAYLOAD: {intent.intent_id}")

            new_rev = c_row["revision"] + 1
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
            UPDATE decision_cycles SET revision = ?, status = 'COLLECTING', updated_at = ?
            WHERE cycle_id = ? AND status IN ('COLLECTING', 'CONFLICTED') AND revision = ?
            """, (new_rev, now, cycle_id, c_row["revision"]))
            if cur.rowcount == 0:
                raise ValueError("CONCURRENT_MODIFICATION_DETECTED_IN_ADD_INTENT")

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

        # Validate the NEW intent with identical host validation!
        self._validate_intent_submission(cycle, new_intent, profile, phase_grants)

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("BEGIN IMMEDIATE")
            cur.execute("SELECT revision, status FROM decision_cycles WHERE cycle_id = ?", (cycle_id,))
            c_row = cur.fetchone()
            if not c_row or c_row["status"] not in ("COLLECTING", "CONFLICTED"):
                raise ValueError(f"CANNOT_SUPERSEDE_IN_SEALED_CYCLE: cycle {cycle_id} status changed concurrently")

            cur.execute("SELECT * FROM decision_intents WHERE intent_id = ? AND cycle_id = ?", (old_intent_id, cycle_id))
            old_row = cur.fetchone()
            if not old_row:
                raise ValueError(f"OLD_INTENT_NOT_FOUND: {old_intent_id}")
            if old_row["status"] != "DRAFT":
                raise ValueError(f"CANNOT_SUPERSEDE_NON_DRAFT_INTENT: intent {old_intent_id} has status {old_row['status']}")

            # Issuer check: profile must own the old intent
            if old_row["issuer_uid"] != profile.actor_uid and profile.role_type != "WORLD_ADMIN":
                raise PermissionError("CANNOT_SUPERSEDE_ANOTHER_ISSUERS_INTENT")

            new_rev = c_row["revision"] + 1
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

            cur.execute("""
            UPDATE decision_cycles SET revision = ?, status = 'COLLECTING', updated_at = ?
            WHERE cycle_id = ? AND status IN ('COLLECTING', 'CONFLICTED') AND revision = ?
            """, (new_rev, now, cycle_id, c_row["revision"]))
            if cur.rowcount == 0:
                raise ValueError("CONCURRENT_MODIFICATION_DETECTED_IN_SUPERSEDE")

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
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("BEGIN IMMEDIATE")
            cur.execute("SELECT * FROM decision_cycles WHERE cycle_id = ?", (cycle_id,))
            cycle = cur.fetchone()
            if not cycle:
                raise ValueError(f"CYCLE_NOT_FOUND: {cycle_id}")

            # Idempotent seal check
            if cycle["status"] == "SEALED":
                if cycle["sealed_batch_id"] == aggregate_batch_id:
                    # Reconstruct and return existing sealed batch
                    ctx = BatchContext(**json.loads(cycle["context_json"]))
                    cur.execute("SELECT * FROM decision_intents WHERE cycle_id = ? AND status = 'SEALED'", (cycle_id,))
                    intents_rows = cur.fetchall()
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
                cur.execute("UPDATE decision_cycles SET status = 'CONFLICTED' WHERE cycle_id = ?", (cycle_id,))
                conn.commit()
                raise ValueError(f"CYCLE_HAS_BLOCKING_CONFLICTS: {analysis}")

            cur.execute("SELECT * FROM decision_intents WHERE cycle_id = ? AND status = 'DRAFT'", (cycle_id,))
            draft_rows = cur.fetchall()
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

            cur.execute("""
            UPDATE decision_cycles SET
                status = 'SEALED',
                sealed_batch_id = ?,
                sealed_digest = ?,
                sealed_at = ?,
                revision = ?,
                updated_at = ?
            WHERE cycle_id = ? AND status = 'COLLECTING' AND revision = ?
            """, (aggregate_batch_id, sealed_digest_str, now, new_rev, now, cycle_id, cycle["revision"]))
            if cur.rowcount == 0:
                raise ValueError("CONCURRENT_MODIFICATION_DETECTED_DURING_SEAL")

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

    def claim_execution(self, cycle_id: str, plan_digest: str, *, native_items=None) -> None:
        """Reserve a sealed cycle once before dispatch, including across Host restarts."""
        with closing(self._get_connection()) as conn, conn:
            conn.execute("BEGIN IMMEDIATE")
            cycle = conn.execute(
                "SELECT status, revision, context_json FROM decision_cycles WHERE cycle_id = ?", (cycle_id,)
            ).fetchone()
            if not cycle or cycle["status"] != "SEALED":
                raise ValueError("EXECUTION_CLAIM_REQUIRES_SEALED_CYCLE")
            prior = conn.execute(
                "SELECT 1 FROM outbox_events WHERE cycle_id = ? AND event_type = 'EXECUTION_CLAIMED'",
                (cycle_id,),
            ).fetchone()
            if prior:
                raise ValueError("EXECUTION_ALREADY_CLAIMED_NO_REPLAY")
            context = json.loads(cycle["context_json"])
            if conn.execute("""
                SELECT 1 FROM test_calendar_claims c
                 WHERE (world_id = ? OR save_instance_id = ?)
                   AND status IN ('CLAIMED','UNKNOWN')
                   AND NOT EXISTS (SELECT 1 FROM test_calendar_reconciliations r WHERE r.plan_digest=c.plan_digest)
            """, (context["world_id"], context["save_instance_id"])).fetchone():
                raise ValueError("TEST_CALENDAR_UNRESOLVED")
            resources = set()
            for item in conn.execute("""
                SELECT action_id, parameters_json, target_resource_key FROM decision_intents
                 WHERE cycle_id = ? AND status = 'SEALED'
            """, (cycle_id,)):
                item_resources = _execution_resources(item)
                if any(key[0] == "native-player-field" for key in resources & item_resources):
                    raise ValueError("DUPLICATE_NATIVE_EXECUTION_RESOURCE")
                resources.update(item_resources)
            if not resources:
                raise ValueError("EXECUTION_CLAIM_REQUIRES_SEALED_INTENTS")
            if native_items is not None:
                actual = [_native_player_field(item.player_id, item.field_id) for item in native_items]
                if len(actual) != len(resources) or set(actual) != resources:
                    raise ValueError("SEALED_AND_BRIDGED_NATIVE_RESOURCES_DIFFER")
            unresolved = conn.execute("""
                SELECT old.cycle_id, prior.action_id, prior.parameters_json, prior.target_resource_key
                  FROM decision_cycles old
                  LEFT JOIN decision_intents prior ON old.cycle_id = prior.cycle_id
                 WHERE old.cycle_id != ?
                   AND json_extract(old.context_json, '$.world_id') = ?
                   AND json_extract(old.context_json, '$.save_instance_id') = ?
                   AND (prior.status = 'UNKNOWN' OR (old.status = 'SEALED' AND EXISTS (
                       SELECT 1 FROM outbox_events e
                        WHERE e.cycle_id = old.cycle_id AND e.event_type = 'EXECUTION_CLAIMED'
                   )))
            """, (cycle_id, context["world_id"], context["save_instance_id"]))
            for held in unresolved:
                try:
                    held_resources = _execution_resources(held)
                except (AttributeError, TypeError, ValueError) as exc:
                    raise ValueError(
                        f"UNRESOLVED_OUTBOX_RESOURCE_UNDECODABLE: reconcile cycle {held['cycle_id']} before execution"
                    ) from exc
                if resources & held_resources:
                    raise ValueError("EXECUTION_RESOURCE_HELD_BY_UNRESOLVED_OUTBOX_CLAIM")
            conn.execute("""
                INSERT INTO outbox_events
                    (cycle_id, event_type, prev_state, new_state, revision, payload_json, timestamp)
                VALUES (?, 'EXECUTION_CLAIMED', 'SEALED', 'SEALED', ?, ?, ?)
            """, (cycle_id, cycle["revision"], json.dumps({"plan_digest": plan_digest, "resources": sorted(resources)}),
                  time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            conn.commit()

    def record_execution_receipts(
        self,
        cycle_id: str,
        receipts: List[Dict[str, Any]],
        *,
        evidence_ref: str = ""
    ) -> Dict[str, Any]:
        """Updates decision outbox items with execution receipts and sets cycle completion.
        Guarantees:
        - Cycle must be in SEALED status (idempotent if already executed, rejects if unsealed).
        - Receipts cannot be empty.
        - Exact 1-to-1 matching with sealed intents (no unknown, duplicate, or missing intents).
        - Cycle only COMPLETED if all intents are SUCCESS/NOOP; any NOT_EXECUTED or FAILED sets STOPPED_PARTIAL.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("BEGIN IMMEDIATE")
            cur.execute("SELECT * FROM decision_cycles WHERE cycle_id = ?", (cycle_id,))
            cycle = cur.fetchone()
            if not cycle:
                raise ValueError(f"CYCLE_NOT_FOUND: {cycle_id}")

            if cycle["status"] in ("COMPLETED", "STOPPED_PARTIAL", "UNKNOWN_LOCKED"):
                raise ValueError(f"CYCLE_ALREADY_FINISHED: cycle {cycle_id} is already in terminal status '{cycle['status']}'")

            if cycle["status"] != "SEALED":
                raise ValueError(f"CANNOT_RECORD_RECEIPTS_FOR_UNSEALED_CYCLE: cycle {cycle_id} is in status '{cycle['status']}'")

            if not receipts:
                raise ValueError(f"EMPTY_RECEIPTS_REJECTED: cannot record empty execution receipts for cycle {cycle_id}")

            # Verify against sealed intents in this cycle
            cur.execute("SELECT intent_id FROM decision_intents WHERE cycle_id = ? AND status = 'SEALED'", (cycle_id,))
            sealed_rows = cur.fetchall()
            sealed_iids = {r["intent_id"] for r in sealed_rows}

            submitted_iids = set()
            for r in receipts:
                iid = r.get("intent_id")
                if not iid or iid not in sealed_iids:
                    raise ValueError(f"UNKNOWN_INTENT_RECEIPT: intent_id '{iid}' does not belong to sealed cycle {cycle_id}")
                if iid in submitted_iids:
                    raise ValueError(f"DUPLICATE_INTENT_RECEIPT: duplicate receipt for intent_id '{iid}'")
                submitted_iids.add(iid)

            if submitted_iids != sealed_iids:
                missing = sealed_iids - submitted_iids
                raise ValueError(f"INCOMPLETE_RECEIPTS: missing receipts for sealed intents: {sorted(list(missing))}")

            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            updated_count = 0
            has_unknown = False
            has_failure = False
            has_not_executed = False

            for r in receipts:
                iid = r["intent_id"]
                outcome = r.get("outcome", "UNKNOWN")
                reason = r.get("reason", "")

                # Map outcome
                if outcome in ("SUCCESS", "SUCCESS_APPLIED", "VERIFIED_SUCCESS"):
                    status = "SUCCESS"
                elif outcome in ("UNCHANGED_ALREADY_TARGET", "NOOP", "REUSED_HISTORICAL_RECEIPT"):
                    status = "NOOP"
                elif "UNKNOWN" in outcome:
                    status = "UNKNOWN"
                    has_unknown = True
                elif outcome in ("NOT_EXECUTED", "BLOCKED_BY_PRIOR_UNKNOWN_CLAIM", "UNSUPPORTED_OR_EXTERNAL", "PARTIAL_EXECUTION_HALTED", "INCOMPLETE_RECEIPTS"):
                    status = "NOT_EXECUTED"
                    has_not_executed = True
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
            if has_unknown:
                new_cycle_status = "UNKNOWN_LOCKED"
            elif has_failure or has_not_executed:
                new_cycle_status = "STOPPED_PARTIAL"
            else:
                new_cycle_status = "COMPLETED"

            cur.execute("""
            UPDATE decision_cycles SET status = ?, revision = ?, updated_at = ?
            WHERE cycle_id = ? AND status = 'SEALED' AND revision = ?
            """, (new_cycle_status, new_rev, now, cycle_id, cycle["revision"]))
            if cur.rowcount == 0:
                raise ValueError("CONCURRENT_MODIFICATION_DETECTED_IN_RECEIPTS")

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
                    "has_failure": has_failure,
                    "has_not_executed": has_not_executed
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
            "all_succeeded_or_noop": (cycle["status"] == "COMPLETED"),
            "exception_count": len(exceptions),
            "exceptions": exceptions
        }
