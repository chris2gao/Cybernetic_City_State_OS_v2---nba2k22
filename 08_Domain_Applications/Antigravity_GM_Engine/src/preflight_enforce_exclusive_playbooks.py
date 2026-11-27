# -*- coding: utf-8 -*-
"""
NBA 2K22 专项任务前置条件检查与标准化脚本 (Preflight):
在每次启动《年度球队战术体系与手册设计》任务的最开始执行：
检查并强制将全联盟 30 支球队主教练的 PlaybookID 对齐为各自专属本队战术手册 (enum_id 0..29)，
防止部分球队（如 CHA/MEM/ORL/WAS）默认指向 Standard Playbook (30) 或错指他队手册（如 MIN->Grizzlies）。
"""
import argparse
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory import GameMemory  # noqa: E402
from coach_locator import CoachLocator  # noqa: E402

PROFILE_PATH = ROOT / "config" / "coach_tactics_profile.json"

# team_id -> (abbreviation, exclusive_playbook_enum_id)
TEAM_EXCLUSIVE_PLAYBOOK = {
    0: ("PHI", 0),   # 76ers Playbook
    1: ("MIL", 1),   # Bucks Playbook
    2: ("WAS", 29),  # Wizards Playbook
    3: ("CHI", 2),   # Bulls Playbook
    4: ("CLE", 3),   # Cavaliers Playbook
    5: ("BOS", 4),   # Celtics Playbook
    6: ("LAC", 5),   # Clippers Playbook
    8: ("MEM", 6),   # Grizzlies Playbook
    9: ("ATL", 7),   # Hawks Playbook
    10: ("MIA", 8),  # Heat Playbook
    11: ("NOP", 19), # Pelicans Playbook
    12: ("UTA", 10), # Jazz Playbook
    13: ("SAC", 11), # Kings Playbook
    14: ("NYK", 12), # Knicks Playbook
    15: ("LAL", 13), # Lakers Playbook
    16: ("ORL", 14), # Magic Playbook
    17: ("DAL", 15), # Mavericks Playbook
    18: ("BKN", 16), # Nets Playbook
    19: ("DEN", 17), # Nuggets Playbook
    20: ("IND", 18), # Pacers Playbook
    21: ("DET", 20), # Pistons Playbook
    22: ("TOR", 21), # Raptors Playbook
    23: ("HOU", 22), # Rockets Playbook
    24: ("OKC", 25), # Thunder Playbook
    25: ("SAS", 23), # Spurs Playbook
    26: ("PHX", 24), # Suns Playbook
    27: ("MIN", 26), # Timberwolves Playbook
    28: ("POR", 27), # Trail Blazers Playbook
    29: ("GSW", 28), # Warriors Playbook
    31: ("CHA", 9),  # Hornets Playbook
}


def main():
    parser = argparse.ArgumentParser(description="Preflight: check and enforce 30-team exclusive Coach.PlaybookID")
    parser.add_argument("--dry-run", action="store_true", help="Check only without writing memory")
    args = parser.parse_args()

    prof = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    f = prof["fields"]["PlaybookID"]
    off, sb, w, sbytes = f["offset"], f["start_bit"], f["width"], f["storage_bytes"]
    mask = ((1 << w) - 1) << sb
    val_mask = (1 << w) - 1

    mem = GameMemory(read_only=args.dry_run)
    if not hasattr(mem, "is_alive"):
        mem.is_alive = lambda: True
    loc = CoachLocator(mem).calibrate()
    pb_by_enum = {b["enum_id"]: b["name"] for b in loc.playbooks}

    updated = 0
    mismatches = 0
    for tid, (abbr, exp_pb) in sorted(TEAM_EXCLUSIVE_PLAYBOOK.items()):
        caddr = loc.coaches[tid]["address"]
        if sbytes == 1:
            cur_raw = mem.read_bytes(caddr + off, 1)[0]
        else:
            cur_raw = struct.unpack("<I", mem.read_bytes(caddr + off, 4))[0]
        cur_pb = (cur_raw >> sb) & val_mask
        cur_name = pb_by_enum.get(cur_pb, "?")
        exp_name = pb_by_enum.get(exp_pb, "?")

        if cur_pb != exp_pb:
            mismatches += 1
            if not args.dry_run:
                new_raw = (cur_raw & ~mask) | ((exp_pb << sb) & mask)
                if sbytes == 1:
                    mem.write_bytes(caddr + off, bytes([new_raw]))
                    rb = mem.read_bytes(caddr + off, 1)[0]
                else:
                    mem.write_bytes(caddr + off, struct.pack("<I", new_raw))
                    rb = struct.unpack("<I", mem.read_bytes(caddr + off, 4))[0]
                actual = (rb >> sb) & val_mask
                assert actual == exp_pb, f"{abbr} PlaybookID CAS fail: expected {exp_pb}, got {actual}"
                updated += 1
                print(f"[FIXED] {abbr:3s} tid={tid:2d}: {cur_pb:2d} ({cur_name}) -> {actual:2d} ({exp_name})")
            else:
                print(f"[MISMATCH] {abbr:3s} tid={tid:2d}: {cur_pb:2d} ({cur_name}) != {exp_pb:2d} ({exp_name})")
        else:
            print(f"[OK] {abbr:3s} tid={tid:2d}: {cur_pb:2d} ({cur_name})")

    print(f"Preflight Summary: PID={mem.pid} | Checked=30 | MismatchesFound={mismatches} | FixedWithCAS={updated}")
    mem.close()


if __name__ == "__main__":
    main()
