# 05_registry

What every file in this system is for, and what loads it. Structured, machine-readable,
and updated in the same change as the code it describes.

## Why this exists at all

The first-generation system had no registry, so answering "is this file still used?"
required reconstructing the answer by reachability analysis. That analysis was correct
and still deleted two working mechanism files, because the thing loading them was not
in the repository and no reference to them existed anywhere. Both were found by
accident while investigating something unrelated.

A registry turns that archaeology into a lookup.

## Holds

One entry per file or exact path-set. Minimum fields:

```yaml
- path: "<exact path or path-set>"
  purpose: "<what it is for>"
  loader: "<what reads it>"
  loader_class: "in_repo_program | external_tool_convention | host_application"
  discovery: "documented convention | hardcoded default | referenced from <path>"
  evidence: "<what establishes the loader claim>"
  cache_dirs: ["<written at runtime, not tracked>"]
  failure_surfacing: "next test run | next execution | never until misuse"
  deletion_rule: "protected | human_decision_required | free"
```

`loader_class` exists because the two files that were lost shared a property: their
loader was outside the repository, reading a path it already knew. Nothing inside the
tree could have revealed them. Any registry that only records in-repository references
reproduces that blind spot.

## Does not hold

**Intermediate files produced by running a task.** Those are traffic, not structure.
They are not registered and they are deleted. If it would not exist in a fresh clone
that has never run anything, it does not belong here.

## The rule that makes it worth having

The registry is updated **with** the development, never after it. A registry that lags
is worse than none: it is consulted, believed, and wrong. The first-generation system
had a generated index claiming 1883 tracked files against a real 503, and it had been
wrong for weeks without anyone noticing, because nothing checked it.

Whatever validator eventually checks this registry should fail on: a registered path
that does not exist, an existing path with no entry, and a declared cache directory
that is neither present nor correctly ignored.

## 当前注册

- `context_management_v1.yml`：上下文管理的 canonical 机制、boot adapter、
  execution loader/validator、活动开发规范、受保护历史和阶段二拆分补充。
- `skills_and_tools_v1.yml`：确定性工具的 Human 选型与接入评估入口；仅注册
  文档，不表示工具已安装、激活或进入 boot。
- `repository_guards_v1.yml`：git 按约定路径从仓库引用图**外部**读取的守卫文件
  （当前为 `.githooks/`）。这正是本 README 开头所述、reachability 分析必然漏掉的
  那一类文件。所有权在 `CORE_MANIFEST.yml` 另行声明：那份答"谁有权编写"，
  本 registry 答"谁加载、怎么被发现、失败何时显形"，两者不可互相替代。
- `repository_validation_v1.yml`：可复用的仓库级确定性校验器、配置与自测入口；
  当前登记个人绝对路径 validator。登记表示可发现和受保护，不表示常驻、boot 加载或
  MCP 暴露。

`08_os/_runs/`、`_runtime/`、角色 private/scratch 不注册。
