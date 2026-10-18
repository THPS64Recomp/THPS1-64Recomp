# THPS1 (N64) game mechanics

What the code does, in our words and formulas, with the addresses where each rule lives ([address-map.md](address-map.md)).
Values for individual tricks, gaps and so on are not tabulated here; they are in [../game-facts/](../game-facts/). Labels:
confidence **H** = the code path that uses the value was read in the N64 code; **M** = the value is an immediate in the
identified function but its exact use was not traced; **L** = a guess.

## Units and time

- Angles are fixed point, **4096 per turn**. Positions, velocities and gravity terms are integer fixed point with **1.0 = 4096**; the
  port converts with float constants 4096.0 and 1/4096 that sit at the start of `.rodata`.
- The physics step is the float `gPhysicsFrameTime` (`0x800F5668`) with value 1/30 s; no direct store to it was found. **Game
  logic steps at a fixed 30 Hz**: `0x80023838..0x80023868` computes a time scale of 256 (= 1.0) and its square every frame,
  and there is no measured-delta path. `XFrames` counts 60 Hz ticks (+2 per game frame), which is why the game's `PingPong` helper
  divides 60 by the frame rate.
- Field offsets of the skater object `CBruce` are N64 offsets.

## Scoring

<!-- table-ok: scoring constants with their addresses; mechanics, not an entity-keyed value table -->
| Rule | Where | Value / formula | Conf |
|---|---|---|---|
| 180-degree credit threshold | `Trick_Land` `0x8004CC10` (inlined `Get180s` at `0x8004CC48`) | the accumulated rotation `abs(tally) >= 1501` adds one more half spin, so about 132 degrees beyond the last full half counts; tally at skater +0x420, count at +0x424 | H |
| Spin points | `0x8004CCE4..0x8004CDA0`, jump table `0x8001B930`, names at `0x8001B8DC` (12-byte stride) | 50 points per half spin, up to 7 halves (1260 degrees); each step has its own trick name (the last is "MEGA"); the call is `Trick_Trick(this, 0x4A, name, points, 0)` | H |
| A lone half spin from state 2 | same | does not count | H |
| Special meter fill | `0x8004CE28..0x8004CEAC` | `meter += landed points`; at 3000 or more the special time is set to 750; while active, special time grows by `landed / 5`, capped at 750; both the meter and the time decay by **2 per frame** (`DoPhysics` `0x8005A1F4`), so a full 750 lasts 12.5 s | H |
| Bail rumble | `0x8004D024` | `Vibrate(8, 1, 150)` (time, motor, strength) | H |
| Wall ride trick | `Physics_StateTransition` `0x8004D048` | 500 points | M |
| Footplant | `DoFootPlantPhysics` `0x80055570` | 100 points | M |
| Handplant | `0x8004E0B0` (inlined in `HandleStickToRail`) | 1000 points (an immediate) | M |
| Nollie / fastplant | `HandleJump` `0x80056B14` (and `0x80057D5C`) | 200 / 250 points | M |

**Multiplier.** `landed = (sum of trick points) * (2*tricks + (n < 3 ? n : 2n - 2)) / 2`, computed in `Land__10CPanelData`
(`0x80045CDC`, `0x80045D48..0x80045D98`) where n is the number of tricks in the combo: +1 per trick, spins +0.5, +0.5, then +1 per
further half spin. `DisplayHolding` (`0x80044750`) prints it in half steps. There is no perfect/sloppy landing in THPS1.

**Nollie and fastplant.** When a jump fires and the last press that started from a neutral stick is exactly UP and younger than 0x14
XFrames, the nollie is awarded; if the press before it was also UP within 0x23 XFrames, the fastplant is awarded and vertical
velocity drops by `0x5000`. [H]

## Trick input

THPS1 has no trick script file: the trick definitions are compiled into `.data` ([game-facts/thps1-tricks.md](../game-facts/thps1-tricks.md)).
The input path is `HandleTricksNew` (`0x8004F13C`; the helpers `0x8004EF10` and `0x8004F030` read the same region and the latter
calls `Trick_Trick`). [H]

- **Pad mask:** UP 1, DOWN 2, LEFT 4, RIGHT 8 (stick axes at skater +0x98D and +0x98C, with a dead zone of 0x28; the D-pad bytes
  at +0xA0, +0xB0, +0x80, +0x90). The flip button is pad byte +0x10, the grab button +0x20.
- **Slot lookup:** a record's address is `0x800D63F8 + id * 0x2C`. For a flip, `id = mask` and the slot is tagged `0x2000`; for a
  grab, `id = 16 + mask`, tagged `0x4000`. A record whose animation id is `0x4E` is an empty slot. Ids 0, 3, 6, 7, 9 to 15 (flips) and
  16, 19, 23, 27 to 31 (grabs) are empty by default; ids from 32 (`0x800D6978`) are specials.
