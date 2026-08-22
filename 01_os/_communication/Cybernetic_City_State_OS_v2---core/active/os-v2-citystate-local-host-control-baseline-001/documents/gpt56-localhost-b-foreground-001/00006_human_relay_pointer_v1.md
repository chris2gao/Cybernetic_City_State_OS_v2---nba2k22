---
document_id: os-v2-citystate-local-host-control-baseline-001::human-relay-pointer-00006-v1
task_id: os-v2-citystate-local-host-control-baseline-001
author_endpoint_id: gpt56-localhost-b-foreground-001
author_task_role: localhost_control_baseline_foreground
purpose: Provide the machine-bound v2 Human relay pointer for Task B post-integration local synchronization and cleanup without long chat copy-paste.
privacy_class: repository_shareable
---
# Task B / Human relay artifact for formal request 00006

Human relay instruction: give the receiver only the exact GitHub ref to this document and instruct it to load the `Exact v2 Human relay pointer` mapping below verbatim as the formal receiver-bootstrap pointer. Do not paraphrase, omit, rewrite, or reconstruct any field.

This document is a relay carrier only. The formal message remains `messages/gpt56-localhost-b-foreground-001/00006_request.yml` at immutable dispatch commit `d778aaa3cfe47ee0c0202cdd2d77df0ff06ad94b`.

## Exact v2 Human relay pointer

```yaml
pointer_contract_version: 2
task_id: os-v2-citystate-local-host-control-baseline-001
message_id: os-v2-citystate-local-host-control-baseline-001::gpt56-localhost-b-foreground-001::00006
carrier: GitHub
exact_path_or_GitHub_ref: d778aaa3cfe47ee0c0202cdd2d77df0ff06ad94b:01_os/_communication/Cybernetic_City_State_OS_v2---core/active/os-v2-citystate-local-host-control-baseline-001/messages/gpt56-localhost-b-foreground-001/00006_request.yml
sender_endpoint_id: gpt56-localhost-b-foreground-001
sender_task_role: localhost_control_baseline_foreground
expected_recipient_endpoint_id: codex-localhost-b-completion-cleanup-executor-005
expected_recipient_task_role: localhost_control_completion_cleanup_execution
one_line_routing_purpose: Synchronize Task B Windows anchor and safely clean merged Task B local state
constitution_evidence_ref: constitutions/gpt56-localhost-b-foreground-001/00006.yml
compliance_receipt_ref: receipts/gpt56-localhost-b-foreground-001/00006.yml
receiver_setup:
  collaboration_role: auxiliary_mechanical
  provider: OpenAI
  product: Codex Desktop
  surface: codex_desktop
  model: GPT-5.6 Terra
  reasoning_or_parameter_profile: codex_terra_task_fit
  session_mode: fresh
  isolation_level: fresh_session
  repository_access_mode: GitHub_plus_local_Windows
  repository_or_worktree_requirement: Use only E:\newStand\study\Cybernetic_City_State_OS_v2 - core as the canonical repository anchor. Synchronize local master by ordinary non-destructive Git only. Inspect and remove only the exact merged Task B worktree/branch when safe; preserve the E:\_pubwork parent and all unrelated/Task C material.
  required_branch_or_sha: master
  local_files_required: true
  github_publication_required_before_start: true
  communication_carrier: GitHub
  routing_basis_ref: documents/gpt56-localhost-b-foreground-001/00006_local_completion_cleanup.md
  availability_assumption_or_observation_ref: role_context/codex-localhost-b-completion-cleanup-executor-005.yml
  limitations:
  - auxiliary_mechanical_only
  - no_acceptance_retest
  - no_RDC_dependency
  - ACL_preflight_before_Task_B_worktree_removal
  - stop_on_abnormal_ACL_or_unrelated_local_changes
  - preserve_E_drive_pubwork_parent_and_unrelated_or_Task_C_material
  - no_force_rebase_squash_amend_or_history_rewrite
  - no_secrets_credentials_admin_escalation_or_system_security_changes
  - no_master_publication
  - do_not_start_Task_C
```

## Receiver action

1. Fresh-read remote `master` and run the repository-wide always-on bootstrap.
2. Load the exact pointer mapping above verbatim and run canonical receiver bootstrap.
3. Validate current Task Authority v2 and live delegation `Human/delegations/00006_completion_cleanup.yml`; do not request a Human task code.
4. If and only if bootstrap passes, execute `documents/gpt56-localhost-b-foreground-001/00006_local_completion_cleanup.md`.
5. This is auxiliary completion housekeeping only: no acceptance rerun, no master publication, no Task C.
6. Publish one formal result to the Task B branch when an authenticated GitHub transport is available, then stop.
