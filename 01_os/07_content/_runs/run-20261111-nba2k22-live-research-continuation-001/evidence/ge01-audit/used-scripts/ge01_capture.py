"""Fresh W01 baseline using existing readers; no game calls or game writes."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[5]
DOMAIN = REPO / "08_Domain_Applications/Antigravity_GM_Engine"
sys.path[:0] = [str(DOMAIN / "world_data_prototype"), str(DOMAIN / "research/rea_native_control")]
from live_world import initialize_save
from live_reader import ReadOnlyGameProcess
from refresh import _context, refresh_world
from player_skill_reader import collect_player_skills, read_tendency_neighborhood
from native_factor_slots import resolve_tendency_slot

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("C:/Users/gk/Documents/ChatGPT/nba2k22/ge01-runtime")
SLOT = Path("E:/games/NBA 2K22/data/steam/steam_settings/1644960/remote/MyLEAGUE0005")
COLD = SLOT.with_name("MyLEAGUE0003")
PID = int(sys.argv[2]) if len(sys.argv) > 2 else 6964


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    receipt_path = ROOT / "FRESH_BASELINE_RECEIPT.json"
    if receipt_path.exists():
        raise FileExistsError("Existing capture receipt must be reconciled, never overwritten")
    try:
        before = _context(PID)
        scene = {key: before[key] for key in ("epoch", "game_progress")}
        mode = scene["game_progress"]
        assert mode["mode_raw"] == 1 and mode["period_raw"] == 29 and mode["league_raw"] == 0
        slot_sha = sha(SLOT)
        cold_sha = sha(COLD) if COLD.is_file() else None
        binding = initialize_save(ROOT / "world-0005", "nba-ge01-0005-20261114", SLOT)
        binding["worldline_id"] = "WL0005-GE01-" + ROOT.name
        binding["slot_declaration_ref"] = "Current Human replies: 0005, 已加载干净0005; GE-01 contract comment 6873776739"
        (ROOT / "world-0005/save.json").write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
        print("Fresh six-family W01 acquisition started; game writes=0", flush=True)
        refresh_world(PID, ROOT / "world-0005", SLOT.name, ROOT / "fresh-capture",
                      families=("schedule", "game-mode", "lineups", "settings", "player-state", "player-skills"))
        requested = (1, 66, 2, 3, 27, 4, 17, 5, 18, 6, 22, 7, 23, 8, 24, 16)
        slots = [resolve_tendency_slot(f"TENDENCY_NATIVE_{number:03d}") for number in requested]
        reader = ReadOnlyGameProcess(PID)
        try:
            model, _ = collect_player_skills(reader)
            pool = model["descriptors"][1]
            counts = Counter(row["native_unique_id_raw"] for row in model["players"])
            rows = []
            for row in model["players"]:
                uid, team = row["native_unique_id_raw"], row["native_team_id"]
                if row["current_core_roster_status"] != "CURRENT_CORE_ROSTER" or counts[uid] != 1:
                    continue
                if type(uid) is not int or type(team) is not int or not 1 <= uid <= 65535:
                    continue
                image = read_tendency_neighborhood(reader, pool, row["source_player_index"])
                rows.append({"uid": uid, "team_id": team, "source_player_index": row["source_player_index"],
                             "roster_slot": row["current_roster_slot"], "neighborhood_hex": image.hex(),
                             "neighborhood_sha256": hashlib.sha256(image).hexdigest(),
                             "values": {slot.factor_id: slot.decode(image) for slot in slots}})
        finally:
            reader.close()
        after = _context(PID)
        assert scene == {key: after[key] for key in scene}
        assert slot_sha == sha(SLOT) and (cold_sha is None or cold_sha == sha(COLD))
        raw_path = ROOT / "fresh-16-slot-values.json"
        raw_path.write_text(json.dumps({"mode": "LIVE_READ", "epoch": scene["epoch"], "rows": rows}, indent=2) + "\n", encoding="utf-8")
        old = json.loads((REPO / "01_os/07_content/_runs/run-20261111-nba2k22-live-research-continuation-001/FIRST_BATCH_FROZEN_PLAN.json").read_bytes())
        by_uid = {row["uid"]: row for row in rows}
        comparison = [{"uid": item["uid"], "factor_id": item["factor_id"], "old_before": item["expected_before"],
                       "qualification_target": item["target"], "fresh": by_uid.get(item["uid"], {}).get("values", {}).get(item["factor_id"])}
                      for item in old["qualifications"]]
        result = {"status": "CAPTURE_COMPLETE", "captured_at": datetime.now(timezone.utc).isoformat(),
                  "scene": scene, "slot": SLOT.name, "slot_identity_basis": binding["slot_declaration_ref"],
                  "native_slot_sha256": slot_sha, "cold_backup_sha256": cold_sha,
                  "binding_sha256": sha(ROOT / "world-0005/save.json"),
                  "source_report_sha256": sha(ROOT / "fresh-capture/refresh-report.json"),
                  "raw_slot_values_sha256": sha(raw_path), "current_roster_subjects": len(rows),
                  "qualification_comparison": comparison, "all_16_match_original": all(row["fresh"] == row["old_before"] for row in comparison),
                  "native_writes": 0, "calendar_dispatches": 0, "save_restore_or_save": False}
    except Exception as error:
        result = {"status": "CAPTURE_FAILED", "error_type": type(error).__name__, "error": str(error),
                  "winerror": getattr(error, "winerror", None), "native_writes": 0, "calendar_dispatches": 0}
    with receipt_path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({key: value for key, value in result.items() if key != "qualification_comparison"}), flush=True)
    return result["status"] != "CAPTURE_COMPLETE"


if __name__ == "__main__":
    raise SystemExit(main())
