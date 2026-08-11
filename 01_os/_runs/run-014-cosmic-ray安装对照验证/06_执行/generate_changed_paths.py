from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("base")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve(strict=True)
    output = args.output.resolve(strict=False)
    completed = subprocess.run(
        [
            "git",
            "-c",
            "core.quotepath=false",
            "diff",
            "--name-only",
            args.base,
        ],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    paths = {line for line in completed.stdout.splitlines() if line}
    paths.add(output.relative_to(repo).as_posix())
    output.write_text("\n".join(sorted(paths)) + "\n", encoding="utf-8")
    print(f"changed_paths={len(paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
