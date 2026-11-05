"""Inspect named native type descriptors in the explicitly known local game PE."""
import json,mmap,struct,zlib
from pathlib import Path
path=Path('E:/games/NBA 2K22/NBA2K22.exe');out=Path(__file__).parent/'settings-pe-inspection.json'
with path.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
    pe=struct.unpack_from('<I',data,0x3C)[0];assert data[pe:pe+4]==b'PE\0\0'
    machine,count,timestamp=struct.unpack_from('<HHI',data,pe+4);optional=pe+24;size_optional=struct.unpack_from('<H',data,pe+20)[0]
    base=struct.unpack_from('<Q',data,optional+24)[0];image_size=struct.unpack_from('<I',data,optional+56)[0];sections=[]
    for i in range(count):
        at=optional+size_optional+i*40;name=data[at:at+8].split(b'\0')[0].decode('ascii')
        vsize,rva,size,offset=struct.unpack_from('<4I',data,at+8);sections.append((name,rva,max(vsize,size),offset,size))
    def to_rva(offset):
        for name,rva,size,off,rawsize in sections:
            if off<=offset<off+rawsize:return rva+offset-off
        raise ValueError('file offset outside PE sections')
    def to_off(rva):
        for name,start,size,off,rawsize in sections:
            if start<=rva<start+rawsize:return off+rva-start
        raise ValueError('RVA not represented in file')
    results=[]
    for name in ('TUNEDATA_SAVED','TUNEDATA','GAME_SETTINGS','GAMESETTINGS','TRADE_SETTINGS','TRADEINFO','FRANCHISE','SETTINGS'):
        target=name.encode()+b'\0';start=0;strings=0;types=[]
        while True:
            at=data.find(target,start)
            if at<0:break
            start=at+len(target);strings+=1
            try:pointer=struct.pack('<Q',base+to_rva(at))
            except ValueError:continue
            pos=0
            while True:
                ref=data.find(pointer,pos)
                if ref<0:break
                pos=ref+8;header=ref-40
                if header<0:continue
                words=struct.unpack_from('<8Q',data,header)
                try:
                    if not 0<words[0]<2000:continue
                    schema=struct.unpack_from('<10I',data,to_off(words[4]-base));fields=to_off(words[1]-base)
                    sample=[]
                    for i in range(min(words[0],4)):
                        w=struct.unpack_from('<10I',data,fields+i*40);sample.append({'crc':hex(w[0]),'offset':w[2],'size':w[3],'format':hex(w[4])})
                    types.append({'type_rva':to_rva(header),'field_count':words[0],'struct_size':schema[5],'field_samples':sample})
                except (ValueError,struct.error):pass
        results.append({'name':name,'string_hits':strings,'types':types})
    result={'machine':machine,'module_timestamp':timestamp,'module_image_size':image_size,'image_base':hex(base),'types':results}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result))
