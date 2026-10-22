# -*- coding: utf-8 -*-
"""
NBA 2K22 原生赛程日历与对阵结果解码器 (AG-NATIVE-01C)
对应 ROSTERDATA Slot 44 (Offset +0x2C0, Stride 24, Capacity 1,260)
"""

import struct
from typing import Dict, Any, Optional

SCHEDULE_RECORD_BYTE_SIZE = 24


def decode_schedule_game(
    raw: bytes,
    game_index: int = 0,
    team_base: int = 0,
    team_names: Optional[Dict[int, str]] = None,
) -> Optional[Dict[str, Any]]:
    """解码 24 字节原生赛程对阵项"""
    if len(raw) != SCHEDULE_RECORD_BYTE_SIZE:
        raise ValueError(f"赛程记录长度必须为 {SCHEDULE_RECORD_BYTE_SIZE} 字节，收到 {len(raw)} 字节")

    home_ptr, away_ptr = struct.unpack_from("<QQ", raw, 0)
    if home_ptr == 0 or away_ptr == 0:
        return None  # 空赛程槽位

    score_1 = struct.unpack_from("<H", raw, 16)[0]
    score_2 = struct.unpack_from("<H", raw, 18)[0]
    status_code = struct.unpack_from("<H", raw, 20)[0]
    game_day_index = struct.unpack_from("<H", raw, 22)[0]

    # 解析主客场球队索引
    home_team_index = (home_ptr - team_base) // 4696 if (team_base > 0 and home_ptr >= team_base) else None
    away_team_index = (away_ptr - team_base) // 4696 if (team_base > 0 and away_ptr >= team_base) else None

    team_names = team_names or {}
    home_name = team_names.get(home_team_index, f"TEAM_{home_team_index}") if home_team_index is not None else "UNKNOWN"
    away_name = team_names.get(away_team_index, f"TEAM_{away_team_index}") if away_team_index is not None else "UNKNOWN"

    if status_code == 1:
        status_label = "HOME_WIN"
        is_played = True
    elif status_code == 0:
        status_label = "AWAY_WIN"
        is_played = True
    elif status_code == 65535:
        status_label = "UNPLAYED"
        is_played = False
    else:
        status_label = f"UNKNOWN_STATUS_{status_code}"
        is_played = False

    return {
        "game_index": game_index,
        "home_team_ptr": f"0x{home_ptr:X}",
        "away_team_ptr": f"0x{away_ptr:X}",
        "home_team_index": home_team_index,
        "away_team_index": away_team_index,
        "home_team_name": home_name,
        "away_team_name": away_name,
        "score_part1": score_1,
        "score_part2": score_2,
        "status_code": status_code,
        "status_label": status_label,
        "is_played": is_played,
        "game_day_index": game_day_index,
        "provenance": "ROSTERDATA_SLOT_44",
    }
