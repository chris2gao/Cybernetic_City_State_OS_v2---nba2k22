# -*- coding: utf-8 -*-
"""
NBA 2K22 内存地址动态探活与自适应校准器 (Address Calibrator & Health Check)
解决游戏重启后 ASLR / 堆内存基址漂移问题：
1. 每次抓取前，自动校验缓存地址与游戏真实内存是否匹配 (快速探活 < 1ms)
2. 若游戏重启或地址漂移，自动启动全局特征码扫描并重新校准内存基址
3. 校验三大核心内存结构锚点：
   - 锚点 A: 30 支核心球队结构体数组 (通过 Pacers 签名与 0x1258 步长验证全部 30 队)
   - 锚点 B: 活跃/自建焦点球员指针 (通过静态指针与 0x118 偏移验证球员姓名)
   - 锚点 C: 全量历史球员池阵列 (通过乔丹 Slot 700 与 0x4F0 步长验证)
4. 将校准结果持久化到 database/runtime_memory_map.json，供自动化采集脚本零依赖调用
"""
import os
import sys
import json
import time
import struct
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
import config

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_FILE = os.path.join(PROJECT_DIR, "database", "runtime_memory_map.json")

class AddressCalibrator:
    def __init__(self, mem: Optional[GameMemory] = None):
        self.mem = mem or GameMemory()
        self.runtime_map = self._load_runtime_map()
        self.previous_pid = self.runtime_map.get("pid")
        self.process_changed = (
            self.previous_pid != self.mem.pid
            or self.runtime_map.get("module_base") != hex(self.mem.base_address)
        )
        if self.process_changed:
            # Heap addresses belong to one process instance. Even when an old
            # address happens to remain readable, discover the new pools again.
            for section, key in (
                ("teams", "pacers_base"),
                ("player_pool", "base_addr"),
                ("staff_pool", "base_addr"),
            ):
                self.runtime_map[section][key] = "0x0"
            self.runtime_map["active_player"].pop("current_addr", None)

    def _load_runtime_map(self) -> Dict:
        defaults = {
            "pid": self.mem.pid,
            "module_base": hex(self.mem.base_address),
            "teams": {
                "pacers_base": "0x7ff4e270fd10",
                "stride": hex(config.TEAM_STRUCT_STRIDE),
            },
            "active_player": {
                "static_ptr_offset": hex(config.ACTIVE_PLAYER_STATIC_PTR_1),
            },
            "player_pool": {
                "base_addr": "0x7ff4e6dfb2e8",
                "stride": "0x4f0",
            },
            "staff_pool": {
                "base_addr": "0x7ff4e2815f88",
                "stride": "0x160",
                "count": 0,
            },
        }
        if os.path.exists(MAP_FILE):
            try:
                with open(MAP_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if not isinstance(loaded, dict):
                    return defaults
                for key, default_value in defaults.items():
                    if isinstance(default_value, dict):
                        section = loaded.get(key)
                        if not isinstance(section, dict):
                            loaded[key] = default_value.copy()
                        else:
                            for subkey, subvalue in default_value.items():
                                section.setdefault(subkey, subvalue)
                    else:
                        loaded.setdefault(key, default_value)
                return loaded
            except Exception:
                pass
        return defaults

    def _cached_hex(self, section: str, key: str, default: int) -> int:
        try:
            value = self.runtime_map.get(section, {}).get(key, hex(default))
            return int(value, 16) if isinstance(value, str) else int(value)
        except (AttributeError, TypeError, ValueError):
            return default

    def _save_runtime_map(self, data: Dict):
        os.makedirs(os.path.dirname(MAP_FILE), exist_ok=True)
        temp_file = MAP_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_file, MAP_FILE)

    # -------------------------------------------------------------------------
    # 锚点 A: 球队数组快速验证与校准
    # -------------------------------------------------------------------------
    def check_and_calibrate_teams(self) -> Tuple[bool, int, Dict[int, Dict]]:
        """
        验证 30 支核心球队地址。
        返回: (is_healthy, pacers_base_addr, validated_teams_dict)
        """
        from source_extensions import roster_directory
        pool_ok, root = self.check_and_calibrate_player_pool()
        if not pool_ok:
            raise RuntimeError('Cannot resolve teams without a validated roster directory')
        roster_directory(self.mem, root)
        first = self.mem.require_uint64(root + 0x90)
        count = self.mem.require_uint64(root + 0x88)
        end = self.mem.require_uint64(root + 0xa0)
        if not 30 <= count <= 1000 or first + count * config.TEAM_STRUCT_STRIDE != end:
            raise RuntimeError('Invalid team array descriptor')
        teams = self._extract_teams_from_pacers(first)
        if set(teams) != config.CORE_TEAM_IDS:
            raise RuntimeError('Roster directory does not contain exactly the 30 NBA identities')
        pacers_base = teams[20]['address']
        self.runtime_map['teams']['pacers_base'] = hex(pacers_base)
        self._save_runtime_map(self.runtime_map)
        return True, pacers_base, teams

    def _extract_teams_from_pacers(self, pacers_base: int) -> Dict[int, Dict]:
        teams = {}
        for idx in range(-35, 35):
            t_addr = pacers_base + idx * config.TEAM_STRUCT_STRIDE
            raw_name = self.mem.read_utf16_string_safe(t_addr + config.TEAM_OFFSETS["TEAM_NAME"], 40)
            raw_city = self.mem.read_utf16_string_safe(t_addr + config.TEAM_OFFSETS["CITY"], 40)
            raw_abb = self.mem.read_utf16_string_safe(t_addr + config.TEAM_OFFSETS["ABB"], 10)
            team_id = self.mem.read_uint16_safe(t_addr + config.TEAM_OFFSETS["UNIQUE_ID"])

            if (
                raw_name and raw_city and raw_abb and team_id is not None
                and team_id in config.CORE_TEAM_IDS
                and len(raw_abb) in (2, 3)
                and "All-Star" not in raw_name
            ):
                if team_id in teams:
                    raise RuntimeError(
                        f"球队数组候选中出现重复核心球队 ID {team_id}；拒绝用覆盖后的结果校准。"
                    )
                teams[team_id] = {
                    "team_id": team_id,
                    "city": raw_city,
                    "name": raw_name,
                    "abbreviation": raw_abb,
                    "address": t_addr
                }
        return teams

    # -------------------------------------------------------------------------
    # 锚点 B: 活跃/焦点自建球员指针验证与校准
    # -------------------------------------------------------------------------
    def check_and_calibrate_active_player(self) -> Tuple[bool, Optional[Dict]]:
        """
        验证当前被选中的焦点/玩家球员；优先使用缓存指针偏移，失效时尝试备用静态偏移。
        """
        active_config = self.runtime_map.get("active_player", {})
        cached_offset = active_config.get("static_ptr_offset", hex(config.ACTIVE_PLAYER_STATIC_PTR_1))
        pointer_offsets = []
        for raw_offset in (cached_offset, hex(config.ACTIVE_PLAYER_STATIC_PTR_1), hex(config.ACTIVE_PLAYER_STATIC_PTR_2)):
            try:
                offset = int(raw_offset, 16) if isinstance(raw_offset, str) else int(raw_offset)
            except (TypeError, ValueError):
                continue
            if offset not in pointer_offsets:
                pointer_offsets.append(offset)

        for ptr_offset in pointer_offsets:
            file_obj = self.mem.read_uint64_safe(self.mem.base_address + ptr_offset)
            if not file_obj:
                continue
            player_addr = file_obj + 0x118
            last_name = self.mem.read_utf16_string_safe(player_addr + config.PLAYER_OFFSETS["LAST_NAME"], 30)
            first_name = self.mem.read_utf16_string_safe(player_addr + config.PLAYER_OFFSETS["FIRST_NAME"], 30)
            if not last_name or not first_name:
                continue

            try:
                face_id = self.mem.require_uint16(player_addr + 0x6C)
                team_pointer = self.mem.require_uint64(player_addr + config.PLAYER_OFFSETS['CURRENT_TEAM'])
                known_teams = self._extract_teams_from_pacers(self._cached_hex('teams', 'pacers_base', 0)) if team_pointer else {}
                team_id = next((tid for tid, team in known_teams.items() if team['address'] == team_pointer), None)
                salary = self.mem.require_uint32(player_addr + config.PLAYER_OFFSETS["SALARY_YEAR_1"]) & 0x7fffffff
                contract_raw = self.mem.require_uint8(player_addr + config.PLAYER_OFFSETS["CONTRACT_YEARS_LEFT"])
                ratings = {
                    "three_point_rating": config.raw_to_rating(self.mem.require_uint8(player_addr + config.PLAYER_OFFSETS["ATTR_THREE_POINT"])),
                    "pass_accuracy_rating": config.raw_to_rating(self.mem.require_uint8(player_addr + config.PLAYER_OFFSETS["ATTR_PASS_ACCURACY"])),
                    "speed_rating": config.raw_to_rating(self.mem.require_uint8(player_addr + config.PLAYER_OFFSETS["ATTR_SPEED"])),
                    "perimeter_defense_rating": config.raw_to_rating(self.mem.require_uint8(player_addr + config.PLAYER_OFFSETS["ATTR_PERIMETER_DEF"])),
                }
            except OSError:
                continue

            player_info = {
                "first_name": first_name,
                "last_name": last_name,
                "full_name": f"{first_name} {last_name}",
                "address": hex(player_addr),
                "face_id": face_id,
                "team_id": team_id,
                "salary_current_year": salary,
                "contract_years_left": config.extract_contract_years(contract_raw),
                **ratings,
            }
            self.runtime_map.setdefault("active_player", {})["static_ptr_offset"] = hex(ptr_offset)
            self.runtime_map["active_player"]["current_addr"] = hex(player_addr)
            self.runtime_map["active_player"]["player_name"] = player_info["full_name"]
            self._save_runtime_map(self.runtime_map)
            return True, player_info
        return False, None

    # -------------------------------------------------------------------------
    # 锚点 C: 全量历史球员池阵列验证与校准
    # -------------------------------------------------------------------------
    def check_and_calibrate_player_pool(self) -> Tuple[bool, int]:
        """
        验证全量 3,320 人历史球员池物理基址。
        通过 Slot 700 (迈克尔·乔丹) 与 Slot 1003 (哈基姆·奥拉朱旺) 进行双锚点毫秒级验证。
        """
        cached_pool = self._cached_hex("player_pool", "base_addr", 0x7FF4E6DFB2E8)
        stride = self._cached_hex("player_pool", "stride", 0x4F0)
        from source_extensions import roster_directory

        def valid_directory(root):
            try:
                roster_directory(self.mem, root)
                return True
            except (OSError, RuntimeError, ValueError):
                return False

        # 1. 快速双锚点验证 (Fast-Path Check < 1ms)
        slot_700 = cached_pool + 700 * stride
        j_last = self.mem.read_utf16_string_safe(slot_700, 20)
        j_first = self.mem.read_utf16_string_safe(slot_700 + 40, 20)
        cf_id = self.mem.read_uint16_safe(slot_700 + 0x6C)

        slot_1003 = cached_pool + 1003 * stride
        h_last = self.mem.read_utf16_string_safe(slot_1003, 20)
        h_cf = self.mem.read_uint16_safe(slot_1003 + 0x6C)

        if j_last == "Jordan" and j_first == "Michael" and cf_id == 1759 and h_last == "Olajuwon" and h_cf == 952 and valid_directory(cached_pool):
            return True, cached_pool

        # 2. 若不匹配，启动特征码扫描定位历史球员池
        print("[!] 历史球员池地址偏移，正在扫描迈克尔·乔丹 (Face ID 1759) 特征定位新池基址...")
        jordan_pattern = "Jordan".encode('utf-16le')
        matches = self.mem.scan_pattern(jordan_pattern, 0x7FF000000000, 0x7FFF00000000)
        new_pool_base = None
        validated_candidates = set()

        for match in matches:
            # 假定该 match 是 slot i 的 last_name (偏移 0)
            # 校验 offset 40 为 Michael, offset 0x6C 为 1759
            f_name = self.mem.read_utf16_string_safe(match + 40, 20)
            cf = self.mem.read_uint16_safe(match + 0x6C)
            if f_name == "Michael" and cf == 1759:
                # 反推基址：假定为 slot 700
                potential_base = match - 700 * stride
                # 校验 slot 1003 是否为 Hakeem Olajuwon (Face 952)
                h_slot = potential_base + 1003 * stride
                h_last = self.mem.read_utf16_string_safe(h_slot, 20)
                h_cf = self.mem.read_uint16_safe(h_slot + 0x6C)
                if h_last == "Olajuwon" and h_cf == 952 and valid_directory(potential_base):
                    validated_candidates.add(potential_base)

        if len(validated_candidates) > 1:
            raise RuntimeError('Multiple valid roster directories; cannot choose an active save from names alone')
        if validated_candidates:
            new_pool_base = validated_candidates.pop()

        if not new_pool_base:
            print("[WARN] 未能重新定位全量球员池基址，保持现有基址。")
            return False, cached_pool

        print(f"[+] 历史球员池基址校准成功！新基准地址: {hex(new_pool_base)} (Jordan & Olajuwon 双核验通过)")
        self.runtime_map["player_pool"]["base_addr"] = hex(new_pool_base)
        self._save_runtime_map(self.runtime_map)
        return True, new_pool_base

    # -------------------------------------------------------------------------
    # 锚点 D: 全量制服组与教练池阵列验证与校准
    # -------------------------------------------------------------------------
    def check_and_calibrate_staff_pool(self) -> Tuple[bool, int, int]:
        """
        验证全量 78 人制服组与教练池阵列物理基址。
        通过 Slot 0 (Doc Rivers) 与 Slot 18 (Rick Carlisle) 进行双锚点毫秒级验证。
        返回: (is_healthy, base_addr, valid_staff_count)
        """
        from source_extensions import roster_directory
        ok, root = self.check_and_calibrate_player_pool()
        if not ok:
            return False, 0, 0
        table = roster_directory(self.mem, root)['staff']
        base, count = table['address'] + 0x30, table['count']
        expected = ((0, 'Doc', 'Rivers'), (18, 'Rick', 'Carlisle'))
        for slot, first, last in expected:
            address = base + slot * 0x160
            if (self.mem.read_utf16_string_safe(address, 20) != first or
                    self.mem.read_utf16_string_safe(address + 40, 20) != last):
                return False, base, count
        self.runtime_map['staff_pool'] = {'base_addr': hex(base), 'stride': hex(0x160), 'count': count}
        self._save_runtime_map(self.runtime_map)
        return True, base, count

    # -------------------------------------------------------------------------
    # 完整自检与一键校准报告
    # -------------------------------------------------------------------------
    def run_full_calibration(self) -> Dict:
        """执行完整内存探活与矫正，并返回标准状态报告"""
        t0 = time.time()
        print("=" * 65)
        print("  NBA 2K22 内存动态探活与自适应地址校准检测")
        print("=" * 65)
        print(f"[*] 目标进程: {self.mem.process_name} (PID: {self.mem.pid})")
        print(f"[*] 模块基址: {hex(self.mem.base_address)}")
        if self.process_changed:
            print(f"[!] 进程实例变化 (缓存 PID {self.previous_pid} -> {self.mem.pid})，废弃旧堆地址并重新扫描。")

        teams_ok, pacers_base, teams = self.check_and_calibrate_teams()
        player_ok, active_player = self.check_and_calibrate_active_player()
        pool_ok, pool_base = self.check_and_calibrate_player_pool()
        staff_ok, staff_base, staff_count = self.check_and_calibrate_staff_pool()
        directory_counts = None
        if pool_ok:
            from source_extensions import roster_directory
            directory = roster_directory(self.mem, pool_base)
            directory_counts = {key: value['count'] for key, value in directory.items()}
            if directory['staff']['address'] + 0x30 != staff_base:
                staff_ok = False
            staff_count = directory['staff']['count']

        t1 = time.time()
        status = "HEALTHY" if (teams_ok and player_ok and pool_ok and staff_ok) else "PARTIAL_WARNING"

        report = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": round((t1 - t0) * 1000, 2),
            "status": status,
            "pid": self.mem.pid,
            "module_base": hex(self.mem.base_address),
            "previous_pid": self.previous_pid,
            "process_changed": self.process_changed,
            "directory_counts": directory_counts,
            "teams": {
                "valid": teams_ok,
                "count": len(teams),
                "pacers_base": hex(pacers_base),
                "stride": hex(config.TEAM_STRUCT_STRIDE)
            },
            "active_player": {
                "valid": player_ok,
                "data": active_player
            },
            "player_pool": {
                "valid": pool_ok,
                "base_addr": hex(pool_base),
                "stride": hex(0x4F0)
            },
            "staff_pool": {
                "valid": staff_ok,
                "base_addr": hex(staff_base),
                "stride": hex(0x160),
                "count": staff_count
            }
        }
        self.runtime_map["pid"] = self.mem.pid
        self.runtime_map["module_base"] = hex(self.mem.base_address)
        self.runtime_map["last_calibration"] = report
        self.runtime_map["staff_pool"] = {
            "base_addr": hex(staff_base),
            "stride": hex(0x160),
            "count": staff_count
        }
        self._save_runtime_map(self.runtime_map)

        print(f"\n[+] 内存探活与校准完成 (耗时: {report['elapsed_ms']} ms)！状态: [{status}]")
        print(f"    - 30 支核心球队: {'有效锁定 (' + str(len(teams)) + '队)' if teams_ok else '异常'}")
        print(f"    - 焦点球员指针: {'锁定 (' + active_player['full_name'] + ')' if player_ok else '未定位'}")
        print(f"    - 全量历史球员池: {'锁定 (Slot 700 Jordan & Slot 1003 Olajuwon 双核验通过)' if pool_ok else '异常'}")
        print(f"    - 制服组目录: {'锁定 (' + str(staff_count) + '个槽位，Doc Rivers & Rick Carlisle 验证通过)' if staff_ok else '异常'}")
        print(f"[*] 校准结果已落盘至: {MAP_FILE}\n")
        return report

if __name__ == "__main__":
    calibrator = AddressCalibrator()
    calibrator.run_full_calibration()
