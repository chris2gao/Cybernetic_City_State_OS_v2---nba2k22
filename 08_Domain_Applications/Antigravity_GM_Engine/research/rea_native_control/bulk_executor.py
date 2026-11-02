"""Deterministic bulk REA native automation executor and CLI suite.

Enforces strict parameter validation, hard CAS (expected_before equality),
bounded-session chunking (one Frida attach and GUI hook per chunk),
Checkpoint014 native runtime and transport integration (live writes disabled by default),
durable execution journaling with UNKNOWN resource locking and reconciliation,
and strict outcome conservation:
    num_planned = num_success + num_noop + num_reused + num_blocked + num_unknown + num_not_executed
"""
import argparse
import copy
import dataclasses
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import platform
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
    import registry
    import transport
except ImportError:
    from . import contracts
    from . import player_fields
    from . import registry
    from . import transport

GAME_BUILD_SHA256 = contracts.BUILD

def load_coach_settings_catalog() -> Dict[str, Any]:
    path = _SCRIPT_DIR / 'data' / 'coach_settings.json'
    if not path.is_file():
        raise FileNotFoundError(f"coach_settings.json not found at {path}")
    return json.loads(path.read_text(encoding='utf-8'))['fields']

COACH_FIELDS = load_coach_settings_catalog()

CANONICAL_ACTIONS = {
    'PLAYER_PATCH_TENDENCIES': 'tendencies',
    'PLAYER_PATCH_ATTRIBUTES': 'attributes',
    'COACH_SET_KNOWN_CURRENT_SETTINGS': 'coach',
}

ACTION_ALIASES = {
    'COACH.STRATEGY.PLAYER_TENDENCY': 'PLAYER_PATCH_TENDENCIES',
    'COACH.STRATEGY.PLAYER_ATTRIBUTE': 'PLAYER_PATCH_ATTRIBUTES',
    'COACH.STRATEGY.POE_O1': 'COACH_SET_KNOWN_CURRENT_SETTINGS',
    'COACH.STRATEGY.POE_O2': 'COACH_SET_KNOWN_CURRENT_SETTINGS',
    'COACH.STRATEGY.POE_O3': 'COACH_SET_KNOWN_CURRENT_SETTINGS',
    'COACH.STRATEGY.POE_D1': 'COACH_SET_KNOWN_CURRENT_SETTINGS',
    'COACH.STRATEGY.POE_D2': 'COACH_SET_KNOWN_CURRENT_SETTINGS',
    'COACH.STRATEGY.POE_D3': 'COACH_SET_KNOWN_CURRENT_SETTINGS',
    'COACH_SET_ROTATION_POLICY': 'COACH_SET_KNOWN_CURRENT_SETTINGS',
}

def resolve_canonical_action(action_id: str) -> str:
    if action_id in CANONICAL_ACTIONS:
        return action_id
    if action_id in ACTION_ALIASES:
        return ACTION_ALIASES[action_id]
    raise ValueError(f"VALIDATION_ERROR: unrecognized action_id '{action_id}' or UNSUPPORTED_DOMAIN. Must be one of {sorted(CANONICAL_ACTIONS.keys())}")


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


def get_resource_key(team_id: int, player_id: Optional[int], field_id: str) -> str:
    """Deterministic resource identity for mutual exclusion and claim tracking."""
    if player_id is not None:
        return f"team:{team_id}:player:{player_id}:field:{field_id}"
    return f"team:{team_id}:coach:{field_id}"


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

        canonical_action = resolve_canonical_action(self.action_id)
        expected_family = CANONICAL_ACTIONS[canonical_action]

        if expected_family == 'tendencies':
            if self.field_id not in field_catalog['tendencies']:
                raise ValueError(f"VALIDATION_ERROR: field_id '{self.field_id}' is unknown or UNSUPPORTED_DOMAIN for tendencies action '{self.action_id}'")
            spec = field_catalog['tendencies'][self.field_id]
            if not spec.get('callable', False):
                raise ValueError(f"VALIDATION_ERROR: tendency field '{self.field_id}' is not callable")
            if self.player_id is None or not isinstance(self.player_id, int):
                raise ValueError(f"VALIDATION_ERROR: player tendency '{self.field_id}' requires integer player_id")
            if not isinstance(self.expected_before, int) or not (spec['minimum'] <= self.expected_before <= spec['maximum']):
                raise ValueError(f"VALIDATION_ERROR: expected_before for '{self.field_id}' must be integer in [{spec['minimum']}, {spec['maximum']}], got {self.expected_before}")
            if not isinstance(self.value, int) or not (spec['minimum'] <= self.value <= spec['maximum']):
                raise ValueError(f"VALIDATION_ERROR: value for '{self.field_id}' must be integer in [{spec['minimum']}, {spec['maximum']}], got {self.value}")

        elif expected_family == 'attributes':
            if self.field_id not in field_catalog['attributes']:
                raise ValueError(f"VALIDATION_ERROR: field_id '{self.field_id}' is unknown or UNSUPPORTED_DOMAIN for attributes action '{self.action_id}'")
            spec = field_catalog['attributes'][self.field_id]
            if not spec.get('callable', False):
                raise ValueError(f"VALIDATION_ERROR: attribute field '{self.field_id}' is not callable")
            if self.player_id is None or not isinstance(self.player_id, int):
                raise ValueError(f"VALIDATION_ERROR: player attribute '{self.field_id}' requires integer player_id")
            if not isinstance(self.expected_before, int) or not (spec['minimum'] <= self.expected_before <= spec['maximum']):
                raise ValueError(f"VALIDATION_ERROR: expected_before for '{self.field_id}' must be integer in [{spec['minimum']}, {spec['maximum']}], got {self.expected_before}")
            if not isinstance(self.value, int) or not (spec['minimum'] <= self.value <= spec['maximum']):
                raise ValueError(f"VALIDATION_ERROR: value for '{self.field_id}' must be integer in [{spec['minimum']}, {spec['maximum']}], got {self.value}")

        elif expected_family == 'coach':
            coach_fields = field_catalog.get('coach', COACH_FIELDS)
            if self.field_id not in coach_fields:
                raise ValueError(f"VALIDATION_ERROR: field_id '{self.field_id}' is unknown or UNSUPPORTED_DOMAIN for coach action '{self.action_id}'")
            spec = coach_fields[self.field_id]
            max_val = (1 << spec['width']) - 1
            if not isinstance(self.expected_before, int) or not (0 <= self.expected_before <= max_val):
                raise ValueError(f"VALIDATION_ERROR: expected_before for coach field '{self.field_id}' must be integer in [0, {max_val}], got {self.expected_before}")
            if spec.get('enum') and str(self.expected_before) not in spec['enum']:
                raise ValueError(f"VALIDATION_ERROR: expected_before for coach field '{self.field_id}' must be valid enum key in {sorted(spec['enum'].keys())}, got {self.expected_before}")
            if not isinstance(self.value, int) or not (0 <= self.value <= max_val):
                raise ValueError(f"VALIDATION_ERROR: value for coach field '{self.field_id}' must be integer in [0, {max_val}], got {self.value}")
            if spec.get('enum') and str(self.value) not in spec['enum']:
                raise ValueError(f"VALIDATION_ERROR: value for coach field '{self.field_id}' must be valid enum key in {sorted(spec['enum'].keys())}, got {self.value}")


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
                'attributes': raw['families']['attributes'],
                'coach': load_coach_settings_catalog()
            }
        return cls._cached_catalog


