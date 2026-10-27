"""Candidate inventory only: string matches are never disabled-feature counts."""
import argparse,hashlib,json,re,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--exe',default='E:/Games/NBA 2K22/NBA2K22.exe');p.add_argument('--out',required=True);a=p.parse_args()
path=Path(a.exe);data=path.read_bytes();pe=struct.unpack_from('<I',data,60)[0];n=struct.unpack_from('<H',data,pe+6)[0];opt=struct.unpack_from('<H',data,pe+20)[0]
sections=[]
for i in range(n):
 h=pe+24+opt+i*40;vs,rva,size,off=struct.unpack_from('<IIII',data,h+8);sections.append((rva,size,off))
def get_rva(off):return next((r+off-o for r,s,o in sections if o<=off<o+s),None)
families={
 'halftime_show':r'HALF_?TIME|HALF.TIME.SHOW',
 'locker_room_coach':r'LOCKER_?ROOM',
 'sideline_interview':r'SIDELINE|INTERVIEW',
 'pregame_intro':r'PRE_?GAME|STARTING_?LINEUP|StartingLineup',
 'postgame':r'POST_?GAME|PLAYER_OF_THE_GAME|PLAYER.OF.THE.GAME',
 'player_information_graphics':r'PLAYER.?INFO|PLAYER.?STAT|STAT.?GRAPHIC|LOWER.?THIRD|LowerThird',
 'replay_highlights':r'REPLAY|HIGHLIGHT',
 'timeout_coach':r'TIMEOUT.*(?:COACH|HUDDLE)|COACH.*(?:HUDDLE|SPEECH)|HUDDLE',
 'ticker':r'TICKER',
 'arena_jumbotron':r'JUMBOTRON|SCORER_TABLE|SCOREBOARD',
 'crowd':r'CROWD|CHANT',
 'commentary_audio':r'COMMENTARY|COMMENTATOR|BROADCAST',
 'scorebug':r'SCOREBUG',
 'presentation_queue':r'PRESENTATION::DEFERRED|PRESENTATION_UPDATE',
 'physics_collision':r'PHYSICS_WORLD|COLLISION|BALL.*TRAJECTORY',
 'physics_animation':r'FOOTPLANT|IKSOLVER|RAGDOLL|CLOTH',
}
hits={key:[] for key in families}
for m in re.finditer(rb'[\x20-\x7e]{5,240}\x00',data):
 s=m.group()[:-1].decode('ascii')
 for key,pat in families.items():
  if re.search(pat,s,re.I):hits[key].append({'text':s,'rva':get_rva(m.start()),'mode_marker':next((v for v in ('MYCAREER','CAREERMODE','MYTEAM','HIGHSCHOOL','PARK','FRANCHISE') if v in s.upper()),'UNCLASSIFIED')})
catalog=[]
for key,rows in hits.items():
 examples=sorted(rows,key=lambda r:(0 if r['text'].lower().endswith('.iff') else 1,0 if '::' in r['text'] else 1,len(r['text'])))[:12]
 catalog.append(dict(family=key,matching_literal_occurrences=len(rows),unique_literal_texts=len({r['text'] for r in rows}),examples=examples,status='STATIC_CANDIDATE_ONLY',currently_enabled=None,hidden_or_disabled=None,injectable_in_game=None))
files=[]
for directory in (path.parent,path.parent/'Mods'):
 if directory.is_dir():
  for f in directory.glob('*.iff'):
   if re.search(r'half|interview|pregame|postgame|score|overlay|lineup|crowd|presentation|jumb|ticker',f.name,re.I):
    files.append({'scope':directory.name,'name':f.name,'size':f.stat().st_size})
header_path=path.parent/'0A'
header=header_path.open('rb').read(32).hex() if header_path.exists() else None
result={'exe_sha256':hashlib.sha256(data).hexdigest(),'coverage':'ASCII nul-terminated5..240 bytes in fixed EXE plus root/Mods top-level filename-only .iff search; packaged assets not decoded','families':catalog,'matching_top_level_iff_files':files,'root_0A_first32_hex':header,'asset_container_status':'UNKNOWN_CUSTOM_CONTAINER; no whole-archive import or extraction attempted','disabled_feature_count':None,'runtime_enabled_feature_count':None,'game_information_injection_verified':False,'limitations':['families overlap; literal count is not feature count','old-version/mode labels may be legacy or shared','calendar context cannot demonstrate match execution','no inference of absent or disabled functionality from zero matches']}
Path(a.out).write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'family_counts':{r['family']:r['unique_literal_texts'] for r in catalog},'iff_candidate_count':len(files),'iff_examples':files[:8],'disabled_feature_count':None,'asset_status':result['asset_container_status']}))
