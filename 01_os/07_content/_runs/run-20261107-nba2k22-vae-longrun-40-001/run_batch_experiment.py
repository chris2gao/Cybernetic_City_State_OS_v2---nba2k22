"""V2 live research runner. Requires an active Human goal pin and an isolated test session."""
import argparse
from collections import Counter
from contextlib import closing
from datetime import date, timedelta
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

from build_observed_round import build
from experiment_round import analyze, plan as make_plan
from live_research_authority import FIELD, MAX_CALENDAR, MAX_CYCLES, MAX_SETTERS, SLOT
from live_research_authority import ResearchAuthority, freeze, require
from read_observed_window import readback

REPO = Path(__file__).resolve().parents[4]
DOMAIN = REPO / "08_Domain_Applications/Antigravity_GM_Engine"
WORLD = DOMAIN / "world_data_prototype"
NATIVE = DOMAIN / "research/rea_native_control"
FAMILIES = ("schedule", "game-mode", "lineups", "settings", "player-state", "player-skills")


def run_checked(script, *args):
    result = subprocess.run([sys.executable, "-B", "-X", "utf8", str(script), *map(str, args)],
                            cwd=REPO, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{Path(script).name} returned {result.returncode}: "
                           + result.stderr.decode("utf-8", "replace")[-1300:])


def schedule_for(database, snapshot):
    from engine import connect

    ident = snapshot["identity"]
    with closing(connect(database, True)) as conn:
        rows = conn.execute("""
            SELECT g.native_game_id AS id, x.scheduled_native_iso_date AS day,
                   h.native_team_id AS home, a.native_team_id AS away, x.game_type_label AS type,
                   s.status_code, s.is_final, x.played_native_iso_date AS played
            FROM games g JOIN game_source_checks x USING(game_id)
            JOIN game_state_observations s ON s.game_id=x.game_id AND s.unit_id=x.unit_id
            JOIN teams h ON h.team_id=g.home_team_id JOIN teams a ON a.team_id=g.away_team_id
            WHERE g.season_id=? AND x.unit_id=? AND x.scheduled_native_iso_date>=?
            ORDER BY CAST(g.native_game_id AS INT)
        """, (ident["season"], snapshot["provenance"]["unit_refs"]["schedule"]["unit_id"], snapshot["start"])).fetchall()
    return [dict(row) for row in rows]


def subplans(template, round_plan, schedule, authority, season_stop, calendar, *, resume_from=None):
    cursor, stop = map(date.fromisoformat, (round_plan["start"], round_plan["stop"]))
    if resume_from is not None:
        cursor = resume_from
    by_day = Counter(row["day"] for row in schedule if row["type"] == "NORMAL")
    windows = []
    while cursor < stop:
        days = 1 if resume_from is not None and not windows else 2
        end = min(cursor + timedelta(days=days), stop)
        start_day, end_day = cursor.isoformat(), end.isoformat()
        if not by_day[end_day] and end - cursor == timedelta(days=2):
            end -= timedelta(days=1)
            end_day = end.isoformat()
        rows = [row for row in schedule if start_day <= row["day"] <= end_day]
        require(rows and all(row["type"] == "NORMAL" and row["status_code"] == "0"
                             and row["is_final"] == 0 and row["played"] is None for row in rows),
                "Calendar control includes an unexpected non-pending or special game")
        part = dict(template, start=start_day, stop_exclusive=end_day, today_raw=calendar.word(cursor),
                    season_stop_exclusive=season_stop.isoformat(), authorization_scope=authority.ref,
                    games=[{k: int(row[k]) if k != "day" else row[k] for k in ("id", "day", "home", "away")}
                           for row in rows])
        calendar.validate_plan(part)
        windows.append(part)
        cursor = end
    require(len(windows) <= 4 and authority.calendar_count + len(windows) <= MAX_CALENDAR,
            "Cannot safely partition round within remaining calendar call budget")
    return windows


