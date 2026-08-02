from __future__ import annotations

import json
from pathlib import Path
import subprocess


repo = Path(__file__).resolve().parents[4]
base = "a0a2cdbb8d9e8d2e8ea2c50bcbcef601088e72dc"
allowed_exact = {
    "08_os/03_mechanisms/environment_capability/实现/正例与负例说明_v1.md",
    "08_os/05_registry/environment_capability_v1.yml",
}
allowed_prefixes = (
    "08_os/06_execution/validators/environment_capability/",
    "08_os/_runs/run-022-环境能力checker提升与回归/",
)


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
outside = sorted(
    path for path in changed
    if path not in allowed_exact and not any(path.startswith(prefix) for prefix in allowed_prefixes)
)
result = {
    "schema_version": "citystate.allowlist_check.v1",
    "base": base,
    "changed_path_count": len(changed),
    "outside_allowlist_count": len(outside),
    "outside_allowlist": outside,
    "passed": not outside,
}
output = repo / "08_os/_runs/run-022-环境能力checker提升与回归/07_测试执行/scope_results.json"
output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, sort_keys=True))
raise SystemExit(0 if result["passed"] else 1)
