"""Shared game-play references. Plain DTOs only; no game, DB or execution access."""
from copy import deepcopy
import json
import re
from typing import TypedDict

VERSION = 'GM_PLAY_POOL_V1'
AUTHORITY = 'REFERENCE_ONLY_NOT_CURRENT_SAVE_NOT_EXECUTION_APPROVAL'


class PlayTypeMembership(TypedDict):
    type_id: int
    evidence_status: str
    evidence_refs: list[str]


class PlayCard(TypedDict):
    play_id: str
    native_crc: int
    names: list[str]
    name_status: str
    entry_kind: str
    types: dict
    type_candidates: list[int]
    purpose: str
    purpose_status: str
    fit_profile_ids: list[str]
    action_tags: list[str]
    naming_clues: list[str]
    evidence_refs: list[str]


def play_id(crc):
    if type(crc) is not int or not 0 < crc <= 0xffffffff:
        raise ValueError('PLAY_CRC_UINT32_NONZERO_REQUIRED')
    return '2K22_PLAY_' + format(crc, '08x')


def infer_name(name, profiles, modifiers):
    """Explain naming clues, never certify engine types, routes or beneficiaries."""
    tokens = re.findall(r'[A-Z]+', name.upper())
    families = {'FIST':'PICK_AND_ROLL', 'QUICK':'OFFSCREEN_SHOT',
                'FLOPPY':'OFFSCREEN_SHOT', 'PUNCH':'POST_ATTACK',
                'POST':'POST_ATTACK', 'POSTUP':'POST_ATTACK', 'GIVE':'HANDOFF',
                'CUT':'CUTTING', 'ISO':'ISOLATION', 'ISOLATION':'ISOLATION',
                'HIGH':'HIGH_POST_HUB', 'ELBOW':'HIGH_POST_HUB'}
    primary = next((families[t] for t in tokens if t in families), 'UNKNOWN')
    tags = [key for key in modifiers if key in tokens]
    if 'SHORT' in tokens and 'ROLL' in tokens:
        tags.insert(0, 'SHORT_ROLL')
    profile = profiles[primary]
    candidates = profile['type_candidates']
    purpose = 'UNKNOWN' if primary == 'UNKNOWN' else profile['purpose']
    clues = [modifiers[t]['meaning'] for t in tags]
    if purpose != 'UNKNOWN' and clues:
        purpose += ' 名称还提示：' + '；'.join(clues) + '。'
    return dict(purpose=purpose, purpose_status='UNKNOWN' if primary=='UNKNOWN' else 'NAME_INFERRED_NOT_ROUTE_VERIFIED',
                fit_profile_ids=[primary], type_candidates=list(candidates),
                action_tags=[primary]+tags, naming_clues=clues)


