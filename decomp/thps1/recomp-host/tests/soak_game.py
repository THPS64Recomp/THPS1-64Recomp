"""THPS1's flows for the soak test (the engine, monitor and summary are shared: decomp/common/host/tests/soak.py).

`play_launch(sk, life_end)` is what one launch of the host does once it is on the main menu: activities, each of which starts and ends on the main
menu, until `life_end`. `sk` is the Soak object (soak.py): sk.step(...) runs suite steps (tests/scenarios.py checkpoints and menus), sk.play() skates,
sk.phase() labels the frame-time windows, sk.seen() / sk.cp_now() look at the screen.

Courses are gated by tapes (SELECT COURSE: "5 MORE TAPES NEEDED TO UNLOCK") and, for two of them, medals; a new career has none, so a soak that wants
several levels sets the tape counters itself with a `poke` (the same kind of RDRAM probe the suite uses elsewhere): the career keeps one record of 20
bytes per course at CAREER_RECORDS, byte +8 of each is the tape count the level select shows ("x 05" after setting 5). The addresses are per code class
(found in Career_GiveTape of each class); nothing else of the game's memory is written. A course that stays locked (the two medal ones) is noticed
(the picture does not change after A) and skipped.
"""
from __future__ import annotations

import time

from run import StepFail   # the suite's runner (shared; soak.py imported it)

import harness as H

# code class -> address of the 10 course records (stride 20; byte +8 = tapes of that course)
CAREER_RECORDS = {"us11": 0x800DE9F4, "us10": 0x800DDD34}
CAREER_PTR = {"us11": 0x800DE7A8, "us10": 0x800DDAE8}   # pointer to the career object; +0x3E0 = the course being played (the game's own number)
TAPES_EACH = 40
# SELECT COURSE order (RIGHT moves down this list, wrapping). Downtown and Streets need medals, which this does not set.
LEVELS = ["Warehouse", "School", "Mall", "SkatePark", "Downtown", "DownhillJam", "Burnside", "Streets", "Unknown"]
# Career runs on the courses whose runs end the ordinary way (Warehouse, School, Mall); the others are competitions (heats, judges, a different pause menu) and are
# played in FREE SKATE only.
CAREER_LEVELS = [0, 1, 2]
FREE_LEVELS = [0, 1, 2, 3, 5, 6, 8]


def unlock_courses(sk):
    import run as R
    base = CAREER_RECORDS.get(R.VERSION.code_class)
    if base is None:
        return
    for i in range(10):
        a = base + i * 20 + 8
        w = sk.ses._peek(a)[0]
        sk.inst.cmd(f"poke {a:#x} {(w & 0x00FFFFFF) | (TAPES_EACH << 24):#x}")


_pause_ref = None


def pause_visible(sk) -> bool:
    """The PAUSED logo on screen, over any level's picture: a template match of the logo's bright pixels (the suite's `pause` checkpoint compares luma grids, which
    the background of other levels breaks)."""
    import run as R
    global _pause_ref
    if _pause_ref is None:
        _pause_ref = H.read_png(R.find_ref("pause"))
    img, _ = sk.ses.shot()
    return (img.w, img.h) == (_pause_ref.w, _pause_ref.h) and H.mask_score(img, _pause_ref, (0.25, 0.08, 0.75, 0.24), 150) >= 0.6


def open_pause(sk):
    for _ in range(4):
        if pause_visible(sk):
            return
        sk.press("START", 25)
        if pause_visible(sk):
            return
        sk.frames(30)
    raise StepFail("the pause menu did not open")


_ls_ref = None


def level_select_visible(sk) -> bool:
    """SELECT COURSE on screen whichever course the cursor is on: the gold "Select Course" lettering down the left edge is the same in every picture (the suite's
    `level_select` checkpoint compares the whole screen, with the Warehouse on it)."""
    import run as R
    global _ls_ref
    if _ls_ref is None:
        _ls_ref = H.read_png(R.find_ref("level_select"))
    img, _ = sk.ses.shot()
    return (img.w, img.h) == (_ls_ref.w, _ls_ref.h) and H.mask_score(img, _ls_ref, (0.02, 0.05, 0.13, 0.95), 120) >= 0.7


