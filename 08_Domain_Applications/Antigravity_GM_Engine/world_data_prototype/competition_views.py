"""Single-unit Game Boxes and source-qualified season totals/rates."""
from contextlib import closing
from collections import defaultdict,Counter
from observation_scope import query_connection,utc_stamp
from schema_model import ident

BOX_TABLES=('game_state_observations','game_period_scores','player_game_boxes','team_game_boxes','native_box_observations')
COUNT_FIELDS=('points','fg_made','fg_attempted','three_made','three_attempted','ft_made','ft_attempted','offensive_rebounds','defensive_rebounds','assists','steals','blocks','turnovers','fouls')

def connect(path,readonly):
    conn=query_connection(path,readonly)
    conn.create_function('competition_utc',1,utc_stamp,deterministic=True)
    return conn

def game_box_snapshot(path,game_id,*,unit_id=None):
    with closing(connect(path,True)) as conn:
        game=conn.execute('SELECT * FROM games WHERE game_id=?',(game_id,)).fetchone()
        if game is None:return {'game_id':game_id,'status':'NOT_OBSERVED'}
        terms=['SELECT unit_id FROM '+ident(table)+' WHERE game_id=?' for table in BOX_TABLES]
        units=[dict(r) for r in conn.execute('''SELECT u.unit_id,u.observed_at,u.effective_at,u.completeness,u.source_key,r.source_grade,u.layout_version
            FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.unit_status='success' AND u.unit_id IN ('''+ ' UNION '.join(terms)+') ORDER BY competition_utc(u.observed_at) DESC,u.unit_id DESC',[game_id]*len(terms))]
        selected=next((u for u in units if u['unit_id']==unit_id),None) if unit_id is not None else (units[0] if units else None)
        if selected is None:return {'game':dict(game),'status':'UNIT_NOT_OBSERVED_FOR_GAME' if unit_id else 'NO_GAME_OBSERVATIONS','selected_unit_id':unit_id,'observation_units':units,'states':[],'period_scores':[],'player_boxes':[],'team_boxes':[]}
        unit=selected['unit_id'];rows={}
        for key,table,order in [('states','game_state_observations','a.observation_id'),('period_scores','game_period_scores','a.team_id,a.period_index'),('player_boxes','player_game_boxes','a.team_id,a.player_id'),('team_boxes','team_game_boxes','a.team_id')]:
            rows[key]=[dict(r) for r in conn.execute('SELECT a.*,u.observed_at,u.effective_at,u.completeness,r.source_grade FROM '+ident(table)+''' a JOIN capture_units u USING(unit_id)
                JOIN capture_runs r USING(run_id) WHERE a.game_id=? AND a.unit_id=? ORDER BY '''+order,(game_id,unit))]
        native=[dict(r) for r in conn.execute('''SELECT side,count(*) AS captured_rows,sum(in_use) AS active_rows,
            sum(CASE WHEN in_use=1 THEN points END) AS captured_active_points,
            sum(CASE WHEN in_use=1 AND points IS NULL THEN 1 ELSE 0 END) AS active_rows_without_points,
            min(CASE WHEN in_use=1 THEN native_team_id END) AS min_team_id,max(CASE WHEN in_use=1 THEN native_team_id END) AS max_team_id
            FROM native_box_observations WHERE game_id=? AND unit_id=? GROUP BY side''',(game_id,unit))]
        native={r['side']:r for r in native};coverage={};derived={};native_points={}
        for side in ('HOME','AWAY'):
            team=game['home_team_id' if side=='HOME' else 'away_team_id'];observed=native.get(side);canonical=[r for r in rows['player_boxes'] if r['team_id']==team and r['in_use']!=0]
            points=None if not canonical or any(r['points'] is None for r in canonical) else sum(r['points'] for r in canonical)
            team_row=conn.execute('SELECT native_team_id FROM teams WHERE team_id=?',(team,)).fetchone();native_team=team_row['native_team_id'] if team_row else None
            team_match=bool(observed and native_team is not None and str(observed['min_team_id'])==str(native_team)==str(observed['max_team_id']))
            all_active_known=all(r['in_use']==1 for r in canonical)
            native_rows=conn.execute('SELECT native_player_id,points,identity_status FROM native_box_observations WHERE game_id=? AND unit_id=? AND side=? AND in_use=1',(game_id,unit,side)).fetchall()
            canonical_ids=[conn.execute('SELECT native_player_id FROM players WHERE player_id=?',(r['player_id'],)).fetchone() for r in canonical]
            canonical_pairs=[(str(p['native_player_id']),r['points']) for p,r in zip(canonical_ids,canonical) if p and p['native_player_id'] is not None]
            native_pairs=[(str(r['native_player_id']),r['points']) for r in native_rows]
            identities_match=bool(native_pairs and len({p[0] for p in native_pairs})==len(native_pairs) and len(canonical_pairs)==len(canonical) and Counter(canonical_pairs)==Counter(native_pairs) and all(r['identity_status']=='CURRENT_CONTEXT_RESOLVED' for r in native_rows))
            full=bool(observed and observed['active_rows']>0 and len(canonical)==observed['active_rows'] and team_match and all_active_known and identities_match and points is not None and observed['active_rows_without_points']==0 and points==observed['captured_active_points'])
            status='ALL_CAPTURED_NATIVE_PARTICIPANTS_RESOLVED' if full else ('NO_CAPTURED_NATIVE_WINDOW' if observed is None else 'PARTIAL_OR_MISMATCHED_CAPTURED_NATIVE_COVERAGE')
            coverage[side]={'team_id':team,'canonical_active_rows':len(canonical),'canonical_captured_points':points,'native_captured_rows':observed['captured_rows'] if observed else None,
                'native_active_rows':observed['active_rows'] if observed else None,'native_team_id_matches':team_match if observed else None,'native_player_ids_and_points_match':identities_match if observed else None,'status':status,
                'scope':'Coverage of this captured Native window; not historical player lifecycle or UI acceptance'}
            derived[side]=points if full else None;native_points[side]=observed['captured_active_points'] if observed and observed['active_rows'] and observed['active_rows_without_points']==0 else None
        state=rows['states'][0] if rows['states'] else None;observed_points={side:state['home_points' if side=='HOME' else 'away_points'] if state else None for side in ('HOME','AWAY')}
        if any(value is not None for value in observed_points.values()):primary=observed_points;score_kind='LITERAL_GAME_STATE_SCORE_FIELDS' if all(v is not None for v in observed_points.values()) else 'PARTIAL_GAME_STATE_SCORE_FIELDS'
        elif all(value is not None for value in derived.values()):primary=derived;score_kind='DERIVED_CANONICAL_BOX_SUM_MATCHING_CAPTURED_NATIVE_WINDOW'
        else:primary={'HOME':None,'AWAY':None};score_kind='NO_COMPLETE_QUALIFIED_SCORE'
        return {'game':dict(game),'status':'SINGLE_OBSERVATION_UNIT','capture':selected,'selected_unit_id':unit,'observation_units':units,**rows,'coverage':coverage,
            'scores':{'home_points':primary['HOME'],'away_points':primary['AWAY'],'value_status':score_kind,'state_points':observed_points,
                'derived_canonical_points':derived,'captured_native_points':native_points,'state_score_fields_present':bool(state and all(v is not None for v in observed_points.values())),
                'state_score_provenance':state['score_provenance'] if state else None,'captured_native_scope':'Sum of in-use rows in this unit, not a substitute for qualified canonical participants'},
            'history':'All earlier states/Boxes remain in history/history-page; select an observation unit to inspect another capture'}

