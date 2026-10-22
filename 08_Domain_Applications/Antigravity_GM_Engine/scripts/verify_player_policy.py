"""Verify current player-rule guards offline; never attach to or write the game."""
import ast
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from growth_engine import GrowthEngine
from modifier import LeagueModifier


class NoMemoryAccess:
    def __getattr__(self, name):
        raise AssertionError(f"Player edit reached memory before rejection: {name}")


def expect_rejected(action):
    try:
        action()
    except PermissionError:
        return
    raise AssertionError("Forbidden legacy operation was not rejected")


def main():
    policy = json.loads((ROOT / "config/gameplay_policy.json").read_text(encoding="utf-8"))
    assert policy["default_player_edits"] == "FORBIDDEN"
    assert policy["natural_development"] == "GAME_CONTROLLED"
    assert policy["mc_growth_story"]["status"] == "DISABLED_DEFERRED"
    assert not policy["historical_gravity"]["automatic_attribute_changes"]
    draft = policy["historical_draft"]
    span = draft["last_class"] - draft["first_class"] + 1
    calculate_year = lambda count: draft["first_class"] + count % span
    assert [calculate_year(n) for n in (0, 1, span - 1, span)] == [1984, 1985, 2020, 1984]
    reference = policy["historical_gravity"]
    reference_year = reference["historical_anchor_year"] + reference["elapsed_historical_years_at_transition"]
    with tempfile.TemporaryDirectory(prefix="gm_policy_") as temporary:
        database = Path(temporary) / "must_not_exist.sqlite"
        expect_rejected(lambda: GrowthEngine(str(database)))
        assert not database.exists(), "Disabled growth engine created a database"
    detached = object.__new__(GrowthEngine)
    expect_rejected(lambda: detached.simulate_monthly_player_growth([], {}))
    modifier = LeagueModifier(mem=NoMemoryAccess())
    for action in (
        lambda: modifier.set_player_attribute(1, "ATTR_THREE_POINT", 99),
        lambda: modifier.set_player_tendency(1, "TEND_SHOT", 100),
        lambda: modifier.set_signature_package(1, 100),
        lambda: modifier.set_player_personality(1),
    ):
        expect_rejected(action)
    legacy = subprocess.run([sys.executable, str(ROOT / "src/generate_1984_class.py")],
                            capture_output=True, text=True, encoding="utf-8")
    assert legacy.returncode != 0 and "Disabled legacy" in legacy.stderr
    parsed = 0
    for directory in (ROOT / "src", ROOT / "scripts"):
        for path in directory.glob("*.py"):
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            parsed += 1
    print(json.dumps({"policy_id": policy["policy_id"], "draft_cycle_length": span,
                      "historical_reference_year_at_2026": reference_year,
                      "legacy_player_operations_rejected_before_memory": 4,
                      "growth_database_created": False, "legacy_handmade_draft_disabled": True,
                      "python_modules_parsed": parsed}, indent=2))


if __name__ == "__main__":
    main()
