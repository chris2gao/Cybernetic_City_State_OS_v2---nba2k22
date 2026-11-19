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
- **Local Python tests: PASS on fixed source commit `a527cc7f4a96356310635530b45bfabcc24ee5a2`.** Windows 10, Python 3.14.6, isolated `E:\\workspace\\_maintenance\\core-pr37-validation` detached validation worktree; command `python -B -m pytest 01_os/06_execution/task_orchestration -q --disable-warnings --maxfail=1` exited 0 with **171 passed, 8 subtests passed (0.82s)**. Original Core working branch remained unchanged. These are functional **offline** tests; independent review still not performed.
- **Cross-stage regression:** a wider `minimum_operational_loop` pytest run was attempted but did not yield a final test verdict and was stopped. It is **UNVERIFIED**, not PASS.
- **New negative path checks:** Review packet displays proposed extras, but `compile_approved` rejects unbound Host operations. Compiled per-instance parameters are held in a copy and cannot be retargeted by external dictionary mutation or a fact/authorization callback.

- **Host mediation boundary (not universal prerequisite):** this candidate does not intercept arbitrary model Shell/GUI calls. It can only constrain callers that actually route through `compile_approved` with a trusted Human decision lookup, trustworthy immutable capability mappings, current domain facts and separately scoped permission.
- **Human architecture decision:** APPROVED for default `EXECUTION` / separately scoped `DEVELOPMENT` and no autonomous promotion. Evidence: [HUMAN_DECISION_MODE_SEPARATION.md](HUMAN_DECISION_MODE_SEPARATION.md). This is not an approval of any specific task prototype or protected operation.
- **New callable gateway:** `execution_mode_gateway.py` + `test_execution_mode_gateway.py`; mode/scope changes invalidate sessions, development requires Host-side authorization, execution still compiles approved prototype Actions only. This is a **callable-level test**, not a shell sandbox.
- **Human refusal-observability decision:** APPROVED to record mediated denials and assess high/repeated policy refusal rates as possible model–OS friction, not automatic proof. See [supplemental Human decision](HUMAN_DECISION_REFUSAL_OBSERVABILITY.md). Numeric alert thresholds are examples, not Human-selected production limits.
- **Audited gateway:** `execution_decision_audit.py` provides structured Host events, cause separation, JSONL append/read and read-only model/task/route summaries. Local negative tests verify no sensitive input capture, same-event deduplication, optional Host audit sink failure warns once and does not stop authorized operations, and no post-hoc denial of already executed Action. Production Host-level routing and audit coverage are NOT implemented.
- **Human trust-first correction:** APPROVED. OS assumes Agent honesty and accepts voluntary reports for unobservable deviations. Self-report is distinct from Host refusal, not automatic misconduct or failure. [Human decision](HUMAN_DECISION_TRUST_FIRST_AGENT_COOPERATION.md). This supersedes surveillance-first interpretations of earlier proposals while preserving separate permissions for protected actions.
- **Self-report reference:** `agent_self_report.py`, `test_agent_self_report.py`; optional JSONL or existing chat/PRMS evidence, never added to Host refusal metrics. No mandatory global Shell/GUI interception or new approval platform.
- **2026-11-17 R1/R2 remediation:** Both HIGH findings now repaired in source and bounded Windows tests: leaf requires bound ProcedureStep or a Host-matched fixed-version operation document; optional audit failure warns once without blocking otherwise authorized actions. Independent review has NOT yet accepted these changes. [Fixed-source handoff](REMEDIATION_REVIEW_HANDOFF.md).
- **R4 PRMS source adapter:** `prms_review_lookup.py` + tests check exact key/digest/scope and source SHA, with separate Host human-provenance callback. Synthetic explicit review fixture supports compile→execute→Done; actual Core Human mode decision is not accepted as a concrete prototype approval. First real Human-approved prototype remains PENDING; no positive real-E2E assertion.
- **Human prototype semantics:** `PENDING` — mechanism architecture discussed, no specific reusable task prototype accepted. Do not invent approvals.
- **Earlier CLI review attempts (historic):** Claude CLI OAuth 401; read-only Codex CLI blocked by Windows policy. Those attempts had no review result. [Attempt receipt](INDEPENDENT_REVIEW_ATTEMPT.md).
- **New independent source review received (2026-11-17):** `PASS_WITH_GAPS` on fixed source `a527cc7f4a96356310635530b45bfabcc24ee5a2`; R1 and R2 closed within the reference-code scope. R3 remains opt-in Host only; R4 real Human-approved prototype and independent Python E2E remain unverified. The reviewer inspected fixed GitHub source/tests but could not run pytest independently. [Received independent review result](INDEPENDENT_REVIEW_RESULT_20261117.md).
- **Human final acceptance:** `PENDING`.
- **Completion pointer:** Draft PR #37 and this record. Candidate has passed the bounded task-orchestration offline test set and awaits Host-binding verification, semantic review, **not** a deployed system or proven efficiency improvement.

