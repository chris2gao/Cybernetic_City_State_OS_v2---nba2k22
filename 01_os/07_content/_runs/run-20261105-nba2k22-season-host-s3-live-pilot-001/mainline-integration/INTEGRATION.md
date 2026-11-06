# S3 mainline integration candidate

Task: `NBA2K22-S3-LIVE-PILOT-MAINLINE-INTEGRATION-20261105-001`. [Issue #30](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/30) fixes both the integration scope and the existing Human approval. Core 877077c16bad41cfa97c1ebc9862a70ce610ff0b §9 requires a separate review before master moves.

Base: `66f8f73f1a91597f4562b834c2acad332ad9de5b`. Pilot source: `58512372e223845936478ec2a6999093bb5c02e7`. The clean integration branch carries the source content from that exact commit, rather than bringing its original local absolute paths into master history. Fourteen receipt/log files replace machine-specific paths with portable markers; the archived initializer replaces its hardcoded save directory with an explicit `NBA2K22_S3_NATIVE_SAVE_ROOT` environment variable. Both forms are bound by file SHA-256 in [redactions.json](redactions.json). Historical raw receipts and byte-for-byte private audit replay belong to the fixed source; the portable mainline receipts are not a byte-for-byte substitute. No live script was run for this integration.

The initial integration added a safety correction for concurrent intent submission. A deterministic offline test inserted a valid draft after the initial empty-intent read and before the seal. The final empty check now runs under the same SQLite write lock as intent submission. A competing draft refuses closure and remains in the collecting cycle.

The [independent review](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/31#issuecomment-6680525322) recorded `FAIL` for `23a795f983fb33e0cce29bc269e51a9aee08ae57`. Under the [correction contract](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/31#issuecomment-6680575736), S3-INT-01 requires the first live FULL reuse to have the same live date, explicit `SAME_STATE_REPEAT`, a strict boolean false for new finals, and matching canonical and raw Native/SQLite game IDs. Calendar exposes the raw SQLite game ID already returned by its query. This matters because Calendar can report a repeat based on its canonical ID fallback. The Host checks both identities before opening an Outbox cycle. Empty or unproven histories are rejected, including the case where both sides appear empty. During an active game the first baseline attempt returns a rejection and preserves the persisted baseline state.

The targeted regression exercises the real progress detector with a fixture SQLite final for the matching and no-Native-final cases. The other cases cover unknown or missing status, missing or non-boolean flags, canonical or Native ID mismatch, missing SQLite ID, changed date, new final, in-progress game, and an unproven empty history. Each refusal checks for zero new Outbox cycles and unchanged Host state, ledger and Outbox DB. See [verification-plan.json](verification-plan.json) for the exact checks. The follow-up independent verdict is pending.

The retained read-only replay matched the full committed [historical closeout](../receipts/pilot-closeout-audit.json) including four cycles and their digests, 225 distinct new finals, 463 final SQLite games, and zero intents. Replaying the exact observation unit of each of the 10 overtime games accepted the authentic header, rejected a missing header, and rejected a modified header by hash. No retained DB, backup, or native save is included.

Acceptance claims:

- `VERIFIED_S3_CALENDAR_WORLD_DATA_SQLITE_OUTBOX_NO_CHANGE`
- `NATIVE_WRITER_LINK_NOT_EXERCISED`

The original pilot Run remains `verified_on_demand`. This integration's completion pointer is the eventual PR and its exact remote merge readback; until an independent verdict and protected publication readback exist, the integration is a candidate.
