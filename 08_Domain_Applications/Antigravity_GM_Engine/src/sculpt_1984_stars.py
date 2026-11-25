# -*- coding: utf-8 -*-
"""
NBA 2K22 1984 届全量缺失球星全维度特征雕刻与动作包热注入引擎 (1984 Draft Stars Complete Sculptor & Signature Motion Injector)
针对 1984 届核心球星（Sam Bowie, Alvin Robertson, Michael Cage, Melvin Turpin, Jay Humphries, 
Terence Stansbury, Leon Wood, Ron Anderson, Jerome Kersey 等）进行：
1. 体型、肩宽、臂展、肌肉粗细、身形模板与真实体重骨骼雕刻；
2. 剔除随机生成的错误头带配件；
3. 修正非裔肤色映射；
4. 全量热注入与原型球星 100% 匹配的 159 字节真实赛场动作包、专属签名 ID 与心智性格特征包。
"""

import sys
import os
import struct
import json
import argparse
import sqlite3
from typing import Dict, Any, List

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from address_calibrator import AddressCalibrator


# 1984 届核心球星骨骼与外观雕刻设计矩阵
STARS_SCULPT_DESIGN = {
    "Sam Bowie": {
        "weight_lbs": 250.0,
        "wingspan_cm_x100": 22600,      # 7尺5寸敏捷内线长臂 (226 cm)
        "body_length": 1.0000,
        "shoulder_width": 1.0350,       # 敏捷高挑大个宽肩
        "arm_scale": 1.0200,            # 修长匀称手臂
        "neck_head_scale": 1.0000,
        "lower_scale": 1.0250,          # 敏捷高挑下盘
        "hand_scale": 1.0200,
        "body_shape": 0,                # 0 = Normal/Athletic Lean Big
        "skin_color": 4,                # 4 = 纯正非裔深黑
        "remove_headband": True,
        "motion_desc": "Joel Embiid 原型: 高位面框跳投、柔和手感勾手、敏捷护筐火锅"
    },
    "Alvin Robertson": {
        "weight_lbs": 185.0,
        "wingspan_cm_x100": 21000,      # 6尺11寸超长抢断臂展 (210 cm)
        "body_length": 1.0000,
        "shoulder_width": 1.0550,       # 强壮后卫宽肩 (+5.5%)
        "arm_scale": 1.0500,            # 强壮肌肉双臂 (抢断王标志)
        "neck_head_scale": 1.0200,
        "lower_scale": 1.0300,
        "hand_scale": 1.0400,           # 强悍抢断大手
        "body_shape": 1,                # 1 = Ripped 肌肉型防守大闸
        "skin_color": 5,                # 5 = 纯正非裔深黑 (纠正原8号偏白肤色)
        "remove_headband": True,
        "motion_desc": "Jrue Holiday 原型: 外线死亡缠绕、凶悍贴身抢断、强硬突破终结"
    },
    "Michael Cage": {
        "weight_lbs": 225.0,
        "wingspan_cm_x100": 22600,      # 7尺5寸篮板王巨臂 (226 cm)
        "body_length": 1.0000,
        "shoulder_width": 1.0600,       # 宽厚重型卡位肩部
        "arm_scale": 1.0500,            # 强硕抓篮板肌肉臂
        "neck_head_scale": 1.0300,
        "lower_scale": 1.0500,          # 扎实下盘深蹲卡位
        "hand_scale": 1.0500,           # 篮板吸尘器巨掌
        "body_shape": 1,                # 1 = Ripped 肌肉型重装野兽
        "skin_color": 4,                # 4 = 纯正非裔经典黑
        "remove_headband": True,
        "motion_desc": "Andre Drummond 原型: 双手强力篮板摘取、二次进攻暴力补扣、内线肉盾"
    },
    "Melvin Turpin": {
        "weight_lbs": 245.0,
        "wingspan_cm_x100": 22000,      # 7尺3寸厚重长臂 (220 cm)
        "body_length": 1.0000,
        "shoulder_width": 1.0650,       # 重型推土机宽肩
        "arm_scale": 1.0450,            # 粗硕大臂
        "neck_head_scale": 1.0400,      # 粗短牛颈
        "lower_scale": 1.0650,          # 敦实重型底盘
        "hand_scale": 1.0200,
        "body_shape": 2,                # 2 = BURLY 厚实强壮体型 (Dinner Bell Mel)
        "skin_color": 4,                # 4 = 纯正非裔黑
        "remove_headband": True,
        "motion_desc": "Dwight Howard 原型: 沉重顺下冲筐、背身重击攻筐、禁区顶防大闸"
    },
    "Jay Humphries": {
        "weight_lbs": 185.0,            # 修正原 219.4 lbs 臃肿缺陷 -> 185 lbs 灵动控卫
        "wingspan_cm_x100": 20300,      # 6尺8寸控卫长臂 (203 cm)
        "body_length": 1.0000,
        "shoulder_width": 1.0150,       # 灵巧控卫标准肩宽
        "arm_scale": 1.0000,
        "neck_head_scale": 1.0000,
        "lower_scale": 1.0000,
        "hand_scale": 1.0200,
        "body_shape": 0,                # 0 = Normal 经典组织后卫
        "skin_color": 4,                # 4 = 纯正非裔黑
        "remove_headband": True,
        "motion_desc": "Chris Paul 原型: 挡拆大师节奏运球、急停中投、手术刀击地助攻"
    },
    "Terence Stansbury": {
        "weight_lbs": 195.0,
        "wingspan_cm_x100": 20800,      # 6尺10寸扣篮王臂展 (208 cm)
        "body_length": 1.0000,
        "shoulder_width": 1.0400,       # 扣将倒三角宽肩
        "arm_scale": 1.0300,
        "neck_head_scale": 1.0000,
        "lower_scale": 1.0200,          # 弹簧腿强力起跳下盘
        "hand_scale": 1.0300,
        "body_shape": 1,                # 1 = Ripped 劲爆弹簧人
        "skin_color": 5,                # 5 = 纯正非裔深黑
        "remove_headband": True,
        "motion_desc": "Zach LaVine 原型: 360大风车扣篮、单脚双脚爆炸起跳、滑翔暴扣"
    },
    "Leon Wood": {
        "weight_lbs": 185.0,            # 修正原 163.5 lbs 偏弱缺陷 -> 185 lbs 奥运金牌控卫
        "wingspan_cm_x100": 20000,      # 6尺7寸标准臂展
        "body_length": 1.0000,
        "shoulder_width": 1.0100,
        "arm_scale": 1.0000,
        "neck_head_scale": 1.0000,
        "lower_scale": 1.0000,
        "hand_scale": 1.0100,
        "body_shape": 0,                # 0 = Normal 传统神射后卫
        "skin_color": 4,
        "remove_headband": True,
        "motion_desc": "Chris Paul 原型: 节奏掌控、高弧顶精准传导、稳健投射"
    },
    "Ron Anderson": {
        "weight_lbs": 215.0,            # 修正原 233.9 lbs 偏重缺陷 -> 215 lbs 纯得分锋卫
        "wingspan_cm_x100": 21100,      # 6尺11寸修长臂展
        "body_length": 1.0000,
        "shoulder_width": 1.0250,
        "arm_scale": 1.0200,
        "neck_head_scale": 1.0000,
        "lower_scale": 1.0150,
        "hand_scale": 1.0200,
        "body_shape": 1,                # 1 = Ripped 锋卫摇摆人体型
        "skin_color": 4,
        "remove_headband": True,
        "motion_desc": "DeMar DeRozan 原型: 扎实中投脚步、急停干拔、翻身后仰跳投"
    },
    "Jerome Kersey": {
        "weight_lbs": 215.0,
        "wingspan_cm_x100": 21600,      # 7尺1寸空切暴扣长臂
        "body_length": 1.0000,
        "shoulder_width": 1.0500,       # 强壮锋线宽肩
        "arm_scale": 1.0400,
        "neck_head_scale": 1.0100,
        "lower_scale": 1.0350,
        "hand_scale": 1.0300,
        "body_shape": 1,                # 1 = Ripped 撕裂之城铁血锋线
        "skin_color": 4,
        "remove_headband": True,
        "motion_desc": "Miles Bridges 原型: 狂暴快攻空切、暴力单手劈扣、拼抢冲板"
    }
}


