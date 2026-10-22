"""Synthetic failure injection for batch ordering, ownership and recovery."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from test_coaching_safety import World,PROFILE
from gm_core.coaching import propose
from gm_core.coaching_batch import propose_batch,validate_batch,batch_digest,normalize_freelance,propose_overall_defense
from coaching_batch_executor import CoachingBatchExecutor,BatchApproval


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.world=World()
        self.profile=copy.deepcopy(PROFILE)
        self.temp=tempfile.TemporaryDirectory()
        patcher=patch('coaching_execution_lock.DEFAULT_LOCK_ROOT',Path(self.temp.name)/'shared_locks')
        patcher.start()
        self.addCleanup(patcher.stop)
        self.batch=propose_batch(self.world.snapshot,[dict(team_id=t,targets={'POEOffense':v},
            action_id='A'+str(t),expected_effect='synthetic technical validation only')
            for t,v in ((20,2),(8,1))],'B01','D01',1,profile=self.profile)
    def tearDown(self):self.temp.cleanup()
    def executor(self):return CoachingBatchExecutor(self.world.memory,self.world.locator,self.profile)
    def approval(self):
        b=self.batch
        return BatchApproval(b['career_id'],b['batch_id'],b['decision_id'],b['version'],
            tuple(a['action_id'] for a in b['actions']),batch_digest(b),True,True)
    def run_batch(self,rollback=False):
        return self.executor().run(self.batch,self.world.snapshot,self.approval(),self.temp.name,rollback)
    def test_offline_and_no_approval_zero_handles(self):
        self.assertTrue(self.executor().inspect(self.batch,self.world.snapshot)['executable'])
        with self.assertRaises(PermissionError):
            self.executor().run(self.batch,self.world.snapshot,None,self.temp.name)
        self.assertEqual(self.world.opens,[])
    def test_all_hold_batch_requires_no_game_handle(self):
        self.batch=propose_batch(self.world.snapshot,[],'HOLD01','D01',1,[8,20],profile=self.profile)
        result=self.run_batch()
        self.assertEqual(result['status'],'NO_WRITE_NEEDED')
        self.assertEqual(self.world.opens,[])
    def test_thirty_team_last_target_preflight_then_full_commit_and_restore(self):
        from config import CORE_TEAM_IDS
        template=copy.deepcopy(self.world.snapshot['teams'][0])
        raw=bytes(self.world.data[0x1000:0x1160])
        self.world.data=bytearray(0x8000)
        self.world.snapshot['teams']=[]
        addresses={}
        for index,tid in enumerate(sorted(CORE_TEAM_IDS)):
            row=copy.deepcopy(template)
            row.update(team_id=tid,abbreviation='T'+str(tid),
                coach_identity=dict(team_id=tid,identity_tag='SYNTHETIC_'+str(tid)))
            self.world.snapshot['teams'].append(row)
            addresses[tid]=0x1000+index*0x200
            self.world.data[addresses[tid]:addresses[tid]+0x160]=raw
        self.world.context={str(t['team_id']):t['coach_identity'] for t in self.world.snapshot['teams']}
        self.world.snapshot['context_identity']=copy.deepcopy(self.world.context)
        factory=self.world.locator
        def locator(mem,profile):
            loc=factory(mem,profile)
            loc.coaches={tid:{'address':address} for tid,address in addresses.items()}
            return loc
        self.world.locator=locator
        self.batch=propose_batch(self.world.snapshot,[dict(team_id=t,targets={'POEOffense':2},
            action_id='A'+str(t),expected_effect='30 synthetic teams; no game outcomes') for t in sorted(addresses)],
            'B30','D01',1,profile=self.profile)
        original=bytes(self.world.data)
        last=addresses[sorted(addresses)[-1]]+0x13f
        self.world.data[last]^=0x80
        with self.assertRaisesRegex(RuntimeError,'STALE_FULL_SHARED_BLOCK'):
            self.run_batch()
        self.assertEqual(self.world.opens,[True])
        self.assertEqual(self.world.writes,[])
        self.world.data[last]^=0x80
        self.assertEqual(self.run_batch()['status'],'COMMITTED_VERIFIED_IN_MEMORY')
        self.assertEqual(len(self.world.writes),30)
        self.assertEqual(self.run_batch(True)['status'],'ROLLED_BACK_VERIFIED_IN_MEMORY')
        self.assertEqual(bytes(self.world.data),original)
    def test_editor_closed_and_exact_action_approval_required(self):
        approval=self.approval()
        for key,value in [('coach_editor_closed_confirmed',False),('action_ids',('A8',))]:
            invalid=BatchApproval(**{**approval.__dict__,key:value})
            with self.assertRaises(PermissionError):
                self.executor().run(self.batch,self.world.snapshot,invalid,self.temp.name)
        self.assertEqual(self.world.opens,[])
    def test_last_target_stale_prevents_all_writes_and_rw(self):
        self.world.data[0x113f]^=0x80
        with self.assertRaisesRegex(RuntimeError,'STALE_FULL_SHARED_BLOCK'):
            self.run_batch()
        self.assertEqual(self.world.writes,[])
        self.assertEqual(self.world.opens,[True])
    def test_two_team_commit_idempotency_and_reverse_recovery(self):
        original=bytes(self.world.data)
        result=self.run_batch()
        self.assertEqual(result['status'],'COMMITTED_VERIFIED_IN_MEMORY')
        self.assertEqual(len(self.world.writes),2)
        self.assertTrue(self.run_batch()['idempotent'])
        self.assertEqual(len(self.world.writes),2)
        self.assertEqual(self.run_batch(True)['status'],'ROLLED_BACK_VERIFIED_IN_MEMORY')
        self.assertEqual(bytes(self.world.data),original)
    def test_second_write_failure_reverses_first(self):
        original=bytes(self.world.data)
        memory=self.world.memory
        calls=[]
        def fail_second(read_only=True):
            mem=memory(read_only)
            write=mem.write_bytes
            def mutate(at,data):
                calls.append(at)
                return False if len(calls)==2 else write(at,data)
            mem.write_bytes=mutate
            return mem
        self.world.memory=fail_second
        with self.assertRaisesRegex(RuntimeError,'FAILED_ROLLED_BACK_TO_OPERATION_PREIMAGE'):
            self.run_batch()
        self.assertEqual(bytes(self.world.data),original)
    def test_third_party_change_is_not_overwritten_on_rollback(self):
        memory=self.world.memory
        calls=[]
        def concurrent(read_only=True):
            mem=memory(read_only)
            write=mem.write_bytes
            def mutate(at,data):
                calls.append(at)
                if len(calls)==2:
                    self.world.data[calls[0]]^=1
                    return False
                return write(at,data)
            mem.write_bytes=mutate
            return mem
        self.world.memory=concurrent
        with self.assertRaisesRegex(RuntimeError,'PARTIAL_UNRECOVERED_MANUAL_REVIEW'):
            self.run_batch()
        self.assertEqual(len(calls),2)
    def test_duplicate_scope_hold_conflict_and_json_approval_denied(self):
        for modify in ('duplicate','hold','approval'):
            batch=copy.deepcopy(self.batch)
            if modify=='duplicate':batch['actions'].append(copy.deepcopy(batch['actions'][0]))
            elif modify=='hold':batch['hold_team_ids']=[8]
            else:batch['approved']=True
            self.assertFalse(validate_batch(batch,self.world.snapshot,self.profile)['valid'])
        self.assertEqual(self.world.opens,[])
    def test_five_sim_fields_never_accepted_for_gm(self):
        for field in ('SimPace','SimPress','SimHelpDef','SimOffReb','SimDefReb'):
            with self.assertRaisesRegex(ValueError,'GM_CONTROL_DISABLED'):
                propose(self.world.snapshot,20,{field:0},'D01',1,'S01','not allowed',profile=self.profile)
    def test_ordered_freelance_and_slot_array_conflicts(self):
        slots=self.profile['freelance_slot_order']
        self.assertEqual(list(normalize_freelance({'freelance_sets':[5,3,18,28]},self.profile).items()),list(zip(slots,[5,3,18,28])))
        with self.assertRaises(ValueError):
            normalize_freelance({'freelance_sets':[5,3,18,28],'FreelanceType':0},self.profile)
    def test_gm_bench_count_is_not_capped_at_test_value_ten(self):
        for count in (7,11,12,15):
            with self.subTest(count=count):
                batch=propose_batch(self.world.snapshot,[dict(team_id=20,targets={'BenchDepth':count},
                    action_id='BENCH',expected_effect='Synthetic chosen rotation count, not a recommendation')],
                    'BENCH'+str(count),'D01',1,profile=self.profile)
                self.assertTrue(validate_batch(batch,self.world.snapshot,self.profile)['executable'])
        for invalid in (-1,256,True,11.5):
            with self.assertRaises(ValueError):
                propose_batch(self.world.snapshot,[dict(team_id=20,targets={'BenchDepth':invalid},
                    action_id='BAD_BENCH',expected_effect='Invalid native integer format')],
                    'BAD_BENCH','D01',1,profile=self.profile)
        self.assertEqual(self.world.opens,[])
    def test_formal_ordered_freelance_uses_full_native_catalog_and_restores_shared_blocks(self):
        self.world.snapshot.update(environment='FORMAL_READ_ONLY',game_date='2021-10-19')
        desired=[33,1,24,0]
        self.batch=propose_batch(self.world.snapshot,[dict(team_id=20,targets={'freelance_sets':desired},
            action_id='FREE',expected_effect='Synthetic complete catalog and ordered-slot contract only')],
            'FULL_NATIVE_FREELANCE','D01',1,profile=self.profile)
        result=validate_batch(self.batch,self.world.snapshot,self.profile)
        self.assertTrue(result['executable'])
        self.assertEqual(len(result['prepared_actions'][0]['blocks']),3)
        original=bytes(self.world.data)
        self.assertEqual(self.run_batch()['status'],'COMMITTED_VERIFIED_IN_MEMORY')
        from coach_codec import decode
        observed=[decode(self.world.data[0x1000:0x1160],self.profile['fields'][name])
                  for name in self.profile['freelance_slot_order']]
        self.assertEqual(observed,desired)
        self.run_batch(True)
        self.assertEqual(bytes(self.world.data),original)
    def test_native_tempo_raw_bounds_masked_commit_and_restore_without_ui_claim(self):
        from coach_codec import decode
        field=self.profile['fields']['Tempo']
        self.assertTrue(field['writable'] and field['production_enabled'])
        self.assertEqual(field['ui_unit'],'UNKNOWN_NATIVE_RAW_INTEGER')
        self.assertIsNone(field['ui_label_zh'])
        self.assertNotIn('raw_range',field)
        self.world.snapshot.update(environment='FORMAL_READ_ONLY',game_date='2021-10-19')
        original=bytes(self.world.data)
        start=0x1000+field['offset']
        mask=((1 << field['width'])-1) << field['start_bit']
        for value in (0,255):
            with self.subTest(value=value):
                self.batch=propose_batch(self.world.snapshot,[dict(team_id=20,targets={'Tempo':value},
                    action_id='NATIVE_RAW',expected_effect='Synthetic native raw boundary only; UI and gameplay effect unknown')],
                    'TEMPO_RAW_'+str(value),'D01',1,profile=self.profile)
                self.assertEqual(self.run_batch()['status'],'COMMITTED_VERIFIED_IN_MEMORY')
                self.assertEqual(decode(self.world.data[0x1000:0x1160],field),value)
                before=int.from_bytes(original[start:start+4],'little')
                after=int.from_bytes(self.world.data[start:start+4],'little')
                self.assertEqual((before ^ after) & ~mask,0)
                self.assertEqual(bytes(self.world.data[:start]),original[:start])
                self.assertEqual(bytes(self.world.data[start+4:]),original[start+4:])
                self.assertEqual(self.run_batch(True)['status'],'ROLLED_BACK_VERIFIED_IN_MEMORY')
                self.assertEqual(bytes(self.world.data),original)
        opens=len(self.world.opens)
        for invalid in (-1,256,True,80.5):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                propose_batch(self.world.snapshot,[dict(team_id=20,targets={'Tempo':invalid},
                    action_id='BAD_RAW',expected_effect='Invalid native integer format')],
                    'BAD_TEMPO','D01',1,profile=self.profile)
        self.assertEqual(len(self.world.opens),opens)
    def test_formal_pending_field_cannot_request_handle(self):
        self.world.snapshot['environment']='FORMAL_READ_ONLY'
        self.world.snapshot['game_date']='2021-10-19'
        self.batch['game_date']='2021-10-19'
        for action in self.batch['actions']:action['game_date']='2021-10-19'
        self.profile['fields']['POEOffense']['production_enabled']=False
        with self.assertRaisesRegex(PermissionError,'PRODUCTION_FIELDS_NOT_READY'):
            self.run_batch()
        self.assertEqual(self.world.opens,[])
    def configure_synthetic_mixed(self):
        self.profile['native']['gameplan_capacity']=1
        self.profile['opponent_overall_defense'].update(production_enabled=True,
            record_selector=dict(mode='UI_BULK_ALL_PRESENT_MATCHUPS',entry_start=0x64,entry_stride=12,entry_count=23))
        # Synthetic selector for codec/transaction tests only, never written to real profile.
        catalog={'PressureOnball':dict(offset=0,start_bit=0,width=3,native_enum_name_crc32={'0':'AUTO_CRC','1':'GAP_CRC'})}
        self.profile['defensive_fields']['PressureOnball']['production_enabled']=True
        self.world.snapshot['defensive_field_catalog']=catalog
        header=bytes([1,0,20,0,8,0])
        self.world.data[0x3004:0x300a]=header
        for index in range(23):
            at=0x3004+0x64+index*12
            self.world.data[at:at+12]=b'\xff'*4+bytes(8)
        self.world.data[0x3068:0x306a]=(42).to_bytes(2,'little')
        self.world.data[0x3074:0x3076]=(43).to_bytes(2,'little')
        from coaching_overall import overall_from_raw
        overall=overall_from_raw(bytes(self.world.data[0x3004:0x3374]),self.profile['opponent_overall_defense'],catalog)
        self.world.snapshot['teams'][0]['gameplans']=[dict(opponent_team_id=8,is_in_use=1,overall_defense=overall)]
        default=propose(self.world.snapshot,8,{'POEOffense':1},'D01',1,'A8','synthetic default',profile=self.profile)
        defense=propose_overall_defense(self.world.snapshot,20,8,{'PressureOnball':1},'D01',1,'DEF20_8','synthetic overall',self.profile)
        self.batch['actions']=[default,defense]
        factory=self.world.locator
        def locator(mem,profile):
            loc=factory(mem,profile)
            loc.profile=profile
            loc.managers={20:0x3000}
            return loc
        self.world.locator=locator
        return patch('coaching_reader.defensive_catalog',return_value=catalog)
    def test_mixed_default_and_overall_commit_preserves_matchup_ids(self):
        with self.configure_synthetic_mixed():
            before=bytes(self.world.data)
            self.assertEqual(self.run_batch()['status'],'COMMITTED_VERIFIED_IN_MEMORY')
            self.assertEqual(self.world.data[0x3068:0x306c],before[0x3068:0x306c])
            self.assertEqual(self.world.data[0x306c],1)
            self.assertEqual(self.world.data[0x3078],1)
            self.run_batch(True)
            self.assertEqual(bytes(self.world.data),before)
    def test_mixed_overall_wrong_record_blocks_all_targets(self):
        with self.configure_synthetic_mixed():
            self.world.data[0x3068]=1
            with self.assertRaisesRegex(RuntimeError,'OVERALL_RECORD_IDENTITY_CHANGED'):
                self.run_batch()
            self.assertEqual(self.world.writes,[])
            self.assertEqual(self.world.opens,[True])
    def test_overall_cannot_select_subset_or_source_supplied_arbitrary_offset(self):
        with self.configure_synthetic_mixed():
            defense=self.batch['actions'][1]
            defense['old_defense_blocks']=defense['old_defense_blocks'][:1]
            self.assertFalse(validate_batch(self.batch,self.world.snapshot,self.profile)['valid'])
            overall=self.world.snapshot['teams'][0]['gameplans'][0]['overall_defense']
            defense['old_defense_blocks']=copy.deepcopy(overall['blocks'])
            overall['blocks'][0]['settings_offset']=0x200
            defense['old_defense_blocks'][0]['settings_offset']=0x200
            with self.assertRaisesRegex(RuntimeError,'OUTSIDE_VERIFIED_OVERALL_BLOCK'):
                self.run_batch()
            self.assertEqual(self.world.writes,[])
    def test_ui_commit_flag_written_last_and_restored_with_group(self):
        with self.configure_synthetic_mixed():
            self.world.data[0x3004]=0
            overall=self.world.snapshot['teams'][0]['gameplans'][0]['overall_defense']
            overall['header_signature']='00'+overall['header_signature'][2:]
            overall['commit_flag_raw']=0
            before=bytes(self.world.data)
            result=self.run_batch()
            self.assertEqual(result['write_log'][-1]['offset'],0)
            self.assertEqual(self.world.data[0x3004],1)
            committed_addresses=[address for address,_ in self.world.writes]
            self.run_batch(True)
            self.assertEqual([address for address,_ in self.world.writes[len(committed_addresses):]],
                             list(reversed(committed_addresses)))
            self.assertEqual(bytes(self.world.data),before)
    def test_mixed_second_object_failure_restores_first_object(self):
        with self.configure_synthetic_mixed():
            before=bytes(self.world.data)
            memory=self.world.memory
            count=[]
            def fail_defense(read_only=True):
                mem=memory(read_only)
                write=mem.write_bytes
                def mutate(at,data):
                    count.append(at)
                    return False if len(count)==2 else write(at,data)
                mem.write_bytes=mutate
                return mem
            self.world.memory=fail_defense
            with self.assertRaisesRegex(RuntimeError,'FAILED_ROLLED_BACK_TO_OPERATION_PREIMAGE'):
                self.run_batch()
            self.assertEqual(bytes(self.world.data),before)


if __name__=='__main__':unittest.main()
