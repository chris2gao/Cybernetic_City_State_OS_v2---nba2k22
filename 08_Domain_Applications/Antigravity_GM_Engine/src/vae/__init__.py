"""
VAE (Vanilla AI Enhancement) Package.
Exports all contracts, adapters, engines, and V2 three-pillar services.
"""

from .contracts import (
    EvidenceTier,
    RoleType,
    SnapshotStatus,
    DiagnosisStatus,
    PreflightStatus,
    ReceiptStatus,
    ReadbackStatus,
    ObservationStatus,
    EvaluationOutcome,
    RevisionStatus,
    FeedbackStatus,
    ProfileSnapshot,
    IssueDiagnosis,
    TrialPreflight,
    ExecutionReceipt,
    TechnicalReadback,
    CompetitiveObservation,
    EffectEvaluation,
    KnowledgeRevision,
    DSeriesFeedback,
    MechanismInteractionEdge,
    RoleDataQuery,
    RoleDataView,
)

from .reader_adapter import VAEReaderAdapter
from .diagnosis import VAEDiagnosisEngine
from .preflight import VAEPreflightEngine
from .simulator import VAEExecutionSimulator
from .readback_adapter import VAEReadbackAdapter
from .observation import VAEObservationComparator
from .evaluator import VAEEvaluationEngine
from .revision import VAEKnowledgeRevisionManager
from .pipeline import VAEE1Pipeline
from .e2_e4_extensions import VAEE2E4ScopeGuard
from .native_actions import VAENativeActionRegistry, ActionSpecification, ActionResult
from .mechanism_registry import VAEMechanismRegistry
from .role_data_service import VAERoleDataService

__all__ = [
    "EvidenceTier",
    "RoleType",
    "SnapshotStatus",
    "DiagnosisStatus",
    "PreflightStatus",
    "ReceiptStatus",
    "ReadbackStatus",
    "ObservationStatus",
    "EvaluationOutcome",
    "RevisionStatus",
    "FeedbackStatus",
    "ProfileSnapshot",
    "IssueDiagnosis",
    "TrialPreflight",
    "ExecutionReceipt",
    "TechnicalReadback",
    "CompetitiveObservation",
    "EffectEvaluation",
    "KnowledgeRevision",
    "DSeriesFeedback",
    "MechanismInteractionEdge",
    "RoleDataQuery",
    "RoleDataView",
    "VAEReaderAdapter",
    "VAEDiagnosisEngine",
    "VAEPreflightEngine",
    "VAEExecutionSimulator",
    "VAEReadbackAdapter",
    "VAEObservationComparator",
    "VAEEvaluationEngine",
    "VAEKnowledgeRevisionManager",
    "VAEE1Pipeline",
    "VAEE2E4ScopeGuard",
    "VAENativeActionRegistry",
    "ActionSpecification",
    "ActionResult",
    "VAEMechanismRegistry",
    "VAERoleDataService",
]
