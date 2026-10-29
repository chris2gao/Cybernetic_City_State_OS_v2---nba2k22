"""Check archival consistency only. No reverse engineering, game or candidate code execution."""
import base64
import hashlib
import json
import subprocess
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[5]
D='08_Domain_Applications/Antigravity_GM_Engine/'
C=D+'research/rea_native_control/'
R='01_os/07_content/_runs/run-20261028-role-native-execution-system-001/'
SOURCE='bc11fa7926a7eaf390b668515e03dc8507ecb656'
FREEZE='baseline/nba2k22-native-execution-checkpoint-014-20261029'


def git(*args):
    return subprocess.run(['git',*args],cwd=ROOT,capture_output=True,check=True).stdout


def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf8'))


def original(path):
    return json.loads(git('show',SOURCE+':'+path))


def validate():
    m=load(C+'data/NATIVE_EXECUTION_BASELINE_MANIFEST_20261029.json')
    deferred=load(C+'data/DEFERRED_NATIVE_CAPABILITIES_20261029.json')
    record=load(R+'closure_20261029/CLOSURE_RECORD.json')
    progress=load(R+'PROGRESS_POINTER.json')
    assert m['fixed_engineering_commit']==SOURCE and deferred['fixed_engineering_commit']==SOURCE
    assert m['full_goal_complete'] is False and deferred['full_goal_complete'] is False
    assert m['closure_status']==deferred['closure_status']==progress['goal_state']=='CLOSED_WITH_DEFERRED_SCOPE'
    assert m['freeze_binding']['branch']==FREEZE and progress['frozen_baseline_branch']==FREEZE
    a=original(C+'data/action_registry.json')['actions']
    b=original(C+'data/native_bindings.json')['bindings']
    reads=original(C+'data/read_catalog.json')['datasets']
    q=original(R+'coverage_current.json')['requirements']
    assert [row['source_record'] for row in m['actions']]==a
    assert [row['source_record'] for row in m['bindings_and_layouts']]==b
    assert m['read_datasets']==reads and [row['current_disposition'] for row in m['requirements']]==q
    counts=m['counts']
    assert (len(a),len(b),len(reads),len(q))==(72,65,15,184)
    assert counts['requirements_with_call_logic']==sum(row['call_logic_available'] for row in q)==42
    assert counts['requirements_without_call_logic']==142 and counts['read_complete_dataset_count']==0
    assert all(row['maturity_assessment']['source_per_binding_maturity_enum']=='NOT_DECLARED_IN_SOURCE' for row in m['bindings_and_layouts'])
    items=[item for group in deferred['groups'] for item in group['items']]
    assert len(items)==len({item['requirement_id'] for item in items})==184
    item_map={item['requirement_id']:item for item in items}
    for row in q:
        item=item_map[row['capability_id']]
        assert item['existing_action_id']==row['native_action_id']
        assert item['native_maturity']==row['native_maturity'] and item['call_logic_available']==row['call_logic_available']
        assert item['remaining_gaps']==row['remaining_gaps'] and item['missing_technical_steps']
    groups={row['group_id']:row for row in deferred['groups']}
    assert len(groups['PERSONAL_DEFENSE_18']['items'])==18
    assert len(groups['NATIVE_READ_AND_DATA_INTEGRATION']['read_datasets'])==15
    for key in ('COACH_OPPONENT_GAMEPLAN','PLAYBOOK_68_SLOTS','FREELANCE_AND_COACH_SETTINGS','STARTERS_AND_ROTATION',
                'TRAINING_AND_DEVELOPMENT','GM_CONTRACT_COMPLETION','STAFF_AND_ROSTER','DRAFT_SCOUT_AND_PICK_RIGHTS'):
        assert groups[key]['items']
    assert m['exact_live_validation_overlay']==original(C+'data/native_live_validation.json')
    audit='01_os/07_content/_runs/run-20261027-nba2k22-myleague-native-control-validation-001/07_测试执行/LIVE_OUTCOME_AUDIT.json'
    assert m['retained_live_outcome_audit']==original(audit)
    for path,source in m['source_files'].items():
        raw=git('show',SOURCE+':'+path)
        assert hashlib.sha256(raw).hexdigest()==source['sha256'] and len(raw)==source['bytes']
        assert git('rev-parse',SOURCE+':'+path).decode().strip()==source['git_blob']
    for path,blob in m['fixed_engineering_file_blobs'].items():
        raw=(ROOT/path).read_bytes()
        # Git normalizes text according to the source attributes, without changing the worktree.
        assert git('hash-object','--path='+path,'--',path).decode().strip()==blob,path
    assert m['verification']['latest_test_count']==124
    for entry in m['verification']['historical_managed_checkpoints']:
        proof=load(entry['path'])
        assert proof['candidate']==entry['candidate'] and proof['result']==entry['result']
        for check in proof['checks']:
            for stream in ('stdout','stderr'):
                key=stream+'_base64'
                if key in check:
                    assert hashlib.sha256(base64.b64decode(check[key],validate=True)).hexdigest()==check['finished'][stream+'_sha256']
    run=yaml.safe_load((ROOT/R/'run.yml').read_text(encoding='utf8'))
    assert run['lifecycle']=='deferred' and run['closure_record']=='closure_20261029/CLOSURE_RECORD.json'
    assert record['exclusion_or_deferral']['status']=='CLOSED_WITH_DEFERRED_SCOPE'
    assert record['exclusion_or_deferral']['full_goal_complete'] is False
    assert record['human_acceptance']['post_delivery_artifact_acceptance']=='PENDING_HUMAN_REVIEW'
    assert record['exclusion_or_deferral']['independent_review']=='NOT_RUN'
    packet=yaml.safe_load((ROOT/R/'task_packet.yml').read_text(encoding='utf8'))['task_packet']
    assert not packet['engineering_continuation_authorized'] and packet['current_engineering_scope_closed']
    modules=load(D+'docs/development/PROJECT_MODULE_REGISTRY_V2.json')['modules']
    for mid in ('P03','P04','P05','P06','P07','P08','P09','P10','P12'):
        module=next(row for row in modules if row['id']==mid)
        assert module['native_execution_checkpoint_014']['status']=='CLOSED_WITH_DEFERRED_SCOPE'
        for path in ('research/rea_native_control/TASK_CLOSURE_20261029.md',
                     'research/rea_native_control/GEMINI_NATIVE_INTEGRATION_HANDOFF_20261029.md'):
            assert path in module['docs'] and (ROOT/D/path).is_file()
        assert 'research/rea_native_control/data/NATIVE_EXECUTION_BASELINE_MANIFEST_20261029.json' in module['artifacts']
    index=(ROOT/D/'PROJECT_INDEX.md').read_text(encoding='utf8')
    assert FREEZE in index and 'CLOSED_WITH_DEFERRED_SCOPE' in index
    changed=set(filter(None,git('diff','--name-only','-z',SOURCE).decode().split('\0')))
    changed.update(filter(None,git('ls-files','--others','--exclude-standard','-z').decode().split('\0')))
    allow=(C,D+'docs/development/',R)
    assert all(path.startswith(allow) or path==D+'PROJECT_INDEX.md' for path in changed)
    # The closure may add archival scripts, but must not modify engineering runtime, tests, or source catalogs.
    for path in changed:
        if path in m['fixed_engineering_file_blobs']:
            assert git('hash-object','--path='+path,'--',path).decode().strip()==m['fixed_engineering_file_blobs'][path]
    print(json.dumps({'result':'PASS','checks':'fixed records,184 unique dispositions,provenance,unchanged engineering,indices,OS deferral and scope',
                      'actions':72,'bindings_layouts':65,'datasets':15,'requirements':184,
                      'new_game_access':False,'independent_acceptance':False,'full_goal_complete':False}))


if __name__=='__main__':
    validate()
