"""Small versioned basketball references. Native mappings are evidence, not approvals."""
from copy import deepcopy
import json
from pathlib import Path


def read_json(path):
    path = Path(path)
    if path.stat().st_size > 2_000_000:
        raise ValueError('KNOWLEDGE_INPUT_TOO_LARGE')
    return json.loads(path.read_text(encoding='utf-8-sig'))


class Knowledge:
    def __init__(self, root):
        root = Path(root)
        self.root = root
        self.cards = read_json(root/'tactics_v1.json')['cards']
        self.franchises = read_json(root/'franchise_references_2021_v1.json')['franchises']
        self.sources = read_json(root/'sources_v1.json')['sources']
        self.rules = read_json(root/'game_engine_rules_v1.json')['rules']
        self.validate()

    def bpti(self):
        """Opt-in BPTI references/cards; does not replace the twelve M2 cards."""
        from .bpti import ResearchIndex
        payload = read_json(self.root/'bpti/research_source_index.json')
        card_path = self.root/'bpti/system_cards_v1.json'
        if not card_path.exists():
            return ResearchIndex(payload)
        card_set = read_json(card_path)
        if card_set['schema_version'] != payload['schema_version'] or card_set['version'] != 'BPTI_SYSTEM_CARDS_V1':
            raise ValueError('BPTI_SYSTEM_CARD_VERSION')
        payload['claims'] += card_set['claims']
        package_path = self.root/'bpti/package_b_v1.json'
        package = read_json(package_path) if package_path.exists() else None
        if package:
            payload['sources'] += package['sources']
            payload['claims'] += package['claims']
        return ResearchIndex(payload, card_set['cards'], package)

    def play_pool(self):
        """Opt-in shared plays, name-based purpose/fit and archived book references."""
        from .play_pool import PlayPool
        return PlayPool(read_json(self.root/'plays/play_pool_v1.json'),
                        read_json(self.root/'plays/observed_catalog_v1.json'))

    def validate(self):
        for rows, key, count in ((self.cards, 'card_id', 12), (self.franchises, 'team', 30),
                                 (self.sources, 'source_id', None), (self.rules, 'rule_id', None)):
            if len({r[key] for r in rows}) != len(rows) or (count and len(rows) != count):
                raise ValueError('KNOWLEDGE_ID_OR_COUNT_INVALID')
        sources = {s['source_id']: s for s in self.sources}
        required = ('version', 'title', 'tags', 'basketball_principle', 'required_roles',
                    'required_abilities', 'counters_and_weaknesses', 'opportunity_cost',
                    'observable_signals', 'unavailable_signals', 'native_links',
                    'reference_sources', 'confidence', 'game_version_scope', 'status', 'superseded_by')
        for card in self.cards:
            if any(k not in card for k in required) or not card['reference_sources']:
                raise ValueError('CARD_FIELDS_OR_SOURCES_REQUIRED')
            if set(card['confidence']) != {'basketball', 'native_mapping', 'in_game_effect'}:
                raise ValueError('THREE_EVIDENCE_AXES_REQUIRED')
            for source in card['reference_sources']:
                if source['source_id'] not in sources or source['url'] != sources[source['source_id']]['url']:
                    raise ValueError('CARD_SOURCE_NOT_REGISTERED')
        for row in self.franchises + self.rules:
            if row['source_id'] not in sources:
                raise ValueError('REFERENCE_SOURCE_NOT_REGISTERED')

    def franchise(self, team, period='2021'):
        rows = [r for r in self.franchises if r['team'] == team.upper() and r['reference_period'].startswith(period)]
        if not rows:
            raise ValueError('FRANCHISE_REFERENCE_NOT_FOUND')
        return deepcopy(rows[0])

    def search(self, tag=None, field=None, team=None, text=None, limit=5):
        if not 1 <= limit <= 5:
            raise ValueError('KNOWLEDGE_LIMIT_1_TO_5')
        pilot = self.franchise(team).get('pilot') if team else None
        preferred = set(pilot['tactic_cards']) if pilot else set()
        rows = [c for c in self.cards if
                (not tag or tag in c['tags']) and
                (not field or any(l['field'] == field for l in c['native_links'])) and
                (not team or c['card_id'] in preferred) and
                (not text or text.casefold() in json.dumps(c, ensure_ascii=False).casefold())]
        return dict(total_matches=len(rows), truncated=len(rows) > limit,
                    team_reference_status='PILOT_HYPOTHESIS_ONLY' if pilot else 'NO_TEAM_PRESET' if team else None,
                    cards=[dict(card_id=c['card_id'], title=c['title'], tags=c['tags'],
                                confidence=c['confidence'], principle=c['basketball_principle']) for c in rows[:limit]])

    def show(self, card_id, native=None):
        card = next((deepcopy(c) for c in self.cards if c['card_id'] == card_id), None)
        if card is None:
            raise ValueError('TACTIC_CARD_NOT_FOUND')
        card['source_binding'] = native.get('source_binding') if native else None
        card['native_resolution'] = [resolve_link(link, native) for link in card['native_links']]
        card['authority'] = 'REFERENCE_ONLY_SEPARATE_GAME_APPROVAL_REQUIRED'
        return card


def catalog(field):
    # Native catalogs are raw-string -> semantic label, not label -> raw.
    return {label: int(raw) for raw, label in field.get('enum', field.get('native_enum_labels', {})).items()}


def resolve_link(link, native):
    result = dict(link, resolution='UNAVAILABLE', raw_candidate=None)
    if not native or not native.get('available') or not native.get('dictionary'):
        result['reason'] = 'SAME_BATCH_COACHING_UNAVAILABLE'
        return result
    dictionary, profile = native['dictionary'], native['profile']
    default = link['scope'] == 'COACH_DEFAULT'
    current = profile.get('fields' if default else 'defensive_fields', {}).get(link['field'])
    captured = dictionary.get('default_fields' if default else 'defensive_fields', {}).get(link['field'])
    if current is None or captured is None:
        result['reason'] = 'FIELD_NOT_IN_BOTH_CATALOGS'
        return result
    mapping = link['mapping_status']
    if mapping == 'DYNAMIC_CATALOG':
        books = dictionary.get('playbooks', [])
        result.update(resolution='SAME_BATCH_DYNAMIC_CATALOG', candidate_count=len(books),
                      reason='Query same-batch named coaching catalog; no permanent playbook raw target')
    elif mapping in ('NATIVE_ENUM', 'HYPOTHESIS'):
        label = link['semantic_label']
        a, b = catalog(current), catalog(captured)
        if label not in a or label not in b or a[label] != b[label]:
            result['reason'] = 'LABEL_MISSING_OR_PROFILE_BATCH_DISAGREE'
        else:
            result.update(resolution='HYPOTHESIS_CANDIDATE' if mapping == 'HYPOTHESIS' else 'SAME_BATCH_NATIVE_ENUM',
                          raw_candidate=b[label], reason='Not certified as Drop' if mapping == 'HYPOTHESIS' else 'Label agrees in current profile and selected batch')
    else:
        result.update(resolution='FIELD_CONTEXT_ONLY', reason='Roster/scalar/native field context; caller must choose a value')
    if 'freelance_slot_order' in dictionary:
        result['freelance_slot_order'] = dictionary['freelance_slot_order']
    return result
