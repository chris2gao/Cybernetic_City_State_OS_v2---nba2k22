"""Bounded role-safe queries. Give roles these results, never the owner DB file.

SQLite file ownership is not a per-column ACL. GM exports exclude evidence paths,
raw materials, restricted metadata, owner transaction/control and native news.
"""
from contextlib import closing
import json
from pathlib import Path
from engine import connect
from schema_model import TABLES, ident
from family_codec import registered_rating_candidate,PROFILE

RATING_COLUMNS={('three_point_shot' if d['name']=='3pt_shot' else d['name'])+'_raw'
                for d in PROFILE['fields']['PLAYER'] if d.get('conversion')=='rating' and d['name']!='potential'}

PUBLIC_TABLES=frozenset(name for name,t in TABLES.items() if t.public)
ENTITY_KEYS=frozenset('player_id team_id staff_id game_id season_id prospect_id'.split())


def history(path,table,*,entity_key=None,entity_id=None,limit=200,role='GM'):
    if role!='GM':raise PermissionError('unsupported role')
    if table not in PUBLIC_TABLES:raise PermissionError('owner-only or unknown dataset')
    if not isinstance(limit,int) or isinstance(limit,bool) or not 1<=limit<=10000:raise ValueError('limit must be 1..10000')
    spec=TABLES[table];cols={c.name for c in spec.columns}
    if entity_key is not None and (entity_key not in ENTITY_KEYS or entity_key not in cols):raise ValueError('invalid entity key')
    where=(' WHERE t.'+ident(entity_key)+'=?') if entity_key else ''
    args=([entity_id] if entity_key else [])+[limit]
    if 'unit_id' in cols:
        sql=f'SELECT t.*,u.observed_at,u.effective_at,u.completeness,r.source_grade FROM {ident(table)} t JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)'+where+' ORDER BY u.observed_at DESC,t.'+ident(spec.key)+' DESC LIMIT ?'
    else:sql=f'SELECT t.* FROM {ident(table)} t'+where+' ORDER BY t.'+ident(spec.key)+' LIMIT ?'
    with closing(connect(path,True)) as c:return [dict(r) for r in c.execute(sql,args)]


def player_card(path,player_id):
    """Return last actual per-field observation with its own age/source.

    A newer partial capture never refreshes the timestamp of an older value.
    Query uses full history, not a truncated history page. Absent fields stay
    NOT_OBSERVED, including attributes the research sample does not contain.
    """
    with closing(connect(path,True)) as c:
        player=c.execute('SELECT * FROM players WHERE player_id=?',(player_id,)).fetchone()
        if player is None:return {'player_id':player_id,'status':'NOT_OBSERVED'}
        result={'player':dict(player),'families':{},'restricted_fields':'WITHHELD'}
        for name in ('player_vitals_observations','player_attribute_snapshots','player_tendency_snapshots','player_contract_observations','player_health_observations','player_morale_observations','player_training_observations'):
            fields={}
            for col in TABLES[name].columns:
                if col.name in ('player_id','unit_id',TABLES[name].key):continue
                sql=f'''SELECT a.{ident(col.name)} AS value,u.unit_id,u.observed_at,u.effective_at,u.completeness,r.source_grade
                  FROM {ident(name)} a JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)
                  WHERE a.player_id=? AND a.{ident(col.name)} IS NOT NULL
                  ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1'''
                row=c.execute(sql,(player_id,)).fetchone()
                fields[col.name]=dict(row) if row else {'value':None,'status':'NOT_OBSERVED'}
                if row and name=='player_attribute_snapshots' and col.name in RATING_COLUMNS:
                    fields[col.name]['decoded_candidate']=registered_rating_candidate(row['value'])
            result['families'][name]=fields
        for name in ('player_badge_values','player_play_type_slots'):
            result['families'][name]=history(path,name,entity_key='player_id',entity_id=player_id)
    return result


