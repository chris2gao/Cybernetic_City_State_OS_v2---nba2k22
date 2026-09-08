# OS execution foundation: diagnosis and decision

Baseline: `3dc058a1a3cf393b936025f43fd737b0848937b4`.
Frozen evidence only: `b79922dce8975add161de69d4614543644ef52f5`.

## What the evidence supports

The original Opus audit found discrepancies between declared policy and observed
artifacts. Its historical 1/49 and 2/6 samples do not establish a causal effect,
a 33% ceiling, or a deletion criterion. CORRECTION-001 invalidated mixed-ref
measurements; CORRECTION-002 withdrew the alleged duplicate-key defects in two
valid master merge fixtures. Replayability fixes source identity, not an oracle,
measurement unit, population, or historical execution authenticity.

The current master has real working primitives: preflight reads Git, path_ledger
measures committed/worktree paths, quiet_verify launches checks, and the workflow
runner verifies artifact hashes and predecessor links. They are not empty shells.
They are manually invoked validators, not an unbypassable execution system.

Concrete defects inspected on this baseline:

1. The entry's wrapped `task_packet` shape differs from the preflight/ledger's
   top-level reads. `prohibitions` and publisher expected-head names also differ.
2. A physical preflight is not a complete task admission validator; absent task
   fields must not be silently represented as a valid task context.
3. The required quiet entry discards successful output and truncates failure
   output before persistence, contradicting the full-log obligation.
4. Section 2 requires byte-identical derivation even where section 7 explicitly
   permits T1 implementation choices. Existing delegated implementation discretion
   must be distinguished from a new load-bearing Human decision.
5. The workflow runner's payload checks do not consume all required schema fields;
   declared tests/writes/role names do not establish actual execution/independence.

## Decision and complete target

Build a foreground managed verification route, wire its machine result into
candidate readiness, correct the identified entry/validator contradictions, and
provide real exact-candidate pilots. Retain accurate boundaries for the existing
artifact validator. Final independent acceptance and Human integration are separate
requirements, not implied by implementation-team tests. The wider OS objective is
not complete until its requested adoption/integration has been resolved explicitly.

The first implementation uses a candidate-tracked, strict JSON check plan to avoid
inventing another YAML dialect for process execution. JSON is deliberately confined
to this new process contract; existing YAML contracts and legal merge fixtures are
not rewritten. All checks are required. No empty list, conditional skip, retry,
cache, resume, background delivery, daemon, database or generic DAG.

An invocation binds a full candidate SHA, exact tracked plan, runner identity,
runtime information, and a new external attempt directory. It runs argv directly
without shell interpolation, streams stdout/stderr to separate complete files,
records raw exit codes and start/end records, stops on the first failure/error,
and explicitly classifies remaining checks as not_run. Only all required checks
actually completed with their expected code and unchanged clean source can pass.
Timeout, unreadable source, malformed input, missing final record, changed input
or damaged evidence fail closed. A consumer recomputes the verdict from the
candidate plan and records rather than accepting a hand-written passed flag.

Guarantees are conditional on using the unmodified managed entry and appropriate
foreground checks. This is not a sandbox, does not prove semantic adequacy of the
checks, and cannot authenticate history against the same full-access actor who can
rewrite code/logs or bypass it. Clean Git checks do not capture ignored inputs,
external services, transient reverted writes or all environmental nondeterminism.
Do not turn these limitations into a claim that policies do not exist: obligation,
detector, consequence, activation and tamper resistance are different properties.

Any independently controlled CI/publisher enforcement or runtime activation needs
an explicit Human deployment decision. Merely adding a hook or an editable receipt
does not establish it. The local transport remains subject to the existing hook.

## Maturity references

Consulted official sources, adapting concepts rather than installing platforms:

- GitHub Actions workflow dependency and skipped-check semantics:
  https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
  and https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- Temporal execution history and attempt identity:
  https://github.com/temporalio/temporal/blob/main/docs/architecture/history-service.md
- Git object identity is content identity, not execution attestation:
  https://git-scm.com/docs/git-hash-object

## Verification and migration

Before business edits the draft boundary was resolved to include the existing
workflow runner and its tests, because its required-field omission is in the named
diagnosis. No frozen source is writable. Each finding needs an actual regression,
not only prose. Exercise actual subprocesses and temporary Git repositories; test
stale candidates, malformed types, skipped checks, timeout, spawn failure, dirty
source, source mutation, byte-exact logs and corrupt/missing records. Run existing
static checks and compare the baseline. A new clean candidate pilot must run through
the actual entry. Preserve failed attempts; do not relabel them successful.

Migration is review-gated: no deletion of an existing mechanism, no global activation
and no old review waiver. The final handoff must list what is mechanically checked,
what remains a Human obligation, and every unimplemented or unverified requirement.
