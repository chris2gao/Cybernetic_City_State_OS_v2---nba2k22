"""Export an audited SQLite capture into immutable, small files for a web GM.

No game memory, network, LLM, or game writes are used. SQLite remains the source;
JSON is a derived reading surface. Publication is a separate explicit operation.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import zipfile

from data_context import decode_context
from data_sync_metadata import stamp_database
from gm_engine import GMEngine
from historical_rookies import is_historical_rookie
from save_context import save_paths
from gm_state_io.lifecycle import guarded
from snapshot_integrity import file_sha256, write_json_atomic
from draft_assets import VERIFIED, trade_window

ROOT = Path(__file__).resolve().parent.parent
PUBLISHED = ROOT / "published"
ARCHIVES = ROOT / "_exports" / "archives"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def connect(path):
    conn = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def write(path, value):
    write_json_atomic(str(path), value)


def public_row(row, excluded=()):
    return {key: row[key] for key in row.keys() if key not in set(excluded) | {"raw_struct", "memory_addr", "memory_address"}}


def verify_bundle(directory, expected_hash=None):
    """Legacy opt-in utility; never called by timestamp export/publication."""
    directory = Path(directory).resolve()
    manifest_path = directory / "manifest.json"
    if expected_hash and file_sha256(str(manifest_path)) != expected_hash:
        raise RuntimeError("Published manifest hash mismatch")
    manifest = load(manifest_path)
    if not manifest.get("files") or manifest.get("audit_verdict") != "PASS_VERIFIED":
        raise RuntimeError("Invalid or unaudited bundle")
    for relative, meta in manifest["files"].items():
        path = (directory / relative).resolve()
        if not path.is_relative_to(directory) or not path.is_file():
            raise RuntimeError(f"Missing or unsafe bundle path: {relative}")
        if path.stat().st_size != meta["bytes"] or file_sha256(str(path)) != meta["sha256"]:
            raise RuntimeError(f"Bundle file changed: {relative}")
    return manifest


def compare_rows(before, after, keys):
    def indexed(rows):
        result = {}
        for row in rows:
            key = tuple(row[field] for field in keys)
            if key in result:
                raise RuntimeError(f"Ambiguous comparison identity: {key}")
            result[key] = row
        return result
    left, right = indexed(before), indexed(after)
    changed = []
    for key in sorted(left.keys() & right.keys(), key=repr):
        fields = {field: {"before": left[key].get(field), "after": right[key].get(field)}
                  for field in left[key].keys() | right[key].keys()
                  if left[key].get(field) != right[key].get(field)}
        if fields:
            changed.append({"identity": list(key), "fields": fields})
    return {"added": [right[key] for key in sorted(right.keys() - left.keys(), key=repr)],
            "removed": [left[key] for key in sorted(left.keys() - right.keys(), key=repr)], "changed": changed}


@guarded('export')
def export_snapshot(save_id, snapshot_id):
    paths = save_paths(save_id)  # Does not create or reset a career.
    for name in ("db_path", "player_pool_db_path"):
        if not Path(paths[name]).is_file():
            raise FileNotFoundError(paths[name])
    audit = GMEngine(db_path=paths["db_path"], snapshots_dir=paths["snapshots_dir"],
                     player_pool_db_path=paths["player_pool_db_path"]).verify_snapshot_gate(snapshot_id)
    source_manifest_path = Path(paths["snapshots_dir"]) / f"ingest_manifest_{snapshot_id}.json"
    source_manifest = load(source_manifest_path)
    source_manifest_hash = file_sha256(str(source_manifest_path))
    source_pool_hash = file_sha256(paths["player_pool_db_path"])
    league, pool = connect(paths["db_path"]), connect(paths["player_pool_db_path"])
    try:
        from player_potential_mask import verify_sanitized_pair
        potential_mask = verify_sanitized_pair(league,pool,snapshot_id)
        metadata = league.execute("SELECT * FROM monthly_snapshots WHERE snapshot_id=?", (snapshot_id,)).fetchone()
        context = decode_context(metadata["notes"])
        if context.get("career_id", save_id) != save_id:
            raise RuntimeError("Context career does not match the selected database")
        if context.get("game_date") and int(context["game_date"][:4]) not in (metadata["season_year"] - 1, metadata["season_year"]):
            raise RuntimeError("Player-confirmed game date does not match the selected season")
        context_hash = hashlib.sha256(json.dumps(context, sort_keys=True).encode()).hexdigest()[:8]
        data_updated_at = source_manifest.get("data_updated_at", source_manifest["timestamp"])
        batch_id = f"{snapshot_id}_{source_manifest_hash[:12]}_{context_hash}_TS2"
        coaching_files={}
        state_io_binding={}
        state_io_summary=source_manifest.get('quality_metrics',{}).get('deterministic_state_io')
        if state_io_summary:
            from gm_state_io.capture_bridge import load_from_connection
            from gm_state_io.common import binding
            state_source=load_from_connection(league,snapshot_id)
            if not audit['checks'].get('state_io_registered_fields_and_identities_match_same_session'):
                raise RuntimeError('STATE_IO_SOURCE_AUDIT_MISSING')
            state_io_binding=binding(state_source)
        if source_manifest.get('quality_metrics',{}).get('coaching_tactics',{}).get('profile')==1:
            from coaching_source import load_coaching_source,coaching_public_files
            source=load_coaching_source(league,snapshot_id,save_id,data_updated_at)
            if source is None or not audit['checks'].get('coaching_30_teams_identity_defaults_and_verified_overall_match_live'):
                raise RuntimeError('COACHING_SOURCE_CAPTURE_FAILED_OR_AUDIT_MISSING')
            coaching_files=coaching_public_files(source,batch_id,data_updated_at)
        final_dir = PUBLISHED / "saves" / save_id / "batches" / batch_id
        pointer_path = PUBLISHED / "saves" / save_id / "latest.json"
        if final_dir.exists():
            return load(final_dir / "manifest.json")

        teams = [public_row(row, {"id", "snapshot_id"}) for row in league.execute(
            "SELECT * FROM team_monthly_stats WHERE snapshot_id=? ORDER BY team_id", (snapshot_id,))]
        identities = {row["team_id"]: public_row(row) for row in league.execute("SELECT team_id, abbreviation,city,name FROM teams")}
        players = [public_row(row, {"id", "snapshot_id", "player_id"}) for row in league.execute(
            "SELECT * FROM player_monthly_stats WHERE snapshot_id=? ORDER BY team_id, player_name, face_id", (snapshot_id,))]
        extended = source_manifest.get('quality_metrics', {}).get('source_extension_profile') == 1
        if extended:
            details = {(row['team_id'], row['player_name'], row['face_id']): row for row in league.execute(
                'SELECT * FROM player_source_details WHERE snapshot_id=?', (snapshot_id,))}
            for player in players:
                row = details[(player['team_id'], player['player_name'], player['face_id'])]
                detail = json.loads(row['details_json'])
                player.update(birth_date=detail['birth_date'], age=detail['age'], age_as_of=detail['age_as_of'],
                              pool_slot=row['pool_slot'], source_details=detail,
                              attributes={key: value['value'] for key, value in detail['attributes'].items()},
                              potential=detail['attributes']['potential']['value'],
                              contract_salary_schedule=[detail['contract'][f'contract_year_{i}']['value'] for i in range(1, 7)],
                              full_cba_ledger_verified=False)
                from player_potential_mask import MARKERS
                player.update(MARKERS)
        staff = [{"staff_slot": row["staff_slot"], "first_name": row["first_name"], "last_name": row["last_name"],
                  "observed_candidate_team_id": row["raw_team_id"], "team_id": None,
                  "team_mapping_status": row["team_mapping_status"]} for row in league.execute(
            "SELECT * FROM staff_pool_observations WHERE snapshot_id=? ORDER BY staff_slot", (snapshot_id,))]
        if extended:
            staff = [json.loads(row['details_json']) for row in league.execute(
                'SELECT details_json FROM staff_source_details WHERE snapshot_id=? ORDER BY staff_slot', (snapshot_id,))]
            staff = [row for row in staff if row['first_name'] or row['last_name']]
        draft_assets = [public_row(row, {'snapshot_id'}) for row in league.execute(
            'SELECT * FROM draft_asset_observations WHERE snapshot_id=? ORDER BY asset_slot', (snapshot_id,))] if extended else []
        simple_draft_summary = source_manifest.get('quality_metrics', {}).get('simple_draft_assets')
        if simple_draft_summary:
            window = trade_window(simple_draft_summary['next_draft_year'])
            draft_assets = [{k: v for k, v in row.items() if k != 'protection'} for row in draft_assets if row['mapping_status'] == VERIFIED]
            for asset in draft_assets:
                asset['asset_id'] = f"draft_pick:{asset['draft_year']}:{asset['draft_round']}:{asset['original_owner_team_id']}"
                asset['within_three_year_trade_window'] = asset['draft_year'] in window
        models = []
        for row in pool.execute("SELECT * FROM player_pool ORDER BY slot_id"):
            model = public_row(row)
            from player_potential_mask import MARKERS
            model.update(MARKERS)
            if model.get('source_details_json'):
                model['source_details'] = json.loads(model.pop('source_details_json'))
            model["model_category"] = "HISTORICAL_ROOKIE" if is_historical_rookie(row["raw_struct"]) else "OTHER_UNCLASSIFIED"
            models.append(model)
        counts = {"teams": len(teams), "active_players": len(players), "staff_observations": len(staff),
                  "player_models": len(models), "historical_rookie_models": sum(row["model_category"] == "HISTORICAL_ROOKIE" for row in models)}
        rules = dict(league.execute("SELECT * FROM seasons WHERE season_year=?", (metadata["season_year"],)).fetchone())
        source_catalog = load(ROOT / "config" / "source_catalog.json")
        source_catalog['sources']=[s for s in source_catalog.get('sources',[]) if s['id']!='coaching_tactics']
        source_catalog['sources']=[s for s in source_catalog['sources'] if s['id']!='state_io_native']
        source_catalog['sources'].append(dict(id='state_io_native',
            status='OBSERVED_SAME_BATCH_SOURCE_AUDITED' if state_io_summary else 'NOT_OBSERVED_IN_THIS_BATCH',
            data_updated_at=data_updated_at if state_io_summary else None,
            domains=state_io_summary['coverage'] if state_io_summary else {},
            query_entrypoint='scripts/gm_data_query.py',generation=state_io_binding.get('generation_id')))
        source_catalog['sources'].append(dict(id='coaching_tactics',
            status='VERIFIED_OBSERVED_SAME_BATCH' if coaching_files else 'NOT_OBSERVED_IN_THIS_BATCH',
            data_updated_at=data_updated_at if coaching_files else None,
            entrypoint='coaching/teams.json' if coaching_files else None,
            dictionary='coaching/field_dictionary.json' if coaching_files else None,
            sim_control='GM_CONTROL_DISABLED'))
        previous = load(pointer_path) if pointer_path.exists() else None
        change_report = {"status": "INITIAL_BASELINE", "previous_batch_id": None, "monthly_game_statistics_available": False}
        if previous:
            previous_dir = PUBLISHED / previous["batch_path"]
            previous_manifest = load(previous_dir / "manifest.json")
            if previous_manifest["context"].get("purpose") != context.get("purpose"):
                raise RuntimeError("Production and validation streams must use different save IDs")
            old_league = load(previous_dir / "league.json")
            old_players = [player for team in old_league["teams"] for player in load(previous_dir / "teams" / f"{team['team_abbr']}.json")["roster"]]
            change_report.update({"status": "COMPARED_TO_PREVIOUS_PUBLISHED_CAPTURE", "previous_batch_id": previous["batch_id"],
                                  "teams": compare_rows(old_league["teams"], teams, ("team_id",)),
                                  "rosters": compare_rows(old_players, players, ("team_id", "player_name", "face_id"))})
        ARCHIVES.mkdir(parents=True, exist_ok=True)
        staging_root = ROOT / "_exports" / "staging"
        staging_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="web_gm_", dir=staging_root) as temp:
            temporary = Path(temp)
            bundle = temporary / "bundle"
            bundle.mkdir()
            write(bundle / "league.json", {"teams": teams, "rules": rules, "counts": counts})
            for team in teams:
                write(bundle / "teams" / f"{team['team_abbr']}.json", {"identity": identities[team["team_id"]], "state": team,
                      "roster": [row for row in players if row["team_id"] == team["team_id"]]})
            write(bundle / "staff.json", {"ownership_verified": extended, "complete_global_employee_pool_verified": extended,
                  "scope": "All named entries in the live roster staff descriptor; 8 reciprocal roles per NBA team" if extended else "Legacy partial pool",
                  "records": staff})
            if extended:
                write(bundle / 'draft_assets.json', {'ownership_verified': bool(simple_draft_summary), 'metadata_verified': bool(simple_draft_summary),
                      'next_draft_year': simple_draft_summary['next_draft_year'] if simple_draft_summary else None,
                      'tradeable_draft_years': trade_window(simple_draft_summary['next_draft_year']) if simple_draft_summary else None,
                      'protection_and_swaps': 'NOT_USED_BY_PLAYER_RULES',
                      'note': 'Simple picks: current owner, original owner, year and round. Only next three drafts are tradeable. No game writes.' if simple_draft_summary else 'Legacy candidate records; ownership/year/round unverified.',
                      'records': draft_assets})
                write(bundle / 'season_totals.json', {'method': 'LIVE_MEMORY_TOTALS_NOT_MONTHLY_OR_GAME_LOGS',
                      'teams': [{'team_id': row['team_id'], 'totals': json.loads(row['totals_json'])} for row in league.execute(
                          'SELECT * FROM team_source_stats WHERE snapshot_id=? ORDER BY team_id', (snapshot_id,))]})
            write(bundle / "source_coverage.json", source_catalog)
            for relative,payload in coaching_files.items():
                write(bundle / relative,payload)
            write(bundle / "data_update.json", {"save_id": save_id, "snapshot_id": snapshot_id,
                  "data_updated_at": data_updated_at, "game_date": context.get("game_date")})
            write(bundle / "changes.json", change_report)
            calculations = {"method": "deterministic_python_v1", "currency": "USD", "financial_room_is_proxy_not_certified_CBA_room": True,
                            "teams": [{"team_id": team["team_id"], "abbr": team["team_abbr"],
                                       "salary_cap_minus_observed_payroll_proxy": rules["salary_cap"] - team["total_salary"],
                                       "observed_payroll_minus_luxury_tax_line": team["total_salary"] - rules["luxury_tax_threshold"],
                                       "observed_roster_salary_sum": sum(player["salary_current_year"] for player in players if player["team_id"] == team["team_id"])} for team in teams]}
            write(bundle / "calculations.json", calculations)
            by_year = defaultdict(list)
            for row in models:
                by_year[str(row["draft_year"]) if row["draft_year"] is not None else "unknown"].append(row)
            catalog, names = {}, defaultdict(list)
            for year, records in sorted(by_year.items()):
                catalog[year] = []
                for start in range(0, len(records), 200):
                    relative = f"player_catalog/{year}_{start // 200 + 1}.json"
                    write(bundle / relative, {"records": records[start:start + 200]})
                    catalog[year].append(relative)
                    for row in records[start:start + 200]:
                        names[row["full_name"].casefold()].append({"slot_id": row["slot_id"], "model_category": row["model_category"], "file": relative})
            write(bundle / "player_catalog/index.json", {"years": catalog, "model_count": len(models), "identity_scope": "Model slots are not persistent person IDs across roster replacements"})
            write(bundle / "player_catalog/name_index.json", dict(sorted(names.items())))
            write(bundle / "audit.json", {key: audit[key] for key in ("snapshot_id", "audit_timestamp", "verifier", "verdict", "checks", "counts", "database_digest_sha256", "player_pool_sha256")})
            (bundle / "SUMMARY.md").write_text(
                f"# {save_id}: {context.get('game_date') or 'GAME DATE UNCONFIRMED'}\n\n"
                f"Data updated at (UTC): {data_updated_at}\n\n"
                f"Purpose: {context['purpose']}; event: {context.get('event')}; game date source: {context.get('game_date_provenance')}.\n\n"
                f"Audited {len(audit['checks'])}/{len(audit['checks'])}; {len(teams)} teams; {len(players)} active players; {len(models)} player models.\n\n"
                "Read manifest.json, source_coverage.json, calculations.json, then only the teams needed. Null means unavailable, never zero.\n\n" +
                ("Team W/L and season totals, player season totals where a current stats index exists, 55 attributes, DOB, six salary years and reciprocal staff ownership are observed. OVR, exact current age without a confirmed date, schedule/game logs, monthly box scores, injuries, full CBA ledger and decoded draft-right metadata remain unavailable. Financial differences are proxies.\n" if extended else
                 "Game results, monthly box scores, injuries, full CBA ledger and staff ownership are unavailable. Financial differences are proxies.\n") +
                "Historical/real-world scenarios are separate from observed game facts. All decisions remain proposals requiring player approval.\n",
                encoding="utf-8")
            backups = temporary / "databases"
            backups.mkdir()
            for name, conn in (("league_state.sqlite", league), ("player_pool.sqlite", pool)):
                destination = sqlite3.connect(backups / name)
                try:
                    conn.backup(destination)
                    stamp_database(destination, snapshot_id, save_id, data_updated_at)
                    destination.commit()
                finally:
                    destination.close()
            archive = ARCHIVES / f"{batch_id}.zip"
            archive_tmp = archive.with_suffix(".zip.tmp")
            with zipfile.ZipFile(archive_tmp, "w", compression=zipfile.ZIP_DEFLATED) as target:
                for database in backups.iterdir():
                    target.write(database, database.name)
                target.write(source_manifest_path, "ingest_manifest.json")
                target.writestr("context.json", json.dumps(context, ensure_ascii=False))
                target.writestr("audit.json", json.dumps(audit, ensure_ascii=False))
                target.writestr("data_update.json", json.dumps({"save_id": save_id, "snapshot_id": snapshot_id,
                                "data_updated_at": data_updated_at, "game_date": context.get("game_date")}))
            os.replace(archive_tmp, archive)
            files = {path.relative_to(bundle).as_posix(): {"bytes": path.stat().st_size}
                     for path in sorted(bundle.rglob("*")) if path.is_file()}
            manifest = {"schema_version": 2, "sync_mode": "TIMESTAMP_ONLY", "data_updated_at": data_updated_at,
                        "player_potential_mask":potential_mask,
                        "batch_id": batch_id, "save_id": save_id, "snapshot_id": snapshot_id,
                        "captured_at_utc": source_manifest["timestamp"], "exported_at_utc": datetime.now(timezone.utc).isoformat(),
                        "context": context, "gm_decisions_allowed": context["purpose"] == "production",
                        "audit_verdict": "PASS_VERIFIED", "audit_check_count": len(audit["checks"]), "counts": counts,
                        "source_binding": {"snapshot_digest_sha256": audit["database_digest_sha256"], "ingest_manifest_sha256": source_manifest_hash,
                                           "player_pool_sha256": source_pool_hash, "exporter_source_sha256": file_sha256(__file__)},
                        "archive": {"filename": archive.name, "bytes": archive.stat().st_size, "release_tag": f"data-{batch_id}"},
                        "files": files, "null_policy": "UNOBSERVED_IS_NULL_NOT_ZERO", "game_write_policy": "PLAYER_APPROVAL_REQUIRED",
                        "reader_contract": "Read latest.json, compare data_updated_at/uploaded_at, and use its batch_path. No JSON verification required."}
            if state_io_summary:
                manifest['state_io']=dict(**state_io_binding,registry_version=state_source['registry_version'],
                                          coverage=state_io_summary['coverage'],query_interface='scripts/gm_data_query.py')
            write(bundle / "manifest.json", manifest)
            # M0 query copies reuse this exact audited two-database backup.
            # No new capture, publication, or game execution is triggered here.
            from gm_data_access.snapshots import install_archive
            install_archive(archive, manifest, ROOT / 'database' / 'query_snapshots')
            final_dir.parent.mkdir(parents=True, exist_ok=True)
            os.replace(bundle, final_dir)
        pointer = {"save_id": save_id, "batch_id": batch_id, "batch_path": final_dir.relative_to(PUBLISHED).as_posix(),
                   "data_updated_at": data_updated_at, "uploaded_at": None, "upload_status": "PENDING_UPLOAD",
                   "sync_mode": "TIMESTAMP_ONLY", "game_date": context.get("game_date"), "purpose": context["purpose"]}
        if state_io_binding:
            pointer.update(state_io_binding)
        write(pointer_path, pointer)
        index_path = PUBLISHED / "index.json"
        index = load(index_path) if index_path.exists() else {"schema_version": 1, "careers": {}}
        index["careers"][save_id] = {"latest": pointer_path.relative_to(PUBLISHED).as_posix(),
                                   "data_updated_at": data_updated_at, "uploaded_at": None,
                                   "game_date": context.get("game_date"), "purpose": context["purpose"]}
        write(index_path, index)
        if state_io_summary and state_io_binding.get('generation_id'):
            from gm_state_io.capture_bridge import mark_captured
            mark_captured(save_id,snapshot_id)
        print(f"[PASS] Exported {batch_id}: {counts}; archive={archive.name}")
        return manifest
    finally:
        league.close()
        pool.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-id", required=True)
    parser.add_argument("--snapshot", required=True)
    args = parser.parse_args()
    export_snapshot(args.save_id, args.snapshot)
