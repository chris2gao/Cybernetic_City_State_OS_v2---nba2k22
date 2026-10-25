"""Owner-only fact backup, recovery and measured storage; never opens the game."""
from contextlib import closing
from datetime import datetime,timezone
import hashlib,json,math,os,shutil,sqlite3,time
from pathlib import Path
from engine import connect
from schema_model import VERSION,ident

FORMAT='WORLD_FACT_BACKUP_V1'

def file_sha256(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as source:
        while block:=source.read(4*1024*1024):digest.update(block)
    return digest.hexdigest()

def _encoded(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),sort_keys=True,allow_nan=False).encode('utf-8')

def _write_json(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as target:
        json.dump(value,target,ensure_ascii=False,indent=2,allow_nan=False);target.write('\n');target.flush();os.fsync(target.fileno())

def _header(conn):
    rows=conn.execute('SELECT save_id,schema_version FROM saves WHERE singleton=1').fetchall();version=conn.execute('PRAGMA user_version').fetchone()[0]
    if len(rows)!=1 or not 1<=version<=VERSION or rows[0]['schema_version']!=version:raise ValueError('unsupported or inconsistent fact database header')
    if conn.execute('SELECT count(*) FROM saves').fetchone()[0]!=1:raise ValueError('fact database must identify exactly one independent save')
    return {'save_id':rows[0]['save_id'],'schema_version':version}

def inventory(path):
    """Stable complete logical fingerprints, including owner ledgers and schema."""
    with closing(connect(path,True)) as conn:
        conn.execute('BEGIN');header=_header(conn)
        if conn.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or conn.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('fact database integrity/FK failure')
        schema=[tuple(r) for r in conn.execute("SELECT type,name,tbl_name,sql FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name")]
        tables={}
        for name, in conn.execute("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
            columns=list(conn.execute('PRAGMA table_info('+ident(name)+')'));keys=[r['name'] for r in sorted(columns,key=lambda r:r['pk']) if r['pk']]
            if not keys:raise ValueError('fact table lacks stable primary key: '+name)
            digest=hashlib.sha256();count=0
            for row in conn.execute('SELECT * FROM '+ident(name)+' ORDER BY '+','.join(ident(key) for key in keys)):
                digest.update(_encoded(list(row)));digest.update(b'\n');count+=1
            tables[name]={'rows':count,'columns':[r['name'] for r in columns],'logical_sha256':digest.hexdigest()}
        return {**header,'schema_sha256':hashlib.sha256(_encoded(schema)).hexdigest(),'tables':tables,'integrity':'ok','foreign_key_errors':0}

def backup_facts(database,new_output_directory,*,max_seconds=300):
    if isinstance(max_seconds,bool) or not isinstance(max_seconds,(int,float)) or not math.isfinite(max_seconds) or max_seconds<=0:raise ValueError('positive finite backup duration required')
    database=Path(database).resolve();out=Path(new_output_directory).resolve();start=time.monotonic();out.mkdir(parents=True,exist_ok=False);pending=out/'facts.pending.sqlite';pending.touch(exist_ok=False)
    try:
        with closing(connect(database,True)) as source,closing(connect(pending)) as target:
            expected=_header(source);progress={'callbacks':0,'pages_total':None}
            def step(status,remaining,total):
                progress['callbacks']+=1;progress['pages_total']=total
                if time.monotonic()-start>max_seconds:raise TimeoutError('fact backup exceeded caller duration; no complete manifest published')
            source.backup(target,pages=256,progress=step,sleep=0.05)
        with pending.open('r+b') as stream:os.fsync(stream.fileno())
        snapshot=inventory(pending)
        if any(snapshot[key]!=expected[key] for key in expected):raise ValueError('snapshot identity/schema changed')
        final=out/'facts.sqlite';pending.rename(final)
        manifest={'format':FORMAT,'status':'COMPLETE_FACT_DATABASE_SNAPSHOT','created_at':datetime.now(timezone.utc).isoformat(),'database_file':'facts.sqlite',
            'sha256':file_sha256(final),'byte_count':final.stat().st_size,'inventory':snapshot,'elapsed_seconds':time.monotonic()-start,'backup_progress':progress,
            'source_access':'SQLITE_READ_ONLY_BACKUP_API','source_artifact_files_included':False,'scope':'FACT_DATABASE_ONLY; source ledger retained, external raw evidence must be retained separately',
            'game_access':False,'active_save_binding_changed':False}
        _write_json(out/'manifest.json',manifest);return manifest
    except BaseException as error:
        _write_json(out/'failure.json',{'status':'INCOMPLETE_BACKUP_NOT_RESTORABLE','error_type':type(error).__name__,'reason':str(error),'game_access':False});raise

def validate_backup(directory,*,expected_save_id):
    if not isinstance(expected_save_id,str) or not expected_save_id:raise ValueError('explicit expected save identity required')
    directory=Path(directory).resolve();manifest=json.loads((directory/'manifest.json').read_bytes())
    if manifest.get('format')!=FORMAT or manifest.get('status')!='COMPLETE_FACT_DATABASE_SNAPSHOT' or manifest.get('database_file')!='facts.sqlite':raise ValueError('incomplete or unsupported backup manifest')
    if manifest.get('inventory',{}).get('save_id')!=expected_save_id:raise ValueError('backup belongs to a different save')
    database=directory/'facts.sqlite'
    if database.stat().st_size!=manifest.get('byte_count') or file_sha256(database)!=manifest.get('sha256'):raise ValueError('backup file size/hash mismatch')
    actual=inventory(database)
    if actual!=manifest['inventory']:raise ValueError('backup logical inventory/schema mismatch')
    return manifest

def restore_facts(backup_directory,new_database,*,expected_save_id):
    """Restore to an exclusive NEW candidate, never replace or rebind active facts."""
    start=time.monotonic();manifest=validate_backup(backup_directory,expected_save_id=expected_save_id);target=Path(new_database).resolve();target.parent.mkdir(parents=True,exist_ok=True)
    source=Path(backup_directory).resolve()/'facts.sqlite'
    with source.open('rb') as src,target.open('xb') as dst:
        shutil.copyfileobj(src,dst,4*1024*1024);dst.flush();os.fsync(dst.fileno())
    if file_sha256(target)!=manifest['sha256'] or inventory(target)!=manifest['inventory']:raise ValueError('restored candidate failed complete hash/inventory validation')
    return {'status':'VERIFIED_NEW_FACT_DATABASE_RECOVERY_CANDIDATE','save_id':expected_save_id,'schema_version':manifest['inventory']['schema_version'],
        'sha256':manifest['sha256'],'byte_count':target.stat().st_size,'table_count':len(manifest['inventory']['tables']),
        'rows_verified':sum(t['rows'] for t in manifest['inventory']['tables'].values()),'elapsed_seconds':time.monotonic()-start,
        'game_access':False,'active_save_binding_changed':False,'source_artifact_files_restored':False,'live_game_alignment':'NOT_INFERRED_FROM_BACKUP'}

def storage_profile(database):
    """Read-only measured page/row inventory; no inferred 100-year pass verdict."""
    database=Path(database).resolve();start=time.monotonic()
    with closing(connect(database,True)) as conn:
        conn.execute('BEGIN');header=_header(conn);tables={};objects={r['name']:dict(r) for r in conn.execute('SELECT name,type,tbl_name FROM sqlite_schema')}
        page_size=conn.execute('PRAGMA page_size').fetchone()[0];page_count=conn.execute('PRAGMA page_count').fetchone()[0];free=conn.execute('PRAGMA freelist_count').fetchone()[0]
        source_units=[dict(r) for r in conn.execute('''SELECT u.unit_id,u.run_id,u.source_key,u.observed_at,r.source_grade FROM capture_units u JOIN capture_runs r USING(run_id)
            WHERE u.unit_status='success' AND NOT EXISTS(SELECT 1 FROM capture_units later WHERE later.unit_status='success' AND later.source_key=u.source_key AND (later.observed_at>u.observed_at OR (later.observed_at=u.observed_at AND later.unit_id>u.unit_id))) ORDER BY u.source_key''')]
        for name, in conn.execute("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
            columns={r['name'] for r in conn.execute('PRAGMA table_info('+ident(name)+')')};row_count=conn.execute('SELECT count(*) FROM '+ident(name)).fetchone()[0]
            tables[name]={'rows':row_count,'table_bytes':None,'index_bytes':None,'latest_source_unit_rows':{}}
            if 'unit_id' in columns:
                for unit in source_units:
                    n=conn.execute('SELECT count(*) FROM '+ident(name)+' WHERE unit_id=?',(unit['unit_id'],)).fetchone()[0]
                    if n:tables[name]['latest_source_unit_rows'][unit['source_key']]=n
            elif name=='capture_runs':
                for unit in source_units:tables[name]['latest_source_unit_rows'][unit['source_key']]=1
        try:
            usage=[dict(r) for r in conn.execute('SELECT name,sum(pgsize) AS bytes,count(*) AS pages FROM dbstat GROUP BY name')];dbstat_status='MEASURED_SQLITE_DBSTAT'
            for table in tables.values():table['table_bytes']=0;table['index_bytes']=0
            for item in usage:
                obj=objects.get(item['name']);owner=obj['tbl_name'] if obj else None
                if owner in tables:tables[owner]['index_bytes' if obj['type']=='index' else 'table_bytes']+=item['bytes']
        except sqlite3.OperationalError:
            usage=[];dbstat_status='DBSTAT_UNAVAILABLE; per-table byte allocation is unknown'
        for table in tables.values():
            total=None if table['table_bytes'] is None else table['table_bytes']+table['index_bytes'];table['allocated_bytes']=total;table['allocated_bytes_per_existing_row']=total/table['rows'] if table['rows'] and total is not None else None
        source_bytes={u['source_key']:conn.execute('SELECT coalesce(sum(byte_count),0) FROM source_artifacts WHERE unit_id=?',(u['unit_id'],)).fetchone()[0] for u in source_units}
        missing_sizes={u['source_key']:conn.execute('SELECT count(*) FROM source_artifacts WHERE unit_id=? AND byte_count IS NULL',(u['unit_id'],)).fetchone()[0] for u in source_units}
        return {**header,'sqlite_version':sqlite3.sqlite_version,'database_file_bytes':database.stat().st_size,'page_size':page_size,'page_count':page_count,'freelist_pages':free,
            'allocated_page_bytes':page_size*page_count,'journal_mode':conn.execute('PRAGMA journal_mode').fetchone()[0],
            'sidecar_bytes':{suffix:Path(str(database)+suffix).stat().st_size if Path(str(database)+suffix).exists() else 0 for suffix in ('-wal','-shm','-journal')},
            'dbstat_status':dbstat_status,'database_objects':usage,'tables':tables,'latest_source_units':source_units,'latest_source_raw_artifact_bytes':source_bytes,'latest_source_artifact_missing_byte_counts':missing_sizes,
            'elapsed_seconds':time.monotonic()-start,'scope':'MEASURED_CURRENT_DATABASE; not a 100-season workload or resource-budget acceptance','game_access':False}

def project_observations(profile,*,source_calls_per_season,years):
    """Explicit fixed-population planning model, separate from actual measurement."""
    if type(years) is not int or years<1:raise ValueError('positive integer years required')
    known={u['source_key'] for u in profile['latest_source_units']}
    if set(source_calls_per_season)-known or any(type(n) is not int or n<0 for n in source_calls_per_season.values()):raise ValueError('explicit known source frequencies required')
    if profile['dbstat_status']!='MEASURED_SQLITE_DBSTAT':raise ValueError('per-table storage unavailable; do not invent a byte projection')
    additions={};estimated=0.0
    for name,table in profile['tables'].items():
        rows=sum(n*source_calls_per_season.get(source,0)*years for source,n in table['latest_source_unit_rows'].items());rate=table['allocated_bytes_per_existing_row']
        if rows:
            if rate is None:raise ValueError('missing measured row allocation for '+name)
            value=rows*rate;additions[name]={'additional_rows':rows,'estimated_additional_allocated_bytes':value};estimated+=value
    return {'status':'LINEAR_FIXED_POPULATION_PROJECTION_NOT_EXECUTED_100_SEASON_TEST','years':years,'source_calls_per_season':source_calls_per_season,
        'estimated_additional_database_bytes':estimated,'estimated_total_database_bytes':profile['allocated_page_bytes']+estimated,
        'recorded_raw_artifact_bytes_at_same_frequencies':sum(profile['latest_source_raw_artifact_bytes'][s]*n*years for s,n in source_calls_per_season.items()),
        'tables':additions,'excluded_costs':['population/draft/retirement and season/identity registry growth','future fields/text/identity transitions','B-tree allocation changes','backup retention policy and temporary recovery copies','raw artifact compression/retention changes and missing source byte counts','query/write latency extrapolation'],
        'capacity_pass':False,'human_resource_budget':'NOT_SPECIFIED'}
