"""Static enum joins, explicit contract encoding, and actual read handler in a fake pool."""
import json
import shutil
import struct
import subprocess
import sys
import unittest
from pathlib import Path

CONTROL=Path(__file__).resolve().parents[1]
ROOT=CONTROL.parents[3]
RUN=ROOT/'01_os/07_content/_runs/run-20261028-role-native-execution-system-001'
sys.path.insert(0,str(CONTROL))
from contracts import NativeActionRequest,Outcome
from facade import NativeControlFacade
from readers import NativeReadCatalog,NativeReadFacade,NativeReadQuery
from signing_fields import decode_record,encode_explicit_contract,load_schema,validate_pool_query
from role_capabilities import RoleCapabilityProfile,RoleCapabilityService

ACTION='READ_TEAM_SIGNING_OFFERS'
DATASET='signing.team_offers'


class SigningContract(unittest.TestCase):
    def setUp(self):self.facade=NativeControlFacade();self.schema=load_schema()

    def terms(self,**changes):
        return {'signing_type':'FREE_AGENT','annual_wages_native':[101,202,303,404,0,0],
            'years_native':4,'option_type':'PLAYER_OPTION','contract_type':'NORMAL',
            'distribution':'CUSTOM','no_trade_clause':False,**changes}

    def query(self,**changes):return {'team_id':20,'statuses':['OFFERED','ACCEPTED','SIGNED'],'include_archived':0,**changes}

    def record(self,*,team=20,player=55,status=1,archived=0,type=2,distribution=0,index=0,wages=None,**flags):
        # Independent raw fixture uses explicit registered offsets, not the codec.
        raw=bytearray(44);struct.pack_into('<HHI6I',raw,0,player,team,123,*(wages or [1,2,3,4,5,6]))
        struct.pack_into('<I',raw,32,(type<<22)|(status<<18)|(distribution<<25)|0xf9|(7<<8)|
                         (1<<12)|(1<<13)|(1<<14)|(1<<15)|(1<<16)|(1<<17)|(2<<28)|(3<<30))
        raw[36:40]=bytes([11,22,33,44]);struct.pack_into('<I',raw,40,55|(4<<8)|(archived<<11)|(1<<12)|0xace00000)
        return {'index':index,'hex':raw.hex()}

    def simulate(self,records,query=None,*,compile=True,**options):
        p=self.query() if query is None else query
        if compile:self.facade.render(NativeActionRequest(ACTION,p))
        action=self.facade.registry.get(ACTION)
        bindings={row['binding_id']:self.facade.registry.binding(row['binding_id']).to_dict() for row in action['call_sequence']}
        result=subprocess.run([shutil.which('node'),str(CONTROL/'tests/signing_offers_harness.js'),str(CONTROL/'runtime/read_signing_offers.js')],
            input=json.dumps({'request':{'action_id':ACTION,'parameters':p},'bindings':bindings,'records':records,'options':options}),
            text=True,capture_output=True,check=True,timeout=10)
        return json.loads(result.stdout)

    def test_all_five_native_enum_tables_join_to_registered_field_type_and_unique_names(self):
        source=json.loads((RUN/'static/sign_native_enums_007.json').read_text(encoding='utf8'))
        registered=json.loads((CONTROL/'evidence/static/types-signing-02.json').read_text(encoding='utf8'))
        fields=next(row for row in registered['types'] if row['name']=='FRANCHISE_SIGNING')['fields']
        by_descriptor={row['descriptor_rva']:row for row in source['enums']}
        prefixes={'Status':'FRANCHISE_SIGNING_STATUS_','Type':'FRANCHISE_SIGNING_'}
        self.assertFalse(source['game_access']);self.assertEqual(len(self.schema['fields']),25)
        self.assertEqual(sum(len(row['rows']) for row in source['enums']),27)
        decoded={row['name']:row for row in self.schema['fields']}
        for field in fields:
            row=decoded[field['name_candidates'][0]]
            self.assertEqual((row['offset'],row['width'],row['shift']),
                (field['offset'],(field['format']>>8)&255,(field['format']>>16)&255))
        for field in fields:
            if field['image_ref_rvas'][1] is None:continue
            name=field['name_candidates'][0];enum=by_descriptor[field['image_ref_rvas'][1]]
            self.assertEqual(field['type_crc'],enum['info_raw'][0])
            self.assertTrue(enum['absolute_entry_pointer_references'])
            self.assertTrue(all(row['name_candidates']==[row['name']] for row in enum['rows']))
            expected={str(row['value']):row['name'].removeprefix(prefixes.get(name,'')) for row in enum['rows']}
            self.assertEqual(expected,self.schema['enums'][name])
        self.assertEqual(self.schema['enums']['Status']['6'],'ACCEPTED')
        self.assertEqual(self.schema['enums']['Status']['8'],'SIGNED')
        self.assertEqual(bytes.fromhex(self.schema['forced_wage_extent_proof']['static_array_info_hex'])[:4],struct.pack('<I',6))

    def test_decode_preserves_all_field_neighbors_six_wages_and_signed_negotiation_byte(self):
        row=decode_record(bytes.fromhex(self.record()['hex']))
        self.assertEqual((row['PlayerId'],row['TeamId'],row['Wage']),(55,20,123))
        self.assertEqual(row['ForcedWage'],[1,2,3,4,5,6]);self.assertEqual(row['PissedOffLevel'],-7)
        self.assertEqual((row['Status'],row['Type'],row['Distribution'],row['OptionType'],row['ContractType']),(1,2,0,2,3))
        self.assertEqual([row[name] for name in ['NoTradeClause','RecentOffer','IsCounterOffer','IsExistingOffer','ForcedOffer','HasMadeVerbalDeal']],[1]*6)
        self.assertEqual([row[name] for name in ['IntSalary','IntTerm','IntWinner','IntRole','IntCity','Years','IsUserInitiated']],[11,22,33,44,55,4,1])
        for raw in [b'',bytes(43),bytes(45)]:
            with self.assertRaises(ValueError):decode_record(raw)

    def test_explicit_private_encoding_matches_independent_bytes_and_never_marks_offer_accepted(self):
        raw=encode_explicit_contract(321,20,self.terms(no_trade_clause=True))
        expected=bytearray(44);struct.pack_into('<HHI6I',expected,0,321,20,101,101,202,303,404,0,0)
        struct.pack_into('<I',expected,32,(2<<22)|(2<<28)|(1<<12));struct.pack_into('<I',expected,40,4<<8)
        self.assertEqual(raw,bytes(expected))
        fields=decode_record(raw)
        for name in ['Status','IsExistingOffer','RecentOffer','ForcedOffer','HasMadeVerbalDeal','IsArchived','IsUserInitiated']:
            self.assertEqual(fields[name],0)
        self.assertFalse(self.schema['maturity']['fresh_offer_lifecycle_qualified'])
        self.assertFalse(self.schema['maturity']['dispatch_implemented'])

    def test_private_encoding_rejects_implicit_terms_unknown_enums_and_representation_overflow(self):
        invalid=[self.terms(annual_wages_native=[1]),self.terms(annual_wages_native=[True]*6),
            self.terms(annual_wages_native=[2**32]*6),self.terms(annual_wages_native=[-1]*6),self.terms(years_native=True),
            self.terms(years_native=8),self.terms(option_type='invented'),self.terms(no_trade_clause=1),self.terms(extra=1)]
        incomplete=self.terms();del incomplete['distribution'];invalid.append(incomplete)
        for terms in invalid:
            with self.assertRaises(ValueError):encode_explicit_contract(55,20,terms)
        for player,team in [(65535,20),(55,65535),(True,20),(-1,20)]:
            with self.assertRaises(ValueError):encode_explicit_contract(player,team,self.terms())
        # Encoding extrema are accepted as extrema, not certified game-legal terms.
        raw=encode_explicit_contract(65534,65534,self.terms(years_native=7,annual_wages_native=[2**32-1]*6))
        self.assertEqual(decode_record(raw)['ForcedWage'],[2**32-1]*6)

    def test_reader_emits_selected_team_status_and_archive_only_without_game_calls_or_raw_bytes(self):
        rows=[self.record(index=0,status=0),self.record(index=1,status=6),self.record(index=2,status=8),
              self.record(index=3,status=1,archived=1),self.record(index=4,status=8,team=21),
              self.record(index=5,status=10),self.record(index=6,status=1,player=65535)]
        result=self.simulate(rows)
        self.assertIsNone(result['error']);self.assertEqual(result['gameCalls'],0);self.assertTrue(result['unchanged'])
        self.assertEqual(result['poolReads'],2000)
        details=result['messages'][0]['details'];offers=details['data']['offers']
        self.assertEqual([row['record_index'] for row in offers],[1,2,6])
        self.assertEqual([row['enums']['Status']['name'] for row in offers],['ACCEPTED','SIGNED','OFFERED'])
        self.assertIsNone(offers[-1]['player_id']);self.assertFalse(offers[-1]['player_identity_resolved'])
        self.assertEqual(offers[0]['fields'],decode_record(bytes.fromhex(rows[1]['hex'])))
        self.assertFalse(details['arbitrary_memory_dump_emitted']);self.assertNotIn('raw_bytes',json.dumps(details))
        self.assertEqual(self.facade.render(NativeActionRequest(ACTION,self.query())).maximum_game_calls,0)

    def test_unknown_status_and_other_enum_values_remain_explicit_and_archive_opt_in(self):
        rows=[self.record(index=0,status=10,type=7,distribution=7),self.record(index=1,archived=1)]
        result=self.simulate(rows,self.query(statuses=['UNRECOGNIZED','OFFERED'],include_archived=1))
        self.assertIsNone(result['error']);offers=result['messages'][0]['details']['data']['offers']
        self.assertEqual(len(offers),2);self.assertEqual(offers[0]['enums']['Status'],{'value':10,'name':None})
        self.assertEqual(offers[0]['enums']['Type'],{'value':7,'name':None})
        self.assertEqual(offers[0]['enums']['Distribution'],{'value':7,'name':None})

    def test_selected_changes_entering_leaving_selection_and_context_changes_emit_no_snapshot(self):
        for before,after in [(self.record(index=0,status=6),self.record(index=0,status=8)),
            (self.record(index=0,status=0),self.record(index=0,status=6)),
            (self.record(index=0,status=6),self.record(index=0,team=21,status=6)),
            (self.record(index=0,status=6),self.record(index=0,status=6,wages=[7,8,9,10,11,12]))]:
            result=self.simulate([before],change_after_first_scan=[after])
            self.assertEqual(result['error'],'SIGNING_SELECTED_RECORD_SET_CHANGED');self.assertFalse(result['messages'])
        for options in ({'root_changes':True},{'team_changes':True},{'null_root':True},{'team_missing':True}):
            result=self.simulate([self.record()],**options)
            self.assertIsNotNone(result['error']);self.assertFalse(result['messages']);self.assertEqual(result['gameCalls'],0)
        result=self.simulate([self.record(),self.record(index=1,team=21)],change_after_first_scan=[self.record(index=1,team=21,status=8)])
        self.assertIsNone(result['error'])

    def test_explicit_queries_reject_empty_or_duplicate_statuses_invalid_identity_and_archive_boolean(self):
        for query in [None,[],self.query(statuses=[]),self.query(statuses=['EMPTY']),self.query(statuses=['SIGNED','SIGNED']),
            self.query(statuses=['signed']),self.query(team_id=65535),self.query(team_id=True),self.query(include_archived=True),self.query(extra=1)]:
            with self.assertRaises(ValueError):validate_pool_query(query)
        for query in [self.query(statuses=[]),self.query(statuses=['SIGNED','SIGNED']),self.query(include_archived=True)]:
            with self.assertRaises(ValueError):NativeReadFacade(self.facade).read(NativeReadQuery(DATASET,query))
            result=self.simulate([],query,compile=False)
            self.assertIsNotNone(result['error']);self.assertEqual(result['poolReads'],0);self.assertFalse(result['messages'])

    def test_role_contract_card_is_explicit_encoding_only_and_signer_remains_unavailable(self):
        service=RoleCapabilityService();profile=RoleCapabilityProfile('GM','gm20',(20,),'w','s','g','season','FREE_AGENCY','snap')
        requirements=[key for key,native in service.mapping.items() if native=='SIGN_FREE_AGENT']
        self.assertTrue(requirements)
        for key in requirements:
            card=service.get_allowed_values(key,profile);desc=service.describe_action(key,profile)
            self.assertFalse(desc['call_logic_available']);self.assertFalse(desc['identity_permission'])
            self.assertEqual(card['parameters']['contract']['properties']['signing_type']['enum'],['FREE_AGENT'])
            self.assertFalse(card['field_values']['contract']['maturity']['dispatch_implemented'])
            self.assertNotIn('root_rva',json.dumps(card))
        self.assertEqual(self.facade.sign(20,55,self.terms()).outcome,Outcome.UNKNOWN_BINDING)
        with self.assertRaises(ValueError):self.facade.render(NativeActionRequest('SIGN_FREE_AGENT',{'team_id':20,'player_id':55,'contract':self.terms()}))
        acquire=self.facade.registry.binding('sign.acquire_or_reset_candidate')
        self.assertTrue(acquire.input_layout['not_callable']);self.assertTrue(any('salary Setter' in value for value in acquire.lifecycle))
        self.assertEqual(len(NativeReadCatalog().list()),14)
        self.assertEqual(NativeReadFacade(self.facade).read(NativeReadQuery(DATASET,self.query())).outcome,Outcome.PREPARED)


if __name__=='__main__':unittest.main()
