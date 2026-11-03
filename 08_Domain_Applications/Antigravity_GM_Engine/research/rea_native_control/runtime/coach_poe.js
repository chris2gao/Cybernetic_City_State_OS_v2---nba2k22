function executeAction(){const p=request.parameters,t=team(p.team_id),coach=ptrAt(read(t.add(0xce8),8)),raw=read(coach,352),word=u32(raw,316),shift=request.action_id==='COACH_APPLY_DEFENSE_POE'?0:15;
 if(!ptrAt(raw,0x18).equals(t))throw Error('COACH_RECIPROCAL_TEAM_BINDING');for(let i=0;i<3;i++)if(!ptrAt(raw,0x120+i*8).isNull())throw Error('NONNULL_REFERENCED_OBJECT_BRANCH_NOT_RECOVERED');
 if(p.expected_before!==undefined&&((word>>>shift)&31)!==p.expected_before)throw Error('EXPECTED_BEFORE_CHANGED');
 const franchise=getter(6278620);let manager=null;for(let i=0;i<36;i++){const m=franchise.add(1691600+i*81520);if(u16(read(m,2))===p.team_id){if(manager)throw Error('DUPLICATE_MANAGER');manager=m;}}if(!manager)throw Error('MANAGER_NOT_FOUND');
 const gp=manager.add(0x7854),original=read(gp,880);if(u16(original,2)!==p.team_id)throw Error('GAMEPLAN_TEAM_MISMATCH');const input=Memory.alloc(880);input.writeByteArray(original);
 for(let i=0;i<3;i++)input.add(0x178+i*2).writeU16(65535);for(const [offset,s] of [[0x17e,15],[0x17f,20],[0x180,25],[0x181,0],[0x182,5],[0x183,10]])input.add(offset).writeU8((word>>>s)&31);
 input.add(shift===0?0x181:0x17e).writeU8(p.value);input.add(0x184).writeU8((u32(raw,0x148)>>>17)&255);for(const [source,dest] of [[0x185,0xe0],[0x186,0xe2],[0x187,0xde],[0x188,0x138],[0x189,0xdf],[0x18a,0x109]])input.add(source).writeU8(new Uint8Array(raw)[dest]);input.add(0x18b).writeU8((u32(raw,0xfc)>>>25)&63);
 if(!getter(18701792).equals(roster)||!equal(read(coach,352),raw)||!equal(read(gp,880),original))throw Error('OBJECT_PRESTATE_CHANGED');
 call('coach.apply_gameplan',input,coach);const after=read(coach,352),expected=raw.slice(0),mask=(31<<shift)>>>0;new DataView(expected).setUint32(316,((word&~mask)|(p.value<<shift))>>>0,true);
 result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{requested_value:p.value,actual_value:(u32(after,316)>>>shift)&31,full_coach_projection_matches:equal(after,expected),original_gameplan_unchanged:equal(read(gp,880),original),scope:'CURRENT_COACH_PROJECTION_ONLY_NOT_PERSISTENT_GAMEPLAN'});
}
