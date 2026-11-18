---
name: os-workflow
description: "City-State OS 七阶段工作流：需求建模、信息收集、结果建模、测试生成、步骤拆分、执行、测试执行；阶段产物与 stage_control、冻结测试、三出口、runner 与发布门。做正式七阶段任务或其中任一阶段时使用。"
---

# 七阶段 Workflow

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/workflow_minimum_operational_loop/启动清单_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

规划、开发、审核角色初始化；任何正式七阶段任务或阶段产物。

适用角色：初始化必载 = 任务规划、任务开发、审核、特色内容开发；按触发加载 = 无

## 启动必读（角色初始化时读完，约 2 KB）

- `01_os/01_workflow/README.md`

## 按动作读取（做到这一步时再读）

- 进入阶段 01 需求建模时：`01_os/01_workflow/01_需求建模/README.md`、`01_os/01_workflow/01_需求建模/方法论_v1.md`
- 进入阶段 02 信息收集时：`01_os/01_workflow/02_信息收集与提炼/README.md`
- 进入阶段 03 结果建模时：`01_os/01_workflow/03_结果建模/README.md`
- 进入阶段 04 测试生成时：`01_os/01_workflow/04_测试生成/README.md`
- 进入阶段 05 步骤拆分时：`01_os/01_workflow/05_步骤拆分/README.md`
- 进入阶段 06 执行时：`01_os/01_workflow/06_执行/README.md`
- 进入阶段 07 测试执行或写审核结论时：`01_os/01_workflow/07_测试执行/README.md`
- 运行 runner、验证或发布七阶段 run 时：`01_os/06_execution/workflow/minimum_operational_loop/README.md`
- 核对协同推演激活状态时：`01_os/03_mechanisms/stage_collaborative_deliberation/激活状态_v1.yml`

## 程序读取（validator / runner 读取；只在修改这些文件或排查校验失败时读）

- `01_os/02_boot/workflow_minimum_operational_loop/启动清单_v1.yml`
- `01_os/01_workflow/实现/七阶段最小运行契约_v1.yml`
- `01_os/01_workflow/01_需求建模/实现/需求结果模型模板_v1.yml`
- `01_os/01_workflow/01_需求建模/实现/最小运行schema_v1.yml`
- `01_os/01_workflow/02_信息收集与提炼/实现/最小运行schema_v1.yml`
- `01_os/01_workflow/03_结果建模/实现/最小运行schema_v1.yml`
- `01_os/01_workflow/04_测试生成/实现/最小运行schema_v1.yml`
- `01_os/01_workflow/05_步骤拆分/实现/最小运行schema_v1.yml`
- `01_os/01_workflow/06_执行/实现/最小运行schema_v1.yml`
- `01_os/01_workflow/07_测试执行/实现/最小运行schema_v1.yml`
- `01_os/05_registry/workflow_minimum_operational_loop_v1.yml`
- `01_os/05_registry/workflow_publication_gate_v1.yml`

## 入口程序（调用即可，不必通读源码）

- `01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py`
- `01_os/03_mechanisms/context_management/实现/verify_context_structure.py`
- `01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_no_canonical_live_state.py`
- `01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation_v2.py`
- `01_os/06_execution/workflow/publication_gate/workflow_publication_gate.py`

## 命令

- `python -B 01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py static .` → 退出 0
- `python -B 01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py validate <run-root> --repo-root . --candidate <40-char>` → 完整提交态验证；缺 candidate 返回 41，不是通过

## 边界与停止

- 测试由证据推导，不由 B 推导；循环开始后测试冻结
- 三出口 pass / retry / invalidate_upstream；预算耗尽或失效不能伪装完成
- 审核者写统一审核结论，07 阶段完成值由它推导
