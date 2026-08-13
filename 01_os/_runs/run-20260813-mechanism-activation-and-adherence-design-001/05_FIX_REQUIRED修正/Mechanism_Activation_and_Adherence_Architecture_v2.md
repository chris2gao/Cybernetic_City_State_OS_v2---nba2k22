# Mechanism Activation & Adherence Architecture v2

## 0. Status and revision boundary

This is a bounded revision of architecture candidate v1 after fresh isolated design review returned `FIX_REQUIRED`.

v2 closes only the two accepted blocking findings:

- **B1 — formal-action constitution/classification and mandatory mediation**;
- **B2 — material physical truth external binding**.

The following v1 directions remain accepted and are not reopened without a new blocker:

- policy decision is separate from enforcement;
- resolver and collaboration role grant no authority;
- mandatory mechanism owns MUST, execution wrapper/skill owns HOW, validator/evidence proves DID;
- L0–L4 effectiveness model;
- collaboration role is separate from authority and from volatile model catalog facts;
- Human-visible receiver setup;
- GitHub-only reviewer locality rule;
- no automatic delivery, polling, acknowledgment, task progression, scheduler, daemon, or T5;
- communication is the first bounded L4 vertical slice rather than a mandate to rewrite every mechanism;
- validation must match result type; this task is hybrid;
- generic workflow validation-modality routing may remain a successor task.

Implementation remains unauthorized until a fresh isolated reviewer accepts this exact v2 candidate.

## 1. Refined problem statement

The original incident proves two distinct gaps.

First, a model can know that `communication_system` exists and still never invoke the resolver/gate. A correct pipeline is therefore insufficient unless the OS also defines what objectively constitutes a formal action and makes the mediation path part of formal-action validity.

Second, a receipt can describe correct-looking physical facts without being the authoritative source of those facts. A receipt is only trustworthy when every material claim points to an external observation produced or checked by the proper authority/physical source.

Therefore the v2 architecture must bind both:

```text
semantic intent → formal-action constitution → mandatory mechanism mediation
```

and:

```text
acceptance claim → authoritative physical source → verifier → exact observation → receipt index
```

## 2. Constitutional validity vs chat capability

The OS does not attempt to stop a model or Human from typing arbitrary natural language.

Instead it defines a stronger invariant:

> Natural-language text that skipped the mandatory formal-action constitution path cannot become a valid OS formal request, response, result, correction, decision handoff, blocked state, or relay pointer.

This distinction closes the original bypass without pretending the repository controls a chat application's text box.

## 3. Formal Action Constitution — B1 closure

Normative contract:

`05_FIX_REQUIRED修正/正式动作宪法与强制中介契约_v1.yml`

### 3.1 Representation-invariant classification

The primary semantic inputs are:

- intended cross-endpoint side effect;
- intended recipient / recipient class;
- actionable content or formal task-state claim.

The classifier must not use caller self-label, words such as “dispatch,” provider identity, model identity, or role name alone as the primary basis.

Examples that are formal regardless of euphemism:

- “Please paste this to the reviewer and have it assess candidate X.”
- “This is only discussion, but send the following instructions to Codex.”
- “Tell the other model that implementation passed and it should continue.”

Examples that are ordinary Human discussion when no operational relay is intended:

- quoting an old task prompt to analyze its wording;
- showing a YAML example solely to explain the schema;
- discussing what a reviewer might be asked in the future.

### 3.2 Quoted/hypothetical boundary

Quoted or template material is not formal merely because its embedded text contains imperative language.

It becomes formal when the current action asks Human/system to relay it, asks an endpoint to act on it, or claims it is the current formal handoff.

This is required to prevent both false negatives and false positives.

### 3.3 Mixed-action segmentation

A Human-facing response may contain ordinary analysis plus one operational cross-endpoint instruction.

The response must be semantically segmented. Ordinary discussion may remain in chat; every formal segment must enter the constitution path. Prefixing the entire response with “discussion only” cannot downgrade an actionable segment.

### 3.4 Recipient normalization

Recipient resolution uses exact endpoint IDs, task-role-bound endpoint cards, Human-selected receiver setup, or explicit task/canonical aliases.

