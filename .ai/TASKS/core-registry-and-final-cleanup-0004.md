---
task_version: "1.0"
task_id: "human-core-registry-and-final-cleanup-0004"
title: "Build the mechanism registry, then use it to finish the cleanup"
mode: "goal"
task_level: 2

intent:
  goal: >-
    Produce a durable machine-readable registry of every mechanism in this repository -
    what loads it, which paths it needs, which cache directories it writes, and when a
    breakage would surface - then use that registry, not a fresh reachability pass, to
    identify and remove what remains unused, cleaning chained references in the same
    commit.
  why_now: >-
    Deciding whether one file may be deleted currently costs an archaeology session:
    reference counts, bootstrap trigger conditions, load profiles. That cost was paid
    three times today for three files. Twice a closure deleted something no reference
    could reveal - the agent permission policy and the runner ignore policy - and both
    were found by accident. A registry converts every future instance of that question
    into a lookup.
  definition_of_done:
    - "A registry artifact exists listing every mechanism with loader, discovery mechanism, exact path set, cache/scratch directories, and failure-surfacing time."
    - "The registry is assembled from the existing 0002 closure and 0003 audit; no new reachability computation is performed."
    - "Every path in the protected list of section 4 appears in the registry and is not deleted."
    - "Deletion candidates are derived from the registry, and each carries its referencing files and the chained edits its removal requires."
    - "Deletions and their chained reference cleanups land together, so no link points at a file that no longer exists."
    - "After deletion the unit suite passes, run-fixtures passes, the release binding is green, and indexes plus repository_index_manifest.json are regenerated."

outputs:
  primary: ".ai/CODEX_REPORTS/core-registry-and-final-cleanup-0004.md"
  additional:
    - ".ai/MECHANISM_REGISTRY.yml"

inputs:
  required_refs:
    - "CORE_MANIFEST.yml"
    - "06_Silicon_Index/AI_Bootstrap_Sequence.md"
    - ".ai/communication_compliance/material_event_policy.yml"
    - "ai/review/latest:.ai/CODEX_REPORTS/core-mechanism-reachability-cleanup-0002-closure.json"
    - "ai/review/latest:.ai/CODEX_REPORTS/core-mechanism-file-audit-0003.md"

scope:
  allowed_actions:
    - "read tracked repository files; run read-only git; run the test suites"
    - "create the registry artifact"
    - "delete the paths authorized in section 5 and edit their referencing files"
    - "regenerate indexes and repository_index_manifest.json"
    - "commit on master and publish to ai/review/latest"
  forbidden_actions:
    - "read .ssh/**, *.pem, *.key, id_rsa*, id_ed25519*, .env, .env.*, .credentials.json, or any credential material"
    - "delete anything in the protected list of section 4"
    - "delete a file while leaving a reference to it in place"
    - "push master"
    - "touch the teacher repository"
    - "edit any file in bootstrap_required_loaded_files without opening a release binding cycle"

return:
  packet_id: "codex-core-registry-and-final-cleanup-0004"

completion_policy: "completion_preserving"
---

# The registry, and the cleanup it makes cheap

## 1. Why the registry comes first

Two cleanups have now deleted files that no reference could reveal: the agent
permission policy, read by Claude Code from outside at a fixed path, and the runner
ignore policy, read by git the same way. Both were found by accident while chasing
something else. Neither would have raised any alarm.

A reachability pass cannot fix this, because the loader is not in the tree. **So the
registry is not derived from reachability — it is built the other way, from the tool
inward**, which is the method the 0003 audit already validated by independently
rediscovering the known casualty before being trusted on the rest.

Both inputs already exist. Do not recompute a closure.

- `0002-closure.json` — 360 root files, 1267 edges, keep set, dynamic-load targets
- `0003 audit` — 18 tracked mechanism paths, 5 environment classes over 13 paths, each
  with loader, discovery mechanism and evidence

## 2. Registry contents

Write `.ai/MECHANISM_REGISTRY.yml`. One entry per mechanism, not per file. Each entry:

```yaml
- mechanism: "<name>"
  loader: "<the tool that reads it>"
  loader_class: "in_repo_program | external_tool_convention | host_application"
  discovery: "documented convention | hardcoded default | referenced from <path>"
  evidence: "<what establishes the claim; not 'looks like config'>"
  paths: ["<exact paths or an exact path-set>"]
  cache_dirs: ["<directories the mechanism writes but does not track>"]
  ownership: "core | domain | UNDECLARED"
  failure_surfacing: "next test run | next runner execution | never until misuse | ..."
  deletion_rule: "protected | human_decision_required | free"
```

