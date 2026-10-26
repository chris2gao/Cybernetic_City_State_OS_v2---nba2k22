import hashlib,json,mmap,re,struct,zlib
from pathlib import Path
repo=Path.cwd();runtime=Path(__file__).parent;app=repo/'08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype'
metadata=json.loads((runtime/'finance-metadata-labeled.json').read_bytes())[0]
entry=json.loads((runtime/'finance-metadata-01/type_entries.json').read_bytes())[0]
entry.update(expected_size=4696,expected_field_count=metadata['field_count'],field_signature_sha256=hashlib.sha256(json.dumps(sorted((f['name_crc'],f['offset'],f['size'],f['format'],f['words'][5]) for f in metadata['fields']),separators=(',',':')).encode()).hexdigest())
types=[entry]+json.loads((runtime/'finance-metadata-02/type_entries.json').read_bytes());enums=json.loads((runtime/'finance-metadata-02/metadata.json').read_bytes());wanted={v['name_crc'] for e in enums for v in e['values']};labels={}
unsigned={'Salary':'salary_raw','MetroPopulation':'metro_population_raw','MetroIncome':'metro_income_raw','TVHomes':'tv_homes_raw'}
signed_names='PromoYearlyExpense OperationsYearlyExpense FacilitiesYearlyExpense GameDayExpense RevGate RevMerch RevConcession RevMedia RevAdvertising RevLeague RevPlayoffs ExpPayroll ExpGameDay ExpPromo ExpStaff ExpOperations ExpSalaryTax ExpPlayoffs BankBalance PlayerBudget StaffBudget DeltaBudget'.split()
float_names='Buzz BaselineFanDemand TicketPrice ParkingPrice HotDogPrice SodaPrice BurgerPrice CoffeePrice NachosPrice IceCreamPrice RestaurantPrice ProgramPrice HatPrice SouvenirPrice CityTaxBreak'.split()
def snake(s):return re.sub(r'(?<!^)(?=[A-Z])','_',s).lower()
scalars={n:{'column':c,'primitive':'u32'} for n,c in unsigned.items()}
scalars.update({n:{'column':snake(n)+'_raw','primitive':'int'} for n in signed_names})
scalars.update({n:{'column':snake(n),'primitive':'float'} for n in float_names})
packed={'IsLuxuryTaxTeam':{'column':'is_luxury_tax_team_raw','primitive':'bool32'},'Facilities_LuxurySuites_Level':{'column':'facility_luxury_suites_raw','primitive':'enum','enum':'TEAMDATA_FACILITY_LEVEL'},'Facilities_Parking_Level':{'column':'facility_parking_raw','primitive':'enum','enum':'TEAMDATA_FACILITY_LEVEL'},'BudgetTier':{'column':'budget_tier_raw','primitive':'enum','enum':'TEAMDATA_BUDGET_TIER'}}
identity={'Id':{'column':'native_team_id','primitive':'u16'},'UnlocalizedTeamName':{'primitive':'char16','extent':25},'UnlocalizedCityName':{'primitive':'char16','extent':18},'UnlocalizedShortTeamName':{'primitive':'char16','extent':7}}
fields={n:next(f for f in metadata['fields'] if f['literal_names']==[n]) for n in scalars|packed|identity}
with Path('E:/games/NBA 2K22/NBA2K22.exe').open('rb') as stream,mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as data:
    pe=struct.unpack_from('<I',data,60)[0];count=struct.unpack_from('<H',data,pe+6)[0];start=pe+24+struct.unpack_from('<H',data,pe+20)[0]
    sections=[struct.unpack_from('<IIII',data,start+i*40+8) for i in range(count)]
    def read(rva,size):
        for vs,va,rs,off in sections:
            if va<=rva and rva+size<=va+rs:return bytes(data[off+rva-va:off+rva-va+size])
        raise ValueError('RVA not present')
    for match in re.finditer(rb'(?<=\x00)[A-Za-z_][A-Za-z0-9_:]{0,95}\x00',data):
        raw=match.group()[:-1];crc=zlib.crc32(raw)
        if crc in wanted:labels.setdefault(crc,set()).add(raw.decode())
    for name,spec in identity.items():
        if 'extent' in spec:
            f=fields[name];ptr=f['words'][6]|f['words'][7]<<32;dim=read(ptr-0x140000000,24)
            assert f['words'][5]>>16==1 and struct.unpack_from('<I',dim)[0]==spec['extent'],(name,f['words'],dim.hex(),spec['extent'])
            spec['dimension_control_hex']=dim.hex()
for name,spec in (scalars|packed|identity).items():
    f=fields[name];spec['binding']=f
    if spec['primitive']!='enum':assert f['primitive_literal_candidates']==[spec['primitive']],(name,f['primitive_literal_candidates'])
enum_labels={}
for e in enums:
    enum_labels[e['name']]={}
    for v in e['values']:
        candidates=sorted(labels.get(v['name_crc'],[]));assert len(candidates)==1,(e,v,candidates)
        enum_labels[e['name']][str(v['value'])]={'label':candidates[0],'name_crc':v['name_crc']}
profile={'layout':'NATIVE_TEAM_FINANCE_TYPED_V1','struct_size':4696,'types':types,'scalars':scalars,'packed':packed,'identity':identity,'enum_labels':enum_labels,'units':'Native representation; monetary scale, UI presentation, legal ranges, accounting duration and CBA arithmetic unproved','legacy_aliases':{'total_salary_raw':'Salary/u32','payroll_raw':'ExpPayroll/int stored as unsigned legacy word','cash_raw':'BankBalance/int stored as unsigned legacy word','budget_raw':'PlayerBudget/int stored as unsigned legacy word','staff_budget_raw':'StaffBudget/int stored as unsigned legacy word','gate_revenue_raw':'RevGate/int stored as unsigned legacy word','merch_revenue_raw':'RevMerch/int stored as unsigned legacy word','media_revenue_raw':'RevMedia/int stored as unsigned legacy word'}}
(app/'finance_native_profile.json').write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'scalar_fields':len(scalars),'packed_fields':len(packed),'identity_fields':len(identity),'enum_labels':enum_labels}))
