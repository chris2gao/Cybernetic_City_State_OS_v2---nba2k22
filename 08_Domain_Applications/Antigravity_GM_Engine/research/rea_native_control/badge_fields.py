"""Exact editor Badge parameters; Native mutability does not grant persona rights."""
import json
from pathlib import Path

REQUIREMENT = 'PLAYER.EDIT.BADGE_SET'


def load_fields(root=None):
    return json.loads(((Path(root) if root else Path(__file__).parent) / 'data/player_badge_fields.json').read_text(encoding='utf8'))


def affected_fields(catalog, field_id):
    field = catalog['fields'].get(field_id)
    if not field or field['sentinel_name']:
        raise ValueError('Explicit non-sentinel Native Badge field required')
    for group in catalog['coupled_groups']:
        if field_id in group:
            return tuple(group)
    return (field_id,)


def validate_parameters(catalog, parameters):
    field_id, value = parameters['field_id'], parameters['value']
    names = affected_fields(catalog, field_id)
    field = catalog['fields'][field_id]
    if type(value) is not int or not 0 <= value <= field['maximum']:
        raise ValueError('Badge value outside recovered per-ID range')
    for key in ('expected_before', 'expected_after'):
        values = parameters[key]
        if not isinstance(values, dict) or set(values) != set(names):
            raise ValueError('Exact possible coupled Badge group required in ' + key)
        if any(type(level) is not int or not 0 <= level <= catalog['fields'][name]['maximum']
               for name, level in values.items()):
            raise ValueError('Badge group values outside exact ranges')
    if parameters['expected_after'][field_id] != value:
        raise ValueError('Requested Badge and explicit after-state disagree')
    if parameters['expected_before'][field_id] == value and parameters['expected_after'] != parameters['expected_before']:
        raise ValueError('Native unchanged-primary early return cannot change other Badges')
    return names


def resource_fields(catalog, parameters):
    names = set(validate_parameters(catalog, parameters))
    index = catalog['fields'][parameters['field_id']]['badge_id']
    if parameters['value'] > 0 and parameters['expected_before'][parameters['field_id']] != parameters['value']:
        if index == 5:
            names.add('Expressive')
        elif index in (21, 24):
            names.add('LowFriendliness')
    return tuple(sorted(names))
