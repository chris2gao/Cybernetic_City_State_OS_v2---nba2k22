"""Issue44: independent synthetic sources, actual ingest and read-only queries."""
import hashlib,json,sys
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from engine import create_database,connect,ingest_capture
from observation_scope import query_at

with TemporaryDirectory() as tmp:
    paths=[Path(tmp)/name for name in ('a.sqlite','b.sqlite')]
    ledgers=[]
    for db,value in zip(paths,(60,90)):
        create_database(db,'same-save')
        with connect(db) as conn:
            ingest_capture(conn,{'save_id':'same-save','run_id':'run','unit_id':'unit','source_key':'SYNTHETIC_ISSUE44','observed_at':'2026-10-24T00:00:00Z','evidence_grade':'SYNTHETIC_FIXTURE','season':{'season_id':'s','season_code':'s'},'facts':{'players':[{'player_id':p,'display_name':p} for p in ('p1','p2')],'player_attribute_snapshots':[{'player_id':p,'shot_close_raw':value} for p in ('p1','p2')]}})
            ledgers.append([dict(row) for row in conn.execute('SELECT unit_id,payload_sha256 FROM capture_units')])
    before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    def page(db,**kwargs):return query_at(db,'2026-10-24T00:00:00Z','query_facts','player_attribute_snapshots',limit=1,**kwargs)['result']
    first=page(paths[0]);same=page(paths[0],cursor=first['next_cursor'])
    try:
        cross=page(paths[1],cursor=first['next_cursor']);outcome='ACCEPTED';error=None
    except ValueError as exc:outcome='REJECTED';error=str(exc)
    result={'host_time':datetime.now().astimezone().isoformat(),'ledgers':ledgers,'same_source_rows':len(same['records']),'same_source_next_key':same['records'][0]['row_key'],'cross_source':outcome,'error':error,'query_bytes_unchanged':before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]}
    print(json.dumps(result,sort_keys=True))
    assert ledgers[0][0]['unit_id']==ledgers[1][0]['unit_id'] and ledgers[0][0]['payload_sha256']!=ledgers[1][0]['payload_sha256']
    assert len(same['records'])==1 and result['query_bytes_unchanged']
    if '--require-rejection' in sys.argv:assert outcome=='REJECTED'
