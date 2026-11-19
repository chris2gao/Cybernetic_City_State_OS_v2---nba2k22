#!/usr/bin/env python3
"""Generate the City-State OS skill adapters from 01_os/05_registry/skills_v1.yml.

Each unit and role becomes <root>/<name>/SKILL.md under every output root
(.agents/skills for Codex and Antigravity, .claude/skills for Claude Code). The
files are thin adapters: when to load, which exact paths to read, which commands
to run. Mechanism text is never copied. What to read comes only from each unit's
boot manifest (`read_tiers`); skills_v1.yml holds skill metadata and the role
matrix. Run with --check to compare without writing (that is what
validate_skills.py does).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REGISTRY = "01_os/05_registry/skills_v1.yml"
INVENTORY = "01_os/03_mechanisms/mechanism_activation/机制生效等级与盘点_v1.yml"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
DESCRIPTION_LIMIT = 1024
# Boot keys whose values are not part of the named read set: read_tiers is the tiering itself;
# optional_extensions names another unit's files (context_management -> prms is tiered in the
# task_continuity boot). Command strings elsewhere contain spaces and are never taken as paths.
SKIPPED_BOOT_KEYS = {"optional_extensions", "read_tiers"}
ROOT_FILE_RE = re.compile(r"^[A-Za-z0-9_.-]+\.[A-Za-z0-9]+$")
TIER_KEYS = {"startup", "on_action", "program", "optional"}
# A second source of "what to read" in the registry is what this design removes.
REGISTRY_READ_KEYS = {"reads", "startup", "on_action", "optional_reads", "program"}
ENTRY_UNIT = "citystate-os"
GENERATED_NOTE = (
    "> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml`{boot}。修改来源后运行 "
    "`python -B 01_os/06_execution/skills/generate_skills.py`。"
)


class SkillError(Exception):
    pass


def load_yaml(root: Path, rel: str) -> Any:
    path = root / rel
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise SkillError(f"YAML_LOAD_FAILED:{rel}:{type(exc).__name__}") from exc


def boot_paths(root: Path, boot_rel: str) -> list[str]:
    """Every existing repository file a boot manifest names, in document order."""
    boot = load_yaml(root, boot_rel)
    found: list[str] = []

    def walk(value: Any, key: str | None = None) -> None:
        if key in SKIPPED_BOOT_KEYS:
            return
        if isinstance(value, dict):
            for k, v in value.items():
                walk(v, str(k))
        elif isinstance(value, list):
            for item in value:
                walk(item, key)
        elif isinstance(value, str):
            text = value.strip()
            if " " in text or any(c in text for c in "<*{"):
                return
            if ROOT_FILE_RE.fullmatch(text):  # a repository-root file such as AGENTS.md
                if (root / text).is_file() and text not in found:
                    found.append(text)
                return
            if not text.startswith(("01_os/", ".githooks/")):
                return
            if (root / text).is_file():
                if text not in found:
                    found.append(text)
            elif "." in text.rsplit("/", 1)[-1] and not (root / text).is_dir():
                raise SkillError(f"SKILL_BOOT_REF_MISSING:{boot_rel}:{text}")

    walk(boot)
    if boot_rel not in found:
        found.insert(0, boot_rel)
    return found


def read_tiers(root: Path, boot_rel: str) -> dict[str, Any]:
    """The boot manifest's read_tiers, shape-checked: startup / optional / program are path lists,
    on_action is a list of {when, reads}."""
    boot = load_yaml(root, boot_rel)
    value = boot.get("read_tiers") if isinstance(boot, dict) else None
    if not isinstance(value, dict) or not value:
        raise SkillError(f"SKILL_BOOT_TIERS_MISSING:{boot_rel}")
    if set(value) - TIER_KEYS:
        raise SkillError(f"SKILL_TIER_KEY_UNKNOWN:{boot_rel}:{sorted(set(value) - TIER_KEYS)}")
    for key in ("startup", "optional", "program"):
        items = value.get(key, []) or []
        if not isinstance(items, list) or not all(isinstance(p, str) and p for p in items):
            raise SkillError(f"SKILL_TIER_INVALID:{boot_rel}:{key}")
    actions = value.get("on_action", []) or []
    if not isinstance(actions, list) or not all(
            isinstance(a, dict) and isinstance(a.get("when"), str) and a["when"].strip()
            and isinstance(a.get("reads", []) or [], list)
            and all(isinstance(p, str) and p.strip() for p in a.get("reads", []) or []) for a in actions):
        raise SkillError(f"SKILL_TIER_INVALID:{boot_rel}:on_action")
    tiered = [p for key in ("startup", "optional", "program") for p in value.get(key, []) or []]
    tiered += [p for a in actions for p in a.get("reads", []) or []]
    entry_points = sorted({p for p in tiered if p.endswith(".py")})
    if entry_points:  # .py files are entry points to call, never a read tier
        raise SkillError(f"SKILL_TIER_ENTRY_POINT:{boot_rel}:{entry_points}")
    return value


def entry_paths(root: Path, registry: dict[str, Any]) -> set[str]:
    """B0: the startup tier of the entry unit's boot, already read by every role."""
    unit = next((u for u in registry.get("units", []) if u.get("name") == ENTRY_UNIT), None)
    if not unit or not unit.get("boot"):
        return set()
    return set(read_tiers(root, unit["boot"]).get("startup", []) or [])


