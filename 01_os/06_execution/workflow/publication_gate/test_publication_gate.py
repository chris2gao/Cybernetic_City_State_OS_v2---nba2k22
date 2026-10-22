"""Cases against the workflow publication gate, driven through its CLI.

The fixture builder writes every artifact by hand from constants held here. It
never calls _collect_nodes, _check_separation or any other production helper to
work out what the answer should be. If it did, a wrong assumption in the gate
would be copied into the expected truth and the suite would agree with the bug.

Every negative case asserts the exit code and a substring of the reason. A test
that only asserts nonzero cannot tell a refusal for the right cause from a
refusal for the wrong one, which is the shape of HK-001: an install check that
reported a master refusal because the output happened to contain the word
BLOCKED.

One valid chain is built once and each case mutates exactly one invariant.
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

def discard(path: Path) -> None:
    """Remove a fixture repository, read-only git objects included.

    shutil.rmtree(..., ignore_errors=True) does not do this on Windows. Git marks
    loose objects read-only, unlink refuses, and ignore_errors swallows it without
    a word. 246 abandoned fixture repositories had piled up in TEMP before anyone
    looked, each one a full seven-stage chain, and every later run got slower for
    it. A cleanup that cannot fail loudly is a cleanup that stops happening.
    """
    def clear_readonly(func, target, _exc):
        os.chmod(target, stat.S_IWRITE)
        func(target)

    handler = ("onexc" if sys.version_info >= (3, 12) else "onerror")
    try:
        shutil.rmtree(path, **{handler: clear_readonly})
    except OSError:
        # Never fail a test on cleanup, but do not pretend it succeeded either.
        print(f"could not remove fixture repository {path}", file=sys.stderr)


HERE = Path(__file__).resolve().parent
GATE = HERE / "workflow_publication_gate.py"
RUN = "01_os/_runs/run-fixture-001"
STAGES = [
    "workflow_stage_01_requirement_modeling",
    "workflow_stage_02_information_collection",
    "workflow_stage_03_result_modeling",
    "workflow_stage_04_test_generation",
    "workflow_stage_05_step_decomposition",
    "workflow_stage_06_execution",
    "workflow_stage_07_test_execution",
]
FILES = ["01_requirement.yml", "02_evidence.yml", "03_result.yml", "04_tests.yml",
         "05_steps.yml", "06_execution.yml", "07_verification.yml"]


def git(repo: Path, *args: str, stdin: bytes | None = None) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          input=stdin, check=True)
    return proc.stdout.decode("utf-8").strip()


# A stage acceptance the mechanism will actually accept.
#
# The earlier version of this constant carried four fields - provenance,
# actor_class, explicit, Human_disposition - and that was the whole positive
# control. It was not a compliant example of anything. A record with those four
# fields and nothing else carries no commitment, names no task, no stage and no
# decision type, and says nothing about which model or which output it accepted,
# so a PASS built on it proved only that four strings were present. Three
# bypasses lived behind that: records omitting task_id and stage_id, a plan
# record naming the wrong model, and a plan record copied into the completion
# slot. All three passed the gate.
#
# Everything below is the mechanism's own vocabulary. The identity, decision type
# and model-version names are EVENT_COMMITMENT_BOUND_FIELDS, the exact fields a v2
# commitment is computed over. This file invents no schema.
#
# Read this before copying it anywhere. These are fabricated approvals. They exist
# in a throwaway repository, for a task and run id that are not real, to give the
# suite a positive control - without one, a gate that refused every record for the
# wrong reason would look exactly like a working gate. They are NOT a template for
# a real run: writing one of these into 01_os/_runs/** by hand is manufacturing a
# Human acceptance, which is the thing this whole arrangement exists to detect.
# test_synthetic_marked_record_is_refused is the guard on that.
#
# The commitments are structurally valid and deliberately not recomputable. The
# mechanism checks commitment structure, which is what makes a record
# challengeable; recomputing a digest against the Human's nonce is the interactive
# challenge, which does not run on a publication path. Computing real digests here
# would also mean importing the mechanism to build the fixture, and the fixture
# does not borrow production code to manufacture its own expected truth.
TASK_ID = "task-gate-fixture-001"
AUTHORITY_ID = "authority-gate-fixture-001"
PLAN_DECISION = "substantive_execution_authorization"
COMPLETION_DECISION = "completion_acceptance"
_TASK_DIGEST = "1f" * 32
_EVENT_DIGEST = "2e" * 32


def commitment(digest: str) -> dict:
    return {"scheme": "citystate-human-task-authority-v2", "algorithm": "sha256",
            "digest": digest}


def accepted(sid: str, decision_type: str, **extra) -> dict:
    """One Human acceptance record, in the mechanism's own field names."""
    record = {
        "provenance": "foreground_current_Human_interaction",
        "actor_class": "current_Human",
        "explicit": True,
        "Human_disposition": "accepted",
        "task_id": TASK_ID,
        "stage_id": sid,
        "task_authority_id": AUTHORITY_ID,
        "decision_id": f"decision-{sid}-{decision_type}",
        "decision_type": decision_type,
        "authorized_scope": [RUN],
        "task_nonce_commitment": commitment(_TASK_DIGEST),
        "nonce_commitment": commitment(_EVENT_DIGEST),
    }
    record.update(extra)
    return record


# Which basis kinds each stage may use, from the profile contract's
# feasibility_basis_contract. Stages 06 and 07 accept only measurement or test
# results; the earlier stages accept an existing artifact reference.
BASIS_KIND = {sid: ("measurement_receipt_ref" if sid in STAGES[5:] else "existing_artifact_ref")
              for sid in STAGES}

# The profile contract the fixture repository carries, cut down to what the
# publication path reads from it. It is written into the synthetic repository
# because the gate reads it at the candidate: it states what that candidate's own
# stages must satisfy, so it is evidence the push carries rather than a rule the
# checkout supplies. A governed run whose repository has no contract is refused,
# which is the right answer.
PROFILE_CONTRACT_PATH = "01_os/03_mechanisms/stage_collaborative_deliberation/阶段profile契约_v1.yml"
PROFILE_CONTRACT_DOC = {
    "common_task_stage_model": {
        "feasibility_basis_contract": {
            "shape": {"value": "substantive", "basis": {"kind": "one_of_the_stage_kinds",
                                                        "ref": "nonempty_string"}},
            "bare_string_accepted": False,
            "prohibited_basis_kinds": ["Human_confirmed", "Human_approved", "Human_authorized",
                                       "authority_reference", "decision_ref"],
            "basis_kinds_by_stage": {sid: [BASIS_KIND[sid]] for sid in STAGES},
        }
    }
}


# The seven profiles this synthetic repository declares. Each names the
# stage-specific fields its stage must carry, and the mechanism composes
# effective_current_stage_model = common fields + these. Two per stage rather than
# one, so a model that happens to carry a single element cannot pass by accident.
PROFILE_SET_PATH = "01_os/03_mechanisms/stage_collaborative_deliberation/阶段profiles_v1.yml"
STAGE_FIELDS = {sid: [f"{sid}_element_a", f"{sid}_element_b"] for sid in STAGES}
PROFILE_SET_DOC = {
    "profiles": [
        {"profile_id": sid,
         "profile_version": 1,
         "required_model_fields": STAGE_FIELDS[sid],
         "mechanism_ref": "01_os/03_mechanisms/stage_collaborative_deliberation"}
        for sid in STAGES
    ]
}


def stage_elements(sid: str) -> dict:
    """One disposition per field this stage's profile requires.

    represented_with_supported_value carries a value; the mechanism also accepts
    an explicit irrelevance with a reason and scope. A missing field, or a
    disposition it does not recognise, is refused.
    """
    return {field: {"disposition": "represented_with_supported_value",
                    "value": f"{field} for the fixture run"}
            for field in STAGE_FIELDS[sid]}


