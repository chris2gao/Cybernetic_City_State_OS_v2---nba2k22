# NBA 2K22 领域全局机制与角色目录 (Domain Global Mechanisms)

本目录为 NBA 2K22 领域专属的全局机制、领域角色定义与加载配置空间。

根据 City-State OS 架构规范：
- `08_Domain_Applications/` 拥有领域业务正文与知识资产；
- `09_Domain_Global_Mechanisms/` 拥有领域机制目录（`domain_mechanisms.yml`）、领域专属角色定义与上下文记忆引导。
Core 核心仓不包含 08 与 09，由本领域独占所有权。

---

## 已注册的领域角色

1. **数据分析与决策角色 (Data Analysis & Decision Architecture)**:
   - 角色 ID: `data_analysis_and_decision`
   - 协作角色类型: `decision_architecture`
   - 说明与定义: [`roles/data_analysis_and_decision/README.md`](roles/data_analysis_and_decision/README.md)
   - 初始化启动引导: [`roles/data_analysis_and_decision/BOOTSTRAP_GUIDE.md`](roles/data_analysis_and_decision/BOOTSTRAP_GUIDE.md)
   - 离线上下文记忆: [`roles/data_analysis_and_decision/OFFLINE_CONTEXT_MEMORY.md`](roles/data_analysis_and_decision/OFFLINE_CONTEXT_MEMORY.md)
   - 当前工作台状态: [`roles/data_analysis_and_decision/CURRENT_STATE.md`](roles/data_analysis_and_decision/CURRENT_STATE.md)