`failure_surfacing` is the field that earns the registry its keep. Sort entries by it.
A mechanism whose breakage never surfaces on its own is the one that needs a declared
entry most, because nothing else will ever report it.

`cache_dirs` matters for the same reason: `.pytest_cache/`, `.ai/runs/<id>/`,
`_branch_locks/` are written at runtime and are invisible to any static analysis.

## 3. Ownership is recorded, not fixed

Mark ownership `UNDECLARED` where `CORE_MANIFEST.yml` covers neither. Measured at this
head, at least these qualify: `.claude/`, `.ai/HANDOFF_COMMON_CONVENTIONS.md`,
`.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`, `.ai/COMMUNICATION_DRIFT_LEDGER.yml`,
`.ai/DECISIONS.md`, `.ai/runs/`, `.gitattributes`. Two are in the receipt-required
bootstrap set, so a domain may edit a file that breaks its own release binding with no
rule forbidding it and no conflict to reveal it.

Record them. **Do not edit the manifest in this task** — that is a separate ownership
decision and it touches a bound surface.

## 4. Protected — deleting any of these fails the task

- the seven `bootstrap_required_loaded_files` paths and the two on-demand paths
- `3号方案.md` — Plan 3 constitution. `AI_Bootstrap_Sequence.md` §1 names it a full
  constitutional source loaded on protected action, constitutional conflict, or
  Engine A/B routing dispute. Measured: referenced by 16 files including
  `.ai/load_profiles/foreground_planner.md`. It is conditionally live, not historical.
- `城邦系统需要实现的目标原则.md` — on the same authority chain, referenced by 7 files
- `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md` — the runtime life contract,
  the other conditional constitutional source
- `.claude/settings.json` and `.ai/runs/.gitignore` — both already lost once
- `.gitattributes`, `.gitignore` — EOL normalization and ignore policy
- the 18 Set A mechanism paths from the 0003 audit
- `01_Research_Reports/` — kept by Human decision despite the manifest listing it
  domain-owned; record the contradiction, do not resolve it

## 5. Authorized deletions

**Human decision, not a reachability finding.** These are removed because the Human has
judged them no longer useful, on evidence already measured. Do not re-derive
justification and do not file them under any deadness criterion.

**`0号方案.md`, `1号方案.md`, `2号方案.md`** — measured at this head: referenced only by
`CORE_MANIFEST.yml`, the auto-generated `index.md`, and the auto-generated
`repository_index_manifest.json`. No protocol, profile, task or test references them.
Record their registry evidence as you delete them, so the record survives the file.

**Historical battle-task records and their indexes** — the executed tasks are not going
to run again. Includes the `07_Execution_Plans` task records and the corresponding
entries elsewhere. Verify what else lives there before removing:
`Dual_Check_Proposal_System/` holds three Stage documents that did not appear in the
reference measurement and must be checked, not assumed.

## 6. The chained edits, which are the part that goes wrong

`00_City_State_Routing_Table.md` links to `Task_001`, `Task_003` and `Verdict_005`.
Those links were repaired **today**, from absolute paths into another repository into
working repository-relative paths. Deleting the targets without editing the table
converts a link that was just fixed into a link to a missing file.

**Delete the target and clean the reference in the same commit.** The routing table is
core-owned but is not in the receipt-required set, so editing it does not open a
rebinding cycle — confirm that yourself before relying on it. If any chained edit does
land on a bound file, stop and report rather than opening a cycle inside this task.

Same rule everywhere: `04_Parliament/Verdicts/index.md`,
`07_Execution_Plans/index.md` and the generated manifest all reference these paths.
Generated indexes are regenerated rather than hand-edited.

## 7. Verification

After the deletion commit: unit suite, `run-fixtures`, release-binding check — all
green. Regenerate indexes and `repository_index_manifest.json`; the manifest has been
wrong before, claiming 1883 tracked files against a real 503.

Then the registry's own test: for every entry, confirm each declared path exists and
each declared cache directory is either present or correctly ignored. An entry that
cannot be verified is a defect in the registry, not a reason to delete the file.

## 8. Stop conditions

A protected path appears in a delete set; a chained edit would touch a
release-bound file; a suite does not recover after deletion; or a registry entry cannot
be given verifiable loader evidence.

Record `origin/master` at start and end. Publish to `ai/review/latest`, verify the head
is on that branch, and write the immutable Human Brief. Everything measured here was
measured at `2f298d2f3d79a7bc24af6949475a945538350dfc`; re-measure, and where you
disagree, your measurement wins and you say so.
