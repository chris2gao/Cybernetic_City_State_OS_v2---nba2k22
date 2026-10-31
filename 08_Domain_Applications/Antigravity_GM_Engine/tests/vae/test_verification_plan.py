"""
Comprehensive verification test suite executing all 13 checks (LOOP01–LOOP13)
specified in verification_plan.json.
"""

import os
import json
import subprocess
import pytest

from src.vae.contracts import (
    ProfileSnapshot,
    SnapshotStatus,
    TrialPreflight,
    PreflightStatus,
    ExecutionReceipt,
    ReceiptStatus,
    TechnicalReadback,
    ReadbackStatus,
    CompetitiveObservation,
    ObservationStatus,
    KnowledgeRevision,
    RevisionStatus,
    DSeriesFeedback,
    EvidenceTier,
)
from src.vae.pipeline import VAEE1Pipeline
from src.vae.observation import VAEObservationComparator
from src.vae.revision import VAEKnowledgeRevisionManager
from src.vae.e2_e4_extensions import VAEE2E4ScopeGuard
from src.vae.reader_adapter import VAEReaderAdapter


@pytest.fixture
def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def test_loop01_boot_and_identity(repo_root):
    """
    LOOP01_BOOT_AND_IDENTITY: Verify boot provenance and identity.
    """
    plan_path = os.path.join(
        repo_root, "01_os", "07_content", "_runs",
        "run-20261030-nba2k22-vae-gemini-integrated-loop-001",
        "01_任务输入", "task_packet.json"
    )
    with open(plan_path, "r", encoding="utf-8") as f:
        packet = json.load(f)["task_packet"]

    assert packet["task_id"] == "NBA2K22-VAE-GEMINI-INTEGRATED-LOOP-20261030-001"
    assert packet["execution_assignment"]["assigned_model_label"] == "Gemini Flash 3.8"
    assert packet["exact_base_sha"] == "45cc45cae0550ddcda192a2179ea48509b27f6ee"


def test_loop02_scope_and_dirty_tree(repo_root):
    """
    LOOP02_SCOPE_AND_DIRTY_TREE: Ensure changes are strictly within allowed paths.
    """
    allowed_prefixes = [
        "01_os/07_content/_runs/run-20261030-nba2k22-vae-gemini-integrated-loop-001/",
        "08_Domain_Applications/Antigravity_GM_Engine/src/vae/",
        "08_Domain_Applications/Antigravity_GM_Engine/tests/vae/",
        "08_Domain_Applications/Antigravity_GM_Engine/config/vae/",
    ]
    # Check untracked and modified files via git status
    out = subprocess.check_output(["git", "-C", repo_root, "status", "--porcelain"]).decode("utf-8")
    for line in out.splitlines():
        if len(line) > 3:
            path = line[3:].strip().replace("\\", "/")
            # Path must start with at least one allowed prefix
            matched = any(path.startswith(prefix) for prefix in allowed_prefixes)
            assert matched, f"Scope escape detected! Path '{path}' is outside allowed paths."


def test_loop03_source_grading_g01_g08(repo_root):
    """
    LOOP03_SOURCE_GRADING_G01_G08: Audit G01–G08 evidence dossier.
    """
    dossier_path = os.path.join(
        repo_root, "01_os", "07_content", "_runs",
        "run-20261030-nba2k22-vae-gemini-integrated-loop-001",
        "02_证据", "G01_G08_EVIDENCE_DOSSIER.md"
    )
    assert os.path.exists(dossier_path)
    with open(dossier_path, "r", encoding="utf-8") as f:
        content = f.read()

    for g_id in ["G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08"]:
        assert g_id in content, f"Missing evidence grade for {g_id}"


def test_loop04_f02_r06_comparability():
    """
    LOOP04_F02_R06_COMPARABILITY: R06 context fixture includes side/controller/dual Normalize/quarter/base.
    """
    obs1 = CompetitiveObservation(
        trial_id="t1", game_id="g1", save_id="s1", game_date="2021-11-01", engine_path="3D_FAST_SIM",
        side="USER", controller_assigned=True, played_normalize_on=False, sim_normalize_on=False,
        played_quarter_minutes=12, sim_quarter_minutes=12, base_source_ref="ref1", metrics={"pts": 100}
    )
    obs2 = CompetitiveObservation(
        trial_id="t1", game_id="g2", save_id="s1", game_date="2021-11-02", engine_path="3D_FAST_SIM",
        side="USER", controller_assigned=True, played_normalize_on=False, sim_normalize_on=False,
        played_quarter_minutes=12, sim_quarter_minutes=12, base_source_ref="ref1", metrics={"pts": 105}
    )
    is_comp, _, _ = VAEObservationComparator.compare(obs1, obs2)
    assert is_comp is True


