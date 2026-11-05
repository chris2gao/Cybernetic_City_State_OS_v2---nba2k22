"""Trusted catalog of recovered Player stat fields, not a game data provider."""
import json
from pathlib import Path

ACTION_FAMILIES = {'PLAYER_SET_ATTRIBUTE': 'attributes', 'PLAYER_PATCH_ATTRIBUTES': 'attributes',
                   'PLAYER_SET_TENDENCY': 'tendencies', 'PLAYER_PATCH_TENDENCIES': 'tendencies'}
ROLE_FIELDS = {'PLAYER.EDIT.ATTR_SET': 'attributes', 'PLAYER.EDIT.ATTR_BATCH': 'attributes',
               'PLAYER.EDIT.TENDENCY_SET': 'tendencies', 'PLAYER.EDIT.TENDENCY_BATCH': 'tendencies'}


def load_fields(root=None):
    root = Path(root) if root is not None else Path(__file__).parent
    return json.loads((root / 'data/player_stat_fields.json').read_text(encoding='utf8'))


def selected_values(action_id, parameters):
    if action_id not in ACTION_FAMILIES:
        raise ValueError('Not a recovered stat action')
    values = parameters['values'] if action_id.startswith('PLAYER_PATCH_') else {parameters['field_id']: parameters['value']}
    if not isinstance(values, dict) or not values:
        raise ValueError('Explicit nonempty Player field values required')
    return values


def allowed_fields(catalog, family, role):
    fields = {key: value for key, value in catalog['families'][family].items() if value['callable']}
    if family == 'attributes':
        return fields if role == 'WORLD_ADMIN' else {key: value for key, value in fields.items()
                                                   if role == 'GM' and key == 'intangibles'}
    return fields if role == 'WORLD_ADMIN' else {key: value for key, value in fields.items() if value['name_known']}


def validate_values(catalog, action_id, parameters):
    values = selected_values(action_id, parameters)
    fields = catalog['families'][ACTION_FAMILIES[action_id]]
    for key, value in values.items():
        if type(key) is not str or key not in fields or not fields[key]['callable']:
            raise ValueError('Unqualified Player field: ' + str(key))
        spec = fields[key]
        if type(value) is not int or not spec['minimum'] <= value <= spec['maximum']:
            raise ValueError('Player value outside exact native UI range: ' + key)
    return values
