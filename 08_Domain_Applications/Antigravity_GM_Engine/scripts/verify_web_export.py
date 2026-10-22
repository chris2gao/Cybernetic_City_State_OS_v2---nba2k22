"""Compare every exported observed value to audited SQLite, including archive backups."""
import argparse
import json
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from data_context import decode_context
from export_web_gm import verify_bundle
from gm_engine import GMEngine
from save_context import save_paths
from snapshot_integrity import file_sha256, snapshot_digest


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def connect(path):
    conn = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def no_runtime_data(value):
    if isinstance(value, dict):
        if {"raw_struct", "memory_addr", "memory_address"} & value.keys():
            raise AssertionError("Runtime data leaked into the web reading surface")
        for item in value.values():
            no_runtime_data(item)
    elif isinstance(value, list):
        for item in value:
            no_runtime_data(item)
    elif isinstance(value, str) and (re.search(r"[A-Za-z]:[\\/]", value) or re.fullmatch(r"0x[0-9a-fA-F]{10,}", value)):
        raise AssertionError("Absolute machine path or runtime address leaked")


def verify(save_id):
    paths = save_paths(save_id)
    root = ROOT / "published"
    pointer = load(root / "saves" / save_id / "latest.json")
    batch = (root / pointer["batch_path"]).resolve()
    if not batch.is_relative_to(root):
        raise AssertionError("Unsafe latest pointer")
    manifest = verify_bundle(batch, pointer["manifest_sha256"])
    if manifest["save_id"] != save_id or manifest["batch_id"] != pointer["batch_id"]:
        raise AssertionError("Latest pointer belongs to another batch or career")
    audit = GMEngine(db_path=paths["db_path"], snapshots_dir=paths["snapshots_dir"], player_pool_db_path=paths["player_pool_db_path"]).verify_snapshot_gate(manifest["snapshot_id"])
    if manifest["source_binding"]["snapshot_digest_sha256"] != audit["database_digest_sha256"]:
        raise AssertionError("Export refers to a different audited database")
    for path in batch.rglob("*.json"):
        no_runtime_data(load(path))
    league, pool = connect(paths["db_path"]), connect(paths["player_pool_db_path"])
    snapshot = manifest["snapshot_id"]
    try:
        notes = league.execute("SELECT notes FROM monthly_snapshots WHERE snapshot_id=?", (snapshot,)).fetchone()[0]
        if manifest["context"] != decode_context(notes):
            raise AssertionError("Game date/context is not bound to the audited snapshot")
        if manifest["gm_decisions_allowed"] != (manifest["context"]["purpose"] == "production"):
            raise AssertionError("Validation data incorrectly marked for production decisions")
        export_league = load(batch / "league.json")
        observed_players = 0
        calculations = {row["team_id"]: row for row in load(batch / "calculations.json")["teams"]}
        for team in export_league["teams"]:
            source = league.execute("SELECT * FROM team_monthly_stats WHERE snapshot_id=? AND team_id=?", (snapshot, team["team_id"])).fetchone()
            for field in source.keys():
                if field not in {"id", "snapshot_id"} and team.get(field) != source[field]:
                    raise AssertionError(f"Team field mismatch: {team['team_id']}/{field}")
            file = load(batch / "teams" / f"{team['team_abbr']}.json")
            if file["state"] != team:
                raise AssertionError("Team file and league file disagree")
            source_players = [dict(row) for row in league.execute("SELECT * FROM player_monthly_stats WHERE snapshot_id=? AND team_id=? ORDER BY player_name,face_id", (snapshot, team["team_id"]))]
            if len(source_players) != len(file["roster"]):
                raise AssertionError("Roster size mismatch")
            for source_player, player in zip(source_players, file["roster"]):
                if {k: v for k, v in source_player.items() if k not in {"id", "snapshot_id", "player_id"}} != player:
                    raise AssertionError("Exported player values differ from SQLite")
            observed_players += len(source_players)
            calc, rules = calculations[team["team_id"]], export_league["rules"]
            if calc["salary_cap_minus_observed_payroll_proxy"] != rules["salary_cap"] - source["total_salary"] or calc["observed_roster_salary_sum"] != sum(p["salary_current_year"] for p in source_players) or calc["observed_payroll_minus_luxury_tax_line"] != source["total_salary"] - rules["luxury_tax_threshold"]:
                raise AssertionError("Deterministic financial calculation mismatch")
        staff = load(batch / "staff.json")
        source_staff = league.execute("SELECT * FROM staff_pool_observations WHERE snapshot_id=? ORDER BY staff_slot", (snapshot,)).fetchall()
        if staff["ownership_verified"] or len(staff["records"]) != len(source_staff):
            raise AssertionError("Staff coverage or ownership claim is invalid")
        for item, source in zip(staff["records"], source_staff):
            if item["team_id"] is not None or any(item[k] != source[k] for k in ("staff_slot", "first_name", "last_name", "team_mapping_status")) or item["observed_candidate_team_id"] != source["raw_team_id"]:
                raise AssertionError("Staff raw observation differs from SQLite")
        catalog = load(batch / "player_catalog/index.json")
        model_count, rookie_count, seen = 0, 0, set()
        for filenames in catalog["years"].values():
            for filename in filenames:
                for model in load(batch / filename)["records"]:
                    if model["slot_id"] in seen:
                        raise AssertionError("Duplicate model slot in catalog")
                    seen.add(model["slot_id"])
                    source = pool.execute("SELECT * FROM player_pool WHERE slot_id=?", (model["slot_id"],)).fetchone()
                    for field in source.keys():
                        if field not in {"raw_struct", "memory_addr"} and model.get(field) != source[field]:
                            raise AssertionError(f"Model field differs from SQLite: {model['slot_id']}/{field}")
                    rookie = (source["raw_struct"][0x70] & 0xE0) == 0xE0
                    if model["model_category"] != ("HISTORICAL_ROOKIE" if rookie else "OTHER_UNCLASSIFIED"):
                        raise AssertionError("Historical rookie classification mismatch")
                    rookie_count += rookie
                    model_count += 1
        if len(export_league["teams"]) != 30 or observed_players != audit["counts"]["player_monthly_stats"] or model_count != audit["player_pool_records"] or rookie_count != audit["historical_rookie_marker_records"]:
            raise AssertionError("Export coverage is incomplete")
        archive = ROOT / "_exports" / "archives" / manifest["archive"]["filename"]
        if file_sha256(str(archive)) != manifest["archive"]["sha256"]:
            raise AssertionError("SQLite archive hash mismatch")
        with tempfile.TemporaryDirectory(prefix="gm_archive_verify_") as temporary:
            with zipfile.ZipFile(archive) as packed:
                if packed.testzip() is not None:
                    raise AssertionError("Archive CRC failed")
                for filename in ("league_state.sqlite", "player_pool.sqlite"):
                    Path(temporary, filename).write_bytes(packed.read(filename))
            copied_league, copied_pool = connect(Path(temporary) / "league_state.sqlite"), connect(Path(temporary) / "player_pool.sqlite")
            try:
                if snapshot_digest(copied_league, snapshot) != audit["database_digest_sha256"]:
                    raise AssertionError("Archived league does not match the audited source")
                if [tuple(row) for row in copied_pool.execute("SELECT * FROM player_pool ORDER BY slot_id")] != [tuple(row) for row in pool.execute("SELECT * FROM player_pool ORDER BY slot_id")]:
                    raise AssertionError("Archived player pool differs from source")
            finally:
                copied_league.close()
                copied_pool.close()
    finally:
        league.close()
        pool.close()
    print(f"[PASS] Web bundle: 30 teams, {observed_players} roster entries, {model_count} models, {rookie_count} historical rookies; archive and calculations verified.")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-id", required=True)
    verify(parser.parse_args().save_id)
