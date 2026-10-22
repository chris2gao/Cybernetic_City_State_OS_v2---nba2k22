# 08 Domain Applications — NBA 2K22 业务应用领域

本目录为 NBA 2K22 领域专属业务应用目录，由城市邦联操作系统（Cybernetic City-State OS v2）纳管。

项目已于 2026-10-22 完成从旧独立仓库到 OS 新仓库的完整业务源码与资产刷新（任务代号：`NBA2K22-OS-MIGRATION-01`）。

---

## 一、仓库与业务目录边界

- **新仓库**：`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22`
- **业务应用主目录**：`08_Domain_Applications/Antigravity_GM_Engine/`
- **OS 系统与机制目录**：`01_os/`（core-owned，跨领域共享机制，禁止业务直接修改）
- **业务工作流运行证据**：`01_os/07_content/_runs/`（domain-owned，每个独立任务的运行记录与证据）

---

## 二、OS 统一启动与开发入口

所有参与本领域开发的模型与工程师，必须遵循 OS 统一启动序列：

1. **实时读取 `origin/master` 最新 40 位 SHA**；
2. **遵守行为准则**：[`AGENT_WORKING_DISCIPLINE.md`](../AGENT_WORKING_DISCIPLINE.md)；
3. **读取根级协作指南**：[`AGENTS.md`](../AGENTS.md)；
4. **读取 OS 入口规范**：[`01_os/README.md`](../01_os/README.md) 与 `01_os/开发入口与单窗口任务规范_v1.md`；
5. **领域级约束**：[`08_Domain_Applications/AGENTS.md`](AGENTS.md) 与 [`domain.yml`](domain.yml)。

---

## 三、最新数据架构方向：平行世界数据架构 V2

本领域业务开发以最新的平行世界数据架构为核心蓝图：

- **核心规范**：[`Antigravity_GM_Engine/docs/development/PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md`](Antigravity_GM_Engine/docs/development/PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md)
- **架构原则**：
  - 允许全面重构原有的双 SQLite（`league_state.sqlite` / `player_pool.sqlite`）与采集容器；
  - 建立统一的“平行篮球世界”数据总线，解耦底层 2K 原生内存抓取与上层业务模型；
  - 历史审计产物保留在 `Antigravity_GM_Engine/docs/development_reviews/`；
  - 原生只读逆向成果（AG-NATIVE-01 至 01D）作为底层数据访问能力储备。

---

## 四、后续工程任务规划与路线图

业务迁移完成后，按以下严格优先级开展后续工程任务（一窗口一任务，只登记不提前执行）：

1. **`WORLD-DATA-ARCH-01`**：完整平行篮球世界概念、逻辑及物理数据库模型（基于 V2 架构）；
2. **`NATIVE-ACCEPT-01`**：AG-NATIVE-01C / 01D 单场比赛、赛季统计与球员数据链独立工程验收；
3. **`WORLD-DATA-IMPL-01`**：新数据平台、统一采集、历史保存、查询及旧数据迁移；
4. **角色数据契约开发**：为 GM、Coach、Player 等独立角色构建数据契约与模拟反馈系统。

---

## 五、独立任务分支与审查流程

- **开发分支规范**：所有业务开发必须在独立任务分支（如 `task/<task-id>` 或 `dev/<feature>`）进行，**严禁直接 Push master**；
- **运行证据（Run Evidence）**：每次任务必须在 `01_os/07_content/_runs/<run-id>/` 下建立持久化任务包（`任务包.yml`）、运行清单（`run.yml`）与完成指针（`completion_pointer_v1.yml`）；
- **门禁与合流**：必须通过本地离线测试及 `workflow_publication_gate`，提交后由独立模型（网页 GPT 或评审代理）进行审核，最后由 Human 授权合流至 `master`。
