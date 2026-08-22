---
document_id: os-v2-citystate-local-host-control-baseline-001::human-relay-pointer-00005-v1
task_id: os-v2-citystate-local-host-control-baseline-001
author_endpoint_id: gpt56-localhost-b-foreground-001
author_task_role: localhost_control_baseline_foreground
purpose: Provide the exact corrected v2 Human relay pointer for formal request 00005 without requiring long chat copy-paste.
privacy_class: repository_shareable
---
# Task B / Human Relay Artifact for Formal Request 00005

Human relay instruction: give the receiver only the exact GitHub ref to this document and instruct it to load the `Exact v2 Human relay pointer` mapping below verbatim as the formal receiver-bootstrap pointer. Do not paraphrase, omit, or rewrite any field. This document is a relay carrier only; the formal message remains `messages/gpt56-localhost-b-foreground-001/00005_request.yml`.

## Exact v2 Human relay pointer

```yaml
pointer_contract_version: 2
task_id: os-v2-citystate-local-host-control-baseline-001
message_id: os-v2-citystate-local-host-control-baseline-001::gpt56-localhost-b-foreground-001::00005
carrier: GitHub
exact_path_or_GitHub_ref: 00b0bbe84313a4acf6f0deaf28c64095727d07ef:01_os/_communication/Cybernetic_City_State_OS_v2---core/active/os-v2-citystate-local-host-control-baseline-001/messages/gpt56-localhost-b-foreground-001/00005_request.yml
sender_endpoint_id: gpt56-localhost-b-foreground-001
sender_task_role: localhost_control_baseline_foreground
expected_recipient_endpoint_id: codex-localhost-b-final-acceptance-reviewer-004
expected_recipient_task_role: localhost_control_final_acceptance_review
one_line_routing_purpose: Reproduce Task B Windows acceptance with GitHub truth and read-only local Git
constitution_evidence_ref: constitutions/gpt56-localhost-b-foreground-001/00005.yml
compliance_receipt_ref: receipts/gpt56-localhost-b-foreground-001/00005.yml
receiver_setup:
  collaboration_role: independent_review
  provider: OpenAI
  product: Codex Desktop
  surface: codex_desktop
  model: GPT-5.6 Sol
  reasoning_or_parameter_profile: codex_sol_strongest_exposed
  session_mode: fresh
  isolation_level: fresh_session
  repository_access_mode: GitHub_plus_local_Windows
  repository_or_worktree_requirement: Reconstruct task truth from exact GitHub refs. Use only E:\newStand\study\Cybernetic_City_State_OS_v2 - core for read-only local Git/path evidence; do not fetch, switch, commit, push, or create local Git metadata.
  required_branch_or_sha: dev/os-v2-citystate-local-host-control-baseline-001
  local_files_required: true
  github_publication_required_before_start: true
  communication_carrier: GitHub
  routing_basis_ref: documents/gpt56-localhost-b-foreground-001/00005_codex_windows_git_readonly_acceptance.md
  availability_assumption_or_observation_ref: role_context/codex-localhost-b-final-acceptance-reviewer-004.yml
  limitations:
    - executor_private_context
    - local_Windows_physical_reproduction_required
    - local_Git_metadata_mutation_prohibited_for_this_acceptance
    - no_RDC_dependency
    - no_master_publication
    - do_not_start_Task_C
    - no_force_rebase_squash_amend_or_history_rewrite
```

## Receiver action

1. Fresh-read remote `master` and perform repository-wide always-on bootstrap.
2. Load the exact pointer mapping above without changing any value.
3. Run canonical receiver bootstrap against formal request `00005`.
4. If bootstrap passes, execute only the direct `required_refs` from the formal message, including `documents/gpt56-localhost-b-foreground-001/00005_codex_windows_git_readonly_acceptance.md`.
5. Do not request a Human Task Authority Code for ordinary v2.1 delegated start.
6. Publish the formal result if an authorized GitHub publication transport is available; otherwise return the exact structured result payload with publication explicitly pending foreground materialization.
7. Stop before Task C.
