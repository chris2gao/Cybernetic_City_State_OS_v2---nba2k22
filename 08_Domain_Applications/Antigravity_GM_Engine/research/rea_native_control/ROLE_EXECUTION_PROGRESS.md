# Role Native execution engineering — active work

Task `NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01`, base Draft PR18 `094f1aa641f93dec2277707ad9dbf5bdb0341247`. The complete M0-M5 task is in progress, not accepted or complete.

`role_capabilities.py` adds the first M0 consumer surface: all183 planning requirements remain addressable,50 existing action mappings are reused, unknown bindings remain visible. Native maturity and explicit host-granted role permission are independent. Metadata excludes Native addresses. `get_allowed_values` distinguishes known Coach enums/UI ranges from unknown BenchDepth UI endpoints. It does not fabricate values for other families.

The host constructs `RoleCapabilityProfile` from authenticated identity, not from a model's role claim. `read_role_visible_data` accepts an existing sanitized provider; it checks world/save/generation/season/snapshot and recipient/team scope, projects only explicitly granted fields and rejects Potential keys in selected nested data. This does not prove that arbitrary provider data was sanitized; the host remains responsible for trusted field semantics. No new capture or database implementation is introduced.

Initial checkpoint: three M0 offline tests passed at `2401f00213a51b67d9393a2df1ff7f0ad866e145`; Managed Run/Inspect succeeded for that exact candidate. No new game evidence, UI, Save/Reload or independent review.

Second checkpoint adds `role_batches.py`: immutable decided batches, collection bound to host identities, phase/team/field constraints, explicit bilateral package agreements, conflict and dependency handling, one-call trade coalescing, persistent execution claims and no-replay behavior, independently observed outcome reconciliation. `submit_decided_actions` now recomputes the plan. Details and integration boundaries: [ROLE_BATCH_EXECUTION.md](ROLE_BATCH_EXECUTION.md). Tests use real planner/compiler with fake transport. Run `python -X utf8 -B -m unittest discover -s <this-directory>/tests -p "test_role_*.py" -v`.

Four further logical POE actions and two daily training patch actions now reuse existing Apply paths, giving56 effective mappings versus50 historical mappings. The raw registry has64 actions. All agreed trade variants use direct Process in the role route. No new live effect is claimed. [Training patch contract](TRAINING_PATCH_CONTRACT.md) documents exact inputs and preserved fields; Native units/slot labels remain unknown. `tools/export_role_coverage.py` exports all183 dispositions, not a completion certificate.

Still required: complete M0 parameter cards and production role-data adapter; M1 real context/readback adapter integration and final hardening; M2-M4 real Native discoveries/implementations, including remaining contract/staff/editor/rotation/Playbook and training functionality; M5 full domain coverage and final handoff. Do not describe the orchestration candidate as the complete Native system.

Resume from `01_os/07_content/_runs/run-20261028-role-native-execution-system-001/ONBOARDING_AND_PLAN.md`. Existing success cases must not be replayed. Live tests require a separately approved consolidated scenario list.
