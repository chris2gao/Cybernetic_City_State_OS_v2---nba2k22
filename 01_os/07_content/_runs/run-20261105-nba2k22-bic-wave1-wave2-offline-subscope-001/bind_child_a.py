"""Bind the two published requirement decisions and prepare Stage01 owner review."""
import argparse
import importlib.util
import json

import yaml

from bind_child_a0 import (
    A0_DIGEST, APPROVAL as A0_COMMIT, APPROVAL_PATH as A0_PATH,
    CORE_SHA, DEFAULT_CORE, OUT, RUN, RUNNER, digest, git, json_bytes,
)

BASE = "b96fab3684e39062f073abac5e83a930d485ed62"
A_COMMIT = "21fda5b02926e3c720ad127843ba4e9a0ce256c3"
A_DIGEST = "693fede10af802267f3657a4f961b812252449d3ebfc1135527f64b88afe2fda"
A_PATH = "01_os/07_content/_runs/run-20261105-nba2k22-bic-scoped-child-a-human-confirmation-001/HUMAN_CHILD_A_CONFIRMATION_20261105.json"
CONTRACT_COMMIT = "18702c5e986e0ff8754116b6ab75d0dc37b31e77"
CONTRACT_PATH = "01_os/07_content/_runs/run-20261105-nba2k22-bic-scoped-child-a-human-confirmation-001/EXECUTION_CONTRACT_CHILD_A_BIND_STAGE01_20261105.md"
REVIEW_COMMIT = "97cfb4af1439bf4fd55e31a7f33c76cbb175e1df"
REVIEW_PATH = ("01_os/07_content/_runs/run-20261105-nba2k22-bic-child-a-owner-review-001/"
               "CHILD_A_OWNER_ADMISSION_HUMAN_REPORT.md")
STATUS = "PENDING_STAGE01_OWNER_ACCEPTANCE"
FULL_GATE = f"NOT_RUN_{STATUS}"


def original(name):
    return git("show", f"{BASE}:{RUN}/{name}")


def source(commit, path):
    ref = f"{commit}:{path}"
    raw = git("show", ref)
    return raw, {"commit": commit, "path": path, "git_blob": git("rev-parse", ref).decode().strip(),
                 "sha256": digest(raw), "confirmation_ref": ref}


def core_module():
    assert git("rev-parse", "HEAD", repo=DEFAULT_CORE).decode().strip() == CORE_SHA
    runner = DEFAULT_CORE / RUNNER
    assert runner.read_bytes() == git("show", f"{CORE_SHA}:{RUNNER}", repo=DEFAULT_CORE)
    spec = importlib.util.spec_from_file_location("child_a_core", runner)
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)
    return core