- **Diagonal flips** (mask 6, 9 and 10): the three slots are copied from six records at `0x800D62F0` by `DoPhysics`
  (`0x80059C94..0x8005A1C4`, jump table `0x8001BD18`), the case being a selector byte at +0x28 of the skater's stats record
  (`0x800D4D80 + skater * 0x154`). There are five cases; which skater uses which is in the game-facts page.
- **Pairing:** directions and buttons go into a 10-slot ring (values at +0x470/+0x498, times at +0x4C0/+0x4E8) and pair if within
  0x14 XFrames (10 game frames), in either order.
- **Record layout** (struct start = name pointer - 0xC): +0x00 key (specials: the skater key, direction history, mask and buttons
  in the low 20 bits; flag bits 20 to 26 select side effects such as negating the orientation, forcing a flip type or toggling
  stance), +0x04 animation id, +0x08 flags, +0x0C name pointer, +0x10 second-animation id, +0x14 and +0x18 hold counts, +0x1C points.

## Grinds

`StartGrind` is inlined in `HandleStickToRail` (`0x8004E95C..0x8004EA64`). The grind type follows from
`dot(rail direction at +0x7F8, board right at +0x8DC)`: if `abs(dot) >= 0xB33` (0.70) it is a boardslide, type 3 (back side) if the
dot is non-negative else type 2 (front side), swapped when the stance flag (+0x208, bit 2) is set. Otherwise the stick mask decides:
DOWN gives type 4 (5-0), DOWN with a side gives 7 (a lean of +-180), UP gives 5 (nosegrind), UP with a side gives 8, else 6 (50-50).
The type is stored at +0x9EC and `Trick_Trick(0x42 + type, name[type], points[type])` is called. [H]

## Physics

<!-- table-ok: physics constants with their addresses; mechanics, not an entity-keyed value table -->
| Rule | Where | Value | Conf |
|---|---|---|---|
| Rail gravity | `DoOnRailPhysics` `0x80050D68` | 13000 (`0x32C8`) | M |
| Ground in-plane gravity | `DoOnGroundPhysics` `0x80052828` | 6500 (`0x1964`), projected onto the floor plane; this drives speed on ramps | M |
| Ground constants | `0x80052828` | 3000, 82, 120, 160, 180, 200 and the float 8.0 (three times); roles not traced | M |
| Air physics | `DoInAirPhysics` `0x800543F8` | 3278, 3547, and the script-set `mAirGravity` / `mTrickGravity`; air gravity 13000 is set every frame at `0x80059C10` | M |
| Wall ride | `DoWallRidePhysics` `0x80055D24` | 9000, 116 | M |
| Ollie | `HandleJump` `0x80056B14` | 2500; float 3.0; the frame time | L |
| Fall-line scale on entering state 2 | `0x8004D048` | 13000 (about 3.17 in 4096 units) | M |

- **Speeds.** Push target `(s + 27 - 10) * 45 / 28` (`HandleKick` `0x80058180`), "too fast" threshold `(s + 49 - 10) * 45 / 28`
  (`DoPhysics` `0x8005AB98`), hard cap `(s + 50) * 45 / 28` (`LimitFinalSpeed`, inlined at `0x8005B898`), where `s` is the skater's
  speed stat. Skaters have four stats (ollie, speed, air, balance; table `0x800D4D80`); board stats are all zero and a special adds 3
  to every stat.
- **Air.** Spin lean maximum `0xA0000` (`HandleSpin` `0x8004FD90`).
- **Landing.** A sideways bail above 30 units per frame when more than 66.4 degrees off the travel line
  (`HandleBailPerpendicular` `0x8004EBFC`, test at `0x8004ED44`); mid-flip tolerance +-26.4 degrees.
- **Rails.** Grind entry boost `velocity += rail direction * (s + 5)` (`0x8004E7C8`); balance dynamics at `0x80051EEC..0x800522A4`, bail
  at `abs(lean) > 4000`; new-rail and same-rail clock at `0x8004E5E4`; rail floor speed in `DoOnRailPhysics` (`0x80051724`).
- **Unit scale** [M-L]: one game unit is about 1 cm; 4096 units = 1 world unit.

## Not yet traced

Speed limiting and braking inside `DoPhysics`, the push code in `DoOnGroundPhysics`, grind balance rates, the exact ollie impulse
(`mJumpStrength`).

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. Facts derived
from analysis of a retail cartridge dump. No game data is reproduced beyond names, addresses and individual values. See the README.
