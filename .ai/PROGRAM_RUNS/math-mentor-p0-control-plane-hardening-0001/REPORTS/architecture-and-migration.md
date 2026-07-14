# P0 Control-Plane Architecture And Migration Boundary

## Outcome

This P0 establishes a deterministic, read-only control plane for Math Mentor.
It does not activate a runtime, Coordinator, teaching session, student-state
writer, review scheduler, node generator, bridge generator, or publication
path.

The control plane separates six questions that were previously easy to
conflate:

1. Which repository contracts are authoritative for a requested action?
2. What maturity level is actually supported by evidence?
3. Which historical artifacts are importer-only or superseded?
4. Which immutable canonical UUID owns each direct-root node record?
5. Can heterogeneous source shapes be normalized without promoting truth or
   readiness?
6. Does a trusted external Human grant authorize an exact effect, and does the
   independently evaluated asset evidence admit the requested read-only use?

## Data Flow

```text
fixed source snapshot
  -> root-only corpus discovery
  -> strict structural parse
  -> immutable UUID registry + typed aliases
  -> open conflict registry (fail closed)
  -> read-only normalized node
  -> pure admission evaluation

external authenticated Human channel
  -> host trust-boundary adapter
  -> sealed AuthorizationContext for one exact effect
  -> pure authorization decision
  -> admission evaluation (authorization cannot override evidence failure)
```

The two final decisions remain independent. An authorization allow cannot
repair an identity, schema, readiness, provenance, or prerequisite failure.
Likewise, an otherwise admissible asset cannot authorize a write.

## Authority Boundary

The authority registry is a derived index of the canonical eight-tier order
in `.ai/PROTOCOL.md`; it does not create authority. Lower numbered tiers have
higher authority, while sources inside one tier are unordered:

1. platform, system, developer, and safety instructions;
2. current explicit Human instruction;
3. authenticated current Human-approved task-specific permission or override;
4. Plan 3 and the Cybernetic Citizen contract;
5. durable repository control protocols;
6. relevant Math Mentor domain-authority protocols;
7. ordinary current signals and task operational details; and
8. routing documents and historical evidence.

An ordinary model-authored packet remains tier 7 even when it contains
approval-shaped words. It cannot become the distinct tier-3 authenticated
Human override. Action records separately identify sources that may grant an
effect, sources that govern and constrain it, and operational-detail sources
that may narrow scope but never grant authority.

## Canonical Corpus Boundary

Only tracked YAML files that are direct children of
`Pure_Math_Intuition_DB/` and are not root bridges or the structural schema are
node candidates. Nested and `_Staging_*` paths are evidence-only exclusions.
They cannot win identity resolution by precedence and cannot be admitted by
claiming a canonical role in a request payload.

The source snapshot is `master@764d03d7d0a9ad553f4f3868699b06d9de5553ea`.
Generated registries bind their evidence to that snapshot even when the
generator is rerun from a descendant implementation commit.

## Identity Boundary

The sole node primary key is `canonical_uuid`. Exact domain IDs, exact root
paths, exact filenames, versioned split-roadmap IDs, and reviewed historical
values are typed aliases. The initial UUIDv5 assignment uses an exact root path
only as a deterministic bootstrap seed; after an accepted crosswalk is
materialized, moves, merges, splits, and replacements require a durable Human
resolution instead of silent recomputation.

No identity is resolved by numeric suffix, basename alone, fuzzy title,
roadmap order, or staging precedence. Candidate edges remain unapproved and
`consumer_allowed` remains false throughout P0.

The frozen independent review recognized ASCII `(n_*)` tags. Seven E4 nodes
use the fullwidth form `（n_*）`; P0 records those exact values as diagnostic
evidence but does not normalize them into edges. This preserves both the
reviewed 473/420 baseline and the previously invisible seven-file method
delta.

The empty Human resolution overlay is an intentional boundary, not missing
work. Genuine semantic disagreements remain open until the Human Speaker
supplies source-bound adjudication.

## Normalization Boundary

The adapter recognizes the four observed schema eras and produces a stable
structural view with provenance. It does not edit the source YAML. Every result
states that mathematical truth was not evaluated and that consumer admission
was not granted.

Source lifecycle fields are preserved as observations. Values such as
`teaching_ready`, validator status, bridge readiness, or disposition are not
converted into new canonical state by normalization.

## Authorization Boundary

Business payloads are untrusted. In particular, `human_gate`, scope labels,
and model-authored approval language are descriptive only. A production host
must authenticate an opaque handle outside the business request and inject a
sealed grant through the trust-boundary adapter.

The deterministic adapter and fixture records are test-only. Production mode
rejects them. P0 contains no real secret, signing key, token, credential, or
production authentication transport.

Authorization is bound to task, request, objective digest, source head,
operation, effect class, exact resources, validity interval, revocation state,
nonce/replay snapshot, and pre/post Human gates. Missing, stale, mismatched,
forged, replayed, or out-of-scope evidence fails closed.