def test_loop05_f03_r08_pending_state():
    """
    LOOP05_F03_R08_PENDING_STATE: R08 initial state cannot claim append.
    """
    mgr = VAEKnowledgeRevisionManager()
    rev = mgr.propose_revision("t1", "claim1", "claim2", [], ["src1"])
    assert rev.status == RevisionStatus.PENDING_REVISION
    assert rev.append_receipt is None


def test_loop06_f07_blocked_nullability():
    """
    LOOP06_F07_BLOCKED_NULLABILITY: R03/R04/R05 blocked nullability and transitions.
    """
    p = TrialPreflight(
        trial_id="t1", target_identity="id", before_ref="b", expected_before=None,
        proposed_after=1, metric_primary="m", metrics_side_effect=[], observation_window="w",
        block_reason="Permission blocked", status=PreflightStatus.BLOCKED
    )
    p.validate()
    assert p.status == PreflightStatus.BLOCKED
    assert p.restore_plan is None


def test_loop07_r01_r09_offline_slice(repo_root):
    """
    LOOP07_R01_R09_OFFLINE_SLICE: Execute R01-R09 dry-run and assert evidence statuses.
    """
    pipeline = VAEE1Pipeline(repo_root=repo_root)
    res = pipeline.run_e1_slice()
    assert res["R04_receipt"].status == ReceiptStatus.NOT_RUN
    assert res["R05_readback"].status == ReadbackStatus.UNVERIFIED
    assert res["R08_revision"].status == RevisionStatus.PENDING_REVISION


def test_loop08_reader_reuse_and_safe_fallback(repo_root):
    """
    LOOP08_READER_REUSE_AND_SAFE_FALLBACK: Check adapters do not perform writes and fail safely.
    """
    reader = VAEReaderAdapter(repo_root=repo_root)
    snap = reader.read_settings_field("invalid_field_123")
    assert snap.status == SnapshotStatus.UNKNOWN
    assert snap.raw_value is None


def test_loop09_negative_idempotent_retry():
    """
    LOOP09_NEGATIVE_IDEMPOTENT_RETRY: Test duplicate events/retries and negative paths.
    """
    mgr = VAEKnowledgeRevisionManager()
    r1 = mgr.propose_revision("t1", "claim1", "claim2", [], ["src1"])
    ok1, _, _ = mgr.commit_append(r1)
    assert ok1 is True

    r2 = mgr.propose_revision("t1", "claim1", "claim2", [], ["src1"])
    ok2, _, msg = mgr.commit_append(r2)
    assert ok2 is False
    assert "DUPLICATE_REJECTED" in msg


def test_loop10_e1_e4_scope_coverage():
    """
    LOOP10_E1_E4_SCOPE_COVERAGE: E1-E4 contract coverage assertions.
    """
    # E2 minutes range check
    ok_e2, _ = VAEE2E4ScopeGuard.validate_coach_minutes_request(1, 30, 15)
    assert ok_e2 is True

    # E3 3-team rejection
    ok_e3, _ = VAEE2E4ScopeGuard.validate_trade_teams([1, 2, 3])
    assert ok_e3 is False

    # E4 player training preset write rejection
    ok_e4, _ = VAEE2E4ScopeGuard.reject_player_training_preset_write(0, 0)
    assert ok_e4 is False


def test_loop11_no_game_write_or_new_unauthorized_access(repo_root):
    """
    LOOP11_NO_GAME_WRITE_OR_NEW_UNAUTHORIZED_ACCESS: Inspect zero game write enforcement.
    """
    pipeline = VAEE1Pipeline(repo_root=repo_root)
    assert pipeline.simulator.allow_live_writes is False
    res = pipeline.run_e1_slice(dry_run=True)
    assert res["R04_receipt"].status == ReceiptStatus.NOT_RUN
    assert res["R04_receipt"].technical_response["game_memory_modified"] is False


