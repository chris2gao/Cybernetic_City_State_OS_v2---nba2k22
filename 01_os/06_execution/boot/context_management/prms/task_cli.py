"""Save task context or resume it into a fresh, readable Human-relay workbench.

Writes are limited to an existing isolated test state. Resume/list are read-only
state operations. No chat, service, credentials or repository is created.
"""
import argparse
import json
from pathlib import Path
import sys

from source import GitSource, PRMSError, canonical
from state import LocalGitState, WriterGate
from task_context import read_task_context, list_task_contexts, resume_task, render_workbench
from handoff import export_handoff, receiver_request


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['save', 'list', 'resume'])
    parser.add_argument('--state-root', required=True)
    parser.add_argument('--role', required=True)
    parser.add_argument('--task')
    parser.add_argument('--session')
    parser.add_argument('--payload')
    parser.add_argument('--operation-id')
    parser.add_argument('--isolated-test-only', action='store_true')
    parser.add_argument('--core-root')
    parser.add_argument('--budget-bytes', type=int, default=1_000_000)
    parser.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    try:
        if Path(args.output).exists():
            raise PRMSError('REJECTED', 'output must be a new file or workbench directory')
        store = LocalGitState(args.state_root)
        gate = WriterGate(store)
        if args.command == 'save':
            if not args.isolated_test_only or not args.session or not args.payload or not args.operation_id:
                raise PRMSError('REJECTED', 'save requires an isolated test host, session, payload and operation ID')
            payload = json.loads(Path(args.payload).read_text(encoding='utf-8'))
            head = store.head()
            current = gate.recover(args.role, head)['current']
            caller = gate.open_isolated_session(args.session, [args.role], allowed_tasks=[payload.get('task_id')],
                allowed_operations=['SAVE_TASK_CONTEXT'])
            result = gate.apply(caller, args.role, operation_id=args.operation_id, expected_head=head,
                expected_version=current['state_version'], expected_epoch=current['owner_epoch'],
                kind='SAVE_TASK_CONTEXT', payload=payload)
        elif args.command == 'list':
            result = list_task_contexts(store, args.role)
        else:
            if not args.core_root or not args.session or not args.task:
                raise PRMSError('REJECTED', 'resume requires Core root, current session and selected task')
            context = read_task_context(store.snapshot(), args.role, args.task)
            spec = context['record']['load_spec']
            source = GitSource(args.core_root, spec['core_commit'], spec['core_repository'])
            result = resume_task(gate, args.role, args.task, source, session_id=args.session, budget_bytes=args.budget_bytes)
            bundle = export_handoff(gate, source, result['package'], handoff_id=args.session,
                **{k: result[k] for k in ('core_plan', 'core_choice', 'history_choice')})
            # Create a fresh workbench. Existing artifacts cannot be silently replaced.
            output = Path(args.output)
            output.mkdir(parents=True, exist_ok=False)
            artifacts = {'recovery.json': result['package'], 'plan.json': result['core_plan'],
                'choice.json': result['core_choice'], 'history-choice.json': result['history_choice'],
                'bundle.json': bundle, 'receiver-request.json': receiver_request(bundle)}
            for name, value in artifacts.items():
                (output / name).write_bytes(canonical(value) + b'\n')
            (output / 'CONTEXT.md').write_text(render_workbench(bundle), encoding='utf-8')
            print(json.dumps({'status': result['package']['status'], 'output': str(output),
                'workbench': str(output / 'CONTEXT.md'), 'previous_window_required': False,
                'state_effect': 'READ_ONLY', 'automatic_injection': False}))
            return 0
        with Path(args.output).open('xb') as stream:
            stream.write(canonical(result) + b'\n')
        print(json.dumps({'status': result.get('status', 'DISCOVERED_DURABLE_TASKS'), 'output': args.output}))
        return 0
    except (PRMSError, KeyError, ValueError, TypeError, OSError) as exc:
        print(json.dumps({'status': getattr(exc, 'status', 'REJECTED'), 'detail': str(exc)}, ensure_ascii=True))
        return 2


if __name__ == '__main__':
    sys.exit(main())
