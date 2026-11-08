"""Full-denominator progress and role-neutral mechanism knowledge queries."""
from collections import Counter, defaultdict
from contextlib import closing
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

STAGES = ("INVENTORIED", "NATIVE_LOCATED", "WRITE_READBACK_QUALIFIED", "SCHEDULED",
          "LIVE_EXPOSED", "BROAD_SCREENED", "CONFIRMING", "REPLICATED_OR_LIMITED")
_REQUIRED = {
    "NATIVE_LOCATED": {"build_sha256", "location"},
    "WRITE_READBACK_QUALIFIED": {"build_sha256", "identity", "legal_domain", "readback_ref"},
    "SCHEDULED": {"worldline_id", "plan_digest", "opportunities"},
    "LIVE_EXPOSED": {"worldline_id", "identity", "field_value", "readback_ref", "exposure_ref"},
    "BROAD_SCREENED": {"worldline_id", "effect", "analysis_ref", "limitations"},
    "CONFIRMING": {"protocol_id", "plan_digest", "independent_worldlines"},
    "REPLICATED_OR_LIMITED": {"reliability", "reason", "analysis_ref", "contradictions"},
}


@dataclass(frozen=True)
class ProgressEvent:
    factor_id: str
    stage: str
    mode: str
    source_sha256: str
    evidence: dict


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _hash(value):
    return sha256(_encode(value).encode()).hexdigest()


_SCHEMA = (
    "CREATE TABLE IF NOT EXISTS inventory (key INTEGER PRIMARY KEY CHECK(key=1), sha256 TEXT NOT NULL)",
    """CREATE TABLE IF NOT EXISTS progress_events (
        ordinal INTEGER PRIMARY KEY, sha256 TEXT NOT NULL UNIQUE, payload TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS window_receipts (
        ordinal INTEGER PRIMARY KEY, mode TEXT NOT NULL, plan_digest TEXT NOT NULL,
        source_sha256 TEXT NOT NULL, payload_sha256 TEXT NOT NULL, payload TEXT NOT NULL,
        UNIQUE(mode, plan_digest)
    )""",
)


