// THPS1's side of the extended draw distance (the setting and governor: common/host/src/draw_distance.cpp).
//
// The far plane. The level's trigger script sets its fog with a command that ExecuteCommandList passes to the fog setter (v1.1
// 0x8005E5CC; the default, 6000 + 2048, at start-up): fog start and end in PlayStation units, and gFarPlane = end / 16 (float, N64
// units). The gameplay camera hands gFarPlane to View_SetFrustum every frame (twice: two frustums of the skater's view), and that one
// value is the projection's far clip, the far end of the cull volume, and (through the projection: the fog is a fixed
// gSPFogPosition(996, 1000)) where the fog ramp lies. So scaling the far argument of exactly those calls moves all three together.
// Other frustums (the sky's 15000 / 20000, the front end's 500, the 2000 one) are left alone: only a call whose far equals
// gFarPlane is scaled.
//
// The buffers. Two top-level display lists of gDlBufSize bytes (0xFA00, from the heap at start-up; gDlBufs) and two matrix pools of
// 500 x 64 bytes (gMtxPools). The game's matrix allocator caps at 500 and then hands out one scratch matrix (gMtxScratch) for the
// rest of the frame; the display list has no cap: its end-of-frame code notices an overrun only afterwards. The game writes the list's
// length into the gfx task's data_size, so each task says how full its buffer was; matrices are counted from the list's G_MTX commands
// that point into the task's pool (the highest one handed out).
//
// Bigger matrix pools. 500 matrices is what limits Full in Downtown (its far streets' environment-mapped meshes take a pool matrix per
// vertex). The pools come from the game heap once, at start-up (the gfx set-up's two Heap_Alloc(gMainHeap, 32000, 8)), and the cap is an
// immediate in the allocator (Gfx_AllocMtx: `slti 500`). With dd_buffers = bigger (the default; src/draw_distance.cpp) thps_mem_alloc
// always asks for kBigMtxCap matrices per pool, whatever the setting, and thps_gfx_alloc_mtx caps at kBigMtxCap only while the setting
// is not `original`; at `original` it runs the game's own allocator (cap 500, in the first 500 slots of the same pools). So the setting
// takes effect at once, in either direction (2026-10-22, the private development notes). With dd_buffers = original both hooks
// leave the game alone: its own requests, pools and allocator, and the governor keeps the far plane within 500.
//
// The mesh queue. The renderer collects the meshes of the frame's course items in one fixed queue (gMeshQueue: 512 entries of 12 bytes,
// mesh / matrix / next, linked into per-material lists). Its flush (v1.1 0x800B5210) drops every entry past 512 without a word. Items are
// queued in course-item order, not by distance, so when a longer far plane lets more far items in, the meshes dropped can be the nearest
// ones (THPS1 Streets start from x2.5: the plaza's grass, rail and building bases vanish and the flat ground under them shows). So the
// queue is a third buffer for the governor: Mesh_QueueEmit (the pass that turns the queue into display-list commands, right after the
// last flush) notes the count. Read only; the game's code runs unchanged.
//
// Runs. The governor alone would hold Streets near x1 (its plaza and the near course take ~500 entries at x2), and a frame can still fill
// the queue before the governor reacts (it acts on the next frame). So with a longer far plane World_DrawItems runs several times,
// farthest first: the items within the game's own far plane last (band 0: what the game draws at x1, which always fits, the original game
// never draws more), and before it the items beyond, cut into runs by what their models would put into the queue (thps_world_draw_items).
// Each run fills and empties the queue on its own, so a run never loses a nearer run's meshes; and far is drawn before near, as in the
// game's single pass (translucent meshes blend over what is behind them). An item is left out of a run by its "skip" byte (+63, which the
// loop tests first), set only for that run and put back. Streets: at most 3 runs beyond x1 at Full, none above 400 entries.
//
// Zone visibility ("full" only). The trigger scripts hide most course items by box as the skater moves (draw-cost culling, as in THPS2/3);
// with "full" the items the box command hid are unhidden for the draw call and drawn in the runs before band 0, whatever their distance,
// and every flag is put back after the call. Items hidden by name (events: secrets, goals) stay hidden. See zone_ownership.h.
#include <algorithm>
#include "guest_mem.h"
#include "zone_ownership.h"
#include <atomic>
#include <cmath>
#include <cstdlib>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <mutex>
#include <vector>

#include "draw_distance.h"
#include "thps_hooks.h"
#include "host.h"
#include "versions.h"

