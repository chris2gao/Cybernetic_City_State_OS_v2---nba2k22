# Executor role memory

### executor-powershell-dollar-expansion

- guidance: Nontrivial PowerShell containing `$` should be placed in a checked-in or temporary `.ps1` and invoked directly; nested command strings can expand variables before the intended shell sees them.
- source_ref: `ai/review/latest@e8ac5bab995a0d5a489953c65f7a5f6c67e35043:.ai/TASKS/v03-local-transport-and-role-memory-0001.md#C`
- last_verified: `2026-07-18`
- expires_or_invalidation: Reverify when command transport or shell quoting semantics change.
- authority: `routing_only`

### executor-pytest-entrypoint

- guidance: Run pytest suites through `python -m pytest`; executing a test module directly may silently run zero tests when it has no `__main__` entrypoint.
- source_ref: `ai/review/latest@e8ac5bab995a0d5a489953c65f7a5f6c67e35043:.ai/TASKS/v03-local-transport-and-role-memory-0001.md#C`
- last_verified: `2026-07-18`
- expires_or_invalidation: Reverify if the repository test runner or module entrypoints change.
- authority: `routing_only`

### executor-eol-rematerialization

- guidance: When EOL conversion leaves a stale worktree materialization, rematerialize the affected file in an isolated clean worktree and verify the staged blob rather than changing global Git configuration.
- source_ref: `ai/review/latest@e8ac5bab995a0d5a489953c65f7a5f6c67e35043:.ai/TASKS/v03-local-transport-and-role-memory-0001.md#C`
- last_verified: `2026-07-18`
- expires_or_invalidation: Reverify after `.gitattributes`, Git autocrlf policy, or workspace filesystem changes.
- authority: `routing_only`
