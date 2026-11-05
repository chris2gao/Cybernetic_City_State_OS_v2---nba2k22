"""Assemble truthful, unaccepted seven-stage candidates without inventing owner approval."""
import copy,hashlib,importlib.util,json,subprocess
from pathlib import Path
import yaml
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
CORE=Path('C:/Users/gk/.codex/worktrees/nba2k22-bic-os-core-08d8e534')
BASE='cdcb293f8a690725cf9168225cc2046ab0574b2b'
D='08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/'
RID='run-20261105-nba2k22-bic-os-integration-readiness-001'
def read(path):return json.loads((OUT/path).read_bytes())
def write(name,value):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
runnerpath=CORE/'01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py'
spec=importlib.util.spec_from_file_location('bic_current_core',runnerpath);runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
req=yaml.safe_load((OUT/'stage01/01_requirement_payload_CANDIDATE.yml').read_bytes())
original=read('sources/requirement/01b_requirement_result_A_candidate_v2.json')
diffs=[]
def compare(a,b,path):
 if type(a)!=type(b):diffs.append({'path':path,'before':a,'after':b});return
 if isinstance(a,dict):
  for key in sorted(set(a)|set(b)):
   if key not in a or key not in b:diffs.append({'path':path+'/'+key,'before':a.get(key),'after':b.get(key)})
   else:compare(a[key],b[key],path+'/'+key)
 elif isinstance(a,list):
  assert len(a)==len(b),path
  for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
 elif a!=b:diffs.append({'path':path,'before':a,'after':b})
for key in ('requirement_id','objective','success_criteria','constraints','consensus_A0','requirement_result_A'):
 compare(original[key],req[key],'/'+key)
for row in diffs:
 path=row['path']
 if path.startswith('/requirement_result_A/consensus_ref/'):
  row['classification']='Representation binding to normalized A0 digest/reference'
 elif '/known_facts/' in path and path.rsplit('/',1)[-1] in {'evidence_status','original_evidence_status','normalization_note'}:
  row['classification']='Conservative enum representation with lossless original status'
 else:raise ValueError('Unreviewed semantic change '+path)
mapping={'source_git_blob':'e16fdf6c4ef69b0a90b8c4abd3856617030a7ae4','source_confirmation_git_blob':'0deae6d2e841d6674e91a81cedd5a221f1f0647f','semantic_fields_checked':['requirement_id','objective','success_criteria','constraints','consensus_A0','requirement_result_A'],'differences':diffs,'all_other_semantic_fields_identical':True,'requirement_findings':runner.requirement_findings(req,2),'confirmation_boundary':'Original Human approval binds fixed JSON blob. Derived normalized confirmation fields carry those original references and are a representation mapping, not a new Human act. Formal owner acceptance of this mapping remains pending.','original_context_preserved':'sources/requirement/ contains the full immutable JSON, including metadata not projected into Core fields.'}
write('stage01/FIELD_EQUIVALENCE_MAP.json',mapping)
plan=read('sources/planning/02_evidence_CANDIDATE_v1.json');p2=copy.deepcopy(plan)
sources=[];resolution=[]
for s in plan['sources']:
 s=copy.deepcopy(s);ref={k:s[k] for k in ('repository','commit','path')}
 try:
  blob=git('rev-parse',ref['commit']+':'+ref['path']).decode().strip();raw=git('show',ref['commit']+':'+ref['path'])
  assert not s.get('blob_sha') or blob==s['blob_sha']
  resolution.append({'source_id':s['source_id'],'status':'RESOLVED','git_blob':blob,'sha256':hashlib.sha256(raw).hexdigest()})
 except (subprocess.CalledProcessError,AssertionError):resolution.append({'source_id':s['source_id'],'status':'UNRESOLVED_OR_BLOB_MISMATCH'})
 s['source_ref']=ref;s['publication_status']='MASTER_INCLUDED' if ref['commit']=='66f8f73f1a91597f4562b834c2acad332ad9de5b' else 'SOURCE_BRANCH_NOT_MASTER';sources.append(s)
