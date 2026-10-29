"""Deterministic recovery artifacts for explicit Human relay, never auto-send.

This is a context-file contract, not a second formal OS communication protocol.
Formal task dispatch still uses communication_system. Receipt generation proves
source/byte validation by this receiver tool, not model identity or comprehension.
The host/Human retains the expected request separately from the relayed bundle.
"""
import base64
from copy import deepcopy
import re

from source import canonical, digest, PRMSError
from recovery import verify_window_recovery
from state import identifier


def _payload(gate, core_source, package, *, handoff_id, core_plan, core_choice, history_choice):
    identifier(handoff_id)
    verify_window_recovery(gate, core_source, package, core_plan=core_plan,
        core_choice=core_choice, history_choice=history_choice)
    if package['status'] == 'BLOCKED':
        raise PRMSError('REQUIRED_SOURCE_NOT_LOADED', 'cannot export a blocked recovery as deliverable context')
    objects = []
    for body in package['core_context']['full_bodies']:
        raw, proof = core_source.read(body['source']['path'], body['source']['blob'])
        objects.append({'kind': 'CORE_BODY', 'repository': core_source.repository,
            'commit': core_source.commit, 'path': proof['path'], 'sha256': digest(raw),
            'bytes': len(raw), 'content_base64': base64.b64encode(raw).decode('ascii')})
    snapshot = gate.store.snapshot(package['state_commit'])
    prefix = f"roles/{package['role_id']}/"
    paths = {prefix + name for name in ('identity.json', 'CURRENT.json', 'owner.json')}
    current = package['role_current']['current']
    if current.get('assignment_id'):
        paths.add(prefix + f"assignments/{current['assignment_id']}.json")
    if current.get('checkpoint'):
        paths.add(prefix + f"checkpoints/{current['checkpoint']}.json")
    paths.update(item['path'] for item in package['selected_events'])
    task = package['role_current'].get('task_context')
    if task:
        paths.update(item['path'] for item in task['source_objects'])
        paths.add(task['pointer']['checkpoint_ref'])
        if task['pointer'].get('assignment_id'):
            paths.add(prefix + f"assignments/{task['pointer']['assignment_id']}.json")
    for path in sorted(paths):
        if path not in snapshot:
            raise PRMSError('SOURCE_MISSING', 'handoff source object missing')
        raw = snapshot[path]
        objects.append({'kind': 'ROLE_STATE', 'commit': package['state_commit'], 'path': path,
            'sha256': digest(raw), 'bytes': len(raw), 'content_base64': base64.b64encode(raw).decode('ascii')})
    if gate.store.head() != package['state_commit']:
        raise PRMSError('VERSION_CONFLICT', 'state changed during handoff source validation')
    return {'schema_version': 'prms.human_relay_bundle.v1', 'handoff_id': handoff_id,
        'delivery_mode': 'HUMAN_RELAY', 'target_session_id': package['session_id'],
        'role_id': package['role_id'], 'task_id': package['task_id'],
        'core_source_commit': core_source.commit, 'state_commit': package['state_commit'],
        'core_plan': deepcopy(core_plan), 'core_choice': deepcopy(core_choice),
        'history_choice': deepcopy(history_choice), 'package': deepcopy(package), 'loaded_objects': objects,
        'authority_effect': 'CONTEXT_ONLY', 'automatic_injection': False,
        'model_understanding': 'NOT_OBSERVABLE', 'action_authorized': False}


def export_handoff(gate, core_source, package, *, handoff_id, core_plan, core_choice, history_choice):
    payload = _payload(gate, core_source, package, handoff_id=handoff_id,
        core_plan=core_plan, core_choice=core_choice, history_choice=history_choice)
    return {**payload, 'bundle_digest': digest(canonical(payload))}


