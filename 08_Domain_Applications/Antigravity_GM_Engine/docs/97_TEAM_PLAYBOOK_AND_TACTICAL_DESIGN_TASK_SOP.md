# NBA 2K22 年度球队战术体系与手册设计标准化任务 (SOP)

> **文档标识 (Document ID)**: `SOP-ANNUAL-TEAM-TACTICAL-DESIGN-V1`  
> **上游知识底座**: [96_NBA2K22_PLAYBOOK_COMPLETE_UNDERSTANDING_AND_DESIGN_GUIDE.md](96_NBA2K22_PLAYBOOK_COMPLETE_UNDERSTANDING_AND_DESIGN_GUIDE.md) | [native_plays_complete_catalog_v1.json](../web_gm/knowledge/plays/native_plays_complete_catalog_v1.json)  
> **下游联动与权威地位**: **全联盟新赛季第一权威原始信息源（Upstream Source of Truth）**。本任务产出的 30 队战术设计报告直接作为后续所有球队研究任务（模拟侧重、全局设置、球员训练模板、99项倾向与战术重力、轮换无形资产微调）的唯一输入基准；后续任务免除重复从零分析。  
> **适用时机**: 每年新赛季阵容确定后（揭幕日 Day 1 优先触发执行），常规执行一次；或某支球队发生核心阵容大变动时单独触发。

---

## 零、任务前置条件（Preflight — 每次任务开始前必须首先执行）

1. **全联盟主教练专属战术手册独占校验与修正**：
   - 在启动任何球队战术设计或内存写入之前，**必须首先运行** [preflight_enforce_exclusive_playbooks.py](../src/preflight_enforce_exclusive_playbooks.py) 检查全部 30 支 NBA 球队主教练的 `PlaybookID`：
     ```powershell
     python 08_Domain_Applications/Antigravity_GM_Engine/src/preflight_enforce_exclusive_playbooks.py
     ```
   - **原因**：原版名单中部分球队主教练（如 `CHA`、`MEM`、`ORL`、`WAS`）默认指向共用的 `Standard Playbook (enum_id=30)`，或错指他队手册（如 `MIN` 错指 `Grizzlies Playbook (6)`）。若不先行绑定本队专属手册（`0–29` 严格 1 对 1 独占），后续写入会互相覆盖。
   - 确认 30/30 球队均绑定本队专属 `PlaybookID` 且 CAS 回读通过后，再进入 Phase 1 与 Phase 2。

---

## 一、核心设计哲学与两阶段分离架构

### 1.1 为什么必须“思考决策”与“格式编译”两阶段分离？
为保证大模型将 **100% 的推理算力投入到篮球战术博弈与阵容优势面发掘**，本任务严格分为两个独立阶段，绝不在一次思考中混杂海量十六进制 CRC 拼接：

* **Phase 1（深度战术决策阶段 — 模型主战场）**：
  - **输入**：球队真实 10 人左右轮换数据（能力、徽章、热区、身高、现有倾向、AI 分配的出场时间段）+ 战术字典索引。
  - **输出**：一份深度、逻辑严密、可直接供人类审阅拍板的 **《[TEAM] 年度攻防战术体系设计报告（Markdown）》**。报告中只写**精确的战术英文原名**，不手写 CRC。
* **Phase 2（确定性编译与写入阶段 — 人类批准后由脚本 0 幻觉执行）**：
  - **触发**：人类审阅并批准 Phase 1 报告后，由本地确定性脚本解析报告中的战术名称表，自动对齐 `native_plays_complete_catalog_v1.json` 查出 `native_crc`、校验 `allowed_positions` 位置掩码与 68 槽容量，生成可执行 JSON 并写入游戏内存。

---

## 二、Phase 1 标准化五步决策流水线

执行模型接到“为 `<TEAM>` 执行年度战术设计任务”时，必须严格按以下 5 步完成思考与报告撰写：

