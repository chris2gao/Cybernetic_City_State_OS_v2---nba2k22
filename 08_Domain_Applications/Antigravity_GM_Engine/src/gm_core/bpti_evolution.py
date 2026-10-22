"""B5 append-only evolution judgments. No name-based peak, simulation or approval."""
from copy import deepcopy
from . import analysis_packet as ap
from .workbench_common import require, text_required, reject_authority

LEVELS = ('ROLE_TWEAK', 'SECONDARY_BRANCH', 'CO_PRIMARY_SYSTEM', 'TACTICAL_REBASE',
          'COACH_ALIGNMENT_CHANGE', 'ORGANIZATIONAL_REIDENTIFICATION')


def current(run, team_id):
    """Return only an evolution bound to this run's current blueprint/source."""
    key=str(team_id)
    row=run['artifacts'].get('BPTI_EVOLUTION',{}).get(key)
    if row is None:
        return None
    blue=run['artifacts'].get('BPTI_BLUEPRINT',{}).get(key)
    value=row['payload']
    if (not blue or value.get('bpti_blueprint_revision')!=blue['revision']
            or value.get('team_id')!=team_id or value.get('source_binding')!=run['source_binding']
            or value.get('status')!='DRAFT_UNAPPROVED'):
        raise ValueError('BPTI_EVOLUTION_STALE_RECORDED_CURRENT_BLUEPRINT_REQUIRED')
    return row


def continuity_error(previous, binding, history_context):
    """Use existing native save identity; batch and season are intentionally excluded.

    A career name or manually repeated history label alone is not lineage proof.
    There is no certified cross-instance bridge in the existing M3 packet contract.
    """
    old=previous['source_binding']
    for key in ('save_id','save_instance_id','generation_id'):
        if not isinstance(old.get(key),str) or not old[key] or not isinstance(binding.get(key),str) or not binding[key]:
            return 'BPTI_PREVIOUS_SAVE_IDENTITY_UNPROVEN'
        if old[key]!=binding[key]:
            return 'BPTI_PREVIOUS_SAVE_IDENTITY_MISMATCH:'+key
    if previous.get('history_branch_context')!=history_context:
        return 'BPTI_PREVIOUS_HISTORY_BRANCH_UNPROVEN_OR_DIFFERENT'
    return None


