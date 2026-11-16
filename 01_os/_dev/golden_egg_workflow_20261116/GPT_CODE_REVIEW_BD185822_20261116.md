# Human/GPT · Core OS 金蛋执行链候选集中复核（代码证据）

**Review target:** `bd185822822543350e9d3c07a1174285b47b788d`  
**Base:** `043ac4864bdc871b03929faafd8bc6bd47d4ee2f`  
**Verdict:** `ENGINEERING_CANDIDATE_PASS_WITH_TARGETED_FIXES`；**not** formal Stage04 frozen, Stage07 PASS, Human master merge authorization, or NBA T15 completed. Reviewer: GPT technical evidence review, Human to decide.

## Evidence directly inspected

- GitHub `compare_commits`: 2 commits ahead; 14 changed files (5 existing, 9 run-owned); production code diff only `run_minimum_operational_loop.py` plus README updates.
- Actual source `run_minimum_operational_loop.py` at target lines 818–959: `next_business_action` (facts, dependencies, priority, approval-choice equality, resource UNKNOWN), `business_time_quality` (reported source layers and time spans), two new opt-in CLI commands.
- `test_business_decisions.py`: T01–T14 and five targeted extra tests; `exercise_task_path.py` really starts the `engineering` subprocess based on CLI selection; `actual_decision_result.json` records exit 0.
- `RESULT.md` reports local managed verification and 53 pytest regression passes. GitHub commit had no status checks or PR-triggered Actions returned at review. Local `verification_receipt.json` could not be read in review because Desktop Commander was offline: local 544.49s receipt/CI PASS is **reported** rather than independently rerun here.
- T15 deliberately NOT_RUN; engine is opt-in and relies on domain adapters for facts, authorization, CAS, journal, resources, and real Done.

## Correctly completed limited scope

- New selection code is real and callable, not just a document.
- No automatic side-effect dispatch, no Native calls, no implicit grants.
- Existing formal frozen test/reviewer validation functions were not modified.
- GE-01 event-time distinctions are preserved in `business_time_quality` output (but supplied metrics are not authenticated by the function).
- Current actual path demonstrates selecting `engineering` ahead of `optional_documentation`, then launching an existing Python test; it does **not** demonstrate automatic adoption by generic model workflows.

## Two concrete algorithmic issues for a **single small follow-up**, not another planning loop

**F01 / goal-relevance flaw (P1):** In `next_business_action`, priorities are fixed at lines 841 and 883–885: `diagnostic:0,preflight:1,business:2,optional:3`. If a ready business node has no necessary diagnostic/preflight dependency, an unrelated diagnostic or preflight still wins. Counterexample: ready `perform_business` versus unrelated ready `check_unrelated` tagged `preflight`; current `min(candidates)` selects `check_unrelated`. The field `kind` is untrusted semantics supplied by the caller. This can reproduce the original excessive preparation problem. **Expected:** In the absence of a documented blocker or dependency, an already-ready high-value business action must not be postponed by an unrelated preparatory node; an early decisive check should win only if it is causally necessary/relevant. Preserve the original T09 behavior when decisive check really is available and necessary.

**F02 / optional-work-on-blocker flaw (P1):** If the main business step is blocked in scope `research` while a ready optional step is in a different scope `docs`, the current function selects `docs` rather than returning the business blocker / eligible remediation action. This risks extending the original idle-preparation spiral. **Expected:** If the primary business result is blocked, prioritize a directly useful local diagnostic/recovery, otherwise return truthful `BLOCKED`; independent *required, authorized business/safety* steps may continue. Do not globally stop unrelated safe required work.

**Implementation constraint:** Test those two cases independently against target SHA first; retain unchanged T01/T02/T09 assertions and real-parent-Done/UNKNOWN/authorization protections. Change the smallest actual selector logic needed (existing runner) and a few bounded tests; no new policy engine, planner, scheduler, monitor, authorization system or live NBA simulation. If the policy cannot be expressed without a new general semantic ontology, stop with one specific limitation instead of designing a platform.

## Other nonblocking limits / future evidence

- Caller-provided fact `source_ref` strings and `kind` are not independently authenticated. This is *documented domain-adapter responsibility*, not a new permission issuer; cannot call this an unconditional safety gate.
- The CLI is opt-in; a single local engineering test exercise is not proof that arbitrary Codex jobs will invoke it.
- Timing: RESULT.md reports a 569.34s earlier pytest run, final handoff reports 544.49s and ~84min cumulative wall over several windows. Without final local receipt, cannot independently reconcile time attribution or claim saved minutes. Do not optimize by skipping safety checks.
- T15 under separate exact NBA authorization remains the external effect comparison and SC-10 closure.

## Review decision

**Accept bounded prototype evidence, do not merge into protected master yet.** Request only one bounded F01/F02 correction and the related negative tests; Human/GPT review the new precise diff/results. No repeat of old Stage04 G2 preflight, no new independent-model review, no extra run/Issue/monitor platform. Merge and actual business deployment remain Human decisions.
