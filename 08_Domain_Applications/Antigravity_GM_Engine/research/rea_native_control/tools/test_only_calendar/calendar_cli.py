"""Explicit, test-only NBA2K22 calendar entry points; never registered as game actions."""
import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

HERE = Path(__file__).resolve().parent
REA_ROOT = HERE.parents[1]
DOMAIN = HERE.parents[3]
WORLD = DOMAIN / "world_data_prototype"
DECODERS = DOMAIN / "research/native_access/AG_NATIVE_01D/decoders"
sys.path[:0] = [str(WORLD), str(REA_ROOT), str(DECODERS)]

from boxscore_decoder import BoxScoreDecoder
from contracts import BUILD
from decision_outbox import DecisionOutbox
from transport import LiveExecutionContext, ReaCliTransport

SCHEMA = "nba2k22.test_only_calendar.plan.v1"
ACTION = "TEST_ONLY_SIM_THROUGH_DATE"
EPOCH_KEYS = ("pid", "creation_filetime", "module_base", "module_size", "pe_timestamp", "game_season_year")


def require(test, reason):
    if not test:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def sha_file(path):
    with Path(path).open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def digest(value):
    return sha_bytes(canonical(value))


def load(path):
    return json.loads(Path(path).read_bytes())


def utc(value):
    stamp = datetime.fromisoformat(value)
    require(stamp.utcoffset() is not None, "Timezone-aware validity window required")
    return stamp


def civil(value):
    result = date.fromisoformat(value)
    require(result.isoformat() == value, "Use ISO calendar date")
    return result


def word(day):
    require(2000 <= day.year < 2064, "Unsupported packed game date")
    return ((day.year - 2000) << 25) | ((day.month - 1) << 21) | (day.day << 16)


def validate_plan(plan, *, observe=False):
    require(plan["schema"] == SCHEMA and plan["build_sha256"] == BUILD and plan["test_only"] is True
            and plan["disposable_save"] is True and plan["event_free_regular_season"] is True,
            "Pinned test-only regular-season plan required")
    require(plan["source_sha256"] == load(HERE / "capability_manifest.json")["source_sha256"],
            "Plan is bound to different calendar source")
    start, end, season_stop = (civil(plan[name]) for name in ("start", "stop_exclusive", "season_stop_exclusive"))
    require(1 <= (end - start).days <= 2 and end < season_stop, "Short regular-season window required")
    raw = plan["today_raw"]
    require(type(raw) is int and 0 <= raw <= 0xffffffff
            and raw & 0xffff0000 == word(start) and ((raw >> 5) & 2047) == 0, "Frozen midnight Today differs")
    for key in ("save_id", "worldline_id", "authorization_scope"):
        require(isinstance(plan[key], str) and 0 < len(plan[key]) <= 128, f"Missing {key}")
    require(re.fullmatch(r"MyLEAGUE\d{4}", plan["loaded_filename"]) is not None,
            "Exact MyLEAGUE slot required")
    for key in ("binding_sha256", "disk_sha256", "cold_backup_sha256"):
        require(re.fullmatch(r"[a-f0-9]{64}", plan[key]) is not None, f"Invalid {key}")
    epoch = plan["epoch"]
    require(set(epoch) == set(EPOCH_KEYS) and all(type(epoch[key]) is int and epoch[key] > 0
            for key in ("pid", "creation_filetime", "module_size", "game_season_year"))
            and epoch["pe_timestamp"] == 1652287197
            and re.fullmatch(r"0x[0-9a-fA-F]+", epoch["module_base"]) is not None,
            "Exact executable process epoch required")
    require(type(plan["engine_thread"]) is int and (plan["engine_thread"] > 0
            or (observe and plan["engine_thread"] == 0)), "Engine thread evidence required")
    require(observe or isinstance(plan["engine_thread_evidence"], str) and plan["engine_thread_evidence"],
            "Read-only frame observation reference required")
    require(type(plan["observation_ms"]) is int and 15000 <= plan["observation_ms"] <= 120000,
            "Observation window outside 15–120 seconds")
    games = plan["games"]
    ids = [game["id"] for game in games]
    require(2 <= len(games) <= 45 and ids == sorted(set(ids)), "Canonical exact Game ID set required")
    days = []
    for game in games:
        day = civil(game["day"])
        require(type(game["id"]) is int and 0 < game["id"] <= 65535 and start <= day <= end
                and all(type(game[key]) is int and 0 <= game[key] <= 65535 for key in ("home", "away"))
                and game["home"] != game["away"], "Invalid scheduled matchup")
        days.append(day)
    require(any(day < end for day in days) and end in days, "Expected finals and next-day controls required")


