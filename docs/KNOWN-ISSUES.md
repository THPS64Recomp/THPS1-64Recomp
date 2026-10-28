# Known issues

What isn't finished or hasn't been checked in v0.2.0. "Untested" means the code exists but hasn't been run in that
setting. Problems fixed before this release are in the [CHANGELOG](../CHANGELOG.md). Found something that isn't here?
[TESTING](TESTING.md) says how to report it.

## Platforms

- **macOS (one universal app) and Windows x64 only.** Linux isn't in this release: its code builds in CI, with stand-in
  game code, but has never been run.
- **Intel Macs are untested.** The app's Intel half has only run under Rosetta on an Apple Silicon Mac. Which Intel GPUs
  RT64's Metal renderer supports hasn't been checked.
- **Windows has been tested on one PC:** Windows 11, an Intel Core i7-8809G with AMD Radeon RX Vega M, Direct3D 12, 150 %
  display scaling. Untested: other GPUs (NVIDIA, Intel), Windows 10, other display scaling, and a controller on Windows.
- **Windows: the first start of a new copy is slow to show a picture**, about 4.5 s on the test PC. Later starts are fast.
  It happens with each newly written program file, even with an existing config folder (probably the GPU driver's
  shader cache).
- **Windows: frame pacing is a little less even than on macOS.** Both hold 60 frames per second, but the slowest 1 % of
  frames take about 18.4 ms on the test PC against 16.9 ms on the Mac.
- **The app isn't notarized (macOS) or code-signed (Windows)**, so the first start needs the one-time Gatekeeper or
  SmartScreen step in the [README](../README.md#install).
- **The missing-compiler page** on macOS was tested with a simulated missing compiler, not on a Mac without the Command
  Line Tools.

## Game versions

- **USA v1.1, USA v1.0 and Europe are supported** ([MANUAL](MANUAL.md#your-game-dump)). Any other release or game is refused.
- **Europe runs at 60 Hz**; the PAL console ran it at 50 Hz. `--tv pal` is experimental (a PAL-sized picture, still paced at
  60 Hz). Real 50 Hz needs a runtime change this project hasn't applied.
- **Hand play.** All three releases pass the automated suite. USA v1.1 has been played by hand on macOS in several rounds,
  USA v1.0 and Europe in a shorter session each, and all three on Windows.

## Graphics

- **Widescreen:** the 3D view is widened and the in-level HUD moves to the screen edges (`hud = expand`; `original` keeps
  it in the centred 4:3 area). The HUD keeps its 4:3 size, and a few elements (the timer, trick lines, the pause menu,
  result pages) stay centred on purpose. Menus, loading screens and other 2D screens are pillarboxed 4:3. In **two-player**
  split screen each player's view fills its half of the wide picture, and each player's HUD sits at its own view's edge.
- **Frame interpolation** at 60 Hz and up pairs 97 to 99 % of the moving parts between game frames in the Warehouse and
  the menus. Other levels have cars and other moving objects whose pairing hasn't been checked. Replays and the
  competition intro are untested.
- **Each level start freezes the picture for about 0.13 s** while the game loads the level (0.2 s in v0.1; unpacking
  and clearing memory now run natively). What remains is the game's own load, which runs in one go as on the console,
  and RT64 showing nothing new for about two more frames after it. The **attract demo** pauses for 60 to 85 ms when it
  loads the next skater (90 to 130 ms in v0.1), more visible in Low Power Mode.
- RT64 **compiles a shader the first time an effect appears.** In a 36-minute soak test that caused one stall of about
  0.4 s, at the first level after the start.
- With the window hidden or covered, the app stops presenting frames; the game keeps running.
- Apple GPUs have no 8x MSAA; asking for it turns MSAA off.
- **Draw distance:** 2x, 4x and Full were checked on one 15-second ride per course (all at 30 fps), not in long play, two-player
  split screen or the competition cameras. The step back reacts one frame late, so in a very busy view one frame can show an
  object out of place. At Full the fog is effectively off.

## Stability

- **A crash in the graphics layer** (inside RT64, seen about once in 40 test sessions under load and once in hand play) is
  fixed in this release. With the fix, a stress test that crashed 2 runs in 14 crashed none in 34. If you see a crash,
  please send `crash.log`.
  Long unattended runs (soak tests) found no crash or hang: 2 h 40 min on macOS, and 1 h plus two 30-minute runs on Windows.

## Input and saves

- **Player 2:** by default the first controller to press a button is player 1 and the next is player 2. The Controls
  tab's Controllers list can swap them or give a controller either player; that choice lasts until you quit
  ([MANUAL](MANUAL.md#controls)). The keyboard is always player 1.
- The game's own PLAYER 1 CONTROLS remap is saved in the career save, so a swapped scheme travels with a save.
- **Cheats are test aids:** off by default. They aren't stored in the Controller Pak save, but progress you make with a
  cheat on (tapes, scores, levels unlocked by playing) is saved as usual. While one is on, the log and `crash.log` name it ([MANUAL](MANUAL.md#cheats)).

## Audio

- Audio comes from the translated audio microcode. The test suite checks its level and spectrum; it isn't claimed to be
  bit-exact with the console.

## Untested

- The **Rumble Pak** on a real controller, and the game's own **Controller Pak manager** (deleting or repairing notes).
- **PAL 50 Hz** (see Game versions).
- **Replays.**

## Not in this release

Texture packs, mods, and a launcher beyond the first-start window.
