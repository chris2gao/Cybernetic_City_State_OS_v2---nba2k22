"""Historical acquisition cutoffs across domains, source pins and complete paging."""
from copy import deepcopy
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from engine import create_database,connect,ingest_capture
from observation_scope import observed_as_of,query_at,current_scope,query_connection,utc_stamp
from query import player_card,team_card,staff_card,prospect_card,game_box,schedule,history,history_page,export_jsonl
from schema_model import TABLES
from test_player_skills import manifest as skill_manifest
from player_skill_reader import skill_payload

T0='2026-10-24T00:00:00.000001+00:00';T1='2026-10-25T01:00:00+00:00'

class ObservationScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.db=self.root/'world.sqlite';create_database(self.db,'save')
        first={'players':[{'player_id':'p1','display_name':'First Player'}],'teams':[{'team_id':'t1','display_name':'First Team'},{'team_id':'t2','display_name':'Other Team'}],
            'staff_members':[{'staff_id':'c1','display_name':'First Coach'}],
            'games':[{'game_id':'g1','season_id':'s1','home_team_id':'t1','away_team_id':'t2','game_date':'2021-10-19','native_game_id':'100'}],
            'game_state_observations':[{'game_id':'g1','status_code':'0'}],
            'player_attribute_snapshots':[{'player_id':'p1','overall_raw':80,'shot_close_raw':70}],
            'player_vitals_observations':[{'player_id':'p1','height_raw':198}],
            'player_badge_values':[{'player_id':'p1','badge_key':'TEST_BADGE','native_code':1,'owned_state':'owned'}],
            'player_play_type_slots':[{'player_id':'p1','slot_index':i,'native_play_code':str(4 if i==0 else 0)} for i in range(4)],
            'team_finance_observations':[{'team_id':'t1','payroll_raw':1000}],
            'staff_skill_observations':[{'staff_id':'c1','offense_raw':80}],
            'staff_team_assignments':[{'staff_id':'c1','team_id':'t1','role_code':'0'}]}
        self.put('unit-a',T0,first)
        later={'players':[{'player_id':'p2','display_name':'Future Player'}],'staff_members':[{'staff_id':'c2','display_name':'Future Coach'}],
            'game_state_observations':[{'game_id':'g1','status_code':'2','home_points':100,'away_points':90,'is_final':1}],
            'player_attribute_snapshots':[{'player_id':'p1','overall_raw':90},{'player_id':'p2','overall_raw':60}],
            'player_badge_values':[{'player_id':'p1','badge_key':'TEST_BADGE','native_code':0,'owned_state':'not_owned'}],
            'player_play_type_slots':[{'player_id':'p1','slot_index':0,'native_play_code':'0'}],
            'team_finance_observations':[{'team_id':'t1','payroll_raw':2000}],
            'staff_skill_observations':[{'staff_id':'c1','offense_raw':90}],
            'staff_team_assignments':[{'staff_id':'c2','team_id':'t1','role_code':'0'}],
            'draft_prospects':[{'prospect_id':'prospect','display_name':'Future Prospect'}],
            'draft_prospect_attribute_snapshots':[{'prospect_id':'prospect','overall_raw':60}]}
        self.put('unit-b',T1,later)
    def put(self,unit,stamp,facts,source='SYNTHETIC_HISTORY_SCOPE',status='success'):
        payload={'save_id':'save','run_id':unit,'unit_id':unit,'source_key':source,'observed_at':stamp,'evidence_grade':'SYNTHETIC_FIXTURE','season':{'season_id':'s1','season_code':'2021-22'},'facts':facts,'unit_status':status}
        with connect(self.db) as c:ingest_capture(c,payload)
        return payload

    def test_timezone_microseconds_and_partial_field_freshness(self):
        result=query_at(self.db,'2026-10-24T08:00:00.000001+08:00','player_card','p1');family=result['result']['families']['player_attribute_snapshots']
        self.assertEqual(family['overall_raw']['value'],80);self.assertEqual(result['observation_scope']['committed_success_units'],1)
        self.assertEqual(query_at(self.db,'2026-10-24T00:00:00Z','player_card','p1')['result']['status'],'NOT_OBSERVED')
        self.assertEqual(player_card(self.db,'p1')['families']['player_attribute_snapshots']['overall_raw']['value'],90)
        current=query_at(self.db,T1,'player_card','p1')['result'];self.assertEqual(current['families']['player_attribute_snapshots']['shot_close_raw']['unit_id'],'unit-a')
    def test_future_entities_and_failed_units_are_not_visible(self):
        self.put('failed','2026-10-23T00:00:00Z',{},status='failed')
        with observed_as_of(self.db,T0) as scope:
            self.assertEqual(len(scope.unit_ids),1);self.assertEqual(player_card(self.db,'p2')['status'],'NOT_OBSERVED');self.assertEqual(staff_card(self.db,'c2')['status'],'NOT_OBSERVED');self.assertEqual(prospect_card(self.db,'prospect')['status'],'NOT_OBSERVED')
        self.assertEqual(query_at(self.db,'2020-01-01T00:00:00Z','schedule')['result'],[])
    def test_badges_and_ordered_slots_select_current_values_at_the_cutoff(self):
        self.put('unobserved-slot','2026-10-25T02:00:00Z',{'player_play_type_slots':[{'player_id':'p1','slot_index':1}]})
        old=query_at(self.db,T0,'player_card','p1')['result']['families'];new=player_card(self.db,'p1')['families']
        self.assertEqual(old['player_badge_values'][0]['owned_state'],'owned');self.assertEqual(new['player_badge_values'][0]['owned_state'],'not_owned')
        self.assertEqual(len(new['player_play_type_slots']),4);self.assertEqual(new['player_play_type_slots'][0]['native_play_code'],'0');self.assertEqual(old['player_play_type_slots'][0]['native_play_code'],'4')
        self.assertEqual(new['player_play_type_slots'][1]['unit_id'],'unit-a');self.assertEqual(len(history(self.db,'player_play_type_slots')),5)
    def test_team_staff_and_game_read_the_same_historical_scope(self):
        with observed_as_of(self.db,T0):
            team=team_card(self.db,'t1');self.assertEqual(team['families']['team_finance_observations']['payroll_raw']['value'],1000);self.assertEqual(team['assigned_staff'][0]['staff_id'],'c1')
            self.assertEqual(staff_card(self.db,'c1')['families']['staff_skill_observations']['offense_raw']['value'],80)
            self.assertEqual(game_box(self.db,'g1')['states'][0]['status_code'],'0');self.assertEqual(schedule(self.db)[0]['status_code'],'0')
        self.assertEqual(schedule(self.db)[0]['status_code'],'2')
    def test_source_key_snapshots_settings_rules_and_market_obey_cutoff(self):
        for unit,stamp,value in [('settings-a',T0,1),('settings-b',T1,2)]:
            self.put(unit,stamp,{'game_setting_observations':[{'setting_obs_id':unit+':setting','field_id':'team_tactic_settings.ace_code','scope_code':'SYNTHETIC','integer_value':value}],
                'league_rule_observations':[{'season_id':'s1','rule_key':'SYNTHETIC_RULE','setting_obs_id':unit+':setting','integer_value':value}]},'BOUND_SETTINGS_AND_RULES')
        from query import settings_snapshot,rules_snapshot,market_snapshot
        with observed_as_of(self.db,T0):
            self.assertIn('settings-a',json.dumps(settings_snapshot(self.db)));self.assertNotIn('settings-b',json.dumps(rules_snapshot(self.db)));self.assertEqual(market_snapshot(self.db)['status'],'NOT_OBSERVED')
    def test_explicit_future_native_unit_pin_cannot_bypass_cutoff(self):
        m=skill_manifest();p=skill_payload({'save_id':'save','native_save_filename':'Synthetic'},m,[{'sha256':'0'*64,'payload_kind':'SYNTHETIC_TEST_SOURCE'}],T1,'future',{'player:native:100':'Skill Test'});p['facts']['players']=[{'player_id':'player:native:100','display_name':'Skill Test'}]
        with connect(self.db) as c:ingest_capture(c,p)
        result=query_at(self.db,T0,'native_player_skills',unit_id=p['unit_id'])['result'];self.assertEqual(result['records'],[])
    def test_history_keyset_paging_is_complete_through_equal_timestamps(self):
        self.put('unit-z',T1,{'player_attribute_snapshots':[{'player_id':'p1','overall_raw':91}]})
        with observed_as_of(self.db,T1):
            cursor=None;rows=[]
            while True:
                page=history_page(self.db,'player_attribute_snapshots',entity_key='player_id',entity_id='p1',limit=1,cursor=cursor);rows+=page['records']
                if not page['has_more']:break
                cursor=page['next_cursor']
            self.assertEqual([r['overall_raw'] for r in rows],[91,90,80]);self.assertEqual(len({r['snapshot_id'] for r in rows}),3)
    def test_scope_freezes_units_and_cursor_rejects_late_backfill(self):
        with observed_as_of(self.db,T1):
            page=history_page(self.db,'player_attribute_snapshots',entity_key='player_id',entity_id='p1',limit=1)
            self.put('unit-zz',T0,{'player_attribute_snapshots':[{'player_id':'p1','overall_raw':79}]})
            self.assertEqual(len(history(self.db,'player_attribute_snapshots',entity_key='player_id',entity_id='p1')),2)
            self.assertEqual(history_page(self.db,'player_attribute_snapshots',entity_key='player_id',entity_id='p1',cursor=page['next_cursor'])['records'][0]['overall_raw'],80)
        with self.assertRaisesRegex(ValueError,'ledger changed'):history_page(self.db,'player_attribute_snapshots',entity_key='player_id',entity_id='p1',cursor=page['next_cursor'])
    def test_nested_scope_cross_database_refusal_and_reset(self):
        with observed_as_of(self.db,T0):
            self.assertEqual(player_card(self.db,'p1')['families']['player_attribute_snapshots']['overall_raw']['value'],80)
            with observed_as_of(self.db,T1):self.assertEqual(player_card(self.db,'p1')['families']['player_attribute_snapshots']['overall_raw']['value'],90)
            with self.assertRaises(ValueError):query_connection(self.root/'other.sqlite',True)
            with self.assertRaises(ValueError):query_connection(self.db,False)
        self.assertIsNone(current_scope());self.assertEqual(player_card(self.db,'p1')['families']['player_attribute_snapshots']['overall_raw']['value'],90)
    def test_export_filters_before_limit_and_original_file_is_unchanged(self):
        before=hashlib.sha256(self.db.read_bytes()).hexdigest();out=self.root/'old.jsonl'
        with observed_as_of(self.db,T0):self.assertEqual(export_jsonl(self.db,out,'player_attribute_snapshots',limit=1)['rows'],1)
        self.assertEqual(json.loads(out.read_text())['overall_raw'],80);self.assertEqual(hashlib.sha256(self.db.read_bytes()).hexdigest(),before)
        with self.assertRaises(PermissionError):query_at(self.db,T0,'inspect_source_capture','unit-a')
        with self.assertRaises(PermissionError):query_at(self.db,T0,'history','player_restricted_observations')
    def test_all_scoped_table_views_are_executable_and_timestamps_require_timezone(self):
        for invalid in ('2026-10-24','2026-10-24T00:00:00',True,'not-a-time'):
            with self.assertRaises(ValueError):utc_stamp(invalid)
        with observed_as_of(self.db,T1),query_connection(self.db,True) as c:
            for name in TABLES:c.execute('SELECT * FROM "'+name+'" LIMIT 0')
        with self.assertRaises(ValueError):history_page(self.db,'players')
    def test_cli_as_of_envelope_and_current_default(self):
        command=[sys.executable,str(BASE/'cli.py'),'player',str(self.db),'p1','--as-of',T0];result=subprocess.run(command,capture_output=True,text=True,check=True)
        value=json.loads(result.stdout);self.assertEqual(value['result']['families']['player_attribute_snapshots']['overall_raw']['value'],80);self.assertIn('CAPTURE_OBSERVED_AT',value['observation_scope']['time_basis'])
        result=subprocess.run(command[:-2],capture_output=True,text=True,check=True);self.assertEqual(json.loads(result.stdout)['families']['player_attribute_snapshots']['overall_raw']['value'],90)

if __name__=='__main__':unittest.main()
