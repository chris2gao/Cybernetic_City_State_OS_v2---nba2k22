#!/usr/bin/env python3
"""Reject live stage-collaborative-deliberation instance state under canonical paths."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXIT_PASS = 0
EXIT_UNAUTHORIZED_STATE = 15
CANONICAL_ROOT = Path("08_os/03_mechanisms/stage_collaborative_deliberation")
PROHIBITED_NAMES = ("objects", "transitions", "events", "receipts", "sessions", "failures", "_runtime")


def validate(repo_root: Path) -> tuple[int, list[str]]:
    canonical = repo_root / CANONICAL_ROOT
    found = [str(CANONICAL_ROOT / name) for name in PROHIBITED_NAMES if (canonical / name).exists()]
    return (EXIT_UNAUTHORIZED_STATE if found else EXIT_PASS, found)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root")
    parser.add_argument("--json-output", action="store_true")
    args = parser.parse_args()
    code, found = validate(Path(args.repo_root))
    if args.json_output:
        print(json.dumps({"exit_code": code, "prohibited_paths": found}))
    return code


if __name__ == "__main__":
    sys.exit(main())
