# -*- coding: utf-8 -*-
"""
NBA 2K22 原生数据深度挖掘独立 SQLite 样本库生成与导出模块 (AG-NATIVE-01B)

支持无游戏环境的离线二进制固件解析，以及有游戏运行时的实时只读内存提取。
将逆向还原的 ROSTERDATA 原生结构与 136 字节 WAIVED_SALARY 映射为关系型模型。
"""

import os
import sqlite3
import struct
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple


SCHEMA_PATH = Path(__file__).parent / "native_sample_schema.sql"
DEFAULT_FIXTURES_DIR = Path(__file__).parent / "fixtures"


class NativeSqliteExporter:
    """原生二进制记录到独立 SQLite 样本库的导出与转换引擎"""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """应用建表 SQL 脚本"""
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(schema_sql)
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def decode_waived_salary(raw: bytes, slot_index: int, team_base: int = 0) -> Optional[Dict[str, Any]]:
        """精确解码 136 字节原生 WAIVED_SALARY 记录"""
        if len(raw) != 136:
            raise ValueError(f"WAIVED_SALARY 记录步长必须为 136 字节，收到 {len(raw)} 字节")

        team_ptr = struct.unpack_from("<Q", raw, 0x08)[0]
        if team_ptr == 0:
            return None  # 空记录槽位

        prev_ptr = struct.unpack_from("<Q", raw, 0x00)[0]
        s1, s2, s3, s4, s5, s6 = struct.unpack_from("<IIIIII", raw, 0x10)
        player_id = struct.unpack_from("<H", raw, 0x34)[0]

        # UTF-16LE 姓名解码并去除空字符
        last_name_raw = raw[0x38:0x60].split(b"\x00\x00\x00")[0]
        if len(last_name_raw) % 2 != 0:
            last_name_raw += b"\x00"
        last_name = last_name_raw.decode("utf-16le", errors="ignore").rstrip("\x00").strip()

        first_name_raw = raw[0x60:0x80].split(b"\x00\x00\x00")[0]
        if len(first_name_raw) % 2 != 0:
            first_name_raw += b"\x00"
        first_name = first_name_raw.decode("utf-16le", errors="ignore").rstrip("\x00").strip()

        full_name = f"{first_name} {last_name}".strip()

        # 球队索引计算 (若提供 team_base)
        team_index = (team_ptr - team_base) // 4696 if (team_base > 0 and team_ptr >= team_base) else -1

        amounts = [s1, s2, s3, s4, s5, s6]
        total_dead_cap = sum(amounts)
        remaining_seasons = sum(1 for a in amounts if a > 0)
        is_stretched = 1 if remaining_seasons >= 3 else 0

        return {
            "slot_index": slot_index,
            "team_index": team_index,
            "player_id": player_id,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "season_1_amount": s1,
            "season_2_amount": s2,
            "season_3_amount": s3,
            "season_4_amount": s4,
            "season_5_amount": s5,
            "season_6_amount": s6,
            "total_dead_cap": total_dead_cap,
            "remaining_seasons": remaining_seasons,
            "is_stretched": is_stretched,
            "prev_record_ptr": f"0x{prev_ptr:X}" if prev_ptr else None,
            "team_ptr": f"0x{team_ptr:X}",
            "provenance": "LIVE_MEMORY_DECODED_V1",
        }

    def import_from_fixtures(self, fixtures_dir: Optional[Path] = None):
        """从二进制切片固件导入并生成 SQLite 样本"""
        fixtures_path = Path(fixtures_dir) if fixtures_dir else DEFAULT_FIXTURES_DIR

        # 1. 导入描述符清单
        desc_json_path = fixtures_path / "sample_descriptors.json"
        if desc_json_path.exists():
            with open(desc_json_path, "r", encoding="utf-8") as f:
                desc_data = json.load(f)
            descriptors = desc_data.get("descriptors", [])
            conn = sqlite3.connect(self.db_path)
            try:
                for d in descriptors:
                    conn.execute("""
                        INSERT OR REPLACE INTO roster_array_descriptors
                        (slot_index, offset_from_manager, offset_from_manager_hex, count, array_pointer,
                         inferred_stride, size_in_heap, object_name, family, getter_rva, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        d["slot_index"], d["offset_from_manager"], d["offset_from_manager_hex"],
                        d["count"], d["pointer_hex"], d["inferred_stride"], d["size_in_heap"],
                        d["object_name"], d["family"], d["getter_rva"], d["status"]
                    ))
                conn.commit()
            finally:
                conn.close()

        # 2. 导入球队信息 (从 sample_teams_30.bin 或描述符基地址计算)
        teams_bin_path = fixtures_path / "sample_teams_30.bin"
        team_base = 0x7FF4E73065F0  # 默认样本基址
        team_rows = []
        if teams_bin_path.exists():
            with open(teams_bin_path, "rb") as f:
                teams_raw = f.read()
            for t_idx in range(30):
                t_slice = teams_raw[t_idx * 4696 : (t_idx + 1) * 4696]
                if len(t_slice) < 4696:
                    break
                t_addr = team_base + t_idx * 4696
                # 球队死钱链表头指针位于 +0xC88
                waived_head = struct.unpack_from("<Q", t_slice, 0xC88)[0]
                # 提取 UTF-16LE 队名与城市
                name = t_slice[0x2B4 : 0x2B4 + 40].decode("utf-16le", errors="ignore").split("\x00")[0].strip()
                city = t_slice[0x2E6 : 0x2E6 + 40].decode("utf-16le", errors="ignore").split("\x00")[0].strip()
                abbrev = t_slice[0x30A : 0x30A + 10].decode("utf-16le", errors="ignore").split("\x00")[0].strip()

                team_rows.append((
                    t_idx, city, name, abbrev, f"0x{t_addr:X}",
                    f"0x{waived_head:X}" if waived_head else None
                ))

            conn = sqlite3.connect(self.db_path)
            try:
                conn.executemany("""
                    INSERT OR REPLACE INTO teams
                    (team_index, city, name, abbreviation, team_pointer, waived_salary_head_ptr)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, team_rows)
                conn.commit()
            finally:
                conn.close()

        # 3. 导入死钱记录 (sample_waived_salary.bin)
        ws_bin_path = fixtures_path / "sample_waived_salary.bin"
        if ws_bin_path.exists():
            with open(ws_bin_path, "rb") as f:
                ws_raw = f.read()
            total_records = len(ws_raw) // 136
            ws_rows = []
            for slot in range(total_records):
                raw_item = ws_raw[slot * 136 : (slot + 1) * 136]
                decoded = self.decode_waived_salary(raw_item, slot, team_base=team_base)
                if decoded is not None:
                    ws_rows.append((
                        decoded["slot_index"], decoded["team_index"], decoded["player_id"],
                        decoded["first_name"], decoded["last_name"], decoded["full_name"],
                        decoded["season_1_amount"], decoded["season_2_amount"], decoded["season_3_amount"],
                        decoded["season_4_amount"], decoded["season_5_amount"], decoded["season_6_amount"],
                        decoded["total_dead_cap"], decoded["remaining_seasons"], decoded["is_stretched"],
                        decoded["prev_record_ptr"], decoded["team_ptr"], decoded["provenance"]
                    ))

            conn = sqlite3.connect(self.db_path)
            try:
                conn.executemany("""
                    INSERT OR REPLACE INTO waived_salaries
                    (slot_index, team_index, player_id, first_name, last_name, full_name,
                     season_1_amount, season_2_amount, season_3_amount, season_4_amount,
                     season_5_amount, season_6_amount, total_dead_cap, remaining_seasons,
                     is_stretched, prev_record_ptr, team_ptr, provenance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, ws_rows)
                conn.commit()
            finally:
                conn.close()


def build_sample_database(db_path: Path, fixtures_dir: Optional[Path] = None) -> Path:
    """便捷工厂函数：创建并初始化独立样本库"""
    exporter = NativeSqliteExporter(db_path)
    exporter.import_from_fixtures(fixtures_dir)
    return db_path


if __name__ == "__main__":
    target_db = Path(__file__).parent / "native_sample.db"
    build_sample_database(target_db)
    print(f"成功在 {target_db} 构建独立 SQLite 样本库。")
