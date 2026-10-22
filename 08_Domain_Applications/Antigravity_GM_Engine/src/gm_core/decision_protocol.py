"""Candidate five-phase GM research protocol. V3 stays active; nothing executes."""
from copy import deepcopy
from uuid import uuid4
from . import market_negotiation as negotiation
from . import decision_portfolio as portfolio
from . import decision_handoff as handoff
from . import bpti_decision, bpti_evolution
from .analysis_packet import team, validate_refs, require_gm_packet
from .workbench_common import now, reject_authority, require, text_required
from .strategy_state import validate as validate_strategy, LIST_FIELDS

PROTOCOL='GM_V4_SINGLE_TRIGGER_INTERNAL_FIVE_PHASES'
DIMENSIONS=('D1_STAFF','D2_TACTICS','D3_ROSTER_USE','D4_MARKET','D5_ASSETS_AND_DEVELOPMENT','D6_TEAM_IDENTITY_AND_MONITORING')
INTEREST=('objective_and_window','evidence_refs','role_priorities','retain_thresholds','sell_conditions',
          'pick_commitment_conditions','contract_risk_conditions','best_internal_alternative_id','reversal_conditions')
HYPOTHESIS=('baseline_refs','mechanism_claim','alternative_explanations','expected_direction','observation_metrics',
            'minimum_evidence_description','falsification_conditions','confounds')


def begin(analysis, run_id=None, strategy_bases=(), constraints=None, season_phase='UNKNOWN'):
    require_gm_packet(analysis)
    if season_phase not in ('UNKNOWN','REGULAR','PLAYOFFS','OFFSEASON'):
        raise ValueError('EXPLICIT_SEASON_PHASE_OR_UNKNOWN_REQUIRED')
    if not analysis['sealed_at']:
        raise ValueError('SEALED_ANALYSIS_REQUIRED')
    if constraints:
        reject_authority(constraints)
        require(constraints,('source_binding','protected_identities','context_evidence'))
        if constraints['source_binding']!=analysis['source_binding']:
            raise ValueError('PLAYER_CONSTRAINT_SOURCE_MISMATCH')
        text_required(constraints['context_evidence'],'player_constraint_evidence')
        players={p['identity'] for t in analysis['teams'] for p in t['player_supply']['players']}
        if not isinstance(constraints['protected_identities'],list) or not set(constraints['protected_identities'])<=players:
            raise ValueError('PLAYER_CONSTRAINT_IDENTITIES_MUST_BE_CURRENT')
    return dict(decision_run_id=run_id or uuid4().hex,revision=1,created_at=now(),
        mode='DEVELOPMENT_CANDIDATE',protocol_id=PROTOCOL,protocol_status='DRAFT_NOT_ENABLED',
        source_binding=deepcopy(analysis['source_binding']),analysis_run_id=analysis['analysis_run_id'],
        analysis_revision=analysis['revision'],expected_team_ids=analysis['expected_team_ids'],
        context=deepcopy(analysis['context']),calculation_version=analysis['calculation_version'],knowledge_version=analysis['knowledge_version'],
        finance_run_id=analysis['finance_run_id'],finance_alignment=analysis['finance_alignment'],
        protected_identities=constraints['protected_identities'] if constraints else [],constraints_context=deepcopy(constraints),
        strategy_bases=deepcopy(list(strategy_bases)),season_phase=season_phase,coach_events=[],phase='P1',status='OPEN',phase_progress={},
        current_final_version=None,latest_final_version=0,approval_status='NOT_GRANTED',execution_authorized=False,artifacts={})


def get(run, kind, aid):
    row=run['artifacts'].get(kind,{}).get(str(aid))
    if not row:
        raise ValueError('ARTIFACT_REQUIRED:'+kind+':'+str(aid))
    return row


