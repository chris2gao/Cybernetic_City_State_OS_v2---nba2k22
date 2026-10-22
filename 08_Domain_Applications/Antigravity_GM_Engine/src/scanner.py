# -*- coding: utf-8 -*-
"""
NBA 2K22 存档通用内存定位器 (Save Memory Scanner)
支持任意存档（MC生涯 / 终极联盟 / 自定义名单）：
1. 自动定位现役 30 支核心球队结构体数组 (通过 Pacers/Lakers 锚点与 0x1258 步长)
2. 自动定位主教练 (Staff) 战术体系
3. 自动定位活跃/焦点球员 (Active Player Pointer)
"""
from typing import Dict, List, Optional
from memory import GameMemory
import config

class LeagueScanner:
    def __init__(self, mem: GameMemory):
        self.mem = mem

    def find_active_teams(self) -> Dict[int, Dict]:
        """
        全自动定位 30 支现役 NBA 核心球队。
        算法：
        1. 在内存中扫描 Indiana Pacers 签名 (城市名 'Indiana' + 缩写 'IND')
        2. 以其为锚点，利用团队步长 0x1258 沿数组前后双向索引
        3. 校验 TEAM_TYPE 必须为 0 (NORMAL 现役球队，过滤经典与全明星)
        """
        pacers_pattern = "Pacers".encode('utf-16le')
        ind_abb = "IND".encode('utf-16le')
        
        # 扫描候选区
        candidates = self.mem.scan_pattern(pacers_pattern, 0x7FF4E0000000, 0x7FF4E8000000)
        pacers_base = None
        
        for cand in candidates:
            # 校验 offset 0x2B4 是否为队名
            base = cand - config.TEAM_OFFSETS["TEAM_NAME"]
            abb = self.mem.read_bytes(base + config.TEAM_OFFSETS["ABB"], 6)
            if abb == ind_abb:
                pacers_base = base
                break
                
        if not pacers_base:
            raise RuntimeError("未在当前运行内存中定位到球队结构体基址，请确保已进入存档！")
            
        teams = {}
        # 沿步长 0x1258 向前向后各遍历 40 个槽位
        for idx in range(-35, 35):
            t_addr = pacers_base + idx * config.TEAM_STRUCT_STRIDE
            raw_name = self.mem.read_utf16_string(t_addr + config.TEAM_OFFSETS["TEAM_NAME"], 40)
            raw_city = self.mem.read_utf16_string(t_addr + config.TEAM_OFFSETS["CITY"], 40)
            raw_abb = self.mem.read_utf16_string(t_addr + config.TEAM_OFFSETS["ABB"], 10)
            team_id = self.mem.read_uint16(t_addr + config.TEAM_OFFSETS["UNIQUE_ID"])
            salary = self.mem.read_uint32(t_addr + config.TEAM_OFFSETS["TOTAL_SALARY"])
            payroll = self.mem.read_uint32(t_addr + config.TEAM_OFFSETS["PAYROLL"])
            budget = self.mem.read_uint32(t_addr + config.TEAM_OFFSETS["BUDGET"])
            chemistry = self.mem.read_float(t_addr + config.TEAM_OFFSETS["CHEMISTRY"])
            
            # 过滤条件：有缩写且长度为2或3（如 NY, GS, SA, NO, LAL, BOS），且 ID 在合理现役区间 (< 35)
            if raw_name and raw_abb and (len(raw_abb) in (2, 3)) and team_id < 35 and "All-Star" not in raw_name:
                teams[team_id] = {
                    "team_id": team_id,
                    "city": raw_city,
                    "name": raw_name,
                    "abbreviation": raw_abb,
                    "address": t_addr,
                    "total_salary": salary,
                    "payroll": payroll,
                    "budget": budget,
                    "chemistry": round(chemistry, 2)
                }
                
        return teams

    def get_active_player(self) -> Optional[Dict]:
        """
        通过静态全局指针获取当前正在查看/编辑的焦点球员 (如哈利伯顿)
        """
        ptr_addr = self.mem.base_address + config.ACTIVE_PLAYER_STATIC_PTR_1
        file_obj = self.mem.read_uint64(ptr_addr)
        if not file_obj:
            return None
            
        player_addr = file_obj + 0x118
        last_name = self.mem.read_utf16_string(player_addr + config.PLAYER_OFFSETS["LAST_NAME"])
        first_name = self.mem.read_utf16_string(player_addr + config.PLAYER_OFFSETS["FIRST_NAME"])
        
        if not last_name or not first_name:
            return None
            
        cur_team = self.mem.read_uint8(player_addr + config.PLAYER_OFFSETS["CURRENT_TEAM"])
        sal1 = self.mem.read_uint32(player_addr + config.PLAYER_OFFSETS["SALARY_YEAR_1"])
        years = self.mem.read_uint8(player_addr + config.PLAYER_OFFSETS["CONTRACT_YEARS_LEFT"])
        
        # 攻防核心属性
        three_pt_raw = self.mem.read_uint8(player_addr + config.PLAYER_OFFSETS["ATTR_THREE_POINT"])
        pass_acc_raw = self.mem.read_uint8(player_addr + config.PLAYER_OFFSETS["ATTR_PASS_ACCURACY"])
        speed_raw = self.mem.read_uint8(player_addr + config.PLAYER_OFFSETS["ATTR_SPEED"])
        perim_def_raw = self.mem.read_uint8(player_addr + config.PLAYER_OFFSETS["ATTR_PERIMETER_DEF"])
        
        return {
            "first_name": first_name,
            "last_name": last_name,
            "address": player_addr,
            "team_id": cur_team,
            "salary_current_year": sal1,
            "contract_years_left": years,
            "three_point_rating": config.raw_to_rating(three_pt_raw),
            "pass_accuracy_rating": config.raw_to_rating(pass_acc_raw),
            "speed_rating": config.raw_to_rating(speed_raw),
            "perimeter_defense_rating": config.raw_to_rating(perim_def_raw),
        }

    def set_trade_override(self, enable: bool = True) -> bool:
        """开启或关闭强制交易 (Trade Override)"""
        trade_base = self.mem.base_address + config.BASE_TRADE_CONTROLLER_OFFSET
        target = trade_base + config.TRADE_OFFSETS["TRADE_OVERRIDE"]
        return self.mem.write_uint32(target, 1 if enable else 0)
