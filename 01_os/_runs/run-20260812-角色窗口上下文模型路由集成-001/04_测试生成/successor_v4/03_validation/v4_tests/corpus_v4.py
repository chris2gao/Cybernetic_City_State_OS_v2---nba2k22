"""Adversarial corpus for the seven v4 predicates.

Same two questions the accepted corpus asks, asked of the extension:

    equivalent meaning  -> equivalent acceptance result
    different meaning   -> different acceptance result

and the three attack shapes that ended v3, applied to v4's own vocabulary:

  * poisoned vocabulary — an unfamiliar token in a normative position must not
    pass merely because no closed positive list recognised it (ST04-V3-IR-008,
    ST04-V3-IR-010: a closed POSITIVE vocabulary treating the unknown as safe);
  * polarity inversion — a prohibition and a permission are not the same
    declaration, and a deny beside an allow does not neutralise the allow;
  * double negation — "not prohibited" is a permission, and must be read as one.

Nothing here is imported from the accepted corpus.  These transformations target
regions the accepted seven predicates never look at: lifecycle, minimum
effective context, freshness/re-entry, route receipts, review independence,
mechanism separation and failure surfacing.

Base tree for every case is `fixtures/baseline_v4`, the tree that satisfies all
fourteen criteria.  An invariance case must leave the whole fourteen-entry
result vector unchanged; a difference case must fail, and fail on the predicate
it was built to probe.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

CONTEXT = "mechanism/context_contract_v1.yml"
WINDOWS = "mechanism/windows_v1.yml"
BOOT = "boot/boot_v1.yml"
ROLES = "mechanism/roles_v1.yml"


def load(tree: Path, rel: str) -> Any:
    return yaml.safe_load((tree / rel).read_text(encoding="utf-8"))


def save(tree: Path, rel: str, data: Any) -> None:
    (tree / rel).write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=4096),
        encoding="utf-8",
        newline="\n",
    )


def copy_tree(src: Path, dest: Path) -> Path:
    shutil.copytree(src, dest)
    return dest


# ---------------------------------------------------------------------------
# Invariance: representation changes that must not move any predicate
# ---------------------------------------------------------------------------


def v4_context_wrapped_in_transparent_container(tree: Path) -> None:
    doc = load(tree, CONTEXT)
    doc["contract"] = {"minimum_effective_context": doc.pop("minimum_effective_context")}
    save(tree, CONTEXT, doc)


def v4_lifecycle_wrapped_in_transparent_container(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["window_contract"] = {"lifecycle": doc.pop("lifecycle")}
    save(tree, WINDOWS, doc)


def v4_lifecycle_states_as_list_of_records(tree: Path) -> None:
    """In-contract list-of-records: the record declares its identity with `id`.

    Filed as V4-FND-04-a with `[{state: X}]`. `state` is not in
    `COLLECTION_ID_FIELD_TOKENS`, so that form is a single-entry mapping keyed
    literally "state" and the collection collapses to one entry - which is what
    the accepted engine does with it too, and therefore outside the accepted
    equivalence contract rather than a v4 defect.
    """
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["states"] = [{"id": s} for s in doc["lifecycle"]["states"]]
    save(tree, WINDOWS, doc)


def v4_lifecycle_states_reversed(tree: Path) -> None:
    """Declaration ORDER carries no meaning, for states or for conditions.

    Since ruling F03-D the conditions are a keyed collection of structured
    records rather than a list of bare strings, so reversing them means
    reversing the mapping's key order. Reversing the mapping OBJECT would yield
    a list of keys and destroy the records - which is a different transformation
    entirely, and would have tested the fixture's shape rather than the
    adapter's order-independence.
    """
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["states"] = list(reversed(doc["lifecycle"]["states"]))
    conditions = doc["lifecycle"]["invalidation_conditions"]
    doc["lifecycle"]["invalidation_conditions"] = {
        k: conditions[k] for k in reversed(list(conditions))
    }
    save(tree, WINDOWS, doc)


# ---------------------------------------------------------------------------
# F03-D: the admitted representations of a typed determinism fact
# ---------------------------------------------------------------------------
#
# Ruling F03-D leaves representation free and fixes the SLOTS. These four
# transformations write the same three slots four different ways; every one of
# them must produce the identical fact and move no predicate. They are the
# `multiple_admitted_forms_must_normalize_to_same_fact` half of the ruling, and
# without them the implementation could satisfy the negative cases by admitting
# exactly one shape - which is rejected option F03-B wearing F03-D's name.


def v4_conditions_as_list_of_records(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    conditions = doc["lifecycle"]["invalidation_conditions"]
    doc["lifecycle"]["invalidation_conditions"] = [
        dict({"id": name}, **record) for name, record in conditions.items()
    ]
    save(tree, WINDOWS, doc)


def v4_conditions_as_list_of_single_entry_mappings(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    conditions = doc["lifecycle"]["invalidation_conditions"]
    doc["lifecycle"]["invalidation_conditions"] = [
        {name: record} for name, record in conditions.items()
    ]
    save(tree, WINDOWS, doc)


def v4_conditions_as_bare_names_with_definitions(tree: Path) -> None:
    """The one form in which a bare string is admitted: an explicit definition.

    A R03's obligation is discharged by the definitions block, not by the
    string's spelling. This is the case that separates F03-D from a blanket ban
    on bare strings.
    """
    doc = load(tree, WINDOWS)
    conditions = doc["lifecycle"]["invalidation_conditions"]
    doc["lifecycle"]["condition_definitions"] = dict(conditions)
    doc["lifecycle"]["invalidation_conditions"] = list(conditions)
    save(tree, WINDOWS, doc)


def v4_condition_slots_spelled_differently(tree: Path) -> None:
    """Slot positions and observation roles are synonym maps, not fixed spellings."""
    doc = load(tree, WINDOWS)
    conditions = doc["lifecycle"]["invalidation_conditions"]
    for record in conditions.values():
        record["observable"] = record.pop("subject")
        observation = record.pop("observation")
        record["comparison"] = "mismatch" if observation == "changed" else observation
    save(tree, WINDOWS, doc)


def v4_derivation_inputs_as_list_of_pairs(tree: Path) -> None:
    doc = load(tree, CONTEXT)
    mec = doc["minimum_effective_context"]
    mec["derivation_inputs"] = [{k: v} for k, v in mec["derivation_inputs"].items()]
    save(tree, CONTEXT, doc)


def v4_load_set_entries_as_records(tree: Path) -> None:
    doc = load(tree, CONTEXT)
    mec = doc["minimum_effective_context"]
    mec["load_set"]["entries"] = [{"path": e} for e in mec["load_set"]["entries"]]
    save(tree, CONTEXT, doc)


def v4_route_receipt_fields_as_mapping(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    rr = doc["model_route_binding"]["route_receipt"]
    rr["required_fields"] = {name: "required" for name in rr["required_fields"]}
    save(tree, WINDOWS, doc)


def v4_failure_states_as_records(tree: Path) -> None:
    """In-contract list-of-records. Filed as V4-FND-04-c with `[{case: X}]`.

    `case` is not in `COLLECTION_ID_FIELD_TOKENS`, so the filed form was a
    single-entry mapping keyed literally "case" - outside the accepted
    equivalence contract, and a test error rather than a package defect.

    The `[{X: {}}]` form is IN contract and is deliberately not used here: it
    moves accepted P02 and v4 P24, and the accepted engine alone moves P02 on it
    in an isolated interpreter. That is recorded as V4-OBS-03 and reported to
    the foreground rather than fixed, because it is in the vendored accepted
    engine and outside this task's write boundary.
    """
    doc = load(tree, WINDOWS)
    doc["failure_states"] = [{"id": c} for c in doc["failure_states"]]
    save(tree, WINDOWS, doc)


def v4_descriptive_metadata_added(tree: Path) -> None:
    """Inert prose beside every v4 region. Description is not declaration."""
    doc = load(tree, CONTEXT)
    doc["notes"] = {
        "authored_by": "a person who likes writing notes",
        "commentary": "this document declares a derivation contract",
        "unrelated_status": "active",
    }
    save(tree, CONTEXT, doc)
    w = load(tree, WINDOWS)
    w["lifecycle"]["commentary"] = "states are listed above; this line explains that"
    save(tree, WINDOWS, w)


def v4_prohibitions_spelled_as_equivalent_negatives(tree: Path) -> None:
    """`prohibited` / `false` / `not_permitted` are the same closed negative."""
    doc = load(tree, CONTEXT)
    mec = doc["minimum_effective_context"]
    mec["default_preload_of_all_runs"] = False
    mec["historical_run_preload"] = "not_permitted"
    save(tree, CONTEXT, doc)


# ---------------------------------------------------------------------------
# Poisoned vocabulary: an unfamiliar token in a normative position
# ---------------------------------------------------------------------------


def v4_unknown_stale_effect_token(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["stale_effect"] = "graceful_degradation_with_partial_context"
    save(tree, WINDOWS, doc)


def v4_unknown_route_receipt_authority_constant(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["model_route_binding"]["route_receipt"]["authority_constant"] = "advisory_plus"
    save(tree, WINDOWS, doc)


def v4_unknown_exactness_entry_form(tree: Path) -> None:
    doc = load(tree, CONTEXT)
    doc["minimum_effective_context"]["exactness"]["entry_form"] = "whatever_the_loader_finds"
    save(tree, CONTEXT, doc)


def v4_unknown_missing_receipt_behaviour(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["model_route_binding"]["route_receipt"]["missing_or_stale_or_inconsistent"] = "best_effort"
    save(tree, WINDOWS, doc)


def v4_unknown_on_failure_behaviour(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["on_failure"] = "log_and_proceed"
    save(tree, WINDOWS, doc)


# ---------------------------------------------------------------------------
# Polarity inversion
# ---------------------------------------------------------------------------


def v4_preload_permitted_instead_of_prohibited(tree: Path) -> None:
    doc = load(tree, CONTEXT)
    doc["minimum_effective_context"]["default_preload_of_all_runs"] = "permitted"
    save(tree, CONTEXT, doc)


def v4_historical_preload_allowed(tree: Path) -> None:
    doc = load(tree, CONTEXT)
    doc["minimum_effective_context"]["historical_run_preload"] = "allowed"
    save(tree, CONTEXT, doc)


def v4_same_window_review_permitted(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["independence"]["same_window_review"] = "permitted"
    save(tree, WINDOWS, doc)


def v4_mixed_polarity_preload_policy(tree: Path) -> None:
    """A deny beside an allow does not neutralise the allow.

    The mirror of the accepted corpus's mixed allow/deny provider policy, on a
    v4 region: the document forbids preloading in one branch and permits it in
    another that is just as normative.
    """
    doc = load(tree, CONTEXT)
    mec = doc["minimum_effective_context"]
    mec["default_preload_of_all_runs"] = "prohibited"
    mec["preload_policy"] = {
        "denied": ["unrelated_role_history"],
        "permitted": ["all_runs_under_the_current_task"],
    }
    save(tree, CONTEXT, doc)


def v4_background_progression_enabled(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["background_progression"] = True
    save(tree, WINDOWS, doc)


# ---------------------------------------------------------------------------
# Double negation
# ---------------------------------------------------------------------------


def v4_double_negated_preload(tree: Path) -> None:
    """`not prohibited` is a permission."""
    doc = load(tree, CONTEXT)
    doc["minimum_effective_context"]["default_preload_of_all_runs"] = "not_prohibited"
    save(tree, CONTEXT, doc)


def v4_double_negated_same_window_review(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["independence"]["same_window_review"] = "not_prohibited"
    save(tree, WINDOWS, doc)


def v4_double_negated_background_progression(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["background_progression"] = "not_disabled"
    save(tree, WINDOWS, doc)


# ---------------------------------------------------------------------------
# Absence and weakening
# ---------------------------------------------------------------------------


def v4_lifecycle_state_removed(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["states"] = [s for s in doc["lifecycle"]["states"] if s != "stale"]
    save(tree, WINDOWS, doc)


def v4_invalidation_conditions_emptied(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["invalidation_conditions"] = []
    save(tree, WINDOWS, doc)


def v4_nondeterministic_invalidation_condition(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["invalidation_conditions"] = [
        "when the window feels stale",
        "approximately every few hours",
    ]
    save(tree, WINDOWS, doc)


def v4_A_named_triggers_kept_conditions_are_prose(tree: Path) -> None:
    """The variant V4-FND-03 said was owed to whoever closed it.

    The finding's own measurement failed on P23 rather than P21, because
    replacing the conditions also removed the A-named change triggers. It said
    so, and recorded that a candidate keeping the A-named triggers while writing
    only their CONDITIONS as prose was not built and was owed. This is it: the
    four A-named triggers survive verbatim as keys, P23 has no complaint, and
    P21 alone must catch it.
    """
    doc = load(tree, WINDOWS)
    conditions = doc["lifecycle"]["invalidation_conditions"]
    doc["lifecycle"]["invalidation_conditions"] = {
        name: "when it feels like it has drifted far enough" for name in conditions
    }
    save(tree, WINDOWS, doc)


def v4_condition_subject_slot_missing(tree: Path) -> None:
    """Slot 1 absent. A comparison with no named subject compares nothing."""
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["invalidation_conditions"]["authorization_ref_changed"] = {
        "observation": "changed"
    }
    save(tree, WINDOWS, doc)


def v4_condition_observation_unrecognised(tree: Path) -> None:
    """Slot 2 present but unrecognised.

    This is the case that proves the F03-D inversion actually landed. Under the
    old closed NEGATIVE vocabulary an unfamiliar word was deterministic by
    default; here it must be UNSUPPORTED. If this case ever passes, the
    implementation has drifted back to presuming the unknown case safe -
    ST04-V3-IR-008, which is what V4-FND-03 was.
    """
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["invalidation_conditions"]["authorization_ref_changed"] = {
        "subject": "authorization_ref",
        "observation": "wobbles_a_bit",
    }
    save(tree, WINDOWS, doc)


def v4_condition_cadence_instead_of_comparison(tree: Path) -> None:
    """A cadence is not an observation of a subject changing."""
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["invalidation_conditions"]["approximately_every_few_hours"] = {
        "subject": "wall_clock",
        "observation": "approximately_every_few_hours",
    }
    save(tree, WINDOWS, doc)


def v4_condition_consequence_is_continue_cached(tree: Path) -> None:
    """Slot 3 recognised and non-compliant, which is not the same as unknown.

    A R03 requires the stale consequence. Declaring that the window carries on
    from cache is fully understood and still fails: `continue_cached` is a named
    role in V4-FRESH-05 and is deliberately absent from V4-FRESH-06.
    """
    doc = load(tree, WINDOWS)
    doc["lifecycle"]["stale_effect"] = "continue_from_cache"
    save(tree, WINDOWS, doc)


def v4_derivation_input_requirement_leaf_as_load_entry(tree: Path) -> None:
    """V4-FND-04-b, second root cause: over-broad load-entry region scoping.

    `approved_reference_set` carries the token `set`, which is a
    LOAD_SET_REGION token. Declaring that A-required input as a structured
    record rather than the bare scalar `required` - more detail, same meaning -
    made the load-set locator claim it and emit a REQUIREMENT leaf as a load
    ENTRY with exact=false. A conforming candidate then failed A04.

    Measured before the fix: P22 pass -> fail, with
    `minimum_effective_context.derivation_inputs.approved_reference_set.source`
    reported as a non-exact load entry.
    """
    doc = load(tree, CONTEXT)
    doc["minimum_effective_context"]["derivation_inputs"]["approved_reference_set"] = {
        "required": True,
        "source": "task_packet",
    }
    save(tree, CONTEXT, doc)


def v4_derivation_inputs_as_pairs(tree: Path) -> None:
    doc = load(tree, CONTEXT)
    mec = doc["minimum_effective_context"]
    mec["derivation_inputs"] = [[k, v] for k, v in mec["derivation_inputs"].items()]
    save(tree, CONTEXT, doc)


def v4_derivation_inputs_as_bare_field_names(tree: Path) -> None:
    doc = load(tree, CONTEXT)
    mec = doc["minimum_effective_context"]
    mec["derivation_inputs"] = list(mec["derivation_inputs"].keys())
    save(tree, CONTEXT, doc)


def v4_unbounded_load_set_entry(tree: Path) -> None:
    doc = load(tree, CONTEXT)
    doc["minimum_effective_context"]["load_set"]["entries"].append("01_os/_runs/**")
    save(tree, CONTEXT, doc)


def v4_derivation_input_removed(tree: Path) -> None:
    doc = load(tree, CONTEXT)
    doc["minimum_effective_context"]["derivation_inputs"].pop("role_id", None)
    save(tree, CONTEXT, doc)


def v4_context_contract_deleted(tree: Path) -> None:
    (tree / CONTEXT).unlink()


def v4_route_receipt_concept_removed(tree: Path) -> None:
    """Remove a whole A07 CONCEPT, not one field name.

    An earlier draft of this case removed `validator_exit_code` and expected a
    failure. That was the test being wrong, not the package: A07 requires the
    receipt to carry surface/model/profile/evidence/limitations/availability as
    *concepts*, and `A_REQUIRED_RECEIPT_CONCEPTS` is five concept roles rather
    than thirteen field names. Requiring an exact field-name list is precisely
    the vendor/spelling coupling the methodology exists to avoid, so removing
    one field of several that carry the same concept must NOT fail. Removing
    every field carrying a concept must.
    """
    doc = load(tree, WINDOWS)
    rr = doc["model_route_binding"]["route_receipt"]
    rr["required_fields"] = [
        f for f in rr["required_fields"] if f not in ("limitations", "availability_assumption")
    ]
    save(tree, WINDOWS, doc)


def v4_independence_removed(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc.pop("independence", None)
    save(tree, WINDOWS, doc)


def v4_failure_states_emptied(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["failure_states"] = []
    save(tree, WINDOWS, doc)


def v4_ownership_restated_instead_of_referenced(tree: Path) -> None:
    """A10: an owner reference is not a licence to restate the owner's rules."""
    doc = load(tree, CONTEXT)
    mec = doc["minimum_effective_context"]
    mec["derivation_rules"] = {
        "step_1": "read the task packet",
        "step_2": "resolve the role",
        "step_3": "compute the effective set",
        "step_4": "pin each entry to a blob digest",
        "step_5": "reject anything unbounded",
    }
    save(tree, CONTEXT, doc)


