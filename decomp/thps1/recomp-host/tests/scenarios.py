"""Scenario definitions for the THPS1 recomp regression suite (data only; engine in run.py).

Checkpoints describe a screen: the expected RT64 frame size and one or more regions that are
compared with a reference frame recorded locally (build/tests/refs/<name>.png, ROM-derived,
never committed). Regions are fractions of the frame, so they don't depend on the resolution;
each is reduced to a gw x gh luma grid, normalised (zero mean, unit std: fades and brightness
don't matter) and compared by mean absolute difference: 0 = same picture, ~1.1 = unrelated.
`tol` is the largest distance that still counts as a match. `tests/run.py --check-refs`
prints, for each checkpoint, how far the *other* references are (as distance/tol; must stay
well above 1) -- run it after recording or after changing a region.

`record` says how --record captures the reference when none exists: ("frame", N) = at
displayed frame N; ("settle", N) = N displayed frames after the step's input.

Menus are navigated without references: the highlighted entry is gold/red (harness.gold),
the others blue/white, so the cursor row is the strongest gold band inside `y_range`, mapped to
the nearest of `rows` (centres as fractions of the frame height).
"""

# Checkpoints whose screen differs on another release, by version id: that release needs its own reference for them, recorded with
# `tools/test.sh --version ID --record` (every other checkpoint uses the first release's picture; games.toml `refs_from`).
OWN_REFS = {
    "thps1_eu": ["load_data_list"],
}

# name: size, regions [(region (x0, y0, x1, y1), gw, gh, tol)], record
# A region (region, "mask", luma_min, min_frac) is a template match instead: at least min_frac
# of the reference's pixels brighter than luma_min must have the same colour (for HUD text over
# a moving 3D background; harness.mask_score).
CHECKPOINTS = {
    # Front end (640x474: 640x480 VI with the first/last lines cropped by the VI timing).
    "logo":           dict(size="640x474", regions=[((0.0, 0.40, 1.0, 0.60), 32, 6, 0.40)], record=("frame", 600),
                           what="Activision logo (after Expansion Pak notice + legal screen)"),
    "title":          dict(size="640x474", regions=[((0.0, 0.0, 1.0, 1.0), 16, 12, 0.35)], record=("settle", 60),
                           what="title screen, PRESS START"),
    "main_menu":      dict(size="640x474", regions=[((0.30, 0.30, 0.70, 0.75), 12, 16, 0.40),
                                                    ((0.0, 0.0, 1.0, 0.25), 16, 4, 0.35)], record=("settle", 60),
                           what="main menu: CAREER MODE .. EXTRAS"),
    "rumble_notice":  dict(size="640x474", regions=[((0.15, 0.35, 0.85, 0.58), 24, 8, 0.40)], record=("settle", 45),
                           what="THIS GAME SUPPORTS RUMBLE PAKS ... OK"),
    "skater_select":  dict(size="640x474", regions=[((0.0, 0.0, 0.62, 1.0), 12, 16, 0.40)], record=("settle", 45),
                           what="SELECT PLAYER (Tony Hawk)"),
    "board_select":   dict(size="640x474", regions=[((0.0, 0.0, 1.0, 1.0), 16, 12, 0.40)], record=("settle", 45),
                           what="SELECT BOARD"),
    "level_select":   dict(size="640x474", regions=[((0.0, 0.0, 1.0, 1.0), 16, 12, 0.40)], record=("settle", 45),
                           what="SELECT COURSE: Warehouse"),
    "tips_ready":     dict(size="640x474", regions=[((0.15, 0.86, 0.85, 0.97), 24, 4, 0.40)], record=("settle", 360),
                           what="loading screen tip with 'PRESS A TO START'"),
    "career_goals":   dict(size="640x474", regions=[((0.0, 0.0, 1.0, 1.0), 16, 12, 0.40)], record=("settle", 360),
                           what="WAREHOUSE TAPE CHALLENGES (career level intro)"),
    "career_menu":    dict(size="640x474", regions=[((0.30, 0.40, 0.70, 0.65), 12, 8, 0.40)], record=("settle", 120),
                           what="career submenu: CONTINUE GAME / NEW GAME / LOAD GAME"),
    "career_menu_loaded": dict(size="640x474", regions=[((0.30, 0.40, 0.70, 0.65), 12, 8, 0.40)], record=("settle", 120),
                               what="career submenu after loading a career: CONTINUE GAME enabled"),
    "options_menu":   dict(size="640x474", regions=[((0.0, 0.0, 0.25, 1.0), 4, 16, 0.40), ((0.25, 0.28, 0.85, 0.78), 12, 14, 0.40)], record=("settle", 90),
                           what="OPTIONS menu"),
    "load_data_empty": dict(size="640x474", regions=[((0.20, 0.42, 0.80, 0.58), 40, 8, 0.35)], record=("settle", 90),
                            what="LOAD DATA on a blank pak: NO TONY HAWK GAME NOTES FOUND"),
    "load_data_list": dict(size="640x474", regions=[((0.20, 0.42, 0.80, 0.58), 40, 8, 0.35)], record=("settle", 90),
                           what="LOAD DATA: note list with the saved career (named 'A')"),
    # In level (320x237). The HUD labels are fixed; everything behind them moves, hence the
    # small native-resolution grid on the letters.
    "in_level":       dict(size="320x237", regions=[((0.090, 0.120, 0.170, 0.165), "mask", 150, 0.8)], record=("settle", 90),
                           what="in level: SCORE label of the HUD"),
    # Native (game-visible) frame of the Warehouse, paused 200 input polls after the A that starts the level (FREE
    # SKATE, Skip Intro). Recorded at 4:3; at 21:9 the game must show the very same frame (the camera
    # must not move: widening the frustum once moved it, Q17). Tolerance 0.06: runs pause at the same game poll (press_after) and land 0.00-0.02 apart; a pause one frame later is 0.12 away, and the old frustum-widening camera 0.52.
    "paused_w90":     dict(size="320x237", regions=[((0.0, 0.25, 1.0, 1.0), 32, 18, 0.06)], record=("settle", 30),
                           what="Warehouse paused 90 frames after the start (camera reference, 4:3)"),
    "pause":          dict(size="320x237", regions=[((0.25, 0.08, 0.75, 0.24), 16, 5, 0.40)], record=("settle", 30),
                           what="PAUSED menu"),
    # In-level menus are drawn over the live 3D scene, whose view depends on how long the run
    # lasted: match their text as templates ("mask"), not the whole picture (Q18: the 16:9 /
    # MSAA / 60 Hz defaults shifted the timing and the background broke the luma grids).
    "statistics":     dict(size="320x237", regions=[((0.37, 0.10, 0.63, 0.17), "mask", 150, 0.7), ((0.15, 0.18, 0.85, 0.55), "mask", 150, 0.5)], record=("settle", 45),
                           what="end of run: STATISTICS"),
    "postrun_menu":   dict(size="320x237", regions=[((0.30, 0.16, 0.70, 0.73), "mask", 150, 0.5)], record=("settle", 45),
                           what="end of run menu: RETRY .. SAVE CAREER .. QUIT"),
    "save_prompt":    dict(size="320x237", regions=[((0.36, 0.35, 0.64, 0.43), "mask", 150, 0.7), ((0.44, 0.50, 0.57, 0.68), "mask", 150, 0.7)], record=("settle", 30),
                           what="SAVE GAME ? YES / NO"),
    "enter_name":     dict(size="320x237", regions=[((0.34, 0.16, 0.67, 0.25), "mask", 170, 0.7), ((0.20, 0.51, 0.82, 0.57), "mask", 170, 0.7)], record=("settle", 30),
                           what="ENTER NAME"),
    # ENTER NAME after 'a' + RIGHT + 'b' (the cursor, yellow, is on the second slot): the two letters must show (the region is only their cells,
    # so the long underscore row cannot carry the match). `--check-refs` lists enter_name -> enter_name_ab as close (1.1): a template mask
    # only asks that the reference's bright pixels are present, and the AB frame contains the blank frame's; the other direction is 3.3.
    "enter_name_ab":  dict(size="320x237", regions=[((0.34, 0.16, 0.67, 0.25), "mask", 170, 0.7), ((0.20, 0.47, 0.30, 0.545), "mask", 170, 0.7)], record=("settle", 30),
                           what="ENTER NAME with 'AB' typed: both letters drawn"),
    "save_ok":        dict(size="320x237", regions=[((0.29, 0.40, 0.68, 0.48), "mask", 150, 0.7), ((0.43, 0.54, 0.53, 0.63), "mask", 150, 0.7)], record=("settle", 45),
                           what="SAVE SUCCESSFUL / OK"),
}

MENUS = {
    "main":    dict(rows=[0.361 + 0.072 * i for i in range(6)], y_range=(0.30, 0.80),
                    items=["CAREER MODE", "TWO PLAYERS", "SINGLE SESSION", "FREE SKATE", "OPTIONS", "EXTRAS"]),
    "career":  dict(rows=[0.447, 0.518, 0.590], y_range=(0.40, 0.70),
                    items=["CONTINUE GAME", "NEW GAME", "LOAD GAME"]),
    "options": dict(rows=[0.317 + 0.072 * i for i in range(7)], y_range=(0.25, 0.85),
                    items=["PLAYER 1 CONTROLS", "PLAYER 2 CONTROLS", "SOUND LEVELS", "TRICK TIPS", "SCORE DISPLAY",
                           "LOAD DATA", "BACK TO MAIN"]),
    "pause":   dict(rows=[0.378 + 0.088 * i for i in range(4)], y_range=(0.30, 0.80),
                    items=["CONTINUE", "RETRY", "SOUND LEVELS", "END RUN"]),
    "pause5":  dict(rows=[0.333 + 0.089 * i for i in range(5)], y_range=(0.28, 0.75),   # with the Skip to Restart cheat
                    items=["CONTINUE", "RETRY", "SKIP TO RESTART", "SOUND LEVELS", "END RUN"]),
    "postrun": dict(rows=[0.192 + 0.0886 * i for i in range(7)], y_range=(0.12, 0.85),
                    items=["RETRY", "TAPE CHALLENGES", "LEVEL SELECT", "EQUIPMENT SELECT", "WATCH REPLAY",
                           "SAVE CAREER", "QUIT"]),
}

# Steps (all waits are in displayed frames or checkpoint matches, never wall-clock presses):
#   ("wait_for", cp)                 poll RT64 frames until checkpoint cp matches
#   ("go", BUTTON, from_cp, to_cp)   press BUTTON until to_cp matches (re-pressed only while
#                                    from_cp still matches, i.e. the press was dropped)
#   ("menu", menu, index)            move the cursor (DOWN) until entry `index` is highlighted
#   ("menu_at", menu, index)         assert the cursor is on entry `index` (no input)
#   ("press_after", BUTTON, N)       press exactly N game input polls after the previous press finished
#   ("press", BUTTON)                one press (3 polls held, 3 released)
#   ("wait", frames)
#   ("dl", tasks, min_tris)          display-list stats of the next gfx tasks: in-level 3D
#   ("audio", frames, min_rms_dbfs)  RMS of the game's audio output over a window
#   ("fps", seconds, min_median)     median displayed fps from the perf log (warn-only if the
#                                    machine is overloaded: load avg > 2 x CPUs)
#   ("pak_snapshot",) / ("pak_changed",)   hash of <config>/saves/thps1_pak1.mpk before/after
#   ("pak_log", regex)               a host "[thps] pak" log line matching regex was printed
#   ("not_cp", cp)                   the current frame must NOT match cp (negative check)
#   ("max_frame", N)                 the checkpoint just matched came within N displayed frames of boot
#   ("log", regex)                   a host "[thps] skip intro|input|launcher" line matching regex
#   ("fps_overlay", seconds, tol)    Show FPS counter lines agree with the perf log's fps (median, +-tol)
#   ("vpad", "attach")               a virtual SDL game controller (no hardware needed)
#   ("vpress", NAME)                 press + release one of its buttons (SDL names: a, dpdown, y ...)
#   ("vpress2", NAME)                the same on a SECOND virtual pad (--control vpad2); ("vpad2", "attach"|"detach") likewise
#   ("log_n", REGEX, N)              at least N host "[thps] input|..." lines match REGEX (a re-attached pad takes its port again)
#   ("log_none", REGEX)              no such host line (yet)
#   ("ctl", "key NAME")              a keyboard tap through the key latch (SDL key name: Space, D, Down ...; sessions with --keyboard)
#   ("bind", INPUT, FIELDS)          replace a binding and save it (controls.cfg), as a user edit would
#   ("file_contains", FILE, regex)   <config>/FILE has a match
#   ("binding_saved", INPUT, B, rx)  the binding was saved (controls.cfg line rx, or controls.json button B)
#   ("audio_max", frames, max_rms)   audio output RMS at most max_rms dBFS (volume setting)
#   ("crash",)                       --control crash: exit 139 and a crash.log naming game code (last step)
#   ("keep_present", NAME)           copy the newest present capture to <out>/NAME.png (UI evidence)
#   ("json_value", FILE, KEY, VALUE) <config>/FILE (recompui settings JSON) has KEY = VALUE
#   ("loadrom", "rom"|"rev0", regex) launcher Load ROM (--control loadrom) with the suite's ROM or a
#                                    synthetic v1.0 header; the host log matches regex
#   ("pad_records", INPUT, [ids])    while INPUT ("vpad:NAME" or N64 buttons) is held, exactly these
#                                    records of the game's PlayStation-style pad layer are pressed
#                                    (0 grind, 1 flip, 2 grab, 3 ollie, ...; run.py)
#   ("skate", INPUTS, "air"|"trick") vpad inputs on the ground; the skater gets airborne / a trick
#                                    counter goes up (CBruce via the skater pointer 0x800D61A8)
#   ("edges", N, max[, "rows"])      border bands of the next N presented frames change by <= max;
#                                    "rows": the top and bottom bands too
#   ("shot", NAME)                   keep the current RDRAM frame as <out>/NNNN_NAME.png (evidence)
#   ("ctl", "COMMAND ...")           send a raw --control command (e.g. "dump 4 DIR"); the reply goes into the notes
#   ("ctl_match", "COMMAND", REGEX)  the same, and the reply must match REGEX (e.g. ("ctl_match", "hud", r"tasks_anchored=[1-9]"))
#   ("name_is", "ab")                THPS1 name-entry buffer (gNameEntryBuf) holds exactly this name (rest blank)
#   ("vstick", "up"|"down"|"left"|"right")   push the virtual pad's left stick for 6 frames, release
#   ("present_wide", "WxH", max)     newest present capture (session `present_every`) is WxH and at
#                                    most `max` of the bands outside the central 4:3 is unrendered
#   ("hfr_motion", SEC, STICK, checks) / ("hfr_cut",) / ("latency", "A/B", N, MAX_MS)
#                                    high frame rate + input latency (tests/hfr_steps.py)

from hfr_steps import ids_phases as IDS_PHASES, ids_clip as IDS_CLIP  # noqa: E402

BOOT_TO_MENU = [
    ("wait_for", "logo"),
    ("go", "START", None, "title"),
    ("go", "START", "title", "main_menu"),
]

# Inside OPTIONS > PLAYER n CONTROLS: the OPTIONS menu is not on screen (not_cp compares the LAST captured frame, so capture a fresh one).
IN_SCREEN = [("wait", 40), ("shot", "in_controls_screen"), ("not_cp", "options_menu")]

TO_LEVEL_SELECT = [
    ("go", "A", None, "rumble_notice"),
    ("go", "A", "rumble_notice", "skater_select"),
    ("go", "A", "skater_select", "board_select"),
    ("go", "A", "board_select", "level_select"),
]

