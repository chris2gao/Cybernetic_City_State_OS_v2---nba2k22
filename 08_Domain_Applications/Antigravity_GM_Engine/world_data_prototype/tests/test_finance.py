"""Finance primitive boundaries, source consistency, history and query provenance."""
import copy,json,struct,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from finance_reader import PROFILE,STRIDE,CORE_IDS,decode_finance,finance_projection_ranges,collect_finance,finance_payload,verify_finance_metadata,validate_name_dimension
from game_mode_reader import decode_game_mode
from engine import create_database,connect,ingest_capture
from query import native_team_finance,team_card
from observation_scope import query_at


def raw_team(tid=0,signed=-1):
    raw=bytearray(STRIDE)
    for name,spec in PROFILE['identity'].items():
        f=spec['binding'];off=f['offset']
        if name=='Id':struct.pack_into('<H',raw,off,tid)
        else:
            text={'UnlocalizedTeamName':'Test Team','UnlocalizedCityName':'City','UnlocalizedShortTeamName':'TST'}[name].encode('utf-16le');raw[off:off+len(text)]=text
    for spec in PROFILE['scalars'].values():
        off=spec['binding']['offset'];kind=spec['primitive'];struct.pack_into('<f' if kind=='float' else '<i' if kind=='int' else '<I',raw,off,1.25 if kind=='float' else signed if kind=='int' else 4294967295)
    return raw


def mode():
    import test_game_mode
    raw=test_game_mode.prefix(29)
    return {'season_year':2022,'observation':decode_game_mode(raw)},{'game-mode-public-prefix.bin':raw}


class FinanceMemory:
    module_base=0x140000000
    def __init__(self,changed=None):
        self.root=0x200000;self.base=0x400000;self.rows=[raw_team(i) for i in range(32)];self.calls=[];self.changed=changed
        if changed=='duplicate':self.rows[1]=raw_team(0)
        if changed=='missing':self.rows[0]=raw_team(60000)
    def read(self,address,size,label):
        from live_reader import ROSTER_RVA
        self.calls.append((address,size,label))
        if address==self.module_base+ROSTER_RVA:return struct.pack('<Q',self.root)
        if address==self.root+128:return struct.pack('<QQ',32,self.base)
        index,offset=divmod(address-self.base,STRIDE);raw=bytes(self.rows[index][offset:offset+size]);assert len(raw)==size
        if self.changed=='projection' and 'PROJECTION' in label and 'RECHECK' in label:return bytes(size)
        return raw


