"""Direct M3 source, research, negotiation and immutable checkpoint acceptance."""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gm_core import analysis_packet as ap, decision_protocol as dp, market_negotiation as neg
from gm_core.analysis_metrics import interval, temporal_links
from gm_core.finance_projection import project
from gm_core.workbench_common import page, export_files
from gm_data_access.analysis_inputs import consume, screen
from gm_data_access.query import QuerySession
from gm_workbench.store import Store
from m3_fixtures import inputs,analysis,review,alternatives,complete,selection,offer,response,coaching_snapshot


class PacketTests(unittest.TestCase):
    def test_counter_deltas_zero_negative_and_identity_ambiguity(self):
        current=inputs()['team_stats'][0]['totals']; previous=deepcopy(current)
        previous.update(w=10,l=10,made=600,attempted=1400,**{'3pt_made':180,'3pt_attempted':500})
        r=interval(current,previous,True)
        self.assertEqual(r['metrics']['games']['value'],5)
        self.assertAlmostEqual(r['metrics']['efg']['value'],190/350)
        self.assertNotEqual(r['metrics']['efg']['value'],ap.metrics(current,'c')['efg']['value']-ap.metrics(previous,'p')['efg']['value'])
        current['attempted']=1397; current['w']=10; current['l']=10
        r=interval(current,previous,True)
        self.assertEqual(r['status'],'NO_NEW_GAMES'); self.assertIsNone(r['metrics']['efg']['value'])
        self.assertEqual(r['metrics']['assist_turnover_ratio']['unknown_reason'],'ZERO_OR_INVALID_DENOMINATOR')
        self.assertEqual(interval(current,previous,False)['status'],'NOT_COMPARABLE')
        p=inputs()['players'][0]; old=deepcopy(p); old['identity']='old:0'
        old['attributes']['3pt_shot']['value']=50
        self.assertEqual(temporal_links([p],[old])[0]['status'],'TEMPORAL_CANDIDATE')
        self.assertEqual(temporal_links([p],[old])[0]['provisional_changes']['attributes'][0]['delta'],25)
        self.assertEqual(temporal_links([p],[old,old])[0]['status'],'AMBIGUOUS')
        self.assertFalse(temporal_links([p],[old])[0]['verified_growth'])

    def test_fact_annotations_seal_and_local_staff_gap(self):
        a=analysis()
        self.assertEqual(a['status'],'SEALED_COMPLETE')
        self.assertEqual(ap.team(a,0)['player_supply']['players'][0]['decoded_attributes']['3pt_shot'],75)
        self.assertEqual(ap.team(a,0)['observed_performance']['cumulative']['games']['value'],25)
        self.assertEqual(a['issue_index'][0]['code'],'STAFF_SOURCE_GAP')
        self.assertIsNone(ap.team(a,0)['observed_performance']['cumulative']['offensive_rating']['value'])
        self.assertEqual(ap.evidence(a,'team_stats:0:made')['value'],760)
        with self.assertRaisesRegex(ValueError,'IMMUTABLE'):ap.annotate(a,dict(teams=[]))
        a=ap.prepare(inputs(),'2021-2022','CHECKPOINT')
        with self.assertRaisesRegex(ValueError,'AUTHORITY'):ap.annotate(a,dict(approved=True,teams=[]))
        self.assertEqual(ap.seal(a)['status'],'SEALED_PARTIAL')

    def test_unidentified_old_pick_does_not_break_unrelated_evidence(self):
        data=inputs();data['picks']=[dict(asset_id=None,team_id=0,trade_eligible=None)]
        a=ap.prepare(data,'2021-2022','CHECKPOINT')
        self.assertEqual(ap.evidence(a,'team_stats:29:made')['value'],760)

    def test_byte_limited_consumption_and_bound_cursors(self):
        class Session:
            available={'players':True}; binding={'batch_id':'synthetic'}
            def query(self,entity,fields,limit,cursor):
                return dict(rows=[dict(identity='p1' if cursor is None else 'p2')],truncated=cursor is None,next_cursor='continue' if cursor is None else None)
        receipts=[]
        self.assertEqual(len(consume(Session(),'players',['identity'],receipts)),2)
        self.assertEqual(receipts[0]['pages'],2); self.assertTrue(receipts[0]['cursor_exhausted'])
        rows=[dict(id=i,text='x'*200) for i in range(6)]
        p=page(rows,['A',1],5,budget=600)
        self.assertLess(p['row_count'],5)
        with self.assertRaisesRegex(ValueError,'CURSOR'):page(rows,['A',2],5,p['next_cursor'])


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'gm_workbench.sqlite'
        self.s=Store(self.path); self.a,self.d=complete(self.s)
    def tearDown(self):
        self.s.close(); self.tmp.cleanup()
    def change(self,command,payload):
        updated,art=dp.apply(self.d,self.a,command,payload)
        self.d=self.s.save_decision(updated,self.d['revision'],art)
    def add_agreed(self,payload):
        self.change('submit-offer',payload)
        o=self.d['artifacts']['OFFER'][payload['offer_id']]['payload']
        for t in o['team_ids']:self.change('respond-offer',response(o,t))
        return o
    def select(self,p):self.change('select',p)
    def validate(self,finance=None,snapshot=None):
        d,art=dp.validate(self.d,self.a,finance,snapshot)
        self.d=self.s.save_decision(d,self.d['revision'],art)
        return self.d['artifacts']['VALIDATION']['current']['payload']

    def test_exact_identities_and_research_invalidation(self):
        r=review(self.a,0); r['player_assessments'][0]['source_identity']='replacement-same-count'
        with self.assertRaisesRegex(ValueError,'EXACT_ROSTER'):self.change('submit-review',r)
        self.change('submit-review',review(self.a,0))
        self.assertFalse(dp.progress(self.d)['all_teams_ready'])
        with self.assertRaisesRegex(ValueError,'P1_P2'):self.change('submit-offer',offer())

    def test_bilateral_same_version_counter_and_no_deal(self):
        o=self.add_agreed(offer())
        self.assertEqual(dp.summary(self.d)['offers'][0]['status'],'AGREED_IN_PRINCIPLE')
        counter=response(o,1,'COUNTER'); counter['conditions']=['Different role return required']
        self.change('respond-offer',counter)
        self.assertEqual(dp.summary(self.d)['offers'][0]['status'],'NEGOTIATING')
        self.change('respond-offer',response(o,1,'REJECT'))
        self.assertEqual(dp.summary(self.d)['offers'][0]['status'],'NO_DEAL')
        new=offer(); new['conditions']=['New complete terms']
        self.change('submit-offer',new)
        with self.assertRaisesRegex(ValueError,'STALE_OFFER'):self.change('respond-offer',response(o,0))
        self.assertEqual(dp.summary(self.d)['offers'][0]['status'],'NEGOTIATING')
        forged=response(self.d['artifacts']['OFFER']['O']['payload'],0); forged['approved']=True
        with self.assertRaisesRegex(ValueError,'AUTHORITY'):self.change('respond-offer',forged)
        terms=neg.canonical_terms(self.a['source_binding'],[1,0],o['moves'],[],[])
        self.assertEqual(neg.digest(terms),o['terms_digest'])
        invalid=offer();invalid['conditions']=[dict(amount=1.5)]
        with self.assertRaisesRegex(ValueError,'INTEGER_MONETARY'):neg.offer(invalid,self.d,self.a,3)
        invalid=offer();invalid['moves'][0]['asset_id']='ambiguous-second-asset-key'
        with self.assertRaisesRegex(ValueError,'EXACT_PLAYER_IDENTITY'):neg.offer(invalid,self.d,self.a,3)

    def test_candidate_competition_selected_conflict_and_supported_trade(self):
        o1=self.add_agreed(offer('O1')); o2=self.add_agreed(offer('O2',0,2))
        p=selection((0,1,2)); p['selected_offer_versions']=[dict(offer_id=o['offer_id'],terms_revision=o['terms_revision']) for o in (o1,o2)]
        p['team_combination_reviews']=[dict(team_id=0,selected_ids=['O1','O2'],team_interest_revision=1,why_better_than_hold='Synthetic combined interest',evidence_refs=['team:0'])]
        self.select(p); v=self.validate()
        self.assertFalse(v['valid_for_finalization']); self.assertIn('SELECTED_ASSET_CONFLICT',{i['code'] for i in v['issues']})
        p=selection((0,1));p['selected_offer_versions']=[dict(offer_id='O1',terms_revision=1)]
        self.select(p);v=self.validate()
        self.assertTrue(v['valid_for_finalization'])
        self.assertEqual(v['specific_approval_items'][0]['executor_readiness'],'REQUIRES_LIVE_TRADE_PLAN')
        self.assertFalse(v['execution_authorized'])

    def test_overlapping_team_dependency_separate_from_duplicate_assets(self):
        self.add_agreed(offer('O1')); self.add_agreed(offer('O2',2,0))
        p=selection((0,1,2)); p['selected_offer_versions']=[dict(offer_id=o,terms_revision=1) for o in ('O1','O2')]
        p['team_combination_reviews']=[dict(team_id=0,selected_ids=['O1','O2'],team_interest_revision=1,why_better_than_hold='Synthetic aggregate',evidence_refs=['team:0'])]
        self.select(p);v=self.validate()
        self.assertTrue(v['valid_for_finalization'])
        self.assertEqual(v['specific_approval_items'],[])
        self.assertEqual({i['executor_readiness'] for i in v['research_items']},{'DEPENDENCY_UNSUPPORTED'})

    def test_atomic_revisions_final_history_and_m1_m2_compatibility(self):
        finance=project(inputs(),'2021-2022',run_id='finance')
        self.s.save_run(finance)
        self.select(selection()); v=self.validate()
        self.assertTrue(v['valid_for_finalization'])
        before=self.d['revision']
        d,art=dp.finalize(self.d,self.a)
        with self.assertRaisesRegex(ValueError,'REVISION_CONFLICT'):self.s.save_decision(d,before-1,art)
        self.assertEqual(self.s.load_decision(self.d['decision_run_id'])['revision'],before)
        self.d=self.s.save_decision(d,before,art)
        self.assertEqual(self.d['current_final_version'],1)
        final=self.s.artifact_history(self.d['decision_run_id'],'FINAL','final',1)
        self.assertEqual(len(final['team_summaries']),30); self.assertEqual(final['specific_approval_items'],[])
        self.assertEqual(len(final['strategy_candidates']),30)
        self.assertEqual(self.s.list_states('synthetic'),[])
        candidate=final['strategy_candidates'][0]
        self.s.save_state(candidate['candidate_state'],candidate['expected_revision'])
        self.assertEqual(self.s.load_state('synthetic','0')['revision'],1)
        self.assertEqual(self.s.load_run('finance')['run_id'],'finance')
        self.select(selection());self.assertIsNone(self.d['current_final_version'])
        self.validate(); d,art=dp.finalize(self.d,self.a); self.d=self.s.save_decision(d,self.d['revision'],art)
        self.assertEqual(self.d['current_final_version'],2)
        self.assertEqual(self.s.artifact_history(self.d['decision_run_id'],'FINAL','final',1),final)
        with Store(self.path,readonly=True) as reader:
            self.assertEqual(reader.load_decision(self.d['decision_run_id'])['current_final_version'],2)

    def test_workbench_export_protection_and_sealed_market_supplement(self):
        receipt=dict(query=dict(query_id='Q',source_domain='pool'),source_binding=self.a['source_binding'],returned_identities=[],rows=[],status='SCREENED')
        self.s.save_market(self.a['analysis_run_id'],receipt)
        self.assertEqual(self.s.load_analysis(self.a['analysis_run_id']),self.a)
        changed=deepcopy(receipt);changed['query']['source_domain']='roster'
        with self.assertRaisesRegex(ValueError,'IMMUTABLE'):self.s.save_market(self.a['analysis_run_id'],changed)
        with self.assertRaisesRegex(ValueError,'IMMUTABLE'):self.s.save_analysis(self.a,1)
        with self.assertRaisesRegex(ValueError,'NOT_FACTS'):Store(Path(self.tmp.name)/'published/gm_workbench.sqlite')
        with self.assertRaisesRegex(ValueError,'TARGET_FACTS'):export_files(Path(self.tmp.name)/'published/analysis',{})

    def test_research_and_unselected_reasons_reach_final_without_rejecting_hold(self):
        p=selection();p['research_action_ids']=['market:0']
        p['rejected_alternatives']=[dict(alternative_id='internal:0',reason='Preserve current configuration pending evidence')]
        self.select(p);v=self.validate()
        self.assertEqual(v['research_items'][0]['item_id'],'market:0')
        d,art=dp.finalize(self.d,self.a);self.d=self.s.save_decision(d,self.d['revision'],art)
        f=self.s.artifact_history(self.d['decision_run_id'],'FINAL','final',1)
        self.assertEqual(len(f['alternatives_not_selected']),60)
        candidate=f['strategy_candidates'][0]['candidate_state']
        self.assertEqual(candidate['current_actions'][0]['status'],'HOLD')
        self.assertEqual([r['alternative_id'] for r in candidate['rejected_hypotheses']],['internal:0'])

    def test_coach_real_offline_generation_conflict_and_forged_digest(self):
        from gm_core.coaching_batch import batch_digest
        alts=alternatives(0)
        alts['alternatives'][1]['action']=dict(action_id='C0',kind='COACHING',requests=[dict(action_id='C0',team_id=0,targets={'POEOffense':2},expected_effect='Synthetic spacing hypothesis')])
        self.change('submit-alternatives',alts)
        p=selection((0,));p['selected_internal_action_versions']=[dict(team_id=0,alternative_id='internal:0',revision=2)]
        self.select(p);v=self.validate(snapshot=coaching_snapshot(self.a['source_binding']))
        artifact=v['generated_artifact_refs'][0]
        self.assertTrue(artifact['dry_run']['valid'])
        self.assertEqual(artifact['batch_digest'],batch_digest(artifact['batch']))
        self.assertEqual(v['specific_approval_items'][0]['batch_digest'],artifact['batch_digest'])
        _,final_artifacts=dp.finalize(self.d,self.a)
        final=next(obj for kind,_,obj in final_artifacts if kind=='FINAL')
        self.assertEqual(final['strategy_candidates'][0]['candidate_state']['current_actions'][0]['status'],'PROPOSED')
        forged=deepcopy(alts);forged['alternatives'][1]['action']['batch_digest']='pretend'
        with self.assertRaisesRegex(ValueError,'AUTHORITY'):self.change('submit-alternatives',forged)
        alt2=deepcopy(alts['alternatives'][1]);alt2['alternative_id']='internal:0b';alt2['action']['action_id']='C0b'
        alt2['action']['requests'][0].update(action_id='C0b',targets={'POEOffense':1})
        alts['alternatives'].append(alt2);self.change('submit-alternatives',alts)
        p['selected_internal_action_versions']=[dict(team_id=0,alternative_id=x,revision=3) for x in ('internal:0','internal:0b')]
        p['team_combination_reviews']=[dict(team_id=0,selected_ids=['C0','C0b'],team_interest_revision=1,why_better_than_hold='Synthetic conflict case',evidence_refs=['team:0'])]
        self.select(p);v=self.validate(snapshot=coaching_snapshot(self.a['source_binding']))
        self.assertFalse(v['valid_for_finalization']);self.assertIn('COACH_FIELD_CONFLICT',{i['code'] for i in v['issues']})

    def test_post_trade_coaching_pending_and_finance_combination(self):
        finance=project(inputs(),'2021-2022',run_id='F')
        self.a.update(finance_alignment='SAME_BATCH',finance_run_id='F')
        self.add_agreed(offer())
        alts=alternatives(0);alts['alternatives'][1]['action']=dict(action_id='C0',kind='COACHING',requests=[dict(action_id='C0',team_id=0,targets={'POEOffense':2},expected_effect='Synthetic post-trade adaptation')])
        self.change('submit-alternatives',alts)
        p=selection((0,1));p['selected_offer_versions']=[dict(offer_id='O',terms_revision=1)]
        self.assertEqual(dp.summary(self.d)['offers'][0]['status'],'NEGOTIATING')
        o=self.d['artifacts']['OFFER']['O']['payload']
        self.change('respond-offer',response(o,0))
        p['selected_internal_action_versions']=[dict(team_id=0,alternative_id='internal:0',revision=2)]
        p['team_combination_reviews']=[dict(team_id=0,selected_ids=['O','C0'],team_interest_revision=1,why_better_than_hold='Synthetic comparison after both changes',evidence_refs=['team:0'])]
        self.select(p);v=self.validate(finance,coaching_snapshot(self.a['source_binding']))
        self.assertTrue(v['valid_for_finalization'])
        self.assertEqual(len(v['specific_approval_items']),1)
        self.assertEqual(v['research_items'][0]['executor_readiness'],'POST_TRADE_COACHING_REPLAN_REQUIRED')
        self.assertEqual(v['finance_evidence']['kind'],'TRADE_OR_SIGNING')


