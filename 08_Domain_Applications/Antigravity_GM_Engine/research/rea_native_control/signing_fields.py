"""Native signing record codec and explicit private proposal encoding only.

Encoding never invokes acquire/reset, GenerateContract, OfferContract or Process.
A correctly encoded44-byte object is not a qualified fresh offer lifecycle.
"""
import json
from pathlib import Path


def load_schema(root=None):
    return json.loads(((Path(root) if root else Path(__file__).parent)/'data/signing_schema.json').read_text(encoding='utf8'))


def decode_record(raw,schema=None):
    schema=schema or load_schema()
    if len(raw)!=schema['bytes']:raise ValueError('Exact44-byte Native signing record required')
    values={}
    for field in schema['fields']:
        output=[]
        for index in range(field['count']):
            offset=field['offset']+index*4
            width,shift=field['width'],field['shift']
            value=(int.from_bytes(raw[offset:offset+4],'little')>>shift)&((1<<width)-1)
            if field['signed'] and value&(1<<(width-1)):value-=1<<width
            output.append(value)
        values[field['name']]=output if field['count']>1 else output[0]
    return values


def encode_explicit_contract(player_id,team_id,contract,*,schema=None):
    """Build private input bytes with explicit terms and EMPTY status, not a game offer."""
    schema=schema or load_schema()
    if any(type(value) is not int or not 0<=value<65535 for value in (player_id,team_id)):
        raise ValueError('Explicit non-sentinel Player/Team UIDs required')
    required={'signing_type','annual_wages_native','years_native','option_type','contract_type','distribution','no_trade_clause'}
    if not isinstance(contract,dict) or set(contract)!=required:raise ValueError('Exact explicit Native contract fields required')
    wages=contract['annual_wages_native']
    if not isinstance(wages,list) or len(wages)!=6 or any(type(value) is not int or not 0<=value<2**32 for value in wages):
        raise ValueError('Six explicit Native uint32 wage values required; no pricing/defaults')
    if type(contract['years_native']) is not int or not 0<=contract['years_native']<=7:
        raise ValueError('Years is a Native3-bit encoding; legal terms are not certified')
    if type(contract['no_trade_clause']) is not bool:raise ValueError('Explicit no-trade boolean required')
    named={'Type':'signing_type','OptionType':'option_type','ContractType':'contract_type','Distribution':'distribution'}
    chosen={}
    for native,key in named.items():
        matches=[int(value) for value,name in schema['enums'][native].items() if name==contract[key]]
        if len(matches)!=1:raise ValueError('Unknown Native signing enum: '+key)
        chosen[native]=matches[0]
    values={'PlayerId':player_id,'TeamId':team_id,'Wage':wages[0],'ForcedWage':wages,
        'Years':contract['years_native'],'NoTradeClause':int(contract['no_trade_clause']),**chosen}
    raw=bytearray(44)
    for field in schema['fields']:
        value=values.get(field['name'],[0]*field['count'] if field['count']>1 else 0)
        sequence=value if field['count']>1 else [value]
        for index,item in enumerate(sequence):
            offset=field['offset']+index*4;width=field['width'];shift=field['shift']
            # UID fields share one DWORD; all bitfield neighbors remain untouched.
            size=4 if offset+4<=44 else 44-offset
            word=int.from_bytes(raw[offset:offset+size],'little')
            mask=((1<<width)-1)<<shift
            word=(word&~mask)|((item&((1<<width)-1))<<shift)
            raw[offset:offset+size]=word.to_bytes(size,'little')
    decoded=decode_record(raw,schema)
    assert decoded['Status']==0 and not decoded['HasMadeVerbalDeal'] and not decoded['ForcedOffer']
    return bytes(raw)


def validate_pool_query(parameters,schema=None):
    schema=schema or load_schema()
    if not isinstance(parameters,dict) or set(parameters)!={'team_id','statuses','include_archived'}:raise ValueError('Exact signing pool query required')
    if type(parameters['team_id']) is not int or not 0<=parameters['team_id']<65535:raise ValueError('Native Team UID required')
    statuses=parameters['statuses'];allowed=set(schema['enums']['Status'].values())-{'EMPTY'}|{'UNRECOGNIZED'}
    if not isinstance(statuses,list) or not statuses or any(type(name) is not str for name in statuses) or len(set(statuses))!=len(statuses) or set(statuses)-allowed:
        raise ValueError('Explicit nonempty unique status names required; EMPTY is not an offer')
    if type(parameters['include_archived']) is not int or parameters['include_archived'] not in (0,1):
        raise ValueError('Explicit archive inclusion0/1 required')
    return tuple(statuses)


