#!/usr/bin/env python3
"""The declared decision vocabularies, each bound to an A requirement.

Every name in this file passes through `provenance.rule`, so a vocabulary that
decides acceptance cannot exist without an authority.  Two properties are what
make this different from the enumerations the reviewer rejected:

  1. these vocabularies identify *positions and polarity* — where a declaration
     sits and which way it points — never *subjects*.  There is no provider,
     model, vendor, product or role-name list anywhere.  An unfamiliar subject is
     read exactly like a familiar one because its name is never consulted;

  2. an unrecognised construct inside a declared position fails closed.  The
     three prior generations failed the other way: unknown fell through to
     "absent", so a novel spelling was silently safe.

`facts.ROLE_CONCEPT_TOKENS` and the old `TRUTH_MARKERS`-driven provider guessing
are deleted rather than extended.  AB-01 is not closed by a longer list.
"""

from __future__ import annotations

from .provenance import rule

# --------------------------------------------------------------------------
# enablement and polarity
# --------------------------------------------------------------------------

ENABLEMENT_NEGATIVE_VALUES = frozenset(
    rule(
        "V-EN-01",
        kind="vocabulary",
        authority="C-03; A13/R13_no_authority_escalation; A14/R14_Human_triggered_progression",
        interpretation=(
            "The closed NEGATIVE set for an enablement position. Values outside "
            "this set remain on the unsafe side; no closed positive vocabulary "
            "can silently treat an unfamiliar grant or trigger as disabled."
        ),
        value={
            "false", "no", "none", "null", "nil", "off", "never", "disabled",
            "disable", "prohibited", "forbidden", "denied", "blocked", "banned",
            "absent", "not_applicable", "not_started", "not_observable",
            "discovery_only", "0",
        },
        rejected_alternatives=(
            "a closed positive set: unfamiliar values such as granted or a named "
            "trigger fell through to safe in the v3 harness",
        ),
    )
)

ENABLEMENT_EMPTY_VALUE_POLICY = rule(
    "V-EN-02",
    kind="default",
    authority="C-03; A13/R13_no_authority_escalation; A14/R14_Human_triggered_progression",
    interpretation=(
        "False, null, zero, an empty scalar and an empty collection are explicit "
        "disabled values. A non-empty value outside V-EN-01 is unsafe."
    ),
    value="false_null_zero_and_empty_are_disabled; every_other_nonempty_value_is_unsafe",
    rejected_alternatives=(
        "absence of a recognized positive word means disabled",
    ),
)

NEGATION_TOKENS = frozenset(
    rule(
        "V-POL-01",
        kind="vocabulary",
        authority="A09/R09_structured_handoff; A14/R14_Human_triggered_progression",
        interpretation=(
            "Tokens by which a key name declares a prohibition. A truthy value on "
            "such a key asserts the prohibition rather than enabling the behaviour."
        ),
        value={
            "prohibited", "prohibit", "prohibits", "prohibition",
            "forbidden", "forbid", "forbids",
            "disallowed", "disallow",
            "disabled", "disable",
            "banned", "ban",
            "denied", "deny",
            "blocked", "block",
            "excluded", "exclude",
            "never", "not", "no", "none", "without", "absent",
        },
        rejected_alternatives=(
            "including the modal 'must' as a negation marker: 'must' alone negates "
            "nothing and, under parity counting (V-POL-02), 'must_not' would have "
            "counted twice and inverted to positive",
        ),
    )
)

NEGATION_PARITY = rule(
    "V-POL-02",
    kind="polarity",
    authority="A13/R13_no_authority_escalation; A14/R14_Human_triggered_progression",
    interpretation=(
        "Polarity is the parity of negation markers in a key name, not their "
        "presence. One marker negates; two markers are a double negative and are "
        "therefore POSITIVE. Closes S25 (master_write_not_forbidden) and S39 "
        "(scheduler_not_prohibited), which the presence rule read as prohibitions."
    ),
    value="parity",
    rejected_alternatives=(
        "presence-of-any-marker => negative: accepted both independent "
        "double-negative counterexamples",
    ),
)

