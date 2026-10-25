"""Native game-mode stages remain distinct from schedule periods and stat phases."""
import copy,json,struct,sys,unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from game_mode_reader import PROFILE,RAW_FIELDS,decode_game_mode,collect_game_mode,verify_game_mode_metadata,game_mode_payload,CALENDAR_PROFILE
from engine import create_database,connect,ingest_capture
from query import game_mode
from observation_scope import query_at

def prefix(period=29,previous=28):
    raw=bytearray(24);raw[:4]=bytes((30,30,0,1));struct.pack_into('<4I',raw,4,1,0,period,previous);struct.pack_into('<I',raw,20,(21<<25)|(10<<21)|(19<<16)|(1140<<5));return bytes(raw)

class ModeMemory:
    module_base=0x140000000;module_size=0x8000000
    def __init__(self,changed=False,wrong_getter=False,bad_code=False):self.changed=changed;self.wrong_getter=wrong_getter;self.bad_code=bad_code;self.calls=[]
    def read(self,address,size,label):
        self.calls.append((address,size,label))
        if label.startswith('GAME_MODE_CODE:'):
            raw=bytes.fromhex(next(p['code_hex'] for p in PROFILE['code_proofs'] if address==self.module_base+p['rva']));return b'\0'*size if self.bad_code else raw
        if label=='GAME_MODE_DATE_EPOCH_CODE':return bytes.fromhex(next(p['hex'] for p in CALENDAR_PROFILE['code_proofs'] if address==self.module_base+p['rva']))
        if address==self.module_base+PROFILE['game_mode_pointer_rva']:return struct.pack('<Q',0x10000000)
        if address==self.module_base+PROFILE['virtual_object_pointer_rva']:return struct.pack('<Q',0x10001000)
        if address==0x10001000:return struct.pack('<Q',self.module_base+0x3000)
        if address==self.module_base+0x3000+0x338:return struct.pack('<Q',self.module_base+PROFILE['verified_virtual_getter_rva']+int(self.wrong_getter))
        if address==0x10000000:return prefix(30 if self.changed and label.endswith(':RECHECK') else 29)
        raise AssertionError('unexpected fixture read')

