"""Current-process native metadata and owner resolution. No game writes."""
import hashlib
import struct
import zlib
from coach_codec import decode, load_profile

def read_exact(mem, address, size):
    raw = mem.read_bytes(address, size)
    if raw is None or len(raw) != size:
        raise RuntimeError("UNREADABLE_COACHING_MEMORY")
    return raw

def u64(mem, address):
    return int.from_bytes(read_exact(mem,address,8),"little")

def live_memory(read_only=True):
    from memory import GameMemory
    mem = GameMemory(read_only=read_only)
    return attach_process_identity(mem)


def attach_process_identity(mem):
    import win32process
    mem.is_alive = lambda: win32process.GetExitCodeProcess(mem.handle) == 259
    mem.creation_time=str(win32process.GetProcessTimes(mem.handle)["CreationTime"])
    return mem

class CoachLocator:
    def __init__(self, mem, profile=None):
        self.mem, self.profile = mem, profile or load_profile()
        self.teams, self.directory = {}, {}
        self.coaches, self.managers = {}, {}
        self.native_fields, self.defense_fields, self.enum_tables = {}, {}, {}

    def alive(self):
        if not self.mem.is_alive():
            raise RuntimeError("STALE_PID")
        return (self.mem.pid,self.mem.base_address)

    def rip_pointer(self,rva,prefix,ret=False):
        address = self.mem.base_address+rva
        raw = read_exact(self.mem,address,8)
        if raw[:3] != bytes.fromhex(prefix) or (ret and raw[7] != 0xc3):
            raise RuntimeError("NATIVE_GETTER_VERSION_MISMATCH")
        return u64(self.mem,address+7+struct.unpack_from("<i",raw,3)[0])

    def type_fields(self,rva,name,size):
        h = struct.unpack("<8Q",read_exact(self.mem,self.mem.base_address+rva,64))
        if not 0<h[0]<2000 or read_exact(self.mem,h[5],len(name)+1) != name.encode()+b"\0":
            raise RuntimeError("NATIVE_TYPE_NAME_MISMATCH")
        schema = struct.unpack("<10I",read_exact(self.mem,h[4],40))
        if schema[5] != size:
            raise RuntimeError("NATIVE_TYPE_SIZE_MISMATCH")
        raw = read_exact(self.mem,h[1],h[0]*40)
        result={}
        for i in range(h[0]):
            w=struct.unpack_from("<10I",raw,i*40)
            if w[0] in result:
                raise RuntimeError("DUPLICATE_NATIVE_FIELD")
            result[w[0]]=dict(offset=w[2],size=w[3],format=w[4],
                              enum_address=w[8]|w[9]<<32)
        return result

    def enum_table(self,address):
        if address in self.enum_tables:
            return self.enum_tables[address]
        h=struct.unpack("<6Q",read_exact(self.mem,address,48))
        if not 0<h[2]<=300:
            raise RuntimeError("NATIVE_ENUM_DESCRIPTOR_INVALID")
        raw=read_exact(self.mem,h[3],h[2]*12)
        table={}
        for i in range(h[2]):
            hashed,value,_=struct.unpack_from("<IiI",raw,i*12)
            if value in table:
                raise RuntimeError("DUPLICATE_NATIVE_ENUM")
            table[value]=hashed
        self.enum_tables[address]=table
        return table

    def verify_native(self):
        n=self.profile["native"]
        fields=self.type_fields(n["coach_type_rva"],"COACHDATA",0x160)
        self.native_fields=fields
        for name,f in self.profile["fields"].items():
            native=fields.get(zlib.crc32(name.encode()))
            if (native is None or native["offset"]!=f["offset"]
                    or ((native["format"]>>16)&255)!=f["start_bit"]
                    or ((native["format"]>>8)&255)!=f["width"]):
                raise RuntimeError("NATIVE_FIELD_LAYOUT_MISMATCH_"+name)
            if f.get("enum_rva") is not None:
                expected=self.mem.base_address+f["enum_rva"]
                if native["enum_address"]!=expected:
                    raise RuntimeError("NATIVE_ENUM_POINTER_MISMATCH")
                table=self.enum_table(expected)
                if isinstance(f["enum"],dict):
                    if any(table.get(int(v))!=zlib.crc32(label.encode()) for v,label in f["enum"].items()):
                        raise RuntimeError("NATIVE_ENUM_LABEL_MISMATCH")
        self.gameplan_fields=self.type_fields(n["gameplan_type_rva"],"GAMEPLAN",n["gameplan_stride"])
        self.defense_fields=self.type_fields(n["defense_type_rva"],"GAMEPLAN_MATCHUP_DEFENSIVE_SETTINGS",8)
        self.playbook_fields=self.type_fields(n["playbook_type_rva"],"PLAYBOOKDATA",n["playbook_stride"])
        # Native PLAYBOOKDATA enum-reference field (name CRC retained until its
        # text label is recovered). Check its layout and enum identity as well.
        book_id=self.playbook_fields.get(0x2abd43f2)
        if (not book_id or book_id["offset"]!=0x54 or book_id["size"]!=1
                or ((book_id["format"]>>16)&255)!=0 or ((book_id["format"]>>8)&255)!=7
                or book_id["enum_address"]!=self.mem.base_address+self.profile["fields"]["PlaybookID"]["enum_rva"]):
            raise RuntimeError("NATIVE_PLAYBOOK_ID_LAYOUT_MISMATCH")
        # Each byte-level Gameplan location is verified independently of packed COACHDATA.
        gp_expected={"TeamId":(2,2),"OpponentId":(4,2),"IsInUse":(0,1),
                     "IsTainted":(1,1),"MatchupGameplan":(0x64,12),"ScoringOption":(0x178,2),
                     "POEOffense":(0x17e,1),"POEDefense":(0x181,1),
                     "HelpDefense":(0x184,1),"RunPlayTendency":(0x185,1),
                     "ZoneUsage":(0x186,1),"BenchDepth":(0x187,1),
                     "BenchUtilization":(0x188,1),"LineupFormFactor":(0x189,1),
                     "PlaybookId":(0x18a,1),"FreelanceType":(0x18b,1)}
        for name,(off,size) in gp_expected.items():
            f=self.gameplan_fields.get(zlib.crc32(name.encode()))
            if not f or (f["offset"],f["size"])!=(off,size):
                raise RuntimeError("NATIVE_GAMEPLAN_LAYOUT_MISMATCH")
        pe_off=int.from_bytes(read_exact(self.mem,self.mem.base_address+0x3c,4),"little")
        if not 64<=pe_off<=4096:
            raise RuntimeError("MODULE_PE_HEADER_INVALID")
        pe=read_exact(self.mem,self.mem.base_address+pe_off,0x60)
        if pe[:4]!=b"PE\0\0" or int.from_bytes(pe[4:6],"little")!=0x8664:
            raise RuntimeError("MODULE_PE_VERSION_MISMATCH")
        return {"status":"VERIFIED_CURRENT_PROCESS_NATIVE_METADATA",
                "evidence_version":self.profile["evidence_version"],
                "coach_field_count":len(fields),"defense_field_count":len(self.defense_fields),
                "module_timestamp":int.from_bytes(pe[8:12],"little"),
                "module_image_size":int.from_bytes(pe[0x50:0x54],"little")}

    def calibrate(self):
        self.alive()
        from source_extensions import roster_directory
        import config
        n=self.profile["native"]
        self.roster=self.rip_pointer(n["roster_getter_rva"],"488b05",True)
        self.franchise=self.rip_pointer(n["franchise_load_rva"],"488b1d")
        if not self.roster or not self.franchise:
            raise RuntimeError("WRONG_ACTIVE_ROSTER_OR_FRANCHISE")
        self.root=self.roster-8
        # Follow the verified native active-roster getter, never a cached heap or
        # fixed historic player slot. Custom rosters can replace the Jordan anchor.
        self.directory=roster_directory(self.mem,self.root)
        count=u64(self.mem,self.root+0x88)
        first=u64(self.mem,self.root+0x90)
        end=u64(self.mem,self.root+0xa0)
        if not 30<=count<=1000 or first+count*config.TEAM_STRUCT_STRIDE!=end:
            raise RuntimeError("INVALID_NATIVE_TEAM_DIRECTORY")
        self.teams={}
        for index in range(count):
            address=first+index*config.TEAM_STRUCT_STRIDE
            raw=read_exact(self.mem,address,config.TEAM_STRUCT_STRIDE)
            tid=int.from_bytes(raw[0xca8:0xcaa],"little")
            if tid not in config.CORE_TEAM_IDS:
                continue
            if tid in self.teams:
                raise RuntimeError("DUPLICATE_CORE_TEAM_ID")
            row={"team_id":tid,"address":address}
            for key,size in (("TEAM_NAME",40),("CITY",40),("ABB",10)):
                off=config.TEAM_OFFSETS[key]
                row[{"TEAM_NAME":"name","CITY":"city","ABB":"abbreviation"}[key]]=raw[off:off+size].decode("utf-16le").split("\0")[0]
            if not row["name"] or not row["city"] or len(row["abbreviation"]) not in (2,3):
                raise RuntimeError("INVALID_CORE_TEAM_IDENTITY")
            self.teams[tid]=row
        if set(self.teams)!=config.CORE_TEAM_IDS or len({t["abbreviation"] for t in self.teams.values()})!=30:
            raise RuntimeError("CORE_TEAM_SET_MISMATCH")
        self.evidence=self.verify_native()
        self.resolve_coaches()
        self.resolve_managers()
        self.playbooks=self.read_playbooks()
        self.alive()
        return self

    def resolve_coaches(self):
        from source_extensions import staff_details
        used=set()
        for tid,team in self.teams.items():
            address=u64(self.mem,team["address"]+0xce8)
            table=self.directory["staff"]
            slot,rem=divmod(address-table["address"],table["stride"])
            if rem or not 0<=slot<table["count"] or address in used:
                raise RuntimeError("INVALID_OR_DUPLICATE_HEAD_COACH")
            detail,raw=staff_details(self.mem,address+0x30,slot,self.teams)
            if (detail["team_id"]!=tid or detail["fields"]["vitals"]["position"]["value"]!=0
                    or detail["team_mapping_status"]!="VERIFIED_RECIPROCAL_TEAM_ROLE"):
                raise RuntimeError("COACH_ROLE_OR_TEAM_MISMATCH")
            used.add(address)
            # Do not include mutable tactics or runtime pointers in person identity.
            native_id=self.native_fields.get(zlib.crc32(b"UniqueId"))
            identity_bytes=raw[0x30:0x80]
            if native_id:
                off=native_id["offset"]
                identity_bytes+=raw[off:off+4]
            identity=dict(team_id=tid,staff_slot=slot,first_name=detail["first_name"],
                          last_name=detail["last_name"],role="HEAD_COACH",
                          identity_tag=hashlib.sha256(identity_bytes).hexdigest())
            self.coaches[tid]=dict(address=address,identity=identity,raw=raw,
                                  roster_signature=self.roster_signature(team))

    def roster_signature(self,team):
        table=self.directory["players"]
        members=[]
        for offset in range(0,0xc8,8):
            ptr=u64(self.mem,team["address"]+offset)
            if not ptr:
                continue
            slot,rem=divmod(ptr-table["address"],table["stride"])
            if rem or not 0<=slot<table["count"]:
                raise RuntimeError("ROSTER_PLAYER_OUTSIDE_CURRENT_POOL")
            raw=read_exact(self.mem,ptr,0x70)
            if int.from_bytes(raw[0x60:0x68],"little")!=team["address"] or slot in [m[0] for m in members]:
                raise RuntimeError("ROSTER_PLAYER_IDENTITY_OR_TEAM_MISMATCH")
            members.append((slot,raw[:0x50].hex(),raw[0x6c:0x6e].hex()))
        if not members:
            raise RuntimeError("EMPTY_ROSTER_IDENTITY")
        return hashlib.sha256(repr(members).encode()).hexdigest()

    def resolve_managers(self):
        n=self.profile["native"]
        for slot in range(n["franchise_capacity"]):
            addr=self.franchise+n["franchise_teams_offset"]+slot*n["franchise_team_stride"]
            tid=int.from_bytes(read_exact(self.mem,addr,2),"little")
            if tid not in self.teams:
                continue
            if tid in self.managers:
                raise RuntimeError("DUPLICATE_GAMEPLAN_MANAGER")
            self.managers[tid]=addr
        if set(self.managers)!=set(self.teams):
            raise RuntimeError("MISSING_GAMEPLAN_MANAGER")

    def read_playbooks(self):
        n=self.profile["native"]
        count=u64(self.mem,self.roster+n["playbook_count_offset"])
        base=u64(self.mem,self.roster+n["playbook_pointer_offset"])
        end=u64(self.mem,self.roster+n["playbook_end_offset"])
        if not 0<count<=4096 or base+count*n["playbook_stride"]!=end:
            raise RuntimeError("INVALID_PLAYBOOK_DIRECTORY")
        result=[]
        for idx in range(count):
            raw=read_exact(self.mem,base+idx*n["playbook_stride"],n["playbook_stride"])
            result.append(dict(index=idx,name=raw[:0x38].decode("utf-16le").split("\0")[0],
                               unique_id=int.from_bytes(raw[0x3e:0x40],"little"),
                               enum_id=raw[0x54]&127,
                               play_crc_slots=list(struct.unpack_from("<68I",raw,0x58))))
            result[-1]["selectable"]=bool(result[-1]["name"])
        ids=[p["enum_id"] for p in result]
        valid=self.enum_table(self.mem.base_address+self.profile["fields"]["PlaybookID"]["enum_rva"])
        if len(set(ids))!=len(ids) or any(p["enum_id"] not in valid for p in result):
            raise RuntimeError("AMBIGUOUS_OR_UNKNOWN_LOADED_PLAYBOOK")
        return result

    def context_identity(self):
        from source_extensions import staff_details
        self.alive()
        # Re-read roots, owner links and roster signatures immediately before any write.
        n=self.profile["native"]
        if (self.rip_pointer(n["roster_getter_rva"],"488b05",True)!=self.roster
                or self.rip_pointer(n["franchise_load_rva"],"488b1d")!=self.franchise):
            raise RuntimeError("ACTIVE_SAVE_CONTEXT_CHANGED")
        for tid,coach in self.coaches.items():
            if int.from_bytes(read_exact(self.mem,self.teams[tid]["address"]+0xca8,2),"little")!=tid:
                raise RuntimeError("TEAM_ID_CHANGED")
            if u64(self.mem,self.teams[tid]["address"]+0xce8)!=coach["address"]:
                raise RuntimeError("COACH_CHANGED")
            if u64(self.mem,coach["address"]+0x18)!=self.teams[tid]["address"]:
                raise RuntimeError("COACH_TEAM_CHANGED")
            detail,raw=staff_details(self.mem,coach["address"]+0x30,coach["identity"]["staff_slot"],self.teams)
            native_id=self.native_fields.get(zlib.crc32(b"UniqueId"))
            identity_bytes=raw[0x30:0x80]
            if native_id:
                identity_bytes+=raw[native_id["offset"]:native_id["offset"]+4]
            if (detail["team_id"]!=tid or detail["fields"]["vitals"]["position"]["value"]!=0
                    or detail["team_mapping_status"]!="VERIFIED_RECIPROCAL_TEAM_ROLE"
                    or hashlib.sha256(identity_bytes).hexdigest()!=coach["identity"]["identity_tag"]):
                raise RuntimeError("COACH_IDENTITY_OR_ROLE_CHANGED")
            if self.roster_signature(self.teams[tid])!=coach["roster_signature"]:
                raise RuntimeError("ROSTER_CHANGED")
        return {str(tid):dict(coach_identity=c["identity"],roster_signature=c["roster_signature"])
                for tid,c in self.coaches.items()}

    def close(self):
        self.mem.close()
