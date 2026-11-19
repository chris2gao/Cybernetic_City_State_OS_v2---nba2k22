---
name: os-domain-content
description: "City-State 领域仓库的特色内容：08_Domain_Applications 下的 domain.yml 与知识目录、09_Domain_Global_Mechanisms 下的领域机制目录 domain_mechanisms.yml。在领域仓工作、开发或使用特色内容时使用；core 仓库没有 08、09 内容。"
---

# 领域内容（08、09）

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/domain_content/启动清单_v1.yml`（读取分层 `read_tiers`）。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

特色内容开发、特色内容教学或使用角色初始化；规划或审核领域任务时。

适用角色：初始化必载 = 特色内容开发、特色内容教学或使用；按触发加载 = 任务规划、任务开发、审核

## 有则必读（初始化时读；不存在时在回执里写明缺失，不算失败）

- `08_Domain_Applications/domain.yml`
- `09_Domain_Global_Mechanisms/domain_mechanisms.yml`

## 按动作读取（做到这一步时再读）

- 按学习或使用进度加载具体内容时，先读 08_Domain_Applications/knowledge_catalog.yml 与 09_Domain_Global_Mechanisms/domain_mechanisms.yml 的条目，只加载当前模块或课次需要的那几份：按目录条目只读当前需要的那几份

## 程序读取（validator / runner 读取；只在修改这些文件或排查校验失败时读）

- `01_os/02_boot/domain_content/启动清单_v1.yml`

## 命令

- `python -B 01_os/06_execution/boot/context_management/prms/cli.py --repo-root . --commit <40-char> --repository <owner/repo> domain --domain-id <id> --output <outside-repo.json>` → 领域目录 G2 发现；缺目录时为 DOMAIN_CATALOG_UNINITIALIZED

## 边界与停止

- 领域只拥有 08_Domain_Applications/ 与 09_Domain_Global_Mechanisms/；其余路径经合并取自 core，不得在领域仓改 core-owned 路径
- 按 domain_mechanisms.yml 列出的条目读取相关领域机制正文，不整目录读取
