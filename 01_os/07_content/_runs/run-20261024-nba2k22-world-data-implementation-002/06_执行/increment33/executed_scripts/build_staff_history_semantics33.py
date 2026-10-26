import json
from pathlib import Path
r=Path(__file__).parent;app=Path.cwd()/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype';functions=json.loads((r/'staff-history-functions33.json').read_bytes());setter=json.loads((r/'staff-history-setter33.json').read_bytes());base=json.loads((app/'staff_history_native_profile.json').read_bytes())
proofs=[]
for value in functions+setter:
    if value['rva'] in {p['rva'] for p in proofs}:continue
    proofs.append({k:value[k] for k in ('rva','code_hex','sha256')})
profile={'format_version':1,'rule':'NATIVE_COACH_STAT_STORAGE_ROLES_V1','compatible_source_decoder':base['layout'],'pe_timestamp':1652287197,'increment_target_position':0,'clear_function_positions':list(range(39)),'last_position':39,'next_free_allocation_marker':65535,'code_proofs':proofs,'limits':['Position0 is the Native stat read/add/write target; calendar year, phase and finalization are not established by this role.','Cleanup visits positions0..38; the meaning of untouched position39 is UNKNOWN, not assumed to be career totals.','NextFree65535 matches the marker written when a node is removed from the free list and tested before reinsertion. A marker is not free-list reachability, ownership or historical person proof.','Derived query annotations preserve original raw values and stored stat_year=NULL. No getter or mutator is invoked.']}
(app/'staff_history_semantics_native_profile.json').write_text(json.dumps(profile,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({'code_windows':len(proofs),'bytes':sum(len(bytes.fromhex(p['code_hex'])) for p in proofs),'year_mapping':None}))
