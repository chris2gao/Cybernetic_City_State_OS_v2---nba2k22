from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_DIR.parents[4]
CANONICAL_TARGET = (
    REPO_ROOT
    / "08_os"
    / "06_execution"
    / "tools"
    / "check_jsonschema"
    / "inspect_schema_refs.py"
)
LINK_PATH = PROJECT_DIR / "target" / "inspect_schema_refs.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    expected_target = CANONICAL_TARGET.resolve(strict=True)
    LINK_PATH.parent.mkdir(exist_ok=True)
    if LINK_PATH.is_symlink():
        if LINK_PATH.resolve(strict=True) != expected_target:
            raise RuntimeError("existing target symlink resolves outside canonical target")
        LINK_PATH.unlink()
    elif LINK_PATH.exists():
        raise RuntimeError("target path exists and is not the managed symlink")
    LINK_PATH.symlink_to(expected_target)
    result = {
        "canonical_target": str(
            CANONICAL_TARGET.relative_to(REPO_ROOT).as_posix()
        ),
        "link_is_symlink": LINK_PATH.is_symlink(),
        "link_resolves_to_canonical": (
            LINK_PATH.resolve(strict=True) == expected_target
        ),
        "canonical_sha256": sha256(expected_target),
        "linked_bytes_sha256": sha256(LINK_PATH),
    }
    result["passed"] = (
        result["link_is_symlink"]
        and result["link_resolves_to_canonical"]
        and result["canonical_sha256"] == result["linked_bytes_sha256"]
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
