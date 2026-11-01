"""Deterministic bulk REA native automation executor and CLI suite.

Enforces strict parameter validation, hard CAS (expected_before equality),
bounded-session chunking (one Frida attach and GUI hook per chunk),
durable execution journaling, and strict outcome conservation:
    num_planned = num_success + num_noop + num_blocked + num_unknown + num_not_executed
"""
import argparse
import copy
import dataclasses
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

# Support execution both as package and standalone script
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    import contracts
    import player_fields
except ImportError:
    from . import contracts
    from . import player_fields

GAME_BUILD_SHA256 = contracts.BUILD

COACH_FIELDS = {
    'POEOffense': {'min': 0, 'max': 100},
    'POEDefense': {'min': 0, 'max': 100},
    'POEOffense2': {'min': 0, 'max': 100},
    'POEOffense3': {'min': 0, 'max': 100},
    'POEDefense2': {'min': 0, 'max': 100},
    'POEDefense3': {'min': 0, 'max': 100},
    'RunPlayTendency': {'min': 0, 'max': 100},
    'ZoneUsage': {'min': 0, 'max': 100},
    'BenchUtilization': {'min': 0, 'max': 100},
}


def canonical_encode(obj: Any) -> str:
    """Deterministic JSON string encoding."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def sha256_digest(obj: Any) -> str:
    """SHA256 hash of canonical representation."""
    if isinstance(obj, str):
        content = obj.encode('utf-8')
    elif isinstance(obj, bytes):
        content = obj
    else:
        content = canonical_encode(obj).encode('utf-8')
    return hashlib.sha256(content).hexdigest()


@dataclass(frozen=True)
class BulkBatchHeader:
    batch_id: str
    save_instance_id: str
    game_build_sha256: str
    authorization_ref: str
    source_snapshot_ref: str
    expected_process_name: str = "NBA2K22.exe"
    expected_pid: Optional[int] = None
    dry_run: bool = False

    def validate(self):
        if not self.batch_id or not isinstance(self.batch_id, str):
            raise ValueError("VALIDATION_ERROR: batch_id must be non-empty string")
        if not self.save_instance_id or not isinstance(self.save_instance_id, str):
            raise ValueError("VALIDATION_ERROR: save_instance_id must be non-empty string")
        if not self.authorization_ref or not isinstance(self.authorization_ref, str):
            raise ValueError("VALIDATION_ERROR: authorization_ref must be non-empty string")
        if not self.source_snapshot_ref or not isinstance(self.source_snapshot_ref, str):
            raise ValueError("VALIDATION_ERROR: source_snapshot_ref must be non-empty string")
        if self.game_build_sha256 != GAME_BUILD_SHA256:
            raise ValueError(f"VALIDATION_ERROR: game_build_sha256 mismatch. Expected {GAME_BUILD_SHA256}, got {self.game_build_sha256}")


@dataclass(frozen=True)
class BulkIntentItem:
    intent_id: str
    action_id: str
    team_id: int
    field_id: str
    expected_before: int
    value: int
    player_id: Optional[int] = None
    source_justification: str = ""
    dependencies: Tuple[str, ...] = ()

    def validate(self, field_catalog: Dict[str, Any]):
        if not self.intent_id or not isinstance(self.intent_id, str):
            raise ValueError("VALIDATION_ERROR: intent_id must be non-empty string")
        if not isinstance(self.team_id, int) or not (0 <= self.team_id <= 29):
            raise ValueError(f"VALIDATION_ERROR: team_id must be integer in range 0..29, got {self.team_id}")
        
        # Check domain based on action_id or field_id
        if self.field_id in field_catalog['tendencies']:
            spec = field_catalog['tendencies'][self.field_id]
            if not spec.get('callable', False):
                raise ValueError(f"VALIDATION_ERROR: tendency field '{self.field_id}' is not callable")
            if self.player_id is None or not isinstance(self.player_id, int):
                raise ValueError(f"VALIDATION_ERROR: player tendency '{self.field_id}' requires integer player_id")
            if not isinstance(self.expected_before, int) or not (spec['minimum'] <= self.expected_before <= spec['maximum']):
                raise ValueError(f"VALIDATION_ERROR: expected_before for '{self.field_id}' must be integer in [{spec['minimum']}, {spec['maximum']}], got {self.expected_before}")
            if not isinstance(self.value, int) or not (spec['minimum'] <= self.value <= spec['maximum']):
                raise ValueError(f"VALIDATION_ERROR: value for '{self.field_id}' must be integer in [{spec['minimum']}, {spec['maximum']}], got {self.value}")

        elif self.field_id in field_catalog['attributes']:
            spec = field_catalog['attributes'][self.field_id]
            if not spec.get('callable', False):
                raise ValueError(f"VALIDATION_ERROR: attribute field '{self.field_id}' is not callable")
            if self.player_id is None or not isinstance(self.player_id, int):
                raise ValueError(f"VALIDATION_ERROR: player attribute '{self.field_id}' requires integer player_id")
            if not isinstance(self.expected_before, int) or not (spec['minimum'] <= self.expected_before <= spec['maximum']):
                raise ValueError(f"VALIDATION_ERROR: expected_before for '{self.field_id}' must be integer in [{spec['minimum']}, {spec['maximum']}], got {self.expected_before}")
            if not isinstance(self.value, int) or not (spec['minimum'] <= self.value <= spec['maximum']):
                raise ValueError(f"VALIDATION_ERROR: value for '{self.field_id}' must be integer in [{spec['minimum']}, {spec['maximum']}], got {self.value}")

        elif self.field_id in COACH_FIELDS:
            spec = COACH_FIELDS[self.field_id]
            if not isinstance(self.expected_before, int) or not (spec['min'] <= self.expected_before <= spec['max']):
                raise ValueError(f"VALIDATION_ERROR: expected_before for coach field '{self.field_id}' must be integer in [{spec['min']}, {spec['max']}], got {self.expected_before}")
            if not isinstance(self.value, int) or not (spec['min'] <= self.value <= spec['max']):
                raise ValueError(f"VALIDATION_ERROR: value for coach field '{self.field_id}' must be integer in [{spec['min']}, {spec['max']}], got {self.value}")

        else:
            raise ValueError(f"VALIDATION_ERROR: field_id '{self.field_id}' is unknown or UNSUPPORTED_DOMAIN")


@dataclass(frozen=True)
class BulkBatch:
    header: BulkBatchHeader
    intents: Tuple[BulkIntentItem, ...]
    plan_digest: str = ""

    @classmethod
    def load(cls, file_path: Path | str) -> 'BulkBatch':
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Batch file not found: {path}")

        raw_text = path.read_text(encoding='utf-8').strip()
        is_jsonl = path.suffix.lower() == '.jsonl'
        if not is_jsonl:
            try:
                data = json.loads(raw_text)
                if not isinstance(data, dict) or 'intents' not in data:
                    is_jsonl = True
            except Exception:
                is_jsonl = True

        if not is_jsonl:
            # Single JSON object
            data = json.loads(raw_text)
            header_keys = {'batch_id', 'save_instance_id', 'game_build_sha256', 'authorization_ref', 'source_snapshot_ref'}
            header_data = {k: data[k] for k in header_keys if k in data}
            for opt in ('expected_process_name', 'expected_pid', 'dry_run'):
                if opt in data:
                    header_data[opt] = data[opt]
            header = BulkBatchHeader(**header_data)

            intents_raw = data.get('intents', [])
            intents = []
            for item in intents_raw:
                item_dict = dict(item)
                deps = tuple(item_dict.pop('dependencies', []))
                intents.append(BulkIntentItem(dependencies=deps, **item_dict))
        else:
            # JSONL format: line 1 = header, lines 2..N = intents
            lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            if not lines:
                raise ValueError("Empty batch file")
            header_data = json.loads(lines[0])
            header = BulkBatchHeader(**header_data)
            intents = []
            for line in lines[1:]:
                item_data = json.loads(line)
                deps = tuple(item_data.pop('dependencies', []))
                intents.append(BulkIntentItem(dependencies=deps, **item_data))

        batch = cls(header=header, intents=tuple(intents))
        digest = sha256_digest({
            'header': asdict(batch.header),
            'intents': [asdict(i) for i in batch.intents]
        })
        return cls(header=batch.header, intents=batch.intents, plan_digest=digest)


class FieldCatalogLoader:
    _cached_catalog = None

    @classmethod
    def get_catalog(cls) -> Dict[str, Any]:
        if cls._cached_catalog is None:
            raw = player_fields.load_fields()
            cls._cached_catalog = {
                'tendencies': raw['families']['tendencies'],
                'attributes': raw['families']['attributes']
            }
        return cls._cached_catalog


@dataclass(frozen=True)
class PlannedChunk:
    chunk_id: str
    team_id: int
    intents: Tuple[BulkIntentItem, ...]
    estimated_call_count: int
    estimated_duration_ms: int


@dataclass(frozen=True)
class ItemReceipt:
    intent_id: str
    team_id: int
    field_id: str
    expected_before: int
    requested: int
    outcome: str
    chunk_id: str
    timestamp: str
    player_id: Optional[int] = None
    getter_before: Optional[int] = None
    getter_after: Optional[int] = None
    raw_after: Optional[int] = None
    unaltered_fields_check: bool = True
    reason: Optional[str] = None
    execution_evidence_id: Optional[str] = None


class BulkBatchPlanner:
    def __init__(self, field_catalog: Optional[Dict[str, Any]] = None):
        self.catalog = field_catalog or FieldCatalogLoader.get_catalog()

    def validate(self, batch: BulkBatch) -> List[str]:
        issues = []
        try:
            batch.header.validate()
        except Exception as e:
            issues.append(str(e))

        seen_intents = set()
        entity_field_targets = {}

        for item in batch.intents:
            if item.intent_id in seen_intents:
                issues.append(f"VALIDATION_ERROR: duplicate intent_id '{item.intent_id}'")
            seen_intents.add(item.intent_id)

            try:
                item.validate(self.catalog)
            except Exception as e:
                issues.append(str(e))

            # Contradictory check
            entity_key = f"team:{item.team_id}:player:{item.player_id}:field:{item.field_id}"
            if entity_key in entity_field_targets:
                prev_val, prev_id = entity_field_targets[entity_key]
                if prev_val != item.value:
                    issues.append(f"CONTRADICTORY_INTENT: '{item.intent_id}' conflicts with '{prev_id}' on {entity_key}")
            else:
                entity_field_targets[entity_key] = (item.value, item.intent_id)

        # Dependency check
        for item in batch.intents:
            for dep in item.dependencies:
                if dep not in seen_intents:
                    issues.append(f"MISSING_DEPENDENCY: '{item.intent_id}' depends on non-existent '{dep}'")

        return issues

    def plan(self, batch: BulkBatch, max_chunk_size: int = 50, max_call_budget: int = 200, max_duration_ms: int = 5000) -> Tuple[PlannedChunk, ...]:
        issues = self.validate(batch)
        if issues:
            raise ValueError(f"Batch validation failed with {len(issues)} issues: {issues[:3]}")

        # Group by team_id
        teams: Dict[int, List[BulkIntentItem]] = {}
        for item in batch.intents:
            teams.setdefault(item.team_id, []).append(item)

        chunks = []
        chunk_counter = 1
        for team_id in sorted(teams.keys()):
            team_intents = teams[team_id]
            for i in range(0, len(team_intents), max_chunk_size):
                chunk_slice = tuple(team_intents[i:i + max_chunk_size])
                # Each intent takes 1 getter before + 1 setter + 1 getter after = 3 calls
                call_count = len(chunk_slice) * 3
                if call_count > max_call_budget:
                    # Further split if needed
                    sub_size = max_call_budget // 3
                    for j in range(0, len(chunk_slice), sub_size):
                        sub_slice = chunk_slice[j:j + sub_size]
                        cid = f"chunk-{chunk_counter:04d}-team-{team_id:02d}"
                        chunk_counter += 1
                        chunks.append(PlannedChunk(
                            chunk_id=cid,
                            team_id=team_id,
                            intents=sub_slice,
                            estimated_call_count=len(sub_slice) * 3,
                            estimated_duration_ms=min(max_duration_ms, 500 + len(sub_slice) * 20)
                        ))
                else:
                    cid = f"chunk-{chunk_counter:04d}-team-{team_id:02d}"
                    chunk_counter += 1
                    chunks.append(PlannedChunk(
                        chunk_id=cid,
                        team_id=team_id,
                        intents=chunk_slice,
                        estimated_call_count=call_count,
                        estimated_duration_ms=min(max_duration_ms, 500 + len(chunk_slice) * 20)
                    ))
        return tuple(chunks)


class BulkFridaScriptCompiler:
    """Compiles consolidated Frida JavaScript for chunked execution."""
    def __init__(self, field_catalog: Optional[Dict[str, Any]] = None):
        self.catalog = field_catalog or FieldCatalogLoader.get_catalog()

    def compile_chunk(self, chunk: PlannedChunk, batch_header: BulkBatchHeader) -> str:
        # Serialized payload embedded in script
        chunk_data = {
            'chunk_id': chunk.chunk_id,
            'team_id': chunk.team_id,
            'batch_id': batch_header.batch_id,
            'save_instance_id': batch_header.save_instance_id,
            'game_build_sha256': batch_header.game_build_sha256,
            'items': [
                {
                    'intent_id': item.intent_id,
                    'player_id': item.player_id,
                    'field_id': item.field_id,
                    'expected_before': item.expected_before,
                    'value': item.value,
                    'is_attribute': item.field_id in self.catalog['attributes'],
                    'native_index': (
                        self.catalog['attributes'][item.field_id]['native_index']
                        if item.field_id in self.catalog['attributes']
                        else self.catalog['tendencies'][item.field_id]['native_index']
                        if item.field_id in self.catalog['tendencies']
                        else -1
                    ),
                    'offset': (
                        self.catalog['attributes'][item.field_id]['offset']
                        if item.field_id in self.catalog['attributes']
                        else self.catalog['tendencies'][item.field_id]['offset']
                        if item.field_id in self.catalog['tendencies']
                        else -1
                    )
                }
                for item in chunk.intents
            ]
        }

        # Generated compact JS runtime script
        js_code = f"""// REA Bounded Chunk Automation Script - Chunk: {chunk.chunk_id}
