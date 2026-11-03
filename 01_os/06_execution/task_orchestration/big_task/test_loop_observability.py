from __future__ import annotations

import copy
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import loop_observability as m

SHA1='a'*40
SHA2='b'*40

def record(index=1, before=SHA1, after=SHA2):
    return {
        'schema_version':m.VERSION,'task_id':'OS-CORE-TEST', 'iteration_id':f'iter-{index:03}',
        'iteration_index':index,'trigger_type':'planned_increment','objective':'Reproducible bounded test',
        'source_ref':'github:core@sha','before_sha':before,'after_sha':after,
        'changed_paths':['01_os/06_execution/task_orchestration/big_task/loop_observability.py'],
        'actual_test_receipts':[{'test_name':'unit','exit_code':0,'status':'PASS','receipt_ref':'07_tests/unit.out'}],
        'expected_vs_observed':{'expected':'case passes','observed':'exit zero'},
        'regression_status':'PASS','evidence_grade':'EXECUTED_VERIFIED',
        'remaining_gaps':[],'next_action_or_stop_reason':'Next bounded increment',
        'outcome':'improvement_verified_in_scope'
    }

def codes(rows):
    return {x['code'] for x in m.validate(rows)}

def test_valid_one_and_chained_two():
    assert not codes([record()])
    assert not codes([record(),record(index=2,before=SHA2,after=SHA2)])

def test_replay_g2s0_missing_evidence_no_invention():
    r={'iteration_id':'iter-001','bounded_objective':'Read only audit','actions':['Read SQL'],
      'sha_before':SHA1,'sha_after':SHA1,'trigger_type':'PLANNED_INCREMENT',
      'test_receipts':[{'test_name':'SQL','exit_code':0,'status':'PASSED'}],
      'outcome':'SUCCESS','next_trigger_or_stop_ref':'iter-002'}
    norm,find=m.replay_legacy([r],m.LEGACY_A,'TASK','sha:path')
    assert norm[0]['before_sha']==SHA1
    assert norm[0]['actual_test_receipts'][0]['exit_code']==0
    assert norm[0]['evidence_grade']=='LEGACY_EVIDENCE_MISSING'
    assert 'LEGACY_EVIDENCE_MISSING:expected_vs_observed' in {x['code'] for x in find}
    assert not m.build_report([r],m.LEGACY_A,find,norm)['strict_audit_pass']

def test_replay_host_claim_pass_is_not_exit_code():
    r={'iteration':1,'phase':'S1','increment':'host','goal':'build','action':'created files',
       'status':'PASS','evidence':{'tests_passed':96}}
    norm,find=m.replay_legacy([r],m.LEGACY_B,None,'sha:path')
    assert norm[0]['actual_test_receipts']==[]
    assert 'LEGACY_SELF_REPORTED_PASS_NOT_EXECUTED_PROOF' in {x['code'] for x in find}
    assert norm[0]['before_sha'] is None

