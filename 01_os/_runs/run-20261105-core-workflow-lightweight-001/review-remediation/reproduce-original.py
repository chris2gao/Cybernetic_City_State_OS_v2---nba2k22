import importlib.util
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import yaml

path = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("runner", path)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
fixture = path.parent / "fixtures/pilot_cross_platform_path_guard"

def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args]).decode().strip()

def save(path, data):
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")

assert git(Path.cwd(), "hash-object", str(path)) == git(Path.cwd(), "rev-parse", f"be6774e3:{path.relative_to(Path.cwd()).as_posix()}")
with tempfile.TemporaryDirectory() as scratch:
    repo = Path(scratch).resolve()
    git(repo, "init", "-qb", "fixture")
    for case, rel in (("git_metadata", ".git/scratch-probe"), ("unauthorized", "unlisted"),
                      ("published", "published"), ("dual_rollback", "rollback")):
        run = repo / rel
        shutil.copytree(fixture, run)
        manifest = runner.load_yaml(run / "manifest.yml")
        entry = manifest["artifacts"][0]
        manifest["artifacts"] = [entry]
        artifact_path = run / entry["path"]
        art = runner.load_yaml(artifact_path)
        art["stage_control"] = {}
        if case == "published":
            art["status"] = "published"
        if case == "dual_rollback":
            art["artifact_version"] = entry["artifact_version"] = 3
            save(artifact_path, art)
            save(run / "manifest.yml", manifest)
            git(repo, "add", f"{rel}/manifest.yml", f"{rel}/{entry['path']}")
            git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "v3")
            art["artifact_version"] = entry["artifact_version"] = 1
        save(artifact_path, art)
        save(run / "manifest.yml", manifest)
        code, changes = runner.sync_candidate(run, repo, apply=True)
        print(json.dumps({"case": case, "exit": code, "changes": len(changes)}))
