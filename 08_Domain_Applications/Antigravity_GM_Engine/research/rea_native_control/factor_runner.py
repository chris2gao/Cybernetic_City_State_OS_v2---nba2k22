"""Nonresident staged VAE runner with a production authority boundary and fixture port."""
from dataclasses import dataclass
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

from contracts import BUILD
from factor_inventory import EXPERIMENT_SAVE_SLOT
from native_factor_slots import require_s4_live_tendency, resolve_tendency_slot


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def record_once(path: Path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())


@dataclass(frozen=True)
class LiveEnvelope:
    """The launch boundary supplies the independently trusted Human pin."""
    raw: bytes
    approved_sha256: str

    def verify(self, plan, binding, operations, windows, now=None):
        now = now or datetime.now(timezone.utc)
        if hashlib.sha256(self.raw).hexdigest() != self.approved_sha256:
            raise ValueError("HUMAN_ENVELOPE_PIN_MISMATCH")
        source = json.loads(self.raw)
        if (source["schema"] != "nba2k22.vae.live_envelope.v1" or source["revoked"] is not False
                or not source["human_decision_ref"] or source["build_sha256"] != BUILD
                or source["binding"] != binding or source["plan_digest"] != digest(plan)
                or source["operation_digests"] != [digest(item) for item in operations]
                or source["calendar_digests"] != [digest(item) for item in windows]
                or type(source["max_setters"]) is not int or not len(operations) <= source["max_setters"] <= 168
                or type(source["max_calendar"]) is not int or not len(windows) <= source["max_calendar"] <= 56
                or not datetime.fromisoformat(source["valid_from"]) <= now < datetime.fromisoformat(source["expires_at"])):
            raise ValueError("HUMAN_ENVELOPE_SCOPE_OR_TIME_MISMATCH")
        if (binding.get("loaded_filename") != EXPERIMENT_SAVE_SLOT or not binding.get("binding_sha256")
                or binding.get("worldline_id") != plan["worldline_id"]
                or binding.get("build_sha256") != BUILD or type(binding.get("pid")) is not int
                or not isinstance(binding.get("epoch"), dict) or binding["epoch"].get("pid") != binding["pid"]
                or plan["stop_exclusive"] > binding.get("last_regular_date", "")):
            raise ValueError("LIVE_DISPOSABLE_SAVE_AND_EPOCH_REQUIRED")
        return source


def window_operations(plan):
    return [{"factor_id": item["factor_id"], "team_id": item["team_id"], "uid": item["uid"],
             "expected_before": item["baseline"], "target": item["target"],
             "live_writer_qualified": item["live_writer_qualified"]}
            for _, item in sorted(plan["teams"].items(), key=lambda row: int(row[0])) if item["arm"] in ("H", "L")]


