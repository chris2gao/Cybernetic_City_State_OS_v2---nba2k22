# -*- coding: utf-8 -*-
"""
NBA 2K22 原生单场比赛、赛季统计与对决矩阵 SQLite 样本导出器 (AG-NATIVE-01D)
纯离线运行，从 fixtures 二进制样本提取数据，构建确定性 SQLite 数据库。
"""

import os
import sys
import json
import sqlite3
import struct
from typing import Dict, List, Any

# 导入解码器
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "decoders"))

from boxscore_decoder import BoxScoreDecoder
from season_stats_decoder import SeasonStatsDecoder
from matchup_matrix_decoder import MatchupMatrixDecoder

FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures")
DB_PATH = os.path.join(BASE_DIR, "native_boxscore_sample.db")


def create_schema(conn: sqlite3.Connection):
    """创建 SQLite 表结构"""
    cursor = conn.cursor()
    cursor.executescript("""
    DROP TABLE IF EXISTS match_game_players;
    DROP TABLE IF EXISTS match_games;
    DROP TABLE IF EXISTS player_season_stats;
    DROP TABLE IF EXISTS player_career_index;
    DROP TABLE IF EXISTS team_matchup_matrix;

    CREATE TABLE match_games (
        game_id INTEGER PRIMARY KEY,
        game_date TEXT NOT NULL,
        played_date TEXT,
        home_team_id INTEGER NOT NULL,
        away_team_id INTEGER NOT NULL,
        winner_team_id INTEGER,
        home_score INTEGER NOT NULL,
        away_score INTEGER NOT NULL,
        point_differential INTEGER,
        status INTEGER,
        was_simulated INTEGER,
        attendance INTEGER,
        q1_home INTEGER, q2_home INTEGER, q3_home INTEGER, q4_home INTEGER, ot_home INTEGER,
        q1_away INTEGER, q2_away INTEGER, q3_away INTEGER, q4_away INTEGER, ot_away INTEGER
    );

    CREATE TABLE match_game_players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INTEGER NOT NULL,
        player_id INTEGER NOT NULL,
        is_home INTEGER NOT NULL,
        is_starter INTEGER NOT NULL,
        minutes INTEGER NOT NULL,
        points INTEGER NOT NULL,
        fgm INTEGER, fga INTEGER, fg_pct REAL,
        tpm INTEGER, tpa INTEGER, tp_pct REAL,
        ftm INTEGER, fta INTEGER, ft_pct REAL,
        oreb INTEGER, dreb INTEGER, reb INTEGER,
        ast INTEGER, stl INTEGER, blk INTEGER, tov INTEGER, fouls INTEGER,
        plus_minus INTEGER,
        ts_pct REAL, efg_pct REAL, game_score REAL,
        double_double INTEGER, triple_double INTEGER,
        FOREIGN KEY (game_id) REFERENCES match_games(game_id)
    );

    CREATE TABLE player_career_index (
        player_id INTEGER NOT NULL,
        player_name TEXT NOT NULL,
        current_stats_index INTEGER,
        history_stats_indices TEXT,
        total_seasons INTEGER,
        PRIMARY KEY (player_id)
    );

    CREATE TABLE player_season_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER NOT NULL,
        season_year INTEGER NOT NULL,
        last_team INTEGER NOT NULL,
        games_played INTEGER NOT NULL,
        games_started INTEGER NOT NULL,
        minutes INTEGER NOT NULL,
        points INTEGER NOT NULL,
        fgm INTEGER, fga INTEGER, fg_pct REAL,
        tpm INTEGER, tpa INTEGER, tp_pct REAL,
        ftm INTEGER, fta INTEGER, ft_pct REAL,
        oreb INTEGER, dreb INTEGER, reb INTEGER,
        ast INTEGER, stl INTEGER, blk INTEGER, tov INTEGER, fouls INTEGER,
        plus_minus INTEGER,
        ppg REAL, rpg REAL, apg REAL,
        FOREIGN KEY (player_id) REFERENCES player_career_index(player_id)
    );

    CREATE TABLE team_matchup_matrix (
        record_index INTEGER PRIMARY KEY,
        team_slot_index INTEGER NOT NULL,
        opponent_slot_index INTEGER NOT NULL,
        home_team_ptr TEXT NOT NULL,
        away_team_ptr TEXT NOT NULL,
        head_to_head_wins INTEGER,
        is_unplayed INTEGER NOT NULL,
        series_status_code INTEGER NOT NULL
    );
    """)
    conn.commit()


