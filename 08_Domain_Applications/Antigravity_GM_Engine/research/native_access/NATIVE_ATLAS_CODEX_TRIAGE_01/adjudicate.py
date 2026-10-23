"""Offline evidence adjudication. Does not import/execute historical readers."""
from collections import Counter
from datetime import date
import ast
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parent

def load(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))

def pointer_number(value):
    return 0 if value in (None,'NULL') else int(value,16)

def checked_size(count,stride):
    if type(count) is not int or count<0 or type(stride) is not int or stride<=0:
        raise ValueError('Count/stride must be nonnegative/positive integers, not floats or booleans')
    result=count*stride
    if result>2**63-1:
        raise ValueError('Byte range overflow')
    return result

def check_layout(stride, fields):
    checked_size(1,stride)
    occupied=set()
    for offset,size in fields:
        if type(offset) is not int or offset<0 or type(size) is not int or size<=0 or offset+size>stride:
            raise ValueError('Field exceeds physical record bounds')
        positions=set(range(offset,offset+size))
        if occupied & positions:
            raise ValueError('Overlapping declared storage fields')
        occupied |= positions
    return True

def record_fields(raw):
    if len(raw)!=52:
        raise ValueError('A complete 52-byte record fixture is required')
    # Only two bounded text regions and the float are interpreted. Packed tail
    # words remain raw: historical player_id/category/flags labels are not facts.
    names=[]
    for off in (0,20):
        value=raw[off:off+20].split(b'\0',1)[0]
        if any(x<32 or x>126 for x in value):
            raise ValueError('Fixture text not printable ASCII; preserve raw instead')
        names.append(value.decode('ascii'))
    value=struct.unpack_from('<f',raw,40)[0]
    if not math.isfinite(value):
        raise ValueError('Non-finite value')
    return dict(first_text=names[0],last_text=names[1],numeric_value=value,
                tail_words_raw=list(struct.unpack_from('<4H',raw,44)))

def raw_draft_fields(raw):
    if len(raw)!=32:
        raise ValueError('Expected 32-byte draft record')
    a,b,c,link,meta=struct.unpack('<QQQII',raw)
    return dict(qword_00=a,qword_08=b,qword_10=c,link_token_raw=link,metadata_raw=meta,
                group_low3=meta&7,round_code_raw=(meta>>3)&31,
                index_raw=(meta>>8)&255,alternate_identity_bit17=bool(meta&(1<<17)),
                year_bits22_31_raw=(meta>>22)&1023,
                protection='UNKNOWN_NOT_DECODED',swap='UNKNOWN_NOT_DECODED')

def raw_playbook_fields(raw):
    if len(raw)!=360:
        raise ValueError('Expected complete 360-byte playbook fixture')
    return dict(lookup_key_low7=raw[84]&127,play_values_raw=list(struct.unpack_from('<68I',raw,88)),
                team_identity='UNKNOWN_REQUIRES_MAPPING',effects='NOT_VERIFIED')

