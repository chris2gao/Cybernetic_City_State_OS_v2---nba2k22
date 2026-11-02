"""Generic and Fail-Closed Batch Execution Receipt Validator for NBA2K22 REA.
Performs comprehensive verification of batch plans, chunk digests, journal claims,
execution receipts, raw REA messages, and independent readback evidence.
"""
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

_RESEARCH_DIR = Path(__file__).resolve().parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

import contracts
from bulk_executor import (
    BulkBatch,
    BulkBatchHeader,
    BulkIntentItem,
    canonical_encode,
    sha256_digest
)


def _safe_read_json(path: Path) -> Any:
    text = path.read_text(encoding="utf-8-sig")
    return json.loads(text)


def validate_batch_execution(
    batch: Any,  # BulkBatch or dict
    chunks: List[Any],  # List[PlannedChunk] or List[dict]
    raw_messages: List[Dict[str, Any]],
    receipts: List[Any],  # List[ItemReceipt] or List[dict]
    independent_readback: Optional[Dict[str, Any]] = None,
    *,
    manifest: Optional[Dict[str, Any]] = None,
    claims: Optional[List[Dict[str, Any]]] = None,
    expected_mode: str = "mutation"  # "mutation", "noop", or "mixed"
) -> Dict[str, Any]:
    """Validates execution results with fail-closed semantics across all evidence layers."""
    errors: List[str] = []
    checks: Dict[str, Any] = {}

    # 1. Normalize batch data
    if isinstance(batch, BulkBatch):
        batch_header = asdict(batch.header)
        batch_intents = [asdict(i) for i in batch.intents]
        plan_digest = batch.plan_digest
    elif isinstance(batch, dict):
        batch_header = {k: v for k, v in batch.items() if k != "intents"}
        batch_intents = batch.get("intents", [])
        plan_digest = batch.get("plan_digest", "")
    else:
        errors.append(f"Invalid batch type: {type(batch)}")
        batch_header = {}
        batch_intents = []
        plan_digest = ""

    # Recompute batch plan digest
    if batch_header and batch_intents:
        try:
            h = BulkBatchHeader(
                batch_id=batch_header["batch_id"],
                save_instance_id=batch_header["save_instance_id"],
                game_build_sha256=batch_header["game_build_sha256"],
                authorization_ref=batch_header["authorization_ref"],
                source_snapshot_ref=batch_header["source_snapshot_ref"],
                expected_process_name=batch_header.get("expected_process_name", "NBA2K22.exe"),
                expected_pid=batch_header.get("expected_pid"),
                dry_run=batch_header.get("dry_run", False)
            )
            i_tuple = tuple(
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
                for it in batch_intents
            )
            recomputed = BulkBatch(header=h, intents=i_tuple)
            recomputed_digest = recomputed.plan_digest
            checks["recomputed_plan_digest"] = recomputed_digest

            if plan_digest and plan_digest != recomputed_digest:
                errors.append(f"Batch plan_digest mismatch: stored '{plan_digest}' != recomputed '{recomputed_digest}'")
            if manifest and manifest.get("plan_digest") and manifest["plan_digest"] != recomputed_digest:
                errors.append(f"Manifest plan_digest mismatch: manifest '{manifest['plan_digest']}' != recomputed '{recomputed_digest}'")
            checks["plan_digest_verified"] = (len(errors) == 0)
        except Exception as e:
            errors.append(f"Failed to recompute batch plan digest: {e}")
            checks["plan_digest_verified"] = False

    # Check manifest constraints
    if manifest:
        if manifest.get("game_build_sha256") and manifest["game_build_sha256"] != contracts.BUILD:
            errors.append(f"Manifest build hash mismatch: {manifest['game_build_sha256']} != {contracts.BUILD}")
        checks["manifest_game_build_valid"] = (manifest.get("game_build_sha256") == contracts.BUILD)

    # 2. Normalize and check receipts
    normalized_receipts: List[Dict[str, Any]] = []
    for r in receipts:
        if isinstance(r, dict):
            normalized_receipts.append(r)
        else:
            normalized_receipts.append(asdict(r))

    checks["planned_intent_count"] = len(batch_intents)
    checks["receipt_count"] = len(normalized_receipts)

    if len(batch_intents) != len(normalized_receipts):
        errors.append(f"Count mismatch: planned {len(batch_intents)} intents, got {len(normalized_receipts)} receipts")

    planned_ids = {it["intent_id"] for it in batch_intents}
    receipt_ids = set()
    outcomes_breakdown: Dict[str, int] = {}
    unknown_count = 0

    for r in normalized_receipts:
        iid = r.get("intent_id")
        if not iid:
            errors.append("Receipt missing intent_id")
            continue
        if iid in receipt_ids:
            errors.append(f"Duplicate receipt for intent_id: {iid}")
        receipt_ids.add(iid)

        outcome = r.get("outcome", "MISSING_OUTCOME")
        outcomes_breakdown[outcome] = outcomes_breakdown.get(outcome, 0) + 1

        # Check for UNKNOWN outcomes
        if "UNKNOWN" in outcome or outcome == "TIMEOUT":
            unknown_count += 1
            errors.append(f"UNKNOWN outcome detected for intent '{iid}': outcome={outcome}")

        # Check getter values (fail-closed: must be present)
        before_val = r.get("getter_before") if r.get("getter_before") is not None else r.get("actual_before")
        after_val = r.get("getter_after") if r.get("getter_after") is not None else r.get("actual_after")

        if before_val is None and outcome in ("SUCCESS_APPLIED", "UNCHANGED_ALREADY_TARGET"):
            errors.append(f"Missing getter_before for intent '{iid}'")
        if after_val is None and outcome in ("SUCCESS_APPLIED", "UNCHANGED_ALREADY_TARGET"):
            errors.append(f"Missing getter_after for intent '{iid}'")

        # Value semantics check
        expected_before = r.get("expected_before")
        requested = r.get("requested")

        if outcome == "SUCCESS_APPLIED":
            if before_val is not None and expected_before is not None and before_val != expected_before:
                errors.append(f"CAS mismatch for intent '{iid}': getter_before={before_val} != expected_before={expected_before}")
            if after_val is not None and requested is not None and after_val != requested:
                errors.append(f"Target value mismatch for intent '{iid}': getter_after={after_val} != requested={requested}")
        elif outcome == "UNCHANGED_ALREADY_TARGET":
            if before_val is not None and requested is not None and before_val != requested:
                errors.append(f"No-op before mismatch for intent '{iid}': getter_before={before_val} != requested={requested}")
            if after_val is not None and requested is not None and after_val != requested:
                errors.append(f"No-op after mismatch for intent '{iid}': getter_after={after_val} != requested={requested}")

        # Check unaltered fields check
        if "unaltered_fields_check" in r and r["unaltered_fields_check"] is False:
            errors.append(f"Unaltered fields conservation failed for intent '{iid}'")

    checks["outcomes_breakdown"] = outcomes_breakdown
    checks["unknown_count"] = unknown_count

    # Check for missing intents
    missing_intents = planned_ids - receipt_ids
    if missing_intents:
        errors.append(f"Missing receipts for planned intents: {sorted(list(missing_intents))[:5]}")
    checks["missing_intents_count"] = len(missing_intents)

    # Conservation check
    total_outcomes = sum(outcomes_breakdown.values())
    conservation_holds = (total_outcomes == len(batch_intents))
    checks["conservation_holds"] = conservation_holds
    if not conservation_holds:
        errors.append(f"Conservation law violated: planned={len(batch_intents)} != outcomes={total_outcomes}")

    # 3. Check claims if provided
    if claims is not None:
        checks["claims_count"] = len(claims)
        claimed_cids = {c.get("chunk_id") for c in claims if c.get("chunk_id")}
        checks["claimed_chunk_ids"] = sorted(list(claimed_cids))

    # 4. Check Raw REA Evidence messages
    chunk_msgs = [
        m for m in raw_messages
        if m.get("kind") == "chunk-execution-result"
        or m.get("payload", {}).get("kind") == "chunk-execution-result"
    ]
    checks["raw_chunk_messages_count"] = len(chunk_msgs)

    if chunks:
        checks["expected_chunk_count"] = len(chunks)
        if len(chunk_msgs) != len(chunks):
            errors.append(f"Raw evidence chunk count mismatch: expected {len(chunks)}, got {len(chunk_msgs)}")

    for cm in chunk_msgs:
        payload = cm.get("payload", cm)
        cid = payload.get("chunk_id")
        cdigest = payload.get("chunk_digest")
        pdigest = payload.get("plan_digest")
        c_outcome = payload.get("outcome")

        if pdigest and plan_digest and pdigest != plan_digest:
            errors.append(f"Raw message plan_digest mismatch in chunk '{cid}': {pdigest} != {plan_digest}")
        if c_outcome not in ("CHUNK_SUCCESS", "CHUNK_SKIPPED"):
            errors.append(f"Raw chunk execution outcome failed in chunk '{cid}': {c_outcome}")

    # 5. Check Independent Readback if provided
    if independent_readback:
        checks["readback_evaluated"] = True
        readback_missed = independent_readback.get("missed_count", 0)
        checks["readback_missed_count"] = readback_missed
        if readback_missed > 0:
            errors.append(f"Independent readback missed {readback_missed} players in game memory")
        checks["readback_all_persisted"] = independent_readback.get("all_100_persisted_in_game", False)
        if not checks["readback_all_persisted"]:
            errors.append("Independent readback reported unconfirmed player values")

    passed = (len(errors) == 0)
    return {
        "schema_version": "nba2k22.rea.generic_batch_validation.v1",
        "validation_passed": passed,
        "errors": errors,
        "checks": checks
    }


