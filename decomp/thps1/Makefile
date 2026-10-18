# THPS1 (N64, U v1.1) decomp - asm round-trip build.
#
#   make setup      venv with pinned splat (once)
#   make extract    baserom.z64 -> baserom.main.bin, splat both configs
#   make            build main image + boot + ROM, then verify checksums
#   make check      checksums only
#   make boot-test  headless mupen64plus screenshots of the built ROM
#
# Nothing produced here (baserom*, asm/, assets/, build/, linker_scripts/) may
# be committed: it is all derived from the user's ROM.

# Path to your own dump (z64, big-endian). Only needed once: it is copied to
# baserom.z64. Example: make extract ROM_SRC=/path/to/thps1.z64
ROM_SRC     ?= baserom.z64
PY          := .venv/bin/python
CROSS       ?= mips-linux-gnu-
AS          := $(CROSS)as
LD          := $(CROSS)ld
OBJCOPY     := $(CROSS)objcopy
ASFLAGS     := -EB -march=vr4300 -mabi=32 -G 0 -I include -I asm --no-pad-sections
LDFLAGS     := -EB --no-check-sections --accept-unknown-input-arch -nostdlib

BUILD       := build
MAIN_BIN    := $(BUILD)/thps1.main.bin
BOOT_BIN    := $(BUILD)/thps1.boot.bin
ROM         := $(BUILD)/thps1.z64
ROM_RNC     := $(BUILD)/thps1.recompressed.z64

MAIN_S      := $(shell find asm/main -name '*.s' 2>/dev/null)
MAIN_O      := $(MAIN_S:%.s=$(BUILD)/%.o)
BOOT_S      := $(shell find asm/boot -name '*.s' 2>/dev/null)
BOOT_O      := $(BOOT_S:%.s=$(BUILD)/%.o)
BIN_O       := $(patsubst %.bin,$(BUILD)/%.o,$(shell find assets/boot -name '*.bin' 2>/dev/null))

.PHONY: all setup extract check clean distclean boot-test recompress recomp-inputs recomp

all: $(ROM) $(ROM_RNC) check

setup: deps
	uv venv .venv -p 3.12
	uv pip install --python $(PY) -r requirements.txt

RNC_COMMIT := 499e8128f9a3890cb4d287a11608b3ae1e0df440
deps:
	@test -d .deps/rnc_propack_source || git clone -q https://github.com/lab313ru/rnc_propack_source .deps/rnc_propack_source
	git -C .deps/rnc_propack_source checkout -q $(RNC_COMMIT)

baserom.z64:
	@test -f "$(ROM_SRC)" || (echo "Put your THPS1 (U) v1.1 z64 at baserom.z64 or pass ROM_SRC=..."; false)
	cp "$(ROM_SRC)" $@

extract: baserom.z64
	shasum -c checksums/input.rom.sha1
	$(PY) -I tools/thps_unpack.py baserom.z64 baserom.main.bin
	shasum -c checksums/input.main.sha1
	rm -rf asm assets linker_scripts
	mkdir -p linker_scripts
	$(PY) -m splat split config/thps1.main.yaml
	$(PY) -m splat split config/thps1.boot.yaml
	$(PY) -I tools/fix_asm.py $$(find asm -name '*.s')

# ---------------------------------------------------------------- objects
$(BUILD)/%.o: %.s
	@mkdir -p $(dir $@)
	$(AS) $(ASFLAGS) -o $@ $<

$(BUILD)/assets/%.o: assets/%.bin
	@mkdir -p $(dir $@)
	$(LD) -EB -r -b binary -o $@ $<

# ---------------------------------------------------------------- main image
$(BUILD)/thps1_main.elf: $(MAIN_O) linker_scripts/thps1_main.ld
	$(LD) $(LDFLAGS) -T linker_scripts/thps1_main.ld \
	  -T linker_scripts/main_undefined_syms_auto.txt \
	  -T linker_scripts/main_undefined_funcs_auto.txt \
	  -Map $(BUILD)/thps1_main.map -o $@

