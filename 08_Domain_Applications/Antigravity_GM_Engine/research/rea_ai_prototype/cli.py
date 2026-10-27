"""Run from any cwd. All execution in this prototype is offline, never live game."""
import argparse,json,sys
from pathlib import Path
from prototype import Intent,KnowledgeStore,NativeBackend,OwnedFixture,Router,ValidatedMemoryBackend,fixture_intent

def examples():
 cases=[]
 def case(name,router,intent,expected):
  receipt=router.act(intent);assert receipt['result']==expected,(name,receipt)
  cases.append({'case':name,'receipt':receipt})
 case('native-candidate-context-missing-memory-fixture',Router(OwnedFixture()),fixture_intent(),'FIXTURE_ONLY_PASS')
 case('native-first-fixture-model',Router(OwnedFixture(),NativeBackend(True)),fixture_intent(),'FIXTURE_ONLY_PASS')
 case('knowledge-with-no-safe-executor',Router(),fixture_intent(environment='REAL_GAME',build='PC22_CURRENT_BUILD_UNVERIFIED',permission_ref=None),'NOT_EXECUTED')
 case('both-fixture-paths-unqualified',Router(OwnedFixture(),NativeBackend(False),ValidatedMemoryBackend(False)),fixture_intent(),'NOT_EXECUTED')
 case('declared-side-effects-disagree',Router(OwnedFixture(),NativeBackend(True),ValidatedMemoryBackend(True,fault='extra_effect_contract')),fixture_intent(),'NOT_EXECUTED')
 case('shared-word-corruption',Router(OwnedFixture(),memory=ValidatedMemoryBackend(True,fault='whole_word')),fixture_intent(),'FAILED_READBACK')
 case('cache-not-refreshed',Router(OwnedFixture(),memory=ValidatedMemoryBackend(True,fault='missing_cache')),fixture_intent(),'FAILED_READBACK')
 case('native-partial-failure-no-auto-memory',Router(OwnedFixture(),NativeBackend(True,fault='after_write')),fixture_intent(),'EXECUTED_BUT_UNVERIFIED')
 case('stale-revision',Router(OwnedFixture()),fixture_intent(expected_revision=0),'NOT_EXECUTED')
 case('build-difference',Router(OwnedFixture()),fixture_intent(build='OTHER_BUILD'),'NOT_EXECUTED')
 case('engine-human-flag',Router(OwnedFixture()),fixture_intent(initiator={'id':'coach:A','role':'COACH','engine_control':'HUMAN_CONTROLLED'}),'NOT_EXECUTED')
 trade={'action_id':'trade-human-negative','action_type':'GM_AI_AI_TRADE','initiator':{'id':'gm:A','role':'GM','engine_control':'AI_CONTROLLED'},'counterparty':{'id':'gm:B','role':'GM','engine_control':'HUMAN_CONTROLLED'},'environment':'REAL_GAME','build':'UNVERIFIED','mode':'PC22_OFFLINE_MYLEAGUE','save_id':'unbound-save','scene_id':'unbound-scene','target_ids':['team:A','team:B'],'arguments':{'player_ids':['player:1'],'pick_ids':[]},'expected_revision':1,'permission_ref':None}
 case('human-trade-path-excluded',Router(),Intent.parse(trade),'NOT_EXECUTED')
 return cases

def main():
 parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
 knowledge=sub.add_parser('knowledge');ks=knowledge.add_subparsers(dest='operation',required=True)
 show=ks.add_parser('show');show.add_argument('mechanism_id');show.add_argument('--role',choices=['GM','COACH','PLAYER'],required=True);show.add_argument('--mode',default='PC22_OFFLINE_MYLEAGUE')
 listing=ks.add_parser('list');listing.add_argument('--role',choices=['GM','COACH','PLAYER'],required=True)
 action=sub.add_parser('action');action.add_argument('operation',choices=['assess','simulate']);action.add_argument('--intent',required=True);action.add_argument('--backend',choices=['memory-model','native-model','none'],default='none')
 demo=sub.add_parser('demo');demo.add_argument('--verify',action='store_true');demo.add_argument('--output')
 args=parser.parse_args()
 if args.command=='knowledge':
  store=KnowledgeStore();result=store.show(args.mechanism_id,args.role,args.mode) if args.operation=='show' else store.query(args.role)
 elif args.command=='action':
  intent=Intent.parse(json.loads(Path(args.intent).read_text(encoding='utf-8')))
  fixture=OwnedFixture() if args.backend!='none' else None
  router=Router(fixture,NativeBackend(args.backend=='native-model')) if fixture else Router()
  result=router.assess(intent) if args.operation=='assess' else router.act(intent)
 else:
  cases=examples();guide=KnowledgeStore().show('AI_COACH_DEFENSE_M1','COACH')
  result={'scope':'OFFLINE_PROTOTYPE_ONLY','knowledge':guide,'cases':cases,'game_operations':0,'live_adapter_installed':False,'overall_result':'DEMO_CONTRACT_VERIFIED'}
  if args.output:
   path=Path(args.output)
   with path.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
  result={'scope':result['scope'],'knowledge':{'mechanism_id':guide['mechanism_id'],'can_reason':guide['can_reason'],'can_execute':guide['can_execute'],'actor_scope_verdict':guide['actor_scope_verdict']},'cases':[{'case':c['case'],'route':c['receipt']['route'],'result':c['receipt']['result'],'game_target':c['receipt']['game_target'],'reasons':c['receipt']['reasons']} for c in cases],'game_operations':0,'live_adapter_installed':False,'overall_result':result['overall_result']}
 print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
 try:main()
 except (ValueError,PermissionError,KeyError,FileNotFoundError) as error:
  print(json.dumps({'result':'INPUT_OR_VISIBILITY_REJECTED','reason':str(error),'game_target':False},ensure_ascii=False));sys.exit(2)
