"""Task-selected project discovery and same-candidate index checks; no state service."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

_PRMS=Path(__file__).resolve().parents[2]/"boot/context_management/prms/source.py"
_spec=importlib.util.spec_from_file_location("project_context_git_source",_PRMS)
_source=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_source)
GitSource=_source.GitSource
safe_path=_source.safe_path

def text(x):return isinstance(x,str) and bool(x.strip())
def exact_commit(x):return isinstance(x,str) and re.fullmatch(r"[0-9a-f]{40}",x) is not None
def _path(base,ref):
    if not text(ref):raise ValueError("source_reference_required")
    path=(Path(base)/ref).as_posix() if base else ref
    return safe_path(path.rstrip("/"))
def _matches(path,declared):
    return path==declared.rstrip("/") or path.startswith(declared.rstrip("/")+"/")

def discover(source,index_path,registry_path,selected_modules=()):
    """Reuse frozen PRMS source reads; directory inventories do not preload bodies."""
    if not index_path or not registry_path:
        return {"status":"PROJECT_CATALOG_NOT_DECLARED","modules":[],"body_reads":[],"action_authorized":False}
    source.read(safe_path(index_path))
    registry=source.json(safe_path(registry_path));base=registry.get("module_base","").rstrip("/")
    if base:safe_path(base)
    modules=registry.get("modules")
    if not isinstance(modules,list) or not modules:raise ValueError("module_records_required")
    cards=[];ids=set();body_reads=[];selected=set(selected_modules)
    for module in modules:
        identifier=module.get("id") if isinstance(module,dict) else None
        if not text(identifier) or identifier in ids:raise ValueError("module_identity_missing_or_duplicate")
        ids.add(identifier)
        refs=[]
        for field in ("docs","artifacts"):
            values=module.get(field,[])
            if not isinstance(values,list):raise ValueError("module_references_must_be_list")
            for ref in values:
                # Core/other-project navigation is disclosed, never loaded through a domain body.
                if text(ref) and ".." in ref.split("/"):
                    refs.append({"reference":ref,"status":"EXTERNAL_NAVIGATION_NOT_LOADED"});continue
                path=_path(base,ref)
                members={p:m["blob"] for p,m in source.tree.items() if _matches(p,path)}
                refs.append({"path":path,"kind":field,"status":"PRESENT" if members else "SOURCE_MISSING",
                             "members":len(members),"fingerprint":hashlib.sha256(json.dumps(members,sort_keys=True).encode()).hexdigest()})
                if identifier in selected and field=="docs" and not ref.endswith("/"):
                    _,proof=source.read(path);body_reads.append(proof)
        cards.append({"id":identifier,"name":module.get("name"),"declared_maturity":module.get("status","UNKNOWN"),
                      "references":refs,"publication_status":"MODULE_RECORD_NOT_FORMAL_MECHANISM"})
    if not selected.issubset(ids):raise ValueError("selected_module_missing")
    return {"status":"DISCOVERED_NOT_ACTIVATED","repository":source.repository,"commit":source.commit,
            "index_path":index_path,"registry_path":registry_path,"modules":cards,"body_reads":body_reads,
            "action_authorized":False}

def source_status(source,ref,published_master):
    if not isinstance(ref,dict) or ref.get("repository")!=source.repository:
        raise ValueError("source_repository_mismatch")
    if not exact_commit(ref.get("commit")) or not exact_commit(published_master):raise ValueError("exact_source_and_master_required")
    frozen=source.at(ref["commit"]);_,proof=frozen.read(safe_path(ref.get("path","")))
    code=subprocess.run(["git","merge-base","--is-ancestor",ref["commit"],published_master],cwd=source.root,capture_output=True).returncode
    if code not in (0,1):raise ValueError("publication_ancestry_unreadable")
    actual="MASTER_INCLUDED" if code==0 else "SOURCE_BRANCH_NOT_MASTER"
    if ref.get("publication_status")!=actual:raise ValueError("source_publication_status_mismatch")
    return {"actual_publication_status":actual,"source":proof,"action_authorized":False}

def inspect_sync(base,candidate,index_path,registry_path,affected_module_ids):
    """Compare exact Git trees and per-module records, not a claimed sync flag."""
    old=base.json(registry_path) if registry_path in base.tree else {"modules":[]}
    new=candidate.json(registry_path)
    modules={m["id"]:m for m in new.get("modules",[])}
    previous={m["id"]:m for m in old.get("modules",[])}
    if len(modules)!=len(new.get("modules",[])):raise ValueError("duplicate_module_id")
    declared=set(affected_module_ids)
    if not declared.issubset(modules):raise ValueError("affected_module_missing")
    changed={p for p in set(base.tree)|set(candidate.tree) if base.tree.get(p)!=candidate.tree.get(p)}
    derived=set();basepath=new.get("module_base","").rstrip("/")
    for identifier,module in modules.items():
        for ref in module.get("artifacts",[]):
            if text(ref) and ".." in ref.split("/"):continue
            path=_path(basepath,ref)
            if any(_matches(p,path) for p in changed if p not in {index_path,registry_path}):derived.add(identifier)
    pending=set(derived-declared)
    for identifier in declared|derived:
        if identifier in previous and previous[identifier]==modules[identifier]:pending.add(identifier)
    if (declared or derived) and not {index_path,registry_path}.issubset(changed):pending.update(declared|derived)
    return {"status":"INDEX_SYNC_PENDING" if pending else "INDEX_SYNCED_FOR_CANDIDATE",
            "base":base.commit,"candidate":candidate.commit,"affected_module_ids":sorted(derived),
            "declared_module_ids":sorted(declared),"pending_module_ids":sorted(pending),
            "action_authorized":False}

def validate_handoff(record,expected_head):
    required=("result","remaining_gaps","next_steps","plan_actual_deltas","reproduction","evidence_scope")
    if not isinstance(record,dict) or not exact_commit(expected_head) or record.get("source_head")!=expected_head:
        return ["handoff_exact_source_head"]
    findings=["handoff_missing:"+f for f in required if f not in record]
    if not text(record.get("result")):findings.append("handoff_result")
    for field in ("remaining_gaps","next_steps","plan_actual_deltas","reproduction"):
        if not isinstance(record.get(field),list) or any(not text(v) for v in record[field]):findings.append("handoff_list:"+field)
    if not record.get("reproduction"):findings.append("handoff_reproduction_required")
    if not text(record.get("evidence_scope")):findings.append("handoff_evidence_scope")
    if record.get("shared_workspace") is True and (not text(record.get("write_owner")) or not text(record.get("next_owner"))):
        findings.append("handoff_shared_workspace_owner")
    if record.get("final_independent_review") is True:
        if (not text(record.get("reviewer_session")) or not text(record.get("executor_session"))
                or record["reviewer_session"]==record["executor_session"] or record.get("private_executor_context_received") is not False):
            findings.append("handoff_review_isolation")
    return findings

def retry_disposition(signature,repairs,*,external_outcome_unknown=False):
    """Count corrective actions only. Caller preserves raw evidence; no retry is run."""
    if external_outcome_unknown:return "UNKNOWN_OUTCOME_NO_REPLAY"
    if not text(signature) or not isinstance(repairs,list):raise ValueError("failure_signature_and_repairs_required")
    matching=[r for r in repairs if r.get("signature")==signature]
    seen=set()
    for row in matching:
        if not text(row.get("remedy")) or not text(row.get("new_evidence")):return "REPEATED_REMEDY_WITHOUT_EVIDENCE"
        key=(row["remedy"],row["new_evidence"])
        if key in seen:return "REPEATED_REMEDY_WITHOUT_EVIDENCE"
        seen.add(key)
    return "JOINT_RESEARCH_REQUIRED" if len(matching)>=3 else "REPAIR_ALLOWED"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['discover','sync']);p.add_argument('--repo-root',type=Path,required=True)
    p.add_argument('--repository',required=True);p.add_argument('--commit',required=True)
    p.add_argument('--index',required=True);p.add_argument('--registry',required=True)
    p.add_argument('--selected-module',action='append',default=[]);p.add_argument('--affected-module',action='append',default=[])
    p.add_argument('--base');p.add_argument('--output',type=Path)
    a=p.parse_args()
    try:
        source=GitSource(a.repo_root,a.commit,a.repository)
        if a.command=='discover':result=discover(source,a.index,a.registry,a.selected_module)
        else:result=inspect_sync(source.at(a.base),source,a.index,a.registry,a.affected_module)
        code=1 if result['status']=='INDEX_SYNC_PENDING' else 0
    except (ValueError,OSError,KeyError,TypeError,_source.PRMSError) as exc:
        result={'status':'SOURCE_OR_CONTRACT_REJECTED','reason':str(exc),'action_authorized':False};code=3
    raw=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:
        with a.output.open('x',encoding='utf-8') as f:f.write(raw+'\n')
    else:print(raw)
    return code
if __name__=='__main__':raise SystemExit(main())
