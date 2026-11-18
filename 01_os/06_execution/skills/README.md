# skills — 按角色加载的 OS skill 生成与校验

Human 2026-11-18 决定把整个 Core OS 做成 skill，按角色加载：Human 只需说明模型的角色，
模型调用对应角色 skill，由它加载该角色需要的全部机制 skill，并输出角色初始化回执。

| 文件 | 作用 |
|---|---|
| `01_os/05_registry/skills_v1.yml` | skill 元数据：机制单元（各自的 boot、何时加载、命令、边界）、五个角色（必载、触发、初始化检查）。**不写读取清单** |
| `01_os/02_boot/*/启动清单_v1.yml` 的 `read_tiers` | 每个单元“读什么”的唯一来源：启动必读、按动作读取、程序读取、有则必读 |
| `generate_skills.py` | 从 skill 元数据与各 boot 的 `read_tiers` 生成 `.agents/skills/<名>/SKILL.md`（Codex、Antigravity）及字节一致的 `.claude/skills/<名>/SKILL.md`（Claude Code） |
| `validate_skills.py` | 只读校验：磁盘上的 skill 与来源生成结果一致；每个单元都有 boot 且 boot 有 `read_tiers`；boot 点名的路径都进了且只进了一层；`skills_v1.yml` 不再带读取键；路径都存在、角色引用的单元都存在、每个已盘点机制都有 skill、输出目录在 `CORE_MANIFEST.yml` 中为 core-owned |
| `test_skills.py` | 生成器与校验器的行为测试 |

```text
python -B 01_os/06_execution/skills/generate_skills.py            # 改了来源或 boot 后重新生成
python -B 01_os/06_execution/skills/validate_skills.py --repo-root .  # 期望 skills_valid，退出 0
python -B -m pytest 01_os/06_execution/skills -q
```

规则：
- skill 是薄适配层，只写何时加载、读哪些精确路径、调用哪些命令；**不复制机制正文**，正文只在 `01_os/` 原处一份。
- 读取分三层（Human 2026-11-18），写在各单元 boot 的 `read_tiers` 里，只写这一处（2026-11-18 OS-CORE-B0-SPLIT-BOOT-TIERS-20261118-001）：**启动必读** `startup`（角色初始化时读，通常是机制 README）、**按动作读取** `on_action`（每条写明做到哪一步时读）、**程序读取** `program`（登记文件、启动清单、机器 schema、`实现/` 契约、fixture，由 validator / runner 读，模型只在修改它们或排查校验失败时读），另有 **有则必读** `optional`（可能不存在的启动读，目前只有领域 08）。`load_order` 不动，仍是各机制自身 validator 的输入。B0 是 `01_os/02_boot/os_entry/启动清单_v1.yml` 的启动必读，由 `citystate-os` 统一加载；别的 boot 点名的 B0 路径显示为“已由 citystate-os 加载”。boot 里的 `.py` 列为“入口程序”。路径未归层报 `SKILL_PATH_UNTIERED`，进了两层报 `SKILL_PATH_MULTI_TIERED`，缺 `read_tiers` 报 `SKILL_BOOT_TIERS_MISSING`，`skills_v1.yml` 里残留读取键报 `SKILL_REGISTRY_READ_KEY`。
- 每个机制的启动必读超过 `startup_budget_bytes` 时，生成与校验只报告 `SKILL_STARTUP_OVER_BUDGET(report-only)`，不阻断。
- 不手改生成的 `SKILL.md`；改 `skills_v1.yml` 或对应 boot 的 `read_tiers` 后重新生成。validator 会把手改报为 `SKILL_FILE_DRIFT`。
- skill 与角色都不授予权限；受保护动作仍按开发入口 §11 与 `repository_publisher_authority_v1.yml`。
- 生成文件能否让模型真正按角色加载，要靠新窗口实测（角色初始化回执与机制矩阵对照），不能由文件存在推断。
