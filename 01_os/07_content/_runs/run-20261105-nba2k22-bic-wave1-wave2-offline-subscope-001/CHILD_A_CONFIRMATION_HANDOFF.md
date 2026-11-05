# Child A v1 Human decision

This document records the earlier candidate at b96fab3684e39062f073abac5e83a930d485ed62. The current review entry is [STAGE01_OWNER_ADMISSION_HANDOFF.md](STAGE01_OWNER_ADMISSION_HANDOFF.md).

The fixed child A0 v1 approval is bound. The current checkpoint is **PENDING_CHILD_A_CONFIRMATION**.

The single next Human decision is whether to approve the complete child A v1 model `NBA2K22-BIC-W1-W2-OFFLINE-A-001` with normalized Requirement payload SHA-256 `693fede10af802267f3657a4f961b812252449d3ebfc1135527f64b88afe2fda`. Review [the complete child A candidate](01_requirement.yml) and [the seven OFF-SC mappings](ACCEPTANCE_MATRIX.json) together. Its confirmation slot is false with a null reference. The previous provisional digest is superseded.

The child A0 model `NBA2K22-BIC-W1-W2-OFFLINE-A0-001` v1 recomputes to the approved SHA-256 `908827305fd94f67a902e79830f08bebaea5f26dc0aade073f5fe647748a46c9`. Both the A0 confirmation and the child A consensus reference bind the original record at commit `7428864602f7d29ee9620db36b7b975f3e2b70c8`. The exact source path, blob and byte hash are recorded in [the binding inventory](A0_BINDING_INTEGRITY.json). The source copy retains the original Human wording.

The binding uses the fixed Core revision `08d8e534a3438269aa7d7eb1b080ab11c172f462`. Actual `requirement_findings` reaches `stage1_confirmation_binding:requirement_result_A`. Actual `evidence_findings` returns an empty list. The prepared seven artifacts and manifest carry the recomputed transitive hashes. [The verification receipt](A0_BINDING_VERIFICATION.json) identifies the exact tested commit and the archived commands, exit codes and output.

Stage01–07 retain candidate status. Stage04 formal freeze and Stage06/07 execution and acceptance remain pending. The complete Core gate is deferred to an eligible committed Run. Full parent BIC remains incomplete.

The recovery entry is [CHECKPOINT.json](CHECKPOINT.json). PRMS is `NOT_SAVED` and recovery uses the published Git commit. The historical preparation checks remain bound to their earlier candidate.
