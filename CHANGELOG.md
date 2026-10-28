# Changelog

All notable changes to THPS1 64: Recompiled are listed here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Changes to the shared host are listed in the
[THPS64Host changelog](https://github.com/THPS64Recomp/THPS64Host/blob/main/CHANGELOG.md).

## [Unreleased]

## [0.2.0] - 2026-10-27

Built on THPS64Host v0.2.0: split screen, Picture Border, rebinding, draw distance and the Original and Enhanced
presets. It runs the USA v1.1, USA v1.0 and Europe releases of the N64 game, on macOS (universal) and Windows x64.

### Added
- Graphics > Picture Border (`border = fill`, `--border fill`): the 3D picture reaches the edges of the window, without
  the thin black frame the game leaves for a TV's overscan. It shows a little more of the scene at the same size (no
  zoom). Menus and loading screens keep their own frame. In a two-player split screen, both views reach the edges too
  and meet at the game's thin divider line in the middle.
- Rebinding in the settings menu: the Controls tab has a row per N64 input with two controller slots and two keyboard
  slots. Choose a slot and press the new button or key; a button another action uses trades places with it, and
  Default puts a row back. A slot that differs from the layout shows in yellow, and Reset all to default (it asks first)
  puts every binding back. Changes work at once and are saved to `controls.cfg` ([MANUAL](docs/MANUAL.md#controls)).
- A Controllers list in the Controls tab: which controller is player 1 or 2, what it is pressing right now, and buttons
  to swap players or give a controller either player. One controller on player 2 with the keyboard alone on player 1
  makes a two-player game with one controller. The choice lasts until you quit.
- Test sessions `menu-controls`, `menu-controls-reload` and `menu-ports` (virtual pads).
- Draw distance (Graphics tab, `draw_distance` in `graphics.cfg`, `--draw-distance`): Original (the game as it
  was), 2x, 4x and Full (the whole course, including the scenery the game hides by area as you skate; secrets and
  items a goal reveals stay hidden until the game shows them). It applies at once, shorter or longer, with no restart: the
  game always gets a bigger matrix buffer at start-up and uses only its own part of it at Original. It steps back on its own if a frame comes close to
  filling one of the game's buffers. Full also draws the scenery that skips the game's distance test but is hidden by
  area (Downhill Jam's lower end: the pool, the blocks and the building below the BRETT wall no longer pop in as you come
  over the edge). `dd_buffers = original` in `graphics.cfg` (`--dd-buffers original`; not in the menu)
  keeps the game's own buffers and memory layout exactly; it needs a restart.
- Tests: Europe's own reference pictures, for the few screens that differ from USA v1.1 (`OWN_REFS` in
  `tests/scenarios.py`), are recorded by `test.sh --version thps1_eu --record`.
- Fog (`fog` in `graphics.cfg`, `--fog`; not in the menu or a preset): Original (the default), Soft or Off. The game's
  fog is thin by design, a haze over the far end of the view (in most courses the last eighth). Soft starts it at 70 %
  of the draw distance, so far scenery fades in instead of popping in; Off shows a long draw distance most clearly. At
  Full draw distance the game's fog is far beyond the courses, so Soft looks like Original there. Test sessions
  `fog-check` (in the suite) and `fog-shot` (opt-in pictures).

### Changed
- Built on THPS64Host v0.2.0.
- Frame Rate (Graphics tab, `refresh` in `graphics.cfg`, `--refresh`) is now Original (30) or 60, default 60. "Match display"
  and 120 are gone: at 120 Hz (what "Match display" gave on a ProMotion Mac) the picture stuttered. A `graphics.cfg` with
  `refresh=display` or another rate moves to 60 once, with a log line.
- Graphics > Preset (`--preset original|enhanced`): Original sets 4:3, the HUD in the 4:3 area, the 4:3 split screen,
  the black frame, 30 fps and the game's draw distance, as on the N64. Enhanced sets 16:9, the HUD at the screen edges,
  the wide split screen, Picture Border Fill, 60 fps and Full draw distance. Choosing one replaces your choices in those
  six rows; Custom shows when they match neither. A new install starts with Enhanced. An existing `graphics.cfg` keeps
  its values, and a setting it lacks takes the new default (so an older file gets Picture Border Fill and Full draw
  distance). Fog is in neither preset.
- Removed the known issue "at 21:9, a far wall can drop out at the right edge". It doesn't happen in v0.1.0. New tests
  check that widescreen never hides scenery at the edges of the picture.
- Two-player split screen fills the picture in widescreen (16:9, 21:9, following the window): each player's view is widened
  to its half, and each player's HUD sits at its own view's edge (also with HUD Placement `original`). 4:3 is unchanged.
  It's on by default; Graphics > Two-Player Split Screen (`split`, `--split original`) keeps both views in the 4:3 area,
  each with its HUD inside it, and black bands at the sides.
- Level starts freeze the picture for about 0.13 s instead of 0.2 s, and the attract demo's pauses are a third shorter:
  the shared host unpacks the game's data twice as fast and runs the game's `memset` and `memcpy` natively.
- BUILDING.md: on Windows use `python` instead of `python3` and a `C:/...` path in `THPS1_ROM`, with a link to the Windows
  test checklist; how `tools/check.sh` shares the build's runtime; `--first-run` needs `build_host.py --split` first; where
  the test output goes; how to test Europe.

## [0.1.0] - 2026-10-18

The first public release, built on THPS64Host v0.1.0. It runs the USA v1.1, USA v1.0 and Europe releases of
the N64 game, on macOS (universal) and Windows x64.

### Added
- A first start that builds the game from your own dump, on your machine, with progress, Cancel and Retry. On macOS it
  offers Apple's installer if the Command Line Tools are missing; the Windows zip brings its own compiler.
- Native rendering through RT64 (Metal, Direct3D 12), scaled to the window, with MSAA 4x.
- Widescreen: 16:9 by default, 21:9, or following the window. The in-level HUD moves to the screen edges
  (`hud = expand`); `original` keeps it in the centred 4:3 area.
- Frame interpolation to the display's rate (60 Hz, 120 Hz on ProMotion) over the game's 30 fps.
- The in-game settings menu (Esc, or Back on a controller): general, controls, graphics, sound and cheats.
- An Xbox-style controller layout (tricks on the face buttons) and the N64 layout; keyboard and SDL controllers, two
  players, hot-plugging; every binding in `controls.cfg`.
- Controller Pak saves as a standard 32 KiB `.mpk` file.
- Cheats for testing: Unlock All Levels, Perfect Balance, Slow Motion and Skip to Restart. They're off by default and
  named in the log and `crash.log` while on. The cheats aren't stored in the save; progress made with one on is saved as usual.
- Europe runs at 60 Hz, like the USA releases.
- Portable mode: a `portable.txt` beside the app keeps settings and saves next to it.

### Fixed
- Far scenery in Downtown dropped out for a frame on quick turns, and logos in levels such as the Warehouse flashed. The
  host now redoes RT64's split of the camera matrix when the camera faces along the world's z axis.
- Short pops in the sound while paused or quiet, when the audio output ran dry for a moment (loads, unpausing, a busy
  machine). The output now fades out and back in instead of cutting.
- A crash in RT64's display-list parser: the runtime told the game the graphics task was done before RT64 had read it
  (an N64ModernRuntime patch).
- The special meter's fill spilled out of its frame with the HUD at the screen edges.
- OPTIONS > PLAYER 2 CONTROLS couldn't be left with one controller or the keyboard.
- The name-entry screen showed only the first letter on macOS (an RT64 Metal patch).
- Stale picture edges in the Chicago competition intro, and a flashing border on the select screens.
- A controller connected at start was opened twice.
- Windows: the settings migration was never saved, and the frame-interpolation time budget never applied.

[Unreleased]: https://github.com/THPS64Recomp/THPS1-64Recomp/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/THPS64Recomp/THPS1-64Recomp/releases/tag/v0.2.0
[0.1.0]: https://github.com/THPS64Recomp/THPS1-64Recomp/releases/tag/v0.1.0
