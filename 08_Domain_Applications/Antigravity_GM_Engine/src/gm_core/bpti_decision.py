"""B4 opt-in basketball reasoning in M3. Plain DTOs only; never stage or apply."""
from copy import deepcopy
from . import analysis_packet as ap
from .bpti import validate_bpti_knowledge
from .decision_handoff import native_intent
from .workbench_common import reject_authority, require, text_required

VERSION = 'BPTI_M3_REASONING_V1'
CATEGORIES = ('HOLD', 'INTERNAL', 'MARKET')


def hold(analysis, payload, reason):
    return dict(version=VERSION, team_id=payload.get('team_id'), status='HOLD',
                source_binding=deepcopy(analysis.get('source_binding', {})), hold_reasons=[reason],
                authority='DEVELOPMENT_CANDIDATE_NO_GAME_AUTHORITY', actual_team_assessment='UNASSESSED')


def prepare(run, analysis, index, payload):
    """Validate caller's basketball judgments, referencing existing facts and interfaces.

    No player-name heuristics, efficiency objective, native values or model dispatch
    are generated here. Unavailable source/knowledge/native support remains HOLD.
    """
    reject_authority(payload)
    require(payload, ('team_id', 'source_binding', 'blueprint', 'why_this_basketball',
                      'identity_application', 'role_evidence', 'decision_context',
                      'alternative_implications', 'native_actions'))
    try:
        ap.require_gm_packet(analysis)
        if payload['source_binding'] != analysis['source_binding'] or run['source_binding'] != analysis['source_binding']:
            raise ValueError('BPTI_SAME_SANITIZED_SOURCE_REQUIRED')
        if analysis.get('potential_mask', {}).get('source_role') != 'GM_SANITIZED':
            raise ValueError('BPTI_GM_SANITIZED_PACKET_REQUIRED')
        t = ap.team(analysis, payload['team_id'])
        blue = payload['blueprint']
        if blue['team_id'] != t['team_id']:
            raise ValueError('BPTI_BLUEPRINT_TEAM_MISMATCH')
        validate_bpti_knowledge(blue, index, as_of=analysis['source_binding']['game_date'], analysis=analysis)
        seed = index.team_identity(t['team'], as_of=analysis['source_binding']['game_date'])
        if seed['identity'] is None or blue['identity_ref'] != seed['identity_id']:
            raise ValueError('BPTI_HISTORICAL_IDENTITY_REFERENCE_MISMATCH')
        families = [blue['primary_system']] + blue['secondary_systems']
        views = [index.system(s, as_of=analysis['source_binding']['game_date']) for s in families]
        if any(v['card'] is None and not v.get('mechanism_entries') for v in views):
            raise ValueError('BPTI_SYSTEM_NOT_AVAILABLE_TO_GM')
        refs = payload['role_evidence']
        if {r['player_ref'] for r in refs} != {r['player_ref'] for r in blue['player_role_refs']}:
            raise ValueError('BPTI_ROLE_SKILL_EVIDENCE_REQUIRED')
        for role in refs:
            ap.validate_refs(analysis, role['evidence_refs'])
            text_required(role['reason'], 'visible_skill_role_reason')
            player = next(p for p in t['player_supply']['players'] if 'player:' + p['identity'] == role['player_ref'])
            if not role['skill_fields'] or any(
                f.casefold() in {'potential', 'intangibles', 'name', 'ovr', 'overall'} or player['decoded_attributes'].get(f) is None
                for f in role['skill_fields']
            ) or role['player_ref'] not in role['evidence_refs']:
                raise ValueError('BPTI_CURRENT_VISIBLE_SKILL_REQUIRED_NOT_HISTORICAL_NAME')
    except (ValueError, KeyError, StopIteration) as exc:
        return hold(analysis, payload, str(exc))

    text_required(payload['why_this_basketball'], 'why_this_basketball')
    identity = payload['identity_application']
    require(identity, ('retained_values', 'role_fit', 'internal_priority', 'market_after_internal', 'tradeoffs'))
    if not isinstance(identity['retained_values'], list) or not identity['retained_values']:
        raise ValueError('BPTI_RETAINED_IDENTITY_OR_EXPLICIT_UNKNOWN_REQUIRED')
    for k in ('role_fit', 'internal_priority', 'market_after_internal', 'tradeoffs'):
        text_required(identity[k], k)
    context = payload['decision_context']
    require(context, ('coach_fit', 'development_plan', 'market_gap_reason', 'identity_role_tradeoff'))
    for k, value in context.items():
        text_required(value, k)
    implications = payload['alternative_implications']
    if set(implications) != set(CATEGORIES):
        raise ValueError('BPTI_HOLD_INTERNAL_MARKET_COMPARISON_REQUIRED')
    for category in CATEGORIES:
        item = implications[category]
        require(item, ('means', 'cost', 'change_conditions'))
        text_required(item['means'], category + '_means')
        text_required(item['cost'], category + '_opportunity_cost')
        if not item['change_conditions']:
            raise ValueError('BPTI_ALTERNATIVE_RECONSIDERATION_REQUIRED')

    support, blocked, supported_actions = [], [], []
    mapped = set()
    for bid in blue['native_binding_refs']:
        b = index.binding(bid, as_of=analysis['source_binding']['game_date'])['binding']
        if b is None or b['system_id'] not in families:
            blocked.append(dict(binding_id=bid, reason='HOLD_UNAVAILABLE_OR_OTHER_FAMILY_BINDING'))
            continue
        support.append(b)
        if b['mapping_status'] in {'SUPPORTED_FIELD_DIRECTION', 'TYPE_MATCHED_ONLY'}:
            mapped.update(b['field_candidates'])
    for original in payload['native_actions']:
        action = deepcopy(original)
        action['team_id'] = t['team_id']
        try:
            # Reuse M3's existing native intent guard, never create a second executor.
            intent = native_intent(run, analysis, action)
            fields = {c['field_key'] for c in intent['changes']}
            if fields - mapped:
                raise ValueError('BPTI_UNKNOWN_OR_UNSUPPORTED_NATIVE_DIRECTION')
            if 'playbook.slot' in fields:
                raise ValueError('BPTI_CRC_SEMANTICS_TYPE_UNKNOWN_HOLD_SLOT_ACTION')
            ap.validate_refs(analysis, action['evidence_refs'])
            supported_actions.append(action)
        except (ValueError, PermissionError, KeyError) as exc:
            blocked.append(dict(action_id=action.get('action_id'), reason=str(exc)))
    dimensions = {
        'D1_STAFF': context['coach_fit'],
        'D2_TACTICS': blue['first_advantage'] + ' / ' + blue['opponent_counter'] + ' / ' + blue['second_answer'],
        'D3_ROSTER_USE': identity['role_fit'],
        'D4_MARKET': identity['market_after_internal'] + ' / ' + context['market_gap_reason'],
        'D5_ASSETS_AND_DEVELOPMENT': context['development_plan'] + ' / ' + identity['tradeoffs'],
        'D6_TEAM_IDENTITY_AND_MONITORING': context['identity_role_tradeoff'],
    }
    return dict(version=VERSION, team_id=t['team_id'], source_binding=deepcopy(analysis['source_binding']),
                status='DRAFT_UNAPPROVED', native_action_status='DRAFT_UNAPPROVED' if supported_actions else 'HOLD',
                blueprint=deepcopy(blue), why_this_basketball=payload['why_this_basketball'],
                primary_secondary_system=dict(primary=blue['primary_system'], secondary=blue['secondary_systems']),
                first_advantage=blue['first_advantage'], opponent_counter=blue['opponent_counter'], second_answer=blue['second_answer'],
                roles_agency=deepcopy(blue['player_role_refs']), role_evidence=deepcopy(refs),
                identity_application=deepcopy(identity), identity_reference=seed,
                dimension_links=dimensions, alternative_implications=deepcopy(implications),
                native_support_and_unknowns=dict(bindings=support, blocked=blocked, effects='UNKNOWN_NOT_PREDICTED'),
                supported_actions=supported_actions, hold_reasons=[],
                native_hold_reasons=[] if supported_actions else ['NO_SUPPORTED_NATIVE_ACTION'],
                observation_limits=['NO_BOX_SCORE_TRENDS_OR_WIN_RATE_EFFECT_CLAIMED', 'AI_CAN_OVERRIDE_MINUTE_BANDS',
                                    'POTENTIAL_MASKED_INTANGIBLES_NOT_SCOUTING_SKILL'],
                actual_team_assessment='UNASSESSED', authority='DEVELOPMENT_CANDIDATE_NO_GAME_AUTHORITY')