def build():
    atlas=load('sources/wide/native_object_atlas_75.json')
    history=load('sources/ag01c/object_catalog.json')
    old={s['slot_index']:s for s in history['descriptors']}
    static=load('static_evidence.json')
    by_slot={}
    for g in static['getters']:
        by_slot.setdefault(g['slot'],[]).append(g)
    enrich=ast.parse((ROOT/'sources/wide/enrich_atlas_and_artifacts.py').read_text(encoding='utf-8'))
    metadata=next(ast.literal_eval(n.value) for n in enrich.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SLOT_METADATA' for t in n.targets))
    # Each rejection is about a specific source claim; not global absence.
    rejected={
       5:'Global CBA rules claim contradicted by native GetFreeAgentDataByIndex family.',
       6:'Team market configuration claim contradicted by native GetStadiumDataByIndex family.',
       9:'Arena/court/uniform claim contradicted by native GetCollegeDataByIndex; fractional stride rejected.',
       10:'Championship/record history claim contradicted by native GetNBAScheduleDataByIndex.',
       11:'Historical awards claim contradicted by native GetNBAAllTwiceScheduleDataByIndex.',
       12:'Retired-jersey/Hall-of-Fame claim contradicted by native GetNBAAllOnceScheduleDataByIndex.',
       13:'Record-book index claim contradicted by native GetNBAConfScheduleDataByIndex.',
       18:'Coach philosophy claim contradicted by native GetPreseasonScheduleDataByIndex.',
       21:'Calendar events claim contradicted by native GetCoachStatDataByIndex.',
       22:'Rotation timeline claim contradicted by native GetPlaybookDataByIndex and 68-case play accessor.',
       25:'Playoff-stat manager claim contradicted by native GetPlayerShotChartManagerDataByIndex.',
       26:'Player playoff totals claim contradicted by native GetPlayerShotChartDataByIndex.',
       30:'Team playoff totals claim contradicted by native GetTeamShotChartDataByIndex.',
       31:'Career-high stat claim contradicted by native GetFirstNameDataByIndex.',
       32:'Advanced/tracking stat claim contradicted by native GetLastNameDataByIndex.',
       33:'All-Star stat claim contradicted by native GetCityNameDataByIndex.',
       34:'Finals stat claim contradicted by native GetTeamMascotNameDataByIndex.',
       35:'Financial ledger claim contradicted by native GetCustomUniformDataByIndex.',
       38:'Standings/tiebreak rule claim is not supported by native GetSpecialTeamDataByIndex; retain unknown fields.',
       39:'Year-by-year career layout contradicted by names/float fixture and native record consumers.',
       41:'Draft-combine measurement claim contradicted by native GetLeagueHistoryDataByIndex.',
       46:'Free-agent preference claim contradicted by native GetHallOfFameDataByIndex.',
       47:'GM/Owner relationship claim contradicted by native GetOnlineTeamupDataByIndex.',
       50:'Playbook catalogue claim contradicted by native GetPlayerAccessoryDataByIndex.',
       52:'Play diagram/route claim contradicted by native GetPlayerBoostDataByIndex.',
       55:'Arena operating expense claim contradicted by native GetSkinDataByIndex.',
       59:'Luxury-tax configuration claim contradicted by native GetBlacktopDataByIndex.',
       63:'Contract options claim contradicted by native GetRetiredJerseyDataByIndex.',
       65:'All-Defensive/All-NBA voting claim not established by native GetHistoricAllStarDataByIndex.',
       66:'Salary cap exceptions claim contradicted by native GetCityDataByIndex.',
       67:'Traded-player-exception claim contradicted by native GetShoeStyleDataByIndex.',
       68:'Chemistry/morale matrix claim contradicted by native GetAttributeRangeDataByIndex.',
       69:'Global injury matrix claim contradicted by native GetRosterIndexDataByIndex.',
       71:'Staff budget claim contradicted by native GetTradeExceptionDataByIndex.',
       74:'Global feature-bitmask claim not established by native GetIndexStorageDataByIndex.',
    }
    rows=[]
    for s in atlas['slots']:
        slot=s['slot_index'];h=old[slot];gs=by_slot.get(slot,[])
        labels=['DESCRIPTOR_OBSERVED']
        if h['object_name']!='UNKNOWN':labels.append('NAME_HISTORICAL')
        if slot in metadata:labels.append('NAME_HYPOTHESIS')
        if gs or slot==1:labels.append('SEMANTICALLY_CORROBORATED')
        if slot in rejected:labels.append('REJECTED_OR_CONFLICT')
        stride=s['inferred_stride_bytes']
        stride_status='HISTORICAL_INFERENCE_NOT_REVALIDATED'
        if type(stride) is not int or stride<=0:
            stride_status='REJECTED_NONINTEGER_OR_MISSING'
        if slot in {1,9,22,24,35,39,42,61}:
            stride={1:1264,9:60,22:360,24:48,35:4020,39:52,42:32,61:136}[slot]
            stride_status='STATIC_CODE_VERIFIED_FOR_HASHED_IMAGE'
        rows.append(dict(slot_index=slot,evidence_labels=labels,
            descriptor=dict(count=s['live_count'],pointer=s['live_pdata_hex'],reported_readable=s['is_readable'],
              matches_historical_count=s['live_count']==h['count'],matches_historical_pointer=pointer_number(s['live_pdata_hex'])==pointer_number(h['pointer_hex']),
              confidence='SOURCE_REPORT_AND_HISTORICAL_FIXTURE_ONLY',new_process_or_save_verified=False),
            historical_name=h['object_name'],historical_name_source='sources/ag01c/object_catalog.json#/descriptors/'+str(slot),
            wide_hypothesis=s.get('temporal_or_identity_relation'),hypothesis_source='sources/wide/enrich_atlas_and_artifacts.py:SLOT_METADATA',
            native_names=sorted(set(r['value'] for g in gs for r in g['resources'])) if slot!=1 else ['ROSTERDATA Slot 1 indexed PLAYER layout (type name not inferred from size alone)'],
            static_evidence_refs=[f"static_evidence.json#/getters/{static['getters'].index(g)}" for g in gs] if slot!=1 else ['static_evidence.json#/extras/player_getter'],
            static_name_confidence='HIGH_BUILD_SPECIFIC' if gs else ('PLAYER_LAYOUT_CORROBORATED_HISTORICAL_NAME_ONLY' if slot==1 else 'NOT_CORROBORATED_THIS_PASS'),
            stride_bytes=stride if stride_status!='REJECTED_NONINTEGER_OR_MISSING' else None,
            stride_status=stride_status,conflict=rejected.get(slot),
            source_refs=['sources/wide/native_object_atlas_75.json#/slots/'+str(slot),'sources/ag01c/object_catalog.json#/descriptors/'+str(slot)],
            current_save_identity='NOT_VERIFIED',production_query='NOT_ASSESSED',game_write='NOT_AUTHORIZED',save_reload='NOT_TESTED'))
    audit=load('sources/wide/read_audit_log.json')
    calls=audit['calls'];heads=[c for c in calls if c['target'].endswith('_head_probe')];tails=[c for c in calls if c['target'].endswith('_tail_probe')]
    raw=(ROOT/'sources/ag01c/fixtures/sample_record_book_500.bin').read_bytes()
    records=[record_fields(raw[i:i+52]) for i in range(0,len(raw),52)]
    bad_stride=atlas['slots'][9]['inferred_stride_bytes']
    result=dict(schema='triage.adjudication.v1',source_commit='b779ad8d677b0f7bb53fdb99e9f8acf12d3d7482',
        static_image_sha256=static['image']['sha256'],slots=rows,
        summary=dict(slot_count=len(rows),matching_historical_pairs=sum(r['descriptor']['matches_historical_count'] and r['descriptor']['matches_historical_pointer'] for r in rows),
            active_reported=sum(bool(s['live_count'] and s['live_pdata_hex']!='NULL') for s in atlas['slots']),
            empty_reported=sum(s['live_count']==0 and s['live_pdata_hex']=='NULL' for s in atlas['slots']),
            named_static_slots=len(by_slot),static_plus_player_layout_slots=len(by_slot)+1,
            explicit_source_claim_conflicts=len(rejected),new_live_reads_performed=0),
        contradictions=dict(slot39=dict(first_record=records[0],second_record=records[1],fixture_records=len(records),
            proposed_leading_u16s=list(struct.unpack_from('<HH',raw)),tail_id_namespace='UNKNOWN_NOT_A_CONFIRMED_SLOT1_INDEX',
            fixture_confidence='Two text regions and float fit sample; tail raw until independent semantic proof.'),
          slot22=dict(rejected_grid_min_bytes=48*5*2,stride_bytes=360,play_field_base=88,play_count=68,play_width=4,play_end_exclusive=360,
            masked_lookup_field=dict(offset=84,mask=127,meaning='native lookup key; team identity mapping not yet verified')),
          slot9=dict(imported_stride=bad_stride,imported_total=atlas['slots'][9]['total_buffer_bytes'],verified_stride=60,
            verified_payload=583*60,adjacent_allocation_gap=34984,arithmetic_slack=4,
            note='Adjacent allocation gap is not allocator padding proof; do not round imported float or treat it as exact stride.'),
          slot42=dict(native_family='DraftData',record_stride=32,record_shape='three qwords + token u32 + metadata u32',
            named_consumer='DraftData_GetByPickTeamAndIndex',native_link_consumer='DRAFTDATA::GetLinkedPick',
            protection_semantics='UNKNOWN',scope_note='Structural bit access is corroborated; year epoch/protection/swap/UI/save semantics are not newly verified.')),
        audit=dict(explicit_logged_calls=len(calls),head_calls=len(heads),tail_calls=len(tails),
          explicit_object_sample_bytes=sum(c['size_bytes'] for c in heads+tails),
          total_explicit_logged_bytes=sum(c['size_bytes'] for c in calls),
          lower_layer_completeness='NOT_PROVEN',permission_disposition='NO_RETROACTIVE_AUTHORIZATION',
          original_managed_verify_scope='JSON/schema/files/log-assertions; not independent live calls or semantic acceptance'),
        limitations=['75 identical count/pointer pairs are compatible with same active session or reused observations; neither freshness nor fabrication is proved.',
                     '64 static family names do not mean 64 decoded objects, 64 current-save bindings or 64 role-query APIs.',
                     'Not observed and unknown fields must not be marked NON_EXISTENT.',
                     'This static evidence cannot establish legality of prior buffer probes or establish every lower-layer call.'])
    return result

def main():
    result=build()
    (ROOT/'adjudication_75.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['summary']))
    print(json.dumps(result['audit']))

if __name__=='__main__':main()