def verification_doc(sid: str, output_commit: str) -> dict:
    """Exactly the five fields the contract names, and status verified.

    verification_record_fields and verification_record_values in the profile
    contract. The mechanism compares the whole document, so an extra key or a
    different status is a refusal - which is the point: a record reading
    status: failed used to publish as an accepted stage.
    """
    return {"schema_version": "stage_verification_result.v1",
            "candidate": output_commit,
            "task_id": TASK_ID,
            "stage_id": sid,
            "status": "verified"}


def current_model(sid: str, baseline: str) -> dict:
    """A complete Current Model: every common field present with a disposition.

    none_material is a real answer and the mechanism accepts it; a missing key or
    a null value is not, and it refuses those. The model cannot name its own
    commit - it is the content of that commit - so the version it carries is the
    baseline it was authored against.
    """
    return {
        # A model is valid for a task and a stage, not in the abstract. Without
        # these two a stage 01 control could bind a model whose content said
        # stage 02 and publish.
        "task_id": TASK_ID,
        "stage_id": sid,
        "stage_specific_model_elements": stage_elements(sid),
        "problem_or_objective": f"establish the {sid} artifact for the fixture run",
        "why_this_stage_is_needed_now": f"{sid} has no accepted artifact in this run yet",
        "Human_intent_understanding": "exercise the publication gate end to end",
        "current_baseline_and_inputs": baseline,
        "proposed_method_or_solution": f"author the {sid} artifact and bind it exactly",
        # A bare string satisfies completeness and nothing else. The contract asks
        # for a basis the world could falsify, and names which kinds each stage may
        # use; Human approval is authority, not evidence, and is prohibited here.
        "feasibility_support": {
            "value": "the preceding stage completed and its output is bound",
            "basis": {"kind": BASIS_KIND[sid], "ref": f"{RUN}/{sid}/output.yml"},
        },
        "expected_output": f"one {sid} artifact with exact stage_control bindings",
        "verification_or_acceptance_method": "independent verification record at its own commit",
        "current_exact_model_version": baseline,
        "constraints_and_dependencies": "none_material",
        "assumptions_risks_alternatives_unknowns": "none_material",
        "downstream_impact": "none_material",
        "open_load_bearing_items": [],
    }


def stage_receipt(sid: str, candidate_version: str) -> dict:
    """A base stage receipt the mechanism will accept.

    Twenty required fields, both gates passing, a zero validator exit code, no
    missing or stale paths, and an exact candidate version. The mechanism checks
    all of that; a receipt short of it is refused with 17 or 12.
    """
    return {
        # 加载与receipt契约_v1 names this identifier. The fixture said
        # "stage_receipt.v1", which is a different schema, and passed: the object
        # existed at the declared blob and nobody asked what schema it was.
        "receipt_schema_version": "stage_collaborative_deliberation.stage_receipt.v1",
        "mechanism_version": 1,
        "active_contract_version": 1,
        "boot_manifest_version": 1,
        "registry_version": 1,
        "loader_version": 1,
        # resolve_profile parses the part after @ as an integer version, so this
        # is "@1" and not "@v1". A reference that does not resolve means the
        # stage's obligations are unknown, which the mechanism refuses.
        "profile_id_and_version": f"{sid}@1",
        "loaded_paths": [f"{RUN}/{sid}/model.yml"],
        "missing_partial_or_stale_paths": [],
        "trigger_evaluation_result_ref": f"{RUN}/{sid}/model.yml",
        "activation_mode_or_dormant_reason": "active",
        "main_mechanism_ref": ["01_os/03_mechanisms/stage_collaborative_deliberation"],
        "detail_granularity_evaluation_result": "sufficient",
        "open_detail_divergence_event_refs": [],
        "deferred_detail_record_refs": [],
        "gate_results": {"start": "pass", "completion": "pass"},
        "validator_mode_and_exit_code": {"mode": "instance", "exit_code": 0},
        "exact_candidate_version": candidate_version,
        "created_by_actor_ref": "gate-fixture",
        "created_at": "2026-09-13T00:00:00Z",
    }


def write(repo: Path, rel: str, data) -> str:
    """Write a file and return the blob sha git will give it.

    hash-object is asked for the sha rather than computing it here: the test is
    about the gate's reading of git, not about reimplementing git's hashing.
    """
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    text = data if isinstance(data, str) else yaml.safe_dump(data, allow_unicode=True,
                                                             sort_keys=False)
    path.write_text(text, encoding="utf-8", newline="\n")
    return git(repo, "hash-object", rel)


def commit(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "--allow-empty", "-m", message)
    return git(repo, "rev-parse", "HEAD")


