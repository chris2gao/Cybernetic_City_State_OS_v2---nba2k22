from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
repo = root.parents[4]
native = repo / "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control"
worlddata = repo / "08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype"
sys.path[:0] = [str(native), str(worlddata)]
from contracts import BUILD
from factor_runner import QualificationDelegation, QualificationEnvelope, digest
from season_cycle_host import SeasonCycleHost
from live_world import initialize_save, read_binding, bound_database
from refresh import _context
from native_factor_slots import resolve_tendency_slot

source = json.loads((root.parent / "FIRST_BATCH_FROZEN_PLAN.json").read_bytes())
pid = source["pid"]
slot = Path("E:/games/NBA 2K22/data/steam/steam_settings/1644960/remote/MyLEAGUE0005")
cold = slot.with_name("MyLEAGUE0003")
target = root / "qualification-live-final"
target.mkdir(exist_ok=False)

def write(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")

def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()

summary = {"status":"STARTING", "actual_successful_setters":0, "calendar_dispatches":0, "completed_groups":[]}
try:
    assert sha(slot)==source["source_save_sha256"] and sha(cold)==source["cold_backup_sha256"]
    assert _context(pid)["epoch"]==source["epoch"]
    world = root / "world-0005"
    shared_outbox = root / "qualification-live-fast/outbox.sqlite"
    host = SeasonCycleHost(state_file=target/"host-state.json",ledger_file=target/"host-ledger.jsonl",outbox_db=shared_outbox)
    initialized = host.bind_verified_live_capture(str(world),slot.name,str(root/"fresh-capture"),
                                                  source["source_report_sha256"],source["epoch"])
    save_binding, binding_sha = read_binding(world, slot.name)
    context = _context(pid)
    assert context["epoch"]==source["epoch"] and context["game_progress"]==source["native_today"]
    binding = {"save_id":save_binding["save_id"],"worldline_id":save_binding["worldline_id"],
               "loaded_filename":slot.name,"binding_sha256":binding_sha,"epoch":context["epoch"],"pid":pid,
               "today":context["game_progress"]["today_native_iso_date"],"minutes":context["game_progress"]["today_minutes_since_midnight_raw"],
               "build_sha256":BUILD,"bound_database_file":bound_database(world,save_binding).name,
               "loaded_slot_attestation_ref":"Human: 直接开始，不用做检查，就是给你准备的。",
               "disk_save":str(slot),"cold_backup":str(cold),"disk_sha256":sha(slot),"cold_backup_sha256":sha(cold),
               "outbox_db":str(host.outbox_db)}
    snapshots = []
    for row in source["qualifications"]:
        snapshot = host.read_factor_qualification_snapshot(pid=pid,epoch=binding["epoch"],team_id=row["team_id"],uid=row["uid"],
                                                          field=row["field_id"],binding_sha256=binding_sha)
        assert snapshot["raw_value"]==row["expected_before"]
        snapshots.append({"factor_id":row["factor_id"],"team_id":row["team_id"],"uid":row["uid"],
                          "expected_before":row["expected_before"],"target":row["target"],"before":snapshot})
    now = datetime.now(timezone.utc)
    parent = {"schema":"nba2k22.live.qualification_parent.v1","human_instruction":"直接开始，不用做检查，就是给你准备的。",
              "authority_ref":"Human direct-start instruction in this chat after Issue40 continuation",
              "task_contract":"https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/40#issuecomment-6794780940",
              "engineering_base":"1372d1b62467dbd6fa51a9db24f0c4feaff40a1c","maximum_setters":16,"maximum_calendar":0,
              "operations":snapshots,"binding":binding,"valid_from":now.isoformat(),"expires_at":(now+timedelta(hours=2)).isoformat(),
              "research_isolation":"QUALIFICATION_ONLY; HUMAN_RELOAD_SAME_UNMODIFIED_0005_REQUIRED_BEFORE_RESEARCH"}
    write(target/"parent-authorization.json",parent)
    parent_pin = sha(target/"parent-authorization.json")
    write(target/"parent-pin.json",{"sha256":parent_pin,"authorization_basis":parent["human_instruction"]})
    for index in range(0,len(snapshots),3):
        operations=snapshots[index:index+3]
        journal=target/f"group-{index//3+1:02d}"
        bound=dict(binding,journal_root=str(journal))
        grant={"schema":"nba2k22.vae.write_qualification.v1","revoked":False,
               "human_decision_ref":parent["authority_ref"]+"; parent sha256 "+parent_pin,
               "binding":bound,"operation_digests":[digest(op) for op in operations],"maximum_setters":len(operations),
               "maximum_calendar":0,"valid_from":parent["valid_from"],"expires_at":parent["expires_at"]}
        raw=json.dumps(grant,sort_keys=True,separators=(",",":")).encode()
        write(target/f"group-{index//3+1:02d}-envelope.json",grant)
        delegation=QualificationDelegation(QualificationEnvelope(raw,hashlib.sha256(raw).hexdigest()),bound,operations,journal)
        host.research_delegation=delegation
        print(f"Executing qualification group {index//3+1}, {len(operations)} slots",flush=True)
        result=delegation.run(host)
        write(target/f"group-{index//3+1:02d}-result.json",result)
        summary["completed_groups"].append(result)
        summary["actual_successful_setters"]+=sum(row["status"]=="APPLIED" for row in result["receipts"])
        if result["status"]!="QUALIFICATION_EVIDENCE_RECORDED":
            raise RuntimeError("QUALIFICATION_GROUP_NOT_VERIFIED_NO_REPLAY")
        print(f"Verified {summary['actual_successful_setters']} actual slot changes",flush=True)
    assert sha(slot)==source["source_save_sha256"] and sha(cold)==source["cold_backup_sha256"]
    summary.update(status="QUALIFICATION_COMPLETE_RELOAD_REQUIRED",successfully_qualified_fields=[row["factor_id"] for row in snapshots],
                   source_save_sha256=sha(slot),cold_backup_sha256=sha(cold))
except BaseException as error:
    summary.update(status="STOPPED_RECONCILIATION_REQUIRED",error_type=type(error).__name__,error=str(error))
finally:
    write(target/"RESULT.json",summary)
    print(json.dumps({key:value for key,value in summary.items() if key!="completed_groups"}),flush=True)
raise SystemExit(summary["status"]!="QUALIFICATION_COMPLETE_RELOAD_REQUIRED")
