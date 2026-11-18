# skills — 按角色加载的 OS skill 生成与校验

Human 2026-11-18 决定把整个 Core OS 做成 skill，按角色加载：Human 只需说明模型的角色，
模型调用对应角色 skill，由它加载该角色需要的全部机制 skill，并输出角色初始化回执。

| 文件 | 作用 |
|---|---|
| `01_os/05_registry/skills_v1.yml` | 唯一来源：机制单元（读取清单、命令、边界）、五个角色（必载、触发、初始化检查） |
| `generate_skills.py` | 从来源与各 boot 清单生成 `.agents/skills/<名>/SKILL.md`（Codex、Antigravity）及字节一致的 `.claude/skills/<名>/SKILL.md`（Claude Code） |
| `validate_skills.py` | 只读校验：磁盘上的 skill 与来源生成结果一致、路径都存在、角色引用的单元都存在、每个已盘点机制都有 skill、输出目录在 `CORE_MANIFEST.yml` 中为 core-owned |
| `test_skills.py` | 生成器与校验器的行为测试 |

```text
python -B 01_os/06_execution/skills/generate_skills.py            # 改了来源或 boot 后重新生成
python -B 01_os/06_execution/skills/validate_skills.py --repo-root .  # 期望 skills_valid，退出 0
python -B -m pytest 01_os/06_execution/skills -q
```

规则：
- skill 是薄适配层，只写何时加载、读哪些精确路径、调用哪些命令；**不复制机制正文**，正文只在 `01_os/` 原处一份。
- boot 清单里的 `.py` 路径列为“入口程序”（调用即可），其余列为“必读”。
- 不手改生成的 `SKILL.md`；改 `skills_v1.yml` 或对应 boot 后重新生成。validator 会把手改报为 `SKILL_FILE_DRIFT`。
- skill 与角色都不授予权限；受保护动作仍按开发入口 §11 与 `repository_publisher_authority_v1.yml`。
- 生成文件能否让模型真正按角色加载，要靠新窗口实测（角色初始化回执与机制矩阵对照），不能由文件存在推断。
