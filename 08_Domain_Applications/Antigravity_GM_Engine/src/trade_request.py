"""Resolve a player-friendly approved trade request into pinned live identities.

No process attachment, writes, approval inference, salary calculations or GM here.
"""
from datetime import date
import re
import struct

from approved_trade_executor import read_exact, name, player_row

ALIASES={'GS':'GSW','NY':'NYK','NO':'NOP','SA':'SAS','PHO':'PHX'}


def metadata(request, fallback_id='trade_request'):
    if request.get('example_only'):
        raise ValueError('Example template cannot execute; fill a concrete request and remove example_only')
    save_id=request.get('save_id','')
    request_id=request.get('request_id',fallback_id)
    for field,value in (('save_id',save_id),('request_id',request_id)):
        if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',value):
            raise ValueError(f'Invalid {field}')
    season=request.get('season','')
    match=re.fullmatch(r'(20\d{2})-(20\d{2})',season)
    if not match or int(match[2])!=int(match[1])+1 or not 2000<=int(match[2])<=2027:
        raise ValueError('Explicit supported season required, e.g. 2021-2022; native header support currently ends at 2027')
    if request.get('game_date'):
        date.fromisoformat(request['game_date'])
    actions=request.get('trades',request.get('actions',[]))
    if not isinstance(actions,list) or not actions:
        raise ValueError('At least one concrete trade is required')
    return {'save_id':save_id,'request_id':request_id,'season':season,'season_year':int(match[2]),
            'output':request.get('output') or f'_exports/execution/{save_id}/{request_id}',
            'policy_id':request.get('policy_id'), 'game_date':request.get('game_date'),
            'source_batch':request.get('source_batch','UNKNOWN'),
            'source_commit':request.get('source_commit','UNKNOWN'),
            'approval_basis':request.get('approval_basis',''), 'input_actions':actions}


def team_id(value,state):
    if type(value) is int:
        if value not in state['teams']:
            raise ValueError(f'Unknown current NBA team ID {value}')
        return value
    if not isinstance(value,str):
        raise ValueError('Team must be a current abbreviation or ID')
    wanted=ALIASES.get(value.upper().strip(),value.upper().strip())
    candidates=[tid for tid,t in state['teams'].items()
                if ALIASES.get(t['abbreviation'],t['abbreviation'])==wanted]
    if len(candidates)!=1:
        raise ValueError(f'Ambiguous/unknown current team {value}')
    return candidates[0]


def resolve_player(spec,state,mem):
    source,target=(team_id(spec[k],state) for k in ('from_team','to_team'))
    if source==target:
        raise ValueError('Player cannot be traded to the same team')
    requested_name=spec.get('name','').strip()
    if not requested_name:
        raise ValueError('Player name is required')
    found=[]
    for tid in (source,target):
        for pointer in state['rosters'][tid]:
            if not pointer:
                continue
            raw=read_exact(mem,pointer,0x4f0)
            if name(raw).casefold()!=requested_name.casefold():
                continue
            row=player_row(raw,state['team_ids'])
            if spec.get('face_id') is not None and row['face_id']!=spec['face_id']:
                continue
            if spec.get('birth_date') is not None and row['birth_date']!=spec['birth_date']:
                continue
            found.append((pointer,raw,row))
    if len(found)!=1:
        raise ValueError(f'{requested_name}: expected one current roster identity, found {len(found)}; supply face_id / birth_date to disambiguate')
    pointer,raw,row=found[0]
    salaries=[row['contract'][f'contract_year_{i}']['value'] for i in range(1,7)]
    years=row['contract']['years_left_on_contract']['value']
    for key,actual in (('salary_sequence',salaries),('years_left',years)):
        if key in spec and spec[key]!=actual:
            raise ValueError(f'{requested_name}: requested original {key} differs from live source')
    result={'name':row['name'],'face_id':row['face_id'],'birth_date':row['birth_date'],
            'from_team':source,'to_team':target,'salary_sequence':salaries,'years_left':years}
    if spec.get('option') is not None:
        if row['contract']['contract_option'].get('label')!=spec['option']:
            raise ValueError('Requested original contract option differs from live source')
        result['option']=spec['option']
    return result,pointer


def reference_mapping(players,pointers,state):
    """Prioritize references in five-player groups, preserving existing roles.

    Excess outgoing bench/active-list references can be removed. If multiple
    outgoing five-player references cannot map to distinct incoming players, the
    planner rejects the layout rather than selecting unrelated replacement roles.
    """
    mappings={}
    for tid in sorted({p[k] for p in players for k in ('from_team','to_team')}):
        outgoing=[p for p in players if p['from_team']==tid]
        incoming=[p for p in players if p['to_team']==tid]
        refs=struct.unpack_from('<40Q',state['team_raw'][tid],0xd28)
        active=struct.unpack_from('<13Q',state['team_raw'][tid],0xd0)
        outgoing.sort(key=lambda p:(-refs.count(pointers[p['face_id']]),
                                    -(pointers[p['face_id']] in active),
                                    state['rosters'][tid].index(pointers[p['face_id']]) if pointers[p['face_id']] in state['rosters'][tid] else len(state['rosters'][tid])))
        mappings[str(tid)]={str(p['face_id']):incoming[i]['face_id'] if i<len(incoming) else 0
                            for i,p in enumerate(outgoing)}
    return mappings


def normalize(request,state,mem,fallback_id='trade_request'):
    meta=metadata(request,fallback_id)
    actions=[]
    all_players=set()
    all_picks=set()
    used_teams=set()
    for index,raw_action in enumerate(meta.pop('input_actions'),1):
        action_id=raw_action.get('action_id') or f"{meta['request_id']}-A{index:02d}"
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,99}',action_id):
            raise ValueError('Invalid action_id')
        players,pointers=[],{}
        for spec in raw_action.get('players',[]):
            row,pointer=resolve_player(spec,state,mem)
            if pointer in all_players:
                raise ValueError('A player occurs in more than one approved transfer')
            all_players.add(pointer)
            players.append(row)
            pointers[row['face_id']]=pointer
        if len(pointers)!=len(players):
            raise ValueError('Duplicate face IDs require a separately reviewed identity mapping')
        picks=[]
        for spec in raw_action.get('picks',[]):
            row={**spec,'original_team':team_id(spec['original_team'],state),
                 'from_team':team_id(spec['from_team'],state),'to_team':team_id(spec['to_team'],state)}
            if type(row['year']) is not int or type(row['round']) is not int or row['round'] not in (1,2):
                raise ValueError('Pick year and round must be exact integers')
            if row['from_team']==row['to_team']:
                raise ValueError('A pick must change current owner')
            key=(row['year'],row['round'],row['original_team'])
            if key in all_picks:
                raise ValueError('A pick appears in more than one approved transfer')
            all_picks.add(key)
            picks.append(row)
        if not players and not picks:
            raise ValueError('Empty trade')
        tids={p[k] for p in players+picks for k in ('from_team','to_team')}
        if tids & used_teams:
            raise ValueError('Trades sharing a team must be separate requests; dependent multi-trade batches are not supported')
        used_teams.update(tids)
        actions.append({'action_id':action_id,'decision_id':raw_action.get('decision_id',meta['request_id']),
                        'version':raw_action.get('version',1),'players':players,'picks':picks,
                        'reference_replacements':raw_action.get('reference_replacements') or reference_mapping(players,pointers,state)})
    if len({a['action_id'] for a in actions})!=len(actions):
        raise ValueError('Duplicate action_id')
    return {**meta,'actions':actions}
