#!/usr/bin/env python3
"""Adversarial and metamorphic corpus.

Part one reproduces all fifteen independent adversarial variants constructed by
the v3 reviewer in
`04_测试生成/独立接收审核/v3/independent_v3_probes.py`, with the same semantic
intent and the same expected classification.  The reviewer's own results are
recorded alongside so the comparison is explicit rather than asserted.

Part two adds metamorphic transformations.  These are the tests that a mutation
corpus structurally cannot provide: mutation testing asks "does a change get
caught", while a metamorphic test asks "does an equivalent rewrite get the same
answer".  Three review generations were lost to the second question, which is why
it is a first-class part of this corpus.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .core import dump_yaml, load_yaml_strict

ROLES = "mechanism/roles_v1.yml"
WINDOWS = "mechanism/windows_v1.yml"
HANDOFF = "mechanism/handoff_v1.yml"

CONFORMING = "conforming"
NONCONFORMING = "nonconforming"


def load(tree: Path, rel: str) -> Any:
    return load_yaml_strict((tree / rel).read_text(encoding="utf-8"))


def save(tree: Path, rel: str, data: Any) -> None:
    (tree / rel).write_text(dump_yaml(data), encoding="utf-8")


def copy_tree(src: Path, dest: Path) -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    return dest


# --------------------------------------------------------------------------
# the fifteen independent v3 variants
# --------------------------------------------------------------------------


def i01_negative_prefix_handoff(tree: Path) -> None:
    doc = load(tree, HANDOFF)
    record = doc["handoff_record"]
    fields = list(record.pop("prohibited_fields"))
    for f in fields:
        record[f"prohibited_{f}"] = True
    save(tree, HANDOFF, doc)


def i02_list_record_handoff(tree: Path) -> None:
    doc = load(tree, HANDOFF)
    record = doc["handoff_record"]
    fields = list(record["prohibited_fields"])
    record["prohibited_fields"] = [{"field": f, "prohibited": True} for f in fields]
    save(tree, HANDOFF, doc)


def i03_list_pair_entry_modes(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["entry_modes"] = [[k, v] for k, v in doc["entry_modes"].items()]
    save(tree, WINDOWS, doc)


def i04_prohibited_provider_list(tree: Path) -> None:
    doc = load(tree, ROLES)
    doc["roles"]["independent_review"]["prohibited_provider"] = ["openai", "anthropic"]
    save(tree, ROLES, doc)


def i05_resource_neighbor_provider_pin(tree: Path) -> None:
    doc = load(tree, ROLES)
    doc["roles"]["independent_review"]["resource_constraints"] = {
        "preferred_provider": {"openai": True}
    }
    save(tree, ROLES, doc)


def i06_unlisted_provider_pin(tree: Path) -> None:
    doc = load(tree, ROLES)
    doc["roles"]["independent_review"]["preferred_provider"] = {"mistral": True}
    save(tree, ROLES, doc)


def i07_role_reference_matrix(tree: Path) -> None:
    target = tree / "workflow/role_reference_matrix.yml"
    entries = {}
    for role in ("backend_execution", "independent_review", "deep_research"):
        entries[role] = {
            "stage_scope": "task-declared",
            "model_route_ref": "model_routing/contract_v1.yml",
            "handoff_ref": "mechanism/handoff_v1.yml",
            "authority_ref": "registry/registry_v1.yml",
        }
    target.write_text(
        dump_yaml(
            {
                "schema_version": "workflow.role_reference_matrix.v1",
                "purpose": "references only; owns no role semantics",
                "role_references": entries,
            }
        ),
        encoding="utf-8",
    )


def i08_generic_id_second_role_source(tree: Path) -> None:
    target = tree / "workflow/second_role_source.yml"
    roles = {}
    for i, label in enumerate(
        ("backend_execution", "independent_review", "deep_research"), start=1
    ):
        roles[f"R{i}"] = {
            "label": label,
            "responsibility": f"normative responsibility for {label}",
            "independence_requirement": "normative separation rule",
            "authority_limit": "normative authority boundary",
        }
    target.write_text(
        dump_yaml(
            {
                "schema_version": "workflow.second_role_source.v1",
                "purpose": "stage-owned mutable role definitions",
                "role_definitions": roles,
            }
        ),
        encoding="utf-8",
    )


def i09_yaml_mapping_model_catalog(tree: Path) -> None:
    target = tree / "workflow/second_model_catalog.yml"
    target.write_text(
        dump_yaml(
            {
                "schema_version": "workflow.stage_model_tiers.v1",
                "stage_owned_tiers": {
                    "GPT-5.6 Sol": {"tier": "flagship", "mutable": True},
                    "GPT-5.6 Terra": {"tier": "balanced", "mutable": True},
                    "GPT-5.6 Luna": {"tier": "economy", "mutable": True},
                },
            }
        ),
        encoding="utf-8",
    )


def i10_markdown_heading_model_catalog(tree: Path) -> None:
    target = tree / "workflow/second_model_catalog_headings.md"
    target.write_text(
        "# Stage-owned mutable model catalog\n\n"
        "## GPT-5.6 Sol\n\nTier: flagship\n\n"
        "## GPT-5.6 Terra\n\nTier: balanced\n\n"
        "## GPT-5.6 Luna\n\nTier: economy\n",
        encoding="utf-8",
    )


def i11_non_boolean_autonomy(tree: Path) -> None:
    doc = load(tree, HANDOFF)
    doc["automatic_task_progression"] = "after_handoff_publication"
    doc["scheduler"] = "run_on_window_entry"
    save(tree, HANDOFF, doc)


def i12_carried_delivery_state(tree: Path) -> None:
    doc = load(tree, HANDOFF)
    doc["handoff_record"]["delivery_state"] = "mutable_runtime_state"
    save(tree, HANDOFF, doc)


def i13_string_authority_grant(tree: Path) -> None:
    doc = load(tree, ROLES)
    doc["roles"]["backend_execution"]["master_write_authorized"] = "granted"
    save(tree, ROLES, doc)


FULL_SURFACE_SENTINEL = "mechanism/full_surface_probe_sentinel.yml"


def i14_full_surface_sentinel(tree: Path) -> None:
    """Topology probe, carried over unchanged in intent from v3's I14.

    v3 proved the validator reads a full candidate tree rather than a
    boot-declared dependency closure.  The analogue here is that the extractor
    must see every document on the declared surface, including one that no
    manifest, registry or contract references.  If discovery ever narrows to a
    reachability closure, this sentinel disappears and the assertion fails.
    """
    (tree / FULL_SURFACE_SENTINEL).write_text(
        dump_yaml(
            {
                "schema_version": "prototype.full_surface_sentinel.v1",
                "purpose": "unreferenced by any manifest, registry or contract",
                "authority_effect": "none",
            }
        ),
        encoding="utf-8",
    )


def i15_no_run_id_binding(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    ident = doc["window_identity"]
    ident["bound_facts"] = [f for f in ident["bound_facts"] if f != "run_id"]
    fresh = doc["entry_modes"]["fresh"]
    fresh["required_fields"] = [f for f in fresh["required_fields"] if f != "run_id"]
    save(tree, WINDOWS, doc)


@dataclass
class Variant:
    name: str
    description: str
    expectation: str
    mutate: Callable[[Path], None]
    deciding_predicates: tuple[str, ...]
    root_cause_classes: tuple[str, ...]
    v3_harness_result: str  # what the previous harness did, per the v3 probe JSON
    v3_finding_refs: tuple[str, ...]


V3_VARIANTS: tuple[Variant, ...] = (
    Variant(
        "I01_negative_prefix_handoff_prohibitions",
        "negative-prefix prohibition fields must stay accepted",
        CONFORMING,
        i01_negative_prefix_handoff,
        ("P04",),
        ("polarity_normalization_failure",),
        "wrongly rejected (RW-T25 red; declared=[])",
        ("ST04-V3-IR-002",),
    ),
    Variant(
        "I02_list_record_handoff_prohibitions",
        "list-of-record prohibition declarations must stay accepted",
        CONFORMING,
        i02_list_record_handoff,
        ("P04",),
        ("polarity_normalization_failure",),
        "wrongly rejected (RW-T25 red; declared=['prohibited'])",
        ("ST04-V3-IR-002",),
    ),
    Variant(
        "I03_list_pair_entry_modes",
        "list-of-pairs preserves fresh/reentry and predecessor semantics",
        CONFORMING,
        i03_list_pair_entry_modes,
        ("P02",),
        ("representation_overfitting",),
        "wrongly rejected (RW-T08, RW-T09 red)",
        ("ST04-V3-IR-003", "ST04-V2-IR-002"),
    ),
    Variant(
        "I04_prohibited_provider_list",
        "a negative provider declaration is not a provider pin",
        CONFORMING,
        i04_prohibited_provider_list,
        ("P03",),
        ("polarity_normalization_failure",),
        "wrongly rejected (RW-T19 red)",
        ("ST04-V3-IR-002", "ST04-V3-IR-005"),
    ),
    Variant(
        "I05_resource_neighbor_provider_pin",
        "resource_constraints contains a normative provider pin",
        NONCONFORMING,
        i05_resource_neighbor_provider_pin,
        ("P03",),
        ("normative_selector_vs_provenance_confusion", "semantic_vs_lexical_confusion"),
        "wrongly accepted (43/43 green; 'source' matched inside 'resource')",
        ("ST04-V3-IR-005",),
    ),
    Variant(
        "I06_unlisted_provider_pin",
        "provider independence forbids unlisted vendors too",
        NONCONFORMING,
        i06_unlisted_provider_pin,
        ("P03",),
        ("normative_selector_vs_provenance_confusion",),
        "wrongly accepted (43/43 green; vendor absent from PROVIDER_TOKENS)",
        ("ST04-V3-IR-005",),
    ),
    Variant(
        "I07_role_reference_matrix",
        "pointer-only role matrix owns no role semantics",
        CONFORMING,
        i07_role_reference_matrix,
        ("P01",),
        ("reference_vs_ownership_confusion",),
        "wrongly rejected (RW-T05, RW-T31 red)",
        ("ST04-V3-IR-006", "ST04-V2-IR-004"),
    ),
    Variant(
        "I08_generic_id_second_role_source",
        "generic IDs with role labels still form a second role source",
        NONCONFORMING,
        i08_generic_id_second_role_source,
        ("P01",),
        ("reference_vs_ownership_confusion",),
        "wrongly accepted (43/43 green; role names lived in a label field)",
        ("ST04-V3-IR-006",),
    ),
    Variant(
        "I09_yaml_mapping_model_catalog",
        "YAML mapping keys restate the live model catalog",
        NONCONFORMING,
        i09_yaml_mapping_model_catalog,
        ("P07",),
        ("semantic_vs_lexical_confusion",),
        "wrongly accepted (43/43 green; key contained a space)",
        ("ST04-V3-IR-007",),
    ),
    Variant(
        "I10_markdown_heading_model_catalog",
        "repeated Markdown headings restate the live model catalog",
        NONCONFORMING,
        i10_markdown_heading_model_catalog,
        ("P07",),
        ("semantic_vs_lexical_confusion",),
        "wrongly accepted (43/43 green; headings were not a recognised entry form)",
        ("ST04-V3-IR-007", "ST04-V2-IR-005"),
    ),
    Variant(
        "I11_non_boolean_autonomy_enablement",
        "descriptive enabled values still activate automation",
        NONCONFORMING,
        i11_non_boolean_autonomy,
        ("P06",),
        ("automation_declaration_semantics_failure",),
        "wrongly accepted (43/43 green; closed positive truth vocabulary)",
        ("ST04-V3-IR-008",),
    ),
    Variant(
        "I12_carried_delivery_state",
        "a handoff cannot carry mutable delivery state",
        NONCONFORMING,
        i12_carried_delivery_state,
        ("P04",),
        ("state_reference_vs_state_carry_confusion",),
        "wrongly accepted (43/43 green; declaration accepted as proof of absence)",
        ("ST04-V3-IR-009",),
    ),
    Variant(
        "I13_string_authority_grant",
        "authority granted as a string is still an escalation",
        NONCONFORMING,
        i13_string_authority_grant,
        ("P05",),
        ("authority_mention_vs_authority_grant_confusion",),
        "wrongly accepted (43/43 green; 'granted' outside the positive vocabulary)",
        ("ST04-V3-IR-010",),
    ),
    Variant(
        "I14_full_surface_sentinel",
        "an unreferenced document on the declared surface must still be seen",
        CONFORMING,
        i14_full_surface_sentinel,
        ("P01", "P02", "P03", "P04", "P05", "P06", "P07"),
        ("evidence_topology_issue",),
        "correctly classified (the one sample of fifteen that was)",
        ("ST04-IR-005", "ST04-V2-IR-006"),
    ),
    Variant(
        "I15_no_run_id_binding",
        "A R02 requires task/role/stage/repository facts but does not mandate run_id",
        CONFORMING,
        i15_no_run_id_binding,
        ("P02",),
        ("requirement_vs_B_choice_confusion",),
        "wrongly rejected (RW-T07 red)",
        ("ST04-V3-IR-004", "ST04-IR-002"),
    ),
)


# --------------------------------------------------------------------------
# metamorphic transformations
# --------------------------------------------------------------------------


def mt_entry_modes_list_of_records(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["entry_modes"] = [
        dict({"mode_id": k}, **v) for k, v in doc["entry_modes"].items()
    ]
    save(tree, WINDOWS, doc)


def mt_entry_modes_list_of_single_maps(tree: Path) -> None:
    doc = load(tree, WINDOWS)
    doc["entry_modes"] = [{k: v} for k, v in doc["entry_modes"].items()]
    save(tree, WINDOWS, doc)


def mt_reverse_ordering(tree: Path) -> None:
    roles = load(tree, ROLES)
    roles["roles"] = dict(reversed(list(roles["roles"].items())))
    for body in roles["roles"].values():
        if isinstance(body.get("allowed_handoff_to_roles"), list):
            body["allowed_handoff_to_roles"] = list(reversed(body["allowed_handoff_to_roles"]))
    save(tree, ROLES, roles)
    handoff = load(tree, HANDOFF)
    record = handoff["handoff_record"]
    record["prohibited_fields"] = list(reversed(record["prohibited_fields"]))
    record["required_fields"] = list(reversed(record["required_fields"]))
    save(tree, HANDOFF, handoff)


def mt_prohibitions_as_mapping(tree: Path) -> None:
    doc = load(tree, HANDOFF)
    record = doc["handoff_record"]
    record["prohibited_fields"] = {f: True for f in record["prohibited_fields"]}
    save(tree, HANDOFF, doc)


def mt_prohibitions_as_suffix(tree: Path) -> None:
    doc = load(tree, HANDOFF)
    record = doc["handoff_record"]
    fields = list(record.pop("prohibited_fields"))
    for f in fields:
        record[f"{f}_prohibited"] = True
    save(tree, HANDOFF, doc)


def mt_unknown_vendor_pin(tree: Path) -> None:
    doc = load(tree, ROLES)
    doc["roles"]["independent_review"]["preferred_provider"] = {"zzq_nonexistent_vendor_9": True}
    save(tree, ROLES, doc)


def mt_provenance_key_rename(tree: Path) -> None:
    """The real pin from I05, moved under a key whose name contains 'source'."""
    doc = load(tree, ROLES)
    doc["roles"]["independent_review"]["outsourced_constraints"] = {
        "preferred_provider": {"openai": True}
    }
    save(tree, ROLES, doc)


def mt_provider_polarity_flip(tree: Path) -> None:
    """I04's negative constraint flipped to a positive selection."""
    doc = load(tree, ROLES)
    doc["roles"]["independent_review"]["preferred_provider"] = ["openai", "anthropic"]
    save(tree, ROLES, doc)


