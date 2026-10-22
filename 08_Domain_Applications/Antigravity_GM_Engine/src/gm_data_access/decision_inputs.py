"""Selected offline coaching sources, never game-memory or executor modules."""
import json
from pathlib import Path
from gm_core.data_reader import attach_coaching_opponents


def prepare_native_artifacts(analysis,decision,selected,query_root,published_root):
    """Use the existing DEV14 offline planner; never stage Desired or open a game handle."""
    from copy import deepcopy
    from gm_core.decision_handoff import NATIVE_KINDS,native_intent
    from gm_state_io.capture_bridge import load_audited_source
    from gm_state_io.plan import build_plan
    from gm_state_io.registry import Registry
    b=analysis['source_binding'];reg=Registry()
    supported=[a for a in selected['actions'] if a['kind'] in NATIVE_KINDS or a['kind']=='COACHING']
    if not supported:
        return []
    source=None;source_error=None
    try:
        source=load_audited_source(b['career_id'],b['batch_id'],query_root,published_root)
        if source['source_snapshot_id']!=b['snapshot_id'] or any(source.get(k)!=b.get(k) for k in ('save_id','save_instance_id','generation_id','registry_version')):
            raise ValueError('M3_DEV14_SOURCE_BINDING_MISMATCH')
        if not all(source.get(k) for k in ('save_instance_id','generation_id')):
            raise ValueError('DEV14_GENERATION_NOT_OBSERVED')
    except (ValueError,OSError) as exc:
        source_error=str(exc)
    pending={i['object_id']:i.get('reason',i['code']) for i in selected['issues'] if i['code'] in
        ('POST_TRADE_NATIVE_REPLAN_REQUIRED','POST_REBIND_SOURCE_REQUIRED','NATIVE_PREPARATION_PENDING')}
    ordinary=[];separate=[];artifacts=[]
    for a in supported:
        if source_error or a['action_id'] in pending:
            artifacts.append(dict(kind='DEV14_SPARSE_INTENT',source_internal_action_ids=[a['action_id']],status='RESEARCH_ONLY',
                reason=source_error or pending[a['action_id']],execution_authorized=False))
            continue
        try:
            intent=native_intent(decision,analysis,a)
        except (ValueError,PermissionError) as exc:
            artifacts.append(dict(kind='DEV14_SPARSE_INTENT',source_internal_action_ids=[a['action_id']],status='BLOCKED_SOURCE',
                reason=str(exc),execution_authorized=False))
            continue
        (separate if intent.get('operation')=='TEAM_BOOK_REBIND' else ordinary).append((a,intent))
    groups=[ordinary] if ordinary else []
    groups.extend([[entry] for entry in separate])
    for entries in groups:
        intent=deepcopy(entries[0][1]);changes={}
        for _,part in entries:
            for change in part['changes']:
                key=(change['object_key'],change['field_key'])
                if key in changes and changes[key]['target_value']!=change['target_value']:
                    raise ValueError('NATIVE_FIELD_CONFLICT')
                changes.setdefault(key,change)
        intent['changes']=list(changes.values())
        intent['reason']='; '.join(a.get('reason',part['reason']) for a,part in entries)
        ids=[a['action_id'] for a,_ in entries]
        try:
            plan=build_plan(intent,source,reg,source)
            artifacts.append(dict(kind='DEV14_SPARSE_INTENT',source_internal_action_ids=ids,status='OFFLINE_PREPARED',
                intent=intent,source_binding=deepcopy(b),registry_version=reg.version,digest=plan['digest'],
                decision_evidence=[{k:a.get(k) for k in ('action_id','kind','evidence_refs','reason','expected_effect','uncertainty','counterplay','why_better_than_hold','role','minutes_target_band')} for a,_ in entries],
                actions_requested=plan['actions_requested'],actions_effective=plan['actions_effective'],unchanged=plan['unchanged'],
                native_blocks_planned=plan['native_blocks_planned'],
                approval_tuple=dict(**{k:plan[k] for k in ('save_id','save_instance_id','generation_id','source_batch_id','decision_id','version')},
                    action_ids=sorted(a['action_id'] for a in plan['actions']),digest=plan['digest']),
                diff=[dict(action_id=a['action_id'],field_key=a['field_key'],object_key=a['object_key'],before=a['expected_observed_raw'],after=a['target_value']) for a in plan['actions']],
                follow_up='NEW_SOURCE_AND_SEPARATE_SLOT_PROPOSAL_AFTER_APPROVED_BINDING' if intent.get('operation')=='TEAM_BOOK_REBIND' else 'MATCHING_ACTIVE_SAVE_STAGE_AND_SEPARATE_PLAYER_APPROVAL',
                approval_status='NOT_GRANTED',execution_authorized=False,planner='gm_state_io.plan.build_plan',mode='OFFLINE_NO_PROCESS_HANDLES'))
        except (ValueError,PermissionError) as exc:
            artifacts.append(dict(kind='DEV14_SPARSE_INTENT',source_internal_action_ids=ids,status='BLOCKED_SOURCE',intent=intent,
                reason=str(exc),approval_status='NOT_GRANTED',execution_authorized=False))
    return artifacts


def coaching_source(published_root,binding,requests):
    directory=Path(published_root)/'saves'/binding['career_id']/'batches'/binding['batch_id']/'coaching'
    snapshot=json.loads((directory/'teams.json').read_text(encoding='utf-8-sig'))
    owners={r['team_id'] for r in requests if r.get('scope')=='VS_OPPONENT_DEFENSE'}
    for owner in sorted(owners):
        team=next(t for t in snapshot['teams'] if t['team_id']==owner)
        # Export contract names the file explicitly; use its team abbreviation only as a fallback.
        path=directory/'opponents'/('team_'+str(owner)+'.json')
        if not path.is_file():
            candidates=[p for p in (directory/'opponents').glob('*.json') if p.stem in (str(owner),team.get('abbreviation'),team.get('team_abbr'),team.get('team'))]
            if len(candidates)!=1:
                raise ValueError('SELECTED_COACH_OWNER_SOURCE_UNAVAILABLE:'+str(owner))
            path=candidates[0]
        attach_coaching_opponents(snapshot,json.loads(path.read_text(encoding='utf-8-sig')))
    return snapshot
