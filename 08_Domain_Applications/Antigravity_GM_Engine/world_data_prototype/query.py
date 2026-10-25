"""Bounded role-safe queries. Give roles these results, never the owner DB file.

SQLite file ownership is not a per-column ACL. GM exports exclude evidence paths,
raw materials, restricted metadata, owner transaction/control and native news.
"""
from contextlib import closing
import json
from pathlib import Path
from observation_scope import query_connection as connect
from schema_model import TABLES, ident,NATIVE_PLAYER_STAT_MAP
from family_codec import registered_rating_candidate,PROFILE
from competition_views import game_box_snapshot,season_summary,player_seasons

RATING_COLUMNS={('three_point_shot' if d['name']=='3pt_shot' else d['name'])+'_raw'
                for d in PROFILE['fields']['PLAYER'] if d.get('conversion')=='rating' and d['name']!='potential'}

PUBLIC_TABLES=frozenset(name for name,t in TABLES.items() if t.public)
ENTITY_KEYS=frozenset('player_id team_id staff_id game_id season_id prospect_id'.split())
HONOR_QUERY_COLUMNS=tuple(NATIVE_PLAYER_STAT_MAP[n] for n in ('MVP','Champion','FinalsMVP','AllNBATeamRank','AllDefensiveTeamRank','AllRookieTeamRank','AllStarStarter','AllStarReserve','RookieOfTheYear','SixthManOfTheYear','DefensivePlayerOfTheYear','MostImprovedPlayer'))


def history_page(path,table,*,entity_key=None,entity_id=None,limit=200,cursor=None):
    """Complete keyset paging over one fixed successful observation ledger."""
    from datetime import datetime,timezone
    from observation_scope import current_scope,observed_as_of
    if table not in PUBLIC_TABLES:raise PermissionError('owner-only or unknown dataset')
    if type(limit) is not int or not 1<=limit<=1000:raise ValueError('history page limit must be 1..1000')
    spec=TABLES[table];columns={c.name for c in spec.columns}
    if 'unit_id' not in columns:raise ValueError('history pages require an observed source-unit table')
    if entity_key is not None and (entity_key not in ENTITY_KEYS or entity_key not in columns or not isinstance(entity_id,str)):raise ValueError('invalid historical entity filter')
    target={'table':table,'entity_key':entity_key,'entity_id':entity_id}
    if cursor is not None:
        if not isinstance(cursor,dict) or set(cursor)!={'format','observed_through','scope_sha256','target','observed_at','record_key'} or cursor['format']!='WORLD_HISTORY_CURSOR_V1' or cursor['target']!=target or not isinstance(cursor['record_key'],str):raise ValueError('invalid history cursor')
    scope=current_scope()
    if scope is None:
        cutoff=cursor['observed_through'] if cursor else datetime.now(timezone.utc).isoformat()
        with observed_as_of(path,cutoff):return history_page(path,table,entity_key=entity_key,entity_id=entity_id,limit=limit,cursor=cursor)
    if cursor and (cursor['scope_sha256']!=scope.fingerprint or cursor['observed_through']!=scope.observed_through):raise ValueError('history observation ledger changed; restart paging with a new scope')
    where=[];args=[]
    if entity_key is not None:where.append('t.'+ident(entity_key)+'=?');args.append(entity_id)
    if cursor:
        from observation_scope import utc_stamp
        stamp=utc_stamp(cursor['observed_at']);where.append('(u.observed_at<? OR (u.observed_at=? AND t.'+ident(spec.key)+'<?))');args.extend((stamp,stamp,cursor['record_key']))
    sql='SELECT t.*,u.observed_at,u.effective_at,u.completeness,r.source_grade FROM '+ident(table)+' t JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)'
    if where:sql+=' WHERE '+' AND '.join(where)
    sql+=' ORDER BY u.observed_at DESC,t.'+ident(spec.key)+' DESC LIMIT ?'
    with closing(connect(path,True)) as c:rows=[dict(r) for r in c.execute(sql,args+[limit+1])]
    more=len(rows)>limit;rows=rows[:limit];next_cursor=None
    if more:
        last=rows[-1];next_cursor={'format':'WORLD_HISTORY_CURSOR_V1','observed_through':scope.observed_through,'scope_sha256':scope.fingerprint,'target':target,'observed_at':last['observed_at'],'record_key':last[spec.key]}
    return {'records':rows,'has_more':more,'next_cursor':next_cursor,'observation_scope':scope.metadata()}


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
        identity=c.execute('''SELECT p.native_unique_id_raw,p.preserved_id_raw,p.canonical_link_status,u.observed_at,r.source_grade
            FROM native_player_sources p JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)
            WHERE p.player_id=? ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''',(player_id,)).fetchone()
        result['native_identity_observation']=dict(identity) if identity else {'status':'NOT_OBSERVED'}
        if player['native_player_id'] is not None:result['legacy_native_id_semantics']='Registered low16 of PLAYERDATA.PreservedId (+760); distinct from UniqueId (+244). Historical opaque player key preserved.'
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
        result['families']['player_badge_values']=player_badges(path,player_id)
        result['families']['player_play_type_slots']=player_play_types(path,player_id)
        result['season_observations']=player_seasons(path,player_id)
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


