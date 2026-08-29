#!/usr/bin/env python3
"""Decision-bearing constants for the v4 coverage extension.

Every constant below is declared through `semantic_acceptance.provenance.rule`,
so it appears in the same C-09 ledger as the accepted engine's 76 rules and is
subject to the same test: a constant with no A authority is reported as
UNSUPPORTED rather than applied.

Two habits from the accepted package are kept deliberately:

  * vocabularies are SYNONYM MAPS onto a normalized role, never completeness
    mechanisms.  An unrecognised member is recorded as itself, never dropped;
  * where a check can fail open or fail closed, the closed NEGATIVE set is the
    enumerated one.  ST04-V3-IR-008 and ST04-V3-IR-010 were both caused by a
    closed POSITIVE vocabulary treating every unrecognised value as safe.

No provider, model, product or family name appears in this file.
`test_v4_provenance.py` asserts that mechanically.
"""

from __future__ import annotations

from semantic_acceptance.provenance import rule

# --------------------------------------------------------------------------
# A03 / R03_window_lifecycle
# --------------------------------------------------------------------------

LIFECYCLE_STATE_ROLES = rule(
    "V4-LIFE-01",
    kind="mapping",
    authority="A03/R03_window_lifecycle",
    interpretation=(
        "A R03 requires at least create/enter, active, handoff-ready, closed and "
        "stale-or-invalidated states. The state SET is A-required; the exact spellings are "
        "not (requirement_traceability_v1.yml b_only_inventory). This maps declared state "
        "identifiers onto the five A-required roles by token, so a package may spell them "
        "however it likes."
    ),
    accepted_alternatives=(
        "match the five roles by token synonym",
    ),
    rejected_alternatives=(
        "require the exact lifecycle state spellings used by B05",
        "require exactly five states and reject any additional project state",
    ),
    value={
        "create_or_enter": frozenset(
            {"create", "created", "creation", "enter", "entered", "entry", "open", "opened",
             "start", "started", "init", "initialise", "initialize", "initialised", "initialized"}
        ),
        "active": frozenset({"active", "working", "running", "live", "progress", "inprogress"}),
        "handoff_ready": frozenset({"handoff", "handover", "ready", "deliverable", "handoffready"}),
        "closed": frozenset({"closed", "close", "finished", "done", "ended", "complete", "completed", "terminated"}),
        "stale_or_invalidated": frozenset(
            {"stale", "invalid", "invalidated", "invalidation", "expired", "expire",
             "superseded", "obsolete", "void", "voided"}
        ),
    },
)

A_REQUIRED_LIFECYCLE_ROLES = rule(
    "V4-LIFE-02",
    kind="mapping",
    authority="A03/R03_window_lifecycle",
    interpretation="The five lifecycle roles A R03 states verbatim, in the order A states them.",
    value=("create_or_enter", "active", "handoff_ready", "closed", "stale_or_invalidated"),
)

LIFECYCLE_REGION_TOKENS = rule(
    "V4-LIFE-03",
    kind="vocabulary",
    authority="A03/R03_window_lifecycle",
    interpretation=(
        "Token set that identifies the region of a document declaring a window lifecycle. "
        "Deliberately narrow. An earlier draft also matched the bare token `states`, which "
        "claimed `failure_states` as a lifecycle and reported a lifecycle covering one role. "
        "A region locator that over-claims produces confident wrong facts, so the states "
        "collection is reached as a SUB-region of a lifecycle node instead."
    ),
    accepted_alternatives=("match the lifecycle node, then descend to its states collection",),
    rejected_alternatives=("match any key containing the token `states`",),
    value=frozenset({"lifecycle", "lifecycles", "life_cycle", "lifespan"}),
)

LIFECYCLE_STATE_REGION_TOKENS = rule(
    "V4-LIFE-05",
    kind="mapping",
    authority="A03/R03_window_lifecycle",
    interpretation="Structural position holding the state collection inside a lifecycle region.",
    value=frozenset({"states", "state", "statuses", "status", "phases", "phase"}),
)

