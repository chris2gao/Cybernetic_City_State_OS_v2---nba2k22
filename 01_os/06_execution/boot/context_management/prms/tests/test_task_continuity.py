import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import GitSource, PRMSError, canonical
from state import LocalGitState, WriterGate
from task_context import resume_task, list_task_contexts, read_task_context
from handoff import receive_handoff
from memory import copy_all_memory
from test_state import setup, apply

ROOT = Path(__file__).resolve().parents[6]
BASE = '446ca66ad48831f5fcdb1af18f37d07619e048c4'


def payload(task, text):
    return {'task_id': task, 'task_plan': {'objective': text, 'plan': ['model', 'implement', 'verify'],
        'progress': ['design approved'], 'open_items': ['finish implementation'],
        'next_steps': ['continue selected task'], 'human_decision_refs': ['fixture Human Q52=B']},
        'load_spec': {'core_repository': 'fixture/core', 'core_commit': BASE, 'role_type': 'engineer',
            'memory_choice_ref': 'Human ongoing task instruction; retain its loading scope',
            'required_paths': ['01_os/03_mechanisms/context_management/README.md'],
            'optional_paths': [], 'selected_paths': [], 'history_depth': 'L3'}}


def save_task(store, gate, caller, task, text):
    apply(store, gate, caller, 'assign-' + task, 'ASSIGN', {'assignment_id': task,
        'task_id': task, 'human_authority_ref': 'fixture Human task instruction'})
    apply(store, gate, caller, 'event-' + task, 'APPEND', {'event_id': task, 'task_id': task,
        'kind': 'HUMAN_DECISION', 'text': 'approved-' + task,
        'source_refs': [{'repository': 'fixture', 'path': 'Human.md', 'commit': 'a' * 40}]})
    return apply(store, gate, caller, 'save-' + task, 'SAVE_TASK_CONTEXT', payload(task, text))


def test_task_a_survives_switch_to_b_and_fresh_process_workbench(setup, tmp_path):
    store, gate, caller, _ = setup
    save_task(store, gate, caller, 'A', 'continue A after a window switch')
    save_task(store, gate, caller, 'B', 'unrelated B content must not load into A')
    before = store.head()
    frozen_a = read_task_context(store.snapshot(), 'engineer', 'A')
    assert gate.recover('engineer')['current']['assignment_id'] == 'B'
    assert {x['task_id'] for x in list_task_contexts(store, 'engineer')['tasks']} == {'A', 'B'}
    # Throw away the original gate and session capability. New processes need
    # only the durable store/role/task and new session, never the old chat.
    cli = Path(__file__).resolve().parents[1] / 'task_cli.py'
    outputs = []
    for session in ('new-window-1', 'new-window-2'):
        output = tmp_path / session
        result = subprocess.run([sys.executable, '-B', str(cli), 'resume', '--state-root', str(store.root),
            '--role', 'engineer', '--task', 'A', '--session', session, '--core-root', str(ROOT), '--output', str(output)],
            capture_output=True, text=True, encoding='utf-8')
        assert result.returncode == 0, result.stdout + result.stderr
        package = json.loads((output / 'recovery.json').read_text(encoding='utf-8'))
        assert package['status'] == 'READY'
        assert package['role_current']['task_context']['record']['task_plan']['objective'] == 'continue A after a window switch'
        assert package['role_current']['assignment']['task_id'] == 'A'
        assert package['role_current']['active_role_assignment_id'] == 'B'
        assert [x['event']['text'] for x in package['selected_events']] == ['approved-A']
        assert package['role_current']['task_context'] == frozen_a
        workbench = (output / 'CONTEXT.md').read_text(encoding='utf-8')
        assert 'continue A after a window switch' in workbench and 'approved-A' in workbench
        assert 'unrelated B content must not load into A' not in workbench
        outputs.append(output)
    # Receiver reads the second workbench's exact files; no implicit session reuse.
    output = outputs[-1]
    load = lambda name: json.loads((output / name).read_text(encoding='utf-8'))
    fresh_gate = WriterGate(LocalGitState(store.root))
    ack = receive_handoff(fresh_gate, GitSource(ROOT, BASE, 'fixture/core'), load('bundle.json'),
        expected_request=load('receiver-request.json'), receiver_session_id='new-window-2',
        core_plan=load('plan.json'), core_choice=load('choice.json'), history_choice=load('history-choice.json'),
        max_bundle_bytes=4_000_000)
    assert ack['context_status'] == 'READY' and ack['model_understanding'] == 'NOT_OBSERVABLE'
    assert store.head() == before


