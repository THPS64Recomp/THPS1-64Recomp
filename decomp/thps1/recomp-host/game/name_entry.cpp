// THPS1 name entry (SAVE CAREER after a run, OPTIONS > CONTROLLER PAK > SAVE DATA): the screen is a row of 13 slots driven only
// by the N64 D-pad (NameEntry_Update, 0x8002B6D0 in v1.1: Left/Right = move the cursor, Up/Down = change the letter, A = accept,
// B = back; it never reads the analog stick). The hook below only tells the host that the screen is running, so src/input.cpp can
// turn the left stick / keyboard arrows into D-pad bits meanwhile (keyboard players have no D-pad key otherwise).
#include "recomp.h"
#include "host.h"

extern "C" void thps_name_entry_update(uint8_t*, recomp_context*) { thps::name_entry_tick(); }