class WindowDelegation:
    """Derive exact S4 sub-batches from the same pinned Human window envelope."""
    def __init__(self, envelope, plan, binding, journal):
        self.envelope = envelope
        self.plan = plan
        self.binding = binding
        self.journal = journal
        self._operations = window_operations(plan)
        self._active = None
        self._verified = None

    def approval(self):
        if (self.journal / "REVOKED").exists():
            raise PermissionError("HUMAN_ENVELOPE_REVOKED")
        return self.envelope.verify(self.plan, self.binding, self._operations, self.plan["subwindows"])

    def bind(self, operation):
        self.approval()
        if operation not in self._operations or not operation["live_writer_qualified"]:
            raise PermissionError("SETTER_NOT_IN_QUALIFIED_WINDOW")
        self._active = dict(operation)
        self._verified = None

    def role_manifest(self):
        root = self.approval()
        if self._active is None:
            raise PermissionError("NO_ACTIVE_SETTER_SUBPLAN")
        op = self._active
        slot = self.slot_for(op)
        return {"save_id": self.binding["save_id"], "worldline_id": self.binding["worldline_id"],
                "bound_database_file": self.binding["bound_database_file"], "binding_sha256": self.binding["binding_sha256"],
                "human_authorization_ref": root["human_decision_ref"], "authorized_at": root["valid_from"],
                "expires_at": root["expires_at"], "action_id": "PLAYER_PATCH_TENDENCIES", "field_id": slot.native_key,
                "player_ids": [op["uid"]],
                "roles": [{"role_type": "GM", "team_id": op["team_id"], "actor_uid": f"vae-factor-{op['team_id']}"}]}

    def slot_for(self, operation):
        return require_s4_live_tendency(resolve_tendency_slot(operation["factor_id"]).native_key)

    @property
    def epoch(self):
        return self.binding["epoch"]

    def check_scene(self, scene, filename, binding_sha256):
        self.approval()
        progress = scene["game_progress"]
        if (filename != self.binding["loaded_filename"] or binding_sha256 != self.binding["binding_sha256"]
                or scene["epoch"] != self.epoch or progress["today_native_iso_date"] != self.plan["start"]
                or progress["today_minutes_since_midnight_raw"] != 0 or progress["period_raw"] != 29
                or progress["mode_raw"] != 1):
            raise ValueError("LIVE_WORLDLINE_EPOCH_OR_SCENE_CHANGED")

    def verify_setter(self, cycle, plan_digest, batch, context):
        manifest = self.role_manifest()
        op = self._active
        if len(batch.intents) != 1 or context["epoch"] != self.epoch:
            raise ValueError("EXACT_SINGLE_TEAM_SUBBATCH_REQUIRED")
        item, = batch.intents
        if (item.action_id, item.team_id, item.player_id, item.field_id, item.expected_before, item.value) != (
                manifest["action_id"], op["team_id"], op["uid"], manifest["field_id"], op["expected_before"], op["target"]):
            raise ValueError("SEALED_SUBBATCH_DIFFERS_FROM_HUMAN_SCOPE")
        self._verified = (cycle, plan_digest, digest(op))
        return manifest["human_authorization_ref"]

    def reserve_setter(self, cycle, plan_digest):
        self.approval()
        if self._verified != (cycle, plan_digest, digest(self._active)):
            raise PermissionError("EXACT_SUBBATCH_VERIFICATION_REQUIRED")
        record_once(self.journal / f"native-subplan-{digest(self.plan)[:20]}-{self._verified[2]}.json",
                    {"cycle": cycle, "plan_digest": plan_digest})


@dataclass(frozen=True)
class QualificationEnvelope:
    raw: bytes
    approved_sha256: str

    def verify(self, binding, operations):
        if hashlib.sha256(self.raw).hexdigest() != self.approved_sha256:
            raise PermissionError("QUALIFICATION_HUMAN_PIN_MISMATCH")
        approval = json.loads(self.raw)
        now = datetime.now(timezone.utc)
        if (approval["schema"] != "nba2k22.vae.write_qualification.v1" or approval["revoked"] is not False
                or not approval["human_decision_ref"] or approval["binding"] != binding
                or approval["operation_digests"] != [digest(op) for op in operations]
                or type(approval["maximum_setters"]) is not int or approval["maximum_setters"] != len(operations)
                or not 1 <= len(operations) <= 3
                or type(approval["maximum_calendar"]) is not int or approval["maximum_calendar"] != 0
                or not datetime.fromisoformat(approval["valid_from"]) <= now < datetime.fromisoformat(approval["expires_at"])
                or binding["loaded_filename"] != EXPERIMENT_SAVE_SLOT or binding["build_sha256"] != BUILD
                or not binding.get("loaded_slot_attestation_ref")
                or type(binding["pid"]) is not int or binding["pid"] != binding["epoch"]["pid"]
                or len({op["factor_id"] for op in operations}) != len(operations)
                or len({op["uid"] for op in operations}) != len(operations)):
            raise PermissionError("QUALIFICATION_HUMAN_SCOPE_OR_TIME_MISMATCH")
        return approval


