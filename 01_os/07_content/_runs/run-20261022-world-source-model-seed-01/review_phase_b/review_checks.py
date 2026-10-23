"""Read-only independent review of pinned Git blobs and original Stage A evidence.
Writes only review evidence under its own directory; never touches candidate/attempt.
"""
import collections, hashlib, json, pathlib, re, shutil, subprocess, sys
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CAND = '142531f2d60813bce5b90254c5e347050c40b406'
ARCH = '734188ab378974cf1d4426e67c675de561aac692'
DOM = '08_Domain_Applications/Antigravity_GM_Engine/'
DEV = DOM + 'docs/development/'
RUN = '01_os/07_content/_runs/run-20261022-world-source-model-seed-01/'
ATTEMPT = pathlib.Path(r'C:\Users\gk\AppData\Local\Temp\citystate_managed_verification_evidence\attempt_seed_01_e5a2d145e33d457d98878bf3fac81c61')
def git(*args):
    p = subprocess.run(['git', '--no-optional-locks', *args], cwd=ROOT, capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode('utf-8','replace'))
    return p.stdout
def blob(path, sha=CAND): return git('show', f'{sha}:{path}')
def load(name): return json.loads(blob(DEV+name))
def sha(data): return hashlib.sha256(data).hexdigest()
def save(name, value): (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def resolve(ref):
    path, _, pointer = ref.partition('#')
    if not '/' in path: path=DEV+path
    elif not path.startswith(('08_Domain_Applications/','01_os/')): path=DOM+path
    try:
        raw=blob(path)
        if not pointer: return {'ok':True,'path':path}
        node=json.loads(raw)
        for tok in pointer.lstrip('/').split('/'):
            tok=tok.replace('~1','/').replace('~0','~')
            node=node[int(tok)] if isinstance(node,list) else node[tok]
        return {'ok':True,'path':path,'value':node}
    except Exception as exc: return {'ok':False,'path':path,'error':str(exc)[:160]}
def evidence():
    inp=json.loads((ATTEMPT/'input.json').read_bytes()); plan=inp['plan']
    expected={'input.json','result.json','source_after.json'}
    records=[]
    for i,check in enumerate(plan['checks'],1):
        prefix=f'{i:03d}'
        expected.update(f'{prefix}.{s}' for s in ['started.json','finished.json','source.json','stdout.bin','stderr.bin'])
        end=json.loads((ATTEMPT/f'{prefix}.finished.json').read_bytes())
        start=json.loads((ATTEMPT/f'{prefix}.started.json').read_bytes())
        source=json.loads((ATTEMPT/f'{prefix}.source.json').read_bytes())
        out=(ATTEMPT/f'{prefix}.stdout.bin').read_bytes(); err=(ATTEMPT/f'{prefix}.stderr.bin').read_bytes()
        records.append({'id':check['id'],'exit_code':end['exit_code'],'status':end['status'],
            'start_id_matches':start['id']==check['id'],'source':source,
            'stdout_digest_matches':sha(out)==end['stdout_sha256'], 'stderr_digest_matches':sha(err)==end['stderr_sha256'],
            'stdout':out.decode('utf-8','replace'),'stderr_bytes':len(err)})
    actual={p.name for p in ATTEMPT.iterdir()}; missing=sorted(expected-actual); extra=sorted(actual-expected)
    original_manifest={p.name:{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in ATTEMPT.iterdir() if p.is_file()}
    mirror=HERE/'evidence_attempt_mirror'
    mirror.mkdir(exist_ok=False)
    for name in sorted(expected & actual): shutil.copyfile(ATTEMPT/name,mirror/name)
    manifest_ok=all(sha((mirror/n).read_bytes())==original_manifest[n]['sha256'] for n in expected & actual)
    original_run=subprocess.run([sys.executable,'-B',str(ROOT/'01_os/06_execution/task_discipline/managed_verification/managed_verify.py'),
        'inspect','--repo-root',str(ROOT),'--candidate',CAND,'--plan',RUN+'verification_plan.json','--attempt',str(ATTEMPT)],capture_output=True)
    mirror_run=subprocess.run([sys.executable,'-B',str(ROOT/'01_os/06_execution/task_discipline/managed_verification/managed_verify.py'),
        'inspect','--repo-root',str(ROOT),'--candidate',CAND,'--plan',RUN+'verification_plan.json','--attempt',str(mirror)],capture_output=True)
    for name,p in [('original_inspect',original_run),('mirror_inspect',mirror_run)]:
        (HERE/(name+'.stdout.txt')).write_bytes(p.stdout); (HERE/(name+'.stderr.txt')).write_bytes(p.stderr)
    save('stage_a_evidence_audit.json',{'candidate':inp['candidate'],'original_attempt':str(ATTEMPT),
        'actual_files':len(actual),'expected_files':len(expected),'missing':missing,'extra':extra,
        'plan_blob_hash_matches':sha(blob(RUN+'verification_plan.json'))==inp['plan_sha256'],
        'original_manifest':original_manifest,'checks':records,'mirror_byte_identical':manifest_ok,
        'original_inspect_exit':original_run.returncode,'mirror_inspect_exit':mirror_run.returncode,
        'original_inspect':original_run.stdout.decode(),'mirror_inspect':mirror_run.stdout.decode(),
        'original_after_unchanged':all(sha((ATTEMPT/n).read_bytes())==v['sha256'] for n,v in original_manifest.items()),
        'limit':'Mirror is an explicitly derived subset, not a repaired original attempt or a new verification run.'})
    print(json.dumps({'expected':len(expected),'actual':len(actual),'missing':missing,'extra':extra,
        'original_inspect_exit':original_run.returncode,'mirror_inspect_exit':mirror_run.returncode,'all_recorded_checks_exit0':all(x['exit_code']==0 for x in records)}))
def catalog():
    c=load('GAME_UI_FIELD_CATALOG_V0.json');n=load('GAME_NATIVE_OBJECT_HINTS_V0.json');q=load('FLASH_R00_PRIORITY_QUEUE_V0.json');a=load('GAME_ACTION_DISCOVERY_SEED_V0.json')
    fields=c['fields']; refs={}; errors=[]
    for f in fields:
        for ref in f.get('source_refs',[]):
            if ref not in refs: refs[ref]=resolve(ref)
            if not refs[ref]['ok']: errors.append({'field_id':f['field_id'],'ref':ref,'error':refs[ref]['error']})
    queue=[]
    for item in q['items']:
        queue.append({**item,'resolved_roots':[resolve(x) for x in item['root_refs']],
            'resolved_fields':[{k:v for k,v in resolve(x).items() if k!='value'}|{'field':resolve(x).get('value')} for x in item['field_refs']]})
    counters={k:dict(collections.Counter(str(x.get(k)) for x in fields)) for k in ['domain','value_type','lifecycle','lifecycle_class','sensitivity','canonicalization_state','native_object','field_family']}
    labels=collections.defaultdict(list)
    for f in fields: labels[str(f.get('label',f.get('meaning'))) ].append(f['field_id'])
    save('catalog_analysis.json',{'keys':list(c),'field_keys':list(fields[0]),'counts':counters,
        'rows':len(fields),'pages':len(c['pages']),'actions':len(a['entries']),'adjacency_groups':len(n['field_adjacency_groups']),
        'source_ref_unique':len(refs),'reference_errors':errors,'roots':n['roots'],'queue':queue,
        'action_unsafe':[x for x in a['entries'] if any(x.get(k) is not False for k in ['current_task_real_write','current_task_readback_verified','current_task_save_reload_verified','production_enabled_by_this_catalog'])],
        'special_fields':[x for x in fields if any(t in x['field_id'].lower() for t in ['age','birth','draft','years_pro','potential','career','teamid','team_id','gameid'])],
        'duplicate_labels':{k:v for k,v in labels.items() if len(v)>1},'field_samples':fields[:3]})
    print(json.dumps({'rows':len(fields),'pages':len(c['pages']),'actions':len(a['entries']),'types':counters['value_type'],'reference_errors':len(errors),'sample_errors':errors[:8],'field_keys':list(fields[0])},ensure_ascii=False))
def arch():
    names=['WORLD_DATA_DOMAIN_MODEL_V1.md','WORLD_DATA_ENTITY_CATALOG_V1.json','WORLD_DATA_IDENTITY_AND_TIME_ADR_V1.md','WORLD_DATA_SOURCE_AND_QUALITY_CONTRACT_V1.md','WORLD_DATA_LEGACY_IMPACT_AND_SCHEMA_HANDOFF_V1.md']
    entities=json.loads(blob(DEV+names[1],ARCH))
    model=blob(DEV+'GAME_DOMAIN_SOURCE_MODEL_V0.md').decode('utf-8')
    mappings=re.findall(r'^\| `([^`]+)` \| ([^|]+) \| ([^|]+) \|',model,re.M)
    save('architecture_mapping_audit.json',{'source_sha':ARCH,'source_keys':list(entities),'entities':entities,'v0_mappings':mappings,
        'source_file_hashes':{name:sha(blob(DEV+name,ARCH)) for name in names}})
    print(json.dumps({'arch_keys':list(entities),'mapping_count':len(mappings),'entity_collection_sizes':{k:len(v) for k,v in entities.items() if isinstance(v,(list,dict))}},ensure_ascii=False))
if __name__=='__main__': {'evidence':evidence,'catalog':catalog,'arch':arch}[sys.argv[1]]()
