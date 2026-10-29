# W1 首轮核对：Core Stage01 v0.2 ↔ NBA Stage01 v0.4 · 证据与兼容差异矩阵

**当前状态**：STATIC_SOURCE_REVIEW_DONE / TESTS_NOT_RUN / NO_CORE_CODE_CHANGED。  
**目标**：仅核查经Human在NBA2K22先行确认的阶段01双层建模是否可通用提升；不在本轮施工Core runner。

## 1. 固定来源

| 来源 | 固定版本 | 精确文件 | Git blob |
|---|---|---|---|
| Core master | e075cdf288a765b7bfd2f4891c8f384404da16e1 | 01_os/01_workflow/01_需求建模/方法论_v0.2.md | 4c81218b68da47305d333967400d4e03f74705f1 |
| Core master | 同上 | 01_os/01_workflow/01_需求建模/README.md | d195a630c33bc62ef6f73ed3fe9a47de6b256e07 |
| Core master | 同上 | 01_os/01_workflow/01_需求建模/实现/最小运行schema_v1.yml | 3c8e708f6f49f5541556f60640463392b0337829 |
| Core master | 同上 | 01_os/02_boot/workflow_minimum_operational_loop/启动清单_v1.yml | 57ae9a013c035ed23a2b45ee560a83e50150070e |
| Core master | 同上 | 01_os/05_registry/workflow_minimum_operational_loop_v1.yml | 0a6cc98b55bacbc157c893ee74fc1703a7dab005 |
| NBA规划 | planning/os-prms-a0-confirmed-01b-20261028 | 01_os/01_workflow/01_需求建模/方法论_v0.4.md | 78f6ea4edb00ee21d246ca662ae8ce188b8131d6 |
| NBA规划 | 同上 | 01_os/01_workflow/01_需求建模/README.md | 5533f30018292e1717401368329461da7857ef2b |
| NBA规划 | 同上 | 01_os/01_workflow/01_需求建模/实现/需求结果模型模板_v1.yml | 5ef0a061f5e1c08b47884691003bcdd962f1b733 |
| NBA规划 | 同上 | 01_os/02_boot/workflow_minimum_operational_loop/启动清单_v1.yml | 6ebc7e8a899010b911970b2fab5822f8808f0328 |
| NBA规划 | 同上 | 01_os/05_registry/workflow_minimum_operational_loop_v1.yml | 316d9314d3dc6ea9e8d890068265a6b469677080 |

此表是已读取的固定 Git blob 的静态核对，不表示已运行 Core/NBA runner，也不意味着 NBA 规划分支文件已并入其master。

## 2. 功能差异矩阵（逐项证据与迁移判断）

