"""Check the confirmed requirement payload and pending stage owner state."""
import hashlib,importlib.util,json,subprocess
from pathlib import Path
import yaml
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
CORE=Path('C:/Users/gk/.codex/worktrees/nba2k22-bic-os-core-08d8e534')
RUNNER='01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py'
spec=importlib.util.spec_from_file_location('scoped_check_core',CORE/RUNNER);core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
assert subprocess.check_output(['git','-C',str(CORE),'rev-parse','HEAD']).decode().strip()=='08d8e534a3438269aa7d7eb1b080ab11c172f462'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(path):return json.loads((OUT/path).read_bytes())
manifest=yaml.safe_load((OUT/'manifest.yml').read_bytes());assert len(manifest['artifacts'])==7
payloads=[]
for item in manifest['artifacts']:
    p=OUT/item['path'];assert digest(p)==item['sha256']
    art=yaml.safe_load(p.read_bytes());payloads.append(art['payload'])
    assert art['status']=='candidate_pending_owner_acceptance'
    assert all(value is None for value in art['stage_control'].values())
    for ref in art['input_refs']:assert digest(OUT/ref['path'])==ref['sha256']
req,p2,p3,p4,p5,p6,p7=payloads
actual_req=core.requirement_findings(req,1);actual_evidence=core.evidence_findings(p2,req)
assert actual_req==[]
assert actual_evidence==[]
assert req['Human_confirmation']['confirmed'] is True
assert req['consensus_Human_confirmation']['confirmed'] is True
binding=read('NORMALIZED_BINDINGS.json')
assert req['requirement_result_A']['consensus_ref']=={
    'model_id':req['consensus_A0']['model_id'],'version':req['consensus_A0']['version'],
    'sha256':binding['child_A0_sha256'],'confirmation_ref':binding['child_A0_confirmation_ref']}
assert req['consensus_Human_confirmation']['confirmation_ref']==binding['child_A0_confirmation_ref']
assert req['Human_confirmation']['confirmation_ref']==binding['child_A_confirmation_ref']
assert binding['child_A_confirmation_ref']!=binding['child_A0_confirmation_ref']
for source in (binding['child_A0_approval_source'],binding['child_A_approval_source']):
    ref=source['commit']+':'+source['path']
    raw=subprocess.check_output(['git','show',ref],cwd=ROOT)
    assert raw==(OUT/source['copy']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==source['sha256']
    assert subprocess.check_output(['git','rev-parse',ref],cwd=ROOT).decode().strip()==source['git_blob']
assert req['Human_confirmation']['content_sha256']==binding['child_A_payload_sha256']
assert req['Human_confirmation']['content_sha256']==core.requirement_confirmation_digest(req)
assert req['consensus_Human_confirmation']['content_sha256']==core.normalized_sha256(req['consensus_A0'])
expected={f'OFF-SC{i:02}' for i in range(1,8)}
assert {c['criterion_id'] for c in req['success_criteria']}==expected
assert {c['criterion_id'] for c in p3['requirement_satisfaction']}==expected
matrix=read('ACCEPTANCE_MATRIX.json');assert {c['criterion_id'] for c in matrix}==expected
assert all(not c['parent_satisfied'] for c in matrix)
for row in read('CANDIDATE_SCHEMA_CHECKS.json')['stages']:assert not row['missing_payload_fields'] and not row['type_findings']
assert not p4['frozen'] and p4['freeze_authorization_ref'] is None
assert p4['test_package_sha256']==core.normalized_sha256(p4['tests'])
assert {c for test in p4['tests'] for c in test['success_criterion_ids']}==expected
assert {t['test_id'] for t in p4['tests']}=={t for step in p5['steps'] for t in step['test_ids']}
assert all(step['retry_budget']==3 and set(step['exits'])=={'pass','retry','invalidate_upstream'} for step in p5['steps'])
assert set(p5['upstream_invalidation_targets']).issubset(core.EXPECTED_STAGE_IDS[:4])
assert p6['attempts']==[] and p7['test_results']==[] and p7['completion'] is False
pkg=read('TEST_PACKAGE.json')
for source in pkg['test_sources']:assert digest(ROOT/source['path'])==source['sha256']
assert p4['scoped_package_file_sha256']==digest(OUT/'TEST_PACKAGE.json')
bindings=read('SOURCE_BINDINGS.json')
for source in bindings['route_inputs']+bindings['evidence_sources']:
    raw=subprocess.check_output(['git','show',source['commit']+':'+source['path']],cwd=ROOT)
    assert hashlib.sha256(raw).hexdigest()==source['sha256']
prior=ROOT/'01_os/07_content/_runs/run-20261105-nba2k22-bic-os-integration-readiness-001'
inventory=json.loads((prior/'integration/source_inventory.json').read_bytes())
for item in inventory['changed_files']:assert digest(ROOT/item['path'])==item['sha256']
parent_map=json.loads((prior/'os/stage01/FIELD_EQUIVALENCE_MAP.json').read_bytes());assert len(parent_map['differences'])==23
print(json.dumps({'check_scope':'Preparation payload consistency and evidence integrity only','preparation_check':'PASS','actual_core_requirement_findings':actual_req,'actual_core_evidence_findings':actual_evidence,'stage01_formal_status':'PENDING_STAGE01_OWNER_ACCEPTANCE','official_complete_run_validate':'NOT_RUN_PENDING_STAGE01_OWNER_ACCEPTANCE','seven_criteria_mapped':7,'source_refs_verified':len(bindings['evidence_sources']),'human_approval_refs_verified':2,'reviewed_files_identical':len(inventory['changed_files']),'post_formal_freeze_execution':'NOT_RUN','parent_status':'INCOMPLETE_UNCHANGED','core_sha':'08d8e534a3438269aa7d7eb1b080ab11c172f462','core_runner_sha256':digest(CORE/RUNNER)}))
