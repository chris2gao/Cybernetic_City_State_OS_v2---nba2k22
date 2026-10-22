"""Deferred signing implementation. NOT RUN / NOT TESTED / LIVE WRITES DISABLED.

Contract packing and target-roster association use original-byte images. GM has
already decided the player, target and exact contract. No bidding, selection,
CBA policy, expiry classification or native negotiation is performed here.
Technical field/layout validation is deferred to the player's later signing task.
"""
from pathlib import Path
import struct

from source_extensions import profile as field_profile,player_details
from roster_associations import describe
from approved_trade_executor import identity,read_exact,dump,now

VERSION='approved_signing_v1_unvalidated'
SIGNING_LAYOUT_VALIDATED=False
SIGNING_EXECUTION_ENABLED=False
OPTION_CODES={'NONE':0,'NULL':0,'TEAM_OPTION':1,'PLAYER_OPTION':2,'2_YEAR_TEAM_OPTION':3}


def integer(value,label,minimum,maximum):
    if type(value) is not int or not minimum<=value<=maximum:
        raise ValueError(f'{label} must be an exact integer in {minimum}..{maximum}')
    return value


def contract_values(offer):
    """Amounts are exact approved integer dollars; never generate a GM offer."""
    salaries=offer.get('salaries',offer.get('salary_sequence'))
    if not isinstance(salaries,list) or not 1<=len(salaries)<=6:
        raise ValueError('One to six approved annual salary amounts required')
    if any(type(v) is not int or not 1<=v<=0x7fffffff for v in salaries):
        raise ValueError('Annual salary must be a positive 31-bit integer; no floats or truncation')
    option=offer.get('option')
    if option not in OPTION_CODES:
        raise ValueError('Explicit approved NONE / TEAM_OPTION / PLAYER_OPTION / 2_YEAR_TEAM_OPTION required')
    years=integer(offer.get('years_left',len(salaries)),'years_left',1,6)
    original=integer(offer.get('original_years',years),'original_years',1,6)
    values={f'contract_year_{i+1}':v for i,v in enumerate(salaries+[0]*(6-len(salaries)))}
    values.update(years_left_on_contract=years,original_contract_years=original,contract_option=OPTION_CODES[option])
    if 'contract_type' in offer:
        if offer['contract_type']!='CORE':
            raise ValueError('Only explicitly approved ordinary CORE signing is prepared; two-way and special types need separate linkage validation')
        values['contract_type']=0
    if 'no_trade' in offer:
        values['no_trade']=integer(offer['no_trade'],'approved no_trade',0,1)
    return values


def encode_contract(original,offer):
    if len(original)!=0x4f0:
        raise ValueError('Full observed current player record required')
    result=bytearray(original)
    definitions={f['name']:f for f in field_profile()['fields']['PLAYER'] if f['group']=='contract'}
    changed_fields=[]
    for key,value in contract_values(offer).items():
        field=definitions[key]
        start,bits=field.get('start_bit',0),field.get('bits',field.get('bytes',0)*8)
        if not 0<=value<(1<<bits):
            raise ValueError('Approved contract field overflows '+key)
        size=(start+bits+7)//8
        offset=field['offset']
        old=int.from_bytes(result[offset:offset+size],'little')
        mask=((1<<bits)-1)<<start
        new=(old & ~mask)|(value<<start)
        result[offset:offset+size]=new.to_bytes(size,'little')
        changed_fields.append({'name':key,'offset':offset,'size':size,'start_bit':start,'bits':bits,
                               'before':(old>>start)&((1<<bits)-1),'target':value})
    return bytes(result),changed_fields


