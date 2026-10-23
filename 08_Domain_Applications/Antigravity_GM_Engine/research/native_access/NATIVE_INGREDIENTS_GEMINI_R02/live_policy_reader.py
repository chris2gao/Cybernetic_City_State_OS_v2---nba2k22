# -*- coding: utf-8 -*-
"""
NBA2K22 · NATIVE-INGREDIENTS-GEMINI-R02
Windows Live Policy-Enforcing Memory Reader.
Loads an externally pinned policy manifest, verifies process binding,
enforces pre-read permits, phase budgets, and sensitive range overrides before RPM.
"""

import os
import sys
import ctypes
from ctypes import wintypes
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

PINNED_POLICY_SHA256 = "c95b696c0210b944520eec96d2a288ba8dc26fd2a6deeb1326ea6d55d4798abc"
PINNED_IMAGE_SHA256 = "1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5"

class PolicyDenied(PermissionError):
    pass

class WindowsLivePolicyReader:
    def __init__(self, policy_path: str, pinned_digest: str = PINNED_POLICY_SHA256):
        self.policy_path = Path(policy_path)
        self.pinned_digest = pinned_digest
        
        # 1. Load and verify policy manifest
        raw_policy = self.policy_path.read_bytes()
        actual_digest = hashlib.sha256(raw_policy).hexdigest()
        if actual_digest != self.pinned_digest:
            raise PolicyDenied(f"Policy manifest digest mismatch: {actual_digest} != {self.pinned_digest}")
            
        self.policy_data = json.loads(raw_policy.decode("utf-8"))
        if self.policy_data.get("mode") != "WINDOWS_LIVE_READ_PROCESS_MEMORY":
            raise PolicyDenied(f"Unsupported policy mode: {self.policy_data.get('mode')}")
            
        self.binding_spec = self.policy_data["binding"]
        self.phase_budgets = self.policy_data["phase_budgets"]
        self.permits = {p["key"]: p for p in self.policy_data["permits"]}
        self.denied_ranges = [(int(d["address"], 16), d["size"]) for d in self.policy_data["denied_ranges"]]
        
        # Runtime tracking
        self.permit_calls = {k: 0 for k in self.permits}
        self.phase_bytes_used = {k: 0 for k in self.phase_budgets}
        self.audit_log: List[Dict[str, Any]] = []
        
        # Win32 kernel32 setup
        self.kernel32 = ctypes.windll.kernel32
        self.kernel32.ReadProcessMemory.argtypes = [
            wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)
        ]
        self.kernel32.ReadProcessMemory.restype = wintypes.BOOL
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel32.CloseHandle.restype = wintypes.BOOL
        
        self.handle: Optional[int] = None
        self.actual_pid: Optional[int] = None
        self.actual_base: Optional[int] = None
        self._bind_and_attach()

    def _bind_and_attach(self):
        import win32api
        import win32process
        
        expected_pid = self.binding_spec["pid"]
        self.actual_pid = expected_pid
        
        # Open process with minimum required permissions: VM_READ | QUERY_INFORMATION
        self.handle = win32api.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, self.actual_pid)
        if not self.handle:
            raise PermissionError(f"Failed to open process PID {self.actual_pid} with PROCESS_VM_READ.")
            
        modules = win32process.EnumProcessModules(self.handle)
        self.actual_base = modules[0]
        
        expected_base = int(self.binding_spec["module_base"], 16)
        if self.actual_base != expected_base:
            self.close()
            raise PolicyDenied(f"Module base mismatch: {hex(self.actual_base)} != {hex(expected_base)}")
            
        if self.binding_spec["image_sha256"] != PINNED_IMAGE_SHA256:
            self.close()
            raise PolicyDenied("Image SHA256 in policy is not pinned image hash.")

    def close(self):
        if self.handle:
            import win32api
            win32api.CloseHandle(self.handle)
            self.handle = None

    def read_permit(self, key: str, phase: str, address: int, size: int) -> bytes:
        """
        The single, gate-guarded entry point for all live process reads.
        Fails closed on any policy mismatch or denied address.
        """
        call_idx = len(self.audit_log) + 1
        timestamp = datetime.utcnow().isoformat() + "Z"
        address = int(address)
        size = int(size)
        
        # 1. Check permit existence
        p = self.permits.get(key)
        if p is None:
            self.audit_log.append({
                "call_index": call_idx, "timestamp": timestamp, "key": key, "phase": phase,
                "address": hex(address), "size": size, "status": "DENIED_PERMIT_NOT_FOUND"
            })
            raise PolicyDenied(f"Permit key '{key}' not found in policy manifest.")
            
        # 2. Check permit exact match
        p_addr = int(p["address"], 16)
        p_size = p["size"]
        p_phase = p["phase"]
        
        if (phase, address, size) != (p_phase, p_addr, p_size):
            self.audit_log.append({
                "call_index": call_idx, "timestamp": timestamp, "key": key, "phase": phase,
                "address": hex(address), "size": size, "status": "DENIED_PERMIT_PARAMETERS_MISMATCH"
            })
            raise PolicyDenied(f"Permit parameter mismatch for key '{key}'.")
            
        # 3. Check sensitive denied ranges
        for d_addr, d_size in self.denied_ranges:
            # Overlap check
            if max(address, d_addr) < min(address + size, d_addr + d_size):
                self.audit_log.append({
                    "call_index": call_idx, "timestamp": timestamp, "key": key, "phase": phase,
                    "address": hex(address), "size": size, "status": "DENIED_SENSITIVE_RANGE_OVERRIDE"
                })
                raise PolicyDenied(f"Address {hex(address)} overlaps sensitive denied range [{hex(d_addr)}, {hex(d_addr+d_size)}).")
                
        # 4. Check permit call count limit
        if self.permit_calls[key] >= p["max_calls"]:
            self.audit_log.append({
                "call_index": call_idx, "timestamp": timestamp, "key": key, "phase": phase,
                "address": hex(address), "size": size, "status": "DENIED_MAX_CALLS_EXCEEDED"
            })
            raise PolicyDenied(f"Permit '{key}' max calls exceeded ({p['max_calls']}).")
            
        # 5. Check phase budget
        cur_phase_bytes = self.phase_bytes_used[phase]
        phase_budget = self.phase_budgets[phase]
        if cur_phase_bytes + size > phase_budget:
            self.audit_log.append({
                "call_index": call_idx, "timestamp": timestamp, "key": key, "phase": phase,
                "address": hex(address), "size": size, "status": "DENIED_PHASE_BUDGET_EXCEEDED"
            })
            raise PolicyDenied(f"Phase budget exceeded for '{phase}': {cur_phase_bytes} + {size} > {phase_budget}")
            
        # 6. Execute Win32 ReadProcessMemory
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
            self.audit_log.append({
                "call_index": call_idx, "timestamp": timestamp, "key": key, "phase": phase,
                "address": hex(address), "size": size, "actual_size": bytes_read.value, "status": "FAILED_RPM"
            })
            raise IOError(f"ReadProcessMemory returned incomplete or failed read at {hex(address)}.")
            
        data = bytes(buf[:size])
        data_hash = hashlib.sha256(data).hexdigest()
        
        self.permit_calls[key] += 1
        self.phase_bytes_used[phase] += size
        
        self.audit_log.append({
            "call_index": call_idx,
            "timestamp": timestamp,
            "key": key,
            "phase": phase,
            "address": hex(address),
            "size": size,
            "actual_size": size,
            "status": "SUCCESS",
            "purpose": p["purpose"],
            "sha256": data_hash,
            "preview_hex": data[:16].hex()
        })
        return data

print("WindowsLivePolicyReader class ready.")
