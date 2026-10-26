import json,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from engine import connect
from schema_model import TABLES,ident
from live_world import read_binding,bound_database
binding,_=read_binding(runtime/'world-saves/nba2k22_test_01','MyLEAGUE0003');db=bound_database(runtime/'world-saves/nba2k22_test_01',binding)
with connect(db,True) as c:
    counts={name:c.execute('SELECT count(*) FROM '+ident(name)).fetchone()[0] for name in TABLES}
    gaps=[dict(r) for r in c.execute('''WITH newest AS (SELECT source_key, max(observed_at) stamp FROM capture_units GROUP BY source_key)
        SELECT u.source_key,g.affected_domain,g.target_field,g.reason,g.impact FROM field_gaps g JOIN capture_units u ON g.gap_id GLOB u.unit_id||':field_gaps:*'
        JOIN newest n ON u.source_key=n.source_key AND u.observed_at=n.stamp ORDER BY u.source_key,g.target_field''')]
report={'binding':binding,'counts':counts,'latest_source_gaps':gaps}
(runtime/'coverage29.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'empty_public_tables':[name for name,t in TABLES.items() if t.public and counts[name]==0],'latest_source_gaps':gaps[:45],'total_latest_gaps':len(gaps)},ensure_ascii=False))