def build_signing_plan(context,request):
    """Build a draft from machine-captured context; never certifies eligibility.

    Context must be captured afresh at the later signing task. A non-NBA source
    team with its own free-agent roster is explicitly unsupported until located.
    No cross-season slot shift or clearing of old extensions is guessed here.
    """
    old=bytes.fromhex(context['player_raw'])
    team=bytes.fromhex(context['target_team_raw'])
    expected_identity=context.get('player_identity',request['player'])
    for key,value in request['player'].items():
        if key in ('name','face_id','birth_date') and value is not None and str(expected_identity.get(key)).casefold()!=str(value).casefold():
            raise ValueError('Captured signing identity differs from GM-approved player')
    if not identity(old,expected_identity):
        raise ValueError('Signing target identity differs from approved player')
    current,contract=struct.unpack_from('<Q',old,0x60)[0],struct.unpack_from('<Q',old,0xa8)[0]
    target=context['target_team_address']
    if str(request['to_team']).upper() not in (str(context['target_team_id']),str(context['target_team_abbreviation']).upper()):
        raise ValueError('Captured target team identity differs from approved target')
    player_address=context['player_address']
    kind=request.get('kind','FREE_AGENT_SIGNING')
    if kind not in ('FREE_AGENT_SIGNING','RENEWAL_REPLACE_CURRENT_CONTRACT'):
        raise ValueError('Unknown signing kind; next-year extensions are not implemented')
    if not describe(team)['valid']:
        raise ValueError('Target roster/count state is inconsistent')
    roster=list(struct.unpack_from('<25Q',team))
    team_after=bytearray(team)
    already_signed=False
    if kind=='FREE_AGENT_SIGNING':
        if current==target and contract==target and roster.count(player_address)==1:
            if encode_contract(old,request['contract'])[0]!=old:
                raise ValueError('Player is already on target but contract differs; explicit renewal scope required')
            already_signed=True
        elif current or contract or player_address in roster:
            raise ValueError('A real free-agent pool/team linkage needs independent source implementation; no pointer-only release')
        else:
            count=team[0xcb1]
            if count>=15:
                raise ValueError('No regular roster vacancy; do not waive another player implicitly')
            struct.pack_into('<Q',team_after,count*8,player_address)
            team_after[0xcb1]=count+1
    else:
        if current!=target or contract!=target or roster.count(player_address)!=1:
            raise ValueError('Renewal requires matching current team, contract team and one roster slot')
    changed,fields=encode_contract(old,request['contract'])
    player_after=bytearray(changed)
    struct.pack_into('<Q',player_after,0x60,target)
    struct.pack_into('<Q',player_after,0xa8,target)
    if not describe(bytes(team_after))['valid']:
        raise ValueError('Signing would leave invalid native roster counts')
    patches=[]
    # Whole uint64 pointers and whole bitfield storage units; never a pointer's low bytes only.
    regions={'PLAYER':[(0x60,8),(0xa8,8)]+[(field['offset'],field['size']) for field in fields],
             'TARGET_TEAM':[(index*8,8) for index in range(15)]+[(0xcb1,1)]}
    for label,address,before,after in (
        ('PLAYER',player_address,old,bytes(player_after)),
        ('TARGET_TEAM',target,team,bytes(team_after))):
        merged=[]
        for offset,size in sorted(set(regions[label])):
            if merged and offset<merged[-1][1]:
                merged[-1]=(merged[-1][0],max(merged[-1][1],offset+size))
            else:
                merged.append((offset,offset+size))
        covered=set()
        for offset,end in merged:
            covered.update(range(offset,end))
            if before[offset:end]!=after[offset:end]:
                patches.append({'entity':label,'offset':offset,'address':address+offset,
                                'before':before[offset:end].hex(),'after':after[offset:end].hex()})
        if any(before[index]!=after[index] and index not in covered for index in range(len(before))):
            raise ValueError('Signing plan changed a byte outside approved ownership/contract/roster fields')
    return {'executor_version':VERSION,'status':'NO_WRITE_NEEDED' if already_signed else 'DRAFT_UNVALIDATED_NOT_EXECUTABLE',
        'action_id':request['action_id'],'save_id':request['save_id'],'season':request['season'],
        'player_identity':expected_identity,'kind':kind,'contract_fields':fields,
        'process':context['process'],'player_address':player_address,'target_team_address':target,
        'player_before':old.hex(),'player_expected':bytes(player_after).hex(),
        'team_before':team.hex(),'team_expected':bytes(team_after).hex(),'patches':patches,
        'source_admission':'TECHNICAL_LAYOUT_PENDING_LIVE_VALIDATION',
        'deferred_validation':['current model and free-agent linkage where applicable',
                               'approved salary year-slot encoding','game UI and save/reload persistence'],
        'database':'NOT_SYNCED','approval_basis':request.get('approval_basis','')}


def capture_signing_context(mem,request,allow_already_target=False):
    """Future read-only locator. It does not decide who is eligible or worth signing."""
    from approved_trade_executor import observe,name,player_row
    from trade_request import team_id
    state=observe(mem,int(request['season'].split('-')[1]))
    target_id=team_id(request['to_team'],state)
    table=state['directory']['players']
    expected=request['player']
    matches=[]
    for index in range(table['count']):
        address=table['address']+index*table['stride']
        header=read_exact(mem,address,80)
        if name(header).casefold()!=expected['name'].strip().casefold():
            continue
        raw=read_exact(mem,address,0x4f0)
        row=player_row(raw,state['team_ids'])
        if any(key in expected and expected[key] is not None and expected[key]!=row[key]
               for key in ('face_id','birth_date')):
            continue
        source=struct.unpack_from('<Q',raw,0x60)[0]
        contract=struct.unpack_from('<Q',raw,0xa8)[0]
        members=state['members'].get(address,[])
        if request.get('kind','FREE_AGENT_SIGNING')=='FREE_AGENT_SIGNING':
            already_target=(source==state['teams'][target_id]['address'] and contract==source and
                            len(members)==1 and members[0][0]==target_id)
            if (members or source or contract) and not (allow_already_target and already_target):
                continue  # Non-null FA team linkage needs a verified adapter, not a guessed pointer clear.
        else:
            if len(members)!=1 or members[0][0]!=target_id:
                continue
        matches.append((address,raw,row))
    if len(matches)!=1:
        raise ValueError('Signing model missing/ambiguous, or source FA linkage is not yet supported; resolve exact model/layout in the signing task')
    address,raw,row=matches[0]
    return {'process':{k:state[k] for k in ('pid','module_base','creation_time','root')},
            'player_address':address,'player_raw':raw.hex(),
            'player_identity':{k:row[k] for k in ('name','face_id','birth_date')},
            'target_team_address':state['teams'][target_id]['address'],
            'target_team_id':target_id,'target_team_abbreviation':state['teams'][target_id]['abbreviation'],
            'target_team_raw':state['team_raw'][target_id].hex()}


