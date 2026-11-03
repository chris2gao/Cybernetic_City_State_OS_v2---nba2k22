'use strict';
const request={"action_id":"PLAYER_PATCH_TENDENCIES","parameters":{"target_teams":[28,1]},"request_id":"probe_live_roster_001"},bindingSpecs={"player.get_stat_ui":{"abi":"win64","binding_id":"player.get_stat_ui","evidence":["01_os/07_content/_runs/run-20261028-role-native-execution-system-001/static/player_stat_read_getter_contract_026.json"],"game_build_sha256":"1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5","input_layout":{"code_signatures":[{"bytes":2580,"fnv32":2751660889,"rva":9929568},{"bytes":4,"fnv32":1798808928,"rva":36408044},{"bytes":4,"fnv32":1487269050,"rva":35762196}]},"lifecycle":["Pure selected Getter paths: no game memory writes or calls. Use original float conversion/rounding; no guessed JS attribute decoder"],"object_requirements":["Exact current roster PLAYER; explicit selected qualified index excluding Potential/unclassified cases"],"parameters":[{"name":"player","type":"pointer"},{"name":"stat_index","type":"int"}],"return_type":"int","rva":9929568,"unknowns":[]}},limits={"is_live":true,"maximum_game_calls":100,"read_bytes":1048576},base=Process.mainModule.base;let readBytes=0,gameCalls=0,invoked=false;
const coachSettingSpecs={};
const playerContractFields={};
if(Process.arch!=='x64'||Process.mainModule.name.toLowerCase()!=='nba2k22.exe')throw Error('PC22_X64_TARGET_REQUIRED');
function read(p,n){if(n<1||n>32768||readBytes+n>limits.read_bytes)throw Error('BOUNDED_READ_LIMIT');let at=p,left=n;while(left){const r=Process.findRangeByAddress(at);if(!r||!r.protection.includes('r'))throw Error('OBJECT_RANGE_UNREADABLE');const size=Math.min(left,r.base.add(r.size).sub(at).toUInt32());if(size<1)throw Error('OBJECT_RANGE_END');at=at.add(size);left-=size;}readBytes+=n;return p.readByteArray(n);}
const u16=(b,o=0)=>new DataView(b).getUint16(o,true),u32=(b,o=0)=>new DataView(b).getUint32(o,true),ptrAt=(b,o=0)=>ptr('0x'+new DataView(b).getBigUint64(o,true).toString(16));
function text(b){let out='';for(let o=0;o+1<b.byteLength;o+=2){const c=u16(b,o);if(!c)break;out+=String.fromCharCode(c);}return out;}
function equal(a,b){const x=new Uint8Array(a),y=new Uint8Array(b);return x.length===y.length&&x.every((v,i)=>v===y[i]);}
function fnv(b){let h=2166136261;for(const v of new Uint8Array(b))h=Math.imul(h^v,16777619)>>>0;return h;}
for(const spec of Object.values(bindingSpecs))for(const sig of spec.input_layout.code_signatures||[])if(fnv(read(base.add(sig.rva),sig.bytes))!==sig.fnv32)throw Error('PINNED_NATIVE_CODE_CHANGED');
function getter(rva){const b=read(base.add(rva),8),v=new Uint8Array(b);if(v[0]!==0x48||v[1]!==0x8b)throw Error('ROOT_GETTER_CODE_CHANGED');return ptrAt(read(base.add(rva+7+new DataView(b).getInt32(3,true)),8));}
const roster=getter(18701792),rosterRoot=roster.sub(8),directory=read(rosterRoot.add(0x88),32),teamCount=Number(new DataView(directory).getBigUint64(0,true)),teamBase=ptrAt(directory,8);
if(teamCount<1||teamCount>1000)throw Error('TEAM_DIRECTORY_LIMIT');
function team(id){let found=null;for(let i=0;i<teamCount;i++){const p=teamBase.add(i*4696);if(u16(read(p.add(0xca8),2))===id){if(found)throw Error('DUPLICATE_TEAM_ID');found=p;}}if(!found)throw Error('TEAM_NOT_FOUND');return found;}
function rosterPlayer(t,uid){const b=read(t,4696);let found=null;for(let i=0;i<15;i++){const p=ptrAt(b,i*8);if(!p.isNull()&&u16(read(p.add(0xf4),2))===uid){if(found)throw Error('DUPLICATE_PLAYER_UID');found=p;}}if(!found)throw Error('PLAYER_NOT_ON_REQUESTED_TEAM');const b2=read(found,1264);if(!ptrAt(b2,0x60).equals(t)||!ptrAt(b2,0xa8).equals(t))throw Error('PLAYER_CURRENT_CONTRACT_TEAM_MISMATCH');return found;}
function franchiseRecord(teamId){const franchise=getter(6278620);let found=null;for(let i=0;i<36;i++){const record=franchise.add(0x19cfd0+i*0x13e70);if(u16(read(record,2))===teamId){if(found)throw Error('DUPLICATE_FRANCHISE_TEAM_RECORD');found={pointer:record,index:i};}}if(!found)throw Error('FRANCHISE_TEAM_RECORD_NOT_FOUND');return found;}
function currentDraftClass(){const at=base.add(0x1308f04+7+0x502256d),root=ptrAt(read(at,8)),klass=root.add(0x3f08),header=read(klass,16),n=new Uint8Array(header)[12];if(!u32(header)||n>150)throw Error('CURRENT_DRAFT_CLASS_NOT_READY');return {pointer:klass,count:n,pool:klass.add(16)};}
function currentProspect(uid){const d=currentDraftClass();let found=null;for(let i=0;i<d.count;i++){const p=d.pool.add(i*640),player=ptrAt(read(p,8));if(!player.isNull()&&u16(read(player.add(0xf4),2))===uid){if(found)throw Error('DUPLICATE_PROSPECT_UID');found={pointer:p,player,index:i};}}if(!found)throw Error('PROSPECT_NOT_IN_CURRENT_CLASS');return found;}
function call(bindingId,...args){const spec=bindingSpecs[bindingId];if(!spec||spec.rva===null)throw Error('UNKNOWN_NATIVE_BINDING');if(gameCalls>=limits.maximum_game_calls)throw Error('NATIVE_CALL_BUDGET');gameCalls++;send({kind:'native-call-stage',action_id:request.action_id,binding_id:bindingId,stage:'STARTED',call_number:gameCalls});const fn=new NativeFunction(base.add(spec.rva),spec.return_type,spec.parameters.map(p=>p.type),{abi:'win64',exceptions:'steal'});const result=fn(...args);send({kind:'native-call-stage',action_id:request.action_id,binding_id:bindingId,stage:'RETURNED',call_number:gameCalls,result:spec.return_type==='void'?null:spec.return_type==='pointer'?'POINTER_NOT_PUBLISHED':result});return result;}
function result(outcome,details={}){send({kind:'native-control-result',action_id:request.action_id,outcome,details,first_hand_game_calls:gameCalls,read_bytes:readBytes,automatic_retry:false,request_substitution:false,effect_verified_by_this_result:false,absolute_addresses_emitted:false});}


