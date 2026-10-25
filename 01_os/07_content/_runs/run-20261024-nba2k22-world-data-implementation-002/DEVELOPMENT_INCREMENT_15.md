# Increment 15 — actual native player vitals, injury/fatigue and morale

Full goal remains active and incomplete. Candidate `7bf3225009ee30879dc86446402776ef054b1a9b` implements **Schema v14 / 83 STRICT tables / 1,207 columns**. The three existing typed family tables now retain both qualified current canonical players and native source-only subjects; no EAV/JSON fact table replaces their columns.

## Native evidence and interpretation

A metadata-only acquisition verified PLAYERDATA, APPEARANCEDATA and SCHEDULEDATE structure headers plus seven enums: injury154, injury-status5, position6, best-hand2, best-dunk-hand3, morale-event25 and organizational-role7. Literal local PE names and primitive type CRCs identify float32 Weight/Morale_Private and signed-byte MoraleEventAdjustment. Current complete field signatures and name-array dimensions are checked in the operational reader. This metadata phase reads no PLAYER values.

PLAYERDATA.Appearance at +144 is a pointer to a separate64-byte APPEARANCEDATA object. Its first four public bytes hold 15-bit HeightInTenthsOfMM and WingspanInTenthsOfMM. Source raw values are retained, with cm values explicitly derived by /100 from these named native units. Only four target bytes are read/rechecked; cosmetics/full appearance data are not acquired. Null/invalid pointers yield unavailable measurements rather than invented zeros, and a target alias into the PLAYER pool is rejected as a measurement source.

The11 vitals fields cover native float weight, raw birth year/month/day, three position codes, handedness/dunk hand, jersey code and years pro. Unlocalized first/last names are separately observed through current uint16[20] metadata. Weight retains its exact word, finite real and hex/nonfinite diagnostic without asserting a UI weight unit. Birth date/age, display conventions, college/country remain unasserted rather than derived from incomplete calendar rules.

The23 health fields retain both injury slots, original injury types, exact native injury/status enum labels, healed percentages, start/healed date words, duration-minute words, side/latest-slot flags, injury-history flags, ProgressiveFatigue and WearAndTear. ProgressiveFatigue is the specific source for fatigue_raw. Native status enums include HEALTHY/PROBABLE/QUESTIONABLE/DOUBTFUL/OUT; mixed slots are preserved without deriving a single aggregate availability/severity. Duration is not remaining recovery time. Energy and recovery_days remain NULL without separate evidence.

The four native morale fields retain float32 Morale_Private, event code/label, s8 event adjustment and organizational role. Both unsigned adjustment bits and the exact signed conversion are available. OrgRole's enum is EXPENDABLE/DISCARD/CAPSPACE/PROSPECT/TENURED/CORE/FOUNDATION. It is not substituted for playing-time role, role satisfaction or external model behavior. Legacy morale_raw/role_code/role_satisfaction_raw are left unasserted by this source. Morale_Private is the C++ encapsulated field name; known hidden Potential values are still physically excluded.

## Actual source, database and queries

`capture-player-state PID SAVE_DIRECTORY LOADED_FILENAME NEW_OUTPUT_DIRECTORY` uses a shared narrow player-pool projector, current metadata validation, complete reciprocal core-roster controls and private-interval checks. It does not reacquire full badge/contract families. The target remains Human-bound `nba2k22_test_01 / MyLEAGUE0003`, actual PID2132; every native operation requests only0x1010 read/query access.

Actual unit `player-state:0cdec9c404bf1ced7f0af1f8` ingested **3,390** subjects and **3,390** snapshots in each of vitals/health/morale, plus40 native field bindings. All **3,390** appearance measurement sources were observed and rechecked. **461** current core-roster subjects matched existing canonical identities through the established qualified rule; other pool subjects remain separate native sources. These observations do not certify cross-session/historical identity lifecycle.

Same-unit source/canonical guards cover all three families, and source-parent ordering now precedes every dependent typed family in DDL/ingest/copy migration. `native-player-state` supports source/name filters and pinned source-index pages. Player cards expose actual per-field observation age; the later state acquisition leaves prior attributes and base badges unchanged. Missing appearance and unknown enum/float cases remain explicit.

Copy migration v13 -> v14 compared **795,710** old rows by all prior columns, retaining the old file hash `00ff3f63ee0a646f7242b8679c3a9ab81cfa00859a79e0fb16a1bf1811e93396`. No old snapshot is rewritten or relabeled. The old v13 file and binding declaration remain available alongside v14.

## Verification and limits

The actual audit verifies every public read chunk, pointer association and four-byte target hash, redecodes all3,390 state projections, checks all requested addresses against known private intervals and compares **13,604** typed records. It validates SQL integrity/FKs, **34 complete pages** covering all3,390 sources, safe role outputs and full three-family exports. No aggregate health/energy/recovery, birth date/age/country/college or generic playing-role/morale value is invented. Old attribute observations and all prior base badge rows remain unchanged.

Development suite passes **105 tests**. Added cases cover exact float/nonfinite storage, signed adjustment, named measurement conversion, absent appearance, dual/unknown injury status, no fabricated availability/energy/recovery/playing-role data, physical private-interval independence, source-only/current matched queries, cross-unit rollback and incomplete-family rejection. Thirteen explicit research replay database examples are retained, including the prior full base-badge example compressed; fixture replay remains RESEARCH_FIXTURE.

Artifacts under `06_执行/increment15/` retain the real v14 SQLite archive (**55,746,936 compressed bytes**), metadata/source investigation and live capture archives, exact scripts, source/binding hashes, migration proof, current queries/exports and final candidate validation. No failure exhausted the three-attempt budget. Remaining native vitals/calendar/UI scales, aggregate health/energy/recovery, playing-time satisfaction, lifecycle identity, other domains/role coverage, capacity/recovery, managed full-candidate verification and independent/Human acceptance remain open. No Q10 exception, game/save write, date advance, Antigravity dispatch or master integration is claimed.
