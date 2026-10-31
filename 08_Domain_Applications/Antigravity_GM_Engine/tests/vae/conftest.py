import sys
from pathlib import Path

# Add 08_Domain_Applications/Antigravity_GM_Engine to sys.path so that 'src.vae' can be imported directly
gm_engine_root = Path(__file__).resolve().parents[2]
if str(gm_engine_root) not in sys.path:
    sys.path.insert(0, str(gm_engine_root))
