import gzip,hashlib,json
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';run=Path(__file__).resolve().parent
capture=run/'player-details-live-v13';source=capture/'player-detail-manifest.json';out=app/'tests/fixtures/player_details_20261025';out.mkdir(exist_ok=False)
manifest=json.loads(source.read_bytes());manifest.pop('metadata');raw=json.dumps(manifest,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
path=out/'manifest.json.gz';path.write_bytes(gzip.compress(raw,mtime=0))
info={'files':{path.name:hashlib.sha256(path.read_bytes()).hexdigest()},'actual_manifest_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'actual_report_sha256':hashlib.sha256((capture/'player-detail-report.json').read_bytes()).hexdigest(),
    'curation':'Complete native pool, all 17 contract fields and all 98 nonreserved base badges; metadata omitted; exact raw source retained in increment14.',
    'replay_grade':'RESEARCH_FIXTURE'}
(out/'source_manifest.json').write_text(json.dumps(info,indent=2)+'\n',encoding='utf-8',newline='\n')
(out/'.gitattributes').write_text('*.gz -text\nsource_manifest.json -text\n',encoding='utf-8',newline='\n')
print(json.dumps({'subjects':len(manifest['players']),'badges':len(manifest['badge_rows']),'fixture_bytes':path.stat().st_size}))
