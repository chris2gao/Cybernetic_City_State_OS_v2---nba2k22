"""One active physical save, generation manifests, sealed resets and shared leases."""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
import hashlib
import os
import sqlite3
from uuid import uuid4
import save_context
from .common import atomic_json, binding, digest, load, now
from .store import connect, initialize

_held = ContextVar('dev14_lifecycle_lock', default=0)
UNRESOLVED = ('APPLYING', 'PREFLIGHT_OK', 'PREPARED', 'PARTIAL_UNRECOVERED',
              'PARTIAL_UNRECOVERED_MANUAL_REVIEW', 'RESET_INTERRUPTED_BLOCKED')


@contextmanager
def lifecycle_lock():
    """OS lease released on crash; unresolved write state is separately durable."""
    if _held.get():
        yield
        return
    root = Path(save_context.DATABASE_DIR)
    root.mkdir(parents=True, exist_ok=True)
    f = (root / '.state_io_lifecycle.lock').open('a+b')
    f.seek(0, 2)
    if not f.tell():
        f.write(b'0')
        f.flush()
    f.seek(0)
    acquired = False
    try:
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        acquired = True
        token = _held.set(1)
        try:
            yield
        finally:
            _held.reset(token)
    except (BlockingIOError, OSError) as exc:
        if not acquired:
            raise RuntimeError('STATE_IO_LIFECYCLE_BUSY') from exc
        raise
    finally:
        if acquired:
            f.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        f.close()


