"""Owner preparation of static audited query copies; never opens live saves."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from gm_data_access import AccessError
from gm_data_access.snapshots import install_archive, read_json


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',required=True,help='Existing local exporter Release backup ZIP')
    p.add_argument('--manifest',required=True,help='Existing exported batch manifest.json')
    p.add_argument('--query-root',type=Path,default=ROOT/'database/query_snapshots')
    a=p.parse_args()
    try:
        # An owner must deliberately invoke this; the consumer query CLI has no creation mode.
        if a.query_root.resolve().is_relative_to(ROOT/'database/saves'):
            raise AccessError('INVALID_INPUT','Query root cannot be inside authoritative saves')
        record=install_archive(a.archive,read_json(a.manifest),a.query_root)
        m=record['source_manifest']
        print(json.dumps(dict(status='STATIC_SNAPSHOT_READY',career_id=m['save_id'],batch_id=m['batch_id'],
                              os_permissions=record['os_permissions']),ensure_ascii=False))
        return 0
    except (AccessError,OSError,ValueError,KeyError) as e:
        print(json.dumps(dict(status=getattr(e,'code','BLOCKED_LOCAL_DB_ACCESS'),message=str(e)[:200]),ensure_ascii=False))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
