from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


REPO = Path(__file__).resolve().parents[4]
RUN = REPO / "08_os/_runs/run-023-通讯机制需求建模"
BASE = "11b6bb2ba8064a1368067e6c9924b506249d8dcc"
MASTER = "a66ee671e47f3a90f3a108eb7531c7c84b0f9d37"
V1_SHA = "cfff1e32928db0c8aeb860260b8ed9c34e32994ab1b137e015dcafe5eac0f4a7"
V1_CONFIRM_SHA = "43ad434934e3193bb74f4457856f394569c37aaca0ec36c99327b148e0bfd89e"
V2_SHA = "2b6f8df7c72f43876d639c6ca9cc1b4e9d5091f97918d82e7c78690cd6c363f7"
V1 = RUN / "01_需求建模/A_通讯机制需求建模_v1.yml"
V2 = RUN / "01_需求建模/A_通讯机制需求建模_v2.yml"
CONFIRM_V1 = RUN / "01_需求建模/Human确认_v1.yml"
CONFIRM_V2 = RUN / "01_需求建模/Human确认_v2.yml"
MANIFEST = RUN / "07_测试执行/A_v1_to_v2_变更清单.yml"
MODEL_RESULTS = RUN / "07_测试执行/results.json"
OUTPUT = RUN / "07_测试执行/scope_revision_results.json"
EXPECTED_SLOTS = {"目标", "成功判据", "边界", "约束", "术语", "关联领域", "假设", "未解歧义"}
ALLOWED_EXACT = {
    "08_os/_runs/run-023-通讯机制需求建模/01_需求建模/A_通讯机制需求建模_v2.yml",
    "08_os/_runs/run-023-通讯机制需求建模/01_需求建模/Human确认_v2.yml",
    "08_os/_runs/run-023-通讯机制需求建模/run.yml",
}
ALLOWED_PREFIX = "08_os/_runs/run-023-通讯机制需求建模/07_测试执行/"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: YAML root must be a mapping")
    return value


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=REPO, text=True, encoding="utf-8", errors="strict",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def semantic_changes(v1: dict[str, Any], v2: dict[str, Any]) -> dict[str, dict[str, Any]]:
    changes: dict[str, dict[str, Any]] = {}
    for slot in EXPECTED_SLOTS - {"约束", "未解歧义"}:
        if v1[slot] != v2[slot]:
            raise ValueError(f"unauthorized semantic change outside constraints/ambiguities: {slot}")

    old_constraints = v1["约束"]
    new_constraints = v2["约束"]
    if new_constraints[: len(old_constraints)] != old_constraints:
        raise ValueError("existing constraints changed or reordered")
    for index in range(len(old_constraints), len(new_constraints)):
        changes[f"约束[{index}]"] = {"operation": "add", "old": None, "new": new_constraints[index]}

    old_ambiguities = v1["未解歧义"]
    new_ambiguities = v2["未解歧义"]
    if len(old_ambiguities) != len(new_ambiguities):
        raise ValueError("ambiguity count changed")
    for index, (old, new) in enumerate(zip(old_ambiguities, new_ambiguities, strict=True)):
        if set(old) != set(new):
            raise ValueError(f"ambiguity field shape changed: {index}")
        for field in old:
            if old[field] != new[field]:
                changes[f"未解歧义[{index}].{field}"] = {
                    "operation": "replace", "old": old[field], "new": new[field]
                }
    return changes


def changed_paths() -> list[str]:
    tracked = {line for line in run("git", "-c", "core.quotepath=false", "diff", "--name-only", BASE, "--").stdout.splitlines() if line}
    untracked = {line for line in run("git", "-c", "core.quotepath=false", "ls-files", "--others", "--exclude-standard").stdout.splitlines() if line}
    return sorted(tracked | untracked)


