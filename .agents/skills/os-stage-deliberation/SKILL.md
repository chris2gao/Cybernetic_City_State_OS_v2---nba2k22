---
name: os-stage-deliberation
description: "City-State OS 七阶段 Workflow 的阶段协同建模：统一当前模型、可行性依据、未知项处置、阶段 start/completion gate、十个状态维度与 stage receipt。正式七阶段 run 的阶段计划与完成签收时使用；默认休眠。"
---

# 阶段协同推演与增量再确认（L1_BOOT_VISIBLE）

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/stage_collaborative_deliberation/启动清单_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

正式七阶段 run 的每个阶段计划与完成检查点；出现承重缺口时。

适用角色：初始化必载 = 任务规划；按触发加载 = 任务开发、审核、特色内容开发

## 启动必读（角色初始化时读完，约 4 KB）

- `01_os/03_mechanisms/stage_collaborative_deliberation/README.md`

## 按动作读取（做到这一步时再读）

- 正式七阶段 run 的阶段计划或完成检查点时：`01_os/03_mechanisms/stage_collaborative_deliberation/方法论_v1.md`、`01_os/03_mechanisms/stage_collaborative_deliberation/阶段profile契约_v1.yml`、`01_os/03_mechanisms/stage_collaborative_deliberation/阶段profiles_v1.yml`
- 核对机制激活状态或其 Human 授权时：`01_os/03_mechanisms/stage_collaborative_deliberation/激活状态_v1.yml`、`01_os/_runs/run-20260804-阶段协同推演闭环激活-001/01_任务输入/Human授权_全局机制激活_v1.yml`

## 程序读取（validator / runner 读取；只在修改这些文件或排查校验失败时读）

- `01_os/02_boot/stage_collaborative_deliberation/启动清单_v1.yml`
- `01_os/03_mechanisms/stage_collaborative_deliberation/实现/结果对象契约_v1.yml`
- `01_os/03_mechanisms/stage_collaborative_deliberation/实现/状态转换与不变量契约_v1.yml`
- `01_os/03_mechanisms/stage_collaborative_deliberation/实现/路由与失败契约_v1.yml`
- `01_os/03_mechanisms/stage_collaborative_deliberation/实现/加载与receipt契约_v1.yml`

## 入口程序（调用即可，不必通读源码）

- `01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_no_canonical_live_state.py`
- `01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation.py`
- `01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation_v2.py`

## 命令

- `python -B 01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_no_canonical_live_state.py .` → 退出 0（先跑）
- `python -B 01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation_v2.py static .` → 退出 0

## 边界与停止

- Human 批准是权力不是证据，不能当可行性依据
- 普通局部可逆选择不要 Human 微审批；新承重选择、范围扩张、未覆盖受保护动作须当前 Human 明确决定
- canonical 目录不保存实时实例状态
