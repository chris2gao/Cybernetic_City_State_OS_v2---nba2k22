# BIC offline baseline candidate

Use `bic_baseline.player_baseline` and `team_baseline` with an existing WorldData database, explicit save ID, season ID, timezone-aware observation cutoff and a maximum field age in seconds. The result preserves the existing public query boundary and adds per-observation provenance, knowledge state and freshness. A card can contain multiple observation units. `effective_at` remains distinct from capture time.

```text
python -B bic_cli.py player <existing-world.sqlite> <player-id> --save-id <save> --season-id <season> --as-of 2026-10-27T00:00:00Z
python -B bic_cli.py team <existing-world.sqlite> <team-id> --save-id <save> --season-id <season> --as-of 2026-10-27T00:00:00Z --max-age-seconds 3600
```

`coverage_report` counts missing and stale scalar observations and lists contributing units. `knowledge_status` classifies source claims conservatively. `badge_intelligence` preserves owned/base-code facts while returning UNKNOWN for unproved eligibility, XP, growth and game effects. Optional `expected_native_identity` binds both UniqueId and PreservedId raw components, with conflicting observed identities rejected.

The historical schema permits a NULL season save ID. Such records are explicitly DATABASE_LOCAL_ONLY after the requested save matches the database header. The full database binding, Native identity history and original grades remain visible. REAL_DATA_NOT_VERIFIED remains the default until independent source admission. League FRANCHISE context is distinct from per-game Fast Sim, CPU 3D or Human 3D evidence; game mode remains UNKNOWN in a general card.

`bic_experiments.factorial_2x2` computes A/B marginal mean differences and a difference-in-differences interaction. Synthetic fixtures are labelled SYNTHETIC_ARITHMETIC_ONLY. Real-data arithmetic retains NOT_CAUSALLY_IDENTIFIED pending design review. Missing treatment cells, team/season clustering, mode ambiguity and absent 3D behavior observations require explicit evidence. No confidence interval is invented for a single observation per cell.

Engineering evidence and reproducible checks are in repository-root `01_os/07_content/_runs/run-20261104-nba2k22-bic-offline-engineering-001/`. Formal OS acceptance and independent review remain pending.
