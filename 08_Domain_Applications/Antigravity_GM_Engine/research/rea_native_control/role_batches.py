"""Decided role batches, technical aggregation and durable at-most-once dispatch.

Profiles, phase grants, agreements and readback providers are trusted HOST inputs.
Role-submitted JSON supplies intentions only. No game decision or automatic retry.
"""
import hashlib
import json
import os
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path

from contracts import NativeActionRequest, Outcome

PLAY_TYPE_SLOTS = {'PLAYER.EDIT.PLAY_TYPE_' + str(slot): str(slot) for slot in range(1, 5)}


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(encode(value).encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class BatchContext:
    world_id: str
    save_instance_id: str
    generation_id: str
    season_id: str
    phase: str
    snapshot_ref: str
    catalog_version: str

    def __post_init__(self):
        if any(not isinstance(v, str) or not v.strip() for v in asdict(self).values()):
            raise ValueError('Complete context required')

    @property
    def scope(self):
        return digest([self.world_id, self.save_instance_id, self.generation_id])


@dataclass(frozen=True)
class ActionIntent:
    intent_id: str
    issuer_uid: str
    action_id: str
    parameters_json: str
    dependencies: tuple[str, ...] = ()
    agreement_ref: str | None = None

    def __post_init__(self):
        if any(not isinstance(v, str) or not v.strip() for v in (self.intent_id, self.issuer_uid, self.action_id)):
            raise ValueError('Intent identities required')
        if not isinstance(self.dependencies, tuple) or any(not isinstance(x, str) or not x for x in self.dependencies):
            raise ValueError('Immutable dependency IDs required')
        if len(set(self.dependencies)) != len(self.dependencies):
            raise ValueError('Duplicate dependency')
        if not isinstance(self.parameters, dict) or encode(self.parameters) != self.parameters_json:
            raise ValueError('Canonical parameter object required')

    @property
    def parameters(self):
        return json.loads(self.parameters_json)

    @classmethod
    def decided(cls, intent_id, issuer_uid, action_id, parameters, *, dependencies=(), agreement_ref=None):
        return cls(intent_id, issuer_uid, action_id, encode(parameters), tuple(dependencies), agreement_ref)


@dataclass(frozen=True)
class RoleActionBatch:
    batch_id: str
    context: BatchContext
    intents: tuple[ActionIntent, ...]

    def __post_init__(self):
        if not isinstance(self.batch_id, str) or not self.batch_id.strip() or not isinstance(self.intents, tuple):
            raise ValueError('Batch ID and immutable intents required')
        if not self.intents or any(not isinstance(x, ActionIntent) for x in self.intents):
            raise ValueError('Nonempty decided batch required')

    @classmethod
    def from_dict(cls, value):
        if set(value) != {'batch_id', 'context', 'intents'}:
            raise ValueError('Exact batch fields required')
        if not isinstance(value['intents'], list):
            raise ValueError('Intent array required')
        intents = []
        for row in value['intents']:
            required = {'intent_id', 'issuer_uid', 'action_id', 'parameters'}
            if not required <= set(row) or set(row) - required - {'dependencies', 'agreement_ref'}:
                raise ValueError('Exact intent fields required')
            if not isinstance(row.get('dependencies', []), list):
                raise ValueError('Dependency array required')
            intents.append(ActionIntent.decided(row['intent_id'], row['issuer_uid'], row['action_id'],
                           row['parameters'], dependencies=row.get('dependencies', []), agreement_ref=row.get('agreement_ref')))
        return cls(value['batch_id'], BatchContext(**value['context']), tuple(intents))


def trade_package(parameters):
    """Canonical identity for bilateral agreement/dedup only; never rewrite calls."""
    sides = [(parameters['team_a'], sorted(parameters['players_a']), sorted(parameters['picks_a'])),
             (parameters['team_b'], sorted(parameters['players_b']), sorted(parameters['picks_b']))]
    return sorted(sides, key=lambda x: x[0])


@dataclass(frozen=True)
class TradeAgreement:
    agreement_ref: str
    context_digest: str
    package_digest: str
    # Exact authenticated issuer -> represented team; supplied by negotiation host.
    parties: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class ReadbackEvidence:
    context_digest: str
    intent_digest: str
    evidence_ref: str
    applied: bool


@dataclass(frozen=True)
class PlannedAction:
    intent: ActionIntent
    native_action_id: str | None
    transaction_key: str
    resources: tuple[str, ...]
    aliases: tuple[ActionIntent, ...] = ()


@dataclass(frozen=True)
class BatchPlan:
    batch: RoleActionBatch
    actions: tuple[PlannedAction, ...]
    issues: tuple[str, ...]


# Each logical requirement may expose only its own fields, even with a shared handler.
COACH_FIELDS = {
    'COACH.STRATEGY.POE_O1': ('POEOffense',),
    'COACH.STRATEGY.POE_D1': ('POEDefense',),
    'COACH.STRATEGY.POE_O2': ('POEOffense2',),
    'COACH.STRATEGY.POE_O3': ('POEOffense3',),
    'COACH.STRATEGY.POE_D2': ('POEDefense2',),
    'COACH.STRATEGY.POE_D3': ('POEDefense3',),
    'COACH.STRATEGY.RUN_PLAY': ('RunPlayTendency',),
    'COACH.STRATEGY.ZONE_USAGE': ('ZoneUsage',),
    'COACH.STRATEGY.BENCH_DEPTH': ('BenchDepth',),
    'COACH.STRATEGY.BENCH_USE': ('BenchUtilization',),
}


def overlaps(a, b):
    return a == b or a.startswith(b + '/') or b.startswith(a + '/')


class ExecutionAggregator:
    def __init__(self, capabilities):
        self.service = capabilities

    def collect(self, submissions, *, aggregate_batch_id):
        """Host supplies (authenticated_profile, role_batch) pairs, never role labels.

        This is a binding to an existing identity service, not an authentication
        implementation. No model can submit another issuer through this entry.
        """
        context, intents = None, []
        for profile, batch in submissions:
            if any(i.issuer_uid != profile.actor_uid for i in batch.intents):
                raise PermissionError('SUBMISSION_ISSUER_DOES_NOT_MATCH_AUTHENTICATED_PROFILE')
            if context is not None and context != batch.context:
                raise ValueError('CANNOT_AGGREGATE_DIFFERENT_CONTEXTS')
            context = batch.context
            intents.extend(batch.intents)
        if context is None:
            raise ValueError('No submissions')
        return RoleActionBatch(aggregate_batch_id, context, tuple(intents))

    def plan(self, batch, *, profiles, phase_grants, agreements=()):
        """phase_grants: host (actor_uid, requirement_id) approvals for this exact context.

        No static table guesses that a date/calendar flag proves a live draft scene.
        The host attests applicability; runtime still checks Native object lifecycle.
        """
        context = batch.context
        if context.catalog_version != self.service.version:
            return BatchPlan(batch, (), ('STALE_CAPABILITY_CATALOG',))
        identities = {p.actor_uid: p for p in profiles}
        if len(identities) != len(profiles):
            return BatchPlan(batch, (), ('AMBIGUOUS_HOST_IDENTITY',))
        agreement_map = {a.agreement_ref: a for a in agreements}
        if len(agreement_map) != len(agreements):
            return BatchPlan(batch, (), ('AMBIGUOUS_AGREEMENT',))
        issues, unique = [], {}
        for intent in batch.intents:
            previous = unique.get(intent.intent_id)
            if previous and previous != intent:
                issues.append('INTENT_ID_REUSED_WITH_DIFFERENT_PAYLOAD:' + intent.intent_id)
            unique[intent.intent_id] = intent
        planned, trade_groups = {}, {}
        for iid, intent in unique.items():
            try:
                profile = identities[intent.issuer_uid]
                if any(getattr(profile, k) != getattr(context, k) for k in
                       ('world_id', 'save_instance_id', 'generation_id', 'season_id', 'phase', 'snapshot_ref')):
                    raise ValueError('ROLE_CONTEXT_MISMATCH')
                req = self.service._requirement(intent.action_id)
                if intent.action_id not in profile.allowed_actions or profile.role_type not in self.service.allowed_roles(intent.action_id):
                    raise PermissionError('ROLE_ACTION_NOT_GRANTED')
                if req['baseline_status'] == 'WORLD_EDIT' and profile.role_type != 'WORLD_ADMIN':
                    raise PermissionError('WORLD_EDIT_NOT_ROLE_SELF_SERVICE')
                if (intent.issuer_uid, intent.action_id) not in phase_grants:
                    raise PermissionError('PHASE_APPLICABILITY_NOT_ATTESTED')
                p = intent.parameters
                external = req['baseline_status'] == 'EXTERNAL'
                native_id = self.service.mapping.get(intent.action_id)
                if external:
                    if set(p) != set(req['input']):
                        raise ValueError('EXACT_EXTERNAL_REQUEST_FIELDS_REQUIRED')
                    if type(p.get('player_uid')) is not int or p['player_uid'] not in profile.player_scope:
                        raise PermissionError('EXTERNAL_REQUEST_PLAYER_IDENTITY_MISMATCH')
                    resources = ()
                else:
                    if not native_id:
                        raise ValueError('UNKNOWN_BINDING')
                    native = self.service.registry.get(native_id)
                    if native['kind'] == 'READ':
                        raise PermissionError('USE_ROLE_VISIBLE_DATA_SERVICE')
                    if not self.service._callable(native):
                        raise ValueError('UNKNOWN_BINDING')
                    self._check_target(intent, profile, native)
                    # Compile all requests before any dispatch, including range/ABI checks.
                    self.service.control.render(NativeActionRequest(native_id, p, iid))
                    resources = self._resources(native, p, intent.action_id)
                transaction = digest([context.scope, intent.issuer_uid, iid])
                if native_id and native_id.startswith('TRADE_'):
                    agreement = agreement_map.get(intent.agreement_ref)
                    package_id = digest(trade_package(p))
                    parties = dict(agreement.parties) if agreement else {}
                    if not agreement or agreement.context_digest != digest(asdict(context)) or agreement.package_digest != package_id:
                        raise PermissionError('EXACT_TRADE_AGREEMENT_REQUIRED')
                    if len(parties) != 2 or set(parties.values()) != {p['team_a'], p['team_b']}:
                        raise PermissionError('BILATERAL_TRADE_PARTIES_REQUIRED')
                    for actor, team in parties.items():
                        party = identities.get(actor)
                        if not party or party.role_type != 'GM' or team not in party.team_scope:
                            raise PermissionError('AGREEMENT_PARTY_IDENTITY_MISMATCH')
                        if any(getattr(party, k) != getattr(context, k) for k in
                               ('world_id', 'save_instance_id', 'generation_id', 'season_id', 'phase', 'snapshot_ref')):
                            raise PermissionError('AGREEMENT_PARTY_CONTEXT_MISMATCH')
                    if parties.get(intent.issuer_uid) not in profile.team_scope:
                        raise PermissionError('ISSUER_NOT_AGREEMENT_PARTY')
                    transaction = digest([context.scope, 'trade', intent.agreement_ref, package_id])
                    # Keep dispatch variant distinct; no silent FullCheck/direct switching.
                    if transaction in trade_groups and trade_groups[transaction].native_action_id != native_id:
                        raise ValueError('TRADE_EXECUTION_PATH_CONFLICT')
                row = PlannedAction(intent, native_id, transaction, resources)
                planned[iid] = row
                if native_id and native_id.startswith('TRADE_'):
                    trade_groups[transaction] = row
            except (KeyError, ValueError, TypeError, PermissionError) as exc:
                issues.append(iid + ':' + str(exc))
        # Validate the original graph, even if both GMs' entries collapse to one trade.
        order, remaining = [], dict(unique)
        for intent in unique.values():
            if any(dep not in unique for dep in intent.dependencies):
                issues.append('MISSING_DEPENDENCY:' + intent.intent_id)
        while remaining:
            ready = [k for k, i in remaining.items() if all(d in order for d in i.dependencies)]
            if not ready:
                issues.append('DEPENDENCY_CYCLE_OR_MISSING')
                break
            order.extend(ready)
            for k in ready:
                del remaining[k]
        rows = [planned[k] for k in order if k in planned]
        for n, left in enumerate(rows):
            for right in rows[n + 1:]:
                if left.transaction_key != right.transaction_key and any(overlaps(a, b) for a in left.resources for b in right.resources):
                    issues.append('CONFLICT_REQUIRES_ROLE_RESOLUTION:' + left.intent.intent_id + ':' + right.intent.intent_id)
        # Coalesce only identical agreed bilateral trades; all aliases stay in receipts.
        collapsed = []
        for row in rows:
            aliases = tuple(r.intent for r in rows if r.transaction_key == row.transaction_key)
            if any(r.transaction_key == row.transaction_key for r in collapsed):
                continue
            collapsed.append(PlannedAction(row.intent, row.native_action_id, row.transaction_key, row.resources, aliases))
        # If one alias depends on another transaction, execute the coalesced trade only
        # after ALL aliases' predecessors, not just whichever issuer appeared first.
        result, pending, done = [], list(collapsed), set()
        while pending:
            ready = [r for r in pending if all(d in done or any(d == a.intent_id for a in r.aliases)
                     for a in r.aliases for d in a.dependencies)]
            if not ready:
                issues.append('COALESCED_DEPENDENCY_CYCLE')
                break
            for r in ready:
                result.append(r)
                done.update(a.intent_id for a in r.aliases)
                pending.remove(r)
        return BatchPlan(batch, tuple(result), tuple(dict.fromkeys(issues)))

    def _check_target(self, intent, profile, native):
        p, handler = intent.parameters, native['runtime_handler']
        if handler.startswith('trade.'):
            if not set(profile.team_scope) & {p['team_a'], p['team_b']}:
                raise PermissionError('TRADE_TEAM_OUTSIDE_ROLE_SCOPE')
            return
        if 'team_id' not in p or p['team_id'] not in profile.team_scope:
            raise PermissionError('TARGET_TEAM_OUTSIDE_ROLE_SCOPE')
        if handler == 'sign.fa_offer':
            if intent.action_id != 'GM.CONTRACT.CONTRACT_OFFER' or profile.role_type != 'GM':
                raise PermissionError('CONTRACT_OFFER_ROLE_SCOPE_ESCAPE')
            if profile.phase != 'FA_SIGNING_OFFERS':
                raise PermissionError('HOST_FA_SIGNING_OFFERS_SCENE_ATTESTATION_REQUIRED')
            from signing_fields import validate_fa_offer_contract
            validate_fa_offer_contract(p['contract'], self.service.signing_schema)
        if handler == 'player.badges':
            from badge_fields import REQUIREMENT, validate_parameters
            if intent.action_id != REQUIREMENT or profile.role_type != 'WORLD_ADMIN':
                raise PermissionError('BADGE_EDITOR_ROLE_SCOPE_ESCAPE')
            validate_parameters(self.service.badge_fields, p)
        if handler == 'player.stats':
            from player_fields import ACTION_FAMILIES, ROLE_FIELDS, allowed_fields, validate_values
            family = ACTION_FAMILIES[native['action_id']]
            if ROLE_FIELDS.get(intent.action_id) != family:
                raise PermissionError('PLAYER_STAT_REQUIREMENT_SCOPE_ESCAPE')
            values = validate_values(self.service.player_stat_fields, native['action_id'], p)
            fields = allowed_fields(self.service.player_stat_fields, family, profile.role_type)
            if set(values) - set(fields):
                raise PermissionError('PLAYER_STAT_FIELD_OUTSIDE_ROLE_SCOPE')
            if profile.role_type == 'PLAYER' and p['player_id'] not in profile.player_scope:
                raise PermissionError('PLAYER_EDIT_IDENTITY_OUTSIDE_ROLE_SCOPE')
        if handler == 'player.playtypes':
            if intent.action_id not in PLAY_TYPE_SLOTS or set(p['slot_values']) != {PLAY_TYPE_SLOTS[intent.action_id]}:
                raise PermissionError('SHARED_HANDLER_SLOT_SCOPE_ESCAPE')
            if profile.role_type == 'PLAYER' and p['player_id'] not in profile.player_scope:
                raise PermissionError('PLAYER_EDIT_IDENTITY_OUTSIDE_ROLE_SCOPE')
        if handler in {'coach.settings', 'coach.poe'}:
            fields = COACH_FIELDS.get(intent.action_id)
            if not fields:
                raise ValueError('REQUIREMENT_FIELD_BINDING_NOT_RECOVERED')
            values = p['settings'] if handler == 'coach.settings' else {fields[0]: p['value']}
            if set(values) != set(fields):
                raise PermissionError('SHARED_HANDLER_FIELD_SCOPE_ESCAPE')
            for field, value in values.items():
                spec = self.service.coach_fields[field]
                if spec['enum'] is None and field != 'BenchDepth' and not 0 <= value <= 100:
                    raise ValueError('VALUE_OUTSIDE_KNOWN_UI_RANGE')
                if field == 'BenchDepth':
                    raise ValueError('UNKNOWN_UI_RANGE_REQUIRES_FIELD_CONTRACT')

    def _resources(self, native, p, requirement):
        handler = native['runtime_handler']
        if handler.startswith('trade.'):
            return tuple(sorted(['player/' + str(x) for x in p['players_a'] + p['players_b']] +
                                ['pick/' + str(x) for x in p['picks_a'] + p['picks_b']]))
        team = 'team/' + str(p['team_id'])
        if handler == 'sign.fa_offer':
            return ('player/' + str(p['player_id']), team + '/offer/' + str(p['player_id']))
        if handler in {'coach.settings', 'coach.poe'}:
            return tuple(team + '/coach/' + f for f in COACH_FIELDS[requirement])
        if handler.startswith('scout.'):
            return (team + '/scouting',)
        if handler.startswith('training.'):
            day = team + '/training/' + str(p['date'])
            if handler == 'training.intensity':
                return (day + '/intensity',)
            if handler == 'training.patch':
                return (day + '/focus',) if native['action_id'] == 'TRAIN_TEAM_PATCH_FOCUS_RAW' else (day + '/profile', day + '/subfocus')
            return (day,)
        if handler == 'rotation.minutes':
            return ('player/' + str(p['player_id']) + '/rotation/minutes',)
        if handler == 'player.playtypes':
            return tuple('player/' + str(p['player_id']) + '/playtypes/' + key for key in sorted(p['slot_values']))
        if handler == 'player.stats':
            from player_fields import ACTION_FAMILIES, selected_values
            return tuple('player/' + str(p['player_id']) + '/stat/' + ACTION_FAMILIES[native['action_id']] + '/' + key
                         for key in sorted(selected_values(native['action_id'], p)))
        if handler == 'player.badges':
            from badge_fields import resource_fields
            return tuple('player/' + str(p['player_id']) + '/badges/' + name
                         for name in resource_fields(self.service.badge_fields, p))
        if handler == 'draft.select':
            return ('draft/current-selection', 'player/' + str(p['player_id']), 'pick/' + str(p['pick_id']))
        return (team + '/native-context',)


class ExecutionJournal:
    """Private execution records; no business database or new approval system.

    The OS file lock releases on process death; an incomplete operation directory
    remains UNKNOWN. Never delete it to retry. Directory and receipt hashes do not
    provide security against an operator editing this private journal.
    """
    def __init__(self, directory):
        self.root = Path(directory).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def lock(self, scope):
        path = self.root / scope
        path.mkdir(exist_ok=True)
        with (path / 'scope.lock').open('a+b') as file:
            file.seek(0)
            if file.read(1) == b'':
                file.write(b'0')
                file.flush()
            file.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                yield path
            finally:
                file.seek(0)
                if os.name == 'nt':
                    msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(file, fcntl.LOCK_UN)

    @staticmethod
    def write(path, value):
        temp = path.with_suffix('.tmp')
        with temp.open('wb') as file:
            file.write(encode(value).encode('utf-8'))
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp, path)