# ---------------------------------------------------------------------------
# Case tables
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Invariant:
    name: str
    property_id: str
    description: str
    transform: Callable[[Path], None]


@dataclass(frozen=True)
class Difference:
    name: str
    attack_class: str
    description: str
    deciding_predicates: tuple[str, ...]
    transform: Callable[[Path], None]
    rationale: str = ""


INVARIANTS: tuple[Invariant, ...] = (
    Invariant("V4MT01", "container-shape invariance",
              "minimum effective context inside a transparent wrapper",
              v4_context_wrapped_in_transparent_container),
    Invariant("V4MT02", "container-shape invariance",
              "lifecycle inside a transparent wrapper",
              v4_lifecycle_wrapped_in_transparent_container),
    # V4MT03 and V4MT08 were filed as V4-FND-04-a and -04-c and are now measured
    # to hold. What changed is the FORM they use, not the adapter. The originals
    # wrote [{state: X}] and [{case: X}], and `state` and `case` are not in
    # COLLECTION_ID_FIELD_TOKENS - so those are single-entry mappings keyed
    # literally "state" and "case", which is outside the accepted equivalence
    # contract. The accepted engine treats its own containers the same way.
    # Ruling F04-A_REFINED: "if a tested form is not in that contract,
    # reclassify the test, not the candidate." Measured on the in-contract form
    # [{id: X}]: zero predicate movement, identical facts.
    Invariant("V4MT03", "container-shape invariance",
              "lifecycle states as an in-contract list-of-records",
              v4_lifecycle_states_as_list_of_records),
    Invariant("V4MT04", "ordering invariance",
              "lifecycle states and invalidation conditions reversed",
              v4_lifecycle_states_reversed),
    Invariant("V4MT05", "container-shape invariance",
              "derivation inputs as a list of single-key mappings",
              v4_derivation_inputs_as_list_of_pairs),
    Invariant("V4MT06", "container-shape invariance",
              "load set entries as records rather than scalars",
              v4_load_set_entries_as_records),
    Invariant("V4MT07", "container-shape invariance",
              "route receipt required fields as a mapping",
              v4_route_receipt_fields_as_mapping),
    Invariant("V4MT08", "container-shape invariance",
              "failure states as records",
              v4_failure_states_as_records),
    Invariant("V4MT09", "mention-vs-declaration distinction",
              "inert descriptive metadata beside every v4 region",
              v4_descriptive_metadata_added),
    Invariant("V4MT10", "negative-vs-positive polarity correctness",
              "equivalent closed-negative spellings of the same prohibition",
              v4_prohibitions_spelled_as_equivalent_negatives),
    # Ruling F03-D: representation is free, the SLOTS are fixed. Four ways of
    # writing the same three slots, all of which must produce the identical fact.
    # Without these the negative F03 cases below could be satisfied by admitting
    # exactly one record shape, which is rejected option F03-B under F03-D's name.
    Invariant("V4MT11", "container-shape invariance",
              "invalidation conditions as an in-contract list of records",
              v4_conditions_as_list_of_records),
    Invariant("V4MT12", "container-shape invariance",
              "invalidation conditions as a list of single-entry mappings",
              v4_conditions_as_list_of_single_entry_mappings),
    Invariant("V4MT13", "representation-neutrality",
              "invalidation conditions as bare names resolved by an explicit definitions block",
              v4_conditions_as_bare_names_with_definitions),
    Invariant("V4MT14", "synonym-not-spelling",
              "condition slot positions and observation role spelled by synonym",
              v4_condition_slots_spelled_differently),
    # Ruling F04-A_REFINED: `derivation_inputs` is a FIELD mapping, so every
    # admitted field-mapping shape must yield the same field names. The
    # single-entry-mapping form is V4MT05 above and was the filed V4-FND-04-b.
    Invariant("V4MT15", "container-shape invariance",
              "derivation inputs as a list of pairs",
              v4_derivation_inputs_as_pairs),
    Invariant("V4MT16", "container-shape invariance",
              "derivation inputs as a bare list of field names",
              v4_derivation_inputs_as_bare_field_names),
    Invariant("V4MT17", "region-scope correctness",
              "an A-required derivation input declared as a structured record rather than a scalar",
              v4_derivation_input_requirement_leaf_as_load_entry),
)


