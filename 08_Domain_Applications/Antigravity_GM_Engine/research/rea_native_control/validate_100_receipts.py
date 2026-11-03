"""Standalone Receipt and Digest Validator for REA 100-Item Live Benchmark.
Performs read-only validation of manifests, batch plans, claims, receipts, and raw evidence.
"""
from dataclasses import asdict
import glob
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

_RESEARCH_DIR = Path(__file__).resolve().parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

import contracts
from bulk_executor import (
    BulkBatch,
    BulkBatchHeader,
    BulkIntentItem,
    BulkBatchPlanner,
    ItemReceipt,
    canonical_encode,
    sha256_digest
)


def _safe_read_json(path: Path) -> Any:
    text = path.read_text(encoding="utf-8-sig")
    return json.loads(text)


def validate_stage(
    stage_dir: Path | str,
    *,
    expected_count: int = 100,
    expected_mode: str = "mutation"  # "noop" or "mutation"
) -> Dict[str, Any]:
    stage_path = Path(stage_dir).resolve()
    if not stage_path.is_dir():
        return {
            "validation_passed": False,
            "errors": [f"Stage directory does not exist: {stage_path}"],
            "checks": {}
        }

    errors: List[str] = []
    checks: Dict[str, Any] = {}

    # 1. Locate files
    manifest_files = list(stage_path.glob("manifest_*.json"))
    batch_files = list(stage_path.glob("batch_*.json"))
    exec_result_files = list(stage_path.glob("execution_result.json"))

    if not manifest_files:
        errors.append("Missing manifest_*.json in stage directory")
        manifest_data = {}
    else:
        manifest_data = _safe_read_json(manifest_files[0])
        checks["manifest_file"] = str(manifest_files[0].name)

    if not batch_files:
        errors.append("Missing batch_*.json in stage directory")
        batch_data = {}
    else:
        batch_data = _safe_read_json(batch_files[0])
        checks["batch_file"] = str(batch_files[0].name)

    exec_result = {}
    if not exec_result_files:
        errors.append("Missing execution_result.json in stage directory")
    else:
        exec_result = _safe_read_json(exec_result_files[0])
        checks["execution_result_file"] = str(exec_result_files[0].name)

    # 2. Check manifest constraints
    if manifest_data:
        if manifest_data.get("game_build_sha256") != contracts.BUILD:
            errors.append(f"Manifest game_build_sha256 mismatch: {manifest_data.get('game_build_sha256')} != {contracts.BUILD}")
        checks["manifest_game_build_valid"] = (manifest_data.get("game_build_sha256") == contracts.BUILD)

        if "cold_backup_sha256" in manifest_data:
            backup_path = Path(manifest_data.get("cold_backup_path", ""))
            if not backup_path.is_absolute():
                backup_path = (_RESEARCH_DIR / "../../../.." / backup_path).resolve()
            if not backup_path.exists():
                errors.append(f"Cold backup file referenced in manifest not found: {backup_path}")
            checks["cold_backup_exists"] = backup_path.exists()

    # 3. Batch plan validation & digest recomputation
    intents_data = batch_data.get("intents", [])
    checks["planned_intent_count"] = len(intents_data)

    if len(intents_data) != expected_count:
        errors.append(f"Expected {expected_count} intents, got {len(intents_data)}")

    # Check unique intent IDs and resource keys
    intent_ids = set()
    resource_keys = set()
    for item in intents_data:
        iid = item.get("intent_id")
        if iid in intent_ids:
            errors.append(f"Duplicate intent_id in batch: {iid}")
        intent_ids.add(iid)

        rkey = f"team:{item.get('team_id')}:player:{item.get('player_id')}:{item.get('field_id')}"
        if rkey in resource_keys:
            errors.append(f"Duplicate target resource key in batch: {rkey}")
        resource_keys.add(rkey)

    checks["unique_intent_ids_count"] = len(intent_ids)
    checks["unique_resource_keys_count"] = len(resource_keys)

    # Recompute batch plan digest
    try:
        header = BulkBatchHeader(
            batch_id=batch_data["batch_id"],
            save_instance_id=batch_data["save_instance_id"],
            game_build_sha256=batch_data["game_build_sha256"],
            authorization_ref=batch_data["authorization_ref"],
            source_snapshot_ref=batch_data["source_snapshot_ref"],
            expected_process_name=batch_data.get("expected_process_name", "NBA2K22.exe"),
            expected_pid=batch_data.get("expected_pid"),
            dry_run=batch_data.get("dry_run", False)
        )
        intents_tuple = tuple(
            BulkIntentItem(
                intent_id=it["intent_id"],
                action_id=it["action_id"],
                team_id=it["team_id"],
                field_id=it["field_id"],
                expected_before=it["expected_before"],
                value=it["value"],
                player_id=it.get("player_id"),
                source_justification=it.get("source_justification", ""),
                dependencies=tuple(it.get("dependencies", ()))
            )
            for it in intents_data
        )
        recomputed_batch = BulkBatch(header=header, intents=intents_tuple)
        checks["recomputed_plan_digest"] = recomputed_batch.plan_digest

        if manifest_data.get("plan_digest") and manifest_data["plan_digest"] != recomputed_batch.plan_digest:
            errors.append(f"Manifest plan_digest mismatch: {manifest_data['plan_digest']} != {recomputed_batch.plan_digest}")
        checks["plan_digest_verified"] = True
    except Exception as e:
        errors.append(f"Failed to recompute batch plan digest: {e}")
        checks["plan_digest_verified"] = False

    # 4. Journal claims validation
    journal_dir = stage_path / "journal"
    claims_dir = journal_dir / "claims"
    claim_files = list(claims_dir.glob("claim_*.json")) if claims_dir.is_dir() else []
    checks["claim_files_count"] = len(claim_files)

    claimed_chunks = set()
    for cf in claim_files:
        try:
            cdata = _safe_read_json(cf)
            cid = cdata.get("chunk_id")
            if cid:
                claimed_chunks.add(cid)
        except Exception as e:
            errors.append(f"Corrupted claim file {cf.name}: {e}")
    checks["claimed_chunk_ids"] = sorted(list(claimed_chunks))

    # 5. Journal receipts validation
    receipts_file = journal_dir / "receipts.jsonl"
    receipts: List[Dict[str, Any]] = []
    if not receipts_file.is_file():
        errors.append(f"Missing receipts.jsonl at {receipts_file}")
    else:
        for line_num, line in enumerate(receipts_file.read_text(encoding="utf-8-sig").splitlines(), 1):
            if not line.strip():
                continue
            try:
                receipts.append(json.loads(line))
            except Exception as e:
                errors.append(f"Invalid JSON at receipts.jsonl line {line_num}: {e}")

    checks["receipt_count"] = len(receipts)
    if len(receipts) != expected_count:
        errors.append(f"Receipt count mismatch: expected {expected_count}, got {len(receipts)}")

    receipt_intents = set()
    outcomes_breakdown: Dict[str, int] = {}

    for r in receipts:
        iid = r.get("intent_id")
        if iid in receipt_intents:
            errors.append(f"Duplicate receipt for intent_id '{iid}' in receipts.jsonl")
        receipt_intents.add(iid)

        outcome = r.get("outcome", "MISSING_OUTCOME")
        outcomes_breakdown[outcome] = outcomes_breakdown.get(outcome, 0) + 1

        # Check outcome semantics
        if expected_mode == "noop":
            if outcome != "UNCHANGED_ALREADY_TARGET":
                errors.append(f"Expected No-op UNCHANGED_ALREADY_TARGET for intent '{iid}', got outcome '{outcome}'")
            if r.get("actual_before") is not None and r.get("actual_before") != r.get("expected_before"):
                errors.append(f"No-op before mismatch for intent '{iid}': before={r.get('actual_before')} != expected={r.get('expected_before')}")
            if r.get("actual_after") is not None and r.get("actual_after") != r.get("requested"):
                errors.append(f"No-op after mismatch for intent '{iid}': after={r.get('actual_after')} != requested={r.get('requested')}")
        elif expected_mode == "mutation":
            if outcome != "SUCCESS_APPLIED":
                errors.append(f"Expected SUCCESS_APPLIED for intent '{iid}', got outcome '{outcome}'")
            if r.get("actual_before") is not None and r.get("actual_before") != r.get("expected_before"):
                errors.append(f"Mutation before mismatch for intent '{iid}': before={r.get('actual_before')} != expected={r.get('expected_before')}")
            if r.get("actual_after") is not None and r.get("actual_after") != r.get("requested"):
                errors.append(f"Mutation after mismatch for intent '{iid}': after={r.get('actual_after')} != requested={r.get('requested')}")

    checks["outcomes_breakdown"] = outcomes_breakdown
    checks["unknown_count"] = outcomes_breakdown.get("UNKNOWN", 0)
    if checks["unknown_count"] > 0:
        errors.append(f"Critical invariant violated: {checks['unknown_count']} UNKNOWN receipts found!")

    # Check that all batch intents were accounted for
    missing_from_receipts = intent_ids - receipt_intents
    if missing_from_receipts:
        errors.append(f"Intents missing from receipts: {sorted(list(missing_from_receipts))[:5]} (total {len(missing_from_receipts)})")
    checks["missing_intents_count"] = len(missing_from_receipts)

    # 6. Conservation check
    total_outcomes = sum(outcomes_breakdown.values())
    conservation_holds = (total_outcomes == len(intents_data))
    checks["conservation_holds"] = conservation_holds
    if not conservation_holds:
        errors.append(f"Conservation law violated: planned={len(intents_data)} != sum(outcomes)={total_outcomes}")

    # 7. Execution result consistency
    if exec_result:
        checks["frida_attach_count"] = exec_result.get("frida_attach_count")
        if exec_result.get("frida_attach_count") is not None and exec_result.get("frida_attach_count") != 1:
            errors.append(f"Expected exactly 1 Frida attach, got {exec_result.get('frida_attach_count')}")
        checks["execution_time_ms"] = exec_result.get("execution_time_ms")
        checks["chunk_count"] = exec_result.get("chunk_count")

    # 8. Raw REA evidence checks
    rea_dirs = list((stage_path / "rea_runtime").glob("*")) if (stage_path / "rea_runtime").is_dir() else []
    checks["rea_session_dirs_count"] = len(rea_dirs)
    rea_messages_valid = False

    for rd in rea_dirs:
        stderr_file = rd / "rea-stderr.log"
        if stderr_file.is_file() and stderr_file.stat().st_size > 0:
            err_content = stderr_file.read_text(encoding="utf-8-sig", errors="replace").strip()
            if err_content:
                errors.append(f"Non-empty rea-stderr.log in {rd.name}: {err_content[:200]}")

        evidence_file = rd / "evidence.json"
        if evidence_file.is_file():
            try:
                raw_ev = _safe_read_json(evidence_file)
                msgs = []
                if isinstance(raw_ev, list):
                    msgs = raw_ev
                elif isinstance(raw_ev, dict):
                    msgs = raw_ev.get("normalized_result", {}).get("messages", [])

                chunk_msgs = [
                    m for m in msgs
                    if m.get("kind") == "chunk-execution-result"
                    or m.get("payload", {}).get("kind") == "chunk-execution-result"
                ]
                checks["evidence_chunk_messages_count"] = len(chunk_msgs)
                if chunk_msgs:
                    rea_messages_valid = True
            except Exception as e:
                errors.append(f"Failed to parse evidence.json in {rd.name}: {e}")

    checks["rea_evidence_verified"] = rea_messages_valid

    passed = (len(errors) == 0)
    return {
        "schema_version": "nba2k22.rea.receipt_validation.v1",
        "stage_directory": str(stage_path),
        "expected_mode": expected_mode,
        "expected_count": expected_count,
        "validation_passed": passed,
        "errors": errors,
        "checks": checks
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate receipts and digest for REA benchmark stage")
    parser.add_argument("--stage-dir", required=True, help="Path to stage directory")
    parser.add_argument("--expected-count", type=int, default=100, help="Expected number of intents")
    parser.add_argument("--mode", choices=["noop", "mutation"], default="mutation", help="Expected stage mode")
    parser.add_argument("--output", help="Optional output JSON file")
    args = parser.parse_args()

    result = validate_stage(args.stage_dir, expected_count=args.expected_count, expected_mode=args.mode)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    sys.exit(0 if result["validation_passed"] else 1)
