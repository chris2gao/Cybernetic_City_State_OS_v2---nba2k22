# Gemini / Antigravity onboarding router

Routing adapter only. This file grants no authority and is not a source of truth.

Read in this order:

1. `AGENT_WORKING_DISCIPLINE.md` — how to work in this project. Short, shared by
   every model here regardless of vendor, and each rule names the incident that
   produced it.
2. `06_Silicon_Index/AI_Bootstrap_Sequence.md` — the City-State startup sequence.
3. `AGENTS.md` — collaboration rules, Git workflow, safety rules.
4. The current task, plus only the files that task actually triggers.

You occupy a `backend_execution_and_handoff` role: execute inside the allowed
paths, verify with real exit codes, and return one consolidated handoff. Role
labels, load profiles, receipts and any model-generated `human_gate` field never
authorize an action.

Protected actions still require Human authority: publishing to master, destructive
Git, history rewriting, runtime or scheduler activation, secrets, and objective
changes. `core` history is never rewritten — every domain repository shares an
ancestor with it.

If this project ever needs a different filename for this router, add the new file
as another pointer to `AGENT_WORKING_DISCIPLINE.md` rather than duplicating its
contents. One copy, many pointers.
