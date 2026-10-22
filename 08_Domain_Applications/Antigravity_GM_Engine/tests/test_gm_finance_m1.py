"""Focused arithmetic, scenario ownership and derived transaction acceptance."""
from copy import deepcopy
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from gm_core.finance_projection import project
from gm_core.finance_scenarios import compare
from gm_workbench.store import Store


def fixture():
    def player(pid, tid, amounts):
        c = {f'contract_year_{i+1}': {'value': v} for i, v in enumerate(amounts)}
        c.update({k: {'value': v} for k, v in dict(years_left_on_contract=3, original_contract_years=3,
                                                  contract_option=0, extension_length=0).items()})
        return dict(identity=pid, name=pid, team_id=tid, team=('A' if tid==1 else 'B'), contract=c)
    return dict(source_binding=dict(career_id='test', batch_id='B1', snapshot_id='S1', game_date='2021-12-12',
                                    data_updated_at='T1', publication_status='PUBLISHED_CURRENT', query_version='m0'),
        context={'season':'2021-2022'}, teams=[dict(team_id=1,team='A'),dict(team_id=2,team='B')],
        players=[player('p1',1,[100,120,140,0,0,0]), player('p2',2,[50,60,70,0,0,0])],
        picks=[dict(asset_id='pick1',team_id=1,owner='A',draft_year=2022,draft_round=1,original_team_id=1,trade_eligible=1)])


class FinanceTests(unittest.TestCase):
    def test_projection_partial_and_known_are_separate(self):
        data=fixture()
        missing=deepcopy(data['players'][0]); missing['identity']='p3'
        missing['contract']['contract_year_2']['value']=None
        missing['contract']['contract_option']['value']=2
        missing['contract']['extension_length']['value']=1
        data['players'].append(missing)
        r=project(data)
        y=r['teams'][0]['years'][1]
        self.assertEqual(y['projected_known_subtotal']['value'],120)
        self.assertIsNone(y['projected_salary_total']['value'])
        self.assertIsNone(y['known_salary_subtotal']['value'])
        self.assertEqual(y['projected_salary_total']['coverage'],'PARTIAL')
        self.assertEqual(len(y['conditional_salary']),1)
        self.assertEqual(r['horizon_seasons'],['2021-2022','2022-2023','2023-2024'])

    def test_certified_mapping_and_option_branches(self):
        data=fixture(); p=data['players'][0]
        p['season_mapping']={'1':{'season':'2021-2022','basis':'OBSERVED'}}
        p['contract']['contract_option']['value']=1
        r=project(data,assumptions={'player_overrides':{'p1':{'option_season':'2023-2024','option_decision':'DECLINE'}}})
        self.assertEqual(r['teams'][0]['years'][0]['known_salary_subtotal']['value'],100)
        e=r['teams'][0]['years'][2]['observed_slot_amounts'][0]
        self.assertEqual(e['option_branches'],{'EXERCISE':140,'DECLINE':0})
        self.assertEqual(e['amount'],0)

    def test_trade_preserves_both_year_vectors_and_empty_side(self):
        r=project(fixture())
        s=compare(r,dict(scenario_id='trade',kind='TRADE_OR_SIGNING',moves=[
            dict(type='TRADE_PLAYER',identity='p1',from_team_id=1,to_team_id=2),
            dict(type='TRADE_PICK',asset_id='pick1',from_team_id=1,to_team_id=2)]))
        for season in r['horizon_seasons']:
            deltas=[y['payroll_delta']['value'] for y in s['team_year_deltas'] if y['season']==season]
            self.assertEqual(sum(deltas),0)
        self.assertEqual(s['team_year_deltas'][0]['after']['value'],0)
        self.assertEqual(s['picks_after'][0]['team_id'],2)
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):
            compare(r,dict(scenario_id='bad',kind='TRADE_OR_SIGNING',moves=[
                dict(type='TRADE_PLAYER',identity='p1',from_team_id=1,to_team_id=2)]*2))

    def test_missing_transfer_remains_unknown_and_replacement_not_double_counted(self):
        data=fixture();data['players'][0]['contract']['contract_year_2']['value']=None
        r=project(data)
        s=compare(r,dict(scenario_id='replace',kind='TRADE_OR_SIGNING',moves=[
            dict(type='REPLACE_CURRENT',identity='p1',to_team_id=1,effective_season='2021-2022',salaries=[200,210,220])]))
        self.assertEqual([y['after']['value'] for y in s['team_year_deltas']],[200,210,220])
        self.assertIsNone(s['team_year_deltas'][1]['payroll_delta']['value'])
        self.assertEqual(s['executor_readiness'],'BLOCKED_EXECUTOR')

    def test_future_extension_preserves_current_and_new_signing_is_research(self):
        r=project(fixture())
        s=compare(r,dict(scenario_id='extend',kind='TRADE_OR_SIGNING',moves=[
            dict(type='EXTEND_FUTURE',identity='p1',to_team_id=1,effective_season='2022-2023',salaries=[160,170]),
            dict(type='SIGN_NEW',identity='candidate',name='Candidate',to_team_id=2,effective_season='2022-2023',salaries=[30,40])]))
        self.assertEqual([y['after']['value'] for y in s['team_year_deltas'] if y['team_id']==1],[100,160,170])
        self.assertEqual([y['after']['value'] for y in s['team_year_deltas'] if y['team_id']==2],[50,90,110])
        self.assertIn('FREE_AGENCY_AND_NATIVE_SIGNING_ELIGIBILITY_UNVERIFIED',s['unknown_reasons'])

    def test_draft_or_wrong_year_policy_and_cash_never_capacity(self):
        data=fixture();data['finance']=[{'team_id':1,'cash':4294967295}]
        for policy in ({'status':'DRAFT'}, {'status':'PLAYER_CONFIRMED','evidence_ref':'test',
            'applies_to':{'career_id':'test','seasons':['2020-2021'],'phases':['REGULAR']}}):
            r=project(data,policy=policy)
            self.assertEqual(r['teams'][0]['years'][0]['finance_eligibility']['status'],'UNKNOWN')
            self.assertIsNone(r['teams'][0]['years'][0]['signing_capacity']['value'])
            self.assertEqual(r['teams'][0]['years'][0]['projected_salary_total']['value'],100)

    def test_atomic_run_and_readonly_and_fact_path(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'gm_workbench.sqlite';r=project(fixture(),run_id='one')
            with Store(p) as s:
                bad=deepcopy(r);bad['teams'][0]['years'].append(bad['teams'][0]['years'][0])
                with self.assertRaises(sqlite3.IntegrityError):s.save_run(bad)
                self.assertEqual(s.list_runs('test'),[])
                s.save_run(r)
                with self.assertRaises(sqlite3.IntegrityError):s.save_run(r)
            with Store(p,readonly=True) as s:
                self.assertEqual(s.load_run('one')['run_id'],'one')
                with self.assertRaises(sqlite3.OperationalError):s.save_run(r)
            with self.assertRaisesRegex(ValueError,'NOT_FACTS'):Store(Path(td)/'saves'/'gm_workbench.sqlite')


if __name__=='__main__':unittest.main()