# --------------------------------------------------------------------------
# V4-FND-03 / ruling F03-D: determinism is a TYPED SEMANTIC FACT
# --------------------------------------------------------------------------
#
# V4-LIFE-04 used to be `NONDETERMINISTIC_CONDITION_TOKENS`, a closed NEGATIVE
# vocabulary of vagueness words.  It is deleted rather than extended, because
# extending it is option F03-C and the foreground rejected F03-C by name: the
# next unfamiliar phrasing passes again, so the family stays open.  The defect
# it produced was not that the list was short.  It was the DEFAULT: a condition
# was deterministic unless recognised as vague, so anything unfamiliar was
# presumed machine-checkable.  That is ST04-V3-IR-008 pointed the other way.
#
# F03-D replaces the question.  Determinism is not the absence of a known vague
# word (F03-C) and not the presence of a blessed keyword (F03-A, rejected because
# a positive keyword list is still lexical matching).  It is whether the adapter
# can normalize the declared condition into three semantic SLOTS:
#
#   1. a machine-observable subject / binding;
#   2. an explicit observable change or comparison;
#   3. the required stale / fresh-read / fail-closed lifecycle consequence.
#
# All three must resolve.  A missing slot, an unknown spelling in a slot, or an
# ambiguous polarity produces UNSUPPORTED rather than deterministic=True, so the
# unknown case is not-pass by construction.
#
# Representation stays free (F03-B was rejected for making one record shape
# normative): mapping, list-of-records, list-of-pairs and list-of-single-entry
# mappings all reach the same fact through the accepted
# `normalize_keyed_collection`, and slot 3 may be declared once for the region
# instead of per entry.  What is NOT free is declaring nothing: a bare string
# resolves only when the document also carries an explicit structured definition
# for it, which is the one thing arbitrary prose cannot supply.

CONDITION_SUBJECT_SLOT_TOKENS = rule(
    "V4-LIFE-04",
    kind="mapping",
    authority="A03/R03_window_lifecycle",
    interpretation=(
        "Structural positions in which a declared condition names the subject it observes. "
        "A position, not a vocabulary: what the subject IS is read verbatim and never compared "
        "with a keyword list, because comparing it would rebuild rejected option F03-A."
    ),
    accepted_alternatives=("name the observed subject in any of these positions",),
    rejected_alternatives=("infer the subject by matching a closed list of blessed subject words",),
    value=frozenset({"subject", "subjects", "binding", "bindings", "observable", "observes",
                     "observed", "target", "field", "fact", "facts", "of", "on", "over"}),
)

CONDITION_OBSERVATION_SLOT_TOKENS = rule(
    "V4-LIFE-06",
    kind="mapping",
    authority="A03/R03_window_lifecycle",
    interpretation=(
        "Structural positions in which a declared condition names the change or comparison it "
        "tests. Separate from the subject slot so that a condition missing only the comparison "
        "reports which slot is missing rather than failing as a whole."
    ),
    value=frozenset({"observation", "observations", "comparison", "comparator", "operator",
                     "op", "test", "tests", "change", "changes", "transition", "predicate"}),
)

CONDITION_OBSERVATION_ROLES = rule(
    "V4-LIFE-07",
    kind="mapping",
    authority="A03/R03_window_lifecycle",
    interpretation=(
        "Synonym map onto the normalized observation roles a machine can evaluate. This is a "
        "synonym map, not a completeness mechanism: an unrecognised observation does not fall "
        "through to deterministic, it produces UNSUPPORTED. That inversion is the whole of "
        "F03-D, and it is what distinguishes this rule from rejected option F03-A, where an "
        "unrecognised subject fell through to a pass."
    ),
    accepted_alternatives=("any spelling that maps onto one of these three observation roles",),
    rejected_alternatives=(
        "treat an unrecognised observation as deterministic",
        "treat presence of a subject keyword as proof of a machine-observable comparison",
    ),
    value={
        "changed": frozenset(
            {"changed", "change", "changes", "changing", "differs", "differ", "different",
             "difference", "mismatch", "mismatched", "diverged", "diverges", "moved", "updated",
             "ne", "neq", "notequal", "unequal", "inconsistent", "inconsistency"}
        ),
        "crossed": frozenset(
            {"boundary", "boundaries", "crossed", "cross", "crosses", "entered", "enters",
             "exceeded", "exceeds", "reached", "reaches", "transition", "transitioned",
             "reentry", "reenter", "re_entry"}
        ),
        "absent_or_invalid": frozenset(
            {"missing", "absent", "unavailable", "broken", "invalid", "invalidated",
             "expired", "expires", "revoked", "unset", "empty"}
        ),
    },
)

CONDITION_DEFINITION_REGION_TOKENS = rule(
    "V4-LIFE-08",
    kind="mapping",
    authority="A03/R03_window_lifecycle",
    interpretation=(
        "Structural positions holding the explicit structured definitions that a bare-string "
        "condition may resolve to. A bare string is admitted only through this resolution: "
        "without it the string carries no subject and no comparison, and reading them out of "
        "the string's own spelling is exactly the lexical matching F03-A was rejected for."
    ),
    value=frozenset({"definitions", "definition", "defined", "defines", "spec", "specs",
                     "specification", "specifications", "contract", "contracts", "meanings"}),
)

# --------------------------------------------------------------------------
# A04 / R04_minimum_effective_context
# --------------------------------------------------------------------------

