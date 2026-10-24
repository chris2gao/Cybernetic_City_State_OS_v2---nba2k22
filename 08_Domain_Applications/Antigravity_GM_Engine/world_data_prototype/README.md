# NBA2K22 per-save world database — full-system development

Task: `nba2k22-world-data-full-implementation-01`. This is an **in-progress engineering candidate**: executable all-domain structure, historical adapters and an operator-bound live game/player adapter; full live-source coverage, whole-system acceptance and independent review are outstanding.

## Implemented structure

**Schema v7: 74 STRICT SQLite tables, 936 columns**. The 59-table approved provisional catalog is implemented with explicit game/finalization/source observations, team state, draft/prospect/waived state and stored opponent-plan/training/mentor source observations. Staging preserves real captured stats when canonical identity is not proven. The original 16 table names and observations are preserved. See [table cards](TABLE_CARDS.md), [complete field dictionary](field_dictionary.json), executable [DDL](schema.sql) and its [catalog generator](schema_model.py).

The database covers player/team/staff identities, typed attributes and named tendencies, vitals/contract/health/morale/training, badges/play types, schedule/period scores/Box/season totals, coaching/tactics/mentors, finances/market/draft, actual settings/rules, awards/records/news, native source governance, external transaction/readback contracts and season closure. **Having a typed table does not establish the Native source for its columns.** UNKNOWN ranges and source gaps remain explicit. Contract offset 833 aliases and badge tier encoding are not silently decoded.

One independent game save has one immutable fact-file identity. No cross-save ancestry or relation is introduced. Identity, event, observation, season totals, finalization and external receipts have different tables. SQLite FK/unique/check constraints and atomic units enforce ordinary paths. Unknown team names stay NULL; no invented team label or historical event is substituted.

## Commands

Run from the repository root; replace `DB`/`SAVE`/`OUT` with new development files and the actual intended identity. Creation and export refuse overwrite. These are **not NBA2K22 game save files**.

```text
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py init DB SAVE
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py smoke
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py replay-ag01d DB AG01D-RESEARCH-ONLY --observed-at 2026-10-24T00:00:00Z
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py summary DB
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py player DB player:AG01D:1612
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py history DB player_season_totals --entity-key player_id --entity-id player:AG01D:1612
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py export DB player_game_boxes OUT
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py migrate-v1 OLD_DB NEW_DB
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py upgrade OLD_V1_OR_V2_DB NEW_V3_DB
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py replay-player-families DB AG01D-REGISTERED-PLAYERS
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py replay-owner-capture CAPTURE_DIRECTORY DB OWNER_CAPTURE_RESEARCH_ONLY
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py init-save SAVE_DIRECTORY nba2k22_test_01 NATIVE_SAVE_FILE
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py capture-live PID SAVE_DIRECTORY MyLEAGUE0003 NEW_CAPTURE_DIRECTORY --game-index 0
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py upgrade-save SAVE_DIRECTORY MyLEAGUE0003
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py capture-season PID SAVE_DIRECTORY MyLEAGUE0003 NEW_CAPTURE_DIRECTORY
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py schedule DB --status-code 2
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py capture-organization PID SAVE_DIRECTORY MyLEAGUE0003 NEW_CAPTURE_DIRECTORY
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py team DB team:native:0
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py staff DB staff:native:70
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py capture-market PID SAVE_DIRECTORY MyLEAGUE0003 NEW_CAPTURE_DIRECTORY
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py market DB --team-id team:native:5
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py prospect DB PROSPECT_OBSERVATION_ID
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py capture-planning PID SAVE_DIRECTORY MyLEAGUE0003 NEW_CAPTURE_DIRECTORY
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py planning DB --team-id team:native:20
python 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/cli.py gameplan DB team:native:20 team:native:0
python -m unittest discover -s 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests -p test_*.py -q
```

