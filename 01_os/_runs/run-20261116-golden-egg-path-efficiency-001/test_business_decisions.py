"""Executable v2 cases. --before uses an explicitly naive fixture, not Core history."""
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RUNNER = ROOT / '01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py'
spec = importlib.util.spec_from_file_location('golden_loop', RUNNER)
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)
BEFORE = '--before' in sys.argv
if BEFORE:
    sys.argv.remove('--before')


def fact(value=True, **bindings):
    return {'value': value, 'bindings': bindings, 'source_ref': 'fixture-observation'}


def step(key, *, kind='business', needs=(), **kw):
    return dict(step_id=key, goal=key, kind=kind, requires=list(needs),
                depends_on=[], done=key + '_done', scope='research', **kw)


def state(steps):
    return {'goal': 'observable research', 'parent_done': 'research_done',
            'context': {'pid': 1, 'worldline': 'old'},
            'facts': {'research_done': fact(False)}, 'approved_choices': {},
            'steps': steps, 'blockers': {}, 'attempted': [],
            'unknown_resources': [], 'stopped_channels': []}


def naive(s):
    """Known bad policy: rerun first entry, reseed decisions, do no preflight ordering."""
    choice = copy.deepcopy(s['approved_choices'])
    if s['context']['worldline'] != 'old':
        for rows in choice.values():
            rows[0]['target'] += 1
    return {'status': 'READY', 'step_id': s['steps'][0]['step_id'],
            'approved_choices': choice}


def decide(s):
    return naive(s) if BEFORE else loop.next_business_action(s)


