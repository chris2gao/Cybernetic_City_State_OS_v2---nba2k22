# Math Mentor Knowledge Completion Program

## 0. Document Status And Authority

- Program version: `1.0-draft`
- Status: planning contract only
- Domain: `08_Domain_Applications/Math_Mentor`
- Execution source branch/head: supplied by the Human-approved launch packet and verified from Git before launch
- Published baseline default: `master`, unless the current Human task names another source branch and immutable head
- Current P3 state: closed

This document defines a future long-run program. Its execution must follow `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`. It does not authorize execution, source publication, P3 entry, bridge generation, status promotion, or merge of an existing repair branch. A future execution packet must name this document, an immutable source head, an exact scope, allowed writes, publication policy, and all human-authorized stage gates.

Where older documents conflict with the current evaluator status model, `NODE_QUALITY_AUDIT_PLAN.md`, `BRIDGE_SCHEMA.md`, and the conservative status semantics take precedence. In particular, a Mode B semantic audit requires model review and must not be represented as a machine proof.

This durable program contract does not encode volatile live progress. Current accepted progress is established by reviewed `.ai/CODEX_REPORTS/`, `.ai/PROGRAM_RUNS/` checkpoints, the active launch packet, and physical Git evidence. Legacy branches and broad repair branches are historical evidence or candidate pools unless a current Human task explicitly selects one.

## 1. Program Purpose And Boundaries

The Knowledge Completion Program completes the Math Mentor knowledge and teaching system as an auditable sequence from corpus inventory through Coordinator consumption.

Its purpose is to make every in-scope knowledge object:

1. identifiable and correctly routed;
2. formally and pedagogically complete;
3. connected to verified prerequisites;
4. ready for mode-correct validation;
5. certified as a safe bridge endpoint;
6. connected by canonical bridges where a real mathematical relation exists;
7. consumable by the Coordinator without bypassing Exam Agent or spaced-review rules.

The program is not a request to maximize file count or force every candidate connection into the graph. Completion means that every in-scope item has either passed its applicable gates or has an explicit unresolved disposition that prevents false completion claims.

### 1.1 In Scope

- Split Level 1-6 roadmaps and their canonical node identities.
- Canonical teaching-node YAML files in `Pure_Math_Intuition_DB/`.
- Node identity, mode, definitions, `sub_topics`, mappings, prerequisites, validation evidence, and teaching readiness.
- Canonical schema-v1 bridges and their registry/index state.
- Coordinator lookup and teaching-flow integration.
- Exam Agent and spaced-review handoff preservation.
- Checkpoints, failure quarantine, rollback evidence, and final review artifacts.

### 1.2 Structural Exclusions

Structural files, schemas, indexes, evaluator implementations, generated/staging directories, protocol documents, and bridge files are not teaching nodes. Stage 0 must classify them before any repair action. `schema.yaml` is the known example that must remain excluded from node-repair counts.

### 1.3 Protected Boundaries

- Do not read `数学知识路线图_全部.yaml` for routine layer work. Use split roadmaps unless a specifically authorized full-graph audit requires the combined file.
- Do not claim full-database mathematical correctness from parse success, executable sanity, shape checks, optional-dependency skips, or semantic-only metadata.
- Do not machine-pass Mode B.
- Do not equate node-ID order with learned mastery.
- Do not generate or consume a bridge to compensate for an incomplete endpoint.
- Do not push or merge a protected source branch without a separate human gate.

## 2. Long-Run Autonomous Program Execution Model

### 2.1 Single Launch, Internal Checkpoints

A human may authorize one long-running execution packet covering a named stage range under `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`. Codex may then continue through that range without stopping after every stage when all internal gates pass. The run still creates a durable checkpoint at every stage and every repair/generation batch.

Internal checkpoints are evidence boundaries, not routine human interruptions. Non-blocking issues are recorded in `.ai/LONG_RUN_LOGS/<program_id>.md` and independent authorized work continues. Stop/continue decisions follow the long-run protocol rather than treating every ambiguity, protected-file skip, scope candidate, or deferred stage as an immediate interruption.

The run stops only when:

