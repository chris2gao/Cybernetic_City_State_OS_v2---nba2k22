"""Pure native coaching encoding. No process, database or write API imports."""
import json
from pathlib import Path

PROFILE = Path(__file__).resolve().parents[1] / "config/coach_tactics_profile.json"

def load_profile():
    return json.loads(PROFILE.read_text(encoding="utf-8"))

def integer(value, minimum, maximum, error="INVALID_NATIVE_COACHING_ENUM"):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(error)
    return value

def block_key(offset, size):
    return f"{offset:#x}:{size}"

def decode(raw, field):
    offset, size = field["offset"], field["storage_bytes"]
    part = raw[offset:offset + size]
    if len(part) != size:
        raise ValueError("INCOMPLETE_COACH_RECORD")
    return (int.from_bytes(part, "little") >> field["start_bit"]) & ((1 << field["width"]) - 1)

def validate_value(field, value, loaded_playbooks=(), *, target=False):
    integer(value, 0, (1 << field["width"]) - 1)
    if field.get('observation_raw_range') is not None:
        integer(value,*field['observation_raw_range'],error='OUTSIDE_OBSERVED_UI_RAW_RANGE')
    # A conservatively approved target range must not suppress genuine native
    # observations or prevent restoring a captured preimage outside that range.
    if target and field.get('raw_range') is not None:
        integer(value,*field['raw_range'],error='OUTSIDE_VERIFIED_RAW_RANGE')
    enum = field.get("enum")
    if isinstance(enum, dict) and str(value) not in enum:
        raise ValueError("INVALID_NATIVE_COACHING_ENUM")
    if enum == "LOADED_PLAYBOOKS" and value not in loaded_playbooks:
        raise ValueError("PLAYBOOK_NOT_LOADED")
    return value

def encode_changes(raw, changes, profile, loaded_playbooks=(), for_write=False):
    if len(raw) != 0x160 or not isinstance(changes, list) or not changes:
        raise ValueError("COACH_RECORD_AND_CHANGES_REQUIRED")
    groups, seen = {}, set()
    for change in changes:
        if not isinstance(change, dict) or set(change) != {"field", "before_raw", "after_raw"}:
            raise ValueError("EXACT_CHANGE_CONTRACT_REQUIRED")
        name = change["field"]
        if not isinstance(name, str) or name not in profile["fields"] or name in seen:
            raise ValueError("UNKNOWN_OR_DUPLICATE_FIELD")
        seen.add(name)
        field = profile["fields"][name]
        if field.get('gm_control_enabled') is False:
            raise ValueError('GM_CONTROL_DISABLED_'+name)
        if for_write and not field["writable"]:
            raise ValueError("FIELD_READ_ONLY")
        before = validate_value(field, change["before_raw"], loaded_playbooks)
        after = validate_value(field, change["after_raw"], loaded_playbooks, target=True)
        if before != decode(raw, field):
            raise ValueError("STALE_FIELD_VALUE")
        offset, size = field["offset"], field["storage_bytes"]
        key = block_key(offset, size)
        if key not in groups:
            old = int.from_bytes(raw[offset:offset + size], "little")
            groups[key] = dict(offset=offset, size=size, before=old, after=old, mask=0, fields=[])
        group = groups[key]
        mask = ((1 << field["width"]) - 1) << field["start_bit"]
        if mask >= 1 << (size * 8) or group["mask"] & mask:
            raise ValueError("INVALID_OR_OVERLAPPING_MASK")
        group["after"] = (group["after"] & ~mask) | (after << field["start_bit"])
        group["mask"] |= mask
        group["fields"].append(name)
    return [dict(offset=g["offset"], size=g["size"],
                 before=g["before"].to_bytes(g["size"], "little").hex(),
                 after=g["after"].to_bytes(g["size"], "little").hex(),
                 mask=g["mask"], fields=g["fields"]) for g in groups.values()]