class QualificationDelegation(WindowDelegation):
    """One-to-three exact raw slots with no calendar or research qualification promotion."""
    def __init__(self, envelope, binding, operations, journal):
        self.envelope = envelope
        self.binding = binding
        self._operations = tuple(operations)
        self.journal = journal
        self.plan = {"binding": binding, "operations": self._operations}
        self._active = None
        self._verified = None

    def approval(self):
        if (self.journal / "REVOKED").exists():
            raise PermissionError("HUMAN_ENVELOPE_REVOKED")
        return self.envelope.verify(self.binding, self._operations)

    def slot_for(self, operation):
        if operation not in self._operations:
            raise PermissionError("QUALIFICATION_OPERATION_OUTSIDE_GRANT")
        slot = resolve_tendency_slot(operation["factor_id"])
        before = operation["before"]
        image = bytes.fromhex(before["neighborhood_hex"])
        if (type(operation["team_id"]) is not int or not 0 <= operation["team_id"] <= 29
                or type(operation["uid"]) is not int or not 1 <= operation["uid"] <= 65535
                or before["status"] != "READ_ONLY_SLOT_OBSERVED" or before["write_qualified"] is not False
                or any(before[key] != self.binding[key] for key in ("save_id", "worldline_id", "loaded_filename",
                                                                   "binding_sha256", "epoch", "today", "minutes"))
                or (before["factor_id"], before["uid"], before["team_id"], before["raw_value"])
                   != (slot.factor_id, operation["uid"], operation["team_id"], operation["expected_before"])
                or before["profile_build_sha256"] != BUILD
                or (before["native_key"], before["index"], before["offset"], before["width_bits"], before["legal_domain"])
                   != (slot.native_key, slot.index, slot.offset, 8, [slot.minimum, slot.maximum])
                or hashlib.sha256(image).hexdigest() != before["neighborhood_sha256"]
                or slot.expected_image(image, operation["expected_before"], operation["target"]) == image
                or abs(operation["target"] - operation["expected_before"]) != 1):
            raise ValueError("QUALIFICATION_FROZEN_NEIGHBORHOOD_OR_SCOPE_MISMATCH")
        return slot

    def bind(self, operation):
        self.approval()
        self.slot_for(operation)
        self._active = dict(operation)
        self._verified = None

    def check_scene(self, scene, filename, binding_sha256):
        self.approval()
        progress = scene["game_progress"]
        if (filename != self.binding["loaded_filename"] or binding_sha256 != self.binding["binding_sha256"]
                or scene["epoch"] != self.epoch or progress["mode_raw"] != 1 or progress["period_raw"] != 29
                or progress["today_native_iso_date"] != self.binding["today"]
                or progress["today_minutes_since_midnight_raw"] != self.binding["minutes"]):
            raise ValueError("QUALIFICATION_WORLDLINE_EPOCH_OR_SCENE_CHANGED")

    def approved_neighborhood(self, field):
        self.approval()
        if self._active is None or self.slot_for(self._active).native_key != field:
            raise PermissionError("QUALIFICATION_FIELD_NOT_ACTIVE")
        return self._active["before"]["neighborhood_hex"]

    def _check_disk(self):
        save = Path(self.binding["disk_save"]).resolve(strict=True)
        backup = Path(self.binding["cold_backup"]).resolve(strict=True)
        if (save.name != EXPERIMENT_SAVE_SLOT or backup.name != "MyLEAGUE0003"
                or save.parent != backup.parent or save.samefile(backup)):
            raise ValueError("QUALIFICATION_DISPOSABLE_AND_BACKUP_REQUIRED")
        for path, key in ((save, "disk_sha256"), (backup, "cold_backup_sha256")):
            with path.open("rb") as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != self.binding[key]:
                    raise ValueError("QUALIFICATION_SAVE_FINGERPRINT_CHANGED")

    def check_readback(self, host, *, after):
        self.approval()
        self._check_lock_storage(host)
        if not (self._claim / "plan.json").is_file():
            raise PermissionError("QUALIFICATION_REQUIRES_PERSISTED_GRANT_CLAIM")
        op = self._active
        slot = self.slot_for(op)
        observed = host.read_factor_qualification_snapshot(
            pid=self.binding["pid"], epoch=self.epoch, team_id=op["team_id"], uid=op["uid"],
            field=slot.native_key, binding_sha256=self.binding["binding_sha256"])
        expected = dict(op["before"])
        if after:
            image = slot.expected_image(bytes.fromhex(expected["neighborhood_hex"]), op["expected_before"], op["target"])
            expected.update(raw_value=op["target"], neighborhood_hex=image.hex(),
                            neighborhood_sha256=hashlib.sha256(image).hexdigest())
        if observed != expected:
            reason = ("QUALIFICATION_INDEPENDENT_NEIGHBORHOOD_MISMATCH" if after
                      else "LIVE_CAS_CHANGED_SINCE_APPROVAL: qualification neighborhood differs")
            raise RuntimeError(reason)
        self._check_disk()
        return observed

    def _check_lock_storage(self, host):
        if (Path(self.binding["outbox_db"]).resolve() != host.outbox_db.resolve()
                or Path(self.binding["journal_root"]).resolve() != self.journal.resolve()):
            raise PermissionError("QUALIFICATION_LOCK_STORAGE_MISMATCH")

    @property
    def _claim(self):
        return self.journal / f"qualification-{self.envelope.approved_sha256}"

    def run(self, host):
        if host.research_delegation is not self or host.state.get("is_offline_mock") or host.state.get("is_mock"):
            raise PermissionError("QUALIFICATION_REQUIRES_BOUND_NATIVE_HOST")
        self.approval()
        self._check_lock_storage(host)
        for operation in self._operations:
            self.slot_for(operation)
        self._check_disk()
        self.journal.mkdir(parents=True, exist_ok=True)
        claim = self._claim
        claim.mkdir()
        record_once(claim / "plan.json", self.plan)
        receipts = []
        try:
            for operation in self._operations:
                self.bind(operation)
                self.check_readback(host, after=False)
            for index, operation in enumerate(self._operations):
                key = f"vae-qualification-{self.envelope.approved_sha256[:20]}-{index}"
                receipt = _execute_host_setter(host, key, operation, self.binding)
                record_once(claim / f"receipt-{index}.json", receipt)
                receipts.append(receipt)
                if receipt["status"] != "APPLIED":
                    break
        except Exception as error:
            record_once(claim / "stop.json", {"status": "STOPPED_RECONCILIATION_REQUIRED",
                                              "exception_type": type(error).__name__,
                                              "completed_receipts": len(receipts)})
            raise
        return {"status": ("QUALIFICATION_EVIDENCE_RECORDED"
                           if len(receipts) == len(self._operations) and receipts[-1]["status"] == "APPLIED"
                           else "QUALIFICATION_STOPPED"), "receipts": receipts, "calendar_calls": 0}


