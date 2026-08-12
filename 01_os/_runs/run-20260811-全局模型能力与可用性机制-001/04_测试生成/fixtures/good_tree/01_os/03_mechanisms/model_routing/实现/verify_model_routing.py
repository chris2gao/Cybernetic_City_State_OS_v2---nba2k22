#!/usr/bin/env python3
"""Fixture mechanism validator (Stage 04 positive fixture, not canonical).

Exists so the frozen tests can prove that a mechanism's *own* validator fails
closed on the B13 defect classes. Stage 05/06 must supply a real one; this one
implements exactly the fail-closed obligations the frozen tests assert, and
nothing more.

B13 obligations implemented here:
  1. strict YAML / duplicate keys
  2. source and freshness fields on registered entries
  3. every source token used anywhere in the catalog resolves in the catalog's
     own reachable source-resolution index, for registered AND unregistered
     entries
  4. registry path existence and registry coverage of the mechanism surface
  5. mechanism_version agreement and catalog_version cross-binding
  6. illegal cost/token/quota fields in routing-semantic positions
  7. declared pointer resolution (load_order, validator, registry)

usage: verify_model_routing.py static <tree_root>
exit 0 pass, non-zero fail.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

MECH = "01_os/03_mechanisms/model_routing"
BOOT = "01_os/02_boot/model_routing/启动清单_v1.yml"
REGISTRY = "01_os/05_registry/model_routing_v1.yml"
LOADER = "01_os/06_execution/boot/model_routing"
FRESHNESS = ("source_refs", "verified_at", "invalidation_conditions", "confidence")
SOURCE_INDEX_KEYS = ("sources", "source_registry", "source_index", "来源")
SOURCE_LOCATORS = ("url", "ref", "path")

# Economic optimization semantics. Citation metadata is not routing logic, so the
# scan is positional: the exempt subtrees below are evidence, not decision inputs.
ECONOMIC_RE = re.compile(
    r"(price|pricing|cost|quota|budget|balance|billing|cheapest|"
    r"minimize_token|token_spend)",
    re.IGNORECASE,
)
EXEMPT_KEYS = {
    "sources", "source_registry", "source_index", "来源",
    "source_refs", "surface_exposure_evidence", "evidence_refs",
    "prohibited_routing_inputs", "invalidation_conditions",
}
NEGATION_RE = re.compile(r"(prohibit|forbidden|not_used|never|no_|false)", re.IGNORECASE)


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


def load(p: Path):
    return yaml.load(p.read_text(encoding="utf-8"), Loader=Strict)


def walk_files(root: Path):
    if root.is_dir():
        for p in sorted(root.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                yield p


def expand_path_set(pattern: str) -> list[str]:
    m = re.search(r"\{([^}]*)\}", pattern)
    if not m:
        return [pattern] if pattern else []
    out = []
    for part in m.group(1).split(","):
        out.extend(expand_path_set(pattern[: m.start()] + part.strip() + pattern[m.end():]))
    return out


def path_matches(pattern: str, rel: str) -> bool:
    if pattern.endswith("**"):
        return rel.startswith(pattern[:-2])
    return rel == pattern


def economic_hits(node, path="", findings=None):
    """Flag economic tokens only outside evidence/citation subtrees."""
    if findings is None:
        findings = []
    if isinstance(node, dict):
        for k, v in node.items():
            if str(k) in EXEMPT_KEYS:
                continue
            # `something_quota_probe: false` is a prohibition declaration, not a
            # routing input. A boolean false disables the field by definition.
            if v is False:
                continue
            if ECONOMIC_RE.search(str(k)) and not NEGATION_RE.search(str(k)):
                findings.append(f"economic_routing_field:{path}{k}")
            economic_hits(v, f"{path}{k}.", findings)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            economic_hits(v, f"{path}[{i}].", findings)
    elif isinstance(node, str):
        m = ECONOMIC_RE.search(node)
        if m and not NEGATION_RE.search(node):
            findings.append(f"economic_routing_value:{path}{m.group(0)}")
    return findings


def collect_source_index(root: Path, docs: dict, boot) -> dict:
    """Source-resolution index reachable from the declared load surface."""
    index: dict = {}
    reachable = list(docs.values())
    if isinstance(boot, dict):
        reachable.append(boot)
        for key, val in boot.items():
            if str(key).endswith("_ref") and isinstance(val, str):
                p = root / val
                if p.is_file() and p.suffix.lower() in (".yml", ".yaml"):
                    try:
                        reachable.append(load(p))
                    except Exception:  # noqa: BLE001
                        pass
    for doc in reachable:
        if not isinstance(doc, dict):
            continue
        for key in SOURCE_INDEX_KEYS:
            block = doc.get(key)
            if isinstance(block, dict):
                index.update(block)
    return index


def catalog_tokens(catalog: dict) -> set:
    tokens = set()
    for e in catalog.get("entries", []) or []:
        if not isinstance(e, dict):
            continue
        for t in e.get("source_refs") or []:
            tokens.add(str(t))
        for pr in e.get("parameter_profiles") or []:
            if isinstance(pr, dict):
                ev = pr.get("surface_exposure_evidence")
                for t in ev if isinstance(ev, list) else ([ev] if ev else []):
                    tokens.add(str(t))
    return tokens


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] != "static":
        print("usage: verify_model_routing.py static <tree_root>", file=sys.stderr)
        return 2
    root = Path(sys.argv[2]).resolve()
    findings: list[str] = []

    docs = {}
    for p in sorted((root / MECH).rglob("*.yml")):
        try:
            docs[p] = load(p)
        except DupKey as exc:
            findings.append(f"duplicate_key:{p.name}:{exc}")
        except Exception as exc:  # noqa: BLE001
            findings.append(f"parse_error:{p.name}:{type(exc).__name__}")

    def by_token(tok):
        for d in docs.values():
            if isinstance(d, dict) and str(d.get("schema_version", "")).startswith(tok):
                return d
        return None

    contract = by_token("citystate.model_routing.contract.v")
    catalog = by_token("citystate.model_routing.catalog.v")
    ledger = by_token("citystate.model_routing.project_observation.v")
    for name, doc in (("contract", contract), ("catalog", catalog), ("ledger", ledger)):
        if doc is None:
            findings.append(f"missing_document:{name}")

    boot = None
    bp = root / BOOT
    if bp.is_file():
        try:
            boot = load(bp)
        except Exception as exc:  # noqa: BLE001
            findings.append(f"boot_parse:{type(exc).__name__}")
    else:
        findings.append("missing_boot_manifest")

    reg = None
    rp = root / REGISTRY
    if rp.is_file():
        try:
            reg = load(rp)
        except Exception as exc:  # noqa: BLE001
            findings.append(f"registry_parse:{type(exc).__name__}")
    else:
        findings.append("missing_registry")

    # 2 + 3: freshness, and source resolution for registered AND unregistered
    if isinstance(catalog, dict):
        index = collect_source_index(root, docs, boot)
        if not index:
            findings.append("no_source_resolution_index_reachable_from_load_surface")
        for tok in sorted(catalog_tokens(catalog)):
            entry = index.get(tok)
            if not isinstance(entry, dict):
                findings.append(f"unresolvable_source_ref:{tok}")
                continue
            if not str(entry.get("kind", "")).strip():
                findings.append(f"source_without_kind:{tok}")
            if not any(str(entry.get(k, "")).strip() for k in SOURCE_LOCATORS):
                findings.append(f"source_without_locator:{tok}")
        for e in catalog.get("entries", []) or []:
            if not isinstance(e, dict):
                findings.append("malformed_entry")
                continue
            label = f"{e.get('surface_id')}::{e.get('model_label')}"
            if not e.get("source_refs"):
                findings.append(f"entry_without_source_refs:{label}")
            if e.get("registered") is not True:
                continue
            for f in FRESHNESS:
                val = e.get(f)
                if val is None or (isinstance(val, (list, str, dict)) and len(val) == 0):
                    findings.append(f"missing_freshness:{label}:{f}")

    if isinstance(ledger, dict):
        for o in ledger.get("observations", []) or []:
            if not isinstance(o, dict) or o.get("validity") not in {
                "formal",
                "diagnostic",
                "anecdotal",
            }:
                findings.append(
                    f"bad_validity:{o.get('observation_id') if isinstance(o, dict) else o}"
                )

    # 5: version agreement and catalog_version cross-binding
    versions = {
        "contract": (contract or {}).get("mechanism_version"),
        "boot": (boot or {}).get("mechanism_version"),
        "registry": (reg or {}).get("mechanism_version"),
    }
    if len(set(versions.values())) != 1 or None in versions.values():
        findings.append(f"version_mismatch:{versions}")
    boot_cv = (boot or {}).get("catalog_version")
    cat_cv = (catalog or {}).get("catalog_version")
    if boot_cv is None or cat_cv is None:
        findings.append(f"catalog_version_unbound:boot={boot_cv} catalog={cat_cv}")
    elif boot_cv != cat_cv:
        findings.append(f"catalog_version_drift:boot={boot_cv} catalog={cat_cv}")

    # 7: declared pointers must resolve
    if isinstance(boot, dict):
        for item in boot.get("load_order", []) or []:
            rel = item.get("path") if isinstance(item, dict) else item
            if not rel or not (root / str(rel)).exists():
                findings.append(f"broken_pointer:load_order:{rel}")
        for key in ("validator", "registry"):
            rel = boot.get(key)
            if not rel or not (root / str(rel)).exists():
                findings.append(f"broken_pointer:{key}:{rel}")
    if not (root / LOADER).is_dir():
        findings.append(f"broken_pointer:loader_dir:{LOADER}")

    # 4: registry path existence and coverage of the mechanism surface
    if isinstance(reg, dict):
        patterns: list[str] = []
        for e in reg.get("entries", []) or []:
            if not isinstance(e, dict):
                findings.append("malformed_registry_entry")
                continue
            for pat in expand_path_set(str(e.get("path", ""))):
                patterns.append(pat)
                base = root / pat[:-2].rstrip("/") if pat.endswith("**") else root / pat
                if pat.endswith("**"):
                    if not base.is_dir() or not any(walk_files(base)):
                        findings.append(f"registry_path_missing:{pat}")
                elif not base.exists():
                    findings.append(f"registry_path_missing:{pat}")
        for surface in (MECH, LOADER, str(Path(BOOT).parent).replace("\\", "/")):
            for p in walk_files(root / surface):
                rel = p.relative_to(root).as_posix()
                if not any(path_matches(pat, rel) for pat in patterns):
                    findings.append(f"registry_coverage_gap:{rel}")

    # 6: illegal economic routing fields in routing-semantic positions
    for name, doc in (("contract", contract), ("catalog", catalog), ("ledger", ledger)):
        if isinstance(doc, dict):
            for hit in economic_hits(doc, f"{name}."):
                findings.append(hit)

    if findings:
        for f in sorted(set(findings)):
            print(f"FAIL {f}")
        return 1
    print("validation_passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