- a required human gate was not granted by the launch packet;
- a mathematical or routing ambiguity exceeds the approved decision policy;
- scope must expand beyond the packet;
- a protected file or branch would be modified;
- a regeneration, merge, or source push is required but unauthorized;
- missing P3/bridge authority prevents all remaining authorized work; otherwise the stage is logged as deferred;
- the same failure signature exhausts three materially different repair attempts;
- validation evidence contradicts a required exit criterion;
- source or review-branch concurrency makes publication unsafe.

### 2.2 Isolated Run Branch

Each run uses an isolated source-derived branch such as `ai/knowledge-completion/<run_id>`. The launch packet binds the run to an exact `source_head`. Existing broad repair branches are evidence pools only and are never implicit execution baselines.

Accepted changes are written in small, domain-coherent commits. Broad YAML reserialization is prohibited. A checkpoint commit must be reviewable independently and must not mix node repair, bridge landing, index updates, and mailbox publication.

### 2.3 Sequential Small Batches

- Node repair, evaluator execution, semantic review preparation, bridge design, and bridge landing use batches of at most five items.
- One long run may process many batches sequentially.
- Passing one batch does not promote another batch.
- Independent failures are quarantined so safe work can continue.
- After three failed repair attempts for the same signature, record the item in `三次修复仍失败_待后续处理.md` or the run-specific failure ledger and stop retrying it.

### 2.4 Run Artifact Layout

A future run should maintain:

```text
.ai/PROGRAM_RUNS/<run_id>/
  MANIFEST.yml
  CHECKPOINTS/stage-0.yml ... stage-9.yml
  REPORTS/stage-0.md ... stage-9.md
  FAILURES.md
  FINAL_REPORT.md
```

`MANIFEST.yml` binds `run_id`, program version, source head, branch, scope, authorized stages, allowed paths, batch limit, human gates, and final publication policy. Checkpoints record counts, changed paths, validation results, unresolved items, rollback commit, and next-stage eligibility.

### 2.5 Outcome States

Final run status uses the taxonomy in `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`:

- `completed_clean`;
- `completed_with_review_log`;
- `completed_with_blockers`;
- `blocked_preflight`;
- `failed_and_reverted`.

These statuses apply only to the authorized stage range. A deferred, unauthorized Stage 7 or Stage 8 does not make an otherwise completed Stage 0-6 run fail.

## 3. Completion Definitions

### 3.1 `node-complete`

A node is `node-complete` when:

- its global identity, filename, roadmap level, title/name, and domain agree;
- it has an accepted Mode A or Mode B route;
- its `sub_topics` are non-empty, coherent, and cover the promised concept;
- it has a reviewed formal definition, theorem skeleton, or axiom skeleton;
- required mapping content and analogy limitations are present;
- it is not a schema, index, bridge, template, or other structural file.

`node-complete` does not by itself mean teaching-ready, validation-passed, bridge-ready, learned, or Coordinator-consumable.

### 3.2 `teaching-ready`

A node is `teaching-ready` when it is node-complete and can support the Coordinator contract:

- explanation before interrogation;
- mode-appropriate intuition before formal compression;
- full `sub_topics` coverage;
- guided forcing questions and corrective explanation;
- student restatement of the formal definition;
- Exam Agent handoff;
- classroom-pass handoff to spaced review.

### 3.3 `validation-ready`

A node is `validation-ready` when all artifacts needed for its assigned lane are present and runnable or reviewable:

- Mode A has concept-relevant executable audit code, declared dependencies, assumptions, edge cases, and non-shape-only assertions.
- Mode B has a formal semantic-review dossier covering definition accuracy, prerequisites, LLM mapping, mapping boundary, misleading risk, and teaching usefulness.

`validation-ready` means the validation can be performed. It is not the same as a passing validation outcome.

### 3.4 `bridge-ready`

A node is `bridge-ready` only when it is node-complete, teaching-ready, validation-ready, and has passed its mode-correct review; all required prerequisite references resolve and are verified; its identity is stable on an approved baseline; and no unresolved warning could alter the proposed connection.

Mode A requires accepted computational evidence. Mode B requires ChatGPT High semantic acceptance and is never machine-passed. Unresolved-mode nodes are not bridge-ready.

### 3.5 `bridge-generated`

