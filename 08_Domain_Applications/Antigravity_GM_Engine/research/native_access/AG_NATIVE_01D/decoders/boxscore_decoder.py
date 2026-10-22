# -*- coding: utf-8 -*-
"""
NBA 2K22 原生单场比赛与 BoxScore 解码器 (BoxScore Decoder)
负责解析 SEASON 单例中 60 字节 SEASON_GAME 结构与 24 字节 BOXSCORE_STATLINE 球员数据行。
"""

import struct
from typing import Dict, List, Any, Optional, Tuple


def decode_schedule_date(date_int: int) -> Tuple[int, int, int, str]:
    """
    解码 2K SCHEDULEDATE 32 位位域
    bits 0..4: Id
    bits 5..15: MinutesSinceMidnight
    bits 16..20: Day (1..31)
    bits 21..24: Month (1..12)
    bits 25..31: BaseYearOffset -> 2000 + offset
    """
    day = (date_int >> 16) & 0x1F
    month = (date_int >> 21) & 0x0F
    year_offset = (date_int >> 25) & 0x7F
    year = 2000 + year_offset
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    return year, month, day, date_str


class BoxScoreDecoder:
    """单场比赛与球员技术统计解码器"""

    @staticmethod
    def decode_game_header(raw_game: bytes) -> Dict[str, Any]:
        """解码 60 字节 SEASON_GAME 结构"""
        if len(raw_game) < 60:
            raise ValueError(f"Game struct too short: expected 60 bytes, got {len(raw_game)}")

        date_val, pdate_val, game_id = struct.unpack_from("<III", raw_game, 0)
        home_team_id, away_team_id = struct.unpack_from("<HH", raw_game, 12)
        flags = struct.unpack_from("<I", raw_game, 56)[0]

        # 状态位解析
        status = (flags >> 11) & 0x03  # 0: Scheduled, 1: In-Progress, 2: Final
        was_simulated = (flags >> 18) & 0x01
        time_period_code = (flags >> 6) & 0x07
        is_nationally_televised = (flags >> 20) & 0x01
        overtime_count = flags & 0x3F

        # 日期
        _, _, _, game_date = decode_schedule_date(date_val)
        played_date = decode_schedule_date(pdate_val)[3] if pdate_val != 0 else game_date

        # 单节比分 LineScore (bytes 44..51)
        q1_h, q2_h, q3_h, q4_h = raw_game[44], raw_game[45], raw_game[46], raw_game[47]
        q1_a, q2_a, q3_a, q4_a = raw_game[48], raw_game[49], raw_game[50], raw_game[51]
        line_ot = struct.unpack_from("<I", raw_game, 52)[0]
        ot_h = line_ot & 0xFF
        ot_a = (line_ot >> 8) & 0xFF
        attendance = (line_ot >> 16) & 0x7FFF

        home_score = q1_h + q2_h + q3_h + q4_h + ot_h
        away_score = q1_a + q2_a + q3_a + q4_a + ot_a
        winner_id = home_team_id if home_score >= away_score else away_team_id
        point_diff = abs(home_score - away_score)

        # 24 字节原生 BOXSCORE (offset 20..44)
        bs_raw = raw_game[20:44]
        stat_idx = struct.unpack_from("<H", bs_raw, 0)[0]
        num_home_players, num_away_players = bs_raw[2], bs_raw[3]

        w20 = struct.unpack_from("<I", bs_raw, 20)[0]
        home_possessions = float(w20 & 0xFF)
        away_possessions = float((w20 >> 14) & 0xFF)

        return {
            "game_id": game_id,
            "game_date": game_date,
            "played_date": played_date,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "winner_team_id": winner_id,
            "home_score": home_score,
            "away_score": away_score,
            "point_differential": point_diff,
            "status": status,
            "was_simulated": bool(was_simulated),
            "is_nationally_televised": bool(is_nationally_televised),
            "overtime_count": overtime_count,
            "attendance": attendance,
            "linescore": {
                "home": {"q1": q1_h, "q2": q2_h, "q3": q3_h, "q4": q4_h, "ot": ot_h, "total": home_score},
                "away": {"q1": q1_a, "q2": q2_a, "q3": q3_a, "q4": q4_a, "ot": ot_a, "total": away_score}
            },
            "boxscore_meta": {
                "stat_lines_index": stat_idx,
                "num_home_players": num_home_players,
                "num_away_players": num_away_players,
                "home_lead": bs_raw[4],
                "home_fastbreak": bs_raw[5],
                "home_paint": bs_raw[6],
                "home_2nd_chance": bs_raw[7],
                "home_pts_off_to": bs_raw[11],
                "away_lead": bs_raw[12],
                "away_fastbreak": bs_raw[13],
                "away_paint": bs_raw[14],
                "away_2nd_chance": bs_raw[15],
                "away_pts_off_to": bs_raw[19],
                "home_possessions": home_possessions,
                "away_possessions": away_possessions
            }
        }

    @staticmethod
    def decode_player_statline(raw_stat: bytes, is_home: bool = True) -> Dict[str, Any]:
        """解码 24 字节原生 BOXSCORE_STATLINE 球员数据行"""
        if len(raw_stat) < 24:
            raise ValueError(f"Statline struct too short: expected 24 bytes, got {len(raw_stat)}")

        w0, w1, w2, w3, w4, w5 = struct.unpack("<IIIIII", raw_stat[:24])

        player_id = w0 & 0xFFFF
        in_use = (w0 >> 16) & 0x01
        minutes = (w0 >> 17) & 0x7F
        raw_pm = (w0 >> 24) & 0xFF
        plus_minus = raw_pm - 256 if raw_pm > 127 else raw_pm

        fgm = w1 & 0xFF
        fga = (w1 >> 8) & 0x1FF
        tpm = (w1 >> 17) & 0x7F
        tpa = (w1 >> 24) & 0xFF

        fta = w2 & 0xFF
        stl = (w2 >> 8) & 0xFF
        blk = (w2 >> 16) & 0xFF
        dreb = (w2 >> 24) & 0xFF

        def_fgm = w3 & 0xFF
        def_fga = (w3 >> 8) & 0x1FF
        def_pts = (w3 >> 17) & 0x7FFF

        ast = w4 & 0x7F
        ftm = (w4 >> 7) & 0x7F
        oreb = (w4 >> 14) & 0xFF
        tov = (w4 >> 22) & 0x7F

        possessions = w5 & 0xFF
        fouls = (w5 >> 8) & 0x0F
        is_starter = (w5 >> 12) & 0x01

        # 确定性得分与篮板求和
        points = fgm * 2 + tpm + ftm
        rebounds = oreb + dreb

        # 高阶数据确定性推导
        ts_denom = 2 * (fga + 0.44 * fta)
        ts_pct = round(points / ts_denom, 4) if ts_denom > 0 else None
        efg_pct = round((fgm + 0.5 * tpm) / fga, 4) if fga > 0 else None
        fg_pct = round(fgm / fga, 4) if fga > 0 else None
        tp_pct = round(tpm / tpa, 4) if tpa > 0 else None
        ft_pct = round(ftm / fta, 4) if fta > 0 else None

        # Hollinger GameScore
        game_score = round(
            points + 0.4 * fgm - 0.7 * fga - 0.4 * (fta - ftm) +
            0.7 * oreb + 0.3 * dreb + stl + 0.7 * ast + 0.7 * blk -
            0.4 * fouls - tov,
            2
        )

        # 两双与三双
        cat_10 = sum(1 for val in [points, rebounds, ast, stl, blk] if val >= 10)
        double_double = 1 if cat_10 >= 2 else 0
        triple_double = 1 if cat_10 >= 3 else 0

        return {
            "player_id": player_id,
            "is_home": is_home,
            "is_starter": bool(is_starter),
            "in_use": bool(in_use),
            "minutes": minutes,
            "points": points,
            "fgm": fgm,
            "fga": fga,
            "fg_pct": fg_pct,
            "tpm": tpm,
            "tpa": tpa,
            "tp_pct": tp_pct,
            "ftm": ftm,
            "fta": fta,
            "ft_pct": ft_pct,
            "oreb": oreb,
            "dreb": dreb,
            "reb": rebounds,
            "ast": ast,
            "stl": stl,
            "blk": blk,
            "tov": tov,
            "fouls": fouls,
            "plus_minus": plus_minus,
            "def_fgm": def_fgm,
            "def_fga": def_fga,
            "def_pts": def_pts,
            "possessions": possessions,
            "ts_pct": ts_pct,
            "efg_pct": efg_pct,
            "game_score": game_score,
            "double_double": double_double,
            "triple_double": triple_double
        }

    @classmethod
    def decode_full_boxscore(cls, raw_game: bytes, raw_statlines: bytes) -> Dict[str, Any]:
        """完整解码一场比赛的概况及双方所有出场球员技术统计，并校验得分守恒"""
        game = cls.decode_game_header(raw_game)
        meta = game["boxscore_meta"]
        num_h = meta["num_home_players"]
        num_a = meta["num_away_players"]
        total_p = num_h + num_a

        if len(raw_statlines) < total_p * 24:
            raise ValueError(
                f"Statlines buffer insufficient: expected {total_p * 24} bytes for {total_p} players, got {len(raw_statlines)}"
            )

        home_players = []
        away_players = []
        for i in range(total_p):
            is_h = (i < num_h)
            p_raw = raw_statlines[i * 24 : (i + 1) * 24]
            p_data = cls.decode_player_statline(p_raw, is_home=is_h)
            if is_h:
                home_players.append(p_data)
            else:
                away_players.append(p_data)

        # 得分守恒校验
        sum_pts_h = sum(p["points"] for p in home_players)
        sum_pts_a = sum(p["points"] for p in away_players)
        is_h_conserved = (sum_pts_h == game["home_score"])
        is_a_conserved = (sum_pts_a == game["away_score"])

        game["home_players"] = home_players
        game["away_players"] = away_players
        game["conservation"] = {
            "home_score_exact": is_h_conserved,
            "away_score_exact": is_a_conserved,
            "sum_pts_home": sum_pts_h,
            "sum_pts_away": sum_pts_a,
            "target_home_score": game["home_score"],
            "target_away_score": game["away_score"]
        }
        return game
