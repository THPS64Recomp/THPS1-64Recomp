# Verification

What has been checked, how to repeat it, and what has not. Numbers are from the maintainer's machine (Apple M2 Pro, 10 cores,
macOS 26.3) unless stated. Labels: **[machine]** a script decides pass or fail; **[hand]** a person looked.

## 1. The decompilation rebuilds the retail ROM byte for byte [machine]

`cd decomp/thps1 && make setup && make extract ROM_SRC=your.z64 && make` prints three `OK` lines:

| Target | Result |
|---|---|
| The main code image rebuilt from disassembly with GNU as and ld | identical to the image inflated from the dump (SHA-1 in `decomp/thps1/checksums/build.main.sha1`) |
| The ROM rebuilt from the boot disassembly plus the original compressed chunks | identical (`decomp/thps1/checksums/build.rom.sha1`) |
| The ROM with the main image **recompressed** by the patched packer | identical (`decomp/thps1/checksums/build.rom_recompressed.sha1`) |

The compression format (RNC ProPack under another magic) is reproduced exactly: all 1,094 compressed pieces of the ROM (14 code
chunks and 1,080 asset pieces) recompress identically (`decomp/common/repack_check.py`; 17 further pieces are stored raw).
An exact recompression is evidence that the decoder, the format description and the packer settings are right.

## 2. N64Recomp translates the whole program without warnings [machine]

`make recomp N64RECOMP=...` on the function list (`decomp/thps1/recomp/thps1.syms.toml`): 2,743 functions, **0 warnings**; the host adds 35
function starts found at run time, giving the 2,778 functions of the generated code. 76 jump tables become `switch`
statements; `decomp/common/recomp_check.py` confirms every word of the code ranges lies in a listed function or in padding, and
reports jump-table, virtual-table and code-pointer coverage.

## 3. The regression suite plays the real game [machine]