def _latest_totals(conn,table,*,season_id=None,entity_id=None,phase_code=None):
    if table not in ('player_season_totals','team_season_totals'):raise PermissionError('unsupported totals family')
    player=table=='player_season_totals';key='player_id' if player else 'team_id';identity='players' if player else 'teams';clauses=["u.unit_status='success'"];args=[]
    if season_id is not None:clauses.append('a.season_id=?');args.append(season_id)
    if entity_id is not None:clauses.append('a.'+key+'=?');args.append(entity_id)
    if phase_code is not None:clauses.append('a.phase_code=?');args.append(phase_code)
    partition='a.'+key+',a.season_id,a.phase_code'+(',a.team_scope,a.team_id' if player else '')
    sql='''WITH ranked AS (SELECT a.*,u.observed_at,u.effective_at,u.completeness,r.source_grade,
        row_number() OVER(PARTITION BY '''+partition+''' ORDER BY competition_utc(u.observed_at) DESC,u.unit_id DESC) AS recency
        FROM '''+ident(table)+''' a JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE '''+' AND '.join(clauses)+''')
        SELECT a.*,e.display_name,s.season_code FROM ranked a JOIN '''+identity+' e ON e.'+key+'=a.'+key+''' JOIN seasons s USING(season_id) WHERE recency=1
        ORDER BY s.season_code DESC,a.season_id,a.'''+key+',a.phase_code'+(',a.team_scope,a.team_id' if player else '')
    values=[dict(r) for r in conn.execute(sql,args)]
    for value in values:value.pop('recency')
    return values

