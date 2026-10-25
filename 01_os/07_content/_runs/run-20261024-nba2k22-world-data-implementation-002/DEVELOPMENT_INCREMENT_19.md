# Increment 19 — coherent acquisition-time queries and observation history

Full goal remains active and incomplete. Final candidate `f2035751aaef8d352e38ee4a0a678c3e1ada359a` adds an observation-time query context, public CLI/API cutoff support and complete cursor paging. Physical schema remains **v16 / 84 STRICT tables / 1,306 columns**; no stored facts or binding were changed.

## User-visible behavior

Public read/export commands accept `--as-of TIMEZONE_AWARE_ISO_TIMESTAMP`. The cutoff is inclusive in **host acquisition observed_at**, not the native game calendar, event occurrence time or an assertion about changes between captures. CLI results wrap the ordinary response with normalized cutoff, save/schema identity, visible committed unit count and a scope fingerprint. Python users can call `query_at(DB,TIMESTAMP,'player_card',PLAYER_ID)` or hold `observed_as_of(DB,TIMESTAMP)` while using the existing public query functions.

All eligible committed successful capture IDs are frozen once per request. Query connections open the original database read-only and build temporary observation projections. Nested calls therefore use the same eligible unit set even if an older-dated capture commits while the request runs. Failed/future units are excluded. Explicitly supplying a future native unit ID does not bypass the cutoff. Public static player/team/staff/game/pick/season identities require visible source evidence, preventing a later-introduced identity/name from appearing through an earlier card.

Fields retain their individual last non-NULL observation time, grade and unit. Later sparse rows do not refresh older values. Player-card PlayType results now select each slot's last actually observed non-NULL code, with no arbitrary history-page cutoff. Code0/NONE clears an observed slot; an unavailable NULL slot does not. Every original slot observation, including an unavailable slot, remains in raw history.

`history-page` returns deterministic timestamp/primary-key pages, `has_more` and `next_cursor`. The cursor binds the cutoff, observation-ledger fingerprint and table/entity filter. Tied timestamps do not drop rows. A late committed/backfilled unit changes the ledger and causes resumption to refuse a mixed view; an existing held Python scope remains fixed. Historical JSONL export counts only visible observations before checking its explicit row cap. The prior bounded `history` API remains compatible.

## Actual database proof

The actual v16 world contains18 successful units. The checker used **19 cutoffs**, including before the first observation, and **56 public unit-based tables**. All **1,064** scoped count results match direct main-database SQL. At four selected player cutoffs, **1,124** per-field comparisons match the independent value/unit/age/grade reference, including values that had not yet been observed. The earliest view does not prematurely expose Curry's later-observed identity.

At the last observed cutoff, **23 existing query results** equal their ordinary current counterparts: player/team/staff/game/schedule, badges and ordered slots, market/settings/rules/planning/gameplan, native player families, honors/record book, awards/history/news/transactions and bounded history. An explicit future skill-source pin remains empty before its capture.

Complete attribute history returns **4,201** unique observations across **17 pages**, without missing or duplicate IDs. Export before the new complete-skill capture contains **811** earlier observations. Query examples retain four actual Curry cutoffs and a historical export receipt. The database remains SHA256 `466d3eeaf7bda194cdba7f26f6013227a9c2a569084ee450a665792746135932`, with the active binding unchanged. The existing `increment17/world-v16.sqlite.gz` is the exact reference database archive; unchanged data is not copied again.

## Validation and provenance

The full suite passes **139 tests**, plus SQLite smoke. Twelve new temporal cases cover timezone/microsecond boundaries, partial-field age, future identities and failed units, explicit native source pins, current slots/ownership, cross-domain cutoffs, equal-time complete paging, pinned requests during backfill, cursor refusal after a ledger change, nested/cross-database contexts, restricted exports, immutable source bytes and CLI envelope compatibility.

Initial full verification is retained under `verification/`: one new fixture assertion still counted five slot rows after a sixth unavailable observation had been added. Only the expected raw-history count was corrected; no observation or runtime query code was removed to pass it. The corrected complete run is under `verification-corrected/`. Actual database checks executed runtime commit `a56e7671f233dd08b5b31b29c01bc8bd0ae90abc`; final candidate differs only in that test correction. The delivery checker compares all executed non-test source/profile/schema bytes across those commits and checks the complete final candidate source hashes.

This is historical observation reconstruction using the current schema/decoder interpretation. It does not certify historical UI rendering, cross-session/lifecycle identity or native occurrence dates. Controlled query projections are not a SQLite file ACL. No game process, game/save write, data migration, history rewrite, capacity stress/optimization, retention reduction, Antigravity dispatch or master integration occurred. Human's capacity deferral until a complete real season remains in force. Native/UI gaps and whole-candidate independent/Human acceptance remain open; no Q10 exception or goal completion is claimed.