def attach_review(payload, row):
    obj = deepcopy(payload)
    if payload.get('bpti_blueprint_revision') != row['revision']:
        raise ValueError('BPTI_CURRENT_BLUEPRINT_REVISION_REQUIRED')
    b = row['payload']
    obj['basketball_reasoning'] = deepcopy(b)
    if 'roles_agency' in b:
        for role in b['roles_agency']:
            obj['team_interest_profile']['role_priorities'].extend(role['roles'])
    if 'dimension_links' in b:
        for dim, conclusion in b['dimension_links'].items():
            obj['decision_dimensions'][dim]['conclusion'] += ' | BPTI: ' + conclusion
    return obj


def attach_alternatives(payload, row, review):
    if (payload.get('bpti_blueprint_revision') != row['revision'] or
            review['payload'].get('bpti_blueprint_revision') != row['revision']):
        raise ValueError('BPTI_BLUEPRINT_REVIEW_STALE')
    obj, prepared = deepcopy(payload), row['payload']
    known = {a['action_id']: a for a in prepared.get('supported_actions', [])}
    for alt in obj['alternatives']:
        if alt['category'] == 'INTERNAL' and alt.get('action') and alt['action'] != known.get(alt['action']['action_id']):
            # Retain the unsupported hypothesis for research; it cannot be selected.
            alt['status'] = 'BLOCKED'
            alt['bpti_native_status'] = 'HOLD_UNSUPPORTED_NATIVE_ACTION'
        if prepared['status'] == 'HOLD' and alt['category'] == 'INTERNAL':
            alt['status'] = 'BLOCKED'
        # MARKET is governed by M3's gap/internal comparison, finance and negotiation,
        # not by the availability of a native tactical write.
        effect = prepared.get('alternative_implications', {}).get(alt['category'])
        if effect:
            alt['proposed_means'] += ' | BPTI: ' + effect['means']
            alt['costs_and_opportunity_costs'] += ' | BPTI: ' + effect['cost']
            alt['change_conditions'] += effect['change_conditions']
            alt['basketball_identity_tradeoff'] = deepcopy(prepared['identity_application'])
    return obj
