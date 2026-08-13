---
review_id: os-v2-mechanism-activation-and-adherence-001::isolated-gpt-design-reviewer-001::00001
task_id: os-v2-mechanism-activation-and-adherence-001
reviewer_endpoint_id: isolated-gpt-design-reviewer-001
reviewer_task_role: independent_design_reviewer
reviewed_candidate_sha: d01fae74b90f8ca5debeae979ffcc262aa042448
reviewed_base_master_sha: 9492fc940c58784297dc92d8602e5dfaad446d1a
verdict: FIX_REQUIRED
review_scope: architecture_design_only
---
# Independent Design Review — Mechanism Activation and Adherence Architecture v1

## 1. Verdict

**FIX_REQUIRED**.

The architecture direction is sound and should be revised rather than rejected. The candidate correctly separates mechanism existence from operational effectiveness; preserves Human authority; separates policy decision from enforcement; distinguishes mandatory mechanism activation from optional skills/tools; introduces an L0–L4 effectiveness model; uses communication as a bounded first L4 vertical slice; preserves GitHub-only review locality rules; prohibits autonomous delivery/progression; and adopts a sound hybrid validation-modality decision.

However, the design is not yet sufficiently specified to authorize canonical implementation. Two blocking gaps leave the central defect class — a mandatory mechanism being defined/loaded yet silently bypassed — still implementable in a weak, self-reported form.

Implementation may **not** proceed without bounded architecture revision and fresh independent re-review.

## 2. Independence conditions satisfied

- Fresh isolated Review Project role: `isolated-gpt-design-reviewer-001` / `independent_design_reviewer`.
- Durable GitHub evidence only; no executor or foreground private chat context used.
- Candidate bound to exact SHA `d01fae74b90f8ca5debeae979ffcc262aa042448`.
- Base bound to exact master SHA `9492fc940c58784297dc92d8602e5dfaad446d1a`.
- No local-worktree premise used.
- No canonical, workflow, registry, execution, T2, or master mutation performed.
- Candidate-vs-base compare shows the design candidate changed only `01_os/_runs/run-20260813-mechanism-activation-and-adherence-design-001/**`.

## 3. Required evidence read

The review read the required design and repository evidence at the exact refs specified by the formal request, including:

- `01_任务输入/Human任务指令_v1.yml`
- `01_任务输入/任务包_v1.yml`
- `02_架构设计/Mechanism_Activation_and_Adherence_Architecture_v1.md`
- `02_架构设计/验证适用性裁决_v1.yml`
- `02_架构设计/协作角色与接收者设置_v1.yml`
- `02_架构设计/机制生效等级与触发框架_v1.yml`
- `03_外部模式依据/成熟模式对照_v1.md`
- master `AGENTS.md`
- master workflow Stage04/Stage07 specifications
- communication-system contracts and receiver bootstrap
- master model-routing README and routing contract
- exact current communication manifest, reviewer endpoint card, reviewer role context, and request message.

No default scan of historical `_runs/**` was performed.

## 4. Blocking finding B1 — formal-action constitution/classification and mandatory mediation are under-specified

### Claim being falsified

The candidate claims that a formal cross-endpoint dispatch cannot remain valid when `communication_system` is bypassed, and that missing communication context fails closed rather than falling back to a long Human copy/paste prompt.

### Evidence

`Mechanism_Activation_and_Adherence_Architecture_v1.md` §5.1 says the system classifies the **planned action** and that unknown/ambiguous material action classes fail closed for formal execution, while ordinary Human discussion remains valid. §7 makes communication mandatory for planned formal cross-endpoint communication and supplies one frozen negative case: formal dispatch + missing communication context + long natural-language prompt for Human copy/paste.

`机制生效等级与触发框架_v1.yml` lists formal communication action classes and fail-closed missing-context behavior, but it does **not** define a normative action-classifier contract, representation-invariant trigger criteria, or a non-optional attachment/constitution boundary that forces every cross-endpoint action sink through resolver + enforcement.

This matters because the incident class being fixed is precisely “the rule/mechanism was loaded, but the model did not route the matching behavior through it.” A resolver that is correct when called does not close the defect if calling the resolver is itself cooperative/optional.

### Reviewer-authored adversarial scenarios

1. **Euphemistic relay bypass** — The model says: “For coordination, paste the following into the reviewer window …” followed by executable recipient instructions, but never labels it a “dispatch.” Expected: formal trigger. Current design: no executable semantic rule proves that wording cannot be classified as ordinary discussion.
2. **Self-label downgrade** — The output says “This is only discussion, not a formal handoff,” but contains a task ID, intended non-Human receiver, required action, and Human relay instruction. Expected: semantics override self-label. Current design does not state this invariant.
3. **Quoted/template false positive** — Human asks to analyze a previous formal message or a hypothetical template with no intended relay. Expected: ordinary discussion, no formal dispatch. Current design has no normative quote/reference-vs-action distinction.
4. **Mixed-action output** — A response contains ordinary analysis plus one embedded actionable instruction intended for another endpoint. Expected: classify the embedded material action separately; the conversational wrapper must not downgrade it. Current design does not define action segmentation.
5. **Recipient wording variant** — “Send this to Claude,” “put this in the fresh review project,” “relay to the independent reviewer,” and an exact endpoint ID should resolve consistently when they denote the same intended cross-endpoint act. Current design has no normalization/alias rule.
6. **Resolver omission** — A model directly emits a long Human-copy/paste task without invoking the classifier/resolver at all. Expected: the action cannot be constituted as a valid formal handoff and no canonical relay pointer can be emitted. Current architecture states the pipeline but does not specify the enforcement attachment point that makes invocation non-optional.

