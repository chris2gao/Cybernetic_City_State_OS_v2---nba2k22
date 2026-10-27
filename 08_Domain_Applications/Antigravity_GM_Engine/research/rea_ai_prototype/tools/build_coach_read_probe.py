import argparse,json,zlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();root=Path(__file__).resolve().parents[3]
profile=json.loads((root/'config/coach_tactics_profile.json').read_text(encoding='utf-8'))
fields={name:profile['fields'][name] for name in ('POEDefense','POEOffense')}
plan={'native':profile['native'],'fields':fields,'crcs':{n:zlib.crc32(n.encode()) for n in [*fields,'UniqueId']},'enum_crc':{name:{value:zlib.crc32(label.encode()) for value,label in f['enum'].items()} for name,f in fields.items()},'selected_abbreviations':['IND','PHI'],'budget_bytes':65536}
js=r'''const plan=__PLAN__,base=Process.mainModule.base;let used=0;
const hex=a=>Array.from(new Uint8Array(a),x=>x.toString(16).padStart(2,'0')).join('');
function read(p,n){if(n<1||n>40000||used+n>plan.budget_bytes)throw Error('budget');used+=n;return p.readByteArray(n);}
function u64(raw,off=0){return ptr('0x'+new DataView(raw).getBigUint64(off,true).toString(16));}
function number(raw,off=0,size=2){const v=new DataView(raw);return size===1?v.getUint8(off):size===2?v.getUint16(off,true):v.getUint32(off,true);}
function getter(rva,prefix,ret){const code=read(base.add(rva),8);if(hex(code.slice(0,3))!==prefix||(ret&&number(code,7,1)!==0xc3))throw Error('getter identity');const displacement=new DataView(code).getInt32(3,true);return u64(read(base.add(rva+7+displacement),8));}
function text(raw){const v=new DataView(raw);let s='';for(let i=0;i+1<raw.byteLength;i+=2){const n=v.getUint16(i,true);if(!n)break;s+=String.fromCharCode(n);}return s;}
const typeHead=read(base.add(plan.native.coach_type_rva),64),count=Number(new DataView(typeHead).getBigUint64(0,true));if(count<1||count>800)throw Error('coach field count');
if(hex(read(u64(typeHead,40),10))!=='434f4143484441544100')throw Error('COACHDATA name');
if(number(read(u64(typeHead,32),40),20,4)!==352)throw Error('coach size');
const metadata=read(u64(typeHead,8),count*40),mv=new DataView(metadata),defs={};
for(let i=0;i<count;i++){const crc=mv.getUint32(i*40,true);for(const [name,wanted] of Object.entries(plan.crcs))if(crc===wanted)defs[name]={offset:mv.getUint32(i*40+8,true),size:mv.getUint32(i*40+12,true),format:mv.getUint32(i*40+16,true),enumPtr:u64(metadata,i*40+32)};}
const fieldProof=[];
for(const [name,f] of Object.entries(plan.fields)){
 const d=defs[name];if(!d||d.offset!==f.offset||((d.format>>>8)&255)!==f.width||((d.format>>>16)&255)!==f.start_bit)throw Error('field layout '+name);
 if(!d.enumPtr.equals(base.add(f.enum_rva)))throw Error('enum identity');
 const eh=read(d.enumPtr,48),ec=Number(new DataView(eh).getBigUint64(16,true));if(ec<1||ec>300)throw Error('enum count');const table=read(u64(eh,24),ec*12),ev=new DataView(table),actual={};
 for(let i=0;i<ec;i++)actual[String(ev.getInt32(i*12+4,true))]=ev.getUint32(i*12,true);
 for(const [value,crc] of Object.entries(plan.enum_crc[name]))if(actual[value]!==crc)throw Error('enum labels changed');
 fieldProof.push({field:name,offset:d.offset,start_bit:f.start_bit,width:f.width,labels:f.enum,layout_and_enum_match:true});
}
const roster=getter(plan.native.roster_getter_rva,'488b05',true),franchise=getter(plan.native.franchise_load_rva,'488b1d',false),root=roster.sub(8);
if(roster.isNull()||franchise.isNull())throw Error('no active roster/franchise');
const teamDesc=read(root.add(0x88),32),tv=new DataView(teamDesc),teams=Number(tv.getBigUint64(0,true)),teamBase=u64(teamDesc,8),teamEnd=u64(teamDesc,24);
if(teams<30||teams>1000||!teamBase.add(teams*4696).equals(teamEnd))throw Error('team directory');
const staffDesc=read(root.add(0x138),32),staffCount=Number(new DataView(staffDesc).getBigUint64(0,true)),staffBase=u64(staffDesc,8),staffEnd=u64(staffDesc,24);
if(staffCount<1||staffCount>10000||!staffBase.add(staffCount*352).equals(staffEnd))throw Error('staff directory');
const chosen=[];
for(let i=0;i<teams;i++){const team=teamBase.add(i*4696),tid=number(read(team.add(0xca8),2));if(!((tid>=0&&tid<=6)||(tid>=8&&tid<=29)||tid===31))continue;const abbr=text(read(team.add(0x30a),10));if(!plan.selected_abbreviations.includes(abbr))continue;
 const coach=u64(read(team.add(0xce8),8));if(coach.compare(staffBase)<0||coach.compare(staffEnd)>=0||coach.sub(staffBase).toUInt32()%352){send({kind:'guard-failure',code:'coach-pool-identity',team_id:tid,abbreviation:abbr,staff_count:staffCount,coach_is_null:coach.isNull(),inside_staff_pool:coach.compare(staffBase)>=0&&coach.compare(staffEnd)<0});throw Error('coach pool identity');}
 chosen.push({abbr,tid,team,coach});}
if(chosen.length!==2||new Set(chosen.map(t=>t.tid)).size!==2)throw Error('selected teams missing');
function snapshot(){const result=[];for(const t of chosen){
 if(number(read(t.team.add(0xca8),2))!==t.tid||!u64(read(t.team.add(0xce8),8)).equals(t.coach))throw Error('coach owner changed');
 const word=number(read(t.coach.add(316),4),0,4),values={};for(const [name,f] of Object.entries(plan.fields)){const raw=(word>>>f.start_bit)&((1<<f.width)-1);if(!Object.hasOwn(f.enum,String(raw)))throw Error('unknown current enum');values[name]={raw,label:f.enum[String(raw)]};}
 let unique=null;if(defs.UniqueId&&defs.UniqueId.offset+4<=352&&((defs.UniqueId.format>>>8)&255)===32)unique=number(read(t.coach.add(defs.UniqueId.offset),4),0,4);
 let manager=null;for(let s=0;s<36;s++){const p=franchise.add(plan.native.franchise_teams_offset+s*plan.native.franchise_team_stride);if(number(read(p,2))===t.tid){if(manager)throw Error('duplicate manager');manager=p;}}
 if(!manager)throw Error('manager missing');const plans=[];
 for(let j=0;j<35;j++){const p=manager.add(4+j*880),h=read(p,6),owner=number(h,2);if(owner===65535)continue;if(owner!==t.tid)throw Error('gameplan owner');const foe=number(h,4);const v=read(p.add(0x17e),6);plans.push({slot:j,owner,opponent:foe,is_in_use:number(h,0,1),is_tainted:number(h,1,1),poe_offense:Array.from(new Uint8Array(v.slice(0,3))),poe_defense:Array.from(new Uint8Array(v.slice(3,6)))});}
 result.push({team_abbreviation:t.abbr,team_id:t.tid,coach_unique_id:unique,coach_values:values,gameplans:plans,engine_control:'UNKNOWN_NOT_READ'});
 }return result;}
const first=snapshot(),second=snapshot();if(JSON.stringify(first)!==JSON.stringify(second))throw Error('snapshot changed');
if(hex(read(base.add(plan.native.coach_type_rva),64))!==hex(typeHead)||hex(read(root.add(0x88),32))!==hex(teamDesc)||hex(read(root.add(0x138),32))!==hex(staffDesc))throw Error('metadata/directory moved');
if(!getter(plan.native.roster_getter_rva,'488b05',true).equals(roster)||!getter(plan.native.franchise_load_rva,'488b1d',false).equals(franchise))throw Error('active context changed');
send({kind:'issue9-coach-read-only',field_proof:fieldProof,teams:first,stable_double_read:true,explicit_read_bytes:used,native_field_count:count,gameplay_consumer_observed:false,game_actor_dispatch_proven:false,hooks:0,native_calls:0,memory_writes:0,absolute_addresses_emitted:false});
'''
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'coach_read_probe.js').write_text(js.replace('__PLAN__',json.dumps(plan,separators=(',',':'))),encoding='utf-8')
print(json.dumps({'script':str(out/'coach_read_probe.js'),'budget':65536,'hook_targets':0,'game_calls':0,'writes':0}))
