"""Independent minimal probes transcribed from fixed V2 source flow.
NOT the original Gemini package or 54 pytest suite; no game/REA calls.
Source SHA: 5d7fdcc9ed277f0db79fa0e986483dfe6d00f06a.
"""
# GM-01 tax calculation (native_actions.py)
payroll = 137_606_000
tax_line = 136_606_000
native_output = max(0, payroll - tax_line)
real_2021_tax_1st_bracket = 1_000_000 * 1.50
assert native_output == 1_000_000
assert native_output != real_2021_tax_1st_bracket
print("V2-FINANCE: overage reported as tax bill")

# role_data_service.py category-only ACL omits player identity binding
allowed_for_player = {"own_attribute_and_growth", "own_training", "tendencies_and_badges"}
request = {"role": "PLAYER", "category": "own_attribute_and_growth", "object_id": "OTHER_PLAYER"}
assert request["category"] in allowed_for_player
print("V2-ACL: other-player query not denied by category ACL")

# revision.py mutates in-memory state before IO, even after file exception returns True
keys=set(); ledger=[]; key="same-key"
keys.add(key); ledger.append(key)
disk_write_success=False
reported_success=True
assert not disk_write_success and reported_success and key in keys
print("V2-DURABILITY: disk failure can still report True")

# readback_adapter.py L3 accepts string refs without evidence validation
getter_before_ref="BEFORE";getter_after_ref="AFTER";save_reload_ref="ANY_REF"
level="L3" if save_reload_ref else "L1"
assert getter_before_ref != getter_after_ref and level=="L3"
print("V2-READBACK: arbitrary string refs can appear L3")

# mechanism_registry.py grants verified based only on Enum passed to method
reported_outcome="CONFIRMED_CONTROLLED"
verified_in_game=(reported_outcome=="CONFIRMED_CONTROLLED")
assert verified_in_game
print("V2-MECHANISM: outcome argument alone can promote verified flag")
