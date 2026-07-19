"""Deterministic append-only writer for Math Mentor learning events.

This is the only module in the package that touches disk.  It is deliberately
narrow:

  * the caller supplies an explicit store path; there is no default target;
  * an event is written only if the structural validator AND the transition
    reducer both accept it;
  * a single-writer lock is taken for the whole read-modify-write window, so two
    processes cannot compute the same sequence number;
  * temporary files are unique per process, and the final name is created with
    O_EXCL so a concurrent writer can never be overwritten;
  * sequence numbers are parsed numerically, so ordering survives past 999;
  * a tail anchor records the event count and head digest, which is what makes
    truncation of the newest events detectable.

Integrity scope, stated honestly: the hash chain plus the tail anchor give
tamper-evidence against edits and truncation **by anything that does not also
rewrite the anchor**.  This is not Git immutability and not a cryptographic
signature; an actor with full write access to the store can rewrite both.

Authority boundary: running this script is not authorization.  A model must
never invoke it to record its own teaching outcome.  `graduated` is refused by
the reducer as a matter of policy - a deterministic writer may compute
`graduation_eligible`, but persisting graduation needs a trusted Human
acceptance path that does not yet exist.  The spaced-review scheduler is a
separate protected boundary and is never written here.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reduce_readonly import reduce_events  # noqa: E402
from validate_events import event_digest, validate_documents  # noqa: E402

LOCK_TIMEOUT_SECONDS = 10.0
EVENT_NAME = re.compile(r"^(\d+)\.yml$")


class WriteRefused(RuntimeError):
    """Raised when validation fails.  No bytes are written in that case."""


class StoreLocked(RuntimeError):
    """Raised when another writer holds the single-writer lock."""


class AnchorUpdateFailed(RuntimeError):
    """The event WAS committed but the tail anchor could not be replaced.

    This is not `WriteRefused`: callers must not report "the store is unchanged".
    """


class SnapshotStale(RuntimeError):
    """The store advanced while a snapshot was being derived.

    Not an error condition for the event log: snapshots are derived data and the
    stale one is simply discarded.
    """


# Re-entrancy: `append_event` holds the lock and then calls helpers that also
# want it.  A plain O_EXCL lock would self-deadlock, so the holder is tracked.
_LOCK_DEPTH: dict[Path, int] = {}


@contextmanager
def single_writer_lock(store: Path, timeout: float = LOCK_TIMEOUT_SECONDS):
    """Hold an exclusive lock for the whole read-modify-write window.

    Uses O_EXCL creation, which is atomic on both Windows and POSIX.  The lock
    file records the owning pid so a stale lock can be diagnosed by a Human;
    it is deliberately NOT auto-broken, because silently stealing a lock is how
    concurrent writers corrupt an append-only store.
    """
    store.mkdir(parents=True, exist_ok=True)
    key = store.resolve()
    if _LOCK_DEPTH.get(key):
        # Already held by this call stack; re-enter without touching the file.
        _LOCK_DEPTH[key] += 1
        try:
            yield
        finally:
            _LOCK_DEPTH[key] -= 1
        return

    lock_path = store / ".writer.lock"
    deadline = time.monotonic() + timeout
    while True:
        try:
            handle = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise StoreLocked(
                    f"another writer holds {lock_path}; if this is stale, a Human must remove it"
                )
            time.sleep(0.05)
    try:
        os.write(handle, f"pid={os.getpid()}\n".encode("utf-8"))
        os.close(handle)
        _LOCK_DEPTH[key] = 1
        yield
    finally:
        _LOCK_DEPTH.pop(key, None)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def _events_dir(store: Path) -> Path:
    return store / "events"


def _event_paths(store: Path) -> list[Path]:
    """Event files ordered by NUMERIC sequence, not lexical filename order."""
    directory = _events_dir(store)
    if not directory.exists():
        return []
    numbered: list[tuple[int, Path]] = []
    for path in directory.glob("*.yml"):
        match = EVENT_NAME.match(path.name)
        if match:
            numbered.append((int(match.group(1)), path))
    numbered.sort(key=lambda item: item[0])
    return [path for _, path in numbered]


def _anchor_path(store: Path) -> Path:
    return store / "integrity" / "head.json"


def read_anchor(store: Path) -> dict | None:
    path = _anchor_path(store)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_anchor(store: Path, events: list[dict]) -> Path:
    path = _anchor_path(store)
    path.parent.mkdir(parents=True, exist_ok=True)
    anchor = {
        "event_count": len(events),
        "head_digest": event_digest(events[-1]) if events else None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "scope_note": (
            "Detects edits to the newest event and truncation of the tail. "
            "Not Git immutability; an actor who rewrites this file too can defeat it."
        ),
    }
    temporary = path.with_suffix(f".json.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(anchor, handle, indent=2, sort_keys=True)
    os.replace(temporary, path)
    return path


def read_store_meta(store: Path) -> dict:
    """Immutable store binding.  A store belongs to exactly one learner.

    Authority never comes from the directory name: a folder named after a learner
    proves nothing.  `store_meta.yml` is the binding, and every event must match it.
    """
    path = store / "store_meta.yml"
    if not path.exists():
        raise WriteRefused(
            f"missing {path.name}: a store must declare its binding "
            "(schema_version, store_id, bound_student_ref, bound_epoch) before use"
        )
    with path.open("r", encoding="utf-8") as handle:
        meta = yaml.safe_load(handle) or {}
    missing = [
        key
        for key in ("schema_version", "store_id", "bound_student_ref", "bound_epoch")
        if not meta.get(key)
    ]
    if missing:
        raise WriteRefused(f"store_meta.yml is missing required keys: {sorted(missing)}")
    return meta


def load_store(store: Path, verify_anchor: bool = True) -> tuple[str, list[dict]]:
    """Read the bound epoch and every event on disk, in numeric order."""
    meta = read_store_meta(store)
    epoch = str(meta["bound_epoch"])

    events: list[dict] = []
    for path in _event_paths(store):
        with path.open("r", encoding="utf-8") as handle:
            events.append(yaml.safe_load(handle))

    if verify_anchor:
        anchor = read_anchor(store)
        if anchor is None:
            # Fail closed: a store that has events but no anchor may have had its
            # anchor deleted to hide a truncation.  Only explicit initialisation
            # or a migration bootstrap may create the first anchor.
            if events:
                raise WriteRefused(
                    "tail anchor is missing while events exist; refusing to proceed. "
                    "Only explicit empty-store initialisation or migration bootstrap "
                    "may create the first anchor."
                )
        else:
            if anchor.get("event_count") != len(events):
                raise WriteRefused(
                    f"tail anchor mismatch: anchor says {anchor.get('event_count')} events, "
                    f"found {len(events)} (truncation or unrecorded append)"
                )
            expected = anchor.get("head_digest")
            actual = event_digest(events[-1]) if events else None
            if expected != actual:
                raise WriteRefused(
                    "tail anchor mismatch: the newest event does not match the recorded head digest"
                )
    return epoch, events


def derive_snapshot(store: Path) -> dict:
    """Recompute the derived snapshot from events on disk.  Pure read."""
    epoch, events = load_store(store)
    report = validate_documents(
        events, check_chain=True, bound_student_ref=read_store_meta(store)["bound_student_ref"]
    )
    if not report.ok:
        raise WriteRefused(f"existing store fails validation: {report.errors}")
    result = reduce_events(events, epoch)
    anchor = read_anchor(store) or {}
    return {
        "derived_at": datetime.now(timezone.utc).isoformat(),
        "bound_epoch": epoch,
        "event_count": len(events),
        # Bind the snapshot to the exact store state it was derived from, so a
        # slow deriver cannot publish over a newer snapshot.
        "source_event_count": anchor.get("event_count"),
        "source_head_digest": anchor.get("head_digest"),
        "snapshot_is_derived": True,
        "rebuildable_from_events": True,
        "nodes": {
            node_id: {
                "status": state.status,
                "qualifying_review_passes": state.review_passes,
                "qualifying_window_kinds": sorted(state.qualifying_kinds),
                "historical_pass_count": state.historical_pass_count,
                "historical_failure_count": state.historical_failure_count,
                "active_review_window_id": state.active_review_window_id,
                "active_review_window_kind": state.active_review_window_kind,
                "graduation_evidence_candidate": state.graduation_evidence_candidate,
                "blocked_from": state.blocked_from,
                "last_event_id": state.last_event_id,
            }
            for node_id, state in sorted(result.snapshot.items())
        },
        "rejected_events": [
            {"event_id": event_id, "reason": reason} for event_id, reason in result.rejected
        ],
    }


def append_event(store: Path, event: dict) -> Path:
    """Validate then atomically append one event.  Refuses on any finding."""
    with single_writer_lock(store):
        meta = read_store_meta(store)
        epoch, existing = load_store(store)

        if event.get("learning_state_epoch") != epoch:
            raise WriteRefused(
                f"event epoch {event.get('learning_state_epoch')!r} != store epoch {epoch!r}"
            )

        bound = meta["bound_student_ref"]
        if event.get("student_ref") != bound:
            raise WriteRefused(
                f"student_ref {event.get('student_ref')!r} does not match the store binding "
                f"{bound!r}; this store accepts events for one learner only"
            )

        expected_prev = event_digest(existing[-1]) if existing else None
        event = dict(event, prev_event_digest=expected_prev)

        candidate = existing + [event]

        report = validate_documents(candidate, check_chain=True, bound_student_ref=bound)
        if not report.ok:
            raise WriteRefused(f"structural validation failed: {report.errors}")

        result = reduce_events(candidate, epoch)
        if result.rejected:
            raise WriteRefused(f"transition rejected: {result.rejected}")

        directory = _events_dir(store)
        directory.mkdir(parents=True, exist_ok=True)
        paths = _event_paths(store)
        next_seq = int(EVENT_NAME.match(paths[-1].name).group(1)) + 1 if paths else 1
        final = directory / f"{next_seq:03d}.yml"

        temporary = directory / f".{next_seq:03d}.{os.getpid()}.tmp"
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            yaml.safe_dump(event, handle, allow_unicode=True, sort_keys=True)

        # Crash-safe append protocol.
        #
        # 1. Reserve the final name with O_EXCL so a concurrent writer cannot be
        #    clobbered.  A crash here leaves a zero-byte reservation, which the
        #    next load detects as an anchor mismatch rather than silently
        #    accepting an empty event.
        # 2. Rename the fully-written temporary over the reservation.
        # 3. Replace the anchor.  A crash between 2 and 3 leaves the event
        #    committed with a stale anchor; `load_store` refuses to proceed and
        #    a Human runs `repair_anchor` after inspecting the tail.
        try:
            descriptor = os.open(final, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            temporary.unlink(missing_ok=True)
            raise WriteRefused(f"refusing to overwrite existing event file {final}")
        os.close(descriptor)

        try:
            os.replace(temporary, final)
        except OSError:
            # Never leave an empty reservation behind on a failed placement.
            try:
                if final.exists() and final.stat().st_size == 0:
                    final.unlink()
            finally:
                temporary.unlink(missing_ok=True)
            raise WriteRefused(f"failed to place event file {final}; store unchanged")

        try:
            write_anchor(store, candidate)
        except OSError as error:
            raise AnchorUpdateFailed(
                f"event {final.name} IS COMMITTED but the tail anchor could not be updated "
                f"({error}). The store is not corrupt, but it will refuse reads until a Human "
                f"inspects the tail and runs repair_anchor."
            ) from error
        return final


def repair_anchor(store: Path) -> Path:
    """Human-run recovery for a committed event whose anchor update failed.

    Deliberately separate from the write path: rebuilding the anchor is exactly
    the operation that could mask a truncation, so it is never automatic.
    """
    _, events = load_store(store, verify_anchor=False)
    report = validate_documents(events, check_chain=True)
    if not report.ok:
        raise WriteRefused(
            f"refusing to rebuild the anchor over an invalid chain: {report.errors}"
        )
    return write_anchor(store, events)


def write_snapshot(store: Path) -> Path:
    """Re-derive the snapshot and publish it atomically, without racing.

    Each snapshot records the anchor it was derived from.  Immediately before
    publication the anchor is re-read: if another writer advanced the store in
    the meantime, this snapshot is stale and is discarded rather than
    overwriting a newer one.  The snapshot is derived data, so dropping it costs
    nothing - it can always be rebuilt from the event log.
    """
    with single_writer_lock(store):
        snapshot = derive_snapshot(store)

        directory = store / "snapshots"
        directory.mkdir(parents=True, exist_ok=True)
        final = directory / "learning_state.yml"
        temporary = directory / f".learning_state.{os.getpid()}.tmp"
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            yaml.safe_dump(snapshot, handle, allow_unicode=True, sort_keys=True)

        # Re-check just before publishing.
        current = read_anchor(store) or {}
        if current.get("head_digest") != snapshot["source_head_digest"]:
            temporary.unlink(missing_ok=True)
            raise SnapshotStale(
                "the store advanced while this snapshot was being derived; "
                "discarding it rather than overwriting a newer snapshot"
            )
        os.replace(temporary, final)
        return final


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: append_event.py <store_dir> <event.yml>", file=sys.stderr)
        return 2

    store = Path(argv[1])
    with Path(argv[2]).open("r", encoding="utf-8") as handle:
        event = yaml.safe_load(handle)

    # Three distinct outcomes; never conflate them.
    try:
        written = append_event(store, event)
    except (WriteRefused, StoreLocked) as error:
        print("outcome: refused_before_commit")
        print(f"REFUSED: {error}", file=sys.stderr)
        print("the store is unchanged")
        return 1
    except AnchorUpdateFailed as error:
        print("outcome: event_committed_snapshot_pending")
        print(f"WARNING: {error}", file=sys.stderr)
        print("the store is NOT unchanged; a Human must inspect the tail and run repair_anchor")
        return 3

    try:
        snapshot_path = write_snapshot(store)
        snapshot = derive_snapshot(store)
    except (OSError, SnapshotStale, WriteRefused) as error:
        # The event is already committed; say so plainly.
        print("outcome: event_committed_snapshot_pending")
        print(f"WARNING: event committed but snapshot publication failed ({error})", file=sys.stderr)
        print("the snapshot is derived and can be rebuilt; the event log is intact")
        return 3

    print("outcome: full_success")
    print(f"appended: {written}")
    print(f"snapshot: {snapshot_path} (derived; rebuildable from events)")
    print(f"event_count after write: {snapshot['event_count']}")
    for node_id, state in snapshot["nodes"].items():
        print(
            f"  {node_id}: {state['status']} "
            f"(qualifying_passes={state['qualifying_review_passes']}, "
            f"graduation_evidence_candidate={state['graduation_evidence_candidate']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
