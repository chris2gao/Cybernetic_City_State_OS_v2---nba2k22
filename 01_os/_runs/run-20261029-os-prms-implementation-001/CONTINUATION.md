# Implementation checkpoint — not completion

Task: `os-prms-global-persistent-role-memory-20261028-001`.
Core base: `446ca66ad48831f5fcdb1af18f37d07619e048c4`.
Branch: `task/os-prms-implementation-20261029`. Sole implementation owner: Codex.

## Evidence already obtained

- Approved A-RC02, B-RC01, catalog addendum and execution contract read from pinned
  planning source `3c53fd2e4ea98c7bd99b3c5961134690c4832803`.
- Nineteen source content hashes independently matched their Git blobs; manifest
  in `source_evidence_manifest.json`. Supplement includes the serial roadmap and
  NBA PR18 discovery inputs at `094f1aa641f93dec2277707ad9dbf5bdb0341247`.
- Planning Run approval-pointer repair published/read back at
  `c58af42455c55bcb0fde668aee393b2b172f9ebe`, only `run.yml` changed.
  See `planning_reconciliation.json`. Old history and original approval files retained.
- Actual Core baseline catalog: seven mechanisms, seven workflow stages, seven
  boot manifests, thirteen registries, three optional tools. Exact source blob
  receipts in `g1_baseline_catalog.json`; these counts are snapshots, not constants.
- All six domains' current remote G2 roots uninitialized; NBA PR18 thirteen project
  modules classified as candidates, zero formal G2. See `domain_inventory.json`.
- Twenty-four PRMS offline checks passed at the prior tested working-tree state;
  forty-four existing working-set regressions passed. Raw logs retained under
  `interim_test_logs/`. Later edits require a new candidate verification run.
- Local real-Git CAS competition, interrupted staging, idempotence, fencing
  limitation, role takeover, event/checkpoint recovery, byte-for-byte copy,
  stale detection and scope-reporting tests implemented.
- `context_example.json` is an actual foreground CLI load of frozen Core source,
  not a real GPT new-window recovery or production role-state proof.

## Implementation surfaces

`01_os/06_execution/boot/context_management/prms/`:
source adapters, G1/G2 catalog, load planner/assembler, local Git state protocol,
dormant GitHub Git Database adapter, cooperative WriterGate, event index/memory,
domain scaffolding, explicit CLI and tests. Canonical entry and registry added;
existing boot receives an optional, non-starting extension; `09` ownership added.
New-domain generator invokes domain-only scaffolding when separately executed.
No new real domain or state repository has been created.

## Required continuation before any completion claim

1. Finish requirement-by-requirement implementation audit. Current code is an
   engineering candidate, not the full verified product. In particular verify:
   authenticated host ingress, RoleAssignment permissions versus evidence refs,
   real GitHub transport behavior, session revocation/late-write races,
   source-dependent summaries, full-copy edge cases, G2 owner/publication checks,
   load dependencies and mandatory mechanism triggers, receipt tamper resistance,
   durable indexes and TaskSeries recovery, K1-to-published-K2 integration.
2. Add machine data contracts/validation and meaningful tests for gaps found;
   do not redefine RES-001..020 to match currently implemented behavior.
3. Account for each of the original 28 B scenarios plus 20 CAT scenarios. Offline
   unit checks are not substitutes for GitHub permission tests, real GPT/Codex
   new-window tests, or independent review. No 48-scenario pass claim exists.
4. Bind verification plan to the exact candidate; run managed_verify run/inspect
   and the relevant Core regression/ownership/scaffolding checks. Preserve logs.
5. Keep all legal independent work moving before requesting any real deployment
   prerequisite. No real state repository, credentials, service activation,
   Core master integration or domain master integration is currently authorized.
6. Complete RES coverage, operator guide, deployment prerequisites, scope manifest,
   completion report and independent-review handoff; publish task branch/PR and
   read back. Do not claim final independent acceptance from Owner tests.

## Operating constraints

The original Core checkout is at `E:/newStand/study/Cybernetic_City_State_OS_v2 - core`.
This task uses a separate normal Git worktree because the app-managed worktree
tool refused the source root outside this chat's registered workspace. No attempt
was made to bypass that app limitation; standard Git is authorized by the task.
User subsequently authorized removing exactly `gpt_pre/1.jpg` through `5.jpg`;
those five untracked images were removed and the original checkout is otherwise
unchanged (its master is behind fetched origin/master).

User confirms Antigravity has finished and only this owner is currently working.
Keep tests on task-specific temp roots for repeatability. The earlier global
pytest temp cleanup permission failure was not a product test assertion failure.
No log entry under the three-attempt failure protocol was warranted.

Local mutable state belongs only in temporary isolated Git repositories, never
in the Core distribution tree. Local same-user direct Git bypass was demonstrated;
`require_enforced()` returns `FENCING_NOT_ENFORCEABLE`. No production enforcement
claim may be made until separately authorized platform tests prove the boundary.