def templates(analysis, key):
    """Actual source identities, deliberately empty judgments; never submittable as complete."""
    t=team(analysis,key);tid=t['team_id'];ref='team:'+str(tid)
    hypothesis={k:[] if k in ('baseline_refs','alternative_explanations','observation_metrics','falsification_conditions','confounds') else '' for k in HYPOTHESIS}
    hypothesis['baseline_refs']=[ref]
    r=dict(team_id=tid,player_assessments=[dict(source_identity=p['identity'],role_assessment='',retain_or_research_position='',
        key_evidence_refs=[p['evidence_ref']],unknowns=[],review_depth='NORMAL') for p in t['player_supply']['players']],
        decision_dimensions={k:dict(conclusion='',evidence_refs=[ref],unknowns=[],alternatives=[]) for k in DIMENSIONS},
        competitive_window=dict(assessment='',evidence_refs=[ref],alternatives=[]),
        team_interest_profile={k:[] for k in INTEREST},evidence_refs=[ref],uncertainties=[],monitoring_hypothesis=hypothesis)
    r['team_interest_profile'].update(objective_and_window='',evidence_refs=[ref],best_internal_alternative_id='internal:'+str(tid))
    if analysis.get('tactical_version'):
        r.update(internal_tactical_diagnosis_refs=['tactical:'+str(tid)],rejected_internal_fixes=[],
            market_gap_after_internal_assessment=dict(status='UNKNOWN',reason='',evidence_refs=[ref]),
            evidence_quality=dict(native_fields='GAME_NATIVE_FIELD_VERIFIED_OR_NOT_OBSERVED',behavior='UNKNOWN'),play_type_coverage='UNKNOWN')
        for p in r['player_assessments']:
            p['role_plan']=dict(role='HOLD',minutes_target_band=None,reason='')
    alts=[]
    for category in ('HOLD','INTERNAL','MARKET'):
        alts.append(dict(alternative_id=category.lower()+':'+str(tid),category=category,status='RESEARCH',problem='',proposed_means='',
            evidence_refs=[ref],benefit_hypotheses=[],costs_and_opportunity_costs='',reversibility='',counterevidence=[],change_conditions=[],selection_reason=''))
    return dict(status='EMPTY_TEMPLATES_NOT_ASSESSED',source_binding=analysis['source_binding'],review_template=r,
        alternatives_template=dict(team_id=tid,alternatives=alts),next_step='Fill explicit judgments and reasoned gaps, then submit each object separately')


def progress(run):
    expected=set(run['expected_team_ids'])
    reviews={int(k) for k in run['artifacts'].get('TEAM_REVIEW',{})}
    alternatives={int(k) for k in run['artifacts'].get('ALTERNATIVES',{})}
    alternatives={tid for tid in alternatives if tid in reviews and
        run['artifacts']['ALTERNATIVES'][str(tid)]['payload']['team_interest_revision']==run['artifacts']['TEAM_REVIEW'][str(tid)]['revision']}
    completed=expected&reviews&alternatives
    return dict(expected_team_ids=sorted(expected),reviewed_team_ids=sorted(reviews),alternatives_team_ids=sorted(alternatives),
        completed_team_ids=sorted(completed),pending_review_team_ids=sorted(expected-reviews),pending_alternatives_team_ids=sorted(expected-alternatives),
        all_teams_ready=len(expected)==30 and completed==expected)


def validate_hypothesis(analysis,h):
    require(h,HYPOTHESIS)
    validate_refs(analysis,h['baseline_refs'])
    for key in HYPOTHESIS[1:]:
        if not isinstance(h[key],(str,list,dict)) or not h[key]:
            raise ValueError('HYPOTHESIS_REASON_OR_GAP_REQUIRED:'+key)


