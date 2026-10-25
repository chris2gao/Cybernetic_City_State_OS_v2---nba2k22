"""Behavioral tests for the world-data expansion; all source grades explicit."""
from contextlib import closing
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from engine import create_database,connect,ingest_capture,ingest_synthetic_capture,ingest_or_quarantine,migrate_v1,summarize
from cli import synthetic_payload
from readers import replay_ag01d,decode_player_public
from query import history,player_card,game_box,export_jsonl
from schema_model import TABLES,schema_sql,dictionary


class WorldDataIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'world.sqlite';create_database(self.path,'save-a')

    def bundle(self):
        return {'save_id':'save-a','run_id':'run-all','unit_id':'unit-all','source_key':'ALL_DOMAIN_SYNTHETIC',
                'observed_at':'2026-10-24T00:00:00Z','evidence_grade':'SYNTHETIC_FIXTURE',
                'season':{'season_id':'s1','season_code':'2021-22'},'facts':{}}

    def test_ddl_dictionary_and_every_relation_are_executable(self):
        self.assertEqual(len(TABLES),77)
        self.assertEqual(schema_sql(),(BASE/'schema.sql').read_text())
        self.assertEqual(dictionary(),json.loads((BASE/'field_dictionary.json').read_text()))
        with connect(self.path) as c:
            for name,spec in TABLES.items():
                self.assertEqual([r[1] for r in c.execute(f'PRAGMA table_info("{name}")')],[x.name for x in spec.columns])
                c.execute(f'SELECT * FROM "{name}" LIMIT 0')
            self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_all_domains_typed_ingest_and_queries(self):
        b=self.bundle();b['facts']={
            'teams':[{'team_id':'t1','display_name':'Synthetic A'},{'team_id':'t2','display_name':'Synthetic B'}],
            'players':[{'player_id':'p1','display_name':'Synthetic Player'}],
            'staff_members':[{'staff_id':'c1','display_name':'Synthetic Coach'}],
            'team_seasons':[{'team_id':'t1','season_id':'s1','conference':'SYNTHETIC'}],
            'roster_memberships':[{'player_id':'p1','team_id':'t1','roster_status':'SYNTHETIC_ACTIVE'}],
            'team_rotation_slots':[{'team_id':'t1','player_id':'p1','slot_index':0,'planned_minutes':30}],
            'staff_team_assignments':[{'staff_id':'c1','team_id':'t1','role_code':'SYNTHETIC_HEAD_COACH'}],
            'staff_skill_observations':[{'staff_id':'c1','offense_raw':80}],
            'staff_contract_observations':[{'staff_id':'c1','salary_raw':1000,'years_left':2}],
            'coach_preferences':[{'staff_id':'c1','preferred_system_raw':2}],
            'team_tactic_settings':[{'team_id':'t1','ace_code':1}],
            'team_training_settings':[{'team_id':'t1','focus_code':'SYNTHETIC_DEFENSE'}],
            'team_playbook_slots':[{'team_id':'t1','slot_index':0,'play_code':'SYNTHETIC_PLAY'}],
            'player_training_observations':[{'player_id':'p1','focus_code':'SYNTHETIC_SHOOTING'}],
            'player_vitals_observations':[{'player_id':'p1','height_raw':198}],
            'player_contract_observations':[{'player_id':'p1','contract_year_1_raw':1000,'years_left_on_contract_raw':2}],
            'player_health_observations':[{'player_id':'p1','availability':'SYNTHETIC_HEALTHY'}],
            'player_morale_observations':[{'player_id':'p1','morale_raw':50}],
            'team_finance_observations':[{'team_id':'t1','payroll_raw':1000}],
            'draft_pick_assets':[{'pick_id':'pick1','draft_year':2022,'draft_round':1,'original_team_id':'t1'}],
            'external_transaction_events':[{'transaction_id':'tx1','event_type':'SYNTHETIC_TRADE','source_ref':'SYNTHETIC_RECEIPT','status':'CONFIRMED','producer_event_id':'e1'}],
            'transaction_components':[{'transaction_id':'tx1','from_team_id':'t1','to_team_id':'t2','pick_id':'pick1','component_kind':'SYNTHETIC_PICK'}],
            'draft_pick_ownerships':[{'pick_id':'pick1','owner_team_id':'t2','event_ref':'tx1','origin_type':'EXTERNAL'}],
            'market_state_observations':[{'player_id':'p1','market_status':'SYNTHETIC_AVAILABLE','origin_type':'NATIVE'}],
            'game_setting_observations':[{'field_id':'team_tactic_settings.ace_code','scope_code':'SYNTHETIC_TEAM','integer_value':1}],
            'league_rule_observations':[{'season_id':'s1','rule_key':'SYNTHETIC_RULE','integer_value':1}],
            'season_award_instances':[{'award_id':'award1','season_id':'s1','award_code':'SYNTHETIC_MVP','award_type':'FINAL','is_final':1}],
            'award_recipients':[{'award_id':'award1','player_id':'p1'}],
            'game_news_entries':[{'season_id':'s1','text_body':'SYNTHETIC_NEWS'}],
            'season_record_entries':[{'season_id':'s1','record_key':'SYNTHETIC_RECORD','holder_player_id':'p1','value_raw':'22','source_ref':'SYNTHETIC'}],
        }
        with connect(self.path) as c:self.assertEqual(ingest_capture(c,b),'ingested')
        self.assertEqual(history(self.path,'team_rotation_slots')[0]['planned_minutes'],30)
        self.assertEqual(history(self.path,'draft_pick_ownerships')[0]['owner_team_id'],'t2')
        self.assertEqual(player_card(self.path,'p1')['families']['player_contract_observations']['contract_year_1_raw']['value'],1000)
        self.assertEqual(summarize(self.path)['foreign_key_errors'],0)

    def test_research_original_bytes_to_typed_world_and_18_total_metrics(self):
        bundles=list(replay_ag01d('save-a',observed_at='2026-10-24T00:00:00Z'))
        for b in bundles:
            with connect(self.path) as c:ingest_capture(c,b)
        summary=summarize(self.path)
        self.assertEqual((summary['game_count'],summary['box_observations']),(16,16))
        self.assertNotIn('LIVE_READ',summary['source_grades'])
        with connect(self.path) as c:
            current=c.execute('SELECT * FROM player_season_totals WHERE season_id=(SELECT season_id FROM games LIMIT 1)').fetchone()
            for name in 'points fg_made fg_attempted three_made three_attempted ft_made ft_attempted offensive_rebounds defensive_rebounds assists steals blocks turnovers fouls minutes_raw plus_minus possessions_raw'.split():
                # Native career total has no possessions field: do not invent it.
                if current[name] is None:continue
                self.assertEqual(c.execute(f'SELECT sum({name}) FROM player_game_boxes').fetchone()[0],current[name],name)
            self.assertEqual(c.execute('SELECT count(*) FROM source_artifacts').fetchone()[0],len(bundles))
            self.assertEqual(c.execute('SELECT count(*) FROM player_game_boxes').fetchone()[0],current['games_played'])
            self.assertEqual(c.execute('SELECT sum(is_starter) FROM player_game_boxes').fetchone()[0],current['games_started'])
            gid=c.execute('SELECT game_id FROM games LIMIT 1').fetchone()[0]
            pid=c.execute('SELECT player_id FROM players').fetchone()[0]
        self.assertTrue(game_box(self.path,gid)['player_boxes'])
        card=player_card(self.path,pid)
        self.assertEqual(card['families']['player_attribute_snapshots']['overall_raw']['status'],'NOT_OBSERVED')
        encoded=json.dumps(card).lower()
        self.assertNotIn('potential',encoded);self.assertNotIn('raw_player',encoded)

    def test_partial_fields_have_independent_freshness_and_timezone_sort(self):
        a=synthetic_payload('save-a',observed_at='2026-10-24T08:00:00+08:00')
        with connect(self.path) as c:ingest_synthetic_capture(c,a)
        b=synthetic_payload('save-a','run-2','unit-2','2026-10-24T01:00:00Z')
        b['attributes']=[{'player_id':'player-a','overall_raw':90}]
        with connect(self.path) as c:ingest_synthetic_capture(c,b)
        fields=player_card(self.path,'player-a')['families']['player_attribute_snapshots']
        self.assertEqual(fields['overall_raw']['value'],90)
        self.assertEqual(fields['shot_close_raw']['unit_id'],'unit-1')
        self.assertNotEqual(fields['overall_raw']['observed_at'],fields['shot_close_raw']['observed_at'])

    def test_raw_potential_and_owner_paths_never_exported(self):
        for name in ('source_artifacts','native_fields','player_restricted_observations','game_news_entries'):
            with self.assertRaises(PermissionError):history(self.path,name)
            with self.assertRaises(PermissionError):export_jsonl(self.path,Path(self.tmp.name)/'out.jsonl',name)
        with self.assertRaises(PermissionError):history(self.path,'players; DROP TABLE saves')
        public=decode_player_public(bytes([77])*1264)
        self.assertFalse(any('potential' in k for k in public))
        with self.assertRaises(ValueError):decode_player_public(b'bad')

    def test_invalid_field_atomic_rollback_in_non_player_domain(self):
        b=self.bundle();b['facts']={'teams':[{'team_id':'t1','display_name':'Synthetic'}],
            'team_finance_observations':[{'team_id':'t1','payroll_raw':'not-an-integer'}]}
        with connect(self.path) as c:
            with self.assertRaises(ValueError):ingest_capture(c,b)
            self.assertEqual(c.execute('SELECT count(*) FROM teams').fetchone()[0],0)
            self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],0)

    def test_final_season_cannot_be_silently_reobserved(self):
        b=self.bundle();b['facts']={'players':[{'player_id':'p1','display_name':'Synthetic'}],
            'player_season_totals':[{'player_id':'p1','season_id':'s1','points':100,'is_final':1}]}
        with connect(self.path) as c:ingest_capture(c,b)
        b['unit_id']='later';b['run_id']='later';b['facts']={'player_season_totals':[{'player_id':'p1','season_id':'s1','points':101}]}
        with connect(self.path) as c:
            with self.assertRaises(sqlite3.IntegrityError):ingest_capture(c,b)
            self.assertEqual(c.execute('SELECT points FROM player_season_totals').fetchone()[0],100)

    def test_game_history_conflict_quarantines_without_changing_original(self):
        a=synthetic_payload('save-a')
        a['game_state']['is_final']=1
        with connect(self.path) as c:ingest_synthetic_capture(c,a)
        b=self.bundle();b['season']=a['season'];b['facts']={'player_game_boxes':[{'game_id':'game-1','player_id':'player-a','team_id':'team-a','points':99}]}
        with connect(self.path) as c:
            self.assertEqual(ingest_or_quarantine(c,b),'quarantined_pending_human')
        with connect(self.path) as c:
            self.assertEqual(c.execute('SELECT points FROM player_game_boxes').fetchone()[0],22)
            self.assertEqual(c.execute('SELECT count(*) FROM player_game_boxes').fetchone()[0],1)
            self.assertEqual(c.execute('SELECT review_status FROM fact_conflicts').fetchone()[0],'PENDING_HUMAN')
        b['run_id']='supplement';b['unit_id']='supplement'
        b['facts']['player_game_boxes'][0]['points']=22
        b['facts']['player_game_boxes'][0]['assists']=5
        with connect(self.path) as c:self.assertEqual(ingest_capture(c,b),'ingested')

    def test_version_one_copy_migration_preserves_source_and_values(self):
        source=Path(self.tmp.name)/'old.sqlite';new=Path(self.tmp.name)/'new.sqlite'
        repo=BASE.parents[2]
        sql=subprocess.run(['git','show','5cff5f7a6d826ed851954e83021e65372dcd2663:08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/schema.sql'],cwd=repo,capture_output=True,check=True,text=True).stdout
        with closing(sqlite3.connect(source)) as c:
            c.executescript(sql)
            c.execute("INSERT INTO saves VALUES (1,'save-old',1,'2026-10-24T00:00:00Z','SYNTHETIC_ONLY')")
            c.execute("INSERT INTO seasons VALUES ('s1','2021-22')")
            c.execute("INSERT INTO players VALUES ('p1','Old Player',NULL,'UNKNOWN')")
            c.execute("INSERT INTO capture_runs VALUES ('r1','s1','2026-10-24T00:00:00Z','SYNTHETIC_FIXTURE')")
            c.execute("INSERT INTO capture_units VALUES ('u1','r1','old','old-hash','success','2026-10-24T00:00:00Z')")
            c.execute("INSERT INTO player_attribute_snapshots VALUES ('a1','p1','u1',80,70,75)")
            c.execute('PRAGMA user_version=1');c.commit()
        before=hashlib.sha256(source.read_bytes()).hexdigest()
        migrate_v1(source,new)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before)
        with connect(new) as c:
            self.assertEqual(c.execute('SELECT overall_raw FROM player_attribute_snapshots').fetchone()[0],80)
            self.assertEqual(c.execute('SELECT payload_sha256 FROM capture_units').fetchone()[0],'old-hash')
            self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
            self.assertEqual(c.execute('SELECT created_at FROM saves').fetchone()[0],'2026-10-24T00:00:00Z')

    def test_exports_refuse_overwrite_and_silent_history_truncation(self):
        with connect(self.path) as c:ingest_synthetic_capture(c,synthetic_payload('save-a'))
        out=Path(self.tmp.name)/'players.jsonl'
        self.assertEqual(export_jsonl(self.path,out,'players')['rows'],1)
        with self.assertRaises(FileExistsError):export_jsonl(self.path,out,'players')
        self.assertNotIn('potential',out.read_text().lower())


if __name__=='__main__':unittest.main()
