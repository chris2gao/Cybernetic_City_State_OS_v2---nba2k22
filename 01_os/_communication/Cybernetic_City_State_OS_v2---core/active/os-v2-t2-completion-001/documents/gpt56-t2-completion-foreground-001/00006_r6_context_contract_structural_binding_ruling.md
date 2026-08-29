---
document_id: os-v2-t2-completion-001::gpt56-t2-completion-foreground-001::r6-context-binding-ruling-00006
task_id: os-v2-t2-completion-001
author_endpoint_id: gpt56-t2-completion-foreground-001
author_task_role: foreground_t2_completion_coordinator
purpose: adjudicate_R6_context_contract_structural_binding_and_continue_FIX_REQUIRED_correction
privacy_class: repository_shareable
---

# R6 foreground ruling: context contract structural binding

Verdict: **DETERMINISTIC_CLAIMABILITY_CLOSURE** over executor WIP
`5b9888eeefa13f6c352e1bf9f42207c3e45801b5`.

The executor correctly stopped after IR-001 provenance gating exposed that
`mechanism/context_contract_v1.yml` is unbound. The missing binding is not a new
Human semantic choice: the document is a fixed A04 contract schema, not an open
keyed collection.

## Work performed or requested

Foreground fresh-checked master/control/implementation heads, read the WIP diff,
read the exact context contract and evaluator structural binding, inspected the
v4 claim-site contract, and tested the proposed profile in a temporary copy.
No implementation-branch files were changed by foreground.
## Exact structural ruling

Register the exact opaque discovery identity:

`mechanism/context_contract_v1.yml: context_contract_v1`

Add profile `context_contract_v1` with:

- `root_child_keys: declaration_name`
- `transparent_containers: *transparent_contract`
- `[minimum_effective_context] -> declaration_name`
- `[minimum_effective_context, derivation_inputs] -> declaration_name`
- `[minimum_effective_context, load_set] -> declaration_name`
- `[minimum_effective_context, exactness] -> declaration_name`

No position in this document is ruled `instance_identity` by this ruling. Load-set
entries are values consumed inside an already-claimed load-set region; they do not
need global declaration claimability. Do not add a default document profile, path
inference, tail matching, generic wrapper inference, or global `contract`
transparency.
## Verification of the ruling

In a temporary copy of the exact WIP acceptance package, foreground applied only
the profile above. Baseline P21-P27 all returned PASS. Using shared transparency
without `contract` left V4MT01 broken; using profile-scoped
`*transparent_contract` made the existing V4MT01 invariant pass. This is why the
wrapper grant is profile-scoped and exact.

## IR-001 family completion requirement

The WIP `_claim_sites()` and accepted `bound_nodes()` contracts both say that an
adapter selecting a semantic claim site must use structural provenance. Therefore
continuation must audit every remaining document-wide `walk_nodes(doc.data)` /
`walk_leaves(doc.data)` semantic selector. If it chooses a fact because a key or
value matches semantic vocabulary, route that selection through claimable
`bound_nodes` / `bound_leaves`. Raw traversal remains valid only as a structural
sub-scan inside a value already reached from a claimable site, or as exact
referential-existence proof that does not itself mint semantic ownership.

At minimum re-check preload positions, freshness binding, route/window binding,
family requirements, mechanism-separation regions, and fallback positions. Do not
fix only the independent review's one `failure_states` witness.
## Remaining correction obligations

IR-002 is still open. The explicit
`model_route_binding.route_receipt.missing_or_stale_or_inconsistent` policy must
be decision-bearing for A12: `fail_closed` or an equivalent supported visible
failure role passes; absent, unknown, contradictory, `best_effort`, or any other
non-fail-closed policy is non-pass. Implement the family, not a literal
`best_effort` blacklist, and apply accepted polarity semantics.

Persist direct regression cases for IR-001 through IR-004; one-shot probes are
not the completion evidence. After all four families are closed, rerun inherited
v3/v4 with actual exit codes, regenerate affected provenance/trace/inventory and
P2-2 evidence, then create a new freeze receipt, refreeze report and exact result
pointer. Preserve the old frozen candidate and FIX_REQUIRED review unchanged.

## Supportability rationale

A04 owns the context contract slots; F02-A owns polarity parity; F03-D owns typed
machine-observable subject binding; correction-003 owns evaluator-side structural
claimability. The ruling adds no new business semantics.

## Feasibility rationale

All required edits remain inside the current successor-v4/T2 completion allowlist
and are forward corrections from `5b9888ee`. Stage01-03, Stage05, master, canonical
implementation and history rewriting remain outside scope.

Stop and return only if a genuinely new open-keyed-vs-contract-field structural
choice appears that cannot be derived from an existing contract, or if another
load-bearing semantic rule is required.