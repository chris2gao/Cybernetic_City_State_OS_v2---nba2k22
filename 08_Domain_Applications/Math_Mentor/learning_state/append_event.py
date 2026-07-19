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


@contextmanager
def single_writer_lock(store: Path, timeout: float = LOCK_TIMEOUT_SECONDS):
    """Hold an exclusive lock for the whole read-modify-write window.

    Uses O_EXCL creation, which is atomic on both Windows and POSIX.  The lock
    file records the owning pid so a stale lock can be diagnosed by a Human;
    it is deliberately NOT auto-broken, because silently stealing a lock is how
    concurrent writers corrupt an append-only store.
    """
    store.mkdir(parents=True, exist_ok=True)
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
        yield
    finally:
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


def load_store(store: Path, verify_anchor: bool = True) -> tuple[str, list[dict]]:
    """Read the bound epoch and every event on disk, in numeric order."""
    epoch_file = store / "epoch.yml"
    with epoch_file.open("r", encoding="utf-8") as handle:
        epoch = str(yaml.safe_load(handle)["bound_epoch"])

    events: list[dict] = []
    for path in _event_paths(store):
        with path.open("r", encoding="utf-8") as handle:
            events.append(yaml.safe_load(handle))

    if verify_anchor:
        anchor = read_anchor(store)
        if anchor is not None:
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
    report = validate_documents(events, check_chain=True)
    if not report.ok:
        raise WriteRefused(f"existing store fails validation: {report.errors}")
    result = reduce_events(events, epoch)
    return {
        "derived_at": datetime.now(timezone.utc).isoformat(),
        "bound_epoch": epoch,
        "event_count": len(events),
        "snapshot_is_derived": True,
        "rebuildable_from_events": True,
        "nodes": {
            node_id: {
                "status": state.status,
                "review_passes": state.review_passes,
                "distinct_windows": len(state.counted_windows),
                "graduation_eligible": state.graduation_eligible,
                "blocked_from": state.blocked_from,
                "last_event_id": state.last_event_id,
            }
            for node_id, state in sorted(result.snapshot.items())
        },
        "superseded_events": list(result.superseded),
        "rejected_events": [
            {"event_id": event_id, "reason": reason} for event_id, reason in result.rejected
        ],
    }


def append_event(store: Path, event: dict) -> Path:
    """Validate then atomically append one event.  Refuses on any finding."""
    with single_writer_lock(store):
        epoch, existing = load_store(store)

        if event.get("learning_state_epoch") != epoch:
            raise WriteRefused(
                f"event epoch {event.get('learning_state_epoch')!r} != store epoch {epoch!r}"
            )

        expected_prev = event_digest(existing[-1]) if existing else None
        event = dict(event, prev_event_digest=expected_prev)

        candidate = existing + [event]

        report = validate_documents(candidate, check_chain=True)
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

        # O_EXCL: never clobber a file a concurrent writer just created.
        try:
            descriptor = os.open(final, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            temporary.unlink(missing_ok=True)
            raise WriteRefused(f"refusing to overwrite existing event file {final}")
        os.close(descriptor)
        os.replace(temporary, final)

        write_anchor(store, candidate)
        return final


def write_snapshot(store: Path) -> Path:
    """Re-derive the snapshot from disk and write it atomically."""
    snapshot = derive_snapshot(store)
    directory = store / "snapshots"
    directory.mkdir(parents=True, exist_ok=True)
    final = directory / "learning_state.yml"
    temporary = directory / f".learning_state.{os.getpid()}.tmp"
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(snapshot, handle, allow_unicode=True, sort_keys=True)
    os.replace(temporary, final)
    return final


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: append_event.py <store_dir> <event.yml>", file=sys.stderr)
        return 2

    store = Path(argv[1])
    with Path(argv[2]).open("r", encoding="utf-8") as handle:
        event = yaml.safe_load(handle)

    try:
        written = append_event(store, event)
    except (WriteRefused, StoreLocked) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 1

    snapshot_path = write_snapshot(store)
    snapshot = derive_snapshot(store)

    print(f"appended: {written}")
    print(f"snapshot: {snapshot_path} (derived; rebuildable from events)")
    print(f"event_count after write: {snapshot['event_count']}")
    for node_id, state in snapshot["nodes"].items():
        print(
            f"  {node_id}: {state['status']} "
            f"(review_passes={state['review_passes']}, "
            f"graduation_eligible={state['graduation_eligible']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
