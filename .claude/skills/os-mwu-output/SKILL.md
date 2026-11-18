---
name: os-mwu-output
description: "City-State OS 三个边界的正式输出格式：正式派单、执行完成交接、独立审核完成。写这三类产出时使用，要求做了什么、方法、可支撑理由、可行理由，以及角色附加字段。"
---

# 最小工作单元输出（L1_BOOT_VISIBLE）

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/minimum_work_unit_output/启动清单_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

写正式派单、执行交接或审核结论时。

适用角色：初始化必载 = 任务规划、任务开发、审核、特色内容开发；按触发加载 = 特色内容教学或使用

## 必读（按顺序全部读完）

- `01_os/02_boot/minimum_work_unit_output/启动清单_v1.yml`
- `01_os/03_mechanisms/minimum_work_unit_output/README.md`
- `01_os/03_mechanisms/minimum_work_unit_output/最小工作单元输出契约_v1.yml`
- `01_os/05_registry/minimum_work_unit_output_v1.yml`

## 入口程序（调用即可，不必通读源码）

- `01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py`

## 命令

- `python -B 01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py --root . static` → validation_passed，退出 0
- `python -B 01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py --root . --require-mwu artifact <path>` → 校验一份正式产出

## 边界与停止

- 审核结论统一为 PASS / FIX_REQUIRED / REJECT
- 执行者理由是待检验的证词，不是证据；不要求也不提交 chain-of-thought