def _rates(row,*,player):
    if player:games=row['games_played'];basis='OBSERVED_SAME_ROW_GAMES_PLAYED'
    else:games=row['wins']+row['losses'] if row['wins'] is not None and row['losses'] is not None else None;basis='DERIVED_SAME_ROW_WINS_PLUS_LOSSES'
    denominator_valid=type(games) is int and games>0 and (player or (row['wins']>=0 and row['losses']>=0))
    per_game={name:row[name]/games if denominator_valid and row[name] is not None else None for name in COUNT_FIELDS}
    rebounds=row['offensive_rebounds']+row['defensive_rebounds'] if row['offensive_rebounds'] is not None and row['defensive_rebounds'] is not None else None
    per_game['total_rebounds']=rebounds/games if denominator_valid and rebounds is not None else None
    shooting={}
    for label,made,attempted in [('field_goal_fraction','fg_made','fg_attempted'),('three_point_fraction','three_made','three_attempted'),('free_throw_fraction','ft_made','ft_attempted')]:
        m,a=row[made],row[attempted]
        if m is None or a is None:value=None;status='NOT_OBSERVED_IN_SAME_ROW'
        elif m<0 or a<0 or m>a:value=None;status='INCONSISTENT_OBSERVED_COUNTS'
        elif a==0:value=None;status='ZERO_ATTEMPTS_UNDEFINED'
        else:value=m/a;status='DERIVED_MADE_DIVIDED_BY_ATTEMPTED'
        shooting[label]={'value':value,'status':status,'scale':'fraction 0..1; no UI rounding asserted'}
    return {'games_denominator':games,'denominator_basis':basis,'denominator_status':'POSITIVE_SAME_ROW_DENOMINATOR' if denominator_valid else 'MISSING_ZERO_OR_INCONSISTENT_DENOMINATOR','per_game_counts':per_game,'shooting_fractions':shooting,
        'provenance':'DERIVED_FROM_ONE_OBSERVED_TOTALS_ROW; no cross-unit field carry','minutes_conversion':'WITHHELD_RAW_NATIVE_TIME_UNIT_NOT_PROMOTED'}

def player_seasons(path,player_id,*,season_id=None,phase_code=None,limit=100):
    if type(limit) is not int or not 1<=limit<=10000:raise ValueError('season observation limit must be 1..10000')
    with closing(connect(path,True)) as conn:
        person=conn.execute('SELECT * FROM players WHERE player_id=?',(player_id,)).fetchone()
        if person is None:return {'player_id':player_id,'status':'NOT_OBSERVED','records':[]}
        rows=_latest_totals(conn,'player_season_totals',season_id=season_id,entity_id=player_id,phase_code=phase_code)
    if len(rows)>limit:raise ValueError('season observations exceed explicit cap; no truncation')
    return {'player':dict(person),'records':[{'totals':row,'derived':_rates(row,player=True)} for row in rows],
        'scope':'Latest row per exact season/phase/team_scope/team_id; no name-based lifecycle links, period-label merging or inferred career sum'}

def season_summary(path,season_id,*,phase_code=None,limit=1000):
    if type(limit) is not int or not 1<=limit<=10000:raise ValueError('season summary limit must be 1..10000')
    with closing(connect(path,True)) as conn:
        season=conn.execute('SELECT * FROM seasons WHERE season_id=?',(season_id,)).fetchone()
        if season is None:return {'season_id':season_id,'status':'NOT_OBSERVED','teams':[],'players':[]}
        teams=_latest_totals(conn,'team_season_totals',season_id=season_id,phase_code=phase_code);players=_latest_totals(conn,'player_season_totals',season_id=season_id,phase_code=phase_code)
    if len(teams)+len(players)>limit:raise ValueError('season summary exceeds explicit cap; no truncation')
    team_results=[];groups=defaultdict(list)
    for row in teams:
        derived=_rates(row,player=False);games=derived['games_denominator'];win_pct=row['wins']/games if games and games>0 and row['wins'] is not None and row['wins']>=0 and row['losses']>=0 else None
        result={'totals':row,'derived':derived,'derived_win_fraction':win_pct};team_results.append(result);groups[row['phase_code']].append(result)
    standings=[]
    for phase,values in sorted(groups.items(),key=lambda item:(item[0] is not None,str(item[0]))):
        ordered=sorted(values,key=lambda item:(item['derived_win_fraction'] is None,-(item['derived_win_fraction'] or 0),item['totals']['team_id']))
        standings.append({'phase_code':phase,'ordered_team_ids':[v['totals']['team_id'] for v in ordered],'basis':'DERIVED_WIN_FRACTION_WITHIN_EXACT_PHASE; stable team-ID display order for ties','official_conference_seeds_and_tiebreaks':'NOT_INFERRED'})
    return {'season':dict(season),'status':'OBSERVED_TOTALS' if teams or players else 'NO_TOTALS_OBSERVED','teams':team_results,
        'players':[{'totals':row,'derived':_rates(row,player=True)} for row in players],'win_fraction_orderings':standings,
        'scope':'Phase/scope/finality remain as observed; no regular-season label, team-stint sum, season closure or UI rounding inferred'}
