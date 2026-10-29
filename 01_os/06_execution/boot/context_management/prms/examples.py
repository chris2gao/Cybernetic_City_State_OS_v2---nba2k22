"""Reproducible isolated-state and read-only actual-source integration exercises."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

from catalog import discover_g1, discover_g2
from context import plan_context, human_choice, assemble_context
from domain_context import plan_domain_context, choose_domain_context, assemble_domain_context, verify_domain_context
from recovery import create_recovery_package, verify_window_recovery
from source import GitSource, GitHubSource, PRMSError
from state import LocalGitState, WriterGate

DOMAIN_COMMIT = "094f1aa641f93dec2277707ad9dbf5bdb0341247"


def core_plan(root, session):
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip()
    source = GitSource(root, head, "chris2gao/Cybernetic_City_State_OS_v2---core")
    catalog = discover_g1(source)
    plan = plan_context(source, catalog, session_id=session, role="implementation_owner",
                        task_id="PRMS", stage="06", actions=["execution_completion"])
    choice = human_choice(plan, session_id=session, selected_paths=[],
                          decision_source="Current Human instruction to implement and verify PRMS in isolation")
    return source, catalog, plan, choice


def isolated_example(root):
    source, catalog, plan, choice = core_plan(root, "isolated-example")
    with tempfile.TemporaryDirectory(prefix="prms-example-") as temp:
        store = LocalGitState.initialize_isolated(Path(temp) / "state.git", sandbox_parent=temp)
        gate = WriterGate(store)
        first = gate.open_isolated_session("first", ["implementation-role"])
        second = gate.open_isolated_session("second", ["implementation-role"])
        def apply(caller, operation, kind, payload, initial=False):
            current = {"state_version": 0, "owner_epoch": 0} if initial else gate.recover("implementation-role")["current"]
            return gate.apply(caller, "implementation-role", operation_id=operation, expected_head=store.head(),
                               expected_version=current["state_version"], expected_epoch=current["owner_epoch"],
                               kind=kind, payload=payload)
        apply(first, "register", "REGISTER", {"definition": {"role_type_id": "implementation_owner", "version": "1"},
             "domain_id": "core", "state_repository_id": "isolated-example"}, initial=True)
        apply(first, "assign", "ASSIGN", {"assignment_id": "PRMS", "task_id": "PRMS",
             "human_authority_ref": "SYNTHETIC fixture assignment; no production authority"})
        apply(first, "decision", "APPEND", {"event_id": "Q52", "task_id": "PRMS", "kind": "HUMAN_DECISION",
             "text": "SYNTHETIC TEST FIXTURE: Q52=B", "source_refs": [{"repository": source.repository,
             "commit": source.commit, "path": "01_os/03_mechanisms/context_management/prms/README.md"}]})
        apply(first, "checkpoint", "CHECKPOINT", {"task_id": "PRMS", "open_items": ["independent review"]})
        apply(second, "claim", "CLAIM", {})
        stale = "UNEXPECTED_SUCCESS"
        try:
            apply(first, "stale-write", "CHECKPOINT", {})
        except PRMSError as exc:
            stale = exc.status
        try:
            gate.require_enforced()
        except PRMSError as exc:
            enforced = exc.status
        history = {"session_id": plan["session_id"], "depth": "L3", "selected_event_ids": [],
                   "decision_source": "Current Human authorized isolated recovery demonstration"}
        package = create_recovery_package(gate, "implementation-role", source, core_plan=plan,
                                          core_choice=choice, history_choice=history, budget_bytes=2_000_000)
        verified = verify_window_recovery(gate, source, package, core_plan=plan, core_choice=choice, history_choice=history)
        assert stale == "STALE_OWNER" and enforced == "FENCING_NOT_ENFORCEABLE" and package["status"] == "READY"
        return {"schema_version": "prms.isolated_example.v1", "scope": "SYNTHETIC_ISOLATED_REAL_GIT",
                "candidate": source.commit, "catalog_counts": catalog["counts"],
                "role_current": package["role_current"], "state_commit": package["state_commit"],
                "writer_gate": {"old_session_result": stale, "enforced_mode_result": enforced,
                                "fencing_mode": package["fencing_mode"]},
                "recovery": {k: v for k, v in package.items() if k not in ("core_context", "role_current")},
                "actual_read_manifest": [b["source"] for b in package["core_context"]["full_bodies"]],
                "verification": verified, "actual_model_window": "NOT_RUN", "action_authorized": False}


def source_example(root):
    core, g1, cp, cc = core_plan(root, "pinned-domain-source")
    cr = assemble_context(core, cp, cc, budget_bytes=2_000_000)
    source = GitHubSource("chris2gao/Cybernetic_City_State_OS_v2---nba2k22", DOMAIN_COMMIT)
    catalog = discover_g2(source, "nba2k22")
    ids = {c["module"].get("id", c["module"].get("module_id")) for c in catalog["candidates"]}
    assert ids == {f"P{x:02}" for x in range(13)} and not catalog["entries"]
    plan = plan_domain_context(source, catalog, cp, role="implementation_owner", required_modules=["P04", "P09"])
    choice = choose_domain_context(plan, session_id=cp["session_id"], selected_ids=[],
                                   decision_source="Current Human instruction to validate P04/P09 source inheritance")
    receipt = assemble_domain_context(source, cr, plan, choice, budget_bytes=2_000_000)
    check = verify_domain_context(source, receipt, core_source=core, core_receipt=cr,
                                  core_plan=cp, core_choice=cc, domain_plan=plan, domain_choice=choice)
    assert receipt["status"] == "READY" and receipt["reads"]
    return {"schema_version": "prms.actual_source_example.v1", "candidate": core.commit,
            "scope": "PINNED_REAL_GITHUB_SOURCE_READ_ONLY", "g1_catalog": g1, "domain_catalog": catalog,
            "core_actual_read_manifest": [b["source"] for b in cr["full_bodies"]],
            "domain_receipt": {k: v for k, v in receipt.items() if k != "reads"},
            "domain_actual_read_manifest": [{k: v for k, v in b.items() if k != "text"} for b in receipt["reads"]],
            "verification": check, "game_or_REA_operations": False, "actual_model_window": "NOT_RUN"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["isolated-state", "pinned-domain-source"])
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()
    result = (isolated_example if args.kind == "isolated-state" else source_example)(Path(args.repo_root).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
