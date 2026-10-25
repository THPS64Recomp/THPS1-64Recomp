# Changelog

All notable changes to THPS1 64: Recompiled are listed here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Changes to the shared host are listed in the
[THPS64Host changelog](https://github.com/THPS64Recomp/THPS64Host/blob/main/CHANGELOG.md).

## [Unreleased]

### Changed
- Built on THPS64Host v0.2.0.
- Removed the known issue "at 21:9, a far wall can drop out at the right edge". It doesn't happen in v0.1.0. New tests
  check that widescreen never hides scenery at the edges of the picture.
- Two-player split screen fills the picture in widescreen (16:9, 21:9, following the window): each player's view is widened
  to its half, and each player's HUD sits at its own view's edge (also with HUD Placement `original`). 4:3 is unchanged.
  It's on by default; Graphics > Two-Player Split Screen (`split`, `--split original`) keeps both views in the 4:3 area,
  each with its HUD inside it, and black bands at the sides.

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

[Unreleased]: https://github.com/THPS64Recomp/THPS1-64Recomp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/THPS64Recomp/THPS1-64Recomp/releases/tag/v0.1.0
