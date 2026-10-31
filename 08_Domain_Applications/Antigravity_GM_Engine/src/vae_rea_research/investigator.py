from __future__ import annotations

import datetime
import json
import os
import subprocess
from typing import Any, Dict, List, Optional, Tuple

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
        stated_question: str,
        observable_target: str,
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
            # Task packet strictly forbids unauthorized live writes
            return SingleFieldRecord(
                field_id=entry.field_id,
                family=entry.family,
                source_ordinal=entry.source_ordinal,
                iteration=iteration,
                sweep=sweep,
                stated_question=stated_question,
                observable_target=observable_target,
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

        # Static REA / Native evidence lookup
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

        if entry.family == "player_tendency":
            stride_hex = "0xDF0"
            unmeasured_effects = [
                "3d_live_court_shot_frequency",
                "calendar_simulation_fga_distribution",
                "ace_tactical_override_threshold",
            ]
            # Check player.json
            player_json_path = os.path.join(
                self.repo_root, "08_Domain_Applications", "Antigravity_GM_Engine",
                "config", "state_io_native", "player.json"
            )
            in_player_json = False
            if os.path.exists(player_json_path):
                try:
                    with open(player_json_path, "r", encoding="utf-8") as f:
                        pdata = json.load(f)
                    offsets = pdata.get("TENDENCY_OFFSETS", {})
                    # candidate key format: tendency.SHOT_TENDENCY -> SHOT_TENDENCY
                    short_key = entry.candidate_native_key.replace("tendency.", "")
                    if short_key in offsets:
                        in_player_json = True
                        primary_sources.append("08_Domain_Applications/Antigravity_GM_Engine/config/state_io_native/player.json")
                except Exception:
                    pass

            # Check R04B
            r04b_path = os.path.join(
                self.repo_root, "08_Domain_Applications", "Antigravity_GM_Engine",
                "docs", "game_mechanics", "catalogs", "R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json"
            )
            in_r04b = False
            if os.path.exists(r04b_path):
                try:
                    with open(r04b_path, "r", encoding="utf-8") as f:
                        r04b_data = json.load(f)
                    for slot in r04b_data.get("native_slots", []):
                        if slot.get("native_registry_key") == entry.candidate_native_key:
                            in_r04b = True
                            primary_sources.append("08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/catalogs/R04B_TENDENCY_PLAYSTYLE_RESEARCH_V1.json")
                            break
                except Exception:
                    pass

            # Check 07_PLAYER_TENDENCY_GUIDE.md
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
            elif entry.source_status == "NAMED_NATIVE":
                native_grade = NativeIdentityGrade.SOURCE_SPEC
                research_status = FieldResearchStatus.EVIDENCE_ADDED
            else:
                native_grade = NativeIdentityGrade.UNVERIFIED
                research_status = FieldResearchStatus.UNKNOWN

        record = SingleFieldRecord(
            field_id=entry.field_id,
            family=entry.family,
            source_ordinal=entry.source_ordinal,
            iteration=iteration,
            sweep=sweep,
            stated_question=stated_question,
            observable_target=observable_target,
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
            next_improvement_direction="Perform live memory reading hook under authorized session to trace assembly consumer RVA",
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
        chk["run_state"] = "IN_PROGRESS"
        chk["cursor"] = new_cursor
        chk["next_field_id"] = next_id
        chk["processed_in_current_sweep"] = chk.get("processed_in_current_sweep", 0) + 1
        if record.research_status == FieldResearchStatus.EVIDENCE_ADDED:
            chk["evidence_added"] = chk.get("evidence_added", 0) + 1
        elif record.research_status == FieldResearchStatus.BLOCKED_FIELD:
            chk["blocked_fields"] = chk.get("blocked_fields", 0) + 1
        chk["last_completed_field"] = record.field_id
        chk["latest_completed_commit"] = record.commit_sha
        chk["actual_executor_model"] = record.model_provenance

        with open(self.checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(chk, f, indent=2, ensure_ascii=False)
