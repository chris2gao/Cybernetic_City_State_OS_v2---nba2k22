// Inspect only. Never acquire/reset, allocate, generate wages, offer or process.
function executeAction(){
 const p=request.parameters,schema=bindingSpecs['sign.pool_read_context'].input_layout.schema;
 const allowed=new Set(Object.values(schema.enums.Status).filter(name=>name!=='EMPTY').concat(['UNRECOGNIZED']));
 if(Object.keys(p).sort().join('|')!=='include_archived|statuses|team_id'||
   !Number.isInteger(p.team_id)||p.team_id<0||p.team_id>=65535||
   !Array.isArray(p.statuses)||!p.statuses.length||new Set(p.statuses).size!==p.statuses.length||
   p.statuses.some(name=>typeof name!=='string'||!allowed.has(name))||
   !Number.isInteger(p.include_archived)||![0,1].includes(p.include_archived))throw Error('EXACT_SIGNING_QUERY_REQUIRED');
 const owner=team(p.team_id),rootAt=base.add(schema.pool.root_rva),root=ptrAt(read(rootAt,8));
 if(root.isNull())throw Error('SIGNING_FRANCHISE_ROOT_UNAVAILABLE');
 const pool=root.add(schema.pool.offset),before=[],rows=[];
 function decode(raw){
  const view=new DataView(raw),fields={};
  for(const field of schema.fields){
   const values=[];
   for(let i=0;i<field.count;i++){
    // Final bytes may have fewer than four remaining; only registered bits enter output.
    const at=field.offset+i*4;let word=0;
    for(let k=0;k<4&&at+k<raw.byteLength;k++)word=(word|(view.getUint8(at+k)<<(k*8)))>>>0;
    let value=field.width===32?word:(word>>>field.shift)&(2**field.width-1);
    if(field.signed&&value>=2**(field.width-1))value-=2**field.width;
    values.push(value);
   }
   fields[field.name]=field.count===1?values[0]:values;
  }
  return fields;
 }
 function selected(fields){
  const label=schema.enums.Status[fields.Status]||'UNRECOGNIZED';
  return fields.TeamId===p.team_id&&fields.Status!==0&&p.statuses.includes(label)&&
   (p.include_archived===1||fields.IsArchived===0);
 }
 for(let index=0;index<schema.pool.count;index++){
  const raw=read(pool.add(index*schema.pool.stride),schema.bytes),fields=decode(raw);
  const included=selected(fields);before.push({raw,included});
  if(!included)continue;
  const enums={};for(const [name,labels] of Object.entries(schema.enums))enums[name]={value:fields[name],name:labels[fields[name]]||null};
  rows.push({record_index:index,player_id:fields.PlayerId===65535?null:fields.PlayerId,
   player_identity_resolved:fields.PlayerId!==65535,team_id:fields.TeamId,fields,enums});
 }
 for(let index=0;index<schema.pool.count;index++){
  const raw=read(pool.add(index*schema.pool.stride),schema.bytes),included=selected(decode(raw));
  if(included!==before[index].included||((included||before[index].included)&&!equal(raw,before[index].raw)))
   throw Error('SIGNING_SELECTED_RECORD_SET_CHANGED');
 }
 if(!ptrAt(read(rootAt,8)).equals(root)||!team(p.team_id).equals(owner))throw Error('SIGNING_READ_CONTEXT_CHANGED');
 result('NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED',{
  read_only:true,snapshot_bracket_unchanged:true,
  data:{team_id:p.team_id,statuses:p.statuses,include_archived:p.include_archived,offers:rows},
  interpretation:'Internal signing pool records; ACCEPTED is distinct from SIGNED; neither proves independent roster/contract effects',
  unknown_scope:['Native save/world/phase identity','current UI availability and currency units','atomicity/ABA and deferred completion','independent signing effects and persistence'],
  arbitrary_memory_dump_emitted:false,hidden_potential_emitted:false,
  observation_scope:'Registered44-byte signing fields only; record_index is transient and not a durable offer identity'
 });
}