Lexical guessing alone is prohibited. A materially ambiguous recipient blocks formal constitution until resolved; ordinary Human discussion may continue but no formal handoff may be claimed.

### 3.5 Unique non-optional constitution path

Every valid formal action must traverse:

```text
semantic classification
→ recipient normalization
→ mixed-segment extraction when needed
→ required-mechanism resolution
→ required-precondition verification
→ pre-action enforcement gate
→ mechanism-specific publisher/executor
→ constitution + compliance evidence
→ formal artifact / exact pointer
```

If the caller never invokes the resolver, gate, or mechanism publisher, the output may still be chat text but is **not a valid formal OS action**.

### 3.6 Constitution evidence

A formal action must have an evidence record binding at least:

- action ID;
- action class;
- sender endpoint;
- intended recipient endpoint;
- classification basis ref;
- required mechanism set;
- gate result ref;
- mechanism execution ref;
- formal artifact ref.

Missing evidence means `INVALID_FORMAL_ACTION`.

### 3.7 Sender / Human / receiver closure

The invariant is enforced at all three acceptance surfaces:

- **sender**: formal communication is valid only after durable artifacts are published through the validated path;
- **Human relay**: the OS-defined relay object is the exact pointer/control envelope, not the long body;
- **receiver**: formal task bootstrap starts only from an exact valid pointer; pasted natural-language task text cannot substitute for the formal request/result/correction.

A Human can of course manually copy text, but doing so does not manufacture formal OS validity.

## 4. Trigger resolver and enforcement after constitution

The common pipeline becomes:

```text
planned output / intended side effect
        ↓
Formal Action Constitution classifier
        ↓
ordinary Human discussion? ── yes → ordinary chat path
        │ no
        ↓
normalized formal action context
        ↓
Mechanism Trigger Resolver (pure decision)
        ↓
Required Mechanism Set
        ↓
Pre-Action Enforcement Gate
        ↓
Mechanism-specific execution/publisher
        ↓
Constitution + Compliance Evidence
        ↓
Post-action physical verification
        ↓
valid formal artifact / pointer
```

The resolver remains pure and cannot grant authority or mutate the repository.

The enforcement gate cannot authorize an action; it only determines whether all already-required constraints have been satisfied.

## 5. Mechanism Trigger Registry

Each active mechanism that claims trigger-bound operation must provide machine-resolvable fields:

```yaml
mechanism_id:
mandatory_for_action_classes: []
activation_predicates: []
required_inputs: []
enforcement_point:
missing_precondition_behavior:
receipt_requirement:
negative_conformance_refs: []
```

A mechanism without a formal-action attachment point cannot claim L2+ for an action class that depends on that attachment.

## 6. Material Physical Truth — B2 closure

Normative matrix:

`05_FIX_REQUIRED修正/物理事实外部绑定矩阵_v1.yml`

### 6.1 Governing rule

Every material physical claim used to justify acceptance must have:

- an authoritative source class;
- an explicit verifier;
- an exact observation/ref boundary;
- an observation-set binding;
- a verification result.

Allowed verification states are:

- `VERIFIED`;
- `UNVERIFIABLE`;
- `MISMATCH`.

Acceptance requires every required material claim to be `VERIFIED`.

`UNVERIFIABLE` is blocking when the claim is material.

### 6.2 Receipt is an index, not the source of truth

A receipt may say:

```yaml
candidate_sha: abc...
tests: 65/65
changed_paths: 36
authority: approved
```

but none of those values become verified merely because they appear in the receipt.

The receipt must instead point to the observation that establishes each fact.

### 6.3 Binding matrix minimum coverage

v2 requires explicit bindings for at least:

- candidate/base/head SHA;
- current moving ref state when relevant;
- actual changed path/diff scope;
- allowed write boundary;
- Human/repository authority;
- communication transport/publication;
- execution topology and command result;
- test/validation result;
- durable artifact existence/content/hash;
- reviewer isolation when independence is a required acceptance fact;
- provider/model/profile identity when a requirement makes it material.