def record(run, analysis, row, payload, previous=None):
    reject_authority(payload)
    require(payload, ('team_id', 'source_binding', 'bpti_blueprint_revision', 'level',
                      'previous_ref', 'observed_changes', 'decision_reason', 'retained_culture',
                      'proposed_culture', 'coach_alignment', 'reconsider_conditions'))
    if payload['source_binding'] != analysis['source_binding'] or row['payload']['source_binding'] != analysis['source_binding']:
        raise ValueError('BPTI_EVOLUTION_SOURCE_MISMATCH')
    if payload['bpti_blueprint_revision'] != row['revision']:
        raise ValueError('BPTI_CURRENT_BLUEPRINT_REVISION_REQUIRED')
    if payload['level'] not in LEVELS:
        raise ValueError('BPTI_UNKNOWN_EVOLUTION_LEVEL')
    b = row['payload']; t = ap.team(analysis, payload['team_id'])
    if 'blueprint' not in b or b['status'] == 'HOLD':
        return dict(team_id=t['team_id'], source_binding=deepcopy(analysis['source_binding']),
                    status='HOLD', reason='AVAILABLE_SOURCE_BOUND_BLUEPRINT_REQUIRED', previous_ref=payload['previous_ref'])
    text_required(payload['decision_reason'], 'evolution_reason')
    text_required(payload['coach_alignment'], 'coach_alignment')
    if not payload['retained_culture'] or not payload['proposed_culture'] or not payload['reconsider_conditions']:
        raise ValueError('BPTI_CULTURE_AND_REVERSAL_REQUIRED')
    if payload['previous_ref'] is not None and previous is None:
        raise ValueError('BPTI_STORED_PREVIOUS_EVOLUTION_REQUIRED')
    if previous:
        if previous['team_id'] != t['team_id'] or previous['source_binding']['career_id'] != run['source_binding']['career_id'] or previous['status'] != 'DRAFT_UNAPPROVED':
            raise ValueError('BPTI_PREVIOUS_TEAM_CAREER_OR_STATUS_MISMATCH')
        error=continuity_error(previous,run['source_binding'],run['context'].get('history_branch_context'))
        if error:
            return dict(team_id=t['team_id'],source_binding=deepcopy(analysis['source_binding']),status='HOLD',
                        reason=error,previous_ref=deepcopy(payload['previous_ref']),bpti_blueprint_revision=row['revision'])
        old_culture = previous['proposed_culture']
        if payload['retained_culture'] != old_culture:
            raise ValueError('BPTI_RETAIN_PREVIOUS_CULTURE_BEFORE_CHANGE')
    else:
        old_culture = payload['retained_culture']
    changes = payload['observed_changes']
    if not isinstance(changes, list) or not changes:
        raise ValueError('BPTI_OBSERVED_CHANGE_EVIDENCE_REQUIRED')
    for change in changes:
        require(change, ('kind', 'evidence_refs', 'observation', 'uncertainty'))
        if change['kind'] not in ('VISIBLE_SKILL', 'ROSTER_ROLE', 'COACH', 'MANAGEMENT', 'LONG_TERM', 'MONTHLY_RESULT'):
            raise ValueError('BPTI_UNKNOWN_OBSERVATION_KIND')
        if not change['evidence_refs']:
            raise ValueError('BPTI_OBSERVATION_REFS_REQUIRED')
        ap.validate_refs(analysis, change['evidence_refs'])
        text_required(change['observation'], 'observation')
        text_required(change['uncertainty'], 'uncertainty')
    kinds = {c['kind'] for c in changes}
    if payload['level'] == 'COACH_ALIGNMENT_CHANGE' and 'COACH' not in kinds:
        raise ValueError('BPTI_COACH_OBSERVATION_REQUIRED')
    if payload['proposed_culture'] != old_culture or payload['level'] == 'ORGANIZATIONAL_REIDENTIFICATION':
        if payload['level'] != 'ORGANIZATIONAL_REIDENTIFICATION' or not {'MANAGEMENT', 'LONG_TERM'} <= kinds:
            raise ValueError('BPTI_CULTURE_INERTIA_REQUIRES_LONG_TERM_AND_MANAGEMENT_EVIDENCE')
        require(payload, ('long_term_context',))
        context = payload['long_term_context']
        require(context, ('seasons', 'management_reference', 'why_tactics_or_coach_alone_insufficient'))
        if not isinstance(context['seasons'], list) or len(set(context['seasons'])) < 2:
            raise ValueError('BPTI_CULTURE_NOT_REWRITTEN_BY_ONE_MONTH')
        text_required(context['management_reference'], 'management_reference')
        text_required(context['why_tactics_or_coach_alone_insufficient'], 'culture_change_reason')
    return dict(version='BPTI_EVOLUTION_V1', team_id=t['team_id'], source_binding=deepcopy(analysis['source_binding']),
                season=run['context']['season'], history_branch_context=deepcopy(run['context'].get('history_branch_context')),
                status='DRAFT_UNAPPROVED', level=payload['level'],
                previous_ref=deepcopy(payload['previous_ref']), previous_system=deepcopy(previous.get('proposed_system')) if previous else None,
                previous_culture=deepcopy(old_culture), observed_changes=deepcopy(changes),
                proposed_system=deepcopy(b['primary_secondary_system']), proposed_culture=deepcopy(payload['proposed_culture']),
                role_evidence=deepcopy(b['role_evidence']), coach_alignment=payload['coach_alignment'],
                decision_reason=payload['decision_reason'], reconsider_conditions=deepcopy(payload['reconsider_conditions']),
                bpti_blueprint_revision=row['revision'], long_term_context=deepcopy(payload.get('long_term_context')),
                approval_status='NOT_GRANTED', execution_authorized=False, actual_team_assessment='UNASSESSED',
                write_policy='EXISTING_M3_ARTIFACT_HISTORY_ONLY_NO_STAFF_MARKET_OR_GAME_WRITE')
