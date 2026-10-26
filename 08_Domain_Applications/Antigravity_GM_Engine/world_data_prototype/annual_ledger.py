"""Annual baseline/addition identity metadata; domain values stay typed rows."""
import hashlib,json,sqlite3

PRIMARY_TABLES={
    'RECORD_BOOK':('season_record_entries',),
    'NATIVE_HONOR_STATS':('native_player_stat_observations',),
    'LEAGUE_HISTORY_AWARDS':('native_league_history_observations','native_award_matrix_observations','season_award_instances','award_recipients'),
    'STAFF_SEASON_HISTORY':('native_coach_stat_observations',),
}
CANONICAL=frozenset(('season_award_instances','award_recipients'))
CONTEXT_TABLES={
    'RECORD_BOOK':('field_gaps',),
    'NATIVE_HONOR_STATS':('native_fields','native_player_sources','native_player_stat_links','native_identity_links','field_gaps'),
    'LEAGUE_HISTORY_AWARDS':('native_league_capture_controls','fact_conflicts','field_gaps'),
    'STAFF_SEASON_HISTORY':('native_staff_history_subjects','native_staff_stat_links','game_mode_observations','field_gaps'),
}

def sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')).hexdigest()


def honor_columns(table):
    if table=='native_player_stat_observations':
        from schema_model import NATIVE_PLAYER_STAT_MAP
        return [NATIVE_PLAYER_STAT_MAP[n] for n in ('MVP','Champion','FinalsMVP','AllNBATeamRank','AllDefensiveTeamRank','AllRookieTeamRank','AllStarStarter','AllStarReserve','RookieOfTheYear','SixthManOfTheYear','DefensivePlayerOfTheYear','MostImprovedPlayer')]
    if table=='native_coach_stat_observations':
        from pathlib import Path
        profile=json.loads(Path(__file__).with_name('staff_history_native_profile.json').read_bytes())
        return [profile['stat_fields'][n]['column'] for n in ('CoachWonTitle','CoachWonCoachOfTheYear')]
    return []


def allowed_native_fields(family):
    from schema_model import TABLES
    table={'NATIVE_HONOR_STATS':'native_player_stat_observations','STAFF_SEASON_HISTORY':'native_coach_stat_observations'}.get(family)
    if table is None:return set()
    return {c.name for c in TABLES[table].columns if c.visibility=='GM_PUBLIC' and c.source.startswith(('CURRENT_PLAYERSTATDATA.','CURRENT_NATIVE.COACHSTATDATA.'))}


def _known_values(conn,table,row,baseline,family,year,names):
    from schema_model import ident
    rows=conn.execute('SELECT t.* FROM '+ident(table)+''' t JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id)
        WHERE (u.unit_id=? OR r.refresh_baseline_unit_id=?) AND r.refresh_family=? AND r.refresh_period_year=?
        AND r.source_grade='LIVE_READ' AND u.unit_status='success' AND t.source_stat_index=? AND t.stat_year IS ?''',
        (baseline,baseline,family,year,row['source_stat_index'],row.get('stat_year'))).fetchall()
    return {name:{source[name] for source in rows if source[name] is not None} for name in names}


def _row_claims(table,row):
    flags=honor_columns(table)
    if not flags:
        key,digest=fingerprint(table,row);return [{'fact_key':key,'fact_sha256':digest,'field_name':None}]
    identity=sha([row.get('source_stat_index'),row.get('stat_year')]);_,digest=fingerprint(table,row)
    result=[{'fact_key':'SOURCE_ROW:'+identity,'fact_sha256':digest,'field_name':None}]
    result.extend({'fact_key':'HONOR:'+identity+':'+name,'fact_sha256':sha(row[name]),'field_name':name} for name in flags if row.get(name) is not None and row[name]>0)
    return result


