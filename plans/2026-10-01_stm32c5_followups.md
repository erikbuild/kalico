# STM32C5 support: follow-ups

Items found while executing `plans/2026-10-01_stm32c5.md` that are real but outside its scope. Each has an owner.

| Item | Where | Owner |
|---|---|---|
| Codex fallback reviewer switches a `--base`/`--commit` review to the working tree; it should keep the requested target, its validation and the plans/ exclusion | `.claude/agents/codex-reviewer.md` (source: HART-CETEC-Admin-Tool kit) | Erik |
| `codex-review.sh` treats an unreadable `codex doctor` result as "not set up" (exit 3), which licenses a same-vendor fallback for a broken tool; unknown auth status should block (raised again by the final whole-branch review) | `scripts/codex-review.sh` lines ~99-107 (source: HART-CETEC-Admin-Tool kit) | Erik |
| `codex-review.sh` creates temp files with `mktemp` before normalizing `TMPDIR`; with `TMPDIR` inside the repo the temp file enters the review scope | `scripts/codex-review.sh` lines ~124-125 (source: HART-CETEC-Admin-Tool kit) | Erik |
| Pre-existing GCC warnings (54) in 9 non-stm32 test configs, identical line for line on main (aaaf2cc5): ar100 18 (src/ar100/util.{c,h}), src/generic/armcm_reset.c 2 in each of 5 configs, simulator 1, linuxprocess 4, same70q20b 21; no stm32 config warns | src/ar100, src/generic/armcm_reset.c, src/simulator, src/linux, src/atsam | Erik |
| STM32H723 SPI bus table was shifted one entry (unguarded PI1-PI3 route) so spi5/spi5a/spi6 mapped to the wrong pins; fixed on this branch by commit dfaaa145 — consider sending upstream (Klipper/Kalico) | src/stm32/stm32h7_spi.c | Erik |
| Shared usbfs.c `usb_init()` (F0/L4/G0/G4/AT32) releases USB reset right after clearing PDWN without the tSTARTUP wait the reference manuals require; fixed for stm32c5 only on this branch | src/stm32/usbfs.c (kalico + katapult) | Erik |
| One of five full Katapult `test-build.sh` runs under `scripts/docker-run.sh` failed to link stm32f0.config because `out/src/generic/armcm_canboot.o` was written with a page-aligned 577,536-byte zero run and an all-zero string table (serial build, each object compiled once; the same command passed on rerun; a container build without the bind mount links fine). Mechanism unknown; suspected Docker Desktop host bind mount under amd64 emulation while another container was compiling. GitHub CI does not use this mount | `scripts/docker-run.sh` local builds | Erik |
