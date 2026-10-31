from __future__ import annotations

import ctypes
import decimal
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class NativeCoachPacingResult:
    """
    Result of evaluating the static disassembly model of the NBA2K22 Coach Dynamic Pacing Engine.
    Strictly distinguishes proven register assembly arithmetic from hypothesized gameplay effects.
    """
    raw_tempo: float
    integer_tempo: int
    tempo_offset_from_50: int
    unclamped_register_ecx: int
    bounded_modifier: int  # strictly in [10, 70]
    base_possession_target: int
    hypothesized_net_target: int  # base_possession_target - bounded_modifier (simulation hypothesis)
    possession_score_5x_2x: int   # 5 * net_target + 2 * secondary_factor
    intermediate_registers: Dict[str, int]
    epistemological_tier: str = "STATIC_DISASSEMBLY_LEAD"
    gameplay_validation_status: str = "PENDING_GAMEPLAY_VALIDATION"


class NativeCoachPacingEngine:
    """
    In-Engine Coach Dynamic Pacing and Possession Target Calculation.

    Reverse Engineering Ground Truth:
    Target: NBA2K22.exe
    Call Site RVA: 0x120ba72..0x120bb1e
    Raw Bytes:
        f3 0f 2d c0              cvtss2si eax, xmm0        ; Tempo to int (SSE2 round to nearest even)
        83 e8 32                 sub      eax, 0x32        ; eax = Tempo - 50
        6b c8 3c                 imul     ecx, eax, 0x3c   ; ecx = (Tempo - 50) * 60
        b8 1f 85 eb 51           mov      eax, 0x51eb851f  ; magic reciprocal (1374389535)
        f7 e9                    imul     ecx              ; signed multiply EDX:EAX = EAX * ECX
        b8 46 00 00 00           mov      eax, 0x46        ; 70
        c1 fa 04                 sar      edx, 4           ; edx = edx >> 4 (arithmetic shift)
        8b ca                    mov      ecx, edx
        c1 e9 1f                 shr      ecx, 0x1f        ; ecx = sign bit
        83 c1 0a                 add      ecx, 0xa         ; ecx = sign bit + 10
        03 ca                    add      ecx, edx         ; ecx = edx + sign bit + 10
        83 f9 46                 cmp      ecx, 0x46        ; cmp ecx, 70
        0f 4f c8                 cmovg    ecx, eax         ; if ecx > 70: ecx = 70
        b8 0a 00 00 00           mov      eax, 0xa         ; 10
        83 f9 0a                 cmp      ecx, 0xa         ; cmp ecx, 10
        0f 4c c8                 cmovl    ecx, eax         ; if ecx < 10: ecx = 10
        8b c7                    mov      eax, edi
        2b c1                    sub      eax, ecx         ; net_target = edi - ecx

    Composite Lineup Evaluation (0x120bafe..0x120bb07):
        edx = rax + rax * 4    ; 5 * rax
        eax = rdx + rcx * 2    ; 5 * rax + 2 * rcx
    """

    TEMPO_MIN_BOUND = 10
    TEMPO_MAX_BOUND = 70
    DEFAULT_BASE_POSSESSIONS = 100

    @classmethod
    def emulate_x86_pacing_instructions(cls, tempo: float) -> Dict[str, Any]:
        """
        Executes exact 32-bit x86 register arithmetic emulation matching the native instructions.
        Returns full dictionary of intermediate register values.
        """
        # 1. cvtss2si eax, xmm0 (round half to even)
        try:
            d = decimal.Decimal(str(float(tempo))).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_EVEN)
            int_tempo = int(d)
        except Exception:
            int_tempo = int(round(float(tempo)))
        eax = ctypes.c_int32(int_tempo).value

        # 2. sub eax, 0x32
        offset = ctypes.c_int32(eax - 0x32).value

        # 3. imul ecx, eax, 0x3c
        ecx_60 = ctypes.c_int32(offset * 0x3C).value

        # 4. mov eax, 0x51eb851f; imul ecx
        magic = 0x51EB851F  # signed 32-bit integer: 1374389535
        prod_64 = magic * ecx_60
        edx_high = ctypes.c_int32(prod_64 >> 32).value
        eax_low = ctypes.c_uint32(prod_64 & 0xFFFFFFFF).value

        # 5. sar edx, 4
        sar_edx = ctypes.c_int32(edx_high >> 4).value

        # 6. mov ecx, edx; shr ecx, 0x1f
        sign_bit = (ctypes.c_uint32(sar_edx).value >> 31)

        # 7. add ecx, 0xa; add ecx, edx
        unclamped_ecx = ctypes.c_int32(sign_bit + 10 + sar_edx).value

        # 8. cmp ecx, 70; cmovg ecx, eax (eax=70)
        clamped_ecx = unclamped_ecx
        if clamped_ecx > cls.TEMPO_MAX_BOUND:
            clamped_ecx = cls.TEMPO_MAX_BOUND

        # 9. cmp ecx, 10; cmovl ecx, eax (eax=10)
        if clamped_ecx < cls.TEMPO_MIN_BOUND:
            clamped_ecx = cls.TEMPO_MIN_BOUND

        return {
            "int_tempo": int_tempo,
            "offset": offset,
            "ecx_60": ecx_60,
            "prod_64": prod_64,
            "edx_high": edx_high,
            "sar_edx": sar_edx,
            "sign_bit": sign_bit,
            "unclamped_ecx": unclamped_ecx,
            "bounded_modifier": clamped_ecx,
        }

    @classmethod
    def calculate_tempo_modifier(cls, tempo: float) -> Tuple[int, int, int]:
        """
        Executes exact integer assembly arithmetic for RVA 0x120ba72..0x120bab8.
        Returns: (integer_tempo, offset_from_50, bounded_modifier)
        """
        regs = cls.emulate_x86_pacing_instructions(tempo)
        return regs["int_tempo"], regs["offset"], regs["bounded_modifier"]

    @classmethod
    def evaluate(
        cls,
        tempo: float,
        base_possession_target: int = DEFAULT_BASE_POSSESSIONS,
        secondary_factor: int = 15,
    ) -> NativeCoachPacingResult:
        """
        Calculates the complete native pacing chain including possession net target
        and the 5x + 2x possession candidate score.
        """
        regs = cls.emulate_x86_pacing_instructions(tempo)
        int_tempo = regs["int_tempo"]
        offset = regs["offset"]
        unclamped_ecx = regs["unclamped_ecx"]
        bounded_mod = regs["bounded_modifier"]

        # 0x120babb: mov eax, edi; sub eax, ecx
        # NOTE: edi is hypothesized as the possession pacing baseline in the simulation struct.
        net_target = base_possession_target - bounded_mod

        # 0x120bafe..0x120bb07:
        # edx = 5 * rax
        # eax = edx + 2 * rcx
        possession_score = 5 * net_target + 2 * secondary_factor

        return NativeCoachPacingResult(
            raw_tempo=float(tempo),
            integer_tempo=int_tempo,
            tempo_offset_from_50=offset,
            unclamped_register_ecx=unclamped_ecx,
            bounded_modifier=bounded_mod,
            base_possession_target=base_possession_target,
            hypothesized_net_target=net_target,
            possession_score_5x_2x=possession_score,
            intermediate_registers=regs,
            epistemological_tier="STATIC_DISASSEMBLY_LEAD",
            gameplay_validation_status="PENDING_GAMEPLAY_VALIDATION",
        )

    @classmethod
    def create_telemetry_validation_spec(cls) -> Dict[str, Any]:
        """
        Defines the future telemetry logging and comparison semantic requirement for Coach Tempo.
        Does NOT mandate database schemas, file formats, or transport protocols.
        """
        return {
            "hypothesis_id": "VAL_CONTRACT_TEMPO_SATURATION",
            "target_mechanism": "COACH_DYNAMIC_PACING_ENGINE",
            "epistemological_status": "STATIC_DISASSEMBLY_LEAD",
            "disassembly_call_sites": ["0x120ba72..0x120bb1e", "0x120b9ae"],
            "required_metrics": [
                {
                    "metric_name": "coach_tempo_slider",
                    "semantic_role": "independent_variable",
                    "observation_type": "DIRECT_SETTING_READ",
                },
                {
                    "metric_name": "team_possessions_per_48",
                    "semantic_role": "primary_outcome",
                    "observation_type": "DERIVED_FROM_BOXSCORE_PACE",
                },
                {
                    "metric_name": "normalize_stats_rule",
                    "semantic_role": "confounder_control",
                    "observation_type": "DIRECT_SETTING_READ",
                },
                {
                    "metric_name": "sim_quarter_length",
                    "semantic_role": "confounder_control",
                    "observation_type": "DIRECT_SETTING_READ",
                },
            ],
            "comparison_conditions": [
                {
                    "condition_name": "TEMPO_MAX_SATURATION_CHECK",
                    "group_a": "Tempo in [90, 100] (where native modifier saturates at 70)",
                    "group_b": "Tempo in [75, 85]",
                    "expected_trend": "Possessions curve flattens as modifier reaches assembly upper ceiling 70.",
                },
                {
                    "condition_name": "TEMPO_MIN_FLOOR_CHECK",
                    "group_a": "Tempo in [0, 40] (where native modifier is clamped to minimum floor 10)",
                    "group_b": "Tempo = 50 (baseline modifier 10)",
                    "expected_trend": "Possessions curve does not decelerate below floor value 10.",
                },
            ],
            "fallback_if_unrecorded": "FLAG_AS_UNKNOWN",
        }
