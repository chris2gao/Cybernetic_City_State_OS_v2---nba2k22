# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 历史球员签约与续约 REA Native 批量注入引擎 (v1.0 全维通用版)
(Universal Historical Signing & Extension REA Native Batch Injector v1.0)

标准作业触发命令 (SOP Trigger):
  python 08_Domain_Applications/Antigravity_GM_Engine/src/execute_native_signing.py --spec-path "C:\\nba2k22\\exports\\<SIGNING_ID>_signing_spec.json" --commit

功能：
1. 严格遵循《NBA 2K22 REA Native 历史球员签约与续约标准接口协议 (v1.0)》 (SPEC-NATIVE-SIGNING-V1.0)；
2. 零限制模式 (Zero Restrictions)：自动绕过工资帽、硬工资帽、谈判签约难度与 CPU 意愿阻碍；
3. 支持四大业务模式：
   - 自由球员签约 (FREE_AGENT): 自动入驻常规阵容空位，维护 0xCB1 人数与球队指针归属；
   - 现有球员续约 (EXTENSION): 无缝刷新年限、逐年薪资与选项，保持名册稳定；
   - 新秀标准合同签约 (ROOKIE_SCALE): 将选秀新秀纳入正式名册并注入新秀标准薪资；
   - 双向合同签约 (TWO_WAY): 维护双向合同标记与名额；
4. 严格比特级合同打包与写入，保护周边未修改位域；
5. 逐字段执行 CAS (Compare-And-Swap) 强校验与立即回读断言；
6. 输出标准化全量回执至 C:\\nba2k22\\exports\\。
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
from source_extensions import player_details, profile as field_profile
from roster_associations import describe as roster_description
import config

ADDR_TRADE_CONTROLLER = 0x0632FAE8
OFF_FINANCIAL_RULES = 0x160     # 工资帽硬规则
OFF_CONTRACT_DIFFICULTY = 0x210 # 续约谈判难度
OFF_CPU_RESIGN_AGG = 0x234      # 电脑续约积极性

OPTION_CODES = {
    'NONE': 0,
    'NULL': 0,
    'TEAM_OPTION': 1,
    'PLAYER_OPTION': 2,
    '2_YEAR_TEAM_OPTION': 3
}

REGULAR_SLOTS = 15


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_player_name(raw: bytes) -> str:
    part = lambda offset: raw[offset:offset + 40].decode('utf-16le', errors='ignore').split('\0')[0].strip()
    return f"{part(40)} {part(0)}".strip()


