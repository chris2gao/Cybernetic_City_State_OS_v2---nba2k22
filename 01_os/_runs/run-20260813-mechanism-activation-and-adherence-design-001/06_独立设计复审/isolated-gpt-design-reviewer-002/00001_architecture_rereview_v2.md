---
review_id: os-v2-mechanism-activation-and-adherence-001::isolated-gpt-design-reviewer-002::00001
task_id: os-v2-mechanism-activation-and-adherence-001
reviewer_endpoint_id: isolated-gpt-design-reviewer-002
reviewer_task_role: independent_design_reviewer
reviewed_candidate_sha: 0ad94301cfc50c5181d5ac362b845d6bd06a41c6
reviewed_base_master_sha: 9492fc940c58784297dc92d8602e5dfaad446d1a
formal_request_ref: 9f392020ab8f265f51e4e8ed08cd6c634d1f7b62:01_os/_communication/Cybernetic_City_State_OS_v2---core/active/os-v2-mechanism-activation-and-adherence-001/messages/foreground-architecture-001/00002_request.yml
verdict: FIX_REQUIRED
review_scope: architecture_design_only
---
# Independent Design Re-review — Mechanism Activation and Adherence Architecture v2

## 1. Verdict

**FIX_REQUIRED**.

The v2 revision materially improves the architecture and closes B1 at architecture level: formal-action validity is now separated from arbitrary chat capability, classification is representation-invariant by contract, mixed/quoted/alias cases are specified, and resolver/gate/publisher omission makes the attempted handoff invalid rather than silently valid.

B2 is **not yet fully closed**. The new physical-truth matrix is substantially stronger, but it still permits a one-sided verification pattern: an observer can prove that a Git object, ref, blob, authorization artifact, or other evidence **exists** without proving that the observed value is the **task-bound expected value for the semantic claim role** or that the claimed writer/actor is the authenticated principal actually exercising the authority. That leaves two required attack families incompletely closed: swapped/stale base/head or candidate-role binding, and evidence content/hash that is valid bytes but bound to the wrong candidate/action. It also leaves actual actor identity incompletely externalized under the canonical authority policy.

The architecture should be revised, not rejected. Implementation and master publication remain unauthorized by this review.

## 2. Independence and exact bindings

This review used the Human-relayed formal request at commit `9f392020ab8f265f51e4e8ed08cd6c634d1f7b62` and the bound endpoint `isolated-gpt-design-reviewer-002` / `independent_design_reviewer`.

The required Human setup attestation records a fresh project, project-only memory, repository connection, and no imported foreground/prior-review chat. It explicitly classifies itself as Human-reported product-state evidence rather than cryptographic or product-API proof; I use it only at that evidence class.

The reviewed architecture object is the immutable commit:

`0ad94301cfc50c5181d5ac362b845d6bd06a41c6`

The base is:

`9492fc940c58784297dc92d8602e5dfaad446d1a`

A Git commit fetch verified that the candidate object exists with commit message `docs(os): revise mechanism activation architecture for B1 B2`.

An actual Git compare `9492fc940c58784297dc92d8602e5dfaad446d1a...0ad94301cfc50c5181d5ac362b845d6bd06a41c6` returned the task design/evidence and communication paths only; no canonical `AGENTS.md`, active mechanism, registry, workflow, or master implementation file is changed by the candidate.

For publication of this review, the task branch was freshly observed at `9f392020ab8f265f51e4e8ed08cd6c634d1f7b62` before creating reviewer-owned evidence.

## 3. Exact evidence read

Candidate `0ad94301cfc50c5181d5ac362b845d6bd06a41c6`:

1. `01_os/_runs/run-20260813-mechanism-activation-and-adherence-design-001/05_FIX_REQUIRED修正/Mechanism_Activation_and_Adherence_Architecture_v2.md`
2. `01_os/_runs/run-20260813-mechanism-activation-and-adherence-design-001/05_FIX_REQUIRED修正/正式动作宪法与强制中介契约_v1.yml`
3. `01_os/_runs/run-20260813-mechanism-activation-and-adherence-design-001/05_FIX_REQUIRED修正/物理事实外部绑定矩阵_v1.yml`
4. `01_os/_runs/run-20260813-mechanism-activation-and-adherence-design-001/04_独立设计审核/StageDesignReview_v1接收与修正裁决_v1.yml`
5. `01_os/_runs/run-20260813-mechanism-activation-and-adherence-design-001/02_架构设计/验证适用性裁决_v1.yml`
6. `01_os/_runs/run-20260813-mechanism-activation-and-adherence-design-001/02_架构设计/协作角色与接收者设置_v1.yml`
7. `01_os/_runs/run-20260813-mechanism-activation-and-adherence-design-001/02_架构设计/机制生效等级与触发框架_v1.yml`

Original durable reviewer evidence at `a837b24342fe33c824d595949dfd6408dfbc3e57`:

