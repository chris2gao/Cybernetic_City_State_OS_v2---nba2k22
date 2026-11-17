# Core OS system upgrade — candidate checkpoint

- **Task:** OS-CORE-HUMAN-REVIEWED-ATOMIC-PROTOTYPES-SYSTEM-UPGRADE-20261116-001
- **Primary outcome:** cross-domain, recursive G/R/A/D prototype design with Human-reviewed **minimal** Ready/Done and concrete operation procedure; reuse via compiled callable and repeated instances; bounded Loop exceptions without runtime scope creep.
- **Branch:** `task/core-human-reviewed-atomic-prototypes-20261116`, from fixed Core master `5806c381c599e817106cbdb7c6352f6156b8cdcc`.
- **Pull request:** https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/pull/37 (Draft; no master merge).
- **Global entry updated:** `AGENT_WORKING_DISCIPLINE.md` §0.1 and `AGENTS.md`.
- **Canonical mechanism:** `01_os/03_mechanisms/task_orchestration/最小任务原型与执行编译契约_v1.md`.
- **Workflow Stage 05 → 06:** both stage README files document human co-design, accepted prototype reuse, prebound actions and INCOMPLETE escalation; does not create Stage08.
- **Implementation:** `reviewed_prototypes.py` + `review_prototype_cli.py` + offline tests. Reuses `atomic_tasks.Executor`, no execution side effects during compilation. Parent digest contains child identities but not the internals of unchanged descendant contracts: only affected child must be re-reviewed.
- **Registry:** `task_orchestration_v1.yml` updated for canonical mechanism, source/test/preview.
- **Scope:** no NBA capture task, no Native Calendar, no T15 restart, no new Core scheduler, no modification to either master.
- **GitHub verification:** Files created/updated through connector and subsequently to be read back. GitHub commit and text checks are not Python execution.
- **Local Python tests: PASS on fixed source commit `3577af05e35f387175bb344f6ab00ff650b0892b`.** Windows 10, Python 3.14.6, isolated `E:\\workspace\\_maintenance\\core-pr37-validation` detached validation worktree; command `python -B -m pytest 01_os/06_execution/task_orchestration -q --disable-warnings --maxfail=1` exited 0 with **142 passed, 8 subtests passed (0.72s)**. Original Core working branch remained unchanged. These are functional **offline** tests; independent review still not performed.
- **Cross-stage regression:** a wider `minimum_operational_loop` pytest run was attempted but did not yield a final test verdict and was stopped. It is **UNVERIFIED**, not PASS.
- **New negative path checks:** Review packet displays proposed extras, but `compile_approved` rejects unbound Host operations. Compiled per-instance parameters are held in a copy and cannot be retargeted by external dictionary mutation or a fact/authorization callback.

- **Trusted Host mandatory next gate:** this candidate does not intercept arbitrary model Shell/GUI calls. It can only constrain callers that actually route through `compile_approved` with a trusted Human decision lookup, trustworthy immutable capability mappings, current domain facts and separately scoped permission.
- **Human architecture decision:** APPROVED for default `EXECUTION` / separately scoped `DEVELOPMENT` and no autonomous promotion. Evidence: [HUMAN_DECISION_MODE_SEPARATION.md](HUMAN_DECISION_MODE_SEPARATION.md). This is not an approval of any specific task prototype or protected operation.
- **New callable gateway:** `execution_mode_gateway.py` + `test_execution_mode_gateway.py`; mode/scope changes invalidate sessions, development requires Host-side authorization, execution still compiles approved prototype Actions only. This is a **callable-level test**, not a shell sandbox.
- **Human prototype semantics:** `PENDING` — mechanism architecture discussed, no specific reusable task prototype accepted. Do not invent approvals.
- **Human final acceptance:** `PENDING`.
- **Completion pointer:** Draft PR #37 and this record. Candidate has passed the bounded task-orchestration offline test set and awaits Host-binding verification, semantic review, **not** a deployed system or proven efficiency improvement.

## Required verification before any merge

```powershell
python -m unittest discover -s 01_os/06_execution/task_orchestration -p test_atomic_tasks.py -v
python -m unittest discover -s 01_os/06_execution/task_orchestration -p test_reviewed_prototypes.py -v
python -m unittest discover -s 01_os/06_execution/task_orchestration -p test_review_prototype_cli.py -v
```

Also compare changed paths with allowed scope, verify reviewer semantics and approval provenance, test one generic/non-game prototype proposal through the read-only preview, and demand independent Host-mediated evidence before claiming runtime enforcement. A model following an AGENTS.md rule is **not** a substitute for tool-level prevention.

**Status:** `candidate_pending_validation`; `human_acceptance: PENDING`; `completion_pointer: https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/pull/37`.
