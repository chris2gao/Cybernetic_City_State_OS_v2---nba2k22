# NBA2K22 historical integration — source-only candidate

**Task ID:** `OS-NBA2K22-HISTORICAL-BRANCH-INTEGRATION-20261103-001`

**Authority:** Human latest 2026-11-03 ruling: source-only mainline integration, offline-local historical snapshot retention. The original full Host merge instruction has been superseded.

- NBA master fixed baseline: `45cc45cae0550ddcda192a2179ea48509b27f6ee`.
- Original Host provenance (NOT a parent in this branch): `1fc2965ae10ef2a34abb37d800d86cd548f24aeb`.
- Integration branch: `integration/nba2k22-source-only-mainline-20261103`.
- Original full-history staging branch / PR #25 remains untouched by this branch. Do NOT merge PR #25.
- Selectively imported **1,978 original source files** (~53,651,720 raw blob bytes), no modified Host-only files copied over master.
- **11** master-version differences kept the current master blob. All original master paths preserved. Only original shared `.gitignore` updated with local-only archive patterns.
- **234** new Host-only large/raw artifacts excluded from candidate (~2,007,813,667 raw bytes): 126 SQLite database/backup/partition files and 108 raw/bulk capture files. These are not deleted from the original Host commit/history.
- Existing three tiny master `.db` research samples retained (221,184 bytes total); **four** `.sql` sources retained.
- Included WorldData v24 SQL/schema/readers, Native higher-order stats, Calendar G1/G2, G2/S0, deterministic REA Bulk, Decision Outbox and SeasonCycleHost files, plus test infrastructure, docs and small fixtures. Exact source list and SHA1 blob IDs: `06_执行/included_source_file_inventory.json`.
- Full excluded path and size/source blob inventory: `06_执行/local_only_artifact_inventory.json`.
- Local SHA256 archive process and recovery: `06_执行/archive_local_artifacts.py`. **Actual local copying and SHA256 receipt are NOT_EXECUTED until access to user's full offline clone.**
- Existing work/product historical test receipts are preserved as originally recorded. This integration does NOT claim new full legacy tests, gameplay validation or fresh independent audit.
- Remote history slimming requires **separate approval**, described in `06_执行/github_history_slimming_plan.md`.
- No NBA master merge is performed by writing this candidate. PR and final SHA must be read back from GitHub.

**Conclusion:** `CANDIDATE_SOURCE_ONLY_INTEGRATION_PREPARED`; local offline archive `PENDING_LOCAL_EXECUTION`; remote old-ref rewriting `NOT_AUTHORIZED`. This is an integration status, not a retroactive OS lifecycle upgrade for prior development runs.