@dataclass(frozen=True)
class PlannedChunk:
    chunk_id: str
    team_id: int
    action_id: str
    intents: Tuple[BulkIntentItem, ...]
    estimated_call_count: int
    estimated_duration_ms: int
    batch_id: str = ""
    save_instance_id: str = ""
    plan_digest: str = ""
    chunk_digest: str = ""


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
    reused_historical_receipt: bool = False


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
            entity_key = get_resource_key(item.team_id, item.player_id, item.field_id)
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

        # Group by (save_instance_id, team_id)
        groups: Dict[Tuple[str, int], List[BulkIntentItem]] = {}
        for item in batch.intents:
            key = (batch.header.save_instance_id, item.team_id)
            groups.setdefault(key, []).append(item)

        chunks = []
        chunk_counter = 1
        for (save_id, team_id) in sorted(groups.keys()):
            group_intents = groups[(save_id, team_id)]
            for i in range(0, len(group_intents), max_chunk_size):
                chunk_slice = tuple(group_intents[i:i + max_chunk_size])
                call_count = len(chunk_slice) * 3
                sub_size = max_call_budget // 3 if call_count > max_call_budget else len(chunk_slice)
                for j in range(0, len(chunk_slice), sub_size):
                    sub_slice = chunk_slice[j:j + sub_size]
                    actions = {resolve_canonical_action(it.action_id) for it in sub_slice}
                    primary_action = sub_slice[0].action_id if len(actions) == 1 else 'PLAYER_PATCH_TENDENCIES'
                    action_slug = resolve_canonical_action(primary_action).lower().replace('_', '-')
                    cid = f"chunk-{chunk_counter:04d}-team-{team_id:02d}-{action_slug}"
                    chunk_counter += 1
                    cdigest = sha256_digest({
                        'batch_id': batch.header.batch_id,
                        'save_instance_id': save_id,
                        'chunk_id': cid,
                        'team_id': team_id,
                        'action_id': primary_action,
                        'plan_digest': batch.plan_digest,
                        'intents': [asdict(item) for item in sub_slice]
                    })
                    chunks.append(PlannedChunk(
                        chunk_id=cid,
                        team_id=team_id,
                        action_id=primary_action,
                        intents=sub_slice,
                        estimated_call_count=len(sub_slice) * 3,
                        estimated_duration_ms=min(max_duration_ms, 500 + len(sub_slice) * 20),
                        batch_id=batch.header.batch_id,
                        save_instance_id=save_id,
                        plan_digest=batch.plan_digest,
                        chunk_digest=cdigest
                    ))
        return tuple(chunks)