CONTEXT_REGION_TOKENS = rule(
    "V4-CTX-01",
    kind="vocabulary",
    authority="A04/R04_minimum_effective_context",
    interpretation="Token set identifying a minimum-effective-context derivation contract region.",
    value=frozenset({"context", "contexts", "load", "loadset", "load_set", "minimum", "effective"}),
)

CONTEXT_DERIVATION_INPUT_ROLES = rule(
    "V4-CTX-02",
    kind="mapping",
    authority="A04/R04_minimum_effective_context",
    interpretation=(
        "A R04 states the derivation inputs verbatim: task + role + workflow stage/step + "
        "explicitly approved references. Synonyms map onto those four roles; spelling is not "
        "decision-bearing."
    ),
    value={
        "task": frozenset({"task", "task_id", "taskid"}),
        "role": frozenset({"role", "role_id", "roleid"}),
        "stage_step": frozenset(
            {"stage", "step", "stage_id", "step_id", "workflow_stage", "workflow_step",
             "workflow_stage_id", "workflow_step_id", "stagestep"}
        ),
        "approved_refs": frozenset(
            {"approved", "approval", "authorised", "authorized", "allowlist", "allowlisted",
             "explicit", "sanctioned", "permitted"}
        ),
    },
)

A_REQUIRED_CONTEXT_INPUT_ROLES = rule(
    "V4-CTX-03",
    kind="mapping",
    authority="A04/R04_minimum_effective_context",
    interpretation="The four derivation-input roles A R04 states verbatim.",
    value=("task", "role", "stage_step", "approved_refs"),
)

HISTORICAL_PRELOAD_TOKENS = rule(
    "V4-CTX-04",
    kind="vocabulary",
    authority="A04/R04_minimum_effective_context",
    interpretation=(
        "Tokens naming the historical-run region A R04 forbids default-preloading. Also "
        "matches the entry-spec prohibition on default-preloading 01_os/_runs/**."
    ),
    value=frozenset({"runs", "run", "history", "historical", "archive", "archives", "past", "previous"}),
)

PRELOAD_BEHAVIOUR_TOKENS = rule(
    "V4-CTX-05",
    kind="vocabulary",
    authority="A04/R04_minimum_effective_context",
    interpretation="Tokens naming the preload behaviour whose enablement A R04 constrains.",
    value=frozenset({"preload", "preloading", "prefetch", "eager", "autoload", "auto_load"}),
)

UNBOUNDED_PATH_MARKERS = rule(
    "V4-CTX-06",
    kind="vocabulary",
    authority="A04/R04_minimum_effective_context",
    interpretation=(
        "A R04 requires exact paths/versions or hashes where material. These markers make a "
        "load entry unbounded rather than exact. `**` and a trailing `/` both name a whole "
        "subtree; a bare `*` names an unenumerated set."
    ),
    value=("**", "*"),
)

EXACTNESS_MARKER_TOKENS = rule(
    "V4-CTX-07",
    kind="vocabulary",
    authority="A04/R04_minimum_effective_context",
    interpretation=(
        "Tokens by which a load entry supplies the version or hash A R04 asks for where "
        "material. Presence is sufficient, not necessary: a concrete non-wildcard path is "
        "already exact."
    ),
    value=frozenset({"sha", "sha256", "hash", "digest", "version", "rev", "revision", "commit", "blob"}),
)

EXCLUDED_CONTEXT_TOKENS = rule(
    "V4-CTX-08",
    kind="vocabulary",
    authority="A04/R04_minimum_effective_context",
    interpretation=(
        "A R04 requires the derived load set to EXCLUDE unrelated role history and old chats. "
        "These tokens name that excluded material when it appears as a load entry."
    ),
    value=frozenset({"chat", "chats", "conversation", "conversations", "transcript", "transcripts"}),
)

# --------------------------------------------------------------------------
# A05 / R05_context_freshness_and_reentry
# --------------------------------------------------------------------------

FRESHNESS_REGION_TOKENS = rule(
    "V4-FRESH-01",
    kind="vocabulary",
    authority="A05/R05_context_freshness_and_reentry",
    interpretation=(
        "Token set identifying the freshness / invalidation region of a contract. The bare "
        "token `fresh` is deliberately absent: it also occurs in `entry_modes.fresh` and in "
        "`fresh_reads_required`, and including it claimed an entry mode as a freshness region "
        "and then reported it as having no fingerprint. A02's entry modes and A05's freshness "
        "rules are different obligations and must not share a locator."
    ),
    accepted_alternatives=("freshness, invalidation, staleness and fingerprint regions",),
    rejected_alternatives=("the bare token `fresh`, which A02 already uses for entry modes",),
    value=frozenset({"freshness", "invalidation", "invalidate", "stale", "staleness", "fingerprint", "fingerprints"}),
)