def review(payload, analysis):
    require(payload,('team_id','player_assessments','decision_dimensions','competitive_window','team_interest_profile',
                     'evidence_refs','uncertainties','monitoring_hypothesis'))
    t=team(analysis,payload['team_id'])
    expected=t['player_supply']['source_identity_set']
    players=payload['player_assessments']
    if not isinstance(players,list) or sorted(p['source_identity'] for p in players)!=expected:
        raise ValueError('EXACT_ROSTER_IDENTITY_SET_REQUIRED')
    for p in players:
        require(p,('source_identity','role_assessment','retain_or_research_position','key_evidence_refs','unknowns','review_depth'))
        text_required(p['role_assessment'],'role_assessment'); text_required(p['retain_or_research_position'],'retain_or_research_position')
        if p['review_depth'] not in ('NORMAL','FOCAL') or 'player:'+p['source_identity'] not in p['key_evidence_refs']:
            raise ValueError('PLAYER_OWN_EVIDENCE_AND_REVIEW_DEPTH_REQUIRED')
        validate_refs(analysis,p['key_evidence_refs'])
        if analysis.get('tactical_version'):
            require(p,('role_plan',));plan=p['role_plan'];require(plan,('role','minutes_target_band','reason'))
            if plan['role'] not in ('STARTER','SIXTH_MAN','ROTATION','DEVELOPMENT','HOLD'):
                raise ValueError('PLAYER_ROLE_PLAN_REQUIRED')
            text_required(plan['reason'],'role_plan_reason')
            band=plan['minutes_target_band']
            if band is not None and (not isinstance(band,list) or len(band)!=2 or any(type(v) not in (int,float) or v<0 for v in band) or band[0]>band[1]):
                raise ValueError('TARGET_MINUTES_BAND_IS_NOT_A_NATIVE_LOCK')
    require(payload['decision_dimensions'],DIMENSIONS)
    for key in DIMENSIONS:
        dim=payload['decision_dimensions'][key]
        require(dim,('conclusion','evidence_refs','unknowns','alternatives'))
        text_required(dim['conclusion'],key); validate_refs(analysis,dim['evidence_refs'])
    require(payload['competitive_window'],('assessment','evidence_refs','alternatives'))
    text_required(payload['competitive_window']['assessment'],'competitive_window')
    validate_refs(analysis,payload['competitive_window']['evidence_refs'])
    interest=payload['team_interest_profile']; require(interest,INTEREST)
    for k in INTEREST:
        if not isinstance(interest[k],(str,list,dict)) or not interest[k]:
            raise ValueError('TEAM_INTEREST_VALUE_OR_REASON_REQUIRED:'+k)
    validate_refs(analysis,interest['evidence_refs']); validate_refs(analysis,payload['evidence_refs'])
    validate_hypothesis(analysis,payload['monitoring_hypothesis'])
    if analysis.get('tactical_version'):
        require(payload,('internal_tactical_diagnosis_refs','rejected_internal_fixes','market_gap_after_internal_assessment','evidence_quality','play_type_coverage'))
        validate_refs(analysis,payload['internal_tactical_diagnosis_refs'])
        if payload['play_type_coverage']!='UNKNOWN':
            raise ValueError('CRC_ONLY_PLAY_TYPE_COVERAGE_MUST_REMAIN_UNKNOWN')
        gap=payload['market_gap_after_internal_assessment']
        require(gap,('status','reason','evidence_refs'))
        if gap['status'] not in ('NO_GAP','GAP_REMAINS','UNKNOWN'):
            raise ValueError('INTERNAL_ASSESSMENT_REQUIRED_BEFORE_MARKET')
        text_required(gap['reason'],'market_gap_reason');validate_refs(analysis,gap['evidence_refs'])
        for fix in payload['rejected_internal_fixes']:
            require(fix,('reason','evidence_refs'));text_required(fix['reason'],'internal_fix_rejection');validate_refs(analysis,fix['evidence_refs'])
        require(payload['evidence_quality'],('native_fields','behavior'))
        if payload['evidence_quality']['behavior'] not in ('BASKETBALL_REASONING','RESEARCH_HYPOTHESIS','HEURISTIC_THRESHOLD','UNKNOWN'):
            raise ValueError('TACTICAL_EFFECT_NOT_ENGINE_VERIFIED')
    return deepcopy(payload)


