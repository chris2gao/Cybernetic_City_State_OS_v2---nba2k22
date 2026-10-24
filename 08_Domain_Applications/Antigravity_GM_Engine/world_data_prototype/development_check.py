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
from readers import replay_ag01d
from query import player_card,game_box,export_jsonl
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
    public_text=(out/'gm-player-card.json').read_text()+(out/'public-player-game-boxes.jsonl').read_text()
    if any(x in public_text.lower() for x in ('potential','raw_player_hex','protected_value_ref','payload_ref')):
        raise RuntimeError('restricted output in public projection')
    checksums={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    report={'task_id':'nba2k22-world-data-full-implementation-01','increment':'01_ALL_DOMAIN_DDL_AND_RESEARCH_ADAPTER',
        'candidate_code_head':subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True,check=True).stdout.strip(),
        'status':'DEVELOPMENT_INCREMENT_VERIFIED_FULL_GOAL_NOT_COMPLETE',
        'environment':{'python':platform.python_version(),'platform':platform.system()},
        'test_exit_code':tests.returncode,'test_command':'python -m unittest discover -s 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests -p test_*.py -q',
        'test_evidence':'tests.stderr.log','database':summarize(db),'native_source_status':'HISTORICAL_RESEARCH_FIXTURE_REPLAY_NOT_CURRENT_LIVE',
        'season_observations':seasons,'observed_team_identities':team_count,
        'public_player_attributes_observed':sum(1 for f in card['families']['player_attribute_snapshots'].values() if f.get('value') is not None),
        'queried_player_id':pid,'queried_game_id':gid,'exported_box_rows':export['rows'],
        'implemented_domains':sorted({t.domain for t in TABLES.values()}),
        'schema_mapping':{'v1_tables_preserved':16,'approved_provisional_tables':59,'actual_tables':len(TABLES),
            'additional_tables':['game_state_observations','season_finalizations']},
        'code_hash_scope':'Actual executed working-tree bytes at candidate_code_head; generated artifacts preserve their bytes via local .gitattributes',
        'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [BASE/'schema.sql',BASE/'field_dictionary.json',BASE/'schema_model.py',BASE/'engine.py',BASE/'readers.py',BASE/'query.py']},
        'artifact_sha256':checksums,'not_run':['live process acquisition','full-domain native source acceptance','100-season capacity benchmark','final managed verification','independent review','Human full-candidate acceptance'],
        'next_owner':'Human-relayed Antigravity bounded Native evidence, then Codex integration',
        'open_source_gaps':['current process/build/save binding','full active schedule window and both-team Box participants','contract offset 833 ambiguity','badge tier encoding','staff-to-team and full coaching source','draft/G League native identities','all setting/rule UI fields','actual awards/records/news sources'],
        'q10_exceptions_approved':[],'game_writes':False,'game_process_access':False,'master_modified':False}
    (out/'development_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'tests_exit':tests.returncode,'tables':len(TABLES),
        'columns':report['database']['column_count'],'games':report['database']['game_count'],'season_observations':seasons,'public_attributes':report['public_player_attributes_observed'],'foreign_key_errors':report['database']['foreign_key_errors']}))
    return 0


if __name__=='__main__':raise SystemExit(main())
