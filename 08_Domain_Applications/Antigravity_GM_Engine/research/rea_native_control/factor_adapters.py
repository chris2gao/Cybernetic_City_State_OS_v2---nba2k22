"""Typed offline preparation for player, coach, training and shared/event factors."""
from dataclasses import dataclass
from math import isfinite
import struct

from native_factor_slots import resolve_tendency_slot


@dataclass(frozen=True)
class PackedField:
    offset: int
    size: int
    start_bit: int
    width: int
    legal: tuple[int, ...]

    def __post_init__(self):
        if self.offset < 0 or self.size < 1 or self.width < 1 or self.start_bit < 0 or self.start_bit + self.width > self.size * 8:
            raise ValueError("PACKED_FIELD_OUTSIDE_STORAGE")
        if any(type(value) is not int or not 0 <= value < 1 << self.width for value in self.legal):
            raise ValueError("PACKED_DOMAIN_OUTSIDE_STORAGE")

    def read(self, image: bytes) -> int:
        if len(image) < self.offset + self.size:
            raise ValueError("PACKED_FIELD_IMAGE_SHORT")
        word = int.from_bytes(image[self.offset:self.offset + self.size], "little")
        return (word >> self.start_bit) & ((1 << self.width) - 1)

    def plan(self, image: bytes, expected: int, requested: int) -> bytes:
        if type(expected) is not int or type(requested) is not int or expected not in self.legal or requested not in self.legal:
            raise ValueError("PACKED_FIELD_LEGAL_DOMAIN_REQUIRED")
        if self.read(image) != expected:
            raise ValueError("PACKED_FIELD_CAS_MISMATCH")
        stop = self.offset + self.size
        word = int.from_bytes(image[self.offset:stop], "little")
        mask = ((1 << self.width) - 1) << self.start_bit
        return image[:self.offset] + ((word & ~mask) | (requested << self.start_bit)).to_bytes(self.size, "little") + image[stop:]

    def verify(self, before, after, expected, requested):
        if self.plan(before, expected, requested) != after:
            raise ValueError("PACKED_FIELD_READBACK_OR_NEIGHBOR_MISMATCH")
        return self.read(after)


@dataclass(frozen=True)
class AdapterContract:
    factor_id: str
    object_kind: str
    unit: str
    action: str | None
    endpoint: str
    qualification: str
    engineering_gap: str
    layout: dict | None = None


_EVENT_ENDPOINTS = {
    "HEALTH_MORALE": "HEALTH_EXPOSURE_DAYS_AND_RECOVERY_EVENT",
    "GLOBAL_CALENDAR": "INDEPENDENT_WORLDLINE_SAME_GAME_IDS",
    "GLOBAL_MODE": "MODE_CONSUMER_AND_INDEPENDENT_WORLDLINE",
    "TRADE_DRAFT": "TRADE_OR_DRAFT_OPPORTUNITY",
    "CONTRACT": "CONTRACT_OR_EXTENSION_OPPORTUNITY",
    "PROGRESSION": "NATIVE_PROGRESSION_SETTLEMENT",
}


def adapter_contract(factor):
    raw = factor.native
    if factor.category == "player_tendency":
        slot = resolve_tendency_slot(factor.factor_id)
        if raw["offset"] != hex(slot.offset) or raw["native_index"] != slot.index:
            raise ValueError(f"TENDENCY_PHYSICAL_CROSSWALK_MISMATCH: {factor.factor_id}")
        return AdapterContract(factor.factor_id, "PLAYER", "PLAYER_UID", "PLAYER_PATCH_TENDENCIES",
                               "SAME_GAME_BOX_AND_OPPONENT_EXPOSURE", factor.adapter_state,
                               "Live slot getter, neighbor bytes, and scene qualification required"
                               if not factor.live_qualified else "New operator grant required",
                               {"key": slot.native_key, "index": slot.index, "offset": slot.offset, "width": 8})
    if factor.category == "coach":
        layout = raw["physical_layout"]
        return AdapterContract(factor.factor_id, "COACH_GAMEPLAN", "TEAM",
                               "COACH_SET_KNOWN_CURRENT_SETTINGS" if layout else None, "TEAM_GAMEPLAN_AND_GAME_BOX",
                               factor.adapter_state, "Reconcile default and opponent-specific active projection"
                               if layout else "Locate Coach metadata and active consumer before exposing a writer", layout)
    if factor.category == "training":
        if factor.factor_id.startswith("TRAIN_DAILY/"):
            focus = factor.factor_id.split("/")[1].startswith("focus_")
            action = "TRAIN_TEAM_PATCH_FOCUS_RAW" if focus else "TRAIN_TEAM_PATCH_PROFILE_RAW"
        else:
            action = None
        return AdapterContract(factor.factor_id, raw["native_object"], raw["unit"], action,
                               "TRAINING_DAY_AND_SETTLEMENT_SNAPSHOTS", factor.adapter_state,
                               "Prove actual action, legal values and settlement with before/after skill and fatigue",
                               raw["physical_layout"])
    return AdapterContract(factor.factor_id, raw["native_object"], "WORLDLINE", None,
                           _EVENT_ENDPOINTS[factor.protocol], factor.adapter_state,
                           f"Locate exact setter and {factor.protocol} consumer before comparing independent worldlines",
                           {"cells": raw["physical_cells"]})


