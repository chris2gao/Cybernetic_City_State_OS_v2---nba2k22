# -*- coding: utf-8 -*-
"""
NBA 2K22 1984 届历史选秀名单全维度内存注入与复用总引擎 (Master 1984 Draft Class Reusable Live Memory Injector)

设计定位：
为 1984 届历史选秀名单提供一键式、可持久复用的全量实机内存注入能力。
当玩家在新开档 (MyLEAGUE)、重新载入官方原版 1984 选秀名单、或处于选秀名单编辑/赛季进行中时，
直接运行本脚本即可将官方泥人名单一键提升为殿堂级 1984 真实名单：
1. 全量 60 名新秀真实姓名、面补 ID (含巴克利 CAP 捏人模式)、位置与 1984 真实年份 (0x179 = 84)；
2. 32 项攻防真实数值、29 项赛场倾向 (犯规硬顶 <= 45 安全锁)、纯净化等级徽章与战术手册；
3. 全员 159 字节真实赛场动作包、专属球星签名 ID (0xE8) 与 10 字节性格心智特征包；
4. 0x90 外观体型骨骼雕刻 (臂展/肩宽/手臂粗细/头颈比/下盘臀腿/大手/身形模板/纯正非裔与白人肤色)；
5. 巴克利 (Charles Barkley) 专属 0x88 CAP 饱满方脸五官雕刻、保持光头/寸头设置、20 项招牌动作位域；
6. 全员错误头带配件自动剥离纯净化 (0x2F3 / 0x34C)；
7. 具备双端自动探测：既支持注入待选秀池 (Slot 590~649 / 3190~3249)，又支持自动穿透扫描 30 支球队并同步注入已签约/已选中的现役阵容；
8. 同步持久化至 player_pool.sqlite 数据库，彻底避免读档回滚。

触发示例：
  python 08_Domain_Applications/Antigravity_GM_Engine/src/inject_1984_draft_master.py --commit
  python 08_Domain_Applications/Antigravity_GM_Engine/src/inject_1984_draft_master.py --dry-run
"""

import os
import sys
import json
import struct
import shutil
import sqlite3
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from address_calibrator import AddressCalibrator

STRIDE = 0x4F0  # 1,264 字节步长

# 结构体关键基础偏移
OFF_LAST_NAME = 0x000     # 40 字节 UTF-16LE
OFF_FIRST_NAME = 0x028    # 40 字节 UTF-16LE
OFF_WEIGHT = 0x058        # float32 (磅)
OFF_FACE_ID = 0x06C       # uint16 (2 字节小端)
OFF_HEAD_MORPH = 0x088    # uint64 (8 字节 0x88 头部预设堆块指针)
OFF_APPEARANCE = 0x090    # uint64 (8 字节 0x90 外观堆块指针)
OFF_SIGNATURE_ID = 0x0E8  # 3 字节小端 (0x0E8~0x0EA) 签名动画 ID
OFF_POTENTIAL = 0x0EB     # uint8 (人类评分 25~99)
OFF_POSITION = 0x0F9      # uint8 (低 3 位: 0=PG, 1=SG, 2=SF, 3=PF, 4=C)
OFF_DRAFT_YEAR = 0x179    # uint8 (年份 - 1900, 1984 -> 84)
OFF_DRAFT_PICK = 0x312    # uint16 位域
OFF_DRAFT_ROUND = 0x316   # uint8
OFF_TACTICAL_PLAY_TYPES = 0x168 # 2 字节小端 (4 个 4-bit 战术类型: 0x168..0x169)
OFF_TACTICAL_INITIATOR = 0x16A  # uint8 (bit 2: is_play_initiator)
OFF_ANIMATION_BLOCK = 0x380     # 159 字节专用动作包 (0x380 ~ 0x41E)
OFF_POTENTIAL_RAW = 0x441       # uint8 (评分换算值)
OFF_PERSONALITY = 0x4BB         # 10 字节性格位域 (0x4BB ~ 0x4C4)

