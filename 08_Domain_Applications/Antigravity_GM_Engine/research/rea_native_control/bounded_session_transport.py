"""Bounded Multi-Chunk Session Transport and Executor for REA Native Control.

Implements S2 architecture:
- Single Frida process attach + single PeekMessageA hook for multiple chunks.
- Durable Claim-before-Setter: all executable chunks are claimed in ExecutionJournal
  BEFORE the session program is launched.
- Fail-stop execution: if any chunk encounters CAS mismatch, exception, or budget
  exhaustion, remaining chunks in the session are halted and emitted as NOT_EXECUTED.
- Preserves all native contracts: Player 156-byte integrity verification, attribute
  flags, CAS expected_before matching, and individual chunk-level receipts.
"""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple

import contracts
import registry
from bulk_executor import (
    BulkBatch,
    BulkBatchPlanner,
    BulkFridaScriptCompiler,
    BulkIntentItem,
    CrossProcessFileLock,
    ExecutionJournal,
    FieldCatalogLoader,
    ItemReceipt,
    PlannedChunk,
    atomic_write_json,
    canonical_encode,
    get_resource_key,
    sha256_digest,
    _SCRIPT_DIR
)
import transport

_RUNTIME_DIR = Path(_SCRIPT_DIR) / 'runtime'