def mt_reference_becomes_ownership(tree: Path) -> None:
    """I07's pointer-only matrix given one semantic field."""
    i07_role_reference_matrix(tree)
    target = tree / "workflow/role_reference_matrix.yml"
    doc = load_yaml_strict(target.read_text(encoding="utf-8"))
    for body in doc["role_references"].values():
        body["responsibility"] = "normative responsibility owned here"
    target.write_text(dump_yaml(doc), encoding="utf-8")


def mt_authority_value_unknown_scalar(tree: Path) -> None:
    doc = load(tree, ROLES)
    doc["roles"]["backend_execution"]["master_write_authorized"] = "per_task_escalation"
    save(tree, ROLES, doc)


def mt_delivery_state_as_pointer(tree: Path) -> None:
    """A REFERENCE to delivery state is a pointer, not carried mutable state."""
    doc = load(tree, HANDOFF)
    doc["handoff_record"]["delivery_state_ref"] = "communication_system/message_v1.yml"
    save(tree, HANDOFF, doc)


def mt_delivery_state_ref_without_a_path(tree: Path) -> None:
    """A pointer-NAMED key holding a value is still carried state.

    This is the fail-closed half of MT11: renaming a field `*_ref` must not
    launder it.
    """
    doc = load(tree, HANDOFF)
    doc["handoff_record"]["delivery_state_ref"] = "delivered_at_2026_08_12"
    save(tree, HANDOFF, doc)


