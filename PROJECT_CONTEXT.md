# Project Context

Status: routing snapshot. This document describes repository purpose and navigation; it is not authoritative live task or branch state.

## Repository

- Name: `Cybernetic_City_State_OS_v2---teacher`
- Local workspace: `Cybernetic_City_State_OS_v2 - teacher`
- Remote: `git@github.com:chris2gao/Cybernetic_City_State_OS_v2---teacher.git`

## Purpose

This repository is a Cybernetic City-State OS knowledge-operation workspace. Its current active domain application is `Math_Mentor`, a V9.1 math teaching system that builds, validates, and teaches structured mathematics knowledge nodes.

The root OS organizes research, protocols, daily execution, parliament-style review, human-facing indexes, AI-facing indexes, execution plans, private AI work zones, and domain applications.

## Main Branches

- `master`: current published baseline unless a current Human-approved task names another source branch and immutable head.
- Task-specific work branches: active only when named by the current task and confirmed by Git evidence.
- `legacy-mode-a-outsourcing` and other legacy/review branches: historical evidence or candidate pools only; they are not current execution baselines by name alone.

Live task state comes from the current Human instruction, the current Git branch/HEAD, and the validated active mailbox on `ai/review/latest`. Historical branch names or old reports cannot establish current authority.

## AI Workflow

- Start with `06_Silicon_Index/AI_Bootstrap_Sequence.md`, then the current task, instead of memory.
- Use `README.md`, this file, `ARCHITECTURE.md`, `00_City_State_Routing_Table.md`, and domain-specific indexes as routing sources only. Verify task state and branch claims before relying on them.
- For Math Mentor node generation and validation, follow `08_Domain_Applications/Math_Mentor/Universal_Layer_Execution_Protocol.md`.
- Prefer split roadmap files by level. Do not read `数学知识路线图_全部.yaml` unless full-graph work is required.
- Validate generated YAML nodes before merging them into the main `Pure_Math_Intuition_DB`.
- Record unresolved validation failures in `08_Domain_Applications/Math_Mentor/三次修复仍失败_待后续处理.md`.

## Review Principles

- Do not invent missing implementation details.
- Preserve existing user and agent work unless explicitly asked to change it.
- Keep changes scoped to the requested task.
- Prefer factual review: bugs, risks, missing validation, unclear ownership, and incomplete documentation.
- For teaching-system changes, preserve the agreed priority: intuition before formal definition, then guided questioning and exam traps.