DIFFERENCES: tuple[Difference, ...] = (
    # poisoned vocabulary
    Difference("V4PV01", "poisoned_vocabulary",
               "unfamiliar stale-effect token in a normative position",
               ("P23",), v4_unknown_stale_effect_token,
               "Deciding predicate is P23, not P21, and that was measured rather "
               "than assumed: the stale EFFECT is read by the freshness adapter, "
               "so an unrecognised effect leaves every A-named trigger with no "
               "compliant effect. P21 owns the states and their conditions; P23 "
               "owns what a trigger does."),
    Difference("V4PV02", "poisoned_vocabulary",
               "unfamiliar route-receipt authority constant",
               ("P24",), v4_unknown_route_receipt_authority_constant),
    Difference("V4PV05", "poisoned_vocabulary",
               "unfamiliar on-failure behaviour",
               ("P27",), v4_unknown_on_failure_behaviour,
               "P27 reads a POSITIVE visible-failure vocabulary, so an unknown "
               "token fails. This is the direction the v3 findings require, and "
               "it is asserted here so a later change to a negative list is red."),
    # polarity
    Difference("V4PL01", "polarity_inversion",
               "default preload of all runs permitted instead of prohibited",
               ("P22",), v4_preload_permitted_instead_of_prohibited),
    Difference("V4PL02", "polarity_inversion",
               "historical run preload allowed",
               ("P22",), v4_historical_preload_allowed),
    Difference("V4PL03", "polarity_inversion",
               "same-window review permitted",
               ("P25",), v4_same_window_review_permitted),
    Difference("V4PL04", "polarity_inversion",
               "mixed deny/permit preload policy with a positive permission",
               ("P22",), v4_mixed_polarity_preload_policy,
               "a deny branch beside an allow branch does not neutralise the allow"),
    Difference("V4PL05", "polarity_inversion",
               "background progression enabled",
               ("P06",), v4_background_progression_enabled,
               "Caught by the ACCEPTED autonomy predicate P06, not by P21. "
               "Measured, not assumed. A03 and A14 overlap here and the accepted "
               "engine already owns autonomy, so P21 correctly does not "
               "re-litigate it. The case stays in the corpus because a future "
               "change that moved lifecycle out of P06's reach would go red."),
    # double negation
    Difference("V4DN01", "double_negation",
               "preload declared not_prohibited",
               ("P22",), v4_double_negated_preload),
    Difference("V4DN02", "double_negation",
               "same-window review declared not_prohibited",
               ("P25",), v4_double_negated_same_window_review,
               "Closed by ruling F02-A. Was V4-FND-02-a, a false PASS against "
               "A08: the rejection vocabulary overlaps the negation-token set, "
               "so \"prohibited\" matched and the modifying \"not\" was "
               "invisible. Parity over MODIFYING negations only."),
    Difference("V4DN03", "double_negation",
               "background progression declared not_disabled",
               ("P06",), v4_double_negated_background_progression,
               "Also P06, for the same measured reason as V4PL05."),
    # absence and weakening
    Difference("V4AB01", "absence_is_not_a_pass",
               "an A-required lifecycle state removed",
               ("P21",), v4_lifecycle_state_removed),
    Difference("V4AB02", "absence_is_not_a_pass",
               "invalidation conditions emptied",
               ("P21",), v4_invalidation_conditions_emptied),
    Difference("V4AB04", "exactness_required",
               "unbounded subtree entry added to the load set",
               ("P22",), v4_unbounded_load_set_entry),
    Difference("V4AB05", "absence_is_not_a_pass",
               "an A-required derivation input removed",
               ("P22",), v4_derivation_input_removed),
    Difference("V4AB06", "absence_is_not_a_pass",
               "the whole context contract document deleted",
               ("P22",), v4_context_contract_deleted),
    Difference("V4AB07", "absence_is_not_a_pass",
               "every field carrying two A-required receipt concepts removed",
               ("P24",), v4_route_receipt_concept_removed),
    Difference("V4AB08", "absence_is_not_a_pass",
               "the independence region removed",
               ("P25",), v4_independence_removed),
    Difference("V4AB09", "absence_is_not_a_pass",
               "failure states emptied",
               ("P27",), v4_failure_states_emptied),
    Difference("V4AB10", "ownership_separation",
               "owner's derivation rules restated locally instead of referenced",
               ("P26",), v4_ownership_restated_instead_of_referenced),
    # determinism, as a typed fact. Ruling F03-D. V4AB03 above was the false
    # pass; these five are the slot-level obligations it decomposes into, and
    # each one must be caught by P21 rather than by a neighbouring predicate.
    Difference("V4AB11", "determinism_required",
               "A-named triggers kept, their conditions written as prose",
               ("P21",), v4_A_named_triggers_kept_conditions_are_prose,
               "The variant V4-FND-03 recorded as owed. Its own measurement failed "
               "on P23 because replacing the conditions also removed the A-named "
               "triggers, so the finding could not show P21 catching this. Here "
               "the triggers survive verbatim, P23 has no complaint, and P21 is "
               "the only predicate that can fail. That is what closes the finding."),
    Difference("V4AB12", "determinism_required",
               "a condition declaring a comparison with no subject",
               ("P21",), v4_condition_subject_slot_missing),
    Difference("V4AB13", "determinism_required",
               "a condition whose observation is an unrecognised word",
               ("P21",), v4_condition_observation_unrecognised,
               "The case that proves the F03-D inversion landed. Under the deleted "
               "closed NEGATIVE vocabulary an unfamiliar word was deterministic by "
               "default. If this ever passes, the implementation has drifted back "
               "to presuming the unknown case safe - ST04-V3-IR-008."),
    Difference("V4AB14", "determinism_required",
               "a cadence declared where a comparison belongs",
               ("P21",), v4_condition_cadence_instead_of_comparison),
    Difference("V4AB15", "determinism_required",
               "the declared stale consequence is to continue from cache",
               ("P21",), v4_condition_consequence_is_continue_cached,
               "Slot 3 recognised and non-compliant, which is not the same as "
               "unknown. `continue_cached` is a named role in V4-FRESH-05 and is "
               "deliberately absent from V4-FRESH-06."),
)

