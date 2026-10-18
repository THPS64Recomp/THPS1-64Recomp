# THPS1 (N64) decompilation and recomp groundwork

Tony Hawk's Pro Skater (N64, USA v1.1), ported by Edge of Reality from Neversoft's PlayStation code. This directory turns your
own ROM dump into a byte-identical rebuild from disassembly. It also produces the function list and code blob that N64Recomp
needs. The native host that runs the result is in [recomp-host/](recomp-host/README.md).

> **No ROM data is included or committed.** `baserom*`, `asm/`, `assets/`, `build/`, `linker_scripts/` and `include/` are
> generated locally from your dump and are git-ignored. The repository holds only configs, tools, symbol lists (addresses and
> names) and docs.

## Build

Requirements:
- macOS or Linux
- `uv`
- GNU binutils for MIPS (`mips-linux-gnu-*` from Homebrew, or set `CROSS=mips64-elf-`)
- a C compiler
- git

```sh
make setup                                   # venv (splat64 0.50.0) + .deps/rnc_propack_source @499e812
make extract ROM_SRC=/path/to/thps1-u-v1.1.z64   # sha1 4900b6c92fb8df1765e91e891dccc525bb102fe1
make                                         # build + verify (prints 3x OK)
make recomp N64RECOMP=/path/to/N64Recomp     # optional: recompile to C in build/recomp/
```

`make extract` checks the ROM's SHA-1. It then inflates the main image into
`baserom.main.bin` (14 ERZ chunks), runs splat on both configs, and fixes up
the asm (see `tools/fix_asm.py`).

## Status

| Target | Result | Checksum (SHA-1) |
|---|---|---|
| Main image `0x80016AC0–0x800F6460` (asm → GNU as/ld) | **byte-identical** | `7725fd5d2420769446ef81e207fddd398948781f` |
| ROM: header + IPL3 + boot asm + original chunks/assets as bins | **byte-identical** | `4900b6c92fb8df1765e91e891dccc525bb102fe1` |
| ROM with the main image **built from asm and recompressed** (patched RNC ProPack) | **byte-identical** | `4900b6c92fb8df1765e91e891dccc525bb102fe1` |
| ERZ recompression of every method-1 chunk in the ROM | 1,094 / 1,094 identical (14 code + 1,080 asset pieces) | none |
| Function list (boot + main) | 2,743 functions (253 boot, 2,490 main) | `recomp/thps1.syms.toml` |
| Named functions | 590 (boot 233/253 libultra+loader; main 357/2,490, 61 `_maybe`) | `symbols/*.txt` |
| N64Recomp (`ffb39cd`, built on macOS arm64) | runs to completion, **0 warnings** | needs 3 instruction patches and 1 ignore (PS1 GTE leftovers) |
| Matching C | none | compiler not identified (see below) |

## Layout

```
config/thps1.boot.yaml   splat: ROM (header, IPL3, boot segment, chunk table, chunks, assets as bin)
config/thps1.main.yaml   splat: the inflated main image (rodata | text | RSP ucode | text | data | bss)
symbols/boot.txt         libultra (n64sym) and loader names
symbols/main.txt         libmus / n_audio (n64sym), ucode, game functions named from the code and a PS1 naming reference
recomp/                  N64Recomp config and generated syms.toml (addresses and names only)
tools/                   thps_unpack, erz (decoder), erz_pack + rnc_propack patch, build_rom, fix_asm, funclist, gen_syms,
                         import_n64sym (older copies of the tools in ../common, which supersede them)
recomp-host/             the native host (README inside)
```

