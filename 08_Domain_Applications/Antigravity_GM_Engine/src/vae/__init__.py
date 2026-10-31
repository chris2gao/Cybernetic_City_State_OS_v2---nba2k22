"""
VAE (Vanilla AI Enhancement) Engine Package.
"""

from .contracts import (
    EvidenceTier,
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

__all__ = [
    "EvidenceTier",
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
]
