"""Additive M3 component of the shared workbench; no independent database."""
import json
from gm_core.workbench_common import now, same_source


def dump(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True)


class M3Store:
    def ensure_m3(self):
        if self.c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='workbench_component_versions'").fetchone():
            version=self.c.execute("SELECT version FROM workbench_component_versions WHERE component='M3'").fetchone()
            if version == (1,):
                return
            if version:
                raise ValueError('UNSUPPORTED_M3_VERSION')
        if self.readonly:
            if not self.c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='analysis_runs'").fetchone():
                raise ValueError('M3_NOT_INITIALIZED')
            return
        statements = [
            'CREATE TABLE IF NOT EXISTS workbench_component_versions(component TEXT PRIMARY KEY, version INTEGER NOT NULL)',
            "INSERT OR IGNORE INTO workbench_component_versions VALUES('M3',1)",
            '''CREATE TABLE IF NOT EXISTS analysis_runs(run_id TEXT PRIMARY KEY, career_id TEXT NOT NULL,
                batch_id TEXT NOT NULL, revision INTEGER NOT NULL, status TEXT NOT NULL, source_json TEXT NOT NULL,
                previous_source_json TEXT, run_json TEXT NOT NULL, created_at TEXT NOT NULL, sealed_at TEXT)''',
            '''CREATE TABLE IF NOT EXISTS team_features(run_id TEXT REFERENCES analysis_runs(run_id), team_id INTEGER,
                feature_json TEXT NOT NULL, PRIMARY KEY(run_id,team_id))''',
            '''CREATE TABLE IF NOT EXISTS market_candidates(run_id TEXT REFERENCES analysis_runs(run_id), candidate_id TEXT,
                team_id INTEGER, candidate_json TEXT NOT NULL, PRIMARY KEY(run_id,candidate_id))''',
            '''CREATE TABLE IF NOT EXISTS decision_runs(run_id TEXT PRIMARY KEY, career_id TEXT NOT NULL, batch_id TEXT NOT NULL,
                analysis_run_id TEXT REFERENCES analysis_runs(run_id), revision INTEGER NOT NULL, phase TEXT NOT NULL,
                status TEXT NOT NULL, current_final_version INTEGER, run_json TEXT NOT NULL, created_at TEXT NOT NULL)''',
            '''CREATE TABLE IF NOT EXISTS decision_artifacts(run_id TEXT REFERENCES decision_runs(run_id), kind TEXT,
                artifact_id TEXT, revision INTEGER, payload_json TEXT NOT NULL, created_at TEXT NOT NULL,
                PRIMARY KEY(run_id,kind,artifact_id,revision))''']
        with self.c:
            for sql in statements:
                self.c.execute(sql)
            if self.c.execute("SELECT version FROM workbench_component_versions WHERE component='M3'").fetchone() != (1,):
                raise ValueError('UNSUPPORTED_M3_VERSION')

    def load_analysis(self, run_id):
        self.ensure_m3()
        row=self.c.execute('SELECT run_json FROM analysis_runs WHERE run_id=?',(run_id,)).fetchone()
        if not row:
            raise ValueError('ANALYSIS_RUN_NOT_FOUND')
        result=json.loads(row[0])
        result['teams']=[json.loads(r[0]) for r in self.c.execute('SELECT feature_json FROM team_features WHERE run_id=? ORDER BY team_id',(run_id,))]
        return result

    def save_analysis(self, run, expected_revision=0):
        self.ensure_m3()
        b=run['source_binding']
        payload={k:v for k,v in run.items() if k!='teams'}
        with self.c:
            self.c.execute('BEGIN IMMEDIATE')
            old=self.c.execute('SELECT revision,sealed_at FROM analysis_runs WHERE run_id=?',(run['analysis_run_id'],)).fetchone()
            if (old[0] if old else 0)!=expected_revision:
                raise ValueError('ANALYSIS_REVISION_CONFLICT')
            if old and old[1]:
                raise ValueError('SEALED_ANALYSIS_IMMUTABLE')
            payload['revision']=expected_revision+1
            args=(b['career_id'],b['batch_id'],payload['revision'],run['status'],dump(b),dump(run['previous_source_binding']),dump(payload),run['created_at'],run['sealed_at'],run['analysis_run_id'])
            if old:
                self.c.execute('UPDATE analysis_runs SET career_id=?,batch_id=?,revision=?,status=?,source_json=?,previous_source_json=?,run_json=?,created_at=?,sealed_at=? WHERE run_id=?',args)
            else:
                self.c.execute('INSERT INTO analysis_runs(career_id,batch_id,revision,status,source_json,previous_source_json,run_json,created_at,sealed_at,run_id) VALUES(?,?,?,?,?,?,?,?,?,?)',args)
            for t in run['teams']:
                self.c.execute('INSERT OR REPLACE INTO team_features VALUES(?,?,?)',(run['analysis_run_id'],t['team_id'],dump(t)))
        run['revision']=payload['revision']
        return run

    def market(self, run_id):
        self.ensure_m3()
        return [json.loads(r[0]) for r in self.c.execute('SELECT candidate_json FROM market_candidates WHERE run_id=? ORDER BY candidate_id',(run_id,))]

    def analysis_context(self, run_id):
        result=self.load_analysis(run_id)
        result['supplemental_evidence']={}
        for candidate in self.market(run_id):
            ref='market:'+candidate['candidate_id']
            result['supplemental_evidence'][ref]=dict(ref_id=ref,kind='MARKET_QUERY' if candidate['candidate_kind']=='SCREEN_QUERY' else 'MARKET_CANDIDATE',
                binding=result['source_binding'],value=candidate,availability='SUPPLEMENTAL_NOT_BASE_PACKET',run_id=run_id)
        return result

    def save_market(self, run_id, receipt, requesting_team=None):
        self.ensure_m3()
        run=self.load_analysis(run_id)
        if not same_source(receipt['source_binding'],run['source_binding']):
            raise ValueError('MARKET_SOURCE_MISMATCH')
        query=receipt['query']
        with self.c:
            self.c.execute('BEGIN IMMEDIATE')
            for old in self.market(run_id):
                if old['query']['query_id']==query['query_id'] and old['query']!=query:
                    raise ValueError('QUERY_ID_IMMUTABLE_USE_NEW_ID')
            from hashlib import sha256
            receipt_id='query:'+query['query_id']+':'+sha256(dump(receipt['returned_identities']).encode()).hexdigest()[:16]
            record=dict(candidate_id=receipt_id,run_id=run_id,team_id=requesting_team,candidate_kind='SCREEN_QUERY',query=query,query_receipt=receipt)
            self.c.execute('INSERT OR IGNORE INTO market_candidates VALUES(?,?,?,?)',(run_id,receipt_id,requesting_team,dump(record)))
            for row in receipt['rows']:
                candidate_id=query['query_id']+':'+row['identity']
                candidate=dict(candidate_id=candidate_id,run_id=run_id,team_id=requesting_team,
                    source_identity=row['identity'],source_owner=row.get('team_id'),
                    candidate_kind={'roster':'ROSTER_PLAYER','pool':'POOL_MODEL','staff':'STAFF_REFERENCE'}[query['source_domain']],
                    fit_refs=[],cost_refs=[],screen_query_ref='market:'+receipt_id,
                    evaluation_status='READ',availability_status='SCOUTING_ONLY' if query['source_domain']=='pool' else 'NOT_NEGOTIATED',
                    query=query, query_receipt={k:v for k,v in receipt.items() if k!='rows'}, values=row,
                    unknowns=['NO_FREE_AGENCY_OR_TRADE_WILLINGNESS_CERTIFIED'])
                self.c.execute('INSERT OR IGNORE INTO market_candidates VALUES(?,?,?,?)',(run_id,candidate_id,requesting_team,dump(candidate)))

    def load_decision(self, run_id):
        self.ensure_m3()
        row=self.c.execute('SELECT run_json FROM decision_runs WHERE run_id=?',(run_id,)).fetchone()
        if not row:
            raise ValueError('DECISION_RUN_NOT_FOUND')
        result=json.loads(row[0])
        result['artifacts']={}
        if 'context' not in result:
            result['context']=self.load_analysis(result['analysis_run_id'])['context']
        result['coach_events']=self.coach_events(result['source_binding']['career_id'],result['context']['season'])
        for kind,aid,rev,payload in self.c.execute('''SELECT a.kind,a.artifact_id,a.revision,a.payload_json FROM decision_artifacts a
            JOIN (SELECT kind,artifact_id,MAX(revision) revision FROM decision_artifacts WHERE run_id=? GROUP BY kind,artifact_id) n
            ON a.kind=n.kind AND a.artifact_id=n.artifact_id AND a.revision=n.revision WHERE a.run_id=?''',(run_id,run_id)):
            result['artifacts'].setdefault(kind,{})[aid]=dict(revision=rev,payload=json.loads(payload))
        return result

    def coach_events(self,career,season):
        self.ensure_m3()
        return [json.loads(row[0]) for row in self.c.execute('''SELECT a.payload_json FROM decision_artifacts a
            JOIN decision_runs d ON d.run_id=a.run_id WHERE a.kind='COACH_EVENT' AND d.career_id=?
            AND json_extract(a.payload_json,'$.season')=? ORDER BY a.created_at''',(career,season))]

    def artifact_history(self, run_id, kind, artifact_id, revision):
        self.ensure_m3()
        row=self.c.execute('SELECT payload_json FROM decision_artifacts WHERE run_id=? AND kind=? AND artifact_id=? AND revision=?',(run_id,kind,artifact_id,revision)).fetchone()
        if not row:
            raise ValueError('ARTIFACT_NOT_FOUND')
        return json.loads(row[0])

    def save_decision(self, run, expected_revision=0, artifacts=()):
        self.ensure_m3()
        allowed={'TEAM_REVIEW','ALTERNATIVES','OFFER','RESPONSE','PORTFOLIO','VALIDATION','FINAL','STRATEGY_CANDIDATE','HYPOTHESIS','COACH_EVENT','BPTI_BLUEPRINT','BPTI_EVOLUTION'}
        payload={k:v for k,v in run.items() if k!='artifacts'}
        b=run['source_binding']
        with self.c:
            self.c.execute('BEGIN IMMEDIATE')
            old=self.c.execute('SELECT revision FROM decision_runs WHERE run_id=?',(run['decision_run_id'],)).fetchone()
            if (old[0] if old else 0)!=expected_revision:
                raise ValueError('DECISION_REVISION_CONFLICT')
            payload['revision']=expected_revision+1
            args=(b['career_id'],b['batch_id'],run['analysis_run_id'],payload['revision'],run['phase'],run['status'],run.get('current_final_version'),dump(payload),run['created_at'],run['decision_run_id'])
            if old:
                self.c.execute('UPDATE decision_runs SET career_id=?,batch_id=?,analysis_run_id=?,revision=?,phase=?,status=?,current_final_version=?,run_json=?,created_at=? WHERE run_id=?',args)
            else:
                self.c.execute('INSERT INTO decision_runs(career_id,batch_id,analysis_run_id,revision,phase,status,current_final_version,run_json,created_at,run_id) VALUES(?,?,?,?,?,?,?,?,?,?)',args)
            for kind,aid,obj in artifacts:
                if kind not in allowed:
                    raise ValueError('INVALID_ARTIFACT_KIND')
                if kind=='COACH_EVENT' and obj['kind']=='CONFIRMED_COACH_CHANGE':
                    if any(e['kind']=='CONFIRMED_COACH_CHANGE' and e['team_id']==obj['team_id'] for e in self.coach_events(b['career_id'],obj['season'])):
                        raise ValueError('COACH_CHANGE_ONCE_PER_TEAM_SEASON')
                rev=self.c.execute('SELECT COALESCE(MAX(revision),0)+1 FROM decision_artifacts WHERE run_id=? AND kind=? AND artifact_id=?',(run['decision_run_id'],kind,aid)).fetchone()[0]
                self.c.execute('INSERT INTO decision_artifacts VALUES(?,?,?,?,?,?)',(run['decision_run_id'],kind,aid,rev,dump(obj),now()))
        return self.load_decision(run['decision_run_id'])