def game_level(sk):
    """The course the game says it is playing (career object +0x3E0), or None."""
    import run as R
    ptr = CAREER_PTR.get(R.VERSION.code_class)
    if ptr is None:
        return None
    p = sk.ses._peek(ptr)[0]
    return sk.ses._peek(p + 0x3E0)[0] if 0x80000000 <= p < 0x80800000 else None


def select_screen_changed(sk, before: "H.Image") -> bool:
    """Did the screen change since `before` (a locked course does nothing when A is pressed; an unlocked one starts loading)?"""
    after, _ = sk.ses.shot()
    return H.thumb_dist(H.thumb(before), H.thumb(after)) > 3.0


def to_level_select(sk, mode: str):
    """From the main menu to SELECT COURSE: mode "career" (a NEW GAME) or "free" (FREE SKATE)."""
    sk.phase("menu", f"{mode}_select")
    if mode == "career":
        sk.step(("menu", "main", 0))
        sk.press("A", 20)
        if sk.seen(["career_menu", "career_menu_loaded"], 30) is None:   # (CONTINUE GAME is enabled once a career is in RAM: its own checkpoint)
            raise StepFail("career menu not reached")
        sk.step(("menu", "career", 1))
    else:
        sk.step(("menu", "main", 3))
    for _ in range(12):
        sk.press("A", 15)
        if level_select_visible(sk):
            return
        cp = sk.seen(["skater_select", "board_select", "rumble_notice"], 8)
        if cp is None and level_select_visible(sk):
            return
    raise StepFail("course select not reached after 12 presses")


def start_level(sk, mode: str, k: int) -> str:
    """At SELECT COURSE: course k (an index of LEVELS), start the run; returns the name when the HUD shows. A locked course raises Locked."""
    unlock_courses(sk)
    cur = sk.ls_idx[mode]          # the game remembers the cursor per mode (career / free skate) for the life of the process
    for _ in range((k - cur) % len(LEVELS)):
        sk.press("RIGHT", 25)
    sk.ls_idx[mode] = k
    name = LEVELS[k]
    sk.frames(20)
    before, _ = sk.ses.shot()
    sk.phase("loading", name)
    sk.inst.press("A", 3, 3, timeout=60 * sk.ses.slow)
    sk.frames(60)
    if not select_screen_changed(sk, before):
        sk.phase("menu", f"{mode}_select")
        raise Locked(name)
    sk.step(("go", "A", None, "in_level", 120))   # goals screen / tips screen: A until the HUD shows
    gl = game_level(sk)
    name = f"L{gl}" if gl is not None else name     # the game's own number: the cursor bookkeeping above can drift
    sk.phase(mode, name)
    return name


class Locked(Exception):
    pass


def finish_career_run(sk):
    """From wherever a career run stands (still skating, paused, STATISTICS, a competition's judges / standings screens, the next heat) to the end-of-run menu: END RUN,
    then A through whatever comes. (Competition courses end with HEAT 1 OVER / JUDGES SCORES / COMPETITION STANDINGS and ask for A, not with STATISTICS.)"""
    for _ in range(30):
        cp = sk.cp_now(["postrun_menu", "statistics"])
        if cp == "postrun_menu":
            return
        if cp == "statistics":
            sk.press("A", 45)
        elif pause_visible(sk):
            sk.step(("menu", "pause", 3))
            sk.press("A", 60)
        elif sk.cp_now(["in_level"]):      # skating: END RUN
            open_pause(sk)
        else:                              # judges, standings, medals, loading: A continues
            sk.press("A", 45)
    raise StepFail("the end-of-run menu was not reached")


