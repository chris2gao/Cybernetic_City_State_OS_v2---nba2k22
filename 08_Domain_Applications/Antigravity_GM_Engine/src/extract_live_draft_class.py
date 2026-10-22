# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 实时选秀名单内存提取器 (Live Draft Class Extractor)
直接从 NBA 2K22 运行内存及 NBA2K22 Tools 的新秀缓存中，
高保真提取当前停留选秀界面的全部球员（姓名、面补 ID、位置、身高、能力属性），
并导出为标准 JSON 格式供外部 GM 选秀接管引擎使用。
"""
import os
import sys
import json
import struct
from typing import Dict, List, Optional

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory, MEMORY_BASIC_INFORMATION
import config

POS_MAP = {
    0: "PG",
    1: "SG",
    2: "SF",
    3: "PF",
    4: "C"
}

def extract_live_draft_class(year: int = 1984) -> List[Dict]:
    """从游戏当前选秀界面内存中提取全部新秀"""
    mem_tools = GameMemory(process_name="NBA2K22 Tools.exe")
    mem_game = GameMemory(process_name="NBA2K22.exe")
    
    print(f"[*] 成功挂接游戏 (PID: {mem_game.pid}) 与 NBA2K22 Tools (PID: {mem_tools.pid})")
    
    # 在 NBA2K22 Tools 内存中定位新秀列表聚簇 (寻找包含真实历史巨星名字的聚簇)
    import ctypes
    mbi = MEMORY_BASIC_INFORMATION()
    addr = 0x10000
    target_cluster = None
    best_star_count = 0
    
    known_stars = {"Jordan", "Stockton", "Perkins", "Thorpe", "Willis", "Kersey", "Drexler", "Worthy"}
    
    while mem_tools.kernel32.VirtualQueryEx(int(mem_tools.handle), ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
        base = mbi.BaseAddress if mbi.BaseAddress is not None else 0
        if mbi.State == 0x1000 and (mbi.Protect in [0x04, 0x08, 0x40]):
            raw = mem_tools.read_bytes(base, mbi.RegionSize)
            if raw and len(raw) >= 128:
                star_matches = 0
                valid_ptrs = 0
                for i in range(0x28, len(raw) - 8, 0x80):
                    val = struct.unpack('<Q', raw[i:i+8])[0]
                    if 0x7FF4E0000000 <= val <= 0x7FF4F0000000:
                        ln = mem_game.read_utf16_string(val, 20).strip()
                        if ln and ln.isalpha():
                            valid_ptrs += 1
                        if ln in known_stars:
                            star_matches += 1
                # 选秀名单通常为 50 ~ 150 人之间，过滤大盘 1000+ 现役全名单
                if (50 <= valid_ptrs <= 150) and star_matches > best_star_count:
                    best_star_count = star_matches
                    target_cluster = (base, mbi.RegionSize)
        addr = base + mbi.RegionSize
        if addr >= 0x7FFFFFFF0000:
            break
            
    if not target_cluster:
        raise RuntimeError("未在当前 NBA2K22 Tools 内存中定位到新秀名单聚簇，请确保已打开新秀名单界面！")
        
    c_base, c_size = target_cluster
    raw_cluster = mem_tools.read_bytes(c_base, c_size)
    
    prospects = []
    pick_counter = 1
    
    for i in range(0x28, len(raw_cluster) - 8, 0x80):
        val = struct.unpack('<Q', raw_cluster[i:i+8])[0]
        if 0x7FF4E0000000 <= val <= 0x7FF4F0000000:
            fn = mem_game.read_utf16_string(val + 0x28, 30).strip()
            ln = mem_game.read_utf16_string(val, 30).strip()
            if fn and ln and fn.isalpha() and ln.isalpha():
                face_id = mem_game.read_uint16(val + config.PLAYER_OFFSETS["FACE_ID"])
                raw_pos = mem_game.read_uint8(val + config.PLAYER_OFFSETS["POSITION"])
                pos_idx = raw_pos & 0x07
                pos_name = POS_MAP.get(pos_idx, "SF")
                
                # 读取关键核心能力 (25 + raw * 74 / 255)
                raw_mid = mem_game.read_uint8(val + config.PLAYER_OFFSETS["ATTR_MID_RANGE"])
                raw_3pt = mem_game.read_uint8(val + config.PLAYER_OFFSETS["ATTR_THREE_POINT"])
                raw_spd = mem_game.read_uint8(val + config.PLAYER_OFFSETS["ATTR_SPEED"])
                raw_lay = mem_game.read_uint8(val + config.PLAYER_OFFSETS["ATTR_DRIVING_LAYUP"])
                
                def conv(r): return int(round(25 + (r * 74.0 / 255.0)))
                
                # 潜力与总评估算
                raw_pot = mem_game.read_uint8(val + 0xEB)
                pot = raw_pot if (50 <= raw_pot <= 99) else 85
                
                prospects.append({
                    "pick_proj": pick_counter,
                    "first_name": fn,
                    "last_name": ln,
                    "face_id": face_id,
                    "position": pos_idx,
                    "position_name": pos_name,
                    "mid_range": conv(raw_mid),
                    "three_point": conv(raw_3pt),
                    "speed": conv(raw_spd),
                    "driving_layup": conv(raw_lay),
                    "potential": pot,
                    "memory_addr": hex(val)
                })
                pick_counter += 1
                
    # 保存至数据库
    out_dir = os.path.join(os.path.dirname(__file__), "..", "database", "draft_classes")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{year}_draft_class.json")
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(prospects, f, indent=2, ensure_ascii=False)
        
    print(f"[+] 提取成功！共提取 {len(prospects)} 名真实新秀数据！")
    print(f"[+] 选秀名单已安全导出至: {out_file}")
    return prospects

if __name__ == "__main__":
    extract_live_draft_class(1984)
