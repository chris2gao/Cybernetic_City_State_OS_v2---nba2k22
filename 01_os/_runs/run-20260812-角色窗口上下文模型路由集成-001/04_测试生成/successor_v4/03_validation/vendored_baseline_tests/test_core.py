"""Unit tests for the normalization primitives.

Each test names the finding it exists to keep closed.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401

from semantic_acceptance.core import (
    DISABLED,
    ENABLED,
    NEGATIVE,
    POSITIVE,
    classify_enablement,
    extract_declarations,
    is_negated,
    is_provenance_segment,
    normalize_keyed_collection,
    parse_markdown_blocks,
    strip_negation,
    tokens,
)


def test_tokens_never_yield_a_substring():
    """ST04-V3-IR-005: 'resource' must not produce the token 'source'."""
    assert tokens("resource_constraints") == ["resource", "constraints"]
    assert "source" not in tokens("resource_constraints")
    assert "source" in tokens("source_evidence")


def test_provenance_is_whole_token():
    assert not is_provenance_segment("resource_constraints")
    assert not is_provenance_segment("outsourced_constraints")
    assert is_provenance_segment("evidence_refs")
    assert is_provenance_segment("routing_basis")


def test_negation_is_prefix_and_suffix_symmetric():
    """ST04-V2-IR-001 and ST04-V3-IR-002 are the two halves of this."""
    assert is_negated("prohibited_private_reasoning")
    assert is_negated("private_reasoning_prohibited")
    assert is_negated("private_reasoning_disabled")
    assert not is_negated("private_reasoning")
    assert strip_negation("prohibited_private_reasoning") == "private_reasoning"
    assert strip_negation("private_reasoning_prohibited") == "private_reasoning"


def test_must_alone_is_not_a_negation():
    assert not is_negated("must_hold")
    assert is_negated("must_not_be_claimed_as")


def test_enablement_closed_negative_set():
    """ST04-V3-IR-008 and ST04-V3-IR-010: unknown must not read as safe."""
    assert classify_enablement(False) == DISABLED
    assert classify_enablement("false") == DISABLED
    assert classify_enablement("none") == DISABLED
    assert classify_enablement(True) == ENABLED
    assert classify_enablement("granted") == ENABLED
    assert classify_enablement("after_handoff_publication") == ENABLED
    assert classify_enablement("run_on_window_entry") == ENABLED
    assert classify_enablement("per_task_escalation") == ENABLED


def test_keyed_collection_shapes_are_equivalent():
    """ST04-V2-IR-002 and ST04-V3-IR-003."""
    body_a = {"required_fields": ["window_id"]}
    body_b = {"required_fields": ["predecessor_window_id"]}
    mapping = {"fresh": body_a, "reentry": body_b}
    pairs = [["fresh", body_a], ["reentry", body_b]]
    records = [dict({"mode_id": "fresh"}, **body_a), dict({"mode_id": "reentry"}, **body_b)]
    singles = [{"fresh": body_a}, {"reentry": body_b}]
    for form in (mapping, pairs, records, singles):
        got = normalize_keyed_collection(form)
        assert set(got) == {"fresh", "reentry"}, form
        assert got["fresh"]["required_fields"] == ["window_id"], form


def test_declaration_forms_reduce_to_the_same_field():
    """The five source forms must produce one (field, polarity) pair."""
    forms = {
        "list": {"prohibited_fields": ["private_reasoning"]},
        "mapping": {"prohibited_fields": {"private_reasoning": True}},
        "records": {"prohibited_fields": [{"field": "private_reasoning", "prohibited": True}]},
        "prefix": {"prohibited_private_reasoning": True},
        "suffix": {"private_reasoning_prohibited": True},
    }
    for label, scope in forms.items():
        decls = extract_declarations(scope)
        fields = {(d.field, d.polarity) for d in decls}
        assert ("private_reasoning", NEGATIVE) in fields, (label, decls)


def test_record_form_never_yields_the_qualifier_name():
    """ST04-V3-IR-002: the previous collector emitted 'prohibited'."""
    decls = extract_declarations(
        {"prohibited_fields": [{"field": "delivery_state", "prohibited": True}]}
    )
    fields = {d.field for d in decls}
    assert fields == {"delivery_state"}
    assert "prohibited" not in fields


def test_prohibited_false_is_positive():
    decls = extract_declarations({"prohibited_delivery_state": False})
    assert [(d.field, d.polarity) for d in decls] == [("delivery_state", POSITIVE)]


def test_markdown_block_forms():
    """ST04-V2-IR-005 and ST04-V3-IR-007: headings and definition lists count."""
    text = (
        "# Title\n\n"
        "## GPT-5.6 Sol\n\n"
        "Setext Heading\n==============\n\n"
        "- list item alpha\n"
        "1. ordered item beta\n\n"
        "| a | b |\n|---|---|\n| cell one | cell two |\n\n"
        "Definition Term\n:   the definition\n\n"
        "plain_key: plain value\n"
    )
    b = parse_markdown_blocks(text)
    assert "GPT-5.6 Sol" in b.headings
    assert "Setext Heading" in b.headings
    assert "list item alpha" in b.list_items
    assert "ordered item beta" in b.list_items
    assert "cell one" in b.table_cells
    assert "Definition Term" in b.definition_terms
    assert "plain_key" in b.key_value_keys


def test_markdown_ignores_fenced_code():
    b = parse_markdown_blocks("```\n## Not A Heading\n```\n## Real Heading\n")
    assert b.headings == ["Real Heading"]
