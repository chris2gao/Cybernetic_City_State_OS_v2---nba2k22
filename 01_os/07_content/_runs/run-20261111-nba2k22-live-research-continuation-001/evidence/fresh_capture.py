from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
repo = root.parents[4]
worlddata = repo / "08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype"
native = repo / "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control"
sys.path[:0] = [str(worlddata), str(native)]
from live_world import initialize_save
from live_reader import ReadOnlyGameProcess
from refresh import _context, refresh_world
from player_skill_reader import collect_player_skills, read_tendency_neighborhood
from native_factor_slots import resolve_tendency_slot

pid = int(sys.argv[1])
slot = Path("E:/games/NBA 2K22/data/steam/steam_settings/1644960/remote/MyLEAGUE0005")
cold = slot.with_name("MyLEAGUE0003")
world = root / "world-0005"
output = root / "fresh-capture"
receipt_path = root / "fresh-capture-receipt.json"

def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

try:
    before = _context(pid)
    scene = {key: before[key] for key in ("epoch", "game_progress")}
    disk_hash, cold_hash = sha(slot), sha(cold)
    assert not slot.samefile(cold)
    assert scene["game_progress"]["mode_raw"] == 1 and scene["game_progress"]["period_raw"] == 29
    assert scene["game_progress"]["league_raw"] == 0
    binding = initialize_save(world, "nba40-live0005-20261111", slot)
    binding["worldline_id"] = "WL0005-LIVE-20261111"
    binding["slot_declaration_ref"] = "Human current request to start prepared 0005"
    (world / "save.json").write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8")
    print("Native WorldData capture started", flush=True)
    refresh_world(pid, world, slot.name, output, families=(
        "schedule", "game-mode", "lineups", "settings", "player-state", "player-skills", "planning"))
    target_ids = (1, 66, 2, 3, 27, 4, 17, 5, 18, 6, 22, 7, 23, 8, 24, 16)
    slots = [resolve_tendency_slot(f"TENDENCY_NATIVE_{number:03d}") for number in target_ids]
    reader = ReadOnlyGameProcess(pid)
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
            raw = {slot.factor_id: slot.decode(image) for slot in slots}
            rows.append({"uid": uid, "team_id": team, "source_player_index": row["source_player_index"],
                         "roster_slot": row["current_roster_slot"], "neighborhood_hex": image.hex(),
                         "neighborhood_sha256": hashlib.sha256(image).hexdigest(), "values": raw})
    finally:
        reader.close()
    after = _context(pid)
    assert scene == {key: after[key] for key in scene}
    assert disk_hash == sha(slot) and cold_hash == sha(cold)
    raw_path = root / "fresh-16-slot-values.json"
    raw_path.write_text(json.dumps({"mode": "LIVE_READ", "epoch": scene["epoch"], "rows": rows}, indent=2) + "\n", encoding="utf-8")
    result = {"status": "CAPTURE_COMPLETE", "captured_at": datetime.now(timezone.utc).isoformat(),
              "scene": scene, "slot": slot.name, "slot_identity_basis": binding["slot_declaration_ref"],
              "native_slot_sha256": disk_hash, "cold_backup_sha256": cold_hash,
              "binding_sha256": sha(world / "save.json"), "source_report_sha256": sha(output / "refresh-report.json"),
              "raw_slot_values_sha256": sha(raw_path), "current_roster_subjects": len(rows), "requested_slots": target_ids,
              "native_writes": 0, "calendar_dispatches": 0}
except Exception as error:
    result = {"status": "CAPTURE_FAILED", "error_type": type(error).__name__, "error": str(error),
              "winerror": getattr(error, "winerror", None), "native_writes": 0, "calendar_dispatches": 0}
receipt_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, separators=(",", ":")), flush=True)
raise SystemExit(result["status"] != "CAPTURE_COMPLETE")