# Sessions = one host instance each; scenarios in a session run in order on the same instance
# (a failure skips the rest of that session). `fresh_pak` starts from a blank Controller Pak. `optin` sessions
# (exploration, evidence frames) run only when named: --session NAME / --only SCENARIO.
# TWO PLAYERS > GRAFFITI with two virtual pads (pad 1 = port 1, pad 2 = port 2), up to the split-screen level; then each pad reaches its own port.
_TWO_PLAYERS_TO_LEVEL = [
    ("wait_for", "title"), ("go", "START", "title", "main_menu"),
    ("vpad", "attach"), ("vpad2", "attach"),
    ("vpress", "leftshoulder"), ("vpress2", "leftshoulder"),           # pad 1 = port 1, pad 2 = port 2
    ("log_n", r"Virtual Controller takes port 2", 1),
    ("menu", "main", 1),
    ("vpress", "a"), ("wait", 40),                                   # TWO PLAYERS > GRAFFITI
    ("vpress", "a"), ("wait", 40),
    ("vpress2", "a"), ("wait", 40), ("vpress", "a"), ("wait", 40),   # PLAYER 1 / PLAYER 2 pick, then the next screens in turn
    ("vpress2", "a"), ("wait", 40), ("vpress", "a"), ("wait", 40),
    ("vpress2", "a"), ("wait", 40), ("vpress", "a"), ("wait", 40),
    ("vpress2", "a"), ("wait", 200),
    ("ctl_match", "inputstate", r"in3d=1"),
]
# Pause the split screen: player 1's pad holds START (a tap through the keyboard path did not pause it), then the paused frame settles.
_TWO_PLAYERS_PAUSE = [("ctl", "vpad button start 1"), ("wait", 10), ("ctl", "vpad button start 0"), ("wait", 45)]
_TWO_PLAYERS_PORTS = [
    ("ctl", "vpad2 button leftshoulder 1"), ("wait", 8),
    ("ctl_match", "inputstate", r"last2=0x0020$"),                    # pad 2 reaches port 2 ...
    ("ctl_match", "inputstate", r"last=0x0000 "),                     # ... and not port 1
    ("ctl", "vpad2 button leftshoulder 0"),
    ("ctl", "vpad button rightshoulder 1"), ("wait", 8),
    ("ctl_match", "inputstate", r"last=0x0010 "),
    ("ctl_match", "inputstate", r"last2=0x0000$"),
    ("ctl", "vpad button rightshoulder 0"),
]

