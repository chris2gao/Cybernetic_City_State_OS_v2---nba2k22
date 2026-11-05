#!/usr/bin/env python3
"""Normalize frozen BIC A0/A v2 into the Core Stage01 payload; no game or source edits.

This is a payload-level canonicalization and Core requirement_findings check.
It does NOT create stage_control, fabricate acceptance, or claim 7-stage runner PASS.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import yaml

SOURCE_COMMIT = "90d1801003e7a49531ef377137a2a975125bdd06"
CORE_TESTED_COMMIT = "08d8e534a3438269aa7d7eb1b080ab11c172f462"
SOURCE_DIR = "01_os/07_content/_runs/run-20261104-nba2k22-basketball-intelligence-core-requirement-001/requirement"
REQUIRED_BLOBS = {
    "01a_A0_consensus_v1.json": "d87eb0385fe359661f3efd4d88f3dfa903972ab1",
    "01a_Human_confirmation_v1.json": "c0092663d590903e0d2779ebe79b1459a2d23480",
    "01b_requirement_result_A_candidate_v2.json": "e16fdf6c4ef69b0a90b8c4abd3856617030a7ae4",
    "01b_Human_confirmation_v2.json": "0deae6d2e841d6674e91a81cedd5a221f1f0647f",
}
ALLOWED_EVIDENCE = {
    "human_requirement", "source_observed", "static_source", "offline_verified",
    "live_effect_verified", "independently_reviewed", "candidate_inference",
}
EXPLICIT_DOWNGRADES = {
    "human_reported_observation": "candidate_inference",
    "human_unverified_causal_hypothesis": "candidate_inference",
    "human_domain_assertion_unverified_this_session": "candidate_inference",
    "human_mechanism_claim_requires_verification": "candidate_inference",
    "human_mechanism_assertion_not_independently_verified": "candidate_inference",
    "human_domain_assertion_requires_mechanism_verification": "candidate_inference",
}
REQUIRED_KEYS = (
    "requirement_id", "objective", "success_criteria", "constraints",
    "consensus_A0", "consensus_Human_confirmation", "requirement_result_A",
    "Human_confirmation",
)


def git_output(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], stderr=subprocess.PIPE
    )


def pinned_json(repo: Path, filename: str) -> tuple[dict, bytes]:
    blob = REQUIRED_BLOBS[filename]
    repo_path = SOURCE_DIR + "/" + filename
    at_commit = git_output(repo, "rev-parse", f"{SOURCE_COMMIT}:{repo_path}").decode().strip()
    if at_commit != blob:
        raise ValueError(f"IMMUTABLE_SOURCE_MISMATCH {filename}: expected {blob}, got {at_commit}")
    raw = git_output(repo, "cat-file", "blob", blob)
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"NOT_AN_OBJECT {filename}")
    return obj, raw


def digest(value: object) -> str:
    data = yaml.safe_dump(value, allow_unicode=True, sort_keys=True, width=4096).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def core_stage01_check(payload: dict, core_root: Path) -> list[str]:
    runner = core_root / "01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py"
    if not runner.is_file():
        raise FileNotFoundError(f"CORE_RUNNER_NOT_FOUND: {runner}")
    spec = importlib.util.spec_from_file_location("bic_core_stage01_runner", runner)
    if spec is None or spec.loader is None:
        raise RuntimeError("CORE_RUNNER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected_a0 = module.normalized_sha256(payload["consensus_A0"])
    if expected_a0 != payload["consensus_Human_confirmation"]["content_sha256"]:
        raise ValueError("NORMALIZED_A0_DIGEST_MISMATCH")
    expected_a = module.requirement_confirmation_digest(payload)
    if expected_a != payload["Human_confirmation"]["content_sha256"]:
        raise ValueError("NORMALIZED_FULL_DIGEST_MISMATCH")
    return module.requirement_findings(payload, 2)


def generate(repo: Path, core_root: Path) -> tuple[dict, dict]:
    old_a0, raw_a0 = pinned_json(repo, "01a_A0_consensus_v1.json")
    h0, _ = pinned_json(repo, "01a_Human_confirmation_v1.json")
    source, raw_source = pinned_json(repo, "01b_requirement_result_A_candidate_v2.json")
    ha, _ = pinned_json(repo, "01b_Human_confirmation_v2.json")

    if h0.get("confirmed") is not True or ha.get("confirmed") is not True:
        raise ValueError("DUAL_HUMAN_CONFIRMATION_MISSING")
    if source.get("Human_confirmation", {}).get("confirmed") is not False:
        raise ValueError("EXPECTED_APPROVED_CANDIDATE_TO_BE_UNMODIFIED_PENDING_SOURCE")
    if ha.get("approved_content", {}).get("git_blob_sha1") != REQUIRED_BLOBS["01b_requirement_result_A_candidate_v2.json"]:
        raise ValueError("HUMAN_APPROVAL_NOT_BOUND_TO_EXACT_CANDIDATE")
    if ha["approved_content"].get("raw_file_sha256") != hashlib.sha256(raw_source).hexdigest():
        raise ValueError("APPROVAL_RAW_SHA256_MISMATCH")
    if h0.get("content_sha256") != hashlib.sha256(raw_a0).hexdigest():
        raise ValueError("A0_RAW_SHA256_MISMATCH")
    if source["consensus_A0"]["model_id"] != old_a0["model_id"]:
        raise ValueError("A0_IDENTITY_MISMATCH")

    a0 = copy.deepcopy(source["consensus_A0"])
    result = copy.deepcopy(source["requirement_result_A"])
    if result.get("model_id") != "NBA2K22-BIC-A-001" or result.get("version") != 2:
        raise ValueError("WRONG_APPROVED_A_VERSION")
    a0_digest = digest(a0)
    h0ref, haref = h0.get("confirmation_ref"), ha.get("confirmation_ref")
    if not isinstance(h0ref, str) or not isinstance(haref, str) or not h0ref or not haref or h0ref == haref:
        raise ValueError("HUMAN_REFERENCES_NOT_DISTINCT")
    result["consensus_ref"] = {
        "model_id": a0["model_id"],
        "version": a0["version"],
        "sha256": a0_digest,
        "confirmation_ref": h0ref,
    }

    conversions = []
    for item in result["result_items"]:
        for fact in item["known_facts"]:
            before = fact["evidence_status"]
            if before in ALLOWED_EVIDENCE:
                continue
            if before not in EXPLICIT_DOWNGRADES:
                raise ValueError(f"UNREVIEWED_EVIDENCE_STATUS {item['result_item_id']}:{before}")
            fact["original_evidence_status"] = before
            fact["evidence_status"] = EXPLICIT_DOWNGRADES[before]
            fact["normalization_note"] = (
                "Conservative status for a Human-reported observation or unverified mechanism "
                "assertion. Original provenance retained; no independent Native proof inferred."
            )
            conversions.append({
                "result_item_id": item["result_item_id"],
                "original_evidence_status": before,
                "machine_evidence_status": fact["evidence_status"],
            })

    payload = {
        "requirement_id": source["requirement_id"],
        "objective": source["objective"],
        "success_criteria": copy.deepcopy(source["success_criteria"]),
        "constraints": copy.deepcopy(source["constraints"]),
        "consensus_A0": a0,
        "consensus_Human_confirmation": {
            "confirmed": True, "model_kind": "consensus_A0",
            "model_id": a0["model_id"], "artifact_version": a0["version"],
            "content_sha256": a0_digest, "confirmation_ref": h0ref,
        },
        "requirement_result_A": result,
        "Human_confirmation": {},
        # Maintain all supporting reviewed semantics without promoting source status.
        "approved_candidate_context": {
            "candidate_kind": source.get("candidate_kind"),
            "candidate_version": source.get("candidate_version"),
            "source_status_at_approval": source.get("status"),
            "schema_basis": source.get("schema_basis"),
            "stage": source.get("stage"),
            "review_metadata": copy.deepcopy(source.get("review_metadata")),
        },
    }
    content_without_approvals = {k: v for k, v in payload.items() if k not in {
        "Human_confirmation", "consensus_Human_confirmation"
    }}
    a_digest = digest(content_without_approvals)
    payload["Human_confirmation"] = {
        "confirmed": True, "model_kind": "requirement_result_A",
        "model_id": result["model_id"], "artifact_version": result["version"],
        "content_sha256": a_digest, "confirmation_ref": haref,
    }

    findings = core_stage01_check(payload, core_root)
    report = {
        "status": "PAYLOAD_CORE_STAGE01_CHECK_PASS" if not findings else "PAYLOAD_CORE_STAGE01_CHECK_FAIL",
        "core_runner_used": str(core_root / "01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py"),
        "core_baseline_at_authoring": CORE_TESTED_COMMIT,
        "source_commit": SOURCE_COMMIT,
        "source_git_blobs": REQUIRED_BLOBS,
        "A0_original_raw_sha256": hashlib.sha256(raw_a0).hexdigest(),
        "A_original_raw_sha256": hashlib.sha256(raw_source).hexdigest(),
        "consensus_A0_normalized_sha256": a0_digest,
        "complete_requirement_payload_normalized_sha256": a_digest,
        "evidence_status_conversions": conversions,
        "core_requirement_findings": findings,
        "approved_content_transformation": (
            "Lossless OS machine-contract projection; original A0/A v2 Git blobs "
            "and both independent Human approval sources immutable. Any material "
            "change requires renewed Human review."
        ),
        "stage_control_status": "NOT_ASSEMBLED",
        "full_seven_stage_runner_status": "NOT_RUN",
        "formal_stage01_acceptance_status": "NOT_CLAIMED",
        "game_access": "NONE",
    }
    if not conversions:
        raise ValueError("EXPECTED_OLD_STATUS_NORMALIZATION_NOT_FOUND")
    return payload, report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--core-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    payload, report = generate(args.repo_root.resolve(), args.core_root.resolve())
    if report["core_requirement_findings"]:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 33
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "01_requirement_payload_CANDIDATE.yml").write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=True, width=4096), encoding="utf-8"
    )
    (out / "stage01_normalization_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": report["status"], "output": str(out),
                      "a0_digest": report["consensus_A0_normalized_sha256"],
                      "a_digest": report["complete_requirement_payload_normalized_sha256"],
                      "normalized_evidence_rows": len(report["evidence_status_conversions"]),
                      "formal_stage01_pass": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
