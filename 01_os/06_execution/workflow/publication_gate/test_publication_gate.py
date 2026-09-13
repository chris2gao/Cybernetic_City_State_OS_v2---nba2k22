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


def current_model(sid: str, baseline: str) -> dict:
    """A complete Current Model: every common field present with a disposition.

    none_material is a real answer and the mechanism accepts it; a missing key or
    a null value is not, and it refuses those. The model cannot name its own
    commit - it is the content of that commit - so the version it carries is the
    baseline it was authored against.
    """
    return {
        "stage_id": sid,
        "problem_or_objective": f"establish the {sid} artifact for the fixture run",
        "why_this_stage_is_needed_now": f"{sid} has no accepted artifact in this run yet",
        "Human_intent_understanding": "exercise the publication gate end to end",
        "current_baseline_and_inputs": baseline,
        "proposed_method_or_solution": f"author the {sid} artifact and bind it exactly",
        "feasibility_support": "the preceding stage completed and its output is bound",
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
        "receipt_schema_version": "stage_receipt.v1",
        "mechanism_version": "stage_collaborative_deliberation.v1",
        "active_contract_version": "阶段profile契约_v1",
        "boot_manifest_version": "fixture-boot-1",
        "registry_version": "fixture-registry-1",
        "loader_version": "fixture-loader-1",
        "profile_id_and_version": f"{sid}@v1",
        "loaded_paths": [f"{RUN}/{sid}/model.yml"],
        "missing_partial_or_stale_paths": [],
        "trigger_evaluation_result_ref": f"{RUN}/{sid}/model.yml",
        "activation_mode_or_dormant_reason": "active",
        "main_mechanism_ref": "01_os/03_mechanisms/stage_collaborative_deliberation",
        "detail_granularity_evaluation_result": "sufficient",
        "open_detail_divergence_event_refs": [],
        "deferred_detail_record_refs": [],
        "gate_results": {"start": "pass", "completion": "pass"},
        "validator_mode_and_exit_code": {"mode": "full", "exit_code": 0},
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
                 completion_mutators: dict | None = None):
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
        self.repo = root / "repo"
        self.repo.mkdir(parents=True)
        git(self.repo, "init", "-b", "fixture")
        git(self.repo, "config", "user.name", "Synthetic gate fixture")
        git(self.repo, "config", "user.email", "gate-fixture@example.invalid")
        write(self.repo, "README.md", "fixture\n")
        self.boundary = commit(self.repo, "boundary")
        self.stages: dict[str, dict] = {}
        self.controls: dict[str, dict] = {}
        self.receipts: dict[str, dict] = {}
        prev_c: str | None = None

        for index, sid in enumerate(STAGES):
            d = f"{RUN}/{sid}"
            baseline = prev_c or self.boundary
            receipt = stage_receipt(sid, baseline)
            model_blob = write(self.repo, f"{d}/model.yml", current_model(sid, baseline))
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
                "deliberation_receipt_ref": {"path": f"{d}/model.yml", "blob_sha": model_blob},
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
                   "deliberation_receipt": receipt})
            w = commit(self.repo, f"{sid} work")

            ver_blob = write(self.repo, f"{d}/verification.yml", {"stage_id": sid, "of": w})
            ver_commit = commit(self.repo, f"{sid} verification evidence")

            # The completion record names the output commit it accepted and the
            # verification evidence it rests on, and carries the closure fields.
            # A plan record copied here is refused on its decision type alone.
            comp_record = accepted(
                sid, COMPLETION_DECISION,
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
                   "deliberation_receipt": receipt})
            c = commit(self.repo, f"{sid} completion acceptance")

            self.stages[sid] = {"m": m, "p": p, "w": w, "c": c}
            self.controls[sid] = control
            self.receipts[sid] = receipt
            prev_c = c

        write(self.repo, f"{RUN}/manifest.yml",
              {"artifacts": [{"stage_id": s, "path": f} for s, f in zip(STAGES, FILES)]})
        write(self.repo, f"{RUN}/run.yml",
              {"task_id": TASK_ID, "base_sha": self.boundary_child(),
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
               "deliberation_receipt": self.receipts[sid]})
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

    def chain(self, plan=None, completion=None) -> Chain:
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
        return Chain(self.tmp,
                     plan_mutators=at_first(plan) if plan is not None else None,
                     completion_mutators=at_first(completion) if completion is not None else None)

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

    def test_completion_record_missing_a_closure_field_is_refused(self):
        code, findings = self.chain(
            completion=lambda r: r.pop("residual_risk")).run_gate()
        self.assertMechanismRefused(code, findings, "completion",
                                    "closure_field_absent:residual_risk", 14)

    # -- the model and the receipt the mechanism requires --------------------

    def test_incomplete_current_model_is_refused(self):
        """The model is judged, not merely hashed.

        Its blob identity was checked all along; whether it was a Current Model
        at all was not.
        """
        chain = Chain(self.tmp)
        sid = STAGES[0]
        path = chain.repo / RUN / sid / "model.yml"
        model = yaml.safe_load(path.read_text(encoding="utf-8"))
        del model["feasibility_support"]
        blob = write(chain.repo, f"{RUN}/{sid}/model.yml", model)
        chain.rewrite_artifact(sid, lambda c: (
            c["current_model_ref"].__setitem__("blob_sha", blob),
            c["plan_acceptance"].__setitem__("accepted_model_blob_sha", blob)))
        code, findings = chain.run_gate()
        joined = " | ".join(findings)
        self.assertNotEqual(code, 0, joined)

    def test_receipt_with_a_failing_gate_is_refused(self):
        chain = Chain(self.tmp)
        sid = STAGES[0]
        index = STAGES.index(sid)
        receipt = json_round(chain.receipts[sid])
        receipt["gate_results"]["completion"] = "fail"
        write(chain.repo, f"{RUN}/{FILES[index]}",
              {"stage_id": sid, "stage_control": json_round(chain.controls[sid]),
               "deliberation_receipt": receipt})
        chain.head = commit(chain.repo, "receipt with a failing gate")
        code, findings = chain.run_gate()
        self.assertMechanismRefused(code, findings, "plan", "base_stage_receipt", 17)

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
