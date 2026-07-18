# Planner role memory

### planner-publish-refs-first

- guidance: Publish every durable task, packet, report, or brief before emitting the pointer that references it; update optional indexes last.
- source_ref: `master@a2b7a452feda0fd36c67ae44968a65b80f358b27:.ai/PROTOCOL.md#Writer-Side-Publish-Order`
- last_verified: `2026-07-18`
- expires_or_invalidation: Reverify when the canonical publication order or pointer contract changes.
- authority: `routing_only`

### planner-name-threat-model-gates

- guidance: State the cooperative threat-model boundary explicitly and keep runtime, gateway, identity, authorization, polling, and protected publication gates separate from descriptive design.
- source_ref: `master@a2b7a452feda0fd36c67ae44968a65b80f358b27:.ai/PROTOCOL.md#Executable-Repository-Compliance-Gate`
- last_verified: `2026-07-18`
- expires_or_invalidation: Reverify after a Human-approved trusted-host or runtime architecture publication.
- authority: `routing_only`
