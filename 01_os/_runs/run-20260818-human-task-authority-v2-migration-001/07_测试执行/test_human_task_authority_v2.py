from __future__ import annotations
import copy, hashlib, importlib.util, tempfile
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[4]
VP=ROOT/'01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation.py'
spec=importlib.util.spec_from_file_location('v',VP); v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
NONCE='synthetic-task-authority-code'

def make_record(decision_id, decision_type, model_version, scope):
    r={'schema_version':'citystate.Human_task_authority_event.v2','task_id':'task-v2-test','task_authority_id':'TA-test-001','initial_authority_holder_endpoint_id':'dispatcher-01','initial_authority_holder_task_role':'decision_architecture','task_authority_scope':['execute','review','complete'],'stage_id':'current_task','decision_id':decision_id,'decision_type':decision_type,'exact_model_version':model_version,'Human_disposition':'authorized','authorized_scope':scope,'actor_class':'current_Human','explicit':True,'provenance':'foreground_current_Human_interaction','stale':False,'invalidated':False,'task_authority_revoked':False,'event_revoked':False}
    r['task_nonce_commitment']={'scheme':v.HUMAN_AUTHORITY_SCHEME,'algorithm':'sha256','digest':v.compute_task_commitment({k:r.get(k) for k in v.TASK_AUTHORITY_BOUND_FIELDS},NONCE)}
    r['nonce_commitment']={'scheme':v.HUMAN_AUTHORITY_SCHEME,'algorithm':'sha256','digest':v.compute_commitment({k:r.get(k) for k in v.EVENT_COMMITMENT_BOUND_FIELDS},NONCE)}
    return r

def confirmation(r, blob):
    return {'explicit':True,'actor_class':'current_Human','scope':'current_task','bound_model_version':r['exact_model_version'],'exact_model_version':r['exact_model_version'],'decision_id':r['decision_id'],'decision_type':r['decision_type'],'authority_protocol':v.HUMAN_AUTHORITY_SCHEME,'task_authority_id':r['task_authority_id'],'durable_disposition_ref':'auth.yml','durable_disposition_blob_sha':blob,'task_nonce_commitment':r['task_nonce_commitment'],'nonce_commitment':r['nonce_commitment']}

def raw_blob(path):
    b=path.read_bytes(); return hashlib.sha1(b'blob %d\0'%len(b)+b).hexdigest()

def main():
    execution=make_record('D-exec','substantive_execution_authorization','model-v1',['execute'])
    completion=make_record('D-complete','completion_acceptance','model-v2',['complete'])
    assert execution['task_nonce_commitment']['digest']==completion['task_nonce_commitment']['digest']
    assert execution['nonce_commitment']['digest']!=completion['nonce_commitment']['digest']
    assert v.verify_human_challenge(execution,NONCE)[0]
    assert v.verify_human_challenge(completion,NONCE)[0]
    assert not v.verify_human_challenge(execution,'wrong-code')[0]
    cross=copy.deepcopy(execution); cross['task_id']='other-task'
    assert not v.verify_human_challenge(cross,NONCE)[0]
    holder_tamper=copy.deepcopy(execution); holder_tamper['initial_authority_holder_endpoint_id']='other-dispatcher'
    assert not v.verify_human_challenge(holder_tamper,NONCE)[0]
    legacy_challenge={'task_id':'task-v2-test','stage_id':'current_task','decision_id':'D-old-challenge','decision_type':'substantive_execution_authorization','exact_model_version':'old','Human_disposition':'authorized','authorized_scope':'x','actor_class':'current_Human','explicit':True,'provenance':'foreground_current_Human_interaction','stale':False,'invalidated':False}
    legacy_bound={k:legacy_challenge.get(k) for k in v.LEGACY_COMMITMENT_BOUND_FIELDS}
    legacy_challenge['nonce_commitment']={'scheme':v.LEGACY_HUMAN_AUTHORITY_SCHEME,'algorithm':'sha256','digest':v.compute_legacy_commitment(legacy_bound,NONCE)}
    assert v.verify_human_challenge(legacy_challenge,NONCE)[0]
    revoked=copy.deepcopy(execution); revoked['task_authority_revoked']=True
    assert v.validate_durable_disposition_record(revoked,{'task_authority_id':'TA-test-001','decision_id':'D-exec','decision_type':'substantive_execution_authorization','exact_model_version':'model-v1','task_nonce_commitment':revoked['task_nonce_commitment'],'nonce_commitment':revoked['nonce_commitment']},{'current_exact_model_version':'model-v1'})==12
    legacy={'task_id':'task-v2-test','stage_id':'current_task','decision_id':'D-old','decision_type':'substantive_execution_authorization','exact_model_version':'old','Human_disposition':'authorized','authorized_scope':'x','actor_class':'current_Human','explicit':True,'provenance':'foreground_current_Human_interaction','stale':False,'invalidated':False,'nonce_commitment':{'scheme':v.LEGACY_HUMAN_AUTHORITY_SCHEME,'algorithm':'sha256','digest':'a'*64}}
    assert v.validate_durable_disposition_record(legacy,{'decision_id':'D-old','decision_type':'substantive_execution_authorization','exact_model_version':'old','nonce_commitment':legacy['nonce_commitment']},{'current_exact_model_version':'old'})==15
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); ap=root/'auth.yml'; ap.write_text(yaml.safe_dump(execution,sort_keys=False,allow_unicode=True),encoding='utf-8',newline='\n')
        conf=confirmation(execution,raw_blob(ap))
        model={'problem_or_objective':'x','Human_intent_understanding':'x','current_baseline_and_inputs':{'x':1},'constraints_and_dependencies':['x'],'proposed_method_or_solution':['x'],'feasibility_support':['x'],'assumptions_risks_alternatives_unknowns':['x'],'open_load_bearing_items':[],'expected_output':'x','verification_or_acceptance_method':['x'],'actual_result':'x','material_deviation':'none','residual_risk':'x','current_exact_model_version':'model-v1','Human_confirmation':conf}
        data={'task_id':'task-v2-test','stage_id':'current_task','current_model':model}
        assert v.validate_model_readiness(data,root)==0
    discipline=(ROOT/'AGENT_WORKING_DISCIPLINE.md').read_text(encoding='utf-8')
    assert "The reviewer never reviews its own family's output." not in discipline
    assert 'same-family review is allowed' in discipline
    contract=(ROOT/'01_os/03_mechanisms/stage_collaborative_deliberation/阶段profile契约_v1.yml').read_text(encoding='utf-8')
    assert 'same_model_family_absolute_prohibition: false' in contract
    print('human_task_authority_v2_tests=PASS')

if __name__=='__main__': main()
