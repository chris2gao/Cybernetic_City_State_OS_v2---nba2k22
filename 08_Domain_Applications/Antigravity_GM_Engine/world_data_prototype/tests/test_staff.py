"""Complete public staff pool, exact role/status fields, references and history."""
import copy,json,struct,sys,unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from staff_reader import PROFILE,CORE_IDS,staff_projection_ranges,decode_staff_fields,classify_staff_assignments,collect_staff,staff_payload,resolve_pool_pointer,verify_staff_metadata
from game_mode_reader import decode_game_mode
from engine import create_database,connect,ingest_capture
from query import native_staff,staff_team_slots,staff_card
from observation_scope import query_at

def put(raw,f,value):
    off,start,width=f['offset'],f['start_bit'],f['width'];size=(start+width+7)//8;word=int.from_bytes(raw[off:off+size],'little');mask=((1<<width)-1)<<start;raw[off:off+size]=((word&~mask)|(value<<start)).to_bytes(size,'little')

def mode():
    import test_game_mode
    raw=test_game_mode.prefix(29);return {'season_year':2022,'observation':decode_game_mode(raw)},{'game-mode-public-prefix.bin':raw}

class StaffMemory:
    module_base=0x140000000
    def __init__(self,changed=None,duplicate=False,empty=False):
        self.root=0x200000;self.team_base=0x400000;self.staff_base=0x800000;self.changed=changed;self.calls=[];self.teams=sorted(CORE_IDS)+[99];self.rows=[]
        names=[] if empty else ['Alice','Bob','']+(['Dave'] if duplicate else [])
        for index,name in enumerate(names):
            raw=bytearray(352);raw[136:216]=b'\xa5'*80;raw[260:265]=b'\xed'*5
            encoded=name.encode('utf-16le');raw[48:48+len(encoded)]=encoded;struct.pack_into('<Q',raw,24,self.team_base if index==0 else self.team_base+30*4696 if index==2 else 0);put(raw,PROFILE['identity']['UniqueId'],100 if index in (0,3) else 200 if index==1 else 65535);put(raw,PROFILE['identity']['PersonType'],0 if index==0 else 15);put(raw,PROFILE['identity']['Status'],0 if index==0 else 1 if index==1 else 3)
            for name,value in (('Wage',16777215),('SoundId',2047),('YearsOfAcquiredStaff',63),('CoachOffense',15)):
                put(raw,PROFILE['fields'][name]['binding'],value)
            self.rows.append(bytes(raw))
    def read(self,address,size,label):
        from live_reader import ROSTER_RVA
        self.calls.append((address,size,label))
        if address==self.module_base+ROSTER_RVA:return struct.pack('<Q',self.root+16 if self.changed=='root' and label.endswith(':RECHECK') else self.root)
        if address==self.root+128:return struct.pack('<QQ',31,self.team_base)
        if address==self.root+19*16:return struct.pack('<QQ',len(self.rows),self.staff_base if self.rows else 0)
        if label.startswith('STAFF_PUBLIC_PROJECTION:'):
            index,off=divmod(address-self.staff_base,352);value=self.rows[index][off:off+size];return bytes(size) if self.changed=='staff' and label.endswith(':RECHECK') else value
        index,off=divmod(address-self.team_base,4696);tid=self.teams[index]
        if off==3240:return struct.pack('<H',tid)
        if off in (692,742):
            value=('Test Team' if off==692 else 'City').encode('utf-16le');return value+bytes(size-len(value))
        if off==3304:
            target=self.staff_base if tid==0 and self.rows else 0;value=struct.pack('<8Q',target,*([0]*7));return bytes(size) if self.changed=='role' and label.endswith(':RECHECK') else value
        raise AssertionError('unexpected staff source read')

