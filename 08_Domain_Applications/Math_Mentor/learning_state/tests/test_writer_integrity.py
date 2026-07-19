"""Writer integrity tests (locking, ordering, tail anchor, recovery).

Every defect listed in the 2026-07-19 independent review has a test here.
All stores are synthetic temporaries; no real learner store is touched.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml
from conftest import EPOCH, NODE, make_event, reach_classroom_passed

from append_event import (
    AnchorUpdateFailed,
    StoreLocked,
    WriteRefused,
    append_event,
    derive_snapshot,
    load_store,
    read_anchor,
    repair_anchor,
    single_writer_lock,
    write_snapshot,
)
from validate_events import event_digest


def _seed(store: Path, count: int = 2) -> None:
    for event in reach_classroom_passed()[:count]:
        append_event(store, event)


# --- defect R4.7: concurrency ----------------------------------------------


def test_lock_held_by_another_process_blocks_entry(synthetic_store):
    """Simulate a foreign holder; same-stack re-entry is intentionally allowed."""
    synthetic_store.mkdir(parents=True, exist_ok=True)
    foreign = synthetic_store / ".writer.lock"
    foreign.write_text("pid=999999\n", encoding="utf-8")
    try:
        with pytest.raises(StoreLocked):
            with single_writer_lock(synthetic_store, timeout=0.2):
                pass
    finally:
        foreign.unlink()


def test_lock_is_strictly_non_reentrant(synthetic_store):
    """Re-entry was removed: a path-keyed depth counter defeated thread safety."""
    with single_writer_lock(synthetic_store):
        with pytest.raises(StoreLocked):
            with single_writer_lock(synthetic_store, timeout=0.2):
                pass
    assert not (synthetic_store / ".writer.lock").exists()


def test_lock_is_released_after_use(synthetic_store):
    with single_writer_lock(synthetic_store):
        pass
    with single_writer_lock(synthetic_store, timeout=0.2):
        pass  # must not raise
    assert not (synthetic_store / ".writer.lock").exists()


def test_existing_event_file_is_never_overwritten(synthetic_store):
    _seed(synthetic_store, 1)
    # Simulate a concurrent writer having already created the next file.
    (synthetic_store / "events" / "002.yml").write_text("placeholder", encoding="utf-8")
    with pytest.raises(WriteRefused, match="refusing to overwrite|tail anchor|validation|does not contain a mapping"):
        append_event(synthetic_store, reach_classroom_passed()[1])


def test_temporary_files_are_process_unique(synthetic_store):
    _seed(synthetic_store, 1)
    leftovers = list((synthetic_store / "events").glob(".*tmp"))
    assert leftovers == [], f"temporary files leaked: {leftovers}"


# --- defect R4.9: numeric ordering -----------------------------------------


def test_sequence_ordering_is_numeric_not_lexical():
    """Lexical sort puts 1000.yml before 999.yml; the loader must not.

    Exercised directly on the ordering helper, because the store itself now
    requires a contiguous sequence starting at 1 and so cannot host a sparse
    999/1000 fixture.
    """
    from append_event import EVENT_NAME

    names = ["001.yml", "002.yml", "999.yml", "1000.yml", "1001.yml"]
    assert sorted(names)[0] == "001.yml"
    assert sorted(names).index("1000.yml") < sorted(names).index("999.yml"), (
        "precondition: lexical order really is wrong here"
    )
    numeric = sorted(names, key=lambda n: int(EVENT_NAME.match(n).group(1)))
    assert numeric == ["001.yml", "002.yml", "999.yml", "1000.yml", "1001.yml"]


def test_sequence_gaps_are_rejected(synthetic_store):
    _seed(synthetic_store, 2)
    # Remove the first event, leaving a gap; the anchor still matches the tail.
    (synthetic_store / "events" / "001.yml").unlink()
    with pytest.raises(WriteRefused, match="gaps or does not start at 1"):
        load_store(synthetic_store)


def test_unexpected_yml_in_events_directory_is_rejected(synthetic_store):
    _seed(synthetic_store, 1)
    (synthetic_store / "events" / "notes.yml").write_text("a: 1\n", encoding="utf-8")
    with pytest.raises(WriteRefused, match="unexpected files"):
        load_store(synthetic_store)


def test_non_mapping_event_file_fails_cleanly(synthetic_store):
    _seed(synthetic_store, 1)
    (synthetic_store / "events" / "001.yml").write_text("- just\n- a list\n", encoding="utf-8")
    with pytest.raises(WriteRefused, match="does not contain a mapping"):
        load_store(synthetic_store)


def test_malformed_yaml_event_file_fails_cleanly(synthetic_store):
    _seed(synthetic_store, 1)
    (synthetic_store / "events" / "001.yml").write_text("a: [unclosed\n", encoding="utf-8")
    with pytest.raises(WriteRefused, match="not valid YAML"):
        load_store(synthetic_store)


# --- defect R4.8: tail integrity -------------------------------------------


def test_tail_anchor_detects_deletion_of_the_newest_event(synthetic_store):
    _seed(synthetic_store, 2)
    (synthetic_store / "events" / "002.yml").unlink()
    with pytest.raises(WriteRefused, match="tail anchor mismatch"):
        load_store(synthetic_store)


def test_tail_anchor_detects_modification_of_the_newest_event(synthetic_store):
    _seed(synthetic_store, 2)
    path = synthetic_store / "events" / "002.yml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    document["node_ref"]["node_id"] = "n_tampered"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(document, handle, allow_unicode=True, sort_keys=True)
    with pytest.raises(WriteRefused, match="tail anchor mismatch"):
        load_store(synthetic_store)


def test_chain_still_detects_middle_tampering(synthetic_store):
    _seed(synthetic_store, 2)
    path = synthetic_store / "events" / "001.yml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    document["node_ref"]["node_id"] = "n_tampered"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(document, handle, allow_unicode=True, sort_keys=True)
    with pytest.raises(WriteRefused, match="integrity chain broken|tail anchor"):
        derive_snapshot(synthetic_store)


def test_anchor_records_count_and_head_digest(synthetic_store):
    _seed(synthetic_store, 2)
    anchor = read_anchor(synthetic_store)
    _, events = load_store(synthetic_store, verify_anchor=False)
    assert anchor["event_count"] == 2
    assert anchor["head_digest"] == event_digest(events[-1])


# --- refusal leaves no trace ----------------------------------------------


def test_refused_write_leaves_the_store_untouched(synthetic_store):
    _seed(synthetic_store, 2)
    before_count = derive_snapshot(synthetic_store)["event_count"]
    illegal = make_event(
        "bad", "classroom_passed", "graduated",
        event_type="human_acceptance",
        source_type="explicit_human_override",
        human_authorization_ref="pretend",
    )
    with pytest.raises(WriteRefused):
        append_event(synthetic_store, illegal)
    after = derive_snapshot(synthetic_store)
    assert after["event_count"] == before_count
    assert after["nodes"][NODE]["status"] == "classroom_passed"
    assert not (synthetic_store / ".writer.lock").exists()


def test_epoch_mismatch_is_refused_at_the_writer(synthetic_store):
    event = make_event("x", "not_seen", "introduced", learning_state_epoch="learning-state-epoch-v1")
    with pytest.raises(WriteRefused, match="epoch"):
        append_event(synthetic_store, event)
    assert list((synthetic_store / "events").glob("*.yml")) == []


# --- snapshots are derived, not authoritative ------------------------------


def test_snapshot_is_rebuildable_after_deletion(synthetic_store):
    _seed(synthetic_store, 2)
    path = write_snapshot(synthetic_store)
    os.remove(path)
    rebuilt = write_snapshot(synthetic_store)
    document = yaml.safe_load(rebuilt.read_text(encoding="utf-8"))
    assert document["snapshot_is_derived"] is True
    assert document["nodes"][NODE]["status"] == "classroom_passed"


def test_snapshot_marks_itself_as_derived(synthetic_store):
    _seed(synthetic_store, 2)
    snapshot = derive_snapshot(synthetic_store)
    assert snapshot["snapshot_is_derived"] is True
    assert snapshot["rebuildable_from_events"] is True


# --- rereview round 2: anchor fail-closed and crash recovery ---------------


def test_missing_anchor_with_events_fails_closed(synthetic_store):
    """Deleting the anchor must not be a way to hide a truncation."""
    _seed(synthetic_store, 2)
    (synthetic_store / "integrity" / "head.json").unlink()
    with pytest.raises(WriteRefused, match="tail anchor is missing"):
        load_store(synthetic_store)


def test_empty_store_without_anchor_is_allowed(synthetic_store):
    epoch, events = load_store(synthetic_store)
    assert events == []
    assert epoch


def test_repair_anchor_recovers_a_committed_event(synthetic_store):
    _seed(synthetic_store, 2)
    (synthetic_store / "integrity" / "head.json").unlink()
    with pytest.raises(WriteRefused):
        load_store(synthetic_store)
    repair_anchor(synthetic_store)
    _, events = load_store(synthetic_store)
    assert len(events) == 2


def test_repair_anchor_refuses_to_paper_over_a_broken_chain(synthetic_store):
    _seed(synthetic_store, 2)
    path = synthetic_store / "events" / "001.yml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    document["node_ref"]["node_id"] = "n_tampered"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(document, handle, allow_unicode=True, sort_keys=True)
    (synthetic_store / "integrity" / "head.json").unlink()
    with pytest.raises(WriteRefused, match="invalid store"):
        repair_anchor(synthetic_store)


def test_anchor_write_failure_reports_event_as_committed(synthetic_store, monkeypatch):
    """The caller must NOT be told the store is unchanged when it is not."""
    _seed(synthetic_store, 1)

    import append_event as writer

    def boom(*args, **kwargs):
        raise OSError("simulated anchor write failure")

    monkeypatch.setattr(writer, "write_anchor", boom)
    with pytest.raises(AnchorUpdateFailed, match="IS COMMITTED"):
        writer.append_event(synthetic_store, reach_classroom_passed()[1])

    monkeypatch.undo()
    # The event really is on disk; the anchor is stale, so reads fail closed.
    with pytest.raises(WriteRefused, match="tail anchor mismatch"):
        load_store(synthetic_store)
    repair_anchor(synthetic_store)
    assert derive_snapshot(synthetic_store)["event_count"] == 2


def test_failed_placement_leaves_no_empty_event_file(synthetic_store, monkeypatch):
    _seed(synthetic_store, 1)

    import append_event as writer

    def boom(src, dst):
        raise OSError("simulated rename failure")

    monkeypatch.setattr(writer.os, "replace", boom)
    with pytest.raises(WriteRefused, match="failed to place event file"):
        writer.append_event(synthetic_store, reach_classroom_passed()[1])
    monkeypatch.undo()

    assert not (synthetic_store / "events" / "002.yml").exists()
    assert derive_snapshot(synthetic_store)["event_count"] == 1
    assert list((synthetic_store / "events").glob(".*tmp")) == []