def retry(sk):
    mode, level = sk.ctx.get("phase"), sk.ctx.get("level")
    sk.phase("retry", level)
    open_pause(sk)
    sk.step(("menu", "pause", 1))
    sk.press("A", 30)
    sk.step(("wait_for", "in_level"))
    sk.phase(mode if mode != "retry" else "career", level)


def to_main_menu(sk):
    """Whatever screen it is: leave it for the main menu (QUIT / B presses, a bounded number of tries)."""
    cands = ["main_menu", "postrun_menu", "save_prompt", "enter_name", "save_ok", "level_select", "career_menu", "options_menu", "pause", "statistics", "in_level"]
    tries = 0
    for _ in range(16):
        cp = sk.cp_now(cands)
        if cp == "main_menu":
            sk.phase("menu", "main_menu")
            return
        if cp == "postrun_menu":
            sk.step(("menu", "postrun", 6))
            sk.press("A", 40)
        elif cp == "save_prompt":          # QUIT in a career asks "SAVE CAREER?": NO
            sk.press("DOWN", 10)
            sk.press("A", 40)
        elif cp == "in_level":
            open_pause(sk)
        elif cp == "pause" or pause_visible(sk):
            sk.step(("menu", "pause", 3))
            sk.press("A", 40)
        elif cp == "statistics":
            sk.press("A", 40)
        elif cp is None:                   # an unknown screen (a free-skate end-of-run menu, ARE YOU SURE?, a goals screen...): B a few times, then QUIT of the free-skate menu
            tries += 1
            if tries % 6:
                sk.press("B", 40)
            else:
                quit_free(sk)
        else:                              # level select, career menu, options, name entry: B goes back
            sk.press("B", 40)
    raise StepFail("could not get back to the main menu")


# -- activities ----------------------------------------------------------------------------------------------------------------------
def career_run(sk, k: int, secs: float, ending: str) -> str:
    to_level_select(sk, "career")
    try:
        start_level(sk, "career", k)
    except Locked as e:
        to_main_menu(sk)
        return f"locked {e}"
    res = sk.play(secs)
    if ending == "retry" and res == "ok":
        try:
            retry(sk)
            res = sk.play(min(secs, 25))
        except StepFail:                   # (a heat ended meanwhile: no pause menu)
            res = "retry-failed"
    finish_career_run(sk)
    sk.phase("menu", "postrun")
    to_main_menu(sk)
    return f"{ending}/{res}"


def free_run(sk, k: int, secs: float, ending: str) -> str:
    to_level_select(sk, "free")
    try:
        start_level(sk, "free", k)
    except Locked as e:
        to_main_menu(sk)
        return f"locked {e}"
    sk.play(secs)
    open_pause(sk)
    sk.step(("menu", "pause", 3))
    sk.press("A", 90)                 # END RUN in free skate: straight to RETRY / LEVEL SELECT / EQUIPMENT SELECT / QUIT
    sk.phase("menu", "postrun")
    if ending == "retry":             # RETRY is the first entry
        sk.press("A", 30)
        sk.step(("wait_for", "in_level"))
        sk.phase("free", LEVELS[k])
        sk.play(min(secs, 20))
        open_pause(sk)
        sk.step(("menu", "pause", 3))
        sk.press("A", 90)
    quit_free(sk)
    to_main_menu(sk)
    return ending


def quit_free(sk):
    """The free-skate end-of-run menu: QUIT is the last of four entries, and asks ARE YOU SURE? with NO under the cursor."""
    for _ in range(3):
        sk.press("DOWN", 8)
    sk.press("A", 40)
    sk.press("UP", 10)
    sk.press("A", 60)


