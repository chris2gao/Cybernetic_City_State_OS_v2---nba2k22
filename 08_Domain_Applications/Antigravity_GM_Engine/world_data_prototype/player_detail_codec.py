"""Verified base badge bits and full native contract storage widths; no game I/O."""
import json
from pathlib import Path
PROFILE_PATH=Path(__file__).with_name('player_detail_native_profile.json')
PROFILE=json.loads(PROFILE_PATH.read_bytes())
LAYOUT='CURRENT_PLAYERDATA_CONTRACT_AND_BASE_BADGES_V1'

def native_unsigned(raw,field):
    offset=field['offset'];width=field['width'];shift=field['start_bit'];size=(shift+width+7)//8
    if not 1<=width<=64 or offset<0 or offset+size>len(raw):raise ValueError('incomplete native public field')
    return (int.from_bytes(raw[offset:offset+size],'little')>>shift)&((1<<width)-1)

def native_contracts(raw):
    if len(raw)!=1264:raise ValueError('PLAYER record must have exactly 1264 positions')
    return {name+'_raw':native_unsigned(raw,field) for name,field in PROFILE['contract_fields'].items()}

def native_badges(raw):
    if len(raw)!=1264:raise ValueError('PLAYER record must have exactly 1264 positions')
    rows=[];levels=PROFILE['enum_labels']['PLAYERDATA_BADGE_LEVEL']
    for key,field in sorted(PROFILE['badge_fields'].items(),key=lambda pair:pair[1]['badge_id']):
        if field['reserved']:continue
        value=native_unsigned(raw,field);kind=field['kind'];label=None
        if kind=='BOOLEAN':status='NATIVE_BOOLEAN_BADGE_FLAG';owned='owned' if value else 'not_owned'
        elif kind=='LEVEL':
            enum=levels.get(str(value))
            if enum and len(enum['labels'])==1:
                label=enum['labels'][0];status='NATIVE_BASE_LEVEL_ENUM; EFFECTIVE_CONTEXT_AND_UI_SEPARATE';owned='not_owned' if value==0 else 'owned'
            else:status='UNKNOWN_BASE_LEVEL_CODE_RETAINED';owned='unknown'
        else:raise ValueError('unsupported native badge field width')
        rows.append({'badge_key':key,'native_badge_id':field['badge_id'],'native_kind':kind,'native_code':value,
            'tier_label':label,'owned_state':owned,'native_level_status':status,
            'native_field_id':'CURRENT_PLAYERDATA_BADGE_V1:'+str(field['name_crc'])})
    return rows