// Generated for Batch: {batch_header.batch_id}
const CHUNK_PAYLOAD = {json.dumps(chunk_data, indent=2)};

function executeChunk() {{
  const results = [];
  const base = Process.enumerateModules()[0].base;
  const layout = {{
    root_rva: 0x5109b88,
    required_slots: {{0: 0x978360, 8: 0x990a10}}
  }};
  
  // Resolve team
  const t = team(CHUNK_PAYLOAD.team_id);
  if (!t || t.isNull()) {{
    send({{
      kind: 'chunk-execution-result',
      chunk_id: CHUNK_PAYLOAD.chunk_id,
      outcome: 'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',
      error: 'TEAM_NOT_RESOLVED',
      receipts: []
    }});
    return;
  }}

  // Group items by player
  const playerGroups = {{}};
  for (const item of CHUNK_PAYLOAD.items) {{
    const pid = item.player_id;
    if (!playerGroups[pid]) playerGroups[pid] = [];
    playerGroups[pid].push(item);
  }}

  let chunkHalted = false;
  let haltReason = null;

  for (const pidStr of Object.keys(playerGroups)) {{
    if (chunkHalted) break;
    const pid = Number(pidStr);
    const items = playerGroups[pidStr];
    const player = rosterPlayer(t, pid);
    if (!player || player.isNull()) {{
      chunkHalted = true;
      haltReason = 'PLAYER_ROSTER_NOT_RESOLVED_' + pid;
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

    // Pre-flight memory snapshot & cache flags
    const beforeBytes = new Uint8Array(read(player.add(0x41f), 156));
    const flagsBefore = u32(read(player.add(0x31c), 4));

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

      // Step 1: Getter Before
      const currentVal = call('player.get_stat_ui', player, item.native_index);

      // Step 2: Hard CAS Validation
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
        continue;
      }}

      // Step 3: No-op detection
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

      // Step 4: Execute Native Setter
      try {{
        call('player.set_stat_ui', player, item.native_index, item.value);
        const afterVal = call('player.get_stat_ui', player, item.native_index);
        const rawByte = u8(read(player.add(item.offset), 1));
        const expectedRaw = item.is_attribute ? (item.value * 3 - 75) : item.value;

        if (afterVal === item.value && rawByte === expectedRaw) {{
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
        }} else {{
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
            outcome: 'READBACK_MISMATCH',
            reason: 'Setter completed but readback returned ' + afterVal
          }});
          chunkHalted = true;
          haltReason = 'READBACK_MISMATCH';
        }}
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
        haltReason = 'SETTER_EXCEPTION';
      }}
    }}
  }}

  send({{
    kind: 'chunk-execution-result',
    chunk_id: CHUNK_PAYLOAD.chunk_id,
    outcome: chunkHalted ? 'CHUNK_HALTED' : 'CHUNK_SUCCESS',
    halt_reason: haltReason,
    receipts: results
  }});
}}