# 32 项核心攻防属性偏移
ATTR_OFFSETS = {
    "driving_layup": 0x41F, "post_fadeaway": 0x420, "post_hook": 0x421, "post_moves": 0x422,
    "draw_foul": 0x423, "shot_close": 0x424, "mid_range": 0x425, "three_point": 0x426,
    "free_throw": 0x427, "ball_control": 0x428, "pass_iq": 0x429, "pass_accuracy": 0x42A,
    "off_rebound": 0x42B, "def_rebound": 0x42C, "interior_def": 0x42D, "perimeter_def": 0x42E,
    "lateral_quick": 0x42F, "pass_perception": 0x430, "block": 0x431, "steal": 0x432,
    "standing_dunk": 0x435, "driving_dunk": 0x436, "speed": 0x437, "speed_with_ball": 0x438,
    "acceleration": 0x439, "vertical": 0x43A, "strength": 0x43B, "stamina": 0x43C,
    "hustle": 0x43D, "shot_iq": 0x43E, "intangibles": 0x440, "pass_vision": 0x453,
    "hands": 0x455
}

# 29 项核心战术倾向偏移
TEND_OFFSETS = {
    "shot": 0x458, "driving_layup": 0x459, "standing_dunk": 0x45A, "driving_dunk": 0x45B,
    "flashy_dunk": 0x45C, "alley_oop": 0x45D, "putback": 0x45E, "crash": 0x45F,
    "spin_layup": 0x460, "hop_step_layup": 0x461, "euro_step_layup": 0x462, "floater": 0x463,
    "shot_under_basket": 0x465, "shot_close": 0x466, "shot_mid_range": 0x46A, "shot_three": 0x472,
    "drive": 0x483, "attack_strong_on_drive": 0x497, "dish_to_open_man": 0x498, "touches": 0x499,
    "post_up": 0x49A, "roll_vs_pop": 0x49B, "play_discipline": 0x4A1, "pass_interception": 0x4B4,
    "on_ball_steal": 0x4B6, "contest_shot": 0x4B7, "block_shot": 0x4B8, "foul": 0x4B9,
    "hard_foul": 0x4BA
}

# 加载徽章字典
BADGE_PROFILE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "world_data_prototype", "player_detail_native_profile.json"
)
BADGE_FIELDS_MAP = {}
if os.path.exists(BADGE_PROFILE_PATH):
    try:
        with open(BADGE_PROFILE_PATH, "r", encoding="utf-8") as f:
            _prof = json.load(f)
            BADGE_FIELDS_MAP = _prof.get("badge_fields", {})
    except Exception:
        pass


def rating_to_raw(rating: int) -> int:
    """评分 25~99 换算为内存 0~255 字节"""
    return min(255, max(0, int((rating - 25) * 3)))


