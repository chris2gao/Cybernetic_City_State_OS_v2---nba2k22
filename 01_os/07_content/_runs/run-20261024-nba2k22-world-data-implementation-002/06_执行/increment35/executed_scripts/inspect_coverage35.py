import json,sys
from contextlib import closing
from pathlib import Path
repo=Path.cwd();r=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES
from live_world import read_binding,bound_database
b,_=read_binding(r/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(r/'world-saves/nba2k22_test_01',b)
with closing(connect(db,True)) as c:
    counts={name:c.execute('SELECT count(*) FROM "'+name+'"').fetchone()[0] for name in TABLES};latest=[dict(row) for row in c.execute('''SELECT source_key,unit_id,observed_at FROM (SELECT source_key,unit_id,observed_at,row_number() OVER(PARTITION BY source_key ORDER BY observed_at DESC,unit_id DESC) AS rn FROM capture_units WHERE unit_status='success') WHERE rn=1 ORDER BY source_key''')];gaps=[]
    for unit in latest:
        gaps.extend(dict(row)|{'source_key':unit['source_key']} for row in c.execute('SELECT affected_domain,target_field,reason,impact FROM field_gaps WHERE gap_id LIKE ?', (unit['unit_id']+':field_gaps:%',)))
result={'tables':len(counts),'total_rows':sum(counts.values()),'empty_tables':[name for name,n in counts.items() if n==0],'latest_sources':latest,'latest_source_gap_declarations':gaps,'note':'Source-local gaps may be superseded by another family; no naive UNKNOWN count acceptance.'};(r/'coverage35.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'tables':len(counts),'empty_tables':result['empty_tables'],'source_count':len(latest),'source_local_gaps':len(gaps)}))
