# 可信 Human 证明模式研究 v1

- task_id: `os-v2-stage-human-alignment-enforcement-root-cause-001`
- purpose: root-cause evidence for CR-002; identify mature patterns that separate a Human trust source from repository-writable claims
- evidence_policy: primary/official sources only; repository facts and external facts kept separate

## Repository fact baseline

Current master `repository_publisher_authority_v1.yml` already states the decisive trust rule: provider names, role labels, receipts, and model-generated `human_gate` fields authenticate nothing. Authority must bind to the Human instruction plus a trusted host or connector principal; accepted binding classes are `trusted_host_injected`, `connector_authenticated`, and `local_authenticated`, with fail-closed behavior when the binding is missing or unverifiable.

Implication: CR-002 cannot be solved by adding more repository fields that the same repo-writing model can mint.

## External mature patterns

### W3C WebAuthn

Source: W3C Web Authentication Level 3, https://www.w3.org/TR/webauthn-3/

The Relying Party supplies a challenge; the authenticator returns authenticator data, client data, and a signature. Verification checks the expected challenge/origin and verifies the signature using the registered credential public key. Architecture lesson: bind the exact stage-approval payload (or digest) into the challenge and verify the assertion against a pre-established trust anchor. Repository text is the payload being authorized, not the source of identity.

Boundary: WebAuthn can prove an authenticated user interaction with the challenged transaction; it cannot prove subjective comprehension. The OS can machine-prove disclosure plus authenticated disposition, not a Human mental state.

### GitHub protected environments / required reviewers

Sources:
- GitHub Docs, Deployments and environments, https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- GitHub Docs, Reviewing deployments, https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments

A workflow job can be held until an allowed reviewer explicitly approves or rejects it. GitHub can prevent self-review and can withhold environment secrets until protection rules pass. Architecture lesson: a host-managed approval event can be a valid Human attestation provider when the approving principal is separated from the model/executor principal and the event is bound to the exact candidate.

Limitations here: feature/plan availability varies, the primitive is deployment-centric, and a single-user connector may collapse initiator and approver identity. It is a possible provider, not the universal trust model.

### DSSE signed envelope

Sources:
- Secure Systems Lab, DSSE, https://github.com/secure-systems-lab/dsse
- DSSE scope, https://github.com/secure-systems-lab/dsse/blob/master/governance/02-scope.md

DSSE signs both payload bytes and payload type using an unambiguous pre-authentication encoding. Its scope explicitly excludes key management, trust establishment, identity binding, payload semantics, and verification policy. Architecture lesson: an authenticated envelope can bind exact bytes and type, but a valid signature is not by itself a trusted Human identity; trust root and principal-binding policy must be external to the envelope and ordinary candidate-writable state.

## Synthesized requirements

A completion-authorizing Human attestation provider must satisfy all of the following:

1. Approval occurs on a trust surface not forgeable solely through ordinary model repository write access.
2. The verifier authenticates a principal against a trust anchor the candidate cannot silently replace for the current task.
3. The proof binds task, stage/profile, exact artifact version or digest, disposition, covered exit items, and freshness/replay data.
4. The proof is verified without trusting receipt-supplied labels such as `actor_class: Human`.
5. Missing, unavailable, stale, replayed, wrong-principal, wrong-artifact, or unrecognized-provider evidence fails closed.
6. Repository-only `Human_relay_record` or `Human_authored_repository_artifact` claims may remain audit evidence but are not completion-authorizing unless backed by a separately verified attestation.
7. Trust-anchor changes are protected architecture/authority changes and cannot be accepted merely because a candidate updates verifier and trust root together.

## Current unknowns before implementation

- Which attestation provider is physically available on the intended Human surface: trusted host injection, WebAuthn/passkey, hardware-backed detached signature, or another independently authenticated provider.
- How a Human trust anchor is initially enrolled and durably protected.
- How validators obtain the frozen accepted trust anchor; preferred model is binding it to the task's fresh-read master SHA or a host-provided root rather than candidate-modifiable trust state.
- Whether GitHub-hosted approval is available and sufficiently principal-separated for this private repository; no assumption is made.