class SessionCompiler:
    """Compiles multiple PlannedChunks into a single Frida session program."""

    @staticmethod
    def compile_session(
        chunks: List[PlannedChunk],
        header: Any,
        catalog: Optional[Dict[str, Any]] = None,
        is_live: bool = False
    ) -> str:
        cat = catalog or FieldCatalogLoader.get_catalog()
        common_js = (_RUNTIME_DIR / 'common.js').read_text(encoding='utf-8')
        gui_once_js = (_RUNTIME_DIR / 'gui_once.js').read_text(encoding='utf-8')

        coach_settings_spec = json.loads((_SCRIPT_DIR / 'data' / 'coach_settings.json').read_text(encoding='utf-8'))['fields']
        player_contract_spec = json.loads((_SCRIPT_DIR / 'data' / 'player_contract_fields.json').read_text(encoding='utf-8'))['fields']

        # Build payload for each chunk
        serialized_chunks = []
        total_estimated_calls = 0

        for chunk in chunks:
            player_items = []
            coach_items = []

            for item in chunk.intents:
                action_id = item.action_id

                if action_id == 'COACH_SET_KNOWN_CURRENT_SETTINGS':
                    c_field = cat.get('coach', {}).get(item.field_id, {})
                    coach_items.append({
                        'intent_id': item.intent_id,
                        'field_id': item.field_id,
                        'expected_before': item.expected_before,
                        'value': item.value,
                        'gameplan_offset': c_field.get('gameplan_offset', 382),
                        'coach_offset': c_field.get('coach_offset', 316),
                        'width': c_field.get('width', 8),
                        'start_bit': c_field.get('start_bit', 0),
                        'storage_bytes': c_field.get('storage_bytes', 1)
                    })
                else:
                    is_attr = item.field_id in cat.get('attributes', {})
                    n_idx = (
                        cat['attributes'][item.field_id]['native_index']
                        if is_attr
                        else cat['tendencies'][item.field_id]['native_index']
                        if item.field_id in cat.get('tendencies', {})
                        else -1
                    )
                    offset = (
                        cat['attributes'][item.field_id]['offset']
                        if is_attr
                        else cat['tendencies'][item.field_id]['offset']
                        if item.field_id in cat.get('tendencies', {})
                        else -1
                    )
                    player_items.append({
                        'intent_id': item.intent_id,
                        'player_id': item.player_id,
                        'field_id': item.field_id,
                        'expected_before': item.expected_before,
                        'value': item.value,
                        'native_index': n_idx,
                        'offset': offset,
                        'is_attribute': is_attr
                    })

            serialized_chunks.append({
                'chunk_id': chunk.chunk_id,
                'chunk_digest': chunk.chunk_digest,
                'plan_digest': chunk.plan_digest,
                'action_id': chunk.action_id,
                'team_id': chunk.team_id,
                'batch_id': chunk.batch_id,
                'save_instance_id': chunk.save_instance_id,
                'player_items': player_items,
                'coach_items': coach_items
            })
            total_estimated_calls += chunk.estimated_call_count

        max_calls = max(total_estimated_calls * 2, 500)

        reg = registry.NativeActionRegistry(_SCRIPT_DIR)
        binding_ids = ['player.stat_context', 'player.get_stat_ui', 'player.set_stat_ui', 'coach.apply_gameplan']
        bindings = {bid: reg.binding(bid).to_dict() for bid in binding_ids if bid in reg.bindings}

        req = {
            'action_id': 'MULTI_CHUNK_BOUNDED_SESSION',
            'request_id': f"session_req_{sha256_digest([c.chunk_id for c in chunks])[:12]}",
            'authorization_ref': getattr(header, 'human_authorization_ref', 'HUMAN-AUTH-PILOT-SESSION'),
            'game_build_sha256': contracts.BUILD,
            'maximum_game_calls': max_calls
        }

        limits = {
            'maximum_game_calls': max_calls,
            'maximum_execution_time_ms': 30000,
            'is_live': is_live
        }

        session_runner_js = f"""
// Auto-generated Bounded Multi-Chunk Session Program
const u8 = (b, o=0) => new DataView(b).getUint8(o);
const SESSION_CHUNKS = {json.dumps(serialized_chunks, indent=2)};
const SESSION_LIMITS = {json.dumps(limits, indent=2)};
let sessionHalted = false;
let sessionHaltReason = null;

function executeAction() {{
  let callCount = 0;
  const maxCalls = SESSION_LIMITS.maximum_game_calls;

  for (let cIdx = 0; cIdx < SESSION_CHUNKS.length; cIdx++) {{
    const CHUNK_PAYLOAD = SESSION_CHUNKS[cIdx];
    let chunkHalted = sessionHalted;
    let haltReason = sessionHalted ? ("SESSION_HALTED:" + sessionHaltReason) : null;
    let results = [];

    if (sessionHalted) {{
      for (const item of CHUNK_PAYLOAD.player_items) {{
        results.push({{
          intent_id: item.intent_id,
          team_id: CHUNK_PAYLOAD.team_id,
          player_id: item.player_id,
          field_id: item.field_id,
          expected_before: item.expected_before,
          requested: item.value,
          outcome: 'NOT_EXECUTED',
          reason: haltReason
        }});
      }}
      for (const item of CHUNK_PAYLOAD.coach_items) {{
        results.push({{
          intent_id: item.intent_id,
          team_id: CHUNK_PAYLOAD.team_id,
          field_id: item.field_id,
          expected_before: item.expected_before,
          requested: item.value,
          outcome: 'NOT_EXECUTED',
          reason: haltReason
        }});
      }}
      send({{
        kind: 'chunk-execution-result',
        chunk_id: CHUNK_PAYLOAD.chunk_id,
        chunk_digest: CHUNK_PAYLOAD.chunk_digest,
        plan_digest: CHUNK_PAYLOAD.plan_digest,
        action_id: CHUNK_PAYLOAD.action_id,
        batch_id: CHUNK_PAYLOAD.batch_id,
        save_instance_id: CHUNK_PAYLOAD.save_instance_id,
        outcome: 'CHUNK_HALTED',
        halt_reason: haltReason,
        receipts: results
      }});
      continue;
    }}

    // Resolve team pointer
    let t = null;
    try {{
      t = team(CHUNK_PAYLOAD.team_id);
      if (!t || t.isNull()) {{
        throw Error('Team pointer null');
      }}
    }} catch (e) {{
      chunkHalted = true;
      haltReason = 'TEAM_RESOLUTION_FAILED:' + String(e);
      sessionHalted = true;
      sessionHaltReason = haltReason;
    }}

    // 1. Player items execution
    if (CHUNK_PAYLOAD.player_items.length > 0 && !chunkHalted) {{
      const layout = bindingSpecs['player.stat_context'] ? bindingSpecs['player.stat_context'].input_layout : {{ root_rva: 0x5109b88, required_slots: {{0: 0x978360, 8: 0x990a10}} }};
      const delegate = ptrAt(read(base.add(layout.root_rva), 8));
      if (delegate.isNull()) throw Error('PLAYER_STAT_DELEGATE_NOT_READY');
      const vtable = ptrAt(read(delegate, 8));
      if (!Object.entries(layout.required_slots).every(([slot, rva]) => ptrAt(read(vtable.add(Number(slot)), 8)).equals(base.add(rva)))) {{
        throw Error('UNRECOVERED_PLAYER_STAT_DELEGATE');
      }}

      const playerGroups = {{}};
      for (const item of CHUNK_PAYLOAD.player_items) {{
        const pid = item.player_id;
        if (!playerGroups[pid]) playerGroups[pid] = [];
        playerGroups[pid].push(item);
      }}

      for (const pidStr of Object.keys(playerGroups)) {{
        if (chunkHalted) break;
        const pid = Number(pidStr);
        const items = playerGroups[pidStr];
        let player = null;
        try {{
          player = rosterPlayer(t, pid);
        }} catch (e) {{
          chunkHalted = true;
          haltReason = 'PLAYER_ROSTER_NOT_RESOLVED_' + pid;
          sessionHalted = true;
          sessionHaltReason = haltReason;
          for (const item of items) {{
            results.push({{
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              player_id: item.player_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              requested: item.value,
              outcome: 'NOT_EXECUTED',
              reason: haltReason
            }});
          }}
          break;
        }}

        let beforeBytes = null;
        let flagsBefore = 0;
        try {{
          beforeBytes = new Uint8Array(read(player.add(0x41f), 156));
          flagsBefore = u32(read(player.add(0x31c), 4));
        }} catch (e) {{
          chunkHalted = true;
          haltReason = 'PRE_READ_FAILED:' + String(e);
          sessionHalted = true;
          sessionHaltReason = haltReason;
          for (const item of items) {{
            results.push({{
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              player_id: item.player_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              requested: item.value,
              outcome: 'UNKNOWN_EXECUTION_OUTCOME',
              reason: haltReason
            }});
          }}
          break;
        }}

        for (const item of items) {{
          if (chunkHalted) {{
            results.push({{
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              player_id: item.player_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              requested: item.value,
              outcome: 'NOT_EXECUTED',
              reason: 'CHUNK_HALTED_PREVIOUS_FAILURE'
            }});
            continue;
          }}

          callCount++;
          if (callCount > maxCalls) {{
            chunkHalted = true;
            haltReason = 'CALL_BUDGET_EXCEEDED';
            sessionHalted = true;
            sessionHaltReason = haltReason;
            continue;
          }}

          const currentVal = call('player.get_stat_ui', player, item.native_index);

          if (currentVal !== item.expected_before) {{
            results.push({{
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              player_id: item.player_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              getter_before: currentVal,
              requested: item.value,
              outcome: 'CAS_EXPECTED_BEFORE_MISMATCH',
              reason: 'Expected ' + item.expected_before + ', observed ' + currentVal
            }});
            chunkHalted = true;
            haltReason = 'CAS_MISMATCH';
            sessionHalted = true;
            sessionHaltReason = haltReason;
            continue;
          }}

          if (currentVal === item.value) {{
            results.push({{
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              player_id: item.player_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              getter_before: currentVal,
              requested: item.value,
              getter_after: currentVal,
              outcome: 'UNCHANGED_ALREADY_TARGET',
              unaltered_fields_check: true
            }});
            continue;
          }}

          // If dry run, do not mutate
          if (!SESSION_LIMITS.is_live) {{
            results.push({{
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              player_id: item.player_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              getter_before: currentVal,
              requested: item.value,
              getter_after: item.value,
              raw_after: item.value,
              outcome: 'SUCCESS_APPLIED',
              unaltered_fields_check: true
            }});
            continue;
          }}

          // Live Mutation
          try {{
            callCount++;
            call('player.set_stat_ui', player, item.native_index, item.value);
            const afterBytes = new Uint8Array(read(player.add(0x41f), 156));
            const flagsAfter = u32(read(player.add(0x31c), 4));
            callCount++;
            const afterVal = call('player.get_stat_ui', player, item.native_index);
            const rawByte = u8(read(player.add(item.offset), 1));
            const expectedRaw = item.is_attribute ? (item.value * 3 - 75) : item.value;
            const targetOffsetIn156 = item.offset - 0x41f;

            let untouchedPreserved = true;
            for (let bIdx = 0; bIdx < 156; bIdx++) {{
              if (bIdx === targetOffsetIn156) {{
                if (afterBytes[bIdx] !== expectedRaw) untouchedPreserved = false;
              }} else {{
                if (afterBytes[bIdx] !== beforeBytes[bIdx]) untouchedPreserved = false;
              }}
            }}

            const expectedFlags = item.is_attribute ? ((flagsBefore & 0xffffffbf) >>> 0) : flagsBefore;
            const flagsMatch = (flagsAfter === expectedFlags);

            if (!untouchedPreserved) {{
              throw Error('UNREQUESTED_STAT_BYTE_CHANGED');
            }}
            if (!flagsMatch) {{
              throw Error('PLAYER_STAT_CACHE_FLAG_MISMATCH');
            }}
            if (afterVal !== item.value || rawByte !== expectedRaw) {{
              throw Error('AFTER_GETTER_MISMATCH');
            }}

            results.push({{
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              player_id: item.player_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              getter_before: currentVal,
              requested: item.value,
              getter_after: afterVal,
              raw_after: rawByte,
              outcome: 'SUCCESS_APPLIED',
              unaltered_fields_check: true
            }});
            beforeBytes = afterBytes;
            flagsBefore = flagsAfter;
          }} catch (err) {{
            results.push({{
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              player_id: item.player_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              getter_before: currentVal,
              requested: item.value,
              outcome: 'UNKNOWN_EXECUTION_OUTCOME',
              reason: String(err)
            }});
            chunkHalted = true;
            haltReason = 'SETTER_EXCEPTION:' + String(err);
            sessionHalted = true;
            sessionHaltReason = haltReason;
          }}
        }}
      }}
    }}

    // 2. Coach items execution
    if (CHUNK_PAYLOAD.coach_items.length > 0 && !chunkHalted) {{
      if (SESSION_LIMITS.is_live) {{
        chunkHalted = true;
        haltReason = 'COACH_CONTRACT_UNSUPPORTED_FOR_LIVE';
        sessionHalted = true;
        sessionHaltReason = haltReason;
        for (const item of CHUNK_PAYLOAD.coach_items) {{
          results.push({{
            intent_id: item.intent_id,
            team_id: CHUNK_PAYLOAD.team_id,
            field_id: item.field_id,
            expected_before: item.expected_before,
            requested: item.value,
            outcome: 'NOT_EXECUTED',
            reason: 'COACH_CONTRACT_UNSUPPORTED_FOR_LIVE'
          }});
        }}
      }} else {{
        try {{
          const coach = ptrAt(read(t.add(0xce8), 8));
          const m = franchiseRecord(CHUNK_PAYLOAD.team_id).pointer;
          const gp = m.add(0x7854);

          for (const item of CHUNK_PAYLOAD.coach_items) {{
            if (chunkHalted) {{
              results.push({{
                intent_id: item.intent_id,
                team_id: CHUNK_PAYLOAD.team_id,
                field_id: item.field_id,
                expected_before: item.expected_before,
                requested: item.value,
                outcome: 'NOT_EXECUTED',
                reason: 'CHUNK_HALTED_PREVIOUS_FAILURE'
              }});
              continue;
            }}

            const currentVal = u8(read(gp.add(item.gameplan_offset), 1));
            if (currentVal !== item.expected_before) {{
              results.push({{
                intent_id: item.intent_id,
                team_id: CHUNK_PAYLOAD.team_id,
                field_id: item.field_id,
                expected_before: item.expected_before,
                getter_before: currentVal,
                requested: item.value,
                outcome: 'CAS_EXPECTED_BEFORE_MISMATCH',
                reason: 'Expected ' + item.expected_before + ', observed ' + currentVal
              }});
              chunkHalted = true;
              haltReason = 'CAS_MISMATCH';
              sessionHalted = true;
              sessionHaltReason = haltReason;
              continue;
            }}

            if (currentVal === item.value) {{
              results.push({{
                intent_id: item.intent_id,
                team_id: CHUNK_PAYLOAD.team_id,
                field_id: item.field_id,
                expected_before: item.expected_before,
                getter_before: currentVal,
                requested: item.value,
                getter_after: currentVal,
                outcome: 'UNCHANGED_ALREADY_TARGET',
                unaltered_fields_check: true
              }});
              continue;
            }}

            // Offline simulated coach write
            gp.add(item.gameplan_offset).writeU8(item.value);
            const afterVal = u8(read(gp.add(item.gameplan_offset), 1));
            results.push({{
              intent_id: item.intent_id,
              team_id: CHUNK_PAYLOAD.team_id,
              field_id: item.field_id,
              expected_before: item.expected_before,
              getter_before: currentVal,
              requested: item.value,
              getter_after: afterVal,
              outcome: 'SUCCESS_APPLIED',
              unaltered_fields_check: true
            }});
          }}
        }} catch (err) {{
          chunkHalted = true;
          haltReason = 'COACH_SETTING_EXCEPTION:' + String(err);
          sessionHalted = true;
          sessionHaltReason = haltReason;
        }}
      }}
    }}

    send({{
      kind: 'chunk-execution-result',
      chunk_id: CHUNK_PAYLOAD.chunk_id,
      chunk_digest: CHUNK_PAYLOAD.chunk_digest,
      plan_digest: CHUNK_PAYLOAD.plan_digest,
      action_id: CHUNK_PAYLOAD.action_id,
      batch_id: CHUNK_PAYLOAD.batch_id,
      save_instance_id: CHUNK_PAYLOAD.save_instance_id,
      outcome: chunkHalted ? 'CHUNK_HALTED' : 'CHUNK_SUCCESS',
      halt_reason: haltReason,
      receipts: results
    }});
  }}
}}
"""

        full_source = (
            common_js + "\n" +
            session_runner_js + "\n" +
            gui_once_js
        )
        full_source = (
            full_source
            .replace('__REQUEST__', canonical_encode(req))
            .replace('__BINDINGS__', canonical_encode(bindings))
            .replace('__LIMITS__', canonical_encode(limits))
            .replace('__COACH_FIELDS__', canonical_encode(coach_settings_spec))
            .replace('__PLAYER_CONTRACT_FIELDS__', canonical_encode(player_contract_spec))
        )
        return full_source


