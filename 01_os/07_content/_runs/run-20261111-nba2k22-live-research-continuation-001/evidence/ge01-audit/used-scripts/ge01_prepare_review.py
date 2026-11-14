"""Prepare exact existing-controller plans and reuse evidence for Human review; inert."""
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

REPO = Path(__file__).resolve().parents[5]
DOMAIN = REPO / "08_Domain_Applications/Antigravity_GM_Engine"
NATIVE = DOMAIN / "research/rea_native_control"
sys.path[:0] = [str(NATIVE), str(DOMAIN / "world_data_prototype"), str(NATIVE / "tools/test_only_calendar")]
import calendar_cli as calendar
from native_factor_slots import resolve_tendency_slot

ROOT = Path("C:/Users/gk/Documents/ChatGPT/nba2k22/ge01-runtime")
RUN = REPO / "01_os/07_content/_runs/run-20261111-nba2k22-live-research-continuation-001"


def load(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    proposal = load(ROOT / "GE01_W01_ENVELOPE_PROPOSAL.json")
    wanted = {item["factor_id"] for item in proposal["operations"]}
    evidence = []
    old = RUN / "_runtime/qualification-live-final"
    for path in sorted(old.glob("group-*/qualification-*/plan.json")):
        parent = load(path)
        for index, operation in enumerate(parent["operations"]):
            if operation["factor_id"] not in wanted:
                continue
            slot = resolve_tendency_slot(operation["factor_id"])
            key = "vae-qualification-" + path.parent.name.split("-", 1)[1][:20] + f"-{index}"
            journal = old / "journals" / key
            readback_path = journal / "runtime/independent-readback.json"
            observed = load(readback_path)
            before, after = operation["before"], observed["qualification_snapshot"]
            assert load(path.parent / f"receipt-{index}.json")["status"] == "APPLIED"
            assert observed["missed_count"] == 0 and all(row["confirmed"] for row in observed["verified_items"])
            slot.verify_readback(bytes.fromhex(before["neighborhood_hex"]), bytes.fromhex(after["neighborhood_hex"]),
                                 operation["expected_before"], operation["target"], observed["verified_items"][0]["readback_getter"])
            native, = (journal / "runtime").glob("*/evidence.json")
            batch, = journal.glob("batch_*.json")
            evidence.append({"factor_id": slot.factor_id, "native_key": slot.native_key,
                             "mode": "LIVE", "outcome": "CONFIRMED_APPLIED", "before": before, "after": after,
                             "independent_review_ref": None, "review_status": "AWAITING_HUMAN_ACCEPTANCE_FOR_REUSE",
                             "native_plan_sha256": sha(batch), "native_evidence_sha256": sha(native),
                             "independent_readback_sha256": sha(readback_path),
                             "paths": [str(item.relative_to(REPO)) for item in (path, batch, native, readback_path)]})
    assert {item["factor_id"] for item in evidence} == wanted and len(evidence) == 5
    reuse = {"schema": "nba2k22.ge01.qualification_reuse.proposal.v1", "build_sha256": calendar.BUILD,
             "status": "HUMAN_TECHNICAL_ACCEPTANCE_PENDING", "slots": evidence,
             "new_qualification_writes": 0, "scope": "Build-scoped setter/Getter byte evidence, not basketball effect or live research acceptance"}
    write(ROOT / "GE01_QUALIFICATION_REUSE_EVIDENCE.json", reuse)
    frame = load(ROOT / "READ_ONLY_ENGINE_FRAME.json")["structuredContent"]
    event, = [row["payload"] for row in frame["normalized_result"]["messages"] if row["type"] == "send"]
    assert event["idle"] and event["game_writes"] == 0 and frame["normalized_result"]["cleanup_error"] is None
    fresh = proposal["baseline"]
    database = Path(proposal["database"])
    report = load(ROOT / "clean-0005-01/fresh-capture/refresh-report.json")
    unit = next(row["unit"]["unit_id"] for row in report["sources"] if row["family"] == "schedule")
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        games = {row["id"]: dict(row) for row in conn.execute("""
            SELECT CAST(g.native_game_id AS INT) id,x.scheduled_native_iso_date day,
                   CAST(h.native_team_id AS INT) home,CAST(a.native_team_id AS INT) away
            FROM games g JOIN game_source_checks x USING(game_id)
            JOIN teams h ON h.team_id=g.home_team_id JOIN teams a ON a.team_id=g.away_team_id
            WHERE x.unit_id=? AND x.game_type_label='NORMAL'
        """, (unit,))}
    stop = (date.fromisoformat(max(row["day"] for row in games.values())) + timedelta(days=1)).isoformat()
    outbox = RUN / "_runtime/qualification-live-fast/outbox.sqlite"
    assert outbox.is_file()
    plans = []
    for window in proposal["calendar_windows"]:
        plan = {"schema": calendar.SCHEMA, "build_sha256": calendar.BUILD,
                "source_sha256": calendar.load(calendar.HERE / "capability_manifest.json")["source_sha256"],
                "test_only": True, "disposable_save": True, "event_free_regular_season": True,
                "start": window["start"], "stop_exclusive": window["stop_exclusive"], "season_stop_exclusive": stop,
                "entry_transition": window["phase"] == "ENTRY_TRANSITION", "entry_minutes": window["entry_minutes"],
                "today_raw": fresh["scene"]["game_progress"].get("today_raw", 726635074) if window["phase"] == "ENTRY_TRANSITION" else calendar.word(date.fromisoformat(window["start"])),
                "save_id": proposal["binding"]["save_id"], "worldline_id": proposal["binding"]["worldline_id"],
                "loaded_filename": "MyLEAGUE0005", "binding_sha256": fresh["binding_sha256"],
                "disk_sha256": fresh["native_slot_sha256"], "cold_backup_sha256": fresh["cold_backup_sha256"],
                "epoch": fresh["scene"]["epoch"], "engine_thread": event["thread"],
                "engine_thread_evidence": frame["evidence_id"], "observation_ms": 120000,
                "authorization_scope": "GE01-W01-" + proposal["plan_digest"][:24],
                "save_directory": str(database.parent), "database": str(database),
                "cold_backup": str(Path(proposal["binding"]["native_save_file"]).with_name("MyLEAGUE0003")),
                "outbox_db": str(outbox),
                "games": [games[ident] for ident in sorted(window["planned_finals"] + window["next_day_controls"])]}
        calendar.validate_plan(plan)
        plans.append(plan)
    write(ROOT / "GE01_NATIVE_CALENDAR_PLANS.json", plans)
    proposal.update(engine_thread=event["thread"], engine_thread_evidence=frame["evidence_id"],
                    native_calendar_digests=[calendar.digest(plan) for plan in plans],
                    qualification_reuse_sha256=sha(ROOT / "GE01_QUALIFICATION_REUSE_EVIDENCE.json"),
                    technical_reuse_acceptance="Human review and acceptance of the five pinned historical Setter/Getter/neighborhood receipts is requested with the exact execution envelope",
                    native_calendar_source_sha256=sha(calendar.HERE / "calendar_cli.py"))
    write(ROOT / "GE01_W01_REVIEW_ENVELOPE.json", proposal)
    lines = ["# GE-01 W01 精确操作封套（待 Human 确认）", "",
             "当前0005及16处历史资格改值按Human最新裁决作为新T0；不回滚、不保存或恢复存档。",
             f"PID {fresh['scene']['epoch']['pid']}；creation FILETIME {fresh['scene']['epoch']['creation_filetime']}；Native Today 2021-11-15 19:30；只读观察engine thread {event['thread']}。", "",
             "采集已完成：463名当前名单球员，299名符合现有筛选。最大20次Setter、5次Calendar；资格试写0次、保存/恢复0次。", "",
             "## 精确修改清单", "", "| Team | UID | 字段 | before → target |", "|---:|---:|---|---|"]
    lines += [f"| {op['team_id']} | {op['uid']} | {op['native_key']} | {op['expected_before']} → {op['target']} |" for op in proposal["operations"]]
    lines += ["", "## 日历清单", "", "| 阶段 | 起止（终点不含当日比赛） | 完成GameID | 下一日保持待赛 |", "|---|---|---|---|"]
    lines += [f"| {item['phase']} | {item['start']} → {item['stop_exclusive']} | {','.join(map(str,item['planned_finals']))} | {','.join(map(str,item['next_day_controls']))} |" for item in proposal["calendar_windows"]]
    lines += ["", "入场7场，W01正式53场；总计60场。5个字段各2H/2L/2C，30队，20次±5处理。复用旧资格原始证据，需Human接纳本文件所附五字段技术复用证据；它不证明篮球效果或已完成独立研究验收。", "",
              "执行保留UID/Team、8位字段和99字节邻域、精确CAS、独立Getter、绑定/epoch、同一Outbox与Journal。CAS或资格条件变化不自动换人换量；UNKNOWN不重播。模拟时游戏须保持前台，实际Native代码再次检查线程/idle/完整GameID，失败停止对应操作。", "",
              "真实风险：比赛随机结果、伤病/轮换/角色变化及跨字段对手干扰；程序不主动保存，但不能仅凭内存操作保证游戏不会自行自动保存。按原生GameID+同源Box、赛后WorldData和H/L/C分析判Done，未显著不等于无效。", "",
              "当前为HUMAN_AUTHORIZATION_REQUIRED。批准上述精确操作和五字段历史资格证据复用后，程序在本封套内连续推进；无新增资格试写或业务替换。",
              f"审核封套SHA256：{sha(ROOT / 'GE01_W01_REVIEW_ENVELOPE.json')}。", ""]
    (ROOT / "GE01_W01_ENVELOPE.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "HUMAN_AUTHORIZATION_REQUIRED", "operations": 20, "calendar": len(plans),
                      "engine_thread": event["thread"], "historical_field_evidence": len(evidence),
                      "envelope_sha256": sha(ROOT / "GE01_W01_REVIEW_ENVELOPE.json")}))


if __name__ == "__main__":
    main()
