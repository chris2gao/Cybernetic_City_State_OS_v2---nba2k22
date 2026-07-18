# Token Usage Profile v0.2

Status: effective, reversible discipline profile.  It reduces repeated context and
transport cost without reducing independent evidence, validation, or accountability.
It does not amend `.ai/PROTOCOL.md`, its frozen seven-field wire contracts, or any
Human gate.  GitHub mailbox events remain authoritative; Local Bus is C0 discussion
only and C1 shadow only.

## Layer 1 — operating discipline

1. Human-facing conclusions default to 3–5 sentences plus a decision list; material
   events retain a separate 2–5 sentence independent expression.
2. Execute and capture commands completely: retain exit code and complete stdout/stderr
   in retained local logs plus a digest.  Summarize only at presentation time; expand
   failures when needed.  Use `;` only for independent commands whose exits are kept.
3. Follow the current fast path.  Each foreground reviewer independently reads all
   decisive primary evidence; background summaries route, never replace evidence.
4. Resume only with an explicit session ID after checking repository, task, protocol
   release, source head, and context epoch.  Never resume the “latest” session.
5. Select provider-neutral risk tiers (`T0_mechanical`, `T1_standard`,
   `T2_semantic`, `T3_high_risk`) with a minimum capability and fallback.  Provider
   model mappings are runtime-local, not durable protocol.
6. Treat failure by signature, not command spelling.  A repeat needs new evidence,
   hypothesis, or remedy and remains subject to the repository repair budget.
7. Cache immutable blobs/hashes.  Invalidate mutable facts (HEAD, status, gate) after
   relevant mutation, context boundary, publication attempt, or conflict; fresh-read
   before protected action.
8. Persist only stable, low-risk routing facts with `source_ref`, `last_verified`,
   `expires_or_invalidation`, and `authority: routing_only`.  Never persist approvals,
   task state, gates, or sensitive configuration as standing memory.
9. Check tool ACL separately from the task allowlist.  Use minimal revocable
   permissions and fail closed for secrets, credentials, `.env`, keys, and key stores.

## Layer 2 — measure before budgeting

Each run is one immutable `token_profile_run.v1` JSON record written through a
temporary file and atomic rename. Missing measurements are `null`; do not infer them
or compare incompatible provider metrics as though they were identical. Compare 3–5
matched runs by task type, scale, and acceptance standard before proposing a budget or
protocol change. The executive core of a run report is at most 60 lines and includes
conclusion, evidence, risk, unknowns, and only actual Human decisions.

Required record fields are `schema_version`, `task_id`, `task_type`, `provider`,
`model`, `effort`, `session_mode`, `protocol_profile`, `input_tokens`, `output_tokens`,
`reasoning_tokens`, `cache_read_tokens`, `cache_write_tokens`, `tool_output_bytes`,
`reported_cost`, `wall_seconds`, `repair_attempts`, `review_rounds`,
`validation_result`, `quality_incidents`, and `metric_source`.

## Layer 3 — Local Bus boundary

- C0 may carry ordinary, non-state-changing discussion only.
- C1 is shadow-only: it may measure mirrors, but consumers use GitHub immutable events.
- Gateway engineering and any C1 authority require a separate task, validator,
  adversarial tests, and Human gate.
- C2 always needs a separate Human `AuthorizationContext`; a payload never authorizes
  itself.

The OS-local bus root is `C:/Users/gk/AppData/Local/CityState/local_bus/`. Messages
carry pointers rather than long content, use atomic publication, and receive 30-day
garbage collection. No Local Bus state transition is authoritative.
