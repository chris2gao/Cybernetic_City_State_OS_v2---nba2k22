"""F2 Iteration 11 — Worldline State Consistency End-to-End Tests.

GPT-6 RDC finding: after force_new_worldline=True:
- worldlines_manifest.json did NOT contain the new worldline
- save.json.worldline_id was still 'worldline-main'
- Registry returned AUTHORIZATION_WILDCARD_TARGET_UNVERIFIED
- Host receipt incorrectly said INITIALIZED_AND_BASELINE_BOUND

These tests verify the complete state machine is consistent:
1. Manifest contains and activates new worldline
2. save.json.worldline_id AND database_file both point to new worldline
3. Registry worldline + database matches manifest + save.json
4. Valid Human auth can pass through
5. Old strict worldline auth cannot authorize new worldline
6. Re-initialization recovers new worldline correctly
7. Mid-failure does not leave half-initialized state
8. Receipt accurately reflects authorization status
"""

import json
import os
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

def _build_save_env(tmp_path: Path) -> dict:
    """Build a minimal save environment with auth that allows wildcards."""
    save_dir = tmp_path / "save"
    native_file = tmp_path / "MyLEAGUE0003"
    native_file.write_bytes(b"FAKE_NBA2K22_SAVE_CONTENT")

    initialize_save(str(save_dir), "nba2k22_it11_01", str(native_file))
    db_path = save_dir / "world.sqlite"

    with connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO seasons (season_id, season_code, save_id) "
            "VALUES ('season:2021', '2021-22', 'nba2k22_it11_01')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO teams (team_id, display_name) VALUES "
            "('team:1', 'MIL'), ('team:2', 'BKN'), ('team:28', 'LAL')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO games (game_id, season_id, game_date, home_team_id, away_team_id, native_game_id) "
            "VALUES ('game:001', 'season:2021', '2021-11-01', 'team:1', 'team:2', '101')"
        )

    # Auth manifest with wildcard scope explicitly declared
    auth = {
        "schema_version": "nba2k22.rea.role_authorizations.v1",
        "save_id": "nba2k22_it11_01",
        "worldline_id": "worldline-main",
        "bound_database_file": "world.sqlite",
        "authorized_worldlines": ["worldline-main", "*"],
        "authorized_databases": ["world.sqlite", "*"],
        "allow_wildcard_scope": True,
        "human_authorization_ref": "HUMAN_IT11_AUTH_20261102",
        "provenance": "SAVE_DB_VERIFIED_DELEGATION",
        "roles": [
            {
                "role_type": "GM",
                "team_id": 28,
                "actor_uid": "gm_user_01",
                "provenance": "SAVE_DB_VERIFIED_DELEGATION",
                "human_authorization_ref": "HUMAN_IT11_AUTH_20261102",
            }
        ],
    }
    (save_dir / "role_authorizations.json").write_text(
        json.dumps(auth, indent=2), encoding="utf-8"
    )

    return {
        "tmp_path": tmp_path,
        "save_dir": save_dir,
        "native_file": native_file,
        "db_path": db_path,
        "auth": auth,
    }


def _make_host(tmp_path: Path, suffix: str = "") -> SeasonCycleHost:
    return SeasonCycleHost(
        workspace_root=tmp_path,
        state_file=tmp_path / f"state{suffix}.json",
        ledger_file=tmp_path / f"ledger{suffix}.jsonl",
        outbox_db=tmp_path / f"outbox{suffix}.db",
    )


# ---------------------------------------------------------------------------
# IT11-C1: New worldline DB created and manifest updated
# ---------------------------------------------------------------------------

def test_it11_c1_new_db_created_and_manifest_contains_new_worldline(tmp_path):
    """C1: force_new_worldline=True must create branch DB and register it in manifest."""
    env = _build_save_env(tmp_path)
    save_dir = env["save_dir"]
    host = _make_host(tmp_path, "_c1")

    receipt = host.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10",
        force_new_worldline=True,
    )

    new_wl_id = receipt["worldline_id"]
    assert new_wl_id != "worldline-main", "New worldline must differ from worldline-main"

    # Manifest must contain and activate new worldline
    manifest = json.loads((save_dir / "worldlines_manifest.json").read_text(encoding="utf-8"))
    assert new_wl_id in manifest["worldlines"], (
        f"New worldline {new_wl_id!r} must appear in worldlines_manifest.json"
    )
    assert manifest["active_worldline_id"] == new_wl_id, (
        "Manifest active_worldline_id must equal new worldline"
    )

    # Branch DB must exist
    branch_db_name = manifest["worldlines"][new_wl_id]["database_file"]
    branch_db_path = save_dir / branch_db_name
    assert branch_db_path.exists(), f"Branch DB {branch_db_path} must exist"

    # Parent worldline recorded
    assert manifest["worldlines"][new_wl_id].get("parent_worldline_id") == "worldline-main", (
        "Branch must record worldline-main as parent"
    )


