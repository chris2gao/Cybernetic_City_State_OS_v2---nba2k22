# -*- coding: utf-8 -*-
"""Deterministic read-only audit of a captured save snapshot.

This program is a scripted verifier, not an AI. It compares stored rows with
live memory, checks source coverage and NULL policy, and binds the result to
the exact database rows and player-pool file that were audited.
"""
import os
import sys
import json
import random
import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from address_calibrator import AddressCalibrator
from save_context import resolve_context
from snapshot_integrity import (
    file_sha256, sanitize_calibration_report, snapshot_digest,
    snapshot_row_counts, write_json_atomic,
)
from historical_rookies import is_historical_rookie
import config


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "database", "league_state.sqlite")
SNAPSHOTS_DIR = os.path.join(PROJECT_DIR, "database", "snapshots")
POS_NAMES = {0: "PG", 1: "SG", 2: "SF", 3: "PF", 4: "C"}
TEAM_OBSERVED_COLUMNS = (
    "total_salary", "payroll", "budget", "staff_budget", "cash", "chemistry",
    "fan_interest", "monthly_gate_revenue", "merch_revenue", "media_revenue",
    "ticket_courtside", "ticket_lower", "ticket_upper", "poe_off_pace",
    "poe_fastbreak", "poe_off_reb", "poe_def_reb", "poe_on_ball",
    "poe_off_ball", "poe_pnr_def", "poe_help_def",
)
TEAM_UNOBSERVED_COLUMNS = (
    "total_games", "total_wins", "total_losses", "win_pct", "conf_rank",
    "month_games", "month_wins", "month_losses", "month_win_pct", "streak",
    "home_w_l", "away_w_l", "ppg", "opp_ppg", "net_rating", "ortg", "drtg",
    "pace", "fg_pct", "three_pt_pct", "three_pt_att", "ft_pct", "rpg", "apg", "tov_pg",
)
PLAYER_OBSERVED_COLUMNS = (
    "position", "three_point_rating", "pass_accuracy_rating", "speed_rating",
    "perimeter_defense_rating", "salary_current_year", "contract_years_left", "face_id",
)
PLAYER_UNOBSERVED_COLUMNS = (
    "overall_rating", "games_played", "minutes_per_game", "ppg", "rpg", "apg",
    "spg", "bpg", "tov_pg", "fg_pct", "three_pt_pct", "ft_pct",
    "true_shooting_pct", "plus_minus", "usage_rate", "per", "injury_status",
    "injury_type", "injury_days_left",
)


def _all_null_clause(columns) -> str:
    return " AND ".join(f'"{column}" IS NULL' for column in columns)


def _all_present_clause(columns) -> str:
    return " AND ".join(f'"{column}" IS NOT NULL' for column in columns)


