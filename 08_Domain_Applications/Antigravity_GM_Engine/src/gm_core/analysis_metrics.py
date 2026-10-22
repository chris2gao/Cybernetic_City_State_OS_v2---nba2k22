"""Explicit counting-stat formulas. No possessions, ratings or player valuation."""
from collections import Counter

VERSION = 'GM_METRICS_V1'
COUNTERS = ('w', 'l', 'made', 'attempted', '3pt_made', '3pt_attempted',
            'free_throws_attempted', 'turnover', 'assists', 'points', 'pa',
            'offensive_rebounds', 'defensive_rebounds')


def metrics(totals, source_ref, scope='CUMULATIVE'):
    t = {k: totals.get(k) for k in COUNTERS}
    result = {}

    def calc(name, fields, numerator, denominator=None, heuristic=False):
        vals = {k: t[k] for k in fields}
        reason, value, den = None, None, None
        if any(type(v) not in (int, float) or v < 0 for v in vals.values()):
            reason = 'MISSING_OR_NEGATIVE_COUNTER'
        else:
            num = numerator(t)
            den = denominator(t) if denominator else None
            if den is not None and den <= 0:
                reason = 'ZERO_OR_INVALID_DENOMINATOR'
            elif num < 0 or (name == 'two_point_pct' and num > den):
                reason = 'INCONSISTENT_COUNTERS'
            else:
                value = num/den if denominator else num
        result[name] = dict(metric_id=name, value=value,
            basis='UNKNOWN' if reason else ('HEURISTIC' if heuristic else 'CALCULATED'),
            scope=scope, unit='count' if name == 'games' else ('fraction' if name in ('efg', 'three_point_attempt_rate', 'two_point_pct', 'three_point_pct', 'free_throw_rate', 'estimated_turnover_rate') else 'ratio'),
            formula_version=VERSION, input_refs=[source_ref+':'+k for k in fields],
            sample=dict(inputs=vals, denominator=den), unknown_reason=reason)

    games = lambda x: x['w']+x['l']
    calc('games', ('w','l'), games)
    calc('efg', ('made','3pt_made','attempted'), lambda x:x['made']+0.5*x['3pt_made'], lambda x:x['attempted'])
    calc('three_point_attempt_rate', ('3pt_attempted','attempted'), lambda x:x['3pt_attempted'], lambda x:x['attempted'])
    calc('two_point_pct', ('made','3pt_made','attempted','3pt_attempted'), lambda x:x['made']-x['3pt_made'], lambda x:x['attempted']-x['3pt_attempted'])
    calc('three_point_pct', ('3pt_made','3pt_attempted'), lambda x:x['3pt_made'], lambda x:x['3pt_attempted'])
    calc('free_throw_rate', ('free_throws_attempted','attempted'), lambda x:x['free_throws_attempted'], lambda x:x['attempted'])
    calc('estimated_turnover_rate', ('turnover','attempted','free_throws_attempted'), lambda x:x['turnover'], lambda x:x['attempted']+0.44*x['free_throws_attempted']+x['turnover'], True)
    calc('assist_turnover_ratio', ('assists','turnover'), lambda x:x['assists'], lambda x:x['turnover'])
    for name, key in (('points_per_game','points'), ('allowed_points_per_game','pa'), ('offensive_rebounds_per_game','offensive_rebounds'), ('defensive_rebounds_per_game','defensive_rebounds')):
        calc(name, (key,'w','l'), lambda x,k=key:x[k], games)
    calc('margin_per_game', ('points','pa','w','l'), lambda x:x['points']-x['pa'], games)
    # A negative scoring margin is meaningful, unlike a negative counter.
    if all(type(t[k]) in (int,float) and t[k] >= 0 for k in ('points','pa','w','l')) and games(t)>0:
        result['margin_per_game'].update(value=(t['points']-t['pa'])/games(t), basis='CALCULATED', unknown_reason=None)
    for name in ('possessions', 'offensive_rating', 'defensive_rating', 'net_rating', 'standard_rebound_pct'):
        result[name] = dict(metric_id=name, value=None, basis='UNKNOWN', scope=scope,
            unit=None, formula_version=VERSION, input_refs=[], sample={}, unknown_reason='SEMANTICS_NOT_CERTIFIED')
    return result


def interval(current, previous, comparable):
    if not comparable:
        return dict(status='NOT_COMPARABLE', counters={}, metrics={})
    delta = {k: current[k]-previous[k] if type(current.get(k)) in (int,float) and type(previous.get(k)) in (int,float) else None for k in COUNTERS}
    m = metrics(delta, 'interval', 'INTERVAL')
    g = m['games']['value']
    return dict(status='NO_NEW_GAMES' if g == 0 else ('COUNTER_RESET_REVIEW' if any(v is not None and v<0 for v in delta.values()) else 'COMPARABLE'), counters=delta, metrics=m)


def temporal_links(current, previous):
    """Multi-field uniqueness is a candidate only. Batch slots are never stable IDs."""
    def key(p):
        return tuple(p.get(k) for k in ('name', 'face_id', 'birth_date'))
    counts = Counter(key(p) for p in previous)
    current_counts = Counter(key(p) for p in current)
    result = []
    for p in current:
        matches = [old for old in previous if key(old) == key(p)]
        unique = all(v is not None for v in key(p)) and counts[key(p)] == current_counts[key(p)] == 1
        changes={}
        if unique:
            old=matches[0]
            for group in ('attributes','contract','season_totals'):
                before=old.get(group) or {}; after=p.get(group) or {}
                diffs=[]
                for field in sorted(set(before)|set(after)):
                    if group=='attributes' and field.casefold() in ('potential','intangibles'):
                        continue
                    a=before.get(field);b=after.get(field)
                    a=a.get('value') if isinstance(a,dict) else a
                    b=b.get('value') if isinstance(b,dict) else b
                    if a!=b:
                        diffs.append(dict(field=field,before=a,after=b,delta=b-a if type(a) in (int,float) and type(b) in (int,float) else None))
                changes[group]=diffs
            changes['team_changed']=old.get('team_id')!=p.get('team_id')
        result.append(dict(identity=p['identity'], status='TEMPORAL_CANDIDATE' if unique else ('AMBIGUOUS' if matches else 'UNMATCHED'),
            previous_identities=[old['identity'] for old in matches], verified_growth=False,
            provisional_changes=changes, attribution='PLAYER_CUMULATIVE_NOT_NEW_TEAM_CONTRIBUTION'))
    return result