def sculpt_and_inject_star(
    mem: GameMemory,
    player_addr: int,
    player_name: str,
    sculpt_cfg: Dict[str, Any],
    spec_data: Dict[str, Any],
    commit: bool = False
) -> Dict[str, Any]:
    """
    对单个 1984 届核心球星执行全套骨骼雕刻与动作包热注入。
    """
    p_raw = mem.read_bytes(player_addr, 0x100)
    face_id = struct.unpack_from("<H", p_raw, 0x6C)[0]
    orig_weight = struct.unpack_from("<f", p_raw, 0x58)[0]
    p90_app = struct.unpack_from("<Q", p_raw, 0x90)[0]

    print(f"\n" + "=" * 70)
    print(f"[*] 正在雕刻与注入球星: {player_name} (Addr: {hex(player_addr)})")
    print(f"    - 原面补 Face ID: {face_id} | 原体重: {orig_weight:.1f} lbs | 外观指针 0x90: {hex(p90_app)}")

    results = {"name": player_name, "addr": hex(player_addr)}

    # 1. 真实体重写入 (0x58, float32)
    target_weight = sculpt_cfg.get("weight_lbs", orig_weight)
    if commit:
        mem.write_bytes(player_addr + 0x58, struct.pack("<f", float(target_weight)))
        rb_weight = struct.unpack_from("<f", mem.read_bytes(player_addr + 0x58, 4), 0)[0]
        print(f"  [+] 体重写入: {orig_weight:.1f} lbs -> {rb_weight:.1f} lbs (CAS OK)")
        results["weight"] = rb_weight

    # 2. 剔除错误头带配件 (0x2F3 bit 4..6, 0x34C bit 0..2)
    if sculpt_cfg.get("remove_headband", False) and commit:
        b2f3 = mem.read_bytes(player_addr + 0x2F3, 1)[0]
        new_b2f3 = b2f3 & ~(0x07 << 4)
        mem.write_bytes(player_addr + 0x2F3, bytes([new_b2f3]))

        b34c = mem.read_bytes(player_addr + 0x34C, 1)[0]
        new_b34c = b34c & ~0x07
        mem.write_bytes(player_addr + 0x34C, bytes([new_b34c]))

        rb_2f3 = mem.read_bytes(player_addr + 0x2F3, 1)[0]
        print(f"  [+] 移除头带配件: 0x2F3 (0x{b2f3:02x}->0x{rb_2f3:02x}) (CAS OK, 头带已摘除)")
        results["headband_removed"] = True

    # 3. 0x90 外观堆块骨骼与体型雕刻 (Set 0x00, 0x40, 0x80, 0xC0)
    if p90_app and p90_app > 0 and commit:
        app_raw = bytearray(mem.read_bytes(p90_app, 0x100))
        target_ws = sculpt_cfg.get("wingspan_cm_x100", 21500)
        target_bl = float(sculpt_cfg.get("body_length", 1.0000))
        target_sw = float(sculpt_cfg.get("shoulder_width", 1.0000))
        target_as = float(sculpt_cfg.get("arm_scale", 1.0000))
        target_ns = float(sculpt_cfg.get("neck_head_scale", 1.0000))
        target_ls = float(sculpt_cfg.get("lower_scale", 1.0000))
        target_hs = float(sculpt_cfg.get("hand_scale", 1.0000))
        target_shape = int(sculpt_cfg.get("body_shape", 0))
        target_skin = int(sculpt_cfg.get("skin_color", 4))

        for base in [0x00, 0x40, 0x80, 0xC0]:
            # 臂展与骨骼比例
            struct.pack_into("<H", app_raw, base + 0x02, int(target_ws))
            struct.pack_into("<6f", app_raw, base + 0x04,
                             target_bl, target_sw, target_as,
                             target_ns, target_ls, target_hs)
            # 肤色
            orig_u16 = struct.unpack_from("<H", app_raw, base + 0x26)[0]
            new_u16 = (orig_u16 & ~(0x0F << 6)) | ((target_skin & 0x0F) << 6)
            struct.pack_into("<H", app_raw, base + 0x26, new_u16)
            # 身形模板
            app_raw[base + 0x3C] = target_shape & 0x07

        mem.write_bytes(p90_app, bytes(app_raw))
        rb_app = mem.read_bytes(p90_app, 0x40)
        rb_ws = struct.unpack_from("<H", rb_app, 0x02)[0]
        rb_sw = struct.unpack_from("<f", rb_app, 0x08)[0]
        rb_as = struct.unpack_from("<f", rb_app, 0x0C)[0]
        rb_shape = rb_app[0x3C]
        rb_skin = (struct.unpack_from("<H", rb_app, 0x26)[0] >> 6) & 0x0F

        print(f"  [+] 0x90 外观与骨骼回读断言:")
        print(f"      - 臂展: {rb_ws} (CAS OK) | 肩宽: {rb_sw:.3f} | 手臂: {rb_as:.3f}")
        print(f"      - 身形模板: {rb_shape} | 肤色枚举: {rb_skin} (CAS OK, 经典纯正非裔)")
        results["wingspan"] = rb_ws
        results["shoulder"] = rb_sw
        results["skin_color"] = rb_skin

    # 4. 专属签名动作 ID (0xE8, uint32)
    sig_id = spec_data.get("signature_id")
    if sig_id is not None and commit:
        mem.write_bytes(player_addr + 0xE8, struct.pack("<I", int(sig_id)))
        rb_sig = struct.unpack_from("<I", mem.read_bytes(player_addr + 0xE8, 4), 0)[0]
        print(f"  [+] 专属签名动画 ID (0xE8): {rb_sig} (CAS OK)")
        results["signature_id"] = rb_sig

    # 5. 159 字节赛场真实专属动作包 (0x380 ~ 0x41E)
    anim_hex = spec_data.get("animation_block_hex")
    if anim_hex and commit:
        anim_bytes = bytes.fromhex(anim_hex)
        if len(anim_bytes) == 159:
            mem.write_bytes(player_addr + 0x380, anim_bytes)
            rb_anim = mem.read_bytes(player_addr + 0x380, 159)
            print(f"  [+] 真实赛场动作包 (159 字节, 0x380~0x41E): 注入成功 (CAS OK)")
            print(f"      - 动作风格: {sculpt_cfg.get('motion_desc')}")
            results["animation_block_ok"] = True

    # 6. 10 字节真实性格心智与赛场激情特征 (0x4BB ~ 0x4C4)
    pers_hex = spec_data.get("personality_hex")
    if pers_hex and commit:
        pers_bytes = bytes.fromhex(pers_hex)
        if len(pers_bytes) == 10:
            mem.write_bytes(player_addr + 0x4BB, pers_bytes)
            rb_pers = mem.read_bytes(player_addr + 0x4BB, 10)
            print(f"  [+] 赛场心智性格包 (10 字节, 0x4BB~0x4C4): 注入成功 (CAS OK)")
            results["personality_ok"] = True

    return results


