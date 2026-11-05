"""Current league/history native metadata and narrowly sourced observations."""
from datetime import datetime,timezone
import hashlib,json,struct
from pathlib import Path
from award_reader import read_native_fields
from live_reader import ReadOnlyGameProcess,ROSTER_RVA
from live_world import _json
from schedule_reader import bounded_block
from family_codec import decode_fixed_utf16
import math
from collections import Counter

PROFILE_PATH=Path(__file__).with_name('league_native_profile.json')
FRANCHISE_RVA=0x632B478


def unsigned_fields(raw,bindings):
    values={}
    for name,f in bindings.items():
        if f.get('array_dimensions') or not 1<=f['width']<=64:continue
        off,size,shift,width=(f[k] for k in ('offset','size','start_bit','width'))
        if off+size>len(raw) or shift+width>size*8:raise ValueError('native numeric field outside record')
        values[name]=(int.from_bytes(raw[off:off+size],'little')>>shift)&((1<<width)-1)
    return values


def decode_native_date(raw,bindings):
    values=unsigned_fields(raw,bindings)
    return {'raw_word_u32':int.from_bytes(raw,'little'),'id_raw':values['Id'],
        'minutes_since_midnight_raw':values['MinutesSinceMidnight'],'day_raw':values['Day'],
        'month_raw':values['Month'],'base_year_offset_raw':values['BaseYearOffset'],
        'date_status':'NATIVE_COMPONENTS_OBSERVED; EPOCH_AND_UI_TIME_NOT_PROMOTED'}


def decode_history_record(raw,index,profile):
    if len(raw)!=152:raise ValueError('league history record must be 152 bytes')
    values=unsigned_fields(raw,profile['bindings']['LEAGUEHISTORYDATA']);names={};text_status=[]
    for name in ('PrimaryTeamName','PrimaryTeamCity','SecondaryTeamName','SecondaryTeamCity','PlayerFirstName','PlayerLastName'):
        f=profile['bindings']['LEAGUEHISTORYDATA'][name];size=f['array_dimensions'][0]
        prefix=raw[f['offset']:f['offset']+size].split(b'\0',1)[0]
        if any(b<32 or b==127 for b in prefix):names[name]=None;text_status.append('INVALID_PREFIX:'+name)
        else:names[name]=prefix.decode('latin1').strip() or None
    floats={}
    for name in ('PrimaryStat','SecondaryStat'):
        off=profile['bindings']['LEAGUEHISTORYDATA'][name]['offset'];word=int.from_bytes(raw[off:off+4],'little');value=struct.unpack_from('<f',raw,off)[0]
        floats[name]={'word_u32':word,'value_real':value if math.isfinite(value) else None,
            'value_text':value.hex() if math.isfinite(value) else f'NONFINITE_NATIVE_FLOAT_WORD:{word:08x}'}
    code=values['Type'];labels=profile['enum_labels']['LEAGUEHISTORY_TYPE'].get(str(code),{}).get('labels',[])
    return {'source_row_index':index,'values':values,'names':names,'stat_values':floats,
        'type_label':labels[0] if len(labels)==1 else None,'text_status':';'.join(text_status) if text_status else 'ASCII_OR_LATIN1_PREFIXES_OBSERVED',
        'source_state':'ALL_ZERO_SLOT' if not any(raw) else 'INVALID_TYPE_SLOT' if code==0 else 'NATIVE_HISTORY_RECORD_OBSERVED'}


def decode_social_message(raw,bank,index,profile):
    if len(raw)!=124:raise ValueError('social message must be 124 bytes')
    bindings=profile['bindings']['FRANCHISE_SOCIALMEDIA::MESSAGE'];values=unsigned_fields(raw,bindings);texts={}
    for name in ('String1','String2'):
        f=bindings[name];part=raw[f['offset']:f['offset']+f['array_dimensions'][0]*2]
        try:texts[name]=decode_fixed_utf16(part) or None
        except UnicodeDecodeError:texts[name]=None;texts[name+'_status']='INVALID_UTF16_PREFIX'
    event=profile['enum_labels']['FRANCHISE_SOCIALMEDIA::EVENT'].get(str(values['Event']),{}).get('labels',[])
    sender=profile['enum_labels']['FRANCHISE_SOCIALMEDIA::SENDER_TYPE'].get(str(values['SenderType']),{}).get('labels',[])
    return {'bank_index':bank,'source_slot_index':index,'values':values,'text_fragments':texts,
        'event_label':event[0] if len(event)==1 else None,'sender_type_label':sender[0] if len(sender)==1 else None,
        'date':decode_native_date(raw[16:20],profile['bindings']['SCHEDULEDATE']),
        'source_state':'ALL_ZERO_SLOT' if not any(raw) else 'NO_EVENT_SLOT' if values['Event']==0 else 'NATIVE_EVENT_AND_PARAMETERS_OBSERVED'}