def alternatives(payload, run, analysis):
    require(payload,('team_id','alternatives'))
    review_row=get(run,'TEAM_REVIEW',payload['team_id'])
    alts=payload['alternatives']
    if not isinstance(alts,list) or {a['category'] for a in alts}!={'HOLD','INTERNAL','MARKET'} or len({a['alternative_id'] for a in alts})!=len(alts):
        raise ValueError('THREE_SUBSTANTIVE_ALTERNATIVE_CATEGORIES_REQUIRED')
    for a in alts:
        require(a,('alternative_id','category','status','problem','proposed_means','evidence_refs','benefit_hypotheses',
            'costs_and_opportunity_costs','reversibility','counterevidence','change_conditions','selection_reason'))
        if a['status'] not in ('VIABLE_CANDIDATE','RESEARCH','BLOCKED','NOT_APPLICABLE'):
            raise ValueError('INVALID_ALTERNATIVE_STATUS')
        for k in ('problem','proposed_means','costs_and_opportunity_costs','reversibility','selection_reason'):
            text_required(a[k],k)
        validate_refs(analysis,a['evidence_refs'])
        if a.get('finance_scenario_ref') and a['finance_scenario_ref'] not in analysis.get('finance_scenario_refs',[]):
            raise ValueError('FINANCE_SCENARIO_MUST_RESOLVE_TO_LINKED_RUN')
        for k in ('benefit_hypotheses','counterevidence','change_conditions'):
            if not a[k]:
                raise ValueError('ALTERNATIVE_REASON_OR_GAP_REQUIRED:'+k)
        if a.get('action'):
            require(a['action'],('action_id','kind'))
            if a['action']['kind']=='COACHING':
                require(a['action'],('requests',))
                if not isinstance(a['action']['requests'],list) or not a['action']['requests']:
                    raise ValueError('NONEMPTY_COACH_REQUESTS_REQUIRED')
                for req in a['action']['requests']:
                    require(req,('action_id','team_id','targets','expected_effect'))
                    if req['team_id']!=payload['team_id'] or not req['targets']:
                        raise ValueError('OWN_TEAM_SPECIFIC_COACH_TARGETS_REQUIRED')
            action=dict(a['action'],team_id=payload['team_id'])
            handoff.validate_tactical_action(run,analysis,action)
        if analysis.get('tactical_version') and a['category']=='MARKET' and a['status']=='VIABLE_CANDIDATE':
            r=review_row['payload']
            if r['market_gap_after_internal_assessment']['status']!='GAP_REMAINS' or not r['rejected_internal_fixes']:
                raise ValueError('MARKET_REQUIRES_EVIDENCED_GAP_AFTER_INTERNAL_COMPARISON')
    internal={a['alternative_id'] for a in alts if a['category']=='INTERNAL'}
    if review_row['payload']['team_interest_profile']['best_internal_alternative_id'] not in internal:
        raise ValueError('BEST_INTERNAL_ALTERNATIVE_MUST_RESOLVE')
    return dict(**deepcopy(payload),team_interest_revision=review_row['revision'])


