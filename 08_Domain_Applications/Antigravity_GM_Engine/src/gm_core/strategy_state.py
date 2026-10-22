"""Explicit caller-supplied strategy analysis with append-only revisions."""
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

VERSION = 'TEAM_STRATEGY_STATE_V1'
LIST_FIELDS = ('identity_reference', 'identity_evidence', 'core_assets_and_hold_thresholds',
               'tactical_direction', 'current_hypotheses', 'observed_challenges',
               'current_actions', 'change_conditions', 'rejected_hypotheses')


def initialize(context, knowledge):
    binding = context['source_binding']
    states = []
    for team in context['teams']:
        ref = knowledge.franchise(team['team'])
        state = dict(state_id=uuid4().hex, schema_version=VERSION, career_id=binding['career_id'],
            team_id=team['team_id'], team_abbr=team['team'], revision=1, supersedes_state_id=None,
            strategist_version='gm_strategy_v1', created_at=datetime.now(timezone.utc).isoformat(),
            source_binding=deepcopy(binding), finance_run_id=None, finance_alignment='NOT_LINKED',
            ownership_cost_preference_if_verified=None,
            competitive_window=dict(assessment='UNASSESSED', evidence=[], alternatives=[]),
            contract_window=dict(status='UNASSESSED', evidence=[]), last_review_batch=None,
            status='UNASSESSED', change_reason='Initial unassessed research candidate')
        state.update({name: [] for name in LIST_FIELDS})
        state['identity_reference'] = [dict(reference_id=ref['reference_id'], historical_period=ref['reference_period'],
                                          claim=ref['identity_reference'], source_id=ref['source_id'])]
        states.append(state)
    return states


def reject_approval(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key.casefold() in {'approved', 'approved_by', 'player_approved', 'executed', 'execution_receipt'}:
                raise ValueError('STRATEGY_CANNOT_GRANT_APPROVAL_OR_EXECUTION')
            reject_approval(item)
    elif isinstance(value, list):
        for item in value:
            reject_approval(item)


def validate(state, knowledge=None):
    required = ('state_id', 'schema_version', 'career_id', 'team_id', 'team_abbr', 'revision',
                'supersedes_state_id', 'strategist_version', 'created_at', 'source_binding',
                'finance_run_id', 'ownership_cost_preference_if_verified', 'competitive_window',
                'contract_window', 'last_review_batch', 'status', 'change_reason') + LIST_FIELDS
    if any(k not in state for k in required) or state['schema_version'] != VERSION:
        raise ValueError('STRATEGY_REQUIRED_FIELDS_OR_VERSION')
    if state['status'] not in {'UNASSESSED', 'DRAFT', 'REVIEWED_ANALYSIS'}:
        raise ValueError('STRATEGY_ANALYSIS_STATUS_REQUIRED')
    if type(state['revision']) is not int or state['revision'] < 1 or type(state['team_id']) is not int:
        raise ValueError('STRATEGY_INVALID_ID_OR_REVISION')
    for key in ('state_id', 'career_id', 'team_abbr', 'strategist_version', 'created_at', 'change_reason'):
        if not isinstance(state[key], str) or not state[key].strip():
            raise ValueError('STRATEGY_TEXT_REQUIRED:'+key)
    datetime.fromisoformat(state['created_at'])
    binding = state['source_binding']
    if not isinstance(binding, dict) or binding.get('career_id') != state['career_id'] or not all(binding.get(k) for k in ('batch_id', 'snapshot_id')):
        raise ValueError('STRATEGY_SOURCE_BINDING_REQUIRED')
    if any(not isinstance(state[k], list) for k in LIST_FIELDS):
        raise ValueError('STRATEGY_LIST_REQUIRED')
    for key in ('competitive_window', 'contract_window'):
        if not isinstance(state[key], dict):
            raise ValueError('STRATEGY_WINDOW_OBJECT_REQUIRED')
    window = state['competitive_window']
    if not isinstance(window.get('assessment'), str) or not all(isinstance(window.get(k), list) for k in ('evidence', 'alternatives')):
        raise ValueError('COMPETITIVE_WINDOW_FIELDS_REQUIRED')
    for action in state['current_actions']:
        if not isinstance(action, dict) or action.get('status') not in {'HOLD', 'PROPOSED', 'RESEARCH'}:
            raise ValueError('STRATEGY_ACTION_STATUS_REQUIRED')
    for item in state['core_assets_and_hold_thresholds']:
        if not isinstance(item, dict) or not all(item.get(k) for k in ('batch_local_identity', 'role', 'retain_reason', 'reconsider_conditions')):
            raise ValueError('CORE_ASSET_CONDITIONS_REQUIRED')
    for item in state['tactical_direction']:
        if not isinstance(item, dict) or not all(k in item for k in ('card_id', 'fit', 'missing_roles', 'evidence')):
            raise ValueError('TACTICAL_DIRECTION_FIELDS_REQUIRED')
        if knowledge and item['card_id'] not in {c['card_id'] for c in knowledge.cards}:
            raise ValueError('UNKNOWN_TACTIC_CARD')
    if state['status'] == 'UNASSESSED' and (state['current_actions'] or state['core_assets_and_hold_thresholds'] or state['ownership_cost_preference_if_verified'] is not None):
        raise ValueError('UNASSESSED_HAS_NO_DECISIONS_OR_BUDGET')
    if state['status'] != 'UNASSESSED' and (not state['identity_evidence'] or not state['change_conditions'] or state['last_review_batch'] != binding['batch_id']):
        raise ValueError('ASSESSED_STATE_NEEDS_EVIDENCE_AND_REVIEW_BATCH')
    if state['revision'] > 1 and not state['supersedes_state_id']:
        raise ValueError('REVISION_PREDECESSOR_REQUIRED')
    reject_approval(state)
    return state


def link_finance(state, run=None):
    result = deepcopy(state)
    if result['finance_run_id'] is None:
        result['finance_alignment'] = 'NOT_LINKED'
    elif run is None or run['run_id'] != result['finance_run_id']:
        raise ValueError('LINKED_FINANCE_RUN_REQUIRED')
    elif run['source_binding']['career_id'] != result['career_id']:
        raise ValueError('FINANCE_CAREER_MISMATCH')
    else:
        result['finance_alignment'] = ('SAME_BATCH' if run['source_binding']['batch_id'] == result['source_binding']['batch_id'] else 'DIFFERENT_BATCH_REVIEW_REQUIRED')
    return result