$(MAIN_BIN): $(BUILD)/thps1_main.elf
	$(OBJCOPY) -O binary $< $@

# ---------------------------------------------------------------- boot + ROM
# The ROM link places header, IPL3, boot segment and every byte after the boot
# segment (chunk table, compressed main chunks, asset packs) from the splat
# config. The chunks are taken from the ROM as-is (bin) for this target.
$(BUILD)/thps1.elf: $(BOOT_O) $(BIN_O) linker_scripts/thps1.ld
	$(LD) $(LDFLAGS) -T linker_scripts/thps1.ld \
	  -T linker_scripts/boot_undefined_syms_auto.txt \
	  -T linker_scripts/boot_undefined_funcs_auto.txt \
	  -Map $(BUILD)/thps1.map -o $@

$(ROM): $(BUILD)/thps1.elf
	$(OBJCOPY) -O binary --gap-fill 0x00 $< $@

# ERZ packer: lab313ru/rnc_propack_source + our look-ahead patch.
# lab313ru/rnc_propack_source checkout (make deps clones it into .deps/)
RNC_SRC     ?= .deps/rnc_propack_source
RNC         := $(BUILD)/tools/rnc_propack
$(RNC): tools/rnc_propack/lookahead.patch
	@mkdir -p $(BUILD)/tools/rnc_src
	cp $(RNC_SRC)/main.c $(BUILD)/tools/rnc_src/main.c
	patch -s -p1 -d $(BUILD)/tools/rnc_src < tools/rnc_propack/lookahead.patch
	cc -O2 -o $@ $(BUILD)/tools/rnc_src/main.c

# Main image built from asm -> ERZ recompress -> spliced into the built ROM.
$(ROM_RNC): $(ROM) $(MAIN_BIN) $(RNC) tools/erz_pack.py tools/build_rom.py
	$(PY) -I tools/build_rom.py $(RNC) $(ROM) $(MAIN_BIN) $@

recompress: $(ROM_RNC)

check: $(MAIN_BIN) $(ROM) $(ROM_RNC)
	@echo "--- main image (asm -> GNU as/ld) vs decompressed baserom image"
	shasum -c checksums/build.main.sha1
	@echo "--- ROM (boot asm + original compressed chunks) vs baserom"
	shasum -c checksums/build.rom.sha1
	@echo "--- ROM with main image recompressed by tools/erz_pack.py"
	shasum -c checksums/build.rom_recompressed.sha1

boot-test: $(ROM_RNC)
	tools/boot_test.sh $(ROM_RNC) $(BUILD)/boot-test

# ---------------------------------------------------------------- N64Recomp
# Function list -> recomp/thps1.syms.toml (committed: addresses/names only) and
# build/thps1.codeblob.bin (ROM-derived, local only). `make recomp` runs
# N64Recomp (set N64RECOMP=/path/to/N64Recomp) into build/recomp/funcs.
N64RECOMP ?= N64Recomp
recomp-inputs: baserom.main.bin
	$(PY) -I tools/gen_syms.py baserom.z64 baserom.main.bin $(BUILD)/thps1.codeblob.bin recomp/thps1.syms.toml

recomp: recomp-inputs
	rm -rf $(BUILD)/recomp/funcs && mkdir -p $(BUILD)/recomp/funcs
	$(N64RECOMP) recomp/thps1.recomp.toml > $(BUILD)/recomp/log.txt 2>&1 || (tail -5 $(BUILD)/recomp/log.txt; false)
	@grep -c "" $(BUILD)/recomp/log.txt >/dev/null; tail -2 $(BUILD)/recomp/log.txt
	@echo "warnings: $$(grep -c '^\[Warn\]' $(BUILD)/recomp/log.txt)"

clean:
	rm -rf $(BUILD)

distclean: clean
	rm -rf asm assets linker_scripts include baserom.main.bin
