"""Verify the first live baseline and seal an empty first round through Host."""
import argparse
import hashlib
import json
import sys
from contextlib import closing
from pathlib import Path

from initialize_pilot import ROOT, sha, write
from engine import connect
from live_reader import ReadOnlyGameProcess
from live_world import bound_database, read_binding
from refresh import SOURCES, _context
from season_cycle_host import HostState, SeasonCycleHost


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    if runtime != (ROOT.parent / "s3-live-private").resolve():
        raise ValueError("Expected the isolated S3 runtime")
    l1 = json.loads((runtime / "l1-receipt.json").read_bytes())
    assert l1["status"] == "BASELINE_RETURNED" and l1["native_disk_unchanged"]
    host = SeasonCycleHost(workspace_root=ROOT, state_file=runtime / "host-state.json",
                           ledger_file=runtime / "host-ledger.jsonl", outbox_db=runtime / "outbox.sqlite")
    assert host.state["status"] == HostState.BASELINE_CAPTURED
    assert host.state["is_offline_mock"] is False
    save_dir = runtime / "world"
    assert Path(host.state["save_directory"]).resolve() == save_dir
    binding, binding_digest = read_binding(save_dir, l1["filename"])
    database = bound_database(save_dir, binding)
    assert database == Path(l1["host"]["database_file"]) == Path(host.state["database_file"])
    assert binding["worldline_id"] == host.state["worldline_id"] == l1["host"]["worldline_id"]
    reports = list(save_dir.glob("vae_capture_*/refresh-report.json"))
    assert len(reports) == 1
    report_path = reports[0]
    report = json.loads(report_path.read_bytes())
    assert report["status"] == "COMPLETED_REQUESTED_SOURCES"
    assert report["binding_sha256"] == binding_digest
    assert report["requested_families"] == list(SOURCES)
    assert [source["family"] for source in report["sources"]] == list(SOURCES)
    assert all(source["status"] == "ACQUIRED" and source["commit_status"] == "COMMITTED_SUCCESS_VERIFIED"
               for source in report["sources"])
    context = _context(l1["pid"])
    assert context["epoch"] == l1["process_epoch"] == report["process_epoch"]
    assert context["game_progress"] == report["game_progress"]
    native = Path(binding["native_save_file"])
    native_before = sha(native)
    assert native_before == l1["native_sha256_after"]
    with closing(connect(database, True)) as conn:
        unit_ids = {row[0] for row in conn.execute("SELECT unit_id FROM capture_units")}
        assert all(source["unit"]["unit_id"] in unit_ids for source in report["sources"])
        final_count = conn.execute("SELECT count(DISTINCT game_id) FROM game_state_observations WHERE is_final=1").fetchone()[0]
    host.role_registry.bind_save_context(save_dir, binding["save_id"], binding["worldline_id"], database)
    assert not host.role_registry.is_authorized, "Review a new role grant before opening the cycle"
    proposals = [
        {"role": "GM", "disposition": "NO_CHANGE", "basis": "Organization, finance and market captured. No verified GM delegation for the isolated worldline."},
        {"role": "COACH", "disposition": "NO_CHANGE", "basis": "Lineups, coach statistics and planning captured. Preserve them as baseline without a verified Coach grant."},
        {"role": "PLAYER", "disposition": "NO_CHANGE", "basis": "Current player skills and period statistics captured. No authenticated player decision or justified tendency target."},
    ]
    reader = ReadOnlyGameProcess(l1["pid"])
    try:
        assert reader.creation_filetime == l1["process_epoch"]["creation_filetime"]
        opened = host.start_cycle("cycle-001", candidate_intents=[], reader=reader)
    finally:
        reader.close()
    assert opened["status"] == "DECISION_CYCLE_OPENED", opened
    assert opened["progress_status"] == "INITIAL_BASELINE_REUSED"
    sealed = host.seal_cycle_decisions("cycle-001")
    assert sealed["status"] == "NO_CHANGE_WAITING_HUMAN_CALENDAR_ADVANCE"
    cycle = host.outbox.get_cycle("cycle-001")
    result = {
        "phase": "L2", "status": sealed["status"], "baseline_batch_id": report["batch_id"],
        "baseline_report_sha256": sha(report_path), "game_date": opened["game_date"],
        "context": context["epoch"], "filename": binding["native_save_filename"],
        "save_id": binding["save_id"], "worldline_id": binding["worldline_id"],
        "database_file": str(database), "binding_sha256": binding_digest,
        "verified_source_count": len(report["sources"]), "final_games_in_sqlite": final_count,
        "role_authorization_status": host.role_registry.authorization_status,
        "proposals": proposals, "native_targets": [], "opened": opened, "sealed": sealed,
        "outbox_status": cycle["status"], "sealed_digest_verified": cycle["sealed_digest"] == sealed["plan_digest"],
        "native_sha256_before": native_before, "native_sha256_after": sha(native),
    }
    result["native_disk_unchanged"] = result["native_sha256_before"] == result["native_sha256_after"]
    write(runtime / "l2-receipt.json", result)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["sealed_digest_verified"] and result["native_disk_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
