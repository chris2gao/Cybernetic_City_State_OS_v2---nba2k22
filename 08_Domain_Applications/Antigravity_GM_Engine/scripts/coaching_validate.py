"""Offline native coaching proposal preparation/validation. No game handles."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot",required=True)
    p.add_argument("--proposal",help="Validate an existing exact proposal")
    p.add_argument("--team-id",type=int)
    p.add_argument("--opponent-team-id",type=int)
    p.add_argument("--set",action="append",default=[],metavar="NATIVE_FIELD=RAW_INTEGER")
    p.add_argument("--decision-id")
    p.add_argument("--version",type=int,default=1)
    p.add_argument("--action-id")
    p.add_argument("--expected-effect")
    p.add_argument("--output",help="Save generated PROPOSED JSON under _exports")
    a=p.parse_args()
    from coaching_cli import load_json,write_json
    from gm_core.coaching import propose,validate_plan
    snapshot=load_json(a.snapshot)
    if a.proposal:
        if a.set or a.output:
            p.error("--proposal is validation only; do not combine with --set/--output")
        plan=load_json(a.proposal)
    else:
        if any(v is None for v in (a.team_id,a.decision_id,a.action_id,a.expected_effect,a.output)) or not a.set:
            p.error("Preparation needs team, decision, action, expected-effect, --set and --output")
        targets={}
        for spec in a.set:
            field,value=spec.split("=",1)
            if field in targets:
                p.error("Duplicate field")
            targets[field]=int(value,0)
        plan=propose(snapshot,a.team_id,targets,a.decision_id,a.version,a.action_id,a.expected_effect,a.opponent_team_id)
        write_json(a.output,plan)
    result=validate_plan(plan,snapshot)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["valid"] else 2

if __name__=="__main__":
    raise SystemExit(main())
