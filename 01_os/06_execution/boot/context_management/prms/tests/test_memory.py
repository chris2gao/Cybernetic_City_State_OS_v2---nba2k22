import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import canonical, PRMSError
from state import LocalGitState, WriterGate
from memory import build_index, stale_dependencies, search_memory, expand_memory, task_visibility
from memory import copy_all_memory, propose_experience, promotion_readiness
from memory import source_dependency_status


def events():
    return {"roles/r/events/a.json": canonical({"event_id": "a", "kind": "HUMAN_DECISION",
            "text": "Approved A", "task_id": "task1", "topic": "requirements", "source_refs": ["source-A"]}),
            "roles/r/events/b.json": canonical({"event_id": "b", "kind": "MODEL_INFERENCE",
            "text": "Candidate B", "task_id": "task2", "topic": "design", "source_refs": ["source-B"]})}


def test_precise_stale_and_no_hit_scope():
    source = events()
    index = build_index(source, "r", "a" * 40, 1)
    source["roles/r/events/a.json"] += b" "
    assert stale_dependencies(index, source) == {"a": "SUMMARY_STALE", "b": "VALID"}
    result = search_memory(index, "absent", task_id="task1")
    assert result["status"] == "NO_MATCH_WITHIN_SCANNED_SCOPE"
    assert result["filtered"] == 1 and result["searched"] == 1
    with pytest.raises(PRMSError, match="SUMMARY_STALE"):
        expand_memory(source, index["entries"][0])
    assert expand_memory(source, index["entries"][1])["kind"] == "MODEL_INFERENCE"


def test_unknown_and_invalid_terminal_closure_stay_visible(tmp_path):
    (tmp_path / "run.yml").write_text("lifecycle: SOME_FREEFORM_DONE\n", encoding="utf-8")
    assert task_visibility(tmp_path)["classification"] == "unknown"
    assert task_visibility(tmp_path)["default_visible"]
    (tmp_path / "run.yml").write_text("lifecycle: verified_on_demand\n", encoding="utf-8")
    assert task_visibility(tmp_path)["reason"] == "closure_not_verified"


def test_copy_physical_content_and_independent_target_current(tmp_path):
    store = LocalGitState.initialize_isolated(tmp_path / "state.git", sandbox_parent=tmp_path)
    gate = WriterGate(store)
    caller = gate.open_isolated_session("session", ["r", "new-r"])
    gate.apply(caller, "r", operation_id="register-r", expected_head=store.head(), expected_version=0,
               expected_epoch=0, kind="REGISTER", payload={"definition": {"role_type_id": "engineer", "version": "1"},
                    "domain_id": "core", "state_repository_id": "isolated"})
    source_events = events()
    frozen = store.commit(store.head(), source_events, "prepare-events")["authoritative_commit_sha"]
    copier = gate.open_isolated_session("copier", ["new-r"], allowed_copy_scopes=[{
        "source_role": "r", "target_role": "new-r", "source_commit": frozen,
        "approval_ref": "test Human authorized r to new-r"}])
    result = copy_all_memory(store, gate, copier, "r", "new-r", source_head=frozen,
                             operation_id="copy", target_expected_head=frozen,
                             scope_approval_ref="test Human authorized r to new-r")
    snapshot = store.snapshot(result["authoritative_commit_sha"])
    manifest = json.loads(snapshot["roles/new-r/copies/copy/manifest.json"])
    for entry in manifest["items"]:
        assert snapshot[entry["target_path"]] == store.snapshot(frozen)[entry["source_path"]]
    assert {x["path"] for x in manifest["excluded_authority"]} == {"roles/r/CURRENT.json", "roles/r/owner.json"}
    assert gate.recover("new-r")["current"]["state_version"] == 1
    assert gate.recover("new-r")["identity"]["copied_authority_valid"] is False
    assert len(gate.recover("new-r")["events"]) == 2
    retry = copy_all_memory(store, gate, copier, "r", "new-r", source_head=frozen,
                            operation_id="copy", target_expected_head=frozen,
                            scope_approval_ref="test Human authorized r to new-r")
    assert retry["status"] == "ALREADY_APPLIED"
    assert store.head() == result["authoritative_commit_sha"]
    # A copied role evolves under its own CURRENT without rewriting source identity or history.
    original_source = {p: raw for p, raw in snapshot.items() if p.startswith("roles/r/")}
    target = gate.recover("new-r")["current"]
    gate.apply(caller, "new-r", operation_id="claim-target", expected_head=store.head(),
               expected_version=target["state_version"], expected_epoch=target["owner_epoch"],
               kind="CLAIM", payload={})
    target = gate.recover("new-r")["current"]
    gate.apply(caller, "new-r", operation_id="evolve-target", expected_head=store.head(),
               expected_version=target["state_version"], expected_epoch=target["owner_epoch"],
               kind="CHECKPOINT", payload={"open_items": ["target-only work"]})
    evolved = store.snapshot()
    assert {p: raw for p, raw in evolved.items() if p.startswith("roles/r/")} == original_source
    assert gate.recover("new-r")["checkpoint"]["state"]["open_items"] == ["target-only work"]
    target = gate.recover("new-r")["current"]
    assert evolved["roles/new-r/definitions/1.json"] == store.snapshot(frozen)["roles/r/definitions/1.json"]
    before_upgrade = store.head()
    with pytest.raises(PRMSError, match="REJECTED"):
        gate.apply(caller, "new-r", operation_id="reused-template", expected_head=before_upgrade,
                   expected_version=target["state_version"], expected_epoch=target["owner_epoch"],
                   kind="UPGRADE_DEFINITION", payload={"role_type_id": "engineer", "version": "1", "compatibility_ref": "fixture"})
    assert store.head() == before_upgrade
    gate.apply(caller, "new-r", operation_id="new-template", expected_head=before_upgrade,
               expected_version=target["state_version"], expected_epoch=target["owner_epoch"],
               kind="UPGRADE_DEFINITION", payload={"role_type_id": "engineer", "version": "2", "compatibility_ref": "fixture"})
    assert gate.recover("new-r")["identity"]["definition"]["version"] == "2"
    assert store.snapshot()["roles/new-r/definitions/1.json"] == store.snapshot(frozen)["roles/r/definitions/1.json"]


