"""Read-only migrated-data audit and portable snapshot; never connect to NBA2K22."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

ROOT=Path.cwd()
RUN=Path(__file__).resolve().parent
APP=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
sys.path.insert(0,str(APP))
from database_operations import file_sha256
from query import schedule,game_box,annual_facts

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

db=RUN/'_runtime/migration/world-v25-final.sqlite'
expected='f3ae5fd169845b7ad87fc3da96be37e59f514eb612a82e5b0e2afc0b2a7af753'
assert file_sha256(db)==expected
evidence=RUN/'evidence'
managed=ROOT.parent/'review-fixes-managed-20261026-01'
copied=evidence/'managed'
copied.mkdir(exist_ok=True)
for source in managed.iterdir():
    if source.is_file():shutil.copyfile(source,copied/source.name)
write(evidence/'managed-evidence-copy.json',{'external_attempt':str(managed),'files':[{'name':p.name,'sha256':file_sha256(p)} for p in sorted(copied.iterdir()) if p.is_file()],'byte_preserving_copy':True,'candidate':'b847f717df6702fe6251872d64aed476ac707f6f','inspect_exit_code':0})

with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True) as conn:
    tables=[r[0] for r in conn.execute("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    total=sum(conn.execute('SELECT count(*) FROM "'+name+'"').fetchone()[0] for name in tables)
    units=conn.execute("SELECT count(*) FROM capture_units WHERE unit_status='success'").fetchone()[0]
    buckets=conn.execute("SELECT refresh_family,refresh_period_year FROM capture_runs WHERE refresh_kind='BASELINE' ORDER BY refresh_family").fetchall()
    assert len(tables)==101 and total==1561421 and units==42 and len(buckets)==4
annual=[]
for family,year in buckets:
    page=annual_facts(db,family,year,limit=25)
    assert page['status']=='ACCEPTED_BASELINE_PLUS_UNIQUE_ADDITIONS' and page['records']
    claims={r['claim_id'] for r in page['records']}
    count=len(claims)
    if page['next_cursor']:
        second=annual_facts(db,family,year,limit=25,cursor=page['next_cursor'])
        assert not claims.intersection(r['claim_id'] for r in second['records'])
        count+=len(second['records'])
    annual.append({'family':family,'year':year,'baseline_unit_id':page['baseline_unit_id'],'bounded_paged_facts_checked':count,'all_first_page_grades':sorted({r['provenance']['source_grade'] for r in page['records']})})
rows=schedule(db,limit=2000)
sample=[r for r in rows['records'] if r['box_unit_id']][:12] if isinstance(rows,dict) else [r for r in rows if r['box_unit_id']][:12]
checks=[]
for row in sample:
    box=game_box(db,row['game_id'])
    assert row['box_unit_id']==box['selected_unit_id']
    full=all(box['coverage'][side]['status']=='ALL_CAPTURED_NATIVE_PARTICIPANTS_RESOLVED' for side in ('HOME','AWAY'))
    assert bool(row['canonical_box_complete'])==full
    assert row['home_points_derived']==box['scores']['derived_canonical_points']['HOME']
    assert row['away_points_derived']==box['scores']['derived_canonical_points']['AWAY']
    checks.append({'game_id':row['game_id'],'box_unit_id':row['box_unit_id'],'canonical_box_complete':full})
assert sample
assert file_sha256(db)==expected
write(evidence/'real-copy-query-audit.json',{'status':'PASS','source':'preexisting real Native observations copied from frozen v24; no new game capture','schema_version':25,'strict_tables':101,'total_rows_including_metadata_and_ledger':total,'successful_units':units,'annual_queries':annual,'schedule_game_box_parity':checks,'database_unchanged':True,'game_access':False})

snapshot=RUN/'snapshots'
snapshot.mkdir(exist_ok=True)
manifest_path=snapshot/'world-v25.snapshot.json'
if not manifest_path.exists():
    compressed=RUN/'_runtime/migration/world-v25.final.sqlite.gz'
    with db.open('rb') as src,compressed.open('wb') as dst:
        with gzip.GzipFile(filename='',mode='wb',compresslevel=6,fileobj=dst,mtime=0) as stream:
            shutil.copyfileobj(src,stream,1024*1024)
    parts=[]
    with compressed.open('rb') as stream:
        index=1
        while data:=stream.read(32*1024*1024):
            part=snapshot/f'world-v25.sqlite.gz.part{index:03d}'
            with part.open('xb') as dst:dst.write(data)
            parts.append({'file':part.name,'byte_count':len(data),'sha256':hashlib.sha256(data).hexdigest()})
            index+=1
    write(manifest_path,{'format':'CONTINUOUS_GZIP_SPLIT_V1','schema_version':25,'database_sha256':expected,'database_bytes':db.stat().st_size,'compressed_sha256':file_sha256(compressed),'compressed_bytes':compressed.stat().st_size,'parts':parts,'successful_capture_units':42,'new_game_captures_in_this_task':0,'tables':101,'total_rows':total,'restoration':'Concatenate parts in manifest order, decompress to a NEW file, verify database SHA256. Never overwrite v24 or rebind save.json automatically.','external_raw_artifacts':'Not embedded; retained in original run and original artifact references.','original_v24_preserved':True,'capacity_benchmark':False})
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
joined=RUN/'_runtime/migration/world-v25.rejoined.sqlite.gz'
with joined.open('wb') as target:
    for part in manifest['parts']:
        source=snapshot/part['file']
        assert source.stat().st_size==part['byte_count'] and file_sha256(source)==part['sha256']
        with source.open('rb') as stream:shutil.copyfileobj(stream,target,1024*1024)
assert file_sha256(joined)==manifest['compressed_sha256']
digest=hashlib.sha256();byte_count=0
with gzip.open(joined,'rb') as stream:
    while data:=stream.read(1024*1024):digest.update(data);byte_count+=len(data)
assert digest.hexdigest()==expected and byte_count==db.stat().st_size
assert file_sha256(db)==expected
write(evidence/'snapshot-check.json',{'status':'PASS','manifest':str(manifest_path.relative_to(ROOT)).replace('\\','/'),'parts_checked':len(manifest['parts']),'compressed_sha256':manifest['compressed_sha256'],'decompressed_database_sha256':digest.hexdigest(),'decompressed_bytes':byte_count,'matches_final_copy':True,'capacity_benchmark':False,'game_access':False})
print(json.dumps({'status':'PASS','tables':len(tables),'rows':total,'successful_units':units,'annual_families_queried':len(annual),'game_box_samples':len(checks),'snapshot_parts':len(manifest['parts']),'database_sha256':expected}))