def apply_setters(host, authority, round_plan, directory):
    pid = authority.epoch["pid"]
    outcomes = []
    for index, target in enumerate(round_plan["write_candidates"], 1):
        authority.bind_target(target)
        cycle = f"vae-v2-r{authority.round_count:02d}-s{index:02d}"
        team, uid = target["team_id"], target["uid"]
        params = {"team_id": team, "player_id": uid, "expected_before": target["expected_before"],
                  "values": {FIELD: target["target"]}}
        getter = host._get_fresh_live_getter(expected_pid=pid, expected_team=team, expected_players={uid},
                                            expected_creation_filetime=authority.epoch["creation_filetime"])
        require(getter is not None, "Native Getter snapshot could not be read")
        if getter(uid, FIELD) != target["expected_before"]:
            outcomes.append(dict(uid=uid, status="LOCAL_CAS_OR_ROSTER_EXCLUDED"))
            continue
        opened = host.start_cycle(cycle, candidate_intents=[{
            "issuer_role": "GM", "actor_uid": f"vae-research-{team}", "parameters": params,
            "reason": f"Human V2 research plan {round_plan['research_plan_digest']}",
        }])
        require(opened["intents_added_count"] == 1, "S4 did not admit exactly one approved role intent")
        seal = host.seal_cycle_decisions(cycle, getter_func=getter, expected_pid=pid)
        require(seal["status"] == "PLAN_PREFLIGHTED_WAITING_AUTH", "S4 could not seal expected intent")
        freeze(directory / f"{cycle}-seal.json", seal)
        try:
            result = host.authorize_and_execute(cycle, seal["plan_digest"], expected_pid=pid,
                                                journal_dir=directory / cycle)
        except RuntimeError as error:
            if not str(error).startswith("LIVE_CAS_CHANGED_SINCE_APPROVAL"):
                raise
            result = {"status": "LOCAL_CAS_OR_ROSTER_EXCLUDED", "executed_count": 0, "success_count": 0}
            # The S4 CAS failed before the reservation or Outbox execution claim.
            from season_cycle_host import HostState
            host.state.update(status=HostState.WAITING_CALENDAR_ADVANCE, active_plan=None)
            host._save_state()
        freeze(directory / f"{cycle}-result.json", result)
        outcomes.append(dict(uid=uid, **result))
        require(result["status"] in ("EXECUTED_AND_READBACK_RECORDED", "LOCAL_CAS_OR_ROSTER_EXCLUDED"),
                f"S4 stopped on {result['status']}")
    return outcomes


def capture_world(output, template, authority):
    from refresh import _context

    before = _context(authority.epoch["pid"])
    authority.check_scene(before, SLOT, template["binding_sha256"])
    run_checked(WORLD / "cli.py", "refresh-world", authority.epoch["pid"], template["save_directory"],
                SLOT, output, "--families", *FAMILIES)
    after = _context(authority.epoch["pid"])
    require(before == after, "WorldData process or date changed during capture")
    from calendar_cli import sha_file
    return dict(status="CAPTURE_COMPLETE", before=before, after=after,
                binding_sha256=template["binding_sha256"], source_report_sha256=sha_file(output / "refresh-report.json"))


def export_pool(r0, template, capture, report_sha, output):
    run_checked(r0, "--database", template["database"],
                "--binding", Path(template["save_directory"]) / "save.json", "--report", capture / "refresh-report.json",
                "--report-sha256", report_sha, "--output", output)


def foreground_probe(calendar, plan, expires):
    script = calendar.render(plan, dispatch=False, expires=expires)
    plan_id = json.dumps(calendar.digest(plan))
    return f"""
const user32 = Process.getModuleByName("user32.dll");
const foreground = new NativeFunction(user32.getExportByName("GetForegroundWindow"), "pointer", []);
const owner = new NativeFunction(user32.getExportByName("GetWindowThreadProcessId"), "uint32", ["pointer","pointer"]);
const pid = Memory.alloc(4), deadline = Date.now() + 47000;
const gate = setInterval(() => {{
    const hwnd = foreground();
    if (!hwnd.isNull() && owner(hwnd, pid) && pid.readU32() === Process.id) {{
        clearInterval(gate);
        observe();
    }} else if (Date.now() >= deadline) {{
        clearInterval(gate);
        send({{kind:"native-control-result", status:"FOREGROUND_WAIT_EXPIRED", pid:Process.id, plan_digest:{plan_id}}});
    }}
}}, 100);
function observe() {{
{script}
}}
"""


