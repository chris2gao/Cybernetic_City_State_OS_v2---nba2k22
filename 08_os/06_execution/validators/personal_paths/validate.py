from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable


EXIT_CLEAN = 0
EXIT_HITS = 1
EXIT_ERROR = 2
DEFAULT_CONFIG = Path(__file__).with_name("patterns.json")


class ValidationError(RuntimeError):
    pass


def run_git(repo: Path, *args: str) -> list[str]:
    completed = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise ValidationError(f"git {' '.join(args)} failed: {detail}")
    return [line for line in completed.stdout.splitlines() if line]


def load_patterns(path: Path) -> list[tuple[str, str]]:
    try:
        document: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot load pattern table {path}: {exc}") from exc
    items = document.get("patterns") if isinstance(document, dict) else None
    if not isinstance(items, list) or not items:
        raise ValidationError("pattern table must contain a non-empty patterns list")

    patterns: list[tuple[str, str]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValidationError(f"pattern {index} requires a string id")
        literal = item.get("literal")
        segments = item.get("segments")
        if isinstance(literal, str):
            value = literal
        elif isinstance(segments, list) and all(isinstance(part, str) for part in segments):
            value = "".join(segments)
        else:
            raise ValidationError(f"pattern {item['id']} requires literal or string segments")
        if not value:
            raise ValidationError(f"pattern {item['id']} is empty")
        patterns.append((item["id"], value))
    return patterns


def normalize_scope(repo: Path, raw_scope: str) -> str:
    candidate = (repo / raw_scope).resolve()
    try:
        relative = candidate.relative_to(repo)
    except ValueError as exc:
        raise ValidationError(f"scope escapes repository: {raw_scope}") from exc
    normalized = relative.as_posix().rstrip("/")
    return normalized or "."


def in_scopes(path: str, scopes: Iterable[str]) -> bool:
    return any(scope == "." or path == scope or path.startswith(scope + "/") for scope in scopes)


def candidate_paths(repo: Path, mode: str, base: str | None) -> list[str]:
    if mode == "tracked":
        return sorted(set(run_git(repo, "ls-files")))
    if not base:
        raise ValidationError("--base is required when --mode changed")
    changed: set[str] = set()
    changed.update(run_git(repo, "diff", "--name-only", "--diff-filter=ACMR", base, "HEAD"))
    changed.update(run_git(repo, "diff", "--name-only", "--diff-filter=ACMR"))
    changed.update(run_git(repo, "diff", "--cached", "--name-only", "--diff-filter=ACMR"))
    changed.update(run_git(repo, "ls-files", "--others", "--exclude-standard"))
    return sorted(changed)


def scan_file(path: Path, relative: str, patterns: list[tuple[str, str]]) -> tuple[list[dict[str, Any]], str | None]:
    if path.is_symlink() or not path.is_file():
        return [], "non_regular"
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ValidationError(f"cannot read {relative}: {exc}") from exc
    if b"\x00" in data:
        return [], "binary"
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return [], "non_utf8"

    hits: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for pattern_id, literal in patterns:
            start = 0
            while True:
                offset = line.find(literal, start)
                if offset < 0:
                    break
                left = max(0, offset - 40)
                right = min(len(line), offset + len(literal) + 40)
                hits.append(
                    {
                        "file": relative,
                        "line": line_number,
                        "pattern": pattern_id,
                        "match": literal,
                        "snippet": line[left:right],
                    }
                )
                start = offset + max(1, len(literal))
    return hits, None


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find configured personal absolute paths in repository text.")
    parser.add_argument("--repo-root", default=".", help="Git repository root")
    parser.add_argument("--mode", choices=("tracked", "changed"), default="tracked")
    parser.add_argument("--base", help="Git base revision required by changed mode")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="JSON pattern table")
    parser.add_argument("--summary-only", action="store_true", help="Suppress detailed hit lines")
    parser.add_argument("scopes", nargs="*", default=["."], help="Repository-relative files or directories")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        repo = Path(args.repo_root).resolve(strict=True)
        actual_root = Path(run_git(repo, "rev-parse", "--show-toplevel")[0]).resolve(strict=True)
        if actual_root != repo:
            raise ValidationError(f"--repo-root must be the Git top level: {actual_root}")
        config = Path(args.config)
        if not config.is_absolute():
            config = repo / config
        patterns = load_patterns(config.resolve())
        scopes = [normalize_scope(repo, scope) for scope in args.scopes]
        candidates = [path for path in candidate_paths(repo, args.mode, args.base) if in_scopes(path, scopes)]

        hits: list[dict[str, Any]] = []
        skipped = {"binary": 0, "non_utf8": 0, "non_regular": 0}
        scanned_files = 0
        for relative in candidates:
            file_hits, reason = scan_file(repo / relative, relative, patterns)
            if reason:
                skipped[reason] += 1
                continue
            scanned_files += 1
            hits.extend(file_hits)

        if not args.summary_only:
            for hit in hits:
                print(
                    f"{hit['file']}:{hit['line']}:{hit['pattern']}: "
                    f"{json.dumps(hit['snippet'], ensure_ascii=False)}"
                )
        hit_counts_by_top_level: dict[str, int] = {}
        hit_files_by_top_level: dict[str, set[str]] = {}
        for hit in hits:
            top_level = hit["file"].split("/", 1)[0]
            hit_counts_by_top_level[top_level] = hit_counts_by_top_level.get(top_level, 0) + 1
            hit_files_by_top_level.setdefault(top_level, set()).add(hit["file"])
        summary = {
            "mode": args.mode,
            "candidate_files": len(candidates),
            "scanned_files": scanned_files,
            "skipped": skipped,
            "hit_files": len({hit["file"] for hit in hits}),
            "hit_file_paths": sorted({hit["file"] for hit in hits}),
            "hit_count": len(hits),
            "hit_counts_by_top_level": dict(sorted(hit_counts_by_top_level.items())),
            "hit_files_by_top_level": {
                key: len(value) for key, value in sorted(hit_files_by_top_level.items())
            },
        }
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return EXIT_HITS if hits else EXIT_CLEAN
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
