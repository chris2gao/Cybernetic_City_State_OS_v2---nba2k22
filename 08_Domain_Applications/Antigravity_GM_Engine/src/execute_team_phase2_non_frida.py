# -*- coding: utf-8 -*-
"""
NBA 2K22 单支球队 Phase 2 执行器（Playbook 68 槽 + Coach 设定/POE/PlaybookID + Initiator + 导出 Frida Native PlayType 载荷）
供 Phase 2 顺序执行 Subagent 按球队逐一调用：
1. python execute_team_phase2_non_frida.py --team <ABBR>
2. 读取输出的 <TEAM>_frida_payload.json，调用 rea:instrument_with_frida 执行 Native PLAYER_SET_PLAY_TYPES_1_TO_4 注入并 CAS 校验。
"""
import argparse
import json
import struct
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory import GameMemory  # noqa: E402
from coach_locator import CoachLocator, u64  # noqa: E402

SPEC_DIR = Path(r"C:\nba2k22\exports\20261126_all30_tactical_design_phase2")
PROFILE_PATH = ROOT / "config" / "coach_tactics_profile.json"


def norm_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return "".join(ch for ch in s.lower() if ch.isalnum())


def read_player_name(mem: GameMemory, p_addr: int) -> str:
    last = mem.read_bytes(p_addr + 0x00, 40).decode("utf-16le", errors="ignore").split("\x00")[0].strip()
    first = mem.read_bytes(p_addr + 0x28, 40).decode("utf-16le", errors="ignore").split("\x00")[0].strip()
    return f"{first} {last}".strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", required=True, help="3-letter team abbreviation, e.g. ATL")
    parser.add_argument("--dry-run", action="store_true", help="Resolve and verify without writing memory")
    args = parser.parse_args()

    team = args.team.upper()
    spec_path = SPEC_DIR / f"{team}_spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    prof = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

    mem = GameMemory(read_only=args.dry_run)
    if not hasattr(mem, "is_alive"):
        mem.is_alive = lambda: True
    loc = CoachLocator(mem).calibrate()

    tid = spec["team_id"]
    pb_enum = spec["playbook_enum_id"]
    book = next(b for b in loc.playbooks if b["enum_id"] == pb_enum)
    pb_ptr_base = u64(mem, loc.roster + loc.profile["native"]["playbook_pointer_offset"])
    pb_addr = pb_ptr_base + book["index"] * loc.profile["native"]["playbook_stride"]
    coach_addr = loc.coaches[tid]["address"]
    team_addr = loc.teams[tid]["address"]

    # 1. Playbook 68 slots
    before_slots = list(struct.unpack_from("<68I", mem.read_bytes(pb_addr + 0x58, 68 * 4), 0))
    target_crcs = [item["native_crc"] for item in spec["playbook_slots_ordered"]]
    assert len(target_crcs) == 68
    pb_writes = 0
    if not args.dry_run:
        for i, crc in enumerate(target_crcs):
            if before_slots[i] != crc:
                mem.write_bytes(pb_addr + 0x58 + i * 4, struct.pack("<I", crc))
                pb_writes += 1
        after_slots = list(struct.unpack_from("<68I", mem.read_bytes(pb_addr + 0x58, 68 * 4), 0))
        assert after_slots == target_crcs, f"{team}: Playbook 68 slots readback mismatch!"

    # 2. Coach settings & POE
    all_targets = {}
    all_targets.update(spec["coach_targets"]["settings"])
    all_targets.update(spec["coach_targets"]["poe"])
    coach_writes = 0
    if not args.dry_run:
        for fname, val in all_targets.items():
            if fname not in prof["fields"]:
                assert val == 0, f"{team} Coach unknown non-zero field {fname}={val}"
                continue
            fspec = prof["fields"][fname]
            off = fspec["offset"]
            sbytes = fspec["storage_bytes"]
            sbit = fspec["start_bit"]
            width = fspec["width"]
            mask = ((1 << width) - 1) << sbit
            if sbytes == 1:
                cur_b = mem.read_bytes(coach_addr + off, 1)[0]
                new_b = (cur_b & ~mask) | ((val << sbit) & mask)
                if new_b != cur_b:
                    mem.write_bytes(coach_addr + off, bytes([new_b]))
                    coach_writes += 1
                rb = mem.read_bytes(coach_addr + off, 1)[0]
                actual = (rb >> sbit) & ((1 << width) - 1)
            else:
                cur_w = struct.unpack("<I", mem.read_bytes(coach_addr + off, 4))[0]
                new_w = (cur_w & ~mask) | ((val << sbit) & mask)
                if new_w != cur_w:
                    mem.write_bytes(coach_addr + off, struct.pack("<I", new_w))
                    coach_writes += 1
                rb = struct.unpack("<I", mem.read_bytes(coach_addr + off, 4))[0]
                actual = (rb >> sbit) & ((1 << width) - 1)
            assert actual == val, f"{team} Coach {fname} mismatch: expected {val}, got {actual}"

    # 3. Resolve roster players & write Initiator (+0x16A bit 2)
    roster_map = {}
    for slot in range(25):
        p_addr = u64(mem, team_addr + slot * 8)
        if p_addr and p_addr > 0x10000:
            pname = read_player_name(mem, p_addr)
            if pname:
                roster_map[norm_name(pname)] = (pname, p_addr)

    frida_players = []
    unmatched = []
    init_writes = 0
    for pl in spec["player_playtypes"]:
        nkey = norm_name(pl["name"])
        match = roster_map.get(nkey)
        if not match:
            # fallback: substring or last name match
            for rk, rv in roster_map.items():
                if nkey in rk or rk in nkey:
                    match = rv
                    break
        if not match:
            unmatched.append(pl["name"])
            continue
        real_name, p_addr = match
        init_val = 1 if pl["initiator"] else 0
        if not args.dry_run:
            cur_362 = mem.read_bytes(p_addr + 362, 1)[0]
            new_362 = (cur_362 & ~(1 << 2)) | (init_val << 2)
            if new_362 != cur_362:
                mem.write_bytes(p_addr + 362, bytes([new_362]))
                init_writes += 1
            rb_362 = mem.read_bytes(p_addr + 362, 1)[0]
            assert ((rb_362 >> 2) & 1) == init_val, f"{team} {real_name} initiator CAS fail"
        sv = pl["slot_values"]
        frida_players.append({
            "name": real_name,
            "addr": hex(p_addr),
            "slots": [sv["1"], sv["2"], sv["3"], sv["4"]],
        })

    payload = {
        "pid": mem.pid,
        "team": team,
        "team_id": tid,
        "playbook_enum_id": pb_enum,
        "pb_addr": hex(pb_addr),
        "coach_addr": hex(coach_addr),
        "pb_writes": pb_writes,
        "coach_writes": coach_writes,
        "init_writes": init_writes,
        "matched_players": len(frida_players),
        "unmatched_players": unmatched,
        "players": frida_players,
    }
    out_payload = SPEC_DIR / f"{team}_frida_payload.json"
    out_payload.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "players"}, ensure_ascii=False))
    mem.close()


if __name__ == "__main__":
    main()
