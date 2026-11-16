#!/usr/bin/env python3
"""Validate declared seven-stage artifacts; do not execute their business work."""
from __future__ import annotations
import argparse, difflib, hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
from typing import Any
import yaml

CONTRACT_PATH="01_os/01_workflow/实现/七阶段最小运行契约_v1.yml"
BOOT_PATH="01_os/02_boot/workflow_minimum_operational_loop/启动清单_v1.yml"
REGISTRY_PATH="01_os/05_registry/workflow_minimum_operational_loop_v1.yml"
RUNNER_PATH="01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py"
HISTORY_GATE_PATH="01_os/06_execution/workflow/publication_gate/workflow_publication_gate.py"
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
STAGE01_SPEC="01_os/01_workflow/01_需求建模/方法论_v1.md"
STAGE01_TEMPLATE="01_os/01_workflow/01_需求建模/实现/需求结果模型模板_v1.yml"
EXPECTED_MECHANISM_ID="stage_collaborative_deliberation_and_incremental_reconfirmation"
EXPECTED_WORKFLOW_ID="citystate_seven_stage_minimum_operational_loop"
PREDECESSORS = dict(zip(EXPECTED_STAGE_IDS, (
    [], EXPECTED_STAGE_IDS[:1], EXPECTED_STAGE_IDS[:2], EXPECTED_STAGE_IDS[:3],
    EXPECTED_STAGE_IDS[3:4], EXPECTED_STAGE_IDS[3:5],
    [EXPECTED_STAGE_IDS[i] for i in (2, 3, 5)],
)))

