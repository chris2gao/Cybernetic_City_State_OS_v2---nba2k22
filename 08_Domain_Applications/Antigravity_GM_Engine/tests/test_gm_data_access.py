"""Synthetic M0 isolation/security/identity tests; no game or production writes."""
import base64
import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from data_sync_metadata import stamp_database
from snapshot_integrity import snapshot_digest
from gm_data_access import AccessError
from gm_data_access.snapshots import install_archive,load_snapshot,validate_pair,ro
from gm_data_access.query import QuerySession


def fixture(root, team_stats=False, team_count=2, native_source=None, potential_mask=None, sid='SYNTHETIC_S1', batch='SYNTHETIC_BATCH'):
    source=root/'source'
    source.mkdir()
    context=dict(career_id='synthetic',game_date='2021-12-12',purpose='validation',synthetic=True,trigger='PLAYER_INITIATED')
    c=sqlite3.connect(source/'league_state.sqlite')
    c.executescript((ROOT/'database/schema.sql').read_text(encoding='utf-8-sig'))
    note='CAPTURE_CONTEXT_V1:'+base64.b64encode(json.dumps(context).encode()).decode()
    c.execute('INSERT INTO monthly_snapshots(snapshot_id,season_year,month_index,month_name,snapshot_date,notes) VALUES (?,?,?,?,?,?)',(sid,2022,2,'SYNTHETIC','2021-12-12',note))
    c.execute('INSERT INTO monthly_snapshots(snapshot_id,season_year,month_index,month_name,snapshot_date,notes) VALUES (?,?,?,?,?,?)',('OLD',2022,1,'OLD','2021-11-12',note))
    for t in range(team_count):
        c.execute('INSERT INTO team_monthly_stats(snapshot_id,team_id,team_abbr,total_salary,payroll,budget,staff_budget,cash) VALUES (?,?,?,?,?,?,?,?)',(sid,t,'T'+str(t),1000,30,1200,200,4294967290 if t else 5))
        c.execute('INSERT INTO team_monthly_stats(snapshot_id,team_id,team_abbr,total_salary) VALUES (?,?,?,?)',('OLD',t,'T'+str(t),99999))
        for n in range(3):
            d=dict(contract={'contract_year_1':dict(value=100+n),'years_left_on_contract':dict(value=1)},attributes={'speed':dict(raw=150,value=70)},season_totals=dict(points=20,minutes=10))
            if potential_mask:
                d['attributes'].update(potential=dict(raw=1,value=1),intangibles=dict(raw=90,value=55))
                d['season_totals']['times']=2
            blob=bytes(0x4f0) if potential_mask else bytes(0x80)
            c.execute('INSERT INTO player_source_details VALUES (?,?,?,?,?,?,?,?,?,?)',(sid,t,n,t*3+n,'Same Name' if n==0 else 'Player'+str(t*3+n),10+n,None,None,json.dumps(d),blob))
        detail=dict(fields=dict(vitals=dict(position=dict(label='HEAD_COACH'),salary=dict(value=10),years_left=dict(value=2)),attributes={}))
        c.execute('INSERT INTO staff_pool_observations VALUES (?,?,?,?,?,?,?,?)',(sid,t,'Coach',str(t),None,'VERIFIED_RECIPROCAL_TEAM_ROLE',bytes(8),None))
        c.execute('INSERT INTO staff_source_details VALUES (?,?,?,?,?,?,?)',(sid,t,t,'HEAD_COACH','VERIFIED_RECIPROCAL_TEAM_ROLE',json.dumps(detail),bytes(8)))
        values={name:1 for name in ('PreferredSystem','ActiveSystem','BenchDepth','BenchUtilization','RunPlayTendency','ZoneUsage','Tempo','HelpDefense','FreelanceType','FreelanceType2','FreelanceType3','FreelanceType4','POEOffense','POEOffense2','POEOffense3','POEDefense','POEDefense2','POEDefense3','PlaybookID','SimPace')}
        coach=dict(coach_identity=dict(first_name='Coach',last_name=str(t)),values=values,readiness={},gameplans=[dict(opponent_team_id=1-t,overall_defense=dict(values={'PressureOnball':None},mixed_fields=['PressureOnball'],status='VERIFIED_GROUP'))])
        c.execute('INSERT INTO coaching_team_observations VALUES (?,?,?)',(sid,t,json.dumps(coach)))
    candidate_slot=max(3,team_count)
    c.execute('INSERT INTO staff_pool_observations VALUES (?,?,?,?,?,?,?,?)',(sid,candidate_slot,'Candidate','Coach',None,'UNASSIGNED',bytes(8),None))
    c.execute('INSERT INTO staff_source_details VALUES (?,?,?,?,?,?,?)',(sid,candidate_slot,None,None,'UNASSIGNED',json.dumps(detail),bytes(8)))
    for n,year in enumerate((2022,2023,2024,2025)):
        c.execute('INSERT INTO draft_asset_observations VALUES (?,?,?,?,?,?,?,?,?)',(sid,n,0,0,year,1,None,'VERIFIED_SIMPLE_FUTURE_PICK',bytes(32)))
    if native_source:
        from gm_state_io.capture_bridge import store
        store(c,native_source)
    stamp_database(c,sid,'synthetic','2026-10-18T00:00:00+00:00')
    if team_stats:
        for t in range(team_count):
            c.execute('INSERT INTO team_source_stats VALUES(?,?,?,?,?)',(sid,t,t,json.dumps(dict(season_year=2022,w=2,l=1,made=30,attempted=60)),bytes(8)))
            c.execute('INSERT INTO team_source_stats VALUES(?,?,?,?,?)',('OLD',t,t,json.dumps(dict(season_year=2021,w=99)),bytes(8)))
    digest=snapshot_digest(c,sid)
    c.commit()
    c.close()
    p=sqlite3.connect(source/'player_pool.sqlite')
    p.execute('CREATE TABLE player_pool(slot_id PRIMARY KEY,full_name,position_name,draft_year,draft_round,draft_pick,cyberface_id,raw_struct,source_details_json)')
    if potential_mask:
        p.execute('ALTER TABLE player_pool ADD COLUMN potential')
        p.execute('ALTER TABLE player_pool ADD COLUMN raw_potential')
    pool_count=max(60,team_count*3)
    for n in range(pool_count):
        blob=bytearray(0x4f0 if potential_mask else 0x80)
        if n==59: blob[0x70]=0xe0
        details=dict(attributes={'potential':dict(raw=1,value=1)} if potential_mask else {})
        p.execute('INSERT INTO player_pool(slot_id,full_name,position_name,draft_year,draft_round,draft_pick,cyberface_id,raw_struct,source_details_json) VALUES (?,?,?,?,?,?,?,?,?)',(n,'Michael Jordan' if n>=58 else 'Player'+str(n),'PG',1984 if n>=58 else 2021,1,1,1,bytes(blob),json.dumps(details)))
    stamp_database(p,sid,'synthetic','2026-10-18T00:00:00+00:00')
    p.commit()
    p.close()
    if potential_mask:
        from player_potential_mask import sanitize_player_potential
        league=sqlite3.connect(source/'league_state.sqlite');pool=sqlite3.connect(source/'player_pool.sqlite')
        try:
            potential_mask=sanitize_player_potential(league,pool,sid)
            digest=snapshot_digest(league,sid)
            league.commit();pool.commit()
        finally:
            league.close();pool.close()
    ingest=dict(snapshot_id=sid,save_id='synthetic',data_updated_at='2026-10-18T00:00:00+00:00',batch_binding=dict(snapshot_digest_sha256=digest,player_pool_sha256='SYNTHETIC_POOL'),quality_metrics=dict(simple_draft_assets=dict(next_draft_year=2022),coaching_tactics=dict(profile=1)))
    audit=dict(snapshot_id=sid,save_id='synthetic',verdict='PASS_VERIFIED',checks=dict(synthetic_only=True),database_digest_sha256=digest,player_pool_sha256='SYNTHETIC_POOL',player_pool_records=pool_count,manifest_binding=dict(manifest_sha256='SYNTHETIC_SOURCE'))
    manifest=dict(batch_id=batch,snapshot_id=sid,save_id='synthetic',data_updated_at=ingest['data_updated_at'],context=context,audit_verdict='PASS_VERIFIED',gm_decisions_allowed=False,source_binding=dict(snapshot_digest_sha256=digest,ingest_manifest_sha256='SYNTHETIC_SOURCE',player_pool_sha256='SYNTHETIC_POOL'))
    if potential_mask:
        manifest['player_potential_mask']=potential_mask
    archive=root/'synthetic.zip'
    with zipfile.ZipFile(archive,'w') as z:
        for n in ('league_state.sqlite','player_pool.sqlite'):
            z.write(source/n,n)
        for name,data in [('audit.json',audit),('ingest_manifest.json',ingest),('context.json',context),('data_update.json',dict(snapshot_id=sid,save_id='synthetic',data_updated_at=ingest['data_updated_at'],game_date=context['game_date']))]:
            z.writestr(name,json.dumps(data))
    published=root/'published'
    (published/'saves/synthetic').mkdir(parents=True)
    latest=dict(save_id='synthetic',batch_id=batch,data_updated_at=ingest['data_updated_at'],game_date=context['game_date'],upload_status='UPLOADED',uploaded_at='2026-10-18T00:01:00+00:00')
    (published/'saves/synthetic/latest.json').write_text(json.dumps(latest))
    queryroot=root/'query_snapshots'
    install_archive(archive,manifest,queryroot)
    return queryroot,published,archive,manifest


class QueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.tmp.name)
        cls.qroot,cls.published,cls.archive,cls.manifest=fixture(cls.root)

    @classmethod
    def tearDownClass(cls):
        # Windows read-only files require owner removal of the test-only attribute.
        for p in cls.root.rglob('*'):
            if p.is_file(): p.chmod(0o600)
        cls.tmp.cleanup()

    def setUp(self):
        self.s=QuerySession(self.qroot,self.published,'synthetic')
    def tearDown(self):
        self.s.close()

    def test_same_batch_only(self):
        r=self.s.query('teams',fields=['total_salary'],limit=50)
        self.assertEqual([x['total_salary'] for x in r['rows']],[1000,1000])
        self.assertFalse(r['source_binding']['production_gm_eligible'])

    def test_default_projection_and_limit(self):
        r=self.s.query('pool')
        self.assertEqual(r['row_count'],20)
        self.assertIsNotNone(r['next_cursor'])
        self.assertNotIn('attributes',r['rows'][0])
        self.assertNotIn('raw_struct',json.dumps(r))

    def test_cursor_pages_no_duplicates(self):
        first=self.s.query('pool',limit=13)
        second=self.s.query('pool',limit=13,cursor=first['next_cursor'])
        self.assertFalse({r['identity'] for r in first['rows']} & {r['identity'] for r in second['rows']})
        with self.assertRaises(AccessError):self.s.query('pool',limit=14,cursor=first['next_cursor'])

    def test_limit_and_cursor_guards(self):
        for limit in (0,51,True,-1):
            with self.assertRaises(AccessError):self.s.query('pool',limit=limit)
        with self.assertRaises(AccessError):self.s.query('pool',cursor='not-a-cursor')

    def test_same_names_not_one_identity(self):
        r=self.s.query('players',filters={'name':'Same Name'})
        self.assertEqual(r['row_count'],2)
        self.assertEqual(r['ambiguity'],'MULTIPLE_CANDIDATES')
        self.assertNotEqual(r['rows'][0]['identity'],r['rows'][1]['identity'])

    def test_name_injection_literal(self):
        self.assertEqual(self.s.query('players',filters={'name':"' OR 1=1 --"})['row_count'],0)

    def test_unverified_fields_rejected(self):
        for field in ('raw_struct','memory_addr','overall_rating','poe_on_ball'):
            with self.assertRaisesRegex(AccessError,'Field is unavailable'):
                self.s.query('players',fields=[field])

    def test_staff_candidates_not_employed(self):
        r=self.s.query('staff',filters={'role':None,'candidate_position':'HEAD_COACH'})
        self.assertEqual(r['row_count'],1)
        self.assertIsNone(r['rows'][0]['team'])

    def test_historical_model_and_unrostered_not_free_agent(self):
        r=self.s.query('pool',filters={'name':'Michael Jordan','draft_year':1984,'historical_rookie':1})
        self.assertEqual(r['row_count'],1)
        self.assertEqual(r['rows'][0]['roster_status'],'NOT_ON_OBSERVED_NBA_ROSTER')

    def test_coaching_19_and_mixed_group(self):
        row=self.s.query('coaching',fields=['values'],filters={'team_id':0})['rows'][0]
        self.assertEqual(len(row['values']),19)
        self.assertNotIn('SimPace',row['values'])
        defense=self.s.query('defense',filters={'team_id':0,'opponent_team_id':1})['rows'][0]
        self.assertIsNone(defense['values']['PressureOnball'])
        self.assertEqual(defense['mixed_fields'],['PressureOnball'])

    def test_picks_three_drafts(self):
        r=self.s.query('picks',filters={'trade_eligible':1})
        self.assertEqual([x['draft_year'] for x in r['rows']],[2022,2023,2024])

    def test_cash_preserved_hypothesis_separate(self):
        row=self.s.query('finance',filters={'team_id':1})['rows'][0]
        self.assertEqual(row['cash'],4294967290)
        self.assertEqual(row['cash_signed32_hypothesis'],-6)
        self.assertEqual(row['financial_eligibility'],'UNKNOWN')

    def test_sql_aggregate(self):
        r=self.s.query('sql',sql='SELECT team,COUNT(*) AS players,SUM(salary) AS total FROM q_players GROUP BY team ORDER BY team')
        self.assertEqual(r['row_count'],2)
        self.assertEqual(r['rows'][0]['players'],3)
        self.assertEqual(r['rows'][0]['total'],303)

    def test_sql_attack_surface(self):
        for sql in ("UPDATE q_teams SET team='X'",'PRAGMA writable_schema=ON',"ATTACH 'x' AS other",'SELECT * FROM q_pool',
                    'SELECT name FROM q_pool; DELETE FROM q_pool',"SELECT load_extension('x')",'SELECT raw_struct FROM facts.player_source_details',
                    'SELECT COUNT(*) FROM facts.player_source_details','SELECT COUNT(*) FROM facts."player_source_details"',
                    'SELECT COUNT(*) FROM /*AS*/ player_pool', 'SELECT COUNT(*) FROM /* AS */ facts.player_pool',
                    'SELECT (WITH q_teams AS (SELECT raw_struct FROM facts.player_source_details) SELECT raw_struct FROM q_teams)',
                    'SELECT group_concat(name) FROM q_pool','SELECT randomblob(1000000000)',"SELECT name FROM sqlite_master"):
            with self.subTest(sql=sql):
                with self.assertRaises(AccessError):self.s.query('sql',sql=sql)

    def test_output_byte_budget(self):
        r=self.s.query('sql',sql="SELECT '"+'z'*14000+"' AS name FROM q_pool ORDER BY slot_id",limit=50)
        self.assertLessEqual(len(json.dumps(r).encode()),20000)
        self.assertTrue(r['truncated'])
        self.assertLess(r['row_count'],50)

    def test_write_to_connections_rejected(self):
        with self.assertRaises(sqlite3.DatabaseError):self.s.c.execute('CREATE TABLE malicious(x)')
        with self.assertRaises(sqlite3.DatabaseError):self.s.c.execute('ATTACH DATABASE ? AS evil',(':memory:',))
        c=ro(self.s.directory/'league_state.sqlite')
        try:
            with self.assertRaises(sqlite3.OperationalError):c.execute('DELETE FROM team_monthly_stats')
        finally:c.close()

    def test_snapshot_immutable_reinstall(self):
        self.assertEqual(install_archive(self.archive,self.manifest,self.qroot)['source_manifest'],self.manifest)
        changed=copy.deepcopy(self.manifest)
        changed['data_updated_at']='changed'
        with self.assertRaises(AccessError):install_archive(self.archive,changed,self.qroot)

    def test_two_database_binding_and_audit(self):
        directory=self.s.directory
        audit=json.loads((directory/'audit.json').read_text())
        ingest=json.loads((directory/'ingest_manifest.json').read_text())
        bad=copy.deepcopy(audit);bad['verdict']='FAIL'
        with self.assertRaises(AccessError):validate_pair(directory,self.manifest,bad,ingest)
        bad=copy.deepcopy(self.manifest);bad['snapshot_id']='OTHER'
        with self.assertRaises(AccessError):validate_pair(directory,bad,audit,ingest)

    def test_missing_and_traversal(self):
        for career,batch in (('synthetic','MISSING'),('../saves','SYNTHETIC_BATCH')):
            with self.assertRaises(AccessError):QuerySession(self.qroot,self.published,career,batch)

    def test_unpublished_and_historical_no_silent_fallback(self):
        pointer=self.published/'saves/synthetic/latest.json'
        original=pointer.read_text()
        try:
            latest=json.loads(original)
            latest.update(upload_status='PENDING_UPLOAD',uploaded_at=None)
            pointer.write_text(json.dumps(latest))
            s=QuerySession(self.qroot,self.published,'synthetic')
            try:
                self.assertEqual(s.binding['publication_status'],'LOCAL_AUDITED_NOT_PUBLISHED')
                self.assertFalse(s.binding['production_gm_eligible'])
            finally:s.close()
            latest.update(batch_id='NEW_BATCH_NOT_INSTALLED',data_updated_at='2026-10-19T00:00:00+00:00')
            pointer.write_text(json.dumps(latest))
            with self.assertRaises(AccessError):QuerySession(self.qroot,self.published,'synthetic')
            s=QuerySession(self.qroot,self.published,'synthetic','SYNTHETIC_BATCH')
            try:
                self.assertEqual(s.binding['publication_status'],'HISTORICAL_EXPLICIT_BATCH')
                self.assertFalse(s.binding['production_gm_eligible'])
            finally:s.close()
        finally:pointer.write_text(original)

    def test_missing_pair_fails_closed(self):
        self.s.close()
        pool=self.s.directory/'player_pool.sqlite'
        moved=pool.with_suffix('.held')
        pool.rename(moved)
        try:
            with self.assertRaises((AccessError,OSError)):load_snapshot(self.qroot,'synthetic','SYNTHETIC_BATCH')
        finally:moved.rename(pool)

    def test_wrong_pool_audit_binding(self):
        audit=json.loads((self.s.directory/'audit.json').read_text())
        ingest=json.loads((self.s.directory/'ingest_manifest.json').read_text())
        audit['player_pool_sha256']='WRONG'
        with self.assertRaises(AccessError):validate_pair(self.s.directory,self.manifest,audit,ingest)

    def test_tampered_snapshot_detected(self):
        p=self.s.directory/'player_pool.sqlite'
        original=p.read_bytes()
        try:
            p.chmod(0o600)
            p.write_bytes(original+b'TAMPER')
            with self.assertRaises(AccessError):load_snapshot(self.qroot,'synthetic','SYNTHETIC_BATCH')
        finally:
            p.write_bytes(original)
            p.chmod(0o444)

    def test_expensive_sql_interrupted(self):
        with self.assertRaises(AccessError) as cm:
            self.s.query('sql',sql='SELECT SUM(a.slot_id+b.slot_id+c.slot_id+d.slot_id+e.slot_id) AS value FROM q_pool a CROSS JOIN q_pool b CROSS JOIN q_pool c CROSS JOIN q_pool d CROSS JOIN q_pool e')
        self.assertEqual(cm.exception.code,'QUERY_TIMEOUT')


if __name__=='__main__':unittest.main()
