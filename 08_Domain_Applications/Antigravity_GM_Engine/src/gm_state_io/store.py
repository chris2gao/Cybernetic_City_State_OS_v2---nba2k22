"""Per-generation control DB migration. Connections are always explicitly closed."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .common import canonical, binding

SCHEMA = Path(__file__).resolve().parents[2] / 'database/gm_control_schema.sql'


@contextmanager
def connect(path):
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    try:
        with c:
            yield c
    finally:
        c.close()


def initialize(path, workspace):
    with connect(path) as c:
        version = c.execute('PRAGMA user_version').fetchone()[0]
        if version > 1:
            raise ValueError('UNSUPPORTED_CONTROL_SCHEMA')
        c.executescript(SCHEMA.read_text(encoding='utf-8'))
        for k, v in binding(workspace).items():
            old = c.execute('SELECT value FROM control_metadata WHERE key=?', (k,)).fetchone()
            if old and old[0] != v:
                raise ValueError('CONTROL_SAVE_BINDING_MISMATCH')
            c.execute('INSERT OR IGNORE INTO control_metadata VALUES (?,?)', (k, v))
        from .registry import Registry
        register(c, Registry())


def register(c, registry):
    c.executemany('INSERT OR REPLACE INTO native_field_registry VALUES (?,?,?)',
                  [(k, registry.version, canonical(v)) for k, v in registry.fields.items()])