def mt_autonomy_key_negated(tree: Path) -> None:
    """The same truthy value under a negated key asserts the prohibition."""
    doc = load(tree, HANDOFF)
    doc["automatic_task_progression_prohibited"] = True
    doc["scheduler_prohibited"] = True
    save(tree, HANDOFF, doc)


def mt_drop_b_only_run_id(tree: Path) -> None:
    i15_no_run_id_binding(tree)


@dataclass
class Metamorphic:
    name: str
    property_id: str
    description: str
    transform: Callable[[Path], None]
    expectation: str  # "invariant" | "flips_to_fail"
    baseline: str  # "baseline" or the name of a v3 variant to start from
    deciding_predicates: tuple[str, ...]


METAMORPHIC: tuple[Metamorphic, ...] = (
    Metamorphic(
        "MT01_entry_mode_list_of_records",
        "container-shape invariance",
        "entry modes as a list of records must give the same result as a mapping",
        mt_entry_modes_list_of_records,
        "invariant",
        "baseline",
        ("P02",),
    ),
    Metamorphic(
        "MT02_entry_mode_list_of_single_maps",
        "container-shape invariance",
        "entry modes as a list of single-entry mappings must give the same result",
        mt_entry_modes_list_of_single_maps,
        "invariant",
        "baseline",
        ("P02",),
    ),
    Metamorphic(
        "MT03_ordering",
        "ordering invariance",
        "reversing unordered collections must not change any result",
        mt_reverse_ordering,
        "invariant",
        "baseline",
        ("P01", "P04"),
    ),
    Metamorphic(
        "MT04_prohibitions_as_mapping",
        "container-shape invariance",
        "prohibitions as a mapping must give the same result as a list",
        mt_prohibitions_as_mapping,
        "invariant",
        "baseline",
        ("P04",),
    ),
    Metamorphic(
        "MT05_prohibitions_as_suffix",
        "container-shape invariance",
        "negation-suffix prohibitions must give the same result as a list",
        mt_prohibitions_as_suffix,
        "invariant",
        "baseline",
        ("P04",),
    ),
    Metamorphic(
        "MT06_unknown_vendor_pin",
        "unknown-provider-name invariance",
        "a pin naming a vendor no list contains must fail exactly like a known one",
        mt_unknown_vendor_pin,
        "flips_to_fail",
        "baseline",
        ("P03",),
    ),
    Metamorphic(
        "MT07_provenance_key_rename",
        "normative-selector vs provenance",
        "renaming an enclosing key to contain 'source' must not silence a real pin",
        mt_provenance_key_rename,
        "flips_to_fail",
        "baseline",
        ("P03",),
    ),
    Metamorphic(
        "MT08_provider_polarity_flip",
        "negative-vs-positive polarity correctness",
        "the same vendor list under a positive selector must fail",
        mt_provider_polarity_flip,
        "flips_to_fail",
        "baseline",
        ("P03",),
    ),
    Metamorphic(
        "MT09_reference_becomes_ownership",
        "reference-vs-ownership distinction",
        "adding one semantic field to a pointer-only matrix must flip it to a second source",
        mt_reference_becomes_ownership,
        "flips_to_fail",
        "baseline",
        ("P01",),
    ),
    Metamorphic(
        "MT10_authority_unknown_scalar",
        "mention-vs-grant distinction",
        "an uninterpretable authority value must fail closed, not pass",
        mt_authority_value_unknown_scalar,
        "flips_to_fail",
        "baseline",
        ("P05",),
    ),
    Metamorphic(
        "MT11_delivery_state_as_pointer",
        "pointer-vs-mutable-state distinction",
        "a REFERENCE to delivery state is a pointer and must stay accepted",
        mt_delivery_state_as_pointer,
        "invariant",
        "baseline",
        ("P04",),
    ),
    Metamorphic(
        "MT11b_delivery_state_ref_without_a_path",
        "pointer-vs-mutable-state distinction",
        "a pointer-named key holding a state value must still fail closed",
        mt_delivery_state_ref_without_a_path,
        "flips_to_fail",
        "baseline",
        ("P04",),
    ),
    Metamorphic(
        "MT12_autonomy_key_negated",
        "negative-vs-positive polarity correctness",
        "a truthy value under a negated autonomy key asserts the prohibition",
        mt_autonomy_key_negated,
        "invariant",
        "baseline",
        ("P06",),
    ),
    Metamorphic(
        "MT13_drop_b_only_run_id",
        "optional-B-field removal invariance",
        "removing run_id, a B_ONLY fact, must not change any result",
        mt_drop_b_only_run_id,
        "invariant",
        "baseline",
        ("P02",),
    ),
)