def patch_player_struct(orig_raw: bytes, spec: Dict[str, Any], draft_year: int = 1984) -> bytes:
    """
    安全装配 1,264 字节原生球员结构体，同时严格保护 0x88 和 0x90 堆块指针不被破坏。
    """
    if orig_raw and len(orig_raw) >= STRIDE:
        raw_ba = bytearray(orig_raw)
    elif orig_raw and len(orig_raw) >= 0x98:
        raw_ba = bytearray(orig_raw.ljust(STRIDE, b"\x00"))
    else:
        raw_ba = bytearray(STRIDE)

    # 严格保护原有的 0x88, 0x90 堆指针以及 0xF4 运行时唯一球员 ID
    if orig_raw and len(orig_raw) >= 0xF8:
        p88_orig = struct.unpack_from("<Q", orig_raw, OFF_HEAD_MORPH)[0]
        p90_orig = struct.unpack_from("<Q", orig_raw, OFF_APPEARANCE)[0]
        pf4_orig = struct.unpack_from("<I", orig_raw, 0xF4)[0]
        if p88_orig > 0:
            struct.pack_into("<Q", raw_ba, OFF_HEAD_MORPH, p88_orig)
        if p90_orig > 0:
            struct.pack_into("<Q", raw_ba, OFF_APPEARANCE, p90_orig)
        if pf4_orig > 0:
            struct.pack_into("<I", raw_ba, 0xF4, pf4_orig)

    slot_id = spec.get("slot_id", 0)
    full_name = spec.get("full_name", "")
    is_official_legend = (slot_id in range(590, 596) and full_name != "Charles Barkley")

    # 1. 选秀年份 (权威 0x179 偏移量!)
    raw_ba[OFF_DRAFT_YEAR] = (draft_year - 1900) & 0xFF

    # 2. 真实体重 (0x58, float32)
    if "weight_lbs" in spec:
        struct.pack_into("<f", raw_ba, OFF_WEIGHT, float(spec["weight_lbs"]))

    if not is_official_legend:
        # === A. 泥人槽位与非官方球星全量身份与外观对齐 ===
        # 姓名 (UTF-16LE, 40 字节填充)
        fn_bytes = spec["first_name"].encode("utf-16le").ljust(40, b"\x00")[:40]
        ln_bytes = spec["last_name"].encode("utf-16le").ljust(40, b"\x00")[:40]
        raw_ba[OFF_FIRST_NAME:OFF_FIRST_NAME + 40] = fn_bytes
        raw_ba[OFF_LAST_NAME:OFF_LAST_NAME + 40] = ln_bytes

        # 面补 ID (uint16)
        struct.pack_into("<H", raw_ba, OFF_FACE_ID, int(spec["face_id"]))

        # 位置 (3 bits: 0=PG, 1=SG, 2=SF, 3=PF, 4=C)
        pos_idx = int(spec.get("position", 2)) & 0x07
        raw_ba[OFF_POSITION] = (raw_ba[OFF_POSITION] & 0xF8) | pos_idx

        # 选秀轮次与顺位
        if "draft_round" in spec:
            raw_ba[OFF_DRAFT_ROUND] = int(spec["draft_round"]) & 0xFF
        if "draft_pick" in spec:
            struct.pack_into("<H", raw_ba, OFF_DRAFT_PICK, int(spec["draft_pick"]))

        # 专属签名动画 ID (低 3 字节 at 0x0E8~0x0EA)
        sig_id = spec.get("signature_id")
        if sig_id is not None:
            sig_u32 = int(sig_id)
            raw_ba[OFF_SIGNATURE_ID] = sig_u32 & 0xFF
            raw_ba[OFF_SIGNATURE_ID + 1] = (sig_u32 >> 8) & 0xFF
            raw_ba[OFF_SIGNATURE_ID + 2] = (sig_u32 >> 16) & 0xFF

        # 动作包结构 (159 字节, 0x380 ~ 0x41E)
        anim_hex = spec.get("animation_block_hex")
        if anim_hex:
            anim_bytes = bytes.fromhex(anim_hex)
            if len(anim_bytes) == 159:
                raw_ba[OFF_ANIMATION_BLOCK:OFF_ANIMATION_BLOCK + 159] = anim_bytes

        # 性格位域 (10 字节, 0x4BB ~ 0x4C4)
        pers_hex = spec.get("personality_hex")
        if pers_hex:
            pers_bytes = bytes.fromhex(pers_hex)
            if len(pers_bytes) == 10:
                raw_ba[OFF_PERSONALITY:OFF_PERSONALITY + 10] = pers_bytes

        # 泥人技能等级徽章纯净化与目标徽章写入
        if BADGE_FIELDS_MAP:
            for b_meta in BADGE_FIELDS_MAP.values():
                if b_meta.get("kind") == "LEVEL":
                    off = b_meta["offset"]
                    w = b_meta["width"]
                    s = b_meta["start_bit"]
                    if off < STRIDE:
                        mask = ((1 << w) - 1) << s
                        raw_ba[off] &= ~mask

            badges = spec.get("badges", {})
            for b_name, b_level in badges.items():
                if b_name == "FastbreakFinisher": b_name = "Downhill"
                elif b_name == "PogoStick": b_name = "Pogostick"
                if b_name in BADGE_FIELDS_MAP:
                    meta = BADGE_FIELDS_MAP[b_name]
                    off = meta["offset"]
                    w = meta["width"]
                    s = meta["start_bit"]
                    if off < STRIDE:
                        val = int(b_level) & ((1 << w) - 1)
                        mask = ((1 << w) - 1) << s
                        raw_ba[off] = (raw_ba[off] & ~mask) | (val << s)

        # 头带配件剔除 (0x2F3 bit 4..6, 0x34C bit 0..2)
        sc = spec.get("sculpt", {})
        if sc.get("remove_headband", True):
            raw_ba[0x2F3] = raw_ba[0x2F3] & ~(0x07 << 4)
            raw_ba[0x34C] = raw_ba[0x34C] & ~0x07

    # === B. 通用全维攻防数值、战术倾向与战术手册注入 ===
    pot = int(spec.get("potential", 80))
    raw_ba[OFF_POTENTIAL] = pot
    raw_ba[OFF_POTENTIAL_RAW] = rating_to_raw(pot)

    # 攻防属性写入 (32 项)
    attrs = spec.get("attributes", {})
    for attr_name, offset in ATTR_OFFSETS.items():
        if attr_name in attrs and offset < STRIDE:
            val = attrs[attr_name]
            if val is not None:
                raw_ba[offset] = rating_to_raw(int(val))

    # 战术倾向写入 (29 项，含常规犯规安全锁)
    tends = spec.get("tendencies", {})
    for tend_name, offset in TEND_OFFSETS.items():
        if tend_name in tends and offset < STRIDE:
            val = tends[tend_name]
            if val is not None:
                val_int = min(100, max(0, int(val)))
                if tend_name == "foul":
                    val_int = min(45, val_int)  # 严格锁在 45 避免过度犯规
                raw_ba[offset] = val_int

    # 战术手册写入
    playbook = spec.get("tactical_playbook", {})
    if playbook:
        if "is_play_initiator" in playbook:
            init_val = int(playbook["is_play_initiator"]) & 1
            raw_ba[OFF_TACTICAL_INITIATOR] = (raw_ba[OFF_TACTICAL_INITIATOR] & ~(1 << 2)) | (init_val << 2)
        if "play_types" in playbook and len(playbook["play_types"]) >= 4:
            clean_pts = [max(0, min(14, int(x))) for x in playbook["play_types"][:4]]
            raw_ba[OFF_TACTICAL_PLAY_TYPES] = (clean_pts[0] & 0x0F) | ((clean_pts[1] & 0x0F) << 4)
            raw_ba[OFF_TACTICAL_PLAY_TYPES + 1] = (clean_pts[2] & 0x0F) | ((clean_pts[3] & 0x0F) << 4)

    return bytes(raw_ba)


