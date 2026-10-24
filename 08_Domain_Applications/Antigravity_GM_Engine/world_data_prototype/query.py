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
ENTITY_KEYS=frozenset('player_id team_id staff_id game_id season_id'.split())


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


def game_box(path,game_id):
    with closing(connect(path,True)) as c:
        game=c.execute('SELECT * FROM games WHERE game_id=?',(game_id,)).fetchone()
        if game is None:return {'game_id':game_id,'status':'NOT_OBSERVED'}
    return {'game':dict(game),'states':history(path,'game_state_observations',entity_key='game_id',entity_id=game_id),
            'period_scores':history(path,'game_period_scores',entity_key='game_id',entity_id=game_id),
            'player_boxes':history(path,'player_game_boxes',entity_key='game_id',entity_id=game_id),
            'team_boxes':history(path,'team_game_boxes',entity_key='game_id',entity_id=game_id)}


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