# --------------------------------------------------------------------------
# Part three: transformation families the independent review proved effective.
#
# The FIX_REQUIRED review ran 63 probes this corpus had never seen and found 29
# counterexamples.  Closing the 29 instances is necessary and not sufficient: an
# instance is a sample, a family is a theorem.  Each transformation below turns
# one of the review's effective families into a durable property, so the same
# DEFECT CLASS cannot return in a spelling nobody happened to try.
#
# These are written independently.  `08_独立审核/**` is the reviewer's immutable
# evidence and is neither imported nor copied here; the constructions differ from
# the probes even where the family is shared, which is the point — a family that
# only holds for the exact bytes the reviewer used is not a family.
# --------------------------------------------------------------------------


def mt_transparent_role_wrapper(tree: Path) -> None:
    """Wrapping a role table in a container that adds nothing must change nothing."""
    doc = load(tree, ROLES)
    doc["binding_document"] = {"contract_body": {"roles": doc.pop("roles")}}
    save(tree, ROLES, doc)


def mt_transparent_window_and_handoff_wrapper(tree: Path) -> None:
    win = load(tree, WINDOWS)
    win["specification"] = {
        "window_identity": win.pop("window_identity"),
        "entry_modes": win.pop("entry_modes"),
    }
    save(tree, WINDOWS, win)
    hand = load(tree, HANDOFF)
    hand["specification"] = {"handoff_record": hand.pop("handoff_record")}
    save(tree, HANDOFF, hand)


