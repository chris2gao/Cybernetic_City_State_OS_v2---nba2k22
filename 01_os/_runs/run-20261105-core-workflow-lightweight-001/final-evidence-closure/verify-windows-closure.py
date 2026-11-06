"""Run supplemental checks from the complete, pinned Windows Core checkout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile

import yaml


CANDIDATE = "40d5c71064be9184f4fa543208757ed57b8af69a"
DELIVERY = "88d43d48aa05d5729c1dfd53084648ffd90943e6"
RUN = "01_os/_runs/run-20261105-core-workflow-lightweight-001"
LOOP = "01_os/06_execution/workflow/minimum_operational_loop"
MANAGED = "01_os/06_execution/task_discipline/managed_verification/managed_verify.py"
PYTHON = [sys.executable, "-B", "-X", "utf8"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def files(path):
    return {p.relative_to(path).as_posix(): sha(p.read_bytes())
            for p in path.rglob("*") if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("output", type=Path, help="new directory outside the source checkout")
    args = parser.parse_args()
    repo, output = args.repo.resolve(), args.output.resolve()
    assert os.name == "nt"
    assert not output.is_relative_to(repo)
    assert git(repo, "rev-parse", "HEAD").decode().strip() == CANDIDATE
    assert git(repo, "rev-parse", "--is-shallow-repository").strip() == b"false"
    assert not git(repo, "status", "--porcelain")
    output.mkdir()
    receipt = {"tested_sha": CANDIDATE, "archive_source_sha": DELIVERY, "platform": sys.platform,
               "full_checkout": True, "checks": {}, "windows_cases": {}}

    def check(name, argv, expected=0):
        proc = subprocess.run(argv, cwd=repo, capture_output=True, check=False)
        # Preserve exact output bytes for later screening and replay.
        for label, data in (("stdout", proc.stdout), ("stderr", proc.stderr)):
            (output / f"{name}.{label}.bin").write_bytes(data)
        receipt["checks"][name] = {"argv": argv, "exit_code": proc.returncode,
                                    "expected_exit_code": expected,
                                    "stdout_sha256": sha(proc.stdout), "stderr_sha256": sha(proc.stderr)}
        (output / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        if proc.returncode != expected:
            raise RuntimeError(f"{name}: got {proc.returncode}, expected {expected}")
        return proc.stdout

    with tempfile.TemporaryDirectory(prefix="core-final-windows-") as tmp:
        scratch = Path(tmp).resolve()
        clone = scratch / "core"
        git(repo, "clone", "-q", "--shared", "--no-checkout", str(repo), str(clone))
        git(clone, "checkout", "-qb", "fixture-path-validation", CANDIDATE)
        assert git(clone, "rev-parse", "--is-shallow-repository").strip() == b"false"
        fixture = repo / LOOP / "fixtures/pilot_cross_platform_path_guard"

        def seed(target):
            shutil.copytree(fixture, target)
            manifest_path = target / "manifest.yml"
            manifest = yaml.safe_load(manifest_path.read_bytes())
            manifest["run_id"] = target.name
            manifest["artifacts"] = manifest["artifacts"][:1]
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            entry = manifest["artifacts"][0]
            artifact = target / entry["path"]
            data = yaml.safe_load(artifact.read_bytes())
            data.update(run_id=target.name, status="planned", stage_control={})
            artifact.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

        outside = scratch / "outside"
        metadata = clone / ".git/scratch-probe"
        protected = clone / "01_os/04_skills_and_tools/scratch-probe"
        for target in (outside, metadata, protected):
            seed(target)
        junction = clone / "01_os/_runs/junction-probe"
        from _winapi import CreateJunction
        CreateJunction(str(outside), str(junction))
        assert junction.is_junction() and junction.resolve() == outside

        for name, target, physical, reason in (
            ("junction", junction, outside, "unsafe_candidate_directory"),
            ("outside", outside, outside, "candidate_sync:"),
            ("protected", protected, protected, "candidate_run_root_required"),
            ("git_metadata", metadata, metadata, "unsafe_candidate_directory"),
        ):
            before = files(physical)
            stdout = check(name, [*PYTHON, str(repo / LOOP / "run_minimum_operational_loop.py"),
                                  "sync-candidate", str(target), "--repo-root", str(clone),
                                  "--apply", "--json-output"], 33)
            observed = json.loads(stdout)
            after = files(physical)
            assert reason in observed["findings"][0]
            assert before == after and junction.is_junction() and junction.resolve() == outside
            receipt["windows_cases"][name] = {"reason": observed["findings"][0],
                                               "before": before, "after": after, "no_writes": True}

    evidence_path = f"{RUN}/review-remediation"
    archive_bytes = git(repo, "show", f"{DELIVERY}:{evidence_path}/attempt.zip")
    index = json.loads(git(repo, "show", f"{DELIVERY}:{evidence_path}/attempt-index.json"))
    assert index["candidate"] == CANDIDATE
    assert len(archive_bytes) == index["archive"]["bytes"] and sha(archive_bytes) == index["archive"]["sha256"]
    assert sha((repo / index["plan"]).read_bytes()) == index["plan_sha256"]
    archive_path = output / "source-attempt.zip"
    archive_path.write_bytes(archive_bytes)
    restored = output / "restored-attempt"
    restored.mkdir()
    with ZipFile(archive_path) as archive:
        assert len(archive.namelist()) == len(index["records"]) == 18
        assert set(archive.namelist()) == set(index["records"])
        for name, expected in index["records"].items():
            assert Path(name).name == name
            data = archive.read(name)
            assert len(data) == expected["bytes"] and sha(data) == expected["sha256"]
            (restored / name).write_bytes(data)
    receipt["restoration"] = {"archive_sha256": sha(archive_bytes), "matched_records": len(files(restored)),
                              "source": f"{DELIVERY}:{evidence_path}/attempt.zip",
                              "plan_sha256": index["plan_sha256"]}
    common = ["--repo-root", str(repo), "--candidate", CANDIDATE,
              "--plan", index["plan"], "--attempt", str(restored)]
    inspected = json.loads(check("inspect", [*PYTHON, MANAGED, "inspect", *common]))
    checkpoint = json.loads(check("checkpoint", [*PYTHON, MANAGED, "checkpoint", *common,
                                                   "--change", "Final evidence closure"]))
    assert inspected == json.loads((restored / "result.json").read_bytes())
    assert checkpoint["candidate"] == CANDIDATE and checkpoint["evidence_scope"] == "attempt_internal_consistency"
    assert checkpoint["status"] == "success" and all(test["exit_code"] == 0 for test in checkpoint["tests"])
    assert files(restored) == {name: rec["sha256"] for name, rec in index["records"].items()}

    pytest = [*PYTHON, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
    for name, target, selection in (
        ("draft_integration", f"{LOOP}/test_minimum_operational_loop.py", "candidate_sync"),
        ("ordinary_isolation", "01_os/03_mechanisms/stage_collaborative_deliberation/实现/test_task_scope_readiness.py",
         "ordinary_work"),
        ("formal_gate", "01_os/06_execution/workflow/publication_gate/test_publication_gate.py",
         "missing_final_stage_completion_commit_is_refused or completion_record_is_judged_independently or plan_record_copied_into_the_completion_slot_is_refused"),
    ):
        check(name, [*pytest, "--basetemp", str(output / f"pytest-{name}"), target, "-k", selection])
    assert not git(repo, "status", "--porcelain")
    receipt.update(source_clean_after=True, execution_status="pass", independent_review="pending")
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps({"tests": len(receipt["checks"]), "evidence": str(output), "status": "pass"}))


if __name__ == "__main__":
    main()
