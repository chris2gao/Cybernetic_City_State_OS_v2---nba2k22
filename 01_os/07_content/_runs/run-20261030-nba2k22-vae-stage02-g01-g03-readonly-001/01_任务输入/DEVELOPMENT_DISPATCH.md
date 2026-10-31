# VAE Stage02 · Codex G01–G03 只读取证任务

## 入口与角色
- 角色：`execution`；主要执行者：Codex（实际模型与运行产品由本次执行回执记录，不能预先假定具体模型）。
- 任务：`NBA2K22-VAE-STAGE02-G01-G03-READONLY-EVIDENCE-20261030-001`。
- 本任务独立于D1–D5；复用已存在Reader、REA研究和信息规范，不重建另一套数据库或通用Getter。
- 用户已确认精确A-v1；**不得再请其重复确认需求语义**。
- 上游正式七阶段Runner未运行且原收尾任务 BLOCKED；此任务只依据Stage02已成立的确认需求基线进行**有界证据调查**，不是宣称已完成Stage01正式Runner或Stage02完整阶段验收。

## 要取得的三组证据
**G01 (P0) 当前游戏 Profile 与身份**：确认当前实例可能对应的save_id/game build/game mode/场景和目标设置路径；能合法只读观察的取得实际值、原始值、显示值、单位、采样时点和source ref；不能观察的逐字段标UNKNOWN，绝不将旧静态 court/settings JSON 当活跃参数。

**G02 (P0) USER/CPU和控制消费者**：分别标注场上Controller、球队经营权、USER/CPU侧、CPU vs User Gameplay值的读取路径；区分已静态找到、UI看到、Getter已读回、消费路径已实机证明；未找到消费函数绝不推断等价。

**G03 (P0) Normalize与Sim差异**：分别研究两个Normalize开关、Played Quarter、Sim Quarter及3D与Calendar Sim的设置来源、字段身份、对应场景和是否实际消费。两个开关不同，不合并为一个normalize字段；没有原生实测就标MODE_UNVERIFIED。

**跨组输出**：`ProfileContextEvidence`（若有真实允许的读回）、字段级`SourceCoverageMatrix`、`FactVsClaim`、`UnknownAndConflictRegister`和下一步最小取证请求。

## 操作门禁
- 先检查本地/线上仓库真实SHA、任务包、现有REA和Reader版本、实际运行权限与既有Read-only工具成熟度。仅在已拥有适当权限且确认为只读时使用；**不得为了研究而启动管理员游戏、注入、附加未经授权的进程、改变任何设置、SaveReload或写存档**。
- Windows10 + NBA2K22可能管理员运行；若Codex无管理员权限，不得自行提权绕过。可以完成纯GitHub/本地静态读取并提出单项Human授权请求。
- 所有真实数据均需对象身份、时间、来源、观察手段、读取的游戏模式与状态。仅有静态来源时结论仍是研究，不是LIVE。
- 不开展G04–G08、F02–F07的全面合同修复、Stage03 B、游戏写入、比赛效果试验或对D系列的工程修改。
- 不能取到当前游戏事实时，按`PARTIALLY_SUPPORTED_WITH_RUNTIME_GAPS`返回，不制造全局阻塞；后续由规划岗位分派下一轮。

## 交付与审核
按现有 Core Stage02 执行清单、证据包Schema和Minimum Work Unit提交有限证据包与完成指针到**本 Run 的允许路径**，精确Commit+测试/读回，标明每条主张的来源等级、反例、未解冲突、限制及关闭步骤。正式Stage02通用runner/receipt不可伪造。
实现工具需使用的当前模型、平台/角色与实际身份来源写入结果记录，无法证明时写UNKNOWN/DECLARED。
建议初验者为VAE规划岗位证据接收（不是独立审核），正式独立审核后续另派公共基线Fork。
