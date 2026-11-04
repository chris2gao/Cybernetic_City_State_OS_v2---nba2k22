# NBA2K22 REA 领域 Profile

本目录连接 Core 的静态工具与 NBA2K22 PC MyLEAGUE 的固定构建。入口会校验目标 SHA256、工具版本和读窗口，并对回执及原始输出验哈希。工具本体由独立 Core checkout 的固定 Git 对象提供。

```text
python -B 08_Domain_Applications/Antigravity_GM_Engine/research/rea_core_profile/bridge.py probe --core-root <core-checkout> --evidence-dir <new-dir>
python -B 08_Domain_Applications/Antigravity_GM_Engine/research/rea_core_profile/bridge.py catalog --nba-root <nba-checkout> --action TRADE_EXECUTE_AGREED_PACKAGE
python -B 08_Domain_Applications/Antigravity_GM_Engine/research/rea_core_profile/bridge.py inspect --core-root <core-checkout> --artifact <exact-build-exe> --evidence-dir <new-dir>
python -B 08_Domain_Applications/Antigravity_GM_Engine/research/rea_core_profile/bridge.py verify-receipt --evidence-dir <existing-dir>
```

`catalog` 需要包含 PR #18 固定提交的本地 Git 对象，可显式运行 `git fetch origin refs/pull/18/head` 获取。Profile 保留该来源的动作、Reader、RVA、ABI 和逐例证据定位。LiveEffectVerified 只对应历史精确输入。StaticRecovered、Pending、LiveSubsetRead 和 ObservedRejection 独立展示。

交易、教练、球探等运行入口由 NBA 领域保有。动作查询返回 PR #26 候选中既有 facade、bulk executor 和 outbox 的版本与入口。当前 Profile 的调用范围为静态工具，实际动作执行需要另一个明确授权的任务和该任务的领域执行入口。历史批单不作为重放输入。

来源见 [PR #18 的能力与验证资料](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/18) 和 [PR #26 的源码集成候选](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/26)。
