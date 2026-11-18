#!/usr/bin/env python3
"""Read-only check that the skill adapters on disk equal what the registry generates.

Fails (exit 1, one line per finding) on a missing or hand-edited SKILL.md, a skill
directory the registry does not produce, a read path that does not exist, a role that
names an unknown unit, an inventoried mechanism without a skill, or an output root
that CORE_MANIFEST.yml does not list as core-owned. Exit 0 prints skills_valid.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_skills  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)
    return generate_skills.main(["--repo-root", args.repo_root, "--check"])


if __name__ == "__main__":
    sys.exit(main())