8. `01_os/_runs/run-20260813-mechanism-activation-and-adherence-design-001/04_独立设计审核/isolated-gpt-design-reviewer-001/00001_architecture_review_v1.md`

Current canonical constraints at master `9492fc940c58784297dc92d8602e5dfaad446d1a` were checked narrowly where material, including `AGENTS.md`, Stage04/Stage07 README semantics, `01_os/05_registry/repository_publisher_authority_v1.yml`, communication message/receiver/carrier contracts, and `01_os/03_mechanisms/model_routing/路由契约_v1.yml`.

No default historical `_runs/**` scan was used.

## 4. B1 fresh adversarial re-review — CLOSED at architecture level

### 4.1 Euphemistic relay / self-label downgrade

**CLOSED.** The formal-action contract makes intended cross-endpoint side effect, intended recipient/class, and actionable/formal-state content the primary basis. Caller self-label and presence/absence of words such as `dispatch` are prohibited as primary classification bases. Therefore `discussion only` or euphemistic phrasing cannot downgrade a materially actionable cross-endpoint segment.

### 4.2 Quoted or historical formal content

**CLOSED.** Quoted/template content remains ordinary discussion when it is analysis/example-only with no requested or claimed cross-endpoint effect. It becomes formal only when the current action asks the Human/system to relay/use it operationally, instructs an endpoint to act, or claims it is the current handoff. This prevents the required false-positive family.

### 4.3 Mixed output segmentation

**CLOSED.** The contract requires semantic segmentation and prohibits whole-message downgrade by a discussion label. An embedded operational segment must traverse the formal path independently of surrounding analysis.

### 4.4 Recipient aliases / ambiguity / representation changes

**CLOSED at design level.** Exact endpoint IDs, task-role-bound endpoint cards, Human-selected receiver setup, and explicit canonical/task aliases are recognized sources. Lexical guessing alone is prohibited. Material ambiguity blocks formal constitution. Alias or segmentation changes therefore cannot lawfully change the intended formal effect without reclassification/normalization.

### 4.5 Missing or stale communication context

**CLOSED at design level, with implementation detail still to freeze.** The formal path verifies required preconditions; missing/invalid/stale mandatory context fails closed, and stale-context negative conformance is explicitly frozen. Implementation must define the exact freshness predicate used by the communication attachment, but the architecture no longer permits stale context to be silently accepted.

### 4.6 Resolver/gate/publisher omitted entirely

**CLOSED.** The unique constitution path is explicitly non-optional. Bypassing any required step makes `formal_action_valid: false`; chat text may still exist but cannot be accepted as an OS formal action. This addresses the central v1 omission defect.

### 4.7 Human-copyable long body without pointer

**CLOSED.** Sender validity requires durable publication through the validated path; the Human relay object is the exact pointer/control envelope; receiver bootstrap starts only from an exact valid pointer. Human manual copy/paste does not manufacture OS formal validity.

### 4.8 Fabricated pointer without durable closure

**CLOSED as an architectural acceptance invariant.** A pointer is valid only through the formal publication path and receiver validation; constitution evidence binds the action, required mechanisms, gate result, mechanism execution, and formal artifact. A pointer-looking string alone is not sufficient. The current canonical receiver bootstrap already requires exact-pointer entry, and v2 explicitly requires the future pointer/control-envelope contract to be versioned rather than silently extended.

**B1 conclusion: PASS at architecture level.** No new B1 blocker found.

## 5. B2 fresh adversarial re-review

The new matrix correctly closes most of the original B2 attack surface:

- prose-copied SHA cannot be authoritative merely by receipt presence; Git object/ref observation is required;
- moving refs require separate current-ref observation/readback where material;
- diff scope comes from actual Git compare, not executor path counts;
- write boundary uses task/Human/canonical authority sources plus actual changed-path validation;
- self-reported test PASS is prohibited without runner/execution binding;
- execution topology requires trusted adapter/host/CI observation;
- role/provider/endpoint card and receipt text cannot grant authority;
- Human authorization is required to bind task/writer/action/target;
- reviewer isolation cannot be proved by endpoint card alone; Human attestation is the specified fallback when machine metadata is unavailable;
- unverified material claims block acceptance.

### Blocking finding B2-R1 — expected-value / semantic-role / authenticated-subject binding remains incomplete

The matrix verifies the **observed physical object**, but does not consistently bind that observation to an **authoritative expected claim specification**.

#### A. Candidate/base/head role can still be wrong while every observed Git object is real

`candidate_base_or_head_SHA` names the authoritative source as the Git object database and remote ref readback. Those sources prove that a commit exists or that a ref currently resolves to a SHA. They do not, by themselves, prove why that SHA is the `candidate`, `base`, or `head` for the current task/review/action.

The receipt contract requires `claimed_value`, source class, verifier, observation ref, observation set, and result, but it has no required `expected_value_ref` / claim-spec source that the verifier must compare against.

The observation set similarly carries `candidate_sha_when_applicable`, but without an authoritative claim-spec ref that field can become another asserted label.

