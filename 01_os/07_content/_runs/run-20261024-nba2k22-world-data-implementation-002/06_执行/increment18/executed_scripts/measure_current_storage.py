import json,shutil,sys
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';sys.path.insert(0,str(app))
from database_operations import storage_profile
r=Path(__file__).resolve().parent;save=r/'world-saves/nba2k22_test_01';binding=json.loads((save/'save.json').read_bytes());db=save/binding['database_file'];output_name=sys.argv[1] if len(sys.argv)>1 else 'storage-measurement-01'
assert Path(output_name).name==output_name
out=r/output_name;out.mkdir(exist_ok=False)
profile=storage_profile(db);profile['host_volume_bytes']={drive:dict(zip(('total','used','free'),shutil.disk_usage(drive+':\\'))) for drive in ('C','E')}
(out/'storage-profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'database_bytes':profile['database_file_bytes'],'dbstat_status':profile['dbstat_status'],'source_keys':[u['source_key'] for u in profile['latest_source_units']],
    'top_tables':[{'table':name,'rows':t['rows'],'table_bytes':t['table_bytes'],'index_bytes':t['index_bytes']} for name,t in sorted(profile['tables'].items(),key=lambda pair:pair[1]['allocated_bytes'] or 0,reverse=True)[:8]]}))
