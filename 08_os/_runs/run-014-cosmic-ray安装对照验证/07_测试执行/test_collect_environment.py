from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).with_name("collect_environment.py")
SPEC = importlib.util.spec_from_file_location("run014_collect_environment", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_cfg(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "pyvenv.cfg"
    path.write_text(content, encoding="utf-8")
    return path


def test_pyvenv_cfg_false_parses_false(tmp_path: Path) -> None:
    cfg = write_cfg(
        tmp_path,
        "home = /usr/bin\nInclude-System-Site-Packages = FALSE\nversion = 3.14.4\n",
    )
    assert MODULE.parse_include_system_site_packages(cfg) is False


def test_pyvenv_cfg_true_parses_true(tmp_path: Path) -> None:
    cfg = write_cfg(tmp_path, "include-system-site-packages=true\n")
    assert MODULE.parse_include_system_site_packages(cfg) is True


@pytest.mark.parametrize(
    "content",
    [
        "home = /usr/bin\n",
        "include-system-site-packages = sometimes\n",
        "include-system-site-packages = false\ninclude-system-site-packages = true\n",
    ],
)
def test_missing_or_unparseable_pyvenv_cfg_value_is_rejected(
    tmp_path: Path, content: str
) -> None:
    cfg = write_cfg(tmp_path, content)
    with pytest.raises(ValueError, match="exactly one parseable"):
        MODULE.parse_include_system_site_packages(cfg)


def test_redaction_is_recursive_and_context_specific() -> None:
    value = {
        "command": ["/runtime/cosmic/bin/python", "/repository/tool.py"],
        "comparison": "/runtime/mutmut/bin/mutmut",
    }
    replacements = [
        ("/runtime/cosmic", "${COSMIC_RAY_VENV}"),
        ("/runtime/mutmut", "${MUTMUT_VENV}"),
        ("/repository", "${REPOSITORY_ROOT}"),
    ]
    assert MODULE.redact(value, replacements) == {
        "command": ["${COSMIC_RAY_VENV}/bin/python", "${REPOSITORY_ROOT}/tool.py"],
        "comparison": "${MUTMUT_VENV}/bin/mutmut",
    }