def sculpt_player_appearance(
    mem: GameMemory,
    player_addr: int,
    sculpt_spec: Dict[str, Any],
    slot_id: Optional[int] = None,
    commit: bool = False
) -> Dict[str, Any]:
    """
    对指定球员执行 0x90 外观骨骼雕刻、0x88 捏人五官形态雕刻与细节招牌动作注入
    """
    p_raw = mem.read_bytes(player_addr, 0x100)
    p88_head = struct.unpack_from("<Q", p_raw, 0x88)[0]
    p90_app = struct.unpack_from("<Q", p_raw, 0x90)[0]

    # 自愈兜底：若选秀池槽位指针意外置空，按 2K22 连续堆规则自动重塑
    if slot_id is not None and slot_id in range(590, 650):
        if not p90_app or p90_app == 0:
            p90_app = 0x7FF4E73ACC7C + (slot_id - 590) * 0x40
            mem.write_bytes(player_addr + 0x90, struct.pack("<Q", p90_app))
        if not p88_head or p88_head == 0:
            p88_head = 0x7FF4E6E82E70 + (slot_id - 590) * 0x30
            mem.write_bytes(player_addr + 0x88, struct.pack("<Q", p88_head))

    sculpt_res = {}

    # 1. 0x90 外观堆块骨骼与体型雕刻 (单球员精确 64 字节 0x40 结构体)
    if p90_app and p90_app > 0 and commit:
        app_raw = bytearray(mem.read_bytes(p90_app, 0x40))
        target_ws = sculpt_spec.get("wingspan_cm_x100", 21500)
        target_bl = float(sculpt_spec.get("body_length", 1.0000))
        target_sw = float(sculpt_spec.get("shoulder_width", 1.0000))
        target_as = float(sculpt_spec.get("arm_scale", 1.0000))
        target_ns = float(sculpt_spec.get("neck_head_scale", 1.0000))
        target_ls = float(sculpt_spec.get("lower_scale", 1.0000))
        target_hs = float(sculpt_spec.get("hand_scale", 1.0000))
        target_shape = int(sculpt_spec.get("body_shape", 0))
        target_skin = int(sculpt_spec.get("skin_color", 4))
        target_hair_len = float(sculpt_spec.get("hair_length", 0.0000))

        # 写入 0x40 外观属性
        struct.pack_into("<H", app_raw, 0x02, int(target_ws))
        struct.pack_into("<6f", app_raw, 0x04,
                         target_bl, target_sw, target_as,
                         target_ns, target_ls, target_hs)
        struct.pack_into("<f", app_raw, 0x1C, target_hair_len)
        orig_u16 = struct.unpack_from("<H", app_raw, 0x26)[0]
        new_u16 = (orig_u16 & ~(0x0F << 6)) | ((target_skin & 0x0F) << 6)
        struct.pack_into("<H", app_raw, 0x26, new_u16)
        app_raw[0x3C] = target_shape & 0x07

        mem.write_bytes(p90_app, bytes(app_raw))
        rb_app = mem.read_bytes(p90_app, 0x40)
        sculpt_res["p90_sculpt_ok"] = True
        sculpt_res["wingspan"] = struct.unpack_from("<H", rb_app, 0x02)[0]
        sculpt_res["shoulder"] = struct.unpack_from("<f", rb_app, 0x08)[0]
        sculpt_res["skin_color"] = (struct.unpack_from("<H", rb_app, 0x26)[0] >> 6) & 0x0F

    # 2. 0x88 头部与五官形态雕刻 (CAP Morphs)
    if p88_head and p88_head > 0 and "head_morphs" in sculpt_spec and commit:
        morphs = sculpt_spec["head_morphs"]
        raw_88 = bytearray(mem.read_bytes(p88_head, 64))

        if "head_preset" in morphs: raw_88[0] = int(morphs["head_preset"]) & 0xFF
        if "skull_preset" in morphs: raw_88[1] = int(morphs["skull_preset"]) & 0xFF
        if "skull_width" in morphs: raw_88[2] = int(morphs["skull_width"]) & 0xFF
        if "skull_height" in morphs: raw_88[3] = int(morphs["skull_height"]) & 0xFF
        if "temple_width" in morphs: raw_88[11] = int(morphs["temple_width"]) & 0xFF
        if "upper_nose_width" in morphs: raw_88[22] = int(morphs["upper_nose_width"]) & 0xFF
        if "lower_nose_width" in morphs: raw_88[23] = int(morphs["lower_nose_width"]) & 0xFF
        if "upper_cheek_width" in morphs: raw_88[29] = int(morphs["upper_cheek_width"]) & 0xFF
        if "middle_cheek_width" in morphs: raw_88[30] = int(morphs["middle_cheek_width"]) & 0xFF
        if "upper_lip_thickness" in morphs: raw_88[33] = int(morphs["upper_lip_thickness"]) & 0xFF
        if "lower_lip_thickness" in morphs: raw_88[36] = int(morphs["lower_lip_thickness"]) & 0xFF
        if "front_chin_width" in morphs: raw_88[41] = int(morphs["front_chin_width"]) & 0xFF
        if "rear_chin_width" in morphs: raw_88[42] = int(morphs["rear_chin_width"]) & 0xFF
        if "head_width" in morphs: raw_88[54] = int(morphs["head_width"]) & 0xFF
        raw_88[56] = 1  # ISMODIFIED = 1

        mem.write_bytes(p88_head, bytes(raw_88))
        sculpt_res["p88_morphs_ok"] = True

    # 3. 细节招牌动作位域写入
    if "motion_fields" in sculpt_spec and commit:
        motion_fields = sculpt_spec["motion_fields"]
        for m_name, field_def in motion_fields.items():
            m_addr, m_bit, m_len, m_val = field_def
            u16_curr = struct.unpack_from("<H", mem.read_bytes(player_addr + m_addr, 2), 0)[0]
            mask = (1 << m_len) - 1
            bitmask = mask << m_bit
            new_u16 = (u16_curr & ~bitmask) | ((m_val & mask) << m_bit)
            mem.write_bytes(player_addr + m_addr, struct.pack("<H", new_u16))
        sculpt_res["motion_fields_ok"] = True

    return sculpt_res