def read_frame(cal, authority, window, runtime):
    front = SimpleNamespace(runtime=runtime, node=None, rea=None)
    probe = dict(window, engine_thread=0, engine_thread_evidence=None, observation_ms=60000)
    observation = cal.invoke(front, foreground_probe(cal, probe, authority.expires_at),
                             "TEST_ONLY_OBSERVE_FRAME", authority.ref, 0, probe["observation_ms"],
                             authority.epoch["pid"], cal.digest(probe))
    require(observation.get("status") == "FRAME_GATE_OBSERVED",
            f"REA frame observation stopped: {observation.get('status', observation.get('code', 'NO_STATUS'))}")
    frame_receipt = cal.load(Path(observation["runtime_directory"]) / "evidence.json")
    native = frame_receipt["normalized_result"]
    require(native["pid"] == authority.epoch["pid"] and not native["messages_truncated"]
            and native["cleanup_error"] is None and observation["plan_digest"] == cal.digest(probe),
            "Foreground frame receipt differs from plan")
    frame, = [row["payload"] for row in native["messages"] if row["type"] == "send"
              and row["payload"].get("event") == "FRAME_GATE_OBSERVED"]
    return frame["thread"], frame_receipt["evidence_id"]


def run_calendar(cal, authority, template, window, runtime):
    authority.bind_calendar(window)
    sim = SimpleNamespace(runtime=runtime, node=None, rea=None, outbox=template["outbox_db"],
                          execute_once=True, approval=None, approved_sha=None)
    result = cal.simulate_to_native_date(sim, window, research_delegation=authority)
    freeze(runtime.with_suffix(".json"), result)
    authority.advance(result)
    return result


