"""Complete Native lineup shapes, explicit references, source units and cutoffs."""
import copy,json,struct,sys,unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from lineup_reader import PROFILE,CORE_IDS,LINEUP_KINDS,collect_lineups,lineup_payload,decode_team_lineups,resolve_lineup_pointer,lineup_player_ranges,team_lineup_ranges,verify_lineup_metadata
from player_detail_reader import reconstruct_projection
from game_mode_reader import decode_game_mode
from live_world import RESTRICTED_PLAYER_RANGES
from engine import create_database,connect,ingest_capture
from query import team_lineups,native_player_rotation
from observation_scope import query_at

def put(raw,f,value):
    off,size,start,width=(f[k] for k in ('offset','size','start_bit','width'));word=int.from_bytes(raw[off:off+size],'little');mask=((1<<width)-1)<<start;raw[off:off+size]=((word&~mask)|(value<<start)).to_bytes(size,'little')

def mode():
    import test_game_mode
    raw=test_game_mode.prefix(29);return {'season_year':2022,'observation':decode_game_mode(raw)},{'game-mode-public-prefix.bin':raw}

class LineupMemory:
    module_base=0x140000000
    def __init__(self,changed=None):
        self.root=0x200000;self.player_base=0x400000;self.team_base=0x800000;self.changed=changed;self.calls=[];self.teams={};self.rows=[]
        self.players=[{'source_player_index':i,'native_unique_id_raw':100+i,'preserved_id_raw':10+i,'observed_name':name,'name_status':'OBSERVED_UTF16_PREFIX','native_team_id':0,'current_core_roster_status':'CURRENT_CORE_ROSTER' if i==0 else 'NOT_CURRENT_CORE_ROSTER','current_roster_slot':0 if i==0 else None} for i,name in enumerate(('Alice','Bob'))]
        for i,p in enumerate(self.players):
            raw=bytearray(1264);raw[40:40+len(p['observed_name'])*2]=p['observed_name'].encode('utf-16le');struct.pack_into('<Q',raw,96,self.team_base);struct.pack_into('<H',raw,244,100+i);struct.pack_into('<I',raw,760,10+i);put(raw,PROFILE['player_fields']['PlayingTime'],127 if i==0 else 0);put(raw,PROFILE['player_fields']['ForceNonStarter'],2 if i==0 else 3);self.rows.append(bytes(raw))
        for index,tid in enumerate(sorted(CORE_IDS)):
            raw=bytearray(4696);put(raw,PROFILE['team_identity']['Id']['binding'],tid)
            for name,text in (('UnlocalizedTeamName','Test Team'),('UnlocalizedCityName','City'),('UnlocalizedShortTeamName','TST')):
                off=PROFILE['team_identity'][name]['binding']['offset'];encoded=text.encode('utf-16le');raw[off:off+len(encoded)]=encoded
            for name in ('LineupPlayer',)+LINEUP_KINDS:
                spec=PROFILE['arrays'][name]
                for slot,pointer in enumerate((self.player_base,self.player_base+1264,0,self.player_base+1,0x90000000)):struct.pack_into('<Q',raw,spec['binding']['offset']+slot*8,pointer)
            spec=PROFILE['arrays']['AdvancedRotationPlayerId'];struct.pack_into('<H',raw,spec['binding']['offset']+47*10+4*2,65535)
            self.teams[self.team_base+index*4696]=(tid,bytes(raw))
    def pool(self,reader,*,ranges,metadata):
        blobs={'player-detail-public-projections.bin':b''.join(b''.join(raw[a:b] for a,b in ranges) for raw in self.rows)}
        for _,(tid,_) in self.teams.items():blobs[f'team-{tid}.roster.bin']=struct.pack('<25Q',self.player_base,*([0]*24))
        return {'season_year':2022,'players':copy.deepcopy(self.players),'descriptors':{1:{'count':2,'address':self.player_base,'stride':1264},8:{'count':30,'address':self.team_base,'stride':4696}},'core_team_pointer_map':{a:t for a,(t,_) in self.teams.items()},'projection_stride':sum(b-a for a,b in ranges),'projection_ranges':ranges,'game_writes':False,'restricted_player_bytes_read':0,'metadata':metadata},blobs
    def read(self,address,size,label):
        from live_reader import ROSTER_RVA
        self.calls.append((address,size,label))
        if address==self.module_base+ROSTER_RVA:return struct.pack('<Q',self.root+16 if self.changed=='root' and 'FINAL' in label else self.root)
        if address==self.root+16:return struct.pack('<QQ',2,self.player_base)
        if address==self.root+128:return struct.pack('<QQ',30,self.team_base)
        if label.startswith('LINEUP_PLAYER_FINAL_RECHECK:'):
            index,offset=divmod(address-self.player_base,1264);value=self.rows[index][offset:offset+size];return bytes(size) if self.changed=='player' else value
        index,offset=divmod(address-self.team_base,4696);tid,raw=self.teams[self.team_base+index*4696]
        if label.startswith('LINEUP_ROSTER_RECHECK:'):return struct.pack('<25Q',self.player_base,*([0]*24))
        value=raw[offset:offset+size];return bytes(size) if self.changed=='team' and label.startswith('LINEUP_TEAM_RECHECK:') else value

