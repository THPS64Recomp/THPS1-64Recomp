# THPS1 (N64, USA v1.1) address map

Where things are in *Tony Hawk's Pro Skater* for the Nintendo 64, USA v1.1 (SHA-1 `4900b6c92fb8df1765e91e891dccc525bb102fe1`).
Facts about the retail cartridge. Labels: **[V]** verified by a script or by reading the code that
uses the value; **[I]** inference. Other releases: [versions.md](versions.md). Data layouts: [formats.md](formats.md).
Mechanics: [mechanics.md](mechanics.md). Observed values: [../game-facts/](../game-facts/).

## 1. Identity and ROM map [V]

| Item | Value |
|---|---|
| Header name, code, revision | `TONY HAWK PRO SKATER`, `NTFE`, 1 |
| Size | 12 MiB (`0xC00000`) |
| Developer / origin | ported by Edge of Reality from Neversoft's PlayStation code (the engine is C++, GCC 2.x vtables) |
| Boot segment | ROM `0x1000` to `0x13B10`, loaded by the IPL3 to RDRAM `0x80000400` (IDO libultra plus Edge of Reality's loader) |
| Asset-root word | ROM `0x13B10`, a `0xB0xxxxxx` ROM address (`0xB0061E26`: the asset tree starts at ROM `0x61E26`); the chunk table follows at `0x13B14` |
| Code chunks | 14 compressed pieces of 64 KiB (stride `0x10000`) of the main image, method 1 of the ERZ format ([erz in formats.md](formats.md#2-erz-compression)) |
| Main image | inflated size `0xDF9A0`, loaded at `0x80016AC0`; SHA-1 of the inflated image is in `decomp/thps1/checksums/input.main.sha1` |
| Asset tree | after the code chunks: containers of 16 KiB ERZ pieces ([formats.md](formats.md#3-the-asset-tree)) |

## 2. RDRAM layout [V]

<!-- table-ok: RDRAM address ranges (layout facts) -->
| Range | Contents |
|---|---|
| `0x80000300`... | libultra globals (`osTvType` at `0x80000300`, `osRomBase` at `0x80000308`) |
| `0x80000400`-`0x80012F10` | boot segment: entry stub `0x80000400`, libultra, loader (`Boot_Main` `0x80000870`) |
| `0x80012F10`-`0x80016AC0` | **boot BSS**, cleared by the entry stub |
| `0x80016AC0`-`0x800223C0` | main image `.rodata` first part (C++ constructor list at `0x800223AC`, just before the code) |
| `0x800223C0`-`0x80097C40` | main `.text`, part 1 (game code, 1,706 functions) |
| `0x80097C40`-`0x8009B0A0` | **RSP microcode inside the CPU `.text`**: audio `n_aspMain` (`0x80097C40`, `0xC60` bytes), `rspboot` (`0x800988A0`, `0xD0`), graphics F3DEX.NoN fifo 2.08 (`0x80098970`, `0x1390`) and its xbus variant (`0x80099D00`, linked but never referenced) |
| `0x8009B0A0`-`0x800C0E20` | main `.text`, part 2 (libraries: libmus, n_audio, heap, archive code, scheduler) |
| `0x800C0E20`-`0x800F6460` | main `.data` |
| `0x800F6460`-`0x800FC8C5` | **game BSS**, cleared by `Boot_Main` |
| `GameEntry` = `0x800C0480` | the function `Boot_Main` calls after inflating the main image |

Both text ranges and the microcode carve-outs are in `decomp/common/games.toml` (row `thps1`). The microcode must be split out
of the CPU text for disassembly and recompilation. [V]

## 3. Packs and name tables [V]

The asset tree has seven packs ([formats.md](formats.md#3-the-asset-tree)): level objects (`.psx`, 80 entries), trigger graphs
(`.trg`, 9), geometry (104), textures (1,488 records), full-screen bitmaps (228), wave tables, audio (16). Name tables:
`gPsxNameTable` `0x800E8A58`, `gTrgNameTable` `0x800E8D18`. Archive objects: root `0x800F566C`, geometry archive `0x800ECFE0`,
texture archive `0x800EECA0`, trigger archive `0x800E8CE0`.

## 4. Key data structures [V unless marked]

<!-- table-ok: addresses and layouts of data structures (layout facts) -->
| Structure | Address | Layout |
|---|---|---|
| Level table | `0x800D5C1C` | 9 records of `0x78` bytes, indexed by the current level number ([formats.md](formats.md#8-level-records-powerups-and-gaps)) |
| Gap table | `0x800DA6D0` | 8-byte records `{s16 id, u16 points, char *name}`, terminated by id -1; 165 entries |
| Compiled trick table | `0x800D62F0` | `0x2C`-byte records: six diagonal-flip source records from `0x800D62F0`, then the 32 flip and grab slots from `0x800D63F8` (slot id times `0x2C`), then the specials from `0x800D6978`; layout and the full list in [game-facts/thps1-tricks.md](../game-facts/thps1-tricks.md) |
| Skater stats | `0x800D4D80` | 11 skaters, stride `0x154`; ollie, speed, air, balance at +0x18..+0x24; a selector byte at +0x28 chooses the diagonal flip set |
| Skater (CBruce) pointer | `0x800D61A8` | pointer to the player object; field offsets are N64 offsets |
| Grind names / points | `0x800D6F9C` / `0x800D6F7C` | 11 name pointers / 10 `u16` points, both indexed by grind type |
| Rail list | `0x800DC5C0` | `CRail` objects (`0x28` bytes) |
| Trigger offset list | `0x800DACB0` | `0x800E0000 - 0x5350`: file offsets of the trigger graph being loaded |
| Command-list jump table | `0x8001C740` | indexed by opcode - 2, 201 entries, 67 live |
| Physics timestep | `0x800F5668` | float, 1/30 s: game logic is fixed at 30 Hz |
| Frame counters | `0x800DE994` (`XFrames`, ticks at 60 Hz, +2 per game frame), `0x800DE7A0` (game state) | [I] for the exact role of the second |
| libmus F-command pointer table | `0x800ECB48` | data pointers to function entries (hidden function starts live behind them) |

Unit conventions: angles are 4096 per turn; positions and velocities are fixed point with 1.0 = 4096. [V]

## 5. Where the host hooks the game [V]

The recomp replaces a few places that touch hardware. Names are the symbol-file names; the hooks are listed in
`decomp/thps1/recomp-host/config/thps1.hooks.toml`.

| Place | Address | Why it is replaced |
|---|---|---|
| `Boot_PioCopy` | `0x80000AA0` | polls the cartridge interface; becomes a ROM-to-RDRAM copy |
| `Erz_UnpackMethod1`, `Erz_UnpackMethod2` | `0x80001330`, `0x80000C40` | handwritten decompressors with computed jumps; replaced by a native decoder |
| `osPiRawStartDma` | `0x80004770` | the game's asset DMA; the runtime's version is a stub, so it is renamed and hooked |
| `osSetEventMesg` | `0x80002E00` | the runtime ignores cartridge-DMA events; hooked to post them |
| `osAiGetStatus` | `0x80010A40` | audio pacing: reports "full" while the host queue holds more than 800 frames |
| `osContGetQuery` | (boot) | reports a pak present so the game's note list works |
| Main image sections | `0x80016AC0` | the entry wrapper re-registers the main sections at their real address (the runtime would place them by ROM offset) |

## 6. Key functions

Name source tags: `n64sym` = exact signature hit of a library function; `hand` = identified by reading the code; `ps1-name` =
the name equals the one used in the PS1 THPS2 demo decompilation (names only, no code used); `ps1-or-hand` = an evidence-tiered
entry in the symbol file that carries no source tag. Drop a class of names by filtering this column.

<!-- table-ok: function names and addresses of the address map; no values -->
| Address | Size | Name | Name source |
|---|---|---|---|
| `0x80000400` | `0x68` | `Boot_Entry` | hand |
| `0x80000870` | `0x230` | `Boot_Main` | hand |
| `0x80000AA0` | `0x68` | `Boot_PioCopy` | hand |
| `0x80000B08` | `0xA0` | `Erz_Unpack` | hand |
| `0x80000C40` | `0x6F0` | `Erz_UnpackMethod2` | hand |
| `0x80001330` | `0xC8` | `Erz_UnpackMethod1` | hand |
| `0x80002E00` | `0x68` | `osSetEventMesg` | n64sym |
| `0x800043D0` | `0x144` | `osCreateThread` | n64sym |
| `0x80004770` | `0xE0` | `osPiRawStartDma` | n64sym |
| `0x80004850` | `0xEC` | `osCartRomInit` | n64sym |
| `0x80007574` | `0x28` | `osContGetQuery` | n64sym |
| `0x8000B470` | `0x264` | `osPfsInitPak` | n64sym |
| `0x8000C900` | `0x1C4` | `osMotorInit` | n64sym |
| `0x80010A40` | `0xC` | `osAiGetStatus` | n64sym |
| `0x80010A50` | `0xA8` | `osAiSetNextBuffer` | n64sym |
| `0x80011010` | `0x20` | `osSpTaskYield` | n64sym |
| `0x80022E14` |  | `Mips_FixMul` | ps1-or-hand |
| `0x80039E60` |  | `SFX_PlayX` | ps1-name |
| `0x8004438C` |  | `DisplayScore` | ps1-name |
| `0x80044750` |  | `DisplayHolding` | ps1-name |
| `0x800453F0` |  | `Panel_Display` | ps1-name |
| `0x80045870` |  | `Panel_Tape` | ps1-name |
| `0x800459B8` |  | `Panel_GoalCounter` | ps1-name |
| `0x80045CDC` |  | `Land__10CPanelData` | ps1-name |
| `0x80045E38` |  | `Bail__10CPanelData` | ps1-name |
| `0x80046368` |  | `Panel_Land` | ps1-name |
| `0x8004C9E8` |  | `Trick_TakeOff__6CBruce` | ps1-name |
| `0x8004CACC` |  | `Trick_Trick__6CBrucePcii` | ps1-name |
| `0x8004CC10` |  | `Trick_Land__6CBruce` | ps1-name |
| `0x8004CED0` |  | `Trick_Bail__6CBruce` | ps1-name |
| `0x8004D048` |  | `Physics_StateTransition` | ps1-name |
| `0x8004E0B0` |  | `HandleStickToRail__6CBruce` | ps1-or-hand |
| `0x8004EBFC` |  | `HandleBailPerpendicular__6CBruceG7SVECTOR` | ps1-or-hand |
| `0x8004F13C` |  | `HandleTricksNew__6CBruce` | ps1-or-hand |
| `0x8004FD90` |  | `HandleSpin__6CBruce` | ps1-or-hand |
| `0x80050D68` |  | `DoOnRailPhysics__6CBruce` | ps1-name |
| `0x80052828` |  | `DoOnGroundPhysics__6CBruce` | ps1-name |
| `0x800543F8` |  | `DoInAirPhysics__6CBruce` | ps1-name |
| `0x80055570` |  | `DoFootPlantPhysics__6CBruce` | ps1-name |
| `0x80055D24` |  | `DoWallRidePhysics__6CBruce` | ps1-name |
| `0x80056B14` |  | `HandleJump__6CBruce` | ps1-name |
| `0x80057EAC` |  | `HandleKick__6CBruce` | ps1-or-hand |
| `0x80059BEC` |  | `DoPhysics__6CBruce` | ps1-name |
| `0x8005BDA8` |  | `ReadAnalogueInput__6CBruce` | ps1-or-hand |
| `0x8005CA0C` |  | `GetFaceFlags` | ps1-name |
| `0x8005CA90` |  | `M3dColij_LineToSphere` | ps1-or-hand |
| `0x8005DF8C` |  | `M3dZone_LineToItem` | ps1-or-hand |
| `0x8005EAB4` |  | `Mem_New` | ps1-name |
| `0x8005EDD0` |  | `Trig_ExecuteRestart` | ps1-name |
| `0x8005F02C` |  | `Trig_LoadTRG` | ps1-or-hand |
| `0x8005F2F8` |  | `Trig_CreateObject` | ps1-name |
| `0x800601A0` |  | `ExecuteCommandList` | ps1-name |
| `0x8006140C` |  | `Trig_ParseTRGFile` | ps1-name |
| `0x800617B8` |  | `Trig_GetPosition` | ps1-name |
| `0x80061904` |  | `Trig_GetLinksPointer` | ps1-name |
| `0x80061CC4` |  | `Trig_SetRestart` | ps1-name |
| `0x80061D7C` |  | `Trig_TriggerCommandPoint` | ps1-name |
| `0x8006278C` |  | `Spool_PSX` | ps1-name |
| `0x80062A90` |  | `Spool_Continue` | ps1-name |
| `0x80068988` |  | `Rail_Update` | ps1-name |
| `0x8006C7D4` |  | `Video_Playback` | ps1-or-hand |
| `0x8006CDAC` |  | `Video_Record` | ps1-or-hand |
| `0x8006EE1C` |  | `Mess_Message` | ps1-name |
| `0x80075694` |  | `MoveToDesiredPos__7CCameraUi` | ps1-or-hand |
| `0x80077584` |  | `CM_Normal__7CCamera` | ps1-or-hand |
| `0x80077A60` |  | `CM_CompetitionIntro__7CCamera` | ps1-or-hand |
| `0x8008486C` |  | `PsxArchive_Load` | hand |
| `0x800849B0` |  | `PsxArchive_Open` | hand |
| `0x80084B88` |  | `TrgArchive_Open` | hand |
| `0x8009B650` |  | `Archive_Open` | hand |
| `0x8009B6F4` |  | `Archive_ReadDir` | hand |
| `0x8009B7D8` |  | `Archive_LoadEntry` | hand |
| `0x8009B898` |  | `Archive_LoadSubDir` | hand |
| `0x8009B988` |  | `Archive_EntryOffset` | hand |
| `0x8009E6B4` |  | `Heap_Alloc` | hand |
| `0x8009FFD8` |  | `Thread_Create` | hand |
| `0x800A00F4` |  | `Thread_Entry` | hand |
| `0x800AB75C` | `0x30` | `MusStartSong` | n64sym |
| `0x800AC314` | `0x24` | `MusHandlePause` | n64sym |
| `0x800B2CF0` |  | `Rom_ReadUnpack` | hand |
| `0x800C0480` |  | `GameEntry` | hand |

Functions the symbol files do not name yet (working names): level-object loader `0x80037DC8`; geometry object builder `0x800B5CA0`,
stream sizer `0x800B68D0`, stream-to-display-list converter `0x800B695C`, vertex fix-up `0x800B6758`, geometry cache `0x800B477C`;
collision walkers `0x80084424` (grid), `0x80084274` (object), `0x800837C8` (model); texture parser `0x800BA1B8`, loader
`0x800BA768`, cache lookup `0x800BAB04`; scheduler create `0x800BC378`, scheduler thread `0x800BC57C`, retrace handler
`0x800BCB0C`, task dispatch and frame-buffer swap `0x800BD05C`, audio thread `0x800BB8F8`, game thread frame loop `0x800B3BC8`.

## 7. Libraries and runtime structure [V]

- **Graphics microcode:** F3DEX.NoN fifo 2.08. **Audio:** libmus (Software Creations) on the n_audio synthesizer; output through
  `osAiSetNextBuffer`.
- **Threads:** every game thread is made by `Thread_Create`, which allocates the stack from the main heap and always hands
  `osCreateThread` the trampoline `Thread_Entry`; the real entries are therefore indirect-call targets.
- **Heap:** the game's own allocator `gMainHeap` (`0x800EA110`), locked by an `OSMesgQueue` inside the heap object.
- **Peripherals:** Controller Pak (`osPfs*`, 17 initialisation sites) and Rumble Pak (`osMotor*`); no EEPROM; no TLB use; the
  standard libultra exception handler. No code overlays in THPS1.
- **C++:** static constructors listed from `0x800223AC`; GCC 2.x vtables (`{delta, index, pfn}`); 86 vtables with 304 slots,
  all pointing at function starts.

## 8. Quirks worth knowing

1. The last byte of the inflated main image differs between the loader's result and a fresh decode: a stale byte left in the
   staging buffer, also on hardware. The host reproduces the loader's result.
2. Alignment padding between objects was filled by the linker with **garbage words** (opcodes that a compiler never emits,
   stray jumps). Every non-zero gap before a 16-byte boundary marks an object boundary (87 seen). Disassemblers must treat
   such words as data.
3. PlayStation GTE (coprocessor 2) instructions survive in a few functions: three reads in one called function (patched to
   no-ops in the recompiler config) and three writes in an uncalled one (ignored).
4. The microcode is linked inside the CPU `.text`; see section 2.
5. Dead code: 821 functions have no caller, data pointer or address-forming reference; 272 are 8-byte empty stubs.
6. Function bounds come from the strong rules (jump targets, data pointers, section starts) and the padding rule; see
   [recomp.md](recomp.md#2-the-function-list).

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. Facts derived
from analysis of a retail cartridge dump (SHA-1 above). No game data is reproduced beyond names, addresses and individual values.
See the README.
