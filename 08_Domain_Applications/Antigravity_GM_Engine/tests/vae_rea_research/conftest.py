import os
import sys

# Ensure 08_Domain_Applications/Antigravity_GM_Engine is in sys.path
engine_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if engine_root not in sys.path:
    sys.path.insert(0, engine_root)
