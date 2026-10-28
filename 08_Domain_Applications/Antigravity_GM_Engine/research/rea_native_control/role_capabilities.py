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
        self.mapping['COACH.ROTATION.PLAYER_MINUTES'] = 'COACH_ROTATION_SET_PLAYER_MINUTES'
        self.mapping['PLAYER.EDIT.ATTR_BATCH'] = 'PLAYER_PATCH_ATTRIBUTES'
        self.mapping['PLAYER.EDIT.TENDENCY_BATCH'] = 'PLAYER_PATCH_TENDENCIES'
        self.mapping['GM.CONTRACT.CONTRACT_OFFER'] = 'CONTRACT_SUBMIT_FREE_AGENT_OFFER'
        self.coach_fields = json.loads((self.registry.root / 'data/coach_settings.json').read_text(encoding='utf-8'))['fields']
        self.play_type_names = json.loads((self.registry.root.parents[1] / 'config/state_io_native/player.json').read_text(encoding='utf-8'))['PLAY_TYPE_NAMES']
        from player_fields import load_fields
        self.player_stat_fields = load_fields(self.registry.root)
        from badge_fields import load_fields as load_badges
        self.badge_fields = load_badges(self.registry.root)
        from signing_fields import load_schema
        self.signing_schema = load_schema(self.registry.root)
        self.player_contract_fields = json.loads((self.registry.root / 'data/player_contract_fields.json').read_text(encoding='utf8'))
        self.version = hashlib.sha256(json.dumps({
            'requirements': inventory, 'mapping': crosswalk,
            'actions': self.registry.catalog, 'coach': self.coach_fields, 'play_type_names': self.play_type_names,
            'player_stat_fields': self.player_stat_fields,
            'badge_fields': self.badge_fields,
            'signing_schema': self.signing_schema,
            'player_contract_fields': self.player_contract_fields,
            'read_catalog': json.loads((self.registry.root / 'data/read_catalog.json').read_text(encoding='utf8')),
            'bindings': {k: b.to_dict() for k, b in self.registry.bindings.items()},
            'live': self.registry.live_validation,
            'effective_mapping': self.mapping,
            'service_contract_code': {
                name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                for name in ('role_capabilities.py', 'role_batches.py', 'runtime_codegen.py', 'player_fields.py', 'badge_fields.py', 'player_editor_state.py', 'signing_fields.py', 'readers.py')},
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
            'role_candidates': self.allowed_roles(action_id),
            'source_role_candidates': deepcopy(req['actor']),
            'phase_requirement': req['phase'], 'known_effect': req['effect'],
            'source_maturity': req['baseline_status'],
            'is_external_request': req['baseline_status'] == 'EXTERNAL',
            'world_editor_only': req['baseline_status'] == 'WORLD_EDIT' or bool(
                native and native.get('kind') == 'MUTATE' and self.allowed_roles(action_id) == ['WORLD_ADMIN']),
            'identity_permission': action_id in profile.allowed_actions and profile.role_type in self.allowed_roles(action_id),
            'executor_action_id': native_id,
            'native_parameter_schema': self._role_schema(action_id, native, profile),
            'native_maturity': native['capability'] if native else 'NOT_BOUND',
            'native_effect_contract': deepcopy(native.get('effect_contract')) if native else None,
            'call_logic_available': self._callable(native),
            'unknowns': self._gaps(native),
            'historical_exact_live_evidence': self._historical_example(action_id, native),
            'catalog_version': self.version,
            'game_build_sha256': self.registry.catalog['game_build_sha256'],
        }

    def allowed_roles(self, action_id):
        req = self._requirement(action_id)
        native_id = self.mapping.get(action_id)
        native = self.registry.get(native_id) if native_id else None
        if native and native.get('role_policy'):
            return list(native['role_policy']['roles'])
        return ['WORLD_ADMIN'] if req['baseline_status'] == 'WORLD_EDIT' else deepcopy(req['actor'])

    def _role_schema(self, action_id, native, profile):
        if native is None:
            return None
        schema = deepcopy(native['input_schema'])
        from badge_fields import REQUIREMENT
        if action_id == REQUIREMENT:
            fields = {name: field for name, field in self.badge_fields['fields'].items()
                      if profile.role_type == 'WORLD_ADMIN' and not field['sentinel_name']}
            schema['field_id']['enum'] = sorted(fields)
            for key in ('expected_before', 'expected_after'):
                schema[key].update(minProperties=1, additionalProperties=False,
                    properties={name: {'type': 'integer', 'minimum': 0, 'maximum': field['maximum']}
                                for name, field in fields.items()})
        from role_batches import PLAY_TYPE_SLOTS
        if action_id in PLAY_TYPE_SLOTS:
            slot = PLAY_TYPE_SLOTS[action_id]
            schema['slot_values'].update(properties={slot: {'type': 'integer', 'minimum': 0, 'maximum': 15}},
                                         required=[slot], additionalProperties=False)
        from player_fields import ROLE_FIELDS, allowed_fields
        if action_id in ROLE_FIELDS:
            fields = allowed_fields(self.player_stat_fields, ROLE_FIELDS[action_id], profile.role_type)
            if 'field_id' in schema:
                schema['field_id']['enum'] = sorted(fields)
            else:
                schema['values'].update(minProperties=1, additionalProperties=False,
                    properties={key: {'type': 'integer', 'minimum': value['minimum'], 'maximum': value['maximum']}
                                for key, value in fields.items()})
        return schema

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
                if profile.role_type in self.allowed_roles(key)]

    def get_allowed_values(self, action_id, profile):
        desc = self.describe_action(action_id, profile)
        fields = {}
        if desc['executor_action_id'] in {'SIGN_FREE_AGENT','CONTRACT_SUBMIT_FREE_AGENT_OFFER'}:
            fields['contract'] = {'status':'RECOVERED_NATIVE_ENCODING_ONLY',
                'enums':deepcopy(self.signing_schema['enums']),
                'maturity':deepcopy(self.signing_schema['maturity']),
                'salary_consumer_semantics':deepcopy(self.player_contract_fields['salary_consumer_semantics']),
                'policy':'Caller decides all terms. No automatic prices, no force/accept flags, no completed signing claim from offer return/status.'}
            if desc['executor_action_id']=='CONTRACT_SUBMIT_FREE_AGENT_OFFER':
                fields['contract']['status']='RECOVERED_FA_PERIOD_EXPLICIT_OFFER_SUBMISSION'
                fields['contract']['maturity']={'fresh_offer_submission_qualified':True,'dispatch_implemented':True,
                    'signing_completion_qualified':False,'native_period':'FA_SIGNING',
                    'supported_types':['NORMAL','HARDSHIP'],'wage_distribution':'CUSTOM'}
        from badge_fields import REQUIREMENT, affected_fields
        if action_id == REQUIREMENT:
            available = {name: field for name, field in self.badge_fields['fields'].items()
                         if profile.role_type == 'WORLD_ADMIN' and not field['sentinel_name']}
            fields['field_id'] = {'values': {name: {
                'meaning': 'Recovered internal Native Badge enum ' + name,
                'minimum': 0, 'maximum': field['maximum'], 'ui_label_verified': False,
                'explicit_coupled_group': list(affected_fields(self.badge_fields, name))}
                for name, field in available.items()},
                'status': 'RECOVERED_INTERNAL_ENUM_AND_RAW_LEVELS',
                'policy': 'Explicit world-editor grant only. Caller supplies exact coupled before/after states; original flag0 rules must agree. No ordinary persona Badge editing.'}
        from player_fields import ROLE_FIELDS, allowed_fields
        if action_id in ROLE_FIELDS:
            available = allowed_fields(self.player_stat_fields, ROLE_FIELDS[action_id], profile.role_type)
            fields['field_id'] = {'values': {key: {name: value[name] for name in
                ('meaning', 'minimum', 'maximum', 'name_known', 'encoding')} for key, value in available.items()},
                'status': 'RECOVERED_NATIVE_UI_VALUES',
                'policy': 'Explicit role grant required; ordinary GM attribute scope is intangibles only; unnamed tendencies are editor-only'}
        from role_batches import PLAY_TYPE_SLOTS
        if action_id in PLAY_TYPE_SLOTS:
            fields['play_type'] = {'values': deepcopy(self.play_type_names), 'status': 'EXISTING_PC22_ENUM',
                                  'exact_slot_key': PLAY_TYPE_SLOTS[action_id],
                                  'meaning': 'Assigned ordered PlayType category; not a specific play CRC or guaranteed CPU usage'}
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
                    'COACH.ROTATION.PLAYER_MINUTES': {'minutes': {'minimum': 0, 'maximum': 48,
                        'meaning': 'Explicit assigned rotation minutes for the supplied roster player; 0 assigns no minutes',
                        'representation': 'integer', 'team_sum_rule': 'NO_AUTOMATIC_BALANCING',
                        'scene': 'Host-attested TEAM_ROTATION and a recovered active Native delegate implementation'}},
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
