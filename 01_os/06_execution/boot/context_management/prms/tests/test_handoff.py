import base64
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import GitSource, PRMSError, canonical, digest
from catalog import discover_g1
from context import plan_context, human_choice
from recovery import create_recovery_package
from handoff import export_handoff, receiver_request, receive_handoff, verify_receiver_ack
from test_state import setup, apply

ROOT = Path(__file__).resolve().parents[6]
BASE = '446ca66ad48831f5fcdb1af18f37d07619e048c4'


@pytest.fixture
def transfer(setup):
    store, gate, caller, _ = setup
    apply(store, gate, caller, 'assignment', 'ASSIGN', {'assignment_id': 'a', 'task_id': 'PRMS', 'human_authority_ref': 'fixture'})
    apply(store, gate, caller, 'decision', 'APPEND', {'event_id': 'decision', 'task_id': 'PRMS',
        'kind': 'HUMAN_DECISION', 'text': 'Q52=B; fixture only',
        'source_refs': [{'repository': 'fixture/source', 'path': 'Human.md', 'commit': 'a' * 40}]})
    apply(store, gate, caller, 'cp', 'CHECKPOINT', {'task_id': 'PRMS', 'open_items': ['independent review']})
    source = GitSource(ROOT, BASE, 'fixture/core')
    plan = plan_context(source, discover_g1(source), session_id='receiver', role='engineer', task_id='PRMS')
    choice = human_choice(plan, session_id='receiver', selected_paths=[], decision_source='fixture Human relay')
    history = {'session_id': 'receiver', 'depth': 'L3', 'selected_event_ids': [], 'decision_source': 'fixture'}
    inputs = dict(core_plan=plan, core_choice=choice, history_choice=history)
    package = create_recovery_package(gate, 'engineer', source, **inputs, budget_bytes=1_000_000)
    bundle = export_handoff(gate, source, package, handoff_id='h1', **inputs)
    receive = dict(expected_request=receiver_request(bundle), receiver_session_id='receiver',
                   max_bundle_bytes=4_000_000, **inputs)
    return store, gate, caller, source, package, bundle, receive


def test_deterministic_human_relay_exports_exact_bytes_and_verifies_ack(transfer):
    store, gate, _, source, package, bundle, inputs = transfer
    before = store.head()
    export_inputs = {k: inputs[k] for k in ('core_plan', 'core_choice', 'history_choice')}
    assert export_handoff(gate, source, package, handoff_id='h1', **export_inputs) == bundle
    for item in bundle['loaded_objects']:
        raw = base64.b64decode(item['content_base64'])
        assert len(raw) == item['bytes'] and digest(raw) == item['sha256']
        actual = source.read(item['path'])[0] if item['kind'] == 'CORE_BODY' else store.snapshot(before)[item['path']]
        assert raw == actual
    ack = receive_handoff(gate, source, bundle, **inputs)
    assert ack['context_status'] == 'READY'
    assert ack['automatic_injection'] is False and ack['model_understanding'] == 'NOT_OBSERVABLE'
    assert ack['model_identity'] == 'NOT_AUTHENTICATED_BY_FILE_CONTRACT'
    assert verify_receiver_ack(gate, source, bundle, ack, **inputs)['status'] == 'VERIFIED_RECEIVER_FILE_RECORD'
    assert store.head() == before
    ack['receiver_session_id'] = 'other'
    with pytest.raises(PRMSError, match='REJECTED'):
        verify_receiver_ack(gate, source, bundle, ack, **inputs)


@pytest.mark.parametrize('change', ['body', 'missing', 'role', 'choice'])
def test_recomputed_bundle_hash_cannot_replace_actual_sources_or_host_choices(transfer, change):
    _, gate, _, source, _, original, inputs = transfer
    bundle = deepcopy(original)
    if change == 'body':
        bundle['loaded_objects'][0]['content_base64'] = base64.b64encode(b'forged').decode()
        bundle['loaded_objects'][0]['sha256'] = digest(b'forged')
        bundle['loaded_objects'][0]['bytes'] = 6
    elif change == 'missing':
        bundle['loaded_objects'].pop()
    elif change == 'role':
        bundle['role_id'] = 'other'
    else:
        bundle['core_choice']['decision_source'] = 'substituted Human decision'
    bundle.pop('bundle_digest')
    bundle['bundle_digest'] = digest(canonical(bundle))
    with pytest.raises(PRMSError):
        receive_handoff(gate, source, bundle, **inputs)
    # Even if an untrusted bundle persuades a caller to replace its request hash,
    # actual source reassembly and separately held choices reject the substitution.
    with pytest.raises(PRMSError):
        receive_handoff(gate, source, bundle, **{**inputs, 'expected_request': receiver_request(bundle)})


