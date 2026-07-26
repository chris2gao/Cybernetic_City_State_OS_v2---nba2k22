---
task_version: "1.0"
task_id: "human-release-rebinding-cycle-0001"
title: "Close the open release binding: one clean semantics + binding pair"
mode: "goal"
task_level: 2

intent:
  goal: >-
    Return the repository to a coherent bound release state by executing one
    complete two-commit release cycle, so that every canonical bootstrap file is
    blob-identical between the semantics commit and the binding child, and the
    release-binding unit test passes for all seven required paths.
  why_now: >-
    Three commits changed release-bound protocol files without opening a release
    window. The policy still declares release_binding_status "bound" while three
    bound paths have moved past protocol_release_head, so the declared state and
    the actual state disagree. Until this is closed, every further protocol edit
    adds another red subtest, and a green fixture run proves nothing about the
    current bootstrap snapshot.
  definition_of_done:
    - "test_release_receipt_files_are_identical_between_semantics_and_binding passes for all seven bootstrap_required_loaded_files paths plus every on-demand path the test derives."
    - "The full unit suite under .ai/communication_compliance/tests passes; report the counts you measured rather than any count quoted here."
    - "run-fixtures passes with mismatch 0."
    - "material_event_policy.yml and lane_epoch.yml both carry a bound status and a release head pointing at the semantics commit of this cycle."
    - "The binding child changed no canonical receipt-loaded file; this is demonstrated by the passing receipt-identity test, not asserted."
    - "master is not pushed. origin/master is unchanged. Core history is not rewritten."
    - "A short report is published to ai/review/latest and its head is returned in the handoff."

outputs:
  primary: ".ai/CODEX_REPORTS/release-rebinding-cycle-0001.md"

inputs:
  required_refs:
    - ".ai/communication_compliance/README.md"
    - ".ai/communication_compliance/material_event_policy.yml"
    - ".ai/lanes/lane_epoch.yml"
    - ".ai/CODEX_REPORTS/core-structural-integrity-diagnosis-0001.md"
  local_files:
    - "E:/newStand/城邦简报/core/03_决策档案/2026-07-26_发布重绑定流程_从历史推定.md"

scope:
  allowed_actions:
    - "revert the single uncommitted line described in section 1"
    - "edit material_event_policy.yml and lane_epoch.yml binding fields"
    - "update canonical_ref_digests where a pinned file changes in this cycle"
    - "regenerate release-derived fixtures, suite, and latest result"
    - "create exactly two source commits on master: semantics, then binding child"
    - "publish one report to ai/review/latest"
  forbidden_actions:
    - "push master or any source branch"
    - "rewrite history, amend, rebase, reset --hard, or force push"
    - "change the content of any bootstrap_required_loaded_files path in the binding child"
    - "change the EOL normalization convention used by existing digests"
    - "delete, relocate, or reclassify anything under domain_owned_paths"
    - "act on either adjudication-pending item C1 or C2 from the diagnosis report"

return:
  packet_id: "codex-release-rebinding-cycle-0001"

completion_policy: "completion_preserving"
---

# Release rebinding cycle — close the open binding

## 0. Authority for this procedure

The procedure is **already written down**. Use
`.ai/communication_compliance/README.md#release-binding` and its `## Verification`
section as the authority, cross-checked against section 6 of
`.ai/CODEX_REPORTS/core-structural-integrity-diagnosis-0001.md`.

A prior Claude derivation exists in the brief vault (`inputs.local_files`). It reached
the same two-commit shape from git history alone but **missed `lane_epoch.yml`
entirely** and asserted that no document described the procedure — that assertion was
wrong. Treat that file as corroborating archaeology, not as authority.

## 1. Step zero: revert one uncommitted line

The working tree carries one uncommitted addition to
`.ai/HANDOFF_COMMON_CONVENTIONS.md` §4.1. **Human decision: revert it.**

Reasons, so it is not re-added later: §4.1 already states the derivation rule; the
added line restates it in a second language inside the same section; and the line
names `.ai/HANDOFF_COMMON_CONVENTIONS.md#4.1` as the authority for its own content,
which is a self-referential loop.

Revert the working-tree change only. Do not touch the committed §4.1 content — that
is legitimate and is part of what this cycle binds.

## 2. What is currently open

Measure this yourself; the following is context, not input data.

Three commits changed release-bound files without opening a release window:
`AGENTS.md`, `.ai/PROTOCOL.md`, and `.ai/HANDOFF_COMMON_CONVENTIONS.md` have each
moved past `protocol_release_head` while the policy still declares `bound`.

This is materially different from being mid-cycle. A repository sitting in a declared
`unbound` window is honestly red. This one declares `bound` and is wrong, so anything
reading `release_binding_status` receives a false signal. Say which of the two states
you find when you measure.

## 3. The cycle

Follow the README. Summarised so the shape is unambiguous:

**Semantics commit.** In one commit: finish all protocol content for this release,
set `protocol_release_head: null` and `release_binding_status: "unbound"` in
`material_event_policy.yml`, and set the corresponding lane fields in
`.ai/lanes/lane_epoch.yml` to their unbound values. Include any
`canonical_ref_digests` updates required by files this cycle changes. Do not attempt
to write a self-referential SHA.

For this cycle the protocol content is **already committed** — it is what commits
`f46093d`, `d9511ae`, and `2f14de3` did. So the semantics commit here may carry only
the unbinding fields plus any digest correction. That is expected, not a shortcut.

**Binding child.** The immediate child writes the semantics commit's full SHA into
`protocol_release_head` and `lane_required_after_protocol_release_head`, sets both
statuses to `bound`, and regenerates release-derived fixtures, suite, and latest
result. It must change no canonical receipt-loaded file.

Commands are in the README `## Verification` section — read them there rather than
from any summary, including this packet.

## 4. Two traps recorded from measurement

1. **"binding-only" does not mean "one file".** The exemplar binding child `c0481ea`
   rewrote a large number of fixture and proof artifacts, because receipts embed the
   release head. The real invariant is that no canonical receipt-loaded file differs
   between the two commits. Do not conclude from the file count that something went
   wrong.
2. **Historical bindings are not uniform.** Of five precedent cycles, three bound to
   the immediately preceding semantics commit and two bound to a later commit in the
   same series (`65fb2a0a`, `028b64be`). Follow the README's rule — bind to the
   semantics parent — but if you build or propose any historical audit over this
   invariant, expect two legitimate exceptions and say so rather than reporting them
   as violations.

## 5. EOL normalization is out of scope

Three existing pins match only after LF normalization while the working tree is CRLF.
The normalization rule is still unwritten and is queued as part of the structural gate
work. **Do not change how digests are computed in this task.** If a digest must be
updated because its file changed in this cycle, compute it the same way the existing
passing pins were computed, and say in the report which way that was.

## 6. Stop conditions

Stop and return `blocked` if: closing the cycle would require changing a
bootstrap-required file's content in the binding child; the fixture regeneration
produces a diff you cannot account for; the receipt-identity test still fails after a
correctly formed pair; any step would require a source push, a history rewrite, or an
adjudication-pending decision; or the working tree contains changes you did not make
and were not described in section 1.

## 7. Reporting

The report at `outputs.primary` states: what you measured before starting, the two
commit SHAs, exactly what each commit changed, the test results with counts you
measured, which normalization the digests used, and anything in this packet that your
measurement contradicted. Publish it to `ai/review/latest` and return
`review_branch_head` in the handoff so an independent reviewer can read it from
GitHub rather than from chat.

Numbers quoted anywhere in this packet were measured by other instances at earlier
heads. Re-measure. Where you disagree, your measurement wins and you say so.