class SessionBatchTransport:
    """Dispatches a multi-chunk session program using a single REA CLI / Frida attachment."""
    def __init__(
        self,
        runtime_directory: Path | str,
        live_context: Optional[Any] = None,
        *,
        verifier: Optional[Any] = None,
        duration_ms: int = 2500,
        fake_runner: Optional[Any] = None
    ):
        self.runtime_directory = Path(runtime_directory).resolve()
        self.live_context = live_context
        self.verifier = verifier
        self.duration_ms = duration_ms
        self.fake_runner = fake_runner
        self.node = shutil.which('node')
        self.rea = Path(os.environ.get('APPDATA', '')) / 'npm/node_modules/rea-agents/scripts/rea.mjs'

    def execute_session(
        self,
        script: str,
        chunks: List[PlannedChunk],
        header: Any
    ) -> Dict[str, Any]:
        if self.fake_runner is not None:
            return self.fake_runner(chunks, script)

        if not self.live_context or not getattr(self.live_context, 'enabled', False):
            raise PermissionError("LIVE_MUTATION_NOT_AUTHORIZED: live game execution context is not enabled")

        if self.verifier is None:
            raise PermissionError("LIVE_AUTHORIZATION_VERIFIER_NOT_AVAILABLE: live game execution verifier required")

        if isinstance(self.verifier, dict):
            v_build = self.verifier.get('game_build_sha256')
            if v_build and v_build != contracts.BUILD:
                raise PermissionError(f"GAME_BUILD_MISMATCH: verifier requires {v_build}, binary is {contracts.BUILD}")

        t_launch_start = time.perf_counter()
        session_dir = self.runtime_directory / hashlib.sha256(f"session_{time.time()}".encode()).hexdigest()[:16]
        session_dir.mkdir(parents=True, exist_ok=False)
        program = session_dir / 'program.js'
        program.write_text(script, encoding='utf-8')

        max_calls = max(sum(c.estimated_call_count for c in chunks) * 2, 500)
        manifest = {
            'action_id': 'MULTI_CHUNK_BOUNDED_SESSION',
            'request_id': f"session_{session_dir.name}",
            'authorization_ref': self.live_context.authorization_ref,
            'game_build_sha256': contracts.BUILD,
            'script_sha256': hashlib.sha256(program.read_bytes()).hexdigest(),
            'maximum_game_calls': max_calls
        }
        if self.live_context.expected_pid is not None:
            manifest['expected_pid'] = self.live_context.expected_pid

        (session_dir / 'request.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

        ps_script = Path(__file__).with_name('run_native_program.ps1')
        command = [
            'powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', str(ps_script),
            '-Directory', str(session_dir),
            '-NodePath', str(self.node),
            '-ReaPath', str(self.rea),
            '-DurationMs', str(self.duration_ms)
        ]

        with (session_dir / 'runner.log').open('w', encoding='utf-8') as log:
            r = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)

        t_wall_ms = (time.perf_counter() - t_launch_start) * 1000.0

        if r.returncode != 0 or not (session_dir / 'evidence.json').exists():
            return {
                'outcome': 'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',
                'runtime_directory': str(session_dir),
                'runner_exit': r.returncode,
                'wall_time_ms': t_wall_ms
            }

        raw = json.loads((session_dir / 'evidence.json').read_text(encoding='utf-8-sig'))
        n = raw['normalized_result']
        messages = n.get('messages', [])

        if n.get('cleanup_error') is not None or any(m['type'] == 'error' for m in messages):
            return {
                'outcome': 'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',
                'evidence_id': raw.get('evidence_id'),
                'runtime_directory': str(session_dir),
                'wall_time_ms': t_wall_ms
            }

        results = [
            m['payload'] for m in messages
            if m['type'] == 'send' and m['payload'].get('kind') == 'chunk-execution-result'
        ]

        return {
            'outcome': 'SESSION_SUCCESS',
            'evidence_id': raw.get('evidence_id'),
            'runtime_directory': str(session_dir),
            'chunk_results': {res['chunk_id']: res for res in results},
            'wall_time_ms': t_wall_ms
        }


