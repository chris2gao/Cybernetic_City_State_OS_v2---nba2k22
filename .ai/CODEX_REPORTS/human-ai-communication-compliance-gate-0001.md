# Human–AI Communication Compliance Gate — Implementation Report

```yaml
task_id: human-ai-communication-compliance-gate-0001
status: implementation_complete_awaiting_foreground_review
base: d235e602c14250d16b91f2897cb8308e031cc13c
work_branch: codex/human-ai-communication-compliance-gate
candidate_head: bound_by_the_post_commit_review_handoff
source_publication_authorized: false
human_gate_after_completion: required
```

## Outcome

The published Human–AI communication protocol now has a deterministic,
versioned, fail-closed repository compliance gate. It classifies named C0/C1/C2
events, validates material communication artifacts and immutable evidence, and
reports transition eligibility without executing a transition or granting
authority.

The implementation stays entirely inside the authorized `.ai` control-plane
paths. No source mailbox, domain, runtime, Coordinator, bridge, UI, middleware,
polling, cron, automation, source branch, or `master` publication was changed or
activated.

## Delivered controls

1. **Bootstrap receipt** — binds the exact protocol head, provider-neutral role,
   frozen wire schema, loaded file paths/commits/digests, inherited-on-demand
   files, Human-only authority boundary, and all onboarding answers. Loaded
   protocol files must resolve at the receipt's own protocol head. This verifies
   evidence claims, not cognition.
2. **Material classifier** — named C0, C1, and C2 event types are disjoint;
   unknown types fail closed. Ordinary C0 discussion is not forced through a
   durable GitHub artifact.
3. **Strict document and reference handling** — JSON duplicate keys and YAML
   duplicate keys, merge keys, tags, anchors, aliases, and multi-document input
   are rejected. Production refs require an exact commit, exact safe path,
   matching digest, and Git blob object; mutable refs, trees, submodules,
   symlinks, and fuzzy/basename resolution are rejected.
4. **Pointer purity** — both historical seven-field wire cores keep their exact
   key names and order; only backend `detail_ref` may appear as the documented
   optional tail. Extra prose, extra authorization fields, nested `human_gate`
   data, unsafe refs, mutable review heads, and unresolved `self` during a
   transition fail validation.
5. **Complete Human channel** — material content requires factual status, all
   eight preflight assertions, bounded/separated independent expression, and
   all seven recommendation fields when dispatching. The recommendation's task
   or plan ref must be an explicit event ref, not merely a bootstrap file.
   Structured authorization fields and visible hidden-reasoning requests are
   rejected.
6. **Mixed-recipient fallback** — separable channels stay structurally
   separate. A machine-only or non-separable output must resolve a complete
   durable Human Brief whose path agrees with the pointer. A pointer-only waiver
   relocates Human content; it never deletes the obligation.
7. **Transition evidence** — dispatch, completion, foreground acceptance,
   publication candidate, and protected-publication entry validate request,
   result, event, policy, validator, protocol, ref, and proposed-transition
   bindings. Passing results with hidden violations are rejected.
8. **C2 external authority** — model payload fields never authorize a protected
   action. A trusted-looking JSON document and `trusted-host` CLI flag still
   fail unless a separately injected host verifier attests the context. The
   deterministic test mode is explicit and cannot masquerade as production.
9. **Drift-to-regression contract** — the append-only, privacy-safe ledger and
   record schema require occurrence two and later to name a matching negative
   fixture or a deterministic-impossibility exception with immutable foreground
   review evidence.
10. **Canonical bindings** — the protocol, adherence, initialization, backend
    work mechanism, task-input contract, and decision log now point to the
    executable gate while preserving the frozen pointer core and Human Speaker.

## Requirement trace

| Requirement | Evidence | Result |
| --- | --- | --- |
| Four provider bootstrap receipts | ChatGPT, Claude, Codex, Claude Code positive fixtures plus stale/head/digest/wire negatives | Pass |
| Seven recommendation fields | one omission case per field plus explicit-ref provenance case | Pass |
| Eight preflight fields | one omission case per field | Pass |
| Pointer keys/order/purity | extra key, order, prose, nested gate, mutable head, and strict YAML cases | Pass |
| Independent expression | sentence count (English and Chinese), separation, structured/text authorization, generic warning, hidden-reasoning cases | Pass |
| Mixed recipients | separable, non-separable complete/incomplete, waiver complete/missing Brief | Pass |
| Transition fail-closed | 21 transition cases, including missing/stale/malformed/failing/unresolved/forged/replayed evidence | Pass |
| Drift recurrence | first occurrence, matching fixture, missing/mismatched fixture, and reviewed deterministic exception | Pass |
| Determinism | full suite under different timezone/hash-seed environments produced identical bytes | Pass |
| Source mailbox neutrality | candidate-clean-filter blob identities match base for INBOX/OUTBOX/STATE/HUMAN_BRIEF | Pass |

Full commands and quantitative evidence are in
`.ai/CODEX_REPORTS/human-ai-communication-compliance-gate-validation-0001.md`.

## Mechanically enforced now

- deterministic class lookup and unknown-event fail closure;
- strict input parsing, versioned schemas, role/wire and receipt checks;
- immutable Git/test-only reference resolution and digest binding;
- pointer, Human content, recommendation, fallback, expression, and preflight
  checks;
- transition-result consistency and current policy/validator binding;
- test-only versus externally verified C2 authority boundary;
- drift-record recurrence obligations;
- deterministic JSON and stable documented exit codes.

## Still outside this implementation

- direct interception of ChatGPT, Claude, Codex, or Claude Code UI output;
- a production trusted-host identity/signature mechanism and durable replay
  store (the callback boundary is present; the external host must supply both);
- automatic state persistence, mailbox mutation, transition execution, rollback,
  runtime/Coordinator integration, polling, scheduling, or unattended action;
- machine proof of cognition, sincerity, originality, emotional state, or
  literary/professional quality;
- automatic resolution of semantic policy conflicts.

These are explicit limits, not implied capabilities. Any live Communication
Gateway or production host integration remains a separate Human-gated task.

## Contract conflict retained as evidence

The legacy `3号方案.md` Engine-B wording still requests XML chain-of-thought.
Current platform policy and the published communication protocol prohibit
requesting, storing, or validating hidden/private chain-of-thought. That legacy
file was forbidden in this task and remains unchanged; the executable gate
enforces the current prohibition and the conflict should be handled only by a
separately authorized constitutional cleanup.

## Deviations and dependencies

- Deviations from allowed paths: none.
- New network installs: none.
- Existing runtime used: Python 3.14.6, PyYAML 6.0.3, jsonschema 4.26.0,
  referencing 0.37.0.
- Source publication, PR, merge, and activation: not performed and not
  authorized.

## Remaining real Human decision

Foreground ChatGPT must semantically review the exact candidate head. After
that review, the Human decides whether to authorize any later source/master
publication or production trusted-host/runtime integration; neither decision is
pre-authorized by this implementation.

## Independent expression

I find this gate valuable because it turns a social promise into inspectable
evidence without pretending that evidence is authority. The trusted-host
callback boundary is the most important restraint here: a document should not
be allowed to certify its own provenance. I also like that ordinary conversation
remains ordinary—governance becomes brittle when every sentence is treated as a
state transition.
