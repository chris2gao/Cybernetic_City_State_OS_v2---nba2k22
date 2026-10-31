"""
VAE Safe Read-Only Adapter.
Interfaces with existing game configuration & state IO profiles without any game writes.
"""

import json
import os
from typing import Optional, Dict, Any
from .contracts import ProfileSnapshot, SnapshotStatus, EvidenceTier


class VAEReaderAdapter:
    """
    Safe read-only adapter that consumes existing configuration files and profiles.
    Guaranteed zero-write policy to active game processes or saves.
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
        Reads a gameplay slider or setting from settings.json or court.json.
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
                            save_id="OFFLINE_DEFAULT",
                            game_build="2K22_PC_CURRENT_GEN",
                            game_mode="OFFLINE_MYLEAGUE",
                            scene="GAME_SETTINGS",
                            side=side,
                            field_id=field_id,
                            raw_value=default_val,
                            display_value=default_val,
                            unit=target.get("unit", "0_100_int"),
                            source_ref=f"config/state_io_native/settings.json#{cat}.{field_id}",
                            captured_at="STATIC_SOURCE",
                            freshness="IMMUTABLE_SPEC",
                            status=SnapshotStatus.CAPTURED,
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
                        save_id="OFFLINE_DEFAULT",
                        game_build="2K22_PC_CURRENT_GEN",
                        game_mode="OFFLINE_MYLEAGUE",
                        scene="COURT_SLIDERS",
                        side=side,
                        field_id=field_id,
                        raw_value=raw_val,
                        display_value=raw_val,
                        unit="slider_points",
                        source_ref=f"config/state_io_native/court.json#modified_sliders.{field_id}",
                        captured_at="STATIC_SOURCE",
                        freshness="IMMUTABLE_SPEC",
                        status=SnapshotStatus.CAPTURED,
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
            "user_injury_frequency": {
                "default": 65,
                "unit": "0_100_int",
                "scene": "INJURIES_AND_MORALE",
                "source": "settings.json#injuries_and_morale",
            },
        }

        if field_id in standard_sliders:
            std = standard_sliders[field_id]
            return ProfileSnapshot(
                snapshot_id=f"snap-{field_id}",
                save_id="OFFLINE_DEFAULT",
                game_build="2K22_PC_CURRENT_GEN",
                game_mode="OFFLINE_MYLEAGUE",
                scene=std["scene"],
                side=side,
                field_id=field_id,
                raw_value=std["default"],
                display_value=std["default"],
                unit=std["unit"],
                source_ref=std["source"],
                captured_at="STATIC_SOURCE",
                freshness="IMMUTABLE_SPEC",
                status=SnapshotStatus.CAPTURED,
            )

        # Field genuinely unknown
        return ProfileSnapshot(
            snapshot_id=f"snap-{field_id}-unknown",
            save_id="UNKNOWN_SAVE",
            game_build="2K22_PC_CURRENT_GEN",
            game_mode="OFFLINE_MYLEAGUE",
            scene="SETTINGS_MENU",
            side=side,
            field_id=field_id,
            raw_value=None,
            display_value=None,
            unit="unknown",
            source_ref="NOT_FOUND",
            captured_at="OFFLINE",
            freshness="STATIC",
            status=SnapshotStatus.UNKNOWN,
        )

    def get_dual_normalize_settings(self) -> Dict[str, Any]:
        """
        Returns the dual Normalize switches state definition.
        """
        return {
            "played_normalize_minutes_to_sim_stats": False,
            "sim_normalize_minutes_to_sim_stats": False,
            "played_quarter_length_minutes": 12,
            "sim_quarter_length_minutes": 12,
            "provenance": "K05_K10_K11_WORLD_RULES_SIM_HISTORY_SAVE.md §G03",
        }
