"""Decode actual synthetic x64 registration bytes, without opening the game PE."""
import re
import struct
import sys
import unittest
from pathlib import Path

CONTROL=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CONTROL/'tools'))
from recover_script_callbacks import recover
from pe_local import Image
from capstone import Cs,CS_ARCH_X86,CS_MODE_64


class SyntheticImage(Image):
    def __init__(self,*,call_target=0x1fbaf0,callback=0x10c0):
        self.base=0x140000000
        self.sha256='SYNTHETIC_X64_BYTES_NOT_GAME'
        self.text={'name':'.text','rva':0x1000,'raw':0,'size':256}
        self.sections=[self.text,{'name':'.rdata','rva':0x2000,'raw':256,'size':128}]
        self.cs=Cs(CS_ARCH_X86,CS_MODE_64)
        self.cs.detail=True
        raw=bytearray(b'\xcc'*256+b'\0'*128)
        strings=[b'void RotationChange()\0',b'void RotationOther()\0']
        at=0
        for index,name in enumerate(strings):
            offset=index*64
            start=0x1000+offset
            declaration=0x2000+at
            raw[256+at:256+at+len(name)]=name
            code=(b'\x45\x33\xc9'+b'\x4c\x8d\x05'+struct.pack('<i',callback-(start+10))+
                  b'\x48\x8d\x15'+struct.pack('<i',declaration-(start+17))+
                  b'\x48\x8b\xcb'+b'\xe8'+struct.pack('<i',call_target-(start+25))+b'\x85\xc0')
            raw[offset:offset+len(code)]=code
            at+=len(name)
        self.data=bytes(raw)

    def unwind_chain(self,rva):
        return []


class CallbackRecovery(unittest.TestCase):
    def test_exact_registration_excludes_following_test_instruction(self):
        result=recover(SyntheticImage(),re.compile('Rotation'),10)
        self.assertEqual(len(result['callbacks']),2)
        self.assertEqual(result['callbacks'][0]['callback_rva'],0x10c0)
        self.assertEqual([row['mnemonic'] for row in result['callbacks'][0]['registration_window']],
                         ['xor','lea','lea','mov','call'])
        self.assertFalse(result['game_access_performed'])

    def test_wrong_registration_target_or_noncode_callback_is_rejected(self):
        for image in [SyntheticImage(call_target=0x1fbaf1),SyntheticImage(callback=0x2000)]:
            self.assertFalse(recover(image,re.compile('Rotation'),10)['callbacks'])

    def test_string_selection_limit_discloses_omitted_matches(self):
        result=recover(SyntheticImage(),re.compile('Rotation'),1)
        self.assertEqual(result['matching_string_count'],2)
        self.assertTrue(result['string_selection_truncated'])
        self.assertEqual(len(result['callbacks']),1)


if __name__=='__main__':unittest.main()
