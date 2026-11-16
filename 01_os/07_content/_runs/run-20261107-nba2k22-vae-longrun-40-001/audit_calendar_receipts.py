"""Recheck private historical REA receipts; print only public-safe facts."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path("08_Domain_Applications/Antigravity_GM_Engine/research/native_access/AG_NATIVE_01D/decoders").resolve()))
from boxscore_decoder import BoxScoreDecoder


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def load(path):
    raw = path.read_bytes()
    evidence = json.loads(raw)
    result = evidence["normalized_result"]
    require(not result["messages_truncated"] and result["cleanup_error"] is None, "Incomplete REA receipt")
    return evidence["evidence_id"], hashlib.sha256(raw).hexdigest(), result


def window(root, dispatched, observed, expected, next_games, today, word, source_file=None):
    evidence, sha, dispatch = load(root / dispatched)
    readback, readback_sha, observed_result = load(root / observed)
    messages = [entry["payload"] for entry in dispatch["messages"]]
    by_event = Counter(msg["event"] for msg in messages)
    require(by_event["WILL_DISPATCH_ONCE"] == by_event["DISPATCH_RETURN"] == 1, "Unexpected dispatch count")
    request = next(msg for msg in messages if msg["event"] == "WILL_DISPATCH_ONCE")
    returned = next(msg for msg in messages if msg["event"] == "DISPATCH_RETURN")
    require(request["command"] == 17 and returned["status"] == 0x504521a8
            and returned["today"] == word and returned["frameStillIdle"], "Native dispatch invariant failed")
    require(dispatch["pid"] == observed_result["pid"] and by_event["STOP"] == 0, "Process or stop mismatch")
    units = [msg for msg in messages if msg["event"] == "REA_POST_SIM_BOX_UNIT"]
    require(len(units) == 1 and units[0]["pid"] == dispatch["pid"], "Box unit process binding failed")
    box_label = units[0]["today_raw"]
    box_label_status = "MATCHES_NATIVE_TODAY"
    if int(box_label, 16) != word:
        require(source_file is not None, "Unexpected Box date metadata mismatch")
        source_bytes = (root / source_file).read_bytes()
        require(hashlib.sha256(source_bytes).hexdigest() == dispatch["source_sha256"],
                "Exact dispatched source hash mismatch")
        source = source_bytes.decode("utf-8")
        require(source.count("mode.add(20).readU32()!==NEXT") == 2
                and f"const NEXT = {word:#x};" in source
                and f"today_raw:'{box_label}'" in source, "Box native date or emission proof absent")
        box_label_status = "STALE_HARDCODED_LABEL_PROVEN_BY_SOURCE_HASH_AND_NATIVE_DATE_GUARDS"
    seen = []
    for row in units[0]["games"]:
        header = bytes.fromhex(row["header_hex"])
        box = bytes.fromhex(row["box_hex"])
        decoded = BoxScoreDecoder.decode_full_boxscore(header, box)
        score = decoded["conservation"]
        require(row["id"] == int.from_bytes(header[8:12], "little")
                and score["home_score_exact"] and score["away_score_exact"], "Box score or identity mismatch")
        seen.append(row["id"])
    require(sorted(seen) == list(expected), "Exact Box IDs differ")
    snapshot = next(row["payload"] for row in observed_result["messages"] if row["payload"]["event"] == "REA_CALENDAR_WINDOW")
    require(snapshot["today"] == today and int(snapshot["today_raw"], 16) == word, "Today mismatch")
    rows = {row["id"]: row for row in snapshot["games"]}
    require(len(rows) == len(snapshot["games"]), "Duplicate readback Game ID")
    require(all(rows[gid]["status"] == 2 and rows[gid]["was_simulated"]
                and rows[gid]["played"] == rows[gid]["d"] for gid in expected), "Exact finals or played dates differ")
    require(all(rows[gid]["status"] == 0 and not rows[gid]["was_simulated"]
                and rows[gid]["played"] is None for gid in next_games), "Next day accidentally played")
    return {"dispatch_evidence": evidence, "dispatch_sha256": sha,
            "readback_evidence": readback, "readback_sha256": readback_sha,
            "source_script_sha256": dispatch["source_sha256"], "today": today,
            "command": request["command"], "native_thread": request["thread"],
            "selected_date_word": request["selected"], "exact_finals_and_score_conserved": seen,
            "next_day_pending": list(next_games), "observed_exceptions": by_event["NATIVE_EXCEPTION_OBSERVED"],
            "emitted_box_today_label": box_label, "box_today_label_status": box_label_status}


def audit(root):
    crash = json.loads((root / "rea-dec30-native-dispatch-crash-receipt.json").read_bytes())
    summary = json.loads((root / "rea-native-calendar-live-test-summary.json").read_bytes())
    require(crash["oldPid"] != crash["newPid"] and summary["process"]["activeFrameAtDispatch"] is False,
            "Crash/restart context missing")
    return {
        "status": "EXECUTION_WINDOW_RAW_RECEIPTS_RECHECKED_WITH_GAPS",
        "independent_review": "PENDING",
        "human_ui_acceptance": "https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/39#issuecomment-6705566190",
        "two_windows": [
            window(root, "rea-dec30-restart-dispatch-receipt.json", "rea-dec30-restart-post-window.json",
                   range(516, 529), range(529, 539), "2021-12-31", 0x2b7f0000),
            window(root, "rea-seven-day-native-dispatch-receipt.json", "rea-seven-day-post-window.json",
                   range(529, 582), range(582, 591), "2022-01-07", 0x2c070000,
                   "rea-seven-day-dispatched-exact.js"),
        ],
        "historic_execution": summary["process"],
        "crash": "prior frame-active dispatch advanced date, then exited; exact fault unverified",
        "exception": "second successful window had RaiseException; code and cause unverified",
        "focus": "foreground observed on successful trials; other states unqualified",
        "persistence": "disk digest matched cold copy at receipt; Save/reload not demonstrated",
        "archived_sim_entry_on_master": False,
        "live_eligibility_for_issue_40": "BLOCKED_ISSUE_39_TECHNICAL_GATES_AND_EXACT_GRANTS",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("private_receipt_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.private_receipt_dir), indent=2))