def validate() -> dict[str, Any]:
    tests: list[dict[str, Any]] = []

    def record(test_id: str, passed: bool, detail: str) -> None:
        tests.append({"test_id": test_id, "passed": bool(passed), "detail": detail})

    v1 = load_yaml(V1)
    v2 = load_yaml(V2)
    confirmation = load_yaml(CONFIRM_V2)
    manifest = load_yaml(MANIFEST)
    run_meta = load_yaml(RUN / "run.yml")

    record("v1_candidate_bytes_unchanged", digest(V1) == V1_SHA, digest(V1))
    record("v1_confirmation_bytes_unchanged", digest(CONFIRM_V1) == V1_CONFIRM_SHA, digest(CONFIRM_V1))
    record("v2_digest_bound", digest(V2) == V2_SHA == manifest.get("v2", {}).get("sha256"), digest(V2))
    record("exact_eight_slots", set(v2) == EXPECTED_SLOTS, "v2 uses schema v1 top-level slots")

    actual_changes = semantic_changes(v1, v2)
    listed_changes = manifest.get("semantic_changes")
    listed_by_path = {
        item["path"]: {"operation": item["operation"], "old": item.get("old"), "new": item.get("new")}
        for item in listed_changes
    } if isinstance(listed_changes, list) else {}
    bases_present = isinstance(listed_changes, list) and all(bool(str(item.get("basis", "")).strip()) for item in listed_changes)
    record("semantic_diff_fully_enumerated", actual_changes == listed_by_path and bases_present, f"changes={len(actual_changes)}")
    record("no_stage3_ambiguity_blocker", all("03_结果建模" not in item["阻塞范围"] for item in v2["未解歧义"]), "all eight blocker scopes exclude stage 3")

    constraints_text = "\n".join(v2["约束"])
    required_constraint_fragments = [
        "Human 在本机操作的 shell 与其 git 凭据",
        "CITYSTATE_ALLOW_MASTER=1",
        "只计为防误操作机制，不构成 action-bound authorization",
        "宿主注入、绑定具体动作与事件，并一次性原子消费",
        "已 push 到远端的 commit 一律不得丢失",
        "未提交工作区内容允许丢失",
        "在途任务必须可从耐久证据恢复并续跑",
        "最终载体由 P5 release design 与 Human gate 决定",
    ]
    record("human_rulings_promoted_to_constraints", all(fragment in constraints_text for fragment in required_constraint_fragments), "rulings 1-3 and attached treatment are constraints")

    # 两态契约。与 validate_requirement_model.py 的 human_gate_two_state 保持同一语义：
    # 只承认"未签"会让 Human 真的确认之后本 run 校验转红——一个正常流程走完必然说谎的测试。
    # 该修复此前已在 validate_requirement_model.py 落地，但当时只改了单个脚本，
    # 未提升为工作流层规则，因此在本新脚本中复发。canonical 落点是 P3 的 transition graph。
    DECISION_KEYS = {"decision", "confirmed_by", "confirmed_at", "statement"}
    SIGNED_TEXT_KEYS = ("confirmed_by", "confirmed_at", "statement")
    decision = confirmation.get("human_decision")
    status = confirmation.get("status")
    keys_exact = isinstance(decision, dict) and set(decision) == DECISION_KEYS

    def _nonempty(value: object) -> bool:
        return isinstance(value, str) and bool(value.strip())

    unsigned = (
        status == "awaiting_human_confirmation"
        and keys_exact
        and all(value is None for value in decision.values())
    )
    confirmed = (
        status == "human_confirmed"
        and keys_exact
        and decision.get("decision") in {"confirmed", "revision_required"}
        and all(_nonempty(decision.get(key)) for key in SIGNED_TEXT_KEYS)
    )
    candidate = confirmation.get("candidate", {})
    bound = candidate == {
        "path": "08_os/_runs/run-023-通讯机制需求建模/01_需求建模/A_通讯机制需求建模_v2.yml",
        "version": 2,
        "sha256": V2_SHA,
    }
    record(
        "human_gate_two_state",
        unsigned or confirmed,
        "confirmation is fully unsigned (awaiting_human_confirmation) or fully signed "
        "(human_confirmed); partial states fail",
    )
    record(
        "human_gate_state_reported",
        status in {"awaiting_human_confirmation", "human_confirmed"},
        f"confirmation status is a declared state: {status}",
    )
    record("human_confirmation_v2_bound", bound, "path/version/sha256 match v2")

    model_result = json.loads(MODEL_RESULTS.read_text(encoding="utf-8"))
    record("reused_schema_validator_15_pass", model_result.get("all_passed") is True and model_result.get("test_count") == 15 and model_result.get("candidate_sha256") == V2_SHA, "validate_requirement_model.py points to v2")
    independent_result = json.loads((RUN / "07_测试执行/independent_scope_revision_results.json").read_text(encoding="utf-8-sig"))
    record(
        "independent_postchange_measurement_pass",
        independent_result.get("result") == "pass"
        and "does not import either task validator" in independent_result.get("measurement_tool", ""),
        "PowerShell measurement is structurally independent from task validators",
    )

    active = run_meta.get("active_candidate", {})
    record("run_metadata_points_to_v2", active.get("sha256") == V2_SHA and active.get("human_confirmation") == "awaiting_human_confirmation" and active.get("stage_3_entry") == "prohibited_until_human_confirmed", "run metadata preserves Human gate")

    personal = run(
        sys.executable,
        "08_os/06_execution/validators/personal_paths/validate.py",
        "--repo-root", ".", "--mode", "changed", "--base", MASTER, "--summary-only",
    )
    personal_summary = json.loads(personal.stdout) if personal.stdout.strip() else {}
    record("personal_paths_changed_from_measured_master", personal.returncode == 0 and personal_summary.get("hit_count") == 0, f"candidate_files={personal_summary.get('candidate_files')}")

    diff_check = run("git", "-c", "core.quotepath=false", "diff", "--check", BASE, "--")
    record(
        "git_diff_check",
        diff_check.returncode == 0,
        "clean" if diff_check.returncode == 0 else diff_check.stderr.strip(),
    )

    paths = changed_paths()
    out_of_scope = [path for path in paths if path not in ALLOWED_EXACT and not path.startswith(ALLOWED_PREFIX)]
    record("exact_allowlist", bool(paths) and not out_of_scope, f"changed={len(paths)}, out_of_scope={len(out_of_scope)}")
    record("no_stage3_or_protocol_implementation", not any("/03_结果建模/" in path or path.startswith(".ai/") for path in paths), "no forbidden implementation paths")

    all_passed = all(item["passed"] for item in tests)
    return {
        "schema_version": "communication_requirement_scope_revision_validation.v1",
        "task_id": "os-v2-communication-requirement-model-scope-revision-001",
        "base": BASE,
        "measured_master": MASTER,
        "v1_sha256": digest(V1),
        "v1_confirmation_sha256": digest(CONFIRM_V1),
        "v2_sha256": digest(V2),
        "semantic_change_count": len(actual_changes),
        "stage3_blocker_count": sum("03_结果建模" in item["阻塞范围"] for item in v2["未解歧义"]),
        "changed_paths": paths,
        "out_of_scope_paths": out_of_scope,
        "test_count": len(tests),
        "tests": tests,
        "all_passed": all_passed,
    }


def main() -> int:
    try:
        result = validate()
        code = 0 if result["all_passed"] else 1
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError, json.JSONDecodeError) as exc:
        result = {"schema_version": "communication_requirement_scope_revision_validation.v1", "all_passed": False, "error": str(exc)}
        code = 1
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"test_count": result.get("test_count"), "all_passed": result.get("all_passed"), "error": result.get("error")}, ensure_ascii=False, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
