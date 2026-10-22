# -*- coding: utf-8 -*-
"""Verified historical-rookie tagging and draft-class lookup.

The game stores a player-type byte in each 0x4F0 player-pool record. The
current historical-rookie classifier uses the high three bits of byte 0x70,
calibrated against the known Iverson and Kobe rookie-clone examples.
This module is intentionally independent of process-memory access so both the
capture script and database-driven GM code use the same deterministic rule.
"""
import os
import sqlite3
from pathlib import Path
from contextlib import closing
from typing import Any, Dict, Iterable, List, Optional, Tuple


HISTORICAL_ROOKIE_TAG_OFFSET = 0x70
HISTORICAL_ROOKIE_TAG_MASK = 0xE0
HISTORICAL_ROOKIE_TAG_VALUE = 0xE0
PLAYER_POOL_STRIDE = 0x4F0


def is_historical_rookie(raw_struct: Optional[bytes]) -> Optional[bool]:
    """Classify a player directly from the player-pool structure at 0x70.

    ``None`` means the source structure is absent or too short to inspect.
    The raw structure remains the persisted evidence; no decoded rookie flag
    or duplicate tag column is needed in SQLite.
    """
    if raw_struct is not None:
        try:
            raw = bytes(raw_struct)
        except (TypeError, ValueError):
            raw = b""
        if len(raw) > HISTORICAL_ROOKIE_TAG_OFFSET:
            raw_tag = raw[HISTORICAL_ROOKIE_TAG_OFFSET]
            return (raw_tag & HISTORICAL_ROOKIE_TAG_MASK) == HISTORICAL_ROOKIE_TAG_VALUE
    return None


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalized_name(row: Dict[str, Any]) -> str:
    full_name = str(row.get("full_name") or "").strip()
    if not full_name:
        full_name = " ".join(
            part for part in (str(row.get("first_name") or "").strip(), str(row.get("last_name") or "").strip())
            if part
        )
    return " ".join(full_name.casefold().split())


def select_historical_rookies(
    rows: Iterable[Any],
    year: int,
    limit: Optional[int] = 60,
) -> List[Dict[str, Any]]:
    """Filter, order, and de-duplicate verified rookies from database rows.

    Draft-year metadata alone never qualifies a clone. The marker is decoded
    directly from raw_struct; no persisted boolean or duplicate tag column is
    consulted.
    Duplicate clones are collapsed by normalized name, year, round, and pick.
    """
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative or None")

    unique: Dict[Tuple[str, int, int, int], Dict[str, Any]] = {}
    for source_row in rows:
        row = dict(source_row)
        if _to_int(row.get("draft_year")) != int(year):
            continue

        rookie_match = is_historical_rookie(row.get("raw_struct"))
        if rookie_match is not True:
            continue

        # Exclude undrafted/invalid placeholders while retaining older NBA
        # drafts that legitimately used more than two rounds.
        draft_round = _to_int(row.get("draft_round"))
        draft_pick = _to_int(row.get("draft_pick"))
        if not (1 <= draft_round <= 15 and 1 <= draft_pick <= 60):
            continue

        name_key = _normalized_name(row)
        if not name_key:
            continue

        row["draft_year"] = int(year)
        # Older snapshots used 30 + round-two-pick even for drafts with fewer
        # than 30 first-round selections. Normalize those unverified values to
        # NULL at query time as well as fixing future captures.
        row["overall_pick"] = draft_pick if draft_round == 1 else None
        key = (name_key, int(year), draft_round, draft_pick)
        # Rows arrive in slot order. Keep the first eligible clone for a
        # given draft identity, making duplicate resolution deterministic.
        unique.setdefault(key, row)

    selected = list(unique.values())
    selected.sort(key=lambda row: (
        _to_int(row.get("draft_round"), 99),
        _to_int(row.get("draft_pick"), 99),
        _to_int(row.get("slot_id"), 0),
    ))

    if limit is not None:
        selected = selected[:limit]

    # ``pick_proj`` is an ordinal among verified candidates, not the original
    # NBA overall pick and not a destination slot in the game's draft board.
    # ``overall_pick`` is retained only where the capture script can verify it.
    for index, row in enumerate(selected, start=1):
        row["pick_proj"] = index
    return selected


