"""
Offline Verification Test Suite for NBA 2K22 MyCAREER Offline Team Practice Unlocker
"""
import os
import struct
import pytest
from pathlib import Path

EXE_PATH = Path(r"E:\Games\NBA 2K22\NBA2K22.exe")
EXPECTED_SHA256 = "1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5"

@pytest.fixture(scope="module")
def exe_bytes():
    assert EXE_PATH.exists(), f"NBA2K22.exe not found at {EXE_PATH}"
    import hashlib
    data = EXE_PATH.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    assert sha == EXPECTED_SHA256, f"Executable hash mismatch: expected {EXPECTED_SHA256}, got {sha}"
    return data

def rva_to_file_offset(rva: int) -> int:
    # In NBA2K22.exe .text: RVA 0x1000..0x21f371f maps to Raw 0x600..0x21f2e00
    # Offset = 0x600 + (rva - 0x1000) = rva - 0xa00
    if 0x1000 <= rva < 0x21f4000:
        return rva - 0xa00
    # In .rdata: RVA 0x21f4000.. maps to Raw 0x21f2e00..
    if 0x21f4000 <= rva < 0x3154000:
        return 0x21f2e00 + (rva - 0x21f4000)
    raise ValueError(f"RVA out of mapped range: 0x{rva:x}")

def test_create_players_entry_and_assertion(exe_bytes):
    """Verify CreatePlayers entry point, practice type offset, and assertion site."""
    # 1. Entry point at RVA 0x163f4a0: rex push rbp, push rbx, push rsi, push rdi, push r12, push r14
    entry_off = rva_to_file_offset(0x163f4a0)
    entry_bytes = exe_bytes[entry_off:entry_off + 7]
    assert entry_bytes == b"\x40\x55\x53\x56\x57\x41\x54"

    # 2. Offset 0x488 read at RVA 0x163f4db
    off_read = rva_to_file_offset(0x163f4db)
    # mov ecx, dword ptr [r14 + 0x488] -> 41 8b 8e 88 04 00 00
    assert exe_bytes[off_read:off_read + 7] == b"\x41\x8b\x8e\x88\x04\x00\x00"

    # 3. Test ecx, ecx ; je ... at RVA 0x163f4ff
    off_branch = rva_to_file_offset(0x163f4ff)
    # 85 c9 0f 84 8e 00 00 00 -> test ecx, ecx; je 0x14163f595
    assert exe_bytes[off_branch:off_branch + 8] == b"\x85\xc9\x0f\x84\x8e\x00\x00\x00"

    # 4. Fatal assertion string at RVA 0x2cc21d0
    off_str = rva_to_file_offset(0x2cc21d0)
    expected_str = "Can't start LivePractice, if type is unknown.".encode("utf-16le")
    assert exe_bytes[off_str:off_str + len(expected_str)] == expected_str

def test_drill_calculate_results_entry(exe_bytes):
    """Verify LiveDrill_HandleCalculateResults entry point and star check."""
    # Entry at RVA 0x11f8680: rex push rbp, push r14, push r15
    off_entry = rva_to_file_offset(0x11f8680)
    assert exe_bytes[off_entry:off_entry + 4] == b"\x40\x55\x41\x56"

    # Star rating check at RVA 0x11f88fb: cmp ebp, 3 (83 fd 03)
    off_star = rva_to_file_offset(0x11f88fb)
    assert exe_bytes[off_star:off_star + 3] == b"\x83\xfd\x03"

def test_live_practice_ended_entry(exe_bytes):
    """Verify HandleLivePracticeEnded entry point."""
    off_entry = rva_to_file_offset(0x11f8bf0)
    # sub rsp, 0x38 (48 83 ec 38)
    assert exe_bytes[off_entry:off_entry + 4] == b"\x48\x83\xec\x38"

def test_tracking_flag_displacement(exe_bytes):
    """Verify the tracking flag address relative calculation."""
    # At RVA 0x11dfe33: cmp dword ptr [rip + 0x51722ea], 0
    off_cmp = rva_to_file_offset(0x11dfe33)
    # 83 3d ea 22 17 05 00
    assert exe_bytes[off_cmp:off_cmp + 2] == b"\x83\x3d"
    disp = struct.unpack_from("<i", exe_bytes, off_cmp + 2)[0]
    assert disp == 0x51722ea
    # Target VA = 0x1411dfe33 + 7 + 0x51722ea = 0x146352124
    target_va = 0x140000000 + 0x11dfe33 + 7 + disp
    assert target_va == 0x146352124

def test_js_patch_file_exists():
    """Verify Frida patch file is deployed and non-empty."""
    patch_path = Path(__file__).parent.parent.parent / "research/mc_offline_practice/patch_offline_team_practice.js"
    assert patch_path.exists(), f"Frida patch file does not exist at {patch_path}"
    content = patch_path.read_text(encoding="utf-8")
    assert "pCreatePlayers" in content
    assert "pHandleDrillResults" in content
    assert "pPracticeEnded" in content