def load_yaml(path:Path)->Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))
def sha256_file(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def normalized_sha256(value:Any)->str:
    raw=yaml.safe_dump(value,allow_unicode=True,sort_keys=True,width=4096).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
def positive_int(v:Any)->bool:
    return isinstance(v,int) and not isinstance(v,bool) and v>0

def requirement_confirmation_digest(payload:dict)->str:
    """Bind the full proposed requirement, including criteria, not just its title."""
    return normalized_sha256({k:v for k,v in payload.items()
                              if k not in {"Human_confirmation","consensus_Human_confirmation"}})

def requirement_findings(payload:dict,artifact_version:int)->list[str]:
    """The one active Stage01 structural contract. Not Human authentication."""
    def text(x):return isinstance(x,str) and bool(x.strip())
    def strings(x,nonempty=False):
        return isinstance(x,list) and (bool(x) or not nonempty) and all(text(v) for v in x)
    def rows(x,nonempty=False):
        return isinstance(x,list) and (bool(x) or not nonempty) and all(isinstance(v,dict) for v in x)
    if not text(payload.get("requirement_id")) or not text(payload.get("objective")):
        return ["stage1_identity"]
    criteria=payload.get("success_criteria")
    if not rows(criteria,True) or any(not text(c.get("criterion_id")) or not text(c.get("statement")) for c in criteria):
        return ["stage1_success_criteria"]
    criterion_ids=[c["criterion_id"] for c in criteria]
    if len(set(criterion_ids))!=len(criterion_ids):return ["stage1_duplicate_criterion"]
    if not strings(payload.get("constraints")):return ["stage1_constraints"]
    a0=payload.get("consensus_A0");a=payload.get("requirement_result_A")
    if not isinstance(a0,dict) or not isinstance(a,dict):return ["stage1_dual_models_required"]
    if not positive_int(a0.get("version")) or not text(a0.get("model_id")):
        return ["stage1_consensus_identity"]
    for field in ("objective","success_direction"):
        if not text(a0.get(field)):return [f"stage1_consensus:{field}"]
    if not strings(a0.get("boundaries"),True) or not isinstance(a0.get("terms"),dict):
        return ["stage1_consensus_scope"]
    if any(not text(k) or not text(v) for k,v in a0["terms"].items()):return ["stage1_consensus_terms"]
    if a.get("version")!=artifact_version or not positive_int(a.get("version")) or not text(a.get("model_id")) or a["model_id"]==a0["model_id"]:
        return ["stage1_result_identity"]
    h0=payload.get("consensus_Human_confirmation");ha=payload.get("Human_confirmation")
    if not isinstance(h0,dict) or not isinstance(ha,dict):return ["stage1_dual_confirmations_required"]
    for confirmation,model,kind,digest in (
        (h0,a0,"consensus_A0",normalized_sha256(a0)),
        (ha,a,"requirement_result_A",requirement_confirmation_digest(payload))):
        if (confirmation.get("confirmed") is not True or confirmation.get("model_kind")!=kind
                or confirmation.get("model_id")!=model["model_id"]
                or type(confirmation.get("artifact_version")) is not int
                or confirmation["artifact_version"]!=model["version"]
                or confirmation.get("content_sha256")!=digest
                or not text(confirmation.get("confirmation_ref"))):
            return [f"stage1_confirmation_binding:{kind}"]
    if h0["confirmation_ref"]==ha["confirmation_ref"]:return ["stage1_distinct_confirmations"]
    expected_ref={"model_id":a0["model_id"],"version":a0["version"],
                  "sha256":normalized_sha256(a0),"confirmation_ref":h0["confirmation_ref"]}
    if a.get("consensus_ref")!=expected_ref:return ["stage1_consensus_ref"]
    items=a.get("result_items")
    if not rows(items,True):return ["stage1_result_items"]
    ids=[];question_ids=set();item_criteria={}
    for item in items:
        identifier=item.get("result_item_id")
        if not text(identifier) or identifier in ids:return ["stage1_result_item_identity"]
        ids.append(identifier)
        for field in ("title","kind","expected_end_state","completeness_rule"):
            value=item.get(field)
            if not text(value) or value.strip().casefold() in {"tbd","todo","complete system","完成一个系统","待定"} or value.strip().startswith("<"):
                return [f"stage1_result_item:{identifier}:{field}"]
        for field,nonempty in (("components",True),("relations",False),("inputs_outputs",True),("acceptance_criterion_ids",True)):
            if not strings(item.get(field),nonempty):return [f"stage1_result_item:{identifier}:{field}"]
        mapped=item["acceptance_criterion_ids"]
        if len(mapped)!=len(set(mapped)) or not set(mapped).issubset(criterion_ids):return ["stage1_result_criterion_mapping"]
        item_criteria[identifier]=set(mapped)
        facts=item.get("known_facts");unknowns=item.get("unknowns")
        if not rows(facts) or not rows(unknowns):return ["stage1_result_evidence"]
        if any(not text(f.get("item")) or f.get("evidence_status") not in {"human_requirement","source_observed","static_source","offline_verified","live_effect_verified","independently_reviewed","candidate_inference"} for f in facts):
            return ["stage1_known_fact_evidence"]
        for q in unknowns:
            if (not text(q.get("question_id")) or q["question_id"] in question_ids
                    or not text(q.get("scope")) or not text(q.get("closure_evidence"))
                    or q.get("status")!="UNKNOWN"):
                return ["stage1_unknown_evidence_question"]
            question_ids.add(q["question_id"])
    if set().union(*item_criteria.values())!=set(criterion_ids):return ["stage1_criterion_coverage"]
    coverage=a.get("coverage")
    if not rows(coverage,True):return ["stage1_coverage"]
    seen=set();covered_questions=set()
    for row in coverage:
        criterion=row.get("success_criterion_id")
        if not text(criterion) or criterion in seen or criterion not in criterion_ids:return ["stage1_coverage_criterion"]
        seen.add(criterion)
        refs=row.get("result_item_ids");qs=row.get("evidence_questions")
        if not strings(refs,True) or not strings(qs) or len(refs)!=len(set(refs)) or len(qs)!=len(set(qs)):
            return ["stage1_coverage_references"]
        if set(refs)!={identifier for identifier,mapped in item_criteria.items() if criterion in mapped}:
            return ["stage1_coverage_result_binding"]
        expected_questions={q["question_id"] for item in items if item["result_item_id"] in refs for q in item["unknowns"]}
        if set(qs)!=expected_questions:return ["stage1_coverage_question_binding"]
        covered_questions.update(qs)
    if seen!=set(criterion_ids) or covered_questions!=question_ids:return ["stage1_coverage_complete"]
    return []

def evidence_findings(payload:dict,requirement:dict)->list[str]:
    """Separate feasibility support from background and preserve exact source scope."""
    import re
    def text(v):return isinstance(v,str) and bool(v.strip())
    def strings(v):return isinstance(v,list) and all(text(x) for x in v)
    sources=payload.get("sources");claims=payload.get("claims")
    if not isinstance(sources,list) or not sources or not all(isinstance(s,dict) for s in sources):return ["stage2_sources"]
    source_ids=set()
    for source in sources:
        sid=source.get("source_id");ref=source.get("source_ref")
        if not text(sid) or sid in source_ids or not isinstance(ref,dict):return ["stage2_source_identity"]
        source_ids.add(sid)
        if "repository" in ref:
            if (not text(ref["repository"]) or not isinstance(ref.get("commit"),str)
                    or re.fullmatch(r"[0-9a-f]{40}",ref["commit"]) is None or not text(ref.get("path"))):
                return ["stage2_exact_source_ref"]
        elif not all(text(ref.get(f)) for f in ("url","version","observed_at")):
            return ["stage2_external_source_ref"]
        if source.get("publication_status") not in {"MASTER_INCLUDED","SOURCE_BRANCH_NOT_MASTER","EXTERNAL_VERSIONED_SOURCE"}:
            return ["stage2_source_publication_status"]
    if not isinstance(claims,list) or not claims or not all(isinstance(c,dict) for c in claims):return ["stage2_claims"]
    item_ids={x["result_item_id"] for x in requirement["requirement_result_A"]["result_items"]}
    criteria={x["criterion_id"] for x in requirement["success_criteria"]}
    kinds={"STATIC_SOURCE","OFFLINE_TEST","LIVE_TOOL_CALL","LIVE_TARGET_EFFECT","INDEPENDENT_REVIEW","UNKNOWN","BACKGROUND_REFERENCE"}
    claim_ids=set();covered_items=set()
    for claim in claims:
        cid=claim.get("claim_id")
        if not text(cid) or cid in claim_ids:return ["stage2_claim_identity"]
        claim_ids.add(cid)
        if claim.get("evidence_kind") not in kinds or claim.get("purpose") not in {"FEASIBILITY","BACKGROUND"}:
            return ["stage2_evidence_classification"]
        if not text(claim.get("limits")):return ["stage2_evidence_limits"]
        if not strings(claim.get("source_ids")) or not claim["source_ids"] or not set(claim["source_ids"]).issubset(source_ids):
            return ["stage2_claim_sources"]
        for field,valid in (("result_item_ids",item_ids),("success_criterion_ids",criteria)):
            if not strings(claim.get(field)) or not set(claim[field]).issubset(valid):return ["stage2_requirement_mapping"]
            if claim["purpose"]=="FEASIBILITY" and not claim[field]:return ["stage2_feasibility_mapping"]
        covered_items.update(claim["result_item_ids"])
        if claim["evidence_kind"]=="UNKNOWN" and not text(claim.get("closure_evidence")):return ["stage2_unknown_closure"]
        if claim["evidence_kind"]=="BACKGROUND_REFERENCE" and claim["purpose"]!="BACKGROUND":return ["stage2_background_not_feasibility"]
    if covered_items!=item_ids:return ["stage2_result_coverage"]
    return []
def run_subvalidator(cmd:list[str],cwd:Path)->int:
    return subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False).returncode