`decomp/thps1/recomp-host/tools/test.sh` starts the host once per session and drives the game by pad input, waiting for
checkpoints (recognised screens) instead of sleeping. Result on the developer (static) build, macOS, 2026-10-15 (the release
candidate's full gate), for each of the three releases: **73 passed, 0 failed, 4 skipped**. The 4 skipped checks need the optional
launcher build, which is not part of this repository. On USA v1.0 the first run of the gate failed one check, the cheats'
save-identity test: it compared the saves of two runs that played differently (one in slow motion). It now compares a pair of runs
with no input, and passes 5 of 5 on all three releases.

| Release | Static (developer) build, full suite | First-run (split) build |
|---|---|---|
| USA v1.1 | 73 / 0 / 4 | the first-run tests pass |
| USA v1.0 | 73 / 0 / 4 (after the fix above) | the first-run build-and-play test passes |
| Europe (runs at NTSC timing) | 73 / 0 / 4 | the first-run build-and-play test passes |

The first-run tests (`decomp/common/host/tests/firstrun_test.py`: build from a dump, then play, the settings-menu hint, a relaunch, an app update) pass
with 0 failures for the three releases.

`tests/run.py --version ID` selects the release (`thps1`, `thps1_us10`, `thps1_eu`); a release's reference pictures live in
their own folder and fall back to its sibling's where the screen is identical. The screens that differ are listed in
`tests/scenarios.py` (`OWN_REFS`), and `test.sh --version ID --record` records them.

<!-- table-ok: the regression scenarios by group, described by what they check -->
| Group | Scenarios | What they check |
|---|---|---|
| Front end | 12 | boot to the logos, title, main menu, Free Skate to the Warehouse level (at least 500 triangles per graphics task), in-level audio level and a recorded WAV, median fps of at least 28, that the four pad buttons press the game's ollie, flip, grab and grind records, an ollie leaves the ground, a flip trick scores, the border bands do not flicker, the pause menu's back button resumes |
| Widescreen | 2 | menus keep the 4:3 frames; in the level the presented 1280x720 frames have at most 15 % unrendered side area (3.4 % seen) |
| Controller Pak | 4 | empty pak message; Career save writes the note and the `.mpk` changes; a new process lists and loads it and offers CONTINUE |
| Settings | 6 | skip intro, fps counter, pad bindings, crash report, bindings persistence, volume zero |
| Settings menu | 6 | the hint shows once; Esc opens and closes the menu, drawn in the presented frame; it blocks the pad; clicked options reach `general.cfg` and `graphics.cfg`; pad navigation and the layout pick; settings persist across a restart |
| HUD, controllers, cheats | the rest | the special meter's fill stays in its frame with HUD placement at 16:9 and 21:9; both controller remap screens can be left with one pad, the keyboard or two pads; controllers plugged and unplugged in menus and in a level; two players; Unlock All Levels from the menu and the flag, with the career records unchanged |
| Camera / aspect | 2 | 4:3 border and 21:9 side bands |
| High frame rate | 3 | input latency (median of six presses, at most 100 ms; about 22 ms seen), motion smoothness at 60 Hz (frame motion 1.0 against 0.5 at 30 fps; 87 to 98 % of transforms paired; no dropped in-between frames), camera cut not interpolated |
| Course cycle | 1 | four courses back to back (pause, END RUN, back to the select screen): each course's song loads only after the old song's channels have stopped reading the shared song buffer (`src/music.cpp`; without it THPS2 crashed after a few courses); the last course has music |

Reference pictures are ROM-derived, so each machine records its own (`test.sh --record`); they are never committed. The suite
records `uptime` with its timings and relaxes the fps check on an overloaded machine. Only one host runs at a time.

**Windows** (2026-10-14, Windows 11 x64, Intel Core i7-8809G, AMD Radeon RX Vega M, D3D12, 3840x2160 at 60 Hz, 150 %, on the head
before the last fixes): the static build passes **44 passed, 0 failed, 4 skipped** for each of the three releases; the first-run
tests pass (16 checks plus one macOS-only skip); and an install test of the Windows zip (unzip, first run builds the game in about
10 s, 30 s of play, exit 0, a relaunch builds nothing; 2026-10-13) passes.
**Windows, release candidate** (2026-10-17, the same PC, the release line with the course-cycle fix): the static build passes
**75 passed, 0 failed, 4 skipped** for each of the three releases (with `course-cycle`); the first-run tests pass; the zip passes
the bundle check and the full ROM scan against every dump; the install test passes; a 30-minute soak of USA v1.1 had no crash or
hang.

## 4. Small checks that need no ROM [machine]

- `tools/test.sh --controls-cfg`: the controls file migration and presets (about 15 s).
- `python3 -I decomp/thps1/recomp-host/tools/gen_versions.py check`: the version and code-class tables validate (all three releases).
- CI (`.github/workflows`): the pinned RT64 and our patches apply cleanly; the host, N64ModernRuntime and RT64 build and link on
  macOS, Linux and Windows against **ROM-free stand-in game functions**, and the ROM-free flags run. CI never sees a ROM.
  It cannot test rendering, audio or input (hosted runners have no GPU). In the public repositories it runs on GitHub's standard runners.
  Locally, `decomp/common/host/tools/mingw_check.py` cross-compiles the whole host (menu included) for Windows with MinGW.
- `erz_selftest`: the host's native decompressor reproduces the decomp's main image for all 14 chunks (needs your dump).

## 5. The release bundle contains no game bytes [machine]

`python3 -I decomp/thps1/recomp-host/tools/scan_bundle.py YOUR.z64 BLOB.bin DIR --sanity` indexes every fourth 32-byte window of the
12 MiB dump and of the 1 MB decompressed code image, then looks every byte offset of every file in `DIR` up. Any copy of 35 or
more consecutive game bytes contains an indexed window. A planted 64-byte copy must be found first (the scanner proves it
detects). **The release candidate's zips:**

Built on 2026-10-18 from one frozen commit: macOS by the release workflow on GitHub, Windows on the test PC. In every scan the
planted bytes were found, and the only runs of 64 or more matching bytes were 16-bit counting tables (the same bytes are in
SDL2, LLVM and the fonts). The release's own `SHA256SUMS` lists the published assets, which are scanned again before publishing.

| Zip | Files, size | ROM-window scan (3 dumps) | ROM-free gate | SHA-256 |
|---|---|---|---|---|
| `THPS1-64Recomp-v0.1.0-macOS-universal.zip` | 46 files, 13.2 MB | clean | passed | `8ce360f6b6a50394042e1cd1889e944ee07483c3034ef324bdb946bd1045670a` |
| `THPS1-64Recomp-v0.1.0-Windows-x64.zip` | 5,706 files, 149.0 MB | clean | passed | `070940ada6f0069f4d9ba22a696a7acf72196b9670cc1c2ee5cff19d507502e0` |

Earlier builds, for comparison: on the first-run (split) macOS bundle of 46 files, 18.8 MB (arm64, our own SDL2 2.32.10; checked 2026-10-12 against USA v1.1,
USA v1.0 and Europe, each with both code images of this game): **no run of 64 bytes or more is a copy**. Five runs of 64-194 bytes match, and all
five are 16-bit counting tables (the UTF-16 alphabet 0x20 ... 0x7E and similar: three in the engine, two in the menu's PromptFont), the same bytes that
SDL2, LLVM and FreeType carry; a table is not game content, and the scanner lists them as such. A planted 64-byte copy was found each time.
The ROM-free gate (`scan_bundle.py --no-rom`, layered checks: package inventory, allowlist, symbols, size budget) passes on the same bundle: the engine is 12.7 MB (budget 14.25 MB) and defines no game function.
On the **Windows zip** (5,706 files, 527 MB, most of it the bundled compiler; 2026-10-13, the same three dumps and code images):
no copy either; the 580-584 runs of 64 bytes or more are all such counting tables (in the compiler's libraries, SDL2, LLVM and
the fonts). The ROM-free gate passes there too: the engine is 12.9 MB (Windows budget 14.3 MB), and a game library planted in
the bundle is refused (allowlist, game-library marker, game symbols).
The generated game library is derived, but is not a byte copy, and stays on the user's machine.

The **source tree** is checked by the exporter that makes this repository (`tools/export_public.py`, private side). The primary
control is a reviewed inventory of every file, so a new file is published only after a maintainer has confirmed it is our own
work. On top of that, as supplementary layers: the same window scan against every dump the maintainer has, numeric arrays
(hex or decimal, bytes or words) and base64 decoded from text, long game strings, and a documentation
linter (no code fence over four instruction-like lines, no table over eight game-sourced rows outside `docs/game-facts/`).

## 6. Performance measurements [machine]

Warehouse, 16:9, 60 Hz interpolation, M2 Pro: every graphics configuration held 30.0 game fps and 60.0 presents per second with
no dropped in-between frames; RT64 render time per game frame was 2.2 ms (1x, MSAA off) to 5.6 ms (4x resolution, MSAA 4x),
18 ms at native 4K. At 120 Hz on the built-in panel the defaults held 120 presents per second. The game's own code costs about
0.8 ms of CPU per 33 ms frame, the same in the split library as in the static build.

## What has NOT been verified

- **Human play** [hand]: USA v1.1 was played on macOS on 2026-10-14 and in two rounds on 2026-10-15 (packaged builds,
  Xbox-style layout, 16:9, HUD placement on). Every finding is fixed and has a test: the special meter's fill, a crash in the
  graphics layer, a controls menu that couldn't be left, the far-street dropout in Downtown, and short audio pops. USA v1.0
  and Europe were played on macOS on 2026-10-17 with a Switch Pro controller (menus, a new career, a level, several song
  changes; no difference from USA v1.1 seen). Two players were played with two pads the same day.
  All three releases were played on the Windows PC on 2026-10-18 from a fresh install (a cold first start with the default
  folders): no problems found.
- **Windows beyond one machine**: one Windows 11 PC (AMD GPU, 150 % display scaling, keyboard and mouse). Not yet: a controller
  on Windows, NVIDIA and Intel GPUs, Windows 10, other display scaling, SmartScreen's Run anyway on a downloaded copy.
- **Linux**: never run on a real machine; it compiles in CI.
- **A clean Mac without developer tools**: the missing-compiler message was tested with a simulated missing compiler.
- **Audio fidelity** against hardware or another emulator: only level, tempo and spectrum measurements.
- **Other machines' performance**: all numbers are one M2 Pro.
- **Levels other than the Warehouse** for frame interpolation, and every level for gameplay completeness; the suite plays one.
- **Notarization.** **Intel Macs**: the universal app's Intel half has run only under Rosetta (it built its game library and played on Metal).
