# 批准交易执行器与 W02 故障修复

2026-10-17，当前版本 `ownership_transfer_v2`。玩家在人数修复后已明确确认“公牛和活塞的交易成功”，并要求将交易规范成填写球员信息即可调用的脚本。当前有限范围写入入口已启用，保留完整身份/人数核验和防重放，不需要手填地址或名单引用映射。DAL/HOU本次已有内存/重启后目标归属证据，尚未收到玩家对应的界面验收；存盘状态仍单列。以下保留首次故障及修复经过，不能删除失败证据或把旧字节回读当作当时的完整成功。

## 当前标准用法

模板为 `examples/approved_trade_request.json`。填写 `request_id`、`save_id`、当前 `season`、批准依据和交易清单；球员通常只需 `name/from_team/to_team`，球队可用缩写或当前ID。`face_id/birth_date` 是可选消歧字段；脚本遇到同名克隆不自行选择。选秀权填 `year/round/original_team/from_team/to_team`。模板自带 `example_only=true`，未填写前不能运行。

1. `python scripts/execute_approved_trades.py --request <local.json> --phase plan`：只读校准和整批核对，将实际face、生日、合同原值固定到本地 `resolved_request.json`，并生成计划。
2. 本聊天玩家已批准该具体方案后，使用 `--phase execute --approve-game-writes`。输入变化必须重新生成计划；执行重新校准和读原值，不沿用旧地址。模型/JSON的approved字段不能批准。
3. `--phase verify`：另开只读连接复核。窗口/进程变化时重建实时身份，拒绝复用旧指针。已有 `WRITE_ATTEMPTED` 时不重放交易；已全部达到目标返回 `NO_WRITE_NEEDED`，不冒认历史变更由本次完成。

Windows包装 `scripts/run_approved_trades.ps1 -Request <path> -Phase plan|execute|verify`，execute须显式 `-ApproveGameWrites`；只按需提升权限，不调用数据更新。玩家仍可直接用普通中文给Codex批准方案，由Codex整理模板并调用，必要时只询问缺失身份。

支持当前NBA2K22签名/已核对布局中的普通名单转队、简单选秀权、以及球队互不重叠的批次。常规容量15；双向转移、释放/签约、同队连续多笔依赖批次、无法保持五人引用组的复杂转队明确拒绝，不默默改其他球员/角色。原有五人引用优先与批准接收球员对应；不会为完成交易挑选无关替代人。日期由玩家提供，可UNKNOWN；存档ID不能自动从内存唯一证明。现有赛季头解码只接受2000–2027范围，实际任务必须与实时头部匹配，新赛季不沿用旧证据。

## 已确认遗漏与修复

首次代码只维护名单/球员引用和归属，漏掉两个独立的人数字段。重启后只读校准当前进程，五名球员和三枚选秀权已经保持目标归属，故不重放交易。

| 字段 | 精确语义与证据 | 本次修复 |
| --- | --- | --- |
| 球队 `+0xCB1`，uint8 | 常规合同名单人数；本机 NBA2K22 Tools 在加入/移除球员时增减；NBA2K22 本体存在直接读取；全联盟其余球队数值与常规指针数量一致 | CHI 15→14；DET 14→15 |
| 球队 `+0x1047`，高4位 | 活动名单人数；本体读取 `uint32(+0x1044) >> 28` 并索引 `team + 0xC8 + count*8`，对应 `+0xD0` 的活动名单。Tools 移除时清零这4位和活动名单引用 | CHI 13→12；整字节 `D1→C1`，保留低4位 |
| 球队 `+0x1047`，低2位 | 双向名单人数；Tools 按2位字段维护，与 `+0xA8/+0xB0` 两槽对应 | 不改 |

DET 的 White 在新增第15个常规槽位，但旧人数仍14，会被人数界限排除；CHI 常规名单14人但旧计数15，活动名单12个非空指针但旧计数13，留下按计数访问空槽的条件。这些是已确认的一致性缺陷；没有取得崩溃调用栈，不能将全部崩溃原因断言为已完全证明或已消除。

受控修复仅写上述三个字节，没有重做球员或选秀权转移。执行后和另开只读连接复核均通过：30队常规/活动/双向人数与引用一致；五名球员和三枚签仍在目标球队。原回执状态 `REPAIR_MEMORY_VERIFIED_UI_PENDING` 保留；之后玩家明确接受CHI/DET游戏界面结果。修复后的保存/重载仍未验收。

## 来源研究

