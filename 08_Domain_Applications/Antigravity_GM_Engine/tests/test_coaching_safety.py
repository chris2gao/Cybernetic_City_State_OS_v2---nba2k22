"""Native codec and transaction failures: no real game handles are used."""
import ast
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from coach_codec import load_profile,decode,encode_changes,block_key
from gm_core.coaching import propose,validate_plan
from coaching_executor import CoachingExecutor,PlayerApproval,plan_digest
from coaching_reader import gameplans,decode_native
from coach_locator import CoachLocator,read_exact

PROFILE=load_profile()
ROOT=Path(__file__).resolve().parents[1]

def fixture():
    raw=bytearray([0xa5]*0x160)
    # A valid neutral coach with arbitrary reserved bits and loaded playbook.
    changes=[]
    for name,f in PROFILE["fields"].items():
        value=int(next(iter(f["enum"]))) if isinstance(f.get("enum"),dict) else (18 if f.get("enum")=="LOADED_PLAYBOOKS" else 50)
        old=int.from_bytes(raw[f["offset"]:f["offset"]+f["storage_bytes"]],"little")
        mask=((1<<f["width"])-1)<<f["start_bit"]
        raw[f["offset"]:f["offset"]+f["storage_bytes"]]=((old&~mask)|(value<<f["start_bit"])).to_bytes(f["storage_bytes"],"little")
    blocks={block_key(f["offset"],f["storage_bytes"]):raw[f["offset"]:f["offset"]+f["storage_bytes"]].hex() for f in PROFILE["fields"].values()}
    teams=[]
    for tid in (20,8):
        teams.append(dict(team_id=tid,abbreviation={20:"IND",8:"GS"}[tid],coach_identity={"team_id":tid,"identity_tag":str(tid)},
                          values={n:decode(raw,f) for n,f in PROFILE["fields"].items()},blocks=blocks.copy(),gameplans=[]))
    snapshot=dict(schema_version=1,snapshot_id="TEST_SNAPSHOT",environment="ISOLATED_TEST",observation_status="OBSERVED_LIVE_READ_ONLY",
                  career_id="ISOLATED_UNIT_TEST",source_batch_id="TEST_BATCH",game_season="2021-2022",game_date=None,
                  policy_id="PLAYER_RULES_20261017_V3",codec_version=PROFILE["codec_version"],process_pid=123,
                  process_creation_time="TEST_CREATION_TIME",native_evidence={"status":"TEST_NATIVE"},
                  context_identity={str(t["team_id"]):t["coach_identity"] for t in teams},teams=teams,
                  playbooks=[{"enum_id":18,"name":"Test Book","play_crc_slots":[0]*68}],loaded_playbook_ids=[18])
    plan=propose(snapshot,20,{"POEOffense":2,"POEDefense":13},"TEST_DECISION",1,"A01","技术测试，无战绩结论")
    return bytes(raw),snapshot,plan

class World:
    def __init__(self):
        raw,self.snapshot,self.plan=fixture()
        self.data=bytearray(0x4000)
        self.data[0x1000:0x1160]=raw
        self.data[0x2000:0x2160]=raw
        self.opens=[]
        self.writes=[]
        self.pid=123
        self.context=copy.deepcopy(self.snapshot["context_identity"])
        self.books=copy.deepcopy(self.snapshot["playbooks"])
        self.fail_write=False
        self.corrupt_after_write=False
        self.unknown_after_write=False
    def memory(self,read_only=True):
        world=self
        self.opens.append(read_only)
        class Memory:
            pid=world.pid
            creation_time="TEST_CREATION_TIME"
            base_address=0x400000
            def is_alive(self):return True
            def read_bytes(self,at,size):return bytes(world.data[at:at+size])
            def write_bytes(self,at,data):
                if read_only:raise AssertionError("READ_ONLY_WRITE")
                world.writes.append((at,bytes(data)))
                if world.fail_write:return False
                world.data[at:at+len(data)]=data
                if world.corrupt_after_write:
                    world.data[at]^=1
                if world.unknown_after_write:
                    world.context={"changed":True}
                return True
            def close(self):pass
        return Memory()
    def locator(self,mem,profile):
        world=self
        class Locator:
            def __init__(self):
                self.mem=mem
                self.playbooks=copy.deepcopy(world.books)
                self.coaches={20:{"address":0x1000},8:{"address":0x2000}}
                self.evidence={"status":"TEST_NATIVE"}
            def calibrate(self):return self
            def context_identity(self):return copy.deepcopy(world.context)
            def close(self):mem.close()
        return Locator()
    def executor(self):return CoachingExecutor(self.memory,self.locator)
    def approval(self):
        p=self.plan
        return PlayerApproval(p["career_id"],p["decision_id"],p["version"],(p["action_id"],),plan_digest(p),True,True)