class GameModeTests(unittest.TestCase):
    def payload(self,period=29,token='one',stamp='2026-10-25T00:00:00Z'):
        return game_mode_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},{'season_year':2022,'observation':decode_game_mode(prefix(period))},[{'sha256':'a'*64,'payload_kind':'SYNTHETIC_MODE_PREFIX'}],stamp,token)

    def test_all_31_periods_use_exact_shared_selector_without_unique_phase(self):
        labels=PROFILE['enum_labels']['GAMEMODE_TIMEPERIOD'];self.assertEqual({int(k) for k in labels},set(range(31)))
        special={2,24,26,28,30}
        for code in range(31):
            row=decode_game_mode(prefix(code));self.assertEqual(row['period_label'],labels[str(code)]['label']);self.assertEqual(row['current_stat_array_position'],24 if code in special else 0)
        self.assertEqual({labels[str(code)]['label'] for code in special},{'LOTTERY_TOURNAMENT','SUMMER_LEAGUE','HOOPS_SUMMIT','PRESEASON','PLAYOFFS'})

    def test_game_mode_and_season_period_two_have_distinct_names(self):
        self.assertEqual(decode_game_mode(prefix(2))['period_label'],'LOTTERY_TOURNAMENT');self.assertEqual(CALENDAR_PROFILE['enum_labels']['SEASON_TIMEPERIOD']['2']['label'],'REGULARSEASON')

    def test_unknown_codes_and_raw_year_bytes_are_not_generalized(self):
        raw=bytearray(prefix(0xffffffff));raw[2:4]=bytes((250,255));row=decode_game_mode(bytes(raw));self.assertIsNone(row['period_label']);self.assertEqual(row['current_stat_array_position'],0);self.assertIn('UNREGISTERED',row['stat_selector_status']);self.assertEqual(row['current_year_byte_raw'],250)
        for raw in (b'',bytes(23),bytes(25)):
            with self.assertRaises(ValueError):decode_game_mode(raw)

    def test_today_uses_verified_month_zero_epoch_and_keeps_invalid_raw_date(self):
        row=decode_game_mode(prefix());self.assertEqual(row['today_native_iso_date'],'2021-11-19');self.assertEqual(row['today_native_time_hhmm'],'19:00')
        raw=bytearray(prefix());raw[20:24]=bytes(4);row=decode_game_mode(bytes(raw));self.assertIsNone(row['today_native_iso_date']);self.assertEqual(row['today_word_raw'],0)

    def test_collect_rechecks_prefix_pointers_and_year_without_player_reads(self):
        reader=ModeMemory()
        with patch('game_mode_reader.verify_game_mode_metadata',return_value=[]),patch('game_mode_reader.observed_game_season_year',return_value=2022):manifest,blobs=collect_game_mode(reader)
        self.assertEqual(manifest['observation']['period_label'],'REGULARSEASON');self.assertEqual(blobs['game-mode-public-prefix.bin'],prefix());self.assertEqual(manifest['getter_invocations'],0);self.assertFalse(manifest['cumulative_phase_inferred']);self.assertTrue(all('PLAYER' not in c[2] for c in reader.calls))

    def test_changed_context_or_different_virtual_getter_rejects_source(self):
        with patch('game_mode_reader.verify_game_mode_metadata',return_value=[]),patch('game_mode_reader.observed_game_season_year',return_value=2022):
            for reader,text in ((ModeMemory(changed=True),'context changed'),(ModeMemory(wrong_getter=True),'virtual getter differs')):
                with self.subTest(text=text),self.assertRaisesRegex(ValueError,text):collect_game_mode(reader)

    def test_metadata_and_code_verifier_rejects_changed_code(self):
        def fields(reader,entry,*args,**kwargs):return {'name':entry['name'],'fields':list((PROFILE['bindings'] if entry['name']=='GAMEMODE' else CALENDAR_PROFILE['bindings']['SCHEDULEDATE']).values())}
        def enum(reader,entry):
            labels=(PROFILE if entry['name'] in PROFILE['enum_labels'] else CALENDAR_PROFILE)['enum_labels'][entry['name']]
            return {'name':entry['name'],'values':[{'value':int(k),'name_crc':v['name_crc']} for k,v in labels.items()]}
        with patch('game_mode_reader.read_native_fields',side_effect=fields),patch('game_mode_reader.read_native_enum',side_effect=enum):
            self.assertEqual(len(verify_game_mode_metadata(ModeMemory())),6)
            with self.assertRaisesRegex(ValueError,'code changed'):verify_game_mode_metadata(ModeMemory(bad_code=True))

    def test_typed_ingest_preserves_history_and_utc_latest_with_cutoffs(self):
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture');one=self.payload();two=self.payload(30,'two','2026-10-24T23:30:00-02:00')
            with connect(db) as c:self.assertEqual(ingest_capture(c,one),'ingested');self.assertEqual(ingest_capture(c,two),'ingested');self.assertEqual(ingest_capture(c,two),'already_applied')
            latest=game_mode(db)['records'][0];self.assertEqual(latest['period_label'],'PLAYOFFS');self.assertEqual(latest['current_stat_array_position'],24)
            old=query_at(db,'2026-10-25T00:30:00Z','game_mode')['result']['records'][0];self.assertEqual(old['period_label'],'REGULARSEASON');self.assertEqual(query_at(db,'2000-01-01T00:00:00Z','game_mode')['result']['records'],[])
            with connect(db,True) as c:self.assertEqual(c.execute('SELECT count(*) FROM game_mode_observations').fetchone()[0],2);self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_cli_and_caps_preserve_source_grade_and_historical_scope(self):
        import cli
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,self.payload())
            output=StringIO()
            with patch.object(sys,'argv',['cli','game-mode',str(db),'--as-of','2026-10-25T00:30:00Z']),redirect_stdout(output):cli.main()
            record=json.loads(output.getvalue())['result']['records'][0];self.assertEqual(record['source_grade'],'RESEARCH_FIXTURE')
            for cap in (0,True,1001):
                with self.assertRaises(ValueError):game_mode(db,limit=cap)

if __name__=='__main__':unittest.main()
