"""Bind a live experiment to the current Human V2 goal and reserve each operation once."""
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

from experiment_round import digest

SLOT = "MyLEAGUE0005"
FIELD = "SHOT_TENDENCY"
MAX_CYCLES = 14
MAX_SETTERS = 168
MAX_CALENDAR = 56
MAX_DAYS = 98


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def utc_now():
    return datetime.now(timezone.utc)


def freeze(path, data):
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
        stream.flush()
        import os
        os.fsync(stream.fileno())


class ResearchAuthority:
    def __init__(self, goal_file, goal_sha, root, binding, epoch, start, season_stop):
        raw = goal_file.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == goal_sha, "Active Human goal source pin mismatch")
        goal = json.loads(raw)
        clauses = ("恢复执行令 V2", "开始真实批量自动实验", SLOT, FIELD, "+5", "-5", "14 个研究周期",
                   "168 次真实字段写入", "56 次原生日历调用", "98 游戏日", "不允许自动跨入季后赛")
        require(goal["source"] == "codex.get_goal" and goal["status"] == "active"
                and all(clause in goal["objective"] for clause in clauses), "Human V2 scope missing")
        require(binding["loaded_filename"] == SLOT and start < season_stop, "Invalid regular-season binding")
        self.root = root
        self.ref = f"codex-goal:{goal['threadId']}:{goal_sha}"
        self.starts_at = utc_now()
        self.expires_at = self.starts_at + timedelta(hours=24)
        self.binding = binding
        self.epoch = epoch
        self.season_stop = min(season_stop, start + timedelta(days=MAX_DAYS))
        self.next_start = start
        self.round = None
        self.target = None
        self.calendar = None
        self.round_count = self.setter_count = self.calendar_count = 0
        self.reserved_players = set()
        self.round_setters = set()
        self.authorized_setter = None

    def active(self):
        require(utc_now() < self.expires_at and not (self.root / "REVOKED").exists(),
                "Human authorization expired or revoked")

    def bind_round(self, plan):
        self.active()
        start, stop = map(date.fromisoformat, (plan["start"], plan["stop"]))
        ident = plan["identity"]
        require(self.round_count < MAX_CYCLES and start == self.next_start
                and 1 <= (stop - start).days <= 7 and stop <= self.season_stop
                and ident["save"] == self.binding["save_id"] and ident["worldline"] == self.binding["worldline_id"]
                and ident["binding_sha256"] == self.binding["binding_sha256"] and ident["epoch"] == self.epoch,
                "Research round exceeds active binding or date budget")
        require(plan["research_plan_digest"] == digest({k: v for k, v in plan.items() if k != "research_plan_digest"}),
                "Research plan digest mismatch")
        candidates = plan["write_candidates"]
        teams = {item["team_id"] for item in candidates}
        players = {item["uid"] for item in candidates}
        assignments = {item["team_id"]: item for item in plan["assignments"]}
        require(plan["factor"] == FIELD and 1 <= len(candidates) == len(teams) == len(players) <= 12
                and len(assignments) == 30 and not players & self.reserved_players
                and self.setter_count + len(candidates) <= MAX_SETTERS, "Research setter budget or carryover conflict")
        for item in candidates:
            row = assignments[item["team_id"]]
            require(row["arm"] in ("H", "L") and row["uid"] == item["uid"] and item["field"] == FIELD
                    and row["baseline"] == item["expected_before"] and row["planned_value"] == item["target"]
                    and type(item["expected_before"]) is int and type(item["target"]) is int
                    and 0 <= item["expected_before"] <= 100 and 0 <= item["target"] <= 100
                    and item["target"] - item["expected_before"] == (5 if row["arm"] == "H" else -5),
                    "Research target does not match the frozen arm and dose")
        self.round_count += 1
        self.round = plan
        self.round_setters.clear()
        self.next_start = start
        freeze(self.root / f"round-{self.round_count:02d}-plan.json", plan)

    def bind_target(self, item):
        self.active()
        require(self.round is not None and item in self.round["write_candidates"]
                and self.next_start.isoformat() == self.round["start"] and item["uid"] not in self.reserved_players,
                "Setter is outside current pre-sim round")
        self.target = dict(item)
        self.authorized_setter = None

    def role_manifest(self):
        self.active()
        require(self.target is not None, "No frozen target")
        t = self.target
        return {
            "save_id": self.binding["save_id"], "worldline_id": self.binding["worldline_id"],
            "binding_sha256": self.binding["binding_sha256"],
            "bound_database_file": Path(self.binding["database"]).name,
            "human_authorization_ref": self.ref, "provenance": "V2_DERIVED_RESEARCH_ROLE",
            "authorized_at": self.starts_at.isoformat(), "expires_at": self.expires_at.isoformat(),
            "action_id": "PLAYER_PATCH_TENDENCIES", "field_id": FIELD, "player_ids": [t["uid"]],
            "roles": [{"role_type": "GM", "team_id": t["team_id"], "actor_uid": f"vae-research-{t['team_id']}"}],
        }

    def check_scene(self, context, slot, binding_sha):
        self.active()
        progress = context["game_progress"]
        require(slot == SLOT and binding_sha == self.binding["binding_sha256"] and context["epoch"] == self.epoch
                and progress["mode_raw"] == 1 and progress["period_raw"] == 29
                and progress["today_minutes_since_midnight_raw"] == 0
                and progress["today_native_iso_date"] == self.next_start.isoformat(), "Native scene or binding drift")

    def verify_setter(self, cycle, plan_digest, batch, context):
        self.active()
        target = self.target
        require(target is not None and len(batch.intents) == 1 and context["player_ids"] == [target["uid"]],
                "Expected exactly one delegated native setter")
        item, = batch.intents
        require((item.team_id, item.player_id, item.field_id, item.expected_before, item.value)
                == (target["team_id"], target["uid"], FIELD, target["expected_before"], target["target"]),
                "Exact S4 native intent differs from delegated dose")
        self.authorized_setter = (cycle, plan_digest)
        return self.ref

    def reserve_setter(self, cycle, plan_digest):
        self.active()
        t = self.target
        require(self.authorized_setter == (cycle, plan_digest) and self.setter_count < MAX_SETTERS
                and t["uid"] not in self.reserved_players and t["team_id"] not in self.round_setters,
                "Setter budget exhausted or operation already reserved")
        freeze(self.root / f"{cycle}-reservation.json",
               {"authorization": self.ref, "plan_digest": plan_digest, "target": t})
        self.setter_count += 1
        self.reserved_players.add(t["uid"])
        self.round_setters.add(t["team_id"])

    def bind_calendar(self, plan):
        self.active()
        self.target = None
        self.calendar = plan
        self.verify_calendar(plan)

    def verify_calendar(self, plan):
        self.active()
        require(self.calendar is not None and digest(self.calendar) == digest(plan)
                and all(plan[key] == self.binding[key] for key in
                        ("loaded_filename", "binding_sha256", "worldline_id", "save_id", "database"))
                and plan["epoch"] == self.epoch and plan["authorization_scope"] == self.ref
                and plan["start"] == self.next_start.isoformat()
                and date.fromisoformat(plan["stop_exclusive"]) <= self.season_stop, "Calendar plan is outside delegated round")
        final = {(r["id"], r["day"], r["home"], r["away"]) for r in plan["games"]
                 if r["day"] < plan["stop_exclusive"]}
        if plan.get("empty_transit") is True:
            require(not final and self.round is None, "Empty calendar transit cannot contain a research window")
        else:
            require(self.round is not None and plan["stop_exclusive"] <= self.round["stop"],
                    "Calendar extends beyond the pre-registered round")
            expected = {(r["game_id"], r["day"], r["home"], r["away"]) for r in self.round["games"]
                        if plan["start"] <= r["day"] < plan["stop_exclusive"]}
            require(final and final == expected, "Calendar finals do not match pre-registered window")
        return {"expires_at": min(self.expires_at, utc_now() + timedelta(minutes=3)).isoformat(),
                "human_decision_ref": self.ref}

    def reserve_calendar(self, plan):
        self.verify_calendar(plan)
        require(self.calendar_count < MAX_CALENDAR, "Calendar call budget exhausted")
        freeze(self.root / f"calendar-{self.calendar_count+1:02d}-reservation.json",
               {"authorization": self.ref, "plan_digest": digest(plan), "start": plan["start"]})
        self.calendar_count += 1

    def advance(self, summary):
        require(summary["status"] == "VERIFIED_IN_MEMORY" and summary["today"] == self.calendar["stop_exclusive"],
                "Calendar did not finish with verified native Today")
        self.next_start = date.fromisoformat(summary["today"])
        self.calendar = None
