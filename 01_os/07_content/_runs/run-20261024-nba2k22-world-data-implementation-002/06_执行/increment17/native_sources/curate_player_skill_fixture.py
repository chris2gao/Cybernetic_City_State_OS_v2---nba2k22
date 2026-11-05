import gzip,hashlib,json
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';r=Path(__file__).resolve().parent;capture=r/'player-skill-live-v16';source=capture/'skill-manifest.json'
out=app/'tests/fixtures/player_skills_20261025';out.mkdir(exist_ok=False);m=json.loads(source.read_bytes());m.pop('metadata');m.pop('core_team_pointer_map')
path=out/'manifest.json.gz';path.write_bytes(gzip.compress(json.dumps(m,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode(),mtime=0))
info={'files':{path.name:hashlib.sha256(path.read_bytes()).hexdigest()},'actual_manifest_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'actual_report_sha256':hashlib.sha256((capture/'skill-report.json').read_bytes()).hexdigest(),
    'replay_grade':'RESEARCH_FIXTURE','curation':'Complete3390 source subjects and all56 public abilities/99 tendencies/initiator/4 slots. Native metadata and owner pointer map omitted. Actual bytes/traces remain in increment17.'}
(out/'source_manifest.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8',newline='\n');(out/'.gitattributes').write_text('*.gz -text\nsource_manifest.json -text\n',encoding='utf-8',newline='\n')
print(json.dumps({'subjects':len(m['players']),'skill_rows':len(m['skill_rows']),'compressed_bytes':path.stat().st_size}))
