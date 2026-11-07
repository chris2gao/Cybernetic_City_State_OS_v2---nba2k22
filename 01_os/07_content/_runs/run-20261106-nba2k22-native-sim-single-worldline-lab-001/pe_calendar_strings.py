"""Bounded, read-only search for static calendar anchors in a supplied PE."""
import hashlib
import mmap
import re
import struct
import sys


def main(path):
    with open(path, "rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        print("sha256", hashlib.sha256(data).hexdigest())
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        count, = struct.unpack_from("<H", data, pe + 6)
        opt_size, = struct.unpack_from("<H", data, pe + 20)
        table = pe + 24 + opt_size
        terms = (sys.argv[2].encode() if len(sys.argv) > 2 else
                 rb"sim(?:ulate)?[ _]*(?:through|to)[ _]*date|calendar[ _]*sim|sim[ _]*until|SCHEDULEDATE|simulat.{0,22}calendar|calendar.{0,22}simulat")
        for index in range(count):
            name, _, rva, size, raw = struct.unpack_from("<8sIIII", data, table + index * 40)
            if not size:
                continue
            for width in (1, 2):
                if width == 1:
                    regex = re.compile(rb"[ -~]{5,180}")
                    decode = "ascii"
                else:
                    regex = re.compile(rb"(?:[ -~]\x00){5,180}")
                    decode = "utf-16-le"
                matches = 0
                for match in regex.finditer(data, raw, raw + size):
                    value = match.group().decode(decode)
                    if not re.search(terms, value.encode("ascii"), re.IGNORECASE):
                        continue
                    print(name.rstrip(b"\0").decode(), hex(rva + match.start() - raw), value)
                    matches += 1
                    if matches == 30:
                        print("section match cap reached", width)
                        break


if __name__ == "__main__":
    main(sys.argv[1])
