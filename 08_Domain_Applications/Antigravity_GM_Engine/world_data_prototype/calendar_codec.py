"""Exact named Native calendar components; derived civil strings have no timezone."""
from datetime import date
import json
from pathlib import Path
PROFILE_PATH=Path(__file__).with_name('calendar_native_profile.json');PROFILE=json.loads(PROFILE_PATH.read_bytes())
LAYOUT='CURRENT_SEASON_CALENDAR_AND_GAME_HEADER_V1'
GAME_CAPACITY=PROFILE['array_dimensions']['SEASON_SCHEDULE']['Games'][0]
STAT_CAPACITY=PROFILE['array_dimensions'][PROFILE['bank_type']]['StatLine'][0]
DATE_FIELDS={'word_raw':32,'id_raw':5,'minutes_since_midnight_raw':11,'day_raw':5,'month_raw':4,'base_year_offset_raw':7}
DATE_TEXT=('month_label','native_iso_date','native_time_hhmm','decode_status')
GAME_FIELDS={'time_period_raw':'TimePeriod','game_type_raw':'Type','force_winner_raw':'ForceWinner','home_uniform_id_raw':'HomeUniformId','away_uniform_id_raw':'AwayUniformId',
    'was_simulated_raw':'WasSimulated','was_sim_to_end_raw':'WasSimToEnd','is_foreign_site_raw':'IsForeignSite','is_selected_raw':'IsSelected','is_nationally_televised_raw':'IsNationallyTelevised','overtime_count_raw':'OvertimeCount','attendance_raw':'Attendance'}
GAME_LABELS={'time_period_label':('time_period_raw','SEASON_TIMEPERIOD'),'game_type_label':('game_type_raw','SEASON_GAMETYPE'),'force_winner_label':('force_winner_raw','SIM_FORCE_WINNER_TYPE')}

def native_unsigned(raw,field):
    offset,size,shift,width=(field[k] for k in ('offset','size','start_bit','width'))
    if not 1<=width<=64 or offset+size>len(raw) or shift+width>size*8:raise ValueError('native calendar scalar outside record')
    return (int.from_bytes(raw[offset:offset+size],'little')>>shift)&((1<<width)-1)

def enum_label(type_name,code):return PROFILE['enum_labels'][type_name].get(str(code),{}).get('label')

def decode_date(raw):
    if len(raw)!=4:raise ValueError('native SCHEDULEDATE must have four bytes')
    b=PROFILE['bindings']['SCHEDULEDATE'];values={name:native_unsigned(raw,f) for name,f in b.items()};word=int.from_bytes(raw,'little');month=values['Month'];minutes=values['MinutesSinceMidnight'];iso=None
    if month<12:
        try:iso=date(PROFILE['year_epoch']+values['BaseYearOffset'],month+1,values['Day']).isoformat()
        except ValueError:pass
    status='DERIVED_NATIVE_COMPONENTS_EPOCH_2000; NO_UI_OR_TIMEZONE_ACCEPTANCE' if iso else 'INVALID_OR_UNSET_NATIVE_DATE; RAW_COMPONENTS_RETAINED'
    return {'word_raw':word,'id_raw':values['Id'],'minutes_since_midnight_raw':minutes,'day_raw':values['Day'],'month_raw':month,'month_label':enum_label('SCHEDULEDATE_MONTH',month),
        'base_year_offset_raw':values['BaseYearOffset'],'native_iso_date':iso,'native_time_hhmm':f'{minutes//60:02d}:{minutes%60:02d}' if iso and minutes<1440 else None,'decode_status':status}

def date_columns(raw,prefix):return {prefix+name:value for name,value in decode_date(raw).items()}

def game_calendar_fields(raw):
    if len(raw)!=60:raise ValueError('native SEASON_GAME must have60 bytes')
    b=PROFILE['bindings']['SEASON_GAME'];values={column:native_unsigned(raw,b[name]) for column,name in GAME_FIELDS.items()}
    values.update(date_columns(raw[b['Date']['offset']:b['Date']['offset']+4],'scheduled_'));values.update(date_columns(raw[b['PlayedDate']['offset']:b['PlayedDate']['offset']+4],'played_'))
    values.update({column:enum_label(type_name,values[source]) for column,(source,type_name) in GAME_LABELS.items()});values['status_label']=enum_label('SEASON_GAMESTATUS',native_unsigned(raw,b['Status']))
    return values
