"""Record read-only evidence for candidate saves and the prior WorldData binding."""
import hashlib
import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def facts(path):
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": digest(path)}


def main():
    save_root, historical, output = (Path(value).resolve() for value in sys.argv[1:])
    binding_path = historical / "save.json"
    binding = json.loads(binding_path.read_bytes())
    db = historical / binding["database_file"]
    if db.with_name(db.name + "-wal").exists():
        raise RuntimeError("Prior database has a WAL. Immutable evidence read would be incomplete.")
    with closing(sqlite3.connect(db.as_uri() + "?mode=ro&immutable=1", uri=True)) as conn:
        calendar = conn.execute(
            "SELECT max(current_native_iso_date) FROM season_calendar_observations"
        ).fetchone()[0]
        final_date = conn.execute(
            "SELECT max(g.game_date) FROM games g JOIN game_state_observations s USING(game_id) WHERE s.is_final=1"
        ).fetchone()[0]
    candidates = []
    for name in ("MyLEAGUE0003", "MyLEAGUE0005"):
        native = save_root / "remote" / name
        backup = save_root / "remote - Copy" / name
        candidates.append({"native": facts(native), "existing_backup": facts(backup) if backup.is_file() else None})
    evidence = {
        "identity_status": "CURRENT_LOADED_FILENAME_UNCONFIRMED",
        "candidates": candidates,
        "historical_binding": {"save_id": binding["save_id"], "filename": binding["native_save_filename"],
                               "sha256": digest(binding_path)},
        "historical_database": facts(db),
        "latest_observed_calendar_date": calendar,
        "latest_observed_final_game_date": final_date,
    }
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False))


if __name__ == "__main__":
    main()
