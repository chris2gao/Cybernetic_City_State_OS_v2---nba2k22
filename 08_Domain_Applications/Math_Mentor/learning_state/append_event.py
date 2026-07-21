"""Deterministic append-only writer for Math Mentor learning events.

This is the only module in the package that touches disk.  It is deliberately
narrow:

  * the caller supplies an explicit store path; there is no default target;
  * an event is written only if the structural validator AND the transition
    reducer both accept it;
  * a single-writer lock is taken for the whole read-modify-write window, so two
    processes cannot compute the same sequence number;
  * temporary files are unique per process AND thread, and the final name uses
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
`graduation_evidence_candidate`, but persisting graduation needs a trusted Human
acceptance path that does not yet exist.  The spaced-review scheduler is a
separate protected boundary and is never written here.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys
import threading
import time
from uuid import uuid4

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reduce_readonly import reduce_events  # noqa: E402
from validate_events import (  # noqa: E402
    ValidatorUnavailable,
    event_digest,
    validate_documents,
)

LOCK_TIMEOUT_SECONDS = 10.0
EVENT_NAME = re.compile(r"^(\d+)\.yml$")
STORE_META_SCHEMA_PATH = Path(__file__).resolve().parent / "learning_store_meta.schema.json"


def _canonical_epoch() -> str:
    with (Path(__file__).resolve().parent / "epoch.yml").open("r", encoding="utf-8") as handle:
        return str(yaml.safe_load(handle)["bound_epoch"])


CANONICAL_EPOCH = _canonical_epoch()


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


@contextmanager
def single_writer_lock(store: Path, timeout: float = LOCK_TIMEOUT_SECONDS):
    """Hold an exclusive lock for the whole read-modify-write window.

    Strictly non-reentrant.  An earlier version tracked depth in a process-global
    dict keyed by path, which made the lock useless between threads in one
    process: a second thread would see "already held" and walk straight in.  No
    call path needs nesting, so the simple exclusive lock is the correct one.

    O_EXCL creation is atomic on both Windows and POSIX.  The lock file records
    the owning pid and thread so a stale lock can be diagnosed by a Human; it is
    deliberately NOT auto-broken, because silently stealing a lock is how
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
            time.sleep(0.02)
    try:
        os.write(
            handle,
            f"pid={os.getpid()}\nthread={threading.get_ident()}\n".encode("utf-8"),
        )
        os.close(handle)
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def _unique_suffix() -> str:
    """Thread- and process-unique temporary suffix.

    PID alone is not enough: two threads in one process share it and would race
    on the same temporary path.
    """
    return f"{os.getpid()}.{threading.get_ident()}.{uuid4().hex[:8]}"


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


ANCHOR_REQUIRED_FIELDS = (
    "schema_version",
    "event_count",
    "head_digest",
    "store_meta_digest",
    "updated_at",
)
ANCHOR_SCHEMA_VERSION = "citystate.math_mentor.learning_state_anchor.v1"


def read_anchor(store: Path) -> dict | None:
    """Read the tail anchor, or None if absent.

    Malformed content is an explicit refusal, never a traceback: an unreadable
    anchor must not be mistaken for a missing one, because "missing" has its own
    (also fail-closed) meaning.
    """
    path = _anchor_path(store)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            anchor = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise WriteRefused(f"tail anchor is not readable JSON: {error}") from error
    if not isinstance(anchor, dict):
        raise WriteRefused("tail anchor is not a JSON object; refusing to interpret it")
    missing = [key for key in ANCHOR_REQUIRED_FIELDS if key not in anchor]
    if missing:
        raise WriteRefused(
            f"tail anchor is missing required fields {sorted(missing)}; refusing to accept a "
            "downgraded anchor. A Human must run repair_anchor after verifying the store."
        )
    if anchor.get("schema_version") != ANCHOR_SCHEMA_VERSION:
        raise WriteRefused(
            f"tail anchor schema_version {anchor.get('schema_version')!r} != "
            f"{ANCHOR_SCHEMA_VERSION!r}"
        )
    return anchor


