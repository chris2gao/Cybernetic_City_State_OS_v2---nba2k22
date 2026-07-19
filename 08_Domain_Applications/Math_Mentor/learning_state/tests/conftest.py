"""Shared fixtures.

Every test in this package works on a synthetic temporary store.  No test may
read, write, hash or otherwise touch a real learner store.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import itertools
from pathlib import Path
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

EPOCH = "learning-state-epoch-v2"
SCHEMA_VERSION = "citystate.math_mentor.learning_event.v2"
NODE = "n_fixture_001"
NEAR_TERM = "near_term_retention"
STABILITY = "stability_review"

# Qualifying passes must have strictly increasing RFC 3339 timestamps, so the
# fixture hands out advancing ones by default.  Computed with timedelta rather
# than by formatting a counter into the day field, which produced dates like
# 2026-01-32 once the suite grew past 31 events.
_EPOCH_START = datetime(2026, 1, 1, tzinfo=timezone.utc)
_CLOCK = itertools.count()


def _next_timestamp() -> str:
    return (_EPOCH_START + timedelta(hours=next(_CLOCK))).isoformat()


def make_event(
    event_id: str,
    source: str,
    target: str,
    *,
    event_type: str = "classroom_result",
    source_type: str | None = None,
    source_ref: str | None = None,
    timestamp: str | None = None,
    **overrides: object,
) -> dict:
    """Build a structurally complete v2 event; overrides break it on purpose.

    `source_type` defaults to whatever the target transition legitimately needs.
    Passing it explicitly overrides that default and is NOT silently corrected,
    so a test can express "classroom evidence offered as a review pass".
    """
    resolved_source_type = source_type or (
        "spaced_review" if target == "review_passed" else "exam_agent"
    )
    event: dict = {
        "schema_version": SCHEMA_VERSION,
        "event_id": event_id,
        "event_type": event_type,
        "student_ref": "fixture_alias_a",
        "node_ref": {"node_id": NODE},
        "transition": {"from": source, "to": target},
        "evidence_provenance": {
            "source_type": resolved_source_type,
            "source_ref": source_ref or f"fixture://{event_id}",
            "evidence_timestamp": timestamp or _next_timestamp(),
            "evidence_limitations": "synthetic fixture",
        },
        "learning_state_epoch": EPOCH,
    }
    if target == "classroom_passed":
        event["classroom_evidence"] = {
            "exam_agent_result": "classroom_passed",
            "covered_subtopics": ["s1", "s2"],
            "definition_restatement": "student restated the criterion",
            "trap_evidence": "rejected the one-sided operation",
            "tool_and_evidence_limitations": "synthetic",
        }
    if target == "review_due":
        event["evidence_provenance"]["source_type"] = source_type or "scheduler_placeholder"
        event.setdefault("review_window_id", f"win-{event_id}")
        event.setdefault("review_window_kind", NEAR_TERM)
    if target == "review_passed":
        event["review_evidence"] = {
            "review_window_id": f"win-{event_id}",
            "review_result": "passed",
            "definition_retention": "retained",
            "transfer_evidence": "solved a transfer item",
        }
    event.update(overrides)
    return event


def open_window(
    event_id: str, source: str, window: str, kind: str,
    timestamp: str | None = None, **overrides,
) -> dict:
    return make_event(
        event_id, source, "review_due",
        event_type="review_result",
        source_type="scheduler_placeholder",
        timestamp=timestamp,
        review_window_id=window,
        review_window_kind=kind,
        **overrides,
    )


def pass_window(
    event_id: str, window: str, source_type: str | None = None,
    timestamp: str | None = None, **overrides,
) -> dict:
    # `timestamp` is threaded into evidence_provenance rather than left in
    # **overrides, where it would become a bogus top-level field.
    event = make_event(
        event_id, "review_due", "review_passed",
        event_type="review_result", source_type=source_type, timestamp=timestamp,
    )
    event["review_evidence"]["review_window_id"] = window
    event.update(overrides)
    return event


def reach_classroom_passed(prefix: str = "c") -> list[dict]:
    return [
        make_event(f"{prefix}1", "not_seen", "introduced"),
        make_event(f"{prefix}2", "introduced", "classroom_passed"),
    ]


def reach_two_review_passes(prefix: str = "r") -> list[dict]:
    """Two passes in two distinct windows of BOTH required kinds.

    This is the only legal route to graduation eligibility: a near-term retention
    check and a later stability check, each opened and then matched by its pass.
    """
    return reach_classroom_passed(prefix) + [
        open_window(f"{prefix}3", "classroom_passed", "win-A", NEAR_TERM),
        pass_window(f"{prefix}4", "win-A"),
        open_window(f"{prefix}5", "review_passed", "win-B", STABILITY),
        pass_window(f"{prefix}6", "win-B"),
    ]


BOUND_STUDENT = "fixture_alias_a"


@pytest.fixture
def synthetic_store(tmp_path: Path) -> Path:
    """A fresh synthetic store.  Never a real learner store."""
    store = tmp_path / "synthetic_store"
    (store / "events").mkdir(parents=True)
    with (store / "store_meta.yml").open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(
            {
                "schema_version": "citystate.math_mentor.learning_store_meta.v1",
                "store_id": "synthetic-store-0001",
                "bound_student_ref": BOUND_STUDENT,
                "bound_epoch": EPOCH,
            },
            handle,
        )
    return store