def native_honors(path,*,flag=None,year=None,subject_name=None,unit_id=None,after_index=-1,limit=200):
    """Raw native selection/winner fields and every source subject reference."""
    if type(limit) is not int or not 1<=limit<=10000:raise ValueError('limit must be 1..10000')
    if type(after_index) is not int or after_index< -1:raise ValueError('after_index must be >= -1')
    if flag is not None and flag not in HONOR_QUERY_COLUMNS:raise ValueError('unregistered native honor field')
    if year is not None and (type(year) is not int or not 1900<=year<=2155):raise ValueError('year outside native byte representation')
    with closing(connect(path,True)) as c:
        args=[];pin=''
        if unit_id is not None:pin=' AND u.unit_id=?';args.append(unit_id)
        unit=c.execute('''SELECT u.unit_id,u.observed_at,u.completeness,r.source_grade,r.season_id AS observation_season_id
            FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.source_key='BOUND_NATIVE_HONOR_STATS'
            AND u.unit_status='success' '''+pin+' ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1',args).fetchone()
        if unit is None:return {'status':'NOT_OBSERVED'}
        columns=(flag,) if flag else HONOR_QUERY_COLUMNS
        where=' WHERE s.unit_id=? AND ('+' OR '.join('s.'+ident(k)+'>0' for k in columns)+')';args=[unit['unit_id']]
        if year is not None:where+=' AND s.stat_year=?';args.append(year)
        if subject_name is not None:
            where+=''' AND EXISTS(SELECT 1 FROM native_player_stat_links l JOIN native_player_sources p USING(player_source_id)
                WHERE l.stat_observation_id=s.stat_observation_id AND p.observed_name=? COLLATE NOCASE)''';args.append(subject_name)
        total=c.execute('SELECT count(*) FROM native_player_stat_observations s'+where,args).fetchone()[0]
        rows=[dict(r) for r in c.execute('SELECT s.* FROM native_player_stat_observations s'+where+
            ' AND s.source_stat_index>? ORDER BY s.source_stat_index LIMIT ?',args+[after_index,limit+1])]
        more=len(rows)>limit;rows=rows[:limit]
        for row in rows:
            subjects=[dict(r) for r in c.execute('''SELECT p.source_player_index,p.native_unique_id_raw,p.preserved_id_raw,p.observed_name,
                p.player_id,p.canonical_link_status,p.current_core_roster_status,l.history_slot_index,l.link_status FROM native_player_stat_links l
                JOIN native_player_sources p USING(player_source_id) WHERE l.stat_observation_id=? ORDER BY p.source_player_index,l.history_slot_index LIMIT 10001''',(row['stat_observation_id'],))]
            if len(subjects)>10000:raise ValueError('source reference cap exceeded; no truncation')
            row['source_subjects']=subjects;row['subject_status']='ALL_OBSERVED_SOURCE_REFERENCES; NO_ARBITRARY_OWNER_CHOICE' if subjects else 'NO_BOUND_SOURCE_SUBJECT'
        return {'status':'OBSERVED_NATIVE_HONOR_FIELDS_WITH_SOURCE_REFERENCES','unit':dict(unit),'matching_native_stat_slots':total,
            'records':rows,'has_more':more,'next_after_index':rows[-1]['source_stat_index'] if more else None,
            'canonical_award_instances':'NOT_ESTABLISHED_BY_THIS_QUERY','reference_count_and_year':'OBSERVED_WORDS_NOT_ALLOCATION_OR_SEASON_CLOSURE_PROOF'}


def native_player_seasons(path,*,player_id=None,subject_name=None,source_index=None,year=None,unit_id=None,after_index=-1,limit=20):
    """All captured fixed-array slots, resolved independently against one source unit."""
    from observation_scope import utc_stamp
    from stat_reference import resolve_reference,RULE
    if type(limit) is not int or not 1<=limit<=100 or type(after_index) is not int or after_index< -1:raise ValueError('invalid native season page')
    if after_index>=0 and unit_id is None:raise ValueError('pin unit_id when continuing native season pages')
    if source_index is not None and (type(source_index) is not int or source_index<0):raise ValueError('invalid source player index')
    if year is not None and (type(year) is not int or not 1900<=year<=2155):raise ValueError('year outside native byte representation')
    with closing(connect(path,True)) as c:
        c.create_function('stat_reference_utc',1,utc_stamp,deterministic=True)
        pin=' AND u.unit_id=?' if unit_id is not None else '';args=[unit_id] if unit_id is not None else []
        unit=c.execute('''SELECT u.unit_id,u.observed_at,u.completeness,r.source_grade,r.season_id AS observation_season_id
            FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.source_key='BOUND_NATIVE_HONOR_STATS'
            AND u.unit_status='success' '''+pin+' ORDER BY stat_reference_utc(u.observed_at) DESC,u.unit_id DESC LIMIT 1',args).fetchone()
        if unit is None:return {'status':'NOT_OBSERVED','unit':None,'records':[],'has_more':False,'next_after_index':None}
        clauses=['p.unit_id=?','p.source_player_index>?'];args=[unit['unit_id'],after_index]
        for column,value in (('player_id',player_id),('source_player_index',source_index),('observed_name',subject_name)):
            if value is not None:clauses.append('p.'+ident(column)+'=?'+(' COLLATE NOCASE' if column=='observed_name' else ''));args.append(value)
        if year is not None:
            clauses.append('''EXISTS(SELECT 1 FROM native_player_stat_links l JOIN native_player_stat_observations s
                ON s.unit_id=l.unit_id AND s.source_stat_index=l.native_stat_index_raw
                WHERE l.player_source_id=p.player_source_id AND l.unit_id=p.unit_id AND l.history_slot_index BETWEEN 0 AND 24
                AND l.native_stat_index_raw<32768 AND s.stat_year=?)''');args.append(year)
        projection='p.player_source_id,p.source_player_index,p.native_unique_id_raw,p.preserved_id_raw,p.observed_name,p.name_status,p.native_team_id,p.current_core_roster_status,p.current_roster_slot,p.player_id,p.canonical_link_status'
        rows=[dict(row) for row in c.execute('SELECT '+projection+' FROM native_player_sources p WHERE '+' AND '.join(clauses)+' ORDER BY p.source_player_index LIMIT ?',args+[limit+1])]
        more=len(rows)>limit;rows=rows[:limit];columns=('stat_observation_id','source_stat_index','stat_year','scoring_identity_status',*NATIVE_PLAYER_STAT_MAP.values());stat_projection=','.join(ident(name) for name in columns)
        for row in rows:
            links=[dict(link) for link in c.execute('''SELECT stat_link_id,history_slot_index,native_stat_index_raw,stat_observation_id,link_status
                FROM native_player_stat_links WHERE unit_id=? AND player_source_id=? ORDER BY history_slot_index''',(unit['unit_id'],row['player_source_id']))]
            row['reference_array_complete']=[link['history_slot_index'] for link in links]==list(range(25));row['captured_reference_count']=len(links);references=[]
            for link in links:
                raw=link['native_stat_index_raw'];position=link['history_slot_index'];record=None
                if 0<=position<25 and raw<32768:
                    found=c.execute('SELECT '+stat_projection+' FROM native_player_stat_observations WHERE unit_id=? AND source_stat_index=?',(unit['unit_id'],raw)).fetchone();record=dict(found) if found else None
                resolution=resolve_reference(raw,position,record)
                if year is not None and (record is None or record['stat_year']!=year):continue
                references.append({'reference_id':link['stat_link_id'],'array_position':position,'native_stat_index_raw':raw,
                    'capture_link_status':link['link_status'],'capture_stat_observation_id':link['stat_observation_id'],
                    'resolution_status':resolution,'record':record,'phase_code':None})
            row['stat_references']=references
        return {'status':'OBSERVED_NATIVE_SEASON_STAT_REFERENCES','unit':dict(unit),'records':rows,'has_more':more,
            'next_after_index':rows[-1]['source_player_index'] if more else None,'reference_rule':RULE,'year_filter':year,
            'scope':'Same-unit Native SeasonStats array references; independent signed16 index checks, including zero and positions after gaps',
            'ownership_and_allocation':'Source association only; shared references, allocation and historical subject lifecycle remain unaccepted',
            'phase_and_order':'No phase labels, chronological slot order, finalization, career aggregation or UI units inferred'}


