"""Exactly the five DEV20-authorized objective checks; isolated evidence and SQLite."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT/'scripts/gm_development_feedback.py'


class M4ObjectiveChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = self.root/'derived/gm_workbench.sqlite'
        self.serial = 0
        self.sample = json.loads((ROOT/'examples/development_feedback/issue6.json').read_text(encoding='utf-8'))
        self.sample['source'].update(producer='SYNTHETIC_M4_IMPORT_TEST', source_batch='SYNTHETIC_B1')
        self.readiness = json.loads((ROOT/'config/m4_readiness_evidence.json').read_text(encoding='utf-8'))
        self.evidence = self.put(self.readiness)
        self.fact = self.root/'snapshot_fact.json'
        self.fact.write_text('{"synthetic_observed_fact": 42}', encoding='utf-8')
        self.before = self.fact.read_bytes()

    def tearDown(self):
        self.assertEqual(self.fact.read_bytes(), self.before)
        self.tmp.cleanup()

    def put(self, obj):
        self.serial += 1
        path = self.root/('input_'+str(self.serial)+'.json')
        path.write_text(json.dumps(obj, ensure_ascii=False), encoding='utf-8')
        return path

    def cli(self, *args, code=0):
        result = subprocess.run([sys.executable, '-B', str(CLI), *map(str, args), '--workbench', str(self.db),
            '--readiness-evidence', str(self.evidence)], cwd=ROOT, capture_output=True, encoding='utf-8',
            env=dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8'), timeout=20)
        self.assertEqual(result.returncode, code, result.stdout+result.stderr)
        return json.loads(result.stdout)

    def ingest(self, obj=None):
        return self.cli('ingest', '--input', self.put(obj or self.sample))

    def test_01_event_import_storage_and_evidence_trace_without_fact_write(self):
        saved = self.ingest()
        self.assertEqual(saved['issue']['occurrences'], 1)
        self.assertEqual(saved['issue']['status'], 'DEFERRED')
        issue_id = saved['issue']['issue_id']
        shown = self.cli('show', '--issue', issue_id)
        self.assertEqual(shown['issue']['latest_source']['error_code'], 'UNKNOWN_PLAYER_POTENTIAL_JSON_MIRROR')
        self.assertEqual(shown['issue']['latest_confidence'], 'STATIC_REPORT')
        self.assertIn('https://github.com/chris2gao/nba2k22-gm-engine/issues/6', shown['issue']['evidence_refs'])
        event = self.cli('show', '--issue', issue_id, '--event-key', shown['history']['rows'][0]['event_key'])['event']
        self.assertEqual(event['source']['source_batch'], 'SYNTHETIC_B1')
        self.assertEqual(event['repro_steps'], self.sample['repro_steps'])
        self.assertFalse(shown['execution_authorized'])

    def test_02_cross_batch_dedup_idempotence_scope_and_history(self):
        first = self.ingest(); same = self.ingest()
        self.assertEqual(same['result'], 'IDEMPOTENT_REPLAY')
        self.assertEqual(same['issue']['revision'], 1)
        second = deepcopy(self.sample)
        second.update(event_id='NEW_BATCH_EVENT', occurred_at='2026-10-21T10:20:13+00:00', status='OPEN', player_decision_ref='')
        second['source']['source_batch'] = 'SYNTHETIC_B2'
        repeated = self.ingest(second)
        self.assertEqual(repeated['issue']['issue_id'], first['issue']['issue_id'])
        self.assertEqual(repeated['issue']['occurrences'], 2)
        self.assertEqual(repeated['issue']['status'], 'DEFERRED')
        history = self.cli('show', '--issue', first['issue']['issue_id'])['history']['rows']
        self.assertEqual({e['source']['source_batch'] for e in history}, {'SYNTHETIC_B1', 'SYNTHETIC_B2'})
        changed = deepcopy(self.sample); changed['title'] = 'Changed content with reused event ID'
        conflict = self.cli('ingest', '--input', self.put(changed), code=2)
        self.assertIn('EVENT_ID_REUSE', conflict['error'])
        distinct = deepcopy(self.sample); distinct.update(event_id='OTHER_ERROR', root_cause_key='DIFFERENT_ROOT_CAUSE')
        self.assertNotEqual(self.ingest(distinct)['issue']['issue_id'], first['issue']['issue_id'])
        scoped = []
        for kind in ('CAREER', 'IDENTITY'):
            for career in ('SYNTHETIC_A', 'SYNTHETIC_B'):
                item = deepcopy(self.sample); item['event_id'] = 'LOCAL_ERROR_001'
                item['scope'] = dict(kind=kind, career_id=career)
                if kind == 'IDENTITY':
                    item['scope'].update(save_instance_id=career+'_INSTANCE', identity_key='player:1')
                item['source'].update(career_id=career, save_instance_id=career+'_INSTANCE')
                saved = self.ingest(item)
                scoped.append(saved['issue']['issue_id'])
                replay = self.ingest(item)
                self.assertEqual(replay['result'], 'IDEMPOTENT_REPLAY')
                self.assertEqual(replay['issue']['occurrences'], 1)
                changed = deepcopy(item); changed['actual'] = 'Changed content in the same scope'
                error = self.cli('ingest', '--input', self.put(changed), code=2)
                self.assertIn('EVENT_ID_REUSE', error['error'])
                shown = self.cli('show', '--issue', saved['issue']['issue_id'])
                self.assertEqual(shown['issue']['revision'], 1)
                self.assertEqual(shown['history']['rows'][0]['source']['career_id'], career)
        self.assertEqual(len(set(scoped+[first['issue']['issue_id']])), 5)

    def test_03_manual_status_revision_and_approval_boundaries(self):
        item = deepcopy(self.sample)
        item.update(root_cause_key='SYNTHETIC_ACCESS_FAILURE', event_id='TRIAGE_TEST', title='Synthetic access report only', status='OPEN', player_decision_ref='')
        item['source']['error_code'] = 'SYNTHETIC_ACCESS_FAILURE'
        ident = self.ingest(item)['issue']['issue_id']
        patch = dict(status='TRIAGED', reason='Synthetic human review', player_decision_ref='')
        self.assertIn('actual_player_decision_reference', self.cli('triage', '--issue', ident, '--input', self.put(patch), '--expected-revision', 1, code=2)['error'])
        patch.update(status='APPROVED', player_decision_ref='SYNTHETIC_USER_CONTEXT')
        self.assertEqual(self.cli('triage', '--issue', ident, '--input', self.put(patch), '--expected-revision', 1, code=2)['status'], 'ERROR')
        patch['status'] = 'TRIAGED'
        self.assertEqual(self.cli('triage', '--issue', ident, '--input', self.put(patch), '--expected-revision', 1)['issue']['revision'], 2)
        patch['status'] = 'DEFERRED'
        self.assertIn('REVISION_CONFLICT', self.cli('triage', '--issue', ident, '--input', self.put(patch), '--expected-revision', 1, code=2)['error'])
        self.cli('triage', '--issue', ident, '--input', self.put(patch), '--expected-revision', 2)
        again = deepcopy(item); again['event_id'] = 'AFTER_TRIAGE'; again['source']['source_batch'] = 'SYNTHETIC_B2'
        self.assertEqual(self.ingest(again)['issue']['status'], 'DEFERRED')
        patch['status'] = 'RESOLVED'
        self.assertIn('FIX_EVIDENCE', self.cli('triage', '--issue', ident, '--input', self.put(patch), '--expected-revision', 4, code=2)['error'])
        patch['evidence_refs'] = ['tests/test_m4_system_evolution.py']
        resolved = self.cli('triage', '--issue', ident, '--input', self.put(patch), '--expected-revision', 4)
        self.assertEqual(resolved['issue']['status'], 'RESOLVED')
        self.assertFalse(resolved['execution_authorized'])
        forged = dict(patch, approved=True)
        self.assertIn('AUTHORITY', self.cli('triage', '--issue', ident, '--input', self.put(forged), '--expected-revision', 5, code=2)['error'])

    def test_04_bounded_queries_small_export_and_reference_only_payloads(self):
        identifiers = []
        for n in range(3):
            obj = deepcopy(self.sample); obj.update(event_id='PAGE_'+str(n), root_cause_key='PAGE_ROOT_'+str(n))
            identifiers.append(self.ingest(obj)['issue']['issue_id'])
        page = self.cli('list', '--limit', 1)
        self.assertEqual(page['row_count'], 1); self.assertTrue(page['truncated'])
        seen = [page['rows'][0]['issue_id']]
        while page['next_cursor']:
            page = self.cli('list', '--limit', 1, '--cursor', page['next_cursor'])
            seen.extend(r['issue_id'] for r in page['rows'])
        self.assertEqual(set(seen), set(identifiers))
        self.assertEqual(len(self.cli('list', '--status', 'DEFERRED')['rows']), 3)
        extra = deepcopy(self.sample); extra.update(event_id='HISTORY_PAGE', root_cause_key='PAGE_ROOT_0')
        self.ingest(extra)
        history = self.cli('show', '--issue', identifiers[0], '--limit', 1)['history']
        self.assertEqual(history['row_count'], 1); self.assertTrue(history['truncated'])
        bad = dict(extra, raw_struct='deadbeef')
        self.cli('ingest', '--input', self.put(bad), code=2)
        bad = deepcopy(extra); bad['actual'] = 'Pointer 0x123456789ABC'
        self.cli('ingest', '--input', self.put(bad), code=2)
        bad = deepcopy(extra); bad['evidence_refs'] = ['C:/Users/private/debug.json']
        self.cli('ingest', '--input', self.put(bad), code=2)
        self.cli('list', '--limit', 51, code=2)
        self.cli('ingest', '--input', self.put(dict(extra, actual='X'*25000)), code=2)
        output = self.root/'handoff'
        exported = self.cli('export', '--output', output, '--limit', 2)
        self.assertEqual(exported['row_count'], 2); self.assertTrue(exported['truncated'])
        self.assertEqual(exported['publication'], 'NOT_REQUESTED')
        index = json.loads((output/'index.json').read_text(encoding='utf-8'))
        self.assertEqual(index['row_count'], 2)
        self.assertLess((output/'index.json').stat().st_size, 24000)
        current = (output/'CURRENT.md').read_text(encoding='utf-8')
        self.assertIn('DEFERRED', current); self.assertIn('GM_V4_NOT_ENABLED', current)
        self.assertIn('https://github.com/chris2gao/nba2k22-gm-engine/issues/6', current)
        self.assertNotIn('raw_struct', current); self.assertNotIn('C:/Users', current)
        self.cli('export', '--output', self.root/'published', code=2)
        self.cli('export', '--output', output, code=2)

    def test_05_readiness_reports_actual_gaps_and_never_activates_v4(self):
        current = self.cli('readiness')
        self.assertFalse(self.db.exists())
        self.assertEqual(current['pr4']['status'], 'MERGED')
        self.assertEqual(current['gm_status'], 'GM_V4_NOT_ENABLED')
        self.assertEqual(current['delivery_status'], 'M4_ENGINEERING_COMPLETE_AWAITING_PLAYER')
        self.assertEqual(current['gates']['actual_30_team_research']['status'], 'UNASSESSED')
        self.assertIn('M4_engineering_integration', current['blocked_conditions'])
        self.assertIn('issue6_fix', current['blocked_conditions'])
        self.assertIn('BPTI_before_new_save', current['blocked_conditions'])
        for role in ('DEVELOPMENT', 'ANALYTICS', 'GM'):
            self.assertEqual(current['gates']['web_'+role]['status'], 'PENDING')
        unmerged = deepcopy(self.readiness)
        unmerged['pr4'] = dict(status='OPEN', evidence_refs=['https://github.com/chris2gao/nba2k22-gm-engine/pull/4'], notes='Synthetic unmerged case')
        unmerged['gates'].pop('sanitized_production_capture')
        self.evidence = self.put(unmerged)
        report = self.cli('readiness')
        self.assertIn('PR4_MAIN_MERGE', report['blocked_conditions'])
        self.assertEqual(report['gates']['sanitized_production_capture']['status'], 'PENDING')
        self.assertEqual(report['gm_status'], 'GM_V4_NOT_ENABLED')
        self.ingest()
        self.assertEqual(self.cli('readiness')['issue6_local_record']['status'], 'DEFERRED')


if __name__ == '__main__':
    unittest.main()
