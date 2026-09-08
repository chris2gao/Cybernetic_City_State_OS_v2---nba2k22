#!/usr/bin/env python3
"""Validate declared seven-stage artifacts; do not execute their business work."""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys
from pathlib import Path
from typing import Any
import yaml

CONTRACT_PATH="01_os/01_workflow/实现/七阶段最小运行契约_v1.yml"
BOOT_PATH="01_os/02_boot/workflow_minimum_operational_loop/启动清单_v1.yml"
REGISTRY_PATH="01_os/05_registry/workflow_minimum_operational_loop_v1.yml"
RUNNER_PATH="01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py"
PILOT_PATH="01_os/06_execution/workflow/minimum_operational_loop/fixtures/pilot_cross_platform_path_guard"
ACTIVE_STATE_PATH="01_os/03_mechanisms/stage_collaborative_deliberation/激活状态_v1.yml"
RUNTIME_GUARD_PATH="01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_no_canonical_live_state.py"
DELIBERATION_VALIDATOR_PATH="01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation_v2.py"
CONTEXT_VALIDATOR_PATH="01_os/03_mechanisms/context_management/实现/verify_context_structure.py"
WORKFLOW_REF_GLOB="01_os/01_workflow/*/实现/阶段协同推演profile引用_v1.yml"
EXPECTED_STAGE_IDS=[
"workflow_stage_01_requirement_modeling","workflow_stage_02_information_collection",
"workflow_stage_03_result_modeling","workflow_stage_04_test_generation",
"workflow_stage_05_step_decomposition","workflow_stage_06_execution",
"workflow_stage_07_test_execution"]
PROHIBITED_OUTPUT_PREFIXES=("01_os/01_workflow/","01_os/02_boot/","01_os/03_mechanisms/","01_os/05_registry/","01_os/06_execution/")
ACCEPTED_VERDICTS={"PASS","PASS_WITH_NON_BLOCKING_NOTES"}
EXPECTED_MECHANISM_ID="stage_collaborative_deliberation_and_incremental_reconfirmation"
EXPECTED_WORKFLOW_ID="citystate_seven_stage_minimum_operational_loop"

def load_yaml(path:Path)->Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))
def sha256_file(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def normalized_sha256(value:Any)->str:
    raw=yaml.safe_dump(value,allow_unicode=True,sort_keys=True,width=4096).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
def positive_int(v:Any)->bool:
    return isinstance(v,int) and not isinstance(v,bool) and v>0
def run_subvalidator(cmd:list[str],cwd:Path)->int:
    return subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False).returncode

