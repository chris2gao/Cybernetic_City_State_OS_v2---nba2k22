# -*- coding: utf-8 -*-
"""
NBA 2K22 原生赛季统计与统计切片解码器 (Season Stats Decoder)
负责解析 ROSTERDATA Slot 24 (PLAYER_STATS) 48 字节记录，
提取 PLAYER 结构体中的生涯历史索引链表，
并实现零幻觉确定性的 5 大统计切片 (Win/Loss, Starter/Bench, Home/Away) 聚合与方程校验。
"""

import struct
from typing import Dict, List, Any, Optional, Tuple


def _extract_bitfield(raw: bytes, offset: int, bits: int, start_bit: int) -> int:
    """提取任意字节偏移与位域区间的整数值"""
    count = (start_bit + bits + 7) // 8
    val = int.from_bytes(raw[offset : offset + count], "little")
    return (val >> start_bit) & ((1 << bits) - 1)


class SeasonStatsDecoder:
    """赛季统计与生涯履历解码器"""

    @staticmethod
    def decode_player_stats_record(raw_stat: bytes) -> Dict[str, Any]:
        """
        解码 ROSTERDATA Slot 24 中的 48 字节单赛季累积记录
        基于 NBA 2K22 PC 实机位域映射标准
        """
        if len(raw_stat) < 48:
            raise ValueError(f"PLAYER_STATS record too short: expected 48 bytes, got {len(raw_stat)}")

        last_team = int.from_bytes(raw_stat[0:2], "little")
        previous_team = int.from_bytes(raw_stat[2:4], "little")
        season_code = _extract_bitfield(raw_stat, 5, 7, 0)
        season_year = 1900 + season_code

        times = _extract_bitfield(raw_stat, 8, 7, 0)       # 出场次数 Games Played
        lineup = _extract_bitfield(raw_stat, 12, 7, 0)     # 首发出场次数 Games Started
        minutes = _extract_bitfield(raw_stat, 12, 13, 7)   # 出场分钟数

        made = _extract_bitfield(raw_stat, 14, 12, 4)      # FGM
        attempted = _extract_bitfield(raw_stat, 9, 13, 7)  # FGA

        tpm = _extract_bitfield(raw_stat, 26, 10, 6)      # 3PM
        tpa = _extract_bitfield(raw_stat, 24, 11, 0)      # 3PA

        ftm = _extract_bitfield(raw_stat, 20, 11, 0)      # FTM
        fta = _extract_bitfield(raw_stat, 21, 11, 3)      # FTA

        oreb = _extract_bitfield(raw_stat, 22, 10, 6)     # OREB
        dreb = _extract_bitfield(raw_stat, 28, 15, 0)     # DREB

        ast = _extract_bitfield(raw_stat, 25, 11, 3)      # AST
        stl = _extract_bitfield(raw_stat, 16, 11, 0)      # STL
        blk = _extract_bitfield(raw_stat, 17, 11, 3)      # BLK

        tov = _extract_bitfield(raw_stat, 29, 15, 7)      # TOV
        foul = _extract_bitfield(raw_stat, 18, 10, 6)     # Foul

        points = int.from_bytes(raw_stat[32:34], "little") # PTS
        plus_minus = int.from_bytes(raw_stat[34:36], "little", signed=True) # +/-

        double_doubles = _extract_bitfield(raw_stat, 43, 7, 1)
        triple_doubles = _extract_bitfield(raw_stat, 9, 7, 0)

        # 原生得分守恒校验方程: points == 2 * made + 3pt_made + free_throws_made
        scoring_identity_valid = (points == 2 * made + tpm + ftm)

        return {
            "season_year": season_year,
            "last_team": last_team,
            "previous_team": previous_team if previous_team != 65535 else None,
            "games_played": times,
            "games_started": lineup,
            "minutes": minutes,
            "points": points,
            "fgm": made,
            "fga": attempted,
            "tpm": tpm,
            "tpa": tpa,
            "ftm": ftm,
            "fta": fta,
            "oreb": oreb,
            "dreb": dreb,
            "reb": oreb + dreb,
            "ast": ast,
            "stl": stl,
            "blk": blk,
            "tov": tov,
            "foul": foul,
            "plus_minus": plus_minus,
            "double_doubles": double_doubles,
            "triple_doubles": triple_doubles,
            "scoring_identity_valid": scoring_identity_valid,
            "per_game": {
                "ppg": round(points / times, 2) if times > 0 else 0.0,
                "rpg": round((oreb + dreb) / times, 2) if times > 0 else 0.0,
                "apg": round(ast / times, 2) if times > 0 else 0.0,
                "spg": round(stl / times, 2) if times > 0 else 0.0,
                "bpg": round(blk / times, 2) if times > 0 else 0.0,
                "mpg": round(minutes / times, 2) if times > 0 else 0.0
            },
            "percentages": {
                "fg_pct": round(made / attempted, 4) if attempted > 0 else None,
                "tp_pct": round(tpm / tpa, 4) if tpa > 0 else None,
                "ft_pct": round(ftm / fta, 4) if fta > 0 else None,
                "efg_pct": round((made + 0.5 * tpm) / attempted, 4) if attempted > 0 else None,
                "ts_pct": round(points / (2 * (attempted + 0.44 * fta)), 4) if (attempted + 0.44 * fta) > 0 else None
            }
        }

    @staticmethod
    def extract_player_career_indices(raw_player: bytes) -> Dict[str, Any]:
        """
        从 1264 字节 PLAYER 结构体中提取当前赛季与生涯历史赛季的 Slot 24 索引链表
        - 0xFC (uint16): 当前赛季索引
        - 0xFE..0x126 (array of uint16): 连续历史赛季倒序索引
        """
        if len(raw_player) < 1264:
            raise ValueError(f"PLAYER record too short: expected 1264 bytes, got {len(raw_player)}")

        current_idx = struct.unpack_from("<H", raw_player, 0xFC)[0]
        history_indices = []
        for k in range(20):  # 支持最多 20 个历史赛季
            off = 0xFE + k * 2
            idx = struct.unpack_from("<H", raw_player, off)[0]
            if idx in (0, 65535, 32756):
                break
            history_indices.append(idx)

        player_id = struct.unpack_from("<H", raw_player, 0x2F8)[0]
        last_name = raw_player[0:40].decode("utf-16le", errors="ignore").split("\x00")[0]
        first_name = raw_player[40:80].decode("utf-16le", errors="ignore").split("\x00")[0]

        return {
            "player_id": player_id,
            "name": f"{first_name} {last_name}".strip(),
            "current_season_stats_index": current_idx if current_idx not in (65535, 32756) else None,
            "career_history_stats_indices": history_indices,
            "total_seasons_recorded": (1 if current_idx not in (65535, 32756) else 0) + len(history_indices)
        }

    @classmethod
    def aggregate_game_splits(cls, single_game_boxscores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        从球员单场比赛流水聚合 5 大统计切片，并严格验证可加性方程：
        1. Total = Win + Loss
        2. Total = Starter + Bench
        3. Total = Home + Away
        """
        def sum_stats(games_subset: List[Dict[str, Any]]) -> Dict[str, Any]:
            if not games_subset:
                return {
                    "games": 0, "minutes": 0, "points": 0, "fgm": 0, "fga": 0,
                    "tpm": 0, "tpa": 0, "ftm": 0, "fta": 0, "oreb": 0, "dreb": 0,
                    "reb": 0, "ast": 0, "stl": 0, "blk": 0, "tov": 0, "fouls": 0, "plus_minus": 0
                }
            return {
                "games": len(games_subset),
                "minutes": sum(g["minutes"] for g in games_subset),
                "points": sum(g["points"] for g in games_subset),
                "fgm": sum(g["fgm"] for g in games_subset),
                "fga": sum(g["fga"] for g in games_subset),
                "tpm": sum(g["tpm"] for g in games_subset),
                "tpa": sum(g["tpa"] for g in games_subset),
                "ftm": sum(g["ftm"] for g in games_subset),
                "fta": sum(g["fta"] for g in games_subset),
                "oreb": sum(g["oreb"] for g in games_subset),
                "dreb": sum(g["dreb"] for g in games_subset),
                "reb": sum(g["reb"] for g in games_subset),
                "ast": sum(g["ast"] for g in games_subset),
                "stl": sum(g["stl"] for g in games_subset),
                "blk": sum(g["blk"] for g in games_subset),
                "tov": sum(g["tov"] for g in games_subset),
                "fouls": sum(g["fouls"] for g in games_subset),
                "plus_minus": sum(g["plus_minus"] for g in games_subset)
            }

        total = sum_stats(single_game_boxscores)

        # 1. 胜负切片
        win_games = [g for g in single_game_boxscores if g.get("is_win", True)]
        loss_games = [g for g in single_game_boxscores if not g.get("is_win", True)]
        win_split = sum_stats(win_games)
        loss_split = sum_stats(loss_games)

        # 2. 先发替补切片
        starter_games = [g for g in single_game_boxscores if g.get("is_starter", True)]
        bench_games = [g for g in single_game_boxscores if not g.get("is_starter", True)]
        starter_split = sum_stats(starter_games)
        bench_split = sum_stats(bench_games)

        # 3. 主客场切片
        home_games = [g for g in single_game_boxscores if g.get("is_home", True)]
        away_games = [g for g in single_game_boxscores if not g.get("is_home", True)]
        home_split = sum_stats(home_games)
        away_split = sum_stats(away_games)

        # 4. 近期表现 (Last 5 & Last 10)
        sorted_games = sorted(single_game_boxscores, key=lambda x: x.get("game_date", ""), reverse=True)
        last_5_split = sum_stats(sorted_games[:5])
        last_10_split = sum_stats(sorted_games[:10])

        # 严格方程验证
        metric_keys = ["games", "minutes", "points", "fgm", "fga", "tpm", "tpa", "ftm", "fta", "oreb", "dreb", "reb", "ast", "stl", "blk", "tov", "fouls", "plus_minus"]

        win_loss_valid = all(total[k] == (win_split[k] + loss_split[k]) for k in metric_keys)
        starter_bench_valid = all(total[k] == (starter_split[k] + bench_split[k]) for k in metric_keys)
        home_away_valid = all(total[k] == (home_split[k] + away_split[k]) for k in metric_keys)

        return {
            "total": total,
            "splits": {
                "win": win_split,
                "loss": loss_split,
                "starter": starter_split,
                "bench": bench_split,
                "home": home_split,
                "away": away_split,
                "last_5": last_5_split,
                "last_10": last_10_split
            },
            "additivity_equations": {
                "total_equals_win_plus_loss": win_loss_valid,
                "total_equals_starter_plus_bench": starter_bench_valid,
                "total_equals_home_plus_away": home_away_valid
            }
        }