- [DB2K Editor 的 PlayerMovement 原始源码](https://github.com/discobisco/2k26-Editor/blob/08cb0098b606499b1f0ed87c5a2ef49a7f2d5b61/2keditor/models/player_movement.py)：加入/移除同时处理 CURRENTTEAM、CONTRACTTEAM 和球队球员槽位；提供结构方法参考。其 [README](https://github.com/discobisco/2k26-Editor/blob/08cb0098b606499b1f0ed87c5a2ef49a7f2d5b61/README.md) 明确 2K22–24 元数据不完整，不能移植其新版偏移到本局。
- 本机 NBA2K22 Tools 的只读反汇编：RVA `0x86DB0` 加入流程，`0x83A20` 移除流程，`0x83910` 人数增减，`0x87040` 更新球员当前/合同球队指针。仅分析磁盘代码，没有调用修改器或注入其函数。
- 本体代码签名与字段见 `config/roster_association_profile.json`；每次受控修复先在当前游戏内存匹配签名。活动人数的本体序列 RVA `0x8E50A6` 显示高4位计数如何参与活动名单访问。

## 实际入口、批准与范围

- `src/approved_trade_executor.py`：`ownership_transfer_v2`，常规/活动/双向人数和关联核验、15人容量、每次写前比较与回读、防重放；经玩家接受CHI/DET修复结果后启用有限范围执行。
- `src/trade_request.py`：中文方案由Codex整理为模板后，解析姓名/球队缩写、实时唯一身份与自动引用映射；不生成GM方案或报价。
- `scripts/execute_approved_trades.py`：标准 plan/execute/verify CLI，执行必须有上一步固定的身份计划和显式批准开关。
- `scripts/repair_approved_roster_counts.py --request <local.json>`：本次故障专用只读计划/复核；另加 `--approve-game-writes` 才进入受控修复，不是通用绕过入口。它要求两笔交易资产已全部在目标、当前赛季/身份/合同原值一致，只接受已确认的三项计数差异；其他不一致全部拒绝。
- Windows 包装：`scripts/run_approved_trades.ps1 -Request <local.json> -Phase plan -RepairCounts`；执行修复另用 `-Phase execute -ApproveGameWrites -RepairCounts`。只按需提升本入口权限，不采集/发布。

每个request记录玩家实际批准依据，JSON本身不能批准。计划包含精确目标身份、原值、目标字节和签名依据；每次写前再次比较，写后立即回读并落盘。已有 `WRITE_ATTEMPTED` 时拒绝重复写入，保留原回执；混合状态不补交易。失败立即停止，无自动回滚/盲目重试，不承诺原子事务。

## 名单布局及验证边界

| 范围 | 处理 |
| --- | --- |
| 常规名单 `+0x00..+0x77`，15个uint64指针 | 保持连续与人数一致；本次不改变非目标成员 |
| 保留槽 `+0x78..+0xA7` | 当前为空，原样保留；不把21个可扫描槽解释为21人常规容量 |
| 双向槽 `+0xA8/+0xB0` | 本次原样保留；双向球员可实际出现在活动名单，不能错误排除 |
| 活动名单 `+0xD0..+0x137`，13个指针 | 与高4位人数一致、无重复、均属本队名单；故障修复只改对应计数，未重新安排引用 |
| 已观测球队球员引用 `+0xD28..+0xE67` | 首次转队已同步对应人物引用；这不是完整战术字段认证 |
| 球员当前队 `+0x60`、合同归属队 `+0xA8` | 各8字节指针，转队时归属同步；薪资/年限/选项不改 |
| 选秀权记录 `+0x00` | 仅当前持有队8字节；原队、选中球员及其他24字节不改 |

14项执行/计数回归与5项请求解析检查通过，包括本次漏人数/空槽、双向可活动、同名歧义、原合同变化、防重放和短写停止。新标准CLI用仅姓名/原队/目标队的本次已完成资产做了只读核对，两笔均为 `NO_WRITE_NEEDED`、零写入。未为测试重做交易。签约源码另见文档38，本次没有运行或测试它。没有全量采集、数据库/JSON更新、GitHub发布、模拟比赛或推进日期；球队资金由游戏刷新，月度更新仍由玩家主动触发，入口保持原样。

本地证据：`_exports/execution/mc_haliburton_2021/W02_approved_v1/` 保留原始计划、逐写回执、`incident.json`；`count_repair_v1/execute_receipt.json` 保留三个字节修复及30队一致性结果，`plan_receipt.json` 为随后零写入复核。重启观测在同存档目录的 `W02_restart_*/`。运行时地址、原始字节、日志不进Git。当前save_id依赖玩家选择，精确游戏日期仍UNKNOWN；重启后观察到变更保留，但脚本未执行游戏保存，修复后的存盘持久化仍未验收。