# ---------------------------------------------------------------------------
# Cases that do NOT hold today
# ---------------------------------------------------------------------------
#
# These are kept in the corpus rather than deleted, and are asserted in the
# direction they actually measure: each test states "this hole is still open".
# When someone closes a hole the corresponding test goes red, which forces the
# table and the finding to be updated together. A corpus that quietly dropped
# its failing cases would be green and worthless - that is the shape of failure
# ST04-V3 was lost to, and it is not repeated here by making the passing suite
# silent about what it could not catch.


@dataclass(frozen=True)
class OpenHole:
    name: str
    finding_id: str
    kind: str
    description: str
    predicate: str
    observed_today: str
    required_by: str
    transform: Callable[[Path], None]
    why_it_matters: str = ""


OPEN_HOLES: tuple[OpenHole, ...] = (
    OpenHole(
        "V4OB01", "V4-OBS-01", "declared_but_unread",
        "exactness.entry_form replaced by an unfamiliar token",
        "P22", "pass", "A04",
        v4_unknown_exactness_entry_form,
        "Not a false pass against A04: A04 requires the load set to BE exact, and "
        "after this transformation every entry still is. The observation is that "
        "`exactness.entry_form` and `unbounded_subtree_entry` read as "
        "decision-bearing declarations but are never consumed - the judgement is "
        "made per entry from the path itself. Recorded so a reader does not "
        "assume those fields are enforced.",
    ),
    OpenHole(
        "V4OB02", "V4-OBS-02", "declared_but_unread",
        "route receipt missing_or_stale_or_inconsistent set to best_effort",
        "P24", "pass", "A07 and A12",
        v4_unknown_missing_receipt_behaviour,
        "Not a false pass against A07, which requires the receipt to CARRY the "
        "A-stated concepts with routing_only authority and says nothing about "
        "stale-receipt behaviour. A12 - visible failure rather than silent "
        "fallback - is arguably engaged, and 'best_effort' matches nothing in "
        "SILENT_FALLBACK_TOKENS. Whether A12 reaches this field is a semantic "
        "question, so it is reported rather than decided here.",
    ),
)

