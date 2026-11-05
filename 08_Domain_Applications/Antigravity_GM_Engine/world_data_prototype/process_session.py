"""Fresh Windows process discovery and owner-only reconnect evidence.

A process epoch is never a save identity or a data-update declaration. No cached
address is accepted here, and reconnect does not ingest facts or refresh history.
"""
import ctypes,json,os
from ctypes import wintypes
from datetime import datetime,timezone
from pathlib import Path


def pid_argument(value):
    if value == 'auto':return None
    try:pid=int(value)
    except (ValueError,TypeError):raise ValueError('PID must be a positive integer or auto') from None
    if pid<=0:raise ValueError('PID must be a positive integer or auto')
    return pid


def discover_game_processes():
    """Toolhelp inventory of executable names only; never chooses one of many."""
    if os.name!='nt':raise OSError('Windows process discovery unavailable')
    class Entry(ctypes.Structure):
        _fields_=[('dwSize',wintypes.DWORD),('cntUsage',wintypes.DWORD),('th32ProcessID',wintypes.DWORD),
            ('th32DefaultHeapID',ctypes.c_size_t),('th32ModuleID',wintypes.DWORD),('cntThreads',wintypes.DWORD),
            ('th32ParentProcessID',wintypes.DWORD),('pcPriClassBase',wintypes.LONG),('dwFlags',wintypes.DWORD),('szExeFile',wintypes.WCHAR*260)]
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.CreateToolhelp32Snapshot.argtypes=[wintypes.DWORD,wintypes.DWORD];k.CreateToolhelp32Snapshot.restype=wintypes.HANDLE
    k.CloseHandle.argtypes=[wintypes.HANDLE];k.CloseHandle.restype=wintypes.BOOL
    for name in ('Process32FirstW','Process32NextW'):
        fn=getattr(k,name);fn.argtypes=[wintypes.HANDLE,ctypes.POINTER(Entry)];fn.restype=wintypes.BOOL
    handle=k.CreateToolhelp32Snapshot(2,0)
    if handle==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
    try:
        entry=Entry();entry.dwSize=ctypes.sizeof(entry);ok=k.Process32FirstW(handle,ctypes.byref(entry));found=[];count=0
        while ok:
            count+=1
            if count>65536:raise RuntimeError('process inventory exceeded bounded limit')
            if entry.szExeFile.lower()=='nba2k22.exe':found.append(int(entry.th32ProcessID))
            ok=k.Process32NextW(handle,ctypes.byref(entry))
        error=ctypes.get_last_error()
        if error not in (0,18):raise ctypes.WinError(error)
        return found
    finally:k.CloseHandle(handle)


def resolve_pid(pid=None):
    if pid is None or pid=='auto':
        found=discover_game_processes()
        if len(found)!=1:raise RuntimeError('expected one running NBA2K22.exe; observed '+str(len(found)))
        return found[0]
    if type(pid) is not int or pid<=0:raise ValueError('positive process ID or auto required')
    return pid


def handle_creation_time(k,handle):
    times=[wintypes.FILETIME() for _ in range(4)];fn=k.GetProcessTimes
    fn.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4;fn.restype=wintypes.BOOL
    if not fn(handle,*(ctypes.byref(value) for value in times)):raise ctypes.WinError(ctypes.get_last_error())
    return (times[0].dwHighDateTime<<32)|times[0].dwLowDateTime


def owner_identity():
    if os.name!='nt':return {'pid':os.getpid(),'creation_filetime':None}
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=wintypes.HANDLE
    return {'pid':os.getpid(),'creation_filetime':handle_creation_time(k,k.GetCurrentProcess())}


def owner_is_live(identity):
    """Missing handle/terminated/PID reuse is terminal; access denial is unknown."""
    if not identity or type(identity.get('pid')) is not int or type(identity.get('creation_filetime')) is not int:
        raise ValueError('cannot establish prior controller termination from this report')
    if os.name!='nt':raise OSError('Windows controller liveness check unavailable')
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE
    k.CloseHandle.argtypes=[wintypes.HANDLE];k.CloseHandle.restype=wintypes.BOOL
    k.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)];k.GetExitCodeProcess.restype=wintypes.BOOL
    handle=k.OpenProcess(0x1000,False,identity['pid'])
    if not handle:
        error=ctypes.get_last_error()
        if error==87:return False
        raise ctypes.WinError(error)
    try:
        if handle_creation_time(k,handle)!=identity['creation_filetime']:return False
        code=wintypes.DWORD()
        if not k.GetExitCodeProcess(handle,ctypes.byref(code)):raise ctypes.WinError(ctypes.get_last_error())
        return code.value==259
    finally:k.CloseHandle(handle)


def reconnect(save_directory,loaded_filename,new_output_directory,*,pid=None):
    """Reconnect to declared loaded save; never treats a restart as new facts."""
    from live_world import read_binding,bound_database
    from refresh import _context,_write
    binding,digest=read_binding(save_directory,loaded_filename);pid=resolve_pid(pid)
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False)
    context=_context(pid);state_path=Path(save_directory)/'process-session.json';previous=None
    if state_path.exists():
        previous=json.loads(state_path.read_bytes())
        if previous.get('save_id')!=binding['save_id'] or previous.get('native_save_filename')!=loaded_filename:raise ValueError('previous process-session save binding differs')
    epoch=context['epoch'];old=previous.get('epoch') if previous else None
    process_keys=('pid','creation_filetime','module_base','module_size','pe_timestamp')
    process_changed=None if old is None else any(old.get(k)!=epoch.get(k) for k in process_keys)
    progress=context.get('game_progress');old_progress=previous.get('game_progress') if previous else None
    progress_changed=None if old_progress is None else old_progress!=progress
    report={'format_version':1,'status':'RECONNECTED_NO_FACT_CAPTURE','save_id':binding['save_id'],'native_save_filename':loaded_filename,
        'binding_sha256':digest,'database_file':bound_database(save_directory,binding).name,'observed_at':datetime.now(timezone.utc).isoformat(),
        'epoch':epoch,'game_progress':progress,'previous_epoch':old,'process_changed':process_changed,'game_progress_changed':progress_changed,
        'data_update_declaration':'NOT_DECLARED; DEVELOPMENT_DEFAULT_SAME_SAVE_REOPENED',
        'loaded_save_identity_basis':'HUMAN_DECLARED_LOADED_SAVE_FILE; NOT_PROVEN_FROM_MEMORY_OR_PID',
        'root_resolution':'FRESH_EACH_CONNECTION_AND_EACH_SOURCE; NO_REUSED_DYNAMIC_ADDRESSES',
        'fact_units_created':0,'annual_refresh_triggered':False,'game_writes':False,'read_trace':context['read_trace'],
        'next_capture':'ONLY_ON_EXPLICIT_CAPTURE_REQUEST; RESTART_ALONE_NEVER_TRIGGERS_CAPTURE'}
    _write(out/'reconnect-report.json',report)
    _write(state_path,{key:value for key,value in report.items() if key not in ('read_trace','previous_epoch')})
    return report
