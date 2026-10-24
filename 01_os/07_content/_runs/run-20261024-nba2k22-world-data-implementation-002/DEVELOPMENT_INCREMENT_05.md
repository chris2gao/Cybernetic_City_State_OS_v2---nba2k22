# Increment 05 — complete observed schedule and completed-game player context

Goal remains **active and incomplete**. Implementation candidate: `babfcff3`. Schema v4 still has **62 STRICT tables and 659 columns**. No master integration, independent review or whole-system acceptance is claimed.

## Implemented data flow

`capture-season PID SAVE_DIRECTORY LOADED_FILENAME NEW_OUTPUT` acquires the actual Slot10 count (bounded by the known SEASON capacity), every 32-byte index row, every 60-byte SEASON record and both-team Box for every final game. It rejects invalid/duplicate game identities, invalid participant windows, nonconserving Boxes and changing source windows. Every index entry is correlated to the SEASON date bits and both current TEAM pointers. A fresh player-context pass resolves the union of final-game participant IDs; the complete schedule is reacquired around it to reject mixed observations. Acquisition uses read/query process rights only and skips the Potential byte.

`schedule DB [--season-id ID] [--status-code 0|1|2] [--limit N]` returns latest observed state, team names and derived Box scores only when canonical rows cover all native in-use participants on both sides. Future/unplayed games get no artificial zero scores or Boxes. The limit rejects truncated output. Calendar/UI encoding remains unverified, so canonical dates remain NULL.

## Actual source and database coverage

The descriptor has **1,232 records: 238 final and 994 scheduled**. All 1,232 date-bit correlations and both team-pointer correlations passed. Both sides of all 238 final-game Boxes conserve period/OT source totals. These prove this observed window; they do not prove a future season/layout or UI calendar semantics.

The final source batch has **411 resolved players, 369 current season totals, 6,133 canonical player Boxes, 6,170 typed native Box rows, 1,904 regulation-period rows and 476 native team Box fragments**. Public player families include 54 attributes, 48 named tendencies, 17 contract fields and four ordered PlayTypes per resolved player. Missing current totals remain absent.

Four Native IDs remain unresolved: **1344, 2382, 9808, 18057**. Their source rows remain staged; no name-based or approximate merge is used. Consequently, 202 of 238 finals have complete canonical player coverage; 36 do not. Query suppresses derived scores for incomplete games. This is an explicit source/identity gap, not a Human Q10 exception or implicit acceptance.

## Evidence-driven corrections

The first bulk capture stopped before ingestion on an invalid UTF16 decoding error. The next pass safely rejected undecodable candidates and ingested 349 players. Byte inspection showed valid names (e.g. Chris Paul, JaVale McGee) followed by uninitialized bytes after the UTF16 NUL. The final decoder trims at aligned NUL code units before decoding, while still rejecting invalid prefixes. This recovered 62 genuine player mappings; no replacement characters or guessed names were substituted. All attempts/evidence are retained.

Schema v4 corrects final-history comparison: only prior final observations define frozen final values. Scheduled/in-progress observations no longer block valid final progression or consistent repeat final acquisition. Conflicting finals still reject. A regression covers scheduled -> in-progress -> final -> repeat final -> conflicting final rejection.

`upgrade-save` copied v3 facts into a new v4 file, retained the original DB/declaration and switched the small engineering binding pointer. The offline audit compared **all 1,467 old rows** to their corresponding new rows; every old value is preserved. No native save file was edited.

## Verification and process restart

The development check passed **45 tests in 17.927 seconds**, with fixture/SQL/query/privacy artifacts retained separately from actual live evidence. The bound-season audit rechecked source hashes, actual read trace/addresses, excluded-byte intervals, every final Box/score, index identities, FK/integrity, latest query counts, missing-score behavior and old-history preservation. Public query/export contains no Potential, owner source path or raw pointer fields. Full observed player Box history export has 11,455 rows, including prior batches.

Human reported NBA2K22 restart after the PID2564 captures had completed. Fresh process lookup found **PID8784**. A new read-only worker reacquired module/root/descriptors and a bounded first-game Box/player control; score conservation passed. It did not ingest new facts or reuse PID2564 as an active handle. Prior captures remain historical observations under the unchanged `nba2k22_test_01 -> MyLEAGUE0003` binding.

Artifacts: `06_执行/increment05/`: exact compressed v4 DB snapshot, archived source attempts, binding, source hashes, full schedule/final queries, player history export, executed audit script and development verification logs. The source process for the full schedule is PID2564; the post-restart probe is separately archived.

Remaining: four player identity gaps, current player lifecycle, calendar/badge/contract semantics, staff/coaching/training, finance/market/draft/G League, settings/rules and actual honors/records/news; then capacity/recovery/role coverage, completed-candidate verification and independent/Human acceptance. Codex continues as Owner; optional Gemini batch research uses Human relay only.
