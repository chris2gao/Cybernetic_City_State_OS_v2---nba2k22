"""Pure three-year salary scenarios. Slot values are not certified purchasing power."""
from datetime import datetime, timezone
import re
from uuid import uuid4

VERSION = 'gm_finance_projection_v1'


def money(value):
    return type(value) is int and 0 <= value <= 2**31 - 1


def season_start(season):
    if not isinstance(season, str) or not re.fullmatch(r'\d{4}-\d{4}', season):
        raise ValueError('INVALID_SEASON: use YYYY-YYYY')
    a, b = map(int, season.split('-'))
    if b != a + 1:
        raise ValueError('INVALID_SEASON: years must be consecutive')
    return a


def seasons(base, horizon=3):
    if type(horizon) is not int or not 1 <= horizon <= 6:
        raise ValueError('HORIZON_MUST_BE_1_TO_6')
    y = season_start(base)
    return [f'{i}-{i+1}' for i in range(y, y+horizon)]


def field(contract, name):
    item = contract.get(name)
    return item.get('value') if isinstance(item, dict) else item


def value(amount, basis='CALCULATED', coverage='COMPLETE', refs=None, assumptions=None, reasons=None):
    return dict(value=amount, unit='USD', basis=basis, coverage=coverage,
                source_refs=refs or [], assumption_ids=assumptions or [], unknown_reasons=reasons or [])


def summarize(entries, predicate=lambda x: True, basis='CALCULATED'):
    selected = [e for e in entries if predicate(e) and e['amount'] is not None]
    if not entries:
        return value(0, basis)
    coverage = 'COMPLETE' if len(selected) == len(entries) else ('PARTIAL' if selected else 'NONE')
    return value(sum(e['amount'] for e in selected) if selected else None, basis, coverage,
                 [e['identity'] for e in selected], sorted({a for e in selected for a in e['assumption_ids']}),
                 sorted({r for e in entries for r in e['unknown_reasons']}))


def normalize_player(row):
    c = row.get('contract') or {}
    slots = [field(c, f'contract_year_{i}') for i in range(1, 7)]
    return dict(identity=row['identity'], name=row['name'], team_id=row['team_id'], team=row['team'],
                salary_slots=slots, years_left=field(c, 'years_left_on_contract'),
                original_contract_years=field(c, 'original_contract_years'),
                contract_option=field(c, 'contract_option'), extension_length=field(c, 'extension_length'),
                extension_option=field(c, 'extension_option'), contract_type=field(c, 'contract_type'),
                season_mapping=row.get('season_mapping', {}))


def player_year(player, target, base, assumptions):
    index = season_start(target) - season_start(base)
    override = assumptions.get('player_overrides', {}).get(player['identity'], {})
    mapping = player.get('season_mapping', {})
    slot = next((int(k) for k, v in override.get('slot_seasons', {}).items() if v == target), index+1)
    if not 1 <= slot <= 6:
        raise ValueError('INVALID_SLOT_MAPPING')
    certified = mapping.get(str(slot), {}).get('season') == target and mapping[str(slot)].get('basis') == 'OBSERVED'
    raw = player['salary_slots'][slot-1]
    amount = raw if money(raw) else None
    reasons = [] if amount is not None else ['MISSING_SALARY_SLOT']
    conditions = []
    if not certified:
        reasons.append('SEASON_MAPPING_ASSUMED')
    if index > 0:
        if player.get('years_left') is None:
            conditions.append('CONTRACT_YEARS_UNKNOWN')
        if player.get('contract_option') not in (0, None):
            conditions.append('OPTION_YEAR_UNVERIFIED')
        elif player.get('contract_option') is None:
            conditions.append('OPTION_STATE_UNKNOWN')
        if player.get('extension_length') not in (0, None):
            conditions.append('EXTENSION_NOT_ADDED_TO_EXISTING_SLOTS')
        elif player.get('extension_length') is None:
            conditions.append('EXTENSION_STATE_UNKNOWN')
        if amount == 0:
            conditions.append('ZERO_SLOT_NOT_CERTIFIED_NO_OBLIGATION')
        years_left = player.get('years_left')
        if type(years_left) is int and slot > years_left and amount:
            conditions.append('POSITIVE_SLOT_BEYOND_OBSERVED_YEARS_LEFT')
    option_season = override.get('option_season')
    if option_season == target:
        conditions = [c for c in conditions if c != 'OPTION_YEAR_UNVERIFIED']
        if override.get('option_decision') == 'DECLINE':
            amount = 0
        elif override.get('option_decision') != 'EXERCISE':
            conditions.append('OPTION_DECISION_REQUIRED')
    conditions = sorted(set(conditions))
    aids = [] if certified else [f'SLOT_SEQUENCE:{player["identity"]}:{target}']
    if override:
        aids.append(f'PLAYER_OVERRIDE:{player["identity"]}:{target}')
    return dict(identity=player['identity'], name=player['name'], season=target, slot=slot,
                observed_slot_amount=raw, amount=amount, basis='OBSERVED' if certified else 'SCENARIO',
                unconditional=certified and not conditions, assumption_ids=aids,
                unknown_reasons=reasons+conditions, conditions=conditions,
                option_branches=({'EXERCISE': raw if money(raw) else None, 'DECLINE': 0}
                                 if option_season == target else None))