class ProgressLedger:
    def __init__(self, study, events=(), *, database=None):
        self.study = study
        self._history = defaultdict(list)
        self.database = Path(database) if database is not None else None
        if self.database is not None:
            identity = _hash({key: asdict(factor) for key, factor in study.factors.items()})
            with closing(sqlite3.connect(self.database)) as conn, conn:
                conn.execute("BEGIN IMMEDIATE")
                tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if tables and tables != {"inventory", "progress_events", "window_receipts"}:
                    raise ValueError("PROGRESS_DATABASE_SCHEMA_MISMATCH")
                for definition in _SCHEMA:
                    conn.execute(definition)
                conn.execute("INSERT OR IGNORE INTO inventory VALUES (1, ?)", (identity,))
                if conn.execute("SELECT sha256 FROM inventory WHERE key=1").fetchone() != (identity,):
                    raise ValueError("PROGRESS_INVENTORY_SHA_MISMATCH")
                for table in ("inventory", "progress_events", "window_receipts"):
                    for operation in ("UPDATE", "DELETE"):
                        conn.execute(f"""CREATE TRIGGER IF NOT EXISTS {table}_no_{operation.lower()}
                            BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT,'immutable progress'); END""")
                self._history = self._restore(conn)
        self.record_many(events)

    def record(self, event):
        self.record_many((event,))

    def record_many(self, events):
        events = tuple(events)
        if not events:
            return
        if self.database is None:
            history = defaultdict(list, {key: list(rows) for key, rows in self._history.items()})
            self._append(history, events)
        else:
            with closing(sqlite3.connect(self.database)) as conn, conn:
                conn.execute("BEGIN IMMEDIATE")
                history = self._restore(conn)
                self._append(history, events, conn)
        self._history = history

    def _restore(self, conn):
        history = defaultdict(list)
        for pin, payload in conn.execute("SELECT sha256,payload FROM progress_events ORDER BY ordinal"):
            if sha256(payload.encode()).hexdigest() != pin:
                raise ValueError("PROGRESS_EVENT_HASH_MISMATCH")
            self._record(history, ProgressEvent(**json.loads(payload)))
        return history

    def _reload(self):
        if self.database is not None:
            with closing(sqlite3.connect(self.database)) as conn:
                self._history = self._restore(conn)

    def _append(self, history, events, conn=None):
        for event in events:
            payload = _encode(asdict(event))
            normalized = ProgressEvent(**json.loads(payload))
            if normalized in history[normalized.factor_id, normalized.mode]:
                continue
            self._record(history, normalized)
            if conn is not None:
                conn.execute("INSERT INTO progress_events(sha256,payload) VALUES (?,?)",
                             (sha256(payload.encode()).hexdigest(), payload))

    def _record(self, timeline, event):
        if event.factor_id not in self.study.factors or event.stage not in STAGES[1:]:
            raise ValueError("UNKNOWN_FACTOR_OR_STAGE")
        if (event.mode not in ("FIXTURE", "LIVE") or len(event.source_sha256) != 64
                or any(char not in "0123456789abcdef" for char in event.source_sha256)
                or not _REQUIRED[event.stage] <= event.evidence.keys()):
            raise ValueError("PROGRESS_EVIDENCE_INCOMPLETE")
        history = timeline[event.factor_id, event.mode]
        previous = history[-1].stage if history else "INVENTORIED"
        limited = (event.stage == "REPLICATED_OR_LIMITED" and event.evidence["reliability"] in
                   ("NO_OPPORTUNITY", "NO_MEASURABLE_ENDPOINT", "UNIDENTIFIABLE_IN_MODE")
                   and bool(event.evidence.get("technical_scope")) and bool(event.evidence["reason"]))
        if previous == STAGES[-1] or (not limited and STAGES.index(event.stage) != STAGES.index(previous) + 1):
            raise ValueError("PROGRESS_CANNOT_SKIP_EVIDENCE_STAGE")
        if (event.stage == "REPLICATED_OR_LIMITED" and event.evidence["reliability"] == "EFFECT_REPLICATED"
                and len(set(event.evidence.get("independent_worldlines", ()))) < 2):
            raise ValueError("REPLICATION_REQUIRES_INDEPENDENT_WORLDLINES")
        if (event.mode == "LIVE" and event.stage == "REPLICATED_OR_LIMITED"
                and event.evidence["reliability"] == "EFFECT_REPLICATED"
                and not all(event.evidence.get(key) for key in ("independent_review_ref", "human_acceptance_ref"))):
            raise ValueError("REPLICATION_REQUIRES_REVIEW_AND_HUMAN_ACCEPTANCE")
        history.append(event)

    def ingest_window(self, directory, expected_result_sha256, *, mode):
        """Replay a pinned WindowRunner result into progress without calling the game."""
        if self.database is None or mode not in ("LIVE", "FIXTURE"):
            raise ValueError("WINDOW_PROGRESS_REQUIRES_PERSISTENT_LEDGER_AND_EVIDENCE_MODE")
        plan, result, events = _window_evidence(Path(directory), expected_result_sha256, mode)
        if not set(plan["factors"]) <= self.study.factors.keys():
            raise ValueError("WINDOW_PROGRESS_UNKNOWN_FACTOR")
        payload = {"status": result["status"], "factors": plan["factors"], "worldline_id": plan["worldline_id"],
                   "start": plan["start"], "stop_exclusive": plan["stop_exclusive"],
                   "result_sha256": expected_result_sha256}
        payload["factor_status"] = {key: row["status"] for key, row in (result.get("analysis") or {}).get("factors", {}).items()}
        with closing(sqlite3.connect(self.database)) as conn, conn:
            conn.execute("BEGIN IMMEDIATE")
            history = self._restore(conn)
            prior = conn.execute("SELECT source_sha256 FROM window_receipts WHERE mode=? AND plan_digest=?",
                                 (mode, result["plan_digest"])).fetchone()
            if prior and prior != (expected_result_sha256,):
                raise ValueError("WINDOW_PROGRESS_CONFLICTING_RESULT")
            if not prior:
                conn.execute("""INSERT INTO window_receipts(mode,plan_digest,source_sha256,payload_sha256,payload)
                             VALUES (?,?,?,?,?)""", (mode, result["plan_digest"], expected_result_sha256,
                                                     _hash(payload), _encode(payload)))
            for event in events:
                prior_events = history[event.factor_id, mode]
                current = prior_events[-1].stage if prior_events else "INVENTORIED"
                if STAGES.index(event.stage) == STAGES.index(current) + 1:
                    self._append(history, (event,), conn)
        self._history = history
        return payload

    def ingest_qualifications(self, raw, expected_sha256):
        """Register independently accepted raw slot evidence in the live account."""
        from native_factor_slots import AcceptedTendencyQualifications

        registry = AcceptedTendencyQualifications.load(raw, expected_sha256)
        if not registry.factor_ids <= self.study.factors.keys():
            raise ValueError("QUALIFICATION_PROGRESS_UNKNOWN_FACTOR")
        self._reload()
        events = []
        for entry in json.loads(raw)["slots"]:
            factor = entry["factor_id"]
            before, after = entry["before"], entry["after"]
            existing = self._history[factor, "LIVE"]
            if not existing:
                events.append(ProgressEvent(factor, "NATIVE_LOCATED", "LIVE", expected_sha256, {
                    "build_sha256": before["profile_build_sha256"], "location": before["offset"],
                    "native_index": before["index"], "width_bits": before["width_bits"],
                }))
            if not existing or existing[-1].stage == "NATIVE_LOCATED":
                events.append(ProgressEvent(factor, "WRITE_READBACK_QUALIFIED", "LIVE", expected_sha256, {
                    "build_sha256": before["profile_build_sha256"],
                    "identity": {"uid": before["uid"], "team_id": before["team_id"], "worldline_id": before["worldline_id"]},
                    "legal_domain": before["legal_domain"], "readback_ref": entry["independent_readback_sha256"],
                    "independent_review_ref": entry["independent_review_ref"], "native_plan": entry["native_plan_sha256"],
                    "native_evidence": entry["native_evidence_sha256"], "before": before["raw_value"], "after": after["raw_value"],
                }))
        self.record_many(events)
        return {"qualification_sha256": expected_sha256, "qualified_factor_ids": sorted(registry.factor_ids)}

    def queue_details(self, mode="LIVE"):
        """Include durable attempt status without promoting incomplete evidence."""
        latest = {}
        if self.database is not None:
            with closing(sqlite3.connect(self.database)) as conn:
                for pin, payload in conn.execute("SELECT payload_sha256,payload FROM window_receipts WHERE mode=? ORDER BY ordinal", (mode,)):
                    if sha256(payload.encode()).hexdigest() != pin:
                        raise ValueError("WINDOW_PROGRESS_RECEIPT_HASH_MISMATCH")
                    row = json.loads(payload)
                    for factor in row["factors"]:
                        latest[factor] = {"status": row["factor_status"].get(factor, row["status"]),
                                          "result_sha256": row["result_sha256"], "worldline_id": row["worldline_id"]}
        return [{"factor_id": key, **row, "last_window": latest.get(key)}
                for key, row in self.coverage(mode)["factors"].items() if row["stage"] != "REPLICATED_OR_LIMITED"]

    def coverage(self, mode="LIVE"):
        if mode not in ("LIVE", "FIXTURE"):
            raise ValueError("UNKNOWN_EVIDENCE_MODE")
        self._reload()
        rows = {}
        for key, factor in self.study.factors.items():
            history = self._history[key, mode]
            rows[key] = {"stage": history[-1].stage if history else "INVENTORIED",
                         "mode": mode, "protocol": factor.protocol, "reference_slots": factor.reference_slots,
                         "qualification": factor.adapter_state,
                         "limit": history[-1].evidence.get("reason") if history and history[-1].stage == STAGES[-1] else None}
        return {"counts": dict(Counter(row["stage"] for row in rows.values())), "factors": rows}

    def next_queue(self):
        return [key for key, row in self.coverage()["factors"].items() if row["stage"] != "REPLICATED_OR_LIMITED"]

    def history(self, factor_id, *, mode="LIVE"):
        if mode not in ("LIVE", "FIXTURE") or factor_id not in self.study.factors:
            raise ValueError("UNKNOWN_FACTOR_OR_EVIDENCE_MODE")
        self._reload()
        return [asdict(event) for event in self._history[factor_id, mode]]

    def query(self, factor_id, role, *, mode="LIVE"):
        if role not in ("GM", "COACH", "PLAYER"):
            raise ValueError("UNKNOWN_KNOWLEDGE_CONSUMER")
        factor = self.study.factors[factor_id]
        if mode not in ("LIVE", "FIXTURE"):
            raise ValueError("UNKNOWN_EVIDENCE_MODE")
        self._reload()
        history = self._history[factor_id, mode]
        report = next((event for event in reversed(history) if event.stage in ("BROAD_SCREENED", "REPLICATED_OR_LIMITED")), None)
        evidence = report.evidence if report else {}
        return {"factor_id": factor_id, "role": role, "action": factor.native.get("name"),
                "context": factor.protocol, "source": report.source_sha256 if report else None,
                "observed_effect": evidence.get("effect"), "game_ids": evidence.get("game_ids", []),
                "expected_effect_range": evidence.get("interval"),
                "reliability": evidence.get("reliability", "UNCONFIRMED"),
                "tradeoff": evidence.get("tradeoff"), "contraindications": evidence.get("limitations"),
                "contradictions": evidence.get("contradictions", []), "evidence_mode": mode,
                "decision_usable": mode == "LIVE" and evidence.get("reliability") == "EFFECT_REPLICATED",
                "execution_authorized": False}


