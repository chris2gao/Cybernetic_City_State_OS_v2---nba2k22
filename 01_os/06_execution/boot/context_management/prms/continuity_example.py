"""Actual isolated Git + fresh-process task continuity, all content synthetic."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from source import GitSource, canonical, digest
from state import LocalGitState, WriterGate
from handoff import receive_handoff


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', required=True)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    candidate = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip()
    with tempfile.TemporaryDirectory(prefix='prms-continuity-') as temporary:
        parent = Path(temporary)
        store = LocalGitState.initialize_isolated(parent / 'state.git', sandbox_parent=parent)
        gate = WriterGate(store)
        caller = gate.open_isolated_session('synthetic-owner', ['engineer'])
        gate.apply(caller, 'engineer', operation_id='register', expected_head=store.head(),
            expected_version=0, expected_epoch=0, kind='REGISTER', payload={'definition': {
                'role_type_id': 'engineer', 'version': '1'}, 'domain_id': 'test', 'state_repository_id': 'isolated'})
        def apply(op, kind, payload):
            current = gate.recover('engineer')['current']
            return gate.apply(caller, 'engineer', operation_id=op, expected_head=store.head(),
                expected_version=current['state_version'], expected_epoch=current['owner_epoch'], kind=kind, payload=payload)
        saves = []
        for task in ('A', 'B'):
            apply('assign-' + task, 'ASSIGN', {'assignment_id': task, 'task_id': task, 'human_authority_ref': 'SYNTHETIC Human instruction'})
            apply('decision-' + task, 'APPEND', {'event_id': task, 'task_id': task, 'kind': 'HUMAN_DECISION',
                'text': 'SYNTHETIC approved plan ' + task,
                'source_refs': [{'repository': 'fixture', 'path': 'Human.md', 'commit': 'a' * 40}]})
            receipt = apply('save-' + task, 'SAVE_TASK_CONTEXT', {'task_id': task, 'task_plan': {
                'objective': 'SYNTHETIC task ' + task, 'plan': ['design', 'implement', 'verify'],
                'progress': ['design saved'], 'open_items': ['implementation'], 'next_steps': ['continue task ' + task],
                'human_decision_refs': ['SYNTHETIC decision-' + task]}, 'load_spec': {
                'core_repository': 'fixture/core', 'core_commit': candidate, 'role_type': 'engineer',
                'memory_choice_ref': 'SYNTHETIC ongoing Human memory instruction', 'history_depth': 'L3'}})
            saves.append({'task_id': task, 'published_commit': receipt['authoritative_commit_sha']})
        frozen = store.head()
        outputs = []
        cli = Path(__file__).with_name('task_cli.py')
        for session in ('fresh-window-1', 'fresh-window-2'):
            output = parent / session
            process = subprocess.run([sys.executable, '-B', str(cli), 'resume', '--state-root', str(store.root),
                '--role', 'engineer', '--task', 'A', '--session', session, '--core-root', str(root), '--output', str(output)],
                capture_output=True)
            if process.returncode:
                raise RuntimeError('fresh-process task recovery failed: ' + process.stdout.decode('utf-8', 'replace'))
            read = lambda name: json.loads((output / name).read_text(encoding='utf-8'))
            package, bundle = read('recovery.json'), read('bundle.json')
            ack = receive_handoff(WriterGate(LocalGitState(store.root)), GitSource(root, candidate, 'fixture/core'), bundle,
                expected_request=read('receiver-request.json'), receiver_session_id=session,
                core_plan=read('plan.json'), core_choice=read('choice.json'), history_choice=read('history-choice.json'),
                max_bundle_bytes=4_000_000)
            task = package['role_current']['task_context']['record']['task_plan']
            facts = [x['event']['text'] for x in package['selected_events']]
            assert package['status'] == 'READY' and task['objective'] == 'SYNTHETIC task A'
            assert facts == ['SYNTHETIC approved plan A']
            assert package['role_current']['active_role_assignment_id'] == 'B'
            outputs.append({'session_id': session, 'context_status': package['status'], 'task_plan': task,
                'facts': facts, 'bundle_digest': bundle['bundle_digest'], 'ack_status': ack['status'],
                'loaded_source_proofs': [x['source'] for x in package['core_context']['full_bodies']],
                'context_markdown_sha256': digest((output / 'CONTEXT.md').read_bytes())})
        assert store.head() == frozen
        result = {'schema_version': 'prms.task_continuity_example.v1', 'candidate': candidate,
            'status': 'VERIFIED_ISOLATED_TASK_CONTINUITY', 'proof_scope': 'SYNTHETIC_REAL_GIT_AND_FRESH_PYTHON_PROCESSES',
            'content': 'SYNTHETIC_TEST_ONLY', 'explicit_saves_before_switch': saves, 'active_assignment': 'B',
            'resumed_task': 'A', 'state_commit': frozen, 'state_unchanged_by_recovery': True,
            'fresh_process_results': outputs, 'actual_model_window': 'NOT_RUN', 'automatic_injection': False}
        print(json.dumps(result, ensure_ascii=True))


if __name__ == '__main__':
    main()
