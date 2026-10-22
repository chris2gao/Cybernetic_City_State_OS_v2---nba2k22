# -*- coding: utf-8 -*-
"""Reusable clean database template and per-career data locations."""
import json
import os
import re
import shutil
import sqlite3
from contextlib import closing
from datetime import datetime
from typing import Dict, Optional


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_DIR = os.path.join(PROJECT_DIR, "database")
TEMPLATE_DIR = os.path.join(DATABASE_DIR, "templates")
TEMPLATE_CONFIG = os.path.join(TEMPLATE_DIR, "save_template.json")
TEMPLATE_VERSION = 2
TEMPLATE_DB = os.path.join(TEMPLATE_DIR, f"league_template_v{TEMPLATE_VERSION}.sqlite")
SAVE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


def validate_save_id(save_id: str) -> str:
    value = str(save_id or "").strip()
    if not SAVE_ID_PATTERN.fullmatch(value):
        raise ValueError("save_id 需为 1-64 位字母、数字、下划线或连字符，并以字母或数字开头")
    return value


def ensure_template_database() -> str:
    """Create the clean template from the canonical schema once, atomically."""
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    with open(TEMPLATE_CONFIG, "r", encoding="utf-8") as source:
        template_config = json.load(source)
    if template_config.get("template_version") != TEMPLATE_VERSION:
        raise RuntimeError("save_template.json 版本与程序不一致，请先完成模板版本迁移。")
    if os.path.exists(TEMPLATE_DB):
        with closing(sqlite3.connect(TEMPLATE_DB)) as conn:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version != TEMPLATE_VERSION:
            raise RuntimeError(
                f"模板数据库版本为 {version}，程序要求 {TEMPLATE_VERSION}；"
                "请通过模板升级流程迁移，不能直接当作新模板使用。"
            )
        return TEMPLATE_DB

    schema_path = os.path.join(DATABASE_DIR, "schema.sql")
    temp_path = TEMPLATE_DB + ".tmp"
    if os.path.exists(temp_path):
        os.remove(temp_path)
    conn = sqlite3.connect(temp_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        with open(schema_path, "r", encoding="utf-8") as source:
            conn.executescript(source.read())
        conn.execute(f"PRAGMA user_version = {TEMPLATE_VERSION}")
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
    else:
        conn.close()
    os.replace(temp_path, TEMPLATE_DB)
    return TEMPLATE_DB


def save_paths(save_id: str) -> Dict[str, str]:
    save_id = validate_save_id(save_id)
    save_dir = os.path.abspath(os.path.join(DATABASE_DIR, "saves", save_id))
    saves_root = os.path.abspath(os.path.join(DATABASE_DIR, "saves"))
    if os.path.commonpath([save_dir, saves_root]) != saves_root:
        raise ValueError("save_id 指向了保存目录之外")
    data_dir = save_dir
    workspace_path = os.path.join(save_dir, 'workspace.json')
    if os.path.isfile(workspace_path):
        with open(workspace_path, encoding='utf-8') as source:
            workspace = json.load(source)
        if workspace['save_id'] != save_id:
            raise ValueError('WORKSPACE_SAVE_ID_MISMATCH')
        if workspace.get('lifecycle_status') == 'RESET_INTERRUPTED_BLOCKED':
            raise RuntimeError('RESET_INTERRUPTED_BLOCKED')
        relative = workspace.get('data_directory', '.')
        data_dir = os.path.abspath(os.path.join(save_dir, relative))
        if os.path.commonpath([data_dir, save_dir]) != save_dir:
            raise ValueError('WORKSPACE_DIRECTORY_OUTSIDE_SAVE')
    return {
        "save_id": save_id,
        "save_dir": save_dir,
        "data_dir": data_dir,
        "db_path": os.path.join(data_dir, "league_state.sqlite"),
        "player_pool_db_path": os.path.join(data_dir, "player_pool.sqlite"),
        "control_db_path": os.path.join(data_dir, "gm_control.sqlite"),
        "snapshots_dir": os.path.join(data_dir, "snapshots"),
        "backups_dir": os.path.join(data_dir, "backups"),
        "evaluations_dir": os.path.join(data_dir, "evaluations"),
    }


def create_or_open_save(save_id: str) -> Dict[str, str]:
    """Create an isolated save database from the clean template or open it."""
    paths = save_paths(save_id)
    return initialize_save(paths)


def initialize_save(paths):
    """Initialize explicit generation paths using the existing clean template."""
    os.makedirs(paths["save_dir"], exist_ok=True)
    os.makedirs(paths["snapshots_dir"], exist_ok=True)
    os.makedirs(paths["backups_dir"], exist_ok=True)
    os.makedirs(paths["evaluations_dir"], exist_ok=True)

    db_path = paths["db_path"]
    if not os.path.exists(db_path):
        template_path = ensure_template_database()
        temp_db_path = db_path + ".tmp"
        shutil.copy2(template_path, temp_db_path)
        try:
            conn = sqlite3.connect(temp_db_path)
            try:
                conn.execute("PRAGMA foreign_keys = ON")
                conn.executemany(
                    "INSERT INTO save_metadata(key, value) VALUES (?, ?)",
                    [
                        ("save_id", paths["save_id"]),
                        ("template_version", str(TEMPLATE_VERSION)),
                        ("created_at", datetime.now().isoformat()),
                    ],
                )
                conn.commit()
            finally:
                # sqlite3's context manager commits/rolls back but does not close
                # the handle. Windows cannot atomically rename an open database.
                conn.close()
            os.replace(temp_db_path, db_path)
        except Exception:
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            raise
    else:
        with closing(sqlite3.connect(db_path)) as conn:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(save_metadata)")}
            if not columns:
                raise RuntimeError(
                    f"{db_path} 不是由新局模板创建的存档数据库；为避免覆盖旧数据，请使用新的 save_id。"
                )
            row = conn.execute("SELECT value FROM save_metadata WHERE key='save_id'").fetchone()
            if not row or row[0] != paths["save_id"]:
                raise RuntimeError("存档目录与数据库内的 save_id 不一致，已停止操作。")
    return paths


def resolve_context(save_id: Optional[str] = None) -> Dict[str, str]:
    """Resolve a save-specific context; None preserves the legacy shared DB."""
    if save_id:
        return create_or_open_save(save_id)
    os.makedirs(os.path.join(DATABASE_DIR, "snapshots"), exist_ok=True)
    os.makedirs(os.path.join(DATABASE_DIR, "backups"), exist_ok=True)
    os.makedirs(os.path.join(DATABASE_DIR, "evaluations"), exist_ok=True)
    return {
        "save_id": "legacy-shared",
        "save_dir": DATABASE_DIR,
        "db_path": os.path.join(DATABASE_DIR, "league_state.sqlite"),
        "player_pool_db_path": os.path.join(DATABASE_DIR, "nba2k22_players.sqlite"),
        "snapshots_dir": os.path.join(DATABASE_DIR, "snapshots"),
        "backups_dir": os.path.join(DATABASE_DIR, "backups"),
        "evaluations_dir": os.path.join(DATABASE_DIR, "evaluations"),
    }