# --------------------------------------------------------------------------
# position kind
# --------------------------------------------------------------------------

DESCRIPTIVE_POSITION_TOKENS = frozenset(
    rule(
        "V-POS-01",
        kind="vocabulary",
        authority="A13/R13_no_authority_escalation; A14/R14_Human_triggered_progression",
        interpretation=(
            "A key naming commentary about a subject rather than a declaration of "
            "it. Such a position yields evidence, never a decision fact. Closes "
            "S18/S20 (authority_note, authority_description read as grants) and "
            "S37 (scheduler_note read as an enabled scheduler)."
        ),
        value={
            "note", "notes", "description", "describes", "rationale", "reason",
            "reasons", "comment", "comments", "narrative", "example", "examples",
            "explanation", "purpose", "summary",
        },
        rejected_alternatives=(
            "word-count prose heuristic alone (is_prose, >=9 words): a one-word "
            "value such as 'unchanged' is still commentary, and length is a "
            "rendering property, not a semantic one",
        ),
    )
)

POINTER_TOKENS = frozenset(
    rule(
        "V-POS-02",
        kind="vocabulary",
        authority="A09/R09_structured_handoff; A01/R01_role_contract",
        interpretation=(
            "A key naming a reference to a subject rather than the subject itself. "
            "Fails closed: a pointer-named key whose value is not a path is treated "
            "as carried state, so a field cannot be laundered by renaming it *_ref."
        ),
        value={
            "ref", "refs", "reference", "references", "pointer", "path", "paths",
            "link", "uri", "url",
        },
    )
)

COLLECTION_ID_FIELD_TOKENS = tuple(
    rule(
        "V-POS-05",
        kind="mapping",
        authority="C-08; A01/R01_role_contract; A02/R02_window_identity",
        interpretation=(
            "Field names by which a list record explicitly declares its keyed "
            "collection identity. They normalize container shape only; the value "
            "is read verbatim and never compared with a subject vocabulary."
        ),
        value=(
            "mode_id", "entry_mode", "role_id", "id", "name", "key", "kind",
            "mode", "role", "label",
        ),
    )
)

DECLARATION_FIELD_NAME_TOKENS = tuple(
    rule(
        "V-POS-06",
        kind="mapping",
        authority="A09/R09_structured_handoff",
        interpretation=(
            "Fields by which a structured prohibition record names the field it "
            "governs. The named value, not the qualifier key, becomes the fact."
        ),
        value=("field", "name", "id", "key", "target", "attribute"),
    )
)

PROVENANCE_TOKENS = frozenset(
    rule(
        "V-POS-03",
        kind="vocabulary",
        authority="A06/R06_role_to_model_requirements",
        interpretation=(
            "A key naming the origin of an observation. A provider named inside "
            "provenance is a record of what happened, not a selection of what must "
            "happen. Whole-token matching only: ST04-V3-IR-005 silenced an entire "
            "subtree because 'source' occurs inside 'resource'."
        ),
        value={
            "evidence", "source", "sources", "citation", "citations", "provenance",
            "basis", "history", "derivation", "observed", "of_record",
        },
        rejected_alternatives=(
            "substring matching on the raw segment",
            "including note/reason/example here: they are descriptive positions "
            "(V-POS-01), a different kind, and conflating them hid S18/S20",
        ),
    )
)

SCHEMA_META_TOKENS = frozenset(
    rule(
        "V-POS-04",
        kind="vocabulary",
        authority="A09/R09_structured_handoff; A07/R07_route_receipt",
        interpretation=(
            "A key declaring the SHAPE of a record. `required_fields: [provider, "
            "model]` names the fields a receipt must carry; it selects nothing."
        ),
        value={
            "fields", "field", "required", "optional", "allowed", "schema", "keys",
            "properties",
        },
    )
)

# --------------------------------------------------------------------------
# A01 / R01 — role semantics
# --------------------------------------------------------------------------