Adversarial consequence: if two real commits X and Y both exist, a verifier can successfully fetch X and Y and even run a real compare while the receipt swaps which one is the task-authorized base and which one is the candidate/head. Existence and compare success are not semantic-role correctness. The same problem applies to a stale-but-existing base when the action requires a fresh designated base.

This fails the required `base/head pair swapped or stale` attack family.

#### B. Valid blob/hash can still be bound to the wrong candidate/action

`durable_artifact_existence_and_content` binds path, commit/local observation set, and blob/content hash. That proves bytes at an exact repository state. It does not by itself prove that the artifact's semantic fields refer to the expected candidate/action/review/test package.

Adversarial consequence: an evidence artifact can exist at the correct path and have a correctly verified hash while its internal `candidate_sha` or action binding points to a different real candidate. A byte/hash verifier succeeds although the acceptance claim is wrong.

This fails the required `evidence ref exists but content/hash/candidate binding is wrong` attack family unless a separate expected-value comparison is mandated.

#### C. Authority references do not yet externalize the actual authenticated writer/actor principal

Canonical master authority policy requires identity binding through `trusted_host_injected`, `connector_authenticated`, or `local_authenticated`, and fails closed when that binding is unavailable. The v2 `Human_or_repository_authority` row correctly requires canonical authority rules plus task-scoped Human authorization, but its authoritative sources/verifier do not explicitly require an observation of the current authenticated host/connector/local principal. `writer_or_actor` appears only as an `exact_binding` field, which can otherwise degrade to a declared identifier.

Therefore the architecture must bind the task-authorized actor to the authenticated principal that actually performs the write/action, not merely to an endpoint/task-role string.

### Required bounded B2 fix

Add a two-sided claim-verification contract for every material claim:

```yaml
claim_role:
expected_claim_source_ref:
expected_value_or_predicate:
observed_authoritative_source_class:
observed_value:
exact_observation_ref:
subject_principal_observation_ref_when_authority_material:
relationship_or_equality_check:
freshness_requirement_when_applicable:
verification_result:
```

At minimum:

1. `candidate_sha` — expected value comes from the exact formal review/task/action input; Git observation must prove that same SHA exists and is the object actually reviewed/executed.
2. `base_sha` — expected value comes from the task/action base binding; Git must prove the object and any required ancestry/merge-base relation. A swapped candidate/base must be `MISMATCH`.
3. `head/current_ref` — keep immutable candidate identity separate from moving-ref observation; if current head matters, read it freshly and compare it against the action's expected head predicate.
4. changed paths — compare the full canonicalized base→candidate/head path set; reject omitted or duplicate path claims and validate the complete set against the authorized boundary.
5. evidence artifacts — verify bytes/hash **and** parse/validate the material candidate/action/review/test-package fields against the expected claim source.
6. authority — combine canonical grant + task/Human authorization with an authenticated principal observation for the actual writer/actor; endpoint/provider/role labels remain non-authoritative.
7. observation sets/receipts — carry the exact claim-spec/expected-value refs so that observations cannot self-assign semantic roles.

This is a bounded B2 correction. It does not require reopening B1 or redesigning the overall architecture.

## 6. Regression checks on previously accepted dimensions

- resolver purity and no authority grant: **PASS**
- decision vs enforcement separation: **PASS**
- MUST/HOW/DID separation: **PASS**
- L0–L4 effectiveness model and negative-evidence requirement: **PASS**
- collaboration role vs authority separation: **PASS**
- volatile model catalog excluded from stable always-on bootstrap: **PASS**
- Human receiver setup direction: **PASS**, with the v2 architecture adding routing/availability provenance refs; the older design YAML should be harmonized during implementation/spec update so there is one machine-readable field list
- GitHub-only reviewer locality: **PASS**
- no automatic delivery, polling, acknowledgement, task progression, scheduler, daemon, or T5 behavior: **PASS**
- common activation layer does not become a mega-mechanism: **PASS**
- communication remains the first bounded L4 vertical slice: **PASS**
- hybrid validation remains sound: **PASS**
- non-code methodology is not falsely validated by parser/document/code checks alone: **PASS**
- generic validation-modality router remains a successor rather than a hard prerequisite: **PASS**

The current canonical pointer has exactly nine Human-chat fields and no `receiver_setup`; v2 correctly requires an explicit version/evolution rather than silently appending an unknown field.

## 7. Final authorization judgment

- Architecture candidate: **FIX_REQUIRED**
- B1 formal-action constitution / mandatory mediation: **PASS at architecture level**
- B2 material physical truth binding: **FIX_REQUIRED — B2-R1**
- Architecture rejection: **NO**
- Canonical implementation authorization from this review: **NO**
- Master publication authorization from this review: **NO**
- Required next step: bounded architecture revision adding authoritative expected-claim/semantic-role and authenticated-subject binding, then a fresh exact-candidate independent re-review

No canonical implementation mutation, master publication, automatic delivery, acknowledgement, or task progression is performed by this reviewer.