def validate_static(repo_root:Path,run_subvalidators:bool=True)->tuple[int,list[str]]:
    required=[CONTRACT_PATH,BOOT_PATH,REGISTRY_PATH,PILOT_PATH+"/manifest.yml",ACTIVE_STATE_PATH,
              RUNTIME_GUARD_PATH,DELIBERATION_VALIDATOR_PATH,CONTEXT_VALIDATOR_PATH]
    missing=[p for p in required if not (repo_root/p).exists()]
    if missing:return 20,[f"missing:{p}" for p in missing]
    try:
        contract,boot,registry,active=[load_yaml(repo_root/p) for p in (CONTRACT_PATH,BOOT_PATH,REGISTRY_PATH,ACTIVE_STATE_PATH)]
    except Exception as exc:return 21,[f"parse:{type(exc).__name__}:{exc}"]
    findings=[]
    stages=contract.get("stage_order",[]) if isinstance(contract,dict) else []
    if [x.get("stage_id") for x in stages if isinstance(x,dict)]!=EXPECTED_STAGE_IDS:findings.append("stage_order")
    declared=[CONTRACT_PATH,BOOT_PATH,REGISTRY_PATH,RUNNER_PATH]
    for item in stages:
        if not isinstance(item,dict):findings.append("stage_entry");continue
        schema_path=item.get("schema_path",""); declared.append(schema_path)
        if not schema_path or not (repo_root/schema_path).is_file():findings.append(f"schema:{schema_path}");continue
        schema=load_yaml(repo_root/schema_path)
        if schema.get("stage_id")!=item.get("stage_id") or schema.get("artifact_kind")!=item.get("artifact_kind"):
            findings.append(f"schema_binding:{schema_path}")
    if any("\\" in p for p in declared):findings.append("repository_path_backslash")
    if findings:return 23,findings
    if active.get("current_activation_state")!="active_dormant" or active.get("default_route")!="dormant":
        return 22,["activation_state"]
    refs=sorted(repo_root.glob(WORKFLOW_REF_GLOB))
    if len(refs)!=7:return 22,[f"workflow_ref_count:{len(refs)}"]
    ids=[]
    for path in refs:
        ref=load_yaml(path);ids.append(ref.get("profile_id"))
        if ref.get("status")!="active_reference" or ref.get("activation_state")!="active_dormant":
            findings.append(f"workflow_ref_state:{path}")
        if ref.get("default_route")!="dormant" or ref.get("reference_not_copy") is not True:
            findings.append(f"workflow_ref_boundary:{path}")
    if sorted(ids)!=sorted(EXPECTED_STAGE_IDS):findings.append("workflow_ref_ids")
    if findings:return 22,findings
    if contract.get("workflow_id")!=EXPECTED_WORKFLOW_ID or contract.get("workflow_version")!=1:
        findings.append("contract_identity")
    if contract.get("semantic_boundary",{}).get("runner_must_not_claim_to_generate_semantic_answers") is not True:
        findings.append("semantic_boundary")
    if boot.get("contract")!=CONTRACT_PATH or boot.get("runner")!=RUNNER_PATH or boot.get("registry")!=REGISTRY_PATH:
        findings.append("boot_binding")
    if boot.get("stage_schemas")!=[item.get("schema_path") for item in stages]:findings.append("boot_stage_schemas")
    if boot.get("default_deliberation_route")!="dormant" or boot.get("create_live_session_by_default") is not False:
        findings.append("boot_policy")
    if boot.get("canonical_live_instance_state")!="prohibited":findings.append("boot_canonical_state")
    if registry.get("workflow_id")!=contract.get("workflow_id") or registry.get("workflow_version")!=1:
        findings.append("registry_workflow_id")
    if registry.get("status")!="minimum_operational":findings.append("registry_status")
    if findings:return 24,findings
    if run_subvalidators:
        commands=[
            ("runtime_guard",[sys.executable,str(repo_root/RUNTIME_GUARD_PATH),str(repo_root)]),
            ("deliberation_static",[sys.executable,str(repo_root/DELIBERATION_VALIDATOR_PATH),"static",str(repo_root)]),
            ("context_static",[sys.executable,str(repo_root/CONTEXT_VALIDATOR_PATH)])]
        for label,cmd in commands:
            code=run_subvalidator(cmd,repo_root)
            if code!=0:return 22,[f"{label}:{code}"]
    code,more=validate_run(repo_root/PILOT_PATH,repo_root)
    if code:return code,[f"pilot:{x}" for x in more]
    return 0,[]

def validate_receipt(receipt:Any,stage_id:str)->bool:
    if not isinstance(receipt,dict):return False
    if receipt.get("mechanism_id")!=EXPECTED_MECHANISM_ID:return False
    if receipt.get("activation_state")!="active_dormant" or receipt.get("profile_id")!=stage_id:return False
    if receipt.get("receipt_status")!="valid":return False
    route=receipt.get("route")
    if route=="dormant":
        return receipt.get("session_id") is None and receipt.get("Human_authorization_ref") is None
    if route in {"full","incremental"}:
        return bool(receipt.get("session_id")) and bool(receipt.get("task_gate_ref")) and bool(receipt.get("Human_authorization_ref"))
    return False

