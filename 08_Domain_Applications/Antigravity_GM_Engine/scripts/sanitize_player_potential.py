"""Read-only dry-run of DEV15 masking on in-memory copies of a sealed batch.

Production masking is automatic inside full_verified_v1 before file install.
This command deliberately cannot convert or mutate historical archives.
"""
import argparse
from contextlib import closing
from pathlib import Path
import json
import sqlite3
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gm_data_access.snapshots import load_snapshot
from player_potential_mask import sanitize_player_potential


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--career',required=True)
    p.add_argument('--batch',required=True)
    p.add_argument('--query-root',type=Path,default=ROOT/'database/query_snapshots')
    p.add_argument('--dry-run',action='store_true',required=True)
    a=p.parse_args()
    record=load_snapshot(a.query_root,a.career,a.batch)
    directory=a.query_root/a.career/a.batch
    with closing(sqlite3.connect(':memory:')) as league, closing(sqlite3.connect(':memory:')) as pool:
        for name,dest in (('league_state.sqlite',league),('player_pool.sqlite',pool)):
            with closing(sqlite3.connect((directory/name).resolve().as_uri()+'?mode=ro',uri=True)) as src:
                src.backup(dest)
        receipt=sanitize_player_potential(league,pool,record['source_manifest']['snapshot_id'],dry_run=True)
    print(json.dumps(receipt,ensure_ascii=False,sort_keys=True))


if __name__=='__main__':
    main()
