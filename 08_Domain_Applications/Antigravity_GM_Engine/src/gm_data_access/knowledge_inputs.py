"""Sealed snapshot adapter; core receives plain dictionaries, never a DB handle."""
from pathlib import Path
from .query import QuerySession
from .finance_inputs import all_rows
from . import AccessError
from gm_core.knowledge import read_json


def load_context(query_root, published_root, profile_path, career, batch=None, allow_local=False):
    session = QuerySession(query_root, published_root, career, batch)
    try:
        binding = session.binding.copy()
        if binding['publication_status'] == 'LOCAL_AUDITED_NOT_PUBLISHED' and not allow_local:
            raise AccessError('LOCAL_AUDITED_NOT_PUBLISHED', 'Use --allow-local-audited for development')
        path = Path(published_root)/'saves'/binding['career_id']/'batches'/binding['batch_id']/'coaching/field_dictionary.json'
        available = bool(session.available['coaching']) and path.is_file()
        return dict(source_binding=binding, teams=all_rows(session, 'teams', ['team_id', 'team']),
                    available=available, dictionary=read_json(path) if available else None,
                    profile=read_json(profile_path))
    finally:
        session.close()
