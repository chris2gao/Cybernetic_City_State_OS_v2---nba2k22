"""Offline intent resolution against the existing pinned REA domain catalog."""
import importlib.util
import json
import hashlib
from pathlib import Path


def native_capabilities(repo_root):
    directory = Path(__file__).parents[1] / 'research/rea_core_profile'
    spec = importlib.util.spec_from_file_location('bic_rea_catalog_bridge', directory / 'bridge.py')
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    profile = json.loads((directory / 'profile.json').read_bytes())
    catalog = bridge.load_catalog(repo_root, profile)
    source = profile['native_research']
    registry = json.loads(bridge.git_blob(repo_root, source['commit'],
                         source['directory'] + '/' + source['action_catalog']))
    catalog['contracts'] = {action['action_id']: action for action in registry['actions']}
    coach_bytes = (directory.parent / 'rea_native_control/data/coach_settings.json').read_bytes()
    catalog['coach_fields'] = json.loads(coach_bytes)['fields']
    catalog['coach_field_source'] = {'path': 'research/rea_native_control/data/coach_settings.json',
                                    'sha256': hashlib.sha256(coach_bytes).hexdigest()}
    return catalog


def _parameter_findings(parameters, schema):
    findings = []
    for name, rule in schema.items():
        if name not in parameters:
            if rule.get('required', True):
                findings.append('MISSING_PARAMETER:' + name)
            continue
        value = parameters[name]
        expected = rule.get('type')
        valid = {'integer': type(value) is int, 'object': isinstance(value, dict),
                 'array': isinstance(value, list), 'string': isinstance(value, str),
                 'boolean': type(value) is bool}.get(expected, False)
        if not valid:
            findings.append('INVALID_TYPE:' + name)
            continue
        if rule.get('enum') is not None and value not in rule['enum']:
            findings.append('OUTSIDE_ENUM:' + name)
        if expected == 'integer' and name.endswith('_id') and value < 0:
            findings.append('NEGATIVE_ID:' + name)
        if expected == 'integer' and ('minimum' in rule and value < rule['minimum'] or 'maximum' in rule and value > rule['maximum']):
            findings.append('OUTSIDE_RANGE:' + name)
    if set(parameters) - set(schema):
        findings.append('UNDECLARED_PARAMETER')
    return findings