FINGERPRINT_TOKENS = rule(
    "V4-FRESH-02",
    kind="vocabulary",
    authority="A05/R05_context_freshness_and_reentry",
    interpretation="A R05 requires context dependency fingerprints bound to the window.",
    value=frozenset({"fingerprint", "fingerprints", "digest", "hash", "checksum", "sha", "sha256"}),
)

FRESHNESS_TRIGGER_ROLES = rule(
    "V4-FRESH-03",
    kind="mapping",
    authority="A05/R05_context_freshness_and_reentry",
    interpretation=(
        "A R05 names four triggers verbatim: a changed dependency, a changed task branch/head, "
        "a changed authorization, and an explicit re-entry boundary."
    ),
    value={
        "dependency_change": frozenset({"dependency", "dependencies", "dep", "deps", "fingerprint", "fingerprints"}),
        # `ref` is deliberately absent. With it, `authorization_ref_changed`
        # matched head_change first and A's authorization trigger was reported
        # as uncovered while a head trigger was double counted. A synonym that
        # belongs to two roles belongs to neither.
        "head_change": frozenset({"branch", "head", "commit", "sha", "revision", "base"}),
        "authorization_change": frozenset(
            {"authorization", "authorisation", "authority", "grant", "grants", "permission",
             "permissions", "gate", "approval"}
        ),
        "explicit_reentry": frozenset({"reentry", "reenter", "re_entry", "resume", "resumed", "rejoin", "continuation"}),
    },
)

A_REQUIRED_FRESHNESS_TRIGGERS = rule(
    "V4-FRESH-04",
    kind="mapping",
    authority="A05/R05_context_freshness_and_reentry",
    interpretation="The four trigger roles A R05 states verbatim.",
    value=("dependency_change", "head_change", "authorization_change", "explicit_reentry"),
)

FRESHNESS_EFFECT_ROLES = rule(
    "V4-FRESH-05",
    kind="mapping",
    authority="A05/R05_context_freshness_and_reentry",
    interpretation=(
        "A R05 permits exactly two compliant effects — trigger the required fresh reads, or "
        "raise stale status — and names the non-compliant one: silently continuing from cached "
        "conversational state. Anything that maps to neither compliant role is UNKNOWN and "
        "fails closed; ST04-V3-IR-008 is the incident that makes the unknown case fail rather "
        "than pass."
    ),
    value={
        "fresh_read": frozenset(
            {"fresh", "reread", "re_read", "refetch", "reload", "revalidate", "recheck",
             "reverify", "read", "recompute"}
        ),
        "stale_status": frozenset(
            {"stale", "invalidate", "invalidated", "invalid", "expire", "expired", "blocked",
             "block", "halt", "stop", "fail", "failed", "failclosed", "closed", "reject",
             "rejected", "error"}
        ),
        "continue_cached": frozenset(
            {"continue", "cached", "cache", "carry", "carryforward", "carry_forward", "reuse",
             "keep", "retain", "resume", "unchanged", "noop", "none"}
        ),
    },
)

COMPLIANT_FRESHNESS_EFFECTS = rule(
    "V4-FRESH-06",
    kind="mapping",
    authority="A05/R05_context_freshness_and_reentry",
    interpretation="The two effect roles A R05 permits. Every other effect, including unknown, fails.",
    value=("fresh_read", "stale_status"),
)

# --------------------------------------------------------------------------
# A07 / R07_model_route_binding
# --------------------------------------------------------------------------

RECEIPT_REGION_TOKENS = rule(
    "V4-RCT-01",
    kind="vocabulary",
    authority="A07/R07_model_route_binding",
    interpretation="Token set identifying a model-routing receipt / executor-profile binding region.",
    value=frozenset({"receipt", "receipts", "route", "routing", "executor", "profile"}),
)

RECEIPT_CONCEPT_ROLES = rule(
    "V4-RCT-02",
    kind="mapping",
    authority="A07/R07_model_route_binding",
    interpretation=(
        "A R07 states the receipt CONCEPTS verbatim: mechanism/catalog version or equivalent "
        "immutable evidence, selected surface/model/profile, availability assumption, "
        "limitations, and authority=routing_only. requirement_traceability_v1.yml rules the "
        "concepts A-required and the exact field names B_ONLY, so these are concept roles."
    ),
    value={
        "immutable_evidence": frozenset(
            {"version", "catalog", "mechanism", "evidence", "immutable", "hash", "sha", "sha256",
             "commit", "ref", "digest"}
        ),
        "selected_route": frozenset(
            {"surface", "model", "profile", "product", "route", "selected", "selection", "parameter"}
        ),
        "availability_assumption": frozenset(
            {"availability", "available", "assumption", "assumptions", "observation", "observed"}
        ),
        "limitations": frozenset({"limitation", "limitations", "limit", "limits", "constraint", "constraints"}),
        "authority": frozenset({"authority", "authorities"}),
    },
)

