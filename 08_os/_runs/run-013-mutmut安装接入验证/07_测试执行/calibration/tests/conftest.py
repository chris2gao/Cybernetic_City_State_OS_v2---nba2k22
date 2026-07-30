from __future__ import annotations

from pathlib import Path
import sys


CALIBRATION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CALIBRATION_ROOT))
