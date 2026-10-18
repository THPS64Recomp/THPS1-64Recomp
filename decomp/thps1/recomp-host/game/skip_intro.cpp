// Skip Intro (skip_intro=1 in general.cfg / the General tab, or --skip-intro / --no-skip-intro): boot straight to
// the title. Like Conker's skip_intro mod, it works through the game's own front end rather
// than around it (RE notes: the private development notes, Q17):
//
// - The boot notice "EXPANSION PAK FOUND. OK" is a message on the pak/notice screen
//   (Front_NoticeUpdate, vtable 0x80020860 in v1.1). It waits for B (or ~9 s). With Skip
//   Intro on, the host presses B for the player while that message is up. Only that message:
//   the same screen shows Controller Pak errors and repair prompts, which are never answered
//   for the player. The message's first text line pointer (gMsgLine0, in the message object)
//   is what tells them apart; gMsgState is nonzero (2) while a message is up.
// - The legal screen and the Activision / Neversoft / ... logo videos are one screen
//   (Front_IntroUpdate, vtable 0x80019270 in v1.1). Its update returns 3 when it is done:
//   START after the legal screen's minimum time, or after the last of up to 10 videos. The
//   front end then shows the title. With Skip Intro on, the hook returns 3 on its first frame.
#include <atomic>
#include <cinttypes>
#include <cstdio>

#include "thps_hooks.h"
#include "host.h"
#include "versions.h"

namespace {
// Addresses come from the version's name table: gMsgLine0 (first text line pointer of the message
// object), gMsgState (nonzero while a notice message is up), gTextExpansionFound / NotFound.
constexpr int k_hold_polls = 2, k_gap_polls = 6;

std::atomic<int> g_b_polls{0};       // > 0: polls left in the current injected press (+ gap)
std::atomic<bool> g_logged_notice{false}, g_logged_intro{false};
}  // namespace

extern "C" int thps_skip_intro_logos(uint8_t*, recomp_context*) {
    if (!thps::settings::skip_intro()) return 0;
    if (!g_logged_intro.exchange(true)) {
        std::printf("[thps] skip intro: legal screen + logos skipped (frame %" PRIu64 ")\n", thps::stats.vi_origin_changes.load());
        std::fflush(stdout);
    }
    return 1;
}

extern "C" void thps_skip_intro_notice(uint8_t* rdram, recomp_context* ctx) {
    if (!thps::settings::skip_intro()) return;
    (void)ctx;
    const thps::SymTable& sym = thps::sym();
    bool message_up = MEM_W(0, (gpr)(int32_t)sym.gMsgState) != 0;
    uint32_t line0 = uint32_t(MEM_W(0, (gpr)(int32_t)sym.gMsgLine0));
    if (!message_up || (line0 != sym.gTextExpansionFound && line0 != sym.gTextExpansionNotFound)) return;
    int expected = 0;
    if (g_b_polls.compare_exchange_strong(expected, k_hold_polls + k_gap_polls) && !g_logged_notice.exchange(true)) {
        std::printf("[thps] skip intro: pressing B on the Expansion Pak notice (frame %" PRIu64 ")\n", thps::stats.vi_origin_changes.load());
        std::fflush(stdout);
    }
}

// Game thread, port 1 poll (main.cpp get_input).
void thps::skip_intro_input(uint16_t* buttons) {
    int n = g_b_polls.load();
    if (n <= 0) return;
    if (n > k_gap_polls) *buttons |= 0x4000;  // B
    g_b_polls.store(n - 1);
}

// Games with front-end overlays (THPS2/3) learn here when a screen is loaded; THPS1 has none.
void thps::skip_intro_overlay_loaded(const char*) {}
