# C4扩展与最终留结果测试：精确候选工程验证

源码/实机证据候选：`d8fc13d86fba5fe2b8627e70accca69fa5d81d8f`。

计划SHA256：`a7bc3ce86dbc2a11e3f206c7849fa82d5fb5ff5753ccb6a9fb263e8767a21559`。

managed_verify的run与inspect均返回success，4项必需检查全部成功：

- native-contract-tests：8项。包括半交易、重复球员、合同错误、反向归属错误不能通过；缺失原生收据不能从退出0晋级。
- offline-preflight：C1离线规格正常，未执行游戏调用。
- artifact-integrity：原C1真实证据、消费许可、原始/暂存字节及C1/C4目录状态一致。
- extended-native-evidence：55个新增证据文件的哈希/暂存字节、10个REA阶段的构建/PID/脚本/清理、私有FullCheck、独立真实交易效果、C1最终13、各新范围已消费均一致。

完整代码候选验证记录保留在同目录managed-extension-code-03；retained_manifest.json记录原始日志逐文件SHA。收尾文档提交后的最终HEAD另外运行同一计划，不把前一候选结果冒充新的HEAD验证。

任务context preflight、big-task closure preflight及MWU validator通过。Git差异空白核对使用`git -c core.whitespace=cr-at-eol diff --cached --check`：原始REA/静态证据为保留哈希而保持原CRLF字节，不能为消除Git显示而改写原始日志。

一次负向测试发现半交易缺失球员时对账器抛StopIteration，已改为明确失败检查值；8项重跑通过。一次提交操作没有返回脚本收据，独立读回仍确认真实互换；验证器专门保持native_return_value_observed=false，未重新执行交易。没有同签名问题耗尽3次修复预算，没有新FAILURE_LOG条目。

这些是执行者自己的工程/证据检查；独立审核尚未建立，也不证明SaveReload、原版AI自主决策链或生产事务可靠性。Human确认总体机制成功并要求结束测试之后没有再附加游戏进程。
