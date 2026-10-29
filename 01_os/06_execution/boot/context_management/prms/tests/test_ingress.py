"""Actual ingress -> WriterGate -> GitHubGitState calls over fake transport.

No GitHub permissions, real host authentication or production fence is proved.
"""
import base64
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source import canonical, PRMSError
from github_state import GitHubGitState
from ingress import TrustedIngress, HostSession, CopyGrant


class GitDatabaseFixture:
    def __init__(self):
        self.ref = 'a' * 40
        self.commits = {self.ref: {'tree': {'sha': 'b' * 40}, 'parents': []}}
        self.trees = {'b' * 40: {}}
        self.blobs = {}
        self.calls = []
        self.before_patch = None

    def __call__(self, method, path, payload):
        path = path.removeprefix('repos/fixture/private-state/')
        self.calls.append((method, path))
        if method == 'GET' and path.startswith('git/ref/'):
            return {'object': {'sha': self.ref}}
        if method == 'GET' and path.startswith('git/commits/'):
            return self.commits[path.rsplit('/', 1)[1]]
        if method == 'POST' and path == 'git/blobs':
            raw = base64.b64decode(payload['content'])
            sha = hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()
            self.blobs[sha] = payload['content']
            return {'sha': sha}
        if method == 'GET' and path.startswith('git/blobs/'):
            return {'content': self.blobs[path.rsplit('/', 1)[1]]}
        if method == 'POST' and path == 'git/trees':
            tree = dict(self.trees[payload['base_tree']])
            tree.update({item['path']: item for item in payload['tree']})
            sha = hashlib.sha1(canonical(tree)).hexdigest()
            self.trees[sha] = tree
            return {'sha': sha}
        if method == 'GET' and path.startswith('git/trees/'):
            commit = path.split('/')[2].split('?')[0]
            tree = self.commits[commit]['tree']['sha']
            return {'tree': list(self.trees[tree].values()), 'truncated': False}
        if method == 'POST' and path == 'git/commits':
            sha = hashlib.sha1(canonical(payload)).hexdigest()
            self.commits[sha] = {'tree': {'sha': payload['tree']},
                                 'parents': [{'sha': p} for p in payload['parents']]}
            return {'sha': sha}
        if method == 'PATCH':
            assert payload['force'] is False
            hook, self.before_patch = self.before_patch, None
            if hook:
                hook()
            if self.commits[payload['sha']]['parents'] != [{'sha': self.ref}]:
                raise RuntimeError('non fast forward')
            self.ref = payload['sha']
            return {'object': {'sha': self.ref}}
        if path.startswith('compare/'):
            ancestor, tip = path.split('/')[1].split('...')
            while tip != ancestor and self.commits[tip]['parents']:
                tip = self.commits[tip]['parents'][0]['sha']
            return {'status': 'ahead' if tip == ancestor else 'diverged'}
        raise AssertionError((method, path))


class BoundTestAuthority:
    """Only test credentials, bound to an independently supplied host channel."""
    def __init__(self):
        self.records = {}
        self.revoked = set()
        self.calls = 0
        self.on_auth = None

    def issue(self, grant):
        credential, host_channel = object(), object()
        self.records[(credential, host_channel)] = grant
        return credential, host_channel

    def authenticate(self, context):
        self.calls += 1
        if self.on_auth:
            self.on_auth(self.calls)
        grant = self.records[context]
        if grant.session_id in self.revoked:
            raise ValueError('revoked')
        return grant


def grant(session='first', **changes):
    value = HostSession(session, 'host-subject', 'fixture Human task packet', 1000,
        ('r', 'target'), ('task',), ('REGISTER', 'CLAIM', 'ASSIGN', 'APPEND', 'CHECKPOINT', 'COPY_ALL_MEMORY', 'RECOVER'))
    return replace(value, **changes)


@pytest.fixture
def host():
    wire, authority = GitDatabaseFixture(), BoundTestAuthority()
    store = GitHubGitState(wire, repository='fixture/private-state', ref='refs/heads/state',
        allowed_state_repository='fixture/private-state', write_enabled=True)
    ingress = TrustedIngress(store, authority, enabled=True, clock=lambda: 100)
    context = authority.issue(grant())
    return wire, authority, store, ingress, context


def mutate(host, context, op, kind, payload, **changes):
    wire, _, store, ingress, _ = host
    snapshot = store.snapshot()
    current = json.loads(snapshot.get('roles/r/CURRENT.json', b'{"state_version":0,"owner_epoch":0}'))
    request = dict(operation_id=op, expected_head=wire.ref, expected_version=current['state_version'],
                   expected_epoch=current['owner_epoch'], kind=kind, payload=payload)
    return ingress.mutate(context, 'r', **{**request, **changes})


def register(host):
    return mutate(host, host[-1], 'register', 'REGISTER', {'definition': {'role_type_id': 'engineer', 'version': '1'},
                   'domain_id': 'core', 'state_repository_id': 'fixture/private-state'})


def test_ingress_dormant_missing_host_and_forged_or_copied_identity(host):
    wire, authority, store, ingress, context = host
    with pytest.raises(PRMSError, match='INGRESS_DISABLED'):
        TrustedIngress(store, authority).recover(context, 'r')
    with pytest.raises(PRMSError, match='AUTHORITY_UNVERIFIED'):
        TrustedIngress(store, enabled=True).recover(context, 'r')
    for forged in ({'session_id': 'first'}, (context[0], object()), grant()):
        with pytest.raises(PRMSError, match='AUTHORITY_UNVERIFIED'):
            ingress.recover(forged, 'r')
    assert wire.calls == []