A bridge is `bridge-generated` when a reviewed P3 design has been landed as a canonical `BRIDGE-XXX.yaml` using `BRIDGE_SCHEMA.md` version `1.0`, with explicit endpoints and honest initial statuses.

Generated does not mean validated, indexed, or Coordinator-consumable.

### 3.6 `coordinator-consumable`

A bridge is `coordinator-consumable` only when:

- every endpoint is present and identity-resolved;
- prerequisites are verified;
- bridge validation has passed for Mode A, Mode B, or mixed as declared;
- the bridge is indexed;
- `teaching_use` and `learned_history_rule` are complete;
- learned-history conditions are satisfied at runtime;
- Coordinator lookup, compressed first display, association-slot teaching, and comprehension checking pass integration tests.

Unindexed, pending, unresolved, failed, or missing-endpoint bridges remain audit warnings or teaser-only records.

## 4. Global Program Invariants

1. Every count distinguishes processed, repaired, passed, review-required, manual, excluded, and missing.
2. A later stage cannot silently weaken an earlier exit criterion.
3. Status promotion requires evidence stored in the checkpoint.
4. Mode B semantic review is a model judgment, not a machine verdict.
5. Bridge generation reads only bridge-ready endpoints.
6. Formal Coordinator consumption requires the canonical bridge contract.
7. Student mastery is established through persisted learning history, not numeric node order.
8. Source commits, review artifacts, and source publication remain separate actions.
9. Every batch has a rollback commit and exact changed-path inventory.
10. A program run may finish with exceptions, but it may not call the knowledge system complete while exceptions remain in scope.

## 5. Multi-Stage Program

### Stage 0 - Corpus Inventory

| Contract | Definition |
| --- | --- |
| Goal | Establish the authoritative teaching-node corpus and exclude structural/schema-like files before repair. |
| Input artifacts | Split Level 1-6 roadmaps, canonical DB directory, mapping index as locator, source head, prior audits, and approved scope. |
| Output artifacts | Corpus manifest; node/bridge/structural classification; identity aliases; parse report; missing/duplicate inventory; exclusion list. |
| Exit criteria | Every in-scope file is classified; every teaching node has one authoritative roadmap identity or an explicit conflict; structural files are excluded; parse failures are enumerated. |
| Validation method | YAML parse, filename/ID/roadmap reconciliation, duplicate detection, split-roadmap coverage, and exact changed-path baseline. |
| Human gate | Required only for scope changes, irreconcilable identity collisions, full-roadmap access, or deletion/merge proposals. |
| Rollback strategy | Remove run-only inventory artifacts and return to the immutable source head; no teaching file is modified in this stage. |
| Codex role | Extract, classify, count, and produce machine-readable evidence without mathematical promotion. |
| ChatGPT review role | At final review, judge whether exclusions and corpus boundaries were semantically correct; interrupt only for declared gate conditions. |

### Stage 1 - Node Identity And Mode Routing Completion

| Contract | Definition |
| --- | --- |
| Goal | Give every teaching node a stable identity, level/domain placement, and accepted Mode A or Mode B route. |
| Input artifacts | Stage 0 manifest, split roadmaps, Universal Protocol routing table, node YAML, and known mode exceptions. |
| Output artifacts | Minimal node patches; routing registry; unresolved-routing ledger; batch validation reports. |
| Exit criteria | Every non-quarantined node has consistent identity metadata and one accepted lane; unresolved nodes remain explicitly manual and cannot progress. |
| Validation method | Roadmap/file/ID consistency checks, domain-based route checks, exception checks, and cross-reference resolution. |
| Human gate | Required for disputed identity, ambiguous mathematical domain, mode-policy change, or node merge/split. |
| Rollback strategy | Revert only the failing batch commit and restore the previous routing registry checkpoint. |
| Codex role | Apply deterministic identity repairs and evidence-backed routes; quarantine ambiguity. |
| ChatGPT review role | Judge ambiguous domain/mode decisions in final review or when an interrupt condition fires. |

### Stage 2 - Formal Content Completion

