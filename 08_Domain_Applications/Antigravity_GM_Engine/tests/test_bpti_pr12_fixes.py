"""Four scoped PR #12 F1-F4 synthetic checks; no older suites or game access."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gm_core import analysis_packet as ap, decision_protocol as dp, bpti_decision as b4, bpti_evolution as b5
from gm_core import decision_portfolio as portfolio
from gm_core import market_negotiation
from gm_workbench.store import Store
import test_bpti_package_c as package_c
from test_m3_t_integration import review
from m3_fixtures import alternatives, selection, offer


class PR12FixChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        package_c.PackageCChecks.setUpClass()
        cls.h=package_c.PackageCChecks()
    @classmethod
    def tearDownClass(cls):
        package_c.PackageCChecks.tearDownClass()
    def write(self,s,d,a,command,payload,**kw):
        return self.h.write(s,d,a,command,payload,**kw)
    def review_all(self,s,d,a,market=False):
        for tid in d['expected_team_ids']:
            r=review(a,tid)
            if market and tid in (0,1):
                r['market_gap_after_internal_assessment']=dict(status='GAP_REMAINS',reason='Synthetic talent gap after internal comparison',evidence_refs=['team:'+str(tid)])
                r['rejected_internal_fixes']=[dict(reason='Current role and coaching cannot supply missing talent',evidence_refs=['team:'+str(tid)])]
            blue=d['artifacts'].get('BPTI_BLUEPRINT',{}).get(str(tid))
            if blue:r['bpti_blueprint_revision']=blue['revision']
            d=self.write(s,d,a,'submit-review',r)
            opts=alternatives(tid)
            if blue:opts['bpti_blueprint_revision']=blue['revision']
            if market and tid in (0,1):opts['alternatives'][2]['status']='VIABLE_CANDIDATE'
            d=self.write(s,d,a,'submit-alternatives',opts)
        return d

    def test_F1_stale_evolution_blocked_then_refreshed_history_preserved(self):
        a,d=self.h.context('FIX_F1')
        with Store(self.h.root/'fix_f1/gm_workbench.sqlite') as s:
            s.save_analysis(a);d=s.save_decision(d)
            d=self.write(s,d,a,'submit-blueprint',self.h.proposal(a),bpti_index=self.h.index)
            e=self.h.evo(a,d['artifacts']['BPTI_BLUEPRINT']['0'])
            d=self.write(s,d,a,'record-evolution',e)
            old=s.artifact_history('FIX_F1','BPTI_EVOLUTION','0',1)
            d=self.write(s,d,a,'submit-blueprint',self.h.proposal(a),bpti_index=self.h.index)
            d=self.review_all(s,d,a)
            d=self.write(s,d,a,'select',selection())
            u,arts=dp.validate(d,a);d=s.save_decision(u,d['revision'],arts)
            report=d['artifacts']['VALIDATION']['current']['payload']
            self.assertFalse(report['valid_for_finalization'])
            self.assertIn('BPTI_EVOLUTION_STALE',[i['code'] for i in report['issues']])
            with self.assertRaisesRegex(ValueError,'CURRENT_DETERMINISTIC'):dp.finalize(d,a)
            with self.assertRaisesRegex(ValueError,'EVOLUTION_STALE'):dp.strategy_candidate(d,a,ap.team(a,0),d['artifacts']['TEAM_REVIEW']['0'],1)
            e=self.h.evo(a,d['artifacts']['BPTI_BLUEPRINT']['0'])
            e['previous_ref']=dict(run_id='FIX_F1',artifact_id='0',revision=1)
            d=self.write(s,d,a,'record-evolution',e,previous_evolution=old)
            u,arts=dp.validate(d,a);d=s.save_decision(u,d['revision'],arts)
            self.assertTrue(d['artifacts']['VALIDATION']['current']['payload']['valid_for_finalization'])
            u,arts=dp.finalize(d,a);d=s.save_decision(u,d['revision'],arts)
            f=d['artifacts']['FINAL']['final']['payload']
            ev=next(x for x in f['bpti_artifacts'] if x['kind']=='BPTI_EVOLUTION')
            self.assertEqual(ev['payload']['bpti_blueprint_revision'],2)
            state=f['strategy_candidates'][0]['candidate_state']
            self.assertEqual(state['bpti_evolution']['payload']['bpti_blueprint_revision'],2)
            self.assertEqual(s.artifact_history('FIX_F1','BPTI_EVOLUTION','0',1),old)
            # An inherited strategy is history, not this run's current blueprint/evolution.
            base=deepcopy(d);base['strategy_bases']=[state]
            base['artifacts'].pop('BPTI_BLUEPRINT');base['artifacts'].pop('BPTI_EVOLUTION')
            cleared=dp.strategy_candidate(base,a,ap.team(a,0),base['artifacts']['TEAM_REVIEW']['0'],2)['candidate_state']
            self.assertNotIn('bpti_evolution',cleared);self.assertNotIn('bpti_reasoning',cleared)

    def test_F2_same_worldline_across_batches_seasons_but_not_instances(self):
        a,d=self.h.context('FIX_F2');d['context']['history_branch_context']='SYNTHETIC_WORLDLINE_A'
        blue=b4.prepare(d,a,self.h.index,self.h.proposal(a));row=dict(revision=1,payload=blue)
        e=self.h.evo(a,row);previous=b5.record(d,a,row,e)
        current=deepcopy(a);current['source_binding'].update(batch_id='SYNTHETIC_NEXT_BATCH',snapshot_id='SYNTHETIC_NEXT_SNAPSHOT',game_date='2022-10-20')
        current['context'].update(season='2022-2023',history_branch_context='SYNTHETIC_WORLDLINE_A')
        nd=dp.begin(current,'FIX_F2_NEXT');nb=b4.prepare(nd,current,self.h.index,self.h.proposal(current));nr=dict(revision=1,payload=nb)
        nxt=self.h.evo(current,nr);nxt['previous_ref']=dict(run_id='FIX_F2',artifact_id='0',revision=1)
        good=b5.record(nd,current,nr,nxt,previous)
        self.assertEqual(good['status'],'DRAFT_UNAPPROVED');self.assertEqual(good['previous_system'],previous['proposed_system'])
        for key in ('save_id','save_instance_id','generation_id'):
            wrong=deepcopy(previous);wrong['source_binding'][key]='OTHER_'+key
            held=b5.record(nd,current,nr,nxt,wrong)
            self.assertEqual(held['status'],'HOLD');self.assertIn(key,held['reason'])
        missing=deepcopy(previous);missing['source_binding'].pop('save_instance_id')
        self.assertIn('UNPROVEN',b5.record(nd,current,nr,nxt,missing)['reason'])
        branch=deepcopy(previous);branch['history_branch_context']='DIFFERENT_BRANCH'
        self.assertEqual(b5.record(nd,current,nr,nxt,branch)['status'],'HOLD')
        wrong=deepcopy(previous);wrong['team_id']=1
        with self.assertRaisesRegex(ValueError,'TEAM_CAREER'):b5.record(nd,current,nr,nxt,wrong)
        wrong=deepcopy(previous);wrong['source_binding']['career_id']='another_career'
        with self.assertRaisesRegex(ValueError,'TEAM_CAREER'):b5.record(nd,current,nr,nxt,wrong)

    def test_F3_native_hold_does_not_veto_evidenced_market(self):
        a,d=self.h.context('FIX_F3');p=self.h.proposal(a);p['native_actions']=[]
        no_action=b4.prepare(d,a,self.h.index,p)
        self.assertEqual(no_action['status'],'DRAFT_UNAPPROVED');self.assertEqual(no_action['native_action_status'],'HOLD')
        unknown=self.h.proposal(a);unknown['native_actions'][0]['changes'][0]['field_key']='coach.Tempo'
        unknown['blueprint']['native_binding_refs']=['B2-MOTION_READ_REACT-TEMPO']
        prepared=b4.prepare(d,a,self.h.index,unknown)
        self.assertEqual(prepared['supported_actions'],[]);self.assertEqual(prepared['native_action_status'],'HOLD')
        with Store(self.h.root/'fix_f3/gm_workbench.sqlite') as s:
            s.save_analysis(a);d=s.save_decision(d)
            d=self.write(s,d,a,'submit-blueprint',unknown,bpti_index=self.h.index)
            d=self.review_all(s,d,a,market=True)
            opts=d['artifacts']['ALTERNATIVES']['0']['payload']['alternatives']
            self.assertEqual(opts[2]['status'],'VIABLE_CANDIDATE')
            p=alternatives(0);p['bpti_blueprint_revision']=1
            p['alternatives'][1].update(status='VIABLE_CANDIDATE',action=unknown['native_actions'][0])
            p['alternatives'][2]['status']='VIABLE_CANDIDATE'
            d=self.write(s,d,a,'submit-alternatives',p)
            alts=d['artifacts']['ALTERNATIVES']['0']['payload']['alternatives']
            self.assertEqual(alts[1]['status'],'BLOCKED');self.assertEqual(alts[1]['bpti_native_status'],'HOLD_UNSUPPORTED_NATIVE_ACTION')
            self.assertEqual(alts[2]['status'],'VIABLE_CANDIDATE')
            move=offer(identity=ap.team(a,0)['player_supply']['players'][0]['identity'])
            d=self.write(s,d,a,'submit-offer',move)
            o=d['artifacts']['OFFER']['O']['payload']
            self.assertEqual(market_negotiation.bilateral(o,[],d['artifacts']['TEAM_REVIEW'],d['artifacts']['ALTERNATIVES']),'NEGOTIATING')
            self.assertFalse(d['execution_authorized'])
            # Removing internal gap evidence still invokes the original M3 market gate.
            r=review(a,0);r['bpti_blueprint_revision']=1;d=self.write(s,d,a,'submit-review',r)
            with self.assertRaisesRegex(ValueError,'INTERNAL_COMPARISON'):dp.apply(d,a,'submit-alternatives',p)

    def test_F4_selected_internal_requires_viable_candidate_research_retained(self):
        a,d=self.h.context('FIX_F4');p=self.h.proposal(a)
        for status in ('BLOCKED','RESEARCH','NOT_APPLICABLE','VIABLE_CANDIDATE'):
            opts=alternatives(0);opts['alternatives'][1].update(status=status,action=p['native_actions'][0])
            artifacts={'ALTERNATIVES':{'0':dict(revision=1,payload=opts)}}
            chosen=selection(exclude=[0]);chosen['selected_internal_action_versions']=[dict(team_id=0,revision=1,alternative_id='internal:0')]
            if status=='VIABLE_CANDIDATE':
                _,actions,issues,_=portfolio.resolve(chosen,artifacts,a)
                self.assertEqual(len(actions),1);self.assertEqual(issues,[])
            else:
                with self.assertRaisesRegex(ValueError,'NOT_VIABLE'):portfolio.resolve(chosen,artifacts,a)
                with self.assertRaisesRegex(ValueError,'NOT_VIABLE'):portfolio.inspect(chosen,artifacts,a,d)
        opts['alternatives'][1]['status']='RESEARCH'
        held=selection();held['research_action_ids']=['internal:0']
        _,actions,issues,research=portfolio.resolve(held,artifacts,a)
        self.assertEqual(actions,[]);self.assertEqual(issues,[])
        self.assertEqual(research[0]['alternative']['status'],'RESEARCH')
        opts['alternatives'][1].update(category='MARKET',status='VIABLE_CANDIDATE')
        with self.assertRaisesRegex(ValueError,'SPECIFIC_INTERNAL'):portfolio.resolve(chosen,artifacts,a)


if __name__=='__main__':unittest.main(verbosity=2)
