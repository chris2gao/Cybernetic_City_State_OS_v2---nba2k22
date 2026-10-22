"""Read calibrated NBA2K22 records for source research; never write game memory."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import struct

from address_calibrator import AddressCalibrator
from memory import GameMemory
import config

ROOT = Path(__file__).resolve().parent.parent


def text16(raw, offset, length=40):
    return raw[offset:offset + length].decode("utf-16le", errors="ignore").split("\0")[0].strip()


def probe(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with GameMemory(read_only=True) as mem:
        calibration = AddressCalibrator(mem).run_full_calibration()
        if calibration["status"] != "HEALTHY":
            raise RuntimeError("Read-only calibration failed")
        teams = AddressCalibrator(mem)._extract_teams_from_pacers(int(calibration["teams"]["pacers_base"], 16))
        staff_base = int(calibration["staff_pool"]["base_addr"], 16)
        staff_stride = int(calibration["staff_pool"]["stride"], 16)
        staff_count = int(calibration["staff_pool"]["count"])
        staff = []
        for slot in range(staff_count):
            address = staff_base + slot * staff_stride
            raw = mem.read_bytes(address, staff_stride)
            if raw is None:
                raise RuntimeError(f"Unreadable staff slot {slot}")
            (output / f"staff_{slot:03d}.bin").write_bytes(raw)
            record = mem.read_bytes(address - 0x30, staff_stride)
            if record is None:
                raise RuntimeError(f"Unreadable full staff record {slot}")
            (output / f"staff_record_{slot:03d}.bin").write_bytes(record)
            staff.append({"slot": slot, "address": hex(address), "first_name": text16(raw, 0),
                          "last_name": text16(raw, 40), "raw_team_byte": raw[0x60],
                          "record_address": hex(address - 0x30),
                          "team_pointer": hex(struct.unpack_from("<Q", record, 0x18)[0]),
                          "position_code": (record[0x10E] >> 2) & 7,
                          "salary_candidate": int.from_bytes(record[0xF8:0xFB], "little"),
                          "years_left": record[0x112] & 15,
                          "offense_code": record[0x100] & 15, "defense_code": record[0x100] >> 4})
        staff_by_address = {int(row["record_address"], 16): row for row in staff}
        team_by_address = {value["address"]: value["abbreviation"] for value in teams.values()}
        for row in staff:
            row["team_from_pointer"] = team_by_address.get(int(row["team_pointer"], 16))
        players, team_rows, seen = [], [], set()
        for team_id, team in sorted(teams.items()):
            address, abbreviation = team["address"], team["abbreviation"]
            raw = mem.read_bytes(address, config.TEAM_STRUCT_STRIDE)
            if raw is None:
                raise RuntimeError(f"Unreadable team {abbreviation}")
            (output / f"team_{abbreviation}.bin").write_bytes(raw)
            staff_links = []
            for offset in range(0, len(raw) - 7, 8):
                pointer = struct.unpack_from("<Q", raw, offset)[0]
                if pointer in staff_by_address:
                    person = staff_by_address[pointer]
                    staff_links.append({"team_offset": hex(offset), "staff_slot": person["slot"],
                                        "name": person["first_name"] + " " + person["last_name"]})
            team_rows.append({"team_id": team_id, "abbreviation": abbreviation, "address": hex(address),
                              "staff_pointer_links": staff_links})
            for offset in range(0, 0xC8, 8):
                pointer = struct.unpack_from("<Q", raw, offset)[0]
                if not pointer or pointer in seen:
                    continue
                first = mem.read_bytes(pointer, 0x4F0)
                if first is None:
                    raise RuntimeError(f"Unreadable player in {abbreviation}")
                name = (text16(first, 40) + " " + text16(first, 0)).strip()
                if sum(char.isalpha() for char in name) < 2:
                    raise RuntimeError(f"Invalid player identity in {abbreviation}")
                seen.add(pointer)
                number = len(players)
                extended = mem.read_bytes(pointer, 0xDF0)
                (output / f"player_{number:03d}.bin").write_bytes(extended if extended is not None else first)
                players.append({"index": number, "team": abbreviation, "team_id": team_id, "name": name,
                                "address": hex(pointer), "face_id": struct.unpack_from("<H", first, 0x6C)[0],
                                "salary_years_candidate": [struct.unpack_from("<I", first, 0x1A4 + 4 * year)[0] for year in range(6)],
                                "contract_raw": first[0x32E], "record_read_bytes": len(extended) if extended is not None else len(first),
                                "birth_year": int.from_bytes(first[0x6E:0x70], "little") & 0xFFF,
                                "birth_month": first[0x6F] >> 4, "birth_day": first[0x70] & 31,
                                "potential_candidate": config.raw_to_rating(first[0x441]),
                                "team_pointer": hex(struct.unpack_from("<Q", first, 0x60)[0]),
                                "contract_team_pointer": hex(struct.unpack_from("<Q", first, 0xA8)[0]),
                                "current_stats_id": struct.unpack_from("<H", first, 0xFC)[0]})
        report = {"captured_at": datetime.now(timezone.utc).isoformat(), "pid": mem.pid,
                  "module_base": hex(mem.base_address), "calibration": calibration,
                  "teams": team_rows, "staff": staff, "players": players,
                  "scope": "Exploratory known records; candidate fields are not verified facts."}
        (output / "probe.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"pid": mem.pid, "teams": len(team_rows), "players": len(players), "staff": len(staff),
                          "team_staff_pointer_matches": sum(len(row["staff_pointer_links"]) for row in team_rows),
                          "staff_team_pointer_matches": sum(row["team_from_pointer"] is not None for row in staff),
                          "output": str(output)}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_exports/source_discovery/current")
    args = parser.parse_args()
    probe(args.output)
