import argparse,json,re,struct,zlib
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--exe',default='E:/Games/NBA 2K22/NBA2K22.exe');p.add_argument('--out',required=True);p.add_argument('--mode',choices=['metadata','growth','presentation'],default='metadata')
a=p.parse_args();source=json.loads(Path(a.source).read_text());data=Path(a.exe).read_bytes()
exact={'FRANCHISE_MENTOR::BADGE','FRANCHISE_MENTOR::MENTEE','FRANCHISE_MENTOR::MENTOR','FRANCHISE_MENTOR::MANAGER','FRANCHISE_TICKER_SETTINGS','STADIUMDATA','GLOBALDATA','TUNEDATA','AI_BADGE_MANAGER','AI_BADGE_BASE','PRESENTATION_TUNING','PRESENTATION_TUNING::CROWD','FRANCHISE_TICKER_TUNING','FRANCHISE_TICKER_TUNING::STAT_VALUE'}
available=[r for r in source['relevant_registrations'] if r['kind']=='struct']
extra=[r for r in available if re.search(r'^PRESENTATION::|HALFTIME|SCOREBUG|OVERLAY',r['name'])]
chosen=[r for r in available if r['name'] in exact]+extra[:12]
if a.mode=='growth':
 exact={'FRANCHISE_PROGRESSION_PHASE_TABLE','FRANCHISE_PROGRESSION_TUNING','BADGE_TUNING','BADGE_TUNING::SHOOTING_BADGES','BADGE_TUNING::COMMON_SPOT_UP','BADGE_TUNING::DEFENSIVE_BADGES','BADGE_TUNING::PERSONALITY_BADGES','CAREERMODE_PROGRESSION::BADGES::TUNING','CAREERMODE_PROGRESSION::FEATURES::TUNING::UNLOCK_REQUIREMENT'}
 chosen=[r for r in available if r['name'] in exact]
if a.mode=='presentation':
 exact={'GLOBALDATA_GAME','GLOBALDATA_CONTROLLER','GLOBALDATA_SAVEDITEMS','GLOBALDATA_USERSAVEDITEMS','FRANCHISE_TICKER_SETTINGS'}
 chosen=[r for r in available if r['name'] in exact]
name_map={}
for m in re.finditer(rb'[A-Za-z_][A-Za-z0-9_:]{2,119}\x00',data):
 s=m.group()[:-1].decode('ascii');crc=zlib.crc32(s.encode());name_map.setdefault(str(crc),[])
 if s not in name_map[str(crc)]:name_map[str(crc)].append(s)
plan={'sha256':source['exe_sha256'],'types':chosen,'xrefs':source['xrefs'][:24],'max_read_bytes':1048576}
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
(out/(a.mode+'-plan.json')).write_text(json.dumps(plan,indent=2),encoding='utf-8')
(out/'literal-crc-map.json').write_text(json.dumps(name_map),encoding='utf-8')
js=r'''const plan=__PLAN__,base=Process.mainModule.base;let bytes=0;const findings=[],refs=[];
const hex=a=>Array.from(new Uint8Array(a),x=>x.toString(16).padStart(2,'0')).join('');
function read(p,n){if(n<1||n>65536||bytes+n>plan.max_read_bytes)throw Error('read budget');bytes+=n;return p.readByteArray(n);}
function ptrAt(raw,o){return ptr('0x'+new DataView(raw).getBigUint64(o,true).toString(16));}
for(const t of plan.types){
 const init=read(base.add(t.initializer_rva),t.initializer_hex.length/2);if(hex(init)!==t.initializer_hex)throw Error('initializer mismatch:'+t.name);
 const head=read(base.add(t.type_rva),64),h=new DataView(head),count=Number(h.getBigUint64(0,true));if(count<0||count>1500)throw Error('field count');
 const name=read(ptrAt(head,40),t.name.length+1);if(hex(name)!==Array.from(t.name+'\0',c=>c.charCodeAt(0).toString(16).padStart(2,'0')).join(''))throw Error('name mismatch');
 const schema=read(ptrAt(head,32),40),stride=new DataView(schema).getUint32(20,true);
 const raw=count?read(ptrAt(head,8),count*40):new ArrayBuffer(0),v=new DataView(raw),fields=[];
 for(let i=0;i<count;i++)fields.push({index:i,words:Array.from({length:10},(_,j)=>v.getUint32(i*40+j*4,true))});
 if(hex(read(base.add(t.type_rva),64))!==hex(head))throw Error('type changed');
 findings.push({name:t.name,type_rva:t.type_rva,count,stride,fields,initializer_match:true,name_match:true});
}
for(const x of plan.xrefs){const raw=read(base.add(x.instruction_rva),7);if(hex(raw)!==x.instruction_hex)throw Error('xref changed');const ins=Instruction.parse(base.add(x.instruction_rva));refs.push({instruction_rva:x.instruction_rva,string:x.string,text:ins.toString(),size:ins.size,live_bytes_match:true,execution_observed:false});}
send({kind:'development-native-metadata-and-xrefs',types:findings,xrefs:refs,explicit_read_bytes:bytes,instance_values_read:0,getter_calls:0,hooks:0,memory_writes:0});
'''
(out/(a.mode+'-probe.js')).write_text(js.replace('__PLAN__',json.dumps(plan,separators=(',',':'))),encoding='utf-8')
print(json.dumps({'selected_types':[r['name'] for r in chosen],'available_struct_names':[r['name'] for r in available if re.search('PRESENTATION|BROADCAST|HALFTIME|MENTOR|TICKER',r['name'])][:45],'xrefs':len(plan['xrefs'])}))
