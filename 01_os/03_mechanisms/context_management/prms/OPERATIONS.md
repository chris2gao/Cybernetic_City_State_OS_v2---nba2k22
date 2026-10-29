# PRMS candidate operator guide

This is a foreground extension of context management, not a deployed service.
Use Python 3 with PyYAML, jsonschema and pytest for verification, and Git. The
read-only GitHub source adapter uses the existing authenticated `gh` CLI. No
command installs tools, provisions credentials or creates a GitHub repository.

## Source discovery and context loading

From the Core checkout, invoke:

```text
python -B 01_os/06_execution/boot/context_management/prms/cli.py catalog --repo-root . --commit <exact-40-char-source> --repository <owner/repo> --output <external-catalog.json>
python -B 01_os/06_execution/boot/context_management/prms/cli.py recover-context --repo-root . --commit <exact-40-char-source> --repository <owner/repo> --session <current-session> --role <role> --task <task> --stage 06 --budget-bytes 200000 --human-choice-source <current-Human-instruction-ref> --output <external-context.json>
```

Use `--action execution_completion` to load the existing minimum-work-unit boot
obligations, or an action class from the existing mechanism-activation registry.
The candidate's frozen `loading_rules_v1.yml` controls these loading obligations.
It does not replace the action constitution or execution gate.

`--optional` proposes a Core source; `--selected` selects that disclosed source
under this session's Human instruction. A different session must receive its own
choice. Missing required sources and insufficient budgets cannot produce READY.
Budgets are explicit UTF-8 byte limits; they are not claims of exact model tokens.
L0–L4 context depth must not be confused with mechanism-effectiveness levels.
Recovery `history_choice.depth` accepts L0 (minimum boot), L1 (current), L2
(selected source excerpts), L3 (selected original events, the compatibility
default), or L4 (all reachable role-record versions and audit records). Mandatory
current-task original evidence remains full at every optional depth. L4 traverses
the frozen Git history, deduplicates exact path/content versions and retains
original bytes. Other roles are filtered. The default 128-commit bound can be
explicitly raised to 1000; any remaining commit or budget omission makes the
audit BLOCKED. A bounded audit never claims a complete history.

G2 APIs are `discover_g2`, `plan_domain_context`, `choose_domain_context` and
`assemble_domain_context`. They consume the same frozen repository/commit and
domain binding. Formal G2 records and 08 module candidates have distinct status.
An absent 09 catalog remains UNINITIALIZED even when task-selected 08 sources are
successfully read. P00 references Core governance; no domain body replaces it.
Candidate cards retain per-document blob inventories and directory-tree
fingerprints without reading those bodies. `compare_domain_catalog` revalidates
the frozen catalog and compares a newly frozen source, marking only changed
module records or body dependencies stale. It reports missing originals, added
modules and filtered references separately. A changed repository commit alone
does not invalidate unrelated, byte-identical module sources.

Retain the expected plan and current-session choice on the host. Call
`verify_recovery(source, receipt, expected_plan=plan, expected_choice=choice)` to
re-resolve source bytes, directory coverage and required paths. The domain verifier
also verifies the Core receipt. A receipt's self-reported hashes or READY label
alone are insufficient. These interfaces verify loading, not model comprehension.

Local source repository names are host-provided routing facts. The remote source
adapter resolves the named GitHub repository directly. Neither a role label nor a
context receipt authenticates a Human or grants filesystem/execution rights.

## Isolated persistent-state exercise

The local state adapter uses real Git objects and an atomic expected-parent ref
update. Create state outside the Core/domain code checkout:

```text
python -B 01_os/06_execution/boot/context_management/prms/state_cli.py init-sandbox --state-root <new-external-temp/state.git> --sandbox-parent <external-temp> --isolated-test-only --output <reply.json>
```

The state CLI also provides `register`, `claim`, `append`, `checkpoint`, `assign`,
`refresh-index`, `recover` and `search`. Mutating calls require a session, role,
operation ID, exact expected head, state version and owner epoch, plus a JSON
payload when applicable. Invoke `--help` for their exact flags. No CLI write is
allowed without the explicit isolated-test marker. JSON replies contain statuses
and source commitments, never access tokens.

Register with `definition: {role_type_id, version}`, `domain_id` and
`state_repository_id`. An append contains `event_id`, a typed evidence `kind`,
`source_refs` with immutable repository/commit/path and the actual content. Source
refs are recorded references, not independently verified observations. The writer
records UTC persistence time separately from observation time, using UNKNOWN when
observation time was not supplied. Corrections append a new event referring to
the retained original. Versioned event and CURRENT schemas are canonical here.