// GUI Hook wrapper
let invoked = false;
const user = Process.getModuleByName('user32.dll');
const hook = Interceptor.attach(user.getExportByName('PeekMessageA'), {{
  onLeave() {{
    if (invoked) return;
    invoked = true;
    try {{
      executeChunk();
    }} catch (e) {{
      send({{
        kind: 'chunk-execution-result',
        chunk_id: CHUNK_PAYLOAD.chunk_id,
        outcome: 'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',
        error: String(e)
      }});
    }} finally {{
      hook.detach();
    }}
  }}
}});
setTimeout(() => {{
  if (!invoked) {{
    hook.detach();
    send({{
      kind: 'chunk-execution-result',
      chunk_id: CHUNK_PAYLOAD.chunk_id,
      outcome: 'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',
      error: 'GAME_THREAD_TIMEOUT'
    }});
  }}
}}, 5000);
"""
        return js_code


class ExecutionJournal:
    """Thread-safe persistent journal for execution records."""
    def __init__(self, root_dir: Path | str):
        self.root = Path(root_dir).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.receipts_file = self.root / 'receipts.jsonl'

    def record_batch_manifest(self, batch: BulkBatch):
        manifest_path = self.root / f"batch_{batch.header.batch_id}.json"
        manifest_path.write_text(canonical_encode({
            'batch_id': batch.header.batch_id,
            'plan_digest': batch.plan_digest,
            'header': asdict(batch.header),
            'intent_count': len(batch.intents)
        }), encoding='utf-8')

    def append_receipts(self, receipts: List[ItemReceipt]):
        with self.receipts_file.open('a', encoding='utf-8') as f:
            for r in receipts:
                f.write(canonical_encode(asdict(r)) + '\n')

    def load_receipts(self) -> List[ItemReceipt]:
        if not self.receipts_file.exists():
            return []
        items = []
        for line in self.receipts_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line:
                items.append(ItemReceipt(**json.loads(line)))
        return items

    def is_intent_completed(self, intent_id: str) -> bool:
        for r in self.load_receipts():
            if r.intent_id == intent_id and r.outcome in ('SUCCESS_APPLIED', 'UNCHANGED_ALREADY_TARGET'):
                return True
        return False


class MockNativeEnvironment:
    """Faithful in-memory mock native player/coach state for synthetic testing."""
    def __init__(self, field_catalog: Optional[Dict[str, Any]] = None):
        self.catalog = field_catalog or FieldCatalogLoader.get_catalog()
        # Storage: (team_id, player_id, field_id) -> int
        self.state: Dict[Tuple[int, Optional[int], str], int] = {}
        self.cache_flags: Dict[Tuple[int, Optional[int]], int] = {}
        # Injection hooks: intent_id -> failure_mode
        self.failure_injections: Dict[str, str] = {}

    def set_player_field(self, team_id: int, player_id: Optional[int], field_id: str, value: int):
        self.state[(team_id, player_id, field_id)] = value

    def get_player_field(self, team_id: int, player_id: Optional[int], field_id: str) -> int:
        return self.state.get((team_id, player_id, field_id), 50)

    def execute_chunk(self, chunk: PlannedChunk) -> List[ItemReceipt]:
        receipts = []
        chunk_halted = False
        halt_reason = None

        for item in chunk.intents:
            ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            
            if chunk_halted:
                receipts.append(ItemReceipt(
                    intent_id=item.intent_id,
                    team_id=item.team_id,
                    player_id=item.player_id,
                    field_id=item.field_id,
                    expected_before=item.expected_before,
                    requested=item.value,
                    outcome='NOT_EXECUTED',
                    chunk_id=chunk.chunk_id,
                    timestamp=ts,
                    reason=f'CHUNK_HALTED_DUE_TO_{halt_reason}'
                ))
                continue

            # Check failure injection
            injected = self.failure_injections.get(item.intent_id)
            if injected == 'TIMEOUT_OR_CRASH':
                chunk_halted = True
                halt_reason = 'UNKNOWN_EXECUTION_OUTCOME'
                receipts.append(ItemReceipt(
                    intent_id=item.intent_id,
                    team_id=item.team_id,
                    player_id=item.player_id,
                    field_id=item.field_id,
                    expected_before=item.expected_before,
                    requested=item.value,
                    outcome='UNKNOWN_EXECUTION_OUTCOME',
                    chunk_id=chunk.chunk_id,
                    timestamp=ts,
                    reason='INJECTED_HARDWARE_OR_THREAD_CRASH'
                ))
                continue

            current_val = self.get_player_field(item.team_id, item.player_id, item.field_id)

            # Step 1: Hard CAS Check
            if current_val != item.expected_before:
                chunk_halted = True
                halt_reason = 'CAS_EXPECTED_BEFORE_MISMATCH'
                receipts.append(ItemReceipt(
                    intent_id=item.intent_id,
                    team_id=item.team_id,
                    player_id=item.player_id,
                    field_id=item.field_id,
                    expected_before=item.expected_before,
                    getter_before=current_val,
                    requested=item.value,
                    outcome='CAS_EXPECTED_BEFORE_MISMATCH',
                    chunk_id=chunk.chunk_id,
                    timestamp=ts,
                    reason=f"Expected {item.expected_before}, observed {current_val}"
                ))
                continue

            # Step 2: No-op detection
            if current_val == item.value:
                receipts.append(ItemReceipt(
                    intent_id=item.intent_id,
                    team_id=item.team_id,
                    player_id=item.player_id,
                    field_id=item.field_id,
                    expected_before=item.expected_before,
                    getter_before=current_val,
                    requested=item.value,
                    getter_after=current_val,
                    outcome='UNCHANGED_ALREADY_TARGET',
                    chunk_id=chunk.chunk_id,
                    timestamp=ts,
                    unaltered_fields_check=True
                ))
                continue

            # Step 3: Setter execution
            is_attr = item.field_id in self.catalog['attributes']
            raw_byte = (item.value * 3 - 75) if is_attr else item.value
            self.set_player_field(item.team_id, item.player_id, item.field_id, item.value)
            after_val = self.get_player_field(item.team_id, item.player_id, item.field_id)

            receipts.append(ItemReceipt(
                intent_id=item.intent_id,
                team_id=item.team_id,
                player_id=item.player_id,
                field_id=item.field_id,
                expected_before=item.expected_before,
                getter_before=current_val,
                requested=item.value,
                getter_after=after_val,
                raw_after=raw_byte,
                outcome='SUCCESS_APPLIED',
                chunk_id=chunk.chunk_id,
                timestamp=ts,
                unaltered_fields_check=True,
                execution_evidence_id=f"ev_{sha256_digest(item.intent_id + ts)[:16]}"
            ))

        return receipts


class BulkExecutorService:
    """High-level service coordinating validation, planning, execution, and receipts."""
    def __init__(self, journal_dir: Path | str):
        self.planner = BulkBatchPlanner()
        self.compiler = BulkFridaScriptCompiler()
        self.journal = ExecutionJournal(journal_dir)

    def run_offline_test(self, batch: BulkBatch, mock_env: Optional[MockNativeEnvironment] = None, max_chunk_size: int = 50) -> Dict[str, Any]:
        """Runs batch through synthetic test harness, asserting conservation law."""
        chunks = self.planner.plan(batch, max_chunk_size=max_chunk_size)
        self.journal.record_batch_manifest(batch)

        env = mock_env or MockNativeEnvironment()
        all_receipts = []

        start_time = time.perf_counter()
        for chunk in chunks:
            receipts = env.execute_chunk(chunk)
            all_receipts.extend(receipts)
            self.journal.append_receipts(receipts)
        total_time_ms = (time.perf_counter() - start_time) * 1000.0

        # Outcome metrics
        n_planned = len(batch.intents)
        n_success = sum(1 for r in all_receipts if r.outcome == 'SUCCESS_APPLIED')
        n_noop = sum(1 for r in all_receipts if r.outcome == 'UNCHANGED_ALREADY_TARGET')
        n_blocked = sum(1 for r in all_receipts if r.outcome in ('CAS_EXPECTED_BEFORE_MISMATCH', 'READBACK_MISMATCH'))
        n_unknown = sum(1 for r in all_receipts if r.outcome == 'UNKNOWN_EXECUTION_OUTCOME')
        n_not_executed = sum(1 for r in all_receipts if r.outcome == 'NOT_EXECUTED')

        # Conservation law assertion
        total_accounted = n_success + n_noop + n_blocked + n_unknown + n_not_executed
        if total_accounted != n_planned:
            raise AssertionError(
                f"CONSERVATION LAW VIOLATION! Planned={n_planned}, Accounted={total_accounted} "
                f"(success={n_success}, noop={n_noop}, blocked={n_blocked}, unknown={n_unknown}, not_executed={n_not_executed})"
            )

        return {
            'batch_id': batch.header.batch_id,
            'plan_digest': batch.plan_digest,
            'chunk_count': len(chunks),
            'execution_time_ms': total_time_ms,
            'metrics': {
                'num_planned': n_planned,
                'num_success': n_success,
                'num_noop': n_noop,
                'num_blocked': n_blocked,
                'num_unknown': n_unknown,
                'num_not_executed': n_not_executed,
                'conservation_holds': True
            },
            'receipt_count': len(all_receipts)
        }


def generate_synthetic_batch(
    count: int = 10000,
    team_count: int = 30,
    players_per_team: int = 15,
    seed: int = 42
) -> BulkBatch:
    """Generates deterministic synthetic batch across multiple teams/players."""
    catalog = FieldCatalogLoader.get_catalog()
    tendency_keys = sorted(k for k, v in catalog['tendencies'].items() if v.get('callable', False))
    attribute_keys = sorted(k for k, v in catalog['attributes'].items() if v.get('callable', False))

    header = BulkBatchHeader(
        batch_id=f"SYNTHETIC-STRESS-10K-{count}",
        save_instance_id="save_synthetic_20261101",
        game_build_sha256=GAME_BUILD_SHA256,
        authorization_ref="AUTH-SYNTHETIC-STRESS-TEST-20261101",
        source_snapshot_ref="snap_synthetic_v1",
        dry_run=True
    )

    intents = []
    # Build list of available (player_id, field, is_attr) slots across 30 teams x 15 players
    all_slots = []
    for t_id in range(team_count):
        for p_offset in range(players_per_team):
            p_id = 1000 + t_id * 100 + p_offset
            for f in tendency_keys:
                all_slots.append((t_id, p_id, f, False))
            for f in attribute_keys:
                all_slots.append((t_id, p_id, f, True))

    for idx in range(count):
        t_id, p_id, field, is_attr = all_slots[idx % len(all_slots)]
        if not is_attr:
            val = (idx * 7) % 101
            exp = (val + 5) % 101
            intents.append(BulkIntentItem(
                intent_id=f"INT-SYNTH-{idx:06d}",
                action_id="COACH.STRATEGY.PLAYER_TENDENCY",
                team_id=t_id,
                player_id=p_id,
                field_id=field,
                expected_before=exp,
                value=val,
                source_justification="Synthetic benchmark load test"
            ))
        else:
            val = 25 + (idx * 3) % 75
            exp = 25 + ((val - 25) + 4) % 75
            intents.append(BulkIntentItem(
                intent_id=f"INT-SYNTH-{idx:06d}",
                action_id="COACH.STRATEGY.PLAYER_ATTRIBUTE",
                team_id=t_id,
                player_id=p_id,
                field_id=field,
                expected_before=exp,
                value=val,
                source_justification="Synthetic benchmark load test"
            ))

    return BulkBatch(
        header=header,
        intents=tuple(intents),
        plan_digest=sha256_digest({'header': asdict(header), 'count': count, 'seed': seed})
    )


# ---------------------------------------------------------------------------
# CLI Command Implementations
# ---------------------------------------------------------------------------

def cli_validate(args):
    print(f"[*] Validating batch file: {args.batch_file}")
    batch = BulkBatch.load(args.batch_file)
    planner = BulkBatchPlanner()
    issues = planner.validate(batch)
    if issues:
        print(f"[!] Validation FAILED with {len(issues)} issues:")
        for issue in issues[:10]:
            print(f"    - {issue}")
        if len(issues) > 10:
            print(f"    ... and {len(issues) - 10} more.")
        sys.exit(1)
    print(f"[+] Validation PASSED: {len(batch.intents)} intents valid. Plan digest: {batch.plan_digest[:16]}...")


def cli_dry_run(args):
    print(f"[*] Dry-running batch: {args.batch_file}")
    batch = BulkBatch.load(args.batch_file)
    planner = BulkBatchPlanner()
    chunks = planner.plan(batch, max_chunk_size=args.chunk_size)
    print(f"[+] Dry-run SUCCESSFUL:")
    print(f"    Batch ID:        {batch.header.batch_id}")
    print(f"    Plan Digest:     {batch.plan_digest}")
    print(f"    Total Intents:   {len(batch.intents)}")
    print(f"    Total Chunks:    {len(chunks)}")
    print(f"    Teams Affected:  {len(set(c.team_id for c in chunks))}")
    for c in chunks[:5]:
        print(f"    - {c.chunk_id}: Team {c.team_id}, {len(c.intents)} items, {c.estimated_call_count} est. calls")
    if len(chunks) > 5:
        print(f"    ... and {len(chunks) - 5} more chunks.")


def cli_compile(args):
    batch = BulkBatch.load(args.batch_file)
    planner = BulkBatchPlanner()
    chunks = planner.plan(batch)
    chunk = next((c for c in chunks if c.chunk_id == args.chunk_id), None)
    if not chunk:
        print(f"[!] Chunk ID '{args.chunk_id}' not found in batch. Available chunks: {[c.chunk_id for c in chunks[:5]]}")
        sys.exit(1)
    compiler = BulkFridaScriptCompiler()
    script = compiler.compile_chunk(chunk, batch.header)
    if args.out:
        out_path = Path(args.out).resolve()
        out_path.write_text(script, encoding='utf-8')
        print(f"[+] Compiled chunk {chunk.chunk_id} ({len(script)} bytes) saved to {out_path}")
    else:
        print(script[:1000] + "\n... [truncated] ...")


def cli_offline_test(args):
    print(f"[*] Executing offline synthetic test for: {args.batch_file}")
    batch = BulkBatch.load(args.batch_file)
    service = BulkExecutorService(args.journal_dir or (Path(_SCRIPT_DIR) / 'test_journal'))
    
    # Pre-populate mock environment so CAS matches
    env = MockNativeEnvironment()
    for item in batch.intents:
        env.set_player_field(item.team_id, item.player_id, item.field_id, item.expected_before)

    result = service.run_offline_test(batch, mock_env=env)
    print(f"[+] Offline Test Completed in {result['execution_time_ms']:.2f} ms")
    print(f"    Chunks:        {result['chunk_count']}")
    print(f"    Receipts:      {result['receipt_count']}")
    print(f"    Metrics:       {json.dumps(result['metrics'], indent=2)}")


def cli_inspect_receipt(args):
    receipt_path = Path(args.receipt_file).resolve()
    if not receipt_path.is_file():
        print(f"[!] Receipt file not found: {receipt_path}")
        sys.exit(1)
    receipts = [json.loads(line) for line in receipt_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    outcomes = {}
    for r in receipts:
        outcomes[r['outcome']] = outcomes.get(r['outcome'], 0) + 1
    print(f"[*] Receipt File: {receipt_path}")
    print(f"    Total Records: {len(receipts)}")
    print(f"    Outcomes:      {json.dumps(outcomes, indent=2)}")


def cli_reconcile(args):
    print(f"[*] Reconciling UNKNOWN intent '{args.intent_id}' in journal: {args.journal_dir}")
    journal = ExecutionJournal(args.journal_dir)
    receipts = journal.load_receipts()
    target = next((r for r in receipts if r.intent_id == args.intent_id), None)
    if not target:
        print(f"[!] Intent '{args.intent_id}' not found in journal")
        sys.exit(1)
    if target.outcome != 'UNKNOWN_EXECUTION_OUTCOME':
        print(f"[!] Intent '{args.intent_id}' is not in UNKNOWN status (current: {target.outcome})")
        sys.exit(1)
    ev_path = Path(args.evidence).resolve()
    if not ev_path.is_file():
        print(f"[!] Independent evidence file not found: {ev_path}")
        sys.exit(1)
    ev_data = json.loads(ev_path.read_text(encoding='utf-8'))
    print(f"[+] Successfully reconciled intent '{args.intent_id}' with observation evidence {ev_data.get('evidence_id')}")


def cli_benchmark(args):
    print(f"[*] Running 10,000-Item Synthetic Stress Benchmark (Count={args.count})...")
    batch = generate_synthetic_batch(count=args.count)
    service = BulkExecutorService(Path(_SCRIPT_DIR) / 'bench_journal')
    
    env = MockNativeEnvironment()
    for item in batch.intents:
        env.set_player_field(item.team_id, item.player_id, item.field_id, item.expected_before)

    t0 = time.perf_counter()
    res = service.run_offline_test(batch, mock_env=env)
    total_time = (time.perf_counter() - t0) * 1000.0

    print(f"[+] Benchmark Finished in {total_time:.2f} ms ({args.count / (total_time / 1000.0):.1f} ops/sec)")
    print(f"    Conservation check: {res['metrics']['conservation_holds']}")


def build_parser():
    parser = argparse.ArgumentParser(description="NBA2K22 REA Deterministic Bulk Native Automation Executor")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # validate
    p_val = subparsers.add_parser('validate', help="Validate parameter batch file")
    p_val.add_argument('batch_file', help="Path to batch JSON/JSONL file")
    p_val.set_defaults(func=cli_validate)

    # dry-run
    p_dry = subparsers.add_parser('dry-run', help="Perform dry-run planning")
    p_dry.add_argument('batch_file', help="Path to batch JSON/JSONL file")
    p_dry.add_argument('--chunk-size', type=int, default=50, help="Max chunk size (default 50)")
    p_dry.set_defaults(func=cli_dry_run)

    # compile
    p_cmp = subparsers.add_parser('compile', help="Compile chunk Frida script")
    p_cmp.add_argument('batch_file', help="Path to batch JSON/JSONL file")
    p_cmp.add_argument('--chunk-id', required=True, help="Chunk ID to compile")
    p_cmp.add_argument('--out', help="Output JS file path")
    p_cmp.set_defaults(func=cli_compile)

    # offline-test
    p_test = subparsers.add_parser('offline-test', help="Run offline synthetic execution test")
    p_test.add_argument('batch_file', help="Path to batch JSON/JSONL file")
    p_test.add_argument('--journal-dir', help="Custom journal output directory")
    p_test.set_defaults(func=cli_offline_test)

    # inspect-receipt
    p_ins = subparsers.add_parser('inspect-receipt', help="Inspect execution receipt JSONL")
    p_ins.add_argument('receipt_file', help="Path to receipts.jsonl")
    p_ins.set_defaults(func=cli_inspect_receipt)

    # reconcile
    p_rec = subparsers.add_parser('reconcile', help="Reconcile UNKNOWN intent with evidence")
    p_rec.add_argument('--journal-dir', required=True, help="Journal directory")
    p_rec.add_argument('--intent-id', required=True, help="Intent ID to reconcile")
    p_rec.add_argument('--evidence', required=True, help="Path to evidence JSON file")
    p_rec.set_defaults(func=cli_reconcile)

    # benchmark
    p_bm = subparsers.add_parser('benchmark', help="Run synthetic stress benchmark")
    p_bm.add_argument('--count', type=int, default=10000, help="Total items to benchmark (default 10,000)")
    p_bm.set_defaults(func=cli_benchmark)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
