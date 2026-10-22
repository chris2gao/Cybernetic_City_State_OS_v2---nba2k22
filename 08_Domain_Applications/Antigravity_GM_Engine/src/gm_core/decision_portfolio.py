"""Validate selected resources and executor dependencies, not universal team value."""
from collections import defaultdict
from copy import deepcopy
from .market_negotiation import bilateral
from .analysis_packet import validate_refs
from .workbench_common import require, text_required
from .coaching_batch import normalize_freelance
from coach_codec import load_profile
from .decision_handoff import NATIVE_KINDS, native_intent


def resolve(portfolio, artifacts, analysis):
    require(portfolio,('portfolio_id','selected_offer_versions','selected_internal_action_versions',
        'research_action_ids','holds','rejected_alternatives','team_combination_reviews'))
    offers, actions = [], []
    issues=[]
    for ref in portfolio['selected_offer_versions']:
        row=artifacts.get('OFFER',{}).get(ref['offer_id'])
        if not row or row['payload']['terms_revision']!=ref['terms_revision']:
            raise ValueError('SELECTED_OFFER_VERSION_NOT_CURRENT')
        offers.append(row['payload'])
    for ref in portfolio['selected_internal_action_versions']:
        row=artifacts.get('ALTERNATIVES',{}).get(str(ref['team_id']))
        if not row or row['revision']!=ref['revision']:
            raise ValueError('SELECTED_ALTERNATIVE_VERSION_NOT_CURRENT')
        matches=[a for a in row['payload']['alternatives'] if a['alternative_id']==ref['alternative_id']]
        if len(matches)!=1 or matches[0]['category']!='INTERNAL' or not matches[0].get('action'):
            raise ValueError('SPECIFIC_INTERNAL_ACTION_REQUIRED')
        if matches[0]['status']!='VIABLE_CANDIDATE':
            raise ValueError('SELECTED_INTERNAL_ALTERNATIVE_NOT_VIABLE')
        action=deepcopy(matches[0]['action']); action['team_id']=ref['team_id']
        action['alternative_ref']=ref
        actions.append(action)
    if len({o['offer_id'] for o in offers})!=len(offers) or len({a['action_id'] for a in actions})!=len(actions):
        raise ValueError('DUPLICATE_SELECTED_ITEM')
    expected={t['team_id'] for t in analysis['teams']}
    holds=portfolio['holds']
    if not isinstance(holds,list) or len({h['team_id'] for h in holds})!=len(holds):
        raise ValueError('UNIQUE_TEAM_HOLDS_REQUIRED')
    for h in holds:
        text_required(h.get('reason'),'hold_reason'); validate_refs(analysis,h.get('evidence_refs'))
    represented={t for o in offers for t in o['team_ids']}|{a['team_id'] for a in actions}|{h['team_id'] for h in holds}
    if represented!=expected:
        issues.append(dict(code='PORTFOLIO_TEAM_COVERAGE',effect='BLOCK_FINAL',missing_team_ids=sorted(expected-represented)))
    if {h['team_id'] for h in holds}&({t for o in offers for t in o['team_ids']}|{a['team_id'] for a in actions}):
        issues.append(dict(code='HOLD_WITH_SELECTED_ACTION',effect='BLOCK_FINAL'))
    for rejected in portfolio['rejected_alternatives']:
        require(rejected,('alternative_id','reason')); text_required(rejected['reason'],'rejected_reason')
    research=[]
    known={}
    for row in artifacts.get('ALTERNATIVES',{}).values():
        tid=row['payload']['team_id']
        for alt in row['payload']['alternatives']:
            item=dict(team_id=tid,alternative_revision=row['revision'],alternative=alt)
            known[alt['alternative_id']]=item
            if alt.get('action'):
                known[alt['action']['action_id']]=item
    refs=portfolio['research_action_ids']
    if not isinstance(refs,list) or any(not isinstance(k,str) or k not in known for k in refs) or len(set(refs))!=len(refs):
        raise ValueError('RESEARCH_IDS_MUST_RESOLVE_TO_ACTUAL_ALTERNATIVES_OR_ACTIONS')
    for ref in refs:
        research.append(dict(research_id=ref,**deepcopy(known[ref])))
    if any(r['alternative_id'] not in known for r in portfolio['rejected_alternatives']):
        raise ValueError('REJECTED_ALTERNATIVE_MUST_RESOLVE')
    return offers,actions,issues,research


