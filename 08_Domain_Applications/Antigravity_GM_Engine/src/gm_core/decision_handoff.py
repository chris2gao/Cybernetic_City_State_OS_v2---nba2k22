"""Pure offline business handoffs. No executor imports or process access."""
from copy import deepcopy
from .coaching_batch import propose_batch, validate_batch, normalize_freelance
from coach_codec import load_profile
from .finance_scenarios import compare
from .analysis_packet import team, validate_refs
from .workbench_common import require, text_required

NATIVE_KINDS={
    'COACH_DEFAULT':('COACH_DEFAULT','coach.'),
    'PERSONAL_DEFENSE':('PERSONAL_DEFENSE','personal.'),
    'PLAYER_PLAY_TYPE':('PLAYER_PLAYTYPE','playtype.'),
    'PLAYER_TENDENCY':('PLAYER_TENDENCY','tendency.'),
    'TEAM_EXCLUSIVE_PLAYBOOK_CONTENT':('PLAYBOOK_SLOT','playbook.slot'),
    'TRAINING_PLAN':(None,'training.'),
    'LINEUP_ROLE':('PLAYER_ROTATION_OVR_BIAS','rotation.intangibles'),
    'TEAM_BOOK_REBIND':('COACH_DEFAULT','coach.PlaybookID')}


def coach_change_gate(run,tid):
    if run.get('season_phase')!='OFFSEASON':
        return 'COACH_CHANGE_OFFSEASON_ONLY'
    if any(e['kind']=='CONFIRMED_COACH_CHANGE' and e['team_id']==tid for e in run.get('coach_events',[])):
        return 'COACH_CHANGE_ONCE_PER_TEAM_SEASON'
    return 'BUSINESS_PROPOSAL_ONLY_NO_STAFF_EXECUTOR'