namespace {

using thps::mem::in_ram;
using thps::mem::word;
using thps::mem::put_word;
using thps::mem::f32;
using thps::mem::hword_ptr;
using thps::mem::HeapStats;
using thps::mem::heap_stats;
using thps::mem::hword;
using thps::zones::flag_ptr;
constexpr uint32_t kMtxPoolSize = 500;   // Gfx_AllocMtx: `slti 500`
constexpr uint32_t kBigMtxCap = 2048;    // with the setting on at start-up (as THPS2/3): 2 x 131072 bytes instead of 2 x 32000
std::atomic<uint32_t> g_mtx_cap{0};      // the pools' size in matrices when thps_mem_alloc enlarged them (0: the game's own 500)
constexpr uint32_t kQueueEntries = 512, kQueueCount = 0x188C;   // the flush: `li t1,512`, count at +6284 (entries at +140, 12 bytes each)
constexpr uint32_t kBlendEntries = 64, kBlendCount = 0x1C98;     // the flush's second list: `li s6,64`, count at +7320 (entries at +6296, 16 bytes)
// A run beyond the far plane stays below the governor's back-off (85 %) on both lists, so the runs never make it lower the far plane.
constexpr uint32_t kRunQueue = 400, kRunBlend = 48, kMaxRuns = 16;

std::atomic<uint32_t> g_queue_hw{0};   // most mesh-queue entries one run used since the last gfx task (game thread writes, gfx thread takes)
std::atomic<uint32_t> g_blend_hw{0};   // the same for the second list
std::atomic<uint32_t> g_runs_hw{0};    // most World_DrawItems runs in one call (band 0 included)
// The reset list: each entry points at a word the frame end zeroes (a pointer an object or particle caches for the frame; most adders put
// one on right after building a pool matrix for it). 2001 slots up to the next global, and none of the 6 adders checks the count.
constexpr uint32_t kResetSlots = 2000;
std::atomic<uint32_t> g_reset_hw{0};   // the most entries one frame had at its end (game thread writes, gfx thread takes)
// Inside the band-0 run of a split call: what the game draws at its own far plane, which a lower factor would not make smaller, so its
// queue use is not shown to the governor (game thread only).
bool g_band0_run = false;


// What one instance of a model puts into the queue and its second list (the flush, v1.1 0x800B5210). A model is a chunk with an offset
// table (word 0 a count, word 1 + i the offset of chunk i); its chunk 1 holds the parts: count, then each part's offset; a part's chunk 0
// is its header: word 0 a pointer whose +4 is the material, word 1 the part flags. Flag 0x800: not drawn; 0x8000: environment-mapped (drawn
// at once with pool matrices, not queued); 0x1 with a material whose (+92 & 3) == 3 and +79 == 0, or no 0x1: the second list; else the queue.
struct ModelCost { uint16_t queue = 0, blend = 0; };
ModelCost model_cost(const uint8_t* rdram, uint32_t model) {
    ModelCost c;
    auto ok = [](uint32_t a) { return a >= 0x80000000u && a < 0x80800000u; };
    if (!ok(model)) return c;
    const uint32_t parts = model + word(rdram, model + 8);
    if (!ok(parts)) return c;
    const uint32_t np = word(rdram, parts);
    for (uint32_t i = 0; i < np && i < 256; i++) {
        const uint32_t part = parts + word(rdram, parts + 4 + 4 * i);
        if (!ok(part)) break;
        const uint32_t hdr = part + word(rdram, part + 4);
        if (!ok(hdr)) break;
        const uint32_t flags = word(rdram, hdr + 4);
        if (flags & 0x8800) continue;
        if (!(flags & 1)) { c.blend++; continue; }
        const uint32_t p0 = word(rdram, hdr);
        if (!ok(p0)) continue;   // no material: the flush skips the part
        const uint32_t mat = word(rdram, p0 + 4);
        if (!ok(mat)) continue;
        const bool second = (word(rdram, mat + 92) & 3) == 3 && rdram[((mat + 79) & 0x3FFFFFF) ^ 3] == 0;
        if (second) c.blend++; else c.queue++;
    }
    return c;
}

// Zone visibility. Each course item has a "hidden" bit per player in its flag halfword (through the pointer at item +4: 1, player 2: 0x40),
// which World_DrawItems tests first. The trigger scripts set and clear those bits by box as the skater moves (World_SetVisibilityInBox,
// v1.1 0x80034AA4, from the trigger command at 0x80060870): THPS1's draw-cost culling, the same design as THPS2/3. At the Mall start 732
// of 900 items are hidden this way, so with any far plane the far end of a corridor stays black until the skater reaches the next trigger.
// Other writers hide one item by name, on events (World_FindItem v1.1 0x80038F9C: hide by name 0x80035250 sets 0x1061, the flag pointer
// by name 0x800352A4 for course set-ups and goals). Only the box kind may be undone for "full". The box hook runs the game's function and
// records, per item, the hidden bits that call changed (set -> noted, cleared -> forgotten); any other writer leaves the record alone, so
// a bit an event set is never in it. An item named by World_FindItem is never unhidden (event-owned) for the rest of the course. The record
// is per course instance: a new item list (pointer or count) or a course start (thps::dd::course_generation; THPS1's is the course items
// drawn again after a pause in drawing them, see thps_world_draw_items: a restart can rebuild the list at the same address; review
// 2026-10-26, finding 7) starts it again: empty, except for what the zone culling did and the items an event named since the course items were last drawn (the new
// course's set-up scripts, which run while it loads, before that first draw). Game thread only. (Now src/zone_ownership.h, shared with THPS2/3.)
std::atomic<uint32_t> g_frames{0};   // Gfx_FrameEnd calls (game frames)
constexpr uint32_t kCourseGap = 8;     // frames without drawing the course items that make the next draw a new course (load screens take seconds)

}  // namespace

bool thps::dd::supported() { return true; }

// Zone ownership: which hidden bits the culling boxes set, the box and find hooks and the course's trigger table are shared by the three
// games (src/zone_ownership.h, src/zone_ownership.cpp). THPS1: the box command shows on any nonzero value. The
// record is per course instance; THPS1's course start is the course items drawn again after a pause (thps_world_draw_items below).
const thps::zones::Profile& thps::zones::profile() {
    static const Profile p{true, 0x30, 0};
    return p;
}

