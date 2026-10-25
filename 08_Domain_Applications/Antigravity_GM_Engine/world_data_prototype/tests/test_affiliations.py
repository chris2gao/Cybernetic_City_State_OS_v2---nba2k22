"""Independent native classification and school/catalog referents, not eligibility."""
from copy import deepcopy
import sqlite3,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from engine import create_database,connect,ingest_capture
from player_affiliation_codec import PROFILE,decode_classification,decode_college,reconstruct_college_projection
from player_affiliation_reader import affiliation_payload,affiliation_projection_ranges
from query import native_affiliations
from live_world import RESTRICTED_PLAYER_RANGES

def put(raw,field,value):
    a=field['offset'];b=field['start_bit'];w=field['width'];n=(b+w+7)//8;word=int.from_bytes(raw[a:a+n],'little');mask=((1<<w)-1)<<b
    raw[a:a+n]=((word&~mask)|(value<<b)).to_bytes(n,'little')
def test_manifest():
    players=[];classes=[];links=[]
    for i,name in enumerate(('Native Test','Other Source')):
        players.append({'source_player_index':i,'native_unique_id_raw':i+1,'preserved_id_raw':i+100,'observed_name':name,'name_status':'OBSERVED_UTF16_PREFIX',
            'native_team_id':0 if i==0 else None,'current_core_roster_status':'CURRENT_CORE_ROSTER' if i==0 else 'NOT_CURRENT_CORE_ROSTER','current_roster_slot':0 if i==0 else None})
        raw=bytearray(1264);put(raw,PROFILE['player_fields']['is_historic_raw'],1);put(raw,PROFILE['player_fields']['is_active_raw'],1)
        classes.append({'source_player_index':i,**decode_classification(bytes(raw))});links.append({'source_player_index':i,'source_object_index':0,'college_source_status':'NATIVE_COLLEGEDATA_REFERENT_OBSERVED'})
    college=bytearray(60);college[:6]=b'France';put(college,PROFILE['college_fields']['college_id_raw'],2047)
    return {'season_year':2022,'descriptors':{'1':{'count':2}},'players':players,'classification_rows':classes,'college_links':links,
        'college_rows':[{'source_object_index':0,**decode_college(bytes(college))}],'game_writes':False,'restricted_player_bytes_read':0}

class AffiliationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'save')
    def payload(self,token='one',m=None):
        return affiliation_payload({'save_id':'save','native_save_filename':'MyLEAGUE0003'},m or test_manifest(),[{'sha256':'0'*64,'payload_kind':'EXPLICIT_SYNTHETIC_CODEC_TEST'}],
            '2026-10-25T00:00:00Z',token,{'player:native:100':'Native Test'})
    def with_player(self,p):p['facts']['players']=[{'player_id':'player:native:100','display_name':'Native Test'}];return p

    def test_independent_flags_and_unknown_code_do_not_imply_signability(self):
        m=test_manifest();row=m['classification_rows'][0]
        self.assertEqual(row['is_historic_raw'],1);self.assertEqual(row['is_active_raw'],1);self.assertEqual(row['free_agency_type_label'],'UNRESTRICTED')
        p=self.payload(m=m);market=p['facts']['market_state_observations'][0]
        self.assertEqual(market['market_status'],'NATIVE_CLASSIFICATION_OBSERVED');self.assertIn('NOT_ESTABLISHED',market['availability_interpretation'])
        raw=bytearray(1264);put(raw,PROFILE['player_fields']['g_league_team_raw'],31);put(raw,PROFILE['player_fields']['free_agency_type_raw'],3)
        decoded=decode_classification(bytes(raw));self.assertIsNone(decoded['g_league_team_label']);self.assertIsNone(decoded['free_agency_type_label'])

    def test_college_referent_does_not_guess_nationality_or_signed_id(self):
        p=self.with_player(self.payload())
        with connect(self.db) as c:
            ingest_capture(c,p);self.assertEqual(c.execute('SELECT count(*) FROM native_college_observations').fetchone()[0],1)
            self.assertEqual(c.execute('SELECT count(*) FROM player_vitals_observations WHERE college IS NOT NULL OR country IS NOT NULL').fetchone()[0],0)
        result=native_affiliations(self.db,limit=1);referent=result['records'][0]['school_country_source']['native_referent']
        self.assertEqual(referent['native_label'],'France');self.assertEqual(referent['college_id_raw'],2047)
        self.assertTrue(result['has_more']);later=native_affiliations(self.db,unit_id=result['unit_id'],after_index=result['next_after_index'])
        self.assertIsNone(later['records'][0]['player_id'])

    def test_missing_college_is_null_not_an_empty_identity(self):
        m=test_manifest();m['college_links'][1]={'source_player_index':1,'source_object_index':None,'college_source_status':'NO_NATIVE_COLLEGE_POINTER'}
        p=self.payload(m=m);self.assertIsNone(p['facts']['player_vitals_observations'][1]['native_college_obs_id'])
        self.assertEqual(len(p['facts']['native_college_observations']),1)

    def test_cross_unit_college_link_rolls_back_complete_unit(self):
        with connect(self.db) as c:
            ingest_capture(c,self.with_player(self.payload()));bad=self.payload('two');bad['facts']['player_vitals_observations'][0]['native_college_obs_id']='player-affiliation:one:college:0'
            with self.assertRaisesRegex(sqlite3.IntegrityError,'cross-unit native college'):ingest_capture(c,bad)
            self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)

    def test_private_player_intervals_and_unselected_college_byte_are_excluded(self):
        raw=bytearray(1264);before=decode_classification(bytes(raw))
        for low,high in RESTRICTED_PLAYER_RANGES:raw[low:high]=b'\xff'*(high-low)
        self.assertEqual(before,decode_classification(bytes(raw)))
        self.assertTrue(all(not(low<b and a<high) for low,high in affiliation_projection_ranges() for a,b in RESTRICTED_PLAYER_RANGES))
        college=bytearray(60);college[:4]=b'Test';college[47]=255
        restored=reconstruct_college_projection(b''.join(college[a:b] for a,b in PROFILE['college_public_ranges']))
        self.assertEqual(restored[47],0);self.assertEqual(decode_college(restored)['native_label'],'Test')

    def test_incomplete_subject_or_missing_college_reference_rejects(self):
        m=test_manifest();m['classification_rows'].pop()
        with self.assertRaisesRegex(ValueError,'incomplete/duplicate'):self.payload(m=m)
        m=test_manifest();m['college_links'][0]['source_object_index']=99
        with self.assertRaisesRegex(ValueError,'absent object'):self.payload(m=m)

    def test_native_filter_is_closed_and_pinned(self):
        with connect(self.db) as c:ingest_capture(c,self.with_player(self.payload()))
        self.assertEqual(len(native_affiliations(self.db,flag='is_historic_raw')['records']),2)
        self.assertEqual(native_affiliations(self.db,flag='is_historic_raw',flag_value=0)['records'],[])
        with self.assertRaisesRegex(ValueError,'classification filter'):native_affiliations(self.db,flag='unknown_sql')

if __name__=='__main__':unittest.main()
