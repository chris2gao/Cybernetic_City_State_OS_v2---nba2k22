# Token scheme implementation 0001 — execution report

## Executive core

- Status: completed candidate for normal PR merge under the pre-approved task packet.
- Source baseline verified: `master` and `origin/master` were both
  `11c34a6962cb7ef94f3469134c915ea15ebb73eb` before branch creation.
- Added `TOKEN_USAGE_PROFILE.md` v0.2 as reversible discipline, explicitly leaving
  `.ai/PROTOCOL.md`, its frozen seven fields, and gate semantics unchanged.
- Added Annex A operational norms for Fable, Codex CLI, Claude Code CLI, seven-step
  dispatch, and C0 chat usage.
- Added local-only token ledger consolidator and C0 chat channel utilities with tests.
- Local Bus remains C0/shadow only; no runtime, coordinator, writer, gateway, or
  scheduler was activated.
- Added the required AGENTS startup instruction and index semantics for the new tools.
- Tool tests: 6/6 passed (`python -m unittest discover -s .ai/token_profile/tests -v`).
- Communication regression: 17/17 passed; complete external log SHA-256 is
  `63a2ce3e7baac1e0315640bf8696e39c195865a375ab0bad38ab25ed2431a15d`.
- Directory index `generate`, `check`, and `validate` passed; second `generate`
  reported `changed_outputs: 0`.
- First index run found the new `.ai/token_profile` directory lacked a semantic
  profile; a narrow generator mapping fixed that cause. No compliance semantics changed.
- Run metrics are in the OS-local immutable ledger record; unavailable provider token
  metrics are `null`, not estimated.
- Residual risk: the new C0 tools are local utilities only and require operational ACL
  enforcement by their host; they make no authority claim.
- drift_cause: null.
- avoided_extra_gates: cleanup, validation, indexing, report, PR, merge, and fresh
  verification remained inside the single Human-approved objective.
- final_original_task_status: completed.
- remaining_real_human_decisions_only: none under the task's pre-approved normal merge.

## Evidence appendix

Validation commands and exact publication/merge heads are recorded in the final review
handoff after the normal PR merge and fresh master verification.

## Independent expression

This is the right boundary for an efficiency program: the tools reduce duplicated
transport while preserving the authority channel that carries actual state changes.
The important follow-up is comparative data, not a premature claim that token savings
alone prove a better workflow. Keeping the bus deliberately non-authoritative is what
makes the local convenience reversible.
