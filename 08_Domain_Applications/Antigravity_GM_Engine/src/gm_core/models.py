"""Serializable contracts shared with the web GM and future versions."""
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Availability(str, Enum):
    OBSERVED = "OBSERVED"
    CALCULATED = "CALCULATED"
    CONFIGURED = "CONFIGURED"
    REFERENCE = "REFERENCE"
    UNKNOWN = "UNKNOWN"


class Readiness(str, Enum):
    READY = "READY"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"


LIFECYCLES = ("CHAMPIONSHIP", "CONTENDING", "RISING", "COMPETITIVE",
              "RETOOLING", "REBUILDING", "UNDETERMINED")
MODULES = ("strategy", "roster", "staff", "offense", "defense", "trades",
           "contracts", "draft_free_agency", "development", "business", "culture", "worldline")


class NegotiationStage(str, Enum):
    DRAFT = "DRAFT"
    OFFERED = "OFFERED"
    COUNTERED = "COUNTERED"
    REJECTED = "REJECTED"
    NEEDS_DATA = "NEEDS_DATA"
    AGREED_IN_PRINCIPLE = "AGREED_IN_PRINCIPLE"
    PROPOSED_FOR_PLAYER_APPROVAL = "PROPOSED_FOR_PLAYER_APPROVAL"
    EXECUTED_VERIFIED = "EXECUTED_VERIFIED"


@dataclass
class Asset:
    kind: str
    asset_id: str
    observed_owner: str | None = None
    player_identity: dict | None = None
    contract: dict | None = None
    draft_pick: dict | None = None
    cash: int | None = None
    availability: str = "UNKNOWN"


@dataclass
class ModelHandoff:
    gm_run_id: str
    model_role: str
    team_scope: list
    source_batch_id: str
    policy_id: str
    submitted_proposals: list = field(default_factory=list)
    trade_offers: list = field(default_factory=list)
    disagreements: list = field(default_factory=list)
    review_verdict: str = "NEEDS_REVIEW"
    implementation: str = "PROTOCOL_ONLY_NO_MODEL_DISPATCH"


@dataclass
class HistoryRecord:
    career_id: str
    branch_id: str
    game_date: str
    category: str
    evidence: list
    value: dict
    status: str = "PROPOSED"
    implementation: str = "RESERVED_V3_NO_CONFIRMED_HISTORY_WRITE"


@dataclass
class Source:
    career_id: str
    batch_id: str
    data_updated_at: str
    uploaded_at: str
    game_date: str
    source_commit: str | None
    batch_path: str


@dataclass
class ModuleResult:
    module: str
    readiness: str
    evaluation: str
    facts: dict = field(default_factory=dict)
    analysis: list = field(default_factory=list)
    missing_data: list = field(default_factory=list)
    strategic_suggestions: list = field(default_factory=list)
    priority: str = "REVIEW"
    executable_operation_ready: bool = False
    status: str = "ANALYSIS_ONLY"

    def to_dict(self):
        return asdict(self)


@dataclass
class PublishedData:
    source: Source
    policy: dict
    gm_policy: dict
    rules_commit: str | None
    league: dict
    teams: dict
    coverage: dict
    calculations: dict
    staff: dict
    root: Any = field(repr=False)
    batch_directory: Any = field(repr=False)
    coaching: dict = field(default_factory=dict)


def module_result(name, facts, analysis, missing=(), suggestions=(), priority="REVIEW"):
    def present(value):
        if isinstance(value, dict) and "availability" in value:
            return value["availability"] != "UNKNOWN" and ("value" not in value or value["value"] is not None)
        if isinstance(value, list):
            return any(present(item) for item in value)
        return value is not None
    known = any(present(value) for value in facts.values())
    readiness = "BLOCKED" if not known else ("PARTIAL" if missing else "READY")
    return ModuleResult(name, readiness, "EVALUABLE" if known else "NOT_EVALUABLE",
                        facts, list(analysis), list(missing), list(suggestions), priority).to_dict()
