"""Offline checks of the paused snapshot; never runs or attaches to the game."""
import argparse,ast,hashlib,json,re,subprocess
from pathlib import Path

REPO=Path(__file__).resolve().parents[4]
DOMAIN=REPO/'08_Domain_Applications/Antigravity_GM_Engine'
RUN=REPO/'01_os/07_content/_runs/run-20261027-rea-development-exploration-01'
E=RUN/'06_执行/evidence'
def load(name):return json.loads((E/name).read_text(encoding='utf-8-sig'))
def integrity():
 manifest=load('SOURCE_MANIFEST.json');paths=set()
 for row in manifest['files']:
  relative=Path(row['path']);assert not relative.is_absolute() and '..' not in relative.parts
  assert row['path'] not in paths;paths.add(row['path'])
  data=(E/relative).read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
  git_path=(E/relative).relative_to(REPO).as_posix()
  blob=subprocess.check_output(['git','show',':'+git_path],cwd=REPO)
  assert hashlib.sha256(blob).hexdigest()==row['sha256'],'Git blob byte normalization:'+row['path']
 assert len(paths)>=40
 allowed=['08_Domain_Applications/Antigravity_GM_Engine/research/rea_development/','08_Domain_Applications/Antigravity_GM_Engine/docs/development/REA_DEVELOPMENT_PLAYBOOK_V1.md','08_Domain_Applications/Antigravity_GM_Engine/docs/development/NBA2K22_DOCUMENT_AUTHORITY_INDEX_V1.md','01_os/07_content/_runs/run-20261027-rea-development-exploration-01/']
 diff=subprocess.check_output(['git','diff','--name-only','-z','7742568ac677b3c16079887463f05e81cb1191ed'],cwd=REPO).decode('utf-8').split('\0')
 untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=REPO).decode('utf-8').split('\0')
 for name in set(diff+untracked)-{''}:
  assert any(name==a or (a.endswith('/') and name.startswith(a)) for a in allowed),name
  assert Path(name).suffix.lower() not in {'.exe','.dll','.iff','.dds','.scne','.animation','.model','.shader'},name
 for path in (DOMAIN/'research/rea_development').glob('*.py'):ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
 for path in [DOMAIN/'docs/development/REA_DEVELOPMENT_PLAYBOOK_V1.md',DOMAIN/'research/rea_development/README.md']:
  for target in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
   if not re.match(r'https?://',target):assert (path.parent/target.split('#')[0]).exists(),target
 print(json.dumps({'check':'artifact-integrity-and-scope','manifest_files':len(paths),'scope':'offline integrity, syntax and local links only','passed':True}))

def evidence():
 sha='1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'
 total=0
 for tag,expected in [('metadata',13),('growth',9),('presentation',5)]:
  raw=load(tag+'-evidence.json');n=raw['normalized_result'];messages=n['messages']
  assert n['cleanup_error'] is None and not any(m['type']=='error' for m in messages)
  p=next(m['payload'] for m in messages if m['type']=='send')
  assert len(p['types'])==expected and len(p['xrefs'])==21
  assert p['hooks']==0 and p['memory_writes']==0 and p['getter_calls']==0 and p['instance_values_read']==0
  assert 0<p['explicit_read_bytes']<=1048576
  assert all(t['initializer_match'] and t['name_match'] and t['count']==len(t['fields']) for t in p['types'])
  assert all(x['live_bytes_match'] and x['execution_observed'] is False for x in p['xrefs'])
  target=load(tag+'-target.json');assert target['sha256']==sha and target['administrator'] is True
  assert hashlib.sha256((E/(tag+'-probe.js')).read_bytes()).hexdigest()==target['script_sha256']
  metric=load(tag+'-metrics.json');assert metric['exit_code']==0 and metric['process_still_running'] is True
  total+=expected
 bulk=load('bulk-fixture/bulk-fixture-results.json');assert bulk['count']==4096 and bulk['owned_process_exit']==0
 assert [p['phase'] for p in bulk['phases']]==['apply','restore']
 for phase in bulk['phases']:
  assert phase['rea']['verified']==4096 and phase['independent_child_check']['matches']==4096 and phase['independent_child_check']['mismatches']==0 and phase['cleanup_error'] is None
  assert phase['rea']['game_target'] is False
 assert bulk['phases'][0]['rea']['negative_cas_abort_no_write'] is True
 trace=load('call-trace-fixture/call-trace-results.json');assert trace['owned_process_exit']==0 and trace['cleanup_error'] is None
 assert len(trace['events'])==16 and {e['name'] for e in trace['events']}=={'reader','writer'}
 assert all(e['argument']==21 and e['result']==(42 if e['name']=='reader' else 43) for e in trace['events'])
 comparison=load('scorebug-comparison.json')['normalized_result'];assert comparison['summary']=={'unchanged':259,'added':0,'removed':0,'changed':2,'unknown':0,'contradiction':0}
 assert {r['logical_path'] for r in comparison['changes']}=={'.','scorebug_intro.SCNE'}
 candidate=load('scorebug-candidate.json');assert candidate['changed_members']==['scorebug_intro.SCNE'] and candidate['game_deployment'] is False and candidate['game_rendering_verified'] is False
 bindings=load('scorebug-bindings.json');assert bindings['node_type_counts']['SceneText']==44 and bindings['ui_trailing_bytes']==24384
 inventory=load('presentation-inventory.json');assert len(inventory['families'])==16 and inventory['disabled_feature_count'] is None and inventory['runtime_enabled_feature_count'] is None and inventory['game_information_injection_verified'] is False
 ui=load('prior-overall/human-ui-observation.json');embiid=next(r for r in ui['comparisons'] if r['name']=='Joel Embiid');assert embiid['human_reported_base_overall']==95 and embiid['human_reported_boosted_display']==96
 contracts=load('rea-tool-contracts.json');assert contracts['package_version']=='6.8.0' and contracts['tool_count']==229
 guide=(DOMAIN/'docs/development/REA_DEVELOPMENT_PLAYBOOK_V1.md').read_text(encoding='utf-8')
 assert '阶段性' in guide and 'UNKNOWN' in guide and '4,096' in guide and '不是原子CAS' in guide and 'MyCAREER' in guide
 handoff=(RUN/'08_结论/PLANNING_HANDOFF.md').read_text(encoding='utf-8');assert 'PARTIAL / HUMAN_PAUSED' in handoff and '不恢复实验' in handoff
 print(json.dumps({'check':'evidence-and-document-contract','metadata_type_observations':total,'fixture_records':4096,'game_writes_verified':False,'disabled_feature_count':'UNKNOWN','passed':True}))

if __name__=='__main__':
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--integrity',action='store_true');g.add_argument('--evidence',action='store_true');args=p.parse_args()
 if args.integrity:integrity()
 else:evidence()
