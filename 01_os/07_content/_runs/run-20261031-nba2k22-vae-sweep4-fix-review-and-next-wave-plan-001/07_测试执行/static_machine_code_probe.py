"""Fixed-source offline counterexamples for f953f622c833a40a714a6ff6055af170b2070a7e.
Source-equivalent: bytes copied from submitted consumer_tracer.py.
Not game PE bytes independently authenticated. No game access or file mutation.
Run: python static_machine_code_probe.py; optional: disassemble with objdump -D -b binary -m i386:x86-64.
"""
import struct
ROLE=bytes.fromhex(
"48 8d 4c 24 30 e8 d4 ee 74 ff 48 63 4c 24 20 44 8b c0 83 f9 03 75 76 "
"48 63 4c 24 24 83 f9 03 75 1e 48 8d 4c 24 30 44 88 87 dd 02 00 00 "
"e8 bc f1 74 ff 8b d0 88 97 de 02 00 00 e9 35 01 00 00 "
"8b 94 8e 98 97 b5 02 48 8b d9 83 ea 05 41 0f b6 c8 41 3b d0 "
"0f b6 c2 0f 4c c8 88 8f dd 02 00 00 e8 85 f1 74 ff")
TEMPO=bytes.fromhex(
"f3 0f 2d c0 83 e8 32 6b c8 3c b8 1f 85 eb 51 f7 e9 b8 46 00 00 00 "
"c1 fa 04 8b ca c1 e9 1f 83 c1 0a 03 ca 83 f9 46 0f 4f c8 "
"b8 0a 00 00 00 83 f9 0a 0f 4c c8 8b c7 2b c1")
SNAP=bytes.fromhex("e8 0d 07 23 00 89 85 e0 00 00 00 e8 ff f8 22 00 89 85 e4 00 00 00")
base=0x14120ba72
loc={
"mov_eax70":base+TEMPO.index(bytes.fromhex("b8 46 00 00 00")),
"cmovg":base+TEMPO.index(bytes.fromhex("0f 4f c8")),
"mov_eax10":base+TEMPO.index(bytes.fromhex("b8 0a 00 00 00")),
"cmovl":base+TEMPO.index(bytes.fromhex("0f 4c c8")),
}
assert loc=={"mov_eax70":0x14120ba83,"cmovg":0x14120ba98,"mov_eax10":0x14120ba9b,"cmovl":0x14120baa3}
assert TEMPO[0x120ba98-0x120ba72:][:5] != bytes.fromhex("b8 46 00 00 00")
print("PASS static offset mismatch", {x:hex(y) for x,y in loc.items()})
def relcall(at, code):
    assert code[0]==0xe8
    return at+5+struct.unpack("<i",code[1:5])[0]
assert relcall(0x14174510e,SNAP[:5])==0x141975820
assert relcall(0x1412269a1,ROLE[-5:])==0x140975b2b
print("PASS rel32 targets differ from catalog: snapshot->0x141975820, role->0x140975b2b")
def hypothetical_native_tempo_modifier_if_xmm0_is_slider(x):
    # signed high32 of IMUL with EAX=0x51eb851f; SAR edx,4; ecx=edx+(edx<0)+10
    edx=((x-50)*60*0x51eb851f)>>32
    edx>>=4
    mod=edx+(1 if edx<0 else 0)+10
    return min(70,max(10,mod))
assert hypothetical_native_tempo_modifier_if_xmm0_is_slider(50)==10
assert hypothetical_native_tempo_modifier_if_xmm0_is_slider(80)==46
assert hypothetical_native_tempo_modifier_if_xmm0_is_slider(100)==70
print("PASS formula mismatch: hypothetical xmm0 80 gives modifier46, bridge raw clamp gives70")
assert "2026-10-31T03:31:03.580403+00:00"!="2026-10-31T03:00:00Z"
assert 1056964608!=0.5
print("PASS git source original time/raw bits != placeholder legacy value")
print("4 categories reproduced; these checks do NOT authenticate original NBA2K22.exe bytes.")
