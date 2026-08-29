#!/usr/bin/env python3
"""Every decision-bearing constant, with the authority that permits it.

C-09 (complete_decision_provenance).  The independent review's AB-02 finding was
that predicate-level `P07 -> A11` labels are not traceability: the extractor's
vocabularies, thresholds, polarity rules and defaults also constrain the accepted
A surface, and none of them carried a trace.  `CATALOG_RESTATEMENT_THRESHOLD = 3`
was the proof — it weakened A11 by letting a two-entry second catalog through, and
no requirement anywhere authorised the number 3.

The rule this module enforces is mechanical, not editorial:

    a constant may decide acceptance only if it is declared here, with an
    `authority` field naming an A requirement or an explicit Human decision.

`DecisionRule.authority == HUMAN_REQUIRED` marks a rule that no A text supports.
Such a rule is *not applied*; it is reported.  Inventing the missing requirement
is what produced ST04-V3-IR-004 (run_id promoted from B), so this module refuses
to do it.

Nothing here is a vendor list.  No provider, model, product or family name
appears in this file, and `test_provenance.py` asserts that mechanically.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Any

HUMAN_REQUIRED = "HUMAN_REQUIREMENT_DECISION_REQUIRED"

B_ONLY = "B_ONLY"


def _plain(value: Any) -> Any:
    """Plain YAML-representable form, recursively.

    A rule's value may be a frozenset, a tuple, or a mapping of names to
    frozensets. The ledger has to be readable by a reviewer months from now, so
    it is emitted as sorted plain data rather than as a Python repr.
    """
    if isinstance(value, (set, frozenset)):
        return sorted(_plain(v) for v in value)
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    return value


@dataclass(frozen=True)
class DecisionRule:
    """One decision-bearing rule and the authority that permits it."""

    rule_id: str
    kind: str  # vocabulary | polarity | threshold | default | ambiguity | mapping
    authority: str  # an A id, an explicit Human decision, or HUMAN_REQUIRED
    interpretation: str
    accepted_alternatives: tuple[str, ...] = ()
    rejected_alternatives: tuple[str, ...] = ()
    value: Any = None

    @property
    def traced(self) -> bool:
        return self.authority != HUMAN_REQUIRED

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "kind": self.kind,
            "authority": self.authority,
            "interpretation": self.interpretation,
            "accepted_alternatives": list(self.accepted_alternatives),
            "rejected_alternatives": list(self.rejected_alternatives),
            "value": _plain(self.value),
        }


REGISTRY: dict[str, DecisionRule] = {}


def rule(
    rule_id: str,
    *,
    kind: str,
    authority: str,
    interpretation: str,
    value: Any = None,
    accepted_alternatives: tuple[str, ...] = (),
    rejected_alternatives: tuple[str, ...] = (),
) -> Any:
    """Declare a decision-bearing constant and return its value.

    The return is the value itself, so a module-level constant cannot exist
    without passing through here.
    """
    if rule_id in REGISTRY:
        raise ValueError(f"duplicate decision rule id: {rule_id}")
    REGISTRY[rule_id] = DecisionRule(
        rule_id=rule_id,
        kind=kind,
        authority=authority,
        interpretation=interpretation,
        accepted_alternatives=accepted_alternatives,
        rejected_alternatives=rejected_alternatives,
        value=value,
    )
    return value


def untraced_rules() -> list[DecisionRule]:
    return [r for r in REGISTRY.values() if not r.traced]


def as_ledger() -> dict[str, Any]:
    return {
        "schema_version": "citystate.stage04.decision_provenance.v1",
        "rule_count": len(REGISTRY),
        "untraced_rule_count": len(untraced_rules()),
        "rules": [REGISTRY[k].as_dict() for k in sorted(REGISTRY)],
    }