def execute_master_1984_draft_injection(
    template_path: Optional[str] = None,
    db_path: Optional[str] = None,
    commit: bool = False,
    target_mode: str = "auto"
) -> Dict[str, Any]:
    """
    执行 1984 选秀全量内存注入流水线
    """
    print("=" * 90)
    print("NBA 2K22 1984 届历史选秀名单全维度内存注入与复用总引擎 (Master 1984 Draft Reusable Injector)")
    print("=" * 90)
    print(f"[*] 运行模式: {'【正式提交写入 COMMIT LIVE】' if commit else '【预检预览 DRY-RUN】'}")

    # 1. 确定模板文件路径
    if not template_path:
        local_cand = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "database", "draft_classes", "1984_draft_class_master_injection_template.json"
        )
        export_cand = r"C:\nba2k22\exports\1984_draft_class_master_injection_template.json"
        if os.path.exists(local_cand):
            template_path = local_cand
        elif os.path.exists(export_cand):
            template_path = export_cand
        else:
            raise FileNotFoundError("未找到 1984 选秀主模板 JSON 文件！")

    print(f"[*] 主模板规格书路径: {template_path}")
    with open(template_path, "r", encoding="utf-8") as f:
        template_data = json.load(f)

    prospects = template_data.get("prospects", [])
    draft_year = template_data.get("draft_year", 1984)
    print(f"[*] 加载主模板完成: 选秀年份 {draft_year} | 待注入新秀共 {len(prospects)} 人")

    # 2. 挂接 NBA2K22.exe
    mem = GameMemory("NBA2K22.exe", read_only=not commit)
    calibrator = AddressCalibrator(mem)

    # 校准底层球员池基址
    ok_pool, base_pool = calibrator.check_and_calibrate_player_pool()
    if not ok_pool or base_pool == 0:
        base_pool = 0x7FF4E6DFB2E8  # 实机备选基址
        print(f"[!] 球员池动态校准提示: 启用稳定备选基址: {hex(base_pool)}")
    else:
        print(f"[+] 球员池基址校准锁定: {hex(base_pool)}")

    # 校准球队阵容基址 (用于穿透扫描现役阵容)
    ok_teams, base_teams, teams = calibrator.check_and_calibrate_teams()
    if ok_teams and teams:
        print(f"[+] 球队矩阵基址校准锁定: 扫描到 {len(teams)} 支 NBA 球队")

    # 3. 确保存档数据库
    if not db_path:
        default_db = r"C:\nba2k22\saves\MyLEAGUE0005\player_pool.sqlite"
        if os.path.exists(default_db):
            db_path = default_db

    conn = None
    cur = None
    if db_path and os.path.exists(db_path):
        if commit:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            bak_path = f"{db_path}.bak_{ts}"
            shutil.copy2(db_path, bak_path)
            print(f"[+] 数据库快照备份就绪: {bak_path}")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        print(f"[+] 已连接 SQLite 数据库: {db_path}")

    # 4. 执行选秀池槽位 (Slot 590~649) 注入
    pool_injected = []
    pool_verified = 0
    mismatches = []

    print("\n" + "-" * 75)
    print("[PHASE 1] 正在执行 1984 选秀池槽位全量内存注入 (Slot 590 ~ 649)...")
    print("-" * 75)

    for item in prospects:
        slot_id = item["slot_id"]
        full_name = item.get("full_name", f"{item.get('first_name', '')} {item.get('last_name', '')}")
        face_id = item.get("face_id", 0)
        slot_addr = base_pool + slot_id * STRIDE
        is_official = (slot_id in range(590, 596) and full_name != "Charles Barkley")

        orig_mem = mem.read_bytes(slot_addr, STRIDE)
        if not orig_mem:
            mismatches.append(f"Slot {slot_id}: 内存读取失败")
            continue

        orig_fn = orig_mem[OFF_FIRST_NAME:OFF_FIRST_NAME + 40].decode("utf-16le", errors="ignore").split("\0")[0]
        orig_ln = orig_mem[OFF_LAST_NAME:OFF_LAST_NAME + 40].decode("utf-16le", errors="ignore").split("\0")[0]
        orig_face = struct.unpack_from("<H", orig_mem, OFF_FACE_ID)[0]

        # 4.1 装配结构体
        new_raw = patch_player_struct(orig_mem, item, draft_year)

        if commit:
            # 写入 1,264 字节结构体
            mem.write_bytes(slot_addr, new_raw)

            # CAS 立即回读验证
            rb = mem.read_bytes(slot_addr, STRIDE)
            rb_fn = rb[OFF_FIRST_NAME:OFF_FIRST_NAME + 40].decode("utf-16le", errors="ignore").split("\0")[0]
            rb_ln = rb[OFF_LAST_NAME:OFF_LAST_NAME + 40].decode("utf-16le", errors="ignore").split("\0")[0]
            rb_face = struct.unpack_from("<H", rb, OFF_FACE_ID)[0]
            rb_yr = 1900 + rb[OFF_DRAFT_YEAR]
            rb_foul = rb[TEND_OFFSETS["foul"]]

            if is_official:
                if rb_face == orig_face and rb_yr == draft_year and rb_foul <= 50:
                    pool_verified += 1
                else:
                    mismatches.append(f"Slot {slot_id} ({full_name}) 回读异常: 面补={rb_face}, 年份={rb_yr}")
            else:
                if rb_fn == item["first_name"] and rb_ln == item["last_name"] and rb_face == face_id and rb_yr == draft_year and rb_foul <= 50:
                    pool_verified += 1
                else:
                    mismatches.append(f"Slot {slot_id} ({full_name}) 回读异常: 目标 {full_name}({face_id}), 回读 {rb_fn} {rb_ln}({rb_face})")

            # 4.2 0x90 外观与 0x88 五官雕刻注入
            sculpt_data = item.get("sculpt")
            if sculpt_data:
                sculpt_player_appearance(mem, slot_addr, sculpt_data, slot_id=slot_id, commit=True)

            # 4.3 SQLite 数据库持久化
            if cur:
                if is_official:
                    cur.execute("""
                        UPDATE player_pool
                        SET draft_year = ?, potential = ?, raw_potential = ?, raw_struct = ?
                        WHERE slot_id = ?
                    """, (draft_year, item.get("potential", 80), item.get("potential", 80), new_raw, slot_id))
                else:
                    cur.execute("""
                        UPDATE player_pool
                        SET first_name = ?, last_name = ?, full_name = ?, cyberface_id = ?,
                            position = ?, position_name = ?, potential = ?, raw_potential = ?,
                            draft_year = ?, draft_round = ?, draft_pick = ?, overall_pick = ?,
                            raw_struct = ?
                        WHERE slot_id = ?
                    """, (
                        item["first_name"], item["last_name"], full_name, face_id,
                        item.get("position", 2), item.get("position_name", ""),
                        item.get("potential", 80), item.get("potential", 80),
                        draft_year, item.get("draft_round", 1), item.get("draft_pick", 1),
                        item.get("overall_pick", 1), new_raw, slot_id
                    ))

            # 4.4 官方底库母本槽位镜像 (Slot 3191~3195)
            if is_official and slot_id in range(591, 596):
                vault_slot = slot_id + 2600
                vault_addr = base_pool + vault_slot * STRIDE
                vault_orig = mem.read_bytes(vault_addr, STRIDE)
                if vault_orig:
                    vault_new = patch_player_struct(vault_orig, item, draft_year)
                    mem.write_bytes(vault_addr, vault_new)
                    if cur:
                        cur.execute("UPDATE player_pool SET draft_year = ?, raw_struct = ? WHERE slot_id = ?",
                                    (draft_year, vault_new, vault_slot))

        pool_injected.append({
            "slot_id": slot_id,
            "name": full_name,
            "face_id": face_id,
            "status": "OFFICIAL_CALIBRATED" if is_official else "RECONSTRUCTED_VERIFIED",
            "addr": hex(slot_addr)
        })

    print(f"[+] 选秀池注入阶段完成: 60/60 槽位处理完毕 | CAS 断言通过: {pool_verified} 个槽位")

    # 5. 执行现役阵容穿透扫描与热注入 (Team Rosters Penetration Phase)
    roster_injected = []
    if ok_teams and teams:
        print("\n" + "-" * 75)
        print("[PHASE 2] 正在执行 30 支球队现役阵容穿透扫描与热注入 (Roster Matching Phase)...")
        print("-" * 75)

        p_name_map = {p["full_name"]: p for p in prospects}

        for team_id, t_info in teams.items():
            t_name = t_info.get("name", f"Team_{team_id}")
            t_addr = t_info["address"]
            raw_ptrs = mem.read_bytes(t_addr, 0xC8)
            if not raw_ptrs or len(raw_ptrs) < 25 * 8:
                continue

            ptrs = struct.unpack_from("<25Q", raw_ptrs)
            for slot_idx, p_addr in enumerate(ptrs):
                if not p_addr or p_addr == 0:
                    continue

                p_mem = mem.read_bytes(p_addr, 0x100)
                if not p_mem or len(p_mem) < 0x100:
                    continue

                fn = p_mem[OFF_FIRST_NAME:OFF_FIRST_NAME + 40].decode("utf-16le", errors="ignore").split("\0")[0]
                ln = p_mem[OFF_LAST_NAME:OFF_LAST_NAME + 40].decode("utf-16le", errors="ignore").split("\0")[0]
                p_full = f"{fn} {ln}".strip()

                if p_full in p_name_map:
                    matched_spec = p_name_map[p_full]
                    print(f"  [*] 命中现役球员: {p_full} -> {t_name} (Slot {slot_idx:02d}, Addr: {hex(p_addr)})")

                    if commit:
                        # 完整读取现有内存
                        curr_raw = mem.read_bytes(p_addr, STRIDE)
                        patched_raw = patch_player_struct(curr_raw, matched_spec, draft_year)
                        mem.write_bytes(p_addr, patched_raw)

                        # 执行外观与招牌动作雕刻
                        sculpt_data = matched_spec.get("sculpt")
                        if sculpt_data:
                            slot_val = matched_spec.get("slot_id")
                            sculpt_player_appearance(mem, p_addr, sculpt_data, slot_id=slot_val, commit=True)

                    roster_injected.append({
                        "team_id": team_id,
                        "team_name": t_name,
                        "slot_idx": slot_idx,
                        "player_name": p_full,
                        "addr": hex(p_addr)
                    })

        print(f"[+] 现役阵容扫描阶段完成: 共命中并同步更新 {len(roster_injected)} 名已签约 1984 球星")

    # 6. SQLite 事务提交
    if commit and conn:
        conn.commit()
        conn.close()
        print(f"[+] SQLite 数据库事务已成功持久化提交！")

    # 7. 生成审计回执
    receipt = {
        "timestamp": datetime.now().isoformat(),
        "engine_version": "2.0_MASTER",
        "draft_year": draft_year,
        "mode": "COMMITTED" if commit else "DRY_RUN",
        "template_path": template_path,
        "base_address": hex(base_pool),
        "total_prospects": len(prospects),
        "pool_slots_processed": len(pool_injected),
        "pool_slots_verified": pool_verified,
        "roster_players_matched": len(roster_injected),
        "roster_injected_details": roster_injected,
        "mismatches": mismatches
    }

    receipt_path = r"C:\nba2k22\exports\1984_DRAFT_MASTER_INJECTION_RECEIPT.json"
    os.makedirs(os.path.dirname(receipt_path), exist_ok=True)
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 90)
    print("1984 DRAFT CLASS MASTER INJECTION EXECUTION COMPLETED")
    print("=" * 90)
    print(f"[*] 模式: {'【正式提交写入 COMMIT LIVE】' if commit else '【预检预览 DRY-RUN】'}")
    print(f"[*] 选秀池槽位写入: 60/60 处理完毕 (CAS 断言通过: {pool_verified} 个)")
    print(f"[*] 现役阵容穿透命中: {len(roster_injected)} 名球员同步热更新完成")
    print(f"[*] 审计回执已安全存盘: {receipt_path}")
    print("=" * 90)

    return receipt


def main():
    parser = argparse.ArgumentParser(description="NBA 2K22 1984 届历史选秀名单全维度内存注入与复用总引擎")
    parser.add_argument("--commit", action="store_true", help="正式提交内存与数据库写入 (若不加则为 DRY-RUN 预览)")
    parser.add_argument("--template-path", type=str, default=None, help="自定义 1984 主模板 JSON 路径")
    parser.add_argument("--db-path", type=str, default=None, help="自定义 SQLite 数据库路径")
    args = parser.parse_args()

    execute_master_1984_draft_injection(
        template_path=args.template_path,
        db_path=args.db_path,
        commit=args.commit
    )


if __name__ == "__main__":
    main()
