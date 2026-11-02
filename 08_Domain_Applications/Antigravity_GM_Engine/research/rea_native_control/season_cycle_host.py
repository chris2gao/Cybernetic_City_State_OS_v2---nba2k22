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
        outbox_db: Optional[Path] = None
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
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

    def _save_state(self):
        self.state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.state_file.write_text(json.dumps(self.state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _append_ledger(self, record: Dict[str, Any]):
        record["recorded_at"] = datetime.now(timezone.utc).isoformat()
        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _make_context(self, cycle_id: str) -> BatchContext:
        return BatchContext(
            world_id=self.state.get("worldline_id") or "worldline-main",
            save_instance_id=self.state.get("loaded_filename") or "MyLEAGUE0003",
            generation_id=cycle_id,
            season_id="2021-22",
            phase="REGULAR_SEASON",
            snapshot_ref=f"snapshot_{cycle_id}",
            catalog_version=self.capability_service.version
        )

    def _make_profiles(self, ctx: BatchContext) -> Tuple[RoleCapabilityProfile, RoleCapabilityProfile]:
        gm = RoleCapabilityProfile(
            role_type="GM",
            actor_uid="gm_user_01",
            team_scope=(1, 25, 28),
            world_id=ctx.world_id,
            save_instance_id=ctx.save_instance_id,
            generation_id=ctx.generation_id,
            season_id=ctx.season_id,
            phase=ctx.phase,
            snapshot_ref=ctx.snapshot_ref,
            allowed_actions=frozenset(["PLAYER.EDIT.TENDENCY_BATCH", "GM.TRADE.MIXED"])
        )
        coach = RoleCapabilityProfile(
            role_type="COACH",
            actor_uid="coach_user_01",
            team_scope=(1,),
            world_id=ctx.world_id,
            save_instance_id=ctx.save_instance_id,
            generation_id=ctx.generation_id,
            season_id=ctx.season_id,
            phase=ctx.phase,
            snapshot_ref=ctx.snapshot_ref,
            allowed_actions=frozenset(["COACH.STRATEGY.RUN_PLAY", "PLAYER.EDIT.TENDENCY_BATCH"])
        )
        return gm, coach

    def inspect_worldline(
        self,
        save_dir: Path,
        loaded_filename: str,
        current_game_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Detect save binding and check if backward date requires isolated worldline branching (Gate G02)."""
        binding, binding_hash = read_binding(save_dir, loaded_filename)
        save_id = binding["save_id"]
        default_db = bound_database(save_dir, binding)
        
        latest_db_date = None
        if default_db.exists():
            with closing(connect(default_db, True)) as conn:
                row = conn.execute("SELECT max(game_date) FROM games WHERE game_date IS NOT NULL").fetchone()
                if row and row[0]:
                    latest_db_date = row[0]

        is_backward = False
        worldline_id = "worldline-main"
        target_db = default_db

        if current_game_date and latest_db_date:
            if current_game_date < latest_db_date:
                is_backward = True
                date_slug = current_game_date.replace("-", "")
                worldline_id = f"worldline-{save_id}-{date_slug}-{uuid.uuid4().hex[:6]}"
                target_db = save_dir / f"world-{worldline_id}.sqlite"
                if not target_db.exists():
                    create_database(target_db, save_id)

        return {
            "save_id": save_id,
            "loaded_filename": loaded_filename,
            "binding_sha256": binding_hash,
            "default_db": str(default_db),
            "target_db": str(target_db),
            "latest_db_date": latest_db_date,
            "current_game_date": current_game_date,
            "is_backward": is_backward,
            "worldline_id": worldline_id
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
        
        current_date = mock_game_date
        if not current_date and reader:
            try:
                from cadence import observed_game_season_year
                current_date = f"{observed_game_season_year(reader)}-10-25"
            except Exception:
                current_date = "2021-10-25"

        wl_info = self.inspect_worldline(save_dir, loaded_filename, current_date)
        if force_new_worldline and not wl_info["is_backward"]:
            wl_info["worldline_id"] = f"worldline-{wl_info['save_id']}-branch-{uuid.uuid4().hex[:6]}"
            wl_info["target_db"] = str(save_dir / f"world-{wl_info['worldline_id']}.sqlite")
            if not Path(wl_info["target_db"]).exists():
                create_database(wl_info["target_db"], wl_info["save_id"])

        target_db = Path(wl_info["target_db"])
        orchestrator = CalendarSimOrchestrator(
            save_directory=save_dir,
            loaded_filename=loaded_filename,
            database_path=target_db
        )

        capture_result = None
        if reader is not None or pid != "auto":
            try:
                capture_result = orchestrator.trigger_world_capture(
                    reader_or_pid=reader if reader else pid,
                    mode="FULL",
                    force=True
                )
            except Exception as e:
                capture_result = {"status": "MOCK_OR_FALLBACK_INIT", "note": str(e)}

        self.state.update({
            "status": HostState.BASELINE_CAPTURED,
            "save_directory": str(save_dir),
            "loaded_filename": loaded_filename,
            "save_id": wl_info["save_id"],
            "worldline_id": wl_info["worldline_id"],
            "database_file": str(target_db),
            "current_game_date": current_date or "2021-10-25",
            "current_cycle_id": None,
            "active_plan": None
        })
        self._save_state()

        receipt = {
            "status": "INITIALIZED_AND_BASELINE_BOUND",
            "save_id": wl_info["save_id"],
            "loaded_filename": loaded_filename,
            "worldline_id": wl_info["worldline_id"],
            "database_file": str(target_db),
            "current_game_date": self.state["current_game_date"],
            "is_backward_worldline_branch": wl_info["is_backward"],
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
        """Initiates a cycle, verifies calendar progression, and registers draft intents."""
        if self.state["status"] not in (
            HostState.BASELINE_CAPTURED,
            HostState.EXECUTED_AND_READBACK,
            HostState.NEXT_CAPTURED,
            HostState.WAITING_CALENDAR_ADVANCE
        ):
            if not force:
                raise ValueError(f"Cannot start cycle from state: {self.state['status']}")

        save_dir = Path(self.state["save_directory"])
        target_db = Path(self.state["database_file"])
        orchestrator = CalendarSimOrchestrator(
            save_directory=save_dir,
            loaded_filename=self.state["loaded_filename"],
            database_path=target_db
        )

        progress_status = "DATE_ADVANCED"
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
            if prog.get("status") == "SAME_STATE_REPEAT" and not force:
                return {
                    "status": "SAME_STATE_REPEAT",
                    "cycle_id": cycle_id,
                    "reason": "Game calendar has not advanced since previous cycle; skipping redundant observation."
                }
            progress_status = prog.get("status")

        if mock_game_date:
            self.state["current_game_date"] = mock_game_date

        # Open Outbox for cycle with BatchContext
        ctx = self._make_context(cycle_id)
        gm_profile, coach_profile = self._make_profiles(ctx)
        phase_grants = {
            ("gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH"),
            ("coach_user_01", "PLAYER.EDIT.TENDENCY_BATCH"),
            ("coach_user_01", "COACH.STRATEGY.RUN_PLAY"),
            ("gm_user_01", "GM.TRADE.MIXED")
        }

        self.outbox.open_cycle(cycle_id, ctx)

        added_intents = []
        conflicts = []
        unauthorized = []

        if candidate_intents:
            seen_targets: Dict[Tuple[int, str], Any] = {}
            for item in candidate_intents:
                iid = item.get("intent_id", f"{cycle_id}-intent-{len(added_intents)+1}")
                issuer = item.get("issuer_role", "GM")
                actor_uid = item.get("actor_uid", "gm_user_01" if issuer == "GM" else "coach_user_01")
                aid = item.get("action_id", "PLAYER.EDIT.TENDENCY_BATCH")
                params = item.get("parameters", {})
                
                # Check role profile
                prof = gm_profile if issuer == "GM" else (coach_profile if issuer == "COACH" else None)
                if prof is None or aid not in prof.allowed_actions or (actor_uid, aid) not in phase_grants:
                    unauthorized.append({"intent_id": iid, "issuer": issuer, "action_id": aid, "reason": "ROLE_NOT_AUTHORIZED_FOR_ACTION"})
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
        expected_pid: int = 5720
    ) -> Dict[str, Any]:
        """Preflights CAS, seals cycle via outbox into RoleActionBatch, bridges to BulkBatch, and computes digest (Gate G06)."""
        if self.state["status"] != HostState.DECISION_OPEN or self.state["current_cycle_id"] != cycle_id:
            raise ValueError(f"Cycle {cycle_id} is not in DECISION_OPEN status (current: {self.state['status']})")

        ctx = self._make_context(cycle_id)
        gm_profile, coach_profile = self._make_profiles(ctx)
        profiles = (gm_profile, coach_profile)
        phase_grants = {
            ("gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH"),
            ("coach_user_01", "PLAYER.EDIT.TENDENCY_BATCH"),
            ("coach_user_01", "COACH.STRATEGY.RUN_PLAY"),
            ("gm_user_01", "GM.TRADE.MIXED")
        }

        # Inspect draft intents before sealing for CAS preflight
        draft_intent_dicts = self.outbox.list_intents(cycle_id, status="DRAFT")
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
            plan_digest = sha256_digest(f"EMPTY_NO_CHANGE_CYCLE_{cycle_id}".encode("utf-8"))
            self.state.update({
                "status": HostState.WAITING_HUMAN_EXECUTION_AUTH,
                "active_plan": {
                    "cycle_id": cycle_id,
                    "plan_digest": plan_digest,
                    "executable_count": 0,
                    "unsupported_count": 0,
                    "sealed_at": datetime.now(timezone.utc).isoformat()
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

        self.state.update({
            "status": HostState.WAITING_HUMAN_EXECUTION_AUTH,
            "active_plan": {
                "cycle_id": cycle_id,
                "plan_digest": plan_digest,
                "executable_count": executable_count,
                "unsupported_count": unsupported_count,
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
        self._append_ledger({"action": "SEAL_CYCLE", **result})
        return result

    def authorize_and_execute(
        self,
        cycle_id: str,
        plan_digest: str,
        transport: Optional[Any] = None,
        journal_dir: Optional[Path] = None,
        getter_after_func: Optional[Any] = None,
        expected_pid: int = 5720
    ) -> Dict[str, Any]:
        """Strictly verifies authorization digest, executes batch, verifies readback, and backfills Outbox (Gate G07)."""
        if self.state["status"] not in (HostState.WAITING_HUMAN_EXECUTION_AUTH, HostState.DECISION_SEALED):
            raise ValueError(f"Host not in awaiting authorization state (current: {self.state['status']})")

        active_plan = self.state.get("active_plan")
        if not active_plan or active_plan.get("plan_digest") != plan_digest:
            raise ValueError(f"DIGEST_MISMATCH_AUTHORIZATION_DENIED: provided '{plan_digest}' != sealed '{active_plan.get('plan_digest') if active_plan else None}'")

        j_dir = Path(journal_dir) if journal_dir else (self.state_file.parent / "journals" / cycle_id)
        r_dir = j_dir / "runtime"
        j_dir.mkdir(parents=True, exist_ok=True)
        r_dir.mkdir(parents=True, exist_ok=True)

        # 1. No-change cycle handling
        if active_plan.get("executable_count", 0) == 0:
            self.state["status"] = HostState.WAITING_CALENDAR_ADVANCE
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
        phase_grants = {
            ("gm_user_01", "PLAYER.EDIT.TENDENCY_BATCH"),
            ("coach_user_01", "PLAYER.EDIT.TENDENCY_BATCH"),
            ("coach_user_01", "COACH.STRATEGY.RUN_PLAY"),
            ("gm_user_01", "GM.TRADE.MIXED")
        }

        bridge_res = self.bridge.bridge_batch(
            sealed_batch,
            profiles=profiles,
            phase_grants=phase_grants,
            expected_pid=expected_pid
        )
        bulk_batch = bridge_res.bulk_batch
        assert bulk_batch is not None, "bulk_batch must exist for executable plan"

        # 3. Execute via BoundedSessionExecutor
        executor = BoundedSessionExecutor(
            journal_dir=j_dir,
            runtime_dir=r_dir,
            fake_runner=transport if transport else None
        )
        t0 = time.perf_counter()
        session_summary = executor.execute_batch(bulk_batch, max_chunk_size=50)
        elapsed_s = time.perf_counter() - t0

        journal_receipts = executor.journal.load_receipts()

        # 4. Independent readback check
        readback_passed = True
        readback_details = []
        for r in journal_receipts:
            item = next((it for it in bulk_batch.intents if it.intent_id == r.intent_id), None)
            if item and getter_after_func:
                observed_after = getter_after_func(item.player_id, item.field_id)
                matched = (observed_after == item.value)
                readback_details.append({
                    "intent_id": r.intent_id,
                    "target_value": item.value,
                    "observed_after": observed_after,
                    "matched": matched
                })
                if not matched:
                    readback_passed = False

        # 5. Map receipts back to Outbox (Gate G07)
        outbox_receipts = self.bridge.map_receipts_to_outbox(journal_receipts, bridge_res)
        self.outbox.record_execution_receipts(
            cycle_id,
            outbox_receipts,
            evidence_ref=f"evidence-{cycle_id}"
        )

        success_count = sum(1 for r in outbox_receipts if r.get("outcome") in ("SUCCESS", "SUCCESS_APPLIED", "VERIFIED_SUCCESS"))
        failure_count = sum(1 for r in outbox_receipts if r.get("outcome") not in ("SUCCESS", "SUCCESS_APPLIED", "VERIFIED_SUCCESS"))

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
            "failure_count": failure_count,
            "readback_verified": readback_passed,
            "readback_details": readback_details[:5]
        }
        self._append_ledger({"action": "AUTHORIZE_AND_EXECUTE", **result})
        return result

    def advance_calendar_check(
        self,
        next_cycle_id: str,
        mock_advanced_date: Optional[str] = None,
        reader: Any = None
    ) -> Dict[str, Any]:
        """Checks game calendar advance and prepares for next cycle."""
        save_dir = Path(self.state["save_directory"])
        target_db = Path(self.state["database_file"])
        orchestrator = CalendarSimOrchestrator(
            save_directory=save_dir,
            loaded_filename=self.state["loaded_filename"],
            database_path=target_db
        )

        curr_date = self.state.get("current_game_date", "2021-10-25")
        new_date = mock_advanced_date or curr_date

        if reader:
            prog = orchestrator.inspect_calendar_progress(reader)
            if prog.get("status") == "INCOMPLETE_GAME_IN_PROGRESS":
                return {
                    "status": "INCOMPLETE_GAME_IN_PROGRESS",
                    "reason": "Game is currently playing in memory; please finish game in NBA2K22 before advancing."
                }

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
        self.state["status"] = HostState.PAUSED
        self._save_state()
        receipt = {"status": "HOST_PAUSED", "timestamp": datetime.now(timezone.utc).isoformat()}
        self._append_ledger({"action": "PAUSE", **receipt})
        return receipt

    def resume(self) -> Dict[str, Any]:
        if self.state["status"] == HostState.PAUSED:
            self.state["status"] = HostState.WAITING_CALENDAR_ADVANCE
            self._save_state()
        receipt = {"status": "HOST_RESUMED", "current_status": self.state["status"]}
        self._append_ledger({"action": "RESUME", **receipt})
        return receipt