SESSIONS = [
    dict(name="frontend", config="suite-config", fresh_pak=True, wav=True, scenarios=[
        ("boot_logo",  "boot to the Activision logo", [("wait_for", "logo")]),
        ("title",      "logos/attract demo -> title (PRESS START); still border bands", [("go", "START", None, "title"),
                                                                                   ("edges", 20, 4.0)]),
        ("main_menu",  "title -> main menu", [("go", "START", "title", "main_menu")]),
        ("freeskate_level", "FREE SKATE -> Warehouse loaded, HUD + 3D", [
            ("menu", "main", 3),
            *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"),
            ("go", "A", "tips_ready", "in_level"),
            ("dl", 10, 500),
        ]),
        ("level_audio", "in-level audio is not silent", [("wait", 60), ("audio", 150, -40.0)]),
        ("level_fps",   "in-level median fps >= 28", [("fps", 10, 28.0)]),
        # THPS1 reads its tricks from the C buttons (OPTIONS > PLAYER 1 CONTROLS: C-down ollie, C-left
        # flip, C-right grab, C-up grind); N64 A/B are menu-only. The default bindings put the tricks
        # on a controller's face buttons (Q19: Xbox A/X did nothing in game before).
        ("level_controls", "default pad bindings reach the game's trick buttons; N64 A alone does not", [
            ("vpad", "attach"),
            ("pad_records", "A", []),             # N64 A: menus only
            ("pad_records", "B", []),             # N64 B: menus only
            ("pad_records", "CD", [3]),           # C-down = X (ollie)
            ("pad_records", "vpad:a", [3]),       # south (Xbox A) = A + C-down -> ollie
            ("pad_records", "vpad:x", [1]),       # west (Xbox X) = C-left -> flip
            ("pad_records", "vpad:b", [2]),       # east (Xbox B) = B + C-right -> grab
            ("pad_records", "vpad:y", [0]),       # north (Xbox Y) = C-up -> grind
        ]),
        ("level_ollie", "Xbox A held and released: the skater ollies (in air)", [
            ("skate", [("vpad", "a", 1), ("wait", 10), ("vpad", "a", 0)], "air"),
        ]),
        ("level_trick", "Xbox A, then X + right in the air: a flip trick is registered", [
            ("skate", [("vpad", "a", 1), ("wait", 10), ("vpad", "a", 0), ("wait", 3),
                       ("axis", "leftx", 32767), ("vpad", "x", 1), ("wait", 6), ("vpad", "x", 0), ("axis", "leftx", 0)], "trick"),
        ]),
        # Q22: south/east send N64 A / B as well (menu accept / back). In the air, B (grab, + N64 B) and
        # Y (grind) must not leak into a menu "back" handler: the skater still ollies, the level goes on
        # (HUD template still there, not paused). The grab itself is checked as pad record 2 in
        # level_controls; the trick counters are in the notes only (a grab needs the right moment and place).
        ("level_grab", "Xbox A, then B + right and Y in the air: the level keeps running", [
            ("skate", [("vpad", "a", 1), ("wait", 10), ("vpad", "a", 0), ("wait", 3),
                       ("axis", "leftx", 32767), ("vpad", "b", 1), ("wait", 6), ("vpad", "b", 0), ("vpad", "y", 1), ("wait", 4),
                       ("vpad", "y", 0), ("axis", "leftx", 0)], "air"),
            ("wait", 30),
            ("wait_for", "in_level"),
        ]),
        # Q19 playtest: "flashing on the edges" of the pause menu / goals overlay. RT64's composited
        # frames (as presented) of a still screen must have still border bands.
        ("border_stable", "pause menu: the border bands of the presented frames don't flicker", [
            ("go", "START", "in_level", "pause"),
            ("wait", 20),
            ("edges", 45, 4.0),
        ]),
        # Q22: east (Xbox B) is N64 B (menu back) + C-right (grab): in the pause menu it resumes the level.
        ("pause_back", "pause menu: Xbox B (N64 B = back) resumes the level", [("vpress", "b"), ("wait", 30), ("wait_for", "in_level")]),
    ]),
    # Widescreen: the RDRAM frames the checkpoints compare stay native 4:3 (RT64 renders that copy
    # at the original aspect), so the 4:3 references apply; the present capture checks the wide
    # picture. Own config dir: --aspect/--window are saved to <config>/graphics.cfg.
    dict(name="widescreen", config="ws-config", fresh_pak=True, wav=False, present_every=30,
         args=["--aspect", "16:9", "--window", "1280x720", "--res-scale", "2", "--msaa", "4", "--hidden"], scenarios=[
        ("ws_menu", "16:9: boot to the main menu (native frames unchanged)", [*BOOT_TO_MENU]),
        ("ws_level", "16:9: Warehouse fills the wide frame (present capture), 30 fps", [
            ("menu", "main", 3),
            *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"),
            ("go", "A", "tips_ready", "in_level"),
            ("dl", 10, 500),
            ("wait", 60),
            ("present_wide", "1280x720", 0.15),
            ("fps", 10, 28.0),
        ]),
    ]),
    # Playtest 2026-10-12 ("flashing border" on the skater / course select): the 640x480 screens never clear the outer 8 px ring of their
    # colour buffer, so with three framebuffers RT64's frame showed stale art around the picture on every third game frame (dl_fixes.cpp
    # clears the ring). `edges ... "rows"` also holds the top and bottom bands of the presented frames still.
    dict(name="ws-select", config="wsel-config", fresh_pak=True, wav=False, args=["--aspect", "16:9", "--window", "1280x720", "--hidden"], scenarios=[
        ("border_select", "skater / board / course select at 16:9: the border bands (sides, top, bottom) of the presented frames don't flicker", [
            *BOOT_TO_MENU,
            ("menu", "main", 3),
            ("go", "A", None, "rumble_notice"),
            ("go", "A", "rumble_notice", "skater_select"),
            ("wait", 20),
            ("edges", 90, 4.0, "rows"),
            ("go", "A", "skater_select", "board_select"),
            ("wait", 20),
            ("edges", 90, 4.0, "rows"),
            ("go", "A", "board_select", "level_select"),
            ("wait", 20),
            ("edges", 90, 4.0, "rows"),
        ]),
        ("border_select_run", "course select after a run (every framebuffer holds the level's last frames): bands still", [
            ("go", "A", "level_select", "tips_ready"),
            ("go", "A", "tips_ready", "in_level"),
            ("wait", 60),
            ("go", "START", "in_level", "pause"),
            ("menu", "pause", 3),
            ("press", "A"),                       # END RUN (free skate: straight to RETRY / LEVEL SELECT / EQUIPMENT SELECT / QUIT)
            ("wait", 90),
            ("press", "DOWN"),                    # LEVEL SELECT
            ("press", "A"),
            ("wait_for", "level_select"),
            ("wait", 30),
            ("edges", 90, 4.0, "rows"),
        ]),
    ]),
    dict(name="sel-43", config="sel43-config", fresh_pak=True, wav=False, args=["--aspect", "original", "--window", "960x720", "--hidden"], scenarios=[
        ("border_select_43", "the same screens at 4:3: the 8 px ring around the picture (inside the band) doesn't flicker", [
            *BOOT_TO_MENU,
            ("menu", "main", 3),
            ("go", "A", None, "rumble_notice"),
            ("go", "A", "rumble_notice", "skater_select"),
            ("wait", 20),
            ("edges", 90, 4.0, "rows"),
            ("go", "A", "skater_select", "board_select"),
            ("wait", 20),
            ("edges", 90, 4.0, "rows"),
            ("go", "A", "board_select", "level_select"),
            ("wait", 20),
            ("edges", 90, 4.0, "rows"),
        ]),
    ]),
    dict(name="pak", config="pak-config", fresh_pak=True, wav=False, scenarios=[
        ("pak_empty", "fresh pak: OPTIONS -> LOAD DATA finds no notes", [
            *BOOT_TO_MENU,
            ("menu", "main", 4),
            ("go", "A", "main_menu", "options_menu"),
            ("menu", "options", 5),
            ("go", "A", "options_menu", "load_data_empty"),
            ("go", "B", "load_data_empty", "options_menu"),
            ("menu", "options", 6),
            ("go", "A", "options_menu", "main_menu"),
        ]),
        ("pak_save", "career run -> END RUN -> SAVE CAREER writes a note (.mpk changes)", [
            ("pak_snapshot",),
            ("menu", "main", 0),
            ("go", "A", "main_menu", "career_menu"),
            ("menu_at", "career", 1),             # no career yet: cursor on NEW GAME
            ("menu", "career", 1),
            *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "career_goals"),
            ("wait", 20),
            ("edges", 45, 4.0),                   # goals overlay: still border bands (Q19)
            ("go", "A", "career_goals", "in_level"),
            ("wait", 60),
            ("go", "START", "in_level", "pause"),
            ("menu", "pause", 3),
            ("go", "A", "pause", "statistics"),
            ("go", "A", "statistics", "postrun_menu"),
            ("menu", "postrun", 5),
            ("go", "A", "postrun_menu", "save_prompt"),
            ("go", "A", "save_prompt", "enter_name"),
            ("press", "UP"),                      # name "A"
            ("go", "A", "enter_name", "save_ok"),
            ("pak_log", r"pak 1: wrote \d+ bytes"),
            ("pak_changed",),
            ("go", "A", "save_ok", "postrun_menu"),
        ]),
    ]),
    # THPS1's name-entry screen (SAVE CAREER): the original reads only the D-pad (Left/Right = cursor, Up/Down = letter). Two bugs
    # lived here: after the first letter the other slots stayed blank on screen (RT64's Metal partial clear, patches/
    # rt64-metal-clear-state.patch), and keyboard / stick players had no way to type (the host maps the stick to the D-pad there).
    dict(name="name-entry", config="name-config", fresh_pak=True, wav=False, scenarios=[
        ("name_dpad", "SAVE CAREER: the D-pad types 'ab' and both letters show on screen", [
            *BOOT_TO_MENU,
            ("menu", "main", 0),
            ("go", "A", "main_menu", "career_menu"),
            ("menu_at", "career", 1),
            ("menu", "career", 1),
            *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "career_goals"),
            ("wait", 20),
            ("go", "A", "career_goals", "in_level"),
            ("wait", 60),
            ("go", "START", "in_level", "pause"),
            ("menu", "pause", 3),
            ("go", "A", "pause", "statistics"),
            ("go", "A", "statistics", "postrun_menu"),
            ("menu", "postrun", 5),
            ("go", "A", "postrun_menu", "save_prompt"),
            ("go", "A", "save_prompt", "enter_name"),
            ("name_is", ""),
            ("press", "UP"),                      # first slot: blank -> 'a'
            ("press", "RIGHT"),
            ("press", "UP"), ("press", "UP"),     # second slot: blank -> 'a' -> 'b'
            ("name_is", "ab"),
            ("wait_for", "enter_name_ab"),
        ]),
        ("name_stick", "same screen: the left stick (= the keyboard arrows) moves the cursor and changes letters", [
            ("vpad", "attach"),
            ("vpress", "leftshoulder"),           # a controller takes a port only when a button is pressed (a stick alone never does)
            ("vstick", "right"), ("vstick", "up"), ("vstick", "up"),     # third slot: blank -> 'a' -> 'b'
            ("name_is", "abb"),
            ("vstick", "left"), ("vstick", "down"),                      # second slot: blank -> 'a' -> 'b' -> 'a'
            ("name_is", "aab"),
        ]),
    ]),
    dict(name="pak-reload", config="pak-config", fresh_pak=False, wav=False, needs=["pak"], scenarios=[
        ("pak_list", "fresh run on the saved pak: LOAD DATA lists the note", [
            *BOOT_TO_MENU,
            ("menu", "main", 4),
            ("go", "A", "main_menu", "options_menu"),
            ("menu", "options", 5),
            ("go", "A", "options_menu", "load_data_list"),
            ("not_cp", "load_data_empty"),
            ("not_cp", "options_menu"),
        ]),
        ("pak_load", "load the note; career menu then offers CONTINUE GAME", [
            ("go", "A", "load_data_list", "options_menu"),
            ("pak_log", r"pak 1: read \d+ bytes at 0 of note 0"),
            ("menu", "options", 6),
            ("go", "A", "options_menu", "main_menu"),
            ("menu", "main", 0),
            ("go", "A", "main_menu", "career_menu_loaded"),
            ("menu_at", "career", 0),             # cursor starts on CONTINUE GAME (enabled)
            ("not_cp", "career_menu"),
        ]),
    ]),
    # QOL features (Q17): Skip Intro, Show FPS, remappable bindings with a virtual controller,
    # then the crash log (the host dies, so it is the last step). Fresh settings files each run.
    dict(name="qol", config="qol-config", fresh_pak=True, wav=False,
         fresh_files=["controls.cfg", "general.cfg", "crash.log", "controls.json", "general.json", "graphics.json", "sound.json"],
         args=["--skip-intro", "--show-fps", "--hidden"], scenarios=[
        ("skip_intro", "Skip Intro: boot to the title in < 150 frames, no logos (was ~600)", [
            ("wait_for", "title"),
            ("max_frame", 150),
            ("log", r"skip intro: pressing B on the Expansion Pak notice"),
            ("log", r"skip intro: legal screen \+ logos skipped"),
            ("go", "START", "title", "main_menu"),
        ]),
        ("fps_counter", "Show FPS: counter lines match the perf log", [("fps_overlay", 5, 2.0)]),
        ("vpad_bindings", "virtual controller moves the menu cursor; rebinding D-pad Down to Y works and is saved", [
            ("menu_at", "main", 0),
            ("vpad", "attach"),
            ("vpress", "dpdown"),
            ("log", r"Virtual Controller takes port 1"),
            ("menu_at", "main", 1),
            ("bind", "dpad_down", "button:y"),
            ("binding_saved", "dpad_down", 3, r"(?m)^dpad_down = button:y$"),   # SDL button 3 = Y
            ("vpress", "y"),
            ("menu_at", "main", 2),
            ("vpress", "dpdown"),            # no longer bound: the cursor stays
            ("menu_at", "main", 2),
        ]),
        ("crash_log", "a crash writes crash.log with the game function names", [("crash",)]),
    ]),
    # New process on the same settings: the rebinding persisted; general.cfg's volume applies.
    dict(name="qol-reload", config="qol-config", fresh_pak=False, wav=False, needs=["qol"],
         args=["--skip-intro", "--volume", "0", "--hidden"], scenarios=[
        ("bindings_persist", "controls.cfg from the last run: Y is D-pad Down", [
            ("wait_for", "title"),
            ("go", "START", "title", "main_menu"),
            ("vpad", "attach"),
            ("menu_at", "main", 0),
            ("vpress", "y"),
            ("menu_at", "main", 1),
        ]),
        ("volume_zero", "--volume 0: the audio output is silent", [("audio_max", 90, -90.0)]),
    ]),
    # Widescreen must not change the game: the same paused frame at 4:3 (records the reference) and
    # at 21:9 (compares). The 21:9 present capture must also fill the side bands.
    dict(name="cam-43", config="cam43-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden", "--aspect", "original", "--window", "960x720"], scenarios=[
        ("cam_ref_43", "4:3: Warehouse paused 90 frames after the start", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"), ("go", "A", "tips_ready", "in_level"),
            ("press_after", "START", 200), ("wait", 30), ("wait_for", "paused_w90"),
            ("edges", 45, 4.0),   # 4:3: the native border is the band (Q19 scissor fix; frontend now runs 16:9)
        ]),
    ]),
    # Play test 2026-10-15: "an intermittent slight popping sound every few seconds while paused (or maybe just quiet)".
    # The real SDL device at volume 0 (the path the user hears, silently). An underrun (the game thread late with the next
    # buffer: 50-150 ms gaps at loads, unpausing, a busy machine) used to be a hard cut to silence and back = two clicks;
    # src/audio.cpp now ramps both edges (declick). audio_declick forces underruns while the music plays and checks the
    # step the device played (THPS_AUDIO_DECLICK=0 = the old hard cut: fails). The underrun counts are a coarse guard.
    dict(name="audio-pause", config="apause-config", fresh_pak=True, wav=False, control_args=["--no-keyboard", "--no-pads"],
         args=["--skip-intro", "--hidden", "--volume", "0"], scenarios=[
        ("audio_level", "Warehouse: at most 3 audio underruns over 20 s of play", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"), ("go", "A", "tips_ready", "in_level"),
            ("wait", 60), ("underruns", 600, 3),
        ]),
        ("audio_declick", "forced underruns under the music: no click at their edges (sample step <= 1024)", [
            ("declick", 150, 4, 1024),
        ]),
        ("audio_declick_short", "short underruns (8 frames, resumed mid fade-out within one callback): no click (sample step <= 1024)", [
            ("declick_gap", 8, 6, 1024),
        ]),
        ("audio_paused", "pause menu: at most 3 audio underruns over 30 s", [
            ("go", "START", "in_level", "pause"), ("wait", 30), ("underruns", 900, 3),
        ]),
    ]),
    dict(name="cam-219", config="cam219-config", fresh_pak=True, wav=False, present_every=15, needs=["cam-43"],
         args=["--skip-intro", "--hidden", "--aspect", "21:9", "--window", "1680x720", "--res-scale", "2"], scenarios=[
        ("cam_same_219", "21:9: the same paused frame as 4:3 (camera unchanged), side bands filled", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"), ("go", "A", "tips_ready", "in_level"),
            ("press_after", "START", 200), ("wait", 30), ("wait_for", "paused_w90"),
            ("present_wide", "1680x720", 0.10),
        ]),
    ]),
    # Frontend build only (THPS1_BINARY=build/cmake-ui/thps1_recomp; skipped otherwise): the
    # launcher and settings menu, driven with the virtual controller. A setting changed in the menu
    # is saved, and a new process starts the game from the launcher with it.
    dict(name="ui", config="ui-config", fresh_pak=True, wav=False, requires="frontend", present_every=6,
         fresh_files=["controls.json", "general.json", "graphics.json", "sound.json"],
         args=["--launcher", "--hidden"], scenarios=[
        ("ui_launcher", "launcher shows Start Game (ROM stored)", [
            ("log", r"launcher ready \(ROM stored: Start Game\)"),
            ("vpad", "attach"),
            ("wait", 60),
            ("keep_present", "ui_launcher"),
        ]),
        ("ui_settings", "Settings: General Skip Intro + Show FPS ON, Graphics Aspect Ratio ORIGINAL + Apply, Sound volume 97; saved", [
            ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "a"), ("wait", 60),          # launcher: Settings
            ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "dpdown"),
            ("vpress", "dpright"), ("vpress", "a"),                                             # Skip Intro: ON
            ("vpress", "dpdown"), ("vpress", "dpright"), ("vpress", "a"), ("wait", 30),         # Show FPS: ON
            ("keep_present", "ui_general_skip_intro_on"),
            ("log", r"settings: skip_intro=1 show_fps=1"),
            ("vpress", "rightshoulder"), ("wait", 30), ("keep_present", "ui_tab_controls"),
            ("vpress", "rightshoulder"), ("wait", 30), ("keep_present", "ui_tab_graphics"),
            ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "dpleft"), ("vpress", "a"),   # Aspect Ratio: ORIGINAL
            ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "dpdown"),
            ("vpress", "a"), ("wait", 30),                                                      # Apply
            ("keep_present", "ui_graphics_applied"),
            ("log", r"gfx: aspect=original"),
            ("vpress", "rightshoulder"), ("wait", 30),
            ("vpress", "dpdown"), ("vpress", "dpleft"), ("vpress", "dpleft"), ("vpress", "dpleft"),  # Main Volume 100 -> 97
            ("keep_present", "ui_tab_sound"),
            ("log", r"settings: .* volume=97"),
            ("vpress", "back"), ("wait", 60),
            ("json_value", "general.json", "thps_skip_intro", "On"),
            ("json_value", "general.json", "thps_show_fps", "On"),
            ("json_value", "graphics.json", "ar_option", "Original"),
            ("json_value", "sound.json", "main_volume", 97),
        ]),
    ]),
    # Frontend build, no ROM stored: the launcher offers Load ROM; a v1.0 header is refused with
    # our wording (an in-UI prompt), the real ROM is accepted and the entry becomes Start Game.
    dict(name="ui-norom", config="ui-norom-config", fresh_pak=True, wav=False, requires="frontend", present_every=6,
         no_rom=True, fresh_files=["thps1.n64.us.1.1.z64", "general.json", "graphics.json", "sound.json", "controls.json"],
         args=["--launcher", "--hidden"], scenarios=[
        ("ui_load_rom", "no ROM: Load ROM; v1.0 header refused (USA v1.1 wording); the ROM accepted -> Start Game", [
            ("log", r"launcher ready \(no ROM yet: Load ROM\)"),
            ("vpad", "attach"), ("wait", 60),
            ("keep_present", "ui_launcher_no_rom"),
            ("loadrom", "rev0", r"header revision 0 \(= version 1\.0\)"), ("wait", 30),
            ("keep_present", "ui_rom_rejected"),
            ("vpress", "a"), ("wait", 30),
            ("loadrom", "rom", r"launcher: ROM stored, Start Game"), ("wait", 30),
            ("keep_present", "ui_launcher_rom_ok"),
        ]),
    ]),
    dict(name="ui-start", config="ui-config", fresh_pak=False, wav=False, requires="frontend", present_every=6,
         needs=["ui"], args=["--launcher", "--hidden"], scenarios=[
        ("ui_start_game", "new process: settings loaded (Skip Intro, Show FPS, 4:3, volume 97); Start Game -> title; FPS overlay; in-game menu", [
            ("log", r"gfx: aspect=original"),
            ("log", r"launcher ready"),
            ("vpad", "attach"),
            ("wait", 60),
            ("vpress", "dpdown"), ("vpress", "dpup"), ("vpress", "a"),
            ("wait_for", "title"),
            ("log", r"skip intro: legal screen \+ logos skipped"),
            ("fps_overlay", 3, 2.0),
            ("keep_present", "ui_title_fps"),
            ("vpress", "back"), ("wait", 45),
            ("keep_present", "ui_ingame_menu"),
        ]),
    ]),
    # OPTIONS > PLAYER 1 / PLAYER 2 CONTROLS (the game's own remap screens; hand play 2026-10-14: "the controls menu soft locks"). Cause:
    # PLAYER 2 CONTROLS reads only port 2, so with one pad or just the keyboard nothing could leave it; the host now answers port 2 with
    # port 1's input in menus while no second pad is attached (input.cpp, game.toml p2_menu_mirror). There is no reference frame of the
    # screens themselves: inside one the OPTIONS menu is not shown (not_cp options_menu), and leaving must bring OPTIONS back
    # (wait_for options_menu times out on a lock).
    dict(name="options-controls", config="optctl-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden", "--keyboard"], scenarios=[
        ("ctlscr_p1_pad", "thps-xbox pad: A enters PLAYER 1 CONTROLS, D-pad changes a row, B (east) leaves", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"),
            ("menu", "main", 4),
            ("go", "A", "main_menu", "options_menu"),
            ("menu_at", "options", 0),
            ("vpad", "attach"), ("vpress", "leftshoulder"),              # the first press claims port 1 (a button that does nothing here)
            ("vpress", "a"), *IN_SCREEN,
            ("vpress", "dpdown"), ("vpress", "dpright"), ("vpress", "dpleft"), ("vpress", "dpup"),
            ("vpress", "b"), ("wait_for", "options_menu"),
            ("menu_at", "options", 0),
        ]),
        ("ctlscr_p1_back_row", "thps-xbox pad: A on BACK TO OPTIONS (the last row; A also sends C-down) leaves", [
            ("vpress", "a"), *IN_SCREEN,
            *[("vpress", "dpdown")] * 7,
            ("vpress", "a"), ("wait_for", "options_menu"),
        ]),
        ("ctlscr_p1_kbd", "keyboard: Space enters, arrows move, D leaves; again with Space on BACK TO OPTIONS", [
            ("ctl", "key Space"), *IN_SCREEN,
            ("ctl", "key Down"), ("wait", 12), ("ctl", "key Right"), ("wait", 12), ("ctl", "key Left"), ("wait", 12), ("ctl", "key Up"), ("wait", 12),
            ("ctl", "key D"), ("wait_for", "options_menu"),
            ("ctl", "key Space"), *IN_SCREEN,
            *[step for _ in range(7) for step in (("ctl", "key Down"), ("wait", 12))],
            ("ctl", "key Space"), ("wait_for", "options_menu"),
        ]),
        # The soft lock: with ONE pad or only the keyboard, PLAYER 2 CONTROLS could not be left.
        # (Leaving either controls screen puts the OPTIONS cursor back on its first row.)
        ("ctlscr_p2_pad", "ONE pad: A enters PLAYER 2 CONTROLS, B (east) leaves (it read only port 2: no way out)", [
            ("wait", 30), ("vpress", "dpdown"), ("menu_at", "options", 1),
            ("vpress", "a"), *IN_SCREEN,
            ("vpress", "b"), ("wait_for", "options_menu"),
        ]),
        ("ctlscr_p2_back_row", "ONE pad: A on BACK TO OPTIONS leaves PLAYER 2 CONTROLS", [
            ("wait", 30), ("vpress", "dpdown"), ("menu_at", "options", 1),
            ("vpress", "a"), *IN_SCREEN,
            *[("vpress", "dpdown")] * 7,
            ("vpress", "a"), ("wait_for", "options_menu"),
        ]),
        ("ctlscr_p2_kbd", "keyboard only: Space enters PLAYER 2 CONTROLS, D leaves; again with Space on BACK TO OPTIONS", [
            ("wait", 30), ("ctl", "key Down"), ("wait", 20),
            ("ctl", "key Space"), *IN_SCREEN,
            ("ctl", "key D"), ("wait_for", "options_menu"),
            ("wait", 30), ("ctl", "key Down"), ("wait", 20),
            ("ctl", "key Space"), *IN_SCREEN,
            *[step for _ in range(7) for step in (("ctl", "key Down"), ("wait", 12))],
            ("ctl", "key Space"), ("wait_for", "options_menu"),
        ]),
        ("ctlscr_p2_n64", "n64 preset, one pad: A enters PLAYER 2 CONTROLS, X (west = N64 B) leaves", [
            ("ctl", "preset n64"),
            ("wait", 30), ("vpress", "dpdown"), ("menu_at", "options", 1),
            ("vpress", "a"), *IN_SCREEN,
            ("vpress", "x"), ("wait_for", "options_menu"),
            ("ctl", "preset thps-xbox"),
        ]),
        ("ctlscr_p2_two_pads", "TWO pads: PLAYER 2 CONTROLS is the second pad's (port 2): its B leaves", [
            ("vpad2", "attach"), ("vpress2", "leftshoulder"),
            ("log_n", r"Virtual Controller takes port 2", 1),
            ("wait", 30), ("vpress", "dpdown"), ("menu_at", "options", 1),
            ("vpress", "a"), *IN_SCREEN,
            ("vpress2", "b"), ("wait_for", "options_menu"),
            ("vpad2", "detach"),
        ]),
    ]),
    # Controller hotplug and two pads (2026-10-14 hand play: the game crashed shortly after a Bluetooth pad was paired; ports are assigned
    # by first button press, input.cpp). Virtual pads: `vpad` = the first, `vpad2` = a second one.
    dict(name="hotplug", config="hotplug-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden"], scenarios=[
        ("hp_menu_cycle", "main menu: a pad attached after boot takes port 1 and moves the cursor at once; detach and re-attach again and again", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"),
            ("menu_at", "main", 0),
            ("vpad", "attach"),
            ("vpress", "dpdown"), ("log_n", r"Virtual Controller takes port 1", 1), ("menu_at", "main", 1),   # the first press claims the port
            ("vpad", "detach"), ("log_n", r"controller disconnected", 1),
            ("press", "DOWN"), ("menu_at", "main", 2),                       # scripted input still works with no pad
            ("vpad", "attach"), ("vpress", "dpdown"), ("log_n", r"takes port 1", 2), ("menu_at", "main", 3),
            ("vpad", "detach"), ("vpad", "attach"), ("vpad", "detach"), ("vpad", "attach"), ("vpad", "detach"),
            ("vpad", "attach"), ("vpress", "dpup"), ("log_n", r"takes port 1", 3), ("menu_at", "main", 2),
            ("vpad", "detach"), ("vpad", "attach"), ("vpad", "detach"),
            ("press", "UP"), ("menu_at", "main", 1),
        ]),
        ("hp_settings_menu", "the settings menu open while a pad is attached and detached: still opens and closes, the pad works after", [
            ("vpad", "attach"),
            ("ui", "esc"), ("ui_state", "open=1"),
            ("vpad", "detach"), ("vpad", "attach"), ("vpad", "detach"),
            ("ui_state", "open=1"),
            ("ui", "esc"), ("ui_state", "open=0"),
            ("vpad", "attach"), ("vpress", "dpdown"), ("menu_at", "main", 2),
            ("vpad", "detach"),
        ]),
        ("hp_two_pads", "two pads: the first to press is port 1, the second port 2; the game reads both", [
            ("vpad", "attach"), ("vpad2", "attach"),
            ("vpress2", "dpup"), ("menu_at", "main", 1),                   # the SECOND pad presses first: it is port 1 and moves the cursor
            ("log_n", r"Virtual Controller takes port 1", 1),
            ("vpress", "leftshoulder"),                                    # the first pad presses next: port 2
            ("log_n", r"Virtual Controller takes port 2", 1),
            ("ctl", "vpad2 button leftshoulder 1"), ("wait", 8),
            ("ctl_match", "inputstate", r"last=0x0020 "),                  # port 1 = pad 2: L (0x0020)
            ("ctl", "vpad2 button leftshoulder 0"),
            ("ctl", "vpad button rightshoulder 1"), ("wait", 8),
            ("ctl_match", "inputstate", r"last2=0x0010$"),                 # port 2 = pad 1: R (0x0010)
            ("ctl", "vpad button rightshoulder 0"),
            ("vpad2", "detach"),                                           # port 1's pad leaves: the other pad becomes port 1
            ("vpress", "dpdown"), ("menu_at", "main", 2),
        ]),
    ]),
    dict(name="hotplug-play", config="hotplugp-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden"], scenarios=[
        ("hp_level", "in a level: a pad attached, detached and re-attached works at once, and the game keeps running", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"), ("go", "A", "tips_ready", "in_level"),
            ("vpad", "attach"), ("pad_records", "vpad:a", [3]),
            ("vpad", "detach"), ("wait", 30), ("pad_records", "CD", [3]),
            ("vpad", "attach"), ("pad_records", "vpad:y", [0]),
            *[step for _ in range(30) for step in (("vpad", "detach"), ("vpad", "attach"))],
            ("pad_records", "vpad:x", [1]),
            ("vpad", "detach"),
            ("dl", 10, 500),
            ("fps", 5, 20.0),
        ]),
    ]),
    # TWO PLAYERS with two virtual pads: the first pad to press is player 1, the second player 2; both choose a skater and the split-screen
    # level runs with each pad on its own port. (Hand play 2026-10-14: "no way to select a second controller for player 2".)
    dict(name="two-players", config="two-players-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden"], scenarios=[
        ("two_players_flow", "TWO PLAYERS > GRAFFITI: both pads pick a skater, the split-screen level loads, each pad reaches its own port", [
            *_TWO_PLAYERS_TO_LEVEL,
            ("shot", "two_players_level"),
            *_TWO_PLAYERS_PORTS,
        ]),
    ]),
    # Matrix-group IDs (src/interp_ids.cpp): pairing statistics + idsdump (RT64's verdict per world transform joined with the display-list walk).
    dict(name="idsprobe", config="idsprobe-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--refresh", "60", "--present-size", "480x360"], scenarios=[
        ("ids_probe", "evidence: pairing statistics standing / skating / turning / ollie, then idsdump", [
            ("wait_for", "title"),
            ("go", "START", "title", "main_menu"),
            ("menu", "main", 3),
            *TO_LEVEL_SELECT,
            ("ctl", "idsscan 1"),
            ("go", "A", "level_select", "tips_ready"),
            ("go", "A", "tips_ready", "in_level"),
            ("wait", 30),
            *IDS_PHASES(40, True),
        ]),
    ]),
    # Performance of the matrix IDs (docs/interpolation-ids.md, "Performance"): VISIBLE window, no capture; IDs off / on interleaved, a present-dump block and an idsstat block
    # for the cost of those debug modes, and a --refresh original baseline in the second session.
    dict(name="idsbench", config="idsbench-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro"] + __import__("os").environ.get("THPS_BENCH_ARGS", "").split(), scenarios=[
        ("ids_bench", "performance: fps, frame-time percentiles, ID walk cost; IDs off/on interleaved (notes)", [
            ("wait_for", "title"),
            ("go", "START", "title", "main_menu"),
            ("menu", "main", 3),
            *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"),
            ("go", "A", "tips_ready", "in_level"),
            ("wait", 30),
            ("vpad", "attach"), ("wait", 30),
            ("bench", 12, "keep"),                       # warm-up
            ("bench", 20, "off"), ("bench", 20, "on"), ("bench", 20, "naive"), ("bench", 20, "off"), ("bench", 20, "on"), ("bench", 20, "naive"),
            ("bench", 20, "off"), ("bench", 20, "on"), ("bench", 20, "naive"),
        ]),
    ]),
    dict(name="idsbench-orig", config="idsbench-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--refresh", "original"] + __import__("os").environ.get("THPS_BENCH_ARGS", "").split(), scenarios=[
        ("ids_bench_orig", "performance baseline: --refresh original (30 fps, no interpolation)", [
            ("wait_for", "title"),
            ("go", "START", "title", "main_menu"),
            ("menu", "main", 3),
            *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"),
            ("go", "A", "tips_ready", "in_level"),
            ("wait", 30),
            ("vpad", "attach"), ("wait", 30),
            ("bench", 12, "keep"),
            ("bench", 20, "keep"), ("bench", 20, "keep"), ("bench", 20, "keep"),
        ]),
    ]),
    # Walk time over a whole boot (front end, loading screens, level start) and a RETRY (camera cut + level restart): the ten slowest walks with their CPU time (`ids slow`).
    dict(name="idsload", config="idsload-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--refresh", "60"], scenarios=[
        ("ids_load", "walk times over front end, level load and a camera cut (notes)", [
            ("ctl", "ids slowreset"),
            ("wait_for", "title"),
            ("go", "START", "title", "main_menu"),
            ("menu", "main", 3),
            *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"),
            ("go", "A", "tips_ready", "in_level"),
            ("wait", 60),
            ("ctl", "ids slow"),
            ("ctl", "ids slowreset"),
            ("hfr_cut",), ("wait", 90),
            ("ctl", "ids slow"),
        ]),
    ]),
    dict(name="idsclip", config="idsclip-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--refresh", "60", "--present-size", "480x360"], scenarios=[
        ("ids_clip", "evidence: every composited frame of ~8 s of skating (THPS_IDS=1: IDs on), into build/ids/clip", [
            ("wait_for", "title"),
            ("go", "START", "title", "main_menu"),
            ("menu", "main", 3),
            *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"),
            ("go", "A", "tips_ready", "in_level"),
            ("wait", 30),
            *IDS_CLIP(),
        ]),
    ]),
    # High frame rate (Q18): 60 Hz frame interpolation in the Warehouse (every composited frame
    # captured small), a camera cut on RETRY, and input latency on the main menu. Explicit
    # --refresh 60 so the session doesn't depend on the default refresh setting.
    dict(name="hfr", config="hfr-config", fresh_pak=True, wav=False,
         args=["--refresh", "60", "--skip-intro", "--hidden", "--present-size", "480x360"], scenarios=[
        ("input_latency", "main menu: press -> first changed presented frame (median of 6, <= 100 ms)", [
            ("wait_for", "title"),
            ("go", "START", "title", "main_menu"),
            ("latency", "DOWN/UP", 6, 100.0),
        ]),
        ("hfr_motion", "60 Hz interpolation: every refresh shows a new, evenly spaced frame while skating", [
            ("menu", "main", 3),
            *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"),
            ("go", "A", "tips_ready", "in_level"),
            ("wait", 30),
            ("hfr_motion", 4.0, "SUP", dict(fm60=0.9, alt=0.3, interp=0.9, paired=0.9, dropped=0.05)),
            ("fps", 5, 28.0),
        ]),
        ("hfr_cut", "RETRY is a camera cut: that frame is not interpolated", [("hfr_cut",)]),
    ]),
]

