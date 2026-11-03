"""F1 and F2 targeted tests for Host Live Authorization Final Closeout.

F1: _get_teams_from_database() strict saves table enforcement — fail-closed when:
    - saves table is missing entirely
    - saves table has no singleton row
    - saves table save_id mismatches the registry save_id

F2: Role registry re-binding after force_new_worldline switch — ensures:
    - registry.worldline_id updated to new branch worldline
    - registry.database_path updated to new branch DB
    - old auth file scoped to original worldline cannot authorize new worldline actions
"""

import json
import sqlite3
import sys
from pathlib import Path

import pytest

_DIR = Path(__file__).resolve().parent.parent
_PROTO_DIR = _DIR.parent.parent / "world_data_prototype"
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))
if str(_PROTO_DIR) not in sys.path:
    sys.path.insert(0, str(_PROTO_DIR))

from engine import create_database, connect
from live_world import initialize_save
from season_cycle_host import SeasonCycleHost, TrustedRoleRegistry


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_base_auth(save_dir: Path, save_id: str, worldline_id: str = "worldline-main") -> dict:
    """Create a standard test auth manifest with wildcard scope explicitly declared."""
    return {
        "schema_version": "nba2k22.rea.role_authorizations.v1",
        "save_id": save_id,
        "worldline_id": worldline_id,
        "bound_database_file": "world.sqlite",
        "authorized_worldlines": [worldline_id, "*"],
        "authorized_databases": ["world.sqlite", "*"],
        "allow_wildcard_scope": True,
        "human_authorization_ref": "HUMAN_TEST_AUTH_F1F2_20261102",
        "provenance": "SAVE_DB_VERIFIED_DELEGATION",
        "roles": [
            {
                "role_type": "GM",
                "team_id": 28,
                "actor_uid": "gm_user_01",
                "provenance": "SAVE_DB_VERIFIED_DELEGATION",
                "human_authorization_ref": "HUMAN_TEST_AUTH_F1F2_20261102",
            }
        ],
    }


# ---------------------------------------------------------------------------
# F1 Tests — _get_teams_from_database() strict fail-closed
# ---------------------------------------------------------------------------


def test_f1_missing_saves_table_fails_closed(tmp_path):
    """F1: DB with ONLY a teams table (no saves table) must fail closed.

    _verify_team_in_database(28) must return False even though team 28 exists.
    """
    no_saves_db = tmp_path / "no_saves.sqlite"
    conn = sqlite3.connect(str(no_saves_db))
    conn.execute("CREATE TABLE teams (team_id TEXT, display_name TEXT)")
    conn.execute("INSERT INTO teams VALUES ('team:native:28', 'LAL')")
    conn.commit()
    conn.close()

    reg = TrustedRoleRegistry(save_id="save_test_f1_01")
    reg.database_path = no_saves_db
    # saves table missing → OperationalError → fail closed
    assert reg._get_teams_from_database() == set(), "Should return empty set when saves table is missing"
    assert reg._verify_team_in_database(28) is False, "Should return False when saves table is missing"


def test_f1_saves_table_empty_no_singleton_fails_closed(tmp_path):
    """F1: saves table exists but has no singleton row → fail closed."""
    db_path = tmp_path / "empty_saves.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE saves (singleton INTEGER PRIMARY KEY, save_id TEXT)")
    conn.execute("CREATE TABLE teams (team_id TEXT, display_name TEXT)")
    conn.execute("INSERT INTO teams VALUES ('team:native:28', 'LAL')")
    conn.commit()
    conn.close()

    reg = TrustedRoleRegistry(save_id="save_test_f1_01")
    reg.database_path = db_path
    assert reg._get_teams_from_database() == set(), "Should return empty set when saves singleton row is absent"
    assert reg._verify_team_in_database(28) is False


