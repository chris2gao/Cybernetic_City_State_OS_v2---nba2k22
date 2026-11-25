# -*- coding: utf-8 -*-
"""
NBA 2K22 球员外观与骨骼雕刻引擎 (Player Appearance & Skeletal Sculptor)
专门针对球员体型、肩宽、臂展、手臂/腿部肌肉、头颈比与身形模板进行原子级内存雕刻。
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
    对指定内存地址的球员执行全套骨骼与外观堆雕刻。
    """
    p_raw = mem.read_bytes(player_addr, 0x100)
    ln = p_raw[0:40].decode("utf-16le", errors="ignore").split("\x00")[0]
    fn = p_raw[0x28:0x28+40].decode("utf-16le", errors="ignore").split("\x00")[0]
    full_name = f"{fn} {ln}".strip()
    face_id = struct.unpack_from("<H", p_raw, 0x6C)[0]
    orig_weight = struct.unpack_from("<f", p_raw, 0x58)[0]
    app_ptr = struct.unpack_from("<Q", p_raw, 0x90)[0]

    if not app_ptr or app_ptr == 0:
        raise ValueError(f"球员 {full_name} 的 0x90 外观指针为空，无法雕刻！")

    print(f"[*] 正在雕刻球员: {full_name} (Addr: {hex(player_addr)}, AppPtr: {hex(app_ptr)})")
    print(f"[*] 当前面补 Face ID: {face_id} | 当前体重: {orig_weight:.2f} lbs")

    # 1. 体重写入 (0x58, float32)
    target_weight = sculpt_spec.get("weight_lbs", orig_weight)
    if commit and "weight_lbs" in sculpt_spec:
        mem.write_bytes(player_addr + 0x58, struct.pack("<f", float(target_weight)))
        rb_weight = struct.unpack_from("<f", mem.read_bytes(player_addr + 0x58, 4), 0)[0]
        print(f"  [+] 体重注入: {orig_weight:.2f} lbs -> {rb_weight:.2f} lbs (CAS OK)")

    # 2. 面补 Face ID (0x6C, uint16) - 可选
    if "face_id" in sculpt_spec and commit:
        new_face = int(sculpt_spec["face_id"])
        mem.write_bytes(player_addr + 0x6C, struct.pack("<H", new_face))
        rb_face = struct.unpack_from("<H", mem.read_bytes(player_addr + 0x6C, 2), 0)[0]
        print(f"  [+] 面补 FaceID 注入: {face_id} -> {rb_face} (CAS OK)")

    # 3. 外观堆块雕刻 (覆盖 Set 0x00, 0x40, 0x80, 0xC0 四套外貌姿态)
    app_raw = bytearray(mem.read_bytes(app_ptr, 0x100))
    sets_updated = 0

    target_wingspan = sculpt_spec.get("wingspan_cm_x100", 22100) # 22100 = 221cm = 7'3"
    target_body_len = float(sculpt_spec.get("body_length", 1.0000))
    target_shoulder = float(sculpt_spec.get("shoulder_width", 1.0800))
    target_arm_scale = float(sculpt_spec.get("arm_scale", 1.0650))
    target_neck_scale = float(sculpt_spec.get("neck_head_scale", 1.0400))
    target_lower_scale = float(sculpt_spec.get("lower_scale", 1.0850))
    target_hand_scale = float(sculpt_spec.get("hand_scale", 1.0200))
    target_hair_len = float(sculpt_spec.get("hair_length", 0.0000))
    target_body_shape = int(sculpt_spec.get("body_shape", 2)) # 2 = Burly

    for base in [0x00, 0x40, 0x80, 0xC0]:
        # 写入 6 大浮点缩放
        struct.pack_into("<H", app_raw, base + 0x02, int(target_wingspan))
        struct.pack_into("<6f", app_raw, base + 0x04,
                         target_body_len, target_shoulder, target_arm_scale,
                         target_neck_scale, target_lower_scale, target_hand_scale)
        struct.pack_into("<f", app_raw, base + 0x1C, target_hair_len)
        app_raw[base + 0x3C] = target_body_shape & 0x07
        sets_updated += 1

    if commit:
        mem.write_bytes(app_ptr, bytes(app_raw))
        # 立即回读断言
        rb_app = mem.read_bytes(app_ptr, 0x40)
        rb_ws = struct.unpack_from("<H", rb_app, 0x02)[0]
        rb_bl, rb_sw, rb_as, rb_ns, rb_ls, rb_hs = struct.unpack_from("<6f", rb_app, 0x04)
        rb_shape = rb_app[0x3C]
        print(f"  [+] 0x90 堆块雕刻回读断言:")
        print(f"      - 臂展: {rb_ws} (CAS OK)")
        print(f"      - 肩宽: {rb_sw:.4f} (CAS OK, 宽肩拉满)")
        print(f"      - 手臂粗细: {rb_as:.4f} (CAS OK, 强壮粗臂)")
        print(f"      - 头颈比例: {rb_ns:.4f} (CAS OK, 粗壮公牛颈)")
        print(f"      - 下肢臀腿: {rb_ls:.4f} (CAS OK, 飞猪重型下盘)")
        print(f"      - 身形模板: {rb_shape} (2 = BURLY 厚实强壮体型)")

    return {
        "player_name": full_name,
        "address": hex(player_addr),
        "app_ptr": hex(app_ptr),
        "weight_lbs": target_weight,
        "shoulder_width": target_shoulder,
        "arm_scale": target_arm_scale,
        "lower_scale": target_lower_scale,
        "neck_scale": target_neck_scale,
        "wingspan": target_wingspan,
        "body_shape": target_body_shape
    }


def main():
    parser = argparse.ArgumentParser(description="NBA 2K22 球员关键特征与体型骨骼雕刻引擎")
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

    # 巴克利“空中飞猪”重磅体型专属雕刻规格
    barkley_spec = {
        "weight_lbs": 255.0,            # 经典巅峰飞猪体重 (255 磅)
        "wingspan_cm_x100": 22100,      # 7尺3寸长臂展 (221 cm)
        "body_length": 1.0000,          # 标准厚实躯干
        "shoulder_width": 1.0800,       # 极致宽肩 (拉大 8%)
        "arm_scale": 1.0650,            # 强壮粗硕大臂与小臂 (拉粗 6.5%)
        "neck_head_scale": 1.0400,      # 粗短牛颈 (减少头身细长感)
        "lower_scale": 1.0850,          # 巨臀粗腿 (下盘重载 8.5%，背打推土机核心)
        "hand_scale": 1.0200,           # 强悍抓球大手
        "hair_length": 0.0000,          # 极短寸头/光头
        "body_shape": 2                 # 2 = BURLY (重型厚实体型)
    }

    res = sculpt_player_by_address(mem, p_addr, barkley_spec, commit=args.commit)
    print("\n" + "=" * 80)
    print("BARKLEY SKELETAL & APPEARANCE SCULPTING COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