| Contract | Definition |
| --- | --- |
| Goal | Complete the formal concept and its promised coverage without inventing unsupported mathematics. |
| Input artifacts | Routed nodes, roadmap descriptions, domain references, quality-gate plan, and prior review findings. |
| Output artifacts | Minimal formal-definition/theorem/axiom patches, corrected `sub_topics`, assumptions, notation, and regeneration exceptions. |
| Exit criteria | Every non-quarantined node satisfies `node-complete` formal-content and coverage requirements. |
| Validation method | Schema checks plus mathematical consistency review against title, `sub_topics`, examples, assumptions, and counterexamples. |
| Human gate | Required for disputed definitions, identity-changing rewrites, or single-node/domain regeneration. |
| Rollback strategy | Revert the batch; retain the pre-edit node and record the precise unresolved claim. |
| Codex role | Draft narrow repairs, preserve identity, and attach evidence and limitations. |
| ChatGPT review role | Perform final mathematical judgment; review immediately only when the run encounters a declared dispute gate. |

### Stage 3 - Prerequisite Closure

| Contract | Definition |
| --- | --- |
| Goal | Replace missing or inferred-only prerequisite state with a resolvable, reviewed dependency graph. |
| Input artifacts | Node-complete corpus, split roadmaps, prerequisite fields, bridge registry as non-authoritative evidence, and identity aliases. |
| Output artifacts | Verified prerequisite lists; missing/deferred ledger; cycle report; prerequisite graph snapshot. |
| Exit criteria | Every required reference resolves; intentional roots are explicit; cycles are either mathematically valid and documented or removed; no ID-order mastery assumption exists. |
| Validation method | Graph resolution, cycle/component analysis, roadmap-level consistency, and targeted mathematical dependency review. |
| Human gate | Required for disputed prerequisite direction, unresolved external dependency, or graph restructuring. |
| Rollback strategy | Revert the affected dependency batch and restore the prior graph snapshot. |
| Codex role | Resolve references and run graph checks; never convert sequence proximity into mastery evidence. |
| ChatGPT review role | Judge mathematical necessity and direction of nontrivial dependencies. |

### Stage 4 - Teaching Readiness

| Contract | Definition |
| --- | --- |
| Goal | Make each node teachable under the Coordinator's intuition-to-definition pipeline. |
| Input artifacts | Node-complete corpus, verified prerequisites, Coordinator prompt, mapping references, and teaching-flow specification. |
| Output artifacts | Mode-correct intuition/mapping, explicit mapping boundaries, subtopic checkpoints, forcing-question plan, definition-restatement hook, and Exam/review handoff metadata. |
| Exit criteria | Every non-quarantined node satisfies `teaching-ready`; Mode B has no everyday metaphor as primary mapping; Mode A retains low-friction physical intuition. |
| Validation method | Coordinator dry-run rubric covering explanation first, every `sub_topics` item, one-question progression, error repair, definition restatement, Exam handoff, and spaced-review handoff. |
| Human gate | Required for teaching-philosophy changes, misleading analogy disputes, or Coordinator contract changes. |
| Rollback strategy | Revert only mapping/teaching patches and restore the prior content-complete checkpoint. |
| Codex role | Build and test the teaching contract without simulating student mastery. |
| ChatGPT review role | Judge conceptual pedagogy, mapping safety, and whether formal compression preserves meaning. |

### Stage 5 - Validation Readiness

| Contract | Definition |
| --- | --- |
| Goal | Provide honest, mode-correct validation evidence for every teaching-ready node. |
| Input artifacts | Teaching-ready nodes, Mode A/B quality gates, evaluator status model, dependency inventory, and prior audit warnings. |
| Output artifacts | Mode A property audits and run results; Mode B semantic dossiers; warning/skip ledger; validated/review/manual census. |
| Exit criteria | Every non-quarantined node is validation-ready and has an honest outcome; no shallow/shape-only/skip result is promoted; no Mode B node is machine-passed. |
| Validation method | Mode A evaluator runs in batches of at most five plus property/edge-case checks; Mode B definition/mapping/prerequisite/teaching semantic review. |
| Human gate | Required for evaluator-policy changes, dependency escalation outside the packet, disputed semantic acceptance, or regeneration. |
| Rollback strategy | Revert audit changes that overclaim; restore the last teaching-ready checkpoint; retain failure evidence. |
| Codex role | Execute and classify evidence, distinguish warnings/skips/failures, and prepare semantic review packets. |
| ChatGPT review role | Perform final Mode B semantic judgment and audit whether Mode A evidence matches the stated concept. |

