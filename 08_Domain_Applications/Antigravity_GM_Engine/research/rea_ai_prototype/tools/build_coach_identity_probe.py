"""Read-only exploration: pool membership is an observed hypothesis, not a gate."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
js=r'''const module=Process.mainModule,base=module.base;let used=0;const budget=65536,failures=[];
const hex=a=>Array.from(new Uint8Array(a),x=>x.toString(16).padStart(2,'0')).join('');
function readable(p,n){if(p.isNull()||n<1||n>1024)return false;let at=p,left=n;while(left>0){const r=Process.findRangeByAddress(at);if(!r||!r.protection.includes('r'))return false;const room=r.base.add(r.size).sub(at).toUInt32();if(room<1)return false;const take=Math.min(room,left);left-=take;at=at.add(take);}return true;}
function read(p,n,label){if(used+n>budget)throw Error('READ_BUDGET_EXHAUSTED');if(!readable(p,n))throw Error('UNREADABLE:'+label);used+=n;return p.readByteArray(n);}
function safe(p,n,label){try{return {ok:true,raw:read(p,n,label)};}catch(e){failures.push({field:label,error:String(e).replace(/0x[0-9a-f]+/gi,'[address]')});return {ok:false,error:'UNREADABLE_OR_ACCESS_EXCEPTION'};}}
function pointer(raw,o=0){return ptr('0x'+new DataView(raw).getBigUint64(o,true).toString(16));}
function integer(raw,o=0,n=2){const d=new DataView(raw);return n===1?d.getUint8(o):n===2?d.getUint16(o,true):d.getUint32(o,true);}
function utf16(raw){const d=new DataView(raw);let s='';for(let i=0;i+1<raw.byteLength;i+=2){const c=d.getUint16(i,true);if(!c)break;if(c<32||c===0xffff)return null;s+=String.fromCharCode(c);}return s||null;}
function getter(rva,prefix){const b=read(base.add(rva),8,'root-getter-code');if(hex(b.slice(0,3))!==prefix)throw Error('BUILD_OR_ROOT_GETTER_MISMATCH');return pointer(read(base.add(rva+7+new DataView(b).getInt32(3,true)),8,'root-pointer'));}
function imageRva(p){return p.compare(base)>=0&&p.compare(base.add(module.size))<0?p.sub(base).toUInt32():null;}
function rtti(p){const first=safe(p,8,'object-first-word');if(!first.ok)return {status:'NO_READABLE_HEADER'};const v=pointer(first.raw),vrva=imageRva(v);if(vrva===null)return {status:'FIRST_WORD_NOT_MAIN_IMAGE_POINTER'};
 const c=safe(v.sub(8),8,'vtable-locator');if(!c.ok)return {status:'VTABLE_CANDIDATE_ONLY',vtable_rva:vrva};const col=pointer(c.raw);if(imageRva(col)===null)return {status:'LOCATOR_NOT_MAIN_IMAGE',vtable_rva:vrva};
 const raw=safe(col,24,'RTTI-locator');if(!raw.ok)return {status:'LOCATOR_UNREADABLE',vtable_rva:vrva};const d=new DataView(raw.raw),self=d.getUint32(20,true),type=d.getUint32(12,true);if(d.getUint32(0,true)!==1||!base.add(self).equals(col))return {status:'LOCATOR_NOT_VERIFIED',vtable_rva:vrva};
 const name=safe(base.add(type+16),96,'RTTI-type-name');if(!name.ok)return {status:'TYPE_NAME_UNREADABLE',vtable_rva:vrva};const a=new Uint8Array(name.raw);let s='';for(const b of a){if(!b)break;if(b<32||b>126)return {status:'TYPE_NAME_NOT_ASCII',vtable_rva:vrva};s+=String.fromCharCode(b);}return {status:'MSVC_RTTI_CANDIDATE',vtable_rva:vrva,decorated_type_name:s||null};}
const roster=getter(18701792,'488b05'),root=roster.sub(8),desc=read(root.add(0x88),32,'team-descriptor'),count=Number(new DataView(desc).getBigUint64(0,true)),teams=pointer(desc,8),end=pointer(desc,24);
if(count<1||count>1000)throw Error('TEAM_ENUMERATION_BUDGET');const teamStrideEquation=teams.add(count*4696).equals(end);
const sd=read(root.add(0x138),32,'staff-descriptor-hypothesis'),staffCount=Number(new DataView(sd).getBigUint64(0,true)),staff=pointer(sd,8),staffEnd=pointer(sd,24),staffEquation=staff.add(staffCount*352).equals(staffEnd);
const rows=[];let firstWouldHaveFailed=null,selected=0;
for(let i=0;i<count;i++){const team=teams.add(i*4696),abbrRaw=safe(team.add(0x30a),10,'team-abbreviation');if(!abbrRaw.ok)continue;const abbr=utf16(abbrRaw.raw);if(!['IND','PHI'].includes(abbr))continue;if(selected++>=32)break;
 const id=safe(team.add(0xca8),2,'team-id'),cp=safe(team.add(0xce8),8,'team-coach-pointer');if(!id.ok||!cp.ok){rows.push({directory_index:i,abbreviation:abbr,status:'TEAM_PROJECTION_PARTIAL'});continue;}
 const tid=integer(id.raw),coach=pointer(cp.raw),inPool=!coach.isNull()&&coach.compare(staff)>=0&&coach.compare(staffEnd)<0,aligned=!coach.isNull()&&((BigInt(coach.toString())-BigInt(staff.toString()))%352n===0n),core=(tid<=6||(tid>=8&&tid<=29)||tid===31);
 const row={directory_index:i,team_id:tid,abbreviation:abbr,core_team_id:core,coach_is_null:coach.isNull(),pool_membership_hypothesis:{inside_staff_pool:inPool,aligned_to_staff_stride:aligned,hard_read_gate:false},writer_or_native_call_identity_qualified:false,object_fields:[]};
 if(firstWouldHaveFailed===null&&(!inPool||!aligned)){firstWouldHaveFailed={directory_index:i,team_id:tid,abbreviation:abbr,core_team_id:core,coach_is_null:coach.isNull()};row.matches_reconstructed_initial_abort_condition=true;}
 if(coach.isNull()){row.status='NULL_REFERENCE_OBSERVED';rows.push(row);continue;}
 const map=Process.findRangeByAddress(coach);row.mapping=map?{mapped:true,protection:map.protection,first_352_bytes_readable:readable(coach,352)}:{mapped:false};
 for(const [label,offset,size] of [['first_name_candidate',0x30,40],['last_name_candidate',0x58,40],['POE_word_candidate',316,4],['team_reciprocal_pointer_candidate',0x18,8]]){
  const r=safe(coach.add(offset),size,label);if(!r.ok){row.object_fields.push({field:label,offset,bytes:size,status:r.error});continue;}
  let value;if(size===40)value={utf16_candidate:utf16(r.raw)};else if(size===8)value={equals_source_team:pointer(r.raw).equals(team)};else{const w=integer(r.raw,0,4);value={defense_low5:w&31,offense_bits15_19:(w>>>15)&31,interpretation:'COACHDATA_LAYOUT_HYPOTHESIS_NOT_OBJECT_TYPE_PROOF'};}
  row.object_fields.push({field:label,offset,bytes:size,status:'READABLE_OBSERVED',...value});
 }
 row.rtti_hypothesis=rtti(coach);
 const again=safe(team.add(0xce8),8,'coach-pointer-recheck');row.same_team_reference_after_read=again.ok&&pointer(again.raw).equals(coach);row.status='BOUNDED_OBJECT_PROJECTION';rows.push(row);
}
const stable=hex(read(root.add(0x88),32,'team-directory-recheck'))===hex(desc)&&hex(read(root.add(0x138),32,'staff-directory-recheck'))===hex(sd)&&getter(18701792,'488b05').equals(roster);
send({kind:'coach-identity-hypothesis-exploration',team_directory_count:count,team_stride_equation_matches:teamStrideEquation,staff_count_hypothesis:staffCount,staff_stride_equation_matches:staffEquation,selection:'reconstruct original PHI/IND abbreviation order including non-core teams',original_failed_absolute_pointer_was_recorded:false,reconstructed_first_abort:firstWouldHaveFailed,observations:rows,isolated_read_failures:failures,stable_directory_recheck:stable,explicit_read_bytes:used,read_budget:budget,hooks:0,native_calls:0,business_writes:0,absolute_addresses_emitted:false});
'''
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'coach_identity_probe.js').write_text(js,encoding='utf-8')
print(json.dumps({'script':'coach_identity_probe.js','staff_pool_is_hypothesis':True,'max_matching_records':32,'read_budget':65536,'calls_or_writes':0}))
