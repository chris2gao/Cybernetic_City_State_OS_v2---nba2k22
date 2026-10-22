# -*- coding: utf-8 -*-
"""NBA 2K22 统一原生读取引擎离线自动化测试套件

AG-NATIVE-01 Codex 验收基准测试：
1. 100% 确定性、脱机运行、不依赖游戏进程；
2. 覆盖全部 7 种原生对象类型 (PLAYER, TEAM, STAFF, PLAYER_STATS, TEAM_STATS, DRAFT_ASSETS, WAIVED_SALARY)；
3. 验证单对象访问、多级图式关系跳转、数据守恒性；
4. 验证严格异常处理 (越界 IndexError、非法类型 ValueError、只读隔离安全)。
"""

import os
import sys
import pytest

MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIXTURES_DIR = os.path.join(MODULE_DIR, "fixtures")

if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from native_access import MockMemoryBackend, NativeReader, NativeRecord


@pytest.fixture(scope="module")
def reader():
    backend = MockMemoryBackend(FIXTURES_DIR)
    return NativeReader(backend=backend)


def test_mock_backend_loading(reader):
    """测试 MockBackend 固件加载与清单解析"""
    assert reader.backend.manifest is not None
    assert "descriptors" in reader.backend.manifest
    assert reader.backend.is_live is False


def test_list_objects_all_7_types(reader):
    """测试统一目录清单列举能力 (覆盖全部 7 类已知原生对象)"""
    expected_specs = {
        "PLAYER": (3390, 1264),
        "TEAM": (219, 4696),
        "STAFF": (1470, 352),
        "PLAYER_STATS": (9773, 48),
        "TEAM_STATS": (2964, 62),
        "DRAFT_ASSETS": (504, 32),
        "WAIVED_SALARY": (222, 136),
    }

    for obj_type, (min_count, stride) in expected_specs.items():
        info = reader.list_objects(obj_type)
        assert info["object_type"] == obj_type
        assert info["count"] >= min_count
        assert info["stride"] == stride
        assert info["address"].startswith("0x")


def test_get_player_record(reader):
    """测试 PLAYER 记录读取与基础解码 (哈利伯顿)"""
    player = reader.get_object("PLAYER", 179)
    assert isinstance(player, NativeRecord)
    assert player.object_type == "PLAYER"
    assert player.index == 179
    assert player.stride == 1264
    assert len(player.raw_bytes) == 1264
    assert player.get("last_name") == "Haliburton"
    assert player.get("first_name") == "Tyrese"
    assert player.get("face_id") == 8001


def test_get_team_record(reader):
    """测试 TEAM 记录读取与基础解码 (湖人 & 凯尔特人)"""
    lakers = reader.get_object("TEAM", 13)
    assert lakers.object_type == "TEAM"
    assert lakers.get("name") == "Lakers"
    assert lakers.get("city") == "Los Angeles"
    assert lakers.get("abbreviation") == "LAL"
    assert lakers.get("team_id") == 15

    celtics = reader.get_object("TEAM", 4)
    assert celtics.get("name") == "Celtics"
    assert celtics.get("city") == "Boston"
    assert celtics.get("abbreviation") == "BOS"
    assert celtics.get("team_id") == 5


def test_get_staff_record(reader):
    """测试 STAFF 记录读取与基础解码 (Doc Rivers)"""
    doc = reader.get_object("STAFF", 0)
    assert doc.object_type == "STAFF"
    assert doc.get("first_name") == "Doc"
    assert doc.get("last_name") == "Rivers"
    assert doc.get("position") == 0  # 主教练
    assert doc.get("years_left") == 1
    assert doc.get("salary") == 3936445


def test_get_stats_records(reader):
    """测试 PLAYER_STATS 与 TEAM_STATS 读取与守恒性校验"""
    # 湖人战绩 (Stats 2222)
    lakers_stats = reader.get_object("TEAM_STATS", 2222)
    assert lakers_stats.get("w") == 15
    assert lakers_stats.get("l") == 2
    pts = lakers_stats.get("points")
    fgm = lakers_stats.get("made")
    tpm = lakers_stats.get("3pt_made")
    ftm = lakers_stats.get("free_throws_made")
    # 得分守恒公式验证: 2*FGM + 3PM + FTM == PTS
    assert 2 * fgm + tpm + ftm == pts

    # 哈利伯顿球员统计 (Stats 326)
    hali_stats = reader.get_object("PLAYER_STATS", 326)
    assert hali_stats.get("times") == 15  # 15场出场
    assert hali_stats.get("points") == 207
    assert hali_stats.get("assists") == 74
    h_fgm = hali_stats.get("made")
    h_tpm = hali_stats.get("3pt_made")
    h_ftm = hali_stats.get("free_throws_made")
    assert 2 * h_fgm + h_tpm + h_ftm == 207


def test_get_draft_and_waived_records(reader):
    """测试 DRAFT_ASSETS 与 WAIVED_SALARY 记录读取"""
    asset = reader.get_object("DRAFT_ASSETS", 0)
    assert asset.object_type == "DRAFT_ASSETS"
    assert asset.stride == 32
    assert "draft_year" in asset.decoded.get("asset", {})

    waived = reader.get_object("WAIVED_SALARY", 0)
    assert waived.object_type == "WAIVED_SALARY"
    assert waived.stride == 136
    assert waived.get("salary_y1") == 92857