class PlayPool:
    def __init__(self, payload, observed):
        if payload.get('version') != VERSION or observed.get('version') != 'GM_PLAY_POOL_SOURCE_V1':
            raise ValueError('PLAY_POOL_VERSION')
        self.payload, self.observed = payload, observed
        self.profiles = payload['fit_profiles']
        self.types = {int(k):v for k,v in payload['play_type_names'].items()}
        self.cards = {}
        for row in payload['plays']:
            if row['play_id'] != play_id(row['native_crc']) or row['play_id'] in self.cards:
                raise ValueError('PLAY_ID_OR_DUPLICATE')
            if not row['fit_profile_ids'] or any(k not in self.profiles for k in row['fit_profile_ids']):
                raise ValueError('PLAY_FIT_PROFILE_MISSING')
            if any(type(t) is not int or t not in self.types or t==0 for t in row['type_candidates']):
                raise ValueError('PLAY_TYPE_CANDIDATE_INVALID')
            if row['types']['status'] not in ('UNKNOWN','PLAYER_REPORTED_UI','NATIVE_TYPE_VERIFIED','MIXED_EVIDENCE'):
                raise ValueError('PLAY_TYPE_EVIDENCE_STATUS_INVALID')
            for member in row['types']['memberships']:
                if (member['type_id'] not in self.types or member['type_id']==0
                    or member['evidence_status'] not in ('PLAYER_REPORTED_UI','NATIVE_TYPE_VERIFIED')
                    or not member['evidence_refs']):
                    raise ValueError('PLAY_TYPE_MEMBERSHIP_EVIDENCE_REQUIRED')
            if row['types']['status']=='UNKNOWN' and row['types']['memberships']:
                raise ValueError('PLAY_TYPE_STATUS_CONFLICT')
            self.cards[row['play_id']] = row
        self.books = {b['enum_id']:b for b in observed['books']}
        self.appearances = {key:[] for key in self.cards}
        for book in self.books.values():
            if len(book['play_crc_slots']) != 68:
                raise ValueError('OBSERVED_BOOK_68_SLOTS_REQUIRED')
            for index, crc in enumerate(book['play_crc_slots']):
                if not crc:
                    continue
                key = play_id(crc)
                if key not in self.cards:
                    raise ValueError('BOOK_REFERENCE_NOT_IN_PLAY_POOL')
                self.appearances[key].append(dict(book_enum_id=book['enum_id'], slot_index=index))

    @staticmethod
    def bounds(limit, offset):
        if type(limit) is not int or not 1<=limit<=5 or type(offset) is not int or offset<0:
            raise ValueError('PLAY_POOL_LIMIT_1_TO_5_NONNEGATIVE_OFFSET')

    def _resolve(self, identifier):
        if type(identifier) is int:
            key = play_id(identifier)
        elif not isinstance(identifier,str) or not identifier.strip():
            raise ValueError('PLAY_ID_OR_NAME_REQUIRED')
        elif identifier.lower().startswith('0x'):
            key = play_id(int(identifier,16))
        elif identifier.upper().startswith('2K22_PLAY_'):
            key = play_id(int(identifier[10:],16))
        else:
            matches = [r['play_id'] for r in self.cards.values()
                       if identifier.casefold() in [n.casefold() for n in r['names']]]
            if len(matches)!=1:
                raise ValueError('PLAY_NAME_NOT_FOUND_OR_AMBIGUOUS_USE_CRC')
            key = matches[0]
        if key not in self.cards:
            raise ValueError('PLAY_NOT_IN_REFERENCE_POOL')
        return key

    def show(self, identifier, book_limit=5, book_offset=0):
        self.bounds(book_limit,book_offset)
        key = self._resolve(identifier)
        card = deepcopy(self.cards[key])
        fit = [deepcopy(self.profiles[p]) for p in card['fit_profile_ids']]
        appearances = self.appearances[key]
        card.update(fit=fit, type_labels=[self.types[m['type_id']] for m in card['types']['memberships']],
                    candidate_type_labels=[self.types[t] for t in card['type_candidates']],
                    known_in_books=self._appearance_page(appearances,book_limit,book_offset),
                    calling_rules=deepcopy(self.payload['calling_rules']), authority=AUTHORITY,
                    implementation_status='NATIVE_TYPE_UNKNOWN_HOLD_GAME_ACTION' if card['types']['status']=='UNKNOWN'
                        else 'TYPE_REFERENCE_ONLY_CURRENT_BATCH_AND_APPROVAL_STILL_REQUIRED',
                    role_semantics='SUITABILITY_NOT_FIXED_POSITION_OR_BENEFICIARY',
                    current_save_binding='NOT_PROVIDED', behavior_effect='NOT_GAMEPLAY_VERIFIED')
        return card

    def _appearance_page(self, rows, limit, offset):
        page = [dict(**r, book_name=self.books[r['book_enum_id']]['name']) for r in rows[offset:offset+limit]]
        return dict(source_batch_id=self.observed['source_batch_id'], status=self.observed['scope'],
                    total_occurrences=len(rows), rows=page,
                    next_offset=offset+limit if offset+limit<len(rows) else None,
                    meaning='ARCHIVED_REFERENCE_NOT_EXCLUSIVE_OWNERSHIP_OR_CURRENT_TEAM_ASSIGNMENT')

    def search(self, *, text=None, role=None, team_style=None, action=None, type_id=None,
               include_inferred_types=False, book_id=None, limit=5, offset=0):
        self.bounds(limit,offset)
        if type_id is not None and (type(type_id) is not int or type_id not in self.types or type_id==0):
            raise ValueError('PLAY_TYPE_1_TO_15_REQUIRED')
        if book_id is not None and book_id not in self.books:
            raise ValueError('BOOK_NOT_IN_REFERENCE_CATALOG')
        matches=[]
        for row in self.cards.values():
            if row['entry_kind']=='FAVORITE_ONLY_ENTRY':
                continue
            fit=[self.profiles[k] for k in row['fit_profile_ids']]
            if text and text.casefold() not in json.dumps([row,fit],ensure_ascii=False).casefold():
                continue
            if role and not any(role.casefold() in json.dumps(p['player_fit'],ensure_ascii=False).casefold() for p in fit):
                continue
            if team_style and not any(team_style.casefold() in json.dumps(p['team_fit'],ensure_ascii=False).casefold() for p in fit):
                continue
            if action and not any(action.casefold() in t.casefold() for t in row['action_tags']):
                continue
            memberships=[m['type_id'] for m in row['types']['memberships']]
            inferred=type_id is not None and type_id not in memberships
            if type_id is not None and inferred and not (include_inferred_types and type_id in row['type_candidates']):
                continue
            if book_id is not None and not any(a['book_enum_id']==book_id for a in self.appearances[row['play_id']]):
                continue
            matches.append(dict(play_id=row['play_id'],names=row['names'],entry_kind=row['entry_kind'],
                types=deepcopy(row['types']),type_match='NAME_INFERRED_CANDIDATE_ONLY' if type_id is not None and inferred else
                    'DECLARED_TYPE_MEMBERSHIP' if type_id is not None else 'NO_TYPE_FILTER',
                purpose=row['purpose'],purpose_status=row['purpose_status'],action_tags=row['action_tags'],
                fit_profile_ids=row['fit_profile_ids'],known_book_count=len({a['book_enum_id'] for a in self.appearances[row['play_id']]})))
        return dict(authority=AUTHORITY,total_matches=len(matches),plays=deepcopy(matches[offset:offset+limit]),
                    next_offset=offset+limit if offset+limit<len(matches) else None,
                    inferred_types_included=include_inferred_types,
                    excluded_entry_kinds=['FAVORITE_ONLY_ENTRY; inspect explicitly with play-show or play-book'],
                    ordering='REFERENCE_ID_ORDER_NOT_RANKING_OR_EXECUTION_FREQUENCY')

    def book(self, book_id, limit=5, offset=0):
        self.bounds(limit,offset)
        if book_id not in self.books:
            raise ValueError('BOOK_NOT_IN_REFERENCE_CATALOG')
        book=self.books[book_id];slots=book['play_crc_slots']
        groups=[dict(group=n,capacity=end-start,occupied=sum(bool(v) for v in slots[start:end]),
                     empty=sum(not v for v in slots[start:end]))
                for n,start,end in [('REGULAR',0,30),('BENCH_GROUP',30,50),('ENDGAME',50,60),('FAVORITE',60,68)]]
        rows=[dict(slot_index=i,play_id=play_id(c) if c else None,
                   names=self.cards[play_id(c)]['names'] if c else [],status='OBSERVED_REFERENCE' if c else 'EMPTY')
              for i,c in enumerate(slots)][offset:offset+limit]
        return dict(authority=AUTHORITY,book={k:v for k,v in book.items() if k!='play_crc_slots'},
                    source_batch_id=self.observed['source_batch_id'],scope=self.observed['scope'],
                    capacity_total=68,groups=groups,slots=rows,next_offset=offset+limit if offset+limit<68 else None,
                    sharing='PLAYS_ARE_SHARED_POOL_REFERENCES_NOT_OWNED_BY_THIS_BOOK',current_save_binding='NOT_PROVIDED')

    def coverage(self):
        rows=list(self.cards.values())
        return dict(version=VERSION,authority=AUTHORITY,plays=len(rows),books=len(self.books),
                    named=sum(bool(r['names']) for r in rows),name_unknown=sum(not r['names'] for r in rows),
                    purpose_inferred=sum(r['purpose_status']=='NAME_INFERRED_NOT_ROUTE_VERIFIED' for r in rows),
                    purpose_unknown=sum(r['purpose_status']=='UNKNOWN' for r in rows),
                    declared_type_membership=sum(bool(r['types']['memberships']) for r in rows),
                    native_type_verified=sum(any(m['evidence_status']=='NATIVE_TYPE_VERIFIED' for m in r['types']['memberships']) for r in rows),
                    type_unknown=sum(r['types']['status']=='UNKNOWN' for r in rows),
                    shared_across_books=sum(len({a['book_enum_id'] for a in self.appearances[r['play_id']]})>1 for r in rows),
                    source_batch_id=self.observed['source_batch_id'],calling_rules=deepcopy(self.payload['calling_rules']))
