"""Read the existing S3 test world and one eligible S4 SHOT_TENDENCY candidate."""
import argparse
from collections import Counter
from contextlib import closing
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
ENGINE = ROOT / "08_Domain_Applications/Antigravity_GM_Engine"
sys.path[:0] = [str(ENGINE / "world_data_prototype"), str(ENGINE / "research/rea_native_control")]

from contracts import BUILD
from engine import connect
from live_reader import ReadOnlyGameProcess
from live_world import bound_database, read_binding
from player_skill_reader import PROFILE, collect_player_skills
from refresh import _context, resolve_pid
from schedule_reader import collect_schedule


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def inspect(runtime, team):
    state = json.loads((runtime / "host-state.json").read_bytes())
    world = runtime / "world"
    save = state["loaded_filename"]
    binding, binding_sha = read_binding(world, save)
    db = bound_database(world, binding)
    if state["save_id"] != binding["save_id"] or state["worldline_id"] != binding["worldline_id"]:
        raise ValueError("Host and SQLite binding disagree")
    if Path(state["database_file"]).resolve() != db:
        raise ValueError("Host SQLite path differs from binding")
    if state["active_plan"] is not None or state["status"] != "NEXT_CAPTURED":
        raise ValueError("Retained Host has unfinished work or is not at the capture checkpoint")
    with closing(sqlite3.connect((runtime / "outbox.sqlite").as_uri() + "?mode=ro", uri=True)) as conn:
        cycles = conn.execute("SELECT cycle_id,status FROM decision_cycles ORDER BY cycle_id").fetchall()
        intents = conn.execute("SELECT count(*) FROM decision_intents").fetchone()[0]
    if len(cycles) != 4 or any(status != "COMPLETED" for _, status in cycles) or intents:
        raise ValueError("Retained S3 Outbox is not four completed zero-intent cycles")
    backup = runtime / "native-disk-backup" / save
    backup_sha = digest(backup)
    initial = json.loads((runtime / "l2-receipt.json").read_bytes())
    if backup_sha != initial["native_sha256_before"]:
        raise ValueError("Retained backup hash does not match the historical S3 receipt")

    pid = resolve_pid("auto")
    before = _context(pid)
    with closing(ReadOnlyGameProcess(pid)) as reader:
        size = wintypes.DWORD(32768)
        image = ctypes.create_unicode_buffer(size.value)
        if not reader.k.QueryFullProcessImageNameW(reader.handle, 0, image, ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())
        build = digest(Path(image.value))
        if build != BUILD or reader.creation_filetime != before["epoch"]["creation_filetime"]:
            raise ValueError("Live build or process epoch changed")
        sched = collect_schedule(reader, with_calendar=True, read_final_boxes=False)
        date = sched["calendar"]["current_native_iso_date"]
        entries = [e for e in sched["manifest"]["entries"] if e.get("record_shape_valid")]
        finals = {str(e["native_game_id"]) for e in entries if e.get("status") == 2}
        if date != state["current_game_date"] or any(e.get("status") == 1 for e in entries):
            raise ValueError("Live calendar differs from the retained capture or a game is underway")
        with closing(connect(db, True)) as conn:
            known = {str(row[0]) for row in conn.execute(
                "SELECT DISTINCT g.native_game_id FROM games g JOIN game_state_observations s USING(game_id) WHERE s.is_final=1"
            )}
        if finals != known:
            raise ValueError("Live finalized games differ from bound SQLite")
        metadata = PROFILE["tendencies"]["shot_tendency_raw"]
        low = metadata["offset"]
        high = low + (metadata["start_bit"] + metadata["width"] + 7) // 8
        # Read identity and the one requested tendency through the existing public reader.
        ranges = sorted([(0, 80), (96, 104), (244, 246), (760, 764), (low, high)])
        pool, _ = collect_player_skills(reader, ranges=ranges)
        seen = Counter(p["native_unique_id_raw"] for p in pool["players"])
        teams = {tid: address for address, tid in pool["core_team_pointer_map"].items()}
        table = pool["descriptors"][1]
        candidates = []
        for player in sorted(pool["players"], key=lambda p: p["native_unique_id_raw"]):
            uid = player["native_unique_id_raw"]
            slot = player["current_roster_slot"]
            if (player["native_team_id"] != team or slot is None or slot >= 15
                    or player["current_core_roster_status"] != "CURRENT_CORE_ROSTER"
                    or seen[uid] != 1 or uid <= 0):
                continue
            index = player["source_player_index"]
            address = table["address"] + index * table["stride"]
            contract_team = int.from_bytes(reader.read(address + 0xa8, 8, "S4_CONTRACT_TEAM"), "little")
            if contract_team != teams[team]:
                continue
            value = pool["skill_rows"][index]["tendencies"]["shot_tendency_raw"]
            if type(value) is not int or not 0 <= value <= 100:
                continue
            candidates.append({"team_id": team, "player_id": uid, "preserved_id": player["preserved_id_raw"],
                               "name": player["observed_name"], "roster_slot": slot, "field_id": "SHOT_TENDENCY",
                               "expected_before": value, "proposed_value": value + (1 if value < 100 else -1)})
            break
        if not candidates:
            raise ValueError("No uniquely identified, current/contract-roster player qualified")
    after = _context(pid)
    if any(after[key] != before[key] for key in ("epoch", "game_progress")):
        raise ValueError("Process or calendar changed during the read")
    return {"status": "AUTHORIZATION_PENDING_HUMAN", "live_epoch": before["epoch"], "build_sha256": build,
            "schedule_date": date, "game_mode_today": before["game_progress"]["today_native_iso_date"],
            "save_binding_basis": "historical Human declaration; current on-screen loaded filename not independently observable",
            "binding_sha256": binding_sha, "save_file": save, "save_id": binding["save_id"],
            "worldline_id": binding["worldline_id"], "database": db.name, "sqlite_final_count": len(known),
            "host_status": state["status"], "host_cursor": state["current_cycle_id"], "outbox_intents": intents,
            "cold_backup_sha256": backup_sha, "cold_backup_is_historical": True,
            "role_manifest_present": (world / "role_authorizations.json").is_file(), "candidates": candidates}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--team", type=int, required=True)
    args = parser.parse_args()
    if args.out.resolve().is_relative_to(args.runtime.resolve()):
        parser.error("write the receipt outside the retained private runtime")
    start = time.perf_counter()
    try:
        result = inspect(args.runtime.resolve(), args.team)
        code = 0
    except Exception as exc:
        result = {"status": "LIVE_READ_NOT_VERIFIED", "error_type": type(exc).__name__,
                  "winerror": getattr(exc, "winerror", None)}
        if isinstance(exc, (ValueError, RuntimeError)):
            result["reason"] = str(exc)
        code = 1
    result["elapsed_seconds"] = round(time.perf_counter() - start, 3)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
