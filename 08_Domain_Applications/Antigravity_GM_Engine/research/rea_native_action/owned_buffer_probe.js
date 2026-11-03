'use strict';
const blocks=[];
for(const size of [384,880]){
 const p=Memory.alloc(size),data=new Uint8Array(size).fill(0x37);p.writeByteArray(data.buffer);
 const rows=[];for(const offset of [0,16,size-16]){const at=p.add(offset),range=Process.findRangeByAddress(at);let direct;
  try{const b=at.readByteArray(Math.min(16,size-offset));direct={success:true,expected_bytes_match:Array.from(new Uint8Array(b)).every(v=>v===0x37)};}catch(e){direct={success:false,error:'OWNED_BOUNDED_READ_EXCEPTION'};}
  rows.push({offset,range_report:range?{protection:range.protection,size:range.size,remaining_bytes:range.base.add(range.size).sub(at).toString()}:null,direct_owned_read:direct});
 }
 blocks.push({allocation_bytes:size,rows});
}
send({kind:'owned-frida-buffer-read-diagnostic',blocks,game_native_calls:0,game_business_writes:0,absolute_addresses_emitted:false,scope:'Only fresh Frida-owned allocations were written and read; no business object touched'});
