# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 全量球员池数据库转储与历史选秀注入引擎 (Player Pool & Draft Injector)
严格执行工程加固与数据真实性规范：
1. 强制接入 AddressCalibrator：每次转储必须先执行动态内存校准与锚点校验，禁止盲目使用固定基址。
2. 暂存缓冲与原子提交 (Atomic Staging)：先写入 staging_player_pool，校验有效槽位数 (>=3000) 与乔丹/大梦锚点，通过后原子切换，防止坏批次破坏旧库。
3. 彻底清除 80 默认值填充：保留 raw_potential 原始字节，未确认语义的潜力字段显式记为 NULL。
4. 在采集期间从球员结构偏移 0x70 统计历史新秀类型码；只持久化原始结构，不重复存储可重算的标签字段。
"""
import os
import sys
import struct
import sqlite3
from typing import Dict, List, Optional, Tuple

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from address_calibrator import AddressCalibrator
from source_extensions import roster_directory, player_details
import config
import json
from historical_rookies import (
    HISTORICAL_ROOKIE_TAG_MASK,
    HISTORICAL_ROOKIE_TAG_OFFSET,
    PLAYER_POOL_STRIDE,
    is_historical_rookie,
    query_historical_draft_class,
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "nba2k22_players.sqlite")
TOTAL_SLOTS = 3320
POS_NAMES = {0: "PG", 1: "SG", 2: "SF", 3: "PF", 4: "C"}

def init_player_pool_schema(conn: sqlite3.Connection):
    """创建 player_pool 表；原始结构是类型码的唯一持久化来源。"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_pool (
            slot_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            draft_year INTEGER,
            draft_round INTEGER,
            draft_pick INTEGER,
            overall_pick INTEGER,
            cyberface_id INTEGER,
            position INTEGER,
            position_name TEXT,
            raw_potential INTEGER,
            potential INTEGER,
            memory_addr TEXT,
            raw_struct BLOB
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_draft_year_pick ON player_pool(draft_year, draft_round, draft_pick)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_full_name ON player_pool(full_name)")
    conn.commit()

