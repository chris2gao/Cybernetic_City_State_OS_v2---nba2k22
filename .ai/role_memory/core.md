# Core role memory

### core-windows-powershell

- guidance: Use Windows paths and PowerShell-native commands in this workspace.
- source_ref: `ai/review/latest@e8ac5bab995a0d5a489953c65f7a5f6c67e35043:.ai/TASKS/v03-local-transport-and-role-memory-0001.md#task`
- last_verified: `2026-07-18`
- expires_or_invalidation: Reverify when the environment class, operating system, or repository AGENTS guidance changes.
- authority: `routing_only`

### core-remote-and-sandbox-boundary

- guidance: The configured Git remote is `origin`; this environment has no repository-enforced filesystem sandbox, so capability must never be confused with task authorization.
- source_ref: `master@a2b7a452feda0fd36c67ae44968a65b80f358b27:AGENTS.md#Git-Workflow`
- last_verified: `2026-07-18`
- expires_or_invalidation: Reverify after remote configuration, runtime permission profile, or AGENTS changes.
- authority: `routing_only`

### core-cooperative-threat-model

- guidance: Lane IDs, profiles, receipts, and role labels are descriptive cooperative metadata; they do not authenticate identity or authorize writes.
- source_ref: `master@a2b7a452feda0fd36c67ae44968a65b80f358b27:.ai/lanes/lane_meta.schema.json`
- last_verified: `2026-07-18`
- expires_or_invalidation: Reverify if a trusted identity, CAS, gateway, or authorization layer is explicitly published.
- authority: `routing_only`

### core-local-authority-redline

- guidance: Local transport carries C0 coordination and C1 shadow evidence only; authoritative C1/C2 events remain immutable Git lane artifacts.
- source_ref: `master@a2b7a452feda0fd36c67ae44968a65b80f358b27:.ai/TOKEN_USAGE_PROFILE.md#Layer-3-Local-Bus-boundary`
- last_verified: `2026-07-18`
- expires_or_invalidation: Reverify only after an independently authorized and published communication-gateway change.
- authority: `routing_only`
