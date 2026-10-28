"""Role-facing requirement catalog. No game access or implied role authority.

The embedding host supplies profiles from its authenticated identity service;
never deserialize a model's self-declared role into a trusted profile.
"""
import hashlib
import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from facade import NativeControlFacade
from registry import NativeActionRegistry

ROOT = Path(__file__).resolve().parents[4]
PLANNING = ROOT / '01_os/07_content/_runs/run-20261028-nba2k22-role-native-execution-model-001/02_角色执行能力建模'


@dataclass(frozen=True)
class RoleCapabilityProfile:
    role_type: str
    actor_uid: str
    team_scope: tuple[int, ...]
    world_id: str
    save_instance_id: str
    generation_id: str
    season_id: str
    phase: str
    snapshot_ref: str
    allowed_actions: frozenset[str] = frozenset()
    # Explicit dataset -> public field allowlist from the trusted host.
    read_grants: tuple[tuple[str, tuple[str, ...]], ...] = ()
    player_scope: tuple[int, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, 'team_scope', tuple(self.team_scope))
        object.__setattr__(self, 'allowed_actions', frozenset(self.allowed_actions))
        object.__setattr__(self, 'player_scope', tuple(self.player_scope))
        object.__setattr__(self, 'read_grants', tuple((k, tuple(v)) for k, v in self.read_grants))
        if self.role_type not in {'GM', 'COACH', 'PLAYER', 'WORLD_ADMIN'}:
            raise ValueError('Unknown role')
        for key in ('actor_uid', 'world_id', 'save_instance_id', 'generation_id', 'season_id', 'phase', 'snapshot_ref'):
            if not isinstance(getattr(self, key), str) or not getattr(self, key).strip():
                raise ValueError('Missing identity: ' + key)
        if any(type(t) is not int or not 0 <= t < 65535 for t in self.team_scope):
            raise ValueError('Native team identity required')
        if any(type(p) is not int or not 0 <= p < 65535 for p in self.player_scope):
            raise ValueError('Native player identity required')


