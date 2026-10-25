"""Single-capture Box selection and same-row season derivations; fixture evidence only."""
from copy import deepcopy
import json,subprocess,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from engine import create_database,connect,ingest_capture
from query import game_box,player_seasons,season_summary
from observation_scope import query_at

T0='2026-10-24T00:00:00Z';T1='2026-10-25T00:00:00Z'

class CompetitionViewsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'save')
        facts={'teams':[{'team_id':'a','native_team_id':'10','display_name':'A'},{'team_id':'b','native_team_id':'20','display_name':'B'}],
            'players':[{'player_id':'p1','native_player_id':'100','display_name':'One'},{'player_id':'p2','native_player_id':'200','display_name':'Two'}],
            'games':[{'game_id':'g','season_id':'s','home_team_id':'a','away_team_id':'b','game_date':None}]}
        self.put('identity',T0,facts)
    def put(self,unit,stamp,facts,season='s'):
        payload={'save_id':'save','run_id':unit,'unit_id':unit,'source_key':'SYNTHETIC_COMPETITION','observed_at':stamp,'evidence_grade':'SYNTHETIC_FIXTURE',
            'season':{'season_id':season,'season_code':season},'facts':facts}
        with connect(self.db) as c:ingest_capture(c,payload)
    def boxes(self):
        return {'game_state_observations':[{'game_id':'g','status_code':'2','is_final':1,'score_provenance':'TOTAL_FIELD_NOT_OBSERVED'}],
            'player_game_boxes':[{'game_id':'g','player_id':p,'team_id':t,'in_use':1,'points':n,'points_provenance':'SYNTHETIC'} for p,t,n in [('p1','a',10),('p2','b',8)]],
            'game_period_scores':[{'game_id':'g','team_id':'a','period_index':1,'period_points':10}],
            'native_box_observations':[{'game_id':'g','side':side,'row_index':0,'native_player_id':p,'native_team_id':t,'in_use':1,'points':n,'points_provenance':'SYNTHETIC','identity_status':'CURRENT_CONTEXT_RESOLVED'} for side,p,t,n in [('HOME',100,10,10),('AWAY',200,20,8)]]}
    def totals(self,points=100,games=5,phase=None,scope='UNVERIFIED_SCOPE',team=None):
        return {'player_season_totals':[{'player_id':'p1','season_id':'s','team_id':team,'team_scope':scope,'phase_code':phase,'games_played':games,'points':points,'fg_made':30,'fg_attempted':60,'three_made':0,'three_attempted':0,'offensive_rebounds':4,'defensive_rebounds':6}],
            'team_season_totals':[{'team_id':'a','season_id':'s','phase_code':phase,'wins':3,'losses':2,'points':500,'fg_made':200,'fg_attempted':400}]}
    def test_repeated_capture_returns_one_complete_unit_and_explicit_history(self):
        facts=self.boxes();self.put('old',T0,facts);self.put('new',T1,facts)
        value=game_box(self.db,'g');self.assertEqual(value['selected_unit_id'],'new');self.assertEqual(len(value['player_boxes']),2)
        self.assertEqual(len(value['observation_units']),2);self.assertEqual(value['scores']['home_points'],10)
        self.assertEqual(value['scores']['value_status'],'DERIVED_CANONICAL_BOX_SUM_MATCHING_CAPTURED_NATIVE_WINDOW')
        self.assertEqual(game_box(self.db,'g',unit_id='old')['selected_unit_id'],'old')
        self.assertEqual(query_at(self.db,T0,'game_box','g')['result']['selected_unit_id'],'old')
    def test_new_partial_unit_does_not_borrow_old_boxes_and_unknown_pin_never_falls_back(self):
        self.put('old',T0,self.boxes());self.put('partial',T1,{'game_state_observations':self.boxes()['game_state_observations']})
        value=game_box(self.db,'g');self.assertEqual(value['player_boxes'],[]);self.assertIsNone(value['scores']['home_points'])
        self.assertEqual(game_box(self.db,'g',unit_id='identity')['status'],'UNIT_NOT_OBSERVED_FOR_GAME')
        self.assertEqual(query_at(self.db,T0,'game_box','g',unit_id='partial')['result']['status'],'UNIT_NOT_OBSERVED_FOR_GAME')
    def test_unplayed_and_all_unused_rows_do_not_invent_zero_scores(self):
        facts=self.boxes();facts['player_game_boxes']=[];facts['game_state_observations']=[{'game_id':'g','status_code':'0'}]
        for row in facts['native_box_observations']:row['in_use']=0;row['points']=0
        self.put('unused',T0,facts);value=game_box(self.db,'g');self.assertIsNone(value['scores']['home_points']);self.assertIsNone(value['scores']['captured_native_points']['HOME'])
    def test_partial_identity_and_equal_total_wrong_identity_are_not_qualified(self):
        for variant in ('missing','wrong-id','wrong-points','unresolved'):
            with self.subTest(variant=variant):
                # Separate DBs avoid asserting conflicting final facts in one history.
                db=self.db;self.db=Path(self.tmp.name)/(variant+'.sqlite');create_database(self.db,'save')
                with connect(db,True) as c:
                    identities={t:[dict(r) for r in c.execute('SELECT * FROM '+t)] for t in ('players','teams','games')}
                self.put('ids',T0,identities);facts=self.boxes()
                if variant=='missing':facts['player_game_boxes']=facts['player_game_boxes'][1:]
                elif variant=='wrong-id':facts['native_box_observations'][0]['native_player_id']=999
                elif variant=='wrong-points':facts['native_box_observations'][0]['points']=11
                else:facts['native_box_observations'][0]['identity_status']='UNRESOLVED_CANONICAL_PLAYER'
                self.put('capture',T1,facts);value=game_box(self.db,'g')
                self.assertIsNone(value['scores']['home_points']);self.assertIsNotNone(value['scores']['captured_native_points']['HOME'])
                self.assertEqual(value['coverage']['HOME']['status'],'PARTIAL_OR_MISMATCHED_CAPTURED_NATIVE_COVERAGE');self.db=db
    def test_unused_slots_do_not_require_native_identity_or_team_match(self):
        facts=self.boxes();unused=deepcopy(facts['native_box_observations'][0]);unused.update(row_index=1,native_team_id=65535,native_player_id=65535,in_use=0,points=0,identity_status='UNRESOLVED')
        facts['native_box_observations'].append(unused);self.put('capture',T0,facts);value=game_box(self.db,'g')
        self.assertEqual(value['scores']['home_points'],10);self.assertEqual(value['coverage']['HOME']['native_captured_rows'],2)
        self.assertNotIn('native_box_observations',value)
    def test_literal_partial_state_score_preserves_provenance_and_does_not_fill(self):
        facts=self.boxes();facts['game_state_observations'][0].update(home_points=10,score_provenance='SYNTHETIC_LITERAL')
        self.put('capture',T0,facts);value=game_box(self.db,'g')['scores'];self.assertEqual(value['value_status'],'PARTIAL_GAME_STATE_SCORE_FIELDS');self.assertIsNone(value['away_points']);self.assertEqual(value['state_score_provenance'],'SYNTHETIC_LITERAL')
    def test_latest_selection_uses_utc_and_microseconds(self):
        self.put('local-later-text','2026-10-24T08:00:00+08:00',self.totals(100))
        self.put('utc-latest','2026-10-24T00:00:00.000001Z',self.totals(110))
        self.assertEqual(player_seasons(self.db,'p1')['records'][0]['totals']['unit_id'],'utc-latest')
        self.put('game-local','2026-10-24T08:00:00+08:00',self.boxes());self.put('game-utc','2026-10-24T00:00:00.000001Z',self.boxes())
        self.assertEqual(game_box(self.db,'g')['selected_unit_id'],'game-utc')
    def test_same_row_rates_no_field_carry_and_zero_attempts_are_undefined(self):
        self.put('old',T0,self.totals());self.put('new',T1,self.totals(120,None))
        records=player_seasons(self.db,'p1')['records'];self.assertEqual(len(records),1);value=records[0]['derived']
        self.assertIsNone(value['per_game_counts']['points']);self.assertEqual(value['shooting_fractions']['field_goal_fraction']['value'],0.5)
        self.assertIsNone(value['shooting_fractions']['three_point_fraction']['value']);self.assertEqual(value['minutes_conversion'],'WITHHELD_RAW_NATIVE_TIME_UNIT_NOT_PROMOTED')
        old=query_at(self.db,T0,'player_seasons','p1')['result']['records'][0]['derived'];self.assertEqual(old['per_game_counts']['points'],20);self.assertEqual(old['per_game_counts']['total_rebounds'],2)
    def test_team_denominator_and_ordering_preserve_unknown_phase_and_no_official_seed(self):
        facts=self.totals();facts['team_season_totals'].append({'team_id':'b','season_id':'s','wins':4,'losses':1,'points':450})
        self.put('capture',T0,facts);value=season_summary(self.db,'s');team=next(r for r in value['teams'] if r['totals']['team_id']=='a')
        self.assertEqual(team['derived']['per_game_counts']['points'],100);self.assertEqual(team['derived_win_fraction'],0.6)
        ordering=value['win_fraction_orderings'][0];self.assertIsNone(ordering['phase_code']);self.assertEqual(ordering['ordered_team_ids'],['b','a']);self.assertEqual(ordering['official_conference_seeds_and_tiebreaks'],'NOT_INFERRED')
    def test_exact_phase_scope_team_and_season_are_never_merged(self):
        self.put('unknown',T0,self.totals());self.put('phase',T1,self.totals(80,4,'1'));self.put('scope',T1,self.totals(60,3,None,'TEAM','a'));self.put('other-team',T1,self.totals(40,2,None,'TEAM','b'))
        other=self.totals();other['player_season_totals'][0]['season_id']='other';other['team_season_totals']=[];self.put('other-season',T1,other,season='other')
        self.assertEqual(len(player_seasons(self.db,'p1')['records']),5)
        self.assertEqual(len(player_seasons(self.db,'p1',season_id='s',phase_code='1')['records']),1)
        self.assertEqual(len(season_summary(self.db,'s')['players']),4)
        with self.assertRaisesRegex(ValueError,'no truncation'):player_seasons(self.db,'p1',limit=1)
        with self.assertRaisesRegex(ValueError,'no truncation'):season_summary(self.db,'s',limit=1)
    def test_invalid_shooting_counts_and_negative_team_denominators_are_not_rates(self):
        facts=self.totals();facts['player_season_totals'][0].update(fg_made=61,fg_attempted=60);facts['team_season_totals'][0].update(wins=-1,losses=3)
        self.put('bad',T0,facts);value=season_summary(self.db,'s');self.assertIsNone(value['players'][0]['derived']['shooting_fractions']['field_goal_fraction']['value'])
        self.assertIsNone(value['teams'][0]['derived']['per_game_counts']['points']);self.assertIsNone(value['teams'][0]['derived_win_fraction'])
    def test_cli_unit_and_season_commands_honor_cutoff(self):
        self.put('old',T0,self.boxes());self.put('new',T1,self.boxes());self.put('totals',T1,self.totals())
        for args,key in [(['game',str(self.db),'g','--unit-id','old'],'selected_unit_id'),(['season',str(self.db),'s'],'teams'),(['player-seasons',str(self.db),'p1'],'records')]:
            result=subprocess.run([sys.executable,str(BASE/'cli.py'),*args,'--as-of',T0],capture_output=True,text=True,check=True);value=json.loads(result.stdout)['result']
            self.assertEqual(value[key],'old' if key=='selected_unit_id' else [])

if __name__=='__main__':unittest.main()
