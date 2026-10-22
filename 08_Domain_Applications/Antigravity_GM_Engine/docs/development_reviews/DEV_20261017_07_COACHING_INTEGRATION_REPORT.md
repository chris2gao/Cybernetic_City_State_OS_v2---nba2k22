# DEV-20261017-07 教练 V2 集成报告

状态：`DEVELOPMENT_IMPLEMENTED_WITH_DECLARED_LIMITATIONS`。开发分支 `codex/coaching-tactics-v1`，交付至现有 PR#1；未部署 main，不自动合并。V2 的 A–E 工程已实现；玩家明确将Tempo的验收改为原生raw读写、界面含义未知。实际生产采集与数据发布仍未触发，工程交付不代表已部署或已发布游戏数据。

初始实施源码提交：`8473d7f9c1687135694443d39ddbd719f8fce2c3`；移除样本限制与Freelance开放见`c8ead5b`。最终原生Tempo及索引以PR#1当前HEAD为准；历史SHA用于定位当时证据，不冒充后续代码版本。

## 当前验收结论

| 模块 | 已完成 | 剩余限制 |
| --- | --- | --- |
| A：19 项默认教练设置 | 19项均支持读取、提案和受控执行。六POE、五数值设置、双体系和命名手册14项有实机写回证据；四Freelance使用34种完整原生枚举、已验证布局和有序codec；Tempo按玩家最新决定开放原生raw并通过针对性离线边界/共享位/恢复检查 | Tempo界面含义未知，不称为已验证的进攻节奏或百分比；同局8位主帅观测40–95供GM参考，不作为白名单。四Freelance未直接查看本局比赛内页面，不冒充UI或持久性测试。BenchDepth由GM按实际阵容选人数，不受9–10样本限制 |
| B：指定对手整体防守 | PHI→IND UI差分、程序同范围操作、用户菜单确认、恢复；18原生字段合法值及8字节掩码，整体组身份保护 | 直接配对的中文为持球压迫AUTO/GAP；其他字段保留原生英文，不猜翻译；不承诺模拟效果 |
| C：1–30队批次 | 整批RO预验、RW前再次预验、外部精确批准、持久preimage/lock、共享块masked写、逆序条件恢复；30队离线与两类对象隔离实机通过 | 软件事务不是物理同时生效；缓存回执不证明当前值，第三方修改转人工审阅 |
| D：正常采集与发布接入 | 原RO采集handle→snapshot-scoped SQLite→源审计→既有导出器33个轻量文件；临时库和导出器守卫测试通过 | 未跑真实全量生产入口或GitHub数据发布，未部署main；不能把本地开发快照补入旧包 |
| E：两份操作手册 | GM手册、执行手册40、32/33/34/36、28、39历史提示、源注册表、SOP和角色索引已同步 | 明确区分工程能力、实机观测、部署与实际数据发布；正式批次仍需玩家批准 |

## 实机证据

- [整体防守证据](DEV_20261017_07_OVERALL_DEFENSE_EVIDENCE.json)：整体页面没有额外All选择。UI把所选字段批量写入该对手14条有效matchup，空槽不写；保留各player/defender ID，不提供逐球员接口。退出UI观察到IsInUse从0到1，不能将0解释为禁用。
- [五数值证据](DEV_20261017_07_SLIDER_EVIDENCE.json)：PHI协防50→51、执行战术70→71、联防1→2、替补使用40→41、板凳深度9→10，用户确认五项一致；事务恢复后30队教练及manager原始块完全一致。板凳深度是轮换人数上限；其余四项倾向0–100、步长1。
- [混合批次证据](DEV_20261017_07_MIXED_BATCH_EVIDENCE.json)：PreferredSystem1→5、ActiveSystem4→3、Playbook0→动态加载的Bucks1在同一4字节块合并写；另一个对象为PHIvsIND持球压迫0→1、14个有效块，共15次写入。用户确认当前体系“主打内线→主打外线”、手册“76人→雄鹿”。PreferredSystem原生枚举/独立位域/回读通过，未单独看到其UI；用户停止同类重复菜单验证。15块按日志条件恢复，所有捕获块一致。交付前代码审查又补齐了显式rollback的逆序，与失败自动恢复保持一致；提交标记恢复顺序由离线测试覆盖，未重复实机测试。