class StaffTests(unittest.TestCase):
    def collect(self,memory=None):
        memory=memory or StaffMemory()
        with patch('staff_reader.collect_game_mode',side_effect=lambda reader:mode()),patch('staff_reader.verify_staff_metadata',return_value=[]):return collect_staff(memory)
    def payload(self,token='one',stamp='2026-10-25T00:00:00Z',memory=None):
        m,_=self.collect(memory);p=staff_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m,[{'sha256':'a'*64,'payload_kind':'SYNTHETIC_STAFF'}],stamp,token,{'staff:native:100':'Alice'});p['facts']['staff_members']=[{'staff_id':'staff:native:100','display_name':'Alice'}];return p
    def database(self,tmp,p=None):
        db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
        with connect(db) as c:ingest_capture(c,p or self.payload())
        return db
    def test_projection_physically_excludes_growth_and_annual_references(self):
        ranges=staff_projection_ranges();self.assertTrue(all(not (a<265 and 260<b) and not (a<216 and 136<b) for a,b in ranges));self.assertTrue(all(a>=24 for a,b in ranges));m,_=self.collect();self.assertEqual(m['player_value_reads'],0);self.assertEqual(m['staff_annual_stat_references_read'],0)
        for row in m['staff']:
            self.assertFalse(any('potential' in key.lower() for group in ('profile','tactics') for key in row[group]));self.assertNotIn('tight_lipped_raw',row['profile'])
    def test_signed_bitfield_and_unsigned_wage_and_unknown_grade(self):
        memory=StaffMemory();d=decode_staff_fields(memory.rows[0]);self.assertEqual(d['profile']['wage_raw'],16777215);self.assertEqual(d['profile']['sound_id_bits_raw'],2047);self.assertEqual(d['profile']['sound_id_signed'],-1);self.assertEqual(d['profile']['years_of_acquired_staff_bits_raw'],63);self.assertEqual(d['profile']['years_of_acquired_staff_signed'],-1);self.assertEqual(d['profile']['coach_offense_raw'],15)
        with self.assertRaises(ValueError):decode_staff_fields(bytes(100))
    def test_full_person_type_status_and_noncore_pointer_are_not_hiring_decisions(self):
        m,_=self.collect();self.assertEqual(m['staff'][1]['person_type_raw'],15);self.assertIsNone(m['staff'][1]['person_type_label']);self.assertEqual(m['staff'][1]['status_label'],'RELEASED');self.assertEqual(m['staff'][1]['assignment_status'],'NO_CORE_ROLE_REFERENCE');self.assertEqual(m['staff'][2]['current_team_native_id_raw'],99);self.assertEqual(m['staff'][2]['current_team_pointer_status'],'CURRENT_NONCORE_TEAM_POOL_POINTER');self.assertIsNone(m['staff'][2]['observed_name'])
        with TemporaryDirectory() as tmp:
            r=native_staff(self.database(tmp),current_core_only=False);self.assertEqual(len(r['records']),3);self.assertNotIn('hireable',r['records'][1])
    def test_duplicate_pool_id_withholds_alias_without_losing_role_or_source(self):
        p=self.payload(memory=StaffMemory(duplicate=True));r=p['facts']['native_staff_sources'][0];self.assertEqual(r['assignment_status'],'RECIPROCAL_CURRENT_TEAM_ROLE');self.assertIsNone(r['staff_id']);self.assertEqual(len(p['facts']['native_staff_sources']),4)
    def test_ambiguous_role_references_do_not_choose_an_owner(self):
        staff=[{'current_team_core_id':0,'person_type_raw':0}];slots=[{'source_staff_index':0,'native_team_id':0,'role_slot_index':0},{'source_staff_index':0,'native_team_id':1,'role_slot_index':0}];classify_staff_assignments(staff,slots);self.assertEqual(staff[0]['core_slot_reference_count'],2);self.assertIsNone(staff[0]['assigned_core_team_id']);self.assertIn('MULTIPLE',staff[0]['assignment_status'])
        self.assertEqual(resolve_pool_pointer(0,{'address':1000,'count':3},352),(None,'NULL_POINTER'));self.assertEqual(resolve_pool_pointer(1001,{'address':1000,'count':3},352),(None,'MISALIGNED_POOL_POINTER'))
    def test_subject_role_root_and_mode_changes_fail_closed(self):
        for changed in ('staff','role','root'):
            with self.subTest(changed=changed),self.assertRaises(ValueError):self.collect(StaffMemory(changed))
        memory=StaffMemory();a=mode();b=copy.deepcopy(a);b[0]['season_year']=2023
        with patch('staff_reader.collect_game_mode',side_effect=[a,b]),patch('staff_reader.verify_staff_metadata',return_value=[]),self.assertRaisesRegex(ValueError,'context changed'):collect_staff(memory)
    def test_primitive_binding_change_is_rejected_before_value_acquisition(self):
        fields=[copy.deepcopy(f) for f in PROFILE['identity'].values()]+[copy.deepcopy(s['binding']) for s in PROFILE['fields'].values()]+[copy.deepcopy(f) for f in PROFILE['excluded_staff_grade_fields'].values()];fields[0]['words'][1]^=1
        with patch('staff_reader.read_native_fields',return_value={'fields':fields}),self.assertRaisesRegex(ValueError,'primitive changed'):verify_staff_metadata(StaffMemory())
    def test_queries_page_one_source_and_include_details_only_when_requested(self):
        with TemporaryDirectory() as tmp:
            db=self.database(tmp);r=native_staff(db);self.assertEqual(len(r['records']),1);self.assertNotIn('profile',r['records'][0]);self.assertEqual(r['records'][0]['staff_id'],'staff:native:100');self.assertEqual(r['game_mode']['unit_id'],r['source']['unit_id']);r=native_staff(db,current_core_only=False,include_details=True,limit=1);self.assertEqual(r['records'][0]['profile']['wage_raw'],16777215);self.assertTrue(r['has_more']);next_page=native_staff(db,current_core_only=False,unit_id=r['source']['unit_id'],after_index=r['next_after_index'],limit=1);self.assertEqual(next_page['records'][0]['observed_name'],'Bob');self.assertIsNone(next_page['records'][0]['staff_id']);slots=staff_team_slots(db,'team:native:0');self.assertEqual(len(slots['records']),8);self.assertEqual(slots['records'][0]['observed_name'],'Alice');self.assertEqual(slots['records'][1]['pointer_status'],'NULL_POINTER');self.assertEqual(staff_card(db,'staff:native:100')['native_source']['records'][0]['profile']['wage_raw'],16777215)
            with self.assertRaises(ValueError):native_staff(db,after_index=0)
    def test_empty_descriptor_is_an_observed_source_with_all_team_slots(self):
        with TemporaryDirectory() as tmp:
            db=self.database(tmp,self.payload(memory=StaffMemory(empty=True)));r=native_staff(db,current_core_only=False);self.assertEqual(r['status'],'OBSERVED');self.assertEqual(r['source_staff_count'],0);self.assertEqual(r['records'],[]);self.assertEqual(len(staff_team_slots(db,'team:native:0')['records']),8)
    def test_historical_queries_and_cli_do_not_borrow_newer_units(self):
        with TemporaryDirectory() as tmp:
            db=self.database(tmp)
            with connect(db) as c:ingest_capture(c,self.payload('two','2026-10-26T00:00:00Z'))
            self.assertEqual(query_at(db,'2026-10-25T12:00:00Z','native_staff')['result']['source']['unit_id'],'native-staff:one');self.assertEqual(query_at(db,'2026-10-25T12:00:00Z','native_staff',unit_id='native-staff:two')['result']['status'],'NOT_OBSERVED')
            from cli import main
            output=StringIO()
            with patch.object(sys,'argv',['cli','native-staff',str(db),'--as-of','2026-10-24T00:00:00Z']),redirect_stdout(output):main()
            self.assertEqual(json.loads(output.getvalue())['result']['status'],'NOT_OBSERVED')
    def test_cross_unit_children_and_incomplete_families_rollback(self):
        with TemporaryDirectory() as tmp:
            db=self.database(tmp);p=self.payload('two','2026-10-26T00:00:00Z');p['facts']['native_staff_profile_observations'][0]['source_staff_id']='native-staff:one:staff:0'
            with connect(db) as c:
                with self.assertRaisesRegex(Exception,'cross-unit Native staff'):ingest_capture(c,p)
            with connect(db) as c:
                self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)
                with self.assertRaisesRegex(Exception,'immutable history'):c.execute('UPDATE native_staff_sources SET observed_name=NULL')
        m,_=self.collect();m['staff'][0]['profile'].pop('wage_raw')
        with self.assertRaisesRegex(ValueError,'incomplete Native staff profile'):staff_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m,[],'2026-10-25T00:00:00Z','bad')

if __name__=='__main__':unittest.main()
