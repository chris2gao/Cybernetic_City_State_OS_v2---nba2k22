# Validation Report — Math Mentor Master Plan And Progress Ledger

## Required outcomes

| Check | Result |
|---|---|
| bound source `master@9e12064...` verified before mutation | pass |
| 13 required ledger sections | pass |
| current-master referenced paths | pass |
| bridge physical inventory and duplicate IDs | pass |
| legacy bridges described as present but non-canonical/non-consumable | pass |
| LRP current-master status reconciled | pass |
| no runtime inferred from documentation | pass |
| ChatGPT/Claude front-agent and Codex/Claude Code backend roles | pass |
| backend resource requires front-agent semantic/pedagogical review | pass |
| UI marked `not_required` | pass |
| next batch has 3–5 exact nodes and is proposal-only | pass (4) |
| YAML/JSON parse | pass |
| `git diff --check` | pass |
| exact changed-path allowlist | pass |
| high-confidence added-secret scan | pass |

## Quantitative reproduction

```yaml
root_candidates: 667
staging_exclusions: 229
unapproved_candidate_edges: 420
explicit_alias_conflicts: 53
pilot_accepted_nodes: 4
consumer_allowed: 0
p0_fresh_checkout_tests: "104/104"
legacy_bridge_files: 14
legacy_bridge_unique_ids: 10
legacy_bridge_duplicate_ids: 4
legacy_bridge_schema_families: 2
legacy_bridge_indexed: 5
legacy_bridge_unindexed: 9
legacy_bridge_explicit_endpoint_resolved: 0
legacy_bridge_unresolved: 14
canonical_bridge_v1_files: 0
```

## Scope assertion

Validation did not activate runtime, execute Coordinator, mutate teaching assets, generate/migrate bridges, promote consumers, create a PR, or publish to source/master.