def reconcile_interruption(args, cal, authority, round_plan, database, outbox):
    old = args.resume
    plan = cal.load(args.recovery_original)
    frame_result = cal.load(args.recovery_frame)
    old_result = cal.load(old / "round-01-sim-03.json")
    raw = cal.load(Path(old_result["private_receipt"]) / "evidence.json")
    native = raw["normalized_result"]
    messages = [row["payload"] for row in native["messages"] if row["type"] == "send"]
    previous = [row["event"] for row in messages if "event" in row]
    require(old_result["status"] == "UNKNOWN_NO_REPLAY" and old_result["plan_digest"] == cal.digest(plan)
            and not native["messages_truncated"] and native["cleanup_error"] is None
            and native["pid"] == authority.epoch["pid"]
            and previous == ["WILL_DISPATCH_ONCE", "DISPATCH_RETURN", "STOP"]
            and messages[1]["frame_idle"] is False, "Interrupted dispatch receipt cannot be reconciled")
    recovered_today = cal.load(args.recovery_raw)
    require(recovered_today.get("event") == "RECOVERY_READ_ONLY" and recovered_today["pid"] == authority.epoch["pid"]
            and recovered_today["today"] == plan["start"] and recovered_today["minutes"] == 0,
            "Recovered packed Today differs from the interrupted start")
    probe = dict(plan, today_raw=recovered_today["raw"], engine_thread=0, engine_thread_evidence=None,
                 observation_ms=60000)
    frame_receipt = cal.load(Path(frame_result["runtime_directory"]) / "evidence.json")
    observed = frame_receipt["normalized_result"]
    require(frame_result["status"] == "FRAME_GATE_OBSERVED" and frame_result["plan_digest"] == cal.digest(probe)
            and observed["pid"] == authority.epoch["pid"] and not observed["messages_truncated"]
            and observed["cleanup_error"] is None, "No bound idle/pending recovery frame")
    frame, = [row["payload"] for row in observed["messages"] if row["type"] == "send"
              and row["payload"].get("event") == "FRAME_GATE_OBSERVED"]
    cal.preflight(plan)
    capture = cal.load(args.recovery_receipt)
    report_path = args.recovery_capture / "refresh-report.json"
    report = cal.load(report_path)
    authority.next_start = date.fromisoformat(plan["start"])
    authority.check_scene(capture["before"], SLOT, capture["binding_sha256"])
    require(capture["status"] == "CAPTURE_COMPLETE" and capture["before"] == capture["after"]
            and capture["source_report_sha256"] == cal.sha_file(report_path)
            and report["binding_sha256"] == authority.binding["binding_sha256"],
            "Recovered WorldData is not bound to the stopped process")
    units = [row["unit"] for row in report["sources"] if row["family"] == "schedule"
             and row["commit_status"] == "COMMITTED_SUCCESS_VERIFIED"]
    unit, = units
    recovered_snapshot = {"identity": round_plan["identity"], "start": plan["start"],
                          "provenance": {"unit_refs": {"schedule": unit}}}
    schedule = schedule_for(database, recovered_snapshot)
    rows = [row for row in schedule if plan["start"] <= row["day"] <= plan["stop_exclusive"]]
    require({(int(row["id"]), row["day"], int(row["home"]), int(row["away"])) for row in rows}
            == {(row["id"], row["day"], row["home"], row["away"]) for row in plan["games"]}
            and all(row["type"] == "NORMAL" and row["status_code"] == "0" and row["is_final"] == 0
                    and row["played"] is None for row in rows), "Recovered schedule has partial or unknown effects")
    results = [cal.load(path) for path in sorted(old.glob("vae-v2-r01-s*-result.json"))]
    require(len(results) == 12 and all(row["success_count"] == 1 and row["readback_verified"] is True for row in results),
            "Missing exact previous S4 treatment receipt")
    outcomes = [dict(uid=target["uid"], **row) for target, row in zip(round_plan["write_candidates"], results, strict=True)]
    authority.setter_count = len(outcomes)
    authority.reserved_players.update(row["uid"] for row in outcomes)
    authority.calendar_count = len(list(old.glob("calendar-*-reservation.json")))
    require(authority.calendar_count == 3, "Unexpected prior calendar claim count")
    prior = [cal.load(old / f"round-01-sim-{number:02d}.json") for number in (1, 2)]
    require(all(row["status"] == "VERIFIED_IN_MEMORY" for row in prior) and prior[-1]["today"] == plan["start"],
            "Prior successful calendar chain differs")
    proof_path = args.output / "round-01-interruption-reconciled.json"
    freeze(proof_path, {"status": "INTERRUPTED_NO_CALENDAR_EFFECT", "prior_plan_digest": cal.digest(plan),
                        "prior_evidence": raw["evidence_id"], "recovered_frame": frame_receipt["evidence_id"],
                        "worlddata_report_sha256": capture["source_report_sha256"],
                        "unchanged_pending_ids": sorted(int(row["id"]) for row in rows),
                        "today": plan["start"], "today_raw": recovered_today["raw"], "original_native_call_consumed": True})
    outbox.record_test_calendar_no_effect(cal.digest(plan), old_result["private_receipt"],
                                          f"sha256:{cal.sha_file(proof_path)}")
    return schedule, frame["thread"], frame_receipt["evidence_id"], outcomes, prior, recovered_today["raw"]


