# NBA Profile 独立审核交接

任务 `OS-CORE-WORKFLOW-REA-PROMOTION-20261029-001`，S4 与 S5 跨仓静态验证。

- NBA 基线 `45cc45cae0550ddcda192a2179ea48509b27f6ee`，测试源 `228abf11fc15d34a0a3d71813581adc6797ef58d`。
- Core 测试源 `f083ae685764e88e6f522cc91f2c58b7a33ee99f`，实际适配器固定到 `a668307405df1f932008ba27be073654878bb577`，适配器字节与 Core 测试源相同。
- 来源为 PR #18 Draft `094f1aa641f93dec2277707ad9dbf5bdb0341247` 和 PR #26 源码候选 `aee5a9109ea5cd0a5c7bc4adb750c64a1603afec`。前者提供能力、绑定与历史逐例记录，后者提供业务 facade、Bulk、Outbox 的定位。

交付包含项目索引、P03/P09 模块记录、领域 Profile 和可执行桥。桥校验静态工具的版本、目标 SHA256、读窗口和回执输出哈希。动作目录覆盖 62 项动作、38 项绑定及 12 组读取资料，保留原例证据分级。

候选绑定的 managed verification 和 inspect 均返回 success。Profile 测试 6 项通过。同候选索引检查返回 `INDEX_SYNCED_FOR_CANDIDATE`，影响模块 P03/P09，pending 为空。项目发现得到 13 项，按需读取 P09 的一个正文。G2 目录仍报告 `DOMAIN_CATALOG_UNINITIALIZED`。

`joint_static_result.json` 记录真实 REA 6.8.0 跨仓静态调用。在非游戏 PE 样本上，原 NBA Profile 拒绝不符构建，测试 Profile 接受该样本并校验真实静态回执。原生业务调用、UI、存档效果均为 `NOT_RUN`，历史逐例证据保持原边界。

独立审核者从上述固定候选重建差异并运行 `verification_plan.json`。跨仓复验使用 `verify_joint.py --core-root <Core checkout> --nba-root <NBA checkout> --core-head <verified Core SHA> --nba-head <verified NBA SHA> --fixture-binary <non-game PE/ELF/Mach-O> --evidence-dir <new directory>`。如缺少 PR #18 的 Git 对象，显式获取 `refs/pull/18/head`。

工程所有者提交证据供另一个隔离会话核对。独立审核状态为 `PENDING`。
