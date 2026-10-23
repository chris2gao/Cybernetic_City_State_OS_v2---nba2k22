"""Executable conceptual counterexamples, not production code or native acceptance."""
from pathlib import Path
import argparse
import copy
import fnmatch
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
D = ROOT / "08_Domain_Applications/Antigravity_GM_Engine/docs/development"
BASE = "407e2134bd2f595477099b2c6e3484c818059fd9"
NAMES = [
    "WORLD_DATA_DOMAIN_MODEL_V1.md", "WORLD_DATA_IDENTITY_AND_TIME_ADR_V1.md",
    "WORLD_DATA_ENTITY_CATALOG_V1.json", "WORLD_DATA_SOURCE_AND_QUALITY_CONTRACT_V1.md",
    "WORLD_DATA_LEGACY_IMPACT_AND_SCHEMA_HANDOFF_V1.md",
]
def strict_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            assert key not in result, f"duplicate key: {key}"
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))

C = strict_json(D / NAMES[2])
E = {e["id"]: e for e in C["entities"]}

def denied(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("negative example was incorrectly accepted")

def conceptual_link(parent_type, parent, child_type, child):
    candidates = [r for r in C["relations"] if r["from"] == parent_type and r["to"] == child_type]
    if not candidates:
        raise ValueError("undeclared relation")
    if E[parent_type]["identity"]["scope"] == "STATIC_RESOURCE":
        if "world_id" in parent or parent.get("dynamic_history") or parent.get("memory"):
            raise ValueError("shared resource contains world data")
        return
    if not parent.get("world_id") or parent["world_id"] != child.get("world_id"):
        raise ValueError("cross-save relation")
    # Catalog specifies the rule, while concrete counterexample expectations are fixed in inputs.
    if any(r["world_rule"] != "SAME_WORLD_REQUIRED" for r in candidates):
        raise AssertionError("world rule weakened")

def binding_continuity(old, new, evidence):
    if not evidence or old["world_id"] != new["world_id"]:
        raise ValueError("same-save continuity unproven")
    return old["world_id"]

def approval_matches(grant, current):
    if tuple(grant) != tuple(current):
        raise ValueError("stale approval")
    return True

def resolve_game(mapping, observation):
    # UNKNOWN mapping never becomes a game by hashing a native ID or allocating per batch.
    if not mapping or mapping["status"] != "VERIFIED":
        raise ValueError("unresolved native identity")
    if mapping["world_id"] != observation["world_id"]:
        raise ValueError("cross-world mapping")
    if mapping["native_id"] != observation["native_id"]:
        raise ValueError("native identity differs")
    return mapping["game_uid"]

def gm_project(world, actor_world, sanitized, fields):
    if world != actor_world or not sanitized:
        raise ValueError("query binding or masking failed")
    allowed = C["query_policy"]["ordinary_GM_allowed_fields"]
    output = {}
    for name, field in fields.items():
        if name not in allowed:
            raise ValueError("field not in DTO")
        if field.get("sensitivity", "PUBLIC") != "PUBLIC":
            raise ValueError("restricted origin")
        if any(x != "PUBLIC" for x in field.get("input_sensitivity", [])):
            raise ValueError("derived from restricted input")
        if isinstance(field["value"], (dict, list)):
            raise ValueError("untyped nested payload")
        output[name] = field["value"]
    return output

def catalog():
    assert len(E) == len(C["entities"])
    assert set(e["domain"] for e in E.values()) == set("ABCDEFG")
    assert C["identity_policy"]["world_branching"] is False
    assert C["identity_policy"]["world_merging"] is False
    assert C["identity_policy"]["cross_world_history_inheritance"] is False
    assert C["constraints"]["batch_is_entity_identity"] is False
    assert C["constraints"]["normal_season_changes_world"] is False
    assert C["constraints"]["unknown_is_zero"] is False
    assert C["constraints"]["native_totals_imply_complete_games"] is False
    aliases = {a for e in E.values() for a in e["aliases"]}
    expected = set("GameSave SaveInstance Season SeasonPhase GameCalendar ObservationTime CaptureBatch Franchise Team TeamSeason Player PlayerIncarnation DraftTemplate Staff Coach RosterMembership Contract Salary WaivedSalary DraftPick TeamFinance Trade Signing StaffEmployment Game TeamGameResult PlayerGameStatline BoxScore SeasonTotals CareerHistory RecordBook Awards PlayerAttributes Tendencies Badges Injury Fatigue Morale Training CoachSettings Playbook TacticalConfiguration NativeObject NativeIdentityMapping CaptureObservation DecoderVersion SourceManifest DataQualityReport AgentObservation AgentDecision Approval ExecutionReceipt GameReadback".split())
    assert expected <= aliases, sorted(expected-aliases)
    assert {"GM角色", "Coach角色", "Player角色"} <= aliases
    rels = {r["id"]: r for r in C["relations"]}
    assert len(rels) == len(C["relations"])
    for ident, e in E.items():
        assert e["definition"] and e["lifecycle"] and e["attributes"] and e["unknown_fields"]
        assert e["identity"]["origin"] == "APPLICATION_GENERATED"
        assert e["source_acceptance"] == "DESIGN_CANDIDATE_NOT_NATIVE_ACCEPTANCE"
        assert e["source_refs"] and all(s in C["source_registry"] for s in e["source_refs"])
        assert e["relations"]
        names = [a["name"] for a in e["attributes"]]
        assert len(names) == len(set(names))
        assert not set(names) & set(C["constraints"]["forbidden_world_fields"])
        assert e["identity"]["world_id_required"] == (ident not in {"DraftTemplate", "DecoderVersion"})
        assert set(e["relations"]) == {r["id"] for r in rels.values() if ident in (r["from"], r["to"])}
    for r in rels.values():
        assert r["from"] in E and r["to"] in E
        assert r["from_cardinality"] in {"1", "0..1", "0..*"}
        assert r["to_cardinality"] in {"0..1", "0..2", "0..*", "1..*"}
        expected_rule = "STATIC_REFERENCE_ONLY" if E[r["from"]]["identity"]["scope"] == "STATIC_RESOURCE" else "SAME_WORLD_REQUIRED"
        assert r["world_rule"] == expected_rule
    for r in C["polymorphic_relations"]:
        assert r["owner"] in E and set(r["targets"]) <= set(E)
        assert r["world_rule"] == "SAME_WORLD_REQUIRED"
    for source in C["source_registry"].values():
        assert (ROOT / source["path"]).is_file(), source["path"]
    model = (D / NAMES[0]).read_text(encoding="utf-8")
    er_lines = re.findall(r'^\s*(\w+)\s+([|o}]+)--([|o{]+)\s+(\w+)\s*:\s*"(R\d+)_[^"]+"', model, re.M)
    assert len(er_lines) == len(rels)
    for source, left, right, target, rid in er_lines:
        r = rels[rid]
        assert (source, target) == (r["from"], r["to"])
        assert left == ("||" if r["from_cardinality"] == "1" else "|o")
        assert right == ("o|" if r["to_cardinality"] == "0..1" else "o{")
    assert "| BoxScore |" in model and "**0..2**" in model
    assert set(rels) == {x[4] for x in er_lines}
    assert "44" in model and len(E) == 44
    print(json.dumps({"check": "CATALOG_RELATIONS", "entities": len(E), "relations": len(rels), "status": "PASS"}))

def scenarios():
    data = strict_json(RUN / "scenario_inputs.json")
    ss = {s["id"]: s for s in data["scenarios"]}
    assert set(ss) == set(C["required_scenarios"])
    results = []
    s = ss["S1_INDEPENDENT_SAVES"]
    players = [{"world_id": w, "uid": "p1", "native_id": s["same_native_player_id"], "name": s["player_name"]} for w in s["worlds"]]
    assert len([p for p in players if p["world_id"] == "A"]) == s["expected_world_A_players"]
    for target in ("PlayerGameStatline", "CareerHistory"):
        conceptual_link("PlayerIncarnation", players[0], target, {"world_id": "A"})
        denied(lambda t=target: conceptual_link("PlayerIncarnation", players[0], t, {"world_id": "B"}))
    conceptual_link("Actor", {"world_id": "A"}, "AgentDecision", {"world_id": "A"})
    denied(lambda: conceptual_link("Actor", {"world_id": "A"}, "AgentDecision", {"world_id": "B"}))
    assert len({(p["world_id"],p["uid"]) for p in players}) == 2
    games=[{"world_id":w,"game_uid":"g7","native_id":7} for w in s["worlds"]]
    assert len({(g["world_id"],g["game_uid"]) for g in games}) == 2
    for target in ("TeamGameResult", "PlayerGameStatline"):
        conceptual_link("Game",games[0],target,{"world_id":"A"})
        denied(lambda t=target:conceptual_link("Game",games[0],t,{"world_id":"B"}))
    results.append({"id": s["id"], "result": "PASS", "players": 2, "games":2, "cross_save_links": "REJECTED"})
    s = ss["S2_CONTINUOUS_CAREER"]
    uid = (s["world"], s["player"])
    for g in s["games"]:
        matches = [m for m in s["memberships"] if m["start"] <= g["year"] < m["end"]]
        assert len(matches) == 1 and matches[0]["team"] == g["expected_team"]
    assert len(s["seasons"]) == 4 and uid == ("A","p1")
    old, new = {"world_id": "A", "binding": s["old_binding"]}, {"world_id": "A", "binding": s["new_binding"]}
    assert binding_continuity(old,new,True) == "A"
    denied(lambda: binding_continuity(old,new,False))
    denied(lambda: binding_continuity(old,{"world_id":"B"},True))
    approval_matches(s["new_binding"],s["new_binding"])
    denied(lambda: approval_matches(s["old_binding"],s["new_binding"]))
    # Membership overlap is explicitly rejected by the conceptual interval constraint.
    def membership_set(rows):
        ordered=sorted(rows,key=lambda m:m["start"])
        if any(a["end"] > b["start"] for a,b in zip(ordered,ordered[1:])):
            raise ValueError("overlapping exclusive memberships")
    membership_set(s["memberships"])
    denied(lambda: membership_set(s["memberships"]+[{"team":"LAL","start":2023,"end":2025}]))
    results.append({"id":s["id"],"result":"PASS","player_uid":"A:p1","stale_approval":"REJECTED"})
    s = ss["S3_REPEAT_CAPTURE"]
    mapping={"world_id":s["world"],"native_id":s["native_game_id"],"game_uid":s["game_uid"],"status":"VERIFIED"}
    game_ids=set()
    observations=[]
    revisions=[]
    for o in s["observations"]:
        observation=dict(o,world_id=s["world"],native_id=s["native_game_id"])
        game_ids.add(resolve_game(mapping,observation))
        observations.append(observation)
        if not revisions or revisions[-1]["score"] != o["score"]:
            revisions.append({"revision":len(revisions)+1,"score":o["score"],"source_batch":o["batch"]})
    assert (len(game_ids),len(observations),len(revisions)) == (s["expected_games"],s["expected_observations"],s["expected_revisions"])
    denied(lambda: resolve_game(dict(mapping,status="UNKNOWN"),observations[0]))
    denied(lambda: resolve_game(mapping,dict(observations[0],world_id="B")))
    assert revisions[0]["score"] == 100 and revisions[1]["score"] == 102
    results.append({"id":s["id"],"result":"PASS","games":len(game_ids),"observations":len(observations),"revisions":len(revisions)})
    s = ss["S4_TOTAL_MISMATCH"]
    before=copy.deepcopy(s)
    total=sum(s["observed_game_points"])
    report={"observed":total,"native":s["native_season_points"],"difference":s["native_season_points"]-total,"coverage":"PARTIAL","status":"CONFLICT"}
    assert total == s["expected_observed_total"] and report["difference"] == s["expected_difference"]
    assert len(s["observed_game_points"]) == s["expected_games"] and s == before
    results.append({"id":s["id"],"result":"PASS",**report})
    s = ss["S5_HIDDEN_POTENTIAL"]
    positive={s["allowed_field"]:{"value":s["allowed_value"],"sensitivity":"PUBLIC"}}
    assert gm_project("A","A",True,positive) == {"points":25}
    for name in s["attacks"]:
        denied(lambda n=name:gm_project("A","A",True,{n:{"value":s["sensitive_value"]}}))
    denied(lambda:gm_project("A","A",True,{"points":{"value":s["nested_attack"]["points"]}}))
    denied(lambda:gm_project("A","A",True,{"points":{"value":99,"input_sensitivity":["HIDDEN_POTENTIAL"]}}))
    denied(lambda:gm_project("A","A",True,{"points":{"value":99,"sensitivity":"HIDDEN_POTENTIAL"}}))
    denied(lambda:gm_project("A","B",True,positive))
    denied(lambda:gm_project("A","A",False,positive))
    results.append({"id":s["id"],"result":"PASS","hidden_direct_nested_alias_derived":"REJECTED","allowed_points":25})
    s = ss["S6_SHARED_TEMPLATE"]
    template={"uid":s["template_id"]}
    for w in s["worlds"]:
        conceptual_link("DraftTemplate",template,"PlayerIncarnation",{"world_id":w})
    denied(lambda:conceptual_link("DraftTemplate",dict(template,memory="A private memory"),"PlayerIncarnation",{"world_id":"B"}))
    careers={("A","p23"):s["world_A_points"],("B","p23"):s["world_B_points"]}
    assert careers[("A","p23")] == 1000 and careers[("B","p23")] == 200
    denied(lambda:conceptual_link("PlayerIncarnation",{"world_id":"A"},"CareerHistory",{"world_id":"B"}))
    denied(lambda:conceptual_link("Actor",{"world_id":"A"},"AgentDecision",{"world_id":"B"}))
    results.append({"id":s["id"],"result":"PASS","shared_static_template":True,"dynamic_inheritance":"REJECTED"})
    for row in results: print(json.dumps(row,ensure_ascii=False))
    print(json.dumps({"check":"SIX_SCENARIOS","status":"PASS","scenario_count":len(results),"evidence_scope":"SYNTHETIC_CONCEPTUAL_ONLY"}))

def links():
    import sys
    sys.path.insert(0,str(ROOT/"01_os/06_execution/task_discipline/packet_input"))
    from task_packet_input import read_packet
    packet=read_packet(RUN/"task_packet.yml").body
    assert packet["task_id"]=="WORLD-DATA-ARCH-01"
    changed=subprocess.check_output(["git","diff","--name-only","-z",BASE,"HEAD"],cwd=ROOT).decode().split("\0")
    changed=[p for p in changed if p]
    assert changed
    assert all(any(fnmatch.fnmatchcase(p,a) for a in packet["allowed_changed_paths"]) for p in changed), changed
    assert not any(p.endswith((".sqlite",".db",".bin")) for p in changed)
    assert not any(p.startswith("01_os/") and not p.startswith("01_os/07_content/_runs/run-20261022-world-data-arch-001/") for p in changed)
    subprocess.run(["git","diff","--check",BASE,"HEAD"],cwd=ROOT,check=True,capture_output=True)
    link_count=0
    for rel in changed:
        path=ROOT/rel
        if path.suffix!=".md" or not path.is_file() or path.name=="human_task.md": continue
        text=path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)",text):
            if "://" in target or target.startswith("#"): continue
            target=target.split("#",1)[0]
            if not target: continue
            assert (path.parent/target).resolve().is_file(), (rel,target)
            link_count+=1
    for name in NAMES:
        assert (D/name).is_file()
    backlog=strict_json(D/"NBA2K22_OS_TASK_BACKLOG_V1.json")
    tasks={t["id"]:t for t in backlog["tasks"]}
    assert len(tasks)==len(backlog["tasks"])
    active=set(); done=set()
    def visit(k):
        assert k not in active,"task dependency cycle"
        if k in done:return
        active.add(k)
        for dep in tasks[k]["depends_on"]: assert dep in tasks; visit(dep)
        active.remove(k);done.add(k)
    for k in tasks:visit(k)
    arch=tasks["WORLD-DATA-ARCH-01"]
    assert arch["state"]=="candidate_ready_for_independent_review"
    assert arch["candidate_branch"]=="task/world-data-arch-01"
    assert (ROOT/arch["completion_pointer"]).is_file()
    assert "season forks" not in arch["acceptance_gate"]
    v2=(D/"PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md").read_text(encoding="utf-8")
    for obsolete in ("多存档/分叉/赛季/批次","恢复或分叉代际","多存档分叉模型"):
        assert obsolete not in v2
    assert C["task_id"]==packet["task_id"]
    print(json.dumps({"check":"LINKS_AND_SCOPE","status":"PASS","changed_paths":len(changed),"local_links":link_count,"task_nodes":len(tasks)}))

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("check",choices=["catalog","scenarios","links"])
    args=parser.parse_args()
    {"catalog":catalog,"scenarios":scenarios,"links":links}[args.check]()
