"""The eight checks explicitly authorized by the M3-T objective. Static/synthetic only."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gm_core import analysis_packet as ap,decision_protocol as dp
from gm_core.decision_handoff import native_intent,validate_tactical_action,coach_change_gate
from gm_core.decision_portfolio import inspect
from gm_core.coaching import raw_from_team
from gm_data_access.analysis_inputs import load_inputs,screen
from gm_data_access.decision_inputs import prepare_native_artifacts
from gm_data_access.query import QuerySession
from gm_data_access import AccessError
from gm_state_io.registry import Registry
from gm_state_io.codec import decode,encode_patch
from gm_state_io.plan import object_key,build_plan
from gm_state_io.team_book import identity as book_identity
from gm_state_io.common import digest
from gm_workbench.store import Store
from test_gm_data_access import fixture
from m3_fixtures import coaching_snapshot,review as old_review,alternatives as old_alternatives,selection

MASK=dict(potential_mask_version='potential_v1',source_role='GM_SANITIZED',potential_source_status='MASKED_NOT_GAME_OBSERVED')


def source_fixture(reg,sid='SYNTHETIC_S1',batch='SYNTHETIC_BATCH',changed_coach=False):
    source=dict(save_id='synthetic',save_instance_id='INSTANCE_TEST',generation_id='GENERATION_TEST',
        source_snapshot_id=sid,source_batch_id=batch,registry_version=reg.version,observed_at='2026-10-20T00:00:00+00:00',
        process_binding='SYNTHETIC_NO_PROCESS',objects=[],coverage={},observation_status='OBSERVED_SAME_SESSION',native_dictionary=reg.fields)
    books=[dict(index=t,enum_id=t,unique_id=100+t,name='T'+str(t),play_crc_slots=[1000+t]*68) for t in range(30)]
    source.update(source_context=dict(playbooks=books),loaded_playbooks=list(range(30)),loaded_play_crcs=[1000+t for t in range(30)],
        team_directory={str(t):dict(name='T'+str(t),abbreviation='T'+str(t),city='Synthetic') for t in range(30)})
    template=coaching_snapshot(dict(snapshot_id=sid,career_id='synthetic',batch_id=batch,game_date='2021-12-12',data_updated_at='T'))['teams'][0]
    base=raw_from_team(template)

    def patch_raw(raw,changes):
        raw=bytearray(raw)
        for block in encode_patch(bytes(raw),changes,reg,source['loaded_playbooks']):
            raw[block['offset']:block['offset']+block['size']]=bytes.fromhex(block['after'])
        return bytes(raw)

    def add(selector,identity,raw,keys):
        source['objects'].append(dict(object_key=object_key(selector),selector=selector,identity=identity,raw=raw.hex(),
            field_keys=keys,values={k:decode(raw,reg.field(k)) for k in keys},source_status='OBSERVED_SAME_SESSION'))

    for tid in range(30):
        raw=bytearray(patch_raw(base,{'coach.PlaybookID':1 if changed_coach and tid==0 else tid}))
        raw[0xEC:0xF4]=bytes([80,60,75,85,55,50,70,65])
        keys=[k for k,f in reg.fields.items() if f['target_kind']=='COACH_DEFAULT']
        add(dict(target_kind='COACH_DEFAULT',team_id=tid),dict(identity_tag='coach:'+str(tid),team_id=tid),bytes(raw),keys)
        for slot in range(68):
            if changed_coach and tid==0:
                continue  # No fresh own-A-book slot observations while A's coach still points to B.
            ident=digest(book_identity(books[tid]))
            selector=dict(target_kind='PLAYBOOK_SLOT',team_id=tid,owner_team_ids=[tid],playbook_identity=ident,slot_index=slot)
            add(selector,dict(playbook_identity=ident,owner_team_ids=[tid]),(1000+tid).to_bytes(4,'little'),['playbook.slot'])
        keys=[k for k,f in reg.fields.items() if f['target_kind']=='TEAM_TRAINING']
        add(dict(target_kind='TEAM_TRAINING',team_id=tid),dict(team_id=tid,franchise_slot=tid),bytes(88),keys)
        for n in range(3):
            pool=tid*3+n;tag='player:'+str(pool)
            raw=bytearray(0x4f0);raw[0x441]=1;raw[0x440]=90;raw[0x2f8:0x2fa]=(pool+1).to_bytes(2,'little')
            raw=patch_raw(raw,{'playtype.slot1':4,'playtype.slot2':7,'playtype.slot3':15,'playtype.slot4':0,
                'playtype.initiator':1,'tendency.TOUCHES_TENDENCY':80})
            ident=dict(pool_slot=pool,native_player_id=pool+1,identity_tag=tag)
            for kind in ('PLAYER_PLAYTYPE','PLAYER_TENDENCY','PLAYER_ROTATION_OVR_BIAS'):
                keys=[k for k,f in reg.fields.items() if f['target_kind']==kind]
                add(dict(target_kind=kind,team_id=tid,player_identity=tag),ident,raw,keys)
            keys=[k for k,f in reg.fields.items() if f['target_kind']=='PLAYER_TRAINING']
            add(dict(target_kind='PLAYER_TRAINING',team_id=tid,player_identity=tag),ident,bytes(796),keys)
    for n in range(2):
        keys=[k for k,f in reg.fields.items() if f['target_kind']=='PERSONAL_DEFENSE']
        add(dict(target_kind='PERSONAL_DEFENSE',team_id=0,opponent_team_id=1,opponent_player_identity='player:'+str(3+n),defender_identity='player:'+str(n)),
            dict(matchup_id=4+n,defender_id=1+n),bytes(8),keys)
    # This M3-only fixture observes no World settings; include only its observed field catalog.
    observed={key for obj in source['objects'] for key in obj['field_keys']}
    source['native_dictionary']={key:reg.fields[key] for key in observed}
    return source


def prepared(qroot,published,batch='SYNTHETIC_BATCH',run_id='TACTICAL_A'):
    data=load_inputs(qroot,published,'synthetic',batch,defense_matchups=['T0:T1'])
    a=ap.prepare(data,'2021-2022','CHECKPOINT',run_id=run_id)
    return data,a


def review(a,tid):
    r=old_review(a,tid)
    r.update(internal_tactical_diagnosis_refs=['tactical:'+str(tid)],rejected_internal_fixes=[],
        market_gap_after_internal_assessment=dict(status='UNKNOWN',reason='No supported gap claim; HOLD pending evidence',evidence_refs=['team:'+str(tid)]),
        evidence_quality=dict(native_fields='GAME_NATIVE_FIELD_VERIFIED',behavior='UNKNOWN'),play_type_coverage='UNKNOWN')
    for p in r['player_assessments']:
        p['role_plan']=dict(role='HOLD',minutes_target_band=None,reason='Preserve current role pending a specific alternative')
    return r


def action(a,kind,target_kind,field,value,tid=0,number=0):
    objects=[o for o in ap.team(a,tid)['tactical_context']['objects'].values() if o['target_kind']==target_kind]
    obj=objects[number]
    return dict(action_id='ACTION_'+kind+'_'+target_kind+'_'+str(number),team_id=tid,kind=kind,
        changes=[dict(action_id='CHANGE_'+kind+'_'+target_kind+'_'+str(number),object_key=obj['object_key'],field_key=field,target_value=value,reason='Synthetic explicit mechanism hypothesis')],
        reason='Synthetic comparative internal alternative',evidence_refs=[obj['evidence_ref']],
        expected_effect='Directional hypothesis only',uncertainty='Live and sim effects UNKNOWN',counterplay='Reassess if opponent adapts',
        why_better_than_hold='Explicit synthetic alternative; no improvement claimed')


def selected(actions):
    return dict(actions=actions,offers=[],issues=[],research=[])


class M3TObjectiveChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.root=Path(cls.tmp.name);cls.reg=Registry()
        cls.source=source_fixture(cls.reg)
        cls.qroot,cls.pub,_,_=fixture(cls.root,team_stats=True,team_count=30,native_source=cls.source,potential_mask=MASK)
        cls.data,cls.a=prepared(cls.qroot,cls.pub)
    @classmethod
    def tearDownClass(cls):
        for p in cls.root.rglob('*'):
            if p.is_file():p.chmod(0o600)
        cls.tmp.cleanup()
    def run_context(self,phase='REGULAR'):
        a=deepcopy(self.a);ap.seal(a)
        return a,dp.begin(a,'D_'+phase,season_phase=phase)
    def compile(self,d,a,actions):
        return prepare_native_artifacts(a,d,selected(actions),self.qroot,self.pub)

    def test_01_original_m3_interfaces_and_precise_rosters_survive_merge(self):
        self.assertEqual(len(self.a['teams']),30)
        self.assertEqual({p['identity'] for t in self.a['teams'] for p in t['player_supply']['players']},{p['identity'] for p in self.data['players']})
        self.assertTrue(all(callable(getattr(dp,name)) for name in ('begin','apply','validate','finalize')))
        a,d=self.run_context()
        with Store(self.root/'derived/gm_workbench.sqlite') as store:
            store.save_analysis(a);d=store.save_decision(d)
            updated,art=dp.apply(d,a,'submit-review',review(a,0));d=store.save_decision(updated,d['revision'],art)
            updated,art=dp.apply(d,a,'submit-alternatives',old_alternatives(0));d=store.save_decision(updated,d['revision'],art)
            self.assertIn('0',d['artifacts']['TEAM_REVIEW']);self.assertIn('0',d['artifacts']['ALTERNATIVES'])
            self.assertEqual(store.list_states('synthetic'),[])
        s=QuerySession(self.qroot,self.pub,'synthetic','SYNTHETIC_BATCH')
        try:
            self.assertTrue(s.available['team_stats']);self.assertTrue(s.available['rotation']);self.assertTrue(s.available['native_books'])
        finally:s.close()

    def test_02_dev14_queries_feed_real_m3_tactical_dtos(self):
        p=ap.team(self.a,0)['player_supply']['players'][0];tc=p['tactical_context']
        self.assertEqual(tc['play_types'],[4,7,15,0]);self.assertEqual(len(tc['named_tendencies']),48)
        self.assertEqual(tc['named_tendencies']['tendency.TOUCHES_TENDENCY'],80)
        self.assertEqual(tc['load']['minutes_per_game'],5)
        t=ap.team(self.a,0)['tactical_context']
        self.assertEqual(len(t['system_proficiencies']['values']),8)
        self.assertEqual(t['playbook']['play_type_coverage'],'UNKNOWN')
        self.assertEqual(t['playbook']['current_binding'],0)
        self.assertEqual(t['system_proficiencies']['optimal_system_claim'],'NOT_ESTABLISHED')
        self.assertEqual(tc['role_assignment'],'GM_RESEARCH_REQUIRED_NO_AUTOMATIC_TOUCH_THRESHOLD')
        self.assertTrue(all(r['binding']['generation_id']=='GENERATION_TEST' for r in self.a['source_access']))

    def test_03_potential_is_masked_and_never_a_scouting_score(self):
        p=ap.team(self.a,0)['player_supply']['players'][0]
        self.assertNotIn('potential',p['decoded_attributes']);self.assertNotIn('intangibles',p['decoded_attributes'])
        self.assertIsNone(p['potential_visibility']['value'])
        s=QuerySession(self.qroot,self.pub,'synthetic','SYNTHETIC_BATCH')
        q=dict(query_id='POT',source_domain='roster',role_question='Forbidden scoring input',filters=[dict(native_field='attributes.potential.value',operator='gte',value=1)],excluded_team_ids=[],order_by=[])
        try:
            with self.assertRaisesRegex(ValueError,'NOT_SCOUTING'):screen(s,q,{'potential','speed'},set())
            s.record['source_manifest'].pop('player_potential_mask')
            with self.assertRaises(AccessError) as denied:s.require_gm_sanitized()
            self.assertEqual(denied.exception.code,'UNMASKED_HISTORICAL_BATCH_EXCLUDED_FROM_GM')
        finally:s.close()
        old=deepcopy(self.a);old['source_binding'].pop('player_potential_visibility')
        with self.assertRaisesRegex(ValueError,'UNMASKED'):ap.summary(old)

    def test_04_coach_personal_player_training_and_rotation_intents(self):
        a,d=self.run_context()
        personal=list(self.reg.field('personal.PressureOnball')['layout']['enum'])
        value=next(int(v) for v in personal if int(v)!=0)
        acts=[action(a,'COACH_DEFAULT','COACH_DEFAULT','coach.POEOffense',2),
            action(a,'PERSONAL_DEFENSE','PERSONAL_DEFENSE','personal.PressureOnball',value),
            action(a,'PERSONAL_DEFENSE','PERSONAL_DEFENSE','personal.PressureOnball',value,number=1),
            action(a,'PLAYER_PLAY_TYPE','PLAYER_PLAYTYPE','playtype.slot1',15),
            action(a,'PLAYER_TENDENCY','PLAYER_TENDENCY','tendency.TOUCHES_TENDENCY',75),
            action(a,'TRAINING_PLAN','PLAYER_TRAINING','training.player.intensity',2),
            action(a,'TRAINING_PLAN','TEAM_TRAINING','training.team.rest_before_b2b',1),
            action(a,'LINEUP_ROLE','PLAYER_ROTATION_OVR_BIAS','rotation.intangibles',70)]
        acts[-1].update(role='SIXTH_MAN',minutes_target_band=[24,30])
        for act in acts:validate_tactical_action(d,a,act)
        result=self.compile(d,a,acts)
        self.assertEqual([r['status'] for r in result],['OFFLINE_PREPARED'],result[0].get('reason'))
        self.assertEqual(len(result[0]['intent']['changes']),8)
        self.assertEqual(result[0]['approval_tuple']['generation_id'],'GENERATION_TEST')
        self.assertFalse(result[0]['execution_authorized'])
        duplicate=deepcopy(acts[4]);duplicate['action_id']='conflicting';duplicate['changes'][0]['target_value']=30
        with self.assertRaisesRegex(ValueError,'NATIVE_FIELD_CONFLICT'):self.compile(d,a,acts+[duplicate])

    def test_05_ordinary_gm_cannot_change_overall_or_switch_books(self):
        a,d=self.run_context()
        bad=action(a,'COACH_DEFAULT','COACH_DEFAULT','coach.PlaybookID',1)
        with self.assertRaisesRegex(PermissionError,'BOOK_SWITCH'):validate_tactical_action(d,a,bad)
        bad=action(a,'PERSONAL_DEFENSE','PERSONAL_DEFENSE','overall.PressureOnball',1)
        with self.assertRaisesRegex(PermissionError,'OVERALL_DEFENSE'):validate_tactical_action(d,a,bad)
        bad['kind']='OVERALL_DEFENSE'
        with self.assertRaisesRegex(PermissionError,'OVERALL_DEFENSE'):validate_tactical_action(d,a,bad)

    def test_06_confirmed_coach_change_rebind_then_new_source_slots(self):
        root=self.root/'coach_case';root.mkdir()
        before=source_fixture(self.reg,'PRE_S','PRE_B',changed_coach=True)
        q,pub,_,_=fixture(root,team_stats=True,team_count=30,native_source=before,potential_mask=MASK,sid='PRE_S',batch='PRE_B')
        _,a=prepared(q,pub,'PRE_B','PRE_A');ap.seal(a)
        d=dp.begin(a,'COACH_D',season_phase='OFFSEASON')
        tc=ap.team(a,0)['tactical_context'];coach=tc['objects'][tc['coach_object_key']]
        event=dict(event_id='E1',kind='CONFIRMED_COACH_CHANGE',reference='SYNTHETIC_PLAYER_CONFIRMATION',team_id=0,current_coach_identity=coach['native_identity'])
        with Store(root/'derived/gm_workbench.sqlite') as store:
            store.save_analysis(a);d=store.save_decision(d)
            update,arts=dp.apply(d,a,'record-coach-event',event);d=store.save_decision(update,d['revision'],arts)
            self.assertEqual(coach_change_gate(d,0),'COACH_CHANGE_ONCE_PER_TEAM_SEASON')
            with self.assertRaisesRegex(ValueError,'ONCE_PER'):dp.apply(d,a,'record-coach-event',dict(event,event_id='E2'))
        self.assertEqual(coach_change_gate(dict(d,season_phase='REGULAR',coach_events=[]),0),'COACH_CHANGE_OFFSEASON_ONLY')
        rebind=dict(action_id='RESTORE_A',team_id=0,kind='TEAM_BOOK_REBIND',event_id='E1',reason='Confirmed B coach must use A team book',
            evidence_refs=['tactical:0'],expected_effect='Restore ownership',uncertainty='Tactical effect UNKNOWN',counterplay='Replan content after source',why_better_than_hold='Restore own named book')
        generated=prepare_native_artifacts(a,d,selected([rebind]),q,pub)[0]
        self.assertEqual(generated['status'],'OFFLINE_PREPARED');self.assertEqual(generated['intent']['operation'],'TEAM_BOOK_REBIND')
        self.assertEqual(generated['intent']['changes'][0]['target_value'],0)
        self.assertEqual(generated['follow_up'],'NEW_SOURCE_AND_SEPARATE_SLOT_PROPOSAL_AFTER_APPROVED_BINDING')
        self.assertFalse(any(o['target_kind']=='PLAYBOOK_SLOT' for o in tc['objects'].values()))
        fresh_root=self.root/'post_binding';fresh_root.mkdir()
        after=source_fixture(self.reg,'POST_S','POST_B')
        q2,p2,_,_=fixture(fresh_root,team_stats=True,team_count=30,native_source=after,potential_mask=MASK,sid='POST_S',batch='POST_B')
        _,a2=prepared(q2,p2,'POST_B','POST_A');ap.seal(a2);d2=dp.begin(a2,'POST_D')
        slot=action(a2,'TEAM_EXCLUSIVE_PLAYBOOK_CONTENT','PLAYBOOK_SLOT','playbook.slot',1001)
        output=prepare_native_artifacts(a2,d2,selected([slot]),q2,p2)[0]
        self.assertEqual(output['status'],'OFFLINE_PREPARED');self.assertEqual(output['source_binding']['batch_id'],'POST_B')
        self.assertEqual(len(output['intent']['changes']),1)
        self.assertEqual(before['source_context']['playbooks'][1],after['source_context']['playbooks'][1])

    def test_07_unknown_sources_and_internal_comparison_are_honest(self):
        a,d=self.run_context()
        p=ap.team(a,0)['player_supply']['players'][0]
        self.assertEqual(p['tactical_context']['training']['fatigue'],'NOT_OBSERVED')
        self.assertEqual(p['tactical_context']['training']['position_specific_templates'],'UNKNOWN')
        self.assertEqual(ap.team(a,0)['tactical_context']['effect_certainty'],dict(live_3d='UNKNOWN',calendar_sim='UNKNOWN'))
        r=review(a,0);r['play_type_coverage']='STATIC_VERIFIED'
        with self.assertRaisesRegex(ValueError,'CRC_ONLY'):dp.review(r,a)
        good=review(a,0);dp.review(good,a)
        d['artifacts']={'TEAM_REVIEW':{'0':dict(revision=1,payload=good)}}
        opts=old_alternatives(0);opts['alternatives'][2]['status']='VIABLE_CANDIDATE'
        with self.assertRaisesRegex(ValueError,'INTERNAL_COMPARISON'):dp.alternatives(opts,d,a)

    def test_08_proposals_are_not_game_approval_and_fields_stay_bounded(self):
        a,d=self.run_context()
        act=action(a,'LINEUP_ROLE','PLAYER_ROTATION_OVR_BIAS','rotation.intangibles',70)
        act.update(role='STARTER',minutes_target_band=[28,34])
        raw_before=[o['raw'] for o in self.source['objects']]
        output=self.compile(d,a,[act])[0]
        self.assertEqual(output['status'],'OFFLINE_PREPARED');self.assertEqual(output['approval_status'],'NOT_GRANTED')
        self.assertNotIn('approved',output['intent']);self.assertNotIn('raw',json.dumps(output))
        self.assertNotIn('address',json.dumps(output));self.assertFalse(output['execution_authorized'])
        self.assertEqual(raw_before,[o['raw'] for o in self.source['objects']])
        bad=deepcopy(act);bad['changes'][0]['field_key']='ability.potential'
        with self.assertRaisesRegex(PermissionError,'NOT_AUTHORIZED'):validate_tactical_action(d,a,bad)
        bad=deepcopy(act);bad['changes'][0]['target_value']=100
        self.assertEqual(self.compile(d,a,[bad])[0]['status'],'BLOCKED_SOURCE')
        forged=deepcopy(review(a,0));forged['approved']=True
        with self.assertRaisesRegex(ValueError,'AUTHORITY'):dp.apply(d,a,'submit-review',forged)


if __name__=='__main__':unittest.main()
