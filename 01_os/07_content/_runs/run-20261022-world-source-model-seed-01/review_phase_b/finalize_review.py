"""Build review-only deliverables from pinned blobs; verify preservation and scope."""
import collections
import hashlib
import json
import pathlib
import subprocess
import yaml

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[4]
RUN = HERE.parent
CAND = '142531f2d60813bce5b90254c5e347050c40b406'
BASE = '407e2134bd2f595477099b2c6e3484c818059fd9'
ARCH = '734188ab378974cf1d4426e67c675de561aac692'
SESSION = '01a1676e-e700-7691-ac54-9e74af1ae21b'
DEV = '08_Domain_Applications/Antigravity_GM_Engine/docs/development/'
PREFIX = RUN.relative_to(ROOT).as_posix() + '/'

def git(*args):
    return subprocess.check_output(['git', '--no-optional-locks', *args], cwd=ROOT)

def pinned(name):
    return git('show', CAND + ':' + DEV + name)

def write(path, value):
    with path.open('w', encoding='utf-8', newline='\n') as target:
        target.write(value.rstrip() + '\n')

def save(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

catalog = json.loads(pinned('GAME_UI_FIELD_CATALOG_V0.json'))
queue = json.loads(pinned('FLASH_R00_PRIORITY_QUEUE_V0.json'))
tasks = next(v for v in queue.values() if isinstance(v, list) and v and isinstance(v[0], dict) and 'id' in v[0])
audit = json.loads((HERE / 'stage_a_evidence_audit.json').read_bytes())
sem = json.loads((HERE / 'semantic_counterexamples.json').read_bytes())
catalog_lines = pinned('GAME_UI_FIELD_CATALOG_V0.json').decode('utf-8').splitlines()
queue_lines = pinned('FLASH_R00_PRIORITY_QUEUE_V0.json').decode('utf-8').splitlines()

def loc(name, needle, pointer=None):
    lines = catalog_lines if name == 'GAME_UI_FIELD_CATALOG_V0.json' else queue_lines
    line = next(i for i, text in enumerate(lines, 1) if needle in text)
    return {'path': DEV + name, 'line': line, 'json_pointer': pointer}

def finding(fid, severity, title, locations, evidence, impact, fix, criteria):
    return dict(finding_id=fid, severity=severity, title=title, locations=locations,
                evidence=evidence, impact=impact, minimum_fix=fix, verification_criteria=criteria)

findings = [
finding('B-01', 'MAJOR', 'R00 队列未提供足够的按目标调查边界和后段对象锚点',
    [loc('FLASH_R00_PRIORITY_QUEUE_V0.json', '"R00-10"'),
     loc('FLASH_R00_PRIORITY_QUEUE_V0.json', '"R00-11"'),
     loc('FLASH_R00_PRIORITY_QUEUE_V0.json', '"R00-12"'),
     loc('FLASH_R00_PRIORITY_QUEUE_V0.json', '"read_only_method"')],
    ['12 项 read_only_method 完全相同，12 项 negative_control 完全相同；no-stat/unplayed 不能直接定义世界身份、设置或操作目录的反例。',
     'R00-10 仅引用 PLAYER、ROSTERDATA 和 world_draft_season；没有绑定 save_context/DEV14 的身份与重置证据。world_draft_season 不是存档连续性证明。',
     'R00-11 仅引用 ROSTERDATA，field_refs 为空；既有 config/state_io_native/world.json 的 SLOT_SETTINGS、SLOT_TRADE、SLOT_SLIDERS、SLOT_FRANCHISE 未链接。',
     'R00-12 仅引用 PLAYER，field_refs 为空；未链接 GAME_ACTION_DISCOVERY_SEED_V0.json 的具体 action 或各领域只读来源。'],
    'Flash 仍需自行猜测跨对象身份、调查起点与边界；机械满足字段非空不能证明可以低成本独立执行全部 12 项。',
    '仅修订 12 行任务及必要引用：按目标列明来源、待答问题、起点、依赖、限定对象/记录/区域或时间预算、匹配正反例与可检验交付。10 链接已有存档绑定证据；11 链接实际设置资料；12 链接具体 action 与被动调查对象。不能获得样本时保留 UNKNOWN 并交接；不要求新增 Reader 或现场调查。',
    ['每项可从固定引用定位起点，调查边界在执行前可确定；负样本说明应出现或不应出现什么。',
     '10 明确相同存档连续性、不同存档隔离与无法证明时 HOLD；不要求本轮切换或加载存档。',
     '11 区分默认配置与游戏观察，12 可枚举被审 action，且全部保留禁止执行。',
     '保留“两条失败路径后升级”等总契约，并在行内引用；不得以 UNKNOWN 数量下降作为唯一验收。']),
finding('B-02', 'MAJOR', '字段目录将部分资产及统计事实归属到错误的概念实体',
    [loc('GAME_UI_FIELD_CATALOG_V0.json', '"AG01D.UI.ROOKIE_REPORT.draft_pick_original_team"', '/fields/11'),
     loc('GAME_UI_FIELD_CATALOG_V0.json', '"AG01D.UI.ROOKIE_REPORT.draft_pick_owner_team"', '/fields/12'),
     loc('GAME_UI_FIELD_CATALOG_V0.json', '"AG01D.UI.SEASON_STATS.season_points"', '/fields/19')
     if any('"AG01D.UI.SEASON_STATS.season_points"' in x for x in catalog_lines)
     else {'path': DEV+'GAME_UI_FIELD_CATALOG_V0.json', 'line': 1147, 'json_pointer':'/fields/19'},
     {'path':DEV+'GAME_UI_FIELD_CATALOG_V0.json','line':1818,'json_pointer':'/fields/33'}],
    ['fields/11、12 的 source 指向 DRAFT_ASSETS 的原始球队和当前持有球队，但 entity 均为 TransactionEvent。13–16 同一页面的选秀轮次/年份/球员资料也不能因页面名而一律作为交易事件。',
     'fields/17–19 的赛季出场、首发和得分累计被标为 Game；fields/33 的 player_statline 也被标为 Game。',
     'ARCH 候选已有 DraftPick、PickOwnership、SeasonTotals、PlayerGameStatline 等概念；模型表列齐 44 名称不保证逐字段语义归属正确。'],
    '归属决定身份、时间与重复粒度。将持有状态当交易事件、赛季累计当单场比赛，会误导 Flash 的对象关系调查和后续事实键设计。',
    '仅更正已证实反例及同一生成规则涉及的行；区分原始来源对象与目标语义实体/投影。选秀权与持有状态分别链接 DraftPick/PickOwnership，赛季累计链接球员/赛季及可用的 stint，单场球员数据链接 PlayerGameStatline 和比赛/球员/球队。未知关系继续 UNKNOWN。原始来源值和历史状态不得覆盖。',
    ['逐条展示上述反例的来源对象、语义实体和关联键，字段不再由页面名默认分配错误实体。',
     '赛季累计与单场事实明确不同粒度；选秀资产、持有快照与交易事件明确区分。',
     '新增少量语义断言验证这些反例；无需重写 888 行或新建物理 Schema。']),
finding('B-03', 'MINOR', '阶段 A 报告计数与原 attempt 严格目录契约不一致',
    [{'path':PREFIX+'OS_MACHINE_VERIFICATION_REPORT.md','section':'阶段 A 证据清单/第 6 节'},
     {'path':audit['original_attempt'],'field':'directory file set'}],
    ['磁盘为 54 文件；OS 规范要求 53，必需文件缺失为 0；额外项为 WORLD_SOURCE_MODEL_SEED_01_OS_MACHINE_VERIFICATION_REPORT.md。',
     '本轮 original Inspect=3（unexpected_or_missing_attempt_files）；53 文件逐字节副本 Inspect=0。历史报告所述 43 与磁盘不符。',
     '10 项 finished 记录均为 exit_code=0；日志 hash、候选 SHA、干净 source 快照一致。没有独立见证原先 managed run/inspect 进程退出瞬间。'],
    '核心机器结果有原始证据支持，但不能声称当前原目录严格 Inspect 通过；额外报告与计数问题不构成架构否决。',
    '由证据所有者追加更正说明，区分历史报告、原目录现状、53 文件派生副本及其 hash。保留原目录。如后续消费方硬性要求 pristine attempt，通过另行授权的验证生成新 attempt；本审核不删除原件、不伪造原始通过。',
    ['更正说明可重算 53+1=54，明确无缺失、原 Inspect=3、副本 Inspect=0。',
     '原 attempt 清单和 hash 保持不变，副本不得冒充新一轮运行或修复后的原始证据。']),
finding('B-04', 'MINOR', '倾向字段继承了相互不兼容的定位线索及错误研究邻域',
    [loc('GAME_UI_FIELD_CATALOG_V0.json', '"AG01D.UI.PLAYER_CARD.player_tendencies"', '/fields/10'),
     {'path':DEV+'GAME_UI_FIELD_CATALOG_V0.json','line':16342,'json_pointer':'/fields/374'}],
    ['AG01D player_tendencies 历史提示为 PLAYER+0x170..0x260，且 discovery_group_ref=NH_CAREER，next_probe 指向职业历史组。',
     'R04/profile 的倾向原生槽提示为 PLAYER+0x458..0x4BA；目录已有 NH_TENDENCIES，却没有将上述矛盾并列为冲突关系。',
     '所有候选仍非当前存档认证，因此本 finding 不判定哪个地址正确。'],
    'Flash 可能沿职业历史区域调查倾向，并将未解决历史偏移当作互不相关的候选，增加错误读取与重复调查成本。',
    '给相关历史提示增加明确冲突/替代来源与 build 状态，修正 next_probe 的语义组；版本或对象基址不足时保持 UNKNOWN，不选定地址、不执行读取。',
    ['读取该倾向项即可发现两套历史定位及未解决原因；不再把 NH_CAREER 当倾向的实际邻域。',
     '保留来源原文，当前认证仍为 false，未解决冲突不会自动成为 canonical 等价。']),
finding('B-05', 'MINOR', '六个 Human 决策符号引用缺少可机器定位的注册映射',
    [loc('GAME_UI_FIELD_CATALOG_V0.json', 'HUMAN_DECISION_20261022')],
    ['source_refs 中六个 HUMAN_DECISION_20261022 不是路径/JSON Pointer，现有目录没有对应解析映射。',
     '同任务 human_task.md 第 3 行确有年龄候选公式等 Human 要求；不是 Human 决策内容缺失。'],
    '消费者可以读到公式，却不能仅凭 source_refs 自动追到持久化裁决；不要把缺映射误报成没有授权或没有来源。',
    '为该符号注册同任务 human_task.md 的准确路径/节或行及固定候选，或改成直接持久化引用；无需改变公式。',
    ['六个引用均可机械解析到相同原始 Human 记录。',
     '公式仍为 Human 优先派生规则，不冒充引擎公式；缺输入仍 UNKNOWN。'])
]

# The active goal's thread ID is authoritative; onboarding memory is another session.
human_path = HERE/'HUMAN_REVIEW_INDEPENDENCE_UPDATE.md'
human_text = human_path.read_text(encoding='utf-8').replace('审核会话为01a16553-fc22-7280-bf52-4fce0302c7ea；本会话此前做知识接入，未生成该候选。',
    '审核会话为'+SESSION+'；此前知识接入会话01a16553-fc22-7280-bf52-4fce0302c7ea仅为历史上下文来源。当前审核会话未生成该固定候选。')
write(human_path, human_text)

data = {'schema_version':'nba2k22.independent_review_findings.v1','task_id':'NBA2K22-OS-INDEPENDENT-REVIEW-01',
    'candidate_sha':CAND,'base_sha':BASE,'arch_reference_sha':ARCH,'review_session_id':SESSION,
    'verdict':'fix_required','severity_counts':dict(collections.Counter(f['severity'] for f in findings)),
    'independence':{'different_model_family':False,'independent_session_required':True,
        'candidate_generation_participation':False,'human_override_ref':'review_phase_b/HUMAN_REVIEW_INDEPENDENCE_UPDATE.md',
        'same_family_is_blocker':False,'exact_runtime_variant':'not independently observable'},
    'findings':findings}
save(RUN/'REVIEW_FINDINGS.json',data)

rows=[]
plans=[
('可作为起点；需限定枚举范围','ROSTERDATA 目录；先记录根有效性与样本对象身份，空项/无效指针为反例，不扩大枚举。'),
('可作为起点；需补派生规则链','PLAYER、birth_year、years_pro；补 original_draft_year 的来源及缺值反例，不要求独立年龄槽。'),
('可作为起点；需限定权限及范围','属性已知偏移；限定可读白名单，Potential 不向普通角色导出，未知编码停止。'),
('需先处理 B-04','倾向 0x458..0x4BA 历史提示；展示 AG01D 冲突，未校准前不选地址。'),
('可作为起点；编码仍未知','Badge 候选区域；2-bit 无法直接代表五级，需另解锁位/组合假设；不强推编码。'),
('可作为起点；需明确记录粒度','SEASON/PLAYER_STATS；限定球员及赛季样本，累计与外部派生分别保存，先处理 B-02 相关映射。'),
('可作为起点；需补跨对象键','Stats 48-byte 候选；限定一组已知比赛/球员，统计为空的反例，禁止把 slot 当全局身份。'),
('可作为起点；需限定 Bank 调查','统计 Bank 与比赛键；先核验 Slot44 不是赛程表的历史纠正，未比赛样本不产生虚构数据。'),
('可作为起点；需页面专用对照','只观察已经可见的 PC22 页面；分开已见/未见/研究虚拟分组，不能以无统计作为页面不存在证明。'),
('未就绪：B-01','链接已有 save_context/DEV14 绑定和 ARCH 身份规则；用现存离线证据比较，同存档连续性未知则 HOLD，不启动切档。'),
('未就绪：B-01','链接 state_io_native/world.json 设置/交易/滑块/联盟槽及 source_catalog；默认值不当观察。'),
('未就绪：B-01','链接具体 action_id 和相应领域来源，按小批目录被动核对依赖/副作用；无执行、无 setter、无批准推断。')]
for task,(status,change) in zip(tasks,plans):
    rows.append('| '+task['id']+' | '+task['target']+' | '+status+' | '+change+' |')
write(RUN/'FLASH_R00_READINESS.md', '''# Flash R00 就绪性 · 阶段 B

固定候选：`'''+CAND+'''`。总体结论：**NOT_READY_AS_COMPLETE_QUEUE / fix_required**。本审核不启动 Flash，也不授予游戏访问权限。前九项可用作规划种子，不表示已经具备现场执行许可或全部执行条件。

12 项都有问题、来源、预期结果、停止条件和禁止写入标记；总契约也提供 UNKNOWN、失败升级与成熟度隔离。但行内方法和负样本完全相同，尤其后三项缺少对应目标的直接来源。这不满足“交给 Flash 后无需重新猜测工程架构”的完整要求。详见 B-01、B-02、B-04。

| 任务 | 目标 | 静态就绪判断 | 最小补充与限制 |
| --- | --- | --- | --- |
'''+ '\n'.join(rows)+'''

每项任务修订后，必须能明确回答：从哪条历史来源开始、限定看哪些对象/记录/字节区域或观察时长、正反例预期是什么、用什么持久化结果回答问题、何时 UNKNOWN/停止/升级。边界可以引用已有小批调查模板，不必现在写 Reader 或强填所有偏移。静态模型能够确定的关系先离线完成；现场样本只有在后续独立授权、重新验证 build/save/identity 后才能采集。

统一结果应包含 build、save/binding/batch 范围、来源路径/版本、假设与实际观察分列、对象/字段关系、样本及反例、失败路径、UNKNOWN 原因和下一步。邻域链接不得升级为物理邻接；静态 getter/codec 不升级为操作权限。12 行修订并通过针对性复核之后，再由 Human 决定是否启动具体小批次。
''')

finding_text=[]
for f in findings:
    lines=['## '+f['finding_id']+' · '+f['severity']+' · '+f['title']]
    lines+=['', '定位：'+'；'.join(x['path']+(':'+str(x['line']) if 'line' in x else '')+((' '+x['json_pointer']) if x.get('json_pointer') else '') for x in f['locations']), '', '证据：'+' '.join(f['evidence']), '', '影响：'+f['impact'], '', '最小修订：'+f['minimum_fix'], '', '验收：'+' '.join(f['verification_criteria'])]
    finding_text.append('\n'.join(lines))
write(RUN/'INDEPENDENT_REVIEW.md', '''# WORLD-SOURCE-MODEL-SEED-01 独立审核 · 阶段 B

**技术结论：fix_required。** 两项 MAJOR、三项 MINOR；没有以 UNKNOWN 数量、同属 GPT-6 或证据计数笔误作为架构阻断。V0 方向可保留，但字段语义归属与 R00 完整可执行性需要小范围修订。本报告不修复七项候选成果。

审核者会话：`'''+SESSION+'''`；固定候选 `'''+CAND+'''`；来源 master `'''+BASE+'''`；ARCH 参考 `'''+ARCH+'''`，后者仍是候选参考，未提升为主线权威。

## 四项独立判定

| 判定层 | 结论 | 边界 |
| --- | --- | --- |
| 阶段 A 机器证据 | 必需证据完整，10/10 原记录支持成功；原目录当前严格 Inspect 不通过 | 54 实际文件，53 必需，无缺失；原 Inspect=3，逐字节 53 文件副本 Inspect=0；不能独立见证历史进程退出瞬间 |
| 架构与业务语义 | fix_required | 七域及 44 名称映射方向可保留；字段级存在 B-02，不能称全量语义通过 |
| Flash R00 | NOT_READY_AS_COMPLETE_QUEUE | 1–9 可作为附带条件的规划种子，10–12 锚点不足；没有启动授权 |
| master 集成与 Human 决策 | PENDING | 仅本地审核分支交付，无 merge/push，无独立集成验收 |

## 独立性与 preflight

Human 在本会话明确允许不同 GPT-6 会话审核，并授权更新领域规则。`different_model_family=false` 如实披露；同族不再构成本轮硬门。要求不同会话、独立上下文、未参与候选生成，且实际检查原始材料。裁决见 `review_phase_b/HUMAN_REVIEW_INDEPENDENCE_UPDATE.md`；三份领域协作文档同步修订，历史任务包不改写。此规则文档更新属于 Human 授权的单独范围，不是候选技术整改；本报告不对自己的规则改动作独立验收。

独立审核工作树从固定候选创建，分支 `review/world-source-model-seed-01-phase-b`。原 Stage A worktree 现为 detached HEAD 且有未跟踪报告，当前 preflight 因 dirty/branch mismatch 返回 1，不能声称本轮 preflight 全绿；候选 SHA、基线祖先关系与原证据中的 clean source snapshot 一致。该历史工作树状态不改变固定 Git 对象。原主工作区及历史 attempt 不修改，最终保存校验另见证据指针。

## 方法与可支持范围

使用固定 Git blob 检查七项成果，离线解析目录、来源 JSON Pointer、12 行任务与 44 实体名称；对照 ARCH 五项概念成果、R01/R02/R04/R05/R06/R07、AG01C/01D 及 native/profile/catalog 配置的相关来源与高风险片段。全量统计/引用解析不等于逐项原生语义认证；业务判断针对高风险关系和可复查反例。脚本及结构化输出位于 `review_phase_b/`，未运行游戏 Reader 或重新执行阶段 A 十项检查。

原 attempt 的 started/finished/source/stdout/stderr 与聚合记录实际存在；stdout/stderr hash 与记录一致，source SHA/树和 clean 状态一致。原 attempt 未删除、移动或修改。副本是预期 53 项的派生子集，既不是原目录修复，也不是新一轮 Managed Verify。原报告“43 文件”需更正；原目录多出的报告导致严格文件集合校验失败，详见 B-03。

## 架构与成熟度审查

- 七大领域覆盖概念入口，ARCH 44 实体名称完整对应；仍需保持实体语义、原始来源对象和 UI 页面分组的区别。B-02 说明仅数齐名称不足以通过语义审核。一个存档一个独立连续世界、不分叉、不继承其他存档动态历史的原则保留；历史 native ID/slot 仍须带 world/binding/batch 范围。
- L0 原始证据、L1 已认证游戏事实、L2 外部派生的隔离合理；原生累计与高级统计应保留来源观察，外算结果另存。UNKNOWN、PARTIAL、CONFLICT、NOT_APPLICABLE、WITHHELD 有区分，不应通过强推数据消除 UNKNOWN。
- 六类年龄字段区分正确。`original_draft_year - birth_year + years_pro` 是 Human 优先派生规则，尚非引擎算法；display_age_observed 单独保存，缺输入仍 UNKNOWN，不要求找到独立年龄槽。Potential 的敏感字段显式隔离，其余未分类字段 fail closed；自然成长仍由引擎决定。本审核没有检验未来 Reader 的实际权限执行。
- 888 是研究行，520 个类型 UNKNOWN 合法；404 个邻域关联均不能当物理证明，29 页面/研究组不能当 29 个实测 UI 页面。当前认证/全枚举标记没有被批量提高。来源指针大部分可解析，六个人工符号引用另列 B-05。未证明 canonical 等价的行保留未解决状态是正确的。
- 207 个 action 的实际写入、readback、save/reload、production 资格均为 false。只读发现不生成执行许可，历史静态 codec/getter 不当生产能力；未来写入仍需身份、状态依赖、关联对象、持久化验证及 Human 批准。
- Native hints 的邻域和指针是版本化调查线索；badge 编码及 Slot44 等历史纠正不能被忽略。B-04 记录一处明确可复查的错误调查组和偏移冲突。本审核不判定当前游戏地址。

## Findings

'''+ '\n\n'.join(finding_text)+'''

## 执行者理由的独立评估与收口

生产者的“目录覆盖、默认禁止执行、来源保留、UNKNOWN 不强填”有原始结构支持；机器检查可以证明这些约束和计数。它们不能证明逐字段实体分配正确，也不能证明复制的通用调查方法足以让 Flash 独立调查世界身份/设置/操作目录。B-01/B-02 是静态检查通过仍不足以支持技术放行的直接反例。

修订可限于具体队列行、实体归属和来源冲突/决策映射，不需要重做架构、重写 888 行或新开发 Reader。由候选生产者提交新 SHA 和修订证据，再对上述修复标准定向复核。阶段 A 目录问题单列流程说明，不冒充缺失核心证据。Human 集成决定、Flash 启动和实机认证继续独立。本次审核完成后停止。
''')

refs=['stage_a_evidence_audit.json','catalog_analysis.json','architecture_mapping_audit.json','semantic_counterexamples.json']
save(HERE/'MINIMUM_WORK_UNIT_OUTPUT.json', {'minimum_work_unit_output':{
    'role':'independent_review',
    'work_performed_or_requested':'完成固定候选的原始机器证据、架构语义和 Flash R00 就绪性独立审核，并记录 Human 授权的领域独立性规则修订。',
    'implementation_or_review_method':'从固定 Git 对象离线解析目录和引用，检查原始 attempt 与日志摘要，用具体实体反例和逐任务队列对照检验生产者主张。',
    'supportability_rationale':'十项机器记录支持结构约束与成功记录；错误实体归属和缺乏目标锚点的任务构成可复查反例，因此不能支持整体放行。',
    'feasibility_rationale':'最小整改只需修改特定队列行、语义映射与来源记录，保留合法 UNKNOWN，无需实机调查或新建 Reader，适合生产者下一轮定向修订。',
    'verdict':'FIX_REQUIRED','primary_evidence_examined':refs,
    'findings_and_residual_risk':'B-01/B-02 为 MAJOR；B-03 至 B-05 为 MINOR。原 Inspect 当前失败、同族经 Human 许可、实机与集成仍未认证。',
    'executor_rationale_assessment':{
        'supportability_assessment':'计数与默认禁止的理由由原始记录支持；覆盖完整不能推出实体正确，字段反例直接推翻全量语义就绪主张。',
        'feasibility_assessment':'前九项可作有条件种子，但后三项尚需重新查找真正对象锚点，统一负样本不能支撑低成本独立执行全部队列。',
        'primary_evidence_refs':refs,
        'unsupported_or_inferred_claims':['888 行等于已认证原生字段不成立','通用方法和字段非空等于 R00 全量可执行不成立','派生副本 Inspect 通过不能证明原目录当前通过']}}})

original=pathlib.Path(audit['original_attempt'])
manifest={p.name:{'bytes':p.stat().st_size,'sha256':digest(p)} for p in original.iterdir() if p.is_file()}
assert manifest == audit['original_manifest'], 'Original attempt changed'
seven=['GAME_DOMAIN_SOURCE_MODEL_V0.md','GAME_UI_FIELD_CATALOG_V0.json','GAME_NATIVE_OBJECT_HINTS_V0.json','GAME_FIELD_LIFECYCLE_RULES_V0.md','FLASH_DISCOVERY_FILL_CONTRACT_V0.md','GAME_ACTION_DISCOVERY_SEED_V0.json','FLASH_R00_PRIORITY_QUEUE_V0.json']
assert all((ROOT/DEV/n).read_bytes() == pinned(n) for n in seven), 'Candidate deliverable modified'
subprocess.check_call(['git','merge-base','--is-ancestor',CAND,'HEAD'],cwd=ROOT)
assert len(catalog['fields']) == 888 and len(tasks)==12
assert len({t['read_only_method'] for t in tasks})==1
assert len({t['negative_control'] for t in tasks})==1
assert catalog['fields'][11]['entity']=='TransactionEvent'
assert catalog['fields'][19]['entity']=='Game'
assert catalog['fields'][33]['entity']=='Game'
packet=yaml.safe_load((HERE/'task_packet.yml').read_bytes())['task_packet']
allowed=packet['allowed_changed_paths']
changed=git('diff','--name-only').decode().splitlines()+git('ls-files','--others','--exclude-standard').decode().splitlines()
outside=[p for p in changed if not any(p==x or (x.endswith('/**') and p.startswith(x[:-2])) for x in allowed)]
assert not outside, outside
pointer={'task_id':'NBA2K22-OS-INDEPENDENT-REVIEW-01','candidate_sha':CAND,'source_master_sha':BASE,
    'arch_reference_sha':ARCH,'review_session_id':SESSION,'verdict':'fix_required','readiness':'NOT_READY_AS_COMPLETE_QUEUE',
    'independence':data['independence'],'branch':'review/world-source-model-seed-01-phase-b',
    'publication':'local_only','master_integration':'PENDING_HUMAN','flash_started':False,
    'original_attempt_unchanged':True,'candidate_seven_deliverables_byte_identical':True,
    'scope_check':'PASS','original_attempt_files':54,'mandatory_attempt_files':53,
    'original_inspect_exit':3,'derived_subset_inspect_exit':0,
    'reports':['INDEPENDENT_REVIEW.md','REVIEW_FINDINGS.json','FLASH_R00_READINESS.md'],
    'evidence_sha256':{p.relative_to(RUN).as_posix():digest(p) for p in sorted(RUN.rglob('*'))
        if p.is_file() and (p.parent==RUN and p.name in ['INDEPENDENT_REVIEW.md','REVIEW_FINDINGS.json','FLASH_R00_READINESS.md'] or HERE in p.parents)
        and p.name not in ['REVIEW_EVIDENCE_POINTER.json','final_verification.json']}}
save(HERE/'REVIEW_EVIDENCE_POINTER.json',pointer)
print(json.dumps({'verdict':data['verdict'],'findings':data['severity_counts'],'candidate_unchanged':True,'attempt_unchanged':True,'scope':'PASS','evidence_files_hashed':len(pointer['evidence_sha256'])}))