def validate_static(repo_root:Path,run_subvalidators:bool=True)->tuple[int,list[str]]:
    required=[CONTRACT_PATH,BOOT_PATH,REGISTRY_PATH,PILOT_PATH+"/manifest.yml",ACTIVE_STATE_PATH,
              RUNTIME_GUARD_PATH,DELIBERATION_VALIDATOR_PATH,CONTEXT_VALIDATOR_PATH,HISTORY_GATE_PATH]
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
    for key,path in (("stage01_active_semantic_spec",STAGE01_SPEC),("stage01_result_model_template",STAGE01_TEMPLATE)):
        if boot.get(key)!=path or not (repo_root/path).is_file():findings.append(f"boot_{key}")
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
    # The pilot is a structural fixture with no commit history of its own, so it
    # is checked for shape only. Passing here says the schemas and the fixture
    # agree; it says nothing about a governed run having been validated.
    code,more=validate_structure(repo_root/PILOT_PATH,repo_root)
    if code:return code,[f"pilot_structural:{x}" for x in more]
    return 0,[]

# Retained for the historical callers that still import it. It is no longer the
# workflow's receipt check: the mechanism owns that, and this shallow copy being
# the one the workflow actually reached was the defect this work removed.
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

DELIBERATION_VALIDATOR="01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation.py"

def load_deliberation_validator(repo_root:Path):
    spec=importlib.util.spec_from_file_location("scd_authoritative",repo_root/DELIBERATION_VALIDATOR)
    if spec is None or spec.loader is None:raise RuntimeError("cannot load the deliberation validator")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def compose_instance(run_root:Path,art:dict,sid:str,run_doc:dict,candidate:str)->dict:
    """Historical single-instance adapter; not the committed-run validation path.

    This function locates and arranges. It decides nothing. Whether the model is
    complete, whether a feasibility basis holds, whether a Human disposition is
    present and current: all of that belongs to the deliberation mechanism and is
    read there, from the document this builds.
    """
    control=art.get("stage_control")
    if not isinstance(control,dict):raise ValueError(f"stage_control missing:{sid}")
    model_ref=control.get("current_model_ref")
    if not isinstance(model_ref,dict) or "path" not in model_ref:
        raise ValueError(f"current_model_ref missing:{sid}")
    model=load_yaml(run_root/model_ref["path"])
    if not isinstance(model,dict):raise ValueError(f"current model unreadable:{sid}")
    receipt=art.get("deliberation_receipt")
    scope={"schema_version":1,"task_id":run_doc.get("task_id"),"candidate":candidate,
           "task_packet":run_doc.get("task_packet_ref"),"action_id":control.get("action_id"),
           "stage_id":sid,"paths":run_doc.get("stage_paths",[])}
    instance={"task_scope":scope,"current_model":model,"receipt":receipt,
              "stage_profile_id_and_version":(receipt or {}).get("profile_id_and_version")}
    mode=(receipt or {}).get("route")
    if mode:instance["activation_mode"]=mode
    reason=(receipt or {}).get("dormant_reason")
    if reason:instance["dormant_reason"]=reason
    return instance

def validate_deliberation(repo_root:Path|None,run_root:Path,art:dict,sid:str,
                          run_doc:dict,candidate:str|None)->tuple[int,str]:
    """Hand the composed instance to the authoritative validator and consume its verdict.

    The runner used to carry its own ten-line receipt check here. That check and
    the mechanism's twenty-field contract were two definitions of one object, and
    the strict one was never reached from the workflow. There is now one owner.

    Without a candidate the canonical instance cannot be built: the mechanism
    binds the model version and the packet allowlist to an exact commit. That is
    reported as not validated rather than replaced by something weaker.
    """
    if candidate is None or repo_root is None:
        return 0,f"deliberation_instance_not_validated:no_candidate:{sid}"
    try:
        validator=load_deliberation_validator(repo_root)
        instance=compose_instance(run_root,art,sid,run_doc,candidate)
    except Exception as exc:
        return 34,f"deliberation_instance_uncomposable:{sid}:{type(exc).__name__}"
    code=validator.validate_task_scope_instance(instance,repo_root,candidate)
    if code:return 34,f"deliberation_instance_rejected:{sid}:mechanism_exit_{code}"
    return 0,""

def payload_schemas(repo_root:Path,read_yaml=load_yaml)->dict[str,dict]:
    """Read required fields from the same canonical schemas checked by static."""
    contract=read_yaml(repo_root/CONTRACT_PATH)
    if not isinstance(contract,dict):raise ValueError("contract_mapping")
    stages=contract.get("stage_order")
    if not isinstance(stages,list) or any(not isinstance(x,dict) for x in stages):
        raise ValueError("schema_stage_order")
    if [x.get("stage_id") for x in stages]!=EXPECTED_STAGE_IDS:
        raise ValueError("schema_stage_order")
    schemas={}
    for item in stages:
        schema=read_yaml(repo_root/item["schema_path"])
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

def validate_structure(run_root:Path,repo_root:Path|None=None)->tuple[int,list[str]]:
    """Shape, hashes, stage order and payload schemas. Not a governed-run verdict.

    Structurally inspectable is not authoritatively validated. This entry never
    reaches the deliberation mechanism and must never be reported as a passing
    run: it is what static uses on a schema fixture, where no candidate exists.
    """
    repo_root=repo_root if repo_root is not None else Path(__file__).resolve().parents[4]
    try:schemas=payload_schemas(repo_root)
    except (OSError,ValueError,TypeError,KeyError,yaml.YAMLError,RecursionError) as exc:
        return 33,[f"payload_schema_source:{type(exc).__name__}"]
    try:return _validate_run(run_root,schemas,repo_root,None)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,yaml.YAMLError,RecursionError) as exc:
        return 33,[f"artifact_structure:{type(exc).__name__}"]

