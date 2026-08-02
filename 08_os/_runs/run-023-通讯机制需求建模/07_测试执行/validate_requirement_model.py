from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


repo = Path(__file__).resolve().parents[4]
run_root = repo / "08_os/_runs/run-023-通讯机制需求建模"
model_path = run_root / "01_需求建模/A_通讯机制需求建模_v2.yml"
confirmation_path = run_root / "01_需求建模/Human确认_v2.yml"
schema_path = repo / "08_os/01_workflow/01_需求建模/实现/需求建模schema_v1.md"
result_path = run_root / "07_测试执行/results.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def exact_mapping_list(value: Any, keys: set[str], allow_empty: bool = True) -> bool:
    if not isinstance(value, list) or (not allow_empty and not value):
        return False
    return all(isinstance(item, dict) and set(item) == keys for item in value)


model = yaml.safe_load(model_path.read_text(encoding="utf-8"))
confirmation = yaml.safe_load(confirmation_path.read_text(encoding="utf-8"))
expected_slots = {"目标", "成功判据", "边界", "约束", "术语", "关联领域", "假设", "未解歧义"}
tests: list[dict[str, Any]] = []


def record(test_id: str, passed: bool, detail: str) -> None:
    tests.append({"test_id": test_id, "passed": passed, "detail": detail})


record("exact_eight_slots", isinstance(model, dict) and set(model) == expected_slots, "top-level keys equal schema v1")
record("goal_nonempty", isinstance(model, dict) and nonempty_string(model.get("目标")), "目标 is a non-empty string")

criteria = model.get("成功判据") if isinstance(model, dict) else None
criteria_shape = exact_mapping_list(criteria, {"描述", "可观察"}, allow_empty=False)
record("success_criteria_shape", criteria_shape, "each criterion has 描述 and 可观察")
record(
    "success_criteria_observable",
    bool(criteria_shape) and all(nonempty_string(item["描述"]) and item["可观察"] is True for item in criteria),
    "all criteria are non-empty and observable",
)

boundaries = model.get("边界") if isinstance(model, dict) else None
constraints = model.get("约束") if isinstance(model, dict) else None
record(
    "boundaries_nonempty",
    isinstance(boundaries, list) and bool(boundaries) and all(nonempty_string(item) for item in boundaries),
    "边界 is a non-empty string array",
)
record(
    "constraints_shape",
    isinstance(constraints, list) and all(nonempty_string(item) for item in constraints),
    "约束 is a string array",
)

terms = model.get("术语") if isinstance(model, dict) else None
terms_shape = exact_mapping_list(terms, {"词", "含义", "别名"})
record(
    "terms_shape",
    bool(terms_shape) and all(
        nonempty_string(item["词"])
        and nonempty_string(item["含义"])
        and isinstance(item["别名"], list)
        and all(nonempty_string(alias) for alias in item["别名"])
        for item in terms
    ),
    "术语 items match schema v1",
)

domains = model.get("关联领域") if isinstance(model, dict) else None
record(
    "related_domains_shape",
    bool(exact_mapping_list(domains, {"领域", "为什么相关"}, allow_empty=False))
    and all(nonempty_string(item["领域"]) and nonempty_string(item["为什么相关"]) for item in domains),
    "关联领域 is directly consumable by stage 2",
)

assumptions = model.get("假设") if isinstance(model, dict) else None
record(
    "assumptions_shape",
    bool(exact_mapping_list(assumptions, {"假设", "如果不成立会怎样"}))
    and all(nonempty_string(item["假设"]) and nonempty_string(item["如果不成立会怎样"]) for item in assumptions),
    "every assumption has a failure consequence",
)

ambiguities = model.get("未解歧义") if isinstance(model, dict) else None
ambiguities_shape = exact_mapping_list(ambiguities, {"歧义", "为何未解", "影响", "阻塞范围"})
record(
    "ambiguities_shape",
    bool(ambiguities_shape) and all(
        nonempty_string(item["歧义"])
        and nonempty_string(item["为何未解"])
        and item["影响"] in {"高", "中", "低"}
        and isinstance(item["阻塞范围"], list)
        and all(nonempty_string(stage) for stage in item["阻塞范围"])
        for item in ambiguities
    ),
    "未解歧义 records impact and scoped blocking",
)