def run_ai_sampling_audit(
    snapshot_id: str = "2021-2022_M01_NOV",
    sample_size: int = 4,
    save_id: Optional[str] = None,
    db_path: Optional[str] = None,
    snapshots_dir: Optional[str] = None,
    player_pool_db_path: Optional[str] = None,
) -> Dict:
    if not 1 <= sample_size <= config.TEAM_MAX_COUNT:
        raise ValueError("sample_size 必须在 1 到 30 之间")
    context = resolve_context(save_id)
    db_path = os.path.abspath(db_path or context["db_path"])
    snapshots_dir = os.path.abspath(snapshots_dir or context["snapshots_dir"])
    player_pool_db_path = os.path.abspath(player_pool_db_path or context["player_pool_db_path"])
    manifest_file = os.path.join(snapshots_dir, f"ingest_manifest_{snapshot_id}.json")
    audit_file = os.path.join(snapshots_dir, f"ai_sampling_audit_{snapshot_id}.json")
    if not os.path.isfile(manifest_file):
        raise FileNotFoundError(f"缺少该批次入库清单: {manifest_file}")
    with open(manifest_file, "r", encoding="utf-8") as source:
        manifest = json.load(source)
    if manifest.get("status") != "INGEST_SUCCESS" or manifest.get("snapshot_id") != snapshot_id:
        raise RuntimeError("入库清单状态或 snapshot_id 不匹配，拒绝质检。")

    checks: Dict[str, bool] = {}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("BEGIN")
    mem = None
    try:
        quick_check = conn.execute("PRAGMA quick_check").fetchone()[0]
        checks["sqlite_quick_check"] = quick_check == "ok"
        fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        checks["foreign_key_integrity"] = len(fk_violations) == 0

        current_digest = snapshot_digest(conn, snapshot_id)
        counts = snapshot_row_counts(conn, snapshot_id)
        binding = manifest.get("batch_binding", {})
        checks["snapshot_digest_matches_manifest"] = (
            binding.get("snapshot_digest_sha256") == current_digest
        )
        checks["snapshot_counts_match_manifest"] = all(
            manifest.get("ingested_counts", {}).get(key) == value
            for key, value in {
                "team_monthly_stats": counts["team_monthly_stats"],
                "player_monthly_stats": counts["player_monthly_stats"],
                "player_growth_history": counts["player_growth_history"],
                "team_monthly_evaluations": counts["team_monthly_evaluations"],
                "staff_pool_observations": counts["staff_pool_observations"],
            }.items()
        )
        season_row = conn.execute(
            """SELECT s.season_year, s.season_code, s.salary_cap,
                      s.luxury_tax_threshold, s.first_apron,
                      s.historical_draft_class_year
               FROM monthly_snapshots AS m
               JOIN seasons AS s ON s.season_year=m.season_year
               WHERE m.snapshot_id=?""",
            (snapshot_id,),
        ).fetchone()
        captured_rules = manifest.get("season_rules", {})
        checks["season_rules_match_manifest"] = bool(
            season_row
            and all(season_row[key] == captured_rules.get(key) for key in (
                "season_year", "season_code", "salary_cap", "luxury_tax_threshold",
                "first_apron", "historical_draft_class_year",
            ))
        )
        checks["season_rule_thresholds_valid"] = bool(
            season_row
            and season_row["salary_cap"] < season_row["luxury_tax_threshold"]
            and season_row["luxury_tax_threshold"] < season_row["first_apron"]
        )

        team_ids = {
            row[0] for row in conn.execute(
                "SELECT team_id FROM team_monthly_stats WHERE snapshot_id=?", (snapshot_id,)
            )
        }
        checks["exact_30_team_ids"] = team_ids == config.CORE_TEAM_IDS
        team_presence = conn.execute(
            f"SELECT count(*) FROM team_monthly_stats WHERE snapshot_id=? AND {_all_present_clause(TEAM_OBSERVED_COLUMNS)}",
            (snapshot_id,),
        ).fetchone()[0]
        checks["team_observed_fields_complete"] = team_presence == config.TEAM_MAX_COUNT
        extended = manifest.get('quality_metrics', {}).get('source_extension_profile') == 1
        team_new = ('total_games', 'total_wins', 'total_losses', 'win_pct', 'ppg', 'opp_ppg', 'fg_pct', 'three_pt_pct', 'ft_pct', 'rpg', 'apg', 'tov_pg')
        player_new = ('games_played', 'minutes_per_game', 'ppg', 'rpg', 'apg', 'spg', 'bpg', 'tov_pg', 'fg_pct', 'three_pt_pct', 'ft_pct')
        team_unknown = tuple(c for c in TEAM_UNOBSERVED_COLUMNS if not extended or c not in team_new)
        player_unknown = tuple(c for c in PLAYER_UNOBSERVED_COLUMNS if not extended or c not in player_new)
        team_nulls = conn.execute(
            f"SELECT count(*) FROM team_monthly_stats WHERE snapshot_id=? AND NOT ({_all_null_clause(team_unknown)})",
            (snapshot_id,),
        ).fetchone()[0]
        checks["unobserved_team_stats_are_null"] = team_nulls == 0

        player_presence = conn.execute(
            f"SELECT count(*) FROM player_monthly_stats WHERE snapshot_id=? AND {_all_present_clause(PLAYER_OBSERVED_COLUMNS)}",
            (snapshot_id,),
        ).fetchone()[0]
        player_rows = counts["player_monthly_stats"]
        checks["player_observed_fields_complete"] = player_presence == player_rows and player_rows > 0
        player_nulls = conn.execute(
            f"SELECT count(*) FROM player_monthly_stats WHERE snapshot_id=? AND NOT ({_all_null_clause(player_unknown)})",
            (snapshot_id,),
        ).fetchone()[0]
        checks["unobserved_player_stats_are_null"] = player_nulls == 0

        staff_rows = conn.execute(
            "SELECT staff_slot, first_name, last_name, raw_team_id, team_mapping_status, memory_address "
            "FROM staff_pool_observations WHERE snapshot_id=? ORDER BY staff_slot",
            (snapshot_id,),
        ).fetchall()
        allowed_staff_status = ('VERIFIED_RECIPROCAL_TEAM_ROLE', 'UNMAPPED_NOT_ASSUMED_FREE_AGENT') if extended else ('UNVERIFIED_CANDIDATE_TEAM_ID', 'UNMAPPED_RAW_TEAM_ID')
        checks["staff_team_mapping_uses_supported_evidence"] = all(
            row["team_mapping_status"] in allowed_staff_status
            for row in staff_rows
        ) and counts["staff_pool_observations"] > 0

        captured_active_player = manifest.get("calibration", {}).get("active_player", {}).get("data") or {}
        active_name = captured_active_player.get("full_name")
        active_face_id = captured_active_player.get("face_id")
        active_rows = []
        if active_name:
            active_rows = conn.execute(
                "SELECT player_name, team_id, position, three_point_rating, pass_accuracy_rating, "
                "speed_rating, perimeter_defense_rating, salary_current_year, contract_years_left, face_id "
                "FROM player_monthly_stats WHERE snapshot_id=? AND player_name=? AND face_id=? LIMIT 2",
                (snapshot_id, active_name, active_face_id),
            ).fetchall()
        active_row = active_rows[0] if len(active_rows) == 1 else None
        checks["active_player_present_in_captured_roster"] = active_row is not None
        checks["active_player_identity_unique"] = len(active_rows) == 1

        player_groups: Dict[int, List[sqlite3.Row]] = {}
        for row in conn.execute(
            "SELECT team_id, player_name, position, salary_current_year, contract_years_left, face_id, "
            "three_point_rating, pass_accuracy_rating, speed_rating, perimeter_defense_rating "
            "FROM player_monthly_stats WHERE snapshot_id=? ORDER BY team_id, player_name, face_id",
            (snapshot_id,),
        ):
            player_groups.setdefault(row["team_id"], []).append(row)
        checks["all_teams_have_rosters"] = set(player_groups) == config.CORE_TEAM_IDS and all(player_groups.values())
        captured_player_names = [
            row[0] for row in conn.execute(
                "SELECT player_name FROM player_monthly_stats WHERE snapshot_id=?",
                (snapshot_id,),
            )
        ]
        checks["captured_roster_names_valid"] = all(
            isinstance(name, str) and sum(character.isalpha() for character in name) >= 2
            for name in captured_player_names
        ) and bool(captured_player_names)

        cursor = conn.cursor()
        # A seeded PRNG makes the audit sample reproducible for the same batch.
        sample_seed = int(current_digest[:16], 16) if current_digest else 0
        rng = random.Random(sample_seed)
        team_samples = rng.sample(sorted(team_ids), min(sample_size, len(team_ids))) if team_ids else []
        teams_cross_check_pass = True

        mem = GameMemory(read_only=True)
        calibrator = AddressCalibrator(mem)
        calib_report = calibrator.run_full_calibration()
        checks["live_calibration_healthy"] = calib_report["status"] == "HEALTHY"
        if not checks["live_calibration_healthy"]:
            raise RuntimeError("实时内存校准未通过，不能给该批次签发审计结果。")
        live_active_player = calib_report.get("active_player", {}).get("data") or {}
        checks["active_player_identity_stable"] = (
            live_active_player.get("full_name") == active_name
            and live_active_player.get("face_id") == active_face_id
        )
        live_teams = calibrator._extract_teams_from_pacers(int(calib_report["teams"]["pacers_base"], 16))
        checks["live_team_ids_match_snapshot"] = set(live_teams) == team_ids == config.CORE_TEAM_IDS

        sample_teams_audit = []
        team_fields = {
            "total_salary": config.TEAM_OFFSETS["TOTAL_SALARY"],
            "payroll": config.TEAM_OFFSETS["PAYROLL"],
            "budget": config.TEAM_OFFSETS["BUDGET"],
            "chemistry": config.TEAM_OFFSETS["CHEMISTRY"],
            "fan_interest": 0xF7C,
            "ticket_courtside": 0xF98,
            "poe_off_pace": 0xEB2,
            "poe_on_ball": 0xEB7,
        }
        for tid in team_samples:
            db_row = conn.execute(
                "SELECT team_abbr, total_salary, payroll, budget, chemistry, fan_interest, "
                "ticket_courtside, poe_off_pace, poe_on_ball "
                "FROM team_monthly_stats WHERE snapshot_id=? AND team_id=?",
                (snapshot_id, tid),
            ).fetchone()
            if not db_row:
                teams_cross_check_pass = False
                continue
            addr = live_teams[tid]["address"]
            live = {
                "total_salary": mem.require_uint32(addr + team_fields["total_salary"]),
                "payroll": mem.require_uint32(addr + team_fields["payroll"]),
                "budget": mem.require_uint32(addr + team_fields["budget"]),
                "chemistry": round(mem.require_float(addr + team_fields["chemistry"]), 2),
                "fan_interest": round(mem.require_float(addr + team_fields["fan_interest"]), 2),
                "ticket_courtside": round(mem.require_float(addr + team_fields["ticket_courtside"]), 2),
                "poe_off_pace": mem.require_uint8(addr + team_fields["poe_off_pace"]),
                "poe_on_ball": mem.require_uint8(addr + team_fields["poe_on_ball"]),
            }
            stored = dict(db_row)
            field_matches = {
                field: (abs(stored[field] - value) < 0.01 if isinstance(value, float) else stored[field] == value)
                for field, value in live.items()
            }
            verified = all(field_matches.values())
            teams_cross_check_pass = teams_cross_check_pass and verified
            sample_teams_audit.append({
                "team_id": tid,
                "abbr": stored["team_abbr"],
                "field_matches": field_matches,
                "verified": verified,
            })
        checks["sampled_teams_match_live_memory"] = teams_cross_check_pass and len(sample_teams_audit) == len(team_samples)

        active_player_audit = {
            "player_name": active_name,
            "face_id": active_face_id,
            "verified": False,
        }
        if active_row is not None:
            p_addr = int(live_active_player["address"], 16)
            raw_pos = mem.require_uint8(p_addr + config.PLAYER_OFFSETS["POSITION"]) & 0x07
            active_live = {
                "position": POS_NAMES.get(raw_pos),
                "three_point_rating": config.raw_to_rating(mem.require_uint8(p_addr + config.PLAYER_OFFSETS["ATTR_THREE_POINT"])),
                "pass_accuracy_rating": config.raw_to_rating(mem.require_uint8(p_addr + config.PLAYER_OFFSETS["ATTR_PASS_ACCURACY"])),
                "speed_rating": config.raw_to_rating(mem.require_uint8(p_addr + config.PLAYER_OFFSETS["ATTR_SPEED"])),
                "perimeter_defense_rating": config.raw_to_rating(mem.require_uint8(p_addr + config.PLAYER_OFFSETS["ATTR_PERIMETER_DEF"])),
                "salary_current_year": mem.require_uint32(p_addr + config.PLAYER_OFFSETS["SALARY_YEAR_1"]) & 0x7fffffff,
                "contract_years_left": config.extract_contract_years(mem.require_uint8(p_addr + config.PLAYER_OFFSETS["CONTRACT_YEARS_LEFT"])),
                "face_id": mem.require_uint16(p_addr + config.PLAYER_OFFSETS["FACE_ID"]),
            }
            active_fields = {key: active_row[key] == value for key, value in active_live.items()}
            active_player_audit["field_matches"] = active_fields
            active_player_audit["verified"] = all(active_fields.values())
        checks["active_player_matches_live_memory"] = active_player_audit["verified"]

        player_samples_audit = []
        roster_cross_check_pass = True
        sample_tids = rng.sample(sorted(player_groups), min(5, len(player_groups))) if player_groups else []
        for tid in sample_tids:
            row = rng.choice(player_groups[tid])
            team_base = live_teams[tid]["address"]
            found_addr = None
            for slot_idx in range(0, 0xC8, 8):
                ptr = mem.require_uint64(team_base + slot_idx)
                if ptr == 0:
                    continue
                if not (0x7FF000000000 <= ptr <= 0x7FFF00000000):
                    continue
                face = mem.require_uint16(ptr + config.PLAYER_OFFSETS["FACE_ID"])
                if face != row["face_id"]:
                    continue
                ln = mem.require_utf16_string(ptr + config.PLAYER_OFFSETS["LAST_NAME"], 20).strip()
                fn = mem.require_utf16_string(ptr + config.PLAYER_OFFSETS["FIRST_NAME"], 20).strip()
                if f"{fn} {ln}".strip() == row["player_name"]:
                    found_addr = ptr
                    break
            if found_addr is None:
                roster_cross_check_pass = False
                player_samples_audit.append({"team_id": tid, "player_name": row["player_name"], "verified": False})
                continue
            live_values = {
                "position": POS_NAMES.get(mem.require_uint8(found_addr + config.PLAYER_OFFSETS["POSITION"]) & 0x07),
                "salary_current_year": mem.require_uint32(found_addr + config.PLAYER_OFFSETS["SALARY_YEAR_1"]) & 0x7fffffff,
                "contract_years_left": config.extract_contract_years(mem.require_uint8(found_addr + config.PLAYER_OFFSETS["CONTRACT_YEARS_LEFT"])),
                "three_point_rating": config.raw_to_rating(mem.require_uint8(found_addr + config.PLAYER_OFFSETS["ATTR_THREE_POINT"])),
                "pass_accuracy_rating": config.raw_to_rating(mem.require_uint8(found_addr + config.PLAYER_OFFSETS["ATTR_PASS_ACCURACY"])),
                "speed_rating": config.raw_to_rating(mem.require_uint8(found_addr + config.PLAYER_OFFSETS["ATTR_SPEED"])),
                "perimeter_defense_rating": config.raw_to_rating(mem.require_uint8(found_addr + config.PLAYER_OFFSETS["ATTR_PERIMETER_DEF"])),
            }
            matches = {field: row[field] == value for field, value in live_values.items()}
            verified = all(matches.values())
            roster_cross_check_pass = roster_cross_check_pass and verified
            player_samples_audit.append({
                "team_id": tid,
                "player_name": row["player_name"],
                "face_id": row["face_id"],
                "matches": matches,
                "verified": verified,
            })
        checks["sampled_players_match_live_memory"] = roster_cross_check_pass and len(player_samples_audit) == len(sample_tids)

        staff_samples = rng.sample(staff_rows, min(5, len(staff_rows))) if staff_rows else []
        staff_cross_check_pass = True
        staff_base = int(calib_report["staff_pool"]["base_addr"], 16)
        staff_stride = int(calib_report["staff_pool"]["stride"], 16)
        staff_audit = []
        for row in staff_samples:
            slot = row["staff_slot"]
            raw_live = mem.read_bytes(staff_base + slot * staff_stride, staff_stride)
            raw_db = conn.execute(
                "SELECT raw_struct FROM staff_pool_observations WHERE snapshot_id=? AND staff_slot=?",
                (snapshot_id, slot),
            ).fetchone()[0]
            matches = raw_live is not None and raw_live == raw_db
            staff_cross_check_pass = staff_cross_check_pass and matches
            staff_audit.append({"staff_slot": slot, "first_name": row["first_name"], "last_name": row["last_name"], "raw_bytes_match": matches})
        checks["sampled_staff_bytes_match_live_memory"] = staff_cross_check_pass and len(staff_audit) == len(staff_samples)
        if extended:
            from audit_source_extensions import audit_extensions
            checks.update(audit_extensions(conn, mem, calib_report, live_teams, snapshot_id,
                          simple_draft_assets=bool(manifest.get('quality_metrics', {}).get('simple_draft_assets'))))
        if manifest.get('quality_metrics',{}).get('coaching_tactics',{}).get('profile')==1:
            from coaching_source import audit_coaching_source
            checks.update(audit_coaching_source(conn,mem,snapshot_id))
        if manifest.get('quality_metrics',{}).get('deterministic_state_io'):
            from gm_state_io.capture_bridge import audit as audit_state_io
            checks.update(audit_state_io(conn,mem,snapshot_id))
    finally:
        if mem is not None:
            mem.close()
        conn.close()

    player_pool_ok = False
    player_pool_count = 0
    rookie_tagged_count = 0
    malformed_player_pool_names = 0
    player_pool_hash = None
    if os.path.isfile(player_pool_db_path):
        player_pool_hash = file_sha256(player_pool_db_path)
        with sqlite3.connect(f"file:{player_pool_db_path}?mode=ro", uri=True) as pool_conn:
            player_pool_count = pool_conn.execute("SELECT count(*) FROM player_pool").fetchone()[0]
            jordan_count = pool_conn.execute(
                "SELECT count(*) FROM player_pool WHERE full_name='Michael Jordan' AND cyberface_id=1759"
            ).fetchone()[0]
            hakeem_count = pool_conn.execute(
                "SELECT count(*) FROM player_pool WHERE full_name='Hakeem Olajuwon' AND cyberface_id=952"
            ).fetchone()[0]
            rookie_tagged_count = sum(
                1 for (raw_struct,) in pool_conn.execute("SELECT raw_struct FROM player_pool")
                if is_historical_rookie(raw_struct) is True
            )
            malformed_player_pool_names = sum(
                1 for (full_name,) in pool_conn.execute("SELECT full_name FROM player_pool")
                if not isinstance(full_name, str)
                or sum(character.isalpha() for character in full_name) < 2
            )
        player_binding = manifest.get("batch_binding", {})
        player_pool_ok = (
            player_pool_count == player_binding.get("player_pool_records")
            and player_pool_hash == player_binding.get("player_pool_sha256")
            and player_pool_count >= 3000
            and malformed_player_pool_names == 0
            and jordan_count > 0
            and hakeem_count > 0
            and rookie_tagged_count > 0
        )
    checks["player_pool_hash_and_anchors_valid"] = player_pool_ok
    checks["player_pool_names_valid"] = malformed_player_pool_names == 0 and player_pool_count > 0

    audit_timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest_sha256 = file_sha256(manifest_file)
    passed = all(checks.values())
    audit_result = {
        "audit_timestamp": audit_timestamp,
        "snapshot_id": snapshot_id,
        "save_id": context["save_id"],
        "verifier": "deterministic_script",
        "verdict": "PASS_VERIFIED" if passed else "REJECTED_AUDIT_FAIL",
        "checks": checks,
        "counts": counts,
        "database_digest_sha256": current_digest,
        "player_pool_sha256": player_pool_hash,
        "player_pool_records": player_pool_count,
        "historical_rookie_marker_records": rookie_tagged_count,
        "malformed_player_pool_name_count": malformed_player_pool_names,
        "foreign_key_violation_count": len(fk_violations),
        "manifest_binding": {
            "manifest_sha256": manifest_sha256,
            "manifest_timestamp": manifest.get("timestamp"),
            "manifest_snapshot_id": manifest.get("snapshot_id"),
            "snapshot_digest_sha256": current_digest,
        },
        "live_calibration": sanitize_calibration_report(calib_report),
        "sample_teams": sample_teams_audit,
        "active_player": active_player_audit,
        "sample_players": player_samples_audit,
        "sample_staff": staff_audit,
        "staff_mapping_policy": ("verified reciprocal NBA team-role links; other entries remain unmapped"
                                 if manifest.get('quality_metrics', {}).get('staff_team_mapping_verified')
                                 else "raw observations only; team ownership remains unverified"),
    }
    write_json_atomic(audit_file, audit_result)
    if not passed:
        failed = [name for name, ok in checks.items() if not ok]
        raise RuntimeError(f"质检拒绝该批次: {', '.join(failed)}。结果已写入 {audit_file}")
    print(f"[+] 脚本抽样质检通过: {snapshot_id} | DB 摘要 {current_digest[:12]} | 凭证 {audit_file}")
    return audit_result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="NBA 2K22 数据快照只读抽样审计")
    parser.add_argument("--snapshot", default="2021-2022_M01_NOV")
    parser.add_argument("--save-id", default=None)
    parser.add_argument("--sample-size", type=int, default=4)
    args = parser.parse_args()
    run_ai_sampling_audit(snapshot_id=args.snapshot, sample_size=args.sample_size, save_id=args.save_id)