def _window_evidence(directory, result_sha, mode):
    from factor_analysis import screen_game_window
    from factor_runner import digest, window_operations

    def read(name, pin):
        raw = (directory / name).read_bytes()
        if sha256(raw).hexdigest() != pin:
            raise ValueError(f"WINDOW_PROGRESS_SOURCE_HASH_MISMATCH: {name}")
        return json.loads(raw)

    result = read("result.json", result_sha)
    plan = read("plan.json", result["plan_file_sha256"])
    run_digest = result["plan_digest"]
    if result["mode"] != mode or run_digest != directory.name or len(run_digest) != 64:
        raise ValueError("WINDOW_PROGRESS_MODE_OR_PLAN_MISMATCH")
    if result["status"] != "ANALYSIS_RECORDED":
        if result.get("analysis") and result["analysis"].get("factors"):
            raise ValueError("WINDOW_PROGRESS_STOPPED_HAS_FACTOR_RESULTS")
        return plan, result, []
    pins = result["evidence_files"]
    ops = window_operations(plan)
    windows = plan["subwindows"]

    def receipt_names(kind, items):
        return [f"vae-{run_digest[:20]}-{kind}-{index:03d}-receipt.json" for index in range(len(items))]

    setter_names, calendar_names = receipt_names("setter", ops), receipt_names("calendar", windows)
    if (set(pins) != {"pre.json", "post.json", *setter_names, *calendar_names}
            or result["setter_attempts"] != len(ops) or result["calendar_attempts"] != len(windows)
            or result["setter_unreturned"] or result["calendar_unreturned"]):
        raise ValueError("WINDOW_PROGRESS_INCOMPLETE_RECEIPTS")
    pre, post = (read(name, pins[name]) for name in ("pre.json", "post.json"))
    if any(row["mode"] != mode or row["worldline_id"] != plan["worldline_id"] or not row.get("source_unit")
           for row in (pre, post)) or pre["today"] != plan["start"] or post["today"] != plan["stop_exclusive"]:
        raise ValueError("WINDOW_PROGRESS_CAPTURE_SCOPE_MISMATCH")
    setters = [read(name, pins[name]) for name in setter_names]
    calendar = [read(name, pins[name]) for name in calendar_names]
    for receipt, window in zip(calendar, windows, strict=True):
        if (receipt["status"] != "VERIFIED" or not receipt.get("source_ref")
                or receipt["today"] != window["stop_exclusive"]
                or sorted(receipt["final_game_ids"]) != sorted(window["planned_finals"])
                or sorted(receipt["next_day_pending_ids"]) != sorted(window["next_day_controls"])):
            raise ValueError("WINDOW_PROGRESS_CALENDAR_RECEIPT_MISMATCH")
    exposures = []
    observed = {}
    for op, receipt in zip(ops, setters, strict=True):
        status = receipt["status"]
        if status not in ("APPLIED", "NOOP", "CAS_MISMATCH", "NOT_EXECUTED") or not receipt.get("source_ref"):
            raise ValueError("WINDOW_PROGRESS_SETTER_RECEIPT_UNVERIFIED")
        if status in ("APPLIED", "NOOP"):
            if receipt.get("value") != op["target"]:
                raise ValueError("WINDOW_PROGRESS_SETTER_DOSE_MISMATCH")
            observed[digest(op)] = op["target"]
        if status == "APPLIED":
            exposures.append(dict(op, source_ref=receipt["source_ref"], worldline_id=plan["worldline_id"],
                                  effective_on=plan["start"], applied=op["target"]))
    if (not exposures or len(exposures) != result["setter_success"] or exposures != result["applied_exposures"]
            or observed != pre["applied_values"]):
        raise ValueError("WINDOW_PROGRESS_APPLIED_EXPOSURE_MISMATCH")
    analysis = screen_game_window(plan, ops, setters, post)
    if analysis != result["analysis"]:
        raise ValueError("WINDOW_PROGRESS_ANALYSIS_REPLAY_MISMATCH")

    events = []
    world = plan["worldline_id"]
    for factor, row in analysis["factors"].items():
        games = sorted(game["game_id"] for game in plan["games"]
                       if any(game[side] and game[side]["factor_id"] == factor for side in ("home", "away")))
        if not games:
            continue
        events.append(ProgressEvent(factor, "SCHEDULED", mode, result_sha, {
            "worldline_id": world, "plan_digest": run_digest, "opportunities": len(games), "game_ids": games,
        }))
        treated = [item for item in exposures if item["factor_id"] == factor]
        if not treated:
            continue
        events.append(ProgressEvent(factor, "LIVE_EXPOSED", mode, result_sha, {
            "worldline_id": world, "identity": [{"uid": item["uid"], "team_id": item["team_id"]} for item in treated],
            "field_value": [item["applied"] for item in treated], "readback_ref": pins["pre.json"],
            "exposure_ref": result_sha, "native_receipts": [item["source_ref"] for item in treated], "game_ids": games,
        }))
        events.append(ProgressEvent(factor, "BROAD_SCREENED", mode, result_sha, {
            "worldline_id": world, "effect": {metric: data["estimates"] for metric, data in row["metrics"].items()},
            "analysis_ref": result_sha, "limitations": sorted({data["limitation"] for data in row["metrics"].values()}),
            "reliability": row["status"], "game_ids": sorted({item["game_id"] for item in row["observations"]}),
            "outcome_source": pins["post.json"],
        }))
    return plan, result, events