def load_approval(plan, path, approved_sha, now):
    raw = Path(path).read_bytes()
    require(sha_bytes(raw) == approved_sha, "Operator-pinned approval SHA256 differs")
    grant = json.loads(raw)
    require(grant["action"] == ACTION and grant["plan_digest"] == digest(plan)
            and grant["authorization_scope"] == plan["authorization_scope"]
            and type(grant["max_dispatches"]) is int and grant["max_dispatches"] == 1
            and grant["approved_by_operator"] is True and isinstance(grant["human_decision_ref"], str)
            and grant["human_decision_ref"].strip() and grant.get("revoked") is False,
            "Exact operator-approved one-dispatch scope required")
    valid_from, valid_until = utc(grant["valid_from"]), utc(grant["expires_at"])
    require(valid_from <= now < valid_until and valid_until - valid_from <= timedelta(hours=24),
            "Approval expired or outside test horizon")
    return grant


def ensure_scene(plan, scene, *, after=False):
    require({key: scene["epoch"][key] for key in EPOCH_KEYS} == plan["epoch"],
            "Process epoch changed")
    facts = scene["game_progress"]
    require(facts["mode_raw"] == 1 and facts["period_raw"] == 29
            and facts["today_native_iso_date"] == plan["stop_exclusive" if after else "start"]
            and facts["today_minutes_since_midnight_raw"] == 0,
            "WorldData progress no longer matches the plan")


def binding_snapshot(directory, filename):
    from live_world import read_binding, bound_database
    binding, sha = read_binding(directory, filename)
    require(bool(binding.get("worldline_id")), "Isolated WorldData worldline binding required")
    return {
        "save_id": binding["save_id"], "worldline_id": binding["worldline_id"],
        "binding_sha256": sha, "database": str(bound_database(directory, binding)),
        "loaded_filename": filename, "native_path": Path(binding["native_save_file"]).resolve(),
        "basis": "OPERATOR_DECLARED_LOADED_FILENAME_PLUS_WORLDDATA_BINDING",
    }


def preflight(plan, *, after=False):
    from refresh import _context
    binding = binding_snapshot(plan["save_directory"], plan["loaded_filename"])
    require(all(binding[key] == plan[key] for key in
                ("save_id", "worldline_id", "binding_sha256", "loaded_filename", "database")),
            "Save or WorldData binding changed")
    disk, backup = binding["native_path"], Path(plan["cold_backup"]).resolve(strict=True)
    require(not disk.samefile(backup) and sha_file(disk) == plan["disk_sha256"]
            and sha_file(backup) == plan["cold_backup_sha256"], "Disk save or cold backup differs")
    ensure_scene(plan, _context(plan["epoch"]["pid"]), after=after)
    return binding


def source(name):
    path = HERE / name
    manifest = load(HERE / "capability_manifest.json")
    raw = path.read_bytes()
    require(sha_bytes(raw) == manifest["source_sha256"][name], "Archived source hash mismatch")
    return raw.decode("utf-8")


