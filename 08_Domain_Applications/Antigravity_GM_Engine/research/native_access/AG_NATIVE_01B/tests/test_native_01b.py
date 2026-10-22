# -*- coding: utf-8 -*-
"""
AG-NATIVE-01B 离线自动化测试套件

涵盖：
1. ROSTERDATA 描述符表（75槽位、67活跃、8预留）与堆连续不变性校验；
2. 原生 C++ Getter RVA 映射一致性；
3. WAIVED_SALARY 136 字节高保真二进制解码与 UTF-16 字符串提取；
4. 代表性实机真实样本数据校验（Luol Deng, Blake Griffin, Batum, Sanders）；
5. 球队链表遍历与双向指针对照；
6. 独立 SQLite 样本库生成、外键约束与 SQL 聚合查询；
7. 异常与边界输入安全防护。
"""

import os
import sys
import json
import sqlite3
import struct
import tempfile
from pathlib import Path
import pytest

MODULE_DIR = str(Path(__file__).parent.parent)
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from export_to_sqlite import (
    NativeSqliteExporter,
    build_sample_database,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def fixtures_data():
    """加载二进制与 JSON 固件"""
    desc_json_path = FIXTURES_DIR / "sample_descriptors.json"
    ws_bin_path = FIXTURES_DIR / "sample_waived_salary.bin"
    teams_bin_path = FIXTURES_DIR / "sample_teams_30.bin"

    assert desc_json_path.exists(), "缺少 sample_descriptors.json 固件"
    assert ws_bin_path.exists(), "缺少 sample_waived_salary.bin 固件"
    assert teams_bin_path.exists(), "缺少 sample_teams_30.bin 固件"

    with open(desc_json_path, "r", encoding="utf-8") as f:
        desc_catalog = json.load(f)

    with open(ws_bin_path, "rb") as f:
        ws_bytes = f.read()

    with open(teams_bin_path, "rb") as f:
        teams_bytes = f.read()

    return {
        "catalog": desc_catalog,
        "ws_bytes": ws_bytes,
        "teams_bytes": teams_bytes,
    }


def test_roster_descriptor_table_slots_and_counts(fixtures_data):
    """测试 1: 验证描述符目录槽位总数 (75)、活跃数 (67) 与空槽数 (8)"""
    catalog = fixtures_data["catalog"]
    assert catalog["total_slots"] == 75
    assert catalog["active_descriptors_count"] == 67
    assert catalog["empty_slots_count"] == 8

    descriptors = catalog["descriptors"]
    assert len(descriptors) == 75

    # 验证核心对象的槽位与步长
    by_name = {d["object_name"]: d for d in descriptors}
    assert by_name["PLAYER"]["slot_index"] == 1
    assert by_name["PLAYER"]["inferred_stride"] == 1264
    assert by_name["PLAYER"]["count"] == 3390

    assert by_name["TEAM"]["slot_index"] == 8
    assert by_name["TEAM"]["inferred_stride"] == 4696
    assert by_name["TEAM"]["count"] == 219

    assert by_name["STAFF"]["slot_index"] == 19
    assert by_name["STAFF"]["inferred_stride"] == 352
    assert by_name["STAFF"]["count"] == 1470

    assert by_name["PLAYER_STATS"]["slot_index"] == 24
    assert by_name["PLAYER_STATS"]["inferred_stride"] == 48

    assert by_name["TEAM_STATS"]["slot_index"] == 28
    assert by_name["TEAM_STATS"]["inferred_stride"] == 62

    assert by_name["DRAFT_ASSETS"]["slot_index"] == 42
    assert by_name["DRAFT_ASSETS"]["inferred_stride"] == 32
    assert by_name["DRAFT_ASSETS"]["count"] == 504

    assert by_name["WAIVED_SALARY"]["slot_index"] == 61
    assert by_name["WAIVED_SALARY"]["inferred_stride"] == 136
    assert by_name["WAIVED_SALARY"]["count"] == 222


def test_heap_contiguity_invariants(fixtures_data):
    """测试 2: 验证数组在堆区紧凑排列的不变性方程 (消除 EndPointer 误区)"""
    descriptors = fixtures_data["catalog"]["descriptors"]

    # 验证 PLAYER 数组 (Slot 1) 到下一个数组 (Slot 2)
    p_desc = descriptors[1]
    next_desc = descriptors[2]
    p_ptr = int(p_desc["pointer_hex"], 16)
    next_ptr = int(next_desc["pointer_hex"], 16)

    assert p_ptr + p_desc["count"] * p_desc["inferred_stride"] == next_ptr


def test_native_getters_assembly_rva_consistency(fixtures_data):
    """测试 3: 验证反汇编提取的原生 Getter RVA 映射"""
    descriptors = fixtures_data["catalog"]["descriptors"]
    by_slot = {d["slot_index"]: d for d in descriptors}

    assert by_slot[61]["getter_rva"] == "0xF3C790"  # GetWaivedSalaryByIndex
    assert by_slot[19]["getter_rva"] == "0xF3C120"  # GetStaffDataByIndex
    assert by_slot[42]["getter_rva"] == "0xF3C940"  # GetDraftDataByIndex
    assert by_slot[28]["getter_rva"] == "0xF413B0"  # GetTeamStatsByIndex


def test_waived_salary_binary_decoding(fixtures_data):
    """测试 4: 验证 136 字节 WAIVED_SALARY 二进制字段解析"""
    raw = fixtures_data["ws_bytes"][:136]
    decoded = NativeSqliteExporter.decode_waived_salary(raw, slot_index=0, team_base=0x7FF4E73065F0)

    assert decoded is not None
    assert decoded["slot_index"] == 0
    assert decoded["team_index"] == 4  # Celtics
    assert decoded["first_name"] == "Demetrius"
    assert decoded["last_name"] == "Jackson"
    assert decoded["full_name"] == "Demetrius Jackson"
    assert decoded["season_1_amount"] == 92857
    assert decoded["season_2_amount"] == 92857
    assert decoded["season_3_amount"] == 92857
    assert decoded["total_dead_cap"] == 92857 * 3
    assert decoded["is_stretched"] == 1


def test_waived_salary_verified_samples(fixtures_data):
    """测试 5: 验证历史真实代表性死钱样本 (Luol Deng, Blake Griffin, Batum, Sanders)"""
    ws_bytes = fixtures_data["ws_bytes"]
    team_base = 0x7FF4E73065F0

    # 1. 湖人队 Luol Deng (Slot 11)
    deng_raw = ws_bytes[11 * 136 : 12 * 136]
    deng = NativeSqliteExporter.decode_waived_salary(deng_raw, 11, team_base)
    assert deng["full_name"] == "Luol Deng"
    assert deng["team_index"] == 13  # Lakers
    assert deng["season_1_amount"] == 5000000
    assert deng["season_2_amount"] == 0
    assert deng["total_dead_cap"] == 5000000

    # 2. 活塞队 Blake Griffin (Slot 7)
    blake_raw = ws_bytes[7 * 136 : 8 * 136]
    blake = NativeSqliteExporter.decode_waived_salary(blake_raw, 7, team_base)
    assert blake["full_name"] == "Blake Griffin"
    assert blake["team_index"] == 20  # Pistons
    assert blake["season_1_amount"] == 29764126
    assert blake["total_dead_cap"] == 29764126

    # 3. 黄蜂队 Nicolas Batum (Slot 2)
    batum_raw = ws_bytes[2 * 136 : 3 * 136]
    batum = NativeSqliteExporter.decode_waived_salary(batum_raw, 2, team_base)
    assert batum["full_name"] == "Nicolas Batum"
    assert batum["team_index"] == 9  # Hornets
    assert batum["season_1_amount"] == 8856969
    assert batum["season_2_amount"] == 8856969
    assert batum["total_dead_cap"] == 17713938

    # 4. 雄鹿队 Larry Sanders (Slot 13)
    sanders_raw = ws_bytes[13 * 136 : 14 * 136]
    sanders = NativeSqliteExporter.decode_waived_salary(sanders_raw, 13, team_base)
    assert sanders["full_name"] == "Larry Sanders"
    assert sanders["team_index"] == 1  # Bucks
    assert sanders["season_1_amount"] == 1865546


def test_team_linked_list_traversal(fixtures_data):
    """测试 6: 验证 TEAM + 0xC88 侵入式链表遍历与死钱数组双向匹配"""
    teams_raw = fixtures_data["teams_bytes"]
    ws_raw = fixtures_data["ws_bytes"]
    ws_base = 0x7FF4E7C3E180  # 固件基址

    # 检查 Team 4 (Celtics)
    celtics_slice = teams_raw[4 * 4696 : 5 * 4696]
    waived_head = struct.unpack_from("<Q", celtics_slice, 0xC88)[0]
    assert waived_head > 0

    # 计算表头对应的 WaivedSalary slot
    head_slot = (waived_head - ws_base) // 136
    assert head_slot == 1  # Guerschon Yabusele

    # 遍历链表
    visited_slots = []
    curr_ptr = waived_head
    while curr_ptr != 0:
        slot = (curr_ptr - ws_base) // 136
        visited_slots.append(slot)
        curr_rec = ws_raw[slot * 136 : (slot + 1) * 136]
        # +0x00 为链表 prev_record_ptr
        curr_ptr = struct.unpack_from("<Q", curr_rec, 0x00)[0]

    # 凯尔特人死钱链表应依次包含 Slot 1 (Yabusele) -> Slot 0 (Jackson) -> None
    assert visited_slots == [1, 0]


def test_sqlite_sample_database_generation_and_integrity():
    """测试 7: 验证 SQLite 独立样本库构建、表结构及 SQL 聚合统计"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = Path(tmpdir) / "test_sample.db"
        build_sample_database(test_db, fixtures_dir=FIXTURES_DIR)

        assert test_db.exists()

        conn = sqlite3.connect(test_db)
        try:
            cur = conn.cursor()

            # 验证记录总数
            cur.execute("SELECT count(*) FROM roster_array_descriptors")
            assert cur.fetchone()[0] == 75

            cur.execute("SELECT count(*) FROM teams")
            assert cur.fetchone()[0] == 30

            cur.execute("SELECT count(*) FROM waived_salaries")
            assert cur.fetchone()[0] == 32

            # 验证关联查询 Top 1 死钱队伍 (Detroit Pistons 应超过 4000 万美元)
            cur.execute("""
                SELECT t.name, sum(w.season_1_amount)
                FROM teams t
                JOIN waived_salaries w ON t.team_index = w.team_index
                GROUP BY t.team_index
                ORDER BY sum(w.season_1_amount) DESC
                LIMIT 1
            """)
            top_team, top_dead = cur.fetchone()
            assert top_team == "Pistons"
            assert top_dead == 45492507
        finally:
            conn.close()


def test_waived_salary_error_handling():
    """测试 8: 异常输入与边界安全防护"""
    # 1. 步长错误
    with pytest.raises(ValueError, match="步长必须为 136 字节"):
        NativeSqliteExporter.decode_waived_salary(b"\x00" * 100, 0)

    # 2. 全零空记录
    empty_result = NativeSqliteExporter.decode_waived_salary(b"\x00" * 136, 0)
    assert empty_result is None