ROLE_SEMANTIC_FIELD_TOKENS = frozenset(
    rule(
        "V-ROLE-01",
        kind="vocabulary",
        authority="A01/R01_role_contract",
        interpretation=(
            "The normative content A01 says a role contract owns: what the role is "
            "responsible for and what independence it must keep. A document binding "
            "either of these to a role entry OWNS role semantics; one binding only "
            "scopes and pointers REFERENCES them. A field that is a pointer takes "
            "precedence: `handoff_ref` names where the rule lives, it is not the rule."
        ),
        value={
            "responsibility", "responsibilities", "duty", "duties",
            "independence", "obligation", "obligations",
        },
        rejected_alternatives=(
            "including 'context': a context scope is applicability metadata, not "
            "normative role content. Including it made S16 (role_applicability with "
            "context_scope) a false second role source",
            "including 'authority', 'handoff', 'produces', 'constraint', 'effects': "
            "each occurs outside any role table — `route_receipt.authority_constant` "
            "in the baseline window contract is the clearest case — so including "
            "them made a routing block look like a role definition",
            "including 'requirement': too generic; it appears in pointer records",
        ),
    )
)

ROLE_LABEL_FIELD_TOKENS = frozenset(
    rule(
        "V-ROLE-02",
        kind="vocabulary",
        authority="A01/R01_role_contract",
        interpretation=(
            "Where an entry may carry its own role identity when the collection key "
            "is a generic identifier. Identity is read verbatim: the label's WORDS "
            "are never checked against a concept list."
        ),
        value={"label", "role", "name", "role_id", "title", "id"},
        rejected_alternatives=(
            "ROLE_CONCEPT_TOKENS: requiring a role's NAME to appear in a closed "
            "concept vocabulary. It produced both directions of error at once — "
            "S14 (real second role source named assembler/examiner) passed because "
            "the names were unlisted, and S17 (quality metrics named review_latency "
            "/research_depth) failed because unrelated names were listed. This is "
            "the vendor-completeness antipattern applied to roles and it is deleted, "
            "not extended.",
        ),
    )
)

ROLE_COLLECTION_MIN_ENTRIES = rule(
    "V-ROLE-03",
    kind="threshold",
    authority="A01/R01_role_contract",
    interpretation=(
        "One role entry carrying normative role content is already a second source "
        "of role semantics under A01's 'exactly one document owns'. The constant is "
        "1 because A01 states no size exception."
    ),
    value=1,
    rejected_alternatives=(
        "2 or 3, on the intuition that a 'table' needs several rows: A01 grants no "
        "size exception, and this is the same defect class as "
        "CATALOG_RESTATEMENT_THRESHOLD=3",
    ),
)

# --------------------------------------------------------------------------
# A06 / R06 / R08 — provider independence
# --------------------------------------------------------------------------

SELECTOR_REGION_TOKENS = frozenset(
    rule(
        "V-PROV-01",
        kind="vocabulary",
        authority="A06/R06_role_to_model_requirements; R08_independence_constraints",
        interpretation=(
            "Keys that open a provider/model SELECTION region. The region is the "
            "decision position; whatever occupies its value slot is the subject, "
            "read verbatim. No vendor name is ever consulted, so an unlisted "
            "provider is detected exactly like a listed one."
        ),
        value={
            "provider", "providers", "model", "models", "vendor", "vendors",
            "family", "families", "surface", "surfaces", "engine", "engines",
            "executor", "executors",
        },
    )
)

SELECTION_CONTAINER_TOKENS = frozenset(
    rule(
        "V-PROV-04",
        kind="vocabulary",
        authority="A06/R06_role_to_model_requirements",
        interpretation=(
            "Qualifiers that make a provider/model region an explicit selection "
            "container. Once claimed, an unrecognized value slot is unsupported "
            "rather than silently ignored."
        ),
        value={"selection", "selector", "choice", "pin", "preference", "policy"},
    )
)

INDEPENDENCE_POSITION_TOKENS = frozenset(
    rule(
        "V-PROV-05",
        kind="vocabulary",
        authority="A08/R08_independence_constraints",
        interpretation=(
            "Qualifiers that turn a model-family mention into an independence "
            "constraint rather than a provider selection."
        ),
        value={"different", "distinct", "independent", "independence", "separate"},
    )
)

