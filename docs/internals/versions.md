# THPS1 recomp: ROM versions and code classes

How the host runs more than one ROM release of Tony Hawk's Pro Skater (N64) without
`if (version == ...)` code. Facts only here: hashes, addresses, names.

**Status in the first release (v0.1):** the downloaded app builds the game from your dump with the *split build*
([recomp.md](recomp.md#5-the-split-build-no-game-code-in-the-app)), which needs a recipe per release (its own symbol file and
fingerprint). Two recipes cover all three releases: `us11` (USA v1.1 and Europe, each with its own code-blob fingerprint) and `us10`
(USA v1.0). The app builds each of them on first run, and the developer (static) build runs them too. The description below covers the
mechanism both builds share.

## The idea in four lines

- A **version** is a ROM we recognise: a row of `decomp/common/games.toml` (hashes, header, geometry,
  display name, `status`). Rows may `inherits = "thps1"` and list only what differs.
- A **code class** is a set of recompiled functions (one generated payload). Versions with identical code
  share a class (v1.1 and the European release: `us11`); a re-linked build has its own (`us10`).
- The host never asks "which version". It reads **names** from `thps::sym()`, a table generated per code
  class from per-class data files, and **facts** from `thps::version()`. A name a class lacks fails the build.
- A real behavioural difference becomes a **named field** in the same tables (or a `games.toml` field), set
  once per version. Never a version test in C++.

## Files

<!-- table-ok: list of files of the version mechanism -->
| File | What | Edited when |
|---|---|---|
| `decomp/common/games.toml` | one row per ROM version (and per game, THPS2/3): SHA-1/MD5/XXH3, header name/code/revision, `game_id`, `display_name`, `code_class`, `tv_default`, `status`, `refs_from`, `rom_names`, geometry (`boot_end`, `main_vram`, `root_ptr`, `main_size`, `entry`, text ranges, ucode) | a version is added |
| `decomp/common/thpsgame.py` | loader; `inherits` merge; `versions("thps1")` | never |
| `recomp-host/versions/classes.toml` | code classes: `game` (the row the payload is built from) and `syms` (symbol file) | a code class is added |
| `recomp-host/versions/host_syms.toml` | the **names the host needs**, whatever the version: `funcs`, `addr`, `field` | the host starts using a new address |
| `recomp-host/versions/<class>/host_force.toml` | function names forced onto the class's symbol file by address (`[force]`), hidden function starts (`splits`), COP2 patch sites (`[cop2]`) | a class is added / a hook is added |
| `recomp-host/versions/<class>/data_syms.toml` | `[addr]` data addresses and `[field]` struct offsets, by name | a class is added / a name is added |
| `recomp-host/config/thps1.hooks.toml` | the N64Recomp `[[patches.hook]]` blocks, **by function name**, shared by all classes | a hook is added |
| `recomp-host/tools/gen_versions.py` | validates everything and writes the outputs below | rarely |
| `recomp-host/tools/gen.py` | per class: forced-name symbol file -> N64Recomp config -> N64Recomp -> namespace header; then the version header and the audio microcode | |

Generated into `recomp-host/build/gen/` (never committed; the C is ROM-derived):

- `thps_versions.h`: `thps::SymTable` (one `uint32_t` per name in `host_syms.toml`), one `sym_<class>`
  constant per class, `sym_names[]` (name -> member, for the control channel), `code_classes[]`,
  `thps::VersionInfo all_versions[]` (every row: ids, hashes, header, `tv_default`, `status`, geometry).
- `<class>/thps1.host.syms.toml`, `<class>/thps1.host.toml` (the N64Recomp config of the class),
  `<class>/RecompiledFuncs/` (the payload), `<class>/namespace.h`.

## How the pieces meet at run time

1. `main.cpp` registers one `recomp::GameEntry` per **runnable** version (`status = supported` and its
   payload linked). Each has its own hash, header name, `game_id` and stored ROM `<game_id>.z64`.
2. `--rom PATH` -> `check_rom_file()` (`rom_check.cpp`) identifies the file by XXH3 of the big-endian ROM
   (`.z64`/`.n64`/`.v64` accepted), falling back to the header to say what it resembles. `--version ID`,
   or the first version (table order) with a stored ROM, picks otherwise.
3. `thps::versions::activate(v)` selects the payload: crash-log function names, `register_overlays` of the
   class; `thps::sym()` now points at the class's table. One class per process.
4. The entrypoint wrapper moves the main-image sections to `v.main_vram` and runs the class's
   `Boot_Entry`; `on_init_callback` writes `osTvType` (`v.tv_default`, or `--tv`).
5. Host code that touches the game reads `thps::sym().Name` (e.g. `gMsgLine0`, `View_Frustum`) and calls
   recompiled functions through `thps::call_guest(sym().Name, ...)` (a lookup by address).
6. The test channel resolves the same names: `--control` commands `sym NAME`, `peek @gSkater`,
   `version`. `tests/run.py --version ID` picks the ROM and the reference directory.

**Payload namespacing.** N64Recomp has no function-name prefix option, so two classes would collide at link
time (`func_80023430`, `GameEntry`, `recomp_entrypoint`...). `gen_versions.py namespace` scans a class's
`funcs_*.c` and writes `#define name <class>_name` for every function it **defines**; CMake force-includes
that header while compiling the class's C (and its `payload_<class>.cpp`). Names the runtime or host provide
(`osXxx_recomp`, `thps_boot_pio_copy`...) are only declared in the generated code, so they stay unrenamed.
Every class goes through this, including the first, so there is no special case. (The idea is the one DKR-R
uses for its two revisions; the script is ours.)

## Status levels

`status` in `games.toml`: `supported` (registered and run, if its class's payload is part of the build) or
`recognised` (identified by hash and named in messages, not run: "known, not yet"). A class a `supported`
version names must exist in `classes.toml`; a `recognised` version may name one that does not exist yet.

## How to add a version

**Same code as an existing version** (a re-release, a region with an identical program, like Europe):

1. Hash the dump (`shasum`, `md5`, XXH3: `tools/gen_versions.py` does not need it; `--check-rom` prints it).
2. Add a `games.toml` row with `inherits = "thps1"` and the differing identity fields (hashes, header name/
   code/revision, `game_id`, `display_name`, `main_sha1`, `asset_root`, `tv_default`, `refs_from`,
   `rom_names`); set `code_class` to the class it shares; `status = "supported"`.
3. `python3 -I decomp/common/thps_unpack.py --game <row> ROM out.bin` must report 14/14 chunks CRC OK and the
   `main_sha1` you wrote; compare the main image with the class's (`cmp`): equal means the same class.
4. `python3 -I tools/gen.py <N64Recomp>` (header only changes), rebuild, `build/cmake/thps1_recomp --check-rom ROM`, boot it.

**Different code** (a re-linked build, like USA v1.0): add a code class.

1. Row as above with the geometry facts (`boot_end`, `main_vram`, `root_ptr`, `main_size`, `entry`, `boot_text`,
   `main_text`, data starts, `ucode`), `code_class = "<new>"`.
2. `versions/classes.toml`: add the class (`game` = the row, `syms` = `recomp/<row>.syms.toml`).
3. Seed it: `<python with rabbitizer> -I recomp-host/tools/seed_class.py <class> ROM --src-rom baserom.z64
   --src-main baserom.main.bin` (the source is v1.1). It unpacks the main image, runs `sigmatch.py` (names and
   exact function ranges from the solved v1.1 symbols), writes `versions/<class>/symbols/*.txt`, runs
   `gen_syms.py` (boundaries from `funclist.py`; writes `recomp/<row>.syms.toml` and
   `build/<row>.codeblob.bin`) and applies sigmatch's ranges over funclist's guesses. Hand fixes go in
   `versions/<class>/syms_fixes.toml`.
4. `versions/<class>/host_force.toml`: every name in
   `host_syms.toml` `funcs`, at this class's addresses, plus the COP2 sites. `data_syms.toml`: every `addr` and
   `field`. `python3 -I tools/gen_versions.py check` lists whatever is missing.
   Find the forced functions with `sigmatch`'s JSON (`--json`) or by xref from a matched neighbour; data
   addresses with `python3 -I recomp-host/tools/translate_data.py <class>` (votes through the matched pairs'
   `lui`/low-half immediates; a field of an object, like `gMsgLine0`, needs the object's address and the
   field offset); check offsets of struct fields in the matched code.
5. `python3 -I tools/gen.py <N64Recomp> <class>`; fix N64Recomp errors (linker alignment garbage that funclist
   took for a function: `syms_fixes.toml`; hidden function starts that show up as "Failed to find function at
   0x..." at run time: `splits` in `host_force.toml`); rebuild (CMake picks up every class under
   `build/gen/*/`); `--check-rom`; boot; `tests/run.py --version <row>` (`--rerecord-cp NAME` for checkpoints
   whose picture differs).

**What never changes when a version is added:** `src/*.cpp`, `CMakeLists.txt`, the hook blocks, the scenarios.
If a new difference needs host behaviour, add a **name** to `host_syms.toml` (an address, an offset) or a
field to `VersionInfo` (a number), set it for every class/version, and read it by name.

## What differs between the known versions (probed 2026-10-11)

| | USA v1.1 | Europe | USA v1.0 |
|---|---|---|---|
| header | `TONY HAWK PRO SKATER`, NTFE, rev 1 | `TONY HAWK SKATEBOARD`, NTFP, rev 0 | `TONY HAWK PRO SKATER`, NTFE, rev 0 |
| SHA-1 | `4900b6c9...` | `c321cd05...` | `fc1b4dec...` |
| XXH3-64 | `B7B085A35E270C23` | `8EF5310EBEB00EA0` | `E771EA04C14F3429` |
| code class | `us11` | `us11` (same program; padding, 1 instruction, 4 splash images differ) | `us10` (re-linked: own symbols, own payload) |
| `tv_default` | `ntsc` | `ntsc` (decision: the Europe release runs at NTSC timing; `--tv pal` is experimental) | `ntsc` |
| status | supported | supported (NTSC timing; PAL experimental) | supported |

The supported-ROM table with all hashes is in the [MANUAL](../MANUAL.md#your-game-dump).

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. Facts derived
from analysis of retail cartridge dumps. No game data is reproduced beyond names, addresses and individual values. See the README.
