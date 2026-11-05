"""Evidence-qualified basketball diagnosis over existing BIC baselines."""
from bic_baseline import knowledge_query, coverage_report, badge_intelligence
from bic_experiments import tactical_evidence_protocol, factorial_2x2
from bic_plans import plan_adjustment
import math

INSPECTION_FIELDS = (
    'player_vitals_observations.height_raw',
    'player_attribute_snapshots.shot_close_raw',
    'player_attribute_snapshots.mid_range_shot_raw',
    'player_attribute_snapshots.passing_accuracy_raw',
    'player_attribute_snapshots.interior_defense_raw',
    'player_attribute_snapshots.perimeter_defense_raw',
    'player_tendency_snapshots.shot_tendency_raw',
    'player_tendency_snapshots.dish_to_open_man_tendency_raw',
)


def _relative_profile(baseline):
    """Compare only existing registered-codec candidates, with their limits."""
    roles = {'shot_close_raw': 'Interior finishing candidate',
             'mid_range_shot_raw': 'Midrange scoring candidate',
             'passing_accuracy_raw': 'Facilitator candidate',
             'interior_defense_raw': 'Interior defensive role candidate',
             'perimeter_defense_raw': 'Perimeter defensive role candidate'}
    family = baseline['facts'].get('families', {}).get('player_attribute_snapshots', {})
    candidates = []
    for field, role in roles.items():
        observation = family.get(field, {})
        converted = observation.get('decoded_candidate') or {}
        if converted.get('value') is not None and observation.get('freshness', {}).get('status') == 'WITHIN_REQUESTED_AGE':
            candidates.append({'field': 'player_attribute_snapshots.' + field,
                               'candidate_value': converted['value'], 'candidate_role': role,
                               'conversion': converted, 'provenance': observation.get('provenance')})
    candidates.sort(key=lambda row: row['candidate_value'], reverse=True)
    distinct = len({row['candidate_value'] for row in candidates}) > 1
    return {'classification': 'HYPOTHESIS' if candidates else 'UNKNOWN',
            'relative_strength_candidates': [row for row in candidates if row['candidate_value'] == candidates[0]['candidate_value']] if candidates else [],
            'relative_weakness_candidates': [row for row in candidates if row['candidate_value'] == candidates[-1]['candidate_value']] if distinct else [],
            'basis': 'Within-player comparison of inspected registered-codec candidate values',
            'limits': ['Derived conversion has no current UI acceptance',
                       'Role names are analyst hypotheses, not Native role certifications',
                       'Relative attributes do not identify efficiency causes or optimal roles']}


def _same_context(first, second):
    for key in ('save_id', 'season_id'):
        if first[key] != second[key]:
            raise ValueError('Diagnostic context mismatch: ' + key)
    if first['observation_scope']['observed_through'] != second['observation_scope']['observed_through']:
        raise ValueError('Diagnostic observation cutoff mismatch')
    if first['game_mode'] != second['game_mode']:
        raise ValueError('Diagnostic game mode mismatch')
    if first['binding'].get('game_build') != second['binding'].get('game_build'):
        raise ValueError('Diagnostic build mismatch')