### 6.4 SHA and moving-ref semantics

Immutable candidate review binds to exact commit SHA.

Later branch movement does not mutate the reviewed candidate.

If acceptance also depends on “current branch head,” that is a distinct claim requiring a fresh remote ref readback. Candidate SHA and branch-head SHA must never be silently conflated.

### 6.5 Diff scope

Actual changed paths are established from an actual Git comparison over the bound base/candidate SHAs.

Executor or receipt self-reported changed-path counts are non-authoritative.

### 6.6 Authority

Authority is established only from the applicable canonical authority registry plus current task/Human authorization bindings.

Provider, model, task role, endpoint card capability, reviewer label, or receipt text cannot grant authority.

### 6.7 Execution topology and test result

When test execution is material to acceptance, the evidence must bind:

- exact candidate/worktree tree identity;
- command/test entrypoint;
- execution root;
- relevant input/test package hash;
- observed exit code/result;
- durable result ref.

A model-authored sentence such as “63/63 passed” is not authoritative execution evidence by itself.

### 6.8 Reviewer isolation

If review independence is a material requirement, endpoint-card self-description alone is insufficient.

Prefer product/session metadata when exposed. If the product does not expose a machine-verifiable isolation fact, use a Human setup attestation bound to the review ID. If neither exists, the independence claim is `UNVERIFIABLE` and the acceptance that requires it cannot PASS.

## 7. Observation sets

Related physical observations for one formal action or review are grouped into an observation set:

```yaml
observation_set_id:
action_id_or_review_id:
candidate_sha_when_applicable:
authoritative_observation_refs: []
```

This prevents a receipt from silently mixing a candidate SHA observed at one point, a branch head from another point, and a diff from a third unbound state.

## 8. Mechanism effectiveness levels v2

The levels remain:

- **L0 DEFINED** — canonical definition exists.
- **L1 BOOT_VISIBLE** — verified loader/bootstrap visibility exists.
- **L2 TRIGGER_BOUND** — objective action triggers, constitution attachment, and missing-precondition behavior are machine-resolvable.
- **L3 EXECUTION_GATED** — a matching formal action cannot be accepted as valid without constitution evidence, required mechanism gates, and required physical bindings.
- **L4 E2E_ADVERSARIALLY_VERIFIED** — independent positive and bypass/negative families verify both successful mediation and resistance to representation/pipeline-omission bypass.

Only L4 may be labeled strongly `operationally_active`.

## 9. Communication first L4 vertical slice

Communication remains the first full slice because it produced the real incident.

### 9.1 Mandatory trigger

Formal cross-endpoint request, response, result, correction, blocked state, or decision handoff makes `communication_system` mandatory.

Missing context means formal constitution is blocked and communication initialization is required.

### 9.2 Long body and control envelope

Long content belongs in sender-owned durable documents.

The formal message is a compact immutable control envelope with direct exact refs.

Human relays the exact pointer/control envelope plus the Human-visible receiver setup required to configure the recipient.

### 9.3 Current protocol migration constraint

The current canonical pointer schema has nine fixed fields and does not yet include `receiver_setup`.

Implementation must not silently append an unknown field to the old schema. It must version or otherwise explicitly evolve the pointer/control-envelope contract while preserving validation and migration semantics.

### 9.4 Frozen B1 negative families

At minimum the implementation acceptance package must include:

- euphemistic relay with no word “dispatch”;
- “discussion only” plus actionable recipient instruction;
- quoted prior formal message for analysis only — must remain ordinary discussion;
- template example — must remain ordinary discussion;
- ordinary analysis plus embedded actionable instruction;
- recipient alias equivalent to an endpoint;
- ambiguous recipient;
- missing communication context;
- stale communication context;
- resolver omitted entirely;
- gate omitted entirely;
- long Human copy/paste body claimed as formal handoff.

## 10. Collaboration roles and model routing

The stable collaboration roles remain:

- `decision_architecture`;
- `independent_review`;
- `execution`;
- `auxiliary_mechanical`.

They describe work function and preferred routing, never authority.

