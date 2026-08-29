#!/usr/bin/env python3
"""Freeze-receipt contract, closed against external evidence.

C-10 (externally_bound_receipt_closure).  The v1 contract closed ST04-V3-IR-001's
three parts — unparseable receipt, validator that never loaded it, ledger that
disagreed with the diff — and the independent review reproduced all three as
closed.  It then found seven ways the receipt still authorised itself:

    R11  changed_paths.count was never validated
    R12  a declared path could contain a dot-dot segment
    R13  an artifact hash path could escape the artifact root
    R14  candidate_sha was neither syntactically nor externally bound
    R15  the artifact hash ledger could be empty
    R16  duplicate artifact hash entries were accepted
    R17  the declared topology was returned but never compared

The direction of authority is the whole fix: every expected fact now comes from
OUTSIDE the receipt, and the receipt is checked against it.  A receipt may still
say anything; it can no longer make what it says true.

`self_hash_excluded` remains the answer to the ledger's self-reference, but the
sentinel is safe only when something external anchors the final bytes.  The full
call therefore binds the receipt's actual SHA-256 to a value read outside the
receipt (normally `git show <container>:<path>`).  The implementation candidate
SHA and the later receipt-container commit stay distinct; putting the latter
inside the receipt would recreate the impossible self-reference.

Artifact hashes follow the same direction of authority. The full call accepts a
path-to-SHA-256 mapping computed from immutable Git blobs. Hashing only the local
Windows worktree is insufficient because checkout line-ending conversion can
produce bytes different from the committed candidate.

Backward-compatible call shape: the external arguments are optional, so a caller
that supplies none still gets every internal-consistency, canonicalisation,
containment, syntax and topology-authorisation check.  Supplying them adds the
external bindings.  The independent probe suite calls the short form and must not
be edited, so the short form has to be strong on its own.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field as dc_field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .core import dump_yaml, load_yaml_strict_single
from .provenance import rule
from .topology import (
    FULL_CANDIDATE_TREE,
    FULL_DECLARED_SURFACE,
    ObservedExecution,
    compare_topology,
    observe_artifact_tree,
    observe_git_diff,
)

SELF_HASH_SENTINEL = rule(
    "V-REC-01",
    kind="mapping",
    authority="C-10 externally_bound_receipt_closure",
    interpretation=(
        "The sole sentinel allowed for the receipt's own changed-path entry. "
        "Final bytes must be anchored by an externally supplied SHA-256."
    ),
    value="self_hash_excluded",
)

REQUIRED_TOP_LEVEL = tuple(
    rule(
        "V-REC-02",
        kind="mapping",
        authority="C-10; R11-R17",
        interpretation="Required fields of the strict freeze-receipt contract.",
        value=(
            "schema_version", "receipt_version", "task_id", "run_id",
            "base_sha", "candidate_sha", "changed_paths", "artifact_hashes",
            "artifact_hash_scope", "topology",
        ),
    )
)

_SHA40 = re.compile(
    rule(
        "V-REC-03",
        kind="mapping",
        authority="C-10; R14",
        interpretation="Canonical lowercase forty-hex Git object identifier syntax.",
        value=r"^[0-9a-f]{40}$",
    )
)
_SHA256 = re.compile(
    rule(
        "V-REC-04",
        kind="mapping",
        authority="C-10 externally_bound_receipt_closure",
        interpretation="Canonical lowercase SHA-256 syntax for an external byte anchor.",
        value=r"^[0-9a-f]{64}$",
    )
)

FORBIDDEN_RELATIVE_PATH_SEGMENTS = frozenset(
    rule(
        "V-REC-05",
        kind="mapping",
        authority="C-10; R12",
        interpretation=(
            "Segments that make a ledger path non-canonical. An empty, current-"
            "directory or parent-directory segment requires resolution and is rejected."
        ),
        value={"", ".", ".."},
    )
)
_WINDOWS_DRIVE_PATTERN = rule(
    "V-REC-06",
    kind="mapping",
    authority="C-10; R12",
    interpretation="Windows drive-prefixed paths are absolute, not repository-relative ledger paths.",
    value=r"^[A-Za-z]:",
)
_WINDOWS_DRIVE = re.compile(_WINDOWS_DRIVE_PATTERN)
FORBIDDEN_LEDGER_SEPARATOR = rule(
    "V-REC-07",
    kind="mapping",
    authority="C-10; R12",
    interpretation="Ledger paths use Git's forward-slash repository spelling; backslash is rejected.",
    value="\\",
)
EXTERNAL_CLOSURE_FIELDS = frozenset(
    rule(
        "V-REC-08",
        kind="mapping",
        authority="C-10; C-11",
        interpretation="External facts required before complete receipt closure may be claimed.",
        value={
            "base_sha", "candidate_sha", "receipt_sha256", "diff_paths",
            "artifact_hashes", "hash_scope", "topology",
        },
    )
)


def is_sha40(value: Any) -> bool:
    return isinstance(value, str) and bool(_SHA40.match(value.strip()))


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(_SHA256.match(value.strip()))


def is_canonical_relpath(value: Any) -> bool:
    """A repository-relative path with no way to mean something else.

    Rejects absolute paths, drive letters, backslashes, empty segments and any
    `.` or `..` segment.  R12 declared `dir/../a.txt`, which set-compares equal
    to `a.txt` only if the comparison happens to normalise — and equal to nothing
    at all if it does not.  A ledger entry that needs resolving is not a ledger.
    """
    if not isinstance(value, str) or not value:
        return False
    if value != value.strip():
        return False
    if FORBIDDEN_LEDGER_SEPARATOR in value or value.startswith("/") or _WINDOWS_DRIVE.match(value):
        return False
    segments = value.split("/")
    if any(s in FORBIDDEN_RELATIVE_PATH_SEGMENTS for s in segments):
        return False
    return True


def _contained(root: Path, rel: str) -> bool:
    """True when `rel` resolves inside `root`.  R13's escape check."""
    try:
        target = (root / rel).resolve()
        base = root.resolve()
    except (OSError, ValueError):
        return False
    return target == base or base in target.parents


