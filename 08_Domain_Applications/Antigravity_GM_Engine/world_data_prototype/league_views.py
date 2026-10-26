"""One-capture league comparisons; no official seeds or eligibility inferred."""
from collections import Counter
from contextlib import closing
from fractions import Fraction
from competition_views import connect,COUNT_FIELDS

COUNT_METRICS=COUNT_FIELDS+('total_rebounds','games_played','games_started','double_doubles','triple_doubles')
SHOOTING={'field_goal_fraction':('fg_made','fg_attempted'),'three_point_fraction':('three_made','three_attempted'),'free_throw_fraction':('ft_made','ft_attempted')}
PLAYER_METRICS=COUNT_METRICS+tuple(n+'_per_game' for n in COUNT_FIELDS+('total_rebounds',))+tuple(SHOOTING)


def _page_args(unit_id,offset,limit):
    if type(offset) is not int or offset<0:raise ValueError('offset must be a nonnegative integer')
    if type(limit) is not int or not 1<=limit<=100:raise ValueError('limit must be 1..100')
    if offset and not unit_id:raise ValueError('continued pages require explicit unit_id')


def _cohort(conn,table,season_id,phase_code,unit_id):
    # Choose one capture before scope/eligibility filtering. Missing fields or
    # subjects in that capture must never be filled from an older capture.
    if table not in ('player_season_totals','team_season_totals'):raise ValueError('invalid totals table')
    clauses=['a.season_id=?','a.phase_code IS ?',"u.unit_status='success'"];args=[season_id,phase_code]
    if unit_id is not None:clauses.append('u.unit_id=?');args.append(unit_id)
    unit=conn.execute('''SELECT DISTINCT u.unit_id,u.observed_at,u.effective_at,u.source_key,u.completeness,u.layout_version,r.source_grade
        FROM '''+table+''' a JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)
        WHERE '''+' AND '.join(clauses)+''' ORDER BY competition_utc(u.observed_at) DESC,u.unit_id DESC LIMIT 1''',args).fetchone()
    if unit is None:return None,[]
    key,identity=('player_id','players') if table=='player_season_totals' else ('team_id','teams')
    rows=[dict(r) for r in conn.execute('SELECT a.*,e.display_name FROM '+table+' a JOIN '+identity+' e USING('+key+') WHERE a.unit_id=? AND a.season_id=? AND a.phase_code IS ? ORDER BY a.'+key,(unit['unit_id'],season_id,phase_code))]
    return dict(unit),rows


def _rank_page(entries,key,*,offset,limit,ascending=False):
    entries.sort(key=lambda e:((e[0] if ascending else -e[0]),e[1][key]))
    result=[];previous=None;rank=0
    for position,(value,row) in enumerate(entries,1):
        if previous is None or value!=previous:rank=position
        previous=value
        if offset<=position-1<offset+limit:
            result.append({'rank':rank,'display_position':position,'value':float(value),'value_exact':{'numerator':value.numerator,'denominator':value.denominator},'totals':row})
    return result,offset+limit if offset+limit<len(entries) else None


def _base(season_id,phase_code,unit,unit_id):
    return {'season_id':season_id,'phase_code':phase_code,'phase_selection':'EXACT_NULL_PHASE' if phase_code is None else 'EXACT_OBSERVED_PHASE_CODE',
        'status':'SINGLE_OBSERVATION_UNIT' if unit else ('UNIT_NOT_OBSERVED_FOR_COHORT' if unit_id is not None else 'NO_TOTALS_OBSERVED'),
        'selected_unit_id':unit['unit_id'] if unit else unit_id,'capture':unit,
        'scope':'Captured cohort only; no missing subjects/fields borrowed from other units, inferred phase/finality, team-stint sum or historical identity proof',
        'tie_policy':'Competition rank by exact rational value; stable canonical ID display order within ties; ties may cross pages',
        'official_rules':'Official standings, conference seeds, tiebreaks, leaderboard eligibility and UI rounding NOT_ESTABLISHED',
        'display_name_scope':'Canonical identity label; not an observed historical name in this totals row'}


