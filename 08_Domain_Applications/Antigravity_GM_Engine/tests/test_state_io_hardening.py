"""DEV14-H synthetic file swaps and foreground approval; no game process."""
from contextlib import closing
import copy
import importlib.util
import os
from pathlib import Path
import shutil
import sqlite3
from unittest.mock import patch
from test_state_io import StateIOTests, FakeSession, ROOT
import save_context
from data_sync_metadata import stamp_database
from gm_state_io.approval import review
from gm_state_io.capture_files import backup, install, put_metadata, source_stamp, require_complete
from gm_state_io.common import binding
from gm_state_io.executor import Executor
from gm_state_io.lifecycle import capture_lease
from gm_state_io.plan import stage


class HardeningTests(StateIOTests):
    def test_rebind_only_own_named_book_and_fresh_slots_in_separate_approval(self):
        from gm_state_io.codec import decode
        from gm_state_io.plan import build_plan, object_key
        own=dict(index=1,enum_id=17,unique_id=11,name='Team A',play_crc_slots=[101]*68)
        other=dict(index=0,enum_id=0,unique_id=22,name='Team B',play_crc_slots=[202]*68)
        self.source['team_directory']={'31':dict(name='Team A',city='City',abbreviation='TMA')}
        self.source['source_context']=dict(playbooks=[own,other])
        self.source['loaded_playbooks']=[0,17]
        self.source['loaded_play_crcs']=[101,202]
        coach=self.source['objects'][0]
        coach['field_keys'].append('coach.PlaybookID')
        coach['values']['coach.PlaybookID']=decode(bytes.fromhex(coach['raw']),self.reg.field('coach.PlaybookID'))
        proposal=self.proposal([(0,'coach.PlaybookID',17)])
        with self.assertRaisesRegex(PermissionError,'ORDINARY_GM_BOOK_SWITCH_DISABLED'):stage(proposal,self.source,self.reg)
        proposal.update(operation='TEAM_BOOK_REBIND',event=dict(kind='CONFIRMED_COACH_CHANGE',reference='player-event-1',
            team_id=31,current_coach_identity=coach['identity']))
        wrong=copy.deepcopy(proposal);wrong['changes'][0]['target_value']=0
        with self.assertRaisesRegex(PermissionError,'MUST_TARGET_OWN_TEAM'):stage(wrong,self.source,self.reg)
        extra=copy.deepcopy(proposal);extra['changes'].append(dict(action_id='extra',object_key=coach['object_key'],
            field_key='coach.POEOffense',target_value=1,reason='must be separate'))
        with self.assertRaisesRegex(PermissionError,'SEPARATE_SINGLE_BINDING'):stage(extra,self.source,self.reg)
        plan=stage(proposal,self.source,self.reg)
        self.assertEqual(plan['objects'][0]['team_book_rebind'],{k:own[k] for k in ('index','enum_id','unique_id','name')})
        self.executor().run(plan,self.approval(plan))
        # A book content change requires a source after binding, not the B-book
        # slot captured before the binding operation. Targets use native identity.
        from gm_state_io.adapters import book_identity
        selector=dict(target_kind='PLAYBOOK_SLOT',team_id=31,owner_team_ids=[31],playbook_identity=book_identity(other),slot_index=0)
        slot=dict(selector=selector,object_key=object_key(selector),identity=selector,raw=(202).to_bytes(4,'little').hex(),
                  field_keys=['playbook.slot'],source_status='OBSERVED_SAME_SESSION',values={'playbook.slot':202})
        self.source['objects'].append(slot)
        slot_proposal=self.proposal([(5,'playbook.slot',101)])
        with self.assertRaisesRegex(PermissionError,'ONLY_OWN_TEAM_NAMED_BOOK'):build_plan(slot_proposal,self.source,self.reg,self.a)
        # An already correctly bound same-team source accepts sparse CRC edits.
        selector['playbook_identity']=book_identity(own)
        slot['object_key']=object_key(selector)
        slot['raw']=(101).to_bytes(4,'little').hex();slot['values']['playbook.slot']=101
        plan=build_plan(self.proposal([(5,'playbook.slot',202)]),self.source,self.reg,self.a)
        self.assertEqual(len(plan['blocks']),1)
        ambiguous=copy.deepcopy(self.source)
        ambiguous['source_context']['playbooks'].append(dict(own,index=2,enum_id=18))
        with self.assertRaisesRegex(ValueError,'MISSING_OR_AMBIGUOUS'):
            build_plan(self.proposal([(5,'playbook.slot',202)]),ambiguous,self.reg,self.a)

    def test_intangibles_sparse_write_preserves_potential_and_other_player_bytes(self):
        from gm_state_io.codec import decode
        from gm_state_io.plan import object_key
        selector=dict(target_kind='PLAYER_ROTATION_OVR_BIAS',team_id=31,player_identity='SAME_NAME_ONE')
        raw=bytearray((i % 256 for i in range(0x4f0)))
        raw[0x440]=90
        field=self.reg.field('rotation.intangibles')
        obj=dict(object_key=object_key(selector),selector=selector,identity=selector,raw=raw.hex(),
                 field_keys=['rotation.intangibles'],source_status='OBSERVED_SAME_SESSION',
                 values={'rotation.intangibles':decode(raw,field)})
        self.source['objects'].append(obj)
        self.state['addresses'][obj['object_key']]=20000
        self.state['memory'][20000:20000+len(raw)]=raw
        for bad in (24,100,True,25.0):
            with self.assertRaises(ValueError):stage(self.proposal([(5,'rotation.intangibles',bad)]),self.source,self.reg)
        plan=stage(self.proposal([(5,'rotation.intangibles',99)]),self.source,self.reg)
        self.assertEqual([(b['offset'],b['size'],b['after']) for b in plan['blocks']],[(0x440,1,'de')])
        self.executor().run(plan,self.approval(plan))
        raw[0x440]=222
        self.assertEqual(self.state['memory'][20000:20000+len(raw)],raw)
        self.executor().run(plan,self.approval(plan),rollback=True)
        self.assertEqual(self.state['memory'][20000+0x440],90)
        self.assertEqual(self.state['memory'][20000+0x441],raw[0x441])

    def test_foreign_pool_rejects_stage_activate_and_capture(self):
        self.manager.create('B')
        a,b=(save_context.save_paths(s) for s in ('A','B'))
        for paths,value in ((a,1),(b,2)):
            for key in ('db_path','player_pool_db_path'):
                with closing(sqlite3.connect(paths[key])) as c,c:
                    stamp_database(c,'M02',paths['save_id'],'same_timestamp')
                    c.execute('CREATE TABLE same_player_id(player_id INTEGER,value INTEGER)')
                    c.execute('INSERT INTO same_player_id VALUES (7,?)',(value,))
        original=Path(a['player_pool_db_path']).read_bytes()
        shutil.copyfile(b['player_pool_db_path'],a['player_pool_db_path'])
        with self.assertRaisesRegex(ValueError,'POOL_SAVE_BINDING_MISMATCH'):
            self.manager.activate('A')
        with self.assertRaisesRegex(ValueError,'POOL_SAVE_BINDING_MISMATCH'):
            stage(self.proposal(),self.source,self.reg)
        with self.assertRaisesRegex(ValueError,'POOL_SAVE_BINDING_MISMATCH'):
            with capture_lease('A',':'.join(binding(self.a).values())):self.fail('foreign pool accepted')
        import auto_pipeline_ingest
        with patch.object(auto_pipeline_ingest,'GameMemory') as memory:
            with self.assertRaisesRegex(ValueError,'POOL_SAVE_BINDING_MISMATCH'):
                with capture_lease('A',':'.join(binding(self.a).values())):
                    auto_pipeline_ingest.run_automated_ingestion(save_id='A')
            memory.assert_not_called()
        Path(a['player_pool_db_path']).write_bytes(original)
        self.manager.activate('A')
        stage(self.proposal(),self.source,self.reg)

    def stages(self):
        paths=save_context.save_paths('A')
        stamp=source_stamp(self.a,'M02','synthetic-time')
        staged=[]
        for key in ('db_path','player_pool_db_path'):
            target=paths[key]+'.capture'
            backup(paths[key],target)
            with closing(sqlite3.connect(target)) as c,c:
                put_metadata(c,stamp)
                stamp_database(c,'M02','A','synthetic-time')
            staged.append(target)
        return paths,staged,stamp

    def test_capture_replacement_preserves_all_three_source_bindings(self):
        paths,staged,stamp=self.stages()
        install(paths,*staged,stamp)
        self.manager.active('A')
        for key,table in (('db_path','save_metadata'),('player_pool_db_path','save_metadata'),('control_db_path','control_metadata')):
            with closing(sqlite3.connect(paths[key])) as c:
                meta=dict(c.execute('SELECT key,value FROM '+table))
                self.assertTrue(all(meta[k]==v for k,v in stamp.items()))
        with closing(sqlite3.connect(paths['player_pool_db_path'])) as c,c:
            c.execute("UPDATE data_sync_metadata SET data_updated_at='foreign' WHERE snapshot_id='M02'")
        with self.assertRaisesRegex(ValueError,'POOL_SOURCE_METADATA_MISMATCH'):self.manager.active('A')

    def test_failed_second_replace_restores_last_good_cohort(self):
        paths,staged,stamp=self.stages()
        original={k:Path(paths[k]).read_bytes() for k in ('db_path','player_pool_db_path','control_db_path')}
        replace=os.replace
        def fail(source,target):
            if source==staged[1]:raise OSError('SYNTHETIC_POOL_REPLACE_FAILURE')
            return replace(source,target)
        with patch('gm_state_io.capture_files.os.replace',side_effect=fail):
            with self.assertRaisesRegex(OSError,'SYNTHETIC_POOL'):install(paths,*staged,stamp)
        self.manager.active('A')
        for key,raw in original.items():self.assertEqual(Path(paths[key]).read_bytes(),raw)

    def test_crash_blocks_all_entry_points_until_explicit_capture_recovery(self):
        paths,staged,stamp=self.stages()
        replace=os.replace
        def crash(source,target):
            if source==staged[1]:raise KeyboardInterrupt('SYNTHETIC_CRASH')
            return replace(source,target)
        with patch('gm_state_io.capture_files.os.replace',side_effect=crash):
            with self.assertRaises(KeyboardInterrupt):install(paths,*staged,stamp)
        with self.assertRaisesRegex(ValueError,'CAPTURE_INSTALL_INCOMPLETE'):self.manager.active('A')
        with self.assertRaisesRegex(ValueError,'CAPTURE_INSTALL_INCOMPLETE'):self.manager.create('B')
        with self.assertRaises(PermissionError):self.manager.recover_capture('A','forged')
        self.assertEqual(self.manager.recover_capture('A',self.manager.read('A')['manifest_digest'])['status'],
                         'LAST_GOOD_CAPTURE_RESTORED')
        self.manager.active('A')

    def test_missing_specific_approval_refuses_and_player_attestation_executes(self):
        plan=stage(self.proposal(),self.source,self.reg)
        executor=Executor(self.reg,lambda ro:FakeSession(self.state,ro),self.root/'locks')
        with self.assertRaisesRegex(PermissionError,'SPECIFIC_EXTERNAL_PLAYER_APPROVAL_REQUIRED'):
            executor.run(plan,None)
        spec=importlib.util.spec_from_file_location('dev14_cli_hardening',ROOT/'scripts/gm_state_io.py')
        cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
        args=cli.parser().parse_args(['apply','--career','A','--change-set',plan['change_set_id'],
            '--approval',str(self.root/'player-approved.json'),
            '--player-approval-reference','model-claim','--loaded-save-confirmation',':'.join(binding(plan).values()),'--editors-closed'])
        with self.assertRaisesRegex(PermissionError,'MODEL_PROVIDED_CLAIM_ONLY'):cli.run(args)
        self.assertEqual(self.state['opens'],[])
        self.assertEqual(self.state['writes'],0)
        # The player explicitly accepts operator attestation rather than an
        # isolated issuer. Complete binding + a real approval reference + the
        # write trigger can use the existing deterministic synthetic backend.
        payload={key:plan[key] for key in ('save_id','save_instance_id','generation_id','source_batch_id','decision_id','version','digest')}
        payload['action_ids']=[a['action_id'] for a in plan['actions']]
        args.approval.write_text(__import__('json').dumps(payload))
        args.approve_game_writes=True
        args.player_approval_reference='SYNTHETIC_EXPLICIT_PLAYER_CHAT_APPROVAL'
        with patch('gm_state_io.executor.Executor',return_value=executor):
            result=cli.run(args)
        self.assertEqual(result['status'],'MEMORY_VERIFIED')
        self.assertEqual(result['approval_state'],'HUMAN_APPROVED_OPERATOR_ATTESTED')

    def test_foreground_manual_supervision_is_scoped_and_not_portable(self):
        plan=stage(self.proposal(),self.source,self.reg)
        executor=Executor(self.reg,lambda ro:FakeSession(self.state,ro),self.root/'locks')
        answers=[':'.join(binding(plan).values()),'EDITORS CLOSED','synthetic-human','APPROVE APPLY '+plan['digest']]
        with patch('sys.stdin.isatty',return_value=True),patch('sys.stdout.isatty',return_value=True), \
             patch('builtins.input',side_effect=answers),patch('builtins.print'):
            with review(plan) as (approval,token):
                with self.assertRaises(PermissionError):executor.run(plan,approval,rollback=True,supervision=token)
                changed=copy.deepcopy(plan);changed['actions'][0]['target_value']=2
                with self.assertRaises(PermissionError):executor.run(changed,approval,supervision=token)
                result=executor.run(plan,approval,supervision=token)
                self.assertEqual(result['status'],'MEMORY_VERIFIED')
                self.assertEqual(result['approval_trust'],'MANUAL_OPERATOR_TRUST_ONLY')
            with self.assertRaises(PermissionError):executor.run(plan,approval,supervision=token)