// World_DrawItems(a0 = world: model list +4 (pointer to {models, count}), item pointers +12, item count +16; a1 = view; a2 = player) entry,
// game thread. Items: model index +2 (halfword), flag halfword through the pointer at +4 (0x2000 = drawn without the sphere test; the view
// mask: 64, or 1 when a2 is 0), model flags through the pointer at +8 (0x20: not drawn), centre +36/+40/+44 and radius +48 (floats,
// PlayStation units: x 0.0625), skip byte +63. View: camera position +144, cull plane normals +464 (5 x 3 floats), far +372. The game's
// sphere test (0x800A535C) culls an item when (radius + far)^2 < distance^2 or n . d + radius < 0 for one of the planes.
//
// Runs. Band 0 is the items within the game's own far plane (and the shown 0x2000 ones): exactly the original pass. The items beyond it are
// sorted by distance, farthest first, and cut into runs by what they would put into the queue (model_cost, items the planes cull count
// nothing): a run ends before it would pass kRunQueue entries or kRunBlend second-list entries. Each run fills and empties the queue on its
// own. (Until 2026-10-21 the runs were fixed distance bands, 1-2x, 2-4x, ... of the far plane: the 1-2x band alone took ~440 entries at
// some spots in Streets, the governor backed off at 85 % and Full settled near x2.)
extern "C" int thps_world_draw_items(uint8_t* rdram, recomp_context* ctx) {
    thread_local bool inside = false;
    if (inside) return 0;
    thps::dd::HookTimer timer;   // ftime: this hook's own time (the game's drawing excluded)
    const auto& s = thps::sym();
    const uint32_t world = uint32_t(ctx->r4), view = uint32_t(ctx->r5);
    thps::zones::Ownership& own = thps::zones::own();
    thps::zones::Record& g_zone = own.z;
    const bool dg = thps::dd::digest::on();   // tests: the decision digest (draw_distance.h): each call's inputs, per item what was unhidden and why it was or was not drawn
    // A course starts: the course items are drawn again after kCourseGap frames without (a load, the front end) or from another item array.
    // THPS1's gfx set-up runs once at start-up, so this is its count of course starts for the governor (the ceiling reset).
    if (world == s.gWorldItems) {
        static uint32_t last_frame = 0, last_arr = 0;
        const uint32_t fr = g_frames.load(std::memory_order_relaxed), a = word(rdram, world + 12);
        const uint32_t cn = word(rdram, world + 16);
        if (fr - last_frame > kCourseGap || a != last_arr) {
            thps::dd::note_course_start();
            if (dg) {   // tests: a course start and why (the frame count itself stays out of the hash: only whether the gap passed kCourseGap)
                const bool gapped = fr - last_frame > kCourseGap, changed = a != last_arr;
                thps::dd::digest::Hash h;
                h.u(gapped), h.u(changed), h.u(a), h.u(last_arr), h.u(cn);
                thps::dd::digest::record('C', uint32_t(ctx->r6), h, std::string(gapped && changed ? "gap+array" : gapped ? "gap" : "array") + " frames=" + std::to_string(fr - last_frame));
            }
        }
        last_frame = fr, last_arr = a;
        if (cn && cn <= 8192) thps::zones::sync(rdram, world);   // a new course instance takes the items named since the last draw, then that list starts again
        own.draw_begins();
    }
    // The function sets its own frustum first (View_SetFrustum, scaled there), so the factor in use, not the view's far before the call,
    // says whether this run reaches past the game's far plane.
    const float game_far = f32(rdram, s.gFarPlane);
    const bool unhide = thps::dd::show_all() && world == s.gWorldItems;   // "full": the zone-culled items too
    const uint32_t n = word(rdram, world + 16), arr = word(rdram, world + 12);
    auto left_to_game = [&](uint32_t why) {   // tests: the call, left to the game (why: 1 its own picture, 2 no usable item list)
        thps::dd::digest::Hash h;
        h.u(why), h.u(world == s.gWorldItems), h.u(n), h.u(unhide), h.u(thps::dd::unhide_everything()), h.f(game_far), h.f(thps::dd::factor());
        thps::dd::digest::record('d', uint32_t(ctx->r6), h);
    };
    if (!(game_far > 0.0f) || (!unhide && !(thps::dd::factor() > 1.001f))) {   // the game's own picture: one run, as the game does
        if (dg) left_to_game(1);
        return 0;
    }
    if (n == 0 || n > 8192) {
        if (dg) left_to_game(2);
        return 0;
    }
    // Zone visibility: clear the bits the zone culling set (not an event's), for this call only; every flag is put back at the end, so
    // collision and the trigger state never see the change. Items with flags 0x2000 | 0x20 are the course's backdrop (skyline, the
    // outside seen through a door): the loop does not queue them but marks them in a per-view table (0x8003546C) that the sky pass
    // (0x800340A0, its own far plane of 20000) draws next frame; at most 48 are registered (0x80033E28), each marked once per call, and
    // they stay in band 0 (one run), so unhiding them cannot overflow the table. Items with 0x2000 alone skip the sphere test and are queued
    // like any other; unhidden, they go into the runs before band 0 like the rest (band 0 stays what the game draws). Downhill Jam's lower
    // end (the pool, blocks and rails below the BRETT wall) is 27 of them, zone-hidden until the skater comes over the edge (2026-10-23).
    static std::vector<uint32_t> saved;   // flag halfword address, value
    static std::vector<uint8_t> unhid;    // per item: unhidden here (drawn in a run before band 0, whatever its distance)
    // tests: cat 0 not this call's (hidden for the player, a model flag, the skip byte; or in no run it draws in), 1 outside the view planes, 2 band 0 (the
    // game's own), 3 held, 4 in a run beyond the far plane
    static std::vector<uint16_t> before;
    static std::vector<uint8_t> cat;
    static std::vector<int32_t> centre, radius;   // per item, for the item lines: camera to the bounding sphere's centre, and its radius
    saved.clear();
    unhid.assign(n, 0);
    if (dg) {
        before.resize(n), cat.assign(n, 0);
        for (uint32_t i = 0; i < n; i++) before[i] = *flag_ptr(rdram, arr, i);
    }
    uint32_t hidden = 0;
    if (unhide) {
        thps::zones::sync(rdram, world);
        thps::zones::build(rdram, ctx);
        for (uint32_t i = 0; i < n && i < g_zone.bits.size(); i++) {
            uint16_t* h = flag_ptr(rdram, arr, i);
            hidden += (*h & 0x41) != 0;
            // Only what the zone culling hid (zone_ownership.h); nothing unhidden gives zone 0 (unhid[i] stays 0).
            const uint16_t zone = own.unhide_bits(i, *h, thps::dd::unhide_everything());
            if (zone) {
                saved.push_back(uint32_t(reinterpret_cast<uint8_t*>(h) - rdram));
                saved.push_back(*h);
                *h = uint16_t(*h & ~zone);
                unhid[i] = 1;
            }
        }
    }
    auto restore = [&] {
        for (size_t k = 0; k + 1 < saved.size(); k += 2) *reinterpret_cast<uint16_t*>(rdram + saved[k]) = uint16_t(saved[k + 1]);
    };
    static uint32_t frames = 0;
    if (unhide && thps::verbose() && (frames++ % 300) == 0) {   // evidence: hidden items, and how many of them only the zone culling hid
        uint32_t named = 0;
        for (uint8_t e : g_zone.event) named += e;
        uint32_t in_state = 0;
        for (uint32_t i = 0; i < n; i++) {
            if (!unhid[i]) continue;
            const uint32_t it = word(rdram, arr + 4 * i);
            for (const auto& [key, culling] : thps::zones::classes())
                if (!culling && thps::zones::item_in_box(rdram, it, key)) { in_state++; break; }
        }
        std::printf("[thps] draw distance: items %u, hidden %u, of them by the zone culling (unhidden for this draw) %u, in state boxes %u; items named by events %u; camera (%.0f, %.0f, %.0f)\n", n, hidden,
                    uint32_t(saved.size() / 2), in_state, named, f32(rdram, view + 144) * 16.0f, f32(rdram, view + 148) * 16.0f, f32(rdram, view + 152) * 16.0f);
        // the ones kept hidden (not the zone culling's, or an event's): index, flags, record, event, centre (item +36/+40/+44, floats)
        for (uint32_t i = 0, shown = 0; i < n && i < g_zone.bits.size() && shown < 64; i++) {
            const uint32_t it = word(rdram, arr + 4 * i);
            const uint16_t f = *flag_ptr(rdram, arr, i);
            if (!(f & 0x41) || unhid[i]) continue;
            std::printf("[thps] draw distance:   kept hidden: item %u flags 0x%04X zone 0x%02X event %u at (%.0f, %.0f, %.0f)\n", i, f, g_zone.bits[i],
                        g_zone.event[i], f32(rdram, it + 36), f32(rdram, it + 40), f32(rdram, it + 44));
            shown++;
        }
        std::fflush(stdout);
    }
    const uint32_t mlist = word(rdram, world + 4);
    const uint32_t models = word(rdram, mlist), nmodels = word(rdram, mlist + 4);
    // Model costs, kept while the course (its item array) stays the same.
    static uint32_t cost_for = 0;
    static std::vector<ModelCost> cost;
    static std::vector<uint8_t> have;
    if (cost_for != arr || cost.size() != nmodels) {
        cost_for = arr;
        cost.assign(nmodels < 65536 ? nmodels : 0, ModelCost{});
        have.assign(cost.size(), 0);
    }
    const float cam[3] = {f32(rdram, view + 144), f32(rdram, view + 148), f32(rdram, view + 152)};
    float plane[5][3];
    for (int p = 0; p < 5; p++)
        for (int k = 0; k < 3; k++) plane[p][k] = f32(rdram, view + 464 + 12 * p + 4 * k);
    const uint32_t mask = uint32_t(ctx->r6) ? 64 : 1;
    auto h16 = [&](uint32_t a) { return hword(rdram, a); };
    static std::vector<uint32_t> skip_addr;   // the skip byte of every item (RDRAM byte address)
    static std::vector<uint8_t> was;
    static std::vector<uint16_t> run;         // 0: band 0; r > 0: the r-th run beyond the far plane (1 = farthest)
    struct Far { float gap; uint32_t i; ModelCost c; };
    constexpr uint16_t kHeld = 0xFFFF;   // an unhidden item beyond unhide_reach() while the factor is below its end: in no run
    const float reach = unhide ? thps::dd::unhide_reach() * game_far : 0.0f;
    static std::vector<Far> far_list;
    skip_addr.resize(n), was.resize(n), run.assign(n, 0), far_list.clear();
    for (uint32_t i = 0; i < n; i++) {
        const uint32_t it = word(rdram, arr + 4 * i);
        skip_addr[i] = ((it + 63) & 0x3FFFFFF) ^ 3;
        was[i] = rdram[skip_addr[i]];
        const float dx = f32(rdram, it + 36) * 0.0625f - cam[0], dy = f32(rdram, it + 40) * 0.0625f - cam[1], dz = f32(rdram, it + 44) * 0.0625f - cam[2];
        const float r = f32(rdram, it + 48) * 0.0625f;
        const float gap = std::sqrt(dx * dx + dy * dy + dz * dz) - r;   // camera to the bounding sphere
        const uint16_t flags = h16(word(rdram, it + 4));
        if (dg) centre.resize(n), radius.resize(n), centre[i] = int32_t(gap + r), radius[i] = int32_t(r);
        if (unhid[i] && gap > reach) { run[i] = kHeld; if (dg) cat[i] = 3; continue; }   // the factor below its end: not drawn this frame
        // band 0: within the far plane, and the backdrop (0x2000 | 0x20); an unhidden item never otherwise (band 0 is what the game draws)
        if (unhid[i] ? (flags & 0x2020) == 0x2020 : ((flags & 0x2000) || !(gap > game_far))) {
            if (dg) cat[i] = 2;
            continue;
        }
        ModelCost c;
        // Drawn at all? The same tests as the game's loop, then the planes (last call's planes: a margin for a turning camera).
        bool drawn = !(flags & mask) && !(word(rdram, word(rdram, it + 8)) & 0x20) && !was[i];
        if (dg) cat[i] = drawn ? 4 : 0;
        for (int p = 0; drawn && !(flags & 0x2000) && p < 5; p++)   // (0x2000: the game skips the sphere test)
            if (plane[p][0] * dx + plane[p][1] * dy + plane[p][2] * dz + r + 0.25f * gap < 0.0f) drawn = false;
        if (dg && cat[i] == 4 && !drawn) cat[i] = 1;
        const uint32_t mi = h16(it + 2);   // the main model (a LOD model, when the game picks one, is smaller)
        if (drawn && mi < cost.size()) {
            if (!have[mi]) cost[mi] = model_cost(rdram, word(rdram, models + 4 * mi)), have[mi] = 1;
            c = cost[mi];
        }
        far_list.push_back({gap, i, c});
    }
    std::sort(far_list.begin(), far_list.end(), [](const Far& a, const Far& b) { return a.gap > b.gap; });
    uint32_t runs = 0, q = 0, bl = 0;
    for (const Far& f : far_list) {
        if (runs == 0 || ((q + f.c.queue > kRunQueue || bl + f.c.blend > kRunBlend) && runs < kMaxRuns)) runs++, q = 0, bl = 0;
        q += f.c.queue, bl += f.c.blend;
        run[f.i] = uint16_t(runs);
    }
    g_runs_hw = std::max(g_runs_hw.load(), runs + 1);
    const uint64_t a0 = ctx->r4, a1 = ctx->r5, a2 = ctx->r6;
    inside = true;
    for (uint32_t r = 1; r <= runs + 1; r++) {   // the runs beyond the far plane, farthest first, then band 0 (always)
        const uint16_t want = uint16_t(r <= runs ? r : 0);
        for (uint32_t i = 0; i < n; i++)
            if (run[i] != want) rdram[skip_addr[i]] = 1;
        ctx->r4 = a0, ctx->r5 = a1, ctx->r6 = a2;
        g_band0_run = want == 0;
        timer.guest([&] { thps::call_guest(s.World_DrawItems, rdram, ctx); });
        g_band0_run = false;
        for (uint32_t i = 0; i < n; i++) rdram[skip_addr[i]] = was[i];
    }
    inside = false;
    restore();
    if (dg) {   // tests: the call's inputs, each item's record and decision, the runs in order, and whether every flag and skip byte was put back
        thps::dd::digest::Hash h;
        h.u(n), h.u(world == s.gWorldItems), h.u(unhide), h.u(thps::dd::unhide_everything()), h.u(mask), h.u(a2);
        h.f(game_far), h.f(f32(rdram, view + 372)), h.f(thps::dd::factor()), h.f(reach);
        for (float c : cam) h.f(c);
        uint32_t restore_bad = 0, counts[5] = {0, 0, 0, 0, 0}, unhidden = 0;
        for (uint32_t i = 0; i < n; i++) {
            restore_bad += *flag_ptr(rdram, arr, i) != before[i] || rdram[skip_addr[i]] != was[i];
            const bool rec = i < g_zone.bits.size();
            h.u(before[i]), h.u(rec ? g_zone.bits[i] : 0), h.u(rec ? g_zone.after[i] : 0), h.u(rec ? g_zone.event[i] : 0), h.u(rec ? g_zone.state[i] : 0);
            h.u(unhid[i]), h.u(cat[i]), h.u(run[i]), h.u(was[i]);
            counts[cat[i]]++, unhidden += unhid[i] != 0;
            if (thps::dd::digest::items())
                thps::dd::digest::item_line(std::to_string(i) + " " + std::to_string(cat[i]) + " " + std::to_string(run[i]) + " " + std::to_string(before[i]) + " " +
                                            std::to_string(unhid[i]) + " " + std::to_string(rec ? g_zone.bits[i] : 0) + " " +
                                            std::to_string(rec ? g_zone.event[i] : 0) + " " + std::to_string(rec ? g_zone.state[i] : 0) + " " +
                                            std::to_string(centre[i]) + " " + std::to_string(radius[i]));
        }
        // the runs in order: each run's first-to-last items in the sorted list (farthest first) with the queue and second-list entries it was cut at
        h.u(runs), h.u(far_list.size());
        uint32_t cur = 0, count = 0, qq = 0, bb = 0;
        auto close_run = [&] { if (cur) h.u(cur), h.u(count), h.u(qq), h.u(bb); };
        for (const Far& f : far_list) {
            if (run[f.i] != cur) close_run(), cur = run[f.i], count = qq = bb = 0;
            count++, qq += f.c.queue, bb += f.c.blend;
            h.u(f.i);
        }
        close_run();
        h.u(restore_bad);
        char d[200];
        std::snprintf(d, sizeof d, "unhidden=%u own=%u held=%u view=%u notdrawn=%u runs=%u restore_bad=%u factor=%.3f far=%.0f", unhidden, counts[2], counts[3],
                      counts[1], counts[0], runs, restore_bad, double(thps::dd::factor()), double(game_far));
        thps::dd::digest::record('D', uint32_t(a2), h, d);
    }
    return 1;
}

