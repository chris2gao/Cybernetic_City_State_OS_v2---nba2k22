# GREA-01: 对手Gameplan修改与原生提交调用链探索任务书

## 1. 任务背景与目标
在NBA 2K22 MyLEAGUE模式中，教练可以为特定对手（如Pacers针对76ers、Bucks、Nets等）制定独立比赛计划（Gameplan），包含个人防守对位、施压策略、战术重点与轮换时间线。
前期REA研究已发现：
- `COACH_ENSURE_OPPONENT_GAMEPLAN` 能找到或分配对手Gameplan槽位；
- 但 `COACH_SET_GAMEPLAN` 仅具有不完整的数据读写，缺少原版游戏业务层完整的保存、刷新、通知和持久化事务机制。

**GREA-01 任务目标**：
1. 彻底逆向搞清对手Gameplan的宿主对象所属关系、内存连续性与索引算法；
2. 解析具体字段（首选 `PressureOnball`）的原生Setter/Apply与位掩码；
3. 阐明修改多对手时的空间隔离机制；
4. 恢复原生UI提交事务流程（包括 `IsInUse` 激活与 `dirty_flags` 同步）；
5. 编写完全隔离的候选编解码器和离线验证测试，供Codex进行独立工程审核。

## 2. 角色分工与执行边界
- **执行模型**：Gemini（REA Native机制探索与隔离候选开发）。
- **工程所有者**：Codex（负责最终工程审核、实机验证与主干集成）。
- **约束边界**：
  - 严禁向运行中的游戏进程注入内存写入；
  - 严禁调用推进日历或产生非受控状态变更的原生函数；
  - 代码与测试只能写入 `08_Domain_Applications/.../experimental/gemini_rea/GREA_01/`；
  - 禁止修改 `master` 或Codex的工作目录。

## 3. 验收标准
1. **结构对齐**：880字节（`0x370`）`GAMEPLAN` 结构及 `0x13E70` 字节 `FRANCHISE_GAMEPLAN_MANAGER` 结构完整逆向；
2. **字段验证**：`PressureOnball`（3 bits，取值0..4）编解码及周边位段隔离完全验证；
3. **多对手隔离**：证明并测试多对手槽位互不干扰的不变性；
4. **事务完整**：文档化完整调用链，包含RVA、参数、汇编与成熟度分级；
5. **离线测试**：单元测试100%通过（pytest exit code 0）。
