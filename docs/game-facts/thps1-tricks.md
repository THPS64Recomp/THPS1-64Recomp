# THPS1 (USA v1.1): tricks, grinds, spins and skaters

Observed values, in our arrangement. The layout, the input decoding and the meaning of the fields are in [../internals/mechanics.md](../internals/mechanics.md#trick-input); addresses are in the [address map](../internals/address-map.md). Source of truth is the game; check any value on your own copy.

**How the table works.** The trick definitions are compiled into `.data` as `0x2C`-byte records. A flip or grab is looked up by its direction mask (UP 1, DOWN 2, LEFT 4, RIGHT 8) at `0x800D63F8 + id * 0x2C` (flips use `id = mask`, grabs `id = 16 + mask`); the three diagonal flip slots are filled at run time from six source records at `0x800D62F0`, chosen per skater. Points are the **base points** of a trick; the combo multiplier is applied on landing. The record address is the start of the `0x2C`-byte record.

## Flips and grabs by direction

Hold the stated direction and press the flip button (flips) or the grab button (grabs). Slots not listed hold no trick.

| Direction | Flip trick | Points | Record | Grab trick | Points | Record |
|---|---|---|---|---|---|---|
| UP | 360 SHOVE IT | 250 | `800D6424` | JAPAN AIR | 350 | `800D66E4` |
| DOWN | IMPOSSIBLE | 250 | `800D6450` | TAILGRAB | 300 | `800D6710` |
| LEFT | KICKFLIP | 100 | `800D64A8` | METHOD | 300 | `800D6768` |
| RIGHT | HEELFLIP | 100 | `800D6558` | INDY NOSEBONE | 300 | `800D6818` |
| UP+LEFT | KICKFLIP TO INDY | 500 | `800D64D4` | MADONNA | 500 | `800D6794` |
| DOWN+LEFT | per skater (below) | | | STALEFISH | 300 | `800D67C0` |
| UP+RIGHT | per skater (below) | | | ROCKET AIR | 350 | `800D6844` |
| DOWN+RIGHT | per skater (below) | | | BENIHANA | 400 | `800D6870` |

Empty slots (animation id `0x4E`): flips 0, 3, 7, 11 to 15 and diagonal slots before they are filled; grabs 16, 19, 23, 27 to 31.

## The diagonal flips, per skater

The three diagonal flip slots (DOWN+LEFT, UP+RIGHT, DOWN+RIGHT) are filled from six source records, by a selector byte in the skater's stats record (`0x800D4D80 + skater * 0x154 + 0x28`).

| Source record | Trick | Points | Record |
|---|---|---|---|
| 0 | VARIAL | 800 | `800D62F0` |
| 1 | FINGER FLIP | 500 | `800D631C` |
| 2 | FRONT FOOT IMPOSSIBLE | 600 | `800D6348` |
| 3 | SEX CHANGE | 500 | `800D6374` |
| 4 | HARDFLIP | 300 | `800D63A0` |
| 5 | 360 FLIP | 300 | `800D63CC` |

| Case | Skaters | DOWN+LEFT | UP+RIGHT | DOWN+RIGHT |
|---|---|---|---|---|
| 0 | Hawk, Lasek | VARIAL | FINGER FLIP | FRONT FOOT IMPOSSIBLE |
| 1 | Rowley, Muska, Campbell, Reynolds, Thomas, Steamer | SEX CHANGE | HARDFLIP | 360 FLIP |
| 2 | Officer Dick | SEX CHANGE | VARIAL | FRONT FOOT IMPOSSIBLE |
| 3 | Glifberg | VARIAL | FINGER FLIP | 360 FLIP |
| 4 | Burnquist | VARIAL | FINGER FLIP | 360 FLIP |

## Specials

34 special-trick records follow the slots, from `0x800D6978` (names in braces). Their inputs are encoded in each record's key field (the skater, a direction history, a mask and buttons) and are not tabulated here. Several tricks appear more than once: the table holds one copy per group of skaters. Base points in the second column.

| # | Special | Points | Record |
|---|---|---|---|
| 1 | {THE 900} | 8000 | `800D6978` |
| 2 | {KICKFLIP MCTWIST} | 4000 | `800D69A4` |
| 3 | {540 BOARD VARIAL} | 2000 | `800D69D0` |
| 4 | {360 FLIP TO MUTE} | 1500 | `800D69FC` |
| 5 | {KICKFLIP MCTWIST} | 4000 | `800D6A28` |
| 6 | {FINGERFLIP AIRWALK} | 2000 | `800D6A54` |
| 7 | {VARIAL HEELFLIP JUDO} | 2500 | `800D6A80` |
| 8 | {BACKFLIP} | 4000 | `800D6AAC` |
| 9 | {ONE FOOTED SMITH} | 750 | `800D6AD8` |
| 10 | {BURNTWIST} | 5000 | `800D6B04` |
| 11 | {KICKFLIP MCTWIST} | 4000 | `800D6B30` |
| 12 | {CHRIST AIR} | 2000 | `800D6B5C` |
| 13 | {FRONT-BACK KICKFLIP} | 1500 | `800D6B88` |
| 14 | {FRONTFLIP} | 4000 | `800D6BB4` |
| 15 | {ONE FOOT 5-0 THUMPIN} | 750 | `800D6BE0` |
| 16 | {360 SHOVE IT REWIND} | 1500 | `800D6C0C` |
| 17 | {BACKFLIP} | 4000 | `800D6C38` |
| 18 | {DOUBLE HARDFLIP} | 1500 | `800D6C64` |
| 19 | {DARKSLIDE} | 750 | `800D6C90` |
| 20 | {FRONTFLIP} | 4000 | `800D6CBC` |
| 21 | {CASPER SLIDE} | 750 | `800D6CE8` |
| 22 | {KICKFLIP UNDERFLIP} | 1500 | `800D6D14` |
| 23 | {BACKFLIP} | 4000 | `800D6D40` |
| 24 | {HEELFLIP TO BLUNTSLIDE} | 750 | `800D6D6C` |
| 25 | {TRIPLE KICKFLIP} | 1500 | `800D6D98` |
| 26 | {FRONTFLIP} | 4000 | `800D6DC4` |
| 27 | {ONE FOOTED NOSEGRIND} | 750 | `800D6DF0` |
| 28 | {540 FLIP} | 1500 | `800D6E1C` |
| 29 | {BACKFLIP} | 4000 | `800D6E48` |
| 30 | {PRIMO GRIND} | 750 | `800D6E74` |
| 31 | {JUDO MADONNA} | 1500 | `800D6EA0` |
| 32 | {YEEEEHAW FRONTFLIP} | 4000 | `800D6ECC` |
| 33 | {ASSUME THE POSITION} | 1500 | `800D6EF8` |
| 34 | {NECKBREAK GRIND} | 750 | `800D6F24` |

## Spins

Rotation adds 50 points per half spin (see the mechanics page), with these names for 1 to 7 halves: 180 OLLIE, 360 OLLIE, 540 OLLIE, 720 OLLIE, 900 OLLIE, 1080 OLLIE, MEGA OLLIE.

## Grind types

The grind type (see the mechanics page for how it is chosen) indexes a table of 11 names at `0x800D6F9C` and 10 base point values at `0x800D6F7C`. Types 0, 1, 9 and 10 are never stored by the grind-start code (they are reached through the special-record path).

| Type | Name | Base points |
|---|---|---|
| 0 | BALANCED SLIDE | 200 |
| 1 | INTO BACKSLIDE | 250 |
| 2 | FS BOARDSLIDE | 100 |
| 3 | BS BOARDSLIDE | 100 |
| 4 | 5-0 GRIND | 125 |
| 5 | NOSEGRIND | 125 |
| 6 | 50 50 GRIND | 100 |
| 7 | SMITH GRIND | 150 |
| 8 | CROOKED GRIND | 150 |
| 9 | NOSESLIDE | 250 |
| 10 | TAILSLIDE |  |

## Skaters

The stats table at `0x800D4D80` (11 records of `0x154` bytes). The four values (small integers) are read at +0x18, +0x1C, +0x20 and +0x24.

| # | Skater | Ollie | Speed | Air | Balance | Diagonal-flip case |
|---|---|---|---|---|---|---|
| 0 | Hawk | 3 | 7 | 7 | 4 | 0 |
| 1 | Burnquist | 4 | 6 | 6 | 4 | 4 |
| 2 | Rowley | 7 | 5 | 3 | 6 | 1 |
| 3 | Lasek | 5 | 7 | 6 | 3 | 0 |
| 4 | Muska | 6 | 4 | 4 | 7 | 1 |
| 5 | Campbell | 7 | 4 | 4 | 6 | 1 |
| 6 | Reynolds | 6 | 5 | 3 | 7 | 1 |
| 7 | Glifberg | 4 | 7 | 7 | 3 | 3 |
| 8 | Thomas | 5 | 5 | 4 | 7 | 1 |
| 9 | Steamer | 6 | 4 | 5 | 6 | 1 |
| 10 | Officer Dick | 5 | 5 | 5 | 5 | 2 |

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. Observed values
from analysis of a retail cartridge dump (USA v1.1, SHA-1 `4900b6c92fb8df1765e91e891dccc525bb102fe1`), recorded as facts about
the game for identification and commentary, not as a reproduction of its data tables. Rights in the game remain with their
owners. Corrections and removal requests: see the README.