def coach_field(contract):
    if contract.object_kind != "COACH_GAMEPLAN" or contract.layout is None:
        raise ValueError("COACH_FIELD_LAYOUT_UNQUALIFIED")
    layout = contract.layout
    if layout.get("enum"):
        legal = tuple(map(int, layout["enum"]))
    elif isinstance(layout.get("range"), list) and len(layout["range"]) == 2:
        legal = tuple(range(layout["range"][0], layout["range"][1] + 1))
    else:
        legal = ()
    return PackedField(layout["coach_offset"], layout["storage_bytes"], layout["start_bit"], layout["width"], legal)


def prepare_coach_patch(contract, native_key, team_id, record, expected, requested):
    field = coach_field(contract)
    if type(team_id) is not int or not 0 <= team_id <= 29 or not native_key:
        raise ValueError("COACH_NATIVE_TEAM_AND_FIELD_REQUIRED")
    if contract.layout["gameplan_offset"] < 0:
        raise ValueError("COACH_ACTIVE_PROJECTION_REQUIRED")
    return ({"team_id": team_id, "values": {native_key: requested},
             "expected_before": {native_key: expected}}, field.plan(record, expected, requested))


def prepare_training_patch(contract, team_id, date, record: bytes, expected, requested):
    """Compose exact existing native training action parameters for fixture qualification."""
    if contract.object_kind != "TEAM_DAILY_TRAINING" or not contract.action or len(record) != 56:
        raise ValueError("TRAINING_DAILY_RECORD_OR_ACTION_REQUIRED")
    offset = contract.layout["record_offset"]
    width = contract.layout["byte_width"]
    if width == 4:
        if type(expected) not in (int, float) or type(requested) not in (int, float) or not all(map(isfinite, (expected, requested))):
            raise ValueError("TRAINING_FOCUS_REQUIRES_FINITE_RAW_VALUE")
        fmt = "<f"
    else:
        if type(expected) is not int or type(requested) is not int or not 0 <= expected <= 255 or not 0 <= requested <= 255:
            raise ValueError("TRAINING_PROFILE_REQUIRES_RAW_BYTE")
        fmt = "<B"
    if record[offset:offset + width] != struct.pack(fmt, expected):
        raise ValueError("TRAINING_DAILY_CAS_MISMATCH")
    after = record[:offset] + struct.pack(fmt, requested) + record[offset + width:]
    parameters = {"team_id": team_id, "date": date}
    if width == 4:
        parameters["focus_values_raw"] = list(struct.unpack_from("<3f", after))
        if not all(map(isfinite, parameters["focus_values_raw"])):
            raise ValueError("TRAINING_NEIGHBOR_FOCUS_NOT_FINITE")
    else:
        parameters["profile_values_raw"] = list(after[12:15])
        parameters["subfocus_points_raw"] = list(after[15:53])
    return parameters, after


def read_shared_setting(contract, root_rva, offset, raw):
    """Decode the registered raw cell without claiming an effective setting or setter."""
    if contract.unit != "WORLDLINE" or len(raw) != 4:
        raise ValueError("EXACT_WORLD_SETTING_WORD_REQUIRED")
    layouts = {(row["root_rva"], row["offset"], row["type"]) for row in contract.layout["cells"]}
    encodings = {kind for rva, member, kind in layouts if (rva, member) == (root_rva, offset)}
    if len(encodings) != 1:
        raise ValueError("WORLD_SETTING_PHYSICAL_CELL_NOT_UNIQUE")
    encoding, = encodings
    value = struct.unpack("<I" if encoding == "uint32" else "<f", raw)[0]
    return {"value": value if isfinite(value) else None, "raw_word": int.from_bytes(raw, "little"),
            "encoding": encoding, "status": "OBSERVED_RAW_WORD_ONLY"}
