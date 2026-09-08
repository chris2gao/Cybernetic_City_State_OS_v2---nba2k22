# Remaining policy / instance-validator convergence

Status: evidence-backed open implementation boundary, not independent acceptance.
Base: `3dc058a1a3cf393b936025f43fd737b0848937b4`. The files below are unchanged by
the foundation candidate except the explicitly identified current task entry.

## What is established by source inspection

1. `01_os/开发入口与单窗口任务规范_v1.md` section 7.2 permits ordinary reversible
   work by current Human task input plus durable scope. Covered actions must not
   trigger repeated micro-authorization. The same policy is machine-readable in
   `01_os/05_registry/repository_publisher_authority_v1.yml`:
   `ordinary_task_execution` requires no code, nonce or authority chain, while
   `legacy_compatibility` retains old artifacts only for referenced history.
2. `01_os/03_mechanisms/stage_collaborative_deliberation/阶段profile契约_v1.yml`
   `mandatory_Human_confirmation_contract`, `inquiry_contract` and
   `activation_contract.dormant_still_requires` still require explicit fresh
   confirmation for every task/stage and disallow earlier-stage confirmation as
   its substitute. These fields are not superseded by the activation record.
3. The current `实现/verify_stage_collaborative_deliberation_v2.py` instance CLI
   calls base `validate_instance`. That production entry unconditionally calls
   `validate_model_readiness`, which requires `validate_mandatory_Human_confirmation`
   and `validate_human_authority`. Mandatory confirmation demands a durable
   disposition ref/blob, decision id and nonce commitment; the v2 branch also
   demands task authority identity and task commitment. This is executable policy,
   not merely prose that can safely be called historical. No runtime instance
   result is claimed from this static call-graph inspection.

The profile contract's older `status: staged_inert` and `candidate_state` do not
create another unresolved activation contradiction: `激活状态_v1.yml.supersession`
explicitly replaces those interpretations with current `active_dormant`.

## Why the pin repair and green checks are insufficient

The unchanged required plan checks workflow/static wiring and the foundation's
packet/process regression suite. It does **not** test a new ordinary task passing
the production stage-instance entry without legacy authority artifacts. Correct
hashes therefore cannot prove this policy / implementation mismatch is resolved.
The overall foundation objective and semantic convergence remain incomplete even
if all seven checks pass. Do not submit this checkpoint as a fully finished OS or
ask an independent reviewer to assume the open requirement has been met.

## Proposed continuation within the same overall task

Use the already-current ordinary task-scope policy as the target, not a newly
invented authorization policy. Unify the profile text and production validation
path around current task scope; retain explicit Human gates for genuinely new
load-bearing choices, uncovered protected actions, and acceptance decisions.
Covered actions do not gain a new gate merely because a workflow stage changes.

Before implementing, the current pin-only amendment would need to cover the
profile contract and production validators, matching tests/fixtures, and every
exact-ref consumer affected by those body changes. Inspect dependency refs first;
do not blanket-allow all of `01_os`. Ordinary input must not silently fall back to
legacy authority parsing, and protected/history routes must not weaken.

Required evidence for that change:

- A real production-entry ordinary positive case using current durable task scope
  without a task code/nonce/delegation chain, paired with the current failure.
- Missing/mismatched task scope, out-of-scope action and absent mandatory evidence
  fail closed; falsey/wrong-type input cannot manufacture an ordinary route.
- Uncovered protected action stays blocked; a covered action is not repeatedly
  gated at stage boundaries. New semantic choices retain the Human decision stop.
- Explicit historical input remains on its declared historical route; no guessed
  authority, automatic conversion, secret collection or new legacy artifact issuance.
- Legal merge fixtures stay unchanged; reference consumers are updated only after
  the revised body is established, and the complete exact-candidate check plan runs.
- Fresh independent semantic/implementation acceptance before integration; if an
  obsolete mechanism is to be deleted, its removal needs the repository's review.

No such body change or acceptance has been performed by this checkpoint. Stronger
independently controlled execution/publication enforcement also remains a separate
deployment boundary; local editable records do not provide it.