class EngineeringCases(unittest.TestCase):
    def test_T01_unavailable_object_no_repeat_and_fetch_refresh(self):
        s = state([step('local_show', needs=['object_available']),
                   step('reachable_source', needs=['remote_available'])])
        s['context']['git_generation'] = 0
        s['facts'].update(object_available=fact(False, git_generation=0),
                          remote_available=fact(True))
        self.assertEqual(decide(s)['step_id'], 'reachable_source')
        s['context']['git_generation'] = 1
        s['facts']['object_available'] = fact(True, git_generation=1)
        self.assertEqual(decide(s)['step_id'], 'local_show')

    def test_T02_approved_twenty_rows_survive_worldline_rebind(self):
        rows = [dict(uid=i, field='F', before=50, target=55) for i in range(20)]
        s = state([step('approved_intervention', needs=['fresh_assignment'], choice_ref='W01')])
        s['approved_choices']['W01'] = rows
        s['context'].update(pid=2, worldline='new')
        s['facts']['fresh_assignment'] = fact(True, pid=2)
        original = copy.deepcopy(s)
        self.assertEqual(decide(s)['approved_choices']['W01'], rows)
        self.assertEqual(s, original)
        if not BEFORE:
            s['steps'][0]['proposed_choice'] = [dict(rows[0], target=1)]
            self.assertEqual(decide(s)['status'], 'BLOCKED')

    def test_T03_invalidate_only_epoch_dependent_evidence(self):
        s = state([step('native_action', needs=['native']), step('refresh_native', kind='preflight')])
        s['context']['pid'] = 2
        s['facts'].update(native=fact(True, pid=1), provenance=fact(True),
                          approved=fact(True))
        d = decide(s)
        self.assertEqual(d['invalidated'], {'native': ['pid']})
        self.assertIn('provenance', d['reused'])
        self.assertIn('approved', d['reused'])
        self.assertEqual(d['step_id'], 'refresh_native')

    def test_T04_read_authority_does_not_cover_write(self):
        s = state([step('write', needs=['exact_setter_authority']),
                   step('read', needs=['exact_admin_read_authority'])])
        s['facts'].update(research_purpose=fact(True), exact_admin_read_authority=fact(True))
        d = decide(s)
        self.assertEqual(d['step_id'], 'read')
        self.assertIn('exact_setter_authority', str(d['blocked']))

    def test_T05_unknown_reserves_resource_but_safe_work_continues(self):
        s = state([step('sim', resource='save5'), step('other_write', resource='save5'),
                   step('unrelated_safe', resource='offline')])
        s['unknown_resources'] = ['save5']
        s['attempted'] = ['sim']
        for _ in range(2):
            d = decide(s)
            self.assertEqual(d['step_id'], 'unrelated_safe')
            self.assertIn('RECONCILE', str(d['blocked']))

    def test_T06_children_and_qualification_do_not_prove_parent_done(self):
        s = state([step('qualification'), step('capture')])
        s['facts'].update(qualification_done=fact(True), capture_done=fact(True))
        self.assertEqual(decide(s)['status'], 'PARENT_INCOMPLETE')
        s['facts']['research_done'] = fact(True)
        self.assertEqual(decide(s)['status'], 'DONE')

    def test_T07_partial_day_guard_blocks_before_dispatch(self):
        finals = list(range(199, 203))
        pending = list(range(203, 210))
        controls = list(range(210, 213))
        original = copy.deepcopy((finals, pending, controls))
        s = state([step('simulate', needs=['fixture_pending_compatible'])])
        s['facts']['fixture_pending_compatible'] = fact(not bool(finals))
        d = decide(s)
        self.assertEqual(d['status'], 'BLOCKED')
        self.assertIsNone(d['step_id'])
        self.assertEqual((finals, pending, controls), original)

    def test_T08_existing_frozen_digest_and_role_guards(self):
        path = RUNNER.with_name('test_minimum_operational_loop.py')
        spec = importlib.util.spec_from_file_location('existing_loop_tests', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        names = ['test_unfrozen_tests', 'test_test_digest_drift', 'test_review_independence']
        suite = unittest.TestSuite(module.MinimumLoopTests(name) for name in names)
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        self.assertTrue(result.wasSuccessful(), result.errors + result.failures)

    def test_T09_decisive_safe_check_precedes_optional_setup(self):
        s = state([step('allocator_ui', kind='optional'),
                   step('fixture_check', kind='preflight', needs=['identity', 'permission'])])
        s['facts'].update(identity=fact(True), permission=fact(True))
        self.assertEqual(decide(s)['step_id'], 'fixture_check')
        s['blockers']['research'] = 'Schedule fixture differs:199'
        s['facts']['fixture_check_done'] = fact(True)
        self.assertEqual(decide(s)['status'], 'BLOCKED')
        self.assertIn('fixture differs', str(decide(s)['blocked']))

    def test_T10_known_local_path_and_bounded_unknown_probe(self):
        s = state([step('remote', needs=['remote_usable']), step('local', needs=['local_usable'])])
        s['facts'].update(remote_usable=fact(False), local_usable=fact(True))
        self.assertEqual(decide(s)['step_id'], 'local')
        s['steps'].insert(0, step('probe', kind='preflight'))
        s['attempted'] = ['probe']
        self.assertEqual(decide(s)['step_id'], 'local')

    def test_T11_standing_scope_reused_and_ui_stopped(self):
        s = state([step('ui', kind='preflight', channel='computer_use'),
                   step('ask_again', kind='optional', needs=['new_scope']),
                   step('admin_read', needs=['admin_read_0005'])])
        s['facts']['admin_read_0005'] = fact(True)
        s['stopped_channels'] = ['computer_use']
        self.assertEqual(decide(s)['step_id'], 'admin_read')
        self.assertIs(s['facts']['admin_read_0005']['value'], True)

    def test_T12_one_affected_difference_query_then_stop(self):
        s = state([step('sim'), step('difference_query', kind='diagnostic')])
        s['blockers']['research'] = 'Schedule fixture differs'
        self.assertEqual(decide(s)['step_id'], 'difference_query')
        s['attempted'] = ['difference_query']
        self.assertEqual(decide(s)['status'], 'BLOCKED')
        self.assertNotIn('framework', str(decide(s)))

    def test_T13_time_layers_are_not_wall_time(self):
        metrics = dict(tool_call=35, tool_result=38, command=84, file_change=8, mcp=12,
                       command_seconds='318.113532', mcp_seconds='28.0956785',
                       monitor_on_seconds=['979.259', '1782.465'],
                       capture_seconds='61.035212', off_intervals='present',
                       human_wait_seconds=None, unknown_seconds=None)
        r = loop.business_time_quality(metrics)
        self.assertEqual(r['execution_items'], 104)
        self.assertEqual(r['records'], 177)
        self.assertEqual(r['mcp_seconds_sum'], '28.0956785')
        self.assertEqual(r['monitor_on_reported_seconds'], '2761.724')
        self.assertIsNone(r['unique_tool_wall_seconds'])
        self.assertEqual(r['unobserved_attribution'], 'UNKNOWN')
        self.assertIsNone(r['human_wait_seconds'])

    def test_T14_path_latency_is_observation_not_safety_gate(self):
        r = loop.business_time_quality({}, first_event='2026-11-16T11:11:19.027Z',
              first_blocker='2026-11-16T11:53:21.519Z', capture_end='2026-11-16T11:36:52.264316Z')
        self.assertEqual(r['event_span_to_blocker_seconds'], '2522.492')
        self.assertAlmostEqual(float(r['capture_to_blocker_seconds']), 989.254684)
        self.assertEqual(r['safety_effect'], 'none')

    def test_actual_runner_cli_uses_decision_function(self):
        s = state([step('optional_documentation', kind='optional'),
                   step('engineering_regression', kind='preflight')])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'input.json'
            path.write_text(json.dumps(s), encoding='utf-8')
            r = subprocess.run([sys.executable, '-B', str(RUNNER), 'next-business-action', str(path)],
                               capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads(r.stdout)['step_id'], 'engineering_regression')

    def test_input_is_exact_v2_and_T15_stays_deferred(self):
        raw = (HERE / 'engineering_tests_v2.yml').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         '9b871027c2a5898b429e0ee1f900c9c1ebd169f8c91643ecb91f64811ac51b43')
        self.assertIn(b'deferred_parent_validation:', raw)

    def test_dependencies_cannot_be_bypassed_by_priority(self):
        a = step('check', kind='preflight')
        a['depends_on'] = ['prepare_identity']
        s = state([a, step('prepare_identity')])
        self.assertEqual(decide(s)['step_id'], 'prepare_identity')

    def test_false_or_missing_binding_is_never_ready(self):
        s = state([step('protected', needs=['permission'])])
        s['facts']['permission'] = fact(True, absent_context_key=None)
        self.assertEqual(decide(s)['status'], 'BLOCKED')

    def test_missing_time_evidence_is_unknown_and_bad_evidence_rejected(self):
        r = loop.business_time_quality({})
        for key in ('execution_items', 'records', 'command_seconds_sum',
                    'mcp_seconds_sum', 'monitor_on_reported_seconds'):
            self.assertIsNone(r[key])
        for bad in ('unmeasured', -1, 'NaN', True):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                loop.business_time_quality({'human_wait_seconds': bad})
        with self.assertRaises(ValueError):
            loop.business_time_quality({}, first_event='2026-11-16T11:00:00',
                                       first_blocker='2026-11-16T11:01:00')


if __name__ == '__main__':
    if BEFORE:
        names = [name for name in unittest.defaultTestLoader.getTestCaseNames(EngineeringCases)
                 if name.startswith(('test_T01_', 'test_T02_', 'test_T09_'))]
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.TestSuite(EngineeringCases(name) for name in names))
        # Exit 1 is the expected negative experiment only when ALL three fail
        # by assertion. Import errors or an accidentally passing naive case do
        # not qualify as the required before evidence.
        raise SystemExit(1 if len(names) == 3 and len(result.failures) == 3
                         and not result.errors else 2)
    unittest.main(verbosity=2)