def _role_findings(baseline, role_requirements, comparison_baselines=()):
    """Evaluate explicit candidate role requirements without inventing game rules.

    Each requirement names an existing public field and a caller-supplied range
    with a source/rationale. The requirement is an assumption, not a certified
    NBA2K22 threshold. No inferred rating/UI transform is performed.
    """
    findings = []
    for requirement in role_requirements:
        name = requirement['field']
        if not requirement.get('rationale') or not requirement.get('source'):
            raise ValueError('Role requirement needs explicit rationale and source')
        for bound in ('minimum', 'maximum'):
            value = requirement.get(bound)
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
                raise ValueError('Role bounds must be finite numeric assumptions')
        if requirement.get('minimum') is not None and requirement.get('maximum') is not None and requirement['minimum'] > requirement['maximum']:
            raise ValueError('Role requirement range is inverted')
        evidence = knowledge_query(name, baseline=baseline, comparison_baselines=comparison_baselines)
        status = evidence['status']
        observation = evidence['sources'][0] if evidence['sources'] else {}
        freshness = observation.get('freshness') or {}
        if status == 'CONFLICT':
            verdict = 'CONFLICT'
        elif status != 'OBSERVATION_AVAILABLE' or freshness.get('status') != 'WITHIN_REQUESTED_AGE':
            verdict = 'UNKNOWN'
        else:
            value = observation['value']
            if type(value) not in (int, float):
                verdict = 'UNKNOWN'
            else:
                low, high = requirement.get('minimum'), requirement.get('maximum')
                outside = low is not None and value < low or high is not None and value > high
                verdict = 'CONFLICT' if outside else 'FACT'
        findings.append({'field': name, 'classification': verdict,
                         'conflict_type': 'SOURCE_CONFLICT' if status == 'CONFLICT' else ('CANDIDATE_ROLE_CONFLICT' if verdict == 'CONFLICT' else None),
                         'problem': 'Compatibility with candidate role requirement: ' + requirement['rationale'],
                         'support': evidence, 'requirement': requirement,
                         'mechanism_explanations': [
                             {'classification': 'HYPOTHESIS', 'text': 'Candidate role requirement may not match observed Native field'},
                             {'classification': 'HYPOTHESIS', 'text': 'Effective context, mode or unobserved mechanism may explain basketball outcome'}],
                         'uncertainty': ['Role threshold is a supplied assumption', 'Raw storage is not automatically a UI rating',
                                         'Observed efficiency does not identify its cause'],
                         'candidate_adjustments': [
                             {'classification': 'HYPOTHESIS', 'direction': 'ROLE_OR_TACTICAL_FIT',
                              'target_field': name, 'source': requirement['source'],
                              'description': 'Review the role requirement against this observed field before selecting a lineup or tactical role',
                              'capability': 'Role decision; no attribute or badge edit'},
                             {'classification': 'HYPOTHESIS', 'direction': 'CONTROLLED_MECHANISM_COMPARISON',
                              'target_field': name, 'description': 'Compare usage/tendency and coach context in separate treatment cells while holding the fixed roster',
                              'native_intent_candidate': 'OFFENSE_FOCUS', 'capability': 'UNKNOWN until a bound Native plan is checked'}],
                         'expected_impact': 'HYPOTHESIS; no numeric effect promised',
                         'validation': tactical_evidence_protocol(baseline['game_mode'])})
    return findings


def diagnose_player(baseline, *, role_requirements=(), comparison_baselines=(), intents=(), catalog=None, required_play_codes=()):
    if baseline['entity_kind'] != 'player':
        raise ValueError('Player baseline required')
    requested = role_requirements or [
        {'field': name, 'source': 'WorldData public field inspection',
         'rationale': 'Inspect actual observation and source gap; no role threshold asserted'}
        for name in INSPECTION_FIELDS]
    findings = _role_findings(baseline, requested, comparison_baselines)
    coverage = coverage_report(baseline)
    badge_report = badge_intelligence(baseline)
    play_types = baseline['facts'].get('families', {}).get('player_play_type_slots', [])
    play_type_fit = []
    for requirement in required_play_codes:
        if not requirement.get('source'):
            raise ValueError('PlayType role requirement needs a source')
        observed = [row for row in play_types if row.get('native_play_code') is not None]
        fresh = bool(observed) and all(row.get('freshness', {}).get('status') == 'WITHIN_REQUESTED_AGE' for row in observed)
        matches = [row for row in observed if str(row['native_play_code']) == str(requirement['code'])]
        status = 'UNKNOWN' if not fresh else ('FACT' if matches else 'CONFLICT')
        play_type_fit.append({'classification': status, 'candidate_role_requirement': requirement,
                              'observations': observed, 'registered_code_matches': matches,
                              'limit': 'Ordered PlayType registration does not prove a play was called or executed'})
    groups = {}
    for family, domain in coverage['domains'].items():
        groups[family] = {'status': domain['status'], 'observed_fields': domain.get('observed_fields', 0),
                          'missing_fields': domain.get('missing_fields', []),
                          'stale_fields': domain.get('stale_fields', [])}
    candidates = list(intents)
    for index, finding in enumerate(findings):
        suggestion = finding['requirement'].get('candidate_intent')
        if suggestion is not None:
            candidates.append({**suggestion, 'diagnosis_finding_index': index})
    plans = [plan_adjustment(intent, catalog) if catalog is not None else
             {'intent': intent, 'status': 'NEEDS_VALIDATION', 'capability_state': 'UNKNOWN',
              'execute': False, 'unknowns': ['Pinned Native catalog unavailable']}
             for intent in candidates]
    for plan in plans:
        identity = plan['intent'].get('identity_source') or {}
        gaps = []
        if not isinstance(identity, dict) or identity.get('save_id') != baseline['save_id'] or identity.get('season_id') != baseline['season_id']:
            gaps.append('DIAGNOSTIC_IDENTITY_NOT_BOUND')
        if baseline['game_mode'] == 'UNKNOWN' or plan['intent'].get('mode') != baseline['game_mode']:
            gaps.append('DIAGNOSTIC_MODE_NOT_BOUND')
        if baseline['binding'].get('game_build') != plan['intent'].get('game_build_sha256'):
            gaps.append('DIAGNOSTIC_BUILD_NOT_BOUND')
        plan['unknowns'].extend(gaps)
        if gaps and plan['status'] != 'FORBIDDEN':
            plan['status'] = 'NEEDS_VALIDATION'
    return {'entity_id': baseline['entity_id'], 'save_id': baseline['save_id'],
            'season_id': baseline['season_id'], 'mode': baseline['game_mode'],
            'data_status': baseline['data_status'], 'findings': findings,
            'relative_basketball_profile': _relative_profile(baseline),
            'coverage': groups, 'badge_facts': badge_report,
            'play_type_fit': play_type_fit,
            'observed_play_types': baseline['facts'].get('families', {}).get('player_play_type_slots', []),
            'game_observations': baseline['facts'].get('season_observations', []),
            'native_plans': plans, 'status': 'DIAGNOSIS_WITH_UNKNOWNS',
            'candidate_role_fit': {'supporting_fields': [f['field'] for f in findings if f['classification'] == 'FACT' and ('minimum' in f['requirement'] or 'maximum' in f['requirement'])],
                                   'conflicting_fields': [f['field'] for f in findings if f['classification'] == 'CONFLICT'],
                                   'unresolved_fields': [f['field'] for f in findings if f['classification'] == 'UNKNOWN'],
                                   'scope': 'Compatibility with supplied assumptions; not a certified basketball optimum'},
            'classification_contract': ['FACT', 'VERIFIED_MECHANISM', 'HYPOTHESIS', 'CONFLICT', 'UNKNOWN'],
            'verified_mechanisms': [],
            'experiment_requirements': {'cells': ['00', '10', '01', '11'],
                'controls': ['save/build/mode', 'team-season clusters', 'roster and coach',
                             'schedule/opponent', 'injury/fatigue/growth', 'randomness'],
                'status': 'CONTROLLED_MODE_SPECIFIC_EVIDENCE_REQUIRED'},
            'limits': ['No Native effect or role threshold certified by this diagnostic',
                       'Badge possession does not establish eligibility or causal game effect']}


