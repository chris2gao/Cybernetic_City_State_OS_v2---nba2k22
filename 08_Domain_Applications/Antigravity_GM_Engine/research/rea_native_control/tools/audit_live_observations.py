"""Audit retained real-game observations; never connect to or alter the game."""
import hashlib,json,sys,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[5]
run=root/'01_os/07_content/_runs/run-20261027-nba2k22-myleague-native-control-validation-001'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def case(n,c):return load(run/f'07_测试执行/batch-{n}/cases/{c}.result.json')['result']['native_result']
def details(n,c):return case(n,c)['details']
def data(n,c):return details(n,c)['data']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
integrity=[]
for n in ['01','02','03','04']:
    folder=run/f'07_测试执行/batch-{n}'
    finished=load(folder/'launcher-finished.json');assert finished['exit_code']==0
    retained=load(folder/'manifest.json');prepared=run/f'03_方案设计/prepared-experiment-batch-{n}'
    batch=load(prepared/'batch.json');calls=0
    batch_blob=subprocess.check_output(['git','show','HEAD:'+(prepared/'batch.json').relative_to(root).as_posix()],cwd=root)
    assert hashlib.sha256(batch_blob).hexdigest()==sha(prepared/'batch.json'),'Repository batch bytes must match executed manifest'
    for row in retained['files']:
        assert sha(folder/row['path'])==row['sha256'],row['path']
    for c in batch['cases']:
        actual=load(folder/f'cases/{c["case_id"]}.result.json')
        assert actual['batch_sha256']==sha(prepared/'batch.json')
        assert actual['result']['original_request']==c['parameters']
        assert sha(folder/f'raw/{c["case_id"]}/program.js')==c['script_sha256']
        program_blob=subprocess.check_output(['git','show','HEAD:'+(prepared/c['script']).relative_to(root).as_posix()],cwd=root)
        assert hashlib.sha256(program_blob).hexdigest()==c['script_sha256'],'Repository program bytes must match executed script'
        native=actual['result']['native_result'];assert native['first_hand_game_calls']<=c['maximum_game_calls']
        calls+=native['first_hand_game_calls']
    assert all(s['cleanup_error'] is None and not s['messages_truncated'] and s['message_errors']==0 for s in retained['sessions'])
    integrity.append({'batch':n,'sessions':len(retained['sessions']),'native_calls':calls,'all_retained_hashes_match':True,'exact_scripts_and_inputs_match':True,'launcher_exit_code':0,'finished_utc':finished['finished_utc']})
before=details('03','scout_before');after=details('03','scout_after')
goal=after['goals'][0]
scout_checks={'native_return_received':case('03','scout_set_existing')['outcome']=='NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED','same_team':before['team_id']==after['team_id']==20,'goal_count_unchanged':before['num_existing_goals']==after['num_existing_goals']==3,'exact_target':goal['focus_type_raw']==2 and goal['num_targets_raw']==1 and [t['player_id'] for t in goal['targets']]==[33143],'real_before_after_change':before['goals'][0]!=goal,'other_goals_unchanged':before['goals'][1:]==after['goals'][1:],'trips_unchanged':before['remaining_trips_raw']==after['remaining_trips_raw']==7,'progress_unchanged_from_batch02':details('02','progress_after')==details('03','progress_after')}
assert all(scout_checks.values()),scout_checks
trade=case('04','trade_agreed');checks={'native_return_received':trade['outcome']=='NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED' and trade['details']['process_return']==1,'canaries_intact':trade['details']['private_canaries_intact'],'full_check_not_called_by_bridge':trade['details']['full_check_called'] is False}
for label,out_uid,in_uid in [('ind',7239,7716),('other',7716,7239)]:
    old=data('04',label+'_before');new=data('04',label+'_after')
    oldids={r['player_id'] for r in old['players']};newids={r['player_id'] for r in new['players']}
    checks[label+'_exact_roster_swap']=newids==oldids-{out_uid}|{in_uid}
    checks[label+'_count_unchanged']=old['roster_count']==new['roster_count']==len(new['players'])
    checks[label+'_roster_identity_links']=all(r['current_team_matches'] and r['contract_team_matches'] for r in new['players'])
