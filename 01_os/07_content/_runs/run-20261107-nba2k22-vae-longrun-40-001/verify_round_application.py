"""Bind exact verified S4 treatment receipts to a frozen VAE round without dispatching."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path

from experiment_round import digest

FIELD = "SHOT_TENDENCY"
ACTION = "PLAYER_PATCH_TENDENCIES"


def require(test, reason):
    if not test:
        raise ValueError(reason)


def pinned_json(path, sha256):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == sha256, "Pinned S4 evidence hash differs")
    return json.loads(raw)


def verified_item(seal, result, getter):
    """Consume the owning Host's successful exact singleton run and independent Getter."""
    seal = seal.get("sealed", seal)
    result = result.get("host_result", result)
    context = seal["live_context"]
    native_digest = seal["native_plan_digest"]
    exact = digest({"native_plan_digest": native_digest, "live_context": context})
    require(seal["status"] == "PLAN_PREFLIGHTED_WAITING_AUTH"
            and seal["plan_digest"] == exact == result["plan_digest"]
            and seal["cycle_id"] == result["cycle_id"], "S4 seal and result differ")
    require(seal["executable_intents_count"] == 1 and seal["unsupported_intents_count"] == 0
            and len(seal["items"]) == 1, "Expected exact singleton S4 batch")
    item = seal["items"][0]
    require(item["action_id"] == ACTION and item["field_id"] == FIELD
            and item["team_id"] == context["team_id"] and item["player_id"] in context["player_ids"],
            "Native treatment target outside the sealed team/UID scope")
    require(result["status"] == "EXECUTED_AND_READBACK_RECORDED"
            and result["readback_verified"] is True and result["batch_validation_passed"] is True
            and result["executed_count"] == result["success_count"] == 1
            and result["noop_count"] == result["failure_count"] == 0,
            "S4 execution is not fully verified")
    require(len(result["readback_details"]) == 1, "S4 result must include one independent readback")
    detail = result["readback_details"][0]
    require(detail["intent_id"] == item["intent_id"] and detail["team_id"] == item["team_id"]
            and detail["player_id"] == item["player_id"] and detail["field_id"] == FIELD
            and detail["source"] == "NBA2K22_POST_EXECUTION_MEMORY" and detail["matched"] is True
            and detail["expected_before"] == item["expected_before"]
            and detail["target_value"] == detail["observed_after"] == item["value"],
            "Native treatment target or Getter readback differs")
    stamp = datetime.fromisoformat(detail["read_timestamp"])
    require(stamp.utcoffset() is not None, "Getter timestamp lacks a timezone")
    require(getter["schema_version"] == "nba2k22.rea.independent_readback.v1"
            and getter["timestamp"] == detail["read_timestamp"] and getter["pid"] == context["epoch"]["pid"]
            and getter["intent_count"] == 1 and getter["missed_count"] == 0
            and getter["verified_items"] == [{
                "intent_id": item["intent_id"], "player_id": item["player_id"],
                "readback_getter": item["value"], "target_tendency": item["value"], "confirmed": True,
            }], "Independent Getter file differs from the Host result")
    return {"action": ACTION, "team_id": item["team_id"], "uid": item["player_id"], "field": FIELD,
            "expected_before": item["expected_before"], "target": item["value"], "observed_after": detail["observed_after"],
            "read_timestamp": detail["read_timestamp"], "host_cycle_id": seal["cycle_id"],
            "host_plan_digest": exact, "native_plan_digest": native_digest, "binding_sha256": context["binding_sha256"],
            "epoch": context["epoch"], "today": context["game_progress"]["today_native_iso_date"]}


def bind_round(plan, rows):
    body = {key: value for key, value in plan.items() if key != "research_plan_digest"}
    require(plan["evidence_scope"] == "FRESH_WORLDDATA_CANDIDATE_NOT_AUTHORIZED"
            and plan["factor"] == FIELD and digest(body) == plan["research_plan_digest"],
            "Expected exact current observed round plan")
    expected = {(row["team_id"], row["uid"], row["field"]): row for row in plan["write_candidates"]}
    actual = {(row["team_id"], row["uid"], row["field"]): row for row in rows}
    require(bool(expected) and len(expected) == len(plan["write_candidates"]) and len(actual) == len(rows)
            and set(actual) == set(expected) and len({row["host_cycle_id"] for row in rows}) == len(rows),
            "Missing, extra or duplicate treatment receipt")
    identity = plan["identity"]
    for key, treatment in expected.items():
        observed = actual[key]
        require(observed["action"] == ACTION and observed["today"] == plan["start"]
                and observed["binding_sha256"] == identity["binding_sha256"]
                and observed["epoch"] == identity["epoch"], "S4 receipt is from a different bound scene")
        require(observed["expected_before"] == treatment["expected_before"]
                and observed["target"] == observed["observed_after"] == treatment["target"],
                "Observed dose differs from preregistered treatment")
    return {"status": "EXACT_TREATMENT_READBACK_RECORDED", "research_plan_digest": plan["research_plan_digest"],
            "treatments": [actual[key] for key in sorted(actual)], "analysis_authority": False}


def read_bundle(plan, directory, bundle_sha):
    bundle = pinned_json(directory / "s4-receipts.json", bundle_sha)
    require(bundle["research_plan_digest"] == plan["research_plan_digest"], "Bundle belongs to another round")
    root = directory.resolve()
    records = []
    for row in bundle["batches"]:
        files = {}
        for kind in ("seal", "result", "getter"):
            ref = row[kind]
            path = (root / ref["file"]).resolve()
            require(path.is_relative_to(root), "Receipt must be inside the private bundle")
            files[kind] = pinned_json(path, ref["sha256"])
        records.append(verified_item(**files) | {"source_files_sha256": {key: row[key]["sha256"] for key in files}})
    return bind_round(plan, records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("private_bundle", type=Path)
    parser.add_argument("bundle_sha256", help="Independent exact pin for the private S4 evidence index")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_bytes())
    receipt = read_bundle(plan.get("plan", plan), args.private_bundle, args.bundle_sha256)
    with args.output.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(receipt, file, ensure_ascii=False, indent=2)
    print(json.dumps({"status": receipt["status"], "treatments": len(receipt["treatments"])}))
