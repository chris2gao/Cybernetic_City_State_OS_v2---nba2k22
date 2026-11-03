"""Inert catalog/plan/source emission CLI. Deliberately no execute command in this task."""
import argparse,json
from pathlib import Path
from contracts import NativeActionRequest
from facade import NativeControlFacade
p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True);c=s.add_parser('catalog');c.add_argument('--domain');c=s.add_parser('plan');c.add_argument('--request',required=True);c=s.add_parser('emit');c.add_argument('--request',required=True);c.add_argument('--out',required=True);a=p.parse_args()
f=NativeControlFacade()
if a.command=='catalog':print(json.dumps(f.registry.list(a.domain),ensure_ascii=False,indent=2))
else:
 d=json.loads(Path(a.request).read_text(encoding='utf-8'));r=NativeActionRequest(d['action_id'],d['parameters'],d.get('request_id',''))
 if a.command=='plan':print(json.dumps(f.prepare(r).to_dict(),ensure_ascii=False,indent=2))
 else:
  program=f.render(r);out=Path(a.out)
  if out.exists():raise FileExistsError('Fresh source output required')
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(program.script,encoding='utf-8');print(json.dumps({'status':'SOURCE_PREPARED_NOT_EXECUTED','action_id':program.action_id,'maximum_game_calls':program.maximum_game_calls}))
