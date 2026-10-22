# -*- coding: utf-8 -*-
"""
AG-NATIVE-01C 自动化测试套件

涵盖：
1. 6 项异常步长原生汇编验证与堆对齐公式自洽性；
2. 历史纪录大全 (Slot 39, NBA_RECORD_BOOK) 52 字节解码与 1920 纪元日期公式；
3. 代表性历史球星纪录精确单点校验 (Wilt 100分、Kobe 81分、Klay 14记三分、Kareem 38,387分)；
4. 赛程日历 (Slot 44, SCHEDULE_CALENDAR) 24 字节解码、主客场关系与未赛哨兵值；
5. 原生官方姓名与文字字典 (Slot 31 & 32, NAME_DICTIONARY) UTF-16LE 提取；
6. 独立多对象 SQLite 样本库生成、外键完整性与 SQL 跨表查询；
7. WAIVED_SALARY 推断字段的启发式归类。
"""

import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path
import pytest

REPO_ROOT = str(Path(__file__).resolve().parents[4])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from research.native_access.AG_NATIVE_01C.decoders.record_book_decoder import (
    decode_record_book_entry,
)
from research.native_access.AG_NATIVE_01C.decoders.schedule_decoder import (
    decode_schedule_game,
)
from research.native_access.AG_NATIVE_01C.export_sample_sqlite import (
    NativeSqliteExporter01C,
    build_sample_database_01c,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def fixtures_c():
    catalog_path = Path(__file__).parent.parent / "object_catalog.json"
    rb_path = FIXTURES_DIR / "sample_record_book_500.bin"
    sched_path = FIXTURES_DIR / "sample_schedule_100.bin"
    fn_path = FIXTURES_DIR / "sample_first_names_100.bin"
    ln_path = FIXTURES_DIR / "sample_last_names_100.bin"
    teams_json_path = FIXTURES_DIR / "sample_teams_catalog.json"

    assert catalog_path.exists()
    assert rb_path.exists()
    assert sched_path.exists()
    assert fn_path.exists()
    assert ln_path.exists()
    assert teams_json_path.exists()

    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    with open(rb_path, "rb") as f:
        rb_bin = f.read()
    with open(sched_path, "rb") as f:
        sched_bin = f.read()
    with open(fn_path, "rb") as f:
        fn_bin = f.read()
    with open(ln_path, "rb") as f:
        ln_bin = f.read()
    with open(teams_json_path, "r", encoding="utf-8") as f:
        teams = json.load(f)

    return {
        "catalog": catalog,
        "rb_bin": rb_bin,
        "sched_bin": sched_bin,
        "fn_bin": fn_bin,
        "ln_bin": ln_bin,
        "teams": teams,
    }


def test_abnormal_strides_verified_by_native_code(fixtures_c):
    """测试 1: 验证 6 项前次有疑问的步长已被原生汇编完全解决并符合对齐公式"""
    descriptors = {d["slot_index"]: d for d in fixtures_c["catalog"]["descriptors"]}

    # Slot 9: Stride 60, Padding 4
    d9 = descriptors[9]
    assert d9["true_stride"] == 60
    assert d9["stride_status"] == "STRIDE_VERIFIED_BY_NATIVE_CODE"
    assert d9["count"] * d9["true_stride"] + d9["alignment_padding_bytes"] == d9["size_in_heap"]

    # Slot 21: Stride 12, Padding 2
    d21 = descriptors[21]
    assert d21["true_stride"] == 12
    assert d21["stride_status"] == "STRIDE_VERIFIED_BY_NATIVE_CODE"
    assert d21["count"] * d21["true_stride"] + d21["alignment_padding_bytes"] == d21["size_in_heap"]

    # Slot 41: Stride 152, Padding 4
    d41 = descriptors[41]
    assert d41["true_stride"] == 152
    assert d41["stride_status"] == "STRIDE_VERIFIED_BY_NATIVE_CODE"
    assert d41["count"] * d41["true_stride"] + d41["alignment_padding_bytes"] == d41["size_in_heap"]

    # Slot 46: Stride 216, Padding 4
    d46 = descriptors[46]
    assert d46["true_stride"] == 216
    assert d46["stride_status"] == "STRIDE_VERIFIED_BY_NATIVE_CODE"
    assert d46["count"] * d46["true_stride"] + d46["alignment_padding_bytes"] == d46["size_in_heap"]

    # Slot 54: Stride 64, Padding 4
    d54 = descriptors[54]
    assert d54["true_stride"] == 64
    assert d54["stride_status"] == "STRIDE_VERIFIED_BY_NATIVE_CODE"
    assert d54["count"] * d54["true_stride"] + d54["alignment_padding_bytes"] == d54["size_in_heap"]

    # Slot 74: Stride 2
    d74 = descriptors[74]
    assert d74["true_stride"] == 2
    assert d74["stride_status"] == "STRIDE_VERIFIED_BY_NATIVE_CODE"


def test_record_book_decoding_and_date_formula(fixtures_c):
    """测试 2: 验证历史纪录大全解码及 1920 纪元压缩日期算法"""
    rb_bin = fixtures_c["rb_bin"]

    # Record 0: Wilt Chamberlain 100分 (1962-03-02)
    rec0 = decode_record_book_entry(rb_bin[0:52], index=0)
    assert rec0["full_name"] == "Wilt Chamberlain"
    assert rec0["stat_value"] == 100.0
    assert rec0["game_date"] == "1962-03-02"
    assert rec0["category_label"] == "SINGLE_GAME_POINTS"

    # Record 1: Kobe Bryant 81分 (2006-01-22)
    rec1 = decode_record_book_entry(rb_bin[52:104], index=1)
    assert rec1["full_name"] == "Kobe Bryant"
    assert rec1["stat_value"] == 81.0
    assert rec1["game_date"] == "2006-01-22"
    assert rec1["category_label"] == "SINGLE_GAME_POINTS"

    # Record 10: Klay Thompson 14记三分 (2018-10-29)
    rec10 = decode_record_book_entry(rb_bin[10 * 52 : 11 * 52], index=10)
    assert rec10["full_name"] == "Klay Thompson"
    assert rec10["stat_value"] == 14.0
    assert rec10["game_date"] == "2018-10-29"
    assert rec10["category_label"] == "SINGLE_GAME_3PM"
    assert rec10["player_id"] == 2338

    # Record 340: Kareem Abdul-Jabbar 生涯总得分 (38,387分)
    rec340 = decode_record_book_entry(rb_bin[340 * 52 : 341 * 52], index=340)
    assert rec340["full_name"] == "Kareem Abdul-Jabbar"
    assert rec340["stat_value"] == 38387.0
    assert rec340["category_label"] == "CAREER_TOTAL_POINTS"


def test_schedule_calendar_decoding(fixtures_c):
    """测试 3: 验证赛程日历解码、对阵双方与胜负状态哨兵"""
    sched_bin = fixtures_c["sched_bin"]
    team_base = 0x7FF4E73065F0
    team_names = {t["team_index"]: t["name"] for t in fixtures_c["teams"]}

    # Game 0: Hawks vs Nets (已赛，主胜)
    g0 = decode_schedule_game(sched_bin[0:24], game_index=0, team_base=team_base, team_names=team_names)
    assert g0["home_team_name"] == "Hawks"
    assert g0["away_team_name"] == "Nets"
    assert g0["status_code"] == 1
    assert g0["status_label"] == "HOME_WIN"
    assert g0["is_played"] is True

    # Game 2: Hawks vs Hornets (已赛，客胜)
    g2 = decode_schedule_game(sched_bin[48:72], game_index=2, team_base=team_base, team_names=team_names)
    assert g2["home_team_name"] == "Hawks"
    assert g2["away_team_name"] == "Hornets"
    assert g2["status_code"] == 0
    assert g2["status_label"] == "AWAY_WIN"
    assert g2["is_played"] is True

    # Game 4: Hawks vs Cavaliers (未赛，哨兵 65535)
    g4 = decode_schedule_game(sched_bin[96:120], game_index=4, team_base=team_base, team_names=team_names)
    assert g4["home_team_name"] == "Hawks"
    assert g4["away_team_name"] == "Cavaliers"
    assert g4["status_code"] == 65535
    assert g4["status_label"] == "UNPLAYED"
    assert g4["is_played"] is False


def test_name_dictionaries_decoding(fixtures_c):
    """测试 4: 验证原生姓名与文字字典提取 (Slot 31 & Slot 32)"""
    fn_bin = fixtures_c["fn_bin"]
    ln_bin = fixtures_c["ln_bin"]

    # 第一名字典验证
    name_0 = fn_bin[0:48].decode("utf-16le", errors="ignore").split("\x00")[0]
    name_1 = fn_bin[48:96].decode("utf-16le", errors="ignore").split("\x00")[0]
    assert name_0 == "Adrian"
    assert name_1 == "Alex"

    # 姓氏字典验证
    last_0 = ln_bin[0:48].decode("utf-16le", errors="ignore").split("\x00")[0]
    last_1 = ln_bin[48:96].decode("utf-16le", errors="ignore").split("\x00")[0]
    assert last_0 == "Abass"
    assert last_1 == "Abdenour"


def test_sqlite_sample_01c_database_integrity():
    """测试 5: 验证 SQLite 独立多对象样本库建表、外键与跨表查询"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = Path(tmpdir) / "test_sample_01c.db"
        build_sample_database_01c(test_db)
        assert test_db.exists()

        conn = sqlite3.connect(test_db)
        try:
            cur = conn.cursor()

            # 验证各表数据量
            cur.execute("SELECT count(*) FROM teams")
            assert cur.fetchone()[0] == 219

            cur.execute("SELECT count(*) FROM nba_record_book")
            assert cur.fetchone()[0] == 500

            cur.execute("SELECT count(*) FROM schedule_games")
            assert cur.fetchone()[0] == 100

            cur.execute("SELECT count(*) FROM name_dictionary")
            assert cur.fetchone()[0] == 200

            # 验证外键约束健全：查询赛程且关联队伍信息
            cur.execute("""
                SELECT s.game_index, ht.name, at.name, s.status_label
                FROM schedule_games s
                JOIN teams ht ON s.home_team_index = ht.team_index
                JOIN teams at ON s.away_team_index = at.team_index
                WHERE s.game_index = 0
            """)
            g_idx, h_name, a_name, status = cur.fetchone()
            assert g_idx == 0
            assert h_name == "Hawks"
            assert a_name == "Nets"
            assert status == "HOME_WIN"

            # 验证历史纪录单场最高分查询
            cur.execute("""
                SELECT full_name, stat_value, game_date
                FROM nba_record_book
                WHERE category_label = 'SINGLE_GAME_POINTS'
                ORDER BY stat_value DESC
                LIMIT 1
            """)
            p_name, p_val, p_date = cur.fetchone()
            assert p_name == "Wilt Chamberlain"
            assert p_val == 100.0
            assert p_date == "1962-03-02"
        finally:
            conn.close()


def test_waived_salary_heuristic_classification():
    """测试 6: 验证死钱延伸条款标记在代码与数据库中均声明为启发式推断"""
    db_path = Path(__file__).parent.parent / "native_sample_01c.db"
    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        # 检查字段名必须包含 heuristic
        cur.execute("PRAGMA table_info(waived_salaries);")
        col_names = [col[1] for col in cur.fetchall()]
        assert "is_stretched_heuristic" in col_names
        assert "is_stretched" not in col_names  # 原生未证实位域已更正为启发式
    finally:
        conn.close()