def validate_run(run_root:Path,repo_root:Path|None=None,candidate:str|None=None)->tuple[int,list[str]]:
    """Full validation. Refuses when the authoritative check cannot be performed.

    An earlier revision returned 0 here with findings saying the deliberation
    instance had not been validated. Anything downstream reading only the exit
    code would have taken never ran the authoritative validator for a pass, which
    is the same defect as collecting a verdict and not consuming it.
    """
    if candidate is None:
        return 41,["deliberation_not_validated:no_candidate:"
                   "full validation requires the commit the run is judged at"]
    repo_root=(repo_root if repo_root is not None else Path(__file__).resolve().parents[4]).resolve()
    try:
        source=CommittedRunSource(repo_root,candidate)
        run_root=run_root.absolute()
        run_rel=run_root.relative_to(repo_root).as_posix()
        schemas=payload_schemas(repo_root,source.load_yaml)
        code,findings=_validate_run(run_root,schemas,repo_root,source=source)
        if code:return code,findings
    except Exception as exc:
        # Failure to read the candidate never becomes a structural-only pass.
        return 33,[f"committed_run_source_or_structure:{type(exc).__name__}:{exc}"]
    gate=source.gate
    findings=gate.Findings()
    try:
        # No publication boundary exemption here: the Human explicitly asked to
        # validate this run. The existing history gate resolves M/P/W/C and calls
        # the semantic owner for each acceptance. It is not reimplemented here.
        code=gate.gate_run(repo_root,candidate,run_rel,None,findings)
        if code:return 34,[f"publication_gate_exit_{code}",*findings.summary()]
        return 0,findings.summary()
    except gate.GateError as exc:
        return 34,[f"publication_gate_exit_{exc.code}:{exc.reason}"]
    except Exception as exc:
        return 34,[f"publication_gate_unreadable:{type(exc).__name__}"]


class CommittedRunSource:
    """Read only exact regular Git blobs; checkout bytes are not candidate data.

    The installed owner already has strict Git source helpers. Reusing
    them is permitted; their source files remain outside this task's write scope.
    Cache bytes only to avoid asking Git repeatedly for the same immutable blob.
    """
    def __init__(self,repo_root:Path,candidate:str):
        installation=Path(__file__).resolve().parents[4]
        owner=load_deliberation_validator(installation)
        self.support=owner.task_scope_support()
        self.support.candidate_id(repo_root,candidate)
        actual=self.support.git(repo_root,"rev-parse","--show-toplevel").decode("utf-8").strip()
        if Path(actual).resolve()!=repo_root:raise ValueError("repository_root_required")
        gate_path=installation/HISTORY_GATE_PATH
        spec=importlib.util.spec_from_file_location("minimum_loop_history_gate",gate_path)
        if spec is None or spec.loader is None:raise RuntimeError("publication_gate_unavailable")
        self.gate=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=self.gate
        spec.loader.exec_module(self.gate)
        self.repo=repo_root
        self.candidate=candidate
        self.cache={}

    def read_bytes(self,path:Path)->bytes:
        # Do not resolve candidate paths through symlinks in the mutable checkout.
        rel=path.absolute().relative_to(self.repo).as_posix()
        if rel not in self.cache:
            self.cache[rel]=self.support.tracked_blob(self.repo,self.candidate,rel)
        return self.cache[rel]

    def load_yaml(self,path:Path)->Any:
        # Workflow schemas have integer exit-code keys. The task-packet YAML
        # subset forbids those, so it is not the schema language for this reader.
        doc=yaml.safe_load(self.read_bytes(path).decode("utf-8"))
        self.support.same_json(doc,doc)
        return doc

    def is_file(self,path:Path)->bool:
        self.read_bytes(path)  # absent, symlink or unreadable means source failure
        return True

    def sha256(self,path:Path)->str:
        return hashlib.sha256(self.read_bytes(path)).hexdigest()

def _validate_run(run_root:Path,schemas:dict[str,dict],repo_root:Path|None=None,
                  candidate:str|None=None,source:CommittedRunSource|None=None)->tuple[int,list[str]]:
    read_yaml=source.load_yaml if source is not None else load_yaml
    is_file=source.is_file if source is not None else Path.is_file
    digest=source.sha256 if source is not None else sha256_file
    manifest_path=run_root/"manifest.yml"
    if not is_file(manifest_path):return 30,["manifest"]
    try:manifest=read_yaml(manifest_path)
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
        if not is_file(path):return 30,[f"{sid}:{rel}"]
        actual=digest(path)
        if item.get("sha256")!=actual:return 31,[f"{sid}:{rel}"]
        try:art=read_yaml(path)
        except Exception as exc:return 33,[f"{sid}:{type(exc).__name__}:{exc}"]
        if not isinstance(art,dict):return 33,[f"artifact_mapping:{sid}"]
        if item.get("artifact_version")!=art.get("artifact_version"):return 32,[f"manifest_version:{sid}"]
        artifacts[sid]=art;paths[sid]=path;hashes[sid]=actual
    # stage_control is required with the rest. A field declared in the schema and
    # not checked here would be exactly the declared-but-unenforced defect this
    # work exists to remove, so the contract and the checker change together.
    required={"stage_control","schema_version","run_id","stage_id","artifact_kind","artifact_version","status","input_refs","deliberation_receipt","payload"}
    kinds=dict(zip(EXPECTED_STAGE_IDS,["requirement_package","evidence_package","result_package","frozen_test_package","step_package","execution_package","verification_package"]))
    run_id=manifest.get("run_id")
    run_doc=read_yaml(run_root/"run.yml") if is_file(run_root/"run.yml") else {}
    if not isinstance(run_doc,dict):run_doc={}
    deliberation_notes:list[str]=[]
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
        # One owner for the deliberation verdict. The runner composes and consumes;
        # it does not judge. A nonzero from the mechanism stops the run here.
        if source is None:
            code,note=validate_deliberation(repo_root,run_root,art,sid,run_doc,candidate)
            if code:return code,[note]
            if note:deliberation_notes.append(note)
        # Exact-candidate callers consume the history gate once after all
        # structural checks. They never use the historical single-instance adapter.
        refs=art.get("input_refs",[])
        if not isinstance(refs,list):return 32,[f"refs:{sid}"]
        by_id={x.get("stage_id"):x for x in refs if isinstance(x,dict)}
        if set(by_id)!=set(PREDECESSORS[sid]):return 32,[f"predecessors:{sid}"]
        for pred in PREDECESSORS[sid]:
            ref=by_id[pred]
            if ref.get("path")!=paths[pred].name or ref.get("sha256")!=hashes[pred] or ref.get("artifact_version")!=artifacts[pred].get("artifact_version"):
                return 32,[f"binding:{sid}:{pred}"]
    p1,p2,p3,p4,p5,p6,p7=[artifacts[s]["payload"] for s in EXPECTED_STAGE_IDS]
    stage1_findings=requirement_findings(p1,artifacts[EXPECTED_STAGE_IDS[0]]["artifact_version"])
    if stage1_findings:return 33,stage1_findings
    stage2_findings=evidence_findings(p2,p1)
    if stage2_findings:return 33,stage2_findings
    source_ids={x.get("source_id") for x in p2.get("sources",[]) if isinstance(x,dict)}
    if any(not set(x.get("source_ids",[])) or not set(x.get("source_ids",[])).issubset(source_ids) for x in p2.get("claims",[])):
        return 33,["stage2_claim_sources"]
    c2=p2.get("completion",{})
    if c2.get("feasibility_basis_complete") is not True or c2.get("conflicts_resolved_or_durable") is not True:return 33,["stage2_completion"]
    evidence_ids={x.get("claim_id") for x in p2.get("claims",[]) if isinstance(x,dict)}
    feasibility_ids={x["claim_id"] for x in p2["claims"] if x["purpose"]=="FEASIBILITY" and x["evidence_kind"] not in {"UNKNOWN","BACKGROUND_REFERENCE"}}
    result_ids=set()
    for claim in p3.get("claims",[]):
        result_ids.add(claim.get("result_claim_id"))
        ids=set(claim.get("evidence_claim_ids",[]))
        if not ids or not ids.issubset(evidence_ids):return 33,["stage3_claim_evidence"]
        if not ids.intersection(feasibility_ids):return 33,["stage3_feasibility_support_required"]
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
    # Surfaced, not swallowed. An earlier revision collected these and returned an
    # empty list, so a run validated without a candidate looked identical to one
    # whose deliberation instance had actually been checked.
    return 0,deliberation_notes

