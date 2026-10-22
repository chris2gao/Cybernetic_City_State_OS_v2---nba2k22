"""Read current coaching facts. Never captures a full data batch or publishes it."""
from datetime import datetime, timezone
import uuid
import zlib
from coach_codec import decode, block_key
from coach_locator import read_exact
from gm_core.coaching import validate_context
from gameplan_codec import decode_header

DEFENSE_NAMES = ("PressureOnball","PressureOffball","ForceDirection","ScreenDefenseOnBall",
    "ScreenDefenseHedge","OffballScreenDefense","PostDefense","DoubleTeamPerimeter",
    "DoubleTeamPost","ScreenDefenseOnBall5","ScreenDefenseHedge5","SwitchRule",
    "OnballHelp","ScreenHelp","ExtendPressure","TagOnRoll","StayAttached","PreRotate")

def decode_native(raw,field):
    off=field["offset"]
    bits=(field["format"]>>8)&255
    shift=(field["format"]>>16)&255
    size=max(field["size"],(shift+bits+7)//8)
    if off+size>len(raw) or not bits:
        raise RuntimeError("UNVERIFIED_NATIVE_BIT_LAYOUT")
    return (int.from_bytes(raw[off:off+size],"little")>>shift)&((1<<bits)-1)

def defensive_catalog(locator):
    """Exact native masks/raw enums. CRCs remain CRCs when labels are unavailable."""
    result={}
    for name in DEFENSE_NAMES:
        field=locator.defense_fields[zlib.crc32(name.encode())]
        bits=(field["format"]>>8)&255
        shift=(field["format"]>>16)&255
        values=locator.enum_table(field["enum_address"]) if field["enum_address"] else {}
        result[name]=dict(offset=field["offset"],storage_bytes=field["size"],start_bit=shift,width=bits,
                          mask=hex(((1<<bits)-1)<<(shift+field["offset"]*8)),
                          native_enum_name_crc32={str(raw):f"{crc:08x}" for raw,crc in values.items()},
                          readiness="LOCATED_READ_ONLY",production_enabled=False)
        expected=locator.profile.get('defensive_fields',{}).get(name)
        if expected:
            if any(result[name][key]!=expected[key] for key in ('offset','storage_bytes','start_bit','width','mask','native_enum_name_crc32')):
                raise RuntimeError('DEFENSIVE_NATIVE_PROFILE_CHANGED_'+name)
            result[name]['native_enum_labels']=expected['native_enum_labels']
            result[name]['readiness']=expected['readiness']
            result[name]['production_enabled']=expected['production_enabled']
        if name=='PreRotate':
            # 0x25 is the native bool kind (0x05) with packed-field flag 0x20.
            if ((field['format']>>24)&0x1f)!=5 or bits!=1 or field['enum_address']:
                raise RuntimeError('PREROTATE_NATIVE_BOOLEAN_LAYOUT_CHANGED')
            result[name]['native_boolean']=True
    return result

def gameplans(locator,tid):
    from coaching_overall import overall_from_raw
    n=locator.profile["native"]
    catalog=defensive_catalog(locator)
    result=[]
    for i in range(n["gameplan_capacity"]):
        raw=read_exact(locator.mem,locator.managers[tid]+n["gameplan_start"]+i*n["gameplan_stride"],
                       n["gameplan_stride"])
        header=decode_header(raw)
        owner=header["team_id"]
        opponent=header["opponent_team_id"]
        if owner==65535:
            continue
        if owner!=tid:
            raise RuntimeError("GAMEPLAN_OWNER_MISMATCH")
        if opponent==tid:
            raise RuntimeError("SELF_GAMEPLAN")
        if opponent not in locator.teams:
            continue
        values=header["values"]
        defenses=[]
        for j in range((0x178-0x64)//12):
            start=0x64+j*12
            data=raw[start+4:start+12]
            settings={}
            for name in DEFENSE_NAMES:
                field=locator.defense_fields.get(zlib.crc32(name.encode()))
                if not field:
                    raise RuntimeError("DEFENSIVE_FIELD_UNVERIFIED")
                value=decode_native(data,field)
                if field["enum_address"] and value not in locator.enum_table(field["enum_address"]):
                    raise RuntimeError("UNKNOWN_DEFENSIVE_ENUM")
                settings[name]=value
            defenses.append(dict(matchup_id=int.from_bytes(raw[start:start+2],"little"),
                                 defender_id=int.from_bytes(raw[start+2:start+4],"little"),
                                 values=settings,readiness="LOCATED_READ_ONLY"))
        rotations=[dict(player_id=int.from_bytes(raw[6+j*4:8+j*4],"little"),
                        rotation_spot=raw[8+j*4],playing_time_raw=raw[9+j*4])
                   for j in range((0x64-6)//4)]
        result.append(dict(opponent_team_id=opponent,is_in_use=raw[0],is_tainted=raw[1],
                           values=values,defensive_matchups=defenses,rotations=rotations,
                           overall_defense=overall_from_raw(raw,locator.profile['opponent_overall_defense'],catalog),
                           readiness=locator.profile['opponent_overall_defense']['readiness'],
                           player_identity_status="GROUP_IDS_AND_CAPTURE_ROSTER_BOUND_INDIVIDUAL_WRITES_NOT_EXPOSED"))
    opponents=[r["opponent_team_id"] for r in result]
    if len(set(opponents))!=len(opponents) or set(opponents)!=set(locator.teams)-{tid}:
        raise RuntimeError("MISSING_OR_DUPLICATE_OPPONENT_GAMEPLAN")
    return sorted(result,key=lambda r:r["opponent_team_id"])

def coaching_snapshot(locator,context,environment="FORMAL_READ_ONLY",allow_unknown_date=False):
    if environment not in ("FORMAL_READ_ONLY","ISOLATED_TEST"):
        raise ValueError("UNKNOWN_SNAPSHOT_ENVIRONMENT")
    context=validate_context(context,environment=="ISOLATED_TEST" or allow_unknown_date)
    identity=locator.context_identity()
    rows=[]
    fields=locator.profile["fields"]
    for tid,c in sorted(locator.coaches.items()):
        raw=read_exact(locator.mem,c["address"],0x160)
        blocks={block_key(f["offset"],f["storage_bytes"]):
                raw[f["offset"]:f["offset"]+f["storage_bytes"]].hex() for f in fields.values()}
        values={name:decode(raw,f) for name,f in fields.items()}
        for name,value in values.items():
            enum=fields[name].get("enum")
            if isinstance(enum,dict) and str(value) not in enum:
                raise RuntimeError("UNKNOWN_NATIVE_ENUM_"+name)
            if enum=="LOADED_PLAYBOOKS" and value not in {p["enum_id"] for p in locator.playbooks}:
                raise RuntimeError("COACH_PLAYBOOK_NOT_LOADED")
        rows.append(dict(team_id=tid,abbreviation=locator.teams[tid]["abbreviation"],
                         coach_identity=c["identity"],roster_signature=c["roster_signature"],
                         values=values,blocks=blocks,gameplans=gameplans(locator,tid),
                         readiness={name:f["readiness"] for name,f in fields.items()},
                         freelance_sets=[values[n] for n in locator.profile['freelance_slot_order']]))
    if locator.context_identity()!=identity:
        raise RuntimeError("CONTEXT_CHANGED_DURING_SNAPSHOT")
    from coaching_targets import process_binding
    return dict(schema_version=1,snapshot_id=uuid.uuid4().hex,**context,
                observed_at=datetime.now(timezone.utc).isoformat(),
                observation_status="OBSERVED_LIVE_READ_ONLY",environment=environment,
                context_origin="PLAYER_SUPPLIED_SAVE_AND_DATE_WITH_LIVE_IDENTITY_CHECKS",
                codec_version=locator.profile["codec_version"],
                effect_status="SIM_EFFECT_PENDING_PLAYER_MONTH",
                process_pid=locator.mem.pid,process_creation_time=locator.mem.creation_time,native_evidence=locator.evidence,
                process_binding=process_binding(locator.mem.pid,locator.mem.creation_time),
                defensive_field_catalog=defensive_catalog(locator),
                context_identity=identity,teams=rows,playbooks=locator.playbooks,
                loaded_playbook_ids=sorted(p["enum_id"] for p in locator.playbooks if p["selectable"]))
