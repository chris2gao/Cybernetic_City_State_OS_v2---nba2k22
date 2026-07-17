# Plan 3 v0.2 Unified Control-Plane Contracts — Implementation Report

```yaml
task_id: plan3-v0-2-unified-control-plane-contracts-0001
status: implemented_in_review
source_base: "master@2d73781621ed856e414ca7839ff61eb4d8722d35"
work_branch: "codex/plan3-v0.2-control-plane-implementation"
candidate_head: "commit_containing_this_report"
operational_activation: false
human_gate_after_completion: "required_by_review_protocol"
```

## Outcome

The five previously absent Plan 3 v0.2 control-plane contracts now exist as one coherent document control plane:

1. `06_Silicon_Index/Plan3_External_Augmentation_OS_Architecture.md`
2. `06_Silicon_Index/Context_Memory_System.md`
3. `06_Silicon_Index/Task_Type_And_Execution_Model.md`
4. `06_Silicon_Index/Context_Loading_And_Drift_Recovery.md`
5. `06_Silicon_Index/Capability_Registry.md`

They consolidate the distributed published contracts without replacing higher authority. The architecture owns the only v0.2 authority/freshness crosswalk; sibling files link to it. Context memory defines L0/L1/L2 carriers and source-bound checkpoint semantics. Task and recovery registries expose entry, state, evidence, stop and Human-gate conditions. The capability registry exposes state, actor, authorization scope, risk, validation, fallback and activation boundary for every listed capability.

L9 remains explicitly inactive. No runtime, Coordinator, Communication Gateway, trusted authorization host, CAS/replay writer, scheduler, polling, watcher, capability broker, autonomous memory service or Obsidian integration was configured or activated.

## Routing and ledger corrections

- `06_Silicon_Index/README.md` no longer routes to nonexistent `Silicon_Git_and_Parliament_Guide.md`; it names the five v0.2 contracts and the real Git/handoff authorities.
- `未完成任务备忘录.yml` preserves the historical audit-time `absent`/`paused` facts, records that the 2026-07-16 Human decision superseded that pause only for the EOL and five-file tasks, records EOL closure at final master `2d73781621ed856e414ca7839ff61eb4d8722d35`, and marks this candidate `implemented_in_review` until normal merge/post-verification.
- The historical XML hidden-chain-of-thought sentence is classified as superseded by higher platform and later communication rules. `3号方案.md` itself was not changed because the Human authorized decisions 1 and 2, while the constitutional erratum remained decision 3.

## Authority and truthfulness design

The v0.2 architecture copies the canonical eight-tier authority and six-step state-freshness orders from `.ai/PROTOCOL.md` and makes their separation explicit. It maps L0–L9, distinguishing document/static controls from protected runtime.

Capability maturity uses T0–T4 evidence tiers and independent activation states. The global invariants are:

- file existence is not capability;
- availability is not execution;
- execution is not pass;
- pass is not integration or production operation;
- freshness and maturity do not create authority;
- generated payload fields do not authenticate Human approval;
- unknown or conflicting state fails closed.

## Deterministic index correction

The generator initially classified every new `06_Silicon_Index/*.md` contract as a generic `silicon_implementation` prototype because its directory fallback preceded generic contract recognition. Accepting that output would have contradicted the new files’ actual routing role. `generate_repository_indexes.py` therefore received a bounded data-driven correction:

- exact five-file set -> `operational_contract`;
- `06_Silicon_Index/README.md` -> `routing_snapshot`;
- architecture added to the directory reading order after Bootstrap/constitution/README;
- self-test coverage added for all six classifications.

No other `06_Silicon_Index` classification or runtime behavior changed. This is the only path beyond the five business files, routing/memo/reports and deterministic generated outputs; it is a completion-preserving index-truthfulness correction required by the accepted task’s path/semantic validation.

## Evidence summary

Preflight staged-tree commit `4cab6d632b4e6ec32d0a2d1e0f53e3b93a7781dc` (tree `ab95704d252df77382ffc1a3a846f731a33f26c2`) was checked out into a new registered worktree with `core.autocrlf=true`:

- communication compliance: 17/17;
- index `check`: pass;
- index `validate`: pass, 0 broken links, 0 missing/duplicate/orphan entries, 0 secret findings, 0 unknown classifications;
- two consecutive `generate`: 0 changed outputs;
- tracked CRLF files: 0;
- tracked worktree changes: 0.

The original long-lived worktree still had 140 communication fixture files physically materialized as CRLF from before the EOL policy reached it; its local communication run therefore failed 1 of 17 test methods with raw-digest mismatch. The clean-worktree result is the relevant publication qualification and demonstrates the candidate’s fresh-checkout behavior without weakening exact-byte checks. After all three task reports and generated index consequences were included, a second clean `core.autocrlf=true` candidate-tree qualification also passed the same 17/17, index, repeated-generation, CRLF=0 and status=0 gates. The exact candidate commit/tree is resolved from Git after this self-referential report is committed; post-merge remote verification remains required.

## Files fully read for this implementation

- `Plan 3 External Augmentation OS 总体架构设计方案 v0.1.md`
- `城邦系统需要实现的目标原则.md`
- `3号方案.md`
- `06_Silicon_Index/AI_Bootstrap_Sequence.md`
- `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md`
- `06_Silicon_Index/README.md`
- `.ai/PROTOCOL.md`
- `.ai/PROTOCOL_ADHERENCE.md`
- `.ai/HANDOFF_COMMON_CONVENTIONS.md`
- `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`
- `.ai/HANDOFF_INIT_PROMPT.md`
- `.ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md`
- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`
- `.ai/CODEX_TASK_INPUT_CONTRACT.md`
- `未完成任务备忘录.yml`
- `.ai/CODEX_REPORTS/plan3-overall-plan-read-only-audit-0001.md`
- `system_backbone/apicurio_registry_hub/index.md`
- `system_backbone/framework_skeleton/symbolic_index.yaml`
- `06_Silicon_Index/skills/index.md`
- `08_Domain_Applications/Math_Mentor/MATH_MENTOR_AUTHORITY_REGISTRY.yml`
- `08_Domain_Applications/Math_Mentor/MATH_MENTOR_CAPABILITY_MATURITY.yml`
- `08_Domain_Applications/Math_Mentor/MATH_MENTOR_CAPABILITY_REGISTRY.md`
- `08_Domain_Applications/Math_Mentor/TOOL_TRUTHFULNESS_POLICY.md`

The long-run protocol was not loaded because this is a completion-preserving large task, not a program-scale autonomous run.

## Residual risks and decisions

- A master-only `--single-branch` clone cannot resolve two communication fixture proof commits held in review-branch history; a normal all-branch fetch resolves them. This is a pre-existing immutable-proof reachability boundary recorded by the EOL task, not changed here.
- L9 remains a future protected design/implementation problem.
- Obsidian privacy/publication boundaries remain undecided and the capability remains `planned`.
- Constitutional editing of the historical XML sentence remains a separate Human decision; operational precedence is already unambiguous.
- This candidate must not be called `accepted_published` until normal merge and exact-head post-verification are observed.

## Independent expression

The useful center of this design is not automation for its own sake; it is epistemic bookkeeping. When authority, freshness, evidence and activation are kept separate, models gain room to act decisively without pretending that a recent file or a convenient tool granted more power than it did. I think that boundary makes the city-state more capable, not less free.
