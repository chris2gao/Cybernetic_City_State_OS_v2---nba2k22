# Stage 2 local partition experiment

This directory contains the repeatable, non-production experiment for
`context-stage2-local-partition-001`.

Run from the repository root:

```powershell
python "01_os/_runs/run-007-上下文管理信息收集测试/artifacts/local-partition/run_local_partition.py"
python "01_os/_runs/run-007-上下文管理信息收集测试/artifacts/local-partition/run_local_partition.py" --verify-only
```

The run creates a local bare Git repository and planner/executor/reviewer clones
under the system temporary directory. It exercises structured handoffs, a fresh
executor process, deterministic stale checks, context-volume measurements, and a
temporary Windows ACL boundary. The temporary tree is removed before the script
returns.

`PART-01=failed` is the expected truthful result when the unrestricted executor
shell can read the planner sibling sentinel. That result demonstrates that
clone/worktree layout is an organizational partition, not an enforced access
boundary.

Generated evidence is written to `results/` and `logs/`. No credential values,
environment-variable dump, private user content, or remote repository mutation
is part of the experiment.