def prohibited_output(repo_root:Path,output_root:Path)->bool:
    try:rel=output_root.resolve().relative_to(repo_root.resolve()).as_posix().rstrip("/")+"/"
    except ValueError:return False
    return any(rel.startswith(prefix) for prefix in PROHIBITED_OUTPUT_PREFIXES)

def _draft_run(run_doc, run_id):
    if (run_doc.get("run_id") != run_id or run_doc.get("lifecycle") != "candidate_pending_validation"
            or {"closure_record", "final_stage_completion_commit", "completion_pointer",
                "human_acceptance", "status"} & run_doc.keys()):
        raise ValueError("draft_run_required")


def _draft_artifact(artifact, run_id, sid, schemas):
    if (artifact.get("schema_version"), artifact.get("run_id"), artifact.get("stage_id"),
            artifact.get("artifact_kind"), artifact.get("status")) != (
            "citystate.workflow.artifact.v1", run_id, sid, schemas[sid]["artifact_kind"], "planned"):
        raise ValueError(f"planned_artifact_identity:{sid}")
    if not positive_int(artifact.get("artifact_version")):
        raise ValueError(f"artifact_version_invalid:{sid}")
    control = artifact.get("stage_control", {})
    if not isinstance(control, dict) or {"plan_acceptance", "completion_acceptance"} & control.keys():
        raise ValueError(f"formal_stage_control:{sid}")


def _draft_manifest_entries(manifest, run_id):
    if (manifest.get("schema_version"), manifest.get("workflow_id"), manifest.get("workflow_version"),
            manifest.get("run_id")) != ("citystate.workflow.run_manifest.v1", EXPECTED_WORKFLOW_ID, 1, run_id):
        raise ValueError("manifest_identity")
    if {"status", "final_stage_completion_commit", "completion_acceptance", "plan_acceptance"} & manifest.keys():
        raise ValueError("draft_manifest_required")
    entries = manifest["artifacts"]
    stages = [entry["stage_id"] for entry in entries]
    if not stages or stages != EXPECTED_STAGE_IDS[:len(stages)]:
        raise ValueError("manifest_stage_order")
    return entries


def _draft_version_floors(repo, head, relative, run_id, owner, source, schemas):
    if source.git(repo, "rev-parse", "--is-shallow-repository").strip() != b"false":
        raise ValueError("full_candidate_history_required")
    floors = {}
    commits = source.git(repo, "log", "--full-history", "--format=%H", head, "--", relative).decode().splitlines()
    for commit in commits:
        def read_optional(name):
            path = f"{relative}/{name}"
            if not source.git(repo, "ls-tree", "-z", commit, "--", path):
                return None
            return source.load_yaml_text(source.tracked_blob(repo, commit, path).decode("utf-8"))

        historical_run = read_optional("run.yml")
        if historical_run is not None:
            _draft_run(historical_run, run_id)
        manifest = read_optional("manifest.yml")
        if manifest is None:
            continue
        for entry in _draft_manifest_entries(manifest, run_id):
            sid, name, version = entry["stage_id"], entry["path"], entry["artifact_version"]
            if not owner._scope_path(name) or "/" in name or not positive_int(version):
                raise ValueError(f"historical_artifact_binding:{sid}")
            artifact = read_optional(name)
            if artifact is None:
                raise ValueError(f"historical_artifact_absent:{sid}")
            _draft_artifact(artifact, run_id, sid, schemas)
            floors[sid] = max(floors.get(sid, 0), version, artifact["artifact_version"])
    return floors


