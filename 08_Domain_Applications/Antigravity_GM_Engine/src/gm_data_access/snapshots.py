"""Static two-database snapshots made from the existing audited backup archive.

The archive is local; no download, publication, JSON hash sync, or live capture.
Local hashes certify sealed SQLite bytes, not the GitHub JSON sync protocol.
"""
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import zipfile

from data_context import decode_context
from snapshot_integrity import snapshot_digest, file_sha256
from . import AccessError, QUERY_VERSION

DB_NAMES = ("league_state.sqlite", "player_pool.sqlite")


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,179}", value) or '..' in value:
        raise AccessError("INVALID_INPUT", "Invalid career or batch identifier")
    return value


def read_json(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 4_000_000:
        raise AccessError("BLOCKED_LOCAL_DB_ACCESS", "Required bounded metadata file unavailable")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def ro(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise AccessError("BLOCKED_LOCAL_DB_ACCESS", "SQLite snapshot file missing")
    conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=2)
    conn.execute("PRAGMA query_only=ON")
    return conn


def validate_pair(directory, manifest, audit, ingest):
    expected = (manifest['snapshot_id'], manifest['save_id'], manifest['data_updated_at'])
    if audit.get('verdict') != 'PASS_VERIFIED' or not audit.get('checks') or not all(audit['checks'].values()):
        raise AccessError("STALE_OR_MIXED_BATCH", "Missing successful source audit")
    if (audit.get('snapshot_id'), audit.get('save_id')) != expected[:2]:
        raise AccessError("STALE_OR_MIXED_BATCH", "Audit identity differs")
    if (ingest.get('snapshot_id'), ingest.get('save_id'), ingest.get('data_updated_at')) != expected:
        raise AccessError("STALE_OR_MIXED_BATCH", "Ingest identity differs")
    binding = manifest.get('source_binding', {})
    digest = audit.get('database_digest_sha256')
    if not digest or digest != binding.get('snapshot_digest_sha256') or digest != ingest.get('batch_binding', {}).get('snapshot_digest_sha256'):
        raise AccessError("STALE_OR_MIXED_BATCH", "Audit and manifest source bindings differ")
    if audit.get('manifest_binding', {}).get('manifest_sha256') != binding.get('ingest_manifest_sha256'):
        raise AccessError("STALE_OR_MIXED_BATCH", "Audit ingest binding differs")
    pool_source = binding.get('player_pool_sha256')
    if not pool_source or pool_source != ingest.get('batch_binding',{}).get('player_pool_sha256') or pool_source != audit.get('player_pool_sha256'):
        raise AccessError('STALE_OR_MIXED_BATCH','Player pool capture/audit bindings differ')
    for name in DB_NAMES:
        with closing(ro(Path(directory) / name)) as c:
            rows = c.execute('SELECT snapshot_id,save_id,data_updated_at FROM data_sync_metadata WHERE snapshot_id=?', (expected[0],)).fetchall()
            if rows != [expected]:
                raise AccessError("STALE_OR_MIXED_BATCH", "Two-database timestamp binding differs")
            if name == 'player_pool.sqlite' and c.execute('SELECT count(*) FROM data_sync_metadata').fetchone()[0] != 1:
                raise AccessError("STALE_OR_MIXED_BATCH", "Player pool must have a single capture identity")
            if name == 'player_pool.sqlite' and c.execute('SELECT count(*) FROM player_pool').fetchone()[0] != audit.get('player_pool_records'):
                raise AccessError('STALE_OR_MIXED_BATCH','Player pool count differs from source audit')
            if name == 'league_state.sqlite':
                context_row = c.execute('SELECT notes FROM monthly_snapshots WHERE snapshot_id=?', (expected[0],)).fetchone()
                context = decode_context(context_row[0]) if context_row else {}
                if context.get('game_date') != manifest.get('context', {}).get('game_date') or context.get('career_id') != expected[1]:
                    raise AccessError("STALE_OR_MIXED_BATCH", "Snapshot game context differs")
                if snapshot_digest(c, expected[0]) != digest:
                    raise AccessError("STALE_OR_MIXED_BATCH", "SQLite snapshot rows do not match source audit")
    if manifest.get('player_potential_mask'):
        from player_potential_mask import verify_sanitized_pair
        with closing(ro(Path(directory)/DB_NAMES[0])) as league, closing(ro(Path(directory)/DB_NAMES[1])) as pool:
            verify_sanitized_pair(league,pool,expected[0])


def install_archive(archive, manifest, root):
    """Owner-only preparation. Consumers never invoke this against live saves."""
    career, batch = identifier(manifest['save_id']), identifier(manifest['batch_id'])
    if manifest.get('audit_verdict') != 'PASS_VERIFIED':
        raise AccessError("STALE_OR_MIXED_BATCH", "Export is not audited")
    root = Path(root).resolve()
    parent = root / career
    parent.mkdir(parents=True, exist_ok=True)
    final = parent / batch
    if final.exists():
        sealed = load_snapshot(root, career, batch)
        if sealed['source_manifest'] != manifest:
            raise AccessError("STALE_OR_MIXED_BATCH", "Immutable batch already exists with different metadata")
        return sealed
    # Keep failed staging evidence; no recursive cleanup of potentially referenced facts.
    stage = Path(tempfile.mkdtemp(prefix='.preparing-', dir=parent))
    with zipfile.ZipFile(archive) as z:
        for name in (*DB_NAMES, 'audit.json', 'ingest_manifest.json', 'context.json', 'data_update.json'):
            entries = [i for i in z.infolist() if i.filename == name]
            cap = 512_000_000 if name in DB_NAMES else 4_000_000
            if len(entries) != 1 or entries[0].file_size > cap:
                raise AccessError("STALE_OR_MIXED_BATCH", "Missing, duplicate or oversized archive member")
            with z.open(name) as source, (stage / name).open('wb') as dest:
                while chunk := source.read(1024 * 1024):
                    dest.write(chunk)
    audit, ingest = read_json(stage/'audit.json'), read_json(stage/'ingest_manifest.json')
    update, context = read_json(stage/'data_update.json'), read_json(stage/'context.json')
    if any(update.get(k) != manifest.get(k) for k in ('save_id', 'snapshot_id', 'data_updated_at')) or context != manifest.get('context') or update.get('game_date') != context.get('game_date'):
        raise AccessError("STALE_OR_MIXED_BATCH", "Archive context or timestamps differ")
    validate_pair(stage, manifest, audit, ingest)
    # Reuse SQLite backup semantics, including WAL; never raw-copy an active database.
    for name in DB_NAMES:
        source_path = stage/name
        target_path = stage/(name+'.backup')
        with closing(ro(source_path)) as source, closing(sqlite3.connect(target_path)) as dest:
            source.backup(dest)
        os.replace(target_path, source_path)
    validate_pair(stage, manifest, audit, ingest)
    record = dict(schema_version=1, query_version=QUERY_VERSION, source_manifest=manifest,
                  audit_verdict='PASS_VERIFIED',
                  created_at=datetime.now(timezone.utc).isoformat(),
                  files={n: file_sha256(str(stage/n)) for n in DB_NAMES},
                  os_permissions='READ_ONLY_FILES_CONSUMER_ACL_REQUIRES_SEPARATE_PRINCIPAL_SETUP',
                  web_role_acceptance='DEFERRED_BY_PLAYER_2026_10_18')
    (stage/'manifest.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    for p in stage.iterdir():
        p.chmod(0o444)
    os.replace(stage, final)
    return record


def load_snapshot(root, career, batch):
    root = Path(root).resolve()
    directory = root/identifier(career)/identifier(batch)
    if directory.is_symlink() or not directory.resolve().is_relative_to(root):
        raise AccessError("BLOCKED_LOCAL_DB_ACCESS", "Symlink snapshots are not permitted")
    record = read_json(directory/'manifest.json')
    m = record['source_manifest']
    if m.get('save_id') != career or m.get('batch_id') != batch or record.get('audit_verdict') != 'PASS_VERIFIED':
        raise AccessError("STALE_OR_MIXED_BATCH", "Snapshot identity differs")
    for name in DB_NAMES:
        p = directory/name
        if p.is_symlink() or file_sha256(str(p)) != record['files'].get(name):
            raise AccessError("STALE_OR_MIXED_BATCH", "Sealed SQLite file changed")
        with closing(ro(p)) as c:
            expected = (m['snapshot_id'],career,m['data_updated_at'])
            if c.execute('SELECT snapshot_id,save_id,data_updated_at FROM data_sync_metadata WHERE snapshot_id=?',(m['snapshot_id'],)).fetchall() != [expected]:
                raise AccessError("STALE_OR_MIXED_BATCH", "Database capture binding differs")
    return record


def source_binding(record, published, career, batch):
    m = record['source_manifest']
    pointer = Path(published)/'saves'/career/'latest.json'
    latest = read_json(pointer) if pointer.is_file() else {}
    published_state = 'LOCAL_AUDITED_NOT_PUBLISHED'
    if latest.get('batch_id') == batch:
        if any(latest.get(k) != m.get(k) for k in ('save_id','data_updated_at')) or latest.get('game_date') != m.get('context',{}).get('game_date'):
            raise AccessError('STALE_OR_MIXED_BATCH','Published pointer and local capture differ')
        if latest.get('upload_status') == 'UPLOADED' and latest.get('uploaded_at'):
            published_state = 'PUBLISHED_CURRENT'
    elif latest.get('data_updated_at','') >= m['data_updated_at']:
        published_state = 'HISTORICAL_EXPLICIT_BATCH'
    return dict(career_id=career, snapshot_id=m['snapshot_id'],batch_id=batch,
                game_date=m.get('context',{}).get('game_date'),data_updated_at=m['data_updated_at'],
                publication_status=published_state, audit='PASS_VERIFIED', query_version=QUERY_VERSION,
                purpose=m.get('context',{}).get('purpose'),
                production_gm_eligible=published_state == 'PUBLISHED_CURRENT' and m.get('gm_decisions_allowed') is True)
