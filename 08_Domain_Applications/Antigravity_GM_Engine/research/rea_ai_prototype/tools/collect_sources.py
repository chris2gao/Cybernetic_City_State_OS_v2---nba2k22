"""Resolve selected immutable Git sources; no copying the prior 52-file archive."""
import argparse,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[5]
D='08_Domain_Applications/Antigravity_GM_Engine/'
BASE='4dbfde51bda76a3dbb3454d5ae42135592c8332e';OLD='b16e69727987f29bff5e2ee31ce82891102ab2d9'
prior='01_os/07_content/_runs/run-20261027-rea-development-exploration-01/06_执行/evidence/'
spec=[('SRC-COACH-PROFILE',BASE,D+'config/coach_tactics_profile.json','PROJECT_GUIDE','LEGACY_COACH_PROJECT_SINGLE_ORIGIN'),('SRC-COACH-READER',BASE,D+'src/coaching_reader.py','PROJECT_GUIDE','LEGACY_COACH_PROJECT_SINGLE_ORIGIN'),('SRC-COACH-CODEC',BASE,D+'src/coach_codec.py','PROJECT_GUIDE','LEGACY_COACH_PROJECT_SINGLE_ORIGIN'),('SRC-TRADE-EXECUTOR',BASE,D+'src/approved_trade_executor.py','PROJECT_GUIDE','LEGACY_TRADE_PROJECT_SINGLE_ORIGIN'),('SRC-R05B-TRADE',BASE,D+'docs/game_mechanics/catalogs/R05B_TRADE_PICK_ROSTER_MECHANICS_V1.json','PROJECT_GUIDE','DEV29_GUIDE_SINGLE_ORIGIN'),('SRC-R04A-BADGES',BASE,D+'docs/game_mechanics/catalogs/PLAYER_BADGES_R04_A_REFERENCE.json','PROJECT_GUIDE','DEV29_GUIDE_SINGLE_ORIGIN'),('SRC-R03-MENTOR',BASE,D+'docs/game_mechanics/guides/K06_TRAINING_HEALTH_GROWTH.md','PROJECT_GUIDE','DEV29_GUIDE_SINGLE_ORIGIN'),('SRC-PRIOR-METADATA',OLD,prior+'metadata-findings.json','REAL_GAME_ARCHIVED_TYPE_DEFINITIONS','CODEX_PRIOR_SINGLE_RUN'),('SRC-PRIOR-GROWTH',OLD,prior+'growth-findings.json','REAL_GAME_ARCHIVED_TYPE_DEFINITIONS','CODEX_PRIOR_SINGLE_RUN')]
rows=[];observations={}
for identity,commit,path,kind,origin in spec:
 raw=subprocess.check_output(['git','show',commit+':'+path],cwd=repo)
 blob=subprocess.check_output(['git','rev-parse',commit+':'+path],cwd=repo).decode().strip()
 rows.append({'source_id':identity,'commit':commit,'path':path,'git_blob':blob,'sha256':hashlib.sha256(raw).hexdigest(),'kind':kind,'origin_group':origin,'first_hand_this_task':False,'url':f'https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/{commit}/{path}'})
 if identity=='SRC-COACH-PROFILE':
  profile=json.loads(raw);observations['coach_fields']={key:profile['fields'][key] for key in ('POEDefense','POEOffense')};observations['historical_effect_status']=profile['effect_status']
 if identity.startswith('SRC-PRIOR-'):
  native=json.loads(raw)['observation']['types'];selected={}
  for t in native:
   if t['name'] in {'FRANCHISE_MENTOR::BADGE','FRANCHISE_MENTOR::MENTOR','FRANCHISE_PROGRESSION_TUNING','BADGE_TUNING::COMMON_SPOT_UP','BADGE_TUNING::SHOOTING_BADGES'}:
    selected[t['name']]={'field_count':t['count'],'field_names':[f['name_candidates'] for f in t['fields']]}
  observations[identity]=selected
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
(out/'source_registry.json').write_text(json.dumps({'sources':rows,'observations':observations,'limitations':['archived records do not become new live observations','same origin stays one origin regardless of file count','profile writable/production flags are historical engineering declarations, not current AI eligibility']},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'sources':len(rows),'prior_archive_files_copied':0,'coach_field_names':list(observations['coach_fields']),'effect_status':observations['historical_effect_status']}))
