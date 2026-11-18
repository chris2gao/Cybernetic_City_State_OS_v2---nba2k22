---
name: os-mechanism-activation
description: "City-State OS 正式跨端点动作的宪法路径。要让另一个模型或端点行动，或要发出/接收任务范围内的 request、response、result、correction、blocked、decision 交接时使用；普通 Human 对话不需要。"
---

# 机制激活与正式动作宪法（L3_EXECUTION_GATED）

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/mechanism_activation/启动清单_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

正式跨端点动作之前（AGENTS.md 要求常开）；核对物质验收主张时。

适用角色：初始化必载 = 任务规划、任务开发、审核、特色内容开发；按触发加载 = 特色内容教学或使用

## 必读（按顺序全部读完）

- `01_os/02_boot/mechanism_activation/启动清单_v1.yml`
- `01_os/03_mechanisms/mechanism_activation/README.md`
- `01_os/03_mechanisms/mechanism_activation/正式动作宪法_v1.yml`
- `01_os/03_mechanisms/mechanism_activation/机制触发注册表_v1.yml`
- `01_os/03_mechanisms/mechanism_activation/物理事实双向绑定契约_v1.yml`
- `01_os/03_mechanisms/mechanism_activation/机制生效等级与盘点_v1.yml`
- `01_os/03_mechanisms/mechanism_activation/验证适用性契约_v1.yml`
- `01_os/05_registry/mechanism_activation_v1.yml`

## 入口程序（调用即可，不必通读源码）

- `01_os/06_execution/boot/mechanism_activation/activation.py`
- `01_os/06_execution/boot/mechanism_activation/validate_mechanism_activation.py`

## 命令

- `python -B 01_os/06_execution/boot/mechanism_activation/validate_mechanism_activation.py static .` → validation_passed，退出 0

## 边界与停止

- 接收方不唯一 → FORMAL_ACTION_BLOCKED_UNTIL_RECIPIENT_RESOLVED
- 绕过 resolver 或 gate → INVALID_FORMAL_ACTION；自我授权禁止
- 物质验收主张须期望来源、物理观察和已执行的比较器三者齐全，全部 VERIFIED 才通过