# ---------------------------------------------------------------------------
# IT11-C2: save.json worldline_id AND database_file both updated
# ---------------------------------------------------------------------------

def test_it11_c2_save_json_worldline_and_db_both_updated(tmp_path):
    """C2: save.json must have BOTH worldline_id and database_file pointing to the new worldline."""
    env = _build_save_env(tmp_path)
    save_dir = env["save_dir"]
    host = _make_host(tmp_path, "_c2")

    receipt = host.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10",
        force_new_worldline=True,
    )

    new_wl_id = receipt["worldline_id"]
    save_data = json.loads((save_dir / "save.json").read_text(encoding="utf-8"))

    assert save_data.get("worldline_id") == new_wl_id, (
        f"save.json worldline_id must be {new_wl_id!r}, got {save_data.get('worldline_id')!r}"
    )
    assert save_data.get("database_file") != "world.sqlite", (
        "save.json database_file must point to branch DB, not world.sqlite"
    )
    # Both receipt and save.json must agree on database_file
    receipt_db = Path(receipt["database_file"]).name
    assert save_data.get("database_file") == receipt_db, (
        f"save.json database_file {save_data.get('database_file')!r} must match receipt database_file {receipt_db!r}"
    )


# ---------------------------------------------------------------------------
# IT11-C3: Manifest, save.json, and Registry all consistent
# ---------------------------------------------------------------------------

def test_it11_c3_manifest_save_registry_all_consistent(tmp_path):
    """C3: Manifest active_worldline_id, save.json worldline_id, and registry worldline_id must all agree."""
    env = _build_save_env(tmp_path)
    save_dir = env["save_dir"]
    host = _make_host(tmp_path, "_c3")

    receipt = host.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10",
        force_new_worldline=True,
    )

    new_wl_id = receipt["worldline_id"]

    manifest = json.loads((save_dir / "worldlines_manifest.json").read_text(encoding="utf-8"))
    save_data = json.loads((save_dir / "save.json").read_text(encoding="utf-8"))

    # All three sources agree on worldline ID
    assert manifest["active_worldline_id"] == new_wl_id, "Manifest must agree"
    assert save_data["worldline_id"] == new_wl_id, "save.json must agree"
    assert host.role_registry.worldline_id == new_wl_id, "Registry must agree"

    # All three sources agree on database path
    manifest_db = manifest["worldlines"][new_wl_id]["database_file"]
    save_db = save_data["database_file"]
    registry_db_name = host.role_registry.database_path.name if host.role_registry.database_path else None

    assert manifest_db == save_db, (
        f"Manifest DB {manifest_db!r} must match save.json DB {save_db!r}"
    )
    assert registry_db_name == manifest_db, (
        f"Registry DB {registry_db_name!r} must match manifest DB {manifest_db!r}"
    )


# ---------------------------------------------------------------------------
# IT11-C4: Valid Human auth passes through after worldline registration
# ---------------------------------------------------------------------------

def test_it11_c4_valid_human_auth_passes_after_worldline_registration(tmp_path):
    """C4: With allow_wildcard_scope=True and new worldline in manifest, auth must pass."""
    env = _build_save_env(tmp_path)
    save_dir = env["save_dir"]
    host = _make_host(tmp_path, "_c4")

    receipt = host.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10",
        force_new_worldline=True,
    )

    # With wildcard auth and new worldline now in manifest, registry should be authorized
    assert host.role_registry.is_authorized is True, (
        f"Registry must be authorized after force_new_worldline with valid wildcard auth. "
        f"Status: {host.role_registry.authorization_status}"
    )
    assert receipt["role_authorization_status"] not in (
        "AUTHORIZATION_WILDCARD_TARGET_UNVERIFIED",
        "DEFAULT_DENIED_UNBOUND",
        "AUTHORIZATION_FILE_MISSING",
    ), (
        f"Receipt role_authorization_status must not indicate unverified wildcard. "
        f"Got: {receipt['role_authorization_status']!r}"
    )
    # Receipt status must reflect full authorization
    assert receipt.get("status") == "INITIALIZED_AND_BASELINE_BOUND", (
        f"With valid auth, status must be INITIALIZED_AND_BASELINE_BOUND. Got: {receipt.get('status')!r}"
    )


