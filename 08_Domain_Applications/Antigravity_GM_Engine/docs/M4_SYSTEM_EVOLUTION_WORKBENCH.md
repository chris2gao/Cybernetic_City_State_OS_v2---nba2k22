# M4 系统自我进化工作台

版本 `M4_SYSTEM_EVOLUTION_V1`，任务依据 [DEV20](development_tasks/DEV_20261020_20_M4_SYSTEM_EVOLUTION_ENGINE_IMPLEMENTATION_V1.md)。它管理外挂工程问题、能力缺口、来源不确定性和开发候选；GM篮球经营反馈、3D/Calendar年度校准、BPTI均由独立任务负责。

## 工作方式

所有命令由玩家触发的任务显式调用，无定时扫描、自动push、Issue创建、模型唤醒或Bug修复。复用 `gm_workbench.sqlite`：新增 `development_issues` 当前投影和 `development_issue_events` 追加历史，以及既有component版本登记。M1/M2/M3数据和版本不改变；M4不读取游戏进程、事实库或生产快照。默认工作台与M3一致：`_exports/dev10_m3/gm_workbench.sqlite`，可用 `--workbench` 指定已有派生库；沿用事实目录路径禁写规则。

```powershell
python -B scripts/gm_development_feedback.py ingest --input examples/development_feedback/issue6.json
python -B scripts/gm_development_feedback.py list --status DEFERRED --limit 5
python -B scripts/gm_development_feedback.py show --issue 从list取得的DEV编号 --limit 5
python -B scripts/gm_development_feedback.py show --issue DEV编号 --event-key 从history取得的event_key
python -B scripts/gm_development_feedback.py readiness
python -B scripts/gm_development_feedback.py export --output _exports/m4_handoff_new --limit 10
```

输入上限24KB；单事件规范化后最多14KB。list/show历史默认10、最多50条，SQL只取一页，并有17KB结果预算；可能少于limit，继续使用next_cursor。list支持status/severity/category/career/capability精确筛选。游标绑定筛选及事件水位，池有变动后重新从第一页开始；不同筛选不能混用游标。show的当前问题和单个事件各自有输入结构大小限制，不默认dump全部历史。export每页最多20项，不覆盖已有目录；有下一页时在新输出目录使用相同筛选和游标继续导出。

## 事件输入

完整形状见 [issue6.json](../examples/development_feedback/issue6.json)，未来规划示例见同目录其余三份JSON。输入不是任意工具日志转储；将**已经实际读取的报告**整理成精简事件，保留原报告引用，不为了补事件运行采集、预检或游戏脚本。

| 字段 | 含义 |
| --- | --- |
| event_id / occurred_at | 同一producer和明确scope内稳定事件ID；带时区的证据事件时间。登记报告时说明该时间是报告/整理时间，不能伪装实际游戏故障起点 |
| category / root_cause_key / affected_capability | 固定工程类别、稳定根因键和能力名。错误文本变化不应随意改变根因；不同根因不能复用键 |
| scope | SYSTEM仅含kind；CAREER需career_id，可加save_instance_id；IDENTITY还需save_instance_id和identity_key。由操作者明确判断范围，不自动跨档合并身份问题 |
| source | source_stage/producer必填；career_id/save_instance_id/generation_id/source_batch/run_id/error_code/code_version实际有才填，缺失不补假值 |
| evidence_refs / repro_steps / actual / expected | 相对仓库路径或GitHub HTTPS引用、小型阅读/复现步骤和实际/预期差异。只引用，不嵌raw、私密路径、地址、凭据或巨大JSON |
| confidence | UNKNOWN、RESEARCH、STATIC_REPORT、REPRODUCED_SYNTHETIC、OBSERVED_PRODUCTION。等级是操作者对原证据的描述，M4不替代来源认证；无引用强制降为UNKNOWN/RESEARCH |
| severity / proposed_owner | P0/P1/P2技术严重程度和负责人建议，不代替玩家优先级、立项或消息授权 |
| next_review_trigger / known_limits / related_issue_ids | 再次讨论条件、边界和关联问题；“没有观察到”与“功能不存在”分开 |
| status / player_decision_ref | 导入只可OPEN或带玩家决定引用的DEFERRED，默认OPEN。其余状态由显式triage改变；引用依沿用的操作者信任，不建设认证服务 |
| roadmap_note | 可选未来规划说明，不新增PLANNED状态；规划候选为DEVELOPMENT_FEATURE_CANDIDATE / RESEARCH / DEFERRED |