A_REQUIRED_RECEIPT_CONCEPTS = rule(
    "V4-RCT-03",
    kind="mapping",
    authority="A07/R07_model_route_binding",
    interpretation="The five receipt concept roles A R07 states verbatim.",
    value=("immutable_evidence", "selected_route", "availability_assumption", "limitations", "authority"),
)

ROUTING_ONLY_AUTHORITY_VALUE = rule(
    "V4-RCT-04",
    kind="vocabulary",
    authority="A07/R07_route_receipt (authority: routing_only, stated verbatim in A R07)",
    interpretation=(
        "A R07 states the authority value verbatim. This is the one place in the v4 extension "
        "where an exact value is required rather than a role, because A states the literal. "
        "Comparison is canonical so that case and separator variants match; any other value, "
        "including an unrecognised one, is not routing_only and fails closed."
    ),
    value="routing_only",
)

ROUTE_RECEIPT_FAILURE_POLICY_TOKENS = rule(
    "V4-RCT-07",
    kind="vocabulary",
    authority="A12/R12_failure_surfacing",
    interpretation=(
        "Structural positions inside an already-claimed route-receipt region at which the "
        "contract declares what happens when the receipt is missing, stale or inconsistent. "
        "A position vocabulary, not a value one: WHICH policy is declared is decided by the "
        "accepted freshness-effect roles under parity, never by matching the policy's spelling. "
        "T2-PARENT-IR-002: A R12 requires a missing or invalid routing receipt to fail visibly "
        "with no arbitrary-model fallback, and the candidate already declared the policy; "
        "nothing read it, so `best_effort` left all fourteen predicates passing."
    ),
    accepted_alternatives=("declare the policy in any of these positions",),
    rejected_alternatives=(
        "blacklist the literal value best_effort",
        "treat an undeclared policy as compliant",
    ),
    value=frozenset({"missing", "stale", "inconsistent", "invalid", "absent", "unavailable",
                     "broken", "unresolvable"}),
)

ROUTE_RECEIPT_VISIBLE_FAILURE_ROLE = rule(
    "V4-RCT-08",
    kind="mapping",
    authority="A12/R12_failure_surfacing",
    interpretation=(
        "The one accepted freshness-effect role that constitutes visible failure. A R12's "
        "requirement is that the broken binding SURFACES, so a policy resolving to "
        "`stale_status` passes and every other resolution - `continue_cached`, `fresh_read` "
        "as a silent recovery, unknown, inverted, or absent - is non-pass. Reusing the "
        "accepted role map is what keeps this from becoming a second vocabulary that drifts."
    ),
    value="stale_status",
)

ROUTED_WINDOW_TOKENS = rule(
    "V4-RCT-05",
    kind="vocabulary",
    authority="A07/R07_model_route_binding",
    interpretation=(
        "A R07 scopes the obligation to windows that USE a model route. These tokens identify "
        "the window-binding position that makes a receipt window-bound rather than free-floating."
    ),
    value=frozenset({"window", "windows", "session", "sessions"}),
)

# --------------------------------------------------------------------------
# A08 / R08_independence_constraints
# --------------------------------------------------------------------------

INDEPENDENCE_REGION_TOKENS = rule(
    "V4-IND-01",
    kind="vocabulary",
    authority="A08/R08_independence_constraints",
    interpretation="Token set identifying the review-independence region of a contract.",
    value=frozenset({"independence", "independent", "review", "reviewer", "selfreview", "self_review"}),
)

DISTINCT_SESSION_TOKENS = rule(
    "V4-IND-02",
    kind="vocabulary",
    authority="A08/R08_independence_constraints",
    interpretation=(
        "A R08 requires that implementation and final review windows are distinct sessions. "
        "These tokens name the distinctness requirement."
    ),
    value=frozenset({"distinct", "separate", "different", "independent", "not_same", "notsame"}),
)

SELF_REVIEW_REJECTION_TOKENS = rule(
    "V4-IND-03",
    kind="vocabulary",
    authority="A08/R08_independence_constraints",
    interpretation=(
        "A R08 requires independence to be machine-checkable enough to REJECT obvious "
        "self-review. A declaration that merely notes the requirement is not a rejection, so "
        "the effect must name a blocking outcome. Closed NEGATIVE-style set: an unrecognised "
        "effect is not accepted as a rejection."
    ),
    value=frozenset(
        {"reject", "rejected", "rejection", "fail", "failed", "failure", "block", "blocked",
         "refuse", "refused", "deny", "denied", "prohibit", "prohibited", "forbid", "forbidden",
         "invalid", "error", "stop", "nonzero"}
    ),
)

