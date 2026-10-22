"""Snapshot-bound business projections and a restricted SELECT sandbox."""
import base64
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import time

from . import AccessError, QUERY_VERSION
from .finance import semantics
from .snapshots import DB_NAMES, read_json, identifier, load_snapshot, source_binding

DEFAULTS = {
    'coach_traits': ('team_id','traits','source_status'),
    'team_stats': ('team_id','team','season_year','totals','source_status'),
    'teams': ('team_id','team','total_wins','total_losses'),
    'players': ('identity','name','team','position','salary','years_left'),
    'pool': ('identity','name','position','draft_year','roster_status','historical_rookie'),
    'staff': ('identity','name','team','role','candidate_position','mapping_status'),
    'coaching': ('team','coach','system','freelance','sliders'),
    'defense': ('team_id','opponent_team_id','values','mixed_fields','status'),
    'picks': ('asset_id','owner','original_team_id','draft_year','draft_round','trade_eligible'),
    'finance': ('team','total_salary','payroll','budget','cash','cash_signed32_hypothesis','financial_eligibility'),
    'finance_semantics': ('field','offset','encoding','unit','time_scope','financial_eligibility'),
    'native_objects': ('identity','object_key','target_kind','team_id','selector','native_identity','source_status'),
    'native_books': ('identity','name','enum_id','index','unique_id'),
    'native_context': ('identity','save_id','save_instance_id','generation_id','registry_version','team_directory','coverage'),
}
for _domain in ('world','gameplay','tactics','tendency','training','personal_defense','rotation'):
    DEFAULTS[_domain] = ('identity','object_key','team_id','player_identity','side','field_key','value','source_status')
JSON_FIELDS = {'attributes','contract','season_totals','totals','system','freelance','sliders','values','mixed_fields','readiness','value','selector','native_identity','field_keys','team_directory','coverage','play_crc_slots','traits'}
FUNCTIONS = {'count','sum','avg','min','max','total','round','abs','coalesce','ifnull','nullif',
             'lower','upper','length','substr','like','instr','in','json_extract','json_remove','json_object',
             'json_array','json_valid','rookie_marker','trim','typeof','row_number','rank','dense_rank'}


def sealed_coach_traits(raw_hex):
    """Reuse DEV12's existing reader on one sealed DEV14 record, never a process."""
    from tactical_reader import read_coach_attributes
    raw=bytes.fromhex(raw_hex or '')
    if len(raw)!=0x160:
        return None
    class SealedRecord:
        def read_bytes(self, offset, size):
            return raw[offset:offset+size]
    result=read_coach_attributes(SealedRecord(),0)
    return json.dumps({k:result[k] for k in ('system_proficiencies','staff_ratings','max_staff_ratings')})