// Mesh_QueueEmit(a0 = queue, a1, a2) entry, game thread. The item pass and the object pass each fill the queue and empty it here. With a
// longer far plane the governor sees the runs beyond the far plane and the object pass (the sphere test lets more objects in), not band 0.
extern "C" void thps_mesh_queue_emit(uint8_t* rdram, recomp_context* ctx) {
    thps::dd::HookTimer timer;
    const uint32_t q = uint32_t(ctx->r4);
    if (q != thps::sym().gMeshQueue) return;   // not the queue this was written for
    if (g_band0_run) return;   // the game's own pass (with a longer far plane: band 0), as full as at x1 whatever the factor
    const uint32_t used = std::min(word(rdram, q + kQueueCount), kQueueEntries);
    uint32_t m = g_queue_hw.load();
    while (used > m && !g_queue_hw.compare_exchange_weak(m, used)) {}
    if (uint32_t(ctx->r5) == 0) return;   // the second list is drawn (and its count reset) only by a draw with a1 = 1: its count is the run's
    const uint32_t blend = std::min(word(rdram, q + kBlendCount), kBlendEntries);
    m = g_blend_hw.load();
    while (blend > m && !g_blend_hw.compare_exchange_weak(m, blend)) {}
}

// Gfx_FrameEnd() entry, game thread: the reset list holds this frame's entries until the body clears it (after sending the gfx task).
// More objects within a longer far plane mean more entries (two players: two views). Read only.
extern "C" void thps_gfx_frame_end(uint8_t* rdram, recomp_context*) {
    thps::dd::HookTimer timer;
    g_frames.fetch_add(1, std::memory_order_relaxed);
    const uint32_t n = word(rdram, thps::sym().gMtxResetCount);
    uint32_t m = g_reset_hw.load();
    while (n > m && !g_reset_hw.compare_exchange_weak(m, n)) {}
}

