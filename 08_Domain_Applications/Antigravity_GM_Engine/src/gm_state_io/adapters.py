"""Native resolvers over one calibrated session, never standalone unsafe writers.

The external code is a field/layout source, not imported: several originals open
PROCESS_ALL_ACCESS in constructors, including their read paths.
"""
import struct
from .common import digest
from .plan import object_key
from .codec import decode


def player_identity(raw, pool_slot):
    return dict(pool_slot=pool_slot,native_player_id=int.from_bytes(raw[0x2f8:0x2fa],'little'),
                identity_tag=digest([raw[:0x50].hex(),raw[0x6c:0x6e].hex(),pool_slot]))


class NativeSession:
    def __init__(self, read_only=True, registry=None, memory=None, locator=None, resolvers=None):
        from coach_locator import CoachLocator, live_memory
        self.registry = registry
        self.owns_memory = memory is None
        self.mem = memory or live_memory(read_only=read_only)
        self.loc = locator or CoachLocator(self.mem).calibrate()
        self.read_only = read_only
        self._players = {}
        self._training = None
        self._roots = {}
        self.resolvers = resolvers or {}

    @property
    def process_binding(self):
        from coaching_targets import process_binding
        return process_binding(self.mem.pid,self.mem.creation_time)

    def read(self, address, size):
        from coach_locator import read_exact
        return read_exact(self.mem,address,size)

    def write(self, address, raw):
        if self.read_only:
            raise PermissionError('READ_ONLY_SESSION')
        return self.mem.write_bytes(address,raw)

    def close(self):
        if self.owns_memory:
            self.mem.close()

    def verify_context_light(self):
        self.loc.alive()
        for rva in self._roots:
            self.root(rva)

    def verify_context(self, source):
        from coaching_targets import validate_session
        if self.process_binding != source['process_binding']:
            raise ValueError('STALE_PROCESS_BINDING')
        if source.get('source_context'):
            context=source['source_context']
            # Slot contents are changeable state, not directory identity. Full
            # before/after slot blocks are still checked by the transaction.
            clean=lambda books:[{k:v for k,v in p.items() if k!='play_crc_slots'} for p in books]
            if clean(self.loc.playbooks)!=clean(context['playbooks']):
                raise ValueError('LOADED_PLAYBOOK_DIRECTORY_CHANGED')
            validate_session(self.loc,dict(context,playbooks=self.loc.playbooks))
        self.loc.alive()

    def root(self, rva):
        from coach_locator import u64
        pointer = u64(self.mem,self.mem.base_address+rva)
        if not pointer:
            raise ValueError('OPTIONAL_NATIVE_ROOT_UNAVAILABLE')
        if rva in self._roots and self._roots[rva] != pointer:
            raise ValueError('NATIVE_OBJECT_ROOT_MOVED')
        self._roots[rva] = pointer
        return pointer

    def players(self, tid):
        from coach_locator import u64
        if tid in self._players:
            return self._players[tid]
        team = self.loc.teams[tid]
        table = self.loc.directory['players']
        result = []
        for roster_slot in range(25):
            ptr = u64(self.mem,team['address']+roster_slot*8)
            if not ptr:
                continue
            pool_slot, remainder = divmod(ptr-table['address'],table['stride'])
            if remainder or not 0<=pool_slot<table['count']:
                raise ValueError('PLAYER_NOT_IN_VERIFIED_DIRECTORY')
            raw = self.read(ptr,0x4f0)
            if int.from_bytes(raw[0x60:0x68],'little') != team['address']:
                raise ValueError('PLAYER_TEAM_IDENTITY_CHANGED')
            ident = player_identity(raw,pool_slot)
            result.append(dict(address=ptr,raw=raw,identity=ident,roster_slot=roster_slot))
        if len({p['identity']['identity_tag'] for p in result}) != len(result):
            raise ValueError('DUPLICATE_PLAYER_IDENTITY')
        self._players[tid] = result
        return result

    def training_slots(self):
        if self._training is None:
            base = self.root(0x632b480)+0xc60
            self._training = {}
            # Build once for thousands of changes; duplicate IDs never pick first.
            for i in range(786):
                address = base+i*796
                pid = int.from_bytes(self.read(address,4),'little')
                if pid in (0,0xffffffff):
                    continue
                self._training.setdefault(pid,[]).append(address)
        return self._training

    def gameplan(self, tid, opp):
        native = self.loc.profile['native']
        hits = []
        for i in range(native['gameplan_capacity']):
            addr = self.loc.managers[tid]+native['gameplan_start']+i*native['gameplan_stride']
            header = self.read(addr,6)
            if int.from_bytes(header[2:4],'little')==tid and int.from_bytes(header[4:6],'little')==opp:
                hits.append(addr)
        if len(hits) != 1:
            raise ValueError('AMBIGUOUS_OPPONENT_GAMEPLAN')
        return hits[0]

    def resolve(self, obj):
        s = obj['selector']
        kind, tid = s['target_kind'], s.get('team_id')
        if tid is not None and tid not in self.loc.teams:
            raise ValueError('TEAM_NOT_IN_OBSERVED_DIRECTORY')
        if kind == 'COACH_DEFAULT':
            coach = self.loc.coaches[tid]
            identity, at = coach['identity'], coach['address']
            if obj.get('team_book_rebind'):
                from .team_book import team_book
                if team_book(self.loc.teams[tid],self.loc.playbooks) != obj['team_book_rebind']:
                    raise ValueError('TEAM_BOOK_REBIND_TARGET_IDENTITY_CHANGED')
        elif kind in ('PLAYER_TENDENCY','PLAYER_PLAYTYPE','PLAYER_TRAINING','PLAYER_ROTATION_OVR_BIAS'):
            hits = [p for p in self.players(tid) if p['identity']['identity_tag']==s['player_identity']]
            if len(hits)!=1:
                raise ValueError('PLAYER_IDENTITY_CHANGED')
            p = hits[0]
            identity, at = p['identity'], p['address']
            if kind == 'PLAYER_TRAINING':
                addresses = self.training_slots().get(identity['native_player_id'],[])
                if len(addresses)!=1:
                    raise ValueError('TRAINING_PLAYER_ID_UNMAPPED_OR_AMBIGUOUS')
                at = addresses[0]
        elif kind == 'GLOBAL_GAMEPLAY':
            if s['side'] not in ('USER','CPU'):
                raise ValueError('USER_CPU_SIDE_REQUIRED')
            at = self.root(0x632b4a0)+(4 if s['side']=='CPU' else 0)
            identity = dict(native_type='TUNEDATA_SAVED',side=s['side'])
        elif kind == 'WORLD_SETTING':
            fields = [self.registry.field(k) for k in obj['field_keys']]
            rvas = {f['layout']['pointer_rva'] for f in fields}
            if len(rvas)!=1:
                raise ValueError('WORLD_OBJECT_SLOT_MISMATCH')
            at = self.root(next(iter(rvas)))
            identity = dict(native_slot=s['native_slot'],group=s['group'])
        elif kind == 'TEAM_TRAINING':
            n = self.loc.profile['native']
            slot, remainder = divmod(self.loc.managers[tid]-(self.loc.franchise+n['franchise_teams_offset']),n['franchise_team_stride'])
            if remainder or not 0<=slot<36:
                raise ValueError('TRAINING_TEAM_SLOT_MISMATCH')
            at = self.root(0x632b480)+slot*88
            identity = dict(team_id=tid,franchise_slot=slot,training_period='CURRENT')
        elif kind == 'PLAYBOOK_SLOT':
            from coach_locator import u64
            from coach_codec import decode as decode_coach
            book=next((p for p in self.loc.playbooks if book_identity(p)==s['playbook_identity']),None)
            if book is None or type(s['slot_index']) is not int or not 0<=s['slot_index']<68:
                raise ValueError('PLAYBOOK_IDENTITY_OR_SLOT_CHANGED')
            owners=sorted(t for t,c in self.loc.coaches.items() if decode_coach(self.read(c['address'],0x160),self.loc.profile['fields']['PlaybookID'])==book['enum_id'])
            if owners!=s['owner_team_ids']:
                raise ValueError('SHARED_PLAYBOOK_OWNER_SET_CHANGED')
            from .team_book import team_book
            if owners != [tid] or digest(team_book(self.loc.teams[tid],self.loc.playbooks)) != book_identity(book):
                raise ValueError('ONLY_OWN_TEAM_NAMED_BOOK_SLOTS_ALLOWED')
            n=self.loc.profile['native']
            at=u64(self.mem,self.loc.roster+n['playbook_pointer_offset'])+book['index']*n['playbook_stride']+0x58+s['slot_index']*4
            identity=dict(playbook_identity=s['playbook_identity'],owner_team_ids=owners)
        elif kind in ('DEFENSE_BLOCK','GAMEPLAN_COMMIT'):
            gp = self.gameplan(tid,s['opponent_team_id'])
            if kind=='GAMEPLAN_COMMIT':
                at, identity = gp, dict(team_id=tid,opponent_team_id=s['opponent_team_id'])
            else:
                at = gp+0x64+s['record_index']*12+4
                ids = self.read(at-4,4)
                identity = dict(matchup_id=int.from_bytes(ids[:2],'little'),defender_id=int.from_bytes(ids[2:],'little'))
        else:
            resolver=self.resolvers.get(kind)
            if resolver is None:
                raise ValueError('BLOCKED_SOURCE_ADAPTER:'+kind)
            # Extensions are reviewed code, never command-line module paths or
            # raw addresses supplied by a model. The same identity contract holds.
            at,identity=resolver(self,obj)
        if identity != obj['identity']:
            raise ValueError('OBJECT_IDENTITY_CHANGED')
        return at


