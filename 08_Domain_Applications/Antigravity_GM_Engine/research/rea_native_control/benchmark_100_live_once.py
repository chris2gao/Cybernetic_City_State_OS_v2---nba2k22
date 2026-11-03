"""100-Item Live Bulk Modification Benchmark Runner.
Executes one-shot live benchmark on NBA2K22 with BoundedSessionExecutor.
"""
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

_RESEARCH_DIR = Path(__file__).resolve().parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

import contracts
import registry
import transport
from bulk_executor import (
    BulkBatch,
    BulkBatchHeader,
    BulkIntentItem,
    BulkBatchPlanner,
    CrossProcessFileLock,
    canonical_encode,
    sha256_digest
)
from bounded_session_transport import BoundedSessionExecutor
from validate_100_receipts import validate_stage


def get_game_process_info() -> Dict[str, Any]:
    """Finds active NBA2K22 process and checks executable SHA256 and start time."""
    cmd = ["powershell", "-NoProfile", "-Command", 
           "Get-Process -Name NBA2K22 -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, Path, @{Name='StartTime';Expression={$_.StartTime.ToString('o')}} | ConvertTo-Json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError("NBA2K22_NOT_RUNNING: NBA2K22.exe process not found")
    data = json.loads(proc.stdout)
    if isinstance(data, list):
        if len(data) != 1:
            raise RuntimeError(f"MULTIPLE_NBA2K22_PROCESSES: Found {len(data)} processes, exactly 1 required")
        data = data[0]

    pid = int(data["Id"])
    exe_path = Path(data["Path"])
    if not exe_path.is_file():
        raise RuntimeError(f"EXE_NOT_FOUND: {exe_path}")

    h = hashlib.sha256(exe_path.read_bytes()).hexdigest().lower()
    return {
        "pid": pid,
        "process_name": data["ProcessName"],
        "path": str(exe_path),
        "start_time": data.get("StartTime"),
        "exe_sha256": h
    }


def perform_preflight(run_dir: Path) -> Dict[str, Any]:
    """Gate G2 / G4: Verifies process, build hash, save file, cold backup, and lock state."""
    proc_info = get_game_process_info()
    if proc_info["exe_sha256"] != contracts.BUILD:
        raise RuntimeError(f"BUILD_MISMATCH: Expected {contracts.BUILD}, got {proc_info['exe_sha256']}")

    # Save file check
    save_path = Path("E:/games/NBA 2K22/data/steam/steam_settings/1644960/remote/MyLEAGUE0003")
    if not save_path.is_file():
        raise RuntimeError(f"ACTIVE_SAVE_NOT_FOUND: {save_path}")

    save_bytes = save_path.read_bytes()
    save_sha256 = hashlib.sha256(save_bytes).hexdigest().lower()

    # Cold backup check
    cold_backup_path = Path("01_os/07_content/_runs/run-20261101-nba2k22-rea-controlled-live-bulk-pilot-001/cold_backup/MyLEAGUE0003_cold_backup")
    if not cold_backup_path.is_file():
        raise RuntimeError(f"COLD_BACKUP_NOT_FOUND: {cold_backup_path}")

    cold_bytes = cold_backup_path.read_bytes()
    cold_sha256 = hashlib.sha256(cold_bytes).hexdigest().lower()
    expected_cold_sha256 = "363cc773f935f632785c54c4d9ab1bf73455bb625b56797823f532eafcdf02d7"
    if cold_sha256 != expected_cold_sha256:
        raise RuntimeError(f"COLD_BACKUP_HASH_MISMATCH: Expected {expected_cold_sha256}, got {cold_sha256}")

    preflight_data = {
        "schema_version": "nba2k22.rea.preflight.v1",
        "task_id": "NBA2K22-REA-100-LIVE-BENCHMARK-20261102-001",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "game_process": proc_info,
        "active_save": {
            "instance_id": "MyLEAGUE0003",
            "path": str(save_path),
            "byte_length": len(save_bytes),
            "sha256": save_sha256
        },
        "cold_backup": {
            "path": str(cold_backup_path),
            "byte_length": len(cold_bytes),
            "sha256": cold_sha256,
            "verified": True
        },
        "preflight_status": "PASSED"
    }

    out_file = run_dir / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / "preflight.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(preflight_data, indent=2, ensure_ascii=False), encoding="utf-8")
    return preflight_data


def probe_live_candidates(run_dir: Path, expected_pid: int) -> List[Dict[str, Any]]:
    """Gate G3: Scans live teams and gathers 100 distinct players with fresh live Getter."""
    reg = registry.NativeActionRegistry(_RESEARCH_DIR)
    common_js = (_RESEARCH_DIR / 'runtime' / 'common.js').read_text(encoding='utf-8')
    gui_once_js = (_RESEARCH_DIR / 'runtime' / 'gui_once.js').read_text(encoding='utf-8')

    b_stat = reg.binding('player.get_stat_ui').to_dict()
    bindings = {'player.get_stat_ui': b_stat}

    target_teams = [0, 1, 2, 3, 4, 5, 6, 7]
    req = {
        'action_id': 'PLAYER_PATCH_TENDENCIES',
        'request_id': 'probe_100_candidates',
        'parameters': {'target_teams': target_teams}
    }
    limits = {'maximum_game_calls': 500, 'read_bytes': 2097152, 'is_live': True}

    action_js = """
const u8 = (b, o = 0) => new DataView(b).getUint8(o);
function executeAction() {
  const targetTeams = [0, 1, 2, 3, 4, 5, 6, 7];
  const allPlayers = [];
  for (const tid of targetTeams) {
    let t;
    try { t = team(tid); } catch(e) { continue; }
    const b = read(t, 4696);
    const teamAbbr = text(b.slice(0x30a, 0x314));
    for (let i = 0; i < 15; i++) {
      const pp = ptrAt(b, i * 8);
      if (pp.isNull()) continue;
      const v = read(pp, 1264);
      const uid = u16(v, 0xf4);
      const firstName = text(v.slice(40, 80));
      const lastName = text(v.slice(0, 40));
      const fullName = (firstName + ' ' + lastName).trim();
      const val = call('player.get_stat_ui', pp, 57);
      const raw = u8(read(pp.add(0x458), 1));
      allPlayers.push({
        team_id: tid,
        team_abbr: teamAbbr,
        slot: i,
        player_id: uid,
        name: fullName,
        shot_tendency: val,
        raw_byte: raw
      });
    }
  }
  send({
    kind: 'chunk-execution-result',
    chunk_id: 'probe_100',
    chunk_digest: 'd',
    plan_digest: 'p',
    action_id: 'PLAYER_PATCH_TENDENCIES',
    batch_id: 'PROBE-100',
    save_instance_id: 'MyLEAGUE0003',
    outcome: 'CHUNK_SUCCESS',
    details: { total_players: allPlayers.length, players: allPlayers },
    receipts: []
  });
}
"""
    script = (
        common_js + "\n" +
        action_js + "\n" +
        gui_once_js
    )
    script = (
        script
        .replace('__REQUEST__', canonical_encode(req))
        .replace('__BINDINGS__', canonical_encode(bindings))
        .replace('__LIMITS__', canonical_encode(limits))
        .replace('__COACH_FIELDS__', '{}')
        .replace('__PLAYER_CONTRACT_FIELDS__', '{}')
    )

    probe_dir = run_dir / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / "probe_100_candidates"
    probe_dir.mkdir(parents=True, exist_ok=True)

    live_ctx = transport.LiveExecutionContext(
        authorization_ref="HUMAN-READONLY-PROBE-100",
        allowed_action_ids=frozenset(["PLAYER_PATCH_TENDENCIES"]),
        maximum_game_calls=500,
        enabled=True,
        expected_pid=expected_pid
    )
    cli = transport.ReaCliTransport(probe_dir, live_ctx, duration_ms=10000)
    res = cli.execute(script, action_id='PLAYER_PATCH_TENDENCIES', request_id='req_probe_100', maximum_game_calls=500)
    if res.get('outcome') != 'CHUNK_SUCCESS':
        raise RuntimeError(f"PROBE_FAILED: Live candidate scan failed: {res.get('outcome')}")

    raw_players = res.get('details', {}).get('players', [])
    if len(raw_players) < 100:
        raise RuntimeError(f"INSUFFICIENT_PLAYERS: Found {len(raw_players)} active players, minimum 100 required")

    # Select exactly 100 unique players
    selected_players: List[Dict[str, Any]] = []
    seen_pids = set()
    for p in raw_players:
        pid = p["player_id"]
        if pid in seen_pids:
            continue
        seen_pids.add(pid)

        before_val = p["shot_tendency"]
        # Policy: if 100 -> 99, otherwise before_val + 1
        target_val = 99 if before_val == 100 else (before_val + 1)

        candidate = {
            "index": len(selected_players) + 1,
            "team_id": p["team_id"],
            "team_abbr": p["team_abbr"],
            "player_id": pid,
            "name": p["name"],
            "field_id": "SHOT_TENDENCY",
            "shot_tendency_getter": before_val,
            "shot_tendency_raw": p["raw_byte"],
            "target_tendency": target_val,
            "change_delta": target_val - before_val
        }
        selected_players.append(candidate)
        if len(selected_players) == 100:
            break

    if len(selected_players) != 100:
        raise RuntimeError(f"CANNOT_SELECT_100: Selected {len(selected_players)} unique players")

    # Save candidate inventory
    inv_file = run_dir / ("06_" + "\u6267\u884c") / "live_candidate_inventory.json"
    inv_file.parent.mkdir(parents=True, exist_ok=True)
    inv_file.write_text(json.dumps({
        "schema_version": "nba2k22.rea.live_candidate_inventory.v1",
        "task_id": "NBA2K22-REA-100-LIVE-BENCHMARK-20261102-001",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_selected": len(selected_players),
        "target_policy": "If 0..99 => before + 1; if 100 => 99; strictly 1-point change",
        "candidates": selected_players
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    return selected_players


def build_batch(
    batch_id: str,
    candidates: List[Dict[str, Any]],
    expected_pid: int,
    mode: str = "mutation"  # "noop" or "mutation"
) -> BulkBatch:
    intents = []
    for c in candidates:
        before_val = c["shot_tendency_getter"]
        target_val = before_val if mode == "noop" else c["target_tendency"]
        intents.append(BulkIntentItem(
            intent_id=f"I-{batch_id}-T{c['team_id']}-P{c['player_id']}",
            action_id="PLAYER_PATCH_TENDENCIES",
            team_id=c["team_id"],
            field_id="SHOT_TENDENCY",
            expected_before=before_val,
            value=target_val,
            player_id=c["player_id"]
        ))

    header = BulkBatchHeader(
        batch_id=batch_id,
        save_instance_id="MyLEAGUE0003",
        game_build_sha256=contracts.BUILD,
        authorization_ref="HUMAN-100-LIVE-BENCHMARK-AUTH-20261102",
        source_snapshot_ref="snapshot_live_probe_100",
        expected_process_name="NBA2K22.exe",
        expected_pid=expected_pid,
        dry_run=False
    )
    return BulkBatch(header=header, intents=tuple(intents))


def execute_session_stage(
    stage_dir: Path,
    batch: BulkBatch,
    expected_pid: int,
    duration_ms: int = 5000
) -> Dict[str, Any]:
    stage_dir.mkdir(parents=True, exist_ok=True)
    journal_dir = stage_dir / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir = stage_dir / "rea_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    # Write batch file
    batch_file = stage_dir / f"batch_{batch.header.batch_id}.json"
    batch_file.write_text(json.dumps({
        **asdict(batch.header),
        "intents": [asdict(i) for i in batch.intents]
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write manifest file
    cold_backup_path = "01_os/07_content/_runs/run-20261101-nba2k22-rea-controlled-live-bulk-pilot-001/cold_backup/MyLEAGUE0003_cold_backup"
    manifest = {
        "task_id": "NBA2K22-REA-100-LIVE-BENCHMARK-20261102-001",
        "human_authorization_ref": batch.header.authorization_ref,
        "plan_digest": batch.plan_digest,
        "save_instance_id": batch.header.save_instance_id,
        "game_build_sha256": batch.header.game_build_sha256,
        "allowed_action_ids": ["PLAYER_PATCH_TENDENCIES", "MULTI_CHUNK_BOUNDED_SESSION"],
        "allowed_fields": ["SHOT_TENDENCY"],
        "expected_pid": expected_pid,
        "maximum_game_calls": 500,
        "cold_backup_path": cold_backup_path,
        "cold_backup_sha256": "363cc773f935f632785c54c4d9ab1bf73455bb625b56797823f532eafcdf02d7"
    }
    manifest_file = stage_dir / f"manifest_{batch.header.batch_id}.json"
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    live_ctx = transport.LiveExecutionContext(
        authorization_ref=manifest["human_authorization_ref"],
        allowed_action_ids=frozenset(manifest["allowed_action_ids"]),
        maximum_game_calls=manifest["maximum_game_calls"],
        enabled=True,
        expected_pid=expected_pid
    )

    executor = BoundedSessionExecutor(
        journal_dir=journal_dir,
        live_context=live_ctx,
        verifier=manifest,
        runtime_dir=runtime_dir,
        duration_ms=duration_ms
    )

    t0 = time.perf_counter()
    res = executor.execute_batch(batch, max_chunk_size=50)
    wall_seconds = time.perf_counter() - t0
    res["wall_clock_seconds"] = round(wall_seconds, 5)

    res_file = stage_dir / "execution_result.json"
    res_file.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    return res


def probe_independent_readback(
    run_dir: Path,
    candidates: List[Dict[str, Any]],
    expected_pid: int
) -> Dict[str, Any]:
    """Gate G9: In an independent REA session, reads back all 100 values to prove game memory persisted."""
    reg = registry.NativeActionRegistry(_RESEARCH_DIR)
    common_js = (_RESEARCH_DIR / 'runtime' / 'common.js').read_text(encoding='utf-8')
    gui_once_js = (_RESEARCH_DIR / 'runtime' / 'gui_once.js').read_text(encoding='utf-8')

    b_stat = reg.binding('player.get_stat_ui').to_dict()
    bindings = {'player.get_stat_ui': b_stat}

    teams = sorted(list(set(c["team_id"] for c in candidates)))
    req = {
        'action_id': 'PLAYER_PATCH_TENDENCIES',
        'request_id': 'independent_readback_100',
        'parameters': {'target_teams': teams}
    }
    limits = {'maximum_game_calls': 500, 'read_bytes': 2097152, 'is_live': True}

    action_js = f"""
const u8 = (b, o = 0) => new DataView(b).getUint8(o);
function executeAction() {{
  const targetTeams = {json.dumps(teams)};
  const readbackResults = [];
  for (const tid of targetTeams) {{
    let t;
    try {{ t = team(tid); }} catch(e) {{ continue; }}
    const b = read(t, 4696);
    for (let i = 0; i < 15; i++) {{
      const pp = ptrAt(b, i * 8);
      if (pp.isNull()) continue;
      const v = read(pp, 1264);
      const uid = u16(v, 0xf4);
      const val = call('player.get_stat_ui', pp, 57);
      const raw = u8(read(pp.add(0x458), 1));
      readbackResults.push({{
        team_id: tid,
        player_id: uid,
        shot_tendency_getter: val,
        shot_tendency_raw: raw
      }});
    }}
  }}
  send({{
    kind: 'chunk-execution-result',
    chunk_id: 'readback_100',
    chunk_digest: 'd',
    plan_digest: 'p',
    action_id: 'PLAYER_PATCH_TENDENCIES',
    batch_id: 'READBACK-100',
    save_instance_id: 'MyLEAGUE0003',
    outcome: 'CHUNK_SUCCESS',
    details: {{ readback: readbackResults }},
    receipts: []
  }});
}}
"""
    script = (
        common_js + "\n" +
        action_js + "\n" +
        gui_once_js
    )
    script = (
        script
        .replace('__REQUEST__', canonical_encode(req))
        .replace('__BINDINGS__', canonical_encode(bindings))
        .replace('__LIMITS__', canonical_encode(limits))
        .replace('__COACH_FIELDS__', '{}')
        .replace('__PLAYER_CONTRACT_FIELDS__', '{}')
    )

    rb_dir = run_dir / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / "independent_readback_run"
    rb_dir.mkdir(parents=True, exist_ok=True)

    live_ctx = transport.LiveExecutionContext(
        authorization_ref="HUMAN-INDEPENDENT-READBACK-100",
        allowed_action_ids=frozenset(["PLAYER_PATCH_TENDENCIES"]),
        maximum_game_calls=500,
        enabled=True,
        expected_pid=expected_pid
    )
    cli = transport.ReaCliTransport(rb_dir, live_ctx, duration_ms=10000)
    t0 = time.perf_counter()
    res = cli.execute(script, action_id='PLAYER_PATCH_TENDENCIES', request_id='req_rb_100', maximum_game_calls=500)
    rb_wall_s = time.perf_counter() - t0

    if res.get('outcome') != 'CHUNK_SUCCESS':
        raise RuntimeError(f"READBACK_FAILED: Independent readback failed: {res.get('outcome')}")

    all_readback = res.get('details', {}).get('readback', [])
    lookup = { (r["team_id"], r["player_id"]): r for r in all_readback }

    verified_items = []
    missed_items = []
    for c in candidates:
        key = (c["team_id"], c["player_id"])
        rb_entry = lookup.get(key)
        if not rb_entry:
            missed_items.append({"candidate": c, "reason": "PLAYER_NOT_FOUND_IN_READBACK"})
            continue

        actual_val = rb_entry["shot_tendency_getter"]
        expected_target = c["target_tendency"]
        if actual_val != expected_target:
            missed_items.append({
                "candidate": c,
                "reason": f"VALUE_MISMATCH: expected {expected_target}, got {actual_val}"
            })
        else:
            verified_items.append({
                "team_id": c["team_id"],
                "player_id": c["player_id"],
                "name": c["name"],
                "initial_getter": c["shot_tendency_getter"],
                "target_tendency": expected_target,
                "readback_getter": actual_val,
                "readback_raw_byte": rb_entry["shot_tendency_raw"],
                "confirmed": True
            })

    readback_report = {
        "schema_version": "nba2k22.rea.independent_readback.v1",
        "task_id": "NBA2K22-REA-100-LIVE-BENCHMARK-20261102-001",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "readback_wall_seconds": round(rb_wall_s, 5),
        "total_targets_evaluated": len(candidates),
        "verified_count": len(verified_items),
        "missed_count": len(missed_items),
        "all_100_persisted_in_game": (len(verified_items) == 100 and len(missed_items) == 0),
        "verified_items": verified_items,
        "missed_items": missed_items
    }

    out_file = run_dir / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / "independent_readback.json"
    out_file.write_text(json.dumps(readback_report, indent=2, ensure_ascii=False), encoding="utf-8")
    return readback_report


def run_100_benchmark():
    run_dir = (_RESEARCH_DIR / "../../../.." / "01_os/07_content/_runs/run-20261102-nba2k22-rea-100-live-benchmark-001").resolve()
    print(f"=== Starting REA 100-Item Live Benchmark on {run_dir.name} ===")

    # 1. Lock check
    lock_path = run_dir / ("06_" + "\u6267\u884c") / ".rea_benchmark.lock"
    with CrossProcessFileLock(lock_path):
        # 2. Gate G2 / G4: Preflight
        print("\n--- Gate G2/G4: Preflight Verification ---")
        t_preflight_0 = time.perf_counter()
        preflight = perform_preflight(run_dir)
        preflight_s = round(time.perf_counter() - t_preflight_0, 5)
        pid = preflight["game_process"]["pid"]
        print(f"[+] Preflight passed for PID {pid} (Build: {preflight['game_process']['exe_sha256'][:16]}...) in {preflight_s}s")

        # 3. Gate G3: Scan 100 Live Candidates
        print("\n--- Gate G3: Probe 100 Live Target Players ---")
        t_probe_0 = time.perf_counter()
        candidates = probe_live_candidates(run_dir, expected_pid=pid)
        probe_s = round(time.perf_counter() - t_probe_0, 5)
        print(f"[+] Scanned and selected {len(candidates)} distinct players across {len(set(c['team_id'] for c in candidates))} teams in {probe_s}s")

        # 4. Gate G6: Stage 1 - 100-Item Live No-op Batch
        print("\n--- Gate G6: Stage 1 - 100-Item Live No-op Execution ---")
        noop_dir = run_dir / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / "noop_100"
        batch_noop = build_batch("BATCH-100-BENCH-NOOP", candidates, expected_pid=pid, mode="noop")
        t_noop_0 = time.perf_counter()
        res_noop = execute_session_stage(noop_dir, batch_noop, expected_pid=pid, duration_ms=5000)
        noop_s = round(time.perf_counter() - t_noop_0, 5)

        # Copy execution result to run level
        noop_exec_file = run_dir / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / "noop_100_execution_result.json"
        noop_exec_file.write_text(json.dumps(res_noop, indent=2, ensure_ascii=False), encoding="utf-8")

        val_noop = validate_stage(noop_dir, expected_count=100, expected_mode="noop")
        print(f"[+] No-op completed in {noop_s}s (Transport: {res_noop['execution_time_ms']:.2f}ms, Chunks: {res_noop['chunk_count']})")
        print(f"    Validation: {'PASSED' if val_noop['validation_passed'] else 'FAILED'}")
        if not val_noop["validation_passed"]:
            raise RuntimeError(f"NOOP_VALIDATION_FAILED: {val_noop['errors']}")

        # 5. Gate G7: Stage 2 - Single 100-Item Live Mutation Batch
        print("\n--- Gate G7: Stage 2 - Single 100-Item Live Mutation Execution ---")
        mut_dir = run_dir / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / "mutation_100"
        batch_mut = build_batch("BATCH-100-BENCH-MUTATION", candidates, expected_pid=pid, mode="mutation")
        t_mut_0 = time.perf_counter()
        res_mut = execute_session_stage(mut_dir, batch_mut, expected_pid=pid, duration_ms=5000)
        full_benchmark_wall_seconds = round(time.perf_counter() - t_mut_0, 5)

        # Copy execution result to run level
        mut_exec_file = run_dir / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / "mutation_100_execution_result.json"
        mut_exec_file.write_text(json.dumps(res_mut, indent=2, ensure_ascii=False), encoding="utf-8")

        val_mut = validate_stage(mut_dir, expected_count=100, expected_mode="mutation")
        print(f"[+] Mutation completed in {full_benchmark_wall_seconds}s (Transport: {res_mut['execution_time_ms']:.2f}ms, Chunks: {res_mut['chunk_count']})")
        print(f"    Validation: {'PASSED' if val_mut['validation_passed'] else 'FAILED'}")
        if not val_mut["validation_passed"]:
            raise RuntimeError(f"MUTATION_VALIDATION_FAILED: {val_mut['errors']}")

        # 6. Gate G9: Stage 3 - Independent Post-Write Live Readback
        print("\n--- Gate G9: Stage 3 - Independent Post-Write Live Readback ---")
        rb_res = probe_independent_readback(run_dir, candidates, expected_pid=pid)
        print(f"[+] Independent readback completed in {rb_res['readback_wall_seconds']}s")
        print(f"    Verified: {rb_res['verified_count']}/100, Missed: {rb_res['missed_count']}")
        if not rb_res["all_100_persisted_in_game"]:
            raise RuntimeError(f"READBACK_VERIFICATION_FAILED: Missed {rb_res['missed_count']} players")

        # 7. Gate G8: Combined Validation Result
        val_combined = {
            "schema_version": "nba2k22.rea.validation_result.v1",
            "task_id": "NBA2K22-REA-100-LIVE-BENCHMARK-20261102-001",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "overall_status": "ALL_GATES_PASSED",
            "stages": {
                "preflight": {"status": "PASSED", "duration_seconds": preflight_s},
                "probe_scan": {"status": "PASSED", "selected_candidates": len(candidates), "duration_seconds": probe_s},
                "stage1_noop": val_noop,
                "stage2_mutation": val_mut,
                "stage3_readback": {
                    "status": "PASSED" if rb_res["all_100_persisted_in_game"] else "FAILED",
                    "verified_count": rb_res["verified_count"],
                    "missed_count": rb_res["missed_count"],
                    "duration_seconds": rb_res["readback_wall_seconds"]
                }
            }
        }
        val_file = run_dir / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / "validation_result.json"
        val_file.write_text(json.dumps(val_combined, indent=2, ensure_ascii=False), encoding="utf-8")

        # 8. Gate G10: Exact Benchmark Timing Report
        confirmed_success = res_mut["metrics"]["num_success"]
        sec_per_planned = round(full_benchmark_wall_seconds / 100.0, 5)
        sec_per_success = round(full_benchmark_wall_seconds / confirmed_success, 5) if confirmed_success else None

        # Compare with historical baselines:
        # Old 12-item per-chunk attach: 39.40411s total, 3.283676s / setter
        # New 12-item single-session: 7.23892s total, 0.60324s / setter
        baseline_12_session_wall_s = 7.23892
        baseline_12_session_per_setter = 0.60324
        baseline_12_per_chunk_wall_s = 39.40411
        baseline_12_per_chunk_per_setter = 3.283676

        speedup_vs_old_per_chunk = round(baseline_12_per_chunk_per_setter / sec_per_success, 2) if sec_per_success else None
        speedup_vs_12_session = round(baseline_12_session_per_setter / sec_per_success, 2) if sec_per_success else None

        print("\n========================================================")
        print("          NBA2K22 REA 100-ITEM BENCHMARK RESULTS        ")
        print("========================================================")
        print(f"  Target Items:                     100")
        print(f"  Confirmed Success:                {confirmed_success}/100")
        print(f"  Unknown Count:                    {res_mut['metrics']['num_unknown']}")
        print(f"  Conservation Holds:               {res_mut['metrics']['conservation_holds']}")
        print(f"  Frida Attach Count:               {res_mut['frida_attach_count']}")
        print(f"  Chunk Count:                      {res_mut['chunk_count']}")
        print(f"  Preflight Wall Time:              {preflight_s:.3f} s")
        print(f"  Probe Scan Wall Time:             {probe_s:.3f} s")
        print(f"  No-op Stage Wall Time:            {noop_s:.3f} s (100 NOOP, 0 Setters)")
        print(f"  Mutation Stage Full Wall Time:    {full_benchmark_wall_seconds:.3f} s")
        print(f"  Mutation Transport Time:          {res_mut['execution_time_ms'] / 1000.0:.3f} s")
        print(f"  Independent Readback Wall Time:   {rb_res['readback_wall_seconds']:.3f} s")
        print(f"  Wall Time per Planned Item:       {sec_per_planned:.5f} s")
        print(f"  Wall Time per Confirmed Success:  {sec_per_success:.5f} s")
        print(f"  Speedup vs Baseline Old Per-Chunk:{speedup_vs_old_per_chunk}x")
        print(f"  Speedup vs Baseline 12-Session:   {speedup_vs_12_session}x")
        print("========================================================")


if __name__ == "__main__":
    run_100_benchmark()