def dump_all_players_to_db(
    mem: Optional[GameMemory] = None,
    total_slots: Optional[int] = None,
    db_path: str = DB_PATH,
) -> int:
    """
    全量抓取球员池入库：强制校验基址 -> 暂存区落盘 -> 锚点门槛断言 -> 原子切换
    """
    mem = mem or GameMemory(process_name="NBA2K22.exe")
    calibrator = AddressCalibrator(mem)
    
    # 1. 强制动态地址校准 (Calibrate First)
    pool_ok, base_addr = calibrator.check_and_calibrate_player_pool()
    stride = PLAYER_POOL_STRIDE
    if not pool_ok or base_addr == 0:
        raise RuntimeError("【校准熔断】历史球员池物理基址未通过校准，终止抓取以保护现有数据库！")
    directory = roster_directory(mem, base_addr)
    descriptor_slots = directory['players']['count'] + 1  # Retain legacy root-relative model slot IDs.
    if total_slots is not None and total_slots != descriptor_slots:
        raise ValueError('Explicit slot limit differs from the complete live roster descriptor')
    total_slots = descriptor_slots

    print(f"[*] 成功挂接 NBA2K22 进程 (PID: {mem.pid})")
    print(f"[*] 球员池基址已通过校准锁定: {hex(base_addr)} (步长: {hex(stride)}, 总槽位: {total_slots})")

    db_path = os.path.abspath(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    init_player_pool_schema(conn)

    # 2. 创建临时暂存表 staging_player_pool
    cursor.execute("DROP TABLE IF EXISTS staging_player_pool")
    cursor.execute("""
        CREATE TABLE staging_player_pool (
            slot_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            draft_year INTEGER,
            draft_round INTEGER,
            draft_pick INTEGER,
            overall_pick INTEGER,
            cyberface_id INTEGER,
            position INTEGER,
            position_name TEXT,
            raw_potential INTEGER,
            potential INTEGER,
            memory_addr TEXT,
            raw_struct BLOB
        )
    """)

    players_to_insert = []
    valid_count = 0
    rejected_short_name_count = 0
    historical_rookie_count = 0
    draft_years_found = set()

    total_bytes = total_slots * stride
    all_raw = mem.read_bytes(base_addr, total_bytes)
    use_bulk = bool(all_raw and len(all_raw) == total_bytes)

    for i in range(total_slots):
        offset_in_buf = i * stride
        slot_addr = base_addr + offset_in_buf

        if use_bulk:
            raw_struct = all_raw[offset_in_buf : offset_in_buf + stride]
        else:
            raw_struct = mem.read_bytes(slot_addr, stride)

        if not raw_struct or len(raw_struct) < stride:
            conn.rollback()
            conn.close()
            raise RuntimeError(
                f"【读取熔断】球员池 Slot {i} 无法完整读取 {stride} 字节；"
                "不能将不可读槽位当作空槽位，保留原正式球员池。"
            )

        # 姓名 (UTF-16LE, 各 40 字节)
        last_name = raw_struct[0:40].decode('utf-16le', errors='ignore').split('\x00')[0].strip()
        first_name = raw_struct[40:80].decode('utf-16le', errors='ignore').split('\x00')[0].strip()

        full_name = f"{first_name} {last_name}".strip()
        if sum(character.isalpha() for character in full_name) < 2:
            if first_name or last_name:
                rejected_short_name_count += 1
            continue

        cf_id = struct.unpack_from("<H", raw_struct, 0x6C)[0]

        # 选秀年份与顺位
        raw_year_byte = struct.unpack_from("<B", raw_struct, 0x179)[0]
        draft_year = 1900 + raw_year_byte if raw_year_byte > 0 else 0

        raw_round_byte = struct.unpack_from("<B", raw_struct, 0x316)[0]
        draft_round = (raw_round_byte >> 4) & 0x0F

        raw_pick_u16 = struct.unpack_from("<H", raw_struct, 0x312)[0]
        draft_pick = (raw_pick_u16 >> 6) & 0x3F

        # The source exposes a round and an in-round pick. A reliable
        # league-wide overall pick for later rounds needs the number of
        # selections in each preceding round for that specific year; do not
        # assume every historical draft had 30 teams or write a fake sentinel.
        overall_pick = draft_pick if draft_round == 1 and 1 <= draft_pick <= 60 else None

        # 位置
        raw_pos = struct.unpack_from("<B", raw_struct, 0xF9)[0]
        pos_idx = raw_pos & 0x07
        pos_name = POS_NAMES.get(pos_idx)

        # 潜力字段真实化处理：杜绝 80 默认常数！
        raw_pot = raw_struct[0x441]
        verified_pot = config.raw_to_rating(raw_pot)

        # Inspect the source type byte for batch validation. The full raw
        # structure is retained, so the same classification can be recomputed.
        rookie_match = is_historical_rookie(raw_struct)
        if rookie_match is None:
            raise RuntimeError(f"球员槽位 {i} 的结构体不含历史新秀类型字节 0x{HISTORICAL_ROOKIE_TAG_OFFSET:X}")

        if 1950 <= draft_year <= 2030:
            draft_years_found.add(draft_year)

        players_to_insert.append((
            i, first_name, last_name, full_name,
            draft_year, draft_round, draft_pick, overall_pick,
            cf_id, pos_idx, pos_name,
            raw_pot, verified_pot,
            None,
            raw_struct
        ))
        historical_rookie_count += int(rookie_match)
        valid_count += 1

    # 写入暂存表
    cursor.executemany("""
        INSERT INTO staging_player_pool 
        (slot_id, first_name, last_name, full_name, draft_year, draft_round, draft_pick, overall_pick, cyberface_id, position, position_name, raw_potential, potential, memory_addr, raw_struct)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, players_to_insert)
    conn.commit()

    # 3. 门槛校验断言 (Validation Threshold Assertions)
    print(f"[*] 暂存区抓取完成 (有效记录: {valid_count} 条)，正在执行数据健康度断言...")
    if valid_count < 3000:
        cursor.execute("DROP TABLE staging_player_pool")
        conn.close()
        raise RuntimeError(f"【质量门槛熔断】有效槽位数不足 3000 (实际: {valid_count})，取消提交！")

    # 检查迈克尔·乔丹 (Face ID 1759, 1984)
    cursor.execute("SELECT count(*) FROM staging_player_pool WHERE full_name = 'Michael Jordan' AND cyberface_id = 1759")
    jordan_count = cursor.fetchone()[0]
    if jordan_count == 0:
        cursor.execute("DROP TABLE staging_player_pool")
        conn.close()
        raise RuntimeError("【锚点校验熔断】未能定位到核心基准锚点迈克尔·乔丹 (Face ID 1759)，取消提交！")

    # 检查奥拉朱旺 (Face ID 952, 1984)
    cursor.execute("SELECT count(*) FROM staging_player_pool WHERE full_name = 'Hakeem Olajuwon' AND cyberface_id = 952")
    hakeem_count = cursor.fetchone()[0]
    if hakeem_count == 0:
        cursor.execute("DROP TABLE staging_player_pool")
        conn.close()
        raise RuntimeError("【锚点校验熔断】未能定位到核心基准锚点奥拉朱旺 (Face ID 952)，取消提交！")

    if historical_rookie_count == 0:
        cursor.execute("DROP TABLE staging_player_pool")
        conn.close()
        raise RuntimeError("【标签校验熔断】未解析到任何历史新秀类型码 7 (raw[0x70] & 0xE0 == 0xE0)，取消提交！")

    # 4. 原子切换暂存表为正式表 (Atomic Swap)
    try:
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute("DROP TABLE IF EXISTS player_pool")
        cursor.execute("ALTER TABLE staging_player_pool RENAME TO player_pool")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_draft_year_pick ON player_pool(draft_year, draft_round, draft_pick)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_full_name ON player_pool(full_name)")
        cursor.execute('ALTER TABLE player_pool ADD COLUMN source_details_json TEXT')
        for row in players_to_insert:
            details = player_details(row[-1])
            cursor.execute('UPDATE player_pool SET source_details_json=? WHERE slot_id=?',
                           (json.dumps(details, sort_keys=True), row[0]))
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        raise
    conn.close()

    print(f"[+] 历史球员池校验通过并完成原子入库！")
    print(f"    - 全量有效球员: {valid_count} 人")
    print(f"    - 拒绝姓名无效/不足 2 个字母的非空槽位: {rejected_short_name_count} 个")
    print(f"    - 选秀年份跨度: {min(draft_years_found) if draft_years_found else 'N/A'} ~ {max(draft_years_found) if draft_years_found else 'N/A'} 年")
    print(f"    - 乔丹/大梦锚点断言: 100% 确认通过")
    print(f"    - 历史新秀类型码 7: {historical_rookie_count} 人 (字段 0x{HISTORICAL_ROOKIE_TAG_OFFSET:X}, 掩码 0x{HISTORICAL_ROOKIE_TAG_MASK:02X})")
    print(f"    - 潜力: 读取 0x441 原始值后确定性解码；不使用旧 0xEB 猜测值")
    print(f"    - 数据库落盘: {db_path}")
    return valid_count

def query_draft_class(year: int, limit: int = 60, db_path: str = DB_PATH) -> List[Dict]:
    """按年份返回已通过历史新秀类型码校验且已排重的候选名单。"""
    return query_historical_draft_class(db_path=db_path, year=year, limit=limit)

if __name__ == "__main__":
    dump_all_players_to_db()
