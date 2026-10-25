# Increment 26 — Native game-mode stages and the shared stat selector

Exact tested/executed candidate: **`3057547feaec7d4dbc73588a26b4513d40a76681`**. Schema is **v19 /87 STRICT tables /1,404 columns**. This increment delivers a new real Native source, typed observation and usable public query. Full-system Native/UI/lifecycle coverage and independent/Human acceptance remain open.

## Native evidence and corrected inference boundary

The Native `GAMEMODE_TIMEPERIOD` enum has31 named values, including NONE, START_OFFSEASON, lottery tournament, retirement/Hall-of-Fame/jersey retirement, league meetings, relocation/realignment, lottery/staff signing/keepers/scouting, combine/workouts/protection/expansion/draft/signing, contract options/qualifying offers/free agency/progression, summer league, All-Star city selection, Hoops Summit/reward camps, preseason, regular season and playoffs. Exact literal CRCs, current enum tables and type initializers are matched. GAMEMODE Mode and League have their own7-value/3-value enums. These are Native labels; actual UI stages and transitions are separate.

The previously ambiguous current-stat selector is now tied to the actual virtual getter. Its current implementation reads the GAMEMODE pointer at RVA0x632b470 and returns the word at+12, which named metadata binds to GAMEMODE.Period and the31-value enum. The selector returns the special branch for codes **2,24,26,28,30**: LOTTERY_TOURNAMENT, SUMMER_LEAGUE, HOOPS_SUMMIT, PRESEASON and PLAYOFFS. The named `PlayerStatData_AddCurrentTimePeriodStat` call path converts this branch to the argument of `PlayerStatData_GetOrCreate`, which selects array position24 for the special current-period lane and position0 for the ordinary current-year lane. Four bounded code windows total **800 bytes** and are matched again before production acquisition. No method is invoked.

Position24 is therefore shared across several periods. It cannot be labeled uniquely as postseason, and a current GAMEMODE period cannot retroactively label previously accumulated records. Historical/current cumulative `phase_code` remains NULL. This is a concrete counterexample to inferring a stat phase from a slot number or the separate `SEASON_TIMEPERIOD` enum.

## Implemented source and database behavior

`game_mode_reader.py` verifies six current metadata types, primitive/nested bindings, date epoch code, selector/call-path code and the actual virtual period getter. It captures only the24-byte public GAMEMODE prefix and repeats its direct pointer, object/vtable/getter and prefix controls. Current Native game-season year is separately read and rechecked. It stores team counts, current/draft raw year bytes, Native mode/league/current/previous period, named Today date components and qualified current-stat array selection. CurrentYear/DraftYear bytes receive no generalized absolute-year interpretation. Unknown enum codes retain raw values/NULL labels and the exact Native default-zero selection.

Schema v19 adds `game_mode_observations` with28 typed columns, PK/FKs, one-row-per-unit uniqueness, append-only behavior, visibility rules and matching generated DDL/dictionary/table cards. `capture-game-mode` acquires and ingests a bound LIVE_READ unit. `game-mode DB [--season-id ID] [--limit 20] [--as-of TIMESTAMP]` returns the latest qualified observation per season using UTC source recency and acquisition cutoffs. The explicit serial `refresh-world` now has14 source families, with ordinary `game-mode` after schedule identity acquisition. No scheduler or game action is added.

## Actual dedicated-save execution

Fresh process controls identify PID8648 and the same creation/build/year epoch before and after acquisition. `nba2k22_test_01 / MyLEAGUE0003` keeps its Human-declared file identity; only the fact-file pointer changes from world-v18.sqlite to world-v19.sqlite. The Native game save is not written.

The actual row is **Mode FRANCHISE /League NBA /Period29 REGULARSEASON /PreviousPeriod NONE**, with current/draft raw year bytes both0 and current-stat array position0. All21 independently checked prefix/enum/date/selector values agree with raw bytes. All source artifacts are hash verified and no PLAYER or protected player interval is read. Other named game-mode periods are proven enum metadata and exercised by fixtures, not claimed as observed transitions.

All **1,374,390** prior rows in86 tables are equal by every old column except the required `saves.schema_version`18-to19 header. The old v18 hash remains `46eec932562bb5b722c490bb71011b4d21db87a4f86d1be742ba5435ea87514d`. New v19 contains **1,374,426 physical rows /34 successful source units**, SHA256 **`d7296d67dcb7c1896a1e3ec242650769c2f84f848dec46049824d89a5395a117`**. Row deltas include new schema visibility rules and the one source unit, not game advancement. Full SQLite and Native evidence are retained as ordered gzip parts with decompression/hash checks. This is ordinary delivery packaging; capacity work remains deferred.

## Two differently named Native date fields

The new GAMEMODE.Today is2021-11-20 00:00. A further small paired read in one rechecked process instance confirms that SEASON.Date is simultaneously2021-11-19 22:00. Their raw period codes are29 and2 respectively, both named REGULARSEASON in their distinct enums. The fresh SEASON.Date word matches the older stored calendar word; the new field was not a reason to rewrite or relabel that prior observation. Sixteen independent raw date-component comparisons are retained with the paired report. The difference is evidence about two named fields, not proof of a fixed offset, UI display convention, game advancement or timezone. Queries keep their own field identity and source time.

## Verification and remaining limits

**206 tests and SQLite smoke pass** at the exact candidate. Nine new tests cover all31 period codes and the five shared-selector cases, the separate meaning of period code2, unknown codes and raw year bytes, invalid dates, stable/changed object and virtual getter controls, changed-code rejection, immutable typed ingestion/idempotency/UTC recency/cutoffs, and CLI/source-grade/cap validation. Existing registered-adapter/table-count assertions are updated for the added source/table. OS preflight, MWU, committed-code hashes, complete archives, save declarations and actual worker-process absence are checked before publication.

No issue exhausted the three-attempt budget. There was no game/save write, getter invocation, date advancement, annual history refresh, scheduler, Core change, Antigravity dispatch or master integration. Raw year semantics, exact cumulative phase/allocation, observed future stage transitions, UI semantics and identity lifecycle remain separate gaps. Full-season capacity and final independent/Human acceptance remain outstanding.