def populate_games_and_boxscores(conn: sqlite3.Connection):
    """解析并导入比赛与单场球员技术统计"""
    games_bin_path = os.path.join(FIXTURES_DIR, "sample_games_slice.bin")
    statbank_bin_path = os.path.join(FIXTURES_DIR, "sample_statbank_slice.bin")

    if not (os.path.exists(games_bin_path) and os.path.exists(statbank_bin_path)):
        return 0, 0

    with open(games_bin_path, "rb") as f:
        games_raw = f.read()
    with open(statbank_bin_path, "rb") as f:
        statbank_raw = f.read()

    cursor = conn.cursor()
    games_count = len(games_raw) // 60
    players_count = 0

    stat_cursor_byte = 0
    for g_idx in range(games_count):
        g_raw = games_raw[g_idx * 60 : (g_idx + 1) * 60]
        meta = BoxScoreDecoder.decode_game_header(g_raw)
        lines = meta["linescore"]
        
        cursor.execute("""
            INSERT INTO match_games (
                game_id, game_date, played_date, home_team_id, away_team_id,
                winner_team_id, home_score, away_score, point_differential,
                status, was_simulated, attendance,
                q1_home, q2_home, q3_home, q4_home, ot_home,
                q1_away, q2_away, q3_away, q4_away, ot_away
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            meta["game_id"], meta["game_date"], meta["played_date"],
            meta["home_team_id"], meta["away_team_id"], meta["winner_team_id"],
            meta["home_score"], meta["away_score"], meta["point_differential"],
            meta["status"], 1 if meta["was_simulated"] else 0, meta["attendance"],
            lines["home"]["q1"], lines["home"]["q2"], lines["home"]["q3"], lines["home"]["q4"], lines["home"]["ot"],
            lines["away"]["q1"], lines["away"]["q2"], lines["away"]["q3"], lines["away"]["q4"], lines["away"]["ot"]
        ))

        # 解码球员统计 (若在 statbank 范围内)
        num_h = meta["boxscore_meta"]["num_home_players"]
        num_a = meta["boxscore_meta"]["num_away_players"]
        tot_p = num_h + num_a
        needed_bytes = tot_p * 24

        if stat_cursor_byte + needed_bytes <= len(statbank_raw):
            sb_slice = statbank_raw[stat_cursor_byte : stat_cursor_byte + needed_bytes]
            stat_cursor_byte += needed_bytes
            
            full = BoxScoreDecoder.decode_full_boxscore(g_raw, sb_slice)
            for p in full["home_players"] + full["away_players"]:
                cursor.execute("""
                    INSERT INTO match_game_players (
                        game_id, player_id, is_home, is_starter, minutes, points,
                        fgm, fga, fg_pct, tpm, tpa, tp_pct, ftm, fta, ft_pct,
                        oreb, dreb, reb, ast, stl, blk, tov, fouls,
                        plus_minus, ts_pct, efg_pct, game_score, double_double, triple_double
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    meta["game_id"], p["player_id"], 1 if p["is_home"] else 0, 1 if p["is_starter"] else 0,
                    p["minutes"], p["points"], p["fgm"], p["fga"], p["fg_pct"],
                    p["tpm"], p["tpa"], p["tp_pct"], p["ftm"], p["fta"], p["ft_pct"],
                    p["oreb"], p["dreb"], p["reb"], p["ast"], p["stl"], p["blk"], p["tov"], p["fouls"],
                    p["plus_minus"], p["ts_pct"], p["efg_pct"], p["game_score"],
                    p["double_double"], p["triple_double"]
                ))
                players_count += 1

    conn.commit()
    return games_count, players_count