def write_anchor(store: Path, events: list[dict], meta: dict | None = None) -> Path:
    path = _anchor_path(store)
    path.parent.mkdir(parents=True, exist_ok=True)
    if meta is None:
        meta = read_store_meta(store)
    anchor = {
        "schema_version": ANCHOR_SCHEMA_VERSION,
        "event_count": len(events),
        "head_digest": event_digest(events[-1]) if events else None,
        # Binding digest: an accidental edit to store_meta.yml after events exist
        # is detected rather than silently followed.
        "store_meta_digest": store_meta_digest(meta),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "scope_note": (
            "Detects edits to the newest event, truncation of the tail, and changes to "
            "the store binding. Not Git immutability; an actor who rewrites this file "
            "too can defeat it."
        ),
    }
    temporary = path.with_suffix(f".json.{_unique_suffix()}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(anchor, handle, indent=2, sort_keys=True)
    os.replace(temporary, path)
    return path


def store_meta_digest(meta: dict) -> str:
    """Stable digest of the canonical binding, for the tail anchor."""
    encoded = json.dumps(meta, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def read_store_meta(store: Path) -> dict:
    """Immutable store binding, validated against its canonical schema.

    Authority never comes from the directory name: a folder named after a learner
    proves nothing.  `store_meta.yml` is the binding, every event must match it,
    and an arbitrary nonempty YAML field is not accepted as one.
    """
    path = store / "store_meta.yml"
    if not path.exists():
        raise WriteRefused(
            f"missing {path.name}: a store must declare its binding "
            "(schema_version, store_id, bound_student_ref, bound_epoch) before use"
        )
    try:
        with path.open("r", encoding="utf-8") as handle:
            meta = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as error:
        raise WriteRefused(f"store_meta.yml is not readable YAML: {error}") from error
    if meta is None:
        meta = {}
    if not isinstance(meta, dict):
        raise WriteRefused("store_meta.yml does not contain a mapping; refusing to interpret it")

    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError as error:  # pragma: no cover - environment failure path
        raise WriteRefused(
            "jsonschema is required to validate store metadata; refusing to proceed "
            "with an unvalidated binding"
        ) from error

    with STORE_META_SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(meta),
        key=lambda e: list(e.path),
    )
    if errors:
        detail = "; ".join(
            f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors
        )
        raise WriteRefused(f"store_meta.yml fails its canonical schema: {detail}")

    if meta["bound_epoch"] != CANONICAL_EPOCH:
        raise WriteRefused(
            f"store bound_epoch {meta['bound_epoch']!r} != package canonical epoch "
            f"{CANONICAL_EPOCH!r}; a store may not follow different transition semantics"
        )
    return meta


def load_store(store: Path, verify_anchor: bool = True) -> tuple[str, list[dict]]:
    """Read the bound epoch and every event on disk, in numeric order."""
    meta = read_store_meta(store)
    epoch = str(meta["bound_epoch"])

    directory = _events_dir(store)
    if directory.exists():
        # Anything ending in .yml inside the authoritative events directory is
        # either an event or a problem; silently ignoring it would hide a
        # misplaced or renamed file.
        unexpected = sorted(
            p.name for p in directory.glob("*.yml") if not EVENT_NAME.match(p.name)
        )
        if unexpected:
            raise WriteRefused(
                f"unexpected files in the events directory: {unexpected}. "
                "Event files must be <number>.yml; nothing else may live here."
            )

    paths = _event_paths(store)
    # Sequence numbers must be contiguous from 1. A gap means an event was
    # removed or never landed, and replaying around it would misstate history.
    expected_seq = [int(EVENT_NAME.match(p.name).group(1)) for p in paths]
    if expected_seq and expected_seq != list(range(1, len(expected_seq) + 1)):
        raise WriteRefused(
            f"event sequence has gaps or does not start at 1: {expected_seq}. "
            "Gaps are not permitted; a missing event must be investigated, not skipped."
        )

    events: list[dict] = []
    for path in paths:
        with path.open("r", encoding="utf-8") as handle:
            try:
                document = yaml.safe_load(handle)
            except yaml.YAMLError as error:
                raise WriteRefused(f"event file {path.name} is not valid YAML: {error}") from error
        if not isinstance(document, dict):
            raise WriteRefused(
                f"event file {path.name} does not contain a mapping; refusing to load"
            )
        events.append(document)

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
            recorded_meta = anchor.get("store_meta_digest")
            if recorded_meta is None:
                # A downgraded anchor is not acceptable: without the binding
                # digest, swapping store_meta.yml would go unnoticed. Rebuilding
                # it is an explicit Human-run repair, never an implicit upgrade.
                raise WriteRefused(
                    "tail anchor is missing store_meta_digest; refusing to accept a downgraded "
                    "anchor. A Human must run repair_anchor after verifying the store binding."
                )
            if recorded_meta != store_meta_digest(meta):
                raise WriteRefused(
                    "store binding changed after events were written: store_meta.yml no longer "
                    "matches the digest recorded in the tail anchor"
                )
    return epoch, events


def derive_snapshot(store: Path, allow_rejected: bool = False) -> dict:
    """Recompute the derived snapshot from events on disk.  Pure read.

    Fail-closed: if the reducer rejects any event on disk, no snapshot is
    produced.  Publishing a snapshot that silently ignores illegal events would
    misrepresent the store as consistent.  `allow_rejected=True` is a diagnostic
    dry-run switch for inspecting what was rejected; it must not be used on a
    publication path.
    """
    epoch, events = load_store(store)
    report = validate_documents(
        events, check_chain=True, bound_student_ref=read_store_meta(store)["bound_student_ref"]
    )
    if not report.ok:
        raise WriteRefused(f"existing store fails validation: {report.errors}")
    result = reduce_events(events, epoch)
    if result.rejected and not allow_rejected:
        raise WriteRefused(
            "refusing to derive a snapshot: the reducer rejected events already on disk "
            f"({[event_id for event_id, _ in result.rejected]}). Run with allow_rejected=True "
            "for diagnosis only."
        )
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
                # Causes stay distinct in the snapshot too: collapsing them would
                # throw away the distinction the reducer just computed.
                "historical_failure_count": state.historical_failure_count,
                "historical_expiry_count": state.historical_expiry_count,
                "historical_decay_count": state.historical_decay_count,
                "active_review_window_id": state.active_review_window_id,
                "active_review_window_kind": state.active_review_window_kind,
                "active_review_window_opened_at": state.active_review_window_opened_at,
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

        # Pre-release authority boundary, NOT identity verification.
        #
        # No trusted Human admission path exists.  A `human_acceptance` event is
        # just a label plus two strings, and persisting one would let anything
        # able to write a file grant Human authority to itself.  The reducer may
        # still EVALUATE such a proposal - that is useful and harmless - but the
        # writer refuses to make it durable.
        if event.get("event_type") == "human_acceptance":
            raise WriteRefused(
                "unsupported_pending_trusted_human_admission: refusing to persist a "
                "human_acceptance event. Unblocking and graduation require a trusted "
                "Human admission path that does not exist yet; an event label, a "
                "source_type string and a human_authorization_ref are not authority."
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

        temporary = directory / f".{next_seq:03d}.{_unique_suffix()}.tmp"
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            yaml.safe_dump(event, handle, allow_unicode=True, sort_keys=True)

        # Failure-aware append protocol.
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
    the operation that could mask a truncation, so it is never automatic and it
    refuses on ANY inconsistency.  Rebuilding over a mixed-learner,
    epoch-mismatched, chain-broken or transition-invalid sequence would launder
    a corrupt store into an apparently valid one.
    """
    with single_writer_lock(store):
        meta = read_store_meta(store)
        bound = meta["bound_student_ref"]
        epoch, events = load_store(store, verify_anchor=False)

        report = validate_documents(events, check_chain=True, bound_student_ref=bound)
        if not report.ok:
            raise WriteRefused(
                f"refusing to rebuild the anchor over an invalid store: {report.errors}"
            )

        result = reduce_events(events, epoch)
        if result.rejected:
            raise WriteRefused(
                "refusing to rebuild the anchor over a transition-invalid sequence: "
                f"{result.rejected}"
            )
        return write_anchor(store, events)


def write_snapshot(store: Path) -> tuple[Path, dict]:
    """Re-derive the snapshot and publish it atomically, without racing.

    Returns the path it published AND the exact snapshot that was written.  The
    snapshot is returned rather than left to the caller to re-derive: a caller
    that re-derives afterwards would describe whatever the store looks like
    then, which may already be a later head than the file on disk.

    Each snapshot records the anchor it was derived from.  Immediately before
    publication the anchor is re-read: if another writer advanced the store in
    the meantime, this snapshot is stale and is discarded rather than
    overwriting a newer one.  The snapshot is derived data, so dropping it costs
    nothing - it can always be rebuilt from the event log.
    """
    # The lock spans derive -> write -> compare -> replace as ONE critical
    # section.  Comparing outside the lock left a TOCTOU window in which another
    # writer could advance the store between the comparison and the replace, so
    # a stale snapshot could still land.  `append_event` releases its lock before
    # calling this, so there is no nested-lock path to reintroduce.
    with single_writer_lock(store):
        snapshot = derive_snapshot(store)  # fail-closed on reducer rejection

        directory = store / "snapshots"
        directory.mkdir(parents=True, exist_ok=True)
        final = directory / "learning_state.yml"
        temporary = directory / f".learning_state.{_unique_suffix()}.tmp"
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            yaml.safe_dump(snapshot, handle, allow_unicode=True, sort_keys=True)

        current = read_anchor(store) or {}
        if current.get("head_digest") != snapshot["source_head_digest"]:
            temporary.unlink(missing_ok=True)
            raise SnapshotStale(
                "the store advanced while this snapshot was being derived; "
                "discarding it rather than overwriting a newer snapshot"
            )
        os.replace(temporary, final)
        # Return the exact snapshot that was published, not just its path: a
        # caller that re-derives afterwards would describe a later store head
        # and misreport what it actually wrote.
        return final, snapshot


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: append_event.py <store_dir> <event.yml>", file=sys.stderr)
        return 2

    store = Path(argv[1])

    # Three outcomes, scoped to EXPECTED OPERATIONAL failures.  They make no
    # claim about arbitrary programmer bugs, which still surface as tracebacks.
    try:
        with Path(argv[2]).open("r", encoding="utf-8") as handle:
            event = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as error:
        print("outcome: refused_before_commit")
        print(f"REFUSED: cannot read the event file ({error})", file=sys.stderr)
        print("the store is unchanged")
        return 1
    if not isinstance(event, dict):
        print("outcome: refused_before_commit")
        print("REFUSED: the event file did not contain a mapping", file=sys.stderr)
        print("the store is unchanged")
        return 1

    try:
        written = append_event(store, event)
    except (WriteRefused, StoreLocked, ValidatorUnavailable) as error:
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
        # Report the snapshot that was actually published. Re-deriving here would
        # describe whatever the store looks like now, which may already be a
        # later head than the file on disk.
        snapshot_path, snapshot = write_snapshot(store)
    except (OSError, SnapshotStale, WriteRefused, StoreLocked) as error:
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