// The game re-derives the gameplay camera's frustum from the view's stored fields (View_Frustum: l, r, b, t, near, far) every frame, so after
// one scaled call the view holds the scaled far and passes that back. A call is the gameplay camera's when its far is gFarPlane or the
// far this function last returned; it gets gFarPlane x k. With k = 1 that is gFarPlane again, so going back to `original` (or the
// governor lowering k) restores the game's own value at the next frame. Game thread only.
float thps::dd::dd_game_far(uint8_t* rdram, float f, float k) {
    static float last_out = 0.0f;
    const float game_far = f32(rdram, thps::sym().gFarPlane);
    if (!(game_far > 0.0f) || (f != game_far && f != last_out)) return f;
    note_game_far(game_far);
    const float out = std::min(game_far * k, std::max(game_far, kFullFarPlane));   // full mode: as far as kFullFarPlane
    last_out = out == game_far ? 0.0f : out;
    note_effective(out / game_far);
    return out;
}

bool thps::dd::dd_game_measure(uint8_t* rdram, uint32_t data_ptr, uint32_t data_size, BufferUse& u) {
    const auto& s = thps::sym();
    const uint32_t phys = data_ptr & 0x3FFFFFF;
    int idx = -1;
    for (int i = 0; i < 2; i++)
        if ((word(rdram, s.gDlBufs + 4 * i) & 0x3FFFFFF) == phys) idx = i;
    if (idx < 0) return false;
    u.dl_cap = word(rdram, s.gDlBufSize);
    u.dl_bytes = data_size;
    const uint32_t big = g_mtx_cap.load();
    u.mtx_cap = big && thps::dd::enlarge_pools() ? big : kMtxPoolSize;   // the cap in force
    if (s.gMeshQueue) {
        u.queue_used = g_queue_hw.exchange(0);
        u.queue_cap = kQueueEntries;
        u.blend_used = g_blend_hw.exchange(0);
        u.blend_cap = kBlendEntries;
        u.runs = g_runs_hw.exchange(0);
    }
    u.reset_used = g_reset_hw.exchange(0);
    u.reset_cap = kResetSlots;
    const uint32_t pool = word(rdram, s.gMtxPools + 4 * idx) & 0x3FFFFFF, scratch = s.gMtxScratch & 0x3FFFFFF;
    const uint32_t end = phys + (data_size < u.dl_cap ? data_size : u.dl_cap);
    for (uint32_t pc = phys; pc + 8 <= end; pc += 8) {
        if ((word(rdram, pc) >> 24) != 0xDA) continue;   // G_MTX
        const uint32_t m = word(rdram, pc + 4) & 0x3FFFFFF;
        if (m >= pool && m < pool + u.mtx_cap * 64) u.mtx_used = std::max(u.mtx_used, (m - pool) / 64 + 1);   // the allocator hands them out in order
        else if (m == scratch) u.mtx_capped = true;
    }
    return true;
}