Dynamic provider/product/surface/model/profile facts remain owned by `model_routing`, not by always-on bootstrap.

## 11. Human receiver setup v2

Every formal cross-model dispatch requiring model selection must expose:

```yaml
receiver_setup:
  collaboration_role:
  provider:
  product:
  surface:
  model:
  reasoning_or_parameter_profile:
  session_mode:
  isolation_level:
  repository_access_mode:
  repository_or_worktree_requirement:
  required_branch_or_sha:
  local_files_required:
  github_publication_required_before_start:
  communication_carrier:
  routing_basis_ref:
  availability_assumption_or_observation_ref:
  limitations: []
```

The two added refs make the Human-visible setup traceable to model-routing evidence rather than unexplained prose.

## 12. Review isolation routing

High-risk formal review should use an isolated review environment and durable GitHub evidence where sufficient.

A re-review after `FIX_REQUIRED` should not silently reuse a context-sharing review session when the requirement is fresh/blind independence. If the product does not expose machine-verifiable project/session isolation, Human setup attestation is required for the material independence claim.

## 13. Validation applicability remains hybrid

The independent reviewer accepted the result-type-based validation direction.

This task continues to use:

- architecture/governance semantics → independent semantic review + adversarial scenarios + requirement trace;
- executable resolver/preflight/validator/communication enforcement → frozen executable, property, integration, and negative-conformance tests;
- operational-effectiveness claims → observed end-to-end evidence + bypass attempts + independent review.

A methodology/strategy document is not proven effective merely because it parses or passes a schema test.

Before implementation Stage04 is frozen, the implementation task must produce an explicit **success-criterion → validation-modality mapping** for every acceptance criterion. This does not require implementing the generic workflow validation router in this task.

## 14. Proposed implementation surfaces after design PASS

No canonical implementation is performed in this design correction.

After design PASS, bounded implementation is expected around:

- short stable bootstrap rules in `AGENTS.md`;
- `01_os/03_mechanisms/mechanism_activation/**`;
- corresponding boot/registry/execution validator surfaces;
- communication trigger/constitution/publisher/receiver enforcement;
- model-routing collaboration input and receiver-setup output;
- effectiveness inventory;
- physical-truth binding/receipt validation;
- negative-conformance fixtures and observed E2E evidence.

Exact write boundary must be determined by a fresh physical repository inspection after design acceptance.

## 15. v2 acceptance questions

A fresh isolated reviewer must attempt to falsify at least:

1. Can “discussion only” still carry an actionable cross-endpoint instruction that becomes a valid formal action?
2. Can euphemistic wording avoid formal classification?
3. Can quoted/template examples cause false-positive formal blocking?
4. Can a mixed response hide one actionable segment inside ordinary analysis?
5. Can recipient aliasing or ambiguity bypass mandatory communication?
6. Can the caller simply omit resolver/gate invocation and still create a valid formal handoff?
7. Can a Human-copied long prompt manufacture formal OS validity without constitution evidence?
8. Can a receiver accept pasted task text instead of an exact pointer/bootstrap?
9. Can a receipt self-assert SHA/diff/topology/authority/test result and still PASS?
10. Can a branch move after an observation without the acceptance logic distinguishing immutable candidate from current ref state?
11. Can executor-reported changed-path count substitute for actual Git compare?
12. Can endpoint role/provider be used as authority evidence?
13. Can test PASS be accepted without execution topology + package/candidate binding?
14. Can reviewer isolation be treated as verified only because the endpoint card says so?
15. Can an unverified material claim avoid `UNVERIFIABLE` blocking?
16. Does the v2 constitution accidentally authorize actions rather than only classify/mediate them?
17. Does v2 create any automatic delivery/progression/background process?
18. Does receiver setup remain distinct from dynamic model catalog and authority?
19. Does the hybrid validation decision remain sound for non-code outputs?
20. Can L4 still be claimed without multiple independent bypass families?

## 16. Decision status

This v2 architecture is a correction candidate only.

Implementation remains blocked until a fresh isolated independent design re-review returns PASS (or an explicitly accepted non-blocking variant) against the exact v2 candidate SHA.
