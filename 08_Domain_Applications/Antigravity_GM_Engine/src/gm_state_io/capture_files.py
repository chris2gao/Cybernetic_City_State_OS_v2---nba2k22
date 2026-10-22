"""Stage complete capture files; journal multi-file installation and fail closed.

There is no atomic filesystem rename spanning SQLite files. A durable PREPARED
journal blocks every managed entry point after a crash; explicit recovery restores
the last complete cohort. Neither directory names nor player IDs establish origin.
"""
from contextlib import closing
from pathlib import Path
import os
import shutil
import sqlite3
from uuid import uuid4
from .common import atomic_json, binding, load, now
from snapshot_integrity import file_sha256

SOURCE_KEYS = ('capture_id', 'capture_snapshot_id', 'capture_updated_at')


def metadata(connection, table='save_metadata'):
    try:
        return dict(connection.execute('SELECT key,value FROM '+table))
    except sqlite3.OperationalError as exc:
        raise ValueError('POOL_SAVE_BINDING_MISMATCH' if table == 'save_metadata'
                         else 'CONTROL_SAVE_BINDING_MISMATCH') from exc


def put_metadata(connection, values, table='save_metadata'):
    connection.execute('CREATE TABLE IF NOT EXISTS '+table+'(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
    connection.executemany('INSERT OR REPLACE INTO '+table+' VALUES (?,?)', values.items())


def source_stamp(workspace, snapshot_id, updated_at):
    return dict(**binding(workspace), capture_id=uuid4().hex,
                capture_snapshot_id=snapshot_id, capture_updated_at=updated_at)


def sync_origin(connection):
    """Latest full-pool source. Historical league snapshots remain untouched."""
    exists = connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='data_sync_metadata'").fetchone()
    if not exists:
        return None
    return connection.execute('SELECT snapshot_id,save_id,data_updated_at FROM data_sync_metadata '
                              'ORDER BY data_updated_at DESC,snapshot_id DESC LIMIT 1').fetchone()


def journal_path(paths):
    return Path(paths['db_path']).parent / '.capture_install.json'


def require_complete(paths):
    path = journal_path(paths)
    if path.exists() and load(path)['status'] not in ('COMMITTED', 'RESTORED'):
        raise ValueError('CAPTURE_INSTALL_INCOMPLETE_MANUAL_RECOVERY_REQUIRED')


def backup(source, target):
    """SQLite backup includes committed WAL pages; handles are closed on Windows."""
    source, target = Path(source), Path(target)
    if target.exists():
        target.unlink()
    with closing(sqlite3.connect(source.resolve().as_uri()+'?mode=ro', uri=True)) as src:
        with closing(sqlite3.connect(target)) as dst:
            src.backup(dst)


def prepare_league(paths):
    require_complete(paths)
    staged = paths['db_path']+'.capture'
    if Path(paths['db_path']).exists():
        backup(paths['db_path'], staged)
    else:
        Path(staged).unlink(missing_ok=True)
    return staged


def install(paths, staged_league, staged_pool, stamp=None):
    """Caller closes all staged connections first. No incomplete cohort is usable."""
    require_complete(paths)
    entries = [dict(target=paths['db_path'], staged=staged_league),
               dict(target=paths['player_pool_db_path'], staged=staged_pool)]
    if stamp:
        staged_control = paths['control_db_path']+'.capture'
        backup(paths['control_db_path'], staged_control)
        with closing(sqlite3.connect(staged_control)) as c:
            put_metadata(c, stamp, 'control_metadata')
            c.commit()
        entries.append(dict(target=paths['control_db_path'], staged=staged_control))
    # Backups are created before the first authoritative rename.
    for item in entries:
        item['existed'] = Path(item['target']).exists()
        item['backup'] = item['target']+'.previous_capture'
        if item['existed']:
            with closing(sqlite3.connect(item['target'])) as c:
                checkpoint = c.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()
                if checkpoint[0]:
                    raise ValueError('CAPTURE_TARGET_DATABASE_BUSY')
            # Exact bytes matter for the previous pool's manifest file hash.
            # SQLite.backup is used for working copies, not rollback originals.
            shutil.copyfile(item['target'], item['backup'])
            item['backup_sha256'] = file_sha256(item['backup'])
        with closing(sqlite3.connect(Path(item['staged']).resolve().as_uri()+'?mode=ro', uri=True)) as c:
            if c.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('CAPTURE_STAGED_DATABASE_INVALID')
    journal = dict(status='PREPARED', created_at=now(), entries=entries, source=stamp)
    atomic_json(journal_path(paths), journal)
    try:
        for item in entries:
            os.replace(item['staged'], item['target'])
        atomic_json(journal_path(paths), dict(journal, status='COMMITTED'))
    except Exception:
        # Preserve PREPARED if restoring any file fails. All callers then stop.
        restore(paths, journal)
        raise


def restore(paths, journal=None):
    journal = journal or load(journal_path(paths))
    expected = {str(Path(paths[k]).resolve()) for k in ('db_path','player_pool_db_path','control_db_path') if k in paths}
    for item in journal['entries']:
        if str(Path(item['target']).resolve()) not in expected or item['backup'] != item['target']+'.previous_capture':
            raise ValueError('INVALID_CAPTURE_RECOVERY_TARGET')
        if item['existed'] and file_sha256(item['backup']) != item['backup_sha256']:
            raise ValueError('CAPTURE_RECOVERY_BACKUP_HASH_MISMATCH')
    for item in journal['entries']:
        if item['existed']:
            # Copy to a new temporary file: keep the backup until all restores succeed.
            temporary = item['target']+'.restore_capture'
            shutil.copyfile(item['backup'], temporary)
            os.replace(temporary, item['target'])
        else:
            Path(item['target']).unlink(missing_ok=True)
    atomic_json(journal_path(paths), dict(journal, status='RESTORED', restored_at=now()))
