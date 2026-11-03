import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();root=Path(__file__).parent;profile=json.loads((root.parents[1]/'config/memory_field_profile.json').read_text(encoding='utf-8'))
contract=[f for f in profile['fields']['PLAYER'] if f['group']=='contract'];plan={'contract_fields':contract,'target_team_ids':[1,2],'read_budget':262144}
source=root.with_name('rea_native_action')/'trade_observe.js';out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'trade_observe.js').write_text(source.read_text(encoding='utf-8').replace('__PLAN__',json.dumps(plan,separators=(',',':'))),encoding='utf-8');print(json.dumps({'selected_teams':[1,2],'core_roster_limit':30,'player_limit_per_team':15,'read_budget':262144,'native_calls':0}))