salary={}
for name,uid,oldteam,newteam in [('brogdon',7239,20,1),('donte',7716,1,20)]:
    old=data('04',name+'_before');new=data('04',name+'_after')
    checks[name+'_uid_unchanged']=old['player_id']==new['player_id']==uid
    checks[name+'_both_owner_links_transferred']=old['current_team_id']==old['contract_team_id']==oldteam and new['current_team_id']==new['contract_team_id']==newteam
    wagekeys=['contract_year_'+str(i) for i in range(1,7)]
    checks[name+'_all_six_wages_unchanged']=all(old['contract_raw'][k]==new['contract_raw'][k] for k in wagekeys)
    salary[name]=old['contract_raw']['contract_year_1']
checks['requested_salary_mismatch']=salary['brogdon']>salary['donte']
assert all(checks.values()),checks
raw=load(run/'07_测试执行/batch-04/raw/trade_agreed/evidence.json')
stages=[m.get('payload',{}) for m in raw['normalized_result']['messages'] if m.get('type')=='send']
called=[m['binding_id'] for m in stages if m.get('kind')=='native-call-stage' and m.get('stage')=='STARTED']
assert called==['trade.add_player','trade.add_player','trade.context','trade.process'],called
result={'source_kind':'RETAINED_REAL_GAME_OBSERVATION_AUDIT','game_access_by_audit':False,'independent_reviewer':False,'integrity':integrity,'coach_status':'REAL_NATIVE_EFFECT_VERIFIED_SUBSET','scout_existing_goal':{'status':'REAL_NATIVE_EFFECT_VERIFIED_GOAL_RECORD_ONLY','checks':scout_checks,'exact_input':{'team_id':20,'goal_index':0,'player_ids':[33143]},'native_evidence_id':case('03','scout_set_existing')['evidence_id'],'independent_read_evidence_id':case('03','scout_after')['evidence_id'],'trip_consumer_cache_and_report':'NOT_VERIFIED'},'trade':{'status':'REAL_NATIVE_EFFECT_VERIFIED_EXACT_PACKAGE','checks':checks,'external_call_sequence':called,'exact_input':{'team_a':20,'team_b':1,'players_a':[7239],'players_b':[7716],'picks_a':[],'picks_b':[]},'salary_year1_raw':salary,'native_evidence_id':trade['evidence_id'],'independent_after_ids':[case('04',c)['evidence_id'] for c in ['ind_after','other_after','brogdon_after','donte_after']],'restored':False},'UI':'NOT_OBSERVED_THIS_TASK','save_reload':'NOT_STUDIED','game_automatic_save':'NOT_OBSERVED','native_calls_total':sum(x['native_calls'] for x in integrity),'attach_sessions_total':sum(x['sessions'] for x in integrity),'session_note':'REA normalized state snapshot says running; complete CLI and administrator launcher exit0 observed; no cleanup_error. Not represented as a DETACHED receipt.'}
# Prepare the final source for these exact inputs offline; no runtime backend is supplied.
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from facade import NativeControlFacade
from contracts import NativeActionRequest
facade=NativeControlFacade()
comparisons=[]
for n in ['01','02','03','04']:
    folder=run/f'03_方案设计/prepared-experiment-batch-{n}'
    for c in load(folder/'batch.json')['cases']:
        final=facade.render(NativeActionRequest(c['action_id'],c['parameters'],c['case_id']))
        same=final.script==(folder/c['script']).read_text(encoding='utf-8')
        expected_reader_extension=n=='01' and c['case_id']=='team_read'
        assert same or expected_reader_extension,(n,c['case_id'])
        comparisons.append({'batch':n,'case_id':c['case_id'],'identical_script':same,'expected_read_only_salary_column_extension':expected_reader_extension and not same})
result['final_source_script_comparison']=comparisons
out=run/'07_测试执行/LIVE_OUTCOME_AUDIT.json'
if '--check' in sys.argv:
    assert load(out)==result,'Retained audit must match actual observations'
else:
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'trade':result['trade']['status'],'scout':result['scout_existing_goal']['status'],'salary':salary,'native_calls_total':result['native_calls_total'],'attach_sessions_total':result['attach_sessions_total'],'raw_integrity_verified':True}))
