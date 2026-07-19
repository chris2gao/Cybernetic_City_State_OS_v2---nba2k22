"""Deterministic append-only writer for Math Mentor learning events.

This is the only module in the package that touches disk.  It is deliberately
narrow:

  * the caller supplies an explicit store path; there is no default target;
  * an event is written only if BOTH the structural validator and the
    transition reducer accept it;
  * writes go to a temporary file and are atomically renamed;
  * the chain digest is computed from the last event on disk, so a tampered
    history cannot be silently extended;
  * after writing, the store is re-read and the derived snapshot is recomputed.

Authority boundary: running this script is not authorization.  A model must
never invoke it to record its own teaching outcome.  Transitions into
`graduated` additionally require `human_authorization_ref`, which a model may
not fabricate.  The spaced-review scheduler is a separate protected boundary and
is never written here.

The store lives outside Git (see the repository .gitignore), so the hash chain
is what provides tamper-evidence.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reduce_readonly import reduce_events  # noqa: E402
from validate_events import event_digest, validate_documents  # noqa: E402


class WriteRefused(RuntimeError):
    """Raised when validation fails.  No bytes are written in that case."""


def _events_dir(store: Path) -> Path:
    return store / "events"


def load_store(store: Path) -> tuple[str, list[dict]]:
    """Read the bound epoch and every event currently on disk, in order."""
    epoch_file = store / "epoch.yml"
    with epoch_file.open("r", encoding="utf-8") as handle:
        epoch = str(yaml.safe_load(handle)["bound_epoch"])

    events: list[dict] = []
    directory = _events_dir(store)
    if directory.exists():
        for path in sorted(directory.glob("*.yml")):
            with path.open("r", encoding="utf-8") as handle:
                events.append(yaml.safe_load(handle))
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
        "nodes": {
            node_id: {
                "status": state.status,
                "review_passes": state.review_passes,
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
    final = directory / f"{len(existing) + 1:03d}.yml"
    if final.exists():
        raise WriteRefused(f"refusing to overwrite existing event file {final}")

    temporary = final.with_suffix(".yml.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(event, handle, allow_unicode=True, sort_keys=True)
    os.replace(temporary, final)
    return final


def write_snapshot(store: Path) -> Path:
    """Re-derive the snapshot from disk and write it atomically."""
    snapshot = derive_snapshot(store)
    directory = store / "snapshots"
    directory.mkdir(parents=True, exist_ok=True)
    final = directory / "learning_state.yml"
    temporary = final.with_suffix(".yml.tmp")
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
    except WriteRefused as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 1

    snapshot_path = write_snapshot(store)
    snapshot = derive_snapshot(store)

    print(f"appended: {written}")
    print(f"snapshot: {snapshot_path}")
    print(f"event_count after write: {snapshot['event_count']}")
    for node_id, state in snapshot["nodes"].items():
        print(f"  {node_id}: {state['status']} (review_passes={state['review_passes']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
