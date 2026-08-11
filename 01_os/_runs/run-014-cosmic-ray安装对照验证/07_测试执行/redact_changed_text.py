from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


BASE = "a6261cf3a8f0e0263b41a6ec32a3dd6c16ed653c"
RUN_REL = Path("01_os/_runs/run-014-cosmic-ray安装对照验证")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def changed_paths(repo: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "-c", "core.quotepath=false", "diff", "--name-only", BASE],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return [line for line in completed.stdout.splitlines() if line]


def encoded_variants(value: str) -> set[str]:
    return {value, value.replace("\\", "\\\\")}


def rebuild_manifest(experiments: Path) -> dict[str, int]:
    manifest_path = experiments / "manifest.json"
    files = sorted(
        path
        for path in experiments.rglob("*")
        if path.is_file()
        and path != manifest_path
        and path.name != ".gitattributes"
    )
    entries = [
        {
            "path": path.relative_to(experiments).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    manifest = {
        "format": "run-014-external-evidence-manifest-v1",
        "source_root_recorded": False,
        "file_count": len(entries),
        "total_bytes": sum(int(entry["bytes"]) for entry in entries),
        "files": entries,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "file_count": len(entries),
        "total_bytes": int(manifest["total_bytes"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--cosmic-venv", required=True)
    parser.add_argument("--mutmut-venv", required=True)
    parser.add_argument("--linux-repository-root", required=True)
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    experiments = repo / RUN_REL / "07_测试执行/evidence/experiments"
    manifest_path = experiments / "manifest.json"

    replacements: list[tuple[str, str]] = []
    contextual = [
        (args.cosmic_venv, "${COSMIC_RAY_VENV}"),
        (args.mutmut_venv, "${MUTMUT_VENV}"),
        (args.linux_repository_root, "${REPOSITORY_ROOT}"),
        (str(repo), "${REPOSITORY_ROOT}"),
        (str(repo).replace("\\", "/"), "${REPOSITORY_ROOT}"),
    ]
    for actual, placeholder in contextual:
        replacements.extend((variant, placeholder) for variant in encoded_variants(actual))
    replacements.extend(
        [
            ("/home/" + "gk", "${USER_HOME}"),
            ("C:\\Users" + "\\gk", "${USER_HOME}"),
            ("C:\\\\Users" + "\\\\gk", "${USER_HOME}"),
            ("E:\\" + "newStand", "${WORKSPACE_ROOT}"),
            ("E:\\\\" + "newStand", "${WORKSPACE_ROOT}"),
        ]
    )
    replacements.sort(key=lambda item: len(item[0]), reverse=True)

    updated = 0
    binary_artifact_count = 0
    replacement_count = 0
    for relative in changed_paths(repo):
        path = repo / relative
        if not path.is_file() or path == manifest_path:
            continue
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            binary_artifact_count += 1
            continue
        redacted = text
        for actual, placeholder in replacements:
            count = redacted.count(actual)
            if count:
                replacement_count += count
                redacted = redacted.replace(actual, placeholder)
        if redacted != text:
            path.write_text(redacted, encoding="utf-8", newline="\n")
            updated += 1

    manifest = rebuild_manifest(experiments)
    summary = {
        "binary_artifact_count": binary_artifact_count,
        "manifest_file_count": manifest["file_count"],
        "manifest_total_bytes": manifest["total_bytes"],
        "replacement_count": replacement_count,
        "updated_text_files": updated,
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
