cmake_minimum_required(VERSION 3.20)

# THPS1 (N64) recomp host. The host itself is shared by THPS1-3 (decomp/common/host, ADR 0006): this file only names the game
# and includes the shared CMake file. The game profile is game/game.toml (names, flags) and game/ (its own C++: skip_intro.cpp);
# the version tables are versions/ and decomp/common/games.toml. Build instructions and options: ../../common/host/cmake/thps_host.cmake
# and README.md.
project(THPS1Recomp C CXX)
set(THPS_FAMILY thps1)
set(THPS_SKIP_INTRO game)   # game/skip_intro.cpp: THPS1's legal screen and logos are one vtable screen (Front_IntroUpdate)
set(THPS_GAME_EXTRA_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/game/name_entry.cpp")   # the name-entry screen reads only the D-pad (see the file)
# The shared host tree (THPS64Host): decomp/common (a directory in the development tree, the submodule in a game repository);
# -DTHPS_HOST_ROOT or $THPS_HOST_ROOT override it with another THPS64Host checkout.
if (NOT THPS_HOST_ROOT AND DEFINED ENV{THPS_HOST_ROOT})
    set(THPS_HOST_ROOT "$ENV{THPS_HOST_ROOT}")
endif()
if (NOT THPS_HOST_ROOT)
    get_filename_component(THPS_HOST_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../common" ABSOLUTE)
endif()
set(THPS_HOST_ROOT "${THPS_HOST_ROOT}" CACHE PATH "The shared host tree (THPS64Host; default decomp/common)")
if (NOT EXISTS "${THPS_HOST_ROOT}/host/cmake/thps_host.cmake")
    message(FATAL_ERROR "The shared host (THPS64Host) was not found: run `git submodule update --init`, or pass -DTHPS_HOST_ROOT=<a THPS64Host checkout>")
endif()
include("${THPS_HOST_ROOT}/host/cmake/thps_host.cmake")
