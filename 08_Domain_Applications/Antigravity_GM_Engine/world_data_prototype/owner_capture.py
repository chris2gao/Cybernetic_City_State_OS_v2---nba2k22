"""Instrumented owner capture -> typed research staging, without false identity.

This imports recorded live-source bytes as a RESEARCH_FIXTURE replay. It does
not promote an unbound capture session to a persistent save or canonical player.
"""
import hashlib
import json
from pathlib import Path
from readers import _module

STAT_MAP={'fgm':'fg_made','fga':'fg_attempted','tpm':'three_made','tpa':'three_attempted',
          'ftm':'ft_made','fta':'ft_attempted','oreb':'offensive_rebounds','dreb':'defensive_rebounds',
          'ast':'assists','stl':'steals','blk':'blocks','tov':'turnovers','fouls':'fouls',
          'minutes':'minutes_raw','plus_minus':'plus_minus','possessions':'possessions_raw','points':'points'}


def recorded_game_capture(capture_directory,save_id):
    directory=Path(capture_directory).resolve()
    report_path=directory/'live-probe-report.json'
    report_raw=report_path.read_bytes();report=json.loads(report_raw)
    if report.get('status')!='BOUNDED_LIVE_BYTES_CAPTURED_NOT_FULL_ACCEPTANCE' or report.get('score_conservation_passed') is not True:
        raise ValueError('capture did not pass bounded layout checks')
    blobs={}
    for name,size in (('header.bin',64),('game.bin',60),('box.bin',None)):
        path=(directory/name).resolve()
        if not path.is_relative_to(directory):raise ValueError('source artifact escaped capture directory')
        data=path.read_bytes()
        if size is not None and len(data)!=size:raise ValueError('incomplete capture artifact '+name)
        if hashlib.sha256(data).hexdigest()!=report.get('artifact_sha256',{}).get(name):raise ValueError('capture artifact hash mismatch '+name)
        blobs[name]=data
    trace=report.get('read_trace',[])
    expected={'SEASON_HEADER':blobs['header.bin'],'ONE_SEASON_GAME':blobs['game.bin'],
              'ONE_GAME_PARTICIPANT_STATBANK':blobs['box.bin']}
    for label,data in expected.items():
        calls=[x for x in trace if x.get('operation')=='ReadProcessMemory' and x.get('label')==label]
        if len(calls)!=1 or not calls[0].get('success') or calls[0].get('returned_bytes')!=len(data) or calls[0].get('sha256')!=hashlib.sha256(data).hexdigest():
            raise ValueError('actual read trace does not match recorded bytes '+label)
    decoder=_module('boxscore_decoder').BoxScoreDecoder
    header=decoder.decode_game_header(blobs['game.bin']);meta=header['boxscore_meta']
    if len(blobs['box.bin'])!=(meta['num_home_players']+meta['num_away_players'])*24:raise ValueError('Box participant window length mismatch')
    full=decoder.decode_full_boxscore(blobs['game.bin'],blobs['box.bin'])
    if not all(full['conservation'][k] for k in ('home_score_exact','away_score_exact')):raise ValueError('raw replay failed score conservation')
    identity=hashlib.sha256(report_raw).hexdigest()
    unit='owner-capture-replay:'+identity[:24]
    season={'season_id':'capture-session:'+identity[:16],'season_code':'UNBOUND_CAPTURE_SESSION:'+identity[:16]}
    gid='source-game:'+identity[:16]+':'+str(full['game_id']);home='source-team:'+str(full['home_team_id']);away='source-team:'+str(full['away_team_id'])
    facts={'teams':[{'team_id':t,'native_team_id':str(n),'display_name':None,'native_identity_status':'UNVERIFIED'}
                    for t,n in ((home,full['home_team_id']),(away,full['away_team_id']))],
        'games':[{'game_id':gid,'season_id':season['season_id'],'home_team_id':home,'away_team_id':away,
                  'native_game_id':str(full['game_id']),'game_date':None}],
        'game_state_observations':[{'game_id':gid,'status_code':str(full['status']),
            'overtime_count':full['overtime_count'],'attendance':full['attendance'],'was_simulated':int(full['was_simulated']),
            'is_final':1,'score_provenance':'NATIVE_TOTAL_NOT_OBSERVED; PERIOD_AND_BOX_SUMS_RECONCILED'}],
        'game_period_scores':[], 'team_game_boxes':[], 'native_box_observations':[],
        'field_gaps':[{'affected_domain':'RES-D','target_field':'PERSISTENT_SAVE_BINDING',
                      'reason':'Current process/capture session does not establish persistent save identity',
                      'impact':'Research staging only; no accepted cross-capture world identity or Q10 exception'},
                     {'affected_domain':'RES-P','target_field':'BOX_CANONICAL_PLAYER_IDENTITIES',
                      'reason':'This replay has no accepted active-player mapping; actual pool controls found duplicate Native IDs',
                      'impact':'Box values remain typed source observations; no invented canonical PLAYER or Q10 exception'},
                     {'affected_domain':'RES-G','target_field':'SCHEDULE_DATE_UI_ENCODING',
                      'reason':'Raw date decoded by historical candidate codec; target calendar/UI month semantics unverified',
                      'impact':'Canonical game_date remains NULL, raw date retained in hashed source'}]}
    for side,team,native_team in (('home',home,full['home_team_id']),('away',away,full['away_team_id'])):
        for q in range(1,5):facts['game_period_scores'].append({'game_id':gid,'team_id':team,'period_index':q,'period_points':full['linescore'][side]['q'+str(q)]})
        raw_box={'game_id':gid,'team_id':team}
        for old,new in (('fastbreak','fastbreak_points'),('paint','paint_points'),('2nd_chance','second_chance_points'),('pts_off_to','points_off_turnovers'),('lead','largest_lead'),('possessions','possessions_raw')):
            raw_box[new]=int(full['boxscore_meta'][side+'_'+old])
        facts['team_game_boxes'].append(raw_box)
        for row,p in enumerate(full[side+'_players']):
            facts['native_box_observations'].append({'game_id':gid,'side':side.upper(),'row_index':row,
                'native_player_id':p['player_id'],'native_team_id':native_team,'in_use':int(p['in_use']),
                **{new:p[old] for old,new in STAT_MAP.items()},
                'points_provenance':'DERIVED_2FGM_PLUS_3PM_PLUS_FTM','identity_status':'UNRESOLVED_CANONICAL_PLAYER'})
    artifacts=[]
    for name,data in {**blobs,'live-probe-report.json':report_raw}.items():
        artifacts.append({'sha256':hashlib.sha256(data).hexdigest(),'payload_kind':'OWNER_CAPTURED_RESEARCH_SOURCE',
                          'payload_ref':'owner-capture:'+name,'byte_count':len(data),'source_version':'OWNER_CAPTURE_REPORT_SHA256:'+identity,'restricted':1})
    return {'save_id':save_id,'run_id':unit,'unit_id':unit,'source_key':'OWNER_RECORDED_GAME_'+str(full['game_id']),
            'observed_at':report['observed_at'],'evidence_grade':'RESEARCH_FIXTURE','decoder_version':'OWNER_LIVE_CAPTURE_REPLAY_V1',
            'save_binding_ref':'UNKNOWN_PERSISTENT_SAVE; CAPTURE_SESSION_REPORT_SHA256:'+identity,
            'season':season,'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}