// `dd item N` / `dd own N` (tests): src/zone_ownership.cpp.
std::string thps::dd::dd_game_item(uint8_t* rdram, uint32_t index) { return thps::zones::dd_item(rdram, index); }
std::string thps::dd::dd_game_own(uint8_t* rdram, uint32_t index) { return thps::zones::dd_own(rdram, index); }

// The matrix pools. The gfx set-up (us11 0x800BDA40, us10 0x800A3DE0, once at start-up) asks Heap_Alloc(gMainHeap, 32000, 8) twice: the
// first result goes to gMtxPools[0], then (s0 = &gMtxPools in the delay slot) the second to gMtxPools[1]. Those two are the only requests
// of that size and alignment made while gMtxPools[1] is still 0, so no other call is touched, and after start-up none matches again.
// With dd_buffers = bigger, each asks for kBigMtxCap x 64 bytes instead. If the heap has no room for the bigger block, the game's own
// request is made after all (and the heap's failed-size cache put back): the game gets its 500.
// Every other request to gMainHeap is run here too (the game's own call, unchanged) to keep the heap's low-water marks for `dd heap`.
// The heap (Heap_AllocUnlocked 0x8009E728): free list head +0, next +4, free bytes at a block's end +20; +16 the size of the last failed
// request (-1 = none), which makes every later request of that size or more fail at once.
namespace {
uint32_t g_first_pool = 0;      // game thread, start-up: what the first pool request returned
bool g_first_big = false;       //   and whether it is the bigger size
// Low-water marks of gMainHeap (any thread that allocates; under g_low_mutex), since the start or `dd heap reset`.
struct HeapLow {
    uint32_t calls = 0, failed = 0, biggest = 0;
    uint32_t free_min = UINT32_MAX, largest_min = UINT32_MAX;   // after an allocation
    int64_t margin_min = INT64_MAX;                              // largest free block before a request - its size
    uint32_t margin_size = 0;                                    //   the request that had the least margin
};
std::mutex g_low_mutex;
HeapLow g_low;
void note_heap(const HeapStats& before, const HeapStats& after, uint32_t size, bool ok) {
    std::lock_guard lock{g_low_mutex};
    g_low.calls++;
    if (!ok) g_low.failed++;
    g_low.biggest = std::max(g_low.biggest, size);
    g_low.free_min = std::min(g_low.free_min, after.free_bytes);
    g_low.largest_min = std::min(g_low.largest_min, after.largest);
    const int64_t m = int64_t(before.largest) - int64_t(size);
    if (m < g_low.margin_min) g_low.margin_min = m, g_low.margin_size = size;
}
}  // namespace