class FinanceTests(unittest.TestCase):
    def collect(self,memory):
        with patch('finance_reader.collect_game_mode',side_effect=lambda reader:mode()),patch('finance_reader.verify_finance_metadata',return_value=[]):return collect_finance(memory)
    def payload(self,token='one',stamp='2026-10-25T00:00:00Z',signed=-1):
        m,_=self.collect(FinanceMemory());m['teams']=m['teams'][:1];m['teams'][0]['finance']=decode_finance(raw_team(signed=signed))
        return finance_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},m,[{'sha256':'a'*64,'payload_kind':'SYNTHETIC_FINANCE'}],stamp,token)
    def test_signed_and_unsigned_boundaries_remain_distinct(self):
        for value in (-2147483648,-1,0,2147483647):
            decoded=decode_finance(raw_team(signed=value));self.assertEqual(decoded['bank_balance_raw'],value);self.assertEqual(decoded['exp_payroll_raw'],value);self.assertEqual(decoded['salary_raw'],4294967295)
        with self.assertRaises(ValueError):decode_finance(bytes(100))
    def test_finite_nonfinite_float_word_preservation(self):
        spec=PROFILE['scalars']['TicketPrice'];off=spec['binding']['offset']
        for word in (0x7fc12345,0x7f800000,0xff800000,0x80000000):
            raw=raw_team();struct.pack_into('<I',raw,off,word);d=decode_finance(raw);self.assertEqual(d['ticket_price_word_u32'],word)
            if word!=0x80000000:self.assertIsNone(d['ticket_price_real'])
            else:self.assertEqual(d['ticket_price_real'],0)
    def test_packed_neighbors_and_unregistered_enums(self):
        raw=raw_team();struct.pack_into('<I',raw,4148,1<<30|12345);struct.pack_into('<I',raw,4160,3<<30|7<<27|5<<24|0xabcdef);d=decode_finance(raw)
        self.assertEqual(d['is_luxury_tax_team_raw'],1);self.assertEqual(d['facility_luxury_suites_label'],'LEVEL_5');self.assertEqual(d['facility_parking_raw'],7);self.assertIsNone(d['facility_parking_label']);self.assertIsNone(d['budget_tier_label']);self.assertNotIn('historic_lottery_picks',d)
    def test_projection_is_small_named_TEAM_source_and_rechecked(self):
        memory=FinanceMemory();m,blobs=self.collect(memory);ranges=finance_projection_ranges();self.assertEqual(len(m['teams']),30);self.assertLess(sum(b-a for a,b in ranges),300);self.assertEqual(m['player_struct_reads'],0);self.assertEqual(len(blobs),31)
        self.assertTrue(any(a==692 and b==792 for a,b in ranges));self.assertFalse(any(a<3992 and 3984<b for a,b in ranges));self.assertTrue(all(size<=300 for _,size,_ in memory.calls))
        self.assertEqual(sum('PROJECTION' in label and 'RECHECK' not in label for _,_,label in memory.calls),sum('PROJECTION' in label and 'RECHECK' in label for _,_,label in memory.calls))
    def test_source_change_duplicate_and_missing_teams_fail_closed(self):
        for change in ('projection','duplicate','missing'):
            with self.subTest(change=change),self.assertRaises(ValueError):self.collect(FinanceMemory(change))
        before=mode();after=copy.deepcopy(before);after[0]['season_year']=2023
        with patch('finance_reader.collect_game_mode',side_effect=[before,after]),patch('finance_reader.verify_finance_metadata',return_value=[]),self.assertRaisesRegex(ValueError,'context changed'):collect_finance(FinanceMemory())
    def test_primitive_binding_change_is_not_hidden_by_same_format(self):
        fields=[copy.deepcopy(s['binding']) for s in (PROFILE['scalars']|PROFILE['packed']|PROFILE['identity']).values()];fields[0]['words'][1]^=1
        with patch('finance_reader.read_native_fields',return_value={'fields':fields}),self.assertRaisesRegex(ValueError,'primitive changed'):verify_finance_metadata(FinanceMemory())
    def test_runtime_initialized_dimension_words_do_not_replace_extent_validation(self):
        spec=PROFILE['identity']['UnlocalizedTeamName'];field=copy.deepcopy(spec['binding']);raw=bytearray.fromhex(spec['dimension_control_hex']);struct.pack_into('<I',raw,8,2);validate_name_dimension(field,spec,raw)
        struct.pack_into('<I',raw,0,24)
        with self.assertRaisesRegex(ValueError,'dimensions changed'):validate_name_dimension(field,spec,raw)
        struct.pack_into('<I',raw,0,25);field['words'][5]=1
        with self.assertRaisesRegex(ValueError,'dimensions changed'):validate_name_dimension(field,spec,raw)
    def test_typed_ingest_history_cutoff_and_same_unit_mode(self):
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture');one=self.payload();two=self.payload('two','2026-10-26T00:00:00Z',-500)
            with connect(db) as c:ingest_capture(c,one);ingest_capture(c,two)
            result=native_team_finance(db,team_id='team:native:0');self.assertEqual(result['records'][0]['bank_balance_raw'],-500);self.assertEqual(result['source']['source_grade'],'RESEARCH_FIXTURE');self.assertEqual(result['game_mode']['unit_id'],result['source']['unit_id']);self.assertEqual(result['records'][0]['observation_season_id'],'season:native-year:2022')
            old=query_at(db,'2026-10-25T12:00:00Z','native_team_finance',team_id='team:native:0');self.assertEqual(old['result']['records'][0]['bank_balance_raw'],-1)
            self.assertEqual(native_team_finance(db,unit_id='native-finance:one')['records'][0]['bank_balance_raw'],-1);self.assertEqual(native_team_finance(db,unit_id='missing')['status'],'NOT_OBSERVED');self.assertIn('ExpPayroll',team_card(db,'team:native:0')['legacy_finance_qualification'])
            with connect(db) as c:
                with self.assertRaisesRegex(Exception,'immutable history'):c.execute('UPDATE native_team_finance_observations SET bank_balance_raw=0')
                self.assertEqual(c.execute('SELECT count(*) FROM team_finance_observations').fetchone()[0],0)
    def test_float_nonfinite_survives_SQLite_and_json_without_NaN(self):
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture');p=self.payload();row=p['facts']['native_team_finance_observations'][0];row['buzz_word_u32']=0x7fc12345;row['buzz_real']=None
            with connect(db) as c:ingest_capture(c,p)
            r=native_team_finance(db);self.assertIsNone(r['records'][0]['buzz_real']);self.assertEqual(r['records'][0]['buzz_word_u32'],0x7fc12345);json.dumps(r,allow_nan=False)


if __name__=='__main__':unittest.main()
