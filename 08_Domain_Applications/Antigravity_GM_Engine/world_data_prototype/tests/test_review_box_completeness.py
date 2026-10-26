"""F-02: schedule and single-game views share the exact strict Box contract."""
import sys,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
import test_competition_views as fixture_module
from query import schedule,game_box

class ReviewBoxCompletenessTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixture_module.CompetitionViewsTests('runTest');self.fixture.setUp();self.addCleanup(self.fixture.doCleanups);self.db=self.fixture.db
    def compare(self,facts):
        self.fixture.put('box','2026-10-24T00:00:00Z',facts);value=schedule(self.db)[0];single=game_box(self.db,'g')
        self.assertEqual(value['unit_id'],single['selected_unit_id']);self.assertEqual(value['box_coverage'],single['coverage'])
        self.assertEqual(value['home_points_derived'],single['scores']['derived_canonical_points']['HOME']);return value
    def assertRejected(self,facts):
        value=self.compare(facts);self.assertEqual(value['canonical_box_complete'],0);self.assertIsNone(value['home_points_derived']);self.assertEqual(value['score_provenance'],'NO_COMPLETE_QUALIFIED_SCORE')
    def test_equal_counts_wrong_person(self):
        facts=self.fixture.boxes();facts['native_box_observations'][0]['native_player_id']=999;self.assertRejected(facts)
    def test_equal_counts_canonical_null_points(self):
        facts=self.fixture.boxes();facts['player_game_boxes'][0]['points']=None;self.assertRejected(facts)
    def test_equal_counts_native_canonical_points_disagree(self):
        facts=self.fixture.boxes();facts['native_box_observations'][0]['points']=11;self.assertRejected(facts)
    def test_matching_source_is_complete(self):
        value=self.compare(self.fixture.boxes());self.assertEqual(value['canonical_box_complete'],1);self.assertEqual((value['home_points_derived'],value['away_points_derived']),(10,8))
    def test_same_count_unresolved_identity_is_rejected(self):
        facts=self.fixture.boxes();facts['native_box_observations'][0]['identity_status']='UNRESOLVED';self.assertRejected(facts)
    def test_later_native_only_partial_unit_does_not_borrow_old_state_or_boxes(self):
        self.fixture.put('old','2026-10-24T00:00:00Z',self.fixture.boxes());facts=self.fixture.boxes();self.fixture.put('partial','2026-10-25T00:00:00Z',{'native_box_observations':facts['native_box_observations']})
        value=schedule(self.db)[0];self.assertEqual(value['box_unit_id'],'partial');self.assertEqual(value['unit_id'],'old');self.assertEqual(value['status_code'],'2');self.assertEqual(value['canonical_box_complete'],0);self.assertIsNone(value['home_points_derived']);self.assertEqual(value['box_unit_id'],game_box(self.db,'g')['selected_unit_id'])
    def test_source_order_compares_utc_and_microseconds(self):
        self.fixture.put('local','2026-10-24T08:00:00+08:00',self.fixture.boxes());self.fixture.put('utc','2026-10-24T00:00:00.000001Z',self.fixture.boxes());self.assertEqual(schedule(self.db)[0]['unit_id'],'utc')

if __name__=='__main__':unittest.main()
