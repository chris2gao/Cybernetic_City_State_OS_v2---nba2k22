import gzip,hashlib,json
from pathlib import Path
repo=Path.cwd();app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';run=Path(__file__).resolve().parent
out=app/'tests/fixtures/league_20261025';out.mkdir(exist_ok=False);sources={}
for name,directory in (('history','history-first'),('news','news-first')):
    capture=run/'league-live-v12'/directory;source=capture/'league-source-manifest.json';report=capture/'league-source-report.json'
    manifest=json.loads(source.read_bytes());manifest.pop('metadata')
    name=name+'-manifest.json.gz';data=json.dumps(manifest,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
    (out/name).write_bytes(gzip.compress(data,mtime=0))
    sources[name]={'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest(),'actual_manifest_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'actual_report_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),'source_pid':2132,'fixture_grade':'RESEARCH_FIXTURE',
        'curation':'Complete decoded source pools with runtime metadata omitted; exact original source and metadata retained in increment13 archives.'}
(out/'source_manifest.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'.gitattributes').write_text('*.gz -text\nsource_manifest.json -text\n',encoding='utf-8')
print(json.dumps({'fixture_files':len(sources),'compressed_bytes':sum(p.stat().st_size for p in out.glob('*.gz'))}))
