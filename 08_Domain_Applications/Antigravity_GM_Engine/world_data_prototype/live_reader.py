"""Bounded read-only Windows probe for known AG01D SEASON/Box layout candidates.

Owner-initiated evidence acquisition, not a background worker or a save-binding
oracle. No writes/injection/debug privilege elevation. Missing Windows access is
reported as such; no automatic elevation or synthetic fallback.
"""
from __future__ import annotations
import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import struct
from readers import _module

SEASON_RVA=0x0632B4B8
GAME_OFFSET=0x28
GAME_STRIDE=60
RESEARCH_GAME_CAPACITY=1232
STATBANK_OFFSET=0x1B6AC
RESEARCH_STAT_CAPACITY=45292


class ReadOnlyGameProcess:
    """Minimal handle whose requested access is VM_READ | QUERY_LIMITED_INFO."""
    def __init__(self,pid):
        if os.name!='nt':raise OSError('Windows process reader unavailable on this platform')
        self.pid=pid;self.trace=[];self.handle=None
        k=ctypes.WinDLL('kernel32',use_last_error=True);self.k=k
        k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE
        k.CloseHandle.argtypes=[wintypes.HANDLE];k.CloseHandle.restype=wintypes.BOOL
        k.ReadProcessMemory.argtypes=[wintypes.HANDLE,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)];k.ReadProcessMemory.restype=wintypes.BOOL
        k.QueryFullProcessImageNameW.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)];k.QueryFullProcessImageNameW.restype=wintypes.BOOL
        self.handle=k.OpenProcess(0x1010,False,pid)
        self.trace.append({'operation':'OpenProcess','pid':pid,'requested_access':'0x1010 VM_READ|QUERY_LIMITED_INFORMATION',
                           'success':bool(self.handle),'winerror':0 if self.handle else ctypes.get_last_error()})
        if not self.handle:
            error=ctypes.WinError(ctypes.get_last_error());error.read_trace=list(self.trace);raise error
        try:
            size=wintypes.DWORD(32768);buffer=ctypes.create_unicode_buffer(size.value)
            if not k.QueryFullProcessImageNameW(self.handle,0,buffer,ctypes.byref(size)):raise ctypes.WinError(ctypes.get_last_error())
            if Path(buffer.value).name.lower()!='nba2k22.exe':raise PermissionError('PID is not NBA2K22.exe')
            self.image_name='NBA2K22.exe'
            self.module_base,self.module_size=self._module()
        except BaseException:
            self.close();raise

    def _module(self):
        class Entry(ctypes.Structure):
            _fields_=[('dwSize',wintypes.DWORD),('th32ModuleID',wintypes.DWORD),('th32ProcessID',wintypes.DWORD),
                ('GlblcntUsage',wintypes.DWORD),('ProccntUsage',wintypes.DWORD),('modBaseAddr',ctypes.POINTER(ctypes.c_ubyte)),
                ('modBaseSize',wintypes.DWORD),('hModule',wintypes.HMODULE),('szModule',wintypes.WCHAR*256),('szExePath',wintypes.WCHAR*260)]
        k=self.k;k.CreateToolhelp32Snapshot.argtypes=[wintypes.DWORD,wintypes.DWORD];k.CreateToolhelp32Snapshot.restype=wintypes.HANDLE
        k.Module32FirstW.argtypes=[wintypes.HANDLE,ctypes.POINTER(Entry)];k.Module32FirstW.restype=wintypes.BOOL
        k.Module32NextW.argtypes=[wintypes.HANDLE,ctypes.POINTER(Entry)];k.Module32NextW.restype=wintypes.BOOL
        snap=k.CreateToolhelp32Snapshot(0x18,self.pid)
        if snap==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
        try:
            item=Entry();item.dwSize=ctypes.sizeof(item);ok=k.Module32FirstW(snap,ctypes.byref(item))
            while ok:
                if item.szModule.lower()=='nba2k22.exe':
                    return ctypes.cast(item.modBaseAddr,ctypes.c_void_p).value,item.modBaseSize
                ok=k.Module32NextW(snap,ctypes.byref(item))
            raise RuntimeError('NBA2K22 module not observed')
        finally:k.CloseHandle(snap)

    def read(self,address,size,label):
        if not self.handle:raise RuntimeError('reader handle closed')
        if not isinstance(size,int) or not 1<=size<=52*24:raise ValueError('bounded read length exceeded')
        if not 0x10000<=address<0x00007FFFFFFFFFFF:raise ValueError('non-canonical user address')
        raw=ctypes.create_string_buffer(size);count=ctypes.c_size_t()
        ok=self.k.ReadProcessMemory(self.handle,ctypes.c_void_p(address),raw,size,ctypes.byref(count))
        entry={'operation':'ReadProcessMemory','pid':self.pid,'label':label,'address':hex(address),'requested_bytes':size,
               'returned_bytes':count.value,'success':bool(ok) and count.value==size,'winerror':0 if ok else ctypes.get_last_error()}
        if entry['success']:entry['sha256']=hashlib.sha256(raw.raw).hexdigest()
        self.trace.append(entry)
        if not entry['success']:raise OSError('bounded read incomplete: '+label)
        return raw.raw

    def close(self):
        if self.handle:self.k.CloseHandle(self.handle);self.handle=None


