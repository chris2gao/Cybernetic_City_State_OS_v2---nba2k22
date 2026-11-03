"""Prepare the exact script for review; this builder never attaches or calls."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from native_action import NativeActionRequest,NativeActionSpec
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--request',required=True);a=p.parse_args();root=Path(__file__).parent;out=Path(a.out)
request=NativeActionRequest.parse(json.loads(Path(a.request).read_text(encoding='utf-8')))
if request.team_id!=20 or request.defense!=13 or request.expected_before!=14:raise ValueError('first PoC only IND20 14->13->14')
subprocess.run([sys.executable,'-B','-X','utf8',str(root/'build_preflight_probe.py'),'--out',str(out),'--team',str(request.team_id)],check=True,capture_output=True)
source=(out/'native_preflight.js').read_text(encoding='utf-8');prefix=source.split('const events=[],errors=[],hooks=[];')[0]
prefix=prefix.replace('const plan=',"const poc={experiment_id:'EXP-NATIVE-ACTION-01',value:13,expected_before:14};\nconst plan=")
prefix=prefix.replace('let used=0;','Object.assign(plan,poc);let used=0;')
script=prefix+(root/'invoke_poc.js').read_text(encoding='utf-8');path=out/'invoke_poc.js'
if path.exists():raise FileExistsError('fresh invocation path required')
path.write_text(script,encoding='utf-8');sha=hashlib.sha256(path.read_bytes()).hexdigest()
package={'experiment_id':'EXP-NATIVE-ACTION-01','script_sha256':sha,'request':request.__dict__,'spec':NativeActionSpec().to_dict(),'maximum_native_calls':3,'calls':['native_service_on_private_shadow','native_service_on_IND_coach_target13','native_service_on_same_coach_restore14'],'game_native_calls_max':2,'approval_status':'PENDING_HUMAN_SPECIFIC_APPROVAL','saved_game_changes':0,'execute_command':'administrator run_rea_admin.ps1 with -ApprovalReceipt binding this exact script SHA; minimum DurationMs 2400'}
(out/'experiment_package.json').write_text(json.dumps(package,indent=2),encoding='utf-8')
print(json.dumps({'script_sha256':sha,'experiment_id':package['experiment_id'],'maximum_native_calls':3,'status':'PREPARED_NOT_EXECUTED'}))
