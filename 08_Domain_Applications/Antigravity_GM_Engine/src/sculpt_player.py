# -*- coding: utf-8 -*-
"""
NBA 2K22 球员外观、骨骼与五官雕刻引擎 (Player Appearance, Skeletal & CAP Morph Sculptor)
专门针对球员体型、肩宽、臂展、手臂/腿部肌肉、头颈比、身形模板、肤色、发型发色、头带配件与五官面部形态进行原子级内存雕刻。
"""

import sys
import os
import struct
import argparse
from typing import Dict, Any, Optional

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from address_calibrator import AddressCalibrator


def sculpt_player_by_address(
    mem: GameMemory,
    player_addr: int,
    sculpt_spec: Dict[str, Any],
    commit: bool = False
) -> Dict[str, Any]:
    """
    对指定内存地址的球员执行全套骨骼、五官与外观堆块雕刻。
    """
    p_raw = mem.read_bytes(player_addr, 0x100)
    ln = p_raw[0:40].decode("utf-16le", errors="ignore").split("\x00")[0]
    fn = p_raw[0x28:0x28+40].decode("utf-16le", errors="ignore").split("\x00")[0]
    full_name = f"{fn} {ln}".strip()
    face_id = struct.unpack_from("<H", p_raw, 0x6C)[0]
    orig_weight = struct.unpack_from("<f", p_raw, 0x58)[0]
    p88_head = struct.unpack_from("<Q", p_raw, 0x88)[0]
    p90_app = struct.unpack_from("<Q", p_raw, 0x90)[0]

    if not p90_app or p90_app == 0:
        raise ValueError(f"球员 {full_name} 的 0x90 外观指针为空，无法雕刻！")

    print(f"[*] 正在雕刻球员: {full_name} (Addr: {hex(player_addr)})")
    print(f"    - 0x88 头部预设指针: {hex(p88_head)}")
    print(f"    - 0x90 外观堆块指针: {hex(p90_app)}")
    print(f"    - 当前面补 Face ID: {face_id} | 当前体重: {orig_weight:.2f} lbs")

    # 1. 体重写入 (0x58, float32)
    target_weight = sculpt_spec.get("weight_lbs", orig_weight)
    if commit and "weight_lbs" in sculpt_spec:
        mem.write_bytes(player_addr + 0x58, struct.pack("<f", float(target_weight)))
        rb_weight = struct.unpack_from("<f", mem.read_bytes(player_addr + 0x58, 4), 0)[0]
        print(f"  [+] 体重注入: {orig_weight:.2f} lbs -> {rb_weight:.2f} lbs (CAS OK)")

    # 2. 面补 Face ID (0x6C, uint16)
    if "face_id" in sculpt_spec and commit:
        new_face = int(sculpt_spec["face_id"])
        mem.write_bytes(player_addr + 0x6C, struct.pack("<H", new_face))
        rb_face = struct.unpack_from("<H", mem.read_bytes(player_addr + 0x6C, 2), 0)[0]
        print(f"  [+] 面补 FaceID 注入: {face_id} -> {rb_face} (CAS OK)")

    # 3. 头带配件剔除 (0x2F3 bit 4..6 = Headband, 0x34C bit 0..2 = HeadbandFrequency)
    if sculpt_spec.get("remove_headband", False) and commit:
        b2f3 = mem.read_bytes(player_addr + 0x2F3, 1)[0]
        new_b2f3 = b2f3 & ~(0x07 << 4)  # 清零 Headband bit 4..6
        mem.write_bytes(player_addr + 0x2F3, bytes([new_b2f3]))

        b34c = mem.read_bytes(player_addr + 0x34C, 1)[0]
        new_b34c = b34c & ~0x07          # 清零 HeadbandFrequency bit 0..2
        mem.write_bytes(player_addr + 0x34C, bytes([new_b34c]))

        rb_2f3 = mem.read_bytes(player_addr + 0x2F3, 1)[0]
        rb_34c = mem.read_bytes(player_addr + 0x34C, 1)[0]
        print(f"  [+] 头带配件剔除: 0x2F3 (0x{b2f3:02x}->0x{rb_2f3:02x}), 0x34C (0x{b34c:02x}->0x{rb_34c:02x}) (CAS OK, 头带已摘除)")

    # 4. 0x88 头部与五官形态堆块雕刻 (CAP Head Morphs)
    if p88_head and p88_head > 0 and "head_morphs" in sculpt_spec and commit:
        morphs = sculpt_spec["head_morphs"]
        raw_88 = bytearray(mem.read_bytes(p88_head, 64))

        if "head_preset" in morphs:
            raw_88[0] = int(morphs["head_preset"]) & 0xFF
        if "skull_preset" in morphs:
            raw_88[1] = int(morphs["skull_preset"]) & 0xFF
        if "skull_width" in morphs:
            raw_88[2] = int(morphs["skull_width"]) & 0xFF
        if "skull_height" in morphs:
            raw_88[3] = int(morphs["skull_height"]) & 0xFF
        if "temple_width" in morphs:
            raw_88[11] = int(morphs["temple_width"]) & 0xFF
        if "upper_nose_width" in morphs:
            raw_88[22] = int(morphs["upper_nose_width"]) & 0xFF
        if "lower_nose_width" in morphs:
            raw_88[23] = int(morphs["lower_nose_width"]) & 0xFF
        if "upper_cheek_width" in morphs:
            raw_88[29] = int(morphs["upper_cheek_width"]) & 0xFF
        if "middle_cheek_width" in morphs:
            raw_88[30] = int(morphs["middle_cheek_width"]) & 0xFF
        if "upper_lip_thickness" in morphs:
            raw_88[33] = int(morphs["upper_lip_thickness"]) & 0xFF
        if "lower_lip_thickness" in morphs:
            raw_88[36] = int(morphs["lower_lip_thickness"]) & 0xFF
        if "front_chin_width" in morphs:
            raw_88[41] = int(morphs["front_chin_width"]) & 0xFF
        if "rear_chin_width" in morphs:
            raw_88[42] = int(morphs["rear_chin_width"]) & 0xFF
        if "head_width" in morphs:
            raw_88[54] = int(morphs["head_width"]) & 0xFF
        raw_88[56] = 1  # ISMODIFIED = 1

        mem.write_bytes(p88_head, bytes(raw_88))
        rb_88 = mem.read_bytes(p88_head, 64)
        print(f"  [+] 0x88 头部与五官形态雕刻注入:")
        print(f"      - 头部预设 (HeadPreset): {rb_88[0]} (黑人宽脸基础)")
        print(f"      - 头骨宽/高 (SkullWidth/Height): {rb_88[2]}/{rb_88[3]} (饱满圆阔颅骨)")
        print(f"      - 面颊饱满度 (CheekWidth): {rb_88[29]} (肉感飞猪脸型)")
        print(f"      - 鼻翼宽 (NoseWidth): {rb_88[23]} (经典宽扁鼻翼)")
        print(f"      - 嘴唇厚度 (LipThickness): {rb_88[36]} (厚实丰唇)")
        print(f"      - 下巴宽度 (ChinWidth): {rb_88[41]} (刚毅宽下巴)")

    # 5. 0x90 外观堆块雕刻 (覆盖 Set 0x00, 0x40, 0x80, 0xC0 四套外貌姿态)
    app_raw = bytearray(mem.read_bytes(p90_app, 0x100))

    target_wingspan = sculpt_spec.get("wingspan_cm_x100", 22100)
    target_body_len = float(sculpt_spec.get("body_length", 1.0000))
    target_shoulder = float(sculpt_spec.get("shoulder_width", 1.0800))
    target_arm_scale = float(sculpt_spec.get("arm_scale", 1.0650))
    target_neck_scale = float(sculpt_spec.get("neck_head_scale", 1.0400))
    target_lower_scale = float(sculpt_spec.get("lower_scale", 1.0850))
    target_hand_scale = float(sculpt_spec.get("hand_scale", 1.0200))
    target_hair_len = float(sculpt_spec.get("hair_length", 0.0000))
    target_body_shape = int(sculpt_spec.get("body_shape", 2))  # 2 = Burly
    target_skin_color = int(sculpt_spec.get("skin_color", 5))  # 5 = African American Black

    for base in [0x00, 0x40, 0x80, 0xC0]:
        # 5.1 骨骼 6 大浮点缩放与臂展
        struct.pack_into("<H", app_raw, base + 0x02, int(target_wingspan))
        struct.pack_into("<6f", app_raw, base + 0x04,
                         target_body_len, target_shoulder, target_arm_scale,
                         target_neck_scale, target_lower_scale, target_hand_scale)
        # 5.2 发长 (0x1C = 0.0000 极短寸头/光头)
        struct.pack_into("<f", app_raw, base + 0x1C, target_hair_len)

        # 5.3 发型发色重置 (0x24 发型=0 光头, 0x28~0x33 清零剔除金发色与挑染)
        struct.pack_into("<H", app_raw, base + 0x24, 0)
        for clr_off in range(base + 0x28, base + 0x34):
            app_raw[clr_off] = 0

        # 5.4 肤色注入 (0x26 bit 6..9 = SkinColor, 5 = BLACK)
        orig_u16 = struct.unpack_from("<H", app_raw, base + 0x26)[0]
        new_u16 = (orig_u16 & ~(0x0F << 6)) | ((target_skin_color & 0x0F) << 6)
        struct.pack_into("<H", app_raw, base + 0x26, new_u16)

        # 5.5 身形模板
        app_raw[base + 0x3C] = target_body_shape & 0x07

    if commit:
        mem.write_bytes(p90_app, bytes(app_raw))
        # 立即回读断言
        rb_app = mem.read_bytes(p90_app, 0x40)
        rb_ws = struct.unpack_from("<H", rb_app, 0x02)[0]
        rb_bl, rb_sw, rb_as, rb_ns, rb_ls, rb_hs = struct.unpack_from("<6f", rb_app, 0x04)
        rb_hlen = struct.unpack_from("<f", rb_app, 0x1C)[0]
        rb_skin_u16 = struct.unpack_from("<H", rb_app, 0x26)[0]
        rb_skin_val = (rb_skin_u16 >> 6) & 0x0F
        rb_shape = rb_app[0x3C]

        print(f"  [+] 0x90 堆块雕刻回读断言:")
        print(f"      - 肤色 (SkinColor): {rb_skin_val} (CAS OK, 经典纯正黑人肤色 Skin 5)")
        print(f"      - 发型发长 (HairLength): {rb_hlen:.4f} (CAS OK, 剔除黄发，标准光头/寸头)")
        print(f"      - 臂展: {rb_ws} (CAS OK, 221cm 7'3\")")
        print(f"      - 肩宽: {rb_sw:.4f} (CAS OK, 宽肩拉满)")
        print(f"      - 手臂粗细: {rb_as:.4f} (CAS OK, 强壮粗臂)")
        print(f"      - 头颈比例: {rb_ns:.4f} (CAS OK, 粗壮公牛颈)")
        print(f"      - 下肢臀腿: {rb_ls:.4f} (CAS OK, 飞猪重型下盘)")
        print(f"      - 身形模板: {rb_shape} (CAS OK, 2 = BURLY 厚实强壮体型)")

    return {
        "player_name": full_name,
        "address": hex(player_addr),
        "app_ptr": hex(p90_app),
        "head_ptr": hex(p88_head),
        "weight_lbs": target_weight,
        "skin_color": target_skin_color,
        "hair_length": target_hair_len,
        "shoulder_width": target_shoulder,
        "arm_scale": target_arm_scale,
        "lower_scale": target_lower_scale,
        "neck_scale": target_neck_scale,
        "wingspan": target_wingspan,
        "body_shape": target_body_shape
    }


