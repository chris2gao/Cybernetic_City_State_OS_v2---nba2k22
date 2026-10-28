"""Offline source and semantics checks; no new process attach or writes."""
import ast,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[3];E=ROOT/'evidence'
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
registry=load(E/'source_registry.json');sources={s['source_id']:s for s in registry['sources']};assert len(sources)==len(registry['sources'])==13
for source in sources.values():
 if 'commit' in source:
  raw=subprocess.check_output(['git','show',source['commit']+':'+source['path']],cwd=REPO)
  blob=subprocess.check_output(['git','rev-parse',source['commit']+':'+source['path']],cwd=REPO).decode().strip();assert blob==source['git_blob']
 else:raw=(ROOT/source['path']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==source['sha256'],source['source_id']
cards=load(ROOT/'data/knowledge_cards.json');assert {c['mechanism_id'] for c in cards}=={'AI_COACH_DEFENSE_M1','AI_BADGE_NATURAL_GROWTH','AI_AI_GM_TRADE'}
for card in cards:
 assert all(ref in sources for ref in card['source_refs'])
 assert card['actor_scope_verdict']=='AI_PATH_UNVERIFIED' and card['can_execute'] is False and card['unknowns']
 assert card['proof_level'] not in {'L3_SAME_MODE_GAME_BEHAVIOR','L4_AUTHORIZED_CALL_WITH_FRESH_READBACK'}
 assert card['game_build_sha256']=='1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5'
manifest=load(E/'live_coach/manifest.json')
assert len(manifest['files'])==17
for record in manifest['files']:
 raw=(ROOT/record['path']).read_bytes();assert len(raw)==record['bytes'] and hashlib.sha256(raw).hexdigest()==record['sha256'],record['path']
 relative=(ROOT/record['path']).relative_to(REPO).as_posix();blob=subprocess.check_output(['git','show',':'+relative],cwd=REPO)
 assert hashlib.sha256(blob).hexdigest()==record['sha256'],'tracked Evidence bytes changed: '+relative
 live=json.loads(raw.decode('utf-8-sig')) if record['path'].endswith('.json') else None
 if live and 'normalized_result' in live:
  assert live['normalized_result']['cleanup_error'] is None
  assert not re.search(r'0x[0-9a-fA-F]{12,16}',json.dumps(live)),record['path']
read=load(E/'live_coach/read-success/coach-findings.json');p=read['observation']
assert p['stable_double_read'] and p['explicit_read_bytes']==9308 and {t['team_abbreviation'] for t in p['teams']}=={'IND','PHI'}
assert p['native_calls']==p['memory_writes']==p['hooks']==0 and not p['game_actor_dispatch_proven']
assert all(t['coach_values']['POEDefense']['raw']==14 and t['coach_values']['POEOffense']['raw']==5 and len(t['gameplans'])==29 for t in p['teams'])
trace=load(E/'live_coach/trace/coach-evidence.json');summary=next(m['payload'] for m in trace['normalized_result']['messages'] if m['type']=='send')
assert summary['event_count']==0 and summary['hook_detached'] and not summary['ai_dispatch_proven']
rejected=load(E/'live_coach/guard-rejection/coach-evidence.json');assert any(m['type']=='error' and 'coach pool identity' in m.get('description','') for m in rejected['normalized_result']['messages'])
identity=load(E/'live_coach/identity-hypothesis/coach-evidence.json')
assert not any(m['type']=='error' for m in identity['normalized_result']['messages'])
h=next(m['payload'] for m in identity['normalized_result']['messages'] if m['type']=='send')
assert h['stable_directory_recheck'] and h['team_directory_count']==219
assert h['explicit_read_bytes']==2724<=h['read_budget']==65536
assert h['native_calls']==h['business_writes']==h['hooks']==0
assert h['original_failed_absolute_pointer_was_recorded'] is False
assert h['reconstructed_first_abort']['team_id']==5000 and h['reconstructed_first_abort']['coach_is_null']
assert len(h['observations'])==5 and h['isolated_read_failures']==[]
assert all(r['pool_membership_hypothesis']['hard_read_gate'] is False and r['writer_or_native_call_identity_qualified'] is False for r in h['observations'])
extra=next(r for r in h['observations'] if r['team_id']==788)
assert not extra['core_team_id'] and extra['mapping']['first_352_bytes_readable']
assert next(f for f in extra['object_fields'] if f['field']=='last_name_candidate')['utf16_candidate']=='Copelovici'
assert next(f for f in extra['object_fields'] if f['field']=='team_reciprocal_pointer_candidate')['equals_source_team']
for tag,script in [('guard-rejection','coach_read_probe.js'),('read-success','coach_read_probe.js'),('trace','coach_trace_probe.js'),('identity-hypothesis','coach_identity_probe.js')]:
 target=load(E/f'live_coach/{tag}/coach-target.json');raw=load(E/f'live_coach/{tag}/coach-evidence.json')
 assert target['administrator'] and target['exe_sha256']==cards[0]['game_build_sha256']
 assert target['pid']==raw['normalized_result']['pid']
 assert hashlib.sha256((E/f'live_coach/{tag}/{script}').read_bytes()).hexdigest()==target['script_sha256']
 assert raw['normalized_result']['source_sha256']==target['script_sha256']
static=load(E/'static_ai_seams.json');followup=load(E/'static_ai_followup.json');assert len(static['queries'])==13 and len(followup['queries'])==9
assert all(not data['game_process_attached'] and not data['absolute_addresses_published'] for data in (static,followup))
fragments=load(E/'candidate_function_fragments.json')['functions'];assert len(fragments)==6
lookup=next(f for f in fragments if f['referenced_literal'].endswith('GetOpponentGameplanIndex'))
assert any(i['mnemonic']=='imul' and '0x370' in i['operands'] for i in lookup['instructions'])
assert any(i['mnemonic']=='cmp' and '0x23' in i['operands'] for i in lookup['instructions'])
assert any(i['mnemonic']=='mov' and i['operands']=='al, 0xff' for i in lookup['instructions'])
matrix=load(ROOT/'data/backend_matrix.json');assert all(m['route']=='NO_SAFE_PATH' for m in matrix['mechanisms']);assert matrix['conditional_native_PoC']=='NOT_EXECUTED'
for file in ROOT.rglob('*.py'):ast.parse(file.read_text(encoding='utf-8'),filename=file.name)
assert not any(p.name=='SOURCE_MANIFEST.json' for p in ROOT.rglob('*')),'do not duplicate old52 manifest'
assert not any(p.suffix.lower() in {'.exe','.iff','.dds','.dll','.scne'} for p in ROOT.rglob('*') if p.is_file())
for name in ('M1_BADGE','M2_COACH','M3_TRADE'):assert (ROOT/'dossiers'/f'{name}.md').is_file()
print(json.dumps({'source_records_verified':len(sources),'live_files_verified':len(manifest['files']),'static_fragments':len(fragments),'identity_hypothesis_observations':len(h['observations']),'AI_gameplay_or_native_action_claims':0,'game_business_writes':0,'current_build_stored_coach_fields':'VERIFIED','native_and_memory_business_eligibility':'NO_SAFE_PATH','result':'EVIDENCE_CONTRACT_PASS'}))
