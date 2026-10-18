"""Splice a main image (built from asm) back into a ROM as ERZ chunks.

Input ROM: the ROM linked from the boot asm + bins (build/thps1.z64). Its
original compressed chunks are *discarded*; the main image is cut into 64 KiB
pieces, each packed with tools/erz_pack.py, and a fresh chunk table is written
(4-byte-aligned spans, last chunk unpadded, then 0x00 fill to a 2-aligned asset
root, as in the retail ROM). If the packed size changes, the asset tree is moved
and its root pointer (word at 0x13B10, read by boot main) is updated, and the
header CRCs are recomputed (CIC-6102 algorithm).

usage: python -I tools/build_rom.py RNC_BIN IN.z64 MAIN.bin OUT.z64
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I drops it
import erz_pack  # noqa: E402

ROOT_PTR, TABLE, STRIDE = 0x13B10, 0x13B14, 0x10000


def n64_crc_6102(rom: bytes):
    seed = 0xF8CA4DDC
    t1 = t2 = t3 = t4 = t5 = t6 = seed
    M = 0xFFFFFFFF
    for i in range(0x1000, 0x101000, 4):
        d = struct.unpack_from(">I", rom, i)[0]
        if (t6 + d) & M < t6:
            t4 = (t4 + 1) & M
        t6 = (t6 + d) & M
        t3 ^= d
        r = ((d << (d & 0x1F)) | (d >> (32 - (d & 0x1F)))) & M if d & 0x1F else d
        t5 = (t5 + r) & M
        t2 = t2 ^ r if t2 > d else t2 ^ (t6 ^ d)
        t1 = (t1 + (t5 ^ d)) & M
    return (t6 ^ t4 ^ t3) & M, (t5 ^ t2 ^ t1) & M


def main(rnc, in_rom, main_bin, out_rom):
    rom = bytearray(open(in_rom, "rb").read())
    img = open(main_bin, "rb").read()
    old_root = struct.unpack_from(">I", rom, ROOT_PTR)[0] & 0x0FFFFFFF
    n_old = struct.unpack_from(">I", rom, TABLE)[0]
    asset_offs = struct.unpack_from(">I", rom, old_root)[0]
    asset_end = old_root + struct.unpack_from(f">{asset_offs + 1}I", rom, old_root + 4)[-1]
    assets = bytes(rom[old_root:asset_end])

    pieces = [img[i:i + STRIDE] for i in range(0, len(img), STRIDE)]
    packed = [erz_pack.pack(rnc, p) for p in pieces]
    n = len(packed)
    hdr = 4 + 4 * (n + 1)
    offs, pos, blob = [], hdr, bytearray()
    for i, p in enumerate(packed):
        offs.append(pos)
        span = len(p) if i == n - 1 else (len(p) + 3) & ~3
        blob += p + b"\0" * (span - len(p))
        pos += span
    offs.append(pos)
    table = struct.pack(f">I{n + 1}I", n, *offs)
    body = table + blob
    root = TABLE + len(body)
    root += root & 1                       # assets are 2-byte aligned (PI DMA)
    out = bytearray(rom[:ROOT_PTR])
    out += struct.pack(">I", 0xB0000000 | root) + body
    out += b"\0" * (root - len(out)) + assets
    out += b"\0" * (len(rom) - len(out))
    if len(out) != len(rom):
        raise SystemExit("ROM grew past its original size")
    if n != n_old or root != old_root:
        print(f"note: layout changed (chunks {n_old}->{n}, asset root "
              f"{old_root:#x}->{root:#x}); not byte-identical")
    c1, c2 = n64_crc_6102(out)
    struct.pack_into(">II", out, 0x10, c1, c2)
    open(out_rom, "wb").write(out)
    print(f"{out_rom}: {n} ERZ chunks, {len(blob):#x} bytes packed, asset root {root:#x}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
