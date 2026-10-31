from __future__ import annotations

import datetime
import json
import os
import subprocess
from typing import Any, Dict, List, Optional

from src.vae_rea_research.contracts import (
    FieldEntry,
    FieldResearchStatus,
    NativeIdentityGrade,
    SingleFieldRecord,
)
from src.vae_rea_research.queue_manager import SharedQueueManager


class SingleFieldInvestigator:
    """
    Executes single-field REA research iterations under the constraints of SINGLE_FIELD_LOOP_CONTRACT_V1.
    Supports single-field execution and automated deterministic sweep loops.
    """

    RUN_DIR_REL = os.path.join(
        "01_os", "07_content", "_runs",
        "run-20261030-nba2k22-vae-rea-single-field-loop-001"
    )

    def __init__(self, repo_root: Optional[str] = None) -> None:
        if repo_root is None:
            cur = os.path.abspath(__file__)
            repo_root = os.path.abspath(os.path.join(cur, "..", "..", "..", "..", ".."))
        self.repo_root = repo_root
        self.queue_mgr = SharedQueueManager(repo_root=self.repo_root)
        self.run_dir = os.path.join(self.repo_root, self.RUN_DIR_REL)
        self.records_dir = os.path.join(self.run_dir, "06_执行", "field_records")
        self.ledger_path = os.path.join(self.run_dir, "06_执行", "iteration_ledger.jsonl")
        self.checkpoint_path = os.path.join(self.run_dir, "06_执行", "current_checkpoint.json")
        os.makedirs(self.records_dir, exist_ok=True)

        # Cache static documents for fast repeated lookups during sweeps
        self._player_json: Optional[Dict[str, Any]] = None
        self._r04b_json: Optional[Dict[str, Any]] = None
        self._r06a_json: Optional[Dict[str, Any]] = None
        self._settings_json: Optional[Dict[str, Any]] = None
        self._load_catalogs()

    def _load_catalogs(self) -> None:
        p_json_path = os.path.join(
            self.repo_root, "08_Domain_Applications", "Antigravity_GM_Engine",
            "config", "state_io_native", "player.json"
        )
        if os.path.exists(p_json_path):
            with open(p_json_path, "r", encoding="utf-8") as f:
                self._player_json = json.load(f)

        r04b_path = os.path.join(
            self.repo_root, "08_Domain_Applications", "Antigravity_GM_Engine",
            "docs", "game_mechanics", "catalogs", "R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json"
        )
        if os.path.exists(r04b_path):
            with open(r04b_path, "r", encoding="utf-8") as f:
                self._r04b_json = json.load(f)

        r06a_path = os.path.join(
            self.repo_root, "08_Domain_Applications", "Antigravity_GM_Engine",
            "docs", "game_mechanics", "catalogs", "R06A_WORLD_GAMEPLAY_SIMULATION_SETTINGS_V1.json"
        )
        if os.path.exists(r06a_path):
            with open(r06a_path, "r", encoding="utf-8") as f:
                self._r06a_json = json.load(f)

        settings_path = os.path.join(
            self.repo_root, "08_Domain_Applications", "Antigravity_GM_Engine",
            "config", "state_io_native", "settings.json"
        )
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                self._settings_json = json.load(f)

    def get_current_checkpoint(self) -> Dict[str, Any]:
        if os.path.exists(self.checkpoint_path):
            with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "schema_version": "nba2k22.vae.single_field_checkpoint.v1",
            "task_id": "NBA2K22-VAE-REA-SINGLE-FIELD-LOOP-20261030-001",
            "run_state": "DISPATCHED_NOT_EXECUTED",
            "sweep": 1,
            "cursor": 0,
            "next_field_id": "TENDENCY_NATIVE_001",
            "processed_in_current_sweep": 0,
            "evidence_added": 0,
            "unknown_fields": 0,
            "blocked_fields": 0,
            "review_readiness": "NOT_READY",
            "last_completed_field": None,
            "actual_executor_model": "Gemini Flash 3.8 (Human-assigned label)",
            "latest_completed_commit": None,
        }

    def _get_current_head_sha(self) -> str:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return res.stdout.strip()
        except Exception:
            return "UNKNOWN"

    def execute_single_field(
        self,
        target_field_id: str,
        stated_question: Optional[str] = None,
        observable_target: Optional[str] = None,
        attempt_live_mutation: bool = False,
        authorized_mutation_token: Optional[str] = None,
    ) -> SingleFieldRecord:
        """
        Processes exactly one field_id with a single stated research question.
        """
        chk = self.get_current_checkpoint()
        sweep = chk.get("sweep", 1)
        cursor = chk.get("cursor", 0)
        entry = self.queue_mgr.get_entry_by_id(target_field_id)

        if not entry:
            raise ValueError(f"Target field_id '{target_field_id}' not found in shared queue.")

        iteration = chk.get("processed_in_current_sweep", 0) + 1
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        current_head = self._get_current_head_sha()

        # Gate on live mutation attempts:
        if attempt_live_mutation:
            return SingleFieldRecord(
                field_id=entry.field_id,
                family=entry.family,
                source_ordinal=entry.source_ordinal,
                iteration=iteration,
                sweep=sweep,
                stated_question=stated_question or f"Attempt live write on {entry.field_id}",
                observable_target=observable_target or "Strict rejection as BLOCKED_FIELD",
                candidate_native_key=entry.candidate_native_key,
                display_name=entry.display_name,
                source_status=entry.source_status,
                offset_hex=entry.offset_hex,
                stride_hex=None,
                byte_width=1,
                declared_raw_range=entry.declared_raw_range,
                native_identity_grade=NativeIdentityGrade.UNVERIFIED,
                ui_mapping_status="UNKNOWN",
                ui_export_label=None,
                consumer_path_status="UNKNOWN",
                game_effect_status="UNKNOWN",
                research_status=FieldResearchStatus.BLOCKED_FIELD,
                primary_sources=[self.queue_mgr.GIT_QUEUE_REF],
                blocker_reason="PROTECTED_ACTION_NO_LIVE_WRITE_AUTHORITY",
                unmeasured_effects=["all_game_effects"],
                next_improvement_direction="Submit scoped OS authorization request for live write trial",
                timestamp_iso=timestamp,
                model_provenance="Gemini Flash 3.8 (Human-assigned label)",
                commit_sha=current_head,
            )

        # Build investigation per family
        primary_sources: List[str] = [self.queue_mgr.GIT_QUEUE_REF]
        native_grade = NativeIdentityGrade.UNVERIFIED
        stride_hex: Optional[str] = None
        byte_width = 1
        ui_mapping_status = "UNKNOWN_UNMAPPED"
        ui_export_label = None
        consumer_path = "UNKNOWN_UNVERIFIED_ASSEMBLY"
        game_effect_status = "UNKNOWN"
        research_status = FieldResearchStatus.UNKNOWN
        unmeasured_effects: List[str] = []
        next_improvement = ""

        if entry.family == "player_tendency":
            stride_hex = "0xDF0"
            unmeasured_effects = [
                "3d_live_court_shot_frequency",
                "calendar_simulation_fga_distribution",
                "ace_tactical_override_threshold",
            ]
            short_key = entry.candidate_native_key.replace("tendency.", "")
            in_player_json = False
            if self._player_json:
                offsets = self._player_json.get("TENDENCY_OFFSETS", {})
                if short_key in offsets:
                    in_player_json = True
                    primary_sources.append("08_Domain_Applications/Antigravity_GM_Engine/config/state_io_native/player.json")

            in_r04b = False
            if self._r04b_json:
                for slot in self._r04b_json.get("native_slots", []):
                    if slot.get("native_registry_key") == entry.candidate_native_key:
                        in_r04b = True
                        primary_sources.append("08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json")
                        break

            guide_path = os.path.join(
                self.repo_root, "08_Domain_Applications", "Antigravity_GM_Engine",
                "docs", "07_PLAYER_TENDENCY_GUIDE.md"
            )
            if os.path.exists(guide_path):
                primary_sources.append("08_Domain_Applications/Antigravity_GM_Engine/docs/07_PLAYER_TENDENCY_GUIDE.md")

            if in_player_json and in_r04b:
                native_grade = NativeIdentityGrade.REA_LOCATED
                ui_mapping_status = "UNVERIFIED_NO_POSITIONAL_INFERENCE"
                consumer_path = "UNVERIFIED_AI_SHOT_EVALUATOR_ASSEMBLY"
                game_effect_status = "UNQUANTIFIED_SEPARATE_SIM_VS_3D_STUDY"
                research_status = FieldResearchStatus.EVIDENCE_ADDED
                question_default = f"Verify native offset, byte width, value range, UI mapping status and consumer path for {entry.display_name} in PC22 MyLEAGUE"
                target_default = f"Confirm offset {entry.offset_hex} in player struct with stride 0xDF0, uint8 range [0, 100], and unverified UI/consumer status"
                next_improvement = "Perform live memory reading hook under authorized session to trace assembly consumer RVA"
            elif entry.source_status == "NAMED_NATIVE":
                native_grade = NativeIdentityGrade.SOURCE_SPEC
                research_status = FieldResearchStatus.EVIDENCE_ADDED
                question_default = f"Locate native source specification for {entry.display_name}"
                target_default = f"Document candidate offset {entry.offset_hex} and note lack of full live readback"
                next_improvement = "Cross-reference disassembly RVA with memory scanner"
            else:
                # 51 unmapped native tendency slots
                native_grade = NativeIdentityGrade.UNVERIFIED
                research_status = FieldResearchStatus.UNKNOWN
                question_default = f"Verify whether raw tendency slot at offset {entry.offset_hex} has confirmed semantic name or consumer in current project registries"
                target_default = f"Record unverified status for unknown raw byte slot {entry.field_id}"
                next_improvement = "Hook memory read at offset {0} in live match to identify consumer calling context".format(entry.offset_hex)

        elif entry.family == "coach_settings":
            primary_sources.append("08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/guides/K04_COACH_AND_PLAYS.md")
            native_grade = NativeIdentityGrade.SOURCE_SPEC
            ui_mapping_status = "UNVERIFIED_IN_GAME_COACH_MENU"
            consumer_path = "UNVERIFIED_ADAPTIVE_COACHING_ENGINE"
            game_effect_status = "UNQUANTIFIED_COACH_SIM_VS_3D_STUDY"
            research_status = FieldResearchStatus.EVIDENCE_ADDED
            unmeasured_effects = [
                "gameplan_poe_3d_execution",
                "coach_system_pace_fatigue_penalty",
                "bench_depth_rotation_enforcement",
            ]
            question_default = f"Identify native memory address, UI option and game engine consumer for coach setting {entry.candidate_native_key} in PC22 MyLEAGUE"
            target_default = f"Record K04 conceptual specification and identify unverified memory offsets/effects for {entry.display_name}"
            next_improvement = "Trace coach gameplan data structures via REA memory scan during live timeout"

        elif entry.family == "world_settings":
            primary_sources.append("08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/catalogs/R06A_WORLD_GAMEPLAY_SIMULATION_SETTINGS_V1.json")
            candidate_info: Optional[Dict[str, Any]] = None
            if self._r06a_json:
                for cand in self._r06a_json.get("registry_candidates", []):
                    if cand.get("id") == entry.candidate_native_key:
                        candidate_info = cand
                        break

            if candidate_info:
                primary_sources.append("08_Domain_Applications/Antigravity_GM_Engine/config/state_io_native/settings.json")
                native_grade = NativeIdentityGrade.REA_LOCATED
                slot_rva = candidate_info.get("slot_rva", "UNKNOWN_RVA")
                storage_type = candidate_info.get("storage_type", "uint32")
                byte_width = 4 if storage_type in ("uint32", "float") else 1
                ui_mapping_status = "UNVERIFIED_MENU_SYNC"
                consumer_path = "UNVERIFIED_LIVE_3D_OR_SIM_ENGINE"
                game_effect_status = "UNQUANTIFIED_FROM_PROFILE_NOT_VERIFIED"
                research_status = FieldResearchStatus.EVIDENCE_ADDED
                unmeasured_effects = [
                    "options_menu_roundtrip_persistence",
                    "simulation_engine_adherence",
                    "live_gameplay_rule_enforcement",
                ]
                question_default = f"Verify slot RVA, offset, storage type, profile range, and runtime verification status for world setting {entry.candidate_native_key}"
                target_default = f"Confirm static R06A registry candidate parameters (RVA {slot_rva}, offset {entry.offset_hex}) and record lack of live readback verification"
                next_improvement = f"Hook memory address at slot RVA {slot_rva} + offset {entry.offset_hex} to verify live game readback"
            else:
                native_grade = NativeIdentityGrade.SOURCE_SPEC
                research_status = FieldResearchStatus.EVIDENCE_ADDED
                question_default = f"Document candidate world setting {entry.candidate_native_key}"
                target_default = f"Record declared parameters and verify R06A reference"
                next_improvement = "Locate candidate in settings.json or R06A"

        else:
            question_default = f"Investigate unknown setting family {entry.family} for {entry.field_id}"
            target_default = "Record UNKNOWN"
            next_improvement = "Classify family"

        actual_question = stated_question or question_default
        actual_target = observable_target or target_default

        record = SingleFieldRecord(
            field_id=entry.field_id,
            family=entry.family,
            source_ordinal=entry.source_ordinal,
            iteration=iteration,
            sweep=sweep,
            stated_question=actual_question,
            observable_target=actual_target,
            candidate_native_key=entry.candidate_native_key,
            display_name=entry.display_name,
            source_status=entry.source_status,
            offset_hex=entry.offset_hex,
            stride_hex=stride_hex,
            byte_width=byte_width,
            declared_raw_range=entry.declared_raw_range,
            native_identity_grade=native_grade,
            ui_mapping_status=ui_mapping_status,
            ui_export_label=ui_export_label,
            consumer_path_status=consumer_path,
            game_effect_status=game_effect_status,
            research_status=research_status,
            primary_sources=primary_sources,
            blocker_reason=None,
            unmeasured_effects=unmeasured_effects,
            next_improvement_direction=next_improvement,
            timestamp_iso=timestamp,
            model_provenance="Gemini Flash 3.8 (Human-assigned label)",
            commit_sha=current_head,
        )

        # Save record
        self._save_record(record)
        # Append ledger
        self._append_ledger(record)
        # Advance checkpoint
        self._advance_checkpoint(record, cursor)

        return record

    def run_sweep(self, max_fields: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes a deterministic single-field iteration loop across the shared queue.
        Stops when max_fields is reached or when the queue sweep is completed.
        """
        processed_count = 0
        chk = self.get_current_checkpoint()
        cursor = chk.get("cursor", 0)

        while cursor < self.queue_mgr.total_count:
            if max_fields is not None and processed_count >= max_fields:
                break

            entry = self.queue_mgr.get_entry_at(cursor)
            if not entry:
                break

            self.execute_single_field(target_field_id=entry.field_id)
            processed_count += 1

            # reload checkpoint cursor
            chk = self.get_current_checkpoint()
            cursor = chk.get("cursor", 0)

        final_chk = self.get_current_checkpoint()
        return {
            "processed_count": processed_count,
            "final_cursor": final_chk.get("cursor", 0),
            "total_count": self.queue_mgr.total_count,
            "sweep_complete": final_chk.get("cursor", 0) >= self.queue_mgr.total_count,
            "evidence_added": final_chk.get("evidence_added", 0),
            "unknown_fields": final_chk.get("unknown_fields", 0),
            "blocked_fields": final_chk.get("blocked_fields", 0),
        }

    def _save_record(self, record: SingleFieldRecord) -> None:
        rec_path = os.path.join(self.records_dir, f"{record.field_id}.json")
        with open(rec_path, "w", encoding="utf-8") as f:
            json.dump(record.to_dict(), f, indent=2, ensure_ascii=False)

    def _append_ledger(self, record: SingleFieldRecord) -> None:
        entry = {
            "iteration": record.iteration,
            "sweep": record.sweep,
            "field_id": record.field_id,
            "family": record.family,
            "stated_question": record.stated_question,
            "status": record.research_status.value,
            "native_grade": record.native_identity_grade.value,
            "offset_hex": record.offset_hex,
            "ui_mapping": record.ui_mapping_status,
            "consumer": record.consumer_path_status,
            "effect": record.game_effect_status,
            "primary_sources_count": len(record.primary_sources),
            "commit_sha": record.commit_sha,
            "timestamp": record.timestamp_iso,
        }
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _advance_checkpoint(self, record: SingleFieldRecord, old_cursor: int) -> None:
        new_cursor = old_cursor + 1
        next_entry = self.queue_mgr.get_entry_at(new_cursor)
        next_id = next_entry.field_id if next_entry else "SWEEP_COMPLETE"

        chk = self.get_current_checkpoint()
        chk["run_state"] = "IN_PROGRESS" if new_cursor < self.queue_mgr.total_count else "SWEEP_1_COMPLETED"
        chk["cursor"] = new_cursor
        chk["next_field_id"] = next_id
        chk["processed_in_current_sweep"] = chk.get("processed_in_current_sweep", 0) + 1
        if record.research_status == FieldResearchStatus.EVIDENCE_ADDED:
            chk["evidence_added"] = chk.get("evidence_added", 0) + 1
        elif record.research_status == FieldResearchStatus.UNKNOWN:
            chk["unknown_fields"] = chk.get("unknown_fields", 0) + 1
        elif record.research_status == FieldResearchStatus.BLOCKED_FIELD:
            chk["blocked_fields"] = chk.get("blocked_fields", 0) + 1
        chk["last_completed_field"] = record.field_id
        chk["latest_completed_commit"] = record.commit_sha
        chk["actual_executor_model"] = record.model_provenance

        with open(self.checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(chk, f, indent=2, ensure_ascii=False)
