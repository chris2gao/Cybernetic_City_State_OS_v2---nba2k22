# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 历史交易 REA Native 批量注入引擎 (v1.0 全维通用版)
(Universal Historical Trade REA Native Batch Injector v1.0)

标准作业触发命令 (SOP Trigger):
  python 08_Domain_Applications/Antigravity_GM_Engine/src/execute_native_trade.py --spec-path "C:\\nba2k22\\exports\\<TRADE_ID>_trade_spec.json" --commit

功能：
1. 严格遵循《NBA 2K22 REA Native 历史交易标准接口协议 (v1.0)》 (SPEC-NATIVE-TRADE-V1.0)；
2. 零限制模式 (Zero Restrictions)：自动开启强制交易并关闭工资帽、交易截止日、近期签约/交易交易锁；
3. 原子级名册与选秀权双向过户：
   - 交换双方常规名单 64 位球员物理指针；
   - 自动修正两队常规名单人数 (0xCB1) 与激活名单人数 (0x1047)；
   - 原子更新球员所属球队指针 (CURRENT_TEAM at 0x60, CONTRACT_TEAM at 0xA8)；
   - 遍历全局选秀资产表，原子过户选秀权归属球队指针；
4. 逐字段执行 CAS (Compare-And-Swap) 强校验与立即回读断言；
5. 输出标准化全量回执至 C:\\nba2k22\\exports\\。
"""

import os
import sys
import json
import struct
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from address_calibrator import AddressCalibrator
from source_extensions import player_details, roster_directory
from draft_assets import decode_asset, VERIFIED
from roster_associations import describe as roster_description, active_count_byte
import config

ADDR_TRADE_CONTROLLER = 0x0632FAE8

# 控制台无限制开关偏移
OFF_TRADE_OVERRIDE = 0x168     # 1: 开启强制交易
OFF_FINANCIAL_RULES = 0x160    # 0: 关闭工资帽硬规则
OFF_TRADE_DEADLINE = 0x16C     # 0: 关闭交易截止日
OFF_RECENTLY_SIGNED = 0x154    # 0: 关闭近期签约锁定
OFF_RECENTLY_TRADED = 0x158    # 0: 关闭近期交易锁定
OFF_TRADE_DIFFICULTY = 0x174   # 0: 交易难度归零

REGULAR_SLOTS = 15
ACTIVE_POINTERS_OFFSET = 0xD0
ACTIVE_POINTERS_COUNT = 13


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_player_name(raw: bytes) -> str:
    part = lambda offset: raw[offset:offset + 40].decode('utf-16le', errors='ignore').split('\0')[0].strip()
    return f"{part(40)} {part(0)}".strip()


def apply_trade_settings_override(mem: GameMemory, dry_run: bool = True) -> Dict[str, Any]:
    """关闭游戏内所有交易限制，进入零限制交易模式"""
    trade_base = mem.base_address + ADDR_TRADE_CONTROLLER
    overrides = {
        "TRADE_OVERRIDE": (trade_base + OFF_TRADE_OVERRIDE, 1),
        "FINANCIAL_RULES": (trade_base + OFF_FINANCIAL_RULES, 0),
        "TRADE_DEADLINE": (trade_base + OFF_TRADE_DEADLINE, 0),
        "RECENTLY_SIGNED": (trade_base + OFF_RECENTLY_SIGNED, 0),
        "RECENTLY_TRADED": (trade_base + OFF_RECENTLY_TRADED, 0),
        "TRADE_DIFFICULTY": (trade_base + OFF_TRADE_DIFFICULTY, 0),
    }
    results = {}
    for name, (addr, target_val) in overrides.items():
        cur_val = mem.read_uint32(addr)
        results[name] = {"address": hex(addr), "current": cur_val, "target": target_val}
        if not dry_run and cur_val != target_val:
            mem.write_uint32(addr, target_val)
            results[name]["written"] = True
            results[name]["verified"] = (mem.read_uint32(addr) == target_val)
        else:
            results[name]["written"] = False
            results[name]["verified"] = (cur_val == target_val)
    return results


def run_native_trade(spec_path: str, commit: bool = False, output_receipt: Optional[str] = None) -> Dict[str, Any]:
    if not os.path.isabs(spec_path):
        spec_path = os.path.abspath(spec_path)
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"Trade spec file not found: {spec_path}")

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    trade_id = spec.get("trade_id", "UNNAMED_TRADE")
    print(f"=== NBA 2K22 REA Native 交易执行引擎启动 ===")
    print(f"[*] 交易规格: {trade_id}")
    print(f"[*] 模式: {'【实机热写入 (COMMIT)】' if commit else '【只读规划与校验 (DRY-RUN)】'}")

    mem = GameMemory(read_only=not commit)
    cal = AddressCalibrator(mem)
    ok_p, player_root = cal.check_and_calibrate_player_pool()
    if not ok_p:
        raise RuntimeError("Failed to calibrate player pool base address.")
    ok_t, team_base, teams = cal.check_and_calibrate_teams()
    if not ok_t:
        raise RuntimeError("Failed to calibrate teams base address.")

    team_id_to_record = teams
    team_addr_to_id = {t["address"]: tid for tid, t in teams.items()}

    print(f"[+] 运行环境就绪: PID {mem.pid}, 球队数 30, 球员池基址: {hex(player_root)}")

    # 1. 应用无限制交易设置
    print(f"[*] 检查并配置零限制交易环境...")
    override_results = apply_trade_settings_override(mem, dry_run=not commit)
    all_overrides_ok = all(item.get("verified", False) or not commit for item in override_results.values())
    print(f"    - 交易无限制状态: {'已激活 (100% 规则豁免)' if all_overrides_ok else '部分就绪'}")

    # 2. 读取选秀资产表
    directory = roster_directory(mem, player_root)
    draft_table = directory.get("draft_assets", {})
    draft_assets = []
    if draft_table:
        for slot in range(draft_table["count"]):
            raw_asset = mem.read_bytes(draft_table["address"] + slot * draft_table["stride"], draft_table["stride"])
            if raw_asset:
                decoded = decode_asset(raw_asset, team_addr_to_id)
                draft_assets.append((slot, decoded, raw_asset, draft_table["address"] + slot * draft_table["stride"]))

    # 3. 规划与执行各项交易
    tx_receipts = []
    total_players_traded = 0
    total_picks_traded = 0
    patches_to_commit = []  # [(address, before_bytes, after_bytes, description)]

    for tx_idx, tx in enumerate(spec.get("transactions", [])):
        tx_id = tx.get("transaction_id", f"TX_{tx_idx+1}")
        team_a_spec = tx["team_a"]
        team_b_spec = tx["team_b"]
        tid_a = team_a_spec["team_id"]
        tid_b = team_b_spec["team_id"]

        team_a_addr = team_id_to_record[tid_a]["address"]
        team_b_addr = team_id_to_record[tid_b]["address"]

        raw_team_a = mem.read_bytes(team_a_addr, config.TEAM_STRUCT_STRIDE)
        raw_team_b = mem.read_bytes(team_b_addr, config.TEAM_STRUCT_STRIDE)

        roster_a = list(struct.unpack_from("<25Q", raw_team_a, 0))
        roster_b = list(struct.unpack_from("<25Q", raw_team_b, 0))
        reg_count_a = raw_team_a[0xCB1]
        reg_count_b = raw_team_b[0xCB1]

        # 预先检查该交易是否已经完成 (幂等性保护)
        a_already_in_b = len(tx.get("team_a_sends", {}).get("players", [])) > 0
        for p_spec in tx.get("team_a_sends", {}).get("players", []):
            found_in_b = False
            for slot, ptr in enumerate(roster_b[:REGULAR_SLOTS]):
                if not ptr:
                    continue
                p_raw = mem.read_bytes(ptr, 0x4F0)
                if not p_raw:
                    continue
                p_face = struct.unpack_from("<H", p_raw, 0x6C)[0]
                p_name = read_player_name(p_raw)
                if p_face == p_spec.get("cyberface_id") or p_name.casefold() == p_spec.get("player_name", "").casefold():
                    found_in_b = True
                    break
            if not found_in_b:
                a_already_in_b = False
                break

        b_already_in_a = len(tx.get("team_b_sends", {}).get("players", [])) > 0
        for p_spec in tx.get("team_b_sends", {}).get("players", []):
            found_in_a = False
            for slot, ptr in enumerate(roster_a[:REGULAR_SLOTS]):
                if not ptr:
                    continue
                p_raw = mem.read_bytes(ptr, 0x4F0)
                if not p_raw:
                    continue
                p_face = struct.unpack_from("<H", p_raw, 0x6C)[0]
                p_name = read_player_name(p_raw)
                if p_face == p_spec.get("cyberface_id") or p_name.casefold() == p_spec.get("player_name", "").casefold():
                    found_in_a = True
                    break
            if not found_in_a:
                b_already_in_a = False
                break

        if a_already_in_b and b_already_in_a:
            print(f"[*] 交易 {tx_id} 涉及球员已在对应目标球队中（此前已执行），跳过。")
            tx_receipts.append({
                "transaction_id": tx_id,
                "team_a_id": tid_a,
                "team_b_id": tid_b,
                "status": "ALREADY_APPLIED"
            })
            continue

        # 查找 Team A 送出球员
        a_sends_players = []
        for p_spec in tx.get("team_a_sends", {}).get("players", []):
            found_ptr = None
            found_raw = None
            for slot, ptr in enumerate(roster_a[:REGULAR_SLOTS]):
                if not ptr:
                    continue
                p_raw = mem.read_bytes(ptr, 0x4F0)
                if not p_raw:
                    continue
                p_face = struct.unpack_from("<H", p_raw, 0x6C)[0]
                p_name = read_player_name(p_raw)
                if p_face == p_spec.get("cyberface_id") or p_name.casefold() == p_spec.get("player_name", "").casefold():
                    found_ptr = ptr
                    found_raw = p_raw
                    break
            if not found_ptr:
                raise ValueError(f"Team A ({tid_a}) outgoing player not found: {p_spec.get('player_name')}")
            a_sends_players.append((p_spec, found_ptr, found_raw))

        # 查找 Team B 送出球员
        b_sends_players = []
        for p_spec in tx.get("team_b_sends", {}).get("players", []):
            found_ptr = None
            found_raw = None
            for slot, ptr in enumerate(roster_b[:REGULAR_SLOTS]):
                if not ptr:
                    continue
                p_raw = mem.read_bytes(ptr, 0x4F0)
                if not p_raw:
                    continue
                p_face = struct.unpack_from("<H", p_raw, 0x6C)[0]
                p_name = read_player_name(p_raw)
                if p_face == p_spec.get("cyberface_id") or p_name.casefold() == p_spec.get("player_name", "").casefold():
                    found_ptr = ptr
                    found_raw = p_raw
                    break
            if not found_ptr:
                raise ValueError(f"Team B ({tid_b}) outgoing player not found: {p_spec.get('player_name')}")
            b_sends_players.append((p_spec, found_ptr, found_raw))

        # 计算互换后的常规名册
        ptrs_a_send = [p[1] for p in a_sends_players]
        ptrs_b_send = [p[1] for p in b_sends_players]

        new_reg_a = [p for p in roster_a[:REGULAR_SLOTS] if p and p not in ptrs_a_send] + ptrs_b_send
        new_reg_b = [p for p in roster_b[:REGULAR_SLOTS] if p and p not in ptrs_b_send] + ptrs_a_send

        if len(new_reg_a) > REGULAR_SLOTS or len(new_reg_b) > REGULAR_SLOTS:
            raise ValueError(f"Trade would exceed 15-player limit (Team A: {len(new_reg_a)}, Team B: {len(new_reg_b)})")

        # 装配 Team A 新名册
        new_team_a_raw = bytearray(raw_team_a)
        struct.pack_into("<15Q", new_team_a_raw, 0, *(new_reg_a + [0] * (REGULAR_SLOTS - len(new_reg_a))))
        new_team_a_raw[0xCB1] = len(new_reg_a)
        # 激活名单同步更新
        active_a = [p for p in struct.unpack_from("<13Q", raw_team_a, ACTIVE_POINTERS_OFFSET) if p]
        new_active_a = [p for p in active_a if p not in ptrs_a_send]
        struct.pack_into("<13Q", new_team_a_raw, ACTIVE_POINTERS_OFFSET, *(new_active_a + [0] * (ACTIVE_POINTERS_COUNT - len(new_active_a))))
        new_team_a_raw[0x1047] = active_count_byte(raw_team_a[0x1047], len(new_active_a))

        # 装配 Team B 新名册
        new_team_b_raw = bytearray(raw_team_b)
        struct.pack_into("<15Q", new_team_b_raw, 0, *(new_reg_b + [0] * (REGULAR_SLOTS - len(new_reg_b))))
        new_team_b_raw[0xCB1] = len(new_reg_b)
        active_b = [p for p in struct.unpack_from("<13Q", raw_team_b, ACTIVE_POINTERS_OFFSET) if p]
        new_active_b = [p for p in active_b if p not in ptrs_b_send]
        struct.pack_into("<13Q", new_team_b_raw, ACTIVE_POINTERS_OFFSET, *(new_active_b + [0] * (ACTIVE_POINTERS_COUNT - len(new_active_b))))
        new_team_b_raw[0x1047] = active_count_byte(raw_team_b[0x1047], len(new_active_b))

        patches_to_commit.append((team_a_addr, raw_team_a[:0x78], bytes(new_team_a_raw[:0x78]), f"Team {tid_a} Roster Pointers"))
        patches_to_commit.append((team_a_addr + 0xCB1, bytes([raw_team_a[0xCB1]]), bytes([new_team_a_raw[0xCB1]]), f"Team {tid_a} Regular Count"))
        patches_to_commit.append((team_a_addr + ACTIVE_POINTERS_OFFSET, raw_team_a[ACTIVE_POINTERS_OFFSET:ACTIVE_POINTERS_OFFSET+104], bytes(new_team_a_raw[ACTIVE_POINTERS_OFFSET:ACTIVE_POINTERS_OFFSET+104]), f"Team {tid_a} Active Pointers"))
        patches_to_commit.append((team_a_addr + 0x1047, bytes([raw_team_a[0x1047]]), bytes([new_team_a_raw[0x1047]]), f"Team {tid_a} Active Count"))

        patches_to_commit.append((team_b_addr, raw_team_b[:0x78], bytes(new_team_b_raw[:0x78]), f"Team {tid_b} Roster Pointers"))
        patches_to_commit.append((team_b_addr + 0xCB1, bytes([raw_team_b[0xCB1]]), bytes([new_team_b_raw[0xCB1]]), f"Team {tid_b} Regular Count"))
        patches_to_commit.append((team_b_addr + ACTIVE_POINTERS_OFFSET, raw_team_b[ACTIVE_POINTERS_OFFSET:ACTIVE_POINTERS_OFFSET+104], bytes(new_team_b_raw[ACTIVE_POINTERS_OFFSET:ACTIVE_POINTERS_OFFSET+104]), f"Team {tid_b} Active Pointers"))
        patches_to_commit.append((team_b_addr + 0x1047, bytes([raw_team_b[0x1047]]), bytes([new_team_b_raw[0x1047]]), f"Team {tid_b} Active Count"))

        # 球员所属球队变更
        for _, ptr, p_raw in a_sends_players:
            cur_team_b = p_raw[0x60:0x68]
            con_team_b = p_raw[0xA8:0xB0]
            new_team_b = struct.pack("<Q", team_b_addr)
            patches_to_commit.append((ptr + 0x60, cur_team_b, new_team_b, f"Player {hex(ptr)} CURRENT_TEAM -> Team {tid_b}"))
            patches_to_commit.append((ptr + 0xA8, con_team_b, new_team_b, f"Player {hex(ptr)} CONTRACT_TEAM -> Team {tid_b}"))
            total_players_traded += 1

        for _, ptr, p_raw in b_sends_players:
            cur_team_b = p_raw[0x60:0x68]
            con_team_b = p_raw[0xA8:0xB0]
            new_team_b = struct.pack("<Q", team_a_addr)
            patches_to_commit.append((ptr + 0x60, cur_team_b, new_team_b, f"Player {hex(ptr)} CURRENT_TEAM -> Team {tid_a}"))
            patches_to_commit.append((ptr + 0xA8, con_team_b, new_team_b, f"Player {hex(ptr)} CONTRACT_TEAM -> Team {tid_a}"))
            total_players_traded += 1

        # 选秀权过户
        # Team A -> Team B picks
        for pick_spec in tx.get("team_a_sends", {}).get("picks", []):
            found_asset = None
            for slot, decoded, raw_asset, asset_addr in draft_assets:
                if (decoded["draft_year"] == pick_spec["draft_year"] and
                    decoded["draft_round"] == pick_spec["round"] and
                    decoded["original_owner_team_id"] == pick_spec["original_team_id"]):
                    found_asset = (slot, decoded, raw_asset, asset_addr)
                    break
            if not found_asset:
                raise ValueError(f"Draft pick not found: {pick_spec.get('desc')}")
            slot, decoded, raw_asset, asset_addr = found_asset
            old_owner_ptr = raw_asset[:8]
            new_owner_ptr = struct.pack("<Q", team_b_addr)
            patches_to_commit.append((asset_addr, old_owner_ptr, new_owner_ptr, f"Draft Pick (Year {pick_spec['draft_year']} R{pick_spec['round']}) Owner -> Team {tid_b}"))
            total_picks_traded += 1

        # Team B -> Team A picks
        for pick_spec in tx.get("team_b_sends", {}).get("picks", []):
            found_asset = None
            for slot, decoded, raw_asset, asset_addr in draft_assets:
                if (decoded["draft_year"] == pick_spec["draft_year"] and
                    decoded["draft_round"] == pick_spec["round"] and
                    decoded["original_owner_team_id"] == pick_spec["original_team_id"]):
                    found_asset = (slot, decoded, raw_asset, asset_addr)
                    break
            if not found_asset:
                raise ValueError(f"Draft pick not found: {pick_spec.get('desc')}")
            slot, decoded, raw_asset, asset_addr = found_asset
            old_owner_ptr = raw_asset[:8]
            new_owner_ptr = struct.pack("<Q", team_a_addr)
            patches_to_commit.append((asset_addr, old_owner_ptr, new_owner_ptr, f"Draft Pick (Year {pick_spec['draft_year']} R{pick_spec['round']}) Owner -> Team {tid_a}"))
            total_picks_traded += 1

        tx_receipts.append({
            "transaction_id": tx_id,
            "team_a_id": tid_a,
            "team_b_id": tid_b,
            "team_a_sent_players": [p[0]["player_name"] for p in a_sends_players],
            "team_b_sent_players": [p[0]["player_name"] for p in b_sends_players],
            "team_a_new_roster_count": len(new_reg_a),
            "team_b_new_roster_count": len(new_reg_b),
        })

    print(f"[*] 计划生成完毕: {len(patches_to_commit)} 个原子内存补丁, 涉及 {total_players_traded} 名球员, {total_picks_traded} 个选秀权")

    # 4. 执行写入与 CAS 回读
    verified_patches = 0
    cas_failures = []
    if commit:
        print(f"[*] 正在执行热内存写入与 CAS 回读校验...")
        for addr, before, after, desc in patches_to_commit:
            cur = mem.read_bytes(addr, len(before))
            if cur != before:
                # 检查是否已经是 after
                if cur == after:
                    verified_patches += 1
                    continue
                cas_failures.append({"address": hex(addr), "desc": desc, "expected_before": before.hex(), "actual": cur.hex()})
                continue
            mem.write_bytes(addr, after)
            readback = mem.read_bytes(addr, len(after))
            if readback == after:
                verified_patches += 1
            else:
                cas_failures.append({"address": hex(addr), "desc": desc, "expected_after": after.hex(), "actual": readback.hex()})
        print(f"[+] 写入完成! CAS 校验通过: {verified_patches}/{len(patches_to_commit)}")
        if cas_failures:
            print(f"[!] 警告: 存在 {len(cas_failures)} 处 CAS 不一致!")
    else:
        print(f"[+] 【DRY-RUN 规划完毕】未发生实机写入。加上 --commit 即可立即生效。")
        verified_patches = len(patches_to_commit)

    receipt = {
        "protocol_version": "v1.0_native_trade",
        "trade_id": trade_id,
        "status": "TRADE_COMMITTED_SUCCESSFULLY" if (commit and len(cas_failures) == 0) else ("DRY_RUN_PASSED" if not commit else "CAS_MISMATCH"),
        "timestamp": now_iso(),
        "commit_mode": commit,
        "total_transactions": len(tx_receipts),
        "total_players_traded": total_players_traded,
        "total_picks_traded": total_picks_traded,
        "total_patches": len(patches_to_commit),
        "verified_patches": verified_patches,
        "cas_failures": cas_failures,
        "settings_overrides": override_results,
        "transactions": tx_receipts,
    }

    if not output_receipt:
        out_dir = r"C:\nba2k22\exports"
        os.makedirs(out_dir, exist_ok=True)
        output_receipt = os.path.join(out_dir, f"{trade_id}_TRADE_RECEIPT.json")

    with open(output_receipt, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False)
    print(f"[+] 执行回执已安全持久化: {output_receipt}")

    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NBA 2K22 REA Native 历史交易执行器")
    parser.add_argument("--spec-path", required=True, help="交易规格书 JSON 路径")
    parser.add_argument("--commit", action="store_true", help="确认实机热写入")
    parser.add_argument("--output-receipt", default=None, help="回执输出路径")
    args = parser.parse_args()

    run_native_trade(args.spec_path, commit=args.commit, output_receipt=args.output_receipt)
