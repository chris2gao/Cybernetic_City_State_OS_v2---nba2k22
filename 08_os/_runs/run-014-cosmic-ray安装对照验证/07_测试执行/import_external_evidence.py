from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil


INCLUDED_NAMES = {
    "all-mutants.txt",
    "baseline.stderr.txt",
    "baseline.stdout.txt",
    "baseline.time",
    "dump.time",
    "exec.stderr.txt",
    "exec.stdout.txt",
    "exec.time",
    "init.stderr.txt",
    "init.stdout.txt",
    "init.time",
    "mutants-files.tsv",
    "normalized.json",
    "receipt.env",
    "report.time",
    "report.txt",
    "results.txt",
    "session.dump.jsonl",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_root", type=Path)
    parser.add_argument("destination_root", type=Path)
    parser.add_argument("--replace-existing", action="store_true")
    args = parser.parse_args()
    source_root = args.source_root.resolve(strict=True)
    destination_root = args.destination_root.resolve(strict=False)
    if destination_root.exists() and not args.replace_existing:
        raise SystemExit("destination already exists; refusing to overwrite evidence")
    destination_root.mkdir(parents=True, exist_ok=True)

    selected = sorted(
        path
        for path in source_root.rglob("*")
        if path.is_file() and path.name in INCLUDED_NAMES
    )
    if not selected:
        raise SystemExit("no evidence files selected")

    entries: list[dict[str, object]] = []
    for source in selected:
        relative = source.relative_to(source_root)
        destination = destination_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        entries.append(
            {
                "path": relative.as_posix(),
                "bytes": destination.stat().st_size,
                "sha256": sha256(destination),
            }
        )

    manifest = {
        "format": "run-014-external-evidence-manifest-v1",
        "source_root_recorded": False,
        "file_count": len(entries),
        "total_bytes": sum(int(item["bytes"]) for item in entries),
        "files": entries,
    }
    manifest_path = destination_root / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "file_count": manifest["file_count"],
                "total_bytes": manifest["total_bytes"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
