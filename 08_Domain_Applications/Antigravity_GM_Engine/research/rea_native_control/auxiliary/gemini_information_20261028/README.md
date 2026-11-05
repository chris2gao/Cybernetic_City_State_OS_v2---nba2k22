# 辅助研究与Owner接收

Human手动把GEMINI_PROMPT_ZH.md发给Gemini；本包不启动模型、不发外部消息。首轮仅三个小包，用实际输出校准能力，而不假定型号名称能证明逆向水平。先局部枚举/布局，再一条短Getter；未通过的包缩小或退回，不升级到实时调用、复杂算法或全局对象生命周期。

`build_information_assist_pack.py --repo <主仓库> --destination <全新独立目录> --source <已提交40位SHA> --manifest-out <Run中的清单路径>`从固定Git blob冻结输入。全EXE不复制，不带私有采集数据。INPUT_MANIFEST.json记录Owner源码、每份文件hash/bytes/blob来源。工具不覆盖已有目录。

Gemini写work/和submissions/<run-id>/；只把提交路径交回。模板初始化后没有结论，不能当作研究成功。submissions目录中的脚本一律视为不可信，不导入、不自动执行。

Owner接收时使用主仓库中的可信检查器、主仓库保留的AUXILIARY_INPUT_MANIFEST_014.json和可信SCOPE.json。不要用Gemini改写的检查器/清单替代：

```powershell
python -X utf8 -B <主仓库>/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/tools/review_aux_submission.py --scope <主仓库>/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/auxiliary/gemini_information_20261028/SCOPE.json --manifest <主仓库>/01_os/07_content/_runs/run-20261028-role-native-execution-system-001/AUXILIARY_INPUT_MANIFEST_014.json --bundle <独立目录> --submission <独立目录>/submissions/<run-id>
```

检查器核对输入完整性、固定目标/任务、文件hash/边界/数量、声明成熟度、真实输出所需结构和反例状态；拒绝越界路径、重解析点、重复JSON键、未列文件及已知禁用工具名。它从不执行提交代码。READY_FOR_CODEX_TRIAGE不是语义正确、工具回执真实、OS访问隔离或独立验收的证明；这些仍需Owner核对。日志中的恶意操作可以伪装，静态筛选不构成安全沙箱。

Owner的快速筛选顺序：

1. 核实主分支最新状态与上次交接提交，输入是否被改，任务是否越界；结构失败先REWORK/REJECT。
2. 按新增价值选择最多三条候选，优先可直接复算的枚举/偏移。将既有事实复述标DUPLICATE，不因篇幅或PASS数量加分。
3. 用可信工具从同SHA二进制独立重放。检查原始字节、CRC唯一性、寄存器/参数、数组extent、正反例与覆盖边界。提交脚本先逐行审查，只在必要时以Owner自写的小离线复算替代。
4. 写review_decisions.json，每项KEEP/REWORK/DUPLICATE/REJECT，附Owner独立来源与理由。只有KEEP的最小事实/代码被挑选入主工程，正常测试与索引同步后另提交。不能整包复制，也不自动注册可调用Reader。

本阶段交接后Codex暂停原探索。Gemini的完成不触发自动接收、合并或继续M0–M5；Human交回后再由Owner处理。Draft PR19维持Draft，完整目标仍未完成。
