"""Calendar metadata/code controls and narrowly bounded public SEASON scalars."""
import hashlib,struct,zlib
from award_reader import read_native_fields
from league_reader import read_native_enum
from calendar_codec import PROFILE,PROFILE_PATH,LAYOUT,GAME_CAPACITY,STAT_CAPACITY,date_columns,enum_label

def verify_calendar_metadata(reader):
    by_type={e['name']:e for e in PROFILE['types']};metadata=[]
    for entry in PROFILE['types']:
        if entry['constructor_rva']==31800976:
            value=read_native_enum(reader,entry);expected={(int(code),v['name_crc']) for code,v in PROFILE['enum_labels'][entry['name']].items()}
            if {(v['value'],v['name_crc']) for v in value['values']}!=expected:raise ValueError('native calendar enum changed')
        else:
            value=read_native_fields(reader,entry,entry['expected_size'],read_enums=False)
            for field in value['fields']:
                name=next((name for name,f in PROFILE['bindings'][entry['name']].items() if f['name_crc']==field['name_crc']),None);expected=PROFILE['bindings'][entry['name']][name]
                if field['words'][1]!=expected['words'][1]:raise ValueError('native calendar primitive type changed')
                if expected['enum_pointer']:
                    referenced=next((e for e in PROFILE['types'] if 0x140000000+e['type_rva']==expected['enum_pointer']),None)
                    if referenced and field['enum_pointer']!=reader.module_base+referenced['type_rva']:raise ValueError('native calendar nested type changed')
                dimension=PROFILE['array_dimensions'].get(entry['name'],{}).get(name)
                if dimension:
                    w=field['words'];ptr=w[6]|w[7]<<32;raw=reader.read(ptr,24,'CALENDAR_ARRAY_EXTENT:'+name)
                    if w[5]>>16!=1 or struct.unpack_from('<I',raw)[0]!=dimension[0]:raise ValueError('native calendar array capacity changed')
                    if reader.read(ptr,24,'CALENDAR_ARRAY_EXTENT_RECHECK:'+name)!=raw:raise ValueError('native calendar capacity unstable')
        metadata.append(value)
    for proof in PROFILE['code_proofs']:
        raw=bytes.fromhex(proof['hex'])
        if reader.read(reader.module_base+proof['rva'],len(raw),'CALENDAR_YEAR_EPOCH_CODE')!=raw:raise ValueError('native date year-epoch code changed')
    return metadata

def collect_calendar_controls(reader,season,slot10_count):
    s=PROFILE['bindings']['SEASON'];g=PROFILE['bindings']['SEASON_SCHEDULE'];bank=PROFILE['bindings'][PROFILE['bank_type']];controls=[]
    def read(offset,size,label):
        raw=reader.read(season+offset,size,label);controls.append((offset,raw,label));return raw
    current=read(s['Date']['offset'],4,'CALENDAR_CURRENT_DATE');period=int.from_bytes(read(s['Period']['offset'],4,'CALENDAR_CURRENT_PERIOD'),'little')
    row={**date_columns(current,'current_'),'period_raw':period,'period_label':enum_label('SEASON_TIMEPERIOD',period)}
    for column,name in [('current_index_raw','CurrentIndex'),('next_index_raw','NextIndex')]:row[column]=int.from_bytes(read(s[name]['offset'],4,'CALENDAR_'+name),'little')
    schedule=s['Schedule']['offset'];count=int.from_bytes(read(schedule+g['NumberOfGames']['offset'],4,'CALENDAR_DECLARED_GAME_COUNT'),'little')
    if count!=slot10_count or not 0<=count<=GAME_CAPACITY:raise ValueError('native schedule count differs from actual Slot10 window')
    row.update({'declared_game_count_raw':count,'source_slot10_count_raw':slot10_count,'game_capacity_verified':GAME_CAPACITY})
    for column,name in [('next_game_id_raw','NextGameId'),('allstar_game_index_raw','AllstarGameIndex'),('rookie_sophomore_game_index_raw','RookieSophomoreGameIndex')]:row[column]=int.from_bytes(read(schedule+g[name]['offset'],4,'CALENDAR_'+name),'little')
    cursor=int.from_bytes(read(s['BoxScoreStatBank']['offset']+bank['CurrentStatLine']['offset'],4,'CALENDAR_BOX_STAT_LINE_CURSOR'),'little')
    if cursor>STAT_CAPACITY:raise ValueError('native Box stat cursor exceeds verified capacity')
    row.update({'box_current_stat_line_raw':cursor,'box_stat_capacity_verified':STAT_CAPACITY})
    for offset,raw,label in controls:
        if reader.read(season+offset,len(raw),label+'_RECHECK')!=raw:raise ValueError('native calendar controls changed')
    return row
