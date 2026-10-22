"""Bidirectional native values; coaching and defense delegate existing codecs."""
import math
import struct
from coach_codec import decode as coach_decode, encode_changes
from defense_codec import encode_defense


def decode(raw, field):
    f = field['layout']
    off, size = f['offset'], f['storage_bytes']
    part = raw[off:off+size]
    if len(part) != size:
        raise ValueError('INCOMPLETE_NATIVE_OBJECT')
    if f.get('encoding') == 'rating':
        from config import raw_to_rating
        return raw_to_rating(part[0])
    if f.get('encoding','').startswith('float32'):
        value = struct.unpack('<f', part)[0]
        if not math.isfinite(value):
            raise ValueError('NONFINITE_NATIVE_VALUE')
        return value*100 if f['encoding']=='float32_percent' else value
    return coach_decode(raw, f)


def validate_value(value, field, playbooks=()):
    f = field['layout']
    if f.get('encoding','').startswith('float32'):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError('FINITE_NUMBER_REQUIRED')
        try:
            encoded=struct.pack('<f',value/100 if f['encoding']=='float32_percent' else value)
        except (OverflowError,struct.error) as exc:
            raise ValueError('FLOAT32_VALUE_OUT_OF_RANGE') from exc
        if not math.isfinite(struct.unpack('<f',encoded)[0]):
            raise ValueError('FLOAT32_VALUE_OUT_OF_RANGE')
    else:
        if type(value) is not int or not 0 <= value < (1 << f['width']):
            raise ValueError('INVALID_NATIVE_INTEGER')
    if 'raw_range' in f and not f['raw_range'][0] <= value <= f['raw_range'][1]:
        raise ValueError('OUTSIDE_NATIVE_RANGE')
    enum = f.get('enum')
    if isinstance(enum, dict) and str(value) not in {str(k) for k in enum}:
        raise ValueError('INVALID_NATIVE_ENUM')
    if enum == 'LOADED_PLAYBOOKS' and value not in playbooks:
        raise ValueError('PLAYBOOK_NOT_LOADED')


def normalized_value(value, field):
    """Compare against the actual native float32 value, not an ideal decimal."""
    encoding=field['layout'].get('encoding','')
    if encoding.startswith('float32'):
        scale=100 if encoding=='float32_percent' else 1
        return struct.unpack('<f',struct.pack('<f',value/scale))[0]*scale
    return value


def encode_patch(raw, changes, registry, playbooks=()):
    """Return changed physical blocks only; merge masks against full preimages."""
    for key, value in changes.items():
        validate_value(value, registry.field(key), playbooks)
    first = registry.field(next(iter(changes)))
    if first['native_codec'] == 'coach_codec':
        return encode_changes(raw, [dict(field=k.split('.',1)[1], before_raw=decode(raw,registry.field(k)), after_raw=v)
                                    for k,v in changes.items()], registry.coach_profile, playbooks, for_write=True)
    if first['native_codec'] == 'defense_codec':
        return [dict(encode_defense(raw, [dict(field=k.split('.',1)[1], before_raw=decode(raw,registry.field(k)),after_raw=v)
                                         for k,v in changes.items()], registry.coach_profile['defensive_fields']), offset=0)]
    groups = {}
    for key, value in changes.items():
        f = registry.field(key)['layout']
        off, size = f['offset'], f['storage_bytes']
        offsets = [off]
        if 'mirror_delta' in f:
            offsets.append(off+f['mirror_delta'])
        for at in offsets:
            before = raw[at:at+size]
            if len(before) != size:
                raise ValueError('INCOMPLETE_NATIVE_BLOCK')
            group = groups.setdefault((at,size), dict(offset=at,size=size,before=before.hex(),after=before.hex(),mask=0,fields=[]))
            shift = f.get('start_bit',0)
            mask = ((1 << f.get('width',size*8))-1) << shift
            if group['mask'] & mask:
                raise ValueError('OVERLAPPING_FIELD_MASKS')
            if f.get('encoding','').startswith('float32'):
                after = struct.pack('<f', value/100 if f['encoding']=='float32_percent' else value)
            elif f.get('encoding') == 'rating':
                from config import rating_to_raw
                after = bytes([rating_to_raw(value)])
            else:
                previous = int.from_bytes(bytes.fromhex(group['after']), 'little')
                after = ((previous & ~mask) | (value << shift)).to_bytes(size, 'little')
            group['after'] = after.hex()
            group['mask'] |= mask
            group['fields'].append(key)
    return sorted(groups.values(), key=lambda g:g['offset'])