def plan_adjustment(intent, catalog):
    """Compile an inspectable plan. Every result is non-executable offline data."""
    if not isinstance(intent.get('parameters', {}), dict):
        raise ValueError('Intent parameters must be an object')
    mapping = {'OFFENSE_FOCUS': 'COACH_APPLY_OFFENSE_POE',
               'DEFENSE_FOCUS': 'COACH_APPLY_DEFENSE_POE',
               'COACH_SETTINGS': 'COACH_SET_KNOWN_CURRENT_SETTINGS',
               'TRAINING_FOCUS': 'TRAIN_PLAYER_SET_FOCUS',
               'PLAYBOOK_CHANGE': 'COACH_ADD_REPLACE_PLAY'}
    action_id = intent.get('action_id') or mapping.get(intent.get('kind'))
    action = catalog['contracts'].get(action_id)
    capability = catalog['actions'].get(action_id)
    result = {'intent': intent, 'action_id': action_id, 'execute': False,
              'source': catalog['source'], 'build_sha256': catalog['game_build_sha256'],
              'execution_authorization': 'SEPARATE_HUMAN_LIVE_AUTHORIZATION_REQUIRED',
              'future_execution_contract': ['fresh bound Getter', 'expected_before CAS',
                  'domain Bulk chunk budget', 'independent readback', 'Journal receipt',
                  'UNKNOWN locks resource; no blind replay', 'authorized failure recovery'],
              'unknowns': []}
    if action is None or capability is None:
        return {**result, 'status': 'NEEDS_VALIDATION', 'capability_state': 'UNKNOWN',
                'unknowns': ['No matching existing catalog action']}
    if intent.get('action_id') and intent.get('kind') in mapping and mapping[intent['kind']] != action_id:
        return {**result, 'status': 'NEEDS_VALIDATION', 'capability_state': 'UNKNOWN',
                'unknowns': ['INTENT_ACTION_MISMATCH']}
    result['capability'] = capability
    historical = capability.get('historical_example') or {}
    exact = historical.get('exact_input') or {}
    exact_before = historical.get('before')
    requested_before = intent.get('expected_before')
    if isinstance(exact.get('settings'), dict) and len(exact['settings']) == 1 and not isinstance(exact_before, dict):
        exact_before = {next(iter(exact['settings'])): exact_before}
    result['historical_validation'] = {
        'action_id': action_id, 'game_build_sha256': catalog['game_build_sha256'],
        'exact_input': exact, 'exact_before': exact_before,
        'record': historical, 'source': catalog['source'],
        'requested_tuple_matches': bool(exact) and intent.get('parameters') == exact
            and requested_before == exact_before
            and intent.get('game_build_sha256') == catalog['game_build_sha256'],
        'current_fresh_getter_verified': False}
    result['input_contract'] = action['input_schema']
    result['native_evidence'] = action.get('evidence', [])
    result['call_sequence_reference'] = action.get('call_sequence', [])
    result['AI_override_and_persistence'] = 'UNKNOWN; separately observe effective settings and save behavior'
    result['coach_field_source'] = catalog.get('coach_field_source')
    forbidden = action.get('domain') in ('D01', 'D02', 'D03', 'D06')
    if forbidden:
        return {**result, 'status': 'FORBIDDEN', 'capability_state': 'FORBIDDEN',
                'unknowns': ['Player edits and transaction/draft operations are outside this diagnostic batch']}
    findings = _parameter_findings(intent.get('parameters', {}), action['input_schema'])
    parameters = intent.get('parameters', {})
    if isinstance(parameters.get('settings'), dict):
        if not parameters['settings']:
            findings.append('EMPTY_SETTINGS')
        for field, value in parameters['settings'].items():
            rule = catalog.get('coach_fields', {}).get(field, {})
            if type(value) is not int or str(value) not in (rule.get('enum') or {}):
                findings.append('UNVERIFIED_SETTING_DOMAIN:' + field)
        before = intent.get('expected_before')
        if not isinstance(before, dict) or set(before) != set(parameters['settings']):
            findings.append('SETTINGS_BEFORE_NOT_BOUND')
        elif any(type(value) is not int or str(value) not in (catalog.get('coach_fields', {}).get(field, {}).get('enum') or {}) for field, value in before.items()):
            findings.append('SETTINGS_BEFORE_DOMAIN_UNVERIFIED')
    for name, rule in action['input_schema'].items():
        if name in parameters and rule.get('type') in ('object', 'array') and name != 'settings':
            findings.append('NESTED_CONTRACT_UNVERIFIED:' + name)
    if intent.get('game_build_sha256') != catalog['game_build_sha256']:
        findings.append('BUILD_NOT_BOUND')
    if intent.get('expected_before') is None:
        findings.append('MISSING_BEFORE_VALUE')
    elif 'value' in action['input_schema']:
        findings.extend('BEFORE_' + finding for finding in _parameter_findings(
            {'value': intent['expected_before']}, {'value': action['input_schema']['value']}))
    identity = intent.get('identity_source')
    if not isinstance(identity, dict) or not identity.get('save_id') or not identity.get('season_id'):
        findings.append('MISSING_SAVE_SEASON_IDENTITY_SOURCE')
    elif 'team_id' in parameters and identity.get('team_id') != parameters['team_id']:
        findings.append('TARGET_TEAM_IDENTITY_NOT_BOUND')
    if not intent.get('before_source'):
        findings.append('BEFORE_SOURCE_NOT_BOUND')
    findings.append('CURRENT_GETTER_EVIDENCE_NOT_VERIFIED')
    if not result['historical_validation']['requested_tuple_matches']:
        findings.append('OUTSIDE_EXACT_HISTORICAL_VALIDATION_SCOPE')
    if intent.get('mode') not in ('FAST_SIM', 'CPU_VS_CPU_3D', 'HUMAN_VS_AI_3D'):
        findings.append('MODE_NOT_BOUND')
    unknowns = action.get('unknowns', []) + action.get('coverage_unknowns', [])
    if not capability.get('runtime_handler') or unknowns:
        findings.append('NATIVE_CAPABILITY_INCOMPLETE')
    if capability['evidence_level'] != 'LiveEffectVerified':
        findings.append('NATIVE_WRITE_NOT_VERIFIED_FOR_CURRENT_PLAN')
    result['unknowns'] = findings + unknowns
    result['capability_state'] = capability['evidence_level']
    result['maturity'] = {'read': 'UNKNOWN', 'write': capability['evidence_level'],
                          'effect': 'EXACT_HISTORICAL_EXAMPLE_ONLY' if capability['evidence_level'] == 'LiveEffectVerified' else 'UNKNOWN'}
    result['maturity']['write'] = 'CURRENT_PLAN_NOT_VERIFIED'
    result['schema_status'] = 'INVALID_OR_INCOMPLETE' if _parameter_findings(parameters, action['input_schema']) else 'SCHEMA_ONLY'
    result['status'] = 'NEEDS_VALIDATION' if findings else 'OFFLINE_PLAN_READY'
    result['effect_scope'] = 'Historical exact-input example only; proposed values and basketball effects remain unverified'
    return result