def record_book(path,*,category_code=None,subject_name=None,unit_id=None,after_index=-1,limit=200):
    """One pinned native record source with explicit bounded index pagination."""
    if type(limit) is not int or not 1<=limit<=10000:raise ValueError('limit must be 1..10000')
    if type(after_index) is not int or after_index< -1:raise ValueError('after_index must be >= -1')
    if category_code is not None and (type(category_code) is not int or not 0<=category_code<=65535):raise ValueError('native category must be uint16')
    with closing(connect(path,True)) as c:
        args=[];pin=''
        if unit_id is not None:pin=' AND u.unit_id=?';args.append(unit_id)
        unit=c.execute('''SELECT u.unit_id,u.observed_at,u.completeness,r.source_grade,r.season_id AS observation_season_id
            FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.source_key='BOUND_RECORD_BOOK'
            AND u.unit_status='success' '''+pin+' ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1',args).fetchone()
        if unit is None:return {'status':'NOT_OBSERVED'}
        where=' WHERE unit_id=?';args=[unit['unit_id']]
        if category_code is not None:where+=' AND native_category_code=?';args.append(category_code)
        if subject_name is not None:
            where+=" AND trim(coalesce(source_first_name,'')||' '||coalesce(source_last_name,''))=? COLLATE NOCASE";args.append(subject_name)
        total=c.execute('SELECT count(*) FROM season_record_entries'+where,args).fetchone()[0]
        rows=[dict(r) for r in c.execute('SELECT * FROM season_record_entries'+where+
            ' AND source_row_index>? ORDER BY source_row_index LIMIT ?',args+[after_index,limit+1])]
        more=len(rows)>limit;rows=rows[:limit]
        return {'status':'OBSERVED_NATIVE_RECORD_SLOTS','unit':dict(unit),'matching_source_slots':total,'records':rows,
            'has_more':more,'next_after_index':rows[-1]['source_row_index'] if more else None,
            'canonical_subject_binding':'NOT_INFERRED_FROM_NAMES_OR_NATIVE_IDS','awards':'NOT_INFERRED_FROM_RECORD_BOOK',
            'record_scope_and_date':'NATIVE_WORDS_WITH_QUALIFIED_RESEARCH_INTERPRETATIONS'}


def settings_snapshot(path,*,scope_code=None,limit=2000):
    """Latest observed settings unit. Native words never become UI defaults."""
    if type(limit) is not int or not 1<=limit<=10000:raise ValueError('limit must be 1..10000')
    with closing(connect(path,True)) as c:
        unit=c.execute('''SELECT u.unit_id,u.observed_at,u.completeness,r.source_grade FROM capture_units u
            JOIN capture_runs r USING(run_id) WHERE u.source_key='BOUND_SETTINGS_AND_RULES' AND u.unit_status='success'
            ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''').fetchone()
        if unit is None:return {'status':'NOT_OBSERVED'}
        where=' AND s.scope_code=?' if scope_code is not None else '';args=[unit['unit_id']]+([scope_code] if scope_code is not None else [])
        rows=[dict(r) for r in c.execute('''SELECT s.*,n.codec,n.legal_range_state FROM game_setting_observations s
            JOIN native_fields n USING(field_id) WHERE s.unit_id=?'''+where+' ORDER BY s.scope_code,s.logical_key LIMIT ?',args+[limit+1])]
        if len(rows)>limit:raise ValueError('settings snapshot exceeds explicit cap; no truncation')
        for row in rows:row['registered_aliases']=json.loads(row.pop('aliases_json') or '[]')
        return {'status':'OBSERVED_NATIVE_WORDS_QUALIFIED_LAYOUT','unit':dict(unit),'settings':rows,
            'ui_value_and_range':'NOT_CERTIFIED_BY_REGISTERED_CANDIDATES','targets_defaults_applied':False}