def inspect(portfolio, artifacts, analysis, decision=None):
    offers,actions,issues,research=resolve(portfolio,artifacts,analysis)
    responses=[v['payload'] for v in artifacts.get('RESPONSE',{}).values()]
    reviews=artifacts.get('TEAM_REVIEW',{})
    assets={}; teams=defaultdict(list); fields={}
    bilateral_checks=[]
    for o in offers:
        state=bilateral(o,responses,reviews,artifacts.get('ALTERNATIVES',{}))
        bilateral_checks.append(dict(offer_id=o['offer_id'],status=state,terms_digest=o['terms_digest']))
        if state!='AGREED_IN_PRINCIPLE':
            issues.append(dict(code='BILATERAL_NOT_AGREED',object_id=o['offer_id'],effect='BLOCK_FINAL'))
        for t in o['team_ids']:
            teams[t].append(o['offer_id'])
        for move in o['moves']:
            key=move['source_identity'] if move['kind']=='TRADE_PLAYER' else move['asset_id']
            if key in assets:
                issues.append(dict(code='SELECTED_ASSET_CONFLICT',object_id=key,actions=[assets[key],o['offer_id']],effect='BLOCK_FINAL'))
            assets[key]=o['offer_id']
        if o['dependency_ids']:
            issues.append(dict(code='DEPENDENCY_UNSUPPORTED',object_id=o['offer_id'],effect='RESEARCH_ONLY'))
    for tid,oids in teams.items():
        if len(oids)>1:
            issues.append(dict(code='DEPENDENCY_UNSUPPORTED_SAME_TEAM_TRADES',team_id=tid,object_id=','.join(oids),effect='RESEARCH_ONLY',
                needed_input='Combine same-pair terms into one renegotiated offer; other overlapping-team sequences are unsupported'))
    rebound={a['team_id'] for a in actions if a['kind']=='TEAM_BOOK_REBIND'}
    for action in actions:
        if analysis.get('tactical_version') and (action['kind'] in NATIVE_KINDS or action['kind']=='COACHING'):
            try:
                context=decision or dict(source_binding=analysis['source_binding'],decision_run_id='PORTFOLIO_CHECK',revision=1,
                    coach_events=[e['payload'] for e in artifacts.get('COACH_EVENT',{}).values()])
                intent=native_intent(context,analysis,action)
                for c in intent['changes']:
                    key=(c['object_key'],c['field_key'])
                    if key in fields and fields[key][0]!=c['target_value']:
                        issues.append(dict(code='NATIVE_FIELD_CONFLICT',object_id=str(key),effect='BLOCK_FINAL'))
                    fields[key]=(c['target_value'],action['action_id'])
                opposing={analysis_t['tactical_context']['objects'][c['object_key']]['selector'].get('opponent_team_id')
                    for analysis_t in analysis['teams'] for c in intent['changes'] if c['object_key'] in analysis_t.get('tactical_context',{}).get('objects',{})}
                if action['team_id'] in teams or opposing&set(teams):
                    issues.append(dict(code='POST_TRADE_NATIVE_REPLAN_REQUIRED',object_id=action['action_id'],effect='RESEARCH_ONLY'))
                if action['team_id'] in rebound and action['kind'] in ('COACHING','COACH_DEFAULT','TEAM_EXCLUSIVE_PLAYBOOK_CONTENT','PLAYER_PLAY_TYPE'):
                    issues.append(dict(code='POST_REBIND_SOURCE_REQUIRED',object_id=action['action_id'],effect='RESEARCH_ONLY'))
            except ValueError as exc:
                issues.append(dict(code='NATIVE_PREPARATION_PENDING',object_id=action['action_id'],reason=str(exc),effect='RESEARCH_ONLY'))
        elif action['kind']=='COACHING':
            for request in action['requests']:
                if request['team_id']!=action['team_id']:
                    raise ValueError('INTERNAL_ACTION_CANNOT_CONTROL_ANOTHER_TEAM')
                for name,value in normalize_freelance(request['targets'],load_profile()).items():
                    key=(request['team_id'],request.get('opponent_team_id'),name)
                    if key in fields and fields[key][0]!=value:
                        issues.append(dict(code='COACH_FIELD_CONFLICT',object_id=str(key),effect='BLOCK_FINAL'))
                    fields[key]=(value,action['action_id'])
            if action['team_id'] in teams:
                issues.append(dict(code='POST_TRADE_COACHING_REPLAN_REQUIRED',object_id=action['action_id'],effect='RESEARCH_ONLY'))
        else:
            issues.append(dict(code='BLOCKED_EXECUTOR',object_id=action['action_id'],kind=action['kind'],effect='RESEARCH_ONLY'))
    # Multiple commitments require a separate team view of the selected combination.
    counts=defaultdict(list)
    for o in offers:
        for tid in o['team_ids']:
            counts[tid].append(o['offer_id'])
    for a in actions:
        counts[a['team_id']].append(a['action_id'])
    combo={r['team_id']:r for r in portfolio['team_combination_reviews']}
    for tid,ids in counts.items():
        if len(ids)>1:
            r=combo.get(tid)
            if not r or set(r.get('selected_ids',[]))!=set(ids) or r.get('team_interest_revision')!=reviews[str(tid)]['revision']:
                issues.append(dict(code='COMBINATION_REVIEW_REQUIRED',team_id=tid,effect='BLOCK_FINAL'))
            else:
                text_required(r.get('why_better_than_hold'),'combination_rationale'); validate_refs(analysis,r.get('evidence_refs'))
    return dict(offers=offers,actions=actions,issues=issues,research=research,bilateral_checks=bilateral_checks)
