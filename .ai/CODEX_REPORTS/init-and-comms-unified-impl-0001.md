# Initialization and multi-environment communications v0.2 — implementation report

## Executive core

- Status: all nine authoritative corrections applied and candidate qualified; independent foreground static/dynamic review remains required after publication.
- Exact base: `master@3506bc43bfac9fdc5b546964074bb7cce83f4a42`.
- Work branch: `dev/init-and-comms-unified-impl-0001`.
- Added four routing-only load profiles with protocol-release pointer and verified canonical SHA-256 digests.
- Added a non-authorizing constitutional digest that fails closed to `3号方案.md` and Awakening.
- Added a cooperative C0/C1 per-instance lane layout, meta/envelope schemas, explicit bound epoch, `base_review_head`, foreground-only deterministic reducer, and immutable STATE provenance refs.
- Kept the seven-field pointer names and order unchanged; validator/policy versions remain `3.0.0` / `v3`.
- Communication gate, validator, policy semantics, fixtures, canonical event/pointer, and STATE transition behavior receive no lane semantics.
- Backend now writes immutable event-identity Human Brief paths; foreground alone owns canonical STATE and latest HUMAN_BRIEF.
- Defined a one-way protocol-release epoch with no-in-flight/old-session/reload cutover preconditions; legacy OUTBOX becomes read-only and dual/mixed delivery fails closed.
- Added tracked `CLAUDE.md` with canonical `.ai/TOKEN_USAGE_PROFILE.md`; Token v0.2 is the backend default discipline.
- Marked the XML change accurately as `platform compatibility and reasoning-disclosure correction`; it changes disclosure behavior but no parser/schema/permission semantics.
- No CAS, new ActorOrigin binding, formal proof, heartbeat, polling, scheduler, Gateway, Coordinator, or runtime was added or activated.
- Corrected semantics head: `3dfd3b622b029896919aa73778d1b9316c45d69b`; mechanical receipt/lane-epoch binding head: `c0481ea4c4958f12b91eab902d55dd3087718e9e`.

## Validation

- Lane tests: `4/4` pass (two same-environment instances isolated plus cross-write rejection; duplicate backend claim; stale epoch exclusion; exact STATE source traceability).
- Communication regression: `17/17` pass; fixture suite `215/215`; log SHA-256 `74b090a0a8d1f0d46517f2da00004b2c345f46ef62dac072c3eeae47c74a2e26`.
- Token tools: `6/6` pass; log SHA-256 `f394ab39f10a8f6966e7c1ad10d2e4293af9fd494ef6bf3a30c2ecf01e860883`.
- Windows runner: `6/6` pass; log SHA-256 `be85db9f8e944dedfae7f16e18d1445ea53f30f3f721fc607027b2a3e958fa5b`.
- PowerShell AST, Python compile, JSON-schema parse, and four profile-digest checks passed.
- Repository indexes: final generate/check/validate passed; second generation reported `changed_outputs: 0`.
- Source-neutral STATE/INBOX/OUTBOX/HUMAN_BRIEF stayed byte-identical to the neutral base.

## Recovery, deviations, and remaining decisions

- First lane run exposed an over-narrow Git-object regex; the repair restricts input to exact `40hex:path` and all four cases then passed.
- Corrections C1–C9 were applied without expanding the cooperative threat model or adding lane behavior to the compliance gate.
- Policy semantics remain byte-equivalent to base except the pre-authorized mechanical `protocol_release_head` binding required by the unchanged 17/17 receipt test.
- Index generation required its normal two-step admission of newly generated index paths; final deterministic run reached zero diff.
- Deviations from the joint v0.2 + corrections authority: none.
- Real Human decisions remaining inside the pre-authorized PR/merge objective: none.
- Required non-Human closure: Fable dynamic validation and ChatGPT independent static review; backend does not self-accept.

## Independent expression

The design is strongest where it stays modest: lanes prevent cooperative writers from stepping on one another, but do not pretend to authenticate them. The release-pointer profiles also make token discipline measurable without turning summaries into authority. If this layer later grows a runtime, it should earn that expansion through a new threat model rather than quietly accumulating security claims.