def native_intent(run,analysis,action):
    """Business contract only. DEV14 independently expands/encodes actual source bytes."""
    tid=action['team_id'];t=team(analysis,tid);tc=t.get('tactical_context',{})
    kind=action['kind'];changes=deepcopy(action.get('changes',[]));event=None
    if kind=='COACHING':
        changes=[];kind='COACH_DEFAULT'
        for r in action['requests']:
            if r.get('scope','COACH_DEFAULT')!='COACH_DEFAULT':
                raise PermissionError('OVERALL_DEFENSE_GM_DISABLED_USE_PERSONAL')
            if r['team_id']!=tid:
                raise ValueError('INTERNAL_ACTION_CANNOT_CONTROL_ANOTHER_TEAM')
            for field,value in normalize_freelance(r['targets'],load_profile()).items():
                if field=='PlaybookID':
                    raise PermissionError('ORDINARY_GM_BOOK_SWITCH_DISABLED_USE_TEAM_BOOK_REBIND')
                changes.append(dict(action_id=r['action_id']+':'+field,object_key=tc.get('coach_object_key'),
                    field_key='coach.'+field,target_value=value,reason=r['expected_effect']))
    if kind not in NATIVE_KINDS:
        raise ValueError('NOT_A_NATIVE_M3_ACTION')
    if kind=='TEAM_BOOK_REBIND':
        events=[e for e in run.get('coach_events',[]) if e['event_id']==action.get('event_id') and e['team_id']==tid]
        if len(events)!=1:
            raise ValueError('SEPARATELY_CONFIRMED_COACH_EVENT_REQUIRED')
        event={k:events[0][k] for k in ('kind','reference','team_id','current_coach_identity')}
        if events[0]['source_binding']!=run['source_binding']:
            raise ValueError('BOOK_REBIND_EVENT_REQUIRES_CURRENT_POST_CHANGE_SOURCE')
        own=tc.get('playbook',{}).get('identity')
        if not own or not tc.get('coach_object_key'):
            raise ValueError('TEAM_NAMED_BOOK_SOURCE_UNAVAILABLE')
        changes=[dict(action_id=action['action_id'],object_key=tc['coach_object_key'],field_key='coach.PlaybookID',
            target_value=own['enum_id'],reason=action['reason'])]
    if not changes:
        raise ValueError('NONEMPTY_SPARSE_NATIVE_CHANGES_REQUIRED')
    known=analysis.get('native_field_catalog',{})
    expected_kind,prefix=NATIVE_KINDS[kind]
    for c in changes:
        if set(c)!={'action_id','object_key','field_key','target_value','reason'}:
            raise ValueError('EXACT_DEV14_CHANGE_FIELDS_REQUIRED')
        text_required(c['reason'],'native_change_reason')
        key=c['field_key']
        if key.startswith('overall.'):
            raise PermissionError('OVERALL_DEFENSE_GM_DISABLED_USE_PERSONAL')
        if key=='coach.PlaybookID' and kind!='TEAM_BOOK_REBIND':
            raise PermissionError('ORDINARY_GM_BOOK_SWITCH_DISABLED_USE_TEAM_BOOK_REBIND')
        f=known.get(key)
        if not f or not key.startswith(prefix) or (not f['gm_enabled'] and kind!='TEAM_BOOK_REBIND'):
            raise PermissionError('M3_ACTION_FIELD_NOT_AUTHORIZED:'+key)
        o=tc.get('objects',{}).get(c['object_key'])
        if o is None:
            raise ValueError('PERSONAL_MATCHUP_UNAVAILABLE' if kind=='PERSONAL_DEFENSE' else 'NATIVE_OBJECT_NOT_OBSERVED')
        if o['team_id']!=tid or key not in o['field_keys'] or o['source_status']!='OBSERVED_SAME_SESSION':
            raise ValueError('M3_NATIVE_OBJECT_SOURCE_OR_TEAM_MISMATCH')
        if expected_kind and o['target_kind']!=expected_kind:
            raise ValueError('M3_NATIVE_ACTION_KIND_MISMATCH')
        if kind=='TRAINING_PLAN' and o['target_kind'] not in ('TEAM_TRAINING','PLAYER_TRAINING'):
            raise ValueError('M3_TRAINING_OBJECT_REQUIRED')
        if o['target_kind'].startswith('PLAYER_'):
            tag=o['selector']['player_identity']
            matches=[p for p in t['player_supply']['players'] if p.get('tactical_context',{}).get('native_player_identity')==tag]
            if len(matches)!=1:
                raise ValueError('NATIVE_PLAYER_NOT_UNIQUE_IN_CURRENT_ROSTER')
        if kind=='LINEUP_ROLE':
            require(action,('role','minutes_target_band'))
            if action['role'] not in ('STARTER','SIXTH_MAN','ROTATION','DEVELOPMENT','HOLD'):
                raise ValueError('ROTATION_ROLE_REQUIRED')
            band=action['minutes_target_band']
            if band is not None and (not isinstance(band,list) or len(band)!=2 or any(type(v) not in (int,float) or v<0 for v in band) or band[0]>band[1]):
                raise ValueError('ORDERED_NONNEGATIVE_TARGET_BAND_REQUIRED_NOT_MINUTE_LOCK')
    intent=dict(decision_id=run['decision_run_id'],version=run['revision'],reason=action.get('reason',action.get('expected_effect','GM internal alternative')),
        changes=changes)
    if event:
        intent.update(operation='TEAM_BOOK_REBIND',event=event)
    return intent


