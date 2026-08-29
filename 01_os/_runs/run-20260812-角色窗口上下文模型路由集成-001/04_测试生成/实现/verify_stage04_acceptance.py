#!/usr/bin/env python3
"""Stage 04 independent acceptance validator, artifact_version 2.

task_id: os-v2-role-window-context-model-routing-integration-001
run_id:  run-20260812-角色窗口上下文模型路由集成-001

Human-gated narrow correction round 1. Closes ST04-IR-001..006 from
04_测试生成/独立接收审核/Stage04冻结测试包独立接收裁决_v1.yml.

Commands:

  package <run_root>      validate 04_tests.yml against the frozen-test schema
                          and its own traceability rules.
  acceptance <tree_root>  run the frozen acceptance checks against a tree.
  selftest [<repo_root>]  positive: candidate tree must be all green.
                          negative: each mutation must turn its target check red.
                          conforming: each legitimate alternative implementation
                                      must stay all green.
                          boundary: declared structural probes.

Exit codes: 0 pass, 1 fail, 2 usage/environment error.

WHAT IS AND IS NOT FROZEN (v2)
------------------------------
Not frozen: the mechanism directory name, canonical filenames, field names,
schema_version naming, the number of contract documents, and whether a third
"successor" entry mode exists at all.

Frozen: the semantic content A requires, discovered either from a boot/registry
declaration of what each loaded document is, or from the document content
itself. Both routes are exercised by conforming variants in the selftest.

Correction notes are marked `# IR-00n` at the site of each fix.
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

Result = tuple[bool, str]

# --------------------------------------------------------------------------
# frozen surface
# --------------------------------------------------------------------------

MECH_PARENT = "01_os/03_mechanisms"
BOOT_PARENT = "01_os/02_boot"
REGISTRY_DIR = "01_os/05_registry"
LOADER_PARENT = "01_os/06_execution/boot"

CONTEXT_BOOT = "01_os/02_boot/context_management/启动清单_v1.yml"
CONTEXT_VALIDATOR = "01_os/03_mechanisms/context_management/实现/verify_context_structure.py"
MODEL_CONTRACT = "01_os/03_mechanisms/model_routing/路由契约_v1.yml"
MODEL_CATALOG = "01_os/03_mechanisms/model_routing/模型与产品面目录_v1.yml"
MODEL_VALIDATOR = "01_os/03_mechanisms/model_routing/实现/verify_model_routing.py"
COMM_MESSAGE = "01_os/03_mechanisms/communication_system/消息契约_v1.yml"
COMM_VALIDATOR = (
    "01_os/06_execution/boot/communication_system/validator/validate_communication_system.py"
)
PUBLISHER_AUTHORITY = "01_os/05_registry/repository_publisher_authority_v1.yml"
MECH_INDEX = "01_os/03_mechanisms/README.md"
WORKFLOW_DIR = "01_os/01_workflow"
ENTRY_SPEC = "01_os/开发入口与单窗口任务规范_v1.md"
DISCIPLINE = "AGENT_WORKING_DISCIPLINE.md"

PUBLISHER_AUTHORITY_SHA256 = (
    "ae9abdf5d729550511de857511a73d36c53f5d52d76e9f57c77b23ad19c29c1a"
)

ROLE_CONCEPTS: dict[str, str] = {
    "foreground": r"foreground|前台|dispatch|adjudicat",
    "backend_execution": r"backend|执行|executor|execution",
    "independent_review": r"review|审核|复核|评审",
    "deep_research": r"research|研究|调研",
    "closed_corpus_refinement": r"refin|closed[_\- ]?corpus|闭合|精炼|语料",
}

ROLE_ATTR_CONCEPTS: dict[str, str] = {
    "responsibility": r"responsib|produces|duty|职责|产出|scope",
    "independence_or_context": r"independen|context|独立|上下文",
    "handoff_direction": r"handoff|交接|next_role|downstream",
    "prohibited_authority": r"authority|prohibit|禁止|权限|grants",
}

# ST04-V2-IR-004: what makes a table a *canonical role source*, as opposed to a
# routing/applicability matrix that happens to be keyed by role. `scope` and
# `context` are deliberately absent here: a `stage_scope` plus `context_hint`
# pair is applicability metadata, not ownership of the role's semantics.
ROLE_SOURCE_CONCEPTS: dict[str, str] = {
    "responsibility": r"responsib|produces|duty|职责|产出|mandate",
    "independence": r"independen|独立|self[_\- ]?review|separation",
    "handoff_direction": r"handoff|交接|next_role|downstream|hands_to",
    "authority_limit": r"authority|prohibit|禁止|权限|grants|forbidden",
}

ROUTE_RECEIPT_CONCEPTS: dict[str, str] = {
    "mechanism_or_catalog_version": r"mechanism_version|catalog_version|source_index_version|version",
    "loaded_paths_or_validator": r"loaded_paths|validator|receipt",
    "surface": r"surface",
    "model": r"model",
    "parameter_profile": r"parameter_profile|profile",
    "routing_basis": r"routing_basis|basis",
    "evidence_refs": r"evidence",
    "limitations": r"limitation",
    "availability_assumption": r"availability",
    "authority": r"authority",
}

HANDOFF_CONCEPTS: dict[str, str] = {
    "from_window": r"from_window|source_window|window_id",
    "task": r"task_id",
    "from_role": r"from_role|sender_role|source_role",
    "next_role": r"next_role|expected_next|recipient_role",
    "outputs": r"output|produced|deliverable",
    "blockers_findings": r"blocker|finding|unresolved",
    "exact_refs": r"ref|pointer|commit|artifact",
    "invalidation": r"invalidat|stale",
    "authority_boundary": r"authority",
}

LIFECYCLE_CONCEPTS: dict[str, str] = {
    "entered": r"enter|created|open",
    "active": r"active",
    "handoff_ready": r"handoff_ready|handoff-ready|ready_for_handoff",
    "closed": r"closed",
    "stale": r"stale|invalidated",
}

# IR-002: A02 requires fresh-versus-reentry. A third mode is optional.
REQUIRED_ENTRY_MODES = ("fresh", "reentry")
REENTRY_RX = r"re[_\-]?entry"

AUTONOMY_KEYS = (
    r"scheduler",
    r"watcher",
    r"daemon",
    r"background_process",
    r"window_spawn",
    r"handoff_delivery",
    r"task_progression",
    r"automatic_delivery",
    r"auto_dispatch",
    r"polling",
)
QUOTA_KEYS = (r"quota", r"entitlement", r"account_probe", r"credit", r"balance")
T3_T4_KEYS = (
    r"retention",
    r"archive_policy",
    r"long_running",
    r"autonomous_continuation",
    r"objective_envelope",
)

PROVIDER_TOKENS = (
    "claude",
    "openai",
    "anthropic",
    "gemini",
    "codex",
    "antigravity",
    "gpt-",
    "opus",
    "sonnet",
    "notebooklm",
)

# IR-004: a key whose own name carries a negation is a *declaration of the
# prohibition*, not an enabling of the behaviour.
NEGATION_RX = r"(prohibit|forbidden|disabled|denied|blocked|banned|disallow|never|absent|^no_|_no_|^not_|_not_)"

# IR-004: provider independence is a property of normative role *bindings*.
# Provenance and citation scalars are description, not selection.
NORMATIVE_BINDING_RX = r"(provider|model|family|surface|vendor|engine|executor|route|assign|prefer|default|selected|pinned)"
# `ref` is matched as a whole segment only: otherwise `preferred_provider`
# would be read as a provenance field because it contains the letters "ref".
PROVENANCE_RX = (
    r"(evidence|source|citation|provenance|note|rationale|basis|comment|example"
    r"|history|why|reason|derivation|(^|_)refs?($|_))"
)

SKIP_DIR_PARTS = {".git", "__pycache__", ".pytest_cache", "_runtime", "08_os"}

# IR-003 discovery route (a): fields in a boot manifest or registry entry that
# describe *what a document is*, as opposed to where it lives or who reads it.
DESCRIPTIVE_KEY_RX = re.compile(
    r"purpose|artifact_kind|document_kind|kind|description|declares|说明|用途", re.I
)


# --------------------------------------------------------------------------
# yaml / hashing helpers
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


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates)


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
        if not p.is_file():
            continue
        if SKIP_DIR_PARTS & set(p.parts):
            continue
        yield p


def flatten(node: Any, path: str = "") -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if isinstance(node, dict):
        for k, v in node.items():
            kp = f"{path}.{k}" if path else str(k)
            if isinstance(v, (dict, list)):
                out.extend(flatten(v, kp))
            else:
                out.append((kp, v))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            kp = f"{path}[{i}]"
            if isinstance(v, (dict, list)):
                out.extend(flatten(v, kp))
            else:
                out.append((kp, v))
    else:
        out.append((path, node))
    return out


def concept_hits(text: str, concepts: dict[str, str]) -> set[str]:
    low = text.lower()
    return {name for name, rx in concepts.items() if re.search(rx, low, re.I)}


NEGATIVE_VALUES = {
    "prohibited",
    "disabled",
    "forbidden",
    "denied",
    "blocked",
    "false",
    "none",
    "never",
    "no",
    "off",
    "absent",
    "not_applicable",
    "discovery_only",
}


def truthy(v: Any) -> bool:
    """IR-004: a value that names a prohibition is not an enabled behaviour."""
    if v is True:
        return True
    if isinstance(v, str):
        s = v.strip().lower()
        if s in NEGATIVE_VALUES:
            return False
        return s in {"true", "yes", "enabled", "on", "active", "allowed", "required"}
    return False


def leaf_of(kp: str) -> str:
    return kp.split(".")[-1].split("[")[0].lower()


def enabled_positions(doc: Any, patterns: tuple[str, ...]) -> list[str]:
    """Key paths where a named behaviour is actually switched on.

    IR-004. Three things make this polarity aware:
      - a key whose own name carries a negation marker is skipped, because a
        truthy value there asserts the prohibition;
      - a value that names a prohibition is not truthy;
      - free prose is never scanned, only key positions.
    """
    out = []
    for kp, val in flatten(doc):
        leaf = leaf_of(kp)
        if not any(re.search(p, leaf, re.I) for p in patterns):
            continue
        if re.search(NEGATION_RX, leaf, re.I):
            continue
        if not truthy(val):
            continue
        out.append(f"{kp}={val!r}")
    return out


# --------------------------------------------------------------------------
# role-table detection
# --------------------------------------------------------------------------

STAGE_KEY_RX = r"^\d{2}_|^workflow_stage|^stage[_\d]|^step"


def _looks_like_role_table(entries: dict[str, Any]) -> bool:
    """ST04-V2-IR-004: a canonical role source, not an applicability matrix.

    Three or more entries must each declare at least two genuine source-of-truth
    properties. A matrix whose per-role payload is `stage_scope` plus
    `context_hint` states where a role applies; it does not own what the role
    is, and is therefore not a second role source.
    """
    scored = 0
    for body in entries.values():
        if not isinstance(body, dict):
            continue
        keys = " ".join(k for k, _ in flatten(body))
        if len(concept_hits(keys, ROLE_SOURCE_CONCEPTS)) >= 2:
            scored += 1
    return scored >= 3


def yaml_role_table(doc: Any) -> set[str]:
    best: set[str] = set()
    stack = [doc]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            structured = {
                k: v
                for k, v in node.items()
                if isinstance(v, dict) and not re.match(STAGE_KEY_RX, str(k), re.I)
            }
            if len(structured) >= 3 and _looks_like_role_table(structured):
                hits: set[str] = set()
                for k in structured:
                    hits |= concept_hits(str(k), ROLE_CONCEPTS)
                if len(hits) > len(best):
                    best = hits
            stack.extend(node.values())
        elif isinstance(node, list):
            entries = {}
            for x in node:
                if isinstance(x, dict):
                    rid = x.get("role_id") or x.get("id") or x.get("role")
                    if isinstance(rid, str) and not re.match(STAGE_KEY_RX, rid, re.I):
                        entries[rid] = x
            if len(entries) >= 3 and _looks_like_role_table(entries):
                hits = set()
                for k in entries:
                    hits |= concept_hits(k, ROLE_CONCEPTS)
                if len(hits) > len(best):
                    best = hits
            stack.extend(node)
    return best


def markdown_tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    tables: list[tuple[list[str], list[list[str]]]] = []
    header: list[str] | None = None
    rows: list[list[str]] = []
    for line in text.splitlines() + [""]:
        s = line.strip()
        is_row = s.startswith("|") and s.count("|") >= 2
        if not is_row:
            if header is not None:
                tables.append((header, rows))
            header, rows = None, []
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= {"-", ":", " "} and c for c in cells):
            continue  # separator
        if header is None:
            header = cells
        else:
            rows.append(cells)
    return tables


def markdown_role_table(text: str) -> set[str]:
    """IR-006: Markdown gets the same dual condition YAML already had.

    A table is a canonical role source only when its first column names three
    or more distinct role concepts AND the table declares normative per-role
    attributes in its header. A role-keyed applicability table — which model
    tier suits which role, which stage a role appears in — declares no
    normative role property and is not a second role source.
    """
    best: set[str] = set()
    for header, rows in markdown_tables(text):
        concepts: set[str] = set()
        for r in rows:
            if r:
                concepts |= concept_hits(r[0], ROLE_CONCEPTS)
        if len(concepts) < 3:
            continue
        attr = concept_hits(" ".join(header[1:]), ROLE_SOURCE_CONCEPTS)
        if not attr:
            continue
        if len(concepts) > len(best):
            best = concepts
    return best


def role_table_concepts(t: Tree, rel: str) -> set[str]:
    if rel.endswith((".yml", ".yaml")):
        return yaml_role_table(t.yml(rel))
    if rel.endswith(".md"):
        return markdown_role_table(t.text(rel) or "")
    return set()


# --------------------------------------------------------------------------
# tree under test
# --------------------------------------------------------------------------


class Tree:
    def __init__(self, root: Path):
        self.root = root
        self._yaml_cache: dict[str, Any] = {}
        self._mech: str | None | bool = False
        self._mech_candidates: list[str] = []
        self._roles_doc: tuple[str | None, Any] | None = None
        self._window_doc: tuple[str | None, Any] | None = None
        self._handoff_doc: tuple[str | None, Any] | None = None
        self._probe_root: Path | None | bool = None
        self._probe_tmp: Any = None
        self._probe_base: tuple[int, str, int] | None = None

    def path(self, rel: str) -> Path:
        return self.root / rel

    def exists(self, rel: str) -> bool:
        return self.path(rel).exists()

    def text(self, rel: str) -> str | None:
        p = self.path(rel)
        if not p.is_file():
            return None
        return p.read_text(encoding="utf-8", errors="replace")

    def yml(self, rel: str) -> Any:
        if rel in self._yaml_cache:
            return self._yaml_cache[rel]
        p = self.path(rel)
        doc: Any = None
        if p.is_file():
            try:
                doc = load_yaml_strict(p)
            except Exception:  # noqa: BLE001
                doc = None
        self._yaml_cache[rel] = doc
        return doc

    def rel(self, p: Path) -> str:
        return p.relative_to(self.root).as_posix()

    # -- surfaces ----------------------------------------------------------

    def system_surface(self) -> list[str]:
        out: list[str] = []
        for p in walk_files(self.path("01_os")):
            rel = self.rel(p)
            if rel.startswith("01_os/_runs/"):
                continue
            out.append(rel)
        for name in (DISCIPLINE, "AGENTS.md", "CLAUDE.md", "README.md", "GEMINI.md"):
            if self.exists(name):
                out.append(name)
        return sorted(out)

    def boot_manifests(self) -> list[str]:
        return sorted(
            self.rel(p) for p in walk_files(self.path(BOOT_PARENT)) if p.suffix in (".yml", ".yaml")
        )

    def boot_loaded_paths(self) -> set[str]:
        out: set[str] = set()
        for rel in self.boot_manifests():
            doc = self.yml(rel)
            if not isinstance(doc, dict):
                continue
            for item in doc.get("load_order") or []:
                if isinstance(item, str):
                    out.add(item)
                elif isinstance(item, dict) and isinstance(item.get("path"), str):
                    out.add(item["path"])
            for key in ("validator", "registry"):
                v = doc.get(key)
                if isinstance(v, str):
                    out.add(v)
        return out

    def active_role_surface(self) -> list[str]:
        loaded = self.boot_loaded_paths()
        d = self.mech_dir()
        out = []
        for rel in self.system_surface():
            if d and rel.startswith(d + "/"):
                continue
            if (
                rel in (DISCIPLINE, "AGENTS.md", "CLAUDE.md", ENTRY_SPEC, "01_os/README.md")
                or rel.startswith(WORKFLOW_DIR + "/")
                or rel.startswith(BOOT_PARENT + "/")
                or rel.startswith(REGISTRY_DIR + "/")
                or rel.startswith("01_os/06_execution/")
                or rel in loaded
            ):
                out.append(rel)
        return out

    def workflow_and_entry_surface(self) -> list[str]:
        return [
            r
            for r in self.system_surface()
            if r.startswith(WORKFLOW_DIR + "/") or r == ENTRY_SPEC
        ]

    # -- naming-neutral mechanism discovery (IR-003) -----------------------

    def _declared_kinds(self, mech: str) -> dict[str, set[str]]:
        """path -> declared artifact kinds, from boot manifest or registry.

        Route (a) of discovery: the mechanism says what each document is. Any
        wording works; only the concept has to be recognisable.
        """
        kinds: dict[str, set[str]] = {}
        sources: list[Any] = []
        bd = self.path(f"{BOOT_PARENT}/{mech}")
        if bd.is_dir():
            for p in sorted(bd.glob("*.yml")):
                sources.append(self.yml(self.rel(p)))
        for p in sorted(self.path(REGISTRY_DIR).glob(f"{mech}_v*.yml")) if self.path(REGISTRY_DIR).is_dir() else []:
            sources.append(self.yml(self.rel(p)))
        for doc in sources:
            if not isinstance(doc, dict):
                continue
            for item in (doc.get("load_order") or []) + (doc.get("entries") or []):
                if not isinstance(item, dict):
                    continue
                path = item.get("path")
                if not isinstance(path, str):
                    continue
                # Only descriptive fields declare what a document *is*. Paths,
                # loaders and evidence pointers are excluded, and any remaining
                # path-shaped token is dropped: otherwise a mechanism directory
                # named `window_role_binding` would declare every one of its
                # files to be the role contract and the window contract at once.
                blob = " ".join(
                    " ".join(w for w in str(v).split() if "/" not in w)
                    for k, v in item.items()
                    if isinstance(v, str) and DESCRIPTIVE_KEY_RX.search(str(k))
                )
                got = set()
                if re.search(r"\brole\b|角色", blob, re.I):
                    got.add("role")
                if re.search(r"\bwindow\b|\bsession\b|窗口|会话", blob, re.I):
                    got.add("window")
                if re.search(r"handoff|交接", blob, re.I):
                    got.add("handoff")
                if got:
                    kinds.setdefault(path, set()).update(got)
        return kinds

    @staticmethod
    def _content_kinds(doc: Any) -> set[str]:
        """Route (b): the document's own content says what it is."""
        if not isinstance(doc, dict):
            return set()
        got: set[str] = set()
        entries = extract_role_entries(doc)
        if len(entries) >= 5 and _looks_like_role_table(entries):
            covered: set[str] = set()
            for rid, body in entries.items():
                covered |= concept_hits(str(rid), ROLE_CONCEPTS)
                label = body.get("label") or body.get("title") or body.get("name")
                if isinstance(label, str):
                    covered |= concept_hits(label, ROLE_CONCEPTS)
            if len(covered) >= 4:
                got.add("role")
        blob = " ".join(f"{k}={v}" for k, v in flatten(doc)).lower()
        if re.search(r"window[_ ]?id", blob) and "fresh" in blob and re.search(REENTRY_RX, blob):
            got.add("window")
        # a handoff contract is a *record* shape: some key path names both the
        # handoff and the fields it must carry. A window contract that merely
        # lists `handoff_ready` as a lifecycle state does not qualify.
        for kp, _ in flatten(doc):
            if re.search(r"handoff|交接", kp, re.I) and re.search(
                r"required|must_carry|字段", kp, re.I
            ):
                got.add("handoff")
                break
        return got

    def mech(self) -> str | None:
        if self._mech is not False:
            return self._mech  # type: ignore[return-value]
        found: list[str] = []
        parent = self.path(MECH_PARENT)
        if parent.is_dir():
            for d in sorted(x for x in parent.iterdir() if x.is_dir()):
                name = d.name
                declared = self._declared_kinds(name)
                covered: set[str] = set()
                for p in walk_files(d):
                    if p.suffix not in (".yml", ".yaml"):
                        continue
                    rel = self.rel(p)
                    covered |= declared.get(rel, set())
                    covered |= self._content_kinds(self.yml(rel))
                if {"role", "window", "handoff"} <= covered:
                    found.append(name)
        self._mech = found[0] if len(found) == 1 else None
        self._mech_candidates = found
        return self._mech  # type: ignore[return-value]

    def mech_candidates(self) -> list[str]:
        self.mech()
        return self._mech_candidates

    def mech_dir(self) -> str | None:
        m = self.mech()
        return f"{MECH_PARENT}/{m}" if m else None

    def mech_files(self) -> list[str]:
        d = self.mech_dir()
        return [self.rel(p) for p in walk_files(self.path(d))] if d else []

    def mech_yaml_files(self) -> list[str]:
        return [r for r in self.mech_files() if r.endswith((".yml", ".yaml"))]

    def doc_of_kind(self, kind: str) -> tuple[str | None, Any]:
        cache = {"role": "_roles_doc", "window": "_window_doc", "handoff": "_handoff_doc"}[kind]
        got = getattr(self, cache)
        if got is not None:
            return got
        m = self.mech()
        result: tuple[str | None, Any] = (None, None)
        if m:
            declared = self._declared_kinds(m)
            by_content = []
            by_declaration = []
            for rel in self.mech_yaml_files():
                doc = self.yml(rel)
                if kind in self._content_kinds(doc):
                    by_content.append((rel, doc))
                elif kind in declared.get(rel, set()):
                    by_declaration.append((rel, doc))
            # Content evidence beats a descriptive phrase: "cross-window handoff
            # contract" declares a handoff, and must not also be read as the
            # window contract.
            ordered = by_content + by_declaration
            if ordered:
                result = ordered[0]
        setattr(self, cache, result)
        return result

    def mech_blob(self) -> str:
        out = []
        for rel in self.mech_yaml_files():
            doc = self.yml(rel)
            if isinstance(doc, dict):
                out.append(" ".join(f"{k}={v}" for k, v in flatten(doc)))
        return " ".join(out)

    def mech_boot_rel(self) -> str | None:
        m = self.mech()
        if not m:
            return None
        d = self.path(f"{BOOT_PARENT}/{m}")
        if not d.is_dir():
            return None
        cands = sorted(p for p in d.glob("*.yml") if p.is_file())
        return self.rel(cands[0]) if cands else None

    def mech_registry_rel(self) -> str | None:
        m = self.mech()
        if not m or not self.path(REGISTRY_DIR).is_dir():
            return None
        cands = sorted(self.path(REGISTRY_DIR).glob(f"{m}_v*.yml"))
        return self.rel(cands[0]) if cands else None

    def mech_loader_dir(self) -> str | None:
        m = self.mech()
        if not m:
            return None
        d = f"{LOADER_PARENT}/{m}"
        return d if self.path(d).is_dir() else None

    # -- probe environment (ST04-V2-IR-006) --------------------------------

    def probe_root(self) -> Path | None:
        """One writable copy of the whole candidate tree, made at most once."""
        if self._probe_root is not None:
            return self._probe_root if self._probe_root is not False else None  # type: ignore[return-value]
        try:
            self._probe_tmp = tempfile.TemporaryDirectory()
            dest = Path(self._probe_tmp.name) / "candidate"
            copy_tree(self.root, dest)
            self._probe_root = dest
        except Exception:  # noqa: BLE001
            self._probe_root = False
            return None
        return dest

    def probe_baseline(self, vrel: str) -> tuple[int, str, int]:
        """Zero-before, measured once on the unmutated candidate tree."""
        if self._probe_base is None:
            root = self.probe_root()
            if root is None:
                self._probe_base = (99, "no candidate tree", 0)
            else:
                n = sum(1 for _ in walk_files(root))
                rc, out = run_validator(root, vrel, root)
                self._probe_base = (rc, out, n)
        return self._probe_base

    def cleanup(self) -> None:
        if self._probe_tmp is not None:
            try:
                self._probe_tmp.cleanup()
            except Exception:  # noqa: BLE001
                pass
            self._probe_tmp = None