class QuerySession:
    def __init__(self, root, published, career, batch=None):
        self.career = identifier(career)
        if batch is None:
            batch = read_json(Path(published)/'saves'/career/'latest.json')['batch_id']
        self.batch = identifier(batch)
        self.directory = Path(root).resolve()/career/batch
        self.record = load_snapshot(root, career, batch)
        self.binding = source_binding(self.record, published, career, batch)
        mask=self.record['source_manifest'].get('player_potential_mask',{})
        self.binding['player_potential_visibility']='MASKED' if mask.get('potential_mask_version')=='potential_v1' else 'UNMASKED_HISTORICAL_EXCLUDED_FROM_GM'
        self.binding['production_gm_eligible'] = self.binding['production_gm_eligible'] and self.binding['player_potential_visibility']=='MASKED'
        self.c = sqlite3.connect(':memory:', timeout=2, uri=True)
        self.c.row_factory = sqlite3.Row
        try:
            for name, alias in zip(DB_NAMES, ('facts','pooldb')):
                path = (self.directory/name).as_uri()+'?mode=ro'
                self.c.execute('ATTACH DATABASE ? AS '+alias,(path,))
            self.c.enable_load_extension(False)
            self.c.create_function('rookie_marker',1,lambda b: int(bool(b and len(b)>0x70 and b[0x70]&0xE0==0xE0)), deterministic=True)
            self.c.create_function('sealed_coach_traits',1,sealed_coach_traits,deterministic=True)
            if self.c.execute("SELECT json_extract('{\"ok\":1}', '$.ok')").fetchone()[0] != 1:
                raise AccessError('BLOCKED_LOCAL_DB_ACCESS','SQLite JSON1 is required')
            self._views()
            self.columns = {v: tuple(r[1] for r in self.c.execute('PRAGMA table_info(q_'+v+')')) for v in DEFAULTS}
            self._raw_tables = {r[0].lower() for db in ('facts','pooldb','temp')
                                for r in self.c.execute('SELECT name FROM '+db+".sqlite_master WHERE type='table'")}
            self.c.execute('SELECT team_id FROM q_defense LIMIT 1').fetchone()
            self.available = {v: self.c.execute('SELECT 1 FROM q_'+v+' LIMIT 1').fetchone() is not None for v in DEFAULTS}
            self.c.execute('PRAGMA query_only=ON')
            for key,value in ((sqlite3.SQLITE_LIMIT_LENGTH,1_000_000), (sqlite3.SQLITE_LIMIT_SQL_LENGTH,16000),
                              (sqlite3.SQLITE_LIMIT_EXPR_DEPTH,64), (sqlite3.SQLITE_LIMIT_VARIABLE_NUMBER,256),
                              (sqlite3.SQLITE_LIMIT_COMPOUND_SELECT,10)):
                self.c.setlimit(key,value)
            self.c.set_authorizer(self._authorize)
        except Exception:
            self.c.close()
            raise

    def close(self):
        self.c.close()

    def require_gm_sanitized(self):
        """GM-role access policy; old audited M0 owner reads stay read-only."""
        mask = self.record['source_manifest'].get('player_potential_mask',{})
        if mask.get('potential_mask_version') != 'potential_v1' or mask.get('source_role') != 'GM_SANITIZED':
            raise AccessError('UNMASKED_HISTORICAL_BATCH_EXCLUDED_FROM_GM',
                              'GM requires a new potential_v1 sanitized capture; do not rewrite sealed history')
        return mask

    def _views(self):
        sid = "'"+self.binding['snapshot_id'].replace("'","''")+"'"
        tables={db:{r[0] for r in self.c.execute('SELECT name FROM '+db+".sqlite_master WHERE type='table'")} for db in ('facts','pooldb')}
        ingest = read_json(self.directory/'ingest_manifest.json')
        def view(name, sql):
            unavailable=any(table not in tables[db] for db,table in re.findall(r'\b(facts|pooldb)\.(\w+)',sql))
            if name in ('coaching','defense') and ingest.get('quality_metrics',{}).get('coaching_tactics',{}).get('profile')!=1:
                unavailable=True
            if unavailable:
                sql='SELECT '+','.join('NULL AS "'+f+'"' for f in DEFAULTS[name])+' WHERE 0'
            self.c.execute('CREATE TEMP VIEW q_'+name+' AS '+sql)
        view('teams', f"SELECT team_id,team_abbr AS team,total_wins,total_losses,total_games,win_pct,total_salary FROM facts.team_monthly_stats WHERE snapshot_id={sid}")
        view('team_stats', f"""SELECT s.team_id,t.team_abbr AS team,
            json_extract(s.totals_json,'$.season_year') AS season_year,
            s.totals_json AS totals,'OBSERVED_STATIC_SOURCE' AS source_status
            FROM facts.team_source_stats s JOIN facts.team_monthly_stats t
            ON t.snapshot_id=s.snapshot_id AND t.team_id=s.team_id WHERE s.snapshot_id={sid}""")
        view('players', f"""SELECT d.snapshot_id||':roster:'||d.team_id||':'||d.roster_slot AS identity,
            d.player_name AS name,d.team_id,t.team_abbr AS team,d.pool_slot,
            p.position_name AS position,d.face_id,d.birth_date,
            json_extract(d.details_json,'$.contract.contract_year_1.value') AS salary,
            json_extract(d.details_json,'$.contract.years_left_on_contract.value') AS years_left,
            json_extract(d.details_json,'$.contract') AS contract,
            json_extract(d.details_json,'$.attributes') AS attributes,
            json_extract(d.details_json,'$.season_totals') AS season_totals,
            'EXPIRY_NOT_CERTIFIED' AS expiry_status
            FROM facts.player_source_details d JOIN facts.team_monthly_stats t
            ON t.snapshot_id=d.snapshot_id AND t.team_id=d.team_id
            LEFT JOIN pooldb.player_pool p ON p.slot_id=d.pool_slot WHERE d.snapshot_id={sid}""")
        view('pool', f"""SELECT {sid}||':pool:'||p.slot_id AS identity,p.full_name AS name,
            p.slot_id,p.position_name AS position,p.draft_year,p.draft_round,p.draft_pick,
            p.cyberface_id AS face_id,rookie_marker(p.raw_struct) AS historical_rookie,
            CASE WHEN EXISTS(SELECT 1 FROM facts.player_source_details d WHERE d.snapshot_id={sid} AND d.pool_slot=p.slot_id)
            THEN 'NBA_ROSTER' ELSE 'NOT_ON_OBSERVED_NBA_ROSTER' END AS roster_status,
            json_extract(p.source_details_json,'$.attributes') AS attributes
            FROM pooldb.player_pool p""")
        view('staff', f"""SELECT s.snapshot_id||':staff:'||s.staff_slot AS identity,
            trim(s.first_name||' '||s.last_name) AS name,s.staff_slot,
            CASE WHEN d.team_mapping_status='VERIFIED_RECIPROCAL_TEAM_ROLE' THEN d.team_id END AS team_id,
            CASE WHEN d.team_mapping_status='VERIFIED_RECIPROCAL_TEAM_ROLE' THEN t.team_abbr END AS team,
            CASE WHEN d.team_mapping_status='VERIFIED_RECIPROCAL_TEAM_ROLE' THEN d.role END AS role,
            d.team_mapping_status AS mapping_status,
            json_extract(d.details_json,'$.fields.vitals.position.label') AS candidate_position,
            json_extract(d.details_json,'$.fields.vitals.salary.value') AS salary,
            json_extract(d.details_json,'$.fields.vitals.years_left.value') AS years_left,
            json_extract(d.details_json,'$.fields.attributes') AS attributes
            FROM facts.staff_pool_observations s LEFT JOIN facts.staff_source_details d
            ON d.snapshot_id=s.snapshot_id AND d.staff_slot=s.staff_slot
            LEFT JOIN facts.team_monthly_stats t ON t.snapshot_id=s.snapshot_id AND t.team_id=d.team_id
            WHERE s.snapshot_id={sid} AND trim(s.first_name||' '||s.last_name)<>''""")
        view('coaching', f"""SELECT c.team_id,t.team_abbr AS team,
            trim(json_extract(c.observation_json,'$.coach_identity.first_name')||' '||json_extract(c.observation_json,'$.coach_identity.last_name')) AS coach,
            json_remove(json_extract(c.observation_json,'$.values'),'$.SimPace','$.SimPress','$.SimHelpDef','$.SimOffReb','$.SimDefReb') AS "values",
            json_object('PreferredSystem',json_extract(c.observation_json,'$.values.PreferredSystem'),
                        'ActiveSystem',json_extract(c.observation_json,'$.values.ActiveSystem')) AS system,
            json_array(json_extract(c.observation_json,'$.values.FreelanceType'),json_extract(c.observation_json,'$.values.FreelanceType2'),
                       json_extract(c.observation_json,'$.values.FreelanceType3'),json_extract(c.observation_json,'$.values.FreelanceType4')) AS freelance,
            json_object('BenchDepth',json_extract(c.observation_json,'$.values.BenchDepth'),
                        'BenchUtilization',json_extract(c.observation_json,'$.values.BenchUtilization'),
                        'RunPlayTendency',json_extract(c.observation_json,'$.values.RunPlayTendency'),
                        'ZoneUsage',json_extract(c.observation_json,'$.values.ZoneUsage'),
                        'Tempo',json_extract(c.observation_json,'$.values.Tempo'),
                        'HelpDefense',json_extract(c.observation_json,'$.values.HelpDefense')) AS sliders,
            json_extract(c.observation_json,'$.readiness') AS readiness
            FROM facts.coaching_team_observations c JOIN facts.team_monthly_stats t
            ON t.snapshot_id=c.snapshot_id AND t.team_id=c.team_id WHERE c.snapshot_id={sid}""")
        view('defense', f"""SELECT c.team_id,t.team_abbr AS team,
            json_extract(g.value,'$.opponent_team_id') AS opponent_team_id,
            json_extract(g.value,'$.overall_defense.values') AS "values",
            json_extract(g.value,'$.overall_defense.mixed_fields') AS mixed_fields,
            json_extract(g.value,'$.overall_defense.status') AS status
            FROM facts.coaching_team_observations c JOIN facts.team_monthly_stats t
            ON t.snapshot_id=c.snapshot_id AND t.team_id=c.team_id,
            json_each(c.observation_json,'$.gameplans') g WHERE c.snapshot_id={sid}""")
        next_year = ingest.get('quality_metrics',{}).get('simple_draft_assets',{}).get('next_draft_year')
        years = tuple(range(next_year,next_year+3)) if type(next_year) is int else ()
        eligible = f"draft_year IN ({','.join(str(y) for y in years)})" if years else 'NULL'
        view('picks', f"""SELECT 'draft_pick:'||draft_year||':'||draft_round||':'||original_owner_team_id AS asset_id,
            asset_slot,current_owner_team_id AS team_id,t.team_abbr AS owner,
            original_owner_team_id AS original_team_id,draft_year,draft_round,mapping_status,
            CASE WHEN mapping_status='VERIFIED_SIMPLE_FUTURE_PICK' THEN {eligible} ELSE NULL END AS trade_eligible
            FROM facts.draft_asset_observations d LEFT JOIN facts.team_monthly_stats t
            ON t.snapshot_id=d.snapshot_id AND t.team_id=d.current_owner_team_id WHERE d.snapshot_id={sid}""")
        view('finance', f"""SELECT team_id,team_abbr AS team,total_salary,payroll,budget,staff_budget,cash,
            CASE WHEN cash>=2147483648 THEN cash-4294967296 ELSE cash END AS cash_signed32_hypothesis,
            monthly_gate_revenue,merch_revenue,media_revenue,'UNKNOWN' AS financial_eligibility
            FROM facts.team_monthly_stats WHERE snapshot_id={sid}""")
        self.c.execute('CREATE TEMP TABLE finance_dictionary(field,offset,encoding,unit,time_scope,evidence,financial_eligibility,usable_as_signing_capacity,evidence_file)')
        self.c.executemany('INSERT INTO finance_dictionary VALUES (?,?,?,?,?,?,?,?,?)', [tuple(r.values()) for r in semantics()])
        view('finance_semantics','SELECT field,offset,encoding,unit,time_scope,evidence,financial_eligibility,usable_as_signing_capacity,evidence_file FROM finance_dictionary')
        view('native_objects',f"""SELECT o.object_key AS identity,o.object_key,
            json_extract(o.object_json,'$.selector.target_kind') AS target_kind,
            json_extract(o.object_json,'$.selector.team_id') AS team_id,
            json_extract(o.object_json,'$.selector.opponent_team_id') AS opponent_team_id,
            json_extract(o.object_json,'$.selector') AS selector,
            json_extract(o.object_json,'$.identity') AS native_identity,
            json_extract(o.object_json,'$.field_keys') AS field_keys,
            json_extract(o.object_json,'$.source_status') AS source_status
            FROM facts.state_io_objects o WHERE o.snapshot_id={sid}""")
        view('native_books',f"""SELECT 'book:'||json_extract(b.value,'$.index')||':'||json_extract(b.value,'$.enum_id')||':'||json_extract(b.value,'$.unique_id') AS identity,
            json_extract(b.value,'$.name') AS name,json_extract(b.value,'$.enum_id') AS enum_id,
            json_extract(b.value,'$.index') AS "index",json_extract(b.value,'$.unique_id') AS unique_id,
            json_extract(b.value,'$.play_crc_slots') AS play_crc_slots
            FROM facts.state_io_captures s,json_each(json_extract(s.metadata_json,'$.source_context.playbooks')) b
            WHERE s.snapshot_id={sid}""")
        view('native_context',f"""SELECT snapshot_id AS identity,save_id,save_instance_id,generation_id,registry_version,
            json_extract(metadata_json,'$.team_directory') AS team_directory,
            json_extract(metadata_json,'$.coverage') AS coverage FROM facts.state_io_captures WHERE snapshot_id={sid}""")
        view('coach_traits',f"""SELECT json_extract(object_json,'$.selector.team_id') AS team_id,
            sealed_coach_traits(json_extract(object_json,'$.raw')) AS traits,
            'STATIC_DEV14_RECORD_EXISTING_DEV12_DECODER' AS source_status FROM facts.state_io_objects
            WHERE snapshot_id={sid} AND json_extract(object_json,'$.selector.target_kind')='COACH_DEFAULT'""")
        for name in ('world','gameplay','tactics','tendency','training','personal_defense','rotation'):
            domain = 'defense' if name=='personal_defense' else name
            predicate = " AND v.target_kind='PERSONAL_DEFENSE'" if name=='personal_defense' else ''
            view(name, f"""SELECT v.object_key||':'||v.field_key AS identity,
                v.object_key,v.team_id,v.opponent_team_id,v.player_identity,v.side,v.slot_index,
                v.field_key,v.value_json AS value,v.source_status,v.registry_version,
                s.save_instance_id,s.generation_id FROM facts.observed_setting_values v
                JOIN facts.state_io_captures s ON s.snapshot_id=v.snapshot_id
                WHERE v.snapshot_id={sid} AND v.domain='{domain}'{predicate}""")

    def _authorize(self, action, arg1, arg2, db, origin):
        if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_RECURSIVE):
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_FUNCTION:
            if arg2=='sealed_coach_traits' and origin=='q_coach_traits':
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_OK if (arg2 or '').lower() in FUNCTIONS else sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_READ:
            # Raw tables/JSON/addresses can only be read through the fixed projections.
            if origin in {'q_'+n for n in DEFAULTS}:
                return sqlite3.SQLITE_OK
            if db == 'temp' and arg1 in {'q_'+n for n in DEFAULTS}:
                return sqlite3.SQLITE_OK
            # SQLite COUNT optimization requests an empty column on an underlying
            # view table with origin=None. User SQL separately forbids all raw
            # identifiers, including quoted forms, before authorization starts.
            if not arg2 and arg1.lower() in self._raw_tables:
                return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY

    def query(self, entity, fields=None, filters=None, limit=20, cursor=None, sql=None, params=None):
        if type(limit) is not int or not 1 <= limit <= 50:
            raise AccessError('INVALID_INPUT','Limit must be 1..50')
        filters = filters or {}
        params = params or []
        if sql is None:
            if entity not in DEFAULTS:
                raise AccessError('INVALID_INPUT','Unknown business projection')
            if not self.available[entity]:
                raise AccessError('UNVERIFIED_FIELD','This snapshot has no observed rows for this source')
            fields = list(fields or DEFAULTS[entity])
            if not fields or any(f not in self.columns[entity] for f in fields):
                raise AccessError('UNVERIFIED_FIELD','Field is unavailable or outside the observed projection')
            conditions, params = [], []
            for key,value in filters.items():
                if key not in self.columns[entity]:
                    raise AccessError('INVALID_INPUT','Unsupported filter')
                if key == 'name':
                    conditions.append('instr(lower(name), lower(?))>0')
                elif value is None:
                    conditions.append('"'+key+'" IS NULL')
                    continue
                else:
                    conditions.append('"'+key+'"=?')
                params.append(value)
            sql = 'SELECT '+','.join('"'+f+'"' for f in fields)+' FROM q_'+entity
            if conditions:
                sql += ' WHERE '+' AND '.join(conditions)
            ordering = 'identity' if 'identity' in self.columns[entity] else ('asset_slot' if entity == 'picks' else ('team_id,opponent_team_id' if entity == 'defense' else ('field' if entity=='finance_semantics' else 'team_id')))
            sql += ' ORDER BY '+ordering
        else:
            if not re.match(r'^\s*SELECT\b',sql,re.I) or ';' in sql or len(sql)>15000 or re.search(r'\bWITH\b',sql,re.I):
                raise AccessError('INVALID_SQL','Only a single bounded SELECT is allowed')
            if '*' in re.sub(r'count\s*\(\s*\*\s*\)','',sql, flags=re.I):
                raise AccessError('INVALID_SQL','Project explicit columns; only COUNT(*) permits a wildcard')
            # Remove comments before recognizing identifiers, so comments cannot
            # disguise an underlying table as an AS alias in the COUNT guard.
            lexical=re.sub(r'/\*.*?\*/|--[^\n]*',' ',sql.lower(),flags=re.S)
            tokens = re.findall(r'[A-Za-z_][A-Za-z_0-9]*',lexical)
            if any(t in self._raw_tables and (i==0 or tokens[i-1]!='as') for i,t in enumerate(tokens)):
                raise AccessError('INVALID_SQL','Only q_* public projections may be queried')
            if not isinstance(params, list) or len(params)>200 or any(type(p) not in (str,int,float,type(None)) for p in params):
                raise AccessError('INVALID_INPUT','SQL params must be a bounded JSON list of scalars')
        fingerprint = hashlib.sha256(json.dumps([self.batch,sql,params,limit],sort_keys=True).encode()).hexdigest()
        offset = 0
        if cursor:
            try:
                token = json.loads(base64.urlsafe_b64decode(cursor.encode()))
                offset = token['offset']
                if token['query'] != fingerprint or type(offset) is not int or not 0<=offset<=10000:
                    raise ValueError()
            except Exception as exc:
                raise AccessError('STALE_OR_MIXED_BATCH','Cursor does not match query and batch') from exc
        deadline = time.monotonic()+2.0
        self.c.set_progress_handler(lambda: int(time.monotonic()>deadline),1000)
        try:
            cur = self.c.execute('SELECT * FROM ('+sql+') LIMIT ? OFFSET ?',(*params,limit+1,offset))
            names = [x[0] for x in cur.description]
            if len(names)>60 or len(set(names))!=len(names) or any(len(n)>80 for n in names):
                raise AccessError('RESULT_LIMIT_REACHED','Too many or duplicate output columns')
            raw = cur.fetchmany(limit+1)
        except sqlite3.Error as exc:
            code = 'QUERY_TIMEOUT' if 'interrupt' in str(exc) else 'INVALID_SQL'
            raise AccessError(code,'SELECT rejected by SQLite read-only sandbox: '+str(exc)[:200]) from exc
        finally:
            self.c.set_progress_handler(None,0)
        rows=[]
        for row in raw[:limit]:
            item=dict(row)
            for key in item:
                if key in JSON_FIELDS and isinstance(item[key],str):
                    item[key]=json.loads(item[key])
            rows.append(item)
        evidence={k: ('CALCULATED_HYPOTHESIS_NOT_OBSERVED' if k=='cash_signed32_hypothesis' else
                      'UNKNOWN' if k in ('financial_eligibility','expiry_status') else
                      'OBSERVED_RAW_WITH_PARTIAL_SEMANTICS' if entity in ('finance','finance_semantics') else
                      'CALCULATED_SQL_PROJECTION_NOT_GAME_OBSERVATION' if entity=='sql' else
                      'UNKNOWN' if rows and all(r[k] is None for r in rows) else
                      'BATCH_LOCAL_IDENTITY' if k=='identity' else
                      'DERIVED_COVERAGE_NOT_FREE_AGENCY' if k=='roster_status' else
                      'OBSERVED_SNAPSHOT_FIELD_OR_NATIVE_DECODE') for k in names}
        result=dict(status='OK',rows=rows,row_count=len(rows),source_binding=self.binding,query_version=QUERY_VERSION,
                    next_cursor=None,truncated=len(raw)>limit,field_evidence=evidence,
                    identity_scope='BATCH_LOCAL_NOT_PERMANENT',
                    ambiguity='MULTIPLE_CANDIDATES' if filters.get('name') and len(rows)>1 else None)
        while len(json.dumps(result,ensure_ascii=False).encode())>17_000 and rows:
            rows.pop()
            result['truncated']=True
        result['row_count']=len(rows)
        if result['truncated']:
            result['status']='RESULT_LIMIT_REACHED'
            if rows and offset+len(rows)<=10000:
                result['next_cursor']=base64.urlsafe_b64encode(json.dumps(dict(query=fingerprint,offset=offset+len(rows))).encode()).decode()
            elif not rows:
                result['message']='One row exceeds output budget; request fewer fields'
        return result