# HUD placement (src/hud_anchor.cpp), regression. `expand` is the DEFAULT (2026-10-14; host.h kDefaultHud): with no --hud the in-level HUD (score, special
# meter, tips) is anchored to the picture's edge at 16:9 and the pause menu stays a centred 4:3 page (overlay rule); an explicit `--hud original` emits
# nothing (the old picture); at 4:3 (--aspect original) nothing moves whatever the setting says. The pictures: the optin hud-* sessions below.
_HUD_TO_LEVEL = [
    *BOOT_TO_MENU,
    ("menu", "main", 3),
    *TO_LEVEL_SELECT,
    ("go", "A", "level_select", "tips_ready"),
    ("go", "A", "tips_ready", "in_level"),
    ("wait", 60),
]
SESSIONS += [
    dict(name="hud", config="hud-config", fresh_pak=True, wav=False, present_every=30,
         args=["--aspect", "16:9", "--window", "1280x720", "--res-scale", "2", "--msaa", "4", "--hidden"], scenarios=[
        ("hud_edges", "default HUD placement (expand) at 16:9: the in-level HUD is anchored to the left edge; the pause menu is not", [
            *_HUD_TO_LEVEL,
            ("ctl_match", "hud", r"mode=expand supported=1 tasks_anchored=[1-9]\d* groups left=[1-9]\d* .* overlay_tasks=0 "),
            ("keep_present", "hud_edges_level"),
            ("go", "START", "in_level", "pause"),
            ("wait", 30),
            ("ctl_match", "hud", r"overlay_tasks=[1-9]"),
            ("keep_present", "hud_edges_pause"),
        ]),
    ]),
    dict(name="hud-original", config="hud-original-config", fresh_pak=True, wav=False, present_every=30,
         args=["--aspect", "16:9", "--window", "1280x720", "--res-scale", "2", "--msaa", "4", "--hidden", "--hud", "original"], scenarios=[
        ("hud_original_inert", "explicit --hud original at 16:9: nothing is anchored (the picture before HUD placement existed)", [
            *_HUD_TO_LEVEL,
            ("ctl_match", "hud", r"mode=original supported=1 tasks_anchored=0 groups left=0 centre=0 right=0 overlay_tasks=0"),
            ("keep_present", "hud_original_level"),
        ]),
    ]),
    dict(name="hud-43", config="hud-43-config", fresh_pak=True, wav=False,
         args=["--aspect", "original", "--window", "960x720", "--hidden"], scenarios=[
        ("hud_default_43", "default HUD placement at 4:3 (--aspect original): the setting says expand, nothing is anchored", [
            *_HUD_TO_LEVEL,
            ("ctl_match", "hud", r"mode=expand supported=1 tasks_anchored=0 groups left=0 centre=0 right=0 overlay_tasks=0"),
        ]),
    ]),
]

# HUD placement (src/hud_anchor.cpp): present captures of the same in-level states with `--hud original` / `expand` at 16:9 and 21:9
# (hud_<free|career>_<variant>_<state>.png in the run's out dir), to look at; run with --session hud-free-edge169 etc.
SESSIONS += [
    dict(name=f"hud-{kind}-{var}", config=f"hud-{kind}-{var}-config", fresh_pak=True, wav=False, present_every=30, optin=True,
         args=["--aspect", asp, "--window", win, "--res-scale", "2", "--msaa", "4", "--hidden", "--hud", *hud.split()], scenarios=[
        (f"hud_{kind}_{var}", f"HUD placement {hud} at {asp}: {kind} run (HUD, trick, pause)", [
            *BOOT_TO_MENU,
            *((("menu", "main", 3),) if kind == "free" else (("menu", "main", 0), ("go", "A", "main_menu", "career_menu"), ("menu_at", "career", 1), ("menu", "career", 1))),
            *TO_LEVEL_SELECT,
            *([("go", "A", "level_select", "tips_ready")] if kind == "free" else [("go", "A", "level_select", "career_goals"), ("wait", 20), ("keep_present", f"hud_{kind}_{var}_goals")]),
            ("go", "A", "tips_ready" if kind == "free" else "career_goals", "in_level"),
            ("wait", 90),
            ("keep_present", f"hud_{kind}_{var}_level"),
            ("vpad", "attach"),
            ("skate", [("vpad", "a", 1), ("wait", 10), ("vpad", "a", 0), ("wait", 3),
                       ("axis", "leftx", 32767), ("vpad", "x", 1), ("wait", 6), ("vpad", "x", 0), ("axis", "leftx", 0)], "trick"),
            ("wait", 3),
            ("keep_present", f"hud_{kind}_{var}_trick"),
            ("ctl", "hud"),
            ("go", "START", "in_level", "pause"),
            ("wait", 30),
            ("keep_present", f"hud_{kind}_{var}_pause"),
            *([] if kind == "free" else [
                ("menu", "pause", 3), ("go", "A", "pause", "statistics"), ("wait", 20), ("keep_present", f"hud_{kind}_{var}_stats"),
                ("go", "A", "statistics", "postrun_menu"), ("wait", 20), ("keep_present", f"hud_{kind}_{var}_postrun"),
            ]),
        ]),
    ])
    for kind in ("free", "career")
    for (var, asp, win, hud) in (("orig169", "16:9", "1280x720", "original"), ("orig219", "21:9", "1280x540", "original"), ("edge169", "16:9", "1280x720", "expand"), ("edge219", "21:9", "1280x540", "expand"),
                                 ("right169", "16:9", "1280x720", "expand --hud-force right"), ("clamp219", "21:9", "1280x540", "16:9"))
]

# The SPECIAL meter is a texrect frame plus a G_FILLRECT for the bar's fill. The fill used to keep the regular (4:3, centred) placement while the
# frame was anchored to the left edge (playtest 2026-10-14: "the fill starts midway through the special bar and extends through"). The test pokes a partly
# filled meter into the skater (Skater_MagicTime: 750 = full), then asserts that every HUD fill went through the grouping, none of it centred (`fills` in
# the `hud` report), and that on the presented picture the fill lies inside the frame (step `meter_inside`).
# Measured (exploration 2026-10-15): the fill is an animation. Its displayed length grows a few units per frame towards the poked value and its colour pulses (green
# while the meter runs down, yellow when full); one poke fades out within a few frames. So the test re-pokes mMagicTime 700 (of 750) every 6 frames for 120 frames:
# by then the fill spans most of the bar, which is what matters (it must END inside the frame).
_SPECIAL = [st for _ in range(20) for st in (("poke_skater", "Skater_MagicTime", 700, "Skater_MagicPoints", 1000), ("wait", 6))]
_SPECIAL_BY_OFFSET = [st for _ in range(20) for st in (("poke_skater", 0x34C, 700, 0x348, 1000), ("wait", 6))]   # for a binary from before the field names (before / after pictures: THPS1_BINARY=<old build>)
SESSIONS += [
    dict(name=f"hud-special{suffix}", config=f"hud-special{suffix}-config", fresh_pak=True, wav=False, present_every=3, optin=optin,
         args=["--aspect", asp, "--window", win, "--res-scale", "2", "--msaa", "4", "--hidden", *hud], scenarios=[
        (f"hud_special{suffix.replace('-', '_')}", f"special meter, partly filled, HUD {' '.join(hud) or 'expand (default)'} at {asp}: the fill lies inside its frame", [
            *_HUD_TO_LEVEL,
            *(_SPECIAL_BY_OFFSET if "old" in suffix else _SPECIAL),
            ("keep_present", f"hud_special{suffix.replace('-', '_')}"),
            *checks,
        ]),
    ])
    for (suffix, asp, win, hud, optin, checks) in (
        ("", "16:9", "1280x720", [], False, [("ctl_match", "hud", r"fills left=[1-9]\d* centre=0 right=0"), ("meter_inside",)]),
        ("-219", "21:9", "1280x540", [], False, [("ctl_match", "hud", r"fills left=[1-9]\d* centre=0 right=0"), ("meter_inside",)]),
        ("-clamp219", "21:9", "1280x540", ["--hud", "16:9"], True, [("ctl_match", "hud", r"fills left=[1-9]\d* centre=0 right=0"), ("meter_inside",)]),
        ("-old169", "16:9", "1280x720", [], True, [("meter_inside",)]),   # (expected to FAIL on a build from before the fix)
        ("-old219", "21:9", "1280x540", [], True, [("meter_inside",)]),
        ("-orig169", "16:9", "1280x720", ["--hud", "original"], True, [("ctl_match", "hud", r"fills left=0 centre=0 right=0"), ("meter_inside",)]),
        ("-orig219", "21:9", "1280x540", ["--hud", "original"], True, [("ctl_match", "hud", r"fills left=0 centre=0 right=0"), ("meter_inside",)]),
    )
]

# Skate around for ~40 s (ollie / flip / grab / grind in a loop) with --hud-debug: host.log lists every anchored group; THPS1's HUD should have nothing at the right
# (grep "-> right"): the play test saw stray glyphs near the right edge.
SESSIONS += [
    dict(name="hud-skate", config="hud-skate-config", fresh_pak=True, wav=False, optin=True, present_every=3,
         args=["--aspect", "16:9", "--window", "1280x720", "--res-scale", "1", "--msaa", "0", "--hidden", "--hud", "expand", "--hud-debug", "1000000"], scenarios=[
        ("hud_skate", "skate around (host.log: groups by anchor)", [
            *_HUD_TO_LEVEL,
            ("vpad", "attach"),
            ("ctl", "vpad axis lefty -32000"),
            *[st for i in range(10) for st in (("vpress", "a"), ("wait", 25), ("vpress", "x"), ("wait", 15), ("vpress", "b"), ("wait", 40), ("vpress", "y"), ("wait", 30),
                                              ("ctl", f"vpad axis leftx {-32000 if i % 2 else 32000}"))],
            ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0"),
            ("ctl_match", "hud", r"."),
        ]),
    ]),
]

SESSIONS += [
    dict(name="hud-dbg", config="hud-dbg-config", fresh_pak=True, wav=False, optin=True,
         args=["--aspect", "16:9", "--window", "1280x720", "--res-scale", "1", "--msaa", "0", "--hidden", "--hud", "expand", "--hud-debug", "100000"], scenarios=[
        ("hud_dbg", "debug", [
            *BOOT_TO_MENU, ("menu", "main", 3), *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"), ("go", "A", "tips_ready", "in_level"),
            ("wait", 40),
            ("go", "START", "in_level", "pause"),
            ("wait", 20),
            ("press", "B"), ("wait", 40),
        ]),
    ]),
]

