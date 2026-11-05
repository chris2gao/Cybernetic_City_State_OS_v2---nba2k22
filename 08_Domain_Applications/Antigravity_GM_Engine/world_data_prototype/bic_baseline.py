"""Offline BIC views over the existing WorldData observation ledger."""
from contextlib import closing
from datetime import datetime
import math

import query
from engine import connect
from observation_scope import observed_as_of, query_connection, utc_stamp


def knowledge_status(source_grade=None, *, observed=False):
    """Source grade is a provenance claim, never independent acceptance."""
    if not observed:
        return 'UNKNOWN'
    return {
        'SYNTHETIC_FIXTURE': 'SYNTHETIC_ONLY',
        'RESEARCH_FIXTURE': 'RESEARCH_REFERENCE',
        'VERIFIED_OBSERVED_SAME_BATCH': 'HISTORICAL_OBSERVATION',
    }.get(source_grade, 'UNVERIFIED_OBSERVATION')


def _decorate(value, units, cutoff, max_age_seconds):
    if isinstance(value, list):
        return [_decorate(item, units, cutoff, max_age_seconds) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: _decorate(item, units, cutoff, max_age_seconds)
              for key, item in value.items()}
    unit = units.get(value.get('unit_id'))
    if unit:
        age = (cutoff - datetime.fromisoformat(utc_stamp(unit['observed_at']))).total_seconds()
        result['provenance'] = unit
        result['knowledge_status'] = knowledge_status(unit['source_grade'], observed=True)
        result['freshness'] = {'age_seconds': age, 'max_age_seconds': max_age_seconds,
                               'status': 'STALE' if age > max_age_seconds else 'WITHIN_REQUESTED_AGE'}
        result['applicability'] = {'season_id': unit['season_id'],
                                    'game_mode': 'UNKNOWN',
                                    'reason': 'League mode does not certify per-game Fast Sim or 3D'}
    elif value.get('status') == 'NOT_OBSERVED':
        result['knowledge_status'] = 'UNKNOWN'
    return result


def _baseline(database, entity_id, *, kind, save_id, season_id, as_of, max_age_seconds, expected_native_identity=None):
    if not isinstance(max_age_seconds, (int, float)) or isinstance(max_age_seconds, bool) or not math.isfinite(max_age_seconds) or max_age_seconds < 0:
        raise ValueError('max_age_seconds must be finite and nonnegative')
    if not save_id or not season_id:
        raise ValueError('Explicit save_id and season_id required')
    cutoff = datetime.fromisoformat(utc_stamp(as_of))
    with closing(connect(database, True)) as conn:
        header = dict(conn.execute('SELECT * FROM saves WHERE singleton=1').fetchone())
        if header['save_id'] != save_id:
            raise ValueError('SAVE_ID_MISMATCH')
        season = conn.execute('SELECT save_id FROM seasons WHERE season_id=?', (season_id,)).fetchone()
        if season is None or season['save_id'] not in (None, save_id):
            raise ValueError('SEASON_ID_MISMATCH')
    with observed_as_of(database, as_of, season_id=season_id) as scope:
        with closing(query_connection(database, True)) as conn:
            units = {row['unit_id']: {**dict(row), 'save_id': save_id} for row in conn.execute(
                'SELECT u.unit_id,u.observed_at,u.effective_at,u.source_key,u.completeness,'
                'u.layout_version,r.run_id,r.season_id,r.source_grade,r.game_date,r.save_binding_ref '
                'FROM capture_units u JOIN capture_runs r USING(run_id)')}
            modes = [dict(row) for row in conn.execute(
                'SELECT unit_id,season_id,mode_label,league_label,period_label,today_native_iso_date '
                'FROM game_mode_observations')]
            roster = [dict(row) for row in conn.execute(
                'SELECT * FROM roster_memberships WHERE '+('player_id' if kind == 'player' else 'team_id')+'=?', (entity_id,))]
            native_identity = []
            if kind == 'player':
                native_identity = [dict(row) for row in conn.execute(
                    'SELECT p.* FROM native_player_sources p JOIN capture_units u USING(unit_id) '
                    'WHERE p.player_id=? ORDER BY u.observed_at,p.unit_id', (entity_id,))]
                for key in ('native_unique_id_raw', 'preserved_id_raw'):
                    values = {row[key] for row in native_identity if row[key] is not None}
                    if len(values) > 1:
                        raise ValueError('NATIVE_IDENTITY_CONFLICT: ' + key)
                if expected_native_identity is not None:
                    if set(expected_native_identity) != {'native_unique_id_raw', 'preserved_id_raw'}:
                        raise ValueError('Both Native identity components required')
                    if not native_identity or any(row[key] != value for row in native_identity for key, value in expected_native_identity.items()):
                        raise ValueError('NATIVE_IDENTITY_MISMATCH')
        card = (query.player_card if kind == 'player' else query.team_card)(database, entity_id)
        return {'entity_kind': kind, 'entity_id': entity_id, 'save_id': save_id,
                'season_id': season_id, 'observation_scope': scope.metadata(),
                'binding': {**header, 'season_save_id': season['save_id'],
                            'season_binding_status': 'EXPLICIT' if season['save_id'] else 'DATABASE_LOCAL_ONLY'},
                'game_mode': 'UNKNOWN', 'league_mode_observations': modes,
                'data_status': 'REAL_DATA_NOT_VERIFIED',
                'facts': _decorate(card, units, cutoff, max_age_seconds),
                'native_identity_history': _decorate(native_identity, units, cutoff, max_age_seconds),
                'roster_history': _decorate(roster, units, cutoff, max_age_seconds),
                'limitations': ['Per-field observation units may differ',
                               'Database header and Native identity require independent source validation',
                               'WITHHELD fields remain subject to the existing public query boundary']}


