import hashlib,json,sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from live_world import _json,read_binding,bound_database,upgrade_bound_save
run=Path(__file__).resolve().parent;save=run/'world-saves/nba2k22_test_01';out=run/'player-skill-migration-v16';out.mkdir(exist_ok=False)
binding,_=read_binding(save,'MyLEAGUE0003');old=bound_database(save,binding);before=hashlib.sha256(old.read_bytes()).hexdigest()
_json(out/'migration-start.json',{'old_file':old.name,'old_sha256':before})
upgrade=upgrade_bound_save(save,'MyLEAGUE0003');new=save/upgrade['database_file'];tables={};total=0
with connect(old,True) as a,connect(new,True) as b:
    b.execute('ATTACH DATABASE ? AS prior',(old.as_uri()+'?mode=ro',))
    for name, in a.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
        if name=='saves':continue
        cols=[r[1] for r in a.execute(f'PRAGMA table_info("{name}")')];key=cols[0];projection=','.join('t."'+col+'"' for col in cols)
        def digest(conn,query):
            h=hashlib.sha256();count=0
            for row in conn.execute(query):h.update(repr(tuple(row)).encode());h.update(b'\n');count+=1
            return count,h.hexdigest()
        source=digest(a,f'SELECT {projection} FROM "{name}" t ORDER BY t."{key}"')
        target=digest(b,f'SELECT {projection} FROM main."{name}" t JOIN prior."{name}" p ON p."{key}"=t."{key}" ORDER BY t."{key}"')
        if source!=target:raise RuntimeError('old data changed: '+name)
        tables[name]={'preserved_rows':source[0],'old_columns_sha256':source[1]};total+=source[0]
    if b.execute('PRAGMA foreign_key_check').fetchall():raise RuntimeError('FK error')
if hashlib.sha256(old.read_bytes()).hexdigest()!=before:raise RuntimeError('old file changed')
_json(out/'migration-report.json',{'status':'REAL_BOUND_V15_TO_V16_OLD_ROWS_PRESERVED','upgrade':upgrade,'old_database_sha256':before,'new_database_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),
    'preserved_rows':total,'tables':tables,'native_save_writes':False})
print(json.dumps({'status':'REAL_BOUND_V15_TO_V16_OLD_ROWS_PRESERVED','preserved_rows':total,'old_sha256':before}))
