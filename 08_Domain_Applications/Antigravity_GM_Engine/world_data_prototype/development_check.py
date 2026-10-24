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
from query import player_card,game_box,export_jsonl,team_card,staff_card
from organization_reader import organization_payload
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
    public_text=''.join((out/name).read_text() for name in ('gm-player-card.json','public-player-game-boxes.jsonl','team-card.json','staff-card.json'))
    if any(x in public_text.lower() for x in ('potential','raw_player_hex','protected_value_ref','payload_ref')):
        raise RuntimeError('restricted output in public projection')
    checksums={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    report={'task_id':'nba2k22-world-data-full-implementation-01','increment':'06_RECIPROCAL_ORGANIZATION_TOTALS_COACHING_AND_FINANCE',
        'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip(),
        'status':'DEVELOPMENT_INCREMENT_VERIFIED_FULL_GOAL_NOT_COMPLETE',
        'environment':{'python':platform.python_version(),'platform':platform.system()},
        'test_exit_code':tests.returncode,'test_command':'python -m unittest discover -s 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests -p test_*.py -q',
        'test_evidence':'tests.stderr.log','database':summarize(db),'native_source_status':'HISTORICAL_AG01D_AND_RECORDED_OWNER_LIVE_SOURCE_REPLAY',
        'check_scope':'This command replays fixtures; actual owner read calls are separately recorded in the Native source evidence',
        'actual_owner_acquisition_evidence_ref':'01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/06_执行/increment06/native_sources/source_manifest.json',
        'season_observations':seasons,'observed_team_identities':team_count,
        'public_player_attributes_observed':sum(1 for f in card['families']['player_attribute_snapshots'].values() if f.get('value') is not None),
        'registered_player_families':summarize(family_db),'owner_source_replay':summarize(owner_db),'organization_replay':summarize(org_db),
        'contract_bit_layout':profile_layout_receipt(),
        'queried_player_id':pid,'queried_game_id':gid,'exported_box_rows':export['rows'],
        'schema_domains':sorted({t.domain for t in TABLES.values()}),
        'schema_mapping':{'v1_tables_preserved':16,'approved_provisional_tables':59,'actual_tables':len(TABLES),
            'additional_tables':['game_state_observations','season_finalizations','native_box_observations','team_state_observations']},
        'code_hash_scope':'Actual executed working-tree bytes at candidate_code_head; generated artifacts preserve their bytes via local .gitattributes',
        'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [BASE/'schema.sql',BASE/'field_dictionary.json',BASE/'schema_model.py',BASE/'engine.py',BASE/'readers.py',BASE/'query.py',BASE/'live_reader.py',BASE/'family_codec.py',BASE/'owner_capture.py',BASE/'live_world.py',BASE/'cli.py',BASE/'schedule_reader.py',BASE/'organization_reader.py']},
        'artifact_sha256':checksums,'not_run':['fresh live acquisition inside this verification command','full-domain native source acceptance','100-season capacity benchmark','final managed verification','independent review','Human full-candidate acceptance'],
        'next_owner':'Codex continues engineering and can research Native directly; Human relays Gemini only for selected batch exploration',
        'open_source_gaps':['four unresolved completed-game Native player IDs','calendar UI encoding','cross-session player/staff lifecycle identity','contract/finance UI semantics','badge tier encoding','gameplan rotations/defense and training/mentor source','decoded play names','staff market availability','draft/G League native identities','all setting/rule UI fields','actual awards/records/news sources'],
        'q10_exceptions_approved':[],'game_writes':False,'game_process_access':False,'master_modified':False}
    (out/'development_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'tests_exit':tests.returncode,'tables':len(TABLES),
        'columns':report['database']['column_count'],'games':report['database']['game_count'],'season_observations':seasons,'public_attributes':report['public_player_attributes_observed'],'foreign_key_errors':report['database']['foreign_key_errors']}))
    return 0


if __name__=='__main__':raise SystemExit(main())
