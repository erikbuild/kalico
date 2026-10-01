# Katapult anatomy — what an STM32C55xxx port would touch

Research date: 2026-10-01. Read-only with respect to `/Users/erik/Code/kalico`.

**Sources**
- Katapult clone: `scratchpad/katapult` (`git clone --depth 200`), HEAD = `ada29fd` (2026-10-01, "rp2040: add RP2350 A4 stepping support"). The 200-commit window reaches back to `9c6e72e` (2022-05-04), which covers every chip-family addition. All `file:line` references below are against `ada29fd` unless marked otherwise.
- GitHub API (`gh api`): all 194 Katapult issues and PRs, saved to `scratchpad/research/katapult_issues.json` and `scratchpad/research/katapult_prs.tsv`. Branches: `master`, `dev-canbus-updates-20220629`, `dev-sdcard-20220519`.
- STM32C5 datasheet digest: `/Users/erik/Code/kalico/digest-docs/digest/st/STM32C55xxx_Datasheet.md`.
- ST CMSIS device pack for C5: `github.com/STMicroelectronics/stm32c5xx-dfp` @ `a5f65bc` (this is the `stm32c5xx_dfp` submodule of `STMicroelectronics/STM32CubeC5`). Headers were downloaded to `scratchpad/c5dfp/`. Line numbers marked "hdr:" refer to `scratchpad/c5dfp/stm32c552xx.h`.
- Kalico (read-only) was used to compare files that are shared between the two projects.

Anything labelled **[SPECULATION]** or **[VERIFY IN RM]** has not been confirmed from a primary source. The STM32C5 reference manual has not been read. Only the datasheet digest and the ST CMSIS header have.

---

## 0. TL;DR

1. **Katapult is a stripped-down fork of Klipper's MCU code.** Most of `src/stm32/*`, `src/generic/*`, and `lib/*` is copied from Klipper and kept in step by hand, through "sync/resync with Klipper" commits. No tooling automates this. Most of what makes Katapult different lives in a few files:
   - `src/{bootentry,flashcmd,sched,command,led,deployer}.c`
   - `src/generic/armcm_canboot.c`
   - `src/generic/armcm_link.lds.S` and `src/generic/armcm_deployer.lds.S`
   - the per-family `src/stm32/flash.c` branches
   - `src/stm32/Kconfig` (bootloader-specific menus)
   - `scripts/flashtool.py` and `scripts/buildbinary.py`
2. **A new STM32 family touches the following files:**
   - `src/stm32/Kconfig`, `src/stm32/Makefile`, `src/stm32/internal.h`
   - a new `src/stm32/stm32c5.c` (clock and startup)
   - a new `#if` branch in `src/stm32/flash.c`
   - family `#if`s in `usbfs.c`, `fdcan.c`, and `stm32f0_serial.c`
   - `lib/stm32c5/` (CMSIS device headers) and an entry in `lib/README`
   - `test/configs/stm32c5*.config` (CI builds every file in that directory)
   - optionally `README.md`

   The linker scripts, protocol code, deployer, and `flashtool.py` do not need family-specific changes.
3. **Katapult has no support for STM32C0, C5, H5, U5, or L4.** L412 is present in Kconfig but hidden with `if 0`. No branches, issues, or PRs mention C0, C5, H5, U5, M33, or TrustZone. A GitHub-wide code search finds no `MACH_STM32C5` in any repository. Upstream Klipper has no H5, C0, C5, or U5 port either.
4. **Katapult's generic ARM code already handles Cortex-M33.** RP2350 support added this in `c0014ef`:
   - `NVIC->IPR` and `SCB->SHPR` branches in `src/generic/armcm_boot.c:62-84`
   - `lib/cmsis-core/core_cm33.h`

   The C5 CMSIS header compiles cleanly against Katapult's CMSIS 5 `core_cm33.h` (clang `-fsyntax-only`, `thumbv8m.main`). The C5 has no TrustZone: hdr:177 sets `__SAUREGION_PRESENT 0`, there are no `_NS`/`_S` aliases, and the datasheet never mentions TrustZone. So no secure-state handling is needed.
5. **The C5 flash controller is a new branch, not a variant of an existing one.** Per the ST header and datasheet it has:
   - 8 KB pages, 2 banks (`FLASH_BANK_SIZE = FLASH_SIZE/2`), page selected with `BKSEL` + `PNB[5:0]`
   - 128-bit (quad-word) programming
   - registers named `FLASH->KEYR`, `SR`, `CR`, and `CCR`

   It looks like the STM32H5 flash controller and matches none of Katapult's four existing branches.
6. **Two existing problems directly affect a C5 port.**
   - Open issue **#192**: `check_erased()` in `src/stm32/flash.c:46` only checks ¼ of the range. With 8 KB pages it checks 2 KB.
   - **SRAM retention across reset.** The bootloader request and double-reset detection rely on a magic value in the last 8 bytes of RAM surviving `NVIC_SystemReset`. The C5 has `SRAM1_RST`/`SRAM2_RST` (erase on system reset) and `SRAM2_ECC` option bits (hdr:5446-5473). Placement, polarity, and factory defaults need RM confirmation.

---

## 1. Repo layout and the relationship with Klipper

### 1.1 Layout (`ada29fd`)