def fingerprint(table,row):
    from schema_model import TABLES
    spec=TABLES[table]
    if table=='season_record_entries':
        names='source_row_index source_first_name source_last_name native_value_word_u32 packed_date_raw native_category_code native_player_id_raw flags_raw'.split()
    elif table=='native_player_stat_observations':names=['source_stat_index','stat_year']+[c.name for c in spec.columns if c.source.startswith('CURRENT_PLAYERSTATDATA.')]
    elif table=='native_coach_stat_observations':names=['source_stat_index','stat_year']+[c.name for c in spec.columns if c.source.startswith('CURRENT_NATIVE.COACHSTATDATA.')]
    elif table=='native_league_history_observations':names=[c.name for c in spec.columns if c.name not in (spec.key,'unit_id','award_id','award_link_status')]
    elif table=='native_award_matrix_observations':names=['award_slot_index','recipient_slot_index','native_player_index_raw']
    else:names=[c.name for c in spec.columns if c.name not in (spec.key,'unit_id','source_history_id')]
    digest=sha({n:row.get(n) for n in names})
    # Raw Native rows are source observations, not canonical finalized awards.
    # Changed source states append new observations. Canonical award identities
    # remain frozen: another value under their stable key is a conflict.
    key=str(row[spec.key]) if table in CANONICAL else digest
    return key,digest


def baseline_row(conn,family,year):
    return conn.execute('''SELECT u.unit_id,u.observed_at FROM capture_units u JOIN capture_runs r USING(run_id)
        WHERE u.unit_status='success' AND r.source_grade='LIVE_READ' AND r.refresh_family=? AND r.refresh_period_year=?
        AND r.refresh_kind='BASELINE' ORDER BY u.observed_at,u.unit_id LIMIT 1''',(family,year)).fetchone()


def addition_plan(conn,payload):
    """Pure SQL-side accepted-fact idempotency; NOT a Native read optimization."""
    from schema_model import TABLES
    family=payload.get('refresh_family');kind=payload.get('refresh_kind','BASELINE' if family else None)
    if not family or kind!='ADDITION':return payload.get('facts',{}),[]
    baseline=payload['refresh_baseline_unit_id'];facts={name:[dict(r) for r in rows] for name,rows in payload.get('facts',{}).items()};claims=[]
    accepted=baseline_row(conn,family,payload['refresh_period_year'])
    if accepted is None or accepted['unit_id']!=baseline:raise ValueError('annual addition baseline family/year does not match')
    if set(facts)-set(PRIMARY_TABLES[family])-set(CONTEXT_TABLES[family]):raise ValueError('annual addition includes an unrelated fact family')
    raw_count=sum(len(facts.get(name,[])) for name in PRIMARY_TABLES[family] if name not in CANONICAL)
    if raw_count>payload['annual_addition_scope']['requested_records']:raise ValueError('addition exceeds evidenced Native record selection')
    field_selection=payload['annual_addition_scope'].get('field_selection')
    if field_selection is not None and (not isinstance(field_selection,list) or not 1<=len(field_selection)<=64 or any(not isinstance(name,str) or name not in allowed_native_fields(family) for name in field_selection) or len(set(field_selection))!=len(field_selection)):raise ValueError('annual addition field selection outside public Native family')
    for table in PRIMARY_TABLES[family]:
        selected=[]
        for index,original in enumerate(facts.get(table,[])):
            row=dict(original);row.setdefault(TABLES[table].key,payload['unit_id']+':'+table+':'+str(index));candidates=_row_claims(table,row);novel=[];flags=honor_columns(table)
            for item in candidates:
                old=conn.execute('SELECT fact_sha256 FROM annual_fact_claims WHERE baseline_unit_id=? AND table_name=? AND fact_key=?',(baseline,table,item['fact_key'])).fetchone()
                if old:
                    if old['fact_sha256']!=item['fact_sha256'] and (table in CANONICAL or item['field_name'] is not None):raise sqlite3.IntegrityError('frozen annual fact conflict; quarantine required')
                    continue
                novel.append(item)
            # Zero is not a newly observed honor. Retraction/change of an already
            # claimed positive value is a frozen-source-fact conflict, not a new award.
            if flags:
                identity=sha([row.get('source_stat_index'),row.get('stat_year')])
                for name in flags:
                    if row.get(name)!=0:continue
                    if conn.execute('SELECT 1 FROM annual_fact_claims WHERE baseline_unit_id=? AND table_name=? AND fact_key=?',(baseline,table,'HONOR:'+identity+':'+name)).fetchone():raise sqlite3.IntegrityError('frozen annual fact conflict; quarantine required')
                if field_selection is not None:
                    # Existing rows can also receive evidence-backed missing/new
                    # raw counter values, explicitly selected by the request.
                    # Values remain typed columns; this ledger stores only their
                    # identity/hash. Default award additions do not refresh counters.
                    if not any(item['field_name'] is None for item in novel):novel=[item for item in novel if item['field_name'] in field_selection]
                    known=_known_values(conn,table,row,baseline,family,payload['refresh_period_year'],field_selection)
                    for name in field_selection:
                        if row.get(name) is None or row[name] in known[name] or (name in flags and row[name]>0):continue
                        value_hash=sha(row[name]);novel.append({'fact_key':'VALUE:'+identity+':'+name+':'+value_hash,'fact_sha256':value_hash,'field_name':name})
            if not novel:continue
            if flags and all(item['field_name'] is not None for item in novel):
                keep={TABLES[table].key,'unit_id','source_stat_index','stat_year','subject_reference_count'}|{item['field_name'] for item in novel}
                row={name:value for name,value in row.items() if name in keep}
                if table=='native_player_stat_observations':row['scoring_identity_status']='SPARSE_NEW_REQUESTED_FIELDS_ONLY; WHOLE_ROW_IDENTITY_NOT_REEVALUATED'
            selected.append(row);claims.extend({'table_name':table,'record_key':row[TABLES[table].key],**item} for item in novel)
        if table in facts:facts[table]=selected
    stat_ids={r['stat_observation_id'] for r in facts.get('native_player_stat_observations',[])}
    coach_ids={r['coach_stat_id'] for r in facts.get('native_coach_stat_observations',[])}
    if family=='NATIVE_HONOR_STATS':
        facts['native_player_stat_links']=[r for r in facts.get('native_player_stat_links',[]) if r.get('stat_observation_id') in stat_ids]
        subjects={r['player_source_id'] for r in facts['native_player_stat_links']};facts['native_player_sources']=[r for r in facts.get('native_player_sources',[]) if r.get('player_source_id') in subjects]
        entities={r.get('player_id') for r in facts['native_player_sources']};facts['native_identity_links']=[r for r in facts.get('native_identity_links',[]) if r.get('entity_id') in entities]
    if family=='STAFF_SEASON_HISTORY':
        facts['native_staff_stat_links']=[r for r in facts.get('native_staff_stat_links',[]) if r.get('coach_stat_id') in coach_ids]
        subjects={r['history_subject_id'] for r in facts['native_staff_stat_links']};facts['native_staff_history_subjects']=[r for r in facts.get('native_staff_history_subjects',[]) if r.get('history_subject_id') in subjects]
    # A targeted adapter carries only the identity/source context for selected
    # rows. Exact repeated proposals create no new unit, context or domain rows.
    return facts,claims