def collect_known_game(reader,game_index):
    """Only explicit known families; capacities are research bounds, not active counts."""
    if not isinstance(game_index,int) or not 0<=game_index<RESEARCH_GAME_CAPACITY:raise ValueError('game index outside research capacity')
    if SEASON_RVA+8>reader.module_size:raise ValueError('research RVA outside current module')
    pointer=reader.read(reader.module_base+SEASON_RVA,8,'SEASON_POINTER_RVA_CANDIDATE')
    season=struct.unpack('<Q',pointer)[0]
    header=reader.read(season,64,'SEASON_HEADER')
    game=reader.read(season+GAME_OFFSET+game_index*GAME_STRIDE,GAME_STRIDE,'ONE_SEASON_GAME')
    decoder=_module('boxscore_decoder').BoxScoreDecoder
    decoded=decoder.decode_game_header(game)
    datetime.strptime(decoded['game_date'],'%Y-%m-%d')
    if decoded['home_team_id']==decoded['away_team_id']:raise ValueError('candidate game teams identical')
    meta=decoded['boxscore_meta'];count=meta['num_home_players']+meta['num_away_players'];idx=meta['stat_lines_index']
    if not 0<=meta['num_home_players']<=26 or not 0<=meta['num_away_players']<=26 or not 1<=count<=52:
        raise ValueError('participant count outside bounded candidate window')
    if idx+count>RESEARCH_STAT_CAPACITY:raise ValueError('candidate StatBank index exceeds research capacity')
    if decoded['status']!=2:raise ValueError('selected game is not final under candidate layout; no Box read')
    raw=reader.read(season+STATBANK_OFFSET+idx*24,count*24,'ONE_GAME_PARTICIPANT_STATBANK')
    full=decoder.decode_full_boxscore(game,raw)
    return {'header':header,'game':game,'box':raw,'decoded':full,'season_pointer':hex(season),
        'layout_grade':'KNOWN_RESEARCH_LAYOUT_PLAUSIBILITY_ONLY','save_binding':'UNKNOWN_NOT_INFERRED_FROM_PID',
        'active_schedule_window':'NOT_PROVEN','capacity_source':'AG_NATIVE_01D research, not a newly proven active count'}


def probe(pid,new_output_directory,game_index=0):
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False)
    result={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_index':game_index,
        'source_mode':'LIVE_READ_ATTEMPT','game_writes':False,'save_binding':'UNKNOWN','source_facts_ingested':False}
    reader=None
    try:
        reader=ReadOnlyGameProcess(pid)
        found=collect_known_game(reader,game_index)
        for name in ('header','game','box'):(out/(name+'.bin')).write_bytes(found[name])
        (out/'decoded-game.json').write_text(json.dumps(found['decoded'],ensure_ascii=False,indent=2),encoding='utf-8')
        result.update({'status':'BOUNDED_LIVE_BYTES_CAPTURED_NOT_FULL_ACCEPTANCE','module_base':hex(reader.module_base),
                       'module_size':reader.module_size,**{k:v for k,v in found.items() if k not in ('header','game','box','decoded')}})
    except (OSError,ValueError,RuntimeError) as error:
        result.update({'status':'SOURCE_UNAVAILABLE','error_type':type(error).__name__,'winerror':getattr(error,'winerror',None),
                       'reason':str(error),'read_trace':getattr(error,'read_trace',[])})
    finally:
        if reader:result['read_trace']=reader.trace;reader.close()
    result['artifact_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    (out/'live-probe-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('pid',type=int);p.add_argument('new_output_directory');p.add_argument('--game-index',type=int,default=0);a=p.parse_args()
    r=probe(a.pid,a.new_output_directory,a.game_index)
    print(json.dumps({k:r.get(k) for k in ('status','pid','winerror','save_binding','source_facts_ingested')}))
    raise SystemExit(0 if r['status']=='BOUNDED_LIVE_BYTES_CAPTURED_NOT_FULL_ACCEPTANCE' else 2)