def payload_schemas(repo_root:Path)->dict[str,dict]:
    """Read required fields from the same canonical schemas checked by static."""
    contract=load_yaml(repo_root/CONTRACT_PATH)
    if not isinstance(contract,dict):raise ValueError("contract_mapping")
    stages=contract.get("stage_order")
    if not isinstance(stages,list) or any(not isinstance(x,dict) for x in stages):
        raise ValueError("schema_stage_order")
    if [x.get("stage_id") for x in stages]!=EXPECTED_STAGE_IDS:
        raise ValueError("schema_stage_order")
    schemas={}
    for item in stages:
        schema=load_yaml(repo_root/item["schema_path"])
        if not isinstance(schema,dict) or schema.get("stage_id")!=item["stage_id"] or schema.get("artifact_kind")!=item["artifact_kind"]:
            raise ValueError("schema_binding")
        fields=schema.get("payload_required_fields")
        if not isinstance(fields,list) or not fields or any(not isinstance(f,str) or not f for f in fields) or len(set(fields))!=len(fields):
            raise ValueError("schema_payload_required_fields")
        schemas[item["stage_id"]]=schema
    return schemas

def payload_type_findings(payload:dict,stage_id:str)->list[str]:
    """Types needed by the execution/review checks, not semantic acceptance."""
    def text(value):return isinstance(value,str) and bool(value.strip())
    def strings(value):return isinstance(value,list) and all(text(x) for x in value)
    def rows(value):return isinstance(value,list) and all(isinstance(x,dict) for x in value)
    findings=[]
    def require(field,predicate):
        if not predicate(payload.get(field)):findings.append(f"payload_type:{stage_id}:{field}")
    if stage_id==EXPECTED_STAGE_IDS[5]:
        for field in ("executor_role","frozen_test_package_sha256"):require(field,text)
        for field in ("allowed_write_paths","actual_write_paths"):require(field,strings)
        require("unauthorized_write_attempts",lambda value:isinstance(value,list))
        require("attempts",rows)
        if rows(payload.get("attempts")):
            for index,row in enumerate(payload["attempts"]):
                if not text(row.get("step_id")) or not text(row.get("result")):
                    findings.append(f"payload_type:{stage_id}:attempts:{index}")
    elif stage_id==EXPECTED_STAGE_IDS[6]:
        for field in ("reviewer_role","verdict"):require(field,text)
        require("completion",lambda value:type(value) is bool)
        require("upstream_invalidation",lambda value:value is None or isinstance(value,dict))
        for field in ("test_results","implementation_claims"):require(field,rows)
        if rows(payload.get("test_results")):
            for index,row in enumerate(payload["test_results"]):
                if not text(row.get("test_id")) or not text(row.get("status")):
                    findings.append(f"payload_type:{stage_id}:test_results:{index}")
        if rows(payload.get("implementation_claims")):
            for index,row in enumerate(payload["implementation_claims"]):
                for field in ("result_claim_ids","evidence_claim_ids"):
                    if not strings(row.get(field)):
                        findings.append(f"payload_type:{stage_id}:implementation_claims:{index}:{field}")
    return findings

def validate_run(run_root:Path,repo_root:Path|None=None)->tuple[int,list[str]]:
    repo_root=repo_root if repo_root is not None else Path(__file__).resolve().parents[4]
    try:schemas=payload_schemas(repo_root)
    except (OSError,ValueError,TypeError,KeyError,yaml.YAMLError,RecursionError) as exc:
        return 33,[f"payload_schema_source:{type(exc).__name__}"]
    try:return _validate_run(run_root,schemas)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,yaml.YAMLError,RecursionError) as exc:
        return 33,[f"artifact_structure:{type(exc).__name__}"]

