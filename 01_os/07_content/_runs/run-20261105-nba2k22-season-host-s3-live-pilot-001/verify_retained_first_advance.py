"""Verify the committed first advance after correcting overtime readback."""
import argparse
import json
from pathlib import Path

from advance_verified_round import finals
from calendar_sim_orchestrator import CalendarSimOrchestrator, captured_game_headers
from initialize_pilot import ROOT, sha, write
from live_world import read_binding
from refresh import _context
from season_cycle_host import HostState, SeasonCycleHost


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    runtime = ROOT.parent / "s3-live-private"
    original_path = runtime / "advance-after-cycle-001.json"
    out = runtime / "advance-after-cycle-001-reverified.json"
    original = json.loads(original_path.read_bytes())
    assert original["status"] == "FAILED_STOPPED_NO_REPLAY"
    assert original["error"] == "AssertionError('New game readback failed')"
    assert original["native_unchanged_during_host_readback"]
    assert not out.exists()
    state = json.loads((runtime / "host-state.json").read_bytes())
    assert state["status"] == HostState.DECISION_OPEN and state["current_cycle_id"] == "cycle-002"
    assert state["worldline_id"] == original["worldline_id"] and state["active_plan"] is None
    save_dir = runtime / "world"
    report_path = Path(original["refresh_report_local"]).resolve()
    assert report_path.is_relative_to(save_dir.resolve())
    assert sha(report_path) == original["refresh_report_sha256"]
    report = json.loads(report_path.read_bytes())
    assert report["status"] == "COMPLETED_REQUESTED_SOURCES" and report["batch_id"] == original["refresh_batch_id"]
    assert report["process_epoch"] == original["epoch"]
    assert all(row["commit_status"] == "COMMITTED_SUCCESS_VERIFIED" for row in report["sources"])
    binding, binding_digest = read_binding(save_dir, state["loaded_filename"])
    assert binding_digest == report["binding_sha256"]
    assert binding["worldline_id"] == original["worldline_id"]
    database = Path(state["database_file"])
    orchestrator = CalendarSimOrchestrator(save_dir, state["loaded_filename"], database)
    schedule_unit = next(row["unit"] for row in report["sources"] if row["family"] == "schedule")
    games = finals(database, schedule_unit["season_id"])
    assert len(games) == original["native_final_count"]
    headers = captured_game_headers(report_path.parent, report)
    new_ids = original["native_new_final_ids"]
    readbacks = [orchestrator.verify_game_sql_integrity(games[game], expected_unit_id=schedule_unit["unit_id"],
                                                       native_header=headers[game]) for game in new_ids]
    assert all(item["verified_in_db"] for item in readbacks), [item for item in readbacks if not item["verified_in_db"]]
    overtime = [item for item in readbacks if item["overtime_count"]]
    assert overtime
    for row in overtime:
        game = row["game_id"]
        raw = headers[game.rsplit(":", 1)[1]]
        assert not orchestrator.verify_game_sql_integrity(game, expected_unit_id=row["unit_id"])["verified_in_db"]
        changed = bytes([raw[0] ^ 1]) + raw[1:]
        wrong = orchestrator.verify_game_sql_integrity(game, expected_unit_id=row["unit_id"], native_header=changed)
        assert wrong["reason"] == "Native overtime header hash mismatch"
    print(json.dumps({"verified_games": len(readbacks), "overtime": overtime,
                      "missing_and_tampered_headers_rejected": True}, ensure_ascii=False))
    if args.check_only:
        return 0
    context = _context(original["epoch"]["pid"])
    assert context["epoch"] == original["epoch"] and context["game_progress"] == report["game_progress"]
    native = Path(binding["native_save_file"])
    native_before = sha(native)
    assert native_before == original["native_sha256_after_readback"]
    host = SeasonCycleHost(workspace_root=ROOT, state_file=runtime / "host-state.json",
                           ledger_file=runtime / "host-ledger.jsonl", outbox_db=runtime / "outbox.sqlite")
    host.role_registry.bind_save_context(save_dir, binding["save_id"], binding["worldline_id"], database)
    assert not host.role_registry.is_authorized
    seal = host.seal_cycle_decisions("cycle-002")
    assert seal["status"] == "NO_CHANGE_WAITING_HUMAN_CALENDAR_ADVANCE"
    assert host.outbox.get_cycle("cycle-002")["sealed_digest"] == seal["plan_digest"]
    unchanged = sha(native) == native_before
    updated = {key: value for key, value in original.items() if key != "error"}
    updated.update(status="VERIFIED_HUMAN_ADVANCE", readbacks=readbacks, next_seal=seal,
                   original_failed_receipt_sha256=sha(original_path), verification_only_recovery=True,
                   recapture_performed=False, native_unchanged_during_host_readback=unchanged)
    write(out, updated)
    return 0 if unchanged else 1


if __name__ == "__main__":
    raise SystemExit(main())