| Path | Role | Origin |
|---|---|---|
| `Makefile`, `src/Makefile` | Build. Produces `katapult.bin` (plus a `canboot.bin` copy) and an optional `deployer.bin` | Klipper build system, adapted. `772817b` "build: sync Makefile with Klipper" |
| `src/Kconfig` | Top menu: architectures, USB/CAN/serial, optimisation, double-reset, button, LED, `BUILD_DEPLOYER` | Klipper's `src/Kconfig` plus Katapult options (`e3e72b8` resync) |
| `src/{sched,command,bootentry,flashcmd,initial_pins,led,deployer}.c` | Katapult core | Katapult. `sched.c` and `command.c` are written in Klipper's style but are much smaller (`83ecbcc`, `db6a9b4`, `799fe53`) |
| `src/canboot.h` | Magic constants and boot API | Katapult (`d30ad28`) |
| `src/generic/armcm_canboot.c` | Bootloader reset handler, magic handling, app launch | Katapult (`2862801`, rewritten in `c0014ef`) |
| `src/generic/armcm_boot.c`, `armcm_reset.c` | Klipper-style reset handler and "request Katapult" function. **Used only by the deployer** | Klipper (`armcm_boot.c` is byte-identical to Kalico's) |
| `src/generic/armcm_link.lds.S`, `armcm_deployer.lds.S` | Linker scripts | Klipper-derived. The bootloader script reserves 8 bytes at the top of RAM |
| `src/generic/{usb_cdc,canbus,canserial,serial_irq,armcm_timer,armcm_irq,crc16_ccitt,alloc}.c` | Transports, timer, IRQ | Klipper (see §1.3) |
| `src/stm32/*` | STM32 HAL: clocks, GPIO, USB, CAN, FDCAN, serial, **flash.c** | Klipper, except `flash.c` (Katapult) and the Kconfig bootloader/app-offset menus |
| `src/lpc176x/*`, `src/rp2040/*` | Other architectures | Klipper plus Katapult `flash.c`. rp2350 adds `rp2350_dblreset.c` |
| `lib/*` | Vendor headers (CMSIS, ST, pico-sdk), kconfiglib, can2040, fast-hash | Vendor packages; provenance recorded in `lib/README` |
| `scripts/flashtool.py` | Host-side flasher (formerly `flash_can.py`; symlink added in `817a665`) | Katapult |
| `scripts/buildbinary.py` | Size check and deployer payload generator | Katapult (`d6c874b`, `f4ac647`) |
| `scripts/buildcommands.py` | Compile-time request processor (vector table, LED/button pins, initial pins) | Klipper-derived, heavily trimmed (679 diff lines vs Kalico) |
| `test/configs/*.config`, `scripts/test-build.sh`, `.github/workflows/test-build.yaml` | CI build matrix (`fcb2f84`, 2025-05-22) | Katapult |
| `protocol.md` | Wire protocol | Katapult |

### 1.2 How Katapult stays in sync with Klipper

- **No automation.** Sync happens through manual commits that typically say "sync"/"resync" and name Klipper:
  - `3e3ca24` stm32: sync low level code with klipper (2024-08-05)
  - `94e4255` stm32: sync stm32h7 and Kconfig updates from Klipper (2025-05-31)
  - `43eb9ad` stm32: add stm32g4.c from klipper
  - `c0014ef` rp2040: Resynchronize with upstream Klipper code and support rp2350 chips
  - `bcff5ca` / `3076dd0` / `6f67a01` / `da7cc96` / `6a233ff` / `2b22438` / `e3e72b8`: the 2022-12 "Resync … with upstream Klipper code" series (PR #56)
  - `3855b34` sync fdcan, `a06bf61` sync can.c, `67020a4` sync can2040, `d0480d2` sync usbserial fix
  - `c055ff1` lpc176x: add source from Klipper, then `365c3bb` lpc176x: remove code specific to Klipper
- **Documentation.** README.md:5-8 says the bootloader "makes use of Klipper's hardware abstraction layer, stripped down". README.md:22 says "Katapult also uses Klipper's build system". README.md:215 says "Katapult is effectively a fork of Klipper's MCU source". Commits follow Klipper's format (`file: description` plus a DCO `Signed-off-by`; README.md:213-229).
- **`lib/README`** records the upstream versions (CMSIS_5 5.7.0, STM32CubeG4 v1.4.0, STM32CubeH7 v1.9.0, and so on; `lib/README:3-90`). `core_cm33.h` came with the rp2350 sync (`c0014ef`), even though `lib/README` still lists CMSIS 5.7.0. Its own header says V5.2.0 (`lib/cmsis-core/core_cm33.h:4`).
- **The "hidden chip" pattern.** When Kconfig is resynced from Klipper, chips without a Katapult flash driver are kept but hidden: `bool "STM32xxx" if 0`. A chip is enabled by removing `if 0` once `flash.c` supports it.
  - `bcff5ca` added G431, H723, and L412 as hidden.
  - `88e208a` unhid H723/H743.
  - `cdb5b56` unhid G431.
  - `66b9b00` unhid H750, `902f335` reverted that ("requires additional work to support flash writes"), and `32584cb` re-enabled it.
  - `src/stm32/Kconfig:87-89` still has `MACH_STM32L412 … if 0`.
- **Maintainer signal [not a written policy].** On 2026-10-01, Arksine commented on open PR #189 (N32G45x): *"Am I correct that all pending work has been merged in Klipper? If so, I'll merge this and its companion PR."* This suggests new-chip PRs are expected to follow the upstream Klipper port. A C5 port that exists only in Kalico may get more scrutiny. **[SPECULATION]**
- **Kalico is not Klipper.** Kalico's `lib/README:169-173` vendors CanBoot's old `flash_can.py` (rev `8702008…`). Upstream Klipper's `src/stm32/` has no H5, C0, C5, or U5 files (checked with `gh api repos/Klipper3d/klipper/contents/src/stm32`).

### 1.3 How far the shared files have drifted (Katapult `ada29fd` vs `/Users/erik/Code/kalico` HEAD)

Count of differing lines (`diff | grep -c '^[<>]'`):

| 0 (identical) | small | large |
|---|---|---|
| `src/stm32/{usbotg.c, gpio.c, clockline.c}` | `usbfs.c` 3 (AT32 guard) | `src/stm32/Kconfig` 219 |
| `src/generic/{armcm_boot.c, armcm_irq.c, canbus.c, crc16_ccitt.c, misc.h, alloc.c}` | `stm32g0.c` 2, `stm32h7.c` 3 (comments only) | `src/stm32/Makefile` 98 |
| `src/initial_pins.c` | `internal.h` 3 (F7, `GPIO_HIGH_SPEED`) | `armcm_timer.c` 137 (Klipper version adds timer IRQ dispatch) |
| `lib/cmsis-core/core_cm33.h` | `stm32g4.c` 15 (Kalico adds 25 MHz PLL base and boost mode) | `sched.c` 344, `command.c` 353 (Katapult-specific) |
| | `gpioperiph.c` 8, `chipid.c` 10, `stm32f0_serial.c` 8 | `canserial.c` 98, `fdcan.c` 51, `can.c` 48 |
| | `armcm_link.lds.S` 11 (Katapult: ORIGIN = FLASH_START, 8-byte `.reserved`) | `armcm_reset.c` 39 (Katapult: unconditional request) |

**Takeaway [inference]:** a C5 clock file, `usbfs.c` and `fdcan.c` changes, `gpioperiph.c`, and `lib/stm32c5` written for Kalico would port to Katapult almost verbatim. Two exceptions:
- Katapult's `stm32g4.c` is older than Kalico's, so check what Katapult's `stm32xx.c` files expect (no `timer_irq.c`, no watchdog, and so on).
- `flash.c`, `Kconfig`, and `Makefile` are Katapult-specific.

### 1.4 Katapult-specific mechanisms

**Boot flow** (bootloader build, ARM):

1. **Reset vector.**
   - `ResetHandler` is a 1-instruction stub preceded by the 8-byte signature `CANBOOT_SIGNATURE` ("CanBoot!") (`src/generic/armcm_canboot.c:138-147`).
   - It branches to `reset_handler_stage_two` (`armcm_canboot.c:110-135`).
2. **Stage two:** the app-start shortcut.
   - It reads the 64-bit "bootup code" from `_stack_end`, which is the last 8 bytes of configured RAM (`armcm_canboot.c:26-31`).
   - If the code is `REQUEST_START_APP` (`src/canboot.h:8`), it clears the code, sets `SCB->VTOR = CONFIG_LAUNCH_APP_ADDRESS`, loads MSP from the app's vector[0], and `bx`'s to vector[1] (`armcm_canboot.c:76-85`). **This happens before `.data`/`.bss` init and before any clock or peripheral setup.** The application therefore always starts from a near-reset chip state.
   - Otherwise it initialises `.data`/`.bss` and calls `armcm_main()` (the per-family clock file).
3. **`armcm_main()`** (for example `src/stm32/stm32g4.c:169-181`) runs:
   - `dfu_reboot_check()`, which is a stub (`src/stm32/dfu_reboot.c:10-19`)
   - `SystemInit()` (optional)
   - `SCB->VTOR = VectorTable`
   - `clock_setup()`
   - `sched_main()`
4. **`sched_main()`** (`src/sched.c:54-70`) calls `timer_setup()` and then `bootentry_check()`. If that returns 0, it calls `application_jump()`. Otherwise it runs the init functions and loops over the task functions forever.
5. **`bootentry_check()`** (`src/bootentry.c:54-68`) enters the bootloader if any of these hold:
   - the bootup code equals `REQUEST_CANBOOT` (`canboot.h:7`)
   - `!application_check_valid()`: the word at `LAUNCH_APP_ADDRESS` is 0 or 0xffffffff (`armcm_canboot.c:60-65`)
   - the button GPIO is active (`bootentry.c:21-29`)

   Otherwise it runs `check_double_reset()` (`bootentry.c:31-51`). This waits 10 ms, writes `REQUEST_CANBOOT` into the RAM slot, and waits until 500 ms total. If the user presses reset during that window, the next boot sees the request. If not, it clears the slot and returns 0. Boards can override this with `CONFIG_HAVE_BOARD_CHECK_DOUBLE_RESET` (`src/Kconfig:151-153`); rp2350 does, using a POWMAN register in `src/rp2040/rp2350_dblreset.c:15-31`.
6. **`application_jump()`** (`armcm_canboot.c:68-74`) runs `irq_disable`, sets the bootup code to `REQUEST_START_APP`, and calls `NVIC_SystemReset()`. The app is therefore always launched through a full system reset.

**The RAM magic slot.**
- `src/generic/armcm_link.lds.S:60-70` places `_stack_start = RAM_START + RAM_SIZE - STACK_SIZE - 8`, the stack, and then an 8-byte `.reserved` section. `_stack_end` (vector[0], the initial MSP) is that reserved slot.
- Kalico's side (`/Users/erik/Code/kalico/src/generic/armcm_reset.c:17-42`) reads Katapult's vector table:
  - It checks `*(bl_vectors[1] - 9) == CANBOOT_SIGNATURE` (the signature sits directly before the Thumb `ResetHandler`).
  - It writes `CANBOOT_REQUEST` (or `CANBOOT_BYPASS` for a plain `reset` command) to `bl_vectors[0]`.
  - It then calls `NVIC_SystemReset()`. A cache clean happens only for `__CORTEX_M == 7`.
- **Consequence:** the slot must survive a system reset. Katapult's own deployer uses the same mechanism (`src/generic/armcm_reset.c:14-25`). Precedent: on H7, `RAM_START` is moved to AXI SRAM "to persist reboot flag" (`src/stm32/Kconfig:186-189`).

**Flash protocol** (`protocol.md`, `src/command.h:26-35`, `src/flashcmd.c`):
- Framing: `0x01 0x88 cmd len payload crc16 0x99 0x03`.
- Commands: CONNECT 0x11, SEND_BLOCK 0x12, EOF 0x13, REQUEST_BLOCK 0x14, COMPLETE 0x15, GET_CANBUS_ID 0x16. Protocol version 1.1.0.
- CONNECT replies with app start address, block size, `CONFIG_MCU`, and the Katapult version (`flashcmd.c:18-34`).
- SEND_BLOCK rejects addresses below `CONFIG_LAUNCH_APP_ADDRESS` (`flashcmd.c:92`), so the bootloader cannot overwrite itself.
- COMPLETE jumps to the app 100 ms after the ack (`flashcmd.c:44-59`).

**Status LED** (`src/led.c:14-43`): a 1 s blink while waiting and a 20 ms blink during transfer. Pins are resolved by `buildcommands.py`.

**Deployer** (`src/deployer.c:64-106`, Makefile:94-104, `scripts/buildbinary.py:16-37`):
- A second image is linked at the old bootloader's `FLASH_APPLICATION_ADDRESS` (`armcm_deployer.lds.S:14`). It is padded so that its code starts at `LAUNCH_APP_ADDRESS` (`armcm_deployer.lds.S:25-27`).
- It embeds `katapult.bin` and writes it to `FLASH_START` using the same `flash_write_block()`.
- It then calls `try_request_canboot()`.
- It reuses the Klipper-style `armcm_boot.c` and `armcm_reset.c`.

**Size guard:** `buildbinary.py:56-67` fails the build if `katapult.bin` is larger than `LAUNCH_APP_ADDRESS - FLASH_START`.

---

## 2. What a new STM32 family requires

### 2.1 `src/stm32/Kconfig`

| Item | Lines | What to add for C5 |
|---|---|---|
| Processor choice | 27-90 | `config MACH_STM32C551` and `MACH_STM32C552`, each `select MACH_STM32C5`. Add `if 0` until `flash.c` supports them |
| Family bools | 96-117 | `config MACH_STM32C5 bool` |
| `HAVE_STM32_USBFS` | 118-121 | add `MACH_STM32C5` (USB DRD FS) |
| `HAVE_STM32_FDCANBUS` | 128-130 | add `MACH_STM32C552` (C551 has no FDCAN, datasheet §3.26) |
| `MCU` string | 134-153 | `"stm32c551xx"` / `"stm32c552xx"`. **Must equal Kalico's `CONFIG_MCU`** (see §5). The Makefile turns this into `-DSTM32C552xx`, which matches ST's `stm32c5xx.h` selector |
| `CLOCK_FREQ` | 155-168 | `144000000` |
| `FLASH_SIZE` | 170-180 | Used only as the linker `rom` length. Use `0x40000`, the smallest C5 size (xC = 256 KB); this is the conservative pattern G0/G4 use |
| `FLASH_BOOT_ADDRESS` | 182-184 | `0x8000000`. **[VERIFY]** C5 `BOOTADD` option bytes default to 0x08000000 (datasheet §3.5; hdr `FLASH_BOOTR_*_BOOTADD`) |
| `RAM_START` / `RAM_SIZE` | 186-204 | `0x20000000` / see §6.3 (`0x10000` for SRAM1 only vs `0x20000`) |
| `STM32_DFU_ROM_ADDRESS` | 220-227 | Not functionally used (`dfu_reboot.c` is a stub). The C5 system flash is at `0x0BF80000` (hdr:1122). Whether the ROM vector table is there is **[VERIFY]** |
| Deployer choice "Build Katapult deployment application" | 234-262 | Add C5 to `STM32_FLASH_START_2000` ("8KiB bootloader") if replacing an existing bootloader is wanted. This choice defines `FLASH_APPLICATION_ADDRESS` (263-277) and so `BUILD_DEPLOYER` (`src/Kconfig:141-144`) |
| `ARMCM_RAM_VECTORTABLE` | 279-282 | Not needed (F0 only; M33 has VTOR) |
| Clock reference | 289-317 | The existing choices are 8/12/16/20/24/25/32 MHz/internal. C5 HSE is 4-50 MHz, so any of them works. The internal reference is HSI144 |
| Comm-interface choice | 333-427 | USART1 PA10/PA9 uses AF7 on C5 (datasheet Table 13 rows PA9/PA10). FDCAN1 is AF9 on PA11/PA12, PB8/PB9, PD0/PD1, PB12/PB13, PB5/PB6 and others (datasheet lines 1809-1861). **PB0/PB1, PC2/PC3, PD12/PD13, and PH13/PH14 have no FDCAN on C5**, so those options must be excluded for C5 |
| App start offset choice | 495-507 | Add C5 to `STM32_APP_START_2000` (8 KiB) and probably a 16 KiB option. **Not 4 KiB:** the page is 8 KB and the app must start on a page boundary (see §2.3) |
| `LAUNCH_APP_ADDRESS` | 509-516 | Existing values cover 0x8002000 and 0x8004000 |
| `BLOCK_SIZE` | 518-520 | 64 (a multiple of the 16-byte quad-word) |

### 2.2 `src/stm32/Makefile` (and `internal.h`)

The template is the G4 enablement (`cdb5b56`), reorganised by `3f84643` and `287c9e1`:

```
dirs-$(CONFIG_MACH_STM32C5) += lib/stm32c5                                   # Makefile:7-13
CFLAGS-$(CONFIG_MACH_STM32C5) += -mcpu=cortex-m33 -Ilib/stm32c5/include      # Makefile:18-25 (rp2350 uses plain -mcpu=cortex-m33, soft-float)
mcu-$(CONFIG_MACH_STM32C5) += stm32/stm32c5.c                                # Makefile:34-40 — MUST be mcu-y, not src-y,
                                                                             #   or the deployer won't link (fix in 287c9e1)
serial-src-$(CONFIG_MACH_STM32C5) := stm32/stm32f0_serial.c                  # Makefile:48-53
# timer: default generic/armcm_timer.c (DWT->CYCCNT)                         # Makefile:41-43
# gpio:  default stm32/gpio.c stm32/gpioperiph.c                             # Makefile:44-46
# usb:   HAVE_STM32_USBFS -> stm32/usbfs.c                                   # Makefile:54-56
# can:   HAVE_STM32_FDCANBUS -> stm32/fdcan.c                                # Makefile:57-60
```

`src/stm32/internal.h:7-23`: add `#elif CONFIG_MACH_STM32C5` / `#include "stm32c5xx.h"`.

**System file:** ST's `system_stm32c5xx.c`:
- includes `<math.h>`
- references `__VECTOR_TABLE`, which `lib/cmsis-core/cmsis_gcc.h:177-178` maps to `__Vectors`, a symbol Katapult does not define. Katapult's generated table is `VectorTable` (`scripts/buildcommands.py:231`).
- only sets FPU and VTOR (`c5dfp/system_stm32c5xx.c:148-157`).

G0 is the precedent for skipping the system file (Makefile:38, and there is no `lib/stm32g0/system_*.c`). **[SPECULATION]** Omit it for C5.

### 2.3 `src/stm32/flash.c`: the per-family branches

The structure is shared. Only the hardware hooks are `#if`'d per family.

- `flash_get_page_size()`: lines 14-40
- `check_erased()`: 43-51
- register-name remaps: 53-60
- `wait_flash()` (`SR & FLASH_SR_BSY`): 63-68
- default keys `0x45670123`/`0xCDEF89AB` if the header lacks `FLASH_KEY1`: 70-73
- `unlock_flash()` (two `KEYR` writes if `CR & FLASH_CR_LOCK`): 76-85
- `lock_flash()` (`CR = FLASH_CR_LOCK`): 88-92
- `erase_page()`: 95-133
- `write_block()`: 136-179
- `flash_write_block()`: 184-240. Blocks must be aligned. The first block of a page decides whether the page needs an erase. The retransmit check comes next. Then it unlocks, erases, and for H7 only does a lock/unlock pair after the erase (`25482ba`). Then it writes, locks, and reads back with `memcmp` (`-3` on mismatch).
- `flash_complete()`: 243-247

| Family | Page / sector size (lines 14-40) | Erase (95-133) | Program width (136-179) | Dual-bank | Cache handling |
|---|---|---|---|---|---|
| F0, F1 | F103: 1 KB or 2 KB depending on `FLASHSIZE_BASE` (<256 KB → 1 KB). F042 1 KB, F072 2 KB, other F0 by flash size | `CR=PER; AR=addr; CR=PER\|STRT` | half-word (16-bit) `writew`, wait after each | n/a | none |
| F2, F4 | 16 K ×4, 64 K, then 128 K sectors | `CR = PSIZE_1\|STRT\|SER\|(snb<<SNB)`. Sector index computed from address, capped at 0x0f | word (32-bit), `PSIZE_1`, wait after each | not handled (single-bank sector map) | none |
| G0, G4 (shared) | 2 KB | `CR = PER\|STRT\|(pidx<<PNB)`. For pidx ≥ 64: if flash ≤ 256 KB, `pidx += 256-64`, else `pidx<128 ? pidx : pidx+256-128` (G0B1 dual-bank page numbering). Capped at 0x3ff | double-word (2×32-bit), wait after each pair | **G0B1 bank-2 remap only** (lines 115-121). Open PR **#181** says this arithmetic is wrong for G474 above 128 KB and splits G0 and G4 | none (G4 `ACR` ICEN/DCEN are left on) |
| H7 | 128 KB sectors | `CR = SER\|START\|(snb<<SNB)`, wait `QW`, `SCB_InvalidateDCache_by_Addr(page,128K)`. Only bank 1 (`snb` capped at 7) | flash-word 256-bit (8×32-bit), wait `QW` then BSY, D-cache invalidate after the block | **bank 1 only** (`CR1/SR1/KEYR1` remap at 56-59) | D-cache invalidate after erase and program. The magic slot gets `SCB_CleanDCache_by_Addr` (`armcm_canboot.c:39-41`, `armcm_reset.c:21-23`) |

**What C5 needs.** These register facts come from the ST header; the sequence is **[SPECULATION, VERIFY IN RM]**.
- **Registers.**
  - `FLASH->ACR` 0x000, `KEYR` 0x004, `SR` 0x020, `CR` 0x028, `CCR` 0x030, `OPTSR_CUR` 0x050 (hdr:470-526).
  - The names match `flash.c`'s generic `FLASH->CR/SR/KEYR`, so no H7-style remap is needed.
  - `FLASH_KEY1/2` are not defined in the header, so the fallback at `flash.c:70-73` applies. Verify the key values.
- **Bits.**
  - `SR`: `BSY` b0, `WBNE` b1, `DBNE` b3, `EOP` b16, `WRPERR` b17, `PGSERR` b18, `STRBERR` b19, `INCERR` b20, `OPTCHANGEERR` b23.
  - `CR`: `LOCK` b0, `PG` b1, `PER` b2, `BER` b3, `FW` b4, `STRT` b5, `PNB[5:0]` b6-11, `MER` b15, `EDATASEL` b29, `BKSEL` b31.
  - `CCR`: `CLR_*` for the `SR` flags.
  - (hdr:5186-5318)
- **Geometry.**
  - `FLASH_PAGE_SIZE 0x2000` (8 KB). `FLASH_BANK_SIZE = FLASH_SIZE >> 1`, so 256 KB per bank on xE and 128 KB per bank on xC (hdr:5059-5089).
  - Datasheet §3.4.1 ("each bank contains 32 pages of 8 Kbytes") describes the 512 KB part.
  - `FLASHSIZE_BASE = 0x08FFF80C` (hdr:1114).
- **Program unit.** 128 bits in the user area (datasheet Table 40). So a 64-byte block is 4 quad-words: write 4 words, then wait until `!(SR & (BSY|WBNE|DBNE))`.
- **Erase.**
  - `bank = (addr-0x08000000) >= bank_size`, `pnb = ((addr-0x08000000) % bank_size) / 8K`
  - `CR = PER | (bank ? BKSEL : 0) | (pnb << PNB_Pos)`, then set `STRT`. Whether `STRT` may be set in the same write is **[VERIFY]**.
  - If `OPTSR_CUR.SWAP_BANK` (hdr:5387-5389) is set, the bank mapping may be swapped **[VERIFY]**.
- **Error flags.** Clear them via `FLASH->CCR` before each operation.
  - Precedent: closed-unmerged PR **#187** ("stm32: clear H7 flash status before operations") reported that ACK_ERROR on an occupied H723 sector was fixed by clearing stale `FLASH_CCR1` flags.
  - Sticky `PGSERR`/`INCERR` blocking later operations is typical of H5-style controllers **[SPECULATION]**.
- **ICACHE.**
  - Datasheet §3.2: ICACHE sits on the C-AHB bus and caches "instruction and data from internal memories". CPU data reads of 0x08xxxxxx (`check_erased`, `memcmp` verify, `application_read_flash`) go through it.
  - If the C5 clock file never enables ICACHE, there is nothing to invalidate. If it does, invalidate after each erase and program, the way H7 does with the D-cache. The reset state is believed to be disabled **[VERIFY]**.
- **No dual-bank surprises if the app fits in bank 1.** A 256 KB xC part has bank 2 at 0x08020000. Klipper/Kalico images bigger than about 120 KB would cross into bank 2. **[inference]**
- **App start must be page-aligned.** `flash_write_block` erases only when `block_address` is the first block of a page (`flash.c:195-206`). An app start that is not page-aligned would never erase its first page, and writes would fail with `-2`/`-3`. Writes below `LAUNCH_APP_ADDRESS` are refused (`flashcmd.c:92`). So C5 app offsets must be multiples of 8 KiB. **[inference from code]**

### 2.4 Per-family clock/startup file contract (`src/stm32/stm32??.c`)

Declared in `src/stm32/internal.h:47-51` and `src/generic/misc.h:21`. G4 is the cleanest template (`src/stm32/stm32g4.c`).

- `struct cline lookup_clock_line(uint32_t periph_base)`: g4.c:19-61.
  - C5 RCC has `AHB1ENR, AHB2ENR, APB1LENR, APB1HENR, APB2ENR, APB3ENR` with matching `*RSTR`, plus `CCIPR1/2` and `CR1/CR2/CFGR1/CFGR2` (hdr:719-762). The layout looks like H5.
- `uint32_t get_pclock_frequency(uint32_t)`: g4.c:64-68
- `void gpio_clock_enable(GPIO_TypeDef*)`: g4.c:71-77. C5 `GPIOA_BASE = AHB2PERIPH_BASE` (hdr:1199).
- `void bootloader_request(void)`: g4.c:157-161. Only `dfu_reboot()` (a stub) is called. The other families call `try_request_canboot()` first, which is harmless.
- `void armcm_main(void)`: g4.c:169-181. It calls `dfu_reboot_check()`, optionally `SystemInit()`, sets `SCB->VTOR = (uint32_t)VectorTable`, calls `clock_setup()`, then `sched_main()`.
  - G0 and H7 also reset the RCC enable and `CCIPR` registers in case a previous bootloader left them set (g0.c:169-181, h7.c:213-223).
- `DECL_CONSTANT_STR("RESERVE_PINS_crystal", …)`: harmless in Katapult.
- C5 clock specifics (datasheet §3.8, §3.9):
  - The chip resets on HSI 144 MHz. PSI can produce 100/144/160 MHz. AHB/APB maximum is 144 MHz.
  - There is no PLL in the datasheet description; the PSI replaces it. **[VERIFY]**
  - CRS trims HSI from USB SOF.
  - `FLASH_LATENCY_DEFAULT` is 3 WS (hdr:5052).
  - USB clock source selection is **[VERIFY IN RM]**.

### 2.5 Peripheral drivers that need C5 `#if`s

- **`src/stm32/usbfs.c:18-54`.**
  - C5 uses `USB_DRD_FS` (hdr:1292), `USB_DRD_PMAADDR` (hdr:1165), `USB_CHEP_*`, `USB_CNTR_USBRST`, `USB_ISTR_IDN`, and `USB_BCDR_DPPU`. The naming is the same as G0.
  - The IRQ is `USB_DRD_FS_IRQn = 62`.
  - The PMA is 2048 bytes. Its access width is 32-bit on G0-style DRD. Expected for C5 as well **[VERIFY]**.
  - In practice, extend the `CONFIG_MACH_STM32G0` branches (`WSIZE 4`, `uint32_t epmword_t`, renames) and `#define USB_IRQn USB_DRD_FS_IRQn`.
- **`src/stm32/fdcan.c:63-85, 176-183, 307-315`.**
  - C5 has a G0/G4-style FDCAN: 0.8 KB message RAM (datasheet §3.26), `FDCAN_RXGFC_LSS_Pos` (hdr:4895), `SRAMCAN_BASE` (hdr:1154), `FDCAN1_IT0_IRQn = 34`, AF9.
  - Add C5 to the `G0 || G4` `RXGFC` path and the `H7 || G4` IRQ/AF path.
  - **Instance mapping:** `fdcan.c:63-76` sends PB0/PB1, PC2/PC3, PB5/PB6, and PB12/PB13 to **FDCAN2**. On C5, PB5/PB6 and PB12/PB13 are **FDCAN1**, and FDCAN2 does not exist.
- **`src/stm32/stm32f0_serial.c:15-125`.**
  - USART1/2/3 are AF7 on C5. Extend the `(CONFIG_MACH_STM32H7 | CONFIG_MACH_STM32G4) ? 7 : 1` expressions.
  - The header already defines both `USART_ISR_RXNE` and `USART_ISR_RXNE_RXFNE` (hdr:12979-12991).
  - It lacks `USART_BRR_DIV_MANTISSA_Pos`, so add the G4-style `4/0` defines (lines 116-120).
- **`src/stm32/gpio.c` and `gpioperiph.c`:** generic. The comment table of `OSPEEDR` values could gain a C5 line.
- **`src/stm32/chipid.c`:** uses `UID_BASE` (C5: `0x08FFF800`, hdr:1113). No change needed.
- **`src/generic/armcm_timer.c:33-44`:** uses `DWT->CYCCNT` and `CoreDebug->DEMCR`. Both exist in Katapult's `core_cm33.h` (`CoreDebug` is deprecated but present) and compile for C5. Whether CYCCNT is implemented on C5's M33 is **[VERIFY]**. rp2350 (also M33) uses this timer.

### 2.6 Linker scripts

There are no per-family linker scripts. `armcm_link.lds.S` uses `FLASH_START`, `FLASH_SIZE`, `RAM_START`, and `RAM_SIZE`. `armcm_deployer.lds.S` uses `FLASH_APPLICATION_ADDRESS`. Nothing to add for C5.

### 2.7 Deployer support

This needs only:
- the clock file in `mcu-y` (§2.2)
- a `STM32_FLASH_START_xxxx` option that includes C5 (`Kconfig:234-262`)

`87eb491` ("stm32: add deployer option for stm32g0") is a one-line Kconfig change of exactly this kind.

### 2.8 lib, tests, and docs

- `lib/stm32c5/include/`: `stm32c5xx.h`, `stm32c551xx.h`, `stm32c552xx.h`, `system_stm32c5xx.h` from `STMicroelectronics/stm32c5xx-dfp` (`Include/`). Record the provenance in `lib/README` (template: `dd69900`).
  - `stm32c5xx.h` includes `stm32_external_env.h` only when `USE_EXTERNAL_ENV` is defined, so that file is not needed.
  - Each per-chip header is about 1.1 MB.
- `test/configs/stm32c5.config` and `stm32c5-canbus.config`. `scripts/test-build.sh` builds every `test/configs/*.config` in CI (`.github/workflows/test-build.yaml`).
- README.md:10-11 support statement. It is already stale: it still says CAN is "limited to stm32 F-series, rp2040, and rp2350".

---

## 3. Recent commits that added STM32 families or variants, and the files they touched

| Commit | Date | Author | Subject | Files |
|---|---|---|---|---|
| `32584cb` | 2026-03-05 | wildBill83 | stm32: enable support for the STM32H750 (PR #177) | `src/stm32/Kconfig` (unhide, 480 MHz `CLOCK_FREQ`, 32 KiB app/deployer offsets) |
| `902f335` / `66b9b00` | 2025-10 | Arksine | enable, then revert, stm32h750 ("requires additional work to support flash writes") | `src/stm32/Kconfig` |
| `94e4255` | 2025-05-31 | Arksine | sync stm32h7 and Kconfig updates from Klipper | `src/stm32/Kconfig`, `src/stm32/stm32h7.c` |
| **G431 set (PR #165 plus follow-ups)** | | | | |
| `dd69900` | 2025-05-16 | K. O'Connor | lib: Add stm32g4 system definition files | `lib/README`, `lib/stm32g4/include/*.h` (12), `lib/stm32g4/system_stm32g4xx.c` |
| `3f84643` | 2025-05-16 | K. O'Connor | stm32: Minor organizational change to Makefile | `src/stm32/Makefile` |
| `cdb5b56` | 2025-05-16 | K. O'Connor | stm32: Add support for stm32g431 chips | `src/stm32/Kconfig` (unhide G431, 8 KiB app offset), `src/stm32/Makefile` (dirs/CFLAGS/src/serial), `src/stm32/flash.c` (G4 joins G0 branches) |
| `43eb9ad` | 2025-05-20 | Arksine | stm32: add stm32g4.c from klipper (missing from PR) | `src/stm32/stm32g4.c` (new, 181 lines) |
| `a8e44fd` | 2025-05-20 | Arksine | stm32: remove timer_irq.c from build | `src/stm32/Makefile` |
| `287c9e1` | 2025-05-20 | Arksine | stm32: fix deployer build (`src-y` → `mcu-y`) | `src/stm32/Makefile` |
| `87eb491` | 2025-05-20 | Arksine | stm32: add deployer option for stm32g0 | `src/stm32/Kconfig` |
| `fcb2f84` | 2025-05-22 | Arksine | test: add katapult test build workflow (prompted by the G4 breakage) | `.github/workflows/test-build.yaml`, `scripts/test-build.sh`, `test/configs/*.config` (20) |
| **H7 (PR #57 / #56)** | | | | |
| `3076dd0` | 2022-12-15 | K. O'Connor | lib: Resync stm32h7 with upstream Klipper | `lib/README`, `lib/stm32h7/*` |
| `bcff5ca` | 2022-12-15 | K. O'Connor | stm32: Resync stm32 code with upstream Klipper code (adds G431/H723/L412 hidden) | `src/command.h`, `src/stm32/{Kconfig, Makefile, dfu_reboot.c, internal.h, serial.c, stm32f0.c, stm32f0_serial.c, stm32f0_timer.c, stm32f1.c, stm32f4.c, stm32g0.c}` |
| `88e208a` | 2022-12-15 | K. O'Connor | stm32: Add support for flashing stm32h7 boards | `src/generic/armcm_canboot.c` (D-cache clean), `src/generic/armcm_reset.c` (D-cache clean), `src/stm32/Kconfig` (unhide, `RAM_START=0x24000000`, 128 KiB app offset), `src/stm32/Makefile`, `src/stm32/flash.c` (H7 branch), `src/stm32/stm32h7.c` (new) |
| `25482ba` | 2023-07-10 | Robin Gay | flash.c: fix write error for STM32H72x (PR #78) | `src/stm32/flash.c` (lock/unlock after erase) |
| **Older** | | | | |
| `115582c` | 2022-05-16 | K. O'Connor | stm32: Add stm32g0 support | `src/stm32/Kconfig`, `src/stm32/Makefile`, `src/stm32/flash.c` (G0 branch), `src/stm32/stm32g0.c` (new) |
| `5cbc25d` | 2022-05-16 | K. O'Connor | stm32: Enable support for stm32f2 | `src/stm32/Kconfig`, `src/stm32/flash.c` |
| `1e6a2de` | 2022-05-16 | K. O'Connor | stm32: Enable support on other stm32f0 chips | `src/stm32/Kconfig`, `src/stm32/flash.c` |
| `fbf5930`, `c3c7940`, `d36b696` | 2022-05-13/14 | Arksine | stm32f4 flash ops, usbotg.c from klipper, enable F4 in Kconfig | `src/flashcmd.c`, `src/stm32/flash.c`, `src/stm32/flash.h`, `src/stm32/usbotg.c`, `src/stm32/Kconfig` |
| **Cortex-M33 precedent** | | | | |
| `c0014ef` | 2024-11-14 | K. O'Connor | rp2040: Resynchronize with upstream Klipper code and support rp2350 chips (PR #138) | `lib/cmsis-core/core_cm33.h` + `mpu_armv8.h` (new), `src/generic/armcm_boot.c` (M33 `IPR`/`SHPR`), `src/generic/armcm_canboot.c` (rewritten, `== 7` cache guard), `src/generic/armcm_irq.c`, `src/generic/armcm_reset.c`, `src/Kconfig`, `src/rp2040/*`, `lib/pico-sdk/*` |
| `aa37e30` | 2024-12-12 | K. O'Connor | rp2040: Add rp2350 specific mechanism for checking for double reset tap | `src/rp2040/rp2350_dblreset.c` (new), `src/rp2040/Kconfig`, `src/rp2040/Makefile` |

**Open PRs that add families (current templates):**
- **#189** (N32G45x): `README.md`, `src/stm32/{Kconfig, Makefile, flash.c, stm32f1.c}`, `test/configs/n32g45x{,-canbus}.config`.
- **#194** (GD32F425): `src/generic/usb_cdc.h`, `src/stm32/{Kconfig, Makefile, usbotg.c}`, `test/configs/gd32f425-*.config`.
- **#191** (GD32F303/E230): adds `lib/cmsis-core/core_cm23.h`, `lib/gd32e23x/*`, and a separate `src/stm32/gd32e230_flash.c`. This shows that a separate flash file per family is also an accepted shape.
- **#181** (G474): `src/stm32/{Kconfig, flash.c}`.

**Template for C5** (the G4 sequence with its follow-up fixes folded in):
- `lib/stm32c5/*` and `lib/README`
- `src/stm32/{Kconfig, Makefile, internal.h, flash.c, stm32c5.c, usbfs.c, fdcan.c, stm32f0_serial.c}`
- `test/configs/stm32c5*.config`
- README

---

## 4. Does Katapult already support C0, H5, U5, any M33 STM32, or C5?

- **Code:** No. `src/stm32/Kconfig:27-90` lists F0/F1/F2/F4/G0B0/G0B1/G431/H723/H743/H750 and a hidden L412. `lib/` holds `stm32f0`, `stm32f1`, `stm32f2`, `stm32f4`, `stm32g0`, `stm32g4`, and `stm32h7` only.
- **Branches:** `master`, `dev-canbus-updates-20220629`, `dev-sdcard-20220519`. None are chip-related.
- **Issues and PRs:** All 194 items were fetched and regex-searched (titles and bodies) for `stm32 c0|c5|h5|u5|u0|l4|l5`, part numbers (`c0xx`, `c5xx`, `h5xx`, `u5xx`, `c071`, `c092`, `c551`, `c552` and similar), `cortex-m33`, `m33`, `trustzone`, and `stm32c`. **There were no hits.** The two regex matches were false positives (#149 and #92 contain "STM32Cube…").
  - GitHub issue search for "C5", "C0", "H5", "U5", "M33", "stm32c5", "stm32h5", "stm32u5", and "trustzone" returned nothing relevant.
  - Chip requests that do exist: #124 (G431, now done), #109 (G473), #181 (G474 PR), #161 (G4 PR), #55 (H723), #189/#190 (N32G45x), #191/#194 (GD32).
- **Cortex-M33 in general:** yes, via RP2350.
  - `src/rp2040/Makefile:13` (`-mcpu=cortex-m33`)
  - generic M33 handling in `src/generic/armcm_boot.c:62-68,78-84`
  - `armcm_canboot.c:39` and `armcm_reset.c:21` were narrowed to `__CORTEX_M == 7`, so an M33 build does not call the Cortex-M7 cache API (`c0014ef`)
- **STM32C5 anywhere on GitHub (code search):** no `MACH_STM32C5` in any repository. C5 support exists in Zephyr (`dts/arm/st/c5/stm32c552.dtsi`) and stm32duino (`variants/STM32C5xx`, `system/Drivers/CMSIS/Device/ST/STM32C5xx`). These are useful references for flash and clock sequencing.
- **Upstream Klipper:** `src/stm32/` has no `stm32h5`, `stm32c0`, `stm32c5`, or `stm32u5`. `lib/` has F0/F1/F2/F4/F7/G0/G4/H7/L4 only.

---

## 5. How `scripts/flashtool.py` identifies the MCU

- **There are no per-MCU tables in Katapult's flashtool.** The MCU string comes from the device.
  - CONNECT returns `<proto ver><app start><block size><CONFIG_MCU>\0<KATAPULT_VERSION>` (`flashtool.py:273-312`; firmware side `flashcmd.c:18-34`).
  - `block_size` must be one of 64/128/256/512 (`flashtool.py:284`).
- **Binary vs device MCU check** (`6c836fc`, `604b7e5`): `_check_binary()` (`flashtool.py:228-251`) runs only if the firmware filename is exactly `klipper.bin`.
  - It scans every byte offset for a zlib-compressed JSON data dictionary and stops early when `"app" == "Klipper"`.
  - `connect_btl()` then raises if `klipper_dict["config"]["MCU"] != mcu_type` (`flashtool.py:304-312`).
  - **For Kalico:** Kalico sets `data["app"] = "Kalico"` (`/Users/erik/Code/kalico/scripts/buildcommands.py:652`). The early `break` never fires, but the last successfully decoded dict is still kept, so the MCU check still applies. Scanning the whole binary costs extra CPU. **[inference from code]**
  - **Consequence:** Katapult's `CONFIG_MCU` for C5 must equal Kalico's `CONFIG_MCU`, for example both `stm32c552xx`, or flashtool refuses to flash.
- **USB identification** (`flashtool.py:87-90`): Katapult is `1d50:6177`, Klipper is `1d50:614e`, gs_usb CAN bridge is `1d50:606f`. The manufacturer string is `"katapult"`, and the product string is `CONFIG_MCU` (`src/generic/usb_cdc.c:136-137`).
- **Only per-MCU heuristic:** `_has_double_buffering()` (`flashtool.py:1032-1035`). If the USB product string starts with `stm32` and characters [5:7] are not in `("f2","f4","h7")`, flashtool sends a priming dummy command. This is needed for the usbfs double-buffered bulk endpoints.
  - `"stm32c552xx"` gives `"c5"`, so it would prime. That is correct, because C5 uses the usbfs (USB DRD FS) driver, not usbotg.
- **CAN:** flashtool queries UUIDs through Klipper's admin CAN IDs (`CANBUS_CMD_QUERY_UNASSIGNED`, `SET_CANBOOT_NODEID`; `src/generic/canserial.c:115-117`). The UUID comes from the chip UID (`src/stm32/chipid.c`, `UID_BASE`). Nothing here is MCU-specific.

---

## 6. Cortex-M33 / TrustZone constraints for the C5

### 6.1 TrustZone

- **The C5 has no TrustZone.**
  - `stm32c552xx.h:176-187`: `__CM33_REV 0x0004`, `__SAUREGION_PRESENT 0U` ("SAU regions not present"), `__MPU_PRESENT 1`, `__VTOR_PRESENT 1`, `__NVIC_PRIO_BITS 4`, `__FPU_PRESENT 1`, `__DSP_PRESENT 1`.
  - There are no `_NS`/`_S` peripheral aliases, no GTZC, no `SECCR`/`NSCR` flash registers. The only `NSCR` is RNG's noise-source register.
  - The datasheet digest never mentions TrustZone. It lists only RDP, WRPG, and HDP (§3.4.1).
- So: no SAU setup, no secure-to-non-secure handoff, and no `-mcmse`. Katapult and the app run in the single available state. Whether the core reports itself as Secure or Non-secure without the Security Extension does not affect Katapult. The architecture detail is from memory and has not been checked against the ARMv8-M ARM.
- **HDP and BOOT_LOCK** exist (hdr `HDP1R/HDP2R`, `FLASH_BOOTR_*_BOOT_LOCK`). They are not used by Katapult. A misconfigured HDP area over 0x08000000 would hide Katapult after `HDP` is closed. **[note]**

### 6.2 What Katapult assumes about VTOR, the reset handler, and the jump

- **Katapult's own vector table** is generated by `scripts/buildcommands.py:213-235`. It goes in `.vector_table` at the start of `.text` (`armcm_link.lds.S:20-27`), so at `FLASH_START = 0x08000000`. vector[0] is `&_stack_end`, the magic slot.
- **`armcm_main` sets `SCB->VTOR = VectorTable`.** M33 has VTOR (`boot_start_application` guards with `#if __CORTEX_M > 0 || __VTOR_PRESENT`, `armcm_canboot.c:81`).
- **App launch** (`armcm_canboot.c:76-85`): `SCB->VTOR = LAUNCH_APP_ADDRESS`; `MSR msp, vtor[0]`; `bx vtor[1]`. This happens immediately after reset, with no clock or peripheral changes. Katapult does **not** touch `MSPLIM`/`PSPLIM` (ARMv8-M stack-limit registers, reset to 0) or `CPACR` (FPU).
  - The app must enable the FPU itself. Kalico's startup would do that if it uses hard-float.
  - The 8 KiB or 16 KiB app offsets satisfy VTOR alignment.
- **NVIC reset loop:** `armcm_boot.c:55-68` (deployer only) uses `NVIC->IPR` for `__CORTEX_M == 33`. The bootloader's `armcm_canboot.c` does not reset the NVIC, because it always enters from a hardware reset.
- **`irq_wait`** uses `wfi` on non-M7 cores (`armcm_irq.c:38-46`). Katapult's main loop never calls it. **[note]**
- **Compiler:** rp2350 builds with `-mcpu=cortex-m33 -mthumb` and the soft-float ABI (`src/rp2040/Makefile:13-14`). `__FPU_USED` is therefore 0. Use the same for C5.
- **ST's `SystemInit`** would only call `SCB_EnableFPU()` and `SCB_SetVTOR(__VECTOR_TABLE)` (`c5dfp/system_stm32c5xx.c:148-157`). Not needed (§2.2).

### 6.3 C5-specific RAM and boot-handshake risks

All of these are **[VERIFY IN RM]**.

1. **SRAM erase on system reset.**
   - `FLASH_OPTSR2_*_SRAM1_RST` ("SRAM1 erase upon system reset") and `SRAM2_RST` (hdr:5446-5469) exist. Their polarity and factory defaults are unknown. (On H5 they are active-low, with "not erased" as the factory default. That is from memory and **[SPECULATION]** for C5.)
   - If the slot's SRAM is erased on reset, all of these break: Kalico→Katapult requests, Katapult→app launch (`REQUEST_START_APP`), double-reset detection, and the deployer handoff.
   - This is the C5 equivalent of the H7 `RAM_START = 0x24000000` decision (`Kconfig:186-189`).
2. **SRAM2 ECC.**
   - `FLASH_OPTSR2_*_SRAM2_ECC` (hdr:5457-5473). SRAM1 is 64 KB at 0x20000000 and SRAM2 is 64 KB at 0x20010000 (hdr:1100-1106). The datasheet says "SRAM2: 64 Kbytes with optional ECC" (§3.4.2).
   - `get_bootup_code()` reads the slot **before** any RAM initialisation (`armcm_canboot.c:113`). If `RAM_SIZE = 0x20000` puts the slot at the top of SRAM2 and ECC is enabled, a cold-boot read of uninitialised SRAM2 may raise an ECC error or NMI. **[SPECULATION]**
   - Safest option: set `RAM_SIZE = 0x10000` so the slot is at the top of SRAM1 (0x2000FFF8). Kalico does not need the same `RAM_SIZE`, because it reads the slot address from Katapult's vector[0].
3. **BOOT0 / BOOTADD / EMPTY.**
   - Datasheet §3.5: BOOT0 selects user flash or the system bootloader, and `BOOTADD` (lockable via `BOOT_LOCK`) defines the user boot address.
   - `FLASH_ACR_EMPTY` exists ("Main Flash memory area empty (not reset by system reset)", hdr:5127-5131). Compare issue **#82**: STM32G0's default `nBOOT_SEL` disabled the BOOT0 pin once flash was programmed, which made reflashing Katapult over ROM DFU painful.
   - Confirm the C5 defaults so that "full chip erase, then flash Katapult over DFU" (README.md:69-72) works, and that re-entering ROM DFU later still works.
4. **ICACHE:** see §2.3. Leave it disabled in Katapult, or invalidate after flash operations.
5. **Bank swap** (`SWAP_BANK`): if set, address-to-bank mapping in `erase_page` must respect it, or Katapult should refuse to run. **[SPECULATION]**

---

## 7. Known Katapult bugs relevant to a C5 port

- **#192** (open, 2026-09-23): `check_erased()` at `src/stm32/flash.c:46` computes its end pointer as `(void*)addr + count / 4`, which is byte arithmetic. It checks only the first quarter of the range.
  - With 8 KB C5 pages, "page already erased" is decided from 2 KB.
  - The per-block out-of-order check looks at 16 of 64 bytes.
  - The final `memcmp` usually turns this into a failed write (`-3`) rather than silent corruption.
  - The fix is a one-liner: `(uint32_t*)addr + count/4`. Expect upstream to fix it. Do not reproduce the bug in new code.
- **#187** (closed, not merged): H7 stale flash status flags caused ACK_ERROR on occupied sectors. Lesson for C5: clear `FLASH->CCR` flags before erase and program.
- **#181** (open): G0 dual-bank page arithmetic shared with G4 is wrong for G4 above 128 KB. Lesson: give C5 its own erase branch; do not join the `G0 || G4` path.
- **`25482ba`** (merged): H72x needed a lock/unlock between erase and program ("avoid triggering … write security"). Watch for similar behaviour on C5.

---

## 8. Checklist: files an STM32C5 port touches in Katapult

**Must change:**
1. `src/stm32/Kconfig`: chip entries (hidden until flash works), `MACH_STM32C5`, `HAVE_STM32_USBFS`, `HAVE_STM32_FDCANBUS` (C552 only), `MCU`, `CLOCK_FREQ`, `FLASH_SIZE`, `RAM_SIZE` (§6.3), deployer offset choice, app offset choice (≥8 KiB, page-aligned), CAN pin `depends on` exclusions, optional `STM32_DFU_ROM_ADDRESS`.
2. `src/stm32/Makefile`: `dirs`, `CFLAGS` (`-mcpu=cortex-m33`), `mcu-$(CONFIG_MACH_STM32C5) += stm32/stm32c5.c`, serial source.
3. `src/stm32/internal.h`: include `stm32c5xx.h`.
4. `src/stm32/stm32c5.c` (new): `lookup_clock_line`, `get_pclock_frequency`, `gpio_clock_enable`, `clock_setup` (HSI144/PSI or HSE, flash latency, USB clock, CRS, FDCAN kernel clock), `bootloader_request`, `armcm_main`. Ideally identical to Kalico's/Klipper's `stm32c5.c`.
5. `src/stm32/flash.c`: C5 branches in `flash_get_page_size` (8 KB), `erase_page` (`PER` + `BKSEL` + `PNB` + `STRT`, `CCR` clear), and `write_block` (quad-word, wait `BSY`/`WBNE`/`DBNE`). Optionally ICACHE invalidate.
6. `src/stm32/usbfs.c`: C5 in the G0/DRD branch, IRQ name.
7. `src/stm32/fdcan.c`: C5 IRQ, AF9, `RXGFC` path, FDCAN1-only instance mapping.
8. `src/stm32/stm32f0_serial.c`: AF7 and `BRR` position defines.
9. `lib/stm32c5/include/{stm32c5xx.h, stm32c551xx.h, stm32c552xx.h, system_stm32c5xx.h}` and an entry in `lib/README`.
10. `test/configs/stm32c5.config` and `test/configs/stm32c5-canbus.config`.

**Optional:** `README.md` (support list); `src/stm32/gpioperiph.c` (comment only).

**No change needed:**
- `src/generic/armcm_canboot.c`, `armcm_boot.c`, `armcm_reset.c`, `armcm_irq.c`, `armcm_timer.c` (already M33-safe)
- `src/generic/armcm_link.lds.S`, `armcm_deployer.lds.S`
- `src/{bootentry,flashcmd,sched,command,led,deployer}.c`
- `scripts/flashtool.py`, `scripts/buildbinary.py`, `scripts/buildcommands.py`
- `lib/cmsis-core/*` (the C5 header passes a clang syntax check against Katapult's CMSIS 5 `core_cm33.h`: `clang --target=thumbv8m.main-none-eabi -mcpu=cortex-m33 -fsyntax-only -DSTM32C552xx`, exit 0)

**Cross-repo constraints (Kalico side):**
- Kalico's `CONFIG_MCU` must match Katapult's (flashtool MCU check).
- Kalico's "Bootloader offset" (`STM32_FLASH_START_*`, Kalico `src/stm32/Kconfig:306-338`) must offer the same 8 KiB/16 KiB offsets as Katapult's "Application start offset".
- Kalico's `try_request_canboot` already works for M33 (its cache clean is guarded by `== 7`).