@dataclass
class ReceiptValidation:
    strict_yaml_parsed: bool
    parse_error: str | None
    required_fields_present: bool
    missing_fields: list[str]
    ledger_matches_diff: bool
    declared_paths: list[str]
    actual_paths: list[str]
    self_entry_present: bool
    self_hash_recursion_avoided: bool
    artifact_hash_mismatches: list[str]
    topology_declared: str | None
    # C-10 additions
    declared_count_matches: bool = True
    paths_canonical: bool = True
    paths_unique: bool = True
    artifact_paths_contained: bool = True
    artifact_paths_unique: bool = True
    hash_scope_complete: bool = True
    sha_syntax_valid: bool = True
    external_bindings_hold: bool = True
    receipt_bytes_binding_holds: bool = True
    external_artifact_bindings_hold: bool = True
    execution_provenance_holds: bool = True
    external_closure_complete: bool = False
    topology_comparison_holds: bool = True
    topology_comparison_detail: str = ""
    external_bindings_checked: tuple[str, ...] = ()
    failures: list[str] = dc_field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.failures

    def as_dict(self) -> dict[str, Any]:
        return {
            "strict_yaml_parsed": self.strict_yaml_parsed,
            "parse_error": self.parse_error,
            "required_fields_present": self.required_fields_present,
            "missing_fields": self.missing_fields,
            "ledger_matches_diff": self.ledger_matches_diff,
            "declared_path_count": len(self.declared_paths),
            "actual_path_count": len(self.actual_paths),
            "self_entry_present": self.self_entry_present,
            "self_hash_recursion_avoided": self.self_hash_recursion_avoided,
            "artifact_hash_mismatches": self.artifact_hash_mismatches,
            "topology_declared": self.topology_declared,
            "declared_count_matches": self.declared_count_matches,
            "paths_canonical": self.paths_canonical,
            "paths_unique": self.paths_unique,
            "artifact_paths_contained": self.artifact_paths_contained,
            "artifact_paths_unique": self.artifact_paths_unique,
            "hash_scope_complete": self.hash_scope_complete,
            "sha_syntax_valid": self.sha_syntax_valid,
            "external_bindings_hold": self.external_bindings_hold,
            "receipt_bytes_binding_holds": self.receipt_bytes_binding_holds,
            "external_artifact_bindings_hold": self.external_artifact_bindings_hold,
            "execution_provenance_holds": self.execution_provenance_holds,
            "external_closure_complete": self.external_closure_complete,
            "external_bindings_checked": list(self.external_bindings_checked),
            "topology_comparison_holds": self.topology_comparison_holds,
            "topology_comparison_detail": self.topology_comparison_detail,
            "failures": list(self.failures),
            "valid": self.valid,
        }


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_receipt(
    *,
    task_id: str,
    run_id: str,
    base_sha: str,
    candidate_sha: str,
    changed_paths: list[str],
    receipt_rel_path: str,
    artifact_root: Path,
    artifact_rel_paths: list[str],
    topology: str,
) -> dict[str, Any]:
    """Build a receipt whose ledger includes itself without hashing itself.

    `artifact_hash_scope` is new and is what makes an empty ledger detectable
    (R15): the scope states what the receipt CLAIMS to cover, so a ledger that
    covers less is a contradiction inside one document rather than an absence
    nobody can see.
    """
    ledger = []
    for rel in sorted(set(changed_paths) | {receipt_rel_path}):
        entry: dict[str, Any] = {"path": rel}
        if rel == receipt_rel_path:
            entry["sha256"] = SELF_HASH_SENTINEL
            entry["note"] = "the receipt cannot contain the digest of its own final bytes"
        ledger.append(entry)

    scope = sorted(set(artifact_rel_paths))
    artifacts = []
    for rel in scope:
        p = artifact_root / rel
        artifacts.append({"path": rel, "sha256": sha256_file(p) if p.is_file() else None})

    return {
        "schema_version": "citystate.stage04.freeze_receipt.v3",
        "receipt_version": 3,
        "task_id": task_id,
        "run_id": run_id,
        "base_sha": base_sha,
        "candidate_sha": candidate_sha,
        "changed_paths": {
            "count": len(ledger),
            "self_entry_included": True,
            "entries": ledger,
        },
        "artifact_hashes": artifacts,
        "artifact_hash_scope": {
            "declared_paths": scope,
            "complete": True,
        },
        "topology": topology,
        "receipt_must_be_loaded_by_package_validator": True,
    }