class NativeCalendarPort:
    """Use the archived calendar primitive and the shared Outbox for exact approved plans."""
    def __init__(self, delegation, native_plans, outbox_db, runtime):
        self.delegation = delegation
        self.plans = native_plans
        self.outbox = outbox_db
        self.runtime = runtime

    def verify_calendar(self, plan):
        from tools.test_only_calendar import calendar_cli
        if type(self.delegation) is not WindowDelegation:
            raise PermissionError("NATIVE_CALENDAR_REQUIRES_WINDOW_AUTHORITY")
        source = self.delegation.approval()
        binding = self.delegation.binding
        pin = calendar_cli.digest(plan)
        if (pin not in source["native_calendar_digests"] or plan["epoch"] != self.delegation.epoch
                or any(plan[key] != binding[key] for key in ("save_id", "worldline_id", "loaded_filename", "binding_sha256"))
                or plan["authorization_scope"] != source["human_decision_ref"]):
            raise PermissionError("NATIVE_CALENDAR_SUBPLAN_OUTSIDE_HUMAN_SCOPE")
        return {"expires_at": source["expires_at"], "human_decision_ref": source["human_decision_ref"]}

    def reserve_calendar(self, plan):
        from tools.test_only_calendar import calendar_cli
        self.verify_calendar(plan)
        pin = calendar_cli.digest(plan)
        record_once(self.delegation.journal / f"native-calendar-{pin}.json", {"plan_digest": pin})

    def __call__(self, key, window):
        from tools.test_only_calendar import calendar_cli
        plan = self.plans[digest(window)]
        finals = [row["id"] for row in plan["games"] if row["day"] < plan["stop_exclusive"]]
        pending = [row["id"] for row in plan["games"] if row["day"] == plan["stop_exclusive"]]
        if (plan["start"] != window["start"] or plan["stop_exclusive"] != window["stop_exclusive"]
                or sorted(finals) != sorted(window["planned_finals"])
                or sorted(pending) != sorted(window["next_day_controls"])):
            raise ValueError("NATIVE_CALENDAR_DIFFERS_FROM_EXPERIMENT_WINDOW")
        self.verify_calendar(plan)
        args = SimpleNamespace(runtime=self.runtime / key, node=None, rea=None, outbox=self.outbox,
                               execute_once=True, approval=None, approved_sha=None)
        result = calendar_cli.simulate_to_native_date(args, plan, research_delegation=self)
        if result["status"] == "VERIFIED_IN_MEMORY":
            return dict(result, status="VERIFIED", source_ref=result["evidence_id"])
        return result


