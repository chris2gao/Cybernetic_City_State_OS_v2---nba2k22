"""Native SeasonStats references; source association is not accepted ownership."""
import hashlib,json,struct
from pathlib import Path

PROFILE_PATH=Path(__file__).with_name('stat_reference_native_profile.json')
RULE='NATIVE_SIGNED_INT16_STAT_INDEX_V1'

def resolve_reference(index,position,record):
    if type(index) is not int or not 0<=index<=65535:raise ValueError('native stat index must be uint16')
    if type(position) is not int or not 0<=position<25:return 'OUTSIDE_VERIFIED_ARRAY_DIMENSION'
    if index>=32768:return 'NEGATIVE_SIGNED_INDEX_REJECTED_BY_NATIVE_GETTER'
    return 'RESOLVED_SAME_UNIT_NATIVE_RECORD' if record is not None else 'NO_SAME_UNIT_SOURCE_RECORD'

def verify_native_reference_contract(reader):
    """Read current metadata/code only. Never call a getter or alter game state."""
    from award_reader import PROFILE_PATH as award_profile,read_native_fields
    from live_reader import ROSTER_RVA
    profile=json.loads(PROFILE_PATH.read_bytes());award=json.loads(award_profile.read_bytes())
    metadata=read_native_fields(reader,next(t for t in award['types'] if t['name']=='PLAYERDATA'),1264,read_enums=False)
    field=next(f for f in metadata['fields'] if f['name_crc']==profile['season_stats_name_crc'])
    if any(field[k]!=v for k,v in profile['season_stats_field'].items()):raise ValueError('native SeasonStats field layout changed')
    if field['array_dimension_control_hex']!=profile['array_dimension_control_hex']:raise ValueError('native SeasonStats dimension changed')
    windows=[]
    for window in profile['code_windows']:
        expected=bytes.fromhex(window['code_hex']);actual=reader.read(reader.module_base+window['rva'],len(expected),'STAT_REFERENCE_CODE:'+window['role'])
        if actual!=expected:raise ValueError('native stat reference code changed: '+window['role'])
        windows.append({'role':window['role'],'rva':window['rva'],'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest()})
    if profile['roster_pointer_rva']!=ROSTER_RVA or profile['stat_descriptor_offset']!=24*16 or profile['stat_stride']!=48:raise ValueError('stat getter bank contract differs from source adapter')
    pointer=reader.read(reader.module_base+ROSTER_RVA,8,'STAT_REFERENCE_ROSTER_POINTER');root=int.from_bytes(pointer,'little')
    if root<0x10000:raise ValueError('invalid stat reference roster root')
    descriptor=reader.read(root+24*16,16,'STAT_REFERENCE_SLOT24_DESCRIPTOR');count,address=struct.unpack('<QQ',descriptor)
    if not 1<=count<=65535 or address<0x10000:raise ValueError('stat reference descriptor outside bounded source envelope')
    if reader.read(root+24*16,16,'STAT_REFERENCE_SLOT24_RECHECK')!=descriptor or reader.read(reader.module_base+ROSTER_RVA,8,'STAT_REFERENCE_ROSTER_RECHECK')!=pointer:raise ValueError('stat reference directory changed')
    return {'rule':RULE,'native_array_count':25,'metadata_status':metadata['status'],'windows':windows,'native_stat_count':count,'stat_stride':48,
            'scope':'Independent signed index and same-bank bounds; no phase, chronological order, record allocation or historical subject lifecycle inference',
            'game_writes':False,'getter_invocations':0}