# ---------------------------------------------------------------------------
# IT11-C5: Old strict worldline auth cannot authorize new worldline
# ---------------------------------------------------------------------------

def test_it11_c5_strict_old_worldline_auth_cannot_authorize_new_worldline(tmp_path):
    """C5: Auth strictly scoped to worldline-main must not authorize a new branch worldline."""
    env = _build_save_env(tmp_path)
    save_dir = env["save_dir"]

    # Overwrite auth to strictly allow only worldline-main (no wildcard)
    strict_auth = {
        "schema_version": "nba2k22.rea.role_authorizations.v1",
        "save_id": "nba2k22_it11_01",
        "worldline_id": "worldline-main",
        "bound_database_file": "world.sqlite",
        "authorized_worldlines": ["worldline-main"],   # no "*"
        "authorized_databases": ["world.sqlite"],       # no "*"
        "human_authorization_ref": "HUMAN_IT11_STRICT_AUTH",
        "provenance": "SAVE_DB_VERIFIED_DELEGATION",
        "roles": [
            {
                "role_type": "GM",
                "team_id": 28,
                "actor_uid": "gm_user_01",
                "provenance": "SAVE_DB_VERIFIED_DELEGATION",
                "human_authorization_ref": "HUMAN_IT11_STRICT_AUTH",
            }
        ],
    }
    (save_dir / "role_authorizations.json").write_text(
        json.dumps(strict_auth, indent=2), encoding="utf-8"
    )

    host = _make_host(tmp_path, "_c5")
    receipt = host.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10",
        force_new_worldline=True,
    )

    # Registry must NOT be authorized — new worldline not in strict whitelist
    assert host.role_registry.is_authorized is False, (
        "Strict worldline-main auth must not authorize new branch worldline"
    )
    assert "MISMATCH" in host.role_registry.authorization_status or \
           host.role_registry.authorization_status in (
               "AUTHORIZATION_WORLDLINE_MISMATCH",
               "AUTHORIZATION_DATABASE_FILE_MISMATCH",
           ), (
        f"Authorization status must indicate mismatch. Got: {host.role_registry.authorization_status!r}"
    )
    # Receipt must NOT claim INITIALIZED_AND_BASELINE_BOUND when auth is missing
    assert receipt.get("status") == "INITIALIZED_BASELINE_BOUND_AUTHORIZATION_PENDING", (
        f"Without valid auth, receipt status must be AUTHORIZATION_PENDING. Got: {receipt.get('status')!r}"
    )
    assert receipt.get("role_authorization_ready") is False, (
        "receipt.role_authorization_ready must be False when not authorized"
    )


# ---------------------------------------------------------------------------
# IT11-C6: Re-initialization recovers new worldline correctly
# ---------------------------------------------------------------------------

def test_it11_c6_reinitialize_recovers_new_worldline(tmp_path):
    """C6: A second initialize_season (no force_new_worldline) must recover the existing branch worldline."""
    env = _build_save_env(tmp_path)
    save_dir = env["save_dir"]

    # First init: create branch
    host1 = _make_host(tmp_path, "_c6a")
    receipt1 = host1.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10",
        force_new_worldline=True,
    )
    new_wl_id = receipt1["worldline_id"]
    new_db_name = Path(receipt1["database_file"]).name

    # Second init on same save_dir (no force): should resume the branch worldline
    # (because manifest now has it as active_worldline_id and save.json points to it)
    host2 = _make_host(tmp_path, "_c6b")
    receipt2 = host2.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10",
    )

    # The second host should pick up the active worldline from manifest/save.json
    assert receipt2["worldline_id"] == new_wl_id, (
        f"Re-initialization must recover worldline {new_wl_id!r}, got {receipt2['worldline_id']!r}"
    )
    assert Path(receipt2["database_file"]).name == new_db_name, (
        f"Re-initialization must recover branch DB {new_db_name!r}"
    )
    assert host2.role_registry.worldline_id == new_wl_id, "Registry must recover new worldline"