def receiver_request(bundle):
    """Sender retains this binding and relays it through the intended Human route.

    A digest is integrity data, not a signature or independent authorization.
    Receiver must use its own retained request, not derive it from an input bundle.
    """
    return {'schema_version': 'prms.receiver_request.v1', 'handoff_id': bundle['handoff_id'],
        'target_session_id': bundle['target_session_id'], 'role_id': bundle['role_id'],
        'task_id': bundle['task_id'], 'bundle_digest': bundle['bundle_digest'],
        'core_source_commit': bundle['core_source_commit'], 'state_commit': bundle['state_commit'],
        'plan_digest': bundle['core_plan']['plan_digest'],
        'core_choice_digest': digest(canonical(bundle['core_choice'])),
        'history_choice_digest': digest(canonical(bundle['history_choice']))}


def receive_handoff(gate, core_source, bundle, *, expected_request, receiver_session_id,
                    core_plan, core_choice, history_choice, max_bundle_bytes):
    """Read/verify exact sources and produce a file receipt; never claim delivery.

    Host supplies the current receiver identity and retained plan/choice. In the
    CLI those are explicit Human-relayed claims and are not authenticated model
    identities. State ref freshness is checked against the actual backend now.
    """
    identifier(receiver_session_id)
    if type(max_bundle_bytes) is not int or max_bundle_bytes <= 0:
        raise PRMSError('REJECTED', 'positive receiver byte budget required')
    wire_bytes = len(canonical(bundle))
    if wire_bytes > max_bundle_bytes:
        raise PRMSError('CONTEXT_BUDGET_INSUFFICIENT', 'receiver cannot silently truncate bundle')
    unsigned = dict(bundle)
    claimed = unsigned.pop('bundle_digest', None)
    if not isinstance(claimed, str) or not re.fullmatch('[0-9a-f]{64}', claimed) or digest(canonical(unsigned)) != claimed:
        raise PRMSError('REJECTED', 'handoff bytes changed')
    if receiver_request(bundle) != expected_request:
        raise PRMSError('AUTHORITY_UNVERIFIED', 'handoff differs from separately retained receiver request')
    if receiver_session_id != expected_request['target_session_id'] or receiver_session_id != core_plan['session_id']:
        raise PRMSError('AUTHORITY_UNVERIFIED', 'handoff addressed to a different current session')
    expected = export_handoff(gate, core_source, bundle['package'], handoff_id=bundle['handoff_id'],
        core_plan=core_plan, core_choice=core_choice, history_choice=history_choice)
    if canonical(bundle) != canonical(expected):
        raise PRMSError('REJECTED', 'handoff objects or choices unsupported by actual source reads')
    manifests = [{k: value for k, value in item.items() if k != 'content_base64'} for item in bundle['loaded_objects']]
    return {'schema_version': 'prms.receiver_ack.v1', 'handoff_id': bundle['handoff_id'],
        'bundle_digest': claimed, 'receiver_request_digest': digest(canonical(expected_request)),
        'receiver_session_id': receiver_session_id, 'role_id': bundle['role_id'], 'task_id': bundle['task_id'],
        'core_source_commit': bundle['core_source_commit'], 'state_commit': bundle['state_commit'],
        'plan_digest': core_plan['plan_digest'], 'core_choice_digest': digest(canonical(core_choice)),
        'history_choice_digest': digest(canonical(history_choice)), 'loaded_objects': manifests,
        'wire_bytes': wire_bytes, 'context_status': bundle['package']['status'],
        'warnings': deepcopy(bundle['package']['warnings']),
        'missing_history_ids': list(bundle['package']['missing_history_ids']),
        'status': 'VERIFIED_CONTEXT_FILE_RECEIPT', 'delivery_mode': 'HUMAN_RELAY',
        'model_identity': 'NOT_AUTHENTICATED_BY_FILE_CONTRACT', 'model_understanding': 'NOT_OBSERVABLE',
        'automatic_injection': False, 'owner_takeover_performed': False, 'action_authorized': False}


def verify_receiver_ack(gate, core_source, bundle, ack, **receiver_inputs):
    expected = receive_handoff(gate, core_source, bundle, **receiver_inputs)
    if canonical(expected) != canonical(ack):
        raise PRMSError('REJECTED', 'ack does not match verified receiver bytes and request')
    return {'status': 'VERIFIED_RECEIVER_FILE_RECORD', 'context_status': ack['context_status'],
            'model_understanding': 'NOT_OBSERVABLE', 'action_authorized': False}