ROLE_SCOPE_TOKENS = frozenset(
    rule(
        "V-PROV-06",
        kind="vocabulary",
        authority="A06/R06_role_to_model_requirements",
        interpretation="Path positions that bind a provider selector to an opaque role identity.",
        value={"role", "roles"},
    )
)

SELECTION_SLOT_TOKENS = frozenset(
    rule(
        "V-PROV-02",
        kind="vocabulary",
        authority="A06/R06_role_to_model_requirements",
        interpretation=(
            "Sub-keys inside a selection region that hold the selected subject. "
            "Closes S09 (provider_selection.chosen) and S13 "
            "(provider_policy.allow.chosen), which the previous extractor could not "
            "see because it only looked at the innermost key and at truth markers."
        ),
        value={
            "chosen", "choice", "selected", "selection", "preferred", "pinned",
            "default", "primary", "value", "use", "uses", "assigned", "bound",
        },
        rejected_alternatives=(
            "expanding every leaf under a selection region: baseline "
            "`different_model_family: {expressed_as: ..., delivered_to: ...}` would "
            "become two normative selectors. Selection must sit in a selection slot",
        ),
    )
)

ALLOW_POLARITY_TOKENS = frozenset(
    rule(
        "V-PROV-03",
        kind="polarity",
        authority="A06/R06_role_to_model_requirements; R08_independence_constraints",
        interpretation=(
            "A sub-region that grants rather than forbids. A mixed allow/deny policy "
            "is decided by its POSITIVE branch: forbidding one provider does not "
            "neutralise pinning another (S13)."
        ),
        value={"allow", "allowed", "permit", "permitted", "include", "included"},
    )
)

# --------------------------------------------------------------------------
# A13 / R13 — authority
# --------------------------------------------------------------------------

GRANT_HEAD_TOKENS = frozenset(
    rule(
        "V-AUTH-01",
        kind="vocabulary",
        authority="A13/R13_no_authority_escalation",
        interpretation=(
            "Keys that CONFER authority: a permission set, a capability set, or an "
            "act declared authorised. Distinguished from keys that merely speak "
            "ABOUT authority (authority_effect, authority_boundary, authority_limit), "
            "which are descriptive scope statements and grant nothing. Closes S23 "
            "(permissions.master_write_authorized.state=granted) and S24 "
            "(capabilities.publish_master=true); removes the S14/i08 false positive "
            "where `authority_limit` was read as a grant."
        ),
        value={
            "grant", "grants", "granted", "granting",
            "permission", "permissions", "permit", "permits", "permitted",
            "privilege", "privileges",
            "capability", "capabilities",
            "authorized", "authorised", "authorization", "authorisation",
        },
        rejected_alternatives=(
            "treating every key containing 'authority' as a grant position: it made "
            "`authority_effect: none` and `authority_boundary` grant candidates and "
            "produced the S14/S18/S20 false positives",
        ),
    )
)

AUTHORITY_NON_GRANT_VALUES = frozenset(
    rule(
        "V-AUTH-02",
        kind="vocabulary",
        authority="A07/R07_route_receipt (authority: routing_only, stated verbatim)",
        interpretation=(
            "Values at a grant position that do NOT confer authority. A07 states the "
            "routing receipt's authority constant verbatim as `routing_only`, so it "
            "is an A-declared non-grant value rather than one this prototype "
            "invented. Everything outside this closed set is a grant: "
            "ST04-V3-IR-010 was caused by a closed POSITIVE set, under which "
            "'granted' fell through to safe."
        ),
        value={"routing_only", "none", "informational", "unchanged"},
    )
)

# --------------------------------------------------------------------------
# A14 / R14 — autonomy
# --------------------------------------------------------------------------

AUTONOMY_STANDALONE_TOKENS = frozenset(
    rule(
        "V-AUTO-01",
        kind="vocabulary",
        authority="A14/R14_Human_triggered_progression",
        interpretation=(
            "Machinery whose mere configuration is autonomous progression. R14 names "
            "scheduler, watcher, daemon and polling directly. 'automation' is "
            "included because a key opening an automation-control region is naming "
            "the same machinery (S41: automation_controls.cadence.trigger)."
        ),
        value={
            "scheduler", "schedulers", "watcher", "watchers", "daemon", "daemons",
            "polling", "poller", "cron", "automation",
        },
    )
)

