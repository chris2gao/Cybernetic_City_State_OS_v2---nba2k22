"""Independent minimal reproduction of fixed candidate's source control flow.

IMPORTANT: This is a source-equivalent counterexample script, NOT the original
Gemini package or its 21-test pytest suite. Original source:
GitHub chris2gao/Cybernetic_City_State_OS_v2---nba2k22
@c2d9caae388bac3ae5e586c69ee0bd2116ba473b
src/vae/{contracts,preflight,reader_adapter,revision,evaluator}.py.
No game/save/REA access.
"""
from dataclasses import dataclass

@dataclass
class Observation:
    save_id: str
    engine_path: str
    trial_id: str = "trial-01"
    side: str = "USER"
    controller_assigned: bool = True
    played_normalize_on: bool = False
    sim_normalize_on: bool = False
    played_quarter_minutes: int = 12
    sim_quarter_minutes: int = 12
    base_source_ref: str = "STATIC_SOURCE"

    def is_comparable_with(self, other):
        for name in ("side", "controller_assigned", "played_normalize_on",
                     "sim_normalize_on", "played_quarter_minutes",
                     "sim_quarter_minutes", "base_source_ref"):
            if getattr(self, name) != getattr(other, name):
                return False, name + " mismatch"
        return True, "Comparable"

before = Observation("SAVE_A", "3D_PLAYED")
after = Observation("SAVE_B", "CALENDAR_SIM", trial_id="unrelated_trial")
assert before.save_id != after.save_id and before.engine_path != after.engine_path
assert before.is_comparable_with(after)[0] is True
print("REPRO_R06: cross-save/cross-path/cross-trial inputs accepted as comparable")

source_tier = "STATIC_DEFAULT"
raw_value = 50
restore_plan = {"rollback_value": raw_value}
authorization_ref = "AUTH_OFFLINE_DEV_DRYRUN"
preflight_ready = (raw_value is not None and bool(restore_plan)
                  and "rollback_value" in restore_plan and bool(authorization_ref))
assert source_tier == "STATIC_DEFAULT" and preflight_ready
print("REPRO_R03: static default plus arbitrary nonempty auth meets READY checks")

class MemoryLedger:
    def __init__(self):
        self.committed_keys = set()
        self.ledger = []
    def commit_append(self, key):
        if key in self.committed_keys:
            return False
        self.committed_keys.add(key)
        self.ledger.append(key)
        return True

a = MemoryLedger()
assert a.commit_append("same-key")
b = MemoryLedger()
assert b.ledger == [] and b.commit_append("same-key")
print("REPRO_R08: fresh instance loses ledger and duplicate protection")

sample_size = 5
delta = -0.021
assert sample_size >= 5 and delta < -0.02
print("REPRO_R07: hard-coded threshold leads to CONFIRMED branch without controls")
