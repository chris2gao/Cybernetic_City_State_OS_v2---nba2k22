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


## Second implementation checkpoint

- The expanded PRMS suite now has 41 passing offline tests (full log retained).
- Added strict record contracts/JSON schemas; session revocation, host task and
  operation scopes; refused isolated-session issuance for remote backends.
- Recovery verification binds host-retained plan and current-session choice,
  re-resolves catalogs/bytes and rejects missing mandatory sources.
- Added task-series recovery, source-dependent summary invalidation, idempotent
  full copy, and consumption of already owner-published K2 governance records.
- Added domain body planning/assembly/verification with generic module registries
  and domain-declared module_base, no hardcoded NBA runtime installation path.
- Actual read-only NBA PR18 source integration loaded six requested P04/P09 docs,
  with thirteen candidate modules, zero formal G2; full-source context verified.
  The retained probe is interim evidence, not final managed candidate acceptance.
- Added a separate-process state CLI and combined Core/Role window-recovery
  package, including assignment/task consistency, stale checkpoint diagnostics,
  history selection, source commits and budget blocking. Real GPT/Codex UI-window
  acceptance remains NOT_RUN, and no production claim is made.
- Added real local three-way Core-to-domain merge regression. It preserves 09 and
  contains no live role-state distribution. Fresh Windows clones needed explicit
  core.longpaths; the generator now carries that setting.
- Original 28+20 scenario obligations are frozen in acceptance_contract.json.
  They are not 48 passing tests. Next priority is per-scenario/result accounting,
  remaining protocol fault/permission-negative tests, operator examples, RES
  coverage and exact-candidate managed_verify run/inspect plus final handoff.
- Original context_example.json is now explicitly a READ_MANIFEST_ONLY evidence
  record; its full source bodies are not embedded or mislabelled a standalone
  READY recovery package. Operational guide and implementation decisions added.

Do not mark this task or goal complete. Real platform enforcement/deployment,
model-window acceptance and final independent review remain separate gates. Keep
completing legal implementation and verification work before asking for those
external prerequisites. No state service or master integration is authorized.

## D5 handoff update

The earlier next-work list above is historical. Code candidate
`65c42a1ba0a7b58d3e572ad739f58aa59b274300` now passed all seven managed checks and
inspect: 52 PRMS tests, 44 existing working-set tests, actual pinned GitHub source
loading, isolated CURRENT/checkpoint/takeover/recovery, Core context structure,
model-routing static verification and scaffold syntax. Full L0-L4 selection and
bounded full-history audit, remote protocol fault tests, stable template-upgrade
tests and copy-target independent evolution are included.

`ENGINEERING_HANDOFF.md` and `completion_pointer.json` are the current handoff
entry. The 48 original scenarios and 20 RES rows have actual evidence accounting;
12 required external-scope scenarios remain NOT_RUN. Source implementation is
frozen at the exact code candidate; the later handoff commit changes run evidence
only. External raw attempts remain in the task-local prms-test-logs directory.
The failed global-pytest cleanup attempt remains failed in validation_attempts;
new checks use unique temporary roots. Do not restart or claim all 48 passed.

Next gates are Human authorization of an actual independent state/host trust
boundary, real platform permission and fault tests, real GPT/Codex recovery
windows, and a separate independent review. No autonomous repository creation,
production ingress activation, new model session or master integration is part
of this handoff. The full goal remains incomplete pending those gates.

## B-28 source differential completion

The subsequent code candidate `8690ed15f661181528da451d683390b9ab8ffa15` is now
the verified implementation. It also passed all seven managed checks and inspect.
Candidate module cards retain actual file blobs/directory-tree fingerprints;
comparison revalidates the original catalog, marks changed modules selectively,
and reports missing originals, added entries and filtered sources separately.
The actual-source exercise copies verified PR18 bytes to an isolated Git fixture,
changes only a P09 body, and proves P09 stale while P04 remains valid. Other
uncopied sources stay explicitly missing. No real PR18 ref was mutated.

B-28 is now PASS_PINNED_SOURCE_DIFFERENTIAL_FIXTURE, with its exact proof scope
recorded. Eleven required real-platform/model-window/independent-review scenarios
remain NOT_RUN. The prior 65c42a1b and 27d9a000 checkpoints remain historical;
the current completion pointer, matrix and verification receipt supersede them.

## Copy authorization and template audit update

Code candidate `e432afd2152bf50834b619f09c64ed61ca245017` supersedes the earlier
implementation checkpoints and passed all seven managed checks plus inspect:
55 PRMS tests and 44 existing working-set tests. This was substantive engineering
progress, not a repeat of the outstanding protected-environment status.

Owner review reproduced a copy bypass: a CHECKPOINT-only host capability could
create target CURRENT through copy. Full copy now uses the shared operation guard;
task-restricted sessions need an exact host-bound source role/commit, target role
and approval reference. Copy grants remain revocable. Unpinned source commits
are rejected. A separate counterexample showed reuse of a copied template version
was accepted; copied definitions now have canonical target paths, and both current
and prior template version IDs cannot be silently reused. The target can upgrade
to a new version without changing source bytes. Copy also validates source CURRENT,
owner, checkpoint and active definition before target publication; incomplete
source checkpoints fail COPY_INCOMPLETE without a target ref advance.

The before/after evidence and expected-red test log are indexed by
`copy_safety_audit.json`. These are Owner isolated counterexamples, not independent
review or actual platform permission proof. Eleven original-scope scenarios remain
NOT_RUN; no production authenticated ingress, real state repository, real model
window or master integration has been created or authorized by this continuation.