def player_baseline(database, player_id, *, save_id, season_id, as_of, max_age_seconds=86400, expected_native_identity=None):
    return _baseline(database, player_id, kind='player', save_id=save_id,
                     season_id=season_id, as_of=as_of, max_age_seconds=max_age_seconds,
                     expected_native_identity=expected_native_identity)


def team_baseline(database, team_id, *, save_id, season_id, as_of, max_age_seconds=86400):
    return _baseline(database, team_id, kind='team', save_id=save_id,
                     season_id=season_id, as_of=as_of, max_age_seconds=max_age_seconds)


def coverage_report(baseline):
    counts = {'NOT_OBSERVED': 0, 'STALE': 0, 'WITHIN_REQUESTED_AGE': 0}
    units = set()
    def visit(value):
        if isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            if value.get('status') == 'NOT_OBSERVED':
                counts['NOT_OBSERVED'] += 1
            if 'freshness' in value:
                counts[value['freshness']['status']] += 1
                units.add(value['provenance']['unit_id'])
            for key, item in value.items():
                if key not in ('provenance', 'freshness', 'applicability'):
                    visit(item)
    visit(baseline['facts'])
    return {'counts': counts, 'observation_units': sorted(units),
            'single_observation_unit': len(units) == 1, 'game_mode': baseline['game_mode'],
            'data_status': baseline['data_status'], 'restricted_fields': 'WITHHELD',
            'save_id': baseline['save_id'], 'season_id': baseline['season_id']}


def badge_intelligence(baseline):
    if baseline['entity_kind'] != 'player':
        raise ValueError('Badge intelligence requires a player baseline')
    observations = baseline['facts'].get('families', {}).get('player_badge_values', [])
    rows = []
    for observation in observations:
        owned = observation.get('owned_state', 'unknown')
        rows.append({'badge_key': observation.get('badge_key'), 'observation': observation,
                     'capability_state': 'OWNED' if owned == 'owned' else 'UNKNOWN',
                     'ownership': owned, 'eligibility': 'UNKNOWN', 'qualification_source': None,
                     'xp': 'UNKNOWN', 'natural_growth': 'UNKNOWN', 'game_effect': 'UNKNOWN'})
    return {'player_id': baseline['entity_id'], 'save_id': baseline['save_id'],
            'season_id': baseline['season_id'], 'badges': rows,
            'status': 'OBSERVATIONS_AVAILABLE' if rows else 'NOT_OBSERVED',
            'limits': ['Absence does not imply eligibility',
                       'MyPLAYER research thresholds do not establish MyLEAGUE rules',
                       'Base ownership does not certify effective animation or success-rate effects']}