def tiers(root: Path, unit: dict[str, Any], b0_set: set[str] | None = None) -> dict[str, Any]:
    """A unit's reads from its boot: startup / optional / on_action / program, plus the boot-named
    paths that are B0 (read by the entry unit) and the .py entry points."""
    boot_rel = unit["boot"]
    value = read_tiers(root, boot_rel)
    named = boot_paths(root, boot_rel)
    b0_set = set() if b0_set is None or unit["name"] == ENTRY_UNIT else b0_set
    startup = list(value.get("startup", []) or [])
    optional = list(value.get("optional", []) or [])
    actions = [(str(a["when"]).strip(), list(a.get("reads", []) or [])) for a in value.get("on_action", []) or []]
    program = list(value.get("program", []) or [])
    # One path may serve several on_action entries (e.g. different sections of one detail file),
    # but it may sit in only one tier, and only once inside any single list.
    lists = [startup, optional, program] + [reads for _, reads in actions]
    tier_sets = [set(startup), set(optional), set(program), {p for _, reads in actions for p in reads}]
    declared = set().union(*tier_sets)
    entry = [p for p in named if p.endswith(".py")]
    b0 = [p for p in named if p in b0_set and p not in declared]
    untiered = [p for p in named if not p.endswith(".py") and p not in declared and p not in b0]
    duplicated = sorted({p for p in declared if sum(p in s for s in tier_sets) > 1}
                        | {p for items in lists for p in items if items.count(p) > 1})
    return {"startup": startup, "optional": optional, "actions": actions, "program": program, "b0": b0,
            "entry": entry, "untiered": untiered, "duplicated": duplicated}


def read_lists(root: Path, unit: dict[str, Any], b0_set: set[str] | None = None) -> tuple[list[str], list[str]]:
    """Every path a unit requires to exist (all tiers except optional) and its entry points."""
    tier = tiers(root, unit, b0_set)
    must: list[str] = []
    for rel in tier["startup"] + [p for _, reads in tier["actions"] for p in reads] + tier["program"] + tier["b0"]:
        if rel not in must:
            must.append(rel)
    return must, tier["entry"]


def startup_bytes(root: Path, unit: dict[str, Any]) -> int:
    return sum((root / p).stat().st_size for p in tiers(root, unit)["startup"] if (root / p).is_file())


def inventory_levels(root: Path) -> dict[str, str]:
    try:
        inv = load_yaml(root, INVENTORY)
    except SkillError:
        return {}
    return {str(e.get("mechanism_id")): str(e.get("current_level")) for e in inv.get("inventory", []) if isinstance(e, dict)}


def one_line(text: Any) -> str:
    """Fold whitespace; YAML folding leaves a space between two CJK characters, drop it."""
    folded = " ".join(str(text).split())
    return re.sub(r"(?<=[^\x00-\x7F])\s+(?=[^\x00-\x7F])", "", folded)


def frontmatter(name: str, description: str) -> str:
    # JSON string syntax is valid YAML and survives colons, quotes and '#'.
    return f"---\nname: {name}\ndescription: {json.dumps(one_line(description), ensure_ascii=False)}\n---\n"


def init_commands(units: dict[str, dict[str, Any]], names: list[str]) -> list[str]:
    commands: list[str] = []
    for name in names:
        for item in units[name].get("commands", []) or []:
            command = str(item.get("command", ""))
            if "<" in command or "退出 0" not in str(item.get("expect", "")):
                continue
            if command not in commands:
                commands.append(command)
    return commands