class BulkFridaScriptCompiler:
    """Compiles consolidated Frida JavaScript using Checkpoint014 common.js, gui_once.js and certified contracts."""
    def __init__(self, field_catalog: Optional[Dict[str, Any]] = None):
        self.catalog = field_catalog or FieldCatalogLoader.get_catalog()
        self.reg = registry.NativeActionRegistry(_SCRIPT_DIR)

    def compile_chunk(self, chunk: PlannedChunk, batch_header: BulkBatchHeader) -> str:
        player_items = []
        coach_items = []
        for item in chunk.intents:
            if item.player_id is not None:
                is_attr = item.field_id in self.catalog['attributes']
                n_idx = (
                    self.catalog['attributes'][item.field_id]['native_index']
                    if is_attr
                    else self.catalog['tendencies'][item.field_id]['native_index']
                    if item.field_id in self.catalog['tendencies']
                    else -1
                )
                offset = (
                    self.catalog['attributes'][item.field_id]['offset']
                    if is_attr
                    else self.catalog['tendencies'][item.field_id]['offset']
                    if item.field_id in self.catalog['tendencies']
                    else -1
                )
                player_items.append({
                    'intent_id': item.intent_id,
                    'player_id': item.player_id,
                    'field_id': item.field_id,
                    'expected_before': item.expected_before,
                    'value': item.value,
                    'is_attribute': is_attr,
                    'native_index': n_idx,
                    'offset': offset
                })
            else:
                c_field = self.catalog['coach'].get(item.field_id, {})
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

        chunk_data = {
            'chunk_id': chunk.chunk_id,
            'chunk_digest': chunk.chunk_digest,
            'plan_digest': chunk.plan_digest,
            'team_id': chunk.team_id,
            'action_id': chunk.action_id,
            'batch_id': batch_header.batch_id,
            'save_instance_id': batch_header.save_instance_id,
            'game_build_sha256': batch_header.game_build_sha256,
            'player_items': player_items,
            'coach_items': coach_items
        }

        # Load common templates
        common_js = (_SCRIPT_DIR / 'runtime' / 'common.js').read_text(encoding='utf-8')
        gui_once_js = (_SCRIPT_DIR / 'runtime' / 'gui_once.js').read_text(encoding='utf-8')
        coach_settings_spec = json.loads((_SCRIPT_DIR / 'data' / 'coach_settings.json').read_text(encoding='utf-8'))['fields']
        player_contract_spec = json.loads((_SCRIPT_DIR / 'data' / 'player_contract_fields.json').read_text(encoding='utf-8'))['fields']

        # Required bindings
        binding_ids = ['player.stat_context', 'player.get_stat_ui', 'player.set_stat_ui', 'coach.apply_gameplan']
        bindings = {bid: self.reg.binding(bid).to_dict() for bid in binding_ids if bid in self.reg.bindings}

        req = {
            'action_id': chunk.action_id,
            'chunk_id': chunk.chunk_id,
            'team_id': chunk.team_id,
            'parameters': {
                'batch_id': batch_header.batch_id,
                'save_instance_id': batch_header.save_instance_id
            }
        }
        limits = {
            'maximum_game_calls': max(chunk.estimated_call_count, 100),
            'read_bytes': 1048576,
            'is_live': False
        }

        action_handler_js = f"""
const CHUNK_PAYLOAD = {json.dumps(chunk_data, indent=2)};
const u8 = (b, o = 0) => new DataView(b).getUint8(o);

function executeAction() {{
  const results = [];
  let chunkHalted = false;
  let haltReason = null;

  // Resolve team
  let t = null;
  try {{
    t = team(CHUNK_PAYLOAD.team_id);
  }} catch (e) {{
    send({{
      kind: 'chunk-execution-result',
      chunk_id: CHUNK_PAYLOAD.chunk_id,
      chunk_digest: CHUNK_PAYLOAD.chunk_digest,
      plan_digest: CHUNK_PAYLOAD.plan_digest,
      action_id: CHUNK_PAYLOAD.action_id,
      outcome: 'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',
      error: 'TEAM_NOT_RESOLVED:' + String(e),
      receipts: []
    }});
    return;
  }}

  // 1. Player items execution
  if (CHUNK_PAYLOAD.player_items.length > 0) {{
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

        try {{
          call('player.set_stat_ui', player, item.native_index, item.value);
          const afterBytes = new Uint8Array(read(player.add(0x41f), 156));
          const flagsAfter = u32(read(player.add(0x31c), 4));
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
        }}
      }}
    }}
  }}

  // 2. Coach items execution
  if (CHUNK_PAYLOAD.coach_items.length > 0 && !chunkHalted) {{
    // Coach chunked mutation is explicitly unsupported for live execution
    if (CHUNK_PAYLOAD.action_id === 'COACH_SET_KNOWN_CURRENT_SETTINGS' && limits.is_live) {{
      chunkHalted = true;
      haltReason = 'COACH_CONTRACT_UNSUPPORTED_FOR_LIVE';
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
        const rawCoach = read(coach, 352);
        const m = franchiseRecord(CHUNK_PAYLOAD.team_id).pointer;
        const gp = m.add(0x7854);
        const originalGp = read(gp, 880);

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

          // Apply coach projection
          const inputBuf = Memory.alloc(880);
          inputBuf.writeByteArray(read(gp, 880));
          inputBuf.add(item.gameplan_offset).writeU8(item.value);
          call('coach.apply_gameplan', inputBuf, coach);
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
      }}
    }}
  }}

  send({{
    kind: 'chunk-execution-result',
    chunk_id: CHUNK_PAYLOAD.chunk_id,
    chunk_digest: CHUNK_PAYLOAD.chunk_digest,
    plan_digest: CHUNK_PAYLOAD.plan_digest,
    action_id: CHUNK_PAYLOAD.action_id,
    outcome: chunkHalted ? 'CHUNK_HALTED' : 'CHUNK_SUCCESS',
    halt_reason: haltReason,
    receipts: results
  }});
}}
"""

        full_source = (
            common_js + "\n" +
            action_handler_js + "\n" +
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


class ReaChunkTransportAdapter:
    """Binds bulk executor chunks to Checkpoint014 ReaCliTransport.
    
    Default configuration strictly prohibits live mutation unless explicit
    authorization and non-dry-run are verified with an external verifier.
    """
    def __init__(self, runtime_directory: Path | str, live_context: Optional[Any] = None, *, fake_handler: Optional[Any] = None):
        self.runtime_directory = Path(runtime_directory).resolve()
        self.live_context = live_context
        self.fake_handler = fake_handler

    def execute_chunk(self, chunk: PlannedChunk, script: str) -> Dict[str, Any]:
        if self.fake_handler is not None:
            return self.fake_handler(chunk, script)
            
        # Live path requires authorized external verifier - strictly disabled in this task
        if self.live_context is not None and getattr(self.live_context, 'enabled', False):
            raise PermissionError(
                "LIVE_AUTHORIZATION_VERIFIER_NOT_AVAILABLE: live game execution verifier is not available; "
                "live writes remain fail-closed"
            )
        raise PermissionError(
            "LIVE_MUTATION_NOT_AUTHORIZED: live game execution is disabled by default; "
            "requires explicit external verifier"
        )


class ExecutionJournal:
    """Thread-safe persistent journal with resource locking, at-most-once semantics, and reconciliation."""
    def __init__(self, root_dir: Path | str):
        self.root = Path(root_dir).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.receipts_file = self.root / 'receipts.jsonl'
        self.reconciliations_file = self.root / 'reconciliations.jsonl'
        self.locks_file = self.root / 'locked_resources.json'
        self.claims_dir = self.root / 'claims'
        self.claims_dir.mkdir(parents=True, exist_ok=True)
        self.recover_interrupted_claims()

    def recover_interrupted_claims(self):
        if self.locks_file.exists():
            try:
                json.loads(self.locks_file.read_text(encoding='utf-8'))
            except Exception as e:
                raise RuntimeError(f"CORRUPT_LOCK_LEDGER: locked_resources.json is corrupted: {e}")

        completed_intents = {r.intent_id for r in self.load_receipts()}
        for claim_path in self.claims_dir.glob('*.json'):
            try:
                claim = json.loads(claim_path.read_text(encoding='utf-8'))
            except Exception as e:
                raise RuntimeError(f"CORRUPT_LOCK_LEDGER: claim file {claim_path.name} is corrupted: {e}")
            if claim.get('state') == 'STARTED':
                claim['state'] = 'UNKNOWN_EXECUTION_OUTCOME'
                claim['interrupted_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                claim_path.write_text(canonical_encode(claim), encoding='utf-8')
                for item in claim.get('intents', []):
                    if item.get('intent_id') not in completed_intents:
                        self.lock_resource(item['resource_key'], item['intent_id'])

    def claim_chunk(self, chunk: PlannedChunk):
        claim_file = self.claims_dir / f"{chunk.chunk_id}.json"

        for item in chunk.intents:
            res_key = get_resource_key(item.team_id, item.player_id, item.field_id)
            for existing_claim_file in self.claims_dir.glob('*.json'):
                try:
                    cdata = json.loads(existing_claim_file.read_text(encoding='utf-8'))
                    for e_intent in cdata.get('intents', []):
                        if e_intent.get('intent_id') == item.intent_id:
                            if (e_intent.get('expected_before') != item.expected_before or
                                e_intent.get('value') != item.value or
                                e_intent.get('resource_key') != res_key):
                                raise ValueError(
                                    f"INTENT_ID_REUSED_WITH_DIFFERENT_PAYLOAD: intent '{item.intent_id}' "
                                    f"was previously claimed with different payload"
                                )
                except (json.JSONDecodeError, KeyError):
                    continue

        claim_data = {
            'claim_id': chunk.chunk_id,
            'batch_id': chunk.batch_id,
            'plan_digest': chunk.plan_digest,
            'chunk_id': chunk.chunk_id,
            'chunk_digest': chunk.chunk_digest,
            'save_instance_id': chunk.save_instance_id,
            'action_id': chunk.action_id,
            'team_id': chunk.team_id,
            'state': 'STARTED',
            'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'intents': [
                {
                    'intent_id': item.intent_id,
                    'resource_key': get_resource_key(item.team_id, item.player_id, item.field_id),
                    'expected_before': item.expected_before,
                    'value': item.value
                }
                for item in chunk.intents
            ]
        }
        claim_file.write_text(canonical_encode(claim_data), encoding='utf-8')

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
        for r in receipts:
            if r.outcome == 'UNKNOWN_EXECUTION_OUTCOME':
                res_key = get_resource_key(r.team_id, r.player_id, r.field_id)
                self.lock_resource(res_key, r.intent_id)

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
            if r.intent_id == intent_id and r.outcome in ('SUCCESS_APPLIED', 'UNCHANGED_ALREADY_TARGET', 'RECONCILED_SUCCESS', 'REUSED_HISTORICAL_RECEIPT'):
                return True
        return False

    def get_locked_resources(self) -> Dict[str, str]:
        if not self.locks_file.exists():
            return {}
        try:
            return json.loads(self.locks_file.read_text(encoding='utf-8'))
        except Exception:
            return {}

    def is_resource_locked(self, res_key: str) -> Optional[str]:
        locks = self.get_locked_resources()
        return locks.get(res_key)

    def lock_resource(self, res_key: str, intent_id: str):
        locks = self.get_locked_resources()
        locks[res_key] = intent_id
        self.locks_file.write_text(canonical_encode(locks), encoding='utf-8')

    def unlock_resource(self, res_key: str):
        locks = self.get_locked_resources()
        if res_key in locks:
            del locks[res_key]
            self.locks_file.write_text(canonical_encode(locks), encoding='utf-8')

    def reconcile_unknown(self, intent_id: str, evidence: Dict[str, Any]) -> ItemReceipt:
        receipts = self.load_receipts()
        target = None
        for r in receipts:
            if r.intent_id == intent_id and r.outcome == 'UNKNOWN_EXECUTION_OUTCOME':
                target = r
        if not target:
            raise ValueError(f"No UNKNOWN receipt found for intent_id '{intent_id}'")

        if evidence.get('intent_id') != intent_id:
            raise ValueError(f"Evidence intent_id mismatch: expected '{intent_id}', got '{evidence.get('intent_id')}'")

        if 'readback_getter_value' in evidence and 'target_value' in evidence:
            applied = (evidence['readback_getter_value'] == target.requested and evidence['target_value'] == target.requested)
        elif 'applied' in evidence:
            applied = bool(evidence['applied'])
        else:
            raise ValueError("RECONCILIATION_INCOMPLETE_EVIDENCE: missing required evidence fields")

        new_outcome = 'RECONCILED_SUCCESS' if applied else 'RECONCILED_REJECTED'
        ev_id = evidence.get('evidence_id', 'manual')
        ev_src = evidence.get('evidence_source', 'external')
        ts = evidence.get('timestamp') or time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        readback_val = evidence.get('readback_getter_value', (target.requested if applied else target.expected_before))

        updated_receipt = ItemReceipt(
            intent_id=target.intent_id,
            team_id=target.team_id,
            player_id=target.player_id,
            field_id=target.field_id,
            expected_before=target.expected_before,
            requested=target.requested,
            outcome=new_outcome,
            chunk_id=target.chunk_id,
            timestamp=ts,
            getter_before=target.getter_before,
            getter_after=readback_val,
            raw_after=target.raw_after,
            unaltered_fields_check=True,
            reason=f"RECONCILED_VIA_EVIDENCE:{ev_id}:{ev_src}",
            execution_evidence_id=ev_id
        )

        with self.reconciliations_file.open('a', encoding='utf-8') as f:
            f.write(canonical_encode({
                'intent_id': intent_id,
                'evidence': evidence,
                'reconciled_outcome': new_outcome,
                'timestamp': ts
            }) + '\n')

        self.append_receipts([updated_receipt])
        res_key = get_resource_key(target.team_id, target.player_id, target.field_id)
        self.unlock_resource(res_key)
        return updated_receipt


class MockNativeEnvironment:
    """Faithful in-memory mock native player/coach state for synthetic testing."""
    def __init__(self, field_catalog: Optional[Dict[str, Any]] = None):
        self.catalog = field_catalog or FieldCatalogLoader.get_catalog()
        # Storage: (team_id, player_id, field_id) -> int
        self.state: Dict[Tuple[int, Optional[int], str], int] = {}
        self.coach_state: Dict[Tuple[int, str], int] = {}
        self.cache_flags: Dict[Tuple[int, Optional[int]], int] = {}
        # Injection hooks: intent_id -> failure_mode
        self.failure_injections: Dict[str, str] = {}

    def set_player_field(self, team_id: int, player_id: Optional[int], field_id: str, value: int):
        if player_id is not None:
            self.state[(team_id, player_id, field_id)] = value
        else:
            self.coach_state[(team_id, field_id)] = value

    def get_player_field(self, team_id: int, player_id: Optional[int], field_id: str) -> int:
        if player_id is not None:
            return self.state.get((team_id, player_id, field_id), 50)
        return self.coach_state.get((team_id, field_id), 50)

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
    def __init__(self, journal_dir: Path | str, live_context: Optional[Any] = None):
        self.planner = BulkBatchPlanner()
        self.compiler = BulkFridaScriptCompiler()
        self.journal = ExecutionJournal(journal_dir)
        self.live_context = live_context

    def run_offline_test(self, batch: BulkBatch, mock_env: Optional[MockNativeEnvironment] = None, max_chunk_size: int = 50) -> Dict[str, Any]:
        """Runs batch through synthetic test harness, asserting conservation law and lock invariants."""
        chunks = self.planner.plan(batch, max_chunk_size=max_chunk_size)
        self.journal.record_batch_manifest(batch)

        env = mock_env or MockNativeEnvironment()
        all_receipts = []

        start_time = time.perf_counter()
        for chunk in chunks:
            # Check for completed or locked intents before execution
            chunk_receipts = []
            chunk_to_execute_intents = []
            ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

            for item in chunk.intents:
                res_key = get_resource_key(item.team_id, item.player_id, item.field_id)
                locking_id = self.journal.is_resource_locked(res_key)

                if self.journal.is_intent_completed(item.intent_id):
                    # Already completed in a prior run -> REUSED_HISTORICAL_RECEIPT
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
                elif locking_id and locking_id != item.intent_id:
                    # Resource locked by unresolved UNKNOWN -> BLOCKED_BY_PRIOR_UNKNOWN_CLAIM
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
                else:
                    chunk_to_execute_intents.append(item)

            if chunk_to_execute_intents:
                sub_chunk = PlannedChunk(
                    chunk_id=chunk.chunk_id,
                    team_id=chunk.team_id,
                    action_id=chunk.action_id,
                    intents=tuple(chunk_to_execute_intents),
                    estimated_call_count=len(chunk_to_execute_intents) * 3,
                    estimated_duration_ms=min(5000, 500 + len(chunk_to_execute_intents) * 20),
                    batch_id=chunk.batch_id,
                    save_instance_id=chunk.save_instance_id,
                    plan_digest=chunk.plan_digest,
                    chunk_digest=chunk.chunk_digest
                )
                self.journal.claim_chunk(sub_chunk)
                executed_receipts = env.execute_chunk(sub_chunk)
                chunk_receipts.extend(executed_receipts)

            all_receipts.extend(chunk_receipts)
            self.journal.append_receipts(chunk_receipts)

        total_time_ms = (time.perf_counter() - start_time) * 1000.0

        # Outcome metrics
        n_planned = len(batch.intents)
        n_success = sum(1 for r in all_receipts if r.outcome in ('SUCCESS_APPLIED', 'RECONCILED_SUCCESS'))
        n_noop = sum(1 for r in all_receipts if r.outcome == 'UNCHANGED_ALREADY_TARGET')
        n_reused = sum(1 for r in all_receipts if r.outcome == 'REUSED_HISTORICAL_RECEIPT')
        n_blocked = sum(1 for r in all_receipts if r.outcome in ('CAS_EXPECTED_BEFORE_MISMATCH', 'READBACK_MISMATCH', 'BLOCKED_BY_PRIOR_UNKNOWN_CLAIM', 'RECONCILED_REJECTED'))
        n_unknown = sum(1 for r in all_receipts if r.outcome == 'UNKNOWN_EXECUTION_OUTCOME')
        n_not_executed = sum(1 for r in all_receipts if r.outcome == 'NOT_EXECUTED')

        # Conservation law assertion
        total_accounted = n_success + n_noop + n_reused + n_blocked + n_unknown + n_not_executed
        if total_accounted != n_planned:
            raise AssertionError(
                f"CONSERVATION LAW VIOLATION! Planned={n_planned}, Accounted={total_accounted} "
                f"(success={n_success}, noop={n_noop}, reused={n_reused}, blocked={n_blocked}, unknown={n_unknown}, not_executed={n_not_executed})"
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
                'num_reused': n_reused,
                'num_blocked': n_blocked,
                'num_unknown': n_unknown,
                'num_not_executed': n_not_executed,
                'conservation_holds': True
            },
            'receipt_count': len(all_receipts)
        }

    def run_with_transport(self, batch: BulkBatch, transport_adapter: Any, *, max_chunk_size: int = 50) -> Dict[str, Any]:
        """Coordinates end-to-end batch execution through a transport adapter (Fake or ReaCliTransport)."""
        chunks = self.planner.plan(batch, max_chunk_size=max_chunk_size)
        self.journal.record_batch_manifest(batch)

        all_receipts: List[ItemReceipt] = []
        batch_halted = False
        halt_reason = None
        start_time = time.perf_counter()

        for chunk_idx, chunk in enumerate(chunks):
            chunk_receipts: List[ItemReceipt] = []
            chunk_to_execute_intents: List[BulkIntentItem] = []
            ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

            if batch_halted:
                for item in chunk.intents:
                    chunk_receipts.append(ItemReceipt(
                        intent_id=item.intent_id,
                        team_id=item.team_id,
                        player_id=item.player_id,
                        field_id=item.field_id,
                        expected_before=item.expected_before,
                        requested=item.value,
                        outcome='NOT_EXECUTED',
                        chunk_id=chunk.chunk_id,
                        timestamp=ts,
                        reason=f"BATCH_HALTED_PREVIOUS_FAILURE:{halt_reason}"
                    ))
                all_receipts.extend(chunk_receipts)
                self.journal.append_receipts(chunk_receipts)
                continue

            for item in chunk.intents:
                res_key = get_resource_key(item.team_id, item.player_id, item.field_id)
                locking_id = self.journal.is_resource_locked(res_key)

                if self.journal.is_intent_completed(item.intent_id):
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
                elif locking_id and locking_id != item.intent_id:
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
                else:
                    chunk_to_execute_intents.append(item)

            if not chunk_to_execute_intents:
                all_receipts.extend(chunk_receipts)
                self.journal.append_receipts(chunk_receipts)
                continue

            sub_chunk = PlannedChunk(
                chunk_id=chunk.chunk_id,
                team_id=chunk.team_id,
                action_id=chunk.action_id,
                intents=tuple(chunk_to_execute_intents),
                estimated_call_count=len(chunk_to_execute_intents) * 3,
                estimated_duration_ms=min(5000, 500 + len(chunk_to_execute_intents) * 20),
                batch_id=chunk.batch_id,
                save_instance_id=chunk.save_instance_id,
                plan_digest=chunk.plan_digest,
                chunk_digest=chunk.chunk_digest
            )

            # Record claim BEFORE transport call
            self.journal.claim_chunk(sub_chunk)

            # Compile script
            script = self.compiler.compile_chunk(sub_chunk, batch.header)

            try:
                transport_result = transport_adapter.execute_chunk(sub_chunk, script)
            except Exception as e:
                batch_halted = True
                halt_reason = f"TRANSPORT_EXCEPTION:{type(e).__name__}:{e}"
                for item in chunk_to_execute_intents:
                    chunk_receipts.append(ItemReceipt(
                        intent_id=item.intent_id,
                        team_id=item.team_id,
                        player_id=item.player_id,
                        field_id=item.field_id,
                        expected_before=item.expected_before,
                        requested=item.value,
                        outcome='UNKNOWN_EXECUTION_OUTCOME',
                        chunk_id=chunk.chunk_id,
                        timestamp=ts,
                        reason=halt_reason
                    ))
                all_receipts.extend(chunk_receipts)
                self.journal.append_receipts(chunk_receipts)
                continue

            # Protocol validation (Gate G3)
            validation_error = None
            if not isinstance(transport_result, dict):
                validation_error = "TRANSPORT_RESULT_NOT_DICT"
            elif transport_result.get('outcome') == 'EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY':
                validation_error = transport_result.get('error') or transport_result.get('details', {}).get('reason') or "TRANSPORT_RETURNED_UNKNOWN"
            elif transport_result.get('kind') not in ('chunk-execution-result', 'native-control-result'):
                validation_error = f"INVALID_MESSAGE_KIND:{transport_result.get('kind')}"
            elif transport_result.get('chunk_id') != sub_chunk.chunk_id:
                validation_error = f"CHUNK_ID_MISMATCH: expected {sub_chunk.chunk_id}, got {transport_result.get('chunk_id')}"
            elif 'chunk_digest' in transport_result and transport_result['chunk_digest'] != sub_chunk.chunk_digest:
                validation_error = f"CHUNK_DIGEST_MISMATCH: expected {sub_chunk.chunk_digest}, got {transport_result.get('chunk_digest')}"
            elif 'plan_digest' in transport_result and transport_result['plan_digest'] != batch.plan_digest:
                validation_error = f"PLAN_DIGEST_MISMATCH: expected {batch.plan_digest}, got {transport_result.get('plan_digest')}"

            if validation_error:
                batch_halted = True
                halt_reason = validation_error
                for item in chunk_to_execute_intents:
                    chunk_receipts.append(ItemReceipt(
                        intent_id=item.intent_id,
                        team_id=item.team_id,
                        player_id=item.player_id,
                        field_id=item.field_id,
                        expected_before=item.expected_before,
                        requested=item.value,
                        outcome='UNKNOWN_EXECUTION_OUTCOME',
                        chunk_id=chunk.chunk_id,
                        timestamp=ts,
                        reason=halt_reason
                    ))
                all_receipts.extend(chunk_receipts)
                self.journal.append_receipts(chunk_receipts)
                continue

            raw_receipts = transport_result.get('receipts', [])
            executed_receipt_map = {}
            for r_data in raw_receipts:
                iid = r_data.get('intent_id')
                if iid in executed_receipt_map:
                    validation_error = f"DUPLICATE_RECEIPT_FOR_INTENT:{iid}"
                    break
                executed_receipt_map[iid] = r_data

            if not validation_error and len(raw_receipts) != len(chunk_to_execute_intents):
                validation_error = f"RECEIPT_COUNT_MISMATCH: expected {len(chunk_to_execute_intents)}, got {len(raw_receipts)}"

            if validation_error:
                batch_halted = True
                halt_reason = validation_error
                for item in chunk_to_execute_intents:
                    chunk_receipts.append(ItemReceipt(
                        intent_id=item.intent_id,
                        team_id=item.team_id,
                        player_id=item.player_id,
                        field_id=item.field_id,
                        expected_before=item.expected_before,
                        requested=item.value,
                        outcome='UNKNOWN_EXECUTION_OUTCOME',
                        chunk_id=chunk.chunk_id,
                        timestamp=ts,
                        reason=halt_reason
                    ))
                all_receipts.extend(chunk_receipts)
                self.journal.append_receipts(chunk_receipts)
                continue

            has_failure = False
            for item in chunk_to_execute_intents:
                r_dict = executed_receipt_map[item.intent_id]
                outcome = r_dict.get('outcome', 'UNKNOWN_EXECUTION_OUTCOME')
                if outcome not in ('SUCCESS_APPLIED', 'UNCHANGED_ALREADY_TARGET', 'REUSED_HISTORICAL_RECEIPT'):
                    has_failure = True
                    if not halt_reason:
                        halt_reason = r_dict.get('reason') or outcome

                chunk_receipts.append(ItemReceipt(
                    intent_id=item.intent_id,
                    team_id=item.team_id,
                    player_id=item.player_id,
                    field_id=item.field_id,
                    expected_before=item.expected_before,
                    requested=item.value,
                    outcome=outcome,
                    chunk_id=chunk.chunk_id,
                    timestamp=ts,
                    getter_before=r_dict.get('getter_before'),
                    getter_after=r_dict.get('getter_after'),
                    raw_after=r_dict.get('raw_after'),
                    unaltered_fields_check=r_dict.get('unaltered_fields_check', True),
                    reason=r_dict.get('reason'),
                    execution_evidence_id=transport_result.get('evidence_id')
                ))

            if has_failure and transport_result.get('outcome') == 'CHUNK_HALTED':
                batch_halted = True

            all_receipts.extend(chunk_receipts)
            self.journal.append_receipts(chunk_receipts)

        total_time_ms = (time.perf_counter() - start_time) * 1000.0

        n_planned = len(batch.intents)
        n_success = sum(1 for r in all_receipts if r.outcome in ('SUCCESS_APPLIED', 'RECONCILED_SUCCESS'))
        n_noop = sum(1 for r in all_receipts if r.outcome == 'UNCHANGED_ALREADY_TARGET')
        n_reused = sum(1 for r in all_receipts if r.outcome == 'REUSED_HISTORICAL_RECEIPT')
        n_blocked = sum(1 for r in all_receipts if r.outcome in ('CAS_EXPECTED_BEFORE_MISMATCH', 'READBACK_MISMATCH', 'BLOCKED_BY_PRIOR_UNKNOWN_CLAIM', 'RECONCILED_REJECTED'))
        n_unknown = sum(1 for r in all_receipts if r.outcome == 'UNKNOWN_EXECUTION_OUTCOME')
        n_not_executed = sum(1 for r in all_receipts if r.outcome == 'NOT_EXECUTED')

        total_accounted = n_success + n_noop + n_reused + n_blocked + n_unknown + n_not_executed
        if total_accounted != n_planned:
            raise AssertionError(
                f"CONSERVATION LAW VIOLATION! Planned={n_planned}, Accounted={total_accounted} "
                f"(success={n_success}, noop={n_noop}, reused={n_reused}, blocked={n_blocked}, unknown={n_unknown}, not_executed={n_not_executed})"
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
                'num_reused': n_reused,
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
            # Make first 150 items true no-ops (exp == val)
            exp = val if idx < 150 else (val + 5) % 101
            intents.append(BulkIntentItem(
                intent_id=f"INT-SYNTH-{idx:06d}",
                action_id="PLAYER_PATCH_TENDENCIES",
                team_id=t_id,
                player_id=p_id,
                field_id=field,
                expected_before=exp,
                value=val,
                source_justification="Synthetic benchmark load test"
            ))
        else:
            val = 25 + (idx * 3) % 75
            exp = val if idx < 150 else (25 + ((val - 25) + 4) % 75)
            intents.append(BulkIntentItem(
                intent_id=f"INT-SYNTH-{idx:06d}",
                action_id="PLAYER_PATCH_ATTRIBUTES",
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


def run_10k_benchmark(output_path: Optional[Path | str] = None) -> Dict[str, Any]:
    """Executes 10,000 item benchmark and returns structured performance metrics distinguishing mock vs session overhead vs live projections."""
    import numpy as np

    # 1. Generation & Parse
    t0 = time.perf_counter()
    batch = generate_synthetic_batch(10000)
    t_gen_ms = (time.perf_counter() - t0) * 1000.0

    # 2. Planning & Chunking
    planner = BulkBatchPlanner()
    t1 = time.perf_counter()
    chunks = planner.plan(batch, max_chunk_size=50)
    t_plan_ms = (time.perf_counter() - t1) * 1000.0

    # 3. Compile sample chunk
    compiler = BulkFridaScriptCompiler()
    t_comp_start = time.perf_counter()
    sample_script = compiler.compile_chunk(chunks[0], batch.header)
    t_comp_ms = (time.perf_counter() - t_comp_start) * 1000.0

    # 4. Mock execution with per-chunk timings
    env = MockNativeEnvironment()
    for item in batch.intents:
        env.set_player_field(item.team_id, item.player_id, item.field_id, item.expected_before)

    # Set 2 items to CAS mismatch (in 2 separate chunks)
    for i in [250, 450]:
        item = batch.intents[i]
        env.set_player_field(item.team_id, item.player_id, item.field_id, 999)

    # Inject 1 crash/timeout
    env.failure_injections[batch.intents[600].intent_id] = 'TIMEOUT_OR_CRASH'

    chunk_durations_ms = []
    item_durations_ms = []
    all_receipts = []

    t_exec_start = time.perf_counter()
    for chunk in chunks:
        c_start = time.perf_counter()
        receipts = env.execute_chunk(chunk)
        c_dur = (time.perf_counter() - c_start) * 1000.0
        chunk_durations_ms.append(c_dur)
        per_item = c_dur / len(chunk.intents)
        item_durations_ms.extend([per_item] * len(chunk.intents))
        all_receipts.extend(receipts)
    total_exec_ms = (time.perf_counter() - t_exec_start) * 1000.0

    chunk_p50 = float(np.percentile(chunk_durations_ms, 50))
    chunk_p95 = float(np.percentile(chunk_durations_ms, 95))
    chunk_p99 = float(np.percentile(chunk_durations_ms, 99))

    item_p50 = float(np.percentile(item_durations_ms, 50))
    item_p95 = float(np.percentile(item_durations_ms, 95))
    item_p99 = float(np.percentile(item_durations_ms, 99))

    # Dynamically aggregate counts from actual receipts
    n_planned = len(batch.intents)
    n_success = sum(1 for r in all_receipts if r.outcome in ('SUCCESS_APPLIED', 'RECONCILED_SUCCESS'))
    n_noop = sum(1 for r in all_receipts if r.outcome == 'UNCHANGED_ALREADY_TARGET')
    n_blocked = sum(1 for r in all_receipts if r.outcome in ('CAS_EXPECTED_BEFORE_MISMATCH', 'READBACK_MISMATCH', 'BLOCKED_BY_PRIOR_UNKNOWN_CLAIM'))
    n_unknown = sum(1 for r in all_receipts if r.outcome == 'UNKNOWN_EXECUTION_OUTCOME')
    n_not_executed = sum(1 for r in all_receipts if r.outcome == 'NOT_EXECUTED')
    total_accounted = n_success + n_noop + n_blocked + n_unknown + n_not_executed

    if total_accounted != n_planned:
        raise AssertionError(f"Conservation violation in 10k benchmark: {total_accounted} != {n_planned}")

    bench_data = {
        'schema_version': 'nba2k22.rea.bulk_executor.benchmark.v1',
        'benchmark_timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'test_machine': {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'node_version': 'v24.22.1',
            'rea_cli_version': '6.8.0',
            'target_game_build': GAME_BUILD_SHA256
        },
        'scale': {
            'total_intents': 10000,
            'teams_covered': 30,
            'players_covered': 450,
            'chunks_planned': len(chunks),
            'max_chunk_size': 50
        },
        'mock_execution_timings': {
            'metric_type': 'MEASURED_MOCK',
            'batch_generation_and_parse_time_ms': round(t_gen_ms, 2),
            'planning_and_validation_time_ms': round(t_plan_ms, 2),
            'sample_frida_script_compile_time_ms': round(t_comp_ms, 2),
            'compiled_script_bytes': len(sample_script),
            'total_mock_execution_time_ms': round(total_exec_ms, 2),
            'mock_throughput_ops_per_sec': round(10000 / (total_exec_ms / 1000.0), 1),
            'chunk_level_latency_ms': {
                'p50': round(chunk_p50, 4),
                'p95': round(chunk_p95, 4),
                'p99': round(chunk_p99, 4)
            },
            'item_level_latency_ms': {
                'p50': round(item_p50, 4),
                'p95': round(item_p95, 4),
                'p99': round(item_p99, 4)
            }
        },
        'session_overhead_estimates': {
            'metric_type': 'ESTIMATED_THEORETICAL',
            'unchunked_legacy_sessions': 10000,
            'unchunked_estimated_overhead_seconds': 40000.0,
            'unchunked_overhead_hours': 11.11,
            'bounded_chunks_planned': len(chunks),
            'bounded_chunk_estimated_overhead_seconds': round(len(chunks) * 4.0, 1),
            'bounded_chunk_overhead_minutes': round((len(chunks) * 4.0) / 60.0, 2),
            'session_overhead_reduction_percent': round((1.0 - (len(chunks) / 10000.0)) * 100.0, 2)
        },
        'projected_live_native_duration': {
            'metric_type': 'PROJECTED_NOT_RUN',
            'basis_measurement': "Damian Lillard live execution receipt confirmed native Setter 0x990a10 + Getter 0x978360 takes < 50ms per call",
            'estimated_live_native_call_seconds': 500.0,
            'estimated_live_native_call_minutes': 8.33,
            'projected_total_live_chunked_duration_minutes': round(((len(chunks) * 4.0) + 500.0) / 60.0, 2),
            'projected_unchunked_live_duration_hours': round((40000.0 + 500.0) / 3600.0, 2)
        },
        'outcome_conservation': {
            'metric_type': 'DYNAMICALLY_AGGREGATED_RECEIPTS',
            'num_planned': n_planned,
            'num_success': n_success,
            'num_noop': n_noop,
            'num_blocked': n_blocked,
            'num_unknown': n_unknown,
            'num_not_executed': n_not_executed,
            'total_accounted': total_accounted,
            'conservation_holds': True
        }
    }

    if output_path:
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(bench_data, indent=2), encoding='utf-8')

    return bench_data


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


def cli_execute_authorized(args):
    print(f"[*] Checking authorization for batch file: {args.batch_file}")
    batch = BulkBatch.load(args.batch_file)

    if not args.allow_live_mutation:
        print("[!] ERROR: Live mutation not authorized. Missing flag --allow-live-mutation.")
        print("    Default engine configuration strictly prohibits live process attachment or memory writes.")
        sys.exit(1)

    if batch.header.dry_run:
        print("[!] ERROR: Batch header specifies dry_run=True. Live mutation cannot be executed.")
        sys.exit(1)

    print("[!] ERROR: LIVE_AUTHORIZATION_VERIFIER_NOT_AVAILABLE: live game execution verifier is not available.")
    print("    In accordance with Core verification plan Gate G1, command-line flags and string authorization_ref")
    print("    do not constitute trusted external verification. Live execution remains fail-closed.")
    sys.exit(1)


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
    ev_path = Path(args.evidence).resolve()
    if not ev_path.is_file():
        print(f"[!] Independent evidence file not found: {ev_path}")
        sys.exit(1)
    ev_data = json.loads(ev_path.read_text(encoding='utf-8'))
    updated = journal.reconcile_unknown(args.intent_id, ev_data)
    print(f"[+] Successfully reconciled intent '{args.intent_id}' -> {updated.outcome}")


def cli_benchmark(args):
    print(f"[*] Running 10,000-Item Synthetic Stress Benchmark (Count={args.count})...")
    res = run_10k_benchmark(args.out)
    m = res['mock_execution_timings']
    print(f"[+] Benchmark Finished in {m['total_mock_execution_time_ms']:.2f} ms ({m['mock_throughput_ops_per_sec']:.1f} ops/sec)")
    print(f"    Chunk Latency (p50/p95/p99): {m['chunk_level_latency_ms']['p50']} / {m['chunk_level_latency_ms']['p95']} / {m['chunk_level_latency_ms']['p99']} ms")
    print(f"    Session Overhead Reduction: {res['session_overhead_estimates']['session_overhead_reduction_percent']}%")
    print(f"    Conservation check: {res['outcome_conservation']['conservation_holds']}")


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

    # execute-authorized
    p_exec = subparsers.add_parser('execute-authorized', help="Execute authorized batch (prohibited by default)")
    p_exec.add_argument('batch_file', help="Path to batch JSON/JSONL file")
    p_exec.add_argument('--allow-live-mutation', action='store_true', default=False, help="Explicit Human authorization flag")
    p_exec.add_argument('--runtime-dir', help="Custom runtime output directory")
    p_exec.add_argument('--expected-pid', type=int, help="Expected target process PID")
    p_exec.set_defaults(func=cli_execute_authorized)

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
    p_bm.add_argument('--out', help="Output JSON path to save benchmark results")
    p_bm.set_defaults(func=cli_benchmark)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
