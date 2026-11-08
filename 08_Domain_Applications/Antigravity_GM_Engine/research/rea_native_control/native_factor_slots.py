"""Exact PLAYER tendency storage and staged, independently checked setter contracts."""
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
from types import MappingProxyType

from contracts import BUILD
from player_fields import load_fields

TENDENCY_START = 0x458
TENDENCY_WIDTH = 99


@dataclass(frozen=True)
class PlayerTendencySlot:
    factor_id: str
    native_key: str
    index: int
    offset: int
    minimum: int
    maximum: int
    named: bool

    @property
    def ordinal(self):
        return self.offset - TENDENCY_START + 1

    @property
    def slot_id(self):
        return self.native_key if self.named else f"UNKNOWN_RAW_BYTE_{self.ordinal:03d}"

    def decode(self, neighbor_bytes: bytes) -> int:
        if len(neighbor_bytes) != TENDENCY_WIDTH:
            raise ValueError("PLAYER_TENDENCY_NEIGHBORHOOD_WIDTH_MISMATCH")
        return neighbor_bytes[self.ordinal - 1]

    def expected_image(self, before: bytes, expected_before: int, requested: int) -> bytes:
        if (type(expected_before) is not int or type(requested) is not int
                or not self.minimum <= expected_before <= self.maximum
                or not self.minimum <= requested <= self.maximum):
            raise ValueError("PLAYER_TENDENCY_VALUE_OUTSIDE_DOMAIN")
        if self.decode(before) != expected_before:
            raise ValueError("PLAYER_TENDENCY_CAS_MISMATCH")
        index = self.ordinal - 1
        return before[:index] + bytes([requested]) + before[index + 1:]

    def verify_readback(self, before: bytes, after: bytes, expected_before: int, requested: int, getter_after: int):
        if after != self.expected_image(before, expected_before, requested) or getter_after != requested:
            raise ValueError("PLAYER_TENDENCY_READBACK_OR_NEIGHBOR_MISMATCH")
        return "NOOP" if expected_before == requested else "VERIFIED"


@lru_cache(maxsize=1)
def tendency_slots():
    descriptors = load_fields()["families"]["tendencies"]
    slots = {}
    indices = set()
    for native_key, row in descriptors.items():
        ordinal = row["offset"] - TENDENCY_START + 1
        factor_id = f"TENDENCY_NATIVE_{ordinal:03d}"
        slot = PlayerTendencySlot(factor_id, native_key, row["native_index"], row["offset"],
                                  row["minimum"], row["maximum"], row["name_known"])
        if (factor_id in slots or slot.index in indices or not 1 <= ordinal <= TENDENCY_WIDTH
                or row["encoding"] != "NATIVE_UI_INTEGER_TENDENCY"
                or row["expected_raw_formula"] != "value" or not 0 <= slot.minimum <= slot.maximum <= 255):
            raise ValueError("TENDENCY_CATALOG_STORAGE_CONFLICT")
        slots[factor_id] = slot
        indices.add(slot.index)
    if len(slots) != TENDENCY_WIDTH or sum(slot.named for slot in slots.values()) != 48:
        raise ValueError("TENDENCY_CATALOG_COVERAGE_MISMATCH")
    return MappingProxyType(slots)


def resolve_tendency_slot(key: str, *, build_sha256: str = BUILD):
    if build_sha256 != BUILD:
        raise ValueError("TENDENCY_BUILD_MISMATCH")
    found = [slot for slot in tendency_slots().values() if key in (slot.factor_id, slot.slot_id, slot.native_key)]
    if len(found) != 1:
        raise ValueError(f"UNKNOWN_OR_AMBIGUOUS_TENDENCY_SLOT: {key}")
    return found[0]


# Qualification is independent of setter availability, research assignment, and approval.
_S4_LIVE_QUALIFIED = frozenset({"TENDENCY_NATIVE_001"})


def require_s4_live_tendency(native_key: str):
    slot = resolve_tendency_slot(native_key)
    if slot.factor_id not in _S4_LIVE_QUALIFIED or native_key != slot.native_key:
        raise ValueError("S4_TENDENCY_SLOT_NOT_LIVE_QUALIFIED")
    return slot


def _sha256_hex(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


@dataclass(frozen=True)
class AcceptedTendencyQualifications:
    """Validated, build-scoped field evidence. A separate window approval authorizes use."""
    sha256: str
    factor_ids: frozenset[str]

    @classmethod
    def load(cls, raw: bytes, approved_sha256: str):
        if sha256(raw).hexdigest() != approved_sha256:
            raise PermissionError("ACCEPTED_QUALIFICATION_PIN_MISMATCH")
        source = json.loads(raw)
        if (source["schema"] != "nba2k22.vae.accepted_tendency_qualifications.v1"
                or source["build_sha256"] != BUILD or not source["slots"]):
            raise ValueError("ACCEPTED_QUALIFICATION_BUILD_OR_SCHEMA_MISMATCH")
        factors = set()
        for evidence in source["slots"]:
            slot = resolve_tendency_slot(evidence["factor_id"])
            before, after = evidence["before"], evidence["after"]
            identity = ("profile_build_sha256", "factor_id", "native_key", "index", "offset", "width_bits",
                        "legal_domain", "save_id", "loaded_filename", "worldline_id", "binding_sha256",
                        "epoch", "today", "minutes", "uid", "team_id")
            if (slot.factor_id in factors or evidence["mode"] != "LIVE" or evidence["outcome"] != "CONFIRMED_APPLIED"
                    or evidence["factor_id"] != slot.factor_id or not evidence["independent_review_ref"]
                    or not all(_sha256_hex(evidence[key]) for key in ("native_plan_sha256", "native_evidence_sha256",
                                                                     "independent_readback_sha256"))
                    or any(before[key] != after[key] for key in identity)
                    or any(row["status"] != "READ_ONLY_SLOT_OBSERVED" or row["write_qualified"] is not False
                           for row in (before, after))
                    or (before["profile_build_sha256"], before["factor_id"], before["native_key"],
                        before["index"], before["offset"], before["width_bits"], before["legal_domain"])
                       != (BUILD, slot.factor_id, slot.native_key, slot.index, slot.offset, 8, [slot.minimum, slot.maximum])
                    or before["loaded_filename"] != "MyLEAGUE0005" or not before["save_id"] or not before["worldline_id"]
                    or not _sha256_hex(before["binding_sha256"])
                    or type(before["epoch"]["pid"]) is not int or before["epoch"]["pid"] <= 0
                    or type(before["epoch"]["creation_filetime"]) is not int or before["epoch"]["creation_filetime"] <= 0
                    or type(before["uid"]) is not int or not 1 <= before["uid"] <= 65535
                    or type(before["team_id"]) is not int or not 0 <= before["team_id"] <= 29):
                raise ValueError("ACCEPTED_QUALIFICATION_EVIDENCE_SCOPE_MISMATCH")
            old, new = (bytes.fromhex(row["neighborhood_hex"]) for row in (before, after))
            if (sha256(old).hexdigest() != before["neighborhood_sha256"]
                    or sha256(new).hexdigest() != after["neighborhood_sha256"]
                    or abs(after["raw_value"] - before["raw_value"]) != 1
                    or slot.verify_readback(old, new, before["raw_value"], after["raw_value"], after["raw_value"]) != "VERIFIED"):
                raise ValueError("ACCEPTED_QUALIFICATION_NEIGHBORHOOD_MISMATCH")
            factors.add(slot.factor_id)
        return cls(approved_sha256, frozenset(factors))
