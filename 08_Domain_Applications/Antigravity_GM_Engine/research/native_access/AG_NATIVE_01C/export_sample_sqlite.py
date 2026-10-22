# -*- coding: utf-8 -*-
"""
AG-NATIVE-01C 独立 SQLite 样本库生成与多对象转换引擎

涵盖：
1. NBA 历史纪录大全 (Slot 39, nba_record_book)
2. 完整赛程与对阵结果 (Slot 44, schedule_games)
3. 原生官方姓名与文字字典 (Slot 31 & 32, name_dictionary)
4. 修订版裁员死钱表 (WAIVED_SALARY, 消除硬编码并明确 is_stretched_heuristic)
"""

import os
import sys
import sqlite3
import struct
from pathlib import Path
from typing import Optional, Dict, Any, List

REPO_ROOT = str(Path(__file__).resolve().parents[3])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from research.native_access.AG_NATIVE_01C.decoders.record_book_decoder import (
    decode_record_book_entry,
)
from research.native_access.AG_NATIVE_01C.decoders.schedule_decoder import (
    decode_schedule_game,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEAMS_FIXTURE_PATH = Path(__file__).parent.parent / "AG_NATIVE_01B" / "fixtures" / "sample_teams_30.bin"
WS_FIXTURE_PATH = Path(__file__).parent.parent / "AG_NATIVE_01B" / "fixtures" / "sample_waived_salary.bin"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teams (
    team_index INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT,
    abbreviation TEXT,
    team_pointer TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS nba_record_book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_index INTEGER NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    stat_value REAL NOT NULL,
    game_date TEXT,
    category_code INTEGER NOT NULL,
    category_label TEXT NOT NULL,
    player_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS schedule_games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_index INTEGER NOT NULL UNIQUE,
    home_team_index INTEGER,
    away_team_index INTEGER,
    home_team_name TEXT NOT NULL,
    away_team_name TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    status_label TEXT NOT NULL,
    is_played INTEGER NOT NULL,
    game_day_index INTEGER NOT NULL,
    FOREIGN KEY (home_team_index) REFERENCES teams(team_index),
    FOREIGN KEY (away_team_index) REFERENCES teams(team_index)
);

CREATE TABLE IF NOT EXISTS name_dictionary (
    dict_type TEXT NOT NULL,
    name_id INTEGER NOT NULL,
    text_value TEXT NOT NULL,
    PRIMARY KEY (dict_type, name_id)
);

CREATE TABLE IF NOT EXISTS waived_salaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_index INTEGER NOT NULL UNIQUE,
    team_index INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    season_1_amount INTEGER NOT NULL,
    season_2_amount INTEGER NOT NULL,
    season_3_amount INTEGER NOT NULL,
    total_dead_cap INTEGER NOT NULL,
    remaining_seasons INTEGER NOT NULL,
    is_stretched_heuristic INTEGER NOT NULL,
    team_ptr TEXT NOT NULL,
    provenance TEXT NOT NULL,
    FOREIGN KEY (team_index) REFERENCES teams(team_index)
);

