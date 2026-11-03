// Deferred Native calls only. No writes to game-owned memory from this script.
function executeAction(){
 const p=request.parameters;
 if(!Number.isInteger(p.minutes)||p.minutes<0||p.minutes>48)throw Error('MINUTES_OUTSIDE_RECOVERED_UI_RANGE');
 const layout=bindingSpecs['rotation.current_delegate'].input_layout;
 const delegate=ptrAt(read(base.add(layout.root_rva),8));
 if(delegate.isNull())throw Error('ROTATION_DELEGATE_NOT_READY');
 const vtable=ptrAt(read(delegate,8));
 const profile=layout.allowed_profiles.find(profile=>Object.entries(profile.slots).every(([slot,target])=>
  ptrAt(read(vtable.add(Number(slot)),8)).equals(base.add(target))));
 if(!profile)throw Error('UNRECOVERED_ROTATION_DELEGATE_IMPLEMENTATION');
 const t=team(p.team_id),player=rosterPlayer(t,p.player_id),franchise=franchiseRecord(p.team_id);
 const nativeIndex=call('rotation.franchise_team_index',t);
 if(nativeIndex!==franchise.index)throw Error('ROTATION_FRANCHISE_TEAM_INDEX_MISMATCH');
 function snapshot(){
  const header=read(t,120),rows=[];
  for(let slot=0;slot<15;slot++){
   const at=ptrAt(header,slot*8);
   if(at.isNull())continue;
   rows.push({slot,pointer:at,uid:u16(read(at.add(0xf4),2)),word:u32(read(at.add(0xf8),4))});
  }
  return rows;
 }
 const before=snapshot(),selected=before.filter(row=>row.pointer.equals(player));
 if(selected.length!==1)throw Error('ROTATION_PLAYER_ROSTER_IDENTITY_AMBIGUOUS');
 const beforeMinutes=(selected[0].word>>>18)&127;
 call('rotation.set_player_minutes',delegate,player,p.minutes);
 // Same team-change path used by the recovered rotation UI, kind=1, flag=0.
 call('rotation.mark_team_change',t,1,0);
 const after=snapshot();
 if(after.length!==before.length||before.some((row,i)=>
  row.slot!==after[i].slot||row.uid!==after[i].uid||!row.pointer.equals(after[i].pointer)))
  throw Error('ROTATION_ROSTER_CHANGED_DURING_NATIVE_CALL');
 for(let i=0;i<before.length;i++){
  const expected=before[i].pointer.equals(player)?
   ((before[i].word&0xfe03ffff)|(p.minutes<<18))>>>0:before[i].word;
  if(after[i].word!==expected)throw Error('ROTATION_NATIVE_VALUE_OR_NEIGHBOR_MISMATCH');
 }
 const changeFlag=new Uint8Array(read(franchise.pointer.add(0x11ff9),1))[0];
 if(changeFlag!==0)throw Error('ROTATION_NATIVE_TEAM_CHANGE_FLAG_MISMATCH');
 result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{
  team_id:p.team_id,player_id:p.player_id,requested_minutes:p.minutes,
  observed_before_minutes:beforeMinutes,observed_after_minutes:p.minutes,
  observed_team_minutes_sum:after.reduce((total,row)=>total+((row.word>>>18)&127),0),
  other_roster_words_preserved:true,native_team_change_flag_raw:changeFlag,
  observation_scope:'Same-handler raw readback only; independent observation and Save/Reload remain required',
  automatic_minute_balancing:false,career_clamping_path_used:false
 });
}
