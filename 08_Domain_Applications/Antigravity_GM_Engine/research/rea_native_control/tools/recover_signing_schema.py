"""Join pinned registered signing fields and recovered enum tables; no process access."""
import argparse
import json
import struct
import sys
from pathlib import Path

CONTROL=Path(__file__).resolve().parents[1]
ROOT=CONTROL.parents[3]
RUN=ROOT/'01_os/07_content/_runs/run-20261028-role-native-execution-system-001'
sys.path.insert(0,str(CONTROL.parent/'rea_native_action'))
from pe_local import Image


def recover(image):
    source=json.loads((CONTROL/'evidence/static/types-signing-02.json').read_text(encoding='utf8'))
    native=next(row for row in source['types'] if row['name']=='FRANCHISE_SIGNING')
    enums=json.loads((RUN/'static/sign_native_enums_007.json').read_text(encoding='utf8'))
    if enums['game_build_sha256']!=image.sha256 or enums['game_access']:raise ValueError('Pinned offline enum source required')
    by_descriptor={row['descriptor_rva']:row for row in enums['enums']}
    prefixes={'Status':'FRANCHISE_SIGNING_STATUS_','Type':'FRANCHISE_SIGNING_'}
    fields=[];enum_maps={}
    for field in native['fields']:
        if len(field['name_candidates'])!=1:raise ValueError('Unique registered field name required')
        name=field['name_candidates'][0];width=(field['format']>>8)&255;shift=(field['format']>>16)&255
        if not 0<width<=32 or shift+width>32:raise ValueError('Unqualified field format')
        item={'name':name,'offset':field['offset'],'width':width,'shift':shift,
            'signed':name=='PissedOffLevel','count':6 if name=='ForcedWage' else 1,
            'source_name_crc':field['crc'],'source_type_crc':field['type_crc']}
        reference=field['image_ref_rvas'][1]
        if reference is not None:
            enum=by_descriptor[reference]
            if enum['info_raw'][0]!=field['type_crc'] or any(row['name'] is None for row in enum['rows']):
                raise ValueError('Unqualified enum descriptor/type/name join')
            enum_maps[name]={str(row['value']):row['name'].removeprefix(prefixes.get(name,'')) for row in enum['rows']}
            item['enum']=name
        fields.append(item)
    forced=next(field for field in native['fields'] if field['name_candidates']==['ForcedWage'])
    array_info=image.read(forced['image_ref_rvas'][0],16)
    if struct.unpack_from('<I',array_info)[0]!=6 or forced['offset']!=8 or len(fields)!=25:
        raise ValueError('Six-slot signing array extent changed')
    return {'source_kind':'PINNED_NATIVE_SIGNING_SCHEMA_NOT_GAME_CAPTURE','game_build_sha256':image.sha256,
        'bytes':44,'fields':fields,'enums':enum_maps,
        'forced_wage_extent_proof':{'offset':8,'next_field_offset':32,'element_size':4,'elements':6,
            'static_array_reference_rva':forced['image_ref_rvas'][0],'static_array_info_hex':array_info.hex()},
        'pool':{'root_rva':0x632b478,'offset':0x1727a8,'count':1000,'stride':44},
        'evidence':['evidence/static/types-signing-02.json',
            (RUN/'static/sign_native_enums_007.json').relative_to(ROOT).as_posix(),
            (RUN/'static/sign_pool_lookup_and_allocate_003.json').relative_to(ROOT).as_posix()],
        'maturity':{'encoding_only':True,'fresh_offer_lifecycle_qualified':False,'dispatch_implemented':False,
            'ui_currency_and_term_legality':'UNVERIFIED_NATIVE_ENCODING_BOUNDS_ONLY',
            'accepted_is_not_signed':True,'signed_status_is_not_independent_membership_proof':True}}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args()
    output=Path(args.out)
    if output.exists():raise SystemExit('Existing evidence is immutable; select a new output')
    schema=recover(Image());output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(schema,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'fields':len(schema['fields']),'enum_values':sum(len(values) for values in schema['enums'].values()),
        'fresh_offer_lifecycle_qualified':False,'game_access':False}))