additional=[('S-BIC-CODE',BASE,D+'bic_baseline.py'),('S-W2-CODE',BASE,D+'bic_diagnostics.py'),('S-W2-PLANS',BASE,D+'bic_plans.py'),('S-W1-TESTS','aec3dbaacd1d56b0c7cc1d40c2f70607493b9a4b','01_os/07_content/_runs/run-20261104-nba2k22-bic-series-remediation-001/verification_receipt.json'),('S-W2-TESTS',BASE,'01_os/07_content/_runs/run-20261105-nba2k22-bic-wave2-remediation-001/verification_receipt.json'),('S-W2-HISTORY',BASE,'01_os/07_content/_runs/run-20261105-nba2k22-bic-wave2-remediation-001/historical_cases.json'),('S-W1-REVIEW','3f27b421e0c1813dbfb890c4583c97e76dfd6f98','01_os/07_content/_runs/run-20261104-nba2k22-bic-batch1-series-review-001/BIC_BATCH1_DIFFERENCE_REVIEW_CLOSEOUT_v1.json'),('S-W2-REVIEW','13414798d5992336e28ae1df7e14bf17fbae6a04','01_os/07_content/_runs/run-20261105-nba2k22-bic-wave2-series-review-001/BIC_WAVE2_DIFFERENCE_REVIEW_CLOSEOUT_v1.json')]
for sid,commit,path in additional:
 try:raw=git('show',commit+':'+path)
 except subprocess.CalledProcessError:
  resolution.append({'source_id':sid,'status':'UNRESOLVED_PATH','commit':commit,'path':path});continue
 sources.append({'source_id':sid,'source_ref':{'repository':'chris2gao/Cybernetic_City_State_OS_v2---nba2k22','commit':commit,'path':path},'publication_status':'SOURCE_BRANCH_NOT_MASTER','sha256':hashlib.sha256(raw).hexdigest()})
 resolution.append({'source_id':sid,'status':'RESOLVED','sha256':hashlib.sha256(raw).hexdigest()})
p2['sources']=sources
for claim in p2['claims']:
 claim['result_item_ids']=claim.pop('linked_result_item_ids');claim['success_criterion_ids']=claim.pop('linked_success_criteria')
 claim['purpose']='FEASIBILITY' if claim['evidence_kind']=='STATIC_SOURCE' else 'BACKGROUND'
 if claim['evidence_kind']!='STATIC_SOURCE':claim['original_evidence_kind']=claim['evidence_kind'];claim['evidence_kind']='BACKGROUND_REFERENCE'
 claim['limits']+='; historical preparatory evidence preserved; not current live-game proof or full BIC completion.'
allitems={x['result_item_id'] for x in req['requirement_result_A']['result_items']};covered={item for c in p2['claims'] for item in c['result_item_ids']}
if allitems-covered:
 p2['claims'].append({'claim_id':'E-FULL-SCOPE-UNKNOWN','statement':'Remaining approved full-BIC outcomes are not delivered by these offline batches','source_ids':['S-A-APPROVED'],'evidence_kind':'UNKNOWN','purpose':'BACKGROUND','limits':'No full BIC-vs-BIC competition or Native mechanism-effect acceptance','result_item_ids':sorted(allitems-covered),'success_criterion_ids':[],'closure_evidence':'Separately authorize and deliver remaining BIC work and obtain independent mode-specific evidence.'})
p2['claims'].extend([{'claim_id':'E-OFFLINE-W1-W2','statement':'Reviewed offline baseline/diagnosis/plan implementations and prior regression archives exist','source_ids':['S-BIC-CODE','S-W2-CODE','S-W2-PLANS','S-W2-TESTS'],'evidence_kind':'OFFLINE_TEST','purpose':'FEASIBILITY','limits':'Prior tests predate present technical freeze; code-level feasibility only; no live or full-BIC assertion','result_item_ids':sorted(covered),'success_criterion_ids':['SC-01','SC-02','SC-07']},{'claim_id':'E-INDEPENDENT-REVIEW','statement':'Two independently authored difference-review closeouts are fixed in separate refs','source_ids':['S-W1-REVIEW','S-W2-REVIEW'],'evidence_kind':'INDEPENDENT_REVIEW','purpose':'FEASIBILITY','limits':'Offline code review only; not Human OS owner acceptance or full BIC completion','result_item_ids':sorted(covered),'success_criterion_ids':['SC-01','SC-02','SC-07']}])
p2['completion']={'feasibility_basis_complete':False,'conflicts_resolved_or_durable':True,'scope':'OFFLINE_SUBSCOPE_CANDIDATE_ONLY_FULL_BIC_FEASIBILITY_NOT_COMPLETE'}
p2['status']='CANDIDATE_NOT_FORMAL_OS_PASS';p2['source_resolution']=resolution
write('SOURCE_RESOLUTION.json',resolution)
p3=read('sources/planning/03_result_B_CANDIDATE_v2.json')
for c in p3['claims']:
 c['result_claim_id']=c['id'];c['evidence_claim_ids']=sorted(set(c['evidence_claim_ids']+['E-OFFLINE-W1-W2','E-INDEPENDENT-REVIEW']));c['actual_delivery']='OFFLINE_PRIMITIVE_IMPLEMENTED_NOT_FULL_A_SATISFACTION'
