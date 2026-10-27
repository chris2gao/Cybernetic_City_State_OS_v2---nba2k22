"""Verify bounded entry/return instrumentation in an owned native-ABI fixture."""
import argparse,ctypes,json,os,subprocess,sys,threading,time
from pathlib import Path

def child():
 callback=ctypes.CFUNCTYPE(ctypes.c_int32,ctypes.c_int32)
 @callback
 def reader(value):return value*2
 @callback
 def writer(value):return reader(value)+1
 stop=threading.Event()
 def worker():
  while not stop.wait(0.02):writer(21)
 thread=threading.Thread(target=worker,daemon=True);thread.start()
 print(json.dumps({'pid':os.getpid(),'writer':hex(ctypes.cast(writer,ctypes.c_void_p).value),'reader':hex(ctypes.cast(reader,ctypes.c_void_p).value)}),flush=True)
 sys.stdin.readline();stop.set();thread.join(timeout=2)

def run(out):
 out.mkdir(parents=True,exist_ok=True)
 if (out/'call-trace-results.json').exists():raise RuntimeError('fresh output required')
 process=subprocess.Popen([sys.executable,'-X','utf8',str(Path(__file__).resolve()),'--child'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 target=json.loads(process.stdout.readline());assert process.pid==target['pid']
 script='''const target=__TARGET__;if(Process.id!==target.pid)throw Error('fixture identity');let captured=0;const handles=[];
for(const name of ['writer','reader'])handles.push(Interceptor.attach(ptr(target[name]),{onEnter(args){this.keep=captured<16;if(this.keep){captured++;this.value=args[0].toInt32();this.thread=Process.getCurrentThreadId();}},onLeave(ret){if(this.keep)send({kind:'owned-call',name,argument:this.value,result:ret.toInt32(),thread_id:this.thread});}}));
setTimeout(()=>{for(const h of handles)h.detach();send({kind:'owned-trace-stop',entry_events:captured,game_target:false});},350);
'''.replace('__TARGET__',json.dumps(target))
 script_path=out/'trace.js';script_path.write_text(script,encoding='utf-8')
 launcher=Path(os.environ['APPDATA'])/'npm/node_modules/rea-agents/scripts/rea.mjs'
 start=time.monotonic()
 try:
  r=subprocess.run(['C:/Program Files/nodejs/node.exe',str(launcher),'instrument-with-frida','attach',str(process.pid),'--script-file',str(script_path),'--duration-ms','700','--format','json'],capture_output=True,text=True,encoding='utf-8',timeout=25)
  (out/'trace-evidence.json').write_text(r.stdout,encoding='utf-8');(out/'trace-stderr.log').write_text(r.stderr,encoding='utf-8')
  if r.returncode:raise RuntimeError('REA trace failed')
  e=json.loads(r.stdout);native=e['normalized_result'];assert native['cleanup_error'] is None
  assert not any(m['type']=='error' for m in native['messages'])
  calls=[m['payload'] for m in native['messages'] if m['type']=='send' and m['payload'].get('kind')=='owned-call']
  assert 4<=len(calls)<=16 and {c['name'] for c in calls}=={'writer','reader'}
  assert all(c['argument']==21 and c['result']==(43 if c['name']=='writer' else 42) for c in calls)
  result={'scope':'OWNED_FIXTURE_ONLY; NO_GAME_HOOKS','evidence_id':e['evidence_id'],'elapsed_ms':round((time.monotonic()-start)*1000),'events':calls,'cleanup_error':None,'limitations':['callbacks are controlled native ABI trampolines in Python/libffi','does not recover unknown game ABI or select safe game hook sites','does not prove native game write ownership']}
 finally:
  if process.poll() is None:process.stdin.write('quit\n');process.stdin.flush();process.wait(timeout=5)
 result['owned_process_exit']=process.returncode
 (out/'call-trace-results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in result.items() if k!='events'}|{'event_count':len(calls),'example_events':calls[:4]}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--child',action='store_true');p.add_argument('--out');a=p.parse_args()
 if a.child:child()
 elif a.out:run(Path(a.out))
 else:p.error('--out required')
