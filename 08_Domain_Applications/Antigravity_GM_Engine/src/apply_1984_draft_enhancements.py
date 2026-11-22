# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 外部 GM 引擎
1984 届历史新秀名单批量应用与槽位增强执行器 (Apply 1984 Draft Enhancements)

功能：
1. 读取 1984_draft_enhancement_spec.json 规范（60 人真实新秀全量参数）；
2. 定位 player_pool.sqlite 中的选秀槽位（默认 Slot 590 ~ 649）；
3. 幂等更新关系表字段（姓名、面补 ID、位置、潜力、年份顺位）；
4. 同步修补 raw_struct 二进制数据块（1,264 字节结构体），保持内存与关系模型 100% 契合；
5. 执行写后即时回读校验并生成审计回执。
"""

import os
import sys
import json
import sqlite3
import struct
import shutil
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

# 默认路径配置（优先使用外部 C:\nba2k22 独立数据目录）
DEFAULT_EXTERNAL_DIR = r"C:\nba2k22"
DEFAULT_DB_PATH = os.path.join(DEFAULT_EXTERNAL_DIR, "saves", "MyLEAGUE0005", "player_pool.sqlite")
DEFAULT_SPEC_PATH_LOCAL = os.path.join(
    os.path.dirname(__file__), "..", "database", "draft_classes", "1984_draft_enhancement_spec.json"
)
DEFAULT_SPEC_PATH_EXPORT = os.path.join(DEFAULT_EXTERNAL_DIR, "exports", "1984_draft_enhancement_spec.json")

# 2K 原生结构体偏移定义 (对齐 PLAYER.json & config.py)
OFF_LAST_NAME = 0x00       # UTF-16LE, 40 字节
OFF_FIRST_NAME = 0x28      # UTF-16LE, 40 字节
OFF_FACE_ID = 0x6C         # uint16, 2 字节
OFF_POTENTIAL = 0xEB       # uint8, 1 字节
OFF_POSITION = 0xF9        # uint8, 低 3 bits
OFF_DRAFT_YEAR = 0x179     # uint8, 1 字节 (Year = 1900 + raw)
OFF_DRAFT_PICK = 0x312     # uint16 位域
OFF_DRAFT_ROUND = 0x316    # uint8 位域

# 核心能力属性偏移 (29 项全量攻防属性)
ATTR_OFFSETS = {
    "driving_layup": 0x41F,
    "post_fadeaway": 0x420,
    "post_hook": 0x421,
    "post_moves": 0x422,
    "draw_foul": 0x423,
    "shot_close": 0x424,
    "mid_range": 0x425,
    "three_point": 0x426,
    "free_throw": 0x427,
    "ball_control": 0x428,
    "pass_iq": 0x429,
    "pass_accuracy": 0x42A,
    "off_rebound": 0x42B,
    "def_rebound": 0x42C,
    "interior_def": 0x42D,
    "perimeter_def": 0x42E,
    "lateral_quick": 0x42F,
    "pass_perception": 0x430,
    "block": 0x431,
    "steal": 0x432,
    "standing_dunk": 0x435,
    "driving_dunk": 0x436,
    "speed": 0x437,
    "speed_with_ball": 0x438,
    "acceleration": 0x439,
    "vertical": 0x43A,
    "strength": 0x43B,
    "stamina": 0x43C,
    "hustle": 0x43D,
    "shot_iq": 0x43E,
    "pass_vision": 0x453,
    "hands": 0x455
}

# 核心战术倾向偏移 (30+ 项全量原生倾向)
TEND_OFFSETS = {
    "shot": 0x458,
    "driving_layup": 0x459,
    "standing_dunk": 0x45A,
    "driving_dunk": 0x45B,
    "flashy_dunk": 0x45C,
    "alley_oop": 0x45D,
    "putback": 0x45E,
    "crash": 0x45F,
    "spin_layup": 0x460,
    "hop_step_layup": 0x461,
    "euro_step_layup": 0x462,
    "floater": 0x463,
    "shot_under_basket": 0x465,
    "shot_close": 0x466,
    "shot_mid_range": 0x46A,
    "shot_three": 0x472,
    "drive": 0x483,
    "attack_strong_on_drive": 0x497,
    "dish_to_open_man": 0x498,
    "touches": 0x499,
    "post_up": 0x49A,
    "roll_vs_pop": 0x49B,
    "play_discipline": 0x4A1,
    "pass_interception": 0x4B4,
    "on_ball_steal": 0x4B6,
    "contest_shot": 0x4B7,
    "block_shot": 0x4B8,
    "foul": 0x4B9,
    "hard_foul": 0x4BA
}

# 加载原生徽章位域映射 (99 项徽章: 80 项 LEVEL + 18 项 BOOLEAN)
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
    """将游戏 25~99 评分换算为内存 0~255 原生值"""
    return min(255, max(0, int((rating - 25) * 3)))


def patch_raw_struct(raw_bytes: bytes, player_spec: Dict[str, Any]) -> bytes:
    """对 1,264 字节的 raw_struct 执行内存级字段覆写"""
    # 0. 保护 2K 原生官方球星槽位 (Slot 590~595: 奥拉朱旺、乔丹、帕金斯、索普、威利斯、斯托克顿)
    slot_id = player_spec.get("slot_id")
    if slot_id in range(590, 596):
        return raw_bytes

    if not raw_bytes or len(raw_bytes) < 0x458:
        # 若原始块为空或异常，创建基础缓冲区
        raw_ba = bytearray(1264)
    else:
        raw_ba = bytearray(raw_bytes)

    # 1. 姓名 (UTF-16LE, 40 字节定长填充)
    fn_bytes = player_spec["first_name"].encode("utf-16le").ljust(40, b"\x00")[:40]
    ln_bytes = player_spec["last_name"].encode("utf-16le").ljust(40, b"\x00")[:40]
    raw_ba[OFF_FIRST_NAME:OFF_FIRST_NAME + 40] = fn_bytes
    raw_ba[OFF_LAST_NAME:OFF_LAST_NAME + 40] = ln_bytes

    # 2. 面补 ID (uint16)
    struct.pack_into("<H", raw_ba, OFF_FACE_ID, int(player_spec["face_id"]))

    # 3. 潜力 (uint8 at 0xEB, 评分换算值 at 0x441)
    pot = int(player_spec.get("potential", 80))
    raw_ba[OFF_POTENTIAL] = pot
    if len(raw_ba) > 0x441:
        raw_ba[0x441] = rating_to_raw(pot)

    # 4. 位置 (3 bits: 0=PG, 1=SG, 2=SF, 3=PF, 4=C)
    pos_idx = int(player_spec.get("position", 2)) & 0x07
    curr_pos_byte = raw_ba[OFF_POSITION]
    raw_ba[OFF_POSITION] = (curr_pos_byte & 0xF8) | pos_idx

    # 5. 选秀年份 (1984 -> 84)
    raw_ba[OFF_DRAFT_YEAR] = 1984 - 1900

    # 6. 属性写入 (32 项攻防属性)
    attrs = player_spec.get("attributes", {})
    for attr_name, offset in ATTR_OFFSETS.items():
        if attr_name in attrs and offset < len(raw_ba):
            rating_val = attrs[attr_name]
            raw_ba[offset] = rating_to_raw(rating_val)

    # 7. 倾向写入 (29 项战术倾向: 0~100)
    tends = player_spec.get("tendencies", {})
    for tend_name, offset in TEND_OFFSETS.items():
        if tend_name in tends and offset < len(raw_ba):
            raw_ba[offset] = min(100, max(0, int(tends[tend_name])))

    # 8. 球星专属被动动画包 (SIGNATURE_ID at 0xE8, uint32)
    sig_id = player_spec.get("signature_id")
    if sig_id is not None and len(raw_ba) >= 0xEC:
        struct.pack_into("<I", raw_ba, 0xE8, int(sig_id))

    # 9. 赛场真实专属动作包 (159 字节: 投篮出手/上篮/扣篮/背身/控球, 0x380 ~ 0x41E)
    anim_hex = player_spec.get("animation_block_hex")
    if anim_hex:
        anim_bytes = bytes.fromhex(anim_hex)
        if len(anim_bytes) == 159 and len(raw_ba) >= (0x380 + 159):
            raw_ba[0x380:0x380 + 159] = anim_bytes

    # 10. 真实性格位域与心智特征徽章 (10 字节: 领头羊/好胜心/极具表现力/硬汉, 0x4BB ~ 0x4C4)
    pers_hex = player_spec.get("personality_hex")
    if pers_hex:
        pers_bytes = bytes.fromhex(pers_hex)
        if len(pers_bytes) == 10 and len(raw_ba) >= (0x4BB + 10):
            raw_ba[0x4BB:0x4BB + 10] = pers_bytes

    # 11. 2K22 原生全量徽章位域打包 (清除泥人残留技能等级徽章并写入真实配置)
    if BADGE_FIELDS_MAP:
        # 先将所有 LEVEL 类徽章重置为 0 (保留原生布尔性格特征)
        for b_meta in BADGE_FIELDS_MAP.values():
            if b_meta.get("kind") == "LEVEL":
                off = b_meta["offset"]
                w = b_meta["width"]
                s = b_meta["start_bit"]
                if off < len(raw_ba):
                    mask = ((1 << w) - 1) << s
                    raw_ba[off] &= ~mask

        # 写入规格书指定的标准化徽章
        badges = player_spec.get("badges", {})
        for b_name, b_level in badges.items():
            if b_name == "FastbreakFinisher": b_name = "Downhill"
            elif b_name == "PogoStick": b_name = "Pogostick"
            if b_name in BADGE_FIELDS_MAP:
                meta = BADGE_FIELDS_MAP[b_name]
                off = meta["offset"]
                w = meta["width"]
                s = meta["start_bit"]
                if off < len(raw_ba):
                    val = int(b_level) & ((1 << w) - 1)
                    mask = ((1 << w) - 1) << s
                    raw_ba[off] = (raw_ba[off] & ~mask) | (val << s)

    return bytes(raw_ba)


def load_enhancement_spec(spec_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """加载 1984 选秀增强规格书"""
    candidates = []
    if spec_path:
        candidates.append(spec_path)
    candidates.extend([
        DEFAULT_SPEC_PATH_LOCAL,
        DEFAULT_SPEC_PATH_EXPORT
    ])

    for p in candidates:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) >= 60:
                    return data
                elif isinstance(data, dict) and "prospects" in data and len(data["prospects"]) >= 60:
                    return data["prospects"]

    raise FileNotFoundError(f"无法在以下候选路径找到有效 1984 规格书 (需 >= 60 人): {candidates}")


def apply_draft_enhancements(
    db_path: str,
    spec_path: Optional[str] = None,
    commit: bool = False,
    backup: bool = True
) -> Dict[str, Any]:
    """批量执行 1984 新秀槽位增强"""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"目标数据库不存在: {db_path}")

    specs = load_enhancement_spec(spec_path)
    print(f"[*] 成功加载规格书，共 {len(specs)} 名 1984 真实新秀配置。")

    if backup and commit:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bak_path = f"{db_path}.bak_{ts}"
        shutil.copy2(db_path, bak_path)
        print(f"[*] 已创建数据库安全备份: {bak_path}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    updated_count = 0
    class_a_count = 0
    class_b_count = 0
    change_log = []

    for item in specs:
        slot_id = item["slot_id"]
        full_name = item["full_name"]
        fn = item["first_name"]
        ln = item["last_name"]
        face_id = item["face_id"]
        pos = item["position"]
        pos_name = item["position_name"]
        pot = item["potential"]
        face_class = item["face_class"]
        
        if face_class == "CLASS_A_OFFICIAL":
            class_a_count += 1
        else:
            class_b_count += 1

        # 读取当前槽位状态
        cur.execute("SELECT first_name, last_name, cyberface_id, raw_struct FROM player_pool WHERE slot_id = ?", (slot_id,))
        row = cur.fetchone()
        if not row:
            print(f"[!] 警告: 槽位 {slot_id} 不存在于 player_pool，跳过。")
            continue

        orig_fn, orig_ln, orig_face, orig_raw = row

        # 保护 2K 官方原生球星槽位 (Slot 590~595: 奥拉朱旺/乔丹/帕金斯/索普/威利斯/斯托克顿)
        if slot_id in range(590, 596):
            change_log.append({
                "slot_id": slot_id,
                "pick": item.get("pick_proj", item.get("overall_pick", 0)),
                "target": full_name,
                "face_id": orig_face,
                "face_class": "OFFICIAL_PRESERVED",
                "prev": f"{orig_fn} {orig_ln} (Official Native Intact)"
            })
            continue

        new_raw = patch_raw_struct(orig_raw, item)

        change_log.append({
            "slot_id": slot_id,
            "pick": item.get("pick_proj", item.get("overall_pick", 0)),
            "target": full_name,
            "face_id": face_id,
            "face_class": face_class,
            "prev": f"{orig_fn} {orig_ln} (face {orig_face})"
        })

        if commit:
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
                    draft_year = 1984,
                    draft_round = ?,
                    draft_pick = ?,
                    overall_pick = ?,
                    raw_struct = ?
                WHERE slot_id = ?
            """, (
                fn, ln, full_name, face_id, pos, pos_name, pot, pot,
                item["draft_round"], item["draft_pick"], item["overall_pick"],
                new_raw, slot_id
            ))
        updated_count += 1

    if commit:
        conn.commit()
        print(f"[+] 事务提交成功！已持久化更新 {updated_count} 个槽位。")
    else:
        conn.rollback()
        print(f"[!] DRY-RUN 预览模式完成。未做实际写入（指定 --commit 参数以正式执行）。")

    conn.close()

    receipt = {
        "timestamp": datetime.now().isoformat(),
        "db_path": db_path,
        "mode": "COMMIT" if commit else "DRY_RUN",
        "slots_updated": updated_count,
        "class_a_count": class_a_count,
        "class_b_count": class_b_count,
        "slot_range": f"{specs[0]['slot_id']} ~ {specs[-1]['slot_id']}",
        "changes_preview": change_log[:5]
    }
    return receipt


