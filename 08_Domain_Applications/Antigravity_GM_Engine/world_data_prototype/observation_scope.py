"""Read-only historical projections over a fixed committed observation ledger."""
from contextlib import contextmanager,closing
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
from engine import connect as open_database
from schema_model import TABLES,VERSION,ident

_CURRENT=ContextVar('world_observation_scope',default=None)

def utc_stamp(value):
    if not isinstance(value,str):raise ValueError('observation cutoff requires a timezone-aware ISO timestamp')
    try:
        parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
        if parsed.utcoffset() is None:raise ValueError('timezone required')
        return parsed.astimezone(timezone.utc).isoformat(timespec='microseconds')
    except (ValueError,OverflowError) as error:raise ValueError('observation cutoff requires a timezone-aware ISO timestamp') from error

@dataclass(frozen=True)
class ObservationScope:
    database:Path
    observed_through:str
    save_id:str
    schema_version:int
    unit_ids:tuple[str,...]

    @property
    def fingerprint(self):
        raw=json.dumps([self.save_id,self.schema_version,self.observed_through,self.unit_ids],separators=(',',':')).encode();return hashlib.sha256(raw).hexdigest()

    def metadata(self):return {'time_basis':'CAPTURE_OBSERVED_AT_NOT_GAME_DATE','observed_through':self.observed_through,'save_id':self.save_id,'schema_version':self.schema_version,'committed_success_units':len(self.unit_ids),'scope_sha256':self.fingerprint}

def current_scope():return _CURRENT.get()

@contextmanager
def observed_as_of(database,observed_through):
    """Freeze eligible committed unit IDs once, including nested query calls."""
    database=Path(database).resolve();cutoff=utc_stamp(observed_through)
    with closing(open_database(database,True)) as conn:
        conn.execute('BEGIN');header=conn.execute('SELECT save_id,schema_version FROM saves WHERE singleton=1').fetchone()
        if header is None or header['schema_version']!=VERSION:raise ValueError('copy-upgrade facts to the current schema before historical queries')
        units=tuple(sorted(row['unit_id'] for row in conn.execute("SELECT unit_id,observed_at FROM capture_units WHERE unit_status='success'") if utc_stamp(row['observed_at'])<=cutoff))
        scope=ObservationScope(database,cutoff,header['save_id'],header['schema_version'],units)
    token=_CURRENT.set(scope)
    try:yield scope
    finally:_CURRENT.reset(token)

def query_connection(path,readonly=False):
    scope=current_scope()
    if scope is None:return open_database(path,readonly)
    if not readonly or Path(path).resolve()!=scope.database:raise ValueError('historical queries require the scoped read-only fact database')
    conn=open_database(path,True)
    try:
        conn.create_function('world_observation_utc',1,utc_stamp,deterministic=True)
        conn.execute('CREATE TEMP TABLE "__observation_units" (unit_id TEXT PRIMARY KEY) WITHOUT ROWID')
        conn.executemany('INSERT INTO "__observation_units" VALUES(?)',((key,) for key in scope.unit_ids));conn.commit()
        spec=TABLES['capture_units'];columns=','.join('world_observation_utc(m.observed_at) AS observed_at' if c.name=='observed_at' else 'm.'+ident(c.name) for c in spec.columns)
        conn.execute('CREATE TEMP VIEW capture_units AS SELECT '+columns+' FROM main.capture_units m JOIN "__observation_units" pin ON pin.unit_id=m.unit_id')
        for name,spec in TABLES.items():
            if name=='capture_units':continue
            if 'unit_id' in {c.name for c in spec.columns}:
                conn.execute('CREATE TEMP VIEW '+ident(name)+' AS SELECT m.* FROM main.'+ident(name)+' m WHERE EXISTS(SELECT 1 FROM capture_units u WHERE u.unit_id=m.unit_id)')
        spec=TABLES['capture_runs'];columns=','.join('world_observation_utc(m.observed_at) AS observed_at' if c.name=='observed_at' else 'm.'+ident(c.name) for c in spec.columns)
        conn.execute('CREATE TEMP VIEW capture_runs AS SELECT '+columns+' FROM main.capture_runs m WHERE EXISTS(SELECT 1 FROM capture_units u WHERE u.run_id=m.run_id)')
        for entity in ('games','players','staff_members','draft_pick_assets','teams','seasons'):
            key=TABLES[entity].key;clauses=[]
            for name,spec in TABLES.items():
                if not spec.public or 'unit_id' not in {c.name for c in spec.columns}:continue
                for column in spec.columns:
                    if column.ref==entity+'('+key+')':clauses.append('EXISTS(SELECT 1 FROM '+ident(name)+' v WHERE v.'+ident(column.name)+'=e.'+ident(key)+')')
            if entity=='teams':clauses.append('EXISTS(SELECT 1 FROM games g WHERE g.home_team_id=e.team_id OR g.away_team_id=e.team_id)')
            if entity=='seasons':clauses.extend(('EXISTS(SELECT 1 FROM capture_runs r WHERE r.season_id=e.season_id)','EXISTS(SELECT 1 FROM games g WHERE g.season_id=e.season_id)'))
            conn.execute('CREATE TEMP VIEW '+ident(entity)+' AS SELECT e.* FROM main.'+ident(entity)+' e WHERE '+(' OR '.join(clauses) if clauses else '0'))
        return conn
    except BaseException:
        conn.close();raise

PUBLIC_QUERIES=frozenset(('history','history_page','player_card','staff_card','team_card','prospect_card','market_snapshot','native_honors','native_player_seasons','record_book','settings_snapshot','rules_snapshot','planning_snapshot','gameplan_card','game_box','schedule','player_badges','player_play_types','native_player_details','native_player_state','native_player_skills','native_affiliations','awards','league_history','native_news','native_transactions','export_jsonl','season_summary','player_seasons','league_calendar','game_mode','current_period_stats'))

PUBLIC_QUERIES=PUBLIC_QUERIES|{'native_team_finance','team_lineups','native_player_rotation','native_staff','staff_team_slots','native_staff_history','current_coach_stats'}
PUBLIC_QUERIES=PUBLIC_QUERIES|{'league_standings','player_leaderboard'}

def query_at(database,observed_through,query_name,*args,**kwargs):
    if query_name not in PUBLIC_QUERIES:raise PermissionError('unsupported historical public query')
    import query
    with observed_as_of(database,observed_through) as scope:
        result=getattr(query,query_name)(database,*args,**kwargs)
        return {'observation_scope':scope.metadata(),'result':result}
