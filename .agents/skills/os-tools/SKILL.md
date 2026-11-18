---
name: os-tools
description: "City-State OS 的 Windows 工具纪律（pwsh 7、UTF-8、退出码、引号）与可选外部工具（check-jsonschema、 mutmut、cosmic-ray、rea）。在 Windows 上写复杂命令、调用外部工具或做变异测试时使用。"
---

# Windows 环境与可选外部工具

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/skills_and_tools/启动清单_v1.yml`（读取分层 `read_tiers`）。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

Windows 命令、外部工具或变异测试相关时。

适用角色：初始化必载 = 无；按触发加载 = 任务开发、审核、特色内容开发

## 启动必读（角色初始化时读完，约 2 KB）

- `01_os/04_skills_and_tools/README.md`

## 按动作读取（做到这一步时再读）

- 在 Windows 上写复杂命令、处理编码或退出码时：`01_os/04_skills_and_tools/windows/README.md`

## 程序读取（validator / runner 读取；只在修改这些文件或排查校验失败时读）

- `01_os/02_boot/skills_and_tools/启动清单_v1.yml`
- `01_os/05_registry/skills_and_tools_v1.yml`

## 边界与停止

- 登记不等于加载；工具可用不等于任务允许