def _scalar_families(conn,entity_key,entity_id,tables):
    result={}
    for table in tables:
        values={}
        for col in TABLES[table].columns:
            if col.name in (entity_key,'unit_id',TABLES[table].key):continue
            row=conn.execute(f'''SELECT a.{ident(col.name)} AS value,u.unit_id,u.observed_at,u.effective_at,u.completeness,r.source_grade
                FROM {ident(table)} a JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)
                WHERE a.{ident(entity_key)}=? AND a.{ident(col.name)} IS NOT NULL
                ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''',(entity_id,)).fetchone()
            values[col.name]=dict(row) if row else {'value':None,'status':'NOT_OBSERVED'}
        result[table]=values
    return result


def staff_card(path,staff_id):
    with closing(connect(path,True)) as c:
        row=c.execute('SELECT * FROM staff_members WHERE staff_id=?',(staff_id,)).fetchone()
        if row is None:return {'staff_id':staff_id,'status':'NOT_OBSERVED'}
        result={'staff':dict(row),'families':_scalar_families(c,'staff_id',staff_id,
            ('staff_contract_observations','staff_skill_observations','coach_preferences'))}
    result['assignments']=history(path,'staff_team_assignments',entity_key='staff_id',entity_id=staff_id)
    return result


def team_card(path,team_id):
    with closing(connect(path,True)) as c:
        row=c.execute('SELECT * FROM teams WHERE team_id=?',(team_id,)).fetchone()
        if row is None:return {'team_id':team_id,'status':'NOT_OBSERVED'}
        result={'team':dict(row),'families':_scalar_families(c,'team_id',team_id,
            ('team_finance_observations','team_state_observations','team_tactic_settings'))}
        unit=c.execute('''SELECT u.unit_id FROM capture_units u JOIN staff_team_assignments a USING(unit_id)
            WHERE a.team_id=? ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''',(team_id,)).fetchone()
        result['assigned_staff']=[] if unit is None else [dict(r) for r in c.execute('''SELECT a.*,p.display_name,u.observed_at,r.source_grade
            FROM staff_team_assignments a JOIN staff_members p USING(staff_id) JOIN capture_units u USING(unit_id)
            JOIN capture_runs r USING(run_id) WHERE a.unit_id=? AND a.team_id=? ORDER BY CAST(a.role_code AS INTEGER)''',(unit[0],team_id))]
        book=c.execute('''SELECT a.unit_id FROM team_playbook_slots a JOIN capture_units u USING(unit_id)
            WHERE team_id=? ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''',(team_id,)).fetchone()
        result['playbook_slots']=[] if book is None else [dict(r) for r in c.execute('''SELECT a.*,u.observed_at,r.source_grade
            FROM team_playbook_slots a JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)
            WHERE a.team_id=? AND a.unit_id=? ORDER BY a.slot_index''',(team_id,book[0]))]
    result['season_totals']=history(path,'team_season_totals',entity_key='team_id',entity_id=team_id)
    return result


def prospect_card(path,prospect_id):
    with closing(connect(path,True)) as c:
        row=c.execute('SELECT * FROM draft_prospects WHERE prospect_id=?',(prospect_id,)).fetchone()
        if row is None:return {'prospect_id':prospect_id,'status':'NOT_OBSERVED'}
        result={'prospect':dict(row),'families':_scalar_families(c,'prospect_id',prospect_id,
            ('draft_prospect_attribute_snapshots','draft_prospect_tendency_snapshots')),'restricted_fields':'WITHHELD'}
    result['play_type_slots']=history(path,'draft_prospect_play_type_slots',entity_key='prospect_id',entity_id=prospect_id)
    return result


