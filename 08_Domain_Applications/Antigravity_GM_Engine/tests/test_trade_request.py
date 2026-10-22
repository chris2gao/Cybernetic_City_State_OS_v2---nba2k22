"""Synthetic trade request normalization; no game or signing module imports."""
import copy
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from trade_request import metadata,normalize


def player(full_name,face,team):
    first,last=full_name.split(' ',1)
    raw=bytearray(0x4f0)
    raw[:len(last.encode('utf-16le'))]=last.encode('utf-16le')
    raw[40:40+len(first.encode('utf-16le'))]=first.encode('utf-16le')
    struct.pack_into('<H',raw,0x6c,face)
    struct.pack_into('<H',raw,0x6e,1994|(3<<12))
    raw[0x70]=12
    struct.pack_into('<Q',raw,0x60,team)
    struct.pack_into('<Q',raw,0xa8,team)
    struct.pack_into('<I',raw,0x1a4,1234567)
    raw[0x32e]=8
    return bytes(raw)


class FakeMemory:
    def __init__(self):
        self.data={1000:player('Coby White',7826,30000),
                   2000:player('Derrick Jones Jr.',7293,30000),
                   3000:player('Jerami Grant',4105,210000)}
    def read_bytes(self,address,size):
        return self.data[address][:size]


def fixture():
    raw=bytearray(0x1258)
    struct.pack_into('<40Q',raw,0xd28,*([2000,11,12,13,14]*8))
    state={'teams':{3:{'address':30000,'abbreviation':'CHI'},21:{'address':210000,'abbreviation':'DET'}},
           'team_ids':{30000:3,210000:21},'rosters':{3:[1000,2000]+[0]*23,21:[3000]+[0]*24},
           'team_raw':{3:bytes(raw),21:bytes(0x1258)}}
    request={'request_id':'TEST','save_id':'SYNTHETIC','season':'2021-2022','trades':[
        {'players':[{'name':'Jerami Grant','from_team':'DET','to_team':'CHI'},
                    {'name':'Coby White','from_team':'CHI','to_team':'DET'},
                    {'name':'Derrick Jones Jr.','from_team':'CHI','to_team':'DET'}]}]}
    return state,request


class RequestTests(unittest.TestCase):
    def test_names_only_pin_observed_identity_and_preserve_contract(self):
        state,request=fixture()
        result=normalize(request,state,FakeMemory())
        grant=result['actions'][0]['players'][0]
        self.assertEqual((grant['face_id'],grant['birth_date']),(4105,'1994-03-12'))
        self.assertEqual(grant['salary_sequence'],[1234567,0,0,0,0,0])
        self.assertEqual(result['actions'][0]['reference_replacements']['3'],{'7293':4105,'7826':0})
        self.assertNotIn('salary_sequence',request['trades'][0]['players'][0])

    def test_same_name_clone_is_not_silently_selected(self):
        state,request=fixture()
        mem=FakeMemory()
        mem.data[4000]=player('Coby White',9999,30000)
        state['rosters'][3][2]=4000
        with self.assertRaisesRegex(ValueError,'found 2'):
            normalize(request,state,mem)
        request['trades'][0]['players'][1]['face_id']=7826
        self.assertEqual(len(normalize(request,state,mem)['actions'][0]['players']),3)

    def test_expected_original_salary_change_is_rejected(self):
        state,request=fixture()
        request['trades'][0]['players'][0]['salary_sequence']=[1]*6
        with self.assertRaisesRegex(ValueError,'differs from live'):
            normalize(request,state,FakeMemory())

    def test_complete_target_state_can_still_be_normalized_for_noop(self):
        state,request=fixture()
        state['rosters']={3:[3000]+[0]*24,21:[1000,2000]+[0]*23}
        result=normalize(request,state,FakeMemory())
        self.assertEqual(len(result['actions'][0]['players']),3)

    def test_examples_empty_requests_and_wrong_seasons_are_rejected(self):
        _,request=fixture()
        for changed in ({**request,'example_only':True},{**request,'trades':[]},
                        {**request,'season':'2021-2025'}):
            with self.assertRaises(ValueError):
                metadata(changed)


if __name__=='__main__':
    unittest.main()
