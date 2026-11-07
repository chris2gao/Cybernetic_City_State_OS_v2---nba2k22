"""NBA2K22 Human-Controlled Season Closed-Loop Host.

Coordinates WorldData acquisition, Decision Outbox, Role Action Batches,
and REA Native Bulk Executor in a nonresident, Human-triggered cycle.
Enforces save/worldline isolation, CAS preflight, plan digest verification,
and independent readback.
"""

from contextlib import closing
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

# Setup paths
_DIR = Path(__file__).resolve().parent
_PROTOTYPE_DIR = _DIR.parent.parent / "world_data_prototype"
if str(_DIR) in sys.path:
    sys.path.remove(str(_DIR))
if str(_PROTOTYPE_DIR) in sys.path:
    sys.path.remove(str(_PROTOTYPE_DIR))
sys.path.insert(0, str(_DIR))
sys.path.insert(0, str(_PROTOTYPE_DIR))

import contracts
from bulk_executor import (
    BulkBatch,
    BulkIntentItem,
    BulkBatchPlanner,
    ExecutionJournal,
    ItemReceipt,
    atomic_write_json,
    sha256_digest,
    canonical_encode
)
from bounded_session_transport import (
    BoundedSessionExecutor,
    SessionBatchTransport
)
from calendar_sim_orchestrator import CalendarSimOrchestrator
from decision_batch_bridge import DecisionBatchBridge, BridgeResult
from decision_outbox import DecisionOutbox
from engine import connect, create_database
from live_reader import ReadOnlyGameProcess
from live_world import read_binding, bound_database, initialize_save
from role_batches import (
    ActionIntent,
    BatchContext,
    ExecutionAggregator,
    RoleActionBatch
)
from role_capabilities import RoleCapabilityProfile, RoleCapabilityService
from schema_model import VERSION
from validate_batch_execution import validate_batch_execution
from transport import LiveExecutionContext


def parse_team_numeric_id(raw_val: Any) -> Optional[int]:
    """Parses numeric team ID from team:native:<ID>, team:<ID>, <ID>, or int."""
    if raw_val is None:
        return None
    s = str(raw_val).strip()
    if s.startswith("team:native:"):
        s = s[len("team:native:"):]
    elif s.startswith("team:"):
        s = s[len("team:"):]
    try:
        return int(s)
    except (ValueError, TypeError):
        return None