def extract_role_entries(doc: Any) -> dict[str, Any]:
    if not isinstance(doc, dict):
        return {}
    best: dict[str, Any] = {}
    for _, v in doc.items():
        if isinstance(v, dict):
            entries = {k: x for k, x in v.items() if isinstance(x, dict)}
            if len(entries) > len(best):
                best = entries
        elif isinstance(v, list):
            entries = {}
            for x in v:
                if isinstance(x, dict):
                    rid = x.get("role_id") or x.get("id") or x.get("role")
                    if isinstance(rid, str):
                        entries[rid] = x
            if len(entries) > len(best):
                best = entries
    return best


BAN_SUFFIX_RX = r"_(prohibited|forbidden|disallowed|disabled|banned|excluded|blocked|denied)$"
BAN_KEY_RX = r"prohibit|forbidden|must_not|disallow|disabled|banned|excluded"


def strip_ban_suffix(leaf: str) -> str | None:
    """ST04-V2-IR-001: `<field>_disabled` and friends all name the same field."""
    m = re.search(BAN_SUFFIX_RX, leaf, re.I)
    return leaf[: m.start()] if m else None


def declared_prohibitions(doc: Any) -> set[str]:
    """Accept list, mapping and every negation-suffix form of "this is banned"."""
    out: set[str] = set()
    for kp, val in flatten(doc):
        leaf = leaf_of(kp)
        parent = kp.rsplit(".", 1)[0] if "." in kp else ""
        if re.search(BAN_KEY_RX, leaf, re.I) and isinstance(val, str):
            out.add(val.strip().lower())
        if re.search(BAN_KEY_RX, parent, re.I) and val is True:
            out.add(leaf)
        base = strip_ban_suffix(leaf)
        if base and val is True:
            out.add(base)
    return out


