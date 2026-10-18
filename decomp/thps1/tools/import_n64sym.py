"""Turn n64sym's splat-format output into symbols/{boot,main}.txt entries.

Only names whose address is a discovered function start (tools/funclist.py)
become `type:func`; data/rodata names are kept for main/boot data; generic
placeholders (`*_rodata_XXXX`, `*_bss_XXXX`, `*_data_XXXX`) are dropped.
Duplicate names get an `_<ADDR>` suffix. Run after n64sym; review the diff.

usage: python tools/import_n64sym.py n64sym.txt baserom.z64 baserom.main.bin
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import funclist  # noqa: E402

# Signature hits inside the main image that are not plausible for THPS1
# (checked by hand: wrong library or tiny generic bodies).
REJECT = {"osBbUsbDevGetHandle", "osVoiceInit", "osVoiceCheckWord", "osVoiceControlGain",
          "ptstart", "MusPtrBankGetCurrent", "n_aspMainTextStart", "rspbootTextStart",
          "gspF3DEX2_NoN_fifoTextStart", "gspF3DEX2_NoN_xbusTextStart"}


def main(sym_path, rom, img):
    boot, main_, fb, fm, _ = funclist.load_all(rom, img, sym_paths=())
    ents = []
    for line in open(sym_path):
        m = re.match(r"(\S+) = (0x[0-9A-F]+);", line.strip())
        if m:
            ents.append((m.group(1), int(m.group(2), 16)))
    counts = collections.Counter(n for n, _ in ents)
    out = {"boot": [], "main": []}
    skipped = []
    for name, a in sorted(ents, key=lambda e: e[1]):
        if re.search(r"_(rodata|bss|data)_[0-9A-F]{4}$", name) or name in REJECT:
            continue
        if counts[name] > 1:
            name = f"{name}_{a:08X}"
        seg = "boot" if a < 0x80016AC0 else "main"
        funcs = fb if seg == "boot" else fm
        img_ = boot if seg == "boot" else main_
        if a in funcs:
            out[seg].append(f"{name} = 0x{a:08X}; // type:func size:0x{funcs[a]:X} n64sym")
        elif img_.in_text(a):
            skipped.append((name, a))
        else:
            out[seg].append(f"{name} = 0x{a:08X}; // n64sym")
    for seg, lines in out.items():
        print(f"## {seg}: {len(lines)}")
        print("\n".join(lines))
    print("## in text but not a discovered start (not imported):", [(n, hex(a)) for n, a in skipped])


if __name__ == "__main__":
    main(*sys.argv[1:4])