def recover_round_two_setters(args, cal, authority, plan, host):
    directory = args.resume_round_two
    outcomes = []
    for index, target in enumerate(plan["write_candidates"], 1):
        cycle = f"vae-v2-r02-s{index:02d}"
        path = directory / f"{cycle}-result.json"
        if path.exists():
            result = cal.load(path)
            reservation = cal.load(directory / f"{cycle}-reservation.json")
            require(result["success_count"] == 1 and result["readback_verified"] is True
                    and reservation["target"] == target and reservation["plan_digest"] == result["plan_digest"],
                    "Previous S4 reservation and verified result differ")
            outcomes.append(dict(uid=target["uid"], **result))
            authority.reserved_players.add(target["uid"])
        else:
            reservation = cal.load(directory / f"{cycle}-reservation.json")
            seal = cal.load(directory / f"{cycle}-seal.json")
            runtime = directory / cycle / "runtime"
            claims = directory / cycle / "claims"
            error_path = directory.with_suffix(".stderr.log")
            error = error_path.read_text(encoding="utf-8")
            require(reservation["target"] == target and reservation["plan_digest"] == seal["plan_digest"]
                    and not 0 <= target["team_id"] <= 29
                    and runtime.is_dir() and claims.is_dir() and not any(runtime.iterdir()) and not any(claims.iterdir())
                    and "chunks = self.planner.plan(batch, max_chunk_size=max_chunk_size)" in error
                    and f"team_id must be integer in range 0..29, got {target['team_id']}" in error,
                    "Missing or unresolved previous setter")
            getter = host._get_fresh_live_getter(expected_pid=authority.epoch["pid"], expected_team=target["team_id"],
                                                expected_players={target["uid"]},
                                                expected_creation_filetime=authority.epoch["creation_filetime"])
            require(getter is not None and getter(target["uid"], FIELD) == target["expected_before"],
                    "Unchanged Native Getter value could not reconcile the rejected setter")
            proof = args.output / f"{cycle}-reconciled.json"
            freeze(proof, dict(status="PLANNER_REJECTED_BEFORE_NATIVE_DISPATCH", plan_digest=seal["plan_digest"],
                               stderr_sha256=cal.sha_file(error_path), unchanged_getter=target["expected_before"]))
            host.outbox.reconcile_rejected_research_setter(cycle, seal["plan_digest"], f"sha256:{cal.sha_file(proof)}")
            outcomes.append(dict(uid=target["uid"], status="LOCAL_WRITER_TEAM_OUTSIDE_CERTIFIED_RANGE"))
    first_setters = [cal.load(path) for path in args.prior_setters.glob("vae-v2-r01-s*-reservation.json")]
    require(len(first_setters) == 12 and len(authority.reserved_players) == 11,
            "Verified setter history is incomplete")
    authority.reserved_players.update(row["target"]["uid"] for row in first_setters)
    authority.setter_count = len(first_setters) + len(list(directory.glob("vae-v2-r02-s*-reservation.json")))
    authority.calendar_count = len(list(args.prior_setters.glob("calendar-*-reservation.json"))) + len(
        list(directory.glob("calendar-*-reservation.json")))
    require(authority.setter_count == 24 and len(authority.reserved_players) == 23 and authority.calendar_count == 5,
            "Cumulative recovered V2 budget differs")
    freeze(args.output / "round-02-recovered-setters.json", outcomes)
    return outcomes