extern "C" int thps_mem_alloc(uint8_t* rdram, recomp_context* ctx) {
    constexpr uint32_t kGamePool = kMtxPoolSize * 64;
    static thread_local bool inside = false;
    if (inside) return 0;
    const auto& s = thps::sym();
    const uint32_t heap = uint32_t(ctx->r4), size = uint32_t(ctx->r5), align = uint32_t(ctx->r6);
    if (heap != s.gMainHeap) return 0;
    auto own_request = [&]() {   // the game's own call, measured
        const HeapStats before = heap_stats(rdram, heap);
        inside = true;
        thps::call_guest(s.Heap_Alloc, rdram, ctx);
        inside = false;
        note_heap(before, heap_stats(rdram, heap), size, uint32_t(ctx->r2) != 0);
        return 1;
    };
    if (size != kGamePool || align != 8 || word(rdram, s.gMtxPools + 4) != 0) return own_request();
    const uint32_t p0 = word(rdram, s.gMtxPools);
    const bool first = p0 == 0, second = p0 != 0 && p0 == g_first_pool && uint32_t(ctx->r16) == s.gMtxPools;
    if (!first && !second) return own_request();
    // The bigger pool is asked for only when it and the request after it will succeed: as in THPS2/3 (2026-10-23), the allocator's failure
    // path takes the heap's lock again while Heap_Alloc holds it, so a failed request hangs the game. Both pools are planned at the first
    // request (review 2026-10-26, finding 1: checking only the request at hand let a bigger first pool leave no room for the second one's
    // native size): placed first fit on a copy of the free list as Heap_AllocUnlocked would (size + 0x1F rounded to 4, plus the alignment; a
    // size at or above the failed-size cache fails at once), the bigger pair must fit and leave a largest free block of thps::dd::plan_floor
    // (what the game's own pair leaves, at most 768 KiB). Otherwise the game's own request is made (and for the second pool too, so both are the game's size). Tests:
    // THPS_DD_POOL_FAIL=1|2 makes that pool's check fail; THPS_DD_HEAP_FREE (src/draw_distance.h) a constrained free list.
    static const int fail_at = std::getenv("THPS_DD_POOL_FAIL") ? std::atoi(std::getenv("THPS_DD_POOL_FAIL")) : 0;
    auto need = [&](uint32_t n) { return ((n + 0x1F) & ~3u) + align; };
    auto plan_fits = [&](uint32_t pools_left) {   // the bigger size for this pool and the `pools_left - 1` after it
        const std::vector<uint32_t> blocks = thps::dd::heap_free_blocks(rdram, heap);
        const uint32_t cache = thps::dd::heap_failed_cache(rdram, heap);
        const int64_t native = thps::dd::first_fit_after(blocks, std::vector<uint32_t>(pools_left, need(kGamePool)), cache);
        return native >= 0 && thps::dd::first_fit_after(blocks, std::vector<uint32_t>(pools_left, need(kBigMtxCap * 64)), cache) >= thps::dd::plan_floor(native);
    };
    if (first) thps::dd::heap_view_begin();
    bool enlarge = first ? thps::dd::big_buffers() && !std::getenv("THPS_DD_NOPOOL") : g_first_big;
    if (enlarge && (fail_at == (first ? 1 : 2) || !plan_fits(first ? 2 : 1))) {
        std::printf("[thps] draw distance: WARNING no room for a %u-byte matrix pool %d: the game's %u\n", kBigMtxCap * 64, first ? 0 : 1, kGamePool);
        std::fflush(stdout);
        enlarge = false;
        if (!first) g_first_big = false;   // the first pool stays bigger than it needs; both are used at the game's cap
    }
    thps::dd::heap_view_take(need(enlarge ? kBigMtxCap * 64 : kGamePool), first ? "matrix pool 0" : "matrix pool 1");
    // tests: the set-up's two pool requests, as made (asked: the size handed to the game's allocator, taken before that call; the matrix allocator itself is not recorded)
    auto note_pool = [&](uint32_t asked, bool big, uint32_t got) {
        thps::dd::digest::Hash h;
        h.u(first), h.u(second), h.u(size), h.u(align), h.u(enlarge), h.u(big), h.u(asked), h.u(got != 0), h.u(g_mtx_cap.load());
        char d[128];
        std::snprintf(d, sizeof d, "pool%d size=%u asked=%u big=%d ok=%d", first ? 0 : 1, size, asked, big, got != 0);
        thps::dd::digest::record('A', 0, h, d);
    };
    if (!enlarge) {
        if (first) g_first_pool = 0, g_first_big = false;
        const uint32_t asked = uint32_t(ctx->r5);
        const int rc = own_request();   // the game's own request
        if (thps::dd::digest::on()) note_pool(asked, false, uint32_t(ctx->r2));
        return rc;
    }
    const HeapStats before = heap_stats(rdram, heap);
    ctx->r5 = int32_t(kBigMtxCap * 64);
    const uint32_t asked = uint32_t(ctx->r5);   // tests: what the game's allocator is asked for
    inside = true;
    thps::call_guest(s.Heap_Alloc, rdram, ctx);
    const bool big = uint32_t(ctx->r2) != 0;
    inside = false;
    const uint32_t got = uint32_t(ctx->r2);
    note_heap(before, heap_stats(rdram, heap), big ? kBigMtxCap * 64 : kGamePool, got != 0);
    if (first) {
        g_first_pool = got, g_first_big = big;
    } else if (g_first_big && big) {
        g_mtx_cap = kBigMtxCap;   // both pools are the bigger size: Gfx_AllocMtx may hand out that many
    }
    if (thps::dd::digest::on()) note_pool(asked, big, got);
    const HeapStats after = heap_stats(rdram, heap);
    std::printf("[thps] draw distance: matrix pool %d: %s (%u bytes) at 0x%08X; heap free %u -> %u bytes, largest block %u -> %u\n", first ? 0 : 1,
                big ? "2048 matrices" : "no room for 2048 matrices, the game's 500", big ? kBigMtxCap * 64 : kGamePool, got, before.free_bytes,
                after.free_bytes, before.largest, after.largest);
    std::fflush(stdout);
    return 1;
}