class TrustedRoleRegistry:
    """Manages authenticated roles bound to the current save file, database, and worldline manifest.
    
    Enforces strict default-deny authorization semantics (H1, H2, H3, H4).
    """

    def __init__(
        self,
        save_dir: Optional[Path] = None,
        save_id: Optional[str] = None,
        worldline_id: Optional[str] = None,
        database_path: Optional[Path] = None,
        *,
        is_mock: bool = False
    ):
        self.save_dir: Optional[Path] = Path(save_dir).resolve() if save_dir else None
        self.save_id: Optional[str] = save_id
        self.worldline_id: Optional[str] = worldline_id
        self.database_path: Optional[Path] = Path(database_path).resolve() if database_path else None
        self.is_mock: bool = is_mock

        self._actors: Dict[Tuple[str, int], str] = {}
        self._actor_provenance: Dict[Tuple[str, int], Dict[str, Any]] = {}
        self._allowed_actions: Dict[str, Set[str]] = {
            "GM": {"PLAYER.EDIT.TENDENCY_BATCH", "PLAYER_PATCH_TENDENCIES", "GM.TRADE.MIXED"},
            "COACH": {"PLAYER.EDIT.TENDENCY_BATCH", "PLAYER_PATCH_TENDENCIES", "COACH.STRATEGY.RUN_PLAY"}
        }
        self._phase_grants: Set[Tuple[str, str]] = set()
        self.authorization_status: str = "UNINITIALIZED"

        if self.save_dir and self.save_id:
            self.bind_save_context(self.save_dir, self.save_id, self.worldline_id or "worldline-main", self.database_path)
        else:
            self.authorization_status = "DEFAULT_DENIED_UNBOUND"

    @property
    def is_authorized(self) -> bool:
        return self.authorization_status in ("AUTHORIZED", "AUTHORIZED_MOCK") and len(self._actors) > 0

    def _refresh_phase_grants(self):
        self._phase_grants = set()
        for (role, _), actor_uid in self._actors.items():
            if role == "GM":
                self._phase_grants.add((actor_uid, "PLAYER.EDIT.TENDENCY_BATCH"))
                self._phase_grants.add((actor_uid, "PLAYER_PATCH_TENDENCIES"))
                self._phase_grants.add((actor_uid, "GM.TRADE.MIXED"))
            elif role == "COACH":
                self._phase_grants.add((actor_uid, "PLAYER.EDIT.TENDENCY_BATCH"))
                self._phase_grants.add((actor_uid, "PLAYER_PATCH_TENDENCIES"))
                self._phase_grants.add((actor_uid, "COACH.STRATEGY.RUN_PLAY"))

    def bind_save_context(
        self,
        save_dir: Path,
        save_id: str,
        worldline_id: str,
        database_path: Optional[Path] = None,
        *,
        is_mock: Optional[bool] = None
    ) -> bool:
        """Binds the registry directly to the active save directory, database, and worldline manifest.
        
        Enforces strict fail-closed authorization verification (H1, H2, H3).
        """
        self.save_dir = Path(save_dir).resolve()
        self.save_id = save_id
        self.worldline_id = worldline_id
        if database_path:
            self.database_path = Path(database_path).resolve()
        if is_mock is not None:
            self.is_mock = is_mock

        auth_file = self.save_dir / "role_authorizations.json"
        if not auth_file.is_file():
            self._actors.clear()
            self._actor_provenance.clear()
            self._phase_grants.clear()
            self.authorization_status = "AUTHORIZATION_FILE_MISSING"

            # Generate configuration template for operator guidance, but never make it active (H1)
            template_path = self.save_dir / "role_authorizations.template.json"
            template_manifest = {
                "schema_version": "nba2k22.rea.role_authorizations.v1",
                "save_id": save_id,
                "worldline_id": worldline_id,
                "bound_database_file": self.database_path.name if self.database_path else "world.sqlite",
                "status": "TEMPLATE_PENDING_HUMAN_AUTHORIZATION",
                "human_authorization_ref": None,
                "provenance": "PENDING_OPERATOR_SIGNING",
                "roles": [
                    {
                        "role_type": "GM",
                        "team_id": 28,
                        "actor_uid": "<HUMAN_OR_AGENT_UID>",
                        "human_authorization_ref": "<HUMAN_DELEGATION_GRANT_REF>",
                        "provenance": "SAVE_DB_VERIFIED_DELEGATION"
                    }
                ]
            }
            try:
                tmp_tpl = template_path.with_suffix(".tmp")
                tmp_tpl.write_text(json.dumps(template_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                os.replace(tmp_tpl, template_path)
            except Exception:
                pass
            return False

        try:
            auth_data = json.loads(auth_file.read_text(encoding="utf-8"))
        except Exception:
            self._actors.clear()
            self._actor_provenance.clear()
            self._phase_grants.clear()
            self.authorization_status = "AUTHORIZATION_FILE_CORRUPT"
            return False

        # Reject template masquerading as active authorization (H1)
        if auth_data.get("status") == "TEMPLATE_PENDING_HUMAN_AUTHORIZATION":
            self._actors.clear()
            self._actor_provenance.clear()
            self._phase_grants.clear()
            self.authorization_status = "TEMPLATE_CANNOT_BECOME_ACTIVE_AUTHORIZATION"
            return False

        # Context Binding Checks (H3)
        if auth_data.get("save_id") != self.save_id:
            self._actors.clear()
            self._actor_provenance.clear()
            self._phase_grants.clear()
            self.authorization_status = "AUTHORIZATION_SAVE_ID_MISMATCH"
            return False

        allowed_worldlines = auth_data.get("authorized_worldlines", [])
        has_wl_wildcard = ("*" in allowed_worldlines)
        if auth_data.get("worldline_id") != self.worldline_id and self.worldline_id not in allowed_worldlines and not has_wl_wildcard:
            self._actors.clear()
            self._actor_provenance.clear()
            self._phase_grants.clear()
            self.authorization_status = "AUTHORIZATION_WORLDLINE_MISMATCH"
            return False

        expected_db_name = self.database_path.name if self.database_path else "world.sqlite"
        allowed_databases = auth_data.get("authorized_databases", [])
        has_db_wildcard = ("*" in allowed_databases)
        if auth_data.get("bound_database_file") != expected_db_name and expected_db_name not in allowed_databases and not has_db_wildcard:
            self._actors.clear()
            self._actor_provenance.clear()
            self._phase_grants.clear()
            self.authorization_status = "AUTHORIZATION_DATABASE_FILE_MISMATCH"
            return False

        # Wildcard scope validation (F2):
        # If wildcard is used, it MUST be qualified by explicit human authorization declaration,
        # and verified against the actual registered worldlines manifest and active database.
        if has_wl_wildcard or has_db_wildcard:
            has_explicit_declaration = bool(
                auth_data.get("wildcard_authorization_purpose")
                or auth_data.get("wildcard_scope_declaration")
                or auth_data.get("allow_wildcard_scope")
                or "WILDCARD" in str(auth_data.get("human_authorization_ref", "")).upper()
                or "WILDCARD" in str(auth_data.get("provenance", "")).upper()
            )
            if not has_explicit_declaration:
                self._actors.clear()
                self._actor_provenance.clear()
                self._phase_grants.clear()
                self.authorization_status = "AUTHORIZATION_WILDCARD_NOT_DECLARED_BY_HUMAN"
                return False

            manifest_file = self.save_dir / "worldlines_manifest.json" if self.save_dir else None
            if manifest_file and manifest_file.exists():
                try:
                    m_data = json.loads(manifest_file.read_text(encoding="utf-8"))
                    known_wls = set(m_data.get("worldlines", {}).keys())
                    known_wls.add("worldline-main")
                    if self.worldline_id not in known_wls:
                        self._actors.clear()
                        self._actor_provenance.clear()
                        self._phase_grants.clear()
                        self.authorization_status = "AUTHORIZATION_WILDCARD_TARGET_UNVERIFIED"
                        return False
                except Exception:
                    self._actors.clear()
                    self._actor_provenance.clear()
                    self._phase_grants.clear()
                    self.authorization_status = "AUTHORIZATION_WILDCARD_TARGET_UNVERIFIED"
                    return False

        # Check Human Authorization / Provenance (H3)
        auth_ref = auth_data.get("human_authorization_ref") or auth_data.get("provenance")
        if not auth_ref or "TEMPLATE" in str(auth_ref).upper():
            self._actors.clear()
            self._actor_provenance.clear()
            self._phase_grants.clear()
            self.authorization_status = "AUTHORIZATION_PROVENANCE_MISSING"
            return False

        # Validate database integrity and teams (H2, F1)
        db_teams = self._get_teams_from_database()
        if not db_teams:
            self._actors.clear()
            self._actor_provenance.clear()
            self._phase_grants.clear()
            self.authorization_status = "DATABASE_VERIFICATION_FAILED"
            return False

        raw_roles = auth_data.get("roles", [])
        if not isinstance(raw_roles, list) or not raw_roles:
            self._actors.clear()
            self._actor_provenance.clear()
            self._phase_grants.clear()
            self.authorization_status = "NO_ROLES_SPECIFIED"
            return False

        verified_roles = []
        for r in raw_roles:
            rtype = str(r.get("role_type", "")).upper()
            tid = parse_team_numeric_id(r.get("team_id"))
            auid = str(r.get("actor_uid", "")).strip()
            role_auth = r.get("human_authorization_ref") or r.get("provenance") or auth_ref

            if rtype not in ("GM", "COACH") or tid is None or not auid or not role_auth:
                continue

            if not self._verify_team_in_database(tid):
                continue

            verified_roles.append({
                "role_type": rtype,
                "team_id": tid,
                "actor_uid": auid,
                "human_authorization_ref": role_auth,
                "provenance": r.get("provenance", auth_data.get("provenance", "SAVE_DB_VERIFIED_DELEGATION")),
                "authorized_at": r.get("authorized_at", auth_data.get("authorized_at"))
            })

        if not verified_roles:
            self._actors.clear()
            self._actor_provenance.clear()
            self._phase_grants.clear()
            self.authorization_status = "NO_VALID_AUTHENTICATED_ROLES"
            return False

        self._actors.clear()
        self._actor_provenance.clear()
        for r in verified_roles:
            rtype = r["role_type"]
            tid = r["team_id"]
            auid = r["actor_uid"]
            self._actors[(rtype, tid)] = auid
            self._actor_provenance[(rtype, tid)] = {
                "provenance": r["provenance"],
                "human_authorization_ref": r["human_authorization_ref"],
                "authorized_at": r["authorized_at"],
                "save_id": self.save_id,
                "worldline_id": self.worldline_id
            }

        self.authorization_status = "AUTHORIZED"
        self._refresh_phase_grants()
        return True

    def _get_teams_from_database(self) -> Set[int]:
        """Queries numeric team IDs from the active save database with fail-closed semantics.

        Enforces strict save identity (F1): the database MUST contain a 'saves' table confirming
        ownership matching self.save_id. If saves table is missing, query fails, no matching
        singleton record exists, or save_id mismatches, access is strictly denied (returns empty set).
        """
        teams = set()
        if not self.database_path or not self.database_path.is_file():
            return set()
        if not self.save_id or not str(self.save_id).strip():
            return set()

        try:
            with closing(connect(self.database_path, True)) as conn:
                cur = conn.cursor()
                # 1. Strictly verify saves table matches active save_id (F1)
                try:
                    cur.execute("SELECT save_id FROM saves WHERE singleton=1")
                    row = cur.fetchone()
                except Exception:
                    # saves table missing, unreadable, or query error -> fail closed
                    return set()

                if not row or not row[0] or str(row[0]).strip() != str(self.save_id).strip():
                    # No record, null save_id, or save_id mismatch -> fail closed
                    return set()

                # 2. Query team_id and native_team_id
                cols = [c[1] for c in cur.execute("PRAGMA table_info(teams)").fetchall()]
                if not cols:
                    return set()

                query = "SELECT team_id" + (", native_team_id" if "native_team_id" in cols else "") + " FROM teams"
                for row in cur.execute(query).fetchall():
                    tid = parse_team_numeric_id(row[0])
                    if tid is not None:
                        teams.add(tid)
                    if len(row) > 1 and row[1] is not None:
                        nid = parse_team_numeric_id(row[1])
                        if nid is not None:
                            teams.add(nid)
        except Exception:
            return set()
        return teams

    def _verify_team_in_database(self, team_id: int) -> bool:
        """Verifies that a team actually exists in the active save database. Fail-closed on any failure."""
        if not self.database_path or not self.database_path.is_file():
            return False
        if not self.save_id or not str(self.save_id).strip():
            return False
        db_teams = self._get_teams_from_database()
        if not db_teams:
            return False
        parsed_tid = parse_team_numeric_id(team_id)
        if parsed_tid is None:
            return False
        return parsed_tid in db_teams

    def get_actor(self, role_type: str, team_id: int) -> Optional[str]:
        """Returns the authenticated actor_uid for a given role and team, or None."""
        rtype = str(role_type).upper()
        parsed_tid = parse_team_numeric_id(team_id)
        if parsed_tid is None:
            return None
        return self._actors.get((rtype, parsed_tid))

    def is_actor_authenticated(self, role_type: str, team_id: int, actor_uid: str) -> bool:
        """Verifies that the actor identity and team scope are authentically registered for the active save."""
        if not self.is_authorized:
            return False
        rtype = str(role_type).upper()
        parsed_tid = parse_team_numeric_id(team_id)
        if parsed_tid is None or not actor_uid:
            return False
        expected = self._actors.get((rtype, parsed_tid))
        if expected is None or expected != str(actor_uid):
            return False

        if not self._verify_team_in_database(parsed_tid):
            return False

        return True

    def get_authenticated_teams(self, role_type: str) -> Tuple[int, ...]:
        """Returns sorted tuple of team IDs authenticated for a given role type in the current save."""
        if not self.is_authorized:
            return ()
        rtype = str(role_type).upper()
        teams = [tid for (r, tid) in self._actors.keys() if r == rtype and self._verify_team_in_database(tid)]
        return tuple(sorted(teams))

    def get_phase_grants(self) -> Set[Tuple[str, str]]:
        if not self.is_authorized:
            return set()
        return set(self._phase_grants)

    def get_profiles(self, ctx: BatchContext) -> Tuple[RoleCapabilityProfile, RoleCapabilityProfile]:
        gm_actors = {uid for (r, _), uid in self._actors.items() if r == "GM"}
        if len(gm_actors) > 1:
            raise ValueError(
                f"AMBIGUOUS_MULTIPLE_ACTORS_FOR_ROLE: Multiple GM actors detected ({sorted(list(gm_actors))}); "
                "single-profile interface cannot disambiguate without expanding privilege."
            )
        elif len(gm_actors) == 1:
            gm_actor = next(iter(gm_actors))
            gm_teams = tuple(sorted([
                tid for (r, tid), uid in self._actors.items()
                if r == "GM" and uid == gm_actor and self._verify_team_in_database(tid)
            ]))
        else:
            gm_actor = "unauthorized_gm"
            gm_teams = ()

        coach_actors = {uid for (r, _), uid in self._actors.items() if r == "COACH"}
        if len(coach_actors) > 1:
            raise ValueError(
                f"AMBIGUOUS_MULTIPLE_ACTORS_FOR_ROLE: Multiple Coach actors detected ({sorted(list(coach_actors))}); "
                "single-profile interface cannot disambiguate without expanding privilege."
            )
        elif len(coach_actors) == 1:
            coach_actor = next(iter(coach_actors))
            coach_teams = tuple(sorted([
                tid for (r, tid), uid in self._actors.items()
                if r == "COACH" and uid == coach_actor and self._verify_team_in_database(tid)
            ]))
        else:
            coach_actor = "unauthorized_coach"
            coach_teams = ()

        gm_actor_id = gm_actor if (self.is_authorized and gm_actor != "unauthorized_gm") else "unauthorized_gm"
        gm_actions = frozenset(self._allowed_actions["GM"]) if (self.is_authorized and gm_actor != "unauthorized_gm") else frozenset()
        gm_teams = gm_teams if self.is_authorized else ()

        coach_actor_id = coach_actor if (self.is_authorized and coach_actor != "unauthorized_coach") else "unauthorized_coach"
        coach_actions = frozenset(self._allowed_actions["COACH"]) if (self.is_authorized and coach_actor != "unauthorized_coach") else frozenset()
        coach_teams = coach_teams if self.is_authorized else ()

        gm = RoleCapabilityProfile(
            role_type="GM",
            actor_uid=gm_actor_id,
            team_scope=gm_teams,
            world_id=ctx.world_id,
            save_instance_id=ctx.save_instance_id,
            generation_id=ctx.generation_id,
            season_id=ctx.season_id,
            phase=ctx.phase,
            snapshot_ref=ctx.snapshot_ref,
            allowed_actions=gm_actions
        )

        coach = RoleCapabilityProfile(
            role_type="COACH",
            actor_uid=coach_actor_id,
            team_scope=coach_teams,
            world_id=ctx.world_id,
            save_instance_id=ctx.save_instance_id,
            generation_id=ctx.generation_id,
            season_id=ctx.season_id,
            phase=ctx.phase,
            snapshot_ref=ctx.snapshot_ref,
            allowed_actions=coach_actions
        )
        return gm, coach

    def inject_mock_authorizations(
        self,
        roles: List[Dict[str, Any]],
        *,
        human_authorization_ref: str = "HUMAN_TEST_MOCK_GRANT"
    ) -> None:
        """Explicitly injects test role authorizations for offline mock testing only.
        
        Strictly prohibited in live mode (H1).
        """
        if not self.is_mock:
            raise ValueError(
                "LIVE_MODE_REJECTS_MOCK_AUTHORIZATION: "
                "Mock authorization injection is strictly prohibited in live mode."
            )
        self._actors.clear()
        self._actor_provenance.clear()
        for r in roles:
            rtype = str(r["role_type"]).upper()
            tid = parse_team_numeric_id(r["team_id"])
            auid = str(r["actor_uid"])
            if tid is not None and auid:
                self._actors[(rtype, tid)] = auid
                self._actor_provenance[(rtype, tid)] = {
                    "provenance": r.get("provenance", "OFFLINE_TEST_MOCK_INJECTION"),
                    "human_authorization_ref": human_authorization_ref,
                    "save_id": self.save_id or "mock_save",
                    "worldline_id": self.worldline_id or "mock_worldline"
                }
        self.authorization_status = "AUTHORIZED_MOCK"
        self._refresh_phase_grants()



class HostState:
    UNBOUND = "UNBOUND"
    SESSION_BOUND = "SESSION_BOUND"
    BASELINE_CAPTURED = "BASELINE_CAPTURED"
    DECISION_OPEN = "DECISION_OPEN"
    DECISION_SEALED = "DECISION_SEALED"
    WAITING_HUMAN_EXECUTION_AUTH = "WAITING_HUMAN_EXECUTION_AUTH"
    EXECUTED_AND_READBACK = "EXECUTED_AND_READBACK"
    WAITING_CALENDAR_ADVANCE = "WAITING_CALENDAR_ADVANCE"
    NEXT_CAPTURED = "NEXT_CAPTURED"
    CONFLICTED = "CONFLICTED"
    CONTEXT_STALE = "CONTEXT_STALE"
    UNKNOWN_LOCKED = "UNKNOWN_LOCKED"
    STOPPED_PARTIAL = "STOPPED_PARTIAL"
    PAUSED = "PAUSED"


class SeasonCycleHost:
    """Nonresident controller orchestrating the Human-driven season closed loop."""

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        state_file: Optional[Path] = None,
        ledger_file: Optional[Path] = None,
        outbox_db: Optional[Path] = None,
        *,
        approved_role_manifest_sha256: Optional[str] = None,
    ):
        self.workspace_root = Path(workspace_root).resolve() if workspace_root else _DIR.parents[3]
        self.state_file = Path(state_file).resolve() if state_file else _DIR / "runtime/season_host_state.json"
        self.ledger_file = Path(ledger_file).resolve() if ledger_file else _DIR / "runtime/season_run_ledger.jsonl"
        self.outbox_db = Path(outbox_db).resolve() if outbox_db else _DIR / "runtime/outbox.db"
        
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.ledger_file.parent.mkdir(parents=True, exist_ok=True)
        self.outbox_db.parent.mkdir(parents=True, exist_ok=True)

        self.capability_service = RoleCapabilityService()
        self.bridge = DecisionBatchBridge(self.capability_service)
        self.outbox = DecisionOutbox(self.outbox_db, capability_service=self.capability_service)
        self.role_registry = TrustedRoleRegistry()
        self.approved_role_manifest_sha256 = approved_role_manifest_sha256

        self.state: Dict[str, Any] = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "status": HostState.UNBOUND,
            "save_directory": None,
            "loaded_filename": None,
            "save_id": None,
            "worldline_id": None,
            "database_file": None,
            "current_game_date": None,
            "current_cycle_id": None,
            "active_plan": None,
            "is_offline_mock": False,
            "pre_pause_status": None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

    def _save_state(self):
        self.state["updated_at"] = datetime.now(timezone.utc).isoformat()
        tmp_file = self.state_file.with_suffix(".tmp")
        tmp_file.write_text(json.dumps(self.state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp_file, self.state_file)

    def _append_ledger(self, record: Dict[str, Any]):
        record["recorded_at"] = datetime.now(timezone.utc).isoformat()
        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _approved_live_context(self, pid: int) -> Dict[str, Any]:
        """Recheck the operator-pinned, bounded delegation and current process/binding."""
        from refresh import _context

        save_dir = Path(self.state["save_directory"])
        db = Path(self.state["database_file"])
        manifest_file = save_dir / "role_authorizations.json"
        if not self.approved_role_manifest_sha256 or not manifest_file.is_file():
            raise ValueError("AUTHORIZATION_PENDING_HUMAN: require the operator-approved role manifest hash")
        raw = manifest_file.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != self.approved_role_manifest_sha256:
            raise ValueError("APPROVED_ROLE_MANIFEST_HASH_MISMATCH")
        grant = json.loads(raw)
        roles = grant.get("roles")
        player_ids = grant.get("player_ids")
        if (not isinstance(roles, list) or len(roles) != 1
                or not isinstance(player_ids, list) or not 1 <= len(player_ids) <= 3
                or any(type(pid) is not int or not 1 <= pid <= 65535 for pid in player_ids)
                or len(set(player_ids)) != len(player_ids)
                or grant.get("save_id") != self.state["save_id"]
                or grant.get("worldline_id") != self.state["worldline_id"]
                or grant.get("bound_database_file") != db.name
                or grant.get("authorized_worldlines") or grant.get("authorized_databases")
                or grant.get("allow_wildcard_scope")
                or grant.get("action_id") != "PLAYER_PATCH_TENDENCIES"
                or grant.get("field_id") != "SHOT_TENDENCY"
                or not grant.get("human_authorization_ref")):
            raise ValueError("LIVE_DELEGATION_SCOPE_INVALID")
        now = datetime.now(timezone.utc)
        if not datetime.fromisoformat(grant["authorized_at"]) <= now < datetime.fromisoformat(grant["expires_at"]):
            raise ValueError("LIVE_DELEGATION_OUTSIDE_APPROVED_TIME")
        binding, binding_sha = read_binding(save_dir, self.state["loaded_filename"])
        if (binding.get("save_id") != self.state["save_id"] or binding.get("worldline_id") != self.state["worldline_id"]
                or bound_database(save_dir, binding) != db.resolve()
                or grant.get("binding_sha256") != binding_sha):
            raise ValueError("LIVE_SAVE_BINDING_CHANGED")
        if (not self.role_registry.bind_save_context(save_dir, self.state["save_id"], self.state["worldline_id"], db,
                                                     is_mock=False)
                or manifest_file.read_bytes() != raw):
            raise ValueError("LIVE_DELEGATION_NOT_VERIFIED")
        context = _context(pid)
        return {"role_manifest_sha256": digest, "binding_sha256": binding_sha, "epoch": context["epoch"],
                "game_progress": context["game_progress"], "team_id": parse_team_numeric_id(roles[0].get("team_id")),
                "actor_uid": roles[0].get("actor_uid"), "role_type": str(roles[0].get("role_type", "")).upper(),
                "player_ids": player_ids}

    def _make_context(self, cycle_id: str) -> BatchContext:
        season_id = "2021-22"
        phase = "REGULAR_SEASON"
        target_db = self.state.get("database_file")
        if target_db and Path(target_db).exists():
            try:
                with closing(connect(Path(target_db), True)) as conn:
                    s_row = conn.execute("SELECT season_id FROM seasons ORDER BY rowid DESC LIMIT 1").fetchone()
                    if s_row and s_row[0]:
                        season_id = s_row[0]
                    c_row = conn.execute("SELECT period_label FROM season_calendar_observations ORDER BY rowid DESC LIMIT 1").fetchone()
                    if c_row and c_row[0]:
                        phase = c_row[0]
            except Exception:
                pass
        curr_date = self.state.get("current_game_date", "unknown_date")
        w_id = self.state.get("worldline_id") or "worldline-main"
        snapshot_ref = f"snap_{w_id}_{curr_date}_{cycle_id}"
        return BatchContext(
            world_id=w_id,
            save_instance_id=self.state.get("loaded_filename") or "MyLEAGUE0003",
            generation_id=cycle_id,
            season_id=season_id,
            phase=phase,
            snapshot_ref=snapshot_ref,
            catalog_version=self.capability_service.version
        )

    def _get_live_getter(self, expected_pid: Optional[int] = None) -> Optional[Any]:
        """Provides a real-time player tendency getter from NBA2K22 memory (pure ReadProcessMemory)."""
        return self._get_fresh_live_getter(expected_pid)

    def _get_fresh_live_getter(
        self, expected_pid: Optional[int] = None, *, expected_team: Optional[int] = None,
        expected_players: Optional[Set[int]] = None, expected_creation_filetime: Optional[int] = None,
    ) -> Optional[Any]:
        """Read fresh values, optionally bound to the actual Native roster and process epoch."""
        try:
            from refresh import resolve_pid
            from player_skill_reader import collect_player_skills
            actual_pid = resolve_pid("auto")
            if expected_pid is not None and actual_pid != expected_pid:
                raise RuntimeError(f"PID_MISMATCH_FRESH_GETTER: expected {expected_pid}, found {actual_pid}")
            reader = ReadOnlyGameProcess(actual_pid)
            try:
                if expected_creation_filetime is not None and reader.creation_filetime != expected_creation_filetime:
                    return None
                m, _ = collect_player_skills(reader)
                if expected_team is not None:
                    team_pointers = [address for address, tid in m["core_team_pointer_map"].items()
                                     if type(tid) is int and tid == expected_team]
                    if len(team_pointers) != 1:
                        return None
                    team_pointer = team_pointers[0]
                    player_pool = m["descriptors"][1]
                player_tendencies = {}
                seen = set()
                for p in m["players"]:
                    uid = p["native_unique_id_raw"]
                    if type(uid) is not int or (expected_players is not None and uid not in expected_players):
                        continue
                    if uid in seen:
                        player_tendencies.pop(uid, None)
                        continue
                    seen.add(uid)
                    if p["current_core_roster_status"] != "CURRENT_CORE_ROSTER":
                        continue
                    s_idx = p["source_player_index"]
                    if expected_team is not None:
                        slot = p["current_roster_slot"]
                        team_id = p["native_team_id"]
                        if (type(team_id) is not int or team_id != expected_team
                                or type(slot) is not int or not 0 <= slot < 15):
                            continue
                        # The reader already verified reciprocal current-team membership.
                        # Match Native rosterPlayer's additional contract-team guard.
                        address = player_pool["address"] + s_idx * player_pool["stride"]
                        contract_team = int.from_bytes(reader.read(address + 0xa8, 8, "S4_CONTRACT_TEAM"), "little")
                        if contract_team != team_pointer:
                            continue
                    player_tendencies[uid] = m["skill_rows"][s_idx]["tendencies"]

                def fresh_getter(player_id: int, field_id: str) -> Optional[int]:
                    tdict = player_tendencies.get(int(player_id), {})
                    norm_key = field_id.lower()
                    if not norm_key.endswith("_raw"):
                        norm_key = norm_key + "_raw"
                    val = tdict.get(norm_key)
                    if val is None:
                        val = tdict.get(field_id)
                    return val

                return fresh_getter
            finally:
                reader.close()
        except RuntimeError as e:
            if "PID_MISMATCH_FRESH_GETTER" in str(e):
                raise
            return None
        except Exception:
            return None

    def _make_profiles(self, ctx: BatchContext) -> Tuple[RoleCapabilityProfile, RoleCapabilityProfile]:
        return self.role_registry.get_profiles(ctx)

    def inspect_worldline(
        self,
        save_dir: Path,
        loaded_filename: str,
        current_game_date: Optional[str] = None,
        target_worldline_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Detect save binding, manage worldlines manifest, and isolate backward dates (Gates G02, P1)."""
        save_json_path = save_dir / "save.json"
        manifest_path = save_dir / "worldlines_manifest.json"

        binding, binding_hash = read_binding(save_dir, loaded_filename)
        save_id = binding["save_id"]
        default_db = bound_database(save_dir, binding)

        # Load or initialize append-only worldlines manifest (P1)
        manifest = {}
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                manifest = {}
        if not manifest:
            manifest = {
                "original_save_id": save_id,
                "primary_database_file": "world.sqlite",
                "active_worldline_id": "worldline-main",
                "worldlines": {
                    "worldline-main": {
                        "database_file": "world.sqlite",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "parent_worldline_id": None
                    }
                }
            }

        latest_db_date = None
        if default_db.exists():
            with closing(connect(default_db, True)) as conn:
                row = conn.execute("SELECT max(game_date) FROM games WHERE game_date IS NOT NULL").fetchone()
                if row and row[0]:
                    latest_db_date = row[0]
                try:
                    c_row = conn.execute("SELECT current_native_iso_date FROM season_calendar_observations WHERE current_native_iso_date IS NOT NULL ORDER BY rowid DESC LIMIT 1").fetchone()
                    if c_row and c_row[0]:
                        if latest_db_date is None or c_row[0] > latest_db_date:
                            latest_db_date = c_row[0]
                except Exception:
                    pass

        is_backward = False
        worldline_id = manifest.get("active_worldline_id", "worldline-main")
        target_db = default_db

        if target_worldline_id and target_worldline_id in manifest.get("worldlines", {}):
            worldline_id = target_worldline_id
            db_name = manifest["worldlines"][worldline_id]["database_file"]
            target_db = save_dir / db_name
            manifest["active_worldline_id"] = worldline_id
        elif current_game_date and latest_db_date and current_game_date < latest_db_date:
            is_backward = True
            date_slug = current_game_date.replace("-", "")
            # Preserve deterministic idempotent identity if already created
            existing_wl = next((w_id for w_id, w_info in manifest.get("worldlines", {}).items() if w_info.get("fork_game_date") == current_game_date), None)
            if existing_wl:
                worldline_id = existing_wl
                target_db = save_dir / manifest["worldlines"][existing_wl]["database_file"]
            else:
                worldline_id = f"worldline-{save_id}-{date_slug}-{uuid.uuid4().hex[:6]}"
                target_db = save_dir / f"world-{worldline_id}.sqlite"
                if not target_db.exists():
                    create_database(target_db, save_id)
                    if default_db and default_db.exists():
                        try:
                            with closing(connect(default_db, True)) as pconn, closing(connect(target_db, False)) as cconn:
                                pcur = pconn.cursor()
                                ccur = cconn.cursor()
                                for srow in pcur.execute("SELECT season_id, season_code, save_id FROM seasons").fetchall():
                                    ccur.execute("INSERT OR IGNORE INTO seasons (season_id, season_code, save_id) VALUES (?, ?, ?)", (srow[0], srow[1], srow[2]))
                                cols = [c[1] for c in pcur.execute("PRAGMA table_info(teams)").fetchall()]
                                if cols:
                                    col_names = ", ".join(cols)
                                    placeholders = ", ".join(["?"] * len(cols))
                                    for trow in pcur.execute(f"SELECT {col_names} FROM teams").fetchall():
                                        ccur.execute(f"INSERT OR IGNORE INTO teams ({col_names}) VALUES ({placeholders})", trow)
                                cconn.commit()
                        except Exception:
                            pass
                manifest["worldlines"][worldline_id] = {
                    "database_file": target_db.name,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "fork_game_date": current_game_date,
                    "parent_worldline_id": manifest.get("active_worldline_id", "worldline-main")
                }
            manifest["active_worldline_id"] = worldline_id
        elif worldline_id in manifest.get("worldlines", {}):
            target_db = save_dir / manifest["worldlines"][worldline_id]["database_file"]
            if not target_db.exists():
                target_db = default_db

        # Atomic write to save.json with immediate verification and rollback (P1)
        orig_bytes = save_json_path.read_bytes() if save_json_path.exists() else None
        try:
            sdata = json.loads(orig_bytes) if orig_bytes else {"save_id": save_id, "loaded_filename": loaded_filename}
            sdata["database_file"] = target_db.name
            sdata["worldline_id"] = worldline_id
            tmp_sjson = save_json_path.with_suffix(".tmp")
            tmp_sjson.write_text(json.dumps(sdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            os.replace(tmp_sjson, save_json_path)

            new_binding, new_hash = read_binding(save_dir, loaded_filename)
            bound_db = bound_database(save_dir, new_binding)
            if bound_db != target_db or not target_db.exists():
                raise RuntimeError(f"SAVE_BINDING_VERIFICATION_FAILED: bound_db {bound_db} != target_db {target_db}")
            binding, binding_hash = new_binding, new_hash

            tmp_m = manifest_path.with_suffix(".tmp")
            tmp_m.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            os.replace(tmp_m, manifest_path)
        except Exception as e:
            if orig_bytes and save_json_path.exists():
                save_json_path.write_bytes(orig_bytes)
            raise RuntimeError(f"WORLDLINE_BINDING_UPDATE_FAILED_FAIL_CLOSED: {e}")

        # Bind role registry directly to active save context and target database
        self.role_registry.bind_save_context(save_dir, save_id, worldline_id, target_db)

        return {
            "save_id": save_id,
            "loaded_filename": loaded_filename,
            "binding_sha256": binding_hash,
            "default_db": str(default_db),
            "target_db": str(target_db),
            "latest_db_date": latest_db_date,
            "current_game_date": current_game_date,
            "is_backward": is_backward,
            "worldline_id": worldline_id,
            "active_worldline_id": manifest.get("active_worldline_id")
        }

    def initialize_season(
        self,
        save_directory: str,
        loaded_filename: str,
        pid: Any = "auto",
        mock_game_date: Optional[str] = None,
        force_new_worldline: bool = False,
        reader: Any = None
    ) -> Dict[str, Any]:
        """Binds environment, checks worldline, and captures initial full baseline."""
        save_dir = Path(save_directory).resolve()
        
        actual_pid = None
        current_date = mock_game_date
        live_reader_instance = None
        should_close_reader = False
        is_mock = (mock_game_date is not None)

        if is_mock:
            # Offline mock mode
            if reader is not None:
                live_reader_instance = reader
        else:
            # LIVE MODE: Connect to live NBA2K22.exe and read true in-game calendar date
            try:
                from refresh import resolve_pid
                actual_pid = resolve_pid(pid)
            except Exception as e:
                raise RuntimeError(f"LIVE_PROCESS_NOT_FOUND: NBA2K22.exe process not accessible ({e})")

            if reader is not None:
                live_reader_instance = reader
            else:
                live_reader_instance = ReadOnlyGameProcess(actual_pid)
                should_close_reader = True

            try:
                from schedule_reader import collect_schedule
                sched = collect_schedule(live_reader_instance, with_calendar=True, read_final_boxes=False)
                cal = sched.get("calendar") or {}
                current_date = cal.get("current_native_iso_date")
            except Exception as e:
                if should_close_reader and live_reader_instance:
                    live_reader_instance.close()
                raise RuntimeError(f"CANNOT_DECODE_LIVE_GAME_DATE: {e}")

            if not current_date:
                if should_close_reader and live_reader_instance:
                    live_reader_instance.close()
                raise RuntimeError("CANNOT_DECODE_LIVE_GAME_DATE: schedule controls returned empty date")

        wl_info = self.inspect_worldline(save_dir, loaded_filename, current_date)
        if force_new_worldline and not wl_info["is_backward"]:
            wl_info["worldline_id"] = f"worldline-{wl_info['save_id']}-branch-{uuid.uuid4().hex[:6]}"
            target_path = save_dir / f"world-{wl_info['worldline_id']}.sqlite"
            wl_info["target_db"] = str(target_path)
            if not target_path.exists():
                create_database(target_path, wl_info["save_id"])
                base_db = save_dir / "world.sqlite"
                if base_db.exists():
                    try:
                        with closing(connect(base_db, True)) as pconn, closing(connect(target_path, False)) as cconn:
                            pcur = pconn.cursor()
                            ccur = cconn.cursor()
                            for srow in pcur.execute("SELECT season_id, season_code, save_id FROM seasons").fetchall():
                                ccur.execute("INSERT OR IGNORE INTO seasons (season_id, season_code, save_id) VALUES (?, ?, ?)", (srow[0], srow[1], srow[2]))
                            cols = [c[1] for c in pcur.execute("PRAGMA table_info(teams)").fetchall()]
                            if cols:
                                col_names = ", ".join(cols)
                                placeholders = ", ".join(["?"] * len(cols))
                                for trow in pcur.execute(f"SELECT {col_names} FROM teams").fetchall():
                                    ccur.execute(f"INSERT OR IGNORE INTO teams ({col_names}) VALUES ({placeholders})", trow)
                            cconn.commit()
                    except Exception:
                        pass
            # F2 state consistency: atomically register new worldline in manifest,
            # update save.json with BOTH database_file AND worldline_id, then re-bind registry.
            # Any failure must roll back both files to avoid half-initialized state.
            manifest_path = save_dir / "worldlines_manifest.json"
            save_json_path = save_dir / "save.json"

            # 1. Load the current manifest (written by inspect_worldline above)
            orig_manifest_bytes = manifest_path.read_bytes() if manifest_path.exists() else None
            orig_save_bytes = save_json_path.read_bytes() if save_json_path.exists() else None
            try:
                manifest_data = json.loads(orig_manifest_bytes) if orig_manifest_bytes else {
                    "original_save_id": wl_info["save_id"],
                    "primary_database_file": "world.sqlite",
                    "active_worldline_id": "worldline-main",
                    "worldlines": {
                        "worldline-main": {
                            "database_file": "world.sqlite",
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "parent_worldline_id": None
                        }
                    }
                }

                # 2. Register the new branch worldline in the manifest
                parent_wl_id = manifest_data.get("active_worldline_id", "worldline-main")
                manifest_data["worldlines"][wl_info["worldline_id"]] = {
                    "database_file": target_path.name,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "parent_worldline_id": parent_wl_id,
                    "branch_reason": "force_new_worldline"
                }
                manifest_data["active_worldline_id"] = wl_info["worldline_id"]

                # 3. Atomic write manifest: tmp → replace
                tmp_m = manifest_path.with_suffix(".tmp")
                tmp_m.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                os.replace(tmp_m, manifest_path)

                # 4. Atomic write save.json with BOTH database_file AND worldline_id updated
                sdata = json.loads(orig_save_bytes) if orig_save_bytes else {
                    "save_id": wl_info["save_id"],
                    "loaded_filename": loaded_filename,
                }
                sdata["database_file"] = target_path.name
                sdata["worldline_id"] = wl_info["worldline_id"]
                tmp_sjson = save_json_path.with_suffix(".tmp")
                tmp_sjson.write_text(json.dumps(sdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                os.replace(tmp_sjson, save_json_path)

                # 5. Immediate readback verification: manifest, save.json, and DB must be consistent
                verify_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                verify_save = json.loads(save_json_path.read_text(encoding="utf-8"))
                new_wl_id = wl_info["worldline_id"]
                if new_wl_id not in verify_manifest.get("worldlines", {}):
                    raise RuntimeError(f"MANIFEST_VERIFY_FAILED: new worldline {new_wl_id!r} not in manifest after write")
                if verify_manifest.get("active_worldline_id") != new_wl_id:
                    raise RuntimeError(f"MANIFEST_ACTIVE_WL_VERIFY_FAILED: active_worldline_id mismatch after write")
                if verify_save.get("worldline_id") != new_wl_id:
                    raise RuntimeError(f"SAVE_JSON_WL_VERIFY_FAILED: worldline_id mismatch in save.json after write")
                if verify_save.get("database_file") != target_path.name:
                    raise RuntimeError(f"SAVE_JSON_DB_VERIFY_FAILED: database_file mismatch in save.json after write")
                if not target_path.exists():
                    raise RuntimeError(f"BRANCH_DB_MISSING: {target_path} not found after creation")

            except Exception as e:
                # Rollback both files on any failure to prevent half-initialized state
                try:
                    if orig_manifest_bytes is not None:
                        manifest_path.write_bytes(orig_manifest_bytes)
                    if orig_save_bytes is not None:
                        save_json_path.write_bytes(orig_save_bytes)
                except Exception:
                    pass
                raise RuntimeError(f"FORCE_NEW_WORLDLINE_STATE_UPDATE_FAILED_FAIL_CLOSED: {e}")

            # F2-B: Re-bind role registry to new worldline+database.
            # The earlier inspect_worldline() call bound the registry to the original worldline.
            # After manifest + save.json are atomically consistent, registry must follow.
            self.role_registry.bind_save_context(
                save_dir,
                wl_info["save_id"],
                wl_info["worldline_id"],  # new branch worldline ID, now registered in manifest
                target_path               # new branch DB path
            )

        target_db = Path(wl_info["target_db"])
        orchestrator = CalendarSimOrchestrator(
            save_directory=save_dir,
            loaded_filename=loaded_filename,
            database_path=target_db
        )

        capture_result = None
        if is_mock and live_reader_instance is None:
            # Offline mock baseline
            capture_result = {"status": "OFFLINE_MOCK_BASELINE_BOUND"}
        else:
            # LIVE FULL Capture: Fail-closed on error
            try:
                target_reader_or_pid = live_reader_instance if live_reader_instance is not None else actual_pid
                capture_result = orchestrator.trigger_world_capture(
                    reader_or_pid=target_reader_or_pid,
                    mode="FULL",
                    force=True
                )
            except Exception as e:
                if should_close_reader and live_reader_instance:
                    live_reader_instance.close()
                raise RuntimeError(f"BASELINE_FULL_CAPTURE_FAILED: {e}")
            finally:
                if should_close_reader and live_reader_instance:
                    live_reader_instance.close()

            if not capture_result or capture_result.get("status") not in (
                "SUCCESS_FULL_CAPTURE", "SUCCESS_INGESTED", "SUCCESS", "COMPLETED_REQUESTED_SOURCES", "SUCCESS_EXPORT_ONLY"
            ):
                raise RuntimeError(f"BASELINE_FULL_CAPTURE_UNCONFIRMED: {capture_result}")

        self.state.update({
            "status": HostState.BASELINE_CAPTURED,
            "save_directory": str(save_dir),
            "loaded_filename": loaded_filename,
            "save_id": wl_info["save_id"],
            "worldline_id": wl_info["worldline_id"],
            "database_file": str(target_db),
            "current_game_date": current_date,
            "current_cycle_id": None,
            "active_plan": None,
            "is_offline_mock": is_mock
        })
        self._save_state()

        # F2 receipt: accurately reflect authorization state.
        # If registry is not authorized (e.g. AUTHORIZATION_WILDCARD_TARGET_UNVERIFIED or DEFAULT_DENIED_UNBOUND),
        # the receipt must NOT imply Live execution is ready. Use a distinct status to flag pending auth.
        auth_ok = self.role_registry.is_authorized
        init_status = (
            "INITIALIZED_AND_BASELINE_BOUND"
            if auth_ok
            else "INITIALIZED_BASELINE_BOUND_AUTHORIZATION_PENDING"
        )

        receipt = {
            "status": init_status,
            "save_id": wl_info["save_id"],
            "loaded_filename": loaded_filename,
            "worldline_id": wl_info["worldline_id"],
            "database_file": str(target_db),
            "current_game_date": current_date,
            "is_backward_worldline_branch": wl_info["is_backward"],
            "role_authorization_status": self.role_registry.authorization_status,
            "role_authorization_ready": auth_ok,
            "capture_summary": capture_result.get("status") if capture_result else "ALREADY_BOUND"
        }
        self._append_ledger({"action": "INITIALIZE_SEASON", **receipt})
        return receipt

    def start_cycle(
        self,
        cycle_id: str,
        force: bool = False,
        mock_game_date: Optional[str] = None,
        candidate_intents: Optional[List[Dict[str, Any]]] = None,
        reader: Any = None
    ) -> Dict[str, Any]:
        """Initiates a cycle, verifies calendar progression, triggers capture, and registers draft intents."""
        reuse_next_capture = self.state["status"] == HostState.NEXT_CAPTURED and bool(candidate_intents)
        use_baseline = (self.state["status"] == HostState.BASELINE_CAPTURED or reuse_next_capture) and not force
        if self.state["status"] not in (
            HostState.BASELINE_CAPTURED,
            HostState.EXECUTED_AND_READBACK,
            HostState.NEXT_CAPTURED,
            HostState.WAITING_CALENDAR_ADVANCE
        ):
            if not force or (not self.state.get("is_offline_mock") and mock_game_date is None):
                raise ValueError(f"Cannot start cycle from state: {self.state['status']}")

        save_dir = Path(self.state["save_directory"])
        target_db = Path(self.state["database_file"])
        orchestrator = CalendarSimOrchestrator(
            save_directory=save_dir,
            loaded_filename=self.state["loaded_filename"],
            database_path=target_db
        )

        progress_status = "DATE_ADVANCED"
        live_reader_instance = None
        should_close_reader = False
        is_mock = bool(self.state.get("is_offline_mock", False) and self.state.get("is_mock", True)) or (mock_game_date is not None)

        if is_mock:
            # Offline mock mode
            if mock_game_date is not None:
                self.state["current_game_date"] = mock_game_date
            if reader is not None:
                prog = orchestrator.inspect_calendar_progress(reader)
                if prog.get("status") == "INCOMPLETE_GAME_IN_PROGRESS":
                    self.state["status"] = HostState.CONTEXT_STALE
                    self._save_state()
                    return {
                        "status": "REJECTED_GAME_IN_PROGRESS",
                        "cycle_id": cycle_id,
                        "reason": "Game is currently underway in memory; cannot start cycle."
                    }
                progress_status = prog.get("status", "DATE_ADVANCED")
        else:
            # LIVE MODE: Connect to live NBA2K22.exe
            try:
                from refresh import resolve_pid
                actual_pid = resolve_pid("auto")
            except Exception as e:
                raise RuntimeError(f"LIVE_PROCESS_NOT_FOUND: NBA2K22.exe is not running ({e})")

            live_reader_instance = reader if reader is not None else ReadOnlyGameProcess(actual_pid)
            should_close_reader = (reader is None)

            try:
                prog = orchestrator.inspect_calendar_progress(live_reader_instance)
                if prog.get("status") == "INCOMPLETE_GAME_IN_PROGRESS":
                    if not use_baseline:
                        self.state["status"] = HostState.CONTEXT_STALE
                        self._save_state()
                    return {
                        "status": "REJECTED_GAME_IN_PROGRESS",
                        "cycle_id": cycle_id,
                        "reason": "Game is currently underway in memory; cannot start cycle."
                    }

                if prog.get("status") == "SAME_STATE_REPEAT" and not force and not use_baseline:
                    return {
                        "status": "SAME_STATE_REPEAT",
                        "cycle_id": cycle_id,
                        "reason": "Latest memory game matches latest database game; no fresh final game observed. Use --force to proceed without new games."
                    }

                # Read current date from memory
                from schedule_reader import collect_schedule
                sched = collect_schedule(live_reader_instance, with_calendar=True, read_final_boxes=False)
                cal = sched.get("calendar") or {}
                mem_date = cal.get("current_native_iso_date")
                if use_baseline:
                    db_game_id = prog.get("latest_db_game_id")
                    native_game_id = prog.get("native_game_id")
                    if (
                        not mem_date or mem_date != self.state["current_game_date"]
                        or prog.get("status") != "SAME_STATE_REPEAT"
                        or prog.get("new_final_game_detected") is not False
                        or not isinstance(db_game_id, str) or not db_game_id
                        or prog.get("latest_memory_game_id") != db_game_id
                        or type(native_game_id) not in (int, str) or not str(native_game_id).isdecimal()
                        or str(native_game_id) != prog.get("latest_db_native_game_id")
                    ):
                        return {"status": "BASELINE_CONTEXT_CHANGED", "cycle_id": cycle_id,
                                "reason": "Live date and matching Native/SQLite finals are required to reuse the initial capture."}
                if mem_date:
                    self.state["current_game_date"] = mem_date

                # Trigger INCREMENTAL capture if new game completed or force
                if prog.get("new_final_game_detected") or force:
                    cap_res = orchestrator.trigger_world_capture(
                        reader_or_pid=live_reader_instance,
                        mode="INCREMENTAL",
                        force=force
                    )
                    if cap_res.get("status") in ("REJECTED_GAME_IN_PROGRESS", "FAILED", "REFRESH_FAILED_FAIL_CLOSED", "SQL_VERIFICATION_FAILED_FAIL_CLOSED"):
                        raise RuntimeError(f"INCREMENTAL_CAPTURE_FAILED: {cap_res}")

                progress_status = prog.get("status", "DATE_ADVANCED")
                if use_baseline:
                    progress_status = "NEXT_CAPTURE_REUSED" if reuse_next_capture else "INITIAL_BASELINE_REUSED"
            finally:
                if should_close_reader and hasattr(live_reader_instance, "close"):
                    live_reader_instance.close()

        # Open Outbox for cycle with BatchContext
        if not is_mock and candidate_intents:
            self._approved_live_context(actual_pid)
        ctx = self._make_context(cycle_id)
        gm_profile, coach_profile = self._make_profiles(ctx)
        phase_grants = self.role_registry.get_phase_grants()

        self.outbox.open_cycle(cycle_id, ctx)

        added_intents = []
        conflicts = []
        unauthorized = []

        if candidate_intents:
            seen_targets: Dict[Tuple[int, str], Any] = {}
            for item in candidate_intents:
                iid = item.get("intent_id", f"{cycle_id}-intent-{len(added_intents)+1}")
                issuer = str(item.get("issuer_role", "GM")).upper()
                params = item.get("parameters", {})
                tid = params.get("team_id", item.get("team_id", params.get("team_a")))

                actor_uid = item.get("actor_uid")
                if not actor_uid and tid is not None:
                    actor_uid = self.role_registry.get_actor(issuer, int(tid))

                if not actor_uid:
                    unauthorized.append({
                        "intent_id": iid,
                        "issuer": issuer,
                        "actor_uid": None,
                        "team_id": tid,
                        "reason": "ACTOR_UID_MISSING_AND_UNAUTHENTICATED"
                    })
                    continue

                aid = item.get("action_id", "PLAYER.EDIT.TENDENCY_BATCH")

                # Trusted role actor check (P0-C & H1-H4)
                if tid is None or not self.role_registry.is_actor_authenticated(issuer, int(tid), actor_uid):
                    unauthorized.append({
                        "intent_id": iid,
                        "issuer": issuer,
                        "actor_uid": actor_uid,
                        "team_id": tid,
                        "reason": "ROLE_ACTOR_NOT_AUTHENTICATED"
                    })
                    continue

                # Check role profile
                prof = gm_profile if issuer == "GM" else (coach_profile if issuer == "COACH" else None)
                if prof is None or aid not in prof.allowed_actions or (actor_uid, aid) not in phase_grants:
                    unauthorized.append({
                        "intent_id": iid,
                        "issuer": issuer,
                        "actor_uid": actor_uid,
                        "action_id": aid,
                        "reason": "ROLE_NOT_AUTHORIZED_FOR_ACTION"
                    })
                    continue

                # Target check
                pid_target = params.get("player_id", item.get("target_player_id"))
                field_id = params.get("field_id", "SHOT_TENDENCY")
                val = params.get("value", item.get("target_value"))
                if val is None and "values" in params:
                    val = params["values"].get(field_id)

                target_key = (int(pid_target) if pid_target is not None else 0, str(field_id))
                if target_key in seen_targets and seen_targets[target_key] != val:
                    conflicts.append({
                        "intent_id": iid,
                        "target_key": target_key,
                        "prior_value": seen_targets[target_key],
                        "conflicting_value": val,
                        "reason": "CONFLICTING_ROLE_TARGET_VALUES"
                    })
                    continue

                seen_targets[target_key] = val

                intent_obj = ActionIntent.decided(
                    iid,
                    actor_uid,
                    aid,
                    params
                )
                self.outbox.add_intent(cycle_id, intent_obj, prof, phase_grants, decision_reason=item.get("reason", "Tactical adjustment"))
                added_intents.append(iid)

        self.state.update({
            "status": HostState.DECISION_OPEN,
            "current_cycle_id": cycle_id,
            "active_plan": None
        })
        self._save_state()

        summary = {
            "status": "DECISION_CYCLE_OPENED",
            "cycle_id": cycle_id,
            "game_date": self.state["current_game_date"],
            "progress_status": progress_status,
            "intents_added_count": len(added_intents),
            "added_intent_ids": added_intents,
            "conflicts_detected": conflicts,
            "unauthorized_rejected": unauthorized,
            "is_no_change_cycle": len(added_intents) == 0
        }
        self._append_ledger({"action": "START_CYCLE", **summary})
        return summary

    def seal_cycle_decisions(
        self,
        cycle_id: str,
        getter_func: Optional[Any] = None,
        expected_pid: Optional[int] = None
    ) -> Dict[str, Any]:
        """Preflights CAS, seals cycle via outbox into RoleActionBatch, bridges to BulkBatch, and computes digest (Gate G06)."""
        if self.state["status"] != HostState.DECISION_OPEN or self.state["current_cycle_id"] != cycle_id:
            raise ValueError(f"Cycle {cycle_id} is not in DECISION_OPEN status (current: {self.state['status']})")

        is_mock = bool(self.state.get("is_offline_mock", False) and self.state.get("is_mock", True))
        draft_intent_dicts = self.outbox.list_intents(cycle_id, status="DRAFT")
        live_no_change = not is_mock and not self.outbox.list_intents(cycle_id)
        live_context = None
        if not is_mock and not live_no_change:
            # LIVE MODE: Mandatory real-time Getter and dynamic PID
            if getter_func is None:
                # No external getter supplied — fetch one internally and require live PID
                getter_func = self._get_live_getter()
                if getter_func is None:
                    raise RuntimeError("LIVE_GETTER_REQUIRED: Cannot seal live cycle without real-time Getter for CAS preflight.")
                # PID is only resolved here when getter is fetched internally.
                # When caller supplies getter_func, they own PID validation context.
                # Strict PID enforcement happens in authorize_and_execute (cannot be bypassed for Native writes).
                if expected_pid is None:
                    try:
                        from refresh import resolve_pid
                        expected_pid = resolve_pid("auto")
                    except Exception as e:
                        raise RuntimeError(f"LIVE_PROCESS_NOT_FOUND: {e}")
            else:
                # Caller supplied getter_func — PID sentinel; real PID check in authorize_and_execute
                if expected_pid is None:
                    expected_pid = 0
        elif is_mock:
            # Mock mode
            if expected_pid is None:
                expected_pid = 5720

        if not is_mock and not live_no_change:
            live_context = self._approved_live_context(expected_pid)
        ctx = self._make_context(cycle_id)
        gm_profile, coach_profile = self._make_profiles(ctx)
        profiles = (gm_profile, coach_profile)
        phase_grants = self.role_registry.get_phase_grants()

        # Inspect draft intents before sealing for CAS preflight
        cas_mismatches = []
        for it in draft_intent_dicts:
            params = json.loads(it["parameters_json"]) if isinstance(it.get("parameters_json"), str) else it.get("parameters", {})
            pid = params.get("player_id") or params.get("player_uid")
            exp_b = params.get("expected_before")
            if getter_func and pid is not None:
                fields_to_check = []
                if "field_id" in params and exp_b is not None:
                    fields_to_check.append((params["field_id"], exp_b))
                elif "values" in params:
                    for f_name, f_val in params["values"].items():
                        exp_val = f_val.get("expected_before") if isinstance(f_val, dict) else exp_b
                        if exp_val is not None:
                            fields_to_check.append((f_name, exp_val))

                for f_name, expected_val in fields_to_check:
                    actual_val = getter_func(pid, f_name)
                    if actual_val != expected_val:
                        cas_mismatches.append({
                            "intent_id": it["intent_id"],
                            "player_id": pid,
                            "field": f_name,
                            "expected_before": expected_val,
                            "actual_getter_before": actual_val,
                            "reason": "CAS_MISMATCH_PREFLIGHT_FAIL_CLOSED"
                        })

        if cas_mismatches:
            self.state["status"] = HostState.CONFLICTED
            self._save_state()
            return {
                "status": "SEAL_FAILED_CAS_MISMATCH",
                "cycle_id": cycle_id,
                "cas_mismatches": cas_mismatches,
                "reason": "One or more intents failed preflight CAS check; cycle remains unsealed."
            }

        # Handle NO_CHANGE cycle cleanly
        if not draft_intent_dicts:
            if not is_mock and not live_no_change:
                raise RuntimeError("NO_DRAFTS_WITH_EXISTING_INTENTS: no-change closure refused")
            plan_digest = sha256_digest(
                canonical_encode({"disposition": "NO_CHANGE", "context": asdict(ctx)})
                if live_no_change else f"EMPTY_NO_CHANGE_CYCLE_{cycle_id}".encode("utf-8")
            )
            batch_id = f"NOOP-BATCH-{cycle_id}"
            now_iso = datetime.now(timezone.utc).isoformat()
            cycle_status = "COMPLETED" if live_no_change else "SEALED"
            with self.outbox._get_connection() as conn:
                cur = conn.cursor()
                if live_no_change:
                    # Serialize the final emptiness check with add_intent, which uses the same write lock.
                    cur.execute("BEGIN IMMEDIATE")
                    cur.execute("SELECT status FROM decision_cycles WHERE cycle_id = ?", (cycle_id,))
                    current = cur.fetchone()
                    if not current or current["status"] != "COLLECTING":
                        raise RuntimeError("NO_CHANGE_CYCLE_CHANGED: cycle is no longer collecting")
                    cur.execute("SELECT 1 FROM decision_intents WHERE cycle_id = ? LIMIT 1", (cycle_id,))
                    if cur.fetchone() is not None:
                        raise RuntimeError("NO_CHANGE_INTENTS_CHANGED: no-change closure refused")
                cur.execute("SELECT revision FROM decision_cycles WHERE cycle_id = ?", (cycle_id,))
                row = cur.fetchone()
                rev = (row["revision"] if row else 0) + 1
                cur.execute("""
                    UPDATE decision_cycles SET
                        status = ?,
                        sealed_batch_id = ?,
                        sealed_digest = ?,
                        sealed_at = ?,
                        revision = ?,
                        updated_at = ?
                    WHERE cycle_id = ?
                """, (cycle_status, batch_id, plan_digest, now_iso, rev, now_iso, cycle_id))
                cur.execute("""
                    INSERT INTO outbox_events (
                        cycle_id, intent_id, event_type, prev_state, new_state, revision, payload_json, timestamp
                    ) VALUES (?, NULL, ?, 'COLLECTING', ?, ?, ?, ?)
                """, (
                    cycle_id,
                    "CYCLE_CLOSED_NO_CHANGE" if live_no_change else "CYCLE_SEALED",
                    cycle_status,
                    rev,
                    json.dumps({
                        "sealed_batch_id": batch_id,
                        "sealed_digest": plan_digest,
                        "sealed_intents_count": 0
                    }),
                    now_iso
                ))
                conn.commit()

            if live_no_change:
                self.state.update(status=HostState.WAITING_CALENDAR_ADVANCE, active_plan=None)
                self._save_state()
                result = {"status": "NO_CHANGE_WAITING_HUMAN_CALENDAR_ADVANCE", "cycle_id": cycle_id,
                          "plan_digest": plan_digest, "executable_intents_count": 0,
                          "unsupported_intents_count": 0, "game_writes": False}
                self._append_ledger({"action": "SEAL_CYCLE", **result})
                return result

            self.state.update({
                "status": HostState.WAITING_HUMAN_EXECUTION_AUTH,
                "active_plan": {
                    "cycle_id": cycle_id,
                    "plan_digest": plan_digest,
                    "executable_count": 0,
                    "unsupported_count": 0,
                    "sealed_at": now_iso
                }
            })
            self._save_state()
            return {
                "status": "PLAN_PREFLIGHTED_WAITING_AUTH",
                "cycle_id": cycle_id,
                "plan_digest": plan_digest,
                "executable_intents_count": 0,
                "unsupported_intents_count": 0,
                "unsupported_details": [],
                "next_required_step": f"Authorize with exact plan_digest: '{plan_digest}'"
            }

        # Seal cycle into immutable RoleActionBatch
        batch_id = f"ROLE-BATCH-{cycle_id}"
        sealed_batch = self.outbox.seal_cycle(cycle_id, aggregate_batch_id=batch_id)

        # Bridge RoleActionBatch into Native BulkBatch
        bridge_res = self.bridge.bridge_batch(
            sealed_batch,
            profiles=profiles,
            phase_grants=phase_grants,
            expected_pid=expected_pid
        )

        plan_digest = ""
        executable_count = 0
        if bridge_res.has_executable_batch and bridge_res.bulk_batch:
            plan_digest = bridge_res.bulk_batch.plan_digest
            executable_count = len(bridge_res.bulk_batch.intents)
        else:
            plan_digest = sha256_digest(f"NO_EXECUTABLE_INTENTS_{cycle_id}".encode("utf-8"))

        unsupported_count = len(bridge_res.unsupported_intents)

        native_plan_digest = plan_digest
        if live_context:
            if (not 1 <= executable_count <= 3 or unsupported_count or len(sealed_batch.intents) != executable_count
                    or any(i.issuer_uid != live_context["actor_uid"] for i in sealed_batch.intents)
                    or any(i.team_id != live_context["team_id"] or i.action_id != "PLAYER_PATCH_TENDENCIES"
                           or i.field_id != "SHOT_TENDENCY" or i.player_id not in live_context["player_ids"]
                           for i in bridge_res.bulk_batch.intents)):
                raise ValueError("LIVE_SCOPE_VIOLATION: sealed batch exceeds the approved S4 delegation")
            plan_digest = sha256_digest({"native_plan_digest": native_plan_digest, "live_context": live_context})

        self.state.update({
            "status": HostState.WAITING_HUMAN_EXECUTION_AUTH,
            "active_plan": {
                "cycle_id": cycle_id,
                "plan_digest": plan_digest,
                "executable_count": executable_count,
                "unsupported_count": unsupported_count,
                "live_context": live_context,
                "sealed_at": datetime.now(timezone.utc).isoformat()
            }
        })
        self._save_state()

        result = {
            "status": "PLAN_PREFLIGHTED_WAITING_AUTH",
            "cycle_id": cycle_id,
            "plan_digest": plan_digest,
            "executable_intents_count": executable_count,
            "unsupported_intents_count": unsupported_count,
            "unsupported_details": [u.get("reason") for u in bridge_res.unsupported_intents],
            "next_required_step": f"Authorize with exact plan_digest: '{plan_digest}'"
        }
        if live_context:
            result.update(live_context=live_context, native_plan_digest=native_plan_digest,
                          items=[asdict(i) for i in bridge_res.bulk_batch.intents])
        self._append_ledger({"action": "SEAL_CYCLE", **result})
        return result

    def authorize_and_execute(
        self,
        cycle_id: str,
        plan_digest: str,
        transport: Optional[Any] = None,
        journal_dir: Optional[Path] = None,
        getter_after_func: Optional[Any] = None,
        expected_pid: Optional[int] = None,
        *,
        live_batch_approval: Optional[Path] = None,
        approved_live_batch_sha256: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Strictly verifies authorization digest, executes batch, verifies readback, and backfills Outbox (Gate G07)."""
        if self.state["status"] not in (HostState.WAITING_HUMAN_EXECUTION_AUTH, HostState.DECISION_SEALED):
            raise ValueError(f"Host not in awaiting authorization state (current: {self.state['status']})")

        active_plan = self.state.get("active_plan")
        if (not active_plan or active_plan.get("cycle_id") != cycle_id
                or active_plan.get("plan_digest") != plan_digest):
            raise ValueError(f"DIGEST_MISMATCH_AUTHORIZATION_DENIED: provided '{plan_digest}' != sealed '{active_plan.get('plan_digest') if active_plan else None}'")

        is_mock = bool(self.state.get("is_offline_mock", False) and self.state.get("is_mock", True))
        if is_mock and not self.role_registry.is_authorized:
            raise ValueError(
                f"ROLE_AUTHORIZATION_REQUIRED: Active save has no verified role authorizations "
                f"(status: {self.role_registry.authorization_status}). Execution aborted fail-closed."
            )

        live_context = None
        if is_mock:
            if transport is None:
                raise RuntimeError(
                    "OFFLINE_MOCK_CANNOT_EXECUTE_WITHOUT_FAKE_TRANSPORT: "
                    "Refusing to construct live native session in mock mode. "
                    "Mock mode is physically prohibited from executing real Native Setters."
                )
        else:
            # LIVE MODE: Verify live process and reject fake transport
            if transport is not None:
                raise RuntimeError(
                    "LIVE_MODE_REJECTS_FAKE_TRANSPORT: "
                    "Live mode requires direct native execution with live GameProcess; "
                    "fake transport is strictly prohibited in live mode."
                )
            try:
                from refresh import resolve_pid
                actual_pid = resolve_pid("auto")
            except Exception as e:
                raise RuntimeError(f"LIVE_PROCESS_NOT_FOUND: NBA2K22.exe is not running ({e})")
            if expected_pid is not None and actual_pid != expected_pid:
                raise RuntimeError("LIVE_PROCESS_CHANGED_SINCE_APPROVAL")
            expected_pid = actual_pid
            live_context = self._approved_live_context(expected_pid)
            if live_context != active_plan.get("live_context"):
                raise RuntimeError("LIVE_CONTEXT_CHANGED_SINCE_APPROVAL")
            if live_batch_approval is None or not approved_live_batch_sha256:
                raise ValueError("EXACT_LIVE_BATCH_AUTHORIZATION_REQUIRED")

        if expected_pid is None:
            expected_pid = 5720

        j_dir = Path(journal_dir) if journal_dir else (self.state_file.parent / "journals" / cycle_id)
        r_dir = j_dir / "runtime"
        # 1. No-change cycle handling
        if active_plan.get("executable_count", 0) == 0:
            if active_plan.get("unsupported_count", 0):
                raise ValueError("UNSUPPORTED_INTENTS_CANNOT_COMPLETE_AS_NO_CHANGE")
            self.state["status"] = HostState.WAITING_CALENDAR_ADVANCE
            self.state["active_plan"] = None
            self._save_state()
            summary = {
                "status": "EXECUTED_NO_CHANGE_SUCCESS",
                "cycle_id": cycle_id,
                "plan_digest": plan_digest,
                "executed_count": 0,
                "success_count": 0,
                "readback_verified": True
            }
            self._append_ledger({"action": "AUTHORIZE_AND_EXECUTE", **summary})
            return summary

        # 2. Reconstruct sealed batch & bridge
        cycle_rec = self.outbox.get_cycle(cycle_id)
        sealed_batch = self.outbox.seal_cycle(cycle_id, aggregate_batch_id=cycle_rec["sealed_batch_id"])

        ctx = self._make_context(cycle_id)
        gm_profile, coach_profile = self._make_profiles(ctx)
        profiles = (gm_profile, coach_profile)
        phase_grants = self.role_registry.get_phase_grants()

        bridge_res = self.bridge.bridge_batch(
            sealed_batch,
            profiles=profiles,
            phase_grants=phase_grants,
            expected_pid=expected_pid
        )
        bulk_batch = bridge_res.bulk_batch
        if bulk_batch is None:
            raise ValueError("SEALED_EXECUTABLE_BATCH_MISSING")

        # Enforce certified live scope allowlist (P0-C)
        if not is_mock:
            for it in bulk_batch.intents:
                act = str(it.action_id).upper()
                fid = str(it.field_id).upper()
                if act not in ("PLAYER.EDIT.TENDENCY_BATCH", "PLAYER_PATCH_TENDENCIES"):
                    raise ValueError(f"LIVE_SCOPE_VIOLATION: action '{it.action_id}' is not in certified live allowlist (PLAYER_PATCH_TENDENCIES only)")
                if fid != "SHOT_TENDENCY":
                    raise ValueError(f"LIVE_SCOPE_VIOLATION: field '{it.field_id}' is not in certified live allowlist (SHOT_TENDENCY only)")
            if (not 1 <= len(bulk_batch.intents) <= 3
                    or len({it.player_id for it in bulk_batch.intents}) != len(bulk_batch.intents)
                    or any(it.team_id != live_context["team_id"] or it.player_id not in live_context["player_ids"]
                           for it in bulk_batch.intents)
                    or any(it.issuer_uid != live_context["actor_uid"] for it in sealed_batch.intents)
                    or len(sealed_batch.intents) != len(bulk_batch.intents)
                    or bridge_res.unsupported_intents):
                raise ValueError("LIVE_SCOPE_VIOLATION: require 1–3 fully bridged single-team intents")
        rebuilt_digest = bulk_batch.plan_digest
        if live_context:
            rebuilt_digest = sha256_digest({"native_plan_digest": rebuilt_digest, "live_context": live_context})
        if (rebuilt_digest != plan_digest or len(bulk_batch.intents) != active_plan["executable_count"]
                or len(bridge_res.unsupported_intents) != active_plan["unsupported_count"]):
            raise ValueError("REBUILT_BATCH_DOES_NOT_MATCH_APPROVED_PLAN")
        if live_context:
            live_batch_authorization_ref = self._verify_live_batch_approval(
                live_batch_approval, approved_live_batch_sha256, cycle_id, plan_digest, bulk_batch, live_context
            )
            getter_before = self._get_fresh_live_getter(
                expected_pid=expected_pid, expected_team=live_context["team_id"],
                expected_players={item.player_id for item in bulk_batch.intents},
                expected_creation_filetime=live_context["epoch"]["creation_filetime"],
            )
            if getter_before is None or any(
                getter_before(item.player_id, item.field_id) != item.expected_before for item in bulk_batch.intents
            ):
                raise RuntimeError("LIVE_CAS_CHANGED_SINCE_APPROVAL: Native UID, roster, contract team or value differs")
            if self._approved_live_context(expected_pid) != live_context:
                raise RuntimeError("LIVE_CONTEXT_CHANGED_DURING_CAS")

        # 3. Execute via BoundedSessionExecutor
        native_context = None
        verifier = None
        j_dir.mkdir(parents=True, exist_ok=True)
        r_dir.mkdir(parents=True, exist_ok=True)
        if live_context:
            native_context = LiveExecutionContext(
                authorization_ref=live_batch_authorization_ref,
                allowed_action_ids=frozenset({"PLAYER_PATCH_TENDENCIES", "MULTI_CHUNK_BOUNDED_SESSION"}),
                maximum_game_calls=500,
                enabled=True,
                expected_pid=expected_pid,
            )
            verifier = {"game_build_sha256": contracts.BUILD, "plan_digest": bulk_batch.plan_digest}
        executor = BoundedSessionExecutor(
            journal_dir=j_dir,
            runtime_dir=r_dir,
            fake_runner=transport,
            live_context=native_context,
            verifier=verifier,
        )
        self.outbox.claim_execution(cycle_id, plan_digest, native_items=bulk_batch.intents if live_context else None)
        self.state["status"] = HostState.UNKNOWN_LOCKED
        self._save_state()
        try:
            return self._execute_claimed(cycle_id, plan_digest, bulk_batch, bridge_res, executor,
                                         r_dir, is_mock, expected_pid, getter_after_func, live_context)
        except Exception as exc:
            cycle = self.outbox.get_cycle(cycle_id)
            if cycle and cycle["status"] == "SEALED":
                uncertain = [{"intent_id": row["intent_id"], "outcome": "UNKNOWN_EXECUTION_OUTCOME",
                              "reason": f"Execution or verification interrupted: {type(exc).__name__}"}
                             for row in self.outbox.list_intents(cycle_id, status="SEALED")]
                self.outbox.record_execution_receipts(cycle_id, uncertain, evidence_ref=f"evidence-{cycle_id}")
            raise

    @staticmethod
    def _verify_live_batch_approval(path, approved_sha, cycle_id, plan_digest, batch, context):
        """Check the private receipt against a digest provided by the Human operator.

        The caller supplies the trusted pin out of band. This checks exact bytes and
        scope; it does not authenticate a Human from a self-declared reference.
        """
        raw = Path(path).read_bytes()
        if hashlib.sha256(raw).hexdigest() != approved_sha:
            raise ValueError("LIVE_BATCH_APPROVAL_HASH_MISMATCH")
        approval = json.loads(raw)
        expected = {
            "schema_version": "nba2k22.s4.batch_approval.v1",
            "cycle_id": cycle_id,
            "plan_digest": plan_digest,
            "native_plan_digest": batch.plan_digest,
            "live_context": context,
            "items": json.loads(canonical_encode([asdict(item) for item in batch.intents])),
        }
        if canonical_encode({key: approval.get(key) for key in expected}) != canonical_encode(expected):
            raise ValueError("LIVE_BATCH_APPROVAL_SCOPE_MISMATCH")
        ref = approval.get("approval_ref")
        if not isinstance(ref, str) or not ref.strip():
            raise ValueError("LIVE_BATCH_APPROVAL_REFERENCE_MISSING")
        now = datetime.now(timezone.utc)
        if not datetime.fromisoformat(approval["approved_at"]) <= now < datetime.fromisoformat(approval["expires_at"]):
            raise ValueError("LIVE_BATCH_APPROVAL_OUTSIDE_APPROVED_TIME")
        return ref

    def _execute_claimed(self, cycle_id, plan_digest, bulk_batch, bridge_res, executor,
                         r_dir, is_mock, expected_pid, getter_after_func, live_context):
        t0 = time.perf_counter()
        session_summary = executor.execute_batch(bulk_batch, max_chunk_size=50)
        elapsed_s = time.perf_counter() - t0

        journal_receipts = executor.journal.load_receipts()

        # 4. Independent fresh readback (P0-A)
        fresh_getter_func = None
        if is_mock:
            fresh_getter_func = getter_after_func
        else:
            fresh_getter_func = self._get_fresh_live_getter(
                expected_pid=expected_pid, expected_team=live_context["team_id"],
                expected_players={item.player_id for item in bulk_batch.intents},
                expected_creation_filetime=live_context["epoch"]["creation_filetime"],
            )
            if self._approved_live_context(expected_pid) != live_context:
                raise RuntimeError("LIVE_CONTEXT_CHANGED_DURING_EXECUTION")

        readback_passed = True
        readback_details = []
        fresh_timestamp = datetime.now(timezone.utc).isoformat()
        if fresh_getter_func is None:
            readback_passed = False
        else:
            for item in bulk_batch.intents:
                observed_after = fresh_getter_func(item.player_id, item.field_id)
                matched = (observed_after == item.value)
                readback_details.append({
                    "intent_id": item.intent_id,
                    "player_id": item.player_id,
                    "team_id": item.team_id,
                    "field_id": item.field_id,
                    "expected_before": item.expected_before,
                    "target_value": item.value,
                    "observed_after": observed_after,
                    "matched": matched,
                    "read_timestamp": fresh_timestamp,
                    "source": "OFFLINE_FIXTURE" if is_mock else "NBA2K22_POST_EXECUTION_MEMORY"
                })
                if not matched:
                    readback_passed = False

        independent_readback_report = {
            "schema_version": "nba2k22.rea.independent_readback.v1",
            "timestamp": fresh_timestamp,
            "pid": expected_pid,
            "intent_count": len(bulk_batch.intents),
            "missed_count": sum(1 for d in readback_details if not d["matched"]),
            "all_100_persisted_in_game": (len(readback_details) > 0 and all(d["matched"] for d in readback_details)),
            "verified_items": [
                {
                    "intent_id": d["intent_id"],
                    "player_id": d["player_id"],
                    "readback_getter": d["observed_after"],
                    "target_tendency": d["target_value"],
                    "confirmed": d["matched"]
                }
                for d in readback_details
            ]
        }

        # 5. Multi-layer batch validation (P0-B)
        planned_chunks = executor.planner.plan(bulk_batch, max_chunk_size=50)

        # Retrieve authentic raw Native REA messages from runtime directory (evidence.json)
        genuine_raw_messages: List[Dict[str, Any]] = []
        evidence_paths = list(r_dir.glob("*/evidence.json"))
        for ev_path in evidence_paths:
            try:
                ev_data = json.loads(ev_path.read_text(encoding="utf-8-sig"))
                genuine_raw_messages.extend(ev_data.get("normalized_result", {}).get("messages", []))
            except Exception:
                pass

        has_genuine_raw_evidence = (len(genuine_raw_messages) > 0)

        # In live mode, genuine raw REA Frida IPC evidence is strictly required
        if not is_mock:
            validation_raw_messages = genuine_raw_messages
            require_native_transport = True
        elif has_genuine_raw_evidence:
            validation_raw_messages = genuine_raw_messages
            require_native_transport = True
        else:
            # Offline mock mode with fake runner: DO NOT falsely synthesize raw Frida messages
            validation_raw_messages = []
            require_native_transport = False

        validation_res = validate_batch_execution(
            batch=bulk_batch,
            chunks=planned_chunks,
            raw_messages=validation_raw_messages,
            receipts=journal_receipts,
            independent_readback=independent_readback_report,
            require_native_transport_evidence=require_native_transport
        )
        if not is_mock:
            errors = validation_res["errors"]
            if len(evidence_paths) != 1 or session_summary.get("frida_attach_count") != 1:
                errors.append("Expected one fresh REA evidence envelope and one attachment")
            else:
                target = json.loads(evidence_paths[0].with_name("target.json").read_text(encoding="utf-8-sig"))
                if target.get("pid") != expected_pid or target.get("exe_sha256") != contracts.BUILD:
                    errors.append("REA target PID or executable build does not match the approved plan")
            self._check_live_journal(executor.journal, bulk_batch, planned_chunks, genuine_raw_messages,
                                     journal_receipts, errors)
            validation_res["validation_passed"] = not errors
        batch_validation_passed = validation_res.get("validation_passed") is True
        atomic_write_json(r_dir / "independent-readback.json", independent_readback_report)
        atomic_write_json(r_dir / "batch-validation.json", validation_res)

        # 6. Map receipts back to Outbox (Gate G07)
        outbox_receipts = self.bridge.map_receipts_to_outbox(journal_receipts, bridge_res)
        has_unknown = (
            any("UNKNOWN" in str(r.get("outcome") or "").upper() for r in outbox_receipts)
            or any("UNKNOWN" in str(getattr(r, "outcome", None) or r.get("outcome") or "").upper() for r in journal_receipts)
            or session_summary.get("metrics", {}).get("num_unknown", 0) > 0
        )

        successful_outcomes = {"SUCCESS", "SUCCESS_APPLIED", "VERIFIED_SUCCESS",
                               "UNCHANGED_ALREADY_TARGET", "NOOP", "REUSED_HISTORICAL_RECEIPT"}
        all_reconciled = (
            batch_validation_passed and readback_passed and not has_unknown
            and all(obr.get("outcome") in successful_outcomes for obr in outbox_receipts)
        )
        for obr in outbox_receipts:
            if not is_mock and not batch_validation_passed:
                obr["outcome"] = "UNKNOWN_UNVERIFIED_EXECUTION"
                obr["reason"] = "Live batch evidence is incomplete or invalid"
                has_unknown = True
                continue
            if obr.get("outcome") not in successful_outcomes:
                continue
            if not all_reconciled:
                obr["outcome"] = "UNVERIFIED_EXECUTION_FAILED" if is_mock else "UNKNOWN_UNVERIFIED_EXECUTION"
                obr["reason"] = "Batch evidence or fresh readback did not establish verified completion"
                has_unknown = has_unknown or not is_mock
            elif obr["outcome"] in ("SUCCESS", "SUCCESS_APPLIED"):
                obr["outcome"] = "VERIFIED_SUCCESS"

        # Record execution receipts into Outbox DB
        self.outbox.record_execution_receipts(
            cycle_id,
            outbox_receipts,
            evidence_ref=f"evidence-{cycle_id}"
        )

        # Fail-closed checks on UNKNOWN and readback failure
        if has_unknown:
            self.state["status"] = HostState.UNKNOWN_LOCKED
            self._save_state()
            summary = {
                "status": "STOPPED_UNKNOWN_LOCKED",
                "cycle_id": cycle_id,
                "plan_digest": plan_digest,
                "elapsed_seconds": round(elapsed_s, 4),
                "executed_count": len(outbox_receipts),
                "readback_verified": False,
                "validation_errors": validation_res.get("errors", []),
                "reason": "UNKNOWN execution outcome detected in journal receipts; Host locked to prevent blind retries."
            }
            self._append_ledger({"action": "AUTHORIZE_AND_EXECUTE", **summary})
            return summary

        if not all_reconciled:
            self.state["status"] = HostState.STOPPED_PARTIAL
            self._save_state()
            summary = {
                "status": ("STOPPED_READBACK_FAILED" if not readback_passed else
                           "STOPPED_VALIDATION_FAILED" if not batch_validation_passed else "STOPPED_PARTIAL"),
                "cycle_id": cycle_id,
                "plan_digest": plan_digest,
                "elapsed_seconds": round(elapsed_s, 4),
                "executed_count": len(outbox_receipts),
                "readback_verified": readback_passed,
                "readback_details": [d for d in readback_details if not d["matched"]][:5],
                "validation_errors": validation_res.get("errors", []),
                "reason": "Independent readback or batch validation failed against memory; active plan preserved, cycle halted."
            }
            self._append_ledger({"action": "AUTHORIZE_AND_EXECUTE", **summary})
            return summary

        success_count = sum(1 for r in outbox_receipts if r.get("outcome") in ("SUCCESS", "SUCCESS_APPLIED", "VERIFIED_SUCCESS"))
        noop_count = len(outbox_receipts) - success_count

        self.state.update({
            "status": HostState.WAITING_CALENDAR_ADVANCE,
            "active_plan": None
        })
        self._save_state()

        result = {
            "status": "EXECUTED_AND_READBACK_RECORDED",
            "cycle_id": cycle_id,
            "plan_digest": plan_digest,
            "elapsed_seconds": round(elapsed_s, 4),
            "executed_count": len(outbox_receipts),
            "success_count": success_count,
            "noop_count": noop_count,
            "failure_count": 0,
            "readback_verified": True,
            "batch_validation_passed": True,
            "readback_details": readback_details[:5]
        }
        self._append_ledger({"action": "AUTHORIZE_AND_EXECUTE", **result})
        return result

    @staticmethod
    def _check_live_journal(journal, batch, chunks, raw_messages, receipts, errors):
        """Check that the single fresh REA session, its claims, and journal agree."""
        manifest = json.loads((journal.root / f"batch_{batch.header.batch_id}.json").read_text(encoding="utf-8-sig"))
        if (manifest.get("plan_digest") != batch.plan_digest
                or manifest.get("header") != asdict(batch.header)
                or manifest.get("intent_count") != len(batch.intents)):
            errors.append("Execution journal manifest differs from the approved native batch")
        claims = [json.loads(path.read_text(encoding="utf-8-sig")) for path in journal.claims_dir.glob("claim_*.json")]
        claim_map = {claim.get("chunk_id"): claim for claim in claims}
        if len(claims) != len(chunks) or set(claim_map) != {chunk.chunk_id for chunk in chunks}:
            errors.append("Execution journal claims do not cover exactly the approved chunks")
        for chunk in chunks:
            claim = claim_map.get(chunk.chunk_id, {})
            if (claim.get("state") != "COMPLETED" or claim.get("plan_digest") != batch.plan_digest
                    or claim.get("chunk_digest") != chunk.chunk_digest
                    or claim.get("batch_id") != batch.header.batch_id
                    or claim.get("save_instance_id") != batch.header.save_instance_id
                    or [(i.get("intent_id"), i.get("expected_before"), i.get("value")) for i in claim.get("intents", [])]
                    != [(i.intent_id, i.expected_before, i.value) for i in chunk.intents]):
                errors.append(f"Execution journal claim differs from approved chunk {chunk.chunk_id}")
        raw_receipts = [
            (payload.get("chunk_id"), row)
            for msg in raw_messages
            for payload in [msg.get("payload", msg)]
            if payload.get("kind") == "chunk-execution-result"
            for row in payload.get("receipts", [])
        ]
        raw_by_id = {row.get("intent_id"): (chunk_id, row) for chunk_id, row in raw_receipts}
        if len(raw_receipts) != len(receipts) or len(raw_by_id) != len(receipts):
            errors.append("Raw REA receipts do not match journal receipt count or uniqueness")
        for item in receipts:
            chunk_id, raw = raw_by_id.get(item.intent_id, (None, {}))
            fields = ("team_id", "player_id", "field_id", "expected_before", "requested", "outcome",
                      "getter_before", "getter_after", "raw_after", "unaltered_fields_check")
            if chunk_id != item.chunk_id or any(raw.get(field) != getattr(item, field) for field in fields):
                errors.append(f"Raw REA receipt differs from journal item {item.intent_id}")

    def advance_calendar_check(
        self,
        next_cycle_id: str,
        mock_advanced_date: Optional[str] = None,
        reader: Any = None
    ) -> Dict[str, Any]:
        """Checks game calendar advance and prepares for next cycle."""
        if self.state["status"] in (HostState.UNKNOWN_LOCKED, HostState.STOPPED_PARTIAL):
            return {
                "status": "ADVANCE_REFUSED_CYCLE_NOT_CLEARED",
                "current_status": self.state["status"],
                "reason": f"Cannot advance calendar while Host is in abnormal/locked state '{self.state['status']}'. Active plan is preserved pending manual resolution."
            }

        save_dir = Path(self.state["save_directory"])
        target_db = Path(self.state["database_file"])
        orchestrator = CalendarSimOrchestrator(
            save_directory=save_dir,
            loaded_filename=self.state["loaded_filename"],
            database_path=target_db
        )

        curr_date = self.state.get("current_game_date", "2021-10-25")
        is_mock = bool(self.state.get("is_offline_mock", False) and self.state.get("is_mock", True)) or (mock_advanced_date is not None)

        if is_mock:
            new_date = mock_advanced_date or curr_date
            if reader:
                prog = orchestrator.inspect_calendar_progress(reader)
                if prog.get("status") == "INCOMPLETE_GAME_IN_PROGRESS":
                    return {
                        "status": "INCOMPLETE_GAME_IN_PROGRESS",
                        "reason": "Game is currently playing in memory; please finish game in NBA2K22 before advancing."
                    }
        else:
            # LIVE MODE: Verify game process, calendar progression, and date
            try:
                from refresh import resolve_pid
                actual_pid = resolve_pid("auto")
            except Exception as e:
                raise RuntimeError(f"LIVE_PROCESS_NOT_FOUND: NBA2K22.exe is not running ({e})")

            live_reader_instance = reader if reader is not None else ReadOnlyGameProcess(actual_pid)
            should_close = (reader is None)
            try:
                prog = orchestrator.inspect_calendar_progress(live_reader_instance)
                if prog.get("status") == "INCOMPLETE_GAME_IN_PROGRESS":
                    return {
                        "status": "INCOMPLETE_GAME_IN_PROGRESS",
                        "reason": "Game is currently playing in memory; please finish game in NBA2K22 before advancing."
                    }

                from schedule_reader import collect_schedule
                sched = collect_schedule(live_reader_instance, with_calendar=True, read_final_boxes=False)
                cal = sched.get("calendar") or {}
                mem_date = cal.get("current_native_iso_date")
                if not mem_date:
                    return {
                        "status": "CALENDAR_READ_FAILED",
                        "reason": "Could not read current native game date from memory."
                    }

                if mem_date <= curr_date and not prog.get("new_final_game_detected"):
                    return {
                        "status": "CALENDAR_NOT_ADVANCED",
                        "current_host_date": curr_date,
                        "memory_date": mem_date,
                        "reason": f"In-game calendar date '{mem_date}' has not advanced past cycle date '{curr_date}', and no new final game was detected."
                    }
                new_date = mem_date
            finally:
                if should_close and hasattr(live_reader_instance, "close"):
                    live_reader_instance.close()

        self.state.update({
            "status": HostState.NEXT_CAPTURED,
            "current_game_date": new_date,
            "current_cycle_id": next_cycle_id
        })
        self._save_state()

        receipt = {
            "status": "CALENDAR_ADVANCE_VERIFIED",
            "previous_date": curr_date,
            "current_date": new_date,
            "next_cycle_id": next_cycle_id,
            "ready_for_cycle": True
        }
        self._append_ledger({"action": "ADVANCE_CALENDAR_CHECK", **receipt})
        return receipt

    def get_status(self) -> Dict[str, Any]:
        """Read-only query of current host lifecycle, outbox statistics, and ledger."""
        cid = self.state.get("current_cycle_id")
        outbox_summary = None
        if cid:
            try:
                outbox_summary = self.outbox.get_outcome_summary(cid)
            except Exception:
                outbox_summary = None
        return {
            "host_status": self.state["status"],
            "save_id": self.state.get("save_id"),
            "worldline_id": self.state.get("worldline_id"),
            "database_file": self.state.get("database_file"),
            "current_game_date": self.state.get("current_game_date"),
            "current_cycle_id": cid,
            "active_plan": self.state.get("active_plan"),
            "outbox_summary": outbox_summary,
            "last_updated": self.state.get("updated_at")
        }

    def pause(self) -> Dict[str, Any]:
        prev_status = self.state.get("status")
        self.state["pre_pause_status"] = prev_status
        self.state["status"] = HostState.PAUSED
        self._save_state()
        receipt = {
            "status": "HOST_PAUSED",
            "pre_pause_status": prev_status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self._append_ledger({"action": "PAUSE", **receipt})
        return receipt

    def resume(self) -> Dict[str, Any]:
        if self.state.get("status") == HostState.PAUSED:
            pre = self.state.get("pre_pause_status", HostState.WAITING_CALENDAR_ADVANCE)
            if pre == HostState.UNKNOWN_LOCKED:
                receipt = {
                    "status": "RESUME_DENIED_UNKNOWN_LOCKED",
                    "reason": "Host was in UNKNOWN_LOCKED before pause; automatic resume is prohibited to prevent blind retries.",
                    "current_status": HostState.UNKNOWN_LOCKED
                }
                self.state["status"] = HostState.UNKNOWN_LOCKED
                self._save_state()
                self._append_ledger({"action": "RESUME", **receipt})
                return receipt

            self.state["status"] = pre
            self._save_state()
        receipt = {"status": "HOST_RESUMED", "current_status": self.state["status"]}
        self._append_ledger({"action": "RESUME", **receipt})
        return receipt