def contract_parameter_schema(schema=None):
    """Role-readable input types; encoding knowledge never promotes dispatch."""
    schema=schema or load_schema()
    enums={'signing_type':'Type','option_type':'OptionType','contract_type':'ContractType','distribution':'Distribution'}
    properties={key:{'type':'string','enum':list(schema['enums'][native].values()),
        'description':'Recovered internal Native enum; current UI availability is unverified'} for key,native in enums.items()}
    properties.update(annual_wages_native={'type':'array','minItems':6,'maxItems':6,
        'items':{'type':'integer','minimum':0,'maximum':2**32-1},
        'description':'Six exact Native wage slots, including explicit unused zeros; no default price or unit conversion'},
        years_native={'type':'integer','minimum':0,'maximum':7,
            'description':'Native3-bit encoding bounds only; legal duration and option-year meaning unverified'},
        no_trade_clause={'type':'boolean','description':'Explicit supplied clause bit; eligibility unverified'})
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False,
        'description':'Private explicit-term encoding only; fresh offer lifecycle and runtime dispatch remain unresolved'}


def validate_fa_offer_contract(contract,schema=None):
    """Qualified exact-term FA-period subset; reject unsupported terms, never replace them."""
    schema=schema or load_schema()
    encode_explicit_contract(0,0,contract,schema=schema)
    if contract['signing_type']!='FREE_AGENT' or contract['contract_type'] not in {'NORMAL','HARDSHIP'} or contract['distribution']!='CUSTOM':
        raise ValueError('Recovered offer path requires FREE_AGENT NORMAL/HARDSHIP and explicit CUSTOM wages')
    years=contract['years_native'];wages=contract['annual_wages_native']
    counts={'NO_OPTION':0,'TEAM_OPTION':1,'PLAYER_OPTION':1,'TEAM_OPTION_2':2}
    if not 1<=years<=6 or years<counts[contract['option_type']]:
        raise ValueError('Exact1..6 total years must contain the selected Native option years')
    if any(not 0<value<=2147483647 for value in wages[:years]) or any(wages[years:]):
        raise ValueError('Active wage slots must be positive31-bit values and unused slots explicitly zero')
    return contract


def encode_fresh_fa_offer(template,player_id,team_id,contract,*,schema=None):
    """Model the registered POD initializer on private bytes; never acquire/reset a live record."""
    schema=schema or load_schema();validate_fa_offer_contract(contract,schema)
    if decode_record(template,schema)['Status']!=0:raise ValueError('Fresh constructor requires an observed EMPTY pool template')
    raw=bytearray(encode_explicit_contract(player_id,team_id,contract,schema=schema))
    word=int.from_bytes(raw[32:36],'little')|(1<<18)|(3<<8)
    raw[32:36]=word.to_bytes(4,'little')
    preserved=int.from_bytes(template[40:44],'little')&0xffffe000
    raw[40:44]=(int.from_bytes(raw[40:44],'little')|preserved).to_bytes(4,'little')
    return bytes(raw)


def validate_pending_offer(parameters,schema=None):
    """Require every registered observed field, never a partial or guessed cancellation target."""
    schema=schema or load_schema()
    if not isinstance(parameters,dict) or set(parameters)!={'player_id','team_id','expected_offer'}:
        raise ValueError('Exact Team/Player and full expected offer required')
    for name in ('player_id','team_id'):
        if type(parameters[name]) is not int or not 0<=parameters[name]<65535:
            raise ValueError('Explicit Native UID required')
    expected=parameters['expected_offer']
    if not isinstance(expected,dict) or set(expected)!={field['name'] for field in schema['fields']}:
        raise ValueError('Every registered offer field must be supplied from the selected observation')
    for field in schema['fields']:
        value=expected[field['name']]
        values=[value] if field['count']==1 else value
        if not isinstance(values,list) or len(values)!=field['count']:
            raise ValueError('Exact registered field extent required')
        low=-(2**(field['width']-1)) if field['signed'] else 0
        high=2**(field['width']-int(field['signed']))-1
        if any(type(item) is not int or not low<=item<=high for item in values):
            raise ValueError('Expected offer field outside registered representation')
    if (expected['PlayerId'],expected['TeamId'],expected['Type'],expected['Status'],expected['IsArchived']) != (
            parameters['player_id'],parameters['team_id'],2,1,0):
        raise ValueError('Only the exact unarchived OFFERED FREE_AGENT record can be withdrawn')
    return expected


def pending_offer_parameter_schema(schema=None):
    schema=schema or load_schema();properties={}
    for field in schema['fields']:
        value={'type':'integer','minimum':-(2**(field['width']-1)) if field['signed'] else 0,
               'maximum':2**(field['width']-int(field['signed']))-1}
        properties[field['name']]=value if field['count']==1 else {
            'type':'array','minItems':field['count'],'maxItems':field['count'],'items':value}
    return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False,
            'description':'Complete registered fields from the explicitly selected current team-offer observation; Status1 Type2 archive0 and exact UIDs required'}
