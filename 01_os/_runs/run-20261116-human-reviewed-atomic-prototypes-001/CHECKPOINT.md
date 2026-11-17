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
- **Local Python tests: PASS on fixed source commit `fd6bac894ee2dc7fff2379ef8ca5c5af02753550`.** Windows 10, Python 3.14.6, isolated `E:\\workspace\\_maintenance\\core-pr37-validation` detached validation worktree; command `python -B -m pytest 01_os/06_execution/task_orchestration -q --disable-warnings --maxfail=1` exited 0 with **171 passed, 8 subtests passed (0.86s)**. Original Core working branch remained unchanged. These are functional **offline** tests; independent review still not performed.
- **Cross-stage regression:** a wider `minimum_operational_loop` pytest run was attempted but did not yield a final test verdict and was stopped. It is **UNVERIFIED**, not PASS.
- **New negative path checks:** Review packet displays proposed extras, but `compile_approved` rejects unbound Host operations. Compiled per-instance parameters are held in a copy and cannot be retargeted by external dictionary mutation or a fact/authorization callback.

- **Trusted Host mandatory next gate:** this candidate does not intercept arbitrary model Shell/GUI calls. It can only constrain callers that actually route through `compile_approved` with a trusted Human decision lookup, trustworthy immutable capability mappings, current domain facts and separately scoped permission.
- **Human architecture decision:** APPROVED for default `EXECUTION` / separately scoped `DEVELOPMENT` and no autonomous promotion. Evidence: [HUMAN_DECISION_MODE_SEPARATION.md](HUMAN_DECISION_MODE_SEPARATION.md). This is not an approval of any specific task prototype or protected operation.
- **New callable gateway:** `execution_mode_gateway.py` + `test_execution_mode_gateway.py`; mode/scope changes invalidate sessions, development requires Host-side authorization, execution still compiles approved prototype Actions only. This is a **callable-level test**, not a shell sandbox.
- **Human refusal-observability decision:** APPROVED to record mediated denials and assess high/repeated policy refusal rates as possible model–OS friction, not automatic proof. See [supplemental Human decision](HUMAN_DECISION_REFUSAL_OBSERVABILITY.md). Numeric alert thresholds are examples, not Human-selected production limits.
- **Audited gateway:** `execution_decision_audit.py` provides structured Host events, cause separation, JSONL append/read and read-only model/task/route summaries. Local negative tests verify no sensitive input capture, same-event deduplication, optional Host audit sink failure warns once and does not stop authorized operations, and no post-hoc denial of already executed Action. Production Host-level routing and audit coverage are NOT implemented.
- **Human trust-first correction:** APPROVED. OS assumes Agent honesty and accepts voluntary reports for unobservable deviations. Self-report is distinct from Host refusal, not automatic misconduct or failure. [Human decision](HUMAN_DECISION_TRUST_FIRST_AGENT_COOPERATION.md). This supersedes surveillance-first interpretations of earlier proposals while preserving separate permissions for protected actions.
- **Self-report reference:** `agent_self_report.py`, `test_agent_self_report.py`; optional JSONL or existing chat/PRMS evidence, never added to Host refusal metrics. No mandatory global Shell/GUI interception or new approval platform.
- **2026-11-17 R1/R2 remediation:** Both HIGH findings now repaired in source and bounded Windows tests: leaf requires bound ProcedureStep or a Host-matched fixed-version operation document; optional audit failure warns once without blocking otherwise authorized actions. Independent review has NOT yet accepted these changes. [Fixed-source handoff](REMEDIATION_REVIEW_HANDOFF.md).
- **R4 PRMS source adapter:** `prms_review_lookup.py` + tests check exact key/digest/scope and source SHA, with separate Host human-provenance callback. Synthetic explicit review fixture supports compile→execute→Done; actual Core Human mode decision is not accepted as a concrete prototype approval. First real Human-approved prototype remains PENDING; no positive real-E2E assertion.
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
