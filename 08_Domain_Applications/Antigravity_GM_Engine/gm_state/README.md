# External GM state

This directory contains player-triggered external analysis, not game observations.

`careers/<save_id>/runs/<run_id>/run.json`, `REPORT.md`, and `teams/<abbr>.json`
are independent analysis snapshots. A new run never overwrites another run.
`careers/<save_id>/proposals/<decision_id>_v<version>.json` contains unapproved
proposals only. v1 does not provide approval, execution, or confirmed-history writes.

Canonical `teams/` and `history/` remain reserved for future player-confirmed
records. Existing formal team dossiers are read-only references. Development
simulations go to `_exports/gm_v1_development/`, not this production directory.
No collector/publisher watches this directory or executes its contents.
