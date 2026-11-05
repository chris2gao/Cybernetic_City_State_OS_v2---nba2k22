# DEV-02 · 徽章与球员能力基准 / Badge Intelligence

**任务 ID**：`NBA2K22-BIC-B1-DEV02-BADGE-INTELLIGENCE-20261104`  
**领域**：NBA2K22 · Basketball Intelligence Core (BIC)  
**岗位/模型**：`research` 建议 Gemini 负责原生机制只读核验；后续 `execution` 建议 Codex 开发基准判读增量；GPT-6 规划和系列审核。  
**状态**：`PUBLISHED_CONDITIONAL_NOT_IMPLEMENTATION_AUTHORIZED`。先阅读同 Run 的 `task_packet.json` 和 DEV-01 事实接口。任务发布不授权逆向写入、游戏进程连接、训练操作或工程执行；此类工作须另走 OS/Human 门。

## 1. 业务目标

构建可以**可靠理解并利用徽章**的篮球能力基准：用原生球员真实能力值、身高/位置等身体条件、现有徽章与等级、已验证的资格限制、经验/升级条件和实际比赛效应，描述当前球技及可发展方向。

Human Q8/Q9 明确**提高徽章权重**，但并不表示徽章是唯一真值。必须把四类情况分清：已有徽章；已达到原生资格但尚未获得；当前未达资格但有证据支持未来可能达到；资格/规则无法验证（UNKNOWN）。不能由“满足必要条件”推导“徽章一定获得”，也不能凭一次投失直接归咎于徽章。

映射：`RES-01B-BADGE-CAPABILITY-AND-GROWTH-BASELINE`、`RES-01B-BADGE-ELIGIBLE-PLAYER-CULTIVATION-CANDIDATE`、`RES-01B-EVIDENCE-QUALIFICATION`、`RES-01B-BASELINE-FOUNDATION`；A0 `SC-01/02/03/07/08`。

## 2. 现有素材与明确限制

- `08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/catalogs/PLAYER_BADGES_R04_A_REFERENCE.json`：标明 `RESEARCH_REFERENCE_NOT_NATIVE_BADGE_DICTIONARY`、`BADGE_LIST_MAY_INCLUDE_MYPLAYER_REQUIREMENTS`；其中游戏攻略与 MyPLAYER 门槛**不得自动推广到 PC22 离线 MyLEAGUE**。
- `08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json`：研究、UI、Native 结构、真实读回、执行授权是独立证据轴；40 组/694 研究项不等于已认证字段或 API。
- `08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/guides/K06_TRAINING_HEALTH_GROWTH.md`：原生训练目录和 11 项已登记设置；训练类型 `player_type` 与比赛 PlayTypes 不同；训练不等于直接徽章/能力加点。
- 已有徽章成长条件逆向、VAE、REA 和当前 WorldData 需在 P0 对照；资料不在本分支或仅本地存在时登记“待取得精确 SHA/路径”，不能宣称已合并或实测。
- `NBA2K22.exe` 原生版本、游戏模式、球员身份与存档世代必须匹配；不以 NBA2K23、次世代 MyNBA 或 NBA2K22 MyPLAYER 的门槛代替本版事实。

## 3. 研究与工程交付

**P0 · 只读证据对账（可先行）**  
逐徽章建立证据行：`badge_id/label/level`、可得球员真实持有状态、适用 PC22 版本与 MyLEAGUE 模式、资格先决条件（属性/身高等）、XP/成长/升级、比赛触发/动画/成功率效果、来源精确版本和证据状态。逐项分类 `NATIVE_VERIFIED | RESEARCH_REFERENCE | HYPOTHESIS | CONTRADICTED | UNKNOWN | NOT_APPLICABLE`；研究标记和执行认证分别记录。不要假设所有徽章机制相同，也不要要求无证据填写精确阈值。

**P1 · 资格与技术能力判读（只在工程启动门后）**  
复用 DEV-01 的真实 `player_baseline`，形成单个球员的徽章能力报告：
- 当前徽章事实、技能与能力值的交叉解释，指出潜在冲突和适用条件。
- **已证资格**与**预测可能满足资格**严格分开；同一徽章不同等级独立判读，不混淆经验与资格。
- 若徽章数据未采集、资格只来自攻略或当前版本不匹配，必须 `UNKNOWN`，不能推断“可获得”。
- 提供高权重徽章线索，但遇到直接能力值、倾向、3D 行为相矛盾时输出争议与下一项检验，不硬编码“有徽章绝对优先”。
- 输出培养建议仅依原生自然成长和已验证训练机制；任何训练实际执行在本任务范围外。

**P2 · 真实示例与反例**  
优先以真实可追溯球员数据解释：西亚卡姆的中距离单打、约基奇篮下/策应；对“当期徽章是否解释成功率差异”只给可证事实、可能机制及缺失证据，不编造徽章状态或断言其因果。再增加一例“当前无徽章但经核验有资格”与一例“仅有 MyPLAYER 研究资料、PC22 MyLEAGUE 不可证明”的负例。如现有快照无法找到所需真实样本，明确缺失并用有来源的替代样本，禁止伪造数据。

## 4. 验收门与可证输出

1. **证据源正确**：Native 证据、研究资料、Human 游戏观察和模型推断分别记录；无“80 徽章说明 = 80 个 PC22 原生认证”的误用。
2. **逐徽章可解释**：对于选定可证徽章，能显示球员数据→资格条件→是否持有/等级→可能的技术特征、限制和 `UNKNOWN`；每条结论可追溯到精确来源。
3. **模型反例**：资格不满足、资格已满足但未拥有、版本不匹配、缺失 XP、徽章与直接能力冲突等不被错误升级为已拥有或已验证效果。
4. **边界**：零游戏写入、零直接修改徽章/能力/潜力、零未经授权训练；Badge XP、动画和成功率没有实证时不能作百分比承诺。
5. **可复用**：徽章能力输出复用 DEV-01 身份/来源/时间契约，并可供 DEV-03 的单因素/交互研究调用。

交付：徽章证据与缺口矩阵、只读判读实现（仅在授权后）、可复核球员示例与负例、原生资格与作用研究任务候选、自动化离线测试及结果、PRMS 检查点。禁止为了“看似全面”而把全徽章统一赋予未经实证的门槛。

## 5. 停止与回流

若 PC22 MyLEAGUE 原生资格阈值、徽章 XP 或游戏效果尚不可核实，输出 `UNKNOWN + source_gap + next_research_question`，不强行编造。重大来源矛盾立即停止相关结论升级，交 GPT-6 规划/ Human 裁决；普通细节采用内部 Loop 研究—测试—修正，在系列完成后统一审核。
