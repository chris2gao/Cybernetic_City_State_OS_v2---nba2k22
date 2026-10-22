"""M3 reads only sealed M0 projections; exports plain DTOs and actual access receipts."""
from copy import deepcopy
import json
import re

from . import AccessError, QUERY_VERSION
from .query import QuerySession
from gm_core.workbench_common import now, require, text_required
from gm_state_io.registry import Registry

PROJECTIONS = {
    'teams': ['team_id','team','total_wins','total_losses','total_salary'],
    'team_stats': ['team_id','team','season_year','totals','source_status'],
    'players': ['identity','name','team_id','team','pool_slot','position','face_id','birth_date','salary','years_left','contract','attributes','season_totals'],
    'staff': ['identity','name','team_id','team','role','candidate_position','mapping_status','salary','years_left','attributes'],
    'coaching': ['team_id','team','coach','values','readiness'],
    'defense': ['team_id','opponent_team_id','values','mixed_fields','status'],
    'picks': ['asset_id','team_id','owner','original_team_id','draft_year','draft_round','trade_eligible'],
    'finance': ['team_id','team','total_salary','payroll','budget','cash','financial_eligibility'],
}


def consume(session, entity, fields, receipts, filters=None, sql=None, params=None, access_suffix=''):
    rows, cursor, pages = [], None, 0
    if not session.available[entity]:
        receipts.append(dict(access_id='access:'+entity, entity=entity, binding=deepcopy(session.binding),
            projection=fields, status='SOURCE_UNAVAILABLE', read_count=0, returned_identities=[], cursor_exhausted=True))
        return rows
    while True:
        p = session.query(entity, fields=fields, filters=filters, sql=sql, params=params, limit=50, cursor=cursor)
        rows.extend(p['rows'])
        pages += 1
        if not p['truncated']:
            break
        if not p['next_cursor'] or p['next_cursor'] == cursor:
            raise AccessError('RESULT_LIMIT_REACHED', 'M3 could not exhaust '+entity)
        cursor = p['next_cursor']
    receipts.append(dict(access_id='access:'+entity+access_suffix, entity=entity, binding=deepcopy(session.binding),
        projection=fields, filters=filters or {}, sql_projection=sql, query_version=QUERY_VERSION, screened_count=None, read_count=len(rows),
        returned_identities=[r.get('identity', r.get('asset_id', str(r.get('team_id'))+':'+str(r.get('opponent_team_id','')))) for r in rows],
        cursor_exhausted=True, pages=pages, status='ROWS_READ_NOT_ASSESSED', requested_scope='ALL_PROJECTED_SOURCE_ROWS',
        execution_origin=dict(kind='LOCAL_CLI', tool_name='QuerySession', time=now())))
    return rows


def load_inputs(query_root, published_root, career, batch, allow_local=False, defense_matchups=()):
    if not batch:
        raise ValueError('EXPLICIT_BATCH_REQUIRED')
    session = QuerySession(query_root, published_root, career, batch)
    try:
        mask = session.require_gm_sanitized()
        if session.binding['publication_status'] == 'LOCAL_AUDITED_NOT_PUBLISHED' and not allow_local:
            raise AccessError('LOCAL_AUDITED_NOT_PUBLISHED', 'Explicit development opt-in required')
        receipts = []
        result = {e: consume(session, e, f, receipts) for e,f in PROJECTIONS.items()}
        reg=Registry()
        native=load_native(session,result['teams'],receipts,reg,defense_matchups)
        if native['context']:
            row=native['context']
            session.binding.update(save_id=row['save_id'],save_instance_id=row['save_instance_id'],
                generation_id=row['generation_id'],registry_version=row['registry_version'])
        for access in receipts:
            access['binding']=deepcopy(session.binding)
        result.update(source_binding=deepcopy(session.binding), context=deepcopy(session.record['source_manifest'].get('context',{})), source_access=receipts)
        result.update(potential_mask=deepcopy(mask),native=native)
        return result
    finally:
        session.close()


