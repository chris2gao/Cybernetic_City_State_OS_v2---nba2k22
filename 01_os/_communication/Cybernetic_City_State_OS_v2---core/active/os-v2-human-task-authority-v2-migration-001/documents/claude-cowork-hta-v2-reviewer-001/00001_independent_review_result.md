---
document_id: os-v2-human-task-authority-v2-migration-001::independent-review-result-00001
task_id: os-v2-human-task-authority-v2-migration-001
author_endpoint_id: claude-cowork-hta-v2-reviewer-001
author_task_role: authority_v2_independent_review
purpose: Independent falsification review result for the exact Human Task Authority v2 migration semantic candidate.
privacy_class: repository_shareable
---
# Independent review result

Primary verdict: **ready_for_human_integration**. No blocking finding.

Reviewed exactly `231347d36bb5a7d929516df6a15273edf3902c61`, parent
`857c667547c93e9b9c3c26ed1316db38919a25a3`. Later commits `c803e2a6`, `08a7975b` and
`026b40fe` were read only for provenance and were not treated as candidate content.

# Reviewer independence disclosure

The candidate executor was OpenAI GPT-5.6 Sol. This reviewer is Anthropic Claude Opus 5 in a
fresh isolated session, distinct endpoint, GitHub-only reconstruction, no executor private
context and no prior reviewer chat. This review is therefore cross-model-family and satisfies
the stricter pre-migration rule that still governs until this candidate reaches master. The
relaxation of that rule proposed by the candidate was not relied upon to conduct this review.

# Predecessor review state

A previous independent reviewer was interrupted. Recomputed from durable repository evidence:
the task communication root contains only foreground-owned artifacts plus the two
dispatcher-prepared reviewer files (`endpoints/claude-cowork-hta-v2-reviewer-001.yml`,
`role_context/claude-cowork-hta-v2-reviewer-001.yml`). There is no reviewer message, index,
constitution, receipt, document, partial review or checkpoint anywhere on the branch, and
`08_结论/completion_pointer_v1.yml` records `result_status: pending`. No durable reviewer
checkpoint existed to inherit, so this review was rebuilt in full from the formal request.

Post-dispatch semantic mutation check: the only path changed between the candidate and branch
HEAD outside this task's communication and run directories is
`01_os/_communication/Cybernetic_City_State_OS_v2---core/discovery.yml`, which gains one entry
registering this task root in `active_task_roots`. That is navigation registration, not
semantic authority content. The semantic candidate is unchanged since dispatch.

# Independently verified scope

- Candidate parent equals the expected base and equals current remote `master`.
- 23 changed paths, 938 insertions, 302 deletions, 0 binary artifacts.
- `git diff --check` across base to candidate: exit 0.
- Fresh remote read at review time: `master` `857c667547c93e9b9c3c26ed1316db38919a25a3`,
  branch `026b40fe909009e7006c14b4efd90f2485d84ff6`. Both match the stated known state, so no
  drift needed explaining.

# Falsification results

## Independently constructed attack harness

This reviewer wrote an independent harness against
`CommunicationValidator.validate_recipient_delegation` at the candidate SHA. It is not derived
from the executor's tests. Sixteen cases: one control that must be accepted, fifteen attacks
that must be rejected. All sixteen behaved correctly.

| Attack | Validator response |
|:--|:--|
| control: well-formed root delegation | ACCEPTED |
| forged root delegator not equal to Human-bound holder | `root_delegator_not_Human_bound_holder` |
| cross-task replay | `authorization_v2_not_live` |
| scope escalation beyond Human task scope | `delegation_exceeds_Human_task_scope` |
| revoked delegation | `authorization_v2_not_live` |
| `granted: false` delegation | `authorization_v2_not_live` |
| self-delegation | `self_delegation_prohibited` |
| recipient mismatch | `authorization_v2_recipient_mismatch` |
| cross-action replay | `authorization_v2_action_not_delegated` |
| redelegation without parent permission | `redelegation_not_granted` |
| redelegation action expansion | `redelegation_action_expansion` |
| revoked parent in chain | `authorization_v2_not_live` |
| delegation ref omitted from `required_refs` | `recipient_delegation_ref_not_in_required_refs` |
| revoked Human task authority at root | `Human_task_authority_v2_invalid` |
| v1-scheme commitment used as a v2 root | `Human_task_authority_v2_invalid` |
| path traversal in delegation ref | `authorization_ref_noncanonical` |

The control case being accepted matters: the harness is discriminating, not rejecting
everything.

## Cryptographic separation, verified by reading the construction

`_canonical_payload` places the scheme string in `payload["domain"]` and binds `task_id` and
`task_authority_id` into the hashed payload. Consequences, verified by reading
`verify_stage_collaborative_deliberation.py` at the candidate rather than inferred from
documentation:

- A v1 preimage cannot produce a v2 digest, because the domain string differs inside the hash.
  Cross-version replay is blocked cryptographically, not merely by a field comparison.
- A code bound to one task cannot produce a valid digest for another task.
- Within one task, each decision event binds `stage_id`, `decision_id`, `decision_type`,
  `exact_model_version` and `authorized_scope`, so one task code supports many events while
  each event keeps an exact distinct binding. Falsification question 1 answers affirmatively.
- `validate_commitment_structure` returns 14 if a commitment mapping carries `Human_nonce`,
  `nonce`, `plaintext` or `code`, which is an explicit plaintext-leakage guard.

## v1 to v2 cutover

