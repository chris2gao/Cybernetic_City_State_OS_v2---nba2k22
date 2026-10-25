"""Verify the completed copy upgrade, allowing newly seeded dictionary rows."""
import hashlib,json,sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from live_world import _json
run=Path(__file__).resolve().parent;save=run/'world-saves/nba2k22_test_01';out=run/'annual-migration-v11'
old=save/'world-v10.sqlite';new=save/'world-v11.sqlite'
before='99dd75ebf5256d390b2ab7dbee260c003dc2e1e81c2d08a1aa8a5f7c27333a3f'
after=hashlib.sha256(old.read_bytes()).hexdigest()
if before!=after:raise RuntimeError('v10 source no longer matches increment11 delivery hash')
tables={};total=0
with connect(old,True) as a,connect(new,True) as b:
    b.execute('ATTACH DATABASE ? AS prior',(old.resolve().as_uri()+'?mode=ro',))
    for name, in a.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
        if name=='saves':continue
        columns=[r[1] for r in a.execute(f'PRAGMA table_info("{name}")')];key=columns[0]
        projection=','.join('t."'+c+'"' for c in columns)
        q=f'SELECT {projection} FROM "{name}" t ORDER BY t."{key}"'
        target=f'SELECT {projection} FROM main."{name}" t JOIN prior."{name}" p ON t."{key}"=p."{key}" ORDER BY t."{key}"'
        def digest(conn,query):
            h=hashlib.sha256();count=0
            for row in conn.execute(query):h.update(repr(tuple(row)).encode('utf-8'));h.update(b'\n');count+=1
            return count,h.hexdigest()
        source=digest(a,q);copied=digest(b,target)
        if source!=copied:raise RuntimeError('old row or column differs: '+name)
        actual=b.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
        if actual!=source[0] and name!='native_fields':raise RuntimeError('unexpected extra rows: '+name)
        tables[name]={'preserved_rows':source[0],'old_columns_sha256':source[1],'new_catalog_rows':actual-source[0]};total+=source[0]
    if b.execute('PRAGMA foreign_key_check').fetchall():raise RuntimeError('FK errors')
    if b.execute('SELECT count(*) FROM capture_runs WHERE refresh_family IS NOT NULL OR refresh_period_year IS NOT NULL').fetchone()[0]:raise RuntimeError('legacy periods relabelled')
report={'status':'REAL_BOUND_DB_COPY_UPGRADE_AND_OLD_COLUMNS_PRESERVED','source_schema':10,'schema_version':11,
    'old_database_sha256_before':before,'old_database_sha256_after':after,
    'new_database_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'preserved_fact_rows':total,
    'new_catalog_rows':sum(t['new_catalog_rows'] for t in tables.values()),'tables':tables,
    'legacy_annual_periods_relabelled':0,'verification_adjustment':'Initial whole-target comparison detected two expected new native_fields rows; compare all old keys/columns instead.',
    'native_save_writes':False}
_json(out/'migration-report.json',report)
print(json.dumps({k:v for k,v in report.items() if k!='tables'}))
