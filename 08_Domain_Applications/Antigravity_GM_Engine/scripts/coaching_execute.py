"""Default offline dry-run. Explicit exact external approval is required for live execution."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot",required=True)
    p.add_argument("--proposal",required=True)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument("--execute",action="store_true")
    mode.add_argument("--rollback",action="store_true")
    p.add_argument("--approve-career-id")
    p.add_argument("--approve-decision-id")
    p.add_argument("--approve-version",type=int)
    p.add_argument("--approve-action-id",action="append",default=[])
    p.add_argument("--approve-plan-digest")
    p.add_argument("--test-save-confirmed",action="store_true")
    p.add_argument("--coach-editor-closed",action="store_true",
                   help="Operator confirms player has left Coach Gameplan; open editor can overwrite live memory")
    p.add_argument("--state-root",default=str(Path(__file__).resolve().parents[1]/"_exports/coaching_execution"))
    p.add_argument("--output",help="Local receipt JSON under _exports")
    a=p.parse_args()
    from coaching_cli import load_json,export_path,write_json
    from coaching_executor import CoachingExecutor,PlayerApproval
    plan,snapshot=load_json(a.proposal),load_json(a.snapshot)
    executor=CoachingExecutor()
    output=export_path(a.output) if a.output else None
    if a.execute or a.rollback:
        state_root=export_path(a.state_root)
        approval=PlayerApproval(a.approve_career_id,a.approve_decision_id,a.approve_version,
                                tuple(a.approve_action_id),a.approve_plan_digest,a.test_save_confirmed,a.coach_editor_closed)
        result=executor.run(plan,snapshot,approval,state_root,a.rollback)
    else:
        result=executor.inspect(plan,snapshot)
    if output:
        write_json(output,result)
    # Runtime addresses remain in local journals, never printed as a shareable receipt.
    public={k:v for k,v in result.items() if k!="runtime_local_only"}
    print(json.dumps(public,ensure_ascii=False,indent=2))
    return 0 if result.get("valid",True) else 2

if __name__=="__main__":
    raise SystemExit(main())
