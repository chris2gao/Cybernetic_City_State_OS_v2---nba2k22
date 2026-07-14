# Validation report

- Four `sandbox_evaluator.py` runs: Mode A 2 passed; Mode B 2
  `review_required` with honest semantic-audit warnings.
- Post-repair `COMPLEX_ANALYSIS-418`: passed.
- P0 consolidated validator: passed; repeat builds byte-identical; materialized
  outputs matched; `consumer_allowed=0`; runtime activation false.
- P0 unittest suite: 104 executed, 103 passed, 1 fixed provenance-count
  assertion failed (`expected E3=8/E4=20`, `actual E3=7/E4=21`).
- All changed YAML and JSON: parsed.
- Four dossiers and consolidated identity evidence: local Draft 2020-12 schemas
  passed.
- `git diff --check`: passed.
- Forbidden-path and high-confidence secret-path/name scan: passed.
- Runtime, Coordinator, state, scheduler, bridge, roadmap, prompt, registry,
  control-plane, and non-pilot-node mutations: none.

The single unittest failure is preserved as evidence rather than normalized
away: `detect_schema_era` defines any path changed since Stage 0 as E4, and the
authorized pilot repair changed exactly one formerly E3 path.
