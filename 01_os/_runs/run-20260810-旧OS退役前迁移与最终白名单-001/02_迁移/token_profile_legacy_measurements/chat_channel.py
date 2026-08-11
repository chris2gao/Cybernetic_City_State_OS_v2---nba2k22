#!/usr/bin/env python3
"""C0-only local chat channel with monotonic, atomically-published messages."""
from __future__ import annotations

import argparse, datetime as dt, os, re, shutil, tempfile, time
from pathlib import Path

DEFAULT_ROOT = Path("C:/Users/gk/AppData/Local/CityState/local_bus/chat/")
SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

def check(value: str, label: str) -> str:
    if not SAFE.fullmatch(value): raise ValueError(f"unsafe {label}")
    return value
def atomic_write(path: Path, content: str) -> None:
    fd, temp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp): os.unlink(temp)
def channel(root: Path, topic: str) -> Path: return root / check(topic, "topic")
def acquire(directory: Path) -> Path:
    lock = directory / ".sequence.lock"; deadline = time.monotonic() + 5
    while True:
        try: lock.mkdir(); return lock
        except FileExistsError:
            if time.monotonic() >= deadline: raise RuntimeError("channel lock timeout")
            time.sleep(.02)
def release(lock: Path) -> None: lock.rmdir()
def new(args: argparse.Namespace) -> None:
    directory = channel(args.root, args.topic); directory.mkdir(parents=True, exist_ok=False)
    people = [check(x, "participant") for x in args.participants.split(",") if x]
    if not people: raise ValueError("participants required")
    created = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    atomic_write(directory / "_channel.yml", "participants:\n" + "".join(f"  - {x}\n" for x in people) + f"task_ref: {args.task_ref}\nstatus: open\ncreated: {created}\n")
    print(directory)
def post(args: argparse.Namespace) -> None:
    directory = channel(args.root, args.topic)
    if not (directory / "_channel.yml").is_file(): raise ValueError("unknown channel")
    sender = check(args.sender, "sender"); body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else args.body
    if body is None or len(body.splitlines()) > 30: raise ValueError("body must contain at most 30 lines")
    lock = acquire(directory)
    try:
        seqs = [int(match.group(1)) for item in directory.glob("[0-9][0-9][0-9]_*.md") if (match := re.match(r"(\d+)_", item.name))]
        seq = max(seqs, default=0) + 1; target = directory / f"{seq:03d}_{sender}.md"
        stamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        content = f"---\nseq: {seq}\nsender: {sender}\nsession_id: {args.session_id}\nreply_to: {args.reply_to or 'null'}\nts: {stamp}\n---\n{body.rstrip()}\n"
        atomic_write(target, content)
    finally: release(lock)
    print(target)
def read(args: argparse.Namespace) -> None:
    directory = channel(args.root, args.topic)
    for path in sorted(directory.glob("[0-9][0-9][0-9]_*.md")): print(path.read_text(encoding="utf-8"), end="")
def gc(args: argparse.Namespace) -> None:
    cutoff = time.time() - args.days * 86400; directory = channel(args.root, args.topic); removed = 0
    for path in directory.glob("[0-9][0-9][0-9]_*.md"):
        if path.stat().st_mtime < cutoff: path.unlink(); removed += 1
    print(f"removed={removed}")
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--root", type=Path, default=DEFAULT_ROOT); sub = parser.add_subparsers(dest="cmd", required=True)
    one = sub.add_parser("new"); one.add_argument("topic"); one.add_argument("--participants", required=True); one.add_argument("--task-ref", required=True); one.set_defaults(fn=new)
    two = sub.add_parser("post"); two.add_argument("topic"); two.add_argument("--sender", required=True); two.add_argument("--session-id", required=True); two.add_argument("--reply-to"); group = two.add_mutually_exclusive_group(required=True); group.add_argument("--body"); group.add_argument("--body-file"); two.set_defaults(fn=post)
    three = sub.add_parser("read"); three.add_argument("topic"); three.set_defaults(fn=read)
    four = sub.add_parser("gc"); four.add_argument("topic"); four.add_argument("--days", type=int, default=30); four.set_defaults(fn=gc)
    args = parser.parse_args()
    try: args.fn(args); return 0
    except (OSError, ValueError, RuntimeError) as exc: parser.error(str(exc))
if __name__ == "__main__": raise SystemExit(main())