def test_experience_never_promotes_on_self_claimed_refs():
    candidate = propose_experience(["evidence"], ["counterexample"], "core", "Core-owner")
    reply = promotion_readiness(candidate, review_ref="claimed review", human_decision_ref="claimed approval",
                                publication_ref="claimed commit")
    assert candidate["layer"] == reply["layer"] == "K1"
    assert reply["status"] == "AUTHORITY_UNVERIFIED" and not reply["action_authorized"]


def test_external_blob_change_invalidates_only_dependent_summary():
    raw = events()
    for number, path in enumerate(sorted(raw)):
        event = json.loads(raw[path])
        event["source_refs"] = [{"repository": "fixture/source", "path": f"{number}.md",
                                "commit": "a" * 40, "blob": str(number) * 40}]
        raw[path] = canonical(event)
    index = build_index(raw, "r", "a" * 40, 1)
    observed = {("fixture/source", "0.md"): {"commit": "b" * 40, "blob": "f" * 40},
                ("fixture/source", "1.md"): {"commit": "b" * 40, "blob": "1" * 40}}
    assert source_dependency_status(index, observed) == {"a": "SUMMARY_STALE", "b": "VALID"}
    assert index["summaries"][0]["source_refs"][0]["blob"] == "0" * 40


def test_copy_cannot_bypass_host_operation_scope(tmp_path):
    store = LocalGitState.initialize_isolated(tmp_path / "state.git", sandbox_parent=tmp_path)
    gate = WriterGate(store)
    owner = gate.open_isolated_session("owner", ["source"])
    gate.apply(owner, "source", operation_id="register", expected_head=store.head(), expected_version=0,
               expected_epoch=0, kind="REGISTER", payload={"definition": {"role_type_id": "engineer", "version": "1"},
                    "domain_id": "core", "state_repository_id": "isolated"})
    frozen = store.head()
    limited = gate.open_isolated_session("limited", ["target"], allowed_operations=["CHECKPOINT"])
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        copy_all_memory(store, gate, limited, "source", "target", source_head=frozen,
                        operation_id="copy", target_expected_head=frozen, scope_approval_ref="caller claimed approval")
    assert store.head() == frozen and not any(p.startswith("roles/target/") for p in store.snapshot())
    unrestricted = gate.open_isolated_session("copy-host", ["target"], allowed_operations=["COPY_ALL_MEMORY"])
    for unpinned in (None, "master", True):
        with pytest.raises(PRMSError, match="REJECTED"):
            copy_all_memory(store, gate, unrestricted, "source", "target", source_head=unpinned,
                            operation_id="copy", target_expected_head=frozen, scope_approval_ref="fixture")
    assert store.head() == frozen