### Stage 6 - Bridge-Readiness Certification

| Contract | Definition |
| --- | --- |
| Goal | Certify which nodes may safely serve as bridge endpoints without generating bridges. |
| Input artifacts | Node, teaching, prerequisite, and validation checkpoints; proposed endpoint families; stable source head. |
| Output artifacts | Bridge-readiness registry; rejection reasons; eligible endpoint sets; P3 gate report. |
| Exit criteria | Every certified endpoint satisfies `bridge-ready`; every uncertified node remains explicitly gated; no bridge YAML exists from this stage. |
| Validation method | Per-endpoint checklist across identity, coverage, formal content, prerequisites, mode evidence, teaching readiness, and unresolved warnings. |
| Human gate | Required to reopen P3 for a named endpoint set and immutable baseline. Certification alone does not open P3. |
| Rollback strategy | Withdraw the affected certification record; node data remains at the prior validated checkpoint. |
| Codex role | Assemble evidence and issue conservative eligibility results; do not infer mathematical connections. |
| ChatGPT review role | Judge endpoint certification and recommend whether the human should open P3. |

### Stage 7 - Bridge Generation

| Contract | Definition |
| --- | --- |
| Goal | Design and land only mathematically justified bridges between certified endpoints. |
| Input artifacts | Human-approved P3 endpoint set and source head, bridge-readiness registry, `BRIDGE_SCHEMA.md`, split roadmaps, and next available bridge ID. |
| Output artifacts | P3 design table, design checkpoint, then canonical bridge YAML in sequential batches of at most five. |
| Exit criteria | Every generated bridge implements an approved design, uses schema `1.0`, has explicit endpoints, and retains honest `pending`/`unindexed` states until later validation. |
| Validation method | Mathematical connection review, schema validation, endpoint identity/level checks, mode/mixed-transition checks, and exact design-to-YAML comparison. |
| Human gate | Mandatory: the launch packet must explicitly reopen P3 and authorize bridge landing. Without both authorities, the program stops at Stage 6. |
| Rollback strategy | Revert the failing bridge batch; do not renumber or modify accepted prior batches; record abandoned IDs in provenance when required. |
| Codex role | Land only reviewed designs; never invent endpoints or connections. |
| ChatGPT review role | Judge bridge mathematics and teaching value at the design checkpoint or final review, as authorized by the launch packet. |

### Stage 8 - Bridge Validation, Registry, And Coordinator Consumption

| Contract | Definition |
| --- | --- |
| Goal | Validate, index, and integration-test generated bridges before formal teaching consumption. |
| Input artifacts | Generated bridges, canonical schema, endpoint registry, mapping index, Coordinator prompt, learning-history contract, and validation evidence. |
| Output artifacts | Mode-correct bridge audit results, index entries, Coordinator lookup tests, consumption census, and rejected-bridge ledger. |
| Exit criteria | Consumable bridges satisfy `coordinator-consumable`; rejected/pending bridges remain excluded; index and files agree with no duplicate or dangling IDs. |
| Validation method | Schema checklist; computational, semantic, or mixed audit; registry consistency; two-direction endpoint lookup; first-use display; learned-history filtering; teaser behavior; comprehension check; Exam and spaced-review regression. |
| Human gate | Required for semantic/mixed acceptance disputes, Coordinator policy changes, and formal teaching admission when not preauthorized. |
| Rollback strategy | Remove/revert the affected index entry and consumption status; retain the bridge as pending or revert its batch. |
| Codex role | Run deterministic checks, update approved registry entries, and execute Coordinator integration tests. |
| ChatGPT review role | Judge semantic/mixed validity and whether the bridge improves the formal and dialectical teaching structure. |

### Stage 9 - Maintenance And Regression Loop