# Cheats (test aids, game/cheats.cpp). SELECT COURSE order: 0 Warehouse, 1 School (2 tapes), 2 Mall (5), 3 Skate Park (8), 4 Downtown (1 medal),
# 5 Downhill Jam (13), 6 Burnside (18), 7 Streets (2 medals), 8 Roswell (26). A course record's word +0x10 is "locked" (gCourseTable, stride
# 0x78: course k at +0x10 + k * 0x78). The career's skater records (gCareerSkaters, 10 x 20 bytes) must be the same before and after: the
# cheat answers "available" without giving tapes or medals, so nothing of it can reach the Controller Pak save.
_CS_LOCKED = lambda k: f"@gCourseTable+{0x10 + k * 0x78:#x}"
_CS_CAREER_SELECT = [
    ("wait_for", "title"), ("go", "START", "title", "main_menu"),
    ("menu", "main", 0), ("go", "A", "main_menu", "career_menu"), ("menu", "career", 1),   # NEW GAME (fresh pak, fresh career)
    *TO_LEVEL_SELECT,
]
_CS_RIGHT = lambda n: [s for _ in range(n) for s in (("press", "RIGHT"), ("wait", 12))]
SESSIONS += [
    dict(name="cheats-unlock", config="cheats-unlock-config", fresh_files=["cheats.cfg"], fresh_pak=True, wav=False, args=["--skip-intro"], scenarios=[
        ("unlock_off_locked", "fresh career, no cheat: School needs 2 tapes, its locked word is set and A does nothing", [
            *_CS_CAREER_SELECT,
            ("peek_save", "career", "@gCareerSkaters", 50),
            *_CS_RIGHT(1),
            ("peek_is", _CS_LOCKED(1), 1, "School locked"),
            ("press_moves", "A", False),
        ]),
        ("unlock_live", "Unlock All Levels turned on live (the menu toggle): tape and medal courses are available, the career is unchanged", [
            ("cheat", "unlock_levels", 1),
            ("log", r"cheats: unlock_levels on"),
            ("file_contains", "cheats.cfg", r"(?m)^unlock_levels = 1$"),
            *_CS_RIGHT(1), ("press", "LEFT"), ("wait", 12),            # the lock is recomputed when the cursor moves
            ("peek_is", _CS_LOCKED(1), 0, "School locked"),
            *_CS_RIGHT(3),
            ("peek_is", _CS_LOCKED(4), 0, "Downtown (medals) locked"),
            *_CS_RIGHT(3),
            ("peek_is", _CS_LOCKED(7), 0, "Streets (medals) locked"),
            ("peek_same", "career"),
            ("press_moves", "A", True),                                    # Streets starts (career: the goals screen)
            ("peek_same", "career"),
            ("cheat", "unlock_levels", 0),
            ("file_contains", "cheats.cfg", r"(?m)^unlock_levels = 0$"),
        ]),
    ]),
    dict(name="cheats-unlock-flag", config="cheats-flag-config", fresh_files=["cheats.cfg"], fresh_pak=True, wav=False, args=["--skip-intro", "--unlock-levels"], scenarios=[
        ("unlock_flag_free", "--unlock-levels, FREE SKATE: every course is available (also Downtown / Streets, 'play career mode to unlock')", [
            ("log", r"cheats on: unlock_levels"),
            ("wait_for", "title"), ("go", "START", "title", "main_menu"),
            ("menu", "main", 3),
            *TO_LEVEL_SELECT,
            ("peek_save", "career", "@gCareerSkaters", 50),
            *[s for k in range(1, 9) for s in (("press", "RIGHT"), ("wait", 12), ("peek_is", _CS_LOCKED(k), 0, f"course {k} locked"))],
            *[s for _ in range(4) for s in (("press", "LEFT"), ("wait", 12))],   # back to Downtown (4)
            ("peek_is", _CS_LOCKED(4), 0, "Downtown locked"),
            ("press_moves", "A", True),
            ("peek_same", "career"),
        ]),
    ]),
]

import os as _os
_CS_FREE_LEVEL = [
    ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
    ("go", "A", "level_select", "tips_ready"), ("go", "A", "tips_ready", "in_level"), ("wait", 30),
]
_CS_GRIND_TRY = [("axis", "lefty", -32767), ("vpad", "a", 1), ("wait", 8), ("vpad", "a", 0), ("wait", 3), ("vpad", "y", 1), ("wait", 12), ("vpad", "y", 0)]
SESSIONS += [
    dict(name="cheats-explore", config="cheats-explore-config", fresh_files=["cheats.cfg"], fresh_pak=True, wav=False, optin=True, args=["--skip-intro"] + _os.environ.get("CS_ARGS", "").split(), scenarios=[
        ("cheats_explore", "exploration: Warehouse, forward + ollie + grind presses; skater state / rail balance samples; pause menu", [
            *_CS_FREE_LEVEL,
            ("vpad", "attach"),
            ("ctl", "peek 0x800DE99C 1"),
            ("skater_watch", 80, _CS_GRIND_TRY, [0x82C, 0x9DC, 0x328]),
            ("ctl", "vpad axis lefty 0"),
            ("go", "START", "in_level", "pause"), ("wait", 20), ("shot", "pause"),
            ("peek_ptr", 0x800E9080, 0, 8),
        ]),
    ]),
]

# Perfect Balance / Slow Motion / Skip to Restart (the game's own cheat flags, game/cheats.cpp). One Warehouse run each way:
# - cheats-flags-off: no cheat: TimeScale (the physics step) 256, flags 0, the rail balance moves on the grinds of the scripted run (physics
#   state 4 = on a rail), the pause menu has 4 entries; END RUN -> SAVE CAREER (name "A"), the pak is kept;
# - cheats-flags-on: all four cheats: TimeScale 128 (slow motion halves it at the course start), the balance stays 0 on every rail sample,
#   the pause menu has 5 entries (SKIP TO RESTART: END RUN is the 5th row); the same save is byte-identical to the one without cheats.
_CS_SAVE = lambda pause_menu, end_run: [
    ("ctl", "vpad axis lefty 0"),
    ("go", "START", "in_level", "pause"), ("wait", 20), ("shot", "pause_menu"),
    ("menu", pause_menu, end_run),
    ("go", "A", "pause", "statistics"),
    ("go", "A", "statistics", "postrun_menu"),
    ("menu", "postrun", 5),
    ("go", "A", "postrun_menu", "save_prompt"),
    ("go", "A", "save_prompt", "enter_name"),
    ("press", "UP"),
    ("go", "A", "enter_name", "save_ok"),
    ("pak_log", r"pak 1: wrote \d+ bytes"),
]
_CS_CAREER_RUN = [
    ("wait_for", "title"), ("go", "START", "title", "main_menu"),
    ("menu", "main", 0), ("go", "A", "main_menu", "career_menu"), ("menu", "career", 1),
    *TO_LEVEL_SELECT,
    ("go", "A", "level_select", "career_goals"),
    ("go", "A", "career_goals", "in_level"),
    ("wait", 30),
    ("vpad", "attach"),
]
SESSIONS += [
    dict(name="cheats-flags-off", config="cheats-flags-off-config", fresh_files=["cheats.cfg"], fresh_pak=True, wav=False, args=["--skip-intro"], scenarios=[
        ("flags_off_run", "no cheat: step 256, flags 0, the rail balance moves on grinds", [
            *_CS_CAREER_RUN,
            ("peek_is", "@gTimeScale", 0x100, "TimeScale"),
            ("peek_is", "@gCheatPerfectBalance", 0, "perfect balance flag"),
            ("peek_is", "@gCheatSlowMotion", 0, "slow motion flag"),
            ("peek_is", "@gCheatSkipToRestart", 0, "skip to restart flag"),
            ("skater_watch", 60, _CS_GRIND_TRY, ["Skater_PhysState", "Skater_RailBalance"]),
        ]),
    ]),
    # Save identity: the same run in both sessions (stand still, no input, then END RUN -> SAVE CAREER), so the only difference
    # can be cheat state. The grind runs above play differently with slow motion on (a goal bit the normal-speed run sometimes
    # earns, career record +3 / +0xB), so their saves are not comparable (gate 2026-10-15: v1.0 / Europe differed by 2 bytes).
    dict(name="cheats-save-off", config="cheats-save-off-config", fresh_files=["cheats.cfg"], fresh_pak=True, wav=False, args=["--skip-intro"], scenarios=[
        ("flags_off_save", "no cheat, no input: pause menu END RUN is the 4th entry; -> SAVE CAREER; the pak is kept for the comparison", [
            *_CS_CAREER_RUN,
            *_CS_SAVE("pause", 3),
            ("pak_keep", "cheats_off"),
        ]),
    ]),
    dict(name="cheats-flags-on", config="cheats-flags-on-config", fresh_files=["cheats.cfg"], fresh_pak=True, wav=False, needs=["cheats-flags-off"],
         args=["--skip-intro", "--perfect-balance", "--slow-motion", "--skip-to-restart", "--unlock-levels"], scenarios=[
        ("flags_on_run", "cheats on: step 128, the game's flags 1, the rail balance stays 0 on rails", [
            ("log", r"cheats on: unlock_levels, perfect_balance, slow_motion, skip_to_restart"),
            *_CS_CAREER_RUN,
            ("peek_is", "@gTimeScale", 0x80, "TimeScale"),
            ("peek_is", "@gCheatPerfectBalance", 1, "perfect balance flag"),
            ("peek_is", "@gCheatSlowMotion", 1, "slow motion flag"),
            ("peek_is", "@gCheatSkipToRestart", 1, "skip to restart flag"),
            ("skater_watch", 60, _CS_GRIND_TRY, ["Skater_PhysState", "Skater_RailBalance"], ("Skater_RailBalance", "Skater_PhysState", 4, 0, 2)),
        ]),
        ("flags_live_off", "turned off live: the host clears the game's flags", [
            ("cheat", "perfect_balance", 0), ("cheat", "slow_motion", 0), ("cheat", "skip_to_restart", 0),
            ("wait", 10),
            ("peek_is", "@gCheatPerfectBalance", 0, "perfect balance flag"),
            ("peek_is", "@gCheatSlowMotion", 0, "slow motion flag"),
            ("peek_is", "@gCheatSkipToRestart", 0, "skip to restart flag"),
        ]),
    ]),    dict(name="cheats-save-on", config="cheats-save-on-config", fresh_files=["cheats.cfg"], fresh_pak=True, wav=False, needs=["cheats-save-off"],
         args=["--skip-intro", "--perfect-balance", "--slow-motion", "--skip-to-restart", "--unlock-levels"], scenarios=[
        ("flags_on_save", "all cheats on, no input: pause menu END RUN is the 5th entry (SKIP TO RESTART added); the save is byte-identical to cheats-save-off's", [
            *_CS_CAREER_RUN,
            *_CS_SAVE("pause5", 4),
            ("pak_same", "cheats_off"),
        ]),
    ]),
]

# The in-game settings menu (THPS_MENU builds; skipped otherwise): tests/menu_session.py in the shared host.
from menu_session import MENU_SESSIONS  # noqa: E402
SESSIONS += MENU_SESSIONS

# Attract-mode pacing (playtest "juttery, very juttery in Low Power Mode"): VISIBLE window, default graphics settings (the packaged app's), boot with the
# intro NOT skipped; consecutive 20 s windows of frame timestamps (ftime stop FILE) while the logos / attract demo run, a shot at the end of each.
import os as _os
_RP_DATA = _os.environ.get("THPS_RP_DATA", "/tmp/claude-rp-data")
SESSIONS += [
    dict(name="rp-attract", config="rp-attract-config", fresh_pak=True, wav=False, optin=True,
         args=_os.environ.get("THPS_RP_ARGS", "").split(), scenarios=[
        ("rp_attract", "frame timestamps over the first 100 s of a boot (logos, attract demo)", [
            *[s for i in range(int(_os.environ.get('THPS_RP_WINDOWS', '5'))) for s in (("ctl", "ftime start"), ("wait", 600), ("ctl", f"ftime stop {_RP_DATA}/attract_{_os.environ.get('THPS_RP_TAG', 'normal')}_{i}.csv"), ("shot", f"attract_{i}"))],
        ]),
    ]),
]

# Level-specific captures (worker RP): courses need tapes at the course select; the total tape count of the career object (USA v1.1: pointer at
# 0x800DE7A8, +0x9F0) unlocks them all. RIGHT moves the cursor: Warehouse, School, Downtown, Chicago, Downhill Jam, Mall, Streets, Burnside, Roswell.
_RP_TAG = _os.environ.get("THPS_RP_TAG", "normal")
_RP_ARGS = ["--hidden", "--present-size", "640x360", "--aspect", "16:9", "--window", "1280x720"] + _os.environ.get("THPS_RP_ARGS", "--refresh 60").split()
_RP_SELECT = lambda rights: [
    ("unlock_courses", 0x800DE9F4, int(_os.environ.get("RP_UNLOCK", "0"))),   # per-course career records (USA v1.1), found by the soak worker
    *[s for _ in range(rights) for s in (("press", "RIGHT"), ("wait", 12))],
    ("shot", "course_select"),
]
def _rp_clip(name, steps, every=1):
    return [("ctl", f"pcap {every} {_RP_DATA}/{_RP_TAG}/{name}"), *steps, ("ctl", "pcap 0"), ("wait", 30)]
def _rp_stick(x, y, frames):
    return [("ctl", f"vpad axis leftx {x}"), ("ctl", f"vpad axis lefty {y}"), ("wait", frames)]
_RP_TURNS = [s for i in range(6) for s in _rp_stick(32767 if i % 2 == 0 else -32767, -32767, 8)]
_RP_BACK = _rp_stick(0, 32767, 150)
_RP_FREE = lambda rights: [
    ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
    *_RP_SELECT(rights),
    ("go", "A", "level_select", "tips_ready"),
    ("go", "A", "tips_ready", "in_level"),
    ("wait", 60),
]
def _rp_cam_session(name, rights, what):
    return dict(name=name, config=f"{name}-config", fresh_pak=True, wav=False, optin=True, args=["--skip-intro"] + _RP_ARGS, scenarios=[
        (name.replace("-", "_"), what, [
            *_RP_FREE(rights),
            ("shot", "start"),
            ("vpad", "attach"),
            # holding back from standing (the camera swings round with the skater), then riding and quick left/right turns; IDs on, then off
            *_rp_clip("back_stand_on", _rp_stick(0, 32767, 120)),
            *_rp_stick(0, 0, 30),
            *_rp_stick(0, -32767, 90),
            *_rp_clip("turns_on", _RP_TURNS),
            ("ctl", "hfrcam"), ("ctl", "vpad axis leftx 0"), ("ctl", "vpad axis lefty 0"), ("wait", 60),
            ("ctl", "ids off"),
            *_rp_stick(0, -32767, 90),
            *_rp_clip("turns_off", _RP_TURNS),
            *_rp_stick(0, 0, 30),
            *_rp_clip("back_stand_off", _rp_stick(0, 32767, 120)),
            ("ctl", "hfrcam"), ("ctl", "stats"),
        ]),
    ])
SESSIONS += [
    _rp_cam_session("rp-warehouse", 0, "Warehouse: hold back from standing, quick turns; IDs on / off (evidence clips)"),
    _rp_cam_session("rp-mall", 2, "Mall: hold back from standing, quick turns; IDs on / off (evidence clips)"),
]

# Chicago competition (career): stages of the competition start, an overview clip (every 6th presented frame), border measurements (`edges`, all frames) and RDRAM shots at each.
_RP_EDGE = lambda n: [("ctl", f"edges 90 {_RP_DATA}/{_RP_TAG}/chicago_edges_{n}"), ("shot", f"chicago_stage{n}")]
SESSIONS += [
    dict(name="rp-chicago", config="rp-chi-config", fresh_pak=True, wav=False, optin=True, args=["--skip-intro"] + _RP_ARGS, scenarios=[
        ("rp_chicago", "career: Chicago competition start (intro, goals, run): stale buffer text/strips", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 0),
            ("go", "A", "main_menu", "career_menu"), ("menu", "career", 1),
            *TO_LEVEL_SELECT,
            *_RP_SELECT(3),
            ("ctl", f"pcap 6 {_RP_DATA}/{_RP_TAG}/chicago_overview"),
            ("press", "A"), ("wait", 150), *_RP_EDGE(1),
            ("wait", 150), *_RP_EDGE(2),
            ("press", "A"), ("wait", 100), *_RP_EDGE(3),
            ("wait", 200), *_RP_EDGE(4),
            ("press", "A"), ("wait", 100), *_RP_EDGE(5),
            ("wait", 300), *_RP_EDGE(6),
            ("press", "A"), ("wait", 100), *_RP_EDGE(7),
            ("wait", 300), *_RP_EDGE(8),
            ("ctl", "pcap 0"), ("ctl", "stats"),
            ("pcap", 90, "chicago_level"), ("ring_black", "chicago_level", 14, 40, 5),
        ]),
    ]),
]