def book_identity(book):
    return digest({k:book[k] for k in ('index','enum_id','unique_id','name')})


def capture_objects(session, coaching):
    """One RO session, shared registry decoder. Unknown optional domains stay absent."""
    from .registry import Registry
    reg = session.registry or Registry()
    objects, coverage = [], {}
    by_kind = {}
    for key, field in reg.fields.items():
        by_kind.setdefault(field['target_kind'],[]).append(key)

    def add(selector, identity, raw, keys, **extra):
        # Decode once during capture, including finite/type checks, never default 50.
        values = {k:decode(raw,reg.field(k)) for k in keys}
        obj = dict(object_key=object_key(selector),selector=selector,identity=identity,raw=raw.hex(),
                   field_keys=keys,values=values,source_status='OBSERVED_SAME_SESSION',**extra)
        objects.append(obj)
        return obj

    for team in coaching['teams']:
        tid = team['team_id']
        at = session.loc.coaches[tid]['address']
        add(dict(target_kind='COACH_DEFAULT',team_id=tid),team['coach_identity'],session.read(at,0x160),by_kind['COACH_DEFAULT'])
        for gp in team['gameplans']:
            overall = gp.get('overall_defense')
            if not overall:
                continue
            opp = gp['opponent_team_id']
            commit_s = dict(target_kind='GAMEPLAN_COMMIT',team_id=tid,opponent_team_id=opp)
            commit = dict(object_key=object_key(commit_s),selector=commit_s,identity=dict(team_id=tid,opponent_team_id=opp),
                          raw=bytes([overall['commit_flag_raw']]).hex(),field_keys=[],source_status='OBSERVED_SAME_SESSION')
            members = []
            for b in overall['blocks']:
                selector = dict(target_kind='DEFENSE_BLOCK',team_id=tid,opponent_team_id=opp,
                                record_index=(b['settings_offset']-0x68)//12)
                members.append(dict(object_key=object_key(selector),selector=selector,identity=b['identity'],
                                    raw=b['raw_block'],field_keys=by_kind['OVERALL_DEFENSE'],source_status='OBSERVED_SAME_SESSION'))
                # PERSONAL targets only when both native IDs uniquely match the
                # corresponding current rosters; never infer the mapping by name.
                target = [p for p in session.players(opp) if p['identity']['native_player_id']==b['identity']['matchup_id']]
                defender = [p for p in session.players(tid) if p['identity']['native_player_id']==b['identity']['defender_id']]
                if len(target)==len(defender)==1:
                    personal_selector = dict(target_kind='PERSONAL_DEFENSE',team_id=tid,opponent_team_id=opp,
                                             opponent_player_identity=target[0]['identity']['identity_tag'],
                                             defender_identity=defender[0]['identity']['identity_tag'])
                    add(personal_selector,b['identity'],bytes.fromhex(b['raw_block']),by_kind['PERSONAL_DEFENSE'],
                        members=[dict(members[-1],field_keys=by_kind['PERSONAL_DEFENSE'])],commit_object=commit)
            selector = dict(target_kind='OVERALL_DEFENSE',team_id=tid,opponent_team_id=opp)
            # Mixed parents carry full member values instead of fabricating one raw.
            objects.append(dict(object_key=object_key(selector),selector=selector,identity=overall['identity'],
                                raw=None,field_keys=by_kind['OVERALL_DEFENSE'],members=members,commit_object=commit,
                                values={'overall.'+k:v for k,v in overall['values'].items()},source_status='OBSERVED_SAME_SESSION'))
        for p in session.players(tid):
            for kind in ('PLAYER_TENDENCY','PLAYER_PLAYTYPE','PLAYER_ROTATION_OVR_BIAS'):
                add(dict(target_kind=kind,team_id=tid,player_identity=p['identity']['identity_tag']),p['identity'],p['raw'],by_kind[kind])
    for book in coaching['playbooks']:
        owners=sorted(t['team_id'] for t in coaching['teams'] if t['values']['PlaybookID']==book['enum_id'])
        if not owners:
            continue
        for slot, crc in enumerate(book['play_crc_slots']):
            ident=book_identity(book)
            add(dict(target_kind='PLAYBOOK_SLOT',playbook_identity=ident,owner_team_ids=owners,slot_index=slot,
                     **({'team_id':owners[0]} if len(owners)==1 else {})),
                dict(playbook_identity=ident,owner_team_ids=owners),int(crc).to_bytes(4,'little'),by_kind['PLAYBOOK_SLOT'])
    # Optional sources do not suppress already audited required coaching sources.
    groups = [('GLOBAL_GAMEPLAY',dict(target_kind='GLOBAL_GAMEPLAY',side=s),dict(native_type='TUNEDATA_SAVED',side=s),2020,by_kind['GLOBAL_GAMEPLAY']) for s in ('USER','CPU')]
    world = {}
    for key in by_kind.get('WORLD_SETTING',[]):
        f = reg.field(key)['layout']
        world.setdefault((f['group'],f['pointer_rva']),[]).append(key)
    for (group,rva),keys in world.items():
        sel = dict(target_kind='WORLD_SETTING',group=group,native_slot=hex(rva))
        groups.append(('WORLD_SETTING',sel,dict(group=group,native_slot=hex(rva)),max(reg.field(k)['layout']['offset']+4 for k in keys),keys))
    for tid in session.loc.teams:
        n = session.loc.profile['native']
        slot = (session.loc.managers[tid]-(session.loc.franchise+n['franchise_teams_offset']))//n['franchise_team_stride']
        groups.append(('TEAM_TRAINING',dict(target_kind='TEAM_TRAINING',team_id=tid),dict(team_id=tid,franchise_slot=slot,training_period='CURRENT'),88,by_kind['TEAM_TRAINING']))
        for p in session.players(tid):
            groups.append(('PLAYER_TRAINING',dict(target_kind='PLAYER_TRAINING',team_id=tid,player_identity=p['identity']['identity_tag']),p['identity'],796,by_kind['PLAYER_TRAINING']))
    for kind, selector, ident, size, keys in groups:
        try:
            obj = dict(selector=selector,identity=ident,field_keys=keys)
            raw = session.read(session.resolve(obj),size)
            add(selector,ident,raw,keys)
            coverage.setdefault(kind,dict(status='OBSERVED_SAME_SESSION',objects=0,missing=0))['objects'] += 1
        except (ValueError, RuntimeError) as exc:
            row = coverage.setdefault(kind,dict(status='NOT_OBSERVED',objects=0,missing=0))
            row['missing'] += 1
            row['reason'] = str(exc)
            row['status'] = 'PARTIALLY_OBSERVED' if row['objects'] else 'NOT_OBSERVED'
    coverage['MENTOR'] = dict(status='DISCOVERED',reason='RELATIONSHIP_CODEC_NOT_ADAPTED_BADGE_WRITES_EXCLUDED')
    coverage['PLAYBOOK_SLOT'] = dict(status='OBSERVED_SAME_SESSION',scope='ALL_SHARED_OWNERS',legal_targets='OBSERVED_LOADED_PLAY_CRCS')
    return objects,coverage
