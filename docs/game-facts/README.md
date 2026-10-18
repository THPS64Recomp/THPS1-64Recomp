# Game facts: observed values

Observed values from the USA v1.1 cartridge, written as **facts about the game** (names, base points, inputs, slots, ids), in our
own arrangement: grouped by meaning, with the columns explained and the raw, unexplained columns (animation ids, flag words,
padding) left out. This folder is the only place in the repository where whole value tables are allowed; everything else in
`docs/` carries layouts, addresses, algorithms and, at most, a handful of landmark values.

| Page | Contents |
|---|---|
| [thps1-tricks.md](thps1-tricks.md) | flips and grabs by direction, the diagonal flips per skater, the specials, spins, grind types and points, the skaters' base stats |
| [thps1-gaps.md](thps1-gaps.md) | all 165 gap entries: id, name, points, kind |

**Source of truth is the game.** Every value here can be checked on your own copy. Where a page
says "not tabulated" the information is in the game but not in our arrangement.

**Removing this folder** removes no other documentation: nothing outside it links to a value that only exists here. Rights holders
who want it changed or removed: see the README's Legal section.

**The policy** (what a documentation page may contain, and the linter that enforces it): addresses, sizes, counts, strides, hashes,
header fields, names, struct layouts and algorithms, anywhere; individual constants with their address, anywhere; full tables of
entity-keyed values only here. Never, anywhere: ROM bytes or hex runs, assembly or decompiled source, textures, models, audio,
renders or video, dialogue and long descriptions. Screenshots only in `docs/screenshots/`: a few, for the README.

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. Facts derived from
analysis of a retail cartridge dump. See the README.