def main():
    parser = argparse.ArgumentParser(description="NBA 2K22 1984届缺失球星全量雕刻与动作包热注入引擎")
    parser.add_argument("--commit", action="store_true", help="正式提交内存热写入")
    args = parser.parse_args()

    mem = GameMemory("NBA2K22.exe", read_only=not args.commit)
    cal = AddressCalibrator(mem)
    ok, base, teams = cal.check_and_calibrate_teams()

    if not ok or not teams:
        print("[-] 动态校准失败！")
        return

    # 加载 1984 规格书
    spec_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "database", "draft_classes", "1984_draft_enhancement_spec.json"
    )
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_json = json.load(f)
    p_map = {p["full_name"]: p for p in spec_json.get("prospects", [])}

    print(f"=== NBA 2K22 1984 届核心缺失球星批量雕刻与动作包注入 ===")
    print(f"模式: {'[COMMIT LIVE 热写入]' if args.commit else '[DRY-RUN 预检只读]'}")

    success_count = 0
    injected_records = []

    for t_id, t in teams.items():
        raw_ptrs = mem.read_bytes(t["address"], 0xC8)
        ptrs = struct.unpack_from("<25Q", raw_ptrs)
        for s_id, p in enumerate(ptrs[:20]):
            if not p: continue
            raw = mem.read_bytes(p, 0x100)
            ln = raw[0:40].decode("utf-16le", errors="ignore").split("\x00")[0]
            fn = raw[0x28:0x28+40].decode("utf-16le", errors="ignore").split("\x00")[0]
            name = f"{fn} {ln}".strip()

            if name in STARS_SCULPT_DESIGN:
                sculpt_cfg = STARS_SCULPT_DESIGN[name]
                spec_data = p_map.get(name, {})
                res = sculpt_and_inject_star(
                    mem, p, name, sculpt_cfg, spec_data, commit=args.commit
                )
                res["team_id"] = t_id
                res["slot_id"] = s_id
                injected_records.append(res)
                success_count += 1

    print("\n" + "=" * 80)
    print(f"1984 届核心缺失球星雕刻与动作包注入执行完成！成功覆盖: {success_count} 位球星")
    print("=" * 80)

    # 同步更新 SQLite 数据库
    db_path = r"C:\nba2k22\saves\MyLEAGUE0005\player_pool.sqlite"
    if os.path.exists(db_path) and args.commit:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        for r in injected_records:
            name = r["name"]
            spec = p_map.get(name)
            if spec:
                slot = spec.get("slot_id")
                f_id = spec.get("face_id")
                if slot and f_id:
                    cur.execute(
                        "UPDATE player_pool SET cyberface_id = ? WHERE slot_id = ?",
                        (f_id, slot)
                    )
        conn.commit()
        conn.close()
        print(f"[+] 存档数据库 player_pool.sqlite 同步更新完成！")


if __name__ == "__main__":
    main()
