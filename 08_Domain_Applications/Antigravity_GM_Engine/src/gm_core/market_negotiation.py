"""Independent bilateral responses to canonical, version-bound trade terms."""
from copy import deepcopy
import hashlib
import json
from .workbench_common import require, reject_authority, text_required
from .analysis_packet import validate_refs


def canonical_terms(source_binding, team_ids, moves, conditions, dependency_ids):
    return dict(source_binding=deepcopy(source_binding), team_ids=sorted(team_ids),
        moves=sorted(deepcopy(moves),key=lambda m:(m['kind'],m.get('source_identity',m.get('asset_id','')),m['from_team_id'],m['to_team_id'])),
        conditions=deepcopy(conditions),dependency_ids=sorted(dependency_ids))


def digest(terms):
    return hashlib.sha256(json.dumps(terms,sort_keys=True,ensure_ascii=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def integer_money(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if key in ('amount','cash_amount','salary','salaries'):
                values=item if isinstance(item,list) else [item]
                if any(type(v) is not int for v in values):
                    raise ValueError('INTEGER_MONETARY_TERMS_REQUIRED')
            integer_money(item)
    elif isinstance(value,list):
        for item in value:
            integer_money(item)


def offer(payload, decision, analysis, revision):
    reject_authority(payload)
    require(payload,('offer_id','team_ids','moves','conditions','dependency_ids'))
    if set(payload)-{'offer_id','team_ids','moves','conditions','dependency_ids','finance_scenario_ref'}:
        raise ValueError('UNSUPPORTED_OFFER_FIELDS')
    text_required(payload['offer_id'],'offer_id')
    teams=payload['team_ids']
    if not isinstance(teams,list) or len(teams)!=2 or len(set(teams))!=2 or any(type(t) is not int or t not in decision['expected_team_ids'] for t in teams):
        raise ValueError('EXACT_TWO_OBSERVED_TEAMS_REQUIRED')
    players={p['identity']:p for t in analysis['teams'] for p in t['player_supply']['players']}
    picks={p['asset_id']:p for t in analysis['teams'] for p in t['financial_and_assets']['picks']}
    if not isinstance(payload['moves'],list) or not payload['moves']:
        raise ValueError('SPECIFIC_MOVES_REQUIRED')
    used=set()
    for m in payload['moves']:
        require(m,('kind','from_team_id','to_team_id'))
        if set(m)-{'kind','source_identity','asset_id','from_team_id','to_team_id'}:
            raise ValueError('ORDINARY_TRADE_PRESERVES_CONTRACT_NO_EXTRA_TERMS')
        if any(type(m[k]) is not int for k in ('from_team_id','to_team_id')) or set((m['from_team_id'],m['to_team_id']))!=set(teams):
            raise ValueError('MOVE_MUST_CONNECT_THE_TWO_TEAMS')
        if m['kind']=='TRADE_PLAYER':
            if 'asset_id' in m:
                raise ValueError('EXACT_PLAYER_IDENTITY_FIELD_REQUIRED')
            identity=m.get('source_identity'); owner=players.get(identity)
        elif m['kind']=='TRADE_PICK':
            if 'source_identity' in m:
                raise ValueError('EXACT_PICK_ASSET_FIELD_REQUIRED')
            identity=m.get('asset_id'); owner=picks.get(identity)
            if not owner or owner['trade_eligible']!=1:
                raise ValueError('PICK_NOT_CURRENT_SIMPLE_TRADE_ELIGIBLE')
        else:
            raise ValueError('SUPPORTED_TRADE_MOVES_ONLY')
        if not isinstance(identity,str) or not identity or not owner or owner['team_id']!=m['from_team_id'] or identity in used:
            raise ValueError('ASSET_NOT_OWNED_OR_DUPLICATE')
        if identity in decision.get('protected_identities',[]):
            raise ValueError('PLAYER_BOUND_IDENTITY_PROTECTED')
        used.add(identity)
    if not isinstance(payload['conditions'],list) or not isinstance(payload['dependency_ids'],list) or any(not isinstance(d,str) for d in payload['dependency_ids']):
        raise ValueError('CONDITIONS_AND_DEPENDENCIES_ARRAY_REQUIRED')
    integer_money(payload['conditions'])
    terms=canonical_terms(decision['source_binding'],teams,payload['moves'],payload['conditions'],payload['dependency_ids'])
    result=deepcopy(payload)
    if payload.get('finance_scenario_ref') and payload['finance_scenario_ref'] not in analysis.get('finance_scenario_refs',[]):
        raise ValueError('FINANCE_SCENARIO_MUST_RESOLVE_TO_LINKED_RUN')
    result.update(source_binding=deepcopy(decision['source_binding']),terms_revision=revision,terms_digest=digest(terms),status='NEGOTIATING')
    return result


def response(payload, offer, decision, analysis, reviews, alternatives):
    # A response echoes the tool-generated digest; it cannot generate it or grant approval.
    reject_authority({k:v for k,v in payload.items() if k!='terms_digest'})
    require(payload,('response_id','offer_id','terms_revision','terms_digest','responding_team_id','team_interest_revision',
        'stance','rationale','alternative_refs','conditions','evidence_refs'))
    t=payload['responding_team_id']
    if payload['offer_id']!=offer['offer_id'] or t not in offer['team_ids']:
        raise ValueError('RESPONSE_PARTY_OR_OFFER_MISMATCH')
    if payload['terms_revision']!=offer['terms_revision'] or payload['terms_digest']!=offer['terms_digest']:
        raise ValueError('STALE_OFFER_RESPONSE')
    if payload['team_interest_revision']!=reviews[str(t)]['revision']:
        raise ValueError('STALE_TEAM_INTEREST')
    if payload['stance'] not in ('ACCEPT_IN_PRINCIPLE','REJECT','COUNTER','NEEDS_EVIDENCE'):
        raise ValueError('INVALID_RESPONSE_STANCE')
    if not isinstance(payload['conditions'],list):
        raise ValueError('RESPONSE_CONDITIONS_ARRAY_REQUIRED')
    if payload['stance']=='ACCEPT_IN_PRINCIPLE' and payload['conditions']:
        raise ValueError('NEW_CONDITIONS_REQUIRE_COUNTER')
    require(payload['rationale'],('gain','cost','opportunity_cost','why_better_than_hold'))
    for k,v in payload['rationale'].items():
        text_required(v,k)
    own_ids={a['alternative_id'] for a in alternatives[str(t)]['payload']['alternatives']}
    if not payload['alternative_refs'] or not set(payload['alternative_refs'])<=own_ids:
        raise ValueError('OWN_TEAM_ALTERNATIVE_REFS_REQUIRED')
    validate_refs(analysis,payload['evidence_refs'])
    result=deepcopy(payload)
    result['team_alternatives_revision']=alternatives[str(t)]['revision']
    return result


def bilateral(offer, responses, reviews, alternatives=None):
    valid={}
    for r in responses:
        if r['offer_id']==offer['offer_id'] and r['terms_revision']==offer['terms_revision'] and r['terms_digest']==offer['terms_digest']:
            valid[r['responding_team_id']]=r
    if any(r['stance']=='REJECT' for r in valid.values()):
        return 'NO_DEAL'
    if any(r['stance']=='COUNTER' for r in valid.values()):
        return 'NEGOTIATING'
    if all(t in valid and valid[t]['stance']=='ACCEPT_IN_PRINCIPLE' and
           valid[t]['team_interest_revision']==reviews[str(t)]['revision'] and
           (alternatives is None or valid[t].get('team_alternatives_revision')==alternatives[str(t)]['revision']) for t in offer['team_ids']):
        return 'AGREED_IN_PRINCIPLE'
    return 'NEGOTIATING'