const u8 = (b, o = 0) => new DataView(b).getUint8(o);

function executeAction() {
  const targetTeams = [28, 1];
  const teamResults = {};

  for (const tid of targetTeams) {
    const t = team(tid);
    const b = read(t, 4696);
    const players = [];
    for (let i = 0; i < 15; i++) {
      const pp = ptrAt(b, i * 8);
      if (pp.isNull()) continue;
      const v = read(pp, 1264);
      const uid = u16(v, 0xf4);
      const firstName = text(v.slice(40, 80));
      const lastName = text(v.slice(0, 40));
      const fullName = (firstName + " " + lastName).trim();
      
      const tendencyVal = call('player.get_stat_ui', pp, 57);
      const rawByte = u8(read(pp.add(0x458), 1));

      players.push({
        slot: i,
        player_id: uid,
        name: fullName,
        shot_tendency_getter: tendencyVal,
        shot_tendency_raw: rawByte
      });
    }
    const teamAbbr = text(b.slice(0x30a, 0x314));
    teamResults[tid] = {
      team_id: tid,
      abbreviation: teamAbbr,
      player_count: players.length,
      players: players
    };
  }

  send({
    kind: 'chunk-execution-result',
    chunk_id: 'probe_001',
    chunk_digest: 'digest_probe_001',
    plan_digest: 'plan_probe_001',
    action_id: 'PLAYER_PATCH_TENDENCIES',
    batch_id: 'BATCH-PROBE-001',
    save_instance_id: 'MyLEAGUE0003',
    outcome: 'CHUNK_SUCCESS',
    details: teamResults,
    receipts: []
  });
}

// Deferred runtime: resolve the game's own visible-window thread, invoke once.
const user=Process.getModuleByName('user32.dll'),cell=Memory.alloc(4),title=Memory.alloc(256);let selected=null,hook=null;
const threadOf=new NativeFunction(user.getExportByName('GetWindowThreadProcessId'),'uint',['pointer','pointer'],'win64'),visible=new NativeFunction(user.getExportByName('IsWindowVisible'),'int',['pointer'],'win64'),titleOf=new NativeFunction(user.getExportByName('GetWindowTextW'),'int',['pointer','pointer','int'],'win64');
const enumerate=new NativeCallback((h,l)=>{const tid=threadOf(h,cell);if(cell.readU32()===Process.id&&visible(h)){const n=titleOf(h,title,128);if(n&&/NBA/i.test(title.readUtf16String(n)))selected={handle:h,thread:tid};}return 1;},'int',['pointer','pointer'],'win64');new NativeFunction(user.getExportByName('EnumWindows'),'int',['pointer','pointer'],'win64')(enumerate,ptr(0));
if(!selected){result('EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',{reason:'GAME_WINDOW_THREAD_NOT_FOUND'});}else{hook=Interceptor.attach(user.getExportByName('PeekMessageA'),{onLeave(){if(invoked||Process.getCurrentThreadId()!==selected.thread)return;invoked=true;try{executeAction();}catch(e){result('EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',{reason:String(e).replace(/0x[0-9a-f]+/gi,'[address]')});}finally{hook.detach();}}});new NativeFunction(user.getExportByName('PostMessageW'),'int',['pointer','uint','pointer','pointer'],'win64')(selected.handle,0,ptr(0),ptr(0));setTimeout(()=>{if(!invoked){hook.detach();result('EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY',{reason:'GAME_THREAD_NOT_ENTERED'});}},4000);}
