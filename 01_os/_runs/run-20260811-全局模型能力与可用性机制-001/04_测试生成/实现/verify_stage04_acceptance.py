#!/usr/bin/env python3
"""Stage 04 independent acceptance validator.

task_id: os-v2-global-model-capability-and-availability-routing-001
run_id:  run-20260811-全局模型能力与可用性机制-001

Three commands, all independently runnable:

  package <run_root>      validate 04_tests.yml against the Stage 04 frozen-test
                          schema and against its own traceability rules.
  acceptance <tree_root>  run the 28 frozen acceptance checks against a tree.
                          `tree_root` may be the repository root or a fixture tree.
  selftest [<repo_root>]  positive: good fixture must be all green.
                          negative: each declared mutation must turn its target
                          check red and must not silently fix another.
                          boundary: declared boundary probes.

Exit codes: 0 pass, 1 fail, 2 usage/environment error.

This program is written by the Stage 04 independent test designer. It does not
implement the mechanism and must not be edited by Stage 05/06 to accommodate an
implementation (01_os/01_workflow/04_测试生成/README.md, frozen-test rule).
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
from typing import Any, Callable

try:
    import yaml
except ImportError:  # pragma: no cover
    print("environment_error: PyYAML is required", file=sys.stderr)
    raise SystemExit(2)

# --------------------------------------------------------------------------
# frozen path and schema surface
#
# Filenames inside the mechanism directory are NOT frozen (dispatch: do not
# overfit filenames). What is frozen is: the mechanism directory, the three
# repository-convention pointer paths (boot manifest, registry, execution
# loader), and the schema_version tokens by which the mechanism documents are
# discovered.
# --------------------------------------------------------------------------

MECH_DIR = "01_os/03_mechanisms/model_routing"
BOOT_MANIFEST = "01_os/02_boot/model_routing/启动清单_v1.yml"
REGISTRY = "01_os/05_registry/model_routing_v1.yml"
LOADER_DIR = "01_os/06_execution/boot/model_routing"
ENTRY_SPEC = "01_os/开发入口与单窗口任务规范_v1.md"
WORKFLOW_DIR = "01_os/01_workflow"
PUBLISHER_AUTHORITY = "01_os/05_registry/repository_publisher_authority_v1.yml"

TOKEN_CONTRACT = "citystate.model_routing.contract.v"
TOKEN_CATALOG = "citystate.model_routing.catalog.v"
TOKEN_LEDGER = "citystate.model_routing.project_observation.v"

# Frozen at Stage 04 from the current task branch. MR-T20 asserts byte identity:
# Stage 05/06 is not authorized to modify publisher authority.
PUBLISHER_AUTHORITY_SHA256 = (
    "ae9abdf5d729550511de857511a73d36c53f5d52d76e9f57c77b23ad19c29c1a"
)

REQUIRED_INPUTS = {
    "task_id",
    "role",
    "risk_tier",
    "task_shape",
    "required_capabilities",
}
REQUIRED_OUTPUTS = {
    "provider",
    "surface",
    "model",
    "parameter_profile",
    "routing_basis",
    "evidence_refs",
    "limitations",
    "availability_assumption",
    "authority",
}
REQUIRED_SURFACES = {
    "chatgpt_web",
    "codex_desktop",
    "claude_code_desktop",
    "gemini_web",
    "antigravity",
}
FRESHNESS_FIELDS = ("source_refs", "verified_at", "invalidation_conditions", "confidence")
VALIDITY_VALUES = {"formal", "diagnostic", "anecdotal"}

# Pure prohibitions. On a tree containing nothing they are vacuously satisfied,
# which is the correct meaning of "must not contain". Their non-vacuity is proven
# by mutation kill (M21, M14, M26), not by the empty-tree probe.
VACUOUS_ON_EMPTY = {"MR-T02", "MR-T23", "MR-T25"}

COST_TOKEN_RE = re.compile(
    r"(price|pricing|cost_per|per_1m|token_cost|token_price|quota_balance|"
    r"budget_score|cheapest|minimize_token|minimize_cost)",
    re.IGNORECASE,
)
BACKGROUND_TOKEN_RE = re.compile(
    r"(crawler|watcher|daemon|scheduler|auto_poll|polling_enabled)", re.IGNORECASE
)
PRICE_ROW_RE = re.compile(r"\$\s?\d")


# --------------------------------------------------------------------------
# strict YAML
# --------------------------------------------------------------------------


class DuplicateKeyError(Exception):
    pass


class StrictLoader(yaml.SafeLoader):
    pass


def _no_duplicates(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise DuplicateKeyError(f"duplicate key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates
)


def load_yaml_strict(path: Path) -> Any:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=StrictLoader)


def normalized_sha256(value: Any) -> str:
    """Identical normalization to the canonical stage runner.

    01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py
    """
    raw = yaml.safe_dump(value, allow_unicode=True, sort_keys=True, width=4096)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk_files(root: Path):
    if not root.is_dir():
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            yield p


# --------------------------------------------------------------------------
# tree under test
# --------------------------------------------------------------------------


class Tree:
    def __init__(self, root: Path):
        self.root = root
        self.errors: list[str] = []
        self._docs: dict[Path, Any] | None = None

    def path(self, rel: str) -> Path:
        return self.root / rel

    def exists(self, rel: str) -> bool:
        return self.path(rel).exists()

    def text(self, rel: str) -> str | None:
        p = self.path(rel)
        if not p.is_file():
            return None
        return p.read_text(encoding="utf-8", errors="replace")

    def mech_files(self) -> list[Path]:
        return list(walk_files(self.path(MECH_DIR)))

    def mech_docs(self) -> dict[Path, Any]:
        """All parseable YAML under the mechanism directory, strictly loaded."""
        if self._docs is not None:
            return self._docs
        docs: dict[Path, Any] = {}
        for p in self.mech_files():
            if p.suffix.lower() not in (".yml", ".yaml"):
                continue
            try:
                docs[p] = load_yaml_strict(p)
            except DuplicateKeyError as exc:
                self.errors.append(f"{p.name}: {exc}")
            except Exception as exc:  # noqa: BLE001
                self.errors.append(f"{p.name}: parse_error: {type(exc).__name__}")
        self._docs = docs
        return docs

    def by_token(self, token: str) -> tuple[Path, Any] | tuple[None, None]:
        for p, doc in self.mech_docs().items():
            if isinstance(doc, dict) and str(doc.get("schema_version", "")).startswith(token):
                return p, doc
        return None, None

    def contract(self):
        return self.by_token(TOKEN_CONTRACT)

    def catalog(self):
        return self.by_token(TOKEN_CATALOG)

    def ledger(self):
        return self.by_token(TOKEN_LEDGER)

    def boot(self) -> Any:
        p = self.path(BOOT_MANIFEST)
        if not p.is_file():
            return None
        try:
            return load_yaml_strict(p)
        except Exception:  # noqa: BLE001
            return None

    def registry(self) -> Any:
        p = self.path(REGISTRY)
        if not p.is_file():
            return None
        try:
            return load_yaml_strict(p)
        except Exception:  # noqa: BLE001
            return None

    def catalog_entries(self) -> list[dict]:
        _, cat = self.catalog()
        if not isinstance(cat, dict):
            return []
        entries = cat.get("entries", [])
        return [e for e in entries if isinstance(e, dict)]


Result = tuple[bool, str]
CHECKS: dict[str, tuple[str, Callable[[Tree], Result]]] = {}


def check(test_id: str, title: str):
    def deco(fn: Callable[[Tree], Result]):
        CHECKS[test_id] = (title, fn)
        return fn

    return deco


# --------------------------------------------------------------------------
# MR-T01 .. MR-T28
# --------------------------------------------------------------------------


@check("MR-T01", "model routing exists as an independent 03_mechanisms capability")
def t01(t: Tree) -> Result:
    if not t.path(MECH_DIR).is_dir():
        return False, f"missing directory {MECH_DIR}"
    if not (t.path(MECH_DIR) / "README.md").is_file():
        return False, "mechanism README.md absent"
    missing = [
        name
        for name, got in (
            ("contract", t.contract()[1]),
            ("catalog", t.catalog()[1]),
            ("project_observation_ledger", t.ledger()[1]),
        )
        if got is None
    ]
    if missing:
        return False, "undiscoverable by schema token: " + ", ".join(missing)
    return True, "mechanism dir, README and three schema-tagged documents present"


@check("MR-T02", "workflow does not duplicate the model catalog")
def t02(t: Tree) -> Result:
    offenders = []
    labels = {
        str(e.get("model_label", "")).strip()
        for e in t.catalog_entries()
        if e.get("model_label")
    }
    for p in walk_files(t.path(WORKFLOW_DIR)):
        if p.suffix.lower() not in (".yml", ".yaml", ".md"):
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        if "citystate.model_routing." in body:
            offenders.append(f"{p.name}: carries a model_routing schema token")
            continue
        hits = {lab for lab in labels if lab and lab in body}
        if len(hits) >= 3:
            offenders.append(f"{p.name}: reproduces {len(hits)} catalog model labels")
    if offenders:
        return False, "; ".join(offenders)
    return True, "no workflow file carries mechanism schema tokens or a label table"


@check("MR-T03", "mechanism declares purpose, loader, disk dependency and failure surfacing")
def t03(t: Tree) -> Result:
    reg = t.registry()
    if not isinstance(reg, dict):
        return False, f"{REGISTRY} missing or unparseable"
    entries = [e for e in reg.get("entries", []) if isinstance(e, dict)]
    if not entries:
        return False, "registry has no entries"
    required = (
        "path",
        "purpose",
        "loader",
        "loader_class",
        "discovery",
        "evidence",
        "failure_surfacing",
        "deletion_rule",
    )
    bad = []
    for e in entries:
        empty = [f for f in required if not str(e.get(f, "")).strip()]
        if "cache_dirs" not in e:
            empty.append("cache_dirs")
        if empty:
            bad.append(f"{e.get('path', '<no path>')}: missing {','.join(empty)}")
    if bad:
        return False, "; ".join(bad[:5])
    if not (t.path(MECH_DIR) / "README.md").is_file():
        return False, "mechanism README.md absent"
    return True, f"{len(entries)} registry entries carry the full declaration set"


@check("MR-T04", "routing input contract carries task/role/risk/shape/capabilities and availability")
def t04(t: Tree) -> Result:
    _, c = t.contract()
    if not isinstance(c, dict):
        return False, "routing contract not found"
    inputs = c.get("inputs")
    if not isinstance(inputs, dict):
        return False, "contract.inputs absent"
    req = set(inputs.get("required", []) or [])
    missing = REQUIRED_INPUTS - req
    if missing:
        return False, "inputs.required missing " + ",".join(sorted(missing))
    opt = set(inputs.get("optional", []) or [])
    avail = {"Human_unavailable_models", "Human_restored_models"}
    if not avail & opt and not inputs.get("availability_default"):
        return False, "no Human availability input and no availability_default"
    return True, f"inputs.required covers {len(REQUIRED_INPUTS)} mandated keys"


@check("MR-T05", "routing output contract carries model, surface, parameters, basis, evidence, limits")
def t05(t: Tree) -> Result:
    _, c = t.contract()
    if not isinstance(c, dict):
        return False, "routing contract not found"
    outputs = c.get("outputs")
    if not isinstance(outputs, dict):
        return False, "contract.outputs absent"
    req = set(outputs.get("required", []) or [])
    missing = REQUIRED_OUTPUTS - req
    if missing:
        return False, "outputs.required missing " + ",".join(sorted(missing))
    return True, f"outputs.required covers {len(REQUIRED_OUTPUTS)} mandated keys"


@check("MR-T06", "route output authority is the constant routing_only")
def t06(t: Tree) -> Result:
    _, c = t.contract()
    if not isinstance(c, dict):
        return False, "routing contract not found"
    outputs = c.get("outputs") if isinstance(c.get("outputs"), dict) else {}
    if outputs.get("authority_constant") != "routing_only":
        return False, f"authority_constant={outputs.get('authority_constant')!r}"
    blob = yaml.safe_dump(c, allow_unicode=True, sort_keys=True)
    granted = [
        tok
        for tok in (
            "master_write_authorized: true",
            "destructive_git_authorized: true",
            "source_write_authorized: true",
            "publication_authorized: true",
        )
        if tok in blob
    ]
    if granted:
        return False, "contract grants non-routing authority: " + ",".join(granted)
    return True, "authority_constant=routing_only and no authority grant in contract"


@check("MR-T07", "registered candidates default available; only Human override excludes or restores")
def t07(t: Tree) -> Result:
    _, c = t.contract()
    if not isinstance(c, dict):
        return False, "routing contract not found"
    rule = c.get("availability_rule")
    if not isinstance(rule, dict):
        return False, "contract.availability_rule absent"
    problems = []
    if rule.get("registered_default") != "available":
        problems.append(f"registered_default={rule.get('registered_default')!r}")
    if rule.get("unavailable_only_by") != "explicit_Human_override":
        problems.append(f"unavailable_only_by={rule.get('unavailable_only_by')!r}")
    if rule.get("restored_by") != "explicit_Human_override":
        problems.append(f"restored_by={rule.get('restored_by')!r}")
    if rule.get("automatic_quota_probe") is not False:
        problems.append("automatic_quota_probe is not false")
    steps = list(c.get("decision_steps", []) or [])
    if not steps or steps[0] != "apply_Human_availability_override":
        problems.append(f"first decision step={steps[0] if steps else None!r}")
    if problems:
        return False, "; ".join(problems)
    return True, "default-available plus Human-only exclusion and restoration"


@check("MR-T08", "no cost, token or quota scoring in the routing decision procedure")
def t08(t: Tree) -> Result:
    _, c = t.contract()
    if not isinstance(c, dict):
        return False, "routing contract not found"
    hits = [s for s in (c.get("decision_steps") or []) if COST_TOKEN_RE.search(str(s))]
    if hits:
        return False, "cost/quota decision step: " + ",".join(map(str, hits))
    prohibited = c.get("prohibited_routing_inputs")
    if not isinstance(prohibited, list) or not prohibited:
        return False, "contract does not declare prohibited_routing_inputs"
    needed = {"token_cost", "price", "quota_balance"}
    if not needed.issubset({str(x) for x in prohibited}):
        return False, "prohibited_routing_inputs missing " + ",".join(
            sorted(needed - {str(x) for x in prohibited})
        )
    leaks = sorted(walk_cost_tokens(c, skip_keys={"prohibited_routing_inputs"}))
    if leaks:
        return False, "cost/quota tokens outside the prohibition list: " + ",".join(leaks)
    return True, "decision procedure carries no cost, token or quota scoring"


def walk_cost_tokens(node: Any, skip_keys: set[str], path: str = "") -> set[str]:
    found: set[str] = set()
    if isinstance(node, dict):
        for k, v in node.items():
            if k in skip_keys:
                continue
            if COST_TOKEN_RE.search(str(k)):
                found.add(f"{path}{k}")
            found |= walk_cost_tokens(v, skip_keys, f"{path}{k}.")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            found |= walk_cost_tokens(v, skip_keys, f"{path}[{i}].")
    elif isinstance(node, str):
        m = COST_TOKEN_RE.search(node)
        if m:
            found.add(f"{path}{m.group(0)}")
    return found


@check("MR-T09", "model and product surface stay separate; identity is (surface, model)")
def t09(t: Tree) -> Result:
    entries = t.catalog_entries()
    if not entries:
        return False, "catalog has no entries"
    seen = set()
    problems = []
    for e in entries:
        for field in ("provider", "surface_id", "model_label"):
            if not str(e.get(field, "")).strip():
                problems.append(f"{e.get('model_label', '<?>')}: missing {field}")
        key = (e.get("surface_id"), e.get("model_label"))
        if key in seen:
            problems.append(f"duplicate identity {key}")
        seen.add(key)
    if problems:
        return False, "; ".join(problems[:5])
    return True, f"{len(entries)} entries keyed by (surface_id, model_label)"


@check("MR-T10", "current product facts carry source, verified_at, invalidation and confidence")
def t10(t: Tree) -> Result:
    entries = [e for e in t.catalog_entries() if e.get("registered") is True]
    if not entries:
        return False, "no registered catalog entries"
    problems = []
    for e in entries:
        label = f"{e.get('surface_id')}::{e.get('model_label')}"
        for f in FRESHNESS_FIELDS:
            val = e.get(f)
            if val is None or (isinstance(val, (list, dict, str)) and len(val) == 0):
                problems.append(f"{label}: missing {f}")
        va = str(e.get("verified_at", ""))
        if va and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", va):
            problems.append(f"{label}: verified_at not an ISO date")
    if problems:
        return False, "; ".join(problems[:5])
    return True, f"{len(entries)} registered entries carry all freshness fields"


@check("MR-T11", "parameter profiles are surface-scoped and evidence-bound")
def t11(t: Tree) -> Result:
    entries = [e for e in t.catalog_entries() if e.get("registered") is True]
    if not entries:
        return False, "no registered catalog entries"
    problems = []
    for e in entries:
        label = f"{e.get('surface_id')}::{e.get('model_label')}"
        profiles = e.get("parameter_profiles")
        if not isinstance(profiles, list) or not profiles:
            problems.append(f"{label}: no parameter_profiles")
            continue
        for pr in profiles:
            if not isinstance(pr, dict):
                problems.append(f"{label}: malformed profile")
                continue
            if not str(pr.get("profile_id", "")).strip():
                problems.append(f"{label}: profile without profile_id")
            if not pr.get("surface_exposure_evidence"):
                problems.append(
                    f"{label}::{pr.get('profile_id')}: no surface_exposure_evidence"
                )
    if problems:
        return False, "; ".join(problems[:5])
    return True, "every registered entry carries surface-bound, evidence-backed profiles"


@check("MR-T12", "API-only reasoning enums cannot masquerade as Web/Desktop parameters")
def t12(t: Tree) -> Result:
    entries = t.catalog_entries()
    if not entries:
        return False, "catalog has no entries"
    problems = []
    for e in entries:
        label = f"{e.get('surface_id')}::{e.get('model_label')}"
        for pr in e.get("parameter_profiles", []) or []:
            if not isinstance(pr, dict):
                continue
            if pr.get("source_class") == "api_documentation" and not pr.get(
                "surface_exposure_evidence"
            ):
                problems.append(f"{label}: api enum without surface evidence")
            levels = {str(v).lower() for v in (pr.get("reasoning_levels") or [])}
            if e.get("surface_id") == "chatgpt_web":
                banned = levels & {"extra_high", "xhigh", "pro", "max"}
                if banned:
                    problems.append(
                        f"{label}: ChatGPT Plus web claims {sorted(banned)} (rejected R01)"
                    )
        if e.get("surface_id") == "chatgpt_web" and e.get("registered") is True:
            ml = str(e.get("model_label", "")).lower()
            if "terra" in ml or "luna" in ml:
                problems.append(
                    f"{label}: Terra/Luna registered on the standard ChatGPT picker (C04)"
                )
    if problems:
        return False, "; ".join(problems[:5])
    return True, "no API-only enum and no rejected ChatGPT-web tier in parameter profiles"


@check("MR-T13", "project observation ledger is separate from the vendor catalog")
def t13(t: Tree) -> Result:
    lp, ledger = t.ledger()
    if not isinstance(ledger, dict):
        return False, "project observation ledger not found"
    obs = ledger.get("observations")
    if not isinstance(obs, list) or not obs:
        return False, "ledger carries no observations list"
    leaked = []
    for e in t.catalog_entries():
        for field in ("observations", "project_observations", "validity", "observed_failure_or_strength"):
            if field in e:
                leaked.append(f"{e.get('surface_id')}::{e.get('model_label')}: {field}")
    if leaked:
        return False, "project evidence inside catalog entry: " + "; ".join(leaked[:5])
    return True, f"ledger holds {len(obs)} observations; catalog holds none"


@check("MR-T14", "diagnostic or anecdotal evidence cannot create a hard qualification boundary")
def t14(t: Tree) -> Result:
    _, ledger = t.ledger()
    if not isinstance(ledger, dict):
        return False, "project observation ledger not found"
    hard_fields = ("qualified", "disqualified", "max_task_tier", "task_ceiling", "hard_gate")
    problems = []
    for o in ledger.get("observations", []) or []:
        if not isinstance(o, dict):
            problems.append("malformed observation")
            continue
        oid = o.get("observation_id", "<?>")
        val = o.get("validity")
        if val not in VALIDITY_VALUES:
            problems.append(f"{oid}: validity={val!r}")
        if not str(o.get("confidence", "")).strip():
            problems.append(f"{oid}: no confidence")
        if val != "formal":
            present = [f for f in hard_fields if o.get(f) not in (None, "", [], False)]
            if present:
                problems.append(f"{oid}: {val} observation sets {present}")
        if str(o.get("surface_id", "")) == "antigravity" and val == "formal":
            problems.append(
                f"{oid}: Antigravity observation claims formal qualification "
                "(Stage02 records these runs as invalid_for_formal_qualification)"
            )
    if problems:
        return False, "; ".join(problems[:5])
    return True, "every observation is graded and no non-formal one gates routing"


@check("MR-T15", "catalog expresses the five in-scope product surfaces")
def t15(t: Tree) -> Result:
    surfaces = {str(e.get("surface_id", "")).strip() for e in t.catalog_entries()}
    missing = REQUIRED_SURFACES - surfaces
    if missing:
        return False, "surfaces absent: " + ",".join(sorted(missing))
    return True, "all five mandated surfaces present"


@check("MR-T16", "unknown stays unknown and entitlement is not account availability")
def t16(t: Tree) -> Result:
    _, cat = t.catalog()
    if not isinstance(cat, dict):
        return False, "catalog not found"
    if cat.get("entitlement_is_account_availability") is not False:
        return False, "catalog does not declare entitlement_is_account_availability: false"
    problems = []
    for e in t.catalog_entries():
        label = f"{e.get('surface_id')}::{e.get('model_label')}"
        if "registered" not in e:
            problems.append(f"{label}: no registered flag")
            continue
        caps = e.get("capabilities")
        if e.get("registered") is True:
            if not isinstance(caps, dict) or not caps:
                problems.append(f"{label}: no capabilities block")
                continue
            for k, v in caps.items():
                if v is None or (isinstance(v, str) and not v.strip()):
                    problems.append(f"{label}: capability {k} is empty rather than 'unknown'")
        if e.get("registered") is False and not str(e.get("status", "")).strip():
            problems.append(f"{label}: unregistered entry without status")
    if problems:
        return False, "; ".join(problems[:5])
    return True, "unknown values are explicit and entitlement is separated from availability"


@check("MR-T17", "entry spec no longer embeds a volatile price or model catalog")
def t17(t: Tree) -> Result:
    body = t.text(ENTRY_SPEC)
    if body is None:
        return False, f"{ENTRY_SPEC} missing"
    price_rows = [ln for ln in body.splitlines() if PRICE_ROW_RE.search(ln)]
    if price_rows:
        return False, f"{len(price_rows)} price rows remain, first: {price_rows[0].strip()[:60]}"
    if COST_TOKEN_RE.search(body) and "per_1m" in body.lower():
        return False, "entry still carries per-1M token pricing text"
    return True, "no price row and no embedded per-token catalog in the entry spec"


@check("MR-T18", "entry spec keeps the stable routing preflight rule and a mechanism pointer")
def t18(t: Tree) -> Result:
    body = t.text(ENTRY_SPEC)
    if body is None:
        return False, f"{ENTRY_SPEC} missing"
    missing = []
    if MECH_DIR not in body:
        missing.append(f"pointer to {MECH_DIR}")
    if "preflight" not in body.lower():
        missing.append("model-routing preflight rule")
    if "executor_profile" not in body:
        missing.append("selected route recorded in executor_profile")
    if "routing_only" not in body:
        missing.append("routing_only grants nothing")
    if "availability" not in body.lower():
        missing.append("Human availability override")
    if missing:
        return False, "entry spec lost: " + "; ".join(missing)
    return True, "preflight rule, executor_profile binding, routing_only and pointer all present"


@check("MR-T19", "test/evidence, independent review and protected-action controls are not weakened")
def t19(t: Tree) -> Result:
    body = t.text(ENTRY_SPEC)
    if body is None:
        return False, f"{ENTRY_SPEC} missing"
    anchors = {
        "§8 evidence standard": "## 8.",
        "§9 independent review and Human gate": "## 9.",
        "T3 blast radius": "T3_high_risk",
        "publisher authority pointer": "repository_publisher_authority_v1.yml",
        "stop conditions": "## 11.",
        "publication transport matrix": "publication_transport",
    }
    missing = [name for name, tok in anchors.items() if tok not in body]
    if missing:
        return False, "entry spec lost: " + "; ".join(missing)
    return True, "all six non-routing control anchors intact"


@check("MR-T20", "publisher authority registry is byte-identical to the Stage 04 baseline")
def t20(t: Tree) -> Result:
    p = t.path(PUBLISHER_AUTHORITY)
    if not p.is_file():
        return False, f"{PUBLISHER_AUTHORITY} missing"
    actual = sha256_file(p)
    if actual != PUBLISHER_AUTHORITY_SHA256:
        return False, f"sha256={actual} expected={PUBLISHER_AUTHORITY_SHA256}"
    return True, "sha256 matches the frozen baseline"


@check("MR-T21", "boot, registry and execution-loader pointers all resolve")
def t21(t: Tree) -> Result:
    boot = t.boot()
    if not isinstance(boot, dict):
        return False, f"{BOOT_MANIFEST} missing or unparseable"
    broken = []
    order = boot.get("load_order", []) or []
    for item in order:
        rel = item.get("path") if isinstance(item, dict) else item
        if not rel or not t.exists(str(rel)):
            broken.append(f"load_order:{rel}")
    for key in ("validator", "registry"):
        rel = boot.get(key)
        if not rel or not t.exists(str(rel)):
            broken.append(f"{key}:{rel}")
    if not t.path(LOADER_DIR).is_dir():
        broken.append(f"loader_dir:{LOADER_DIR}")
    reg = t.registry()
    if isinstance(reg, dict):
        for e in reg.get("entries", []) or []:
            if not isinstance(e, dict):
                continue
            for rel in expand_path_set(str(e.get("path", ""))):
                if not glob_exists(t.root, rel):
                    broken.append(f"registry:{rel}")
    if broken:
        return False, "; ".join(broken[:6])
    return True, f"{len(order)} boot entries plus registry paths and loader dir all resolve"


@check("MR-T22", "mechanism version agrees across contract, boot manifest and registry")
def t22(t: Tree) -> Result:
    _, c = t.contract()
    boot = t.boot()
    reg = t.registry()
    if not isinstance(c, dict) or not isinstance(boot, dict) or not isinstance(reg, dict):
        return False, "contract, boot manifest or registry missing"
    vs = {
        "contract": c.get("mechanism_version"),
        "boot": boot.get("mechanism_version"),
        "registry": reg.get("mechanism_version"),
    }
    if len(set(vs.values())) != 1 or None in vs.values():
        return False, f"version mismatch {vs}"
    return True, f"mechanism_version={list(vs.values())[0]} agrees in three places"


@check("MR-T23", "duplicate keys in mechanism YAML fail closed")
def t23(t: Tree) -> Result:
    t.mech_docs()
    dups = [e for e in t.errors if "duplicate key" in e]
    if dups:
        return False, "; ".join(dups[:5])
    parse = [e for e in t.errors if "parse_error" in e]
    if parse:
        return False, "; ".join(parse[:5])
    return True, "all mechanism YAML loads under a duplicate-rejecting strict loader"


@check("MR-T24", "the mechanism validator itself fails closed on a missing freshness field")
def t24(t: Tree) -> Result:
    boot = t.boot()
    if not isinstance(boot, dict):
        return False, f"{BOOT_MANIFEST} missing or unparseable"
    rel = boot.get("validator")
    if not rel or not t.exists(str(rel)):
        return False, f"declared validator {rel!r} does not resolve"
    cat_path, cat = t.catalog()
    if cat_path is None:
        return False, "catalog not found"
    with tempfile.TemporaryDirectory() as td:
        probe = Path(td) / "tree"
        # copy only what the mechanism validator needs, never the whole repository
        for sub in (MECH_DIR, LOADER_DIR, str(Path(BOOT_MANIFEST).parent).replace("\\", "/")):
            src = t.path(sub)
            if src.is_dir():
                shutil.copytree(src, probe / sub)
        for f in (REGISTRY,):
            if t.exists(f):
                (probe / f).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(t.path(f), probe / f)
        rel_cat = cat_path.relative_to(t.root)
        doc = load_yaml_strict(probe / rel_cat)
        touched = False
        for e in doc.get("entries", []) or []:
            if isinstance(e, dict) and e.get("registered") is True and "verified_at" in e:
                del e["verified_at"]
                touched = True
                break
        if not touched:
            return False, "no registered entry with verified_at to probe"
        (probe / rel_cat).write_text(
            yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=4096),
            encoding="utf-8",
        )
        try:
            proc = subprocess.run(
                [sys.executable, str(probe / str(rel)), "static", str(probe)],
                capture_output=True,
                timeout=120,
                cwd=str(probe),
            )
        except Exception as exc:  # noqa: BLE001
            return False, f"validator not runnable: {type(exc).__name__}"
        if proc.returncode == 0:
            return False, "mechanism validator returned 0 on a catalog missing verified_at"
    return True, f"mechanism validator exits {proc.returncode} on the freshness mutation"


@check("MR-T25", "no cost, price or quota fields anywhere in the mechanism")
def t25(t: Tree) -> Result:
    offenders = []
    for p in t.mech_files():
        if p.suffix.lower() not in (".yml", ".yaml", ".md", ".py"):
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        for ln_no, line in enumerate(body.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            m = COST_TOKEN_RE.search(line)
            if not m:
                continue
            if re.search(r"(prohibited|forbidden|not_used|: false|never|no_)", line, re.I):
                continue
            offenders.append(f"{p.name}:{ln_no}: {m.group(0)}")
    if offenders:
        return False, "; ".join(offenders[:6])
    return True, "no active cost, price or quota field in the mechanism body"


@check("MR-T26", "no automatic fallback chain; unavailability re-runs task fit")
def t26(t: Tree) -> Result:
    _, c = t.contract()
    if not isinstance(c, dict):
        return False, "routing contract not found"
    if "fallback_chain" in c or "automatic_fallback" in c:
        return False, "contract declares an automatic fallback chain"
    val = c.get("on_primary_unavailable")
    if val != "rerun_task_fit_among_remaining_candidates":
        return False, f"on_primary_unavailable={val!r}"
    return True, "no fallback chain; unavailability re-enters task-fit selection"


@check("MR-T27", "no crawler, watcher, scheduler or background probe is started")
def t27(t: Tree) -> Result:
    boot = t.boot()
    if not isinstance(boot, dict):
        return False, f"{BOOT_MANIFEST} missing or unparseable"
    problems = []
    if boot.get("background_processes_started") is not False:
        problems.append("boot does not declare background_processes_started: false")
    if boot.get("automatic_quota_probe") is not False:
        problems.append("boot does not declare automatic_quota_probe: false")
    if boot.get("invocation") not in (
        "explicit_Human_or_authorized_task_executor_only",
        "explicit_Human_or_authorized_executor_command",
    ):
        problems.append(f"boot invocation={boot.get('invocation')!r}")
    scan_roots = [t.path(MECH_DIR), t.path(LOADER_DIR), t.path(BOOT_MANIFEST).parent]
    for root in scan_roots:
        for p in walk_files(root):
            if p.suffix.lower() not in (".yml", ".yaml", ".md", ".py"):
                continue
            for ln_no, line in enumerate(
                p.read_text(encoding="utf-8", errors="replace").splitlines(), 1
            ):
                m = BACKGROUND_TOKEN_RE.search(line)
                if not m:
                    continue
                if re.search(r"(prohibited|: false|no_|not_|never|must not)", line, re.I):
                    continue
                problems.append(f"{p.name}:{ln_no}: {m.group(0)}")
    if problems:
        return False, "; ".join(problems[:6])
    return True, "boot declares no background process and no active probe token found"


@check("MR-T28", "registry covers every mechanism file and every registered path exists")
def t28(t: Tree) -> Result:
    reg = t.registry()
    if not isinstance(reg, dict):
        return False, f"{REGISTRY} missing or unparseable"
    patterns: list[str] = []
    for e in reg.get("entries", []) or []:
        if isinstance(e, dict):
            patterns.extend(expand_path_set(str(e.get("path", ""))))
    uncovered = []
    roots = [t.path(MECH_DIR), t.path(LOADER_DIR), t.path(BOOT_MANIFEST).parent]
    for root in roots:
        for p in walk_files(root):
            rel = p.relative_to(t.root).as_posix()
            if not any(path_matches(pat, rel) for pat in patterns):
                uncovered.append(rel)
    if not t.exists(REGISTRY):
        uncovered.append(REGISTRY)
    if uncovered:
        return False, "unregistered: " + "; ".join(uncovered[:6])
    return True, f"{len(patterns)} registry patterns cover every mechanism file"


# --------------------------------------------------------------------------
# path-set helpers (registry entries use {a,b} sets and ** suffixes)
# --------------------------------------------------------------------------


def expand_path_set(pattern: str) -> list[str]:
    m = re.search(r"\{([^}]*)\}", pattern)
    if not m:
        return [pattern] if pattern else []
    out = []
    for part in m.group(1).split(","):
        out.extend(expand_path_set(pattern[: m.start()] + part.strip() + pattern[m.end():]))
    return out


def path_matches(pattern: str, rel: str) -> bool:
    if pattern.endswith("/**"):
        return rel.startswith(pattern[:-2])
    if pattern.endswith("**"):
        return rel.startswith(pattern[:-2])
    return rel == pattern


def glob_exists(root: Path, pattern: str) -> bool:
    if pattern.endswith("**"):
        base = root / pattern[:-2].rstrip("/")
        return base.is_dir() and any(walk_files(base))
    return (root / pattern).exists()


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------


def run_acceptance(root: Path) -> tuple[int, list[dict]]:
    tree = Tree(root)
    rows = []
    failed = 0
    for tid in sorted(CHECKS):
        title, fn = CHECKS[tid]
        try:
            ok, detail = fn(tree)
        except Exception as exc:  # noqa: BLE001 - a crashing check is a failing check
            ok, detail = False, f"check_error: {type(exc).__name__}: {exc}"
        if not ok:
            failed += 1
        rows.append({"test_id": tid, "title": title, "passed": ok, "detail": detail})
    return failed, rows


def count_criteria_textually(a_path: Path) -> int:
    """Count A's 成功判据 entries without a YAML parse.

    Used only when A does not parse. Deterministic: the entries are the lines
    matching `    - 描述:` inside the `  成功判据:` block.
    """
    count = 0
    inside = False
    for line in a_path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\s{2}成功判据:\s*$", line):
            inside = True
            continue
        if inside:
            if re.match(r"^\s{2}\S", line):
                break
            if re.match(r"^\s{4}-\s*描述:", line):
                count += 1
    return count


def cmd_package(run_root: Path) -> int:
    tests_path = run_root / "04_测试生成" / "04_tests.yml"
    if not tests_path.is_file():
        print(f"FAIL package: {tests_path} not found")
        return 1
    try:
        art = load_yaml_strict(tests_path)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL package: parse_error {type(exc).__name__}: {exc}")
        return 1

    findings: list[str] = []
    # Defects in artifacts this stage may not write. Reported every run, never
    # silently absorbed, and never counted against this package's own exit code.
    upstream: list[str] = []
    common = [
        "schema_version",
        "run_id",
        "stage_id",
        "artifact_kind",
        "artifact_version",
        "status",
        "input_refs",
        "deliberation_receipt",
        "payload",
    ]
    for f in common:
        if f not in art:
            findings.append(f"missing common field {f}")
    if art.get("stage_id") != "workflow_stage_04_test_generation":
        findings.append("stage_id is not workflow_stage_04_test_generation")
    if art.get("artifact_kind") != "frozen_test_package":
        findings.append("artifact_kind is not frozen_test_package")
    if art.get("status") != "complete":
        findings.append("status is not complete")
    if not isinstance(art.get("artifact_version"), int) or art["artifact_version"] < 1:
        findings.append("artifact_version is not a positive integer")

    receipt = art.get("deliberation_receipt", {})
    if not isinstance(receipt, dict):
        findings.append("deliberation_receipt is not a mapping")
    else:
        if receipt.get("profile_id") != "workflow_stage_04_test_generation":
            findings.append("receipt profile_id mismatch")
        if receipt.get("activation_state") != "active_dormant":
            findings.append("receipt activation_state is not active_dormant")
        if receipt.get("route") == "dormant":
            if receipt.get("session_id") is not None or receipt.get("Human_authorization_ref") is not None:
                findings.append("dormant receipt created a session or carried Human authorization")
        elif receipt.get("route") in ("full", "incremental"):
            if not (receipt.get("session_id") and receipt.get("task_gate_ref") and receipt.get("Human_authorization_ref")):
                findings.append("non-dormant receipt lacks gate or Human authorization")
        else:
            findings.append(f"receipt route={receipt.get('route')!r}")

    refs = art.get("input_refs", [])
    if not isinstance(refs, list) or not refs:
        findings.append("input_refs empty")
        refs = []
    need = {
        "workflow_stage_01_requirement_modeling",
        "workflow_stage_02_information_collection",
        "workflow_stage_03_result_modeling",
    }
    got = {r.get("stage_id") for r in refs if isinstance(r, dict)}
    if not need.issubset(got):
        findings.append("input_refs missing predecessor stages " + ",".join(sorted(need - got)))
    for r in refs:
        if not isinstance(r, dict):
            continue
        rel = r.get("path")
        p = run_root / str(rel)
        if not p.is_file():
            findings.append(f"input_ref path does not resolve: {rel}")
            continue
        actual = sha256_file(p)
        if r.get("sha256") != actual:
            findings.append(f"input_ref sha256 drift: {rel} actual={actual}")

    payload = art.get("payload", {})
    if not isinstance(payload, dict):
        print("FAIL package: payload is not a mapping")
        return 1
    for f in ("frozen", "freeze_authorization_ref", "tests", "test_package_sha256"):
        if f not in payload:
            findings.append(f"payload missing {f}")
    if payload.get("frozen") is not True:
        findings.append("payload.frozen is not true")
    if not str(payload.get("freeze_authorization_ref", "")).strip():
        findings.append("freeze_authorization_ref empty")

    tests = payload.get("tests", [])
    digest = normalized_sha256(tests)
    if payload.get("test_package_sha256") != digest:
        findings.append(
            f"test_package_sha256 mismatch: declared={payload.get('test_package_sha256')} actual={digest}"
        )

    # traceability: evidence ids from Stage 02, subjects from B, criteria from A.
    recon = run_root / "02_信息收集与提炼" / "证据对齐与冲突消解_v1.yml"
    b_path = run_root / "03_结果建模" / "B_结果模型_v1.yml"
    a_path = run_root / "01_需求建模" / "requirement" / "A_需求建模_v3.yml"
    evidence_ids: set[str] = set()
    if recon.is_file():
        d = load_yaml_strict(recon)
        evidence_ids |= set((d.get("accepted_claims") or {}).keys())
        evidence_ids |= set((d.get("rejected_or_downgraded_claims") or {}).keys())
        evidence_ids |= set((d.get("source_registry") or {}).keys())
        evidence_ids |= {c.get("id") for c in (d.get("conflicts_resolved") or []) if isinstance(c, dict)}
    else:
        findings.append("reconciliation evidence file not found")
    b_ids: set[str] = set()
    if b_path.is_file():
        b_doc = load_yaml_strict(b_path)
        b_ids = set(((b_doc.get("B") or {}).get("claims") or {}).keys())
    else:
        findings.append("B result model not found")
    criteria_count = 0
    if a_path.is_file():
        try:
            a_doc = load_yaml_strict(a_path)
            criteria_count = len(((a_doc.get("A") or {}).get("成功判据") or []))
        except Exception as exc:  # noqa: BLE001
            # Stage 01 defect, reported not repaired: A is declared machine-readable
            # (schema_version: citystate.requirement_model.A.v1) but does not parse.
            # Counting the criteria by structure keeps this package checkable while
            # leaving the defect visible on every run. Fixing A is out of the
            # Stage 04 write boundary.
            criteria_count = count_criteria_textually(a_path)
            upstream.append(
                f"A_需求建模_v3.yml declares schema_version citystate.requirement_model.A.v1 "
                f"but is not valid YAML ({getattr(exc, 'problem', type(exc).__name__)}); "
                f"成功判据 counted structurally as {criteria_count}. "
                f"Repair is outside the Stage 04 write boundary."
            )
    else:
        findings.append("A requirement model not found")

    if not isinstance(tests, list) or not tests:
        findings.append("payload.tests is empty")
        tests = []
    seen_ids = set()
    kinds = {"positive": 0, "negative": 0, "boundary": 0}
    for tst in tests:
        if not isinstance(tst, dict):
            findings.append("malformed test entry")
            continue
        tid = tst.get("test_id", "<?>")
        if tid in seen_ids:
            findings.append(f"{tid}: duplicate test_id")
        seen_ids.add(tid)
        ids = set(tst.get("evidence_claim_ids") or [])
        if not ids:
            findings.append(f"{tid}: evidence_claim_ids empty")
        unknown = ids - evidence_ids
        if unknown:
            findings.append(f"{tid}: evidence ids not in Stage 02: {sorted(unknown)}")
        if ids & b_ids:
            findings.append(f"{tid}: evidence_claim_ids point into B (self-证明)")
        subj = set(tst.get("subject_result_claim_ids") or [])
        if not subj:
            findings.append(f"{tid}: subject_result_claim_ids empty")
        unknown_subj = subj - b_ids
        if unknown_subj:
            findings.append(f"{tid}: subject not a B claim: {sorted(unknown_subj)}")
        crit = tst.get("success_criterion_index")
        if not isinstance(crit, int) or not (1 <= crit <= max(criteria_count, 1)):
            findings.append(f"{tid}: success_criterion_index out of A range: {crit!r}")
        if tst.get("can_fail") is not True:
            findings.append(f"{tid}: can_fail is not true")
        if not str(tst.get("measurement", "")).strip():
            findings.append(f"{tid}: measurement empty")
        if not str(tst.get("pass_condition", "")).strip():
            findings.append(f"{tid}: pass_condition empty")
        k = tst.get("kind")
        if k not in kinds:
            findings.append(f"{tid}: kind={k!r}")
        else:
            kinds[k] += 1
    missing_impl = sorted(seen_ids - set(CHECKS))
    if missing_impl:
        findings.append(f"tests without an implemented check: {missing_impl}")
    missing_decl = sorted(set(CHECKS) - seen_ids)
    if missing_decl:
        findings.append(f"implemented checks not declared in the package: {missing_decl}")
    for k, n in kinds.items():
        if n == 0:
            findings.append(f"no {k} test declared")

    for u in upstream:
        print(f"UPSTREAM_DEFECT (out of Stage 04 write boundary): {u}")
    if findings:
        print(f"FAIL package: {len(findings)} finding(s)")
        for f in findings:
            print(f"  - {f}")
        return 1
    print(
        f"PASS package: {len(tests)} frozen tests "
        f"(positive={kinds['positive']} negative={kinds['negative']} boundary={kinds['boundary']}), "
        f"digest={digest}"
    )
    return 0


def cmd_acceptance(root: Path, as_json: bool, expect_red: bool) -> int:
    failed, rows = run_acceptance(root)
    if as_json:
        print(json.dumps({"root": str(root), "failed": failed, "results": rows}, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            mark = "PASS" if r["passed"] else "FAIL"
            print(f"{mark} {r['test_id']} {r['title']}")
            if not r["passed"]:
                print(f"       {r['detail']}")
        print(f"--- {len(rows) - failed}/{len(rows)} passed against {root}")
    if expect_red:
        return 0 if failed > 0 else 1
    return 0 if failed == 0 else 1


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------


def build_good_tree(fixtures: Path, repo_root: Path, dest: Path) -> None:
    shutil.copytree(fixtures / "good_tree", dest)
    src = repo_root / PUBLISHER_AUTHORITY
    if not src.is_file():
        raise SystemExit(f"environment_error: {PUBLISHER_AUTHORITY} not found under {repo_root}")
    tgt = dest / PUBLISHER_AUTHORITY
    tgt.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, tgt)


def apply_mutation(tree: Path, mut: dict) -> None:
    if "operations" in mut:
        for op in mut["operations"]:
            apply_one(tree, {**op, "mutation_id": mut["mutation_id"]})
        return
    apply_one(tree, mut)


def apply_one(tree: Path, mut: dict) -> None:
    rel = mut["file"]
    p = tree / rel
    op = mut["operation"]
    if op == "delete_file":
        p.unlink()
        return
    if op == "create_file":
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(mut["content"], encoding="utf-8")
        return
    body = p.read_text(encoding="utf-8")
    if op == "replace":
        if mut["find"] not in body:
            raise SystemExit(f"environment_error: mutation {mut['mutation_id']} anchor not found in {rel}")
        body = body.replace(mut["find"], mut["replace"], 1)
    elif op == "append":
        body = body + mut["append"]
    elif op == "delete_line":
        needle = mut["find"]
        lines = [ln for ln in body.splitlines(keepends=True) if needle not in ln]
        if len(lines) == len(body.splitlines(keepends=True)):
            raise SystemExit(f"environment_error: mutation {mut['mutation_id']} anchor not found in {rel}")
        body = "".join(lines)
    else:
        raise SystemExit(f"environment_error: unknown operation {op}")
    p.write_text(body, encoding="utf-8")


def cmd_selftest(here: Path, repo_root: Path, as_json: bool) -> int:
    fixtures = here.parent / "fixtures"
    muts_path = fixtures / "mutations_v1.yml"
    if not muts_path.is_file():
        print(f"environment_error: {muts_path} not found")
        return 2
    mutations = load_yaml_strict(muts_path).get("mutations", [])

    report: dict[str, Any] = {"positive": None, "negative": [], "boundary": []}
    rc = 0

    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / "good"
        build_good_tree(fixtures, repo_root, good)
        failed, rows = run_acceptance(good)
        baseline_red = {r["test_id"] for r in rows if not r["passed"]}
        report["positive"] = {
            "passed": len(rows) - failed,
            "total": len(rows),
            "red": sorted(baseline_red),
        }
        if failed:
            rc = 1

    for mut in mutations:
        with tempfile.TemporaryDirectory() as td:
            tree = Path(td) / "mut"
            build_good_tree(fixtures, repo_root, tree)
            try:
                apply_mutation(tree, mut)
            except SystemExit as exc:
                report["negative"].append(
                    {"mutation_id": mut["mutation_id"], "ok": False, "detail": str(exc)}
                )
                rc = 1
                continue
            _, rows = run_acceptance(tree)
            red = {r["test_id"] for r in rows if not r["passed"]}
            target = mut["target_check"]
            killed = target in red
            collateral = sorted(red - {target})
            ok = killed
            report["negative"].append(
                {
                    "mutation_id": mut["mutation_id"],
                    "target_check": target,
                    "killed": killed,
                    "collateral": collateral,
                    "ok": ok,
                }
            )
            if not ok:
                rc = 1

    # boundary probes: an empty tree must be all red; a tree with only the
    # mechanism directory must not accidentally satisfy pointer or registry checks.
    with tempfile.TemporaryDirectory() as td:
        empty = Path(td) / "empty"
        empty.mkdir()
        failed, rows = run_acceptance(empty)
        green = sorted(r["test_id"] for r in rows if r["passed"])
        # A pure prohibition ("the tree must not contain X") is vacuously true on an
        # empty tree. That is correct semantics, not a defect, and it is exactly the
        # set whose non-vacuity is proven by its own mutation instead. Any other
        # check passing here would be a vacuous existence assertion.
        ok = set(green) == set(VACUOUS_ON_EMPTY)
        report["boundary"].append(
            {
                "probe": "empty_tree",
                "expected_green": sorted(VACUOUS_ON_EMPTY),
                "actual_green": green,
                "failed": failed,
                "total": len(rows),
                "ok": ok,
            }
        )
        if not ok:
            rc = 1
    with tempfile.TemporaryDirectory() as td:
        partial = Path(td) / "partial"
        build_good_tree(fixtures, repo_root, partial)
        shutil.rmtree(partial / "01_os/02_boot/model_routing")
        shutil.rmtree(partial / "01_os/05_registry/model_routing_v1.yml", ignore_errors=True)
        (partial / "01_os/05_registry/model_routing_v1.yml").unlink(missing_ok=True)
        _, rows = run_acceptance(partial)
        red = {r["test_id"] for r in rows if not r["passed"]}
        need = {"MR-T21", "MR-T22", "MR-T24", "MR-T27", "MR-T28", "MR-T03"}
        ok = need.issubset(red)
        report["boundary"].append(
            {
                "probe": "mechanism_without_boot_or_registry",
                "expected_red": sorted(need),
                "actual_red": sorted(red),
                "ok": ok,
            }
        )
        if not ok:
            rc = 1

    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        pos = report["positive"]
        print(f"positive  good fixture: {pos['passed']}/{pos['total']} green" + (f"  RED={pos['red']}" if pos["red"] else ""))
        killed = sum(1 for r in report["negative"] if r.get("killed"))
        print(f"negative  mutations killed: {killed}/{len(report['negative'])}")
        for r in report["negative"]:
            if not r.get("ok"):
                print(f"  - NOT KILLED {r['mutation_id']} -> {r.get('target_check')} {r.get('detail', '')}")
            elif r.get("collateral"):
                print(f"    {r['mutation_id']} killed {r['target_check']}; collateral {r['collateral']}")
        for b in report["boundary"]:
            print(f"boundary  {b['probe']}: {'ok' if b.get('ok', b.get('failed') == b.get('total')) else 'FAILED'}")
    print("SELFTEST " + ("PASS" if rc == 0 else "FAIL"))
    return rc


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    p1 = sub.add_parser("package")
    p1.add_argument("run_root", type=Path)
    p2 = sub.add_parser("acceptance")
    p2.add_argument("tree_root", type=Path)
    p2.add_argument("--json", action="store_true")
    p2.add_argument("--expect-red", action="store_true", help="exit 0 when at least one check fails")
    p3 = sub.add_parser("selftest")
    p3.add_argument("repo_root", type=Path, nargs="?", default=here.parents[4])
    p3.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.command == "package":
        return cmd_package(args.run_root.resolve())
    if args.command == "acceptance":
        return cmd_acceptance(args.tree_root.resolve(), args.json, args.expect_red)
    return cmd_selftest(here, args.repo_root.resolve(), args.json)


if __name__ == "__main__":
    raise SystemExit(main())
