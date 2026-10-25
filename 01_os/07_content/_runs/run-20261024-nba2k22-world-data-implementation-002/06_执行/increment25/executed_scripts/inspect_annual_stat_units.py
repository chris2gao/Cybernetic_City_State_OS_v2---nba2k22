import json,sys
from pathlib import Path
r=Path(__file__).resolve().parent;sys.path.insert(0,str(Path.cwd()/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from engine import connect
from query import native_player_seasons
c=connect(r/'world-saves/nba2k22_test_01/world-v18.sqlite',True)
for row in c.execute("SELECT u.unit_id,u.observed_at,r.source_grade,r.refresh_family,r.refresh_period_year FROM capture_units u JOIN capture_runs r USING(run_id) WHERE u.source_key='BOUND_NATIVE_HONOR_STATS' AND u.unit_status='success' ORDER BY u.observed_at"):
    item=dict(row);item['stat_bank_artifact']=[dict(a) for a in c.execute("SELECT payload_ref,sha256,byte_count FROM source_artifacts WHERE unit_id=? AND payload_ref LIKE '%player-stat-bank.bin'",(row['unit_id'],))];print(json.dumps(item))
print('latest',json.dumps(native_player_seasons(r/'world-saves/nba2k22_test_01/world-v18.sqlite',limit=1)['unit']));c.close()