Documentation: [formats](../../docs/internals/formats.md), [address map](../../docs/internals/address-map.md),
[mechanics](../../docs/internals/mechanics.md), [recomp](../../docs/internals/recomp.md), [symbols](../../docs/internals/symbols.md),
[versions](../../docs/internals/versions.md), observed values in [game-facts](../../docs/game-facts/README.md). Shared tools:
[../common/](https://github.com/THPS64Recomp/THPS64Host/blob/main/TOOLS.md).

Sister projects (planned, separate repositories): the same approach for Tony Hawk's Pro Skater 2 and 3 (N64).

## Learnings and gotchas

1. **ERZ = RNC ProPack, and the stock packer reproduces it** with one patch:
   lab313ru/rnc_propack_source's look-ahead buffer (`0xFFFF − dict`) must
   grow (we use 0x20000).
   - Unpatched, 2 of 14 code chunks differ. Both are chunks with 40 KB zero
     runs: run lengths get truncated at the buffer edge, which changes the
     match-distance choice.
   - Patched: 1,094/1,094 chunks are identical.
   - Layout rule for the chunk table: spans are 4-aligned, the last chunk is
     unpadded, and the asset root is 2-aligned.
2. **The linker filled inter-object alignment padding with garbage**, not
   zeros. Expect `pref`, `lld`, COP2 and `$k0` ops, plus `jal`s into nowhere,
   between functions. This breaks GNU as (`fix_asm.py` turns these into
   `.word`) and function discovery (`funclist.looks_like_padding`).
   - Upside: every non-zero gap before a 16-byte boundary marks an object
     (TU) boundary. That's 87 seen.
3. **RSP microcode `.text` is linked inside the CPU `.text`** (`0x80097C40–0x8009B0A0`):
   n_aspMain, rspboot, and F3DEX.NoN fifo + xbus. Split it out as `textbin`,
   or disassemblers and recompilers treat it as MIPS.
4. Boot segment layout is entry stub → libultra `.rodata` → `.text`. splat
   needs `linker_section_order: .text` on that rodata subsegment to stay
   byte-identical.
5. **PS1 GTE (COP2) instructions survive in N64 code**:
   - 3× `mfc2` in `func_8005D0B0`, which **is** called.
   - 3× `ctc2` in `func_8006F574`, which is uncalled.
   The VR4300 has no COP2, so these paths must be dead. N64Recomp can't
   translate them; patch them to `nop`.
6. spimdisasm `alabel`s (from `j` targets) are mostly *intra*-function jumps
   in this game; don't use them as function starts. Splat glabels are "weak"
   too. Jump-table data, branches that cross a start, and garbage padding all
   need handling (see `funclist.py`).
7. **N64Recomp symbol-file mode needs the entry function at rom 0x1000.** The
   code blob is therefore `ROM[0:0x1000] | boot | main image`.
8. n64sym gives false positives on tiny functions inside the game image
   (`osVoiceInit`, `osBbUsbDevGetHandle`, `MusPtrBankGetCurrent`, …). Filter
   them (`tools/import_n64sym.py` REJECT list).
9. Python 3.12+ `tempfile` returns absolute paths, and rnc_propack treats
   **any argv starting with `/` as a flag**. Run it with `cwd=` and relative
   names.
10. `checksums/baserom.sha1` was silently ignored by the `baserom*` gitignore
    rule. Anchor ROM ignore patterns (`/baserom*`).
11. Game logic steps at a fixed **1/30 s** (`0x800F5668`). PS1 per-frame
    constants may need ×2 when compared.


## Compiler identification (not done)

The matching compiler is not identified. Stock gcc 2.7.2 (the KMC-tailored mac build) and egcs 2.91.66 with GNU as do not
reproduce the target's code on a small test function: the target's `div` expansion matches old GNU as (binutils 2.6), it keeps a
value in `$a3`, reuses `$a0`, and hoists a `lui` of a global to the third instruction, which neither compiler does at -O1 or -O2 for
MIPS II or III; and it has load-delay `nop`s although it also uses branch-likely instructions. SN64 (ccn64 / asn64) is the best
guess [inference]; its only available build is Linux-only, so testing it needs a Linux machine. Matching C is therefore out of
scope; the recomp does not need it.
