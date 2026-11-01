"""Offline batch protocol tests using the REAL planner/compiler and fake transport.

No target process, memory access, game effects or live readback is implied.
"""
import json
import sys
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from facade import NativeControlFacade
from role_capabilities import RoleCapabilityProfile, RoleCapabilityService
from role_batches import (ActionIntent, BatchContext, ExecutionAggregator, ExecutionJournal,
                          NativeActionDispatcher, ReadbackEvidence, RoleActionBatch,
                          TradeAgreement, digest, trade_package)


class CountingTransport:
    def __init__(self, outcomes=()):
        self.calls = []
        self.outcomes = list(outcomes)

    def execute(self, script, **kwargs):
        self.calls.append((script, kwargs))
        outcome = self.outcomes.pop(0) if self.outcomes else 'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED'
        if isinstance(outcome, Exception):
            raise outcome
        return {'outcome': outcome}


class BatchProtocol(unittest.TestCase):
    def setUp(self):
        self.transport = CountingTransport()
        self.service = RoleCapabilityService(control=NativeControlFacade(transport=self.transport))
        self.ctx = BatchContext('world', 'save', 'gen', 'season', 'REGULAR_SEASON', 'snapshot', self.service.version)
        self.coach = RoleCapabilityProfile('COACH', 'coach20', (20,), 'world', 'save', 'gen',
                                          'season', 'REGULAR_SEASON', 'snapshot',
                                          frozenset({'COACH.STRATEGY.RUN_PLAY', 'COACH.STRATEGY.ZONE_USAGE'}))
        self.profiles = [self.coach]
        self.grants = {(self.coach.actor_uid, a) for a in self.coach.allowed_actions}
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.journal = ExecutionJournal(self.temp.name)

    def intent(self, iid='one', field='RunPlayTendency', value=55, deps=()):
        action = 'COACH.STRATEGY.RUN_PLAY' if field == 'RunPlayTendency' else 'COACH.STRATEGY.ZONE_USAGE'
        return ActionIntent.decided(iid, 'coach20', action, {'team_id': 20, 'settings': {field: value}}, dependencies=deps)

    def plan(self, *intents, batch_id='batch', agreements=()):
        batch = RoleActionBatch(batch_id, self.ctx, tuple(intents))
        return ExecutionAggregator(self.service).plan(batch, profiles=self.profiles,
                                                     phase_grants=self.grants, agreements=agreements)

    def observe(self, ctx, intent, native):
        return ReadbackEvidence(digest(asdict(ctx)), digest(asdict(intent)), 'OFFLINE_FAKE_READBACK', True)

    def dispatch(self, plan, readback=True):
        return NativeActionDispatcher(self.service, self.journal).dispatch(plan,
                   pre_dispatch_context=lambda *_: None, readback=self.observe if readback else None)

    def test_partial_outcome_stops_batch_and_is_not_replayed_after_restart(self):
        self.transport.outcomes = ['NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED', RuntimeError('lost receipt')]
        plan = self.plan(self.intent(), self.intent('two', 'ZoneUsage', 10))
        self.assertFalse(plan.issues)
        result = self.dispatch(plan)
        self.assertEqual([r.outcome for r in result], ['APPLIED_READBACK_CONFIRMED', 'UNKNOWN_EXECUTION_OUTCOME'])
        restarted = NativeActionDispatcher(self.service, ExecutionJournal(self.temp.name))
        result = restarted.dispatch(plan, pre_dispatch_context=lambda *_: self.fail('Replayed'), readback=self.observe)
        self.assertEqual(len(self.transport.calls), 2)
        self.assertTrue(result[0].reused_historical_receipt)

    def test_unknown_reserves_field_even_with_new_batch_and_intent_ids(self):
        self.dispatch(self.plan(self.intent()), readback=False)
        result = self.dispatch(self.plan(self.intent('different'), batch_id='different'))
        self.assertEqual(result[0].outcome, 'NOT_EXECUTED')
        self.assertEqual(len(self.transport.calls), 1)
        # Another independent field is not globally frozen by that unresolved write.
        self.dispatch(self.plan(self.intent('zone', 'ZoneUsage', 10), batch_id='zone'))
        self.assertEqual(len(self.transport.calls), 2)

    def test_started_without_result_is_unknown_not_permission_to_retry(self):
        plan = self.plan(self.intent())
        directory = self.journal.root / self.ctx.scope / plan.actions[0].transaction_key
        directory.mkdir(parents=True)
        result = self.dispatch(plan)
        self.assertEqual(result[0].outcome, 'UNKNOWN_EXECUTION_OUTCOME')
        self.assertFalse(self.transport.calls)

    def test_conflicts_cycles_and_missing_dependencies_have_zero_calls(self):
        for plan in [self.plan(self.intent(), self.intent('two', value=25)),
                     self.plan(self.intent(deps=('absent',))),
                     self.plan(self.intent(deps=('two',)), self.intent('two', 'ZoneUsage', deps=('one',)))]:
            self.assertTrue(plan.issues)
            self.assertTrue(all(r.outcome == 'NOT_EXECUTED' for r in self.dispatch(plan)))
        self.assertFalse(self.transport.calls)

    def test_dependency_order_and_payload_freezing(self):
        parameters = {'team_id': 20, 'settings': {'RunPlayTendency': 55}}
        a = ActionIntent.decided('one', 'coach20', 'COACH.STRATEGY.RUN_PLAY', parameters)
        parameters['settings']['RunPlayTendency'] = 99
        plan = self.plan(self.intent('two', 'ZoneUsage', 10, deps=('one',)), a)
        self.assertEqual([r.intent.intent_id for r in plan.actions], ['one', 'two'])
        self.dispatch(plan)
        self.assertIn('"RunPlayTendency":55', self.transport.calls[0][0])
        self.assertNotIn('"RunPlayTendency":99', self.transport.calls[0][0])

    def test_shared_handler_target_and_phase_grants_cannot_expand_authority(self):
        escape = ActionIntent.decided('escape', 'coach20', 'COACH.STRATEGY.RUN_PLAY',
                                      {'team_id': 20, 'settings': {'ZoneUsage': 55}})
        wrong_team = ActionIntent.decided('other', 'coach20', 'COACH.STRATEGY.RUN_PLAY',
                                         {'team_id': 1, 'settings': {'RunPlayTendency': 55}})
        for intent in [escape, wrong_team, self.intent(value=101)]:
            self.assertTrue(self.plan(intent).issues)
        self.grants.clear()
        self.assertTrue(self.plan(self.intent()).issues)
        self.assertFalse(self.transport.calls)

    def test_batch_and_intent_id_payload_changes_are_rejected_durably(self):
        self.dispatch(self.plan(self.intent()))
        with self.assertRaises(ValueError):
            self.dispatch(self.plan(self.intent(value=80)))
        with self.assertRaises(ValueError):
            self.dispatch(self.plan(self.intent(value=80), batch_id='new-batch'))
        self.assertEqual(len(self.transport.calls), 1)

    def test_exact_trade_is_once_for_both_gms_and_does_not_add_salary_matching(self):
        aid = 'GM.TRADE.EXECUTE_AGREED'
        gm = replace(self.coach, role_type='GM', actor_uid='gm20', allowed_actions=frozenset({aid}))
        other = replace(gm, actor_uid='gm1', team_scope=(1,))
        self.profiles = [gm, other]
        self.grants = {('gm20', aid), ('gm1', aid)}
        package = {'team_a': 20, 'team_b': 1, 'players_a': [7239], 'players_b': [7716], 'picks_a': [], 'picks_b': []}
        reverse = {'team_a': 1, 'team_b': 20, 'players_a': [7716], 'players_b': [7239], 'picks_a': [], 'picks_b': []}
        a = ActionIntent.decided('a', 'gm20', aid, package, agreement_ref='agreement')
        b = ActionIntent.decided('b', 'gm1', aid, reverse, agreement_ref='agreement')
        agreement = TradeAgreement('agreement', digest(asdict(self.ctx)), digest(trade_package(package)), (('gm20', 20), ('gm1', 1)))
        self.assertTrue(self.plan(a).issues)
        plan = self.plan(a, b, agreements=(agreement,))
        self.assertFalse(plan.issues)
        self.assertEqual(len(plan.actions), 1)
        result = self.dispatch(plan)
        self.assertEqual([r.outcome for r in result], ['APPLIED_READBACK_CONFIRMED'] * 2)
        self.assertEqual(len(self.transport.calls), 1)
        self.assertIn('AGREED_DIRECT_PROCESS', self.transport.calls[0][0])
        self.assertEqual(json.loads(result[1].original_parameters_json), reverse)

    def test_bad_readback_binding_and_stale_context_do_not_claim_success(self):
        dispatcher = NativeActionDispatcher(self.service, self.journal)
        result = dispatcher.dispatch(self.plan(self.intent()), pre_dispatch_context=lambda *_: None,
                    readback=lambda *_: ReadbackEvidence('wrong-save', 'wrong-intent', 'fake', True))
        self.assertEqual(result[0].outcome, 'UNKNOWN_EXECUTION_OUTCOME')
        self.assertEqual(len(self.transport.calls), 1)

        def stale(*_):
            raise ValueError('different generation')
        result = dispatcher.dispatch(self.plan(self.intent('other', 'ZoneUsage'), batch_id='other'),
                                     pre_dispatch_context=stale, readback=self.observe)
        self.assertEqual(result[0].outcome, 'NOT_EXECUTED')
        self.assertEqual(len(self.transport.calls), 1)

    def test_reconcile_proves_effect_without_native_replay_and_preserves_unknown(self):
        plan = self.plan(self.intent())
        self.dispatch(plan, readback=False)
        key = plan.actions[0].transaction_key
        dispatcher = NativeActionDispatcher(self.service, self.journal)
        negative = dispatcher.reconcile_unknown(self.ctx, key,
                     observer=lambda c, i: ReadbackEvidence(digest(asdict(c)), digest(asdict(i)), 'OFFLINE_NEGATIVE', False))
        self.assertEqual(negative.outcome, 'UNKNOWN_EXECUTION_OUTCOME')
        positive = dispatcher.reconcile_unknown(self.ctx, key,
                     observer=lambda c, i: ReadbackEvidence(digest(asdict(c)), digest(asdict(i)), 'OFFLINE_POSITIVE', True))
        self.assertEqual(positive.outcome, 'APPLIED_READBACK_CONFIRMED')
        self.assertEqual(len(self.transport.calls), 1)
        record = self.journal.root / self.ctx.scope / key
        self.assertTrue((record / 'native_result.json').is_file())
        self.assertTrue((record / 'result_before_reconciliation.json').is_file())
        self.assertEqual(self.dispatch(plan)[0].outcome, 'APPLIED_READBACK_CONFIRMED')
        self.assertEqual(len(self.transport.calls), 1)

    def test_role_requests_are_recorded_not_transformed_into_native_actions(self):
        aid = 'PLAYER.AGENCY.TRADE_REQUEST'
        player = replace(self.coach, role_type='PLAYER', actor_uid='player7239',
                         player_scope=(7239,), allowed_actions=frozenset({aid}))
        self.profiles = [player]
        self.grants = {(player.actor_uid, aid)}
        request = ActionIntent.decided('request', player.actor_uid, aid,
                   {'player_uid': 7239, 'preferred_team_uids': [1], 'conditions': 'decided by player'})
        plan = self.plan(request)
        self.assertFalse(plan.issues)
        self.assertEqual(self.dispatch(plan)[0].outcome, 'EXTERNAL_REQUEST_RECORDED')
        self.assertFalse(self.transport.calls)
        other = replace(request, intent_id='impersonate', parameters_json=request.parameters_json.replace('7239', '7716'))
        self.assertTrue(self.plan(other, batch_id='other').issues)

    def test_four_additional_poe_requirements_reuse_known_apply_without_new_claims(self):
        for suffix, field, value in [('POE_O2', 'POEOffense2', 8), ('POE_O3', 'POEOffense3', 11),
                                      ('POE_D2', 'POEDefense2', 17), ('POE_D3', 'POEDefense3', 20)]:
            aid = 'COACH.STRATEGY.' + suffix
            self.profiles = [replace(self.coach, allowed_actions=frozenset({aid}))]
            self.grants = {('coach20', aid)}
            intent = ActionIntent.decided(suffix, 'coach20', aid, {'team_id': 20, 'settings': {field: value}})
            plan = self.plan(intent, batch_id=suffix)
            self.assertFalse(plan.issues)
            desc = self.service.describe_action(aid, self.profiles[0])
            self.assertEqual(desc['source_maturity'], 'STATIC')
            self.assertIsNone(desc['historical_exact_live_evidence'])
            self.assertTrue(desc['call_logic_available'])
            values = self.service.get_allowed_values(aid, self.profiles[0])['field_values']
            self.assertEqual(list(values), [field])

    def test_equivalent_trade_execution_routes_all_use_direct_process(self):
        for aid in ['GM.TRADE.EXECUTE_AGREED', 'GM.TRADE.PICK_ONLY', 'GM.TRADE.MULTI_PLAYER', 'GM.TRADE.MIXED']:
            self.assertEqual(self.service.mapping[aid], 'TRADE_EXECUTE_AGREED_PACKAGE')

    def test_context_lock_serializes_independent_dispatchers(self):
        with self.journal.lock(self.ctx.scope):
            with self.assertRaises(OSError):
                with ExecutionJournal(self.temp.name).lock(self.ctx.scope):
                    self.fail('Concurrent scope lease')
        with self.journal.lock(self.ctx.scope):
            pass

    def test_collection_binds_model_claims_to_authenticated_host_identity(self):
        aggregator = ExecutionAggregator(self.service)
        batch = RoleActionBatch('source', self.ctx, (self.intent(),))
        merged = aggregator.collect([(self.coach, batch)], aggregate_batch_id='aggregate')
        self.assertEqual(merged.intents, batch.intents)
        forged = replace(self.intent(), issuer_uid='other-coach')
        with self.assertRaises(PermissionError):
            aggregator.collect([(self.coach, replace(batch, intents=(forged,)))], aggregate_batch_id='forged')
        with self.assertRaises(ValueError):
            aggregator.collect([(self.coach, batch),
                 (self.coach, replace(batch, context=replace(self.ctx, save_instance_id='other')))], aggregate_batch_id='mixed')

    def test_json_ingestion_freezes_payload_and_rejects_extra_authority_fields(self):
        obj = {'batch_id': 'json', 'context': asdict(self.ctx), 'intents': [{
            'intent_id': 'one', 'issuer_uid': 'coach20', 'action_id': 'COACH.STRATEGY.RUN_PLAY',
            'parameters': {'team_id': 20, 'settings': {'RunPlayTendency': 55}}}]}
        batch = RoleActionBatch.from_dict(obj)
        obj['intents'][0]['parameters']['settings']['RunPlayTendency'] = 90
        self.assertEqual(batch.intents[0].parameters['settings']['RunPlayTendency'], 55)
        obj['intents'][0]['allowed_actions'] = ['ANY']
        with self.assertRaises(ValueError):
            RoleActionBatch.from_dict(obj)


if __name__ == '__main__':
    unittest.main()
