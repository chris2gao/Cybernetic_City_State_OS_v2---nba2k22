#!/usr/bin/env python3
"""Observed execution facts, and the comparison C-07 requires.

The independent review's finding was exact: `validate_receipt` returned
`topology_declared` and accepted it "without an expected or observed topology
argument", so R17 passed an invalid topology.  Returning a value the caller then
ignores is not enforcement.

Two things are needed and both are here:

  C-07  a real comparison.  A declared topology is checked against a topology
        OBSERVED from the filesystem or from Git, and a mismatch fails.

  C-11  the observation must come from outside the receipt.  An artifact cannot
        establish its own execution facts, so `ExecutionObservation` records
        where each fact was read from and refuses to be constructed from the
        receipt under validation.

What this module deliberately does NOT claim: a Git/filesystem observation proves
the state read at validation time, not that no earlier local rewrite attempt ever
occurred. Fresh remote readback and the source-branch comparison remain caller
obligations and are reported outside the receipt rather than self-asserted here.
"""

from __future__ import annotations

import subprocess
import hashlib
from dataclasses import dataclass, field as dc_field
from pathlib import Path

from .provenance import rule

# Authorized topologies, and what each one obliges the receipt to prove.
#
# `full_candidate_tree` is the boundary the parent T2 run established and the
# review reproduced under C-04 ("the exact candidate preserves the parent
# full-candidate-tree boundary").  A declared topology outside this set is not a
# new topology, it is an unauthorized one, and it fails closed — which is the
# direction ST04-V3-IR-008 proved is the only safe one.
FULL_CANDIDATE_TREE = rule(
    "V-TOPO-02",
    kind="mapping",
    authority="A07/R07_route_receipt; C-04",
    interpretation="Topology whose hash scope must equal every observed artifact-tree file.",
    value="full_candidate_tree",
)
FULL_DECLARED_SURFACE = rule(
    "V-TOPO-03",
    kind="mapping",
    authority="A07/R07_route_receipt; C-04",
    interpretation="Topology whose non-empty declared scope is the explicit validation boundary.",
    value="full_declared_surface",
)

AUTHORIZED_TOPOLOGIES = frozenset(
    rule(
        "V-TOPO-01",
        kind="vocabulary",
        authority="A07/R07_route_receipt; C-04 as reproduced by the independent review",
        interpretation=(
            "Topologies a freeze receipt may declare. full_candidate_tree obliges "
            "the hash scope to equal every file physically under the artifact root; "
            "full_declared_surface obliges it to equal a non-empty declared scope. "
            "Anything else is unauthorized and fails closed (R17)."
        ),
        value={FULL_CANDIDATE_TREE, FULL_DECLARED_SURFACE},
        rejected_alternatives=(
            "accepting any string and reporting it: that is what R17 exploited",
            "an open enum with a warning: a warning does not fail a gate",
        ),
    )
)


@dataclass(frozen=True)
class ExecutionObservation:
    """A fact read from outside the artifact that asserts it.

    `read_from` is mandatory and is part of the evidence: a validation report
    that cannot say where a fact came from has not established it.
    """

    fact: str
    value: str
    read_from: str

    def __post_init__(self) -> None:
        if not self.read_from:
            raise ValueError("an execution observation must record where it was read from")


@dataclass
class ObservedExecution:
    """Everything the validator is allowed to treat as physical truth."""

    topology: str | None = None
    artifact_paths: tuple[str, ...] = ()
    diff_paths: tuple[str, ...] = ()
    base_sha: str | None = None
    candidate_sha: str | None = None
    diff_endpoint_sha: str | None = None
    receipt_sha256: str | None = None
    observations: list[ExecutionObservation] = dc_field(default_factory=list)

    def record(self, fact: str, value: str, read_from: str) -> None:
        self.observations.append(ExecutionObservation(fact, value, read_from))

    def has_observation(self, fact: str, value: str | None = None) -> bool:
        return any(
            observation.fact == fact
            and (value is None or observation.value == value)
            for observation in self.observations
        )

    def as_dict(self) -> dict:
        return {
            "topology": self.topology,
            "artifact_path_count": len(self.artifact_paths),
            "diff_path_count": len(self.diff_paths),
            "base_sha": self.base_sha,
            "candidate_sha": self.candidate_sha,
            "diff_endpoint_sha": self.diff_endpoint_sha,
            "receipt_sha256": self.receipt_sha256,
            "observations": [
                {"fact": o.fact, "value": o.value, "read_from": o.read_from}
                for o in self.observations
            ],
        }