def build():
    core = core_module()
    a0_raw, a0_source = source(A0_COMMIT, A0_PATH)
    a_raw, a_source = source(A_COMMIT, A_PATH)
    contract, contract_source = source(CONTRACT_COMMIT, CONTRACT_PATH)
    _, review_source = source(REVIEW_COMMIT, REVIEW_PATH)
    a0_record, a_record = json.loads(a0_raw), json.loads(a_raw)
    assert a0_record["decision_id"] != a_record["decision_id"]
    assert a0_source["confirmation_ref"] != a_source["confirmation_ref"]
    assert a_record["exact_human_statement"] in contract.decode("utf-8")
    assert a0_record["status"] == "HUMAN_CONFIRMED_FIXED_CHILD_A0_V1"
    assert a_record["decision_status"] == "HUMAN_CONFIRMED_FIXED_CHILD_A_V1"
    assert a_record["formal_Stage01"] == "NOT_PASSED"
    assert a_record["exact_approval_scope"]["parent_BIC"] == "INCOMPLETE_UNCHANGED"
    a0_source["copy"] = "sources/HUMAN_CHILD_A0_CONFIRMATION_20261105.json"
    a_source["copy"] = "sources/HUMAN_CHILD_A_CONFIRMATION_20261105.json"
    assert original(a0_source["copy"]) == a0_raw
    prior_binding = json.loads(original("A0_BINDING_INTEGRITY.json"))
    for key in ("commit", "path", "git_blob", "sha256"):
        assert prior_binding["approval_source"][key] == a0_source[key]

    requirement = yaml.safe_load(original("01_requirement.yml"))
    payload = requirement["payload"]
    a0, a = payload["consensus_A0"], payload["requirement_result_A"]
    assert core.normalized_sha256(a0) == A0_DIGEST
    assert core.requirement_confirmation_digest(payload) == A_DIGEST
    a0_confirmation = payload["consensus_Human_confirmation"]
    assert a0_confirmation["confirmed"] is True
    assert a0_confirmation["confirmation_ref"] == a0_source["confirmation_ref"]
    assert a0_record["fixed_binding"]["normalized_sha256"] == A0_DIGEST
    assert a0_record["fixed_binding"]["model_id"] == a0["model_id"]
    assert a0_record["fixed_binding"]["artifact_version"] == a0["version"] == 1
    assert a["consensus_ref"] == {"model_id": a0["model_id"], "version": 1, "sha256": A0_DIGEST,
                                  "confirmation_ref": a0_source["confirmation_ref"]}
    matrix = json.loads(original("ACCEPTANCE_MATRIX.json"))
    criteria = [item["criterion_id"] for item in payload["success_criteria"]]
    results = [item["result_item_id"] for item in a["result_items"]]
    questions = [q["question_id"] for item in a["result_items"] for q in item["unknowns"]]
    assert criteria == [item["criterion_id"] for item in matrix] == a0_record["fixed_binding"]["acceptance_criterion_ids"]
    assert results == [item["requirement_item"] for item in matrix]
    assert a_record["source_binding"] == {
        "repository": "chris2gao/Cybernetic_City_State_OS_v2---nba2k22",
        "child_run_id": OUT.name, "fixed_child_candidate_commit": BASE,
        "fixed_child_requirement_path": f"{RUN}/01_requirement.yml",
        "previous_A0_Human_approval_commit": A0_COMMIT, "previous_A0_Human_approval_path": A0_PATH,
        "previous_A0_model_id": a0["model_id"], "previous_A0_version": 1,
        "previous_A0_normalized_sha256": A0_DIGEST, "this_model_kind": "requirement_result_A",
        "this_model_id": a["model_id"], "this_model_version": a["version"],
        "approved_core_requirement_confirmation_digest_sha256": A_DIGEST,
        "fixed_core_revision": CORE_SHA, "criterion_ids": criteria, "result_ids": results,
        "unknown_question_ids": questions,
    }
    confirmation = payload["Human_confirmation"]
    assert confirmation["confirmed"] is False and confirmation["confirmation_ref"] is None
    assert confirmation["content_sha256"] == A_DIGEST and confirmation["model_id"] == a["model_id"]
    confirmation.update(confirmed=True, confirmation_ref=a_source["confirmation_ref"],
                        status="HUMAN_CONFIRMED_FIXED_CHILD_A_V1")
    assert core.requirement_confirmation_digest(payload) == A_DIGEST

    outputs = {a_source["copy"]: a_raw}
    manifest = yaml.safe_load(original("manifest.yml"))
    assert [entry["stage_id"] for entry in manifest["artifacts"]] == core.EXPECTED_STAGE_IDS
    previous, changes, stage_checks = {}, [], []
    schemas = core.payload_schemas(DEFAULT_CORE)
    for entry in manifest["artifacts"]:
        path, sid = entry["path"], entry["stage_id"]
        old_bytes = original(path)
        assert digest(old_bytes) == entry["sha256"]
        artifact = requirement if path == "01_requirement.yml" else yaml.safe_load(old_bytes)
        assert artifact["status"] == "candidate_pending_owner_acceptance"
        assert all(value is None for value in artifact["stage_control"].values())
        artifact["input_refs"] = [previous[ref["stage_id"]].copy() for ref in artifact["input_refs"]]
        stage_payload = artifact["payload"]
        missing = [key for key in schemas[sid]["payload_required_fields"] if key not in stage_payload]
        types = core.payload_type_findings(stage_payload, sid)
        stage_checks.append({"stage_id": sid, "missing_payload_fields": missing, "type_findings": types})
        assert not missing and not types, stage_checks[-1]
        new_bytes = yaml.safe_dump(artifact, allow_unicode=True, sort_keys=False, width=4096).encode()
        changes.append({"path": path, "old_sha256": entry["sha256"], "new_sha256": digest(new_bytes),
                        "input_refs": artifact["input_refs"]})
        entry["sha256"] = digest(new_bytes)
        previous[sid] = entry.copy()
        outputs[path] = new_bytes
    outputs["manifest.yml"] = yaml.safe_dump(manifest, sort_keys=False).encode()
    findings = {"requirement_findings": core.requirement_findings(payload, 1),
                "evidence_findings": core.evidence_findings(yaml.safe_load(outputs["02_evidence.yml"])["payload"], payload)}
    print(json.dumps(findings))
    assert findings == {"requirement_findings": [], "evidence_findings": []}
    outputs["CANDIDATE_SCHEMA_CHECKS.json"] = json_bytes({
        "stages": stage_checks, **findings, "formal_full_run": FULL_GATE,
        "scope": "Applicable Core payload and type checks. Formal stage decisions remain pending.",
    })
    inventory = {"base": BASE, "core_sha": CORE_SHA, "core_runner_sha256": digest((DEFAULT_CORE / RUNNER).read_bytes()),
                 "contract_source": contract_source, "preparation_review_source": review_source,
                 "A0_approval": a0_source, "A_approval": a_source,
                 "child_A0_sha256": A0_DIGEST, "child_A_sha256": A_DIGEST,
                 "coverage_matrix_sha256": digest(original("ACCEPTANCE_MATRIX.json")),
                 "criterion_ids": criteria, "result_ids": results, "unknown_question_ids": questions,
                 "artifacts": changes, "manifest_sha256": digest(outputs["manifest.yml"]),
                 "formal_stage01_pass": False, "status": STATUS}
    outputs["CHILD_A_BINDING_INTEGRITY.json"] = json_bytes(inventory)

    bindings = json.loads(original("NORMALIZED_BINDINGS.json"))
    bindings.update(child_confirmed=True, child_A_confirmation_ref=a_source["confirmation_ref"],
                    child_A_approval_source=a_source, status=STATUS,
                    owner_sequence="Review the bound Stage01 scope and decide the formal stage plan.")
    outputs["NORMALIZED_BINDINGS.json"] = json_bytes(bindings)
    owner = json.loads(original("OWNER_DECISION_PACKAGE.json"))
    owner.pop("next_Human_decision")
    owner.update(status=STATUS, candidate_artifacts=manifest["artifacts"],
                 single_gate="Stage01 owner plan admission", formal_full_run=FULL_GATE,
                 current_decision_package="STAGE01_OWNER_ADMISSION_PACKAGE.json")
    owner["decisions"][0].update(request="Decide the formal Stage01 plan on its exact Current_Model.",
                                  current_disposition="DUAL_REQUIREMENTS_CONFIRMED_FORMAL_STAGE_PENDING")
    outputs["OWNER_DECISION_PACKAGE.json"] = json_bytes(owner)
    checkpoint = json.loads(original("CHECKPOINT.json"))
    checkpoint.update(status=STATUS, child_A_confirmation_ref=a_source["confirmation_ref"], admission_task_base_sha=BASE,
                      admission_task_id="NBA2K22-BIC-W1-W2-CHILD-A-BIND-STAGE01-ADMISSION-20261105-001",
                      progress=["Both fixed requirement decisions bound", "Stage01–07 transitive artifact hashes verified"],
                      next_steps=["Review STAGE01_OWNER_ADMISSION_HANDOFF.md for the formal Stage01 plan decision"])
    outputs["CHECKPOINT.json"] = json_bytes(checkpoint)
    run_doc = yaml.safe_load(original("run.yml"))
    run_doc.update(formal_status=STATUS, closure_record="STAGE01_OWNER_ADMISSION_HANDOFF.md")
    outputs["run.yml"] = yaml.safe_dump(run_doc, sort_keys=False).encode()
    package = json.loads(original("OWNER_DECISION_PACKAGE.json"))
    outputs["STAGE01_OWNER_ADMISSION_PACKAGE.json"] = json_bytes({
        "status": STATUS, "run_task_id": run_doc["task_id"], "stage_id": manifest["artifacts"][0]["stage_id"],
        "dual_requirement_evidence": "CHILD_A_BINDING_INTEGRITY.json", "stage01_candidate": manifest["artifacts"][0],
        "manifest_sha256": inventory["manifest_sha256"], "core_revision": CORE_SHA,
        "applicable_findings": findings, "next_decision": "Stage01 formal plan acceptance after binding its exact Current_Model",
        "review_material": ["01_requirement.yml", "ACCEPTANCE_MATRIX.json", "NORMALIZED_BINDINGS.json",
                            "STAGE01_ADMISSION_VERIFICATION.json"],
        "authority": {
            "formal_record_actor_class_required_by_pinned_core": "current_Human",
            "review_coordination": "GPT-6 / decision_architecture",
            "stage_action_and_owner_context": "Use run.yml task_packet_ref and the packet's unique stage_actions entry for the actual Stage01 action. Bind the action ID and exact scope before recording either decision.",
            "policy_refs": package["lawful_owner_resolution"]["policy_refs"] + [
                "01_os/06_execution/workflow/publication_gate/workflow_publication_gate.py",
                "01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation.py",
            ],
        },
        "required_history": [
            {"phase": "M", "required": "Committed Current_Model for exact run task and Stage01 with scoped action, complete model and feasibility basis."},
            {"phase": "P", "required": "Separate actual Human plan acceptance of M by commit/path/blob, under the stage acceptance validator. Stage01 predecessor_completion_commit is null."},
            {"phase": "W", "required": "Commit the actual authorized Stage01 output after P. The exact output blob must be absent at P."},
            {"phase": "V", "required": "Record verification_result as exact commit/path/blob in a commit distinct from W. Current preparation logs cover the candidate only."},
            {"phase": "C", "required": "Separate actual Human completion acceptance bound to W and its verification result. Its record is absent at W. Stage02 plan later binds this C."},
        ],
        "missing_control_bindings": ["action_id", "current_model_ref", "deliberation_receipt_ref",
                                     "plan_acceptance", "completion_acceptance"],
        "strict_git_ancestry": ["M->P", "P->W", "W->C"],
        "stage_control": requirement["stage_control"],
        "formal_full_run": FULL_GATE,
    })
    return outputs, inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, inventory = build()
    for path, raw in outputs.items():
        if args.check:
            assert (OUT / path).read_bytes() == raw, path
        else:
            (OUT / path).write_bytes(raw)
    assert (OUT / "ACCEPTANCE_MATRIX.json").read_bytes() == original("ACCEPTANCE_MATRIX.json")
    assert (OUT / "sources/HUMAN_CHILD_A0_CONFIRMATION_20261105.json").read_bytes() == original(
        "sources/HUMAN_CHILD_A0_CONFIRMATION_20261105.json")
    print(json.dumps({"child_A0_sha256": A0_DIGEST, "child_A_sha256": A_DIGEST,
                      "artifact_count": len(inventory["artifacts"]), "status": STATUS}))


if __name__ == "__main__":
    main()