def validate_tactical_action(run,analysis,action):
    kind=action['kind']
    if kind in ('OVERALL_DEFENSE','VS_OPPONENT_DEFENSE'):
        raise PermissionError('OVERALL_DEFENSE_GM_DISABLED_USE_PERSONAL')
    if kind=='COACHING':
        for r in action['requests']:
            if r.get('scope','COACH_DEFAULT')!='COACH_DEFAULT':
                raise PermissionError('OVERALL_DEFENSE_GM_DISABLED_USE_PERSONAL')
            if 'PlaybookID' in r['targets']:
                raise PermissionError('ORDINARY_GM_BOOK_SWITCH_DISABLED_USE_TEAM_BOOK_REBIND')
    if kind=='COACH_CHANGE':
        gate=coach_change_gate(run,action['team_id'])
        if gate!='BUSINESS_PROPOSAL_ONLY_NO_STAFF_EXECUTOR':
            raise ValueError(gate)
        return
    if kind not in NATIVE_KINDS and kind!='COACHING':
        return
    if analysis.get('tactical_version'):
        require(action,('reason','evidence_refs','expected_effect','uncertainty','counterplay','why_better_than_hold'))
        validate_refs(analysis,action['evidence_refs'])
        for k in ('reason','expected_effect','uncertainty','counterplay','why_better_than_hold'):
            text_required(action[k],k)
        # Missing observations remain scoped research; explicit wrong/forbidden fields are errors.
        try:
            native_intent(run,analysis,action)
        except ValueError as exc:
            if str(exc) not in ('PERSONAL_MATCHUP_UNAVAILABLE','NATIVE_OBJECT_NOT_OBSERVED','TEAM_NAMED_BOOK_SOURCE_UNAVAILABLE'):
                raise


