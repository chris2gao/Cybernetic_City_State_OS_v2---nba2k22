"""Verify delivered review evidence, without re-running candidate/game checks."""
import hashlib
import json
import pathlib
import subprocess

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[4]
RUN=HERE.parent
def command(args, cwd=ROOT):
    result=subprocess.run(args,cwd=cwd,capture_output=True)
    return {'exit_code':result.returncode,'stdout':result.stdout.decode('utf-8','replace').strip(),
            'stderr':result.stderr.decode('utf-8','replace').strip()}

pointer=json.loads((HERE/'REVIEW_EVIDENCE_POINTER.json').read_bytes())
bad=[name for name,expected in pointer['evidence_sha256'].items()
     if hashlib.sha256((RUN/name).read_bytes()).hexdigest()!=expected]
assert not bad,bad
findings=json.loads((RUN/'REVIEW_FINDINGS.json').read_bytes())
assert len(findings['findings'])==5
for f in findings['findings']:
    assert all(f[k] for k in ['finding_id','severity','locations','evidence','impact','minimum_fix','verification_criteria'])
    for location in f['locations']:
        if location['path'].endswith('GAME_UI_FIELD_CATALOG_V0.json') and location.get('json_pointer'):
            doc=json.loads((ROOT/location['path']).read_bytes())
            for key in location['json_pointer'].strip('/').split('/'):
                doc=doc[int(key)] if isinstance(doc,list) else doc[key]
            text=(ROOT/location['path']).read_text(encoding='utf-8').splitlines()
            assert doc['field_id'] in text[location['line']-1],location
mwu=command(['python','-X','utf8','-B','01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py',
             'artifact',str(HERE/'MINIMUM_WORK_UNIT_OUTPUT.json'),'--require-mwu'])
assert mwu['exit_code']==0,mwu
diff=command(['git','diff','--check'])
assert diff['exit_code']==0,diff
remote=command(['git','ls-remote','origin','refs/heads/master','refs/heads/task/world-source-model-seed-01'])
assert remote['exit_code']==0,remote
assert pointer['source_master_sha']+'\trefs/heads/master' in remote['stdout']
assert pointer['candidate_sha']+'\trefs/heads/task/world-source-model-seed-01' in remote['stdout']
main=pathlib.Path(r'E:\workspace\Cybernetic_City_State_OS_v2 - nba2k22')
main_head=command(['git','rev-parse','HEAD'],main)
assert main_head['stdout']==pointer['source_master_sha']
main_status=command(['git','status','--porcelain','--untracked-files=normal'],main)
assert not any(x[:2] != '??' for x in main_status['stdout'].splitlines())
report={'status':'PASS','review_scope_only':True,'hashed_evidence_count':len(pointer['evidence_sha256']),
        'evidence_hash_mismatches':bad,'finding_schema_and_locations':'PASS','mwu':mwu,'diff_check':diff,
        'fresh_remote_refs':remote,'main_head':main_head['stdout'],'main_status':main_status['stdout'],
        'limits':'No game checks, no candidate repair, no new managed verification run, no master integration.'}
(HERE/'final_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'PASS','evidence_files':len(pointer['evidence_sha256']),'finding_locations':'PASS','MWU':'PASS','remote_refs':'MATCH','main_tracked_files':'UNCHANGED'}))