class Workspaces:
    @property
    def root(self):
        return Path(save_context.DATABASE_DIR)

    def path(self, save_id):
        return self.root / 'saves' / save_context.validate_save_id(save_id) / 'workspace.json'

    def read(self, save_id):
        if save_id == 'legacy-shared':
            raise ValueError('EXPLICIT_ISOLATED_SAVE_REQUIRED')
        w = load(self.path(save_id))
        if w['save_id'] != save_id or w['manifest_digest'] != digest({k: v for k, v in w.items() if k != 'manifest_digest'}):
            raise ValueError('INVALID_WORKSPACE_MANIFEST')
        return w

    def write(self, w):
        w = {k: v for k, v in w.items() if k != 'manifest_digest'}
        w['manifest_digest'] = digest(w)
        atomic_json(self.path(w['save_id']), w)
        return w

    def list(self):
        return [self.read(p.parent.name) for p in sorted((self.root/'saves').glob('*/workspace.json'))]

    def active(self, save_id=None, expected=None):
        pointer = load(self.root/'active_save.json') if (self.root/'active_save.json').exists() else None
        if not pointer or pointer.get('activation_status') != 'ACTIVE':
            raise ValueError('NO_ACTIVE_SAVE')
        if save_id is not None and pointer['save_id'] != save_id:
            raise ValueError('REQUESTED_SAVE_IS_NOT_ACTIVE')
        w = self.read(pointer['save_id'])
        journal=self.path(w['save_id']).parent/'reset_activation.json'
        if journal.exists() and load(journal).get('status')=='PREPARED':
            raise ValueError('RESET_INTERRUPTED_BLOCKED')
        if binding(pointer) != binding(w) or (expected is not None and binding(expected) != binding(w)):
            raise ValueError('STALE_SAVE_GENERATION')
        if w['lifecycle_status'] in ('RETIRED', 'RESET_INTERRUPTED_BLOCKED'):
            raise ValueError(w['lifecycle_status'])
        self.check_databases(w)
        return w

    def check_databases(self, w):
        from .capture_files import metadata, sync_origin, require_complete, SOURCE_KEYS
        paths = save_context.save_paths(w['save_id'])
        require_complete(paths)
        metas, origins = {}, {}
        for key, table in (('db_path', 'save_metadata'), ('player_pool_db_path', 'save_metadata'),
                           ('control_db_path', 'control_metadata')):
            p = Path(paths[key])
            if not p.exists():
                raise ValueError('POOL_SAVE_BINDING_MISMATCH' if key == 'player_pool_db_path' else 'WORKSPACE_DATABASE_MISSING')
            c = sqlite3.connect(p.as_uri()+'?mode=ro', uri=True)
            try:
                meta = metadata(c, table)
                if any(meta.get(k) != v for k, v in binding(w).items()):
                    raise ValueError('POOL_SAVE_BINDING_MISMATCH' if key == 'player_pool_db_path' else 'WORKSPACE_DATABASE_BINDING_MISMATCH')
                metas[key] = meta
                if key != 'control_db_path':
                    origins[key] = sync_origin(c)
            finally:
                c.close()
        if origins['db_path'] != origins['player_pool_db_path']:
            raise ValueError('POOL_SOURCE_METADATA_MISMATCH')
        origin = origins['db_path']
        if origin and origin[1] != w['save_id']:
            raise ValueError('POOL_SAVE_BINDING_MISMATCH')
        # Before the first hardened capture older enrolled generations have only
        # binding metadata. Once any source token exists, require it in all three.
        if any(k in meta for meta in metas.values() for k in SOURCE_KEYS):
            expected = {k: metas['db_path'].get(k) for k in SOURCE_KEYS}
            if not all(expected.values()) or any(any(meta.get(k) != v for k,v in expected.items()) for meta in metas.values()):
                raise ValueError('POOL_SOURCE_METADATA_MISMATCH')
            if not origin or origin != (expected['capture_snapshot_id'], w['save_id'], expected['capture_updated_at']):
                raise ValueError('POOL_SOURCE_METADATA_MISMATCH')
        return paths

    def idle(self, *, recovering_capture=None):
        from .capture_files import require_complete
        from coaching_execution_lock import DEFAULT_LOCK_ROOT
        if DEFAULT_LOCK_ROOT.exists():
            for path in DEFAULT_LOCK_ROOT.glob('*.lock'):
                if load(path).get('status')=='WRITE_PHASE_UNRESOLVED_UNTIL_JOURNAL_FINALIZED':
                    raise RuntimeError('UNRESOLVED_NATIVE_WRITE_REQUIRES_MANUAL_REVIEW')
        for w in self.list():
            if w['save_id'] != recovering_capture:
                require_complete(save_context.save_paths(w['save_id']))
            journal=self.path(w['save_id']).parent/'reset_activation.json'
            if journal.exists() and load(journal).get('status')=='PREPARED':
                raise RuntimeError('RESET_INTERRUPTED_BLOCKED')
            if w['lifecycle_status'] == 'RESET_INTERRUPTED_BLOCKED':
                raise RuntimeError('RESET_INTERRUPTED_BLOCKED')
            p = Path(save_context.save_paths(w['save_id'])['control_db_path'])
            if not p.exists():
                continue
            with connect(p) as c:
                rows = c.execute('SELECT status FROM execution_runs').fetchall()
                if any(r[0] in UNRESOLVED for r in rows):
                    raise RuntimeError('UNRESOLVED_WRITE_BLOCKS_SAVE_LIFECYCLE')

    def recover_capture(self, save_id, confirmation):
        """Explicit last-good restoration; never auto-unlock native write state."""
        from .capture_files import restore, journal_path
        with lifecycle_lock():
            w = self.read(save_id)
            if confirmation != w['manifest_digest']:
                raise PermissionError('EXPLICIT_CAPTURE_RECOVERY_MANIFEST_REQUIRED')
            self.idle(recovering_capture=save_id)
            paths = save_context.save_paths(save_id)
            journal = load(journal_path(paths))
            if journal['status'] != 'PREPARED':
                raise ValueError('NO_INCOMPLETE_CAPTURE_TO_RECOVER')
            restore(paths, journal)
            self.check_databases(w)
            return dict(status='LAST_GOOD_CAPTURE_RESTORED', **binding(w))

    def _fresh(self, w, paths):
        save_context.initialize_save(paths)
        with connect(paths['db_path']) as c:
            c.executemany('INSERT OR REPLACE INTO save_metadata VALUES (?,?)', binding(w).items())
        # Fresh pool contains no observations, never copied from the old world.
        with connect(paths['player_pool_db_path']) as c:
            c.execute('CREATE TABLE IF NOT EXISTS save_metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
            c.executemany('INSERT OR REPLACE INTO save_metadata VALUES (?,?)', binding(w).items())
        initialize(paths['control_db_path'], w)

    def create(self, save_id):
        save_context.validate_save_id(save_id)
        if save_id == 'legacy-shared':
            raise ValueError('EXPLICIT_ISOLATED_SAVE_REQUIRED')
        with lifecycle_lock():
            self.idle()
            if len([w for w in self.list() if w['lifecycle_status'] != 'RETIRED']) >= 4:
                raise ValueError('FOUR_SAVE_LIMIT')
            p = self.path(save_id)
            if p.exists() or (p.parent.exists() and any(p.parent.iterdir())):
                raise ValueError('SAVE_ALREADY_EXISTS_USE_EXPLICIT_ADOPT_OR_NEW_ID')
            w = dict(save_id=save_id, save_instance_id=uuid4().hex, generation_id=uuid4().hex,
                     schema_version=1, created_at=now(), lifecycle_status='NEW_UNCAPTURED', data_directory='.')
            paths = save_context.save_paths(save_id)
            self._fresh(w, paths)
            return self.write(w)

    def adopt(self, save_id, confirmation):
        """Explicitly bind an existing physical career, without claiming a new capture."""
        if confirmation != save_id:
            raise PermissionError('EXPLICIT_EXISTING_SAVE_ADOPTION_REQUIRED')
        with lifecycle_lock():
            self.idle()
            if self.path(save_id).exists():
                raise ValueError('SAVE_ALREADY_REGISTERED')
            if len([w for w in self.list() if w['lifecycle_status'] != 'RETIRED']) >= 4:
                raise ValueError('FOUR_SAVE_LIMIT')
            paths = save_context.save_paths(save_id)
            if not Path(paths['db_path']).exists():
                raise ValueError('EXISTING_SAVE_REQUIRED')
            # Adoption is a conscious enrollment of an existing complete cohort,
            # never permission to relabel a foreign/missing pool.
            from contextlib import closing
            from .capture_files import sync_origin, put_metadata
            if not Path(paths['player_pool_db_path']).exists():
                raise ValueError('POOL_SAVE_BINDING_MISMATCH')
            origins = []
            for key in ('db_path', 'player_pool_db_path'):
                with closing(sqlite3.connect(Path(paths[key]).as_uri()+'?mode=ro', uri=True)) as c:
                    origins.append(sync_origin(c))
                    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                    if 'save_metadata' in tables:
                        prior = dict(c.execute('SELECT key,value FROM save_metadata'))
                        if prior.get('save_id', save_id) != save_id or any(prior.get(k) for k in ('save_instance_id','generation_id')):
                            raise ValueError('EXISTING_DATABASE_ALREADY_BOUND')
            if origins[0] is None or origins[0] != origins[1] or origins[0][1] != save_id:
                raise ValueError('POOL_SOURCE_METADATA_MISMATCH')
            save_context.create_or_open_save(save_id)
            w = dict(save_id=save_id, save_instance_id=uuid4().hex, generation_id=uuid4().hex,
                     schema_version=1, created_at=now(), lifecycle_status='NEW_UNCAPTURED', data_directory='.')
            with connect(paths['db_path']) as c:
                c.executemany('INSERT OR REPLACE INTO save_metadata VALUES (?,?)', binding(w).items())
            with connect(paths['player_pool_db_path']) as c:
                put_metadata(c, binding(w))
            initialize(paths['control_db_path'], w)
            return self.write(w)

    def activate(self, save_id):
        with lifecycle_lock():
            self.idle()
            w = self.read(save_id)
            if w['lifecycle_status'] == 'RETIRED':
                raise ValueError('RETIRED_SAVE')
            self.check_databases(w)
            atomic_json(self.root/'active_save.json', dict(**binding(w), activation_status='ACTIVE', activated_at=now()))
            return w

    def deactivate(self):
        with lifecycle_lock():
            self.idle()
            atomic_json(self.root/'active_save.json', dict(activation_status='INACTIVE', activated_at=now()))

    def retire(self, save_id, confirmation):
        with lifecycle_lock():
            self.idle()
            w = self.read(save_id)
            if confirmation != w['manifest_digest']:
                raise PermissionError('EXPLICIT_RETIRE_MANIFEST_APPROVAL_REQUIRED')
            if (self.root/'active_save.json').exists():
                p = load(self.root/'active_save.json')
                if p.get('save_id') == save_id:
                    self.deactivate()
            w['lifecycle_status'] = 'RETIRED'
            return self.write(w)

    def reset_plan(self, save_id):
        w = self.read(save_id)
        self.check_databases(w)
        return dict(**binding(w), manifest_digest=w['manifest_digest'],
                    archive=str(self.path(save_id).parent/'reset_archives'/w['generation_id']),
                    databases=['league_state.sqlite', 'player_pool.sqlite', 'gm_control.sqlite'],
                    approval_required=True, published_history_preserved=True)

    def reset(self, save_id, generation, confirmation, *, fault=None):
        with lifecycle_lock():
            self.idle()
            old = self.read(save_id)
            if generation != old['generation_id'] or confirmation != old['manifest_digest']:
                raise PermissionError('EXACT_SAVE_GENERATION_MANIFEST_APPROVAL_REQUIRED')
            # Old published protocol has no generation. Never point it at a new world.
            published = Path(save_context.PROJECT_DIR)/'published/saves'/save_id
            if published.exists() and any(published.iterdir()):
                raise ValueError('BLOCKED_UNSUPPORTED_GENERATION:CREATE_NEW_SAVE_ID')
            paths = self.check_databases(old)
            archive = self.path(save_id).parent/'reset_archives'/old['generation_id']/uuid4().hex
            archive.mkdir(parents=True, exist_ok=True)
            manifest = dict(**binding(old), created_at=now(), files={}, workspace=old)
            for name in ('league_state.sqlite', 'player_pool.sqlite', 'gm_control.sqlite'):
                source = Path(paths['data_dir'])/name
                if not source.exists():
                    raise ValueError('RESET_REQUIRES_ALL_THREE_DATABASES')
                target = archive/name
                if not target.exists():
                    src = sqlite3.connect(source.as_uri()+'?mode=ro', uri=True)
                    dst = sqlite3.connect(target)
                    try:
                        src.backup(dst)
                    finally:
                        dst.close()
                        src.close()
                check = sqlite3.connect(target.as_uri()+'?mode=ro', uri=True)
                try:
                    if check.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                        raise ValueError('RESET_ARCHIVE_VALIDATION_FAILED')
                finally:
                    check.close()
                manifest['files'][name] = hashlib.sha256(target.read_bytes()).hexdigest()
            # Journals are kept in the immutable old generation directory; archive
            # their contents as well so the sealed backup is independently usable.
            import shutil
            journal_dir = Path(paths['data_dir'])/'state_io_journals'
            if journal_dir.exists():
                shutil.copytree(journal_dir, archive/'state_io_journals', dirs_exist_ok=True)
                for p in (archive/'state_io_journals').rglob('*.json'):
                    manifest['files'][p.relative_to(archive).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
            atomic_json(archive/'manifest.json', manifest)
            for name, expected in manifest['files'].items():
                if hashlib.sha256((archive/name).read_bytes()).hexdigest() != expected:
                    raise ValueError('RESET_ARCHIVE_VALIDATION_FAILED')
            if fault:
                fault('archive_verified')
            fresh = dict(old, save_instance_id=uuid4().hex, generation_id=uuid4().hex, created_at=now(), lifecycle_status='NEW_UNCAPTURED')
            fresh.pop('last_snapshot_id',None)
            fresh['data_directory'] = 'generations/'+fresh['generation_id']
            directory = self.path(save_id).parent/fresh['data_directory']
            new_paths = dict(paths, data_dir=str(directory), db_path=str(directory/'league_state.sqlite'),
                             player_pool_db_path=str(directory/'player_pool.sqlite'), control_db_path=str(directory/'gm_control.sqlite'),
                             snapshots_dir=str(directory/'snapshots'), backups_dir=str(directory/'backups'),
                             evaluations_dir=str(directory/'evaluations'))
            self._fresh(fresh, new_paths)
            if fault:
                fault('generation_prepared')
            journal = self.path(save_id).parent/'reset_activation.json'
            atomic_json(journal, dict(status='PREPARED', old=old, new=fresh, archive=str(archive)))
            try:
                self.write(fresh)  # single data-generation commit for all three DBs
                if fault:
                    fault('manifest_committed')
                if (self.root/'active_save.json').exists():
                    p = load(self.root/'active_save.json')
                    if p.get('save_id') == save_id:
                        atomic_json(self.root/'active_save.json', dict(**binding(fresh), activation_status='ACTIVE', activated_at=now()))
                if fault:
                    fault('active_committed')
                atomic_json(journal, dict(status='COMMITTED', old=old, new=fresh, archive=str(archive)))
            except BaseException:
                # Synchronous failure restores the single old commit. If a process
                # dies here, active() rejects the mismatch; recover() is explicit.
                self.write(old)
                if (self.root/'active_save.json').exists() and load(self.root/'active_save.json').get('save_id')==save_id:
                    atomic_json(self.root/'active_save.json', dict(**binding(old), activation_status='ACTIVE', activated_at=now()))
                atomic_json(journal, dict(status='RESTORED_OLD', old=old, new=fresh, archive=str(archive)))
                raise
            return self.read(save_id)

    def recover(self, save_id, confirmation):
        with lifecycle_lock():
            journal = self.path(save_id).parent/'reset_activation.json'
            j = load(journal)
            if confirmation != j['old']['manifest_digest']:
                raise PermissionError('RESET_RECOVERY_APPROVAL_REQUIRED')
            if j['status'] != 'PREPARED':
                return dict(status=j['status'])
            self.write(j['old'])
            if (self.root/'active_save.json').exists() and load(self.root/'active_save.json').get('save_id') == save_id:
                atomic_json(self.root/'active_save.json', dict(**binding(j['old']), activation_status='ACTIVE', activated_at=now()))
            atomic_json(journal, dict(j, status='RESTORED_OLD'))
            return dict(status='RESTORED_OLD')