def diagnose_team(team, players, *, roles=None, opponent=None, team_requirements=()):
    """Inspect a fixed supplied roster and its candidate role contracts."""
    if team['entity_kind'] != 'team':
        raise ValueError('Team baseline required')
    roles = roles or {}
    seen = set()
    reports = []
    for player in players:
        _same_context(team, player)
        if player['entity_id'] in seen:
            raise ValueError('Duplicate player in fixed roster')
        seen.add(player['entity_id'])
        memberships = player.get('roster_history', [])
        ordered = sorted(memberships, key=lambda row: (row.get('provenance', {}).get('observed_at', ''), row.get('unit_id', '')))
        membership = ordered[-1] if ordered else None
        if membership is not None and membership.get('team_id') != team['entity_id']:
            raise ValueError('Roster membership conflict')
        report = diagnose_player(player, role_requirements=roles.get(player['entity_id'], ()))
        report['roster_membership_status'] = 'OBSERVED' if membership else 'UNKNOWN'
        reports.append(report)
    if opponent is not None:
        if opponent['entity_kind'] != 'team':
            raise ValueError('Opponent must be a team baseline')
        _same_context(team, opponent)
    profiles = {}
    for report in reports:
        for finding in report['findings']:
            profiles.setdefault(finding['field'], []).append({
                'player_id': report['entity_id'], 'classification': finding['classification'],
                'support': finding['support'], 'requirement': finding['requirement']})
    technical_fit = []
    for field, comparisons in profiles.items():
        technical_fit.append({'field': field, 'players': comparisons,
                              'classification': 'HYPOTHESIS',
                              'interpretation': 'Compare which fixed-roster players meet each supplied role range',
                              'uncertainty': 'Complementarity, defensive matchup and rotation effects need controlled behavior evidence'})
    return {'team_id': team['entity_id'], 'fixed_roster': sorted(seen), 'players': reports,
            'team_context': team['facts'], 'opponent_context_status': 'SUPPLIED_SAME_SCOPE' if opponent else 'UNKNOWN',
            'team_setting_fit': _role_findings(team, team_requirements),
            'technical_fit': technical_fit,
            'complementarity': {'classification': 'HYPOTHESIS', 'basis': 'Explicit per-player candidate role requirements',
                                'missing': 'Certified role interactions and mode-specific matchup observations'},
            'defense_matchups': 'UNKNOWN', 'rotation_rationale': 'Candidate role evidence; minutes allocation not inferred',
            'validation': tactical_evidence_protocol(team['game_mode'])}


def diagnose_and_plan(player, *, catalog, role_requirements=(), intents=(), comparisons=(), required_play_codes=()):
    return diagnose_player(player, role_requirements=role_requirements,
                           comparison_baselines=comparisons, intents=intents, catalog=catalog,
                           required_play_codes=required_play_codes)


def synthetic_validation(cells):
    return factorial_2x2(cells, synthetic=True, mode='SYNTHETIC')