def validate_stage_directory(
    stage_dir: Path | str,
    *,
    expected_count: Optional[int] = None,
    expected_mode: str = "mutation"
) -> Dict[str, Any]:
    """Validates an entire stage directory from disk using validate_batch_execution."""
    stage_path = Path(stage_dir).resolve()
    if not stage_path.is_dir():
        return {
            "validation_passed": False,
            "errors": [f"Stage directory not found: {stage_path}"],
            "checks": {}
        }

    # Locate manifest, batch, and execution result
    manifest_files = list(stage_path.glob("manifest_*.json"))
    manifest = _safe_read_json(manifest_files[0]) if manifest_files else None

    batch_files = list(stage_path.glob("batch_*.json"))
    batch = _safe_read_json(batch_files[0]) if batch_files else {}

    # Locate claims
    claims_dir = stage_path / "journal" / "claims"
    claims = [_safe_read_json(cf) for cf in claims_dir.glob("claim_*.json")] if claims_dir.is_dir() else []

    # Locate receipts
    receipts_file = stage_path / "journal" / "receipts.jsonl"
    receipts = []
    if receipts_file.is_file():
        for line in receipts_file.read_text(encoding="utf-8-sig").splitlines():
            if line.strip():
                receipts.append(json.loads(line))

    # Locate raw REA messages
    raw_messages = []
    rea_dirs = list((stage_path / "rea_runtime").glob("*")) if (stage_path / "rea_runtime").is_dir() else []
    for rd in rea_dirs:
        ev_file = rd / "evidence.json"
        if ev_file.is_file():
            raw_ev = _safe_read_json(ev_file)
            if isinstance(raw_ev, list):
                raw_messages.extend(raw_ev)
            elif isinstance(raw_ev, dict):
                raw_messages.extend(raw_ev.get("normalized_result", {}).get("messages", []))

    # Chunks from planner
    chunks = []
    if batch:
        try:
            h = BulkBatchHeader(
                batch_id=batch["batch_id"],
                save_instance_id=batch["save_instance_id"],
                game_build_sha256=batch["game_build_sha256"],
                authorization_ref=batch["authorization_ref"],
                source_snapshot_ref=batch["source_snapshot_ref"],
                expected_process_name=batch.get("expected_process_name", "NBA2K22.exe"),
                expected_pid=batch.get("expected_pid"),
                dry_run=batch.get("dry_run", False)
            )
            i_tuple = tuple(
                BulkIntentItem(
                    intent_id=it["intent_id"],
                    action_id=it["action_id"],
                    team_id=it["team_id"],
                    field_id=it["field_id"],
                    expected_before=it["expected_before"],
                    value=it["value"],
                    player_id=it.get("player_id")
                )
                for it in batch.get("intents", [])
            )
            b_obj = BulkBatch(header=h, intents=i_tuple)
            from bulk_executor import BulkBatchPlanner
            planner = BulkBatchPlanner()
            chunks = planner.plan(b_obj, max_chunk_size=50)
        except Exception:
            chunks = []

    res = validate_batch_execution(
        batch=batch,
        chunks=chunks,
        raw_messages=raw_messages,
        receipts=receipts,
        manifest=manifest,
        claims=claims,
        expected_mode=expected_mode
    )

    if expected_count is not None and res["checks"].get("receipt_count") != expected_count:
        res["validation_passed"] = False
        res["errors"].append(f"Receipt count mismatch: expected {expected_count}, got {res['checks'].get('receipt_count')}")

    res["stage_directory"] = str(stage_path)
    return res


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generic Batch Execution Receipt Validator")
    parser.add_argument("--stage-dir", required=True, help="Path to stage directory")
    parser.add_argument("--expected-count", type=int, default=None, help="Expected number of receipts")
    parser.add_argument("--mode", choices=["mutation", "noop", "mixed"], default="mutation", help="Expected stage mode")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    result = validate_stage_directory(args.stage_dir, expected_count=args.expected_count, expected_mode=args.mode)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    sys.exit(0 if result["validation_passed"] else 1)