AUTOMATION_QUALIFIER_TOKENS = frozenset(
    rule(
        "V-AUTO-02",
        kind="vocabulary",
        authority="A14/R14_Human_triggered_progression",
        interpretation="Qualifiers that make a named behaviour autonomous.",
        value={"automatic", "automated", "auto", "autonomous", "background"},
    )
)

AUTOMATION_BEHAVIOUR_TOKENS = frozenset(
    rule(
        "V-AUTO-03",
        kind="vocabulary",
        authority="A14/R14_Human_triggered_progression",
        interpretation=(
            "The behaviours R14 requires to stay Human-triggered. Only meaningful "
            "beside a qualifier (V-AUTO-02); `progression` alone names a policy "
            "block, not an enabled behaviour."
        ),
        value={
            "delivery", "deliver", "progression", "progress", "spawn", "dispatch",
            "advance", "processes", "process", "acknowledgment", "acknowledgement",
            "retry", "escalation",
        },
    )
)

# --------------------------------------------------------------------------
# A09 / R09 — handoff payload
# --------------------------------------------------------------------------

DELIVERY_STATE_TOKENS = frozenset(
    rule(
        "V-HAND-01",
        kind="vocabulary",
        authority="A09/R09_structured_handoff",
        interpretation=(
            "Mutable runtime state R09 forbids a handoff payload from carrying. A "
            "REFERENCE to such state is permitted; a VALUE of it is not."
        ),
        value={
            "delivery", "delivered", "read", "opened", "accepted", "acceptance",
            "understood", "receipt",
        },
    )
)

PRIVATE_REASONING_TOKENS = frozenset(
    rule(
        "V-HAND-02",
        kind="vocabulary",
        authority="A09/R09_structured_handoff",
        interpretation="Private reasoning R09 forbids a handoff payload from carrying.",
        value={"reasoning", "thought", "thoughts", "cot", "deliberation"},
    )
)

PAYLOAD_SCOPE_TOKENS = frozenset(
    rule(
        "V-HAND-03",
        kind="vocabulary",
        authority="A09/R09_structured_handoff",
        interpretation=(
            "The scope a handoff actually CARRIES, as opposed to a sibling block "
            "that declares policy about it."
        ),
        value={"record", "payload", "envelope", "body", "content"},
    )
)

HANDOFF_RECORD_TOKENS = frozenset(
    rule(
        "V-HAND-04",
        kind="mapping",
        authority="A09/R09_structured_handoff",
        interpretation=(
            "The declared handoff-record position. It gates prohibition and "
            "payload extraction so one document cannot satisfy another's handoff."
        ),
        value={"handoff", "record"},
    )
)

# --------------------------------------------------------------------------
# A02 / R02 — window identity
# --------------------------------------------------------------------------

A_REQUIRED_IDENTITY_FACTS = tuple(
    rule(
        "V-WIN-01",
        kind="mapping",
        authority="A02/R02_window_identity",
        interpretation=(
            "The identity facts A R02 requires a window to bind. `run` is absent on "
            "purpose: R02 does not require it. ST04-V3-IR-004 was caused by "
            "promoting run_id from a B choice into an A requirement."
        ),
        value=("task", "role", "stage", "step", "branch", "head"),
    )
)

B_ONLY_IDENTITY_FACTS = tuple(
    rule(
        "V-WIN-02",
        kind="mapping",
        authority="B_ONLY (recorded as evidence; mechanically excluded from decisions)",
        interpretation=(
            "Facts a B design may choose to bind and which acceptance must ignore. "
            "`decision_facts.WindowIdentityFact` carries these in a separate field "
            "that no predicate reads, so the promotion cannot recur by editing."
        ),
        value=("run",),
    )
)