class ProjectionTests(unittest.TestCase):
    def test_team_stats_filters_current_snapshot(self):
        from test_gm_data_access import fixture
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);q,pub,_,_=fixture(root,team_stats=True)
            s=QuerySession(q,pub,'synthetic')
            try:
                result=s.query('team_stats')
                self.assertEqual(len(result['rows']),2)
                self.assertEqual([r['totals']['w'] for r in result['rows']],[2,2])
                self.assertNotIn('raw_struct',json.dumps(result))
            finally:
                s.close()
                for f in root.rglob('*'):
                    if f.is_file():f.chmod(0o600)

    def test_new_team_stats_view_and_older_missing_source(self):
        # Reuse the M0 archive fixture; all files are isolated synthetic temporary copies.
        from test_gm_data_access import fixture
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); q,pub,_,_=fixture(root)
            s=QuerySession(q,pub,'synthetic')
            try:
                self.assertFalse(s.available['team_stats'])
                # An empty older source yields explicit unavailable, not invented rows.
                receipts=[];self.assertEqual(consume(s,'team_stats',['team_id','totals'],receipts),[])
                self.assertEqual(receipts[0]['status'],'SOURCE_UNAVAILABLE')
                result=screen(s,dict(query_id='Q',source_domain='roster',role_question='Explicit speed',
                    filters=[dict(native_field='attributes.speed.value',operator='gte',value=65)],excluded_team_ids=[0],
                    order_by=[dict(native_field='attributes.speed.value',direction='DESC')]),{'speed'},set(),2)
                self.assertEqual(result['matched_count'],3); self.assertEqual(result['filter_population_count'],3)
                self.assertEqual(len(result['rows']),2); self.assertFalse(result['cursor_exhausted'])
                self.assertEqual(result['unknown_required_field_count'],0)
                query=deepcopy(result['query']);query['filters'][0]['native_field']='attributes.made_up.value'
                with self.assertRaisesRegex(ValueError,'UNREGISTERED'):screen(s,query,{'speed'},set())
                poolq=dict(query_id='POOL',source_domain='pool',role_question='Missing skill is unknown',filters=[dict(native_field='attributes.speed.value',operator='gte',value=60)],excluded_team_ids=[],order_by=[])
                p=screen(s,poolq,{'speed'},set())
                self.assertEqual(p['matched_count'],0); self.assertEqual(p['unknown_required_field_count'],60)
            finally:
                s.close()
                for f in root.rglob('*'):
                    if f.is_file():f.chmod(0o600)


if __name__=='__main__':unittest.main()
