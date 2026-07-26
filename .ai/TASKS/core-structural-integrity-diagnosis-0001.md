---
task_version: "1.0"
task_id: "human-core-structural-integrity-diagnosis-0001"
title: "Core structural integrity: diagnosis and proposal only"
mode: "plan"
task_level: 1

intent:
  goal: >-
    Produce one diagnosis-and-proposal document for the structural integrity
    defects already found in core, plus a mechanically checkable design for the
    pre-commit structural gate that would have caught them. Change no core-owned
    file and resolve no adjudication-pending question in this task.
  why_now: >-
    Two audits found the same class of defect repeatedly: a hand-maintained
    declaration in core drifting from the tree it declares. The repository has a
    communication-compliance validator but nothing that checks structural
    declarations. Fixing the instances without the gate reproduces them.
  definition_of_done:
    - "Every known issue in section A is re-measured at the executor's own HEAD and its status recorded as confirmed / already-fixed / not-reproducible, with the command used."
    - "Each confirmed issue carries a proposed remedy, the paths it would touch, whether those paths are core-owned, and the resulting domain-merge blast radius."
    - "The two adjudication-pending items in section C are presented as options with consequences, and NOT decided."
    - "A concrete design for the structural gate covers at minimum: core_owned_paths / domain_owned_paths vs actual tree, canonical_ref_digests with an explicit EOL normalization rule, and referenced-path existence."
    - "The relationship between the two independent binding mechanisms (canonical_ref_digests and protocol_release_head) is addressed directly, with a proposal for which is authoritative or how they reconcile."
    - "The correct procedure for redoing a release binding is established from repository evidence and stated, or explicitly reported as not determinable with what is missing named."
    - "Zero tracked files outside outputs.primary are modified. git status on the source branch is unchanged at task end."

outputs:
  primary: ".ai/CODEX_REPORTS/core-structural-integrity-diagnosis-0001.md"

inputs:
  required_refs:
    - ".ai/PROTOCOL.md"
    - ".ai/CODEX_WORK_MECHANISM_PROTOCOL.md"
    - "CORE_MANIFEST.yml"
    - ".ai/load_profiles/backend_executor.md"
    - ".ai/load_profiles/math_mentor_teacher.md"
    - ".ai/communication_compliance/material_event_policy.yml"
    - ".ai/lanes/lane_epoch.yml"
  local_files:
    - "E:/newStand/城邦简报/03_决策档案/2026-07-26_城邦系统初始化与通讯协议加载.md"
    - "E:/newStand/城邦简报/03_决策档案/2026-07-26_引导链断点审计.md"
    - "E:/newStand/城邦简报/03_决策档案/2026-07-26_后端交付通道授权与摘要失配.md"
    - "E:/newStand/城邦简报/03_决策档案/2026-07-26_重构交接报告.md"

scope:
  allowed_actions:
    - "read any repository file"
    - "run read-only git commands"
    - "run .ai/communication_compliance/validate_communication.py without --output"
    - "run the repository unit tests"
    - "write exactly one new file at outputs.primary and publish it to ai/review/latest"
  forbidden_files:
    - "every path listed in CORE_MANIFEST.yml core_owned_paths"
    - ".ai/load_profiles/*.md"
    - ".ai/communication_compliance/material_event_policy.yml"
  forbidden_actions:
    - "any source-branch commit"
    - "any push to master or origin/master"
    - "any history rewrite"
    - "deleting or relocating files under domain_owned_paths"
    - "refreshing any canonical_ref_digests value"
    - "redoing the release binding"

return:
  packet_id: "codex-core-structural-integrity-diagnosis-0001"

completion_policy: "completion_preserving"
---

# Core structural integrity — diagnosis and proposal only

## How to read this packet

This is a **plan-mode, no-hands** task. The single permitted mutation is writing
`outputs.primary` and publishing it to the review branch. Every defect below is
to be analysed and proposed against; none is to be fixed in this task.

The reason is not caution for its own sake. At least two items require a Human
decision that is not yet made. An executor that analyses and repairs in the same
pass returns a diff mixing *repair* with *unadjudicated design change*, and those
cannot be separated afterwards.

**Numbers in this packet are stale by construction.** The counts and SHAs in the
archives were measured at an earlier HEAD by a different instance. Re-measure
every one of them. Where your measurement disagrees with what is written here,
**your measurement wins, and you say so explicitly in the report.** A disagreement
is a finding, not an error to smooth over.

## A. Known issues — do not rediscover these

Two audit documents plus two handover documents (`inputs.local_files`) hold the
evidence and the commands. Read them before starting so this ground is not
re-covered. What they already establish:

1. **Four dangling references in the bootstrap chain.** `AGENTS.md` (core-owned)
   points at Math Mentor paths absent from core, at a roadmap YAML absent from
   core, and gives two evaluator scripts as bare filenames whose real location is
   elsewhere in the tree. `.ai/PROTOCOL.md` prescribes which sections of
   `BRIDGE_SCHEMA.md` to read; that file does not exist. `.ai/USER_UPLOADS/` is
   named as a carrier by three protocols and does not exist.
2. **The root routing table points into another repository.** Its task entries are
   absolute `file:///` URLs into the *teacher* domain, while the referenced task
   files exist locally under `07_Execution_Plans/`. The table is the first entry
   in `core_owned_paths`, so every domain that merges core inherits links pointing
   at teacher.
3. **`CORE_MANIFEST.yml` declares zero and the tree holds hundreds.**
   `domain_owned_paths` is annotated "Core never ships content here." Core tracks
   a substantial number of files under exactly those paths. See section C item 1 —
   this is *not* yours to clean up.
4. **Core-owned files depend on domain-owned paths.** `AGENTS.md` and the routing
   table are core-owned yet hang execution rules and entry points on
   `08_Domain_Applications/` and `02_Protocols/`, both domain-owned.