def render_unit(root: Path, unit: dict[str, Any], registry: dict[str, Any], levels: dict[str, str]) -> str:
    tier = tiers(root, unit, entry_paths(root, registry))
    entry = tier["entry"]
    level = levels.get(str(unit.get("mechanism_id", "")), "")
    title = unit["title"] + (f"（{level}）" if level else "")
    boot_note = f" + `{unit['boot']}`（读取分层 `read_tiers`）"
    lines = [frontmatter(unit["name"], unit["description"]), f"# {title}", "", GENERATED_NOTE.format(boot=boot_note), ""]
    lines += ["## 何时加载", "", str(unit.get("when", "")).strip(), ""]
    roles_req = [r["title"] for r in registry["roles"] if unit["name"] in r.get("required", [])]
    roles_trig = [r["title"] for r in registry["roles"] if unit["name"] in [t["unit"] for t in r.get("triggered", [])]]
    lines += ["适用角色：初始化必载 = " + ("、".join(roles_req) or "无") + "；按触发加载 = " + ("、".join(roles_trig) or "无"), ""]
    if tier["startup"]:
        size = sum((root / p).stat().st_size for p in tier["startup"]) // 1024
        lines += [f"## 启动必读（角色初始化时读完，约 {size} KB）", ""] + [f"- `{p}`" for p in tier["startup"]] + [""]
    optional = tier["optional"]
    if optional:
        lines += ["## 有则必读（初始化时读；不存在时在回执里写明缺失，不算失败）", ""] + [f"- `{p}`" for p in optional] + [""]
    if tier["actions"]:
        lines += ["## 按动作读取（做到这一步时再读）", ""]
        for when, reads in tier["actions"]:
            lines.append(f"- {when}：" + ("、".join(f"`{p}`" for p in reads) if reads else "按目录条目只读当前需要的那几份"))
        lines.append("")
    if tier["b0"]:
        lines += ["## 已由 citystate-os 加载（B0，不必重读）", ""] + [f"- `{p}`" for p in tier["b0"]] + [""]
    if tier["program"]:
        lines += ["## 程序读取（validator / runner 读取；只在修改这些文件或排查校验失败时读）", ""] + [f"- `{p}`" for p in tier["program"]] + [""]
    if entry:
        lines += ["## 入口程序（调用即可，不必通读源码）", ""] + [f"- `{p}`" for p in entry] + [""]
    commands = unit.get("commands", []) or []
    if commands:
        lines += ["## 命令", ""]
        for item in commands:
            lines.append(f"- `{item['command']}` → {item.get('expect', '')}")
        lines.append("")
    boundaries = unit.get("boundaries", []) or []
    if boundaries:
        lines += ["## 边界与停止", ""] + [f"- {b}" for b in boundaries] + [""]
    if unit["name"] == "citystate-os":
        lines += render_catalog(root, registry, levels)
    return "\n".join(lines).rstrip() + "\n"


def render_catalog(root: Path, registry: dict[str, Any], levels: dict[str, str]) -> list[str]:
    roles = registry["roles"]
    out = ["## Core OS 机制单元目录", "",
           "| Skill | 内容 | 生效等级 | 启动读取 | " + " | ".join(r["title"] for r in roles) + " |",
           "|---|---|---|---|" + "---|" * len(roles)]
    for unit in registry["units"]:
        cells = []
        for role in roles:
            if unit["name"] in role.get("required", []):
                cells.append("必")
            elif unit["name"] in [t["unit"] for t in role.get("triggered", [])]:
                cells.append("触")
            else:
                cells.append("—")
        level = levels.get(str(unit.get("mechanism_id", "")), "—")
        size = startup_bytes(root, unit) // 1024
        out.append(f"| `{unit['name']}` | {unit['title']} | {level} | {size} KB | " + " | ".join(cells) + " |")
    l4 = sorted(m for m, lv in levels.items() if lv == "L4_E2E_ADVERSARIALLY_VERIFIED")
    state = ("达到 L4 的机制：" + "、".join(l4)) if l4 else "当前没有任何机制达到 L4"
    out += ["", "图例：必 = 角色初始化时加载；触 = 命中触发条件时加载；— = 不加载。"
            f"只有独立验收过的 L4 才可称 operationally_active；{state}。", ""]
    unit_by_name = {u["name"]: u for u in registry["units"]}
    out += ["各角色初始化的启动读取量（启动必读合计，不含按动作读取与程序读取）：", ""]
    for role in roles:
        total = sum(startup_bytes(root, unit_by_name[n]) for n in role.get("required", []))
        out.append(f"- {role['title']}：约 {total // 1024} KB")
    out += [""]
    out += ["## 角色初始化", "",
            "Human 说明你的角色后，调用对应的角色 skill，它会加载其余全部必载 skill：", ""]
    for role in roles:
        out.append(f"- {role['title']}（`{role['collaboration_role']}`）→ `{role['name']}`")
    out += ["", "没有说明角色时，先问 Human 角色是什么，再初始化。", ""]
    regs = sorted(p.name for p in (root / "01_os/05_registry").glob("*.yml"))
    out += ["## 登记文件（系统结构的权威描述）", ""] + [f"- `01_os/05_registry/{n}`" for n in regs] + [""]
    return out