def render(plan, *, dispatch, expires):
    validate_plan(plan, observe=not dispatch)
    data = dict(plan["epoch"], creation_filetime=str(plan["epoch"]["creation_filetime"]),
                plan_digest=digest(plan), thread=plan["engine_thread"], today=plan["today_raw"],
                selected=word(civil(plan["stop_exclusive"]) - timedelta(days=1)),
                stop=word(civil(plan["stop_exclusive"])), dispatch=dispatch,
                expires_ms=int(expires.timestamp() * 1000),
                games=[dict(game, day=word(civil(game["day"]))) for game in plan["games"]])
    return "'use strict';\nconst calendarPlan = " + canonical(data).decode() + ";\n" + source("native_today.js") + source("simulate_to_native_date.js")


def audit_native_result(raw, plan):
    result = raw["normalized_result"]
    require(result["pid"] == plan["epoch"]["pid"] and not result["messages_truncated"]
            and result["cleanup_error"] is None
            and all(message["type"] == "send" for message in result["messages"]),
            "REA receipt incomplete, target changed or cleanup failed")
    events = [message["payload"] for message in result["messages"]]
    by_event = lambda name: [event for event in events if event.get("event") == name]
    require(not by_event("NATIVE_EXCEPTION_OBSERVED") and not by_event("STOP"),
            "Exception or stop observed; retain lock for reconciliation")
    sent, returned = by_event("WILL_DISPATCH_ONCE"), by_event("DISPATCH_RETURN")
    next_word = word(civil(plan["stop_exclusive"]))
    require(sent == [{"event": "WILL_DISPATCH_ONCE", "command": 17, "thread": plan["engine_thread"],
                      "selected": word(civil(plan["stop_exclusive"]) - timedelta(days=1))}]
            and len(returned) == 1 and returned[0]["today"] == next_word
            and returned[0]["status"] == 0x504521a8 and returned[0]["frame_idle"] is True,
            "Native dispatch count, thread, date or return differs")
    finals = {row["id"]: row for row in plan["games"] if row["day"] != plan["stop_exclusive"]}
    pending = sorted(row["id"] for row in plan["games"] if row["day"] == plan["stop_exclusive"])
    observed = by_event("NEXT_DAY_PENDING")
    require(len(observed) == 1 and sorted(observed[0]["ids"]) == pending, "Next-day pending set differs")
    boxes = by_event("REA_POST_SIM_BOX_UNIT")
    require(bool(boxes) and all(unit["part"] == index and unit["total"] == len(boxes)
            and unit["pid"] == result["pid"] and unit["today_raw"] == next_word
            for index, unit in enumerate(boxes)), "Missing or mismatched Box capture unit")
    seen = set()
    for row in (row for unit in boxes for row in unit["games"]):
        game_id = row["id"]
        require(game_id in finals and game_id not in seen, "Box Game ID differs")
        header, box = bytes.fromhex(row["header_hex"]), bytes.fromhex(row["box_hex"])
        planned = finals[game_id]
        require(len(header) == 60 and int.from_bytes(header[8:12], "little") == game_id
                and int.from_bytes(header[:4], "little") & 0xffff0000 == word(civil(planned["day"]))
                and int.from_bytes(header[4:8], "little") & 0xffff0000 == word(civil(planned["day"]))
                and int.from_bytes(header[12:14], "little") == planned["home"]
                and int.from_bytes(header[14:16], "little") == planned["away"],
                "Box header identity differs")
        flags = int.from_bytes(header[56:60], "little")
        require((flags >> 11) & 3 == 2 and flags & 0x40000
                and 1 <= header[22] <= 26 and 1 <= header[23] <= 26
                and len(box) == (header[22] + header[23]) * 24, "Final flags or Box dimensions differ")
        stats = BoxScoreDecoder.decode_full_boxscore(header, box)["conservation"]
        require(stats["home_score_exact"] and stats["away_score_exact"], "Score conservation failed")
        seen.add(game_id)
    require(seen == set(finals), "Expected Box Game IDs incomplete")
    return {"today": plan["stop_exclusive"], "final_game_ids": sorted(seen),
            "next_day_pending_ids": pending, "persistence": "NOT_VERIFIED"}


