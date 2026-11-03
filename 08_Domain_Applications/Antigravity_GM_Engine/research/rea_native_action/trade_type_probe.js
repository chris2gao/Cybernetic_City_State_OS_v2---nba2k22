'use strict';
const base=Process.mainModule.base,size=Process.mainModule.size;let used=0;
function read(p,n){if(n<1||n>8192||used+n>32768)throw Error('TYPE_READ_BUDGET');const r=Process.findRangeByAddress(p);if(!r||!r.protection.includes('r')||p.add(n).compare(r.base.add(r.size))>0)throw Error('TYPE_RANGE_UNREADABLE');used+=n;return p.readByteArray(n);}
const pointer=(b,o=0)=>ptr('0x'+new DataView(b).getBigUint64(o,true).toString(16));
const u32=(b,o=0)=>new DataView(b).getUint32(o,true);
function rva(p){return p.compare(base)>=0&&p.compare(base.add(size))<0?p.sub(base).toUInt32():null;}
const result=[];for(const [name,rv] of [['FRANCHISE_TRADE_ELEMENT',82877056],['FRANCHISE_TRADE',82877120],['FRANCHISE_TRANSACTION_RECORD',82877824],['FRANCHISE_TRANSACTION',82877952]]){
 try{const h=read(base.add(rv),48),count=Number(new DataView(h).getBigUint64(0,true));if(count<1||count>200)throw Error('FIELD_COUNT_LIMIT');const v=read(pointer(h,32),32),table=read(pointer(h,8),count*40),fields=[];
  for(let i=0;i<count;i++)fields.push({crc:u32(table,i*40),offset:u32(table,i*40+8),size:u32(table,i*40+12),format:u32(table,i*40+16),referenced_type_or_enum_rva:rva(pointer(table,i*40+32))});
  result.push({name,type_rva:rv,object_size:u32(v,20),field_count:count,fields,status:'READ_OBSERVED'});
 }catch(e){result.push({name,status:'ISOLATED_TYPE_READ_FAILURE',error:String(e).replace(/0x[0-9a-f]+/gi,'[address]')});}
}
send({kind:'native-trade-types',types:result,explicit_read_bytes:used,native_calls:0,business_writes:0,absolute_addresses_emitted:false});
