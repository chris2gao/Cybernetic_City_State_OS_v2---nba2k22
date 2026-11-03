#!/usr/bin/env python3
"""Archive local-only Host Git blobs outside this repository and record SHA256.

Run only on the authorized PC with Host's complete original Git objects present.
Nothing is fetched, rewritten, deleted, pruned, force-pushed or staged.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args],
                       text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError(f"git {args!r}: {p.stderr.strip()}")
    return p.stdout.strip()

def safe_relative(path: str) -> Path:
    p = PurePosixPath(path)
    if p.is_absolute() or not p.parts or any(x in ("..", ".") for x in p.parts):
        raise ValueError(f"unsafe path: {path!r}")
    if "\\" in path or ":" in path:
        raise ValueError(f"non-POSIX relative path: {path!r}")
    return Path(*p.parts)

def sha256_file(path: Path) -> tuple[int, str]:
    size = 0
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            size += len(b)
            h.update(b)
    return size, h.hexdigest()

def archive_blob(repo: Path, archive: Path, row: dict) -> dict:
    sha = row["git_blob_sha1"]
    size = row["size_bytes"]
    rel = safe_relative(row["path"])
    if git(repo, "cat-file", "-t", sha) != "blob":
        raise RuntimeError(f"not a blob: {sha}")
    if int(git(repo, "cat-file", "-s", sha)) != size:
        raise RuntimeError(f"source size mismatch: {rel}")
    output = archive / rel
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.is_symlink():
        raise RuntimeError(f"refusing symlink: {output}")
    if output.exists():
        if not output.is_file() or git(repo, "hash-object", str(output)) != sha:
            raise RuntimeError(f"existing destination has differing bytes: {output}")
        actual, digest = sha256_file(output)
    else:
        fd, temp_name = tempfile.mkstemp(prefix=".nba2k22-", dir=output.parent)
        temp = Path(temp_name)
        try:
            digestor = hashlib.sha256()
            actual = 0
            with os.fdopen(fd, "wb") as dst:
                p = subprocess.Popen(["git", "-C", str(repo), "cat-file", "blob", sha],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                assert p.stdout is not None
                for b in iter(lambda: p.stdout.read(4 * 1024 * 1024), b""):
                    dst.write(b)
                    digestor.update(b)
                    actual += len(b)
                err = p.stderr.read().decode("utf-8", errors="replace") if p.stderr else ""
                if p.wait():
                    raise RuntimeError(f"git cat-file failure: {rel}: {err}")
            if actual != size or git(repo, "hash-object", str(temp)) != sha:
                raise RuntimeError(f"file integrity failed: {rel}")
            digest = digestor.hexdigest()
            os.replace(temp, output)
        finally:
            if temp.exists():
                temp.unlink()
    return {"path": row["path"], "size_bytes": actual, "sha256": digest,
            "git_blob_sha1": sha, "source_commit": row["source_commit"],
            "local_archive_path": str(output)}

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--archive", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    repo, inventory_path, archive = a.repo.resolve(), a.inventory.resolve(), a.archive.resolve()
    if git(repo, "rev-parse", "--is-inside-work-tree") != "true":
        raise RuntimeError("not a complete Git worktree")
    if archive == repo or repo in archive.parents:
        raise RuntimeError("archive must be outside the Git worktree")
    inv = json.loads(inventory_path.read_text(encoding="utf-8"))
    entries = inv["excluded_files"]
    if len(entries) != inv["local_only_count"]:
        raise RuntimeError("inventory count mismatch")
    if sum(x["size_bytes"] for x in entries) != inv["local_only_total_bytes"]:
        raise RuntimeError("inventory bytes mismatch")
    if git(repo, "cat-file", "-t", inv["source_commit"]) != "commit":
        raise RuntimeError("Host source commit not found locally; fetch Host before archiving")
    for row in entries:
        safe_relative(row["path"])
    if a.dry_run:
        print(json.dumps({"dry_run": True, "files": len(entries),
                          "total_size_bytes": inv["local_only_total_bytes"]}, indent=2))
        return 0
    archive.mkdir(parents=True, exist_ok=True)
    complete = []
    for i, row in enumerate(entries, 1):
        complete.append(archive_blob(repo, archive, row))
        if i % 20 == 0 or i == len(entries):
            print(f"archived {i}/{len(entries)}", file=sys.stderr)
    receipt = {"schema_version": "nba2k22.offline_archive.receipt.v1",
               "source_commit": inv["source_commit"],
               "archive_complete": True, "file_count": len(complete),
               "total_size_bytes": sum(x["size_bytes"] for x in complete),
               "files": complete}
    result = archive / "local_archive_receipt.sha256.json"
    tmp = result.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, result)
    print(json.dumps({"archive_complete": True, "files": len(complete),
                      "receipt": str(result)}, indent=2))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ARCHIVE_ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
