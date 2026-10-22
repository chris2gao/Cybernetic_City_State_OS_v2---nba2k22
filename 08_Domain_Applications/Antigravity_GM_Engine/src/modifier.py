# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 外部 GM 引擎修改与热注入器 (League Modifier)
提供对球员属性、倾向、性格徽章、球星专属动画以及交易状态的标准化安全写入接口。
"""
import sys
import os
from typing import Optional, List

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
import config

class LeagueModifier:
    def __init__(self, mem: Optional[GameMemory] = None):
        self.mem = mem if mem else GameMemory()

    @staticmethod
    def _reject_legacy_player_edit():
        raise PermissionError(
            "Generic player edits are disabled by the current player policy. "
            "An approved trade does not authorize ability changes. Historical-gravity "
            "edits need a separate controlled executor; MC growth remains deferred."
        )

    def set_player_attribute(self, player_address: int, attr_name: str, rating_25_to_99: int) -> bool:
        """
        设置球员某项能力值 (自动换算为 2K 底层 0~255 原生值)
        :param player_address: 球员内存绝对基址
        :param attr_name: 属性名 (如 ATTR_THREE_POINT, ATTR_PASS_ACCURACY)
        :param rating_25_to_99: 游戏内评分 (25~99)
        """
        self._reject_legacy_player_edit()
        offset = config.PLAYER_OFFSETS.get(attr_name)
        if offset is None:
            raise KeyError(f"未知的属性名称: {attr_name}")
            
        raw_val = config.rating_to_raw(rating_25_to_99)
        return self.mem.write_uint8(player_address + offset, raw_val)

    def set_player_tendency(self, player_address: int, tend_name: str, value_0_to_100: int) -> bool:
        """设置球员战术倾向 (0~100)"""
        self._reject_legacy_player_edit()
        offset = config.PLAYER_OFFSETS.get(tend_name)
        if offset is None:
            raise KeyError(f"未知的倾向名称: {tend_name}")
            
        val = min(100, max(0, value_0_to_100))
        return self.mem.write_uint8(player_address + offset, val)

    def set_signature_package(self, player_address: int, signature_id: int, audio_sig_id: Optional[int] = None) -> bool:
        """
        为球员挂载球星赛场专属被动动画与音频 (如库里、利拉德、特雷杨)
        """
        self._reject_legacy_player_edit()
        audio_id = audio_sig_id if audio_sig_id is not None else signature_id
        res1 = self.mem.write_uint32(player_address + config.PLAYER_OFFSETS["SIGNATURE_ID"], signature_id)
        res2 = self.mem.write_uint32(player_address + config.PLAYER_OFFSETS["AUDIO_SIG_ID"], audio_id)
        return res1 and res2

    def set_player_personality(self, player_address: int, expressive: bool = True, friendly: bool = True, alpha_dog: bool = True) -> bool:
        """设置球员性格：开启极具表现力、友善、领头羊，并关闭内敛和悠闲"""
        self._reject_legacy_player_edit()
        # 读取 0x4BB 开始的 10 字节性格位域
        cur_bytes = bytearray(self.mem.read_bytes(player_address + 0x4BB, 10))
        if len(cur_bytes) < 10:
            return False
            
        if expressive:
            cur_bytes[5] |= 0x02   # 0x4C0 bit 1: EXPRESSIVE
            cur_bytes[5] |= 0x01   # 0x4C0 bit 0: PAT_MY_BACK
        if friendly:
            cur_bytes[2] |= 0x02   # 0x4BD bit 1: FRIENDLY
        if alpha_dog:
            cur_bytes[0] |= 0x02   # 0x4BB bit 1: ALPHA_DOG
            
        # 抹除 RESERVED (0x4BC bit 1) 与 LAID_BACK (0x4C1 bit 1)
        cur_bytes[1] &= ~0x02
        cur_bytes[6] &= ~0x02
        
        return self.mem.write_bytes(player_address + 0x4BB, bytes(cur_bytes))

    def set_trade_override(self, enable: bool = True) -> bool:
        """一键开启或关闭强制交易开关 (Trade Override)"""
        trade_base = self.mem.base_address + config.BASE_TRADE_CONTROLLER_OFFSET
        target = trade_base + config.TRADE_OFFSETS["TRADE_OVERRIDE"]
        return self.mem.write_uint32(target, 1 if enable else 0)

    def set_cpu_cpu_trade(self, enable: bool = False) -> bool:
        """开启或彻底关闭游戏原生 CPU 自动弱智交易"""
        trade_base = self.mem.base_address + config.BASE_TRADE_CONTROLLER_OFFSET
        target = trade_base + config.TRADE_OFFSETS["CPU_CPU_TRADE"]
        return self.mem.write_uint32(target, 1 if enable else 0)

if __name__ == "__main__":
    modifier = LeagueModifier()
    print("LeagueModifier 已就绪，连接 PID:", modifier.mem.pid)