IDENTITY_FACT_SYNONYMS: dict[str, frozenset[str]] = rule(
    "V-WIN-03",
    kind="mapping",
    authority="A02/R02_window_identity",
    interpretation=(
        "Spellings of the same identity fact. A synonym map is a normalisation of "
        "the SUBJECT NAME A02 itself uses, not an inference about meaning."
    ),
    value={
        "task": frozenset({"task", "task_id"}),
        "role": frozenset({"role", "role_id"}),
        "stage": frozenset({"stage", "stage_id", "workflow_stage", "workflow_stage_id"}),
        "step": frozenset({"step", "step_id", "workflow_step", "workflow_step_id"}),
        "branch": frozenset({"branch", "task_branch", "work_branch"}),
        "head": frozenset(
            {"head", "entry_repository_head", "repository_head", "entry_head", "commit"}
        ),
        "run": frozenset({"run", "run_id"}),
        "window": frozenset({"window", "window_id"}),
        "lifecycle": frozenset({"lifecycle", "lifecycle_state", "state"}),
    },
)

WINDOW_REGION_TOKENS = frozenset(
    rule(
        "V-WIN-06",
        kind="mapping",
        authority="A02/R02_window_identity",
        interpretation="The required window head of a window-identity region.",
        value={"window"},
    )
)

IDENTITY_REGION_TOKENS = frozenset(
    rule(
        "V-WIN-07",
        kind="mapping",
        authority="A02/R02_window_identity",
        interpretation="The alternative identity heads of a window-identity region.",
        value={"identity", "id"},
    )
)

ENTRY_REGION_TOKENS = frozenset(
    rule(
        "V-WIN-13",
        kind="mapping",
        authority="A02/R02_window_identity",
        interpretation="The required entry head of an entry-mode collection.",
        value={"entry"},
    )
)

MODE_REGION_TOKENS = frozenset(
    rule(
        "V-WIN-14",
        kind="mapping",
        authority="A02/R02_window_identity",
        interpretation="The alternative mode heads of an entry-mode collection.",
        value={"mode", "modes"},
    )
)

BOUND_FACT_FIELD_TOKENS = frozenset(
    rule(
        "V-WIN-08",
        kind="mapping",
        authority="A02/R02_window_identity",
        interpretation="Fields that explicitly enumerate facts bound into a window identity.",
        value={"bound", "required", "facts", "fields"},
    )
)

LATEST_SESSION_POSITION_TOKENS = frozenset(
    rule(
        "V-WIN-09",
        kind="mapping",
        authority="A02/R02_window_identity",
        interpretation="The latest-session pointer position that A02 forbids as formal identity.",
        value={"latest"},
    )
)

LATEST_SESSION_SAFE_STATUS = rule(
    "V-WIN-10",
    kind="mapping",
    authority="A02/R02_window_identity",
    interpretation=(
        "The only positive textual status that establishes a latest-session "
        "pointer is prohibited as formal identity. Every other enabled status at "
        "that position fails closed as allowed_or_ambiguous."
    ),
    value="prohibited_as_formal_identity",
    rejected_alternatives=(
        "substring searches for prohibit/allow inside arbitrary prose",
    ),
)

PREDECESSOR_POSITION_TOKENS = frozenset(
    rule(
        "V-WIN-11",
        kind="mapping",
        authority="A02/R02_window_identity",
        interpretation="Fields that bind a re-entry mode to its exact predecessor.",
        value={"predecessor"},
    )
)

REQUIRED_QUALIFIER_TOKENS = frozenset(
    rule(
        "V-WIN-15",
        kind="mapping",
        authority="A02/R02_window_identity",
        interpretation="Qualifier asserting that an identity or predecessor fact is mandatory.",
        value={"required"},
    )
)

MATCH_QUALIFIER_TOKENS = frozenset(
    rule(
        "V-WIN-16",
        kind="mapping",
        authority="A02/R02_window_identity",
        interpretation="Qualifier declaring the predecessor matching relation.",
        value={"match"},
    )
)

EXACT_PREDECESSOR_MATCH = rule(
    "V-WIN-12",
    kind="mapping",
    authority="A02/R02_window_identity",
    interpretation="R02 requires an explicitly identified predecessor; exact is the declared match relation.",
    value="exact",
)