`replay-ag01d` reads the existing research files directly, hashes the actual inputs, decodes bounded 60-byte game, 24-byte Box, 48-byte cumulative and registered public PLAYER fields, then passes typed consistency units to `engine.ingest_capture`. It does not call the game process. Its output is **RESEARCH_FIXTURE**, with original save binding unverified. It imports 16 Curry game samples, 13 native season records and 54 public attribute values. The current-season reconciliation tests compare 16 additive metrics plus games played/started. Regulation quarter totals are a separate derived view; no native final total or individual overtime score is fabricated. Only one player's Box is supplied by this fixture, so it is not a complete both-team Box.

`replay-player-families` reads three actual historical PLAYER samples into public names, 54 attributes, 17 contracts, 48 registered named tendencies and four ordered PlayType slots per player. Offset 833's original-years bit 4–6 and extension-length bit 7–9 do not overlap in the registry; `family_codec.py` decodes the cross-byte field. This does not establish current UI meaning or full legal ranges, and badge ownership/tier remains an explicit gap.

`ingest_capture` accepts typed relational rows for all implemented domains. Source families may declare required fields; missing required values reject the unit. A failed unit cannot populate facts. Replays of the identical unit are idempotent; new observation units retain repeated values. Changed historical final games or finalized season totals cannot silently enter accepted facts; `ingest_or_quarantine` records a proposed digest for Human disposition while preserving accepted history. v1/v2 copy upgrades preserve old fact/registry rows and source-file bytes and add missing current catalog entries; they do not migrate the legacy production databases.

## Query, freshness and privacy

`query.player_card` returns each field's last actual non-NULL observation with its own unit, timestamp and source grade. A newer partial record never refreshes an older field. `query.history` returns bounded history; `query.export_jsonl` streams all selected rows and refuses a limit that would silently truncate history. Native totals and derived Box formulas are separated.

Registered attribute bytes also expose a separate `decoded_candidate` through the existing `src/config.py:raw_to_rating` codec. The raw observation remains unchanged, and the conversion is explicitly `DERIVED_REGISTERED_CODEC / target_ui_validation=NOT_OBSERVED`; it is not an observed UI fact or a proof of a complete game legal range.

SQLite file ownership is **not** a role ACL. Keep the owner database and all source artifacts inaccessible to ordinary roles. Give GM only the controlled query/export results. Public attributes never accept Potential; owner metadata/raw artifact paths/restricted observations/news/control tables are not available through GM history/export. Restricted observation storage is only a contract: this increment does not implement or authorize writing hidden values. The complete original PLAYER bytes are consumed locally but never included in a role result.

## Development state and serial handoff

The OS task/run is `01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/`. The work order remains [the serial task authority](WORK_ORDER_CODEX_ANTIGRAVITY_SERIAL_V1.md), with Human's subsequent clarification: **Codex may perform its own Native reverse engineering; Gemini is an optional batch-research assistant to save quota, not a required gate.** If offloading is useful, Human manually relays [the optional batch request](ANTIGRAVITY_NATIVE_REQUEST_01.md). No computer-use dispatch or concurrent model access. Codex resumes integration after Human returns the evidence and Antigravity has stopped all workspace/game operations.

`live_reader.py PID NEW_OUTPUT --game-index 0 [--player-links]` requests only `VM_READ|QUERY_LIMITED_INFORMATION`, logs actual API outcomes and never injects or writes. After Human granted administrator access, the Owner obtained one current 60-byte game and its full 624-byte / 26-player Box. The report's hex `0x1B6AC` offset failed score conservation; its decimal `112308` (`0x1B6B4`) candidate reproduced both teams' 122/106 period totals. Both raw controls and complete read traces are retained in the domain run. Optional player lookup reads only 2-byte IDs, names and Slot24 indices/totals, never hidden Potential.

Current PLAYER pool controls found duplicate Native IDs: Jrue Holiday at indices 16/742 and Kyrie Irving at 249/3389; one of each has a valid current Slot24 record, the other has sentinel 65535. This is evidence for context-dependent identity, not permission to merge records automatically. The source replay therefore stores all 26 rows in owner-only typed staging, leaves canonical player Boxes empty, and retains pending save/player/date bindings. The historical date decoder's month/UI meaning is unverified, so canonical `game_date` stays NULL. `inspect-source DB UNIT_ID` exposes bounded developer quality results. Native raw IDs are not silently turned into stable player identities.

