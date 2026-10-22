"""Focused development receipt using an existing static M02 snapshot; no game."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[1]


def main():
    root=ROOT/'_exports/m1_acceptance'/uuid4().hex
    root.mkdir(parents=True)
    career='mc_haliburton_2021'
    batch='2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2'
    common=['--career',career,'--workbench',str(root/'gm_workbench.sqlite')]
    def call(*args):
        p=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/gm_finance.py'),*args,*common],capture_output=True,text=True,encoding='utf-8')
        if p.returncode:
            raise RuntimeError(p.stdout[:300]+p.stderr[:300])
        return json.loads(p.stdout)
    run_id='M1_M02_DEVELOPMENT_'+root.name
    data=call('project','--batch',batch,'--base-season','2021-2022','--run',run_id)
    assert len(data['teams'])==30
    assert all(len(t['years'])==3 for t in data['teams'])
    samples={}
    for team in ('GSW','SAS','CLE'):
        r=call('show','--run',run_id,'--team',team)
        samples[team]=r['teams'][0]['years']
        assert all(y['signing_capacity'] is None for y in samples[team])
    contracts=call('show','--run',run_id,'--team','SAS','--season','2021-2022','--contracts','--limit','2')
    assert len(contracts['rows'])==2 and contracts['next_offset']==2
    scenario_file=root/'keep.json'
    scenario_file.write_text(json.dumps(dict(scenario_id='KEEP_DEVELOPMENT',kind='KEEP',rationale='Development CLI acceptance only')),encoding='utf-8')
    compared=call('compare','--run',run_id,'--scenario',str(scenario_file))
    assert len(compared['alternatives'])==3 and compared['approval_status']=='NOT_REQUESTED'
    shown=call('show','--run',run_id,'--scenario','KEEP_DEVELOPMENT','--team','SAS')
    assert len(shown['rows'])==3 and all(y['payroll_delta']['value']==0 for y in shown['rows'])
    exported=call('export','--run',run_id,'--output',str(root/'export'))
    assert (root/'export/summary.json').is_file() and (root/'export/summary.md').is_file()
    receipt=dict(status='PASS_LOCAL_STATIC_DEVELOPMENT',created_at=datetime.now(timezone.utc).isoformat(),
                 source_binding=data['source_binding'],team_count=30,years_per_team=3,
                 team_samples=samples,contract_drilldown='PASS_BOUNDED',keep_compare='PASS',
                 three_alternatives='PASS',export='PASS',web_acceptance='DEFERRED_BY_PLAYER_NOT_TESTED',
                 new_capture=False,game_writes=False,formal_gm=False)
    (root/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=receipt['status'],teams=30,team_years=90,receipt=str(root/'receipt.json')),ensure_ascii=False))


if __name__=='__main__':main()
