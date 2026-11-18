---
name: os-context-management
description: "City-State OS 的上下文管理机制：三个信息平面、文件放在哪里、私有运行时怎么处理、累计区的可见性与归档、项目资料发现与索引同步、workspace 边界。每个角色初始化时加载。"
---

# 上下文管理、文件放置与工作集（L1_BOOT_VISIBLE）

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/context_management/启动清单_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

每个角色初始化；放置或删除文件；枚举仓库或历史；归档 run；改项目资料索引。

适用角色：初始化必载 = 任务规划、任务开发、审核、特色内容开发、特色内容教学或使用；按触发加载 = 无

## 启动必读（角色初始化时读完，约 5 KB）

- `01_os/03_mechanisms/context_management/README.md`
- `01_os/03_mechanisms/context_management/文件隔离与产物生命周期_v1.md`

## 按动作读取（做到这一步时再读）

- 需要理解三个信息平面、恢复与 stale 规则时：`01_os/03_mechanisms/context_management/方法论_v1.md`
- 枚举历史、判断可见性或归档 run 时：`01_os/03_mechanisms/context_management/工作集与归档契约_v1.yml`
- 涉及执行者、workspace 与访问边界时：`01_os/03_mechanisms/context_management/决定_谁执行_v0.2.md`
- 修改项目资料索引或模块记录时：`01_os/03_mechanisms/context_management/项目资料发现与索引同步契约_v1.yml`

## 已由 citystate-os 加载（B0，不必重读）

- `01_os/README.md`

## 程序读取（validator / runner 读取；只在修改这些文件或排查校验失败时读）

- `01_os/02_boot/context_management/启动清单_v1.yml`
- `01_os/03_mechanisms/context_management/实现/文件布局契约_v1.yml`
- `01_os/05_registry/context_management_v1.yml`

## 入口程序（调用即可，不必通读源码）

- `01_os/03_mechanisms/context_management/实现/verify_context_structure.py`

## 命令

- `python -B 01_os/03_mechanisms/context_management/实现/verify_context_structure.py` → context-management structure: PASS，退出 0
- `python -B 01_os/06_execution/boot/context_management/working_set/visible_set.py --list` → 默认工作集，并报告隐藏了什么；过滤结果不是穷举

## 边界与停止

- clone/worktree 只是 workspace_partition，不是访问边界
- 发布只用精确 allowlist；禁止 git add --all、git add .
- 旧聊天不是事实来源；依赖 hash 变化即 stale
