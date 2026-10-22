# -*- coding: utf-8 -*-
"""
NBA 2K22 原生球队对决矩阵解码器 (Matchup Matrix Decoder)
负责解析 ROSTERDATA Slot 44 (1,260 条记录，步长 24 字节)。
纠正 AG-NATIVE-01C 中将 Slot 44 误判为全季赛程的结论：
实机验证证明 Slot 44 是 36 支球队对 35 支对手的对决交锋胜负流水与系列赛规划表 (36 * 35 = 1260)。
"""

import struct
from typing import Dict, List, Any, Optional


class MatchupMatrixDecoder:
    """球队交锋对决矩阵解码器"""

    @staticmethod
    def decode_record(raw_record: bytes, record_index: int = 0) -> Dict[str, Any]:
        """解码 24 字节 Slot 44 对决记录"""
        if len(raw_record) < 24:
            raise ValueError(f"Matchup record too short: expected 24 bytes, got {len(raw_record)}")

        p_home, p_away = struct.unpack_from("<QQ", raw_record, 0)
        score_bytes = struct.unpack_from("<BBBB", raw_record, 16)
        h2h_wins, status_code = struct.unpack_from("<HH", raw_record, 20)

        # 归属球队与对手槽位索引
        team_slot_idx = record_index // 35
        opponent_slot_idx = record_index % 35

        is_unplayed = (h2h_wins == 65535)

        return {
            "record_index": record_index,
            "team_slot_index": team_slot_idx,
            "opponent_slot_index": opponent_slot_idx,
            "home_team_ptr": hex(p_home),
            "away_team_ptr": hex(p_away),
            "packed_score_bytes": list(score_bytes),
            "head_to_head_wins": None if is_unplayed else h2h_wins,
            "is_unplayed": is_unplayed,
            "series_status_code": status_code
        }

    @classmethod
    def decode_team_series(cls, raw_35_records: bytes, team_slot_idx: int = 0) -> List[Dict[str, Any]]:
        """解码一支球队对全部 35 个可能对手的完整对决记录切片 (35 * 24 = 840 字节)"""
        if len(raw_35_records) < 35 * 24:
            raise ValueError(f"Team slice too short: expected 840 bytes, got {len(raw_35_records)}")

        series = []
        for i in range(35):
            rec = raw_35_records[i * 24 : (i + 1) * 24]
            series.append(cls.decode_record(rec, record_index=team_slot_idx * 35 + i))
        return series
