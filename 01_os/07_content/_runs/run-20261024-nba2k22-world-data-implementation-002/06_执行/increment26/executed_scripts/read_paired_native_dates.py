"""Clarify two differently named Native date fields without inventing UI meaning."""
from datetime import datetime,timezone
import hashlib,json,sys
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).resolve().parent;dest=runtime.parent/'06_执行/increment26';sys.path.insert(0,str(repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'))
from live_reader import ReadOnlyGameProcess,SEASON_RVA
from game_mode_reader import PROFILE,verify_game_mode_metadata,decode_game_mode
from calendar_reader import verify_calendar_metadata
from calendar_codec import decode_date,enum_label
from refresh import _context
from live_world import _json
pid=int(sys.argv[1]);reader=None;report={'observed_at':datetime.now(timezone.utc).isoformat(),'pid':pid,'game_writes':False,'getter_invocations':0}
try:
    report['context_before']=_context(pid);reader=ReadOnlyGameProcess(pid);verify_game_mode_metadata(reader);verify_calendar_metadata(reader);controls=[]
    def read(address,size,label):
        raw=reader.read(address,size,label);controls.append((address,raw,label));return raw
    mp=read(reader.module_base+PROFILE['game_mode_pointer_rva'],8,'PAIRED_GAME_MODE_POINTER');sp=read(reader.module_base+SEASON_RVA,8,'PAIRED_SEASON_POINTER')
    mode=read(int.from_bytes(mp,'little'),24,'PAIRED_GAME_MODE_PUBLIC_PREFIX');season=read(int.from_bytes(sp,'little'),8,'PAIRED_SEASON_DATE_AND_PERIOD')
    for address,raw,label in controls:
        if reader.read(address,len(raw),label+':RECHECK')!=raw:raise ValueError('paired source changed')
    report.update({'status':'CURRENT_PAIRED_NAMED_NATIVE_DATE_FIELDS_CAPTURED','game_mode_today':decode_date(mode[20:24]),'season_date':decode_date(season[:4]),'game_mode_period':decode_game_mode(mode)['period_label'],'season_period':enum_label('SEASON_TIMEPERIOD',int.from_bytes(season[4:8],'little')),'mode_prefix_hex':mode.hex(),'season_prefix_hex':season.hex(),'interpretation':'Distinct named fields in one rechecked acquisition; difference is observed. UI display, date progression and a fixed offset contract are not inferred.'});reader.close();report['context_after']=_context(pid)
    if report['context_before']['epoch']!=report['context_after']['epoch']:raise ValueError('paired process/build/year changed')
except Exception as error:report.update({'status':'PAIRED_NATIVE_DATE_CAPTURE_FAILED','reason':str(error),'error_type':type(error).__name__})
finally:
    if reader:reader.close()
report['read_trace']=reader.trace if reader else [];_json(dest/'paired-native-dates.json',report)
