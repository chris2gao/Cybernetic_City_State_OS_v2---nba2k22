"""
VAE Safe Read-Only Adapter.
Interfaces with existing game configuration & state IO profiles without any game writes.
Fixes P0-01: Disentangles static spec defaults from live observed captures.
Never marks static config readouts as SnapshotStatus.CAPTURED.
"""

import json
import os
from typing import Optional, Dict, Any
from .contracts import ProfileSnapshot, SnapshotStatus, EvidenceTier


class VAEReaderAdapter:
    """
    Safe read-only adapter that consumes existing configuration files and profiles.
    Guaranteed zero-write policy to active game processes or saves.
    Strictly reports STATIC_SPEC or OFFLINE_FIXTURE, never false CAPTURED.
    """

    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.settings_path = os.path.join(
            repo_root, "08_Domain_Applications", "Antigravity_GM_Engine", "config", "state_io_native", "settings.json"
        )
        self.court_path = os.path.join(
            repo_root, "08_Domain_Applications", "Antigravity_GM_Engine", "config", "state_io_native", "court.json"
        )
        self.training_path = os.path.join(
            repo_root, "08_Domain_Applications", "Antigravity_GM_Engine", "config", "state_io_native", "training.json"
        )

    def read_settings_field(self, field_id: str, side: str = "USER") -> ProfileSnapshot:
        """
        Reads a gameplay slider or setting from static configurations.
        Fixes P0-01: Correctly marks static specifications as STATIC_SPEC or OFFLINE_FIXTURE,
        never claiming SnapshotStatus.CAPTURED without a verified live game process.
        """
        # 1. Search in settings.json (fields dictionary)
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                fields = data.get("fields", {})
                for cat, items in fields.items():
                    if isinstance(items, dict) and field_id in items:
                        target = items[field_id]
                        default_val = target.get("default", 50)
                        return ProfileSnapshot(
                            snapshot_id=f"snap-{field_id}",
                            save_id=None,  # No active save attached in static spec
                            game_build="2K22_PC_CURRENT_GEN",
                            game_mode="OFFLINE_MYLEAGUE",
                            scene="GAME_SETTINGS",
                            side=side,
                            field_id=field_id,
                            raw_value=default_val,
                            display_value=default_val,
                            unit=target.get("unit", "0_100_int"),
                            source_ref=f"config/state_io_native/settings.json#{cat}.{field_id}",
                            captured_at=None,  # Not captured from live memory
                            freshness="IMMUTABLE_SPEC",
                            status=SnapshotStatus.STATIC_SPEC,
                        )
            except Exception:
                pass

        # 2. Search in court.json (modified_sliders)
        if os.path.exists(self.court_path):
            try:
                with open(self.court_path, "r", encoding="utf-8") as f:
                    court_data = json.load(f)
                mod_sliders = court_data.get("modified_sliders", {})
                if field_id in mod_sliders:
                    s_info = mod_sliders[field_id]
                    raw_val = s_info.get(f"hof_default_{side.lower()}", 50.0)
                    return ProfileSnapshot(
                        snapshot_id=f"snap-{field_id}",
                        save_id=None,
                        game_build="2K22_PC_CURRENT_GEN",
                        game_mode="OFFLINE_MYLEAGUE",
                        scene="COURT_SLIDERS",
                        side=side,
                        field_id=field_id,
                        raw_value=raw_val,
                        display_value=raw_val,
                        unit="slider_points",
                        source_ref=f"config/state_io_native/court.json#modified_sliders.{field_id}",
                        captured_at=None,
                        freshness="IMMUTABLE_SPEC",
                        status=SnapshotStatus.STATIC_SPEC,
                    )
            except Exception:
                pass

        # 3. Known standard gameplay slider fixtures (e.g. three_point_success)
        standard_sliders = {
            "three_point_success": {
                "default": 50,
                "unit": "0_100_slider",
                "scene": "GAMEPLAY_SHOOTING_SLIDERS",
                "source": "NBA2K22_DEFAULT_HOF_SLIDERS",
            },
            "mid_range_shot_success": {
                "default": 50,
                "unit": "0_100_slider",
                "scene": "GAMEPLAY_SHOOTING_SLIDERS",
                "source": "NBA2K22_DEFAULT_HOF_SLIDERS",
            },
            "defensive_awareness": {
                "default": 50,
                "unit": "0_100_slider",
                "scene": "DEFENSE_SLIDERS",
                "source": "NBA2K22_DEFAULT_HOF_SLIDERS",
            },
            "fatigue_rate": {
                "default": 50,
                "unit": "0_100_slider",
                "scene": "FATIGUE_SLIDERS",
                "source": "NBA2K22_DEFAULT_HOF_SLIDERS",
            },
        }

        if field_id in standard_sliders:
            cfg = standard_sliders[field_id]
            return ProfileSnapshot(
                snapshot_id=f"snap-{field_id}",
                save_id=None,
                game_build="2K22_PC_CURRENT_GEN",
                game_mode="OFFLINE_MYLEAGUE",
                scene=cfg["scene"],
                side=side,
                field_id=field_id,
                raw_value=cfg["default"],
                display_value=cfg["default"],
                unit=cfg["unit"],
                source_ref=f"fixture/standard_sliders#{field_id}",
                captured_at=None,
                freshness="FIXTURE_DEFAULT",
                status=SnapshotStatus.OFFLINE_FIXTURE,
            )

        # 4. Unknown field fallback
        return ProfileSnapshot(
            snapshot_id=f"snap-unknown-{field_id}",
            save_id=None,
            game_build="2K22_PC_CURRENT_GEN",
            game_mode="OFFLINE_MYLEAGUE",
            scene="UNKNOWN_SCENE",
            side=side,
            field_id=field_id,
            raw_value=None,
            display_value=None,
            unit="unknown",
            source_ref=f"UNKNOWN_FIELD#{field_id}",
            captured_at=None,
            freshness="STALE_OR_MISSING",
            status=SnapshotStatus.UNKNOWN,
        )


    def get_dual_normalize_settings(self) -> Dict[str, Any]:
        """
        Reads dual normalize switches from static knowledge specifications.
        Note (P2-12): Returns research specifications; live runtime memory mapping remains UNKNOWN.
        """
        return {
            "played_normalize_minutes_to_sim_stats": False,
            "sim_normalize_minutes_to_sim_stats": False,
            "played_quarter_length_minutes": 12,
            "sim_quarter_length_minutes": 12,
            "status": "STATIC_RESEARCH_SPECIFICATION",
            "runtime_memory_address": "UNKNOWN_PENDING_LIVE_READBACK",
        }
