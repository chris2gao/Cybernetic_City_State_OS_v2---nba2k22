"""Full-denominator progress and role-neutral mechanism knowledge queries."""
from collections import Counter, defaultdict
from dataclasses import dataclass

STAGES = ("INVENTORIED", "NATIVE_LOCATED", "WRITE_READBACK_QUALIFIED", "SCHEDULED",
          "LIVE_EXPOSED", "BROAD_SCREENED", "CONFIRMING", "REPLICATED_OR_LIMITED")
_REQUIRED = {
    "NATIVE_LOCATED": {"build_sha256", "location"},
    "WRITE_READBACK_QUALIFIED": {"build_sha256", "identity", "legal_domain", "readback_ref"},
    "SCHEDULED": {"worldline_id", "plan_digest", "opportunities"},
    "LIVE_EXPOSED": {"worldline_id", "identity", "field_value", "readback_ref", "exposure_ref"},
    "BROAD_SCREENED": {"worldline_id", "effect", "analysis_ref", "limitations"},
    "CONFIRMING": {"protocol_id", "plan_digest", "independent_worldlines"},
    "REPLICATED_OR_LIMITED": {"reliability", "reason", "analysis_ref", "contradictions"},
}


@dataclass(frozen=True)
class ProgressEvent:
    factor_id: str
    stage: str
    mode: str
    source_sha256: str
    evidence: dict


class ProgressLedger:
    def __init__(self, study, events=()):
        self.study = study
        self._history = defaultdict(list)
        for event in events:
            self.record(event)

    def record(self, event):
        if event.factor_id not in self.study.factors or event.stage not in STAGES[1:]:
            raise ValueError("UNKNOWN_FACTOR_OR_STAGE")
        if (event.mode not in ("FIXTURE", "LIVE") or len(event.source_sha256) != 64
                or any(char not in "0123456789abcdef" for char in event.source_sha256)
                or not _REQUIRED[event.stage] <= event.evidence.keys()):
            raise ValueError("PROGRESS_EVIDENCE_INCOMPLETE")
        history = self._history[event.factor_id, event.mode]
        previous = history[-1].stage if history else "INVENTORIED"
        limited = (event.stage == "REPLICATED_OR_LIMITED" and event.evidence["reliability"] in
                   ("NO_OPPORTUNITY", "NO_MEASURABLE_ENDPOINT", "UNIDENTIFIABLE_IN_MODE")
                   and bool(event.evidence.get("technical_scope")) and bool(event.evidence["reason"]))
        if previous == STAGES[-1] or (not limited and STAGES.index(event.stage) != STAGES.index(previous) + 1):
            raise ValueError("PROGRESS_CANNOT_SKIP_EVIDENCE_STAGE")
        if (event.stage == "REPLICATED_OR_LIMITED" and event.evidence["reliability"] == "EFFECT_REPLICATED"
                and len(set(event.evidence.get("independent_worldlines", ()))) < 2):
            raise ValueError("REPLICATION_REQUIRES_INDEPENDENT_WORLDLINES")
        history.append(event)

    def coverage(self, mode="LIVE"):
        rows = {}
        for key, factor in self.study.factors.items():
            history = self._history[key, mode]
            rows[key] = {"stage": history[-1].stage if history else "INVENTORIED",
                         "mode": mode, "protocol": factor.protocol, "reference_slots": factor.reference_slots,
                         "qualification": factor.adapter_state,
                         "limit": history[-1].evidence.get("reason") if history and history[-1].stage == STAGES[-1] else None}
        return {"counts": dict(Counter(row["stage"] for row in rows.values())), "factors": rows}

    def next_queue(self):
        return [key for key, row in self.coverage()["factors"].items() if row["stage"] != "REPLICATED_OR_LIMITED"]

    def query(self, factor_id, role, *, mode="LIVE"):
        if role not in ("GM", "COACH", "PLAYER"):
            raise ValueError("UNKNOWN_KNOWLEDGE_CONSUMER")
        factor = self.study.factors[factor_id]
        if mode not in ("LIVE", "FIXTURE"):
            raise ValueError("UNKNOWN_EVIDENCE_MODE")
        history = self._history[factor_id, mode]
        report = next((event for event in reversed(history) if event.stage in ("BROAD_SCREENED", "REPLICATED_OR_LIMITED")), None)
        evidence = report.evidence if report else {}
        return {"factor_id": factor_id, "role": role, "action": factor.native.get("name"),
                "context": factor.protocol, "source": report.source_sha256 if report else None,
                "expected_effect_range": evidence.get("interval"),
                "reliability": evidence.get("reliability", "UNCONFIRMED"),
                "tradeoff": evidence.get("tradeoff"), "contraindications": evidence.get("limitations"),
                "contradictions": evidence.get("contradictions", []), "evidence_mode": mode,
                "decision_usable": mode == "LIVE" and evidence.get("reliability") == "EFFECT_REPLICATED",
                "execution_authorized": False}
