"""Pure 8-byte defensive-setting codec; contains no object/activation guesses."""
from coach_codec import integer


def encode_defense(raw, changes, catalog):
    if not isinstance(raw,bytes) or len(raw)!=8 or not isinstance(changes,list) or not changes:
        raise ValueError('EXACT_DEFENSE_BLOCK_AND_CHANGES_REQUIRED')
    old=int.from_bytes(raw,'little')
    after=old
    mask=0
    names=[]
    for change in changes:
        if not isinstance(change,dict) or set(change)!={'field','before_raw','after_raw'}:
            raise ValueError('EXACT_CHANGE_CONTRACT_REQUIRED')
        name=change['field']
        if name not in catalog or name in names:
            raise ValueError('UNKNOWN_OR_DUPLICATE_DEFENSIVE_FIELD')
        field=catalog[name]
        shift=field['offset']*8+field['start_bit']
        width=field['width']
        if type(shift) is not int or type(width) is not int or width<1 or shift<0 or shift+width>64:
            raise ValueError('INVALID_DEFENSIVE_MASK')
        part=((1<<width)-1)<<shift
        if mask&part:
            raise ValueError('OVERLAPPING_DEFENSIVE_MASKS')
        legal={'0':None,'1':None} if field.get('native_boolean') is True and width==1 else field['native_enum_name_crc32']
        for value in (change['before_raw'],change['after_raw']):
            integer(value,0,(1<<width)-1,'INVALID_DEFENSIVE_ENUM')
            if str(value) not in legal:
                raise ValueError('INVALID_DEFENSIVE_ENUM')
        if ((old>>shift)&((1<<width)-1))!=change['before_raw']:
            raise ValueError('STALE_DEFENSIVE_VALUE')
        after=(after&~part)|(change['after_raw']<<shift)
        mask|=part
        names.append(name)
    return dict(size=8,before=raw.hex(),after=after.to_bytes(8,'little').hex(),mask=mask,fields=names)