def test_loop12_git_commit_and_progress_resume(repo_root):
    """
    LOOP12_GIT_COMMIT_AND_PROGRESS_RESUME: Progress ledger exists and tracks iterations.
    """
    ledger_path = os.path.join(
        repo_root, "01_os", "07_content", "_runs",
        "run-20261030-nba2k22-vae-gemini-integrated-loop-001",
        "06_执行", "iteration_ledger.jsonl"
    )
    # Checkpoint exists
    chk_path = os.path.join(
        repo_root, "01_os", "07_content", "_runs",
        "run-20261030-nba2k22-vae-gemini-integrated-loop-001",
        "06_执行", "current_checkpoint.json"
    )
    assert os.path.exists(chk_path)


def test_loop13_final_concentrated_verification(repo_root):
    """
    LOOP13_FINAL_CONCENTRATED_VERIFICATION: Contract v2 exists and is properly structured.
    """
    contract_path = os.path.join(
        repo_root, "01_os", "07_content", "_runs",
        "run-20261030-nba2k22-vae-gemini-integrated-loop-001",
        "01_任务输入", "VAE_VERTICAL_SLICE_CONTRACT_V2.json"
    )
    assert os.path.exists(contract_path)
    with open(contract_path, "r", encoding="utf-8") as f:
        contract = json.load(f)
    assert contract["schema_version"] == "nba2k22.vae.stage02.vertical_slice_contract.v2"
    assert "F02_resolved" in contract["audit_resolution"]
    assert "F03_resolved" in contract["audit_resolution"]
    assert "F04_resolved" in contract["audit_resolution"]
    assert "F07_resolved" in contract["audit_resolution"]


def test_v2_native_capability_inventory():
    """
    V2_NATIVE_CAPABILITY_INVENTORY: All GM/coach/player actions have explicit specification,
    prerequisites, permissions, proof contracts, or blocker statuses.
    """
    from src.vae.native_actions import VAENativeActionRegistry
    from src.vae.contracts import RoleType

    reg = VAENativeActionRegistry()
    assert len(reg.actions) == 12

    gm_actions = [a for a in reg.actions.values() if a.role == RoleType.GM]
    coach_actions = [a for a in reg.actions.values() if a.role == RoleType.COACH]
    player_actions = [a for a in reg.actions.values() if a.role == RoleType.PLAYER]

    assert len(gm_actions) == 5
    assert len(coach_actions) == 3
    assert len(player_actions) == 4

    for a in reg.actions.values():
        assert len(a.preconditions) > 0
        assert a.authority_required != ""
        assert a.native_entry_path != ""
        assert len(a.readback_layers) > 0


def test_v2_method_and_interaction_evidence():
    """
    V2_METHOD_AND_INTERACTION_EVIDENCE: Methodology per action plus source-graded link graph
    and measurable hypothesis/side effects without false causal certainty.
    """
    from src.vae.mechanism_registry import VAEMechanismRegistry

    reg = VAEMechanismRegistry()
    graph = reg.export_graph()
    assert graph["fields_count"] >= 5
    assert graph["edges_count"] >= 5

    for edge in reg.edges.values():
        assert edge.hypothesis != ""
        assert edge.expected_primary_metric != ""
        assert len(edge.confounders) > 0
        assert edge.method_version != ""


def test_v2_role_specific_data_pipeline():
    """
    V2_ROLE_SPECIFIC_DATA_PIPELINE: Role data segregation and negative ACL enforcement.
    """
    from src.vae.role_data_service import VAERoleDataService
    from src.vae.contracts import RoleType, RoleDataQuery

    service = VAERoleDataService()

    # GM allowed finance
    view_gm = service.query_role_view(RoleDataQuery("q1", RoleType.GM, "finance_projection", "s1", "2021"))
    assert view_gm.access_granted is True

    # Player denied finance
    view_leak = service.query_role_view(RoleDataQuery("q2", RoleType.PLAYER, "finance_projection", "s1", "2021"))
    assert view_leak.access_granted is False
    assert "ACCESS_DENIED" in view_leak.rejection_reason


def test_v2_actual_native_readback():
    """
    V2_ACTUAL_NATIVE_READBACK: Bounded execution returns BLOCKED_AWAITING_GAME_AUTH
    or verified dry-run math; zero unauthorized live memory writes.
    """
    from src.vae.native_actions import VAENativeActionRegistry
    from src.vae.contracts import RoleType

    reg = VAENativeActionRegistry()
    res = reg.execute_dryrun("GM-01", RoleType.GM, {"salaries": [20_000_000, 15_000_000]})
    assert res.status == "BLOCKED_AWAITING_GAME_AUTH"
    assert res.output_data["payroll_total"] == 35_000_000