| ID | 现行Core v0.2 | NBA v0.4 已先行定义 | Core候选处理 | 测试/反例 |
|---|---|---|---|---|
| D01 | 一个Stage01直接生成完整A | Stage01内部01a共识A0→01b完整需求结果A | 语义分层而不新增第8阶段 | 只批准A0时Stage01不可结束 |
| D02 | A为目标/成功/边界等8槽结构 | A0保持共识；完整A列出最终产物结果项和完整性 | 8槽保留，新增result_items作为明确扩展 | 只有8槽但未具备结果清单不能宣称完成01b |
| D03 | Human同义确认A版本 | A0和完整A分别独立Human版本确认 | A0确认≠A确认；必须对版本绑定做兼容设计 | 错把A0确认当最终A阻断 |
| D04 | 02收集A的领域与可行性依据 | 02从各结果项的确切未知和来源缺口收集 | 增加EVQ/RES/SC链接而不改变02功能归属 | 不能用泛泛文献代替RES逐项证据 |
| D05 | 03从证据得结果方案B，禁止01固定技术路线 | 01b先描述目标成品A，03才确定实现选型B | 精确规定A目标规格 vs B物理设计界限 | 未证实SQL表数不得从候选升级为事实 |
| D06 | Core v1 Stage01机器payload要求requirement_id/objective/success_criteria/constraints/Human_confirmation | NBA新增模板含stage01.consensus_A0 / requirement_result_A.result_items / coverage/unknowns | 对旧v1进行向后兼容扩展或新profile，禁止简单改旧schema令历史Run失败 | 替换旧单层语义后，新任务须使用双层A0/A；无需提供旧模式兼容入口 |
| D07 | Core Boot没有stage01_active_semantic_spec | NBA Boot有此路径和stage01_result_model_template | 在Core规范有结论后给Boot增加稳定发现入口和校验 | 断裂的规范/模板引用必须报告 |
| D08 | Core Registry未登记v0.4/模板 | NBA Registry多两条入口 | 同一Core升级PR同步Registry和Boot | 忘记登记新规范→索引一致性失败 |
| D09 | 原Core v0.2默认2–4问/轮、同层低依赖、Human确认 | NBA v0.4继承相同问答纪律 | 原机制保留，不重复发明提问算法 | 不把01a/01b强制变成“每轮一问” |
| D10 | Core测试/runner仍验证七阶段最小结构及原确认关系 | NBA明确v0.4尚未使v1 runner具备“语义充分性”自动检查 | 先定义可执行负例和最小结构门，再考虑模型对内容充分性的审查边界 | 只看到v0.4文件存在不能报机器已验收 |
| D11 | 需求Schema按跨领域统一八槽 | NBA举了数据库对象、字段、DDL/来源映射等深入示例 | 通用result_item模型可迁移；篮球/SQL专有字段按任务类型profile选择 | 非数据库项目不得被强制填写SQL表/字段 |
| D12 | 当前Core workflow、stage_collaborative_deliberation、PRMS各有owner | NBA先行的核心文件带领域Human特批 | 回主Core独立变更，避免领域继续维护并列权威；新角色加载通过PRMS目录/Boot | 不能以旧领域版替代新Core真实SHA；不升级任何其他领域 |

## 3. 第一轮核心判断

1. **真正产品级差异**是阶段01由一个笼统A变成A0共识+最终成果A；保留七阶段ID和02/03职责，避免01b与03混同。
2. **当前可实证的机器缺口**是现行Runner仅检查旧v1 payload/版本链，NBA模板也明确template_only。仅修改README/Boot并不能证明结果项完整，不能直接发布“自动保障了A的完整性”。
3. **Human后续裁决：迁移形式改为直接替换单层需求建模语义**；无旧v1兼容层或双轨profile。采用A0/A独立确认 + RES/EVQ/SC完整性映射 + 定向负例。Core的现行 PRMS、任务编排和阶段协同机制继续作为权威。
4. **Human已确认替换方向**：从此次Core更新起，Stage01统一使用A0→A双层建模，旧任务不额外兼容；旧历史文件在Git中保留，不为它们建立继续执行的旧语义入口。
5. **仍待技术实证**：Core stage01 runner/stage publication gate 的每个数据入口、新规范负例的真实运行、详细差异文件树和依赖闭包。没有在本轮调用动态测试。

## 4. 后续W1设计/工程包完成定义

- GPT：收口A0/A正式规范、旧语义直接替换策略、每个结果项/证据链接、B与02边界；产出Human可审阅的设计B和负例合同。
- Codex：在合法Core工程分支实现不破坏七阶段的schema/validator、Boot/Registry、新规范测试，更新相关索引与回执；不能把方法论文档更新冒充自动运行成功。
- 独立审核：固定代码SHA，检查有意破坏的A0/A绑定与历史Run例子，并核实新结构和结果项；最终Human决定Core受保护合并。
- REA工具开发继续排在本任务后续独立包，不在W1实现时自动并行启动。


## Human 后续方向确认 · 2026-10-29

**以本节为准覆盖文件中仍然存在的“兼容”“旧任务迁移门”等早期工程建议。** Human 明确指示：“不需要兼容旧任务，不要过度设计，这就是为什么要更新和完善新的工作机制。我们需要的就是替换掉旧的对应语义内容，完成迁移即可。” 因此 W1 的最终产品目标是**单一新的阶段01语义**；旧v0.2记录仅留历史，不保留旧模式执行支持；不新增双版本路由、旧Run追溯重验、兼容映射器或迁移开关。七阶段顺序与现有通用机制保持，更新必要源文件、入口和最小校验。此裁决优先于本Run早期候选文字。
