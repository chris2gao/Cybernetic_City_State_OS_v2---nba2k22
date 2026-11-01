# VAE Sweep 1 → 后续 Gemini REA 只读验证问题清单

此文件只组织**可证伪问题**，不启动 Gemini、游戏、MC 或自动化任务。全部 204 条具体问题分别存放 `06_执行/field_records/<field_id>.json`，固定队列和索引以审计回执为准。

## 高优先级（受原任务 Human 调度约束）

| 对象 | 背景缺口 | 建议只读观察 |
|---|---|---|
| `WORLD_REG_057–058` | 最近交易限制、交易难度与 `settings.*` 候选偏移重合 | 双次 PC22 MyLEAGUE UI/raw 读取，单独确认 SLOT_TRADE+0x158/+0x174，不能发起交易 |
| `WORLD_REG_059–066` | CPU 续约、合同难度、潜力/耐久/名气在工资预期中的角色 | 各字段分开取证，记录生涯阶段与薪资规则，无报价或续约 |
| `WORLD_REG_067–069` | 自然成长、回归、训练效果 | 分辨训练效果和赛季发展，仅做当下静态读回 |
| `WORLD_REG_070–081` | 伤病频率、效果、严重度、持续时间、开关、Morale/Chemistry | 确认游戏模式/UI字段身份及不同 setting slot，不推进日期或制造伤病 |
| `WORLD_REG_082–084` | 3D Quarter、Calendar Sim Quarter、Normalize Stats | 分离 played 与 sim 状态、Minutes 与 Stats 两个 normalize 项，记录原生 slot |
| `WORLD_REG_085–086` | Game Difficulty/Speed 都是 `0x00` 但分别为 SLOT_SLIDERS 与 SLOT_SETTINGS | 只读验证 slot 身份，**禁止**只凭 offset 判断重复 |
| `COACH_DEFAULT_001–006` | 六个 POE 编码与赛前/ACE 临场覆盖的关系 | 对同 Coach 读原生设置和 UI 列举；不推断比赛收益 |
| `COACH_DEFAULT_007–010` | Preferred vs Active System、Playbook ID 与 BenchDepth | 读系统值、书 CRC 与阵容轮换，标识原生与项目私有层 |
| `COACH_DEFAULT_011–015` | RunPlay/Zone/BenchUtilization/Tempo/HelpDefense | 先验证字段-UI身份，绝不由 Coach Tempo 名字断言 SimPace |
| `COACH_DEFAULT_016–019` | 四 Freelance 选项与实际上场生效/ACE | 保留 slot 顺序，查“设置”与“激活”是否不同对象 |
| `TENDENCY_NATIVE_001–099` | 倾向单字段候选身份、同版玩家修改与真正 Native 消费者 | 分字段双读回 Player UID+原始值；严格分离 Attribute/Tendency/Badge/Coach/PlayType |

## 验证模板

- 对象：`field_id` + 固定字段队列 blob `af5567e14e03cd9f7761e396a978311e347d7c17` + 当前世界线/存档/PC22 build。
- 输入：只读原生候选与同一时间源 UI；不得擅自写内存、提交交易、模拟日历或切换保存。
- 输出：原始 raw 值、对象 UID、UI label/value、slot/module base、两次读回时间、`MATCH / MISMATCH / BLOCKED / UNKNOWN`，记录异常和混杂因子。
- 严格区分 `PC22_NATIVE_PROVEN`（后续真正有证据）和 `EXTERNAL_SOURCE_HYPOTHESIS`（本 Sweep 的原有状态）。
- Human 明确转交之后才由独立 Gemini REA 或审查窗口消费；本 GPT 没有执行跨模型调用。