def apply(run, analysis, command, payload, *, bpti_index=None, previous_evolution=None):
    reject_authority({k:v for k,v in payload.items() if not (command=='respond-offer' and k=='terms_digest')})
    if analysis['source_binding']!=run['source_binding'] or analysis['revision']!=run['analysis_revision']:
        raise ValueError('SOURCE_CHANGE_REBASE_REQUIRED')
    run=deepcopy(run)
    artifacts=[]
    if command=='submit-blueprint':
        if bpti_index is None:
            raise ValueError('BPTI_KNOWLEDGE_INDEX_REQUIRED')
        obj=bpti_decision.prepare(run,analysis,bpti_index,payload); kind,aid='BPTI_BLUEPRINT',str(payload['team_id'])
    elif command=='record-evolution':
        row=get(run,'BPTI_BLUEPRINT',payload['team_id'])
        obj=bpti_evolution.record(run,analysis,row,payload,previous_evolution); kind,aid='BPTI_EVOLUTION',str(payload['team_id'])
    elif command=='record-coach-event':
        obj=coach_event(run,analysis,payload);kind,aid='COACH_EVENT',payload['event_id']
    elif command=='submit-review':
        row=run['artifacts'].get('BPTI_BLUEPRINT',{}).get(str(payload['team_id']))
        if row:
            payload=bpti_decision.attach_review(payload,row)
        obj=review(payload,analysis); kind,aid='TEAM_REVIEW',str(payload['team_id'])
    elif command=='submit-alternatives':
        row=run['artifacts'].get('BPTI_BLUEPRINT',{}).get(str(payload['team_id']))
        if row:
            payload=bpti_decision.attach_alternatives(payload,row,get(run,'TEAM_REVIEW',payload['team_id']))
        obj=alternatives(payload,run,analysis); kind,aid='ALTERNATIVES',str(payload['team_id'])
    else:
        if not progress(run)['all_teams_ready']:
            raise ValueError('P1_P2_ALL_30_REQUIRED_FOR_MARKET_SELECTION')
        if command=='submit-offer':
            if analysis.get('tactical_version'):
                for tid in payload['team_ids']:
                    options=get(run,'ALTERNATIVES',tid)['payload']['alternatives']
                    if not any(a['category']=='MARKET' and a['status']=='VIABLE_CANDIDATE' for a in options):
                        raise ValueError('BOTH_PARTIES_NEED_INTERNAL_COMPARISON_BEFORE_TRADE')
            previous=run['artifacts'].get('OFFER',{}).get(payload['offer_id'])
            obj=negotiation.offer(payload,run,analysis,(previous['payload']['terms_revision'] if previous else 0)+1)
            kind,aid='OFFER',payload['offer_id']
        elif command=='respond-offer':
            o=get(run,'OFFER',payload['offer_id'])['payload']
            obj=negotiation.response(payload,o,run,analysis,run['artifacts']['TEAM_REVIEW'],run['artifacts']['ALTERNATIVES'])
            kind,aid='RESPONSE',payload['offer_id']+':'+str(payload['responding_team_id'])
        elif command=='select':
            portfolio.resolve(payload,run['artifacts'],analysis)
            obj=deepcopy(payload); kind,aid='PORTFOLIO','selected'
            run['phase']='P4'
        else:
            raise ValueError('UNKNOWN_DECISION_COMMAND')
    artifacts.append((kind,aid,obj))
    # Any change invalidates the current validation/final pointer; old artifacts remain readable.
    run['current_final_version']=None
    run['status']='OPEN' if progress(run)['all_teams_ready'] else 'PARTIAL'
    run['validation_revision']=None
    return run,artifacts


def validate(run, analysis, finance=None, coach_snapshot=None, native_artifacts=None):
    run=deepcopy(run)
    if analysis['source_binding']!=run['source_binding'] or analysis['revision']!=run['analysis_revision']:
        raise ValueError('SOURCE_CHANGE_REBASE_REQUIRED')
    p=get(run,'PORTFOLIO','selected')
    selected=portfolio.inspect(p['payload'],run['artifacts'],analysis,run)
    prog=progress(run)
    issues=selected['issues']
    # Changed P1 interests require refreshed P2 and any bilateral acceptances.
    for tid in run['expected_team_ids']:
        r=run['artifacts'].get('TEAM_REVIEW',{}).get(str(tid))
        a=run['artifacts'].get('ALTERNATIVES',{}).get(str(tid))
        if not r or not a or a['payload']['team_interest_revision']!=r['revision']:
            issues.append(dict(code='TEAM_RESEARCH_STALE_OR_INCOMPLETE',team_id=tid,effect='BLOCK_FINAL'))
        b=run['artifacts'].get('BPTI_BLUEPRINT',{}).get(str(tid))
        if b and any(not x or x['payload'].get('bpti_blueprint_revision')!=b['revision'] for x in (r,a)):
            issues.append(dict(code='BPTI_BLUEPRINT_REVIEW_STALE',team_id=tid,effect='BLOCK_FINAL'))
        try:
            bpti_evolution.current(run,tid)
        except ValueError as exc:
            issues.append(dict(code='BPTI_EVOLUTION_STALE',team_id=tid,reason=str(exc),effect='BLOCK_FINAL'))
    valid=prog['all_teams_ready'] and not any(i['effect']=='BLOCK_FINAL' for i in issues)
    generated=handoff.generate(run,selected,analysis,finance,coach_snapshot,native_artifacts) if valid else dict(specific_approval_items=[],research_items=[],generated_artifact_refs=[],finance_evidence={'status':'NOT_EVALUATED'})
    report=dict(report_id=uuid4().hex,decision_run_revision=run['revision']+1,portfolio_revision=p['revision'],
        source_check='MATCHED_SEALED_ANALYSIS',roster_coverage=prog,bilateral_checks=selected['bilateral_checks'],
        issues=issues,valid_for_finalization=valid,approval_status='NOT_GRANTED',**generated)
    report['execution_authorized']=False
    run['phase']='P5' if valid else 'P4'; run['status']='VALIDATED' if valid else 'PARTIAL'
    run['validation_revision']=run['revision']+1; run['current_final_version']=None
    return run,[('VALIDATION','current',report)]


