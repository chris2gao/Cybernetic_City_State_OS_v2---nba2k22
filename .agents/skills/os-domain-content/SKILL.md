---
name: os-domain-content
description: "City-State 领域仓库的特色内容：08_Domain_Applications 下的 domain.yml、领域机制目录 domain_mechanisms.yml 与知识目录。在领域仓工作、开发或使用特色内容时使用；core 仓库没有 08 内容。"
---

# 领域内容（08）

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

特色内容开发、特色内容教学或使用角色初始化；规划或审核领域任务时。

适用角色：初始化必载 = 特色内容开发、特色内容教学或使用；按触发加载 = 任务规划、任务开发、审核

## 有则必读（不存在时在回执里写明缺失，不算失败）

- `08_Domain_Applications/domain.yml`
- `08_Domain_Applications/domain_mechanisms.yml`
- `08_Domain_Applications/knowledge_catalog.yml`

## 命令

- `python -B 01_os/06_execution/boot/context_management/prms/cli.py --repo-root . --commit <40-char> --repository <owner/repo> domain --domain-id <id> --output <outside-repo.json>` → 领域目录 G2 发现；缺目录时为 DOMAIN_CATALOG_UNINITIALIZED

## 边界与停止

- 领域只拥有 08_Domain_Applications/；其余路径与 core 一致，不得在领域仓改 core-owned 路径
- 按 domain_mechanisms.yml 列出的条目读取相关领域机制正文，不整目录读取