def mt_descriptive_positions_added(tree: Path) -> None:
    """Commentary about a subject is not a declaration of it, at any length."""
    doc = load(tree, ROLES)
    doc["roles"]["backend_execution"]["authority_summary"] = "unchanged"
    doc["roles"]["backend_execution"]["permission_rationale"] = "stated elsewhere"
    save(tree, ROLES, doc)
    hand = load(tree, HANDOFF)
    hand["progression"]["scheduler_explanation"] = "named here only to record that it stays off"
    save(tree, HANDOFF, hand)


def mt_role_applicability_metadata(tree: Path) -> None:
    """Applicability metadata keyed by role name owns no role semantics."""
    target = tree / "workflow/stage_role_applicability.yml"
    target.write_text(
        dump_yaml(
            {
                "schema_version": "workflow.stage_role_applicability.v1",
                "applicability": {
                    "backend_execution": {"stage_scope": "execution", "context_scope": "minimal"},
                    "independent_review": {"stage_scope": "review", "context_scope": "primary"},
                    "deep_research": {"stage_scope": "research", "context_scope": "declared_lanes"},
                },
            }
        ),
        encoding="utf-8",
    )


def mt_unseen_role_labels_second_source(tree: Path) -> None:
    """A real second role source whose role names appear in no vocabulary."""
    target = tree / "workflow/stage_owned_roles.yml"
    target.write_text(
        dump_yaml(
            {
                "schema_version": "workflow.stage_owned_roles.v1",
                "definitions": {
                    "K1": {
                        "designation": "wright",
                        "responsibility": "normative construction responsibility",
                    },
                    "K2": {
                        "designation": "assayer",
                        "independence_requirement": "normative separation from the wright",
                    },
                },
            }
        ),
        encoding="utf-8",
    )


