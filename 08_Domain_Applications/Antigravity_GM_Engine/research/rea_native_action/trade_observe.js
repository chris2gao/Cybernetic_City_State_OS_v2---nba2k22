'use strict';
const plan=__PLAN__,base=Process.mainModule.base;let used=0;const failures=[];
function read(p,n){if(n<1||n>8192||used+n>plan.read_budget)throw Error('READ_BUDGET');const range=Process.findRangeByAddress(p);if(!range||!range.protection.includes('r')||p.add(n).compare(range.base.add(range.size))>0)throw Error('UNREADABLE_RANGE');used+=n;return p.readByteArray(n);}
const pointer=(b,o=0)=>ptr('0x'+new DataView(b).getBigUint64(o,true).toString(16)),u16=(b,o=0)=>new DataView(b).getUint16(o,true),u32=(b,o=0)=>new DataView(b).getUint32(o,true);
function text(b){let s='';for(let o=0;o+1<b.byteLength;o+=2){const c=u16(b,o);if(!c)break;s+=String.fromCharCode(c);}return s;}
function getter(rva){const raw=read(base.add(rva),8);if(new Uint8Array(raw)[0]!==0x48||new Uint8Array(raw)[1]!==0x8b)throw Error('ROOT_GETTER_CHANGED');return pointer(read(base.add(rva+7+new DataView(raw).getInt32(3,true)),8));}
const roster=getter(18701792),root=roster.sub(8),desc=read(root.add(0x88),32),count=Number(new DataView(desc).getBigUint64(0,true)),teamBase=pointer(desc,8);if(count<30||count>1000)throw Error('TEAM_ENUMERATION_BUDGET');
const teams=[],allTeams=[],liveTeams={};for(let i=0;i<count;i++){
 const team=teamBase.add(i*4696);try{const id=u16(read(team.add(0xca8),2));if(!((id<=6)||(id>=8&&id<=29)||id===31))continue;const raw=read(team,4696),abbr=text(raw.slice(0x30a,0x314)),pointers=[];for(let j=0;j<15;j++)pointers.push(pointer(raw,j*8));
  const summary={team_id:id,abbreviation:abbr,name:text(raw.slice(0x2b4,0x2dc)),regular_count:new Uint8Array(raw)[0xcb1],nonnull_regular_slots:pointers.filter(p=>!p.isNull()).length,total_salary_raw:u32(raw,0xcbc),payroll_raw:u32(raw,0xff4),native_trade_control_kind:(u32(raw,0xee8)>>>4)&3};allTeams.push(summary);
  if(!plan.target_team_ids.includes(id))continue;const players=[];liveTeams[id]={pointer:team,raw,players:[]};
  for(let slot=0;slot<15;slot++){const p=pointers[slot];if(p.isNull())continue;try{const b=read(p,1264),contract={};for(const f of plan.contract_fields){const bytes=f.bits?Math.ceil((f.start_bit+f.bits)/8):f.bytes;if(f.offset+bytes>b.byteLength)continue;let v=0;for(let k=0;k<bytes;k++)v+=new Uint8Array(b)[f.offset+k]*2**(8*k);if(f.bits)v=Math.floor(v/2**f.start_bit)%2**f.bits;contract[f.name]=v;}
   const player={slot,unique_id:u16(b,0xf4),name:[text(b.slice(40,80)),text(b.slice(0,40))].filter(Boolean).join(' '),current_team_matches:pointer(b,0x60).equals(team),contract_team_matches:pointer(b,0xa8).equals(team),face_id:u16(b,0x6c),contract};players.push(player);liveTeams[id].players.push({pointer:p,raw:b,public:player});
  }catch(e){players.push({slot,status:'ISOLATED_PLAYER_READ_FAILURE'});}}
  teams.push({...summary,players});
 }catch(e){failures.push({directory_index:i,status:'ISOLATED_TEAM_READ_FAILURE'});}
}
send({kind:'native-trade-roster-observation',teams,all_core_teams:allTeams,isolated_failures:failures,stable_roster_root:getter(18701792).equals(roster),explicit_read_bytes:used,native_calls:0,business_writes:0,absolute_addresses_emitted:false});
