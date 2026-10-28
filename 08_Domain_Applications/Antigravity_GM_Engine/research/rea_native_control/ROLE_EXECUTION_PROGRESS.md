# Role Native execution engineering — active work

Task `NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01`, base Draft PR18 `094f1aa641f93dec2277707ad9dbf5bdb0341247`. The complete M0-M5 task is in progress, not accepted or complete.

`role_capabilities.py` adds the first M0 consumer surface: all183 planning requirements remain addressable,50 existing action mappings are reused, unknown bindings remain visible. Native maturity and explicit host-granted role permission are independent. Metadata excludes Native addresses. `get_allowed_values` distinguishes known Coach enums/UI ranges from unknown BenchDepth UI endpoints. It does not fabricate values for other families.

The host constructs `RoleCapabilityProfile` from authenticated identity, not from a model's role claim. `read_role_visible_data` accepts an existing sanitized provider; it checks world/save/generation/season/snapshot and recipient/team scope, projects only explicitly granted fields and rejects Potential keys in selected nested data. This does not prove that arbitrary provider data was sanitized; the host remains responsible for trusted field semantics. No new capture or database implementation is introduced.

Offline tests: `python -X utf8 -m unittest discover -s <this-directory>/tests -p test_role_capabilities.py -v`. Three tests passed at the initial checkpoint. No new game evidence, UI, Save/Reload or independent review.

Still required: M0 complete parameter cards and phase/target enforcement; submit_decided_actions; M1 immutable batch contracts, agreement validation, conflicts/dependencies and durable no-replay journal; M2-M4 real Native discoveries/implementations; M5 per-requirement disposition and final index synchronization. Do not describe this initial module as a complete service or the overall system.

Resume from `01_os/07_content/_runs/run-20261028-role-native-execution-system-001/ONBOARDING_AND_PLAN.md`. Existing success cases must not be replayed. Live tests require a separately approved consolidated scenario list.