def sync_candidate(run_root: Path, repo_root: Path, *, apply: bool = False) -> tuple[int, list[str]]:
    """Rebind draft artifact bytes only. This command never validates acceptance."""
    source_errors = ()
    try:
        repo_root = repo_root.resolve()
        run_root = run_root.absolute()
        relative = run_root.relative_to(repo_root).as_posix()
        if relative == "." or run_root.resolve() != run_root or prohibited_output(repo_root, run_root):
            raise ValueError("unsafe_candidate_directory")
        owner = load_deliberation_validator(Path(__file__).resolve().parents[4])
        git = owner.task_scope_support()
        source_errors = (git.VerificationError,)
        if not owner._scope_path(relative):
            raise ValueError("unsafe_candidate_directory")
        if Path(git.git(repo_root, "rev-parse", "--show-toplevel").decode().strip()).resolve() != repo_root:
            raise ValueError("repository_root_required")
        head = git.git(repo_root, "rev-parse", "HEAD").decode().strip()
        git.candidate_id(repo_root, head)
        def committed_yaml(path):
            return yaml.safe_load(git.tracked_blob(repo_root, head, path.relative_to(repo_root).as_posix()))

        roots = committed_yaml(repo_root / CONTRACT_PATH)["run_roots"]
        parents = {roots[key].split("/<run-id>/")[0] for key in ("shared_os_development", "domain_workflow")}
        if relative.rpartition("/")[0] not in parents or run_root.name.casefold() == "_runtime":
            raise ValueError("candidate_run_root_required")
        schemas = payload_schemas(repo_root, committed_yaml)
        # Search reachable history too: removing a receipt in the working tree
        # must not turn an accepted Run back into a writable draft.
        protected = r'(plan_acceptance|completion_acceptance|final_stage_completion_commit)["\x27]?[[:space:]]*:'
        if git.git(repo_root, "log", "--all", "-1", "--format=%H", "-G", protected, "--", relative).strip():
            raise ValueError("formal_history_present")
        formal_names = {"plan_acceptance.yml", "completion_acceptance.yml", "workflow_completion.yml"}
        formal_paths = [f":(glob){relative}/**/{name}" for name in sorted(formal_names)]
        if git.git(repo_root, "log", "--all", "--full-history", "-1", "--format=%H", "--", *formal_paths).strip():
            raise ValueError("formal_history_present")
        if any(p.name.casefold() in formal_names for p in run_root.rglob("*")):
            raise ValueError("formal_record_present")

        original = {}
        updated = {}

        def read(name):
            if not owner._scope_path(name) or "/" in name:
                raise ValueError("artifact_path_must_be_local")
            path = run_root / name
            if path.is_symlink() or path.resolve() != path or not path.is_file() or path in original:
                raise ValueError(f"invalid_or_duplicate_artifact:{name}")
            original[path] = path.read_bytes()
            doc = git.load_yaml_text(original[path].decode("utf-8"))
            if not isinstance(doc, dict):
                raise ValueError(f"artifact_mapping:{name}")
            return path, doc

        def refresh(path, before, after):
            if before != after:
                updated[path] = yaml.safe_dump(after, allow_unicode=True, sort_keys=False, width=120).encode("utf-8")
            return hashlib.sha256(updated.get(path, original[path])).hexdigest()

        _, run_doc = read("run.yml")
        _draft_run(run_doc, run_root.name)
        normalized = git.normalize_packet(git.load_yaml_text(
            owner._scope_blob(repo_root, head, run_doc.get("task_packet_ref"), git).decode("utf-8")))
        packet = normalized.body
        branch = git.git(repo_root, "symbolic-ref", "HEAD").decode().strip()
        if (normalized.source_format != "wrapped_v1" or packet["task_id"] != run_doc.get("task_id")
                or not owner._scope_path(packet["branch"]) or packet["branch"] in {"master", "main"}
                or branch != f"refs/heads/{packet['branch']}"):
            raise ValueError("draft_task_scope_mismatch")
        git.git(repo_root, "merge-base", "--is-ancestor", packet["exact_base_sha"], head)
        allowed = packet["allowed_changed_paths"]
        if not all(owner._scope_path(path, pattern=True) for path in allowed):
            raise ValueError("invalid_candidate_allowlist")
        manifest_path, manifest = read("manifest.yml")
        entries = _draft_manifest_entries(manifest, run_root.name)
        for path in [manifest_path.name, *(entry["path"] for entry in entries)]:
            if not owner._scope_path(path) or "/" in path or not owner._scope_allowed(f"{relative}/{path}", allowed):
                raise ValueError(f"candidate_path_not_authorized:{path}")
        floors = _draft_version_floors(repo_root, head, relative, run_root.name, owner, git, schemas)
        bindings = {}
        for entry in entries:
            sid = entry["stage_id"]
            path, artifact = read(entry["path"])
            version = artifact["artifact_version"]
            _draft_artifact(artifact, run_root.name, sid, schemas)
            if (not positive_int(entry["artifact_version"])
                    or version < max(entry["artifact_version"], floors.get(sid, 0))):
                raise ValueError(f"artifact_version_regression_or_invalid:{sid}")
            refs = artifact["input_refs"]
            if not isinstance(refs, list) or sorted(ref["stage_id"] for ref in refs) != sorted(PREDECESSORS[sid]):
                raise ValueError(f"predecessors:{sid}")
            for ref in refs:
                expected = bindings[ref["stage_id"]]
                if ref["path"] != expected["path"] or not positive_int(ref["artifact_version"]) or ref["artifact_version"] > expected["artifact_version"]:
                    raise ValueError(f"dependency_identity_or_version:{sid}:{ref['stage_id']}")
            new_refs = [ref | bindings[ref["stage_id"]] for ref in refs]
            digest = refresh(path, artifact, artifact | {"input_refs": new_refs})
            bindings[sid] = {"path": path.name, "artifact_version": version, "sha256": digest}
        refresh(manifest_path, manifest, manifest | {"artifacts": [
            entry | bindings[entry["stage_id"]] for entry in entries
        ]})
        diff = ["".join(difflib.unified_diff(
            original[path].decode().splitlines(keepends=True), new.decode().splitlines(keepends=True),
            fromfile=path.name, tofile=path.name,
        )) for path, new in updated.items()]
        if not apply:
            return (1 if updated else 0), diff
        if (git.git(repo_root, "rev-parse", "HEAD").decode().strip() != head
                or git.git(repo_root, "symbolic-ref", "HEAD").decode().strip() != branch or any(
               path.is_symlink() or path.resolve() != path or path.read_bytes() != data
               for path, data in original.items())):
            raise ValueError("candidate_changed_during_sync")
        # Each replacement is atomic. Manifest goes last so an interrupted run
        # cannot advertise hashes for replacements that have not yet happened.
        for path, data in updated.items():
            with tempfile.NamedTemporaryFile(dir=run_root, delete=False) as tmp:
                temporary = Path(tmp.name)
                try:
                    tmp.write(data)
                    tmp.close()
                    os.replace(temporary, path)
                finally:
                    temporary.unlink(missing_ok=True)
        return 0, diff
    except (OSError, ValueError, TypeError, KeyError, AttributeError, yaml.YAMLError, RuntimeError, *source_errors) as exc:
        return 33, [f"candidate_sync:{exc}"]

