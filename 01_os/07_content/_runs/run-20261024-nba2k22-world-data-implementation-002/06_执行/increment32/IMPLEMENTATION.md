# Increment32: annual Native staff history

Candidate code: `9db85720f4c00587c296eacae0c035018104f22b`.

The ordinary staff reader intentionally omits COACHDATA.SeasonStats. This new
annual source fills that acquisition/query gap without importing historical
references on every ordinary refresh. The Human's latest Computer Use stop is
recorded in the durable work order; no Computer Use is used in this increment.

Current Native COACHSTATDATA has12 bytes and7 fields: NextFree uint16,
CoachWins/CoachLosses/CoachPlayoffWins/CoachPlayoffLosses uint16, and
CoachWonTitle/CoachWonCoachOfTheYear uint8. Current COACHDATA.SeasonStats is a
40-element signed16 array at136, with extent40 and stride2. Native consumer
0xeaf930 independently rejects negative references and references outside the
current bank count. Native bank getter0xf3c3a0 establishes descriptor offsets
0x150/0x158, Slot21 and stride12. Getter code is verified as bytes and never
invoked. Index0 can resolve, including after earlier negative references; no
player-specific sentinel or stop-after-empty-slot rule is imported.

The COACHSTATMANAGERDATA metadata separately describes a2-byte FirstFree. Its
free-list lifecycle has not been proved and is not used to declare allocation.
ROSTERDATA_COLDEF was inspected as a candidate lookup enum; its current literals
describe identity/audio/lookup columns, not roster descriptor slots. It is not
used as evidence for Slot21. The actual getter establishes that bank location.

Schema v23 adds3 STRICT tables and27 columns, totaling99 tables/1756 columns:
native_staff_history_subjects, native_coach_stat_observations and
native_staff_stat_links. Annual source subjects preserve the entire bounded
staff descriptor identity projection; every subject retains all40 signed
references, including rejected ones. Distinct referenced rows store all7 fields.
Cross-unit subject/stat references and mismatched bank indices are rejected by
SQL. Adapter completeness checks reject omitted/duplicate subjects, references,
stat rows, wrong shared-reference counts or invented statistical years.

The row has no year member. stat_year stays NULL; no chronological/current
position, phase, team, finalization or canonical award event is inferred. The
annual capture-run season-year only controls refresh cadence. Shared bank rows
retain their distinct source-subject count, and canonical subject aliases require
a globally unique current pool UID and exact existing name; lifecycle stays
unproved. Native flag bytes retain0..255 storage without a UI boolean claim.

`refresh-world auto ... --families staff-history` resolves the current process
and the fourth annual family STAFF_SEASON_HISTORY. Same-year prior success is
checked before any staff/reference/stat value read. Other annual buckets and
ordinary staff source behavior remain unchanged. `staff-history DB` supports
staff ID, exact name, source index, pinned-unit paging,1..50 subject pages and
observation cutoffs. Each result includes all40 links and joined typed fields.
Staff cards include this independently timed source. Privacy projection reads
only staff[48,128) and[136,218); no PLAYER value or staff growth/max-grade byte
is acquired.

261 tests and SQLite smoke pass at the candidate. An initial full-suite failure
was the old96-table test expectation; the expectation was updated to99 and the
full suite passed. New tests cover signed boundaries/zero/after-negative links,
privacy projections/control changes, full raw flags and unknown years, duplicate
UID alias withholding, family completeness, queries/paging/cutoffs/CLI, immutable
history, cross-unit rollback and same-year no-read skips. This development
verification does not establish complete-system independent acceptance.

Actual acquisition and copy-upgrade evidence are recorded in the adjacent
worker/actual reports and portable snapshot. v22 and all prior factual columns
are compared/retained; saves.schema_version changes only in the new v23 copy.

Actual source: `native-staff-history:bbfad4dcf2acda8b0c224761`, gamePID11668 /
creation FILETIME134374763743810259, Native Today2021-11-20 and season-year2022.
The capture contains1470 source staff subjects,58800 independent signed links
and217 distinct referenced coach-stat rows. All217 accepted links resolve to
separate rows in this sample;58583 references are negative and retained without
stat links. All2940 UID/name comparisons,58800 signed-reference comparisons,
1519 scalar comparisons,5880 repeated public projection interval checks and1691
registered artifact hashes pass.240 current unique-ID/exact-name subjects link
to existing staff identities. No subject-sharing occurs in this particular
source, while fixture coverage retains the shared-reference case.

Every prior factual column across96 tables/1402757 rows is equal after upgrade
(apart from saves.schema_version in the copied header). The three preexisting
annual families remain exact. A second actual same-year staff-history call
returns ANNUAL_ALREADY_REFRESHED, reads no staff/reference/stat values, and keeps
the database SHA unchanged. Full source-unit pagination visits all1470 subjects;
the before-source observation cutoff returns NOT_OBSERVED. Actual workerPID1948
was confirmed absent after its terminal report.

The new local fact file is world-v23.sqlite:1464967 rows,40 successful units,
SHA256`c243f31c3f5f1525800691e9b1ed12f1ebf001cad682b4870b0950a2058033b1`.
The full gzip snapshot is retained in four bounded parts with stream/part/file
hashes; the Native source/metadata/code archive is retained beside it. This is
functional integrity/snapshot evidence, not a full-season capacity evaluation.

No game/save write, getter invocation, date advancement, capacity work, master
merge or independent acceptance is performed. Full world-data development remains active.