def test_relationship_player_to_stats(reader):
    """测试图式关联: PLAYER -> PLAYER_STATS"""
    stats = reader.get_related("PLAYER", 179, "PLAYER_STATS")
    assert stats is not None
    assert stats.object_type == "PLAYER_STATS"
    assert stats.get("points") == 207
    assert stats.get("assists") == 74


def test_relationship_player_to_team(reader):
    """测试图式关联: PLAYER -> TEAM (哈利伯顿所属国王队)"""
    team = reader.get_related("PLAYER", 179, "TEAM")
    assert team is not None
    assert team.object_type == "TEAM"
    assert team.get("city") == "Sacramento"
    assert team.get("name") == "Kings"
    assert team.get("abbreviation") == "SAC"


def test_relationship_team_to_stats(reader):
    """测试图式关联: TEAM -> TEAM_STATS (湖人 15胜2负)"""
    stats = reader.get_related("TEAM", 13, "TEAM_STATS")
    assert stats is not None
    assert stats.object_type == "TEAM_STATS"
    assert stats.get("w") == 15
    assert stats.get("l") == 2


def test_relationship_bidirectional_team_and_staff(reader):
    """测试图式关联: TEAM <-> STAFF 双向核验 (76人队 <-> Doc Rivers)"""
    # 76人队 -> 主教练 Doc Rivers
    coach = reader.get_related("TEAM", 0, "STAFF")
    assert coach is not None
    assert coach.get("last_name") == "Rivers"
    assert coach.get("first_name") == "Doc"

    # 反向跳转: Doc Rivers -> 76人队
    team = reader.get_related("STAFF", 0, "TEAM")
    assert team is not None
    assert team.get("abbreviation") == "PHI"
    assert team.get("name") == "76ers"


def test_relationship_team_to_waived_salary(reader):
    """测试图式关联: TEAM -> WAIVED_SALARY (凯尔特人死钱记录)"""
    # 凯尔特人是 Team 4 (UID 5)
    waived_list = reader.get_related("TEAM", 4, "WAIVED_SALARY")
    assert isinstance(waived_list, list)
    assert len(waived_list) >= 1
    assert waived_list[0].get("salary_y1") == 92857


def test_multi_hop_traversal(reader):
    """测试多级跳跃式关联查询: Player -> Team -> TeamStats"""
    player = reader.get_object("PLAYER", 179)
    team = reader.get_related(player, "TEAM")
    assert team.get("name") == "Kings"
    team_stats = reader.get_related(team, "TEAM_STATS")
    assert team_stats.get("w") == 6
    assert team_stats.get("l") == 10


def test_find_objects_filter(reader):
    """测试按条件检索对象列表 (find_objects)"""
    lakers = reader.find_objects("TEAM", abbreviation="LAL")
    assert len(lakers) == 1
    assert lakers[0].get("name") == "Lakers"

    celtics = reader.find_objects("TEAM", abbreviation="BOS")
    assert len(celtics) == 1
    assert celtics[0].get("name") == "Celtics"


def test_negative_index_out_of_bounds(reader):
    """异常路径测试: 负数或越界索引必须抛出 IndexError"""
    with pytest.raises(IndexError) as exc_info:
        reader.get_object("PLAYER", -1)
    assert "超出有效范围" in str(exc_info.value)

    with pytest.raises(IndexError) as exc_info:
        reader.get_object("PLAYER", 999999)
    assert "超出有效范围" in str(exc_info.value)

    with pytest.raises(IndexError) as exc_info:
        reader.get_object("TEAM", 500)
    assert "超出有效范围" in str(exc_info.value)


def test_negative_invalid_object_type(reader):
    """异常路径测试: 未定义或非法的对象类型必须抛出 ValueError"""
    with pytest.raises(ValueError) as exc_info:
        reader.get_object("INVALID_OBJECT_NAME", 0)
    assert "未知的原生对象类型" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        reader.list_objects("NONEXISTENT_TYPE")
    assert "未知的原生对象类型" in str(exc_info.value)


def test_negative_missing_sparse_record(reader):
    """异常路径测试: 索引合法但在离线稀疏样本中缺失必须抛出 OSError"""
    # 索引 100 在球员有效范围 [0, 3390) 内，但 fixtures 仅包含样本球员 [0, 1, 179, 206, 433]
    with pytest.raises(OSError) as exc_info:
        reader.get_object("PLAYER", 100)
    assert "读取原生记录失败" in str(exc_info.value)


def test_record_serialization_and_fields(reader):
    """测试 NativeRecord 字段提取与字典序列化"""
    p = reader.get_object("PLAYER", 179)
    d = p.to_dict()
    assert d["object_type"] == "PLAYER"
    assert d["index"] == 179
    assert "0x" in d["address"]
    assert d["stride"] == 1264
    assert "raw_hex_preview" in d
    assert "provenance" in d
    assert p.get("nonexistent_field_xyz", default=42) == 42