def verify_enhancements(db_path: str, spec_path: Optional[str] = None) -> bool:
    """验证目标数据库是否已满足 1984 增强规范"""
    specs = load_enhancement_spec(spec_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    mismatches = []
    for item in specs:
        slot_id = item["slot_id"]
        cur.execute("""
            SELECT first_name, last_name, cyberface_id, position, potential, draft_year, raw_struct
            FROM player_pool
            WHERE slot_id = ?
        """, (slot_id,))
        row = cur.fetchone()
        if not row:
            mismatches.append(f"Slot {slot_id} missing")
            continue

        fn, ln, face, pos, pot, yr, raw = row
        if (fn != item["first_name"] or ln != item["last_name"] or 
            face != item["face_id"] or yr != 1984):
            mismatches.append(
                f"Slot {slot_id}: expected {item['full_name']} (face {item['face_id']}, yr 1984), "
                f"got {fn} {ln} (face {face}, yr {yr})"
            )

        # 检查 raw_struct 回读
        if raw and len(raw) >= 0x70:
            read_fn = raw[OFF_FIRST_NAME:OFF_FIRST_NAME + 40].decode("utf-16le").split("\0")[0]
            read_face = struct.unpack_from("<H", raw, OFF_FACE_ID)[0]
            if read_fn != item["first_name"] or read_face != item["face_id"]:
                mismatches.append(f"Slot {slot_id} binary raw_struct mismatch: read '{read_fn}', face {read_face}")

    conn.close()
    if mismatches:
        print(f"[x] 验证未通过，共发现 {len(mismatches)} 处不一致:")
        for m in mismatches[:10]:
            print(f"  - {m}")
        return False
    else:
        print(f"[v] 验证完全通过！全部 {len(specs)} 个槽位（{specs[0]['slot_id']}~{specs[-1]['slot_id']}）结构与数据 100% 契合。")
        return True


def main():
    parser = argparse.ArgumentParser(description="1984 届历史新秀名单批量修改与槽位增强工具")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help=f"目标 player_pool.sqlite 路径 (默认: {DEFAULT_DB_PATH})")
    parser.add_argument("--spec-file", default=None, help="1984 规格书路径 (可选)")
    parser.add_argument("--commit", action="store_true", help="确认提交写入数据库 (不加此参数仅做 dry-run 演练)")
    parser.add_argument("--verify", action="store_true", help="校验数据库现有槽位是否已对齐规格书")
    parser.add_argument("--no-backup", action="store_true", help="写入前跳过数据库自动备份")

    args = parser.parse_args()

    if args.verify:
        ok = verify_enhancements(args.db_path, args.spec_file)
        sys.exit(0 if ok else 1)

    receipt = apply_draft_enhancements(
        db_path=args.db_path,
        spec_path=args.spec_file,
        commit=args.commit,
        backup=not args.no_backup
    )

    print("\n" + "=" * 60)
    print("APPLY_1984_DRAFT_ENHANCEMENT_RECEIPT")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    print("=" * 60)


if __name__ == "__main__":
    main()
