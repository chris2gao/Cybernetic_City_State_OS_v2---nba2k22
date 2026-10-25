"""Bounded whole-window schedule acquisition; directory count is source evidence.

The 32-byte Slot10 index and 60-byte SEASON pool are retained separately. Their
equality and identity relationship must be checked, not inferred from a count.
"""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,struct
from pathlib import Path
from live_reader import ReadOnlyGameProcess,SEASON_RVA,ROSTER_RVA,GAME_OFFSET,GAME_STRIDE,STATBANK_OFFSET,RESEARCH_GAME_CAPACITY,RESEARCH_STAT_CAPACITY
from readers import _module
from live_world import collect_world,world_payload,read_binding,bound_database,_json,_AcquisitionReceipt
from engine import connect,ingest_capture
from owner_capture import STAT_MAP
from schema_model import DOMAIN


def bounded_block(reader,address,size,label,chunk=1200):
    if type(size) is not int or not 1<=size<=2_000_000:raise ValueError('block outside explicit acquisition envelope')
    return b''.join(reader.read(address+off,min(chunk,size-off),label+':'+str(off)) for off in range(0,size,chunk))


def collect_schedule(reader,*,frozen_cache=None):
    frozen_cache=frozen_cache or {}
    season_pointer=reader.read(reader.module_base+SEASON_RVA,8,'SCHEDULE_SEASON_POINTER')
    roster_pointer=reader.read(reader.module_base+ROSTER_RVA,8,'SCHEDULE_ROSTER_POINTER')
    season=struct.unpack('<Q',season_pointer)[0];root=struct.unpack('<Q',roster_pointer)[0]
    descriptor=reader.read(root+10*16,16,'SCHEDULE_SLOT10_DESCRIPTOR')
    count,index=struct.unpack('<QQ',descriptor)
    if not 1<=count<=RESEARCH_GAME_CAPACITY:raise ValueError('actual Slot10 count outside known SEASON window')
    header=reader.read(season,64,'SCHEDULE_SEASON_HEADER')
    games=bounded_block(reader,season+GAME_OFFSET,count*60,'SCHEDULE_GAMES_60')
    native_index=bounded_block(reader,index,count*32,'SCHEDULE_SLOT10_32')
    decoder=_module('boxscore_decoder').BoxScoreDecoder
    entries=[];boxes={};errors=[];reused={}
    for i in range(count):
        raw=games[i*60:(i+1)*60];g=decoder.decode_game_header(raw);meta=g['boxscore_meta']
        item={'pool_index':i,'native_game_id':g['game_id'],'home_team_id':g['home_team_id'],
              'away_team_id':g['away_team_id'],'status':g['status'],'date_candidate':g['game_date'],
              'stat_lines_index':meta['stat_lines_index'],'home_players':meta['num_home_players'],
              'away_players':meta['num_away_players'],'overtime_count':g['overtime_count']}
        item['record_shape_valid']=bool(g['game_id'] not in (0,0xFFFFFFFF) and g['home_team_id']!=g['away_team_id'] and
                                        g['status'] in (0,1,2))
        if not item['record_shape_valid']:errors.append({'pool_index':i,'reason':'NON_GAME_OR_UNRECOGNIZED_RECORD'})
        if item['record_shape_valid'] and g['status']==2:
            prior=frozen_cache.get(g['game_id'])
            if prior and prior['header_sha256']==hashlib.sha256(raw).hexdigest():
                item['box_status']='REUSED_FROZEN_SOURCE; NATIVE_BOX_NOT_REREAD';item['prior_full_unit_id']=prior['unit_id'];reused[i]=prior;entries.append(item);continue
            n=meta['num_home_players']+meta['num_away_players'];start=meta['stat_lines_index']
            if not 1<=meta['num_home_players']<=26 or not 1<=meta['num_away_players']<=26 or start+n>RESEARCH_STAT_CAPACITY:
                item['box_status']='REJECTED_PARTICIPANT_WINDOW';errors.append({'pool_index':i,'reason':item['box_status']})
            else:
                data=reader.read(season+STATBANK_OFFSET+start*24,n*24,f'SCHEDULE_FINAL_BOX:{i}')
                decoded=decoder.decode_full_boxscore(raw,data);boxes[i]=data
                passed=all(decoded['conservation'][k] for k in ('home_score_exact','away_score_exact'))
                item['box_status']='SCORE_CONSERVATION_PASSED' if passed else 'REJECTED_SCORE_CONSERVATION'
                item['home_score']=decoded['home_score'];item['away_score']=decoded['away_score']
                if not passed:errors.append({'pool_index':i,'reason':item['box_status']})
        entries.append(item)
    ids=Counter(e['native_game_id'] for e in entries if e['record_shape_valid'])
    duplicates={str(k):v for k,v in ids.items() if v>1}
    # Repeat complete schedule/index and each captured Box to reject a mid-read
    # simulation/update; this does not advance or pause the game's state.
    if bounded_block(reader,season+GAME_OFFSET,count*60,'SCHEDULE_GAMES_RECHECK')!=games:raise ValueError('schedule changed during acquisition')
    if bounded_block(reader,index,count*32,'SCHEDULE_INDEX_RECHECK')!=native_index:raise ValueError('Slot10 index changed during acquisition')
    for i,data in boxes.items():
        start=entries[i]['stat_lines_index']
        if reader.read(season+STATBANK_OFFSET+start*24,len(data),f'SCHEDULE_BOX_RECHECK:{i}')!=data:raise ValueError('Box changed during acquisition')
    for address,data,label in ((reader.module_base+SEASON_RVA,season_pointer,'SCHEDULE_SEASON_POINTER_RECHECK'),
        (reader.module_base+ROSTER_RVA,roster_pointer,'SCHEDULE_ROSTER_POINTER_RECHECK'),
        (root+10*16,descriptor,'SCHEDULE_DESCRIPTOR_RECHECK'),(season,header,'SCHEDULE_HEADER_RECHECK')):
        if reader.read(address,len(data),label)!=data:raise ValueError('schedule directory/header changed during acquisition')
    return {'header':header,'games':games,'native_index':native_index,'boxes':boxes,'reused':reused,
            'manifest':{'actual_slot10_count':count,'season_capacity_bound':RESEARCH_GAME_CAPACITY,
                'season_pointer':hex(season),'roster_root':hex(root),'slot10_address':hex(index),
                'record_count':len(entries),'status_counts':dict(Counter(str(e['status']) for e in entries)),
                'duplicate_game_ids':duplicates,'errors':errors,'entries':entries,
                'raw_identity_samples':[{'pool_index':i,'season_words':list(struct.unpack('<15I',games[i*60:(i+1)*60])),
                                        'slot10_words':list(struct.unpack('<8I',native_index[i*32:(i+1)*32]))}
                                       for i in sorted({0,min(1,count-1),min(2,count-1),count-1})],
                'header_words':list(struct.unpack('<16I',header)),
                'scope':'ACTUAL_DESCRIPTOR_BOUNDED_WINDOW; INDEX_RELATION_NOT_YET_CERTIFIED',
                'game_writes':False,'native_boxes_read':len(boxes),'frozen_boxes_reused':len(reused),
                'reuse_semantics':'Current header/directory read; prior immutable full Box retained at its original source time. Unread Native Box equality is not asserted.'}}