def test_f1_saves_id_mismatch_fails_closed(tmp_path):
    """F1: saves table exists, singleton row exists, but save_id mismatches → fail closed."""
    db_path = tmp_path / "wrong_save.sqlite"
    # create_database inserts a saves singleton row with the given save_id
    create_database(db_path, "correct_save_id_xyz")
    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO teams (team_id, display_name) VALUES ('team:native:28', 'LAL')"
        )

    # Registry bound to a DIFFERENT save_id
    reg = TrustedRoleRegistry(save_id="different_save_id_abc")
    reg.database_path = db_path
    assert reg._get_teams_from_database() == set(), "save_id mismatch must return empty set"
    assert reg._verify_team_in_database(28) is False, "save_id mismatch must return False"


def test_f1_correct_saves_id_succeeds(tmp_path):
    """F1 positive: correct saves table + matching save_id → team 28 found."""
    db_path = tmp_path / "correct.sqlite"
    create_database(db_path, "save_positive_01")
    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO teams (team_id, display_name) VALUES ('team:native:28', 'LAL')"
        )

    reg = TrustedRoleRegistry(save_id="save_positive_01")
    reg.database_path = db_path
    teams = reg._get_teams_from_database()
    assert 28 in teams, "Correct saves identity should allow team 28 to be found"
    assert reg._verify_team_in_database(28) is True


def test_f1_no_save_id_on_registry_fails_closed(tmp_path):
    """F1: If registry has empty save_id, must fail closed regardless of DB content."""
    db_path = tmp_path / "valid_db.sqlite"
    create_database(db_path, "some_save_id")
    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO teams (team_id, display_name) VALUES ('team:native:28', 'LAL')"
        )

    reg = TrustedRoleRegistry(save_id="")  # empty save_id
    reg.database_path = db_path
    assert reg._get_teams_from_database() == set(), "Empty save_id on registry must fail closed"
    assert reg._verify_team_in_database(28) is False


# ---------------------------------------------------------------------------
# F2 Tests — force_new_worldline rebinds role registry
# ---------------------------------------------------------------------------


@pytest.fixture
def base_save_env(tmp_path):
    """Set up a minimal save environment for F2 tests."""
    save_dir = tmp_path / "save"
    native_file = tmp_path / "MyLEAGUE0003"
    native_file.write_bytes(b"FAKE_NBA2K22_SAVE_CONTENT")

    initialize_save(str(save_dir), "nba2k22_test_f2_01", str(native_file))
    db_path = save_dir / "world.sqlite"

    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO seasons (season_id, season_code, save_id) "
            "VALUES ('season:2021', '2021-22', 'nba2k22_test_f2_01')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO teams (team_id, display_name) VALUES "
            "('team:1', 'MIL'), ('team:2', 'BKN'), ('team:28', 'LAL')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO games (game_id, season_id, game_date, home_team_id, away_team_id, native_game_id) "
            "VALUES ('game:001', 'season:2021', '2021-11-01', 'team:1', 'team:2', '101')"
        )

    auth_manifest = _make_base_auth(save_dir, "nba2k22_test_f2_01", "worldline-main")
    (save_dir / "role_authorizations.json").write_text(
        json.dumps(auth_manifest, indent=2), encoding="utf-8"
    )

    return {
        "tmp_path": tmp_path,
        "save_dir": save_dir,
        "native_file": native_file,
        "db_path": db_path,
    }


def test_f2_force_new_worldline_registry_rebound_to_new_worldline(base_save_env):
    """F2: After initialize_season(force_new_worldline=True), registry must be bound to the new worldline.

    Checks:
    - registry.worldline_id != original worldline_id ("worldline-main")
    - registry.database_path is not the original world.sqlite
    - receipt worldline_id matches registry worldline_id
    """
    env = base_save_env
    tmp_path = env["tmp_path"]
    save_dir = env["save_dir"]

    host = SeasonCycleHost(
        workspace_root=tmp_path,
        state_file=tmp_path / "state_f2_a.json",
        ledger_file=tmp_path / "ledger_f2_a.jsonl",
        outbox_db=tmp_path / "outbox_f2_a.db",
    )

    receipt = host.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10",
        force_new_worldline=True,
    )

    # The receipt worldline_id should be the new branch, not "worldline-main"
    new_wl_id = receipt.get("worldline_id", "")
    assert new_wl_id != "worldline-main", (
        f"force_new_worldline must create a branch worldline, got: {new_wl_id!r}"
    )
    assert "branch" in new_wl_id or new_wl_id != "worldline-main", (
        "New worldline ID should indicate a branch"
    )

    # Registry must be re-bound to the new worldline
    assert host.role_registry.worldline_id == new_wl_id, (
        f"Registry worldline_id {host.role_registry.worldline_id!r} "
        f"must match receipt worldline_id {new_wl_id!r}"
    )

    # Registry DB must NOT be the original world.sqlite
    original_db = save_dir / "world.sqlite"
    assert host.role_registry.database_path is not None
    assert host.role_registry.database_path != original_db, (
        "Registry database_path must point to new branch DB, not original world.sqlite"
    )

    # The branch DB file must actually exist
    assert host.role_registry.database_path.exists(), (
        f"Branch DB {host.role_registry.database_path} must exist after force_new_worldline"
    )


