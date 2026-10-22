"""Read one sealed M0 batch into plain DTOs; never pass SQLite to gm_core."""
from . import AccessError
from .query import QuerySession


def all_rows(session, entity, fields):
    rows, cursor = [], None
    while True:
        page = session.query(entity, fields=fields, limit=50, cursor=cursor)
        rows.extend(page['rows'])
        if not page['truncated']:
            return rows
        if not page['next_cursor'] or page['next_cursor'] == cursor:
            raise AccessError('RESULT_LIMIT_REACHED', 'Cannot consume the complete input projection')
        cursor = page['next_cursor']


def load_inputs(query_root, published_root, career, batch=None, allow_local=False):
    session = QuerySession(query_root, published_root, career, batch)
    try:
        if session.binding['publication_status'] == 'LOCAL_AUDITED_NOT_PUBLISHED' and not allow_local:
            raise AccessError('LOCAL_AUDITED_NOT_PUBLISHED', 'Use --allow-local-audited for development')
        teams = all_rows(session, 'teams', ['team_id', 'team', 'total_salary'])
        players = all_rows(session, 'players', ['identity', 'name', 'team_id', 'team', 'contract', 'years_left'])
        finance = all_rows(session, 'finance', ['team_id', 'team', 'total_salary', 'payroll', 'budget', 'cash']) if session.available['finance'] else []
        picks = all_rows(session, 'picks', ['asset_id', 'team_id', 'owner', 'original_team_id', 'draft_year', 'draft_round', 'trade_eligible']) if session.available['picks'] else []
        return dict(source_binding=session.binding.copy(), context=session.record['source_manifest'].get('context', {}),
                    teams=teams, players=players, finance=finance, picks=picks,
                    finance_semantics=all_rows(session, 'finance_semantics', ['field', 'encoding', 'unit', 'time_scope', 'financial_eligibility']))
    finally:
        session.close()