@dataclass(frozen=True)
class ExecutionResult:
    intent_id: str
    outcome: str
    original_parameters_json: str
    native_outcome: str | None = None
    evidence_ref: str | None = None
    reason: str | None = None
    reused_historical_receipt: bool = False


class NativeActionDispatcher:
    def __init__(self, capabilities, journal):
        self.service, self.journal = capabilities, journal

    def dispatch(self, plan, *, pre_dispatch_context, readback=None):
        """Only accepts plans recomputed by the trusted host for the current batch.

        pre_dispatch_context(context, intent) must raise on stale/mismatched context.
        readback is an independent host observer, not a flag supplied by a model.
        """
        if plan.issues:
            return tuple(ExecutionResult(i.intent_id, 'NOT_EXECUTED', i.parameters_json,
                                         reason=';'.join(plan.issues)) for i in plan.batch.intents)
        ctx = plan.batch.context
        results, completed = {}, set()
        with self.journal.lock(ctx.scope) as scope:
            # Bind batch identity and every issuer+intent ID before any Native call.
            batch_path = scope / ('batch-' + digest(plan.batch.batch_id) + '.json')
            fingerprint = digest(asdict(plan.batch))
            if batch_path.exists() and json.loads(batch_path.read_text(encoding='utf-8')) != fingerprint:
                raise ValueError('BATCH_ID_REUSED_WITH_DIFFERENT_PAYLOAD')
            self.journal.write(batch_path, fingerprint)
            for intent in plan.batch.intents:
                key = digest([intent.issuer_uid, intent.intent_id])
                path = scope / ('intent-' + key + '.json')
                value = digest([asdict(ctx), asdict(intent)])
                if path.exists() and json.loads(path.read_text(encoding='utf-8')) != value:
                    raise ValueError('INTENT_ID_REUSED_WITH_DIFFERENT_PAYLOAD')
                self.journal.write(path, value)
            stopped = False
            for row in plan.actions:
                intent, record = row.intent, scope / row.transaction_key
                dependencies = {d for a in row.aliases for d in a.dependencies} - {a.intent_id for a in row.aliases}
                result = None
                if stopped or not dependencies <= completed:
                    result = ExecutionResult(intent.intent_id, 'NOT_EXECUTED', intent.parameters_json, reason='DEPENDENCY_OR_BATCH_STOP')
                elif record.exists():
                    receipt = record / 'result.json'
                    if receipt.exists():
                        try:
                            old = json.loads(receipt.read_text(encoding='utf-8'))
                            old['reused_historical_receipt'] = True
                            result = ExecutionResult(**old)
                        except (OSError, ValueError, TypeError):
                            result = ExecutionResult(intent.intent_id, 'UNKNOWN_EXECUTION_OUTCOME', intent.parameters_json, reason='DAMAGED_JOURNAL')
                    else:
                        result = ExecutionResult(intent.intent_id, 'UNKNOWN_EXECUTION_OUTCOME', intent.parameters_json, reason='STARTED_WITHOUT_RESULT_NO_REPLAY')
                else:
                    # Across new IDs/batches, unresolved prior effects still reserve resources.
                    for prior in scope.iterdir():
                        if not prior.is_dir():
                            continue
                        try:
                            claim = json.loads((prior / 'claim.json').read_text(encoding='utf-8'))
                            status = json.loads((prior / 'result.json').read_text(encoding='utf-8'))['outcome'] if (prior / 'result.json').exists() else 'UNKNOWN_EXECUTION_OUTCOME'
                            if status not in {'APPLIED_READBACK_CONFIRMED', 'REJECTED_BY_GAME', 'EXTERNAL_REQUEST_RECORDED'} and any(overlaps(a, b) for a in row.resources for b in claim['resources']):
                                raise ValueError('UNRESOLVED_PRIOR_EFFECT')
                        except (OSError, ValueError, KeyError):
                            result = ExecutionResult(intent.intent_id, 'NOT_EXECUTED', intent.parameters_json, reason='UNRESOLVED_OR_DAMAGED_PRIOR_CLAIM')
                            break
                    if result is None:
                        result = self._execute(row, ctx, record, pre_dispatch_context, readback)
                success = result.outcome in {'APPLIED_READBACK_CONFIRMED', 'EXTERNAL_REQUEST_RECORDED'}
                if success:
                    completed.update(a.intent_id for a in row.aliases)
                if result.outcome in {'UNKNOWN_EXECUTION_OUTCOME', 'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED'}:
                    stopped = True
                for alias in row.aliases:
                    results[alias.intent_id] = ExecutionResult(alias.intent_id, result.outcome, alias.parameters_json,
                                                             result.native_outcome, result.evidence_ref, result.reason,
                                                             result.reused_historical_receipt)
            return tuple(results[i.intent_id] for i in plan.batch.intents)

    def _execute(self, row, ctx, record, guard, readback):
        intent = row.intent
        if row.native_action_id and self.service.control.transport is None:
            return ExecutionResult(intent.intent_id, 'NOT_EXECUTED', intent.parameters_json, reason='EXPLICIT_NATIVE_TRANSPORT_REQUIRED')
        try:
            guard(ctx, intent)
        except Exception:
            return ExecutionResult(intent.intent_id, 'NOT_EXECUTED', intent.parameters_json, reason='CURRENT_CONTEXT_NOT_CONFIRMED')
        record.mkdir(exist_ok=False)
        self.journal.write(record / 'claim.json', {'context': asdict(ctx), 'intent': asdict(intent),
                           'resources': row.resources, 'native_action_id': row.native_action_id})
        result = ExecutionResult(intent.intent_id, 'UNKNOWN_EXECUTION_OUTCOME', intent.parameters_json,
                                 reason='STARTED_WITHOUT_CONFIRMED_RESULT')
        try:
            if row.native_action_id is None:
                # Durable outbox only. No automatic messaging or conversion into a Setter.
                result = ExecutionResult(intent.intent_id, 'EXTERNAL_REQUEST_RECORDED', intent.parameters_json,
                                         evidence_ref=str(record / 'claim.json'))
            else:
                native = self.service.control.dispatch(NativeActionRequest(row.native_action_id, intent.parameters, intent.intent_id))
                self.journal.write(record / 'native_result.json', asdict(native))
                if native.outcome == Outcome.REJECTED:
                    result = ExecutionResult(intent.intent_id, 'REJECTED_BY_GAME', intent.parameters_json, str(native.outcome))
                elif native.outcome == Outcome.RETURNED:
                    result = ExecutionResult(intent.intent_id, 'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED', intent.parameters_json, str(native.outcome))
                    if readback is not None:
                        evidence = readback(ctx, intent, native)
                        if not isinstance(evidence, ReadbackEvidence) or evidence.context_digest != digest(asdict(ctx)) or evidence.intent_digest != digest(asdict(intent)) or not evidence.evidence_ref or type(evidence.applied) is not bool:
                            raise ValueError('Readback evidence not bound to exact request')
                        if evidence.applied:
                            result = ExecutionResult(intent.intent_id, 'APPLIED_READBACK_CONFIRMED', intent.parameters_json,
                                                     str(native.outcome), evidence.evidence_ref)
        except Exception:
            result = ExecutionResult(intent.intent_id, 'UNKNOWN_EXECUTION_OUTCOME', intent.parameters_json,
                                     reason='CALL_OR_READBACK_FAILED_NO_AUTOMATIC_RETRY')
        self.journal.write(record / 'result.json', asdict(result))
        return result

    def reconcile_unknown(self, context, transaction_key, *, observer):
        """Record independently proven effect, never invoke or replay a Native action.

        observer consumes the ORIGINAL claim and must provide exact-bound evidence.
        A negative observation alone does not establish that an operation never ran;
        it cannot clear the reservation or authorize automatic replay.
        """
        if len(transaction_key) != 64 or any(c not in '0123456789abcdef' for c in transaction_key):
            raise ValueError('Journal transaction digest required')
        with self.journal.lock(context.scope) as scope:
            record = scope / transaction_key
            claim = json.loads((record / 'claim.json').read_text(encoding='utf-8'))
            if claim['context'] != asdict(context):
                raise ValueError('Original claimed context required')
            receipt = record / 'result.json'
            if receipt.exists():
                old = json.loads(receipt.read_text(encoding='utf-8'))
                if old['outcome'] in {'APPLIED_READBACK_CONFIRMED', 'REJECTED_BY_GAME', 'EXTERNAL_REQUEST_RECORDED'}:
                    return ExecutionResult(**old)
            fields = claim['intent'] | {'dependencies': tuple(claim['intent']['dependencies'])}
            intent = ActionIntent(**fields)
            evidence = observer(context, intent)
            if not isinstance(evidence, ReadbackEvidence) or evidence.context_digest != digest(asdict(context)) or evidence.intent_digest != digest(asdict(intent)) or not evidence.evidence_ref or type(evidence.applied) is not bool:
                raise ValueError('Independent evidence must bind original context and intent')
            result = ExecutionResult(intent.intent_id, 'APPLIED_READBACK_CONFIRMED' if evidence.applied else 'UNKNOWN_EXECUTION_OUTCOME',
                                     intent.parameters_json, evidence_ref=evidence.evidence_ref,
                                     reason='INDEPENDENT_RECONCILIATION_NO_NATIVE_CALL')
            # Preserve the prior receipt rather than rewriting historical uncertainty.
            if receipt.exists() and not (record / 'result_before_reconciliation.json').exists():
                self.journal.write(record / 'result_before_reconciliation.json', json.loads(receipt.read_text(encoding='utf-8')))
            self.journal.write(record / 'reconciliation.json', asdict(evidence))
            self.journal.write(receipt, asdict(result))
            return result
