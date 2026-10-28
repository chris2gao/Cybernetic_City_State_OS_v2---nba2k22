"""Prepare immutable exact-input programs, then execute one authorized case once.

Preparation never discovers or attaches a process. Human approval is recorded by
the local Owner; this file is an accidental-execution guard, not authentication.
No target selection, decision optimization, retry or compensation is performed.
"""
import argparse
import hashlib
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

from contracts import BUILD, NativeActionRequest
from facade import NativeControlFacade
from transport import LiveExecutionContext, ReaCliTransport

READ_ACTIONS = {
    'READ_TEAM_ROSTER_BASIC', 'READ_COACH_CURRENT',
    'READ_PLAYER_PROFILE_ATTRIBUTES_TENDENCIES_BADGES',
    'SCOUT_LIST_CURRENT_PUBLIC_PROSPECTS', 'SCOUT_READ_PROSPECT_INFO',
    'SCOUT_READ_PROGRESS_RAW', 'SCOUT_READ_TRIP_BUDGET',
}
EFFECT_ACTIONS = {'COACH_SET_KNOWN_CURRENT_SETTINGS', 'SCOUT_ASSIGN_TARGETS',
                  'SCOUT_SET_EXISTING_GOAL_TARGETS', 'TRADE_EXECUTE_AGREED_PACKAGE'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def source_fingerprints():
    root = Path(__file__).parent
    files = [p for pattern in ('*.py', '*.ps1', 'runtime/*.js', 'data/*.json') for p in root.glob(pattern)]
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(files)}


def prepare(request_file, directory):
    requests = load(request_file)
    directory = Path(directory).resolve()
    if directory.exists():
        raise FileExistsError('Do not overwrite an already prepared batch')
    specs = requests['cases']
    if not 1 <= len(specs) <= 12:
        raise ValueError('One finite batch of 1..12 explicitly supplied cases required')
    facade = NativeControlFacade()
    cases, names = [], set()
    # Validate and render all inputs before creating the output directory.
    for spec in specs:
        name, action = spec['case_id'], spec['action_id']
        if not name.replace('_', '').replace('-', '').isalnum() or name in names:
            raise ValueError('Unique simple case_id required')
        names.add(name)
        if action not in READ_ACTIONS | EFFECT_ACTIONS:
            raise ValueError('This first-batch runner does not qualify that action')
        parameters = spec['parameters']
        if action == 'COACH_SET_KNOWN_CURRENT_SETTINGS':
            settings = parameters['settings']
            if len(settings) != 1 or 'POEDefense' in settings:
                raise ValueError('One new field only; do not repeat the prior defense test')
        if action in EFFECT_ACTIONS and not spec.get('input_source'):
            raise ValueError('Effect inputs must name their direct Human/GM source')
        request = NativeActionRequest(action, parameters, name)
        program = facade.render(request)
        cases.append((spec, program))
    directory.mkdir(parents=True, exist_ok=False)
    records = []
    for spec, program in cases:
        name = spec['case_id']
        path = directory/(name+'.js')
        path.write_text(program.script, encoding='utf-8')
        records.append({
            'case_id': name, 'action_id': spec['action_id'],
            'parameters': spec['parameters'], 'input_source': spec.get('input_source'),
            'kind': 'READ' if spec['action_id'] in READ_ACTIONS else 'NATIVE_EFFECT',
            'script': path.name, 'script_sha256': digest(path),
            'maximum_game_calls': program.maximum_game_calls,
            'maximum_read_bytes': 1048576, 'frida_duration_ms': 15000,
            'game_thread_hook_ms': 4000,
            'requires_successful_cases': spec.get('requires_successful_cases', []),
            'not_executed': True,
        })
    manifest = {
        'schema': 'pc22.functional_validation_batch.v1',
        'batch_id': requests['batch_id'], 'game_build_sha256': BUILD,
        'save_context_supplied': requests.get('save_context', 'NOT_YET_CONFIRMED'),
        'source_fingerprints': source_fingerprints(), 'cases': records,
        'maximum_game_calls': sum(case['maximum_game_calls'] for case in records),
        'maximum_attach_sessions': len(records), 'automatic_retry': False,
        'automatic_trip_execution': False, 'automatic_recovery_write': False,
        'game_target': 'One current NBA2K22 process, pinned by PID and start time on first approved case',
        'recovery': 'Leave approved effects for inspection. On an unclear result, independently read only; if still unclear stop. Human may reload the recoverable test save. No automatic save/reload.',
    }
    path = directory/'batch.json'
    write(path, manifest)
    print(json.dumps({'status': 'PREPARED_NOT_EXECUTED', 'batch': str(path), 'sha256': digest(path), 'cases': len(records), 'maximum_game_calls': manifest['maximum_game_calls']}))


