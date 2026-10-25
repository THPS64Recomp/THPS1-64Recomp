# THPS1 recomp host (N64: USA v1.1; Europe and USA v1.0 recognised)

The native macOS (arm64) host for Tony Hawk's Pro Skater for N64, made with
[N64Recomp](https://github.com/N64Recomp/N64Recomp) and run on N64ModernRuntime + RT64 (Metal). This is the developer
README. Users want the top-level [README](../../../README.md) and [docs/MANUAL.md](../../../docs/MANUAL.md).

> **No ROM data is in this directory.** The recompiled C, the code blob, dumps and build output are all generated locally from
> your own dump and are git-ignored (`build/`, `*.png`, `*.bin`). This directory holds only our C++ and CMake, configs, small
> tools and notes.

How it works inside: [docs/internals/recomp.md](../../../docs/internals/recomp.md). What has been verified:
[docs/VERIFICATION.md](../../../docs/VERIFICATION.md).

## Layout

The host (sources, CMake file, Python tools, test harness, RT64 patches) lives in `../common/host/`; this directory is the game's profile.
`tools/` and `tests/` here hold small wrappers with the shared tools' names, so the commands below run from this directory.
Where this README says `src/x.cpp`, it is `../common/host/src/x.cpp`.

```
CMakeLists.txt            9 lines: project(), THPS_FAMILY, include(../common/host/cmake/thps_host.cmake)
game/game.toml            the game profile: names, config folder, wording, flags (-> thps::game in build/gen/thps_versions.h)
game/skip_intro.cpp       THPS1's Skip Intro; game/game_hooks.def its own hook imports
config/thps1.hooks.toml   N64Recomp [[patches.hook]] blocks (loader, PI, events...), by function name, shared
                          by every ROM version (docs/internals/versions.md)
config/thps1.aspMain.toml RSPRecomp config template for the audio microcode
versions/                 ROM versions: code classes, the names the host needs (host_syms.toml), per-class
                          forced names + data addresses (docs/internals/versions.md)
recipes/<class>/          committed ROM-free release inputs (symbol file rows, code-blob fingerprints)
tools/gen.py              wrapper -> ../common/host/tools/gen.py: syms -> N64Recomp -> build/gen/, RSPRecomp -> build/gen/rsp/
tools/gen_versions.py     validates the version tables; writes build/gen/thps_versions.h, per-class N64Recomp configs
tools/build_host.py       ROM -> generated C -> host in one command (Windows, Linux, macOS); tools/build_windows.ps1 wraps it
tools/test.sh, tests/     the regression suite (shared runner and harness; tests/scenarios.py is this game's)
../common/host/src/       main, hooks, input, audio, pak, widescreen, rom_check, versions, the first-run flow, the split build ...
../common/host/patches/   our RT64 patches (applied by tools/setup_runtime.py)
../common/gen_host_syms.py  the class's syms.toml -> build/gen/<class>/thps1.host.syms.toml
```

## Build

The one-command route (Windows, Linux, macOS):

```sh
python3 -I tools/build_host.py --rom /path/to/your/thps1-usa-v1.1.z64
```

It fetches the pinned N64ModernRuntime and RT64 and applies our patches (`tools/setup_runtime.py`), builds N64Recomp and RSPRecomp
at the pinned commit, makes a Python venv with `rabbitizer`, inflates your ROM's code and generates the C (`tools/gen.py`), then
configures and builds the host with CMake and Ninja. `--stub` builds with ROM-free stand-in functions to check the toolchain.

By hand, once the runtime tree is in `<runtime-dir>` (its `lib/N64ModernRuntime` and `lib/rt64` at the pins, patches applied):

```sh
cd decomp/thps1
make extract ROM_SRC=/path/to/thps1-u-v1.1.z64   # once (decomp README)
make recomp-inputs                               # -> build/thps1.codeblob.bin (local)
cd recomp-host
python3 -I tools/gen.py /path/to/N64Recomp         # -> build/gen/us11/RecompiledFuncs (2,778 funcs) + rsp/n_aspMain.cpp
cmake -S . -B build/cmake -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DRECOMP_RUNTIME_DIR=<runtime-dir>
cmake --build build/cmake                        # ~790 steps, first build ~8 min
```

Prerequisites on macOS: Xcode (or the Command Line Tools) with the Metal toolchain, Homebrew `cmake ninja sdl2 pkgconf`.

## Split build: no game code in the app

`-DTHPS_SPLIT_GAME_LIB=ON` builds the engine without any recompiled game code. On first run the app translates the user's ROM
with the bundled N64Recomp and RSPRecomp, compiles the C with the system compiler and loads
`<config>/game/thps1_game_<class>.<dylib|so|dll>`. This is how releases are built. Design, numbers and findings:
[docs/internals/recomp.md](../../../docs/internals/recomp.md#5-the-split-build-no-game-code-in-the-app). Files: `src/game_abi.h`,
`src/game_split.cpp`, `src/game_live.cpp` (the in-memory research mode, `-DTHPS_LIVERECOMP=ON`), `game-lib/`, `tools/package_split.py`
(assembles the `.app`), `tools/scan_bundle.py` (the ROM-byte scan). `recipes/us11` serves USA v1.1 and Europe, `recipes/us10` USA v1.0.

## In-game settings menu

Esc (controller: Back) opens an RmlUi menu over the game (General, Controls, Graphics, Sound) that edits `general.cfg`, `graphics.cfg` and
`controls.cfg`; the code (`src/ui/`, `ui/`) is shared by all three games.
Its libraries and fonts are fetched by `tools/setup_runtime.py` at pinned hashes, never stored here. `-DTHPS_MENU=OFF` builds without it.

## Windows and Linux (ported, not yet run on either)

macOS is the only system this host has been played on. The Windows and Linux support was written against the
upstream sources and cross-checked without those systems (CI builds it).

- **OS-specific code** lives in `src/platform.{h,cpp}` (timer resolution, UTF-8 arguments and paths, per-user config
  folder, window visibility), `src/crash.cpp` (POSIX signals, or an unhandled-exception filter on Windows),
  `create_window()` in `src/main.cpp` and `src/rt64_context.cpp` (the window and renderer handle), and the CMake
  file. Structure after Zelda64Recomp's `main.cpp`; credits in the top-level `NOTICE.md`.
- **Config folder:** macOS `~/Library/Application Support/THPS1-64Recomp`, Windows `%LOCALAPPDATA%\THPS1-64Recomp`,
  Linux `$XDG_CONFIG_HOME` (or `~/.config`)`/THPS1-64Recomp`; a `portable.txt` next to the exe (or in the working
  directory) overrides all of them.
- **Graphics API:** Metal on macOS; elsewhere RT64 picks (D3D12 on Windows, then Vulkan; Vulkan on Linux).
  `--api auto|d3d12|vulkan|metal` forces one. Alt+Enter toggles fullscreen on Windows and Linux.
- **Build on Windows** (Visual Studio 2022 with "C++ Clang Compiler for Windows" and "C++ CMake tools", clang-cl only):
  `powershell -ExecutionPolicy Bypass -File tools\build_windows.ps1 -Rom <your ROM>` (or
  `python tools/build_host.py --rom <your ROM>`, which also works on Linux and macOS: it fetches the pinned runtime, applies
  our RT64 patches, builds N64Recomp, generates the C from your ROM on your machine, and builds the host).
- **Build with no ROM** (CI, toolchain checks; the exe links but cannot play):
  `python -I tools/setup_runtime.py <dir>` then `cmake -S . -B build/cmake -G Ninja -DRECOMP_RUNTIME_DIR=<dir> -DTHPS_STUB_FUNCS=ON`.
  `tools/gen_stub.py` writes one empty function per symbol of the public `recomp/*.syms.toml`.
- **Linux:** the same CMake file (clang or gcc, SDL2 and Vulkan development packages); RT64 is built with
  `RT64_SDL_WINDOW_VULKAN`. Nothing of it has been compiled yet (CI will).
- **Tests on Windows:** `python -I tests\run.py` (the harness no longer needs `fcntl`, `getloadavg` or `/dev/null`; the
  `crash_log` step expects exit code 0xC0000005). References recorded on a Mac are Metal frames: `--record` your own.

## Supported ROMs

One binary runs several releases; it identifies the file by hash (so `.z64`, `.n64`, `.v64` all work) and
keeps a copy per version in `--config` (`<game id>.z64`). `build/cmake/thps1_recomp --check-rom FILE` says
what a file is. Hashes are of the big-endian ROM. How versions are modelled: [docs/internals/versions.md](../../../docs/internals/versions.md). The downloaded app (split build) builds and runs all three on first launch.

| Release | Header (name, code, rev) | SHA-1 | MD5 | XXH3-64 | Status |
|---|---|---|---|---|---|
| USA v1.1 (preferred) | `TONY HAWK PRO SKATER`, NTFE, 1 | `4900b6c92fb8df1765e91e891dccc525bb102fe1` | `aff424a1883dc7bb92c7b2ebe9342f85` | `B7B085A35E270C23` | supported, full suite |
| Europe | `TONY HAWK SKATEBOARD`, NTFP, 0 | `c321cd05eec58765467878ac8015784535280e3c` | `c9e9c4a18b1540c6b4111331d7c663b8` | `8EF5310EBEB00EA0` | supported at NTSC timing (see below) |
| USA v1.0 | `TONY HAWK PRO SKATER`, NTFE, 0 | `fc1b4dec85e6874fa7321edc24f5a1e78600d9d0` | `5ed7e392198a5fa56ee37ea9e93a8d50` | `E771EA04C14F3429` | supported, full suite |

- Europe is the same program as v1.1 (it runs v1.1's recompiled code; four splash images and one
  instruction differ). The game is PAL-aware at run time (it reads `osTvType`), but the runtime paces
  retraces at 60 Hz and the frame sizes are NTSC's, so the host runs Europe with `osTvType = NTSC`
  (`tv_default` in `decomp/common/games.toml`). `--tv pal|ntsc|mpal` overrides; PAL is experimental: the picture is
  PAL-sized and everything runs at 60 Hz instead of 50. Real PAL needs a runtime change
  (`patches/ultramodern-vi-rate.patch`, not applied to the pinned runtime).
- USA v1.0 is a different link of the same sources, so it has its own recompiled payload (code class
  `us10`) inside the same binary. Build it with `tools/gen.py` (every class under `versions/` is generated).
- `--version ID` (a `games.toml` row: `thps1`, `thps1_eu`, `thps1_us10`) picks which stored ROM to run when
  several are stored; without it the first stored one in the table's order runs.

## Run (play)

```sh
build/cmake/thps1_recomp --rom /path/to/thps1.z64
```

The window runs until you close it. The ROM is checked (XXH3
`0xB7B085A35E270C23` of the big-endian v1.1 ROM; `.z64`/`.n64`/`.v64`
accepted) and a copy is kept in `--config` (default
`~/Library/Application Support/THPS1-64Recomp`, or the folder holding a
`portable.txt`), so later runs need no `--rom`. Controller Pak saves go to
`<config>/saves/thps1_pak1.mpk` (standard 32 KiB .mpk; `.bak` = previous).

**Controls.** THPS1 puts its four trick buttons on the **C buttons** (OPTIONS >
PLAYER 1 CONTROLS shows it): N64 A and B are only read by the menus. The
default bindings therefore put the tricks on a controller's face buttons, as
in the PlayStation and Xbox Tony Hawk games:

<!-- table-ok: our own default control bindings -->
| THPS1 action | N64 button (game) | Xbox / SDL controller | Keyboard |
|---|---|---|---|
| Ollie (hold, release to jump) | C-down | **A** (also N64 A = menu accept) | Space (also N64 A), K |
| Flip trick | C-left | **X** | J |
| Grab trick | C-right | **B** (also N64 B = menu back) | L |
| Grind / slide | C-up | **Y** | I |
| Spin (with the stick) | L / R | LB / RB or RT | Q / E |
| (Select; unused in game) | Z | LT | S |
| Pause | START | Menu (Start) | Return |
| Menu accept / back | A / B | A / B (the same buttons as ollie / grab) | Space / D |
| Skate / menus | stick, D-pad | left stick, D-pad | arrows |
| C buttons directly | C | right stick | |

Tricks are direction + button, as on the N64: e.g. ollie (A), then in the air
right + X = a flip trick, B (+ direction) = a grab, Y near a rail = a grind.
This is the **`thps-xbox`** preset (the default; "south = ollie, north = grind,
east = grab, west = kick/flip", as in the Xbox-era Tony Hawk games). The other
preset, **`n64`**, is the plain N64 layout (A south, B west, the C buttons on the
right stick / Y / B / RB / RS): `--controls-preset n64`, back with
`--controls-preset thps-xbox` (also `--control "preset NAME"`). A preset replaces every
binding and is saved; the previous file is kept as `controls.cfg.bak`.

A and B send two N64 buttons at once: A = ollie (C-down) + menu accept (A), B = grab
(C-right) + menu back (B). That is safe because the game reads N64 A/B only in menus, never in
the skating code (checked: `level_controls` sees no trick record for N64 A or B alone;
`level_grab` presses B and Y in the air and the level goes on). The visible effect is in the
pause menu, where B (back) resumes the level (`pause_back`).

Bindings are in `<config>/controls.cfg` (edit it, or `--control bind`; its `preset =` line says
`thps-xbox`, `n64` or `custom`). Moving off the old layout is automatic: a file that is exactly a
layout an earlier build generated (the earlier N64 one; any field order, lines may be missing) and
has no `preset =` line is rewritten once to `thps-xbox`, with the old file saved as
`controls.cfg.pre-xbox.bak` and one log line. A file you changed by hand is never touched.
A second pad is player 2.

The in-game PLAYER 1 CONTROLS screen (OPTIONS) can swap which C button does which action
(left/right on a row; it also has RESET TO DEFAULT). That happens inside the game, after
these bindings, and **it is saved in the career save**: SAVE CAREER writes the four-entry
action table (identity 0,1,2,3 = default) as big-endian words at payload offset 2448 of the
2,592-byte note . If a loaded career has a swapped scheme, open OPTIONS > PLAYER 1
CONTROLS > RESET TO DEFAULT and save the career again. The scheme is kept nowhere else (OPTIONS
has LOAD DATA but no SAVE DATA), so a fresh pak or no save always starts on the default scheme.

Options:
- `--mute` no sound device (audio still runs, paced by a virtual device);
  `--wav PATH` also records the game's audio; `--audio-fifo N` sets the
  host queue depth at which `osAiGetStatus` reports "FIFO full" (800).
- `--controls-preset thps-xbox|n64` (see Controls). `--windowed` / `--fullscreen` (saved to `graphics.cfg`).
- `--no-pak` (no Controller Pak), `--rumble-pak` (a Rumble Pak instead of
  the Controller Pak: pad rumble, no saves), `--save-dir DIR`.
- `--seconds N` quit after N s; `--no-keyboard`; `--press SEC:BUTTONS:DUR`
  scripts port 1 (`A B Z START L R UP DOWN LEFT RIGHT CU CD CL CR` and the
  analog stick `SUP SDOWN SLEFT SRIGHT`; join with `+`).
- The terminal stays quiet by default (settings line, warnings, errors, saves,
  crash reports). `--verbose` adds the per-second `status` (tasks, loader
  counters), `audio` (frames/s, non-silent buffers, peak, queue depth,
  FIFO-full answers) and `perf` lines (displayed fps, gfx/audio tasks, VIs,
  time in `send_dl`/`update_screen`, presents skipped while the window is
  occluded), the `[dl]` display-list summaries and the boot diagnostics;
  `--control` keeps the per-second lines too (the test runner reads them).
  `--show-fps` shows the counter in the window title.
- `--no-pads` ignores physical game controllers (headless test runs; the
  `--control vpad` virtual pad still works). `--no-edge-fix` turns off the
  scissor fix for the never-cleared last column/row (A/B; see "How the rest
  works").
- Evidence dumps (**ROM-derived: keep them local**), into `--dump-dir DIR`:
  - `--rt64-dump-every N` / `--rt64-dump-frames a,b`: RT64's own output
    (Metal), read back from RDRAM at the VI origin, for displayed frames.
  - `--dump-frames 300,600` / `--dump-every N` (gfx tasks): `dl_inspect`'s
    textures + software composite. Slow (stalls the gfx thread up to
    ~0.3 s per dump), so expect dropped frames while it runs.
  - `--dl-log N` / `--dl-every N` display-list summaries.
  - `--present-dump-every N`: every Nth *presented* frame as the window shows
    it (after upscaling, MSAA resolve and the VI pass), via the RT64 patch:
    `present_NNNNNN_WxH.png`. It is composited into its own target, so it
    works with the window occluded or `--hidden`. `--present-size WxH`
    (default: the window's size), `--present-pair` (also
    `present_NNNNNN_native_*.png`: the same frame's native framebuffer from
    RDRAM). The `perf` line counts `presented/s` (composited), `window/s`
    (actually presented) and `present_dumps`.
- Graphics (saved to `<config>/graphics.cfg`; a flag overrides and is saved):
  `--aspect original|16:9|21:9|expand` (expand = follow the window; default 16:9),
  `--window WxH` (1280x720), `--res-scale N` (internal resolution multiplier,
  0 = auto from the window, the default), `--msaa 0|2|4|8` (default 4; Apple GPUs
  have no 8x, RT64 then turns MSAA off: see `[thps] gfx effective`),
  `--refresh original|display|N` (frame interpolation target, default `display`;
  `original` = the game's 30 fps). For a 16:9 picture use a 16:9 window too.
  See [Graphics defaults](#graphics-defaults-and-high-frame-rate).
- High frame rate: `--hfr-tags 0` (RT64's automatic pairing only, no cut handling),
  `--hfr-cut-jump F[:MIN]` / `--hfr-cut-angle DEG` (camera-cut thresholds, default 8:40 and 25).
- `--hidden` (never show the window: frames are composited, not presented),
  `--cull-extra K` (scale the widescreen cull widening; 0 = off, for A/B),
  control `split [on|off]` (the `split` setting live for one run, for A/B, and the split-screen counters).
- `--always-present` (present even when the window is occluded),
  `--null-audio` (don't run the audio microcode).
- `--control`: read commands from stdin, one per line, each answered with
  `[ctl] ok <cmd> ...` (used by the tests): `press BUTTONS [HOLD [GAP]]`
  (held for HOLD *game input polls*, then released for GAP polls, so it works
  the same at 30 fps and at 3 fps), `shot PATH` (RT64 readback of the next
  displayed frame), `dl [N]` (triangle/matrix counts of the next N gfx
  tasks), `audio` (RMS/peak since the last `audio`), `edges N [DIR]`
  (frame-to-frame change of the left/right border bands of the next N
  *presented* frames, i.e. RT64's final image; DIR also gets the first 6 as
  PNGs), `peek`/`poke`/`ramsave`, `vpad`, `bind`, `stats`, `wait FRAMES`,
  `quit` (EOF on stdin also quits).  adds `pcap EVERY [DIR]` (present captures
  on/off at run time), `dltrace` (trace the next gfx task), `hfr` / `hfrdbg` / `hfrcam`
  (pairing counters, the next frame's paired/unpaired transforms, camera-cut detector),
  `latency BUTTONS` (press -> first present where the menu cursor moved), `border [original|fill]` (the border setting
  live for one run, for A/B, and the crop counters). Full list in
  `src/control.cpp`.

## Tests

```sh
tools/test.sh --record   # first time on a machine: capture reference frames (~3 min)
tools/test.sh            # controls.cfg test + whole suite: ~255 s on an M2 Pro (load 4-9); exit 1 on any failure
tools/test.sh --controls-cfg           # only the controls.cfg migration/preset test (no ROM, ~15 s)
tools/test.sh --only pak_save          # one scenario (+ the ones before it in its session)
tools/test.sh --rerun-failed           # only what failed last time
tools/test.sh --check-refs             # how distinct the recorded references are
```

`tests/run.py` starts `thps1_recomp --control --mute --no-keyboard` once per
**session** and walks the game through **scenarios**, waiting for
**checkpoints** instead of sleeping: it asks for RT64 frames (`shot`) until one
matches the checkpoint's reference, and only then sends the next input. A
press that the game drops (menus ignore input while they fade in) is repeated
only while the previous screen is still showing. Menus are navigated by
finding the highlighted (gold) entry in the frame, so they need no references.
Only one host runs at a time (`build/tests/.lock`; the runner waits up to
10 min for any other `thps1_recomp` to exit). It records `uptime` in each log
and, if the load average is above 2 x the CPU count, multiplies timeouts by 3
and turns the fps check into a warning.

<!-- table-ok: our own regression scenarios, described by what they check -->
| Session | Scenario | Checks |
|---|---|---|
| frontend | `boot_logo` | boots to the Activision logo (Expansion Pak notice + legal screen before it) |
| | `title` | START during the logos/attract demo -> title, PRESS START |
| | `main_menu` | START -> main menu |
| | `freeskate_level` | FREE SKATE -> rumble notice -> skater -> board -> Warehouse -> loading tip -> in level (HUD template); `dl`: >= 500 triangles per gfx task (3.8k seen) |
| | `level_audio` | 150 frames in level: RMS >= -40 dBFS and non-silent buffers (about -15 dBFS seen); the session's `--wav` is also checked (last 8 s) |
| | `level_fps` | median displayed fps over 10 s >= 28 (warning only on an overloaded machine) |
| | `level_controls` | with the default bindings, a virtual pad's A / X / B / Y press the game's ollie / flip / grab / grind records (its PlayStation-style pad layer at `0x800D49E0`); N64 A or B alone presses none |
| | `level_ollie` | virtual A held 10 frames and released: the skater is airborne (CBruce physics state, skater pointer `0x800D61A8`) |
| | `level_trick` | virtual A, then right + X in the air: a trick counter goes up (`Trick_Trick`); "went up" = any counter rose (others decay on landing) |
| | `level_grab` | virtual A, then B + right and Y in the air: airborne, and the level goes on (HUD template still matches): N64 B sent with the grab doesn't leak into a menu handler |
| | `border_stable` | pause menu: the border bands of the presented frames don't change (`edges`; also on the title and, in `pak_save`, the TAPE CHALLENGES screen). At the 16:9 default these are the widescreen side bands; the 4:3 border (scissor fix) is checked in `cam_ref_43` |
| | `pause_back` | pause menu: virtual B (N64 B = back, + C-right) resumes the level |
| widescreen (`--aspect 16:9 --window 1280x720 --res-scale 2 --hidden`, own config dir) | `ws_menu` | boot to the main menu with the 4:3 references: RT64's RDRAM copy stays native 4:3, so the game-visible frames must not change |
| | `ws_level` | FREE SKATE -> Warehouse as above, then the newest present capture (`--present-dump-every 30`) is 1280x720 and at most 15% of the bands outside the central 4:3 is unrendered (3.4% seen); median fps >= 28 |
| pak (blank pak) | `pak_empty` | OPTIONS -> LOAD DATA: "NO TONY HAWK GAME NOTES FOUND." |
| | `pak_save` | CAREER -> NEW GAME -> Warehouse -> pause -> END RUN -> STATISTICS -> SAVE CAREER -> YES -> name "A" -> SAVE SUCCESSFUL; host log `pak 1: wrote 2592 bytes ... note 0`; the `.mpk` hash changes |
| pak-reload (new process, same pak) | `pak_list` | OPTIONS -> LOAD DATA lists the note ("A") |
| | `pak_load` | select it: host log `pak 1: read 2816 bytes at 0 of note 0`; CAREER then opens with CONTINUE GAME enabled and selected (on a blank pak the cursor starts on NEW GAME) |
| qol / qol-reload | `skip_intro`, `fps_counter`, `vpad_bindings`, `crash_log`, `bindings_persist`, `volume_zero` | the settings checks (skip intro, fps counter, bindings, crash log, volume) |
| cam-43 (`--aspect original --window 960x720`) | `cam_ref_43` | Warehouse paused 200 polls after the start (reference `paused_w90`); `edges` of the 4:3 border |
| cam-219 (`--aspect 21:9 --window 1680x720`) | `cam_same_219` | the same native frame as at 4:3 (camera unchanged), side bands filled |
| dropout-219, dropout-169, dropout-fit (21:9, 16:9, following the window) | `dropout_*` | the paused `cam-219` frame captured with the cull planes widened 1x, 4x, not at all (4:3) and 1x again (`cull K`): the two 1x captures match, and 4x matches 1x in the side bands, so nothing the wide picture shows is culled (`present_cmp`) |
| two-players-169, -219, -169-hudorig (`--aspect 16:9` / `21:9`, two virtual pads; the last with `--hud original`) | `two_players_*` | TWO PLAYERS > GRAFFITI: the split screen fills the wide picture (`present_split`: >= 90 % of the side-band columns drawn), each player's HUD block at its own view's left edge (`split` counters: groups at q0 and q2), each pad on its own port |
| two-players-169-splitorig (`--aspect 16:9 --split original --hud expand`) | `two_players_169_splitorig` | both views in the 4:3 middle: black side bands, each player's HUD with its view (`present_bands_clear`: the side bands are black; `split` counters: `kept` > 0, no group placed, `bands` reported). Shared: `tests/hud_sessions.py` |
| two-players-43 (`--aspect original`) | `two_players_43` | the paused split screen at 4:3: `split on`, `off`, `on` give the same picture (0 % of pixels differ) |
| crop, crop-219, crop-43 (`--border fill`; 16:9, 21:9 at 1280x540, 4:3) | `crop_level_*`, `crop_pause_*`, `crop_menu_toggle` | Warehouse: each outer band of the presented frame holds picture (`border` step: >= 90 % of its lines), the stats count cropped tasks; the pause menu's bands are still (`edges`); Graphics > Picture Border switches the frame back and forth at run time (graphics.cfg) |
| border-default (16:9, no flag) | `border_default` | the default leaves the black frame (every band <= 5 % picture) and crops no task |
| two-players-169-crop (`--aspect 16:9 --border fill`, two virtual pads) | `two_players_169_crop` | TWO PLAYERS > GRAFFITI, paused: both split views reach the window's edges (`border`: picture in all four bands), the split halves are cropped (`crop_halves`) and still widened (`split` views); `border original` (live) brings the black frame back and changes 1 % to 15 % of the pixels (the frame is about 11 %) |
| hfr (`--refresh 60 --hidden --skip-intro`) | `input_latency` | main menu: median of 6 DOWN/UP presses -> first present with the cursor moved <= 100 ms (~22 ms seen) |
| | `hfr_motion` | Warehouse, stick up 4 s, every present captured: frame_motion on a 60 Hz timeline >= 0.9 (1.0 seen; 0.5 at 30 fps), even steps (alternation <= 0.3; 0.01 seen, 1.0 at 30 fps), RT64 interpolating >= 90 % of game frames, >= 60 % of transforms paired (87–98 %), <= 5 % in-between frames dropped (0), fps >= 28 |
| | `hfr_cut` | pause -> RETRY: the host logs a camera cut and that frame is not interpolated |
| menu / menu-reload (`tests/menu_session.py`, skipped with `--features` `menu=0`) | `menu_hint`, `menu_open_close`, `menu_blocks_pad`, `menu_settings_click`, `menu_pad`, `menu_persist` | the in-game settings menu: the one-time hint; Esc opens and closes it over the game (checked in the presented frame); it blocks the pad; clicks change Show FPS, MSAA and Aspect and reach `general.cfg` / `graphics.cfg`; pad navigation and the layout pick, the volume slider; the settings persist in a new process and the hint does not return |
| course-cycle (`tests/course_cycle.py`) | `course_cycle` | four courses back to back (pause -> END RUN -> select): the host log shows a song load at every course start, with any old-song channels still reading the shared buffer stopped first (`src/music.cpp`, `Music_LoadSong` hook); no crash; 150 frames of the last course have music (RMS >= -40 dBFS) |

Full run, 2026-10-12, USA v1.1, Europe and USA v1.0 (static build): **35 pass, 0 fail, 4 skipped** (the four need the optional launcher build).
`tests/firstrun_test.py` (build from a dump on first run, play, the menu hint) passes 15 of 15.

The exact input scripts are the step lists in `tests/scenarios.py`. The save
does not need a 2-minute run: END RUN from the pause menu ends the run, and the
end-of-run menu has SAVE CAREER.

**Reference frames** are ROM-derived, so they stay in `build/tests/refs/`
(gitignored). Only the scenario definitions, regions and tolerances are
committed. To make references on a new machine: build, then
`tools/test.sh --record`. This captures each missing checkpoint at the timing in
its `record` field, and writes `build/tests/refs/sheet.png` (+ `sheet.txt` with
the order). Look at the sheet, check that every frame is the screen its name
says, then run `tools/test.sh --check-refs`: every other reference must be more
than 1.2 x the tolerance away. Then run `tools/test.sh` twice. To redo them all,
use `--rerecord`. Matching is resolution-independent: regions are fractions of
the frame, compared as normalised luma grids (fade- and brightness-proof), or for
the HUD as a colour template of the reference's bright pixels.

Output: `build/tests/out/<time>/` holds `results.json` (status, seconds,
frames, checkpoint distances, notes per scenario), each session's `host.log`,
a PNG of every checkpoint as matched, and `failure_sheet.png` with the last
frames polled before a failure. The newest 10 runs are kept.

## Graphics defaults and high frame rate

Measured on an M2 Pro (`tools/gfx_matrix.sh`). Warehouse, 16:9, 60 Hz interpolation.
Every configuration held 30.0 game fps, 60.0 presents/s and dropped no in-between frames.
Times are RT64 render time per game frame (two display frames, GPU waits included):

| res-scale | MSAA off | 2x | 4x |
|---|---|---|---|
| 1 | 2.2 ms | 2.4 | 2.3 |
| 2 | 2.3 | 2.4 | 2.6 |
| 3 | 2.7 | 3.0 | 3.8 |
| 4 | 3.4 | 4.0 | 5.6 |
| 9 (native 4K) | | | 18.2 |

MSAA in widescreen needed an RT64 fix: new render targets are cleared, otherwise the never-drawn
right-edge columns showed magenta (`patches/rt64-hfr.patch`).

**Defaults** (`<config>/graphics.cfg`, or the matching flags, which are saved back):

| Setting | Default | Flag | Values |
|---|---|---|---|
| aspect | `16:9` | `--aspect` | `original` (4:3), `16:9`, `21:9`, `expand` (follow the window) |
| window | `1280x720` | `--window WxH` | initial window size (`--fullscreen`) |
| res_scale | `0` | `--res-scale N` | internal resolution; 0 = integer scale of the window (3x here, 9x fullscreen on 4K) |
| msaa | `4` | `--msaa` | 0, 2, 4 (8 isn't offered by Apple GPUs: RT64 turns MSAA off) |
| refresh | `display` | `--refresh` | `original` (the game's 30 fps), `display` (the display's rate: 60, 120 on ProMotion), or N (30..1000) |
| hud | `expand` | `--hud` | HUD placement in widescreen: `original` (the HUD stays in the centred 4:3 area, as on a TV), `16:9` (score, special meter, tips... move to the edges of a 16:9 picture, also at 21:9), `expand` (the default: to the edges of the window's picture; the same as `16:9` in a 16:9 window). Nothing moves at `--aspect original`. Menu: Graphics > HUD Placement. Menus, loading screens, the pause menu and result pages always stay a centred 4:3 page. In a widened two-player split screen each player's HUD block goes to its own view's edge, with `original` too (the views fill the picture there; `16:9` uses the halves of a 16:9 picture) (`src/hud_anchor.cpp`; the same setting works in THPS2 and THPS3, rules per game in `game/game.toml`) |
| split | `wide` | `--split` | two-player split screens in widescreen: `wide` each player's view fills its half of the wide picture (RT64 patch `rt64-splitscreen-widescreen.patch`), `original` both views stay in the centred 4:3 area (the picture before v0.2), black side bands, each player's HUD where the game draws it, whatever `hud` says. Nothing changes at `--aspect original`. Menu: Graphics > Two-Player Split Screen. Tests `two-players-169`, `-219`, `-169-hudorig`, `-169-splitorig`, `-43`, `menu-hud` |
| border | `original` | `--border` | the game's 8 px frame around the 3D picture (scissor and depth clear inset by 8 px; a TV hid the edge): `original` keeps it, `fill` widens the inset scissor and clears to the whole 320x240 frame and drops the black top/bottom bands, so the 3D reaches the window's edges at every aspect, same scale (no zoom). 320-wide 3D frames only: the 640x480 front-end pages keep their frame. Menu: Graphics > Picture Border (`src/border_crop.cpp`; tests `crop*`, `border-default`) |

A `graphics.cfg` written before  that still holds exactly the old defaults (4:3, 960x720,
no MSAA; the host saved them on first start) is moved to these once, with a log line; a file
with any value you changed keeps it (a missing `refresh` line means `display`).

HUD Placement defaults to `expand` (2026-10-14). Builds before that saved `hud=original` on their first start, so a `graphics.cfg` without a `cfg_rev` line that says `hud=original` is moved to `expand` once, with a log line,
and stamped `cfg_rev=2` (a line the host writes itself); from then on `hud=original` is a choice and stays (`tests/gfx_cfg_test.py`). Other values are never touched.

How the interpolation works (`src/interpolation.cpp`):
- RT64 renders in-between frames and pairs each transform with the previous frame's.
  THPS1's matrices suit this well: world-space model matrices that are loaded, never pushed,
  and a view-projection camera.
- The host tells RT64 the game's rate (30) on every task.
- On a camera cut (level start, RETRY, any jump of the camera), it tags that frame
  `G_EX_ID_IGNORE`, so the cut isn't swept. The RT64 calls go through our patch's
  `Interpreter::commandHook`; nothing is written into the game's memory.
- `refresh=original` restores the plain 30 fps output.

Input latency (`--control latency`): about 22 ms from the poll that delivers a press to the
first presented frame showing the menu cursor moved, at 30 and at 60 Hz. The game reacts in the
frame it polls, its scheduler starts gfx tasks without waiting for a retrace, and RT64's
PresentEarly shows the frame before the VI swap. So no scheduler patch was needed.

## How it works

Boot, frame pacing, audio, input, Controller Pak, widescreen and interpolation: [docs/internals/recomp.md](../../../docs/internals/recomp.md).

## Not done

- No in-game pak swapping (start with `--rumble-pak` for rumble, untested on a real pad).
- Controller Pak: the in-game pak manager (delete notes, repair) is not
  exercised by the tests.
- Widescreen: the in-level HUD is anchored to the screen edges by default (`--hud expand`, `src/hud_anchor.cpp`; `--hud original` keeps
  it centred 4:3). It keeps its 4:3 size. 2D menus and loading screens are
  pillarboxed 4:3. At 21:9 a far wall can still drop out at the right edge.
- High frame rate: tested in the Warehouse only (other levels have cars and other moving
  objects: check pairing with `--control hfrdbg` there). The cut detector looks at camera motion;
  replays (`Video_Playback` camera switches) and the competition intro aren't tested yet.
  At 120 Hz (`refresh=display` on the built-in ProMotion panel) the defaults held 120 presents/s
  with no dropped frames (6.1 ms render per game frame).
- Texture packs: not attempted. The in-game settings menu (Esc) has no rebinding of single keys or buttons yet (edit `controls.cfg`).

