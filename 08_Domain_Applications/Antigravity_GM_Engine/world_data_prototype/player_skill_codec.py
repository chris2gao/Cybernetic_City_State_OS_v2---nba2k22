"""Current native public skill storage; no rating/UI conversion or getter call."""
import json
from pathlib import Path
from player_detail_codec import native_unsigned
PROFILE_PATH=Path(__file__).with_name('player_skill_native_profile.json');PROFILE=json.loads(PROFILE_PATH.read_bytes())
LAYOUT='CURRENT_PUBLIC_PLAYER_SKILLS_V1'

def play_label(code):
    value=PROFILE['play_type_enum'].get(str(code));return value['labels'][0] if value and len(value['labels'])==1 else None

def decode_skills(raw):
    if len(raw)!=1264:raise ValueError('PLAYER projection requires1264 positions')
    attrs={name:native_unsigned(raw,f) for name,f in PROFILE['attributes'].items()}
    tendencies={name:native_unsigned(raw,f) for name,f in PROFILE['tendencies'].items()}
    tendencies['is_play_initiator_raw']=native_unsigned(raw,PROFILE['initiator'])
    slots=[]
    for slot,f in PROFILE['play_types'].items():
        code=native_unsigned(raw,f);slots.append({'slot_index':int(slot),'native_play_code':str(code),'native_play_label':play_label(code)})
    return {'attributes':attrs,'tendencies':tendencies,'play_types':slots}