def probe_schedule(pid,new_output_directory):
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    report={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_writes':False}
    try:
        reader=ReadOnlyGameProcess(pid);found=collect_schedule(reader)
        reader.close()
        for name in ('header','games','native_index'):(out/(name+'.bin')).write_bytes(found[name])
        for i,data in found['boxes'].items():(out/f'box-{i}.bin').write_bytes(data)
        (out/'schedule-manifest.json').write_text(json.dumps(found['manifest'],indent=2)+'\n',encoding='utf-8',newline='\n')
        report.update({'status':'WINDOW_CAPTURED_PENDING_INDEX_SEMANTICS','module_base':hex(reader.module_base),
            'module_size':reader.module_size,'read_trace':reader.trace,
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}})
    except (OSError,ValueError,RuntimeError) as error:
        report.update({'status':'SOURCE_UNAVAILABLE_OR_CHANGED','reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[])})
    finally:
        if reader:reader.close()
    (out/'schedule-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    return report


def index_relationship(found,context):
    """Verify every Slot10 date and TEAM pointer against every SEASON row."""
    teams={t['address']:t['native_team_id'] for t in context['teams']}
    matches={'date_except_low5':0,'home_team_pointer':0,'away_team_pointer':0}
    for i in range(found['manifest']['record_count']):
        game=found['games'][i*60:(i+1)*60];idx=found['native_index'][i*32:(i+1)*32]
        date=struct.unpack_from('<I',game)[0];date2=struct.unpack_from('<I',idx)[0]
        h,a=struct.unpack_from('<HH',game,12);hp,ap=struct.unpack_from('<QQ',idx,8)
        tests=((date&~31)==(date2&~31),teams.get(hp)==h,teams.get(ap)==a)
        if not all(tests):raise ValueError('Slot10/SEASON identity mismatch at '+str(i))
        for key,passed in zip(matches,tests):matches[key]+=int(passed)
    return {'record_count':found['manifest']['record_count'],'all_record_matches':matches,
            'scope':'ACTUAL_PAIRED_WINDOW_CURRENT_TEAM_POINTERS','date_ui_calendar_validation':'NOT_OBSERVED'}


def schedule_facts(found,season,selected_native_ids):
    decoder=_module('boxscore_decoder').BoxScoreDecoder
    facts={name:[] for name in ('games','game_state_observations','game_period_scores','team_game_boxes','player_game_boxes','native_box_observations','game_source_checks')}
    tid=lambda n:'team:native:'+str(n)
    for i,entry in enumerate(found['manifest']['entries']):
        g=decoder.decode_game_header(found['games'][i*60:(i+1)*60]);gid=season['season_id']+':game:'+str(g['game_id'])
        facts['games'].append({'game_id':gid,'season_id':season['season_id'],'native_game_id':str(g['game_id']),
            'home_team_id':tid(g['home_team_id']),'away_team_id':tid(g['away_team_id']),'game_date':None})
        check={'game_id':gid,'header_sha256':hashlib.sha256(found['games'][i*60:(i+1)*60]).hexdigest(),'game_status_raw':g['status']}
        if g['status']!=2:
            facts['game_source_checks'].append({**check,'box_mode':'HEADER_ONLY_NOT_FINAL','reuse_basis':'CURRENT_HEADER_ONLY; NO_FINAL_BOX_EXPECTED'})
            facts['game_state_observations'].append({'game_id':gid,'status_code':str(g['status']),'is_final':0,
                'score_provenance':'NOT_FINAL_NO_ACCEPTED_SCORE'})
            continue
        if i in found.get('reused',{}):
            facts['game_source_checks'].append({**check,'box_mode':'REUSED_FROZEN_BOX','prior_full_unit_id':found['reused'][i]['unit_id'],'reuse_basis':'MATCHING_CURRENT_HEADER_AND_PRIOR_QUALIFIED_FROZEN_SOURCE; UNREAD_BOX_EQUALITY_NOT_ASSERTED'})
            continue
        facts['game_source_checks'].append({**check,'box_mode':'FULL_NATIVE_BOX','box_sha256':hashlib.sha256(found['boxes'][i]).hexdigest(),'reuse_basis':'ACTUAL_NATIVE_BOX_READ_AND_RECHECK'})
        g=decoder.decode_full_boxscore(found['games'][i*60:(i+1)*60],found['boxes'][i])
        facts['game_state_observations'].append({'game_id':gid,'status_code':str(g['status']),'is_final':1,
            'overtime_count':g['overtime_count'],'attendance':g['attendance'],'was_simulated':int(g['was_simulated']),
            'score_provenance':'NATIVE_PERIOD_AND_DERIVED_BOX_CONSERVATION; TOTAL_FIELD_NOT_OBSERVED'})
        for side in ('home','away'):
            native_team=g[side+'_team_id'];team=tid(native_team)
            facts['game_period_scores'].extend({'game_id':gid,'team_id':team,'period_index':q,'period_points':g['linescore'][side]['q'+str(q)]} for q in range(1,5))
            facts['team_game_boxes'].append({'game_id':gid,'team_id':team,**{new:int(g['boxscore_meta'][side+'_'+old]) for old,new in
                (('fastbreak','fastbreak_points'),('paint','paint_points'),('2nd_chance','second_chance_points'),('pts_off_to','points_off_turnovers'),('lead','largest_lead'),('possessions','possessions_raw'))}})
            for row,p in enumerate(g[side+'_players']):
                stats={new:p[old] for old,new in STAT_MAP.items()};resolved=p['in_use'] and p['player_id'] in selected_native_ids
                facts['native_box_observations'].append({'game_id':gid,'side':side.upper(),'row_index':row,
                    'native_player_id':p['player_id'],'native_team_id':native_team,'in_use':int(p['in_use']),**stats,
                    'points_provenance':'DERIVED_2FGM_PLUS_3PM_PLUS_FTM',
                    'identity_status':'CURRENT_CONTEXT_RESOLVED' if resolved else 'UNRESOLVED_CANONICAL_PLAYER'})
                if resolved:
                    facts['player_game_boxes'].append({'game_id':gid,'player_id':'player:native:'+str(p['player_id']),'team_id':team,**stats,
                        'defensive_fg_made':p['def_fgm'],'defensive_fg_attempted':p['def_fga'],'defensive_points':p['def_pts'],
                        'is_starter':int(p['is_starter']),'in_use':1,'points_provenance':'DERIVED_2FGM_PLUS_3PM_PLUS_FTM'})
    return facts


def frozen_game_sources(database,season_id):
    from competition_views import game_box_snapshot
    from schema_model import VERSION
    from observation_scope import utc_stamp
    with connect(database,True) as conn:
        if conn.execute('PRAGMA user_version').fetchone()[0]!=VERSION:raise ValueError('copy-upgrade facts before incremental schedule capture')
        rows=[dict(r) for r in conn.execute('''SELECT c.game_id,c.unit_id,c.header_sha256,u.observed_at,g.native_game_id FROM game_source_checks c
            JOIN capture_units u USING(unit_id) JOIN capture_runs r USING(run_id) JOIN games g USING(game_id)
            WHERE c.box_mode='FULL_NATIVE_BOX' AND g.season_id=? AND u.unit_status='success' AND r.source_grade='LIVE_READ' ''',(season_id,))]
    result={};seen=set()
    for row in sorted(rows,key=lambda r:(utc_stamp(r['observed_at']),r['unit_id']),reverse=True):
        if row['game_id'] in seen:continue
        seen.add(row['game_id']);box=game_box_snapshot(database,row['game_id'],unit_id=row['unit_id'])
        if len(box['states'])!=1 or box['states'][0]['is_final']!=1 or len(box['period_scores'])!=8 or len(box['team_boxes'])!=2:continue
        if any(side['status']!='ALL_CAPTURED_NATIVE_PARTICIPANTS_RESOLVED' for side in box['coverage'].values()):continue
        result[int(row['native_game_id'])]=row
    return result


def capture_season(pid,save_directory,loaded_filename,new_output_directory,*,recheck_frozen=False):
    binding,binding_hash=read_binding(save_directory,loaded_filename)
    from schema_model import VERSION
    with connect(bound_database(save_directory,binding),True) as conn:
        if conn.execute('PRAGMA user_version').fetchone()[0]!=VERSION:raise ValueError('copy-upgrade facts before incremental schedule capture')
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None
    stamp=datetime.now(timezone.utc).isoformat()
    try:
        from cadence import observed_game_season_year
        reader=ReadOnlyGameProcess(pid);year=observed_game_season_year(reader)
        cache={} if recheck_frozen else frozen_game_sources(bound_database(save_directory,binding),'season:native-year:'+str(year))
        found=collect_schedule(reader,frozen_cache=cache)
        if found['manifest']['errors'] or found['manifest']['duplicate_game_ids']:raise ValueError('schedule source contains invalid, duplicate or nonconserving games')
        decoder=_module('boxscore_decoder').BoxScoreDecoder;targets=set()
        for i,data in found['boxes'].items():
            full=decoder.decode_full_boxscore(found['games'][i*60:(i+1)*60],data)
            targets.update(p['player_id'] for side in ('home_players','away_players') for p in full[side] if p['in_use'])
        one,context,blobs=collect_world(reader,None,target_native_ids=targets,current_context_only=True)
        if context['game_season_year']!=year:raise ValueError('native season changed during incremental schedule capture')
        relation=index_relationship(found,context)
        after=collect_schedule(reader,frozen_cache=cache)
        if any(found[k]!=after[k] for k in ('header','games','native_index','boxes')):raise ValueError('schedule changed while collecting player context')
        reader.close()
        for name in ('header','games','native_index'):blobs['schedule-'+name+'.bin']=found[name]
        for i,data in found['boxes'].items():blobs[f'schedule-box-{i}.bin']=data
        for name,data in blobs.items():(out/name).write_bytes(data)
        _json(out/'player-context.json',context);_json(out/'schedule-manifest.json',found['manifest']);_json(out/'index-relationship.json',relation)
        report={'observed_at':stamp,'pid':pid,'save_id':binding['save_id'],'native_save_filename':loaded_filename,
            'binding_sha256':binding_hash,'status':'COMPLETE_DESCRIPTOR_WINDOW_AND_PLAYER_CONTROLS_PASSED',
            'read_trace':reader.trace,'game_writes':False,'potential_bytes_read':0,
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        _json(out/'acquisition-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,
            'payload_kind':'BOUND_SEASON_WINDOWS_SOURCE','source_version':'BOUND_SCHEDULE_V1','payload_ref':out.name+'/'+p.name}
            for p in sorted(out.iterdir()) if p.is_file()]
        for path in (DOMAIN/'config/memory_field_profile.json',DOMAIN/'config/state_io_native/player.json'):
            artifacts.append({'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'byte_count':path.stat().st_size,'restricted':1,
                'payload_kind':'REGISTERED_DECODER_LAYOUT','source_version':'BOUND_SCHEDULE_V1','payload_ref':str(path.relative_to(DOMAIN))})
        token=hashlib.sha256((out/'acquisition-report.json').read_bytes()).hexdigest()[:24]
        payload=world_payload(binding,one,context,blobs,artifacts,stamp,token)
        selected={int(p['native_player_id']) for p in payload['facts']['players']}
        payload['facts'].update(schedule_facts(found,payload['season'],selected))
        team_ids={g[k] for g in payload['facts']['games'] for k in ('home_team_id','away_team_id')}
        for key in sorted(team_ids-{t['team_id'] for t in payload['facts']['teams']}):
            native=int(key.rsplit(':',1)[1]);teams=[t for t in context['teams'] if t['native_team_id']==native]
            if len(teams)!=1:raise ValueError('nonunique schedule TEAM native identity')
            t=teams[0];payload['facts']['teams'].append({'team_id':key,'native_team_id':str(native),
                'display_name':(t['city']+' '+t['name']).strip(),'native_identity_status':'CURRENT_POINTER_AND_UNIQUE_POOL_ID'})
            payload['facts']['team_seasons'].append({'team_id':key,'season_id':payload['season']['season_id'],'team_name':t['name']})
        payload.update({'evidence_grade':'LIVE_READ','source_key':'BOUND_COMPLETE_DESCRIPTOR_SCHEDULE_AND_PLAYERS',
                        'decoder_version':'BOUND_SCHEDULE_AND_PUBLIC_PLAYER_V1'})
        receipt=_AcquisitionReceipt(payload,reader)
        with connect(bound_database(save_directory,binding)) as conn:status=ingest_capture(conn,payload,_live_receipt=receipt)
        result={'status':status,'unit_id':payload['unit_id'],'save_id':binding['save_id'],'source_grade':'LIVE_READ',
            'native_save_filename':loaded_filename,'season':payload['season'],'schedule_status_counts':found['manifest']['status_counts'],
            'counts':{name:len(rows) for name,rows in payload['facts'].items()},'targeted_native_player_ids':len(targets),
            'unresolved_native_player_ids':sorted(targets-selected),'index_relationship':relation,
                'native_boxes_read':len(found['boxes']),'frozen_boxes_reused':len(found['reused']),'recheck_frozen':recheck_frozen,
            'game_writes':False,'potential_bytes_read':0,'full_goal_complete':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'SEASON_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,
            'reason':str(error),'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False})
        raise
    finally:
        if reader:reader.close()


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('pid',type=int);p.add_argument('new_output_directory');a=p.parse_args()
    r=probe_schedule(a.pid,a.new_output_directory);print(json.dumps({'status':r['status']}))
    raise SystemExit(0 if r['status']=='WINDOW_CAPTURED_PENDING_INDEX_SEMANTICS' else 2)
