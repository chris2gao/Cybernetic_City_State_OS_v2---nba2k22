# -*- coding: utf-8 -*-
"""
 NBA 2K22 Windows 内存读取与受控写入底层封装
"""
import ctypes
from ctypes import wintypes
import win32process
import win32api
import win32con
import struct
from typing import Optional, List, Tuple

PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("PartitionId", wintypes.WORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]

class GameMemory:
    def __init__(self, process_name: str = "NBA2K22.exe", read_only: bool = True):
        self.process_name = process_name
        self.read_only = read_only
        self.kernel32 = ctypes.windll.kernel32
        # ctypes defaults undeclared arguments to 32-bit C ints. That can
        # truncate HANDLEs and pointers in a 64-bit game process, especially
        # on the restart-rescan path that was not exercised by the old cache.
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
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t),
        ]
        self.kernel32.ReadProcessMemory.restype = wintypes.BOOL
        self.kernel32.WriteProcessMemory.argtypes = [
            wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t),
        ]
        self.kernel32.WriteProcessMemory.restype = wintypes.BOOL
        self.kernel32.VirtualQueryEx.argtypes = [
            wintypes.HANDLE, ctypes.c_void_p,
            ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t,
        ]
        self.kernel32.VirtualQueryEx.restype = ctypes.c_size_t
        self.pid: Optional[int] = None
        self.handle: Optional[int] = None
        self.base_address: Optional[int] = None
        self.attach()

    def attach(self) -> bool:
        """根据进程名挂接游戏进程 (基于 Toolhelp32Snapshot, 无需第三方库)"""
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
        
        snapshot = self.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)
        
        success = self.kernel32.Process32First(snapshot, ctypes.byref(entry))
        while success:
            exe_name = entry.szExeFile.decode('latin-1', errors='ignore')
            if exe_name.lower() == self.process_name.lower():
                self.pid = entry.th32ProcessID
                break
            success = self.kernel32.Process32Next(snapshot, ctypes.byref(entry))
        self.kernel32.CloseHandle(snapshot)
        
        if not self.pid:
            raise ProcessLookupError(f"未找到正在运行的 {self.process_name} 进程，请先启动游戏！")
        
        desired_access = (
            PROCESS_VM_READ | PROCESS_QUERY_INFORMATION
            if self.read_only
            else win32con.PROCESS_ALL_ACCESS
        )
        try:
            self.handle = win32api.OpenProcess(desired_access, False, self.pid)
        except Exception as exc:
            mode = "只读采集" if self.read_only else "经批准的读写操作"
            raise PermissionError(
                f"Windows 拒绝以{mode}权限打开 {self.process_name} (PID: {self.pid})；"
                "请让采集进程运行在与游戏相同或更高的 Windows 权限级别，"
                "并确认该进程允许外部只读访问。"
            ) from exc
        if not self.handle:
            mode = "只读采集" if self.read_only else "读写操作"
            raise PermissionError(
                f"无法以{mode}权限打开游戏进程 (PID: {self.pid})；"
                "请确认 NBA 2K22 与采集脚本运行在相同 Windows 权限级别。"
            )
        
        # 获取主模块基址 (NBA2K22.exe)
        modules = win32process.EnumProcessModules(self.handle)
        self.base_address = modules[0]
        return True

    def close(self):
        if self.handle:
            win32api.CloseHandle(self.handle)
            self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        # Keep short-lived capture/audit invocations from leaking process handles
        # when an exception unwinds before their explicit success cleanup.
        try:
            self.close()
        except Exception:
            pass

    def read_bytes(self, address: int, size: int) -> Optional[bytes]:
        """从指定内存地址读取指定长度的字节，仅在完整读取时返回，杜绝部分截断或假数据"""
        buf = (ctypes.c_char * size)()
        bytes_read = ctypes.c_size_t()
        res = self.kernel32.ReadProcessMemory(
            int(self.handle),
            ctypes.c_void_p(address),
            buf,
            size,
            ctypes.byref(bytes_read)
        )
        if res and bytes_read.value == size:
            return bytes(buf[:size])
        return None

    def write_bytes(self, address: int, data: bytes) -> bool:
        """向指定内存地址写入原始字节"""
        if self.read_only:
            raise PermissionError("该 GameMemory 实例为只读采集句柄，禁止写入游戏内存")
        buf = (ctypes.c_char * len(data))(*data)
        bytes_written = ctypes.c_size_t()
        res = self.kernel32.WriteProcessMemory(
            int(self.handle),
            ctypes.c_void_p(address),
            buf,
            len(data),
            ctypes.byref(bytes_written)
        )
        return bool(res and bytes_written.value == len(data))

    def read_uint8_safe(self, address: int) -> Optional[int]:
        b = self.read_bytes(address, 1)
        return b[0] if b is not None else None

    def read_uint8(self, address: int) -> int:
        val = self.read_uint8_safe(address)
        return val if val is not None else 0

    def write_uint8(self, address: int, value: int) -> bool:
        return self.write_bytes(address, bytes([value & 0xFF]))

    def read_uint16_safe(self, address: int) -> Optional[int]:
        b = self.read_bytes(address, 2)
        return struct.unpack("<H", b)[0] if b is not None else None

    def read_uint16(self, address: int) -> int:
        val = self.read_uint16_safe(address)
        return val if val is not None else 0

    def write_uint16(self, address: int, value: int) -> bool:
        return self.write_bytes(address, struct.pack("<H", value))

    def read_uint32_safe(self, address: int) -> Optional[int]:
        b = self.read_bytes(address, 4)
        return struct.unpack("<I", b)[0] if b is not None else None

    def read_uint32(self, address: int) -> int:
        val = self.read_uint32_safe(address)
        return val if val is not None else 0

    def write_uint32(self, address: int, value: int) -> bool:
        return self.write_bytes(address, struct.pack("<I", value))

    def read_uint64_safe(self, address: int) -> Optional[int]:
        b = self.read_bytes(address, 8)
        return struct.unpack("<Q", b)[0] if b is not None else None

    def read_uint64(self, address: int) -> int:
        val = self.read_uint64_safe(address)
        return val if val is not None else 0

    def write_uint64(self, address: int, value: int) -> bool:
        return self.write_bytes(address, struct.pack("<Q", value))

    def read_float_safe(self, address: int) -> Optional[float]:
        b = self.read_bytes(address, 4)
        return struct.unpack("<f", b)[0] if b is not None else None

    def read_float(self, address: int) -> float:
        val = self.read_float_safe(address)
        return val if val is not None else 0.0

    def require_uint8(self, address: int) -> int:
        return self._require_value(self.read_uint8_safe(address), address, "uint8")

    def require_uint16(self, address: int) -> int:
        return self._require_value(self.read_uint16_safe(address), address, "uint16")

    def require_uint32(self, address: int) -> int:
        return self._require_value(self.read_uint32_safe(address), address, "uint32")

    def require_uint64(self, address: int) -> int:
        return self._require_value(self.read_uint64_safe(address), address, "uint64")

    def require_float(self, address: int) -> float:
        return self._require_value(self.read_float_safe(address), address, "float")

    @staticmethod
    def _require_value(value, address: int, value_type: str):
        if value is None:
            raise OSError(f"ReadProcessMemory failed for {value_type} at 0x{address:X}")
        return value

    def write_float(self, address: int, value: float) -> bool:
        return self.write_bytes(address, struct.pack("<f", float(value)))

    def read_utf16_string(self, address: int, max_length: int = 40) -> str:
        b = self.read_bytes(address, max_length)
        if not b:
            return ""
        return b.decode('utf-16le', errors='ignore').split('\x00')[0]

    def read_utf16_string_safe(self, address: int, max_length: int = 40) -> Optional[str]:
        b = self.read_bytes(address, max_length)
        if b is None:
            return None
        return b.decode('utf-16le', errors='ignore').split('\x00')[0]

    def require_utf16_string(self, address: int, max_length: int = 40) -> str:
        value = self.read_utf16_string_safe(address, max_length)
        if value is None:
            raise OSError(f"ReadProcessMemory failed for UTF-16 string at 0x{address:X}")
        return value

    def write_utf16_string(self, address: int, text: str, max_length: int = 40) -> bool:
        encoded = text.encode('utf-16le')
        if len(encoded) < max_length:
            encoded += b'\x00' * (max_length - len(encoded))
        else:
            encoded = encoded[:max_length]
        return self.write_bytes(address, encoded)

    def scan_pattern(self, pattern: bytes, start_addr: int = 0x7FF400000000, end_addr: int = 0x7FF500000000) -> List[int]:
        """分块扫描已提交的可读内存区，保留跨块边界命中并避免整区大读。"""
        if not pattern:
            raise ValueError("pattern 不能为空")
        if start_addr < 0 or end_addr <= start_addr:
            raise ValueError("扫描地址范围无效")

        mbi = MEMORY_BASIC_INFORMATION()
        addr = start_addr
        matches = []
        chunk_size = 1024 * 1024
        overlap = max(0, len(pattern) - 1)
        readable_protections = {0x02, 0x04, 0x08, 0x20, 0x40, 0x80}

        while self.kernel32.VirtualQueryEx(int(self.handle), ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            base = int(mbi.BaseAddress or 0)
            region_size = int(mbi.RegionSize)
            if base <= 0 or region_size <= 0:
                break
            region_end = min(base + region_size, end_addr)
            protection = int(mbi.Protect) & 0xFF
            guarded = bool(int(mbi.Protect) & 0x100)
            if int(mbi.State) == 0x1000 and protection in readable_protections and not guarded:
                cursor = max(base, addr)
                carry = b""
                while cursor < region_end:
                    size = min(chunk_size, region_end - cursor)
                    raw = self.read_bytes(cursor, size)
                    if raw is None:
                        carry = b""
                        cursor += size
                        continue
                    scan_buf = carry + raw
                    scan_base = cursor - len(carry)
                    search_at = 0
                    while True:
                        found = scan_buf.find(pattern, search_at)
                        if found < 0:
                            break
                        absolute = scan_base + found
                        if start_addr <= absolute and absolute + len(pattern) <= end_addr:
                            matches.append(absolute)
                        search_at = found + 1
                    carry = scan_buf[-overlap:] if overlap else b""
                    cursor += size
            addr = base + region_size
            if addr >= end_addr or addr >= 0x7FFFFFFFFFFF:
                break
        return sorted(set(matches))
