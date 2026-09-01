#!/usr/bin/env python3
"""Tests for the working-set and archive tooling.

The archive and reference-safety tests run against a real temporary Git
repository rather than a mocked one, for the same reason the path-ledger tests
do: the behaviour under test is Git's, and a mock would only prove that the mock
agrees with the assumption being tested.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import archive_group  # noqa: E402
import lifecycle  # noqa: E402
import reference_safety  # noqa: E402
import validate_working_set  # noqa: E402
import visible_set as working_set  # noqa: E402
from lifecycle import OPEN, TERMINAL, UNKNOWN, WorkingSetError  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[5]


# --------------------------------------------------------------------------
# lifecycle classification
# --------------------------------------------------------------------------


@pytest.mark.parametrize("state", sorted(lifecycle.TERMINAL_STATES))
def test_declared_terminal_states_classify_terminal(state):
    assert lifecycle.classify(state) == TERMINAL


@pytest.mark.parametrize("state", sorted(lifecycle.OPEN_STATES))
def test_declared_open_states_classify_open(state):
    assert lifecycle.classify(state) == OPEN


@pytest.mark.parametrize(
    "state",
    [
        None,
        "",
        "   ",
        # Real free-text values observed on d9a18b57. None of them may be
        # silently promoted to a terminal state.
        "complete_awaiting_Human_fast_forward_authorization",
        "IMPLEMENTATION_AUTHORIZED_NO_MASTER_PUBLICATION",
        "architecture_v3_fresh_independent_rereview_dispatched",
        "COMPLETE_MASTER_PUBLISHED",
        "integrated_and_verified",  # near-miss on a real enum value
    ],
)
def test_freeform_and_missing_states_are_unknown(state):
    assert lifecycle.classify(state) == UNKNOWN


def test_open_and_terminal_sets_are_disjoint():
    assert not (lifecycle.OPEN_STATES & lifecycle.TERMINAL_STATES)


# --------------------------------------------------------------------------
# group state reading
# --------------------------------------------------------------------------


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_missing_state_file_is_unknown_not_an_error(tmp_path):
    group = tmp_path / "run-x"
    group.mkdir()
    state = lifecycle.read_group_state(group)
    assert state.classification == UNKNOWN
    assert state.state_raw is None


def test_state_written_under_status_key_is_not_read_as_lifecycle(tmp_path):
    group = tmp_path / "run-x"
    _write(group / "run.yml", "status: verified_on_demand\n")
    assert lifecycle.read_group_state(group).classification == UNKNOWN


def test_closure_record_outside_group_is_rejected(tmp_path):
    group = tmp_path / "run-x"
    _write(group / "run.yml", "lifecycle: excluded\nclosure_record: ../escape.yml\n")
    with pytest.raises(WorkingSetError, match="closure_record_outside_group"):
        lifecycle.read_group_state(group)


def test_closure_record_must_be_declared(tmp_path):
    group = tmp_path / "run-x"
    _write(group / "run.yml", "lifecycle: excluded\n")
    state = lifecycle.read_group_state(group)
    with pytest.raises(WorkingSetError, match="closure_record_not_declared"):
        lifecycle.validate_closure_record(state)


def test_closure_record_must_exist_on_disk(tmp_path):
    group = tmp_path / "run-x"
    _write(group / "run.yml", "lifecycle: excluded\nclosure_record: 08/p.yml\n")
    state = lifecycle.read_group_state(group)
    with pytest.raises(WorkingSetError, match="closure_record_unreadable"):
        lifecycle.validate_closure_record(state)


def test_closure_record_must_carry_a_closure_key(tmp_path):
    group = tmp_path / "run-x"
    _write(group / "run.yml", "lifecycle: excluded\nclosure_record: 08/p.yml\n")
    _write(group / "08" / "p.yml", "note: nothing closing here\n")
    state = lifecycle.read_group_state(group)
    with pytest.raises(WorkingSetError, match="closure_record_has_no_closure_key"):
        lifecycle.validate_closure_record(state)


def test_valid_closure_record_returns_the_ref(tmp_path):
    group = tmp_path / "run-x"
    _write(group / "run.yml", "lifecycle: excluded\nclosure_record: 08/p.yml\n")
    _write(group / "08" / "p.yml", "completion_pointer:\n  status: integrated\n")
    state = lifecycle.read_group_state(group)
    assert lifecycle.validate_closure_record(state) == "08/p.yml"


# --------------------------------------------------------------------------
# real temporary Git repository
# --------------------------------------------------------------------------


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@pytest.fixture()
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@example.invalid")
    _git(root, "config", "user.name", "t")
    _git(root, "config", "core.quotepath", "false")
    return root


def _make_group(repo: Path, gid: str, *, state: str, closure: bool = True) -> Path:
    group = repo / "01_os" / "_runs" / gid
    body = f"lifecycle: {state}\n"
    if closure:
        body += "closure_record: 08_结论/pointer.yml\n"
        _write(group / "08_结论" / "pointer.yml",
               "completion_pointer:\n  status: integrated\n")
    _write(group / "run.yml", body)
    return group


def _commit_all(repo: Path, message: str = "c") -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)


def test_archive_moves_a_clean_terminal_group(repo):
    _make_group(repo, "run-a", state="excluded")
    _commit_all(repo)
    result = archive_group.archive_group(repo, "01_os/_runs/run-a")
    assert result["moved"] is True
    assert result["secure_erasure_claim"] is False
    assert not (repo / "01_os/_runs/run-a").exists()
    assert (repo / "01_os/_runs/_archive/run-a/run.yml").is_file()


def test_archive_is_idempotent(repo):
    _make_group(repo, "run-a", state="deferred")
    _commit_all(repo)
    archive_group.archive_group(repo, "01_os/_runs/run-a")
    again = archive_group.archive_group(repo, "01_os/_runs/run-a")
    assert again["already_archived"] is True
    assert again["moved"] is False


def test_archive_refuses_a_non_terminal_group(repo):
    _make_group(repo, "run-b", state="candidate_pending_validation")
    _commit_all(repo)
    with pytest.raises(WorkingSetError, match="group_state_not_terminal"):
        archive_group.archive_group(repo, "01_os/_runs/run-b")
    assert (repo / "01_os/_runs/run-b").is_dir()


def test_archive_refuses_a_freeform_state(repo):
    _make_group(repo, "run-c", state="COMPLETE_MASTER_PUBLISHED")
    _commit_all(repo)
    with pytest.raises(WorkingSetError, match="group_state_not_terminal"):
        archive_group.archive_group(repo, "01_os/_runs/run-c")


def test_archive_refuses_when_a_live_reference_exists(repo):
    _make_group(repo, "run-d", state="excluded")
    _write(repo / "01_os" / "05_registry" / "r.yml",
           "evidence: 01_os/_runs/run-d/08_结论/pointer.yml\n")
    _commit_all(repo)
    with pytest.raises(WorkingSetError, match="live_references_block_archive"):
        archive_group.archive_group(repo, "01_os/_runs/run-d")
    assert (repo / "01_os/_runs/run-d").is_dir()


def test_archive_refuses_tracked_private_runtime(repo):
    group = _make_group(repo, "run-e", state="excluded")
    _write(group / "_runtime" / "scratch.txt", "x\n")
    _commit_all(repo)
    with pytest.raises(WorkingSetError, match="tracked_private_runtime_inside_group"):
        archive_group.archive_group(repo, "01_os/_runs/run-e")


def test_archive_rejects_a_path_escaping_the_repository(repo):
    with pytest.raises(WorkingSetError, match="group_path_invalid"):
        archive_group.archive_group(repo, "../outside")


def test_reference_scan_ignores_matches_inside_the_group(repo):
    group = _make_group(repo, "run-f", state="excluded")
    _write(group / "self.md", "see 01_os/_runs/run-f/run.yml\n")
    _commit_all(repo)
    found = reference_safety.find_live_references(repo, "01_os/_runs/run-f")
    assert found == []


def test_reference_scan_reports_exact_referencing_paths(repo):
    _make_group(repo, "run-g", state="excluded")
    _write(repo / "docs" / "a.md", "01_os/_runs/run-g\n")
    _write(repo / "docs" / "b.md", "01_os/_runs/run-g/run.yml\n")
    _commit_all(repo)
    result = reference_safety.scan(repo, "01_os/_runs/run-g")
    assert result["reference_safe"] is False
    assert result["referencing_paths"] == ["docs/a.md", "docs/b.md"]


# --------------------------------------------------------------------------
# working set partition and reporting
# --------------------------------------------------------------------------


def test_open_and_unknown_visible_terminal_hidden(repo):
    """Hiding requires proof of completion, not absence of proof of life.

    An earlier revision hid UNKNOWN alongside TERMINAL. That is what independent
    review T3-IR-001 rejected: it hid exactly the groups whose state the tree
    cannot vouch for, and took most of the reported benefit from doing so.
    """
    _make_group(repo, "run-open", state="candidate_pending_validation")
    _make_group(repo, "run-done", state="excluded")
    _make_group(repo, "run-freeform", state="COMPLETE_MASTER_PUBLISHED")
    unknown = repo / "01_os" / "_runs" / "run-unknown"
    _write(unknown / "notes.md", "no run.yml here\n")
    _write(repo / "01_os" / "03_mechanisms" / "m.yml", "a: 1\n")
    _commit_all(repo)

    paths = reference_safety.tracked_paths(repo)
    groups = working_set.collect_groups(repo, paths)
    split = working_set.partition(repo, paths, groups)

    assert "01_os/03_mechanisms/m.yml" in split["visible"]
    assert any(p.startswith("01_os/_runs/run-open/") for p in split["visible"])
    # Unknown, by either route — no run.yml at all, or a freeform status string.
    assert any(p.startswith("01_os/_runs/run-unknown/") for p in split["visible"])
    assert any(p.startswith("01_os/_runs/run-freeform/") for p in split["visible"])
    # Only the positively classified terminal group is hidden.
    assert not any(p.startswith("01_os/_runs/run-done/") for p in split["visible"])
    assert any(p.startswith("01_os/_runs/run-done/") for p in split["hidden"])


def test_unknown_group_is_visible_and_still_not_archivable(repo):
    """The focused fixture for T3-IR-001: visible and archivable are separate."""
    _make_group(repo, "run-unknown-state", state="architecture_root_cause_active")
    _commit_all(repo)

    paths = reference_safety.tracked_paths(repo)
    groups = working_set.collect_groups(repo, paths)
    split = working_set.partition(repo, paths, groups)

    state = groups["01_os/_runs/run-unknown-state"]
    assert state.classification == UNKNOWN
    assert any(p.startswith("01_os/_runs/run-unknown-state/") for p in split["visible"])

    with pytest.raises(WorkingSetError, match="group_state_not_terminal"):
        archive_group.archive_group(repo, "01_os/_runs/run-unknown-state")
    assert (repo / "01_os/_runs/run-unknown-state").is_dir()


def test_index_puts_unknown_in_visible_and_reports_it_separately(repo):
    _make_group(repo, "run-open", state="research_only")
    _make_group(repo, "run-done", state="verified_on_demand")
    _make_group(repo, "run-unclear", state="whatever_string")
    _commit_all(repo)

    index = working_set.build_index(repo, head="0" * 40)
    assert "01_os/_runs/run-unclear" in index["visible_groups"]
    assert "01_os/_runs/run-open" in index["visible_groups"]
    assert index["hidden_groups"] == ["01_os/_runs/run-done"]
    assert "01_os/_runs/run-unclear" in index["unknown_state_groups"]
    assert index["unknown_state_groups_default_visible"] is True
    assert index["unknown_state_groups_archivable"] is False


def test_default_classification_sets_are_the_corrected_policy():
    assert working_set.DEFAULT_VISIBLE_CLASSIFICATIONS == {OPEN, UNKNOWN}
    assert working_set.DEFAULT_HIDDEN_CLASSIFICATIONS == {TERMINAL}


def test_report_always_states_what_it_excluded(repo):
    _make_group(repo, "run-done", state="excluded")
    _write(repo / "01_os" / "03_mechanisms" / "m.yml", "a: 1\n")
    _commit_all(repo)
    report = working_set.build_report(repo)
    assert report["hidden_files"] > 0
    assert report["excluded_listing_bytes"] > 0
    assert report["filtered_result_is_not_exhaustive"] is True
    assert report["visible_listing_bytes"] < report["full_listing_bytes"]


def test_index_is_not_authority(repo):
    _write(repo / "01_os" / "03_mechanisms" / "m.yml", "a: 1\n")
    _commit_all(repo)
    index = working_set.build_index(repo, head="0" * 40)
    assert index["index_is_not_authority"] is True
    assert index["authority_is_physical_tree"] is True


def test_cli_list_reports_hidden_count_on_stderr(repo):
    _make_group(repo, "run-done", state="excluded")
    _write(repo / "01_os" / "03_mechanisms" / "m.yml", "a: 1\n")
    _commit_all(repo)
    script = Path(working_set.__file__)
    proc = subprocess.run(
        [sys.executable, "-B", str(script), "--repository-root", str(repo), "--list"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert proc.returncode == 0
    assert "hidden" in proc.stderr
    assert "--include-hidden" in proc.stderr


# --------------------------------------------------------------------------
# contract drift guard
# --------------------------------------------------------------------------


def test_repository_contract_validates_clean():
    assert validate_working_set.validate(REPO_ROOT) == []


def test_contract_drift_is_detected(tmp_path):
    source = REPO_ROOT / validate_working_set.CONTRACT
    fake = tmp_path / validate_working_set.CONTRACT
    fake.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8").replace(
        "    - excluded\n", "", 1
    )
    fake.write_text(text, encoding="utf-8")
    findings = validate_working_set.validate(tmp_path)
    assert any(f.startswith("terminal_state_drift") for f in findings)


def test_contract_flipping_unknown_back_to_hidden_is_rejected(tmp_path):
    """The regression guard for T3-IR-001.

    The rejected policy is internally consistent and produces a much larger
    headline number, so nothing else in the suite would catch its return.
    """
    source = REPO_ROOT / validate_working_set.CONTRACT
    fake = tmp_path / validate_working_set.CONTRACT
    fake.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8").replace(
        "unknown_group_default_visible: true",
        "unknown_group_default_visible: false",
        1,
    )
    fake.write_text(text, encoding="utf-8")
    findings = validate_working_set.validate(tmp_path)
    assert any(
        f.startswith("visibility_policy_drift:unknown_group_default_visible")
        for f in findings
    )


def test_contract_marking_unknown_archivable_is_rejected(tmp_path):
    source = REPO_ROOT / validate_working_set.CONTRACT
    fake = tmp_path / validate_working_set.CONTRACT
    fake.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8").replace(
        "unknown_group_archivable: false",
        "unknown_group_archivable: true",
        1,
    )
    fake.write_text(text, encoding="utf-8")
    findings = validate_working_set.validate(tmp_path)
    assert any(
        f.startswith("visibility_policy_drift:unknown_group_archivable")
        for f in findings
    )


def test_missing_contract_is_reported_not_crashed(tmp_path):
    assert validate_working_set.validate(tmp_path) == [
        f"contract_missing:{validate_working_set.CONTRACT}"
    ]
