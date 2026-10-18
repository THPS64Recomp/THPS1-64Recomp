# THPS1 (N64, USA v1.1) data formats

Layouts, flags, algorithms and the code that reads them. Every claim names the
function (see [address-map.md](address-map.md)) that consumes the data. Labels: **[V]** verified by decoding every instance
we tried, or by reading the code; **[I]** inference. All values are big-endian. This page describes *how the data is arranged*;
the data itself is not reproduced. Observed value lists live in [../game-facts/](../game-facts/).

Prior art credited in [NOTICE](../../NOTICE.md): the PS1 versions of these files are described by the community (for example the
object record and face-flag names in the io_thps_scene Blender importer), and the N64 layouts here were re-derived from the
N64 code. Where a layout is the same as the PS1 one, we say "PS1 layout".

## 1. Conventions

- Angles: 4096 per turn. Positions and velocities: fixed point, 1.0 = 4096. Level geometry uses the PlayStation world unit;
  the N64 renders it scaled by 1/16.
- The PS1 axes are kept: **+Y is down**. A viewer needs `(x, -y, -z)` (a 180 degree turn about X) to get Y-up with the
  same handedness and triangle order.
- Our tools that read these formats are `decomp/common/thps_unpack.py` (code image) and `repack_check.py` (compression
  round trip). Tools that extract or convert assets are not part of this repository.

## 2. ERZ compression

"ERZ" is Rob Northen Computing's ProPack ("RNC") container with the three-byte magic changed. Everything compressed in the
ROM uses it: the 14 code chunks and the asset pieces. The decoders are handwritten MIPS in the boot segment
(`Erz_UnpackMethod1` at `0x80001330`, `Erz_UnpackMethod2` at `0x80000C40`, dispatcher `Erz_Unpack` at `0x80000B08`). [V]

| Offset | Field |
|---|---|
| 0x00 | `'E' 'R' 'Z'` and the method byte (1 or 2) |
| 0x04 | unpacked size |
| 0x08 | packed size (bytes after the 18-byte header) |
| 0x0C | CRC-16 of the unpacked data (CRC-16/ARC) |
| 0x0E | CRC-16 of the packed data |
| 0x10 | leeway: how far the output may overrun the input when unpacking in place |
| 0x11 | number of blocks in the bit stream |

- **Method 1** (Huffman and LZ77): the bit stream is read LSB-first from little-endian 16-bit words. Each block has three
  canonical Huffman tables (literal-run lengths, match distances, match lengths; a 5-bit symbol count, then a 4-bit code length
  per symbol) and a 16-bit item count. An item is a literal run (raw bytes taken straight from the input) followed, except
  for the last item, by a match (distance + 1, length + 2). Symbol values of 2 or more encode a number as the top bit plus
  (value - 1) extra bits. All 14 code chunks use method 1. [V]
- **Method 2**: no Huffman; bits are read MSB-first one at a time from bytes, literals and short offsets are whole bytes. Used
  by the nested audio pack. [V]
- Each stored CRC-16 is checked by the loader's equivalent; our decoder checks both, which is an oracle independent of our own
  code: a wrong decode cannot pass 14 chunk CRCs.