def _validate_run(run_root:Path,schemas:dict[str,dict])->tuple[int,list[str]]:
    manifest_path=run_root/"manifest.yml"
    if not manifest_path.is_file():return 30,["manifest"]
    try:manifest=load_yaml(manifest_path)
    except Exception as exc:return 33,[f"manifest_parse:{type(exc).__name__}:{exc}"]
    if not isinstance(manifest,dict):return 33,["manifest_mapping"]
    if manifest.get("schema_version")!="citystate.workflow.run_manifest.v1":return 33,["manifest_schema"]
    if manifest.get("workflow_id")!=EXPECTED_WORKFLOW_ID or manifest.get("workflow_version")!=1:return 33,["manifest_identity"]
    if manifest.get("route")!="normal" or manifest.get("deliberation_default_route")!="dormant":return 33,["manifest_route"]
    if manifest.get("completion_expected") is not True:return 39,["manifest_completion_expected"]
    entries=manifest.get("artifacts",[])
    if not isinstance(entries,list) or any(not isinstance(x,dict) for x in entries):return 33,["manifest_artifacts_list"]
    if [x.get("stage_id") for x in entries if isinstance(x,dict)]!=EXPECTED_STAGE_IDS:return 32,["manifest_stage_order"]
    artifacts={};paths={};hashes={}
    for item in entries:
        sid,rel=item.get("stage_id"),item.get("path","");path=run_root/rel
        if not path.is_file():return 30,[f"{sid}:{rel}"]
        actual=sha256_file(path)
        if item.get("sha256")!=actual:return 31,[f"{sid}:{rel}"]
        try:art=load_yaml(path)
        except Exception as exc:return 33,[f"{sid}:{type(exc).__name__}:{exc}"]
        if not isinstance(art,dict):return 33,[f"artifact_mapping:{sid}"]
        if item.get("artifact_version")!=art.get("artifact_version"):return 32,[f"manifest_version:{sid}"]
        artifacts[sid]=art;paths[sid]=path;hashes[sid]=actual
    required={"schema_version","run_id","stage_id","artifact_kind","artifact_version","status","input_refs","deliberation_receipt","payload"}
    predecessors={
      EXPECTED_STAGE_IDS[0]:[],EXPECTED_STAGE_IDS[1]:[EXPECTED_STAGE_IDS[0]],
      EXPECTED_STAGE_IDS[2]:EXPECTED_STAGE_IDS[:2],EXPECTED_STAGE_IDS[3]:EXPECTED_STAGE_IDS[:3],
      EXPECTED_STAGE_IDS[4]:[EXPECTED_STAGE_IDS[3]],EXPECTED_STAGE_IDS[5]:EXPECTED_STAGE_IDS[3:5],
      EXPECTED_STAGE_IDS[6]:[EXPECTED_STAGE_IDS[2],EXPECTED_STAGE_IDS[3],EXPECTED_STAGE_IDS[5]]}
    kinds=dict(zip(EXPECTED_STAGE_IDS,["requirement_package","evidence_package","result_package","frozen_test_package","step_package","execution_package","verification_package"]))
    run_id=manifest.get("run_id")
    for sid in EXPECTED_STAGE_IDS:
        art=artifacts[sid]
        if not required.issubset(art) or art.get("schema_version")!="citystate.workflow.artifact.v1" or art.get("stage_id")!=sid or art.get("run_id")!=run_id:return 33,[f"common:{sid}"]
        payload=art["payload"]
        if not isinstance(payload,dict):return 33,[f"payload_mapping:{sid}"]
        missing=[field for field in schemas[sid]["payload_required_fields"] if field not in payload]
        if missing:return 33,[f"payload_required:{sid}:{field}" for field in missing]
        type_findings=payload_type_findings(payload,sid)
        if type_findings:return 33,type_findings
        if art.get("artifact_kind")!=kinds[sid] or art.get("status")!="complete" or not positive_int(art.get("artifact_version")):
            return 33,[f"identity:{sid}"]
        if not validate_receipt(art.get("deliberation_receipt"),sid):return 34,[sid]
        refs=art.get("input_refs",[])
        if not isinstance(refs,list):return 32,[f"refs:{sid}"]
        by_id={x.get("stage_id"):x for x in refs if isinstance(x,dict)}
        if set(by_id)!=set(predecessors[sid]):return 32,[f"predecessors:{sid}"]
        for pred in predecessors[sid]:
            ref=by_id[pred]
            if ref.get("path")!=paths[pred].name or ref.get("sha256")!=hashes[pred] or ref.get("artifact_version")!=artifacts[pred].get("artifact_version"):
                return 32,[f"binding:{sid}:{pred}"]
    p1,p2,p3,p4,p5,p6,p7=[artifacts[s]["payload"] for s in EXPECTED_STAGE_IDS]
    hc=p1.get("Human_confirmation",{})
    if hc.get("confirmed") is not True or hc.get("artifact_version")!=artifacts[EXPECTED_STAGE_IDS[0]].get("artifact_version") or not p1.get("success_criteria"):
        return 33,["stage1"]
    source_ids={x.get("source_id") for x in p2.get("sources",[]) if isinstance(x,dict)}
    if any(not set(x.get("source_ids",[])) or not set(x.get("source_ids",[])).issubset(source_ids) for x in p2.get("claims",[])):
        return 33,["stage2_claim_sources"]
    c2=p2.get("completion",{})
    if c2.get("feasibility_basis_complete") is not True or c2.get("conflicts_resolved_or_durable") is not True:return 33,["stage2_completion"]
    evidence_ids={x.get("claim_id") for x in p2.get("claims",[]) if isinstance(x,dict)}
    result_ids=set()
    for claim in p3.get("claims",[]):
        result_ids.add(claim.get("result_claim_id"))
        ids=set(claim.get("evidence_claim_ids",[]))
        if not ids or not ids.issubset(evidence_ids):return 33,["stage3_claim_evidence"]
    criteria={x.get("criterion_id") for x in p1.get("success_criteria",[]) if isinstance(x,dict)}
    mapped=set()
    for item in p3.get("requirement_satisfaction",[]):
        mapped.add(item.get("criterion_id"))
        if not set(item.get("result_claim_ids",[])).issubset(result_ids):return 33,["stage3_result_mapping"]
    if mapped!=criteria:return 33,["stage3_criteria_mapping"]
    if p4.get("frozen") is not True or not p4.get("freeze_authorization_ref"):return 35,["stage4_freeze"]
    test_ids=set()
    for test in p4.get("tests",[]):
        test_ids.add(test.get("test_id"));ids=set(test.get("evidence_claim_ids",[]))
        if not ids or not ids.issubset(evidence_ids):return 35,["stage4_test_evidence"]
    if p4.get("test_package_sha256")!=normalized_sha256(p4.get("tests",[])):return 35,["stage4_digest"]
    budgets={}
    step_dependencies={}
    for step in p5.get("steps",[]):
        sid,budget=step.get("step_id"),step.get("retry_budget");budgets[sid]=budget;step_dependencies[sid]=set(step.get("depends_on",[]))
        if not step.get("test_ids") or not set(step.get("test_ids",[])).issubset(test_ids):return 37,["stage5_test_binding"]
        if not positive_int(budget) or budget>3:return 37,["stage5_retry_budget"]
        if set(step.get("exits",[]))!={"pass","retry","invalidate_upstream"}:return 37,["stage5_exits"]
    if not budgets or any(not deps.issubset(budgets) for deps in step_dependencies.values()):return 37,["stage5_dependencies"]
    resolved=set()
    while True:
        new={sid for sid,deps in step_dependencies.items() if deps.issubset(resolved)}-resolved
        if not new:break
        resolved.update(new)
    if resolved!=set(budgets):return 37,["stage5_dependency_cycle"]
    invalidation_targets=set(p5.get("upstream_invalidation_targets",[]))
    if not invalidation_targets or not invalidation_targets.issubset(set(EXPECTED_STAGE_IDS[:4])):return 37,["stage5_invalidation_targets"]
    allowed,actual=set(p6.get("allowed_write_paths",[])),set(p6.get("actual_write_paths",[]))
    if not actual.issubset(allowed) or p6["unauthorized_write_attempts"]!=[]:return 36,["stage6_allowlist"]
    if p6.get("frozen_test_package_sha256")!=p4.get("test_package_sha256"):return 35,["stage6_test_digest"]
    attempt_rows=p6.get("attempts",[])
    grouped={}
    for attempt in attempt_rows:
        sid,n=attempt.get("step_id"),attempt.get("attempt")
        if sid not in budgets or not positive_int(n) or n>budgets[sid]:return 37,["stage6_attempt"]
        if attempt.get("result") not in {"pass","retry","invalidate_upstream"}:return 37,["stage6_attempt_result"]
        grouped.setdefault(sid,[]).append((n,attempt.get("result")))
    if set(grouped)!=set(budgets):return 37,["stage6_attempt_coverage"]
    for sid,rows in grouped.items():
        nums=sorted(n for n,_ in rows)
        if nums!=list(range(1,max(nums)+1)) or max(rows)[1]!="pass":return 37,["stage6_attempt_sequence"]
    if not p7.get("reviewer_role") or p7.get("reviewer_role")==p6.get("executor_role"):return 38,["stage7_independence"]
    if p7.get("verdict") not in ACCEPTED_VERDICTS:return 38,["stage7_verdict"]
    results=p7.get("test_results",[])
    if any(x.get("status")!="passed" for x in results) or {x.get("test_id") for x in results}!=test_ids:return 38,["stage7_tests"]
    for claim in p7.get("implementation_claims",[]):
        if not set(claim.get("result_claim_ids",[])).issubset(result_ids):return 38,["stage7_result_claim_binding"]
        if not set(claim.get("evidence_claim_ids",[])).issubset(evidence_ids):return 38,["stage7_evidence_claim_binding"]
    if p7.get("completion") is not True or p7.get("upstream_invalidation") is not None:return 39,["stage7_completion"]
    return 0,[]

