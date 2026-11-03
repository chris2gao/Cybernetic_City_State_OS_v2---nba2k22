"""Low-overhead performance profiling and metrics collector for WorldData capture.

Measures segmented timings (ReadProcessMemory, metadata verification, decoding,
payload construction, SQLite ingest, transactions, commit) and resource metrics
(bytes read, rows inserted, peak RSS) without corrupting live/fixture provenance.
"""
from __future__ import annotations

import contextlib
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import time
from typing import Any, Dict, Optional


class _ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD),
        ('PageFaultCount', wintypes.DWORD),
        ('PeakWorkingSetSize', ctypes.c_size_t),
        ('WorkingSetSize', ctypes.c_size_t),
        ('QuotaPeakPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPagedPoolUsage', ctypes.c_size_t),
        ('QuotaPeakNonPagedPoolUsage', ctypes.c_size_t),
        ('QuotaNonPagedPoolUsage', ctypes.c_size_t),
        ('PagefileUsage', ctypes.c_size_t),
        ('PeakPagefileUsage', ctypes.c_size_t),
    ]


def get_process_memory() -> Dict[str, int]:
    """Return working set and peak working set in bytes."""
    if os.name != 'nt':
        return {'working_set_bytes': 0, 'peak_working_set_bytes': 0}
    try:
        psapi = ctypes.WinDLL('psapi', use_last_error=True)
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(_ProcessMemoryCounters),
            wintypes.DWORD,
        ]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        counters = _ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(_ProcessMemoryCounters)
        handle = kernel.GetCurrentProcess()
        if psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            return {
                'working_set_bytes': int(counters.WorkingSetSize),
                'peak_working_set_bytes': int(counters.PeakWorkingSetSize),
            }
    except Exception:
        pass
    return {'working_set_bytes': 0, 'peak_working_set_bytes': 0}


class PerformanceTrace:
    """Low-overhead timing and counter accumulator."""

    def __init__(self, label: str = 'capture_trace', *, enabled: bool = True):
        self.label = label
        self.enabled = enabled
        self.timings: Dict[str, float] = {}
        self.counts: Dict[str, int] = {}
        self.bytes_transferred: Dict[str, int] = {}
        self.metadata: Dict[str, Any] = {}
        self._start_wall = time.perf_counter()
        self._start_time = time.time()
        self._initial_mem = get_process_memory()

    @contextlib.contextmanager
    def section(self, name: str):
        if not self.enabled:
            yield
            return
        t0 = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - t0
            self.timings[name] = self.timings.get(name, 0.0) + elapsed

    def add_count(self, key: str, amount: int = 1):
        if self.enabled:
            self.counts[key] = self.counts.get(key, 0) + amount

    def add_bytes(self, key: str, amount: int):
        if self.enabled:
            self.bytes_transferred[key] = self.bytes_transferred.get(key, 0) + amount

    def set_meta(self, key: str, value: Any):
        self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        total_wall = time.perf_counter() - self._start_wall
        mem = get_process_memory()
        return {
            'label': self.label,
            'enabled': self.enabled,
            'started_at': self._start_time,
            'total_wall_seconds': total_wall,
            'timings_seconds': {k: round(v, 6) for k, v in self.timings.items()},
            'counts': dict(self.counts),
            'bytes_transferred': dict(self.bytes_transferred),
            'initial_memory': self._initial_mem,
            'final_memory': mem,
            'peak_working_set_bytes': mem.get('peak_working_set_bytes', 0),
            'metadata': dict(self.metadata),
        }


def benchmark_trace_overhead(iterations: int = 100_000) -> Dict[str, float]:
    """Measure the invocation overhead of PerformanceTrace."""
    trace = PerformanceTrace('overhead_test')
    t0 = time.perf_counter()
    for _ in range(iterations):
        with trace.section('test_section'):
            pass
        trace.add_count('test_counter', 1)
    elapsed = time.perf_counter() - t0
    return {
        'iterations': iterations,
        'total_seconds': elapsed,
        'per_call_microseconds': (elapsed / iterations) * 1_000_000,
    }