`replay-owner-capture` verifies recorded-byte hashes and matching API trace entries, decodes raw bytes again, checks both-team score conservation and writes a **research-only replay**. Its `RESEARCH_FIXTURE` grade describes replay/candidate maturity; its origin is this task's recorded live acquisition. It is not an accepted, persistently bound world database, and cannot be used to claim a complete source or independent acceptance. JSON PASS assertions alone cannot bypass raw-byte conservation checks.

## Operator-bound current world (increment 04)

Human assigned `nba2k22_test_01` to the loaded native file `MyLEAGUE0003` in the declared remote save directory. `init-save` creates a small `save.json` declaration and one `world.sqlite`, refusing overwrite. `capture-live` takes the loaded filename explicitly and checks it against this declaration. Human announces switches and provides the new filename; reopening the same file keeps its save ID. File hashes, PID, pool positions and pointers are acquisition controls, not a replacement save identity. This prototype does not invoke the older production capture system or modify the game file.

`live_world.py` traverses the bounded PLAYER, TEAM and Slot24 descriptors, links both game teams to unique TEAM IDs, and discriminates duplicate player IDs using valid current-team pointers and current Slot24 records. A unique pool ID and valid TEAM pointer can also identify a player without a current cumulative record. That player still gets public fields and a game Box; the missing total stays absent. Ambiguity remains explicit, never a name-based merge. Selected source bytes, directory descriptors and game/Box bytes are reread to reject mixed observations.

The adapter requests public PLAYER segments on either side of Potential byte 1089; that byte is **never read**. Public binary artifacts contain a documented zero placeholder at the excluded position. They remain owner-only. The fresh Windows acquisition can emit `LIVE_READ` through an in-process acquisition receipt bound to the exact payload. A JSON payload passed directly to generic ingestion cannot assert that grade. `LIVE_READ` establishes acquisition provenance; UI semantics, unknown ranges and missing fields retain their own evidence limits.

Actual second acquisition into this bound world contains 26 players, 26 canonical game Boxes, 25 native season totals, 54 registered public attributes / 48 named tendencies / 17 contract fields / four PlayTypes per player, two teams and eight period scores. All 26 original native Box rows remain in source staging. Rodney Hood has no current Slot24 record; no cumulative zeros were substituted. Game date stays NULL pending UI calendar evidence. The earlier research replay remains unchanged with its original unbound identity and zero canonical Boxes.

## Complete observed schedule window (increment 05)

`capture-season` reads the actual Slot10 count within the known SEASON bound, retains its 32-byte index and all 60-byte records, reads both-team Boxes for every final, then resolves the union of completed-game player IDs. Every index entry is checked against its SEASON date bits and both current TEAM pointers. Complete windows and captured Boxes are reread around player-context acquisition. Invalid/duplicate/nonconserving game sources reject the batch. Unknown player mappings remain typed source rows and explicit gaps; no identity is invented.

Actual descriptor count is 1,232: 238 final games with both-team score conservation and 994 unplayed games. The final capture has 411 resolved players, 6,133 canonical game Boxes, all 6,170 native Box rows and 369 current player totals. Four IDs remain unresolved. Unplayed games get no artificial zero scores/Boxes; all canonical dates stay NULL pending UI calendar semantics. `schedule` uses latest observed state and exposes derived scores only when both canonical player Boxes cover every native in-use participant. Its row cap rejects truncation.

Schema v4 fixes final-history comparison to use only prior final observations, allowing scheduled/in-progress/final progression and consistent final re-observation. Conflicting finals still reject. `upgrade-save` copies v1/v2/v3 facts into a new current-schema file and switches the small binding pointer while retaining the old DB and declaration. Name decoding stops at the aligned UTF-16 NUL before interpreting padding; invalid text before the terminator still rejects a candidate.

## Current organization source (increment 06)

