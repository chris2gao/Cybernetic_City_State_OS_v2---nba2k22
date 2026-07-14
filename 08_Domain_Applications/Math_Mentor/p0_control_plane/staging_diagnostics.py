"""Read-only diagnostics for the excluded Math Mentor staging corpus."""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import sys
from typing import Any, Sequence

import yaml

try:
    from identity import IdentityError, canonical_json_bytes, sha256_bytes, strict_identity
    from registry_builder import (
        BuildError,
        load_config,
        resolve_commit,
        snapshot_blobs,
        snapshot_tree,
    )
except ImportError:  # pragma: no cover - package import path
    from .identity import (  # type: ignore
        IdentityError,
        canonical_json_bytes,
        sha256_bytes,
        strict_identity,
    )
    from .registry_builder import (  # type: ignore
        BuildError,
        load_config,
        resolve_commit,
        snapshot_blobs,
        snapshot_tree,
    )


def _is_root_candidate(path: str, db_root: str) -> bool:
    prefix = db_root + "/"
    if not path.startswith(prefix):
        return False
    relative = path[len(prefix) :]
    name = PurePosixPath(path).name
    return (
        "/" not in relative
        and PurePosixPath(name).suffix.lower() in {".yaml", ".yml"}
        and name != "schema.yaml"
        and not name.startswith("BRIDGE-")
    )


def scan_staging(repo_root: Path, expected_source_head: str) -> dict[str, Any]:
    """Reproduce staging overlap counts without making staging identity-capable."""

    repo_root = repo_root.resolve()
    source_head = resolve_commit(repo_root, expected_source_head)
    config = load_config(repo_root)
    if source_head != str(config["baseline"]["expected_head"]):
        raise BuildError("staging diagnostics require the frozen baseline source head")
    db_root = str(config["db_root"])
    tree = snapshot_tree(repo_root, source_head, db_root)
    paths = sorted(tree)
    root_paths = [path for path in paths if _is_root_candidate(path, db_root)]
    staging_assets = [path for path in paths if "/_Staging_" in path]
    staging_yaml = [
        path
        for path in staging_assets
        if PurePosixPath(path).suffix.lower() in {".yaml", ".yml"}
    ]
    blobs = snapshot_blobs(repo_root, source_head, [*root_paths, *staging_yaml])

    root_names = {PurePosixPath(path).name for path in root_paths}
    root_hashes: set[str] = set()
    root_ids: set[str] = set()
    for path in root_paths:
        raw = blobs[path]
        root_hashes.add(sha256_bytes(raw))
        document = yaml.safe_load(raw.decode("utf-8"))
        if not isinstance(document, dict):
            raise BuildError(f"root candidate is not a mapping: {path}")
        identity = strict_identity(document)
        if identity.value is not None:
            root_ids.add(identity.value)

    parse_pass = 0
    parse_fail = 0
    parsed_non_mapping = 0
    parsed_without_top_level_id = 0
    basename_shadows = 0
    strict_identity_overlap = 0
    raw_content_identical = 0
    parse_failure_paths: list[str] = []

    for path in staging_yaml:
        raw = blobs[path]
        if PurePosixPath(path).name in root_names:
            basename_shadows += 1
        if sha256_bytes(raw) in root_hashes:
            raw_content_identical += 1
        try:
            document = yaml.safe_load(raw.decode("utf-8"))
        except (UnicodeError, yaml.YAMLError):
            parse_fail += 1
            parse_failure_paths.append(path)
            continue
        parse_pass += 1
        if not isinstance(document, dict):
            parsed_non_mapping += 1
            continue
        if "id" not in document:
            parsed_without_top_level_id += 1
        try:
            identity = strict_identity(document)
        except IdentityError:
            continue
        if identity.value in root_ids:
            strict_identity_overlap += 1

    return {
        "source_head": source_head,
        "policy": {
            "diagnostic_only": True,
            "identity_resolution_allowed": False,
            "staging_precedence_allowed": False,
            "runtime_activation_performed": False,
        },
        "summary": {
            "tracked_staging_assets": len(staging_assets),
            "staging_yaml_files": len(staging_yaml),
            "staging_non_yaml_files": len(staging_assets) - len(staging_yaml),
            "yaml_parse_pass": parse_pass,
            "yaml_parse_fail": parse_fail,
            "parsed_non_mapping": parsed_non_mapping,
            "parsed_without_top_level_id": parsed_without_top_level_id,
            "basename_shadows_of_root_candidates": basename_shadows,
            "strict_identity_overlap_with_root": strict_identity_overlap,
            "raw_content_identical_to_root": raw_content_identical,
            "identity_resolution_from_staging": 0,
        },
        "parse_failure_paths": sorted(parse_failure_paths),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--expected-source-head", required=True)
    args = parser.parse_args(argv)
    try:
        result = scan_staging(args.repo_root, args.expected_source_head)
    except (BuildError, OSError, ValueError) as exc:
        print(f"staging diagnostics failed: {exc}", file=sys.stderr)
        return 2
    sys.stdout.buffer.write(canonical_json_bytes(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