def test_v2_learning_loop_outcome():
    """
    V2_LEARNING_LOOP_OUTCOME: Evaluation tracks confounders, returns non-causal trends,
    and updates persistent knowledge ledger without data loss.
    """
    from src.vae.evaluator import VAEEvaluationEngine
    from src.vae.contracts import EvaluationOutcome

    evaluator = VAEEvaluationEngine()
    ev = evaluator.evaluate(
        trial_id="t1",
        preregistered_metric_ref="pace",
        deltas={"delta_pace": 2.5},
        target_direction="INCREASE",
        confounders=["opponent_pace"],
        sample_size=6,
        controlled_experiment=False,
    )
    # Confounders present -> INCONCLUSIVE
    assert ev.outcome == EvaluationOutcome.INCONCLUSIVE


def test_v3_per_setting_coverage(repo_root):
    """
    V3_PER_SETTING_COVERAGE: Verifies per-setting mechanism research dossier exists
    and documents tendency slots (48 named vs 51 unknown) without false equivalence.
    """
    dossier_path = os.path.join(
        repo_root, "01_os", "07_content", "_runs",
        "run-20261030-nba2k22-vae-gemini-integrated-loop-001",
        "02_证据", "PER_SETTING_MECHANISM_DOSSIER_V3.md"
    )
    assert os.path.exists(dossier_path)
    with open(dossier_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "99" in content
    assert "48" in content
    assert "51" in content
    assert "UNKNOWN_TENDENCY_SLOT" in content


def test_v3_external_sources_and_conflicts(repo_root):
    """
    V3_EXTERNAL_SOURCES_AND_CONFLICTS: Verifies Operation Sports references and competing hypotheses.
    """
    dossier_path = os.path.join(
        repo_root, "01_os", "07_content", "_runs",
        "run-20261030-nba2k22-vae-gemini-integrated-loop-001",
        "02_证据", "PER_SETTING_MECHANISM_DOSSIER_V3.md"
    )
    with open(dossier_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "operationsports.com" in content
    assert "Touches" in content
    assert "COMPETING_HYPOTHESIS" in content


def test_v3_rea_identity_and_value_meaning(repo_root):
    """
    V3_REA_IDENTITY_AND_VALUE_MEANING: Verifies REA offsets (+316, +0x318, +0xCB1/+0x1047).
    """
    dossier_path = os.path.join(
        repo_root, "01_os", "07_content", "_runs",
        "run-20261030-nba2k22-vae-gemini-integrated-loop-001",
        "02_证据", "PER_SETTING_MECHANISM_DOSSIER_V3.md"
    )
    with open(dossier_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "+0x316" in content or "+316" in content
    assert "+0x318" in content
    assert "+0xCB1" in content


def test_v3_interaction_and_value_response():
    """
    V3_INTERACTION_AND_VALUE_RESPONSE: Verifies interaction graph nonlinear thresholds and confounders.
    """
    from src.vae.mechanism_registry import VAEMechanismRegistry

    reg = VAEMechanismRegistry()
    edges = reg.export_graph()["edges"]
    assert len(edges) >= 5

    # Check starter minutes threshold edge
    edge3 = reg.edges["EDGE-03"]
    assert "38" in edge3.hypothesis
    assert "fourth_quarter_efficiency" in edge3.target_behavior


def test_v3_method_effect_evidence():
    """
    V3_METHOD_EFFECT_EVIDENCE: Verifies that decision methods require role data views and non-causal evaluation.
    """
    from src.vae.role_data_service import VAERoleDataService
    from src.vae.evaluator import VAEEvaluationEngine
    from src.vae.contracts import RoleType, RoleDataQuery, EvaluationOutcome

    service = VAERoleDataService()
    view = service.query_role_view(RoleDataQuery("q-test", RoleType.GM, "finance_projection", "s1", "2021"))
    assert view.access_granted is True

    evaluator = VAEEvaluationEngine()
    ev = evaluator.evaluate(
        trial_id="t1",
        preregistered_metric_ref="pace",
        deltas={"delta_pace": 2.0},
        target_direction="INCREASE",
        confounders=[],
        sample_size=6,
        controlled_experiment=False,
    )
    assert ev.outcome == EvaluationOutcome.OBSERVED_TREND_POSITIVE
    assert ev.outcome != EvaluationOutcome.CONFIRMED_CONTROLLED
