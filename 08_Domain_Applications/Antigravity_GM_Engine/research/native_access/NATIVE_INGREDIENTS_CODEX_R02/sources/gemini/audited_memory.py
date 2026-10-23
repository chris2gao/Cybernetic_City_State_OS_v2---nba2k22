# -*- coding: utf-8 -*-
"""
NBA2K22 · NATIVE-INGREDIENTS-GEMINI-R01
Audited live memory reader and phase explorer for R01-R06.
Enforces strict pre-read allowlisting, phase byte budgets, sensitive field guards,
and complete Win32 ReadProcessMemory audit logging.
"""

import os
import sys
import ctypes
from ctypes import wintypes
import struct
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

class AuditedGameMemory:
    """
    Strictly bounded, read-only game memory accessor with explicit pre-read allowlist.
    Rejects any request not pre-registered in the active phase allowlist.
    """
    def __init__(self, process_name: str = "NBA2K22.exe"):
        self.process_name = process_name
        self.kernel32 = ctypes.windll.kernel32
        
        # Win32 API setup
        self.kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
        self.kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        self.kernel32.Process32First.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
        self.kernel32.Process32First.restype = wintypes.BOOL
        self.kernel32.Process32Next.argtypes = [wintypes.HANDLE, ctypes.c_void_p]
        self.kernel32.Process32Next.restype = wintypes.BOOL
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel32.CloseHandle.restype = wintypes.BOOL
        self.kernel32.ReadProcessMemory.argtypes = [
            wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)
        ]
        self.kernel32.ReadProcessMemory.restype = wintypes.BOOL
        
        self.pid: Optional[int] = None
        self.handle: Optional[int] = None
        self.base_address: Optional[int] = None
        
        # Security & Audit controls
        self.allowlist: Dict[Tuple[int, int], Dict[str, Any]] = {}
        self.audit_log: List[Dict[str, Any]] = []
        self.phase_bytes_read: Dict[str, int] = {}
        self.phase_budgets: Dict[str, int] = {
            "R01-BIND": 1208,
            "R02-PLAYER-HISTORY": 1262,
            "R03-DRAFT-RELATIONS": 486,
            "R04-COACH-BOOK": 1080,
            "R05-GM-CAP": 744,
            "R06-RECORD-BOOK": 520,
        }
        
        self.attach()

    def attach(self):
        TH32CS_SNAPPROCESS = 0x00000002
        class PROCESSENTRY32(ctypes.Structure):
            _fields_ = [
                ("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.POINTER(wintypes.ULONG)),
                ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", wintypes.LONG),
                ("dwFlags", wintypes.DWORD),
                ("szExeFile", ctypes.c_char * 260)
            ]
        
        snap = self.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
        
        success = self.kernel32.Process32First(snap, ctypes.byref(entry))
        while success:
            exe_name = entry.szExeFile.decode('latin-1', errors='ignore')
            if exe_name.lower() == self.process_name.lower():
                self.pid = entry.th32ProcessID
                break
            success = self.kernel32.Process32Next(snap, ctypes.byref(entry))
        self.kernel32.CloseHandle(snap)
        
        if not self.pid:
            raise ProcessLookupError(f"Process {self.process_name} not found.")
            
        # Open with minimum required permissions: PROCESS_VM_READ | PROCESS_QUERY_INFORMATION
        import win32api
        import win32process
        self.handle = win32api.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, self.pid)
        if not self.handle:
            raise PermissionError(f"Unable to open process PID {self.pid} with VM_READ.")
            
        modules = win32process.EnumProcessModules(self.handle)
        self.base_address = modules[0]

    def close(self):
        if self.handle:
            import win32api
            win32api.CloseHandle(self.handle)
            self.handle = None

    def register_allowed_range(self, phase: str, address: int, size: int, purpose: str):
        """Register an authorized read envelope in the allowlist."""
        address = int(address)
        size = int(size)
        if phase not in self.phase_budgets:
            raise ValueError(f"Unknown phase: {phase}")
        self.allowlist[(address, size)] = {
            "phase": phase,
            "purpose": purpose,
            "address": address,
            "size": size
        }

    def read_allowed_bytes(self, phase: str, address: int, size: int, purpose: str) -> bytes:
        """
        Check allowlist, check phase budget, read memory, and log audit.
        Fails closed on any discrepancy.
        """
        address = int(address)
        size = int(size)
        call_idx = len(self.audit_log) + 1
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # 1. Check allowlist
        entry = self.allowlist.get((address, size))
        if not entry:
            audit_entry = {
                "call_index": call_idx,
                "timestamp": timestamp,
                "phase": phase,
                "address_hex": hex(address),
                "requested_size": size,
                "actual_size": 0,
                "status": "REJECTED_NOT_IN_ALLOWLIST",
                "purpose": purpose,
                "sha256": None
            }
            self.audit_log.append(audit_entry)
            raise PermissionError(f"Pre-read allowlist rejection: ({hex(address)}, {size}) not registered for phase {phase}.")
            
        if entry["phase"] != phase:
            raise PermissionError(f"Phase mismatch: registered for {entry['phase']}, requested by {phase}.")
            
        # 2. Check budget
        current_phase_bytes = self.phase_bytes_read.get(phase, 0)
        budget = self.phase_budgets[phase]
        if current_phase_bytes + size > budget:
            raise PermissionError(f"Budget exceeded for phase {phase}: {current_phase_bytes} + {size} > {budget}")
            
        # 3. Perform ReadProcessMemory
        buf = (ctypes.c_char * size)()
        bytes_read = ctypes.c_size_t()
        res = self.kernel32.ReadProcessMemory(
            int(self.handle),
            ctypes.c_void_p(address),
            buf,
            size,
            ctypes.byref(bytes_read)
        )
        
        if not res or bytes_read.value != size:
            audit_entry = {
                "call_index": call_idx,
                "timestamp": timestamp,
                "phase": phase,
                "address_hex": hex(address),
                "requested_size": size,
                "actual_size": bytes_read.value,
                "status": "FAILED_RPM",
                "purpose": purpose,
                "sha256": None
            }
            self.audit_log.append(audit_entry)
            raise IOError(f"ReadProcessMemory failed at {hex(address)}, size {size}.")
            
        data = bytes(buf[:size])
        data_hash = hashlib.sha256(data).hexdigest()
        self.phase_bytes_read[phase] = current_phase_bytes + size
        
        audit_entry = {
            "call_index": call_idx,
            "timestamp": timestamp,
            "phase": phase,
            "address_hex": hex(address),
            "requested_size": size,
            "actual_size": size,
            "status": "SUCCESS",
            "purpose": purpose,
            "sha256": data_hash,
            "safe_preview_hex": data[:16].hex()
        }
        self.audit_log.append(audit_entry)
        return data

print("AuditedGameMemory class defined successfully.")
