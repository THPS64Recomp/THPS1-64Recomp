"""Inflate THPS1's main code image from the ROM, exactly as boot main does.

Boot main (0x80000870) reads `count` + `count+1` table-relative offsets at ROM
0x13B14. For each chunk it PIO-copies to 0x803E0000, inflates ERZ (= RNC
ProPack, magic renamed) method 1/2 or copies raw, writing to
0x80016AC0 + i*0x10000. Each chunk's two CRC-16s are checked here.

usage: python -I tools/thps_unpack.py baserom.z64 baserom.main.bin
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I drops it
import erz  # noqa: E402

TABLE, VRAM, STRIDE = 0x13B14, 0x80016AC0, 0x10000


def chunk_spans(rom, table=TABLE):
    n = struct.unpack_from(">I", rom, table)[0]
    offs = struct.unpack_from(f">{n + 1}I", rom, table + 4)
    return [(table + offs[i], offs[i + 1] - offs[i]) for i in range(n)]


def unpack(rom, table=TABLE):
    img = bytearray()
    for i, (a, span) in enumerate(chunk_spans(rom, table)):
        if rom[a:a + 3] == erz.MAGIC:
            data, info = erz.decompress(rom, a)
            if not (info["pcrc_ok"] and info["ucrc_ok"]):
                raise SystemExit(f"chunk {i}: CRC mismatch")
        else:
            data = rom[a:a + span]
        if len(img) != i * STRIDE:
            raise SystemExit(f"chunk {i}: previous chunk shorter than 0x{STRIDE:X}")
        img += data
    return bytes(img)


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    img = unpack(rom)
    open(sys.argv[2], "wb").write(img)
    print(f"{sys.argv[2]}: {VRAM:08X}-{VRAM + len(img):08X} ({len(img):#x} bytes)")
