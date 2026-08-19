---
document_id: os-v2-citystate-local-host-control-program-design-001::independent-review-result-00001
task_id: os-v2-citystate-local-host-control-program-design-001
author_endpoint_id: claude-cowork-citystate-program-reviewer-001
author_task_role: program_design_independent_review
purpose: Independent review result for the exact CityState A/B/C program-design semantic candidate.
privacy_class: repository_shareable
---
# Independent review result

Verdict: **ready_for_human_integration**, with one authority-sequencing item the Human must
decide before any subsequent round. The candidate itself requires no changes.

Reviewed exactly `3248912d182c3f185378af9e003f4ac21b9e0b6a`. The later metadata and
communication commits on this branch (`9c55aa3e`, `36f6fddd`, `2b6b8d43`, `6f7bb609`) were
read only for provenance checking and were not treated as candidate content.

# Scope recomputed from the repository, not from executor self-report

- The candidate parent is `536995889b0b33cd050a520e31fdafd32151153c`, which equals the
  current remote `master`. The declared `base_sha` is therefore true and the candidate sits
  on a clean fast-forward base.
- 11 files, 691 insertions, 0 deletions, 0 binary artifacts.
- Every changed path is under
  `01_os/_runs/run-20260818-citystate-local-host-control-program-design-001/`.
  No canonical file and no registry file is touched. Under section 4 of the OS entry,
  `01_os/_runs/**` is not registered, so this candidate triggers no registry-synchronisation
  obligation. `canonical_implementation_changes: 0` was confirmed by path inspection rather
  than accepted from the completion pointer.

# Primary questions

## Q1 Topology: exactly A/B/C, Task C exactly two stages - PASS

Cross-checked in four independent places: `program_shape.major_tasks_exactly` (3),
`task_C.major_stages_exactly` (2), `validation_summary` (3 / 2), and
`final_program_acceptance`. `no_micro_phase_expansion: true` guards against later expansion.

## Q2 Task A durable but freshness-aware - PASS

The stable/volatile split is not only stated, it is enforced at acceptance: `non_goals`
explicitly refuses to freeze the volatile directory as permanent truth, and acceptance
requires dated attributable fresh-search evidence, requires category files to separate stable
guidance from volatile snapshot facts, and forbids promoting any availability claim from chat
memory.

## Q3 Task B: proven local-host capability into a long-lived contract - PASS

- Unicode: `Git -z` to raw bytes to strict UTF-8 to filesystem Path;
  `terminal_text_is_not_path_fact`;
  `PowerShell_console_codepage_is_not_a_correctness_control`; acceptance requires that hostile
  `quotePath` settings not alter path-ledger correctness.
- ACL and worktree hygiene: ACL preflight before worktree removal, and abnormal ACL behaviour
  must fail before mutation and return to the Human.
- Cache: disposable pytest defaults to `-p no:cacheprovider`; acceptance forbids creating an
  unreadable cache.
- GUI separation: `general_GUI_computer_use: not_proven_and_not_required_for_baseline`,
  consistent with the probe's `not_proven` list. The probe artifact additionally records that
  the Human disabled Computer Use and that the artifact must not be used as authority for
  further Computer Use tests.

Independent corroboration by this reviewer, from first-hand measurement on the same
workstation on the same day rather than from executor report:

- PowerShell 5.1 reads a BOM-less UTF-8 script under cp936 and corrupts CJK literals
  (match false), while PowerShell 7 reads the same file correctly (match true).
- With `[Console]::OutputEncoding = gb2312`, one Chinese repository path degrades from
  93 characters / 143 bytes to 105 characters / 180 bytes, and the ASCII character following
  a CJK character is absorbed into a double-byte character. The figures are identical under
  PowerShell 5.1 and PowerShell 7, which shows the defect is decided by the console code page
  and not by the host.
- The `_git_blob` defect fixed on master the same day belongs to exactly the failure class
  this contract is designed to prevent: `subprocess` decoded with the process locale, the
  `UnicodeDecodeError` was raised inside the reader thread and did not propagate, the return
  code stayed 0, stdout became `None`, and the symptom surfaced as `yaml_input_must_be_text`.

The load-bearing premise of the Task B contract is therefore confirmed by independent
measurement, not merely asserted by the design.

## Q4 Task C: entitlement before VPS, argosbx boundary, ingress separation - PASS

- `entitlement_gate_first: true` and `C2_must_not_start_on_blocked_C1: true`. On C1 BLOCK,
  both VPS mutation and production build are prohibited.
- The rationale correctly separates "the vendor plugin has write capability" from "a
  user-created custom MCP has write capability". This is the sharpest and most load-bearing
  distinction in the candidate.
