# -*- coding: utf-8 -*-
"""Run non-destructive static checks without opening the game or user databases."""
import json
import pathlib
import sqlite3
import sys


PROJECT_DIR = pathlib.Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_DIR / "src"
SCHEMA_PATH = PROJECT_DIR / "database" / "schema.sql"
TEMPLATE_PATH = PROJECT_DIR / "database" / "templates" / "save_template.json"


def main() -> None:
    sources = sorted(SOURCE_DIR.glob("*.py"))
    for source in sources:
        compile(source.read_text(encoding="utf-8"), str(source), "exec")
    print(f"[PASS] Python syntax: {len(sources)} modules")

    with TEMPLATE_PATH.open("r", encoding="utf-8") as source:
        template = json.load(source)
    sys.path.insert(0, str(SOURCE_DIR))
    from save_context import TEMPLATE_VERSION
    from season_rules import load_configured_season_rules

    if template.get("template_version") != TEMPLATE_VERSION:
        raise RuntimeError("save template version does not match application version")
    rules = load_configured_season_rules()
    print(
        f"[PASS] Save template v{TEMPLATE_VERSION}: {rules['season_code']} "
        f"salary rules validated"
    )

    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        integrity = conn.execute("PRAGMA quick_check").fetchone()[0]
        foreign_key_issues = conn.execute("PRAGMA foreign_key_check").fetchall()
        tables = conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        if integrity != "ok" or foreign_key_issues or tables < 20:
            raise RuntimeError(
                f"schema check failed: integrity={integrity}, "
                f"foreign_keys={len(foreign_key_issues)}, tables={tables}"
            )
        print(
            f"[PASS] SQLite schema: {tables} tables, quick_check=ok, "
            "foreign_key_issues=0"
        )
    finally:
        conn.close()

    print("[INFO] Static checks only; no live game process or saved database was opened.")


if __name__ == "__main__":
    main()