class Chain:
    """A complete, valid five-node chain for seven stages.

    Per stage the commits are, in order:
        M   the current model is published
        P   the plan acceptance is published, naming the model blob at M
        W   the stage output and the artifact are published
        C   the completion acceptance is published, naming W
    plus one evidence commit after W holding the verification record, because a
    candidate must never embed its own sha.
    """

    def __init__(self, root: Path, plan_mutators: dict | None = None,
                 completion_mutators: dict | None = None,
                 model_mutators: dict | None = None,
                 receipt_mutators: dict | None = None,
                 verification_mutators: dict | None = None,
                 profile_set: dict | None = None,
                 packet_mutator=None):
        """The mutators change a stage's acceptance record as it is written.

        Structural cases have to be built into the chain, not edited afterwards.
        The gate reads each record at the commit that carries it, so rewriting a
        file at the branch head leaves the accepted record untouched and the gate
        correctly sees nothing. Changing what was accepted means changing that
        commit, which rewrites history.

        Both halves take mutators because the gate judges both, and for a while
        only the plan half could be varied. A chain with a well-formed plan record
        and an untouched completion record was refused on the completion record -
        correct, but it meant no negative could be aimed at one half while the
        other was known good.
        """
        plan_mutators = plan_mutators or {}
        completion_mutators = completion_mutators or {}
        # The model, the receipt and the verification document each live at their
        # own commit, so a case that changes one has to change it as the chain is
        # built. Editing any of them afterwards leaves the published object alone
        # and the gate correctly sees nothing.
        model_mutators = model_mutators or {}
        receipt_mutators = receipt_mutators or {}
        verification_mutators = verification_mutators or {}
        self.repo = root / "repo"
        self.repo.mkdir(parents=True)
        git(self.repo, "init", "-b", "fixture")
        git(self.repo, "config", "user.name", "Synthetic gate fixture")
        git(self.repo, "config", "user.email", "gate-fixture@example.invalid")
        write(self.repo, "README.md", "fixture\n")
        # The gate reads the profile contract at the candidate, so the repository
        # being judged has to carry it. A governed run in a repository without one
        # is refused rather than judged against whatever the checkout happens to
        # have.
        write(self.repo, PROFILE_CONTRACT_PATH, PROFILE_CONTRACT_DOC)
        write(self.repo, PROFILE_SET_PATH, PROFILE_SET_DOC if profile_set is None else profile_set)
        policy_path = "01_os/05_registry/repository_publisher_authority_v1.yml"
        write(self.repo, policy_path,
              (HERE.parents[3] / policy_path).read_text(encoding="utf-8"))
        self.boundary = commit(self.repo, "boundary")
        # Synthetic scope only: allow canonical schemas copied by the runner
        # integration fixture as well as this run. No production authority is made.
        self.packet = {
            "task_id": TASK_ID, "branch": "fixture", "exact_base_sha": self.boundary,
            "allowed_changed_paths": ["01_os/**"],
            "required_tests": ["synthetic-gate-check"], "prohibitions": [],
            "stage_actions": [
                {"action_id": f"act-{i + 1}", "kind": "ordinary_task_work",
                 "target": "refs/heads/fixture", "expected_target_head": None,
                 "stage_ids": [sid], "paths": [RUN], "confirmation": None}
                for i, sid in enumerate(STAGES)],
        }
        if packet_mutator is not None:
            packet_mutator(self.packet)
        packet_path = f"{RUN}/task_packet.yml"
        self.packet_ref = {"path": packet_path, "blob_sha": write(
            self.repo, packet_path, {"task_packet": self.packet})}
        commit(self.repo, "synthetic task scope")
        self.stages: dict[str, dict] = {}
        self.controls: dict[str, dict] = {}
        self.receipts: dict[str, dict] = {}
        self.embedded: dict[str, dict] = {}
        prev_c: str | None = None

        for index, sid in enumerate(STAGES):
            d = f"{RUN}/{sid}"
            baseline = prev_c or self.boundary
            # The full twenty-field receipt is its own artifact, published at M and
            # reached through stage_control.deliberation_receipt_ref. The stage
            # artifact embeds only the binding fields. Keeping a second full copy
            # inside the artifact would be two sources for one object, and while
            # the gate read that copy the declared ref was never resolved at all.
            receipt = stage_receipt(sid, baseline)
            if sid in receipt_mutators:
                receipt_mutators[sid](receipt, self)
            receipt_blob = write(self.repo, f"{d}/receipt.yml", receipt)
            embedded = {key: receipt[key] for key in
                        ("profile_id_and_version", "exact_candidate_version")}
            embedded["route"] = "active"
            model = current_model(sid, baseline)
            if sid in model_mutators:
                model_mutators[sid](model, self)
            model_blob = write(self.repo, f"{d}/model.yml", model)
            m = commit(self.repo, f"{sid} model")

            # exact_model_version names M, which exists by now. A record written at
            # P can name the commit it accepted; it could not name its own.
            plan_record = accepted(sid, PLAN_DECISION,
                                   exact_model_version=m, accepts=model_blob)
            if prev_c is not None:
                # The binding lives in the record the Human accepted, where the
                # blob sha covers it, not in a summary field of the artifact.
                plan_record["predecessor_completion_commit"] = prev_c
            if sid in plan_mutators:
                plan_mutators[sid](plan_record, self)
            plan_blob = write(self.repo, f"{d}/plan_acceptance.yml", plan_record)
            p = commit(self.repo, f"{sid} plan acceptance")

            out_blob = write(self.repo, f"{d}/output.yml",
                             {"stage_id": sid, "result": f"output of {sid}"})
            control = {
                "action_id": f"act-{index + 1}",
                "current_model_ref": {"path": f"{d}/model.yml", "blob_sha": model_blob},
                # Points at the receipt, not at the model. It pointed at model.yml
                # and passed, because nothing resolved it.
                "deliberation_receipt_ref": {"path": f"{d}/receipt.yml",
                                             "blob_sha": receipt_blob},
                "plan_acceptance": {
                    "commit": p,
                    "path": f"{d}/plan_acceptance.yml",
                    "blob_sha": plan_blob,
                    "accepted_model_commit": m,
                    "accepted_model_path": f"{d}/model.yml",
                    "accepted_model_blob_sha": model_blob,
                },
            }
            write(self.repo, f"{RUN}/{FILES[index]}",
                  {"stage_id": sid, "stage_control": control,
                   "deliberation_receipt": embedded})
            w = commit(self.repo, f"{sid} work")

            ver_doc = verification_doc(sid, w)
            if sid in verification_mutators:
                verification_mutators[sid](ver_doc, self)
            ver_blob = write(self.repo, f"{d}/verification.yml", ver_doc)
            ver_commit = commit(self.repo, f"{sid} verification evidence")

            # The completion record names the output commit it accepted and the
            # verification evidence it rests on, and carries the closure fields.
            # A plan record copied here is refused on its decision type alone.
            comp_record = accepted(
                sid, COMPLETION_DECISION,
                actual_result=f"Produced the synthetic {sid} output and recorded verification.",
                bound_output_version=w,
                verification_result={"commit": ver_commit,
                                     "path": f"{d}/verification.yml",
                                     "blob_sha": ver_blob},
                plan_vs_actual_delta="none_material",
                material_deviation="none_material",
                residual_risk="none_material",
                downstream_baseline=w,
            )
            if sid in completion_mutators:
                completion_mutators[sid](comp_record, self)
            comp_blob = write(self.repo, f"{d}/completion_acceptance.yml", comp_record)
            control["completion_acceptance"] = {
                "path": f"{d}/completion_acceptance.yml",
                "blob_sha": comp_blob,
                "bound_output_version": w,
                "output_path": f"{d}/output.yml",
                "output_blob_sha": out_blob,
                "verification_result": {"commit": ver_commit,
                                        "path": f"{d}/verification.yml",
                                        "blob_sha": ver_blob},
            }
            write(self.repo, f"{RUN}/{FILES[index]}",
                  {"stage_id": sid, "stage_control": control,
                   "deliberation_receipt": embedded})
            c = commit(self.repo, f"{sid} completion acceptance")

            self.stages[sid] = {"m": m, "p": p, "w": w, "c": c}
            self.controls[sid] = control
            self.receipts[sid] = receipt
            self.embedded[sid] = embedded
            prev_c = c

        write(self.repo, f"{RUN}/manifest.yml",
              {"artifacts": [{"stage_id": s, "path": f} for s, f in zip(STAGES, FILES)]})
        write(self.repo, f"{RUN}/run.yml",
              {"task_id": TASK_ID, "base_sha": self.boundary_child(),
               "task_packet_ref": self.packet_ref,
               "final_stage_completion_commit": prev_c})
        self.head = commit(self.repo, "run identity")

    def boundary_child(self) -> str:
        return self.stages[STAGES[0]]["m"] if self.stages else self.boundary

    def rewrite_artifact(self, sid: str, mutate) -> None:
        index = STAGES.index(sid)
        control = json_round(self.controls[sid])
        mutate(control)
        # The receipt travels with the artifact. Rewriting one without it would
        # make every structural mutation fail on a missing receipt instead of on
        # the invariant the case is actually about.
        write(self.repo, f"{RUN}/{FILES[index]}",
              {"stage_id": sid, "stage_control": control,
               "deliberation_receipt": self.embedded[sid]})
        self.head = commit(self.repo, f"mutate {sid}")

    def rewrite_run(self, mutate) -> None:
        doc = yaml.safe_load((self.repo / RUN / "run.yml").read_text(encoding="utf-8"))
        mutate(doc)
        write(self.repo, f"{RUN}/run.yml", doc)
        self.head = commit(self.repo, "mutate run identity")

    def run_gate(self, boundary: str | None = None,
                 base: str | None = None) -> tuple[int, list[str]]:
        cmd = [sys.executable, str(GATE), "--repo-root", str(self.repo),
               "--candidate", self.head, "--json"]
        if boundary:
            cmd += ["--boundary", boundary]
        if base:
            cmd += ["--base", base]
        proc = subprocess.run(cmd, capture_output=True, check=False)
        payload = json.loads(proc.stdout.decode("utf-8"))
        return proc.returncode, payload["findings"]


def json_round(value):
    return json.loads(json.dumps(value))


