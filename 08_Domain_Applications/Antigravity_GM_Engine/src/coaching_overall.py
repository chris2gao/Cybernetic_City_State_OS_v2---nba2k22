"""Pure representation of the PC UI's overall-defense bulk operation.

UI evidence shows no special All row: it sets the chosen field on every present
opponent matchup. Empty slots, defender assignments and other fields are retained.
"""
import hashlib
import json


def overall_from_raw(raw,rule,catalog):
    selector=rule.get('record_selector')
    if not selector:
        return None
    if selector.get('mode')!='UI_BULK_ALL_PRESENT_MATCHUPS':
        raise ValueError('UNVERIFIED_OVERALL_STORAGE_MODE')
    start,stride,count=(selector[k] for k in ('entry_start','entry_stride','entry_count'))
    if (start,stride,count)!=(0x64,12,23) or len(raw)!=0x370:
        raise ValueError('UNVERIFIED_OVERALL_ARRAY_LAYOUT')
    if raw[0] not in (0,1):
        raise ValueError('UNKNOWN_GAMEPLAN_COMMIT_FLAG')
    blocks=[]
    for index in range(count):
        offset=start+index*stride
        matchup=int.from_bytes(raw[offset:offset+2],'little')
        defender=int.from_bytes(raw[offset+2:offset+4],'little')
        if matchup==65535:
            continue
        data=raw[offset+4:offset+12]
        values={}
        for name,field in catalog.items():
            shift=field['offset']*8+field['start_bit']
            value=(int.from_bytes(data,'little')>>shift)&((1<<field['width'])-1)
            legal={'0','1'} if field.get('native_boolean') is True and field['width']==1 else field['native_enum_name_crc32']
            if str(value) not in legal:
                raise ValueError('UNKNOWN_DEFENSIVE_ENUM')
            values[name]=value
        blocks.append(dict(settings_offset=offset+4,identity=dict(matchup_id=matchup,defender_id=defender),
            raw_block=data.hex(),values=values))
    ids=[b['identity']['matchup_id'] for b in blocks]
    if not ids or len(ids)!=len(set(ids)):
        raise ValueError('EMPTY_OR_DUPLICATE_OVERALL_MATCHUP_GROUP')
    binding=[dict(settings_offset=b['settings_offset'],**b['identity']) for b in blocks]
    identity=dict(storage='UI_BULK_ALL_PRESENT_MATCHUPS',entry_count=len(blocks),
        ordered_matchup_identity_sha256=hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest())
    values={name:blocks[0]['values'][name] if len({b['values'][name] for b in blocks})==1 else None for name in catalog}
    return dict(status='OBSERVED_OVERALL_VERIFIED',identity=identity,header_signature=raw[:6].hex(),
        values=values,blocks=blocks,commit_flag_raw=raw[0],
        mixed_fields=[name for name,value in values.items() if value is None],
        semantics='UI_OVERALL_BULK_PRESENT_OPPONENT_MATCHUPS_NOT_INDIVIDUAL_TARGETING')
