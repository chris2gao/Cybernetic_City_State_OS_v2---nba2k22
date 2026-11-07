"""Find verified RIP-relative references and direct callers in PE function ranges."""
import bisect
import hashlib
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_64, Cs
from capstone.x86 import X86_OP_MEM, X86_REG_RIP
import numpy as np


def main(path, targets, dump=False, around=None):
    data = Path(path).read_bytes()
    print("sha256", hashlib.sha256(data).hexdigest())
    pe, = struct.unpack_from("<I", data, 0x3C)
    count, = struct.unpack_from("<H", data, pe + 6)
    opt_size, = struct.unpack_from("<H", data, pe + 20)
    table = pe + 24 + opt_size
    sections = {}
    for index in range(count):
        name, _, rva, size, raw = struct.unpack_from("<8sIIII", data, table + index * 40)
        sections[name.rstrip(b"\0")] = (rva, data[raw:raw + size])
    text_rva, code = sections[b".text"]
    _, pdata = sections[b".pdata"]
    functions = sorted((start, end) for start, end, _ in struct.iter_unpack("<III", pdata[:len(pdata)//12*12]) if start < end)
    starts = [start for start, _ in functions]
    engine = Cs(CS_ARCH_X86, CS_MODE_64)
    engine.detail = True
    for target in targets:
        print("target", hex(target))
        if dump:
            index = bisect.bisect_right(starts, target) - 1
            lo, hi = functions[index]
            if not lo <= target < hi:
                raise ValueError("target outside a PE unwind range")
            print("range", hex(lo), hex(hi), "code_sha256",
                  hashlib.sha256(code[lo-text_rva:hi-text_rva]).hexdigest())
            for ins in engine.disasm(code[lo-text_rva:hi-text_rva], lo):
                if around is not None and abs(ins.address - target) > around:
                    continue
                annotation = ""
                for op in ins.operands:
                    if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
                        address = ins.address + ins.size + op.mem.disp
                        rva, rdata = sections[b".rdata"]
                        offset = address - rva
                        if 0 <= offset < len(rdata):
                            value = rdata[offset:offset+100].split(b"\0", 1)[0]
                            if len(value) >= 5 and all(32 <= char < 127 for char in value):
                                annotation = f" ; {address:#x} {value.decode()}"
                print(f"{ins.address:#x} {ins.mnemonic} {ins.op_str}{annotation}".rstrip())
            continue
        for chunk in range(0, len(code)-3, 1048576):
            size = min(1048576, len(code)-3-chunk)
            for alignment in range(4):
                start = chunk + alignment
                count = (size + 3 - alignment) // 4
                disps = np.frombuffer(code, dtype="<i4", offset=start, count=count)
                ends = text_rva + start + 4 + np.arange(count, dtype=np.int32)*4
                hits = np.flatnonzero(disps == target - ends)
                for hit in hits:
                    end_rva = int(ends[hit])
                    index = bisect.bisect_right(starts, end_rva - 5) - 1
                    if index < 0:
                        continue
                    lo, hi = functions[index]
                    if not (lo <= end_rva - 5 < hi):
                        continue
                    instructions = list(engine.disasm(code[lo-text_rva:min(hi, end_rva+16)-text_rva], lo))
                    for pos, ins in enumerate(instructions):
                        rip = any(op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP
                                  and ins.address + ins.size + op.mem.disp == target for op in ins.operands)
                        direct = (ins.mnemonic in {"call", "jmp"} and ins.op_str == hex(target))
                        if (rip or direct) and ins.address <= end_rva <= ins.address + ins.size:
                            print("function", hex(lo), hex(hi), "xref", hex(ins.address))
                            for around in instructions[max(0,pos-5):pos+5]:
                                print(f"  {around.address:#x} {around.mnemonic} {around.op_str}".rstrip())


if __name__ == "__main__":
    main(sys.argv[1], [int(arg, 0) for arg in sys.argv[2:] if not arg.startswith("--")],
         "--dump" in sys.argv[2:], 0x45 if "--around" in sys.argv[2:] else None)