`capture-organization` follows current TEAM/STAFF/TEAM_STATS descriptors without reading PLAYER structures. All 30 core teams' eight role pointers must align to the staff array and match both each STAFF record's reverse TEAM pointer and its role bits. The adapter checks current COACHDATA/GAMEPLAN/PLAYBOOKDATA metadata using the existing read-only verifier, resolves assigned native staff IDs, decodes staff contracts/seven public skill fields and captures 24 head-coach defaults. The native metadata gives PreferredSystem/ActiveSystem four-bit widths; the older STAFF three-bit profile is not used for these observations.

Actual source provides 30 team totals, 240 assigned staff, 30 coach/default observations, 30 native finance snapshots and chemistry/fan state. Every team's wins/losses/points/opponent points reconciles exactly with the current complete schedule. The 84 loaded playbooks resolve all head-coach book codes and contribute 68 ordered native CRC slots per team (2,040 observations). Native book unique ID and loaded enum code are kept distinct. Play text labels, training and unassigned-staff market availability remain explicit gaps.

`team` and `staff` return typed allowed fields, source grade and observation freshness; raw structures, source pointers and Potential are withheld. Financial amounts retain unsigned raw integers, with no signed-cash conversion, cap-space calculation or salary-unit assertion. Schema v5 adds distinct typed coach fields, extra native team stats/finance columns and the state observation table. Copy-upgrade preserves old files and history.

## Native future picks and source market state (increment 07)

`capture-market` verifies current draft getter executable bytes and actual descriptors, accepts only complete simple future-pick year/round/original-team groups, and rereads records/controls. Actual source has 300 picks across 2022–2026 (30 original teams per year/round). Identity uses save-local year/round/original team; ownership is a separate append-only observation. Protection and swap statuses stay UNKNOWN. No tradeability window, trade event or draft result is inferred.

All 222 actual 136-byte waived-salary records are retained as typed observations; 32 map to current core teams. Three unsigned salary buckets and candidate inline UTF16 names are read, with canonical player FK and absolute salary years left unproven. The first Q word is not treated as a PLAYER pointer. Unmapped/empty owners remain explicit; no cap-space total or release event is invented.

The actual prospect pool has 90 allocated templates with no name and native ID zero. These produce slot-state observations, **zero prospect people** and zero prospect attribute/tendency/play-type facts. The acquisition skips Potential byte1089 on every prospect read and reread. Separate typed prospect families support named source observations, never PLAYER instances. Class year is nullable and cannot be filled from the future-pick base year. `market` and `prospect` provide bounded role-safe queries; free-agent availability is explicitly not observed by this source.

## Stored opponent plans and training (increment 08)

`capture-planning` verifies native roster/franchise getters and current plan/defense metadata, reads all registered 35 plan slots per core team, then accepts the complete 29-core-opponent set per team. It joins canonical rotation/defensive subjects only to exact reciprocal current-roster UIDs for the corresponding own/opponent team. Stale or sentinel IDs retain raw values and NULL player FKs. SQLite checks parent/child unit consistency and same-unit roster ownership.

Actual source has 870 core opponent plans (869 native commit flags0, one flag1), 20,010 ordered rotation rows and 20,010 defensive rows. The commit bit is observed state, not game-effect proof. The 461-player current roster binds 456 unique training IDs. All 786 registered training slots are classified; this capacity is not treated as an active count. Only ID+0 and flag bytes+0x318 are read from PLAYER_TRAINING; overall/attribute history arrays are not acquired. Thirty team training records supply six registered flag fields each.

Thirty mentor headers have plausible owner/count fields and 61 relation headers whose two subjects match current own-roster UIDs. These produce observed associations with activity/effect explicitly unverified; badge slots, tiers, consent and improvement are not inferred. `planning` returns bounded source snapshots and `gameplan` returns one owner's stored opponent plan with identity/commit state. Default COACHDATA, byte-based GAMEPLAN and global rotation remain separate concepts.

No source unreadability is a Q10 exception by itself. Missing player IDs, lifecycle, calendar/badge/contract/finance UI semantics, training focus/safe history, global rotation/effect, mentor badge activity, initialized class/year, protection/swaps and results, G League, settings and honors/news still require source evidence. No full-system acceptance, capacity benchmark, game writes, production migration or master integration is claimed.