class ExactPreparedTransport:
    def __init__(self, backend, case, approved_script):
        self.backend, self.case, self.approved_script = backend, case, approved_script

    def execute(self, script, *, action_id, request_id, maximum_game_calls):
        if script != self.approved_script or action_id != self.case['action_id'] or maximum_game_calls != self.case['maximum_game_calls']:
            raise ValueError('Rendered program differs from the inspected approved case')
        return self.backend.execute(script, action_id=action_id, request_id=request_id, maximum_game_calls=maximum_game_calls)


def execute(batch_file, approval_file, case_id, runtime):
    batch_file, runtime = Path(batch_file).resolve(), Path(runtime).resolve()
    batch, approval = load(batch_file), load(approval_file)
    if approval.get('batch_sha256') != digest(batch_file) or not approval.get('human_confirmation_ref'):
        raise PermissionError('Recorded Human authority covering this exact batch is required')
    if approval.get('recoverable_test_save_confirmed') is not True:
        raise PermissionError('Current recoverable test save has not been confirmed')
    if approval.get('administrator_runtime_launch_approved') is not True:
        raise PermissionError('Administrator runtime must be explicitly included in the approved batch')
    if case_id not in approval.get('approved_case_ids', []):
        raise PermissionError('Case is not included in the current approval')
    case = next(c for c in batch['cases'] if c['case_id'] == case_id)
    if source_fingerprints() != batch['source_fingerprints']:
        raise ValueError('Source changed after batch preparation; re-prepare before approval')
    program = batch_file.parent/case['script']
    if digest(program) != case['script_sha256']:
        raise ValueError('Approved script changed')
    runtime.mkdir(parents=True, exist_ok=True)
    for required in case['requires_successful_cases']:
        previous = load(runtime/(required+'.result.json'))
        if previous.get('owner_reviewed_prerequisite_satisfied') is not True:
            raise PermissionError('Required observation has not been reviewed: '+required)
    # Reserve a case before any process discovery. An exception is never a retry grant.
    marker = runtime/(case_id+'.started.json')
    with marker.open('x', encoding='utf-8') as stream:
        json.dump({'case_id': case_id, 'batch_sha256': digest(batch_file), 'human_confirmation_ref': approval['human_confirmation_ref']}, stream)
    identity_script = Path(__file__).with_name('validation_runtime_identity.ps1')
    identity = subprocess.run(['powershell.exe', '-NoProfile', '-File', str(identity_script)], check=True, capture_output=True, encoding='utf-8-sig')
    target = json.loads(identity.stdout)
    if target['exe_sha256'] != BUILD:
        raise ValueError('Pinned PC22 executable mismatch')
    if approval.get('expected_pid') is not None and target['pid'] != approval['expected_pid']:
        raise ValueError('Human-approved game PID has changed')
    if approval.get('expected_process_start_utc') is not None and target['process_start_utc'] != approval['expected_process_start_utc']:
        raise ValueError('Human-approved game lifetime has changed')
    pinned_file = runtime/'pinned_target.json'
    if pinned_file.exists():
        if load(pinned_file) != target:
            raise ValueError('Game PID or lifetime changed; current batch cannot continue')
    else:
        write(pinned_file, target)
    context = LiveExecutionContext(approval['human_confirmation_ref'], frozenset({case['action_id']}), case['maximum_game_calls'], enabled=True, expected_pid=target['pid'])
    backend = ReaCliTransport(runtime/'raw', context, duration_ms=case['frida_duration_ms'])
    transport = ExactPreparedTransport(backend, case, program.read_text(encoding='utf-8'))
    facade = NativeControlFacade(transport=transport)
    result = facade.dispatch(NativeActionRequest(case['action_id'], case['parameters'], case_id))
    record = {'case_id': case_id, 'batch_sha256': digest(batch_file), 'target': target, 'result': asdict(result), 'owner_reviewed_prerequisite_satisfied': False, 'effect_verdict': 'NOT_YET_INDEPENDENTLY_READ_BACK'}
    write(runtime/(case_id+'.result.json'), record)
    print(json.dumps({'case_id': case_id, 'outcome': result.outcome, 'effect_verdict': record['effect_verdict'], 'record': str(runtime/(case_id+'.result.json'))}))
    return record