def test_remote_ingress_assignment_events_takeover_and_revoke(host):
    wire, authority, store, ingress, context = host
    assert register(host)['ingress_status'] == 'IMPLEMENTED_UNVERIFIED_PLATFORM'
    mutate(host, context, 'assign', 'ASSIGN', {'assignment_id': 'a1', 'task_id': 'task', 'human_authority_ref': 'fixture'})
    mutate(host, context, 'event', 'APPEND', {'event_id': 'e1', 'task_id': 'task', 'kind': 'HUMAN_DECISION',
        'text': 'approved fixture', 'source_refs': [{'repository': 'fixture', 'path': 'Human.md', 'commit': 'a' * 40}]})
    mutate(host, context, 'cp', 'CHECKPOINT', {'task_id': 'task'})
    second = authority.issue(grant('second'))
    mutate(host, second, 'claim', 'CLAIM', {})
    before = wire.ref
    with pytest.raises(PRMSError, match='STALE_OWNER'):
        mutate(host, context, 'old-cp', 'CHECKPOINT', {'task_id': 'task'})
    assert wire.ref == before
    assert ingress.recover(second, 'r')['current']['owner_epoch'] == 2
    authority.revoked.add('second')
    with pytest.raises(PRMSError, match='AUTHORITY_UNVERIFIED'):
        ingress.recover(second, 'r')
    ingress.revoke_session('first')
    with pytest.raises(PRMSError, match='AUTHORITY_UNVERIFIED'):
        ingress.recover(context, 'r')
    with pytest.raises(PRMSError, match='FENCING_NOT_ENFORCEABLE'):
        ingress.require_enforced()
    assert all(method != 'PATCH' or path == 'git/refs/heads/state' for method, path in wire.calls)


def test_host_scopes_expiry_and_binding_change_cannot_publish(host):
    wire, authority, _, ingress, context = host
    register(host)
    before = wire.ref
    for limited in (grant('read-only', allowed_operations=('RECOVER',)),
                    grant('wrong-role', allowed_roles=('other',)), grant('expired', expires_at=99)):
        with pytest.raises(PRMSError, match='AUTHORITY_UNVERIFIED'):
            mutate(host, authority.issue(limited), limited.session_id, 'CHECKPOINT', {'task_id': 'task'})
    with pytest.raises(PRMSError, match='AUTHORITY_UNVERIFIED'):
        mutate(host, context, 'wrong-task', 'ASSIGN', {'assignment_id': 'a', 'task_id': 'other', 'human_authority_ref': 'caller'})
    authority.records[context] = grant(allowed_roles=('other',))
    with pytest.raises(PRMSError, match='AUTHORITY_UNVERIFIED'):
        ingress.recover(context, 'r')
    assert wire.ref == before


def test_revoke_between_prepare_and_publish_prevents_remote_ref_update(host):
    wire, authority, _, _, context = host
    register(host)
    before = wire.ref
    authority.on_auth = lambda count: authority.revoked.add('first') if count == 4 else None
    with pytest.raises(PRMSError, match='AUTHORITY_UNVERIFIED'):
        mutate(host, context, 'late-revoke', 'CHECKPOINT', {'task_id': 'task'})
    assert wire.ref == before
    assert sum(method == 'PATCH' for method, _ in wire.calls) == 1


def test_every_copy_requires_exact_four_part_host_grant(host):
    wire, authority, _, ingress, context = host
    register(host)
    frozen = wire.ref
    kwargs = dict(source_commit=frozen, operation_id='copy', expected_head=frozen, approval_ref='Human-copy')
    with pytest.raises(PRMSError, match='AUTHORITY_UNVERIFIED'):
        ingress.copy(context, 'r', 'target', **kwargs)
    bound = authority.issue(grant('copy', copy_grants=(CopyGrant('r', 'target', frozen, 'Human-copy'),)))
    for source, target, changed in [('other', 'target', {}), ('r', 'r', {}),
            ('r', 'target', {'source_commit': 'f' * 40}), ('r', 'target', {'approval_ref': 'caller'})]:
        with pytest.raises(PRMSError, match='AUTHORITY_UNVERIFIED'):
            ingress.copy(bound, source, target, **{**kwargs, **changed})
    assert wire.ref == frozen
    reply = ingress.copy(bound, 'r', 'target', **kwargs)
    assert reply['status'] == 'PUBLISHED'
    assert ingress.recover(bound, 'target')['identity']['copied_authority_valid'] is False
    assert ingress.copy(bound, 'r', 'target', **kwargs)['status'] == 'ALREADY_APPLIED'


def test_competing_ingress_child_cannot_overwrite_winning_owner(host):
    wire, authority, _, ingress, context = host
    register(host)
    second = authority.issue(grant('second'))
    wire.before_patch = lambda: mutate(host, second, 'winner', 'CLAIM', {})
    with pytest.raises(PRMSError, match='PUBLISH_NOT_CONFIRMED'):
        mutate(host, context, 'loser', 'CHECKPOINT', {'task_id': 'task'})
    restored = ingress.recover(second, 'r')
    assert restored['current']['operation_id'] == 'winner'
    assert restored['current']['owner_epoch'] == 2
