function executeAction(){
 const p=request.parameters,t=team(p.team_id),c=ptrAt(read(t.add(0xce8),8)),b=read(c,352),ownerMatches=ptrAt(b,0x18).equals(t),w=u32(b,316),settings={};
 for(const [name,spec] of Object.entries(coachSettingSpecs)){
  settings[name]=spec.storage_bytes===1?new Uint8Array(b)[spec.coach_offset]:(u32(b,spec.coach_offset)>>>spec.start_bit)&(2**spec.width-1);
 }
 result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{read_only:true,data:{team_id:p.team_id,reciprocal_owner_matches:ownerMatches,class_identity:ownerMatches?'PRIOR_LAYOUT_WITH_RECIPROCAL_LINK':'UNVERIFIED_COACH_HYPOTHESIS_FROM_TEAM_POINTER',name:[text(b.slice(0x30,0x58)),text(b.slice(0x58,0x80))].join(' '),offense:(w>>>15)&31,offense2:(w>>>20)&31,offense3:(w>>>25)&31,defense:w&31,defense2:(w>>>5)&31,defense3:(w>>>10)&31,known_current_settings:settings,projection_fingerprint_fnv32:fnv(b),reference_slots_null:[0,1,2].map(i=>ptrAt(b,0x120+i*8).isNull())},coverage:'Bounded current Coach-pointer observation; no staff pool/alignment hard gate; ten mapped current fields, not full rotation or persistent Gameplan'});
}
