"""Pure mutually exclusive alternatives; no offers, approvals or game writes."""
from copy import deepcopy
from .finance_projection import eligibility, money, season_start, summarize, value

KINDS = {'KEEP', 'INTERNAL_COACHING', 'TRADE_OR_SIGNING'}


def compare(run, proposal):
    kind = proposal.get('kind')
    if kind not in KINDS or not proposal.get('scenario_id'):
        raise ValueError('SCENARIO_ID_AND_KIND_REQUIRED')
    moves = proposal.get('moves', [])
    if not isinstance(moves, list) or (kind != 'TRADE_OR_SIGNING' and moves):
        raise ValueError('ROSTER_MOVES_REQUIRE_TRADE_OR_SIGNING')
    teams = {t['team_id']: t for t in run['teams']}
    rows = {(t['team_id'], y['season']): deepcopy(y['observed_slot_amounts']) for t in run['teams'] for y in t['years']}
    original_players = {p['identity']: p for p in run['players']}
    owners = {identity: p['team_id'] for identity, p in original_players.items()}
    picks = {p['asset_id']: deepcopy(p) for p in run['picks']}
    used, affected, assets = set(), set(), []
    unknown = []
    for move in moves:
        action = move.get('type')
        identity = move.get('asset_id') if action == 'TRADE_PICK' else move.get('identity')
        if not identity or identity in used:
            raise ValueError('MISSING_OR_DUPLICATE_SCENARIO_ASSET')
        used.add(identity)
        target = move.get('to_team_id')
        if type(target) is not int or target not in teams:
            raise ValueError('UNKNOWN_TARGET_TEAM')
        source = move.get('from_team_id')
        affected.add(target)
        if action in ('TRADE_PLAYER', 'TRADE_PICK'):
            if source not in teams or source == target:
                raise ValueError('INVALID_SOURCE_TEAM')
            affected.add(source)
        if action == 'TRADE_PLAYER':
            if identity not in owners or owners[identity] != source:
                raise ValueError('PLAYER_NOT_OWNED_BY_SOURCE')
            for season in run['horizon_seasons']:
                entries = rows[(source, season)]
                entry = next(e for e in entries if e['identity'] == identity)
                entries.remove(entry)
                rows[(target, season)].append(entry)
            owners[identity] = target
        elif action == 'TRADE_PICK':
            if identity not in picks or picks[identity]['team_id'] != source or picks[identity].get('trade_eligible') != 1:
                raise ValueError('PICK_NOT_OWNED_OR_NOT_TRADE_ELIGIBLE')
            picks[identity]['team_id'], picks[identity]['owner'] = target, teams[target]['team']
        elif action in ('SIGN_NEW', 'REPLACE_CURRENT', 'EXTEND_FUTURE'):
            salaries = move.get('salaries')
            if not isinstance(salaries, list) or not 1 <= len(salaries) <= 6 or any(not money(v) or v == 0 for v in salaries):
                raise ValueError('EXPLICIT_POSITIVE_INTEGER_SALARIES_REQUIRED')
            start = season_start(move['effective_season'])
            if start < season_start(run['base_season']):
                raise ValueError('CONTRACT_BEFORE_BASE_SEASON')
            if action == 'SIGN_NEW':
                if identity in owners or not move.get('name'):
                    raise ValueError('NEW_SIGNING_REQUIRES_DISTINCT_IDENTITY_AND_NAME')
                owners[identity] = target
                name = move['name']
                unknown.append('FREE_AGENCY_AND_NATIVE_SIGNING_ELIGIBILITY_UNVERIFIED')
            else:
                if identity not in owners or owners[identity] != target:
                    raise ValueError('CONTRACT_REPLACEMENT_REQUIRES_CURRENT_OWNER')
                name = original_players[identity]['name']
                if action == 'REPLACE_CURRENT' and start != season_start(run['base_season']):
                    raise ValueError('USE_EXTEND_FUTURE_FOR_FUTURE_REPLACEMENT')
                if action == 'EXTEND_FUTURE':
                    if start <= season_start(run['base_season']):
                        raise ValueError('EXTENSION_MUST_START_IN_FUTURE')
                    unknown.append('FUTURE_REPLACEMENT_IS_EXPLICIT_SCENARIO_NOT_OBSERVED_EXTENSION')
            for season in run['horizon_seasons']:
                index = season_start(season)-start
                if index < 0:
                    continue
                entries = rows[(target, season)]
                entries[:] = [e for e in entries if e['identity'] != identity]
                # Zero beyond the proposed term is a scenario assumption, not certified free agency.
                amount = salaries[index] if index < len(salaries) else 0
                entries.append(dict(identity=identity, name=name, season=season, slot=None,
                    observed_slot_amount=None, amount=amount, basis='SCENARIO', unconditional=False,
                    assumption_ids=[f'PROPOSED_CONTRACT:{proposal["scenario_id"]}:{identity}:{season}'],
                    unknown_reasons=['PROPOSED_NOT_EXECUTED'], conditions=['PROPOSED_CONTRACT'], option_branches=None))
            unknown.append('SIGNING_EXECUTOR_UNVALIDATED')
        else:
            raise ValueError('UNSUPPORTED_MOVE_TYPE')
        assets.append(dict(asset_id=identity, type=action, from_team_id=source, to_team_id=target))
    deltas = []
    for tid in sorted(affected):
        for before in teams[tid]['years']:
            season = before['season']
            entries = rows[(tid, season)]
            subtotal = summarize(entries, basis='SCENARIO')
            total = value(subtotal['value'] if subtotal['coverage'] == 'COMPLETE' else None,
                          'SCENARIO', subtotal['coverage'], subtotal['source_refs'], subtotal['assumption_ids'], subtotal['unknown_reasons'])
            b = before['projected_salary_total']['value']
            a = total['value']
            deltas.append(dict(team_id=tid, team=teams[tid]['team'], season=season,
                before=before['projected_salary_total'], after=total,
                payroll_delta=value(a-b if a is not None and b is not None else None, 'SCENARIO',
                                    'COMPLETE' if a is not None and b is not None else 'NONE'),
                contracts_before=len(before['observed_slot_amounts']), contracts_after=len(entries),
                future_occupancy_status='SCENARIO_NOT_CERTIFIED_ROSTER_SLOTS',
                finance_eligibility=eligibility(run.get('policy'), run['source_binding'], season,
                                                total, tid, run['assumptions'].get('phase', 'UNKNOWN'))))
    if not moves:
        deltas = [dict(team_id=t['team_id'], team=t['team'], season=y['season'],
                       before=y['projected_salary_total'], after=y['projected_salary_total'],
                       payroll_delta=value(0, 'SCENARIO'), contracts_before=len(y['observed_slot_amounts']),
                       contracts_after=len(y['observed_slot_amounts']), finance_eligibility=y['finance_eligibility'])
                  for t in run['teams'] for y in t['years']]
    signing = any(m['type'] in ('SIGN_NEW', 'REPLACE_CURRENT', 'EXTEND_FUTURE') for m in moves)
    return dict(schema_version=1, scenario_id=proposal['scenario_id'], kind=kind, source_run_id=run['run_id'],
        source_binding=run['source_binding'], status='ANALYSIS_ONLY', approval_status='NOT_REQUESTED',
        assumptions=proposal.get('assumptions', []), moves=deepcopy(moves), team_year_deltas=deltas,
        assets_before_after=assets, picks_after=list(picks.values()),
        rationale=proposal.get('rationale', ''), opportunity_cost=proposal.get('opportunity_cost', []),
        coaching_cards=proposal.get('coaching_cards', []),
        finance_eligibility='SEE_TEAM_YEAR_RESULTS',
        executor_readiness='BLOCKED_EXECUTOR' if signing else ('SEPARATE_PLAYER_APPROVAL_REQUIRED' if moves or kind == 'INTERNAL_COACHING' else 'NO_ACTION'),
        unknown_reasons=sorted(set(unknown)), total_non_salary_cost='UNKNOWN',
        alternatives=[dict(kind='KEEP', salary_change=0, explanation='Retain current contracts and assets'),
                      dict(kind='INTERNAL_COACHING', salary_change=0, explanation='Compare role/system optimization; no fixed win uplift'),
                      dict(kind='TRADE_OR_SIGNING', candidate_status='PRESENT' if moves else 'NO_CANDIDATE',
                           explanation='Assess talent gap, future commitments and asset opportunity cost')])
