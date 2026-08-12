#!/usr/bin/env python3
"""Fixture mechanism validator (Stage 04 positive fixture, not canonical).

Exists so that MR-T24 can prove the mechanism's own validator fails closed on a
catalog entry missing a freshness field. Stage 05/06 must supply a real one; this
one only implements the fail-closed obligations the frozen tests assert.

usage: verify_model_routing.py static <tree_root>
exit 0 pass, non-zero fail.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

MECH = "01_os/03_mechanisms/model_routing"
BOOT = "01_os/02_boot/model_routing/启动清单_v1.yml"
REGISTRY = "01_os/05_registry/model_routing_v1.yml"
FRESHNESS = ("source_refs", "verified_at", "invalidation_conditions", "confidence")


class DupKey(Exception):
    pass


class Strict(yaml.SafeLoader):
    pass


def _nodup(loader, node, deep=False):
    out = {}
    for k, v in node.value:
        key = loader.construct_object(k, deep=deep)
        if key in out:
            raise DupKey(str(key))
        out[key] = loader.construct_object(v, deep=deep)
    return out


Strict.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _nodup)


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] != "static":
        print("usage: verify_model_routing.py static <tree_root>", file=sys.stderr)
        return 2
    root = Path(sys.argv[2]).resolve()
    findings: list[str] = []

    docs = {}
    for p in sorted((root / MECH).rglob("*.yml")):
        try:
            docs[p] = yaml.load(p.read_text(encoding="utf-8"), Loader=Strict)
        except DupKey as exc:
            findings.append(f"duplicate_key:{p.name}:{exc}")
        except Exception as exc:  # noqa: BLE001
            findings.append(f"parse_error:{p.name}:{type(exc).__name__}")

    def by_token(tok):
        for p, d in docs.items():
            if isinstance(d, dict) and str(d.get("schema_version", "")).startswith(tok):
                return d
        return None

    contract = by_token("citystate.model_routing.contract.v")
    catalog = by_token("citystate.model_routing.catalog.v")
    ledger = by_token("citystate.model_routing.project_observation.v")
    for name, doc in (("contract", contract), ("catalog", catalog), ("ledger", ledger)):
        if doc is None:
            findings.append(f"missing_document:{name}")

    if catalog:
        for e in catalog.get("entries", []) or []:
            if not isinstance(e, dict):
                findings.append("malformed_entry")
                continue
            label = f"{e.get('surface_id')}::{e.get('model_label')}"
            if e.get("registered") is not True:
                continue
            for f in FRESHNESS:
                val = e.get(f)
                if val is None or (isinstance(val, (list, str, dict)) and len(val) == 0):
                    findings.append(f"missing_freshness:{label}:{f}")

    if ledger:
        for o in ledger.get("observations", []) or []:
            if not isinstance(o, dict) or o.get("validity") not in {
                "formal",
                "diagnostic",
                "anecdotal",
            }:
                findings.append(f"bad_validity:{o.get('observation_id') if isinstance(o, dict) else o}")

    boot = None
    bp = root / BOOT
    if bp.is_file():
        try:
            boot = yaml.load(bp.read_text(encoding="utf-8"), Loader=Strict)
        except Exception as exc:  # noqa: BLE001
            findings.append(f"boot_parse:{type(exc).__name__}")
    else:
        findings.append("missing_boot_manifest")

    reg = None
    rp = root / REGISTRY
    if rp.is_file():
        try:
            reg = yaml.load(rp.read_text(encoding="utf-8"), Loader=Strict)
        except Exception as exc:  # noqa: BLE001
            findings.append(f"registry_parse:{type(exc).__name__}")
    else:
        findings.append("missing_registry")

    versions = {
        "contract": (contract or {}).get("mechanism_version"),
        "boot": (boot or {}).get("mechanism_version"),
        "registry": (reg or {}).get("mechanism_version"),
    }
    if len({v for v in versions.values()}) != 1 or None in versions.values():
        findings.append(f"version_mismatch:{versions}")

    if boot:
        for item in boot.get("load_order", []) or []:
            rel = item.get("path") if isinstance(item, dict) else item
            if not rel or not (root / str(rel)).exists():
                findings.append(f"broken_pointer:{rel}")

    if findings:
        for f in findings:
            print(f"FAIL {f}")
        return 1
    print("validation_passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
