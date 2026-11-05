# BIC Wave2 offline diagnosis and Native plans

`bic_diagnostics.diagnose_player` consumes a scoped `player_baseline`. Its default inspection covers body, finishing, shooting, passing, defense and tendencies through existing public fields. The result retains badges, ordered PlayTypes, season observations, coverage gaps and source-linked findings. It distinguishes FACT, VERIFIED_MECHANISM, HYPOTHESIS, CONFLICT and UNKNOWN. No mechanism in this candidate is certified VERIFIED_MECHANISM.

Relative strengths/weaknesses use only existing `decoded_candidate` values from `src/config.py:raw_to_rating`. They are explicitly hypotheses about inspected candidate conversions, with their NOT_OBSERVED UI acceptance. Role labels are analyst directions for investigation. They are not Native role certifications or promised game outcomes.

Callers may supply `role_requirements` with `field`, `source`, `rationale` and optional finite `minimum`/`maximum` values in the actual field's storage units. These are visible candidate assumptions. No universal basketball threshold, personality weight or optimal tactic is embedded. A disagreement means a fact conflicts with that supplied criterion. It does not diagnose a causal game mechanism. `required_play_codes` similarly tests observed registration against sourced role assumptions, preserving UNKNOWN for stale/incomplete observations.

`diagnose_team` checks fixed supplied players against save/season/cutoff/build/mode and known roster membership. It presents per-player technical fit, team setting criteria and uncertainties about complementarity, opponent defense and rotation effects. Missing role/control evidence remains visible. Supplied opponent team facts must share context.

`bic_plans.native_capabilities` reuses the existing Core Profile bridge's pinned PR18 catalog and historical per-example maturity. It reads no live target. `plan_adjustment` maps OFFENSE_FOCUS, DEFENSE_FOCUS, COACH_SETTINGS, TRAINING_FOCUS and PLAYBOOK_CHANGE to existing catalog actions, or accepts an explicit catalog action ID. It checks declared parameter contracts, before values/source, target identity, build and mode. Nested or numeric domains without evidence are NEEDS_VALIDATION. Player edits, transactions and draft actions are FORBIDDEN in this diagnostic batch. An OFFLINE_PLAN_READY result still has execute=false and requires separate live authorization.

`diagnose_and_plan` joins the flow. A role requirement can contain a `candidate_intent`, which is linked back to its finding index. Independent intents can also be inspected. The linked flow checks diagnosis/plan identity, build and mode. An unavailable catalog affects the plan, while fact diagnosis continues. Outputs point to existing Bulk CAS, readback, chunk, Journal and recovery obligations without implementing another executor. Historical write/effect examples remain bounded to original inputs.

```text
python -B bic_wave2_cli.py <existing.sqlite> <player-id> --save-id <save> --season-id <season> --as-of <aware-ISO-time> --team-id <team-id> --request <candidate-role-and-intents.json>
```

Request JSON may contain `role_requirements`, `team_requirements`, `required_play_codes` and `intents`. Omit it for source/gap inspection. Known source-gaps produce partial reports. Native catalog Git objects are resolved through existing `research/rea_core_profile/profile.json`; missing objects produce an explicit capability gap. Other source-contract errors fail closed.

`synthetic_validation` reuses the first-wave factorial helper. Experiment outputs remain synthetic. Validation requirements include save/build/mode, assignment, team-season clusters, opponent/schedule, roster/coach, injury/fatigue/growth, randomness and timestamped 3D behavior evidence. Box-score association alone cannot identify a causal setting or certify tactical execution.

Evidence and historical Siakam/Jokic cases are in repository-root `01_os/07_content/_runs/run-20261104-nba2k22-bic-wave2-001/`. Historical records retain UNBOUND build/save headers and REAL_DATA_NOT_VERIFIED. This candidate awaits GPT-6 series review and formal OS acceptance.