def coach_event(run,analysis,payload):
    require(payload,('event_id','kind','reference','team_id','current_coach_identity'))
    if set(payload)!={'event_id','kind','reference','team_id','current_coach_identity'}:
        raise ValueError('EXACT_CONFIRMED_COACH_EVENT_FIELDS_REQUIRED')
    text_required(payload['event_id'],'event_id');text_required(payload['reference'],'actual_player_confirmation_reference')
    if payload['kind']=='CONFIRMED_COACH_CHANGE':
        gate=handoff.coach_change_gate(run,payload['team_id'])
        if gate!='BUSINESS_PROPOSAL_ONLY_NO_STAFF_EXECUTOR':
            raise ValueError(gate)
    elif payload['kind']=='INITIAL_SAVE':
        if run['context']['node_type'] not in ('BOOTSTRAP','SEASON_INITIALIZATION'):
            raise ValueError('INITIAL_SAVE_BINDING_REQUIRES_INITIALIZATION_NODE')
    else:
        raise ValueError('CONFIRMED_INITIAL_SAVE_OR_COACH_CHANGE_REQUIRED')
    tc=team(analysis,payload['team_id']).get('tactical_context',{})
    obj=tc.get('objects',{}).get(tc.get('coach_object_key'))
    if not obj or obj['native_identity']!=payload['current_coach_identity']:
        raise ValueError('CONFIRMED_COACH_MUST_MATCH_CURRENT_POST_CHANGE_SOURCE')
    return dict(**deepcopy(payload),source_binding=deepcopy(run['source_binding']),season=run['context']['season'],
        authority='OPERATOR_REFERENCE_TO_PLAYER_CONFIRMATION_NOT_GAME_WRITE_APPROVAL')


