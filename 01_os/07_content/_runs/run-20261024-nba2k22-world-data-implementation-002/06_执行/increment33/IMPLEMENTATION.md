# Increment33: Native staff-history storage roles and position queries

Candidate code: `d118dd8edaa683f792acfe8bf3e9d283de82d42a`.

Previous turn classification: PROGRESS. Increment32 published the full annual
staff reference/stat source, v23 schema and real database. This increment traces
its unresolved storage semantics and adds consumer-facing code-derived results
without resampling the annual source or changing stored facts.

Native0xeafda0 passes position0 to the verified stat getter0xeaf930, adds the
requested delta, and tail-calls setter0xeafaa0. The setter reads/writes the
reference at COACHDATA+0x88 and stores selected scalar members. Bounded game
result callers pass the CoachWins/CoachLosses/CoachPlayoffWins/CoachPlayoffLosses
column selectors with a delta of1. This establishes a mechanical increment
target, not a calendar-year or finalized-season label.

The setter's allocation path uses the Slot20 manager at offsets0x140/0x148,
reads FirstFree, removes that node from the list by advancing FirstFree to
NextFree, and writes NextFree=65535. Clear routine0xeaf580 checks that marker
before reinserting a node. The current Native COACHSTATMANAGERDATA schema has a
2-byte FirstFree; COACHSTATDATA has the independently verified2-byte NextFree.
The clear loop starts at COACHDATA+0x88 and iterates39 positions,0..38. The
untouched position39 is not proved to be career totals. That initial hypothesis
is withheld. No historical year/phase/ownership or free-list reachability is
inferred from these paths.

staff_history_semantics_native_profile.json retains9 exact code windows totaling
1288 bytes. The code-only verifier compares those bytes through a fresh actual
ReadOnlyGameProcess and never invokes a getter or mutator. Native metadata for
the stat and manager types is also reverified. Runtime proof uses the supported
PE timestamp1652287197, gamePID11668/creation FILETIME134374763743810259, stable
Native Today2021-11-20 and season-year2022. Connection checks read their normal
small game-mode/season controls; no annual staff/reference/stat values are read.
WorkerPID2740 is independently confirmed absent after its terminal report.

`staff-history DB --reference-position N` selects a single stored reference per
returned source subject, including missing and rejected references. It retains
pinned-unit pagination, staff/name/index filters and acquisition cutoffs. The
default still returns all40 references. Each row adds storage_roles with an
explicit CODE_DERIVED basis: position0 increment target, whether the clear loop
visits that position, and whether the observed NextFree matches the Native
allocation marker. Unsupported source decoders withhold these annotations.
A position role is not proof that a missing reference has a record; missing
values retain NOT_OBSERVED marker status. No raw column, NULL stat_year, original
observation time or source identity is rewritten.

All265 tests and SQLite smoke pass at the candidate. Four new tests cover
position0/clear-loop/last-position roles, marker and unsupported-decoder behavior,
exact Native code rejection on byte changes, filtering/CLI/cutoffs and original
row preservation. Native verification is separate from fixture success.

Actual queries compared1470 subjects, all58800 raw reference rows and217 resolved
records with the stored source. All217 NextFree words match the Native marker;
58583 missing/rejected links retain NOT_OBSERVED. Position0 has30 resolved
references; other resolved references span positions1..24 in this sample. This
distribution is observation, not a year mapping or an allowed-history-length
limit. Single-position queries at0/1/38/39 and the actual CLI cutoff path pass.

The schema staysv23:99 tables/1756 columns,1464967 rows and40 successful units.
The database SHA256 remains exactly
`c243f31c3f5f1525800691e9b1ed12f1ebf001cad682b4870b0950a2058033b1`.
The existing full snapshot remains in increment32. No new annual capture, game
write, getter/mutator invocation, date advance, Computer Use, capacity work,
master integration or independent acceptance occurs. Full world-data development
remains active with the calendar/phase and remaining domain-source gaps open.