if __name__ == "__main__":
    import argparse
    from factor_inventory import StudyInputs

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    parser.add_argument("database", type=Path)
    parser.add_argument("--mode", choices=("LIVE", "FIXTURE"), default="LIVE")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("coverage")
    commands.add_parser("queue")
    query = commands.add_parser("query")
    query.add_argument("factor_id")
    query.add_argument("role", choices=("GM", "COACH", "PLAYER"))
    history = commands.add_parser("history")
    history.add_argument("factor_id")
    qualifications = commands.add_parser("ingest-qualifications")
    qualifications.add_argument("accepted_registry", type=Path)
    qualifications.add_argument("expected_sha256")
    ingest = commands.add_parser("ingest-window")
    ingest.add_argument("directory", type=Path)
    ingest.add_argument("expected_result_sha256")
    args = parser.parse_args()
    ledger = ProgressLedger(StudyInputs.load(args.inputs), database=args.database)
    if args.command == "coverage":
        result = ledger.coverage(args.mode)
    elif args.command == "queue":
        result = ledger.queue_details(args.mode)
    elif args.command == "query":
        result = ledger.query(args.factor_id, args.role, mode=args.mode)
    elif args.command == "history":
        result = ledger.history(args.factor_id, mode=args.mode)
    elif args.command == "ingest-qualifications":
        if args.mode != "LIVE":
            parser.error("ingest-qualifications requires LIVE mode")
        result = ledger.ingest_qualifications(args.accepted_registry.read_bytes(), args.expected_sha256)
    else:
        result = ledger.ingest_window(args.directory, args.expected_result_sha256, mode=args.mode)
    print(json.dumps(result, ensure_ascii=False))