def invoke(args, script, action, ref, calls, observation_ms, pid, request):
    context = LiveExecutionContext(ref, frozenset({action}), calls, enabled=True, expected_pid=pid)
    transport = ReaCliTransport(args.runtime, context, duration_ms=observation_ms,
                                node_path=args.node, rea_path=args.rea)
    return transport.execute(script, action_id=action, request_id=request, maximum_game_calls=calls)


def read_native_today(args):
    from refresh import _context
    before = binding_snapshot(args.save_directory, args.loaded_filename)
    epoch = _context(args.pid)["epoch"]
    result = invoke(args, source("native_today.js"), "TEST_ONLY_READ_NATIVE_TODAY",
                    args.read_ref, 0, 15000, epoch["pid"], "read-native-today")
    require(result.get("event") == "REA_NATIVE_TODAY" and result["pid"] == epoch["pid"],
            "REA did not return a verified Today")
    after = binding_snapshot(args.save_directory, args.loaded_filename)
    scene = _context(args.pid)
    require(before == after and scene["epoch"] == epoch
            and scene["game_progress"]["today_native_iso_date"] == result["today"]
            and scene["game_progress"]["today_minutes_since_midnight_raw"] == result["minutes"],
            "Save binding, epoch or date changed")
    return result | {"binding_status": before["basis"], "save_id": before["save_id"],
                     "worldline_id": before["worldline_id"], "loaded_filename": before["loaded_filename"],
                     "binding_sha256": before["binding_sha256"], "epoch": epoch}