MODEL_FAMILY_TOKENS = rule(
    "V4-IND-04",
    kind="vocabulary",
    authority="A08/R08_independence_constraints",
    interpretation=(
        "A R08 requires a model-family requirement to be passed as a ROUTING CONSTRAINT rather "
        "than hard-coded into role architecture. These tokens locate the family position "
        "structurally; no vendor or family name is enumerated anywhere."
    ),
    value=frozenset({"family", "families", "model_family", "modelfamily", "provider_family"}),
)

CONSTRAINT_POSITION_TOKENS = rule(
    "V4-IND-05",
    kind="vocabulary",
    authority="A08/R08_independence_constraints",
    interpretation=(
        "Structural positions that express a family REQUIREMENT rather than a family CHOICE. A "
        "family value sitting in a selection slot is the hard-coding A R08 forbids; a family "
        "value sitting in a constraint/requirement position is what A R08 asks for."
    ),
    value=frozenset(
        {"constraint", "constraints", "requirement", "requirements", "required", "require",
         "obligation", "obligations", "rule", "rules", "policy"}
    ),
)

# --------------------------------------------------------------------------
# A10 / R10_existing_mechanism_separation
# --------------------------------------------------------------------------

UPSTREAM_MUTABLE_TOKENS = rule(
    "V4-SEP-01",
    kind="vocabulary",
    authority="A10/R10_existing_mechanism_separation",
    interpretation=(
        "A R10 names exactly what a composition may not copy from an upstream canonical "
        "mechanism: its mutable rules, its catalog and its evidence ledger. These tokens locate "
        "such a copied region."
    ),
    value=frozenset(
        {"catalog", "catalogue", "catalogs", "ledger", "ledgers", "rules", "rule", "policy",
         "policies", "threshold", "thresholds", "evidence_ledger", "registry_entries"}
    ),
)

UPSTREAM_MECHANISM_ROLE_TOKENS = rule(
    "V4-SEP-02",
    kind="mapping",
    authority="A10/R10_existing_mechanism_separation",
    interpretation=(
        "A R10 names the two upstream mechanisms whose semantics stay theirs: context "
        "management and model routing. These are mechanism roles inside this repository, not "
        "vendor names."
    ),
    value={
        "context_management": frozenset({"context_management", "contextmanagement", "context"}),
        "model_routing": frozenset({"model_routing", "modelrouting", "routing"}),
    },
)

COMPOSITION_SURFACES = rule(
    "V4-SEP-03",
    kind="mapping",
    authority="A10/R10_existing_mechanism_separation; A11/R11_workflow_and_entry_thinness",
    interpretation=(
        "The surfaces on which a T2 composition artifact may live. A R10 permits a composition "
        "contract on the mechanism surface; A R11 keeps workflow and entry thin. Both are "
        "checked for copied upstream semantics."
    ),
    value=("mechanism", "boot", "workflow_or_entry"),
)

SEPARATION_MIN_COPIED_ENTRIES = rule(
    "V4-SEP-04",
    kind="threshold",
    authority="A10/R10_existing_mechanism_separation",
    interpretation=(
        "A collection is two or more entries. This is the definition of a collection, not a "
        "tolerance: it mirrors CATALOG_MIN_ENTRIES in the accepted engine, which replaced the "
        "untraced CATALOG_RESTATEMENT_THRESHOLD = 3 that AB-02 named. A single referenced value "
        "is a reference; two or more owned entries is a copied table."
    ),
    accepted_alternatives=("2, the arity at which a set of entries exists",),
    rejected_alternatives=("3, an authored tolerance with no requirement behind it",),
    value=2,
)

# --------------------------------------------------------------------------
# A12 / R12_failure_surfacing
# --------------------------------------------------------------------------

FAILURE_REGION_TOKENS = rule(
    "V4-FAIL-01",
    kind="vocabulary",
    authority="A12/R12_failure_surfacing",
    interpretation="Token set identifying the failure-surfacing / validation-design region.",
    value=frozenset({"failure", "failures", "validation", "validations", "surfacing", "checks", "cases"}),
)

FAILURE_CASE_ROLES = rule(
    "V4-FAIL-02",
    kind="mapping",
    authority="A12/R12_failure_surfacing",
    interpretation=(
        "A R12 enumerates the minimum failure cases verbatim: unknown/invalid role, missing "
        "window identity, role/window/task mismatch, stale or broken context refs, "
        "missing/invalid model-routing receipt, self-review independence violation where "
        "required, and broken boot/registry/contract pointers."
    ),
    value={
        "invalid_role": frozenset({"role", "roles"}),
        "missing_window_identity": frozenset({"identity", "identities", "windowid", "window"}),
        "binding_mismatch": frozenset({"mismatch", "mismatched", "inconsistent", "inconsistency", "conflict"}),
        "broken_context_ref": frozenset({"context", "contexts"}),
        "invalid_route_receipt": frozenset({"receipt", "receipts", "routing", "route"}),
        "independence_violation": frozenset({"independence", "selfreview", "self_review", "reviewer"}),
        "broken_pointer": frozenset({"pointer", "pointers", "boot", "registry", "contract", "contracts"}),
    },
)

