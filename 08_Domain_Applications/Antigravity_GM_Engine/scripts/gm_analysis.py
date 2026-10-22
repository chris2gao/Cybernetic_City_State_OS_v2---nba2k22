"""Explicit M3A fact preparation and analysis, over existing static snapshots only."""
import argparse
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gm_data_access import AccessError
from gm_data_access.analysis_inputs import load_inputs, screen
from gm_data_access.query import QuerySession
from gm_core import analysis_packet as packet
from gm_core.workbench_common import page, export_files, reject_authority, same_source
from gm_core.knowledge import Knowledge
from gm_workbench.store import Store


def read_input(path):
    path=Path(path)
    if path.stat().st_size>2_000_000:
        raise ValueError('INPUT_TOO_LARGE')
    return json.loads(path.read_text(encoding='utf-8-sig'))


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('prepare','import-analysis','seal','show','team','players','native','market','screen-market','evidence','export'))
    p.add_argument('--workbench',type=Path,default=ROOT/'_exports/dev10_m3/gm_workbench.sqlite')
    p.add_argument('--query-root',type=Path,default=ROOT/'database/query_snapshots')
    p.add_argument('--published-root',type=Path,default=ROOT/'published')
    p.add_argument('--career'); p.add_argument('--batch'); p.add_argument('--season'); p.add_argument('--run')
    p.add_argument('--node-type',choices=('BOOTSTRAP','SEASON_INITIALIZATION','CHECKPOINT'))
    p.add_argument('--previous-batch'); p.add_argument('--history-context',help='Explicit comparable history branch/context key')
    p.add_argument('--previous-season'); p.add_argument('--previous-history-context')
    p.add_argument('--finance-run'); p.add_argument('--strategy-ref',action='append',default=[],help='Explicit TEAM:REVISION, never latest silently')
    p.add_argument('--supersedes-run')
    p.add_argument('--expected-revision',type=int)
    p.add_argument('--input',type=Path); p.add_argument('--query',type=Path); p.add_argument('--ref')
    p.add_argument('--team'); p.add_argument('--limit',type=int,default=20); p.add_argument('--cursor')
    p.add_argument('--defense-matchup',action='append',default=[],help='prepare: OWNER:OPPONENT, exact team ID or abbreviation; only requested personal matchups are read')
    p.add_argument('--target-kind');p.add_argument('--field-key');p.add_argument('--player-identity')
    p.add_argument('--output',type=Path); p.add_argument('--allow-local-audited',action='store_true')
    return p


