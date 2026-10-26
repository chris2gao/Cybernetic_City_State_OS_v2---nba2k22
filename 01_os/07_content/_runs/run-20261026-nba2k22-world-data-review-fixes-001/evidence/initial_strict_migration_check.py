"""NEW v25 copy; stream-compare every v24 row/column except version header."""
import hashlib,json,sqlite3,sys,time
from pathlib import Path
root=Path.cwd();run=Path(__file__).resolve().parent;out=run/'evidence';out.mkdir(exist_ok=True)
app=root/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import migrate_database
from schema_model import ident,VERSION
from database_operations import file_sha256
source=root/'01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/_runtime/world-saves/nba2k22_test_01/world-v24.sqlite'
target=run/'_runtime/migration/world-v25.sqlite';target.parent.mkdir(parents=True,exist_ok=True)
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
before=file_sha256(source);assert before=='f76b943e4c716748b4df1c8f6c94779fb57ebb312bbeeb9e4d4dfd97a024b218';assert not target.exists()
start=time.monotonic();migrate_database(source,target)
old=sqlite3.connect(source.as_uri()+'?mode=ro',uri=True);new=sqlite3.connect(target.resolve().as_uri()+'?mode=ro',uri=True)
old.row_factory=new.row_factory=sqlite3.Row;results=[]
for name, in old.execute("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
    info=old.execute('PRAGMA table_info('+ident(name)+')').fetchall();columns=[r['name'] for r in info if not (name=='saves' and r['name']=='schema_version')];keys=[r['name'] for r in info if r['pk']];assert keys
    sql='SELECT '+','.join(ident(c) for c in columns)+' FROM '+ident(name)+' ORDER BY '+','.join(ident(k) for k in keys)
    def scan(conn):
        digest=hashlib.sha256();count=0
        for row in conn.execute(sql):digest.update((json.dumps(list(row),ensure_ascii=False,sort_keys=True,allow_nan=False,separators=(',',':'))+'\n').encode('utf-8'));count+=1
        return count,digest.hexdigest()
    a,b=scan(old),scan(new);assert a==b,name;results.append({'table':name,'old_columns_compared':len(columns),'rows':a[0],'old_new_logical_sha256':a[1]})
assert len(results)==100 and sum(r['rows'] for r in results)==1470952
assert new.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not new.execute('PRAGMA foreign_key_check').fetchmany(1);assert new.execute('PRAGMA user_version').fetchone()[0]==VERSION==25
assert new.execute('SELECT count(*) FROM player_restricted_observations').fetchone()[0]==0
baselines=[dict(r) for r in new.execute("SELECT refresh_family,refresh_period_year,refresh_kind,count(*) AS runs FROM capture_runs WHERE refresh_kind='BASELINE' GROUP BY refresh_family,refresh_period_year")]
claims=new.execute('SELECT count(*) FROM annual_fact_claims').fetchone()[0];header={'old':dict(old.execute('SELECT * FROM saves').fetchone()),'new':dict(new.execute('SELECT * FROM saves').fetchone())};old.close();new.close();after=file_sha256(source);assert before==after
report={'status':'V24_ORIGINAL_AND_ALL_OLD_ROWS_PRESERVED_IN_NEW_V25_COPY','source':str(source),'target':str(target),'source_sha256_before':before,'source_sha256_after':after,'target_sha256':file_sha256(target),'schema_version':25,'tables_compared':len(results),'old_rows_preserved':sum(r['rows'] for r in results),'old_field_values_except_schema_header_unchanged':True,'comparison':results,'header':header,'annual_baselines':baselines,'backfilled_identity_claims':claims,'integrity':'ok','foreign_key_errors':0,'restricted_rows':0,'active_save_binding_changed':False,'game_access':False,'elapsed_seconds':round(time.monotonic()-start,2)}
write(out/'v24-copy-migration.json',report);print(json.dumps({k:v for k,v in report.items() if k not in ('comparison','header','annual_baselines')},ensure_ascii=False))
