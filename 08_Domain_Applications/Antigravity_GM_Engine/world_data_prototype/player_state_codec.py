"""Typed native vitals/health/morale storage; no inferred clinical/UI state."""
import json,math,struct
from pathlib import Path
from player_detail_codec import native_unsigned
from family_codec import decode_fixed_utf16
PROFILE_PATH=Path(__file__).with_name('player_state_native_profile.json');PROFILE=json.loads(PROFILE_PATH.read_bytes())
LAYOUT='CURRENT_PLAYERDATA_VITALS_HEALTH_MORALE_V1'

def enum_label(type_name,value):
    entry=PROFILE['enum_labels'].get(type_name,{}).get(str(value));labels=entry['labels'] if entry else []
    return labels[0] if len(labels)==1 else None

def floating(raw,field):
    word=native_unsigned(raw,field);value=struct.unpack('<f',word.to_bytes(4,'little'))[0]
    return word,value if math.isfinite(value) else None,value.hex() if math.isfinite(value) else f'NONFINITE_NATIVE_FLOAT_WORD:{word:08x}'

def decode_player_state(raw,appearance=None,*,appearance_status='NO_NATIVE_APPEARANCE_POINTER'):
    if len(raw)!=1264:raise ValueError('PLAYER projection must have 1264 positions')
    groups=PROFILE['groups'];vitals={key:native_unsigned(raw,f) for key,f in groups['vitals'].items() if key!='weight'}
    word,value,text=floating(raw,groups['vitals']['weight']);vitals.update({'weight_raw':word,'weight_real':value,'weight_value_text':text,
        'weight_value_status':'NATIVE_FLOAT32_STORAGE; WEIGHT_UI_UNIT_UNVERIFIED','appearance_status':appearance_status})
    for name,part in (('last_name',raw[:40]),('first_name',raw[40:80])):
        try:vitals[name]=decode_fixed_utf16(part) or None
        except UnicodeDecodeError:vitals[name]=None
    if appearance is not None:
        if len(appearance)!=4:raise ValueError('appearance public extent must be exactly four bytes')
        vitals.update({key:native_unsigned(appearance,f) for key,f in groups['appearance'].items()})
        vitals['height_cm_native_derived']=vitals['height_raw']/100.0;vitals['wingspan_cm_native_derived']=vitals['wingspan_raw']/100.0
    else:vitals.update({'height_raw':None,'wingspan_raw':None,'height_cm_native_derived':None,'wingspan_cm_native_derived':None})
    for key,type_name in (('primary_position','PLAYERDATA_POSITION'),('secondary_position','PLAYERDATA_POSITION'),('tertiary_position','PLAYERDATA_POSITION')):
        vitals[key]=enum_label(type_name,vitals[key+'_raw'])
    vitals['handedness']=enum_label('PLAYERDATA_BESTHAND',vitals['best_hand_raw']);vitals['best_dunk_hand_label']=enum_label('PLAYERDATA_BESTDUNKHAND',vitals['best_dunk_hand_raw'])
    health={key:native_unsigned(raw,f) for key,f in groups['health'].items()}
    for slot in (1,2):
        health[f'injury{slot}_type_label']=enum_label('PLAYERDATA_INJURY',health[f'injury{slot}_type_raw'])
        health[f'injury{slot}_status_label']=enum_label('INJURY_STATUS',health[f'injury{slot}_status_raw'])
    morale={key:native_unsigned(raw,f) for key,f in groups['morale'].items() if key!='morale'}
    word,value,text=floating(raw,groups['morale']['morale']);morale.update({'morale_word_raw':word,'morale_real':value,'morale_value_text':text,
        'morale_value_status':'NATIVE_FLOAT32_STORAGE; UI_SCALE_AND_GLOBAL_SATISFACTION_NOT_INFERRED'})
    adjustment=morale['morale_event_adjustment_raw'];morale['morale_event_adjustment_signed']=adjustment-256 if adjustment>=128 else adjustment
    morale['morale_event_label']=enum_label('PLAYERDATA_MORALE_EVENT',morale['morale_event_type_raw']);morale['org_role_label']=enum_label('PLAYERDATA_ORG_ROLE',morale['org_role_raw'])
    return {'vitals':vitals,'health':health,'morale':morale}
