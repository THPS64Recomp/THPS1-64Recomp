# Manual

How to use THPS1 64: Recompiled: the game dump, the first start, controls, settings, cheats, command-line flags and files.
Installing is covered in the [README](../README.md#install).

Everything the app writes goes to its config folder: `~/Library/Application Support/THPS1-64Recomp/` on macOS,
`%LOCALAPPDATA%\THPS1-64Recomp\` on Windows, or the folder holding a `portable.txt`. It's all plain text except the saves.

## Your game dump

Three releases of the cartridge are supported. The app identifies a dump by hash, never by its file name, and converts
`.n64` and `.v64` dumps to the big-endian `.z64` form first. All three are 12 MiB.

| Release | Header name, code, revision | SHA-1 | MD5 | XXH3-64 |
|---|---|---|---|---|
| USA v1.1 | `TONY HAWK PRO SKATER`, NTFE, 1 | `4900b6c92fb8df1765e91e891dccc525bb102fe1` | `aff424a1883dc7bb92c7b2ebe9342f85` | `B7B085A35E270C23` |
| USA v1.0 | `TONY HAWK PRO SKATER`, NTFE, 0 | `fc1b4dec85e6874fa7321edc24f5a1e78600d9d0` | `5ed7e392198a5fa56ee37ea9e93a8d50` | `E771EA04C14F3429` |
| Europe | `TONY HAWK SKATEBOARD`, NTFP, 0 | `c321cd05eec58765467878ac8015784535280e3c` | `c9e9c4a18b1540c6b4111331d7c663b8` | `8EF5310EBEB00EA0` |

- To check a dump: `shasum -a 1 your.z64`, or start the app with `--check-rom FILE`, which says what a file is.
- The app refuses other games, other platforms' versions and modified dumps. For a dump of this game with an unknown hash
  it shows the SHA-1, which is useful in a bug report.
- **Two recipes cover the three releases.** The first-start build uses a recipe (the list of where each function starts,
  plus a fingerprint of the code). USA v1.0 is a separate link of the program, so it has its own (`us10`). Europe is the
  same program as USA v1.1 apart from 230 words, so it uses v1.1's recipe (`us11`). Details:
  [docs/internals/versions.md](internals/versions.md).
- **Several releases:** `--rom FILE` adds another dump, and `--version ID` picks the one to run: `thps1` (USA v1.1),
  `thps1_us10` (USA v1.0) or `thps1_eu` (Europe).

### Why Europe runs at 60 Hz

Europe is the PAL release. The app runs it with the console's TV type set to NTSC, as other N64 recomps do with PAL games:
the runtime paces video at 60 Hz, and the game scales its own timing from the TV type, so you get full-speed play. What
differs in Europe (the title screen, four splash images, a few instructions) still shows. Real 50 Hz would need changes
to N64ModernRuntime for no gain in play. `--tv pal` is an experimental override: a PAL-sized picture, still paced at 60 Hz.

## The first start

1. The **Choose your game** window opens. Click **Choose ROM...**, drag the dump onto the window, or start the app with
   `--rom FILE`. Each problem has its own page: the file can't be read, it isn't an N64 ROM, it's a different game, or
   it's this game but not a known dump.
2. A copy of the dump goes into the config folder, so the game can be rebuilt after an update. It never leaves your machine.
3. **The build.** The app translates the game's code to C with the bundled N64Recomp and RSPRecomp, compiles it, and loads
   the library. The window shows each step, and **Cancel** stops cleanly. On an M2 Pro it takes 4.5 s with 10 cores and
   18 s with one.
4. **No compiler (macOS)?** The app checks for Apple's Command Line Tools without opening Apple's installer. If they're
   missing it shows **Install** (which opens Apple's installer, only when you click it), **Retry** and **Quit**. Or run
   `xcode-select --install` yourself. If the compiler fails because the Xcode licence isn't accepted, run
   `sudo xcodebuild -license accept` once.
5. The game starts. A hint about the settings menu shows once, a few seconds in.

If a step fails, the page names it, shows the end of the log, and offers **Open log folder**, **Retry** and **Quit**. Every
command and its time is in `first-run.log`, and the build's own logs stay in `game/work-<class>/logs/`. Those logs hold only
compiler output, so they're safe to attach to a bug report.

The library is rebuilt only when the app, the recipe or the dump changes, or if the library fails to load. `first-run.log`
says which happened. If the app builds again on every start, it's probably using a new config folder each time (for
example a moved app with `portable.txt` left behind): check the folder named in the first line of the log.

## Controls

THPS1 reads its four trick buttons from the **C buttons**; N64 A and B only work in the menus. The default preset,
`thps-xbox`, puts the tricks on a controller's face buttons:

<!-- table-ok: our own default control bindings, not game data -->
| THPS1 action | N64 button | Xbox / SDL controller | Keyboard |
|---|---|---|---|
| Ollie (hold, release to jump) | C-down | **A** (also N64 A = menu accept) | Space (also N64 A), K |
| Flip trick | C-left | **X** | J |
| Grab trick | C-right | **B** (also N64 B = menu back) | L |
| Grind / slide | C-up | **Y** | I |
| Spin (with the stick) | L / R | LB / RB or RT | Q / E |
| (Select; unused in the game) | Z | LT | S |
| Pause | START | Menu (Start) | Return |
| Skate / menus | stick, D-pad | left stick, D-pad | arrow keys |
| C buttons directly | C | right stick | |

Tricks are a direction plus a button, as on the N64: ollie (A), then in the air right + X for a flip trick, B with a
direction for a grab, and Y near a rail for a grind. A and B send two N64 buttons at once (A is ollie and accept, B is grab
and back). That's safe because the game reads N64 A and B only in menus. One visible effect: in the pause menu, B resumes
the level.

- **Rebinding.** Open the settings menu (Esc, or Back on a controller) and its Controls tab. Under **Bindings**, each
  N64 input has a row with two controller slots and two keyboard slots, and the row names what the game does with it.
  Choose a slot (click it, or move to it and press Enter or A), then press the button, trigger or stick direction for a
  controller slot, or the key for a keyboard slot. Esc or Back cancels, Backspace or Delete empties the slot, and after
  5 seconds the slot gives up and stays as it was.
  - The change works at once and is saved to `controls.cfg` with `preset = custom`. The first change in a session keeps
    the file it replaces as `controls.cfg.bak`.
  - If another action already uses that button, the two trade: the other action gets the slot's old button. Menu
    accept and menu back (N64 A and B) may share a button with a trick, as the default layout does, so they keep theirs.
  - **Default** on a row puts that row back as the layout has it.
  - A slot shown in yellow differs from the layout you chose (Face buttons or N64), so you can see what you changed.
  - **Reset all to default**, below the rows, puts every binding back to that layout. It asks first: press it again
    (it now says **Confirm: reset all**) to do it; anything else cancels. The old file is kept as `controls.cfg.bak`.
- **Presets.** Controller Layout, at the top of the Controls tab, resets every binding to a layout: **Face buttons**
  (`thps-xbox`, the default) or **N64 layout** (`n64`: A south, B west, the C buttons on the right stick, Y, B, RB and
  RS). `--controls-preset n64` and `--controls-preset thps-xbox` do the same from the command line. The previous file is
  kept as `controls.cfg.bak`.
- **Editing `controls.cfg`.** The app reads it at start. Each line is `INPUT = FIELD, FIELD ...`, with up to four fields
  per input.
  - Inputs: `a b z l r start c_up c_down c_left c_right dpad_up dpad_down dpad_left dpad_right stick_left stick_right
    stick_up stick_down`.
  - Fields: `key:NAME` (an SDL key name such as `Space`, `Return`, `Left`, `A`; the keyboard counts on port 1 only),
    `button:NAME` (`a b x y back start leftstick rightstick leftshoulder rightshoulder dpup dpdown dpleft dpright`),
    `axis:NAME+` or `axis:NAME-` (`leftx lefty rightx righty lefttrigger righttrigger`), or `none`.
  - The `preset =` line says `thps-xbox`, `n64` or `custom`. The app never rewrites a file you edited by hand on its
    own; a change in the menu does, after keeping the old file as `controls.cfg.bak`.
- **Players 1 and 2.** By default, ports are given out by the first button press. Player 1 has the keyboard and the first
  controller that presses a button; player 2 is the next controller that presses one; a third is ignored. Moving a stick
  doesn't claim a port. Plug in or pair a controller at any time, then press a button on it. If player 1's controller is
  unplugged, player 2's becomes player 1.
- **The Controllers list** (Controls tab) shows each connected controller, which player it is and the buttons it's
  pressing right now, so you can tell two controllers apart. **Player 1** or **Player 2** on a controller's row gives it
  that player (a controller already there trades places with it), and **Swap players 1 and 2** trades them. The
  keyboard always belongs to player 1. With one controller set to Player 2, the keyboard alone is player 1, so the
  keyboard and one controller can play a two-player game. The choice lasts until you quit; at the next start, the first
  press decides again.
- **OPTIONS > PLAYER 2 CONTROLS** reads only the second controller in the original game. While no second controller is
  attached, the app answers port 2 with port 1's input in menus, so you can leave the screen. In a level, port 2 stays
  empty.
- **The game's own remap screen** (OPTIONS > PLAYER 1 CONTROLS) can swap which C button does what. That happens inside the
  game, after these bindings, and **is saved in the career save**. If a loaded career has a swapped scheme, open that
  screen, choose RESET TO DEFAULT and save the career again.

## The settings menu

**Esc** (controller: **Back**) opens the settings menu over the game. Its tabs:
- **General:** skip intro, show FPS;
- **Controls:** the layout presets, the Controllers list and rebinding (see [Controls](#controls));
- **Graphics:** aspect ratio, HUD placement, two-player split screen, picture border, resolution, MSAA, frame rate, window mode;
- **Sound:** volume;
- **Cheats:** see [Cheats](#cheats).

Move with the arrow keys or the D-pad, pick with Enter or A, change tab with LB / RB, and close with Esc, B or Back. The
menu writes the same files as the command-line flags (below). Full screen: Alt+Enter on Windows; on macOS, the window's full-screen button or Ctrl+Cmd+F.

## Settings files

The files are the source of truth; a change in the menu writes them.

### `general.cfg`
Written with defaults on the first start.

| Key | Default | Meaning | Flag (one run) |
|---|---|---|---|
| `skip_intro` | `0` | `1` boots straight to the title (no Expansion Pak notice, legal screen or logos) | `--skip-intro` / `--no-skip-intro` |
| `show_fps` | `0` | `1` shows presented and game frames per second in the window title | `--show-fps` / `--no-show-fps` |
| `volume` | `100` | master volume, 0 to 100 | `--volume N` |

### `graphics.cfg`
A command-line flag overrides the value and **is saved back**.

| Key | Default | Values | Flag |
|---|---|---|---|
| `aspect` | `16:9` | `original` (4:3), `16:9`, `21:9`, `expand` (follow the window) | `--aspect` |
| `window` | `auto` | the first window size: `auto` is 1280x720 (on Windows, enlarged by the display scaling); `WxH` is exact pixels | `--window WxH`, `--fullscreen`, `--windowed` |
| `res_scale` | `0` | internal resolution multiplier; `0` is an integer scale of the window (3x at 720p) | `--res-scale N` |
| `msaa` | `4` | `0`, `2`, `4` (Apple GPUs have no 8x; asking for it turns MSAA off) | `--msaa N` |
| `refresh` | `display` | `original` (the game's 30 fps), `display` (the display's rate: 60, or 120 on ProMotion), or a number from 30 to 1000 | `--refresh X` |
| `hud` | `expand` | HUD placement in widescreen: `original` (the centred 4:3 area, as on a TV), `16:9` (the edges of a 16:9 picture), `expand` (the edges of the window's picture). No effect at `aspect original`. Menus, the pause menu and result pages always stay a centred 4:3 page. In a widened two-player split screen each player's HUD sits at the edge of their own view, with `original` too | `--hud X` |
| `split` | `wide` | two-player split screen in widescreen: `wide` each player's view fills its half of the picture; `original` both views stay in the centred 4:3 area with black bands at the sides, as on a TV, and each player's HUD stays inside its view. No effect at `aspect original` | `--split X` |
| `border` | `original` | the thin black frame around the 3D picture. The game draws its 3D 8 pixels in from each edge of its 320x240 frame, and a TV hid that edge. `original` keeps the frame; `fill` draws the picture all the way to the edges of the window, at every aspect ratio. Fill shows a little more of the scene at the same size: nothing is cut off and nothing is zoomed. Menus and loading screens keep their own frame | `--border X` |

The file also holds a `cfg_rev` line that the app writes itself; leave it. Files from earlier builds that say
`hud=original` (the old default) are moved to `expand` once; choose `original` again to keep it.

For a 16:9 picture, use a 16:9 window. Camera cuts (a level start, RETRY) aren't interpolated. Input latency on an M2 Pro is
about 22 ms from the poll to the first frame that shows the effect.

## Cheats

The settings menu's **Cheats** tab (or one flag each, for one run) turns on aids that make play testing faster. They're
all off by default. They work through the game's own course select and cheat flags in memory, and **the cheats themselves
are never stored in your save**: turning them on and off leaves a career save byte-identical. **Progress you make while a
cheat is on is saved as usual**, though: tapes, scores, medals and levels you unlock by playing go into the career like any
other progress. While one is on, the log says so at the start and on each change, and `crash.log` names it.

| Cheat | Flag | What it does | Takes effect |
|---|---|---|---|
| Unlock All Levels | `--unlock-levels` | every course can be picked in SELECT COURSE (career, free skate, single session), the medal ones too; tapes and medals stay as they are | when the course-select cursor moves |
| Perfect Balance | `--perfect-balance` | grinds never lose balance (the game's own cheat) | at once |
| Slow Motion | `--slow-motion` | the game runs at half speed (the game's own cheat) | at the next course start or RETRY |
| Skip to Restart | `--skip-to-restart` | the pause menu gets SKIP TO RESTART, to jump to any start point of the course (the game's own cheat) | the next time you pause |

The menu stores them in `cheats.cfg` (`unlock_levels`, `perfect_balance`, `slow_motion`, `skip_to_restart`: `0` or `1`).
There's no such file until you change a cheat in the menu. A flag turns a cheat on for one run and isn't saved.

## Command-line flags

On macOS, from Terminal: `"/Applications/THPS1 64 Recompiled.app/Contents/MacOS/thps1_recomp" --flag`. On Windows, from PowerShell in
the app's folder: `.\THPS1-64Recomp.exe --flag`. The Windows program has no console window, so the shell doesn't wait for it. To
wait and see its exit code, pipe it: `.\THPS1-64Recomp.exe --check-rom FILE | Out-Host`, then read `$LASTEXITCODE`.

<!-- table-ok: the app's command-line flags -->
| Flag | Meaning |
|---|---|
| `--rom FILE` | identify this dump and store a copy (the first start, or to add another release) |
| `--version ID` | which stored release to run: `thps1` (USA v1.1), `thps1_us10` (USA v1.0), `thps1_eu` (Europe) |
| `--check-rom FILE` | print what a file is and exit |
| `--config DIR`, `--save-dir DIR` | use this config folder / this Controller Pak folder |
| `--features` | print the build's capabilities and exit |
| `--mute`, `--volume N` | silence / set the volume |
| `--no-pak`, `--rumble-pak` | no Controller Pak / a Rumble Pak instead (untested on a real controller) |
| `--no-keyboard`, `--no-pads` | ignore the keyboard / the controllers |
| `--api auto\|d3d12\|vulkan\|metal` | force a graphics API (macOS always uses Metal) |
| `--tv ntsc\|pal\|mpal` | the TV type reported to the game; every release defaults to `ntsc` (60 Hz), and PAL is experimental |
| `--build-game`, `--rebuild-game`, `--keep-game-work` | first-start build control: build and exit, force a rebuild, keep the work folder |
| `--unlock-levels`, `--perfect-balance`, `--slow-motion`, `--skip-to-restart` | a cheat for one run |
| `--verbose` | per-second status, audio and performance lines on the terminal |
| `--seconds N` | quit after N seconds |

Developer and test flags (`--control`, `--press`, `--dump-*`, `--present-*`, `--wav`, `--hidden` and others) are listed in
[the host README](../decomp/thps1/recomp-host/README.md). **What they dump is derived from the game: keep it local.**

Exit codes for scripts: 0 normal, 6 already running, 7 the config folder is missing or not writable, 10 you quit or
cancelled during the first start.

## Saves

Career saves go to a virtual Controller Pak, `saves/thps1_pak1.mpk`: a standard 32 KiB `.mpk` image. In the game, SAVE
CAREER comes at the end of a run (the pause menu's END RUN leads there), and OPTIONS > LOAD DATA loads. The previous file is
kept as `.bak`. To move a save, copy the file. There's no in-game pak swapping.

## Files

| What | Where, in the config folder |
|---|---|
| Your dump (a copy) | `thps1.n64.us.1.1.z64`, `thps1.n64.us.1.0.z64` or `thps1.n64.eu.1.0.z64` |
| The built game library | `game/thps1_game_<class>.dylib` or `.dll` (class `us11` for USA v1.1 and Europe, `us10` for USA v1.0) |
| Controller Pak saves | `saves/thps1_pak1.mpk` (and `.bak`) |
| Settings | `general.cfg`, `graphics.cfg`, `controls.cfg`, `cheats.cfg` |
| Crash report | `crash.log` |
| First-start build log | `first-run.log` |
| Instance lock | `thps1.lock` (one running copy per config folder) |

**Updating:** replace the app. Saves and settings are outside it and are kept; the game library is rebuilt once.
**Uninstalling:** delete the app, and the config folder if you also want to remove your saves, settings and the copy of
your dump. Back up `saves/thps1_pak1.mpk` first if you want to keep your career.

## Troubleshooting

| Problem | What to try |
|---|---|
| "Open Anyway" isn't there (macOS) | try to open the app first: the button appears only after a blocked start |
| "Windows protected your PC" | **More info**, then **Run anyway**; or tick **Unblock** in the zip's Properties before extracting |
| The build fails with a compiler error | read the log named on the page; run `xcode-select --install`, or `sudo xcodebuild -license accept` |
| A black window, or the game is slow | make sure no other copy is running; try `--msaa 0` and `--res-scale 1`; report your machine |
| No sound | check the output device, `volume` in `general.cfg`, and that `--mute` isn't set |
| A controller does nothing | press a button on it first: ports are given out on the first press |
| Saves are gone after an update | they live in `saves/`; if you switched to or from portable mode, copy `saves/` across |

## Questions

**What's in the download?** Our engine (the host code, N64ModernRuntime, RT64, SDL), the translator tools (N64Recomp and
RSPRecomp, unmodified), the recipes (names, addresses and sizes) and the licence notices. There's no game code or data in
it. Every release zip is scanned for copied ROM bytes before it's published ([VERIFICATION](VERIFICATION.md)).

**Why does it build something at the first start?** We can't distribute the game's code, so the app makes it on your
machine from your dump, once, and keeps the result there.

**Why does macOS need the Command Line Tools?** For the C compiler that compiles the translated code. The app checks for
them and never installs anything by itself. The Windows zip carries its own compiler.

**What does SmartScreen's "Unknown publisher" mean?** Only that the program has no signature (a certificate costs money and
needs a legal identity). Run anyway doesn't install anything or change any Windows setting. Windows normally asks once per
copy of the program.

**Which controllers work?** Any controller SDL knows: Xbox, PlayStation, Switch Pro and many others. Buttons go by position, as on an Xbox pad: on a Switch or other Nintendo controller the bottom button is ollie, whatever its label says.

**Is there a Linux version?** The code is written and builds in CI, but nobody has run it on a Linux desktop, so it isn't
in this release.

**What do I need to play?** A dump of the game's N64 cartridge (`.z64`, `.n64` or `.v64`; the README lists the supported
dumps). Download the zip for your system, start the app and choose your dump. It checks the dump and builds the game once;
later starts skip this.