def test_wrong_session_stale_state_and_receiver_budget_are_rejected(transfer):
    store, gate, caller, source, _, bundle, inputs = transfer
    for changed, error in [({'receiver_session_id': 'other'}, 'AUTHORITY_UNVERIFIED'),
                           ({'max_bundle_bytes': len(canonical(bundle)) - 1}, 'CONTEXT_BUDGET_INSUFFICIENT')]:
        with pytest.raises(PRMSError, match=error):
            receive_handoff(gate, source, bundle, **{**inputs, **changed})
    apply(store, gate, caller, 'new-cp', 'CHECKPOINT', {'task_id': 'PRMS'})
    with pytest.raises(PRMSError, match='VERSION_CONFLICT'):
        receive_handoff(gate, source, bundle, **inputs)


def test_missing_history_is_disclosed_and_blocked_context_cannot_be_exported(transfer):
    _, gate, _, source, _, _, inputs = transfer
    shared = {k: inputs[k] for k in ('core_plan', 'core_choice', 'history_choice')}
    shared['history_choice'] = {**shared['history_choice'], 'selected_event_ids': ['not-durable']}
    package = create_recovery_package(gate, 'engineer', source, **shared, budget_bytes=1_000_000)
    assert package['status'] == 'PARTIAL'
    bundle = export_handoff(gate, source, package, handoff_id='partial', **shared)
    ack = receive_handoff(gate, source, bundle, expected_request=receiver_request(bundle),
        receiver_session_id='receiver', max_bundle_bytes=4_000_000, **shared)
    assert ack['context_status'] == 'PARTIAL' and ack['missing_history_ids'] == ['not-durable']
    assert 'SELECTED_HISTORY_NOT_DURABLE' in ack['warnings']
    blocked = create_recovery_package(gate, 'engineer', source, **shared, budget_bytes=1)
    with pytest.raises(PRMSError, match='REQUIRED_SOURCE_NOT_LOADED'):
        export_handoff(gate, source, blocked, handoff_id='blocked', **shared)


def test_cli_file_export_receive_and_ack_are_real_foreground_calls(transfer, tmp_path):
    store, _, _, source, package, _, inputs = transfer
    files = {'plan': inputs['core_plan'], 'choice': inputs['core_choice'],
             'history-choice': inputs['history_choice'], 'package': package}
    for name, value in files.items():
        (tmp_path / (name + '.json')).write_bytes(canonical(value))
    common = ['--core-root', str(ROOT), '--core-commit', source.commit, '--core-repository', source.repository,
        '--state-root', str(store.root), '--bundle', str(tmp_path / 'bundle.json'),
        '--receiver-request', str(tmp_path / 'request.json')]
    for name in ('plan', 'choice', 'history-choice'):
        common += ['--' + name, str(tmp_path / (name + '.json'))]
    cli = Path(__file__).resolve().parents[1] / 'handoff_cli.py'
    def call(command, *extra):
        return subprocess.run([sys.executable, '-B', str(cli), command, *common, *extra],
                              capture_output=True, text=True, encoding='utf-8')
    result = call('export', '--package', str(tmp_path / 'package.json'), '--handoff-id', 'cli-h1')
    assert result.returncode == 0, result.stdout + result.stderr
    raw = (tmp_path / 'bundle.json').read_bytes()
    assert call('export', '--package', str(tmp_path / 'package.json'), '--handoff-id', 'cli-h1').returncode == 2
    assert (tmp_path / 'bundle.json').read_bytes() == raw
    args = ['--ack', str(tmp_path / 'ack.json')]
    assert call('receive', *args, '--receiver-session', 'wrong').returncode == 2
    assert not (tmp_path / 'ack.json').exists()
    result = call('receive', *args, '--receiver-session', 'receiver')
    assert result.returncode == 0, result.stdout + result.stderr
    result = call('verify-ack', *args, '--receiver-session', 'receiver')
    assert result.returncode == 0, result.stdout + result.stderr
    ack = json.loads((tmp_path / 'ack.json').read_text(encoding='utf-8'))
    assert ack['automatic_injection'] is False and ack['owner_takeover_performed'] is False