### Step 1：阵容诊断与建队思路定调（Roster-First）
1. 盘点全队核心轮换（首发 5 人 + 关键替补 3–5 人）的能力结构、射程分布（三分 ≥ 78 的人数）、持球发起点、内线类型（吃饼 / 外弹三分 / 高位轴心 / 真低位）及年龄结构。
2. 明确本队唯一的**主建队路线**（可辅以次级标签）：
   - **体系/团队流**（传切、手递手、高位分享球，如勇士/掘金/热火/国王）
   - **超级持球大核流**（五外/四外一内挡拆驱动，如独行侠/灰熊/老鹰）
   - **双核/多核错位联动流**（多持球锋卫交替点名与连环掩护，如凯尔特人/太阳/快船）
   - **内线低位统治流**（低位吸夹击辐射外围，如 76 人）
   - **防守反击/平民拼抢流**（青年军/无超巨阵容，主打转换、空接与简洁挡拆）
3. 给出匹配的 **教练首选进攻体系 (`PreferredSystem`)** 与 **`Freelance 1–4` 优先级**。

### Step 2：第一批战术筛选 —— 核心球员个人战术池（Player-Level Pool）
1. **选人**：从轮换中挑出真正需要专门设计战术的进攻点（通常 **3–6 人**，纯蓝领 3D/护筐中锋不单独占名额，只作为空间/掩护/空接配合点）。
2. **配额与筛选**：为每位入选球员从 [native_plays_complete_catalog_v1.json](../web_gm/knowledge/plays/native_plays_complete_catalog_v1.json) 中筛选 **1 至 5 个**最能释放其个人天赋的战术，且必须同时满足三条硬性防坑铁律：
   - **`in_ui_playbook_pool == true`（UI 可见池铁律）**：只能从 84 队实机可装配战术池中选取，严禁选入 `5OUT BIG TOP`、`FLOPPYS TOP` 等 Freelance 内部隐藏动作（塞入手册会被 UI 直接隐藏）；
   - **`usable_by_era_policy == true`（>=1980 年代空间铁律）**：80 年代以前全部排除，90/00 年代慎选；
   - **`allowed_positions` 位置掩码覆盖**：必须覆盖该球员的场上轮换位置。
3. **写明理由**：每条个人战术必须说明**为什么适合该球员的徽章/热区/打法**。

### Step 3：第二批战术筛选 —— 轮换时段阵容搭配与攻防优势面（Lineup-Synergy Pool）
1. **拆解出场时间段**：依据原版 AI 或拟定的轮换时间表，归纳出球队每场真实出现的 **3–4 套核心 5 人阵容**：
   - **阵容 A（首发主力阵）**
   - **阵容 B（衔阶段：核心之一带替补）**
   - **阵容 C（纯替补轮换阵）**
   - **阵容 D（决胜关键时刻 Closing Lineup）**
2. **进攻优势面与联动战术筛选**：
   - 分析每套 5 人阵容的最大协同优势面（例如：凯尔特人双探花同场突出 `STS`/`HAMMER` 多点三分 + `PUNCH ZIP` 错位背身；A 核+空间 5 号位突出 `5OUT` + `POP CNR`），从战术库中筛选出**第二批阵容联动战术**。
3. **防守体系设计（按阵容时段建模，不做 30×30 对位）**：
   - 针对上述 3–4 套 5 人阵容各自的防挡拆能力、外线挤过/换防弹性、内线护筐与篮板短板，设计本队的**持久化防守体系**：
     - 教练宏观 **防守 POE 1–3**
     - **联防使用率 (`ZoneUsage`)** 与 **协防强度 (`HelpDefense`)**
     - 核心轮换球员的 **个人防守定位与防守倾向调整方向**（谁领防、谁扫荡、谁沉退护筐）。

### Step 4：终极决策 —— 战术手册装填（Capacity Decision）
将【第一批个人战术池】与【第二批阵容联动池】合并去重，按以下实机验证容量规则裁剪填入（**所有战术名必须 100% 精确匹配 `native_plays_complete_catalog_v1.json` 且 `in_ui_playbook_pool == true`**）：
* **UI 可见主列表（`Regular 0–29` + `Bench 30–49`，建议总计 `36–42` 条，不超过 42 条可见上限）**：
  - **Regular 常规槽（`0–29`）**：放首发主力与双核联动的核心高胜率战术（如 26–30 条）。
  - **Bench 替补槽（`30–49`）**：专门放**第六人/替补得分手的 1–5 个专属战术** + **衔阶段与纯替补的高容错简洁战术**（如 8–12 条，未使用的空槽保持 `0`）。
