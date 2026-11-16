"""Build a VAE season stop receipt and check a later Human handoff, offline only."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path

from experiment_round import digest

BINDING = ("save", "worldline", "season", "loaded_filename", "binding_sha256", "database_identity",
           "disk_sha256", "source_report_sha256", "epoch")
DANGER = {"CRASH", "RAISE_EXCEPTION", "UNKNOWN_DISPATCH", "CAS_CONFLICT", "PARTIAL_CAPTURE",
          "FOCUS_LOST", "EPOCH_DRIFT", "BINDING_DRIFT", "EXPIRED_AUTHORITY", "EVENT_BOUNDARY",
          "QUALIFICATION_DRIFT"}
HANDOFF_ACTIONS = {"CONTINUE_NEXT_REGULAR_SEASON", "RESTORE_FROZEN_BASELINE"}


def require(test, reason):
    if not test:
        raise ValueError(reason)


def exact_date(value):
    parsed = date.fromisoformat(value)
    require(parsed.isoformat() == value, "ISO civil date required")
    return parsed


def is_sha256(value):
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def check_scene(scene):
    require(all(scene.get(key) for key in BINDING), "Incomplete WorldData and process binding")
    for key in ("binding_sha256", "disk_sha256", "source_report_sha256"):
        require(is_sha256(scene[key]), f"Invalid {key}")
    require(type(scene["season"]) is int and scene["season"] > 0, "Verified native season year required")
    return exact_date(scene["today"])


def make_checkpoint(scene, *, last_regular_day, stop_reason, research_intent, frozen_backup_sha256, windows):
    today = check_scene(scene)
    last = exact_date(last_regular_day)
    require(research_intent in {"FOLLOW_DEVELOPMENT", "REPLICATE_FROM_BASELINE"}, "Unknown research intent")
    require(is_sha256(frozen_backup_sha256), "Exact frozen backup SHA256 required")
    require(stop_reason in DANGER or (stop_reason == "REGULAR_SEASON_BOUNDARY" and today > last),
            "No observed hard stop or regular-season boundary")
    seen_games, seen_windows = set(), set()
    verified, unresolved = [], []
    for window in windows:
        plan_digest = window["plan_digest"]
        require(is_sha256(plan_digest) and plan_digest not in seen_windows, "Invalid or duplicate round plan")
        require((window["save"], window["worldline"], window["season"]) ==
                (scene["save"], scene["worldline"], scene["season"]), "Round belongs to a different season binding")
        seen_windows.add(plan_digest)
        ids = window["verified_game_ids"]
        require(len(ids) == len(set(ids)) and not seen_games.intersection(ids),
                "Duplicate verified Game IDs")
        seen_games.update(ids)
        require(window["status"] in {"SCREENING_RECORDED", "STOPPED_PARTIAL_READBACK", "UNKNOWN_NO_REPLAY"}
                and is_sha256(window.get("receipt_sha256")), "Incomplete window evidence summary")
        if window["status"] == "SCREENING_RECORDED":
            verified.append(window)
        else:
            unresolved.append(window)
    clean_boundary = stop_reason == "REGULAR_SEASON_BOUNDARY" and not unresolved
    recommendation = ("CONTINUE_NEXT_REGULAR_SEASON" if clean_boundary and research_intent == "FOLLOW_DEVELOPMENT"
                      else "RESTORE_FROZEN_BASELINE")
    checkpoint = {
        "schema": "nba2k22.vae.season_checkpoint.v1",
        "status": "AWAITING_HUMAN_HANDOFF" if clean_boundary else "STOPPED_RECONCILIATION_REQUIRED",
        "stop_reason": stop_reason, "scene": scene, "last_regular_day": last_regular_day,
        "recommended_human_action": recommendation,
        "recommendation_basis": "VERIFIED_SEASON_BOUNDARY" if clean_boundary else "ONLY_IF_RECONCILIATION_REQUIRES_RESET",
        "reconciliation_required_before_action": not clean_boundary,
        "frozen_backup_sha256": frozen_backup_sha256, "windows": windows,
        "screened_windows": len(verified), "unresolved_windows": len(unresolved),
        "verified_game_ids": sorted(seen_games),
        "original_authority_reusable": False,
    }
    return {**checkpoint, "checkpoint_digest": digest(checkpoint)}


def verify_rebind(checkpoint, decision, fresh):
    body = {key: value for key, value in checkpoint.items() if key != "checkpoint_digest"}
    require(digest(body) == checkpoint["checkpoint_digest"]
            and decision["checkpoint_digest"] == checkpoint["checkpoint_digest"]
            and decision.get("human_ref") and decision["action"] in HANDOFF_ACTIONS,
            "Expected Human decision for exact checkpoint and supported action")
    require(not checkpoint["reconciliation_required_before_action"] or decision.get("reconciliation_ref"),
            "Read-only reconciliation must precede this handoff")
    today = check_scene(fresh)
    prior = checkpoint["scene"]
    require(fresh["source_report_sha256"] != prior["source_report_sha256"]
            and fresh["loaded_filename"] == decision["confirmed_loaded_filename"]
            and fresh["mode_raw"] == 1 and fresh["period_raw"] == 29 and fresh["league_raw"] == 0,
            "Expected fresh Human-confirmed regular-season NBA save binding")
    if decision["action"] == "CONTINUE_NEXT_REGULAR_SEASON":
        require(fresh["save"] == prior["save"] and fresh["worldline"] == prior["worldline"]
                and fresh["season"] == prior["season"] + 1 and today > exact_date(prior["today"]),
                "Next-season capture does not continue the bound worldline")
    else:
        require(fresh["disk_sha256"] == checkpoint["frozen_backup_sha256"]
                and fresh["worldline"] != prior["worldline"] and fresh["database_identity"] != prior["database_identity"]
                and fresh["season"] == decision["expected_restored_season"]
                and fresh["today"] == decision["expected_restored_today"],
                "Restored baseline does not match backup, date and isolated worldline")
    return {"status": "REBIND_VERIFIED_AUTHORITY_REQUIRES_FRESH_REVIEW",
            "checkpoint_digest": checkpoint["checkpoint_digest"], "human_ref": decision["human_ref"],
            "fresh_scene": fresh, "live_write_authorized": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("checkpoint", "verify-rebind"))
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--input-sha256", required=True)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == args.input_sha256, "Checkpoint input pin differs")
    payload = json.loads(raw)
    result = make_checkpoint(**payload) if args.command == "checkpoint" else verify_rebind(**payload)
    with args.output.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
    print(json.dumps({"status": result["status"]}))
