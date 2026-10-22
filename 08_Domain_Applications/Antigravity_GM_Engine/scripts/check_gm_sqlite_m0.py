"""Local snapshot/CLI smoke verification, not Web-session acceptance or a GM round."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--career',required=True)
    p.add_argument('--query-root',type=Path,default=ROOT/'database/query_snapshots')
    p.add_argument('--output',type=Path,default=ROOT/'_exports/dev10_m0/local_cli_receipt.json')
    a=p.parse_args()
    if not a.output.resolve().is_relative_to(ROOT/'_exports'):
        p.error('Local verification receipts must stay under _exports')
    common=[sys.executable,'-B',str(ROOT/'scripts/gm_data_query.py'),'--career',a.career,'--query-root',str(a.query_root)]
    checks=[]
    binding=None
    cases=[('status',['status']),
           ('SAS_roster',['team','roster','--team','SAS','--limit','20']),
           ('SAS_staff_8_roles',['staff','team','--team','SAS','--limit','20']),
           ('Popovich',['staff','search','--name','Popovich']),
           ('candidates',['staff','search','--job','HEAD_COACH','--candidates','--limit','3']),
           ('1984_Jordan',['player','search','--scope','pool','--name','Michael Jordan','--draft-year','1984','--historical-rookie']),
           ('unrostered',['player','search','--scope','pool','--unrostered','--limit','3']),
           ('contracts_attributes',['team','roster','--team','SAS','--fields','identity,name,salary,contract,attributes','--limit','1']),
           ('coaching_19',['coaching','team','--team','SAS','--fields','team,coach,values']),
           ('opponent_18',['coaching','opponent','--team','SAS','--opponent','GSW']),
           ('picks',['picks','team','--team','SAS','--trade-eligible']),
           ('team_aggregate',['sql','--select','SELECT team,COUNT(*) AS player_count,SUM(salary) AS roster_salary FROM q_players GROUP BY team ORDER BY team','--limit','50']),
           ('roster_count',['sql','--select','SELECT COUNT(*) AS n FROM q_players']),
           ('finance_semantics',['finance','semantics']),
           ('cash_issues',['issues']),
           ('read_only_rejection',['sql','--select',"UPDATE q_teams SET team='FORBIDDEN'"])]
    for name,args in cases:
        result=subprocess.run(common+args,capture_output=True,text=True,encoding='utf-8',timeout=15)
        obj=json.loads(result.stdout)
        if name=='read_only_rejection':
            assert obj['status']=='INVALID_SQL',obj
            checks.append(dict(check=name,passed=True,expected_rejection=obj['status']))
            continue
        assert result.returncode==0 and obj['status'] in ('OK','QUERYABLE_LOCAL','RESULT_LIMIT_REACHED'),(name,obj)
        if binding is None:binding=obj['source_binding']
        assert obj['source_binding']==binding,name
        assert len(result.stdout.encode('utf-8'))<=20000,name
        if name=='SAS_staff_8_roles':assert obj['row_count']==8
        if name=='coaching_19':assert len(obj['rows'][0]['values'])==19
        if name=='opponent_18':assert len(obj['rows'][0]['values'])==18
        if name=='team_aggregate':assert obj['row_count']==30
        if name=='1984_Jordan':assert obj['row_count']>=1
        if name=='contracts_attributes':assert len(obj['rows'][0]['attributes'])==55
        item=dict(check=name,passed=True,row_count=obj['row_count'],truncated=obj['truncated'])
        if name in ('cash_issues','roster_count'):item['minimal_evidence']=obj['rows']
        checks.append(item)
    receipt=dict(schema_version=1,task='DEV-20261018-10_V2_M0',status='IMPLEMENTED_LOCAL',
                 verified_at=datetime.now(timezone.utc).isoformat(),source_binding=binding,checks=checks,
                 no_game_process=True,no_capture_or_publication=True,
                 three_web_roles={r:dict(status='DEFERRED_BY_PLAYER_NOT_TESTED',blocking_delivery=False)
                                  for r in ('WEB_ANALYTICS','WEB_GM','WEB_DEVELOPMENT')})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(status='LOCAL_CLI_PASS',checks=len(checks),source_binding=binding),ensure_ascii=False))


if __name__=='__main__':main()
