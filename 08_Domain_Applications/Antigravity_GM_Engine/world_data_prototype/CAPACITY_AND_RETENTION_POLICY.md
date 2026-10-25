# Capacity and retention — current Human direction

Authority: Human clarification on 2026-10-25, during `nba2k22-world-data-full-implementation-01`.

The current dedicated-test dataset represents about one month. Capacity stress tests and storage optimization are deferred. First expand the actual world-data coverage to a complete game season, then measure that season's real database growth and use it to estimate multi-year storage and decide the retention horizon. A complete schedule with unplayed games is not evidence of a season of completed game/history data.

The early page-allocation inspection and fixed-population models are retained only as exploratory engineering evidence. They are not an accepted season-size baseline, a 100-year workload result, a resource-budget verdict or a reason to trim history. They do not establish how often every source will actually be captured over a season.

The 100-year horizon remains a target to evaluate with representative season evidence. If that evidence shows 100 years cannot be retained in the operational database at acceptable cost, Human will decide the actual retained-year range. No shorter horizon, history deletion, pruning or automatic rollover has been authorized or implemented.

Continue the other engineering work, including Native source coverage, typed ingest/query/history and fact backup/recovery. The existing per-save isolation and append-only history remain in effect. Historical records and awards refresh once per game-season year per save. The capacity deferral does not pause the overall engineering goal or authorize game simulation/date advance/save writes.