# Discovery: course select (tapes poke) -> stage shots of the load / intro / goals screens of a chosen course (RP_COURSE), in free skate or career (RP_MODE=career).
_RP_ONE_FIND = [
    ("wait_for", "title"), ("go", "START", "title", "main_menu"),
    *([("menu", "main", 0), ("go", "A", "main_menu", "career_menu"), ("menu", "career", 1)] if _os.environ.get("RP_MODE") == "career" else [("menu", "main", 3)]),
    *TO_LEVEL_SELECT,
    *_RP_SELECT(int(_os.environ.get("RP_COURSE", "2"))),
    ("press", "A"),
    *[s for i in range(14) for s in (("wait", 100), ("shot", f"stage{i:02d}"), ("press", "A") if i % 3 == 2 else ("wait", 1))],
]
SESSIONS += [
    dict(name="rp-find", config="rp-find-config", fresh_pak=True, wav=False, optin=True, args=["--skip-intro"] + _RP_ARGS, scenarios=[
        ("rp_find", "course select unlock + stage shots for course index RP_COURSE", _RP_ONE_FIND),
    ]),
]

# Downtown "line tear on quick turns" (worker TEAR, 2026-10-15; the private development notes): every composited frame of ~10 s of skating in Downtown at 21:9 with
# quick alternating turns, into <host>/build/tear/<TEAR_TAG>. Exploration only (optin); the frames are analysed offline (tear metrics in the LOG).
# TEAR_ARGS: extra host args (e.g. "--refresh original", "--hfr-tags 0").
_TEAR_DIR = _os.path.join(_os.environ.get("THPS_HOST", "."), "build", "tear", _os.environ.get("TEAR_TAG", "run"))
_TEAR_TURNS = [s for k in range(8) for s in (("ctl", f"vpad axis leftx {32767 if k % 2 else -32767}"), ("wait", 14 + 6 * (k % 3)),
                                              ("ctl", "vpad axis leftx 0"), ("wait", 10))]
SESSIONS += [
    dict(name="tear-downtown", config="tear-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--unlock-levels", "--aspect", "21:9", "--present-size", "840x360"] + _os.environ.get("TEAR_ARGS", "").split(),
         scenarios=[
        ("tear_downtown", "evidence: every composited frame of quick turns in Downtown at 21:9 into build/tear/<TEAR_TAG>", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            *[s for _ in range(4) for s in (("press", "RIGHT"), ("wait", 12))],
            ("peek_is", _CS_LOCKED(4), 0, "Downtown locked"),
            ("press", "A"), ("wait", 600),                   # Downtown's tips screen is not the tips_ready reference (Warehouse)
            ("press", "A"), ("wait", 300),
            ("shot", "downtown_in_level"),
            ("vpad", "attach"),
            ("ctl", "vpad axis lefty -32000"), ("wait", 40),
            ("ctl", f"pcap 1 {_TEAR_DIR}"),
            *_TEAR_TURNS,
            ("ctl", "vpad button a 1"), ("wait", 8), ("ctl", "vpad button a 0"), ("wait", 30),
            *_TEAR_TURNS,
            ("ctl", "pcap 0"), ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0"), ("wait", 20),
        ]),
    ]),
]

# Draw distance (2026-10-17): free skate in one course. At the start spot (the same for every
# setting) a composited frame, triangle counts and buffer use for each factor in DD_AB, then (with the setting from DD_ARGS) the camera
# swung round and a ride with frame times. Exploration only (optin).
# DD_RIGHTS: RIGHT presses at the course select; DD_TAG: output folder name; DD_ARGS: extra host args (e.g. "--draw-distance 2x");
# DD_AB: factors to compare at the start ("1 2 4 8"; empty = none).
_DD_DIR = _os.path.join(_os.environ.get("DD_OUT", "/tmp/dd"), _os.environ.get("DD_TAG", "run"))
_DD_SHOT = lambda name: [("ctl", f"pcap 1 {_DD_DIR}/{name}"), ("wait", 3), ("ctl", "pcap 0"), ("wait", 10)]
# DD_TRACE=1: a dltrace of each factor's frame too (the host log's [trace] lines, after "ok dltrace task=N").
# DD_AB entries "K[:S]": factor K, with `dd showall S` first when given (64:0 / 64:auto = the zone-culled items off / on in the same frame).
_DD_ABP = lambda pre: [s for t in _os.environ.get("DD_AB", "1 2 4 8").split() for k, sa in [(t.split(":") + [""])[:2]] for s in (
    *([("ctl", f"dd showall {sa}")] if sa else []),
    ("ctl", f"dd factor {k}"), ("ctl", "dd reset"), ("wait", 20), *_DD_SHOT(f"{pre}_x{k}{'_s' + sa if sa else ''}"), ("dl", 30, 0), ("ctl", "dd"),
    *([("ctl", "dltrace 1"), ("wait", 10)] if _os.environ.get("DD_TRACE") else []))]
_DD_AB = _DD_ABP("start")
_DD_RIDE_STEPS = lambda ride: [s for st in ride.split() for s in (
    (("ctl", f"vpad axis leftx {st.split(':')[0][2:]}"),) if st.startswith("x=") else (("ctl", f"vpad axis lefty {st.split(':')[0]}"),)) +
    (("wait", int(st.split(':')[1])),)]
# DD_VANTAGES "ride1;ride2": after the start comparison, unpause, ride on (DD_RIDE syntax), pause and compare again (v1_x.., v2_x..).
# DD_CLEAN=1: before each pause also an unpaused x1 and x64 frame (no pause menu over the picture; the skater stands, so nearly the same frame).
# DD_FLIP=1: instead, unpaused, a few consecutive frames with the zone-culled items hidden, then a few with them drawn (`dd showall 0` /
# `auto`; the skater moves only a frame or two in between): what "full" adds, wherever the skater is.
_DD_FLIP = lambda pre: [("ctl", "dd showall 0"), ("wait", 4), ("ctl", f"pcap 1 {_DD_DIR}/{pre}_flip_s0"), ("wait", 4), ("ctl", "pcap 0"),
                        ("ctl", "dd showall auto"), ("wait", 4), ("ctl", f"pcap 1 {_DD_DIR}/{pre}_flip_sauto"), ("wait", 4), ("ctl", "pcap 0")]
_DD_CLEAN = lambda pre: _DD_FLIP(pre) if _os.environ.get("DD_FLIP") else [s for t in (_os.environ.get("DD_AB", "1 2 4 8").split() if _os.environ.get("DD_CLEAN") else []) for k, sa in [(t.split(":") + [""])[:2]] for s in (
    *([("ctl", f"dd showall {sa}")] if sa else []), ("ctl", f"dd factor {k}"), ("wait", 20), *_DD_SHOT(f"{pre}_clean_x{t.replace(':', '_s')}"))]
_DD_VANTAGES = [s for n, ride in enumerate([v for v in _os.environ.get("DD_VANTAGES", "").split(";") if v.strip()], 1) for s in (
    ("press", "START"), ("wait", 45), ("vpad", "attach"), *_DD_RIDE_STEPS(ride),
    ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0"), ("wait", 30), *_DD_CLEAN(f"v{n}"), ("press", "START"), ("wait", 45), *_DD_ABP(f"v{n}"))]
SESSIONS += [
    dict(name="dd-probe", config="dd-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--unlock-levels", "--present-size", "960x540", "--aspect", "16:9", "--window", "1280x720",
               "--refresh", "60"] + _os.environ.get("DD_ARGS", "").split(),
         scenarios=[
        ("dd_probe", "draw distance: start spot per factor (frame, triangles, buffers), camera swing, ride with frame times", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            *[s for _ in range(int(_os.environ.get("DD_RIGHTS", "0"))) for s in (("press", "RIGHT"), ("wait", 12))],
            ("shot", "course_select"),
            ("press", "A"), ("wait", 600),
            # DD_EARLY=N: the level's first frames in N windows of 5 frames, buffers per window (and every 2nd frame captured)
            *([("ctl", f"pcap 2 {_DD_DIR}/early"), ("ctl", "dd reset"), ("press", "A"),
               *[s for _ in range(int(_os.environ["DD_EARLY"])) for s in (("wait", 5), ("ctl", "dd"), ("ctl", "dd reset"))], ("ctl", "pcap 0")]
              if _os.environ.get("DD_EARLY") else [("press", "A"), ("wait", 300)]),
            ("shot", "in_level"),
            ("ctl", "dd"),
            *([("ctl", f"ramsave {_DD_DIR}/ram_start.bin")] if _os.environ.get("DD_RAMSAVE") else []),
            # DD_PRE "KEY:frames ...": presses before the ride, with a shot after each (with --skip-to-restart in DD_ARGS: START, then the pause
            # menu's SKIP TO RESTART, the 4th row, to one of the course's restart points: repeatable spots all over the course)
            *[s for st in _os.environ.get("DD_PRE", "").split() for s in (("press", st.split(":")[0]), ("wait", int(st.split(":")[1])), ("shot", "pre"))],
            # DD_RIDE "lefty:frames lefty:frames ..." (stick y, negative = forward; leftx with x=) before the comparison: to a spot with a long view
            # (DD_RIDECAP=N: every Nth composited frame of it, in ridecap/)
            ("vpad", "attach"),
            *([("ctl", f"pcap {_os.environ['DD_RIDECAP']} {_DD_DIR}/ridecap")] if _os.environ.get("DD_RIDECAP") else []),
            *[s for st in _os.environ.get("DD_RIDE", "").split() for s in (
                (("ctl", f"vpad axis leftx {st.split(':')[0][2:]}"),) if st.startswith("x=") else (("ctl", f"vpad axis lefty {st.split(':')[0]}"),)) +
                (("wait", int(st.split(':')[1])),)],
            *([("ctl", "pcap 0")] if _os.environ.get("DD_RIDECAP") else []),
            ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0"),
            *_DD_CLEAN("start"),
            *([("press", "START"), ("wait", 45)] if _os.environ.get("DD_PAUSE", "1") == "1" else []),   # paused: the same picture for every factor
            *_DD_AB,
            *_DD_VANTAGES,
            # DD_CTL "cmd1;cmd2;..." at the paused spot after DD_AB (exploration: "dd factor 2;dltrace 1;dd factor 4;dltrace 1")
            *[s for c in _os.environ.get("DD_CTL", "").split(";") if c.strip() for s in (("ctl", c.strip()), ("wait", 20))],
            ("ctl", "dd mode " + _os.environ.get("DD_MODE", "original")),
            *([("ctl", "dd factor " + _os.environ["DD_FACTOR"])] if _os.environ.get("DD_FACTOR") else []),   # exploration: any factor
            *([("ctl", "dd testcap " + _os.environ["DD_TESTCAP"])] if _os.environ.get("DD_TESTCAP") else []),   # exercise the governor
            ("ctl", "dd reset"),
            *([("press", "START"), ("wait", 45)] if _os.environ.get("DD_PAUSE", "1") == "1" else []),
            ("vpad", "attach"),
            ("ctl", "vpad axis lefty 32767"), ("wait", 120), ("ctl", "vpad axis lefty 0"), ("wait", 40),
            *_DD_SHOT("back"),
            ("dl", 30, 0),
            ("ctl", "ftime start"),
            *([("ctl", f"pcap {_os.environ['DD_TOUR']} {_DD_DIR}/tour")] if _os.environ.get("DD_TOUR") else []),   # every Nth composited frame of the ride
            ("ctl", "vpad axis lefty -32767"),
            # DD_BURSTS=N: N short bursts of consecutive frames along the ride (b0, b1, ...: pairs of runs line up within a burst)
            *[s for k in range(int(_os.environ.get("DD_BURSTS") or "0")) for s in (("wait", 40), *_DD_SHOT(f"b{k}"),
                                                                              ("ctl", f"vpad axis leftx {(-32767, 0, 32767, 0)[k % 4]}"))],
            ("wait", 150),
            *_DD_SHOT("ride1"),
            *[s for k in range(6) for s in (("ctl", f"vpad axis leftx {32767 if k % 2 else -32767}"), ("wait", 20), ("ctl", "vpad axis leftx 0"), ("wait", 20))],
            *_DD_SHOT("ride2"),
            ("dl", 30, 0),
            *([("ctl", "pcap 0")] if _os.environ.get("DD_TOUR") else []),
            ("ctl", f"ftime stop {_DD_DIR}/ftime.csv"),
            ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0"), ("wait", 20),
            ("ctl", "dd"), ("ctl", "stats"),
        ]),
    ]),
]
# Heap headroom with the always-allocated 2048-matrix pools (2026-10-22, the private development notes; optin, measurement): FREE SKATE,
# DH_COURSES courses back to back in one process (from the course select's DH_FIRST-th course, Warehouse = 0),
# each loaded, skated ~12 s and ended (END RUN -> LEVEL SELECT). `dd heap` before each course (its reply has the previous course's
# low-water marks, then resets them), after the load, after the ride and after the exit. DD_ARGS: extra host args
# (e.g. "--draw-distance full", "--dd-buffers original").
_DH_PLAY = [("ctl", "vpad axis lefty -32767"),
            *[x for k in range(12) for x in (("ctl", f"vpad axis leftx {(-32767, 0, 32767, 0)[k % 4]}"),
                                             ("ctl", "vpad button a 1"), ("wait", 8), ("ctl", "vpad button a 0"), ("wait", 22))],
            ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0")]
SESSIONS += [
    dict(name="dd-heap", config="dd-heap-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--unlock-levels"] + _os.environ.get("DD_ARGS", "").split(), scenarios=[
        ("dd_heap", "heap headroom: courses back to back, `dd heap` low-water marks per course", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            *[s for i in range(int(_os.environ.get("DH_COURSES", "9"))) for s in (
                # FREE SKATE's course select starts at Warehouse again after END RUN
                *[s for _ in range(int(_os.environ.get("DH_FIRST", "0")) + i) for s in (("press", "RIGHT"), ("wait", 12))],
                ("shot", f"select_{i}"),
                ("ctl", "dd heap reset"),
                ("press", "A"), ("wait", 600), ("press", "A"), ("wait", 300),
                ("shot", f"in_level_{i}"),
                ("ctl", "dd heap"),
                *([("vpad", "attach")] if i == 0 else []),
                *_DH_PLAY,
                ("ctl", "dd heap"), ("ctl", "dd"),
                ("press", "START"), ("wait", 45), ("menu", "pause", 3), ("press", "A"), ("wait", 90),
                ("press", "DOWN"), ("press", "A"), ("wait_for", "level_select"), ("wait", 30),
                ("ctl", "dd heap"))],
            ("ctl", "dd heap"),
        ]),
    ]),
]
# Course cycle (src/music.cpp; the THPS2 crash after a few courses, 2026-10-17: THPS1 has the same music player): Warehouse, School,
# Downtown, Downhill Jam back to back in a career (Chicago is a competition), each ended from the pause menu: END RUN -> statistics ->
# the post-run menu -> LEVEL SELECT. The course select keeps its cursor on the last course (RIGHT moves it).
from course_cycle import course_cycle_session, LOAD_LINE  # noqa: E402
# Draw distance Full and the game's events (2026-10-22): Full unhides the course items the trigger scripts hide by area, never the ones an
# event hides. Mall, free skate, no input: the skater rolls down the start corridors and through the CLOSED / CERRADO signs at the end of
# the CITY MALL tunnel; breaking them hides course items 356 and 359 by name (flags 0x1061: the trigger command's hide by name 0x80035250,
# so World_FindItem marks them as event-owned). Before: drawn; after: hidden for good, also with Full.
SESSIONS += [dict(name="dd-event", config="dd-event-config", fresh_pak=True, wav=False,
    args=["--skip-intro", "--hidden", "--unlock-levels", "--draw-distance", "full", "--window", "960x540"], scenarios=[
    ("dd_event_item", "draw distance full: the Mall signs the skater breaks stay hidden afterwards (event-owned), before that they are drawn", [
        ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
        ("press", "RIGHT"), ("wait", 12), ("press", "RIGHT"), ("wait", 12),
        # The A that starts the run is pressed until the course is on screen (the HUD checkpoint): with a fixed wait a slow load once
        # swallowed it, the run started late and the no-input roll had not reached the signs when they were checked. Mall's tips screen
        # does not match the shared `tips_ready` reference, so the in-level checkpoint is the anchor.
        ("press", "A"), ("wait", 600), ("go", "A", None, "in_level"), ("wait", 30),
        ("ctl_match", "dd item 356", r"event 0 drawn 1"),
        ("ctl_match", "dd item 359", r"event 0 drawn 1"),
        ("ctl_same", "dd item 356", r" named (\d+) ", "named"),   # what the course's set-up scripts named
        ("shot", "before_signs"),
        ("wait", 900),
        ("shot", "after_signs"),
        ("ctl_match", "dd item 356", r"flags 0x1061 zone 0x00 event 1 drawn 0"),
        ("ctl_match", "dd item 359", r"flags 0x1061 zone 0x00 event 1 drawn 0"),
        ("go", "START", "in_level", "pause"),   # a pause is not a new course: the record and its event ownership stay
        ("wait", 60), ("go", "START", "pause", "in_level"), ("wait", 10),
        ("ctl_match", "dd item 356", r"flags 0x1061 zone 0x00 event 1 drawn 0"),
    ]),
    # RETRY rebuilds the course, with the item list at the same address and count (review 2026-10-26, finding 7): the zone record starts
    # again, so the signs are the game's again (not event-owned, drawn) and the event-owned items are exactly what the set-up named (before
    # the fix the record survived the RETRY: the signs stayed event-owned, `named` two more).
    ("dd_event_retry", "pause > RETRY: the signs are back and not event-owned; event ownership is the new run's", [
        ("go", "START", "in_level", "pause"), ("menu", "pause", 1), ("press", "A"), ("wait", 300), ("go", "A", None, "in_level"), ("wait", 30),
        ("ctl_match", "dd item 356", r"event 0 drawn 1"),
        ("ctl_match", "dd item 359", r"event 0 drawn 1"),
        ("ctl_same", "dd item 356", r" named (\d+) ", "named"),
        ("ctl_match", "dd", r"course_starts=[2-9]"),
    ]),
    # Governor feedback across a transition (review 2026-10-26, finding 6), deterministic: `dd stale 99` gives a 99 % sample measured across
    # a transition and one built before it, in one critical section: both dropped, Full keeps its ceiling. `dd feed 99` (the control case)
    # gives a current one once the settle is over: it panics.
    ("dd_stale_feedback", "a stale buffer sample after a setting change is dropped; a current one still acts", [
        ("ctl", "dd mode full"), ("wait", 10), ("ctl", "dd reset"),
        ("ctl_match", "dd stale 99", r"ceiling=64\.00 .* panics=0 .* stale_dropped=1 settle_dropped=[1-9]"),
        ("wait", 10),
        ("ctl_match", "dd feed 99", r"ceiling=(?!64\.00)\d.* panics=1 "),
        ("ctl_match", "dd mode full", r"ceiling=64\.00 "),
    ]),
])]
# Downhill Jam's lower end (the pool, blocks, the building below the BRETT wall) is 27 items with flag 0x2000 (no sphere test), zone-hidden
# at the start; "full" draws them too (until 2026-10-23 they were left hidden and popped in as the skater came over the edge). Item 133 is
# one of them. (The flags may read with the hidden bits cleared when the reply lands during the draw call: 0x2000.)
SESSIONS += [dict(name="dd-downhill", config="dd-downhill-config", fresh_pak=True, wav=False,
    args=["--skip-intro", "--hidden", "--unlock-levels", "--draw-distance", "full", "--window", "960x540"], scenarios=[
    ("dd_downhill_end", "draw distance full: Downhill Jam's zone-hidden 0x2000 items (the lower end) are drawn from the start", [
        ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
        *[s for _ in range(5) for s in (("press", "RIGHT"), ("wait", 12))],
        ("press", "A"), ("wait", 600), ("press", "A"), ("wait", 60),
        ("shot", "in_level"),
        ("ctl_match", "dd item 133", r"flags 0x20(41|00) zone 0x41 event 0 drawn 1"),
        ("ctl_match", "dd item 214", r"flags 0x20(41|00) zone 0x41 event 0 drawn 1"),
    ]),
])]