def run(a):
    write=a.action in ('prepare','import-analysis','seal','screen-market')
    with Store(a.workbench,readonly=not write) as store:
        if a.action=='prepare':
            if not all((a.career,a.batch,a.season,a.node_type)):
                raise ValueError('PREPARE_REQUIRES_CAREER_BATCH_SEASON_NODE')
            inputs=load_inputs(a.query_root,a.published_root,a.career,a.batch,a.allow_local_audited,a.defense_matchup)
            previous=load_inputs(a.query_root,a.published_root,a.career,a.previous_batch,a.allow_local_audited) if a.previous_batch else None
            if previous:
                previous.update(season=a.previous_season,history_branch_context=a.previous_history_context)
            finance=store.load_run(a.finance_run) if a.finance_run else None
            strategies=[]
            for ref in a.strategy_ref:
                tid,rev=ref.rsplit(':',1)
                strategies.append(store.load_state(a.career,tid,int(rev)))
            commit=subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
            r=packet.prepare(inputs,a.season,a.node_type,previous,finance,strategies,a.run,a.history_context,commit)
            r['code_worktree_dirty']=bool(subprocess.run(['git','-C',str(ROOT),'status','--porcelain','--untracked-files=normal'],capture_output=True,text=True,check=True).stdout.strip())
            if a.supersedes_run:
                old=store.load_analysis(a.supersedes_run)
                if old['source_binding']['career_id']!=a.career:
                    raise ValueError('SUPERSEDES_CAREER_MISMATCH')
                r['supersedes_run_id']=a.supersedes_run
            knowledge=Knowledge(ROOT/'web_gm/knowledge')
            r['reference_evidence']={}
            for card in knowledge.cards:
                ref='knowledge:'+card['card_id']
                r['reference_evidence'][ref]=dict(ref_id=ref,kind='KNOWLEDGE',version=card['version'],
                    value=card,availability='REFERENCE_NOT_CURRENT_GAME_FACT')
            tactical=read_input(ROOT/'config/gm_tactical_knowledge_v1.json')
            for card in tactical['knowledge_cards']:
                ref='tactical-knowledge:'+card['id']
                r['reference_evidence'][ref]=dict(ref_id=ref,kind='KNOWLEDGE',version=tactical['version'],
                    availability='REFERENCE_NOT_ENGINE_CAUSAL_VERIFICATION',value=dict(title=card['title'],
                        basketball_principle=card['basketball_principle'],research_heuristics=card.get('requirements',{}),
                        contraindications=card.get('contraindications',[]),counterplay_and_cost=card.get('counterplay_and_cost'),
                        classification='BASKETBALL_REASONING_AND_HEURISTIC_THRESHOLD',live_3d_effect='UNKNOWN',calendar_sim_effect='UNKNOWN'))
            for state in strategies:
                ref='strategy:'+state['state_id']+':'+str(state['revision'])
                r['reference_evidence'][ref]=dict(ref_id=ref,kind='STRATEGY',value=state,availability='ANALYSIS_ONLY',binding=state['source_binding'])
            if finance:
                ref='finance_run:'+finance['run_id']
                r['reference_evidence'][ref]=dict(ref_id=ref,kind='FINANCE',value=dict(run_id=finance['run_id'],base_season=finance['base_season'],
                    status=finance['status']),binding=finance['source_binding'],availability=r['finance_alignment'])
                r['finance_scenario_refs']=[s['scenario_id'] for s in finance.get('scenarios',[])]
            store.save_analysis(r)
            return packet.summary(r)
        if not a.run:
            raise ValueError('RUN_REQUIRED')
        r=store.load_analysis(a.run)
        packet.require_gm_packet(r)
        if a.career and a.career!=r['source_binding']['career_id']:
            raise ValueError('CAREER_MISMATCH')
        if a.action in ('import-analysis','seal'):
            if a.expected_revision is None:
                raise ValueError('EXPECTED_REVISION_REQUIRED')
            r=packet.annotate(r,read_input(a.input)) if a.action=='import-analysis' else packet.seal(r)
            store.save_analysis(r,a.expected_revision)
            return packet.summary(r)
        meta=dict(run_id=a.run,revision=r['revision'],source_binding=r['source_binding'],authority='ANALYSIS_ONLY',execution_authorized=False)
        if a.action=='show':
            return packet.summary(r)
        if a.action=='players':
            t=packet.team(r,a.team)
            rows=[{k:p[k] for k in ('identity','name','position','salary','years_left','decoded_attributes','season_totals','evidence_ref','unknowns')} for p in t['player_supply']['players']]
            for row,p in zip(rows,t['player_supply']['players']):
                row['potential_visibility']=p.get('potential_visibility')
                row['tactical_context']={k:v for k,v in p.get('tactical_context',{}).items() if k not in ('field_refs','objects')}
            return dict(**meta,**page(rows,[a.run,r['revision'],'players',t['team_id']],a.limit,a.cursor))
        if a.action=='native':
            t=packet.team(r,a.team);rows=[]
            for obj in t.get('tactical_context',{}).get('objects',{}).values():
                if a.target_kind and obj['target_kind']!=a.target_kind:
                    continue
                if a.player_identity:
                    matches=[p for p in t['player_supply']['players'] if p['identity']==a.player_identity]
                    if len(matches)!=1 or obj['selector'].get('player_identity')!=matches[0].get('tactical_context',{}).get('native_player_identity'):
                        continue
                for key,value in obj['fields'].items():
                    if not a.field_key or key==a.field_key:
                        rows.append(dict(**value,evidence_ref='native:'+value['identity'],target_kind=obj['target_kind'],selector=obj['selector']))
            rows.sort(key=lambda row:row['identity'])
            return dict(**meta,**page(rows,[a.run,r['revision'],'native',t['team_id'],a.target_kind,a.field_key,a.player_identity],a.limit,a.cursor))
        if a.action=='team':
            t=packet.team(r,a.team)
            compact={k:v for k,v in t.items() if k not in ('player_supply','coaching_context','tactical_context')}
            compact['player_supply']=dict(source_identity_set=t['player_supply']['source_identity_set'], coverage=t['player_supply']['coverage'])
            compact['coaching_context']=dict(defaults=t['coaching_context']['defaults'],opponent_count=len(t['coaching_context']['overall']))
            compact['tactical_context']=packet.tactical_summary(t)
            return dict(**meta,team=compact)
        if a.action=='evidence':
            return dict(**meta,evidence=packet.evidence(store.analysis_context(a.run),a.ref))
        if a.action=='screen-market':
            query=read_input(a.query); reject_authority(query)
            b=r['source_binding']
            s=QuerySession(a.query_root,a.published_root,b['career_id'],b['batch_id'])
            try:
                s.require_gm_sanitized()
                if not same_source(s.binding,b):
                    raise ValueError('SOURCE_CHANGE_REBASE_REQUIRED')
                profile=read_input(ROOT/'config/memory_field_profile.json')['fields']
                receipt=screen(s,query,[f['name'] for f in profile['PLAYER'] if f.get('group')=='attributes'],
                    [f['name'] for f in profile['STAFF'] if f.get('group')=='attributes'],min(a.limit,5),a.cursor)
            finally:
                s.close()
            requesting=packet.team(r,a.team)['team_id'] if a.team else None
            store.save_market(a.run,receipt,requesting)
            return dict(**meta,receipt=receipt)
        if a.action=='market':
            rows=[c for c in store.market(a.run) if c['candidate_kind']!='SCREEN_QUERY']
            if a.team:
                tid=packet.team(r,a.team)['team_id']; rows=[c for c in rows if c['team_id']==tid]
            rows=[{k:v for k,v in c.items() if k not in ('query_receipt','query')} for c in rows]
            return dict(**meta,**page(rows,[a.run,'market',a.team,len(rows)],min(a.limit,5),a.cursor))
        if not a.output:
            raise ValueError('EXPLICIT_NEW_EXPORT_DIRECTORY_REQUIRED')
        b=r['source_binding']; s=QuerySession(a.query_root,a.published_root,b['career_id'],b['batch_id'])
        try:
            s.require_gm_sanitized()
            if not same_source(s.binding,b):
                raise ValueError('EXPORT_SOURCE_UNAVAILABLE_OR_CHANGED')
        finally:
            s.close()
        return export_files(a.output,{'index.json':packet.summary(r),'access_coverage.json':r['source_access'],
            'methods_and_gaps.json':dict(methods=r['method_registry'],issues=r['issue_index']),
            'team_summaries.json':[dict(team_id=t['team_id'],team=t['team'],annotations=t['annotations']) for t in r['teams']]})


def main():
    try:
        print(json.dumps(run(parser().parse_args()),ensure_ascii=False,allow_nan=False))
        return 0
    except (ValueError,KeyError,TypeError,OSError,sqlite3.Error,AccessError) as exc:
        print(json.dumps(dict(status=getattr(exc,'code','M3_INPUT_OR_STORE_ERROR'),message=str(exc)[:250]),ensure_ascii=False))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
