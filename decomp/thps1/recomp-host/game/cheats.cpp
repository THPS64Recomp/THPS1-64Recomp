// THPS1's cheats (test aids; the shared part, cheats.cfg and the menu: common/host/src/cheats.cpp). RE notes: the private development notes "Cheats".
//
// Unlock All Levels (--unlock-levels). SELECT COURSE keeps one record per course (gCourseTable, 9 x 0x78 bytes); its word +0x10 says
// "locked": A does nothing on a locked course and the screen says what it needs (tapes, medals, or career progress in the other
// modes). CourseSelect_UpdateLock(screen) is the game's only writer of that word: run when the screen is made and each time the cursor
// moves, it sets the word of the course under the cursor (gCourseCursor) from the tapes (+0x3C) or medals
// (+0x40) the course needs and what the career's skater has. With the cheat on, the hook answers "available" (word = 0) and skips the
// count; the career's tapes and medals are not read or written, so nothing of this reaches the save. Every mode (career, free skate,
// single session) uses the same screen and word. Takes effect at the next cursor move.
#include <cstdio>
#include <string>
#include <utility>

#include "recomp.h"
#include "host.h"
#include "thps_hooks.h"
#include "versions.h"

// Perfect Balance, Slow Motion, Skip to Restart: the game's own cheat flags. THPS1 keeps them as words in one block that its
// button-code handler (v1.1 func_80069064, v1.0 func_80068844; called from the pause menu) toggles with `xori 1`, and that the game reads
// where it uses them (no accessor function): DoOnRailPhysics zeroes the rail balance (skater +0x9DC) while gCheatPerfectBalance is set;
// the frame update (v1.1 func_80035D08) halves the physics step (0x800DE99C) while gCheatSlowMotion is set (fast motion, the next flag,
// multiplies it by 1.5; the handler clears one when it sets the other); the pause menu builder (v1.1 func_80091974) adds the
// restart-point entry while gCheatSkipToRestart is set. The host sets a flag word to 1 at every controller poll while the cheat is on
// (the game clears these words only through its own toggle), and to 0 once when it is turned off. Live: the next frame.
// Not saved: a career saved with all of them on is byte-identical to one saved with none (sessions cheats-flags-off / -on).
bool thps::cheats::game_has(Id id) { return id == UnlockLevels || id == PerfectBalance || id == SlowMotion || id == SkipToRestart; }

const char* thps::cheats::game_note(Id id) {
    switch (id) {
        case UnlockLevels: return "Every course can be picked in SELECT COURSE (career, free skate, single session), also the ones that need medals. Takes effect when the cursor moves.";
        case PerfectBalance: return "Grinds never lose balance (the game's own cheat). Takes effect at once.";
        case SlowMotion: return "The game runs at half speed (the game's own cheat). Takes effect at once.";
        case SkipToRestart: return "The pause menu gets the game's restart-point entry: jump to any start point of the level. Takes effect the next time you pause.";
        default: return "";
    }
}

namespace {
bool g_set[thps::cheats::kCount] = {};   // game thread only: the host set this flag word, so it clears it again when the cheat goes off
}

std::string thps::cheats::game_stats() { return ""; }

void thps::cheats::game_tick(uint8_t* rdram) {
    const thps::SymTable& sym = thps::sym();
    const std::pair<Id, uint32_t> flags[] = {{PerfectBalance, sym.gCheatPerfectBalance}, {SlowMotion, sym.gCheatSlowMotion}, {SkipToRestart, sym.gCheatSkipToRestart}};
    for (const auto& [id, addr] : flags) {
        const bool want = on(id);
        if (want) {
            if (MEM_W(0, (gpr)(int32_t)addr) != 1) MEM_W(0, (gpr)(int32_t)addr) = 1;
            g_set[id] = true;
        } else if (g_set[id]) {
            MEM_W(0, (gpr)(int32_t)addr) = 0;
            g_set[id] = false;
        }
    }
}

extern "C" int thps_unlock_course(uint8_t* rdram, recomp_context*) {
    if (!thps::cheats::on(thps::cheats::UnlockLevels)) return 0;
    const thps::SymTable& sym = thps::sym();
    const uint32_t cur = uint32_t(MEM_W(0, (gpr)(int32_t)sym.gCourseCursor));
    if (cur > 8) return 0;   // the screen clamps it to 0..8; anything else: let the game decide
    MEM_W(sym.Course_Locked, (gpr)(int32_t)(sym.gCourseTable + cur * sym.Course_Stride)) = 0;
    return 1;
}
