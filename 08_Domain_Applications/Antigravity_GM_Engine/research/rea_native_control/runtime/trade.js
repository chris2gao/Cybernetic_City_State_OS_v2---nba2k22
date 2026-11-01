function executeAction(){const p=request.parameters,a=team(p.team_a),b=team(p.team_b),playerTransfers=[],pickTransfers=[];
 for(const [from,to,ids] of [[a,b,p.players_a],[b,a,p.players_b]])for(const uid of ids)playerTransfers.push({from,to,player:rosterPlayer(from,uid)});
 for(const [from,to,ids] of [[a,b,p.picks_a],[b,a,p.picks_b]])for(const uid of ids){const pick=call('pick.by_id',uid);if(pick.isNull()||call('pick.unique_id',pick)!==uid||!ptrAt(read(pick,8)).equals(from))throw Error('REQUESTED_PICK_ID_OR_CURRENT_OWNER_MISMATCH');pickTransfers.push({from,to,pick});}
 // No salary matching, player valuation, contract modification or alternative search.
 const mode=ptrAt(read(base.add(0x11c1ad0+7+0x51699c1),8)),fr=ptrAt(read(base.add(0x12e945b+7+0x5042016),8));if(u32(read(mode.add(0x150),4))!==1||!u32(read(fr.add(8),4))||u32(read(fr.add(0xac),4)))throw Error('NATIVE_TRADE_LIFECYCLE_NOT_READY');
 const allocation=Memory.alloc(1700),proposal=allocation.add(16),canary=new Uint8Array(16).fill(0xa7),out=Memory.alloc(4);allocation.writeByteArray(new Uint8Array(1700).buffer);allocation.writeByteArray(canary.buffer);proposal.add(1668).writeByteArray(canary.buffer);for(let i=0;i<8;i+=2)proposal.add(i).writeU16(65535);proposal.add(4).writeU16(p.team_a);proposal.add(8).writeU32(0x43ffff);out.writeU32(0);
 const guard=()=>equal(allocation.readByteArray(16),canary.buffer)&&equal(proposal.add(1668).readByteArray(16),canary.buffer);
 for(const x of playerTransfers){if(call('trade.add_player',proposal,x.from,x.to,x.player)!==1){result('REJECTED_BY_GAME',{step:'ADD_REQUESTED_PLAYER'});return;}if(!guard())throw Error('PRIVATE_PROPOSAL_CANARY');}
 for(const x of pickTransfers){if(call('trade.add_pick',proposal,x.from,x.to,x.pick)!==1){result('REJECTED_BY_GAME',{step:'ADD_REQUESTED_PICK'});return;}if(!guard())throw Error('PRIVATE_PROPOSAL_CANARY');}
 if(p.execution_mode==='AGREED_DIRECT_PROCESS'){
  const context=call('trade.context');if(context.isNull())throw Error('NATIVE_TRADE_CONTEXT_NULL');read(context,8);
  const ret=call('trade.process',proposal,context,out);
  result(ret!==0?'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED':'REJECTED_BY_GAME',{process_return:ret,game_output_code:out.readU32(),same_requested_assets:true,private_canaries_intact:guard(),submission_mode:'AGREED_DIRECT_PROCESS',external_valuation_or_salary_check:false,full_check_called:false,native_process_internal_identity_validation:true});return;
 }
 if(call('trade.validate',proposal)!==1){result('REJECTED_BY_GAME',{step:'VALIDATE'});return;}if(!guard())throw Error('PRIVATE_PROPOSAL_CANARY');
 // The wrapper itself calls original FullCheck and Process; no duplicated rules.
 const ret=call('trade.commit_wrapper',proposal,out);result(ret===0?'NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED':'REJECTED_BY_GAME',{wrapper_return:ret,game_output_code:out.readU32(),same_requested_assets:true,private_canaries_intact:guard()});
}
