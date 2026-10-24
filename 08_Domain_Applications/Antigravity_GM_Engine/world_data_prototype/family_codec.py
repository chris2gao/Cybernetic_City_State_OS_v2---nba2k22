"""Read-only public PLAYER family decoding from explicit registered layouts.

Bit widths describe storage, never legal UI ranges. Registration and a binary
fixture are separate evidence from current-process/UI verification.
"""
import hashlib
import json
import importlib.util
from functools import lru_cache
from schema_model import PROFILE,PLAYER_CONFIG,DOMAIN


@lru_cache(maxsize=1)
def _rating_codec():
    path=DOMAIN/'src/config.py'
    spec=importlib.util.spec_from_file_location('world_registered_rating_config',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.raw_to_rating


def registered_rating_candidate(raw):
    if type(raw) is not int or not 0<=raw<=255:
        return {'value':None,'status':'OUTSIDE_REGISTERED_BYTE_STORAGE'}
    return {'value':_rating_codec()(raw),'codec':'src/config.py:raw_to_rating',
            'status':'DERIVED_REGISTERED_CODEC','target_ui_validation':'NOT_OBSERVED'}


def extract_unsigned(raw,definition):
    offset=definition['offset']
    start=definition.get('start_bit',0)
    width=definition.get('bits',definition.get('bytes',0)*8)
    if type(offset) is not int or type(start) is not int or type(width) is not int:
        raise ValueError('integer layout required')
    if offset<0 or start<0 or not 1<=width<=64:raise ValueError('invalid unsigned field layout')
    size=(start+width+7)//8
    if offset+size>len(raw):raise ValueError('incomplete registered field read')
    return (int.from_bytes(raw[offset:offset+size],'little')>>start)&((1<<width)-1)


def public_player_families(raw):
    if len(raw)!=PROFILE['record_bytes']['PLAYER']:
        raise ValueError('PLAYER record must be exactly registered length')
    attrs={};contracts={}
    for definition in PROFILE['fields']['PLAYER']:
        name=definition['name']
        if name=='potential':continue
        value=extract_unsigned(raw,definition)
        if definition['group']=='attributes':attrs[('three_point_shot' if name=='3pt_shot' else name)+'_raw']=value
        elif definition['group']=='contract':contracts[name+'_raw']=value
    tendencies={}
    for name,offset in PLAYER_CONFIG['TENDENCY_OFFSETS'].items():
        if not 0<=offset<len(raw):raise ValueError('tendency outside PLAYER')
        tendencies[name.lower()+'_raw']=raw[offset]
    # Only names actually present in the registry are decoded. The other raw
    # tendency bytes remain unknown rather than acquiring guessed field names.
    play_types=[{'slot_index':i,'native_play_code':str((raw[0x168+i//2]>>(4*(i%2)))&15)} for i in range(4)]
    vitals={'last_name':raw[0:40].decode('utf-16le').split('\0')[0],
            'first_name':raw[40:80].decode('utf-16le').split('\0')[0]}
    return {'attributes':attrs,'contracts':contracts,'tendencies':tendencies,'play_types':play_types,'vitals':vitals,
            'source_status':'REGISTERED_LAYOUT_RESEARCH_FIXTURE_NOT_LIVE_UI_ACCEPTANCE',
            'family_completeness':{'attributes':'ALL_PUBLIC_REGISTERED_FIELDS','contracts':'ALL_REGISTERED_FIELDS',
                                   'tendencies':'NAMED_FIELDS_ONLY_NOT_ENTIRE_NATIVE_TENDENCY_FAMILY',
                                   'play_types':'FOUR_ORDERED_REGISTERED_SLOTS','badges':'UNKNOWN_ENCODING_NOT_DECODED'}}


def profile_layout_receipt():
    """Evidence for the apparent offset-833 alias: disjoint registered bit ranges."""
    definitions={f['name']:f for f in PROFILE['fields']['PLAYER']}
    a=definitions['original_contract_years'];b=definitions['extension_length']
    def span(d):return [d['offset']*8+d.get('start_bit',0),d['offset']*8+d.get('start_bit',0)+d['bits']-1]
    sa,sb=span(a),span(b)
    return {'source':'config/memory_field_profile.json','source_grade':'REGISTERED_BIT_LAYOUT',
            'original_contract_years':{'definition':a,'absolute_bit_span':sa},
            'extension_length':{'definition':b,'absolute_bit_span':sb},
            'registered_bits_overlap':max(sa[0],sb[0])<=min(sa[1],sb[1]),
            'current_game_semantics':'UNKNOWN_PENDING_TARGET_UI_OR_NATIVE_CONTROL',
            'profile_sha256':hashlib.sha256(json.dumps(PROFILE,sort_keys=True).encode()).hexdigest()}