def load_native(session, teams, receipts, registry, defense_matchups=()):
    """Same M0 cursor contract, partitioning named tendencies by team below its row cap."""
    contexts=consume(session,'native_context',list(session.columns['native_context']),receipts)
    objects=[]
    kinds=('COACH_DEFAULT','PLAYER_TENDENCY','PLAYER_PLAYTYPE','PLAYER_ROTATION_OVR_BIAS','TEAM_TRAINING','PLAYER_TRAINING','PLAYBOOK_SLOT')
    fields=list(session.columns['native_objects'])
    sql='SELECT '+','.join('"'+f+'"' for f in fields)+' FROM q_native_objects WHERE team_id=? AND target_kind IN ('+','.join('?' for _ in kinds)+') ORDER BY identity'
    for t in teams:
        objects.extend(consume(session,'native_objects',fields,receipts,sql=sql,params=[t['team_id'],*kinds],access_suffix=':'+str(t['team_id'])))
    books=consume(session,'native_books',list(session.columns['native_books']),receipts)
    traits=consume(session,'coach_traits',list(session.columns['coach_traits']),receipts)
    values=[]
    for domain in ('tactics','training','rotation'):
        values.extend(consume(session,domain,list(session.columns[domain]),receipts))
    requested=[]
    for matchup in defense_matchups:
        pair=[]
        for key in matchup.split(':'):
            hits=[t for t in teams if str(t['team_id'])==key or t['team']==key.upper()]
            if len(hits)!=1:
                raise ValueError('UNKNOWN_DEFENSE_MATCHUP_TEAM')
            pair.append(hits[0]['team_id'])
        if len(pair)!=2 or pair[0]==pair[1]:
            raise ValueError('OWNER_AND_OPPONENT_REQUIRED')
        if pair in requested:
            continue
        requested.append(pair)
        filters=dict(team_id=pair[0],opponent_team_id=pair[1])
        values.extend(consume(session,'personal_defense',list(session.columns['personal_defense']),receipts,filters=filters,access_suffix=':'+matchup))
        objects.extend(consume(session,'native_objects',fields,receipts,filters=dict(**filters,target_kind='PERSONAL_DEFENSE'),access_suffix=':personal:'+matchup))
    names=[key for key,f in registry.fields.items() if f['domain']=='tendency' and f['gm_enabled']]
    if session.available['tendency']:
        fields=list(session.columns['tendency'])
        sql='SELECT '+','.join('"'+f+'"' for f in fields)+' FROM q_tendency WHERE team_id=? AND field_key IN ('+','.join('?' for _ in names)+') ORDER BY identity'
        for t in teams:
            values.extend(consume(session,'tendency',fields,receipts,sql=sql,params=[t['team_id'],*names],access_suffix=':'+str(t['team_id'])))
    else:
        consume(session,'tendency',list(session.columns['tendency']),receipts)
    catalog={key:dict(field_key=key,domain=f['domain'],target_kind=f['target_kind'],gm_enabled=f['gm_enabled'],
        write_capability=f['write_capability'],enum=f['layout'].get('enum'),value_range=f['layout'].get('raw_range'),
        native_evidence=f['native_evidence'],behavior_evidence=f['behavior_evidence'],restricted_operation=f.get('restricted_operation'))
        for key,f in registry.fields.items() if f['domain'] in ('tactics','defense','training','rotation','tendency') and not key.startswith('tendency.RAW_')}
    return dict(context=contexts[0] if len(contexts)==1 else None,objects=objects,books=books,values=values,coach_traits=traits,defense_matchups=requested,
        field_catalog=catalog,consumer_registry_version=registry.version,
        unknowns=['51_UNNAMED_TENDENCIES_EXCLUDED','CRC_PLAY_TYPE_MAPPING_UNKNOWN','FATIGUE_NOT_OBSERVED',
                  'POSITION_SPECIFIC_UI_TRAINING_TEMPLATES_UNKNOWN','TRAINING_EFFECT_NOT_QUANTIFIED'])


