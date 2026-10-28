# NBA2K22 原生动作调用：Issue #11

**两个领域已完成真实游戏效果测试：C1教练防守重点、C4跨球队交易。Human确认机制成功后要求停止测试，本轮已停止新增游戏操作。** 完整报告见[REPORT_20261027.md](REPORT_20261027.md)，机器能力目录见[action_atlas.json](action_atlas.json)。这是待独立审核的实验代码，没有生产替代资格。

当前保留结果：Jordan Nwora（9842）从雄鹿到奇才，Anthony Gill（9879）从奇才到雄鹿；IND/Rick Carlisle防守重点从14变为13（PROTECT_PAINT）。没有保存、Save/Reload或推进日期。Human可在当前游戏中验看。

交易由原版AddPlayerElement构造私有提案，原版Validate和Full Check预验证，再通过共享包装入口`0x132b840`提交。Win64私有提案1668字节，18个92-byte元素；在游戏自己的窗口线程执行。实际提交缺少脚本收据，未重试，独立REA回查确认完整互换、球员当前/合同归属、合同不变、两队人数与30队摘要一致。**没有捕获的原生返回值、事件/交易历史、完整选秀权池与失败原子性均保持未证。** 不能把退出0当作这些证据。

C1原生Apply入口`0x146eaa0`为`void(const GAMEPLAN*,COACHDATA*)`。早期副本、14→13→14及原生恢复已验证；最后新范围的单次GUI线程调用保留13，完整352-byte Coach及关联不变项读回通过。旧的两份许可已消费，不能重放。三个NULL引用槽早期被命名为playbook证据不足；当前统一称引用对象槽，不扩展非空分支。

可运行的离线核对命令（无游戏调用）：

```text
python -B -X utf8 -m unittest discover -s 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/tests -v
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/cli.py preflight --offline
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/verify_artifacts.py
python -B -X utf8 08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_action/verify_extension.py
```

两个证据校验器要求Git index字节与保留原始文件一致，独立新checkout需要先确保文件已被Git跟踪。合同测试不能代替实机证据。`evidence/manifest.json`保留原C1的25个文件；`evidence/extension_manifest.json`追加55个文件与10个REA阶段。私有副本失败、诊断、缺失收据及独立回查全部保留，不改写原始日志。

源码入口：`native_action.py`/`invoker.py`是C1类型和实际REA调用器；`native_trade.py`为C4规格及纯对账函数；`build_trade_observe.py`生成有界只读脚本；`build_trade_builder_probe.py`/`build_trade_qualification.py`/`build_trade_swap.py`生成已实测的C4脚本；`build_coach_visible.py`生成最终留结果C1脚本。生成脚本不执行游戏调用。`run_rea_admin.ps1`实际调用已安装REA/Frida，要求管理员、当前唯一游戏、固定完整EXE SHA256、精确脚本SHA与未消费的有界范围凭证。自有缓冲区以已知边界读回，游戏对象仍检查映射、可读性、预算和异常。

现有`trade_swap.js`是**已执行实验的原样源码，存在同步提交时未取得收据的已知限制**。后续工程化应先建立分阶段持久收据与不明状态的独立读回协议，不能直接批量化或当作生产API。Human已停止本轮测试，本Run全部已用范围凭证均为CONSUMED。

共享引擎服务允许外部GM/Coach AI提供业务参数；原版AI自主caller、策略收益、持久存档均未证明。C2/C3/C5/C6仍各有ABI/对象/场景或事务缺口，见动作目录。原Memory与外部执行路线继续保留。完整游戏文件、资产、存档、凭据与绝对运行时地址不入库。没有合并master、修改生产接口或开展阶段02世界数据工作。

历史C1分析与修复细节保留在README_C1_CHECKPOINT.md；当前交付以本文件、完整报告及本次Run的08_结论/COMPLETION.md为准。