class NativeWindowPort:
    """Reuse the actual Host, separately authorized calendar, and WorldData capture entry points."""
    mode = "LIVE"

    def __init__(self, host, calendar_dispatch, worlddata_capture, binding):
        self.host = host
        self.calendar_dispatch = calendar_dispatch
        self.capture = worlddata_capture
        self.binding = binding

    def setter(self, key, operation):
        return _execute_host_setter(self.host, key, operation, self.binding)

    def simulate(self, key, window):
        return self.calendar_dispatch(key, window)


def _execute_host_setter(host, key, operation, binding):
    delegation = host.research_delegation
    delegation.bind(operation)
    slot = delegation.slot_for(operation)
    team, uid = operation["team_id"], operation["uid"]
    getter = host._get_fresh_live_getter(expected_pid=binding["pid"], expected_team=team,
                                         expected_players={uid}, expected_creation_filetime=binding["epoch"]["creation_filetime"],
                                         tendency_field=slot.native_key)
    if getter is None:
        return {"status": "NOT_EXECUTED", "source_ref": key}
    if getter(uid, slot.native_key) != operation["expected_before"]:
        return {"status": "CAS_MISMATCH", "source_ref": key}
    opened = host.start_cycle(key, candidate_intents=[{
        "issuer_role": "GM", "parameters": {"team_id": team, "player_id": uid,
        "field_id": slot.native_key, "expected_before": operation["expected_before"], "value": operation["target"]}}])
    if opened["intents_added_count"] != 1:
        return {"status": "UNKNOWN", "source_ref": key}
    seal = host.seal_cycle_decisions(key, getter_func=getter, expected_pid=binding["pid"])
    if seal["status"] != "PLAN_PREFLIGHTED_WAITING_AUTH":
        return {"status": "UNKNOWN", "source_ref": key}
    try:
        result = host.authorize_and_execute(key, seal["plan_digest"], expected_pid=binding["pid"])
    except RuntimeError as error:
        if not str(error).startswith("LIVE_CAS_CHANGED_SINCE_APPROVAL"):
            raise
        host.exclude_research_cas_cycle(key, seal["plan_digest"])
        return {"status": "CAS_MISMATCH", "source_ref": seal["plan_digest"]}
    if (result.get("status") != "EXECUTED_AND_READBACK_RECORDED"
            or result.get("readback_verified") is not True or result.get("batch_validation_passed") is not True):
        return {"status": "UNKNOWN", "source_ref": seal["plan_digest"]}
    return {"status": "APPLIED" if result["success_count"] == 1 else "NOOP",
            "source_ref": seal["plan_digest"], "value": operation["target"]}