SESSIONS += [course_cycle_session(
    "course-cycle", [("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 0), ("go", "A", "main_menu", "career_menu"),
                     ("menu", "career", 1), *TO_LEVEL_SELECT],
    [[], [("press", "RIGHT"), ("wait", 20)], [("press", "RIGHT"), ("wait", 20)], [("press", "RIGHT"), ("wait", 20), ("press", "RIGHT"), ("wait", 20)]],
    [("go", "A", "level_select", "career_goals"), ("go", "A", "career_goals", "in_level")],
    [("go", "START", "in_level", "pause"), ("menu", "pause", 3), ("go", "A", "pause", "statistics"), ("go", "A", "statistics", "postrun_menu"),
     ("menu", "postrun", 2), ("go", "A", "postrun_menu", "level_select")],
    expect=LOAD_LINE,   # THPS1 stops the menu song before it loads the course's: no channel reads the buffer then (2026-10-17)
)]

# 21:9 far-wall dropout (v0.2 queue item 2), evidence (optin): in a course (DROPOUT_COURSE, 0 = Warehouse; RIGHT presses on the course select),
# skate and turn, then pause at N stops; at each stop a present capture with the normal cull widening (cull 1) and with it x4 (cull 4).
# Anything that appears only at cull 4 is something the game culls that the wide picture should show.
_DROP_COURSE = int(_os.environ.get("DROPOUT_COURSE", "0"))
_DROP_STOPS = int(_os.environ.get("DROPOUT_STOPS", "10"))
SESSIONS += [
    dict(name="dropout-scan", config="dropout-config", fresh_pak=True, wav=False, optin=True, present_every=5,
         args=["--skip-intro", "--hidden", "--unlock-levels", "--aspect", "21:9", "--window", "1680x720", "--present-size", "840x360"]
              + _os.environ.get("DROPOUT_ARGS", "").split(), scenarios=[
        ("dropout_scan", "evidence: paused stops at 21:9, cull 1 vs cull 4 present captures (dropout_<stop>_c1/_c4.png)", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            *[s for _ in range(_DROP_COURSE) for s in (("press", "RIGHT"), ("wait", 12))],
            ("press", "A"), ("wait", 600), ("press", "A"), ("wait", 300),
            ("vpad", "attach"), ("vpress", "leftshoulder"), ("wait", 20),
            *[s for i in range(_DROP_STOPS) for s in (
                ("ctl", "vpad axis lefty -32000"), ("ctl", f"vpad axis leftx {(-1) ** (i // 2) * (12000 + 2500 * i)}"), ("wait", 25 + 5 * (i % 5)),
                ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0"), ("wait", 4),
                ("press", "START"), ("wait", 40),
                ("keep_present", f"dropout_{i:02d}_c1"),
                ("ctl", "cull 4"), ("wait", 12), ("keep_present", f"dropout_{i:02d}_c4"),
                ("ctl", "cull 0"), ("wait", 12), ("keep_present", f"dropout_{i:02d}_c0"),
                ("ctl", "cull 1"), ("wait", 12), ("keep_present", f"dropout_{i:02d}_c1b"),
                ("vpress", "b"), ("wait", 30),
            )],
        ]),
    ]),
]
# The level start at 21:9 (where the dropout was first seen, Q16 "uw219, top right"): every presented frame of the first seconds,
# then the paused frame of cam-219 with a cull A/B.
SESSIONS += [
    dict(name="dropout-start", config="dropout-start-config", fresh_pak=True, wav=False, optin=True, present_every=15,
         args=["--skip-intro", "--hidden", "--aspect", "21:9", "--window", "1680x720", "--res-scale", "2"]
              + _os.environ.get("DROPOUT_ARGS", "").split(), scenarios=[
        ("dropout_start", "evidence: the Warehouse start at 21:9 (pcap) and the paused cam-219 frame, cull 1 / 4", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"), ("press", "A"),
            ("pcap", 150, "start_pcap"),
            ("wait_for", "in_level"),
            ("press_after", "START", 200), ("wait", 30), ("wait_for", "paused_w90"),
            ("keep_present", "start_paused_c1"),
            ("ctl", "cull 4"), ("wait", 12), ("keep_present", "start_paused_c4"), ("ctl", "cull 1"),
        ]),
    ]),
]
# Every presented frame of ~12 s of skating with turns at 21:9 (DROPOUT_COURSE), for an offline pop / hole detector.
SESSIONS += [
    dict(name="dropout-pcap", config="dropout-pcap-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--unlock-levels", "--aspect", "21:9", "--window", "1680x720", "--present-size", "840x360"]
              + _os.environ.get("DROPOUT_ARGS", "").split(), scenarios=[
        ("dropout_pcap", "evidence: every presented frame of skating with turns at 21:9 (drop_pcap/)", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            *[s for _ in range(_DROP_COURSE) for s in (("press", "RIGHT"), ("wait", 12))],
            ("press", "A"), ("wait", 600), ("press", "A"), ("wait", 300),
            ("vpad", "attach"), ("vpress", "leftshoulder"), ("wait", 20),
            ("ctl", "vpad axis lefty -32000"), ("wait", 20),
            ("ctl", "pcap 1 " + _os.path.join(_os.environ.get("THPS_HOST", "."), "build", "droppcap", str(_DROP_COURSE) + _os.environ.get("DROPOUT_TAG", ""))),
            *[s for i in range(12) for s in (("ctl", f"vpad axis leftx {(-1) ** i * 24000}"), ("wait", 15), ("ctl", "vpad axis leftx 0"), ("wait", 15))],
            ("ctl", "pcap 0"), ("ctl", "vpad axis lefty 0"), ("wait", 10),
        ]),
    ]),
]
# 21:9 dropout regression (v0.2 queue item 2): on the paused cam-219 Warehouse frame (an exact input poll), culling 4x wider than the
# widescreen hook does (cull 4) adds nothing to the picture's side bands, so nothing the wide picture shows is culled; culling at 4:3
# (cull 0) takes something away there, so the check would see a dropout. At 21:9, 16:9 and fit window (expand, a 2.9:1 window).
SESSIONS += [
    dict(name=f"dropout-{var}", config=f"dropout-{var}-config", fresh_pak=True, wav=False, present_every=30,
         args=["--skip-intro", "--hidden", "--aspect", asp, "--window", win, "--res-scale", "2"], scenarios=[
        (f"dropout_{var}", f"{asp} ({win}): the paused Warehouse frame, side bands: cull 4 = cull 1, cull 0 loses geometry", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            ("go", "A", "level_select", "tips_ready"), ("go", "A", "tips_ready", "in_level"),
            ("press_after", "START", 200), ("wait", 30), ("wait_for", "paused_w90"),
            # The presented picture fades into the pause screen ~100 presents after the game-visible frame shows it: let it settle.
            # present_every 30 (not 5): at 2100x720 the PNG writers fell seconds behind every 5th present, so the newest capture
            # on disk was an old frame.
            ("wait", 60), ("keep_present", f"dropout_{var}_c1"),
            ("ctl", "cull 4"), ("wait", 20), ("keep_present", f"dropout_{var}_c4"),
            ("ctl", "cull 0"), ("wait", 20), ("keep_present", f"dropout_{var}_c0"),
            ("ctl", "cull 1"), ("wait", 20), ("keep_present", f"dropout_{var}_c1b"),
            # The two 1x captures: the same paused picture, apart from animated textures (a Warehouse poster keeps cycling).
            ("present_cmp", f"dropout_{var}_c1", f"dropout_{var}_c1b", 0.0, 0.01),
            # 4x culling adds nothing in the side bands, ignoring what moved between the two 1x captures.
            ("present_cmp", f"dropout_{var}_c1", f"dropout_{var}_c4", 0.0, 0.0, "sides", f"mask:dropout_{var}_c1b"),
            ("present_cmp", f"dropout_{var}_c1", f"dropout_{var}_c0", 0.0, 1.0, "sides"),
        ]),
    ])
    for (var, asp, win) in (("219", "21:9", "1680x720"), ("169", "16:9", "1280x720"), ("fit", "expand", "2100x720"))
]
# Two players in widescreen (v0.2, rt64-splitscreen-widescreen.patch + hud_anchor.cpp): the side-by-side split screen fills the wide picture,
# each view widened like the one-player camera (RT64 counters: `split` views > 0), each player's HUD block at its own view's left edge
# (groups at the quarter points q0 / q2 of the wide frame), both pads on their own ports. present_split: in each side band outside the
# central 4:3 area >= 90 % of the columns are drawn (the release build: 0 %). `169-hudorig`: HUD Placement `original` places the split
# screen's HUD the same way (the views fill the picture; the 4:3 spot would leave each HUD inside its view), so the same groups are expected.
SESSIONS += [
    dict(name=f"two-players-{var}", config=f"two-players-{var}-config", fresh_pak=True, wav=False, present_every=30,
         args=["--skip-intro", "--hidden", "--aspect", asp, "--window", win, "--res-scale", "2", *extra], scenarios=[
        (f"two_players_{var}", f"two players at {asp}{' (hud original)' if extra else ''}: the split screen fills the picture, each HUD at its view's edge, each pad on its port", [
            *_TWO_PLAYERS_TO_LEVEL,
            ("wait", 60),
            ("present_split", win, 0.90),
            ("keep_present", f"two_players_{var}"),
            ("ctl_match", "split", r"wide=1 views=[1-9]\d* .* hud_tasks=[1-9]\d* groups q0=[1-9]\d* q1=\d+ q2=[1-9]\d* "),
            ("ctl_match", "hud", r"mode=%s " % ("original" if extra else "expand")),
            *_TWO_PLAYERS_PORTS,
        ]),
    ])
    for (var, asp, win, extra) in (("169", "16:9", "1280x720", []), ("219", "21:9", "1680x720", []),
                                   ("169-hudorig", "16:9", "1280x720", ["--hud", "original"]))
]
# Evidence (optin): the HUD of `two-players-169-hudorig` where the first version put it (`--hud-force centre`: every group at the regular, 4:3
# placement, as `original` did in split screen before), the "before" of a before / after pair with that session's capture.
SESSIONS += [
    dict(name="two-players-169-hudorig-old", config="two-players-169-hudorig-old-config", fresh_pak=True, wav=False, present_every=30, optin=True,
         args=["--skip-intro", "--hidden", "--aspect", "16:9", "--window", "1280x720", "--res-scale", "2", "--hud", "original", "--hud-force", "centre"],
         scenarios=[
        ("two_players_169_hudorig_old", "two players at 16:9, hud original, every HUD group at the 4:3 spot (the first version)", [
            *_TWO_PLAYERS_TO_LEVEL,
            ("wait", 60),
            ("keep_present", "two_players_169_hudorig_old"),
            ("ctl", "split"), ("ctl", "hud"),
        ]),
    ]),
]
# Two players with split original (hud expand): each player's HUD stays with its view in the 4:3 middle (hud_sessions.two_players_split_original).
from hud_sessions import two_players_split_original  # noqa: E402
SESSIONS.append(two_players_split_original(_TWO_PLAYERS_TO_LEVEL))
# At 4:3 (--aspect original) the split-screen switch changes nothing: the same paused frame with `split on` and `split off` (live A/B).
SESSIONS += [
    dict(name="two-players-43", config="two-players-43-config", fresh_pak=True, wav=False, present_every=10,
         args=["--skip-intro", "--hidden", "--aspect", "original", "--window", "960x720", "--res-scale", "2"], scenarios=[
        ("two_players_43", "two players at 4:3, paused: the split-screen widening switch leaves the picture unchanged", [
            *_TWO_PLAYERS_TO_LEVEL,
            ("wait", 30),
            *_TWO_PLAYERS_PAUSE,
            ("wait", 60),                                                     # the pause fade (about 100 presents) is over
            ("keep_present", "two_players_43_on", "now"),
            ("ctl", "split off"), ("wait", 15), ("keep_present", "two_players_43_off", "now"),
            ("ctl", "split on"), ("wait", 15), ("keep_present", "two_players_43_on2", "now"),
            ("present_same", "two_players_43_on", "two_players_43_off", 0.0),
            ("present_same", "two_players_43_on", "two_players_43_on2", 0.0),
        ]),
    ]),
]
# Evidence (optin): before / after pictures with `split off` / `on` on the same paused frame, at 16:9, 21:9, 21:9 in a 16:9 window and
# "fit window" (expand, 1600x600), hud expand (default) and original.
SESSIONS += [
    dict(name=f"two-players-ab-{var}", config=f"two-players-ab-{var}-config", fresh_pak=True, wav=False, present_every=10, optin=True,
         args=["--skip-intro", "--hidden", "--aspect", asp, "--window", win, "--res-scale", "2", *extra], scenarios=[
        (f"two_players_ab_{var}", f"two players at {asp} in {win}, paused: split off / on", [
            *_TWO_PLAYERS_TO_LEVEL,
            ("wait", 30),
            *_TWO_PLAYERS_PAUSE,
            ("ctl", "split off"), ("wait", 15), ("keep_present", f"2p_{var}_before"),
            ("ctl", "split on"), ("wait", 15), ("keep_present", f"2p_{var}_after"),
            ("ctl", "split"), ("ctl", "hud"),
        ]),
    ])
    for (var, asp, win, extra) in (("169", "16:9", "1280x720", []), ("219", "21:9", "1680x720", []), ("219in169", "21:9", "1280x720", []),
                                   ("fit", "expand", "1600x600", []), ("169-hudorig", "16:9", "1280x720", ["--hud", "original"]))
]
SESSIONS += [
    dict(name="two-players-hud", config="two-players-hud-config", fresh_pak=True, wav=False, present_every=10, optin=True,
         args=["--skip-intro", "--hidden", "--aspect", "16:9", "--window", "1280x720", "--res-scale", "2", "--hud-debug", "3000"], scenarios=[
        ("two_players_hud", "two players at 16:9, HUD groups (--hud-debug) idle and after player 1's trick", [
            *_TWO_PLAYERS_TO_LEVEL,
            ("wait", 30),
            ("keep_present", "two_players_hud_idle"),
            ("skate", [("vpad", "a", 1), ("wait", 10), ("vpad", "a", 0), ("wait", 3),
                       ("axis", "leftx", 32767), ("vpad", "x", 1), ("wait", 6), ("vpad", "x", 0), ("axis", "leftx", 0)], "trick"),
            ("wait", 3),
            ("keep_present", "two_players_hud_trick"),
            ("wait", 20),
            ("keep_present", "two_players_hud_trick2"),
            ("ctl", "split"), ("ctl", "hud"),
        ]),
    ]),
]
# Evidence (optin): culling A/B on the paused split screen at 21:9: the widened cull planes (cull 1) against none (cull 0) and twice as wide (cull 2).
SESSIONS += [
    dict(name="two-players-cull", config="two-players-cull-config", fresh_pak=True, wav=False, present_every=10, optin=True,
         args=["--skip-intro", "--hidden", "--aspect", "21:9", "--window", "1680x720", "--res-scale", "2", "--hud", "original"], scenarios=[
        ("two_players_cull", "two players at 21:9, paused: present captures with cull 1 / 0 / 2", [
            *_TWO_PLAYERS_TO_LEVEL,
            ("wait", 30),
            *_TWO_PLAYERS_PAUSE,
            ("keep_present", "cull_k1"),
            ("ctl", "cull 0"), ("wait", 15), ("keep_present", "cull_k0"),
            ("ctl", "cull 2"), ("wait", 15), ("keep_present", "cull_k2"),
            ("ctl", "cull 1"), ("wait", 15), ("keep_present", "cull_k1b"),
        ]),
    ]),
]