| Contract | Definition |
| --- | --- |
| Goal | Establish a repeatable regression baseline and process future node, bridge, Coordinator, Exam, and review-system changes. |
| Input artifacts | All accepted checkpoints, final corpus/bridge registries, test results, unresolved ledger, and source commit range. |
| Output artifacts | Final report, regression manifest, maintenance schedule, unresolved backlog, review packet, and proposed integration commits. |
| Exit criteria | Initial regression suite passes for accepted scope; all exceptions are explicit; final counts reconcile; ChatGPT review package is complete. Ongoing maintenance remains event-driven. |
| Validation method | Re-run parse, identity, mode, prerequisite, node-quality, bridge-schema, index, Coordinator, Exam, and spaced-review checks on affected batches. |
| Human gate | Mandatory for final source integration/publication, merge, scope expansion, regeneration, or declaring the entire program complete. |
| Rollback strategy | Revert to the last accepted stage checkpoint; preserve reports and failure evidence; never use destructive reset on protected history. |
| Codex role | Produce the final evidence package and continue approved regression repairs without overstating closure. |
| ChatGPT review role | Perform the final end-to-end review, classify residual defects, and recommend accept, repair, partial accept, or rollback to the human. |

## 6. Mode A And Mode B Rules

### 6.1 Mode A - Computable Algebra Lane

- Use domain/subdomain routing, not level number alone.
- Everyday physical intuition is primary and must be mathematically bounded.
- Formal content states assumptions and the general claim before audit promotion.
- Code must test the stated concept rather than an unrelated example.
- `v8_sanity_audit` must test mathematical properties, including relevant edge cases where practical.
- Type, shape, length, successful execution, and optional-dependency skip are not sufficient for pass.
- A passing executable audit proves only its tested claims, not the entire node or theorem.
- Bridge readiness requires accepted computational evidence plus teaching and prerequisite gates.

### 6.2 Mode B - Pure Structure Lane

- Use domain/subdomain routing and named meta-logic exceptions.
- LLM architecture is the primary intuition model; everyday physical metaphor cannot be primary.
- Every mapping states where the analogy applies and where it fails.
- Code may be an intuition anchor or computable special case, never proof of the full structure.
- `v9_semantic_audit` must review definition accuracy, prerequisites, mapping boundaries, misleading risk, and teaching usefulness.
- Machine execution cannot produce a Mode B semantic pass.
- ChatGPT High provides final semantic judgment; unresolved content remains `review_required`.
- Bridge readiness requires explicit semantic acceptance plus teaching and prerequisite gates.

### 6.3 Mixed Bridges

Nodes retain a justified A or B route. `mixed` is a bridge mode, not an escape from unresolved node routing. A mixed bridge requires:

- certified endpoints from both lanes or a specific computable-to-structural teaching transition;
- separate evidence for Mode A and Mode B claims;
- a non-empty, mathematically accurate `mode_transition`;
- review that the transition does not turn an analogy into a theorem.

## 7. Bridge-Ready Certification Checklist

A node may be certified only when all applicable items are true:

- [ ] Canonical identity and roadmap level resolve.
- [ ] File is a teaching node, not structural/schema-like.
- [ ] Domain and Mode A/B route are accepted.
- [ ] `sub_topics` completely cover the declared concept.
- [ ] Formal definition/theorem/axiom skeleton is reviewed.
- [ ] Required prerequisites resolve and are verified.
- [ ] Mode-appropriate primary intuition/mapping is present.
- [ ] Mapping boundary prevents false inference.
- [ ] Coordinator teaching flow can cover intuition, definition, all subtopics, questions, restatement, and Exam handoff.
- [ ] Validation artifacts are ready and have the required accepted outcome.
- [ ] No shape-only, optional-skip, semantic-overclaim, or unresolved-mode warning remains.
- [ ] The node exists on the immutable baseline named by the certification.
- [ ] Certification evidence and reviewer are recorded.
- [ ] `bridge_readiness_status` is promoted only after the checklist passes.

## 8. End-To-End Execution Packet Contract

A future program-start packet must include at least:

```yaml
decision: "start_program"
program_ref: "08_Domain_Applications/Math_Mentor/KNOWLEDGE_COMPLETION_PROGRAM.md"
program_version: "1.0-draft"
run_id: "<unique-id>"
source_branch: "<branch>"
source_head: "<immutable-sha>"
work_branch: "ai/knowledge-completion/<run_id>"
scope:
  levels: [1, 2, 3, 4, 5, 6]
  domains: ["<explicit or all>"]
  node_manifest_ref: "<optional preapproved manifest>"
authorized_stages: [0, 1, 2, 3, 4, 5, 6]
p3_reopened: false
bridge_landing_authorized: false
allowed_paths:
  - "08_Domain_Applications/Math_Mentor/<explicit paths>"
batch_limit: 5
retry_limit_per_failure_signature: 3
publication:
  push_source: false
  publish_review_artifacts: true
human_gates:
  regeneration: "required"
  p3_reopen: "required"
  source_push: "required"
stop_rules_ref: "<packet section or artifact>"
final_report_ref: ".ai/PROGRAM_RUNS/<run_id>/FINAL_REPORT.md"
```

### 8.1 Internal Continuation Algorithm

For each authorized stage:

1. verify the previous checkpoint and current worktree head;
2. compute exact in-scope batches of at most five;
3. apply one batch and run its gate;
4. commit accepted work or revert the batch;
5. quarantine exhausted failures and continue independent work;
6. write the stage checkpoint and reconcile counts;
7. continue automatically only when exit criteria pass and no human gate is triggered.

The program does not pause merely because a stage number changed. It pauses because evidence failed, authority is missing, or a declared gate requires judgment.

### 8.2 Checkpoint Minimum Fields

```yaml
run_id: "<id>"
stage: 0
input_head: "<sha>"
output_head: "<sha>"
processed: 0
passed: 0
review_required: 0
manual_review_required: 0
excluded: 0
failed: 0
changed_paths: []
validation_evidence: []
quarantined_items: []
rollback_commit: "<sha-or-null>"
exit_criteria_passed: false
next_stage_authorized: false
human_gate: "not_required | required | satisfied"
```

### 8.3 Final Review

After the last authorized stage, Codex publishes one consolidated review package. ChatGPT reviews the full checkpoint chain rather than relying on the final status word. The human then decides whether to accept, request follow-up repair, expand the program, open P3, integrate source commits, or roll back selected batches.

The final package must include `.ai/LONG_RUN_LOGS/<program_id>.md`. Imperfections that did not block independent work enter targeted post-run repair rather than causing repeated Human interruption during the run.

## 9. Historical P2.10-B Evidence Snapshot

The deep-repair branch `ai/p2-10-b-645-deep-repair-review@29d6bd4` was recorded as evidence and a candidate pool, not an approved baseline or current source branch.

- Initial candidates processed: 649.
- Structural exclusions: 1 (`schema.yaml`).
- Teaching-node repair attempts: 648.
- Scoped Mode A audit passes: 29.
- `review_required`: 589.
- `manual_review_required`: 30.
- Bridge-gated teaching nodes: 648.
- Mode B machine passes: 0.
- Whole-branch merge recommendation: do not merge wholesale.

Future program execution must begin Stage 0 from the named current source head and may consult the temporary branch only as non-authoritative repair evidence. Accepted repairs should be replayed in small, minimal-diff cohorts.

P3 remains closed. This document does not reopen it. Stage 7 is unreachable unless a later human-approved execution packet explicitly sets `p3_reopened: true`, names certified endpoints and an immutable baseline, and authorizes bridge landing.

## 10. Non-Goals

- No claim that the full database is mathematically correct.
- No immediate P3 start.
- No bridge generation under this planning task.
- No conversion of `review_required` or `manual_review_required` into completed status.
- No wholesale merge of the deep-repair temporary branch.
- No node, evaluator, bridge, index, schema, automation, staging/generated, or roadmap edit under this planning task.
- No source-branch push under this planning task.
- No replacement of ChatGPT final review or human gates with autonomous status promotion.

## 11. Program Launch Readiness

This plan is ready for ChatGPT and human review. It is not ready for execution until a launch packet supplies the required immutable baseline, exact scope, allowed stage range, path permissions, P3/bridge flags, stop rules, and publication policy.

Recommended first execution authorization is Stages 0-6 together under `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`. That run can inventory, repair, validate, and certify endpoints continuously while keeping P3 closed. Stages 7-8 require explicit launch authorization when P3 or bridge work is intended; if they are not authorized, they are logged as deferred rather than treated as a failure. After final ChatGPT review, the human may issue a separate authorization for Stages 7-9.