5. **Antigravity has no protocol role.** `AGENTS.md` and
   `AGENT_WORKING_DISCIPLINE.md` treat it as a backend executor;
   `protocol_role_compatibility` in `.ai/PROTOCOL.md` does not list it under any
   role. By the protocol's own rule — authority comes from role plus Human
   authorization — a partner with no role has no authority.
6. **Two different mandatory read sets for the same event.**
   `.ai/HANDOFF_INIT_PROMPT.md` and `.ai/load_profiles/backend_executor.md` both
   specify what to load at a context boundary, and they do not agree.
7. **`math_mentor_teacher.md` pins four files that do not exist in core.** See
   section C item 2 — also not yours to clean up.
8. **Six specification gaps** where a rule is readable but not executable: the
   review-branch publication authority question, determining whether lane cutover
   is active, the missing EOL normalization rule for digests, the absent
   `lane_instance_id` format and uniqueness rule, the unmaterialised
   `.ai/lanes/<id>/events/` path, and `token_profile_run.v1` fields this
   environment cannot measure.
9. **Who writes `STATE.yml` / `OUTBOX.md` is contradictory.**
   `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md` assigns it to the backend;
   `.ai/PROTOCOL.md` forbids the backend from writing it after lane cutover; and
   whether cutover is active cannot be determined from the files.

## B. Red lines

These are boundaries, not preferences. Crossing one is a stop-and-report event.

1. **Core history is never rewritten.** Every domain shares an ancestor with core.
   One rewrite breaks mergeability for all of them simultaneously and nothing
   repairs it afterwards.
2. **Changing a pinned file requires updating `canonical_ref_digests` in the same
   change.** This has already been missed once in this repository's recent history.
3. **Do not refresh any `canonical_ref_digests` value in this task.** Note the
   correction to the original wording: as of the current HEAD there are **no
   mismatched digests left** — the `AGENTS.md` digest and both `.ai/PROTOCOL.md`
   digests were refreshed in an unpushed commit. The prior values are recoverable
   from `origin/master` and from the archive documents, so the evidence is not
   destroyed, but it is no longer visible in the working tree. **Establishing why
   those digests drifted is a task item; refreshing anything further is not.**
4. **Anything under `core_owned_paths` merges into every domain repository.** A
   broad refactor there manufactures conflicts in every domain at once — and
   merge conflict *is* the mechanism that detects unauthorized domain edits.
   Drowning it disables the detector. Any proposal touching core-owned paths must
   state its blast radius explicitly.
5. **Diagnosis and proposal only.** No repair, no cleanup, no reclassification in
   this task, however obvious it looks.

## C. Two items that look like cleanup and are not

Both are design decisions with materially different consequences. Present the
options and the consequences; do not choose.

1. **Files tracked under `domain_owned_paths`.** The bulk are execution history
   under `.ai/CODEX_REPORTS/` and `.ai/PROGRAM_RUNS/`, inherited from the teacher
   lineage when core was forked. Either the classification is wrong — that history
   is legitimately core's — or the classification is right and core should archive
   and drop it. These lead to opposite manifests and opposite merge behaviour for
   every domain. Re-measure the counts per path; do not trust the numbers quoted
   in the archives.
2. **`.ai/load_profiles/math_mentor_teacher.md`.** Every file it pins is absent
   from core. Either the profile should be deleted from core, or core should not
   carry domain load profiles at all — which is a statement about what
   `.ai/load_profiles/` means, not about one file.

## D. What the report must contain

Write one document at `outputs.primary`, structured as:

1. **Re-measurement table** — every section A item: your measured status, the
   command, and any disagreement with this packet.
2. **Per-issue remedy proposal** — paths touched, core-owned or not, domain blast
   radius, and whether it can be done without crossing section B.
3. **Adjudication-pending items** — section C, options and consequences, no
   recommendation stronger than a stated trade-off.
4. **Structural gate design** — what it checks, how it runs, where it hooks, and
   which section A items it would have caught. Must cover manifest-vs-tree,
   digests with an explicit EOL rule, and referenced-path existence. State what it
   would *not* catch.
5. **The two binding mechanisms** — `canonical_ref_digests` in the load profiles
   and `protocol_release_head` in `material_event_policy.yml` are independent,
   cover overlapping files, and can disagree. Propose which is authoritative, or
   how they reconcile. This is not optional; the current state has one of them red.
6. **Release rebinding procedure** — establish it from repository evidence and
   state it, or report it as not determinable and name exactly what is missing.
   This matters first because it triggers the moment any bound file is touched,
   and right now the correct way to finish that is unknown.
7. **Sequencing** — the order the remedies should be applied in, and which ones
   are blocked on a Human decision.
8. **Evidence boundary** — what you verified this session, what you took from the
   archives without re-verifying, and what remains `not_run`.

## E. Validator baseline

`run-fixtures` has been run and passed fully; the validator itself is healthy. It
checks communication-event compliance and does **not** check any section A item.
The adjacent unit tests are red on release-binding comparison for two paths, and
at least one of those was already red before the current work began. Re-establish
this baseline yourself rather than quoting it — including whether the failure
predates the unpushed commits.

Note that `validate_communication.py` writes files only when `--output` is passed.
Run it without `--output` to keep this task read-only.

## F. Stop conditions

Stop and return `blocked` on: any need to modify a file outside
`outputs.primary`; any requirement for a source-branch commit or push; a section C
item that cannot be described without effectively deciding it; discovery that a
red line has already been crossed in existing history; or contradiction between
this packet and measured repository state that changes the objective rather than
a detail.

Contradictions that change only a detail are reported and worked around — do not
stop for those, and do not silently follow this packet over your own measurement.