target_terms = {
    "全部 core 窗口",
    "provider-neutral",
    "单一通讯权威",
    "通讯 canonical",
    "任务闭环",
    "可审计",
    "可验证",
    "兼容观察期",
    "真实 rollback",
    "分层权威",
    "Token/资源 canonical",
    "workflow canonical",
    "新 OS 默认活动系统宣告门",
}
defined_terms = {item["词"] for item in terms} if isinstance(terms, list) else set()
goal = model.get("目标", "") if isinstance(model, dict) else ""
record(
    "goal_keywords_defined",
    all(keyword in goal and keyword in defined_terms for keyword in target_terms),
    "all configured goal keywords appear in 术语",
)

criteria_text = "\n".join(item["描述"] for item in criteria) if isinstance(criteria, list) else ""
required_tags = [f"[R{index}]" for index in range(1, 12)]
record(
    "v2_eleven_requirements_covered",
    all(criteria_text.count(tag) == 1 for tag in required_tags),
    "v2 section 3.2 R1-R11 each map to one observable criterion",
)

expected_candidate_path = "08_os/_runs/run-023-通讯机制需求建模/01_需求建模/A_通讯机制需求建模_v2.yml"
candidate = confirmation.get("candidate") if isinstance(confirmation, dict) else None
decision = confirmation.get("human_decision") if isinstance(confirmation, dict) else None
record(
    "candidate_digest_bound",
    isinstance(candidate, dict)
    and candidate.get("path") == expected_candidate_path
    and candidate.get("version") == 2
    and candidate.get("sha256") == digest(model_path),
    "confirmation template binds candidate path, version, and SHA-256",
)
DECISION_KEYS = {"decision", "confirmed_by", "confirmed_at", "statement"}
SIGNED_TEXT_KEYS = ("confirmed_by", "confirmed_at", "statement")
status = confirmation.get("status") if isinstance(confirmation, dict) else None
keys_exact = isinstance(decision, dict) and set(decision) == DECISION_KEYS

# 两态契约。原先只承认"未签"一种通过状态，Human 一旦真的确认，本 run 的校验就会转红——
# 一个在正常流程里必然说谎的测试。改为：要么四字段全空且状态为等待，要么四字段全填且
# 状态为已确认。中间态一律失败，因此"执行方半签"仍然被拦。
unsigned_state = (
    status == "awaiting_human_confirmation"
    and keys_exact
    and all(value is None for value in decision.values())
)
confirmed_state = (
    status == "human_confirmed"
    and keys_exact
    and decision.get("decision") in {"confirmed", "revision_required"}
    and all(nonempty_string(decision.get(key)) for key in SIGNED_TEXT_KEYS)
)
record(
    "human_gate_two_state",
    unsigned_state or confirmed_state,
    "confirmation is either fully unsigned (awaiting_human_confirmation) "
    "or fully signed (human_confirmed); partial states fail",
)
record(
    "human_gate_state_reported",
    status in {"awaiting_human_confirmation", "human_confirmed"},
    f"confirmation status is a declared state: {status}",
)

all_passed = all(item["passed"] for item in tests)
result = {
    "schema_version": "communication_requirement_model_validation.v1",
    "base": "11b6bb2ba8064a1368067e6c9924b506249d8dcc",
    "schema_ref": "08_os/01_workflow/01_需求建模/实现/需求建模schema_v1.md",
    "schema_sha256": digest(schema_path),
    "candidate_sha256": digest(model_path),
    "test_count": len(tests),
    "tests": tests,
    "all_passed": all_passed,
}
result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"test_count": len(tests), "all_passed": all_passed}, sort_keys=True))
raise SystemExit(0 if all_passed else 1)