class RoleCapabilityService:
    def __init__(self, registry=None, control=None):
        self.registry = registry or (control.registry if control is not None else NativeActionRegistry())
        if control is not None and control.registry is not self.registry:
            raise ValueError('Capability and execution binding registries must be identical')
        self.control = control or NativeControlFacade(self.registry)
        inventory = json.loads((PLANNING / '三角色及世界控制_原子操作目录_v1.json').read_text(encoding='utf-8'))
        crosswalk = json.loads((PLANNING / '既有REA_62动作与需求原子动作交叉表_v1.json').read_text(encoding='utf-8'))
        self.requirements = {r['id']: r for r in inventory['operations']}
        if len(self.requirements) != len(inventory['operations']):
            raise ValueError('Duplicate requirement identity')
        self.mapping = {r['capability_id']: r['rea_action_id'] for r in crosswalk['known_mappings']}
        self.source_mapping_count = len(self.mapping)
        # Preserve PR18 crosswalk as historical evidence; current Human architecture
        # requires ALL agreed package variants to use Process without FullCheck.
        for key in ('GM.TRADE.PICK_ONLY', 'GM.TRADE.MIXED', 'GM.TRADE.MULTI_PLAYER'):
            self.mapping[key] = 'TRADE_EXECUTE_AGREED_PACKAGE'
        for suffix in ('POE_O2', 'POE_O3', 'POE_D2', 'POE_D3'):
            self.mapping['COACH.STRATEGY.' + suffix] = 'COACH_SET_KNOWN_CURRENT_SETTINGS'
        self.mapping['TRAIN.TEAM_FOCUS'] = 'TRAIN_TEAM_PATCH_FOCUS_RAW'
        self.mapping['TRAIN.TEAM_PROFILE'] = 'TRAIN_TEAM_PATCH_PROFILE_RAW'
        self.coach_fields = json.loads((self.registry.root / 'data/coach_settings.json').read_text(encoding='utf-8'))['fields']
        self.version = hashlib.sha256(json.dumps({
            'requirements': inventory, 'mapping': crosswalk,
            'actions': self.registry.catalog, 'coach': self.coach_fields,
            'bindings': {k: b.to_dict() for k, b in self.registry.bindings.items()},
            'live': self.registry.live_validation,
            'effective_mapping': self.mapping,
            'service_contract_code': {
                name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                for name in ('role_capabilities.py', 'role_batches.py', 'runtime_codegen.py')},
            'runtime_sources': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted((self.registry.root / 'runtime').glob('*.js'))},
        }, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def _requirement(self, action_id):
        if action_id not in self.requirements:
            raise KeyError('Unknown requirement: ' + action_id)
        return self.requirements[action_id]

    def describe_action(self, action_id, profile):
        req = self._requirement(action_id)
        native_id = self.mapping.get(action_id)
        native = self.registry.get(native_id) if native_id else None
        # Return meaningful metadata, not raw binding RVAs, pointers or offsets.
        return {
            'action_id': action_id, 'meaning': req['label'],
            'required_role_inputs': deepcopy(req['input']),
            'role_candidates': deepcopy(req['actor']),
            'phase_requirement': req['phase'], 'known_effect': req['effect'],
            'source_maturity': req['baseline_status'],
            'is_external_request': req['baseline_status'] == 'EXTERNAL',
            'world_editor_only': req['baseline_status'] == 'WORLD_EDIT',
            'identity_permission': action_id in profile.allowed_actions,
            'executor_action_id': native_id,
            'native_parameter_schema': deepcopy(native['input_schema']) if native else None,
            'native_maturity': native['capability'] if native else 'NOT_BOUND',
            'call_logic_available': self._callable(native),
            'unknowns': self._gaps(native),
            'historical_exact_live_evidence': self._historical_example(action_id, native),
            'catalog_version': self.version,
            'game_build_sha256': self.registry.catalog['game_build_sha256'],
        }

    def _historical_example(self, action_id, native):
        example = native.get('live_validation') if native else None
        if not example:
            return None
        from role_batches import COACH_FIELDS
        parameters = example.get('exact_input', {})
        if action_id in COACH_FIELDS and not set(COACH_FIELDS[action_id]) <= set(parameters.get('settings', {})):
            return None
        if action_id in {'GM.TRADE.PICK_ONLY', 'GM.TRADE.MIXED', 'GM.TRADE.MULTI_PLAYER'}:
            players = len(parameters.get('players_a', [])) + len(parameters.get('players_b', []))
            picks = len(parameters.get('picks_a', [])) + len(parameters.get('picks_b', []))
            if ((action_id.endswith('PICK_ONLY') and (players or not picks)) or
                (action_id.endswith('MIXED') and not (players and picks)) or
                (action_id.endswith('MULTI_PLAYER') and players <= 2)):
                return None
        return deepcopy(example)

    def _gaps(self, native):
        if not native:
            return ['Native function, ABI, context and readback not bound for this requirement']
        gaps = list(native['unknowns']) + list(native.get('coverage_unknowns', []))
        for step in native['call_sequence']:
            if step.get('binding_id'):
                b = self.registry.binding(step['binding_id'])
                gaps.extend(b.unknowns)
                if b.rva is None and b.return_type != 'LAYOUT':
                    gaps.append('Native entry unresolved')
        if not native['runtime_handler']:
            gaps.append('No runtime handler')
        return list(dict.fromkeys(gaps))

    def _callable(self, native):
        if not native or not native['runtime_handler'] or native['unknowns']:
            return False
        for step in native['call_sequence']:
            if step.get('binding_id'):
                b = self.registry.binding(step['binding_id'])
                if b.unknowns or (b.rva is None and b.return_type != 'LAYOUT'):
                    return False
        return True

    def list_role_capabilities(self, profile):
        return [self.describe_action(key, profile) for key, req in self.requirements.items()
                if profile.role_type in req['actor'] or
                (profile.role_type == 'WORLD_ADMIN' and req['baseline_status'] == 'WORLD_EDIT')]

    def get_allowed_values(self, action_id, profile):
        desc = self.describe_action(action_id, profile)
        fields = {}
        if desc['executor_action_id'] in {
                'COACH_SET_KNOWN_CURRENT_SETTINGS', 'COACH_SET_ROTATION_POLICY',
                'COACH_APPLY_DEFENSE_POE', 'COACH_APPLY_OFFENSE_POE'}:
            for key, field in self.coach_fields.items():
                from role_batches import COACH_FIELDS
                if key not in COACH_FIELDS.get(action_id, ()):
                    continue
                if field['enum']:
                    fields[key] = {'values': deepcopy(field['enum']), 'status': 'RECOVERED_ENUM'}
                elif key in {'RunPlayTendency', 'ZoneUsage', 'BenchUtilization'}:
                    fields[key] = {'minimum': 0, 'maximum': 100, 'status': 'HISTORICAL_UI_RANGE'}
                else:
                    fields[key] = {'status': 'UNKNOWN_UI_RANGE', 'values': None}
        return {'action_id': action_id, 'parameters': desc['native_parameter_schema'],
                'field_values': fields, 'catalog_version': self.version,
                'native_value_contract': {
                    'TRAIN.TEAM_FOCUS': {'focus_values_raw': {'length': 3, 'type': 'finite_float32',
                        'units': 'UNKNOWN_NATIVE_SCALE', 'slot_meanings': 'UNKNOWN', 'conversion_or_sum_rule': 'NONE_INFERRED'}},
                    'TRAIN.TEAM_PROFILE': {'profile_values_raw': {'length': 3, 'type': 'uint8', 'enum_names': 'UNKNOWN'},
                        'subfocus_points_raw': {'length': 38, 'type': 'uint8', 'slot_meanings': 'UNKNOWN'}}
                }.get(action_id),
                'warning': 'Encoding bounds do not certify UI semantics or role permission'}

    def read_role_visible_data(self, profile, dataset_id, *, provider):
        """Consume an already sanitized snapshot provider, never initiate capture.

        Provider signature: provider(profile, dataset_id) -> envelope containing
        exact world/save/generation/season/snapshot identity and a data object.
        """
        grants = dict(profile.read_grants)
        if dataset_id not in grants:
            raise PermissionError('Dataset not granted')
        result = deepcopy(provider(profile, dataset_id))
        for key in ('world_id', 'save_instance_id', 'generation_id', 'season_id', 'snapshot_ref'):
            if result.get(key) != getattr(profile, key):
                raise ValueError('Snapshot identity mismatch: ' + key)
        if result.get('actor_uid') != profile.actor_uid or result.get('role_type') != profile.role_type:
            raise PermissionError('Snapshot recipient mismatch')
        if result.get('team_scope') != list(profile.team_scope):
            raise PermissionError('Snapshot team scope mismatch')
        data = result['data']
        if not isinstance(data, dict):
            raise ValueError('Explicit field projection required')
        result['data'] = {key: data[key] for key in grants[dataset_id] if key in data}
        def inspect(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if 'potential' in str(key).casefold():
                        raise PermissionError('Hidden Potential is excluded from role views')
                    inspect(item)
            elif isinstance(value, list):
                for item in value:
                    inspect(item)
        inspect(result['data'])
        # Project the envelope too: provider debug metadata is not role-visible data.
        return {key: result[key] for key in ('world_id', 'save_instance_id', 'generation_id',
                'season_id', 'snapshot_ref', 'actor_uid', 'role_type', 'team_scope', 'data')}

    def submit_decided_actions(self, batch, *, profiles, phase_grants, agreements=(),
                               journal, pre_dispatch_context, readback=None):
        """Host entry: recompute constraints; never trust a role-supplied BatchPlan."""
        from role_batches import ExecutionAggregator, NativeActionDispatcher
        plan = ExecutionAggregator(self).plan(batch, profiles=profiles,
                   phase_grants=phase_grants, agreements=agreements)
        return NativeActionDispatcher(self, journal).dispatch(plan,
                   pre_dispatch_context=pre_dispatch_context, readback=readback)
