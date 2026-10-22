"""Additive M4 issue/event component of the existing derived workbench."""
import base64
from copy import deepcopy
import json
from uuid import uuid4

from gm_core import development_feedback as feedback
from gm_core.workbench_common import now


class DevelopmentStore:
    def ensure_development(self):
        table = self.c.execute("SELECT 1 FROM sqlite_master WHERE name='workbench_component_versions'").fetchone()
        version = self.c.execute("SELECT version FROM workbench_component_versions WHERE component='M4'").fetchone() if table else None
        if version == (1,):
            return
        if version:
            raise ValueError('UNSUPPORTED_M4_VERSION')
        if self.readonly:
            raise ValueError('M4_NOT_INITIALIZED_INGEST_FIRST')
        with self.c:
            self.c.execute('CREATE TABLE IF NOT EXISTS workbench_component_versions(component TEXT PRIMARY KEY, version INTEGER NOT NULL)')
            self.c.execute('''CREATE TABLE IF NOT EXISTS development_issues(
                issue_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL UNIQUE, revision INTEGER NOT NULL,
                category TEXT NOT NULL, severity TEXT NOT NULL, status TEXT NOT NULL,
                first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, occurrences INTEGER NOT NULL,
                career_id TEXT, capability TEXT NOT NULL, issue_json TEXT NOT NULL)''')
            self.c.execute('''CREATE TABLE IF NOT EXISTS development_issue_events(
                event_key TEXT PRIMARY KEY, issue_id TEXT NOT NULL REFERENCES development_issues(issue_id),
                kind TEXT NOT NULL, revision INTEGER NOT NULL, occurred_at TEXT NOT NULL,
                recorded_at TEXT NOT NULL, payload_json TEXT NOT NULL, UNIQUE(issue_id,revision))''')
            self.c.execute("INSERT INTO workbench_component_versions VALUES('M4',1)")

    def development_issue(self, issue_id):
        self.ensure_development()
        row = self.c.execute('SELECT issue_json FROM development_issues WHERE issue_id=?', (issue_id,)).fetchone()
        if not row:
            raise ValueError('DEVELOPMENT_ISSUE_NOT_FOUND')
        return json.loads(row[0])

    def _save_development_issue(self, issue):
        self.c.execute('''INSERT INTO development_issues VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(issue_id) DO UPDATE SET revision=excluded.revision,
            severity=excluded.severity,status=excluded.status,first_seen=excluded.first_seen,
            last_seen=excluded.last_seen,occurrences=excluded.occurrences,issue_json=excluded.issue_json''',
            (issue['issue_id'], issue['fingerprint'], issue['revision'], issue['category'], issue['severity'],
             issue['status'], issue['first_seen'], issue['last_seen'], issue['occurrences'],
             issue['scope'].get('career_id'), issue['affected_capability'], feedback.encoded(issue)))

    def ingest_development(self, payload):
        obj = feedback.event(payload)
        self.ensure_development()
        with self.c:
            self.c.execute('BEGIN IMMEDIATE')
            old = self.c.execute('SELECT issue_id,payload_json FROM development_issue_events WHERE event_key=?', (obj['event_key'],)).fetchone()
            if old:
                if json.loads(old[1]) != obj:
                    raise ValueError('EVENT_ID_REUSE_WITH_DIFFERENT_CONTENT')
                return dict(result='IDEMPOTENT_REPLAY', issue=feedback.brief(self.development_issue(old[0])))
            row = self.c.execute('SELECT issue_json FROM development_issues WHERE fingerprint=?', (obj['fingerprint'],)).fetchone()
            if row:
                issue = json.loads(row[0])
                issue['revision'] += 1
                issue['occurrences'] += 1
                issue['first_seen'] = min(issue['first_seen'], obj['occurred_at'])
                issue['last_seen'] = max(issue['last_seen'], obj['occurred_at'])
                # Imports never reopen/resolve/defer a player's existing decision.
                issue['latest_source'] = deepcopy(obj['source'])
                issue['latest_evidence_refs'] = obj['evidence_refs']
                issue['latest_confidence'] = obj['confidence']
                issue['finding_kind'] = obj['finding_kind']
            else:
                issue = {k:deepcopy(v) for k,v in obj.items() if k not in ('event_key', 'event_id', 'occurred_at', 'source')}
                issue.update(revision=1, first_seen=obj['occurred_at'], last_seen=obj['occurred_at'], occurrences=1,
                    first_source=deepcopy(obj['source']), latest_source=deepcopy(obj['source']),
                    latest_evidence_refs=obj['evidence_refs'], latest_confidence=obj['confidence'])
            self._save_development_issue(issue)
            self.c.execute('INSERT INTO development_issue_events VALUES(?,?,?,?,?,?,?)',
                (obj['event_key'], issue['issue_id'], 'OBSERVATION', issue['revision'], obj['occurred_at'], now(), feedback.encoded(obj)))
        return dict(result='RECORDED', issue=feedback.brief(issue))

    def triage_development(self, issue_id, payload, expected_revision):
        change = feedback.triage(payload)
        if type(expected_revision) is not int or expected_revision < 1:
            raise ValueError('EXPECTED_REVISION_REQUIRED')
        self.ensure_development()
        with self.c:
            self.c.execute('BEGIN IMMEDIATE')
            issue = self.development_issue(issue_id)
            if issue['revision'] != expected_revision:
                raise ValueError('DEVELOPMENT_REVISION_CONFLICT')
            before = issue['status']
            for key in ('status', 'severity', 'proposed_owner', 'next_review_trigger', 'player_decision_ref'):
                if key in change:
                    issue[key] = change[key]
            issue['revision'] += 1
            issue['latest_triage'] = deepcopy(change)
            self._save_development_issue(issue)
            record = dict(**change, previous_status=before, new_status=issue['status'],
                authority='OPERATOR_REFERENCE_TO_PLAYER_DECISION_ONLY_NO_GAME_OR_PROJECT_APPROVAL')
            stamp = now()
            self.c.execute('INSERT INTO development_issue_events VALUES(?,?,?,?,?,?,?)',
                ('triage:'+uuid4().hex, issue_id, 'TRIAGE', issue['revision'], stamp, stamp, feedback.encoded(record)))
        return dict(result='TRIAGED', issue=feedback.brief(issue), execution_authorized=False)

    def _development_page(self, sql, params, binding, limit, cursor, project):
        if type(limit) is not int or not 1 <= limit <= 50:
            raise ValueError('LIMIT_1_TO_50')
        watermark = self.c.execute('SELECT COALESCE(MAX(rowid),0) FROM development_issue_events').fetchone()[0]
        signature = feedback.fingerprint([binding, watermark])
        offset = 0
        if cursor:
            try:
                token = json.loads(base64.urlsafe_b64decode(cursor))
                offset = token['offset']
                if token['query'] != signature or type(offset) is not int or offset < 0:
                    raise ValueError()
            except Exception as exc:
                raise ValueError('STALE_OR_MIXED_CURSOR') from exc
        # SQL fetch and presentation are both bounded, rather than loading the whole pool.
        records = self.c.execute(sql+' LIMIT ? OFFSET ?', (*params, limit+1, offset)).fetchall()
        rows = []
        for row in records[:limit]:
            obj = project(row)
            if len(feedback.encoded(rows+[obj]).encode()) > 17000:
                if not rows:
                    raise ValueError('ROW_EXCEEDS_BUDGET_REQUEST_EVENT_DETAIL')
                break
            rows.append(obj)
        more = len(records) > len(rows)
        next_cursor = base64.urlsafe_b64encode(feedback.encoded(dict(query=signature, offset=offset+len(rows))).encode()).decode() if more else None
        return dict(rows=rows, row_count=len(rows), next_cursor=next_cursor, truncated=more,
            evidence_watermark=watermark, execution_authorized=False)

    def list_development(self, filters=None, limit=20, cursor=None):
        self.ensure_development()
        filters = filters or {}
        if set(filters) - {'status', 'severity', 'category', 'career_id', 'capability'}:
            raise ValueError('UNKNOWN_ISSUE_FILTER')
        clauses = []; params = []
        for key, value in sorted(filters.items()):
            if key == 'status' and value not in feedback.STATUSES:
                raise ValueError('INVALID_DEVELOPMENT_STATUS')
            if key == 'severity' and value not in ('P0', 'P1', 'P2'):
                raise ValueError('INVALID_SEVERITY')
            if key == 'category' and value not in feedback.CATEGORIES:
                raise ValueError('INVALID_CATEGORY')
            clauses.append(key+'=?'); params.append(value)
        sql = 'SELECT issue_json FROM development_issues'+(' WHERE '+' AND '.join(clauses) if clauses else '')
        return self._development_page(sql+' ORDER BY severity,first_seen,issue_id', params, ['issues', filters], limit, cursor,
            lambda row: feedback.brief(json.loads(row[0])))

    def development_history(self, issue_id, limit=20, cursor=None):
        self.development_issue(issue_id)
        def projection(row):
            obj = json.loads(row[5])
            return dict(event_key=row[0], kind=row[1], revision=row[2], occurred_at=row[3], recorded_at=row[4],
                source=obj.get('source'), confidence=obj.get('confidence'), evidence_refs=obj.get('evidence_refs', []),
                status_change=obj.get('new_status'), player_decision_ref=obj.get('player_decision_ref'))
        return self._development_page('''SELECT event_key,kind,revision,occurred_at,recorded_at,payload_json
            FROM development_issue_events WHERE issue_id=? ORDER BY revision DESC''', [issue_id], ['history', issue_id], limit, cursor, projection)

    def development_event(self, issue_id, event_key):
        self.development_issue(issue_id)
        row = self.c.execute('SELECT payload_json FROM development_issue_events WHERE issue_id=? AND event_key=?', (issue_id, event_key)).fetchone()
        if not row:
            raise ValueError('DEVELOPMENT_EVENT_NOT_FOUND')
        return json.loads(row[0])

    def development_counts(self):
        self.ensure_development()
        return [dict(status=s, severity=p, count=n) for s,p,n in self.c.execute(
            'SELECT status,severity,COUNT(*) FROM development_issues GROUP BY status,severity ORDER BY status,severity')]

    def development_issue6(self):
        self.ensure_development()
        row = self.c.execute("SELECT issue_json FROM development_issues WHERE json_extract(issue_json,'$.root_cause_key')=?",
            ('DEV14_REGISTRY_WORLD_POTENTIAL_ALIAS',)).fetchone()
        return json.loads(row[0]) if row else None