def mt_double_negated_authority(tree: Path) -> None:
    """Two negations are a grant of the thing they twice deny."""
    doc = load(tree, ROLES)
    doc["roles"]["backend_execution"]["publication_never_disallowed"] = True
    save(tree, ROLES, doc)


def mt_double_negated_autonomy(tree: Path) -> None:
    doc = load(tree, HANDOFF)
    doc["progression"]["watcher_not_disabled"] = True
    save(tree, HANDOFF, doc)


def mt_nested_autonomy_enablement(tree: Path) -> None:
    """Enablement one level down is enablement."""
    doc = load(tree, HANDOFF)
    doc["progression"]["daemon"] = {"activation": {"state": "armed"}}
    save(tree, HANDOFF, doc)


def mt_unknown_vocabulary_automation_region(tree: Path) -> None:
    """An automation region written entirely in unfamiliar words must fail closed."""
    doc = load(tree, HANDOFF)
    doc["progression"]["automation_envelope"] = {"cadence": {"fires_on": "stage_exit"}}
    save(tree, HANDOFF, doc)


def mt_nested_authority_grant(tree: Path) -> None:
    doc = load(tree, ROLES)
    doc["roles"]["backend_execution"]["privileges"] = {
        "publication": {"disposition": "conferred"}
    }
    save(tree, ROLES, doc)


