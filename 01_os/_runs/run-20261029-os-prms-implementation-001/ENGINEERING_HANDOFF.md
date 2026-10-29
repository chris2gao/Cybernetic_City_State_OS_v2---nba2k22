# OS-PRMS context continuity — engineering closure

Status: **TASK_CLOSED_CONTEXT_CONTINUITY_SCOPE**. Human explicitly confirmed that
correct task-plan-based context management/loading ends this task. A window is a
temporary workbench. Work is normally sequential; Human explicitly requests saving
A before switching to B. This closes that engineering scope; full original product
acceptance and production deployment are not claimed.

Verified code candidate: `26daab91962354e5bc37391e523771e239ada4ed`. Core base:
`446ca66ad48831f5fcdb1af18f37d07619e048c4`. Branch:
`task/os-prms-implementation-20261029`; Draft [PR #10](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/pull/10).
Later delivery commits only update this Run's evidence; their code blobs must match
the verified candidate. No Core/master or domain/master integration was performed.

## Usable task continuity

- Explicit SAVE_TASK_CONTEXT atomically publishes an immutable task plan, progress,
  open work, next steps, retained Human instructions, per-task CURRENT and checkpoint.
  Plan revisions preserve originals. Events and actual Human decisions remain typed.
- Each task has its own durable pointer. Saving B does not overwrite A. A fresh
  workbench needs only state location, role, selected task and its new session ID;
  Core version and loading choices come from the saved task, not the old chat.
- Resume loads B0 and the task-selected Core bodies, saved plan/progress and all
  latest durable task facts. B's business content does not enter A's workbench.
  Checkpoint lag, missing history, stale sources and budget failures stay explicit.
  Resume is read-only and does not silently switch the active assignment.
- task_cli.py produces readable CONTEXT.md and exact machine bundle/plan/choice/
  source evidence. Human relays it. Receiver and ack CLI reread sources and verify
  role/task/session/choice/body bindings. No automatic injection or comprehension
  is asserted. Full role copy also retains usable task contexts without transferring
  operational assignments.

Read `01_os/03_mechanisms/context_management/prms/TASK_CONTINUITY.md` for commands
and input fields. Boot and Registry point to that contract and its foreground CLI.
This is a context-file bridge; formal OS communications keep their canonical owner.

## Evidence

All **8 managed checks**, consumer inspect, **77 PRMS tests** and **44 existing
working-set regression tests** passed for this exact code candidate. The actual
continuity example explicitly saves synthetic A then B in isolated real Git, starts
two fresh Python processes to restore A, verifies receiver file receipts, and
confirms no state mutation. See `task_continuity_example.json` and
`context_continuity_acceptance.json`.

Pinned real NBA source loading remains verified: 13 module candidates, 0 formal
G2, six selected P04/P09 body reads; selective source-change fixture proof remains
separate. D0 planning approval-pointer repair remains remote-verified at
`c58af42455c55bcb0fde668aee393b2b172f9ebe`. No game or REA operation occurred.

`verification_receipt.json` retains actual finished records and raw-log hashes.
`changed_paths.json` lists the full change set. `requirements_coverage.json`
retains the 20 original requirement axes; `acceptance_results.json` retains all
48 original obligations and **11 external-scope NOT_RUN**. Their statuses were not
promoted by the clarified closure. `all_original_acceptance_passed` remains false.

## Independent review response and remaining scope

The Human-relayed initial read-only review is recorded in INDEPENDENT_REVIEW_R1_R2.md.
IR-01 now has dormant callable TrustedIngress -> WriterGate -> GitHub backend code
and fake-transport call-chain tests. IR-02 now denies all unspecified copy grants
and checks the exact source/target/commit/approval tuple. IR-03 now has deterministic
Human-relay export/receive/ack and, additionally, usable per-task workbench recovery.
These are Owner repair results, not independent rereview acceptance.

The local same-principal Git bypass remains possible. The injected host adapter is
IMPLEMENTED_UNVERIFIED_PLATFORM; require_enforced still refuses strong-fencing
claims. No real state repository, credential, identity-provider integration or
service was deployed. Real GitHub/host/model-window experiments and independent
rereview remain future work outside Human's clarified task-closure condition.
Production status: **PRODUCTION_NOT_ACCEPTED**. PR remains Draft for review.

Historical copy counterexamples in copy_safety_audit.json refer to their original
code candidates; current regression evidence is verification_receipt.json and the
new tests. Previous pytest/shared-cleanup and other attempt evidence is preserved.

## Reproduce

```text
git checkout 26daab91962354e5bc37391e523771e239ada4ed
python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py run --repo-root . --candidate 26daab91962354e5bc37391e523771e239ada4ed --plan 01_os/_runs/run-20261029-os-prms-implementation-001/verification_plan.json --attempt <existing-external-parent/new-attempt>
python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py inspect --repo-root . --candidate 26daab91962354e5bc37391e523771e239ada4ed --plan 01_os/_runs/run-20261029-os-prms-implementation-001/verification_plan.json --attempt <same-attempt>
python -B 01_os/06_execution/boot/context_management/prms/continuity_example.py --repo-root .
```

Use a new attempt. Frozen source reading requires existing lawful gh read access;
the task continuity example needs Python/Git and existing project dependencies.
No production environment is necessary for these engineering checks.
