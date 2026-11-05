"""Offline CLI smoke plus exact reviewed-source and historical artifact checks."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
D=ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'tests'))
from test_observation_scope import ObservationScopeTests,T0,T1
from observation_scope import query_at
from query import player_card
fixture=ObservationScopeTests();fixture.setUp()
commands=[]
try:
    before=hashlib.sha256(fixture.db.read_bytes()).hexdigest()
    for name,args in [('player',['bic_cli.py','player',str(fixture.db),'p1']),('team',['bic_cli.py','team',str(fixture.db),'t1']),('diagnosis',['bic_wave2_cli.py',str(fixture.db),'p1','--team-id','t1'])]:
        command=[sys.executable,'-B','-X','utf8',str(D/args[0]),*args[1:],'--save-id','save','--season-id','s1','--as-of',T1]
        result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (OUT/(name+'.stdout.log')).write_bytes(result.stdout)
        (OUT/(name+'.stderr.log')).write_bytes(result.stderr)
        assert result.returncode==0,(name,result.stderr.decode(errors='replace')[-1500:])
        data=json.loads(result.stdout)
        if name=='diagnosis':
            assert data['player']['data_status']=='REAL_DATA_NOT_VERIFIED'
            assert data['team']['players']
            assert not data['player']['verified_mechanisms']
        else:assert data['baseline']['entity_kind']==name
        public=[arg.replace(str(fixture.root),'<synthetic-temp>') for arg in command]
        public[0]='python'
        commands.append({'name':name,'command':public,'exit_code':result.returncode,'output_sha256':hashlib.sha256(result.stdout).hexdigest()})
    old=query_at(fixture.db,T0,'player_card','p1')['result']
    latest=player_card(fixture.db,'p1')
    assert old['families']['player_attribute_snapshots']['overall_raw']['value']==80
    assert latest['families']['player_attribute_snapshots']['overall_raw']['value']==90
    after=hashlib.sha256(fixture.db.read_bytes()).hexdigest()
    assert before==after
finally:fixture.doCleanups()
inventory=json.loads(Path(__file__).with_name('source_inventory.json').read_bytes())
for entry in inventory['changed_files']:
    path=ROOT/entry['path']
    assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'],entry['path']
large_audit=json.loads(Path(__file__).with_name('large_database_audit.json').read_bytes())
assert not large_audit['new_database_archive_paths'] and not large_audit['new_files_over_10mib']
assert all(item['unchanged_from_master'] for item in large_audit['existing_tracked_files'])
for name in ['query.py','schema.sql']:
    path=D/name
    if path.exists():
        relative=path.relative_to(ROOT).as_posix()
        original=subprocess.check_output(['git','show',inventory['engineering_master']+':'+relative],cwd=ROOT)
        assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256(original).digest()
receipt={'commands':commands,'synthetic_database_unchanged':before==after,'synthetic_only':True,'query_at_legacy_isolation':'PASS: cutoff 80 vs current 90','reviewed_changed_files_identical':len(inventory['changed_files']),'formal_os_pass':False,'game_operations':False}
freeze=json.loads(Path(__file__).with_name('technical_test_freeze.json').read_bytes())
for item in freeze['tests']:
    assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
receipt['technical_freeze_package_sha256']=freeze['package_sha256']
receipt['formal_stage04_freeze_approved']=False
(OUT/'cli_integrity_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'cli_checks':3,'source_files_verified':len(inventory['changed_files']),'query_at_isolation':'PASS','database_unchanged':True}))