Only the host issues isolated session capabilities. It can restrict allowed roles,
tasks and operations. Saving an assignment's Human reference does not expand that
host scope. Revocation rejects later calls through that capability. Local code and
filesystem access remain cooperative; a same-principal direct Git writer can
bypass this library. `require_enforced()` deliberately refuses production claims.
Every write interface, including full copy, uses the same operation authorization.
A task-scoped session cannot turn a caller-supplied approval string into full-copy
authority. The host must bind `allowed_copy_scopes` to the exact source role,
frozen source commit, target role and approval reference; mismatches and revocation
reject the copy before any state publication. Fully unrestricted isolated test
sessions remain test-host grants, not authenticated production sessions.

Checkpoint publication commits its complete event-hash manifest and CURRENT in
one Git tree. Recovery verifies those hashes and preserves exact Human-decision
events. It cannot recover unsaved conversation or hidden model reasoning.

`copy_all_memory` freezes the source commit, copies complete content bytes into
the target snapshot and verifies the manifest. The target has a new identity and
CURRENT. Operational owner, assignment and CURRENT authority do not transfer.
Original records remain in Git history. Duplicate operation IDs reconcile instead
of repeating a copy; conflicting requests fail closed.

## Derived memory and governance

Indexes declare their exact frozen event scope, indexed/filtered counts and source
commit. Search no-hit means no match within that scope. Source excerpts preserve
evidence kinds and omissions; they never replace the original Human decision.
Content-hash changes invalidate only affected dependencies. Unknown task states
stay visible. Task-series recovery reads explicitly selected run metadata and
valid closure objects; closing a chat or completing all member rows alone does
not fabricate a series-level Human closeout.

K1 proposals preserve scope, sources and falsifiers. A caller's review/approval
references do not make K2. `reconcile_experience_publication` consumes matching
Human and independent-review records from the owner's freshly resolved published
master. This is record verification under the existing governance trust boundary,
not a new identity-authentication service or permission to publish or execute.

## Deployment prerequisites and acceptance limits

The dormant GitHub Git Database adapter implements prepare/commit/non-force ref
advance/readback and uncertain-result reconciliation. It does not provision a
repository or establish a permission boundary. Before production acceptance:

1. Human selects and authorizes a dedicated state repository and trust domain.
   Mutable CURRENT and credentials must not enter Core or domain code branches.
2. A separately authorized trusted ingress authenticates actual sessions and binds
   their assignments. Models receive no direct effective-state write credentials.
3. Platform permissions/rules reserve effective ref updates for the WriterGate.
   Old/read-only sessions must fail actual direct REST and Git writes. Higher
   platform administrators remain outside this guarantee.
4. Isolated GitHub CAS, staging faults, timeout/readback and delayed old-writer
   scenarios are executed with complete raw evidence. No blind external replay.
5. Real GPT/Codex new-window recovery is compared with frozen ground truth, and a
   different session performs final independent review. Human decides integration.

Without those prerequisites, report FENCING_NOT_ENFORCEABLE / NOT_RUN / BLOCKED
for the affected requirements. Local tests, publication records and source loading
cannot substitute for platform enforcement, a real model window or independent
acceptance. New-domain scaffolding and local merge fixtures do not upgrade any
existing domain. Core/master and domain/master remain protected publications.

## Reproducible verification and examples

The tracked run `01_os/_runs/run-20261029-os-prms-implementation-001/` contains
the unchanged original 48 acceptance obligations, a per-scenario test map, and
the managed verification plan. `acceptance.py --repo-root . --run-path <run>`
executes the offline suite in a fresh external temporary directory, reads actual
JUnit outcomes, requires all 48 mappings and reports each required proof scope.
Its zero exit status means its offline checks passed; it explicitly reports
`all_original_acceptance_passed: false` while external gates remain unverified.

`examples.py isolated-state --repo-root .` creates and removes only a temporary
isolated Git fixture, publishes CURRENT/checkpoint/assignment, rejects an old
session and verifies a new recovery package. All event content is labeled
synthetic. It cannot create an active role in this Core checkout.

`examples.py pinned-domain-source --repo-root .` reads actual immutable NBA PR18
sources through GitHub, verifies the thirteen candidate module identities and
task-selected P04/P09 bodies, and emits the actual G1/G2 catalogs and read proofs.
It performs no domain code write, game operation or REA invocation.
