# Increment34: ordinary Native coach win/loss observations

Candidate code: `27f2f17a9a9887c18315ac78e4d9a7289d729a23`.

Previous goal turn classification: PROGRESS. Increment33 verified the Native
position0 read/add/write target and storage markers. This increment uses that
proof to acquire ordinary current-counter observations without resampling all
annual history or importing annual awards during later ordinary refreshes.

Schema v24 adds native_current_coach_stat_observations: one row per current
COACHDATA source slot, with native UID/name, optional existing canonical staff
alias, signed position0 reference, link status, optional bank index/shared-source
count, NextFree/marker status, NULL stat_year and four uint16 win/loss counters.
The total is100 STRICT tables and1775 columns. Missing/outside/negative links
retain NULL values; SQL rejects partial resolved rows, mismatched indices or
invented statistical years. Shared records retain their subject reference count.
No current job/hiring/lifecycle or historical ownership is inferred.

The ordinary source projects staff[48,128),[136,138) and[216,218): names, exactly
one signed reference and UID. It excludes all other39 reference positions and
staff growth/max-grade bytes. Distinct referenced stat rows are projected only
over[0,10), retaining NextFree and CoachWins/CoachLosses/CoachPlayoffWins/
CoachPlayoffLosses. Native title and coach-of-year bytes[10,12) are physically
unrequested and absent from the new table, payload and query. Full stat metadata
and code can be checked without acquiring those annual values. No PLAYER value
is read. All selected values, descriptors, root, mode/date and code/metadata
bindings are checked with fresh current-process addresses.

`refresh-world auto ... --families coach-stats` is the twentieth registered
source and an ordinary family with no annual bucket. Default world refresh now
includes it after staff acquisition. Original staff and annual history readers
remain independently timed sources. `coach-stats DB` defaults to resolved
references and supports staff ID, exact name, source index, all sources, pinned
unit pagination,1..100 row pages and acquisition cutoffs. Staff cards include
native_increment_stats separately from native_history. Native observation season
and mode/stage do not silently label the counter's calendar year or phase.

All273 tests and SQLite smoke pass at the exact candidate. Eight new tests
exercise physical exclusions, exact10-byte decoding, shared/missing records,
duplicate UID alias withholding, mid-capture changes, incomplete/annual-field
injection rejection, two same-year changing-value observations and cutoffs,
queries/CLI, SQL rollback and observed-empty sources. Fixture values demonstrate
changed counters across observation dates; later-month Native game progression
was not induced.

Actual copy-upgrade and two Native captures are recorded in worker-result.json.
They retain separate observed_at/unit IDs and preserve the four annual buckets.
The adjacent actual report compares all prior99 tables/1464967 rows against the
retained v23 file, all raw names/UID/references/counters, actual privacy/annual
exclusion intervals and artifact hashes. The full v24 snapshot and Native source
archive are retained for owner verification. The actual game was not advanced.

Actual units are native-current-coach:3fbb2144f1ef34529cf6720a and
native-current-coach:8f256bfd653ddfb7e7182e60. Each captures1470 staff sources,
30 resolved position0 subjects and30 distinct10-byte stat projections. The
second observation is a separate successful ordinary unit in the same Native
season-year2022; refresh_family/refresh_period_year remain NULL for both.
The process was freshly discovered as PID11668 / creation FILETIME
134374763743810259, with Native Today2021-11-20. WorkerPID9236 was independently
confirmed absent after its terminal report.

Actual comparisons pass for5880 UID/name values,2940 signed references,
300 counters/NextFree words,17640 repeated staff projection intervals,
120 award-free stat intervals and3018 registered artifact hashes. All prior
factual columns across99 tables/1464967 rows remain equal apart from the copied
saves.schema_version header. All four existing annual buckets remain exact.
Latest resolved querying returns30 subjects, full pinned paging visits1470,
and the first-observation cutoff returns the first unit after the second exists.

The current local file is world-v24.sqlite with1470952 rows and42 successful
units. SHA256 is
`f76b943e4c716748b4df1c8f6c94779fb57ebb312bbeeb9e4d4dfd97a024b218`.
The retained v23 baseline remains SHA256
`c243f31c3f5f1525800691e9b1ed12f1ebf001cad682b4870b0950a2058033b1`.
The full snapshot's bounded parts, compressed stream and decompressed database
hash are verified. This is functional integrity evidence, not capacity work.

No game/save write, getter/mutator invocation, Computer Use, capacity evaluation,
master integration or independent acceptance occurs. Year/phase/team/ownership
semantics and remaining world-data source gaps remain open; the full goal stays active.