def screen(session, query, player_fields, staff_fields, limit=5, cursor=None):
    """Compile registered field names only; all caller values stay SQL parameters."""
    session.require_gm_sanitized()
    require(query, ('query_id','source_domain','role_question','filters','excluded_team_ids','order_by'))
    text_required(query['query_id'], 'query_id')
    text_required(query['role_question'], 'role_question')
    limit=min(limit,query.get('limit',limit))
    if type(limit) is not int or not 1<=limit<=5:
        raise ValueError('MARKET_LIMIT_1_TO_5')
    domain = query['source_domain']
    entity = {'roster':'players','pool':'pool','staff':'staff'}.get(domain)
    if not entity or not session.available[entity]:
        raise ValueError('MARKET_SOURCE_UNAVAILABLE')
    allowed = set(staff_fields if domain == 'staff' else player_fields)
    required_fields = set()
    params = []

    def field(name):
        if entity in ('players','pool') and name.casefold() in ('attributes.potential.value','attributes.intangibles.value'):
            raise ValueError('MASKED_POTENTIAL_AND_ROTATION_BIAS_NOT_SCOUTING_SCORES')
        match = re.fullmatch(r'attributes\.([A-Za-z0-9_]+)\.value', name)
        if match and match[1] in allowed:
            required_fields.add(name)
            return "json_extract(attributes, '$.\""+match[1]+"\".value')"
        if name in session.columns[entity] and name not in {'attributes', 'contract', 'season_totals'}:
            required_fields.add(name)
            return '"'+name+'"'
        raise ValueError('UNREGISTERED_MARKET_FIELD:'+name)

    conditions, ordering = [], []
    if not isinstance(query['filters'], list) or not isinstance(query['order_by'], list):
        raise ValueError('MARKET_FILTERS_AND_ORDER_LIST_REQUIRED')
    for f in query['filters']:
        expr = field(f['native_field'])
        op = f['operator']
        if op == 'is_null':
            conditions.append(expr+' IS NULL')
        elif op in ('eq','gte','lte') and type(f.get('value')) in (str,int,float):
            conditions.append(expr+{'eq':' = ?','gte':' >= ?','lte':' <= ?'}[op])
            params.append(f['value'])
        else:
            raise ValueError('INVALID_MARKET_OPERATOR_OR_VALUE')
    for o in query['order_by']:
        direction = o['direction'].upper()
        if direction not in ('ASC','DESC'):
            raise ValueError('INVALID_MARKET_ORDER')
        expr = field(o['native_field'])
        ordering.extend([expr+' IS NULL ASC', expr+' '+direction])
    ordering.append('identity ASC')
    excluded = query['excluded_team_ids']
    if not isinstance(excluded, list) or len(excluded)>30 or any(type(t) is not int for t in excluded):
        raise ValueError('INVALID_EXCLUDED_TEAM_IDS')
    population = ''
    if excluded:
        if entity == 'pool':
            # Pool has no certified team_id. Ownership is available only through same-batch roster join.
            population = ' NOT EXISTS(SELECT identity FROM q_players r WHERE r.pool_slot=q_pool.slot_id AND r.team_id IN ('+','.join('?' for _ in excluded)+'))'
        else:
            population = '(team_id IS NULL OR team_id NOT IN ('+','.join('?' for _ in excluded)+'))'
    base_params = list(excluded)
    base_where = ' WHERE '+population if population else ''
    where = base_where+(' AND ' if population else ' WHERE ')+(' AND '.join(conditions) or '1=1')
    projection = 'identity,name'+(',team_id,team' if entity in ('players','staff') else ',roster_status')
    # Return the specific decoded values used in screening, not whole raw structs.
    projection += ''.join(','+field_expr+' AS "screen_'+str(i)+'"' for i,field_expr in enumerate([field(k) for k in sorted(required_fields)]))
    stats_sql = 'SELECT COUNT(*) AS population FROM q_'+entity+base_where
    population_count = session.query('sql', sql=stats_sql, params=base_params)['rows'][0]['population']
    matched = session.query('sql', sql='SELECT COUNT(*) AS matched FROM q_'+entity+where, params=base_params+params)['rows'][0]['matched']
    # Explicit is_null is a requested class, not a silently failed numeric comparison.
    null_fields = [field(f['native_field']) for f in query['filters'] if f['operator'] != 'is_null']
    unknown = session.query('sql', sql='SELECT COUNT(*) AS unknown_count FROM q_'+entity+base_where+(' AND ' if population else ' WHERE ')+(' OR '.join(e+' IS NULL' for e in null_fields) or '0=1'), params=base_params)['rows'][0]['unknown_count']
    result = session.query('sql', sql='SELECT '+projection+' FROM q_'+entity+where+' ORDER BY '+','.join(ordering), params=base_params+params, limit=limit, cursor=cursor)
    return dict(query=deepcopy(query), source_binding=deepcopy(session.binding), filter_population_count=population_count,
        matched_count=matched, unknown_required_field_count=unknown, screen_fields=sorted(required_fields),
        rows=result['rows'], returned_identities=[r['identity'] for r in result['rows']], next_cursor=result['next_cursor'],
        cursor_exhausted=not result['truncated'], status='SCREENED_SUBSET_READ_NOT_ASSESSED',
        execution_origin=dict(kind='LOCAL_CLI', tool_name='QuerySession', time=now()), query_version=QUERY_VERSION)