class GateCases(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="gate-fixture-"))
        self.chain = Chain(self.tmp)

    def tearDown(self) -> None:
        discard(self.tmp)

    def assertRefused(self, code: int, findings: list[str], expect_code: int, expect: str) -> None:
        joined = " | ".join(findings)
        self.assertEqual(code, expect_code, f"expected exit {expect_code}, got {code}: {joined}")
        self.assertIn(expect, joined, f"refused, but not for the named reason: {joined}")

    # -- the valid chain ----------------------------------------------------

    def test_valid_chain_passes(self):
        code, findings = self.chain.run_gate()
        self.assertEqual(code, 0, " | ".join(findings))

    def test_ordinary_push_with_no_governed_run_passes(self):
        empty = Path(tempfile.mkdtemp(prefix="gate-empty-"))
        try:
            repo = empty / "repo"
            repo.mkdir(parents=True)
            git(repo, "init", "-b", "fixture")
            git(repo, "config", "user.name", "n")
            git(repo, "config", "user.email", "e@example.invalid")
            write(repo, "README.md", "no runs here\n")
            head = commit(repo, "only content")
            proc = subprocess.run([sys.executable, str(GATE), "--repo-root", str(repo),
                                   "--candidate", head, "--json"],
                                  capture_output=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stdout.decode("utf-8"))
        finally:
            discard(empty)

    # -- one mutated invariant per case -------------------------------------

    def test_equality_edge_is_refused(self):
        sid = STAGES[2]
        same = self.chain.stages[sid]["p"]
        self.chain.rewrite_artifact(
            sid, lambda c: c["plan_acceptance"].__setitem__("accepted_model_commit", same))
        code, findings = self.chain.run_gate()
        self.assertRefused(code, findings, 13, "not strict ancestry")

    def test_wrong_commit_is_refused(self):
        sid = STAGES[3]
        other = self.chain.stages[STAGES[5]]["p"]
        self.chain.rewrite_artifact(
            sid, lambda c: c["plan_acceptance"].__setitem__("commit", other))
        code, findings = self.chain.run_gate()
        self.assertNotEqual(code, 0)
        self.assertTrue(any("plan acceptance at P" in f or "not strict ancestry" in f
                            for f in findings), " | ".join(findings))

    def test_right_commit_wrong_blob_is_refused(self):
        sid = STAGES[1]
        bad = "0" * 40
        self.chain.rewrite_artifact(
            sid, lambda c: c["plan_acceptance"].__setitem__("blob_sha", bad))
        code, findings = self.chain.run_gate()
        self.assertRefused(code, findings, 15, "plan acceptance at P")

    def test_right_blob_wrong_path_is_refused(self):
        """Refused at reference resolution, before separation is reached.

        The reason moved when the predecessor binding moved into the accepted
        record: the gate now has to read that record while collecting nodes, so an
        unresolvable path fails there rather than later at the blob comparison.
        Both are correct refusals; this asserts the one that actually fires.
        """
        sid = STAGES[1]
        self.chain.rewrite_artifact(
            sid, lambda c: c["plan_acceptance"].__setitem__("path", f"{RUN}/nope.yml"))
        code, findings = self.chain.run_gate()
        self.assertRefused(code, findings, 11,
                           "plan acceptance record is absent or unreadable at its own commit")

    def test_output_already_present_at_P_is_refused(self):
        """S9b. An output that existed when it was authorised was not authorised."""
        sid = STAGES[4]
        earlier = self.chain.stages[sid]["w"]
        self.chain.rewrite_artifact(
            sid, lambda c: c["completion_acceptance"].__setitem__("output_path",
                                                                  f"{RUN}/{FILES[0]}"))
        code, findings = self.chain.run_gate()
        self.assertNotEqual(code, 0, f"{earlier} | " + " | ".join(findings))

    def test_completion_acceptance_present_at_W_is_refused(self):
        """S9c. A completion acceptance written with the output accepts nothing."""
        sid = STAGES[2]
        d = f"{RUN}/{sid}"
        blob = self.chain.controls[sid]["completion_acceptance"]["blob_sha"]
        self.chain.rewrite_artifact(
            sid, lambda c: c["completion_acceptance"].update(
                {"path": f"{d}/model.yml",
                 "blob_sha": self.chain.controls[sid]["plan_acceptance"]["accepted_model_blob_sha"]}))
        code, findings = self.chain.run_gate()
        self.assertNotEqual(code, 0, f"{blob} | " + " | ".join(findings))

    def test_verification_inside_the_output_commit_is_refused(self):
        sid = STAGES[5]
        w = self.chain.stages[sid]["w"]
        self.chain.rewrite_artifact(
            sid, lambda c: c["completion_acceptance"]["verification_result"].__setitem__("commit", w))
        code, findings = self.chain.run_gate()
        self.assertRefused(code, findings, 14, "must not live in the output commit")

    def test_stage_one_naming_a_predecessor_is_refused(self):
        def name_one(record, chain):
            record["predecessor_completion_commit"] = chain.boundary
        chain = Chain(Path(tempfile.mkdtemp(prefix="gate-mut-")),
                      {STAGES[0]: name_one})
        try:
            code, findings = chain.run_gate()
            self.assertRefused(code, findings, 11, "must not name a predecessor")
        finally:
            discard(chain.repo.parent)

    def test_stage_two_without_a_predecessor_binding_is_refused(self):
        def drop(record, chain):
            record.pop("predecessor_completion_commit", None)
        chain = Chain(Path(tempfile.mkdtemp(prefix="gate-mut-")),
                      {STAGES[1]: drop})
        try:
            code, findings = chain.run_gate()
            self.assertRefused(code, findings, 11, "must name predecessor_completion_commit")
        finally:
            discard(chain.repo.parent)

    def test_wrong_predecessor_breaks_the_chain(self):
        """A record naming the wrong completion commit fails S9c.

        The named commit does not carry that stage's completion acceptance blob,
        so the chain does not close. Nothing here depends on a summary field being
        consistent with the record: the binding is the record.
        """
        def wrong(record, chain):
            if chain.stages:
                record["predecessor_completion_commit"] = chain.boundary
        chain = Chain(Path(tempfile.mkdtemp(prefix="gate-mut-")),
                      {STAGES[4]: wrong})
        try:
            code, findings = chain.run_gate()
            self.assertNotEqual(code, 0, " | ".join(findings))
        finally:
            discard(chain.repo.parent)

    # -- run identity -------------------------------------------------------

    def test_missing_final_stage_completion_commit_is_refused(self):
        self.chain.rewrite_run(lambda d: d.pop("final_stage_completion_commit"))
        code, findings = self.chain.run_gate()
        self.assertRefused(code, findings, 11, "must state final_stage_completion_commit")

    def test_malformed_final_stage_completion_commit_is_refused(self):
        self.chain.rewrite_run(lambda d: d.__setitem__("final_stage_completion_commit", "nope"))
        code, findings = self.chain.run_gate()
        self.assertRefused(code, findings, 11, "must state final_stage_completion_commit")

    def test_well_formed_but_wrong_final_commit_is_refused(self):
        wrong = self.chain.stages[STAGES[0]]["c"]
        self.chain.rewrite_run(
            lambda d: d.__setitem__("final_stage_completion_commit", wrong))
        code, findings = self.chain.run_gate()
        self.assertNotEqual(code, 0, " | ".join(findings))

    # -- governance transition ----------------------------------------------
    #
    # These two cases look alike and mean opposite things. A run that was never a
    # seven-stage run is not applicable. A run that was governed in the published
    # state and is not at the candidate has dropped its identity, and must be
    # refused: otherwise a candidate un-governs itself by deleting one file.
    #
    # An earlier version of this file had one test, named
    # test_missing_manifest_makes_the_run_not_governed, which built a fully
    # governed chain, deleted the manifest and asserted exit 0. It encoded the
    # escape as the expected behaviour.

    def test_never_governed_run_without_a_manifest_is_not_applicable(self):
        no_manifest = f"{RUN}-ordinary"
        write(self.chain.repo, f"{no_manifest}/notes.md", "an ordinary run\n")
        self.chain.head = commit(self.chain.repo, "an ordinary run directory")
        code, findings = self.chain.run_gate()
        self.assertEqual(code, 0, " | ".join(findings))

    def test_governed_run_that_drops_its_manifest_is_refused(self):
        base = self.chain.head
        (self.chain.repo / RUN / "manifest.yml").unlink()
        self.chain.head = commit(self.chain.repo, "drop manifest")
        code, findings = self.chain.run_gate(base=base)
        self.assertRefused(code, findings, 16, "seven-stage manifest is gone")

    def test_governed_run_that_drops_its_run_yml_is_refused(self):
        base = self.chain.head
        (self.chain.repo / RUN / "run.yml").unlink()
        self.chain.head = commit(self.chain.repo, "drop run identity")
        code, findings = self.chain.run_gate(base=base)
        self.assertRefused(code, findings, 16, "identity is missing or malformed")

    def test_governed_run_deleted_outright_is_refused(self):
        base = self.chain.head
        shutil.rmtree(self.chain.repo / RUN)
        self.chain.head = commit(self.chain.repo, "delete the run")
        code, findings = self.chain.run_gate(base=base)
        self.assertRefused(code, findings, 16, "run directory is gone")

    def test_first_push_has_no_transition_to_check_and_that_is_not_a_hole(self):
        """On a new branch the local_git old sha is all-zero and there is no base.

        Escaping governance by deleting a declaration needs a published state to
        escape from, and on a first push this run was never published, so nothing
        is lost. The candidate is judged on its own by the boundary and the chain.

        The all-zero sha is not silently treated as a commit, and neither master
        nor a merge-base is substituted for it.

        A draft used the run's own base_sha as a fallback anchor here. It could
        never fire, because base_sha names where the task started, which is before
        the run existed. This case now records why there is nothing to check
        rather than pretending something was checked.
        """
        (self.chain.repo / RUN / "manifest.yml").unlink()
        self.chain.head = commit(self.chain.repo, "drop manifest on a new branch")
        code, findings = self.chain.run_gate()
        self.assertEqual(code, 0, " | ".join(findings))
        self.assertTrue(any("not seven-stage runs" in f for f in findings),
                        " | ".join(findings))

    def test_proof_a_convenient_ancestor_narrows_the_history_the_gate_can_see(self):
        """CAPABILITY BOUNDARY PROOF, not a guarantee.

        This case passes on purpose. It proves that the gate cannot authenticate a
        caller-supplied base; it does not prove the gate prevents this bypass. Read
        it as the reason the binding belongs to the caller, never as coverage.

        The gate cannot tell a real old head from any other ancestor.

        A base picked from early in the branch is still a strict ancestor, and the
        run was not yet governed there, so the removal goes unseen. This is not a
        gate defect to fix inside the gate: it is why binding the base to the
        transport's real old head is the caller's responsibility, and why a caller
        that invents one has produced a false receipt.
        """
        convenient = self.chain.boundary
        (self.chain.repo / RUN / "manifest.yml").unlink()
        self.chain.head = commit(self.chain.repo, "drop manifest")
        code, _ = self.chain.run_gate(base=convenient)
        self.assertEqual(code, 0, "documents the boundary of what --base can prove")

    def test_base_must_strictly_precede_the_candidate(self):
        code, findings = self.chain.run_gate(base=self.chain.head)
        self.assertRefused(code, findings, 10, "must strictly precede")

    def test_governed_run_that_corrupts_its_base_is_refused(self):
        base = self.chain.head
        self.chain.rewrite_run(lambda d: d.__setitem__("base_sha", "not-a-sha"))
        code, findings = self.chain.run_gate(boundary=self.chain.boundary, base=base)
        self.assertRefused(code, findings, 16, "does not stop being governed")

    def test_malformed_base_sha_refuses_rather_than_exempting(self):
        """GD-10. Unable to place a run is not the same as an exempt run."""
        self.chain.rewrite_run(lambda d: d.__setitem__("base_sha", "not-a-sha"))
        code, findings = self.chain.run_gate(boundary=self.chain.boundary)
        self.assertRefused(code, findings, 11, "exemption cannot be established")

    def test_missing_run_yml_with_a_manifest_is_refused_without_a_base(self):
        """Even with no published state to compare against, a manifest without an
        identity is refused rather than skipped."""
        (self.chain.repo / RUN / "run.yml").unlink()
        self.chain.head = commit(self.chain.repo, "drop run identity")
        code, findings = self.chain.run_gate()
        self.assertRefused(code, findings, 11, "no readable run.yml")


