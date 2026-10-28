# PR14历史测试建议（Issue15结果另列）

下文保留PR14静态交接时的历史建议，不是Issue15当前状态或新许可要求。Issue15已有Coach新字段、既有球探Goal与薪资不等直接Process交易实测，见[验证报告](VALIDATION_RESULTS.md)。角色模型阅读[机制说明](ROLE_MODEL_MECHANISM_GUIDE.md)，默认交易走新增执行路径；此处旧Wrapper/FullCheck建议不再是当前GM执行要求。后续仅保留训练、选秀、签权/混合包和球探消费等具体未测缺口，不自动开展。

先继承本分支最终提交、Registry/Bindings/ReadCatalog和原始证据。以下目标与数值均由Human或外部GM/Coach/Player模型提供，测试执行者不得自行寻找配平资产、替换人选或优化设置。本轮无任何新游戏/Fixture/单元/回归测试结果。

**不重测PR12的IND防守14→13和原单换单交易；不补原交易收据、SaveReload或交易规则百科。** 新Facade代码集成尚未实测，下一任务按Human范围决定覆盖。每种新逻辑先一个具体案例，拒绝/未知就返回原请求，不能自动换方案。

| 顺序 | 需要的最小场景/模型输入 | 一次测试检查什么 | 约束 |
|---|---|---|---|
| 1 已知对象读取与Coach新字段 | 当前测试存档；指定team/player；一个新POE或Bench字段及值 | UID/合同/当前Coach子集与已有页面相符；仅指定投影字段变化 | 三引用槽NULL；不把当前投影称持久Gameplan；不为重复原成功案例单开试验 |
| 2 训练日程/强度 | 指定球队、已存在的native_date_key、完整训练配置或强度raw值 | 64-byte输入+8日训练payload、值域/float格式和只改指定日/强度；原生日程可能合法no-op | 不猜日期键；不自动选择无比赛日；若已有比赛/无记录由原服务处理或返回上下文不符 |
| 3 球探读取→指定对象分派 | 有有效本届候选人的存档；指定球队、1..17个公开候选UID、空余目标槽 | 当前届次/原始排名/点数/次数；Goal构造→SetSpecific→Append三次调用，目标UID保持一致 | 验证团队索引/Trip+0x13aac；3槽满时返回原拒绝；不自动删除旧目标，不读隐藏潜力 |
| 4 显式执行考察（仅Human要求时） | 已配置specific-prospect目标、剩余次数>0 | 原生DoScoutingTripForTeam消耗一次并更新所配置目标的进度 | 不在无目标或自动挑选类型上执行；不推进日期，不假设立即解锁完整报告 |
| 5 指定当前选秀权选指定新秀 | 独立选秀场景；给定team_id、native pick_id、当前届次player_id | 当前会话Native UID反核、拥有者/空选人槽一致；选择后由引擎完成相关流程 | 只当前未使用pick；不自动推进到指定未来顺位；原生选择本身可能推进下一pick |
| 6 新资产构造链 | 模型给定球队和选秀权/球员组合 | 原生Pick ID→对象→ID反核、AddPlayer/AddPick、Validate及Wrapper执行给定提案 | 不重测原样例；不寻找合法组合、不修工资、拒绝不改提案；有界18元素是物理结构上限 |

**不得直接进入调用的候选**：签约/续约的初始化/枚举/状态处理，Waive八参数中业务标志，员工属性，球员父/子对象copy与refresh链，导师manager映射，完整轮换/分钟，完整Playbook/Gameplan提交。先恢复这些明确缺口再给新测试范围，不能把候选地址当成可用Setter。

接口输入参考Registry的input_schema及各NativeBinding。`LiveExecutionContext.enabled`默认false；下一任务明确授权后，调用方在管理员环境配置允许动作和外部桥调用预算。CLI只提供catalog/plan/emit，没有隐式执行命令。若原生返回/脚本收据缺失，报告UNKNOWN并停止该请求，不自动重试。这里是交接清单，不是已经执行的测试脚本。
