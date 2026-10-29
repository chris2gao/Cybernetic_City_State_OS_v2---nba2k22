import copy
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import GitSource, PRMSError
from catalog import discover_g1, discover_g2, B0_PATHS, compatibility
from context import plan_context, human_choice, assemble_context, verify_recovery

ROOT = Path(__file__).resolve().parents[6]
BASE = "446ca66ad48831f5fcdb1af18f37d07619e048c4"


@pytest.fixture(scope="module")
def src():
    return GitSource(ROOT, BASE, "chris2gao/Cybernetic_City_State_OS_v2---core")


def test_catalog_frozen_baseline_counts_and_proofs(src):
    catalog = discover_g1(src)
    assert catalog["counts"] == {"MECHANISM": 7, "WORKFLOW": 7, "BOOT": 7,
                                 "REGISTRY": 13, "OPTIONAL_TOOL": 3}
    assert catalog["scanned_paths"] + catalog["excluded_paths"] == len(src.tree)
    for entry in catalog["entries"]:
        assert entry["source"]["commit"] == BASE
        assert entry["source"]["blob"] == src.tree[entry["path"]]["blob"]
        assert not entry["body_loaded"] and not entry["action_authorized"]


def test_worktree_edit_cannot_change_frozen_source(src):
    # Prove reads use immutable objects, even if the caller changes source metadata.
    data, proof = src.read("AGENTS.md")
    assert data.startswith(b"# Agent")
    with pytest.raises(PRMSError, match="SUMMARY_STALE"):
        src.read("AGENTS.md", "0" * 40)


@pytest.mark.parametrize("path", ["../AGENTS.md", "/etc/passwd", ".env", ".ssh/id_rsa", "a\\b"])
def test_sensitive_or_escape_paths_rejected(src, path):
    with pytest.raises(PRMSError, match="REJECTED"):
        src.read(path)


def test_optional_rejection_and_mandatory_b0(src):
    cat = discover_g1(src)
    optional = "01_os/03_mechanisms/model_routing/README.md"
    plan = plan_context(src, cat, session_id="s1", role="implementation_owner", task_id="task",
                        optional_paths=[optional])
    choice = human_choice(plan, session_id="s1", selected_paths=[], decision_source="test Human input")
    receipt = assemble_context(src, plan, choice, budget_bytes=1_000_000)
    assert receipt["status"] == "READY"
    loaded = {x["source"]["path"] for x in receipt["full_bodies"]}
    assert set(B0_PATHS) <= loaded and optional not in loaded
    assert receipt["excluded_optional"] == [optional]
    assert verify_recovery(src, receipt, expected_plan=plan, expected_choice=choice)["action_authorized"] is False


def test_budget_blocks_without_silent_truncation(src):
    plan = plan_context(src, discover_g1(src), session_id="s", role="r", task_id="t")
    choice = human_choice(plan, session_id="s", selected_paths=[], decision_source="test")
    receipt = assemble_context(src, plan, choice, budget_bytes=1)
    assert receipt["status"] == "BLOCKED" and receipt["required_not_loaded"]
    assert not receipt["full_bodies"]


def test_cross_session_and_receipt_forgery_rejected(src):
    plan = plan_context(src, discover_g1(src), session_id="s", role="r", task_id="t")
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        human_choice(plan, session_id="other", selected_paths=[], decision_source="test")
    choice = human_choice(plan, session_id="s", selected_paths=[], decision_source="test")
    receipt = assemble_context(src, plan, choice, budget_bytes=1_000_000)
    receipt["full_bodies"][0]["text"] = "forged"
    with pytest.raises(PRMSError, match="REJECTED"):
        verify_recovery(src, receipt, expected_plan=plan, expected_choice=choice)


def test_missing_source_blocks_required_loading(src):
    plan = plan_context(src, discover_g1(src), session_id="s", role="r", task_id="t",
                        required_paths=["01_os/absent.md"])
    choice = human_choice(plan, session_id="s", selected_paths=[], decision_source="test")
    receipt = assemble_context(src, plan, choice, budget_bytes=1_000_000)
    assert receipt["status"] == "BLOCKED"
    assert receipt["missing"] == [{"path": "01_os/absent.md", "status": "SOURCE_MISSING"}]


def test_wrong_domain_rejected(src):
    with pytest.raises(PRMSError):
        discover_g2(src, "nba2k22")


def test_receipt_cannot_remove_task_mandatory_source(src):
    required = "01_os/03_mechanisms/model_routing/README.md"
    plan = plan_context(src, discover_g1(src), session_id="s", role="r", task_id="t", required_paths=[required])
    choice = human_choice(plan, session_id="s", selected_paths=[], decision_source="test Human input")
    receipt = assemble_context(src, plan, choice, budget_bytes=1_000_000)
    receipt["mandatory_paths"].remove(required)
    with pytest.raises(PRMSError, match="REJECTED"):
        verify_recovery(src, receipt, expected_plan=plan, expected_choice=choice)


def test_receipt_cannot_replace_choice_or_directory(src):
    plan = plan_context(src, discover_g1(src), session_id="s", role="r", task_id="t")
    choice = human_choice(plan, session_id="s", selected_paths=[], decision_source="test Human input")
    original = assemble_context(src, plan, choice, budget_bytes=1_000_000)
    receipt = copy.deepcopy(original)
    receipt["human_choice"]["decision_source"] = "substituted claim"
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        verify_recovery(src, receipt, expected_plan=plan, expected_choice=choice)
    receipt = copy.deepcopy(original)
    receipt["directory_cards"].pop()
    with pytest.raises(PRMSError, match="SUMMARY_STALE"):
        verify_recovery(src, receipt, expected_plan=plan, expected_choice=choice)


def test_core_inheritance_difference_and_toctou_commit_drift(src):
    candidate_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    candidate = GitSource(ROOT, candidate_sha, src.repository)
    assert compatibility(src, src)["status"] == "CORE_SOURCE_BLOBS_MATCH"
    difference = compatibility(candidate, src)
    assert difference["status"] == "CORE_VERSION_DIVERGED"
    assert "01_os/02_boot/context_management/启动清单_v1.yml" in difference["different_paths"]
    assert difference["merge_performed"] is False
    plan = plan_context(src, discover_g1(src), session_id="s", role="independent_reviewer", task_id="task")
    choice = human_choice(plan, session_id="s", selected_paths=[], decision_source="fixture")
    with pytest.raises(PRMSError, match="SUMMARY_STALE"):
        assemble_context(candidate, plan, choice, budget_bytes=1_000_000)


def test_reviewer_default_does_not_load_executor_narrative_or_rea_body(src):
    narrative = "01_os/_runs/executor-report.md"
    rea = "08_Domain_Applications/research/rea.md"
    plan = plan_context(src, discover_g1(src), session_id="review", role="independent_reviewer",
                        task_id="task", optional_paths=[narrative, rea])
    choice = human_choice(plan, session_id="review", selected_paths=[], decision_source="fixture independent review")
    receipt = assemble_context(src, plan, choice, budget_bytes=1_000_000)
    assert receipt["status"] == "READY"
    assert set(receipt["excluded_optional"]) == {narrative, rea}
    assert not any(x["source"]["path"] in (narrative, rea) for x in receipt["full_bodies"])
    assert not receipt["action_authorized"]