// Gfx_AllocMtx() entry, game thread: the game's allocator with the bigger cap (only once both pools are the bigger size, and only while the
// setting is not `original`). The game's code: n = gMtxCount; if (n < 500) { gMtxCount = n + 1; return gMtxPools[gFrameIndex] + n x 64; }
// return gMtxScratch. A switch in the middle of a frame is harmless: the count only grows within a frame, both caps index the same pools,
// and past 500 the game's own body hands out its scratch matrix as it always does.
extern "C" int thps_gfx_alloc_mtx(uint8_t* rdram, recomp_context* ctx) {
    const uint32_t cap = g_mtx_cap.load(std::memory_order_relaxed);
    if (!cap || !thps::dd::enlarge_pools()) return 0;   // the game's own body (cap 500)
    const auto& s = thps::sym();
    const uint32_t n = word(rdram, s.gMtxCount);
    if (int32_t(n) < int32_t(cap)) {
        put_word(rdram, s.gMtxCount, n + 1);
        const uint32_t pool = word(rdram, s.gMtxPools + 4 * (word(rdram, s.gFrameIndex) & 1));
        ctx->r2 = int32_t(pool + n * 64);
    } else {
        ctx->r2 = int32_t(s.gMtxScratch);
    }
    return 1;
}

// `dd heap [reset]` (tests): the game heap's failed-size cache, free bytes, free blocks and the largest one, the pools' size and the cap in
// force, then the low-water marks since the start (or the last reset): least free bytes and smallest largest block after an allocation,
// the least margin between a request and the largest free block (and that request's size), failed requests, the biggest request.
std::string thps::dd::dd_game_heap(uint8_t* rdram, bool reset) {
    const HeapStats h = heap_stats(rdram, thps::sym().gMainHeap);
    const uint32_t pool = g_mtx_cap.load() ? g_mtx_cap.load() : kMtxPoolSize, cap = g_mtx_cap.load() && enlarge_pools() ? pool : kMtxPoolSize;
    HeapLow l;
    {
        std::lock_guard lock{g_low_mutex};
        l = g_low;
        if (reset) g_low = HeapLow{};
    }
    char buf[440];
    std::snprintf(buf, sizeof buf, "at 0x%08X failed %d free %u blocks %u largest %u mtx_pool %u mtx_cap %u low: calls %u free_min %u largest_min %u margin_min %lld "
                  "(size %u) failed_calls %u biggest %u view_fail %u", thps::sym().gMainHeap, int32_t(h.failed), h.free_bytes, h.blocks, h.largest, pool, cap, l.calls,
                  l.calls ? l.free_min : 0, l.calls ? l.largest_min : 0, l.calls ? (long long)l.margin_min : 0LL, l.margin_size, l.failed, l.biggest,
                  thps::dd::heap_view_fails());
    return buf;
}

// `dd dlprobe` (THPS2/3 only): THPS1's display lists stay the game's own (64000 bytes; Full peaked at 57 %, 2026-10-21).
std::string thps::dd::dd_game_dlprobe(uint8_t*, bool) { return "none"; }
