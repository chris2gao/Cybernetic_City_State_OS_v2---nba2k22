"""Durable per-task workspace; a model window is only a disposable reader."""
import base64
import json
import re

from source import PRMSError, canonical, digest, safe_path
from catalog import discover_g1
from context import plan_context, human_choice


def normalize_task_context(payload, identity):
    from state import identifier
    task_id = identifier(payload.get('task_id'))
    plan, spec = payload.get('task_plan'), payload.get('load_spec')
    if not isinstance(plan, dict) or not isinstance(spec, dict):
        raise PRMSError('REJECTED', 'task plan and load specification required')
    if not isinstance(plan.get('objective'), str) or not plan['objective'].strip():
        raise PRMSError('REJECTED', 'durable task objective required')
    for name in ('plan', 'progress', 'open_items', 'next_steps', 'human_decision_refs'):
        if not isinstance(plan.get(name), list):
            raise PRMSError('REJECTED', 'task plan requires explicit ' + name)
    if (not isinstance(spec.get('core_repository'), str) or not spec['core_repository']
            or not isinstance(spec.get('core_commit'), str) or not re.fullmatch('[0-9a-f]{40}', spec['core_commit'])
            or spec.get('role_type') != identity['definition']['role_type_id']
            or not isinstance(spec.get('memory_choice_ref'), str) or not spec['memory_choice_ref']):
        raise PRMSError('REJECTED', 'frozen Core source, role and retained Human memory instruction required')
    for name in ('actions', 'required_paths', 'optional_paths', 'selected_paths', 'selected_event_ids'):
        if not isinstance(spec.get(name, []), list) or not all(isinstance(x, str) for x in spec.get(name, [])):
            raise PRMSError('REJECTED', 'load specification requires lists of strings')
    for path in spec.get('required_paths', []) + spec.get('optional_paths', []):
        safe_path(path)
    if not set(spec.get('selected_paths', [])) <= set(spec.get('optional_paths', [])):
        raise PRMSError('REJECTED', 'selected memory must belong to disclosed optional paths')
    from depth import DEPTHS
    if spec.get('history_depth', 'L3') not in DEPTHS:
        raise PRMSError('REJECTED', 'unknown history depth')
    return {'schema_version': 'prms.task_context.v1', 'task_id': task_id,
            'task_plan': json.loads(canonical(plan)), 'load_spec': json.loads(canonical(spec))}


def read_task_context(snapshot, role_id, task_id):
    from state import identifier
    prefix = f'roles/{identifier(role_id)}/tasks/{identifier(task_id)}/'
    pointer_path = prefix + 'CURRENT.json'
    if pointer_path not in snapshot:
        raise PRMSError('SOURCE_MISSING', 'no durable context for selected task')
    pointer = json.loads(snapshot[pointer_path])
    path = pointer.get('context_ref', '')
    if (pointer.get('role_id') != role_id or pointer.get('task_id') != task_id
            or not path.startswith(prefix + 'contexts/') or path not in snapshot):
        raise PRMSError('SOURCE_MISSING', 'task context pointer is missing or inconsistent')
    safe_path(path)
    record = json.loads(snapshot[path])
    identity = json.loads(snapshot[f'roles/{role_id}/identity.json'])
    normalized = normalize_task_context(record, identity)
    if (normalized['task_id'] != task_id or record.get('role_id') != role_id
            or record.get('state_version') != pointer.get('state_version')):
        raise PRMSError('REJECTED', 'task context identity differs from request')
    checkpoint = pointer.get('checkpoint_ref', '')
    if (not checkpoint.startswith(f'roles/{role_id}/checkpoints/') or checkpoint not in snapshot):
        raise PRMSError('SOURCE_MISSING', 'task checkpoint unavailable')
    safe_path(checkpoint)
    return {'pointer': pointer, 'record': record, 'source_objects': [
        {'path': pointer_path, 'sha256': digest(snapshot[pointer_path])},
        {'path': path, 'sha256': digest(snapshot[path])}], 'checkpoint': json.loads(snapshot[checkpoint])}


def list_task_contexts(store, role_id):
    from state import identifier
    head = store.head()
    snapshot = store.snapshot(head)
    prefix = f'roles/{identifier(role_id)}/tasks/'
    tasks = []
    for path in sorted(snapshot):
        if path.startswith(prefix) and path.endswith('/CURRENT.json'):
            task_id = path[len(prefix):].split('/')[0]
            context = read_task_context(snapshot, role_id, task_id)
            plan = context['record']['task_plan']
            tasks.append({'task_id': task_id, 'objective': plan['objective'], 'open_items': plan['open_items'],
                          'next_steps': plan['next_steps'], 'context_ref': context['pointer']['context_ref']})
    return {'state_commit': head, 'role_id': role_id, 'tasks': tasks, 'scope': 'DURABLE_TASK_CONTEXTS_ONLY'}