class CodecTests(unittest.TestCase):
    def test_all_legal_enums_and_reserved_bits(self):
        raw,_,_=fixture()
        for name,f in PROFILE["fields"].items():
            if f.get('gm_control_enabled') is False:continue
            if not isinstance(f.get("enum"),dict):continue
            for enum in map(int,f["enum"]):
                with self.subTest(field=name,value=enum):
                    b=encode_changes(raw,[dict(field=name,before_raw=decode(raw,f),after_raw=enum)],PROFILE,[18])[0]
                    after=bytearray(raw)
                    after[b["offset"]:b["offset"]+b["size"]]=bytes.fromhex(b["after"])
                    self.assertEqual(decode(after,f),enum)
                    old=int.from_bytes(bytes.fromhex(b["before"]),"little")
                    new=int.from_bytes(bytes.fromhex(b["after"]),"little")
                    self.assertEqual((old^new)&~b["mask"],0)
                    if name.startswith("POE"):self.assertEqual(old&0xc0000000,new&0xc0000000)
    def test_illegal_poe_and_strict_types(self):
        raw,_,_=fixture()
        for name,f in PROFILE["fields"].items():
            if not name.startswith("POE"):continue
            for value in list(set(range(32))-set(map(int,f["enum"])))+[True,1.0,"2",None,-1,32]:
                with self.subTest(field=name,value=value):
                    with self.assertRaises(ValueError):encode_changes(raw,[dict(field=name,before_raw=decode(raw,f),after_raw=value)],PROFILE)
    def test_shared_block_is_one_write(self):
        raw,s,p=fixture()
        result=encode_changes(raw,p["changes"],PROFILE)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]["size"],4)
        self.assertEqual(set(result[0]["fields"]),{"POEOffense","POEDefense"})
    def test_loaded_playbook_only(self):
        raw,s,p=fixture()
        with self.assertRaisesRegex(ValueError,"PLAYBOOK_NOT_LOADED"):
            encode_changes(raw,[dict(field="PlaybookID",before_raw=18,after_raw=19)],PROFILE,[18])
    def test_readonly_field_write_denied(self):
        raw,s,p=fixture()
        # Tempo is now player-approved raw read/write. Exercise a deliberately
        # read-only fixture rather than reinstate the superseded production gate.
        readonly=copy.deepcopy(PROFILE)
        readonly['fields']['Tempo']['writable']=False
        with self.assertRaisesRegex(ValueError,"FIELD_READ_ONLY"):
            encode_changes(raw,[dict(field="Tempo",before_raw=decode(raw,readonly["fields"]["Tempo"]),after_raw=80)],readonly,for_write=True)
    def test_target_range_does_not_reject_observed_preimage(self):
        raw,s,p=fixture()
        profile=copy.deepcopy(PROFILE)
        profile['fields']['BenchDepth']['raw_range']=[9,10]
        old=decode(raw,profile['fields']['BenchDepth'])
        self.assertNotIn(old,range(9,11))
        result=encode_changes(raw,[dict(field='BenchDepth',before_raw=old,after_raw=10)],profile)
        self.assertEqual(result[0]['after'],'0a')
        with self.assertRaisesRegex(ValueError,'OUTSIDE_VERIFIED_RAW_RANGE'):
            encode_changes(raw,[dict(field='BenchDepth',before_raw=old,after_raw=11)],profile)
    def test_unknown_or_duplicate_field(self):
        raw,s,p=fixture()
        for changes in ([dict(field="poe_off_pace",before_raw=0,after_raw=1)],p["changes"]*2):
            with self.assertRaises(ValueError):encode_changes(raw,changes,PROFILE)
    def test_incomplete_read_is_unknown(self):
        with self.assertRaisesRegex(RuntimeError,"UNREADABLE"):
            read_exact(type("M",(),{"read_bytes":lambda *a:b"\0"})(),12,4)

