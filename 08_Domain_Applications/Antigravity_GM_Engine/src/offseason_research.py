"""Offline P0 inventory. Reads selected archived facts, never attaches to a game.

Presence of a decoded field is deliberately separate from offseason semantics.
This module has no path for promoting evidence to a verified game executor.
"""
import json
from pathlib import Path
import re
import sqlite3


CONTRACT_FIELDS = (
    "years_left_on_contract", "original_contract_years", "contract_option",
    "extension_length", "extension_option", "bird_years",
    *(f"contract_year_{i}" for i in range(1, 7)),
)
BLOCKERS = (
    "OFFSEASON_SAFE_GATE_NOT_FOUND", "NATIVE_AI_SIGNING_NOT_CONTAINED",
    "CONTRACT_TRANSITION_NOT_VERIFIED", "SIGNING_ELIGIBILITY_NOT_VERIFIED",
    "EXECUTOR_NOT_VERIFIED", "CROSS_SEASON_PERSISTENCE_NOT_VERIFIED",
)


def load_json(path):
    return Path(path).read_text(encoding="utf-8-sig")


def child(root, relative):
    root = Path(root).resolve()
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("Path leaves the selected archive")
    return candidate


def output_directory(root, relative):
    """Research/simulation artifacts must remain inside the local _exports tree."""
    base = (Path(root) / "_exports").resolve()
    output = (Path(root) / relative).resolve()
    if not output.is_relative_to(base) or output == base:
        raise ValueError("Output must be a child of _exports")
    return output


def inspect_archive(root, save_id):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", save_id):
        raise ValueError("Invalid archive save identifier")
    root = Path(root).resolve()
    published = root / "published"
    pointer = json.loads(load_json(published / "saves" / save_id / "latest.json"))
    if pointer.get("save_id") != save_id:
        raise ValueError("Archive pointer belongs to another save")
    batch = child(published, pointer["batch_path"])
    expected_parent = (published / "saves" / save_id / "batches").resolve()
    if batch.parent != expected_parent or batch.name != pointer["batch_id"]:
        raise ValueError("Archive pointer selects another save/batch")
    league = json.loads(load_json(batch / "league.json"))
    update = json.loads(load_json(batch / "data_update.json"))
    if update.get("save_id") != save_id:
        raise ValueError("Archive data update belongs to another save")
    ids, player_count, schedules, clauses = set(), 0, 0, {}
    finance = {name: 0 for name in ("total_salary", "payroll", "budget", "cash")}
    for state in league["teams"]:
        abbreviation = state["team_abbr"]
        if not re.fullmatch(r"[A-Z0-9]{2,4}", abbreviation):
            raise ValueError("Invalid archive team abbreviation")
        team = json.loads(load_json(child(batch, f"teams/{abbreviation}.json")))
        tid = team["identity"]["team_id"]
        if tid in ids or tid != state["team_id"]:
            raise ValueError("Ambiguous archived team identity")
        ids.add(tid)
        for name in finance:
            if team["state"].get(name) is not None:
                finance[name] += 1
        for player in team["roster"]:
            player_count += 1
            schedule = player.get("contract_salary_schedule")
            if isinstance(schedule, list) and len(schedule) == 6 and all(v is not None for v in schedule):
                schedules += 1
            contract = player.get("source_details", {}).get("contract", {})
            for name in CONTRACT_FIELDS:
                if contract.get(name, {}).get("value") is not None:
                    clauses[name] = clauses.get(name, 0) + 1
    schema = {"status": "ARCHIVE_DB_ABSENT", "tables": {}}
    db = root / "database" / "saves" / save_id / "league_state.sqlite"
    if db.is_file():
        # Never use save_context.create_or_open_save: research must not initialize,
        # migrate, or refresh a database. Close the read-only connection explicitly.
        connection = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            connection.execute("PRAGMA query_only=ON")
            schema["status"] = "READ_ONLY_ARCHIVE_INSPECTED"
            for table in ("player_source_details", "player_monthly_stats",
                          "team_monthly_stats", "seasons", "market_free_agents"):
                exists = connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
                ).fetchone()
                if exists:
                    columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')]
                    # Only selected snapshot rows; never dump player raw_struct.
                    snapshot_id = update.get("snapshot_id")
                    count = None
                    if "snapshot_id" in columns and snapshot_id:
                        count = connection.execute(
                            f'SELECT count(*) FROM "{table}" WHERE snapshot_id=?', (snapshot_id,)
                        ).fetchone()[0]
                    schema["tables"][table] = {"columns": columns, "selected_snapshot_rows": count}
        finally:
            connection.close()
    return {
        "save_id": save_id, "batch_id": pointer["batch_id"], "snapshot_id": update.get("snapshot_id"),
        "data_updated_at": pointer["data_updated_at"], "game_date": pointer.get("game_date"),
        "evidence_scope": "HISTORICAL_ARCHIVE_FIELD_AVAILABILITY_ONLY",
        "team_count": len(ids), "roster_count": player_count,
        "six_salary_slots_present": schedules, "contract_fields_present": clauses,
        "team_finance_fields_present": finance, "league_rule_values": league.get("rules", {}),
        "database": schema,
        "expiry_pool": None, "free_agency_status": "UNKNOWN",
        "warning": "Archived monthly fields do not prove expiry, legal cap room, or current live state.",
    }


def inventory(root, save_id):
    root = Path(root)
    profile = json.loads(load_json(root / "config/memory_field_profile.json"))
    definitions = {f["name"]: f for f in profile["fields"]["PLAYER"]}
    fields = [{"name": name, "profile": definitions.get(name),
               "availability": "PROFILE_DEFINED" if name in definitions else "UNKNOWN",
               "offseason_semantics": "NOT_VERIFIED"} for name in CONTRACT_FIELDS]
    return {
        "schema_version": 1, "task_id": "DEV_20261017_04", "stage": "P0",
        "status": "PARTIAL_RESEARCH_REAL_GAME_GATES_UNVERIFIED",
        "game_attached": False, "game_writes": 0, "season_advances": 0,
        "profile_version": profile["profile_version"], "fields": fields,
        "archived_field_inventory": inspect_archive(root, save_id),
        "season_rule_source": "CONFIGURED_NOT_LIVE_CBA",
        "blockers": list(BLOCKERS),
        "stage_permissions": {"P1_SYNTHETIC_SIMULATION": True,
                              "P1_REAL_GAME_LEGALITY": False, "P2": False, "P3": False},
        "unknowns": ["offseason_phase", "native_ai_signing_control", "free_agent_directory",
                     "rfa_and_qualifying_offer", "service_years", "asking_salary",
                     "next_season_salary_slot_semantics", "validated_signing_exceptions",
                     "available_roster_slots", "cash_units_sign_and_tax_settlement",
                     "native_signing_operation_and_persistence"],
    }
