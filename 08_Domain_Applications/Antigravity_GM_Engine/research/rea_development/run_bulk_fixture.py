"""Actual REA mutation experiment in a disposable owned process, never the game."""
import argparse,ctypes,hashlib,json,os,subprocess,sys,time
from pathlib import Path

COUNT=4096
def expected(i,changed=False):
 value=i*3+(7 if changed else 0);generation=2 if changed else 1
 return [i+1,value,generation,((i+1)^value^generation)&0xffffffff]
def child():
 array=(ctypes.c_uint32*(COUNT*4))()
 for i in range(COUNT):array[i*4:i*4+4]=expected(i)
 print(json.dumps({'pid':os.getpid(),'address':hex(ctypes.addressof(array)),'count':COUNT,'stride':16}),flush=True)
 for line in sys.stdin:
  mode=line.strip()
  if mode=='quit':return
  changed=mode=='verify-applied'
  failures=[i for i in range(COUNT) if list(array[i*4:i*4+4])!=expected(i,changed)]
  print(json.dumps({'kind':mode,'matches':COUNT-len(failures),'mismatches':len(failures),'sha256':hashlib.sha256(bytes(array)).hexdigest()}),flush=True)

def probe_script(target,restore=False):
 return '''const target=__TARGET__,restore=__RESTORE__;if(Process.id!==target.pid)throw Error('owned PID changed');
const base=ptr(target.address),count=target.count,stride=16,bytes=count*stride;
if(count!==4096||bytes!==65536)throw Error('fixture shape');
const before=base.readByteArray(bytes),v=new DataView(before);let casChecks=0;
function expected(i,changed){const value=i*3+(changed?7:0),g=changed?2:1;return [i+1,value,g,((i+1)^value^g)>>>0];}
function matches(i,words){return words.every((x,k)=>v.getUint32(i*16+k*4,true)===x);}
let mismatchAbortProof=null;
if(!restore){const wrong=expected(0,false);wrong[1]++;mismatchAbortProof=!matches(0,wrong);if(!mismatchAbortProof)throw Error('negative CAS failed');}
// Entire plan is checked before the first write. This is not cross-process atomic CAS.
for(let i=0;i<count;i++){if(!matches(i,expected(i,restore)))throw Error('before mismatch at '+i);casChecks++;}
const desired=new ArrayBuffer(bytes),d=new DataView(desired);
for(let i=0;i<count;i++)expected(i,!restore).forEach((x,k)=>d.setUint32(i*16+k*4,x,true));
base.writeByteArray(desired);
const after=new DataView(base.readByteArray(bytes));let verified=0;
for(let i=0;i<count;i++){if(!expected(i,!restore).every((x,k)=>after.getUint32(i*16+k*4,true)===x))throw Error('readback mismatch');verified++;}
send({kind:restore?'owned-fixture-restored':'owned-fixture-bulk-applied',records:count,stride,cas_checks:casChecks,negative_cas_abort_no_write:mismatchAbortProof,verified,bytes_written:bytes,explicit_bytes_read:bytes*2,game_target:false});
'''.replace('__TARGET__',json.dumps(target)).replace('__RESTORE__','true' if restore else 'false')

def run(out):
 out.mkdir(parents=True,exist_ok=True)
 if (out/'bulk-fixture-results.json').exists():raise RuntimeError('use fresh output directory')
 process=subprocess.Popen([sys.executable,'-X','utf8',str(Path(__file__).resolve()),'--child'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 target=json.loads(process.stdout.readline());assert target['pid']==process.pid
 (out/'fixture-target.json').write_text(json.dumps(target,indent=2),encoding='utf-8')
 launcher=Path(os.environ['APPDATA'])/'npm/node_modules/rea-agents/scripts/rea.mjs'
 results=[]
 try:
  for tag,restore in [('apply',False),('restore',True)]:
   script=out/(tag+'.js');script.write_text(probe_script(target,restore),encoding='utf-8')
   started=time.monotonic()
   completed=subprocess.run(['C:/Program Files/nodejs/node.exe',str(launcher),'instrument-with-frida','attach',str(process.pid),'--script-file',str(script),'--duration-ms','500','--format','json'],capture_output=True,text=True,encoding='utf-8',timeout=25)
   (out/(tag+'-evidence.json')).write_text(completed.stdout,encoding='utf-8')
   (out/(tag+'-stderr.log')).write_text(completed.stderr,encoding='utf-8')
   if completed.returncode:raise RuntimeError(f'REA {tag} exit{completed.returncode}')
   evidence=json.loads(completed.stdout);native=evidence['normalized_result']
   errors=[m for m in native['messages'] if m['type']=='error']
   if errors:raise RuntimeError(json.dumps(errors))
   proof=next(m['payload'] for m in native['messages'] if m['type']=='send')
   assert proof['verified']==COUNT and proof['game_target'] is False and native['cleanup_error'] is None
   process.stdin.write('verify-original\n' if restore else 'verify-applied\n');process.stdin.flush()
   independent=json.loads(process.stdout.readline());assert independent['mismatches']==0
   results.append(dict(phase=tag,elapsed_ms=round((time.monotonic()-started)*1000),response_bytes=len(completed.stdout.encode()),evidence_id=evidence['evidence_id'],rea=proof,independent_child_check=independent,cleanup_error=native['cleanup_error']))
 finally:
  if process.poll() is None:
   process.stdin.write('quit\n');process.stdin.flush()
   try:process.wait(timeout=5)
   except subprocess.TimeoutExpired:process.terminate();process.wait(timeout=5)
 result={'scope':'DISPOSABLE_OWNED_FIXTURE_ONLY; NO_GAME_WRITES','count':COUNT,'phases':results,'owned_process_exit':process.returncode,'limitations':['fixture memory is deliberately quiescent; no concurrent game engine','whole-plan validation is not atomic native CAS','no allocator, native index, UI commit, persistence or game legality proof','Frida performs an actual write to the owned fixture']}
 (out/'bulk-fixture-results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(result))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--child',action='store_true');p.add_argument('--out');a=p.parse_args()
 if a.child:child()
 elif a.out:run(Path(a.out))
 else:p.error('--out required')
