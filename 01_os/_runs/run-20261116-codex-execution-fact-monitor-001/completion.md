# Codex execution-fact monitor — G1 / G2 / G3 candidate

completion_pointer: This file. Code candidate `475a2245aa9a8b422c2c0edfcb3dbd123c518dea`; later delivery commit changes only this Run. Branch `task/execution-fact-monitor-20261115`, base `043ac4864bdc871b03929faafd8bc6bd47d4ee2f`. No master integration or independent acceptance claimed.

## Implementation and actual Done

- G1: Read-only native JSONL parsing. Reused Codex candidate `f739d4c9…`; corrected native seconds/nanoseconds durations, MCP results/errors, function arguments, orphan results, source locators and unknown call IDs. A native item ID is not invented as a call ID. Messages/reasoning are ignored; missing data stays unknown.
- G1 real sample: NBA #44 execution session `01a1df5a-4c7c-75b3-9174-cd55b3087c96`. Replay produced 114 records: 22 tool calls, 24 results, 55 command items, 8 file-change items and 5 MCP items. These are different evidence levels, not 114 distinct business operations. Two results lack a matching call. Independent raw-source comparisons in `verify_real_replay.py` verified every native command/exit code/available duration, MCP arguments/results, and original call IDs.
- Historical source SHA-256 before/after: `9f5e7760d9cf8c86c85081c9e036454949480c24c693b76ec3d8c4d9adb5632b`. Source was not modified; no SQLite supplement was necessary.
- G2: Explicit foreground watch of the current native session `01a1df56-1f09-7930-a12f-466f4743a337`, starting at byte 1777261, interval 0.2 s. It collected 3 newly generated native events; all retained fields were checked against the original source at their byte offsets. No synthetic appends were made to official logs. Final parser bookkeeping adds an optional native item ID; the actual captured fields remain valid under the final parser.
- Real terminal Ctrl+C printed `stopped` after 23.946 s; the hosting PowerShell/PTY returned exit 1. Post-stop Win32 process count for PID 11584 was zero, and the events file remained 2805 bytes with SHA-256 `8faf462687e4556fa58c8216a94defed7ade54e58b0ba5e82cb27aa18dac7398` across subsequent commands. No watcher/service/scheduled task remains. Native Codex logging continues independently.
- ON resource sample: process cumulative CPU 0.0625 s, working set 17,764,352 bytes, private bytes 12,959,744. The tool's loop CPU counter returned 0.0 s at host timer resolution; this is not proof of zero CPU. These observations concern only the bounded 23.946 s run, not general overhead.
- G3: Both replay and live watch have usable local `events.jsonl` and `report.md`. Report retains unmatched results, chronological known times, unknown fields and original source pointers. Corrupt source lines become explicit gaps. It makes no behavior judgment or business-time attribution.

## Readable local outputs and raw verification

The following existing local artifacts are intentionally not copied into Git: native outputs can include task text, paths, commands and tool results.

- Replay: `C:/Users/gk/Documents/ChatGPT/nba2k22/factmon-codex-validation/replay/events.jsonl` (605712 bytes), `report.md` (77368 bytes), `verification.json`.
- ON/OFF: `C:/Users/gk/Documents/ChatGPT/nba2k22/factmon-codex-validation/watch/events.jsonl`, `report.md`, `verification.json`.
- Exact-candidate managed raw attempt: `C:/Users/gk/Documents/ChatGPT/nba2k22/factmon-codex-validation/managed-475a2245/`. `run` and `inspect` returned success for required `focused_contracts` (11 tests) and `real_replay`. Plan SHA-256 `0379f288668c440cde66fe73c7700f40a16221f906b4c03d4ccddebc5ccf989d`; input SHA-256 `5084bb8c6cc327b55ea0a243ce3ad32779eb35f98faab3784e4f5daf6e75dea0`; result SHA-256 `65ceae5be15cc4c246522a7ee8345854159d8cb42683d4d40e315a3758ffd9b6`.
- Actual commands/results and the resource/stop observations are also in this execution's native Codex session, readable by the same tool. The earlier managed attempt for `d7d87c81…` remains local; after correcting missing-call-ID semantics, the affected final candidate was verified again. No full-project suite or parallel monitoring framework was added.

## Boundaries and handoff rationale

minimum_work_unit_output:

- work_performed_or_requested: Complete Human-approved Codex G1 -> G2 -> G3 on the existing isolated Codex branch, without importing DeepSeek implementation or changing Workflow.
- implementation_or_review_method: Parse explicit native event fields; match only actual call IDs; manually watch real new native events and stop via terminal Ctrl+C; run focused tests and exact-candidate managed replay verification.
- supportability_rationale: The historical sample demonstrates real commands, results and durations while unchanged source hashes constrain the read-only claim. Live source-offset checks and process termination establish this bounded ON/OFF result. These are executor measurements, not independent acceptance.
- feasibility_rationale: Python standard library and readable Codex JSONL provide all required inputs; no Codex binary modification, log database, filesystem scanner, external service or future collector is required.
- exact_result_or_candidate_ref: 475a2245aa9a8b422c2c0edfcb3dbd123c518dea
- verification_evidence: The exact local managed attempt, actual replay/watch outputs and native session named above.
- residual_risk_or_unproved_limits: Native logs may omit calls/results or use a future unsupported event format. The monitor cannot reconstruct missing events, attribute business Done or prevent source-side log loss. Report excerpts are truncated; full observed values remain in events.jsonl. Outputs are not automatically redacted. A stopped monitor is OFF; it does not disable Codex's own logging. Independent review and Human master integration remain separate.
