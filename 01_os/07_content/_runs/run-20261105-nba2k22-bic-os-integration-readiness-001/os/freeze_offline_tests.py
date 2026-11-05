"""Technical content freeze only; does not grant formal stage owner acceptance."""
import hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
BASE='cdcb293f8a690725cf9168225cc2046ab0574b2b'
D='08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/'
names=['test_bic_baseline.py','test_bic_experiments.py','test_observation_scope.py','test_player_details.py','test_bic_remediation.py','test_bic_wave2.py','test_bic_wave2_remediation.py']
rows=[]
for index,name in enumerate(names,1):
    path=D+'tests/'+name
    raw=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+path])
    rows.append({'test_id':f'OFFLINE-{index:02d}','path':path,'source_commit':BASE,'sha256':hashlib.sha256(raw).hexdigest()})
encoded=json.dumps(rows,sort_keys=True,separators=(',',':')).encode()
package={'technical_freeze_at':datetime.now(timezone.utc).isoformat(),'source_commit':BASE,'tests':rows,'package_sha256':hashlib.sha256(encoded).hexdigest(),'digest_algorithm':'SHA256 UTF8 compact JSON sorted keys over tests only','technical_content_frozen':True,'formal_stage04_freeze_approved':False,'freeze_authorization_ref':None,'prior_runs':'41 and 65 test archives predate this technical freeze; never represented as post-freeze results','purpose':'Prospective integration regression on unchanged reviewed offline code only'}
(OUT/'TECHNICAL_TEST_FREEZE.json').write_text(json.dumps(package,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'path':str(OUT/'TECHNICAL_TEST_FREEZE.json'),'package_sha256':package['package_sha256']}))
