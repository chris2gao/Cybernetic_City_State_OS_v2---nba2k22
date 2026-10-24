# NBA2K22 per-save world database — full-system development

Task: `nba2k22-world-data-full-implementation-01`. This is an **in-progress engineering candidate**: executable all-domain structure with a bounded historical research adapter; full live-source coverage, whole-system acceptance and independent review are outstanding.

## Implemented structure

**61 STRICT SQLite tables, 632 columns**. The 59-table approved provisional catalog is implemented, retaining the original prototype's `game_state_observations` and adding explicit `season_finalizations`. The original 16 table names and observations are preserved. See [table cards](TABLE_CARDS.md), [complete field dictionary](field_dictionary.json), executable [DDL](schema.sql) and its [catalog generator](schema_model.py).

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
python -m unittest discover -s 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests -p test_*.py -q
```

`replay-ag01d` reads the existing research files directly, hashes the actual inputs, decodes bounded 60-byte game, 24-byte Box, 48-byte cumulative and registered public PLAYER fields, then passes typed consistency units to `engine.ingest_capture`. It does not call the game process. Its output is **RESEARCH_FIXTURE**, with original save binding unverified. It imports 16 Curry game samples, 13 native season records and 54 public attribute values. The current-season reconciliation tests compare 16 additive metrics plus games played/started. Regulation quarter totals are a separate derived view; no native final total or individual overtime score is fabricated. Only one player's Box is supplied by this fixture, so it is not a complete both-team Box.

`ingest_capture` accepts typed relational rows for all implemented domains. Source families may declare required fields; missing required values reject the unit. A failed unit cannot populate facts. Replays of the identical unit are idempotent; new observation units retain repeated values. Changed historical final games or finalized season totals cannot silently enter accepted facts; `ingest_or_quarantine` records a proposed digest for Human disposition while preserving accepted history. Copy migration leaves the original v1 SQLite hash and observations unchanged; it is not a legacy production-database migration.

## Query, freshness and privacy

`query.player_card` returns each field's last actual non-NULL observation with its own unit, timestamp and source grade. A newer partial record never refreshes an older field. `query.history` returns bounded history; `query.export_jsonl` streams all selected rows and refuses a limit that would silently truncate history. Native totals and derived Box formulas are separated.

SQLite file ownership is **not** a role ACL. Keep the owner database and all source artifacts inaccessible to ordinary roles. Give GM only the controlled query/export results. Public attributes never accept Potential; owner metadata/raw artifact paths/restricted observations/news/control tables are not available through GM history/export. Restricted observation storage is only a contract: this increment does not implement or authorize writing hidden values. The complete original PLAYER bytes are consumed locally but never included in a role result.

## Development state and serial handoff

The OS task/run is `01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/`. The work order remains [the serial task authority](WORK_ORDER_CODEX_ANTIGRAVITY_SERIAL_V1.md). After the first implementation increment, Human relays [the bounded Native request](ANTIGRAVITY_NATIVE_REQUEST_01.md) manually. No computer-use dispatch or concurrent model access. Codex resumes integration after Human returns the evidence and Antigravity has stopped all workspace/game operations.

No source unreadability is a Q10 exception by itself. Live save binding, full schedule and both-team Box, badge/contract ambiguities, staff assignments, draft/G League, settings and honors/news still require source evidence. No full-system acceptance, capacity benchmark, game writes, production migration or master integration is claimed.