def market_snapshot(path,*,team_id=None,limit=10000):
    if type(limit) is not int or not 1<=limit<=10000:raise ValueError('limit must be 1..10000')
    with closing(connect(path,True)) as c:
        unit=c.execute('''SELECT u.unit_id,u.observed_at,r.source_grade FROM capture_units u JOIN capture_runs r USING(run_id)
            WHERE u.source_key='BOUND_NATIVE_MARKET_SOURCES' AND u.unit_status='success'
            ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''').fetchone()
        if unit is None:return {'status':'NOT_OBSERVED'}
        args=[unit['unit_id']];where=''
        if team_id is not None:where=' AND o.owner_team_id=?';args.append(team_id)
        picks=[dict(r) for r in c.execute('''SELECT a.*,o.owner_team_id,o.source_row_index,o.native_pick_index_raw,
            o.protection_status,o.swap_status,o.origin_type FROM draft_pick_assets a JOIN draft_pick_ownerships o USING(pick_id)
            WHERE o.unit_id=?'''+where+' ORDER BY a.draft_year,a.draft_round,a.original_team_id',args)]
        args=[unit['unit_id']];where=''
        if team_id is not None:where=' AND team_id=?';args.append(team_id)
        waived=[dict(r) for r in c.execute('SELECT * FROM waived_salary_observations WHERE unit_id=?'+where+' ORDER BY source_row_index',args)]
        slots=[dict(r) for r in c.execute('SELECT * FROM draft_pool_slot_observations WHERE unit_id=? ORDER BY source_row_index',(unit['unit_id'],))]
        if len(picks)+len(waived)+len(slots)>limit:raise ValueError('market snapshot exceeds explicit row cap; no truncation')
        return {'status':'OBSERVED_PARTIAL_MARKET_SOURCES','unit':dict(unit),'future_picks':picks,
            'waived_salary_source_observations':waived,'draft_pool_slots':slots,
            'free_agent_availability':'NOT_OBSERVED_BY_THIS_SOURCE','draft_results':'NOT_INFERRED_FROM_ASSET_OR_SLOT_STATE'}


def game_box(path,game_id):
    with closing(connect(path,True)) as c:
        game=c.execute('SELECT * FROM games WHERE game_id=?',(game_id,)).fetchone()
        if game is None:return {'game_id':game_id,'status':'NOT_OBSERVED'}
    return {'game':dict(game),'states':history(path,'game_state_observations',entity_key='game_id',entity_id=game_id),
            'period_scores':history(path,'game_period_scores',entity_key='game_id',entity_id=game_id),
            'player_boxes':history(path,'player_game_boxes',entity_key='game_id',entity_id=game_id),
            'team_boxes':history(path,'team_game_boxes',entity_key='game_id',entity_id=game_id)}


def schedule(path,*,season_id=None,status_code=None,limit=2000):
    """Latest observed schedule state; scores only from complete canonical Boxes."""
    if type(limit) is not int or not 1<=limit<=10000:raise ValueError('limit must be 1..10000')
    if status_code is not None and status_code not in ('0','1','2'):raise ValueError('native status must be 0, 1 or 2')
    clauses=[];args=[]
    if season_id is not None:clauses.append('g.season_id=?');args.append(season_id)
    if status_code is not None:clauses.append('s.status_code=?');args.append(status_code)
    where=' WHERE '+' AND '.join(clauses) if clauses else ''
    sql='''WITH state AS (
        SELECT s.*,u.observed_at,r.source_grade,
        row_number() OVER (PARTITION BY s.game_id ORDER BY u.observed_at DESC,s.unit_id DESC) AS recency
        FROM game_state_observations s JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)),
      box AS (SELECT game_id,unit_id,team_id,count(*) AS rows,sum(points) AS points
        FROM player_game_boxes GROUP BY game_id,unit_id,team_id),
      expected AS (SELECT game_id,unit_id,side,sum(in_use) AS rows FROM native_box_observations GROUP BY game_id,unit_id,side)
      SELECT g.*,h.display_name AS home_team_name,a.display_name AS away_team_name,
        s.status_code,s.is_final,s.observed_at,s.source_grade,s.unit_id,
        CASE WHEN hb.rows=he.rows AND hb.rows>0 THEN hb.points END AS home_points_derived,
        CASE WHEN ab.rows=ae.rows AND ab.rows>0 THEN ab.points END AS away_points_derived,
        CASE WHEN hb.rows=he.rows AND ab.rows=ae.rows AND hb.rows>0 AND ab.rows>0 THEN 1 ELSE 0 END AS canonical_box_complete,
        'DERIVED_CANONICAL_BOX_SUM_WHEN_ALL_NATIVE_PARTICIPANTS_RESOLVED' AS score_provenance
      FROM games g JOIN teams h ON h.team_id=g.home_team_id JOIN teams a ON a.team_id=g.away_team_id
        LEFT JOIN state s ON s.game_id=g.game_id AND s.recency=1
        LEFT JOIN box hb ON hb.game_id=g.game_id AND hb.unit_id=s.unit_id AND hb.team_id=g.home_team_id
        LEFT JOIN box ab ON ab.game_id=g.game_id AND ab.unit_id=s.unit_id AND ab.team_id=g.away_team_id
        LEFT JOIN expected he ON he.game_id=g.game_id AND he.unit_id=s.unit_id AND he.side='HOME'
        LEFT JOIN expected ae ON ae.game_id=g.game_id AND ae.unit_id=s.unit_id AND ae.side='AWAY' '''
    sql+=where+' ORDER BY g.season_id,CAST(g.native_game_id AS INTEGER),g.game_id LIMIT ?'
    with closing(connect(path,True)) as c:
        count=c.execute('SELECT count(*) FROM ('+sql+')',args+[10001]).fetchone()[0]
        if count>limit:raise ValueError(f'schedule needs limit >= {count}; no silent truncation')
        return [dict(row) for row in c.execute(sql,args+[limit])]


