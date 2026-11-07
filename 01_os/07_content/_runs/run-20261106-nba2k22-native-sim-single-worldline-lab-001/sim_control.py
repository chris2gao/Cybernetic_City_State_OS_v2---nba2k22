"""Offline SIM_THROUGH_DATE control model. No game transport is present."""
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Binding:
    save: str
    worldline: str
    build_sha256: str
    epoch: str
    season: str
    mode: str = "MyLEAGUE"


@dataclass(frozen=True)
class Game:
    game_id: str
    day: date
    home: str
    away: str
    final: bool = False
    simulated: bool = False
    box_complete: bool = False
    capture_unit: str = ""


@dataclass(frozen=True)
class Snapshot:
    binding: Binding
    day: date
    games: tuple[Game, ...]
    schedule_complete: bool
    phase: str = "REGULAR_SEASON"
    runtime: str = "IDLE"
    blocking_dates: tuple[date, ...] = ()


@dataclass(frozen=True)
class Plan:
    binding: Binding
    start: date
    target: date
    expected_game_ids: tuple[str, ...]
    max_polls: int

    @property
    def digest(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True, default=str).encode()).hexdigest()


def window(plan, snapshot):
    # This convention is for the offline contract. Native endpoint inclusivity is unverified.
    return {g.game_id: g for g in snapshot.games if plan.start <= g.day <= plan.target}


def preflight(plan, snapshot):
    if (snapshot.binding != plan.binding or plan.binding.mode != "MyLEAGUE"
            or not all((plan.binding.save, plan.binding.worldline, plan.binding.epoch, plan.binding.season))
            or len(plan.binding.build_sha256) != 64
            or any(char not in "0123456789abcdef" for char in plan.binding.build_sha256)):
        return "BINDING_MISMATCH"
    if snapshot.phase != "REGULAR_SEASON" or snapshot.runtime != "IDLE":
        return "UNSAFE_SCENE"
    if snapshot.day != plan.start or not (0 < (plan.target - plan.start).days <= 7 and 1 <= plan.max_polls <= 100):
        return "INVALID_WINDOW"
    if any(plan.start <= day <= plan.target for day in snapshot.blocking_dates):
        return "SEASON_EVENT"
    ids = [game.game_id for game in snapshot.games]
    if (not snapshot.schedule_complete or len(ids) != len(set(ids))
            or any(not all((g.game_id, g.home, g.away)) or g.home == g.away for g in snapshot.games)):
        return "SCHEDULE_UNKNOWN"
    pending = {g.game_id for g in window(plan, snapshot).values() if not g.final}
    if pending != set(plan.expected_game_ids) or len(pending) != len(plan.expected_game_ids):
        return "SCHEDULE_MISMATCH"
    if not pending:
        return "OFFDAY_ONLY"
    return "DRY_RUN_READY"


def assess(plan, before, after, previous_day):
    if (after.binding != plan.binding or after.phase != before.phase or not after.schedule_complete
            or after.runtime not in {"IDLE", "SIMULATING", "SAVING"}
            or after.day < previous_day or after.day > plan.target
            or any(plan.start <= day <= plan.target for day in after.blocking_dates)):
        return "UNKNOWN"
    old, new = window(plan, before), window(plan, after)
    if len({g.game_id for g in after.games}) != len(after.games) or old.keys() != new.keys():
        return "UNKNOWN"
    for key, g in old.items():
        observed = new[key]
        if (g.day, g.home, g.away) != (observed.day, observed.home, observed.away):
            return "UNKNOWN"
        if g.final and g != observed:
            return "UNKNOWN"
    before_final = {g.game_id for g in before.games if g.final}
    if any(g.final and g.game_id not in old and g.game_id not in before_final for g in after.games):
        return "UNKNOWN"
    if after.runtime != "IDLE" or after.day < plan.target:
        return "PENDING"
    completed = [new[key] for key in plan.expected_game_ids]
    units = {g.capture_unit for g in completed}
    if not all(g.final and g.simulated and g.box_complete and g.capture_unit for g in completed) or len(units) != 1:
        return "PARTIAL_RESULT"
    return "OFFLINE_COMPLETE"


def _record(stream, event, **fields):
    stream.write(json.dumps({"event": event, **fields}, sort_keys=True) + "\n")
    stream.flush()
    os.fsync(stream.fileno())


def run_fixture(plan, before, observations, journal_dir, *, fixture_grant_digest=None):
    """Feed scripted readback to the offline model, with an at-most-once journal.

    An exclusive journal is reserved for a save/worldline in this harness directory.
    Even a partial journal survives as a hold. Use a separate directory per test.
    The fixture grant is exclusively a simulation input, with zero live authority.
    """
    readiness = preflight(plan, before)
    if readiness != "DRY_RUN_READY" or fixture_grant_digest is None:
        return readiness
    if fixture_grant_digest != plan.digest:
        return "FIXTURE_GRANT_MISMATCH"
    identity = json.dumps([plan.binding.save, plan.binding.worldline], ensure_ascii=False)
    lock = Path(journal_dir) / (hashlib.sha256(identity.encode()).hexdigest() + ".jsonl")
    try:
        stream = lock.open("x", encoding="utf-8")
    except FileExistsError:
        return "HELD_NO_REPLAY"
    with stream:
        _record(stream, "OFFLINE_RESERVED", plan_digest=plan.digest, plan=asdict_json(plan))
        result = "UNKNOWN"
        previous_day = before.day
        try:
            frames = iter(observations)
            for tick in range(1, plan.max_polls + 1):
                observed = next(frames)
                result = assess(plan, before, observed, previous_day)
                _record(stream, "OBSERVED", tick=tick, day=observed.day.isoformat(), status=result)
                if result != "PENDING":
                    break
                previous_day = observed.day
            else:
                result = "TIMEOUT_UNKNOWN"
        except StopIteration:
            result = "TIMEOUT_UNKNOWN"
        except Exception as exc:
            _record(stream, "OBSERVATION_ERROR", error_type=type(exc).__name__)
            result = "UNKNOWN"
        _record(stream, "OFFLINE_STOPPED", status=result)
        return result


def asdict_json(plan):
    return json.loads(json.dumps(asdict(plan), default=str))
