function executeAction(){const p=request.parameters;
 if(['SCOUT_LIST_CURRENT_PUBLIC_PROSPECTS','SCOUT_LIST_DRAFT_PROSPECTS'].includes(request.action_id)){const d=currentDraftClass(),rows=[],limit=p.limit===undefined?150:p.limit;for(let i=0;i<d.count&&rows.length<limit;i++){const prospect=d.pool.add(i*640),header=read(prospect,24),player=ptrAt(header);if(player.isNull()||(u32(header,0x14)&0x8000))continue;const b=read(player,80);rows.push({player_id:u16(read(player.add(0xf4),2)),name:[text(b.slice(40,80)),text(b.slice(0,40))].join(' ')});}result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{read_only:true,prospects:rows,scope:'Current valid class, public identity only; no hidden ratings/potential/report claims'});return;}
 if(request.action_id==='SCOUT_READ_PROSPECT_INFO'){const pr=currentProspect(p.player_id),b=read(pr.pointer,640);if(u32(b,0x14)&0x8000)throw Error('HIDDEN_PROSPECT_NOT_PUBLIC');const identity=read(pr.player,80),bytes=new Uint8Array(b);result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{read_only:true,data:{player_id:p.player_id,name:[text(identity.slice(40,80)),text(identity.slice(0,40))].join(' '),expert_rank_raw:Array.from(bytes.slice(0x268,0x26b)),expert_position_rank_raw:Array.from(bytes.slice(0x26e,0x271)),mock_draft_rank_raw:Array.from(bytes.slice(0x274,0x277))},unknown_fields:['UI_rank_conversion','visible_ability_estimates','report_text'],scope:'Public identity and static-named global rank bytes only; not hidden ratings/potential'});return;}
 const t=team(p.team_id),record=franchiseRecord(p.team_id),trip=record.pointer.add(0x13aac);
 if(['SCOUT_READ_TRIP_BUDGET','SCOUT_READ_STAFF_CAPACITY_SCHEDULE'].includes(request.action_id)){
  const count=new Uint8Array(read(trip,1))[0],goals=[],quality=[];let klass=null;
  try{klass=currentDraftClass();}catch(e){quality.push('CURRENT_CLASS_UNAVAILABLE_TARGET_IDENTITIES_UNKNOWN');}
  if(count>3)quality.push('GOAL_COUNT_EXCEEDS_STATIC_LAYOUT_HYPOTHESIS');
  for(let i=0;i<Math.min(count,3);i++){
   const b=read(trip.add(4+i*148),148),flags=u32(b,136),n=(flags>>>12)&255,targets=[];
   if(n>17)quality.push('GOAL_'+i+'_TARGET_COUNT_EXCEEDS_STATIC_LAYOUT_HYPOTHESIS');
   for(let j=0;j<Math.min(n,17);j++){
    const packed=u32(b,j*4),index=packed&255;let uid=null,publicIdentity=false;
    if(klass&&index<klass.count){
     const prospect=read(klass.pool.add(index*640),24),player=ptrAt(prospect);
     publicIdentity=!player.isNull()&&!(u32(prospect,0x14)&0x8000);
     if(publicIdentity)uid=u16(read(player.add(0xf4),2));
    }
    targets.push({class_index_raw:index,player_id:uid,public_identity_resolved:publicIdentity});
   }
   goals.push({goal_index:i,focus_type_raw:flags&7,num_targets_raw:n,targets,fingerprint_fnv32:fnv(b)});
  }
  result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{read_only:true,team_id:p.team_id,franchise_record_index:record.index,remaining_trips_raw:(u32(read(t.add(0x1068),4))>>>15)&15,num_existing_goals:count,goals,quality_flags:quality,scope:'Bounded Goal target identity decoding from native SetSpecific packed class index; no hidden ratings or report claims'});return;
 }
 const prospect=currentProspect(p.player_id);if(u32(read(prospect.pointer.add(0x14),4))&0x8000)throw Error('HIDDEN_PROSPECT_NOT_A_PUBLIC_REPORT');const b=read(prospect.pointer.add(0x18+record.index*16),16),flags=u32(b,8);result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{read_only:true,player_id:p.player_id,team_id:p.team_id,scouting_points_raw:u32(b,12)&255,had_workout:!!(flags&0x40000000),had_medical:!!(flags&0x80000000),report_text:'UNKNOWN_NATIVE_PRESENTATION_GETTER',revealed_ratings:'UNKNOWN_DISCLOSURE_MAPPING',scope:'Per-team raw progress flags; not an unlocked report or direct hidden player attributes'});
}