`LEGACY_HUMAN_AUTHORITY_SCHEME`, `LEGACY_COMMITMENT_BOUND_FIELDS` and
`compute_legacy_commitment` are retained. `validate_commitment_structure` accepts both schemes
by default, and `validate_authority_record_commitments` dispatches on the record's own scheme,
requiring v2 records to carry both a task commitment and an event commitment under the v2
scheme while validating v1 records under the v1 scheme only. The protected-action path in
`validate_communication_system.py` keeps an explicit legacy branch for historical v1 direct
Human authorization. Legacy verification therefore remains physically usable before master
integration, and the two regimes cannot be confused for one another. No dual-authority or
no-authority window was found.

## Repository integration

All 55 exact `blob_sha` pins in the stage boot manifest and the seven workflow profile
reference files were recomputed against the candidate tree: 0 stale, 0 missing targets. The
two pins that changed are exactly the two files whose content changed.

An independent scan of the candidate tree for a persisted plaintext code field
(`Human_nonce:`, `plaintext_code:`, `task_authority_code:`, `authorization_code:`) found none.
Only `*_plaintext_stored: false` flags and prose statements are present.

The candidate does not touch `01_os/05_registry/repository_publisher_authority_v1.yml`, the
`.githooks/` guards or any secrets surface, so publisher authority and protected-action
controls outside this validator are unchanged. Human override semantics are strengthened
rather than weakened: `角色与权限边界_v1.yml` now states `root_authority: current_Human`,
`grants_authority: false` for roles, `validator_grants_authority: false`, and
`model_provider_role_or_code_possession_alone_authorizes: false`.

## Review isolation

`AGENT_WORKING_DISCIPLINE.md` changes rule 1 from an absolute cross-family requirement to a
relationship-isolation requirement, with cross-family preferred and same-family permitted only
when explicitly selected and disclosed as a limitation. Rule 2, that the author does not design
the verification of their own work, is preserved and made explicit about endpoint, session and
private-context isolation. This does not create a self-review path: the author bar is unchanged
and the isolation conditions are conjunctive. It is a real relaxation of a previously absolute
rule, it matches the Human-confirmed design, and it is disclosed rather than silent.

# Independent reproduction versus executor self-report

Independently reproduced at the candidate SHA in a clean isolated worktree:

- focused authority v2 test: PASS, exit 0
- communication validator unit tests: 25 passed, exit 0, matching the executor's claim
- `git diff --check`: exit 0
- binary artifact count: 0
- 55 exact blob pins: 0 stale
- the 16-case falsification harness above

`NOT_RUN` by this reviewer, and therefore still executor self-report rather than independent
PASS: `stage_runtime_guard_exit_code`, `stage_static_exit_code`,
`communication_static_exit_code` and `master_v1_current_model_readiness_exit`. These were not
reproduced here and must not be recorded as independently verified.

# Non-blocking findings

1. **GitHub receiver bootstrap does not re-validate the delegation chain.**
   `receiver_bootstrap.py:139` calls `validate_message(message, message_path=..., cards=cards)`
   without `task_root`. `validate_recipient_delegation` is invoked only inside
   `if task_root is not None:` in `validate_message`, so in GitHub pointer mode the recipient
   delegation chain is not re-checked. Publication-time validation does cover it
   (`publish_message.py:343` and `republish_github.py:117` both pass `task_root`), and the
   binding gate against an adversary with Git write is the out-of-band Human code challenge,
   so this is a defense-in-depth gap rather than an authority bypass. It is nonetheless worth
   closing, because the receiver-bootstrap contract elsewhere requires the receiver to replay
   validation rather than trust the sender. A blob-reading chain validator for GitHub mode
   would close it.

2. **The root authority document is format-checked, not Human-checked, at message validation
   time.** `_validate_Human_task_authority_v2` verifies that the commitment is a 64-hex sha256
   digest under the v2 scheme; it does not and cannot verify the digest against a live Human
   secret, because the plaintext code must never persist. An actor with Git write can therefore
   author a syntactically valid root document. The binding check is the separate challenge tool
   run against the current Human. This is disclosed in the candidate's `known_limits`. It is
   recorded here so that no later reader treats a validator `VERIFIED` as evidence that a Human
   was actually consulted.

3. **Root-level `authorized_actions` are bounded by Human `task_authority_scope` but not by any
   Human-declared action list.** Child delegations must narrow both actions and scope, and every
   node's scope must be a subset of the Human task scope, but the initial holder chooses the
   action vocabulary. This matches the confirmed design, in which the Human binds scope and the
   dispatcher allocates actions inside it. Recorded as a design property, not a defect.

4. **Pre-existing local Git identity in the provenance record.** The candidate's validation
   summary reports `observed_local_git_identity: Fixture <fixture@example.invalid>` and marks it
   `pre_existing_configuration: true, changed_by_this_task: false`. Independent of this review's
   scope, but worth a housekeeping pass before further publication work.

5. **No CI.** The repository has no `.github/` workflows, so every test result in this task is
   a local executor or local reviewer run. This review's reproductions are local-reviewer
   evidence, not CI evidence.

# Blocking findings

None. Against the pragmatic blocking standard: Human authority is not forgeable by a model
without also defeating the out-of-band challenge, delegation and challenge are not bypassable
through the sanctioned paths, cross-task and cross-scope and cross-action replay are rejected
both structurally and cryptographically, isolation is not substantively defeated and this very
review is cross-family, the v1 to v2 cutover is correct and reversible-safe before integration,
Human root authority is strengthened rather than weakened, protected-action authority outside
this validator is untouched, the candidate matches the Human-confirmed architecture, and the
candidate sits on the current master as a clean fast-forward base.

# What this review did not do

No implementation, no fix, no modification of the semantic candidate, no master modification,
no merge, no force push, no rebase, squash, amend or reset. All recomputation used read-only
`git show` and `git diff` at exact SHAs plus isolated worktrees outside the shared clone.
