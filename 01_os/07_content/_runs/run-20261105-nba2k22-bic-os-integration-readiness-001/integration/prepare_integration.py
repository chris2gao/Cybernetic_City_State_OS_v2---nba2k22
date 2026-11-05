"""Derive integration provenance without changing any business source."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
RUN=OUT.parent
MASTER='66f8f73f1a91597f4562b834c2acad332ad9de5b'
W1='aec3dbaacd1d56b0c7cc1d40c2f70607493b9a4b'
W2='cdcb293f8a690725cf9168225cc2046ab0574b2b'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def write(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
contract_sha='716a01986715e369850a2bbb4d30ed143070d257'
contract_path=RUN.relative_to(ROOT).as_posix()+'/EXECUTION_CONTRACT.md'
(RUN/'EXECUTION_CONTRACT.md').write_bytes(git('show',contract_sha+':'+contract_path))
reviews=[('3f27b421e0c1813dbfb890c4583c97e76dfd6f98','run-20261104-nba2k22-bic-batch1-series-review-001/DIFFERENCE_REVIEW_HUMAN_CLOSEOUT.md'),('13414798d5992336e28ae1df7e14bf17fbae6a04','run-20261105-nba2k22-bic-wave2-series-review-001/BIC_WAVE2_DIFFERENCE_REVIEW_CLOSEOUT_v1.json'),('13414798d5992336e28ae1df7e14bf17fbae6a04','run-20261105-nba2k22-bic-wave2-series-review-001/DIFFERENCE_REVIEW_HUMAN_CLOSEOUT.md')]
(OUT/'reviews').mkdir(exist_ok=True)
sources=[]
freeze_source=Path('C:/Users/gk/.codex/worktrees/nba2k22-bic-os-readiness/Cybernetic_City_State_OS_v2 - nba2k22')/RUN.relative_to(ROOT)/'os/TECHNICAL_TEST_FREEZE.json'
freeze_bytes=freeze_source.read_bytes()
freeze=json.loads(freeze_bytes)
assert freeze['package_sha256']==hashlib.sha256(json.dumps(freeze['tests'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
for item in freeze['tests']:
    assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
(OUT/'technical_test_freeze.json').write_bytes(freeze_bytes)
for sha,path in reviews:
    path='01_os/07_content/_runs/'+path
    content=git('show',sha+':'+path)
    dest=OUT/'reviews'/(('wave1_' if sha.startswith('3f27') else 'wave2_')+Path(path).name)
    dest.write_bytes(content)
    sources.append({'commit':sha,'path':path,'copy':dest.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(content).hexdigest(),'copy_identical':True})
write('review_sources.json',sources)
ancestry=[]
for older,newer in [(MASTER,W1),(W1,W2),(MASTER,W2)]:
    result=subprocess.run(['git','merge-base','--is-ancestor',older,newer],cwd=ROOT)
    assert result.returncode==0
    ancestry.append({'older':older,'newer':newer,'exit_code':result.returncode,'ahead_behind':git('rev-list','--left-right','--count',older+'...'+newer).decode().strip()})
paths=git('diff','--name-only','-z',MASTER,W2).decode('utf-8').rstrip('\0').split('\0')
entries=[]
for path in paths:
    raw=git('show',W2+':'+path)
    entries.append({'path':path,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
tree=git('ls-tree','-r','-l','-z',W2).decode('utf-8').rstrip('\0').split('\0')
large=[];database=[];licensed=[]
for row in tree:
    meta,path=row.split('\t',1)
    size=meta.split()[-1]
    if size.isdigit() and int(size)>10*1024*1024:large.append({'path':path,'bytes':int(size)})
    if Path(path).suffix.lower() in {'.sqlite','.sqlite3','.db','.bak','.zip','.7z'}:database.append(path)
    if Path(path).name.lower().startswith(('license','copying')):licensed.append(path)
write('source_inventory.json',{'engineering_master':MASTER,'wave1':W1,'wave2':W2,'ancestry':ancestry,'changed_files':entries,'tracked_large_files_over_10mib':large,'tracked_database_archive_paths':database,'license_paths':licensed,'checks_scope':'All tracked object metadata; changed public engineering files hashed, no database payload opened','business_source_changed_in_this_task':False})
special=[]
for path in sorted(set(database+[item['path'] for item in large])):
    original=git('rev-parse',MASTER+':'+path).decode().strip()
    candidate=git('rev-parse',W2+':'+path).decode().strip()
    special.append({'path':path,'master_blob':original,'candidate_blob':candidate,'unchanged_from_master':original==candidate})
write('large_database_audit.json',{'existing_tracked_files':special,'new_database_archive_paths':[p for p in paths if Path(p).suffix.lower() in {'.sqlite','.sqlite3','.db','.bak','.zip','.7z'}],'new_files_over_10mib':[e for e in entries if e['bytes']>10*1024*1024],'new_dependency_or_license_files':[p for p in paths if Path(p).name.lower().startswith(('requirements','pyproject','package.json','license','copying'))],'license_review_scope':'No dependency/license change introduced by reviewed BIC diff. No general repository license certification; repository has no discovered LICENSE/COPYING filename.'})
(OUT/'engineering_diff.name-status.txt').write_bytes(git('diff','--name-status',MASTER,W2))
write('PRECHECK_ACTUAL.json',{'master':MASTER,'core':'08d8e534a3438269aa7d7eb1b080ab11c172f462','contract_commit':contract_sha,'ancestry':ancestry,'candidate_creation':'New branch created at NBA master then git merge --ff-only fixed Wave2; master unchanged','engineering_changed_files':len(entries),'reviews':sources})
print(json.dumps({'ancestry':'PASS','engineering_files':len(entries),'large_files':len(large),'database_archive_paths':len(database),'reviews':len(sources),'technical_freeze_verified':freeze['package_sha256']}))