def recover_after_allstar(args, cal, authority, template, snapshot, host):
    old = args.resume_post_allstar
    original = cal.load(old / "round-05-sim-01.json")
    folder = Path(original["private_receipt"])
    raw = cal.load(folder / "evidence.json")
    manifest = cal.load(folder / "request.json")
    js = (folder / "program.js").read_text(encoding="utf-8")
    packed = json.loads(next(line for line in js.splitlines() if line.startswith("const calendarPlan = "))
                        .removeprefix("const calendarPlan = ").removesuffix(";"))
    native = raw["normalized_result"]
    payloads = [row["payload"] for row in native["messages"] if row["type"] == "send"]
    require(original["status"] == "UNKNOWN_NO_REPLAY"
            and manifest["request_id"] == packed["plan_digest"] == original["plan_digest"]
            and manifest["script_sha256"] == cal.sha_file(folder / "program.js")
            and manifest["maximum_game_calls"] == 1 and native["pid"] == authority.epoch["pid"]
            and not native["messages_truncated"] and native["cleanup_error"] is None
            and payloads == [{"event": "WILL_DISPATCH_ONCE", "command": 17, "thread": packed["thread"],
                              "selected": packed["selected"]}], "Post-event original dispatch is ambiguous")
    require(authority.next_start >= date(2022, 2, 21) and cal.word(authority.next_start) > packed["stop"],
            "Native Today is not beyond the Human-handled event and original request")
    historical = dict(snapshot, start="2022-02-05")
    schedule = schedule_for(Path(template["database"]), historical)
    planned = {(row["id"], row["day"], row["home"], row["away"]) for row in packed["games"]}
    recovered = [row for row in schedule if row["day"] <= "2022-02-07"]
    require(planned == {(int(row["id"]), cal.word(date.fromisoformat(row["day"])), int(row["home"]), int(row["away"]))
                        for row in recovered}
            and all(row["is_final"] == 1 and row["played"] == row["day"] for row in recovered),
            "WorldData did not prove the old window closed")
    roots = (args.prior_setters, args.prior_second_run, old)
    setters = [cal.load(path) for root in roots for path in root.glob("vae-v2-*-reservation.json")]
    authority.setter_count = len(setters)
    authority.reserved_players = {row["target"]["uid"] for row in setters}
    authority.calendar_count = sum(len(list(root.glob("calendar-*-reservation.json"))) for root in roots)
    require(authority.setter_count == 60 and authority.calendar_count == 18, "Original V2 budgets are not conserved")
    authority.round_count = 5
    authority.season_stop = min(authority.season_stop, date(2022, 4, 16))
    proof = args.output / "round-05-human-event-reconciliation.json"
    freeze(proof, {"status": "HUMAN_ADVANCED_PAST_REQUEST", "today": authority.next_start.isoformat(),
                   "prior_plan_digest": original["plan_digest"], "prior_evidence": raw["evidence_id"],
                   "worlddata_report_sha256": snapshot["identity"]["source_report_sha256"],
                   "original_window_closed_game_ids": sorted(int(row["id"]) for row in recovered),
                   "attribution": "EXCLUDED_HUMAN_ASSISTED_EVENT_INTERVAL", "setter_reservations": authority.setter_count,
                   "calendar_reservations": authority.calendar_count})
    host.outbox.record_test_calendar_human_advance(original["plan_digest"], original["private_receipt"],
                                                  f"sha256:{cal.sha_file(proof)}")


def advance_empty_days(args, cal, authority, template, schedule, season_stop):
    first_game = min(date.fromisoformat(row["day"]) for row in schedule if row["type"] == "NORMAL")
    if first_game == authority.next_start:
        return None
    while authority.next_start < first_game:
        start = authority.next_start
        end = min(first_game, start + timedelta(days=2))
        rows = [row for row in schedule if start.isoformat() <= row["day"] <= end.isoformat()]
        require(all(row["day"] == end.isoformat() and row["type"] == "NORMAL" and row["status_code"] == "0"
                    and row["is_final"] == 0 and row["played"] is None for row in rows),
                "Empty-day transit intersects a game or event")
        window = dict(template, start=start.isoformat(), stop_exclusive=end.isoformat(), today_raw=cal.word(start),
                      empty_transit=True, season_stop_exclusive=season_stop.isoformat(),
                      authorization_scope=authority.ref,
                      games=[{k: int(row[k]) if k != "day" else row[k] for k in ("id", "day", "home", "away")}
                             for row in rows])
        thread, ref = read_frame(cal, authority, window, args.output / f"transit-frame-{start}")
        window.update(engine_thread=thread, engine_thread_evidence=ref)
        run_calendar(cal, authority, template, window, args.output / f"transit-calendar-{start}")
    return args.output / "post-transit-capture"


