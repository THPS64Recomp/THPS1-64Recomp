# THPS1 (USA v1.1): gaps

All 165 entries of the gap table at `0x800DA6D0`: 8-byte records `{s16 id, u16 points, char *name}`, ended by id -1. Layout and the rules for when a gap fires are in [../internals/formats.md](../internals/formats.md#8-level-records-powerups-and-gaps). The game stores each name inside square brackets; they are omitted below. Ids 0 to 2 are generic; from 1000 up the id block (the hundreds) groups gaps by area of a level. The level a gap belongs to is not tabulated.

| Id | Name | Points | Kind | Record |
|---|---|---|---|---|
| 0 | WIMPY GAP | 250 | generic | `800DA6D0` |
| 1 | GAP | 500 | generic | `800DA6D8` |
| 2 | PHAT GAP | 1000 | generic | `800DA6E0` |
| 1001 | TRANSFER | 200 | street/park gap | `800DA6E8` |
| 1005 | TAXI GAP | 600 | street/park gap | `800DA6F0` |
| 1006 | KICKER GAP | 100 | street/park gap | `800DA6F8` |
| 1007 | OVER THE PIPE | 300 | street/park gap | `800DA700` |
| 1008 | SECRET ROOM | 300 | street/park gap | `800DA708` |
| 1009 | FACEPLANT | 400 | street/park gap | `800DA710` |
| 1010 | ACID DROP | 1000 | street/park gap | `800DA718` |
| 1100 | KICKER 2 STREET | 100 | street/park gap | `800DA720` |
| 1101 | BS GAP | 500 | street/park gap | `800DA728` |
| 1102 | T 2 T GAP | 500 | street/park gap | `800DA730` |
| 1103 | SECRET TUNNEL ENTRANCE | 500 | street/park gap | `800DA738` |
| 1104 | TUNNEL GAP | 1000 | street/park gap | `800DA740` |
| 1105 | OVER THE TUNNEL | 2000 | street/park gap | `800DA748` |
| 1106 | CAR OLLIE | 100 | street/park gap | `800DA750` |
| 1107 | CHEESY DECK GAP | 50 | street/park gap | `800DA758` |
| 1108 | DECK GAP | 250 | street/park gap | `800DA760` |
| 1109 | BURLY DECK GAP | 2500 | street/park gap | `800DA768` |
| 1110 | TRUCK GAP | 250 | street/park gap | `800DA770` |
| 1111 | ROOF 2 ROOF | 2000 | street/park gap | `800DA778` |
| 1112 | SUCKY ROOM GAP | 1500 | street/park gap | `800DA780` |
| 1113 | BIG ASS | 1500 | street/park gap | `800DA788` |
| 1114 | GLASS GAP | 750 | street/park gap | `800DA790` |
| 1200 | WHOOP GAP | 1000 | street/park gap | `800DA798` |
| 1201 | WALL GAP | 100 | street/park gap | `800DA7A0` |
| 1202 | OVER THE BOX | 100 | street/park gap | `800DA7A8` |
| 1203 | OVER THE RAFTERS | 2000 | street/park gap | `800DA7B0` |
| 1204 | OVER THE PIPE | 700 | street/park gap | `800DA7B8` |
| 1205 | POOL HIP | 500 | street/park gap | `800DA7C0` |
| 1206 | POOL 2 WALKWAY | 700 | street/park gap | `800DA7C8` |
| 1207 | HP TRANSFER | 250 | street/park gap | `800DA7D0` |
| 1300 | BRIDGE GAP | 1000 | street/park gap | `800DA7D8` |
| 1301 | VERT WALL GAP | 700 | street/park gap | `800DA7E0` |
| 1302 | TWINKIE TRANSFER | 700 | street/park gap | `800DA7E8` |
| 1303 | OVER DA POOL | 800 | street/park gap | `800DA7F0` |
| 2000 | ROOF 2 ROOF GAP | 500 | street/park gap | `800DA7F8` |
| 2001 | SWIM TEAM GAP | 1000 | street/park gap | `800DA800` |
| 2002 | AWNING GAP | 125 | street/park gap | `800DA808` |
| 2003 | GARBAGE OLLIE | 50 | street/park gap | `800DA810` |
| 2004 | ROOF TO AWNING GAP | 750 | street/park gap | `800DA818` |
| 2005 | DITCH SLAP | 250 | street/park gap | `800DA820` |
| 2006 | OVER THE AIR CONDITIONER | 750 | street/park gap | `800DA828` |
| 2007 | OVER A FOOTBRIDGE | 1000 | street/park gap | `800DA830` |
| 2008 | PARK GAP | 500 | street/park gap | `800DA838` |
| 2009 | MINI GAP | 250 | street/park gap | `800DA840` |
| 2010 | PLANTER GAP | 100 | street/park gap | `800DA848` |
| 2011 | KICKER GAP | 100 | street/park gap | `800DA850` |
| 2300 | OVER A 16 STAIR SET | 250 | street/park gap | `800DA858` |
| 2301 | OVER A HUGE 32 STAIR GAP | 2000 | street/park gap | `800DA860` |
| 2302 |  | 500 | street/park gap | `800DA868` |
| 2303 | SKATER ESCALATOR GAP | 500 | street/park gap | `800DA870` |
| 2304 | 32 STEPS OFF A MEZZANINE | 2500 | street/park gap | `800DA878` |
| 2305 | THE FLYING LEAP | 100 | street/park gap | `800DA880` |
| 2306 | PLANTER GAP | 100 | street/park gap | `800DA888` |
| 2307 | RAMP GAP | 250 | street/park gap | `800DA890` |
| 2308 | GOING UP GAP | 250 | street/park gap | `800DA898` |
| 2309 | GOING DOWN GAP | 250 | street/park gap | `800DA8A0` |
| 2310 | FOUNTAIN GAP | 250 | street/park gap | `800DA8A8` |
| 2600 | RAGING GORGE GAP | 250 | street/park gap | `800DA8B0` |
| 2602 | HUGE WATER HAZARD GAP | 1000 | street/park gap | `800DA8B8` |
| 2603 | 50 FEET | 50 | street/park gap | `800DA8C0` |
| 2604 | 100 FEET | 100 | street/park gap | `800DA8C8` |
| 2605 | 150 FEET | 150 | street/park gap | `800DA8D0` |
| 2606 | 200 FEET | 200 | street/park gap | `800DA8D8` |
| 2607 | 250 FEET | 250 | street/park gap | `800DA8E0` |
| 2609 | SMALL WATER HAZARD GAP | 250 | street/park gap | `800DA8E8` |
| 2610 | BIG WATER HAZARD GAP | 500 | street/park gap | `800DA8F0` |
| 2611 | 25 FEET | 25 | street/park gap | `800DA8F8` |
| 2612 | 75 FEET | 75 | street/park gap | `800DA900` |
| 2613 | 125 FEET | 125 | street/park gap | `800DA908` |
| 2614 | 175 FEET | 175 | street/park gap | `800DA910` |
| 2615 | 225 FEET | 225 | street/park gap | `800DA918` |
| 3000 | RAMP 2 RAMP | 250 | street/park gap | `800DA920` |
| 3001 | TUNNEL GAP | 500 | street/park gap | `800DA928` |
| 3003 | LOW DECK GAP | 500 | street/park gap | `800DA930` |
| 3004 | HIGH DECK GAP | 1000 | street/park gap | `800DA938` |
| 3005 | DECK GAP | 1500 | street/park gap | `800DA940` |
| 3300 | PORCH GAP | 250 | street/park gap | `800DA948` |
| 3301 | PORCH GAP | 500 | street/park gap | `800DA950` |
| 3302 | LOMBARD GAP | 5000 | street/park gap | `800DA958` |
| 3303 | THE GONZ GAP | 500 | street/park gap | `800DA960` |
| 3304 | PAGODA GAP | 1000 | street/park gap | `800DA968` |
| 3305 | OVER THE SEVEN | 100 | street/park gap | `800DA970` |
| 3306 | HUBBA GAP | 750 | street/park gap | `800DA978` |
| 3307 | STREET GAP | 250 | street/park gap | `800DA980` |
| 3308 | STREET GAP | 500 | street/park gap | `800DA988` |
| 3309 | SPANKY GAP | 1000 | street/park gap | `800DA990` |
| 3310 | C BLOCK GAP | 500 | street/park gap | `800DA998` |
| 3311 | PLANTER GAP | 500 | street/park gap | `800DA9A0` |
| 3312 | FOUNTAIN GAP | 750 | street/park gap | `800DA9A8` |
| 3313 | SPINE GAP | 1000 | street/park gap | `800DA9B0` |
| 3314 | RAMP 2 RAMP | 500 | street/park gap | `800DA9B8` |
| 3315 | RAMP 2 RAMP | 750 | street/park gap | `800DA9C0` |
| 3316 | OVERSIZED 8 SET | 500 | street/park gap | `800DA9C8` |
| 3317 | ACID DROP-IN | 1000 | street/park gap | `800DA9D0` |
| 3318 | FOUNTAIN GAP | 250 | street/park gap | `800DA9D8` |
| 3319 | PORCH GAP | 750 | street/park gap | `800DA9E0` |
| 3320 | KICKER GAP | 500 | street/park gap | `800DA9E8` |
| 3321 | PAGODA HOP | 500 | street/park gap | `800DA9F0` |
| 3322 | PAGODA HOP | 750 | street/park gap | `800DA9F8` |
| 11000 | CHANNEL GAP | 250 | grind gap | `800DAA00` |
| 11001 | KICKER 2 LEDGE | 200 | grind gap | `800DAA08` |
| 11002 | GAP | 1000 | grind gap | `800DAA10` |
| 11100 | FREAKIN POOL GRIND | 100 | grind gap | `800DAA18` |
| 11101 | GAP | 100 | grind gap | `800DAA20` |
| 11102 | GAP | 100 | grind gap | `800DAA28` |
| 11200 | ROLL IN CHANNEL GAP | 1000 | grind gap | `800DAA30` |
| 11201 | CHANNEL GAP | 500 | grind gap | `800DAA38` |
| 12000 | HALL PASS GAP | 1000 | grind gap | `800DAA40` |
| 12001 | GAP | 1000 | grind gap | `800DAA48` |
| 12002 | GAP | 1000 | grind gap | `800DAA50` |
| 13000 | GAP | 1000 | grind gap | `800DAA58` |
| 13001 | GAP | 1000 | grind gap | `800DAA60` |
| 13002 | GAP | 1000 | grind gap | `800DAA68` |
| 21000 | BIG RAIL | 200 | awarded as a grind trick | `800DAA70` |
| 21001 | DECK 2 RAIL | 300 | awarded as a grind trick | `800DAA78` |
| 21002 | TAXI 2 LEDGE | 500 | awarded as a grind trick | `800DAA80` |
| 21003 | TAXI 2 RAIL | 1000 | awarded as a grind trick | `800DAA88` |
| 21004 | KICKER 2 LEDGE | 200 | awarded as a grind trick | `800DAA90` |
| 21005 | MONSTER GRIND | 500 | awarded as a grind trick | `800DAA98` |
| 21006 | HIGH RAIL | 200 | awarded as a grind trick | `800DAAA0` |
| 21007 | HOLY COW | 3000 | awarded as a grind trick | `800DAAA8` |
| 21008 | TRANSITION GRIND | 400 | awarded as a grind trick | `800DAAB0` |
| 21200 | KICKER 2 EDGE | 100 | awarded as a grind trick | `800DAAB8` |
| 21201 | BS GRIND | 200 | awarded as a grind trick | `800DAAC0` |
| 21202 | RAIL 2 RAIL TRANSFER | 750 | awarded as a grind trick | `800DAAC8` |
| 21203 | BILLBOARD GRIND | 500 | awarded as a grind trick | `800DAAD0` |
| 21204 | DIRTY RAIL | 3000 | awarded as a grind trick | `800DAAD8` |
| 21205 | DEATH GRIND | 2000 | awarded as a grind trick | `800DAAE0` |
| 21300 | TRIPLE RAIL | 1000 | awarded as a grind trick | `800DAAE8` |
| 21301 | BRIDGE GRIND | 800 | awarded as a grind trick | `800DAAF0` |
| 21302 | HAWK BRIDGE GRIND | 1000 | awarded as a grind trick | `800DAAF8` |
| 21400 | RAFTER RAIL | 1000 | awarded as a grind trick | `800DAB00` |
| 21401 | PIPE 2 BOX GRIND | 1000 | awarded as a grind trick | `800DAB08` |
| 21402 | LIGHT GRIND | 500 | awarded as a grind trick | `800DAB10` |
| 21403 | WALKWAY RAIL TRANS | 700 | awarded as a grind trick | `800DAB18` |
| 21404 | POOL RAIL TRANS | 1000 | awarded as a grind trick | `800DAB20` |
| 21500 | ET GRIND | 1000 | awarded as a grind trick | `800DAB28` |
| 21501 | BHOUSE RAIL | 1000 | awarded as a grind trick | `800DAB30` |
| 21502 | POOL GRIND | 2000 | awarded as a grind trick | `800DAB38` |
| 21503 | DECK GRIND | 800 | awarded as a grind trick | `800DAB40` |
| 21504 | MB EMERSON GRIND | 2000 | awarded as a grind trick | `800DAB48` |
| 22000 | DUMPSTER RAIL GAP | 250 | awarded as a grind trick | `800DAB50` |
| 22001 | PLAYGROUND RAIL | 500 | awarded as a grind trick | `800DAB58` |
| 22002 | RAIL TO RAIL TRANSFER | 750 | awarded as a grind trick | `800DAB60` |
| 22003 | HUGE RAIL | 1000 | awarded as a grind trick | `800DAB68` |
| 22004 | BIG DADDY RAIL | 2500 | awarded as a grind trick | `800DAB70` |
| 22005 | FUNBOX TO RAIL TRANSFER | 250 | awarded as a grind trick | `800DAB78` |
| 22006 | FUNBOX TO TABLE TRANSFER | 500 | awarded as a grind trick | `800DAB80` |
| 22007 | GIMME GAP | 50 | awarded as a grind trick | `800DAB88` |
| 22008 | HANDICAP RAMP RAIL | 500 | awarded as a grind trick | `800DAB90` |
| 22300 | COFFEE GRIND | 1000 | awarded as a grind trick | `800DAB98` |
| 22301 | FOR THE WHOLE ATRIUM | 500 | awarded as a grind trick | `800DABA0` |
| 22302 | RAIL COMBO | 500 | awarded as a grind trick | `800DABA8` |
| 22601 | NEVERSOFT ELEC CO GAP | 1500 | awarded as a grind trick | `800DABB0` |
| 23000 | DOWN THE SPIRAL | 2000 | awarded as a grind trick | `800DABB8` |
| 23001 | LOMBARD LEDGE | 250 | awarded as a grind trick | `800DABC0` |
| 23002 | HUBBA LEDGE | 500 | awarded as a grind trick | `800DABC8` |
| 23003 | HOOK RAIL | 750 | awarded as a grind trick | `800DABD0` |
| 23004 | RAIL 2 RAIL | 500 | awarded as a grind trick | `800DABD8` |
| 23005 | BACKWOODS LEDGE | 250 | awarded as a grind trick | `800DABE0` |
| 23006 | BENDY'S LIP | 500 | awarded as a grind trick | `800DABE8` |
| 23007 | ARE YOU KIDDING? | 3000 | awarded as a grind trick | `800DABF0` |

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. Observed values
from analysis of a retail cartridge dump (USA v1.1, SHA-1 `4900b6c92fb8df1765e91e891dccc525bb102fe1`), recorded as facts about
the game for identification and commentary, not as a reproduction of its data tables. Rights in the game remain with their
owners. Corrections and removal requests: see the README.
