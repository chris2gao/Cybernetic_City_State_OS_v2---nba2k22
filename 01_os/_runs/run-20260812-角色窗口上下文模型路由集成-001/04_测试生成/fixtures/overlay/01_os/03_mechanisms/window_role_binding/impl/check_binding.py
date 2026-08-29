#!/usr/bin/env python3
"""Reference composition validator for the Stage 04 good-tree overlay.

THIS IS A TEST FIXTURE, NOT THE MECHANISM. It exists to prove that the frozen
Stage 04 checks are satisfiable by *some* implementation, and that the
validator-probe checks (RW-T37..RW-T42) are not vacuous. Stage 05/06 writes the
real validator under whatever canonical name it chooses; this file is never
loaded by the repository.

Usage: check_binding.py [static] <tree_root>     exit 0 pass, non-zero fail.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("environment_error: PyYAML is required", file=sys.stderr)
    raise SystemExit(2)

MECH = "window_role_binding"
MECH_DIR = f"01_os/03_mechanisms/{MECH}"
BOOT = f"01_os/02_boot/{MECH}/boot_v1.yml"

# ST04-IR-005: a composition validator is allowed — and by A10 encouraged — to
# resolve the existing mechanisms it references instead of restating them. This
# fixture deliberately does so, which is what makes the RW-T37..T42 probes
# actually exercise the dependency-closure staging.
MODEL_ROUTING_CONTRACT = "01_os/03_mechanisms/model_routing/路由契约_v1.yml"

AUTHORITY_DENY = re.compile(
    r"publish|filesystem|file_write|secret|credential|master_write|human_gate|"
    r"destructive|source_write|authorized",
    re.I,
)


class DuplicateKeyError(Exception):
    pass


class StrictLoader(yaml.SafeLoader):
    pass


def _no_dup(loader, node, deep=False):
    out = {}
    for k_node, v_node in node.value:
        k = loader.construct_object(k_node, deep=deep)
        if k in out:
            raise DuplicateKeyError(f"duplicate key: {k!r}")
        out[k] = loader.construct_object(v_node, deep=deep)
    return out


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_dup)


def load(p: Path):
    return yaml.load(p.read_text(encoding="utf-8"), Loader=StrictLoader)


def flatten(node, path=""):
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            kp = f"{path}.{k}" if path else str(k)
            out.extend(flatten(v, kp)) if isinstance(v, (dict, list)) else out.append((kp, v))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            kp = f"{path}[{i}]"
            out.extend(flatten(v, kp)) if isinstance(v, (dict, list)) else out.append((kp, v))
    else:
        out.append((path, node))
    return out


ROLE_WORDS = ("foreground", "backend", "review", "research", "refin")


def _kinds(doc) -> set:
    """Classify a document by content, not by its schema_version wording.

    ST04-IR-003: naming is an implementation choice, so this fixture validator
    must not recognise its own documents by an exact token either. Otherwise the
    alternate-schema-name conforming variant would fail here rather than in the
    thing it is meant to exercise.
    """
    if not isinstance(doc, dict):
        return set()
    got = set()
    entries = {}
    for _, v in doc.items():
        if isinstance(v, dict):
            cand = {k: x for k, x in v.items() if isinstance(x, dict)}
            if len(cand) > len(entries):
                entries = cand
    if len(entries) >= 5:
        hit = sum(1 for k in entries if any(w in str(k).lower() for w in ROLE_WORDS))
        if hit >= 4:
            got.add("role")
    blob = " ".join(f"{k}={v}" for k, v in flatten(doc)).lower()
    if re.search(r"window[_ ]?id", blob) and "fresh" in blob and re.search(r"re[_\-]?entry", blob):
        got.add("window")
    for kp, _ in flatten(doc):
        if re.search(r"handoff|交接", kp, re.I) and re.search(r"required|must_carry", kp, re.I):
            got.add("handoff")
            break
    return got


def doc_by_kind(root: Path, kind: str):
    d = root / MECH_DIR
    if not d.is_dir():
        return None, None
    for p in sorted(d.rglob("*.yml")):
        try:
            doc = load(p)
        except Exception as exc:  # noqa: BLE001
            raise SystemExit(f"unparseable {p}: {type(exc).__name__}: {exc}")
        if kind in _kinds(doc):
            return p, doc
    return None, None


def main() -> int:
    argv = [a for a in sys.argv[1:] if a != "static"]
    if not argv:
        print("usage: check_binding.py [static] <tree_root>", file=sys.stderr)
        return 2
    root = Path(argv[0]).resolve()
    problems: list[str] = []

    # 1. declared pointers resolve
    boot_p = root / BOOT
    if not boot_p.is_file():
        print(f"FAIL boot manifest missing: {BOOT}")
        return 1
    try:
        boot = load(boot_p)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL unparseable boot manifest: {type(exc).__name__}: {exc}")
        return 1
    for item in boot.get("load_order") or []:
        p = item.get("path") if isinstance(item, dict) else item
        if not isinstance(p, str) or not (root / p).exists():
            problems.append(f"broken load_order pointer: {p!r}")
    for key in ("validator", "registry"):
        v = boot.get(key)
        if not isinstance(v, str) or not (root / v).exists():
            problems.append(f"broken {key} pointer: {v!r}")

    # 1b. cross-mechanism dependency actually resolved and read
    dep = root / MODEL_ROUTING_CONTRACT
    if not dep.is_file():
        problems.append(f"declared cross-mechanism dependency missing: {MODEL_ROUTING_CONTRACT}")
    else:
        try:
            depdoc = load(dep)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"unparseable {MODEL_ROUTING_CONTRACT}: {type(exc).__name__}")
            depdoc = {}
        const = ((depdoc or {}).get("outputs") or {}).get("authority_constant")
        if const != "routing_only":
            problems.append(f"model_routing authority constant is {const!r}, expected routing_only")

    # 2. contracts parse
    try:
        _, roles_doc = doc_by_kind(root, "role")
        _, win_doc = doc_by_kind(root, "window")
        _, hand_doc = doc_by_kind(root, "handoff")
    except SystemExit as exc:
        print(f"FAIL {exc}")
        return 1
    for name, doc in (("role", roles_doc), ("window", win_doc), ("handoff", hand_doc)):
        if not isinstance(doc, dict):
            problems.append(f"{name} contract not discoverable")
    if problems:
        for p in problems:
            print(f"FAIL {p}")
        return 1

    # 3. role contract
    roles = {}
    for _, v in roles_doc.items():
        if isinstance(v, dict):
            cand = {k: x for k, x in v.items() if isinstance(x, dict)}
            if len(cand) > len(roles):
                roles = cand
    if len(roles) < 5:
        problems.append(f"role contract exposes {len(roles)} roles, need >= 5")
    if str(roles_doc.get("authority_effect", "")).strip().lower() != "none":
        problems.append("role contract does not declare authority_effect: none")
    for rid, body in roles.items():
        for kp, val in flatten(body):
            leaf = kp.split(".")[-1].split("[")[0]
            if AUTHORITY_DENY.search(leaf) and val is True:
                problems.append(f"role {rid} grants authority via {kp}={val!r}")

    # 4. window contract
    ident = win_doc.get("window_identity")
    if not isinstance(ident, dict):
        problems.append("window contract declares no window_identity block")
    else:
        uniq = ident.get("uniqueness")
        if not isinstance(uniq, str) or "unique" not in uniq.lower():
            problems.append(f"window identity uniqueness is not declared: {uniq!r}")
        if not ident.get("window_id_field"):
            problems.append("window identity declares no window_id field")
    modes = win_doc.get("entry_modes")
    if isinstance(modes, list):
        # a list of mode records is the same declaration as a mapping
        norm = {}
        for item in modes:
            if isinstance(item, dict):
                mid = next(
                    (str(item[k]) for k in ("mode_id", "entry_mode", "mode", "id", "name")
                     if isinstance(item.get(k), str)),
                    None,
                )
                if mid:
                    norm[mid] = {k: v for k, v in item.items()
                                 if k not in ("mode_id", "entry_mode", "mode", "id", "name")}
        modes = norm
    if not isinstance(modes, dict) or not modes:
        problems.append("window contract declares no entry_modes")
    else:
        # ST04-IR-002: A02 mandates fresh versus reentry. A third successor mode
        # is optional, so its absence or a different name is not a defect.
        if not any(str(k) == "fresh" for k in modes):
            problems.append("entry mode missing: fresh")
        re_key = next((k for k in modes if re.search(r"re[_\-]?entry", str(k), re.I)), None)
        if re_key is None:
            problems.append("entry mode missing: reentry")
        re_ = (modes.get(re_key) if re_key else None) or {}
        req = [str(x) for x in (re_.get("required_fields") or [])]
        if not any("predecessor" in x for x in req):
            problems.append(f"reentry does not require a predecessor window id: {req}")
    blob = " ".join(f"{k}={v}" for k, v in flatten(win_doc)).lower()
    for kp, val in flatten(win_doc):
        leaf = kp.split(".")[-1].split("[")[0]
        if re.search(r"required_fields|bound_facts|window_id_field", leaf) and isinstance(val, str):
            if re.search(r"latest|most[_\- ]recent", val, re.I):
                problems.append(f"latest-session used as a formal identity field: {kp}={val!r}")
    route = ((win_doc.get("model_route_binding") or {}).get("route_receipt")) or {}
    if not route.get("required_fields"):
        problems.append("no model-routing receipt is bound to the window")
    elif str(route.get("authority_constant", "")).strip() != "routing_only":
        problems.append(f"route authority is not routing_only: {route.get('authority_constant')!r}")
    if "stale" not in blob:
        problems.append("window contract declares no stale semantics")

    # 5. handoff contract
    rec = hand_doc.get("handoff_record") or {}
    if not rec.get("required_fields"):
        problems.append("handoff contract declares no required fields")
    raw = rec.get("prohibited_fields") or []
    if isinstance(raw, dict):
        prohibited = {str(k) for k, v in raw.items() if v is True}
    else:
        prohibited = {str(x) for x in raw}
    # `<field>_disabled: true` and friends declare the same prohibition
    for k, v in rec.items():
        m = re.search(r"_(prohibited|forbidden|disallowed|disabled|banned)$", str(k), re.I)
        if m and v is True:
            prohibited.add(str(k)[: m.start()])
    if "private_chain_of_thought" not in prohibited:
        problems.append("handoff does not prohibit a private chain-of-thought field")

    # 6. every role reference resolves
    known = set(roles)
    for doc in (win_doc, hand_doc, roles_doc):
        for kp, val in flatten(doc):
            leaf = kp.split(".")[-1].split("[")[0]
            if leaf in ("role_id", "role") or leaf.endswith(("_role", "_roles")):
                if isinstance(val, str) and val and val not in known:
                    problems.append(f"unknown role reference {kp}={val!r}")

    if problems:
        for p in problems:
            print(f"FAIL {p}")
        print(f"composition: {len(problems)} problem(s)")
        return 1
    print("composition: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