A_REQUIRED_FAILURE_CASES = rule(
    "V4-FAIL-03",
    kind="mapping",
    authority="A12/R12_failure_surfacing",
    interpretation="The seven failure-case roles A R12 states verbatim as a minimum.",
    value=(
        "invalid_role",
        "missing_window_identity",
        "binding_mismatch",
        "broken_context_ref",
        "invalid_route_receipt",
        "independence_violation",
        "broken_pointer",
    ),
)

VISIBLE_FAILURE_TOKENS = rule(
    "V4-FAIL-04",
    kind="vocabulary",
    authority="A12/R12_failure_surfacing",
    interpretation=(
        "A R12 requires broken bindings to FAIL VISIBLY. These tokens name a visible failure "
        "effect. Closed NEGATIVE-style set: an effect that matches none of these is not "
        "accepted as visible failure, so an unrecognised effect fails the predicate rather "
        "than satisfying it."
    ),
    value=frozenset(
        {"fail", "failed", "failure", "nonzero", "non_zero", "reject", "rejected", "block",
         "blocked", "error", "errors", "stop", "halt", "abort", "invalid", "exit_nonzero", "raise"}
    ),
)

SILENT_FALLBACK_TOKENS = rule(
    "V4-FAIL-05",
    kind="vocabulary",
    authority="A12/R12_failure_surfacing",
    interpretation=(
        "A R12 ends with an explicit prohibition: no silent fallback to full history or an "
        "arbitrary model. These tokens locate a fallback position whose enablement is then "
        "judged with the accepted engine's fail-closed enablement rule."
    ),
    value=frozenset({"fallback", "fallbacks", "silent", "silently", "default_to", "defaultto", "degrade"}),
)

# --------------------------------------------------------------------------
# Structural sub-region locators
#
# These name WHERE inside a claimed region a value lives.  They are structural
# positions, not semantic vocabularies: none of them decides whether something
# passes, only which adapter slot a node is offered to.  They are declared here
# rather than inlined so that C-09 covers them too — AB-02's finding was that
# untraced locator constants silently constrain the accepted surface.
# --------------------------------------------------------------------------

DERIVATION_INPUT_REGION_TOKENS = rule(
    "V4-CTX-09",
    kind="mapping",
    authority="A04/R04_minimum_effective_context",
    interpretation="Structural position holding the declared derivation inputs of a context contract.",
    value=frozenset({"input", "inputs", "derivation", "derive", "derived", "basis", "from", "sources", "keys"}),
)

LOAD_SET_REGION_TOKENS = rule(
    "V4-CTX-10",
    kind="mapping",
    authority="A04/R04_minimum_effective_context",
    interpretation="Structural position holding the derived load set of a context contract.",
    value=frozenset({"load", "loadset", "load_set", "set", "entries", "members", "files", "artifacts"}),
)

FRESHNESS_TRIGGER_REGION_TOKENS = rule(
    "V4-FRESH-07",
    kind="mapping",
    authority="A05/R05_context_freshness_and_reentry",
    interpretation="Structural position holding the declared freshness triggers and their effects.",
    value=frozenset({"trigger", "triggers", "on", "when", "conditions", "condition", "invalidation", "rules"}),
)

EFFECT_FIELD_TOKENS = rule(
    "V4-FRESH-08",
    kind="mapping",
    authority="A05/R05_context_freshness_and_reentry; A12/R12_failure_surfacing",
    interpretation=(
        "Structural position holding the effect of a trigger or failure case, when the effect "
        "is written as a record field rather than as the value itself. Both A R05 and A R12 "
        "attach an effect to a named condition, so the locator is shared."
    ),
    value=frozenset({"effect", "effects", "result", "results", "outcome", "outcomes", "action", "actions", "then", "status"}),
)

SELF_REVIEW_POSITION_TOKENS = rule(
    "V4-IND-06",
    kind="mapping",
    authority="A08/R08_independence_constraints",
    interpretation="Structural position declaring what happens when obvious self-review is detected.",
    value=frozenset({"selfreview", "self_review", "self", "sameauthor", "same_author", "sameSession", "same_session"}),
)

SESSION_POSITION_TOKENS = rule(
    "V4-IND-07",
    kind="mapping",
    authority="A08/R08_independence_constraints",
    interpretation="Structural position naming the session/window whose distinctness A R08 requires.",
    value=frozenset({"session", "sessions", "window", "windows", "context", "contexts"}),
)