@pytest.mark.parametrize('change,expected',[
    ({'iteration_id':'iter-001'},'DUPLICATE_ITERATION_ID'),
    ({'task_id':None},'INVALID_TASK_ID'),
    ({'trigger_type':'fiction'},'INVALID_TRIGGER_TYPE'),
    ({'before_sha':None},'INVALID_BEFORE_SHA'),
    ({'actual_test_receipts':[{'test_name':'x','status':'PASS','exit_code':2,'receipt_ref':'07_tests/x.out'}]},'PASS_CONTRADICTS_EXIT_CODE'),
    ({'actual_test_receipts':[{'test_name':'x','status':'FAIL','exit_code':1,'receipt_ref':'07_tests/x.out'}],'outcome':'improvement_verified_in_scope'},'SUCCESS_CLAIM_WITH_FAILED_TEST'),
    ({'outcome':'objective_met_ready_for_series_review','remaining_gaps':[{'id':'g1','status':'OPEN'}]},'OPEN_GAP_CONTRADICTS_OBJECTIVE_MET'),
    ({'outcome':'objective_met_ready_for_series_review','remaining_gaps':[{'id':'g1','status':'BLOCKED'}]},'OPEN_GAP_CONTRADICTS_OBJECTIVE_MET'),
    ({'independent_review_status':'PASS'},'SELF_DECLARED_INDEPENDENT_REVIEW'),
    ({'protected_actions':[{'action':'merge-master','status':'EXECUTED'}]},'PROTECTED_ACTION_REQUIRES_EXTERNAL_HUMAN_PROOF'),
    ({'lifecycle':'completed'},'LIFECYCLE_NOT_IN_CANONICAL_ENUM'),
    ({'stop_reason':'task_branch_push'},'INVALID_GENUINE_STOP_REASON'),
    ({'continuation_reason':'unknown'},'UNRECOGNIZED_CONTINUATION_REASON'),
    ({'expected_vs_observed':{}},'MISSING_EXPECTED_VS_OBSERVED'),
    ({'actual_test_receipts':[],'evidence_grade':'EXECUTED_VERIFIED'},'EVIDENCE_GRADE_EXCEEDS_TEST_PROOF'),
    ({'review_schedule':{'review_mode':'deferred_to_series'}},'DEFERRED_REVIEW_BOUNDARY_INCOMPLETE'),
    ({'changed_paths':[]},'NO_CHANGED_PATHS_OR_RESEARCH_ACTIONS'),
    ({'outcome':'genuine_stop_reached'},'STOP_WITHOUT_GENUINE_STOP_REASON'),
])
def test_negative_cases(change,expected):
    rows=[record(),record(index=2,before=SHA2,after=SHA2)]
    rows[1].update(change)
    assert expected in codes(rows)

def test_checkpoint_chain_mismatch():
    assert 'CHECKPOINT_SHA_CHAIN_MISMATCH' in codes([record(),record(index=2,before=SHA1,after=SHA2)])

def test_wrong_order():
    assert 'NONCONTIGUOUS_ITERATION_ORDER' in codes([record(index=2)])

def test_all_malformed_inputs_fail_closed(tmp_path):
    p=tmp_path/'bad.jsonl'
    for raw,expected in [('not json','INVALID_JSONL'),('','EMPTY_JSONL'),('[]','JSONL_RECORD_NOT_OBJECT'),('{}\n','INVALID_REQUIRED')]:
        p.write_text(raw,encoding='utf-8')
        if expected=='INVALID_REQUIRED':
            assert m.validate(m.read_jsonl(p))
        else:
            with pytest.raises(ValueError,match=expected):m.read_jsonl(p)

def test_deterministic_report_and_no_input_rewrite(tmp_path):
    p=tmp_path/'log.jsonl';out=tmp_path/'report.json'
    original=json.dumps(record(),sort_keys=True)+'\n';p.write_text(original)
    assert m.main(['--input',str(p),'--report',str(out)])==0
    first=out.read_bytes();assert p.read_text()==original
    assert m.main(['--input',str(p),'--report',str(out)])==0
    assert first==out.read_bytes()

def test_strict_fails_on_legacy_unknown(tmp_path):
    p=tmp_path/'legacy.jsonl';p.write_text('{"iteration":1,"increment":"x"}\n')
    assert m.main(['--input',str(p),'--format','strict'])==1

def test_unknown_object_types_are_findings_not_exceptions():
    broken=record();broken.update({'trigger_type':[], 'outcome':{}, 'protected_actions':42,
      'changed_paths':None,'actual_test_receipts':None,'lifecycle':[],'regression_status':[]})
    assert len(m.validate([broken]))>=6

def test_review_ready_requires_verified_evidence_and_schedule():
    r=record();r['outcome']='objective_met_ready_for_series_review';r['review_schedule']={
     'review_mode':'deferred_to_series','series_id':'S','review_trigger':'series-complete',
     'must_review_before':'master-merge','candidate_head':SHA2,'verification_receipt':'ci-1',
     'downstream_consumption':'candidate_only','deferral_reason':'reversible','next_owner':'independent_review'}
    assert not codes([r]);assert m.build_report([r],'strict',[])['review_candidate']
    r['review_schedule']['downstream_consumption']='blocking_authoritative_dependency'
    assert 'DEFERRED_REVIEW_BOUNDARY_INCOMPLETE' in codes([r])


def test_report_cannot_overwrite_raw_log(tmp_path):
    p=tmp_path/"input.jsonl"
    raw=json.dumps(record())+"\n"
    p.write_text(raw)
    assert m.main(["--input",str(p),"--report",str(p)])==3
    assert p.read_text()==raw