def rules_snapshot(path,*,season_id=None,limit=2000):
    if type(limit) is not int or not 1<=limit<=10000:raise ValueError('limit must be 1..10000')
    with closing(connect(path,True)) as c:
        args=[];season=''
        if season_id is not None:season=' AND r.season_id=?';args.append(season_id)
        unit=c.execute('''SELECT u.unit_id,u.observed_at,r.source_grade,r.season_id FROM capture_units u
            JOIN capture_runs r USING(run_id) WHERE u.source_key='BOUND_SETTINGS_AND_RULES' AND u.unit_status='success' '''+season+
            ' ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1',args).fetchone()
        if unit is None:return {'status':'NOT_OBSERVED'}
        rows=[dict(r) for r in c.execute('''SELECT r.*,s.logical_key,s.scope_code,s.raw_word_u32,s.value_status,
            s.semantic_status,s.registered_range_status,s.aliases_json FROM league_rule_observations r
            JOIN game_setting_observations s USING(setting_obs_id) WHERE r.unit_id=? ORDER BY r.rule_key LIMIT ?''',(unit['unit_id'],limit+1))]
        if len(rows)>limit:raise ValueError('rules snapshot exceeds explicit cap; no truncation')
        for row in rows:row['registered_aliases']=json.loads(row.pop('aliases_json') or '[]')
        return {'status':'OBSERVED_REGISTERED_LEAGUE_WORDS','unit':dict(unit),'rules':rows,
            'business_policy_or_cba_effect':'NOT_INFERRED_FROM_WORDS'}


def planning_snapshot(path,*,team_id=None,limit=5000):
    if type(limit) is not int or not 1<=limit<=10000:raise ValueError('limit must be 1..10000')
    with closing(connect(path,True)) as c:
        unit=c.execute('''SELECT u.unit_id,u.observed_at,r.source_grade FROM capture_units u JOIN capture_runs r USING(run_id)
            WHERE u.source_key='BOUND_PLANNING_AND_TRAINING' AND u.unit_status='success'
            ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''').fetchone()
        if unit is None:return {'status':'NOT_OBSERVED'}
        groups={};total=0
        for table in ('gameplan_observations','team_training_settings','player_training_observations','mentorship_relations','mentor_manager_observations'):
            args=[unit['unit_id']];where=''
            if team_id is not None:where=' AND team_id=?';args.append(team_id)
            rows=[dict(r) for r in c.execute('SELECT * FROM '+ident(table)+' WHERE unit_id=?'+where+' ORDER BY '+ident(TABLES[table].key),args)]
            total+=len(rows);groups[table]=rows
        if total>limit:raise ValueError('planning snapshot exceeds explicit cap; no truncation')
        counts={r['identity_status']:r['n'] for r in c.execute('SELECT identity_status,count(*) AS n FROM player_training_slot_observations WHERE unit_id=? GROUP BY identity_status',(unit['unit_id'],))}
        return {'status':'OBSERVED_STORED_PLANS_AND_TRAINING','unit':dict(unit),'families':groups,
            'native_commit_flag_counts':{str(r['is_in_use_raw']):r['n'] for r in c.execute('SELECT is_in_use_raw,count(*) AS n FROM gameplan_observations WHERE unit_id=? GROUP BY is_in_use_raw',(unit['unit_id'],))},
            'training_slot_identity_counts':counts,'game_effect':'NOT_INFERRED_FROM_COMMIT_FLAG','training_history':'NOT_ACQUIRED'}


def gameplan_card(path,team_id,opponent_team_id):
    with closing(connect(path,True)) as c:
        plan=c.execute('''SELECT p.*,u.observed_at,r.source_grade FROM gameplan_observations p JOIN capture_units u USING(unit_id)
            JOIN capture_runs r USING(run_id) WHERE p.team_id=? AND p.opponent_team_id=?
            ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''',(team_id,opponent_team_id)).fetchone()
        if plan is None:return {'team_id':team_id,'opponent_team_id':opponent_team_id,'status':'NOT_OBSERVED'}
        rotations=[dict(r) for r in c.execute('''SELECT a.*,p.display_name FROM gameplan_rotation_observations a
            LEFT JOIN players p USING(player_id) WHERE a.plan_id=? ORDER BY a.slot_index''',(plan['plan_id'],))]
        defenses=[dict(r) for r in c.execute('''SELECT a.*,o.display_name AS opponent_display_name,d.display_name AS defender_display_name
            FROM gameplan_defense_observations a LEFT JOIN players o ON o.player_id=a.opponent_player_id
            LEFT JOIN players d ON d.player_id=a.defender_player_id WHERE a.plan_id=? ORDER BY a.slot_index''',(plan['plan_id'],))]
        return {'plan':dict(plan),'rotations':rotations,'defenses':defenses,'game_effect':'NOT_INFERRED_FROM_COMMIT_FLAG'}


def game_box(path,game_id,*,unit_id=None):
    return game_box_snapshot(path,game_id,unit_id=unit_id)


