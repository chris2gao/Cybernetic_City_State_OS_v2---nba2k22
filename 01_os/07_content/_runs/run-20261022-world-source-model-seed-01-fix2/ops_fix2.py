"""Bounded source inspection and protected-baseline recording; no game access."""
import collections, hashlib, json, pathlib, subprocess, sys, tempfile
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[3]
DOM='08_Domain_Applications/Antigravity_GM_Engine/'
DEV=DOM+'docs/development/'
OLD='01_os/07_content/_runs/run-20261022-world-source-model-seed-01/'
BASE='8cdbfaefbcb001c6ca0612017957c6414876eea4'
def git(*args,root=ROOT):
    return subprocess.check_output(['git','--no-optional-locks',*args],cwd=root)
def load(path):return json.loads((ROOT/path).read_bytes())
def save(name,data):
    (HERE/name).write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def hashed(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def baseline():
    main=pathlib.Path(r'E:\workspace\Cybernetic_City_State_OS_v2 - nba2k22')
    protected=[main/OLD/'OS_MACHINE_VERIFICATION_REPORT.md',main/'08_Domain_Applications/提示词.txt']
    attempt=pathlib.Path(r'C:\Users\gk\AppData\Local\Temp\citystate_managed_verification_evidence\attempt_seed_01_e5a2d145e33d457d98878bf3fac81c61')
    manifest={str(p):hashed(p) for p in attempt.iterdir() if p.is_file()}
    save('preservation_baseline.json',{'main_head':git('rev-parse','HEAD',root=main).decode().strip(),
        'main_status_z':git('status','--porcelain','-z','--untracked-files=all',root=main).decode('utf-8'),
        'main_untracked_sha256':{str(p):hashed(p) for p in protected},'original_attempt_manifest':manifest,
        'review_report_sha256':{n:hashlib.sha256(git('show',BASE+':'+OLD+n)).hexdigest() for n in ['INDEPENDENT_REVIEW.md','REVIEW_FINDINGS.json','FLASH_R00_READINESS.md']}})
    print('Baseline recorded: two existing main files, original attempt, review report Git blobs.')
def inspect():
    c=load(DEV+'GAME_UI_FIELD_CATALOG_V0.json');h=load(DEV+'GAME_NATIVE_OBJECT_HINTS_V0.json');a=load(DEV+'GAME_ACTION_DISCOVERY_SEED_V0.json')
    print('CATALOG',list(c),'HINTS',list(h),'ACTIONS',list(a))
    for i,f in enumerate(c['fields']):
        if i<39 or f['entity'] in ['TransactionEvent','SeasonTotals','PlayerGameStatline']:
            print(i,f['field_id'],f['entity'],f.get('native_object_hint'),f.get('native_offset_or_getter_hint'))
    print('ROOTS',[(i,r) for i,r in enumerate(h['roots'])])
    print('GROUPS',h['field_adjacency_groups'])
    print('ACTIONS sample',[(i,x) for i,x in enumerate(a['entries'][:4])])
    print('HUMAN FIELDS',[(i,f['field_id']) for i,f in enumerate(c['fields']) if 'HUMAN_DECISION_20261022' in f['source_refs']])
def preflight():
    out=pathlib.Path(tempfile.mkdtemp(prefix='seed_fix2_preflight_'))
    p=subprocess.run([sys.executable,'-B',str(ROOT/'01_os/06_execution/task_discipline/preflight/preflight_task_context.py'),
        '--packet',str(HERE/'task_packet.yml'),'--repo-root',str(ROOT),'--json'],capture_output=True)
    (out/'stdout.json').write_bytes(p.stdout);(out/'stderr.txt').write_bytes(p.stderr)
    body=json.loads(p.stdout)
    print(json.dumps({'exit_code':p.returncode,'evidence_directory':str(out),'hard_failures':body['hard_failures'],
        'head':body['report']['local_head'],'branch':body['report']['branch_actual'],'dirty':body['report']['dirty_path_count']},ensure_ascii=False))
    raise SystemExit(p.returncode)
if __name__=='__main__':
    {'baseline':baseline,'inspect':inspect,'preflight':preflight}[sys.argv[1]]()
