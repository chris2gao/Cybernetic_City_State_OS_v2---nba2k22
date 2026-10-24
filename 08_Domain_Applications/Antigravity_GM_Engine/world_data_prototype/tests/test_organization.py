"""Actual organization-source fixtures and typed semantics, not fresh live proof."""
import copy,hashlib,json,struct,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from organization_reader import organization_payload,registered_fields,coach_values,verify_staff_assignment,reconcile_team
from engine import create_database,connect,ingest_capture
from query import team_card,staff_card
from readers import _module
FIXTURE=BASE/'tests/fixtures/organization_20261024'


class OrganizationTests(unittest.TestCase):
    def manifest(self):return json.loads((FIXTURE/'manifest.json').read_bytes())
    def payload(self,manifest=None,token='fixture'):
        source=json.loads((FIXTURE/'source_manifest.json').read_bytes())
        artifacts=[{'sha256':v,'payload_kind':'ACTUAL_CURATED_ORGANIZATION_SOURCE','payload_ref':k} for k,v in source['files'].items()]
        return organization_payload({'save_id':'fixture','native_save_filename':'MyLEAGUE0003'},manifest or self.manifest(),artifacts,'2026-10-24T00:00:00Z',token)

    def test_actual_families_roundtrip_queries_and_unsigned_finance(self):
        m=self.manifest();m['teams'][0]['finance']['cash_raw']=0xFFFFFFFF
        p=self.payload(m)
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,p)
            team=team_card(db,'team:native:0');staff=staff_card(db,'staff:native:70')
            self.assertEqual(team['families']['team_finance_observations']['cash_raw']['value'],4294967295)
            self.assertEqual(team['families']['team_finance_observations']['cap_space_raw']['status'],'NOT_OBSERVED')
            self.assertEqual(len(team['playbook_slots']),68);self.assertEqual(len(team['assigned_staff']),1)
            self.assertEqual(staff['staff']['display_name'],'Doc Rivers')
            self.assertEqual(len(staff['families']['staff_skill_observations']),7)
            self.assertNotIn('potential',json.dumps({'team':team,'staff':staff}).lower())
            self.assertNotIn('address',json.dumps({'team':team,'staff':staff}).lower())
            with connect(db,True) as c:self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())

    def test_native_four_bit_system_not_truncated_to_old_staff_registry(self):
        raw=bytearray((FIXTURE/'staff.bin').read_bytes());raw[266]=(raw[266]&0xF0)|9
        self.assertEqual(coach_values(raw)['preferred_system_raw'],9)
        self.assertEqual(registered_fields(raw,'STAFF')['preferred_system'],1)

    def test_wrong_role_or_missing_reciprocal_pointer_rejects(self):
        m=self.manifest();raw=(FIXTURE/'staff.bin').read_bytes();team=m['teams'][0]['address']
        verify_staff_assignment(raw,team,0)
        with self.assertRaisesRegex(ValueError,'reciprocal'):verify_staff_assignment(raw,team,1)
        changed=bytearray(raw);struct.pack_into('<Q',changed,0x18,0)
        with self.assertRaisesRegex(ValueError,'reciprocal'):verify_staff_assignment(changed,team,0)

    def test_correct_scoring_formula_cannot_hide_wrong_current_team_total(self):
        games=(FIXTURE/'schedule-games.bin').read_bytes();decoder=_module('boxscore_decoder').BoxScoreDecoder
        entries=[]
        for i in range(len(games)//60):
            g=decoder.decode_game_header(games[i*60:(i+1)*60]);entries.append({k:g[k] for k in ('status','home_team_id','away_team_id')})
        season={'games':games,'manifest':{'entries':entries}}
        raw=(FIXTURE/'team-stats.bin').read_bytes();self.assertEqual(reconcile_team(raw,season,0)['season_year'],2022)
        changed=bytearray(raw);struct.pack_into('<H',changed,8,int.from_bytes(raw[8:10],'little')+2)
        struct.pack_into('<H',changed,12,int.from_bytes(raw[12:14],'little')+1)
        with self.assertRaisesRegex(ValueError,'schedule totals mismatch'):reconcile_team(changed,season,0)

    def test_duplicate_staff_ids_and_conflicting_person_identity_do_not_merge(self):
        m=self.manifest();m['staff'].append(copy.deepcopy(m['staff'][0]))
        with self.assertRaisesRegex(ValueError,'identity not unique'):self.payload(m)
        with TemporaryDirectory() as tmp:
            db=Path(tmp)/'world.sqlite';create_database(db,'fixture')
            with connect(db) as c:ingest_capture(c,self.payload())
            m=self.manifest();m['staff'][0]['first_name']='Different Person'
            with connect(db) as c:
                with self.assertRaisesRegex(ValueError,'identity collision'):ingest_capture(c,self.payload(m,'changed'))
            with connect(db,True) as c:self.assertEqual(c.execute('SELECT count(*) FROM capture_units').fetchone()[0],1)


if __name__=='__main__':unittest.main()