def render_role(root: Path, role: dict[str, Any], units: dict[str, dict[str, Any]]) -> str:
    lines = [frontmatter(role["name"], role["description"]), f"# 角色：{role['title']}（`{role['collaboration_role']}`）", "",
             GENERATED_NOTE.format(boot=""), ""]
    lines += [f"- 产出：{role['produces']}", f"- 模式：{role['mode']}", "- 不得："] + [f"  - {m}" for m in role.get("must_not", [])] + [""]
    lines += ["## 初始化（按顺序全部完成，再开始工作）", "",
              "1. 确认仓库、分支、HEAD、Human 目标与当前任务；有任务包就读任务包，有未完成任务就按 `os-task-continuity` 从 run 或简报库恢复。",
              "2. 依次读取下列 skill 文件（与本文件同级目录），并读完每个 skill 的“启动必读”与“有则必读”；"
              "“按动作读取”做到那一步时再读，“程序读取”不主动读：", ""]
    for name in role["required"]:
        lines.append(f"   - `../{name}/SKILL.md` — {units[name]['title']}")
    checks = init_commands(units, role.get("init_checks", []))
    lines += ["", "3. 运行初始化检查（只读，期望全部退出 0）：", ""] + [f"   - `{c}`" for c in checks]
    lines += ["", "4. 输出角色初始化回执，然后开始工作：", "", "```text", "ROLE_INIT_RECEIPT",
              f"role: {role['name']}", "repository / branch / head: <实测>", "human_objective: <一句话>",
              "skills_loaded: <上面第 2 步的 skill 名>", "paths_read: <启动必读实际读取的路径数与字节数，及缺失的“有则必读”项>",
              "validators: <命令 = 退出码>", "gaps: <未读、失败或与预期不符之处；没有就写 none>", "```", ""]
    triggered = role.get("triggered", []) or []
    if triggered:
        lines += ["## 工作中按触发加载", ""] + [f"- `../{t['unit']}/SKILL.md`：{t['when']}" for t in triggered] + [""]
    lines += ["## 临时工作台", "",
              "- 聊天窗口只是工作台；重要决定、结论与证据在形成时落进仓库（run 记录）或简报库。",
              "- 一个窗口承担一个任务还是一个系列由 Human 决定；任务边界与纪律按 `os-task-discipline`。",
              "- 发现自己偏离了已审步骤、加了多余检查或误判 Done，按 `os-task-orchestration` 主动自报（AGENT_SELF_REPORT）。", ""]
    return "\n".join(lines).rstrip() + "\n"


