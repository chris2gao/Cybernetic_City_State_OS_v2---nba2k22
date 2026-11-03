"""League comparison behavior on isolated fixtures; not Native/UI acceptance."""
import json,subprocess,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from engine import create_database,connect,ingest_capture
from query import league_standings,player_leaderboard
from observation_scope import query_at
from league_views import PLAYER_METRICS

T0='2026-10-24T00:00:00Z';T1='2026-10-25T00:00:00Z'

class LeagueViewsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'save')
        self.put('identity',T0,{'players':[{'player_id':p,'display_name':p} for p in ('p1','p2','p3','p4')], 'teams':[{'team_id':t,'display_name':t} for t in ('a','b','c','d')]})
    def put(self,unit,stamp,facts):
        with connect(self.db) as conn:ingest_capture(conn,{'save_id':'save','run_id':unit,'unit_id':unit,'source_key':'SYNTHETIC_LEAGUE','observed_at':stamp,'evidence_grade':'SYNTHETIC_FIXTURE','season':{'season_id':'s','season_code':'s'},'facts':facts})
    def player(self,p,points=20,games=2,scope='OBSERVED',phase=None,**kw):
        return {'player_id':p,'season_id':'s','team_scope':scope,'phase_code':phase,'games_played':games,'points':points,**kw}
    def team(self,t,wins=2,losses=1,phase=None):return {'team_id':t,'season_id':'s','phase_code':phase,'wins':wins,'losses':losses}
    def test_source_cohort_is_not_latest_per_entity_and_never_borrows_metric(self):
        self.put('old',T0,{'player_season_totals':[self.player('p1'),self.player('p2')]})
        self.put('new',T1,{'player_season_totals':[self.player('p1',None)]})
        value=player_leaderboard(self.db,'s');self.assertEqual(value['selected_unit_id'],'new');self.assertEqual(value['records'],[]);self.assertEqual(value['coverage']['captured_rows'],1)
        self.assertEqual(player_leaderboard(self.db,'s',unit_id='old')['coverage']['ranked_rows'],2)
    def test_exact_null_phase_is_distinct_and_missing_unit_does_not_fallback(self):
        self.put('null',T0,{'team_season_totals':[self.team('a')]})
        self.put('phase',T1,{'team_season_totals':[self.team('b',phase='1')]})
        self.assertEqual(league_standings(self.db,'s')['selected_unit_id'],'null')
        self.assertEqual(league_standings(self.db,'s',phase_code='1')['records'][0]['totals']['team_id'],'b')
        self.assertEqual(league_standings(self.db,'s',unit_id='phase')['status'],'UNIT_NOT_OBSERVED_FOR_COHORT')
        self.assertEqual(player_leaderboard(self.db,'missing')['status'],'NO_TOTALS_OBSERVED')
    def test_rational_ties_competition_rank_stable_order_and_paging(self):
        self.put('u',T0,{'team_season_totals':[self.team('d',1,2),self.team('c',1,3),self.team('b',4,2),self.team('a',2,1)]})
        first=league_standings(self.db,'s',limit=1);self.assertEqual(first['records'][0]['totals']['team_id'],'a');self.assertEqual(first['records'][0]['rank'],1)
        rest=league_standings(self.db,'s',unit_id='u',offset=first['next_offset']);self.assertEqual([r['rank'] for r in rest['records']],[1,3,4]);self.assertEqual(rest['records'][0]['value_exact'],{'numerator':2,'denominator':3})
        with self.assertRaisesRegex(ValueError,'unit_id'):league_standings(self.db,'s',offset=1)
    def test_zero_missing_and_negative_win_loss_excluded(self):
        self.put('u',T0,{'team_season_totals':[self.team('a',0,0),self.team('b',None,1),self.team('c',-1,2),self.team('d',0,1)]})
        value=league_standings(self.db,'s');self.assertEqual(value['coverage']['ranked_rows'],1);self.assertEqual(value['records'][0]['value'],0)
        self.assertEqual(sum(value['coverage']['excluded_by_reason'].values()),3)
    def test_scope_ambiguity_rejected_and_literal_team_filter_not_roster(self):
        self.put('u',T0,{'player_season_totals':[self.player('p1',scope='A',team_id='a'),self.player('p2',scope='B',team_id='b'),self.player('p3',scope=None)]})
        with self.assertRaisesRegex(ValueError,'multiple team_scope'):player_leaderboard(self.db,'s')
        self.assertEqual(player_leaderboard(self.db,'s',team_scope='A',team_id='a')['coverage']['ranked_rows'],1)
        self.assertEqual(player_leaderboard(self.db,'s',team_scope='A',team_id='b')['records'],[])
        self.assertEqual(player_leaderboard(self.db,'s',team_scope='missing')['selected_unit_id'],'u')
        self.assertEqual(player_leaderboard(self.db,'s',null_team_scope=True)['records'][0]['totals']['player_id'],'p3')
        with self.assertRaisesRegex(ValueError,'mutually exclusive'):player_leaderboard(self.db,'s',team_scope='A',null_team_scope=True)
    def test_requested_scope_never_selects_older_unit(self):
        self.put('old',T0,{'player_season_totals':[self.player('p1',scope='OLD')]});self.put('new',T1,{'player_season_totals':[self.player('p2',scope='NEW')]})
        value=player_leaderboard(self.db,'s',team_scope='OLD');self.assertEqual(value['selected_unit_id'],'new');self.assertEqual(value['records'],[])
    def test_per_game_totals_rebounds_and_ascending(self):
        self.put('u',T0,{'player_season_totals':[self.player('p1',20,2,offensive_rebounds=1,defensive_rebounds=2),self.player('p2',30,4,offensive_rebounds=2,defensive_rebounds=4)]})
        self.assertEqual(player_leaderboard(self.db,'s')['records'][0]['totals']['player_id'],'p1')
        self.assertEqual(player_leaderboard(self.db,'s',metric='points')['records'][0]['totals']['player_id'],'p2')
        self.assertEqual(player_leaderboard(self.db,'s',ascending=True)['records'][0]['totals']['player_id'],'p2')
        value=player_leaderboard(self.db,'s',metric='total_rebounds_per_game');self.assertEqual([r['rank'] for r in value['records']],[1,1]);self.assertEqual(value['records'][0]['value'],1.5)
    def test_shooting_denominators_thresholds_and_inconsistent_counts(self):
        self.put('u',T0,{'player_season_totals':[self.player('p1',fg_made=2,fg_attempted=4),self.player('p2',fg_made=1,fg_attempted=1),self.player('p3',fg_made=0,fg_attempted=0),self.player('p4',fg_made=2,fg_attempted=1)]})
        value=player_leaderboard(self.db,'s',metric='field_goal_fraction',min_attempts=2)
        self.assertEqual(len(value['records']),1);self.assertEqual(value['records'][0]['value'],.5);self.assertEqual(len(value['coverage']['excluded_by_reason']),3)
    def test_min_games_unknown_and_invalid_counts(self):
        self.put('u',T0,{'player_season_totals':[self.player('p1',games=0),self.player('p2',games=None),self.player('p3',points=None),self.player('p4',games=1)]})
        value=player_leaderboard(self.db,'s',min_games=2);self.assertEqual(value['records'],[])
        zero=player_leaderboard(self.db,'s',min_games=0);self.assertIn('ZERO_GAMES_UNDEFINED',zero['coverage']['excluded_by_reason'])
    def test_cutoff_and_pinned_unit_visibility(self):
        self.put('old',T0,{'player_season_totals':[self.player('p1')]});self.put('new',T1,{'player_season_totals':[self.player('p2')]})
        self.assertEqual(query_at(self.db,T0,'player_leaderboard','s')['result']['selected_unit_id'],'old')
        self.assertEqual(query_at(self.db,T0,'player_leaderboard','s',unit_id='new')['result']['status'],'UNIT_NOT_OBSERVED_FOR_COHORT')
    def test_utc_source_selection_and_observation_provenance(self):
        self.put('local','2026-10-24T08:00:00+08:00',{'team_season_totals':[self.team('a')]})
        self.put('utc','2026-10-24T00:00:00.000001Z',{'team_season_totals':[self.team('b')]})
        value=league_standings(self.db,'s');self.assertEqual(value['selected_unit_id'],'utc');self.assertEqual(value['capture']['source_grade'],'SYNTHETIC_FIXTURE');self.assertEqual(value['records'][0]['totals']['unit_id'],'utc')
    def test_validation_and_all_registered_metrics(self):
        self.put('u',T0,{'player_season_totals':[self.player('p1')]})
        for metric in PLAYER_METRICS:self.assertEqual(player_leaderboard(self.db,'s',metric=metric)['selected_unit_id'],'u')
        for args in ({'metric':'overall'},{'min_games':-1},{'min_games':True},{'limit':101},{'offset':-1},{'min_attempts':1},{'ascending':1}):
            with self.subTest(args=args),self.assertRaises(ValueError):player_leaderboard(self.db,'s',**args)
    def test_cli_commands_as_of_and_source_pin(self):
        self.put('old',T0,{'player_season_totals':[self.player('p1')],'team_season_totals':[self.team('a')]});self.put('new',T1,{'player_season_totals':[self.player('p2')],'team_season_totals':[self.team('b')]})
        for command in ('standings','player-leaderboard'):
            result=subprocess.run([sys.executable,str(BASE/'cli.py'),command,str(self.db),'s','--as-of',T0],capture_output=True,text=True,check=True)
            self.assertEqual(json.loads(result.stdout)['result']['selected_unit_id'],'old')

if __name__=='__main__':unittest.main()
