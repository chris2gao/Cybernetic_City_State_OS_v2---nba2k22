"""Exact Native date/layout semantics and query provenance; fixtures are synthetic."""
from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,struct,subprocess,sys,unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from calendar_codec import PROFILE,GAME_CAPACITY,STAT_CAPACITY,decode_date,game_calendar_fields,date_columns
from calendar_reader import verify_calendar_metadata,collect_calendar_controls
from schedule_reader import collect_schedule,schedule_facts
from test_schedule import ScheduleMemory
from engine import create_database,connect,ingest_capture
from query import schedule,league_calendar,game_box
from observation_scope import query_at

def word(year=2021,month=9,day=19,minutes=1170,ident=1):return ((year-2000)<<25)|(month<<21)|(day<<16)|(minutes<<5)|ident

class CalendarTests(unittest.TestCase):
    def test_native_month_zero_and_year_epoch_are_distinct_from_old_research_guess(self):
        value=decode_date(word().to_bytes(4,'little'));self.assertEqual(value['native_iso_date'],'2021-10-19');self.assertEqual(value['month_label'],'OCTOBER');self.assertEqual(value['native_time_hhmm'],'19:30');self.assertEqual(value['base_year_offset_raw'],21)
        self.assertEqual(decode_date(word(month=0,day=1,minutes=0).to_bytes(4,'little'))['native_iso_date'],'2021-01-01');self.assertEqual(PROFILE['year_epoch'],2000)
    def test_raw_zero_invalid_date_unknown_month_and_invalid_time_are_retained(self):
        for raw in (0,word(month=15),word(month=1,day=30)):
            value=decode_date(raw.to_bytes(4,'little'));self.assertEqual(value['word_raw'],raw);self.assertIsNone(value['native_iso_date'])
        self.assertEqual(decode_date(word(year=2000,month=1,day=29).to_bytes(4,'little'))['native_iso_date'],'2000-02-29')
        value=decode_date(word(minutes=1500).to_bytes(4,'little'));self.assertIsNone(value['native_time_hhmm']);self.assertEqual(value['minutes_since_midnight_raw'],1500)
    def test_game_period_type_status_and_force_winner_are_separate_native_enums(self):
        raw=bytearray(ScheduleMemory().game);raw[4:8]=bytes(4);struct.pack_into('<I',raw,56,(3<<6)|(1<<9)|(3<<11)|(2<<13))
        value=game_calendar_fields(raw);self.assertEqual((value['time_period_label'],value['game_type_label'],value['status_label'],value['force_winner_label']),('POSTSEASON','ALLSTAR','POSTPONED','DO_NOT_CARE'))
        self.assertIsNone(value['played_native_iso_date'])  # No substitution of scheduled date for absent played date.
    def test_postponed_schedule_header_never_reads_a_box_or_invents_a_score(self):
        reader=ScheduleMemory();raw=bytearray(reader.games);struct.pack_into('<I',raw,56,3<<11);reader.games=bytes(raw)
        found=collect_schedule(reader);self.assertEqual(found['boxes'],{});self.assertEqual(found['manifest']['status_counts'],{'3':1,'0':1})
        facts=schedule_facts(found,{'season_id':'s'},set());self.assertEqual(facts['game_source_checks'][0]['status_label'],'POSTPONED');self.assertEqual(facts['game_source_checks'][0]['box_mode'],'HEADER_ONLY_NOT_FINAL');self.assertEqual(facts['player_game_boxes'],[])
    def test_capacities_come_from_current_native_array_metadata(self):
        self.assertEqual((GAME_CAPACITY,STAT_CAPACITY),(1742,45292));self.assertEqual(PROFILE['array_dimensions']['SEASON_SCHEDULE']['Games'],[1742])
    def test_native_declared_count_mismatch_is_rejected(self):
        s=PROFILE['bindings']['SEASON'];g=PROFILE['bindings']['SEASON_SCHEDULE']
        class Reader:
            def read(self,address,size,label):
                if address==s['Schedule']['offset']+g['NumberOfGames']['offset']:return (2).to_bytes(4,'little')
                return bytes(size)
        with self.assertRaisesRegex(ValueError,'differs from actual Slot10'):collect_calendar_controls(Reader(),0,3)
    def test_epoch_code_and_array_extent_changes_are_rejected(self):
        entries={e['name']:e for e in PROFILE['types']};fields={name:{'fields':deepcopy(list(bindings.values()))} for name,bindings in PROFILE['bindings'].items()}
        enums={name:{'values':[{'value':int(code),'name_crc':value['name_crc']} for code,value in values.items()]} for name,values in PROFILE['enum_labels'].items()}
        data={}
        for type_name,bindings in PROFILE['array_dimensions'].items():
            for name,dimension in bindings.items():
                f=PROFILE['bindings'][type_name][name];w=f['words'];data[w[6]|w[7]<<32]=dimension[0].to_bytes(4,'little')+bytes(20)
        for p in PROFILE['code_proofs']:data[0x140000000+p['rva']]=bytes.fromhex(p['hex'])
        class Reader:
            module_base=0x140000000
            def read(self,address,size,label):return data[address]
        with patch('calendar_reader.read_native_fields',side_effect=lambda reader,entry,*args,**kwargs:fields[entry['name']]),patch('calendar_reader.read_native_enum',side_effect=lambda reader,entry:enums[entry['name']]):
            self.assertEqual(len(verify_calendar_metadata(Reader())),len(entries))
            pointer=0x140000000+PROFILE['code_proofs'][0]['rva'];data[pointer]=b'\0'*len(data[pointer])
            with self.assertRaisesRegex(ValueError,'epoch code changed'):verify_calendar_metadata(Reader())

class CalendarQueryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'save')
        self.put('old','2026-10-24T00:00:00Z',word(),0)
        self.put('new','2026-10-25T00:00:00Z',word(month=10,day=19),3)
    def put(self,unit,stamp,date_word,status):
        raw=bytearray(60);struct.pack_into('<I',raw,0,date_word);struct.pack_into('<I',raw,56,(2<<6)|(status<<11)|(2<<13));values=game_calendar_fields(raw)
        facts={'teams':[{'team_id':'a'},{'team_id':'b'}],'games':[{'game_id':'g','season_id':'s','home_team_id':'a','away_team_id':'b'}],
            'game_state_observations':[{'game_id':'g','status_code':str(status),'is_final':0}],
            'game_source_checks':[{'game_id':'g','header_sha256':str(status)*64,'box_mode':'HEADER_ONLY_NOT_FINAL','game_status_raw':status,'reuse_basis':'SYNTHETIC',**values}],
            'season_calendar_observations':[{'season_id':'s',**date_columns(date_word.to_bytes(4,'little'),'current_'),'period_raw':2,'period_label':'REGULARSEASON'}]}
        payload={'save_id':'save','run_id':unit,'unit_id':unit,'source_key':'SYNTHETIC_CALENDAR','observed_at':stamp,'evidence_grade':'SYNTHETIC_FIXTURE','season':{'season_id':'s','season_code':'native-year-label-not-calendar-year'},'facts':facts}
        with connect(self.db) as conn:ingest_capture(conn,payload)
    def test_current_calendar_and_historical_cutoff_keep_their_own_source_time(self):
        current=league_calendar(self.db)['records'][0];self.assertEqual(current['current_native_iso_date'],'2021-11-19');self.assertEqual(current['unit_id'],'new')
        old=query_at(self.db,'2026-10-24T00:00:00Z','league_calendar')['result']['records'][0];self.assertEqual(old['current_native_iso_date'],'2021-10-19');self.assertEqual(old['unit_id'],'old')
        self.assertEqual(query_at(self.db,'2000-01-01T00:00:00Z','league_calendar')['result']['records'],[])
    def test_schedule_filters_native_date_period_type_and_postponed_status(self):
        values=schedule(self.db,status_code='3',period_code=2,game_type_code=0,native_date_from='2021-11-01',native_date_to='2021-11-30');self.assertEqual(len(values),1)
        row=values[0];self.assertIsNone(row['game_date']);self.assertEqual(row['native_game_date'],'2021-11-19');self.assertEqual(row['calendar_unit_id'],'new');self.assertEqual(row['status_label'],'POSTPONED');self.assertIsNone(row['home_points_derived'])
        self.assertEqual(schedule(self.db,period_code=3),[]);self.assertEqual(schedule(self.db,native_date_to='2021-10-31'),[])
        old=query_at(self.db,'2026-10-24T00:00:00Z','schedule')['result'][0];self.assertEqual(old['calendar_unit_id'],'old');self.assertEqual(old['native_game_date'],'2021-10-19')
    def test_invalid_filters_and_caps_are_explicit(self):
        for kwargs in ({'status_code':'4'},{'period_code':True},{'game_type_code':4},{'native_date_from':'2021-2-3'},{'native_date_from':'2021-11-30','native_date_to':'2021-11-01'}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):schedule(self.db,**kwargs)
        with self.assertRaises(ValueError):league_calendar(self.db,limit=0)
    def test_cli_calendar_and_filtered_schedule_support_as_of(self):
        for args in (['calendar',str(self.db)],['schedule',str(self.db),'--period-code','2','--native-date-from','2021-10-01']):
            result=subprocess.run([sys.executable,str(BASE/'cli.py'),*args,'--as-of','2026-10-24T00:00:00Z'],capture_output=True,text=True,check=True);value=json.loads(result.stdout)['result'];self.assertTrue(value)

if __name__=='__main__':unittest.main()