可用source_stage：CAPTURE、ACCESS、ANALYTICS、GM_INTERFACE、APPROVAL、EXECUTION、HANDOFF、MANUAL_RESEARCH。M0查询错误可引用已有AccessError报告；M3源包/交接阻断可引用已有验证工件；DEV14规划/审批/回读失败引用已有回执，均只整理工程问题。没有报告时保留UNKNOWN，不宣称复现。类别用于路由，不自动将一条推测认证为Bug。

指纹只由category、root_cause_key、scope、affected_capability生成，不含batch/run/title。因此同根因跨批追加到同一问题；不同scope/身份或根因分开。CAREER/IDENTITY事件的幂等键包含producer、event_id及完整scope，同一producer可在不同存档复用局部事件ID；同scope内完全相同为IDEMPOTENT_REPLAY，不增加occurrences/revision，同ID不同内容仍拒绝。SYSTEM表示明确的全局命名空间，保留原producer+event_id键以兼容已登记的系统级问题；系统级事件ID仍须全局唯一，局部存档事件使用CAREER/IDENTITY。occurrences统计独立证据事件数，**不等于游戏实际故障次数**。首次/最近按事件时间归并，处理时间另存。当前问题保留首次描述、最新来源/证据与最新人工分流；历史事件保存每次原描述，不覆盖旧记录。

## 人工分流与决定

仅支持OPEN、TRIAGED、DEFERRED、RESOLVED、DISMISSED。没有APPROVED或自动批准状态。每次triage需实际玩家决定引用和expected-revision，RESOLVED还需修复证据引用；仅作为问题管理状态，不授予开发、游戏执行或正式GM权限。

```json
{
  "status": "DEFERRED",
  "reason": "玩家明确留到后续独立开发窗口",
  "player_decision_ref": "填写真实玩家决定的记录引用",
  "evidence_refs": ["docs/development_reviews/M3_T_IMPLEMENTATION_AND_ACCEPTANCE.md"],
  "next_review_trigger": "玩家另行批准修复范围与最小验证时"
}
```

```powershell
python -B scripts/gm_development_feedback.py triage --issue DEV编号 --input triage.json --expected-revision 从show取得的版本
```

数据库事务及BEGIN IMMEDIATE串行化导入，人工修订使用CAS。新事件不会自动重开RESOLVED/DISMISSED或取消DEFERRED；可积累重复证据，交玩家再决定。过期修订失败且不写新历史。RESOLVED是操作者引用实际决定与证据后的记录，不声称M4亲自执行修复。JSON中的approved=true、execution_authorized等自行授予权限字段被拒绝。

## GitHub交接

export生成CURRENT.md、轻量index.json、readiness.json及按问题ID的小型详情JSON，详情含最近3条历史摘要；完整历史仍由show分页查询。CURRENT包含范围、复现条件、UNKNOWN、建议owner、下次触发条件、玩家决定和证据链接。index带全池状态/严重度计数、当前页和下一页游标，不能把第一页当全池。

默认导出到调用者指定的新本地目录；之后仅在玩家授权的文档/代码同步任务中选择提交文件。本轮开发PR纳入4条现有报告/规划引用及生成的 [CURRENT](../web_gm/development_feedback/CURRENT.md)，无SQLite、运行日志或游戏数据。后续刷新使用新目录，再审阅替换索引；不自动覆盖、push、创建GitHub Issue或触发Codex。

## 准备状态报告

`readiness`读取 [m4_readiness_evidence.json](../config/m4_readiness_evidence.json) 的带日期小型证据清单，并可附加本地Issue #6管理状态；没有库时也能报告，不因此创建数据库。清单是显式维护的GitHub/验收引用，**不会在线探测Web、GitHub、游戏或伪装实时验收**。以后新证据出现时由相应任务更新清单日期/状态/引用；未知条件保持PENDING。

分开列出M0–M3-T正式工程、M4工程及实际合并情况、PR #4真实合并记录、三个Web连接、已脱敏新生产批次及GM消费、真实30队研究、GSW/SAS/OKC无写入演练、Issue #6、BPTI、新采集/校准接口与玩家切换/新档决定。旧M02接口演练不能替代新脱敏批次正式经营演练。即使将来证据齐备，M4仍只输出GM_V4_NOT_ENABLED，切换规则由独立玩家任务完成。

Issue #6只登记已有合成报告的已知风险，未证明所有生产采集必然失败；本轮不修复、不重现或测DEV14。BPTI是正式新档前置，季后赛采集与年度校准是独立后续项目；本M4均不实施。实际30队仍UNASSESSED，V3生效，正式GM V4未启用。