# Border crop (graphics setting `border`, src/border_crop.cpp): the shared tests/crop_sessions.py.
from crop_sessions import crop_sessions  # noqa: E402
SESSIONS += crop_sessions([("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
                           ("go", "A", "level_select", "tips_ready"), ("go", "A", "tips_ready", "in_level")],
                          pause=[("go", "START", "in_level", "pause")])
# Border crop in a two-player split screen at 16:9: each view's own inset scissor goes to the frame's edges too (crop_sessions.crop_two_players).
from crop_sessions import crop_two_players  # noqa: E402
SESSIONS.append(crop_two_players(_TWO_PLAYERS_TO_LEVEL, _TWO_PLAYERS_PAUSE))
# Level-start freeze (v0.2 queue item 3, tests/load_freeze.py): the course cycle's four starts with frame timestamps over each load.
# `lf-probe` (optin) runs in a visible window, the user's case; THPS_LF_SAMPLE=4 adds a `sample` of the host over each load phase.
from load_freeze import load_freeze_session  # noqa: E402
_LF = dict(
    to_select=[("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 0), ("go", "A", "main_menu", "career_menu"),
               ("menu", "career", 1), *TO_LEVEL_SELECT],
    courses=[[], [("press", "RIGHT"), ("wait", 20)], [("press", "RIGHT"), ("wait", 20)], [("press", "RIGHT"), ("wait", 20), ("press", "RIGHT"), ("wait", 20)]],
    phases=[("A", "career_goals"), ("A", "in_level")],
    end_run=[("go", "START", "in_level", "pause"), ("menu", "pause", 3), ("go", "A", "pause", "statistics"), ("go", "A", "statistics", "postrun_menu"),
             ("menu", "postrun", 2), ("go", "A", "postrun_menu", "level_select")],
)
SESSIONS += [load_freeze_session("lf-probe", **_LF, hidden=False, optin=True, limits={"composited": 1000.0, "game": 1000.0})]
# The suite's check (hidden window, the first three courses): the median over the three starts of the longest gap between game
# frames while the course loads stays under LF_GAME_MS (one preempted window on a busy machine does not fail it; a warning only
# when the machine is overloaded). Before the v0.2 fixes (ERZ decoder, native memset / memcpy) every start was over it.
LF_GAME_MS = 130.0   # 2026-10-18: 64-107 ms after the fixes (load 4-5), 120-222 ms before (load 9-11)
SESSIONS += [load_freeze_session("lf-check", **{**_LF, "courses": _LF["courses"][:3]}, limits={"game": 1000.0}, median=("game", LF_GAME_MS))]
# Draw distance in a two-player split screen (2026-10-21; optin, exploration): TWO PLAYERS > GRAFFITI as in `two-players`, with DD2P_RIGHTS
# RIGHT presses (pad 1's dpad) at the course select (the DD2P_AT-th selection press, counted from 0), then paused: x1 / x64 frames and
# dltraces as in dd-probe (DD_AB, DD_TRACE), then unpaused with the setting from DD_ARGS / DD_MODE, a ride of both players and the buffers.
def _dd2p_select():
    seq = [("vpress", "a"), ("vpress", "a"), ("vpress2", "a"), ("vpress", "a"), ("vpress2", "a"), ("vpress", "a"), ("vpress2", "a"), ("vpress", "a"), ("vpress2", "a")]
    at, n, out = int(_os.environ.get("DD2P_AT", "-1")), int(_os.environ.get("DD2P_RIGHTS", "0")), []
    for i, st in enumerate(seq):
        if i == at:
            out += [s for _ in range(n) for s in (("vpress", "dpright"), ("wait", 12))] + [("shot", "course_select")]
        out += [st, ("wait", 40 if i < len(seq) - 1 else 200)]
        if _os.environ.get("DD2P_SHOTS"): out.append(("shot", f"sel{i}"))
    return out
SESSIONS += [
    dict(name="dd-2p", config="dd-2p-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--unlock-levels", "--present-size", "960x540", "--aspect", "16:9", "--window", "1280x720",
               "--refresh", "60"] + _os.environ.get("DD_ARGS", "").split(),
         scenarios=[
        ("dd_2p", "draw distance in two-player split screen: paused frames and traces per factor, a ride, buffers", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"),
            ("vpad", "attach"), ("vpad2", "attach"),
            ("vpress", "leftshoulder"), ("vpress2", "leftshoulder"),
            ("log_n", r"Virtual Controller takes port 2", 1),
            ("menu", "main", 1),
            *_dd2p_select(),
            ("ctl_match", "inputstate", r"in3d=1"),
            ("shot", "in_level"), ("ctl", "dd"), ("ctl", "dd heap"),
            *_TWO_PLAYERS_PAUSE,
            *_DD_AB,
            ("ctl", "dd mode " + _os.environ.get("DD_MODE", "original")), ("ctl", "dd reset"),
            ("ctl", "vpad button start 1"), ("wait", 10), ("ctl", "vpad button start 0"), ("wait", 45),
            ("ctl", "ftime start"),
            ("ctl", "vpad axis lefty -32767"), ("ctl", "vpad2 axis lefty -32767"), ("wait", 150),
            *_DD_SHOT("ride1"),
            *[s for k in range(4) for s in (("ctl", f"vpad axis leftx {32767 if k % 2 else -32767}"), ("ctl", f"vpad2 axis leftx {-32767 if k % 2 else 32767}"),
                                            ("wait", 25), ("ctl", "vpad axis leftx 0"), ("ctl", "vpad2 axis leftx 0"), ("wait", 25))],
            *_DD_SHOT("ride2"),
            ("ctl", f"ftime stop {_DD_DIR}/ftime.csv"),
            ("ctl", "vpad axis lefty 0"), ("ctl", "vpad2 axis lefty 0"), ("wait", 20),
            ("ctl", "dd"), ("ctl", "stats"), ("ctl", "dd heap"),
        ]),
    ]),
]

# Draw distance's matrix pools (2026-10-22, the private development notes): with dd_buffers = bigger (the default) the game gets pools of
# 2048 matrices once at start-up and keeps its own cap (500) at `original`, so the setting takes effect at once, both ways; with
# --dd-buffers original the game's own pools (500) whatever the setting.
_DDB_TO_LEVEL = [("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT, ("press", "A"), ("wait", 600), ("press", "A"), ("wait", 300)]
SESSIONS += [
    dict(name="dd-buffers", config="dd-buffers-config", fresh_pak=True, wav=False,
         args=["--skip-intro", "--hidden", "--draw-distance", "original", "--dd-buffers", "bigger"], scenarios=[
        ("dd_buffers_now", "default buffers: pools of 2048 with the game's cap 500 at Original; Full raises the cap at once, Original puts it back", [
            *_DDB_TO_LEVEL,
            ("ctl_match", "dd heap", r"mtx_pool 2048 mtx_cap 500 "),
            ("ctl_match", "dd", r"buffers=bigger .* mtx_cap=500 "),
            ("ctl", "dd mode full"), ("wait", 30),
            ("ctl_match", "dd heap", r"mtx_pool 2048 mtx_cap 2048 "),
            ("ctl_match", "dd", r"mtx_cap=2048 "),
            ("ctl", "dd mode original"), ("wait", 30),
            ("ctl_match", "dd heap", r"mtx_pool 2048 mtx_cap 500 .* failed_calls 0 "),
        ]),
    ]),
    dict(name="dd-buffers-own", config="dd-buffers-own-config", fresh_pak=True, wav=False,
         args=["--skip-intro", "--hidden", "--draw-distance", "original", "--dd-buffers", "original"], scenarios=[
        ("dd_buffers_own", "--dd-buffers original: the game's own pools (500), at Original and at Full", [
            *_DDB_TO_LEVEL,
            ("ctl_match", "dd heap", r"mtx_pool 500 mtx_cap 500 "),
            ("ctl_match", "dd", r"buffers=original .* mtx_cap=500 "),
            ("ctl", "dd mode full"), ("wait", 30),
            ("ctl_match", "dd heap", r"mtx_pool 500 mtx_cap 500 "),
            ("ctl", "dd mode original"),
        ]),
    ]),
    # Opt-in demo: Downtown at Original, then Graphics > Draw Distance > Full in the menu in the middle of the run, a ride: the pool use goes past
    # the game's 500 with no restart (`dd`: mtx_hw > 500, mtx_capped=0). DD_ARGS: extra host args.
    dict(name="dd-switch", config="dd-switch-config", fresh_pak=True, wav=False, optin=True, requires="menu",
         fresh_files=["graphics.cfg"],
         args=["--skip-intro", "--hidden", "--unlock-levels", "--window", "1280x720", "--draw-distance", "original"] + _os.environ.get("DD_ARGS", "").split(), scenarios=[
        ("dd_switch", "switch Original -> Full in the menu mid-run: the matrix pool use passes 500 at once", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), ("menu", "main", 3), *TO_LEVEL_SELECT,
            *[s for _ in range(4) for s in (("press", "RIGHT"), ("wait", 12))],
            ("shot", "select"),
            ("press", "A"), ("wait", 600), ("press", "A"), ("wait", 300),
            ("shot", "in_level_original"),
            ("ctl", "dd reset"), ("wait", 60),
            ("ctl_match", "dd", r"mode=original .* mtx_cap=500 "),
            ("ui", "esc"), ("ui_state", "open=1"), ("ui", "tab 2"), ("ui", "click #lbl_dd_full"), ("log", r"draw distance: full"), ("ui", "esc"),
            ("ctl", "dd reset"),
            ("vpad", "attach"),
            ("ctl", "vpad axis lefty -32767"), ("wait", 150), ("ctl", "vpad axis lefty 0"), ("wait", 30),
            # pause -> END RUN -> RETRY: the course starts again (the game is not restarted); Downtown's start overview takes ~560 pool matrices at Full
            ("press", "START"), ("wait", 45), ("menu", "pause", 3), ("press", "A"), ("wait", 90), ("press", "A"), ("wait", 600), ("press", "A"), ("wait", 300),
            ("shot", "in_level_full"),
            ("ctl_match", "dd", r"mode=full .* mtx_hw=(50[1-9]|5[1-9]\d|[6-9]\d\d|1\d\d\d|20[0-4]\d) mtx_cap=2048 "),   # past the game's 500, no restart
            ("ctl_match", "dd", r"mtx_capped=0 "),
            ("ctl", "dd heap"),
        ]),
    ]),
]

import os as _os  # noqa: E402
# Frame pacing in a visible window (2026-10-23, the user's "stuttery" report; optin): the title left alone until the attract demo runs
# (frame times over PACE_DEMO frames), or with PACE_MODE=ride the first course (frame times over a 12 s ride). PACE_ARGS: host args (e.g.
# "--refresh 60" or "--refresh display"). Run it with THPS1_BINARY of the build to compare.
_PACE_RIDE = [("ctl", "vpad axis lefty -32767"),
              *[x for k in range(12) for x in (("ctl", f"vpad axis leftx {(-32767, 0, 32767, 0)[k % 4]}"), ("wait", 30))],
              ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0")]
SESSIONS += [
    dict(name="pace", config="pace-config", fresh_pak=True, wav=False, optin=True, fresh_files=["graphics.cfg"],
         args=["--skip-intro", "--window", "1280x720"] + _os.environ.get("PACE_ARGS", "").split(), scenarios=[
        ("pace", "frame pacing: attract demo and a ride, ftime in a visible window", [
            *([("wait_for", "title"), ("wait", int(_os.environ.get("PACE_IDLE", "600"))), ("shot", "demo"),
               ("ctl", "ftime start"), ("wait", int(_os.environ.get("PACE_DEMO", "600"))), ("ctl", "ftime stop"), ("shot", "demo_end")]
              if _os.environ.get("PACE_MODE", "demo") == "demo" else
              [*_HUD_TO_LEVEL, ("vpad", "attach"),
               ("ctl", "ftime start"), *_PACE_RIDE, ("ctl", "ftime stop"), ("shot", "ride")]),
            ("ctl", "dd"),
        ]),
    ]),
]
# The bigger matrix pools on a constrained heap (review 2026-10-26, finding 1): THPS_DD_HEAP_FREE makes the planning see a free list of the
# given blocks from the first pool request (at start-up), and both requests are taken from that view (`dd heap` view_fail counts one it
# could not have satisfied: the real allocator hangs there). 150,000 bytes hold the game's two 32,000-byte pools but not one bigger
# pool and a game's one: both stay the game's size and nothing fails (before the fix the first was enlarged and the second one's native
# size no longer fitted). 300,000 + 900,000: both bigger pools fit the first block (the second, the one later requests rely on, untouched).
SESSIONS += [
    dict(name="dd-heap-plan", config="dd-heap-plan-config", fresh_pak=True, wav=False, env={"THPS_DD_HEAP_FREE": "150000"},
         args=["--skip-intro", "--hidden", "--draw-distance", "full"], scenarios=[
        ("dd_heap_plan_tight", "a free list with room for the game's pools only: both the game's size, no request that would fail", [
            ("wait_for", "title"),
            ("log", r"draw distance: WARNING no room for a 131072-byte matrix pool 0"),
            ("ctl_match", "dd heap", r"mtx_pool 500 mtx_cap 500 .* failed_calls 0 .* view_fail 0"),
        ]),
    ]),
    dict(name="dd-heap-plan-room", config="dd-heap-plan-config", fresh_pak=True, wav=False, env={"THPS_DD_HEAP_FREE": "300000,900000"},
         args=["--skip-intro", "--hidden", "--draw-distance", "full"], scenarios=[
        ("dd_heap_plan_room", "room for both bigger pools in the first block: 2048 matrices, nothing fails", [
            ("wait_for", "title"),
            ("ctl_match", "dd heap", r"mtx_pool 2048 mtx_cap 2048 .* failed_calls 0 .* view_fail 0"),
        ]),
    ]),
]