# ---------------------------------------------------------------------------
# Invariance cases that do NOT hold today
# ---------------------------------------------------------------------------
#
# Each of these is a representation change with no change of meaning, and each
# moves a predicate. That is RC-01 - the root cause the accepted methodology was
# built to eliminate - reappearing inside the v4 adapters. The accepted engine
# closed this family for roles, windows, handoff and entry modes (root-cause
# S01-S03, reviewer S02/S04); the v4 adapters did not inherit the fix because
# they do their own traversal.
#
# Recorded here in the direction they measure, for the same reason as OPEN_HOLES.


@dataclass(frozen=True)
class OpenInvarianceHole:
    name: str
    finding_id: str
    description: str
    predicate_that_moves: str
    observed_fact_effect: str
    transform: Callable[[Path], None]
    equivalent_form_precedent: str = ""


# All three entries this table held are gone, and for two different reasons. The
# table is kept, empty, because the tests that read it are the mechanism that
# forces a finding and its code to move together; deleting the table would delete
# the mechanism along with its current contents.
#
#   V4MT03 (V4-FND-04-a) and V4MT08 (V4-FND-04-c) were EXECUTOR TEST ERRORS.
#     They wrote `[{state: X}]` and `[{case: X}]`. Neither `state` nor `case` is
#     in COLLECTION_ID_FIELD_TOKENS, so both are single-entry mappings keyed
#     literally "state" and "case" - outside the accepted equivalence contract,
#     and the accepted engine treats its own containers the same way. Ruling
#     F04-A_REFINED requires proving a form is inside the contract before
#     claiming an equivalence case, and reclassifying the TEST when it is not.
#     Both now run the in-contract `[{id: X}]` form as ordinary invariants and
#     move no predicate.
#
#   V4MT05 (V4-FND-04-b) was a REAL DEFECT and is CLOSED.
#     `derivation_inputs` is a field-to-value mapping, not a keyed collection of
#     entities, and `role_id` is an id-field token - so `[{role_id: required}]`
#     normalized to an entity keyed "required" and the `role` input role
#     vanished while the other three survived. That asymmetry was the finding's
#     open question. `_normalize_field_mapping` answers it.
#
# Anything added here in future must be a measured representation change with no
# change of meaning that still moves a predicate.
OPEN_INVARIANCE_HOLES: tuple[OpenInvarianceHole, ...] = ()
