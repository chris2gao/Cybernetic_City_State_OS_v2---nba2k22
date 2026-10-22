# ChatGPT 网页版专用：三类基线入口

> [**所有网页版基线共同宗旨**](../../docs/PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)：研究/开发目标是完整游戏原料和可靠工具，不是在R系列或DEV28中制造固定行为程序充当人格；六阶段独立模型与真实玩家审批边界以项目级文档为准。

> **只适用于 Web GPT（ChatGPT 网页/连接 GitHub 的聊天）。** 请勿与 Codex 的 `docs/32_DATA_CAPTURE_BASELINE_PROMPT.md` / `docs/33_DEVELOPMENT_BASELINE_PROMPT.md` 混用。角色与持久记忆协议：`docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md`。

## 选择基线

三个角色的本地SQLite按需访问共用 [GM_SQLITE_QUERY_ACCESS.md](../../docs/GM_SQLITE_QUERY_ACCESS.md) 和 [消费者能力V2](../data_contracts/CONSUMER_DATA_CAPABILITIES_V2.md)。玩家已决定完成M0实现后再建立各Web终端连接；本地PowerShell验证不冒称Web连接验收，连接未建立时保持明确阻断。查询静态同批双库，不默认读取整份员工/模型池JSON，不修改游戏事实；各角色业务与当前GM规则不因M0自动改变。

| 网页 GPT 窗口 | 基线文件 | 角色 | 任务产物 |
| --- | --- | --- | --- |
| **GM** | [GM_BASELINE.md](GM_BASELINE.md) | 30 队独立建队、运营、交易、历史线取舍 | 待批准 GM 方案、经营总结与记忆 |
| **开发规划** | [DEVELOPMENT_BASELINE.md](DEVELOPMENT_BASELINE.md) | 架构、规格、Codex 开发任务书与审查 | 开发任务/验收报告与记忆 |
| **数据整理分析** | [ANALYTICS_BASELINE.md](ANALYTICS_BASELINE.md) | GitHub 已发布数据 → Python/SQL → 分析结果回写 GitHub | `docs/gm_analysis/` Markdown/JSON 与记忆 |

## 数据分析 V2：以 GM 决策准备替代排行榜

`WEB_GPT_ANALYTICS_V2` 已将《[ANALYTICS_DECISION_READY_V2_METHOD.md](../../docs/gm_analysis/ANALYTICS_DECISION_READY_V2_METHOD.md)》作为正式方法规范。分析任务默认产出：**简明报告、30队逐队决策准备表、跨批变化表、计算方法及来源文件、主分析JSON**，每份锁定 career/batch/时间/代码版本。默认不重复长篇球队排行榜、全部55项原始属性清单或870组防守配置原文。具体判断仍属于GM，分析端不给交易执行授权。

M02开始有同批教练19项与针对对手OVERALL18项来源；M01不含教练，不回填。分析必须核验跨批身份再认定球员自然成长，未明确认证`poss`的原生定义时不能称计算值为标准百回合攻防效率；`is_in_use_raw=0`不是防守不存在。更新仍由玩家触发，基线初始化只加载方法不计算/发布；详细规则和例外以最新方法规范为准。

## 三份可复制的初始化指令

### GM 基线

```text
请使用 GitHub 连接读取 chris2gao/nba2k22-gm-engine 仓库的 web_gm/baselines/GM_BASELINE.md，按其中的最小读取顺序初始化「Web GPT GM 基线」。只读取并报告当前基线版本与待办状态，不启动 GM 回合、不生成交易、不改游戏和仓库。等待我从本基线新开任务窗口给出指令。
```

### 开发规划基线

```text
请使用 GitHub 连接读取 chris2gao/nba2k22-gm-engine 仓库的 web_gm/baselines/DEVELOPMENT_BASELINE.md，初始化「Web GPT 开发规划基线」。只建立工程与职责上下文，不向 Codex 下发任务、不改代码、不触发采集/测试/发布/GM 或游戏执行。等待我的具体开发需求。
```

### 数据整理分析基线

```text
请使用 GitHub 连接读取 chris2gao/nba2k22-gm-engine 仓库的 web_gm/baselines/ANALYTICS_BASELINE.md，初始化「Web GPT 数据整理分析基线」。只读取规则、入口与最近分析记忆并报告就绪；不开始新的分析、不发布、不运行游戏、不触发 GM。等待我从本基线另开分析任务窗口。
```

## 从基线新开工作窗口：GM 按赛季，分析/开发按任务

**GM：一个游戏赛季对应一个派生决策聊天。** 玩家每赛季手动从 GM 基线新开一次，指定当前存档、赛季和首个节点；同赛季各月度、交易截止日、季后赛轮次、休赛期或突发经营需求，**继续在该赛季聊天**，由玩家逐次触发。单次节点（通常一轮、最多三轮 GM 审议）交付后，写节点成果 → 更新 `web_gm/seasons/<season_id>/INDEX.md` 与 `GM_CURRENT.md` → 报告提交 SHA → **在同一聊天待命，不结束赛季聊天**。仅玩家确认赛季结束并完成赛季总结后，新赛季才新开聊天；因上下文不足换聊天时沿用同赛季身份及 GitHub 记忆续接。既存 `W01/W02` 是节点归档号而非不同聊天的强制要求。

**开发规划与数据分析**仍按独立任务窗口运行；任务完成后写会话记录、更新自己的 `*_CURRENT.md` 并结束该任务窗口。

新开任何聊天时，若没有继承文字上下文，发送对应基线初始化/任务指令；**即使复制了聊天历史，仍必须核对 GitHub 文件最新版**。不能假设自动收到其他聊天的结论。未成功上传不能声称已有持久记忆。

这三个基线**不能自动互相唤起**；窗口之间通过仓库文件交接。只需要按需读取本岗位文件，不要一次性加载三个基线和全部 30 队完整 JSON。
