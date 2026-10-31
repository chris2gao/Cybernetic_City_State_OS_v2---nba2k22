"""
Tests for VAE Read-Only Reader Adapter Safety.
Fixes P0-01: Proves that static configurations return STATIC_SPEC or OFFLINE_FIXTURE,
and never false CAPTURED without live game connection.
"""

import os
from src.vae.reader_adapter import VAEReaderAdapter
from src.vae.contracts import SnapshotStatus


def test_reader_adapter_read_only_and_fallback():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    adapter = VAEReaderAdapter(repo_root=repo_root)

    # 1. Read existing field from static config -> must be STATIC_SPEC or OFFLINE_FIXTURE, NOT CAPTURED
    snap = adapter.read_settings_field("three_point_success", side="USER")
    assert snap.status in [SnapshotStatus.STATIC_SPEC, SnapshotStatus.OFFLINE_FIXTURE]
    assert snap.status != SnapshotStatus.CAPTURED
    assert snap.raw_value is not None
    assert snap.captured_at is None  # Not captured from live memory

    # 2. Read nonexistent field -> graceful fallback to UNKNOWN
    snap_unknown = adapter.read_settings_field("nonexistent_slider_xyz", side="USER")
    assert snap_unknown.status == SnapshotStatus.UNKNOWN
    assert snap_unknown.raw_value is None

    # 3. Read dual normalize
    norm = adapter.get_dual_normalize_settings()
    assert "played_normalize_minutes_to_sim_stats" in norm
    assert "sim_normalize_minutes_to_sim_stats" in norm
    assert norm["played_quarter_length_minutes"] == 12
    assert norm["runtime_memory_address"] == "UNKNOWN_PENDING_LIVE_READBACK"