def test_task_scoped_copy_requires_exact_host_grant_and_remains_revocable(tmp_path):
    store = LocalGitState.initialize_isolated(tmp_path / "state.git", sandbox_parent=tmp_path)
    gate = WriterGate(store)
    owner = gate.open_isolated_session("owner", ["source"])
    gate.apply(owner, "source", operation_id="register", expected_head=store.head(), expected_version=0,
               expected_epoch=0, kind="REGISTER", payload={"definition": {"role_type_id": "engineer", "version": "1"},
                    "domain_id": "core", "state_repository_id": "isolated"})
    frozen = store.head()
    task_only = gate.open_isolated_session("task-only", ["target"], allowed_tasks=["task"],
                                          allowed_operations=["COPY_ALL_MEMORY"])
    kwargs = dict(source_head=frozen, operation_id="copy", target_expected_head=frozen,
                  scope_approval_ref="host-authorized-copy")
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        copy_all_memory(store, gate, task_only, "source", "target", **kwargs)
    bound = gate.open_isolated_session("bound", ["target"], allowed_tasks=["task"],
        allowed_operations=["COPY_ALL_MEMORY"], allowed_copy_scopes=[{
            "source_role": "source", "target_role": "target", "source_commit": frozen,
            "approval_ref": "host-authorized-copy"}])
    for changed in ({"source_head": "a" * 40}, {"scope_approval_ref": "self-claimed approval"}):
        with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
            copy_all_memory(store, gate, bound, "source", "target", **{**kwargs, **changed})
    assert store.head() == frozen
    reply = copy_all_memory(store, gate, bound, "source", "target", **kwargs)
    assert reply["status"] == "PUBLISHED" and gate.recover("target")["identity"]["copied_authority_valid"] is False
    assert copy_all_memory(store, gate, bound, "source", "target", **kwargs)["status"] == "ALREADY_APPLIED"
    gate.revoke_isolated_session(bound)
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        copy_all_memory(store, gate, bound, "source", "target", **kwargs)


def test_invalid_source_checkpoint_prevents_target_copy_publication(tmp_path):
    store = LocalGitState.initialize_isolated(tmp_path / "state.git", sandbox_parent=tmp_path)
    gate = WriterGate(store)
    caller = gate.open_isolated_session("owner", ["source", "target"])
    gate.apply(caller, "source", operation_id="register", expected_head=store.head(), expected_version=0,
               expected_epoch=0, kind="REGISTER", payload={"definition": {"role_type_id": "engineer", "version": "1"},
                    "domain_id": "core", "state_repository_id": "isolated"})
    gate.apply(caller, "source", operation_id="cp", expected_head=store.head(), expected_version=1,
               expected_epoch=1, kind="CHECKPOINT", payload={})
    snapshot = store.snapshot()
    checkpoint_path = "roles/source/checkpoints/cp.json"
    invalid = json.loads(snapshot[checkpoint_path])
    invalid["event_manifest"]["roles/source/events/missing.json"] = "f" * 64
    # Direct local corruption is possible in cooperative mode; recovery must expose it.
    store.commit(store.head(), {checkpoint_path: canonical(invalid)}, "fixture-corruption")
    frozen = store.head()
    copier = gate.open_isolated_session("copier", ["target"], allowed_copy_scopes=[{
        "source_role": "source", "target_role": "target", "source_commit": frozen, "approval_ref": "fixture"}])
    with pytest.raises(PRMSError, match="COPY_INCOMPLETE"):
        copy_all_memory(store, gate, copier, "source", "target", source_head=frozen,
                        operation_id="copy", target_expected_head=frozen, scope_approval_ref="fixture")
    assert store.head() == frozen and not any(p.startswith("roles/target/") for p in store.snapshot())


@pytest.mark.parametrize("tasks,copies", [(None, None), (None, []), (["task"], None), (["task"], [])])
def test_no_host_mode_has_a_permissive_copy_default(tmp_path, tasks, copies):
    store = LocalGitState.initialize_isolated(tmp_path / "state.git", sandbox_parent=tmp_path)
    gate = WriterGate(store)
    caller = gate.open_isolated_session("session", ["target"], allowed_tasks=tasks,
        allowed_operations=["COPY_ALL_MEMORY"], allowed_copy_scopes=copies)
    with pytest.raises(PRMSError, match="AUTHORITY_UNVERIFIED"):
        gate.authorize_copy(caller, "source", "target", "a" * 40, "caller approval")