# ---------------------------------------------------------------------------
# IT11-C7: Mid-failure in manifest write rolls back, no false success
# ---------------------------------------------------------------------------

def test_it11_c7_mid_failure_rolls_back_no_false_success(tmp_path, monkeypatch):
    """C7: If the force_new_worldline manifest write fails, rollback prevents half-initialized state.

    Strategy: monkeypatch os.replace to fail specifically when writing worldlines_manifest.json
    for the SECOND time (the first write is from inspect_worldline, which must succeed).
    After failure, save.json worldline_id must remain worldline-main (no branch ID leaked).
    """
    env = _build_save_env(tmp_path)
    save_dir = env["save_dir"]

    # Monkeypatch os.replace to fail on the SECOND write to worldlines_manifest.json.
    # inspect_worldline() writes it first (must succeed), then force_new_worldline writes again.
    original_replace = os.replace
    manifest_write_count = {"n": 0}

    def failing_replace(src, dst):
        if Path(dst).name == "worldlines_manifest.json":
            manifest_write_count["n"] += 1
            if manifest_write_count["n"] == 2:
                # Simulate write failure on second manifest write (our F2 block)
                try:
                    Path(src).unlink(missing_ok=True)
                except Exception:
                    pass
                raise OSError("SIMULATED_MANIFEST_WRITE_FAILURE")
        return original_replace(src, dst)

    monkeypatch.setattr(os, "replace", failing_replace)

    host = _make_host(tmp_path, "_c7")
    with pytest.raises(RuntimeError, match="FORCE_NEW_WORLDLINE_STATE_UPDATE_FAILED_FAIL_CLOSED"):
        host.initialize_season(
            save_directory=str(save_dir),
            loaded_filename="MyLEAGUE0003",
            mock_game_date="2021-11-10",
            force_new_worldline=True,
        )

    # After failure and rollback, save.json must NOT contain a new branch worldline ID.
    # save.json is rolled back to the pre-branch state (worldline-main).
    restored_save = json.loads((save_dir / "save.json").read_text(encoding="utf-8"))
    restored_wl_id = restored_save.get("worldline_id", "worldline-main")
    assert restored_wl_id == "worldline-main", (
        f"After rollback, save.json worldline_id must be worldline-main (pre-branch state), "
        f"not a new branch ID. Got: {restored_wl_id!r}"
    )


# ---------------------------------------------------------------------------
# IT11-C8: Receipt accurately reflects authorization — no false INITIALIZED_AND_BASELINE_BOUND
# ---------------------------------------------------------------------------

def test_it11_c8_receipt_accurate_when_authorization_missing(tmp_path):
    """C8: Receipt status must distinguish auth-pending from fully-authorized initialization."""
    env = _build_save_env(tmp_path)
    save_dir = env["save_dir"]

    # Remove auth file entirely — default deny should apply
    (save_dir / "role_authorizations.json").unlink()

    host = _make_host(tmp_path, "_c8")
    receipt = host.initialize_season(
        save_directory=str(save_dir),
        loaded_filename="MyLEAGUE0003",
        mock_game_date="2021-11-10",
        force_new_worldline=True,
    )

    # With no auth file, registry must be default-denied
    assert host.role_registry.is_authorized is False
    assert receipt.get("status") == "INITIALIZED_BASELINE_BOUND_AUTHORIZATION_PENDING", (
        f"Receipt must signal AUTHORIZATION_PENDING when auth is missing. Got: {receipt.get('status')!r}"
    )
    assert receipt.get("role_authorization_ready") is False

    # But worldline state should still be consistent
    new_wl_id = receipt["worldline_id"]
    manifest = json.loads((save_dir / "worldlines_manifest.json").read_text(encoding="utf-8"))
    assert new_wl_id in manifest["worldlines"], "Manifest must still be updated even if auth is missing"
    save_data = json.loads((save_dir / "save.json").read_text(encoding="utf-8"))
    assert save_data.get("worldline_id") == new_wl_id, "save.json worldline_id must still be updated"
