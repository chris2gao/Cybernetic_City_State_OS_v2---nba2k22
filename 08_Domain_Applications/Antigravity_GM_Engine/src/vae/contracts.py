"""
VAE Data Contracts and Business Object Validation (R01–R09).
Implements revised Stage02 contract v2 with:
- P0-01~P0-04, P1-05~P1-07, F02~F07 bug fixes
- Human V2 Three-Pillar Requirements: Native Capabilities, Mechanism Registry, Role Data Views.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Set
import hashlib
import json
import uuid


class EvidenceTier(str, Enum):
    SOURCE_RESEARCH = "SOURCE_RESEARCH"
    STATIC_CODE = "STATIC_CODE"
    OFFLINE_FIXTURE = "OFFLINE_FIXTURE"
    LIVE_READBACK = "LIVE_READBACK"
    UI_VERIFIED = "UI_VERIFIED"
    SAVE_RELOAD_VERIFIED = "SAVE_RELOAD_VERIFIED"
    COMPETITIVE_OBSERVED = "COMPETITIVE_OBSERVED"
    UNKNOWN = "UNKNOWN"


class RoleType(str, Enum):
    GM = "GM"
    COACH = "COACH"
    PLAYER = "PLAYER"
    WORLD_ADMIN = "WORLD_ADMIN"


class SnapshotStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    STATIC_SPEC = "STATIC_SPEC"          # Read from offline static configs/specs (settings.json, court.json)
    OFFLINE_FIXTURE = "OFFLINE_FIXTURE"  # Hardcoded test/dev fixture
    CAPTURED = "CAPTURED"                # Verified readback from active live game process/save
    MODE_UNVERIFIED = "MODE_UNVERIFIED"
    ERROR = "ERROR"


class DiagnosisStatus(str, Enum):
    EVIDENCE_GAP = "EVIDENCE_GAP"
    DIAGNOSED = "DIAGNOSED"
    NO_CHANGE = "NO_CHANGE"
    INCONCLUSIVE = "INCONCLUSIVE"


class PreflightStatus(str, Enum):
    PLANNED = "PLANNED"
    READY = "READY"
    BLOCKED = "BLOCKED"


class ReceiptStatus(str, Enum):
    NOT_RUN = "NOT_RUN"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    PERMISSION_DENIED = "PERMISSION_DENIED"


class ReadbackStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    INCONSISTENT = "INCONSISTENT"
    SKIPPED = "SKIPPED"


class ObservationStatus(str, Enum):
    INSUFFICIENT = "INSUFFICIENT"
    NOT_OBSERVED = "NOT_OBSERVED"        # Execution was NOT_RUN or no game observation performed
    OFFLINE_FIXTURE = "OFFLINE_FIXTURE"  # Synthetic or simulated sample fixture
    RECORDED = "RECORDED"                # Strictly reserved for verified real live game observations
    INCOMPARABLE = "INCOMPARABLE"


class EvaluationOutcome(str, Enum):
    INCONCLUSIVE = "INCONCLUSIVE"
    OBSERVED_TREND_POSITIVE = "OBSERVED_TREND_POSITIVE"
    OBSERVED_TREND_NEGATIVE = "OBSERVED_TREND_NEGATIVE"
    NO_APPARENT_CHANGE = "NO_APPARENT_CHANGE"
    CONFIRMED_CONTROLLED = "CONFIRMED_CONTROLLED"  # Only valid under controlled experiments
    REFUTED_CONTROLLED = "REFUTED_CONTROLLED"


class RevisionStatus(str, Enum):
    PENDING_REVISION = "PENDING_REVISION"
    APPENDED = "APPENDED"
    SKIPPED = "SKIPPED"
    DUPLICATE_REJECTED = "DUPLICATE_REJECTED"


class FeedbackStatus(str, Enum):
    OPTIONAL = "OPTIONAL"
    SUBMITTED = "SUBMITTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


# -------------------------------------------------------------------------
# R01: ProfileSnapshot
# -------------------------------------------------------------------------
@dataclass
class ProfileSnapshot:
    snapshot_id: str
    save_id: Optional[str]
    game_build: str
    game_mode: str
    scene: str
    side: str  # "USER" | "CPU" | "NEUTRAL"
    field_id: str
    raw_value: Any
    display_value: Any
    unit: str
    source_ref: str
    captured_at: Optional[str]
    freshness: str
    status: SnapshotStatus = SnapshotStatus.UNKNOWN

    def validate(self) -> None:
        if not self.snapshot_id or not self.field_id:
            raise ValueError("R01: snapshot_id and field_id are required")
        if self.side not in ["USER", "CPU", "NEUTRAL"]:
            raise ValueError(f"R01: invalid side {self.side}")
        # P0-01: Static configs cannot claim CAPTURED
        if self.status == SnapshotStatus.CAPTURED:
            if not self.save_id or self.save_id == "OFFLINE_DEFAULT" or self.captured_at == "STATIC_SOURCE":
                raise ValueError("R01 P0-01 VIOLATION: Static source cannot claim SnapshotStatus.CAPTURED")
            if not self.captured_at:
                raise ValueError("R01: captured_at is required when status is CAPTURED")


# -------------------------------------------------------------------------
# R02: IssueDiagnosis
# -------------------------------------------------------------------------
@dataclass
class IssueDiagnosis:
    issue_id: str
    game_ref: str
    observed_symptom: str
    basketball_source_ref: str
    plausible_causes: List[str]
    confounders: List[str]
    no_change_decision: bool = False
    status: DiagnosisStatus = DiagnosisStatus.EVIDENCE_GAP

    def validate(self) -> None:
        if not self.issue_id or not self.observed_symptom:
            raise ValueError("R02: issue_id and observed_symptom are required")
        if not isinstance(self.plausible_causes, list):
            raise ValueError("R02: plausible_causes must be a list")


# -------------------------------------------------------------------------
# R03: TrialPreflight (Fixes F07: Blocked state nullability; Fixes P0-02: Safety gates)
# -------------------------------------------------------------------------
@dataclass
class TrialPreflight:
    trial_id: str
    target_identity: str
    before_ref: str
    expected_before: Any
    proposed_after: Any
    metric_primary: str
    metrics_side_effect: List[str]
    observation_window: str
    restore_plan: Optional[Dict[str, Any]] = None
    technical_path: Optional[str] = None
    authorization_ref: Optional[str] = None
    block_reason: Optional[str] = None
    block_timestamp: Optional[str] = None
    status: PreflightStatus = PreflightStatus.PLANNED

    def validate(self) -> None:
        if not self.trial_id or not self.target_identity:
            raise ValueError("R03: trial_id and target_identity are required")
        if self.status == PreflightStatus.READY:
            if not self.restore_plan:
                raise ValueError("R03: restore_plan is mandatory when status is READY")
            if not self.technical_path:
                raise ValueError("R03: technical_path is mandatory when status is READY")
            if not self.authorization_ref:
                raise ValueError("R03: authorization_ref is mandatory when status is READY")
            # P0-02: Dev mock authorization tokens cannot grant READY
            if "DRYRUN" in self.authorization_ref or "MOCK" in self.authorization_ref:
                raise ValueError(f"R03 P0-02 VIOLATION: Mock authorization {self.authorization_ref} cannot enter READY")
        elif self.status == PreflightStatus.BLOCKED:
            if not self.block_reason:
                raise ValueError("R03: block_reason is mandatory when status is BLOCKED")


# -------------------------------------------------------------------------
# R04: ExecutionReceipt (Fixes F07: Not-run state nullability)
# -------------------------------------------------------------------------
@dataclass
class ExecutionReceipt:
    trial_id: str
    action_id: str
    auth_ref: str
    actual_scene: str
    technical_request_ref: str
    technical_response: Optional[Dict[str, Any]] = None
    executed_at: Optional[str] = None
    skip_or_abort_reason: Optional[str] = None
    status: ReceiptStatus = ReceiptStatus.NOT_RUN

    def validate(self) -> None:
        if not self.trial_id or not self.action_id:
            raise ValueError("R04: trial_id and action_id are required")
        if self.status == ReceiptStatus.EXECUTED:
            if self.technical_response is None or not self.executed_at:
                raise ValueError("R04: technical_response and executed_at are mandatory when EXECUTED")
        elif self.status in [ReceiptStatus.NOT_RUN, ReceiptStatus.REJECTED, ReceiptStatus.PERMISSION_DENIED]:
            if not self.skip_or_abort_reason:
                raise ValueError(f"R04: skip_or_abort_reason is mandatory when status is {self.status}")


# -------------------------------------------------------------------------
# R05: TechnicalReadback (Fixes P1-06: Structured multi-layer readback)
# -------------------------------------------------------------------------
@dataclass
class TechnicalReadback:
    trial_id: str
    verification_level: str  # "L0" | "L1" | "L2" | "L3" | "ALL"
    getter_before_ref: Optional[str] = None
    getter_after_ref: Optional[str] = None
    ui_ref: Optional[str] = None
    save_reload_ref: Optional[str] = None
    conflicts: Optional[List[str]] = None
    layers: Dict[str, str] = field(default_factory=lambda: {
        "L0_memory": "UNVERIFIED",
        "L1_process": "UNVERIFIED",
        "L2_ui_settings": "UNVERIFIED",
        "L3_save_reload": "UNVERIFIED"
    })
    status: ReadbackStatus = ReadbackStatus.UNVERIFIED

    def validate(self) -> None:
        if not self.trial_id or not self.verification_level:
            raise ValueError("R05: trial_id and verification_level are required")
        if self.status == ReadbackStatus.VERIFIED:
            if not self.getter_before_ref or not self.getter_after_ref:
                raise ValueError("R05: getter before/after refs are mandatory when VERIFIED")


# -------------------------------------------------------------------------
# R06: CompetitiveObservation (Fixes F02 & P0-04: Strict Comparability Context)
# -------------------------------------------------------------------------
@dataclass
class CompetitiveObservation:
    trial_id: str
    game_id: str
    save_id: str
    game_date: str
    engine_path: str  # "3D_FAST_SIM" | "3D_PLAYED" | "CALENDAR_SIM"
    side: str         # "USER" | "CPU" | "NEUTRAL"
    controller_assigned: bool
    played_normalize_on: bool
    sim_normalize_on: bool
    played_quarter_minutes: int  # 1..12
    sim_quarter_minutes: int     # 1..12
    base_source_ref: str
    metrics: Dict[str, Any]
    human_note: str = ""
    confounders: List[str] = field(default_factory=list)
    source_refs: List[str] = field(default_factory=list)
    status: ObservationStatus = ObservationStatus.INSUFFICIENT

    def validate(self) -> None:
        if not self.trial_id or not self.game_id:
            raise ValueError("R06: trial_id and game_id are required")
        if not self.save_id:
            raise ValueError("R06: save_id is required")
        if not self.engine_path:
            raise ValueError("R06: engine_path is required")
        if not (1 <= self.played_quarter_minutes <= 12):
            raise ValueError("R06: played_quarter_minutes must be between 1 and 12")
        if not (1 <= self.sim_quarter_minutes <= 12):
            raise ValueError("R06: sim_quarter_minutes must be between 1 and 12")
        if not self.base_source_ref:
            raise ValueError("R06: base_source_ref is required for strict provenance")
        # P0-03: Synthetic fixture cannot be marked RECORDED
        if self.status == ObservationStatus.RECORDED:
            if not self.source_refs or any("SYNTHETIC" in s or "OFFLINE" in s for s in self.source_refs):
                raise ValueError("R06 P0-03 VIOLATION: Offline/synthetic data cannot claim ObservationStatus.RECORDED")

    def is_comparable_with(self, other: "CompetitiveObservation") -> Tuple[bool, str]:
        """
        Fixes F02 & P0-04: Enforces save_id, engine_path, side, controller,
        dual Normalize, quarter lengths, and base_source.
        """
        # P0-04: Strict save_id matching
        if self.save_id != other.save_id:
            return False, f"save_id mismatch: {self.save_id} vs {other.save_id}"
        # P0-04: Strict engine_path matching
        if self.engine_path != other.engine_path:
            return False, f"engine_path mismatch: {self.engine_path} vs {other.engine_path}"
        # F02 Context matching
        if self.side != other.side:
            return False, f"Side mismatch: {self.side} vs {other.side}"
        if self.controller_assigned != other.controller_assigned:
            return False, f"Controller assignment mismatch: {self.controller_assigned} vs {other.controller_assigned}"
        if self.played_normalize_on != other.played_normalize_on:
            return False, f"Played Normalize mismatch: {self.played_normalize_on} vs {other.played_normalize_on}"
        if self.sim_normalize_on != other.sim_normalize_on:
            return False, f"Sim Normalize mismatch: {self.sim_normalize_on} vs {other.sim_normalize_on}"
        if self.played_quarter_minutes != other.played_quarter_minutes:
            return False, f"Played quarter length mismatch: {self.played_quarter_minutes} vs {other.played_quarter_minutes}"
        if self.sim_quarter_minutes != other.sim_quarter_minutes:
            return False, f"Sim quarter length mismatch: {self.sim_quarter_minutes} vs {other.sim_quarter_minutes}"
        if self.base_source_ref != other.base_source_ref:
            return False, f"Base source ref mismatch: {self.base_source_ref} vs {other.base_source_ref}"
        return True, "Comparable"


# -------------------------------------------------------------------------
# R07: EffectEvaluation (Fixes P1-07: Non-causal trend evaluation)
# -------------------------------------------------------------------------
@dataclass
class EffectEvaluation:
    trial_id: str
    preregistered_metric_ref: str
    outcome: EvaluationOutcome
    side_effects: List[str]
    confidence: float  # 0.0 .. 1.0
    competing_explanations: List[str]
    sample_size: int = 0
    confounders_controlled: bool = False

    def validate(self) -> None:
        if not self.trial_id or not self.preregistered_metric_ref:
            raise ValueError("R07: trial_id and preregistered_metric_ref are required")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("R07: confidence must be between 0.0 and 1.0")
        # P1-07: Causal confirmation cannot be claimed without controlled experiment
        if self.outcome in [EvaluationOutcome.CONFIRMED_CONTROLLED, EvaluationOutcome.REFUTED_CONTROLLED]:
            if not self.confounders_controlled or self.sample_size < 20:
                raise ValueError("R07 P1-07 VIOLATION: Cannot claim CONFIRMED_CONTROLLED without controlled confounders and sample_size >= 20")


# -------------------------------------------------------------------------
# R08: KnowledgeRevision (Fixes F03: Initial status; Fixes F04: Idempotency Key)
# -------------------------------------------------------------------------
@dataclass
class KnowledgeRevision:
    revision_id: str
    idempotency_key: str
    trial_id: str
    prior_claim_ref: str
    new_claim: str
    counterexamples: List[str]
    source_refs: List[str]
    revision_time: Optional[str] = None
    append_receipt: Optional[Dict[str, Any]] = None
    # Fixes F03: initial_status MUST be PENDING_REVISION, NOT APPENDED!
    status: RevisionStatus = RevisionStatus.PENDING_REVISION

    @classmethod
    def create_pending(
        cls,
        trial_id: str,
        prior_claim_ref: str,
        new_claim: str,
        counterexamples: List[str],
        source_refs: List[str],
    ) -> "KnowledgeRevision":
        # Fixes F04: Generate deterministic idempotency_key
        payload = f"{trial_id}|{prior_claim_ref}|{new_claim}".encode("utf-8")
        idempotency_key = hashlib.sha256(payload).hexdigest()
        revision_id = f"rev-{uuid.uuid4().hex[:12]}"
        return cls(
            revision_id=revision_id,
            idempotency_key=idempotency_key,
            trial_id=trial_id,
            prior_claim_ref=prior_claim_ref,
            new_claim=new_claim,
            counterexamples=counterexamples,
            source_refs=source_refs,
            status=RevisionStatus.PENDING_REVISION,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeRevision":
        return cls(
            revision_id=data["revision_id"],
            idempotency_key=data["idempotency_key"],
            trial_id=data["trial_id"],
            prior_claim_ref=data["prior_claim_ref"],
            new_claim=data["new_claim"],
            counterexamples=data.get("counterexamples", []),
            source_refs=data.get("source_refs", []),
            revision_time=data.get("revision_time"),
            append_receipt=data.get("append_receipt"),
            status=RevisionStatus(data.get("status", RevisionStatus.PENDING_REVISION)),
        )

    def validate(self) -> None:
        if not self.revision_id or not self.idempotency_key or not self.trial_id:
            raise ValueError("R08: revision_id, idempotency_key, and trial_id are required")
        if self.status == RevisionStatus.APPENDED:
            if not self.revision_time or not self.append_receipt:
                raise ValueError("R08: revision_time and append_receipt are required when status is APPENDED")


# -------------------------------------------------------------------------
# R09: DSeriesFeedback
# -------------------------------------------------------------------------
@dataclass
class DSeriesFeedback:
    trial_id: str
    evidence_tier: EvidenceTier
    d1_information: str
    d2_reader: str
    d3_capture: str
    d4_service: str
    d5_execution: str
    owner: str
    status: FeedbackStatus = FeedbackStatus.OPTIONAL

    def validate(self) -> None:
        if not self.trial_id or not self.owner:
            raise ValueError("R09: trial_id and owner are required")


# -------------------------------------------------------------------------
# V2 Pillar 2: Mechanism Interaction Edge
# -------------------------------------------------------------------------
@dataclass
class MechanismInteractionEdge:
    edge_id: str
    source_field: str
    target_behavior: str
    domain: str  # "TACTICS", "ROTATION", "TRAINING", "FINANCE", "TENDENCY"
    edge_type: str  # "DIRECT_CAUSE", "CORRELATION", "MODULATOR", "CONFLICT"
    evidence_tier: EvidenceTier
    hypothesis: str
    expected_primary_metric: str
    side_effects: List[str]
    confounders: List[str]
    method_version: str = "v1.0"
    verified_in_game: bool = False


# -------------------------------------------------------------------------
# V2 Pillar 3: Role Data Query & Response
# -------------------------------------------------------------------------
@dataclass
class RoleDataQuery:
    query_id: str
    requester_role: RoleType
    target_category: str
    save_id: str
    season: str
    object_id: Optional[str] = None
    requested_fields: List[str] = field(default_factory=list)


@dataclass
class RoleDataView:
    query_id: str
    role: RoleType
    category: str
    save_id: str
    season: str
    timestamp: str
    freshness: str
    data: Dict[str, Any]
    source_grade: EvidenceTier
    access_granted: bool = True
    rejection_reason: Optional[str] = None
