# Increment 18 — actual fact backup and verified recovery

Full goal remains active and incomplete. Code candidate `d372d86da0cfd52a7eb4a51196efc285d0b43c46` adds owner backup/recovery and explicit storage-inspection tools. Physical schema stays **v16 / 84 STRICT tables / 1,306 columns**.

## Current Human capacity direction

Human clarified that current test data covers about one month. **Capacity stress and storage optimization are deferred until actual complete-season coverage exists.** After that, measure real seasonal growth, estimate longer storage and let Human determine the retention horizon if100 years is not feasible. A full unplayed schedule is not a full season of completed/history data. No shorter horizon, pruning or deletion is authorized. Canonical policy is `world_data_prototype/CAPACITY_AND_RETENTION_POLICY.md`; exact Human statement is retained in `human_capacity_cadence_20261025.md`.

Page-allocation measurements and simple fixed-population models completed before this clarification are retained under `early_capacity_observations/` only for traceability. They are **not a representative seasonal baseline, a100-season execution result, a resource-budget verdict or retention-decision evidence**. No capacity/A-B job remains running. Other engineering continues.

## Runnable recovery operations

`backup-facts DB NEW_DIRECTORY` uses the standard SQLite online backup API with a read-only source connection. It preserves the committed database snapshot, including committed WAL content. A complete manifest is published only after the database's file hash, save/schema header, full schema fingerprint, every table's ordered row digest, SQL integrity and all FKs are validated. Incomplete copies have no complete manifest and are rejected by recovery. Completed database/manifest files are fsynced; no real power-failure/directory-fsync claim is made.

`restore-facts BACKUP_DIRECTORY NEW_DATABASE --expected-save-id SAVE_ID` verifies the manifest and snapshot before writing, creates a new file exclusively and verifies its full hash/inventory again. An existing database is never overwritten, and `save.json` is never rebound. This is recovery of the same save-local fact database, not a game save, new world branch or proof of current live-game alignment. Original source ledgers/hashes are preserved. External raw evidence files remain separately retained owner artifacts, and are explicitly not bundled/restored by this command.

`storage-profile DB` reports rows, page allocation, sidecars, latest source-unit row counts and recorded artifact sizes. Missing optional dbstat is explicit UNKNOWN for per-table bytes. Primary Python3.14.6 has no dbstat; the available bundled Python3.12.14/SQLite3.53.1 supports it. This runtime difference is retained in the exploratory evidence; no global interpreter/configuration change was made. The pure projection helper remains an explicitly labeled planning model, not an activated job or a pass verdict.

## Actual database verification

The Human-bound `nba2k22_test_01` v16 database was **555,216,896 bytes**. Actual backup/recovery verified all **84 tables and843,987 total rows**, including owner ledgers and zero-row tables. Every original row/schema fingerprint matches the completed snapshot. Backup took **35.095 seconds**, and new-file recovery including complete validation took **54.070 seconds** on the observed host. These are current-size measurements, not extrapolated long-history latency.

Seven public result families match before/after recovery: player card, complete native skills, contracts/base badges, vitals/health/morale, affiliation/college, team card and game Box. Original database SHA256 remains `466d3eeaf7bda194cdba7f26f6013227a9c2a569084ee450a665792746135932`; the active binding is unchanged. The verified snapshot has SHA256 `d903066148c1fc145d7323a4eb32d0f349a8f0c31fddce42269cfd05529d1f4f` and a **58,275,615-byte** compressed evidence archive.

The complete unit suite passes **127 tests**, plus SQLite smoke. Eight dedicated operation cases cover full round trip, wrong-save refusal, corrupted bytes, incomplete/altered manifests, no overwrite, committed/uncommitted WAL separation, interrupted copy and measurement/model distinction. Those eight also pass with the bundled dbstat-capable runtime. No blocking failure exhausted three repair attempts.

Current-size query timings are retained separately as one fixed-order run with uncontrolled OS/SQLite caches; they are not long-history query performance evidence. No game process, original game save, date advancement, source-history rewrite, automatic retention mechanism, Antigravity dispatch or master integration was used.

## Evidence and remaining work

`06_执行/increment18/` contains the backup manifest, compressed verified facts snapshot, actual recovery receipt, complete logical inventory, query equality/timing evidence, test/smoke logs, source/commit hash checks, scripts and Human capacity-policy pointer. To reconstruct the backup component from the evidence archive, decompress `verified-fact-backup.sqlite.gz` as `facts.sqlite` in a new directory and put `backup_manifest.json` there as `manifest.json`; the normal recovery validator then checks it. Ordinary backups produced by the CLI already have that ready-to-use directory layout.

Continue Native/UI source gaps and usable ingest/query/history. Full-season collection precedes renewed capacity evaluation and a Human retention decision. Cross-session identity, final managed verification and independent/Human acceptance remain open. No Q10 exception or full-goal completion is claimed.
