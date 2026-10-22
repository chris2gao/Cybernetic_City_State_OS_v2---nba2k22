"""Single native dictionary, projecting existing profiles instead of copying offsets."""
from copy import deepcopy
from pathlib import Path
from coach_codec import load_profile
from .common import digest, load

NATIVE = Path(__file__).resolve().parents[2]/'config/state_io_native'


class Registry:
    def __init__(self):
        self.coach_profile = load_profile()
        self.fields = {}
        for name, f in self.coach_profile['fields'].items():
            default = name in self.coach_profile['gm_default_fields']
            self.add('coach.'+name, 'tactics', 'COACH_DEFAULT', deepcopy(f),
                     writable=default and f['writable'] and f['production_enabled'],
                     evidence=f['readiness'], codec='coach_codec')
            if name == 'PlaybookID':
                self.fields['coach.PlaybookID']['gm_enabled'] = False
                self.fields['coach.PlaybookID']['restricted_operation'] = 'TEAM_BOOK_REBIND'
        for name, f in self.coach_profile['defensive_fields'].items():
            for kind in ('OVERALL_DEFENSE', 'PERSONAL_DEFENSE'):
                layout = dict(offset=0, storage_bytes=8, start_bit=f['offset']*8+f['start_bit'],
                              width=f['width'], enum=({'0':'OFF','1':'ON'} if f.get('native_boolean') else
                                                    f.get('native_enum_labels') or f['native_enum_name_crc32']))
                self.add(('overall.' if kind == 'OVERALL_DEFENSE' else 'personal.')+name,
                         'defense', kind, layout, writable=f['production_enabled'],
                         evidence=f['readiness'], codec='defense_codec')
                if kind == 'OVERALL_DEFENSE':
                    self.fields['overall.'+name]['gm_enabled'] = False
        player = load(NATIVE/'player.json')
        known = {v: k for k, v in player['TENDENCY_OFFSETS'].items()}
        for offset in range(0x458, 0x4bb):
            name = known.get(offset, 'RAW_'+hex(offset))
            self.add('tendency.'+name, 'tendency', 'PLAYER_TENDENCY',
                     dict(offset=offset, storage_bytes=1, start_bit=0, width=8, raw_range=[0, 100]),
                     writable=offset in known, evidence='ANTIGRAVITY_NATIVE_PLAYER_REPORTED',
                     behavior='NAMED_NATIVE' if offset in known else 'UNKNOWN_RAW_BYTE')
        for slot in range(1, 5):
            self.add('playtype.slot'+str(slot), 'tactics', 'PLAYER_PLAYTYPE',
                     dict(offset=0x168+(slot-1)//2, storage_bytes=1, start_bit=4*((slot-1)%2), width=4,
                          enum=player['PLAY_TYPE_NAMES'], slot=slot), writable=True)
        self.add('playtype.initiator', 'tactics', 'PLAYER_PLAYTYPE',
                 dict(offset=0x16a, storage_bytes=1, start_bit=2, width=1), writable=True)
        memory_profile = load(NATIVE.parent/'memory_field_profile.json')
        intangibles = next(f for f in memory_profile['fields']['PLAYER'] if f['name']=='intangibles')
        if (intangibles['offset'], intangibles['bytes'], intangibles['conversion']) != (0x440, 1, 'rating'):
            raise ValueError('INTANGIBLES_PROFILE_LAYOUT_CHANGED')
        self.add('rotation.intangibles', 'rotation', 'PLAYER_ROTATION_OVR_BIAS',
                 dict(offset=intangibles['offset'], storage_bytes=1, start_bit=0, width=8,
                      encoding='rating', raw_range=[25,99]), writable=True,
                 evidence='PLAYER_AUTHORIZED_NATIVE_RATING_PROFILE',
                 behavior='ROTATION_BIAS_NOT_EXACT_MINUTES_OR_GENERAL_ABILITY_PERMISSION')
        court = load(NATIVE/'court.json')
        for name, f in court['modified_sliders'].items():
            self.add('gameplay.'+name, 'gameplay', 'GLOBAL_GAMEPLAY',
                     dict(offset=4+f['table_index']*8, storage_bytes=4, encoding='float32_percent',
                          raw_range=[0, 100], mirror_delta=0x3f0,
                          pointer_rva=int(court['slot_sliders_rva'], 16)), writable=True,
                     behavior='NATIVE_SETTING_EFFECT_NOT_QUANTIFIED')
        # Import both world catalogs, retaining independent native slots/pages.
        occupied = set()
        for catalog_name in ('world', 'settings'):
            catalog = load(NATIVE/(catalog_name+'.json'))
            for group, fields in catalog['fields'].items():
                for name, f in fields.items():
                    if 'slot' not in f or 'offset' not in f or f.get('type') not in ('uint32', 'float'):
                        continue
                    slot = catalog['slots'].get(f['slot'])
                    if not slot or 'rva' not in slot:
                        continue
                    location = (slot['rva'], f['offset'])
                    if location in occupied:
                        continue
                    occupied.add(location)
                    unknown = 'boost' in name.lower() or f.get('status') in ('UNKNOWN', 'UNVERIFIED')
                    self.add('world.'+group+'.'+name, 'world', 'WORLD_SETTING',
                             dict(offset=int(f['offset'], 16), storage_bytes=4,
                                  encoding='float32' if f['type'] == 'float' else 'uint', start_bit=0, width=32,
                                  pointer_rva=int(slot['rva'], 16), group=group), writable=not unknown,
                             behavior='UNKNOWN' if unknown else 'NATIVE_SETTING_EFFECT_NOT_QUANTIFIED')
        training = load(NATIVE/'training.json')
        offsets = training['structures']['team_training']['offsets']
        for name in ('home_intensity','away_intensity','automate_intensity','rest_before_b2b','rest_after_b2b','injury_recovery'):
            f = offsets[name]
            self.add('training.team.'+name, 'training', 'TEAM_TRAINING',
                     dict(offset=int(f['offset'], 16), storage_bytes=1, start_bit=f['start_bit'], width=f['width'],
                          raw_range=[0, 5] if 'intensity' in name and name != 'automate_intensity' else [0, 1]), writable=True)
        flags = training['structures']['player_training']['offsets']['flags']
        for name in ('position','player_type','intensity','injury_recovery','is_intensity_overriden'):
            f = flags[name]
            limits = {'position': 5, 'player_type': 8, 'intensity': 5}
            self.add('training.player.'+name, 'training', 'PLAYER_TRAINING',
                     dict(offset=int(flags['offset'],16), storage_bytes=4, start_bit=f['start_bit'], width=f['width'],
                          raw_range=[0, limits.get(name,1)]), writable=True)
        self.add('playbook.slot', 'tactics', 'PLAYBOOK_SLOT',
                 dict(offset=0, storage_bytes=4, encoding='uint', start_bit=0, width=32),
                 writable=True, behavior='OWN_TEAM_NAMED_BOOK_OBSERVED_PLAY_CRC_ONLY')
        self.add('mentor.relationship', 'training', 'MENTOR',
                 dict(offset=0, storage_bytes=1, start_bit=0, width=8), writable=False,
                 evidence='DISCOVERED', behavior='RELATIONSHIP_AND_BADGE_PERMISSION_ADAPTER_PENDING')
        self._version = None

    @property
    def version(self):
        if self._version is None:
            self._version=digest(self.fields)
        return self._version

    def add(self, key, domain, kind, layout, *, writable=False, codec='native',
            evidence='ANTIGRAVITY_NATIVE_PLAYER_REPORTED', behavior='NATIVE_SETTING_EFFECT_NOT_QUANTIFIED'):
        if key in self.fields:
            raise ValueError('DUPLICATE_NATIVE_FIELD')
        self._version=None
        self.fields[key] = dict(field_key=key, domain=domain, target_kind=kind, layout=layout,
                               native_codec=codec, source_adapter='gm_state_io.adapters.NativeSession', writer_adapter='gm_state_io.adapters.NativeSession',
                               read_status='DISCOVERED' if evidence=='DISCOVERED' else 'READ_VERIFIED',
                               write_capability='MEMORY_WRITE_VERIFIED' if writable else 'READ_ONLY',
                               game_save_persisted=False, gm_enabled=writable,
                               behavior_evidence=behavior, native_evidence=evidence,
                               validity_scope='SAVE_GENERATION_BATCH_OBJECT', setting_page=kind)

    def field(self, key):
        if key not in self.fields:
            raise ValueError('UNREGISTERED_FIELD:'+str(key))
        return self.fields[key]