def mt_mixed_polarity_provider_policy(tree: Path) -> None:
    """Forbidding one subject does not neutralise pinning another."""
    doc = load(tree, ROLES)
    doc["roles"]["independent_review"]["model_policy"] = {
        "permitted": {"selected": "Halcyon-Reasoner-3"},
        "denied": ["Kestrel-Engine"],
    }
    save(tree, ROLES, doc)


def mt_provider_in_selection_slot(tree: Path) -> None:
    """A subject in a declared selection slot is a pin wherever the slot sits."""
    doc = load(tree, ROLES)
    doc["roles"]["independent_review"]["model_selection"] = {"assigned": "Halcyon-Reasoner-3"}
    save(tree, ROLES, doc)


def mt_two_entry_second_catalog(tree: Path) -> None:
    """A11 grants no size exception: two entries are already a second catalog."""
    target = tree / "workflow/stage_two_entry_catalog.yml"
    target.write_text(
        dump_yaml(
            {
                "schema_version": "workflow.stage_two_entry_catalog.v1",
                "stage_owned": {
                    "GPT-5.6 Sol": {"tier": "flagship"},
                    "GPT-5.6 Terra": {"tier": "balanced"},
                },
            }
        ),
        encoding="utf-8",
    )


def mt_catalog_spelling_equivalents(tree: Path) -> None:
    """Case, spacing and punctuation variants are the same identifier."""
    target = tree / "workflow/stage_variant_catalog.yml"
    target.write_text(
        dump_yaml(
            {
                "schema_version": "workflow.stage_variant_catalog.v1",
                "stage_owned": {
                    "gpt 5.6 sol": {"tier": "flagship"},
                    "GPT_5_6_TERRA": {"tier": "balanced"},
                    "gpt-5.6-luna": {"tier": "economy"},
                },
            }
        ),
        encoding="utf-8",
    )


def mt_catalog_with_unseen_identifiers(tree: Path) -> None:
    """A second catalog is one by shape, even when every identifier is unfamiliar."""
    target = tree / "workflow/stage_unseen_catalog.yml"
    target.write_text(
        dump_yaml(
            {
                "schema_version": "workflow.stage_unseen_catalog.v1",
                "routing_table": {
                    "entries": [
                        {"model": "Halcyon-Reasoner-3", "tier": "primary"},
                        {"model": "Kestrel-Engine", "tier": "secondary"},
                    ]
                },
            }
        ),
        encoding="utf-8",
    )


def mt_single_identifier_mention(tree: Path) -> None:
    """One identifier named once is a mention, not a catalog."""
    target = tree / "workflow/stage_single_mention.yml"
    target.write_text(
        dump_yaml(
            {
                "schema_version": "workflow.stage_single_mention.v1",
                "model_catalog_ref": "model_routing/catalog_v1.yml",
                "worked_example_identifier": "GPT-5.6 Sol",
            }
        ),
        encoding="utf-8",
    )


def mt_nested_carried_state_in_list(tree: Path) -> None:
    """Carried state inside a list of records is the same carried state."""
    doc = load(tree, HANDOFF)
    doc["handoff_record"]["audit_trail"] = [{"step": 1, "read_state": "opened"}]
    save(tree, HANDOFF, doc)


