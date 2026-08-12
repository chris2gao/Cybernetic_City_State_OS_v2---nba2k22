#!/usr/bin/env python3
"""Stage 07 independent measurement.
Does NOT import or call verify_model_routing.py or verify_stage04_acceptance.py.
Own strict YAML loader, own reachability computation, own hashing.
"""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
import yaml

ROOT = Path(sys.argv[1]).resolve()
MECH = ROOT / "01_os/03_mechanisms/model_routing"
BOOT = ROOT / "01_os/02_boot/model_routing/启动清单_v1.yml"
REG = ROOT / "01_os/05_registry/model_routing_v1.yml"
ENTRY = ROOT / "01_os/开发入口与单窗口任务规范_v1.md"
PUBAUTH = ROOT / "01_os/05_registry/repository_publisher_authority_v1.yml"
out: dict = {}

class Dup(yaml.SafeLoader):
    pass

def _nodup(loader, node, deep=False):
    seen = {}
    for k, v in node.value:
        key = loader.construct_object(k, deep=deep)
        if key in seen:
            raise ValueError(f"duplicate_key:{key}")
        seen[key] = loader.construct_object(v, deep=deep)
    return seen

Dup.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _nodup)

def load(p: Path):
    return yaml.load(p.read_text(encoding="utf-8"), Loader=Dup)

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rel(p: Path) -> str:
    return str(p.relative_to(ROOT)).replace("\\", "/")

# M1 independent strict parse
m1 = {}
for p in sorted(MECH.rglob("*.yml")) + [BOOT, REG]:
    try:
        load(p); m1[rel(p)] = "strict_parse_ok"
    except Exception as e:
        m1[rel(p)] = f"FAIL:{e}"
out["M1_strict_yaml_parse"] = m1

# M2 source-ref resolvability from the declared mechanism load surface
boot = load(BOOT)
surface = {i["path"] if isinstance(i, dict) else i for i in boot.get("load_order", [])}
surface |= {boot.get("validator"), boot.get("registry"),
            "01_os/02_boot/model_routing/启动清单_v1.yml",
            "01_os/06_execution/boot/model_routing/README.md"}
surface = sorted(x for x in surface if x)
out["M2_load_surface_paths"] = surface
surface_text = "".join((ROOT / r).read_text(encoding="utf-8", errors="replace")
                       for r in surface if (ROOT / r).is_file())

catalog = load(MECH / "模型与产品面目录_v1.yml")
tokens = set()
for e in catalog["entries"]:
    tokens |= {str(t) for t in (e.get("source_refs") or [])}
    for prof in (e.get("parameter_profiles") or []):
        if isinstance(prof, dict):
            tokens |= {str(t) for t in (prof.get("surface_exposure_evidence") or [])}

res = {}
for t in sorted(tokens):
    defined = bool(re.search(rf"^\s*{re.escape(t)}\s*:\s*$", surface_text, re.M))
    res[t] = "defined_in_load_surface" if defined else "opaque_token_no_resolution_entry"
out["M2_source_ref_resolution"] = res
out["M2_canonical_pointer_to_source_index"] = bool(
    re.search(r"证据对齐与冲突消解|source_registry|source_index", surface_text))

recon = ROOT / "01_os/_runs/run-20260811-全局模型能力与可用性机制-001/02_信息收集与提炼/证据对齐与冲突消解_v1.yml"
srcreg = set((load(recon).get("source_registry") or {}).keys()) if recon.is_file() else set()
out["M2_defined_only_in_unregistered_run_evidence"] = sorted(tokens & srcreg)
out["M2_defined_nowhere_at_all"] = sorted(t for t in tokens if t not in srcreg
                                          and res[t] != "defined_in_load_surface")

# M3 registry coverage both directions + does validator ever read registry entries
reg = load(REG)
reg_paths = [e["path"] for e in reg["entries"]]
mech_files = sorted(rel(p) for p in MECH.rglob("*") if p.is_file())

def covered(f: str) -> bool:
    return any((rp.endswith("/**") and f.startswith(rp[:-2])) or rp == f for rp in reg_paths)

out["M3_uncovered_mechanism_files"] = [f for f in mech_files if not covered(f)]
out["M3_registry_paths_missing_on_disk"] = [
    rp for rp in reg_paths if not (ROOT / rp.replace("/**", "")).exists()]
vsrc = (MECH / "实现/verify_model_routing.py").read_text(encoding="utf-8")
out["M3_validator_reads_registry_entries"] = bool(
    re.search(r'registry(\[|\.get\()\s*["\']entries', vsrc))
out["M3_validator_checks_entry_spec_pointer"] = bool(
    re.search(r"开发入口|entry_spec", vsrc))

# M4 entry-spec residue
entry_text = ENTRY.read_text(encoding="utf-8")
out["M4_entry_points_at_mechanism"] = bool(re.search(r"03_mechanisms/model_routing", entry_text))
out["M4_entry_residual_price"] = sorted(set(re.findall(r"\$\d[\d.,]*|每\s*1M\s*token|价格表", entry_text)))
out["M4_entry_residual_model_labels"] = sorted(set(re.findall(
    r"GPT-5\.\d\s*\w*|Gemini 3\.\d Pro|Opus 4\.\d|Sonnet \d|Sol|Terra|Luna", entry_text)))

# M5 hashes
out["M5_publisher_authority_sha256"] = sha(PUBAUTH)
out["M5_mechanism_sha256"] = {rel(p): sha(p) for p in sorted(MECH.rglob("*")) if p.is_file()}

# M6 cost/quota scan over mechanism
banned = re.compile(r"(?<![a-z_])(price|pricing|cost|quota|balance|billing)(?![a-z_])", re.I)
hits = []
for p in sorted(MECH.rglob("*")):
    if p.is_file():
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if banned.search(line):
                hits.append(f"{rel(p)}:{i}:{line.strip()[:110]}")
out["M6_cost_quota_mentions_in_mechanism"] = hits

# M7 catalog identities
out["M7_catalog_identities"] = [
    {"provider": e.get("provider"), "surface_id": e.get("surface_id"),
     "model_label": e.get("model_label"), "registered": e.get("registered"),
     "source_refs": e.get("source_refs")} for e in catalog["entries"]]

sys.stdout.reconfigure(encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=2))
