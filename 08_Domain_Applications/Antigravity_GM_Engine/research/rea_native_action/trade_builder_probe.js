const preview={kind:'native-trade-builder-receipt',source_kind:'REAL_GAME_FUNCTIONS_PRIVATE_TRADE_INPUT_ONLY',experiment_id:'EXP-NATIVE-TRADE-BUILD-01',native_calls:0,game_commit_calls:0,status:'NOT_EXECUTED',AI_caller_proven:false,transaction_effect_claimed:false};
function fingerprint(bytes){let h=2166136261;for(const b of new Uint8Array(bytes))h=Math.imul(h^b,16777619)>>>0;return h;}
for(const f of plan.native_signatures)if(fingerprint(read(base.add(f.rva),f.bytes))!==f.fnv32)throw Error('TRADE_NATIVE_CODE_CHANGED');
const tA=liveTeams[1],tB=liveTeams[2],pA=tA?.players.find(p=>p.public.unique_id===9842&&p.public.name==='Jordan Nwora'),pB=tB?.players.find(p=>p.public.unique_id===9879&&p.public.name==='Anthony Gill');
if(!tA||!tB||!pA||!pB||!pA.public.current_team_matches||!pB.public.current_team_matches||!pA.public.contract_team_matches||!pB.public.contract_team_matches)throw Error('TRADE_OBJECT_IDENTITY_NOT_QUALIFIED');
for(const p of [pA,pB])if(p.public.contract.no_trade!==0||p.public.contract.contract_type!==0||p.public.contract.years_left_on_contract!==1||p.public.contract.contract_year_1!==1517981)throw Error('TRADE_CONTRACT_BASELINE_CHANGED');
const allocation=Memory.alloc(1700),proposal=allocation.add(16),canary=new Uint8Array(16).fill(0xa7);allocation.writeByteArray(new Uint8Array(1700).buffer);allocation.writeByteArray(canary.buffer);proposal.add(1668).writeByteArray(canary.buffer);for(let off=0;off<8;off+=2)proposal.add(off).writeU16(65535);proposal.add(4).writeU16(1);proposal.add(8).writeU32(0x43ffff);
const addPlayer=new NativeFunction(base.add(19786784),'int',['pointer','pointer','pointer','pointer'],{abi:'win64',exceptions:'steal'}),validate=new NativeFunction(base.add(19843376),'int',['pointer'],{abi:'win64',exceptions:'steal'});
function same(a,b){const x=new Uint8Array(a),y=new Uint8Array(b);return x.length===y.length&&x.every((v,i)=>v===y[i]);}
function guard(){return same(allocation.readByteArray(16),canary.buffer)&&same(proposal.add(1668).readByteArray(16),canary.buffer);}
let finished=false;
onGameGuiThreadOnce(context=>{
 preview.thread=context;
 if(!getter(18701792).equals(roster)||!same(read(tA.pointer,4696),tA.raw)||!same(read(tB.pointer,4696),tB.raw)||!same(read(pA.pointer,1264),pA.raw)||!same(read(pB.pointer,1264),pB.raw))throw Error('TRADE_PRESTATE_CHANGED');
 preview.native_calls++;const a=addPlayer(proposal,tA.pointer,tB.pointer,pA.pointer);if(a!==1||!guard())throw Error('FIRST_NATIVE_ADD_FAILED');
 preview.native_calls++;const b=addPlayer(proposal,tB.pointer,tA.pointer,pB.pointer);if(b!==1||!guard())throw Error('SECOND_NATIVE_ADD_FAILED');
 preview.native_calls++;const valid=validate(proposal);preview.native_validate_result=valid;
 preview.proposal_header={receiving_team1:proposal.readU16(),receiving_team2:proposal.add(2).readU16(),offering_team:proposal.add(4).readU16(),id:proposal.add(6).readU16(),flags:proposal.add(8).readU32(),AI_initiated:!!(proposal.add(8).readU32()&0x400000),force_legal_money:!!(proposal.add(8).readU32()&0x800000)};
 preview.elements=[];for(let i=0;i<18;i++){const e=proposal.add(12+i*92),f=e.add(4).readU32();if(!(f&0x30000))continue;preview.elements.push({slot:i,from_team_id:e.readU16(),to_team_id:e.add(2).readU16(),player_id:f&65535,element_type:(f>>>16)&3,from_value:e.add(16).readU32(),to_value:e.add(20).readU32()});}
 preview.canaries_intact=guard();preview.game_objects_unchanged=same(read(tA.pointer,4696),tA.raw)&&same(read(tB.pointer,4696),tB.raw)&&same(read(pA.pointer,1264),pA.raw)&&same(read(pB.pointer,1264),pB.raw);
 preview.status=valid===1&&preview.canaries_intact&&preview.game_objects_unchanged?'PRIVATE_NATIVE_PROPOSAL_ABI_AND_VALIDATE_VERIFIED':'PRIVATE_NATIVE_PROPOSAL_REQUIRES_INVESTIGATION';finished=true;
},bridge=>{if(bridge.error){preview.failure=bridge.error;preview.status='FAILED_OR_ABORTED';}if(!bridge.bridge_completed)return;preview.bridge=bridge;preview.explicit_read_bytes=used;preview.absolute_addresses_emitted=false;send(preview);},1800);
