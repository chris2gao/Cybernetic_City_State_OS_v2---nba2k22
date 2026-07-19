"""Shared fixtures.

Every test in this package works on a synthetic temporary store.  No test may
read, write, hash or otherwise touch a real learner store.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

EPOCH = "learning-state-epoch-v2"
SCHEMA_VERSION = "citystate.math_mentor.learning_event.v2"
NODE = "n_fixture_001"


def make_event(
    event_id: str,
    source: str,
    target: str,
    *,
    event_type: str = "classroom_result",
    source_type: str | None = None,
    source_ref: str | None = None,
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
            "evidence_timestamp": "2026-01-01T00:00:00Z",
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
        event.setdefault("review_window_id", f"win-{event_id}")
    if target == "review_passed":
        event["review_evidence"] = {
            "review_window_id": f"win-{event_id}",
            "review_result": "passed",
            "definition_retention": "retained",
            "transfer_evidence": "solved a transfer item",
        }
    event.update(overrides)
    return event


def reach_classroom_passed(prefix: str = "c") -> list[dict]:
    return [
        make_event(f"{prefix}1", "not_seen", "introduced"),
        make_event(f"{prefix}2", "introduced", "classroom_passed"),
    ]


def reach_two_review_passes(prefix: str = "r") -> list[dict]:
    """Two passes earned in two DISTINCT windows, the legal graduation path."""
    return reach_classroom_passed(prefix) + [
        make_event(f"{prefix}3", "classroom_passed", "review_due", review_window_id="win-A"),
        make_event(f"{prefix}4", "review_due", "review_passed"),
        make_event(f"{prefix}5", "review_passed", "review_due", review_window_id="win-B"),
        make_event(f"{prefix}6", "review_due", "review_passed"),
    ]


@pytest.fixture
def synthetic_store(tmp_path: Path) -> Path:
    """A fresh synthetic store.  Never a real learner store."""
    store = tmp_path / "synthetic_store"
    (store / "events").mkdir(parents=True)
    with (store / "epoch.yml").open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump({"bound_epoch": EPOCH}, handle)
    return store
