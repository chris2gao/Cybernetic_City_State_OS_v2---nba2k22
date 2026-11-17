"""Read-only CLI to preview any domain task prototype before Human review.

An input JSON is only a proposal. This never writes approvals, grants authority,
invokes a tool, or marks the prototype accepted.
"""
from __future__ import annotations

import argparse
from dataclasses import fields
import json
from pathlib import Path
from typing import Any

from reviewed_prototypes import Criterion, Operation, ProcedureStep, Prototype, review_packet


SCHEMA = "citystate.task-prototype-review.v1"


def _strict(model: type, payload: Any):
    if not isinstance(payload, dict):
        raise ValueError(f"{model.__name__} must be an object")
    accepted = {f.name for f in fields(model)}
    extra = set(payload) - accepted
    if extra:
        raise ValueError(f"{model.__name__} unknown fields: {sorted(extra)}")
    try:
        return model(**payload)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {model.__name__}: {exc}") from exc


def parse_node(value: Any) -> Prototype:
    if not isinstance(value, dict):
        raise ValueError("Prototype must be an object")
    allowed = {f.name for f in fields(Prototype)}
    if set(value) - allowed:
        raise ValueError(f"Unknown prototype fields: {sorted(set(value) - allowed)}")
    op = value.get("operation")
    if op is not None:
        op = _strict(Operation, dict(op, parameters=tuple(op["parameters"])))
    return Prototype(
        key=value["key"],
        goal=value["goal"],
        ready=tuple(_strict(Criterion, item) for item in value.get("ready", [])),
        done=tuple(_strict(Criterion, item) for item in value["done"]),
        operation=op,
        children=tuple(parse_node(child) for child in value.get("children", [])),
        procedure=tuple(_strict(ProcedureStep, item) for item in value.get("procedure", [])),
    )


def parse_document(doc: Any) -> Prototype:
    if not isinstance(doc, dict) or set(doc) != {"schema", "prototype"} or doc["schema"] != SCHEMA:
        raise ValueError("Expected exact proposal schema and prototype fields")
    candidate = parse_node(doc["prototype"])
    review_packet(candidate)  # Validate complete tree and detailed criteria before preview.
    return candidate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect, never approve or execute, an atomic task prototype")
    parser.add_argument("--input", required=True, type=Path, help="JSON proposal to inspect")
    args = parser.parse_args(argv)
    try:
        proposal = json.loads(args.input.read_text(encoding="utf-8"))
        packet = review_packet(parse_document(proposal))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "INVALID_PROPOSAL", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"schema": SCHEMA, "status": "PENDING_HUMAN_REVIEW", "nodes": packet},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
