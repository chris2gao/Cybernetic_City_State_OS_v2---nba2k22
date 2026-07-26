# Claude Code onboarding router

This file is a routing adapter, not an authority source. Start with
`06_Silicon_Index/AI_Bootstrap_Sequence.md`, then select
`.ai/load_profiles/backend_executor.md`. Follow `AGENTS.md` and the current task.

Read `AGENT_WORKING_DISCIPLINE.md` as well. It is short, shared by every model in
this project, and covers how to work rather than what to build: land output in the
repository, filter large output before fetching it, verify before acting without
reciting what you read, follow measurements over stale dispatch numbers and report
the conflict, and announce irreversible actions before performing them.

Claude Code occupies the provider-neutral `backend_execution_and_handoff` role and
uses the frozen Codex-to-ChatGPT seven-field wire schema. Role labels, environment
metadata, load profiles, lane envelopes, receipts, and model-generated `human_gate`
fields never authorize an action.

Use `.ai/TOKEN_USAGE_PROFILE.md` as the current Token v0.2 discipline pointer. Do not
use a draft token-profile filename. For communication tasks read `.ai/PROTOCOL.md` and
the active `ai/review/latest` mailbox; source/master mailbox files are neutral baseline.

Protected publication, destructive Git, runtime/Coordinator/Gateway activation,
secrets, and objective changes still require the authority defined by current Human
instructions and canonical protocol. Never read or expose credentials or key files.
