"""DEV27 T1-T3: small static fixtures only; no native/game access."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from gm_state_io.common import digest
from gm_state_io.team_book import identity, team_book, validate_rebind, validate_slot


def book(name, index=2):
    return dict(name=name, index=index, enum_id=index, unique_id=index + 1)


class TeamBookSuffixChecks(unittest.TestCase):
    def test_T1_existing_and_suffix_names(self):
        for name, abbreviation, city in (
            ('Bulls', 'CHI', 'Chicago'), ('Heat', 'MIA', 'Miami'),
            ('Warriors', 'GSW', 'Golden State'),
        ):
            team = dict(name=name, abbreviation=abbreviation, city=city)
            for label in (name, name + ' Playbook', abbreviation,
                          abbreviation + ' Playbook', city + ' ' + name,
                          city + ' ' + name + ' Playbook'):
                with self.subTest(label=label):
                    native = book(label)
                    self.assertEqual(team_book(team, [native]), identity(native))

    def test_T2_missing_wrong_similar_and_ambiguous(self):
        team = dict(name='Bulls', abbreviation='CHI', city='Chicago')
        for books in ([], [book('Lakers Playbook')],
                      [book('Bulls Practice Playbook')], [book('BullsPlaybook')],
                      [book('Bulls Playbook Practice')],
                      [book('Bulls Playbook'), book('Bulls Playbook', 3)],
                      [book('Bulls'), book('Bulls Playbook', 3)]):
            with self.subTest(books=books):
                with self.assertRaisesRegex(ValueError, '^TEAM_NAMED_BOOK_MISSING_OR_AMBIGUOUS$'):
                    team_book(team, books)

    def test_T3_static_slot_and_rebind_contracts(self):
        own, other = book('Bulls Playbook'), book('Lakers Playbook', 3)
        source = dict(team_directory={'1': dict(name='Bulls', abbreviation='CHI', city='Chicago')},
                      source_context=dict(playbooks=[own, other]))
        obj = dict(identity={'coach': 'static-coach'},
                   selector=dict(team_id=1, owner_team_ids=[1], playbook_identity=digest(identity(own))))
        self.assertIsNone(validate_slot(source, obj))
        for field, value in (('owner_team_ids', [2]), ('playbook_identity', digest(identity(other)))):
            bad = copy.deepcopy(obj)
            bad['selector'][field] = value
            with self.assertRaises(PermissionError):
                validate_slot(source, bad)
        event = dict(kind='INITIAL_SAVE', reference='static-player-confirmed-event',
                     team_id=1, current_coach_identity=obj['identity'])
        proposal = dict(operation='TEAM_BOOK_REBIND', event=event)
        self.assertEqual(validate_rebind(proposal, source, obj, own['enum_id']), identity(own))
        with self.assertRaisesRegex(PermissionError, '^TEAM_BOOK_REBIND_MUST_TARGET_OWN_TEAM_NAMED_BOOK$'):
            validate_rebind(proposal, source, obj, other['enum_id'])
        for bad in (dict(operation='TEAM_BOOK_REBIND'),
                    dict(operation='TEAM_BOOK_REBIND', event=dict(event, current_coach_identity={} ))):
            with self.assertRaisesRegex(PermissionError, '^TEAM_BOOK_REBIND_EVENT_AND_CURRENT_COACH_REQUIRED$'):
                validate_rebind(bad, source, obj, own['enum_id'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