def materialize_pilot(repo_root:Path,output_root:Path)->tuple[int,list[str]]:
    if prohibited_output(repo_root,output_root):return 40,["canonical_output_root"]
    source=repo_root/PILOT_PATH
    if output_root.exists() and any(output_root.iterdir()):return 40,["output_not_empty"]
    output_root.mkdir(parents=True,exist_ok=True)
    for item in source.iterdir():
        if item.is_file():shutil.copy2(item,output_root/item.name)
    # Materialising the fixture checks its shape. The copy has no commit history
    # of its own, so there is nothing for the authoritative validator to judge and
    # this is not, and must not be reported as, a governed-run validation.
    code,findings=validate_structure(output_root,repo_root)
    if code:return code,findings
    manifest=load_yaml(output_root/"manifest.yml")
    completion={"schema_version":"citystate.workflow.completion.v1","run_id":manifest.get("run_id"),"workflow_id":manifest.get("workflow_id"),"status":"complete","final_stage":EXPECTED_STAGE_IDS[-1],"artifacts":manifest.get("artifacts"),"default_deliberation_route":"dormant","canonical_live_state_created":False}
    (output_root/"workflow_completion.yml").write_text(yaml.safe_dump(completion,allow_unicode=True,sort_keys=False,width=120),encoding="utf-8",newline="\n")
    return 0,[]

def next_business_action(state:dict)->dict:
    """Choose ONE existing business step from explicit domain observations.

    Opt-in engineering path: no tool execution, polling, permission issuance or
    durable journal. The domain owns facts, exact scope/CAS, resource reservations
    and reconciliation across restarts. As in PR23, Done is independent of child
    flags; unlike its ordered walk, a blocked node does not hide safe siblings.
    """
    import copy
    if not isinstance(state,dict) or not state.get("goal"):
        raise ValueError("Business goal required")
    context=state["context"];facts=state["facts"];steps=state["steps"]
    if not isinstance(context,dict) or not isinstance(facts,dict) or not isinstance(steps,list):
        raise ValueError("Context/facts mappings and finite steps required")
    valid={};invalidated={}
    for key,observation in facts.items():
        if not isinstance(observation,dict) or not isinstance(observation.get("bindings"),dict) or not observation.get("source_ref"):
            raise ValueError(f"Fact requires source_ref and explicit validity bindings: {key}")
        changed=[k for k,v in observation["bindings"].items() if k not in context or context[k]!=v]
        if changed:invalidated[key]=changed
        else:valid[key]=observation.get("value")
    def observed(key):return valid.get(key) is True
    by_id={}
    priority={"diagnostic":0,"preflight":1,"business":2,"optional":3}
    for step in steps:
        if not isinstance(step,dict) or not step.get("step_id") or not step.get("goal") or step["step_id"] in by_id:
            raise ValueError("Unique step IDs and business goals required")
        if step.get("kind") not in priority or not isinstance(step.get("requires"),list) or not isinstance(step.get("depends_on"),list) or not step.get("done"):
            raise ValueError("Step kind, Ready requirements, dependencies and independent Done required")
        by_id[step["step_id"]]=step
    for step in steps:
        if not set(step["depends_on"]).issubset(by_id):raise ValueError("Unknown step dependency")
    # Reuse the Stage05 finite dependency invariant, without starting a scheduler.
    resolved=set()
    while True:
        new={k for k,s in by_id.items() if set(s["depends_on"]).issubset(resolved)}-resolved
        if not new:break
        resolved.update(new)
    if resolved!=set(by_id):raise ValueError("Business dependency cycle")
    choices=copy.deepcopy(state.get("approved_choices",{}))
    report={"goal":state["goal"],"status":"BLOCKED","step_id":None,
            "invalidated":invalidated,"reused":sorted(valid),"blocked":{},
            "approved_choices":choices,"authority_effect":"none"}
    if observed(state["parent_done"]):
        report["status"]="DONE"
        return report
    candidates=[];unfinished=0
    for position,step in enumerate(steps):
        key=step["step_id"]
        if observed(step["done"]):continue
        unfinished+=1;reasons=[]
        if step.get("resource") in state.get("unknown_resources",[]):reasons.append("RECONCILE: domain journal/readback required for resource")
        if key in state.get("attempted",[]):reasons.append("RECONCILE: attempted without observed Done; no replay")
        if step.get("channel") in state.get("stopped_channels",[]):reasons.append("Human stopped channel")
        blocker=state.get("blockers",{}).get(step.get("scope"))
        if blocker and step["kind"]!="diagnostic":reasons.append(str(blocker))
        missing=[name for name in step["requires"] if not observed(name)]
        if missing:reasons.append("Ready missing/false/stale: "+",".join(missing))
        if any(not observed(by_id[d]["done"]) for d in step["depends_on"]):reasons.append("Unfinished predecessor")
        if "choice_ref" in step:
            ref=step["choice_ref"]
            if ref not in choices:reasons.append("Missing approved business choice")
            elif "proposed_choice" in step and step["proposed_choice"]!=choices[ref]:reasons.append("Approved business choice changed; do not reseed on runtime rebind")
        if reasons:report["blocked"][key]=reasons
        else:candidates.append((priority[step["kind"]],position,key))
    # kind alone gives preparation no privilege over real Ready work.
    eligible=[c for c in candidates if by_id[c[2]]["kind"]=="business"]
    if not eligible:
        pending=[k for k,s in by_id.items() if s["kind"]=="business" and not observed(s["done"])]
        if pending:
            # Only declared, unfinished predecessors can unblock this business.
            # A shared scope or a diagnostic/preflight label is not causality.
            needed=set()
            while pending:
                for dep in by_id[pending.pop()]["depends_on"]:
                    if dep not in needed and not observed(by_id[dep]["done"]):
                        needed.add(dep);pending.append(dep)
            eligible=[c for c in candidates if c[2] in needed]
        else:
            # A task may itself consist of required checks (e.g. verification).
            # A blocked required check must not fall back to optional busywork.
            required=any(s["kind"]!="optional" and not observed(s["done"]) for s in steps)
            eligible=[c for c in candidates if not required or by_id[c[2]]["kind"]!="optional"]
        for c in candidates:
            if c not in eligible:report["blocked"][c[2]]=["Deferred: unrelated to unfinished required work"]
    if eligible:
        report.update(status="READY",step_id=min(eligible)[2])
    elif not unfinished:report["status"]="PARENT_INCOMPLETE"
    return report