# --------------------------------------------------------------------------
# check registry
# --------------------------------------------------------------------------

CHECKS: dict[str, tuple[str, Callable[[Tree], Result]]] = {}


def check(test_id: str, title: str):
    def deco(fn: Callable[[Tree], Result]):
        CHECKS[test_id] = (title, fn)
        return fn

    return deco


def need_mech(t: Tree) -> Result | None:
    if t.mech() is None:
        cands = t.mech_candidates()
        if len(cands) > 1:
            return False, f"more than one candidate composition mechanism: {cands}"
        return False, "no role/window composition mechanism is discoverable"
    return None


# ---- role contract -------------------------------------------------------


@check("RW-T01", "a single role/window composition mechanism exists and is self-describing")
def t01(t: Tree) -> Result:
    if not t.path(MECH_PARENT).is_dir():
        return False, f"{MECH_PARENT} missing"
    bad = need_mech(t)
    if bad:
        return bad
    d = t.mech_dir()
    assert d
    if not t.exists(f"{d}/README.md"):
        return False, f"{d}/README.md missing"
    return True, f"mechanism `{t.mech()}` declares role, window and handoff contracts"


@check("RW-T02", "role contract registers the real project roles A requires")
def t02(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("role")
    entries = extract_role_entries(doc)
    if len(entries) < 5:
        return False, f"role contract exposes {len(entries)} structured role entries, need >= 5"
    covered: set[str] = set()
    for rid, body in entries.items():
        covered |= concept_hits(str(rid), ROLE_CONCEPTS)
        label = body.get("label") or body.get("title") or body.get("name")
        if isinstance(label, str):
            covered |= concept_hits(label, ROLE_CONCEPTS)
    missing = sorted(set(ROLE_CONCEPTS) - covered)
    if missing:
        return False, f"role concepts not registered: {missing}"
    return True, f"{len(entries)} roles cover all five A R01 concepts"


@check("RW-T03", "every role entry declares responsibility, independence, handoff and authority limits")
def t03(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("role")
    entries = extract_role_entries(doc)
    if not entries:
        return False, "no role entries"
    bad_rows = []
    for rid, body in entries.items():
        keys = " ".join(k for k, _ in flatten(body))
        missing = sorted(set(ROLE_ATTR_CONCEPTS) - concept_hits(keys, ROLE_ATTR_CONCEPTS))
        if missing:
            bad_rows.append(f"{rid}:{missing}")
    if bad_rows:
        return False, "role entries missing declared properties: " + "; ".join(bad_rows[:4])
    return True, f"all {len(entries)} role entries declare the four A R01 properties"


@check("RW-T04", "role metadata cannot grant publisher, filesystem, security or Human-gated authority")
def t04(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("role")
    grants = enabled_positions(
        doc,
        (
            r"publish",
            r"filesystem",
            r"file_write",
            r"secret",
            r"credential",
            r"master_write",
            r"human_gate",
            r"destructive",
            r"grants_authority",
            r"source_write",
        ),
    )
    if grants:
        return False, f"role contract enables authority: {grants[:4]}"
    neutral = [
        kp
        for kp, v in flatten(doc)
        if re.search(r"authority", leaf_of(kp), re.I)
        and isinstance(v, str)
        and v.strip().lower() in {"none", "routing_only", "no_authority"}
    ]
    if not neutral:
        return False, "role contract never declares its authority effect as none"
    return True, f"authority-neutral ({len(neutral)} declaration(s)), no grant fields"


@check("RW-T05", "no second canonical role source outside the composition mechanism")
def t05(t: Tree) -> Result:
    offenders = []
    for rel in t.active_role_surface():
        hits = role_table_concepts(t, rel)
        if len(hits) >= 3:
            offenders.append(f"{rel}{sorted(hits)}")
    if offenders:
        return False, "duplicate normative role table: " + "; ".join(offenders[:3])
    return True, "single role source across the active surface"


@check("RW-T06", "context_management boot does not carry an active role source")
def t06(t: Tree) -> Result:
    doc = t.yml(CONTEXT_BOOT)
    if not isinstance(doc, dict):
        return False, f"{CONTEXT_BOOT} missing or unparseable"
    d = t.mech_dir()
    offenders = []
    for item in doc.get("load_order") or []:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", ""))
        purpose = str(item.get("purpose", ""))
        if not re.search(r"role|角色", purpose, re.I):
            continue
        if d and path.startswith(d + "/"):
            continue
        offenders.append(f"{path} <- {purpose}")
    if offenders:
        return False, "context boot declares a foreign role source: " + "; ".join(offenders)
    return True, "context boot carries no role source outside the composition mechanism"


# ---- formal window identity ---------------------------------------------


@check("RW-T07", "window contract defines a project-level window identity bound to task facts")
def t07(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("window")
    if not isinstance(doc, dict):
        return False, "no window contract document"
    blob = " ".join(f"{k}={v}" for k, v in flatten(doc))
    need = {
        "window_id": r"window[_ ]?id",
        "task": r"task_id",
        "run": r"run_id",
        "role": r"role_id|role",
        "stage_step": r"stage|step",
        "repository_head": r"head|branch|repository",
        "uniqueness": r"uniq",
    }
    missing = sorted(set(need) - concept_hits(blob, need))
    if missing:
        return False, f"window identity does not bind: {missing}"
    return True, "window identity binds task/run/role/stage/repository facts and declares uniqueness"


@check("RW-T08", "fresh and reentry are separately defined, and any further mode keeps its own identity")
def t08(t: Tree) -> Result:
    """IR-002: A02 mandates fresh-versus-reentry only.

    A third successor/fork mode is an optional design choice (E-003 offers it,
    it does not require it). If one is present its semantics are judged; if it
    is absent that is conforming, and a rename is not a defect.
    """
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("window")
    modes = find_entry_modes(doc)
    if not modes:
        return False, "no entry-mode block found"
    have = {k for k in modes if k in ("fresh",) or re.search(REENTRY_RX, k, re.I)}
    fresh = any(k == "fresh" or re.search(r"^fresh", k, re.I) for k in modes)
    reentry = any(re.search(REENTRY_RX, k, re.I) for k in modes)
    if not (fresh and reentry):
        return False, f"fresh/reentry not both declared: modes={sorted(modes)}"
    extra = [k for k in modes if k not in have]
    for k in extra:
        blob = " ".join(f"{kk}={vv}" for kk, vv in flatten(modes[k]))
        if not re.search(r"window[_ ]?id", blob, re.I):
            return False, f"additional mode {k!r} declares no window identity of its own"
        if not re.search(r"predecessor|prior_window|previous_window|parent", blob, re.I):
            return False, f"additional mode {k!r} does not name the window it descends from"
    tail = f"; optional further modes {sorted(extra)} keep their own identity" if extra else "; no further mode declared, which is conforming"
    return True, "fresh and reentry are separable" + tail


MODE_ID_KEYS = ("mode_id", "entry_mode", "mode", "id", "name", "kind")


def _modes_from_list(node: list) -> dict[str, Any]:
    """ST04-V2-IR-002: a list of mode records is the same declaration.

    A does not constrain the container. Any list whose records carry an
    identifier is normalised to the same {mode_id: body} shape a mapping gives.
    """
    out: dict[str, Any] = {}
    for item in node:
        if not isinstance(item, dict):
            continue
        mid = next(
            (str(item[k]) for k in MODE_ID_KEYS if isinstance(item.get(k), str)), None
        )
        if mid:
            out[mid] = {k: v for k, v in item.items() if k not in MODE_ID_KEYS}
    return out


def _has_fresh_and_reentry(keys) -> bool:
    ks = [str(k) for k in keys]
    return any(re.search(r"^fresh", k, re.I) for k in ks) and any(
        re.search(REENTRY_RX, k, re.I) for k in ks
    )


def find_entry_modes(doc: Any) -> dict[str, Any]:
    """The entry-mode block, whether declared as a mapping or a list of records."""
    stack: list[Any] = [doc]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if _has_fresh_and_reentry(node.keys()):
                return {str(k): v for k, v in node.items() if isinstance(v, dict)} or {
                    str(k): {} for k in node
                }
            stack.extend(node.values())
        elif isinstance(node, list):
            normalised = _modes_from_list(node)
            if normalised and _has_fresh_and_reentry(normalised.keys()):
                return normalised
            stack.extend(node)
    return {}


@check("RW-T09", "formal reentry requires an exact predecessor window identity")
def t09(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("window")
    modes = find_entry_modes(doc)
    target = None
    for k, v in modes.items():
        if re.search(REENTRY_RX, k, re.I) and isinstance(v, dict):
            target = v
    if target is None:
        return False, "no reentry entry-mode block"
    flat = flatten(target)
    declared = [
        f"{k}={v!r}"
        for k, v in flat
        if re.search(r"requir", k, re.I)
        and re.search(r"predecessor|prior_window|previous_window|parent", f"{k}={v}", re.I)
    ]
    if not declared:
        return False, "reentry does not require an exact predecessor window id"
    if not any(re.search(r"exact|identical|equal", f"{k}={v}", re.I) for k, v in flat):
        return False, "reentry binds a predecessor but never requires an exact match"
    return True, f"reentry requires an exact predecessor ({declared[0]})"


@check("RW-T10", "latest or most-recent session is rejected as a formal window identity")
def t10(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("window")
    rejected = False
    enabled = []
    for k, v in flatten(doc):
        blob = f"{k}={v}".lower()
        if not re.search(r"latest|most[_\- ]recent|--continue|continue_most_recent", blob):
            continue
        if re.search(r"prohibit|reject|not_identity|forbidden|false|never|discovery_only", blob):
            rejected = True
        elif truthy(v) or re.search(r"identity", k, re.I):
            enabled.append(f"{k}={v!r}")
    if enabled:
        return False, f"latest-session treated as identity: {enabled[:3]}"
    if not rejected:
        return False, "window contract never rejects latest/most-recent as formal identity"
    return True, "latest-session convenience is explicitly not a formal identity"


@check("RW-T11", "host session identity may be not_observable and is never required")
def t11(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("window")
    flat = flatten(doc)
    blob = " ".join(f"{k}={v}" for k, v in flat).lower()
    if "not_observable" not in blob:
        return False, "window contract has no not_observable disposition for host session id"
    forced = [
        f"{k}={v!r}"
        for k, v in flat
        if re.search(r"host_session|provider_session|host_id", k, re.I)
        and re.search(r"requir", f"{k}{v}", re.I)
        and truthy(v)
    ]
    if forced:
        return False, f"provider host session id is mandatory: {forced}"
    return True, "host session id is optional with an explicit not_observable value"


@check("RW-T12", "window lifecycle declares its states and deterministic invalidation")
def t12(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("window")
    blob = " ".join(f"{k}={v}" for k, v in flatten(doc))
    missing = sorted(set(LIFECYCLE_CONCEPTS) - concept_hits(blob, LIFECYCLE_CONCEPTS))
    if missing:
        return False, f"lifecycle states missing: {missing}"
    if not re.search(r"invalidat|stale_when|stale_condition", blob, re.I):
        return False, "lifecycle declares no invalidation condition"
    return True, "lifecycle states and invalidation conditions are declared"


# ---- context binding -----------------------------------------------------


@check("RW-T13", "window binds context_management by pointer, with fingerprints and stale receipt")
def t13(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("window")
    blob = " ".join(f"{k}={v}" for k, v in flatten(doc))
    need = {
        "mechanism_pointer": r"context_management",
        "entry_or_refs": r"context_entry|approved_ref|ref_set|refs",
        "fingerprint": r"fingerprint|hash|digest",
        "stale": r"stale|invalidat",
    }
    missing = sorted(set(need) - concept_hits(blob, need))
    if missing:
        return False, f"context binding incomplete: {missing}"
    return True, "context binding points at context_management with fingerprints and stale state"


@check("RW-T14", "the composition mechanism does not restate context_management policy")
def t14(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    offenders = []
    for rel in t.mech_yaml_files():
        doc = t.yml(rel)
        if not isinstance(doc, dict):
            continue
        sv = str(doc.get("schema_version", ""))
        if "context_management.boot_manifest.v" in sv or "citystate.context.layout.v" in sv:
            offenders.append(f"{rel} claims {sv}")
            continue
        copied = {leaf_of(k) for k, _ in flatten(doc)} & {
            "三个信息平面",
            "workspace_partition",
            "enforced_access_boundary",
        }
        if copied:
            offenders.append(f"{rel} copies {sorted(copied)}")
    if offenders:
        return False, "context policy duplicated: " + "; ".join(offenders[:3])
    return True, "no context_management policy is restated inside the mechanism"


@check("RW-T15", "no silent fallback to full run history or old chat")
def t15(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    blob = t.mech_blob()
    if not re.search(r"_runs|history|历史", blob, re.I):
        return False, "the mechanism never states a position on historical preload"
    if not re.search(r"prohibit|forbidden|no_default|not_a_source|禁止|false|disabled", blob, re.I):
        return False, "historical preload is mentioned but never prohibited"
    enabled = []
    for rel in t.mech_yaml_files():
        enabled += enabled_positions(
            t.yml(rel), (r"default_preload", r"preload_all", r"load_full_history", r"chat_as_source")
        )
    if enabled:
        return False, f"historical preload enabled: {enabled}"
    return True, "default historical preload and chat-as-source are prohibited"


# ---- model routing binding ----------------------------------------------


@check("RW-T16", "role and task requirements are translated into model_routing's declared inputs")
def t16(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    contract = t.yml(MODEL_CONTRACT)
    if not isinstance(contract, dict):
        return False, f"{MODEL_CONTRACT} missing; cannot check input parity"
    required_inputs = list((contract.get("inputs") or {}).get("required") or [])
    if not required_inputs:
        return False, "model_routing declares no required inputs"
    blob = t.mech_blob()
    missing = [i for i in required_inputs if i not in blob]
    if missing:
        return False, f"routing inputs not produced by the composition layer: {missing}"
    if "model_routing" not in blob:
        return False, "the composition layer never points at model_routing"
    return True, f"all {len(required_inputs)} model_routing required inputs are produced"


@check("RW-T17", "a routed window binds a route receipt with the fields A R07 requires")
def t17(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("window")
    blob = " ".join(f"{k}={v}" for k, v in flatten(doc))
    if not re.search(r"receipt", blob, re.I):
        return False, "window contract binds no routing receipt"
    missing = sorted(set(ROUTE_RECEIPT_CONCEPTS) - concept_hits(blob, ROUTE_RECEIPT_CONCEPTS))
    if missing:
        return False, f"route receipt missing: {missing}"
    return True, "route receipt carries all ten declared properties"


@check("RW-T18", "route authority is constant routing_only and never alters task authority")
def t18(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    ok = False
    for rel in t.mech_yaml_files():
        doc = t.yml(rel)
        if not isinstance(doc, dict):
            continue
        for k, v in flatten(doc):
            if isinstance(v, str) and v.strip() == "routing_only":
                ok = True
            if re.search(r"authority", leaf_of(k), re.I) and isinstance(v, str):
                if v.strip().lower() in {"execution", "publisher", "full", "master_write"}:
                    return False, f"{rel}: {k}={v!r} escalates authority"
    if not ok:
        return False, "routing_only is never asserted by the composition layer"
    grants = []
    for rel in t.mech_yaml_files():
        grants += enabled_positions(
            t.yml(rel), (r"allowed_changed_paths", r"risk_tier", r"master_write", r"destructive_git")
        )
    if grants:
        return False, f"composition output mutates task authority: {grants[:3]}"
    return True, "authority stays routing_only; no task-authority field is written"


@check("RW-T19", "role architecture pins no provider in a normative binding")
def t19(t: Tree) -> Result:
    """IR-004: only normative selection keys are scanned.

    A provenance or evidence scalar that names a vendor describes where a fact
    came from; it does not bind a role to that vendor.
    """
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("role")
    offenders = []
    # ST04-V2-IR-003: a normative binding is a subtree, not a scalar. Once a key
    # on the path selects a provider/model/family, every key and every scalar
    # below it is part of that selection -- `preferred_provider: {openai: true}`
    # pins a vendor exactly as `preferred_provider: openai` does.
    for k, v in flatten(doc):
        segments = [s.split("[")[0].lower() for s in k.split(".")]
        if any(re.search(PROVENANCE_RX, s, re.I) for s in segments):
            continue
        binding_at = next(
            (i for i, s in enumerate(segments) if re.search(NORMATIVE_BINDING_RX, s, re.I)),
            None,
        )
        if binding_at is None:
            continue
        # keys below the binding point, plus the leaf value
        below = " ".join(segments[binding_at + 1 :])
        hay = f"{below} {v}".lower() if isinstance(v, (str, int, float, bool)) else below.lower()
        if not truthy(v) and not isinstance(v, str):
            # a mapping key set to false does not pin anything
            if v is False:
                continue
        if any(tok in hay for tok in PROVIDER_TOKENS):
            offenders.append(f"{k}={v!r}")
    for rid in extract_role_entries(doc):
        if any(tok in str(rid).lower() for tok in PROVIDER_TOKENS):
            offenders.append(f"role id {rid!r}")
    if offenders:
        return False, f"provider pinned in a normative role binding: {offenders[:3]}"
    return True, "no provider is bound normatively in the role contract"


@check("RW-T20", "an unrouted or receipt-less window is not silently accepted")
def t20(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("window")
    blob = " ".join(f"{k}={v}" for k, v in flatten(doc))
    if not re.search(r"fail[_ ]?closed|blocked|reject", blob, re.I):
        return False, "window contract declares no fail-closed disposition"
    if not re.search(r"receipt", blob, re.I):
        return False, "no receipt requirement to fail closed on"
    return True, "missing or stale receipt is declared fail-closed"


# ---- independence --------------------------------------------------------


@check("RW-T21", "review and implementation windows must be distinct project windows")
def t21(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    blob = t.mech_blob()
    if not re.search(r"independen", blob, re.I):
        return False, "independence is never expressed"
    if not re.search(r"distinct|different_window|!=|separate", blob, re.I):
        return False, "no rule requiring the review window to differ from the implementation window"
    return True, "review window must differ from the implementation window"


@check("RW-T22", "different_model_family is a routing constraint, not a vendor in role architecture")
def t22(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    blob = t.mech_blob()
    if not re.search(r"different_model_family|model_family", blob, re.I):
        return False, "model-family independence is never expressed"
    if not re.search(r"constraint|routing_input|required_capabilit|surface_constraint", blob, re.I):
        return False, "model-family independence is not expressed as a routing constraint"
    _, role_doc = t.doc_of_kind("role")
    for k, v in flatten(role_doc):
        if re.search(r"family", leaf_of(k), re.I) and isinstance(v, str):
            if any(tok in v.lower() for tok in PROVIDER_TOKENS):
                return False, f"role contract pins a model family: {k}={v!r}"
    return True, "model-family independence travels as a routing constraint"


@check("RW-T23", "host session freshness is disclosed, not claimed as proof")
def t23(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    blob = t.mech_blob()
    if not re.search(r"assert|disclos|declared_by", blob, re.I):
        return False, "no disclosure/assertion field for unobservable session freshness"
    overclaim = []
    for rel in t.mech_yaml_files():
        doc = t.yml(rel)
        if not isinstance(doc, dict):
            continue
        for k, v in flatten(doc):
            if re.search(r"session_freshness|host_freshness", k, re.I) and isinstance(v, str):
                if re.search(r"proven|verified|guaranteed", v, re.I):
                    overclaim.append(f"{k}={v!r}")
    if overclaim:
        return False, f"unobservable freshness claimed as proven: {overclaim}"
    return True, "session freshness is a disclosed assertion, not a technical proof"


# ---- handoff -------------------------------------------------------------


@check("RW-T24", "handoff contract carries the fields A R09 requires")
def t24(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("handoff")
    if not isinstance(doc, dict):
        return False, "no handoff contract document"
    blob = " ".join(f"{k}={v}" for k, v in flatten(doc))
    missing = sorted(set(HANDOFF_CONCEPTS) - concept_hits(blob, HANDOFF_CONCEPTS))
    if missing:
        return False, f"handoff missing: {missing}"
    return True, "handoff carries all nine A R09 properties"


@check("RW-T25", "handoff prohibits private reasoning and delivery/acceptance state")
def t25(t: Tree) -> Result:
    """IR-004: list, mapping and `<field>_prohibited: true` forms all count."""
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("handoff")
    prohibited = declared_prohibitions(doc)
    if not any(re.search(r"chain_of_thought|private_reasoning|reasoning", p) for p in prohibited):
        return False, f"handoff never prohibits a private reasoning field; declared={sorted(prohibited)[:6]}"
    if not any(re.search(r"deliver|read_state|accepted|receipt_state", p) for p in prohibited):
        return False, f"handoff never prohibits delivery/read/acceptance state; declared={sorted(prohibited)[:6]}"
    # A field that *is* the prohibition declaration is not a carried field.
    carried = []
    for k, _ in flatten(doc):
        leaf = leaf_of(k)
        if not re.search(r"chain_of_thought|private_reasoning", leaf, re.I):
            continue
        if re.search(BAN_KEY_RX, k, re.I) or strip_ban_suffix(leaf):
            continue
        carried.append(k)
    if carried:
        return False, f"handoff itself carries a reasoning field: {carried}"
    return True, f"private reasoning and delivery state are prohibited ({len(prohibited)} declared)"


@check("RW-T26", "handoff does not imply automatic delivery, acceptance or progression")
def t26(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    _, doc = t.doc_of_kind("handoff")
    blob = " ".join(f"{k}={v}" for k, v in flatten(doc))
    if not re.search(r"human[_ ]?(triggered|relayed)|does_not_imply|no_automatic", blob, re.I):
        return False, "handoff never states that it does not progress the task by itself"
    enabled = enabled_positions(doc, AUTONOMY_KEYS)
    if enabled:
        return False, f"handoff enables autonomous behaviour: {enabled[:3]}"
    return True, "handoff is a declarative pointer with no automatic progression"


@check("RW-T27", "communication_system transport stays separable from window handoff")
def t27(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    msg = t.yml(COMM_MESSAGE)
    if not isinstance(msg, dict):
        return False, f"{COMM_MESSAGE} missing or unparseable"
    blob = " ".join(f"{k}={v}" for k, v in flatten(msg))
    leaked = [tok for tok in ("window_id", "entry_mode", "lifecycle_state", "route_receipt") if tok in blob]
    if leaked:
        return False, f"window lifecycle leaked into the message contract: {leaked}"
    _, doc = t.doc_of_kind("handoff")
    hblob = " ".join(f"{k}={v}" for k, v in flatten(doc))
    if not re.search(r"communication", hblob, re.I):
        return False, "handoff contract never states its relation to communication_system"
    return True, "message contract is unchanged; handoff references it without merging"


# ---- failure surfacing / composition -------------------------------------


@check("RW-T28", "boot manifest, registry and execution loader pointers exist and resolve")
def t28(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    boot_rel = t.mech_boot_rel()
    reg_rel = t.mech_registry_rel()
    loader = t.mech_loader_dir()
    missing = [
        n
        for n, v in (("boot manifest", boot_rel), ("registry", reg_rel), ("execution loader dir", loader))
        if not v
    ]
    if missing:
        return False, f"missing convention pointer: {missing}"
    boot = t.yml(boot_rel)  # type: ignore[arg-type]
    if not isinstance(boot, dict):
        return False, f"{boot_rel} unparseable"
    broken = []
    for item in boot.get("load_order") or []:
        p = item if isinstance(item, str) else (item or {}).get("path")
        if not isinstance(p, str) or not t.exists(p):
            broken.append(str(p))
    for key in ("validator", "registry"):
        v = boot.get(key)
        if not isinstance(v, str) or not t.exists(v):
            broken.append(f"{key}={v!r}")
    if broken:
        return False, f"broken declared pointers: {broken[:4]}"
    return True, "all declared boot pointers resolve"


@check("RW-T29", "the mechanism registry declares failure surfacing for every entry")
def t29(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    reg_rel = t.mech_registry_rel()
    if not reg_rel:
        return False, "no registry file"
    reg = t.yml(reg_rel)
    entries = (reg or {}).get("entries") if isinstance(reg, dict) else None
    if not entries:
        return False, f"{reg_rel} has no entries"
    required = {
        "path",
        "purpose",
        "loader",
        "loader_class",
        "discovery",
        "evidence",
        "cache_dirs",
        "failure_surfacing",
        "deletion_rule",
    }
    for e in entries:
        if not isinstance(e, dict):
            return False, "non-mapping registry entry"
        miss = sorted(required - set(e))
        if miss:
            return False, f"registry entry {e.get('path')!r} missing {miss}"
    d = t.mech_dir()
    if not any(str(e.get("path", "")).startswith(d or "@") for e in entries):
        return False, "registry does not cover the mechanism directory"
    return True, f"{len(entries)} registry entries carry all nine fields"


@check("RW-T30", "the mechanism index lists the composition mechanism")
def t30(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    txt = t.text(MECH_INDEX)
    if txt is None:
        return False, f"{MECH_INDEX} missing"
    m = t.mech()
    assert m
    if m not in txt:
        return False, f"{MECH_INDEX} does not mention `{m}`"
    return True, "mechanism index points at the composition mechanism"


@check("RW-T31", "workflow and the development entry keep no second role source or context policy")
def t31(t: Tree) -> Result:
    offenders = []
    for rel in t.workflow_and_entry_surface():
        hits = role_table_concepts(t, rel)
        if len(hits) >= 3:
            offenders.append(f"{rel} role table {sorted(hits)}")
        if rel.endswith((".yml", ".yaml")):
            doc = t.yml(rel)
            if isinstance(doc, dict) and "context_management.boot_manifest.v" in str(
                doc.get("schema_version", "")
            ):
                offenders.append(f"{rel} duplicates context boot")
    if offenders:
        return False, "; ".join(offenders[:3])
    return True, "workflow and entry carry no role table or context boot duplicate"


@check("RW-T43", "workflow and the development entry keep no second mutable model catalog")
def t43(t: Tree) -> Result:
    """IR-001: the A11 clause the v1 package omitted on a false premise.

    Ownership-aware: a pointer to model_routing, an invocation of its boot
    validator, or a reference to its receipt field names is exactly what A11
    asks for and must stay green. What is prohibited is a second *mutable*
    catalog: three or more of the live catalog's own model identifiers restated
    as structured entries, or a document claiming the catalog schema itself.
    """
    labels = catalog_identifiers(t)
    if len(labels) < 3:
        return False, f"{MODEL_CATALOG} not readable ({len(labels)} identifiers); cannot judge duplication"
    offenders = []
    for rel in t.workflow_and_entry_surface():
        if rel.endswith((".yml", ".yaml")):
            doc = t.yml(rel)
            if isinstance(doc, dict) and "model_routing.catalog.v" in str(doc.get("schema_version", "")):
                offenders.append(f"{rel} claims the catalog schema")
                continue
        text = t.text(rel) or ""
        structured = set()
        for line in structured_entry_lines(text):
            for lab in labels:
                if lab in line:
                    structured.add(lab)
        if len(structured) >= 3:
            offenders.append(f"{rel} restates {sorted(structured)[:4]}")
    if offenders:
        return False, "second mutable model catalog: " + "; ".join(offenders[:3])
    return True, f"no duplicated catalog ({len(labels)} live identifiers checked); pointers are allowed"


def structured_entry_lines(text: str) -> list[str]:
    """Lines that carry a structured entry rather than prose.

    ST04-V2-IR-005: a Markdown definition list states its term on one line and
    the definition on the next, so the term line has no leading marker at all.
    Recognising only pipes, dashes and `key:` let a definition-list catalog pass.
    """
    lines = text.splitlines()
    out: list[str] = []
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not s:
            continue
        if s.startswith("|") or re.match(r"^[-*+]\s", s) or re.match(r"^\d+[.)]\s", s):
            out.append(s)
            continue
        if re.match(r"^[\w\-.一-鿿]+\s*:", s):
            out.append(s)
            continue
        # definition-list term: the next non-empty line begins a definition
        for j in range(i + 1, min(i + 3, len(lines))):
            nxt = lines[j].strip()
            if not nxt:
                continue
            if re.match(r"^[:：]\s", nxt) or nxt in (":", "："):
                out.append(s)
            break
        # table cell content also counts, split so a single row yields its cells
        if s.startswith("|"):
            out.extend(c.strip() for c in s.strip("|").split("|"))
    return out


def catalog_identifiers(t: Tree) -> set[str]:
    doc = t.yml(MODEL_CATALOG)
    out: set[str] = set()
    if not isinstance(doc, dict):
        return out
    for e in doc.get("entries") or []:
        if not isinstance(e, dict):
            continue
        for k in ("model_label", "surface_label", "model_id", "product_surface", "parameter_profile"):
            v = e.get(k)
            if isinstance(v, str) and len(v.strip()) >= 4:
                out.add(v.strip())
    return out


@check("RW-T32", "existing context, model and communication validators still pass")
def t32(t: Tree) -> Result:
    results = []
    for rel in (CONTEXT_VALIDATOR, MODEL_VALIDATOR, COMM_VALIDATOR):
        if not t.exists(rel):
            return False, f"{rel} missing"
        rc, out = run_validator(t.root, rel, t.root)
        results.append(f"{Path(rel).name}={rc}")
        if rc != 0:
            return False, f"{rel} exits {rc}: {out[:160]}"
    return True, "existing mechanism validators all exit 0 (" + ", ".join(results) + ")"


@check("RW-T33", "publisher authority is byte-identical to the Stage 04 baseline")
def t33(t: Tree) -> Result:
    p = t.path(PUBLISHER_AUTHORITY)
    if not p.is_file():
        return False, f"{PUBLISHER_AUTHORITY} missing"
    got = sha256_file(p)
    if got != PUBLISHER_AUTHORITY_SHA256:
        return False, f"sha256 {got} != frozen {PUBLISHER_AUTHORITY_SHA256}"
    return True, "publisher authority unchanged"


# ---- explicit non-goals --------------------------------------------------


@check("RW-T34", "no scheduler, watcher, daemon or automatic progression is enabled")
def t34(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    enabled = []
    surfaces = t.mech_yaml_files() + [x for x in (t.mech_boot_rel(), t.mech_registry_rel()) if x]
    for rel in surfaces:
        enabled += [f"{rel}:{p}" for p in enabled_positions(t.yml(rel), AUTONOMY_KEYS)]
    if enabled:
        return False, f"autonomous behaviour enabled: {enabled[:3]}"
    boot_rel = t.mech_boot_rel()
    boot = t.yml(boot_rel) if boot_rel else None
    if not isinstance(boot, dict):
        return False, "no boot manifest to carry the declaration"
    declared = [
        k
        for k, _ in flatten(boot)
        if re.search(r"background_process|automatic|scheduler|watcher|daemon", leaf_of(k), re.I)
    ]
    if not declared:
        return False, "boot manifest never declares its autonomy posture"
    return True, f"boot declares {len(declared)} autonomy positions, none enabled"


@check("RW-T35", "no automated quota or account probing is enabled")
def t35(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    enabled = []
    for rel in t.mech_yaml_files() + [x for x in (t.mech_boot_rel(),) if x]:
        enabled += [f"{rel}:{p}" for p in enabled_positions(t.yml(rel), QUOTA_KEYS)]
    if enabled:
        return False, f"quota probing enabled: {enabled[:3]}"
    return True, "no quota or entitlement probing is enabled"


@check("RW-T36", "no T3 retention or T4 autonomous-continuation semantics is enabled")
def t36(t: Tree) -> Result:
    bad = need_mech(t)
    if bad:
        return bad
    enabled = []
    for rel in t.mech_yaml_files():
        enabled += [f"{rel}:{p}" for p in enabled_positions(t.yml(rel), T3_T4_KEYS)]
    if enabled:
        return False, f"out-of-scope roadmap semantics enabled: {enabled[:3]}"
    return True, "no T3 retention or T4 continuation semantics"


# ---- mechanism-validator probes -----------------------------------------


def run_validator(cwd: Path, validator_rel: str, tree_root: Path) -> tuple[int, str]:
    for argv in (["static", str(tree_root)], [str(tree_root)]):
        try:
            proc = subprocess.run(
                [sys.executable, str(cwd / validator_rel), *argv],
                capture_output=True,
                timeout=300,
                cwd=str(cwd),
            )
        except Exception as exc:  # noqa: BLE001
            return 99, f"{type(exc).__name__}: {exc}"
        out = (proc.stdout + proc.stderr).decode("utf-8", "replace")
        if proc.returncode == 2 and "usage" in out.lower():
            continue
        return proc.returncode, out
    return 2, "validator rejected both calling conventions"


MECH_SNAPSHOT_DIRS = (MECH_PARENT, BOOT_PARENT, LOADER_PARENT, REGISTRY_DIR)


def probe_full_tree(t: Tree, label: str, mutate: Callable[[Path], bool]) -> Result:
    """Run the mechanism's own validator against the FULL candidate tree.

    ST04-V2-IR-006. The previous rounds staged a computed dependency closure.
    The independent review showed that closure was simultaneously history-heavy
    (776 of 1012 staged files came from unrelated `_runs`) and still incomplete
    (16 resolvable file references left out), so a green baseline rested on an
    accidental path scan rather than on a real bound. The crawler is deleted
    rather than improved: the honest environment for a composition validator is
    the candidate tree itself.

    One writable copy is made per tree under test and reused by every probe;
    the mechanism surface is snapshotted before each injection and restored
    after, so the probes stay independent without copying the tree six times.
    """
    bad = need_mech(t)
    if bad:
        return bad
    boot_rel = t.mech_boot_rel()
    boot = t.yml(boot_rel) if boot_rel else None
    if not isinstance(boot, dict):
        return False, "no boot manifest"
    vrel = boot.get("validator")
    if not isinstance(vrel, str) or not t.exists(vrel):
        return False, f"declared validator {vrel!r} does not resolve"

    root = t.probe_root()
    if root is None:
        return False, "could not materialise the candidate tree for probing"
    rc0, out0, n = t.probe_baseline(vrel)
    if rc0 != 0:
        return False, f"validator exits {rc0} on the unmutated candidate tree ({n} files): {out0[:200]}"

    snapshot: dict[Path, bytes] = {}
    for d in MECH_SNAPSHOT_DIRS:
        base = root / d
        if base.is_dir():
            for p in base.rglob("*"):
                if p.is_file():
                    snapshot[p] = p.read_bytes()
    try:
        if not mutate(root):
            return False, f"{label}: no anchor to mutate"
        rc1, _ = run_validator(root, vrel, root)
    finally:
        for p, data in snapshot.items():
            if not p.is_file() or p.read_bytes() != data:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
        for d in MECH_SNAPSHOT_DIRS:
            base = root / d
            if base.is_dir():
                for p in list(base.rglob("*")):
                    if p.is_file() and p not in snapshot:
                        p.unlink()
    if rc1 == 0:
        return False, f"validator returns 0 on {label}"
    return True, f"validator exits 0 on the {n}-file candidate tree and {rc1} on {label}"


# ST04-V2-IR-006: the dependency crawler and the closure-based probe wrapper
# that used to live here are deleted, not improved. probe_full_tree() above
# runs the mechanism's declared validator against the candidate tree itself.


def _mech_doc_path(t: Tree, probe: Path, kind: str) -> Path | None:
    rel, _ = t.doc_of_kind(kind)
    return probe / rel if rel else None


def _patch_yaml(p: Path, fn: Callable[[Any], bool]) -> bool:
    try:
        doc = load_yaml_strict(p)
    except Exception:  # noqa: BLE001
        return False
    if not fn(doc):
        return False
    p.write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=4096), encoding="utf-8"
    )
    return True


@check("RW-T37", "mechanism validator fails closed on an unknown role reference")
def t37(t: Tree) -> Result:
    def mutate(probe: Path) -> bool:
        p = _mech_doc_path(t, probe, "window")
        if p is None or not p.is_file():
            return False

        def fn(doc: Any) -> bool:
            if not isinstance(doc, dict):
                return False
            doc["role_id"] = "role_that_does_not_exist"
            return True

        return _patch_yaml(p, fn)

    return probe_full_tree(t, "unknown role reference", mutate)


@check("RW-T38", "mechanism validator fails closed on a lost window-identity uniqueness rule")
def t38(t: Tree) -> Result:
    def mutate(probe: Path) -> bool:
        p = _mech_doc_path(t, probe, "window")
        if p is None or not p.is_file():
            return False

        def fn(doc: Any) -> bool:
            stack = [doc]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    for k in list(node):
                        if re.search(r"uniq", str(k), re.I):
                            node[k] = False
                            return True
                    stack.extend(node.values())
                elif isinstance(node, list):
                    stack.extend(node)
            return False

        return _patch_yaml(p, fn)

    return probe_full_tree(t, "window identity uniqueness removed", mutate)


@check("RW-T39", "mechanism validator fails closed on an invalid reentry")
def t39(t: Tree) -> Result:
    def mutate(probe: Path) -> bool:
        p = _mech_doc_path(t, probe, "window")
        if p is None or not p.is_file():
            return False
        body = p.read_text(encoding="utf-8")
        for needle in ("predecessor_window_id", "predecessor"):
            if needle in body:
                p.write_text(body.replace(needle, "latest_session", 1), encoding="utf-8")
                return True
        return False

    return probe_full_tree(t, "reentry rebound to latest session", mutate)


@check("RW-T40", "mechanism validator fails closed on a broken declared pointer")
def t40(t: Tree) -> Result:
    def mutate(probe: Path) -> bool:
        boot_rel = t.mech_boot_rel()
        if not boot_rel:
            return False

        def fn(doc: Any) -> bool:
            if not isinstance(doc, dict):
                return False
            doc["registry"] = "01_os/05_registry/does_not_exist_v1.yml"
            return True

        return _patch_yaml(probe / boot_rel, fn)

    return probe_full_tree(t, "registry pointer broken", mutate)


@check("RW-T41", "mechanism validator fails closed on an authority escalation attempt")
def t41(t: Tree) -> Result:
    def mutate(probe: Path) -> bool:
        p = _mech_doc_path(t, probe, "role")
        if p is None or not p.is_file():
            return False

        def fn(doc: Any) -> bool:
            entries = extract_role_entries(doc)
            for _, body in entries.items():
                if isinstance(body, dict):
                    body["master_write_authorized"] = True
                    return True
            return False

        return _patch_yaml(p, fn)

    return probe_full_tree(t, "role entry granting master write", mutate)


@check("RW-T42", "mechanism validator fails closed on a missing route receipt binding")
def t42(t: Tree) -> Result:
    def mutate(probe: Path) -> bool:
        p = _mech_doc_path(t, probe, "window")
        if p is None or not p.is_file():
            return False

        def fn(doc: Any) -> bool:
            hit = False
            stack: list[Any] = [doc]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    for k, v in list(node.items()):
                        if re.search(r"receipt", str(k), re.I) and isinstance(v, dict):
                            for kk in list(v):
                                if re.search(r"required_fields", str(kk), re.I):
                                    v[kk] = []
                                    hit = True
                        stack.append(v)
                elif isinstance(node, list):
                    stack.extend(node)
            return hit

        return _patch_yaml(p, fn)

    return probe_full_tree(t, "route receipt required fields emptied", mutate)


# --------------------------------------------------------------------------
# runners
# --------------------------------------------------------------------------


def copy_tree(src: Path, dest: Path) -> None:
    def ignore(_dir, names):
        return [n for n in names if n in SKIP_DIR_PARTS]

    shutil.copytree(src, dest, ignore=ignore, symlinks=True)


def run_acceptance(root: Path) -> tuple[int, list[dict]]:
    t = Tree(root)
    rows = []
    failed = 0
    try:
        for test_id, (title, fn) in CHECKS.items():
            try:
                passed, detail = fn(t)
            except Exception as exc:  # noqa: BLE001
                passed, detail = False, f"check raised {type(exc).__name__}: {exc}"
            rows.append({"test_id": test_id, "title": title, "passed": passed, "detail": detail})
            if not passed:
                failed += 1
    finally:
        t.cleanup()
    return failed, rows


def cmd_acceptance(root: Path, as_json: bool, expect_red: bool) -> int:
    failed, rows = run_acceptance(root)
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for r in rows:
            print(f"{'PASS' if r['passed'] else 'FAIL'}  {r['test_id']}  {r['detail']}")
    print(f"acceptance: {len(rows) - failed}/{len(rows)} green")
    if expect_red:
        return 0 if failed else 1
    return 0 if failed == 0 else 1


def apply_overlay(overlay: Path, dest: Path) -> None:
    for p in sorted(overlay.rglob("*")):
        if not p.is_file():
            continue
        tgt = dest / p.relative_to(overlay)
        tgt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, tgt)


def apply_one(tree: Path, mut: dict) -> None:
    rel = mut["file"]
    p = tree / rel
    op = mut["operation"]
    if op == "delete_file":
        if not p.is_file():
            raise SystemExit(f"environment_error: mutation {mut['mutation_id']} target {rel} absent")
        p.unlink()
        return
    if op == "create_file":
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(mut["content"], encoding="utf-8")
        return
    if op == "move_file":
        tgt = tree / mut["to"]
        tgt.parent.mkdir(parents=True, exist_ok=True)
        if not p.is_file():
            raise SystemExit(f"environment_error: mutation {mut['mutation_id']} source {rel} absent")
        shutil.move(str(p), str(tgt))
        return
    if not p.is_file():
        raise SystemExit(f"environment_error: mutation {mut['mutation_id']} target {rel} absent")
    body = p.read_text(encoding="utf-8")
    if op == "replace":
        if mut["find"] not in body:
            raise SystemExit(f"environment_error: mutation {mut['mutation_id']} anchor not found in {rel}")
        body = body.replace(mut["find"], mut["replace"], 1)
    elif op == "replace_all":
        if mut["find"] not in body:
            raise SystemExit(f"environment_error: mutation {mut['mutation_id']} anchor not found in {rel}")
        body = body.replace(mut["find"], mut["replace"])
    elif op == "append":
        body = body + mut["append"]
    elif op == "delete_line":
        needle = mut["find"]
        lines = body.splitlines(keepends=True)
        kept = [ln for ln in lines if needle not in ln]
        if len(kept) == len(lines):
            raise SystemExit(f"environment_error: mutation {mut['mutation_id']} anchor not found in {rel}")
        body = "".join(kept)
    else:
        raise SystemExit(f"environment_error: unknown operation {op}")
    p.write_text(body, encoding="utf-8")


def apply_change_set(tree: Path, mut: dict) -> None:
    if "operations" in mut:
        for op in mut["operations"]:
            apply_one(tree, {**op, "mutation_id": mut.get("mutation_id") or mut.get("variant_id")})
        return
    apply_one(tree, mut)


# A pure prohibition is vacuously true on an empty tree. Non-vacuity for these
# three is proven by their own mutations instead.
VACUOUS_ON_EMPTY: set[str] = {"RW-T05", "RW-T31"}


def build_candidate_tree(fixtures: Path, repo_root: Path, dest: Path) -> None:
    copy_tree(repo_root, dest)
    apply_overlay(fixtures / "overlay", dest)
    edits_path = fixtures / "overlay_edits_v1.yml"
    if edits_path.is_file():
        for e in load_yaml_strict(edits_path).get("edits", []):
            apply_one(dest, {**e, "mutation_id": e.get("edit_id", "edit")})
    ensure_git(dest)


def ensure_git(dest: Path) -> None:
    env_args = ["-c", "user.email=stage04@local", "-c", "user.name=stage04"]
    for argv in (["init", "-q"], ["add", "-A"], [*env_args, "commit", "-q", "-m", "fixture"]):
        subprocess.run(["git", *argv], cwd=str(dest), capture_output=True, timeout=900, check=False)


def cmd_selftest(here: Path, repo_root: Path, as_json: bool) -> int:
    fixtures = here.parent / "fixtures"
    muts_path = fixtures / "mutations_v3.yml"
    if not muts_path.is_file():
        print(f"environment_error: {muts_path} not found")
        return 2
    mset = load_yaml_strict(muts_path)
    mutations = mset.get("mutations", [])
    conforming = mset.get("conforming_variants", [])

    report: dict[str, Any] = {
        "positive": None,
        "negative": [],
        "conforming": [],
        "boundary": [],
    }
    rc = 0

    master_dir = tempfile.TemporaryDirectory()
    master = Path(master_dir.name) / "candidate"
    build_candidate_tree(fixtures, repo_root, master)

    def clone(dest: Path) -> None:
        shutil.copytree(master, dest, symlinks=True)

    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / "good"
        clone(good)
        failed, rows = run_acceptance(good)
        report["positive"] = {
            "passed": len(rows) - failed,
            "total": len(rows),
            "red": sorted(r["test_id"] for r in rows if not r["passed"]),
            "detail": [f"{r['test_id']}: {r['detail']}" for r in rows if not r["passed"]][:8],
        }
        if failed:
            rc = 1

    for mut in mutations:
        with tempfile.TemporaryDirectory() as td:
            tree = Path(td) / "mut"
            clone(tree)
            try:
                apply_change_set(tree, mut)
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
            report["negative"].append(
                {
                    "mutation_id": mut["mutation_id"],
                    "target_check": target,
                    "closes": mut.get("closes"),
                    "killed": killed,
                    "collateral": sorted(red - {target}),
                    "ok": killed,
                }
            )
            if not killed:
                rc = 1

    # conforming variants: legitimate alternative implementations that the
    # independent review showed the v1 package would have rejected.
    for var in conforming:
        with tempfile.TemporaryDirectory() as td:
            tree = Path(td) / "conf"
            clone(tree)
            try:
                apply_change_set(tree, var)
            except SystemExit as exc:
                report["conforming"].append(
                    {"variant_id": var["variant_id"], "ok": False, "detail": str(exc)}
                )
                rc = 1
                continue
            failed, rows = run_acceptance(tree)
            red = sorted(r["test_id"] for r in rows if not r["passed"])
            report["conforming"].append(
                {
                    "variant_id": var["variant_id"],
                    "closes": var.get("closes"),
                    "green": len(rows) - failed,
                    "total": len(rows),
                    "red": red,
                    "detail": [f"{r['test_id']}: {r['detail']}" for r in rows if not r["passed"]][:4],
                    "ok": failed == 0,
                }
            )
            if failed:
                rc = 1

    with tempfile.TemporaryDirectory() as td:
        empty = Path(td) / "empty"
        empty.mkdir()
        failed, rows = run_acceptance(empty)
        green = sorted(r["test_id"] for r in rows if r["passed"])
        ok = set(green) == VACUOUS_ON_EMPTY
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
        clone(partial)
        m = Tree(partial).mech()
        shutil.rmtree(partial / f"{BOOT_PARENT}/{m}", ignore_errors=True)
        for f in (partial / REGISTRY_DIR).glob(f"{m}_v*.yml"):
            f.unlink()
        _, rows = run_acceptance(partial)
        red = {r["test_id"] for r in rows if not r["passed"]}
        need = {"RW-T28", "RW-T29", "RW-T34", "RW-T37", "RW-T38", "RW-T39", "RW-T40", "RW-T41", "RW-T42"}
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
        print(f"positive   candidate tree: {pos['passed']}/{pos['total']} green" + (f"  RED={pos['red']}" if pos["red"] else ""))
        for d in pos.get("detail", []):
            print(f"    {d}")
        killed = sum(1 for r in report["negative"] if r.get("killed"))
        print(f"negative   mutations killed: {killed}/{len(report['negative'])}")
        for r in report["negative"]:
            if not r.get("ok"):
                print(f"  - NOT KILLED {r['mutation_id']} -> {r.get('target_check')} {r.get('detail','')}")
        okc = sum(1 for r in report["conforming"] if r.get("ok"))
        print(f"conforming variants green: {okc}/{len(report['conforming'])}")
        for r in report["conforming"]:
            if not r.get("ok"):
                print(f"  - REJECTED CONFORMING {r['variant_id']} red={r.get('red')}")
                for d in r.get("detail", []):
                    print(f"      {d}")
        for b in report["boundary"]:
            print(f"boundary   {b['probe']}: {'ok' if b['ok'] else 'FAILED'}")
            if not b["ok"]:
                print(f"    {b}")
    print("SELFTEST " + ("PASS" if rc == 0 else "FAIL"))
    master_dir.cleanup()
    return rc


# --------------------------------------------------------------------------
# package validation
# --------------------------------------------------------------------------


def cmd_package(run_root: Path) -> int:
    pkg_path = run_root / "04_测试生成/04_tests.yml"
    if not pkg_path.is_file():
        print(f"missing: {pkg_path}")
        return 1
    try:
        pkg = load_yaml_strict(pkg_path)
    except Exception as exc:  # noqa: BLE001
        print(f"unparseable 04_tests.yml: {type(exc).__name__}: {exc}")
        return 1

    problems: list[str] = []
    for field in (
        "schema_version",
        "run_id",
        "stage_id",
        "artifact_kind",
        "artifact_version",
        "status",
        "input_refs",
        "deliberation_receipt",
        "payload",
    ):
        if field not in pkg:
            problems.append(f"missing required artifact field {field}")
    if pkg.get("artifact_kind") != "frozen_test_package":
        problems.append("artifact_kind must be frozen_test_package")
    if pkg.get("stage_id") != "workflow_stage_04_test_generation":
        problems.append("stage_id mismatch")
    if not isinstance(pkg.get("artifact_version"), int) or pkg["artifact_version"] < 2:
        problems.append("artifact_version must be an integer >= 2 for the corrected package")

    for ref in pkg.get("input_refs") or []:
        p = run_root / str(ref.get("path"))
        if not p.is_file():
            problems.append(f"input_ref missing on disk: {ref.get('path')}")
            continue
        got = sha256_file(p)
        if got != ref.get("sha256"):
            problems.append(f"input_ref sha mismatch {ref.get('path')}: {got} != {ref.get('sha256')}")
    for ref in pkg.get("supporting_refs") or []:
        p = run_root / str(ref.get("path"))
        if not p.is_file():
            problems.append(f"supporting_ref missing on disk: {ref.get('path')}")
        elif sha256_file(p) != ref.get("sha256"):
            problems.append(f"supporting_ref sha mismatch {ref.get('path')}")

    payload = pkg.get("payload") or {}
    tests = payload.get("tests") or []
    if payload.get("frozen") is not True:
        problems.append("payload.frozen must be true")
    if not payload.get("freeze_authorization_ref"):
        problems.append("payload.freeze_authorization_ref missing")

    ids = [x.get("test_id") for x in tests]
    if len(ids) != len(set(ids)):
        problems.append("duplicate test_id")
    declared = set(CHECKS)
    if set(ids) != declared:
        problems.append(
            f"frozen ids differ from implemented checks: only_in_yaml={sorted(set(ids)-declared)} "
            f"only_in_code={sorted(declared-set(ids))}"
        )
    for x in tests:
        for f in (
            "test_id",
            "kind",
            "title",
            "success_criterion_ids",
            "evidence_claim_ids",
            "measurement",
            "pass_condition",
            "can_fail",
            "fails_when",
        ):
            if f not in x:
                problems.append(f"{x.get('test_id')}: missing {f}")
        if x.get("kind") not in ("positive", "negative", "boundary"):
            problems.append(f"{x.get('test_id')}: bad kind")
        if x.get("can_fail") is not True:
            problems.append(f"{x.get('test_id')}: can_fail must be true")
        if not x.get("evidence_claim_ids"):
            problems.append(f"{x.get('test_id')}: no evidence claim binding")
        if not x.get("success_criterion_ids"):
            problems.append(f"{x.get('test_id')}: no A success-criterion binding")

    # every accepted blocker must be visibly closed by the package itself
    closed = set()
    for x in tests:
        for b in x.get("closes") or []:
            closed.add(b)
    for b in (pkg.get("correction_round") or {}).get("closes") or []:
        closed.add(b)
    required_blockers = {f"ST04-IR-00{i}" for i in range(1, 7)} | {
        f"ST04-V2-IR-00{i}" for i in range(1, 7)
    }
    missing_blockers = sorted(required_blockers - closed)
    if missing_blockers:
        problems.append(f"accepted blockers not bound to any test: {missing_blockers}")

    body = {k: v for k, v in payload.items() if k != "test_package_sha256"}
    digest = normalized_sha256(body)
    if digest != payload.get("test_package_sha256"):
        problems.append(f"test_package_sha256 mismatch: computed {digest}")

    if problems:
        for p in problems:
            print(f"FAIL {p}")
        print(f"package: {len(problems)} problem(s)")
        return 1
    print(f"package: OK ({len(tests)} tests, digest {digest})")
    return 0


def main() -> int:
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="command", required=True)
    p1 = sub.add_parser("package")
    p1.add_argument("run_root", type=Path)
    p2 = sub.add_parser("acceptance")
    p2.add_argument("tree_root", type=Path)
    p2.add_argument("--json", action="store_true")
    p2.add_argument("--expect-red", action="store_true")
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
