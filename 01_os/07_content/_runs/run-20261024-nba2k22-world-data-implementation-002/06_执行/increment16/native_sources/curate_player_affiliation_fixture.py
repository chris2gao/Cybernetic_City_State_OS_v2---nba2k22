import gzip,hashlib,json
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';run=Path(__file__).resolve().parent;capture=run/'player-affiliation-live-v15'
source=capture/'affiliation-manifest.json';out=app/'tests/fixtures/player_affiliations_20261025';out.mkdir(exist_ok=False)
m=json.loads(source.read_bytes())
for key in ('metadata','core_team_pointer_map','college_pointer_values_owner_only','college_object_pointers_owner_only'):m.pop(key)
raw=json.dumps(m,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode();path=out/'manifest.json.gz';path.write_bytes(gzip.compress(raw,mtime=0))
info={'files':{path.name:hashlib.sha256(path.read_bytes()).hexdigest()},'actual_manifest_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'actual_report_sha256':hashlib.sha256((capture/'affiliation-report.json').read_bytes()).hexdigest(),'replay_grade':'RESEARCH_FIXTURE',
    'curation':'Complete source subjects, classification rows and college object/link rows; metadata and owner pointer maps omitted. Actual bytes/traces retained in increment16.'}
(out/'source_manifest.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8',newline='\n');(out/'.gitattributes').write_text('*.gz -text\nsource_manifest.json -text\n',encoding='utf-8',newline='\n')
print(json.dumps({'subjects':len(m['players']),'college_objects':len(m['college_rows']),'compressed_fixture_bytes':path.stat().st_size}))
