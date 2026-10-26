"""F-01 isolated controlled-adapter data; zero real game/process access."""
from copy import deepcopy
import hashlib,json,sqlite3,struct,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
import test_review_live_conflicts as controlled
from engine import create_database,connect,ingest_acquired_capture,CaptureQuarantined
from cadence import ANNUAL_FAMILIES,attach_annual_period,annual_status
from annual_ledger import sha,honor_columns
from schema_model import NATIVE_PLAYER_STAT_MAP
from query import annual_facts
from annual_additions import load_request,capture_annual_additions,SelectedReads,collect_records_selected,collect_honors_selected,collect_staff_selected,collect_league_selected
from live_reader import ROSTER_RVA

def stat_row(index=1):
    return {'source_stat_index':index,'stat_year':2022,**{column:(122 if native=='CompactYear' else 0) for native,column in NATIVE_PLAYER_STAT_MAP.items()}}

def encode_fields(size,fields,values):
    raw=bytearray(size)
    for name,value in values.items():
        f=fields[name];old=int.from_bytes(raw[f['offset']:f['offset']+f['size']],'little');mask=((1<<f['width'])-1)<<f['start_bit'];word=(old&~mask)|(value<<f['start_bit']);raw[f['offset']:f['offset']+f['size']]=word.to_bytes(f['size'],'little')
    return bytes(raw)

class MemoryFixture:
    def __init__(self,pid=123):
        self.module_base=0x140000000;self.root=0x200000;self.parts={self.module_base+ROSTER_RVA:self.root.to_bytes(8,'little')};self.trace=[{'success':True,'operation':'CONTROLLED_FIXTURE_NOT_WINDOWS'}];self.closed=False
    def descriptor(self,slot,count,address,stride,raw=None):
        self.parts[self.root+slot*16]=struct.pack('<QQ',count,address)
        if raw is not None:self.parts[address]=raw
    def read(self,address,size,label):
        for start,raw in self.parts.items():
            if start<=address and address+size<=start+len(raw):
                self.trace.append({'operation':label,'address':address,'size':size,'success':True});return raw[address-start:address-start+size]
        raise AssertionError('untargeted fixture memory read: '+label+' '+hex(address)+' '+str(size))
    def close(self):self.closed=True

class ReviewAnnualAdditionsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.directory=Path(self.tmp.name);self.db=self.directory/'world.sqlite';create_database(self.db,'save');self.state=stat_row();self.family='NATIVE_HONOR_STATS'
        self.baseline=self.payload('baseline',self.family,{'native_player_stat_observations':[self.state]})
        with connect(self.db) as conn:ingest_acquired_capture(conn,self.baseline,_live_receipt=controlled.receipt(self.baseline))
        native=self.directory/'MyLEAGUE0003';native.write_bytes(b'CONTROLLED_FIXTURE_NOT_GAME_SAVE')
        (self.directory/'save.json').write_text(json.dumps({'save_id':'save','native_save_file':str(native),'native_save_filename':native.name,'identity_basis':'HUMAN_DECLARED_LOADED_SAVE_FILE','database_file':'world.sqlite'}),encoding='utf-8')
    def payload(self,unit,family,facts,addition=False):
        artifact=hashlib.sha256(('controlled-proof-'+unit).encode()).hexdigest()
        value={'save_id':'save','run_id':unit,'unit_id':unit,'source_key':ANNUAL_FAMILIES[family],'evidence_grade':'LIVE_READ','observed_at':'2026-10-26T00:00:00Z','decoder_version':'CONTROLLED_ADAPTER_TEST_ONLY','season':{'season_id':'season:native-year:2022','season_code':'NATIVE_YEAR:2022'},'facts':deepcopy(facts),'artifacts':[{'sha256':artifact,'payload_kind':'CONTROLLED_FIXTURE_NOT_NATIVE','payload_ref':'fixture/'+unit+'.json'}]}
        attach_annual_period(value,family,2022)
        if addition:value.update(refresh_kind='ADDITION',refresh_baseline_unit_id='baseline' if family==self.family else 'league-baseline',refresh_request_sha256=sha(['request',unit]),refresh_evidence_sha256=artifact,annual_addition_scope={'format':'TARGETED_NATIVE_ANNUAL_ADDITION_V1','requested_records':1,'untargeted_history_full_record_reads':0})
        return value
    def request(self,family=None,selectors=None):
        return {'format':'WORLD_ANNUAL_ADDITION_REQUEST_V1','save_id':'save','family':family or self.family,'period_year':2022,'baseline_unit_id':'baseline','reason':'NEW_FACT','evidence_ref':'CONTROLLED_STAGE_EVIDENCE_NOT_GAMEPLAY','selectors':selectors or {'indices':[1]}}
    def test_same_2022_baseline_then_regular_playoff_and_finals_honors(self):
        before=None
        with connect(self.db) as conn:
            before=dict(conn.execute("SELECT * FROM native_player_stat_observations WHERE unit_id='baseline'").fetchone())
            for unit,native in [('regular','MVP'),('playoff','Champion'),('finals','FinalsMVP')]:
                self.state[NATIVE_PLAYER_STAT_MAP[native]]=1;payload=self.payload(unit,self.family,{'native_player_stat_observations':[self.state]},True)
                self.assertEqual(ingest_acquired_capture(conn,payload,_live_receipt=controlled.receipt(payload)),'ingested')
                stored=dict(conn.execute('SELECT * FROM native_player_stat_observations WHERE unit_id=?',(unit,)).fetchone());self.assertEqual(stored[NATIVE_PLAYER_STAT_MAP[native]],1)
                for other in ('MVP','Champion','FinalsMVP'):
                    if other!=native:self.assertIsNone(stored[NATIVE_PLAYER_STAT_MAP[other]])
                self.assertIsNone(stored['points_raw'])
            self.assertEqual(dict(conn.execute("SELECT * FROM native_player_stat_observations WHERE unit_id='baseline'").fetchone()),before)
            self.assertEqual(annual_status(conn,self.family,2022)['previous_unit_id'],'baseline');self.assertEqual(conn.execute("SELECT count(*) FROM capture_runs WHERE refresh_kind='BASELINE'").fetchone()[0],1)
        page=annual_facts(self.db,self.family,2022);flags=[r for r in page['records'] if r['kind']=='NATIVE_HONOR_FLAG'];self.assertEqual(len(flags),3);self.assertEqual({r['field_name'] for r in flags},{NATIVE_PLAYER_STAT_MAP[n] for n in ('MVP','Champion','FinalsMVP')})
    def test_repeated_honor_request_does_not_implicitly_refresh_unrequested_counters(self):
        self.state[NATIVE_PLAYER_STAT_MAP['MVP']]=1;first=self.payload('first',self.family,{'native_player_stat_observations':[self.state]},True)
        with connect(self.db) as conn:
            ingest_acquired_capture(conn,first,_live_receipt=controlled.receipt(first));count=conn.execute('SELECT count(*) FROM capture_units').fetchone()[0]
            self.state['points_raw']=500;again=self.payload('different-request',self.family,{'native_player_stat_observations':[self.state]},True)
            self.assertEqual(ingest_acquired_capture(conn,again,_live_receipt=controlled.receipt(again)),'annual_addition_already_applied');self.assertEqual(conn.execute('SELECT count(*) FROM capture_units').fetchone()[0],count)
    def test_explicit_new_native_field_value_is_sparse_and_idempotent(self):
        row=stat_row();row['points_raw']=500;payload=self.payload('new-points',self.family,{'native_player_stat_observations':[row]},True);payload['annual_addition_scope']['field_selection']=['points_raw']
        with connect(self.db) as conn:
            self.assertEqual(ingest_acquired_capture(conn,payload,_live_receipt=controlled.receipt(payload)),'ingested');stored=conn.execute("SELECT * FROM native_player_stat_observations WHERE unit_id='new-points'").fetchone();self.assertEqual(stored['points_raw'],500);self.assertIsNone(stored['fg_made_raw'])
            repeat=self.payload('same-points',self.family,{'native_player_stat_observations':[row]},True);repeat['annual_addition_scope']['field_selection']=['points_raw'];self.assertEqual(ingest_acquired_capture(conn,repeat,_live_receipt=controlled.receipt(repeat)),'annual_addition_already_applied')
        values=[r for r in annual_facts(self.db,self.family,2022)['records'] if r['kind']=='NATIVE_FIELD_VALUE'];self.assertEqual([r['values'] for r in values],[{'points_raw':500}])
    def test_explicit_missing_zero_value_is_not_mistaken_for_no_fact(self):
        other=self.directory/'missing-zero.sqlite';create_database(other,'save');row=stat_row();row['mvp_raw']=None;baseline=self.payload('baseline',self.family,{'native_player_stat_observations':[row]})
        with connect(other) as conn:
            ingest_acquired_capture(conn,baseline,_live_receipt=controlled.receipt(baseline));row['mvp_raw']=0;addition=self.payload('observed-zero',self.family,{'native_player_stat_observations':[row]},True);addition['annual_addition_scope']['field_selection']=['mvp_raw'];self.assertEqual(ingest_acquired_capture(conn,addition,_live_receipt=controlled.receipt(addition)),'ingested')
        values=[r for r in annual_facts(other,self.family,2022)['records'] if r['kind']=='NATIVE_FIELD_VALUE'];self.assertEqual([r['values'] for r in values],[{'mvp_raw':0}])
    def test_second_full_baseline_still_blocked(self):
        payload=self.payload('second-baseline',self.family,{'native_player_stat_observations':[self.state]})
        with connect(self.db) as conn:
            with self.assertRaisesRegex(sqlite3.IntegrityError,'annual refresh already'):ingest_acquired_capture(conn,payload,_live_receipt=controlled.receipt(payload))
            self.assertEqual(conn.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)
    def test_honor_change_or_retraction_is_quarantined(self):
        self.state[NATIVE_PLAYER_STAT_MAP['MVP']]=1;first=self.payload('mvp',self.family,{'native_player_stat_observations':[self.state]},True)
        with connect(self.db) as conn:
            ingest_acquired_capture(conn,first,_live_receipt=controlled.receipt(first));self.state[NATIVE_PLAYER_STAT_MAP['MVP']]=0;changed=self.payload('retracted',self.family,{'native_player_stat_observations':[self.state]},True)
            with self.assertRaises(CaptureQuarantined):ingest_acquired_capture(conn,changed,_live_receipt=controlled.receipt(changed))
            self.assertEqual(conn.execute('SELECT count(*) FROM fact_conflicts').fetchone()[0],1);self.assertIsNone(conn.execute("SELECT 1 FROM native_player_stat_observations WHERE unit_id='retracted'").fetchone())
    def test_wrong_baseline_or_unrelated_family_rejected(self):
        payload=self.payload('wrong',self.family,{'native_player_stat_observations':[self.state]},True);payload['refresh_baseline_unit_id']='missing'
        with connect(self.db) as conn:
            with self.assertRaisesRegex(ValueError,'baseline'):ingest_acquired_capture(conn,payload,_live_receipt=controlled.receipt(payload))
            payload=self.payload('unrelated',self.family,{'player_attribute_snapshots':[{'player_id':'p','overall_raw':90}]},True)
            with self.assertRaisesRegex(ValueError,'unrelated'):ingest_acquired_capture(conn,payload,_live_receipt=controlled.receipt(payload))
    def test_proven_missing_source_row_is_appended_once(self):
        missing=stat_row(2);payload=self.payload('missing-row',self.family,{'native_player_stat_observations':[missing]},True)
        with connect(self.db) as conn:
            self.assertEqual(ingest_acquired_capture(conn,payload,_live_receipt=controlled.receipt(payload)),'ingested')
            repeat=self.payload('missing-repeat',self.family,{'native_player_stat_observations':[missing]},True)
            self.assertEqual(ingest_acquired_capture(conn,repeat,_live_receipt=controlled.receipt(repeat)),'annual_addition_already_applied');self.assertEqual(conn.execute('SELECT count(*) FROM native_player_stat_observations').fetchone()[0],2)
    def test_staff_new_honor_is_sparse_and_year_stays_unknown(self):
        import staff_history_reader
        fields=staff_history_reader.PROFILE['stat_fields'];row={'source_stat_index':1,'stat_year':None,'subject_reference_count':2,**{s['column']:0 for s in fields.values()}}
        baseline=self.payload('coach-baseline','STAFF_SEASON_HISTORY',{'native_coach_stat_observations':[row]})
        with connect(self.db) as conn:
            ingest_acquired_capture(conn,baseline,_live_receipt=controlled.receipt(baseline));changed=dict(row);column=fields['CoachWonTitle']['column'];changed[column]=1;payload=self.payload('coach-title','STAFF_SEASON_HISTORY',{'native_coach_stat_observations':[changed]},True);payload['refresh_baseline_unit_id']='coach-baseline'
            self.assertEqual(ingest_acquired_capture(conn,payload,_live_receipt=controlled.receipt(payload)),'ingested');stored=conn.execute("SELECT * FROM native_coach_stat_observations WHERE unit_id='coach-title'").fetchone();self.assertEqual(stored[column],1);self.assertIsNone(stored['stat_year']);self.assertIsNone(stored['next_free_raw']);self.assertIsNone(stored['coach_wins_raw'])
    def test_canonical_frozen_award_conflict_uses_same_receipt_quarantine(self):
        award={'award_id':'award:mvp:2022','season_id':'season:native-year:2022','award_code':'MVP','award_type':'CONTROLLED_FIXTURE','is_final':1,'source_year_raw':2022,'source_fingerprint':'a'*64}
        baseline=self.payload('league-baseline','LEAGUE_HISTORY_AWARDS',{'season_award_instances':[award]})
        with connect(self.db) as conn:
            ingest_acquired_capture(conn,baseline,_live_receipt=controlled.receipt(baseline));changed=dict(award,source_fingerprint='b'*64);proposal=self.payload('award-conflict','LEAGUE_HISTORY_AWARDS',{'season_award_instances':[changed]},True)
            with self.assertRaises(CaptureQuarantined):ingest_acquired_capture(conn,proposal,_live_receipt=controlled.receipt(proposal))
            self.assertEqual(conn.execute('SELECT source_fingerprint FROM season_award_instances').fetchone()[0],'a'*64)
    def test_request_validation_is_bounded_and_evidence_explicit(self):
        request=self.request();path=self.directory/'request.json';path.write_text(json.dumps(request),encoding='utf-8');self.assertEqual(load_request(path)[2],1)
        for change in ({'evidence_ref':''},{'reason':'REPEAT_FULL_SOURCE'},{'selectors':{'indices':list(range(129))}},{'selectors':{'indices':[True]}},{'selectors':{'indices':[1,1]}},{'fields':['potential_raw']}):
            value=request|change;path.write_text(json.dumps(value),encoding='utf-8')
            with self.subTest(change=change),self.assertRaises(ValueError):load_request(path)
    def test_honors_real_adapter_path_targeted_bytes_and_cached_replay(self):
        import award_reader
        profile=json.loads(award_reader.PROFILE_PATH.read_bytes());process=MemoryFixture();process.descriptor(1,4,0x900000,1264);raw=encode_fields(48,profile['stat_fields'],{'CompactYear':122,'MVP':1});process.descriptor(24,4,0x500000,48,bytes(48)+raw+bytes(96))
        metadata={'name':'PLAYERSTATDATA','fields':[dict(value) for value in profile['stat_fields'].values()]};request=self.request();path=self.directory/'request.json';path.write_text(json.dumps(request),encoding='utf-8');mode={'season_year':2022,'observation':{'period_raw':29}}
        class ReaderFactory(MemoryFixture):
            calls=0
            def __init__(self,pid):self.__dict__.update(process.__dict__);ReaderFactory.calls+=1
        with patch('annual_additions.ReadOnlyGameProcess',ReaderFactory),patch('live_world.ReadOnlyGameProcess',ReaderFactory),patch('process_session.resolve_pid',return_value=123),patch('annual_additions.collect_game_mode',return_value=(mode,{})),patch('award_reader.read_native_fields',return_value=metadata):
            result=award_reader.capture_native_honors(123,self.directory,'MyLEAGUE0003',self.directory/'addition',addition_request=path);self.assertEqual(result['status'],'ingested')
            self.assertEqual(result['read_cost']['targeted_history_record']['bytes'],48);self.assertEqual(result['read_cost']['targeted_history_record_recheck']['bytes'],48)
            again=capture_annual_additions(123,self.directory,'MyLEAGUE0003',self.directory/'replay',path);self.assertEqual(again['status'],'already_applied');self.assertFalse(again['fresh_native_capture']);self.assertEqual(ReaderFactory.calls,1)
        reads=[r for r in process.trace if r.get('operation','').startswith('honor-stat-')];self.assertEqual(len(reads),2);self.assertTrue(all(r['address']==0x500000+48 for r in reads))
    def test_other_three_collectors_read_only_selected_history(self):
        import records_reader,staff_history_reader,league_reader
        records=MemoryFixture();records.parts[records.module_base+records_reader.RECORD_GETTER_RVA]=records_reader.GETTER_CORE.ljust(64,b'\0');raw=bytearray(52);raw[:4]=b'Test';raw[40:44]=struct.pack('<f',10);records.descriptor(39,4,0x500000,52,bytes(52)+raw+bytes(104));session=SelectedReads(records)
        manifest,factory=collect_records_selected(session,self.request('RECORD_BOOK'),2022);session.recheck();self.assertEqual([r['source_row_index'] for r in manifest['record_rows']],[1]);self.assertEqual(session.cost['targeted_history_record']['bytes'],52);self.assertEqual(len(factory({'save_id':'save','native_save_filename':'MyLEAGUE0003'},manifest,[],'2026-10-26T00:00:00Z','record')['facts']['season_record_entries']),1)
        staff=MemoryFixture();directory=bytearray(704)
        for i in range(2):
            directory[i*352+48:i*352+48+8]='Test'.encode('utf-16le');directory[i*352+136:i*352+216]=struct.pack('<40h',1,*([-1]*39));directory[i*352+216:i*352+218]=(i+1).to_bytes(2,'little')
        staff.descriptor(19,2,0x600000,352,directory);stats=bytearray(48);stats[12:24]=encode_fields(12,{n:s['binding'] for n,s in staff_history_reader.PROFILE['stat_fields'].items()},{'CoachWonTitle':1});staff.descriptor(21,4,0x700000,12,stats);session=SelectedReads(staff)
        with patch('staff_history_reader.verify_metadata',return_value=[]):manifest,factory=collect_staff_selected(session,self.request('STAFF_SEASON_HISTORY'),2022)
        session.recheck();self.assertEqual(manifest['stats'][0]['subject_reference_count'],2);self.assertEqual(session.cost['targeted_history_record']['bytes'],12);self.assertEqual(session.cost['reference_directory']['bytes'],164)
        import test_staff as staff_fixture
        manifest['game_mode']=staff_fixture.mode()[0];self.assertEqual(len(factory({'save_id':'save','native_save_filename':'MyLEAGUE0003'},manifest,[],'2026-10-26T00:00:00Z','staff',{})['facts']['native_coach_stat_observations']),1)
        league=MemoryFixture();profile=json.loads(league_reader.PROFILE_PATH.read_bytes());franchise=0x800000;league.parts[league.module_base+league_reader.FRANCHISE_RVA]=franchise.to_bytes(8,'little');league.descriptor(41,4,0x900000,152);field=profile['bindings']['FRANCHISE']['SeasonAwardWinnerIndex'];league.parts[franchise+field['offset']]=(37).to_bytes(2,'little');session=SelectedReads(league)
        with patch('league_reader.verify_league_metadata',return_value=[]):manifest,factory=collect_league_selected(session,self.request('LEAGUE_HISTORY_AWARDS',{'history_indices':[],'matrix_slots':[[0,0]]}),2022)
        session.recheck();self.assertEqual(manifest['award_winner_matrix'][0]['native_player_index_raw'],37);self.assertNotIn('targeted_history_record',session.cost);self.assertEqual(session.cost['targeted_matrix_cell']['bytes'],2)
        payload=factory({'save_id':'save','native_save_filename':'MyLEAGUE0003'},manifest,[],'2026-10-26T00:00:00Z','league',{});self.assertEqual(len(payload['facts']['native_award_matrix_observations']),1);self.assertEqual(payload['facts']['season_award_instances'],[])
    def test_four_reader_entries_route_explicit_addition_requests(self):
        import records_reader,award_reader,staff_history_reader,league_ingest
        for fn,kwargs,family in [(records_reader.capture_records,{},'RECORD_BOOK'),(award_reader.capture_native_honors,{},self.family),(staff_history_reader.capture_staff_history,{},'STAFF_SEASON_HISTORY'),(league_ingest.capture_league,{'mode':'HISTORY_AWARDS'},'LEAGUE_HISTORY_AWARDS')]:
            with self.subTest(family=family),patch('annual_additions.capture_annual_additions',return_value={'routed':True}) as call:
                self.assertEqual(fn(123,'save','MyLEAGUE0003','out',addition_request='request.json',**kwargs),{'routed':True});self.assertEqual(call.call_args.kwargs['family'],family)

if __name__=='__main__':unittest.main()
