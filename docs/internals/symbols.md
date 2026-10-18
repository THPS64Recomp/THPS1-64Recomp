# Symbols: coverage, sources and evidence

How the function and data names in `decomp/thps1/symbols/{boot,main}.txt` came about, how much is named, and how far to trust each
name. Names are identifiers only; no code from any reference project is used. Labels: **[H]** read in the N64 code and matches the
reference function's behaviour; **[V]** vtable slot with matching slot count, base-class slots and size; **[M]** two independent
signals (callee sequence and size, a unique string and unit, a parent's call skeleton); **[C]** call-graph vote from at least two
anchors; **[C?]** a single anchor, kept with a `_maybe` suffix.

## Coverage

| Segment | Named | How |
|---|---|---|
| Boot segment (libultra, IDO) | 233 of 253 | n64sym's built-in signatures (exact byte match, imported by `decomp/common/import_n64sym.py`); the 5 loader functions by hand |
| Main image | 357 of 2,490 (61 with a `_maybe` suffix) | n64sym hits for libgcc, libmus and n_audio; names borrowed from the PS1 *Tony Hawk's Pro Skater 2* demo decompilation after the N64 code was read; hand identification. Each entry carries its evidence tier |
| Overall | 590 of 2,743 | the rest are `func_<address>` |

Roughly 650 game-code functions are never referenced (272 are 8-byte empty stubs, many PlayStation leftovers); they translate
harmlessly and are not worth naming effort. The recomp does not need names: it needs correct function bounds, which come from
the rules in [recomp.md](recomp.md#2-the-function-list).

## Where the names come from

- **n64sym** (shygoo; MIT): libultra, libmus and libgcc functions recognised by exact byte signature. Tag `n64sym`.
- **The PS1 THPS2 demo decompilation** (emoluvjd; no licence granted for its code): the PlayStation game is the ancestor of this
  engine, and its function and class names (`CBruce`, `Trick_Land`, `DoOnRailPhysics` ...) were used as a **naming reference only**.
  No code, header or data was copied, and nothing from that repository is part of this one. Tag `ps1`. The "name source" column in the
  [address map](address-map.md#6-key-functions) lets a reader filter these out. The reference game is
  not this game (it has manuals and a create-a-skater mode; THPS1 inlines far more), so every name needs its own evidence.
- **Hand identification** from the disassembly: the loader, the Edge of Reality asset layer (`Archive_*`, `Rom_ReadUnpack`,
  the `.psx`/`.trg` loaders and name tables, SPOOL, TRIG, OB, heap and `Mem_*`), and various engine pieces. Tags `manual`, `loader`.
- Untagged entries are evidence-tiered ([H], [M], [V], [C]) entries whose names also follow the reference.

No leaked source code was used.

## Method for game code

A candidate is named only after reading the N64 code ([H]), or when it has a string anchor or a distinctive constant set plus a
consistent source order ([M]). The ranking aids we used (not published here; they read a local copy of the PS1 source) were: an
alignment of each translation unit's function order against the PS1 unit's order (the compiler keeps source order), a rare-constant
ranking (shared constants weighted by rarity), a call-graph vote from named anchors, and the padding between objects as unit
boundaries. They are noisy: the sequel game differs, a few huge functions (`DoPhysics` is 8.6 KB) match everything, and most PS1
strings live in file-scope tables, so per-function string anchors are rare.

Lessons worth keeping:
- **Inlining breaks naive alignment.** THPS1 inlines animation running (`Debug_RunAnim*`), the physics-state dispatch (into
  `DoPhysics`) and the hand-plant start (into `HandleStickToRail`). Fix those by hand before any automatic propagation, or the
  names drift downstream.
- **PS1 operators are invisible calls.** `a - b` on vectors is a `jal` on the N64 but not a call name in the PS1 source.
- **GTE macros became functions.** The port turned the PS1 geometry-engine macros into small float functions
  (`0x80042C70` to `0x800433E4`); they anchor many physics helpers.
- **A name vetoed after reading the code stays vetoed** (`// reject 0xADDR why` lines): empty stubs and setters produced false
  proposals.
- **splat parses comments in symbol files.** A comment token containing `:` that is not a valid attribute, or any `;`, makes the
  extract step fail. Keep comments free of both.
- **n64sym gives false positives on tiny functions** inside the game image; the importer's reject list filters them.

## Next targets

Speed limiting and braking inside `DoPhysics`, the push code in `DoOnGroundPhysics`, grind start inside `HandleStickToRail`, and
the callers of `GetFaceFlags`.

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. Facts derived
from analysis of a retail cartridge dump. No game data is reproduced beyond names, addresses and individual values. See the README.
