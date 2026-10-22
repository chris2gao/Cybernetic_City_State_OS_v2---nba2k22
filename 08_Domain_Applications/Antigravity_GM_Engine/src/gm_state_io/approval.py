"""Optional foreground review, explicitly NOT an isolated approval issuer.

Same-user code/PTY access can impersonate the operator. This workflow therefore
provides MANUAL_OPERATOR_TRUST_ONLY, never cryptographic human authentication.
Player decision 2026-10-20 accepts operator attestation of specific chat approval
through the ordinary CLI. Review is optional; no isolated issuer is planned here.
"""
from contextlib import contextmanager
import json
import os
import sys
from weakref import WeakKeyDictionary
from .common import binding, canonical, digest

TRUST = 'MANUAL_OPERATOR_TRUST_ONLY'
_reviews = WeakKeyDictionary()


class _Supervision:
    pass


def require_supervision(plan, approval, supervision, rollback=False):
    proof = _reviews.get(supervision) if isinstance(supervision, _Supervision) else None
    expected = (os.getpid(), digest(plan), approval, bool(rollback))
    if proof != expected:
        raise PermissionError('MODEL_PROVIDED_CLAIM_ONLY_UNSUPERVISED_RW_DISABLED')


@contextmanager
def review(plan, *, rollback=False):
    """Keep approval in this foreground process; never issue a reusable file."""
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise PermissionError('PENDING_HUMAN_APPROVAL_FOREGROUND_TERMINAL_REQUIRED')
    from .executor import ExternalApproval
    operation = 'ROLLBACK' if rollback else 'APPLY'
    print(canonical(dict(status='PENDING_HUMAN_APPROVAL', trust=TRUST,
        warning='No OS privilege isolation: only the human operator may run this command. '
                'Models must not feed terminal input or approve their own actions.',
        operation=operation, complete_plan=plan)))
    print('Only approved registered fields are written; no general ability, Potential, badge, '
          'contract or other unselected writes. Memory readback does not prove save persistence.')
    expected = ':'.join(binding(plan).values())
    loaded = input('Type the actually loaded save_id:save_instance_id:generation_id: ').strip()
    if loaded != expected:
        raise PermissionError('LOADED_SAVE_CONFIRMATION_MISMATCH')
    if input('Close the relevant editors, then type EDITORS CLOSED: ').strip() != 'EDITORS CLOSED':
        raise PermissionError('EDITORS_CLOSED_CONFIRMATION_REQUIRED')
    reference = input('Human operator approval reference: ').strip()
    if not reference:
        raise PermissionError('HUMAN_OPERATOR_REFERENCE_REQUIRED')
    if plan.get('operation') == 'TEAM_BOOK_REBIND':
        event = plan['event']
        expected_event = 'CONFIRM '+event['kind']+' '+event['reference']
        if input('Confirm the actual new-save / completed coach-change event. Type '+expected_event+': ').strip() != expected_event:
            raise PermissionError('TEAM_BOOK_REBIND_EVENT_NOT_HUMAN_CONFIRMED')
    if input('Type APPROVE '+operation+' '+plan['digest']+': ').strip() != 'APPROVE '+operation+' '+plan['digest']:
        raise PermissionError('PENDING_HUMAN_APPROVAL_EXACT_DIGEST_REQUIRED')
    approval = ExternalApproval(**binding(plan), source_batch_id=plan['source_batch_id'],
        decision_id=plan['decision_id'], version=plan['version'],
        action_ids=tuple(a['action_id'] for a in plan['actions']), digest=plan['digest'],
        player_approval_reference=reference, loaded_save_confirmation=loaded, editors_closed=True)
    supervision = _Supervision()
    _reviews[supervision] = (os.getpid(), digest(plan), approval, bool(rollback))
    try:
        yield approval, supervision
    finally:
        _reviews.pop(supervision, None)
