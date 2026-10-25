# Increment 20 — coherent Game Boxes and source-qualified season summaries

Full engineering goal remains active and incomplete. Runtime candidate `f4fb41ce85d50d29610392b0bdc5e078ded8b720` adds single-unit Game Boxes, season summaries and player season observations. Physical schema remains **v16 / 84 STRICT tables / 1,306 columns**. This increment queries the existing operator-bound facts; it acquires no new game data and does not migrate or change stored facts.

## Result

`game DB GAME_ID [--unit-id UNIT]` now selects one successful acquisition unit, comparing normalized UTC timestamps with microsecond precision and deterministic unit-ID ties. Its states, periods and both public Box families all come from that unit. A newer partial observation remains partial; older rows are not borrowed to fill it. An explicit unavailable/out-of-scope unit never silently falls back. Available capture metadata and the existing append-only history APIs retain access to earlier observations.

Score fields distinguish literal game-state values with their provenance, sums of captured Native in-use rows and canonical player sums qualified against that same captured window. Qualification checks exact counts, unique Native participant IDs, current-context resolution status, team IDs and per-player points. Inactive allocation slots do not count as participants. An incomplete or mismatched mapping withholds the primary derived score while retaining the separately described captured-row sum. This is evidence of the captured window, not proof of historical lifecycle or UI semantics. Literal partial scores remain partial. Four observed quarter rows are not expanded into invented overtime splits.

`season DB SEASON_ID [--phase-code CODE] [--limit 1000]` selects the latest totals per exact entity/season/phase; player records additionally retain exact team scope and team ID. `player-seasons DB PLAYER_ID [--season-id ID] [--phase-code CODE] [--limit 100]` exposes the same qualified observations, also included in the player card. Both APIs support the existing acquisition `--as-of` cutoff. Distinct periods/scopes/team stints are never summed into a career total.

Each count per game uses the same row's observed player games played or the explicitly labeled team wins-plus-losses denominator. Missing, zero or inconsistent denominators yield NULL rates. Shooting fractions use same-row made/attempted values, with zero attempts undefined and invalid counts flagged. Native raw minutes are retained without conversion. Unknown phase and observed finality remain as recorded. Win-fraction display ordering stays within an exact phase and does not assert official conference seeds, tiebreaks or season closure. Explicit caps refuse truncation.

## Actual stored-fact verification

The checker independently selects eligible units and latest totals, compares typed rows against direct main-database SQL and recalculates rates without using the query helper's selection/derivation functions.

- All **1,232** games choose their latest successful unit. All have multiple stored units; an earlier explicit pin is also checked for each game. All **9,745** selected public game rows match SQL, and every returned row has the selected unit ID.
- **202** final games qualify both canonical team scores. The remaining **36** finals with unresolved/mismatched captured participants retain unknown primary derived scores. The **994** unplayed games retain no invented zero scores. Side coverage counts are439 qualified,37 incomplete and1,988 without a captured Native window.
- Exact observed `season:native-year:2022` has **369** latest player totals and **30** latest team totals. **6,783** per-game/shooting-fraction calculations agree with independent arithmetic. **369** player-season query results match their exact selected period/scope keys.
- Current season results equal results at the latest acquisition cutoff. A cutoff preceding the first actual cumulative capture exposes no later totals.
- The source DB remains SHA256 `466d3eeaf7bda194cdba7f26f6013227a9c2a569084ee450a665792746135932`, and active `save.json` is unchanged. `increment17/world-v16.sqlite.gz` remains the exact reference archive; unchanged data is not copied again.

Examples, all-game comparison receipts and the executed checker are under `06_执行/increment20/`. The checker initially based its pre-first-total cutoff on the latest selected rows, which excluded an earlier cumulative capture. Its boundary was corrected to the minimum of all actual cumulative observations; no runtime query code or source facts were changed to resolve that checker assertion.

## Validation and scope

**151 tests plus SQLite smoke pass.** Twelve new fixture tests cover repeat/pinned captures, newer partials, unknown pins, unplayed/unused slots, missing/wrong identities and points, inactive slots, partial literal provenance, UTC/microsecond order, missing denominators, zero/invalid shooting counts, exact phase/scope/team/season separation, explicit caps and CLI historical cutoffs. An initial targeted fixture used a different default provenance in a frozen final re-observation; the existing immutable-fact guard correctly rejected it. The fixture now preserves identical provenance. That guard was not weakened.

Executed candidate source hashes, independent SQL receipts, archive hash, OS preflight and MWU validation are checked before evidence publication. This remains developer verification, with Native/UI/lifecycle gaps and whole-candidate independent/Human acceptance outstanding. No Q10 exception is inferred.

Human's current direction is unchanged: **capacity stress, storage optimization and retention estimates wait for a complete real season**, rather than treating the present one-month sample or unplayed schedule as a season-sized workload. No history trimming or shorter retention horizon is authorized. Historical records/awards retain the once-per-game-season-year cadence. No game/process access, game/save write, date advance, new capture, schema migration, Antigravity dispatch, capacity work or master integration occurred in this increment.