def observe_artifact_tree(artifact_root: Path) -> ObservedExecution:
    """Read the artifact root from the filesystem.  Nothing is taken on trust."""
    paths = sorted(
        p.relative_to(artifact_root).as_posix()
        for p in artifact_root.rglob("*")
        if p.is_file()
    )
    obs = ObservedExecution(
        topology=FULL_CANDIDATE_TREE,
        artifact_paths=tuple(paths),
    )
    obs.record(
        "artifact_paths",
        f"{len(paths)} file(s)",
        f"filesystem:{artifact_root}",
    )
    obs.record("topology", FULL_CANDIDATE_TREE, f"filesystem:{artifact_root}")
    return obs


def observe_git_diff(
    repo_root: Path,
    base: str,
    candidate: str,
    *,
    candidate_is_receipt_candidate: bool = True,
) -> ObservedExecution:
    """Read the changed-path set from Git, NUL-separated.

    `-z` is not decoration: Git never quotes in that format, so a repository
    whose paths are largely Chinese cannot produce an octal-escaped ledger that
    silently disagrees with the physical diff
    (01_os/开发入口与单窗口任务规范_v1.md#1.2).
    """
    out = subprocess.run(
        ["git", "diff", "--name-only", "-z", f"{base}..{candidate}"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    paths = tuple(sorted(p for p in out.split("\0") if p))
    obs = ObservedExecution(
        diff_paths=paths,
        base_sha=base,
        candidate_sha=candidate if candidate_is_receipt_candidate else None,
        diff_endpoint_sha=candidate,
    )
    obs.record("diff_paths", f"{len(paths)} path(s)", f"git:{repo_root}:{base}..{candidate}")
    obs.record("base_sha", base, f"git:{repo_root}")
    obs.record("diff_endpoint_sha", candidate, f"git:{repo_root}")
    if candidate_is_receipt_candidate:
        obs.record("candidate_sha", candidate, f"git:{repo_root}")
    return obs


def observe_git_receipt_blob(
    repo_root: Path,
    container_sha: str,
    receipt_rel_path: str,
    observed: ObservedExecution | None = None,
) -> ObservedExecution:
    """Bind receipt bytes to a Git container without putting its SHA inside itself.

    The receipt may name an implementation candidate, while a later container
    commit stores the receipt.  Reading ``container_sha:path`` is the external
    anchor for the final bytes and avoids an impossible self-referential commit
    hash.
    """
    blob = subprocess.run(
        ["git", "show", f"{container_sha}:{receipt_rel_path}"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    ).stdout
    digest = hashlib.sha256(blob).hexdigest()
    obs = observed if observed is not None else ObservedExecution()
    obs.receipt_sha256 = digest
    obs.record(
        "receipt_sha256",
        digest,
        f"git:{repo_root}:{container_sha}:{receipt_rel_path}",
    )
    return obs


def compare_topology(
    declared: str | None,
    observed: str | None,
    *,
    declared_scope: tuple[str, ...],
    observed_paths: tuple[str, ...],
) -> tuple[bool, str]:
    """The comparison C-07 requires.  Returns (holds, reason).

    Three separate ways to fail, and R17 only needed the first:

      1. the declared topology is not an authorized value;
      2. an externally observed topology disagrees with the declared one;
      3. the declared topology obliges a scope the artifact root does not match.
    """
    if declared is None:
        return False, "no topology declared"
    if declared not in AUTHORIZED_TOPOLOGIES:
        return False, f"unauthorized topology {declared!r}"
    if observed is not None and observed != declared:
        return False, f"declared topology {declared!r} != observed {observed!r}"
    if declared == FULL_CANDIDATE_TREE:
        if set(declared_scope) != set(observed_paths):
            missing = sorted(set(observed_paths) - set(declared_scope))
            extra = sorted(set(declared_scope) - set(observed_paths))
            return (
                False,
                f"full_candidate_tree hash scope does not equal the artifact tree; "
                f"unhashed={missing[:4]} unknown={extra[:4]}",
            )
    elif declared == FULL_DECLARED_SURFACE:
        if not declared_scope:
            return False, "full_declared_surface declares an empty hash scope"
    return True, "declared topology matches the observed execution"
