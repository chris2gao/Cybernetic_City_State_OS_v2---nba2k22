#!/usr/bin/env python3
"""One-off construction step: move the read tiers of every skill unit from skills_v1.yml into
that unit's boot manifest (`read_tiers`), creating a boot for the six units that had none,
then strip the read keys from skills_v1.yml. Run once, before generate_skills.py is changed;
it computes the tiers with the base generator so the tier content is carried over, not re-decided.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
sys.path.insert(0, str(ROOT / "01_os/06_execution/skills"))
import generate_skills as gs  # noqa: E402  (base version)

REG = ROOT / "01_os/05_registry/skills_v1.yml"
NEW_BOOTS = {
    "citystate-os": ("os_entry", "os_entry"),
    "os-task-continuity": ("task_continuity", "prms"),
    "os-task-discipline": ("task_discipline", "task_discipline"),
    "os-publication": ("publication", "publication"),
    "os-tools": ("skills_and_tools", "skills_and_tools"),
    "os-domain-content": ("domain_content", "domain_content"),
}
DETAIL = "01_os/02_boot/os_entry/开发入口_按动作细则_v1.md"
BASIS = "01_os/02_boot/os_entry/入口依据与事故记录_v1.md"
TIER_COMMENT = (
    "# Read tiers (Human decision 2026-11-18, OS-CORE-B0-SPLIT-BOOT-TIERS-20261118-001). The single\n"
    "# place that says what a model reads: startup at role initialization; on_action when the stated\n"
    "# action happens; program = read by validators / runners, a model reads it only to edit it or to\n"
    "# debug a validator failure; optional = startup read that may be absent. .py paths are entry\n"
    "# points and are not tiered. generate_skills.py renders this into the skills; validate_skills.py\n"
    "# fails on a path this manifest names outside every tier. Any load_order in this manifest is\n"
    "# unchanged and remains what the mechanism's own validator consumes. authority_effect: none.\n"
)


def dump(tiers: dict) -> str:
    body = yaml.safe_dump({"read_tiers": tiers}, allow_unicode=True, sort_keys=False, width=1000)
    return TIER_COMMENT + body


def os_entry_tiers() -> dict:
    return {
        "startup": ["AGENT_WORKING_DISCIPLINE.md", "AGENTS.md", "01_os/README.md", "01_os/开发入口与单窗口任务规范_v1.md"],
        "on_action": [
            {"when": "做到开发入口某节标题下写明的动作时（发布、建任务包、测试与证据、审核、completion pointer 等），读该节",
             "reads": [DETAIL]},
            {"when": "要理解、质疑或修改某条 B0 规则时，按规则旁的（依据：…§编号）读对应条目",
             "reads": [BASIS]},
        ],
        "program": ["01_os/02_boot/os_entry/启动清单_v1.yml", "CORE_MANIFEST.yml"],
    }


def unit_tiers(unit: dict) -> dict:
    t = gs.tiers(ROOT, unit)
    out: dict = {}
    if t["startup"]:
        out["startup"] = t["startup"]
    if unit.get("optional_reads"):
        out["optional"] = list(unit["optional_reads"])
    if t["actions"]:
        out["on_action"] = [{"when": w, "reads": r} for w, r in t["actions"]]
    if t["program"]:
        out["program"] = t["program"]
    return out


def main() -> int:
    registry = yaml.safe_load(REG.read_text(encoding="utf-8"))
    for unit in registry["units"]:
        name = unit["name"]
        if name in NEW_BOOTS:
            folder, mechanism = NEW_BOOTS[name]
            boot_rel = f"01_os/02_boot/{folder}/启动清单_v1.yml"
            tiers = os_entry_tiers() if name == "citystate-os" else unit_tiers(unit)
            if name != "citystate-os":
                tiers.setdefault("program", []).insert(0, boot_rel)
            head = (f"schema_version: citystate.read_tiers.boot_manifest.v1\nmechanism_id: {mechanism}\n"
                    "mechanism_version: 1\n"
                    "# Added 2026-11-18 (OS-CORE-B0-SPLIT-BOOT-TIERS-20261118-001) so that every skill unit has\n"
                    "# exactly one boot manifest that says what to read. It loads, it does not authorize.\n"
                    "failure_policy: fail_closed_on_missing_or_partial\nbackground_processes_started: false\n"
                    "authority_effect: none\n")
            path = ROOT / boot_rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(head + dump(tiers), encoding="utf-8", newline="\n")
        else:
            path = ROOT / unit["boot"]
            text = path.read_text(encoding="utf-8")
            if "read_tiers:" in text:
                raise SystemExit(f"ALREADY_MIGRATED:{unit['boot']}")
            path.write_text(text.rstrip("\n") + "\n" + dump(unit_tiers(unit)), encoding="utf-8", newline="\n")

    # strip the read keys from skills_v1.yml units and give the six units their boot
    lines = REG.read_text(encoding="utf-8").split("\n")
    out, skip, current = [], False, None
    for line in lines:
        if line.startswith("  - name: "):
            current = line.split(": ", 1)[1].strip()
        if line.startswith("roles:"):
            current = None
        key = line[4:].split(":", 1)[0] if line.startswith("    ") and not line.startswith("     ") else None
        if current and key is not None:
            skip = key in {"reads", "startup", "on_action", "optional_reads"}
            if key == "when" and current in NEW_BOOTS:
                out.append(line)
                folder = NEW_BOOTS[current][0]
                out.append(f"    boot: 01_os/02_boot/{folder}/启动清单_v1.yml")
                continue
        elif current and line.strip() == "":
            skip = False
        if not skip:
            out.append(line)
    REG.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print("read_tiers_migrated units=%d new_boots=%d" % (len(registry["units"]), len(NEW_BOOTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