class LineupTests(unittest.TestCase):
    def collect(self,memory=None):
        memory=memory or LineupMemory()
        with patch('lineup_reader.collect_game_mode',side_effect=lambda reader:mode()),patch('lineup_reader.verify_lineup_metadata',return_value=[]),patch('lineup_reader.collect_public_player_pool',side_effect=memory.pool):return collect_lineups(memory)
    def payload(self,token='one',stamp='2026-10-25T00:00:00Z'):
        m,_=self.collect();p=lineup_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m,[{'sha256':'a'*64,'payload_kind':'SYNTHETIC_LINEUP'}],stamp,token,{'player:native:10':'Alice'});p['facts']['players']=[{'player_id':'player:native:10','display_name':'Alice'}];return p
    def database(self,tmp,p=None):
        db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
        with connect(db) as c:ingest_capture(c,p or self.payload())
        return db
    def test_projection_excludes_private_bytes_and_decodes_unsigned_boundaries(self):
        ranges=lineup_player_ranges();self.assertEqual(sum(b-a for a,b in ranges),102);self.assertFalse(any(a<hi and lo<b for a,b in ranges for lo,hi in RESTRICTED_PLAYER_RANGES));m,_=self.collect();self.assertEqual(m['player_rotation_rows'][0]['playing_time_raw'],127);self.assertEqual(m['player_rotation_rows'][0]['force_non_starter_label'],'TRUE_FOREVER');self.assertIsNone(m['player_rotation_rows'][1]['force_non_starter_label']);self.assertEqual(m['player_rotation_rows'][1]['force_non_starter_raw'],3)
    def test_pointer_states_do_not_force_foreign_or_stale_references_to_owner(self):
        memory=LineupMemory();desc={'address':memory.player_base,'count':2}
        self.assertEqual(resolve_lineup_pointer(0,desc,memory.players,0)['pointer_status'],'NULL_POINTER');self.assertEqual(resolve_lineup_pointer(memory.player_base+1,desc,memory.players,0)['pointer_status'],'MISALIGNED_PLAYER_POINTER');self.assertEqual(resolve_lineup_pointer(memory.player_base+1264*2,desc,memory.players,0)['pointer_status'],'OUTSIDE_CURRENT_PLAYER_POOL');r=resolve_lineup_pointer(memory.player_base,desc,memory.players,1);self.assertEqual(r['source_player_index'],0);self.assertIn('WITHOUT_OWNER',r['pointer_status'])
    def test_complete_arrays_include_disabled_zero_and_sentinel_slots(self):
        m,_=self.collect();t=m['teams'][0];self.assertEqual(t['settings']['has_advanced_rotation_raw'],0);self.assertEqual(len(t['lineup_player_slots']),13);self.assertEqual(set(t['named_lineups']),set(LINEUP_KINDS));self.assertTrue(all(len(rows)==5 for rows in t['named_lineups'].values()));self.assertEqual(len(t['advanced_slots']),240);self.assertEqual(t['advanced_slots'][-1],{'axis0_index':47,'axis1_index':4,'native_player_id_raw':65535,'namespace_status':'UNVERIFIED_NATIVE_PLAYER_ID_NAMESPACE'});self.assertEqual(sum(r['native_player_id_raw']==0 for r in t['advanced_slots']),239)
    def test_source_rechecks_reject_subject_team_root_and_mode_changes(self):
        for changed in ('player','team','root'):
            with self.subTest(changed=changed),self.assertRaises(ValueError):self.collect(LineupMemory(changed))
        memory=LineupMemory();a=mode();b=copy.deepcopy(a);b[0]['season_year']=2023
        with patch('lineup_reader.collect_game_mode',side_effect=[a,b]),patch('lineup_reader.verify_lineup_metadata',return_value=[]),patch('lineup_reader.collect_public_player_pool',side_effect=memory.pool),self.assertRaisesRegex(ValueError,'context changed'):collect_lineups(memory)
    def test_changed_native_array_extent_is_rejected(self):
        fields=[s['binding'] for s in PROFILE['arrays'].values()]+list(PROFILE['team_flags'].values())+list(PROFILE['team_counts'].values())+[s['binding'] for s in PROFILE['team_identity'].values()]
        class MetadataMemory:
            module_base=0x140000000
            def read(self,address,size,label):return struct.pack('<QQQ',14,8,0)
        with patch('lineup_reader.read_native_fields',return_value={'fields':fields}),self.assertRaisesRegex(ValueError,'extent/stride changed'):verify_lineup_metadata(MetadataMemory())
    def test_incomplete_global_named_and_matrix_sources_fail_before_ingest(self):
        for family in ('lineup_player_slots','named_lineups','advanced_slots'):
            m,_=self.collect()
            if family=='named_lineups':m['teams'][0][family]['Starter'].pop()
            else:m['teams'][0][family].pop()
            with self.subTest(family=family),self.assertRaises(ValueError):lineup_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m,[],'2026-10-25T00:00:00Z','bad')
    def test_query_keeps_one_unit_actual_pointer_status_and_qualified_minutes(self):
        with TemporaryDirectory() as tmp:
            db=self.database(tmp);r=team_lineups(db,'team:native:0',include_advanced=True);self.assertEqual(r['source']['unit_id'],r['game_mode']['unit_id']);self.assertEqual(r['source']['source_grade'],'RESEARCH_FIXTURE');self.assertEqual(len(r['global_slots']),13);self.assertEqual(r['global_slots'][0]['observed_name'],'Alice');self.assertEqual(r['global_slots'][0]['playing_time_raw'],127);self.assertIsNone(r['global_slots'][0]['planned_minutes']);self.assertIsNone(r['global_slots'][0]['role_code']);self.assertEqual(r['global_slots'][1]['observed_name'],'Bob');self.assertIsNone(r['global_slots'][1]['player_id']);self.assertEqual(r['global_slots'][2]['pointer_status'],'NULL_POINTER');self.assertEqual(len(r['advanced']['slots']),240);self.assertNotIn('player_id',r['advanced']['slots'][0]);self.assertFalse(team_lineups(db,'team:native:0')['advanced']['included'])
    def test_player_rotation_pages_require_unit_and_keep_source_only_subjects(self):
        with TemporaryDirectory() as tmp:
            db=self.database(tmp);self.assertEqual(len(native_player_rotation(db)['records']),1);r=native_player_rotation(db,current_roster_only=False,limit=1);self.assertTrue(r['has_more']);second=native_player_rotation(db,current_roster_only=False,limit=1,unit_id=r['source']['unit_id'],after_index=r['next_after_index']);self.assertEqual(second['records'][0]['observed_name'],'Bob');self.assertIsNone(second['records'][0]['player_id']);self.assertIsNone(second['records'][0]['force_non_starter_label'])
            with self.assertRaises(ValueError):native_player_rotation(db,after_index=0)
    def test_historical_cutoffs_and_cli_do_not_borrow_later_sources(self):
        with TemporaryDirectory() as tmp:
            db=self.database(tmp);p=self.payload('two','2026-10-26T00:00:00Z')
            with connect(db) as c:ingest_capture(c,p)
            old=query_at(db,'2026-10-25T12:00:00Z','team_lineups','team:native:0');self.assertEqual(old['result']['source']['unit_id'],'native-lineups:one');self.assertEqual(query_at(db,'2026-10-25T12:00:00Z','team_lineups','team:native:0',unit_id='native-lineups:two')['result']['status'],'NOT_OBSERVED')
            from cli import main
            output=StringIO()
            with patch.object(sys,'argv',['cli','lineups',str(db),'team:native:0','--as-of','2026-10-24T00:00:00Z']),redirect_stdout(output):main()
            self.assertEqual(json.loads(output.getvalue())['result']['status'],'NOT_OBSERVED')
    def test_cross_unit_links_invented_minutes_and_history_updates_reject(self):
        for mutation,signature in (('unit','rotation subject'),('minutes','invents minutes/role')):
            with TemporaryDirectory() as tmp:
                db=self.database(tmp);p=self.payload('two','2026-10-26T00:00:00Z')
                if mutation=='unit':p['facts']['team_lineup_slots'][0]['source_player_id']='native-lineups:one:player:0'
                else:p['facts']['team_rotation_slots'][0]['planned_minutes']=127
                with connect(db) as c:
                    with self.assertRaisesRegex(Exception,signature):ingest_capture(c,p)
                with connect(db) as c:self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)
        with TemporaryDirectory() as tmp:
            db=self.database(tmp)
            with connect(db) as c:
                with self.assertRaisesRegex(Exception,'immutable history'):c.execute('UPDATE team_advanced_rotation_slots SET native_player_id_raw=0')

if __name__=='__main__':unittest.main()
