"""Bounded research-file acquisition -> versioned decode -> typed unit bundles.

No process handle, process injection, game-state write, or save-file overwrite.
This adapter replays historical captured bytes, never certifies a current save.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
from schema_model import DOMAIN, PROFILE, TENDENCY_FIELDS

NATIVE=DOMAIN/'research/native_access/AG_NATIVE_01D'
SOURCE_REF='21d62ec9e04b86a1f737c1500ea2f41c34583215:research/native_access/AG_NATIVE_01D'


def _module(name):
    path=NATIVE/'decoders'/f'{name}.py'
    spec=importlib.util.spec_from_file_location('world_data_'+name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def artifact(path,kind):
    path=Path(path).resolve()
    data=path.read_bytes()
    return {'sha256':hashlib.sha256(data).hexdigest(),'payload_kind':kind,
            'payload_ref':str(path.relative_to(DOMAIN)),'byte_count':len(data),'source_version':SOURCE_REF,'restricted':1}


def decode_player_public(raw):
    """Decode only registered public unsigned scalars; never return raw PLAYER bytes.

    Contract offset 833 and packed STAFF fields are intentionally not decoded by
    this scalar adapter. Native byte ranges are storage bounds, not UI legality.
    """
    if len(raw)!=1264:raise ValueError('PLAYER record must be exactly 1264 bytes')
    return {('three_point_shot' if r['name']=='3pt_shot' else r['name'])+'_raw':
            int.from_bytes(raw[r['offset']:r['offset']+r['bytes']],'little')
            for r in PROFILE['fields']['PLAYER'] if r['group']=='attributes' and r['name']!='potential'}


def replay_ag01d(save_id,*,observed_at=None):
    """Produce independent source units from immutable AG01D research samples.

    Native IDs are scoped to this sample/save and its evidenced season. An
    identity mapping into a different live save is NEVER inferred from a name.
    Each artifact checksum describes the actual file consumed in this replay.
    """
    observed_at=observed_at or datetime.now(timezone.utc).isoformat()
    box=_module('boxscore_decoder').BoxScoreDecoder
    season_decoder=_module('season_stats_decoder').SeasonStatsDecoder
    games_path=NATIVE/'fixtures/sample_curry_season_games.json'
    career_path=NATIVE/'fixtures/sample_player_career_slice.json'
    games=json.loads(games_path.read_text(encoding='utf-8'))
    career=json.loads(career_path.read_text(encoding='utf-8'))['Curry']
    player_raw=bytes.fromhex(career['raw_player_hex'])
    identity=season_decoder.extract_player_career_indices(player_raw)
    native_player=identity['player_id']
    stats_map=career['stats_records_hex']
    current=identity['current_season_stats_index']
    if str(current) not in stats_map:raise ValueError('current career stats index missing from source')
    totals=season_decoder.decode_player_stats_record(bytes.fromhex(stats_map[str(current)]))
    year=totals['season_year']
    season={'season_id':f'season:{year}','season_code':f'{year-1}-{str(year)[2:]}'}
    pid=f'player:AG01D:{native_player}'
    version='AG01D_RESEARCH_LAYOUT_REPLAY_V1'
    def envelope(key,facts,artifacts):
        return {'save_id':save_id,'run_id':'ag01d-replay:'+observed_at,'unit_id':'ag01d:'+key+':'+observed_at,
            'source_key':key,'observed_at':observed_at,'evidence_grade':'RESEARCH_FIXTURE',
            'decoder_version':version,'save_binding_ref':'UNVERIFIED_ORIGINAL_SAVE: '+SOURCE_REF,
            'season':season,'completeness':'PARTIAL','facts':facts,'artifacts':artifacts}
    yield envelope('player',{'players':[{'player_id':pid,'display_name':identity['name'],
            'native_player_id':str(native_player),'native_identity_status':'UNVERIFIED'}],
        'player_attribute_snapshots':[{'player_id':pid,**decode_player_public(player_raw)}]},
        [artifact(career_path,'RESTRICTED_RESEARCH_PLAYER_AND_CAREER')])
    mapping={'fgm':'fg_made','fga':'fg_attempted','tpm':'three_made','tpa':'three_attempted','ftm':'ft_made',
             'fta':'ft_attempted','oreb':'offensive_rebounds','dreb':'defensive_rebounds','ast':'assists',
             'stl':'steals','blk':'blocks','tov':'turnovers','fouls':'fouls','minutes':'minutes_raw',
             'plus_minus':'plus_minus','possessions':'possessions_raw','def_fgm':'defensive_fg_made',
             'def_fga':'defensive_fg_attempted','def_pts':'defensive_points'}
    for sample in games:
        header=box.decode_game_header(bytes.fromhex(sample['game_raw_hex']))
        stat=box.decode_player_statline(bytes.fromhex(sample['curry_statline_hex']))
        if stat['player_id']!=native_player or not stat['in_use']:raise ValueError('sample player identity/in-use mismatch')
        home='team:'+str(header['home_team_id']);away='team:'+str(header['away_team_id'])
        gid=f'{season["season_id"]}:game:{header["game_id"]}'
        # The source explicitly identifies GSW's native team in this fixture;
        # verify the participant using the season record rather than guessing by name.
        team='team:'+str(totals['last_team'])
        if team not in (home,away):raise ValueError('season team not a sample game participant')
        facts={'teams':[{'team_id':t,'display_name':None,
                        'native_team_id':t.split(':')[1],'native_identity_status':'UNVERIFIED'} for t in (home,away)],
            'games':[{'game_id':gid,'season_id':season['season_id'],'home_team_id':home,
                      'away_team_id':away,'native_game_id':str(header['game_id']),'game_date':header['game_date']}],
            'game_state_observations':[{'game_id':gid,'status_code':str(header['status']),
                'overtime_count':header['overtime_count'],'attendance':header['attendance'],
                'was_simulated':int(header['was_simulated']),'score_provenance':'NOT_OBSERVED_NATIVE_TOTAL'}],
            'game_period_scores':[],
            'player_game_boxes':[{'game_id':gid,'player_id':pid,'team_id':team,
                **{new:stat[old] for old,new in mapping.items()},'points':stat['points'],
                'points_provenance':'DERIVED_2FGM_PLUS_3PM_PLUS_FTM',
                'is_starter':int(stat['is_starter']),'in_use':int(stat['in_use'])}]}
        for side,t in [('home',home),('away',away)]:
            for q in range(1,5):facts['game_period_scores'].append({'game_id':gid,'team_id':t,'period_index':q,
                'period_points':header['linescore'][side]['q'+str(q)]})
        yield envelope('game:'+str(header['game_id']),facts,[artifact(games_path,'RESEARCH_GAME_AND_SINGLE_PLAYER_BOX')])
    stats_mapping={**mapping,'games_played':'games_played','games_started':'games_started','points':'points',
                   'double_doubles':'double_doubles','triple_doubles':'triple_doubles','foul':'fouls'}
    # One row per actual native career record; no invented team-specific split.
    for idx in [current]+identity['career_history_stats_indices']:
        if str(idx) not in stats_map:continue
        s=season_decoder.decode_player_stats_record(bytes.fromhex(stats_map[str(idx)]))
        sy=s['season_year'];ss={'season_id':f'season:{sy}','season_code':f'{sy-1}-{str(sy)[2:]}'}
        facts={'player_season_totals':[{'player_id':pid,'season_id':ss['season_id'],
            **{new:s[old] for old,new in stats_mapping.items() if old in s and new not in ('defensive_fg_made','defensive_fg_attempted','defensive_points')},
            'team_scope':'UNKNOWN_NATIVE_SCOPE'}]}
        payload=envelope('season-total:'+str(idx),facts,[artifact(career_path,'RESTRICTED_RESEARCH_PLAYER_AND_CAREER')])
        payload['run_id']=payload['run_id']+':'+str(sy);payload['season']=ss
        yield payload
