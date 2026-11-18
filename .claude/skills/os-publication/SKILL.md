---
name: os-publication
description: "City-State OS 的发布规则：传输矩阵（本地 git / GitHub API / gh）、发布权限与需要 Human 确认的动作、 push 守卫、master 集成。commit、push、开 PR 或任何受保护动作之前使用。"
---

# 发布、Git 与受保护动作

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/publication/启动清单_v1.yml`（读取分层 `read_tiers`）。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

开发角色初始化；任何 commit / push / PR / master 集成之前。

适用角色：初始化必载 = 任务开发、特色内容开发；按触发加载 = 任务规划、审核

## 启动必读（角色初始化时读完，约 9 KB）

- `01_os/05_registry/repository_publisher_authority_v1.yml`
- `.githooks/README.md`

## 按动作读取（做到这一步时再读）

- push 被守卫拒绝、或要修改守卫时：`01_os/05_registry/repository_guards_v1.yml`

## 程序读取（validator / runner 读取；只在修改这些文件或排查校验失败时读）

- `01_os/02_boot/publication/启动清单_v1.yml`

## 命令

- `git config --get core.hooksPath` → .githooks（本地传输的守卫）；不一致即 blocked
- `git ls-remote origin refs/heads/master` → 发布前 fresh 读取 40 位 SHA，不沿用旧值

## 边界与停止

- master 集成、force、改写历史、删除、runtime 激活需当前 Human 明确确认
- core 历史永不改写；普通任务分支发布是正常流程，不需逐次确认
