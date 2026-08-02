from __future__ import annotations

import json
from pathlib import Path
import subprocess


repo = Path(__file__).resolve().parents[4]
base = "dab1ecef2d34c4cb70dfa6529a2b2f9f4612570b"
allowed_prefix = "08_os/_runs/run-023-通讯机制需求建模/"


def git_paths(*arguments: str) -> set[str]:
    process = subprocess.run(
        ["git", "-c", "core.quotepath=false", *arguments, "-z"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    return {item for item in process.stdout.decode("utf-8").split("\0") if item}


changed = git_paths("diff", "--name-only", base)
changed.update(git_paths("ls-files", "--others", "--exclude-standard"))
outside = sorted(path for path in changed if not path.startswith(allowed_prefix))
result = {
    "schema_version": "citystate.allowlist_check.v1",
    "base": base,
    "changed_path_count": len(changed),
    "outside_allowlist_count": len(outside),
    "outside_allowlist": outside,
    "passed": not outside,
}
output = repo / "08_os/_runs/run-023-通讯机制需求建模/07_测试执行/scope_results.json"
output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, sort_keys=True))
raise SystemExit(0 if result["passed"] else 1)
