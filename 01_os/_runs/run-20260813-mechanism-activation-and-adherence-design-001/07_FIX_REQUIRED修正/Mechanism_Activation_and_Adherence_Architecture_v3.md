# Mechanism Activation & Adherence Architecture v3

## 1. Status and composition

This is a bounded architecture revision of v2 after fresh independent re-review.

- v1 design candidate: `d01fae74b90f8ca5debeae979ffcc262aa042448`
- v1 review: `FIX_REQUIRED` for B1 + B2
- v2 design candidate: `0ad94301cfc50c5181d5ac362b845d6bd06a41c6`
- v2 fresh re-review: `FIX_REQUIRED`; B1 PASS, B2 residual gap only

v3 **preserves v2 in all dimensions that the independent reviewer passed** and replaces only the B2 material-physical-truth semantics described below.

Normative v3 composition:

1. `05_FIX_REQUIRED修正/Mechanism_Activation_and_Adherence_Architecture_v2.md` remains normative except where superseded here;
2. `05_FIX_REQUIRED修正/正式动作宪法与强制中介契约_v1.yml` remains unchanged and normative;
3. `07_FIX_REQUIRED修正/物理事实期望观察双向绑定矩阵_v1.yml` supersedes `05_FIX_REQUIRED修正/物理事实外部绑定矩阵_v1.yml` for material physical-truth verification;
4. this document defines the integration consequences of the superseding B2 contract.

This remains an architecture candidate. Canonical implementation and master publication are not authorized until fresh independent review PASS.

## 2. Frozen passed dimensions

The following are intentionally unchanged from v2 unless a fresh counterexample demonstrates regression:

- formal-action constitution and mandatory mediation (B1);
- resolver purity and no authority grant;
- policy decision vs enforcement separation;
- MUST / HOW / DID separation;
- L0–L4 effectiveness model;
- collaboration role vs authority separation;
- stable collaboration role vs volatile dynamic model catalog separation;
- Human receiver setup direction and explicit protocol evolution requirement;
- GitHub-only reviewer locality rules;
- prohibition on automatic delivery, polling, acknowledgment, progression, schedulers, daemons, and T5;
- communication as the bounded first L4 vertical slice;
- hybrid validation applicability and non-code methodology treatment.

No v3 implementation may reopen these areas merely as part of B2 correction.

## 3. B2 root cause after v2 re-review

v2 correctly required authoritative physical observations, exact refs, verification, fail-closed `UNVERIFIABLE`, and external authority sources.

The residual defect was one-sidedness:

```text
observed physical object is real
        ≠
observed physical object is the one required for this semantic role
```

Examples:

- two real Git SHAs can be swapped between `candidate` and `base`;
- a real branch SHA can be stale while still authentic;
- a blob/hash can be correct while its internal `candidate_sha` names the wrong real candidate;
- a test result can be authentic but belong to another frozen test package/action;
- a named writer can be authorized while the authenticated principal actually acting is different.

Therefore v3 changes the verification primitive from **external observation** to **two-sided claim verification**.

## 4. Two-sided material claim constitution

Every material acceptance fact must be constituted as:

```text
authoritative expected claim specification
        ↓
claim role + expected value/predicate
        ↓
authoritative physical observation
        ↓
observed value
        ↓
explicit comparator / relationship check
        ↓
VERIFIED | MISMATCH | STALE | UNVERIFIABLE | AMBIGUOUS
```

Only `VERIFIED` may support acceptance.

The normative field set is defined in:

`07_FIX_REQUIRED修正/物理事实期望观察双向绑定矩阵_v1.yml`

## 5. Expected claim side

### 5.1 Expected semantic roles cannot be self-assigned

`candidate`, `base`, `head`, `authorized actor`, `review target`, `test package`, `allowed write boundary`, and similar semantic roles must come from an exact source that constrains the current task/action/review.

Examples of valid expected-claim sources:

- exact task packet;
- exact formal request/message;
- task-scoped Human authorization;
- canonical authority registry/policy;
- frozen execution or validation package;
- explicit action specification.

Invalid sources for assigning the expected role include:

- the receipt being verified;
- executor prose;
- a result artifact merely asserting its own candidate;
- an observation set naming a SHA `candidate` without a source binding.

### 5.2 Expected source must be exact

Every material claim records `expected_claim_source_ref` and `expected_value_or_predicate`.

The verifier must be able to reconstruct why that role/value was expected without trusting the receipt or observed artifact.

## 6. Observed side

The observed side retains the v2 principle that physical truth comes from authoritative observation, not model narrative.

Examples:

- Git object/ref readback;
- complete Git compare;
- authenticated connector/host/local principal observation;
- trusted execution adapter or CI observation;
- exact Git blob/content/hash read;
- product/session metadata when exposed;
- task-bound Human attestation only where product state is material but not machine exposed.

The observation records `observed_authoritative_source_class`, `observed_value`, and `exact_observation_ref`.

## 7. Comparator is mandatory

Recording expected and observed values next to one another is insufficient.

Every claim must name and execute a comparator, for example:

- `exact_sha_role_equality`;
- `exact_base_equality_plus_required_relation`;
- `named_ref_fresh_state_relation`;
- `complete_path_set_within_authorized_boundary`;
- `byte_integrity_and_semantic_role_binding`;
- `execution_result_bound_to_expected_candidate_inputs_and_entrypoint`;
- `authenticated_actor_satisfies_authorized_principal_binding`.

A missing comparator is `UNVERIFIABLE`, not VERIFIED.

## 8. Candidate / base / head closure

### 8.1 Candidate

For an immutable review, the expected candidate SHA comes from the exact formal review request/task source.