p3['claims'].extend([{'result_claim_id':'B-W2-DIAGNOSIS','outcome':'Source-qualified player/team diagnosis with R01-R04 conservative guards','evidence_claim_ids':['E-OFFLINE-W1-W2','E-INDEPENDENT-REVIEW'],'source_commit':BASE,'scope':'OFFLINE_ONLY'},{'result_claim_id':'B-W2-PLANS','outcome':'Offline plan mapping to pinned Native catalog; no current authenticated Getter; execute false','evidence_claim_ids':['E-OFFLINE-W1-W2','E-INDEPENDENT-REVIEW'],'source_commit':BASE,'scope':'OFFLINE_ONLY'}])
oldmapping=p3['requirement_satisfaction'];p3['original_requirement_satisfaction']=oldmapping
p3['requirement_satisfaction']=[{'criterion_id':c['criterion_id'],'result_claim_ids':sorted({claim['id'] for claim in p3['claims'] if c['criterion_id'] in claim.get('sc',[])}),'status':'NOT_DELIVERED' if c['criterion_id']=='SC-05' else 'PARTIAL_OFFLINE_PRIMITIVES_ONLY','full_criterion_satisfied':False} for c in req['success_criteria']]
p3['full_BIC_success_criteria_satisfied_by_this_batch']=False;p3['formal_completion']=False
p4=read('sources/planning/04_tests_CANDIDATE_v2.json');p4['scope']='Wave1/Wave2 reviewed offline subscope; retained 15 original design scenarios, plus prospective technical integration package';p4['technical_freeze_ref']='../TECHNICAL_TEST_FREEZE.json';p4['frozen']=False;p4['freeze_authorization_ref']=None;p4['test_package_sha256']=runner.normalized_sha256(p4['tests']);p4['formal_stage04_acceptance']='PENDING_OWNER_FREEZE_APPROVAL';p4['prior_test_runs']='41 and 65 archived results are prior evidence, not post-freeze results'
p5=read('sources/planning/05_steps_CANDIDATE_v2.json')
for s in p5['steps']:
 s['exits']=[x.lower() for x in s['exits']];s['actual_delivery_status']='OFFLINE_IMPLEMENTATION_REVIEWED_NOT_FORMAL_STAGE05_ACCEPTANCE';s['engineering_authority']='Human offline engineering authorization overrides prior P0-only restriction; does not approve OS gates'