## Required verification before any merge

```powershell
python -m unittest discover -s 01_os/06_execution/task_orchestration -p test_atomic_tasks.py -v
python -m unittest discover -s 01_os/06_execution/task_orchestration -p test_reviewed_prototypes.py -v
python -m unittest discover -s 01_os/06_execution/task_orchestration -p test_review_prototype_cli.py -v
```

Also compare changed paths with allowed scope, verify reviewer semantics and approval provenance, test one generic/non-game prototype proposal through the read-only preview, and demand independent Host-mediated evidence before claiming runtime enforcement. A model following an AGENTS.md rule is **not** a substitute for tool-level prevention.

**Status:** `independent_source_review_PASS_WITH_GAPS`; `human_prototype_acceptance: PENDING`; `master_integration: NOT_AUTHORIZED`; `completion_pointer: https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/pull/37`.


## 2026-11-17 首个真实 Human 原型执行（后续状态，覆盖本文件较早的 PENDING 描述）

- **Human 具体原型已首次批准**：当前会话中 Human 对完整 G/R/A/D、唯一只读映射操作、无额外业务 Ready 和独立结果 Done 明确回复“批准”。准确原型 `core-prms-registry-read-v1`；digest `5bbfdfd45e75b936933922620a81e0c55b645a212b380256447a5c28ba9ce501`。这是单一原型的批准，不等于全部 PR #37 设计或 master 集成授权。
- **持久来源**：`FIRST_PRMS_PROTOTYPE_PROPOSAL.json`、`HUMAN_PROTOTYPE_APPROVAL_20261117.md`、`HUMAN_PROTOTYPE_REVIEWS.json`；后两者含真实 Human 对话批准的摘要及来源文件 SHA256。文件由 Agent 整理并提交，GitHub 提交者身份自身不构成 Human 的独立身份认证。
- **实际 Windows 隔离执行：`LOCAL_READ_ONLY_E2E_PASS`**。固定 Python 源码 `a527cc7f4a96356310635530b45bfabcc24ee5a2`；实际 `PRMSReviewLookup→ExecutionModeGateway.compile_execution→catalog.mapping→Done` 只读闭环。来源校验负例拒绝编译且工具零调用；正例在本地基于真实批准归档的内容校验后执行已有 callable **1 次**。观察到 `READY→ADVANCED→DONE`，`prms_v1` 三项真实注册条目及 Git blob/readback，退出码 0。
- **明确缺口**：回调 `verify_human_source` 此次由执行侧进行**来源文件内容验证**，不是可信 Host 对当前 Human 会话的独立身份认证。此项生产身份绑定仍 `NOT_IMPLEMENTED`。不能写成 R4 生产认证门完全关闭；不能把此次本地 E2E 说成生产 Agent Host 接管。
- **本地重新运行测试**：Windows 隔离工作树在同一固定源码 `a527cc7...` 上执行 `python -B -m pytest 01_os/06_execution/task_orchestration -q --disable-warnings --maxfail=1`，**171 passed、8 subtests passed、退出码 0，0.87s**。这是任务推进侧的真实测试，不是假称独立 reviewer 测试。
- **完整证据**：[FIRST_PRMS_PROTOTYPE_E2E_RESULT_20261117.md](FIRST_PRMS_PROTOTYPE_E2E_RESULT_20261117.md)。历史独立源码审核 `PASS_WITH_GAPS` 保留，R1/R2 不重开；R3 普遍工具拦截不作为本次业务试点前置。
- **状态**：`FIRST_REAL_HUMAN_PROTOTYPE_APPROVED_AND_LOCAL_E2E_DONE`，`HOST_IDENTITY_ATTESTATION_PENDING`，`CORE_PR37_DRAFT_NOT_MERGED`。不新增抽象治理阶段或临时 PRMS 业务函数。
