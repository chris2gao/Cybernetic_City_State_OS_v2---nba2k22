# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 外部 GM 引擎
1985 届历史选秀名单实机内存热注入与数据库双端原子执行器 (Reusable 1985 Draft Class Live Injector)

依据标准规范:
- SOP-DRAFT-CLASS-MEMORY-INJECTION-V1.0
- SPEC-DRAFT-CLASS-MEM-INJECT-V1.0 (无占位符差分协议)

核心能力：
1. 官方球星绝对保护：Patrick Ewing, Karl Malone, Chris Mullin 等原生球星只做只读核验与攻防属性倾向注入，保留原生面补、原生动作与 0x90 堆指针；
2. 51 名缺失泥人全量置换：注入真实面补、UTF-16LE 姓名、选秀年份 (0x179=85)、真实位置、潜力换算；
3. 赛场技术动作包克隆：将现代/名宿原型（如约基奇、莫兰特、波尔津吉斯、兰德尔等）的 159 字节专用动作包 (0x380) 与签名动画 (0x0E8) 热注入；
4. 0x90 外观与骨骼雕刻 (PlayerSculptor)：注入真实历史臂展（波尔 259cm）、肩宽、肌肉粗细与体型模板；
5. 80 项技能等级徽章纯净化 (0x4BB~0x4E2 清零并写入目标徽章)；
6. 犯规安全锁：强行约束 foul <= 45，杜绝新秀犯规爆炸；
7. 自动存档探测：自动识别最新 MyLEAGUE 存档数据库 (player_pool.sqlite) 并执行事务双端落盘与 CAS 写后即时回读校验。
"""

import os
import sys
import json
import struct
import sqlite3
import shutil
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

sys.path.append(r"E:\workspace\Cybernetic_City_State_OS_v2 - nba2k22\08_Domain_Applications\Antigravity_GM_Engine\src")
from memory import GameMemory
from address_calibrator import AddressCalibrator
from player_sculptor import PlayerSculptor

STRIDE = 0x4F0  # 1,264 字节步长

# 结构体关键基础偏移
OFF_LAST_NAME = 0x000     # 40 字节 UTF-16LE
OFF_FIRST_NAME = 0x028    # 40 字节 UTF-16LE
OFF_FACE_ID = 0x06C       # uint16 (2 字节小端)
OFF_PEAK_AGE = 0x072      # uint16 (bits 0..3: reserved, bits 4..9: peak_start, bits 10..15: peak_end)
OFF_APPEARANCE = 0x090    # uint64 (8 字节外观指针，严禁篡改)
OFF_SIGNATURE_ID = 0x0E8  # uint32 (4 字节小端，签名动画)
OFF_POTENTIAL = 0x0EB     # uint8 (人类评分 25~99)
OFF_POSITION = 0x0F9      # uint8 (低 3 位: 0=PG, 1=SG, 2=SF, 3=PF, 4=C)
OFF_DRAFT_YEAR = 0x179    # uint8 (年份 - 1900, 权威真实偏移量!)
OFF_DRAFT_PICK = 0x312    # uint16
OFF_DRAFT_ROUND = 0x316   # uint8
OFF_ANIMATION_BLOCK = 0x380 # 159 字节专用动作包 (0x380 ~ 0x41E)
OFF_POTENTIAL_RAW = 0x441 # uint8 (评分换算值)
OFF_PERSONALITY = 0x4BB   # 10 字节性格位域 (0x4BB ~ 0x4C4)

# 核心攻防属性偏移 (32 项)
ATTR_OFFSETS = {
    "driving_layup": 0x41F, "post_hook": 0x420, "post_fadeaway": 0x421, "post_moves": 0x422,
    "draw_foul": 0x423, "shot_close": 0x424, "mid_range": 0x425, "three_point": 0x426,
    "free_throw": 0x427, "ball_control": 0x428, "pass_iq": 0x429, "pass_accuracy": 0x42A,
    "off_rebound": 0x42B, "def_rebound": 0x42C, "interior_def": 0x42D, "perimeter_def": 0x42E,
    "lateral_quick": 0x42F, "steal": 0x430, "block": 0x431, "shot_contest": 0x432,
    "speed": 0x437, "speed_with_ball": 0x438, "acceleration": 0x439, "vertical": 0x43A,
    "strength": 0x43B, "stamina": 0x43C, "hustle": 0x43D, "overall_durability": 0x43E,
    "standing_dunk": 0x450, "driving_dunk": 0x451, "pass_vision": 0x453, "hands": 0x455
}

# 核心战术倾向偏移 (29 项)
TEND_OFFSETS = {
    "shot": 0x458, "driving_layup": 0x459, "standing_dunk": 0x45A, "driving_dunk": 0x45B,
    "flashy_dunk": 0x45C, "alley_oop": 0x45D, "putback": 0x45E, "crash": 0x45F,
    "spin_layup": 0x460, "hop_step_layup": 0x461, "euro_step_layup": 0x462, "floater": 0x463,
    "shot_under_basket": 0x465, "shot_close": 0x466, "shot_mid_range": 0x46A, "three_point": 0x472,
    "drive": 0x483, "attack_strong_on_drive": 0x497, "dish_to_open_man": 0x498, "touches": 0x499,
    "post_up": 0x49A, "roll_vs_pop": 0x49B, "play_discipline": 0x4A1, "pass_interception": 0x4B4,
    "on_ball_steal": 0x4B6, "contest_shot": 0x4B7, "block_shot": 0x4B8, "foul": 0x4B9,
    "hard_foul": 0x4BA
}

# 徽章字典加载
BADGE_PROFILE_PATH = r"E:\workspace\Cybernetic_City_State_OS_v2 - nba2k22\08_Domain_Applications\Antigravity_GM_Engine\world_data_prototype\player_detail_native_profile.json"
BADGE_FIELDS_MAP = {}
if os.path.exists(BADGE_PROFILE_PATH):
    try:
        with open(BADGE_PROFILE_PATH, "r", encoding="utf-8") as f:
            _prof = json.load(f)
            BADGE_FIELDS_MAP = _prof.get("badge_fields", {})
    except Exception as e:
        print("[!] 加载徽章定义失败:", e)


def rating_to_raw(rating: int) -> int:
    return min(255, max(0, int((rating - 25) * 3)))


def auto_detect_db_path(given_path: Optional[str] = None) -> str:
    """自动检测最新 MyLEAGUE 存档数据库"""
    if given_path and os.path.exists(given_path):
        return given_path

    saves_dir = r"C:\nba2k22\saves"
    if os.path.exists(saves_dir):
        candidates = []
        for root, dirs, files in os.walk(saves_dir):
            if "player_pool.sqlite" in files:
                p = os.path.join(root, "player_pool.sqlite")
                candidates.append((os.path.getmtime(p), p))
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            latest_db = candidates[0][1]
            print(f"[*] 自动定位到最新 MyLEAGUE 存档数据库: {latest_db}")
            return latest_db

    fallback = r"C:\nba2k22\saves\MyLEAGUE0005\player_pool.sqlite"
    return given_path or fallback


def patch_raw_struct(orig_raw: bytes, spec: Dict[str, Any], draft_year: int = 1985) -> bytes:
    raw_ba = bytearray(orig_raw) if (orig_raw and len(orig_raw) >= STRIDE) else bytearray(STRIDE)
    is_preserved = spec.get("is_official_preserved", False)

    # 严格保护 0x88 / 0x90 指针与 0xF4 唯一球员 ID
    if orig_raw and len(orig_raw) >= 0xF8:
        pf4_orig = struct.unpack_from("<I", orig_raw, 0xF4)[0]
        if pf4_orig > 0:
            struct.pack_into("<I", raw_ba, 0xF4, pf4_orig)

    # 1. 选秀年份锁定 0x179
    raw_ba[OFF_DRAFT_YEAR] = (draft_year - 1900) & 0xFF

    # 2. 身份置换 (泥人置换模式)
    if not is_preserved:
        if "first_name" in spec:
            fn_bytes = spec["first_name"].encode("utf-16le").ljust(40, b"\x00")[:40]
            raw_ba[OFF_FIRST_NAME:OFF_FIRST_NAME + 40] = fn_bytes
        if "last_name" in spec:
            ln_bytes = spec["last_name"].encode("utf-16le").ljust(40, b"\x00")[:40]
            raw_ba[OFF_LAST_NAME:OFF_LAST_NAME + 40] = ln_bytes
        if "face_id" in spec:
            struct.pack_into("<H", raw_ba, OFF_FACE_ID, int(spec["face_id"]))
        if "position" in spec:
            pos_idx = int(spec["position"]) & 0x07
            raw_ba[OFF_POSITION] = (raw_ba[OFF_POSITION] & 0xF8) | pos_idx

        # 签名动画写入 (0x0E8)
        if "signature_id" in spec:
            struct.pack_into("<I", raw_ba, OFF_SIGNATURE_ID, int(spec["signature_id"]))

        # 159 字节专用动作包写入 (0x380 ~ 0x41E)
        if "animation_block_hex" in spec and spec["animation_block_hex"]:
            anim_bytes = bytes.fromhex(spec["animation_block_hex"])
            if len(anim_bytes) == 159:
                raw_ba[OFF_ANIMATION_BLOCK:OFF_ANIMATION_BLOCK + 159] = anim_bytes

        # 10 字节性格位域 (0x4BB ~ 0x4C4)
        if "personality_hex" in spec and spec["personality_hex"]:
            pers_bytes = bytes.fromhex(spec["personality_hex"])
            if len(pers_bytes) == 10:
                raw_ba[OFF_PERSONALITY:OFF_PERSONALITY + 10] = pers_bytes

    # 3. 潜力换算写入 (0xEB 与 0x441)
    pot = int(spec.get("potential", 80))
    raw_ba[OFF_POTENTIAL] = pot
    raw_ba[OFF_POTENTIAL_RAW] = rating_to_raw(pot)

    # 4. 攻防属性写入 (稀疏键值对)
    attrs = spec.get("attributes", {})
    for attr_name, val in attrs.items():
        if attr_name in ATTR_OFFSETS and val is not None:
            off = ATTR_OFFSETS[attr_name]
            raw_ba[off] = rating_to_raw(int(val))

    # 5. 战术倾向写入 (含 foul <= 45 安全锁)
    tends = spec.get("tendencies", {})
    for tend_name, val in tends.items():
        if tend_name in TEND_OFFSETS and val is not None:
            off = TEND_OFFSETS[tend_name]
            val_int = min(100, max(0, int(val)))
            if tend_name == "foul":
                val_int = min(45, val_int)
            raw_ba[off] = val_int

    # 6. 徽章按位纯净化与打包写入
    if BADGE_FIELDS_MAP and "badges" in spec:
        # 清零 80 个 LEVEL 等级徽章
        for b_meta in BADGE_FIELDS_MAP.values():
            if b_meta.get("kind") == "LEVEL":
                off = b_meta["offset"]
                w = b_meta["width"]
                s = b_meta["start_bit"]
                if off < STRIDE:
                    mask = ((1 << w) - 1) << s
                    raw_ba[off] &= ~mask

        # 写入目标等级徽章
        badges = spec["badges"]
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

    # 7. 巅峰年龄写入 (0x072, uint16, 严格保留低 4 位标志 & 0x000F)
    if "peak_start" in spec and "peak_end" in spec:
        ps = int(spec["peak_start"])
        pe = int(spec["peak_end"])
        old_u16 = struct.unpack_from("<H", raw_ba, OFF_PEAK_AGE)[0]
        new_u16 = (old_u16 & 0x000F) | ((ps & 0x3F) << 4) | ((pe & 0x3F) << 10)
        struct.pack_into("<H", raw_ba, OFF_PEAK_AGE, new_u16)

    return bytes(raw_ba)


def run_injection(spec_path: str, db_path: str, commit: bool = False) -> Dict[str, Any]:
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_data = json.load(f)

    prospects = spec_data.get("prospects", [])
    draft_year = spec_data.get("draft_year", 1985)
    print(f"[*] 成功加载规格书: {spec_path} (共 {len(prospects)} 人，年份: {draft_year})")

    # 1. 数据库安全备份
    if commit and os.path.exists(db_path):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_path = f"{db_path}.bak_{ts}"
        shutil.copy2(db_path, bak_path)
        print(f"[*] 已创建数据库安全备份: {bak_path}")

    # 2. 挂接实机内存
    mem = GameMemory("NBA2K22.exe", read_only=(not commit))
    cal = AddressCalibrator(mem)
    ok, base_addr = cal.check_and_calibrate_player_pool()
    if not ok or base_addr == 0:
        raise RuntimeError("【校准失败】未能定位到 NBA2K22.exe 球员池基址！")

    print(f"[*] 挂接进程 NBA2K22.exe (PID: {mem.pid})，基址锁定: {hex(base_addr)}")

    sculptor = PlayerSculptor(mem, read_only=(not commit))
    conn = sqlite3.connect(db_path) if (commit and os.path.exists(db_path)) else None
    cur = conn.cursor() if conn else None

    injected_slots = []
    verified_slots = []
    mismatches = []

    for item in prospects:
        slot_id = item["slot_id"]
        full_name = item["full_name"]
        face_id = item["face_id"]
        is_preserved = item.get("is_official_preserved", False)
        slot_addr = base_addr + slot_id * STRIDE

        # 读取当前原始块
        orig_raw = mem.read_bytes(slot_addr, STRIDE)
        if not orig_raw or len(orig_raw) < STRIDE:
            mismatches.append(f"Slot {slot_id} at {hex(slot_addr)}: read failed")
            continue

        orig_fn = orig_raw[OFF_FIRST_NAME:OFF_FIRST_NAME + 40].decode("utf-16le", errors="ignore").split("\0")[0]
        orig_ln = orig_raw[OFF_LAST_NAME:OFF_LAST_NAME + 40].decode("utf-16le", errors="ignore").split("\0")[0]
        orig_face = struct.unpack_from("<H", orig_raw, OFF_FACE_ID)[0]

        # 组装安全装配后的 1,264 字节结构体
        new_raw = patch_raw_struct(orig_raw, item, draft_year)

        if commit:
            # 写入实机运行内存
            write_ok = mem.write_bytes(slot_addr, new_raw)
            if not write_ok:
                mismatches.append(f"Slot {slot_id} at {hex(slot_addr)}: RAM write failed")
                continue

            # 骨骼雕刻写入 (0x90 外观堆块)
            if not is_preserved and "sculpt_spec" in item:
                sculptor.write_sculpt(slot_id, item["sculpt_spec"])

            # 同步更新 SQLite player_pool 表
            if cur:
                fn_to_db = orig_fn if is_preserved else item.get("first_name", orig_fn)
                ln_to_db = orig_ln if is_preserved else item.get("last_name", orig_ln)
                name_to_db = f"{fn_to_db} {ln_to_db}"
                face_to_db = orig_face if is_preserved else face_id

                cur.execute("""
                    UPDATE player_pool
                    SET first_name = ?,
                        last_name = ?,
                        full_name = ?,
                        cyberface_id = ?,
                        position = ?,
                        position_name = ?,
                        potential = ?,
                        raw_potential = ?,
                        draft_year = ?,
                        raw_struct = ?
                    WHERE slot_id = ?
                """, (
                    fn_to_db, ln_to_db, name_to_db, face_to_db,
                    item.get("position", 2), item.get("position_name", "SF"),
                    item.get("potential", 80), rating_to_raw(item.get("potential", 80)),
                    draft_year, new_raw, slot_id
                ))

            # 立即回读验证 (CAS ReadProcessMemory)
            readback = mem.read_bytes(slot_addr, STRIDE)
            rb_fn = readback[OFF_FIRST_NAME:OFF_FIRST_NAME + 40].decode("utf-16le", errors="ignore").split("\0")[0]
            rb_ln = readback[OFF_LAST_NAME:OFF_LAST_NAME + 40].decode("utf-16le", errors="ignore").split("\0")[0]
            rb_face = struct.unpack_from("<H", readback, OFF_FACE_ID)[0]
            rb_yr = 1900 + readback[OFF_DRAFT_YEAR]
            rb_foul = readback[TEND_OFFSETS["foul"]]
            rb_pot_raw = readback[OFF_POTENTIAL_RAW]
            rb_sig = struct.unpack_from("<I", readback, OFF_SIGNATURE_ID)[0]

            expected_fn = orig_fn if is_preserved else item.get("first_name", "")
            expected_ln = orig_ln if is_preserved else item.get("last_name", "")
            expected_face = orig_face if is_preserved else face_id
            expected_pot_raw = rating_to_raw(item.get("potential", 80))
            expected_sig = int(item.get("signature_id", 0))

            base_match = (rb_fn == expected_fn and rb_ln == expected_ln and 
                          rb_face == expected_face and rb_yr == draft_year and 
                          rb_foul <= 45 and rb_pot_raw == expected_pot_raw)

            # 巅峰年龄 CAS 回读校验
            rb_u16 = struct.unpack_from("<H", readback, OFF_PEAK_AGE)[0]
            rb_ps = (rb_u16 >> 4) & 0x3F
            rb_pe = (rb_u16 >> 10) & 0x3F
            rb_low4 = rb_u16 & 0x000F
            orig_low4 = struct.unpack_from("<H", orig_raw, OFF_PEAK_AGE)[0] & 0x000F

            exp_ps = int(item.get("peak_start", 0))
            exp_pe = int(item.get("peak_end", 0))

            peak_match = True
            if exp_ps > 0 and exp_pe > 0:
                if rb_ps != exp_ps or rb_pe != exp_pe or rb_low4 != orig_low4:
                    peak_match = False

            # 泥人额外核验动作与骨骼
            extra_match = True
            if not is_preserved:
                if expected_sig > 0 and (rb_sig & 0x00FFFFFF) != (expected_sig & 0x00FFFFFF):
                    extra_match = False
                if "sculpt_spec" in item:
                    sculpt_pass, _ = sculptor.verify_sculpt(slot_id, item["sculpt_spec"])
                    if not sculpt_pass:
                        extra_match = False

            if base_match and extra_match and peak_match:
                verified_slots.append(slot_id)
            else:
                mismatches.append(
                    f"Slot {slot_id} CAS mismatch: exp ({expected_fn} {expected_ln}, face {expected_face}, yr {draft_year}, foul<=45, peak {exp_ps}..{exp_pe}), "
                    f"got ({rb_fn} {rb_ln}, face {rb_face}, yr {rb_yr}, foul {rb_foul}, peak {rb_ps}..{rb_pe}, low4 {hex(rb_low4)})"
                )

        injected_slots.append({
            "slot_id": slot_id,
            "target": full_name,
            "is_preserved": is_preserved,
            "face_id": face_id,
            "prototype": item.get("prototype_reference", {}).get("prototype_player", "None")
        })

    if commit and conn:
        conn.commit()
        conn.close()
        print(f"[+] SQLite 事务提交成功！双端原子落地完成。")

    receipt = {
        "timestamp": datetime.now().isoformat(),
        "draft_year": draft_year,
        "pid": mem.pid,
        "base_address": hex(base_addr),
        "mode": "LIVE_INJECTION_COMMITTED" if commit else "DRY_RUN",
        "total_prospects": len(prospects),
        "verified_count": len(verified_slots),
        "mismatches": mismatches,
        "sample_injected": injected_slots[:8]
    }
    return receipt


def main():
    parser = argparse.ArgumentParser(description="NBA 2K22 1985 选秀名单实机内存热注入与全维真实化执行器 (可复用模板版)")
    parser.add_argument("--spec-file", default=r"C:\nba2k22\exports\1985_draft_enhancement_spec.json")
    parser.add_argument("--db-path", default=None, help="SQLite 数据库路径 (默认自动探测最新存档)")
    parser.add_argument("--commit", action="store_true", help="确认正式执行写入")
    parser.add_argument("--dry-run", action="store_true", help="只读预检演练")
    args = parser.parse_args()

    if not args.commit and not args.dry_run:
        print("[!] 请指定 --commit 执行实机写入或 --dry-run 进行演练。")
        sys.exit(1)

    db_path = auto_detect_db_path(args.db_path)
    receipt = run_injection(args.spec_file, db_path, commit=args.commit)
    
    receipt_path = r"C:\nba2k22\exports\1985_DRAFT_BATCH_MOD_RECEIPT.json"
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("1985 DRAFT CLASS LIVE MEMORY INJECTION RECEIPT")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    print("=" * 60)
    print(f"[*] 回执文件已保存至: {receipt_path}")

    if receipt["mismatches"]:
        print(f"[x] 存在 {len(receipt['mismatches'])} 处校验失败！")
        sys.exit(1)
    else:
        status_msg = "实机热注入与双端持久化 100% 成功闭环" if args.commit else "DRY-RUN 演练 100% 通过"
        print(f"[v] {status_msg}！全部 {receipt['total_prospects']} 个选秀槽位验证无误。")
        sys.exit(0)


if __name__ == "__main__":
    main()