class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.w=World();self.temp=tempfile.TemporaryDirectory()
        patcher=patch('coaching_execution_lock.DEFAULT_LOCK_ROOT',Path(self.temp.name)/'shared_locks')
        patcher.start()
        self.addCleanup(patcher.stop)
    def tearDown(self):self.temp.cleanup()
    def run_action(self,rollback=False):return self.w.executor().run(self.w.plan,self.w.snapshot,self.w.approval(),self.temp.name,rollback)
    def test_default_dry_run_has_no_handles(self):
        result=self.w.executor().inspect(self.w.plan,self.w.snapshot)
        self.assertTrue(result["valid"])
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(self.w.opens,[])
    def test_no_approval_no_handles(self):
        with self.assertRaises(PermissionError):self.w.executor().run(self.w.plan,self.w.snapshot,None,self.temp.name)
        self.assertEqual(self.w.opens,[])
    def test_json_approval_cannot_authorize(self):
        self.w.plan["approved"]=True
        with self.assertRaises(ValueError):self.run_action()
        self.assertEqual(self.w.opens,[])
    def test_editor_closed_precondition_before_handles(self):
        p=self.w.plan
        approval=PlayerApproval(p['career_id'],p['decision_id'],p['version'],(p['action_id'],),plan_digest(p),True)
        with self.assertRaisesRegex(PermissionError,'COACH_EDITOR_MUST_BE_CLOSED'):
            self.w.executor().run(p,self.w.snapshot,approval,self.temp.name)
        self.assertEqual(self.w.opens,[])
    def test_formal_disabled_before_handles(self):
        self.w.snapshot["environment"]="FORMAL_READ_ONLY"
        self.w.snapshot["game_date"]=self.w.plan["game_date"]="2021-10-19"
        profile=copy.deepcopy(PROFILE)
        profile['fields']['POEOffense']['production_enabled']=False
        executor=CoachingExecutor(self.w.memory,self.w.locator,profile)
        with self.assertRaisesRegex(PermissionError,"PRODUCTION_DISABLED"):
            executor.run(self.w.plan,self.w.snapshot,self.w.approval(),self.temp.name)
        self.assertEqual(self.w.opens,[])
    def test_ready_formal_fields_still_require_exact_external_approval(self):
        self.w.snapshot['environment']='FORMAL_READ_ONLY'
        self.w.snapshot['game_date']=self.w.plan['game_date']='2021-10-19'
        profile=copy.deepcopy(PROFILE)
        for change in self.w.plan['changes']:
            profile['fields'][change['field']]['production_enabled']=True
        executor=CoachingExecutor(self.w.memory,self.w.locator,profile)
        with self.assertRaisesRegex(PermissionError,'SPECIFIC_EXTERNAL_PLAYER_APPROVAL_REQUIRED'):
            executor.run(self.w.plan,self.w.snapshot,None,self.temp.name)
        self.assertEqual(self.w.opens,[])
        p=self.w.plan
        approval=PlayerApproval(p['career_id'],p['decision_id'],p['version'],(p['action_id'],),plan_digest(p),False,True)
        receipt=executor.run(p,self.w.snapshot,approval,self.temp.name)
        self.assertEqual(receipt['status'],'EXECUTED_VERIFIED')
        self.assertEqual(len(self.w.writes),1)
    def test_wrong_coach_plan_before_handles(self):
        self.w.plan["verified_coach_identity"]={"wrong":True}
        with self.assertRaises(ValueError):self.run_action()
        self.assertEqual(self.w.opens,[])
    def test_changed_save_no_rw_handle(self):
        self.w.context={"wrong":True}
        with self.assertRaisesRegex(RuntimeError,"WRONG_SAVE"):self.run_action()
        self.assertEqual(self.w.opens,[True])
    def test_pid_change_no_rw_handle(self):
        self.w.pid=456
        with self.assertRaisesRegex(RuntimeError,"STALE_PID"):self.run_action()
        self.assertEqual(self.w.opens,[True])
    def test_loaded_book_changed_no_rw_handle(self):
        self.w.books[0]["play_crc_slots"][0]=12345
        with self.assertRaisesRegex(RuntimeError,"DIRECTORY_CHANGED"):self.run_action()
        self.assertEqual(self.w.opens,[True])
    def test_spoofed_loaded_ids_cannot_allow_unnamed_book(self):
        self.w.snapshot["loaded_playbook_ids"].append(97)
        self.assertFalse(validate_plan(self.w.plan,self.w.snapshot)["valid"])
        with self.assertRaises(ValueError):self.run_action()
        self.assertEqual(self.w.opens,[])
    def test_shared_reserved_bit_changed_no_rw(self):
        self.w.data[0x113f]^=0x80
        with self.assertRaisesRegex(RuntimeError,"STALE_FULL"):self.run_action()
        self.assertEqual(self.w.opens,[True])
    def test_one_write_neighbor_team_idempotence_and_rollback(self):
        original=bytes(self.w.data)
        result=self.run_action()
        self.assertEqual(result["status"],"EXECUTED_VERIFIED")
        self.assertEqual(len(self.w.writes),1)
        self.assertEqual(bytes(self.w.data[0x2000:0x2160]),original[0x2000:0x2160])
        self.assertEqual(result["persistence"],"NOT_VERIFIED_BY_MEMORY_READBACK")
        repeated=self.run_action()
        self.assertTrue(repeated["idempotent"])
        self.assertEqual(repeated['current_state'],'NOT_REVALIDATED_CACHED_RECEIPT')
        self.assertEqual(len(self.w.writes),1)
        self.assertEqual(self.run_action(True)["status"],"ROLLED_BACK")
        self.assertEqual(bytes(self.w.data),original)
        self.assertTrue(self.run_action(True)["idempotent"])
    def test_other_team_can_be_target_independently(self):
        original=bytes(self.w.data[0x1000:0x1160])
        self.w.plan=propose(self.w.snapshot,8,{"POEOffense":4},"D2",1,"A2","技术测试")
        self.run_action()
        self.assertEqual(bytes(self.w.data[0x1000:0x1160]),original)
        self.assertEqual(self.w.writes[0][0],0x213c)
    def test_error_rolls_back_without_clearing_unrelated_changes(self):
        self.w.corrupt_after_write=True
        with self.assertRaisesRegex(RuntimeError,"PARTIAL_UNRECOVERED"):self.run_action()
        self.assertEqual(len(self.w.writes),1)
        journal=json.loads(next(Path(self.temp.name).glob("*.json")).read_text())
        self.assertEqual(journal["status"],"PARTIAL_UNRECOVERED")
    def test_failed_write_with_unchanged_block_restores(self):
        self.w.fail_write=True
        with self.assertRaisesRegex(RuntimeError,"FAILED_ROLLED_BACK"):self.run_action()
    def test_explicit_rollback_does_not_overwrite_new_value(self):
        self.run_action()
        self.w.data[0x113c]^=1
        with self.assertRaisesRegex(RuntimeError,"STALE_FULL"):self.run_action(True)
        self.assertEqual(len(self.w.writes),1)
    def test_preimage_exists_before_first_write(self):
        memory=self.w.memory
        def checked(read_only=True):
            mem=memory(read_only)
            if not read_only:
                write=mem.write_bytes
                def wrapped(at,data):
                    journals=list(Path(self.temp.name).glob("*.json"))
                    self.assertEqual(len(journals),1)
                    self.assertEqual(json.loads(journals[0].read_text())["status"],"PREPARED")
                    return write(at,data)
                mem.write_bytes=wrapped
            return mem
        self.w.memory=checked
        self.run_action()
    def test_gameplan_preset_stays_blocked(self):
        self.w.snapshot["teams"][0]["gameplans"]=[dict(opponent_team_id=8,is_in_use=0,values={"POEOffense":0})]
        self.w.plan=propose(self.w.snapshot,20,{"POEOffense":2},"D",1,"A","预设",8)
        result=self.w.executor().inspect(self.w.plan,self.w.snapshot)
        self.assertTrue(result["valid"])
        self.assertIn("MATCHUP_EXECUTION_BLOCKED_NOT_ACTIVATED",result["readiness"])
        with self.assertRaisesRegex(PermissionError,"MATCHUP_EXECUTION_BLOCKED"):self.run_action()
        self.assertEqual(self.w.opens,[])

