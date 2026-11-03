"""Bounded nine-domain ASCII/RIP-xref discovery from the pinned PC22 file only."""
import argparse,json,re,struct,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'rea_native_action'))
from pe_local import Image
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--per-domain',type=int,default=90);p.add_argument('--focused',action='store_true');p.add_argument('--operations',action='store_true');a=p.parse_args();im=Image();start=time.monotonic()
if not 1<=a.per_domain<=160:raise ValueError('Bounded domain cap required')
queries={
 'D02':r'(Franchise_.*(?:Sign|Contract|Option|Waiv|Release)|(?:Sign|Waive|Release|Extend|ContractOption).*(?:Player|Contract)|FREEAGENCY::|CONTRACT::)',
 'D03':r'((?:PLAYER|PLAYERDATA|COACHDATA|STAFF|PLAYEREDITOR)::.*(?:Set|Apply)|(?:Set|Edit|Modify|Adjust|Apply).*(?:Attribute|Tendency|Badge|PlayType)|Player_(?:Set|Edit))',
 'D04':r'(GAMEPLAN_MANAGER::|COACH::|(?:Set|Apply|Add|Replace|Remove).*(?:Gameplan|Playbook|Freelance|POE|ACE)|Playbook_.*(?:Set|Add|Remove))',
 'D05':r'(Franchise_.*(?:Roster|Staff|Coach|Lineup)|(?:Set|Apply|Swap|Adjust).*(?:Rotation|Minutes|Lineup|Starter|Position|Role)|(?:Hire|Fire).*(?:Coach|Staff)|ROSTER::)',
 'D06':r'(Draft_(?:Draft|Select|Set|Get)|FRANCHISE_DRAFT::|(?:Set|Add|Transfer).*DraftPick)',
 'D07':r'(FRANCHISE_TRAINING::|(?:Set|Apply|Assign|Get).*(?:Training|Mentor)|Franchise_.*(?:Training|Mentor))',
 'D08':r'(Franchise_.*(?:Get|Find).*(?:Stat|History|Calendar|Award|Game|Finance)|(?:Get|Find).*(?:PlayerStats|TeamStats|Standings|SeasonStats|CareerStats)|ROSTERDATA::)',
 'D09':r'(Franchise_.*Scout|(?:Set|Assign|Add|Remove|Get|Update|Clear).*(?:Scout|Prospect)|(?:SCOUT|SCOUTING|SCOUTINGREPORT)::)',
 'EXTRA':r'(Franchise_.*(?:Injur|Suspend|Retire|Progress|Advance|Expansion)|(?:Set|Apply|Update).*(?:Morale|Fatigue|Injury)|Trade_.*AddPick)'}
if a.focused:queries={
 'D02':r'^(?:Franchise_(?:Sign|Contract|PlayerContract|Option|Waive|Release)_|FRANCHISE_SIGNING::|FRANCHISE_COACH::Sign)',
 'D03':r'^(?:(?:PLAYER|PLAYERDATA|COACHDATA|STAFF)::(?:Set|Apply|Adjust|Modify)|.*PLAYER_EDITOR::(?:Save|Apply)|(?:PlayerEditor|PlayerAttribute|PlayerTendency|PlayerBadge|PlayerPlayType)_).*',
 'D04':r'^(?:(?:FRANCHISE_GAMEPLAN_MANAGER|FRANCHISE_PLAYBOOK|GAMEPLAN_MANAGER|PLAYBOOK)::|Franchise_(?:Gameplan|Playbook)_).*',
 'D05':r'^(?:Franchise_(?:Team|Roster|Lineup|Staff)_(?:Set|Apply|Assign|Remove|Add|Swap)|(?:TEAMDATA|ROSTER|ROTATION)::(?:Set|Apply|Assign|Remove|Add|Swap)).*',
 'D07':r'^(?:FRANCHISE_TRAINING::(?:Set|Get|Apply)|FRANCHISE_MENTOR::MANAGER::|Franchise_Training_).*',
 'D09':r'^(?:FRANCHISE_SCOUT::|Franchise_Scout_).*',
 'D01':r'^Franchise_Trade_Add.*'}
if a.operations:queries={
 'D03':r'(?:(?:Set|Apply|Assign|Modify|Edit).*(?:Badge|Tendency|PlayType|PlayerAttribute|PlayerRating)|(?:Badge|Tendency|PlayType|PlayerAttribute|PlayerRating).*(?:Set|Apply|Assign|Modify))',
 'D05':r'(?:(?:Set|Apply|Assign|Swap|Add|Remove).*(?:Rotation|Minutes|Lineup|Starter|Roster|Position|Staff)|(?:Rotation|Minutes|Lineup|Starter|Roster).*(?:Set|Apply|Assign|Swap))',
 'D04':r'(?:(?:Set|Apply|Assign|Add|Remove).*(?:Playbook|Freelance|Gameplan|System|Scheme)|(?:Playbook|Freelance|Gameplan).*(?:Set|Apply|Assign|Add|Remove))',
 'D07':r'(?:Training.*(?:Set|Apply|Assign|Change)|(?:Set|Apply|Assign|Change).*Training)',
 'D08':r'(?:Get|Read|Find).*(?:CareerStats|SeasonStats|TeamStats|PlayerStats|Award|Standings|History|Calendar)',
 'EXTRA':r'^Franchise_Player_(?:Retire|Waive|Release|Set)|^Franchise_Team_.*(?:Waive|Release)'}
compiled={k:re.compile(v,re.I) for k,v in queries.items()};rd=im.section('.rdata');rows={k:[] for k in queries};by_rva={}
for m in re.finditer(rb'[\x20-\x7e]{5,240}\x00',im.data[rd['raw']:rd['raw']+rd['size']]):
 literal=m.group()[:-1].decode('ascii');rv=rd['rva']+m.start()
 for domain,pattern in compiled.items():
  if len(rows[domain])<a.per_domain and pattern.search(literal):
   row={'rva':rv,'literal':literal,'domain':domain};rows[domain].append(row);by_rva.setdefault(rv,[]).append(row)
refs=[];text=im.read(im.text['rva'],im.text['size'])
for m in re.finditer(rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]....',text,re.S):
 rv=im.text['rva']+m.start();target=rv+7+struct.unpack_from('<i',m.group(),3)[0]
 if target not in by_rva:continue
 chain=im.unwind_chain(rv)
 for row in by_rva[target]:refs.append({**row,'instruction_rva':rv,'unwind_chain':chain,'primary_rva':chain[-1]['begin'] if chain else None})
 if len(refs)>=1400:break
result={'source_kind':'STATIC_PC22_PE_FILE_NO_TARGET_EXECUTION','game_build_sha256':im.sha256,'queries':queries,'strings':rows,'references':refs,'bounds':{'per_domain_strings':a.per_domain,'references':1400},'limitations':['ASCII name and RIP-relative reference are leads, not ABI or executed effect proof','unwind fragments require chain recovery','string caps may omit other operations'],'elapsed_ms':round((time.monotonic()-start)*1000)}
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'surface_discovery.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'elapsed_ms':result['elapsed_ms'],'domains':{k:{'strings':len(v),'refs':sum(r['domain']==k for r in refs)} for k,v in rows.items()},'references':len(refs),'game_access':False}))