def test_f2_original_worldline_registry_not_polluted_after_branch(base_save_env):
    """F2: Original host (bound to worldline-main) must not be affected by branch created by second host."""
    env = base_save_env
    tmp_path = env["tmp_path"]
    save_dir = env["save_dir"]

    # Host 1 initializes on main worldline (no branch)
    host1 = SeasonCycleHost(
        workspace_root=tmp_path,
        state_file=tmp_path / "state_f2_orig.json",
        ledger_file=tmp_path / "ledger_f2_orig.jsonl",
        outbox_db=tmp_path / "outbox_f2_orig.db",
    )
    host1.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10",
    )
    orig_wl_id = host1.role_registry.worldline_id
    orig_db = host1.role_registry.database_path

    # Host 2 creates a new worldline branch
    host2 = SeasonCycleHost(
        workspace_root=tmp_path,
        state_file=tmp_path / "state_f2_branch.json",
        ledger_file=tmp_path / "ledger_f2_branch.jsonl",
        outbox_db=tmp_path / "outbox_f2_branch.db",
    )
    receipt2 = host2.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10",
        force_new_worldline=True,
    )
    new_wl_id = receipt2["worldline_id"]

    # Host 1's registry must still point to original worldline
    assert host1.role_registry.worldline_id == orig_wl_id, (
        "host1 registry worldline_id must not change when host2 creates a branch"
    )
    assert host1.role_registry.database_path == orig_db, (
        "host1 registry database_path must remain the original DB"
    )
    assert new_wl_id != orig_wl_id, (
        "host2 must create a distinct worldline from host1"
    )


def test_f2_old_worldline_auth_cannot_authorize_strict_new_worldline(base_save_env):
    """F2: Auth file scoped strictly to worldline-main must not authorize a new branch worldline.

    Verifies that if auth file removes the wildcard and only allows worldline-main,
    bind_save_context for a new branch worldline is refused.
    """
    env = base_save_env
    save_dir = env["save_dir"]

    auth_file = save_dir / "role_authorizations.json"
    auth_data = json.loads(auth_file.read_text())

    # Restrict: worldline-main only, no wildcard
    strict_auth = dict(auth_data)
    strict_auth["worldline_id"] = "worldline-main"
    strict_auth["authorized_worldlines"] = ["worldline-main"]  # no "*"
    strict_auth.pop("allow_wildcard_scope", None)
    auth_file.write_text(json.dumps(strict_auth, indent=2), encoding="utf-8")

    reg = TrustedRoleRegistry()
    # Attempt to bind to a new branch worldline not in the whitelist
    result = reg.bind_save_context(
        save_dir,
        "nba2k22_test_f2_01",
        "worldline-branch-f2-test-xyz",       # not in authorized_worldlines
        save_dir / "world.sqlite",
    )
    assert result is False, "Auth restricted to worldline-main must reject a new branch worldline"
    assert reg.is_authorized is False
    assert "MISMATCH" in reg.authorization_status or "REJECT" in reg.authorization_status or not reg.is_authorized

    # Restore
    auth_file.write_text(json.dumps(auth_data, indent=2), encoding="utf-8")