上述仅用于玩家确认的新开终极联盟隔离测试存档，没有正式存档修改、日期推进、比赛模拟、保存/重启复测。此前六POE持久性证据仍按DEV06原报告，不扩张成本次其他字段的落盘证明。

## 实现与来源边界

纯编码位于`coach_codec.py`、`defense_codec.py`、`coaching_overall.py`；GM纯离线合同位于`gm_core/coaching_batch.py`。执行器为`coaching_batch_executor.py`，当前对象解析为`coaching_targets.py`，CLI为`scripts/coaching_batch.py`。原单动作CLI继续兼容默认范围，旧`VS_OPPONENT`预设不执行，新整体作用域是`VS_OPPONENT_DEFENSE`。

`coaching_source.py`冻结采集时profile，旧批次不受较新readiness追认。写入允许范围只限制目标，不能用开发期窄范围过滤真实原生观测或否认原值。五项Sim在GM提案/编码处一律禁用。旧TEAM策略语义/setter保持撤销。

## 验证命令与结果

从开发工作树运行，全部为离线测试或帮助命令，不连接游戏，不发布数据：

```powershell
python -m unittest discover -s tests -p 'test_coaching*.py' -q
python -m unittest discover -s tests -p 'test_gm*.py' -q
python scripts/coaching_snapshot.py --help
python scripts/coaching_validate.py --help
python scripts/coaching_execute.py --help
python scripts/coaching_batch.py --help
```

结果：74项教练测试、40项GM测试通过；4个帮助入口通过。修正了两处旧测试假设：TEAM旧枚举不再允许；当前已发布批次已有赛季统计，不能继续断言所有球队生命周期均不可评估。生命周期实现及正式决策文件没有改动。

## 后续入口

后续工程补充：顺序脚本执行保持不变，两个执行器增加跨state-root的共享进程锁，未完整恢复或最终journal未落盘时保留锁供人工审阅；新增7项离线覆盖。四个已确认百分比字段增加独立观测范围检查，非法101不能发布；BenchDepth的9–10人为白名单已按玩家明确要求撤销，真实11可以观察、GM也可以选择11、12等人数。四Freelance不再因没做重复菜单检查而禁用，其完整原生枚举/布局和有序codec已核对；未追加实机UI声明。新增2项来源与2项批次合同覆盖。当前教练测试85项、GM40项均通过，没有新增实机测试、采集或数据发布。历史8473d7f的实机证据仍按原记录，不将新能力称为当时已实机验证。

玩家最终明确选择开放原生Tempo读写，标注界面含义未确认，不称作已验证的进攻节奏；再以同局其他教练实际值确定实用参考，不为菜单端点增加测试或限值。profile、字段矩阵、源注册表和角色手册均已同步至19项。针对性命令 `python -m unittest discover -s tests -p test_coaching_batch.py -k native_tempo -v` 单项通过，验证0/255原生存储边界、负数/256/bool/小数拒绝、共享位保护、提交与恢复；这些存储端点不是战术建议。此前85项教练及40项GM测试的通过记录保持，未声称本轮重跑整套或新的实机写入。

开发完成后无需为凑齐报告运行玩家未触发的数据任务。main部署、真实正常采集/审计/-Publish结果及Tempo UI/效果映射保留为明确的运行或观察限制；不将其假称已完成。当前交付是具备19项默认字段、整体防守、30队批次、正常来源集成和双手册的工程版本，不自动进入正式GM、采集、发布或游戏写入。