def populate_career_and_season_stats(conn: sqlite3.Connection):
    """解析并导入球员生涯索引与多赛季统计"""
    career_json_path = os.path.join(FIXTURES_DIR, "sample_player_career_slice.json")
    if not os.path.exists(career_json_path):
        return 0, 0

    with open(career_json_path, "r", encoding="utf-8") as f:
        career_data = json.load(f)

    cursor = conn.cursor()
    players_count = 0
    seasons_count = 0

    for name, p_info in career_data.items():
        raw_player = bytes.fromhex(p_info["raw_player_hex"])
        parsed_indices = SeasonStatsDecoder.extract_player_career_indices(raw_player)
        pid = parsed_indices["player_id"]

        cursor.execute("""
            INSERT INTO player_career_index (
                player_id, player_name, current_stats_index, history_stats_indices, total_seasons
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            pid, name, parsed_indices["current_season_stats_index"],
            json.dumps(parsed_indices["career_history_stats_indices"]),
            parsed_indices["total_seasons_recorded"]
        ))
        players_count += 1

        # 导入各赛季记录
        for idx_str, st_hex in p_info["stats_records_hex"].items():
            raw_st = bytes.fromhex(st_hex)
            st = SeasonStatsDecoder.decode_player_stats_record(raw_st)
            cursor.execute("""
                INSERT INTO player_season_stats (
                    player_id, season_year, last_team, games_played, games_started,
                    minutes, points, fgm, fga, fg_pct, tpm, tpa, tp_pct,
                    ftm, fta, ft_pct, oreb, dreb, reb, ast, stl, blk, tov, fouls,
                    plus_minus, ppg, rpg, apg
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid, st["season_year"], st["last_team"], st["games_played"], st["games_started"],
                st["minutes"], st["points"], st["fgm"], st["fga"], st["percentages"]["fg_pct"],
                st["tpm"], st["tpa"], st["percentages"]["tp_pct"],
                st["ftm"], st["fta"], st["percentages"]["ft_pct"],
                st["oreb"], st["dreb"], st["reb"], st["ast"], st["stl"], st["blk"], st["tov"], st["foul"],
                st["plus_minus"], st["per_game"]["ppg"], st["per_game"]["rpg"], st["per_game"]["apg"]
            ))
            seasons_count += 1

    conn.commit()
    return players_count, seasons_count


def populate_matchup_matrix(conn: sqlite3.Connection):
    """解析并导入 Slot 44 球队对决矩阵"""
    matrix_bin_path = os.path.join(FIXTURES_DIR, "sample_matchup_matrix_slice.bin")
    if not os.path.exists(matrix_bin_path):
        return 0

    with open(matrix_bin_path, "rb") as f:
        raw_matrix = f.read()

    series = MatchupMatrixDecoder.decode_team_series(raw_matrix, team_slot_idx=0)
    cursor = conn.cursor()
    for rec in series:
        cursor.execute("""
            INSERT INTO team_matchup_matrix (
                record_index, team_slot_index, opponent_slot_index,
                home_team_ptr, away_team_ptr, head_to_head_wins,
                is_unplayed, series_status_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rec["record_index"], rec["team_slot_index"], rec["opponent_slot_index"],
            rec["home_team_ptr"], rec["away_team_ptr"], rec["head_to_head_wins"],
            1 if rec["is_unplayed"] else 0, rec["series_status_code"]
        ))
    conn.commit()
    return len(series)


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        create_schema(conn)
        g_cnt, p_cnt = populate_games_and_boxscores(conn)
        c_cnt, s_cnt = populate_career_and_season_stats(conn)
        m_cnt = populate_matchup_matrix(conn)
        print(f"Export successful to {DB_PATH}:")
        print(f"  - match_games: {g_cnt}")
        print(f"  - match_game_players: {p_cnt}")
        print(f"  - player_career_index: {c_cnt}")
        print(f"  - player_season_stats: {s_cnt}")
        print(f"  - team_matchup_matrix: {m_cnt}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
