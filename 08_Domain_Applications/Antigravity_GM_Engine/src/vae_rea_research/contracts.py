from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class FieldResearchStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    EVIDENCE_ADDED = "EVIDENCE_ADDED"
    UNKNOWN = "UNKNOWN"
    BLOCKED_FIELD = "BLOCKED_FIELD"
    NEEDS_REPEAT = "NEEDS_REPEAT"
    CANDIDATE_REVIEWABLE = "CANDIDATE_REVIEWABLE"


class NativeIdentityGrade(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    SOURCE_SPEC = "SOURCE_SPEC"
    REA_LOCATED = "REA_LOCATED"
    ASSEMBLY_CONSUMED = "ASSEMBLY_CONSUMED"
    LIVE_RECEIPT = "LIVE_RECEIPT"


@dataclass(frozen=True)
class FieldEntry:
    field_id: str
    family: str
    source_ordinal: int
    candidate_native_key: str
    display_name: str
    source_status: str
    offset_hex: Optional[str]
    declared_raw_range: List[int]
    ui_mapping: str
    consumer: str
    effect: str
    source_ref: str


@dataclass
class SingleFieldRecord:
    field_id: str
    family: str
    source_ordinal: int
    iteration: int
    sweep: int
    stated_question: str
    observable_target: str
    candidate_native_key: str
    display_name: str
    source_status: str
    offset_hex: Optional[str]
    stride_hex: Optional[str]
    byte_width: int
    declared_raw_range: List[int]
    native_identity_grade: NativeIdentityGrade
    ui_mapping_status: str
    ui_export_label: Optional[str]
    consumer_path_status: str
    game_effect_status: str
    research_status: FieldResearchStatus
    primary_sources: List[str]
    blocker_reason: Optional[str] = None
    unmeasured_effects: List[str] = field(default_factory=list)
    next_improvement_direction: str = ""
    timestamp_iso: str = ""
    model_provenance: str = "Gemini Flash 3.8 (Human-assigned label)"
    commit_sha: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_id": self.field_id,
            "family": self.family,
            "source_ordinal": self.source_ordinal,
            "iteration": self.iteration,
            "sweep": self.sweep,
            "stated_question": self.stated_question,
            "observable_target": self.observable_target,
            "candidate_native_key": self.candidate_native_key,
            "display_name": self.display_name,
            "source_status": self.source_status,
            "offset_hex": self.offset_hex,
            "stride_hex": self.stride_hex,
            "byte_width": self.byte_width,
            "declared_raw_range": self.declared_raw_range,
            "native_identity_grade": self.native_identity_grade.value,
            "ui_mapping_status": self.ui_mapping_status,
            "ui_export_label": self.ui_export_label,
            "consumer_path_status": self.consumer_path_status,
            "game_effect_status": self.game_effect_status,
            "research_status": self.research_status.value,
            "primary_sources": self.primary_sources,
            "blocker_reason": self.blocker_reason,
            "unmeasured_effects": self.unmeasured_effects,
            "next_improvement_direction": self.next_improvement_direction,
            "timestamp_iso": self.timestamp_iso,
            "model_provenance": self.model_provenance,
            "commit_sha": self.commit_sha,
        }
