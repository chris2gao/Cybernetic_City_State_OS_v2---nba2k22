# -*- coding: utf-8 -*-
"""
NBA 2K22 原生历史纪录大全与排行榜解码器 (AG-NATIVE-01C)
对应 ROSTERDATA Slot 39 (Offset +0x270, Stride 52, Capacity 69,040)
"""

import struct
from typing import Dict, Any, Optional

RECORD_BYTE_SIZE = 52

CATEGORY_NAMES = {
    0x008F: "SINGLE_GAME_POINTS",
    0x018F: "SINGLE_GAME_FGM",
    0x028F: "SINGLE_GAME_3PM",
    0x038F: "SINGLE_GAME_FTM",
    0x048F: "SINGLE_GAME_REBOUNDS",
    0x058F: "SINGLE_GAME_ASSISTS",
    0x068F: "SINGLE_GAME_BLOCKS",
    0x078F: "SINGLE_GAME_STEALS",
    0x00AF: "PLAYOFF_GAME_POINTS",
    0x01AF: "PLAYOFF_GAME_FGM",
    0x02AF: "PLAYOFF_GAME_3PM",
    0x00CF: "SEASON_TOTAL_POINTS",
    0x01CF: "SEASON_TOTAL_FGM",
    0x02CF: "SEASON_TOTAL_3PM",
    0x00E0: "CAREER_TOTAL_POINTS",
    0x01E0: "CAREER_TOTAL_FGM",
    0x02E0: "CAREER_TOTAL_3PM",
    0x03E0: "CAREER_TOTAL_FTM",
    0x05E0: "CAREER_TOTAL_ASSISTS",
    0x06E0: "CAREER_TOTAL_BLOCKS",
    0x0AE0: "CAREER_AVG_PPG",
    0x0BE0: "CAREER_AVG_FG_PCT",
    0x0CE0: "CAREER_AVG_3P_PCT",
    0x0DE0: "CAREER_AVG_FT_PCT",
    0x0FE0: "CAREER_AVG_APG",
    0x10E0: "CAREER_AVG_BPG",
    0x11E0: "CAREER_AVG_SPG",
    0x12E0: "CAREER_AVG_MPG",
    0x13E0: "CAREER_TOTAL_GAMES",
    0x14E0: "CAREER_TOTAL_FOULS",
    0x17E0: "CAREER_TOTAL_TRIPLE_DOUBLES",
    0x17EF: "ACTIVE_CAREER_TRIPLE_DOUBLES",
}


def decode_record_book_entry(raw: bytes, index: int = 0) -> Optional[Dict[str, Any]]:
    """解码 52 字节历史纪录项"""
    if len(raw) != RECORD_BYTE_SIZE:
        raise ValueError(f"记录长度必须为 {RECORD_BYTE_SIZE} 字节，收到 {len(raw)} 字节")

    if not any(raw):
        return None  # 空记录

    first_name = raw[0:20].split(b"\x00")[0].decode("latin1", errors="ignore").strip()
    last_name = raw[20:40].split(b"\x00")[0].decode("latin1", errors="ignore").strip()
    full_name = f"{first_name} {last_name}".strip()

    stat_value = struct.unpack_from("<f", raw, 40)[0]
    packed_date = struct.unpack_from("<H", raw, 44)[0]
    cat_code = struct.unpack_from("<H", raw, 46)[0]
    player_id = struct.unpack_from("<H", raw, 48)[0]
    flags = struct.unpack_from("<H", raw, 50)[0]

    # 解码 16 位压缩日期 (1920 Epoch)
    date_iso = None
    if packed_date > 0:
        year = 1920 + (packed_date >> 9)
        month = (packed_date >> 5) & 0x0F
        day = packed_date & 0x1F
        if 1 <= month <= 12 and 1 <= day <= 31:
            date_iso = f"{year:04d}-{month:02d}-{day:02d}"

    cat_label = CATEGORY_NAMES.get(cat_code, f"CATEGORY_0x{cat_code:04X}")

    return {
        "index": index,
        "first_name": first_name,
        "last_name": last_name,
        "full_name": full_name,
        "stat_value": round(stat_value, 3),
        "packed_date": packed_date,
        "game_date": date_iso,
        "category_code": cat_code,
        "category_label": cat_label,
        "player_id": player_id,
        "flags": flags,
        "provenance": "ROSTERDATA_SLOT_39",
    }
