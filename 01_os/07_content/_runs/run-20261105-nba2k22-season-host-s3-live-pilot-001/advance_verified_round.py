"""Read back one explicitly Human-triggered S3 calendar advance."""
import argparse
import json
from contextlib import closing
from datetime import date
from pathlib import Path

from initialize_pilot import ROOT, sha, write
from calendar_sim_orchestrator import CalendarSimOrchestrator, captured_game_headers
from engine import connect
from live_reader import ReadOnlyGameProcess
from live_world import bound_database, read_binding
from refresh import _context
from schedule_reader import collect_schedule
from season_cycle_host import HostState, SeasonCycleHost


def finals(database, season):
    with closing(connect(database, True)) as conn:
        return {row[0]: row[1] for row in conn.execute("""
            SELECT DISTINCT g.native_game_id, g.game_id
            FROM games g JOIN game_state_observations o USING(game_id)
            WHERE g.season_id=? AND o.is_final=1 AND g.native_game_id IS NOT NULL
        """, (season,))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--completed-trigger", required=True, choices=("已完成日历模拟",))
    parser.add_argument("--after-cycle", required=True, choices=tuple(f"cycle-{i:03}" for i in range(1, 5)))
    args = parser.parse_args()
    number = int(args.after_cycle.split("-")[1])
    next_cycle = f"cycle-{number + 1:03}"
    runtime = ROOT.parent / "s3-live-private"
    receipt_path = runtime / f"advance-after-{args.after_cycle}.json"
    baseline = json.loads((runtime / "l2-receipt.json").read_bytes())
    if receipt_path.exists():
        raise RuntimeError("Prior attempt exists. Inspect its receipt before any recovery.")
    state = json.loads((runtime / "host-state.json").read_bytes())
    if state["status"] != HostState.WAITING_CALENDAR_ADVANCE or state["current_cycle_id"] != args.after_cycle or state["active_plan"] is not None:
        raise RuntimeError("Host is not waiting for this specific Human advance.")
    binding_dir = runtime / "world"
    binding, binding_sha = read_binding(binding_dir, baseline["filename"])
    database = bound_database(binding_dir, binding)
    assert binding_sha == baseline["binding_sha256"]
    assert Path(state["database_file"]) == database == Path(baseline["database_file"])
    assert state["worldline_id"] == baseline["worldline_id"]
    pid = baseline["context"]["pid"]
    context = _context(pid)
    assert context["epoch"] == baseline["context"], "Live process, build or season epoch changed"
    season = f"season:native-year:{context['epoch']['game_season_year']}"
    before = finals(database, season)
    native_file = Path(binding["native_save_file"])
    before_save = sha(native_file)
    host = SeasonCycleHost(workspace_root=ROOT, state_file=runtime / "host-state.json",
                           ledger_file=runtime / "host-ledger.jsonl", outbox_db=runtime / "outbox.sqlite")
    assert host.outbox.get_cycle(args.after_cycle)["status"] == "COMPLETED"
    host.role_registry.bind_save_context(binding_dir, binding["save_id"], binding["worldline_id"], database)
    assert not host.role_registry.is_authorized, "Review a newly available role grant before sealing"
    receipt = {"human_trigger": args.completed_trigger, "after_cycle": args.after_cycle,
               "worldline_id": binding["worldline_id"], "epoch": context["epoch"],
               "today": context["game_progress"]["today_native_iso_date"],
               "game_date_before": state["current_game_date"], "final_count_before": len(before),
               "native_sha256_before_readback": before_save, "status": "READBACK_STARTED"}
    write(receipt_path, receipt)
    reader = ReadOnlyGameProcess(pid)
    try:
        assert reader.creation_filetime == context["epoch"]["creation_filetime"]
        schedule = collect_schedule(reader, with_calendar=True, read_final_boxes=False)
        entries = [row for row in schedule["manifest"]["entries"] if row["record_shape_valid"]]
        assert all(row["status"] != 1 for row in entries), "Game still in progress"
        final_ids = {str(row["native_game_id"]) for row in entries if row["status"] == 2}
        new_ids = final_ids - before.keys()
        after_date = schedule["calendar"]["current_native_iso_date"]
        elapsed_days = (date.fromisoformat(after_date) - date.fromisoformat(state["current_game_date"])).days
        receipt.update(game_date_after=after_date, elapsed_days=elapsed_days, native_new_final_ids=sorted(new_ids),
                       native_final_count=len(final_ids))
        assert elapsed_days > 0 and new_ids and before.keys() <= final_ids, "Calendar or finalized-game continuity not verified"
        receipt["advance"] = host.advance_calendar_check(next_cycle, reader=reader)
        assert receipt["advance"]["status"] == "CALENDAR_ADVANCE_VERIFIED", receipt["advance"]
        assert receipt["advance"]["current_date"] == after_date
        write(receipt_path, receipt)
        prior_reports = set(binding_dir.glob("vae_capture_*/refresh-report.json"))
        if number == 4:
            orchestrator = CalendarSimOrchestrator(binding_dir, baseline["filename"], database)
            captured = orchestrator.trigger_world_capture(reader_or_pid=reader, mode="INCREMENTAL")
            assert captured["status"] == "SUCCESS_INGESTED", captured
        else:
            receipt["opened"] = host.start_cycle(next_cycle, reader=reader, candidate_intents=[])
            assert receipt["opened"]["status"] == "DECISION_CYCLE_OPENED", receipt["opened"]
        new_reports = set(binding_dir.glob("vae_capture_*/refresh-report.json")) - prior_reports
        assert len(new_reports) == 1
        report_path = new_reports.pop()
        report = json.loads(report_path.read_bytes())
        assert report["status"] == "COMPLETED_REQUESTED_SOURCES"
        assert report["process_epoch"] == context["epoch"] and report["binding_sha256"] == binding_sha
        assert all(row["commit_status"] == "COMMITTED_SUCCESS_VERIFIED" for row in report["sources"])
        after = finals(database, season)
        assert after.keys() - before.keys() == new_ids and after.keys() == final_ids
        orchestrator = CalendarSimOrchestrator(binding_dir, baseline["filename"], database)
        schedule_unit = next(row["unit"]["unit_id"] for row in report["sources"] if row["family"] == "schedule")
        headers = captured_game_headers(report_path.parent, report)
        readbacks = [orchestrator.verify_game_sql_integrity(after[game], expected_unit_id=schedule_unit,
                                                           native_header=headers[game])
                     for game in sorted(new_ids)]
        receipt.update(refresh_batch_id=report["batch_id"], refresh_report_sha256=sha(report_path),
                       refresh_report_local=str(report_path), final_count_after=len(after),
                       readbacks=readbacks, source_count=len(report["sources"]))
        assert all(item["verified_in_db"] for item in readbacks), "New game readback failed"
        assert _context(pid)["game_progress"] == report["game_progress"], "Game progressed during readback"
        if number < 4:
            receipt["next_seal"] = host.seal_cycle_decisions(next_cycle)
            assert receipt["next_seal"]["status"] == "NO_CHANGE_WAITING_HUMAN_CALENDAR_ADVANCE"
        receipt["status"] = "VERIFIED_HUMAN_ADVANCE"
    except Exception as exc:
        receipt.update(status="FAILED_STOPPED_NO_REPLAY", error=repr(exc))
        raise
    finally:
        reader.close()
        receipt["native_sha256_after_readback"] = sha(native_file)
        receipt["native_unchanged_during_host_readback"] = receipt["native_sha256_after_readback"] == before_save
        write(receipt_path, receipt)
    print(json.dumps({key: value for key, value in receipt.items() if key not in ("readbacks", "native_new_final_ids")},
                     ensure_ascii=False))
    return 0 if receipt["native_unchanged_during_host_readback"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