METAMORPHIC = METAMORPHIC + (
    Metamorphic(
        "MT14_transparent_role_wrapper",
        "transparent-container invariance",
        "wrapping the role table in two containers that add no content changes nothing",
        mt_transparent_role_wrapper,
        "invariant",
        "baseline",
        ("P01",),
    ),
    Metamorphic(
        "MT15_transparent_window_and_handoff_wrapper",
        "transparent-container invariance",
        "wrapping the window and handoff blocks changes nothing",
        mt_transparent_window_and_handoff_wrapper,
        "invariant",
        "baseline",
        ("P02", "P04"),
    ),
    Metamorphic(
        "MT16_descriptive_positions",
        "descriptive-position invariance",
        "commentary about authority or a scheduler is not a declaration of either",
        mt_descriptive_positions_added,
        "invariant",
        "baseline",
        ("P05", "P06"),
    ),
    Metamorphic(
        "MT17_role_applicability_metadata",
        "applicability-metadata vs ownership",
        "a role-keyed applicability table owns no role semantics",
        mt_role_applicability_metadata,
        "invariant",
        "baseline",
        ("P01",),
    ),
    Metamorphic(
        "MT18_unseen_role_labels_second_source",
        "applicability-metadata vs ownership",
        "role names in no vocabulary still form a second role source",
        mt_unseen_role_labels_second_source,
        "flips_to_fail",
        "baseline",
        ("P01",),
    ),
    Metamorphic(
        "MT19_double_negated_authority",
        "double-negation polarity correctness",
        "publication_never_disallowed: true is a grant",
        mt_double_negated_authority,
        "flips_to_fail",
        "baseline",
        ("P05",),
    ),
    Metamorphic(
        "MT20_double_negated_autonomy",
        "double-negation polarity correctness",
        "watcher_not_disabled: true enables a watcher",
        mt_double_negated_autonomy,
        "flips_to_fail",
        "baseline",
        ("P06",),
    ),
    Metamorphic(
        "MT21_nested_autonomy_enablement",
        "nested-enablement detection",
        "a daemon armed two levels down is armed",
        mt_nested_autonomy_enablement,
        "flips_to_fail",
        "baseline",
        ("P06",),
    ),
    Metamorphic(
        "MT22_unknown_vocabulary_automation_region",
        "unknown-vocabulary fail-closed",
        "an automation region written in unfamiliar words fails closed",
        mt_unknown_vocabulary_automation_region,
        "flips_to_fail",
        "baseline",
        ("P06",),
    ),
    Metamorphic(
        "MT23_nested_authority_grant",
        "nested-enablement detection",
        "a privilege conferred two levels down is conferred",
        mt_nested_authority_grant,
        "flips_to_fail",
        "baseline",
        ("P05",),
    ),
    Metamorphic(
        "MT24_mixed_polarity_provider_policy",
        "mixed-polarity policy correctness",
        "a deny list beside an allow selection does not neutralise the selection",
        mt_mixed_polarity_provider_policy,
        "flips_to_fail",
        "baseline",
        ("P03",),
    ),
    Metamorphic(
        "MT25_provider_in_selection_slot",
        "mixed-polarity policy correctness",
        "a subject in a declared selection slot is a pin",
        mt_provider_in_selection_slot,
        "flips_to_fail",
        "baseline",
        ("P03",),
    ),
    Metamorphic(
        "MT26_two_entry_second_catalog",
        "catalog-size independence",
        "two entries are already a second mutable catalog",
        mt_two_entry_second_catalog,
        "flips_to_fail",
        "baseline",
        ("P07",),
    ),
    Metamorphic(
        "MT27_catalog_spelling_equivalents",
        "catalog spelling equivalence",
        "case, spacing and punctuation variants are the same identifiers",
        mt_catalog_spelling_equivalents,
        "flips_to_fail",
        "baseline",
        ("P07",),
    ),
    Metamorphic(
        "MT28_catalog_with_unseen_identifiers",
        "unknown-vocabulary fail-closed",
        "a routing table of unfamiliar identifiers is still a second catalog",
        mt_catalog_with_unseen_identifiers,
        "flips_to_fail",
        "baseline",
        ("P07",),
    ),
    Metamorphic(
        "MT29_single_identifier_mention",
        "catalog-size independence",
        "one identifier named once is a mention and must stay accepted",
        mt_single_identifier_mention,
        "invariant",
        "baseline",
        ("P07",),
    ),
    Metamorphic(
        "MT30_nested_carried_state_in_list",
        "pointer-vs-mutable-state distinction",
        "carried delivery state inside a list of records is still carried",
        mt_nested_carried_state_in_list,
        "flips_to_fail",
        "baseline",
        ("P04",),
    ),
)
