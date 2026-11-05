# MyLEAGUE实机功能验证报告

任务：NBA2K22-REA-MYLEAGUE-NATIVE-CONTROL-VALIDATION-01 / Issue15。基线0008af1，继承PR14静态发现2bdda79。Human确认独立可恢复MyLEAGUE日历存档，后续授予本任务持续执行权，明确GM协商、薪资/能力匹配与策略属于外部角色模型。使用者入口：[机制与执行说明](ROLE_MODEL_MECHANISM_GUIDE.md)。

## 三个已取得的实际效果

| 操作 | 精确输入与原生链 | 独立回读结论 |
|---|---|---|
| 新教练字段 | IND20 / Rick Carlisle，RunPlayTendency=55；Apply 0x146eaa0一次 | 90→55；另9项不变，完整352字节投影符合预期，原Gameplan未变 |
| 设置既有球探目标 | IND20，goal_index=0，player_ids=[33143]（Sam Perkins）；SetSpecific 0x1322f30一次 | Goal0原11人→仅UID33143，focus=2、数量1；Goal1/2完整指纹/内容不变，总Goal数3、剩余次数raw7及进度raw69不变 |
| 薪资不等交易执行 | IND20的Malcolm Brogdon UID7239 ↔ MIL1的Donte DiVincenzo UID7716；AddPlayer×2→context Getter→直接Process 0x12e93b0 | 返回1；Brogdon当前/合同球队均20→1，DiVincenzo均1→20；两队名单恰好交换这两人，IND人数15、MIL14保持；两人六年工资字段不变 |

三项均为真实Native与另外只读会话的证据，非Fixture。成熟度只覆盖该教练字段、已有Goal记录设置和该交易资产包，不推广为所有参数均已实测。

交易首年薪资raw为21,700,000与4,675,830，差17,024,170。桥没有执行外围FullCheck、额外Validate、旧Wrapper或外挂薪资/能力评估；Process内部固有资产身份检查保留。未调用完整检查来判定“该交易按完整规则必定不合法”；本轮证明的是不等薪资资产包直接执行成功。两队薪资汇总raw分别133,596,695→116,572,525、151,091,215→168,115,385；payroll_raw汇总未变，未扩展解释其完整语义。

## 保留的拒绝与缺口

Batch02向满3槽IND Trip追加[33143]，原生initialize→focus_specific→append，Append返回0：`REJECTED_BY_GAME`。三个旧Goal、次数和进度独立回读不变。后续Human允许明确设置已有Goal，Batch03另立新请求执行成功；不能将追加拒绝改写为成功。

已有Goal setter只证明目标记录变化。Trip还有聚合缓存，原版DoScout消费前会重建；本轮未执行或消耗行程，未证明完整消费链、UI目标显示或报告解锁。公开候选原始排名/点数不等于隐藏评级或完整报告。

日历场景下选秀为`DEFERRED_NO_SCENE`，未调用Draft getter/selection，未推进日期。签权/混合资产本轮未测；训练、完整Gameplan/轮换、签约/裁员/编辑/导师仍有明确缺口，见[ACTION_SURFACE](ACTION_SURFACE.md)。Player Reader只证明身份与合同17字段，不是完整属性/倾向/徽章读取。

## 可复核的批次与证据

Run：`01_os/07_content/_runs/run-20261027-nba2k22-myleague-native-control-validation-001/`。

| 批次 | Manifest SHA256 | 会话/外部原生调用 | 实测源码 |
|---|---|---|---|
| 01 Coach及只读 | b6074763b5260c5ac6e30a454ecb6a8a832853ec6f1afb964ea0ee3b10f4d8a8 | 6/1 | 8bda78883cbb8f9b10eeabf9a8f08a116fe296db |
| 02 Player及满槽追加拒绝 | 7c7d45475ded7bd5a72b24b986baf5a00424b26a9c32bcb166f5804b365ed4f6 | 7/4 | c97f65c3a25288998db7ba5e160da929c14abc5a |
| 03 既有Goal设置 | 2e41c4ca36a733e55e7fc5e3b635dab11a48820f7ed3e85a19ad57d2088fdd91 | 7/1 | cd61cdb876fe1ea0bec8429294d9b4820dd57f30 |
| 04 直接Process交易 | 1c037007c0fd6ad0881e6b6f5b450048a41e0abf32df4b08c8ca33deef4114d7 | 9/8 | baf361d5的已提交准备脚本，实现与cd61cdb8一致 |

合计29次有限附加、14次外部原生调用；其中Coach1、Append链3、已有Goal1、交易4，其余5为Player Getter。每次读取上限1MiB、REA15秒、GUI线程Hook4秒；唯一PID10940/启动时间及完整EXE SHA固定，标准UAC管理员启动。外部桥调用次数不等于原生内部嵌套调用数。

每批保留原始REA Evidence、实际脚本、请求、case记录、启动退出和逐文件SHA。`07_测试执行/LIVE_OUTCOME_AUDIT.json`逐项核对所有保留文件、精确输入、脚本、次数与前后效果。四个launcher均exit0，无消息错误/截断，cleanup_error均null。原始REA snapshot state仍写running，保留原样；以CLI/launcher完整退出为事实，不伪造DETACHED回执。

效果按Human要求保留；未调用专门保存、恢复、日期推进或UI操作。游戏是否自动保存未观测；本轮UI对应、Save/Reload和独立审核均未证明。交付为研发候选及Draft PR，不等于master或生产Writer验收。

实测后源码只新增去重/空资产包技术检查、授权措辞与证据文档更新。收尾离线核对29个实测输入：28个生成JS与保留脚本一致；唯一差异为Batch01的旧Team Reader，后来增加了首年薪资列，已在Batch03/04实际使用。四个业务效果/拒绝脚本均一致，不增加游戏调用。所有准备脚本与raw文件用局部-text属性保留真实字节，避免Git换行转换破坏SHA。