def query_historical_draft_class(
    db_path: str,
    year: int,
    limit: Optional[int] = 60,
    *, for_native_injection: bool = False,
) -> List[Dict[str, Any]]:
    """Read a verified historical draft class from a player-pool SQLite DB."""
    resolved_path = os.path.abspath(db_path)
    if not os.path.isfile(resolved_path):
        raise FileNotFoundError(f"球员池数据库不存在: {resolved_path}")

    uri = Path(resolved_path).as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        conn.row_factory = sqlite3.Row
        columns = {row[1] for row in conn.execute("PRAGMA table_info(player_pool)")}
        if not columns:
            raise RuntimeError(f"数据库中不存在 player_pool 表: {resolved_path}")
        if "draft_year" not in columns:
            raise RuntimeError("player_pool 缺少 draft_year 字段，无法查询历史选秀名单")

        requested_columns = (
            "slot_id", "full_name", "first_name", "last_name", "draft_year",
            "draft_round", "draft_pick", "overall_pick", "position", "position_name",
            "cyberface_id", "raw_potential", "potential", "memory_addr", "raw_struct",
        )
        select_terms = [
            f'"{name}"' if name in columns else f'NULL AS "{name}"'
            for name in requested_columns
        ]
        sql = (
            f'SELECT {", ".join(select_terms)} FROM player_pool '
            'WHERE draft_year = ? ORDER BY slot_id ASC'
        )
        rows = conn.execute(sql, (int(year),)).fetchall()
        from player_potential_mask import tables
        masked_source = 'player_potential_masks' in tables(conn)

    if for_native_injection:
        if masked_source:
            raise PermissionError('SANITIZED_PLAYER_POOL_NOT_NATIVE_INJECTION_SOURCE')
        raise PermissionError('NATIVE_INJECTION_REQUIRES_INDEPENDENT_CALIBRATED_SOURCE_ADAPTER')
    results = select_historical_rookies(rows, year=year, limit=limit)
    if masked_source:
        from player_potential_mask import MARKERS
        for row in results:
            row.update(MARKERS)
            row['mask_version']='potential_v1'
    return results


def preflight_native_rookie_source(rows, source):
    """Validate an independent native DTO; this does not inject or approve writes.

    No private/fresh source collector exists here. A future controlled adapter
    must supply calibrated identity/binding; a GM-sanitized pool is never one.
    """
    from player_potential_mask import PLAYER_BYTES
    if source.get('source_role') == 'GM_SANITIZED' or source.get('mask_version') or source.get('potential_mask_version'):
        raise PermissionError('SANITIZED_PLAYER_POOL_NOT_NATIVE_INJECTION_SOURCE')
    if source.get('source_role') not in ('FRESH_NATIVE_CALIBRATED','NATIVE_INJECTION_PRIVATE') or not source.get('native_binding'):
        raise PermissionError('INDEPENDENT_NATIVE_INJECTION_SOURCE_REQUIRED')
    for row in rows:
        if row.get('player_raw_masked') or row.get('mask_version') or row.get('potential_mask_version') or row.get('source_role') == 'GM_SANITIZED':
            raise PermissionError('SANITIZED_PLAYER_POOL_NOT_NATIVE_INJECTION_SOURCE')
        if len(row.get('raw_struct',b'')) != PLAYER_BYTES or not row.get('native_identity'):
            raise ValueError('NATIVE_INJECTION_PLAYER_IDENTITY_AND_FULL_RAW_REQUIRED')
    return dict(status='NATIVE_SOURCE_PREFLIGHT_ONLY_NOT_WRITE_AUTHORIZATION',rows=len(rows),
                native_binding=source['native_binding'],execution_authorized=False)
