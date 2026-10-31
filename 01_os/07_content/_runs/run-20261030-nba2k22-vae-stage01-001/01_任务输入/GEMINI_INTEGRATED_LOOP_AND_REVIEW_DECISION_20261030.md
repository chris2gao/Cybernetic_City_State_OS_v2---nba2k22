# VAE · 一体化Gemini循环开发与集中审核决策（2026-10-30）

## Human本轮指令
“给gemini的任务，尽量做成loop的，让它可以不断完善，需要你重新规划下任务，另外任务不要切成一个一个的，尽量统一开发，统一审核，集中开发，集中审核。”

这条明确指示覆盖旧NBA项目默认Codex主Owner/Gemini辅助模式的**当前VAE新任务分配**，但不推翻Core权限、独立审核、Workflow版本与阶段检查点。

## 实施路径
- 一个Gemini开发主任务：`NBA2K22-VAE-GEMINI-INTEGRATED-LOOP-20261030-001`。
- 单一派单提交：`49659925312275d101232c3bc522f162436d28d5`。
- 单Run：`01_os/07_content/_runs/run-20261030-nba2k22-vae-gemini-integrated-loop-001/`；除下一轮真的触发权限/架构越界，**内部G01-G08、R01-R09、F02-F07与原型修复只写进同Run并持续迭代**。
- 主Owner：Gemini Flash 3.8（Human声明，平台型号认证UNKNOWN）；本地安全只读/离线程序开发。Codex额度不可用，旧任务仍`deferred`。
- 项目规划仍由当前GPT`decision_architecture`；开发者的实施与静态测试不等于独立审核。
- 一个集中审核：首个完整原型候选和统一证据/测试报告冻结后，另开一个GPT`independent_review`窗口，从公共基线独立启动，整体验收。一般内部循环不安排独立审核，只有材料重要变更后针对阻塞问题必要复验。

## 循环合同与收敛
同一任务`inspect → evidence/oracle → implement → cheap_verify → repair → checkpoint → repeat`，按失败集收缩、GAP明确减少和可重放功能增长来判断继续，不按固定轮数。
目标交付是真实可执行的**离线/安全只读纵向原型**与严谨的现实信息缺口，不把过去静态settings/court值、REA特定实例、fixture测试伪称当前游戏LIVE成功。
工作流既有Human阶段计划/完成检查点仍保留；涉及受保护游戏操作、启动进程、提权、SaveReload和存档写入必须另有具体Human授权。新增全局架构或超出allowlist需要立即停止并回传。
Gemini窗口并不在后台自动执行：只有Human实际启动并保持可用的执行面时才推进，每轮真实结果存GitHub，不承诺无限自主持续运行。

## 上游阶段与现有问题
- Human确认固定A-v1：`5abf3cb154654872a3d05278b96658f190ed9241`，blob `612ed21f8f3e441366296ee2ac6170bb5974584b`；批准`a98aa2db6e442bbc3aecfa552665ea13d482683e`。
- 独立审核`PARTIALLY_SUPPORTED`，F02–F07开放；Gemini同Run闭合合同修订与测试，不改原A或审核材料。
- Core完整七阶段Runner`NOT_RUN`，不能夸大为已验收；单阶段runner不存在不能替代真实完成凭据。
- VAE与D1–D5平行；不改旧Reader/REA等共享代码，除非另有授权扩边。

## 规划任务接收
Gemini开发期间完整日志留在它的Run；只在产生可供集中审核的完整候选，或真正需要Human处理的止步事项时向规划岗位交接。
正式结果须按MWU给出task_id、精确Git SHA、可执行原型、测试结果、源分级、模型身份来源、风险和完结指针。规划窗口据此统一安排审核，不接受“某个小缺口已修好”作为需要另立审核任务的理由。

PRMS SAVE_TASK_CONTEXT和Formal Communication v2未执行，本决策以GitHub Run固定指针恢复。