- **Recompression is reproducible**: the stock packer (lab313ru's rnc_propack_source) reproduces every piece identically
  once its look-ahead buffer (`0xFFFF - dictionary`) is enlarged (we use `0x20000`). Unpatched, 2 of the 14 code chunks differ,
  both with 40 KB zero runs whose run lengths are truncated at the buffer edge. Patched: 1,094 of 1,094 method-1 pieces are
  identical. Layout rule of the chunk table: spans are 4-aligned, the last chunk is unpadded, and the asset root is 2-aligned.

## 3. The asset tree

| Layer | Layout | Reader |
|---|---|---|
| Asset root | the ROM word at `0x13B10` (`0xB0061E26` gives ROM `0x61E26`), stored by the boot code to `gAssetRootRom` (`0x80011C2C`) | root object `0x800F566C`, set up at `0x800C02A4` |
| Container | `u32 count; u32 off[count + 1]`, offsets relative to the container start; entry *i* is `off[i]..off[i+1]` | `Archive_ReadDir` `0x8009B6F4`, `Archive_EntryOffset` `0x8009B988`, `Archive_LoadEntry` `0x8009B7D8` (size = delta, rounded up to even) |
| Pack | a top-level entry is a container of **16 KiB pieces**, each ERZ-packed or raw; the pieces concatenate to one logical stream and offsets inside the pack are stream offsets | stream object at archive +0xC: open `0x800B2AE4`, read and unpack `Rom_ReadUnpack` `0x800B2CF0` |
| Sub-archive | the same container format inside a stream entry | `Archive_LoadSubDir` `0x8009B898` |

The root holds **7 packs**:

| Pack | Role | Entries |
|---|---|---|
| 0 | `.psx` level and object files | 80, named by `gPsxNameTable` |
| 1 | `.trg` trigger and node graphs | 9, named by `gTrgNameTable` |
| 2 | geometry (N64 models) | 104 |
| 3 | texture records | 1,488 |
| 4 | full-screen bitmaps (CI8) | 228 |
| 5 | wave tables for libmus (raw, not a container) | - |
| 6 | audio data (nested ERZ, method 2) | 16 |

Packs 2 to 4 are opened through virtual calls in the initialiser at `0x800C0204`, so their root indexes are inferred from
content rather than from code. [I]

## 4. `.psx` entries (pack 0)

PS1 `.psx` files were split and endian-converted field by field (pairs of `u16` stay in place, so the PS1 magic reads
`0x00020004`). Each entry is a 4-part sub-archive:

| Part | Content | Reader |
|---|---|---|
| 0 | object list: `u32 n`, then n records of 36 bytes: `u32 flags; s32 x,y,z (20.12); s16 rx,ry,rz; u16 model; ...; name checksum at +28` (PS1 layout) | level loader `0x80037DC8` |
| 1 | model headers: `u32 n`, then n x 24 bytes: flags, `s32` radius (20.12), bounding-box pairs | the loader stores `&hdr[model]` in the object |
| 2 | the PS1 file minus geometry: header with `ptr_meta` and the object count, the object list again, tagged chunks (a palette and a block map), and the model name checksums | `PsxArchive_Load` `0x8008486C`, for `Spool_Continue` |
| 3 | `u32` index of this file's geometry entry in pack 2 (equal to the `.psx` index + 1) | `0x80037DC8` and the geometry cache `0x800B477C` |

The PS1 vertex, plane and face arrays are gone; N64 geometry lives in pack 2. **Placement** (`0x80037DC8`, per object): position
is the fixed-point triple divided by 4096; the model matrix is a scale of 1/16 plus a translation of position/16, clamped to
+-32000. A small fix-up table at `0x800D3EE8` (10 entries of `{psx, object, dy}`) adjusts one level's objects by a few units. [V]

## 5. Geometry (pack 2)

An entry holds `u32 n` models, each a 3-part sub-archive (built by `0x800B5CA0`):

| Part | Content |
|---|---|
| 0 | bounds: 8 floats (min xyz, max xyz, radius, one more) |
| 1 | group list: each group (one material) is itself a 3-part sub-archive |
| 2 | vertices: `u32 count; u32 0`, then count x the 16-byte F3DEX2 vertex: `s16 x,y,z; u16 0; s16 s,t (S10.5); u8 r,g,b,a` (pre-lit colours; 0x80 is about 1.0) |

**Group:** part 0 is a header `{u32 tex, u32 gflags, u32 constant}`: `gflags & 1` marks textured (then `tex` is a pack-3 index,
replaced by the texture-cache pointer at `0x800B6338`); `gflags & 0x8000` marks a special group copied raw and skipped by
collision (light or sprite quads); `gflags & 0x400` feeds the geometry mode. Part 1 is the packed triangle stream. Part 2 is
`u32 n` and n pairs `{u16 col_flags, u16 render_flags}` in stream triangle order.

**Packed stream** (sized by `0x800B68D0`, converted to F3DEX2 at load time by `0x800B695C`):

| First byte | Size | Meaning |
|---|---|---|
| `0x00` | 1 | end of list |
| `1xxxxxxx` | 2 | triangle: three 5-bit vertex-cache slots `a=(w>>10)&31, b=(w>>5)&31, c=w&31`; two in a row become one two-triangle command |
| `x01xxxxx` | 2 | load vertices: `n = w & 31` (0 means 32) into slots starting at `(w>>5)&31`; vertices are consumed sequentially across all groups of a model (`0x800B6758` patches the source address) |
| `x10xxxxx` | 2 | select matrix: the second byte is an index (skinned skaters use it) |
| `x11sssss` | 5 | set the texture coordinates of cache slot `s`: `s16 s, s16 t` |

Texture coordinates: the texture command is emitted with scale `0xFFFF`, so texel = st / 32; with no extra tile shift. [V]

**Collision uses the same data.** `M3dZone_LineToItem` (`0x8005DF8C`) walks a grid of `u16` object lists (`0xFFFF` terminated)
at level +0x30, then per object (`0x80084274`) and per model (`0x800837C8`), which walks the converted display list and tests
triangles using `col_flags`. A hit fills a face record where `face[0]` holds `render_flags` and `face[3]` holds
`col_flags << 16`, where `GetFaceFlags` (`0x8005CA0C`) reads them. [V]

### Face flags

`col_flags`:

| Bit | Meaning | Read at |
|---|---|---|
| 0x0001 | not collidable: always skipped | `0x80083CC4` |
| 0x0002 | trigger face: hit only by trigger queries | `0x80083CD0` |
| 0x0010 | camera collides (set by the camera's collision reaction) | `0x8005E00C` |
| 0x0020 | excluded unless a global is set (`DoPhysics`) | `0x8005DFE0` |
| 0x0040 | **vert** (`Face_Air`); line-of-sight queries exclude it. It sits on invisible walls above the coping, which hold the skater on the lip line; the ramp faces are ordinary skatable faces with steep normals | `GetFaceFlags` |
| 0x0080 | **not wall-ridable** | `GetFaceFlags` |
| 0x0100 | **not skatable** (a wall) | `GetFaceFlags` |
| 0x1E00 | terrain / sound type `(f & 0x1E00) >> 9` | `GetFaceFlags` |

`render_flags` are the PS1 face flags: 0x0001 textured, 0x0010 triangle, 0x0020 tiled, **0x0080 invisible**, 0x0800 gouraud.
Most untextured faces in a level carry 0x80 (invisible vert walls and triggers). Note that 0x0110 (camera-solid, not skatable)
faces are mostly vertical walls, not floors. [V]

## 6. Textures and bitmaps

**Texture record (pack 3)**, parsed by `0x800BA1B8` (loaded by `0x800BA768`):

| Offset | Field |
|---|---|
| 0x00 | `char name[32]` (`psxtxt_<PS1 checksum>` or a UI name) |
| 0x20 | `u16 w, h` |
| 0x24 | two bytes, unknown |
| 0x26 | `u8 fmt` (G_IM_FMT: 0 RGBA, 2 CI, 3 IA, 4 I) |
| 0x27 | `u8 bits` (4, 8, 16 or 32) |
| 0x28 | `u8 n0, n1`: a CI palette is `2*n0*(n1 or 1)` bytes; for non-CI, `n1` is the mip level count |
| 0x2A | `u16 data_size` |
| 0x2C | clamp/mirror flags, then words and bytes not yet decoded |
| 0x3F | pixel data, rows padded to 8 bytes (a TMEM line); then the palette (RGBA5551) and optional scroll or animation words |

1,482 of the 1,488 records decode; the other 6 are UI glyphs with an unusual header. [V]

**Bitmaps (pack 4):** each entry is a 3-part sub-archive: a header (`u32 0x00080410, u32 0x03000000, u32 w, u32 h, u32 ncolours,
u32 stride, u32 0`), an RGBA5551 palette and CI8 pixels. Title, loading and menu screens up to 640x240; all 228 decode. [V]

## 7. `.trg` trigger graphs (pack 1)

The PS1 header was word-swapped (the magic `_TRG` reads `GRT_`). `u32 version (2)`, `u32 count` (`Trig_LoadTRG` `0x8005F02C` reads
the count as a `u16` at +0xA), then `u32 offsets[count]` (file relative). Node bodies are `u16`-converted and identical to PS1:

- `u16 type` comes first.
- **Links** (`Trig_GetLinksPointer` `0x80061904`): at node+2 for types 2, 3, 6, 8 to 14, 1000 and 1001; node+4 for type 5;
  node+6 for type 1. Layout `u16 n; u16 node[n]`.
- **Position** (`Trig_GetPosition` `0x800617B8`): after the links, aligned down to 4 (`(node + 2n + 7) & ~3`, for types 3, 8, 10,
  11, 13, 1000, 1001): `s32 x,y,z` in world units (the game shifts them left by 12). Types 1 and 7 skip a name and a
  0xFF-terminated flag list first.
- **Rails** are type 10; `Rail_NextNode` (`0x80068F60`) follows links to type-10 nodes. `CRail` objects are built when a rail node
  receives a pulse. Rail nodes coincide with geometry vertices (median distance 1 to 2 units).
- **Restarts** are type 8: position as above, then `s16 rx, ry` (yaw, 4096 per turn) and `rz`, then a name (`Re_Start_*` for the
  main start, `Ho_*` for the HORSE spots).
- **Command points** are type 6: `u16 type, u16 n`, n links, then the node's own `u32` checksum at `(node + 4 + 2n + 3) & ~3`,
  then the `u16` command stream. The own checksum names the `.psx` object whose trigger faces (`col_flags` 0x02) fire the point.
- **Powerups** are type 5; the kind is the `u16` after the type.

**Command lists** (`ExecuteCommandList`, `0x800601A0`): the opcode is a `u16`, dispatched through the jump table at `0x8001C740`
indexed by opcode - 2 (201 entries, 67 live). `0xC9` is the gap command, `0xC8` sets the fade colour, `0xCA` the sky colour,
as in the PS1 game. [V]

## 8. Level records, powerups and gaps

**Level table** `0x800D5C1C`: 9 records of `0x78` bytes, indexed by the current level number (`0x800C0E20`).

| Offset | Field |
|---|---|
| +0x00 | level name (`char *`) |
| +0x04 | city (`char *`) |
| +0x08 | short name (`char *`) |
| +0x14 | trigger-graph name (`char *`) |
| +0x18 / +0x1C / +0x20 | gold / silver / bronze scores; non-zero only for competitions |
| +0x24 | level-select bitmap name |
| +0x30 / +0x34 | load / background bitmap names |
| +0x38 | the name used in the "5 %s" goal counter |
| +0x44 / +0x48 | High Score / Pro Score |
| +0x60 | read by `ExecuteCommand__6CBaddyUs` |

Readers include `Panel_GoalCounter`, `Panel_Tape`, `DisplayScore` and the competition-intro camera. The tape messages (S-K-A-T-E,
high score, pro score, the "5 objects" counter, hidden tape) are strings in `.rodata` reached through a pointer table at `0x800DDCAC`.

**Powerups (type 5).** Kinds: K = 4, S = 5, A = 6, E = 10, T = 15, secret tape = 16, bonuses of 100 / 200 / 500 points = 21 / 22 / 23.
Every street park has one of each letter and one tape; competition parks have none. [V]

**The "5 objects" goal.** Baddy command `0x42C0` (plus a `u16` argument), reached in the compare chain of
`ExecuteCommand__6CBaddyUs` at `0x80070FA8`, calls `Panel_GoalCounter`, which increments a counter in the skater object and prints
the counter. Two layouts: **direct** (each goal object is a type-1 baddy whose command list ends in `42C0 0000`) and **counter** (one
hidden baddy holds `4281 42C0` and the link graph pulses it; walking the links back reaches exactly five source nodes, either
type-6 command points or type-14 nodes that each hold an object-name checksum matching a `.psx` object record). [V]

**Gaps.** The gap table (section 4 of the address map) has 8-byte records `{s16 id, u16 points, char *name}`, ended by id -1,
the same layout as the PS1 `GapTricks` table. Ids 0 to 2 are generic; ids from 1000 are per level; ids of 10000 and up are
grind gaps; ids of 20000 and up are awarded as a grind trick. The command `0xC9` (a 4-byte-aligned end checksum, then an `s16`
gap type) fires a gap:
- firing a point completes the skater's pending gaps whose end checksum is the point's own checksum, then pushes
  `(end checksum, type)` if the checksum is not 0 (10 slots plus a count at skater +0x3D4);
- ground contact (physics state 0) clears all pending gaps;
- the rail state invalidates pending gaps with a type below 10000.

A park has between 16 and 140 gap commands (Burnside the fewest, Downtown the most). All gaps with their points are in
[../game-facts/thps1-gaps.md](../game-facts/thps1-gaps.md). [V]

## 9. Open questions

- The meaning of the group constant in the geometry header, and of `gflags` bits 0x400, 0x800, 0x1000 and 0x2000 (render modes).
- The special 0x8000 groups (lights and sprites); texture header bytes 0x24 and 0x25 and 0x2C to 0x3E; texture animation trailers.
- Skater models (the bone-matrix selection and the 19 bone objects) and animations: not located.
- Trigger node types other than 10 (cameras, cars) and the full command-list semantics.

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. Facts derived
from analysis of a retail cartridge dump. No game data is reproduced beyond names, addresses and individual values. See the README.
