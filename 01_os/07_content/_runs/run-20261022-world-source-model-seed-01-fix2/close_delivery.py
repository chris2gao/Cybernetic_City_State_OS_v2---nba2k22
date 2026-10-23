"""Persist the new candidate's exact evidence; never touch historical attempts."""
import hashlib,json,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[4]
HERE=pathlib.Path(__file__).resolve().parent
RUN=HERE.relative_to(ROOT).as_posix()+'/'
BASE='8cdbfaefbcb001c6ca0612017957c6414876eea4'
def write(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def main():
    external=pathlib.Path(sys.argv[1]).resolve()
    invocation=json.loads((external/'invocation_receipt.json').read_bytes())
    assert [x['mode'] for x in invocation['commands']]==['preflight','run','inspect']
    assert all(x['exit_code']==0 for x in invocation['commands'])
    candidate=invocation['candidate_sha']
    assert git('rev-parse','HEAD').decode().strip()==candidate,'close only the candidate just verified'
    target=HERE/'verification'/'candidate_attempt'
    assert not target.exists(),'preserve every previously archived attempt'
    shutil.copytree(external/'attempt',target)
    logs=HERE/'verification'/'invocations';logs.mkdir()
    for name in ['preflight.stdout','preflight.stderr','run.stdout','run.stderr','inspect.stdout','inspect.stderr','invocation_receipt.json']:
        shutil.copyfile(external/name,logs/name)
    hashes={p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(target.iterdir()) if p.is_file()}
    changed=git('diff','--name-only','-z',BASE,candidate).decode('utf-8').strip('\0').split('\0')
    # This code and the receipt added at closure are disclosed separately from the tested source.
    changes={'base_sha':BASE,'verified_candidate_sha':candidate,'verified_candidate_paths':changed,
       'closure_only_paths':[RUN+'close_delivery.py',RUN+'completion_pointer.json',RUN+'run.yml',RUN+'verification_receipt.json',RUN+'changed_paths.json',RUN+'repair_report.md',RUN+'verification/**'],
       'final_delivery_paths':'git diff --name-only -z '+BASE+' HEAD; final exact set is measured at publication'}
    write(HERE/'changed_paths.json',changes)
    receipt={'schema_version':'nba2k22.seed_fix2.execution_verification.v1','candidate_sha':candidate,
       'preflight_exit_code':0,'managed_run_exit_code':0,'managed_inspect_exit_code':0,
       'required_checks':9,'negative_mutations_rejected':16,'evidence_file_count':len(hashes),
       'strict_attempt_ref':RUN+'verification/candidate_attempt','sha256':hashes,
       'invocation_logs_ref':RUN+'verification/invocations','external_original':str(external),
       'original_B03_attempt':'PRESERVED_UNCHANGED; NOT_INSPECTED_OR_REPAIRED_BY_THIS_TASK',
       'source_candidate_vs_delivery':'Verification binds the committed repair SHA above. Following commits contain closure/evidence only; no business correction is inferred from them.',
       'independent_recheck':'NOT_RUN_SEPARATE_SESSION_REQUIRED','live_game':'NOT_RUN','Flash':'NOT_RUN','master':'NOT_MODIFIED'}
    write(HERE/'verification_receipt.json',receipt)
    pointer={'task_id':'WORLD-SOURCE-MODEL-SEED-01-FIX2','status':'candidate_ready_for_independent_review',
       'source_branch':'task/world-source-model-seed-01-fix2','review_base_sha':BASE,
       'original_candidate_sha':'142531f2d60813bce5b90254c5e347050c40b406','verified_repair_sha':candidate,
       'delivery_head_resolution':'Resolve the task branch current commit; final remote head is read back after ordinary non-force publication. Closure evidence is not a new business repair.',
       'findings':{x:'IMPLEMENTED_OFFLINE_CHECKED_PENDING_INDEPENDENT_RECHECK' for x in ['B-01','B-02','B-04','B-05']},
       'B-03':'UNCHANGED_OWNER_FOLLOWUP; original files/hashes preserved, no original Inspect pass claimed',
       'verification':{'receipt':RUN+'verification_receipt.json','plan':RUN+'verification_plan.json',
          'strict_attempt':RUN+'verification/candidate_attempt','new_run_exit_code':0,'new_inspect_exit_code':0,
          'scope':'nine declared offline checks plus sixteen rejecting mutations; no 888-field native certification'},
       'changed_paths':RUN+'changed_paths.json','semantic_changes':RUN+'semantic_change_manifest.json',
       'repair_report':RUN+'repair_report.md','execution_output':RUN+'execution_output.json',
       'independent_recheck':'PENDING_SEPARATE_SESSION','R00_planning_status':'TARGETED_QUEUE_OFFLINE_CHECKED; INDEPENDENT_RECHECK_PENDING; NOT_DISPATCHED',
       'not_run':['Flash activation','live game reads/writes','save load/switch/reset','production database operations','Save/Reload proof','master integration','new independent review'],
       'next_step':'Different-session targeted recheck of B-01/B-02/B-04/B-05; Human decides later Flash scope. Do not launch a third unbounded repair.'}
    write(HERE/'completion_pointer.json',pointer)
    run=HERE/'run.yml';text=run.read_text(encoding='utf-8').replace('lifecycle: candidate_pending_validation','lifecycle: candidate_ready_for_independent_review')
    run.write_bytes(text.encode('utf-8'))
    report=HERE/'repair_report.md'
    report.write_bytes(report.read_bytes()+('\n## 实际新候选验证\n\n候选 `'+candidate+'`：OS Preflight=0、Managed Run=0、Inspect=0，九项必需检查全部完成；16 个反向变异全部被拒绝。新 attempt 的 '+str(len(hashes))+' 个文件按原始字节归档于 `verification/candidate_attempt/`，外围调用日志单独保存，未混入严格 attempt。\n\n该结果只绑定上述修复提交；本次收尾提交保存验证证据和完成指针，不冒称原 B-03 attempt 已通过。最终分支 SHA 由发布后远端读回报告。\n').encode('utf-8'))
    print(json.dumps({'candidate':candidate,'archived_files':len(hashes),'checks':9,'status':pointer['status']}))
if __name__=='__main__':main()