def inspect_source_capture(path,unit_id):
    """Developer evidence/quality inspection; not an ordinary-role Player query."""
    with closing(connect(path,True)) as c:
        unit=c.execute('SELECT u.*,r.source_grade,r.decoder_version,r.save_binding_ref FROM capture_units u JOIN capture_runs r USING(run_id) WHERE unit_id=?',(unit_id,)).fetchone()
        if unit is None:return {'unit_id':unit_id,'status':'NOT_OBSERVED'}
        staged=[dict(r) for r in c.execute('SELECT game_id,side,native_team_id,count(*) AS rows,sum(points) AS derived_box_points FROM native_box_observations WHERE unit_id=? GROUP BY game_id,side,native_team_id ORDER BY side',(unit_id,))]
        periods=[dict(r) for r in c.execute('SELECT game_id,team_id,sum(period_points) AS regulation_period_sum FROM game_period_scores WHERE unit_id=? GROUP BY game_id,team_id',(unit_id,))]
        gaps=[dict(r) for r in c.execute('SELECT target_field,reason,impact,human_exception_ref FROM field_gaps')]
        canonical=c.execute('SELECT count(*) FROM player_game_boxes WHERE unit_id=?',(unit_id,)).fetchone()[0]
        return {'unit':dict(unit),'typed_native_box_staging':staged,'period_sums':periods,
                'canonical_player_box_rows':canonical,'gaps':gaps,'status':'RESEARCH_SOURCE_NOT_CANONICAL_PLAYER_ACCEPTANCE'}


def export_jsonl(path,destination,table,*,limit=10000):
    """Exclusive streamed export, all rows in stable primary-key order.

    Maximum row count is explicit. Refuse an incomplete export instead of
    silently truncating a long history. Output contains public typed facts only.
    """
    if table not in PUBLIC_TABLES:raise PermissionError('owner-only or unknown export')
    if not isinstance(limit,int) or limit<=0:raise ValueError('positive export limit required')
    dest=Path(destination).resolve()
    with closing(connect(path,True)) as c:
        n=c.execute(f'SELECT count(*) FROM {ident(table)}').fetchone()[0]
        if n>limit:raise ValueError(f'export needs limit >= {n}; no silent truncation')
        cols={x.name for x in TABLES[table].columns}
        sql=f'SELECT t.*'+(',u.observed_at,u.effective_at,r.source_grade' if 'unit_id' in cols else '')+f' FROM {ident(table)} t'
        if 'unit_id' in cols:sql+=' JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)'
        sql+=' ORDER BY t.'+ident(TABLES[table].key)
        with dest.open('x',encoding='utf-8',newline='\n') as out:
            for row in c.execute(sql):out.write(json.dumps(dict(row),ensure_ascii=False,allow_nan=False)+'\n')
    return {'table':table,'rows':n,'path':str(dest),'role':'GM'}