class LegacyAndBoundaryTests(unittest.TestCase):
    def test_old_setter_rejects_before_any_memory_access(self):
        from strategy_manager import StrategyManager
        manager=object.__new__(StrategyManager)
        with self.assertRaisesRegex(RuntimeError,"LEGACY_TEAM_POE_OFFSETS_REVOKED"):
            manager.set_team_strategy(20,off_pace=5)
    def test_bootstrap_preserves_ticket_only(self):
        from bootstrap_new_game import apply_approved_ticket_templates
        class Manager:
            def set_ticket_pricing(self,tid,**kwargs):calls.append((tid,kwargs));return True
            def set_team_strategy(self,*a,**k):raise AssertionError("Legacy write")
        calls=[]
        count=apply_approved_ticket_templates({20:{"abbreviation":"IND"}},Manager())
        self.assertEqual(count,1)
        self.assertEqual(calls[0][0],20)
    def test_no_other_legacy_setter_callers(self):
        for path in (ROOT/"src").rglob("*.py"):
            tree=ast.parse(path.read_text(encoding="utf-8-sig"))
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
                    self.assertNotEqual(node.func.attr,"set_team_strategy",str(path))
    def test_gm_core_has_no_game_imports(self):
        denied={"memory","coach_locator","coaching_executor","strategy_manager","scanner"}
        for path in (ROOT/"src/gm_core").glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8-sig"))):
                if isinstance(node,ast.ImportFrom):self.assertNotIn((node.module or "").split(".")[0],denied)
                elif isinstance(node,ast.Import):
                    for item in node.names:self.assertNotIn(item.name.split(".")[0],denied)

