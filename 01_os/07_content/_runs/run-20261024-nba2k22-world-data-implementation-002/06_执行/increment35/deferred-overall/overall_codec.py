"""Native cache branch and explicitly qualified display-conversion candidates."""
import json,math,struct
from pathlib import Path
PROFILE_PATH=Path(__file__).with_name('overall_native_profile.json');PROFILE=json.loads(PROFILE_PATH.read_bytes());LAYOUT=PROFILE['layout']


def decode_overall(raw):
    if len(raw)!=1264:raise ValueError('reconstructed PLAYERDATA required')
    word=int.from_bytes(raw[364:368],'little');value=struct.unpack('<f',raw[364:368])[0];valid=(raw[796]>>6)&1;finite=math.isfinite(value)
    result={'cache_word_raw':word,'cache_value_f32':value if finite else None,'cache_valid_raw':valid,'native_float_result_f32':None,'display_input_kind':None,'display_scaled_nearest_f32':None,'display_nearest_even_candidate':None,'rounding_independent_integer':None,'availability_status':'INVALID_CACHE_NO_RECOMPUTATION','rounding_status':'NOT_APPLICABLE_INVALID_CACHE'}
    if not valid:return result
    if not finite:result.update(availability_status='VALID_FLAG_NONFINITE_CACHE_WORD_RETAINED',rounding_status='NOT_APPLICABLE_NONFINITE');return result
    result.update(native_float_result_f32=value,availability_status='VALID_FINITE_CACHE_NATIVE_FLOAT_BRANCH')
    rule=PROFILE['display_converter'];product=None
    if rule['normalized_min']<=value<=rule['normalized_max']:result['display_input_kind']='NORMALIZED_NATIVE_CONVERTER_BRANCH';product=value*rule['normalized_scale']
    elif rule['absolute_min']<=value<=rule['absolute_max']:result['display_input_kind']='ABSOLUTE_NATIVE_CONVERTER_BRANCH';product=value
    else:result['rounding_status']='OUTSIDE_VERIFIED_DISPLAY_CONVERTER_INPUT_DOMAIN';return result
    scaled=struct.unpack('<f',struct.pack('<f',product))[0];result['display_scaled_nearest_f32']=scaled;result['display_nearest_even_candidate']=round(scaled)
    # A float32 times100 is exact in Python float64 (at most31 significant bits).
    # Only an integral exact product/absolute input is invariant under SSE modes.
    if product.is_integer():result.update(rounding_independent_integer=int(product),rounding_status='EXACT_INTEGER_WITHOUT_MULTIPLICATION_OR_ROUNDING_AMBIGUITY')
    else:result['rounding_status']='ASSUMED_NEAREST_EVEN; GAME_THREAD_MXCSR_NOT_OBSERVED'
    return result