def check_registry(root: Path, registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    units = registry.get("units") or []
    roles = registry.get("roles") or []
    names = [u.get("name") for u in units] + [r.get("name") for r in roles]
    for name in names:
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            errors.append(f"SKILL_NAME_INVALID:{name}")
    if len(set(names)) != len(names):
        errors.append("SKILL_NAME_DUPLICATE")
    unit_names = {u.get("name") for u in units}
    for item in units + roles:
        if len(one_line(item.get("description", ""))) > DESCRIPTION_LIMIT or not item.get("description"):
            errors.append(f"SKILL_DESCRIPTION_INVALID:{item.get('name')}")
    try:
        b0_set = entry_paths(root, registry)
    except SkillError as exc:
        errors.append(str(exc))
        b0_set = set()
    if ENTRY_UNIT not in unit_names:
        errors.append(f"SKILL_ENTRY_UNIT_MISSING:{ENTRY_UNIT}")
    for unit in units:
        second_source = sorted(REGISTRY_READ_KEYS & set(unit))
        if second_source:
            errors.append(f"SKILL_REGISTRY_READ_KEY:{unit.get('name')}:{second_source}")
        if not unit.get("boot"):
            errors.append(f"SKILL_UNIT_WITHOUT_BOOT:{unit.get('name')}")
            continue
        if not (root / unit["boot"]).is_file():
            errors.append(f"SKILL_BOOT_MISSING:{unit['name']}:{unit['boot']}")
            continue
        try:
            tier = tiers(root, unit, b0_set)
            must, entry = read_lists(root, unit, b0_set)
        except SkillError as exc:
            errors.append(f"{exc}")
            continue
        for rel in tier["untiered"]:
            errors.append(f"SKILL_PATH_UNTIERED:{unit['name']}:{rel}")
        for rel in tier["duplicated"]:
            errors.append(f"SKILL_PATH_MULTI_TIERED:{unit['name']}:{rel}")
        for rel in dict.fromkeys(must + entry + tier["untiered"]):
            if not (root / rel).is_file():
                errors.append(f"SKILL_READ_MISSING:{unit['name']}:{rel}")
    for role in roles:
        for ref in list(role.get("required", [])) + [t.get("unit") for t in role.get("triggered", [])] + list(role.get("init_checks", [])):
            if ref not in unit_names:
                errors.append(f"SKILL_ROLE_UNKNOWN_UNIT:{role.get('name')}:{ref}")
        if "citystate-os" not in role.get("required", []):
            errors.append(f"SKILL_ROLE_WITHOUT_ENTRY:{role.get('name')}")
    mapped = {str(u.get("mechanism_id")) for u in units if u.get("mechanism_id")}
    for mechanism_id in inventory_levels(root):
        if mechanism_id not in mapped:
            errors.append(f"SKILL_MECHANISM_WITHOUT_UNIT:{mechanism_id}")
    try:
        manifest = load_yaml(root, "CORE_MANIFEST.yml")
        owned = set(manifest.get("core_owned_paths", []))
        for out_root in registry.get("output_roots", []):
            if f"{out_root}/" not in owned:
                errors.append(f"SKILL_ROOT_NOT_CORE_OWNED:{out_root}/")
    except SkillError as exc:
        errors.append(str(exc))
    return errors


def budget_report(root: Path, registry: dict[str, Any]) -> list[str]:
    """Report-only: units whose startup tier exceeds startup_budget_bytes."""
    limit = registry.get("startup_budget_bytes")
    exempt = set(registry.get("startup_budget_exempt", []) or [])
    if not isinstance(limit, int):
        return []
    out = []
    for unit in registry.get("units", []):
        if unit["name"] in exempt:
            continue
        size = startup_bytes(root, unit)
        if size > limit:
            out.append(f"SKILL_STARTUP_OVER_BUDGET(report-only):{unit['name']}:{size}>{limit}")
    return out


def render_all(root: Path) -> tuple[dict[str, str], list[str]]:
    registry = load_yaml(root, REGISTRY)
    if not isinstance(registry, dict):
        raise SkillError("SKILL_REGISTRY_INVALID")
    errors = check_registry(root, registry)
    if errors:
        return {}, errors
    levels = inventory_levels(root)
    units = {u["name"]: u for u in registry["units"]}
    files: dict[str, str] = {}
    bodies = {u["name"]: render_unit(root, u, registry, levels) for u in registry["units"]}
    bodies.update({r["name"]: render_role(root, r, units) for r in registry["roles"]})
    for out_root in registry["output_roots"]:
        for name, body in bodies.items():
            files[f"{out_root}/{name}/SKILL.md"] = body
    return files, []


def compare(root: Path, files: dict[str, str]) -> list[str]:
    registry = load_yaml(root, REGISTRY)
    errors = []
    for rel, body in files.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"SKILL_FILE_MISSING:{rel}")
        elif path.read_bytes() != body.encode("utf-8"):
            errors.append(f"SKILL_FILE_DRIFT:{rel}")
    for out_root in registry.get("output_roots", []):
        base = root / out_root
        if base.is_dir():
            for skill in sorted(p for p in base.iterdir()):
                rel = f"{out_root}/{skill.name}/SKILL.md"
                if rel not in files:
                    errors.append(f"SKILL_FILE_NOT_GENERATED:{out_root}/{skill.name}")
    return errors


def write(root: Path, files: dict[str, str]) -> None:
    for rel, body in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body.encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--check", action="store_true", help="compare only; write nothing")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    try:
        files, errors = render_all(root)
        if not errors and args.check:
            errors = compare(root, files)
    except SkillError as exc:
        errors = [str(exc)]
    if errors:
        for error in errors:
            print(error)
        return 1
    for note in budget_report(root, load_yaml(root, REGISTRY)):
        print(note)
    if not args.check:
        write(root, files)
        print(f"skills_generated files={len(files)}")
    else:
        print(f"skills_valid files={len(files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