def run(args):
    sys.path[:0] = [str(WORLD), str(NATIVE), str(args.calendar)]
    from refresh import _context
    from season_cycle_host import HostState, SeasonCycleHost
    import calendar_cli as cal

    template = cal.load(args.template)
    context = cal.load(args.capture_receipt)
    capture = args.capture
    capture_receipt = args.capture_receipt
    pool = args.pool
    report_sha = context["source_report_sha256"]
    require(cal.sha_file(capture / "refresh-report.json") == report_sha, "Fresh capture report hash mismatch")
    snapshot = build(pool, Path(template["database"]), capture_receipt)
    schedule = schedule_for(Path(template["database"]), snapshot)
    last = max(date.fromisoformat(row["day"]) for row in schedule if row["type"] == "NORMAL")
    season_stop = last + timedelta(days=1)
    first = date.fromisoformat(snapshot["start"])
    args.output.mkdir()
    authority = ResearchAuthority(args.goal, args.goal_sha, args.output, template, template["epoch"], first, season_stop)
    if args.resume is None:
        authority.check_scene(_context(template["epoch"]["pid"]), SLOT, template["binding_sha256"])
    host = SeasonCycleHost(workspace_root=REPO, state_file=args.output / "host-state.json",
                           ledger_file=args.output / "host-ledger.jsonl", outbox_db=Path(template["outbox_db"]),
                           research_delegation=authority)
    host.state.update(status=HostState.BASELINE_CAPTURED, save_directory=template["save_directory"],
                      loaded_filename=SLOT, save_id=template["save_id"], worldline_id=template["worldline_id"],
                      database_file=template["database"], current_game_date=first.isoformat(),
                      is_offline_mock=False, is_mock=False, current_cycle_id=None, active_plan=None)
    host._save_state()
    results = []
    starting_round = 1
    if args.resume_round_two is not None:
        starting_round = 2
        authority.round_count = 1
        authority.season_stop = min(authority.season_stop, date(2022, 4, 16))
        previous = cal.load(args.resume_round_two / "round-01-analysis.json")["summary"]
        merged = cal.load(args.resume_round_two / "round-01-reconciled-analysis.json")["summary"]
        results.append(dict(previous, qualified_worlddata_games=merged["qualified_worlddata_games"],
                            effects=merged["contrasts"]))
    try:
        if args.resume_post_allstar is not None:
            recover_after_allstar(args, cal, authority, template, snapshot, host)
            starting_round = 6
            results = cal.load(args.resume_post_allstar / "STOP.json")["completed"]
            transit_capture = advance_empty_days(args, cal, authority, template, schedule, season_stop)
            if transit_capture is not None:
                capture = transit_capture
                capture_receipt = capture.with_suffix(".json")
                status = capture_world(capture, template, authority)
                freeze(capture_receipt, status)
                report_sha = status["source_report_sha256"]
                pool = args.output / "post-transit-pool"
                export_pool(args.r0, template, capture, report_sha, pool)
            snapshot = build(pool, Path(template["database"]), capture_receipt, excluded_uids=authority.reserved_players)
            schedule = schedule_for(Path(template["database"]), snapshot)
        for number in range(starting_round, MAX_CYCLES + 1):
            if authority.next_start + timedelta(days=7) > authority.season_stop:
                break
            resuming = args.resume is not None and number == 1
            resume_treatments = args.resume_round_two is not None and number == 2
            if resuming:
                round_plan = cal.load(args.resume / "round-01-plan.json")
            elif resume_treatments:
                round_plan = cal.load(args.resume_round_two / "round-02-plan.json")
            else:
                round_plan = make_plan(snapshot, 20261107 + number - 1, writable_teams=range(30))
            authority.bind_round(round_plan)
            host.state["current_game_date"] = round_plan["start"]
            prior = []
            if resuming:
                schedule, thread, frame_ref, outcomes, prior, recovered_word = reconcile_interruption(
                    args, cal, authority, round_plan, Path(template["database"]), host.outbox)
                windows = subplans(template, round_plan, schedule, authority, season_stop, cal,
                                   resume_from=authority.next_start)
                windows[0]["today_raw"] = recovered_word
            else:
                windows = subplans(template, round_plan, schedule, authority, season_stop, cal)
                thread, frame_ref = read_frame(cal, authority, windows[0], args.output / f"frame-{number:02d}")
                if resume_treatments:
                    outcomes = recover_round_two_setters(args, cal, authority, round_plan, host)
                else:
                    outcomes = apply_setters(host, authority, round_plan, args.output)
            for window in windows:
                window.update(engine_thread=thread, engine_thread_evidence=frame_ref)
            treated = {row["uid"] for row in outcomes if row.get("success_count") == 1}
            require(treated, "No verified treatment in this cycle")
            finals = [game for item in prior for game in item["final_game_ids"]]
            calls = [item["evidence_id"] for item in prior]
            for index, window in enumerate(windows, 4 if resuming else 1):
                result = run_calendar(cal, authority, template, window,
                                      args.output / f"round-{number:02d}-sim-{index:02d}")
                finals.extend(result["final_game_ids"])
                calls.append(result["evidence_id"])
            require(sorted(finals) == round_plan["planned_expected_game_ids"], "Window schedule mismatch")
            capture = args.output / f"round-{number:02d}-post"
            status = capture_world(capture, template, authority)
            capture_receipt = capture.with_suffix(".json")
            freeze(capture_receipt, status)
            report_sha = status["source_report_sha256"]
            audit, data = readback(round_plan, capture, Path(template["save_directory"]), SLOT, report_sha)
            game_ids = set(audit["verified_game_ids"])
            screened = dict(round_plan, games=[game for game in round_plan["games"] if game["game_id"] in game_ids])
            # For the per-protocol screen, exclude entire strata with a missed treatment.
            dropped = {row["stratum"] for row in round_plan["assignments"]
                       if row["arm"] in ("H", "L") and row["uid"] not in treated}
            screened["assignments"] = [dict(row, arm="RESERVE") if row["stratum"] in dropped else row
                                       for row in round_plan["assignments"]]
            screen_arms = {row["team_id"]: row["arm"] for row in screened["assignments"]}
            screened["games"] = [dict(game, home_arm=screen_arms[game["home"]], away_arm=screen_arms[game["away"]])
                                 for game in screened["games"]]
            effect = analyze(screened, data) if game_ids else {"classification": "NO_QUALIFIED_WORLDDATA", "contrasts": {}}
            summary = {"cycle": number, "today": authority.next_start.isoformat(), "setter_success": len(treated),
                       "setter_candidates": len(outcomes), "calendar_calls": len(calls), "final_games": len(finals),
                       "qualified_worlddata_games": len(game_ids), "effects": effect["contrasts"],
                       "classification": effect["classification"], "persistence": "IN_MEMORY_ONLY"}
            freeze(args.output / f"round-{number:02d}-analysis.json", dict(summary=summary, audit=audit, effect=effect,
                                                                         calls=calls, setter_outcomes=outcomes))
            results.append(summary)
            print(json.dumps(summary), flush=True)
            if (number == MAX_CYCLES or authority.setter_count == MAX_SETTERS or authority.calendar_count == MAX_CALENDAR
                    or authority.next_start + timedelta(days=7) > authority.season_stop):
                break
            pool = args.output / f"round-{number:02d}-next-pool"
            export_pool(args.r0, template, capture, report_sha, pool)
            snapshot = build(pool, Path(template["database"]), capture_receipt, excluded_uids=authority.reserved_players)
            schedule = schedule_for(Path(template["database"]), snapshot)
    except Exception as error:
        freeze(args.output / "STOP.json", dict(status="STOPPED", reason=str(error), completed=results,
                                              setter_reservations=authority.setter_count,
                                              calendar_reservations=authority.calendar_count,
                                              today=authority.next_start.isoformat()))
        raise
    freeze(args.output / "STOP.json", dict(status="BOUND_REACHED", completed=results,
                                          today=authority.next_start.isoformat(), persistence="IN_MEMORY_ONLY"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("template", "capture", "capture-receipt", "pool", "calendar", "r0", "goal", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    for name in ("resume", "recovery-capture", "recovery-receipt", "recovery-original", "recovery-frame", "recovery-raw"):
        parser.add_argument(f"--{name}", type=Path)
    parser.add_argument("--resume-round-two", type=Path)
    parser.add_argument("--prior-setters", type=Path)
    parser.add_argument("--prior-second-run", type=Path)
    parser.add_argument("--resume-post-allstar", type=Path)
    parser.add_argument("--goal-sha", required=True)
    run(parser.parse_args())
