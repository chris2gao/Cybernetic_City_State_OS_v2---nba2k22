"""Typed historical awards and ordinary native message/transaction acquisition."""
from collections import defaultdict
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
from cadence import attach_annual_period,prepare_annual_capture
from engine import connect,ingest_acquired_capture as ingest_capture
from league_reader import PROFILE_PATH,collect_league_source
from live_reader import ReadOnlyGameProcess
from live_world import _AcquisitionReceipt,_json,bound_database,read_binding
from schema_model import HISTORY_NATIVE_MAP,MESSAGE_NATIVE_MAP

AWARD_SUBJECTS={label:'PLAYER' for label in ('MVP','ROY','SIXTHMAN','DEFENSIVEPOY','MOSTIMPROVEDPLAYER',
    'ALLNBATEAM1','ALLNBATEAM2','ALLNBATEAM3','ALLDEFENSIVETEAM1','ALLDEFENSIVETEAM2','ALLROOKIETEAM1','ALLROOKIETEAM2')}
AWARD_SUBJECTS.update({'CHAMPION':'TEAM','COACH':'STAFF','GM':'STAFF'})
DATE_MAP={'raw_word_u32':'date_word_raw','id_raw':'date_id_raw','minutes_since_midnight_raw':'date_minutes_raw',
    'day_raw':'date_day_raw','month_raw':'date_month_raw','base_year_offset_raw':'date_year_offset_raw'}
NAME_MAP={'PrimaryTeamName':'primary_team_name','PrimaryTeamCity':'primary_team_city','SecondaryTeamName':'secondary_team_name',
    'SecondaryTeamCity':'secondary_team_city','PlayerFirstName':'player_first_name','PlayerLastName':'player_last_name'}


def existing_history_awards(conn):
    return {(r['source_year_raw'],r['award_code']):dict(r) for r in conn.execute('''SELECT award_id,source_year_raw,award_code,source_fingerprint
        FROM season_award_instances WHERE award_type='NATIVE_ROSTER_HISTORY' ''')}


def semantic_history(row):
    return {'names':row['names'],'values':{k:v for k,v in row['values'].items() if k not in ('NextFree','PrimaryStat','SecondaryStat')},
        'primary_word':row['stat_values']['PrimaryStat']['word_u32'],'secondary_word':row['stat_values']['SecondaryStat']['word_u32']}