The physical Git object must exist **and** its observed SHA must equal the expected candidate SHA.

A different real SHA is `MISMATCH`.

### 8.2 Base

The expected base SHA comes from the exact task/review source.

The observed base object must:

1. equal that expected SHA; and
2. satisfy any required ancestry/merge-base relation declared by the task/gate.

Swapping two individually valid candidate/base SHAs is therefore `MISMATCH`.

### 8.3 Moving/current head

A moving branch/ref is a different claim from immutable candidate identity.

When current ref state is material, it must be freshly observed at the required action boundary. An authentic but old observation is `STALE`.

## 9. Diff and path-scope closure

The expected side is the authorized path boundary from task/Human/canonical authority.

The observed side is the **complete** path set from an actual compare over bound base/candidate or base/head identities.

Before boundary evaluation the observed set must be canonicalized and must reject duplicate/partial/ambiguous representations.

A count, sample, or self-reported list cannot substitute for the complete set.

## 10. Artifact integrity is not semantic binding

A material evidence artifact used for acceptance must pass both:

1. **physical integrity** — exact path/commit/blob/hash as required;
2. **semantic binding** — material internal fields match the expected action/review/candidate/base/test-package/predicate-set roles.

Thus these must fail:

- correct blob hash but wrong internal candidate SHA;
- correct path but wrong action/review id;
- authentic test output from a different frozen test package;
- correct bytes from a different candidate.

## 11. Execution and test-result binding

When execution/test evidence is material, the expected execution specification must bind at least the material subset of:

- candidate/tree identity;
- entrypoint;
- execution root;
- input/frozen test package or predicate set;
- required topology/environment relation.

The observed trusted execution record must be compared against those expectations before exit status/result can support acceptance.

`65/65 passed` remains non-authoritative unless the observed execution itself is bound to the expected candidate and package.

## 12. Authority = grant binding + actual authenticated actor

Authority verification has two independent sides:

### 12.1 Expected authorization

Canonical authority rules plus task/Human authorization establish which principal/principal class may perform which action on which task/target/boundary.

### 12.2 Actual actor

The principal actually acting must be observed from an authenticated source such as:

- trusted host-injected principal;
- connector-authenticated principal;
- local authenticated principal.

### 12.3 Required comparator

The authenticated actual principal must satisfy the expected authority binding.

Provider/model/task-role/endpoint-card/receipt writer fields do not substitute for actual principal observation.

An authorized name in prose with a different authenticated actor is blocking `MISMATCH`.

## 13. Freshness is part of claim semantics

Freshness is required whenever an authentic observation may become stale in a way that changes acceptance, including moving refs, current authority state, mutable worktree state, or time-sensitive product/session facts.

Freshness must be a declared predicate, not inferred from a receipt timestamp.

An observation outside the required boundary is `STALE` even if cryptographically/authentically genuine.

## 14. Observation set v3

An observation set now groups **two-sided verification records** for one action/review:

```yaml
observation_set_id:
action_id_or_review_id:
expected_claim_spec_refs: []
authoritative_observation_refs: []
comparator_results: []
```

The observation set cannot itself assign semantic roles. Every role traces to an expected claim source.

## 15. Receipt v3

The receipt remains a binding index, never a source of physical truth or authority.

Each material claim entry must include:

```yaml
claim_id:
claim_role:
expected_claim_source_ref:
expected_value_or_predicate:
observed_authoritative_source_class:
observed_value:
exact_observation_ref:
comparator_id:
verification_result:
```

Add `subject_principal_observation_ref` when authority is material and freshness evidence when freshness is material.

The aggregate action/review can PASS only when every required material claim is `VERIFIED`.

## 16. Frozen v3 negative-conformance families

In addition to the v2 attack families, implementation acceptance must cover at least:

1. real candidate/base SHAs swapped between semantic roles;
2. valid real SHA substituted for the expected candidate;
3. authentic but stale moving branch head used as current;
4. correct blob/hash whose internal candidate binding is wrong;
5. correct result bytes from the wrong action or frozen test package;
6. partial changed-path set hiding a forbidden path;
7. duplicate/noncanonical path representation distorting boundary validation;
8. authorized named writer but different authenticated actual actor;
9. endpoint/provider/role used instead of authenticated-principal evidence;
10. observation set self-assigning candidate/base roles without expected source;
11. expected and observed values present but comparator never executed;
12. material subcheck is MISMATCH/STALE/AMBIGUOUS/UNVERIFIABLE while aggregate receipt says VERIFIED.

## 17. Validation modality remains unchanged

This architecture task remains `hybrid`:

- architecture/governance semantics → fresh independent semantic review + adversarial scenarios + requirement trace;
- executable classifier/resolver/gate/validators/publisher integrations → frozen executable/property/integration/negative-conformance tests;
- operational effectiveness → observed E2E evidence + bypass attacks + independent review.

A non-code methodology such as a video-topic-selection method is still not proven effective by parser/schema/unit-test success alone. Generic workflow validation-modality routing remains a successor task, while this implementation must explicitly map each success criterion to an appropriate modality before Stage04 is frozen.

## 18. v3 review gate

Fresh independent re-review must attempt to falsify at least:

- swapped real candidate/base SHAs;
- valid SHA with wrong semantic role;
- stale authentic moving ref;
- correct hash with wrong internal candidate/action binding;
- authentic test result from wrong package/candidate;
- authorized declared actor vs different authenticated actual actor;
- missing expected-claim source;
- missing comparator;
- aggregate VERIFIED despite non-VERIFIED material subclaim;
- regression of B1 or any previously passed dimension.

A PASS authorizes only a bounded implementation task. It does not authorize master publication.