def test_latest_durable_task_event_is_loaded_even_after_checkpoint_and_switch(setup):
    store, gate, caller, _ = setup
    save_task(store, gate, caller, 'A', 'A objective')
    apply(store, gate, caller, 'later-A', 'APPEND', {'event_id': 'later-A', 'task_id': 'A',
        'kind': 'OBSERVATION', 'text': 'later durable fact',
        'source_refs': [{'repository': 'fixture', 'path': 'result.md', 'commit': 'a' * 40}]})
    save_task(store, gate, caller, 'B', 'B objective')
    result = resume_task(WriterGate(LocalGitState(store.root)), 'engineer', 'A', GitSource(ROOT, BASE, 'fixture/core'),
        session_id='new', budget_bytes=1_000_000)
    assert 'later durable fact' in [x['event']['text'] for x in result['package']['selected_events']]
    assert 'CHECKPOINT_LAGS_DURABLE_EVENTS' in result['package']['warnings']
    assert result['package']['status'] == 'PARTIAL'


def test_task_plan_revision_budget_and_missing_original_fail_explicitly(setup):
    store, gate, caller, _ = setup
    save_task(store, gate, caller, 'A', 'first objective')
    apply(store, gate, caller, 'revise-A', 'SAVE_TASK_CONTEXT', payload('A', 'Human revised objective'))
    source = GitSource(ROOT, BASE, 'fixture/core')
    result = resume_task(gate, 'engineer', 'A', source, session_id='new', budget_bytes=1_000_000)
    assert result['package']['role_current']['task_context']['record']['task_plan']['objective'] == 'Human revised objective'
    assert 'roles/engineer/tasks/A/contexts/save-A.json' in store.snapshot()
    assert resume_task(gate, 'engineer', 'A', source, session_id='small', budget_bytes=1)['package']['status'] == 'BLOCKED'
    with pytest.raises(PRMSError, match='SOURCE_MISSING'):
        resume_task(gate, 'engineer', 'missing', source, session_id='new', budget_bytes=1_000_000)
    snapshot = store.snapshot()
    pointer = json.loads(snapshot['roles/engineer/tasks/A/CURRENT.json'])
    pointer['context_ref'] = 'roles/engineer/tasks/A/contexts/missing.json'
    store.commit(store.head(), {'roles/engineer/tasks/A/CURRENT.json': canonical(pointer)}, 'corrupt-test-pointer')
    with pytest.raises(PRMSError, match='SOURCE_MISSING'):
        resume_task(gate, 'engineer', 'A', source, session_id='new', budget_bytes=1_000_000)


def test_full_copy_retains_usable_task_context_without_transferring_assignments(setup):
    store, gate, caller, _ = setup
    save_task(store, gate, caller, 'A', 'durable A plan')
    frozen = store.head()
    copier = gate.open_isolated_session('copier', ['copied'], allowed_copy_scopes=[{
        'source_role': 'engineer', 'target_role': 'copied', 'source_commit': frozen, 'approval_ref': 'Human-copy'}])
    copy_all_memory(store, gate, copier, 'engineer', 'copied', source_head=frozen,
        operation_id='copy-tasks', target_expected_head=frozen, scope_approval_ref='Human-copy')
    result = resume_task(gate, 'copied', 'A', GitSource(ROOT, BASE, 'fixture/core'),
        session_id='new-copy-window', budget_bytes=1_000_000)
    package = result['package']
    assert package['role_current']['task_context']['record']['task_plan']['objective'] == 'durable A plan'
    assert package['role_current']['assignment'] is None
    assert package['role_current']['task_context']['pointer']['assignment_id'] is None
    assert [x['event']['text'] for x in package['selected_events']] == ['approved-A']
    assert 'TASK_ASSIGNMENT_MISSING' in package['warnings']
