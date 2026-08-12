#!/usr/bin/env python3
"""Stage 07 fresh independent reviewer probes (v2).

Written from the mechanism declaration surface only. Deliberately imports
nothing from the Stage 04 acceptance harness or the Stage 06 validator helpers:
only stdlib + pyyaml. Every check below is the reviewer's own measurement.

Usage:
  python reviewer_probes_v2.py <repo_root> <run_root> [--json out.json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

MECH = "01_os/03_mechanisms/model_routing"
BOOT = "01_os/02_boot/model_routing/启动清单_v1.yml"
REG = "01_os/05_registry/model_routing_v1.yml"
LOADER = "01_os/06_execution/boot/model_routing"
VALIDATOR = f"{MECH}/实现/verify_model_routing.py"
CATALOG = f"{MECH}/模型与产品面目录_v1.yml"
CONTRACT = f"{MECH}/路由契约_v1.yml"
SRCIDX = f"{MECH}/来源索引_v1.yml"
LEDGER = f"{MECH}/项目观察证据_v1.yml"

EXPECTED_DIGEST = "848b691712166a968c821ad6e53cafaf477b86bf7b1d7773306ad4e6ebf3e48c"
COPY_SUBTREES = [
    "01_os/02_boot/model_routing",
    "01_os/03_mechanisms/model_routing",
    "01_os/06_execution/boot/model_routing",
]


def rd(p: Path) -> Any:
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# Part 1 - frozen package digest, recomputed from the declared normalization
# --------------------------------------------------------------------------
def part_digest(run_root: Path) -> dict[str, Any]:
    tests_path = run_root / "04_测试生成/04_tests.yml"
    receipt_path = run_root / "04_测试生成/freeze_receipt_v3.yml"
    payload = rd(tests_path)
    receipt = rd(receipt_path)

    # the declared normalization is sha256 over payload.tests, so read it from
    # payload rather than assuming a top-level key
    tests = (payload.get("payload") or {}).get("tests")
    blob = yaml.safe_dump(tests, allow_unicode=True, sort_keys=True, width=4096)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()

    # locate the frozen-artifact block in the receipt without assuming its key path
    def find_key(node: Any, key: str) -> list[Any]:
        out = []
        if isinstance(node, dict):
            for k, v in node.items():
                if k == key:
                    out.append(v)
                out.extend(find_key(v, key))
        elif isinstance(node, list):
            for v in node:
                out.extend(find_key(v, key))
        return out

    ids = [t.get("id") for t in tests] if isinstance(tests, list) else []
    artifact_version = payload.get("artifact_version")
    return {
        "tests_file": str(tests_path.as_posix()),
        "artifact_version": artifact_version,
        "tests_file_sha256": sha_file(tests_path),
        "receipt_artifact_sha256": find_key(receipt, "artifact_sha256"),
        "receipt_test_package_sha256": find_key(receipt, "test_package_sha256"),
        "recomputed_test_package_sha256": digest,
        "expected_test_package_sha256": EXPECTED_DIGEST,
        "digest_match": digest == EXPECTED_DIGEST,
        "test_count": len(ids),
        "test_count_is_35": len(ids) == 35,
        "duplicate_test_ids": sorted(
            {i for i in ids if ids.count(i) > 1}
        ),
        "test_ids": ids,
    }


# --------------------------------------------------------------------------
# Part 2 - F2: source resolution audited from the declaration surface
# --------------------------------------------------------------------------
CLAIM_ID_RE = re.compile(r"^C\d{2}_")


def part_f2(repo: Path) -> dict[str, Any]:
    boot = rd(repo / BOOT)
    catalog = rd(repo / CATALOG)
    srcidx = rd(repo / SRCIDX)
    registry = rd(repo / REG)

    declared_load = []
    for item in boot.get("load_order") or []:
        declared_load.append(item.get("path") if isinstance(item, dict) else item)

    reachable = {
        "source_index_in_boot_load_order": SRCIDX in declared_load,
        "catalog_in_boot_load_order": CATALOG in declared_load,
        "contract_in_boot_load_order": CONTRACT in declared_load,
        "ledger_in_boot_load_order": LEDGER in declared_load,
        "boot_validator_pointer": boot.get("validator"),
        "boot_validator_is_canonical": boot.get("validator") == VALIDATOR,
        "boot_registry_pointer": boot.get("registry"),
        "boot_registry_is_canonical": boot.get("registry") == REG,
        "catalog_source_index_ref": catalog.get("source_index_ref"),
        "catalog_points_at_source_index": catalog.get("source_index_ref") == SRCIDX,
        "all_boot_load_paths_exist": all((repo / p).is_file() for p in declared_load),
        "registry_ids_mechanism_root": any(
            str(e.get("path", "")).startswith(MECH) for e in registry.get("entries") or []
        ),
    }

    sources = srcidx.get("sources") or {}
    tokens: dict[str, list[str]] = {}
    for entry in catalog.get("entries") or []:
        ident = f"{entry.get('surface_id')}::{entry.get('model_label')}"
        for t in entry.get("source_refs") or []:
            tokens.setdefault(str(t), []).append(ident + "#source_refs")
        for prof in entry.get("parameter_profiles") or []:
            if not isinstance(prof, dict):
                continue
            ev = prof.get("surface_exposure_evidence")
            ev = ev if isinstance(ev, list) else ([ev] if ev else [])
            for t in ev:
                tokens.setdefault(str(t), []).append(
                    ident + "#" + str(prof.get("profile_id")) + ".surface_exposure_evidence"
                )

    unresolved = sorted(t for t in tokens if t not in sources)
    claim_shaped = sorted(t for t in tokens if CLAIM_ID_RE.match(t))
    unused = sorted(set(sources) - set(tokens))

    locators = {}
    for sid, rec in sources.items():
        rec = rec or {}
        url, ref, path = rec.get("url"), rec.get("ref"), rec.get("path")
        kind = rec.get("kind")
        if url:
            ltype, lval = "url", str(url)
            durable = bool(re.match(r"^https?://[^\s]+\.[^\s]+", lval))
            detail = "http(s) absolute URL" if durable else "not an absolute http(s) URL"
        elif ref:
            lval = str(ref)
            ltype = "ref"
            m = re.search(r"sha256:([0-9a-f]{64})", lval)
            durable = bool(m)
            detail = "content-addressed sha256 ref" if durable else "opaque ref, not content-addressed"
        elif path:
            ltype, lval = "path", str(path)
            durable = (repo / lval).exists()
            detail = "in-repo path exists" if durable else "in-repo path MISSING"
        else:
            ltype, lval, durable, detail = "none", "", False, "no locator"
        locators[sid] = {
            "kind": kind,
            "locator_type": ltype,
            "locator": lval,
            "durable": durable,
            "detail": detail,
            "used_by": sorted(set(tokens.get(sid, []))),
        }

    # a Stage02 claim id must never appear as a source identity anywhere
    catalog_text = (repo / CATALOG).read_text(encoding="utf-8")
    srcidx_text = (repo / SRCIDX).read_text(encoding="utf-8")
    claim_leak = sorted(
        set(re.findall(r"\bC\d{2}_[A-Za-z0-9_]+", catalog_text + srcidx_text))
    )

    ag_pricing = sources.get("GOOGLE_AG_PRICING") or {}
    return {
        "declaration_surface_reachability": reachable,
        "token_count": len(tokens),
        "unresolved_tokens": unresolved,
        "claim_id_shaped_tokens": claim_shaped,
        "claim_id_strings_present_in_catalog_or_index": claim_leak,
        "unused_source_ids": unused,
        "GOOGLE_AG_PRICING_present": bool(ag_pricing),
        "GOOGLE_AG_PRICING_record": ag_pricing,
        "GOOGLE_AG_PRICING_used_by": sorted(set(tokens.get("GOOGLE_AG_PRICING", []))),
        "locators": locators,
        "non_durable_locators": sorted(
            sid for sid, v in locators.items() if not v["durable"]
        ),
    }


# --------------------------------------------------------------------------
# Part 3 - F3: reviewer's own mutation probes against the canonical validator
# --------------------------------------------------------------------------
def make_tree(repo: Path, dest: Path) -> None:
    for sub in COPY_SUBTREES:
        shutil.copytree(repo / sub, dest / sub, dirs_exist_ok=True)
    (dest / "01_os/05_registry").mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo / REG, dest / REG)


def run_validator(tree: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(tree / VALIDATOR), "static", str(tree)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    msg = (proc.stderr or proc.stdout or "").strip().splitlines()
    return proc.returncode, (msg[-1] if msg else "")


def edit_yaml(tree: Path, rel: str, fn) -> None:
    p = tree / rel
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    fn(doc)
    p.write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=4096),
        encoding="utf-8",
    )


def edit_text(tree: Path, rel: str, old: str, new: str) -> None:
    p = tree / rel
    t = p.read_text(encoding="utf-8")
    if old not in t:
        raise RuntimeError(f"probe_anchor_missing:{rel}:{old[:40]}")
    p.write_text(t.replace(old, new, 1), encoding="utf-8")


def _first_registered(doc):
    for e in doc["entries"]:
        if e.get("registered") is True:
            return e
    raise RuntimeError("no registered entry")


def _unregistered(doc):
    for e in doc["entries"]:
        if e.get("registered") is False:
            return e
    raise RuntimeError("no unregistered entry")


PROBES: list[tuple[str, str, str, Any]] = [
    # (id, dispatch_defect_class, description, mutation callable)
    ("R00", "control", "unmutated copy of the canonical tree must pass", None),
    (
        "R01", "1_registered_bogus_source_ref",
        "registered entry gains an unresolvable source_ref",
        lambda t: edit_yaml(t, CATALOG, lambda d: _first_registered(d)["source_refs"].append("REVIEWER_BOGUS_SRC")),
    ),
    (
        "R02", "2_unregistered_bogus_source_ref",
        "unregistered discovered entry gains an unresolvable source_ref",
        lambda t: edit_yaml(t, CATALOG, lambda d: _unregistered(d)["source_refs"].append("REVIEWER_BOGUS_SRC")),
    ),
    (
        "R02b", "2_unregistered_bogus_surface_evidence",
        "unregistered entry gains a profile whose surface_exposure_evidence is unresolvable",
        lambda t: edit_yaml(t, CATALOG, lambda d: _unregistered(d)["parameter_profiles"].append(
            {"profile_id": "reviewer_probe", "surface_exposure_evidence": ["REVIEWER_BOGUS_SRC"]})),
    ),
    (
        "R03", "3_registry_path_missing_object",
        "registry entry points at a nonexistent object",
        lambda t: edit_yaml(t, REG, lambda d: d["entries"][3].__setitem__(
            "path", "01_os/05_registry/model_routing_reviewer_absent_v9.yml")),
    ),
    (
        "R04", "4_registry_coverage_deleted",
        "registry entry covering the mechanism root is removed",
        lambda t: edit_yaml(t, REG, lambda d: d.__setitem__(
            "entries", [e for e in d["entries"] if not str(e.get("path", "")).startswith(MECH)])),
    ),
    (
        "R05a", "5_version_drift_catalog",
        "boot catalog_version drifts from the catalog",
        lambda t: edit_yaml(t, BOOT, lambda d: d.__setitem__("catalog_version", 2)),
    ),
    (
        "R05b", "5_version_drift_source_index",
        "boot source_index_version drifts from the source index",
        lambda t: edit_yaml(t, BOOT, lambda d: d.__setitem__("source_index_version", 7)),
    ),
    (
        "R05c", "5_version_drift_mechanism",
        "catalog mechanism_version drifts from the rest of the mechanism",
        lambda t: edit_yaml(t, CATALOG, lambda d: d.__setitem__("mechanism_version", 2)),
    ),
    (
        "R06a", "6_economic_routing_field_contract_input",
        "price_weight added to the routing contract inputs",
        lambda t: edit_yaml(t, CONTRACT, lambda d: d["inputs"].__setitem__("price_weight", "0.4")),
    ),
    (
        "R06b", "6_economic_routing_field_decision_step",
        "quota_balance added to the routing contract decision steps",
        lambda t: edit_yaml(t, CONTRACT, lambda d: d["decision_steps"].insert(0, "score_by_quota_balance")),
    ),
    (
        "R06c", "6_economic_routing_field_output",
        "cheapest-first preference added to routing contract outputs",
        lambda t: edit_yaml(t, CONTRACT, lambda d: d["outputs"]["required"].append("cheapest_available_model")),
    ),
    (
        "R07", "7_boot_load_order_pointer_break",
        "a required boot load_order pointer is broken",
        lambda t: edit_yaml(t, BOOT, lambda d: d["load_order"][2].__setitem__(
            "path", "01_os/03_mechanisms/model_routing/不存在的目录_v9.yml")),
    ),
    (
        "R08a", "8_boot_validator_pointer_break",
        "boot validator pointer no longer resolves",
        lambda t: edit_yaml(t, BOOT, lambda d: d.__setitem__(
            "validator", "01_os/03_mechanisms/model_routing/实现/absent_validator.py")),
    ),
    (
        "R08b", "8_catalog_source_index_pointer_break",
        "catalog source_index_ref no longer resolves to the canonical index",
        lambda t: edit_yaml(t, CATALOG, lambda d: d.__setitem__(
            "source_index_ref", "01_os/03_mechanisms/model_routing/来源索引_v9.yml")),
    ),
    (
        "R08c", "8_boot_registry_pointer_break",
        "boot registry pointer no longer resolves",
        lambda t: edit_yaml(t, BOOT, lambda d: d.__setitem__(
            "registry", "01_os/05_registry/model_routing_v9.yml")),
    ),
    # ---- residual-strength probes (informational, not in the 8 required classes)
    (
        "X01", "residual_source_locator_strength",
        "a used source keeps kind but its only locator is a nonexistent in-repo path",
        lambda t: edit_yaml(t, SRCIDX, lambda d: d["sources"].__setitem__(
            "GOOGLE_AG_MODELS", {"kind": "provider_first_party", "title": "x",
                                 "path": "01_os/03_mechanisms/model_routing/绝不存在_v9.yml",
                                 "verified_at": "2026-08-11"})),
    ),
    (
        "X02", "residual_economic_field_in_catalog",
        "price_weight added to a catalog entry rather than to the routing contract",
        lambda t: edit_yaml(t, CATALOG, lambda d: _first_registered(d).__setitem__("price_weight", 0.4)),
    ),
    (
        "X03", "residual_overbroad_registry_wildcard",
        "every registry entry collapsed into a single 01_os/** wildcard",
        lambda t: edit_yaml(t, REG, lambda d: d.__setitem__("entries", [
            {**d["entries"][0], "path": "01_os/**"}])),
    ),
    (
        "X04", "residual_ledger_formal_upgrade",
        "an antigravity diagnostic observation is silently upgraded to formal",
        lambda t: edit_yaml(t, LEDGER, lambda d: d["observations"][0].__setitem__("validity", "formal")),
    ),
    (
        "X05", "residual_unregistered_to_registered_without_evidence",
        "the discovered Opus 4.8 candidate is flipped to registered with no new evidence",
        lambda t: edit_yaml(t, CATALOG, lambda d: _unregistered(d).update({"registered": True})),
    ),
    (
        "X06", "residual_opus48_rebound_to_antigravity",
        "the discovered Opus 4.8 candidate is moved back onto antigravity",
        lambda t: edit_text(t, CATALOG,
                            "    surface_id: claude_code_desktop\n    model_label: Claude Opus 4.8",
                            "    surface_id: antigravity\n    model_label: Claude Opus 4.8"),
    ),
]


def part_f3(repo: Path, workdir: Path) -> list[dict[str, Any]]:
    results = []
    for pid, cls, desc, fn in PROBES:
        tree = workdir / pid
        tree.mkdir(parents=True, exist_ok=True)
        make_tree(repo, tree)
        error = None
        if fn is not None:
            try:
                fn(tree)
            except Exception as exc:  # probe construction failure is itself a finding
                error = f"{type(exc).__name__}:{exc}"
        if error:
            results.append({"probe": pid, "defect_class": cls, "description": desc,
                            "probe_error": error, "exit_code": None, "verdict": "PROBE_ERROR"})
            continue
        code, msg = run_validator(tree)
        if pid == "R00":
            verdict = "OK_CONTROL_GREEN" if code == 0 else "CONTROL_FAILED"
        elif pid.startswith("X"):
            verdict = "CAUGHT" if code != 0 else "NOT_CAUGHT"
        else:
            verdict = "FAIL_CLOSED" if code != 0 else "FALSE_GREEN"
        results.append({
            "probe": pid, "defect_class": cls, "description": desc,
            "exit_code": code, "validator_message": msg, "verdict": verdict,
        })
        shutil.rmtree(tree, ignore_errors=True)
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root", type=Path)
    ap.add_argument("run_root", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    run_root = args.run_root.resolve()

    report: dict[str, Any] = {
        "reviewer": "stage07_fresh_final_independent_reviewer",
        "harness": "reviewer_probes_v2.py (stdlib + pyyaml only; no Stage04/Stage06 helper imports)",
        "python": sys.version.split()[0],
        "repo_root": str(repo),
    }
    report["frozen_package"] = part_digest(run_root)
    report["f2_source_resolution"] = part_f2(repo)
    with tempfile.TemporaryDirectory(prefix="s07probe_") as tmp:
        report["f3_probes"] = part_f3(repo, Path(tmp))

    if args.json:
        args.json.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    d = report["frozen_package"]
    print(f"digest_match={d['digest_match']} count={d['test_count']} recomputed={d['recomputed_test_package_sha256']}")
    f2 = report["f2_source_resolution"]
    print(f"f2 tokens={f2['token_count']} unresolved={f2['unresolved_tokens']} "
          f"claim_shaped={f2['claim_id_shaped_tokens']} non_durable={f2['non_durable_locators']} "
          f"unused={f2['unused_source_ids']} ag_pricing_used={len(f2['GOOGLE_AG_PRICING_used_by'])}")
    for r in report["f3_probes"]:
        print(f"{r['probe']:<5} {r['verdict']:<18} exit={r.get('exit_code')} "
              f"{r.get('validator_message','')[:70]}")
    bad = [r for r in report["f3_probes"]
           if r["verdict"] in {"FALSE_GREEN", "CONTROL_FAILED", "PROBE_ERROR"}]
    print(f"required_class_failures={len(bad)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
