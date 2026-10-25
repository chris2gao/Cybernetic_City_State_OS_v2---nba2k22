"""Reproducible increment checks and a retained research SQLite example.

This is a development check, not whole-system managed acceptance. All output goes
to a NEW caller-selected directory. It never reads a game process or save file.
"""
from contextlib import closing
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from engine import create_database,connect,ingest_capture,summarize
from readers import replay_ag01d,replay_player_families
from family_codec import profile_layout_receipt
from owner_capture import recorded_game_capture
from query import player_card,game_box,export_jsonl,team_card,staff_card,market_snapshot,planning_snapshot,gameplan_card,settings_snapshot,rules_snapshot,record_book,native_honors
from organization_reader import organization_payload
from market_reader import market_payload
from planning_reader import planning_payload
from settings_reader import settings_payload
from records_reader import records_payload
from award_reader import honors_payload
from schema_model import BASE,TABLES,dictionary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('new_output_directory');args=parser.parse_args()
    out=Path(args.new_output_directory).resolve();out.mkdir(parents=True,exist_ok=False)
    repo=BASE.parents[2]
    test_command=[sys.executable,'-m','unittest','discover','-s',str(BASE/'tests'),'-p','test_*.py','-q']
    tests=subprocess.run(test_command,cwd=repo,capture_output=True)
    (out/'tests.stdout.log').write_bytes(tests.stdout);(out/'tests.stderr.log').write_bytes(tests.stderr)
    if tests.returncode:
        print(json.dumps({'development_tests_exit':tests.returncode,'logs':str(out)}));return tests.returncode
    db=out/'ag01d-world.sqlite';create_database(db,'AG01D-RESEARCH-ONLY')
    applied=[]
    for bundle in replay_ag01d('AG01D-RESEARCH-ONLY',observed_at='2026-10-24T00:00:00Z'):
        with connect(db) as c:applied.append(ingest_capture(c,bundle))
    with connect(db) as c:
        pid=c.execute('SELECT player_id FROM players').fetchone()[0]
        gid=c.execute('SELECT game_id FROM games ORDER BY game_id LIMIT 1').fetchone()[0]
        seasons=c.execute('SELECT count(*) FROM player_season_totals').fetchone()[0]
        team_count=c.execute('SELECT count(*) FROM teams').fetchone()[0]
    card=player_card(db,pid);box=game_box(db,gid)
    (out/'gm-player-card.json').write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'game-box.json').write_text(json.dumps(box,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    export=export_jsonl(db,out/'public-player-game-boxes.jsonl','player_game_boxes')
    family_db=out/'registered-players.sqlite';create_database(family_db,'AG01D-REGISTERED-PLAYERS')
    for payload in replay_player_families('AG01D-REGISTERED-PLAYERS',observed_at='2026-10-24T00:00:00Z'):
        with connect(family_db) as c:ingest_capture(c,payload)
    owner_db=out/'owner-capture-research.sqlite';create_database(owner_db,'OWNER_CAPTURE_RESEARCH_ONLY')
    owner_payload=recorded_game_capture(BASE/'tests/fixtures/owner_capture_20261024','OWNER_CAPTURE_RESEARCH_ONLY')
    with connect(owner_db) as c:ingest_capture(c,owner_payload)
    org_source=BASE/'tests/fixtures/organization_20261024'
    org_manifest=json.loads((org_source/'manifest.json').read_bytes());org_sources=json.loads((org_source/'source_manifest.json').read_bytes())
    for name,digest in org_sources['files'].items():
        if hashlib.sha256((org_source/name).read_bytes()).hexdigest()!=digest:raise ValueError('organization fixture hash mismatch')
    org_db=out/'organization-research.sqlite';create_database(org_db,'ORGANIZATION_RESEARCH_ONLY')
    org_payload=organization_payload({'save_id':'ORGANIZATION_RESEARCH_ONLY','native_save_filename':'MyLEAGUE0003'},org_manifest,
        [{'sha256':digest,'payload_kind':'ACTUAL_CURATED_ORGANIZATION_RESEARCH','payload_ref':name} for name,digest in org_sources['files'].items()],
        '2026-10-24T00:00:00Z','development-fixture')
    with connect(org_db) as c:ingest_capture(c,org_payload)
    (out/'team-card.json').write_text(json.dumps(team_card(org_db,'team:native:0'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'staff-card.json').write_text(json.dumps(staff_card(org_db,'staff:native:70'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    market_source=BASE/'tests/fixtures/market_20261024';market_manifest=json.loads((market_source/'manifest.json').read_bytes())
    market_sources=json.loads((market_source/'source_manifest.json').read_bytes())
    for name,digest in market_sources['files'].items():
        if hashlib.sha256((market_source/name).read_bytes()).hexdigest()!=digest:raise ValueError('market fixture hash mismatch')
    market_db=out/'market-research.sqlite';create_database(market_db,'MARKET_RESEARCH_ONLY')
    bundle=market_payload({'save_id':'MARKET_RESEARCH_ONLY','native_save_filename':'MyLEAGUE0003'},market_manifest,
        [{'sha256':digest,'payload_kind':'ACTUAL_MARKET_RESEARCH','payload_ref':name} for name,digest in market_sources['files'].items()],
        '2026-10-24T00:00:00Z','development-fixture')
    with connect(market_db) as c:ingest_capture(c,bundle)
    (out/'market-snapshot.json').write_text(json.dumps(market_snapshot(market_db),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    plan_source=BASE/'tests/fixtures/planning_20261024';plan_manifest=json.loads((plan_source/'manifest.json').read_bytes())
    plan_sources=json.loads((plan_source/'source_manifest.json').read_bytes())
    for name,digest in plan_sources['files'].items():
        if hashlib.sha256((plan_source/name).read_bytes()).hexdigest()!=digest:raise ValueError('planning fixture hash mismatch')
    plan_db=out/'planning-research.sqlite';create_database(plan_db,'PLANNING_RESEARCH_ONLY')
    bundle=planning_payload({'save_id':'PLANNING_RESEARCH_ONLY','native_save_filename':'MyLEAGUE0003'},plan_manifest,
        [{'sha256':digest,'payload_kind':'ACTUAL_PLANNING_RESEARCH','payload_ref':name} for name,digest in plan_sources['files'].items()],
        '2026-10-24T00:00:00Z','development-fixture')
    with connect(plan_db) as c:ingest_capture(c,bundle)
    (out/'planning-snapshot.json').write_text(json.dumps(planning_snapshot(plan_db),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'gameplan-card.json').write_text(json.dumps(gameplan_card(plan_db,'team:native:20','team:native:0'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    settings_source=BASE/'tests/fixtures/settings_20261024';settings_manifest=json.loads((settings_source/'manifest.json').read_bytes())
    settings_sources=json.loads((settings_source/'source_manifest.json').read_bytes())
    for name,digest in settings_sources['files'].items():
        if hashlib.sha256((settings_source/name).read_bytes()).hexdigest()!=digest:raise ValueError('settings fixture hash mismatch')
    settings_db=out/'settings-research.sqlite';create_database(settings_db,'SETTINGS_RESEARCH_ONLY')
    bundle=settings_payload({'save_id':'SETTINGS_RESEARCH_ONLY','native_save_filename':'MyLEAGUE0003'},settings_manifest,
        [{'sha256':digest,'payload_kind':'ACTUAL_SETTINGS_WORD_RESEARCH','payload_ref':name} for name,digest in settings_sources['files'].items()],
        '2026-10-24T00:00:00Z','development-fixture')
    with connect(settings_db) as c:ingest_capture(c,bundle)
    settings=settings_snapshot(settings_db);rules=rules_snapshot(settings_db)
    (out/'settings-snapshot.json').write_text(json.dumps(settings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'rules-snapshot.json').write_text(json.dumps(rules,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Registered global contract-factor labels can contain 'potential', but
    # no PLAYER source or value is acquired by the settings adapter.
    with connect(settings_db,True) as c:
        if c.execute('SELECT count(*) FROM players').fetchone()[0]:raise RuntimeError('PLAYER data in settings-only replay')
    if any(x in json.dumps([settings,rules]).lower() for x in ('raw_player_hex','protected_value_ref','payload_ref','"address"')):
        raise RuntimeError('restricted source metadata in settings projection')
    record_source=BASE/'tests/fixtures/records_20261024';record_manifest=json.loads((record_source/'manifest.json').read_bytes())
    record_sources=json.loads((record_source/'source_manifest.json').read_bytes())
    for name,digest in record_sources['files'].items():
        if hashlib.sha256((record_source/name).read_bytes()).hexdigest()!=digest:raise ValueError('record fixture hash mismatch')
    record_db=out/'records-research.sqlite';create_database(record_db,'RECORDS_RESEARCH_ONLY')
    bundle=records_payload({'save_id':'RECORDS_RESEARCH_ONLY','native_save_filename':'MyLEAGUE0003'},record_manifest,
        [{'sha256':digest,'payload_kind':'ACTUAL_CURATED_RECORD_BOOK','payload_ref':name} for name,digest in record_sources['files'].items()],
        '2026-10-24T00:00:00Z','development-fixture')
    with connect(record_db) as c:ingest_capture(c,bundle)
    (out/'record-book-page.json').write_text(json.dumps(record_book(record_db),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'wilt-records.json').write_text(json.dumps(record_book(record_db,category_code=0x8f,subject_name='Wilt Chamberlain'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    honor_source=BASE/'tests/fixtures/honors_20261025';honor_manifest=json.loads((honor_source/'manifest.json').read_bytes())
    honor_sources=json.loads((honor_source/'source_manifest.json').read_bytes())
    for name,digest in honor_sources['files'].items():
        if hashlib.sha256((honor_source/name).read_bytes()).hexdigest()!=digest:raise ValueError('native honor fixture hash mismatch')
    honor_db=out/'native-honors-research.sqlite';create_database(honor_db,'NATIVE_HONORS_RESEARCH_ONLY')
    canonical={'player:native:'+str(p['preserved_id_raw']):p['observed_name'] for p in honor_manifest['players'] if p['current_core_roster_status']=='CURRENT_CORE_ROSTER'}
    bundle=honors_payload({'save_id':'NATIVE_HONORS_RESEARCH_ONLY','native_save_filename':'MyLEAGUE0003'},honor_manifest,
        [{'sha256':digest,'payload_kind':'ACTUAL_CURATED_NATIVE_STAT_AND_PUBLIC_PROJECTIONS','payload_ref':name} for name,digest in honor_sources['files'].items()],
        '2026-10-25T00:00:00Z','development-fixture',canonical)
    bundle['facts']['players']=[{'player_id':k,'display_name':v,'native_player_id':k.rsplit(':',1)[1],'native_identity_status':'UNVERIFIED'} for k,v in canonical.items()]
    with connect(honor_db) as c:ingest_capture(c,bundle)
    (out/'native-mvp-source.json').write_text(json.dumps(native_honors(honor_db,flag='mvp_raw'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'native-honor-source.json').write_text(json.dumps(native_honors(honor_db),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    public_text=''.join((out/name).read_text() for name in ('gm-player-card.json','public-player-game-boxes.jsonl','team-card.json','staff-card.json','market-snapshot.json','planning-snapshot.json','gameplan-card.json','record-book-page.json','wilt-records.json','native-mvp-source.json','native-honor-source.json'))
    if any(x in public_text.lower() for x in ('potential','raw_player_hex','protected_value_ref','payload_ref')):
        raise RuntimeError('restricted output in public projection')
    checksums={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    report={'task_id':'nba2k22-world-data-full-implementation-01','increment':'11_NATIVE_STAT_HONOR_FIELDS_COMPLETE_SOURCE_REFERENCES_AND_PRIVACY',
        'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip(),
        'status':'DEVELOPMENT_INCREMENT_VERIFIED_FULL_GOAL_NOT_COMPLETE',
        'environment':{'python':platform.python_version(),'platform':platform.system()},
        'test_exit_code':tests.returncode,'test_command':'python -m unittest discover -s 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests -p test_*.py -q',
        'test_evidence':'tests.stderr.log','database':summarize(db),'native_source_status':'HISTORICAL_AG01D_AND_RECORDED_OWNER_LIVE_SOURCE_REPLAY',
        'check_scope':'This command replays fixtures; actual owner read calls are separately recorded in the Native source evidence',
        'actual_owner_acquisition_evidence_ref':'01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/06_执行/increment11/native_sources/source_manifest.json',
        'season_observations':seasons,'observed_team_identities':team_count,
        'public_player_attributes_observed':sum(1 for f in card['families']['player_attribute_snapshots'].values() if f.get('value') is not None),
        'registered_player_families':summarize(family_db),'owner_source_replay':summarize(owner_db),'organization_replay':summarize(org_db),'market_replay':summarize(market_db),'planning_replay':summarize(plan_db),'settings_replay':summarize(settings_db),'records_replay':summarize(record_db),'native_honors_replay':summarize(honor_db),
        'contract_bit_layout':profile_layout_receipt(),
        'queried_player_id':pid,'queried_game_id':gid,'exported_box_rows':export['rows'],
        'schema_domains':sorted({t.domain for t in TABLES.values()}),
        'schema_mapping':{'v1_tables_preserved':16,'approved_provisional_tables':59,'actual_tables':len(TABLES),
            'additional_tables':['game_state_observations','season_finalizations','native_box_observations','team_state_observations',
                'draft_pool_slot_observations','draft_prospect_attribute_snapshots','draft_prospect_tendency_snapshots','draft_prospect_play_type_slots','waived_salary_observations',
                'gameplan_observations','gameplan_rotation_observations','gameplan_defense_observations','player_training_slot_observations','mentor_manager_observations','native_mentor_relation_observations',
                'native_player_stat_observations','native_player_sources','native_player_stat_links']},
        'code_hash_scope':'Actual executed working-tree bytes at candidate_code_head; generated artifacts preserve their bytes via local .gitattributes',
        'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [BASE/'schema.sql',BASE/'field_dictionary.json',BASE/'schema_model.py',BASE/'engine.py',BASE/'readers.py',BASE/'query.py',BASE/'live_reader.py',BASE/'family_codec.py',BASE/'owner_capture.py',BASE/'live_world.py',BASE/'cli.py',BASE/'schedule_reader.py',BASE/'organization_reader.py',BASE/'market_reader.py',BASE/'planning_reader.py',BASE/'settings_reader.py',BASE/'records_reader.py',BASE/'award_reader.py',BASE/'award_native_profile.json']},
        'artifact_sha256':checksums,'not_run':['fresh live acquisition inside this verification command','full-domain native source acceptance','100-season capacity benchmark','final managed verification','independent review','Human full-candidate acceptance'],
        'next_owner':'Codex continues engineering and can research Native directly; Human relays Gemini only for selected batch exploration',
        'open_source_gaps':['four unresolved completed-game Native player IDs','calendar UI encoding','cross-session player/staff lifecycle identity; preserved vs unique ID canonical transition not inferred','contract/finance UI semantics','badge tier encoding','training focus/schedules and safe history fields','global rotation and committed-plan effect','mentor badge activity/effect','decoded play names','player/staff market availability','initialized prospect class/year and G League identities','pick protection/swaps and historical results','global setting NativeType descriptors, full UI names/ranges/scale and remaining league rules','record category/subject/scope/date semantics; native honor flag subjects/allocation/final-instance acceptance and news source'],
        'q10_exceptions_approved':[],'game_writes':False,'game_process_access':False,'master_modified':False}
    (out/'development_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'tests_exit':tests.returncode,'tables':len(TABLES),
        'columns':report['database']['column_count'],'games':report['database']['game_count'],'season_observations':seasons,'public_attributes':report['public_player_attributes_observed'],'foreign_key_errors':report['database']['foreign_key_errors']}))
    return 0


if __name__=='__main__':raise SystemExit(main())
