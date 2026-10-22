# -*- coding: utf-8 -*-
"""
NBA 2K22 数据库初始化与升级迁移工具
执行 schema.sql 中的全量表定义，确保支持跨越几十个赛季的多维数据规范化。
"""
import os
import sqlite3


def ensure_snapshot_context_columns(conn):
    """Add the rule and snapshot metadata columns required for bound GM decisions."""
    required_keys = {
        "monthly_snapshots": "snapshot_id",
        "seasons": "season_year",
    }
    for table, key_column in required_keys.items():
        columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        if key_column not in columns:
            raise RuntimeError(
                f"{table} lacks required key column {key_column}; automatic migration cannot preserve its identity."
            )

    additions = {
        "monthly_snapshots": {
            "season_year": "INTEGER",
            "month_index": "INTEGER",
            "month_name": "TEXT",
            "snapshot_date": "TEXT",
            "games_in_period": "INTEGER DEFAULT 0",
            "total_games_played": "INTEGER DEFAULT 0",
            "notes": "TEXT",
        },
        "seasons": {
            "season_code": "TEXT",
            "salary_cap": "INTEGER",
            "luxury_tax_threshold": "INTEGER",
            "first_apron": "INTEGER",
            "second_apron": "INTEGER",
            "historical_draft_class_year": "INTEGER",
            "season_status": "TEXT",
        },
    }
    for table, desired_columns in additions.items():
        columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        for column, column_type in desired_columns.items():
            if column not in columns:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def quarantine_unverified_coaches(conn):
    """Preserve legacy staff rows before clearing their unverified team links."""
    table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='coaches'"
    ).fetchone()
    if not table_exists:
        return 0
    columns = {row[1] for row in conn.execute("PRAGMA table_info(coaches)")}
    required = {
        "coach_id", "team_id", "first_name", "last_name", "preferred_system",
        "active_system", "offense_grade", "defense_grade", "style_preference_1",
        "style_preference_2", "style_preference_3", "memory_address",
    }
    if not required.issubset(columns):
        raise RuntimeError("coaches 表结构与隔离迁移不兼容，未更改任何教练记录。")

    legacy_count = conn.execute("SELECT count(*) FROM coaches").fetchone()[0]
    if not legacy_count:
        return 0

    before = conn.total_changes
    conn.execute("""
        INSERT OR IGNORE INTO coach_mapping_quarantine (
            legacy_coach_id, legacy_team_id, first_name, last_name, preferred_system,
            active_system, offense_grade, defense_grade, style_preference_1,
            style_preference_2, style_preference_3, memory_address,
            quarantined_at, quarantine_reason
        )
        SELECT coach_id, team_id, first_name, last_name, preferred_system,
               active_system, offense_grade, defense_grade, style_preference_1,
               style_preference_2, style_preference_3, memory_address,
               CURRENT_TIMESTAMP,
               'Legacy coach provenance/team mapping was not verified; retained for recovery.'
        FROM coaches
    """)
    quarantined = conn.total_changes - before
    conn.execute("DELETE FROM coaches")
    return quarantined


def init_or_migrate(db_path=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = db_path or os.path.join(base_dir, "database", "league_state.sqlite")
    schema_path = os.path.join(base_dir, "database", "schema.sql")

    print(f"[*] 正在读取数据库模型定义: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    print(f"[*] 正在连接数据库并执行升级: {db_path}")
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        ensure_snapshot_context_columns(conn)
        quarantined = quarantine_unverified_coaches(conn)
        conn.commit()

        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()
        print(f"[+] 数据库迁移与初始化成功！当前共有 {len(tables)} 张规范化数据表：")
        for idx, (t_name,) in enumerate(tables, 1):
            print(f"    {idx:2d}. {t_name}")
        if quarantined:
            print(f"[!] 已将 {quarantined} 条旧制服组记录移入 coach_mapping_quarantine；尚未验证球队归属，因此未保留为正式 coaches。")

if __name__ == "__main__":
    init_or_migrate()
