"""Trust-first, voluntary Agent disclosures about task-prototype deviations.

These are Agent statements, not authenticated Host gateway observations.
A disclosure is NOT a denied operation, does not grant permission, and must
never enter the denominator/numerator of Host-denial metrics. No monitor.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Callable, Iterable
from uuid import uuid4


KINDS = frozenset({
    "UNNECESSARY_CHECK", "EXTRA_STEP_PROPOSED", "EXECUTION_DEVIATION",
    "UNEXPECTED_RESULT", "PROTOTYPE_MISMATCH", "OTHER",
})
HANDLINGS = frozenset({
    "STOPPED_AND_REPORTED", "CORRECTED_WITHIN_SCOPE",
    "REQUESTED_HUMAN_DECISION", "DISCLOSED_AFTER_ACTION",
})


@dataclass(frozen=True)
class AgentSelfReport:
    event_id: str
    timestamp_utc: str
    source: str                    # AGENT_SELF_REPORT, never HOST_OBSERVED
    model_ref: str
    task_id: str
    session_ref: str
    prototype_ref: str
    kind: str
    handling: str
    description: str               # Concise, non-sensitive Agent statement
    consequence: str               # Actual or possible effect on business Done
    evidence_ref: str              # Optional link to existing Run/PRMS evidence

    @classmethod
    def create(
        cls, *, model_ref: str, task_id: str, session_ref: str,
        prototype_ref: str, kind: str, handling: str, description: str,
        consequence: str, evidence_ref: str = "",
    ) -> "AgentSelfReport":
        if kind not in KINDS or handling not in HANDLINGS:
            raise ValueError("Unknown Agent disclosure kind or handling")
        if not all(isinstance(s, str) and s.strip() for s in
                   (model_ref, task_id, session_ref, prototype_ref,
                    description, consequence)):
            raise ValueError("Agent disclosure requires task, source and concrete explanation")
        return cls(
            event_id=str(uuid4()),
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            source="AGENT_SELF_REPORT",
            model_ref=model_ref, task_id=task_id, session_ref=session_ref,
            prototype_ref=prototype_ref, kind=kind, handling=handling,
            description=description, consequence=consequence,
            evidence_ref=evidence_ref,
        )

    def as_record(self) -> dict:
        return asdict(self)


def append_self_report_jsonl_sink(path: str | Path) -> Callable[[AgentSelfReport], None]:
    """Optional local persistence into an EXISTING Run directory, no new service.

    If no writable sink is available, an Agent can report in the active
    conversation / existing PRMS checkpoint. A missing log file is not a
    reason to block unrelated authorized business work.
    """
    target = Path(path)

    def append(report: AgentSelfReport) -> None:
        if not isinstance(report, AgentSelfReport) or report.source != "AGENT_SELF_REPORT":
            raise TypeError("Only AgentSelfReport can be written to this stream")
        line = (json.dumps(report.as_record(), ensure_ascii=False,
                           sort_keys=True, separators=(",", ":")) + "\n")
        with target.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(line)

    return append


def load_self_reports(path: str | Path) -> tuple[AgentSelfReport, ...]:
    """Read-only; never interpret user/model-supplied text as Host proof."""
    required = set(AgentSelfReport.__dataclass_fields__)
    results = []
    with Path(path).open(encoding="utf-8") as stream:
        for lineno, line in enumerate(stream, 1):
            obj = json.loads(line)
            if not isinstance(obj, dict) or set(obj) != required:
                raise ValueError(f"Invalid self-report at line {lineno}")
            report = AgentSelfReport(**obj)
            if report.source != "AGENT_SELF_REPORT" or report.kind not in KINDS or report.handling not in HANDLINGS:
                raise ValueError(f"Invalid self-report provenance or enum at line {lineno}")
            results.append(report)
    return tuple(results)


def summarize_self_reports(
    reports: Iterable[AgentSelfReport], *,
    model_ref: str | None = None, task_id: str | None = None,
) -> dict:
    """Descriptive counts, not a model compliance score or observed denial rate."""
    selected: list[AgentSelfReport] = []
    seen: set[str] = set()
    for report in reports:
        if report.source != "AGENT_SELF_REPORT":
            raise ValueError("Host observations must not be mixed with Agent self-reports")
        if (model_ref is not None and report.model_ref != model_ref) or (
                task_id is not None and report.task_id != task_id):
            continue
        if report.event_id in seen:
            continue
        seen.add(report.event_id)
        selected.append(report)
    kinds: dict[str, int] = {}
    handlings: dict[str, int] = {}
    for report in selected:
        kinds[report.kind] = kinds.get(report.kind, 0) + 1
        handlings[report.handling] = handlings.get(report.handling, 0) + 1
    return {
        "source": "AGENT_SELF_REPORT",
        "disclosures": len(selected),
        "by_kind": kinds,
        "by_handling": handlings,
        "interpretation": (
            "Trust-first voluntary disclosures. They can inform prototype "
            "improvements; they are not Host-confirmed denials or evidence of model disobedience."
        ),
    }
