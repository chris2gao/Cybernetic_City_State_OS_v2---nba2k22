# NBA2K22 per-save world database — full-system development

Task: `nba2k22-world-data-full-implementation-01`. This is an **in-progress engineering candidate**: executable all-domain structure with a bounded historical research adapter; full live-source coverage, whole-system acceptance and independent review are outstanding.

## Implemented structure

**Schema v3: 62 STRICT SQLite tables, 659 columns**. The 59-table approved provisional catalog is implemented, retaining `game_state_observations`, adding explicit `season_finalizations` and typed `native_box_observations` staging. The latter preserves real captured stats when a canonical player binding is not proven. The original 16 table names and observations are preserved. See [table cards](TABLE_CARDS.md), [complete field dictionary](field_dictionary.json), executable [DDL](schema.sql) and its [catalog generator](schema_model.py).

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

No source unreadability is a Q10 exception by itself. Live save binding, full schedule and both-team Box, badge/contract ambiguities, staff assignments, draft/G League, settings and honors/news still require source evidence. No full-system acceptance, capacity benchmark, game writes, production migration or master integration is claimed.
