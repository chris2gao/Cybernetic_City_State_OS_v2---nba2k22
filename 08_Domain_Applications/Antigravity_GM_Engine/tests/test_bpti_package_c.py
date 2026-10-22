"""Exactly C-C1..C-C5: synthetic local engineering acceptance; no game access."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.append(str(ROOT/'scripts'))
from gm_core import analysis_packet as ap, decision_protocol as dp, bpti_decision as b4, bpti_evolution as b5
from gm_core.knowledge import Knowledge
from gm_data_access.decision_inputs import prepare_native_artifacts
from gm_state_io.registry import Registry
from gm_workbench.store import Store
from test_m3_t_integration import source_fixture, prepared, review, action, selected, fixture, MASK
from m3_fixtures import alternatives


class PackageCChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name)
        cls.source=source_fixture(Registry())
        cls.qroot,cls.pub,_,_=fixture(cls.root,team_stats=True,team_count=30,native_source=cls.source,potential_mask=MASK)
        _,cls.a=prepared(cls.qroot,cls.pub,run_id='BPTI_C_SYNTHETIC')
        for tid,abbr in enumerate(('GSW','CHI','MIA')):
            t=ap.team(cls.a,tid);t['team']=abbr
            for p in t['player_supply']['players']:
                # Explicitly synthetic CURRENT skills, never historical peak by name.
                p['decoded_attributes'].update({'3pt_shot':78 if tid==0 else 52,'midrange_shot':82 if tid==1 else 58,'block':84 if tid==2 else 40})
        ap.seal(cls.a)
        cls.index=Knowledge(ROOT/'web_gm/knowledge').bpti()
    @classmethod
    def tearDownClass(cls):
        for p in cls.root.rglob('*'):
            if p.is_file():p.chmod(0o600)
        cls.tmp.cleanup()
    def context(self,name='C'):
        a=deepcopy(self.a);return a,dp.begin(a,name,season_phase='REGULAR')
    def proposal(self,a,tid=0):
        system=('MOTION_READ_REACT','ISOLATION_MIDRANGE_CREATION','DEFENSE_FIRST_RIM_PROTECTION')[tid]
        role=('MOVEMENT_SHOOTER_CONNECTOR','MIDRANGE_CREATOR','RIM_ANCHOR')[tid]
        skill=('3pt_shot','midrange_shot','block')[tid]
        chain=(('Off-ball separation through movement and connection','Switch and top-lock','Backcut then secondary-side reset'),
               ('Creator earns a midrange advantage with spacing','Early help and traps','Pass to release then re-attack'),
               ('Rim anchor protects paint and initiates outlet','Pull anchor outward and force recovery','Contain first then rotate from weak side'))[tid]
        t=ap.team(a,tid);p=t['player_supply']['players'][0];ref=p['evidence_ref']
        view=self.index.system(system,as_of=a['source_binding']['game_date'])
        claims=view['card']['evidence_claim_ids'] if view['card'] else ['B1-E4-'+system]
        blue=dict(schema_version='BPTI_KNOWLEDGE_V1',object_type='SystemBlueprint',blueprint_id='SYNTHETIC_'+str(tid),
            evidence_claim_ids=claims,identity_ref='B3-TEAM-'+t['team'],primary_system=system,secondary_systems=[],
            source_binding=deepcopy(a['source_binding']),team_id=tid,coach_ref='native-object:'+t['tactical_context']['coach_object_key'],
            player_role_refs=[dict(player_ref=ref,roles=[role],agency=['STRUCTURED_READ','BAILOUT_RIGHT','RESET_RIGHT'])],
            first_advantage=chain[0],opponent_counter=chain[1],second_answer=chain[2],
            native_binding_refs=['B2-'+system+'-COACH'],internal_alternatives=['HOLD','INTERNAL','MARKET'],
            unknowns=['Actual live and simulation effects unknown'],status='DRAFT_UNAPPROVED')
        implications={cat:dict(means=cat+' evaluates '+role,cost=cat+' opportunity cost: preserve assets vs '+role,
            change_conditions=['New source or counterplay evidence']) for cat in ('HOLD','INTERNAL','MARKET')}
        return dict(team_id=tid,source_binding=deepcopy(a['source_binding']),blueprint=blue,
            why_this_basketball=chain[0]+' using current '+skill+'; historical identity is reference only',
            identity_application=dict(retained_values=['Patient organizational continuity'],role_fit=role+' from current '+skill,
                internal_priority='Try role and coach adjustments before acquisition',market_after_internal='Acquire only if evidenced gap remains',
                tradeoffs='Current salary and asset cost remain M1 evidence, no invented signing capacity'),
            role_evidence=[dict(player_ref=ref,skill_fields=[skill],evidence_refs=[ref],reason='Current synthetic visible skill supports '+role)],
            decision_context=dict(coach_fit='Current coach configuration needs scoped alignment',development_plan='Game-controlled growth; train current role',
                market_gap_reason='Unknown until internal comparison',identity_role_tradeoff='Retain culture; revise tactical role if needed'),
            alternative_implications=implications,native_actions=[action(a,'COACH_DEFAULT','COACH_DEFAULT','coach.RunPlayTendency',65,tid)])
    def write(self,store,d,a,cmd,p,**kw):
        u,arts=dp.apply(d,a,cmd,p,**kw);return store.save_decision(u,d['revision'],arts)
    def evo(self,a,row,level='ROLE_TWEAK'):
        return dict(team_id=0,source_binding=deepcopy(a['source_binding']),bpti_blueprint_revision=row['revision'],level=level,
            previous_ref=None,observed_changes=[dict(kind='VISIBLE_SKILL',evidence_refs=[ap.team(a,0)['player_supply']['players'][0]['evidence_ref']],
                observation='Current passing/shooting role changed in synthetic source',uncertainty='No real match performance evidence')],
            decision_reason='Adapt roles to visible current skills; no name-to-peak rule',retained_culture=['Continuity'],proposed_culture=['Continuity'],
            coach_alignment='Keep organization, revise coach emphasis',reconsider_conditions=['New source contradicts fit'])

    def test_C_C1_distinct_systems_reasons_and_roles(self):
        a,d=self.context();rows=[b4.prepare(d,a,self.index,self.proposal(a,t)) for t in range(3)]
        self.assertEqual([r['status'] for r in rows],['DRAFT_UNAPPROVED']*3)
        self.assertEqual(len({r['first_advantage'] for r in rows}),3)
        self.assertEqual(len({r['roles_agency'][0]['roles'][0] for r in rows}),3)
        self.assertIn('secondary-side',rows[0]['second_answer']);self.assertIn('midrange',rows[1]['first_advantage'])
        self.assertIn('Rim anchor',rows[2]['first_advantage'])
        self.assertTrue(all(r['actual_team_assessment']=='UNASSESSED' for r in rows))

    def test_C_C2_existing_m3_comparison_and_workbench(self):
        a,d=self.context('C2')
        with Store(self.root/'c2/gm_workbench.sqlite') as s:
            s.save_analysis(a);d=s.save_decision(d)
            d=self.write(s,d,a,'submit-blueprint',self.proposal(a),bpti_index=self.index)
            r=review(a,0);r['bpti_blueprint_revision']=1
            d=self.write(s,d,a,'submit-review',r)
            rr=d['artifacts']['TEAM_REVIEW']['0']['payload']
            self.assertTrue(all('BPTI:' in v['conclusion'] for v in rr['decision_dimensions'].values()))
            alts=alternatives(0);alts['bpti_blueprint_revision']=1
            alts['alternatives'][1]['action']=d['artifacts']['BPTI_BLUEPRINT']['0']['payload']['supported_actions'][0]
            d=self.write(s,d,a,'submit-alternatives',alts)
            options=d['artifacts']['ALTERNATIVES']['0']['payload']['alternatives']
            self.assertTrue(all('opportunity cost' in x['costs_and_opportunity_costs'] for x in options))
            self.assertIn('salary',options[1]['basketball_identity_tradeoff']['tradeoffs'])
            bad=deepcopy(alts);bad['alternatives'][2]['status']='VIABLE_CANDIDATE'
            with self.assertRaisesRegex(ValueError,'INTERNAL_COMPARISON'):dp.apply(d,a,'submit-alternatives',bad)
            d=self.write(s,d,a,'submit-blueprint',self.proposal(a),bpti_index=self.index)
            with self.assertRaisesRegex(ValueError,'STALE'):dp.apply(d,a,'submit-alternatives',alts)
            self.assertEqual(s.artifact_history('C2','BPTI_BLUEPRINT','0',1)['first_advantage'],rr['basketball_reasoning']['first_advantage'])
            self.assertEqual(s.list_states('synthetic'),[])

    def test_C_C3_visible_skills_cross_team_star_and_coach_evolution(self):
        a,d=self.context('C3')
        # Synthetic historical-name star on GSW: role still follows current skills, not former CHI peak.
        ap.team(a,0)['player_supply']['players'][0]['name']='Michael Jordan (SYNTHETIC OTHER TEAM)'
        p=self.proposal(a);b=b4.prepare(d,a,self.index,p)
        self.assertEqual(b['roles_agency'][0]['roles'],['MOVEMENT_SHOOTER_CONNECTOR'])
        bad=deepcopy(p);bad['role_evidence'][0]['skill_fields']=['name']
        self.assertEqual(b4.prepare(d,a,self.index,bad)['status'],'HOLD')
        with Store(self.root/'c3/gm_workbench.sqlite') as s:
            s.save_analysis(a);d=s.save_decision(d)
            d=self.write(s,d,a,'submit-blueprint',p,bpti_index=self.index)
            e=self.evo(a,d['artifacts']['BPTI_BLUEPRINT']['0'])
            d=self.write(s,d,a,'record-evolution',e)
            previous=s.artifact_history('C3','BPTI_EVOLUTION','0',1)
            e['previous_ref']=dict(run_id='C3',artifact_id='0',revision=1);e['level']='COACH_ALIGNMENT_CHANGE'
            e['observed_changes'].append(dict(kind='COACH',evidence_refs=[p['blueprint']['coach_ref']],observation='Synthetic current coach alignment changed',uncertainty='No staff market or game effect established'))
            d=self.write(s,d,a,'record-evolution',e,previous_evolution=previous)
            now=d['artifacts']['BPTI_EVOLUTION']['0']['payload']
            self.assertEqual(now['previous_culture'],now['proposed_culture'])
            self.assertEqual(now['previous_system'],previous['proposed_system'])
            self.assertEqual(now['previous_ref']['revision'],1)
            month=deepcopy(e);month['proposed_culture']=['Rewrite after one hot month'];month['level']='ORGANIZATIONAL_REIDENTIFICATION'
            with self.assertRaisesRegex(ValueError,'CULTURE_INERTIA'):dp.apply(d,a,'record-evolution',month,previous_evolution=previous)
            self.assertEqual(len(b5.LEVELS),6)

    def test_C_C4_unavailable_sources_and_unknowns_hold(self):
        a,d=self.context();p=self.proposal(a)
        bad=deepcopy(p);bad['source_binding']['batch_id']='OTHER'
        self.assertEqual(b4.prepare(d,a,self.index,bad)['status'],'HOLD')
        raw=deepcopy(a);raw['potential_mask']['source_role']='RAW_ARCHIVE'
        self.assertEqual(b4.prepare(d,raw,self.index,p)['status'],'HOLD')
        past=deepcopy(a);past['source_binding']['game_date']='1900-01-01';pastd=dp.begin(past,'PAST')
        old=self.proposal(a);old['source_binding']=past['source_binding'];old['blueprint']['source_binding']=past['source_binding']
        self.assertEqual(b4.prepare(pastd,past,self.index,old)['status'],'HOLD')
        unknown=deepcopy(p);unknown['native_actions'][0]['changes'][0]['field_key']='coach.Tempo'
        unknown['blueprint']['native_binding_refs']=['B2-MOTION_READ_REACT-TEMPO']
        held=b4.prepare(d,a,self.index,unknown)
        self.assertEqual(held['native_action_status'],'HOLD');self.assertEqual(held['native_support_and_unknowns']['effects'],'UNKNOWN_NOT_PREDICTED')
        self.assertNotIn('win_rate',held);self.assertNotIn('box_score_prediction',held)
        spec=importlib.util.spec_from_file_location('bpti_c_cli',ROOT/'scripts/gm_decision.py');cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
        with Store(self.root/'c4/gm_workbench.sqlite') as s:
            s.save_analysis(a);stored=s.save_decision(dp.begin(a,'MISSING_SOURCE'))
        inp=self.root/'bpti_input.json';inp.write_text(json.dumps(p),encoding='utf-8')
        args=cli.parser().parse_args(['submit-blueprint','--workbench',str(self.root/'c4/gm_workbench.sqlite'),'--run','MISSING_SOURCE','--expected-revision',str(stored['revision']),
            '--query-root',str(self.root/'absent'),'--published-root',str(self.pub),'--input',str(inp)])
        self.assertEqual(cli.run(args)['status'],'HOLD')

    def test_C_C5_unapproved_dev14_intent_and_existing_guards(self):
        a,d=self.context();p=self.proposal(a);b=b4.prepare(d,a,self.index,p)
        before=deepcopy(self.source)
        out=prepare_native_artifacts(a,d,selected(b['supported_actions']),self.qroot,self.pub)[0]
        self.assertEqual(out['status'],'OFFLINE_PREPARED');self.assertEqual(out['approval_status'],'NOT_GRANTED');self.assertFalse(out['execution_authorized'])
        self.assertEqual(self.source,before);self.assertNotIn('approved',out['intent'])
        for field in ('ability.potential','ability.overall','badge.test','tendency.UNKNOWN51','coach.PlaybookID','playbook.slot'):
            bad=deepcopy(p);bad['native_actions'][0]['changes'][0]['field_key']=field
            self.assertEqual(b4.prepare(d,a,self.index,bad)['native_action_status'],'HOLD',field)
        forged=deepcopy(p);forged['approved']=True
        with self.assertRaisesRegex(ValueError,'AUTHORITY'):dp.apply(d,a,'submit-blueprint',forged,bpti_index=self.index)
        with Store(self.root/'c5/gm_workbench.sqlite') as s:
            s.save_analysis(a);d=s.save_decision(d)
            with self.assertRaisesRegex(ValueError,'REVISION_CONFLICT'):s.save_decision(d,0)
        self.assertEqual(d['protocol_status'],'DRAFT_NOT_ENABLED');self.assertFalse(d['execution_authorized'])
        self.assertFalse(dp.progress(d)['all_teams_ready'])
        self.assertEqual(sum(len(x) for x in d['artifacts'].values()),0)


if __name__=='__main__':unittest.main(verbosity=2)