def prohibited_output(repo_root:Path,output_root:Path)->bool:
    try:rel=output_root.resolve().relative_to(repo_root.resolve()).as_posix().rstrip("/")+"/"
    except ValueError:return False
    return any(rel.startswith(prefix) for prefix in PROHIBITED_OUTPUT_PREFIXES)

def materialize_pilot(repo_root:Path,output_root:Path)->tuple[int,list[str]]:
    if prohibited_output(repo_root,output_root):return 40,["canonical_output_root"]
    source=repo_root/PILOT_PATH
    if output_root.exists() and any(output_root.iterdir()):return 40,["output_not_empty"]
    output_root.mkdir(parents=True,exist_ok=True)
    for item in source.iterdir():
        if item.is_file():shutil.copy2(item,output_root/item.name)
    code,findings=validate_run(output_root,repo_root)
    if code:return code,findings
    manifest=load_yaml(output_root/"manifest.yml")
    completion={"schema_version":"citystate.workflow.completion.v1","run_id":manifest.get("run_id"),"workflow_id":manifest.get("workflow_id"),"status":"complete","final_stage":EXPECTED_STAGE_IDS[-1],"artifacts":manifest.get("artifacts"),"default_deliberation_route":"dormant","canonical_live_state_created":False}
    (output_root/"workflow_completion.yml").write_text(yaml.safe_dump(completion,allow_unicode=True,sort_keys=False,width=120),encoding="utf-8",newline="\n")
    return 0,[]

def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=("static","validate","materialize-pilot"))
    parser.add_argument("target");parser.add_argument("output",nargs="?")
    parser.add_argument("--json-output",action="store_true");parser.add_argument("--skip-subvalidators",action="store_true",help=argparse.SUPPRESS)
    args=parser.parse_args()
    if args.command=="static":code,findings=validate_static(Path(args.target),not args.skip_subvalidators)
    elif args.command=="validate":code,findings=validate_run(Path(args.target))
    else:
        if not args.output:parser.error("materialize-pilot requires output")
        code,findings=materialize_pilot(Path(args.target),Path(args.output))
    if args.json_output:print(json.dumps({"command":args.command,"exit_code":code,"findings":findings},ensure_ascii=False))
    elif findings:
        for finding in findings:print(finding,file=sys.stderr)
    return code
if __name__=="__main__":raise SystemExit(main())