class WindowRunner:
    def __init__(self, port, journal: Path, *, live_envelope: LiveEnvelope | None = None):
        self.port = port
        self.journal = journal
        self.live_envelope = live_envelope

    def run(self, plan, analyze):
        operations = window_operations(plan)
        windows = plan["subwindows"]
        if not operations or not windows or len({(item["team_id"], item["factor_id"], item["uid"]) for item in operations}) != len(operations):
            raise ValueError("EMPTY_OR_DUPLICATE_WINDOW_OPERATIONS")
        self._validate_calendar(plan, windows)
        if self.port.mode not in ("LIVE", "FIXTURE"):
            raise ValueError("UNKNOWN_RESEARCH_PORT_MODE")
        if self.port.mode == "LIVE":
            from factor_readback import FactorWorldDataPort
            delegation = self.port.host.research_delegation if isinstance(self.port, NativeWindowPort) else None
            if (self.live_envelope is None or not isinstance(self.port, NativeWindowPort)
                    or type(delegation) is not WindowDelegation or delegation.envelope is not self.live_envelope
                    or delegation.binding != self.port.binding or digest(delegation.plan) != digest(plan)
                    or not isinstance(self.port.calendar_dispatch, NativeCalendarPort)
                    or self.port.calendar_dispatch.delegation is not delegation
                    or not isinstance(self.port.capture, FactorWorldDataPort)
                    or self.port.capture.binding != self.port.binding
                    or Path(self.port.calendar_dispatch.outbox).resolve() != self.port.host.outbox_db
                    or any(not op["live_writer_qualified"] for op in operations)):
                raise PermissionError("LIVE_MULTI_FACTOR_QUALIFICATION_AND_DELEGATION_REQUIRED")
            for op in operations:
                require_s4_live_tendency(resolve_tendency_slot(op["factor_id"]).native_key)
            self.live_envelope.verify(plan, self.port.binding, operations, windows)
        elif self.live_envelope is not None:
            raise ValueError("FIXTURE_PORT_CANNOT_CONSUME_REAL_AUTHORITY")
        if any(op["expected_before"] is None or op["target"] is None for op in operations):
            raise ValueError("EXACT_BASELINE_AND_DOSE_REQUIRED")

        run_digest = digest(plan)
        self.journal.mkdir(parents=True, exist_ok=True)
        run = self.journal / run_digest
        run.mkdir()
        record_once(run / "plan.json", plan)
        setters = []
        calendar = []
        try:
            for index, operation in enumerate(operations):
                key = f"vae-{run_digest[:20]}-setter-{index:03d}"
                self._check_authority(plan, operations, windows)
                record_once(run / f"{key}-claim.json", operation)
                receipt = self.port.setter(key, operation)
                record_once(run / f"{key}-receipt.json", receipt)
                setters.append(receipt)
                if not receipt.get("source_ref") or receipt["status"] not in ("APPLIED", "NOOP", "CAS_MISMATCH", "NOT_EXECUTED"):
                    return self._finish(run, "STOPPED_UNKNOWN_NO_REPLAY", setters, calendar)
                if receipt["status"] in ("APPLIED", "NOOP") and receipt.get("value") != operation["target"]:
                    return self._finish(run, "STOPPED_UNKNOWN_NO_REPLAY", setters, calendar)
            if not any(item["status"] == "APPLIED" for item in setters):
                return self._finish(run, "NO_TREATMENT_EXPOSURE", setters, calendar)
            pre = self.port.capture("pre", plan, setters)
            applied = {digest(op): op["target"] for op, receipt in zip(operations, setters, strict=True)
                       if receipt["status"] in ("APPLIED", "NOOP")}
            if (pre["mode"] != self.port.mode or pre["worldline_id"] != plan["worldline_id"]
                    or pre["today"] != plan["start"] or pre["applied_values"] != applied or not pre.get("source_unit")):
                return self._finish(run, "STOPPED_PREWINDOW_IDENTITY_DRIFT", setters, calendar)
            record_once(run / "pre.json", pre)
            for index, window in enumerate(windows):
                key = f"vae-{run_digest[:20]}-calendar-{index:03d}"
                self._check_authority(plan, operations, windows)
                record_once(run / f"{key}-claim.json", window)
                result = self.port.simulate(key, window)
                calendar.append(result)
                record_once(run / f"{key}-receipt.json", result)
                if (result["status"] != "VERIFIED" or result["today"] != window["stop_exclusive"]
                        or sorted(result["final_game_ids"]) != sorted(window["planned_finals"])
                        or sorted(result["next_day_pending_ids"]) != sorted(window["next_day_controls"])
                        or not result.get("source_ref")):
                    return self._finish(run, "STOPPED_CALENDAR_NOT_VERIFIED", setters, calendar)
            post = self.port.capture("post", plan, setters)
            if post["mode"] != self.port.mode or post["worldline_id"] != plan["worldline_id"] or post["today"] != plan["stop_exclusive"]:
                return self._finish(run, "STOPPED_POSTWINDOW_IDENTITY_DRIFT", setters, calendar)
            record_once(run / "post.json", post)
            result = analyze(plan, operations, setters, post)
            exposures = [dict(op, source_ref=receipt["source_ref"], worldline_id=plan["worldline_id"],
                              effective_on=plan["start"], applied=receipt["value"])
                         for op, receipt in zip(operations, setters, strict=True) if receipt["status"] == "APPLIED"]
            return self._finish(run, "ANALYSIS_RECORDED", setters, calendar, result, exposures)
        except Exception as error:
            self._finish(run, "STOPPED_EXCEPTION_RECONCILIATION_REQUIRED", setters, calendar,
                         {"exception_type": type(error).__name__})
            raise

    @staticmethod
    def _validate_calendar(plan, windows):
        cursor = plan["start"]
        games = {row["game_id"]: row["date"] for row in plan["games"]}
        if len(games) != len(plan["games"]):
            raise ValueError("DUPLICATE_PLANNED_GAME")
        if not 1 <= (date.fromisoformat(plan["stop_exclusive"]) - date.fromisoformat(cursor)).days <= 7:
            raise ValueError("RESEARCH_WINDOW_EXCEEDS_SEVEN_DAYS")
        used = set()
        for window in windows:
            end = window["stop_exclusive"]
            finals = window["planned_finals"]
            controls = window["next_day_controls"]
            if (cursor != window["start"] or not 1 <= (date.fromisoformat(end) - date.fromisoformat(cursor)).days <= 2
                    or not finals or not controls or len(finals) != len(set(finals)) or len(controls) != len(set(controls))
                    or set(finals) & used or set(finals) & set(controls)
                    or any(gid not in games or not cursor <= games[gid] < end for gid in finals)
                    or (end < plan["stop_exclusive"] and set(controls) != {gid for gid, day in games.items() if day == end})):
                raise ValueError("INVALID_EXACT_CALENDAR_SUBWINDOW")
            used.update(finals)
            cursor = end
        if cursor != plan["stop_exclusive"] or used != set(games):
            raise ValueError("CALENDAR_COVERAGE_MISMATCH")

    def _check_authority(self, plan, operations, windows):
        if self.port.mode == "LIVE":
            if (self.journal / "REVOKED").exists():
                raise PermissionError("HUMAN_ENVELOPE_REVOKED")
            self.live_envelope.verify(plan, self.port.binding, operations, windows)

    def _finish(self, run, status, setters, calendar, analysis=None, exposures=()):
        claimed_setters = sum(1 for _ in run.glob("*-setter-*-claim.json"))
        claimed_calendar = sum(1 for _ in run.glob("*-calendar-*-claim.json"))
        result = {"status": status, "mode": self.port.mode, "setter_attempts": claimed_setters,
                  "setter_success": sum(row["status"] == "APPLIED" for row in setters),
                  "setter_unreturned": claimed_setters - len(setters),
                  "calendar_attempts": claimed_calendar, "calendar_unreturned": claimed_calendar - len(calendar),
                  "analysis": analysis, "applied_exposures": exposures}
        record_once(run / "result.json", result)
        return result