def business_time_quality(metrics:dict,*,first_event=None,first_blocker=None,capture_end=None)->dict:
    """Stage07 labels existing evidence; it neither collects nor monitors events.

    Counts/durations come from an existing source report. Reported ON intervals
    and duration sums are NEVER interpreted as unique wall or reasoning time.
    """
    from decimal import Decimal, InvalidOperation
    from datetime import datetime
    def seconds(value):
        try:number=Decimal(str(value))
        except InvalidOperation as exc:raise ValueError("Numeric time required") from exc
        if not number.is_finite() or number<0:raise ValueError("Nonnegative finite time required")
        return number
    counts={k:metrics.get(k) for k in ("tool_call","tool_result","command","file_change","mcp")}
    if any(v is not None and (type(v) is not int or v<0) for v in counts.values()):raise ValueError("Nonnegative integer layer counts required")
    executions=None if any(counts[k] is None for k in ("command","file_change","mcp")) else sum(counts[k] for k in ("command","file_change","mcp"))
    def supplied_seconds(key):return None if metrics.get(key) is None else str(seconds(metrics[key]))
    result={"layers":counts,"execution_items":executions,
            "records":None if any(v is None for v in counts.values()) else sum(counts.values()),
            "command_seconds_sum":supplied_seconds("command_seconds"),
            "mcp_seconds_sum":supplied_seconds("mcp_seconds"),
            "monitor_on_reported_seconds":None if metrics.get("monitor_on_seconds") is None else str(sum((seconds(v) for v in metrics["monitor_on_seconds"]),Decimal(0))),
            "monitor_on_basis":"REPORTED_SOURCE_INTERVALS_NOT_INDEPENDENT_WALL_MEASUREMENT",
            "capture_source_seconds":supplied_seconds("capture_seconds"),
            "off_intervals":metrics.get("off_intervals","UNKNOWN"),
            "human_wait_seconds":supplied_seconds("human_wait_seconds"),
            "unique_tool_wall_seconds":None,"unobserved_attribution":"UNKNOWN","safety_effect":"none"}
    def span(a,b):
        start=datetime.fromisoformat(a.replace("Z","+00:00"));end=datetime.fromisoformat(b.replace("Z","+00:00"))
        if start.utcoffset() is None or end.utcoffset() is None:raise ValueError("Evidence timestamps require explicit timezone")
        delta=end-start
        value=Decimal(delta.days*86400+delta.seconds)+Decimal(delta.microseconds)/1000000
        return str(seconds(value))
    if first_event and first_blocker:result["event_span_to_blocker_seconds"]=span(first_event,first_blocker)
    if capture_end and first_blocker:result["capture_to_blocker_seconds"]=span(capture_end,first_blocker)
    return result


def main()->int:
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=("static","validate","materialize-pilot","sync-candidate","next-business-action","business-time-quality"))
    parser.add_argument("target");parser.add_argument("output",nargs="?")
    parser.add_argument("--json-output",action="store_true");parser.add_argument("--skip-subvalidators",action="store_true",help=argparse.SUPPRESS)
    parser.add_argument("--repo-root",type=Path,default=None)
    parser.add_argument("--apply",action="store_true",help="apply sync-candidate changes; default previews only")
    parser.add_argument("--candidate",default=None,
                        help="exact commit whose run artifacts and acceptance history are judged; "
                             "required for full validation, independent of dirty checkout bytes")
    args=parser.parse_args()
    if args.apply and args.command!="sync-candidate":parser.error("--apply requires sync-candidate")
    if args.command in {"next-business-action","business-time-quality"}:
        try:
            source=json.loads(Path(args.target).read_text(encoding="utf-8"))
            result=next_business_action(source) if args.command=="next-business-action" else business_time_quality(**source)
        except (KeyError,TypeError,ValueError,OSError) as exc:
            print(json.dumps({"status":"INPUT_ERROR","reason":str(exc)},ensure_ascii=False))
            return 33
        print(json.dumps(result,ensure_ascii=False))
        return 0
    if args.command=="static":code,findings=validate_static(Path(args.target),not args.skip_subvalidators)
    elif args.command=="validate":code,findings=validate_run(Path(args.target),args.repo_root,args.candidate)
    elif args.command=="sync-candidate":
        code,findings=sync_candidate(Path(args.target),args.repo_root or Path.cwd(),apply=args.apply)
    else:
        if not args.output:parser.error("materialize-pilot requires output")
        code,findings=materialize_pilot(Path(args.target),Path(args.output))
    if args.json_output:print(json.dumps({"command":args.command,"exit_code":code,"findings":findings},ensure_ascii=False))
    elif findings:
        for finding in findings:print(finding,file=sys.stderr)
    return code
if __name__=="__main__":raise SystemExit(main())
