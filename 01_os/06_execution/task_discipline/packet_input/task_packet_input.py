"""Shared, fail-closed reader for task-discipline packet inputs.

Canonical input has exactly one top-level ``task_packet`` mapping. Existing flat
packets are accepted as the explicitly reported ``legacy_flat`` format. This is
input validation, not an authority or publication gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import yaml


class PacketInputError(ValueError):
    """The packet cannot be consumed without ambiguity or missing context."""


@dataclass(frozen=True)
class PacketInput:
    body: dict[str, Any]
    source_format: str
    normalized_fields: tuple[str, ...] = ()


def _check_yaml_nodes(node: yaml.Node, active: set[int], checked: set[int]) -> None:
    """Check raw explicit keys before SafeLoader expands legal YAML merges."""
    identity = id(node)
    if identity in active:
        raise PacketInputError("yaml_cycle")
    if identity in checked:
        return
    active.add(identity)
    if isinstance(node, yaml.MappingNode):
        explicit: set[tuple[str, str]] = set()
        for key, value in node.value:
            if not isinstance(key, yaml.ScalarNode) or key.tag not in {
                "tag:yaml.org,2002:str", "tag:yaml.org,2002:merge"
            }:
                raise PacketInputError("yaml_mapping_key_must_be_string")
            signature = (key.tag, key.value)
            if signature in explicit:
                raise PacketInputError(f"yaml_duplicate_explicit_key:{key.value}")
            explicit.add(signature)
            _check_yaml_nodes(value, active, checked)
    elif isinstance(node, yaml.SequenceNode):
        for value in node.value:
            _check_yaml_nodes(value, active, checked)
    active.remove(identity)
    checked.add(identity)


def load_yaml_text(text: str) -> Any:
    """Reject ambiguous explicit keys/cycles; retain normal SafeLoader merges."""
    loader = yaml.SafeLoader(text)
    try:
        node = loader.get_single_node()
        if node is None:
            raise PacketInputError("packet_empty_document")
        _check_yaml_nodes(node, set(), set())
        return loader.construct_document(node)
    except (yaml.YAMLError, RecursionError) as exc:
        raise PacketInputError(f"packet_yaml_error:{type(exc).__name__}:{exc}") from exc
    finally:
        loader.dispose()


def _string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise PacketInputError(f"packet_field_must_be_nonempty_string:{field}")


def _strings(value: Any, field: str, *, nonempty: bool = False) -> None:
    if not isinstance(value, list):
        raise PacketInputError(f"packet_field_must_be_list:{field}")
    if nonempty and not value:
        raise PacketInputError(f"packet_field_must_be_nonempty_list:{field}")
    for item in value:
        _string(item, f"{field}[]")


def _sha(value: Any, field: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-fA-F]{40}", value) is None:
        raise PacketInputError(f"packet_field_must_be_40_hex_sha:{field}")


def normalize_packet(data: Any) -> PacketInput:
    if not isinstance(data, dict):
        raise PacketInputError("packet_root_must_be_mapping")
    if "task_packet" in data:
        if set(data) != {"task_packet"}:
            raise PacketInputError("packet_mixed_wrapped_and_top_level_fields")
        body = data["task_packet"]
        source_format = "wrapped_v1"
    else:
        body = data
        source_format = "legacy_flat"
    if not isinstance(body, dict):
        raise PacketInputError("task_packet_must_be_mapping")
    body = dict(body)
    normalized: list[str] = []
    if "explicit_prohibitions" in body:
        _strings(body["explicit_prohibitions"], "explicit_prohibitions")
        if "prohibitions" in body:
            _strings(body["prohibitions"], "prohibitions")
            if body["prohibitions"] != body["explicit_prohibitions"]:
                raise PacketInputError("packet_conflicting_prohibitions_fields")
            normalized.append("explicit_prohibitions:equal_to_prohibitions")
        elif source_format == "legacy_flat":
            body["prohibitions"] = body["explicit_prohibitions"]
            normalized.append("explicit_prohibitions->prohibitions")
        else:
            raise PacketInputError("packet_field_missing:prohibitions")
        del body["explicit_prohibitions"]
    for field in ("task_id", "branch", "exact_base_sha", "allowed_changed_paths",
                  "required_tests", "prohibitions"):
        if field not in body:
            raise PacketInputError(f"packet_field_missing:{field}")
    _string(body["task_id"], "task_id")
    _string(body["branch"], "branch")
    _sha(body["exact_base_sha"], "exact_base_sha")
    _strings(body["allowed_changed_paths"], "allowed_changed_paths", nonempty=True)
    _strings(body["required_tests"], "required_tests", nonempty=True)
    _strings(body["prohibitions"], "prohibitions")
    if "big_task" in body and type(body["big_task"]) is not bool:
        raise PacketInputError("packet_field_must_be_boolean:big_task")
    if "publisher" in body:
        publisher = body["publisher"]
        if not isinstance(publisher, dict):
            raise PacketInputError("packet_field_must_be_mapping:publisher")
        for field in ("expected_remote_master_head", "expected_remote_head"):
            if field in publisher:
                _sha(publisher[field], f"publisher.{field}")
        # These are distinct refs, not aliases. A source branch's CAS head can
        # legitimately differ from master. Never infer one from the other.
    return PacketInput(body, source_format, tuple(normalized))


def read_packet(path: Path) -> PacketInput:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PacketInputError(f"packet_read_error:{type(exc).__name__}:{path}") from exc
    return normalize_packet(load_yaml_text(text))