def same_screen(sk, ref, timeout: float = 0.0) -> bool:
    """Does the screen look like `ref` (a frame grabbed earlier; mean RGB difference of the 16x12 thumbnails under 4: measured 16 for the controls page, 10 for sound levels, 5.7 for the LOAD DATA message, 0-3 for the list itself)? Used on OPTIONS, whose list the suite's
    checkpoints only know with the cursor on the first row, and whose sub-screens have gold controller buttons that fool the highlight detector."""
    end = time.monotonic() + timeout * sk.ses.slow
    while True:
        img, _ = sk.ses.shot()
        if H.thumb_dist(H.thumb(ref), H.thumb(img)) < 4.0:
            return True
        if time.monotonic() >= end:
            return False
        sk.frames(10)


def leave_screen(sk, ref) -> bool:
    """Get off a sub-screen of OPTIONS back to `ref`: B; else UP + A (the controls page's BACK TO OPTIONS is its last row, UP wraps to it); else 7 x DOWN + A."""
    for keys in (["B"], ["UP", "A"], ["DOWN"] * 7 + ["A"]):
        for k in keys:
            sk.press(k, 12)
        if same_screen(sk, ref, 6):
            return True
    return False


def menu_cycle(sk) -> str:
    """OPTIONS and its screens, EXTRAS, the in-game settings menu (Esc): open, every tab, close."""
    sk.phase("menu", "options")
    sk.step(("menu", "main", 4), ("go", "A", "main_menu", "options_menu"))
    for idx in (0, 2, 3, 4, 5):   # controls, sound levels, trick tips, score display, load data (PLAYER 2 CONTROLS: no way back by B / UP+A found, left out)
        sk.step(("menu", "options", idx))
        ref, _ = sk.ses.shot()
        sk.press("A", 45)
        if idx in (3, 4):                         # trick tips, score display: toggles on the list itself; put them back
            sk.press("A", 20)
            continue
        end = time.monotonic() + 20 * sk.ses.slow   # a screen of its own (LOAD DATA reads the pak first): wait for it, then leave it
        while same_screen(sk, ref) and time.monotonic() < end:
            sk.frames(15)
        if not same_screen(sk, ref):
            if not leave_screen(sk, ref):
                raise StepFail(f"options entry {idx} did not return to the options menu")
    sk.step(("menu", "options", 6), ("go", "A", "options_menu", "main_menu"))
    sk.phase("menu", "extras")
    sk.step(("menu", "main", 5))
    sk.press("A", 90)
    for _ in range(3):
        if sk.cp_now(["main_menu"]):
            break
        sk.press("B", 60)
    sk.step(("wait_for", "main_menu"))
    # the settings menu over the main menu: open, every tab, close
    sk.phase("menu", "settings")
    sk.inst.cmd("ui esc")
    sk.frames(20)
    for tab in range(6):
        sk.inst.cmd(f"ui tab {tab}")
        sk.frames(15)
    sk.inst.cmd("ui esc")
    sk.frames(20)
    sk.phase("menu", "main_menu")
    sk.step(("wait_for", "main_menu"))
    return "ok"


def play_launch(sk, life_end: float):
    sk.ls_idx = {"career": 0, "free": 0}
    only = set(filter(None, sk.a.only.split(",")))
    while time.monotonic() < life_end and time.monotonic() < sk.deadline:
        pick = sk.rng.random()
        secs = sk.rng.choice((25, 40, 60, 90))
        kind = "career" if pick < 0.45 else "freeskate" if pick < 0.80 else "menus"
        if only and kind not in only:
            kind = sk.rng.choice(sorted(only))
        k = sk.rng.choice(CAREER_LEVELS if kind == "career" else FREE_LEVELS)
        if kind == "career":
            ending = sk.rng.choice(("end", "retry", "end", "timeup"))
            if ending == "timeup":
                secs = 150   # the career's clock is 2:00; play() returns as soon as the statistics show
            sk.activity("career", lambda: career_run(sk, k, secs, ending), level=LEVELS[k], ending=ending)
        elif kind == "freeskate":
            ending = sk.rng.choice(("quit", "retry"))
            sk.activity("freeskate", lambda: free_run(sk, k, secs, ending), level=LEVELS[k], ending=ending)
        else:
            sk.activity("menus", lambda: menu_cycle(sk))
