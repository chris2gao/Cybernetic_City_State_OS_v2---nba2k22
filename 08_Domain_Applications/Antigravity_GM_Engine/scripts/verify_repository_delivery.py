"""Verify remote project revision and full archived career databases, read-only."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from export_web_gm import verify_bundle
from save_context import save_paths
from snapshot_integrity import file_sha256, write_json_atomic


def run(arguments):
    return subprocess.run(arguments, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=True).stdout.strip()


def table_fingerprints(path):
    connection = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        assert connection.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
        assert not connection.execute("PRAGMA foreign_key_check").fetchall()
        result = {}
        tables = connection.execute("SELECT name,sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        for name, schema in tables.fetchall():
            quoted = '"' + name.replace('"', '""') + '"'
            rows = sorted(hashlib.sha256(repr(row).encode("utf-8")).hexdigest()
                          for row in connection.execute(f"SELECT * FROM {quoted}"))
            result[name] = {"schema": schema, "rows": len(rows),
                            "sha256": hashlib.sha256("\n".join(rows).encode()).hexdigest()}
        return result
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-id", required=True)
    args = parser.parse_args()
    paths = save_paths(args.save_id)
    config = json.loads((ROOT / "config/github_sync.json").read_text(encoding="utf-8"))
    repository = config["repository"]
    metadata = json.loads(run(["gh", "repo", "view", repository, "--json", "isPrivate,nameWithOwner"]))
    assert metadata["isPrivate"] and metadata["nameWithOwner"] == repository
    assert not run(["git", "status", "--porcelain"]), "Project has unpublished changes"
    head = run(["git", "rev-parse", "HEAD"])
    remote_head = run(["git", "ls-remote", "origin", f"refs/heads/{config['branch']}"]).split()[0]
    assert head == remote_head, "Remote source branch differs from the reviewed project"
    tracked = set(run(["git", "ls-files"]).splitlines())
    source_files = set()
    for directory in ("src", "scripts", "config", "docs", "web_gm"):
        for path in (ROOT / directory).rglob("*"):
            if path.is_file() and path.suffix in {".py", ".ps1", ".json", ".md"} and "__pycache__" not in path.parts:
                source_files.add(path.relative_to(ROOT).as_posix())
    assert not source_files - tracked, f"Unpublished project source paths: {sorted(source_files - tracked)}"
    pointer_path = f"published/saves/{args.save_id}/latest.json"
    response = json.loads(run(["gh", "api", f"repos/{repository}/contents/{pointer_path}?ref={head}"]))
    pointer_bytes = base64.b64decode(response["content"])
    assert pointer_bytes == (ROOT / pointer_path).read_bytes()
    pointer = json.loads(pointer_bytes)
    manifest = verify_bundle(ROOT / "published" / pointer["batch_path"], pointer["manifest_sha256"])
    policy_path = "config/gameplay_policy.json"
    policy_response = json.loads(run(["gh", "api", f"repos/{repository}/contents/{policy_path}?ref={head}"]))
    assert base64.b64decode(policy_response["content"]) == (ROOT / policy_path).read_bytes()
    archive = manifest["archive"]
    database_results = {}
    with tempfile.TemporaryDirectory(prefix="gm_delivery_") as temporary:
        run(["gh", "release", "download", archive["release_tag"], "--repo", repository,
             "--pattern", archive["filename"], "--dir", temporary])
        downloaded = Path(temporary) / archive["filename"]
        assert downloaded.stat().st_size == archive["bytes"]
        assert file_sha256(str(downloaded)) == archive["sha256"]
        with zipfile.ZipFile(downloaded) as package:
            assert package.testzip() is None
            for name, source in (("league_state.sqlite", paths["db_path"]),
                                 ("player_pool.sqlite", paths["player_pool_db_path"])):
                destination = Path(temporary) / name
                destination.write_bytes(package.read(name))
                original = table_fingerprints(source)
                restored = table_fingerprints(destination)
                assert original == restored, f"Full database tables differ: {name}"
                database_results[name] = {"tables": len(restored),
                                          "rows": sum(item["rows"] for item in restored.values()),
                                          "all_table_schemas_and_row_hashes_match": True}
    report = {"repository": repository, "private": True, "project_commit": head,
              "all_project_source_files_versioned": len(source_files),
              "remote_source_revision_matches": True, "remote_policy_bytes_match": True,
              "data_batch_id": manifest["batch_id"], "game_date": manifest["context"]["game_date"],
              "downloaded_archive_sha256_verified": True, "databases": database_results,
              "web_access_test": "PLAYER_HANDLED_NOT_PERFORMED"}
    write_json_atomic(str(ROOT / "_exports/final_delivery.json"), report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