FRESH_TOKENS = frozenset(
    rule(
        "V-WIN-04",
        kind="vocabulary",
        authority="A02/R02_window_identity",
        interpretation="Entry-mode identities R02 requires to be distinguishable (fresh side).",
        value={"fresh", "new", "initial", "create", "first"},
    )
)

REENTRY_TOKENS = frozenset(
    rule(
        "V-WIN-05",
        kind="vocabulary",
        authority="A02/R02_window_identity",
        interpretation="Entry-mode identities R02 requires to be distinguishable (reentry side).",
        value={"reentry", "reenter", "resume", "continuation", "resumed", "rejoin"},
    )
)

# --------------------------------------------------------------------------
# A11 — no second mutable catalog
# --------------------------------------------------------------------------

CATALOG_MIN_ENTRIES = rule(
    "V-CAT-01",
    kind="threshold",
    authority="A11/R11_workflow_and_entry_thinness",
    interpretation=(
        "A catalog is a COLLECTION of entries; two is the smallest collection. This "
        "is definitional, not a tolerance: it does not say 'a small duplicate is "
        "allowed', it says a single scalar mention is not a collection. A11 grants "
        "no size exception, which is why the previous value of 3 was an A11 "
        "weakening (S43)."
    ),
    value=2,
    rejected_alternatives=(
        "CATALOG_RESTATEMENT_THRESHOLD=3, the untraced constant named in the "
        "independent review as the proof of AB-02: it let a two-entry authoritative "
        "mutable catalog pass",
        "1: a single identifier appearing as a scalar value is a mention, and the "
        "baseline's `example_identifier_mentioned_singly` is exactly that",
    ),
)

CATALOG_IDENTIFIER_FIELD_TOKENS = frozenset(
    rule(
        "V-CAT-02",
        kind="vocabulary",
        authority="A11/R11_workflow_and_entry_thinness; R10_existing_mechanism_separation",
        interpretation=(
            "Fields by which an entry binds a routing identifier. Read from the live "
            "catalog's own declared field names plus the generic `model`, so a "
            "second catalog is detected by SHAPE even when every identifier in it is "
            "unseen (S42). No identifier VALUE is enumerated anywhere."
        ),
        value={"model", "model_label", "model_id", "product_surface", "parameter_profile"},
    )
)

# --------------------------------------------------------------------------
# discovery
# --------------------------------------------------------------------------

DECLARING_SURFACES = tuple(
    rule(
        "V-DISC-02",
        kind="mapping",
        authority="A11/R11_workflow_and_entry_thinness; the tree's own surface declaration",
        interpretation=(
            "Surfaces on which a positive declaration is normative. Surface "
            "MEMBERSHIP is a declared discovery input, not an inference: A11 is "
            "itself stated in terms of a surface ('workflow stages and the stable "
            "development entry'), and the tree declares its own prefixes. What a "
            "document MEANS is still decided only by an adapter."
        ),
        value=("mechanism", "boot", "registry", "workflow_or_entry"),
        rejected_alternatives=(
            "deriving the surface from the file name or directory: ST04-IR-003",
            "scanning every discovered document regardless of surface: it would let "
            "one artifact's prohibitions satisfy A09 on another's behalf",
        ),
    )
)

TRANSPARENT_CONTAINER_POLICY = rule(
    "V-DISC-01",
    kind="ambiguity",
    authority="C-08; A01/R01; A02/R02; A09/R09",
    interpretation=(
        "Transparent container depth is not semantic, so discovery has no depth "
        "cutoff. Traversal stops only on an actual object-cycle; a finite deeper "
        "wrapper can never hide a declaration."
    ),
    value="unbounded_finite_tree_with_ancestor_cycle_guard",
    rejected_alternatives=(
        "top-level-only lookup",
        "a fixed maximum depth, which merely moves the representation escape to depth+1",
    ),
)

ROLE_OWNER_REQUIRED_SURFACE = rule(
    "V-DISC-04",
    kind="mapping",
    authority="A01/R01_role_contract; R10_existing_mechanism_separation",
    interpretation=(
        "The sole role-semantics owner belongs to the existing mechanism surface. "
        "Other declared surfaces may carry pointer-only references."
    ),
    value="mechanism",
)
