"""DEV14 bounded synthetic acceptance. Never opens an NBA2K22 handle."""
import copy
import json
from pathlib import Path
import shutil
import sqlite3
import struct
import subprocess
import base64
import importlib.util
import sys
import tempfile
import unittest
from contextlib import closing
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import save_context
from gm_state_io.common import binding, digest, load
from gm_state_io.registry import Registry
from gm_state_io.plan import build_plan, stage, object_key, load_plan
from gm_state_io.workspace import Workspaces, lifecycle_lock
from gm_state_io.executor import Executor, ExternalApproval
from gm_state_io.capture_bridge import store, load_from_connection
from gm_state_io.reconcile import reconcile


class FakeSession:
    def __init__(self, state, read_only):
        self.state,self.read_only=state,read_only
        state['opens'].append(read_only)

    def verify_context(self,plan):
        if self.state.get('identity_changed'):
            raise ValueError('OBJECT_IDENTITY_CHANGED')
        if self.state['binding']!=plan['process_binding']:
            raise ValueError('STALE_PROCESS_BINDING')

    def resolve(self,obj):
        if self.state.get('wrong_team') is not None and self.state['wrong_team']==obj['selector'].get('team_id'):
            raise ValueError('PLAYER_IDENTITY_CHANGED')
        return self.state['addresses'][obj['object_key']]

    def read(self,at,size):
        return bytes(self.state['memory'][at:at+size])

    def write(self,at,raw):
        if self.read_only:raise AssertionError('RO_WRITE')
        self.state['writes']+=1
        if self.state.get('fail_write')==self.state['writes']:
            if self.state.get('partial'):
                self.state['memory'][at:at+len(raw)]=bytes([255])*len(raw)
            return False
        self.state['memory'][at:at+len(raw)]=raw
        return True

    def close(self):pass


class SupervisedSyntheticExecutor(Executor):
    """Drive the actual foreground review with synthetic operator input only."""
    def run(self, plan, approval, *, rollback=False, supervision=None):
        from gm_state_io.approval import review
        from gm_state_io.executor import require_approval
        require_approval(plan, approval)
        answers=[':'.join(binding(plan).values()),'EDITORS CLOSED','SYNTHETIC_PLAYER_APPROVAL',
                 'APPROVE '+('ROLLBACK' if rollback else 'APPLY')+' '+plan['digest']]
        if plan.get('operation') == 'TEAM_BOOK_REBIND':
            event=plan['event']
            answers.insert(3,'CONFIRM '+event['kind']+' '+event['reference'])
        with patch('sys.stdin.isatty',return_value=True), patch('sys.stdout.isatty',return_value=True), \
             patch('builtins.input',side_effect=answers), patch('builtins.print'):
            with review(plan,rollback=rollback) as (human,token):
                return super().run(plan,human,rollback=rollback,supervision=token)


class FullCaptureSession:
    """Complete 30-team synthetic native source, including noncontinuous ID 31."""
    def __init__(self, reg):
        from types import SimpleNamespace
        import config
        self.registry=reg
        self.mem=SimpleNamespace(read_only=True)
        n=reg.coach_profile['native']
        self.loc=SimpleNamespace(teams={t:{} for t in sorted(config.CORE_TEAM_IDS)},
                                 coaches={t:dict(address=10000+t*0x200) for t in config.CORE_TEAM_IDS},
                                 franchise=100,native_evidence={})
        self.loc.profile=reg.coach_profile
        self.loc.managers={t:100+n['franchise_teams_offset']+i*n['franchise_team_stride'] for i,t in enumerate(sorted(self.loc.teams))}

    def verify_context(self,source):pass
    def read(self,at,size):return bytes(size)
    def resolve(self,obj):return 0
    def players(self,tid):
        return [dict(identity=dict(native_player_id=tid*10+i+1,identity_tag='player_'+str(tid)+'_'+str(i)),raw=bytes(0x4f0)) for i in range(2)]

    def coaching(self):
        teams=[]
        for tid in self.loc.teams:
            gameplans=[]
            for opp in self.loc.teams:
                if tid==opp:continue
                gameplans.append(dict(opponent_team_id=opp,overall_defense=dict(
                    identity=dict(group=tid,opponent=opp),commit_flag_raw=0,values={k:0 for k in self.registry.coach_profile['defensive_fields']},
                    blocks=[dict(settings_offset=0x68,raw_block=bytes(8).hex(),identity=dict(matchup_id=opp*10+1,defender_id=tid*10+1))])))
            teams.append(dict(team_id=tid,coach_identity=dict(team_id=tid,identity_tag='coach_'+str(tid)),gameplans=gameplans,values=dict(PlaybookID=0)))
        book=dict(index=0,enum_id=0,unique_id=11,name='SYNTHETIC_BOOK',play_crc_slots=[0]*68)
        return dict(career_id='A',source_batch_id='2021-2022_M02',observed_at='2026-10-19',process_binding='a'*64,
                    context_identity={},native_evidence={},playbooks=[book],teams=teams)


class StateIOTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.database=self.root/'database'
        self.database.mkdir()
        shutil.copyfile(ROOT/'database/schema.sql',self.database/'schema.sql')
        self.patches=[patch.object(save_context,'DATABASE_DIR',str(self.database)),
                      patch.object(save_context,'PROJECT_DIR',str(self.root)),
                      patch.object(save_context,'TEMPLATE_DIR',str(self.database/'templates')),
                      patch.object(save_context,'TEMPLATE_DB',str(self.database/'templates/league_template_v2.sqlite'))]
        for p in self.patches:p.start()
        self.manager=Workspaces()
        self.a=self.manager.create('A')
        self.manager.activate('A')
        self.a=self.manager.write(dict(self.a,lifecycle_status='CAPTURED'))
        self.reg=Registry()
        self.source=self.make_source(self.a)
        self.state=dict(memory=bytearray(40000),addresses={},opens=[],writes=0,binding=self.source['process_binding'])
        for i,obj in enumerate(self.source['objects']):
            at=100+i*3000
            self.state['addresses'][obj['object_key']]=at
            self.state['memory'][at:at+len(bytes.fromhex(obj['raw']))]=bytes.fromhex(obj['raw'])

    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()

    def make_source(self,w):
        objects=[]
        def obj(selector,raw,keys,identity=None):
            from gm_state_io.codec import decode
            objects.append(dict(object_key=object_key(selector),selector=selector,identity=identity or selector,
                                raw=raw.hex(),field_keys=keys,source_status='OBSERVED_SAME_SESSION',
                                values={k:decode(raw,self.reg.field(k)) for k in keys}))
        coach=bytes(0x160)
        obj(dict(target_kind='COACH_DEFAULT',team_id=31),coach,['coach.POEOffense','coach.POEDefense','coach.BenchDepth'])
        for side in ('USER','CPU'):
            raw=bytearray(2020)
            struct.pack_into('<f',raw,4+24*8,0.5)
            struct.pack_into('<f',raw,4+24*8+0x3f0,0.5)
            obj(dict(target_kind='GLOBAL_GAMEPLAY',side=side),bytes(raw),['gameplay.inside_shot_success'])
        for identity in ('SAME_NAME_ONE','SAME_NAME_TWO'):
            obj(dict(target_kind='PLAYER_TENDENCY',team_id=31,player_identity=identity),bytes(0x4f0),['tendency.SHOT_TENDENCY'])
        return dict(**binding(w),source_batch_id='batch_M02',source_snapshot_id='2021-2022_M02',
                    registry_version=self.reg.version,process_binding='a'*64,source_context=None,loaded_playbooks=[0],
                    objects=objects,native_dictionary=self.reg.fields,observed_at='2026-10-19',coverage={})

    def proposal(self, specs=None):
        specs=specs or [(0,'coach.POEOffense',1),(0,'coach.POEDefense',13),(1,'gameplay.inside_shot_success',55),
                        (3,'tendency.SHOT_TENDENCY',80),(4,'tendency.SHOT_TENDENCY',40)]
        return dict(decision_id='DEV14_TEST',version=1,reason='synthetic acceptance',changes=[
            dict(action_id='a'+str(i),object_key=self.source['objects'][obj]['object_key'],field_key=key,target_value=value,reason='synthetic')
            for i,(obj,key,value) in enumerate(specs)])

    def approval(self,plan):
        return ExternalApproval(**binding(plan),source_batch_id=plan['source_batch_id'],decision_id=plan['decision_id'],
                                version=plan['version'],action_ids=tuple(a['action_id'] for a in plan['actions']),
                                digest=plan['digest'],player_approval_reference='SYNTHETIC_PLAYER_APPROVAL',
                                loaded_save_confirmation=':'.join(binding(plan).values()),editors_closed=True)

    def executor(self):
        return SupervisedSyntheticExecutor(self.reg,lambda ro:FakeSession(self.state,ro),self.root/'locks')

    def test_stage_sparse_shared_coach_bits_and_two_sides(self):
        before=Path(save_context.save_paths('A')['db_path']).read_bytes()
        p=stage(self.proposal(),self.source,self.reg)
        self.assertEqual(p['native_blocks_planned'],5) # one shared coach, mirrored slider, two players
        self.assertEqual(stage(self.proposal(),self.source,self.reg)['digest'],p['digest'])
        coach=[b for b in p['blocks'] if b['selector']['target_kind']=='COACH_DEFAULT'][0]
        self.assertEqual(coach['mask'],(31<<15)|31)
        self.assertEqual(Path(save_context.save_paths('A')['db_path']).read_bytes(),before)
        self.assertFalse(self.state['opens'])
        self.assertEqual(p['actions'][2]['selector']['side'],'USER')

    def test_approval_before_any_handle_and_model_claims_refused(self):
        p=stage(self.proposal(),self.source,self.reg)
        with self.assertRaises(PermissionError):self.executor().run(p,None)
        self.assertFalse(self.state['opens'])
        bad=self.proposal();bad['approved']=True
        with self.assertRaises(ValueError):stage(bad,self.source,self.reg)
        with self.assertRaises(PermissionError):stage(self.proposal([(3,'tendency.RAW_0x467',50)]),self.source,self.reg)

    def test_apply_readback_idempotency_drift_and_rollback(self):
        p=stage(self.proposal(),self.source,self.reg)
        original=bytes(self.state['memory'])
        result=self.executor().run(p,self.approval(p))
        self.assertEqual(result['status'],'MEMORY_VERIFIED')
        self.assertFalse(result['persisted_in_save'])
        count=self.state['writes']
        self.assertEqual(self.executor().run(p,self.approval(p))['status'],'NO_WRITE_NEEDED')
        self.assertEqual(self.state['writes'],count)
        result=self.executor().run(p,self.approval(p),rollback=True)
        self.assertEqual(result['status'],'ROLLED_BACK_VERIFIED_IN_MEMORY')
        self.assertEqual(bytes(self.state['memory']),original)

    def test_stale_block_and_moved_player_no_write_handle(self):
        p=stage(self.proposal(),self.source,self.reg)
        b=p['blocks'][0];at=self.state['addresses'][b['object_key']]+b['offset']
        self.state['memory'][at]=255
        with self.assertRaisesRegex(ValueError,'STALE_SOURCE'):self.executor().run(p,self.approval(p))
        self.assertNotIn(False,self.state['opens'])
        self.state['wrong_team']=31
        with self.assertRaisesRegex(ValueError,'IDENTITY_CHANGED'):self.executor().preflight(p)

    def test_mid_write_failure_conditional_restore(self):
        p=stage(self.proposal(),self.source,self.reg)
        before=bytes(self.state['memory'])
        self.state['fail_write']=2
        with self.assertRaisesRegex(RuntimeError,'FAILED_ROLLED_BACK'):self.executor().run(p,self.approval(p))
        self.assertEqual(bytes(self.state['memory']),before)
        self.assertFalse(list((self.root/'locks').glob('*.lock')))

    def test_partial_write_retains_process_lock_and_blocks_switch(self):
        self.manager.create('B')
        p=stage(self.proposal(),self.source,self.reg)
        self.state.update(fail_write=2,partial=True)
        with self.assertRaisesRegex(RuntimeError,'PARTIAL_UNRECOVERED'):self.executor().run(p,self.approval(p))
        self.assertTrue(list((self.root/'locks').glob('*.lock')))
        with self.assertRaisesRegex(RuntimeError,'UNRESOLVED'):self.manager.activate('B')

    def test_two_saves_same_snapshot_separate_approval_and_facts(self):
        p=stage(self.proposal(),self.source,self.reg)
        self.executor().run(p,self.approval(p))
        self.manager.create('B')
        for career,value in [('A',1),('B',2)]:
            with closing(sqlite3.connect(save_context.save_paths(career)['db_path'])) as c, c:
                c.execute('CREATE TABLE test_identity(snapshot_id TEXT PRIMARY KEY,player_id INTEGER,value INTEGER)')
                c.execute('INSERT INTO test_identity VALUES (?,?,?)',('2021-2022_M02',7,value))
            with closing(sqlite3.connect(save_context.save_paths(career)['player_pool_db_path'])) as c,c:
                c.execute('CREATE TABLE test_player_pool(player_id INTEGER PRIMARY KEY,value INTEGER)')
                c.execute('INSERT INTO test_player_pool VALUES (?,?)',(7,value))
            with closing(sqlite3.connect(save_context.save_paths(career)['control_db_path'])) as c:
                self.assertEqual(c.execute('SELECT count(*) FROM approval_records').fetchone()[0],1 if career=='A' else 0)
        self.manager.activate('B')
        with self.assertRaisesRegex(ValueError,'ACTIVE'):self.executor().run(p,self.approval(p))
        with self.assertRaisesRegex(ValueError,'NOT_IN_ACTIVE'):load_plan(p['change_set_id'],self.reg,'B')
        for career,value in [('A',1),('B',2)]:
            with closing(sqlite3.connect(save_context.save_paths(career)['db_path'])) as c:
                self.assertEqual(c.execute('SELECT value FROM test_identity').fetchone()[0],value)
            with closing(sqlite3.connect(save_context.save_paths(career)['player_pool_db_path'])) as c:
                self.assertEqual(c.execute('SELECT value FROM test_player_pool WHERE player_id=7').fetchone()[0],value)

    def test_four_limit_retire_and_reset_confirmation_archive(self):
        for career in ('B','C','D'):self.manager.create(career)
        with self.assertRaisesRegex(ValueError,'FOUR_SAVE_LIMIT'):self.manager.create('E')
        self.manager.retire('D',self.manager.read('D')['manifest_digest'])
        self.manager.create('E')
        p=stage(self.proposal(),self.source,self.reg)
        old=self.manager.read('A')
        with self.assertRaises(PermissionError):self.manager.reset('A',old['generation_id'],None)
        plan=self.manager.reset_plan('A')
        fresh=self.manager.reset('A',old['generation_id'],old['manifest_digest'])
        self.assertNotEqual(fresh['generation_id'],old['generation_id'])
        self.assertEqual(fresh['lifecycle_status'],'NEW_UNCAPTURED')
        self.assertTrue(list(Path(plan['archive']).glob('*/gm_control.sqlite')))
        self.assertEqual(self.manager.active()['generation_id'],fresh['generation_id'])
        with self.assertRaises(ValueError):self.executor().run(p,self.approval(p))
        with closing(sqlite3.connect(save_context.save_paths('A')['control_db_path'])) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM approval_records').fetchone()[0],0)

    def test_reset_injected_failure_preserves_complete_generation(self):
        self.manager.create('B')
        old=self.manager.read('A')
        paths=save_context.save_paths('A')
        hashes={k:Path(paths[k]).read_bytes() for k in ('db_path','player_pool_db_path','control_db_path')}
        for point in ('archive_verified','generation_prepared','manifest_committed','active_committed'):
            def fail(at):
                if at==point:raise RuntimeError('INJECTED_'+point)
            with self.assertRaisesRegex(RuntimeError,'INJECTED'):self.manager.reset('A',old['generation_id'],old['manifest_digest'],fault=fail)
            self.assertEqual(self.manager.active()['generation_id'],old['generation_id'])
            for key,value in hashes.items():self.assertEqual(Path(save_context.save_paths('A')[key]).read_bytes(),value)
        self.assertEqual(self.manager.read('B')['lifecycle_status'],'NEW_UNCAPTURED')

    def test_published_reset_blocked_and_no_shared_or_no_active(self):
        p=self.root/'published/saves/A';p.mkdir(parents=True);(p/'latest.json').write_text('{}')
        w=self.manager.read('A')
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED_GENERATION'):self.manager.reset('A',w['generation_id'],w['manifest_digest'])
        with self.assertRaises(ValueError):self.manager.create('legacy-shared')
        self.manager.deactivate()
        with self.assertRaisesRegex(ValueError,'NO_ACTIVE_SAVE'):stage(self.proposal(),self.source,self.reg)

    def test_capture_projection_unknown_and_reconcile_drift_report_only(self):
        path=save_context.save_paths('A')['db_path']
        with closing(sqlite3.connect(path)) as c, c:
            summary=store(c,self.source)
            self.assertGreater(summary['fields'],0)
            result=load_from_connection(c,self.source['source_snapshot_id'])
        self.assertEqual(result['objects'],sorted(self.source['objects'],key=lambda o:o['object_key']))
        p=stage(self.proposal(),self.source,self.reg)
        self.executor().run(p,self.approval(p))
        newer=copy.deepcopy(self.source)
        newer.update(source_batch_id='batch_M03',source_snapshot_id='2021-2022_M03')
        writes=self.state['writes']
        report=reconcile(newer,self.reg)
        self.assertTrue(all(r['status']=='DRIFT_DETECTED' for r in report['rows']))
        self.assertEqual(self.state['writes'],writes)
        for obj in newer['objects']:
            at=self.state['addresses'][obj['object_key']]
            obj['raw']=self.state['memory'][at:at+len(bytes.fromhex(obj['raw']))].hex()
        matched=reconcile(newer,self.reg)
        self.assertTrue(all(r['status']=='MATCHED' for r in matched['rows']))
        self.assertEqual(self.state['writes'],writes)

    def test_complete_synthetic_capture_and_bounded_m0_domains(self):
        from gm_state_io.capture_bridge import capture
        from gm_data_access.query import QuerySession
        full=FullCaptureSession(self.reg)
        source=capture(full.mem,full.coaching(),self.reg,session=full)
        self.assertEqual(len([o for o in source['objects'] if o['selector']['target_kind']=='COACH_DEFAULT']),30)
        self.assertEqual(len([o for o in source['objects'] if o['selector']['target_kind']=='OVERALL_DEFENSE']),870)
        self.assertEqual(len([o for o in source['objects'] if o['selector']['target_kind']=='PLAYER_TENDENCY']),60)
        with closing(sqlite3.connect(save_context.save_paths('A')['db_path'])) as c,c:
            summary=store(c,source)
            c.commit()
            self.assertGreater(summary['fields'],20000)
            self.assertEqual(c.execute("SELECT count(*) FROM observed_setting_values WHERE field_key LIKE 'tendency.%' AND team_id=31").fetchone()[0],198)
            # Exercise real M0 view construction and query sandbox over only an
            # isolated DB, without rewriting an existing immutable M0 snapshot.
            q=QuerySession.__new__(QuerySession)
            q.batch='batch_M02'
            q.binding=dict(snapshot_id='2021-2022_M02',batch_id='batch_M02')
            q.directory=self.root
            (self.root/'ingest_manifest.json').write_text('{}')
            q.c=sqlite3.connect(':memory:')
            q.c.row_factory=sqlite3.Row
            q.c.execute('ATTACH DATABASE ? AS facts',(save_context.save_paths('A')['db_path'],))
            q.c.execute("ATTACH DATABASE ':memory:' AS pooldb")
            q._views()
            from gm_data_access.query import DEFAULTS
            q.columns={v:tuple(r[1] for r in q.c.execute('PRAGMA table_info(q_'+v+')')) for v in DEFAULTS}
            q._raw_tables={r[0].lower() for db in ('facts','pooldb','temp') for r in q.c.execute('SELECT name FROM '+db+".sqlite_master WHERE type='table'")}
            q.available={v:q.c.execute('SELECT 1 FROM q_'+v+' LIMIT 1').fetchone() is not None for v in DEFAULTS}
            q.c.execute('PRAGMA query_only=ON')
            q.c.set_authorizer(q._authorize)
            try:
                result=q.query('tendency',filters={'team_id':31},limit=20)
                self.assertEqual(result['row_count'],20)
                self.assertTrue(result['next_cursor'])
                self.assertEqual(q.query('gameplay',filters={'side':'CPU'})['row_count'],4)
                self.assertEqual(q.query('rotation',filters={'team_id':31})['row_count'],2)
                native=q.query('native_objects',filters={'team_id':31},limit=20)
                self.assertEqual(native['row_count'],20)
                self.assertIsInstance(native['rows'][0]['selector'],dict)
                self.assertNotIn('raw',native['rows'][0])
                self.assertEqual(q.query('native_books')['rows'][0]['enum_id'],0)
            finally:q.close()

    def test_overall_bulk_and_personal_conflict_noop_and_shared_playbook(self):
        full=FullCaptureSession(self.reg)
        from gm_state_io.capture_bridge import capture
        source=capture(full.mem,full.coaching(),self.reg,session=full)
        overall=next(o for o in source['objects'] if o['selector']['target_kind']=='OVERALL_DEFENSE')
        prop=dict(decision_id='DEF',version=1,reason='synthetic',changes=[dict(action_id='def',object_key=overall['object_key'],
                    field_key='overall.PressureOnball',target_value=1,reason='synthetic')])
        with self.assertRaisesRegex(PermissionError,'OVERALL_DEFENSE_GM_DISABLED_USE_PERSONAL'):
            build_plan(prop,source,self.reg,self.a)
        personal=next(o for o in source['objects'] if o['selector']['target_kind']=='PERSONAL_DEFENSE' and o['selector']['team_id']==overall['selector']['team_id'] and o['selector']['opponent_team_id']==overall['selector']['opponent_team_id'])
        prop['changes']=[dict(action_id='personal',object_key=personal['object_key'],field_key='personal.PressureOffball',target_value=1,reason='synthetic')]
        p=build_plan(prop,source,self.reg,self.a)
        self.assertEqual(len(p['blocks']),2)
        self.assertEqual(p['blocks'][-1]['selector']['target_kind'],'GAMEPLAN_COMMIT')
        self.assertTrue(all(b['selector']['target_kind']!='OVERALL_DEFENSE' for b in p['blocks']))
        prop['changes'][0]['target_value']=0
        self.assertEqual(build_plan(prop,source,self.reg,self.a)['blocks'],[])

    def test_native_training_packed_codec_and_approval_generation(self):
        from gm_state_io.codec import encode_patch,decode
        raw=bytes([0xff])*88
        blocks=encode_patch(raw,{'training.team.away_intensity':3,'training.team.rest_before_b2b':0},self.reg)
        self.assertEqual(len(blocks),1)
        self.assertEqual(blocks[0]['mask'],23)
        updated=bytearray(raw);b=blocks[0];updated[b['offset']:b['offset']+b['size']]=bytes.fromhex(b['after'])
        self.assertEqual(decode(updated,self.reg.field('training.team.away_intensity')),3)
        self.assertEqual(updated[0x54]&0xe8,raw[0x54]&0xe8)
        p=stage(self.proposal(),self.source,self.reg)
        from dataclasses import replace
        with self.assertRaises(PermissionError):self.executor().run(p,replace(self.approval(p),generation_id='OTHER'))
        self.assertEqual(self.state['opens'],[])

    def test_reset_interruption_recovery_and_capture_binding_guard(self):
        from gm_state_io.common import atomic_json
        from gm_state_io.lifecycle import capture_lease,verify_lease
        old=self.manager.read('A')
        with self.assertRaises(PermissionError):
            with capture_lease('A','A_ONLY_IS_NOT_A_GAME_IDENTITY'):pass
        with capture_lease('A',':'.join(binding(old).values())):
            self.assertEqual(verify_lease('A')['generation_id'],old['generation_id'])
        new=self.manager.reset('A',old['generation_id'],old['manifest_digest'])
        journal=self.manager.path('A').parent/'reset_activation.json'
        record=load(journal)
        atomic_json(journal,dict(record,status='PREPARED'))
        atomic_json(self.database/'active_save.json',dict(**binding(old),activation_status='ACTIVE'))
        with self.assertRaisesRegex(ValueError,'RESET_INTERRUPTED_BLOCKED'):self.manager.active()
        self.assertEqual(self.manager.recover('A',old['manifest_digest'])['status'],'RESTORED_OLD')
        self.assertEqual(self.manager.active()['generation_id'],old['generation_id'])

    def test_thousands_of_sparse_changes_one_approved_transaction(self):
        from gm_state_io.codec import decode
        keys=[k for k,v in self.reg.fields.items() if v['domain']=='tendency' and v['gm_enabled']]
        source=copy.deepcopy(self.source)
        source['objects']=[]
        changes=[]
        self.state['memory']=bytearray(160000)
        self.state['addresses']={}
        for i in range(50):
            selector=dict(target_kind='PLAYER_TENDENCY',team_id=31,player_identity='bulk_'+str(i))
            key=object_key(selector)
            source['objects'].append(dict(object_key=key,selector=selector,identity=selector,raw=bytes(0x4f0).hex(),
                                          field_keys=keys,source_status='OBSERVED_SAME_SESSION',values={k:0 for k in keys}))
            self.state['addresses'][key]=100+i*3000
            for n,name in enumerate(keys):
                changes.append(dict(action_id=f'p{i}_{n}',object_key=key,field_key=name,target_value=50,reason='synthetic bulk'))
        p=stage(dict(decision_id='BULK',version=1,reason='synthetic bulk',changes=changes),source,self.reg)
        self.assertEqual(p['actions_requested'],2400)
        self.assertEqual(self.executor().run(p,self.approval(p))['blocks_written'],2400)
        self.assertEqual(self.state['opens'],[True,False])
        self.assertEqual(self.state['writes'],2400)

    def test_lifecycle_lock_excludes_another_process(self):
        helper=self.root/'lock_probe.py'
        helper.write_text(
            'import sys\n'
            f'sys.path.insert(0,{str(ROOT/"src")!r})\n'
            'import save_context\n'
            'save_context.DATABASE_DIR=sys.argv[1]\n'
            'from gm_state_io.workspace import lifecycle_lock\n'
            'try:\n'
            '    with lifecycle_lock():\n'
            '        print("UNEXPECTED_ACQUIRED")\n'
            'except RuntimeError as exc:\n'
            '    print(str(exc))\n',encoding='utf-8')
        with lifecycle_lock():
            result=subprocess.run([sys.executable,'-B',str(helper),str(self.database)],capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'STATE_IO_LIFECYCLE_BUSY')

    def test_ro_to_rw_race_refuses_without_retaining_false_partial_state(self):
        self.manager.create('B')
        p=stage(self.proposal(),self.source,self.reg)
        def factory(ro):
            if not ro:
                b=p['blocks'][0]
                self.state['memory'][self.state['addresses'][b['object_key']]+b['offset']]=255
            return FakeSession(self.state,ro)
        executor=SupervisedSyntheticExecutor(self.reg,factory,self.root/'locks')
        with self.assertRaisesRegex(ValueError,'STALE_SOURCE'):executor.run(p,self.approval(p))
        self.assertEqual(self.state['writes'],0)
        self.assertFalse(list((self.root/'locks').glob('*.lock')))
        self.manager.activate('B')

    def test_cli_capture_transport_delegates_only_existing_full_pipeline(self):
        from contextlib import nullcontext
        from types import SimpleNamespace
        spec=importlib.util.spec_from_file_location('dev14_test_cli',ROOT/'scripts/gm_state_io.py')
        cli=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        args=['-GameDateUnknown','-Season','2022','-Month','2','-Name','CHECKPOINT','-Publish']
        encoded=base64.b64encode(json.dumps(args).encode()).decode()
        parsed=cli.parser().parse_args(['capture','--career','A','--approve-capture','--approve-publish',
                                       '--loaded-save-confirmation','synthetic-confirmation','--capture-args-base64',encoded])
        with patch('gm_state_io.lifecycle.capture_lease',return_value=nullcontext()),patch.object(cli.subprocess,'run',return_value=SimpleNamespace(returncode=0)) as dispatch:
            self.assertEqual(cli.run(parsed)['status'],'FULL_PIPELINE_COMPLETED')
            call=dispatch.call_args.args[0]
            self.assertEqual(call[-len(args):],args)
            self.assertIn(str(ROOT/'scripts/run_data_update.ps1'),call)
            self.assertNotIn('shell',dispatch.call_args.kwargs)
        parsed.approve_publish=False
        with self.assertRaises(PermissionError):cli.run(parsed)


if __name__=='__main__':unittest.main()
