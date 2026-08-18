---
document_id: os-v2-communication-git-blob-utf8-decoding-fix-001::receiver-route-correction-00002
task_id: os-v2-communication-git-blob-utf8-decoding-fix-001
author_endpoint_id: gpt56-communication-utf8-foreground-001
author_task_role: communication_utf8_foreground_dispatch
purpose: Correct only the execution receiver route for the existing UTF-8 implementation dispatch.
privacy_class: repository_shareable
---
# Correction scope

The previously published message `00001` selected `Claude Code Desktop / Sonnet 5` because the foreground interpreted the Human shorthand `CC` as Claude Code. The Human has now clarified that, for the current local execution work, `CC` means the currently used `Claude Desktop Cowork / Claude Opus 5` surface.

This correction supersedes only the receiver route of message `00001`. It does not rewrite, delete, invalidate or reinterpret the immutable `00001` message, constitution, receipt, sender index or recovered pointer. Those artifacts remain durable history of the original routed dispatch.

# Corrected receiver

- collaboration role: execution
- provider: Anthropic
- product: Claude Desktop
- surface: `claude_desktop_cowork`
- model: `Claude Opus 5`
- parameter profile: `claude_desktop_cowork_opus5_task_time`
- endpoint: `claude-cowork-communication-utf8-executor-001`
- task role: `communication_utf8_executor`

The same B task session may re-enter execution after this correction is canonically published and its v2 pointer validates. Re-entry is not implicit continuation: before implementation mutation, the receiver must fresh-read remote master, task branch and worktree state and must pass canonical receiver bootstrap using the corrected pointer.

# Unchanged implementation semantics

The implementation objective, scope, allowlist, prohibitions, tests and completion requirements remain exactly those already authorized by:

- `01_os/_runs/run-20260817-communication-git-blob-utf8-decoding-fix-001/01_任务输入/任务包_v1.yml`
- `documents/gpt56-communication-utf8-foreground-001/00001_execution_dispatch.md`
- `Human/decisions/00001_execution_authorization.yml`

The executor must still implement the narrow locale-independent Git blob UTF-8 decoding fix, must not make `PYTHONUTF8` or Windows locale configuration the permanent solution, must not alter protocol/schema/authority/stage-alignment semantics, and must not publish master.

# Publication rule

Publish this as an append-only formal `correction` message from the same foreground sender. The correction must reference and supersede message `00001` only for receiver routing. Canonical publisher/resolver/gate/receiver validation must run normally; no pointer field may be manually edited.
