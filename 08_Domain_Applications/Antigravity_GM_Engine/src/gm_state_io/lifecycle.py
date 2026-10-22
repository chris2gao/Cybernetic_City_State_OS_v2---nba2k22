"""Coordinate the unchanged full pipeline and publisher with save lifecycle."""
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
import os
from uuid import uuid4
import save_context
from .common import atomic_json, binding, load, now
from .workspace import Workspaces, lifecycle_lock

LEASE_ENV='NBA2K22_DEV14_LIFECYCLE_LEASE'


def lease_path():
    return Path(save_context.DATABASE_DIR)/'.state_io_lease.json'


def owner_alive(pid):
    if os.name=='nt':
        # os.kill(pid, 0) is not a POSIX existence probe on Windows. Query only;
        # never send a signal or request process termination rights.
        import ctypes
        from ctypes import wintypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.DWORD)
        kernel.OpenProcess.restype=wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes=(wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD))
        kernel.GetExitCodeProcess.restype=wintypes.BOOL
        kernel.CloseHandle.argtypes=(wintypes.HANDLE,)
        kernel.CloseHandle.restype=wintypes.BOOL
        handle=kernel.OpenProcess(0x1000,False,pid)
        if not handle:
            return False
        try:
            code=wintypes.DWORD()
            return bool(kernel.GetExitCodeProcess(handle,ctypes.byref(code))) and code.value==259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid,0)
        return True
    except OSError:
        return False


def verify_lease(career):
    token=os.environ.get(LEASE_ENV)
    lease=load(lease_path())
    if not token or lease.get('token')!=token or lease.get('save_id')!=career:
        raise ValueError('INVALID_LIFECYCLE_LEASE')
    # Do not treat an orphaned token file as a live lock owner.
    if not owner_alive(lease['pid']):
        raise ValueError('LIFECYCLE_OWNER_NO_LONGER_RUNNING')
    return Workspaces().active(career,lease)


@contextmanager
def operation(career, name):
    manager=Workspaces()
    if not manager.path(career).exists():
        # Preserve the legacy tools when no DEV14 save has been enrolled, but
        # never let a legacy career bypass an already selected managed world.
        if (manager.root/'active_save.json').exists() and load(manager.root/'active_save.json').get('activation_status')=='ACTIVE':
            raise ValueError('LEGACY_CAREER_CANNOT_BYPASS_ACTIVE_WORKSPACE')
        yield None
        return
    if os.environ.get(LEASE_ENV):
        yield verify_lease(career)
        return
    if name=='capture':
        raise PermissionError('MANAGED_CAPTURE_REQUIRES_FULL_PIPELINE_LOADED_SAVE_CONFIRMATION')
    with lifecycle_lock():
        manager.idle()
        yield manager.active(career)


def guarded(name):
    def decorate(function):
        @wraps(function)
        def wrapped(save_id,*args,**kwargs):
            with operation(save_id,name):
                return function(save_id,*args,**kwargs)
        return wrapped
    return decorate


@contextmanager
def capture_lease(career, confirmation):
    with lifecycle_lock():
        manager=Workspaces()
        manager.idle()
        w=manager.active(career)
        if confirmation != ':'.join(binding(w).values()):
            raise PermissionError('GAME_SAVE_BINDING_UNVERIFIED_EXPLICIT_LOADED_SAVE_CONFIRMATION_REQUIRED')
        token=uuid4().hex
        lease=dict(**binding(w),token=token,pid=os.getpid(),operation='FULL_CAPTURE_AND_OPTIONAL_PUBLISH',created_at=now())
        atomic_json(lease_path(),lease)
        previous=os.environ.get(LEASE_ENV)
        os.environ[LEASE_ENV]=token
        try:
            yield w
        finally:
            if previous is None:
                os.environ.pop(LEASE_ENV,None)
            else:
                os.environ[LEASE_ENV]=previous
            # The OS lock remains authoritative; remove only our token record.
            if lease_path().exists() and load(lease_path()).get('token')==token:
                lease_path().unlink()