class AcceptanceCases(unittest.TestCase):
    """Both acceptance records are opened, and the mechanism judges them.

    Before these existed the gate proved that a run's seven stages chained by
    strict ancestry, that each phase added its own artifact, and that a
    verification record sat where it was declared - and never opened the two
    records the whole arrangement is about. A chain whose plan acceptance read
    actor_class: executor with Human_disposition: rejected passed, reported as
    "seven stages chained and separated". The mechanism refused that identical
    record with exit 15. Topology was measured; acceptance was declared.

    Worse, the fixture's own records were no better: {stage_id, accepts} carries
    nothing to accept, and the mechanism refused it with the same 15. The
    baseline was not a valid chain with one bad case next to it - the whole
    population was unjudgeable, and a gate that never looked could not tell.

    Every refusal here asserts exit 17 and which half was refused, so a refusal
    for the wrong cause cannot pass as a refusal.
    """

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="gate-accept-"))

    def tearDown(self) -> None:
        discard(self.tmp)

    def chain(self, plan=None, completion=None, model=None, receipt=None,
              verification=None) -> Chain:
        """A chain whose first stage carries the mutation under test.

        A mutation is a mapping to merge, or a callable for cases that must remove
        a field rather than change one. Omission is its own attack: the identity
        checks used to fire only when both sides were present, so a record that
        simply left task_id out bound to nothing and passed.
        """
        def at_first(mutation):
            if callable(mutation):
                return {STAGES[0]: lambda record, _: mutation(record)}
            return {STAGES[0]: lambda record, _: record.update(mutation)}
        return Chain(
            self.tmp,
            plan_mutators=at_first(plan) if plan is not None else None,
            completion_mutators=at_first(completion) if completion is not None else None,
            model_mutators=at_first(model) if model is not None else None,
            receipt_mutators=at_first(receipt) if receipt is not None else None,
            verification_mutators=at_first(verification) if verification is not None else None)

    def assertMechanismRefused(self, code: int, findings: list[str], half: str,
                               reason: str, owner_code: int | None = None) -> None:
        """Exit 17, the right half, and the mechanism's own diagnosis.

        Asserting only 17 and the half was too weak: two different defects in the
        same record satisfied the same assertion, so a case could pass while
        proving something other than what it claimed. The reason string comes from
        the mechanism, not from the gate.
        """
        joined = " | ".join(findings)
        self.assertEqual(code, 17, f"expected exit 17, got {code}: {joined}")
        self.assertIn(f"{half} acceptance was refused by the deliberation mechanism",
                      joined, joined)
        self.assertIn(reason, joined, f"refused, but not for the named reason: {joined}")
        if owner_code is not None:
            self.assertIn(f"exit {owner_code})", joined,
                          f"refused with a different mechanism code: {joined}")

    # -- the positive control ------------------------------------------------

    def test_wellformed_chain_passes(self):
        """Without this, a gate that refused everything would look like a gate."""
        code, findings = self.chain().run_gate()
        self.assertEqual(code, 0, " | ".join(findings))

    # -- who the record says accepted ----------------------------------------

    def test_plan_record_from_an_executor_is_refused(self):
        code, findings = self.chain(plan={"actor_class": "executor"}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "common_Human_record", 15)

    def test_plan_record_with_a_rejected_disposition_is_refused(self):
        code, findings = self.chain(plan={"Human_disposition": "rejected"}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "common_Human_record", 15)

    def test_plan_record_that_is_not_explicit_is_refused(self):
        code, findings = self.chain(plan={"explicit": False}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "common_Human_record", 14)

    def test_plan_record_without_foreground_provenance_is_refused(self):
        code, findings = self.chain(plan={"provenance": None}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "common_Human_record", 15)

    def test_stale_plan_record_is_refused(self):
        code, findings = self.chain(plan={"stale": True}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "common_Human_record", 12)

    def test_synthetic_marked_record_is_refused(self):
        """A fixture must not be able to manufacture an acceptance.

        This is the guard on the fabricated approvals above. The mechanism refuses
        any record carrying synthetic_test_record outside a synthetic authority
        context, and the gate has no flag that could supply one - offering it
        would be a production bypass wearing a test's clothes.
        """
        code, findings = self.chain(plan={"synthetic_test_record": True}).run_gate()
        self.assertMechanismRefused(code, findings, "plan",
                                    "synthetic_record_outside_synthetic_context", 15)

    # -- the record must carry a commitment at all ---------------------------

    def test_record_without_a_commitment_is_refused(self):
        """"Challengeable" is a claim about a commitment nobody had checked.

        Until this, the publication path validated the common Human fields and
        stopped. A record with no nonce_commitment at all passed, while the
        registry described it as challengeable. Structure is the challengeable
        part; recomputing the digest is the interactive challenge and does not
        run here.
        """
        code, findings = self.chain(
            plan=lambda r: r.pop("nonce_commitment")).run_gate()
        self.assertMechanismRefused(code, findings, "plan",
                                    "authority_record_commitments", 15)

    def test_record_with_a_malformed_commitment_digest_is_refused(self):
        code, findings = self.chain(
            plan={"nonce_commitment": commitment("not-hex" + "0" * 57)}).run_gate()
        self.assertMechanismRefused(code, findings, "plan",
                                    "authority_record_commitments", 15)

    # -- identity, including by omission -------------------------------------

    def test_record_naming_another_stage_is_refused(self):
        code, findings = self.chain(plan={"stage_id": STAGES[4]}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "stage_id_mismatch", 15)

    def test_record_naming_another_task_is_refused(self):
        code, findings = self.chain(plan={"task_id": "some-other-task"}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "task_id_mismatch", 15)

    def test_record_omitting_task_id_is_refused(self):
        """Bypass 1. The run declares a task; the record simply left it out.

        The identity comparisons used to fire only when both sides were present,
        so omission bound the record to nothing and passed.
        """
        code, findings = self.chain(plan=lambda r: r.pop("task_id")).run_gate()
        self.assertMechanismRefused(code, findings, "plan",
                                    "task_id_absent_from_record", 15)

    def test_record_omitting_stage_id_is_refused(self):
        code, findings = self.chain(plan=lambda r: r.pop("stage_id")).run_gate()
        self.assertMechanismRefused(code, findings, "plan",
                                    "stage_id_absent_from_record", 15)

    # -- what the plan record accepted ---------------------------------------

    def test_plan_record_naming_a_stale_model_version_is_refused(self):
        """Bypass 2. The record accepts a model other than the one bound.

        stage_control binds the real current model; the record names an older
        commit. Nothing compared the two, so it passed.
        """
        chain = self.chain(plan=lambda r: r.update({"exact_model_version": r["accepts"]}))
        code, findings = chain.run_gate()
        self.assertMechanismRefused(
            code, findings, "plan",
            "plan_record_model_version_is_not_the_accepted_model_commit", 13)

    def test_control_accepting_a_model_it_did_not_bind_is_refused(self):
        """The same gap from the control side rather than the record side."""
        chain = self.chain()
        sid = STAGES[0]
        other = chain.controls[STAGES[3]]["current_model_ref"]["blob_sha"]
        chain.rewrite_artifact(
            sid, lambda c: c["plan_acceptance"].__setitem__("accepted_model_blob_sha", other))
        code, findings = chain.run_gate()
        joined = " | ".join(findings)
        self.assertNotEqual(code, 0, joined)

    # -- what the completion record accepted ---------------------------------

    def test_completion_record_is_judged_independently(self):
        """A good plan record does not vouch for the completion record."""
        code, findings = self.chain(completion={"actor_class": "executor"}).run_gate()
        self.assertMechanismRefused(code, findings, "completion", "common_Human_record", 15)

    def test_synthetic_marked_completion_record_is_refused(self):
        code, findings = self.chain(completion={"synthetic_test_record": True}).run_gate()
        self.assertMechanismRefused(code, findings, "completion",
                                    "synthetic_record_outside_synthetic_context", 15)

    def test_plan_record_copied_into_the_completion_slot_is_refused(self):
        """Bypass 3. The same decision filed twice, accepting nothing new.

        A completion acceptance that is a copy of the plan acceptance accepts no
        output and rests on no verification evidence. Nothing distinguished the
        two decisions, so it passed. They are different decision types, and the
        mechanism refuses the substitution on that alone.
        """
        def as_plan(record):
            record.clear()
            record.update(accepted(STAGES[0], PLAN_DECISION,
                                   exact_model_version="0" * 40, accepts="0" * 40))
        code, findings = self.chain(completion=as_plan).run_gate()
        self.assertMechanismRefused(code, findings, "completion",
                                    "decision_type_is_not_a_completion_acceptance", 15)

    def test_completion_record_not_binding_the_stage_output_is_refused(self):
        chain = self.chain(completion={"bound_output_version": "0" * 40})
        code, findings = chain.run_gate()
        self.assertMechanismRefused(
            code, findings, "completion",
            "completion_record_does_not_bind_the_stage_output_commit", 13)

    def test_completion_record_not_naming_the_verification_evidence_is_refused(self):
        chain = self.chain(completion={"verification_result": {
            "commit": "0" * 40, "path": "elsewhere.yml", "blob_sha": "0" * 40}})
        code, findings = chain.run_gate()
        self.assertMechanismRefused(
            code, findings, "completion",
            "completion_record_does_not_name_the_verification_evidence", 13)

    def test_control_declaring_another_stages_output_is_refused_by_ancestry(self):
        """What actually constrains the declared output, stated as it really is.

        A revision on 2026-09-13 added an acceptance check meant to catch a control
        declaring an output the stage never produced. It could never fire: the W
        node is derived from that same bound_output_version, so both sides of the
        comparison came from one field. It is gone, and no second source of W was
        introduced to prop it up.

        This records the true proposition instead. The declaration is still not
        free - strict ancestry refuses it, and that refusal has independent
        physical basis in the object graph rather than in a restated field.
        """
        chain = self.chain()
        sid = STAGES[0]
        elsewhere = chain.stages[STAGES[3]]["w"]
        self.assertNotEqual(elsewhere, chain.stages[sid]["w"])
        chain.rewrite_artifact(
            sid,
            lambda c: c["completion_acceptance"].__setitem__("bound_output_version", elsewhere))
        code, findings = chain.run_gate()
        joined = " | ".join(findings)
        self.assertEqual(code, 13, joined)
        self.assertIn("not strict ancestry", joined, joined)

    def test_completion_actual_result_missing_is_refused(self):
        code, findings = self.chain(completion=lambda r: r.pop("actual_result")).run_gate()
        self.assertMechanismRefused(code, findings, "completion", "actual_result_required", 14)

    def test_completion_boolean_actual_result_is_refused(self):
        code, findings = self.chain(completion={"actual_result": True}).run_gate()
        self.assertMechanismRefused(code, findings, "completion", "actual_result_required", 14)

    def test_completion_empty_risk_is_refused(self):
        code, findings = self.chain(completion={"residual_risk": []}).run_gate()
        self.assertMechanismRefused(code, findings, "completion", "closure_field_empty:residual_risk", 14)

    def test_completion_record_missing_a_closure_field_is_refused(self):
        code, findings = self.chain(
            completion=lambda r: r.pop("residual_risk")).run_gate()
        self.assertMechanismRefused(code, findings, "completion",
                                    "closure_field_absent:residual_risk", 14)

    # -- the model belongs to this task and this stage ------------------------

    def test_model_naming_another_task_is_refused(self):
        code, findings = self.chain(model={"task_id": "some-other-task"}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "model_task_mismatch", 13)

    def test_model_naming_another_stage_is_refused(self):
        """stage 01's control binding a model whose content says stage 02.

        The binding was exact - right path, right blob, right commit - and the
        model inside it belonged to a different stage. Everything the gate checked
        was true and the stage was still not this stage's.
        """
        code, findings = self.chain(model={"stage_id": STAGES[1]}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "model_stage_mismatch", 13)

    # -- the model satisfies this stage's profile, not just the common fields --

    def test_model_missing_a_stage_specific_required_field_is_refused(self):
        """effective_current_stage_model = common fields + this profile's fields.

        Validating only the common set lets any stage pass another stage's
        obligations, which is exactly what the publication path was doing.
        """
        def drop_one(model):
            del model["stage_specific_model_elements"][STAGE_FIELDS[STAGES[0]][1]]
        code, findings = self.chain(model=drop_one).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "effective_stage_model", 16)

    def test_model_with_no_stage_specific_surface_at_all_is_refused(self):
        code, findings = self.chain(
            model=lambda m: m.pop("stage_specific_model_elements")).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "effective_stage_model", 16)

    def test_element_with_an_unrecognised_disposition_is_refused(self):
        def bad_disposition(model):
            field = STAGE_FIELDS[STAGES[0]][0]
            model["stage_specific_model_elements"][field] = {"disposition": "looks_fine"}
        code, findings = self.chain(model=bad_disposition).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "effective_stage_model", 16)

    def test_receipt_naming_a_profile_that_does_not_resolve_is_refused(self):
        """An unidentified profile means the stage's obligations are unknown."""
        code, findings = self.chain(
            receipt={"profile_id_and_version": "workflow_stage_01_requirement_modeling@99"}
        ).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "effective_stage_model", 16)

    def test_receipt_naming_another_stages_profile_is_refused(self):
        """Stage 01 judged against stage 05's obligations is not stage 01 judged."""
        code, findings = self.chain(
            receipt={"profile_id_and_version": f"{STAGES[4]}@1"}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "effective_stage_model", 16)

    def test_wrong_profile_with_its_matching_fields_is_refused(self):
        """Changing both sides of the field check must not change stage identity."""
        def replace_elements(model):
            model["stage_specific_model_elements"] = stage_elements(STAGES[4])
        code, findings = self.chain(
            receipt={"profile_id_and_version": f"{STAGES[4]}@1"},
            model=replace_elements).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "effective_stage_model", 16)

    def test_boolean_solution_is_refused_through_gate(self):
        code, findings = self.chain(model={"proposed_method_or_solution": True}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "current_model_completeness", 16)

    def test_task_packet_reference_is_required(self):
        chain = self.chain()
        chain.rewrite_run(lambda doc: doc.pop("task_packet_ref", None))
        code, findings = chain.run_gate()
        self.assertEqual(code, 11, findings)
        self.assertIn("task_packet_ref", " | ".join(findings))

    def test_paths_come_from_each_selected_packet_action(self):
        def per_stage_paths(packet):
            for sid, action in zip(STAGES, packet["stage_actions"]):
                action["paths"] = [f"{RUN}/{sid}"]
        chain = Chain(self.tmp, packet_mutator=per_stage_paths)
        code, findings = chain.run_gate()
        self.assertEqual(code, 0, findings)

    def test_dormant_stage_with_complete_model_and_acceptances_passes(self):
        chain = self.chain(receipt={"activation_mode_or_dormant_reason": "dormant: triggers absent"})
        chain.embedded[STAGES[0]]["route"] = "dormant"
        chain.rewrite_artifact(STAGES[0], lambda control: None)
        code, findings = chain.run_gate()
        self.assertEqual(code, 0, findings)

    def test_ordinary_local_choice_needs_no_additional_human_checkpoint(self):
        chain = self.chain(model={"ordinary_local_choices": [
            {"description": "Choose a reversible local representation inside the approved scope.",
             "requires_Human_confirmation": False}]})
        code, findings = chain.run_gate()
        self.assertEqual(code, 0, findings)

    def test_receipt_boolean_exit_is_not_zero(self):
        def boolean_exit(receipt):
            receipt["validator_mode_and_exit_code"]["exit_code"] = False
        code, findings = self.chain(receipt=boolean_exit).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "receipt_validator_result_invalid", 17)

    def test_load_bearing_item_needs_a_bound_decision(self):
        code, findings = self.chain(model={"open_load_bearing_items": [
            {"load_bearing": True, "disposition": "resolved",
             "Human_basis": {"actor_class": "current_Human", "kind": "explicit_statement"}}
        ]}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "decision_basis_required", 15)

    def test_unresolved_item_is_not_ready(self):
        code, findings = self.chain(model={"open_load_bearing_items": [
            {"load_bearing": False, "disposition": "unresolved"}
        ]}).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "substantive_readiness_failed", 16)

    def decision_chain(self, covered=True):
        def packet(doc):
            doc["stage_actions"][0]["covered_decision_ids"] = ["choice-1"] if covered else []

        def model(doc, chain):
            doc["open_load_bearing_items"] = [{
                "load_bearing": True, "disposition": "resolved", "decision_id": "choice-1",
                "Human_basis": {"kind": "current_task_scope", "decision_id": "choice-1",
                                "task_packet": json_round(chain.packet_ref), "action_id": "act-1"}}]

        return Chain(self.tmp, packet_mutator=packet, model_mutators={STAGES[0]: model})

    def test_exact_packet_decision_coverage_passes(self):
        code, findings = self.decision_chain().run_gate()
        self.assertEqual(code, 0, findings)
        self.assertEqual(findings, [f"{RUN}: seven stages chained, separated and accepted"])

    def test_uncovered_packet_decision_is_refused(self):
        code, findings = self.decision_chain(covered=False).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "decision_not_covered", 15)

    def test_whitespace_stage_value_is_refused_through_gate(self):
        def blank(model):
            model["stage_specific_model_elements"][STAGE_FIELDS[STAGES[0]][0]]["value"] = " \t"
        code, findings = self.chain(model=blank).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "effective_stage_model", 16)

    def test_complete_canonical_profiles_pass(self):
        # Input obligations come from the actual contract, never a production
        # validator helper. The expected verdict remains the explicit zero below.
        profiles = yaml.safe_load((HERE.parents[3] / PROFILE_SET_PATH).read_text(encoding="utf-8"))
        self.assertEqual({p["profile_id"] for p in profiles["profiles"]}, set(STAGES))
        mutations = {}
        for profile in profiles["profiles"]:
            elements = {field: {"disposition": "represented_with_supported_value",
                                "value": f"synthetic supported value for {field}"}
                        for field in profile["required_model_fields"]}
            mutations[profile["profile_id"]] = (
                lambda model, chain, fields=elements:
                    model.update(stage_specific_model_elements=json_round(fields)))
        code, findings = Chain(self.tmp, model_mutators=mutations, profile_set=profiles).run_gate()
        self.assertEqual(code, 0, findings)

    def test_wrong_profile_with_both_stages_fields_is_refused(self):
        """No missing field can explain this refusal; the profile is wrong."""
        def add_other_elements(model):
            model["stage_specific_model_elements"].update(stage_elements(STAGES[4]))
        code, findings = self.chain(
            receipt={"profile_id_and_version": f"{STAGES[4]}@1"},
            model=add_other_elements).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "effective_stage_model", 16)

    def profile_set_case(self, mutate):
        chain = self.chain()
        profiles = json_round(PROFILE_SET_DOC)
        mutate(profiles)
        write(chain.repo, PROFILE_SET_PATH, profiles)
        chain.head = commit(chain.repo, "mutate candidate profile set")
        return chain.run_gate()

    def test_profile_with_empty_required_fields_is_refused(self):
        code, findings = self.profile_set_case(
            lambda doc: doc["profiles"][0].update(required_model_fields=[]))
        self.assertMechanismRefused(code, findings, "plan", "effective_stage_model", 16)

    def test_duplicate_profile_identity_is_refused(self):
        # Retain seven entries so a count check alone cannot explain the failure.
        def duplicate(doc):
            doc["profiles"][1] = json_round(doc["profiles"][0])
        code, findings = self.profile_set_case(duplicate)
        self.assertMechanismRefused(code, findings, "plan", "effective_stage_model", 16)
        self.assertIn(f": {STAGES[0]}: plan acceptance", " | ".join(findings))

    def test_profile_with_repeated_required_field_is_refused(self):
        def duplicate(doc):
            doc["profiles"][0]["required_model_fields"].append(STAGE_FIELDS[STAGES[0]][0])
        code, findings = self.profile_set_case(duplicate)
        self.assertMechanismRefused(code, findings, "plan", "effective_stage_model", 16)

    # -- the receipt is this schema's receipt --------------------------------

    def test_receipt_with_another_schema_identifier_is_refused(self):
        """Existing at the right blob is not the same as being this schema.

        The fixture carried "stage_receipt.v1" while the contract names
        "stage_collaborative_deliberation.stage_receipt.v1", and it passed,
        because the object resolved and nobody asked what it was.
        """
        code, findings = self.chain(
            receipt={"receipt_schema_version": "stage_receipt.v1"}).run_gate()
        self.assertMechanismRefused(
            code, findings, "plan",
            "receipt_schema_version_is_not_the_canonical_stage_receipt", 17)

    def test_receipt_missing_a_required_field_is_refused(self):
        code, findings = self.chain(
            receipt=lambda r: r.pop("trigger_evaluation_result_ref")).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "base_stage_receipt", 17)

    # -- object id syntax is syntax ------------------------------------------

    def test_receipt_version_with_a_sign_is_refused(self):
        """int(value, 16) accepts a leading sign. An object id does not.

        "+" followed by 39 hex digits is forty characters and parses as a number,
        so the first version of this check passed it.
        """
        code, findings = self.chain(
            receipt={"exact_candidate_version": "+" + "a" * 39}).run_gate()
        self.assertMechanismRefused(
            code, findings, "plan",
            "receipt_exact_candidate_version_is_not_a_commit_id", 17)

    def test_receipt_version_with_underscores_is_refused(self):
        """int(value, 16) treats underscores as digit separators. Same defect."""
        code, findings = self.chain(
            receipt={"exact_candidate_version": "a" * 20 + "_" * 2 + "b" * 18}).run_gate()
        self.assertMechanismRefused(
            code, findings, "plan",
            "receipt_exact_candidate_version_is_not_a_commit_id", 17)

    def test_receipt_version_in_uppercase_is_refused(self):
        code, findings = self.chain(
            receipt={"exact_candidate_version": "A" * 40}).run_gate()
        self.assertMechanismRefused(
            code, findings, "plan",
            "receipt_exact_candidate_version_is_not_a_commit_id", 17)

    # -- the model and the receipt the mechanism requires --------------------

    def test_incomplete_current_model_is_refused(self):
        """The model is judged, not merely hashed.

        Its blob identity was checked all along; whether it was a Current Model
        at all was not.
        """
        code, findings = self.chain(
            model=lambda m: m.pop("expected_output")).run_gate()
        self.assertMechanismRefused(code, findings, "plan",
                                    "current_model_completeness", 16)

    def test_receipt_with_a_failing_gate_is_refused(self):
        def fail_completion(receipt):
            receipt["gate_results"]["completion"] = "fail"
        code, findings = self.chain(receipt=fail_completion).run_gate()
        self.assertMechanismRefused(code, findings, "plan", "base_stage_receipt", 17)

    def test_receipt_version_that_is_not_a_commit_is_refused(self):
        """Truthy is not exact.

        validate_base_stage_receipt requires exact_candidate_version to be
        non-empty, and "not-a-commit" is non-empty. A receipt whose version cannot
        be a commit id at all was published as an accepted stage.
        """
        code, findings = self.chain(
            receipt={"exact_candidate_version": "not-a-commit"}).run_gate()
        self.assertMechanismRefused(
            code, findings, "plan",
            "receipt_exact_candidate_version_is_not_a_commit_id", 17)

    def test_receipt_version_naming_a_real_but_wrong_commit_is_not_refused(self):
        """A characterisation test for an open contract ambiguity. Read the name.

        This asserts what the publication path currently does, not what it should
        do. exact_candidate_version here is a real commit in this repository, well
        formed, and wrong: it is the boundary, not anything this stage produced.
        It passes.

        The format check added alongside it refuses "not-a-commit", which is a
        string that could never be a commit id. It deliberately does not decide
        which commit the field must name, because no governing contract settles
        that for the publication path. _scope_receipt defines it for the
        task-scope path as equal to the candidate being validated, but applying
        that per stage would require a stage receipt to name a commit that does
        not exist when the receipt is written.

        So this is recorded rather than guessed. If someone later gives the field
        a referent, this test fails and forces the contract to be updated with it,
        which is the point of writing it down instead of leaving a silent gap.
        """
        # The boundary commit: real, well formed, and not this stage's anything.
        chain = Chain(self.tmp,
                      receipt_mutators={STAGES[0]: lambda r, ch: r.__setitem__(
                          "exact_candidate_version", ch.boundary)})
        code, findings = chain.run_gate()
        joined = " | ".join(findings)
        self.assertEqual(code, 0, f"behaviour changed - update the contract too: {joined}")

    def test_receipt_reference_pointing_at_something_else_is_refused(self):
        """The declared ref is resolved, so it has to name the receipt.

        It pointed at model.yml in the fixture and passed, because the gate read
        an embedded copy and never resolved the ref at all.
        """
        chain = self.chain()
        sid = STAGES[0]
        model_blob = chain.controls[sid]["current_model_ref"]["blob_sha"]
        chain.rewrite_artifact(sid, lambda c: c["deliberation_receipt_ref"].update(
            {"path": f"{RUN}/{sid}/model.yml", "blob_sha": model_blob}))
        code, findings = chain.run_gate()
        joined = " | ".join(findings)
        self.assertNotEqual(code, 0, joined)

    # -- the evidence the completion rests on --------------------------------

    def test_verification_document_saying_failed_is_refused(self):
        """A verification record that says it failed is not acceptance evidence.

        The reference was checked and the document was never opened, so a
        verification file correctly bound to its own W, task and stage, at a real
        blob, reading status: failed, published as "seven stages chained,
        separated and accepted".

        This asks nothing new of anyone. The contract has required these five
        fields with status verified all along, and _scope_completion already
        compares exactly this shape; it simply was not reached from here.
        """
        code, findings = self.chain(
            verification={"status": "failed"}).run_gate()
        self.assertMechanismRefused(
            code, findings, "completion",
            "verification_document_is_not_a_verified_result_for_this_stage", 14)

    def test_verification_document_for_another_stage_is_refused(self):
        code, findings = self.chain(
            verification={"stage_id": STAGES[4]}).run_gate()
        self.assertMechanismRefused(
            code, findings, "completion",
            "verification_document_is_not_a_verified_result_for_this_stage", 14)

    # -- feasibility is supported, not asserted ------------------------------

    def test_feasibility_support_as_a_bare_string_is_refused(self):
        """Completeness is satisfied by a confident sentence. That was the gap.

        The publication path called only the completeness helper, so a model whose
        feasibility_support was one string passed here while _scope_feasibility
        refused the same model with 16.
        """
        code, findings = self.chain(
            model={"feasibility_support": "it will be fine"}).run_gate()
        self.assertMechanismRefused(code, findings, "plan",
                                    "feasibility_support_must_carry_a_basis", 16)

    def test_feasibility_basis_kind_not_allowed_for_the_stage_is_refused(self):
        code, findings = self.chain(model={"feasibility_support": {
            "value": "a real sentence",
            "basis": {"kind": "test_result_ref", "ref": "somewhere"}}}).run_gate()
        self.assertMechanismRefused(code, findings, "plan",
                                    "feasibility_basis_kind_not_allowed_for_stage", 16)

    def test_human_approval_as_a_feasibility_basis_is_refused(self):
        """Approval is authority, not evidence.

        The Human approves because the work is feasible, so feasibility cannot be
        established by the approval. The contract prohibits these kinds by name.
        """
        code, findings = self.chain(model={"feasibility_support": {
            "value": "the Human approved it",
            "basis": {"kind": "Human_approved", "ref": "a decision"}}}).run_gate()
        self.assertMechanismRefused(code, findings, "plan",
                                    "feasibility_basis_kind_prohibited", 16)

    # -- what the verdict is about -------------------------------------------

    def test_working_tree_cannot_move_the_verdict(self):
        """The verdict is about the candidate, not about what is on disk.

        The runner's validate_run reads the working tree, which is why it was not
        wired into this gate: a push of commit X with a dirty tree would have been
        judged on the tree rather than on X. Here the same candidate is judged
        twice with both acceptance files vandalised in between, and the answer
        does not move.
        """
        chain = self.chain()
        first, findings = chain.run_gate()
        self.assertEqual(first, 0, " | ".join(findings))
        for name in ("plan_acceptance.yml", "completion_acceptance.yml"):
            path = chain.repo / RUN / STAGES[0] / name
            path.write_text("actor_class: executor\nHuman_disposition: rejected\n",
                            encoding="utf-8")
        second, findings = chain.run_gate()
        self.assertEqual(second, 0,
                         f"the working tree moved a verdict about a commit: {' | '.join(findings)}")


if __name__ == "__main__":
    unittest.main()