def simulate_to_native_date(args, plan, *, research_delegation=None):
    require(args.execute_once, "TEST_ONLY_SIM_DISABLED")
    if research_delegation is None:
        require(args.approval and args.approved_sha, "TEST_ONLY_SIM_DISABLED")
    else:
        require(not args.approval and not args.approved_sha, "Mixed calendar authority")
    validate_plan(plan)
    require(Path(args.outbox).resolve(strict=True) == Path(plan["outbox_db"]).resolve(strict=True),
            "Use the approved shared Host Outbox")
    def check_approval():
        if research_delegation is not None:
            return research_delegation.verify_calendar(plan)
        return load_approval(plan, args.approval, args.approved_sha, datetime.now(timezone.utc))

    grant = check_approval()
    script = render(plan, dispatch=True, expires=utc(grant["expires_at"]))
    preflight(plan)
    plan_digest = digest(plan)
    outbox = DecisionOutbox(args.outbox)
    if research_delegation is not None:
        research_delegation.reserve_calendar(plan)
    outbox.claim_test_calendar(plan_digest, plan["worldline_id"], plan["loaded_filename"],
                               digest(plan["epoch"]), plan["start"])
    try:
        check_approval()
        preflight(plan)
    except Exception as error:
        outbox.finish_test_calendar(plan_digest, "NOT_EXECUTED", "POST_CLAIM_PREFLIGHT_REJECTED")
        return {"status": "NOT_EXECUTED", "plan_digest": plan_digest, "reason": str(error)}
    try:
        result = invoke(args, script, ACTION, grant["human_decision_ref"], 1,
                        plan["observation_ms"], plan["epoch"]["pid"], plan_digest)
        require(result.get("plan_digest") == plan_digest, "Native result not bound to plan")
        folder = Path(result["runtime_directory"])
        raw = json.loads((folder / "evidence.json").read_text(encoding="utf-8-sig"))
        native = raw["normalized_result"]
        program = folder / "program.js"
        require(program.read_text(encoding="utf-8") == script
                and native["source_sha256"] == sha_file(program),
                "Dispatched REA source hash differs")
        if result.get("status") == "FRAME_GATE_NOT_OBSERVED":
            require(native["pid"] == plan["epoch"]["pid"] and not native["messages_truncated"]
                    and native["cleanup_error"] is None and len(native["messages"]) == 1
                    and native["messages"][0]["type"] == "send"
                    and native["messages"][0]["payload"].get("status") == "FRAME_GATE_NOT_OBSERVED",
                    "No-dispatch receipt incomplete")
            outbox.finish_test_calendar(plan_digest, "NOT_EXECUTED", raw["evidence_id"])
            return {"status": "NOT_EXECUTED", "reason": "FRAME_GATE_NOT_OBSERVED", "plan_digest": plan_digest}
        require(result.get("status") == "RETURNED_WITH_NATIVE_READBACK", "Native outcome incomplete")
        summary = audit_native_result(raw, plan)
        preflight(plan, after=True)
    except Exception as error:
        # A process interruption before this handler leaves CLAIMED, which also fences.
        receipt = result.get("runtime_directory", "RECONCILIATION_REQUIRED") if "result" in locals() else "RECONCILIATION_REQUIRED"
        outbox.finish_test_calendar(plan_digest, "UNKNOWN", receipt)
        return {"status": "UNKNOWN_NO_REPLAY", "plan_digest": plan_digest,
                "reason": str(error), "private_receipt": receipt}
    outbox.finish_test_calendar(plan_digest, "VERIFIED_IN_MEMORY", raw["evidence_id"])
    return {"status": "VERIFIED_IN_MEMORY", "plan_digest": plan_digest,
            "evidence_id": raw["evidence_id"], **summary}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("read-native-today", "plan", "observe-frame", "simulate-to-native-date", "inspect", "audit"))
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--outbox", type=Path)
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--approved-sha")
    parser.add_argument("--execute-once", action="store_true")
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--save-directory", type=Path)
    parser.add_argument("--loaded-filename")
    parser.add_argument("--pid", type=int)
    parser.add_argument("--read-ref")
    parser.add_argument("--node")
    parser.add_argument("--rea")
    args = parser.parse_args()
    try:
        if args.command == "read-native-today":
            require(args.runtime and args.save_directory and args.loaded_filename and args.pid and args.read_ref,
                    "Explicit read-only scope and bound slot required")
            result = read_native_today(args)
        else:
            require(args.plan is not None, "Exact plan file required")
            plan = load(args.plan)
            validate_plan(plan, observe=args.command == "observe-frame")
            if args.command == "plan":
                result = {"status": "PLAN_ONLY", "plan_digest": digest(plan), "default": "DISABLED"}
            elif args.command == "inspect":
                require(args.outbox and args.outbox.is_file(), "Existing shared Outbox required")
                require(args.outbox.resolve() == Path(plan["outbox_db"]).resolve(), "Outbox differs from plan")
                result = DecisionOutbox.inspect_test_calendar(args.outbox, digest(plan))
            elif args.command == "audit":
                require(args.receipt is not None, "Private REA receipt required")
                result = audit_native_result(json.loads(args.receipt.read_text(encoding="utf-8-sig")), plan)
            elif args.command == "observe-frame":
                require(args.runtime and args.read_ref, "Explicit read-only frame scope required")
                preflight(plan)
                result = invoke(args, render(plan, dispatch=False, expires=datetime.now(timezone.utc) + timedelta(minutes=1)),
                                "TEST_ONLY_OBSERVE_FRAME", args.read_ref, 0, plan["observation_ms"],
                                plan["epoch"]["pid"], digest(plan))
            else:
                require(args.runtime and args.outbox, "Private runtime and approved shared Outbox required")
                result = simulate_to_native_date(args, plan)
        print(json.dumps(result, indent=2))
        return 2 if result and ("UNKNOWN" in result.get("status", "")
                                or result.get("status") in {"NOT_EXECUTED", "FRAME_GATE_NOT_OBSERVED"}
                                or result.get("outcome")) else 0
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error) as error:
        print(json.dumps({"status": "STOPPED", "reason": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
