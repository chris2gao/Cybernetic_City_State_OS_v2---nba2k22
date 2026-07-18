import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROLE_FILES = ["core.md", "planner.md", "executor.md", "reviewer.md", "teacher.md"]
PROFILE_MAP = {
    "backend_executor.md": "executor.md",
    "foreground_planner.md": "planner.md",
    "foreground_independent_reviewer.md": "reviewer.md",
    "math_mentor_teacher.md": "teacher.md",
}
REQUIRED_FIELDS = (
    "source_ref",
    "last_verified",
    "expires_or_invalidation",
    "authority",
)


def entries(text: str) -> list[str]:
    return [part for part in re.split(r"(?m)^### ", text)[1:] if part.strip()]


def field(section: str, name: str) -> str | None:
    match = re.search(rf"(?m)^- {re.escape(name)}:\s*(.+)$", section)
    return match.group(1).strip() if match else None


def test_every_role_memory_entry_has_routing_fields() -> None:
    for name in ROLE_FILES:
        text = (ROOT / name).read_text(encoding="utf-8")
        sections = entries(text)
        assert sections, f"{name} has no memory entries"
        for section in sections:
            for required in REQUIRED_FIELDS:
                assert field(section, required), f"{name} entry lacks {required}"
            assert field(section, "authority") == "`routing_only`"
            assert re.fullmatch(r"`\d{4}-\d{2}-\d{2}`", field(section, "last_verified") or "")


def test_each_load_profile_routes_to_core_and_exact_role_memory() -> None:
    profiles = ROOT.parent / "load_profiles"
    for profile, role_file in PROFILE_MAP.items():
        text = (profiles / profile).read_text(encoding="utf-8")
        assert "`.ai/role_memory/core.md`" in text
        assert f"`.ai/role_memory/{role_file}`" in text


def test_index_declares_non_authorizing_write_rules() -> None:
    text = (ROOT / "index.md").read_text(encoding="utf-8")
    assert "authority: routing_only" in text
    assert "Never store task state, approval, Human gates" in text
    assert "Memory points to evidence" in text