CREATE INDEX IF NOT EXISTS idx_record_book_cat ON nba_record_book(category_label);
CREATE INDEX IF NOT EXISTS idx_schedule_played ON schedule_games(is_played);
"""


class NativeSqliteExporter01C:
    """多对象原生结构转独立 SQLite 样本库导出器"""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
        finally:
            conn.close()

    def import_teams_from_catalog(self, catalog_path: Path) -> Dict[int, str]:
        """从 JSON 目录导入全量 219 支球队 (含 30 核心队、历史队与扩张队)"""
        import json
        with open(catalog_path, "r", encoding="utf-8") as f:
            teams = json.load(f)

        team_names = {}
        rows = []
        for t in teams:
            t_idx = t["team_index"]
            team_names[t_idx] = t["name"]
            rows.append((t_idx, t["name"], t.get("city", ""), t.get("abbreviation", ""), t["team_pointer"]))

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.executemany("""
                INSERT OR REPLACE INTO teams (team_index, name, city, abbreviation, team_pointer)
                VALUES (?, ?, ?, ?, ?)
            """, rows)
            conn.commit()
        finally:
            conn.close()
        return team_names

    def import_record_book(self, rb_bin: bytes, limit: int = 500):
        """导入历史纪录大全"""
        count = min(limit, len(rb_bin) // 52)
        rows = []
        for i in range(count):
            raw = rb_bin[i * 52 : (i + 1) * 52]
            entry = decode_record_book_entry(raw, index=i)
            if entry:
                rows.append((
                    entry["index"], entry["full_name"], entry["first_name"], entry["last_name"],
                    entry["stat_value"], entry["game_date"], entry["category_code"],
                    entry["category_label"], entry["player_id"]
                ))

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.executemany("""
                INSERT OR REPLACE INTO nba_record_book
                (record_index, full_name, first_name, last_name, stat_value, game_date,
                 category_code, category_label, player_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
            conn.commit()
        finally:
            conn.close()

    def import_schedule(self, sched_bin: bytes, team_base: int, team_names: Dict[int, str]):
        """导入赛程日历"""
        count = len(sched_bin) // 24
        rows = []
        for i in range(count):
            raw = sched_bin[i * 24 : (i + 1) * 24]
            game = decode_schedule_game(raw, game_index=i, team_base=team_base, team_names=team_names)
            if game:
                rows.append((
                    game["game_index"], game["home_team_index"], game["away_team_index"],
                    game["home_team_name"], game["away_team_name"], game["status_code"],
                    game["status_label"], int(game["is_played"]), game["game_day_index"]
                ))

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.executemany("""
                INSERT OR REPLACE INTO schedule_games
                (game_index, home_team_index, away_team_index, home_team_name, away_team_name,
                 status_code, status_label, is_played, game_day_index)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
            conn.commit()
        finally:
            conn.close()

    def import_dictionaries(self, fn_bin: bytes, ln_bin: bytes):
        """导入官方姓名字典"""
        rows = []
        for i in range(len(fn_bin) // 48):
            name = fn_bin[i * 48 : (i + 1) * 48].decode("utf-16le", errors="ignore").split("\x00")[0].strip()
            if name:
                rows.append(("FIRST_NAME", i, name))

        for i in range(len(ln_bin) // 48):
            name = ln_bin[i * 48 : (i + 1) * 48].decode("utf-16le", errors="ignore").split("\x00")[0].strip()
            if name:
                rows.append(("LAST_NAME", i, name))

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.executemany("""
                INSERT OR REPLACE INTO name_dictionary (dict_type, name_id, text_value)
                VALUES (?, ?, ?)
            """, rows)
            conn.commit()
        finally:
            conn.close()

    def import_waived_salaries_refined(self, ws_bin: bytes, team_base: int):
        """导入死钱明细 (已修正: 动态指针计算、明确 is_stretched_heuristic)"""
        count = len(ws_bin) // 136
        rows = []
        for slot in range(count):
            raw = ws_bin[slot * 136 : (slot + 1) * 136]
            team_ptr = struct.unpack_from("<Q", raw, 0x08)[0]
            if team_ptr == 0:
                continue

            # 校验球队指针步长对齐与有效范围
            if team_base > 0 and team_ptr >= team_base:
                offset_delta = team_ptr - team_base
                if offset_delta % 4696 == 0:
                    team_idx = offset_delta // 4696
                else:
                    team_idx = -1
            else:
                team_idx = -1

            if not (0 <= team_idx < 30):
                continue  # 跳过非 30 支核心 NBA 球队的特殊死钱

            s1, s2, s3, s4, s5, s6 = struct.unpack_from("<IIIIII", raw, 0x10)
            player_id = struct.unpack_from("<H", raw, 0x34)[0]

            last_name_raw = raw[0x38:0x60].split(b"\x00\x00\x00")[0]
            if len(last_name_raw) % 2 != 0:
                last_name_raw += b"\x00"
            last_name = last_name_raw.decode("utf-16le", errors="ignore").rstrip("\x00").strip()

            first_name_raw = raw[0x60:0x80].split(b"\x00\x00\x00")[0]
            if len(first_name_raw) % 2 != 0:
                first_name_raw += b"\x00"
            first_name = first_name_raw.decode("utf-16le", errors="ignore").rstrip("\x00").strip()
            full_name = f"{first_name} {last_name}".strip()

            amounts = [s1, s2, s3, s4, s5, s6]
            total_dead_cap = sum(amounts)
            remaining_seasons = sum(1 for a in amounts if a > 0)
            # 明确为推断启发式标记，非原生位域
            is_stretched_heuristic = 1 if remaining_seasons >= 3 else 0

            rows.append((
                slot, team_idx, player_id, full_name, s1, s2, s3,
                total_dead_cap, remaining_seasons, is_stretched_heuristic,
                f"0x{team_ptr:X}", "LIVE_MEMORY_OR_FIXTURE_REFINED"
            ))

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.executemany("""
                INSERT OR REPLACE INTO waived_salaries
                (slot_index, team_index, player_id, full_name, season_1_amount,
                 season_2_amount, season_3_amount, total_dead_cap, remaining_seasons,
                 is_stretched_heuristic, team_ptr, provenance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
            conn.commit()
        finally:
            conn.close()


def build_sample_database_01c(db_path: Path) -> Path:
    """构建完整的 AG-NATIVE-01C 样本库"""
    exporter = NativeSqliteExporter01C(db_path)
    team_base = 0x7FF4E73065F0

    # 1. 球队全量目录 (219 队)
    teams_catalog_path = FIXTURES_DIR / "sample_teams_catalog.json"
    if teams_catalog_path.exists():
        team_names = exporter.import_teams_from_catalog(teams_catalog_path)
    else:
        team_names = {}

    # 2. 纪录大全
    rb_path = FIXTURES_DIR / "sample_record_book_500.bin"
    if rb_path.exists():
        with open(rb_path, "rb") as f:
            exporter.import_record_book(f.read())

    # 3. 赛程日历
    sched_path = FIXTURES_DIR / "sample_schedule_100.bin"
    if sched_path.exists():
        with open(sched_path, "rb") as f:
            exporter.import_schedule(f.read(), team_base, team_names)

    # 4. 字典
    fn_path = FIXTURES_DIR / "sample_first_names_100.bin"
    ln_path = FIXTURES_DIR / "sample_last_names_100.bin"
    if fn_path.exists() and ln_path.exists():
        with open(fn_path, "rb") as f1, open(ln_path, "rb") as f2:
            exporter.import_dictionaries(f1.read(), f2.read())

    # 5. 死钱
    if WS_FIXTURE_PATH.exists():
        with open(WS_FIXTURE_PATH, "rb") as f:
            exporter.import_waived_salaries_refined(f.read(), team_base)

    return db_path


if __name__ == "__main__":
    out_db = Path(__file__).parent / "native_sample_01c.db"
    build_sample_database_01c(out_db)
    print(f"成功构建 AG-NATIVE-01C 独立样本库: {out_db}")
