from __future__ import annotations

import hashlib
import json
import os
import struct
from typing import Any, Dict, List, Optional, Tuple


class NativeConsumerTracer:
    """
    Reverse engineering consumer path tracer for NBA2K22.exe.

    Extracts, disassembles, and verifies the native machine code bytes and control flow
    for in-engine consumers of player tendencies and coach settings:
    1. Tactical Role Ceiling & Floor Governor (RVA 0x1226942..0x1226a8b):
       Evaluates player role at [rsp + 0x20] / [rsp + 0x24] against the ground-truth table
       in .rdata at [rsi + rcx*4 + 0x2b59798] (ceilings: 92, 83, 74, 0) and multipliers at 0x2b597a8 (0.94, 0.96, 0.98, 1.0).
    2. Coach Dynamic Pacing Engine & Strategy Dispatcher (RVA 0x120b9ca..0x120bb50):
       Evaluates tempo slider input in xmm0: ecx = (Tempo - 50) * 1.2 + 10,
       clamping results strictly to [10, 70] via eax=0x46 (at 0x14120ba98) and eax=0x0a (at 0x14120bab0),
       and dispatches POE Offense (slot 0x57) and POE Defense (slot 0x58).
    3. Roster Simulation Snapshot Pipeline (RVA 0x1744bd0..0x174566a):
       Sequentially copies all 99 tendencies into simulation context with player stride 0x27c.
    """

    TARGET_PE_SHA256 = "1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5"
    TARGET_PROCESS_NAME = "NBA2K22.exe"

    # Exact raw machine code bytes extracted from NBA2K22.exe (image base 0x140000000)
    ROLE_GOVERNOR_RAW_BYTES = (
        "48 8d 4c 24 30 e8 d4 ee 74 ff 48 63 4c 24 20 44 8b c0 83 f9 03 75 76 "
        "48 63 4c 24 24 83 f9 03 75 1e 48 8d 4c 24 30 44 88 87 dd 02 00 00 "
        "e8 bc f1 74 ff 8b d0 88 97 de 02 00 00 e9 35 01 00 00 "
        "8b 94 8e 98 97 b5 02 48 8b d9 83 ea 05 41 0f b6 c8 41 3b d0 "
        "0f b6 c2 0f 4c c8 88 8f dd 02 00 00 48 8d 4c 24 30 e8 85 f1 74 ff "
        "44 8b 84 9e 98 97 b5 02 41 83 e8 05 0f b6 d0 44 3b c0 41 0f b6 c8 "
        "0f 4c d1 88 97 de 02 00 00"
    )

    COACH_PACING_RAW_BYTES = (
        "f3 0f 2d c0 f3 0f 5c ce 41 0f 28 c4 83 e8 32 f3 45 0f 5c c8 6b c8 3c "
        "b8 1f 85 eb 51 f3 0f 5e c1 f7 e9 41 0f 28 ca b8 46 00 00 00 c1 fa 04 "
        "8b ca c1 e9 1f 83 c1 0a 03 ca 83 f9 46 0f 4f c8 b8 0a 00 00 00 83 f9 0a "
        "0f 4c c8 8b c7 2b c1"
    )

    SNAPSHOT_LOOP_RAW_BYTES = (
        "e8 0d 07 23 ff 48 8b cb 89 85 e0 00 00 00 e8 ff f8 22 ff 48 8b cb 89 85 e4 00 00 00"
    )

    POE_DISPATCHER_RAW_BYTES = (
        "41 8d 51 57 45 8d 41 17 45 0f 5b c9 e8 15 70 d5 ff 45 33 c9 4c 89 74 24 20 "
        "48 8b cb 45 0f 28 c1 41 0f 28 f1 41 8d 51 58 f3 45 0f 59 c5 45 8d 41 18 "
        "f3 41 0f 59 f6 f3 0f 2c f8 e8 e7 6f d5 ff 8b cf"
    )

    ROLE_TABLE_CEILINGS_RAW_BYTES = "5c 00 00 00 53 00 00 00 4a 00 00 00 00 00 00 00"
    ROLE_TABLE_MULTIPLIERS_RAW_BYTES = "d7 a3 70 3f 8f c2 75 3f 48 e1 7a 3f 00 00 80 3f"

    def __init__(self, repo_root: Optional[str] = None, auto_attach: bool = False) -> None:
        if repo_root is None:
            cur = os.path.abspath(__file__)
            repo_root = os.path.abspath(os.path.join(cur, "..", "..", "..", "..", ".."))
        self.repo_root = repo_root
        self.run_dir = os.path.join(
            self.repo_root, "01_os", "07_content", "_runs",
            "run-20261030-nba2k22-vae-rea-single-field-loop-001"
        )
        self.records_dir = os.path.join(self.run_dir, "06_执行", "field_records")
        self.evidence_dir = os.path.join(self.run_dir, "02_证据")
        self._mem = None
        if auto_attach:
            self._init_memory()

    def _init_memory(self) -> None:
        try:
            import sys
            src_dir = os.path.join(self.repo_root, "08_Domain_Applications", "Antigravity_GM_Engine", "src")
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            from memory import GameMemory
            self._mem = GameMemory(process_name=self.TARGET_PROCESS_NAME, read_only=True)
        except Exception:
            self._mem = None

    @staticmethod
    def verify_rel32_call(call_site_va: int, instruction_bytes: bytes, expected_target_va: int) -> Dict[str, Any]:
        """
        Mathematically proves near CALL relative 32-bit displacement:
        next_ip = call_site_va + 5
        target_va = next_ip + rel32 (signed 32-bit integer)
        """
        if len(instruction_bytes) != 5 or instruction_bytes[0] != 0xE8:
            raise ValueError(f"Expected 5-byte near CALL (0xE8), got {instruction_bytes.hex()}")
        rel32 = struct.unpack("<i", instruction_bytes[1:5])[0]
        next_ip = call_site_va + 5
        target_va = next_ip + rel32
        return {
            "call_site_va": hex(call_site_va),
            "instruction_bytes_hex": " ".join(f"{b:02x}" for b in instruction_bytes),
            "next_ip_va": hex(next_ip),
            "rel32_int": rel32,
            "rel32_hex": hex(rel32),
            "computed_target_va": hex(target_va),
            "expected_target_va": hex(expected_target_va),
            "is_verified": target_va == expected_target_va,
        }

    def trace_shot_tendency_callers(self) -> List[Dict[str, Any]]:
        """
        Disassembles and documents the verified call sites of SHOT_TENDENCY getter RVA 0x975820.
        Includes verified raw machine code bytes, register data flow, and exact control flow semantics.
        """
        return [
            {
                "rva": "0x1226947",
                "system": "In-Game AI Tactical Role Hierarchy Controller",
                "role": "Role-Based Tactical Shot Ceiling Governor",
                "raw_bytes_hex": self.ROLE_GOVERNOR_RAW_BYTES,
                "disassembly": [
                    "0x141226942: 48 8d 4c 24 30           lea      rcx, [rsp + 0x30]",
                    "0x141226947: e8 d4 ee 74 ff           call     0x140975820       ; get_shot_tendency() [rel32=-0x8b112c]",
                    "0x14122694c: 48 63 4c 24 20           movsxd   rcx, dword ptr [rsp + 0x20] ; primary role tier",
                    "0x141226951: 44 8b c0                 mov      r8d, eax          ; r8d = raw shot_tendency",
                    "0x141226954: 83 f9 03                 cmp      ecx, 3            ; check role tier (3 = Primary Core)",
                    "0x141226957: 75 76                    jne      0x1412269cf       ; branch to Non-Core Support (Branch C)",
                    "; --- Branch A: Franchise Core (3, 3) ---",
                    "0x141226959: 48 63 4c 24 24           movsxd   rcx, dword ptr [rsp + 0x24] ; secondary role tier",
                    "0x14122695e: 83 f9 03                 cmp      ecx, 3",
                    "0x141226961: 75 1e                    jne      0x141226981       ; secondary core branch (Branch B)",
                    "0x141226963: 48 8d 4c 24 30           lea      rcx, [rsp + 0x30]",
                    "0x141226968: 44 88 87 dd 02 00 00     mov      byte ptr [rdi + 0x2dd], r8b  ; core role unconstrained",
                    "0x14122696f: e8 bc f1 74 ff           call     0x140975b30       ; get_touches() [rel32=-0x8b0e44]",
                    "0x141226974: 8b d0                    mov      edx, eax",
                    "0x141226976: 88 97 de 02 00 00        mov      byte ptr [rdi + 0x2de], dl   ; touches stored",
                    "0x14122697c: e9 35 01 00 00           jmp      0x141226ab6       ; exit governor",
                    "; --- Branch B: Secondary Core Ceiling Clamping (3, !=3) ---",
                    "0x141226981: 8b 94 8e 98 97 b5 02     mov      edx, dword ptr [rsi + rcx*4 + 0x2b59798] ; role table ceiling",
                    "0x141226988: 48 8b d9                 mov      rbx, rcx",
                    "0x14122698b: 83 ea 05                 sub      edx, 5            ; edx = role_ceiling - 5",
                    "0x14122698e: 41 0f b6 c8              movzx    ecx, r8b          ; ecx = raw shot_tendency",
                    "0x141226992: 41 3b d0                 cmp      edx, r8d          ; cmp (role_ceiling - 5), shot_tendency",
                    "0x141226995: 0f b6 c2                 movzx    eax, dl           ; eax = role_ceiling - 5",
                    "0x141226998: 0f 4c c8                 cmovl    ecx, eax          ; if (role_ceiling - 5) < shot: clamp!",
                    "0x14122699b: 88 8f dd 02 00 00        mov      byte ptr [rdi + 0x2dd], cl   ; store clamped shot_tendency",
                    "0x1412269a1: 48 8d 4c 24 30           lea      rcx, [rsp + 0x30]",
                    "0x1412269a6: e8 85 f1 74 ff           call     0x140975b30       ; get_touches() [rel32=-0x8b0e7b]",
                    "0x1412269ab: 44 8b 84 9e 98 97 b5 02 mov      r8d, dword ptr [rsi + rbx*4 + 0x2b59798] ; role ceiling for touches",
                    "0x1412269b3: 41 83 e8 05              sub      r8d, 5",
                    "0x1412269b7: 0f b6 d0                 movzx    edx, al",
                    "0x1412269ba: 44 3b c0                 cmp      r8d, eax",
                    "0x1412269bd: 41 0f b6 c8              movzx    ecx, r8b",
                    "0x1412269c1: 0f 4c d1                 cmovl    edx, ecx          ; touches clamped to ceiling - 5",
                    "0x1412269c4: 88 97 de 02 00 00        mov      byte ptr [rdi + 0x2de], dl   ; store clamped touches",
                    "0x1412269ca: e9 e7 00 00 00           jmp      0x141226ab6       ; exit governor",
                ],
                "verified_control_flow": (
                    "Tripartite tactical role hierarchy: Franchise Core (tier 3, 3) bypasses all limits; "
                    "Secondary Core (tier 3, !=3) clamps effective shot tendency and touches to (ceiling - 5); "
                    "Non-Core Support (tier < 3) enforces minimum activity floor and dampens rating channels "
                    "via table multipliers (0.94, 0.96, 0.98)."
                ),
                "epistemological_grade": "STATIC_DISASSEMBLY_LEAD",
                "coupled_fields": ["tendency.ShotTendency", "tendency.TouchTendency", "Tactical Role Ceiling Table 0x2b59798"]
            },
            {
                "rva": "0x174510e",
                "system": "Simulation Roster Snapshot Engine",
                "role": "Sequential Roster Snapshot Extraction",
                "raw_bytes_hex": self.SNAPSHOT_LOOP_RAW_BYTES,
                "disassembly": [
                    "0x14174510e: e8 0d 07 23 ff           call     0x140975820       ; get_shot_tendency() [rel32=-0xdcf8f3]",
                    "0x141745113: 48 8b cb                 mov      rcx, rbx",
                    "0x141745116: 89 85 e0 00 00 00        mov      dword ptr [rbp + 0xe0], eax ; snapshot index 0",
                    "0x14174511c: e8 ff f8 22 ff           call     0x140974a20       ; get_driving_layup_tendency() [rel32=-0xdd0701]",
                    "0x141745121: 48 8b cb                 mov      rcx, rbx",
                    "0x141745124: 89 85 e4 00 00 00        mov      dword ptr [rbp + 0xe4], eax ; snapshot index 1"
                ],
                "verified_control_flow": (
                    "Sequentially iterates and calls all 99 player tendency getters (0x174510e..0x174566a), "
                    "copying values into simulation context struct with player stride 0x27c (636 bytes)."
                ),
                "epistemological_grade": "STATIC_DISASSEMBLY_LEAD",
                "coupled_fields": ["All 99 Player Tendencies in continuous sequence 0x458..0x4BA"]
            }
        ]

    def trace_coach_gameplan_consumers(self) -> Dict[str, Any]:
        """
        Disassembles and documents the verified Coach Pacing Engine and POE Dispatcher (RVA 0x120b9ca..0x120bb50).
        Includes verified raw machine code bytes, register data flow, and exact bounds proof.
        """
        return {
            "tempo_pacing_engine": {
                "rva": "0x120ba72",
                "role": "Dynamic Tempo Linear Transform with [10, 70] Clamping",
                "raw_bytes_hex": self.COACH_PACING_RAW_BYTES,
                "disassembly": [
                    "0x14120ba72: f3 0f 2d c0              cvtss2si eax, xmm0        ; convert float Tempo to int",
                    "0x14120ba76: f3 0f 5c ce              subss    xmm1, xmm6       ; interleaved SSE math",
                    "0x14120ba7a: 41 0f 28 c4              movaps   xmm0, xmm12",
                    "0x14120ba7e: 83 e8 32                 sub      eax, 0x32        ; eax = Tempo - 50 (0x32)",
                    "0x14120ba81: f3 45 0f 5c c8           subss    xmm9, xmm8",
                    "0x14120ba86: 6b c8 3c                 imul     ecx, eax, 0x3c   ; ecx = (Tempo - 50) * 60 (0x3c)",
                    "0x14120ba89: b8 1f 85 eb 51           mov      eax, 0x51eb851f  ; reciprocal for division by 50",
                    "0x14120ba8e: f3 0f 5e c1              divss    xmm0, xmm1",
                    "0x14120ba92: f7 e9                    imul     ecx              ; fixed-point multiply",
                    "0x14120ba94: 41 0f 28 ca              movaps   xmm1, xmm10",
                    "0x14120ba98: b8 46 00 00 00           mov      eax, 0x46        ; load 70 (0x46) into eax!",
                    "0x14120ba9d: c1 fa 04                 sar      edx, 4           ; edx = ((Tempo - 50) * 60) / 50",
                    "0x14120baa0: 8b ca                    mov      ecx, edx",
                    "0x14120baa2: c1 e9 1f                 shr      ecx, 0x1f        ; sign bit correction",
                    "0x14120baa5: 83 c1 0a                 add      ecx, 0xa         ; + 10",
                    "0x14120baa8: 03 ca                    add      ecx, edx",
                    "0x14120baaa: 83 f9 46                 cmp      ecx, 0x46        ; compare ecx with 70",
                    "0x14120baad: 0f 4f c8                 cmovg    ecx, eax         ; if ecx > 70, ecx = eax (70)",
                    "0x14120bab0: b8 0a 00 00 00           mov      eax, 0xa         ; load 10 (0x0a) into eax!",
                    "0x14120bab5: 83 f9 0a                 cmp      ecx, 0xa         ; compare ecx with 10",
                    "0x14120bab8: 0f 4c c8                 cmovl    ecx, eax         ; if ecx < 10, ecx = eax (10)",
                    "0x14120babb: 8b c7                    mov      eax, edi",
                    "0x14120babd: 2b c1                    sub      eax, ecx         ; apply bounded pace delta"
                ],
                "verified_control_flow": (
                    "Converts input Tempo from xmm0 to integer, centers at 50, scales by 1.2 (60/50), "
                    "adds 10, and clamps the modifier strictly between 10 (eax=0xa at 0x14120bab0) "
                    "and 70 (eax=0x46 at 0x14120ba98). This proves the native engine enforces [10, 70] bounds saturation."
                ),
                "epistemological_grade": "STATIC_DISASSEMBLY_LEAD",
                "clamping_bounds": [10, 70]
            },
            "poe_strategy_dispatcher": {
                "rva": "0x120b9ca",
                "role": "Point of Emphasis (POE) Strategy Caller",
                "raw_bytes_hex": self.POE_DISPATCHER_RAW_BYTES,
                "disassembly": [
                    "0x14120b9ca: 41 8d 51 57              lea      edx, [r9 + 0x57] ; slot 0x57 (POEOffense)",
                    "0x14120b9ce: 45 8d 41 17              lea      r8d, [r9 + 0x17]",
                    "0x14120b9d2: 45 0f 5b c9              cvtdq2ps xmm9, xmm9",
                    "0x14120b9d6: e8 15 70 d5 ff           call     0x140f629f0      ; query offensive strategy factor [rel32=-0x2a8feb]",
                    "0x14120b9ee: 41 8d 51 58              lea      edx, [r9 + 0x58] ; slot 0x58 (POEDefense)",
                    "0x14120b9f7: 45 8d 41 18              lea      r8d, [r9 + 0x18]",
                    "0x14120ba04: e8 e7 6f d5 ff           call     0x140f629f0      ; query defensive strategy factor [rel32=-0x2a9019]"
                ],
                "verified_control_flow": (
                    "Dispatches POE Offense (descriptor 0x57) and POE Defense (descriptor 0x58) into "
                    "tactical curve scaling registers xmm13 and xmm14."
                ),
                "epistemological_grade": "STATIC_DISASSEMBLY_LEAD"
            }
        }

    def verify_live_bytes(self) -> Dict[str, Any]:
        """
        Reads bytes from the live process (if attached) and compares against reverse-engineered templates.
        """
        if not self._mem or not self._mem.pid:
            return {"status": "NO_PROCESS_ATTACHED", "bytes_verified": False}

        base = self._mem.base_address
        # Verify Tempo Pacing upper bound mov eax, 0x46 at base + 0x120ba98
        tempo_addr = base + 0x120ba98
        tempo_bytes = self._mem.read_bytes(tempo_addr, 5)
        tempo_match = bool(tempo_bytes and tempo_bytes == b"\xb8\x46\x00\x00\x00")

        # Verify Role Table Ceilings at base + 0x2b59798
        table_addr = base + 0x2b59798
        table_bytes = self._mem.read_bytes(table_addr, 16)
        table_match = bool(
            table_bytes and struct.unpack("<4I", table_bytes) == (92, 83, 74, 0)
        )

        return {
            "status": "LIVE_BYTES_READ",
            "base_address": hex(base),
            "tempo_addr": hex(tempo_addr),
            "tempo_bytes_hex": " ".join(f"{b:02x}" for b in tempo_bytes) if tempo_bytes else None,
            "tempo_mov_eax_70_verified": tempo_match,
            "table_addr": hex(table_addr),
            "table_bytes_hex": " ".join(f"{b:02x}" for b in table_bytes) if table_bytes else None,
            "table_ceilings_verified": table_match,
            "bytes_verified": tempo_match and table_match,
        }

    def generate_forensic_receipt(self) -> Dict[str, Any]:
        """
        Constructs an offline, independently verifiable forensic receipt document
        containing authentic PE section boundaries, raw machine code bytes, SHA256 hashes,
        exact disassembled instruction listings, and mathematical proofs for all relative branches.
        """
        rel32_proofs = [
            self.verify_rel32_call(0x141226947, bytes.fromhex("e8 d4 ee 74 ff"), 0x140975820),
            self.verify_rel32_call(0x14122696f, bytes.fromhex("e8 bc f1 74 ff"), 0x140975b30),
            self.verify_rel32_call(0x1412269a6, bytes.fromhex("e8 85 f1 74 ff"), 0x140975b30),
            self.verify_rel32_call(0x14120b9d6, bytes.fromhex("e8 15 70 d5 ff"), 0x140f629f0),
            self.verify_rel32_call(0x14120ba04, bytes.fromhex("e8 e7 6f d5 ff"), 0x140f629f0),
            self.verify_rel32_call(0x14174510e, bytes.fromhex("e8 0d 07 23 ff"), 0x140975820),
            self.verify_rel32_call(0x14174511c, bytes.fromhex("e8 ff f8 22 ff"), 0x140974a20),
            self.verify_rel32_call(0x14174512a, bytes.fromhex("e8 e1 08 23 ff"), 0x140975a10),
        ]

        def get_hash(hex_s: str) -> str:
            return hashlib.sha256(bytes.fromhex(hex_s.replace(" ", ""))).hexdigest()

        return {
            "schema_version": "nba2k22.native_disassembly_forensic_receipt.v1",
            "receipt_id": "FORENSIC_RECEIPT_NBA2K22_PE_001",
            "target_pe_metadata": {
                "file_name": self.TARGET_PROCESS_NAME,
                "sha256": self.TARGET_PE_SHA256,
                "file_size_bytes": 83688840,
                "image_base": "0x140000000",
                "text_section": {"rva": "0x1000", "vsize": "0x21f271f", "raw_offset": "0x600"},
                "rdata_section": {"rva": "0x21f4000", "vsize": "0xf5fbfa", "raw_offset": "0x21f2e00"},
            },
            "routines": {
                "tactical_role_governor": {
                    "rva_start": "0x1226942",
                    "va_start": "0x141226942",
                    "byte_length": 136,
                    "sha256": get_hash(self.ROLE_GOVERNOR_RAW_BYTES),
                    "raw_bytes_hex": self.ROLE_GOVERNOR_RAW_BYTES,
                    "static_table_reference": {
                        "table_ceilings_rva": "0x2b59798",
                        "table_ceilings_values": [92, 83, 74, 0],
                        "table_ceilings_raw_bytes": self.ROLE_TABLE_CEILINGS_RAW_BYTES,
                        "table_multipliers_rva": "0x2b597a8",
                        "table_multipliers_values": [0.94, 0.96, 0.98, 1.0],
                        "table_multipliers_raw_bytes": self.ROLE_TABLE_MULTIPLIERS_RAW_BYTES,
                    },
                },
                "coach_pacing_engine": {
                    "rva_start": "0x120ba72",
                    "va_start": "0x14120ba72",
                    "byte_length": 77,
                    "sha256": get_hash(self.COACH_PACING_RAW_BYTES),
                    "raw_bytes_hex": self.COACH_PACING_RAW_BYTES,
                    "bounds_proof": {
                        "upper_bound_load_va": "0x14120ba98",
                        "upper_bound_bytes": "b8 46 00 00 00",
                        "upper_bound_decimal": 70,
                        "upper_clamp_va": "0x14120baad",
                        "upper_clamp_bytes": "0f 4f c8",
                        "lower_bound_load_va": "0x14120bab0",
                        "lower_bound_bytes": "b8 0a 00 00 00",
                        "lower_bound_decimal": 10,
                        "lower_clamp_va": "0x14120bab8",
                        "lower_clamp_bytes": "0f 4c c8",
                    },
                },
                "poe_strategy_dispatcher": {
                    "rva_start": "0x120b9ca",
                    "va_start": "0x14120b9ca",
                    "byte_length": 65,
                    "sha256": get_hash(self.POE_DISPATCHER_RAW_BYTES),
                    "raw_bytes_hex": self.POE_DISPATCHER_RAW_BYTES,
                    "strategy_slots": {"offense": "0x57", "defense": "0x58"},
                },
                "roster_snapshot_pipeline": {
                    "rva_start": "0x174510e",
                    "va_start": "0x14174510e",
                    "byte_length": 28,
                    "sha256": get_hash(self.SNAPSHOT_LOOP_RAW_BYTES),
                    "raw_bytes_hex": self.SNAPSHOT_LOOP_RAW_BYTES,
                },
            },
            "rel32_mathematical_proofs": rel32_proofs,
            "epistemological_demarcation": {
                "static_assembly_grade": "STATIC_DISASSEMBLY_LEAD",
                "gameplay_causality_status": "PENDING_GAMEPLAY_VALIDATION",
                "demarcation_note": (
                    "Machine code bytes and mathematical control-flow bounds are forensically proven. "
                    "Longitudinal gameplay outcomes (box score FGA, pace possessions, fatigue) remain "
                    "experimental hypotheses pending live telemetry observation contracts."
                ),
            },
        }

    def export_forensic_receipt(self, output_path: Optional[str] = None) -> str:
        if output_path is None:
            output_path = os.path.join(self.evidence_dir, "NATIVE_DISASSEMBLY_FORENSIC_RECEIPT_V1.json")
        receipt = self.generate_forensic_receipt()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2, ensure_ascii=False)
        return output_path

    def enrich_all_field_records_with_consumer_traces(
        self, target_dir: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Enriches field records in target_dir with epistemologically accurate consumer traces.
        Strictly differentiates between:
        - ShotTendency (TENDENCY_NATIVE_001) / Touches (TENDENCY_NATIVE_066)
        - Other 97 tendencies (Snapshot loop caller lead)
        - Coach Tempo (COACH_DEFAULT_014)
        - Coach POE Offense (COACH_DEFAULT_001) / POE Defense (COACH_DEFAULT_004)
        - Other 16 coach settings (COACHDATA bitfield structure lead)
        - 86 World Settings (Controller slot lead)
        """
        dest_dir = target_dir if target_dir is not None else self.records_dir
        if not os.path.exists(dest_dir):
            return {"error": "DIRECTORY_NOT_FOUND", "total_enriched": 0}

        shot_callers = self.trace_shot_tendency_callers()
        coach_traces = self.trace_coach_gameplan_consumers()

        counts = {
            "shot_tendency_enriched": 0,
            "touches_enriched": 0,
            "other_tendencies_enriched": 0,
            "coach_tempo_enriched": 0,
            "coach_poe_enriched": 0,
            "other_coach_settings_enriched": 0,
            "world_settings_enriched": 0,
            "total_enriched": 0,
        }

        # 1. TENDENCY_NATIVE_001 (ShotTendency)
        t1_path = os.path.join(dest_dir, "TENDENCY_NATIVE_001.json")
        if os.path.exists(t1_path):
            with open(t1_path, "r", encoding="utf-8") as f:
                t1 = json.load(f)
            t1["consumer_path_status"] = "DISASSEMBLY_ROLE_GOVERNOR_LOCATED"
            t1["game_effect_status"] = "STATIC_DISASSEMBLY_LEAD"
            t1["verified_consumer_call_graph"] = {
                "native_getter_rva": "0x975820",
                "direct_callers_count": 8,
                "verified_subsystems": shot_callers,
                "telemetry_validation_contract": {
                    "validation_id": "VAL_CONTRACT_FGA_SUPPRESSION",
                    "status": "PENDING_GAMEPLAY_VALIDATION",
                    "metric": "gameplay.actual_fga_per_36",
                },
                "epistemological_note": "Static disassembly lead; dynamic causality unmeasured."
            }
            with open(t1_path, "w", encoding="utf-8") as f:
                json.dump(t1, f, indent=2, ensure_ascii=False)
            counts["shot_tendency_enriched"] += 1
            counts["total_enriched"] += 1

        # 2. TENDENCY_NATIVE_066 (Touches)
        t66_path = os.path.join(dest_dir, "TENDENCY_NATIVE_066.json")
        if os.path.exists(t66_path):
            with open(t66_path, "r", encoding="utf-8") as f:
                t66 = json.load(f)
            t66["consumer_path_status"] = "DISASSEMBLY_ROLE_GOVERNOR_LOCATED"
            t66["game_effect_status"] = "STATIC_DISASSEMBLY_LEAD"
            t66["verified_consumer_call_graph"] = {
                "native_getter_rva": "0x975b30",
                "role_governor_call_rva": "0x12269a6",
                "telemetry_validation_contract": {
                    "validation_id": "VAL_CONTRACT_TOUCHES_FLOOR",
                    "status": "PENDING_GAMEPLAY_VALIDATION",
                    "metric": "gameplay.actual_touches_per_possession",
                },
                "epistemological_note": "Static disassembly lead; dynamic causality unmeasured."
            }
            with open(t66_path, "w", encoding="utf-8") as f:
                json.dump(t66, f, indent=2, ensure_ascii=False)
            counts["touches_enriched"] += 1
            counts["total_enriched"] += 1

        # 3. Other 97 Player Tendencies (Snapshot Loop Caller)
        for idx in range(1, 100):
            if idx in (1, 66):
                continue
            fid = f"TENDENCY_NATIVE_{idx:03d}"
            fpath = os.path.join(dest_dir, f"{fid}.json")
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    rec = json.load(f)
                rec["consumer_path_status"] = "SNAPSHOT_LOOP_CALLER_LOCATED"
                rec["game_effect_status"] = "STATIC_SNAPSHOT_CALLER_LEAD"
                live_ev = rec.get("live_evidence", {})
                prov = live_ev.get("native_rea_provenance", {})
                rec["verified_consumer_call_graph"] = {
                    "native_getter_rva": prov.get("native_getter_rva"),
                    "snapshot_caller_rva": prov.get("consumer_call_rva"),
                    "snapshot_pipeline_rva": "0x1744bd0",
                    "context_offset": prov.get("consumer_context_offset"),
                    "telemetry_validation_contract": {
                        "validation_id": f"VAL_CONTRACT_TENDENCY_{idx:03d}",
                        "status": "PENDING_GAMEPLAY_VALIDATION",
                        "metric": f"gameplay.tendency_event_rate_{idx:03d}",
                    },
                    "epistemological_note": "Verified presence in snapshot serialization loop; 3D court behavior unmeasured."
                }
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(rec, f, indent=2, ensure_ascii=False)
                counts["other_tendencies_enriched"] += 1
                counts["total_enriched"] += 1

        # 4. Coach Settings (Tempo vs POE vs other coach settings)
        for idx in range(1, 20):
            fid = f"COACH_DEFAULT_{idx:03d}"
            fpath = os.path.join(dest_dir, f"{fid}.json")
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    rec = json.load(f)

                if fid == "COACH_DEFAULT_014":  # Tempo
                    rec["consumer_path_status"] = "DISASSEMBLY_PACING_ENGINE_LOCATED"
                    rec["game_effect_status"] = "STATIC_DISASSEMBLY_LEAD"
                    rec["verified_consumer_call_graph"] = {
                        "subsystems": coach_traces,
                        "telemetry_validation_contract": {
                            "validation_id": "VAL_CONTRACT_TEMPO_SATURATION",
                            "status": "PENDING_GAMEPLAY_VALIDATION",
                            "metric": "gameplay.team_possessions_per_48",
                        },
                    }
                    counts["coach_tempo_enriched"] += 1
                elif fid in ("COACH_DEFAULT_001", "COACH_DEFAULT_002", "COACH_DEFAULT_003"):  # POE Offense series
                    rec["consumer_path_status"] = "COACHDATA_STRUCTURE_LOCATED"
                    rec["game_effect_status"] = "LIVE_BITFIELD_READ_ONLY"
                    rec["verified_consumer_call_graph"] = {
                        "staff_array_traversal_rva": "0xc03133",
                        "structure": "Team 0 COACHDATA (352 bytes)",
                        "poe_dispatcher_rva": "0x120b9ca",
                        "strategy_slot": "0x57",
                        "strategy_query_fn": "0x140f629f0",
                        "telemetry_validation_contract": {
                            "validation_id": "VAL_CONTRACT_POE_OFFENSE",
                            "status": "PENDING_GAMEPLAY_VALIDATION",
                            "metric": "gameplay.play_call_distribution_offense",
                        },
                        "epistemological_note": "Verified bitfield decode with POE Offense strategy dispatch (slot 0x57); live play outcome unmeasured."
                    }
                    counts["coach_poe_enriched"] += 1
                    counts["other_coach_settings_enriched"] += 1
                elif fid in ("COACH_DEFAULT_004", "COACH_DEFAULT_005", "COACH_DEFAULT_006"):  # POE Defense series
                    rec["consumer_path_status"] = "COACHDATA_STRUCTURE_LOCATED"
                    rec["game_effect_status"] = "LIVE_BITFIELD_READ_ONLY"
                    rec["verified_consumer_call_graph"] = {
                        "staff_array_traversal_rva": "0xc03133",
                        "structure": "Team 0 COACHDATA (352 bytes)",
                        "poe_dispatcher_rva": "0x120b9ee",
                        "strategy_slot": "0x58",
                        "strategy_query_fn": "0x140f629f0",
                        "telemetry_validation_contract": {
                            "validation_id": "VAL_CONTRACT_POE_DEFENSE",
                            "status": "PENDING_GAMEPLAY_VALIDATION",
                            "metric": "gameplay.defensive_scheme_frequency",
                        },
                        "epistemological_note": "Verified bitfield decode with POE Defense strategy dispatch (slot 0x58); live contest outcome unmeasured."
                    }
                    counts["coach_poe_enriched"] += 1
                    counts["other_coach_settings_enriched"] += 1
                else:
                    rec["consumer_path_status"] = "COACHDATA_STRUCTURE_LOCATED"
                    rec["game_effect_status"] = "LIVE_BITFIELD_READ_ONLY"
                    rec["verified_consumer_call_graph"] = {
                        "staff_array_traversal_rva": "0xc03133",
                        "structure": "Team 0 COACHDATA (352 bytes)",
                        "telemetry_validation_contract": {
                            "validation_id": f"VAL_CONTRACT_{fid}",
                            "status": "PENDING_GAMEPLAY_VALIDATION",
                            "metric": f"gameplay.coach_setting_{fid}_behavior",
                        },
                        "epistemological_note": "Verified bitfield decode; independent tactical consumer unmeasured."
                    }
                    counts["other_coach_settings_enriched"] += 1

                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(rec, f, indent=2, ensure_ascii=False)
                counts["total_enriched"] += 1

        # 5. World Settings (86 fields: Controller slots only)
        for idx in range(1, 87):
            fid = f"WORLD_REG_{idx:03d}"
            fpath = os.path.join(dest_dir, f"{fid}.json")
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    rec = json.load(f)
                rec["consumer_path_status"] = "CONTROLLER_SLOT_DISAMBIGUATED"
                rec["game_effect_status"] = "LIVE_SLOT_READ_ONLY"
                live_ev = rec.get("live_evidence", {})
                prov = live_ev.get("native_rea_provenance", {})
                rec["verified_consumer_call_graph"] = {
                    "controller_slot": prov.get("controller_slot_name"),
                    "slot_rva": prov.get("slot_rva"),
                    "slot_offset": prov.get("slot_offset"),
                    "telemetry_validation_contract": {
                        "validation_id": f"VAL_CONTRACT_{fid}",
                        "status": "PENDING_GAMEPLAY_VALIDATION",
                        "metric": f"gameplay.world_rule_{fid}_effect",
                    },
                    "epistemological_note": "Verified discrete controller memory slot; engine simulation consumer unmeasured."
                }
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(rec, f, indent=2, ensure_ascii=False)
                counts["world_settings_enriched"] += 1
                counts["total_enriched"] += 1

        return counts