def verify_signing_plan(mem,plan):
    player=read_exact(mem,plan['player_address'],0x4f0)
    team=read_exact(mem,plan['target_team_address'],0x1258)
    expected_team=bytes.fromhex(plan['team_expected'])
    checks={'player_record_exact':player==bytes.fromhex(plan['player_expected']),
            'identity':identity(player,plan['player_identity']),
            'target_roster_exact':team[:0xc8]==expected_team[:0xc8],
            'native_roster_counts':describe(team)['valid']}
    from approved_trade_executor import observe
    live=observe(mem,int(plan['season'].split('-')[1]))
    target_id=next((tid for tid,record in live['teams'].items() if record['address']==plan['target_team_address']),None)
    placements=live['members'].get(plan['player_address'],[])
    checks['one_target_roster_membership']=len(placements)==1 and placements[0][0]==target_id
    return {'checks':checks,'verified':all(checks.values()),
            'contract_readback':player_details(player)['contract'],'observed_at':now()}


def execute_signing_plan(mem,plan,output,human_approval_confirmed=False):
    """Prepared write/readback implementation; unreachable while deferred gates are false."""
    if not SIGNING_LAYOUT_VALIDATED or not SIGNING_EXECUTION_ENABLED:
        raise PermissionError('Signing writes disabled until the player-triggered technical validation; JSON flags cannot enable them')
    if not human_approval_confirmed or mem.read_only:
        raise PermissionError('Specific signing approval and explicit write handle required')
    if plan['process']['pid']!=mem.pid or plan['process']['module_base']!=mem.base_address:
        raise ValueError('Signing process identity changed')
    from approved_trade_executor import observe
    live=observe(mem,int(plan['season'].split('-')[1]))
    if any(live[k]!=plan['process'][k] for k in ('pid','module_base','creation_time','root')):
        raise ValueError('Signing process start identity or roster directory changed')
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    if (out/'WRITE_ATTEMPTED').exists():
        raise RuntimeError('Prior signing attempt exists; inspect current state, never replay')
    if read_exact(mem,plan['player_address'],0x4f0)!=bytes.fromhex(plan['player_before']):
        raise ValueError('Player changed since signing plan')
    if read_exact(mem,plan['target_team_address'],0x1258)!=bytes.fromhex(plan['team_before']):
        raise ValueError('Team changed since signing plan')
    receipt={'executor_version':VERSION,'action_id':plan['action_id'],'status':'PRECONDITION_FAILED',
             'started_at':now(),'journal':[],'write_calls':0,'database':'NOT_SYNCED',
             'persistence':'PERSISTENCE_NOT_VERIFIED'}
    dump(out/'plan.json',plan)
    if plan['status']=='NO_WRITE_NEEDED':
        receipt['verification']=verify_signing_plan(mem,plan)
        receipt['status']='NO_WRITE_NEEDED' if receipt['verification']['verified'] else 'PRECONDITION_FAILED'
        dump(out/'receipt.json',receipt)
        return receipt
    try:
        for item in plan['patches']:
            original=bytes.fromhex(item['before'])
            if read_exact(mem,item['address'],len(original))!=original:
                raise ValueError('Signing write-before comparison failed')
            step={**item,'status':'WRITE_RESULT_UNKNOWN'}
            receipt['journal'].append(step)
            receipt['status']='WRITE_RESULT_UNKNOWN'
            (out/'WRITE_ATTEMPTED').touch(exist_ok=True)
            dump(out/'receipt.json',receipt)
            receipt['write_calls']+=1
            ok=mem.write_bytes(item['address'],bytes.fromhex(item['after']))
            raw=mem.read_bytes(item['address'],len(original))
            step['readback']=raw.hex() if raw is not None else None
            if not ok or step['readback']!=item['after']:
                raise OSError('Signing write/readback failed; stop subsequent operations')
            step['status']='READBACK_MATCHED'
            dump(out/'receipt.json',receipt)
        receipt['verification']=verify_signing_plan(mem,plan)
        receipt['status']='EXECUTED_VERIFIED' if receipt['verification']['verified'] else 'PARTIALLY_APPLIED'
    except Exception as exc:
        receipt['error']=f'{type(exc).__name__}: {exc}'
        if any(s['status']=='READBACK_MATCHED' for s in receipt['journal']):
            receipt['status']='PARTIALLY_APPLIED'
    receipt['completed_at']=now()
    dump(out/'receipt.json',receipt)
    return receipt