def league_calendar(path,*,season_id=None,limit=20):
    from observation_scope import utc_stamp
    if type(limit) is not int or not 1<=limit<=1000:raise ValueError('calendar limit must be1..1000')
    with closing(connect(path,True)) as c:
        c.create_function('calendar_utc',1,utc_stamp,deterministic=True)
        where=' AND a.season_id=?' if season_id else '';args=[season_id] if season_id else []
        rows=[dict(r) for r in c.execute('''WITH ranked AS (SELECT a.*,u.observed_at,u.effective_at,u.completeness,r.source_grade,
            row_number() OVER(PARTITION BY a.season_id ORDER BY calendar_utc(u.observed_at) DESC,u.unit_id DESC) AS recency
            FROM season_calendar_observations a JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE u.unit_status='success' '''+where+''')
            SELECT * FROM ranked WHERE recency=1 ORDER BY season_id''',args)]
    if len(rows)>limit:raise ValueError('calendar exceeds explicit cap; no truncation')
    for row in rows:row.pop('recency')
    return {'records':rows,'scope':'Current named Native SEASON calendar/period; not the phase of every cumulative stat or franchise offseason substage','timezone':'NOT_OBSERVED','ui_calendar_acceptance':'NOT_ASSERTED'}


def schedule(path,*,season_id=None,status_code=None,period_code=None,game_type_code=None,native_date_from=None,native_date_to=None,limit=2000):
    """Latest observed schedule state; scores only from complete canonical Boxes."""
    if type(limit) is not int or not 1<=limit<=10000:raise ValueError('limit must be 1..10000')
    if status_code is not None and status_code not in ('0','1','2','3'):raise ValueError('native status must be0..3 including POSTPONED')
    clauses=[];args=[]
    if season_id is not None:clauses.append('g.season_id=?');args.append(season_id)
    if status_code is not None:clauses.append('s.status_code=?');args.append(status_code)
    for column,value,bound in [('time_period_raw',period_code,7),('game_type_raw',game_type_code,3)]:
        if value is not None:
            if type(value) is not int or not 0<=value<=bound:raise ValueError('invalid native classification code')
            clauses.append('hc.'+column+'=?');args.append(value)
    from datetime import date
    for value,operator in ((native_date_from,'>='),(native_date_to,'<=')):
        if value is not None:
            try:valid=date.fromisoformat(value).isoformat()==value
            except (TypeError,ValueError):valid=False
            if not valid:raise ValueError('native schedule date filter must be YYYY-MM-DD')
            clauses.append('hc.scheduled_native_iso_date'+operator+'?');args.append(value)
    if native_date_from and native_date_to and native_date_from>native_date_to:raise ValueError('native date range is reversed')
    where=' WHERE '+' AND '.join(clauses) if clauses else ''
    sql='''WITH state AS (
        SELECT s.*,u.observed_at,r.source_grade,
        row_number() OVER (PARTITION BY s.game_id ORDER BY u.observed_at DESC,s.unit_id DESC) AS recency
        FROM game_state_observations s JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)),
      header_checks AS (SELECT c.*,u.observed_at AS header_observed_at,row_number() OVER(PARTITION BY c.game_id ORDER BY u.observed_at DESC,c.unit_id DESC) AS recency
        FROM game_source_checks c JOIN capture_units u USING(unit_id)),
      box AS (SELECT game_id,unit_id,team_id,count(*) AS rows,sum(points) AS points
        FROM player_game_boxes GROUP BY game_id,unit_id,team_id),
      expected AS (SELECT game_id,unit_id,side,sum(in_use) AS rows FROM native_box_observations GROUP BY game_id,unit_id,side)
      SELECT g.*,h.display_name AS home_team_name,a.display_name AS away_team_name,
        s.status_code,s.is_final,s.observed_at,s.source_grade,s.unit_id,
        hc.unit_id AS calendar_unit_id,hc.header_observed_at AS calendar_observed_at,hc.scheduled_native_iso_date AS native_game_date,hc.scheduled_native_time_hhmm AS native_game_time,
        hc.played_native_iso_date AS native_played_date,hc.time_period_raw,hc.time_period_label,hc.game_type_raw,hc.game_type_label,hc.status_label,
        CASE WHEN hb.rows=he.rows AND hb.rows>0 THEN hb.points END AS home_points_derived,
        CASE WHEN ab.rows=ae.rows AND ab.rows>0 THEN ab.points END AS away_points_derived,
        CASE WHEN hb.rows=he.rows AND ab.rows=ae.rows AND hb.rows>0 AND ab.rows>0 THEN 1 ELSE 0 END AS canonical_box_complete,
        'DERIVED_CANONICAL_BOX_SUM_WHEN_ALL_NATIVE_PARTICIPANTS_RESOLVED' AS score_provenance
      FROM games g JOIN teams h ON h.team_id=g.home_team_id JOIN teams a ON a.team_id=g.away_team_id
        LEFT JOIN state s ON s.game_id=g.game_id AND s.recency=1
        LEFT JOIN header_checks hc ON hc.game_id=g.game_id AND hc.recency=1
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


def player_badges(path,player_id):
    with closing(connect(path,True)) as c:
        rows=[dict(r) for r in c.execute('''WITH b AS (SELECT v.*,u.observed_at,r.source_grade,
            row_number() OVER(PARTITION BY v.badge_key ORDER BY u.observed_at DESC,v.unit_id DESC) AS recency
            FROM player_badge_values v JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)
            WHERE v.player_id=?) SELECT * FROM b WHERE recency=1 ORDER BY native_badge_id,badge_key''',(player_id,))]
        for row in rows:row.pop('recency')
        return rows


def player_play_types(path,player_id):
    """Latest observed value of each ordered slot; all raw observations stay in history."""
    with closing(connect(path,True)) as c:
        rows=[dict(r) for r in c.execute('''WITH slots AS (SELECT p.*,u.observed_at,r.source_grade,
            row_number() OVER(PARTITION BY p.slot_index ORDER BY u.observed_at DESC,p.unit_id DESC) AS recency
            FROM player_play_type_slots p JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)
            WHERE p.player_id=? AND p.native_play_code IS NOT NULL) SELECT * FROM slots WHERE recency=1 ORDER BY slot_index''',(player_id,))]
        for row in rows:row.pop('recency')
        return rows


def native_player_details(path,*,subject_name=None,source_index=None,unit_id=None,after_index=-1,limit=10):
    if type(limit) is not int or not 1<=limit<=100 or type(after_index) is not int or after_index< -1:raise ValueError('invalid player detail page')
    if source_index is not None and (type(source_index) is not int or source_index<0):raise ValueError('invalid source index')
    with closing(connect(path,True)) as c:
        if unit_id is None:
            latest=c.execute("SELECT unit_id FROM capture_units WHERE source_key='BOUND_PLAYER_CONTRACT_AND_BASE_BADGES' AND unit_status='success' ORDER BY observed_at DESC,unit_id DESC LIMIT 1").fetchone()
            if latest is None:return {'status':'NOT_OBSERVED','records':[],'unit_id':None,'has_more':False}
            unit_id=latest['unit_id']
        clauses=['p.unit_id=?','p.source_player_index>?'];args=[unit_id,after_index]
        if subject_name is not None:clauses.append('p.observed_name LIKE ?');args.append('%'+subject_name+'%')
        if source_index is not None:clauses.append('p.source_player_index=?');args.append(source_index)
        rows=[dict(r) for r in c.execute('''SELECT p.*,u.observed_at,r.source_grade FROM native_player_sources p
            JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE '''+' AND '.join(clauses)+' ORDER BY p.source_player_index LIMIT ?',args+[limit+1])]
        more=len(rows)>limit;rows=rows[:limit]
        for row in rows:
            contract=c.execute('SELECT * FROM player_contract_observations WHERE source_player_id=? AND unit_id=?',(row['player_source_id'],unit_id)).fetchone()
            row['contract']=dict(contract) if contract else None
            row['base_badges']=[dict(r) for r in c.execute('SELECT * FROM player_badge_values WHERE source_player_id=? AND unit_id=? ORDER BY native_badge_id',(row['player_source_id'],unit_id))]
        return {'records':rows,'unit_id':unit_id,'has_more':more,'next_after_index':rows[-1]['source_player_index'] if more else None,
            'semantics':'Stored base badges, raw contract values and qualified current identities; effective context/UI/salary scale/lifecycle separate',
            'legacy_column_aliases':{'original_contract_years_raw':'Native ContractLength; original-duration semantics not asserted','contract_type_raw':'Native RosterType; not a financial contract-type classification'}}


def native_player_state(path,*,subject_name=None,source_index=None,unit_id=None,after_index=-1,limit=20):
    if type(limit) is not int or not 1<=limit<=100 or type(after_index) is not int or after_index< -1:raise ValueError('invalid player state page')
    if source_index is not None and (type(source_index) is not int or source_index<0):raise ValueError('invalid source player index')
    with closing(connect(path,True)) as c:
        if unit_id is None:
            latest=c.execute("SELECT unit_id FROM capture_units WHERE source_key='BOUND_PLAYER_VITALS_HEALTH_MORALE' AND unit_status='success' ORDER BY observed_at DESC,unit_id DESC LIMIT 1").fetchone()
            if latest is None:return {'status':'NOT_OBSERVED','records':[],'has_more':False,'unit_id':None}
            unit_id=latest['unit_id']
        clauses=['p.unit_id=?','p.source_player_index>?'];args=[unit_id,after_index]
        if subject_name is not None:clauses.append('p.observed_name LIKE ?');args.append('%'+subject_name+'%')
        if source_index is not None:clauses.append('p.source_player_index=?');args.append(source_index)
        rows=[dict(r) for r in c.execute('''SELECT p.*,u.observed_at,r.source_grade FROM native_player_sources p
            JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE '''+' AND '.join(clauses)+' ORDER BY p.source_player_index LIMIT ?',args+[limit+1])]
        more=len(rows)>limit;rows=rows[:limit]
        for row in rows:
            for key,table in (('vitals','player_vitals_observations'),('health','player_health_observations'),('morale','player_morale_observations')):
                value=c.execute('SELECT * FROM '+ident(table)+' WHERE source_player_id=? AND unit_id=?',(row['player_source_id'],unit_id)).fetchone()
                row[key]=dict(value) if value else None
        return {'records':rows,'unit_id':unit_id,'has_more':more,'next_after_index':rows[-1]['source_player_index'] if more else None,
            'semantics':'Native stored body/position/injury slots/fatigue/morale; UI scale, aggregate availability, recovery days, energy and playing-role satisfaction remain separate'}


def native_player_skills(path,*,subject_name=None,source_index=None,unit_id=None,after_index=-1,limit=20):
    if type(limit) is not int or not 1<=limit<=100 or type(after_index) is not int or after_index< -1:raise ValueError('invalid skill page')
    if source_index is not None and (type(source_index) is not int or source_index<0):raise ValueError('invalid skill source index')
    with closing(connect(path,True)) as c:
        if unit_id is None:
            latest=c.execute("SELECT unit_id FROM capture_units WHERE source_key='BOUND_PUBLIC_PLAYER_SKILLS' AND unit_status='success' ORDER BY observed_at DESC,unit_id DESC LIMIT 1").fetchone()
            if latest is None:return {'status':'NOT_OBSERVED','records':[],'has_more':False,'unit_id':None}
            unit_id=latest['unit_id']
        clauses=['p.unit_id=?','p.source_player_index>?'];args=[unit_id,after_index]
        if subject_name is not None:clauses.append('p.observed_name LIKE ?');args.append('%'+subject_name+'%')
        if source_index is not None:clauses.append('p.source_player_index=?');args.append(source_index)
        rows=[dict(r) for r in c.execute('''SELECT p.*,u.observed_at,r.source_grade FROM native_player_sources p
            JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE '''+' AND '.join(clauses)+' ORDER BY p.source_player_index LIMIT ?',args+[limit+1])]
        more=len(rows)>limit;rows=rows[:limit]
        for row in rows:
            for key,table in [('attributes','player_attribute_snapshots'),('tendencies','player_tendency_snapshots')]:
                value=c.execute('SELECT * FROM '+ident(table)+' WHERE source_player_id=? AND unit_id=?',(row['player_source_id'],unit_id)).fetchone();row[key]=dict(value) if value else None
            row['play_types']=[dict(r) for r in c.execute('SELECT * FROM player_play_type_slots WHERE source_player_id=? AND unit_id=? ORDER BY slot_index',(row['player_source_id'],unit_id))]
        return {'records':rows,'unit_id':unit_id,'has_more':more,'next_after_index':rows[-1]['source_player_index'] if more else None,
            'semantics':'Native unsigned skill storage and ordered PlayType enum; no overall getter call, rating/UI transform, effective context or behavior acceptance'}


def native_affiliations(path,*,subject_name=None,source_index=None,flag=None,flag_value=1,unit_id=None,after_index=-1,limit=20):
    from player_affiliation_codec import PROFILE as affiliation_profile
    if type(limit) is not int or not 1<=limit<=100 or type(after_index) is not int or after_index< -1:raise ValueError('invalid affiliation page')
    if source_index is not None and (type(source_index) is not int or source_index<0):raise ValueError('invalid affiliation source index')
    if flag is not None:
        if flag not in affiliation_profile['player_fields'] or type(flag_value) is not int or not 0<=flag_value<(1<<affiliation_profile['player_fields'][flag]['width']):raise ValueError('invalid native classification filter')
    with closing(connect(path,True)) as c:
        if unit_id is None:
            latest=c.execute("SELECT unit_id FROM capture_units WHERE source_key='BOUND_PLAYER_AFFILIATION_CLASSIFICATION' AND unit_status='success' ORDER BY observed_at DESC,unit_id DESC LIMIT 1").fetchone()
            if latest is None:return {'status':'NOT_OBSERVED','records':[],'has_more':False,'unit_id':None}
            unit_id=latest['unit_id']
        clauses=['p.unit_id=?','p.source_player_index>?'];args=[unit_id,after_index]
        if subject_name is not None:clauses.append('p.observed_name LIKE ?');args.append('%'+subject_name+'%')
        if source_index is not None:clauses.append('p.source_player_index=?');args.append(source_index)
        if flag is not None:clauses.append('m.'+ident(flag)+'=?');args.append(flag_value)
        rows=[dict(r) for r in c.execute('''SELECT p.*,u.observed_at,r.source_grade FROM native_player_sources p
            JOIN market_state_observations m ON m.source_player_id=p.player_source_id AND m.unit_id=p.unit_id
            JOIN capture_units u ON u.unit_id=p.unit_id JOIN capture_runs r USING(run_id) WHERE '''+' AND '.join(clauses)+' ORDER BY p.source_player_index LIMIT ?',args+[limit+1])]
        more=len(rows)>limit;rows=rows[:limit]
        for row in rows:
            state=c.execute('SELECT * FROM market_state_observations WHERE source_player_id=? AND unit_id=?',(row['player_source_id'],unit_id)).fetchone();row['classification']=dict(state)
            vitals=c.execute('SELECT native_college_obs_id,college_source_status,college_country_semantics_status FROM player_vitals_observations WHERE source_player_id=? AND unit_id=?',(row['player_source_id'],unit_id)).fetchone()
            row['school_country_source']=dict(vitals) if vitals else None
            if vitals and vitals['native_college_obs_id']:
                college=c.execute('SELECT * FROM native_college_observations WHERE college_observation_id=? AND unit_id=?',(vitals['native_college_obs_id'],unit_id)).fetchone()
                row['school_country_source']['native_referent']=dict(college) if college else None
        counts={key:c.execute('SELECT count(*) FROM market_state_observations WHERE unit_id=? AND '+ident(key)+'=1',(unit_id,)).fetchone()[0] for key,f in affiliation_profile['player_fields'].items() if f['width']==1}
        return {'records':rows,'unit_id':unit_id,'has_more':more,'next_after_index':rows[-1]['source_player_index'] if more else None,
            'source_boolean_counts':counts,'semantics':'Native independent flags, codes and COLLEGEDATA referents; signability, active G League assignment and school/country/nationality category not inferred'}


def awards(path,*,year=None,award_code=None,after_key='',limit=200):
    if type(limit) is not int or not 1<=limit<=1000:raise ValueError('limit must be 1..1000')
    if year is not None and (type(year) is not int or not 1<=year<=4095):raise ValueError('invalid native year')
    clauses=['a.award_id>?'];args=[after_key]
    if year is not None:clauses.append('a.source_year_raw=?');args.append(year)
    if award_code is not None:clauses.append('a.award_code=?');args.append(award_code)
    with closing(connect(path,True)) as c:
        values=[dict(r) for r in c.execute('''SELECT a.*,u.observed_at,r.source_grade FROM season_award_instances a
            JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE '''+' AND '.join(clauses)+' ORDER BY a.award_id LIMIT ?',args+[limit+1])]
        more=len(values)>limit;values=values[:limit]
        for award in values:
            award['recipients']=[dict(r) for r in c.execute('''SELECT p.recipient_id,p.player_id,p.team_id,p.staff_id,p.rank_index,p.source_subject_type,
                h.player_first_name,h.player_last_name,h.primary_team_name,h.primary_team_city,h.secondary_team_name,h.secondary_team_city,
                h.player_id_raw,h.primary_team_id_raw,h.secondary_team_id_raw,p.source_history_id
                FROM award_recipients p LEFT JOIN native_league_history_observations h ON h.history_observation_id=p.source_history_id
                WHERE p.award_id=? ORDER BY p.recipient_id''',(award['award_id'],))]
            observed=c.execute('''SELECT u.observed_at,u.unit_id,r.source_grade,h.award_link_status
                FROM native_league_history_observations h JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)
                WHERE h.award_id=? ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1''',(award['award_id'],)).fetchone()
            award['latest_source_observation']=dict(observed) if observed else None
        return {'awards':values,'has_more':more,'next_after_key':values[-1]['award_id'] if more else None,
            'scope':'NATIVE_ROSTER_HISTORY is archived source history; canonical subject lifecycle and world occurrence not inferred'}


def league_history(path,*,year=None,type_label=None,unit_id=None,after_index=-1,limit=200):
    if type(limit) is not int or not 1<=limit<=1000 or type(after_index) is not int or after_index< -1:raise ValueError('invalid history page')
    with closing(connect(path,True)) as c:
        if unit_id is None:
            latest=c.execute("SELECT u.unit_id FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.source_key='BOUND_LEAGUE_HISTORY_AND_AWARDS' AND u.unit_status='success' ORDER BY u.observed_at DESC,u.unit_id DESC LIMIT 1").fetchone()
            if latest is None:return {'status':'NOT_OBSERVED','records':[],'has_more':False,'unit_id':None}
            unit_id=latest['unit_id']
        clauses=['h.unit_id=?','h.source_row_index>?','h.native_type_code<>0'];args=[unit_id,after_index]
        if year is not None:
            if type(year) is not int or not 1<=year<=4095:raise ValueError('invalid native year')
            clauses.append('h.native_year_raw=?');args.append(year)
        if type_label is not None:clauses.append('h.native_type_label=?');args.append(type_label)
        rows=[dict(r) for r in c.execute('''SELECT h.*,u.observed_at,r.source_grade FROM native_league_history_observations h
            JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE '''+' AND '.join(clauses)+' ORDER BY h.source_row_index LIMIT ?',args+[limit+1])]
        more=len(rows)>limit;rows=rows[:limit]
        return {'records':rows,'unit_id':unit_id,'has_more':more,'next_after_index':rows[-1]['source_row_index'] if more else None,
            'scope':'NATIVE_ROSTER_HISTORY; no inferred lifetime subjects, UI award acceptance or world occurrence'}


def native_news(path,*,event_label=None,unit_id=None,after_index=-1,limit=200):
    """Explicit safe event projection: no generic parameters or text fragments."""
    if type(limit) is not int or not 1<=limit<=1000 or type(after_index) is not int or after_index< -1:raise ValueError('invalid news page')
    with closing(connect(path,True)) as c:
        if unit_id is None:
            latest=c.execute("SELECT unit_id FROM capture_units WHERE source_key='BOUND_NATIVE_NEWS_AND_TRANSACTIONS' AND unit_status='success' ORDER BY observed_at DESC,unit_id DESC LIMIT 1").fetchone()
            if latest is None:return {'status':'NOT_OBSERVED','records':[],'has_more':False,'unit_id':None}
            unit_id=latest['unit_id']
        clauses=['m.unit_id=?','m.bank_index*2000+m.source_slot_index>?','m.event_code>0'];args=[unit_id,after_index]
        if event_label is not None:clauses.append('m.event_label=?');args.append(event_label)
        projection='m.bank_index,m.source_slot_index,m.event_code,m.event_label,m.sender_type_label,m.date_word_raw,m.date_id_raw,m.date_minutes_raw,m.date_day_raw,m.date_month_raw,m.date_year_offset_raw,m.source_state,m.active_prefix_status'
        rows=[dict(r) for r in c.execute('SELECT '+projection+''',u.observed_at,r.source_grade FROM native_social_message_observations m
            JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE '''+' AND '.join(clauses)+' ORDER BY m.bank_index,m.source_slot_index LIMIT ?',args+[limit+1])]
        more=len(rows)>limit;rows=rows[:limit]
        return {'records':rows,'unit_id':unit_id,'has_more':more,'next_after_index':rows[-1]['bank_index']*2000+rows[-1]['source_slot_index'] if more else None,
            'content_status':'NATIVE_EVENT_AND_DATE_COMPONENTS; RENDERED_TEXT_AND_UI_ACTIVITY_UNVERIFIED',
            'withheld':'Generic parameters and string fragments stay owner-only pending renderer/privacy semantics'}


def native_transactions(path,*,unit_id=None):
    with closing(connect(path,True)) as c:
        if unit_id is None:
            latest=c.execute("SELECT unit_id FROM capture_units WHERE source_key='BOUND_NATIVE_NEWS_AND_TRANSACTIONS' AND unit_status='success' ORDER BY observed_at DESC,unit_id DESC LIMIT 1").fetchone()
            if latest is None:return {'status':'NOT_OBSERVED'}
            unit_id=latest['unit_id']
        control=c.execute('''SELECT c.transaction_count,u.observed_at,r.source_grade FROM native_league_capture_controls c
            JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) WHERE c.unit_id=? AND c.source_mode='NEWS_TRANSACTIONS' ''',(unit_id,)).fetchone()
        rows=[dict(r) for r in c.execute("SELECT source_slot_index,native_type_code,native_type_label,data_count_raw,date_word_raw,active_prefix_status FROM native_transaction_observations WHERE unit_id=? AND active_prefix_status='WITHIN_DECLARED_COUNT_PREFIX_CANDIDATE' ORDER BY source_slot_index",(unit_id,))]
        return {'unit_id':unit_id,'native_control':dict(control) if control else None,'candidate_entries':rows,
            'status':'NATIVE_STORAGE_NOT_EXTERNAL_EXECUTION_OR_ACCEPTED_TRANSACTION'}


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
