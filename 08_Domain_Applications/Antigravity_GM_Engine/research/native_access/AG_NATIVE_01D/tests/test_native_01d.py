# -*- coding: utf-8 -*-
"""
NBA 2K22 原生单场比赛、赛季统计与对决矩阵单元测试套件 (AG-NATIVE-01D)
纯离线运行，100% 依赖真实实机导出的 binary/json fixtures。
"""

import os
import sys
import json
import sqlite3
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "decoders"))
sys.path.insert(0, BASE_DIR)

from boxscore_decoder import BoxScoreDecoder
from season_stats_decoder import SeasonStatsDecoder
from matchup_matrix_decoder import MatchupMatrixDecoder
import export_to_sqlite_01d

FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures")
DB_PATH = os.path.join(BASE_DIR, "native_boxscore_sample.db")


@pytest.fixture(scope="module")
def games_slice_raw():
    path = os.path.join(FIXTURES_DIR, "sample_games_slice.bin")
    with open(path, "rb") as f:
        return f.read()


@pytest.fixture(scope="module")
def statbank_slice_raw():
    path = os.path.join(FIXTURES_DIR, "sample_statbank_slice.bin")
    with open(path, "rb") as f:
        return f.read()


@pytest.fixture(scope="module")
def curry_games_data():
    path = os.path.join(FIXTURES_DIR, "sample_curry_season_games.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def player_career_data():
    path = os.path.join(FIXTURES_DIR, "sample_player_career_slice.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def matchup_slice_raw():
    path = os.path.join(FIXTURES_DIR, "sample_matchup_matrix_slice.bin")
    with open(path, "rb") as f:
        return f.read()


class TestSingleGameBoxScore:
    """单场比赛与 BoxScore 解码测试"""

    def test_decode_game_headers(self, games_slice_raw):
        assert len(games_slice_raw) >= 600
        # 解码 Game 0 (GameId 1: Bucks vs Nets)
        g0 = BoxScoreDecoder.decode_game_header(games_slice_raw[0:60])
        assert g0["game_id"] == 1
        assert g0["home_team_id"] == 1   # Bucks
        assert g0["away_team_id"] == 18  # Nets
        assert g0["home_score"] == 122
        assert g0["away_score"] == 106
        assert g0["winner_team_id"] == 1
        assert g0["point_differential"] == 16
        assert g0["linescore"]["home"]["total"] == 122
        assert g0["linescore"]["away"]["total"] == 106

        # 解码 Game 1 (GameId 2: Lakers vs Warriors)
        g1 = BoxScoreDecoder.decode_game_header(games_slice_raw[60:120])
        assert g1["game_id"] == 2
        assert g1["home_team_id"] == 15  # Lakers
        assert g1["away_team_id"] == 29  # Warriors
        assert g1["home_score"] == 109
        assert g1["away_score"] == 125
        assert g1["winner_team_id"] == 29

    def test_game_scoring_conservation(self, games_slice_raw, statbank_slice_raw):
        """核心物理定律验证：sum(Player.PTS) == Team Final Score"""
        # Game 0: 26 players (13 home + 13 away)
        g0_raw = games_slice_raw[0:60]
        sb0_raw = statbank_slice_raw[0 : 26 * 24]
        full0 = BoxScoreDecoder.decode_full_boxscore(g0_raw, sb0_raw)
        assert full0["conservation"]["home_score_exact"] is True
        assert full0["conservation"]["away_score_exact"] is True
        assert full0["conservation"]["sum_pts_home"] == 122
        assert full0["conservation"]["sum_pts_away"] == 106

        # Game 1: 26 players (13 home + 13 away)
        g1_raw = games_slice_raw[60:120]
        sb1_raw = statbank_slice_raw[26 * 24 : 52 * 24]
        full1 = BoxScoreDecoder.decode_full_boxscore(g1_raw, sb1_raw)
        assert full1["conservation"]["home_score_exact"] is True
        assert full1["conservation"]["away_score_exact"] is True
        assert full1["conservation"]["sum_pts_home"] == 109
        assert full1["conservation"]["sum_pts_away"] == 125

    def test_player_statline_identities(self, statbank_slice_raw):
        """测试单场球员数据数学自洽性与高级数据推导"""
        # 提取 Game 1 中库里 (PID 1612) 的单场表现
        curry_stat = None
        for i in range(26, 52):
            raw_p = statbank_slice_raw[i * 24 : (i + 1) * 24]
            dec = BoxScoreDecoder.decode_player_statline(raw_p, is_home=False)
            if dec["player_id"] == 1612:
                curry_stat = dec
                break

        assert curry_stat is not None
        assert curry_stat["minutes"] == 32
        assert curry_stat["fgm"] == 7
        assert curry_stat["fga"] == 20
        assert curry_stat["tpm"] == 2
        assert curry_stat["ftm"] == 2
        # 得分公式: pts = fgm * 2 + tpm + ftm = 14 + 2 + 2 = 18
        assert curry_stat["points"] == 18
        assert curry_stat["reb"] == 2
        assert curry_stat["ast"] == 6
        assert curry_stat["stl"] == 2
        assert curry_stat["plus_minus"] == 0
        assert curry_stat["is_starter"] is True
        assert curry_stat["game_score"] > 0


class TestSeasonStatsAndSplits:
    """赛季统计汇总与 5 大统计切片测试"""

    def test_season_totals_identity(self, player_career_data):
        """测试 Slot 24 PLAYER_STATS 原生总账守恒: PTS = 2*FGM + 3PM + FTM"""
        for name in ["Curry", "LeBron", "AD"]:
            cur_idx = player_career_data[name]["stats_indices"][0]
            raw_hex = player_career_data[name]["stats_records_hex"][str(cur_idx)]
            st = SeasonStatsDecoder.decode_player_stats_record(bytes.fromhex(raw_hex))
            assert st["scoring_identity_valid"] is True
            assert st["points"] == 2 * st["fgm"] + st["tpm"] + st["ftm"]

    def test_sum_of_games_equals_season_total(self, curry_games_data, player_career_data):
        """
        终极闭环验证：
        单场比赛流水账 (SEASON) 逐场求和 == 赛季汇总表 (ROSTERDATA Slot 24)
        """
        assert len(curry_games_data) == 16
        single_games = []
        for g_entry in curry_games_data:
            g_raw = bytes.fromhex(g_entry["game_raw_hex"])
            g_meta = BoxScoreDecoder.decode_game_header(g_raw)
            p_raw = bytes.fromhex(g_entry["curry_statline_hex"])
            p_data = BoxScoreDecoder.decode_player_statline(p_raw, is_home=(g_meta["home_team_id"] == 29))
            # 记录胜负与日期
            p_data["is_win"] = (g_meta["winner_team_id"] == 29)
            p_data["game_date"] = g_meta["game_date"]
            single_games.append(p_data)

        agg = SeasonStatsDecoder.aggregate_game_splits(single_games)
        tot = agg["total"]

        # 与 Slot 24 原生记录完全比对
        cur_idx = player_career_data["Curry"]["stats_indices"][0]
        curry_slot24 = SeasonStatsDecoder.decode_player_stats_record(
            bytes.fromhex(player_career_data["Curry"]["stats_records_hex"][str(cur_idx)])
        )

        assert tot["games"] == curry_slot24["games_played"] == 16
        assert tot["minutes"] == curry_slot24["minutes"] == 517
        assert tot["points"] == curry_slot24["points"] == 416
        assert tot["fgm"] == curry_slot24["fgm"] == 143
        assert tot["fga"] == curry_slot24["fga"] == 290
        assert tot["tpm"] == curry_slot24["tpm"] == 65
        assert tot["tpa"] == curry_slot24["tpa"] == 139
        assert tot["ftm"] == curry_slot24["ftm"] == 65
        assert tot["fta"] == curry_slot24["fta"] == 69
        assert tot["reb"] == curry_slot24["reb"] == 79
        assert tot["ast"] == curry_slot24["ast"] == 92
        assert tot["stl"] == curry_slot24["stl"] == 24
        assert tot["tov"] == curry_slot24["tov"] == 44
        assert tot["plus_minus"] == curry_slot24["plus_minus"] == 73

    def test_statistical_splits_additivity_equations(self, curry_games_data):
        """测试 5 类统计切片的可加性方程"""
        single_games = []
        for g_entry in curry_games_data:
            g_raw = bytes.fromhex(g_entry["game_raw_hex"])
            g_meta = BoxScoreDecoder.decode_game_header(g_raw)
            p_raw = bytes.fromhex(g_entry["curry_statline_hex"])
            p_data = BoxScoreDecoder.decode_player_statline(p_raw, is_home=(g_meta["home_team_id"] == 29))
            p_data["is_win"] = (g_meta["winner_team_id"] == 29)
            p_data["game_date"] = g_meta["game_date"]
            single_games.append(p_data)

        splits_res = SeasonStatsDecoder.aggregate_game_splits(single_games)
        eqs = splits_res["additivity_equations"]
        assert eqs["total_equals_win_plus_loss"] is True
        assert eqs["total_equals_starter_plus_bench"] is True
        assert eqs["total_equals_home_plus_away"] is True


class TestPlayerCardCareerProgression:
    """球员卡片生涯履历链表测试"""

    def test_lebron_career_indices_chain(self, player_career_data):
        raw_p = bytes.fromhex(player_career_data["LeBron"]["raw_player_hex"])
        info = SeasonStatsDecoder.extract_player_career_indices(raw_p)
        assert info["player_id"] == 1013
        assert info["current_season_stats_index"] == 3296
        # 验证历史索引链表长度大于 15 个赛季
        assert len(info["career_history_stats_indices"]) >= 17
        assert info["total_seasons_recorded"] >= 18

        # 验证 2021 赛季历史记录
        idx_2021 = info["career_history_stats_indices"][0]  # 5148
        st_2021 = SeasonStatsDecoder.decode_player_stats_record(
            bytes.fromhex(player_career_data["LeBron"]["stats_records_hex"][str(idx_2021)])
        )
        assert st_2021["season_year"] == 2021
        assert st_2021["last_team"] == 15  # Lakers
        assert st_2021["games_played"] == 45
        assert st_2021["points"] == 1126


class TestTeamMatchupMatrix:
    """Slot 44 球队对决矩阵测试"""

    def test_decode_hawks_matchups(self, matchup_slice_raw):
        assert len(matchup_slice_raw) == 840  # 35 * 24
        series = MatchupMatrixDecoder.decode_team_series(matchup_slice_raw, team_slot_idx=0)
        assert len(series) == 35

        # Game 0: BKN (1 win)
        assert series[0]["head_to_head_wins"] == 1
        assert series[0]["is_unplayed"] is False

        # Game 4: CLE (unplayed)
        assert series[4]["is_unplayed"] is True
        assert series[4]["head_to_head_wins"] is None

        # Game 28: WAS (2 wins)
        assert series[28]["head_to_head_wins"] == 2


class TestSQLiteDatabaseIntegration:
    """SQLite 样本库导出与查询完整性测试"""

    def test_database_queries(self):
        # 确保数据库文件存在
        export_to_sqlite_01d.main()
        assert os.path.exists(DB_PATH)

        conn = sqlite3.connect(DB_PATH)
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM match_games")
            assert cur.fetchone()[0] == 10

            cur.execute("SELECT COUNT(*) FROM match_game_players")
            assert cur.fetchone()[0] == 52

            cur.execute("SELECT COUNT(*) FROM player_career_index")
            assert cur.fetchone()[0] == 3

            cur.execute("SELECT COUNT(*) FROM player_season_stats")
            assert cur.fetchone()[0] >= 40

            cur.execute("SELECT COUNT(*) FROM team_matchup_matrix")
            assert cur.fetchone()[0] == 35

            # 跨表关联查询：验证 Game 1 (Lakers vs Warriors) 球员总得分与比赛得分完全吻合
            cur.execute("""
                SELECT g.game_id, g.home_score, g.away_score,
                       SUM(CASE WHEN p.is_home = 1 THEN p.points ELSE 0 END) as sum_h,
                       SUM(CASE WHEN p.is_home = 0 THEN p.points ELSE 0 END) as sum_a
                FROM match_games g
                JOIN match_game_players p ON g.game_id = p.game_id
                WHERE g.game_id = 2
                GROUP BY g.game_id
            """)
            row = cur.fetchone()
            assert row is not None
            assert row[1] == row[3] == 109
            assert row[2] == row[4] == 125
        finally:
            conn.close()
