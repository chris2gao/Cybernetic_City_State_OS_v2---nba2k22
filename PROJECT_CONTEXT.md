# Project Context

Status: routing snapshot. This document describes repository purpose and navigation; it is not authoritative live task, branch, remote, or mailbox state.

## Repository

- Repository family role: reusable Cybernetic City-State core.
- Local repository suffix: `core`.
- Canonical ownership and domain-merge boundary: `CORE_MANIFEST.yml`.
- Live Git identity, branches, remotes, and worktrees must be measured from Git rather than copied from this snapshot.

## Purpose

This repository stores the domain-neutral operating mechanism for a Cybernetic City-State: constitutional authority, bootstrap and load profiles, communication and handoff contracts, compliance validators, cooperative lanes, role memory, execution protocols, indexes, and governance records.

Domain-specific content belongs in a domain repository. Core may define generic extension points and merge contracts, but it does not select, route to, or ship an active binding for a particular domain.

## Main Branches

- `master`: local source baseline unless a current Human-approved task names another source branch and immutable head.
- Task-specific work branches: active only when named by the current task and confirmed by Git evidence.
- `ai/review/latest`: durable review reports and Human Briefs; it is not the source branch.
- Other legacy or review branches are historical evidence or candidate pools only.

Live task state comes from the current Human instruction, the current Git branch/HEAD, and any validated active mailbox. Historical branch names or old reports cannot establish current authority.

## AI Workflow

- Start with `06_Silicon_Index/AI_Bootstrap_Sequence.md`, then the current task.
- Read `AGENT_WORKING_DISCIPLINE.md` and `.ai/TOKEN_USAGE_PROFILE.md` early.
- Use `README.md`, this file, `ARCHITECTURE.md`, `00_City_State_Routing_Table.md`, and generated indexes as routing aids only.
- At a context boundary, select exactly one current profile under `.ai/load_profiles/`.
- For handoff work, load `.ai/PROTOCOL.md` and `.ai/STATE.yml`.
- Validate code, schemas, fixtures, release binding, and generated indexes in proportion to the changed surface.

## Review Principles

- Do not invent missing implementation details or live state.
- Preserve unrelated Human and agent work.
- Keep changes within the current authority and ownership boundary.
- Lead reviews with concrete risks, exact paths, and verifiable Git evidence.
- Treat generated navigation and historical records as non-authoritative unless a current protocol explicitly promotes them.