def eligibility(policy, binding, season, total, team_id, phase):
    reasons = []
    if not policy or policy.get('status') != 'PLAYER_CONFIRMED' or not policy.get('evidence_ref'):
        reasons.append('NO_CONFIRMED_EXTERNAL_FINANCE_POLICY')
    applies = (policy or {}).get('applies_to', {})
    if applies.get('career_id') != binding.get('career_id') or season not in applies.get('seasons', []) or phase not in applies.get('phases', []):
        reasons.append('POLICY_SCOPE_NOT_APPLICABLE')
    if (policy or {}).get('expires_after_season') and season_start(season) > season_start(policy['expires_after_season']):
        reasons.append('POLICY_EXPIRED')
    if (policy or {}).get('counting_basis') != 'ROSTER_CONTRACT_SALARY_ONLY':
        reasons.append('COUNTING_BASIS_UNSUPPORTED')
    limit = (policy or {}).get('team_spending_limit_by_season', {}).get(str(team_id), {}).get(season)
    if not money(limit):
        reasons.append('TEAM_SPENDING_LIMIT_UNKNOWN')
    if total['coverage'] != 'COMPLETE' or total['unknown_reasons']:
        reasons.append('COMMITMENT_OR_SEMANTICS_INCOMPLETE')
    if reasons:
        return dict(status='UNKNOWN', scope='EXTERNAL_POLICY_ONLY_NOT_NATIVE_CBA', limit=limit,
                    headroom=None, reasons=reasons)
    gap = limit-total['value']
    return dict(status='WITHIN_EXTERNAL_LIMIT' if gap >= 0 else 'OVER_EXTERNAL_LIMIT',
                scope='EXTERNAL_POLICY_ONLY_NOT_NATIVE_CBA', limit=limit, headroom=gap, reasons=[])


def team_results(players, team, targets, base, assumptions, picks, binding, policy=None):
    result = []
    for target in targets:
        entries = [player_year(p, target, base, assumptions) for p in players]
        projected = summarize(entries, basis='SCENARIO')
        known = summarize(entries, lambda e: e['unconditional'])
        full_known = value(known['value'] if known['coverage'] == 'COMPLETE' else None,
                           coverage=known['coverage'], refs=known['source_refs'], reasons=known['unknown_reasons'])
        projected_total = value(projected['value'] if projected['coverage'] == 'COMPLETE' else None,
                                'SCENARIO', projected['coverage'], projected['source_refs'],
                                projected['assumption_ids'], projected['unknown_reasons'])
        reference = assumptions.get('reference_lines', {}).get(target, {})
        def proxy(key):
            line = reference.get(key)
            amount = line-projected_total['value'] if money(line) and projected_total['value'] is not None else None
            return value(amount, 'SCENARIO', 'COMPLETE' if amount is not None else 'NONE',
                         assumptions=[f'REFERENCE_LINE:{target}:{key}'],
                         reasons=['PROXY_NOT_SIGNING_CAPACITY'])
        result.append(dict(team_id=team['team_id'], team=team['team'], season=target,
            known_salary_subtotal=known, known_salary_total=full_known,
            projected_known_subtotal=projected, projected_salary_total=projected_total,
            observed_slot_amounts=entries,
            conditional_salary=[e for e in entries if e['conditions']],
            known_contract_count=sum(e['unconditional'] for e in entries),
            uncertain_contract_count=sum(not e['unconditional'] for e in entries),
            known_roster_occupancy=len(players) if target == base else None,
            projected_contract_count=sum(e['amount'] is not None and e['amount'] > 0 for e in entries),
            salary_cap_proxy_gap=proxy('salary_cap'), tax_line_proxy_gap=proxy('tax_line'),
            signing_capacity=value(None, coverage='NONE', reasons=['NOT_CERTIFIED_FROM_CASH_OR_CAP_PROXY']),
            finance_eligibility=eligibility(policy, binding, target, projected_total, team['team_id'], assumptions.get('phase', 'UNKNOWN')),
            pick_assets=[p for p in picks if p['team_id'] == team['team_id']],
            unknown_costs=['DRAFT_ROOKIE_SALARIES', 'FUTURE_SIGNINGS', 'TAX_AND_NON_ROSTER_COSTS']))
    return result


def project(inputs, base_season=None, horizon=3, assumptions=None, policy=None, run_id=None):
    assumptions = assumptions or {}
    base = base_season or inputs.get('context', {}).get('season') or inputs.get('context', {}).get('season_id')
    if not base:
        raise ValueError('BASE_SEASON_REQUIRED')
    targets = seasons(base, horizon)
    teams = inputs['teams']
    if len({t['team_id'] for t in teams}) != len(teams):
        raise ValueError('DUPLICATE_TEAM_IDENTITY')
    players = [normalize_player(p) for p in inputs['players']]
    if len({p['identity'] for p in players}) != len(players):
        raise ValueError('DUPLICATE_PLAYER_IDENTITY')
    if any(p['team_id'] not in {t['team_id'] for t in teams} for p in players):
        raise ValueError('PLAYER_TEAM_NOT_IN_INPUT')
    binding = inputs['source_binding']
    result = dict(schema_version=1, calculation_version=VERSION, run_id=run_id or 'finance_'+uuid4().hex,
        created_at=datetime.now(timezone.utc).isoformat(), status='ANALYSIS_ONLY', source_binding=binding,
        base_season=base, horizon_seasons=targets,
        season_anchor_evidence='CALLER_SUPPLIED' if base_season else 'SNAPSHOT_CONTEXT',
        rule_set_id=policy.get('policy_id') if policy else None, policy=policy,
        assumptions=assumptions, players=players, teams=[], finance_observed=inputs.get('finance', []),
        finance_semantics=inputs.get('finance_semantics', []), picks=inputs.get('picks', []), scenarios=[])
    for team in teams:
        rows = team_results([p for p in players if p['team_id'] == team['team_id']], team, targets,
                            base, assumptions, result['picks'], binding, policy)
        result['teams'].append(dict(team_id=team['team_id'], team=team['team'], years=rows))
    return result