def league_standings(path,season_id,*,phase_code=None,unit_id=None,offset=0,limit=30):
    _page_args(unit_id,offset,limit)
    with closing(connect(path,True)) as conn:unit,rows=_cohort(conn,'team_season_totals',season_id,phase_code,unit_id)
    entries=[];excluded=Counter()
    for row in rows:
        wins,losses=row['wins'],row['losses']
        if type(wins) is not int or type(losses) is not int:excluded['MISSING_WIN_LOSS']+=1
        elif wins<0 or losses<0:excluded['NEGATIVE_WIN_LOSS']+=1
        elif wins+losses==0:excluded['ZERO_GAMES_UNDEFINED']+=1
        else:entries.append((Fraction(wins,wins+losses),row))
    records,next_offset=_rank_page(entries,'team_id',offset=offset,limit=limit)
    return {**_base(season_id,phase_code,unit,unit_id),'metric':'wins_divided_by_wins_plus_losses','records':records,
        'coverage':{'captured_rows':len(rows),'ranked_rows':len(entries),'excluded_by_reason':dict(excluded)},'offset':offset,'next_offset':next_offset}


def _metric(row,metric,min_games,min_attempts):
    games=row['games_played']
    if type(games) is not int or games<0:return None,'MISSING_OR_INVALID_GAMES'
    if games<min_games:return None,'BELOW_REQUESTED_MIN_GAMES'
    if metric in SHOOTING:
        made,attempted=(row[n] for n in SHOOTING[metric])
        if made is None or attempted is None:return None,'MISSING_METRIC'
        if made<0 or attempted<0 or made>attempted:return None,'INCONSISTENT_SHOOTING_COUNTS'
        if attempted==0:return None,'ZERO_ATTEMPTS_UNDEFINED'
        if attempted<min_attempts:return None,'BELOW_REQUESTED_MIN_ATTEMPTS'
        return Fraction(made,attempted),None
    per_game=metric.endswith('_per_game');name=metric.removesuffix('_per_game') if per_game else metric
    if name=='total_rebounds':
        parts=[row['offensive_rebounds'],row['defensive_rebounds']]
        value=sum(parts) if all(type(v) is int and v>=0 for v in parts) else None
    else:value=row[name]
    if type(value) is not int or value<0:return None,'MISSING_OR_INVALID_METRIC'
    if per_game and games==0:return None,'ZERO_GAMES_UNDEFINED'
    return Fraction(value,games if per_game else 1),None


def player_leaderboard(path,season_id,*,metric='points_per_game',phase_code=None,team_scope=None,null_team_scope=False,team_id=None,min_games=1,min_attempts=0,ascending=False,unit_id=None,offset=0,limit=20):
    _page_args(unit_id,offset,limit)
    if metric not in PLAYER_METRICS:raise ValueError('unsupported player leaderboard metric')
    if type(min_games) is not int or min_games<0:raise ValueError('min_games must be a nonnegative integer')
    if type(min_attempts) is not int or min_attempts<0:raise ValueError('min_attempts must be a nonnegative integer')
    if min_attempts and metric not in SHOOTING:raise ValueError('min_attempts applies only to shooting fractions')
    if type(ascending) is not bool:raise ValueError('ascending must be boolean')
    if type(null_team_scope) is not bool or (null_team_scope and team_scope is not None):raise ValueError('null_team_scope is boolean and mutually exclusive with team_scope')
    with closing(connect(path,True)) as conn:unit,rows=_cohort(conn,'player_season_totals',season_id,phase_code,unit_id)
    captured=len(rows);scopes=sorted({r['team_scope'] for r in rows},key=lambda v:(v is not None,str(v)))
    if null_team_scope:selected_scope=None
    elif team_scope is None:
        if len(scopes)>1:raise ValueError('multiple team_scope values in selected unit; select an exact team_scope')
        selected_scope=scopes[0] if scopes else None
    else:selected_scope=team_scope
    rows=[r for r in rows if r['team_scope']==selected_scope and (team_id is None or r['team_id']==team_id)]
    entries=[];excluded=Counter()
    for row in rows:
        value,reason=_metric(row,metric,min_games,min_attempts)
        if reason:excluded[reason]+=1
        else:entries.append((value,row))
    records,next_offset=_rank_page(entries,'player_id',offset=offset,limit=limit,ascending=ascending)
    return {**_base(season_id,phase_code,unit,unit_id),'metric':metric,'ascending':ascending,'team_scope':selected_scope,'available_team_scopes':scopes,'team_id_filter':team_id,
        'eligibility':{'min_games':min_games,'min_attempts':min_attempts,'basis':'USER_REQUESTED_THRESHOLDS_ONLY; no official qualification asserted'},
        'records':records,'coverage':{'captured_rows':captured,'scope_filtered_rows':len(rows),'ranked_rows':len(entries),'excluded_by_reason':dict(excluded)},'offset':offset,'next_offset':next_offset,
        'team_filter_scope':'Literal team_id on this totals row only; no current roster join or inferred team split'}
