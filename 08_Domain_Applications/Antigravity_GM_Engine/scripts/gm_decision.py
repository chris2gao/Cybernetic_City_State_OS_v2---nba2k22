"""Candidate M3B research workflow. Local derived artifacts only; V4 not enabled."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gm_data_access import AccessError
from gm_data_access.query import QuerySession
from gm_data_access.decision_inputs import coaching_source
from gm_data_access.decision_inputs import prepare_native_artifacts
from gm_core import decision_protocol as protocol
from gm_core import analysis_packet
from gm_core.workbench_common import page, export_files, same_source
from gm_workbench.store import Store
from gm_analysis import read_input


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('begin','template','submit-review','submit-alternatives','submit-offer','respond-offer','record-coach-event','submit-blueprint','record-evolution','select','validate','finalize','show','team','artifact','export'))
    p.add_argument('--workbench',type=Path,default=ROOT/'_exports/dev10_m3/gm_workbench.sqlite')
    p.add_argument('--query-root',type=Path,default=ROOT/'database/query_snapshots')
    p.add_argument('--published-root',type=Path,default=ROOT/'published')
    p.add_argument('--run'); p.add_argument('--analysis-run'); p.add_argument('--career')
    p.add_argument('--mode',choices=('development',),default='development')
    p.add_argument('--season-phase',choices=('UNKNOWN','REGULAR','PLAYOFFS','OFFSEASON'),default='UNKNOWN',help='Explicit player context; does not advance the game or implement offseason control')
    p.add_argument('--input',type=Path); p.add_argument('--expected-revision',type=int)
    p.add_argument('--output-context',type=Path); p.add_argument('--output',type=Path)
    p.add_argument('--constraints',type=Path,help='Source-bound restrictive player rules with context_evidence; cannot grant approval')
    p.add_argument('--team'); p.add_argument('--players',action='store_true')
    p.add_argument('--limit',type=int,default=20); p.add_argument('--cursor')
    p.add_argument('--kind',choices=('TEAM_REVIEW','ALTERNATIVES','OFFER','RESPONSE','PORTFOLIO','VALIDATION','FINAL','STRATEGY_CANDIDATE','HYPOTHESIS','COACH_EVENT','BPTI_BLUEPRINT','BPTI_EVOLUTION'))
    p.add_argument('--artifact-id'); p.add_argument('--artifact-revision',type=int)
    p.add_argument('--section',help='artifact: dotted stored-object path, including list indices; results remain paginated')
    return p


def check_source(a,analysis):
    analysis_packet.require_gm_packet(analysis)
    b=analysis['source_binding']; s=QuerySession(a.query_root,a.published_root,b['career_id'],b['batch_id'])
    try:
        s.require_gm_sanitized()
        if not same_source(s.binding,b):
            raise ValueError('SOURCE_CHANGE_REBASE_REQUIRED')
    finally:
        s.close()


def run(a):
    writes=a.action not in ('show','template','team','artifact','export')
    with Store(a.workbench,readonly=not writes) as store:
        if a.action=='template':
            return protocol.templates(store.analysis_context(a.analysis_run),a.team)
        if a.action=='begin':
            analysis=store.analysis_context(a.analysis_run)
            check_source(a,analysis)
            bases=[]
            for t in analysis['teams']:
                for ref in t['strategy_refs']:
                    state=store.load_state(analysis['source_binding']['career_id'],str(t['team_id']),ref['revision'])
                    if state['state_id']!=ref['state_id']:
                        raise ValueError('STRATEGY_REFERENCE_CHANGED')
                    bases.append(state)
            if a.output_context:
                context_path=a.output_context.resolve()
                if context_path.exists() or any(x.casefold() in {'published','saves','query_snapshots','seasons'} for x in context_path.parts):
                    raise ValueError('NEW_CONTEXT_FILE_OUTSIDE_FACTS_REQUIRED')
            d=protocol.begin(analysis,a.run,bases,read_input(a.constraints) if a.constraints else None,a.season_phase)
            d=store.save_decision(d)
            if a.output_context:
                context_path.parent.mkdir(parents=True,exist_ok=True)
                with context_path.open('x',encoding='utf-8') as stream:
                    json.dump(protocol.summary(d),stream,ensure_ascii=False,indent=2)
            return protocol.summary(d)
        if not a.run:
            raise ValueError('RUN_REQUIRED')
        d=store.load_decision(a.run)
        analysis=store.analysis_context(d['analysis_run_id'])
        analysis_packet.require_gm_packet(analysis)
        if a.career and a.career!=d['source_binding']['career_id']:
            raise ValueError('CAREER_MISMATCH')
        if writes:
            if a.expected_revision is None:
                raise ValueError('EXPECTED_REVISION_REQUIRED')
            if a.action=='validate':
                check_source(a,analysis)
                finance=store.load_run(analysis['finance_run_id']) if analysis['finance_run_id'] else None
                requests=[]
                selected=d['artifacts'].get('PORTFOLIO',{}).get('selected')
                native=None
                if selected and analysis.get('tactical_version'):
                    from gm_core.decision_portfolio import inspect
                    selection=inspect(selected['payload'],d['artifacts'],analysis,d)
                    if not any(i['effect']=='BLOCK_FINAL' for i in selection['issues']):
                        native=prepare_native_artifacts(analysis,d,selection,a.query_root,a.published_root)
                elif selected:
                    from gm_core.decision_portfolio import resolve
                    _,actions,_,_=resolve(selected['payload'],d['artifacts'],analysis)
                    requests=[r for action in actions if action['kind']=='COACHING' for r in action['requests']]
                snapshot=coaching_source(a.published_root,d['source_binding'],requests) if requests else None
                updated,artifacts=protocol.validate(d,analysis,finance,snapshot,native)
            elif a.action=='finalize':
                check_source(a,analysis)
                updated,artifacts=protocol.finalize(d,analysis)
            else:
                payload=read_input(a.input)
                options={}
                if a.action in ('submit-blueprint','record-evolution'):
                    try:
                        check_source(a,analysis)
                    except (ValueError,OSError,AccessError) as exc:
                        return dict(status='HOLD',reason=str(exc)[:250],execution_authorized=False)
                if a.action=='submit-blueprint':
                    from gm_core.knowledge import Knowledge
                    options['bpti_index']=Knowledge(ROOT/'web_gm/knowledge').bpti()
                if a.action=='record-evolution':
                    ref=payload.get('previous_ref')
                    if ref:
                        previous_run=store.load_decision(ref['run_id'])
                        if previous_run['source_binding']['career_id']!=d['source_binding']['career_id'] or str(ref['artifact_id'])!=str(payload['team_id']):
                            raise ValueError('BPTI_PREVIOUS_EVOLUTION_CAREER_TEAM_MISMATCH')
                        options['previous_evolution']=store.artifact_history(ref['run_id'],'BPTI_EVOLUTION',str(ref['artifact_id']),ref['revision'])
                        # Recover the trusted stored context for pre-F2 immutable artifacts.
                        options['previous_evolution']['history_branch_context']=previous_run['context'].get('history_branch_context')
                updated,artifacts=protocol.apply(d,analysis,a.action,payload,**options)
            d=store.save_decision(updated,a.expected_revision,artifacts)
            result=protocol.summary(d)
            if a.action=='validate':
                v=d['artifacts']['VALIDATION']['current']['payload']
                result['validation']={k:v[k] for k in ('report_id','valid_for_finalization','issues','bilateral_checks')}
                result['specific_approval_item_count']=len(v['specific_approval_items'])
                result['specific_approval_items']=[dict(item_id=i['item_id'],kind=i['kind'],executor_readiness=i['executor_readiness'],
                    digest=i.get('digest',i.get('batch_digest')),action_count=len(i.get('action_ids',[]))) for i in v['specific_approval_items'][:20]]
                result['details']='artifact --kind VALIDATION --artifact-id current --section specific_approval_items'
            return result
        meta=dict(run_id=a.run,revision=d['revision'],source_binding=d['source_binding'],execution_authorized=False)
        if a.action=='show':
            return protocol.summary(d)
        if a.action=='team':
            t=analysis_packet.team(analysis,a.team)
            r=d['artifacts'].get('TEAM_REVIEW',{}).get(str(t['team_id']))
            if a.players:
                return dict(**meta,**page(r['payload']['player_assessments'] if r else [],[a.run,d['revision'],'assessments',t['team_id']],a.limit,a.cursor))
            return dict(**meta,team_id=t['team_id'],team=t['team'],review={k:v for k,v in r['payload'].items() if k!='player_assessments'} if r else None,
                alternatives=d['artifacts'].get('ALTERNATIVES',{}).get(str(t['team_id'])))
        if a.action=='artifact':
            if not a.kind or not a.artifact_id:
                raise ValueError('KIND_AND_ARTIFACT_ID_REQUIRED')
            obj=store.artifact_history(a.run,a.kind,a.artifact_id,a.artifact_revision) if a.artifact_revision else protocol.get(d,a.kind,a.artifact_id)['payload']
            if a.section:
                for key in a.section.split('.'):
                    obj=obj[int(key)] if isinstance(obj,list) else obj[key]
                rows=obj if isinstance(obj,list) else ([dict(field=k,value=v) for k,v in obj.items()] if isinstance(obj,dict) else [dict(value=obj)])
            else:
                rows=[dict(field=k,value=v if not isinstance(v,(list,dict)) else None,
                    child_count=len(v) if isinstance(v,(list,dict)) else None,
                    next_section=k if isinstance(v,(list,dict)) else None) for k,v in obj.items()]
            return dict(**meta,**page(rows,[a.run,d['revision'],a.kind,a.artifact_id,a.artifact_revision,a.section],a.limit,a.cursor))
        if not a.output:
            raise ValueError('EXPLICIT_NEW_EXPORT_DIRECTORY_REQUIRED')
        check_source(a,analysis)
        files={'index.json':protocol.summary(d),'checkpoint.json':dict(revision=d['revision'],phase_progress=protocol.progress(d),
            artifact_refs=[dict(kind=k,artifact_id=aid,revision=row['revision']) for k,rows in d['artifacts'].items() for aid,row in rows.items()])}
        files['bpti_artifacts.json']=[dict(kind=k,artifact_id=aid,revision=row['revision'],payload=row['payload'])
            for k in ('BPTI_BLUEPRINT','BPTI_EVOLUTION') for aid,row in d['artifacts'].get(k,{}).items()]
        if d['current_final_version']:
            f=store.artifact_history(a.run,'FINAL','final',d['current_final_version'])
            files.update({'team_summaries.json':f['team_summaries'],'selected_items.json':dict(specific_approval_items=f['specific_approval_items'],research_items=f['research_items'],holds=f['holds']),
                'hypotheses.json':f['hypotheses'],'strategy_candidates.json':f['strategy_candidates'],'offline_artifacts.json':f['generated_artifact_refs']})
            for index,artifact in enumerate(f['generated_artifact_refs']):
                if artifact.get('kind')=='DEV14_SPARSE_INTENT' and artifact.get('status')=='OFFLINE_PREPARED':
                    files['intent_'+str(index+1)+'.json']=artifact['intent']
                    files['approval_tuple_'+str(index+1)+'.json']=artifact['approval_tuple']
        return export_files(a.output,files)


def main():
    try:
        print(json.dumps(run(parser().parse_args()),ensure_ascii=False,allow_nan=False))
        return 0
    except (ValueError,KeyError,TypeError,OSError,sqlite3.Error,AccessError) as exc:
        print(json.dumps(dict(status=getattr(exc,'code','M3_INPUT_OR_STORE_ERROR'),message=str(exc)[:250]),ensure_ascii=False))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