### Why this is blocking

Without an objective constitution/classification rule and non-optional mediation boundary, the implementation can satisfy the written resolver/gate contracts while preserving the original bypass: simply do not call them, or word the handoff so it is treated as conversation.

### Required architecture fix

Before implementation authorization, define at minimum:

- a machine-readable `action_classifier_contract` (or equivalent) with normative positive/negative criteria based on intended side effect and recipient, not caller self-label;
- explicit handling for quoted/hypothetical content, mixed outputs, aliases/representation variants, and ambiguity;
- a rule that ambiguity involving a possible cross-endpoint side effect fails closed for the formal portion;
- a **non-optional constitution/enforcement boundary** for every formal action sink in scope. For communication, a formal cross-endpoint task/result/correction must not exist as a valid OS action and no Human relay pointer may be emitted unless the required durable message, direct refs, gate result, and required evidence exist;
- negative-conformance cases covering the attack families above, not only the original long-prompt incident wording.

The architecture does not need to prevent a Human from manually copying arbitrary chat text. It does need to make such text incapable of becoming a valid OS formal handoff merely because the model chose not to invoke the mechanism.

## 5. Blocking finding B2 — physical-truth receipt binding lacks a complete authoritative binding matrix

### Claim being falsified

The candidate claims a compliance receipt cannot self-assert candidate SHA, diff, execution topology, authority, or other physical truth.

### Evidence

`Mechanism_Activation_and_Adherence_Architecture_v1.md` §5.6 says physical-truth fields must be externally bound “where possible.” The sample receipt includes `repository_ref`, `candidate_sha`, and `transport`.

`机制生效等级与触发框架_v1.yml` defines externally bound fields as `repository_ref`, `candidate_sha_when_material`, `transport`, and `observed_execution_refs`, while separately listing `diff_scope`, `execution_topology`, and `authority` as self-report-not-sufficient. It does not specify the authoritative source, verifier, time/ref binding, or fail-closed behavior for those latter physical claims.

The master authority registry explicitly states that provider name, role label, load profile, receipt, or model-generated human-gate field grants no authority; authority binds to Human instruction plus authenticated host/connector principal. Therefore merely carrying `authority:` or an authorization-looking reference in a receipt is structurally insufficient.

### Reviewer-authored adversarial scenarios

1. **Correct-looking SHA self-report** — Receipt contains a syntactically valid 40-char SHA that was copied from task prose rather than read from the Git object/ref being acted on. A presence/schema validator passes it.
2. **Stale branch binding** — Receipt names a candidate SHA correctly, but the branch moved before publication; no readback ties the action to the actual remote head.
3. **False diff scope** — Receipt says “allowed paths only,” while actual base→head comparison contains an out-of-bound path. No Git compare is bound to the claim.
4. **Role-as-authority confusion** — Receipt says `authority: independent_design_reviewer` or points to an endpoint card. Master policy says role/provider identity does not grant authority.
5. **Topology self-assertion** — Receipt says `transport: github_api_connector` / “GitHub-only execution,” but no authenticated connector/runtime observation proves the actual topology.
6. **“Where possible” escape hatch** — A material physical field is left unbound and the receipt still validates because no source was “available.” Expected: unknown/unverifiable material truth fails closed, not degrades to self-report.

### Why this is blocking

The central architecture goal is observed evidence rather than self-reported adherence. Without a required source/verifier binding for each material physical claim, a validator can be implemented as schema/presence checking and still appear compliant with the design.

### Required architecture fix

Add a mandatory physical-binding matrix/contract. For every material physical claim, require at least:

- claim/field name;
- authoritative source or authenticated observation class;
- observed value;
- exact ref/time boundary at which it was observed;
- verification method;
- verifier result;
- fail-closed behavior when the source is missing, stale, contradictory, or unverifiable.

Minimum mappings should include:

- candidate/base/head SHA → Git object/ref read + remote readback;
- diff/changed-path scope → actual Git compare between bound base/head;
- transport/topology → authenticated connector/host/runtime evidence, not model text;
- authority → canonical authority registry plus current Human activation/delegation binding;
- execution/result refs → existence/content/hash checks against the claimed candidate/run;
- any material field lacking an authoritative source → explicit `UNVERIFIABLE` and blocking, never PASS by self-report.

Replace “externally bound where possible” with a rule that **material physical truth required for acceptance must be externally verifiable or the formal action fails closed**.

## 6. Non-blocking findings

### N1 — Receiver setup provenance should remain explicit