class LocatorAndGameplanTests(unittest.TestCase):
    def test_manager_owner_ids_are_not_array_indices(self):
        profile=copy.deepcopy(PROFILE)
        profile["native"].update(franchise_capacity=6,franchise_teams_offset=0x100,franchise_team_stride=0x80)
        data=bytearray([255]*0x1000)
        data[0x180:0x182]=(20).to_bytes(2,"little")
        data[0x380:0x382]=(8).to_bytes(2,"little")
        mem=type("M",(),{"read_bytes":lambda _,at,size:bytes(data[at:at+size])})()
        locator=CoachLocator(mem,profile)
        locator.franchise=0
        locator.teams={20:{},8:{}}
        locator.resolve_managers()
        self.assertEqual(locator.managers,{20:0x180,8:0x380})
        data[0x200:0x202]=(20).to_bytes(2,"little")
        locator.managers={}
        with self.assertRaisesRegex(RuntimeError,"DUPLICATE_GAMEPLAN_MANAGER"):locator.resolve_managers()
    def test_coach_directory_duplicate_owner_and_role_fail(self):
        from source_extensions import STAFF_TEAM_SLOTS
        world=World()
        mem=world.memory()
        locator=CoachLocator(mem)
        locator.teams={20:{"address":0x500},8:{"address":0x600}}
        locator.directory={"staff":{"address":0x1000,"stride":0x160,"count":2}}
        locator.roster_signature=lambda team:"test_roster"
        world.data[0x500+0xce8:0x500+0xcf0]=(0x1000).to_bytes(8,"little")
        world.data[0x600+0xce8:0x600+0xcf0]=(0x1160).to_bytes(8,"little")
        def detail(mem,anchor,slot,teams):
            return ({"team_id":20 if slot==0 else 8,"fields":{"vitals":{"position":{"value":0}}},
                     "team_mapping_status":"VERIFIED_RECIPROCAL_TEAM_ROLE","first_name":"Test","last_name":str(slot)},bytes(0x160))
        with patch("source_extensions.staff_details",side_effect=detail):
            locator.resolve_coaches()
            self.assertEqual(set(locator.coaches),{20,8})
            world.data[0x600+0xce8:0x600+0xcf0]=(0x1000).to_bytes(8,"little")
            with self.assertRaisesRegex(RuntimeError,"DUPLICATE_HEAD_COACH"):locator.resolve_coaches()
        world.data[0x600+0xce8:0x600+0xcf0]=(0x1160).to_bytes(8,"little")
        def wrong_role(*args):
            row,raw=detail(*args)
            row["fields"]["vitals"]["position"]["value"]=1
            return row,raw
        with patch("source_extensions.staff_details",side_effect=wrong_role):
            with self.assertRaisesRegex(RuntimeError,"COACH_ROLE"):locator.resolve_coaches()
    def test_gameplan_bytes_are_not_coach_bitfields(self):
        from gameplan_codec import decode_header,encode_changes as gameplan_encode
        raw=bytearray(0x370)
        raw[2:4]=(20).to_bytes(2,"little")
        raw[4:6]=(8).to_bytes(2,"little")
        raw[0x17e:0x184]=bytes([2,7,10,13,16,19])
        result=decode_header(raw)
        self.assertEqual(result["values"]["POEOffense2"],7)
        self.assertEqual(result["values"]["POEDefense3"],19)
        self.assertEqual(result["is_in_use"],0)
        with self.assertRaises(PermissionError):gameplan_encode(raw,{"IsInUse":1})
        with self.assertRaises(ValueError):decode_header(raw[:-1])
    def test_invalid_self_or_duplicate_opponents_fail_closed(self):
        from coaching_reader import DEFENSE_NAMES
        import zlib
        n=PROFILE["native"]
        raw=bytearray([255]*(n["gameplan_start"]+n["gameplan_capacity"]*n["gameplan_stride"]))
        def set_record(index,owner,opponent):
            at=n["gameplan_start"]+index*n["gameplan_stride"]
            raw[at:at+n["gameplan_stride"]]=bytes(n["gameplan_stride"])
            raw[at+2:at+4]=owner.to_bytes(2,"little")
            raw[at+4:at+6]=opponent.to_bytes(2,"little")
        set_record(9,20,8)
        profile=copy.deepcopy(PROFILE)
        profile['opponent_overall_defense']['record_selector']=None
        profile['defensive_fields']={}
        loc=type("L",(),{"profile":profile,"teams":{20:{},8:{}},"managers":{20:0},
                         "mem":type("M",(),{"read_bytes":lambda _,at,size:bytes(raw[at:at+size])})(),
                         "defense_fields":{zlib.crc32(name.encode()):dict(offset=0,size=4,format=1<<8,enum_address=0) for name in DEFENSE_NAMES}})()
        loc.defense_fields[zlib.crc32(b'PreRotate')]['format']=(5<<24)|(1<<8)
        self.assertEqual(len(gameplans(loc,20)),1)
        set_record(10,20,8)
        with self.assertRaisesRegex(RuntimeError,"DUPLICATE_OPPONENT"):gameplans(loc,20)
        set_record(10,20,20)
        with self.assertRaisesRegex(RuntimeError,"SELF_GAMEPLAN"):gameplans(loc,20)
        set_record(10,8,20)
        with self.assertRaisesRegex(RuntimeError,"OWNER_MISMATCH"):gameplans(loc,20)
    def test_old_proposal_requires_native_snapshot_contract(self):
        from fixtures import project,proposal
        from gm_core.decisions import validate_proposal
        with tempfile.TemporaryDirectory() as directory:
            data=project(directory)
            old=proposal(data)
            old.update(operation="TACTIC_CHANGE",changes=[{"field":"poe_off_pace","value":3}])
            result=validate_proposal(old,data)
            self.assertFalse(result["valid"])
            self.assertIn("LEGACY_TACTICAL_CHANGE_CONTRACT_REVOKED",result["errors"])
    def test_gm_outer_proposal_binds_native_plan(self):
        from fixtures import project,proposal
        from gm_core.decisions import validate_proposal
        with tempfile.TemporaryDirectory() as directory:
            data=project(directory)
            outer=proposal(data)
            _,snapshot,_=fixture()
            snapshot.update(career_id=data.source.career_id,source_batch_id=data.source.batch_id)
            snapshot["teams"][0]["abbreviation"]="T20"
            native=propose(snapshot,20,{"POEOffense":2},outer["decision_id"],outer["version"],"A01","测试方案")
            outer.update(operation="TACTIC_CHANGE",teams=["T20"],coaching_plan=native,coaching_snapshot=snapshot)
            result=validate_proposal(outer,data)
            self.assertTrue(result["valid"],result)
            self.assertFalse(result["execution_authorized"])
            outer["coaching_plan"]["version"]+=1
            self.assertIn("COACHING_PLAN_CONTEXT_MISMATCH",validate_proposal(outer,data)["errors"])
    def test_defense_onball_and_hedge_are_separate(self):
        raw=bytes([0b10101000,0b00101101,0,0,0,0,0,0])
        onball={"offset":0,"size":4,"format":(8<<16)|(3<<8)}
        hedge={"offset":0,"size":4,"format":(11<<16)|(3<<8)}
        self.assertEqual(decode_native(raw,onball),5)
        self.assertEqual(decode_native(raw,hedge),5)
        changed=bytearray(raw)
        changed[1]^=1
        self.assertNotEqual(decode_native(changed,onball),decode_native(raw,onball))
        self.assertEqual(decode_native(changed,hedge),decode_native(raw,hedge))

if __name__=="__main__":unittest.main()