def run_series(next_plan, runner_for, analyze, *, maximum_windows, maximum_calendar, maximum_setters):
    """Continue only from sealed outcomes and keep aggregate research limits."""
    if not 1 <= maximum_windows <= 14 or not 1 <= maximum_calendar <= 56 or not 1 <= maximum_setters <= 168:
        raise ValueError("BOUNDED_SERIES_BUDGET_REQUIRED")
    results = []
    used_setters = used_calendar = 0
    for _ in range(maximum_windows):
        plan = next_plan(tuple(results))
        if plan is None:
            break
        if results and (plan["worldline_id"] != results[-1]["worldline_id"]
                        or plan["start"] != results[-1]["stop_exclusive"]):
            raise ValueError("SERIES_CONTINUATION_NOT_BOUND_TO_PREVIOUS_WORLDLINE_AND_TODAY")
        if (used_setters + len(window_operations(plan)) > maximum_setters
                or used_calendar + len(plan["subwindows"]) > maximum_calendar):
            break
        result = runner_for(plan).run(plan, analyze)
        used_setters += result["setter_attempts"]
        used_calendar += result["calendar_attempts"]
        results.append(dict(result, stop_exclusive=plan["stop_exclusive"], worldline_id=plan["worldline_id"]))
        if result["status"] != "ANALYSIS_RECORDED":
            break
    return {"windows": results, "setter_attempts": used_setters, "calendar_attempts": used_calendar}