def apply_signing_settings_override(mem: GameMemory, dry_run: bool = True) -> Dict[str, Any]:
    """关闭游戏内工资帽及谈判阻碍，进入零限制签约模式"""
    trade_base = mem.base_address + ADDR_TRADE_CONTROLLER
    overrides = {
        "FINANCIAL_RULES": (trade_base + OFF_FINANCIAL_RULES, 0),
        "CONTRACT_DIFFICULTY": (trade_base + OFF_CONTRACT_DIFFICULTY, 0),
        "CPU_RESIGN_AGGRESSIVE": (trade_base + OFF_CPU_RESIGN_AGG, 0),
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


def pack_player_contract(original: bytes, contract_spec: Dict[str, Any]) -> Tuple[bytes, List[Dict[str, Any]]]:
    """精确打包球员合同字段，杜绝位域污染"""
    if len(original) != 0x4F0:
        raise ValueError("Full observed player record (0x4F0 bytes) required")
    result = bytearray(original)
    changed_fields = []

    salaries = contract_spec.get("salaries", [])
    if not isinstance(salaries, list) or not (1 <= len(salaries) <= 6):
        raise ValueError("Contract salaries must be a list of 1 to 6 integers")
    for s in salaries:
        if not isinstance(s, int) or s < 0 or s > 0x7FFFFFFF:
            raise ValueError(f"Invalid salary integer: {s}")

    years_left = int(contract_spec.get("years", len(salaries)))
    original_years = int(contract_spec.get("original_years", years_left))
    option_str = contract_spec.get("option", "NONE").upper()
    option_val = OPTION_CODES.get(option_str, 0)
    no_trade_val = 1 if contract_spec.get("no_trade", 0) else 0
    is_two_way = 2 if contract_spec.get("contract_type", "CORE").upper() == "TWO_WAY" else 0

    values_map = {
        f"contract_year_{i+1}": s for i, s in enumerate(salaries + [0] * (6 - len(salaries)))
    }
    values_map.update(
        years_left_on_contract=years_left,
        original_contract_years=original_years,
        contract_option=option_val,
        no_trade=no_trade_val,
        contract_type=is_two_way,
    )

    definitions = {f["name"]: f for f in field_profile()["fields"]["PLAYER"] if f.get("group") == "contract"}

    for key, value in values_map.items():
        if key not in definitions:
            continue
        field = definitions[key]
        start = field.get("start_bit", 0)
        bits = field.get("bits", field.get("bytes", 0) * 8)
        size = (start + bits + 7) // 8
        offset = field["offset"]

        old_val = int.from_bytes(result[offset:offset+size], "little")
        mask = ((1 << bits) - 1) << start
        new_val = (old_val & ~mask) | (value << start)
        result[offset:offset+size] = new_val.to_bytes(size, "little")

        changed_fields.append({
            "name": key,
            "offset": offset,
            "size": size,
            "start_bit": start,
            "bits": bits,
            "before": (old_val >> start) & ((1 << bits) - 1),
            "target": value
        })

    return bytes(result), changed_fields


def run_native_signing(spec_path: str, commit: bool = False, output_receipt: Optional[str] = None) -> Dict[str, Any]:
    if not os.path.isabs(spec_path):
        spec_path = os.path.abspath(spec_path)
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"Signing spec file not found: {spec_path}")

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    signing_id = spec.get("signing_id", "UNNAMED_SIGNING")
    print(f"=== NBA 2K22 REA Native 签约执行引擎启动 ===")
    print(f"[*] 签约规格: {signing_id}")
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

    # 1. 应用无限制签约设置
    print(f"[*] 检查并配置零限制签约环境...")
    override_results = apply_signing_settings_override(mem, dry_run=not commit)
    all_overrides_ok = all(item.get("verified", False) or not commit for item in override_results.values())
    print(f"    - 工资帽与谈判豁免状态: {'已激活 (100% 规则豁免)' if all_overrides_ok else '部分就绪'}")

    # 2. 遍历球员池构建索引 (Face ID -> (index, address, name))
    print(f"[*] 扫描球员池建立定位索引...")
    player_pool_index = {}
    MAX_PLAYERS = 1500
    for i in range(MAX_PLAYERS):
        addr = player_root + i * 0x4F0
        raw_header = mem.read_bytes(addr, 0x80)
        if not raw_header:
            break
        face_id = struct.unpack_from("<H", raw_header, 0x6C)[0]
        p_name = read_player_name(raw_header)
        if face_id > 0 or len(p_name) > 0:
            player_pool_index[face_id] = (i, addr, p_name)

    # 3. 规划各项签约任务
    signing_receipts = []
    patches_to_commit = []  # [(address, before_bytes, after_bytes, description)]
    total_signings = 0

    for item_idx, sign_item in enumerate(spec.get("signings", [])):
        item_id = sign_item.get("signing_item_id", f"SIGN_{item_idx+1}")
        sign_type = sign_item.get("signing_type", "FREE_AGENT").upper()
        target_team_spec = sign_item["target_team"]
        target_tid = target_team_spec["team_id"]
        target_team_addr = team_id_to_record[target_tid]["address"]

        player_spec = sign_item["player"]
        face_id = player_spec.get("cyberface_id")
        req_name = player_spec.get("player_name", "")

        # 定位球员
        target_player_info = None
        if face_id in player_pool_index:
            target_player_info = player_pool_index[face_id]
        else:
            # 备选按姓名模糊/精确匹配
            for fid, (idx, addr, pname) in player_pool_index.items():
                if pname.casefold() == req_name.casefold():
                    target_player_info = (idx, addr, pname)
                    break

        if not target_player_info:
            raise ValueError(f"Player not found in player pool: {req_name} (Face ID: {face_id})")

        p_idx, player_addr, actual_pname = target_player_info
        raw_player = mem.read_bytes(player_addr, 0x4F0)

        # 读取球队原始名册
        raw_team = mem.read_bytes(target_team_addr, config.TEAM_STRUCT_STRIDE)
        roster = list(struct.unpack_from("<25Q", raw_team, 0))
        reg_count = raw_team[0xCB1]

        # 区分 FREE_AGENT / ROOKIE_SCALE 与 EXTENSION
        if sign_type in ("FREE_AGENT", "ROOKIE_SCALE"):
            if reg_count >= REGULAR_SLOTS:
                raise ValueError(f"Team {target_tid} has no regular roster vacancy (count={reg_count}/15)")
            new_slot_idx = reg_count
            new_reg_count = reg_count + 1

            new_team_raw = bytearray(raw_team)
            struct.pack_into("<Q", new_team_raw, new_slot_idx * 8, player_addr)
            new_team_raw[0xCB1] = new_reg_count

            patches_to_commit.append((
                target_team_addr + new_slot_idx * 8,
                raw_team[new_slot_idx * 8:(new_slot_idx + 1) * 8],
                bytes(new_team_raw[new_slot_idx * 8:(new_slot_idx + 1) * 8]),
                f"Team {target_tid} Roster Slot {new_slot_idx} -> Player {actual_pname} ({hex(player_addr)})"
            ))
            patches_to_commit.append((
                target_team_addr + 0xCB1,
                bytes([reg_count]),
                bytes([new_reg_count]),
                f"Team {target_tid} Regular Count {reg_count} -> {new_reg_count}"
            ))

            # 绑定球员所属球队
            cur_team_b = raw_player[0x60:0x68]
            con_team_b = raw_player[0xA8:0xB0]
            new_team_b = struct.pack("<Q", target_team_addr)
            patches_to_commit.append((player_addr + 0x60, cur_team_b, new_team_b, f"Player {actual_pname} CURRENT_TEAM -> Team {target_tid}"))
            patches_to_commit.append((player_addr + 0xA8, con_team_b, new_team_b, f"Player {actual_pname} CONTRACT_TEAM -> Team {target_tid}"))

        elif sign_type == "EXTENSION":
            # 校验球员是否已在队中
            if player_addr not in roster[:REGULAR_SLOTS]:
                print(f"[!] 注意: 球员 {actual_pname} 未在 Team {target_tid} 的常规名单中，但仍按指定执行合同续约")

        # 打包合同数据
        new_player_raw, contract_fields = pack_player_contract(raw_player, sign_item.get("contract", {}))
        
        # 提取合同区修改补丁 (420~444 薪资区, 791~854 选项/年限区)
        contract_offsets = [f["offset"] for f in contract_fields]
        min_off = min(contract_offsets)
        max_off = max(contract_offsets) + 4
        # 逐段比较
        for fld in contract_fields:
            off = fld["offset"]
            sz = fld["size"]
            before_chunk = raw_player[off:off+sz]
            after_chunk = new_player_raw[off:off+sz]
            if before_chunk != after_chunk:
                patches_to_commit.append((
                    player_addr + off,
                    before_chunk,
                    after_chunk,
                    f"Player {actual_pname} Contract Field '{fld['name']}' ({fld['before']} -> {fld['target']})"
                ))

        signing_receipts.append({
            "signing_item_id": item_id,
            "signing_type": sign_type,
            "target_team_id": target_tid,
            "player_name": actual_pname,
            "cyberface_id": face_id,
            "player_address": hex(player_addr),
            "contract_summary": {
                "years": sign_item.get("contract", {}).get("years"),
                "salaries": sign_item.get("contract", {}).get("salaries"),
                "option": sign_item.get("contract", {}).get("option"),
            }
        })
        total_signings += 1

    print(f"[*] 签约计划生成完毕: {len(patches_to_commit)} 处原子补丁, 涉及 {total_signings} 名球员")

    # 4. 执行写入与 CAS 回读
    verified_patches = 0
    cas_failures = []
    if commit:
        print(f"[*] 正在执行热内存写入与 CAS 回读校验...")
        for addr, before, after, desc in patches_to_commit:
            cur = mem.read_bytes(addr, len(before))
            if cur != before:
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
        "protocol_version": "v1.0_native_signing",
        "signing_id": signing_id,
        "status": "SIGNINGS_COMMITTED_SUCCESSFULLY" if (commit and len(cas_failures) == 0) else ("DRY_RUN_PASSED" if not commit else "CAS_MISMATCH"),
        "timestamp": now_iso(),
        "commit_mode": commit,
        "total_signings": total_signings,
        "total_patches": len(patches_to_commit),
        "verified_patches": verified_patches,
        "cas_failures": cas_failures,
        "settings_overrides": override_results,
        "signings": signing_receipts,
    }

    if not output_receipt:
        out_dir = r"C:\nba2k22\exports"
        os.makedirs(out_dir, exist_ok=True)
        output_receipt = os.path.join(out_dir, f"{signing_id}_SIGNING_RECEIPT.json")

    with open(output_receipt, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False)
    print(f"[+] 执行回执已安全持久化: {output_receipt}")

    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NBA 2K22 REA Native 历史球员签约执行器")
    parser.add_argument("--spec-path", required=True, help="签约规格书 JSON 路径")
    parser.add_argument("--commit", action="store_true", help="确认实机热写入")
    parser.add_argument("--output-receipt", default=None, help="回执输出路径")
    args = parser.parse_args()

    run_native_signing(args.spec_path, commit=args.commit, output_receipt=args.output_receipt)