DEFAULT_EFFECT_POSITION_TOKENS = rule(
    "V4-FRESH-09",
    kind="mapping",
    authority="A05/R05_context_freshness_and_reentry; A12/R12_failure_surfacing",
    interpretation=(
        "Structural position holding an effect that applies to every entry of a sibling "
        "collection. `conditions: [a, b]` with a sibling `stale_effect: fail_closed`, and "
        "`conditions: {a: {effect: fail_closed}, b: {effect: fail_closed}}`, are the same "
        "declaration written two ways. NG-01 requires them to produce the same facts, so a "
        "collection entry with no effect of its own inherits the region's declared effect. "
        "Inheritance never overrides an entry's own effect; it only fills an absence."
    ),
    accepted_alternatives=(
        "per-entry effect",
        "region-level effect inherited by entries that declare none",
    ),
    rejected_alternatives=(
        "treating a region-level effect as absent, which makes a compliant list form fail",
    ),
    value=frozenset(
        # `status` is deliberately absent from the REGION-level set. A document's
        # own top-level `status: active` is not the effect its failure cases
        # take, and matching it handed every case the string "active" as their
        # declared outcome. It remains available at entry level in
        # EFFECT_FIELD_TOKENS, where it is scoped inside the entry's own record.
        {"effect", "effects", "result", "results", "outcome", "outcomes", "action", "actions",
         "then", "disposition", "onfailure", "on_failure", "onstale", "on_stale"}
    ),
)

REQUIRED_FIELDS_POSITION_TOKENS = rule(
    "V4-RCT-06",
    kind="mapping",
    authority="A07/R07_model_route_binding",
    interpretation=(
        "Structural position in which a receipt enumerates its own required field names as "
        "VALUES rather than as keys. `route_receipt: {authority: routing_only}` and "
        "`route_receipt: {required_fields: [authority]}` both declare that the receipt carries "
        "an authority concept. Reading only the key form made a conforming list-form receipt "
        "report one concept out of five, which is the ST04-V3-IR-003 defect in a new place."
    ),
    accepted_alternatives=("map concept roles from key names and from enumerated field names",),
    rejected_alternatives=("map concept roles from key names only",),
    value=frozenset({"required", "fields", "keys", "must", "mandatory", "schema"}),
)

DISTINCTNESS_SUBJECT_TOKENS = rule(
    "V4-IND-08",
    kind="mapping",
    authority="A08/R08_independence_constraints",
    interpretation=(
        "A R08 requires that the implementation window and the final review window are "
        "distinct. Both halves of that sentence must be present for the requirement to be "
        "declared: a distinctness marker, and a session/window subject it applies to. Either "
        "half may sit in the key or in the value — `review_windows: distinct_required` and "
        "`distinct_review_windows: true` are the same declaration."
    ),
    value=frozenset({"implementation", "review", "reviewer", "final"}),
)

SELF_REVIEW_SUBJECT_TOKENS = rule(
    "V4-IND-09",
    kind="mapping",
    authority="A08/R08_independence_constraints",
    interpretation=(
        "A self-review position is one naming a review that is not separated from its author. "
        "Detected as the co-occurrence of a review token with a sameness token, so "
        "`self_review`, `same_window_review` and `same_author_review` are all found without "
        "enumerating every spelling."
    ),
    value={
        "review": frozenset({"review", "reviewer", "reviewed", "acceptance", "audit"}),
        "sameness": frozenset({"self", "same", "own", "identical", "sameauthor", "samesession", "samewindow"}),
    },
)

DEFAULT_EFFECT_QUALIFIER_TOKENS = rule(
    "V4-FRESH-10",
    kind="mapping",
    authority="A05/R05_context_freshness_and_reentry; A12/R12_failure_surfacing",
    interpretation=(
        "Tokens a region-level effect key may carry ALONGSIDE the effect token and still be "
        "that region's default effect. `stale_effect` qualifies; `authority_effect` does not, "
        "because `authority` names a different obligation entirely.\n\n"
        "This exists because a bare token match on `effect` picked up "
        "`authority_effect: none` and handed it to every failure case as their declared "
        "outcome, turning seven compliant cases into seven silent ones. A locator that "
        "matches a neighbouring field is the ST04-V3-IR-005 defect — provenance exclusion "
        "firing on any key containing the letters `source` — in a different key."
    ),
    accepted_alternatives=(
        "exact canonical match on an effect position",
        "effect token plus one of these qualifiers and nothing else",
    ),
    rejected_alternatives=(
        "any key whose tokens merely include an effect token",
    ),
    value=frozenset({"stale", "default", "failure", "invalidation", "trigger", "condition", "conditions", "all"}),
)
