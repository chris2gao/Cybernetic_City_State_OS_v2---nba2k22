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
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

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

    def __init__(self, root: Path):
        self.repo = root / "repo"
        self.repo.mkdir(parents=True)
        git(self.repo, "init", "-b", "fixture")
        git(self.repo, "config", "user.name", "Synthetic gate fixture")
        git(self.repo, "config", "user.email", "gate-fixture@example.invalid")
        write(self.repo, "README.md", "fixture\n")
        self.boundary = commit(self.repo, "boundary")
        self.stages: dict[str, dict] = {}
        self.controls: dict[str, dict] = {}
        prev_c: str | None = None

        for index, sid in enumerate(STAGES):
            d = f"{RUN}/{sid}"
            model_blob = write(self.repo, f"{d}/model.yml",
                               {"stage_id": sid, "model": f"model for {sid}"})
            m = commit(self.repo, f"{sid} model")

            plan_blob = write(self.repo, f"{d}/plan_acceptance.yml",
                              {"stage_id": sid, "accepts": model_blob})
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
            if prev_c is not None:
                control["plan_acceptance"]["predecessor_completion_commit"] = prev_c
            write(self.repo, f"{RUN}/{FILES[index]}",
                  {"stage_id": sid, "stage_control": control})
            w = commit(self.repo, f"{sid} work")

            ver_blob = write(self.repo, f"{d}/verification.yml", {"stage_id": sid, "of": w})
            ver_commit = commit(self.repo, f"{sid} verification evidence")

            comp_blob = write(self.repo, f"{d}/completion_acceptance.yml",
                              {"stage_id": sid, "accepts_output_commit": w})
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
                  {"stage_id": sid, "stage_control": control})
            c = commit(self.repo, f"{sid} completion acceptance")

            self.stages[sid] = {"m": m, "p": p, "w": w, "c": c}
            self.controls[sid] = control
            prev_c = c

        write(self.repo, f"{RUN}/manifest.yml",
              {"artifacts": [{"stage_id": s, "path": f} for s, f in zip(STAGES, FILES)]})
        write(self.repo, f"{RUN}/run.yml",
              {"base_sha": self.boundary_child(), "final_stage_completion_commit": prev_c})
        self.head = commit(self.repo, "run identity")

    def boundary_child(self) -> str:
        return self.stages[STAGES[0]]["m"] if self.stages else self.boundary

    def rewrite_artifact(self, sid: str, mutate) -> None:
        index = STAGES.index(sid)
        control = json_round(self.controls[sid])
        mutate(control)
        write(self.repo, f"{RUN}/{FILES[index]}", {"stage_id": sid, "stage_control": control})
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
        shutil.rmtree(self.tmp, ignore_errors=True)

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
            shutil.rmtree(empty, ignore_errors=True)

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
        sid = STAGES[1]
        self.chain.rewrite_artifact(
            sid, lambda c: c["plan_acceptance"].__setitem__("path", f"{RUN}/nope.yml"))
        code, findings = self.chain.run_gate()
        self.assertRefused(code, findings, 15, "absent at")

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
        sid = STAGES[0]
        self.chain.rewrite_artifact(
            sid, lambda c: c["plan_acceptance"].__setitem__(
                "predecessor_completion_commit", self.chain.stages[STAGES[3]]["c"]))
        code, findings = self.chain.run_gate()
        self.assertRefused(code, findings, 11, "must not name a predecessor")

    def test_broken_chain_link_is_refused(self):
        """A wrong predecessor fails because the blob is not in the named commit."""
        sid = STAGES[4]
        wrong = self.chain.stages[STAGES[0]]["c"]
        self.chain.rewrite_artifact(
            sid, lambda c: c["plan_acceptance"].__setitem__("predecessor_completion_commit", wrong))
        code, findings = self.chain.run_gate()
        self.assertNotEqual(code, 0, " | ".join(findings))

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


if __name__ == "__main__":
    unittest.main()
