"""Native school/catalog labels and independent classification flags."""
import json
from pathlib import Path
from player_detail_codec import native_unsigned
PROFILE_PATH=Path(__file__).with_name('player_affiliation_native_profile.json');PROFILE=json.loads(PROFILE_PATH.read_bytes())
LAYOUT='CURRENT_PLAYERDATA_AFFILIATION_AND_CLASSIFICATION_V1'

def label(type_name,raw):
    entry=PROFILE['enum_labels'].get(type_name,{}).get(str(raw));values=entry['labels'] if entry else []
    return values[0] if len(values)==1 else None

def decode_classification(raw):
    if len(raw)!=1264:raise ValueError('PLAYER projection must have1264 positions')
    values={name:native_unsigned(raw,f) for name,f in PROFILE['player_fields'].items()}
    values.update({'native_player_type_label':label('PLAYERDATA_TYPE',values['native_player_type_raw']),
        'g_league_team_label':label('GLEAGUE_TEAM_ID',values['g_league_team_raw']),'free_agency_type_label':label('FREE_AGENCY_TYPE',values['free_agency_type_raw'])})
    return values

def reconstruct_college_projection(packed):
    ranges=PROFILE['college_public_ranges']
    if len(packed)!=sum(b-a for a,b in ranges):raise ValueError('incomplete college public projection')
    raw=bytearray(60);at=0
    for low,high in ranges:raw[low:high]=packed[at:at+high-low];at+=high-low
    return bytes(raw)

def decode_college(raw):
    if len(raw)!=60:raise ValueError('COLLEGEDATA projection must have60 positions')
    values={name:native_unsigned(raw,f) for name,f in PROFILE['college_fields'].items() if name!='native_label'}
    field=PROFILE['college_fields']['native_label'];prefix=raw[:field['array_extent']].split(b'\0',1)[0]
    if any(b<32 or b==127 for b in prefix):text=None;status='INVALID_CONTROL_IN_NATIVE_NAME'
    else:
        try:text=prefix.decode('utf-8').strip() or None;status='UTF8_OR_ASCII_PREFIX_OBSERVED'
        except UnicodeDecodeError:text=prefix.decode('latin1').strip() or None;status='LATIN1_PREFIX_CANDIDATE; UI_ENCODING_UNVERIFIED'
    values.update({'native_label':text,'name_encoding_status':status,'appearance_group_label':label('COLLEGEDATA_REGION',values['appearance_group_raw']),
        'source_scope_status':'NATIVE_COLLEGEDATA_REFERENT; SCHOOL_COUNTRY_CATEGORY_AND_COUNTRY_ID_SEMANTICS_UNVERIFIED'})
    return values