def strategy_candidate(run, analysis, t, review_row, final_version):
    tid=t['team_id']; r=review_row['payload']
    evolution=bpti_evolution.current(run,tid)
    base=next((s for s in run['strategy_bases'] if s['team_id']==tid),None)
    state=deepcopy(base) if base else {key:[] for key in LIST_FIELDS}
    revision=base['revision'] if base else 0
    validation=get(run,'VALIDATION','current')['payload']
    selected=get(run,'PORTFOLIO','selected')['payload']
    current_actions=[]
    for ref in selected['selected_offer_versions']:
        o=get(run,'OFFER',ref['offer_id'])['payload']
        if tid in o['team_ids']:
            ready=any(i['item_id']==o['offer_id'] for i in validation['specific_approval_items'])
            current_actions.append(dict(action_id=o['offer_id'],status='PROPOSED' if ready else 'RESEARCH',terms_revision=o['terms_revision'],terms_digest=o['terms_digest']))
    for ref in selected['selected_internal_action_versions']:
        if ref['team_id']!=tid:
            continue
        alt=next(a for a in get(run,'ALTERNATIVES',tid)['payload']['alternatives'] if a['alternative_id']==ref['alternative_id'])
        aid=alt['action']['action_id']
        ready=any(aid in item.get('source_internal_action_ids',[]) for item in validation['specific_approval_items'])
        current_actions.append(dict(alternative_id=ref['alternative_id'],action_id=aid,status='PROPOSED' if ready else 'RESEARCH',revision=ref['revision']))
    current_actions.extend(dict(status='HOLD',reason=h['reason']) for h in selected['holds'] if h['team_id']==tid)
    state.update(state_id=uuid4().hex,schema_version='TEAM_STRATEGY_STATE_V1',career_id=run['source_binding']['career_id'],
        team_id=tid,team_abbr=t['team'],revision=revision+1,supersedes_state_id=base['state_id'] if base else None,
        strategist_version=PROTOCOL,created_at=now(),source_binding=deepcopy(run['source_binding']),finance_run_id=analysis['finance_run_id'],
        finance_alignment=analysis['finance_alignment'],ownership_cost_preference_if_verified=None,
        competitive_window=dict(assessment=r['competitive_window']['assessment'],evidence=r['competitive_window']['evidence_refs'],alternatives=r['competitive_window']['alternatives']),
        contract_window=dict(status='ANALYSIS_ONLY',evidence=r['evidence_refs']),last_review_batch=run['source_binding']['batch_id'],
        status='REVIEWED_ANALYSIS',change_reason='Candidate derived from explicit complete team review, final '+str(final_version),
        identity_evidence=r['evidence_refs'],change_conditions=r['team_interest_profile']['reversal_conditions'],
        current_hypotheses=[r['monitoring_hypothesis']],observed_challenges=[r['decision_dimensions']],current_actions=current_actions,
        rejected_hypotheses=[deepcopy(a) for a in selected['rejected_alternatives']
            if a['alternative_id'] in {alt['alternative_id'] for alt in get(run,'ALTERNATIVES',tid)['payload']['alternatives']}])
    if not isinstance(state['change_conditions'],list):
        state['change_conditions']=[state['change_conditions']]
    b=run['artifacts'].get('BPTI_BLUEPRINT',{}).get(str(tid))
    e=evolution
    # A carried strategy base is historical; never inherit its old current BPTI state.
    state.pop('bpti_reasoning',None)
    state.pop('bpti_evolution',None)
    if b:
        state['bpti_reasoning']=dict(revision=b['revision'],payload=deepcopy(b['payload']))
    if e:
        state['bpti_evolution']=dict(revision=e['revision'],payload=deepcopy(e['payload']))
    validate_strategy(state)
    return dict(base_state_id=base['state_id'] if base else None,expected_revision=revision,candidate_state=state,
        reason=state['change_reason'],save_policy='EXPLICIT_M2_SAVE_ONLY')