def sequence(batch_file, approval_file, runtime):
    """Run only prepared cases, isolating independent reads from failed probes.

    Each approved sequence supports at most one exact business submission.
    Append and explicitly requested replacement are separate actions.
    """
    batch, runtime = load(batch_file), Path(runtime).resolve()
    effects = [c for c in batch['cases'] if c['kind'] == 'NATIVE_EFFECT']
    if len(effects) > 1:
        raise ValueError('One exact new business submission per approved sequence')
    records = {}
    effect_unclear = False
    for case in batch['cases']:
        if case['kind'] == 'NATIVE_EFFECT' and effect_unclear:
            raise RuntimeError('No further business submission after an unclear effect')
        if any(not records.get(required, {}).get('owner_reviewed_prerequisite_satisfied') for required in case['requires_successful_cases']):
            records[case['case_id']] = {'status': 'NOT_EXECUTED_PREREQUISITE_UNSATISFIED'}
            continue
        try:
            record = execute(batch_file, approval_file, case['case_id'], runtime)
        except Exception as exc:
            records[case['case_id']] = {'status': 'EXECUTION_STATE_UNKNOWN_NO_RETRY', 'error_type': type(exc).__name__, 'message': str(exc)}
            if case['kind'] == 'NATIVE_EFFECT':
                effect_unclear = True
            continue
        native = record['result'].get('native_result') or {}
        details = native.get('details', {})
        readable = native.get('outcome') == 'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED' and details.get('read_only') is True
        data = details.get('data', {})
        if case['action_id'] == 'READ_TEAM_ROSTER_BASIC':
            readable = readable and data.get('team_id') == case['parameters']['team_id']
            if case['parameters']['team_id'] == 20:
                readable = readable and data.get('abbreviation', '').strip().upper() == 'IND'
        if case['action_id'] == 'READ_COACH_CURRENT':
            readable = readable and data.get('team_id') == 20 and data.get('reciprocal_owner_matches') is True and data.get('reference_slots_null') == [True, True, True]
        if case['action_id'] == 'SCOUT_READ_PROSPECT_INFO':
            readable = readable and data.get('player_id') == case['parameters']['player_id']
        if case['action_id'] == 'SCOUT_READ_TRIP_BUDGET':
            readable = readable and details.get('team_id') == case['parameters']['team_id'] and details.get('quality_flags') == []
        record['owner_reviewed_prerequisite_satisfied'] = bool(readable)
        record['prerequisite_review_method'] = 'DETERMINISTIC_READ_IDENTITY_CHECK_NOT_HUMAN_ACCEPTANCE'
        if case['kind'] == 'NATIVE_EFFECT':
            effect_unclear = native.get('outcome') != 'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED'
        records[case['case_id']] = record
        write(runtime/(case['case_id']+'.result.json'), record)
    verdict = {'status': 'NO_NEW_EFFECT_PROVEN', 'automatic_second_submission': False}
    if effects and effects[0]['action_id'] == 'COACH_SET_KNOWN_CURRENT_SETTINGS':
        effect = effects[0]
        before = records.get('coach_before', {}).get('result', {}).get('native_result') or {}
        after = records.get('coach_after', {}).get('result', {}).get('native_result') or {}
        observed = records.get(effect['case_id'], {}).get('result', {}).get('native_result') or {}
        prior = before.get('details', {}).get('data', {})
        later = after.get('details', {}).get('data', {})
        field, value = next(iter(effect['parameters']['settings'].items()))
        old, actual = prior.get('known_current_settings', {}).get(field), later.get('known_current_settings', {}).get(field)
        same_identity = prior.get('team_id') == later.get('team_id') == effect['parameters']['team_id'] and prior.get('name') == later.get('name') and prior.get('reciprocal_owner_matches') is True and later.get('reciprocal_owner_matches') is True
        unchanged_other_settings = bool(prior.get('known_current_settings')) and {k:v for k,v in prior.get('known_current_settings', {}).items() if k != field} == {k:v for k,v in later.get('known_current_settings', {}).items() if k != field}
        readback_received = before.get('outcome') == after.get('outcome') == 'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED'
        native_returned = observed.get('outcome') == 'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED'
        projection_checked = observed.get('details', {}).get('full_projection_matches') is True and observed.get('details', {}).get('original_gameplan_unchanged') is True
        confirmed = native_returned and projection_checked and readback_received and same_identity and old is not None and old != value and actual == value and unchanged_other_settings
        # This compares separate real sessions; simulated data must never be fed here.
        verdict = {'action_id': effect['action_id'], 'field': field, 'before': old, 'requested': value, 'independent_after': actual, 'same_identity': same_identity, 'other_known_settings_unchanged': unchanged_other_settings, 'native_return_observed': native_returned, 'in_function_full_projection_matches': projection_checked, 'status': 'REAL_NATIVE_EFFECT_VERIFIED' if confirmed else 'ALREADY_AT_TARGET_NOT_NEW_EFFECT' if old == actual == value else 'EXECUTED_EFFECT_UNVERIFIED' if observed else 'NOT_EXECUTED_OR_RESULT_UNKNOWN', 'UI_correspondence': 'UNKNOWN_NOT_OBSERVED', 'save_reload': 'NOT_STUDIED', 'automatic_second_submission': False}
    scout_verdict = None
    if effects and effects[0]['action_id'] == 'SCOUT_ASSIGN_TARGETS':
        effect = effects[0]
        observed = records.get(effect['case_id'], {}).get('result', {}).get('native_result') or {}
        before = (records.get('scout_before', {}).get('result', {}).get('native_result') or {}).get('details', {})
        after = (records.get('scout_after', {}).get('result', {}).get('native_result') or {}).get('details', {})
        previous, current = before.get('goals', []), after.get('goals', [])
        before_count, after_count = before.get('num_existing_goals'), after.get('num_existing_goals')
        appended = current[before_count] if isinstance(before_count, int) and before_count < len(current) else {}
        actual_ids = [t.get('player_id') for t in appended.get('targets', [])]
        identities_match = before.get('team_id') == after.get('team_id') == effect['parameters']['team_id']
        unchanged_old = identities_match and isinstance(before_count, int) and len(previous) == before_count and previous == current[:before_count]
        trips_unchanged = identities_match and before.get('remaining_trips_raw') == after.get('remaining_trips_raw')
        accepted = observed.get('outcome') == 'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED'
        verified = accepted and isinstance(before_count, int) and after_count == before_count+1 and actual_ids == effect['parameters']['player_ids'] and unchanged_old and trips_unchanged
        rejected = observed.get('outcome') == 'REJECTED_BY_GAME'
        scout_verdict = {'action_id': effect['action_id'], 'exact_request': effect['parameters'], 'native_append_result': observed.get('details', {}).get('native_append_result'), 'before_goals': before_count, 'after_goals': after_count, 'old_goals_unchanged': unchanged_old, 'trip_budget_unchanged': trips_unchanged, 'status': 'REAL_NATIVE_EFFECT_VERIFIED' if verified else 'REJECTED_BY_GAME' if rejected else 'EXECUTED_EFFECT_UNVERIFIED', 'rejection_unchanged_state_verified': rejected and unchanged_old and before_count == after_count and trips_unchanged, 'automatic_second_submission': False}
    write(runtime/'sequence-summary.json', {'batch_sha256': digest(batch_file), 'cases': records, 'coach_effect': verdict, 'scout_effect': scout_verdict})
    print(json.dumps({'summary': str(runtime/'sequence-summary.json'), 'coach_effect': verdict, 'scout_effect': scout_verdict}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('--requests', required=True)
    prep.add_argument('--directory', required=True)
    run = sub.add_parser('execute-case')
    run.add_argument('--batch', required=True)
    run.add_argument('--approval', required=True)
    run.add_argument('--case', required=True)
    run.add_argument('--runtime', required=True)
    ordered = sub.add_parser('execute-sequence')
    ordered.add_argument('--batch', required=True)
    ordered.add_argument('--approval', required=True)
    ordered.add_argument('--runtime', required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.requests, args.directory)
    elif args.command == 'execute-case':
        execute(args.batch, args.approval, args.case, args.runtime)
    else:
        sequence(args.batch, args.approval, args.runtime)


if __name__ == '__main__':
    main()