def write_receipt(path: Path, receipt: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write canonical LF bytes even on Windows. The external anchor hashes the
    # Git blob; platform newline translation would otherwise make the worktree
    # file and committed object different byte strings.
    path.write_bytes(dump_yaml(receipt).encode("utf-8"))


def git_changed_paths(repo_root: Path, base: str, candidate: str) -> list[str]:
    return list(observe_git_diff(repo_root, base, candidate).diff_paths)


def _parse_failure(actual_changed_paths: Sequence[str], error: str) -> ReceiptValidation:
    return ReceiptValidation(
        strict_yaml_parsed=False,
        parse_error=error,
        required_fields_present=False,
        missing_fields=list(REQUIRED_TOP_LEVEL),
        ledger_matches_diff=False,
        declared_paths=[],
        actual_paths=sorted(actual_changed_paths),
        self_entry_present=False,
        self_hash_recursion_avoided=False,
        artifact_hash_mismatches=[],
        topology_declared=None,
        failures=[f"strict_yaml_parse: {error}"],
    )


def validate_receipt(
    receipt_path: Path,
    *,
    actual_changed_paths: Iterable[str],
    receipt_rel_path: str,
    artifact_root: Path,
    expected_base_sha: str | None = None,
    expected_candidate_sha: str | None = None,
    expected_receipt_sha256: str | None = None,
    observed_execution: ObservedExecution | None = None,
    expected_artifact_hashes: Mapping[str, str] | None = None,
    expected_hash_scope: Iterable[str] | None = None,
) -> ReceiptValidation:
    """Check a receipt against facts supplied from outside it.

    Authority direction is outside -> receipt.  Every argument after
    `receipt_path` is an external observation; nothing the receipt says about
    itself is taken as establishing anything.
    """
    receipt_digest = sha256_file(receipt_path)
    text = receipt_path.read_text(encoding="utf-8")
    try:
        data = load_yaml_strict_single(text)
    except Exception as exc:
        return _parse_failure(list(actual_changed_paths), f"{type(exc).__name__}: {exc}")

    if not isinstance(data, dict):
        data = {}
    failures: list[str] = []
    checked: list[str] = []

    missing = [f for f in REQUIRED_TOP_LEVEL if f not in data]
    if missing:
        failures.append(f"missing_required_fields: {missing}")

    # ---- changed-path ledger -------------------------------------------------
    changed_value = data.get("changed_paths")
    changed = changed_value if isinstance(changed_value, dict) else {}
    ledger_value = changed.get("entries")
    ledger = ledger_value if isinstance(ledger_value, list) else []
    entries = [e for e in ledger if isinstance(e, dict)]
    declared_raw = [str(e.get("path")) for e in entries]
    declared = sorted(declared_raw)
    actual = sorted(set(actual_changed_paths))

    # R11 — the declared count is an assertion about the ledger, so check it.
    declared_count = changed.get("count")
    count_ok = isinstance(declared_count, int) and declared_count == len(entries)
    if not count_ok:
        failures.append(
            f"declared_changed_path_count {declared_count!r} != {len(entries)} ledger entries"
        )

    # R12 — canonical form, then containment, then set equality.
    noncanonical = [p for p in declared_raw if not is_canonical_relpath(p)]
    if noncanonical:
        failures.append(f"noncanonical_changed_paths: {noncanonical[:4]}")
    paths_unique = len(declared_raw) == len(set(declared_raw))
    if not paths_unique:
        failures.append("duplicate_changed_path_entries")

    ledger_matches = declared == actual
    if not ledger_matches:
        failures.append(
            f"ledger_does_not_match_diff: declared={len(declared)} actual={len(actual)}"
        )

    # ---- self entry ----------------------------------------------------------
    self_entries = [e for e in entries if e.get("sha256") == SELF_HASH_SENTINEL]
    self_entry = next((e for e in entries if e.get("path") == receipt_rel_path), None)
    self_present = self_entry is not None
    self_ok = bool(self_entry) and self_entry.get("sha256") == SELF_HASH_SENTINEL
    if not self_present:
        failures.append("receipt_not_declared_in_its_own_ledger")
    elif not self_ok:
        failures.append("receipt_self_entry_carries_a_digest_of_its_own_bytes")
    if len(self_entries) > 1 or any(
        e.get("path") != receipt_rel_path for e in self_entries
    ):
        # C-10: the sentinel is safe only for the unique receipt entry.
        failures.append("self_hash_sentinel_used_outside_the_unique_receipt_entry")

    # ---- artifact hashes -----------------------------------------------------
    artifact_value = data.get("artifact_hashes")
    artifact_entries = [
        e for e in (artifact_value if isinstance(artifact_value, list) else [])
        if isinstance(e, dict)
    ]
    artifact_paths = [str(e.get("path")) for e in artifact_entries]
    mismatches: list[str] = []
    escaped: list[str] = []
    external_artifact_binding_ok = True
    external_hashes = dict(expected_artifact_hashes or {})
    if expected_artifact_hashes is not None:
        checked.append("artifact_hashes")
        invalid_expected_hashes = [
            path for path, digest in external_hashes.items()
            if not is_canonical_relpath(path) or not is_sha256(digest)
        ]
        if invalid_expected_hashes:
            external_artifact_binding_ok = False
            failures.append(
                f"external_artifact_hash_expectations_invalid: {invalid_expected_hashes[:4]}"
            )
    for entry in artifact_entries:
        rel = str(entry.get("path"))
        if not is_canonical_relpath(rel) or not _contained(artifact_root, rel):
            escaped.append(rel)
            continue
        p = artifact_root / rel
        if expected_artifact_hashes is not None:
            actual_hash = external_hashes.get(rel)
        else:
            actual_hash = sha256_file(p) if p.is_file() else None
        if entry.get("sha256") != actual_hash:
            mismatches.append(rel)
    if escaped:
        failures.append(f"artifact_hash_path_outside_artifact_root: {escaped[:4]}")
    if mismatches:
        failures.append(f"artifact_hash_mismatch: {mismatches[:4]}")
    artifact_unique = len(artifact_paths) == len(set(artifact_paths))
    if not artifact_unique:
        failures.append("duplicate_artifact_hash_entries")
    if expected_artifact_hashes is not None and set(artifact_paths) != set(external_hashes):
        external_artifact_binding_ok = False
        failures.append("artifact_hash_ledger_does_not_match_external_git_blob_scope")
    if mismatches and expected_artifact_hashes is not None:
        external_artifact_binding_ok = False

    # ---- hash scope (R15) ----------------------------------------------------
    scope_value = data.get("artifact_hash_scope")
    scope_block = scope_value if isinstance(scope_value, dict) else {}
    scope_paths_value = scope_block.get("declared_paths")
    scope_declared = [
        str(p)
        for p in (scope_paths_value if isinstance(scope_paths_value, list) else [])
        if isinstance(p, str)
    ]
    scope_complete = bool(scope_block.get("complete")) and bool(scope_declared)
    if not scope_complete:
        failures.append("artifact_hash_scope_is_absent_empty_or_not_declared_complete")
    elif sorted(set(scope_declared)) != sorted(set(artifact_paths)):
        failures.append(
            f"artifact_hash_ledger_does_not_cover_its_declared_scope: "
            f"scope={len(set(scope_declared))} hashed={len(set(artifact_paths))}"
        )

    # ---- SHA syntax and external binding (R14) -------------------------------
    sha_ok = is_sha40(data.get("base_sha")) and is_sha40(data.get("candidate_sha"))
    if not sha_ok:
        failures.append(
            f"sha_not_40_hex: base={data.get('base_sha')!r} candidate={data.get('candidate_sha')!r}"
        )
    bindings_hold = external_artifact_binding_ok
    receipt_binding_holds = True
    provenance_holds = True
    if expected_base_sha is not None:
        checked.append("base_sha")
        if not is_sha40(expected_base_sha) or str(data.get("base_sha")).strip() != expected_base_sha.strip():
            bindings_hold = False
            failures.append("base_sha_does_not_match_the_externally_supplied_expectation")
    if expected_candidate_sha is not None:
        checked.append("candidate_sha")
        if not is_sha40(expected_candidate_sha) or str(data.get("candidate_sha")).strip() != expected_candidate_sha.strip():
            bindings_hold = False
            failures.append("candidate_sha_does_not_match_the_externally_supplied_expectation")
    if expected_receipt_sha256 is not None:
        checked.append("receipt_sha256")
        if not is_sha256(expected_receipt_sha256) or receipt_digest != expected_receipt_sha256:
            receipt_binding_holds = False
            bindings_hold = False
            failures.append("receipt_bytes_do_not_match_the_external_sha256_anchor")

    if observed_execution is not None:
        observed_fields = (
            ("base_sha", observed_execution.base_sha, data.get("base_sha")),
            ("candidate_sha", observed_execution.candidate_sha, data.get("candidate_sha")),
            ("receipt_sha256", observed_execution.receipt_sha256, receipt_digest),
        )
        for fact_name, observed_value, declared_value in observed_fields:
            if observed_value is None:
                continue
            if not observed_execution.has_observation(fact_name, str(observed_value)):
                provenance_holds = False
                bindings_hold = False
                failures.append(f"observed_{fact_name}_has_no_execution_provenance")
                continue
            checked.append(f"observed_{fact_name}")
            if str(observed_value) != str(declared_value):
                bindings_hold = False
                if fact_name == "receipt_sha256":
                    receipt_binding_holds = False
                failures.append(f"receipt_does_not_match_observed_{fact_name}")

        if observed_execution.has_observation("diff_paths"):
            checked.append("diff_paths")
            if sorted(set(observed_execution.diff_paths)) != declared:
                bindings_hold = False
                failures.append("ledger_does_not_match_the_externally_observed_diff")
        elif observed_execution.diff_paths:
            provenance_holds = False
            bindings_hold = False
            failures.append("observed_diff_paths_have_no_execution_provenance")
    if expected_hash_scope is not None:
        checked.append("hash_scope")
        if sorted(set(expected_hash_scope)) != sorted(set(artifact_paths)):
            bindings_hold = False
            failures.append("artifact_hash_ledger_does_not_match_the_expected_hash_scope")

    # ---- topology (R17 / C-07) ----------------------------------------------
    declared_topology = data.get("topology")
    filesystem_observation = observe_artifact_tree(artifact_root)
    if observed_execution is None or observed_execution.topology is None:
        # The short call can check whether the declared topology is authorized
        # and whether its scope obligation holds, but it cannot claim which
        # topology was executed. That external closure remains explicitly false.
        observed_topology_arg = None
    else:
        if observed_execution.has_observation("topology", observed_execution.topology):
            observed_topology_arg = observed_execution.topology
            checked.append("topology")
        else:
            observed_topology_arg = filesystem_observation.topology
            provenance_holds = False
            bindings_hold = False
            failures.append("observed_topology_has_no_execution_provenance")
    topo_ok, topo_detail = compare_topology(
        declared_topology if isinstance(declared_topology, str) else None,
        observed_topology_arg,
        declared_scope=tuple(sorted(set(artifact_paths))),
        observed_paths=filesystem_observation.artifact_paths,
    )
    if not topo_ok:
        failures.append(f"topology: {topo_detail}")

    external_closure_complete = (
        EXTERNAL_CLOSURE_FIELDS <= set(checked)
        and bindings_hold
        and receipt_binding_holds
        and provenance_holds
        and topo_ok
    )

    return ReceiptValidation(
        strict_yaml_parsed=True,
        parse_error=None,
        required_fields_present=not missing,
        missing_fields=missing,
        ledger_matches_diff=ledger_matches,
        declared_paths=declared,
        actual_paths=actual,
        self_entry_present=self_present,
        self_hash_recursion_avoided=self_ok,
        artifact_hash_mismatches=mismatches,
        topology_declared=declared_topology if isinstance(declared_topology, str) else None,
        declared_count_matches=count_ok,
        paths_canonical=not noncanonical,
        paths_unique=paths_unique,
        artifact_paths_contained=not escaped,
        artifact_paths_unique=artifact_unique,
        hash_scope_complete=scope_complete,
        sha_syntax_valid=sha_ok,
        external_bindings_hold=bindings_hold,
        receipt_bytes_binding_holds=receipt_binding_holds,
        external_artifact_bindings_hold=external_artifact_binding_ok,
        execution_provenance_holds=provenance_holds,
        external_closure_complete=external_closure_complete,
        topology_comparison_holds=topo_ok,
        topology_comparison_detail=topo_detail,
        external_bindings_checked=tuple(checked),
        failures=failures,
    )
