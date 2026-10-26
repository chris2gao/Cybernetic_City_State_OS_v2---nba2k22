"""Public typed filters, fixed-ledger paging and complete exclusive exports."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE))
from engine import create_database,connect,ingest_capture
from fact_queries import fact_fields,query_facts,export_filtered_facts
from observation_scope import query_at,observed_as_of
from schema_model import TABLES
T0='2026-10-24T00:00:00Z';T1='2026-10-25T00:00:00Z'

class FactQueryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.db=Path(self.tmp.name)/'world.sqlite';create_database(self.db,'save')
        self.put('old',T0,[('p1',60),('p2',70),('p3',None),('p4',90)])
        self.put('new',T1,[('p1',80),('p2',75)])
    def put(self,unit,stamp,values):
        facts={'players':[{'player_id':p,'display_name':"O'Brien" if p=='p2' else p} for p,v in values], 'player_attribute_snapshots':[{'player_id':p,'shot_close_raw':v} for p,v in values]}
        with connect(self.db) as conn:ingest_capture(conn,{'save_id':'save','run_id':unit,'unit_id':unit,'source_key':'SYNTHETIC_FILTERS','observed_at':stamp,'evidence_grade':'SYNTHETIC_FIXTURE','season':{'season_id':'s','season_code':'s'},'facts':facts})
    def test_typed_and_filters_projection_and_source_metadata(self):
        value=query_facts(self.db,'player_attribute_snapshots',columns=['player_id','shot_close_raw'],filters=[{'column':'shot_close_raw','op':'gte','value':70},{'column':'shot_close_raw','op':'lt','value':90}])
        self.assertEqual(sorted(r['values']['shot_close_raw'] for r in value['records']),[70,75,80])
        self.assertTrue(all(set(r['values'])=={'player_id','shot_close_raw'} for r in value['records']))
        self.assertEqual(value['records'][0]['provenance']['source_grade'],'SYNTHETIC_FIXTURE');self.assertEqual(value['observation_scope']['save_id'],'save')
    def test_text_in_quotes_and_injection_values_are_bound_literals(self):
        rows=query_facts(self.db,'players',filters=[{'column':'display_name','op':'eq','value':"O'Brien"}])['records'];self.assertEqual(rows[0]['values']['player_id'],'p2')
        self.assertEqual(query_facts(self.db,'players',filters=[{'column':'display_name','op':'eq','value':"' OR 1=1 --"}])['records'],[])
        rows=query_facts(self.db,'players',columns=['player_id'],filters=[{'column':'player_id','op':'in','value':['p1','p4']}])['records'];self.assertEqual([r['values']['player_id'] for r in rows],['p1','p4'])
    def test_explicit_null_filters_preserve_null(self):
        value=query_facts(self.db,'player_attribute_snapshots',columns=['shot_close_raw'],filters=[{'column':'shot_close_raw','op':'is_null'}]);self.assertEqual([r['values'] for r in value['records']],[{'shot_close_raw':None}])
        self.assertEqual(len(query_facts(self.db,'player_attribute_snapshots',filters=[{'column':'shot_close_raw','op':'not_null'}])['records']),5)
    def test_rejects_invalid_columns_predicates_types_and_caps(self):
        cases=[{'columns':[]},{'columns':['player_id','player_id']},{'columns':['potential_raw']},{'columns':['player_id;DROP TABLE saves']},{'filters':[{'column':'shot_close_raw','op':'eq','value':True}]},{'filters':[{'column':'shot_close_raw','op':'eq','value':70.0}]},{'filters':[{'column':'shot_close_raw','op':'eq','value':2**63}]},{'filters':[{'column':'player_id','op':'eq','value':1}]},{'filters':[{'column':'shot_close_raw','op':'eq','value':None}]},{'filters':[{'column':'shot_close_raw','op':'is_null','value':None}]},{'filters':[{'column':'player_id','op':'in','value':[]}]},{'filters':[{'column':'player_id','op':'LIKE','value':'p%'}]},{'limit':True},{'limit':1001},{'limit':0}]
        for kw in cases:
            with self.subTest(kw=kw),self.assertRaises(ValueError):query_facts(self.db,'player_attribute_snapshots',**kw)
    def test_all_owner_datasets_and_unsupported_roles_are_denied(self):
        for table,spec in TABLES.items():
            if not spec.public:
                with self.subTest(table=table),self.assertRaises(PermissionError):query_facts(self.db,table)
                with self.assertRaises(PermissionError):export_filtered_facts(self.db,Path(self.tmp.name)/'denied',table)
        for role in ('OWNER','player',None):
            with self.assertRaises(PermissionError):query_facts(self.db,'players',role=role)
        self.assertFalse((Path(self.tmp.name)/'denied').exists())
    def test_cursor_pages_all_observations_once_in_key_order(self):
        values=[];cursor=None
        while True:
            page=query_facts(self.db,'player_attribute_snapshots',limit=1,cursor=cursor);values.extend(page['records']);cursor=page['next_cursor']
            if cursor is None:break
        self.assertEqual(len(values),6);self.assertEqual(len({r['row_key'] for r in values}),6);self.assertEqual([r['row_key'] for r in values],sorted(r['row_key'] for r in values))
    def test_changed_target_cutoff_and_eligible_ledger_rejected(self):
        first=query_at(self.db,T0,'query_facts','player_attribute_snapshots',limit=1)['result'];cursor=first['next_cursor']
        with self.assertRaisesRegex(ValueError,'target'):query_facts(self.db,'player_attribute_snapshots',cursor=cursor,columns=['player_id'])
        with self.assertRaisesRegex(ValueError,'cutoff'):query_at(self.db,T1,'query_facts','player_attribute_snapshots',cursor=cursor)
        self.put('backfilled',T0,[('p1',65)])
        with self.assertRaisesRegex(ValueError,'ledger'):query_facts(self.db,'player_attribute_snapshots',cursor=cursor)
    def test_later_observation_does_not_change_pinned_cutoff(self):
        first=query_at(self.db,T0,'query_facts','player_attribute_snapshots',limit=1)['result'];self.put('later',T1,[('p4',95)])
        rest=query_facts(self.db,'player_attribute_snapshots',cursor=first['next_cursor']);self.assertEqual(len(rest['records']),3);self.assertEqual(rest['observation_scope'],first['observation_scope'])
    def test_export_hash_metadata_projection_and_exclusive_output(self):
        out=Path(self.tmp.name)/'export';kw={'columns':['player_id','shot_close_raw'],'filters':[{'column':'unit_id','op':'eq','value':'old'}]}
        manifest=export_filtered_facts(self.db,out,'player_attribute_snapshots',**kw);data=(out/'facts.jsonl').read_bytes();rows=[json.loads(line) for line in data.splitlines()]
        self.assertEqual(manifest['rows'],4);self.assertEqual(manifest['sha256'],hashlib.sha256(data).hexdigest());self.assertEqual(rows,query_facts(self.db,'player_attribute_snapshots',**kw)['records'])
        self.assertEqual({c['name'] for c in manifest['field_metadata']['columns']},{'player_id','shot_close_raw'});self.assertTrue((out/'manifest.json').is_file());self.assertFalse((out/'manifest.pending.json').exists())
        with self.assertRaises(FileExistsError):export_filtered_facts(self.db,out,'players')
        self.assertEqual((out/'facts.jsonl').read_bytes(),data)
    def test_over_cap_export_refuses_before_creating_directory(self):
        out=Path(self.tmp.name)/'over'
        with self.assertRaisesRegex(ValueError,'no silent truncation'):export_filtered_facts(self.db,out,'player_attribute_snapshots',max_rows=1)
        self.assertFalse(out.exists())
        with self.assertRaises(ValueError):export_filtered_facts(self.db,out,'players',max_rows=True)
    def test_interrupted_export_has_no_complete_manifest(self):
        out=Path(self.tmp.name)/'partial'
        with patch('fact_queries._record',side_effect=[{'controlled_fixture':True},RuntimeError('controlled failure')]):
            with self.assertRaisesRegex(RuntimeError,'controlled'):export_filtered_facts(self.db,out,'player_attribute_snapshots')
        self.assertTrue((out/'facts.pending.jsonl').is_file());self.assertFalse((out/'manifest.json').exists());self.assertEqual(json.loads((out/'failure.json').read_bytes())['status'],'INCOMPLETE_EXPORT')
    def test_historical_query_and_export_filter_before_count(self):
        result=query_at(self.db,T0,'query_facts','player_attribute_snapshots')['result'];self.assertEqual(len(result['records']),4)
        out=Path(self.tmp.name)/'historical'
        with observed_as_of(self.db,T0):manifest=export_filtered_facts(self.db,out,'player_attribute_snapshots',max_rows=4)
        self.assertEqual(manifest['rows'],4);self.assertTrue(all(r['provenance']['unit_id']=='old' for r in map(json.loads,(out/'facts.jsonl').read_text(encoding='utf-8').splitlines())))
    def test_public_field_catalog_matches_types_and_visibility(self):
        for table,spec in TABLES.items():
            if spec.public:
                result=fact_fields(table);self.assertTrue(all(c['visibility']=='GM_PUBLIC' for c in result['columns']));self.assertEqual({c['name'] for c in result['columns']},{c.name for c in spec.columns if c.visibility=='GM_PUBLIC'})
    def test_queries_and_exports_preserve_database_bytes(self):
        before=hashlib.sha256(self.db.read_bytes()).hexdigest();query_facts(self.db,'players');export_filtered_facts(self.db,Path(self.tmp.name)/'unchanged','player_attribute_snapshots');self.assertEqual(hashlib.sha256(self.db.read_bytes()).hexdigest(),before)
    def test_cli_fields_filters_cutoff_and_export(self):
        args=[sys.executable,str(BASE/'cli.py')];result=subprocess.run(args+['fact-fields','player_attribute_snapshots'],capture_output=True,text=True,check=True);self.assertEqual(json.loads(result.stdout)['key'],'snapshot_id')
        filters=json.dumps([{'column':'shot_close_raw','op':'gte','value':70}]);result=subprocess.run(args+['query-facts',str(self.db),'player_attribute_snapshots','--filters-json',filters,'--as-of',T0],capture_output=True,text=True,check=True);self.assertEqual(len(json.loads(result.stdout)['result']['records']),2)
        result=subprocess.run(args+['export-filtered',str(self.db),'player_attribute_snapshots',str(Path(self.tmp.name)/'cli'),'--columns-json','["player_id"]','--as-of',T0,'--max-rows','4'],capture_output=True,text=True,check=True);self.assertEqual(json.loads(result.stdout)['result']['rows'],4)

if __name__=='__main__':unittest.main()
