"""Behaviour tests for the skill generator and validator (isolated temp repos + the real tree)."""
from pathlib import Path
import shutil
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_skills as gs  # noqa: E402

REPO = Path(__file__).resolve().parents[3]


def mini_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "01_os/05_registry").mkdir(parents=True)
    (root / "01_os/02_boot/m1").mkdir(parents=True)
    (root / "01_os/03_mechanisms/m1").mkdir(parents=True)
    (root / "01_os/03_mechanisms/mechanism_activation").mkdir(parents=True)
    (root / "01_os/03_mechanisms/m1/README.md").write_text("# m1\n", encoding="utf-8")
    (root / "01_os/03_mechanisms/m1/check.py").write_text("print('ok')\n", encoding="utf-8")
    (root / "01_os/02_boot/m1/启动清单_v1.yml").write_text(yaml.safe_dump({
        "load_order": [{"path": "01_os/03_mechanisms/m1/README.md"}],
        "validator": "01_os/03_mechanisms/m1/check.py",
        "commands": {"static": "python 01_os/03_mechanisms/m1/check.py <repo-root>"},
    }, allow_unicode=True), encoding="utf-8")
    (root / "01_os/03_mechanisms/mechanism_activation/机制生效等级与盘点_v1.yml").write_text(
        yaml.safe_dump({"inventory": [{"mechanism_id": "m1", "current_level": "L1_BOOT_VISIBLE"}]}), encoding="utf-8")
    (root / "CORE_MANIFEST.yml").write_text(yaml.safe_dump({"core_owned_paths": [".agents/skills/", ".claude/skills/"]}), encoding="utf-8")
    registry = {
        "output_roots": [".agents/skills", ".claude/skills"],
        "units": [
            {"name": "citystate-os", "title": "入口", "description": "入口描述", "when": "总是",
             "reads": ["CORE_MANIFEST.yml"], "commands": [{"command": "python v.py", "expect": "退出 0"}]},
            {"name": "os-m1", "title": "机制一", "mechanism_id": "m1", "description": "机制一描述：带冒号", "when": "需要时",
             "boot": "01_os/02_boot/m1/启动清单_v1.yml", "startup": ["01_os/03_mechanisms/m1/README.md"],
             "commands": [{"command": "python 01_os/03_mechanisms/m1/check.py .", "expect": "退出 0"},
                          {"command": "python x.py <placeholder>", "expect": "退出 0"}]},
        ],
        "roles": [{"name": "role-x", "title": "角色", "collaboration_role": "execution", "description": "角色描述",
                   "produces": "p", "mode": "m", "must_not": ["n"], "required": ["citystate-os", "os-m1"],
                   "triggered": [], "init_checks": ["citystate-os", "os-m1"]}],
    }
    (root / gs.REGISTRY).write_text(yaml.safe_dump(registry, allow_unicode=True), encoding="utf-8")
    return root


def test_real_repository_skills_are_current():
    files, errors = gs.render_all(REPO)
    assert errors == []
    assert gs.compare(REPO, files) == []
    assert gs.main(["--repo-root", str(REPO), "--check"]) == 0


def test_generation_is_deterministic_and_mirrors_are_identical(tmp_path):
    root = mini_repo(tmp_path)
    first, errors = gs.render_all(root)
    assert errors == []
    second, _ = gs.render_all(root)
    assert first == second
    assert first[".agents/skills/os-m1/SKILL.md"] == first[".claude/skills/os-m1/SKILL.md"]
    body = first[".agents/skills/os-m1/SKILL.md"]
    assert "## 启动必读" in body and "- `01_os/03_mechanisms/m1/README.md`" in body
    assert "## 程序读取" in body and "启动清单_v1.yml" in body        # boot manifest is program tier
    assert "## 入口程序" in body and "check.py" in body              # .py listed as entry point
    head = yaml.safe_load(body.split("---\n")[1])
    assert head["name"] == "os-m1" and "冒号" in head["description"]  # frontmatter stays valid YAML
    role = first[".agents/skills/role-x/SKILL.md"]
    assert "python 01_os/03_mechanisms/m1/check.py ." in role and "<placeholder>" not in role


