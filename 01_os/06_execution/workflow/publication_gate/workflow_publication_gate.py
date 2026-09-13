#!/usr/bin/env python3
"""Transport-independent workflow publication gate.

Decides whether a run history may be published. It is not a git hook. A git hook
is one caller among several, and a transport that does not call this gate is not
covered by it.

What this gate owns:
    reference resolution, composition, Git ordering, tree and blob presence, and
    fail-closed progression.

What this gate does not own, and must never reimplement:
    Human disposition semantics, Current Model completeness, receipt validity,
    feasibility basis, closure semantics. Those belong to
    stage_collaborative_deliberation and exist there already. A second copy would
    be a second mechanism, which the architecture decision prohibits.

The chain, per stage, from 阶段产物到instance映射契约_v2.yml:

    C_prev -> M_i -> P_i -> W_i -> C_i

Every edge is strict Git ancestry: X != Y and X is an ancestor of Y. The
inequality is checked separately because `merge-base --is-ancestor` exits 0 when
the two commits are the same, so ancestry alone would let one commit satisfy an
edge with itself.

Strict ancestry alone is not enough. Five commits with identical trees satisfy
every edge and prove nothing, so the gate also checks phase content separation:
each phase must actually have added its own artifact. See `_check_separation`.

What the chain proves and does not prove is stated in the contract and repeated
here so that nobody reading only this file overstates it:

    proves    the accepted content existed as an independently committed Git node
              before any record referred to it, and each phase added its own
              artifact
    does not  that the work happened after the acceptance. No runtime supervises
    prove     the working tree. An author may produce everything first and commit
              it in the required order afterwards.

Human authenticity is likewise out of scope here. The gate can establish that an
acceptance record exists, is bound to this exact task, stage and version, and
carries a well-formed commitment, which means a Human can later challenge it with
human_challenge_verify.py. It cannot establish that a Human accepted anything.
Those are different claims.

So is the publication base. The exact claim is:

    the gate validates the transition given an authentic publication base
    the caller establishes the publication-base binding

`--base` is checked only for being a strict ancestor of the candidate. Ancestry
does not make a commit the real old head of this publication: many commits are
ancestors, and a caller that picks a convenient one narrows the governance
history it will be judged against. Establishing that binding belongs to the
transport and cannot be done from inside a transport-independent tool:

    local_git       the remote-old sha and ref update context on pre-push stdin
    API, connector  a fresh read of the exact remote ref head, bound by
                    expected-head or compare-and-swap
    unknown         blocked

A caller that invents a base has produced a false receipt, in the same sense that
repository_guards_v1.yml already gives to reporting hook_guard passed from a
transport the hook never ran on.

Usage:
    workflow_publication_gate.py --repo-root REPO --candidate FULL_COMMIT_SHA
                                 [--json] [--boundary FULL_COMMIT_SHA]

Exit codes:
    0   publication permitted by this gate
    10  usage or input error
    11  a required reference is missing or malformed
    12  a binding does not match
    13  an ordering edge is violated
    14  phase content separation is violated
    15  a named blob is absent or differs at the commit that should carry it
    16  the stage chain is incomplete
    20  the repository could not be read
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

PASS = 0
USAGE = 10
REF = 11
ORDERING = 13
SEPARATION = 14
BLOB = 15
CHAIN = 16
ACCEPT = 17
REPO = 20

STAGE_IDS = [
    "workflow_stage_01_requirement_modeling",
    "workflow_stage_02_information_collection",
    "workflow_stage_03_result_modeling",
    "workflow_stage_04_test_generation",
    "workflow_stage_05_step_decomposition",
    "workflow_stage_06_execution",
    "workflow_stage_07_test_execution",
]

RUNS_ROOT = "01_os/_runs"
MECHANISM = "01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation.py"


class GateError(Exception):
    def __init__(self, code: int, reason: str):
        super().__init__(reason)
        self.code = code
        self.reason = reason


def _require(condition: bool, code: int, reason: str) -> None:
    if not condition:
        raise GateError(code, reason)


@dataclass
class Findings:
    """Findings a reader must act on, and a count of the ones they must not.

    A gate that prints one line per run directory printed fifty-seven lines
    against this repository, all of them saying the same thing: not a governed
    run. Output like that on every push is what makes people reach for
    --no-verify, so the uninteresting majority is counted rather than listed.
    """

    rows: list[str] = field(default_factory=list)
    not_governed: int = 0

    def note(self, text: str) -> None:
        self.rows.append(text)

    def skip(self) -> None:
        self.not_governed += 1

    def summary(self) -> list[str]:
        out = list(self.rows)
        if self.not_governed:
            out.append(f"{self.not_governed} run directories are not seven-stage runs, not judged")
        return out


# -- git access ---------------------------------------------------------------
# Implemented here rather than imported. task_discipline/packet_input and
# task_discipline/managed_verification are forbidden paths for this task, and
# depending on a module this task may not modify would couple the gate to
# something it cannot fix.


def _git_try(repo: Path, *args: str) -> tuple[int, bytes, str]:
    proc = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo), *args],
        capture_output=True, check=False)
    return proc.returncode, proc.stdout, proc.stderr.decode("utf-8", "replace")


def _git(repo: Path, *args: str) -> bytes:
    code, out, err = _git_try(repo, *args)
    if code != 0:
        raise GateError(REPO, f"git {' '.join(args[:2])} exited {code}: {err.strip()[:200]}")
    return out


_ABSENT = ("not a valid object name", "does not exist", "exists on disk, but not in")


def _looks_absent(stderr: str) -> bool:
    """Absent is not the same as unreadable.

    `not a tree object` is deliberately excluded. It is what a corrupt object
    graph produces, and treating it as absence was a defect in a sibling tool in
    this repository: a broken repository would have reported nothing to check.
    """
    low = stderr.lower()
    return any(marker in low for marker in _ABSENT)


def _is_sha(value: object) -> bool:
    return (isinstance(value, str) and len(value) == 40
            and all(c in "0123456789abcdef" for c in value))


def _commit_exists(repo: Path, sha: str) -> bool:
    try:
        kind = _git(repo, "cat-file", "-t", sha).decode("utf-8").strip()
    except GateError:
        return False
    return kind == "commit"


def _strictly_precedes(repo: Path, earlier: str, later: str) -> bool:
    """X != Y and X is an ancestor of Y.

    The inequality is separate on purpose: --is-ancestor exits 0 for X == Y, so
    without it a single commit would satisfy an edge with itself and the whole
    chain could collapse onto one node.
    """
    if earlier == later:
        return False
    proc = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo),
         "merge-base", "--is-ancestor", earlier, later],
        capture_output=True, check=False)
    return proc.returncode == 0


def _blob_at(repo: Path, commit: str, path: str) -> str | None:
    """Return the blob sha of `path` at `commit`, or None when absent.

    Reads the tree at a named commit. It never searches history for where a blob
    first appeared: that technique has no precedent in this repository and it
    already produced a wrong answer here once, when a namespace cutover re-added
    every path and made every run report the same date.
    """
    proc = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo), "ls-tree", "-z", commit, "--", path],
        capture_output=True, check=False)
    if proc.returncode != 0:
        return None
    out = proc.stdout.decode("utf-8", "replace").strip("\0").strip()
    if not out:
        return None
    meta = out.split("\t", 1)[0].split()
    if len(meta) < 3 or meta[1] != "blob":
        return None
    return meta[2]


def _load_yaml_at(repo: Path, commit: str, path: str):
    import yaml
    blob = _blob_at(repo, commit, path)
    if blob is None:
        return None
    raw = _git(repo, "cat-file", "blob", blob)
    try:
        return yaml.safe_load(raw.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - an unreadable file is a fact about it
        raise GateError(REF, f"unreadable:{path}:{type(exc).__name__}") from exc


# -- reference shapes ---------------------------------------------------------


def _ref_pair(value: object, where: str) -> tuple[str, str]:
    _require(isinstance(value, dict) and set(value) == {"path", "blob_sha"},
             REF, f"expected {{path, blob_sha}} at {where}")
    path, blob = value["path"], value["blob_sha"]  # type: ignore[index]
    _require(isinstance(path, str) and bool(path.strip()), REF, f"empty path at {where}")
    _require(isinstance(blob, str) and len(blob) == 40, REF, f"malformed blob_sha at {where}")
    return path, blob


def _blob_must_match(repo: Path, commit: str, path: str, blob: str, where: str) -> None:
    actual = _blob_at(repo, commit, path)
    _require(actual is not None, BLOB, f"{where}: {path} absent at {commit[:12]}")
    _require(actual == blob, BLOB,
             f"{where}: {path} at {commit[:12]} is {actual[:12] if actual else 'none'}, declared {blob[:12]}")


def _blob_must_be_absent(repo: Path, commit: str, path: str, blob: str, where: str) -> None:
    actual = _blob_at(repo, commit, path)
    _require(actual != blob, SEPARATION,
             f"{where}: {path} already present with the same content at {commit[:12]}")


# -- the gate -----------------------------------------------------------------


@dataclass
class StageNodes:
    stage_id: str
    c_prev: str | None
    m: str
    p: str
    w: str
    c: str | None = None


def _read_stage_control(artifact: dict, stage_id: str) -> dict:
    control = artifact.get("stage_control")
    _require(isinstance(control, dict), REF, f"{stage_id}: stage_control missing")
    return control  # type: ignore[return-value]


def _collect_nodes(repo: Path, candidate: str, run_root: str,
                   manifest: dict, findings: Findings) -> list[StageNodes]:
    entries = manifest.get("artifacts")
    _require(isinstance(entries, list) and bool(entries), REF, "manifest has no artifacts")
    by_stage: dict[str, dict] = {}
    for item in entries:  # type: ignore[union-attr]
        _require(isinstance(item, dict), REF, "manifest artifact entry is not a mapping")
        sid, rel = item.get("stage_id"), item.get("path")
        _require(isinstance(sid, str) and isinstance(rel, str), REF, "manifest entry missing stage_id or path")
        art = _load_yaml_at(repo, candidate, f"{run_root}/{rel}")
        _require(isinstance(art, dict), REF, f"{sid}: artifact unreadable at the candidate")
        by_stage[sid] = art  # type: ignore[assignment]

    _require([x.get("stage_id") for x in entries] == STAGE_IDS,  # type: ignore[union-attr]
             CHAIN, "manifest stage order does not match the seven canonical stages")

    nodes: list[StageNodes] = []
    for index, sid in enumerate(STAGE_IDS):
        control = _read_stage_control(by_stage[sid], sid)
        plan = control.get("plan_acceptance")
        _require(isinstance(plan, dict), REF, f"{sid}: plan_acceptance missing")

        for key in ("commit", "accepted_model_commit"):
            _require(_is_sha(plan.get(key)), REF, f"{sid}: plan_acceptance.{key} is not a 40-char sha")

        # The predecessor binding is read from the plan acceptance record itself,
        # not from a summary field in the stage artifact. The record is covered by
        # its blob sha, so editing the binding changes the hash and is caught; a
        # field in the artifact could be edited while the record it claims to
        # summarise stayed untouched.
        accepted = _load_yaml_at(repo, plan["commit"], plan.get("path", ""))
        _require(isinstance(accepted, dict), REF,
                 f"{sid}: plan acceptance record is absent or unreadable at its own commit")
        c_prev = accepted.get("predecessor_completion_commit")
        if index == 0:
            _require(c_prev is None, REF,
                     f"{sid}: stage 01 must not name a predecessor completion commit")
        else:
            _require(_is_sha(c_prev), REF,
                     f"{sid}: the plan acceptance record must name predecessor_completion_commit "
                     f"as a 40-character sha")

        completion = control.get("completion_acceptance")
        _require(isinstance(completion, dict), REF, f"{sid}: completion_acceptance missing")
        w = completion.get("bound_output_version")
        _require(_is_sha(w), REF, f"{sid}: bound_output_version is not a 40-char sha")

        nodes.append(StageNodes(stage_id=sid, c_prev=c_prev, m=plan["accepted_model_commit"],
                                p=plan["commit"], w=w))

    # C_i is named by the next stage, because a record inside C_i cannot carry
    # C_i's own sha. The final C_7 is named by the run completion pointer.
    #
    # An earlier revision followed this assignment with a _chain_stages check
    # asserting nodes[i].c_prev == nodes[i-1].c. Substituting this very line, both
    # sides are the same value, so the check compared a variable with itself and
    # could never fail. It has been removed rather than repaired: what actually
    # binds the chain is S9c in _check_separation, where the C_i named by stage
    # i+1 must contain stage i's completion acceptance blob. A wrong commit fails
    # there because the blob is not in it.
    for index in range(len(nodes) - 1):
        nodes[index].c = nodes[index + 1].c_prev
    return nodes


def _check_ordering(repo: Path, nodes: list[StageNodes]) -> None:
    for node in nodes:
        edges = [(node.m, node.p, "M->P"), (node.p, node.w, "P->W")]
        if node.c_prev is not None:
            edges.insert(0, (node.c_prev, node.m, "Cprev->M"))
        if node.c is not None:
            edges.append((node.w, node.c, "W->C"))
        for earlier, later, name in edges:
            _require(_commit_exists(repo, earlier), REF, f"{node.stage_id}: {name} left node is not a commit")
            _require(_commit_exists(repo, later), REF, f"{node.stage_id}: {name} right node is not a commit")
            _require(_strictly_precedes(repo, earlier, later), ORDERING,
                     f"{node.stage_id}: {name} is not strict ancestry "
                     f"({earlier[:12]} -> {later[:12]})")


def _check_separation(repo: Path, nodes: list[StageNodes], controls: dict[str, dict]) -> None:
    """Each phase must have added its own artifact.

    Without this, four empty commits satisfy every ordering edge and the chain
    certifies nothing. This proves committed-history separation between phases.
    It does not observe the working tree and must never be described as evidence
    of real authoring order.
    """
    for node in nodes:
        control = controls[node.stage_id]
        plan = control["plan_acceptance"]
        completion = control["completion_acceptance"]

        plan_path, plan_blob = _ref_pair({"path": plan.get("path"), "blob_sha": plan.get("blob_sha")},
                                         f"{node.stage_id}.plan_acceptance")
        _blob_must_match(repo, node.p, plan_path, plan_blob, f"{node.stage_id} plan acceptance at P")
        _blob_must_be_absent(repo, node.m, plan_path, plan_blob,
                             f"{node.stage_id} plan acceptance must not predate the model it accepts")

        model_path = plan.get("accepted_model_path")
        model_blob = plan.get("accepted_model_blob_sha")
        _ref_pair({"path": model_path, "blob_sha": model_blob}, f"{node.stage_id}.accepted_model")
        _blob_must_match(repo, node.m, model_path, model_blob, f"{node.stage_id} accepted model at M")
        _blob_must_match(repo, node.p, model_path, model_blob,
                         f"{node.stage_id} accepted model unchanged at P")

        out_path = completion.get("output_path")
        out_blob = completion.get("output_blob_sha")
        _ref_pair({"path": out_path, "blob_sha": out_blob}, f"{node.stage_id}.output")
        _blob_must_match(repo, node.w, out_path, out_blob, f"{node.stage_id} stage output at W")
        _blob_must_be_absent(repo, node.p, out_path, out_blob,
                             f"{node.stage_id} output already existed when it was authorised")

        if node.c is not None:
            comp_path, comp_blob = _ref_pair(
                {"path": completion.get("path"), "blob_sha": completion.get("blob_sha")},
                f"{node.stage_id}.completion_acceptance")
            _blob_must_match(repo, node.c, comp_path, comp_blob,
                             f"{node.stage_id} completion acceptance at C")
            _blob_must_be_absent(repo, node.w, comp_path, comp_blob,
                                 f"{node.stage_id} completion acceptance must not predate the output it accepts")


def _check_verification(repo: Path, nodes: list[StageNodes], controls: dict[str, dict]) -> None:
    for node in nodes:
        ref = controls[node.stage_id]["completion_acceptance"].get("verification_result")
        _require(isinstance(ref, dict) and set(ref) == {"commit", "path", "blob_sha"},
                 REF, f"{node.stage_id}: verification_result must be {{commit, path, blob_sha}}")
        _require(_is_sha(ref["commit"]), REF, f"{node.stage_id}: verification commit is not a sha")
        _require(ref["commit"] != node.w, SEPARATION,
                 f"{node.stage_id}: verification evidence must not live in the output commit")
        _blob_must_match(repo, ref["commit"], ref["path"], ref["blob_sha"],
                         f"{node.stage_id} verification record")


def _load_mechanism() -> object:
    """Import the deliberation mechanism, which is what judges an acceptance record.

    Where it is loaded from is a security property, not a convenience. It comes
    from the installation this gate is part of - resolved next to this file - and
    never from the repository under judgement or from a candidate blob.

    The first version of this function took it from the repo-root argument. That
    is the repository being judged. A crafted repository could have shipped its
    own permissive verify_stage_collaborative_deliberation.py, and this gate would
    have imported it and executed it, letting the push choose its own judge and
    run arbitrary code in the process. The docstring at the time already said "the
    checkout judges, the candidate is judged"; the code did the opposite. It was
    caught because a synthetic fixture repository correctly reported the mechanism
    missing, which would not have happened had the lookup been right.

    Evidence is read at the candidate, because evidence is what the push asserts.
    Judgement is read from here, because a judge the defendant supplies is not one.
    """
    import importlib.util

    path = Path(__file__).resolve().parents[4] / MECHANISM
    if not path.is_file():
        raise GateError(REPO, f"the deliberation mechanism is missing at {MECHANISM}. "
                              f"Unable to ask is not an answer.")
    spec = importlib.util.spec_from_file_location("scd_for_publication_gate", path)
    if spec is None or spec.loader is None:
        raise GateError(REPO, f"cannot load the deliberation mechanism at {MECHANISM}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "validate_stage_acceptance_context"):
        raise GateError(REPO, "the deliberation mechanism has no "
                              "validate_stage_acceptance_context entry; this gate will not "
                              "substitute a judgement of its own")
    return module


def _acceptance_ref(control: dict, field_name: str, stage_id: str, fallback_commit: str | None):
    """Where one acceptance record lives. References only; content comes next."""
    ref = control.get(field_name)
    _require(isinstance(ref, dict), REF, f"{stage_id}: {field_name} is missing or not a mapping")
    path = ref.get("path")
    blob = ref.get("blob_sha")
    _require(isinstance(path, str) and path, REF, f"{stage_id}: {field_name} has no path")
    _require(_is_sha(blob), REF, f"{stage_id}: {field_name} blob_sha is not a 40-character sha")
    commit = ref.get("commit", fallback_commit)
    _require(_is_sha(commit), REF,
             f"{stage_id}: {field_name} has no commit to read it at")
    return commit, path, blob


def _exact(repo: Path, ref: Any, where: str) -> dict:
    """An exact {commit, path, blob_sha} reference, verified against the candidate."""
    _require(isinstance(ref, dict), REF, f"{where}: reference is missing or not a mapping")
    missing = {"commit", "path", "blob_sha"} - set(ref)
    _require(not missing, REF, f"{where}: reference is missing {sorted(missing)}")
    _require(_is_sha(ref["commit"]), REF, f"{where}: commit is not a 40-character sha")
    _require(_is_sha(ref["blob_sha"]), REF, f"{where}: blob_sha is not a 40-character sha")
    _require(isinstance(ref["path"], str) and ref["path"], REF, f"{where}: path is empty")
    _blob_must_match(repo, ref["commit"], ref["path"], ref["blob_sha"], where)
    return {"commit": ref["commit"], "path": ref["path"], "blob_sha": ref["blob_sha"]}


def _acceptance_context(repo: Path, node: StageNodes, control: dict, art: dict,
                        task_id: str, phase: str) -> dict:
    """Assemble what one stage acceptance claims to accept, from candidate objects.

    Resolution only. Every reference is read at its own commit and checked against
    its declared blob, so the content handed to the mechanism is what was
    published rather than what happens to be on disk. Nothing here decides whether
    the acceptance is valid: no field of the record is compared with any other,
    because that comparison belongs to the mechanism and a second copy of it here
    is precisely the failure this arrangement exists to prevent.
    """
    field_name = f"{phase}_acceptance"
    fallback = node.p if phase == "plan" else node.c
    commit, path, blob = _acceptance_ref(control, field_name, node.stage_id, fallback)
    record_ref = _exact(repo, {"commit": commit, "path": path, "blob_sha": blob},
                        f"{node.stage_id} {field_name}")
    record = _load_yaml_at(repo, commit, path)
    _require(isinstance(record, dict), REF,
             f"{node.stage_id}: {field_name} at {commit[:12]} is not a mapping")

    context = {"task_id": task_id, "stage_id": node.stage_id, "phase": phase,
               "record": record, "record_ref": record_ref,
               "receipt": art.get("deliberation_receipt")}

    if phase == "plan":
        model_ref = control.get("current_model_ref")
        _require(isinstance(model_ref, dict), REF,
                 f"{node.stage_id}: current_model_ref is missing or not a mapping")
        # The model lives at M, which is a topology fact this gate already holds.
        # The control states path and blob; it does not restate the commit.
        bound = _exact(repo, {"commit": node.m, "path": model_ref.get("path"),
                              "blob_sha": model_ref.get("blob_sha")},
                       f"{node.stage_id} current_model_ref")
        accepted = _exact(repo, {"commit": control[field_name].get("accepted_model_commit"),
                                 "path": control[field_name].get("accepted_model_path"),
                                 "blob_sha": control[field_name].get("accepted_model_blob_sha")},
                          f"{node.stage_id} plan_acceptance accepted model")
        context["bound_model"] = bound
        context["accepted_model"] = accepted
        context["model"] = _load_yaml_at(repo, accepted["commit"], accepted["path"])
    else:
        completion = control[field_name]
        context["stage_output_commit"] = node.w
        context["accepted_output"] = _exact(
            repo, {"commit": completion.get("bound_output_version"),
                   "path": completion.get("output_path"),
                   "blob_sha": completion.get("output_blob_sha")},
            f"{node.stage_id} completion_acceptance accepted output")
        context["accepted_verification"] = _exact(
            repo, completion.get("verification_result"),
            f"{node.stage_id} completion_acceptance verification evidence")
    return context


def _check_acceptance(repo: Path, nodes: list[StageNodes], controls: dict[str, dict],
                      arts: dict[str, dict], run_doc: dict) -> None:
    """Open both acceptance records and let the mechanism judge them.

    Until this existed the gate checked that a run's seven stages chained by
    strict ancestry, that each phase added its own artifact, and that a
    verification record sat where it was declared - and never opened the two
    records the whole arrangement is about. A chain whose plan acceptance said
    actor_class: executor and Human_disposition: rejected passed with
    "seven stages chained and separated", while the mechanism refused the same
    record with exit 15. Topology was measured; acceptance was declared.

    The records are read at their own commits from the declared blob, so what is
    judged is what was published, not what happens to be in the working tree.
    The verdict is the mechanism's; this function resolves references and
    consumes an exit code.

    This runs last on purpose. A malformed chain should still report its own
    ordering, separation or blob diagnosis rather than every defect collapsing
    into one acceptance failure.
    """
    mech = _load_mechanism()
    task_id = run_doc.get("task_id")
    _require(isinstance(task_id, str) and task_id, REF,
             "run.yml must state task_id; without it an acceptance record cannot be bound to a "
             "task, and a record that simply omits the field would bind to nothing")
    for node in nodes:
        control = controls[node.stage_id]
        art = arts[node.stage_id]
        for phase in ("plan", "completion"):
            context = _acceptance_context(repo, node, control, art, task_id, phase)
            code, reason = mech.validate_stage_acceptance_context(context)
            _require(code == 0, ACCEPT,
                     f"{node.stage_id}: {phase} acceptance was refused by the deliberation "
                     f"mechanism ({reason}, exit {code}). The record is at "
                     f"{context['record_ref']['path']} in {context['record_ref']['commit'][:12]}. "
                     f"This gate does not restate what a Human acceptance is; it assembled the "
                     f"exact objects from the candidate, asked the owner, and the owner said no.")


ABSENT = "absent"
NOT_GOVERNED = "not_governed"
UNREADABLE = "unreadable"
EXEMPT = "exempt"
GOVERNED = "governed"


def run_state(repo: Path, ref: str, run_root: str, boundary: str | None) -> str:
    """How a run stands at one ref. Reads only what already exists.

    A run is governed when it has a seven-stage manifest and a readable identity
    whose base descends from the effective boundary. Everything else is named
    separately, because the difference between "was never a seven-stage run" and
    "was one and its identity is now unreadable" is the whole point of this
    function.
    """
    manifest = _load_yaml_at(repo, ref, f"{run_root}/manifest.yml")
    if manifest is None:
        run_doc = _load_yaml_at(repo, ref, f"{run_root}/run.yml")
        return ABSENT if run_doc is None else NOT_GOVERNED
    if not isinstance(manifest, dict):
        return UNREADABLE
    run_doc = _load_yaml_at(repo, ref, f"{run_root}/run.yml")
    if not isinstance(run_doc, dict):
        return UNREADABLE
    if boundary is None:
        return GOVERNED
    base = run_doc.get("base_sha")
    if not _is_sha(base):
        return UNREADABLE
    return GOVERNED if _strictly_precedes(repo, boundary, base) else EXEMPT


def check_governance_transition(repo: Path, base: str | None, candidate: str,
                                run_root: str, boundary: str | None,
                                findings: Findings) -> str | None:
    """Refuse a run that was governed at the base and is not at the candidate.

    Governance must not be something a candidate can drop by deleting a field. A
    run that was a governed seven-stage run stays one; removing its manifest, its
    run.yml, or the base it is placed by is a refusal, not a reclassification.

    With no base there is no transition to check, and that is not a hole. Escaping
    governance by deleting a declaration requires a published state to escape
    from. On the first push of a branch nothing about this run was ever published,
    so the candidate is judged on its own by the boundary and the full chain.

    A draft of this function used the run's own declared base_sha as a fallback
    anchor. It could never fire: base_sha names where the task started, which is
    by definition before the run existed, so the run was never governed there. The
    test that asserted the reason rather than only a nonzero exit is what caught
    it.
    """
    if base is None:
        return None
    if run_state(repo, base, run_root, boundary) != GOVERNED:
        return None
    state = run_state(repo, candidate, run_root, boundary)
    if state == GOVERNED:
        return None
    lost = {
        ABSENT: "the run directory is gone",
        NOT_GOVERNED: "its seven-stage manifest is gone",
        UNREADABLE: "its identity is missing or malformed",
        EXEMPT: "its declared base no longer descends from the effective boundary",
    }[state]
    return (f"{run_root}: governed at the base and not at the candidate, because {lost}. "
            f"A governed run does not stop being governed by dropping a declaration.")


def gate_run(repo: Path, candidate: str, run_root: str,
             boundary: str | None, findings: Findings) -> int:
    manifest = _load_yaml_at(repo, candidate, f"{run_root}/manifest.yml")
    if manifest is None:
        findings.skip()
        return PASS
    _require(isinstance(manifest, dict), REF, f"{run_root}: manifest is not a mapping")

    run_doc = _load_yaml_at(repo, candidate, f"{run_root}/run.yml")
    _require(isinstance(run_doc, dict), REF,
             f"{run_root}: has a manifest but no readable run.yml")

    if boundary is not None:
        base = run_doc.get("base_sha")
        _require(_is_sha(base), REF,
                 f"{run_root}: run.yml base_sha is missing or malformed, so exemption cannot be "
                 f"established. Unable to place a run is not the same as an exempt run.")
        if not _strictly_precedes(repo, boundary, base):
            # The run started at or before the boundary, so the rule does not
            # reach back to it. Ancestry decides this; history is never searched.
            findings.note(f"{run_root}: predates the effective boundary, exempt")
            return PASS

    nodes = _collect_nodes(repo, candidate, run_root, manifest, findings)
    controls: dict[str, dict] = {}
    arts: dict[str, dict] = {}
    entries = manifest["artifacts"]
    for item in entries:
        art = _load_yaml_at(repo, candidate, f"{run_root}/{item['path']}")
        controls[item["stage_id"]] = art["stage_control"]  # type: ignore[index]
        # The whole artifact is kept, not just stage_control. The stage receipt is
        # a required field of the artifact and the mechanism needs it to judge an
        # acceptance; re-reading it from a second location would be a second
        # source for one object.
        arts[item["stage_id"]] = art  # type: ignore[assignment]

    # C_7 comes from run.yml directly. There is no completion-pointer file in
    # this path at all.
    #
    # Two earlier revisions went through a pointer file: the first read
    # completion_pointer_v1.yml by name, which would have read a superseded
    # record; the second required run.yml to name which pointer was current.
    # Both were solving a problem the indirection itself created. Which record is
    # current is only a question when there are several, and 08_结论 accumulates
    # them: the precedent run carries four. A path at a commit resolves to
    # exactly one blob, so a field in run.yml has no currency question to answer.
    #
    # Pointer files keep their value as a human-readable ledger with supersession
    # history. The gate simply does not need them: it needs one commit id, and
    # the run states it.
    final_c = run_doc.get("final_stage_completion_commit")
    _require(_is_sha(final_c), REF,
             f"{run_root}: run.yml must state final_stage_completion_commit as a 40-character sha")
    nodes[-1].c = final_c

    _check_ordering(repo, nodes)
    _check_separation(repo, nodes, controls)
    _check_verification(repo, nodes, controls)
    _check_acceptance(repo, nodes, controls, arts, run_doc)
    findings.note(f"{run_root}: seven stages chained, separated and accepted")
    return PASS


def discover_runs(repo: Path, candidate: str) -> list[str]:
    """Enumerate every run root at the candidate.

    The caller never supplies a run root. If it could, omitting one would be the
    cheapest bypass available, and the omission would look exactly like a run that
    does not exist.

    Governance is decided by the boundary, not by which paths this push happens to
    touch. Deriving the set from a diff would let the base a caller passes narrow
    what gets judged.

    An absent 01_os/_runs tree means there are no governed runs. Any other git
    failure refuses: being unable to look is not the same as there being nothing
    to see, and an earlier revision of this function collapsed the two by catching
    every error and returning an empty list.
    """
    code, out, err = _git_try(repo, "ls-tree", "-d", "--name-only", f"{candidate}:{RUNS_ROOT}")
    if code != 0:
        if _looks_absent(err):
            return []
        raise GateError(REPO, f"cannot enumerate {RUNS_ROOT} at the candidate: {err.strip()[:200]}")
    names = [n for n in out.decode("utf-8").splitlines() if n.strip()]
    return [f"{RUNS_ROOT}/{n}" for n in names]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--boundary", default=None,
                        help="effective-from commit; runs whose base is not a descendant are exempt")
    parser.add_argument("--base", default=None,
                        help="the authentic publication base this candidate advances from. The "
                             "gate checks only that it strictly precedes the candidate; binding "
                             "it to the transport's real old head is the caller's job")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    findings = Findings()
    if not _is_sha(args.candidate):
        print("candidate must be a full 40-character commit sha", file=sys.stderr)
        return USAGE
    repo = args.repo_root.resolve()

    code = PASS
    try:
        if not _commit_exists(repo, args.candidate):
            raise GateError(REPO, "candidate is not a commit in this repository")
        base = args.base
        if base is not None:
            _require(_is_sha(base), USAGE, "base must be a full 40-character commit sha")
            _require(_commit_exists(repo, base), REPO, "base is not a commit in this repository")
            _require(_strictly_precedes(repo, base, args.candidate), USAGE,
                     "base must strictly precede the candidate")
        # Runs are taken from both refs. Taking them from the candidate alone
        # would mean a governed run deleted outright was simply never seen.
        runs = sorted(set(discover_runs(repo, args.candidate))
                      | (set(discover_runs(repo, base)) if base else set()))
        if not runs:
            findings.note("no run directories at the candidate; nothing for this gate to judge")
        # Every run is judged and every failure is reported. An earlier revision
        # stopped at the first one, so a caller saw a single defect, fixed it,
        # pushed again and met the next. The ledger discipline used elsewhere in
        # this repository asks for the whole population, not the first row.
        for run_root in runs:
            try:
                lost = check_governance_transition(repo, base, args.candidate, run_root,
                                                   args.boundary, findings)
                if lost is not None:
                    findings.note(lost)
                    result = CHAIN
                else:
                    result = gate_run(repo, args.candidate, run_root, args.boundary, findings)
            except GateError as exc:
                findings.note(f"{run_root}: {exc.reason}")
                result = exc.code
            if result != PASS and code == PASS:
                code = result
    except GateError as exc:
        code = exc.code
        findings.note(exc.reason)

    if args.json:
        print(json.dumps({"exit_code": code, "findings": findings.summary(),
                          "candidate": args.candidate}, ensure_ascii=False))
    else:
        for row in findings.summary():
            print(row, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