def free_chain_candidate(raw,count,start):
    visited=[];seen=set();index=start
    while index!=65535:
        if index>=count or index in seen:return {'status':'INVALID_CANDIDATE_CHAIN','indices':visited,'terminal_index':index}
        seen.add(index);visited.append(index);index=int.from_bytes(raw[index*152+136:index*152+138],'little')
    return {'status':'TERMINATED_CANDIDATE_CHAIN; MANAGER_TABLE_IDENTITY_NOT_ASSUMED','indices':visited,'terminal_index':index}


def collect_league_source(reader):
    profile=json.loads(PROFILE_PATH.read_bytes());metadata=[]
    for entry in profile['types']:
        metadata.append(read_native_enum(reader,entry) if entry['constructor_rva']==0x1e53e90 else read_native_fields(reader,entry,read_enums=False))
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'LEAGUE_ROSTER_POINTER');root=int.from_bytes(pointer,'little')
    franchise_pointer=reader.read(reader.module_base+FRANCHISE_RVA,8,'LEAGUE_FRANCHISE_POINTER');franchise=int.from_bytes(franchise_pointer,'little')
    if root<0x10000 or franchise<0x10000:raise ValueError('native roster/franchise root unavailable')
    descriptor=reader.read(root+41*16,16,'LEAGUE_HISTORY_DESCRIPTOR');count,address=struct.unpack('<QQ',descriptor)
    if not 1<=count<=10000 or address<0x10000:raise ValueError('league history array outside bound')
    manager_descriptor=reader.read(root+40*16,16,'LEAGUE_MANAGER_CANDIDATE_DESCRIPTOR');manager_count,manager=struct.unpack('<QQ',manager_descriptor)
    manager_raw=reader.read(manager,4,'LEAGUE_MANAGER_CANDIDATE_WORD') if manager_count==1 and manager>=0x10000 else None
    history=bounded_block(reader,address,count*152,'LEAGUE_HISTORY_TABLE');rows=[decode_history_record(history[i*152:(i+1)*152],i,profile) for i in range(count)]
    controls=[(address,history,'LEAGUE_HISTORY_RECHECK')];blobs={'league-history.bin':history}
    if manager_raw:blobs['league-manager-candidate.bin']=manager_raw;controls.append((manager,manager_raw,'LEAGUE_MANAGER_CANDIDATE_RECHECK'))
    native=profile['bindings']['FRANCHISE'];social_base=franchise+native['SocialMedia']['offset'];s=profile['bindings']['FRANCHISE_SOCIALMEDIA::DATA'];message_f=s['Message'];banks,capacity=message_f['array_dimensions']
    if (banks,capacity)!=(2,2000):raise ValueError('native message array dimension changed')
    counts_raw=reader.read(social_base+s['ActiveMessageCount']['offset'],4,'LEAGUE_SOCIAL_ACTIVE_COUNTS');active=list(struct.unpack('<2H',counts_raw))
    if any(n>capacity for n in active):raise ValueError('native social active count exceeds bank capacity')
    messages_raw=bounded_block(reader,social_base+message_f['offset'],banks*capacity*124,'LEAGUE_SOCIAL_MESSAGES');messages=[]
    for bank in range(banks):
        for i in range(capacity):
            start=(bank*capacity+i)*124;row=decode_social_message(messages_raw[start:start+124],bank,i,profile)
            row['active_prefix_status']='WITHIN_DECLARED_COUNT_PREFIX_CANDIDATE' if i<active[bank] else 'OUTSIDE_DECLARED_COUNT_PREFIX';messages.append(row)
    controls.extend(((social_base+s['ActiveMessageCount']['offset'],counts_raw,'LEAGUE_SOCIAL_COUNTS_RECHECK'),(social_base+message_f['offset'],messages_raw,'LEAGUE_SOCIAL_MESSAGES_RECHECK')))
    blobs['social-active-counts.bin']=counts_raw;blobs['social-messages.bin']=messages_raw
    transaction_count_raw=reader.read(franchise+native['NumTransactions']['offset'],2,'LEAGUE_TRANSACTION_COUNT');transaction_count=int.from_bytes(transaction_count_raw,'little');transaction_capacity=native['Transaction']['array_dimensions'][0]
    if transaction_count>transaction_capacity or transaction_capacity!=250:raise ValueError('native transaction count/capacity invalid')
    transactions_raw=bounded_block(reader,franchise+native['Transaction']['offset'],transaction_capacity*320,'LEAGUE_TRANSACTIONS');transactions=[]
    for i in range(transaction_capacity):
        raw=transactions_raw[i*320:(i+1)*320];values=unsigned_fields(raw,profile['bindings']['FRANCHISE_TRANSACTION'])
        items=[dict(source_item_index=j,**unsigned_fields(raw[j*8:(j+1)*8],profile['bindings']['FRANCHISE_TRANSACTION_RECORD'])) for j in range(39)]
        label=profile['enum_labels']['TRANSACTION_TYPE'].get(str(values['Type']),{}).get('labels',[])
        transactions.append({'source_slot_index':i,'values':values,'items':items,'date':decode_native_date(raw[312:316],profile['bindings']['SCHEDULEDATE']),
            'type_label':label[0] if len(label)==1 else None,'active_prefix_status':'WITHIN_DECLARED_COUNT_PREFIX_CANDIDATE' if i<transaction_count else 'OUTSIDE_DECLARED_COUNT_PREFIX'})
    controls.extend(((franchise+native['NumTransactions']['offset'],transaction_count_raw,'LEAGUE_TRANSACTION_COUNT_RECHECK'),(franchise+native['Transaction']['offset'],transactions_raw,'LEAGUE_TRANSACTIONS_RECHECK')))
    blobs['transaction-count.bin']=transaction_count_raw;blobs['transactions.bin']=transactions_raw
    matrix_f=native['SeasonAwardWinnerIndex'];matrix_raw=reader.read(franchise+matrix_f['offset'],15*5*2,'LEAGUE_SEASON_AWARD_WINNER_MATRIX')
    matrix=[{'award_slot_index':a,'recipient_slot_index':r,'native_player_index_raw':struct.unpack_from('<H',matrix_raw,(a*5+r)*2)[0]} for a in range(15) for r in range(5)]
    controls.append((franchise+matrix_f['offset'],matrix_raw,'LEAGUE_AWARD_MATRIX_RECHECK'));blobs['season-award-winner-matrix.bin']=matrix_raw
    for target,raw,label in controls:
        if bounded_block(reader,target,len(raw),label)!=raw:raise ValueError('league source changed during acquisition')
    for target,raw,label in ((reader.module_base+ROSTER_RVA,pointer,'LEAGUE_ROOT_RECHECK'),(reader.module_base+FRANCHISE_RVA,franchise_pointer,'LEAGUE_FRANCHISE_RECHECK'),(root+41*16,descriptor,'LEAGUE_HISTORY_DESCRIPTOR_RECHECK'),(root+40*16,manager_descriptor,'LEAGUE_MANAGER_DESCRIPTOR_RECHECK')):
        if reader.read(target,len(raw),label)!=raw:raise ValueError('league source context changed')
    return {'metadata':metadata,'history_descriptor':{'count':count,'address':address,'stride':152},'franchise_root':franchise,
        'history':rows,'manager_slot40_candidate':{'count':manager_count,'first_word':int.from_bytes(manager_raw[:2],'little') if manager_raw else None,
            'free_chain':free_chain_candidate(history,count,int.from_bytes(manager_raw[:2],'little')) if manager_raw else None},
        'social_active_counts':active,'messages':messages,'transaction_count':transaction_count,'transactions':transactions,
        'award_winner_matrix':matrix,'game_writes':False,'player_struct_reads':0,
        'source_scope':'NATIVE_ROSTER_HISTORY_AND_CURRENT_FRANCHISE_EVENTS; NOT_INFERRED_WORLD_OCCURRENCE'},blobs


