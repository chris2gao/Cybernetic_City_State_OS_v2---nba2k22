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

## Admission Boundary

Admission is a pure read-only evaluation over an exact asset and blob. It keeps
authorization, identity, schema, readiness, validator, provenance, and
prerequisite dimensions separate. It cannot write state or promote learning
status.

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
3. A separately authorized task selects a production trust adapter and audit
   store. Test fixtures must not cross that boundary.
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

## Remaining Human Decisions

- Accept or reject the exact candidate head after ChatGPT review.
- Adjudicate individual identity conflicts required for the certified pilot.
- Choose the pilot subset and its semantic certification threshold.
- Select the production authentication, persistence, audit, rollback, and
  privacy design in later separately scoped tasks.
