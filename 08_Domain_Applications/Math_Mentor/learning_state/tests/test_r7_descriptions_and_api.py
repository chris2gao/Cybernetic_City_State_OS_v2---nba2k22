"""Round-7: canonical descriptions must match behaviour, and so must annotations.

Three claims had drifted away from the code they described:

  * `learning_state_epoch` said mismatches are "ignored"; they are rejected
    fail-closed, and snapshot derivation then refuses to publish at all;
  * `prev_event_digest` said the hash chain "replaces Git immutability"; it does
    not, and `append_event`'s own module docstring already said so honestly;
  * `write_snapshot` was annotated `-> Path` while returning a 2-tuple.

A wrong description is not cosmetic here: the first-lesson audit showed a stale
status claim forcing a downstream reader to adjudicate which statement to trust.

All stores are synthetic temporaries. No real learner store is touched.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
import typing

import pytest
import yaml
from conftest import reach_classroom_passed

import append_event as writer
from append_event import append_event, write_snapshot

PACKAGE = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PACKAGE / "learning_event.schema.json"


def _schema() -> dict:
    with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# --- corrected descriptions ------------------------------------------------


def test_epoch_description_says_rejected_not_ignored():
    description = _schema()["properties"]["learning_state_epoch"]["description"]
    assert "REJECTED" in description or "rejected" in description
    assert "ignored by the reducer" not in description


def test_prev_event_digest_does_not_claim_to_replace_git():
    description = _schema()["properties"]["prev_event_digest"]["description"]
    assert "replaces Git immutability" not in description
    assert "does NOT replace Git immutability" in description


def test_epoch_mismatch_is_actually_rejected():
    """The behaviour the description now claims."""
    from reduce_readonly import reduce_events

    events = reach_classroom_passed()
    events[0]["learning_state_epoch"] = "some-other-epoch"
    result = reduce_events(events, "learning-state-epoch-v2")
    assert any("epoch mismatch" in reason for _, reason in result.rejected)


def test_snapshot_derivation_refuses_while_any_event_is_rejected(synthetic_store):
    """Fail-closed, which is why 'ignored' was the wrong word."""
    from append_event import WriteRefused, derive_snapshot

    append_event(synthetic_store, reach_classroom_passed()[0])
    bad = reach_classroom_passed()[1]
    bad["learning_state_epoch"] = "some-other-epoch"
    with pytest.raises(WriteRefused):
        append_event(synthetic_store, bad)
    # The refused event never landed, so the store still derives cleanly.
    assert derive_snapshot(synthetic_store)["event_count"] == 1


# --- corrected API signature -----------------------------------------------


def test_write_snapshot_annotation_matches_its_return_value():
    hints = typing.get_type_hints(write_snapshot)
    annotation = hints["return"]
    assert typing.get_origin(annotation) is tuple, f"expected a tuple, got {annotation}"
    args = typing.get_args(annotation)
    assert args[0] is Path
    assert args[1] is dict


def test_write_snapshot_actually_returns_path_and_snapshot(synthetic_store):
    for event in reach_classroom_passed():
        append_event(synthetic_store, event)
    returned = write_snapshot(synthetic_store)
    assert isinstance(returned, tuple) and len(returned) == 2
    path, snapshot = returned
    assert isinstance(path, Path) and path.exists()
    assert isinstance(snapshot, dict)
    # The published file must equal the returned snapshot, which is the whole
    # reason the snapshot is returned rather than re-derived by the caller.
    with path.open("r", encoding="utf-8") as handle:
        assert yaml.safe_load(handle) == snapshot


def test_write_snapshot_docstring_states_both_return_values():
    doc = inspect.getdoc(write_snapshot) or ""
    assert "path" in doc.lower()
    assert "snapshot" in doc.lower()