def probe_league_source(pid,new_output_directory):
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    report={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_writes':False}
    try:
        reader=ReadOnlyGameProcess(pid);manifest,blobs=collect_league_source(reader);reader.close()
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'league-source-manifest.json',manifest)
        report.update({'status':'LEAGUE_SOURCE_CAPTURED','read_trace':reader.trace,
            'reader_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    except Exception as error:
        report.update({'status':'LEAGUE_SOURCE_UNAVAILABLE','error_type':type(error).__name__,'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
    finally:
        if reader:reader.close()
    _json(out/'league-source-report.json',report);return report


def read_native_enum(reader,entry):
    code=bytes.fromhex(entry['initializer_hex'])
    if reader.read(reader.module_base+entry['initializer_rva'],len(code),'LEAGUE_ENUM_INITIALIZER:'+entry['name'])!=code:raise ValueError('enum initializer changed')
    header=reader.read(reader.module_base+entry['type_rva'],48,'LEAGUE_ENUM_HEADER:'+entry['name']);h=struct.unpack('<6Q',header)
    name_address=reader.module_base+entry['name_rva']
    if name_address not in h:raise ValueError('enum type-name pointer not present in current header')
    if reader.read(name_address,len(entry['name'])+1,'LEAGUE_ENUM_NAME:'+entry['name'])!=entry['name'].encode()+b'\0':raise ValueError('enum type name changed')
    if not 1<=h[2]<=4096:raise ValueError('enum table outside explicit bound')
    raw=bounded_block(reader,h[3],h[2]*12,'LEAGUE_ENUM_VALUES:'+entry['name'])
    if reader.read(reader.module_base+entry['type_rva'],48,'LEAGUE_ENUM_HEADER_RECHECK:'+entry['name'])!=header or bounded_block(reader,h[3],len(raw),'LEAGUE_ENUM_VALUES_RECHECK:'+entry['name'])!=raw:raise ValueError('enum source changed')
    return {'name':entry['name'],'type_rva':entry['type_rva'],'header_hex':header.hex(),
        'values':[{'name_crc':c,'value':v,'aux':a} for c,v,a in struct.iter_unpack('<IiI',raw)],
        'status':'CURRENT_ENUM_INITIALIZER_NAME_HEADER_AND_VALUE_TABLE_VERIFIED'}


def probe_league_metadata(pid,new_output_directory):
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    report={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_writes':False,'player_struct_reads':0}
    try:
        profile=json.loads(PROFILE_PATH.read_bytes());reader=ReadOnlyGameProcess(pid);metadata=[]
        for entry in profile['types']:
            if entry['constructor_rva']==0x1e53e90:
                metadata.append(read_native_enum(reader,entry));continue
            t=read_native_fields(reader,entry,read_enums=False)
            for f in t['fields']:
                w=f['words'];dimensions=(w[5]>>16)&65535;ptr=w[6]|w[7]<<32
                if 1<=dimensions<=8 and reader.module_base<=ptr<reader.module_base+reader.module_size:
                    raw=reader.read(ptr,dimensions*24,'LEAGUE_NATIVE_ARRAY_DIMENSIONS:'+entry['name'])
                    f['array_dimension_records_hex']=raw.hex()
                    f['array_dimensions']=[struct.unpack_from('<I',raw,i*24)[0] for i in range(dimensions)]
                    if reader.read(ptr,len(raw),'LEAGUE_NATIVE_ARRAY_DIMENSIONS_RECHECK:'+entry['name'])!=raw:raise ValueError('native dimension control changed')
            metadata.append(t)
        reader.close();_json(out/'league-native-metadata.json',metadata)
        report.update({'status':'LEAGUE_NATIVE_METADATA_CAPTURED','read_trace':reader.trace,
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    except Exception as error:
        report.update({'status':'LEAGUE_NATIVE_METADATA_UNAVAILABLE','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
    finally:
        if reader:reader.close()
    _json(out/'league-metadata-report.json',report);return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('pid',type=int);p.add_argument('new_output_directory');p.add_argument('--source',action='store_true');a=p.parse_args()
    r=(probe_league_source if a.source else probe_league_metadata)(a.pid,a.new_output_directory);print(json.dumps({'status':r['status'],'reason':r.get('reason')}))
    raise SystemExit(0 if r['status'] in ('LEAGUE_NATIVE_METADATA_CAPTURED','LEAGUE_SOURCE_CAPTURED') else 2)