def generate(decision, selected, analysis, finance=None, coach_snapshot=None, native_artifacts=None):
    items, research, generated = [], [], []
    research.extend(dict(item_id=r['research_id'],kind='RESEARCH_ALTERNATIVE',team_id=r['team_id'],
        alternative_revision=r['alternative_revision'],alternative=r['alternative'],executor_readiness='RESEARCH_ONLY',
        approval_status='NOT_GRANTED',execution_authorized=False) for r in selected.get('research',[]))
    moves=[]
    issues=selected['issues']
    bad_offers={i.get('object_id') for i in issues if i['code']=='DEPENDENCY_UNSUPPORTED'}
    overlapping={i['team_id'] for i in issues if i['code']=='DEPENDENCY_UNSUPPORTED_SAME_TEAM_TRADES'}
    for offer in selected['offers']:
        blocked=offer['offer_id'] in bad_offers or bool(set(offer['team_ids'])&overlapping)
        item=dict(item_id=offer['offer_id'],kind='SPECIFIC_TRADE_INTENT',source_binding=deepcopy(decision['source_binding']),
            terms=deepcopy(offer),analysis_status='BILATERAL_REVIEWED',rule_check='CURRENT_SIMPLE_ASSETS_CHECKED',
            financial_evidence='COST_COMPARISON_ONLY_SIGNING_CAPACITY_UNKNOWN',
            executor_readiness='DEPENDENCY_UNSUPPORTED' if blocked else 'REQUIRES_LIVE_TRADE_PLAN',
            approval_status='NOT_GRANTED',execution_authorized=False,
            next_step='Player approval, then separate live identity/regular-capacity/five-man-reference plan')
        (research if blocked else items).append(item)
        moves.extend(dict(type=m['kind'],identity=m.get('source_identity'),asset_id=m.get('asset_id'),
            from_team_id=m['from_team_id'],to_team_id=m['to_team_id']) for m in offer['moves'])
    requests=[]
    pending={i.get('object_id') for i in issues if i['code']=='POST_TRADE_COACHING_REPLAN_REQUIRED'}
    if analysis.get('tactical_version'):
        for artifact in native_artifacts or []:
            generated.append(deepcopy(artifact))
            item=dict(item_id='DEV14:'+','.join(artifact['source_internal_action_ids']),kind='DEV14_SPARSE_INTENT',
                source_internal_action_ids=artifact['source_internal_action_ids'],source_binding=deepcopy(decision['source_binding']),
                analysis_status='EVIDENCE_REVIEWED',rule_check='DEV14_OFFLINE_PLANNER' if artifact['status']=='OFFLINE_PREPARED' else 'BLOCKED_AFFECTED_ACTION',
                financial_evidence='NO_CONTRACT_CHANGE',approval_status='NOT_GRANTED',execution_authorized=False,
                executor_readiness='OFFLINE_PREPARED_REQUIRES_ACTIVE_STAGE_AND_PLAYER_APPROVAL' if artifact['status']=='OFFLINE_PREPARED' else artifact['status'])
            if artifact['status']=='OFFLINE_PREPARED':
                item.update(digest=artifact['digest'],action_ids=artifact['approval_tuple']['action_ids'],approval_tuple=artifact['approval_tuple'])
                items.append(item)
            else:
                item['reason']=artifact.get('reason');research.append(item)
    for action in selected['actions']:
        if analysis.get('tactical_version') and (action['kind'] in NATIVE_KINDS or action['kind']=='COACHING'):
            if native_artifacts is None:
                research.append(dict(item_id=action['action_id'],kind=action['kind'],executor_readiness='DEV14_OFFLINE_PREPARATION_PENDING',execution_authorized=False))
            continue
        if action['kind']!='COACHING' or action['action_id'] in pending:
            research.append(dict(item_id=action['action_id'],kind=action['kind'],action=deepcopy(action),
                executor_readiness='POST_TRADE_COACHING_REPLAN_REQUIRED' if action['action_id'] in pending else 'BLOCKED_EXECUTOR',
                approval_status='NOT_GRANTED',execution_authorized=False))
            continue
        requests.extend(deepcopy(action['requests']))
    if requests:
        if coach_snapshot is None:
            research.append(dict(kind='COACHING',executor_readiness='EXECUTION_PREPARATION_PENDING',requests=requests))
        else:
            b=decision['source_binding']
            if any(coach_snapshot.get(k)!=b.get(v) for k,v in [('career_id','career_id'),('source_batch_id','batch_id'),('game_date','game_date'),('data_updated_at','data_updated_at')]):
                raise ValueError('OFFLINE_COACHING_SOURCE_MISMATCH')
            # Merge identical field targets while keeping their original reasoning in portfolio.
            merged={}
            for r in requests:
                key=(r['team_id'],r.get('opponent_team_id'))
                r['targets']=normalize_freelance(r['targets'],load_profile())
                if key in merged:
                    for f,v in r['targets'].items():
                        if f in merged[key]['targets'] and merged[key]['targets'][f]!=v:
                            raise ValueError('COACH_FIELD_CONFLICT')
                    merged[key]['targets'].update(r['targets'])
                else:
                    merged[key]=r
            batch=propose_batch(coach_snapshot,list(merged.values()),decision['decision_run_id']+'_coach',decision['decision_run_id'],decision['revision'])
            dry=validate_batch(batch,coach_snapshot)
            generated.append(dict(kind='COACHING_OFFLINE_ARTIFACT',batch=batch,dry_run=dry,
                gm_verdict=dict(valid=dry['valid'],executable_after_separate_player_approval=dry['executable'],
                    blocked_action_ids=dry['blocked_action_ids'],mode='OFFLINE_NO_PROCESS_HANDLES'),
                action_ids=[a['action_id'] for a in batch['actions']],batch_digest=dry['batch_digest']))
            if dry['executable']:
                items.append(dict(item_id=batch['batch_id'],kind='COACHING_BATCH',action_ids=generated[-1]['action_ids'],
                    source_internal_action_ids=[a['action_id'] for a in selected['actions'] if a['kind']=='COACHING' and a['action_id'] not in pending and a.get('requests')],
                    batch_digest=dry['batch_digest'],source_binding=deepcopy(b),executor_readiness='OFFLINE_PREPARED_REQUIRES_PLAYER_APPROVAL',
                    analysis_status='REVIEWED',rule_check='PURE_CODEC_VALIDATED',financial_evidence='NO_CONTRACT_CHANGE',
                    approval_status='NOT_GRANTED',execution_authorized=False))
            else:
                research.append(dict(kind='COACHING',executor_readiness='BLOCKED_CODEC_OR_READINESS',artifact_ref=batch['batch_id']))
    finance_result=None
    if moves and finance and analysis['finance_alignment']=='SAME_BATCH':
        finance_result=compare(finance,dict(scenario_id=decision['decision_run_id']+'_portfolio_r'+str(decision['revision']),kind='TRADE_OR_SIGNING',moves=moves))
    return dict(specific_approval_items=items,research_items=research,generated_artifact_refs=generated,
        finance_evidence=finance_result or dict(status='NOT_LINKED_OR_STALE',signing_capacity=None),execution_authorized=False)
