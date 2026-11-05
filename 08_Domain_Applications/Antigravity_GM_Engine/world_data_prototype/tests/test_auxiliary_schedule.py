"""Auxiliary header checks never acquire Boxes or claim Box conservation."""
from copy import deepcopy
from pathlib import Path
import json,struct,sys,unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from test_schedule import ScheduleMemory
from schedule_reader import collect_schedule,schedule_facts,index_relationship
from organization_reader import reconcile_team,organization_payload
import test_organization as organization_fixture
FIXTURE=organization_fixture.FIXTURE
from readers import _module

class HeaderOnlyMemory(ScheduleMemory):
    def read(self,address,size,label):
        if 'FINAL_BOX:' in label or 'BOX_RECHECK:' in label:raise AssertionError('auxiliary source attempted a Box read')
        return super().read(address,size,label)

class AuxiliaryScheduleTests(unittest.TestCase):
    def test_played_header_is_available_with_zero_native_box_calls(self):
        memory=HeaderOnlyMemory();found=collect_schedule(memory,read_final_boxes=False)
        self.assertEqual(found['boxes'],{});self.assertEqual(found['reused'],{});self.assertEqual(found['manifest']['native_boxes_read'],0);self.assertEqual(found['manifest']['final_headers_without_box_reads'],1)
        self.assertIn('NO_BOX_REVALIDATION',found['manifest']['box_read_policy']);self.assertNotIn('CONSERVATION_PASSED',found['manifest']['entries'][0]['box_status'])
        full=_module('boxscore_decoder').BoxScoreDecoder.decode_game_header(memory.game);self.assertEqual(found['manifest']['entries'][0]['home_score'],full['home_score'])
        index_relationship(found,memory.context)
    def test_invalid_box_bytes_are_not_read_or_declared_verified_by_header_source(self):
        memory=HeaderOnlyMemory();memory.bank=b'\xff'*len(memory.bank);found=collect_schedule(memory,read_final_boxes=False)
        self.assertEqual(found['manifest']['errors'],[]);self.assertIn('BOX_NOT_READ_OR_REVALIDATED',found['manifest']['entries'][0]['box_status'])
        with self.assertRaisesRegex(ValueError,'not a Box acquisition'):schedule_facts(found,{'season_id':'s'},set())
    def test_changed_header_still_rejects_auxiliary_acquisition(self):
        with self.assertRaisesRegex(ValueError,'schedule changed'):collect_schedule(HeaderOnlyMemory(changed=True),read_final_boxes=False)
    def test_auxiliary_totals_reconciliation_uses_same_header_points_and_rejects_wrong_totals(self):
        games=(FIXTURE/'schedule-games.bin').read_bytes();decoder=_module('boxscore_decoder').BoxScoreDecoder;entries=[]
        for i in range(len(games)//60):
            game=decoder.decode_game_header(games[i*60:(i+1)*60]);entries.append({k:game[k] for k in ('status','home_team_id','away_team_id')})
        raw=(FIXTURE/'team-stats.bin').read_bytes();window={'games':games,'manifest':{'entries':entries},'boxes':{}};result=reconcile_team(raw,window,0)
        self.assertEqual(result['games'],result['values']['w']+result['values']['l'])
        changed=bytearray(raw);struct.pack_into('<H',changed,8,int.from_bytes(raw[8:10],'little')+2);struct.pack_into('<H',changed,12,int.from_bytes(raw[12:14],'little')+1)
        with self.assertRaisesRegex(ValueError,'schedule totals mismatch'):reconcile_team(changed,window,0)
    def test_optional_organization_calendar_is_its_own_typed_observation_not_stat_phase(self):
        fixture=organization_fixture.OrganizationTests();manifest=fixture.manifest();manifest['calendar']={'current_word_raw':1,'period_raw':2,'period_label':'REGULARSEASON'}
        payload=fixture.payload(manifest);self.assertEqual(payload['facts']['season_calendar_observations'][0]['period_label'],'REGULARSEASON')
        self.assertTrue(all(r['phase_code'] is None for r in payload['facts']['team_season_totals']))
    def test_invalid_read_policy_is_not_silently_truthy(self):
        for value in (None,0,'false'):
            with self.subTest(value=value),self.assertRaises(ValueError):collect_schedule(HeaderOnlyMemory(),read_final_boxes=value)

if __name__=='__main__':unittest.main()