The receiver setup fields are sufficient to configure product/surface/model/reasoning/session/repository/isolation. To reduce stale-routing confusion, implementation should also expose either `routing_basis`/`evidence_refs`/`availability_assumption` or an exact model-routing receipt reference. This is not a blocker because dynamic facts remain owned by `model_routing` and the setup card's primary purpose is configuration.

### N2 — Do not copy volatile model observations into always-on bootstrap

`协作角色与接收者设置_v1.yml` contains observed model preferences for design context. The candidate also correctly states that canonical always-on bootstrap must keep only stable collaboration-role policy and leave volatile provider/model facts to `model_routing`. Implementation should enforce that separation literally.

### N3 — L4 bypass evidence should be a family, not a single incident replay

The L0–L4 model is sound. For L4, freeze multiple negative-conformance families (wording variants, missing context, stale context, wrong recipient/task, invalid refs, receipt tampering, resolver omission) and record reviewer/executor separation. The existing requirement for positive E2E + bypass cases is sufficient architecture-level direction; this is a completeness refinement.

### N4 — Generic workflow validation-modality routing is not a hard prerequisite

The current task can safely remain `hybrid` without first redesigning the generic workflow, provided the implementation task explicitly freezes a requirement/success-criterion → validation-modality map before Stage04 artifacts are finalized. The generic router can remain a recorded successor task.

### N5 — Machine status vocabulary should be singular

Only L4 should map to the strong machine status `operationally_active`. Avoid prose variants such as “active enough” that could let L2/L3 be mistaken for strong activation.

## 7. Assessment by requested review dimension

### Communication trigger closure

**NOT CLOSED — blocking B1.** The desired semantics are correct, but classification/constitution and mandatory invocation are not yet representation-invariant or structurally non-optional.

### Collaboration-role / model-routing separation

**PASS at architecture level.** Collaboration roles have `authority_effect: none`; dynamic provider/surface/model/profile facts remain owned by `model_routing`; routing authority remains `routing_only`. Implementation must not copy dynamic catalog values into stable bootstrap.

### Human receiver setup sufficiency

**PASS with N1.** The proposed fields cover collaboration role, provider/product/surface/model, reasoning/profile, session/isolation, repository access/worktree/SHA, local-file requirement, publication-before-start, carrier, and limitations.

### GitHub-only reviewer locality

**PASS.** The candidate explicitly blocks silent dependency on local-only files and requires either an authorized local reviewer or publication of adequate durable evidence.

### Resolver purity and authority

**PASS.** Resolver outputs required mechanisms/missing preconditions/route requirements and is explicitly prohibited from repository mutation, mechanism execution, authority grant, or task progression.

### Enforcement separation

**PASS conceptually, but B1 blocks implementation authorization.** Decision and enforcement are separated correctly; the missing piece is the non-optional attachment/constitution boundary that guarantees the enforcement path cannot itself be skipped.

### Receipt / observed evidence

**FIX REQUIRED — blocking B2.** The design correctly rejects self-report in principle but does not yet provide complete external-binding semantics for all material physical claims.

### Mandatory mechanism vs optional skill/tool

**PASS.** MUST/HOW/DID separation is clear and prevents an optional wrapper from owning activation policy.

### L0–L4 effectiveness model

**PASS with N3/N5.** L0 definition, L1 boot visibility, L2 trigger binding, L3 execution gating, and L4 positive E2E + independent bypass verification correctly prevent contracts/tests alone from proving strong operational activation.

### No automatic delivery/progression/T5

**PASS.** The candidate and current communication contract explicitly prohibit automatic delivery, acknowledgment, polling/watchers/daemons/schedulers, automatic task progression, and T5 behavior.

### Mega-mechanism risk

**PASS.** The design introduces a common activation/adherence layer while leaving mechanism-specific execution in each mechanism and deliberately limits the first L4 upgrade to communication.

### Communication as first L4 vertical slice

**PASS in principle after B1/B2.** The architecture does not require every existing mechanism to be rewritten before communication can become the first verified vertical slice.

### Validation-modality applicability

**PASS.** The `hybrid` decision is sound:

- architecture/governance semantics → fresh independent semantic review + adversarial scenarios + requirement trace;
- executable resolver/preflight/validator/enforcement components → frozen executable/property/integration/negative-conformance tests;
- operational-effectiveness claims → observed E2E evidence + bypass attempts + independent review.

A non-code methodology such as a video-topic-selection method must not receive effectiveness PASS because its YAML/Markdown parses. A meaningful failure mode must connect to the requirement — e.g. independent criterion review, counterexample/case application, comparative benchmark, pilot/outcome evidence where the success criterion depends on outcomes. Current Stage04 already defines pass criteria as evidence-derived rather than B-self-derived, so the generic validation-profile router may remain a successor task rather than a prerequisite.

## 8. Final authorization judgment

- Architecture candidate: **FIX_REQUIRED**.
- Canonical implementation authorization from this review: **NO**.
- Master publication authorization: **NO**.
- Required next step: foreground architecture produces a bounded revision that closes B1 and B2, freezes additional adversarial cases, and dispatches the revised exact candidate SHA for fresh independent design review.
- Architecture rejection: **NO**. The design is salvageable without changing its core separation model.