def _serialized(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'))
def _sha(value):return hashlib.sha256(_serialized(value).encode('utf-8')).hexdigest()


def league_payload(binding,manifest,artifacts,observed_at,token,existing=None):
    mode=manifest['capture_mode'];year=manifest['season_year'];unit='native-league:'+token;existing=existing or {}
    if mode not in ('HISTORY_AWARDS','NEWS_TRANSACTIONS') or manifest.get('game_writes') is not False or manifest.get('player_struct_reads')!=0:raise ValueError('typed league capture requires explicit read-only source mode')
    facts={};periods={};control={'source_mode':mode,'observation_year':year}
    def period(y):
        value={'season_id':f'season:native-year:{y}','season_code':f'NATIVE_YEAR:{y}'};periods[y]=value;return value['season_id']
    if mode=='HISTORY_AWARDS':
        rows=manifest['history'];count=manifest['history_descriptor']['count']
        if len(rows)!=count or {r['source_row_index'] for r in rows}!=set(range(count)):raise ValueError('incomplete/duplicate native history slots')
        facts.update({'native_league_history_observations':[],'season_award_instances':[],'award_recipients':[],'fact_conflicts':[]})
        groups=defaultdict(list);links={}
        for r in rows:
            label=r['type_label'];y=r['values']['Year'];i=r['source_row_index']
            if label not in AWARD_SUBJECTS:links[i]=(None,'NOT_AWARD_CATEGORY');continue
            if not 1<=y<year:links[i]=(None,'SOURCE_YEAR_NOT_CLOSED');continue
            groups[y,label].append(r)
        for (y,label),members in sorted(groups.items()):
            subject=AWARD_SUBJECTS[label]
            has_subject=lambda r:bool(r['names']['PrimaryTeamName']) if subject=='TEAM' else bool(r['names']['PlayerFirstName'] or r['names']['PlayerLastName'])
            if any(not has_subject(r) or r['text_status']!='ASCII_OR_LATIN1_PREFIXES_OBSERVED' for r in members):
                for r in members:links[r['source_row_index']]=(None,'HISTORICAL_SUBJECT_NOT_READABLE')
                continue
            # Duplicate storage copies do not create duplicate recipients. Ties
            # with different inline identities remain separate, without a rank inference.
            unique={}
            for r in sorted(members,key=lambda r:r['source_row_index']):unique.setdefault(_serialized(semantic_history(r)),r)
            fingerprint=_sha(sorted(unique));previous=existing.get((y,label));award=f'native-history-award:{y}:{label}'
            if previous:
                if previous['source_fingerprint']!=fingerprint:
                    facts['fact_conflicts'].append({'object_ref':previous['award_id'],'evidence_a':previous['source_fingerprint'] or 'SOURCE_FINGERPRINT_MISSING',
                        'evidence_b':fingerprint,'review_status':'PENDING_HUMAN'})
                    for r in members:links[r['source_row_index']]=(None,'IMMUTABLE_AWARD_CONFLICT_RECORDED')
                    continue
                award=previous['award_id'];state='SAME_ARCHIVED_AWARD_REOBSERVED'
            else:
                facts['season_award_instances'].append({'award_id':award,'season_id':period(y),'award_code':label,'award_type':'NATIVE_ROSTER_HISTORY','is_final':1,
                    'source_year_raw':y,'source_fingerprint':fingerprint,'finality_basis':'NATIVE_ROSTER_HISTORY_ENTRY_FOR_CLOSED_SOURCE_YEAR; NOT_CURRENT_WORLD_FINALIZATION'})
                for semantic,r in sorted(unique.items()):
                    facts['award_recipients'].append({'recipient_id':award+':recipient:'+hashlib.sha256(semantic.encode('utf-8')).hexdigest()[:24],
                        'award_id':award,'player_id':None,'team_id':None,'staff_id':None,'rank_index':None,
                        'source_history_id':f'{unit}:history:{r["source_row_index"]}','source_subject_type':subject})
                state='NATIVE_ARCHIVED_AWARD_RECORDED'
            for r in members:links[r['source_row_index']]=(award,state)
        for r in rows:
            i=r['source_row_index'];item={'history_observation_id':f'{unit}:history:{i}','source_row_index':i,
                **{column:r['values'][native] for native,column in HISTORY_NATIVE_MAP.items()},
                **{column:r['names'][native] for native,column in NAME_MAP.items()},'native_type_label':r['type_label'],
                'source_state':r['source_state'],'text_status':r['text_status'],'award_id':links[i][0],'award_link_status':links[i][1]}
            for native,prefix in (('PrimaryStat','primary'),('SecondaryStat','secondary')):
                v=r['stat_values'][native];item.update({prefix+'_stat_word_raw':v['word_u32'],prefix+'_stat_real':v['value_real'],prefix+'_stat_text':v['value_text']})
            facts['native_league_history_observations'].append(item)
        matrix=manifest['award_winner_matrix']
        if len(matrix)!=75 or {(r['award_slot_index'],r['recipient_slot_index']) for r in matrix}!={(a,b) for a in range(15) for b in range(5)}:raise ValueError('incomplete award matrix')
        facts['native_award_matrix_observations']=matrix
        manager=manifest['manager_slot40_candidate'];chain=manager.get('free_chain') or {}
        control.update({'history_slot_count':count,'manager_first_free_candidate':manager['first_word'],
            'free_chain_status':chain.get('status'),'free_chain_count':len(chain['indices']) if 'indices' in chain else None,'matrix_cell_count':75})
        gaps=[('HISTORICAL_SUBJECT_LIFECYCLE','Inline historical identities are retained without binding current PLAYER/TEAM/STAFF','No name/ID-only canonical subject transition'),
            ('HISTORY_WORLD_SCOPE','Native roster history is source-recorded archival history, not a claim of this save simulating old events','Award type/finality basis is explicit; current-year matrix is not final'),
            ('LEAGUE_MANAGER_SLOT40_IDENTITY','Free-chain candidate is corroborative; exact manager slot identity is not yet independently proven','No allocator validity inferred solely from manager candidate')]
    else:
        messages=manifest['messages'];transactions=manifest['transactions']
        if len(messages)!=4000 or {(r['bank_index'],r['source_slot_index']) for r in messages}!={(b,i) for b in range(2) for i in range(2000)}:raise ValueError('incomplete native message storage')
        if len(transactions)!=250 or {r['source_slot_index'] for r in transactions}!=set(range(250)):raise ValueError('incomplete transaction storage')
        active=manifest['social_active_counts'];tc=manifest['transaction_count']
        if len(active)!=2 or any(type(n) is not int or not 0<=n<=2000 for n in active) or not 0<=tc<=250:raise ValueError('invalid native event counts')
        facts.update({'native_social_message_observations':[],'game_news_entries':[],'native_transaction_observations':[],'native_transaction_item_observations':[]})
        for r in messages:
            message=f'{unit}:message:{r["bank_index"]}:{r["source_slot_index"]}'
            expected='WITHIN_DECLARED_COUNT_PREFIX_CANDIDATE' if r['source_slot_index']<active[r['bank_index']] else 'OUTSIDE_DECLARED_COUNT_PREFIX'
            if r['active_prefix_status']!=expected:raise ValueError('message active-prefix annotation mismatch')
            text=r['text_fragments'];facts['native_social_message_observations'].append({'message_observation_id':message,
                'bank_index':r['bank_index'],'source_slot_index':r['source_slot_index'],**{col:r['values'][native] for native,col in MESSAGE_NATIVE_MAP.items()},
                **{col:r['date'][native] for native,col in DATE_MAP.items()},'event_label':r['event_label'],'sender_type_label':r['sender_type_label'],
                'string1_fragment':text['String1'],'string2_fragment':text['String2'],'text_status':';'.join(v for k,v in text.items() if k.endswith('_status')) or 'UTF16_PREFIX_FRAGMENTS_ONLY',
                'source_state':r['source_state'],'active_prefix_status':expected})
            if r['values']['Event'] and expected=='WITHIN_DECLARED_COUNT_PREFIX_CANDIDATE':
                facts['game_news_entries'].append({'season_id':period(year),'native_news_id':f'SOCIAL_BANK:{r["bank_index"]}:SLOT:{r["source_slot_index"]}:MESSAGE_INDEX:{r["values"]["MessageIndex"]}',
                    'text_body':None,'occurrence_time':None,'source_message_id':message,'content_status':'NATIVE_NONZERO_EVENT_IN_COUNT_PREFIX_CANDIDATE; RENDERED_TEXT_AND_UI_ACTIVITY_UNVERIFIED'})
        for r in transactions:
            tid=f'{unit}:transaction:{r["source_slot_index"]}';items=r['items']
            if len(items)!=39 or {i['source_item_index'] for i in items}!=set(range(39)):raise ValueError('incomplete transaction parameters')
            expected='WITHIN_DECLARED_COUNT_PREFIX_CANDIDATE' if r['source_slot_index']<tc else 'OUTSIDE_DECLARED_COUNT_PREFIX'
            if r['active_prefix_status']!=expected:raise ValueError('transaction active-prefix annotation mismatch')
            if expected.startswith('WITHIN') and r['values']['NumData']>39:raise ValueError('transaction count exceeds parameter capacity')
            facts['native_transaction_observations'].append({'native_transaction_id':tid,'source_slot_index':r['source_slot_index'],
                'native_type_code':r['values']['Type'],'data_count_raw':r['values']['NumData'],**{col:r['date'][native] for native,col in DATE_MAP.items()},
                'native_type_label':r['type_label'],'active_prefix_status':expected})
            facts['native_transaction_item_observations'].extend({'native_transaction_id':tid,'source_item_index':i['source_item_index'],
                'integer_word_raw':i['Int'],'native_type_code':i['Type']} for i in items)
        control.update({'social_active_count0':active[0],'social_active_count1':active[1],'transaction_count':tc})
        gaps=[('NEWS_RENDERED_TEXT_AND_PARAMETERS','Message enum and parameters are observed but localization/renderer and parameter meanings are not accepted','No generated headlines, player binding or generic raw parameter export'),
            ('NATIVE_SCHEDULEDATE_EPOCH_UI','Date bit components are verified; epoch/month/time UI mapping remains unpromoted','Keep components and raw word; occurrence_time NULL'),
            ('NATIVE_TRANSACTION_EVENT_SEMANTICS','Count/allocated storage and tagged values do not independently prove accepted external transactions','Keep native storage separate from external execution/receipt tables')]
    facts['native_league_capture_controls']=[control]
    facts['field_gaps']=[{'affected_domain':'RES-H' if mode=='HISTORY_AWARDS' else 'RES-M','target_field':t,'reason':r,'impact':i} for t,r,i in gaps]
    return {'save_id':binding['save_id'],'run_id':unit,'unit_id':unit,'source_key':'BOUND_LEAGUE_HISTORY_AND_AWARDS' if mode=='HISTORY_AWARDS' else 'BOUND_NATIVE_NEWS_AND_TRANSACTIONS',
        'observed_at':observed_at,'evidence_grade':'RESEARCH_FIXTURE','decoder_version':'NATIVE_LEAGUE_HISTORY_AND_EVENTS_V1',
        'save_binding_ref':'HUMAN_DECLARED_SAVE:'+binding['save_id']+':'+binding['native_save_filename'],
        'season':{'season_id':f'season:native-year:{year}','season_code':f'NATIVE_YEAR:{year}'},'referenced_seasons':list(periods.values()),
        'facts':facts,'artifacts':artifacts,'completeness':'PARTIAL'}


def capture_league(pid,save_directory,loaded_filename,new_output_directory,*,mode):
    if mode not in ('HISTORY_AWARDS','NEWS_TRANSACTIONS'):raise ValueError('explicit league mode required')
    binding,binding_hash=read_binding(save_directory,loaded_filename);db=bound_database(save_directory,binding)
    out=Path(new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False);reader=None;stamp=datetime.now(timezone.utc).isoformat()
    try:
        reader=ReadOnlyGameProcess(pid)
        if mode=='HISTORY_AWARDS':
            year,previous=prepare_annual_capture(reader,db,'LEAGUE_HISTORY_AWARDS')
            if previous:
                previous.update({'save_id':binding['save_id'],'read_trace':reader.trace});_json(out/'ingest-result.json',previous);return previous
        manifest,blobs=collect_league_source(reader,mode);reader.close()
        if mode=='HISTORY_AWARDS' and manifest['season_year']!=year:raise ValueError('annual league-history season changed')
        for name,raw in blobs.items():(out/name).write_bytes(raw)
        _json(out/'league-source-manifest.json',manifest)
        report={'status':'BOUND_NATIVE_LEAGUE_SOURCE_CAPTURED','mode':mode,'pid':pid,'observed_at':stamp,'binding_sha256':binding_hash,
            'read_trace':reader.trace,'game_writes':False,'player_struct_reads':0,
            'executed_code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(__file__).with_name('league_reader.py'),PROFILE_PATH)},
            'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        _json(out/'league-source-report.json',report)
        artifacts=[{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'byte_count':p.stat().st_size,'restricted':1,
            'payload_kind':'NATIVE_LEAGUE_SOURCE_OR_CONTROL','source_version':'NATIVE_LEAGUE_HISTORY_AND_EVENTS_V1','payload_ref':out.name+'/'+p.name} for p in sorted(out.iterdir()) if p.is_file()]
        token=hashlib.sha256((out/'league-source-report.json').read_bytes()).hexdigest()[:24]
        with connect(db) as conn:
            payload=league_payload(binding,manifest,artifacts,stamp,token,existing_history_awards(conn));payload['evidence_grade']='LIVE_READ'
            if mode=='HISTORY_AWARDS':attach_annual_period(payload,'LEAGUE_HISTORY_AWARDS',manifest['season_year'])
            receipt=_AcquisitionReceipt(payload,reader);status=ingest_capture(conn,payload,_live_receipt=receipt)
        result={'status':status,'mode':mode,'unit_id':payload['unit_id'],'save_id':binding['save_id'],'source_grade':'LIVE_READ',
            'counts':{k:len(v) for k,v in payload['facts'].items()},'game_writes':False,'player_struct_reads':0,'full_goal_complete':False}
        _json(out/'ingest-result.json',result);return result
    except Exception as error:
        _json(out/'failure.json',{'status':'LEAGUE_CAPTURE_OR_INGEST_FAILED','error_type':type(error).__name__,'reason':str(error),
            'read_trace':reader.trace if reader else getattr(error,'read_trace',[]),'game_writes':False});raise
    finally:
        if reader:reader.close()