def insert_claims(conn,unit,baseline,family,year,claims):
    from engine import _insert
    for item in claims:
        record={'claim_id':'annual-claim:'+sha([baseline,item['table_name'],item['fact_key']]),'unit_id':unit,
            'baseline_unit_id':baseline,'refresh_family':family,'refresh_period_year':year,**item}
        _insert(conn,'annual_fact_claims',record)


def index_baseline(conn,unit,family,year):
    from schema_model import TABLES,ident
    claims=[]
    for table in PRIMARY_TABLES[family]:
        for source in conn.execute('SELECT * FROM '+ident(table)+' WHERE unit_id=?',(unit,)):
            row=dict(source)
            for item in _row_claims(table,row):
                if conn.execute('SELECT 1 FROM annual_fact_claims WHERE baseline_unit_id=? AND table_name=? AND fact_key=?',(unit,table,item['fact_key'])).fetchone():continue
                claims.append({'table_name':table,'record_key':row[TABLES[table].key],**item})
    insert_claims(conn,unit,unit,family,year,claims)


def backfill_baselines(conn):
    rows=conn.execute("SELECT u.unit_id,r.refresh_family,r.refresh_period_year FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.unit_status='success' AND r.source_grade='LIVE_READ' AND r.refresh_kind='BASELINE'").fetchall()
    for row in rows:index_baseline(conn,row['unit_id'],row['refresh_family'],row['refresh_period_year'])