* **Endgame 末段槽（`50–59`，6–8 槽）**：专门放带 `END` 后缀的末段关键球/绝杀战术（如 `ISO 1 FIST END`、`FIST 5 END`、`PUNCH 32 FIST END`）。注意：**`END` 末段战术在常规手册 UI 列表中默认隐藏不显示，由系统在最后时刻自动调用，不占主列表名额**。
* **Favorite 收藏槽（`60–67`，8 槽）**：写入本队最高频的 8 条核心快捷战术。

### Step 5：参数联动收尾（`PlayType` & 倾向建议）
1. 为全队核心轮换球员给出精确的 **`PlayType 1–4`** 配置方案（1/2 槽主用）。**重要实机校准：在 NBA 2K22 中，`14` 才是真正的“三分/外线投篮 (3 PT)”，切勿误填 `15`（`15` 在游戏 UI 中显示为空/无效）！**
2. 给出教练 `RunPlayTendency`（执行战术频率）与核心球员 `Play Discipline`（战术纪律）建议，以及后续对轮换出场时间/无形资产的微调指引。

---

## 三、Phase 1 标准交付报告模板

每次单队任务的输出报告必须严格包含以下 6 个标准章节，其中第 4、5 节使用标准 Markdown 表格，以便 Phase 2 编译脚本直接解析：

1. `## 1. 球队风格诊断与建队思路`（含主建队路线、进攻体系、Freelance 1–4、整体进攻 POE 1–3）
2. `## 2. 第一批筛选：核心球员个人战术池`（每人 1–5 个战术 + 选中理由）
3. `## 3. 第二批筛选：轮换阵容时段与攻防优势面`（3–4 套 5 人阵容的进攻联动战术 + 阵容级防守体系 & 教练防守 POE 1–3 / Zone / HelpDef）
4. `## 4. 68 槽战术手册终极装填清单`（分 Regular 0–29、Bench 30–49、Endgame 50–59、Favorite 60–67 四张表，列明：`槽位 | 战术精确英文名 | 所属12大类 | 主要触发球员/目的`）
5. `## 5. 球员 PlayType 1–4 与纪律性联动配置表`（列明：`球员 | 位置 | PlayType 1 | PlayType 2 | PlayType 3 | PlayType 4 | Initiator | 战术纪律建议`）
6. `## 6. 下游轮换/无形资产联动微调建议`（可选：指出哪些配合效果极佳的双人/三人组值得在轮换时间上绑定）

---

## 四、Phase 2 标准化编译与顺序 REA Native 注入规范

1. **全联盟确定性编译**：
   运行 [compile_all_30_tactics_phase2.py](../src/compile_all_30_tactics_phase2.py)，校验 30 队报告无重名、无非法战术、无 `PlayType 15` 脏数据，并生成 `manifest.json` 与 30 份 `<TEAM>_spec.json`。
2. **单队顺序注入与 CAS 校验**：
   严格按球队顺序逐一执行（先完成前一步 Preflight）：
   - 运行 `python 08_Domain_Applications/Antigravity_GM_Engine/src/execute_team_phase2_non_frida.py --team <TEAM>`（完成 68 槽 Playbook CRC、教练设置/POE/独占 `PlaybookID`、球员 `Initiator` 写入与 CAS 回读，并生成 `<TEAM>_frida_payload.json`）；
   - 调用 REA MCP `rea:instrument_with_frida` 对 `<TEAM>_frida_payload.json` 内全部球员执行游戏原生 `PLAYER_SET_PLAY_TYPES_1_TO_4`（RVA `0xf1e370` / `0xf1e390` / `0xf1e3b0` / `0xf1e3d0`）注入并完成 `PLAYER+0x168` CAS 回读校验。
3. **蜂群批处理建议**：
   Phase 1 可使用 Swarm（每批 5 队、冷启动读取 `scratch/swarm_inputs/<TEAM>_m02_dec.json` 与 `ui_usable_plays_by_cat.json`）；Phase 2 统一由单个具备写/MCP 权限的 Subagent 按顺序逐队执行。
