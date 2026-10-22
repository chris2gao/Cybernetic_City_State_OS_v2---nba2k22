"""Match already loaded team-named books; no cloning or GM hiring decisions."""
import unicodedata
from .common import digest


def normalized(name):
    return ''.join(c for c in unicodedata.normalize('NFKC', name or '').casefold() if c.isalnum())


def identity(book):
    return {k:book[k] for k in ('index','enum_id','unique_id','name')}


def team_book(team, books):
    aliases = {normalized(team.get(k)) for k in ('name','abbreviation')}
    aliases.add(normalized((team.get('city') or '')+(team.get('name') or '')))
    aliases.discard('')
    matches = []
    for book in books:
        labels = {normalized(book.get('name'))}
        parts = unicodedata.normalize('NFKC', book.get('name') or '').rsplit(None, 1)
        if len(parts) == 2 and parts[1].casefold() == 'playbook':
            labels.add(normalized(parts[0]))
        if aliases & labels:
            matches.append(book)
    if len(matches) != 1:
        raise ValueError('TEAM_NAMED_BOOK_MISSING_OR_AMBIGUOUS')
    return identity(matches[0])


def validate_rebind(proposal, source, obj, value):
    event = proposal.get('event')
    if (proposal.get('operation') != 'TEAM_BOOK_REBIND' or not isinstance(event, dict)
        or set(event) != {'kind','reference','team_id','current_coach_identity'}
        or event['kind'] not in ('INITIAL_SAVE','CONFIRMED_COACH_CHANGE')
        or not isinstance(event['reference'],str) or not event['reference'].strip()
        or event['team_id'] != obj['selector'].get('team_id')
        or event['current_coach_identity'] != obj['identity']):
        raise PermissionError('TEAM_BOOK_REBIND_EVENT_AND_CURRENT_COACH_REQUIRED')
    directory = source.get('team_directory',{})
    team = directory.get(str(event['team_id']))
    if team is None:
        raise ValueError('TEAM_NAMED_BOOK_SOURCE_UNAVAILABLE')
    book = team_book(team, (source.get('source_context') or {}).get('playbooks',[]))
    if value != book['enum_id']:
        raise PermissionError('TEAM_BOOK_REBIND_MUST_TARGET_OWN_TEAM_NAMED_BOOK')
    return book


def validate_slot(source, obj):
    selector = obj['selector']
    tid = selector.get('team_id')
    if type(tid) is not int or selector.get('owner_team_ids') != [tid]:
        raise PermissionError('TEAM_BOOK_OBJECT_NOT_BOUND_TO_SINGLE_TEAM')
    team = source.get('team_directory',{}).get(str(tid))
    if team is None:
        raise ValueError('TEAM_NAMED_BOOK_SOURCE_UNAVAILABLE')
    book = team_book(team, (source.get('source_context') or {}).get('playbooks',[]))
    if selector['playbook_identity'] != digest(book):
        raise PermissionError('ONLY_OWN_TEAM_NAMED_BOOK_SLOTS_ALLOWED')
