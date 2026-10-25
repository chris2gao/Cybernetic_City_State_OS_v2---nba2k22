import json,sys
from pathlib import Path
r=Path(__file__).resolve().parent;app=Path.cwd()/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from database_operations import project_observations
from cadence import ANNUAL_FAMILIES
profile=json.loads((r/'storage-measurement-bundled-01/storage-profile.json').read_bytes())
for n in (20,40):
    calls={u['source_key']:1 if u['source_key'] in ANNUAL_FAMILIES.values() else n for u in profile['latest_source_units'] if u['source_key']!='BOUND_GAME_PLAYER_WORLD'}
    value=project_observations(profile,source_calls_per_season=calls,years=100)
    print(json.dumps({'status':value['status'],'ordinary_calls_per_season':n,'fixed_population_projected_gib':value['estimated_total_database_bytes']/1024**3,
        'recorded_uncompressed_source_artifact_gib':value['recorded_raw_artifact_bytes_at_same_frequencies']/1024**3,
        'top_tables':[(name,round(t['estimated_additional_allocated_bytes']/1024**3,3)) for name,t in sorted(value['tables'].items(),key=lambda pair:pair[1]['estimated_additional_allocated_bytes'],reverse=True)[:4]]}))