def test_hand_edit_missing_file_and_stale_directory_are_reported(tmp_path):
    root = mini_repo(tmp_path)
    assert gs.main(["--repo-root", str(root)]) == 0
    assert gs.main(["--repo-root", str(root), "--check"]) == 0
    edited = root / ".claude/skills/os-m1/SKILL.md"
    edited.write_text(edited.read_text(encoding="utf-8") + "hand edit\n", encoding="utf-8")
    (root / ".agents/skills/role-x/SKILL.md").unlink()
    (root / ".agents/skills/old-skill").mkdir()
    files, _ = gs.render_all(root)
    errors = gs.compare(root, files)
    assert "SKILL_FILE_DRIFT:.claude/skills/os-m1/SKILL.md" in errors
    assert "SKILL_FILE_MISSING:.agents/skills/role-x/SKILL.md" in errors
    assert "SKILL_FILE_NOT_GENERATED:.agents/skills/old-skill" in errors
    assert gs.main(["--repo-root", str(root), "--check"]) == 1


def test_registry_errors_fail_closed(tmp_path):
    root = mini_repo(tmp_path)
    (root / "01_os/03_mechanisms/m1/README.md").unlink()
    _, errors = gs.render_all(root)
    assert errors == ["SKILL_BOOT_REF_MISSING:01_os/02_boot/m1/启动清单_v1.yml:01_os/03_mechanisms/m1/README.md"]
    (root / "01_os/03_mechanisms/m1/README.md").write_text("# m1", encoding="utf-8")
    registry = yaml.safe_load((root / gs.REGISTRY).read_text(encoding="utf-8"))
    registry["units"][1]["reads"] = ["01_os/03_mechanisms/m1/extra.md"]
    registry["roles"][0]["required"].append("os-unknown")
    registry["units"][1]["mechanism_id"] = "other"
    (root / gs.REGISTRY).write_text(yaml.safe_dump(registry, allow_unicode=True), encoding="utf-8")
    _, errors = gs.render_all(root)
    assert "SKILL_READ_MISSING:os-m1:01_os/03_mechanisms/m1/extra.md" in errors
    assert "SKILL_ROLE_UNKNOWN_UNIT:role-x:os-unknown" in errors
    assert "SKILL_MECHANISM_WITHOUT_UNIT:m1" in errors


def test_output_root_must_be_core_owned(tmp_path):
    root = mini_repo(tmp_path)
    (root / "CORE_MANIFEST.yml").write_text(yaml.safe_dump({"core_owned_paths": [".agents/skills/"]}), encoding="utf-8")
    _, errors = gs.render_all(root)
    assert "SKILL_ROOT_NOT_CORE_OWNED:.claude/skills/" in errors


def test_untiered_path_fails_closed(tmp_path):
    root = mini_repo(tmp_path)
    (root / "01_os/03_mechanisms/m1/rules.md").write_text("# rules", encoding="utf-8")
    registry = yaml.safe_load((root / gs.REGISTRY).read_text(encoding="utf-8"))
    registry["units"][1]["reads"] = ["01_os/03_mechanisms/m1/rules.md"]
    (root / gs.REGISTRY).write_text(yaml.safe_dump(registry, allow_unicode=True), encoding="utf-8")
    _, errors = gs.render_all(root)
    assert "SKILL_PATH_UNTIERED:os-m1:01_os/03_mechanisms/m1/rules.md" in errors
    registry["units"][1]["on_action"] = [{"when": "写规则时", "reads": ["01_os/03_mechanisms/m1/rules.md"]}]
    (root / gs.REGISTRY).write_text(yaml.safe_dump(registry, allow_unicode=True), encoding="utf-8")
    files, errors = gs.render_all(root)
    assert errors == [] and "写规则时：`01_os/03_mechanisms/m1/rules.md`" in files[".agents/skills/os-m1/SKILL.md"]


def test_command_templates_carry_every_required_option():
    """Each templated python command names every option its --help marks as required."""
    import re
    import subprocess
    registry = yaml.safe_load((REPO / gs.REGISTRY).read_text(encoding="utf-8"))
    checked = 0
    for unit in registry["units"]:
        for item in unit.get("commands", []) or []:
            argv = item["command"].split()
            script = next((a for a in argv if a.endswith(".py")), None)
            if argv[:1] != ["python"] or not script:
                continue
            usage = subprocess.run([sys.executable, "-B", str(REPO / script), "--help"], capture_output=True,
                                   text=True, encoding="utf-8", cwd=REPO).stdout
            head = usage.split(chr(10) * 2, 1)[0]  # the usage block ends at the first blank line
            optional = set(re.findall(r"\[(--[a-z][a-z0-9-]*)", head))
            required = {o for o in re.findall(r"(?<![\[\w-])(--[a-z][a-z0-9-]*)", head) if o not in optional}
            missing = sorted(o for o in required if o not in argv)
            assert not missing, (unit["name"], item["command"], missing)
            checked += 1
    assert checked >= 15
