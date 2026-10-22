# -*- coding: utf-8 -*-
"""Stable hashes for binding manifests, audits, and GM decisions to DB rows."""
import hashlib
import json
import os
import sqlite3
import copy
from typing import Any, Dict, Iterable


SNAPSHOT_TABLES = (
    "team_monthly_stats",
    "player_monthly_stats",
    "player_growth_history",
    "team_monthly_evaluations",
    "staff_pool_observations",
    "market_trade_block",
    "market_trade_offers",
    "market_free_agents",
)
EXTENSION_TABLES = ('player_source_details', 'staff_source_details', 'team_source_stats', 'draft_asset_observations',
                    'coaching_source_captures','coaching_team_observations',
                    'state_io_captures','state_io_objects','observed_setting_values','player_potential_masks')


def _json_value(value: Any):
    if isinstance(value, bytes):
        return {"blob_sha256": hashlib.sha256(value).hexdigest(), "length": len(value)}
    return value


def snapshot_row_counts(conn: sqlite3.Connection, snapshot_id: str) -> Dict[str, int]:
    counts = {}
    for table in SNAPSHOT_TABLES + EXTENSION_TABLES:
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        if not exists:
            counts[table] = 0
            continue
        counts[table] = conn.execute(
            f"SELECT count(*) FROM {table} WHERE snapshot_id = ?", (snapshot_id,)
        ).fetchone()[0]
    return counts


def snapshot_digest(conn: sqlite3.Connection, snapshot_id: str) -> str:
    """Hash snapshot rows plus the metadata and season rules that govern them."""
    digest = hashlib.sha256()

    snapshot_context = conn.execute(
        """SELECT snapshot_id, season_year, month_index, month_name, snapshot_date,
                  games_in_period, total_games_played, notes
           FROM monthly_snapshots WHERE snapshot_id=?""",
        (snapshot_id,),
    ).fetchone()
    if snapshot_context is None:
        digest.update(b"monthly_snapshots:MISSING\n")
    else:
        digest.update(b"monthly_snapshots:1\n")
        digest.update(json.dumps(
            [_json_value(value) for value in snapshot_context],
            ensure_ascii=False, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8"))
        digest.update(b"\n")
        season = conn.execute(
            """SELECT season_year, season_code, salary_cap, luxury_tax_threshold,
                      first_apron, second_apron, historical_draft_class_year,
                      season_status
               FROM seasons WHERE season_year=?""",
            (snapshot_context[1],),
        ).fetchone()
        if season is None:
            digest.update(b"season_rules:MISSING\n")
        else:
            digest.update(b"season_rules:1\n")
            digest.update(json.dumps(
                [_json_value(value) for value in season],
                ensure_ascii=False, separators=(",", ":"), allow_nan=False,
            ).encode("utf-8"))
            digest.update(b"\n")

    # Preserve hashes of older captures with no extension records.
    extension_tables = tuple(table for table in EXTENSION_TABLES if conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
        and conn.execute(f'SELECT 1 FROM {table} WHERE snapshot_id=? LIMIT 1', (snapshot_id,)).fetchone())
    for table in SNAPSHOT_TABLES + extension_tables:
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        if not exists:
            digest.update(f"{table}:MISSING\n".encode("utf-8"))
            continue
        columns = [
            row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
            if row[1] != "id"
        ]
        if not columns or "snapshot_id" not in columns:
            digest.update(f"{table}:INVALID_SCHEMA\n".encode("utf-8"))
            continue
        column_sql = ", ".join(f'"{column}"' for column in columns)
        rows = conn.execute(
            f"SELECT {column_sql} FROM {table} WHERE snapshot_id=? ORDER BY rowid",
            (snapshot_id,),
        ).fetchall()
        digest.update(f"{table}:{len(rows)}\n".encode("utf-8"))
        for row in rows:
            normalized = [_json_value(value) for value in row]
            digest.update(json.dumps(normalized, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8"))
            digest.update(b"\n")
    return digest.hexdigest()


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sanitize_calibration_report(report: Dict) -> Dict:
    """Keep health evidence while excluding process-specific pointer values."""
    cleaned = copy.deepcopy(report)
    cleaned.pop("module_base", None)
    for section, key in (
        ("teams", "pacers_base"),
        ("player_pool", "base_addr"),
        ("staff_pool", "base_addr"),
    ):
        cleaned.get(section, {}).pop(key, None)
    active_data = cleaned.get("active_player", {}).get("data")
    if isinstance(active_data, dict):
        active_data.pop("address", None)
    return cleaned


def write_json_atomic(path: str, payload: Dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as target:
        json.dump(payload, target, indent=2, ensure_ascii=False, allow_nan=False)
        target.flush()
        os.fsync(target.fileno())
    os.replace(temp_path, path)
