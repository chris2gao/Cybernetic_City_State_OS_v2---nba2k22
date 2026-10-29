"""Bounded decision-information literals and confirmed RIP LEA references; PE only."""
import argparse,json,re,struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'rea_native_action'))
from pe_local import Image

QUERIES={
 'advanced_statistics':r'^(?:STAT_(?:CalculatedPossessions|[A-Za-z0-9_]*(?:PER|TrueShooting|EffectiveFieldGoal|OffensiveRating|DefensiveRating|NetRating))|Simulator_GetTeamPaceConstant|[A-Za-z0-9_:]*(?:Get|Calculate|Compute|Calc)(?:TrueShooting|EffectiveFieldGoal|OffensiveRating|DefensiveRating|NetRating|Efficiency|Usage|Possessions|Pace|WinShares)[A-Za-z0-9_]*)$',
 'game_and_season_statistics':r'^(?:(?:PLAYER|TEAM|SEASON|SCHEDULE|GAME|BOX_SCORE|BOXSCORE)[A-Za-z_:]*(?:Get|Find|Read)[A-Za-z_:]*(?:Stat|Box|Score|Game|Season|Schedule)|Franchise_(?:Get|Stats_)[A-Za-z_:]*(?:Stat|Box|Score|Game|Season|Schedule))',
 'opponent_and_team_information':r'^(?:(?:FRANCHISE_GAMEPLAN_MANAGER|GAMEPLAN_MANAGER|COACHDATA|TEAMDATA)::(?:Get|Find|Read)|Franchise_(?:Gameplan|Team|Opponent)_(?:Get|Find|Read))',
 'tracking_and_shot_information':r'(?:Get|Calculate|Compute)[A-Za-z0-9_:]*(?:ShotChart|ShotZone|ShotLocation|LineupStat|OnOff|MatchupStat|DefensiveFG|PlayByPlay)',
 'registered_stat_objects':r'^[A-Z0-9_]*(?:SHOTCHART|STATDATA)[A-Z0-9_]*$'
}

def recover(image,per_group=64,reference_limit=128):
 rdata=image.section('.rdata');compiled={key:re.compile(pattern,re.I) for key,pattern in QUERIES.items()}
 selected={key:[] for key in QUERIES};counts={key:0 for key in QUERIES};by_rva={}
 for match in re.finditer(rb'[\x20-\x7e]{5,220}\x00',image.data[rdata['raw']:rdata['raw']+rdata['size']]):
  literal=match.group()[:-1].decode('ascii');rva=rdata['rva']+match.start()
  for group,pattern in compiled.items():
   if not pattern.search(literal):continue
   counts[group]+=1
   if len(selected[group])<per_group:
    selected[group].append({'rva':rva,'literal':literal});by_rva.setdefault(rva,[]).append(group)
 text=image.read(image.text['rva'],image.text['size']);references={key:[] for key in QUERIES};unconfirmed=[];cache={};overflow={key:0 for key in QUERIES}
 for match in re.finditer(rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]....',text,re.S):
  site=image.text['rva']+match.start();target=site+7+struct.unpack_from('<i',match.group(),3)[0]
  if target not in by_rva:continue
  chain=image.unwind_chain(site)
  if not chain or chain[0]['end']-chain[0]['begin']>24576:
   if len(unconfirmed)<24:unconfirmed.append({'site_candidate_rva':site,'literal_rva':target,'reason':'NO_UNWIND_OR_OVERSIZED_FRAGMENT'})
   continue
  lo,hi=chain[0]['begin'],chain[0]['end']
  if (lo,hi) not in cache:cache[lo,hi]=image.instruction_rows(lo,hi)
  rows=cache[lo,hi];at=next((i for i,row in enumerate(rows) if row['rva']==site and row['mnemonic']=='lea'),None)
  if at is None:continue
  for group in by_rva[target]:
   if len(references[group])>=reference_limit:overflow[group]+=1;continue
   references[group].append({'literal_rva':target,'site_rva':site,'primary_rva':chain[-1]['begin'],
    'instruction_boundary_confirmed':True,'window':rows[max(0,at-5):at+8]})
 return {'source_kind':'PINNED_PE_DECISION_INFORMATION_LEADS_NOT_REA_PROVIDER','game_build_sha256':image.sha256,
  'game_access':False,'queries':QUERIES,'groups':{key:{'matching_literals':counts[key],'selected_literals':selected[key],
   'selection_truncated':counts[key]>len(selected[key]),'references':references[key],'omitted_reference_count':overflow[key]} for key in QUERIES},
  'limits':{'per_group_literals':per_group,'per_group_references':reference_limit,'fragment_bytes':24576},
  'unconfirmed_candidates':unconfirmed,
  'qualification':'Names/references are discovery leads only; getter ABI, exact stat definition, input context and live values require separate evidence'}

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args();out=Path(args.out)
 if out.exists():raise SystemExit('Existing evidence is immutable; select a new output')
 data=recover(Image());out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')
 for key,group in data['groups'].items():
  print(json.dumps({'group':key,'matching':group['matching_literals'],'truncated':group['selection_truncated'],
   'references':len(group['references']),'omitted_references':group['omitted_reference_count'],
   'literals':[row['literal'] for row in group['selected_literals']]}))
