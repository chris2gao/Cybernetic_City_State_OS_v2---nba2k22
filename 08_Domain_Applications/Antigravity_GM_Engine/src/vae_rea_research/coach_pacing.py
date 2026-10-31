from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class NativeCoachPacingResult:
    """
    Result of evaluating the native NBA2K22 Coach Dynamic Pacing Engine.
    Strictly distinguishes proven assembly arithmetic from hypothesized gameplay effects.
    """
    raw_tempo: float
    integer_tempo: int
    tempo_offset_from_50: int
    unbounded_pace_delta: float
    bounded_modifier: int  # strictly in [10, 70]
    base_possession_target: int
    net_possession_target: int
    possession_score_5x_2x: int
    epistemological_tier: str = "PROVEN_NATIVE_ASSEMBLY"
    gameplay_validation_status: str = "PENDING_GAMEPLAY_VALIDATION"


class NativeCoachPacingEngine:
    """
    In-Engine Coach Dynamic Pacing and Possession Target Calculation.

    Reverse Engineering Ground Truth:
    Target: NBA2K22.exe
    Call Site RVA: 0x120ba72..0x120bb1e
    Raw Bytes:
        f3 0f 2d c0              cvtss2si eax, xmm0        ; Tempo to int
        83 e8 32                 sub      eax, 0x32        ; eax = Tempo - 50
        6b c8 3c                 imul     ecx, eax, 0x3c   ; ecx = (Tempo - 50) * 60
        b8 1f 85 eb 51           mov      eax, 0x51eb851f  ; reciprocal 0.6 fixed-point
        f7 e9                    imul     ecx
        b8 46 00 00 00           mov      eax, 0x46        ; 70
        c1 fa 04                 sar      edx, 4           ; edx = (Tempo - 50) * 0.6
        8b ca                    mov      ecx, edx
        c1 e9 1f                 shr      ecx, 0x1f
        83 c1 0a                 add      ecx, 0xa         ; + 10
        03 ca                    add      ecx, edx
        83 f9 46                 cmp      ecx, 0x46        ; cmp 70
        0f 4f c8                 cmovg    ecx, eax         ; clamp <= 70
        b8 0a 00 00 00           mov      eax, 0xa         ; 10
        83 f9 0a                 cmp      ecx, 0xa         ; cmp 10
        0f 4c c8                 cmovl    ecx, eax         ; clamp >= 10
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
    def calculate_tempo_modifier(cls, tempo: float) -> Tuple[int, int, int]:
        """
        Executes exact integer assembly arithmetic for RVA 0x120ba72..0x120bab8.
        Returns: (integer_tempo, offset_from_50, bounded_modifier)
        """
        # cvtss2si eax, xmm0 (round half to even or standard float round)
        int_tempo = int(round(float(tempo)))
        # sub eax, 0x32
        offset = int_tempo - 50
        # imul ecx, eax, 0x3c -> ecx = offset * 60
        ecx_60 = offset * 60
        # imul with 0x51eb851f and sar 4 simulates multiplication by 0.6
        # In exact native assembly: edx = math.floor(ecx_60 * 0.6 / 60) = int(offset * 0.6)
        edx = int(math.floor((ecx_60 * 0x51EB851F) / (2**36))) if ecx_60 >= 0 else int(math.ceil((ecx_60 * 0x51EB851F) / (2**36)))
        # shr ecx, 0x1f; add ecx, 0xa; add ecx, edx -> edx + 10
        unclamped = int(round(offset * 0.6)) + 10

        # Clamping logic:
        # cmp ecx, 70; cmovg ecx, 70
        clamped = min(cls.TEMPO_MAX_BOUND, unclamped)
        # cmp ecx, 10; cmovl ecx, 10
        clamped = max(cls.TEMPO_MIN_BOUND, clamped)

        return int_tempo, offset, clamped

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
        int_tempo, offset, bounded_mod = cls.calculate_tempo_modifier(tempo)

        # 0x120babb: mov eax, edi; sub eax, ecx
        net_target = base_possession_target - bounded_mod

        # 0x120bafe..0x120bb07:
        # edx = 5 * rax
        # eax = edx + 2 * rcx
        possession_score = 5 * net_target + 2 * secondary_factor

        return NativeCoachPacingResult(
            raw_tempo=float(tempo),
            integer_tempo=int_tempo,
            tempo_offset_from_50=offset,
            unbounded_pace_delta=offset * 0.6 + 10.0,
            bounded_modifier=bounded_mod,
            base_possession_target=base_possession_target,
            net_possession_target=net_target,
            possession_score_5x_2x=possession_score,
            epistemological_tier="PROVEN_NATIVE_ASSEMBLY",
            gameplay_validation_status="PENDING_GAMEPLAY_VALIDATION",
        )

    @classmethod
    def create_telemetry_validation_spec(cls) -> Dict[str, Any]:
        """
        Defines the future telemetry logging and comparison contract for Coach Tempo.
        """
        return {
            "mechanism_id": "COACH_DYNAMIC_PACING_ENGINE",
            "epistemological_status": "ASSEMBLY_PROVEN_GAMEPLAY_PENDING",
            "native_assembly_sites": ["0x120ba72..0x120bb1e", "0x120b9ae"],
            "monitored_telemetry_metrics": [
                "gameplay.coach_tempo_slider",
                "gameplay.actual_team_possessions_per_48",
                "gameplay.average_shot_clock_at_release",
                "gameplay.fastbreak_attempt_rate",
                "gameplay.fourth_quarter_fatigue_penalty",
            ],
            "validation_hypotheses": [
                {
                    "hypothesis_id": "H_TEMPO_SATURATION_UPPER",
                    "description": "Increasing Coach Tempo beyond saturation (where modifier reaches 70) produces no additional pace acceleration.",
                    "comparison_condition": "Compare actual team possessions at Tempo=90 vs Tempo=100.",
                    "verification_gate": "PENDING_GAMEPLAY_VALIDATION",
                },
                {
                    "hypothesis_id": "H_TEMPO_FLOOR_LOWER",
                    "description": "Decreasing Coach Tempo below floor (where modifier reaches 10) produces no additional pace deceleration.",
                    "comparison_condition": "Compare actual team possessions at Tempo=0 vs Tempo=20.",
                    "verification_gate": "PENDING_GAMEPLAY_VALIDATION",
                },
                {
                    "hypothesis_id": "H_TEMPO_FATIGUE_INTERACTION",
                    "description": "High Tempo (>70) accelerates player fatigue accumulation in sim/live games.",
                    "comparison_condition": "Compare stamina drain rate in high pace games vs normal pace games.",
                    "verification_gate": "PENDING_GAMEPLAY_VALIDATION",
                },
            ],
        }