p5['wave2_steps']=[{'step_id':'W2-DIAGNOSE','depends_on':['S01','S02'],'module':D+'bic_diagnostics.py','result_claim_ids':['B-W2-DIAGNOSIS'],'test_ids':['OFFLINE-06','OFFLINE-07']},{'step_id':'W2-PLAN','depends_on':['W2-DIAGNOSE'],'module':D+'bic_plans.py','result_claim_ids':['B-W2-PLANS'],'test_ids':['OFFLINE-06','OFFLINE-07']}]
p6={'executor_role':'execution','allowed_write_paths':[D],'actual_write_paths':[D+'bic_baseline.py',D+'bic_experiments.py',D+'bic_diagnostics.py',D+'bic_plans.py',D+'observation_scope.py'],'unauthorized_write_attempts':[],'frozen_test_package_sha256':None,'attempts':[],'reviewed_code_commit':BASE,'scope':'OFFLINE_W1_W2_ONLY','status':'HISTORICAL_IMPLEMENTATION_EVIDENCE_NOT_RECONSTRUCTED_FORMAL_EXECUTION','performance_limit':'Five warm synthetic diagnostic calls exclude baseline/database IO; no whole-database performance acceptance','formal_execution_against_approved_frozen_package':False}
p7={'reviewer_role':'independent_review','verdict':'PENDING_OS_ACCEPTANCE','test_results':[],'implementation_claims':[],'completion':False,'upstream_invalidation':None,'independent_code_reviews':[{'commit':row[1],'path':row[2]} for row in additional if 'REVIEW' in row[0]],'scope':'OFFLINE_W1_W2_ONLY','full_BIC_completion':False,'post_freeze_integration_results':'PENDING_WORKSTREAM_B_RECEIPT'}
payloads=[req,p2,p3,p4,p5,p6,p7]
contract=yaml.safe_load((CORE/runner.CONTRACT_PATH).read_bytes());entries=[];previous={}
preds=[[],[0],[0,1],[0,1,2],[3],[3,4],[2,3,5]]
runroot=OUT/'stage_candidates';runroot.mkdir(exist_ok=True)
schemaresults=[]
for i,(stage,payload) in enumerate(zip(contract['stage_order'],payloads)):
 sid=stage['stage_id'];schema=yaml.safe_load((CORE/stage['schema_path']).read_bytes())
 missing=[f for f in schema['payload_required_fields'] if f not in payload]
 schemaresults.append({'stage_id':sid,'payload_required_missing':missing,'status':'CANDIDATE_NOT_ACCEPTED'})
 art={'schema_version':'citystate.workflow.artifact.v1','run_id':RID,'stage_id':sid,'artifact_kind':stage['artifact_kind'],'artifact_version':2 if i==0 else 1,'status':'candidate_pending_owner_acceptance','input_refs':[previous[j] for j in preds[i]],'stage_control':{'action_id':f'OS-STAGE-{i+1:02d}','current_model_ref':None,'deliberation_receipt_ref':None,'plan_acceptance':None,'completion_acceptance':None,'status':'NOT_GRANTED_CANDIDATE_ONLY'},'deliberation_receipt':{'receipt_status':'NOT_GRANTED','reason':'No fabricated stage disposition; actual owner acceptance history required'},'payload':payload}
 name=stage['artifact_filename'];raw=yaml.safe_dump(art,allow_unicode=True,sort_keys=False,width=4096).encode();(runroot/name).write_bytes(raw)
 entry={'stage_id':sid,'path':name,'artifact_version':art['artifact_version'],'sha256':hashlib.sha256(raw).hexdigest()};entries.append(entry);previous[i]=entry.copy()
manifest={'schema_version':'citystate.workflow.run_manifest.v1','run_id':RID,'workflow_id':contract['workflow_id'],'workflow_version':1,'route':'normal','deliberation_default_route':'dormant','completion_expected':True,'artifacts':entries,'candidate_only':True,'full_BIC_completion_claimed':False}
(runroot/'manifest.yml').write_text(yaml.safe_dump(manifest,sort_keys=False),encoding='utf-8',newline='\n')
(runroot/'run.yml').write_text(yaml.safe_dump({'task_id':'NBA2K22-BIC-W1-W2-OS-INTEGRATION-READINESS-20261105-001','lifecycle':'candidate_ready_for_independent_review','ownership':'domain','purpose':'Unaccepted OS candidates; completion_expected is runner input expectation, never completion status'}),encoding='utf-8',newline='\n')
write('PAYLOAD_CHECKS.json',{'stage01_requirement_findings':runner.requirement_findings(req,2),'stage02_evidence_findings':runner.evidence_findings(p2,req),'schema_required_fields':schemaresults,'formal_acceptance':False})
print(json.dumps({'stage1_findings':mapping['requirement_findings'],'equivalence_differences':len(diffs),'source_resolutions':len(resolution),'unresolved':[r for r in resolution if r['status']!='RESOLVED'],'stage_payloads':len(entries),'stage2_findings':runner.evidence_findings(p2,req)}))