def resume_task(gate, role_id, task_id, core_source, *, session_id, budget_bytes):
    """Restore a task into a new session without rewriting its plan or authority."""
    from recovery import create_recovery_package
    head = gate.store.head()
    task = read_task_context(gate.store.snapshot(head), role_id, task_id)
    spec = task['record']['load_spec']
    if core_source.commit != spec['core_commit'] or core_source.repository != spec['core_repository']:
        raise PRMSError('SUMMARY_STALE', 'task requires its recorded Core source; upgrades must be explicit')
    plan = plan_context(core_source, discover_g1(core_source), session_id=session_id,
        role=spec['role_type'], task_id=task_id, stage=spec.get('stage'), actions=spec.get('actions', []),
        required_paths=spec.get('required_paths', []), optional_paths=spec.get('optional_paths', []))
    # Human's saved task instruction governs selection; a new workbench does not
    # erase it. Rebind its context-only choice to this session, never execution.
    choice = human_choice(plan, session_id=session_id, selected_paths=spec.get('selected_paths', []),
        decision_source=spec['memory_choice_ref'])
    history = {'session_id': session_id, 'depth': spec.get('history_depth', 'L3'),
        'selected_event_ids': spec.get('selected_event_ids', []), 'decision_source': spec['memory_choice_ref']}
    package = create_recovery_package(gate, role_id, core_source, core_plan=plan, core_choice=choice,
        history_choice=history, budget_bytes=budget_bytes)
    if head != package['state_commit']:
        raise PRMSError('VERSION_CONFLICT', 'task moved while resuming; reread instead of mixing snapshots')
    return {'package': package, 'core_plan': plan, 'core_choice': choice, 'history_choice': history,
        'state_effect': 'READ_ONLY', 'selection_basis': 'RETAINED_HUMAN_TASK_INSTRUCTION',
        'previous_window_required': False}


def render_workbench(bundle):
    """Readable actual material to open/paste in a new workbench via Human relay."""
    package = bundle['package']
    lines = [f"# Task {bundle['task_id']} — session {bundle['target_session_id']}",
        '', f"Context status: {package['status']}. State: {bundle['state_commit']}.",
        'This file restores context only. It does not claim model comprehension, takeover or new execution authority.', '']
    context = package['role_current'].get('task_context')
    if context:
        lines += ['## Saved task plan and progress', '', '```json',
                  json.dumps(context['record']['task_plan'], ensure_ascii=False, indent=2), '```', '']
    lines += ['## Role and current state', '', '```json', json.dumps({
        k: v for k, v in package['role_current'].items() if k != 'task_context'}, ensure_ascii=False, indent=2), '```', '',
        '## Discovered mechanism directory', '', '```json',
        json.dumps(package['core_context']['directory_cards'], ensure_ascii=False, indent=2), '```', '']
    lines += ['## Gaps and warnings', '', json.dumps({'warnings': package['warnings'],
        'missing_history_ids': package['missing_history_ids'], 'excluded_events': package['excluded_events'],
        'unloaded_sources': package['core_context']['required_not_loaded']}, ensure_ascii=False), '',
        '## Durable task facts and decisions', '']
    for item in package['selected_events']:
        event = item['event']
        lines += [f"### {event['event_id']} ({event['kind']})", '',
                  json.dumps(event, ensure_ascii=False, indent=2), '']
    if package['optional_summaries']:
        lines += ['## Selected history summaries', '', '```json',
                  json.dumps(package['optional_summaries'], ensure_ascii=False, indent=2), '```', '']
    audit = package['role_history_audit']
    if audit:
        lines += ['## Explicitly selected full role history', '', f"Audit status: {audit['status']}", '']
        for item in audit['items']:
            raw = base64.b64decode(item['content'])
            try:
                content = raw.decode('utf-8')
            except UnicodeDecodeError:
                content = 'Non-text original bytes (base64): ' + item['content']
            lines += [f"### {item['path']}", '', content, '']
    lines += ['## Loaded Core bodies', '']
    for body in package['core_context']['full_bodies']:
        proof = body['source']
        lines += [f"### {proof['path']} @ {proof['commit']}", '', body['text'], '']
    return '\n'.join(lines)