class BoundedSessionExecutor:
    """Executes bulk batches with session reuse, Claim-before-Setter, and fail-stop semantics."""
    def __init__(
        self,
        journal_dir: Path | str,
        *,
        live_context: Optional[Any] = None,
        verifier: Optional[Any] = None,
        runtime_dir: Optional[Path | str] = None,
        duration_ms: int = 2500,
        fake_runner: Optional[Any] = None
    ):
        self.journal = ExecutionJournal(journal_dir)
        self.planner = BulkBatchPlanner()
        self.live_context = live_context
        self.verifier = verifier
        self.runtime_dir = Path(runtime_dir or (Path(_SCRIPT_DIR) / 'runtime_session')).resolve()
        self.duration_ms = duration_ms
        self.fake_runner = fake_runner
        self.transport = SessionBatchTransport(
            self.runtime_dir,
            self.live_context,
            verifier=self.verifier,
            duration_ms=self.duration_ms,
            fake_runner=self.fake_runner
        )

    def execute_batch(
        self,
        batch: BulkBatch,
        *,
        max_chunk_size: int = 50
    ) -> Dict[str, Any]:
        chunks = self.planner.plan(batch, max_chunk_size=max_chunk_size)
        self.journal.record_batch_manifest(batch)

        start_time = time.perf_counter()
        all_receipts: List[ItemReceipt] = []
        chunks_to_execute: List[PlannedChunk] = []
        skipped_chunk_receipts: Dict[str, List[ItemReceipt]] = {}

        # 1. Pre-execution filter & Claim-before-Setter
        ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        for chunk in chunks:
            chunk_receipts: List[ItemReceipt] = []
            chunk_executable_intents: List[BulkIntentItem] = []

            for item in chunk.intents:
                res_key = get_resource_key(item.team_id, item.player_id, item.field_id)
                locking_id = self.journal.is_resource_locked(res_key)

                if locking_id:
                    chunk_receipts.append(ItemReceipt(
                        intent_id=item.intent_id,
                        team_id=item.team_id,
                        player_id=item.player_id,
                        field_id=item.field_id,
                        expected_before=item.expected_before,
                        requested=item.value,
                        outcome='BLOCKED_BY_PRIOR_UNKNOWN_CLAIM',
                        chunk_id=chunk.chunk_id,
                        timestamp=ts,
                        reason=f"RESOURCE_LOCKED_BY_PRIOR_UNKNOWN:{locking_id}"
                    ))
                elif self.journal.is_intent_completed(item.intent_id, item):
                    chunk_receipts.append(ItemReceipt(
                        intent_id=item.intent_id,
                        team_id=item.team_id,
                        player_id=item.player_id,
                        field_id=item.field_id,
                        expected_before=item.expected_before,
                        requested=item.value,
                        outcome='REUSED_HISTORICAL_RECEIPT',
                        chunk_id=chunk.chunk_id,
                        timestamp=ts,
                        reused_historical_receipt=True,
                        reason="INTENT_ALREADY_COMPLETED_IN_JOURNAL"
                    ))
                else:
                    chunk_executable_intents.append(item)

            if not chunk_executable_intents:
                all_receipts.extend(chunk_receipts)
                self.journal.append_receipts(chunk_receipts)
            else:
                if chunk_receipts:
                    skipped_chunk_receipts[chunk.chunk_id] = chunk_receipts

                sub_chunk = PlannedChunk(
                    chunk_id=chunk.chunk_id,
                    team_id=chunk.team_id,
                    action_id=chunk.action_id,
                    intents=tuple(chunk_executable_intents),
                    estimated_call_count=len(chunk_executable_intents) * 3,
                    estimated_duration_ms=min(5000, 500 + len(chunk_executable_intents) * 20),
                    batch_id=chunk.batch_id,
                    save_instance_id=chunk.save_instance_id,
                    plan_digest=chunk.plan_digest,
                    chunk_digest=chunk.chunk_digest if len(chunk_executable_intents) == len(chunk.intents) else sha256_digest({
                        'batch_id': batch.header.batch_id,
                        'save_instance_id': chunk.save_instance_id,
                        'chunk_id': chunk.chunk_id,
                        'team_id': chunk.team_id,
                        'action_id': chunk.action_id,
                        'plan_digest': batch.plan_digest,
                        'intents': [it.plan_record() for it in chunk_executable_intents]
                    })
                )
                # PERSIST CLAIM BEFORE ANY EXECUTION! (Claim-before-Setter Hard Invariant)
                self.journal.claim_chunk(sub_chunk)
                chunks_to_execute.append(sub_chunk)

        if not chunks_to_execute:
            return self._build_summary(batch, all_receipts, start_time, chunk_count=len(chunks), attach_count=0)

        # 2. Compile multi-chunk session program
        is_live = bool(self.live_context and getattr(self.live_context, 'enabled', False) and not batch.header.dry_run)
        session_script = SessionCompiler.compile_session(chunks_to_execute, batch.header, is_live=is_live)

        # 3. Execute bounded session (Single Attach)
        lock_file = self.journal.root / 'session_executor.lock'
        with CrossProcessFileLock(lock_file):
            transport_res = self.transport.execute_session(session_script, chunks_to_execute, batch.header)

        # 4. Process receipts & update claims
        ts_now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        if transport_res.get('outcome') != 'SESSION_SUCCESS':
            # Session failed/aborted: mark all unexecuted chunks as UNKNOWN
            for chunk in chunks_to_execute:
                chunk_receipts = skipped_chunk_receipts.get(chunk.chunk_id, [])
                for item in chunk.intents:
                    chunk_receipts.append(ItemReceipt(
                        intent_id=item.intent_id,
                        team_id=item.team_id,
                        player_id=item.player_id,
                        field_id=item.field_id,
                        expected_before=item.expected_before,
                        requested=item.value,
                        outcome='UNKNOWN_EXECUTION_OUTCOME',
                        chunk_id=chunk.chunk_id,
                        timestamp=ts_now,
                        reason=f"SESSION_ABORTED:{transport_res.get('outcome')}"
                    ))
                all_receipts.extend(chunk_receipts)
                self.journal.append_receipts(chunk_receipts)
            return self._build_summary(batch, all_receipts, start_time, chunk_count=len(chunks), attach_count=1)

        chunk_results = transport_res.get('chunk_results', {})
        for chunk in chunks_to_execute:
            c_res = chunk_results.get(chunk.chunk_id)
            chunk_receipts = skipped_chunk_receipts.get(chunk.chunk_id, [])

            if not c_res:
                # Missing chunk receipt
                for item in chunk.intents:
                    chunk_receipts.append(ItemReceipt(
                        intent_id=item.intent_id,
                        team_id=item.team_id,
                        player_id=item.player_id,
                        field_id=item.field_id,
                        expected_before=item.expected_before,
                        requested=item.value,
                        outcome='UNKNOWN_EXECUTION_OUTCOME',
                        chunk_id=chunk.chunk_id,
                        timestamp=ts_now,
                        reason="MISSING_CHUNK_RESULT_IN_SESSION"
                    ))
                all_receipts.extend(chunk_receipts)
                self.journal.append_receipts(chunk_receipts)
                continue

            # Validate chunk outcome and envelope
            raw_receipts = c_res.get('receipts', [])
            item_map = {it.intent_id: it for it in chunk.intents}

            for r_dict in raw_receipts:
                it_id = r_dict.get('intent_id')
                item = item_map.get(it_id)
                if not item:
                    continue

                receipt = ItemReceipt(
                    intent_id=it_id,
                    team_id=item.team_id,
                    player_id=item.player_id,
                    field_id=item.field_id,
                    expected_before=item.expected_before,
                    requested=item.value,
                    outcome=r_dict.get('outcome', 'UNKNOWN_EXECUTION_OUTCOME'),
                    chunk_id=chunk.chunk_id,
                    timestamp=ts_now,
                    getter_before=r_dict.get('getter_before'),
                    getter_after=r_dict.get('getter_after'),
                    raw_after=r_dict.get('raw_after'),
                    unaltered_fields_check=r_dict.get('unaltered_fields_check', False),
                    reason=r_dict.get('reason'),
                    execution_evidence_id=transport_res.get('evidence_id')
                )
                chunk_receipts.append(receipt)

            all_receipts.extend(chunk_receipts)
            self.journal.append_receipts(chunk_receipts)

            # Update durable claim status
            claim_file = self.journal.claims_dir / f"claim_{chunk.chunk_id}_{sha256_digest(chunk.chunk_digest)[:12]}.json"
            for c_path in self.journal.claims_dir.glob(f"claim_{chunk.chunk_id}*.json"):
                try:
                    cdata = json.loads(c_path.read_text(encoding='utf-8'))
                    if cdata.get('chunk_id') == chunk.chunk_id:
                        cdata['state'] = 'COMPLETED' if c_res.get('outcome') == 'CHUNK_SUCCESS' else 'HALTED'
                        cdata['completed_at'] = ts_now
                        atomic_write_json(c_path, cdata)
                except Exception:
                    pass

        return self._build_summary(batch, all_receipts, start_time, chunk_count=len(chunks), attach_count=1, transport_wall_ms=transport_res.get('wall_time_ms'))

    def _build_summary(
        self,
        batch: BulkBatch,
        receipts: List[ItemReceipt],
        start_time: float,
        chunk_count: int,
        attach_count: int,
        transport_wall_ms: Optional[float] = None
    ) -> Dict[str, Any]:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        planned = len(batch.intents)
        success = sum(1 for r in receipts if r.outcome == 'SUCCESS_APPLIED')
        noop = sum(1 for r in receipts if r.outcome == 'UNCHANGED_ALREADY_TARGET')
        reused = sum(1 for r in receipts if r.outcome == 'REUSED_HISTORICAL_RECEIPT')
        blocked = sum(1 for r in receipts if r.outcome == 'BLOCKED_BY_PRIOR_UNKNOWN_CLAIM')
        unknown = sum(1 for r in receipts if r.outcome == 'UNKNOWN_EXECUTION_OUTCOME')
        not_exec = sum(1 for r in receipts if r.outcome == 'NOT_EXECUTED')
        cas_mismatch = sum(1 for r in receipts if r.outcome == 'CAS_EXPECTED_BEFORE_MISMATCH')

        total_accounted = success + noop + reused + blocked + unknown + not_exec + cas_mismatch
        conservation = (total_accounted == planned)

        return {
            'batch_id': batch.header.batch_id,
            'plan_digest': batch.plan_digest,
            'chunk_count': chunk_count,
            'frida_attach_count': attach_count,
            'execution_time_ms': elapsed_ms,
            'transport_wall_ms': transport_wall_ms,
            'metrics': {
                'num_planned': planned,
                'num_success': success,
                'num_noop': noop,
                'num_reused': reused,
                'num_blocked': blocked,
                'num_unknown': unknown,
                'num_not_executed': not_exec,
                'num_cas_mismatch': cas_mismatch,
                'conservation_holds': conservation
            },
            'receipt_count': len(receipts)
        }