- Preservation boundary: `default_no_touch` covers `/root/agsbx/**`, the three services,
  firewall state and existing listeners. Mutation requires prior `ss`, systemd,
  `iptables-save`, `ip6tables-save` and `nft` snapshots, and afterwards requires comparison
  against baseline with zero unintended delta to protected services, ports, routing and
  firewall.
- Separation is coherent: a dedicated CityState Named Tunnel that explicitly does not reuse
  the existing argosbx tunnel, loopback-only VPS origin on 127.0.0.1:18080, reverse bridge on
  127.0.0.1:18181, the Edge owning external contract, authentication, audit and filtering,
  and the Local Agent as a local execution adapter only. Desktop Commander is bound as
  `local_adapter_not_remote_control_plane`.

## Q5 Dependencies, stop conditions, protected actions, gates - PASS with one gap

All three tasks are `planned_not_yet_executable` and require, at activation, a freshly
resolved remote `master` SHA, a fresh task packet and fresh Human stage authority. C2
additionally requires C1 PASS, Task B complete, a ready hostname and fresh authorization for
runtime and network mutation. Prior chat is explicitly refused as proof of current product
entitlement or VPS state. The gap is finding 1.

# Findings

## Finding 1 - blocking for the next round, not for the candidate

The authorization the candidate rests on has been invalidated, and no live authorization
currently covers a change round.

`02_dangqian/Human authorization v1` reads `stale: false` and `invalidated: false` inside the
candidate. The same file at branch head reads `stale: true`, `invalidated: true`,
`invalidated_by: D-CITYSTATE-PROGRAM-DESIGN-001-FORMAL-REVIEW-SCOPE`, which is the decision
that dispatched this review. The superseding authorization covers only publishing this review
communication context and reviewing `3248912d`, and forbids modifying master or implementing
A/B/C.

Consequence: had this review returned `changes_required`, no authorization in force would
permit those changes to be made. This does not retroactively invalidate the artifact, since
the candidate was produced while v1 was live and `consumed_by` records it, but it is a hard
constraint on what may happen next. It is reported as a conflict for the Human to resolve
rather than silently resolved here.

## Finding 2 - non-blocking, provenance

The review dispatch authorization carries a `durable_authority_ref` pointing at Human
authorization v2 under the run directory. That path does not exist at the reviewed commit
`3248912d`; it exists only at branch head. The reference is legitimate in itself, because it
is the authority for the dispatch rather than for the candidate, but under the
`GitHub_only_reconstruction` constraint a reviewer working strictly from the candidate SHA
cannot resolve it. A durable authority reference should resolve at the commit against which
it is cited.

## Finding 3 - non-blocking, routing coherence

Tasks A, B and C share one `preferred_receiver_setup_at_activation` profile
(GPT-5.6 Sol on `chatgpt_web`). Task B declares `local_files_required: true` and
`repository_access_mode: local_git_with_GitHub_readback`, so a web surface is expected to
drive local host control. The stated mitigations are that the route must be revalidated at
activation and that the local device must be observed online at activation; the latter
constrains the device, not whether the executor surface can reach it. The dependency is
acknowledged indirectly in C2 acceptance, which forbids retiring the vendor Remote Desktop
Commander relay before end-to-end acceptance passes, but it does not appear in Task B's own
`start_condition`. Suggest stating the required local channel explicitly there.

## Finding 4 - non-blocking, evidence-grade boundary

The external evidence for OpenAI entitlement, the MCP Python SDK, the MCP 2026-07-28 protocol
and Cloudflare Tunnel is well formed: dated, with locators and explicit `invalidation`
conditions. Under `GitHub_only_reconstruction` this review did not verify those claims against
their external sources, so they remain executor observations. The design contains that risk by
requiring C1 to re-verify entitlement at activation, so it is not blocking. The evidence grade
must not be promoted to verified fact on the strength of this review.

## Finding 5 - non-blocking, observation

`DNS_current_state: propagation_pending_or_not_reverified_in_this_task` is honest
self-labelling and is contained by activating the production hostname only after C1 PASS and
C2 authorization. No action.

# Positive fact that belongs in the record

On meeting a boundary conflict the executor did not silently widen scope. It produced a
formal dispatch boundary defect record stating the conflict, the mechanical remedy that would
require Human authorization, and a `not_done` list, and recorded `resolution` only after new
Human authority existed, binding the exact pointer commit. This is the behaviour section 4 of
`AGENT_WORKING_DISCIPLINE.md` requires. Reviews usually record only negatives; this is
recorded deliberately.

# What this review did not do

No implementation, no master modification, no worktree in the shared clone, no checkout of
the shared working tree. All recomputation was performed with read-only `git show` and
`git diff` against exact SHAs.
