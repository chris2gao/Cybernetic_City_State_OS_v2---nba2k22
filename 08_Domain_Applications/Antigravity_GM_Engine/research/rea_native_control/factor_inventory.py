"""Load the fixed VAE study inputs without promoting plan rows to native evidence."""
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path


EXPERIMENT_SAVE_SLOT = "MyLEAGUE0005"


@dataclass(frozen=True)
class FactorRecord:
    factor_id: str
    category: str
    protocol: str
    source_rows: tuple[str, ...]
    adapter_state: str
    reference_slots: tuple[str, ...]
    native: dict

    @property
    def live_qualified(self):
        return self.adapter_state == "S4_BOUNDED_LIVE_VERIFIED"


@dataclass(frozen=True)
class StudyInputs:
    baseline: dict
    factors: dict[str, FactorRecord]
    protocols: dict
    fixtures: dict
    players: tuple
    reference: dict

    @classmethod
    def load(cls, directory: Path):
        def read_json(name):
            return json.loads((directory / name).read_bytes())

        def read_csv(name):
            with (directory / name).open(encoding="utf-8-sig", newline="") as stream:
                return tuple(csv.DictReader(stream))

        baseline = read_json("0005_baseline_manifest.json")
        if baseline["loaded_slot"] != EXPERIMENT_SAVE_SLOT:
            raise ValueError("BASELINE_EXPERIMENT_SAVE_SLOT_MISMATCH")
        for name, digest in baseline["output_sha256"].items():
            if sha256((directory / name).read_bytes()).hexdigest() != digest:
                raise ValueError(f"BASELINE_EXPORT_HASH_MISMATCH: {name}")
        catalog = read_json("full_factor_registry.json")
        reference = read_json("experiment_assignment_matrix.json")
        protocols = {row["protocol_id"]: row for row in read_json("category_study_protocols.json")["protocols"]}
        if reference["status"] != "PLANNING_ONLY" or catalog["coverage"]["authorized_writes"] != 0:
            raise ValueError("REFERENCE_ASSIGNMENT_CANNOT_AUTHORIZE_NATIVE")
        raw_fixtures = read_csv("remaining_schedule.csv")
        fixtures = {int(row["game_id"]): row for row in raw_fixtures}
        if len(fixtures) != len(raw_fixtures) or set(fixtures) != {int(key) for key in reference["game_index"]}:
            raise ValueError("REFERENCE_GAME_ID_SET_MISMATCH")
        slots = defaultdict(list)
        for window in reference["windows"]:
            for game_id in window["real_game_ids"]:
                fixture = fixtures[game_id]
                if fixture["phase"] != "REGULAR_SEASON" or fixture["scheduled_state"] != "PENDING":
                    raise ValueError("REFERENCE_PLAN_INCLUDES_UNQUALIFIED_GAME")
            for factor_id in window["fields"]:
                slots[factor_id].append(window["window_id"])
        factors = {}
        source_rows = []
        for raw in catalog["factors"]:
            factor_id = raw["factor_id"]
            protocol = raw["protocol"]
            if factor_id in factors or protocol not in protocols:
                raise ValueError("DUPLICATE_FACTOR_OR_UNKNOWN_PROTOCOL")
            source_rows.extend(raw["sources"])
            factors[factor_id] = FactorRecord(factor_id, raw["category"], protocol, tuple(raw["sources"]),
                                              raw["setter"]["status"], tuple(slots.pop(factor_id, ())), raw)
        if slots:
            raise ValueError("REFERENCE_PLAN_CONTAINS_UNKNOWN_FACTOR")
        event_factors = [row["factor_id"] for row in reference["event_reservations"]]
        if (len(event_factors) != len(set(event_factors))
                or set(event_factors) != {key for key, row in factors.items() if not row.reference_slots}):
            raise ValueError("REFERENCE_EVENT_COVERAGE_NOT_CONSERVED")
        by_category = dict(Counter(factor.category for factor in factors.values()))
        if by_category != catalog["coverage"]["categorization"]:
            raise ValueError("FACTOR_CATEGORY_DENOMINATOR_MISMATCH")
        stage = [row for row in source_rows if row.startswith(("TENDENCY_NATIVE_", "COACH_DEFAULT_", "WORLD_REG_"))]
        projections = [row for row in source_rows if row.startswith("COACH_PROJECTION/")]
        if (len(stage) != len(set(stage)) or len(stage) != catalog["coverage"]["source_stage02_rows"]
                or len(projections) != len(set(projections))
                or len(projections) != catalog["coverage"]["coach_projection_rows"]):
            raise ValueError("SOURCE_CROSSWALK_NOT_ONE_TO_ONE")
        players = read_csv("eligible_player_pool.csv")
        if (sum(row["phase"] == "REGULAR_SEASON" for row in fixtures.values()) != baseline["remaining_regular_fixture_ids"]
                or sum(row["phase"] == "SCHEDULED_SPECIAL" for row in fixtures.values()) != baseline["remaining_special_fixture_ids"]
                or len({row["native_team_id"] for row in players}) != baseline["teams"]
                or len({row["native_uid"] for row in players}) != baseline["unique_uids"]
                or sum(row["eligible_now"] == "True" for row in players) != baseline["eligible_uids"]):
            raise ValueError("PLAYER_POOL_COVERAGE_MISMATCH")
        return cls(baseline, factors, protocols, fixtures, players, reference)

    def crosswalk(self):
        return {
            key: {
                "source_rows": record.source_rows,
                "protocol": record.protocol,
                "adapter_state": record.adapter_state,
                "reference_slots": record.reference_slots,
                "experiment_state": "REFERENCE_SCHEDULED" if record.reference_slots else "EVENT_SOURCE_REQUIRED",
                "live_writer_qualified": record.live_qualified,
                "execution_authorized": False,
                "needs_fresh_qualification": not record.live_qualified,
            }
            for key, record in self.factors.items()
        }