Requests, grants, and decisions must be factory-issued and retain their full
issuance fingerprint. Directly constructed, copied, duck-typed, serialized and
rehydrated, or post-issuance-mutated objects are untrusted even if a caller
copies private-looking fields or methods.

The verifier constructs a coherent request/grant snapshot, verifies that
snapshot against the module-owned issuance record, and then consumes only the
checked snapshot. It never validates an object and then rereads caller-owned
fields for the current decision. The replay set is also captured by one exact
immutable-set read. This closes check/use field-replacement seams without
claiming process isolation or a durable trust store.

Secret classification is a fixed module policy floor rather than a caller
method. It applies case-insensitively to `.env` variants, SSH/private-key
material, credential names and directories, Git/cloud/tool credential stores,
and common key-container suffixes. Control characters, Windows ADS syntax,
trailing dot/space components, wildcards, and non-normalized paths are rejected
before classification. Tests use path strings only and never read secrets.

Replay handling is intentionally narrower than a production replay defense.
The host may supply an immutable point-in-time set of already-consumed nonces,
and P0 denies a nonce found in that snapshot. P0 does not update the snapshot,
atomically consume a newly allowed nonce, persist nonce state, or coordinate
across processes. Those capabilities remain missing runtime layers rather than
being implied by a static `replay_status` label.

## Admission Boundary

Admission is a pure read-only evaluation over an exact asset and blob. It keeps
authorization, identity, schema, readiness, validator, provenance, and
prerequisite dimensions separate. It cannot write state or promote learning
status.

Admission requests and trusted admission evidence are issued through internal
factories and tracked by object identity plus a full-field fingerprint.
Post-issuance mutation through `object.__setattr__`, direct construction,
copying, serialization reentry, and duck typing fail closed. Test fixture
evidence always identifies itself as `test_fixture` and is rejected outside
test mode. Admission decision dimension and restriction mappings are exposed
as read-only mappings. This is static in-process hardening, not a production
evidence transport or durable trust store.

Each admission issuance record retains a separate issuer-owned snapshot and
returns a fresh consumption copy only after the caller object still matches its
fingerprint. Admission then uses that copy throughout evaluation. Replacing a
caller request or evidence field after the check cannot relax a state-write
request, promote readiness, or rewrite an asset binding.

Legacy review prompts and tables are read-only importer inputs. An R5 `PASSED`
claim cannot become `graduated`, and a legacy artifact cannot be executed by
relabeling its role. Staging, structural, duplicate, stale, and mismatched-blob
evidence remains blocked or quarantined.

All 229 staging assets are excluded before identity resolution. The diagnostic
scanner may parse them read-only to measure 213 parse passes, 15 parse failures,
195 basename shadows, and 180 strict-ID overlaps; none of those measurements
creates staging precedence or admission.

## Required Migration Order After P0

1. ChatGPT reviews the exact development-branch head and the Human gate closes
   this P0 candidate.
2. Humans adjudicate only the genuine identity conflicts needed by a small
   certified pilot; all other records may remain unbound.
3. A separately authorized task selects a production authentication and
   admission-evidence adapter, atomic durable nonce-consumption store, and
   audit store. Test fixtures must not cross that boundary.
4. Validators certify exact node blobs; the certified subset alone can enter a
   Human-triggered read-only vertical slice.
5. A legacy importer may map old review evidence into a quarantine/staging
   model, never directly into production graduation.
6. Persistence, rollback, observability, scheduler behavior, and E2E evaluation
   require their own Human-approved implementation scope before activation.

## Explicit Limitations

- P0 performs structural parsing, not semantic review of all 667 node bodies.
- P0 records candidate identity evidence but does not approve semantic
  equivalence.
- No prior accepted crosswalk existed at the fixed base. The generated file is
  the bootstrap materialization; future regeneration must preserve accepted
  UUID rows through a reviewed migration input.
- Stage 0 data is historical, non-authoritative evidence and is labeled with
  its older source head and known limitations.
- The combined roadmap is a prohibited input and was not read.
- Maturity evidence in this task reaches static tests only; it is not runtime
  or production evidence.
- The corrected implementation head
  `eebd2688f099d1be035576793a70d135086d4fa6` statically addresses the three
  independent-review blockers, replay clarification, and adversarial snapshot
  findings and passes 104/104 tests. Acceptance still binds to the future
  report commit itself after exact-head review.
- Immutable Git blobs at the corrected implementation head, not raw Windows
  worktree bytes, prove committed generated output. Worktree JSON is parsed
  and canonicalized separately so CRLF conversion cannot create a false drift
  result or a false byte-proof claim.

## Remaining Human Decisions

- Accept or reject the exact candidate head after ChatGPT review.
- Adjudicate individual identity conflicts required for the certified pilot.
- Choose the pilot subset and its semantic certification threshold.
- Select the production authentication, persistence, audit, rollback, and
  privacy design in later separately scoped tasks.