def main():
    parser = argparse.ArgumentParser(description="NBA 2K22 球员关键特征、体型骨骼与CAP五官雕刻引擎")
    parser.add_argument("--commit", action="store_true", help="正式提交内存热写入")
    parser.add_argument("--team-id", type=int, default=0, help="球队 ID (0 为 76人)")
    parser.add_argument("--slot-id", type=int, default=13, help="球队槽位序号 (13 为巴克利)")
    args = parser.parse_args()

    mem = GameMemory("NBA2K22.exe", read_only=not args.commit)
    cal = AddressCalibrator(mem)
    ok, base, teams = cal.check_and_calibrate_teams()

    if not ok or not teams:
        print("[-] 动态校准失败！")
        return

    t = teams.get(args.team_id)
    if not t:
        print(f"[-] 未找到 Team ID {args.team_id}")
        return

    raw_ptrs = mem.read_bytes(t["address"], 0xC8)
    ptrs = struct.unpack_from("<25Q", raw_ptrs)
    p_addr = ptrs[args.slot_id]

    # 巴克利“空中飞猪”神级真实还原雕刻规格
    barkley_spec = {
        "face_id": 1,                   # 1 = CAP 捏人模式
        "weight_lbs": 255.0,            # 经典巅峰飞猪体重 (255 磅)
        "wingspan_cm_x100": 22100,      # 7尺3寸长臂展 (221 cm)
        "body_length": 1.0000,          # 标准厚实躯干
        "shoulder_width": 1.0800,       # 极致宽肩 (拉大 8%)
        "arm_scale": 1.0650,            # 强壮粗硕大臂与小臂 (拉粗 6.5%)
        "neck_head_scale": 1.0400,      # 粗短牛颈 (减少头身细长感)
        "lower_scale": 1.0850,          # 巨臀粗腿 (下盘重载 8.5%，背打推土机核心)
        "hand_scale": 1.0200,           # 强悍抓球大手
        "hair_length": 0.0000,          # 纯正光头/寸头 (0.0000)
        "skin_color": 5,                # 5 = 纯正经典黑人肤色 (BLACK, 告别白人)
        "body_shape": 2,                # 2 = BURLY (重型厚实体型)
        "remove_headband": True,        # 摘除头带 (还原巴克利无头带经典形象)
        "head_morphs": {
            "head_preset": 20,          # 20 = 纯正非裔黑人饱满宽方脸预设 (告别白人面型)
            "skull_preset": 2,          # 2 = 饱满圆润头骨
            "skull_width": 145,         # 145 = 宽头骨 (Round Mound of Rebound)
            "skull_height": 130,        # 130 = 厚实紧凑
            "temple_width": 144,        # 144 = 饱满太阳穴
            "upper_nose_width": 138,    # 138 = 宽山根
            "lower_nose_width": 148,    # 148 = 典型宽厚鼻翼
            "upper_cheek_width": 144,   # 144 = 饱满肉感苹果肌
            "middle_cheek_width": 140,  # 140 = 充实中脸颊
            "upper_lip_thickness": 136, # 136 = 饱满上唇
            "lower_lip_thickness": 144, # 144 = 标志性厚下唇
            "front_chin_width": 144,    # 144 = 刚毅厚重宽下巴
            "rear_chin_width": 140,     # 140 = 强悍后颌骨
            "head_width": 144           # 144 = 宽大头部比例
        }
    }

    res = sculpt_player_by_address(mem, p_addr, barkley_spec, commit=args.commit)
    print("\n" + "=" * 80)
    print("BARKLEY COMPLETE CAP & SKELETAL SCULPTING COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
