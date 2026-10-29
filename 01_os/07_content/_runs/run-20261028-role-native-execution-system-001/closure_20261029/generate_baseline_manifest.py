"""Deterministic inventory of fixed Git blobs; no binary analysis or game access."""
import base64
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
D = '08_Domain_Applications/Antigravity_GM_Engine/'
C = D + 'research/rea_native_control/'
R = '01_os/07_content/_runs/run-20261028-role-native-execution-system-001/'
SOURCE = 'bc11fa7926a7eaf390b668515e03dc8507ecb656'
START = '094f1aa641f93dec2277707ad9dbf5bdb0341247'
FORK = '39086984adfa554d36315382d41bc2e5d2e54c39'
GEMINI_OBSERVED = 'ddf85f2863c8c4ba465bc79644036d3e62f056e4'
FREEZE = 'baseline/nba2k22-native-execution-checkpoint-014-20261029'
MANIFEST = C + 'data/NATIVE_EXECUTION_BASELINE_MANIFEST_20261029.json'
DEFERRED = C + 'data/DEFERRED_NATIVE_CAPABILITIES_20261029.json'


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True).stdout


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def emit(path, obj):
    (ROOT / path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def build():
    provenance = {}

    def raw(path):
        value = git('show', SOURCE + ':' + path)
        provenance[path] = {'commit': SOURCE, 'git_blob': git('rev-parse', SOURCE + ':' + path).decode().strip(),
                            'sha256': digest(value), 'bytes': len(value)}
        return value

    def load(path):
        return json.loads(raw(path))

    catalog = load(C + 'data/action_registry.json')
    binding_catalog = load(C + 'data/native_bindings.json')
    read_catalog = load(C + 'data/read_catalog.json')
    coverage = load(R + 'coverage_current.json')
    live = load(C + 'data/native_live_validation.json')
    audit_path = '01_os/07_content/_runs/run-20261027-nba2k22-myleague-native-control-validation-001/07_测试执行/LIVE_OUTCOME_AUDIT.json'
    live_audit = load(audit_path)
    supplement = load(C + 'data/supplemental_requirements.json')
    planning = '01_os/07_content/_runs/run-20261028-nba2k22-role-native-execution-model-001/02_角色执行能力建模/'
    original = load(planning + '三角色及世界控制_原子操作目录_v1.json')['operations']
    crosswalk = load(planning + '既有REA_62动作与需求原子动作交叉表_v1.json')
    for name in ('ROLE_EXECUTION_PROGRESS.md','VALIDATION_RESULTS.md','ROLE_BATCH_EXECUTION.md',
                 'TRAINING_PATCH_CONTRACT.md','ROTATION_MINUTES_CONTRACT.md','PLAYER_PLAYTYPE_NATIVE_CONTRACT.md',
                 'PLAYER_STAT_NATIVE_CONTRACT.md','BADGE_NATIVE_CONTRACT.md','PLAYER_EDITOR_READ_CONTRACT.md',
                 'SIGNING_NATIVE_CONTRACT.md','PLAYER_CONTRACT_READ_CONTRACT.md','FA_OFFER_NATIVE_CONTRACT.md',
                 'OFFER_WITHDRAWAL_NATIVE_CONTRACT.md','DECISION_INFORMATION_DISCOVERY_20261028.md'):
        raw(C + name)
    actions = catalog['actions'];bindings = binding_catalog['bindings'];requirements = coverage['requirements']
    reads = read_catalog['datasets'];action_map = {a['action_id']: a for a in actions}
    assert (len(actions),len(bindings),len(reads),len(requirements)) == (72,65,15,184)
    assert len(original)==183 and len(supplement['operations'])==1
    source_requirements = {a['id']: a for a in original + supplement['operations']}
    assert set(source_requirements)=={a['capability_id'] for a in requirements}
    assert git('merge-base', SOURCE, GEMINI_OBSERVED).decode().strip()==FORK

    managed = []
    paths = git('ls-tree','-r','--name-only',SOURCE,'--',R).decode().splitlines()
    for path in paths:
        if not re.fullmatch(re.escape(R) + r'MANAGED_CHECKPOINT_\d+_EVIDENCE.json',path):continue
        proof = load(path);tests = []
        for check in proof.get('checks',[]):
            end = check.get('finished',{})
            for stream in ('stdout','stderr'):
                key = stream + '_base64'
                if key not in check:continue
                output = base64.b64decode(check[key],validate=True)
                assert digest(output)==end[stream+'_sha256']
                tests += [int(n) for n in re.findall(rb'Ran (\d+) tests?',output)]
        managed.append({'path':path,'candidate':proof['candidate'],'result':proof['result'],
                        'tests_observed_in_retained_output':tests,
                        'managed_inspect_observed':proof.get('managed_inspect_observed'),
                        'evidence_scope':'Historical exact candidate; outputs rehashed, checks not rerun by closure'})
    latest = next(row for row in managed if row['path'].endswith('014_EVIDENCE.json'))
    assert latest['tests_observed_in_retained_output']==[124] and latest['result']['status']=='success'

    binding_rows=[]
    for binding in bindings:
        users=[a for a in actions if any(step.get('binding_id')==binding['binding_id'] for step in a.get('call_sequence',[]))]
        binding_rows.append({'binding_id':binding['binding_id'],'source_record':binding,
            'maturity_assessment':{'source_per_binding_maturity_enum':'NOT_DECLARED_IN_SOURCE',
                'rva_declared':binding.get('rva') is not None,'abi_declared':binding.get('abi'),
                'unresolved_source_unknowns':binding.get('unknowns',[]),
                'referencing_action_ids':[a['action_id'] for a in users],
                'referencing_action_maturities':{a['action_id']:a['capability'] for a in users},
                'new_live_validation':'NOT_RUN','universal_callability_or_live_acceptance':False,
                'note':'Function and layout records are distinct. Empty unknowns/RVA do not prove current object, scene, all arguments, or runtime success.'}})
    action_rows=[]
    for a in actions:
        action_rows.append({'action_id':a['action_id'],'source_record':a,
            'runtime_route_declared':bool(a.get('runtime_handler')),
            'exact_live_overlay':live['actions'].get(a['action_id']),
            'mapped_requirement_ids':[q['capability_id'] for q in requirements if q['native_action_id']==a['action_id']],
            'limits':'Source maturity retained verbatim; handler declaration is not all-input callability or live proof.'})

    counts={'native_action_records':len(actions),'binding_and_layout_records':len(bindings),'read_datasets':len(reads),
            'original_requirements':len(original),'supplemental_requirements':len(supplement['operations']),
            'total_requirements':len(requirements),'historical_mappings':coverage['historical_mapping_count'],
            'effective_mappings':coverage['effective_mapping_count'],
            'requirements_with_call_logic':sum(q['call_logic_available'] for q in requirements),
            'requirements_without_call_logic':sum(not q['call_logic_available'] for q in requirements),
            'action_maturity_histogram':dict(collections.Counter(a['capability'] for a in actions)),
            'requirement_maturity_histogram':dict(collections.Counter(a['native_maturity'] for a in requirements)),
            'read_complete_dataset_count':sum(bool(q['coverage_complete']) for q in reads)}
    engineering_files={}
    for path in git('ls-tree','-r','--name-only',SOURCE,'--',C).decode().splitlines():
        if Path(path).suffix in {'.py','.js','.json','.ps1'}:
            engineering_files[path]=git('rev-parse',SOURCE+':'+path).decode().strip()
    manifest={'schema_version':'nba2k22.native_execution_frozen_baseline.v1','date':'2026-10-29',
        'task_id':'NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01','closure_status':'CLOSED_WITH_DEFERRED_SCOPE',
        'full_goal_complete':False,'fixed_engineering_commit':SOURCE,'original_start_commit':START,
        'game_build_sha256':catalog['game_build_sha256'],'source_pr':18,'engineering_pr':19,
        'freeze_binding':{'branch':FREEZE,'must_equal_final_engineering_head':True,
            'commit_identity':'The Git commit containing these closure files, resolved and verified after commit/push',
            'exact_post_publication_sha_receipt':'NATIVE_EXECUTION_CLOSURE_RECEIPT_20261029.json in the parent workspace and final Human report',
            'self_reference_note':'A file cannot contain its own containing commit hash. Fixed source SHA above pins all engineering records; final freeze ref pins this closure tree.'},
        'counts':counts,'count_semantics':'Registration, mapping, parameter-specific call logic, exact live example and full acceptance are distinct.',
        'actions':action_rows,'bindings_and_layouts':binding_rows,
        'read_datasets':reads,'role_read_dispositions':coverage['read_datasets'],
        'requirements':[{'capability_id':q['capability_id'],'original_requirement':source_requirements[q['capability_id']],
                         'current_disposition':q} for q in requirements],
        'source_crosswalk':crosswalk,'supplemental_catalog':supplement,
        'exact_live_validation_overlay':live,'retained_live_outcome_audit':live_audit,
        'legacy_prior_live_tags':[{'action_id':a['action_id'],'source_evidence':a.get('evidence',[]),
             'scope_note':a.get('scope_note'),'current_input_generalization':False} for a in actions if a['capability']=='PRIOR_LIVE_SUCCESS'],
        'verification':{'new_game_tests':'NOT_RUN','historical_managed_checkpoints':managed,
            'latest_tested_candidate':latest['candidate'],'latest_test_count':124,
            'latest_run':latest['result']['status'],'latest_inspect':latest['managed_inspect_observed'],
            'independent_acceptance':'NOT_RUN','UI_or_save_reload_acceptance':'NOT_PROVEN'},
        'unavailable_or_unconfirmed':{
            'no_runtime_handler_actions':[a['action_id'] for a in actions if not a.get('runtime_handler')],
            'requirements_without_call_logic':[q['capability_id'] for q in requirements if not q['call_logic_available']],
            'binding_unknowns':{b['binding_id']:b['unknowns'] for b in bindings if b.get('unknowns')},
            'actions_without_exact_effect_overlay':[a['action_id'] for a in actions if not str(live['actions'].get(a['action_id'],{}).get('status','')).startswith('REAL_NATIVE_EFFECT_VERIFIED')],
            'all_new_checkpoint_features_require_separate_live_scene_evidence':True},
        'gemini':{'branch':'gemini_rea','observed_head_at_closure_start':GEMINI_OBSERVED,'historical_fork':FORK,
                  'source_history_includes_checkpoint014_finalization':False,'research_reviewed_this_task':False},
        'fixed_engineering_file_blobs':engineering_files,'source_files':provenance}
    emit(MANIFEST,manifest)

    group_specs={
      'COACH_OPPONENT_GAMEPLAN':('教练对手Gameplan','恢复指定owner/opponent持久对象、提交路径和独立回读；ensure存在不证明完整编辑。','复核一个明确对手计划的对象、ABI和持久提交'),
      'PERSONAL_DEFENSE_18':('18项个人防守','每个字段需原生索引/枚举、指定对手球员身份、Setter/Apply及不相关字段保持。','一次只接收一个已闭合个人防守字段'),
      'PLAYBOOK_68_SLOTS':('Playbook的68个槽位','68为槽位容量，不是68个已实现函数；需球队Book身份、槽/Play引用、增删替换和刷新回读。','恢复一个指定槽位的替换事务并验证边界'),
      'FREELANCE_AND_COACH_SETTINGS':('Freelance与教练剩余设置','恢复4槽Freelance及系统/ACE/自动化/帮助防守等；现有POE和部分设置仅保留各自已实现范围。','分别接收Freelance一槽或一个剩余Coach字段'),
      'STARTERS_AND_ROTATION':('首发和完整轮换','精确分钟0..48已实现离线；首发/顺序/情景五人组/比赛换人需独立Native链、轴与身份验证。','先复核指定首发或一个完整轮换事务'),
      'TRAINING_AND_DEVELOPMENT':('训练与球员培养控制','已有团队日历/强度/RAW patch；个人训练/恢复/导师与单位/标签及Native消费链仍需闭合。','选择一个个人训练或导师事务并恢复消费/回读'),
      'GM_CONTRACT_COMPLETION':('GM合同签约完成链','报价提交与撤回不是完成签约；需个体响应/延迟确认、阶段、资格、名单/工资/合同最终变化及选项/续约链。','选择明确签约阶段和一个个体完成事务；禁止整池自动决策处理器'),
      'STAFF_AND_ROSTER':('员工与球队名单业务','需名单/球队/员工身份、签雇裁及对应业务规则、事务刷新和独立读回；禁止靠直接改归属替代。','选择一个明确名单或员工事务'),
      'DRAFT_SCOUT_AND_PICK_RIGHTS':('选秀、球探与选秀权','已恢复选择/部分球探服务仍需真实阶段与指定资产验证；满槽append拒绝保留，Goal写入不证明报告/消费。','在后续批准场景复核一个指定签权或球探消费链'),
      'GM_TRADE_REMAINING':('交易剩余覆盖','历史两名球员精确包成功不推广到签权/混合/多方；批次协商和Native内部检查需按指定资产覆盖。','分别审核指定签权或混合资产包'),
      'PLAYER_EDIT_REMAINING':('球员编辑剩余范围','PlayType/属性倾向/Badge已有离线子集；身体/伤病/资料/潜力等未闭合，普通角色权限不自动扩大。','仅接收独立小字段合同；Potential/父对象复制保持不可调用'),
      'EXTERNAL_PLAYER_REQUESTS':('球员外部请求','本地outbox已实现，外部人格/消息传递/业务决定属于独立系统；不得将请求误记Native调用。','未来角色宿主任务对接本地请求，不制造Native函数'),
      'WORLD_CONTROL_DEFERRED':('世界控制保留需求','原始世界设置/规则/日期推进等保留，未经明确另批不恢复或调用。','Human另行选择世界控制任务')}

    def group(q):
        name=q['capability_id']
        if name.startswith('COACH.DEFENSE.'):return 'PERSONAL_DEFENSE_18'
        if name.startswith('COACH.PLAYBOOK.OPPONENT_'):return 'COACH_OPPONENT_GAMEPLAN'
        if name.startswith('COACH.PLAYBOOK.FREELANCE_') or name.startswith('COACH.STRATEGY.'):return 'FREELANCE_AND_COACH_SETTINGS'
        if name.startswith('COACH.PLAYBOOK.'):return 'PLAYBOOK_68_SLOTS'
        if name.startswith('COACH.ROTATION.'):return 'STARTERS_AND_ROTATION'
        if name.startswith('TRAIN.'):return 'TRAINING_AND_DEVELOPMENT'
        if name.startswith('GM.CONTRACT.'):return 'GM_CONTRACT_COMPLETION'
        if name.startswith(('GM.STAFF.','GM.ROSTER.')):return 'STAFF_AND_ROSTER'
        if name.startswith(('GM.SCOUT.','GM.DRAFT.')):return 'DRAFT_SCOUT_AND_PICK_RIGHTS'
        if name.startswith('GM.TRADE.'):return 'GM_TRADE_REMAINING'
        if name.startswith('PLAYER.EDIT.'):return 'PLAYER_EDIT_REMAINING'
        if name.startswith('PLAYER.AGENCY.'):return 'EXTERNAL_PLAYER_REQUESTS'
        if name.startswith('WORLD.'):return 'WORLD_CONTROL_DEFERRED'
        raise ValueError(name)
    groups=[]
    for gid,(name,steps,next_task) in group_specs.items():
        items=[]
        for q in requirements:
            if group(q)!=gid:continue
            a=action_map.get(q['native_action_id'],{})
            items.append({'requirement_id':q['capability_id'],'requirement_origin':q['requirement_origin'],
                'meaning':q['meaning'],'existing_action_id':q['native_action_id'],'kind':q['kind'],
                'source_maturity':q['source_maturity'],'native_maturity':q['native_maturity'],
                'call_logic_available':q['call_logic_available'],'remaining_gaps':q['remaining_gaps'],
                'missing_technical_steps':[steps,'真实当前构建/对象/场景与独立观察、UI/Save轴按后续任务范围分别证明；本次未运行'],
                'credible_evidence':{'fixed_source_commit':SOURCE,'coverage_source':R+'coverage_current.json',
                    'action_evidence':a.get('evidence',[]),'historical_exact_live_evidence':q.get('historical_exact_live_evidence')},
                'suggested_next_task':next_task,'status':'DEFERRED_NOT_AUTHORIZATION'})
        groups.append({'group_id':gid,'domain':name,'requirement_count':len(items),'items':items})
    groups.append({'group_id':'NATIVE_READ_AND_DATA_INTEGRATION','domain':'尚未完成的原生读取和数据接入',
        'requirement_count':0,'items':[],'read_datasets':[{'dataset_id':s['dataset_id'],'action_id':s['action_id'],
            'maturity':s['capability'],'coverage_complete':s['coverage_complete'],
            'available_scope':s['available_scope'],'missing_technical_steps':s.get('coverage_unknowns',[])+[
                '将可信采集接入角色数据源，证明当前save/scene/identity/time；不把host标签当Native认证'],
            'credible_evidence':s.get('evidence',[]),'suggested_next_task':'从既有世界数据候选复用来源，单独建立选择性Reader/角色投影适配任务'} for s in reads],
        'cross_references':'READ-kind original requirements remain exactly once in their business groups; these15 datasets are a separate coverage axis.',
        'world_candidate':'a3927fb150a213201e404cca043ced4f57409bd1; not merged or accepted by this closure',
        'shot_chart':'114/28/2 byte types and14x2 layouts remain static leads; enum/entity/time/live bindings require future evidence'})
    deferred={'schema_version':'nba2k22.deferred_native_capabilities.v1','date':'2026-10-29',
        'closure_status':'CLOSED_WITH_DEFERRED_SCOPE','full_goal_complete':False,'fixed_engineering_commit':SOURCE,
        'freeze_branch':FREEZE,'all_original_requirements_retained':True,'original_requirement_count':183,
        'supplemental_requirement_count':1,'total_requirement_dispositions':sum(g['requirement_count'] for g in groups),
        'interpretation':'Every requirement keeps its actual implementation and remaining validation/integration limits. An implemented subset is not reset to unimplemented. External requests are not missing Native functions.',
        'no_new_task_authority':True,'groups':groups}
    assert deferred['total_requirement_dispositions']==184
    assert next(g for g in groups if g['group_id']=='PERSONAL_DEFENSE_18')['requirement_count']==18
    emit(DEFERRED,deferred)
    print(json.dumps({'source':SOURCE,'counts':counts,'managed_receipts':len(managed),'deferred_groups':len(groups),
                      'new_game_access':False,'full_goal_complete':False},ensure_ascii=False))


if __name__=='__main__':
    build()
