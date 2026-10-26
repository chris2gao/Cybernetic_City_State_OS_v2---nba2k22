"""Build bounded repair completion metadata from primary local evidence."""
import json
from pathlib import Path
import subprocess
import sys

root=Path.cwd();run=Path(__file__).resolve().parent;out=run/'08_结论';out.mkdir(exist_ok=True)
candidate='b847f717df6702fe6251872d64aed476ac707f6f'
app='08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
def load(p):return json.loads((run/p).read_text(encoding='utf-8'))
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert subprocess.run(['git','diff','--quiet',candidate,'--',app]).returncode==0
assert load('evidence/managed/result.json')['status']=='success'
assert load('evidence/real-copy-query-audit.json')['status']=='PASS'
assert load('evidence/snapshot-check.json')['status']=='PASS'
migration=load('evidence/v24-copy-migration-final.json')
assert migration['old_rows_preserved']==1470952 and migration['backfilled_identity_claims']==90455
prefix=run.relative_to(root).as_posix()
pointer={
 'packet_id':'nba2k22-world-data-review-fixes-01','status':'ready_for_independent_review',
 'delivery_scope':'F01_F02_F03_bounded_repairs_only_then_stop',
 'source_branch':'task/nba2k22-world-data-review-fixes-20261026',
 'source_base':'17ec1cea88c2bb6c36264792f70c94bef9a8bdb4','source_head':candidate,
 'tested_candidate':candidate,'functional_source_head':'9ac289de03be821d229f22e23fc6955bed8b74bb',
 'final_publication_receipt':'publication-receipt.json',
 'scope_and_authority':{'original_development_remains_closed':True,'master_integration':'NOT_PERFORMED','independent_review':'NOT_RUN','human_final_acceptance':'NOT_CLAIMED','next_task_started':False,'game_reads':0,'game_writes':0,'game_date_advance':0,'computer_use':0,'new_real_capture_units':0},
 'verification':{'managed_run':'success','managed_inspect':'success','exact_candidate':candidate,'plan_sha256':'9751ea4d323f17a55b4e9b5ca4f67305d493645c54478c8a6f430a65496c3887','regression_tests':329,'targeted_new_tests':28,'sqlite_smoke':'PASS','old_tables_compared':100,'old_rows_preserved':1470952,'old_v24_hash_unchanged':True,'all_old_values_except_version_header_unchanged':True,'new_catalog_rows_verified':14,'new_identity_claims':90455,'integrity':'ok','foreign_key_errors':0,'real_copy_annual_families_queried':4,'real_copy_box_parity_samples':12,'snapshot_parts_verified':4,'proof_limit':'Controlled adapter and fixture checks are not new Windows/game/UI/lifecycle acceptance.'},
 'database':{'schema_version':25,'strict_tables':101,'columns':1789,'total_rows_including_metadata':1561421,'successful_capture_units':42,'final_copy':'_runtime/migration/world-v25-final.sqlite','sha256':migration['target_sha256'],'original_v24_sha256':migration['source_sha256_after'],'original_binding_unchanged':True,'save_id':'nba2k22_test_01','native_save_file':'MyLEAGUE0003','snapshot_manifest':'snapshots/world-v25.snapshot.json','snapshot_does_not_embed_all_external_raw_artifacts':True},
 'entrypoints':{'handoff':prefix+'/NEXT_TASK_HANDOFF.md','closeout':prefix+'/CLOSEOUT.md','repair_contract':app+'/REVIEW_FIXES_F01_F02_F03.md','schema':app+'/schema.sql','field_dictionary':app+'/field_dictionary.json','cli':app+'/cli.py','source_coverage_maturity':'01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/06_执行/increment37/','managed_evidence':prefix+'/evidence/managed/'},
 'residual_limits':['No automatic full discovery of all same-year new facts; explicit bounded scene-evidenced requests required.','Stable source record/field identity does not prove cross-slot historical person/award equivalence.','Partial league award groups do not become complete canonical recipient groups.','Historical identity/shared references, coach year/phase, unresolved old Box participants, UI units/rounding and official eligibility remain at prior evidence maturity.'],
 'human_approved_deferrals':['Overall','Full lifecycle scenes supplied in a separate Human-triggered task','Full-season capacity and retention evaluation after a real complete season'],
 'unaccepted_scenarios':['postseason','offseason','draft and free agency','cross-season','100-season capacity','game writes'],
 'next_owner':'Human-organized independent reviewer',
 'next_development':'Separate full-lifecycle scenes and incremental acquisition task after review; no execution by this handoff.'}
write(out/'review_fixes_completion.yml',{'completion_pointer':pointer})
unit={'role':'execution',
 'work_performed_or_requested':'完成独立审核 F-01/F-02/F-03 定点修复，固定 v25 候选、原 v24 保持证明与下一任务交接，随后停止施工。',
 'implementation_or_review_method':'一次年度基线与受证据约束的字段级追加账本；四来源所选记录读取；schedule/Box共享严格判定；原receipt验证后事务回滚并独立隔离；精确提交受控验证及新副本逐值比较。',
 'supportability_rationale':'2022基线后新增MVP/冠军/FinalsMVP、重复及冻结冲突由28项针对性反例覆盖；329项回归及受控inspect通过；旧100表1470952行原值和原哈希保持，真实副本查询与快照校验另有原始证据。',
 'feasibility_rationale':'复用现有20族Reader、来源profile和SQLite工程，在独立fixture及新副本上完成；未连接游戏。自动未来事实发现、跨槽位历史身份、真实季后赛和容量均未被本任务证明，交Human后续场景处理。',
 'exact_result_or_candidate_ref':candidate,
 'verification_evidence':[prefix+'/evidence/managed/result.json',prefix+'/evidence/managed-evidence-copy.json',prefix+'/evidence/v24-copy-migration-final.json',prefix+'/evidence/real-copy-query-audit.json',prefix+'/evidence/snapshot-check.json'],
 'residual_risk_or_unproved_limits':pointer['residual_limits']+pointer['unaccepted_scenarios']}
write(out/'execution_result.yml',{'minimum_work_unit_output':unit})
validator=[sys.executable,'-X','utf8','01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py','artifact',str(out/'execution_result.yml'),'--require-mwu']
result=subprocess.run(validator,capture_output=True,text=True,encoding='utf-8')
write(out/'mwu-validation.json',{'command':validator,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'effect':'structural validation only; no independent acceptance'})
assert result.returncode==0,result.stdout+result.stderr
preflight=[sys.executable,'-X','utf8','01_os/06_execution/task_discipline/preflight/preflight_task_context.py','--packet',str(run/'任务包.yml'),'--repo-root',str(root),'--allow-dirty','--json']
result=subprocess.run(preflight,capture_output=True,text=True,encoding='utf-8')
write(out/'prepublication-preflight.json',{'command':preflight,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
assert result.returncode==0,result.stdout[-1200:]+result.stderr[-300:]
print(json.dumps({'status':'READY_FOR_INDEPENDENT_REVIEW','managed_candidate':candidate,'mwu_validator':0,'preflight':0,'application_tree_unchanged':True}))
