import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import GitSource, PRMSError
from catalog import discover_g1, discover_g2, compare_domain_catalog
from context import plan_context, human_choice, assemble_context
from domain_context import plan_domain_context, choose_domain_context, assemble_domain_context, verify_domain_context
from memory import task_series_current

CORE = Path(__file__).resolve().parents[6]
BASE = "446ca66ad48831f5fcdb1af18f37d07619e048c4"


def commit(root):
    for args in [["init", "-q"], ["add", "--", "01_os/", "08_Domain_Applications/"],
                 ["-c", "user.name=PRMS test", "-c", "user.email=test@example.invalid", "commit", "-qm", "explicit scope fixture"]]:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip()
    return GitSource(root, sha, "example/maths")


@pytest.fixture
def domain_source(tmp_path):
    domain = tmp_path / "08_Domain_Applications"
    domain.mkdir()
    (domain / "domain.yml").write_text("domain_id: maths2.0\nrepository: example/maths\n")
    for task, lifecycle in [("active", "research_only"), ("unknown", "CUSTOM_DONE"), ("terminal", "verified_on_demand")]:
        root = tmp_path / f"01_os/_runs/{task}"
        root.mkdir(parents=True)
        (root / "run.yml").write_text(yaml.safe_dump({"task_id": task, "lifecycle": lifecycle,
                        "closure_record": "closure.yml", "open_items": ["remaining work"]}))
        if task == "terminal":
            (root / "closure.yml").write_text("completion_pointer: {status: accepted_for_fixture_scope}\n")
    return commit(tmp_path)


def test_series_unknown_visible_terminal_requires_real_closure_and_series_decision(domain_source):
    paths = [f"01_os/_runs/{t}/run.yml" for t in ["active", "unknown", "terminal"]]
    result = task_series_current(domain_source, paths, series_id="series", related_task_ids=["active", "unknown", "terminal"])
    by_id = {t["task_id"]: t for t in result["tasks"]}
    assert by_id["unknown"]["classification"] == "unknown" and by_id["unknown"]["default_visible"]
    assert not by_id["terminal"]["default_visible"] and by_id["terminal"]["closure_verified"]
    assert result["status"] == "ACTIVE_OR_UNCONFIRMED"
    terminal_only = task_series_current(domain_source, paths, series_id="series", related_task_ids=["terminal"])
    assert len(terminal_only["filtered_paths"]) == 2
    assert terminal_only["status"] == "ACTIVE_OR_UNCONFIRMED"  # no series closeout exists


def test_domain_source_context_never_substitutes_nba_for_empty_maths(domain_source):
    core = GitSource(CORE, BASE, "chris2gao/Cybernetic_City_State_OS_v2---core")
    cp = plan_context(core, discover_g1(core), session_id="s", role="planner", task_id="task")
    cc = human_choice(cp, session_id="s", selected_paths=[], decision_source="fixture current Human input")
    cr = assemble_context(core, cp, cc, budget_bytes=1_000_000)
    catalog = discover_g2(domain_source, "maths2.0")
    dp = plan_domain_context(domain_source, catalog, cp, role="planner")
    choice = choose_domain_context(dp, session_id="s", selected_ids=[], decision_source="fixture optional scope empty")
    receipt = assemble_domain_context(domain_source, cr, dp, choice, budget_bytes=1_000_000)
    assert receipt["domain_catalog_status"] == "DOMAIN_CATALOG_UNINITIALIZED"
    assert receipt["reads"] == [] and not receipt["action_authorized"]
    verify_domain_context(domain_source, receipt, core_source=core, core_receipt=cr,
                          core_plan=cp, core_choice=cc, domain_plan=dp, domain_choice=choice)
    with pytest.raises(PRMSError, match="SOURCE_MISSING"):
        plan_domain_context(domain_source, catalog, cp, role="planner", required_modules=["P09"])
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        choose_domain_context(dp, session_id="different-session", selected_ids=[], decision_source="old approval")
    tampered = copy.deepcopy(catalog)
    tampered["candidates"].append({"module": {"module_id": "P09", "docs": []}})
    with pytest.raises(PRMSError, match="SUMMARY_STALE"):
        plan_domain_context(domain_source, tampered, cp, role="planner")


def test_selected_module_bodies_and_directory_references_are_separate(tmp_path):
    domain = tmp_path / "08_Domain_Applications"
    domain.mkdir()
    (domain / "domain.yml").write_text("domain_id: nba2k22\nrepository: example/maths\n")
    engine = domain / "Antigravity_GM_Engine"
    registry = engine / "docs/development/PROJECT_MODULE_REGISTRY_V2.json"
    registry.parent.mkdir(parents=True)
    (engine / "docs/README.md").write_text("# Synthetic mechanism source\n")
    (engine / "research").mkdir()
    (engine / "research/README.md").write_text("# Synthetic tool source; no execution\n")
    registry.write_text(json.dumps({"module_base": "08_Domain_Applications/Antigravity_GM_Engine/", "modules": [{"id": "P00", "context_kind": "CORE_GOVERNANCE_REFERENCE", "docs": ["AGENTS.md"]},
            {"id": "P04", "docs": ["docs/README.md"]}, {"id": "P09", "docs": ["research/README.md"]},
            {"id": "P11", "docs": ["docs/reference/"]}]}))
    (tmp_path / "01_os").mkdir()
    (tmp_path / "01_os/fixture.md").write_text("# Isolated source fixture\n")
    source = commit(tmp_path)
    core = GitSource(CORE, BASE, "chris2gao/Cybernetic_City_State_OS_v2---core")
    cp = plan_context(core, discover_g1(core), session_id="s", role="planner", task_id="task")
    cc = human_choice(cp, session_id="s", selected_paths=[], decision_source="fixture")
    cr = assemble_context(core, cp, cc, budget_bytes=1_000_000)
    dp = plan_domain_context(source, discover_g2(source, "nba2k22"), cp, role="planner", required_modules=["P04", "P09"])
    choice = choose_domain_context(dp, session_id="s", selected_ids=[], decision_source="fixture")
    receipt = assemble_domain_context(source, cr, dp, choice, budget_bytes=1_000_000)
    assert receipt["status"] == "READY" and len(receipt["reads"]) == 2
    assert all(r["publication_status"] == "CANDIDATE_NOT_FORMAL_G2" for r in receipt["reads"])
    directory = next(c["id"] for c in dp["cards"] if c.get("source_kind") == "DIRECTORY_REFERENCE")
    choice = choose_domain_context(dp, session_id="s", selected_ids=[directory], decision_source="fixture directory expansion")
    receipt = assemble_domain_context(source, cr, dp, choice, budget_bytes=1_000_000)
    assert receipt["status"] == "PARTIAL"
    assert receipt["missing"][0]["status"] == "DIRECTORY_REQUIRES_EXPLICIT_EXPANSION"
    # A real second Git snapshot changes one module body, not every module card.
    frozen = discover_g2(source, "nba2k22")
    (engine / "research/README.md").write_text("# Synthetic changed P09 source\n")
    changed = commit(tmp_path)
    differential = compare_domain_catalog(source, frozen, changed)
    statuses = {e["module_id"]: e["status"] for e in differential["module_entries"]}
    assert statuses["P04"] == "VALID" and statuses["P09"] == "SUMMARY_STALE"
    assert differential["added_modules"] == [] and differential["body_loaded"] is False
    assert not differential["action_authorized"]
    forged = copy.deepcopy(frozen)
    forged["candidates"][0]["module"]["docs"] = []
    with pytest.raises(PRMSError, match="SUMMARY_STALE"):
        compare_domain_catalog(source, forged, changed)