def finalize(run, analysis):
    run=deepcopy(run)
    v=get(run,'VALIDATION','current')['payload']
    p=get(run,'PORTFOLIO','selected')
    if not v['valid_for_finalization'] or v['decision_run_revision']!=run['revision'] or v['portfolio_revision']!=p['revision']:
        raise ValueError('CURRENT_DETERMINISTIC_VALIDATION_REQUIRED')
    for tid in run['expected_team_ids']:
        bpti_evolution.current(run,tid)
    version=run['latest_final_version']+1
    hypotheses=[]; candidates=[]; summaries=[]
    selected_ids={ref['alternative_id'] for ref in p['payload']['selected_internal_action_versions']}
    hold_teams={h['team_id'] for h in p['payload']['holds']}
    market_teams={tid for ref in p['payload']['selected_offer_versions'] for tid in get(run,'OFFER',ref['offer_id'])['payload']['team_ids']}
    rejected={r['alternative_id']:r['reason'] for r in p['payload']['rejected_alternatives']}
    unselected=[]
    for tid in run['expected_team_ids']:
        row=get(run,'ALTERNATIVES',tid)
        for alt in row['payload']['alternatives']:
            if alt['alternative_id'] in selected_ids or (alt['category']=='HOLD' and tid in hold_teams):
                continue
            # A negotiated market package may differ from a broad research alternative; retain its reference.
            unselected.append(dict(team_id=tid,alternative_id=alt['alternative_id'],alternative_revision=row['revision'],
                status='EXPLICITLY_REJECTED' if alt['alternative_id'] in rejected else 'NOT_SELECTED',
                reason=rejected.get(alt['alternative_id'],alt['selection_reason']),
                negotiated_market_package_selected=tid in market_teams and alt['category']=='MARKET'))
    for t in analysis['teams']:
        r=get(run,'TEAM_REVIEW',t['team_id']); a=get(run,'ALTERNATIVES',t['team_id'])
        h=deepcopy(r['payload']['monitoring_hypothesis'])
        h.update(hypothesis_id=run['decision_run_id']+':'+str(t['team_id'])+':'+str(version),action_or_hold_id=str(t['team_id']),execution_receipt_ref=None)
        hypotheses.append(h)
        candidates.append(strategy_candidate(run,analysis,t,r,version))
        summaries.append(dict(team_id=t['team_id'],team=t['team'],competitive_window=r['payload']['competitive_window'],
            objective=r['payload']['team_interest_profile']['objective_and_window'],review_revision=r['revision'],alternatives_revision=a['revision']))
    f=dict(final_id=run['decision_run_id']+':final:'+str(version),version=version,decision_run_id=run['decision_run_id'],
        portfolio_revision=p['revision'],validation_report_id=v['report_id'],source_binding=run['source_binding'],protocol_version=PROTOCOL,
        status='FINAL_PROPOSED',approval_status='NOT_GRANTED',execution_authorized=False,team_summaries=summaries,
        specific_approval_items=v['specific_approval_items'],research_items=v['research_items'],holds=p['payload']['holds'],
        alternatives_not_selected=unselected,hypotheses=hypotheses,strategy_candidates=candidates,
        generated_artifact_refs=v['generated_artifact_refs'],supersedes_final_id=run['decision_run_id']+':final:'+str(version-1) if version>1 else None)
    f['bpti_artifacts']=[dict(kind=k,artifact_id=aid,revision=row['revision'],payload=deepcopy(row['payload']))
        for k in ('BPTI_BLUEPRINT','BPTI_EVOLUTION') for aid,row in run['artifacts'].get(k,{}).items()]
    run.update(current_final_version=version,latest_final_version=version,phase='P5',status='FINAL_PROPOSED')
    artifacts=[('FINAL','final',f)]
    artifacts.extend(('STRATEGY_CANDIDATE',str(c['candidate_state']['team_id']),c) for c in candidates)
    artifacts.extend(('HYPOTHESIS',str(t['team_id']),h) for t,h in zip(analysis['teams'],hypotheses))
    return run,artifacts


def summary(run):
    return dict(**{k:run[k] for k in ('decision_run_id','revision','mode','protocol_id','protocol_status','source_binding','analysis_run_id','context','phase','status','current_final_version')},
        season_phase=run.get('season_phase','UNKNOWN'),
        coach_events=[{k:e[k] for k in ('event_id','kind','team_id','season','reference')} for e in run.get('coach_events',[])],
        phase_progress=progress(run),approval_status='NOT_GRANTED',execution_authorized=False,
        offers=[dict(offer_id=o['payload']['offer_id'],terms_revision=o['payload']['terms_revision'],terms_digest=o['payload']['terms_digest'],
            status=negotiation.bilateral(o['payload'],[r['payload'] for r in run['artifacts'].get('RESPONSE',{}).values()],run['artifacts'].get('TEAM_REVIEW',{}),run['artifacts'].get('ALTERNATIVES',{}))) for o in run['artifacts'].get('OFFER',{}).values()])
