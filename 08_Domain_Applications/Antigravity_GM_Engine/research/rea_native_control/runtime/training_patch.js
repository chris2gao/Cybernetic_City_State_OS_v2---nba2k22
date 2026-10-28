// Partial daily training update through the original Native service.
// All writes here target caller-owned input; game data is read only by this bridge.
function executeAction(){
 const p=request.parameters,t=team(p.team_id),daily=call('training.daily_by_date',t,p.date);
 if(daily.isNull())throw Error('NO_EXISTING_TRAINING_RECORD_FOR_REQUESTED_DATE');
 const before=read(daily,56),input=Memory.alloc(64);
 input.writeByteArray(new Uint8Array(64).buffer);
 input.add(8).writeByteArray(before);
 let fields;
 if(request.action_id==='TRAIN_TEAM_PATCH_FOCUS_RAW'){
  for(let i=0;i<3;i++)input.add(8+i*4).writeFloat(p.focus_values_raw[i]);
  fields=['focus_values_raw'];
 }else if(request.action_id==='TRAIN_TEAM_PATCH_PROFILE_RAW'){
  for(let i=0;i<3;i++)input.add(20+i).writeU8(p.profile_values_raw[i]);
  for(let i=0;i<38;i++)input.add(23+i).writeU8(p.subfocus_points_raw[i]);
  fields=['profile_values_raw','subfocus_points_raw'];
 }else throw Error('UNSUPPORTED_TRAINING_PATCH');
 call('training.set_team_on_date',t,p.date,input);
 result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{
  date_key:p.date,requested_fields:fields,unrequested_daily_input_preserved:true,
  scope:'Private input preserves remaining daily record; Native may no-op. No date substitution, unit conversion, allocation optimization or game-field writer.'
 });
}
