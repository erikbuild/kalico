# Kalico anatomy: what adding an STM32 family touches (target: STM32C551/C552)

Repo: `/Users/erik/Code/kalico` (branch `stm32c5-support`, HEAD `aaaf2cc5`). Read-only research.
Line numbers are for the current tree. Anything not read directly from a cited file is marked
**[inference]** or **[unverified]**.

Extra evidence gathered outside the repo (scratchpad, not in the repo):
`.../scratchpad/research/c5dfp/` holds `stm32c5xx.h`, `stm32c551xx.h`, `stm32c552xx.h`,
`system_stm32c5xx.{h,c}`, `dfp.pdsc` and `c552_clock.json`. They were downloaded with `gh api` from
ST's `STMicroelectronics/stm32c5xx-dfp` (tag 2.1.0, commit `a5f65bc6`, 2026-06-15). That is the
`stm32c5xx_dfp` submodule of `STMicroelectronics/STM32CubeC5` (tag-2.1.0).

---

## 0. Key findings (TL;DR)

1. **Adding a family is a fixed set of edits.** You touch `src/stm32/Kconfig`, `src/stm32/Makefile`
   and `src/stm32/internal.h`. You add a new `src/stm32/stm32XX.c` for clock and startup, and a
   `lib/stm32XX/` directory with an entry in `lib/README`. Then you add per-family `#if` branches in
   the shared drivers (serial, spi, i2c, adc, usbfs, fdcan, hard_pwm), plus `test/configs/*.config`,
   `scripts/flash_usb.py` and `klippy/extras/temperature_mcu.py`. The G4 commit `c5d56f44` plus
   `9ab367d8`, and the L4 commit `d9c917b9` plus `57b0eb5d`, are the cleanest whole-family templates
   (section 6).
2. **Cortex-M33 is already supported in the generic layer, via RP2350.**
   - `lib/cmsis-core/core_cm33.h` exists (CMSIS 5.7.0 / core V5.2.0).
   - `src/generic/armcm_boot.c:62,78` has `__CORTEX_M == 33` branches.
   - `src/rp2040/Makefile:12` builds with `-mcpu=cortex-m33` and uses `generic/armcm_timer.c` (DWT + SysTick).
   - No ARM target passes `-mfloat-abi`/`-mfpu`, so Kalico builds soft-float everywhere and the C5 FPU would go unused.
3. **Confirmed blocker in shared code: `src/stm32/dfu_reboot.c:39` `#if __CORTEX_M >= 7`.**
   - This is true for M33 (33 ≥ 7), so the code calls `SCB_CleanDCache_by_Addr()`.
   - `core_cm33.h` does not declare that function. It only comes from `cachel1_armv7.h`, which `core_cm7.h:2230` includes.
   - I confirmed it fails as an undeclared function with a clang `-fsyntax-only` check against the C5 header. RP2350 never hit this because it does not build `stm32/dfu_reboot.c`.
4. **The C5 has no PLL.**
   - SYSCLK comes from HSIS (144 MHz), HSIDIV3 (48 MHz, the reset default), HSE, or PSIS. PSI is a "programmable-speed" oscillator at 100/144/160 MHz, referenced to HSE, HSI/18 or LSE (`RCC->CR2` PSIREFSRC/PSIREF/PSIFREQ).
   - Every existing `stm32*.c` clock_setup is built around a PLL, so C5 needs a new clock file. No existing clock_setup can be adapted.
   - PSI gives an exact 144 MHz only for HSE = 8/16/24/32/48 MHz. 25/50 MHz gives 141.67 MHz, and 12/20 MHz are not supported. This comes from DS Table 37 and the DFP clock descriptor.
5. **The C5 is structurally an H5-like part, and Kalico has no H5.**
   - Bus map from the C5 header: APB1 0x40000000, APB2 0x40010000, AHB1 0x40020000, AHB2 0x42020000, APB3 0x44000000, AHB3 0x44020000.
   - RCC has `CFGR1/CFGR2`, `APB1LENR/APB1HENR/APB2ENR/APB3ENR`, `AHB1ENR/AHB2ENR`, `CCIPR1/2`, plus ICACHE and SBS.
   - The closest Kalico code differs by peripheral:
     - Clock-line mapping: H7/G4 style (`stm32h7.c:51-65` APB1L/APB1H split).
     - USART: `stm32f0_serial.c`.
     - SPI: `stm32h7_spi.c`.
     - I2C: `stm32f0_i2c.c`.
     - ADC: `stm32h7_adc.c`, which needs a new branch.
     - USB: `usbfs.c` with the G0 `USB_DRD_FS` branch.
     - FDCAN: `fdcan.c` with the G0/G4 fixed-RAM `RXGFC` branch.
     - Timer: `generic/armcm_timer.c`.
     - GPIO: plain `gpio.c` + `gpioperiph.c`.
6. **The vendor header fits Kalico's CMSIS 5 core as-is.**
   - The ST DFP 2.1.0 headers (`stm32c551xx.h`/`stm32c552xx.h`) `#include <core_cm33.h>`. They passed a clang `-fsyntax-only` check against Kalico's `lib/cmsis-core`, including DWT, CoreDebug, `NVIC->IPR` and `SCB->SHPR` uses. (I used clang because no arm-none-eabi-gcc is installed here.)
   - STM32CubeC5 itself pins CMSIS core "Release 6.3.0", but the device header does not need it.
   - The HAL2-era header has **no `MODIFY_REG`**; it uses `STM32_MODIFY_REG`. `stm32h7_adc.c:215` uses `MODIFY_REG`.
   - `system_stm32c5xx.c` needs CMSIS-6 `SCB_SetVTOR`/`__VECTOR_TABLE`. Follow the G0 precedent and do not compile a vendor `system_*.c` (section 2).

---

## 1. Build / configuration

### 1.1 `src/Kconfig` (top level)
- `src/Kconfig:11-35` defines the architecture choice; `MACH_STM32` is at :21. `src/Kconfig:41` sources `src/stm32/Kconfig`.
- Generic comms symbols:
  - `SERIAL` (:50), `USBSERIAL` (:63), `USBCANBUS` (:65), `USB` (:67-69).
  - `USB_PRODUCT` defaults to `MCU` (:84-86).
  - `CANSERIAL`/`CANBUS`/`CANBUS_FREQUENCY` (:343-351).
- Feature gates: `WANT_ADC` (:127, depends `HAVE_GPIO_ADC`) and `WANT_HARD_PWM` (:147, depends `HAVE_GPIO_HARD_PWM`).
- `HAVE_*` capability symbols that arch Kconfigs `select`: `src/Kconfig:395-416`
  - `HAVE_GPIO`, `HAVE_GPIO_ADC/SPI/SDIO/I2C/HARD_PWM`
  - `HAVE_STRICT_TIMING`, `HAVE_CHIPID`, `HAVE_BOOTLOADER_REQUEST`
  - `HAVE_LIMITED_CODE_SIZE`, `HAVE_SOFTWARE_DIVIDE_REQUIRED`
- `HAVE_STEPPER_OPTIMIZED_BOTH_EDGE` (:366) enables `WANT_STEPPER_OPTIMIZED_BOTH_EDGE`.
- No change is needed here for a new STM32 family.

### 1.2 `src/stm32/Kconfig` (575 lines), section by section

| Lines | What | What a new family adds |
|---|---|---|
| 5-18 | `STM32_SELECT`: selects `HAVE_GPIO`, `HAVE_GPIO_ADC`, I2C/SPI (`!MACH_STM32F031`), SDIO (F4 only, :12), `HAVE_GPIO_HARD_PWM` (explicit family list, :13), `HAVE_STRICT_TIMING`, `HAVE_CHIPID`, `HAVE_STEPPER_OPTIMIZED_BOTH_EDGE if !MACH_STM32H7` (:16), `HAVE_BOOTLOADER_REQUEST`, `HAVE_LIMITED_CODE_SIZE if FLASH_SIZE < 0x10000` | Add `MACH_STM32C5` to the :13 list once `hard_pwm.c` has a table |
| 29-124 | `choice "Processor model"`: each `MACH_STM32xxxx` selects a family symbol plus optional sub-family (`MACH_STM32G07x`, `G0Bx`, `F0x2`, `F4x5`) | `MACH_STM32C551`, `MACH_STM32C552` selecting `MACH_STM32C5` |
| 126-132 | low-RAM variant toggles (F103x6, F070x6) | n/a |
| 134-161 | hidden family bools (`MACH_STM32F0..H7, L4, N32G45x`) | `config MACH_STM32C5 bool` |
| 162-165 | `HAVE_STM32_USBFS` (F0x2, G0Bx, L4, G4, AT32; F1/F070 only with crystal) | add `MACH_STM32C5` |
| 166-168 | `HAVE_STM32_USBOTG` (F2/F4/F7/H7) | no |
| 169-171 | `HAVE_STM32_CANBUS` (bxCAN) | no |
| 172-174 | `HAVE_STM32_FDCANBUS` (`MACH_STM32G0B1 \|\| H7 \|\| G4`) | add `MACH_STM32C552` only (C551 has no FDCAN; `stm32c551xx.h` has no `FDCAN1_BASE`/`SRAMCAN_BASE`) |
| 175-180 | `HAVE_STM32_USBCANBUS` = USB && (CAN\|\|FDCAN) && !F1 | automatic |
| 182-209 | `MCU` string, e.g. `"stm32g0b1xx"`. The Makefile turns it into `-DSTM32G0B1xx` (Makefile:19, `tr a-z A-Z \| tr X x`) | `"stm32c551xx"`/`"stm32c552xx"`. These produce `-DSTM32C551xx`/`-DSTM32C552xx`, exactly the macros `stm32c5xx.h:80-83` switches on |
| 211-230 | `CLOCK_FREQ` per MCU | 144000000 |
| 232-243 | `FLASH_SIZE`. By convention this is the *smallest* variant of the line, e.g. G0 0x20000 although G0B1 has 512K | 0x40000 (256K "C" parts; "E" parts are 512K) |
| 245-247 | `FLASH_BOOT_ADDRESS` 0x8000000 | same (`FLASH_BASE 0x08000000`) |
| 249-251, 253-274 | `RAM_START` 0x20000000, `RAM_SIZE` per family | 0x20000 (SRAM1 0x20000000 64K + SRAM2 0x20010000 64K, contiguous per header) |
| 276-278 | `STACK_SIZE` 512 | same |
| 290-298 | `STM32_DFU_ROM_ADDRESS`: G0/G4/L4/F4/F7 0x1fff0000, H7 0x1ff09800, AT32 0x1fffb000 | **[unverified]** C5 header has `FLASH_SYSTEM_BASE 0x0BF80000` (`stm32c552xx.h:1122`). AN2606 is needed to confirm the DFU entry vector |
| 305-337 | `choice "Bootloader offset"`, gated per family (`STM32_FLASH_START_2000` "8KiB" for F1/F070/G0/G4/F0x2 at :307-308, etc.) | C5 pages are 8 KB (DS §3.4.1), so 8KiB (Katapult), 16/32/64/128KiB are all natural |
| 338-353 | `FLASH_APPLICATION_ADDRESS` from the offset choice | automatic |
| 355-358 | `ARMCM_RAM_VECTORTABLE` (F0 only, no VTOR on M0) | n/a (M33 has VTOR) |
| 365-390 | `choice "Clock Reference"` (8/12/16/20/24/25 MHz, internal) and `CLOCK_REF_FREQ` (internal = 1) | Must be restricted for C5: only 8/16/24 MHz (and internal) give an exact 144 MHz PSI. 32/48 MHz would also work but have no Kconfig entry. 12/20 are unsupported; 25 gives 141.67 MHz |
| 392-399 | `STM32F0_TRIM` | n/a |
| 406-515 | `choice "Communication interface"`, gated by `depends on`/`if` per family. Details below | prune/extend for C5 |
| 516-544 | `choice "CAN bus interface"` for USB-CAN bridge | prune/extend for C5 |
| 547-573 | hidden `STM32_CANBUS_*` symbols OR-ing the two menus | maybe a new PE0/PE1 option |

Comms options and how they map onto C5 pins (AFs from DS Table 13):
- `STM32_USB_PA11_PA12` (:408) is fine (PA11=USB_DM, PA12=USB_DP).
- `STM32_SERIAL_USART1` PA10/PA9 AF7 is fine. `_ALT_PB7_PB6` AF7 is fine.
- `USART2` PA3/PA2 AF7 is fine. `_ALT_PD6_PD5` AF7 is fine.
- **`STM32_SERIAL_USART3` (PB11/PB10, :437-440) is only excluded for F0/F401/F411, so it would appear for C5. PB11 does not exist on C5** (DS Table 13 note: "Port B has no PB11 row"). It must be excluded.
- `USART3_ALT_PD9_PD8` AF7 is fine. `STM32_SERIAL_UART4` PA1/PA0 (H7-only, :449-452) matches C5 (UART4 RX/TX AF8 on PA1/PA0).
- CAN:
  - PA11/PA12, PA11/PB9, PB8/PB9 and PD0/PD1 are all valid AF9 on C5.
  - PB5/PB6 and PB12/PB13 are **FDCAN1** on C5, but `fdcan.c:64-77` maps them to FDCAN2 (see 4.10).
  - PB0/PB1, PC2/PC3, PD12/PD13 and PH13/PH14 have no FDCAN on C5.
  - C5-only FDCAN1 pin options include PE0/PE1, plus PB7/PD5 (TX) and PH2 (RX).

### 1.3 `src/stm32/Makefile` (121 lines)
- `:4` `CROSS_PREFIX=arm-none-eabi-`.
- `:6-16` `dirs-$(CONFIG_MACH_xxx) += lib/stm32xx`, which creates `out/` subdirs for compiled lib sources.
- `:18-19` `MCU`, `MCU_UPPER`. `:33` adds `-D$(MCU_UPPER) -mthumb -Ilib/cmsis-core -Ilib/fast-hash`.
- `:21-32` per-family `-mcpu=... -Ilib/stm32xx/include`.
  - C5 needs `CFLAGS-$(CONFIG_MACH_STM32C5) += -mcpu=cortex-m33 -Ilib/stm32c5/include`.
  - Precedent: `src/rp2040/Makefile:12` uses `-mcpu=cortex-m33`.
  - No `-mfloat-abi`/`-mfpu` anywhere: soft-float.
- `:35-37` link: `-nostdlib -lgcc -lc_nano -T out/src/generic/armcm_link.ld`.
- `:40-42` always built: `stm32/watchdog.c stm32/clockline.c stm32/dfu_reboot.c generic/crc16_ccitt.c generic/armcm_{boot,irq,reset}.c`.
- `:44-52` **family clock file + vendor system file.**
  - G0 is the only family that does *not* compile a vendor `system_*.c` (`:49`).
  - The others call `SystemInit()` from `armcm_main`.
- `:54-56` timer: default `generic/armcm_timer.c`; F0/G0 use `generic/timer_irq.c stm32/stm32f0_timer.c` (M0 has no DWT).
- `:57-60` gpio: default `gpio.c gpioperiph.c`; F1 `gpio.c` only; H7 `stm32h7_gpio.c gpioperiph.c`.
- `:62-69` adc: default `adc.c`; F0/G0 `stm32f0_adc.c`; G4/H7/L4 `stm32h7_adc.c`; N32 its own. Built if `CONFIG_WANT_ADC`.
- `:71-73` spi: default `spi.c`; H7 `stm32h7_spi.c`. Built if `CONFIG_WANT_GPIO_SPI`.
- `:75-79` i2c: default `stm32f0_i2c.c`; F1/F2/F4 `i2c.c`. Built if `CONFIG_WANT_GPIO_I2C`.
- `:81-86` serial: default `serial.c`; F0/G0/G4/H7 `stm32f0_serial.c`.
  - **[observation]** L4 falls through to `serial.c`, which uses `USARTx->SR/DR`. Those registers do not exist in `stm32l412xx.h` (its `USART_TypeDef` has ISR/RDR/TDR). L4 serial therefore appears not to compile.
  - CI only builds L4 with the default USB choice. Unrelated to C5 but noted.
- `:88-90` usb: `usbfs.c` if `HAVE_STM32_USBFS`, `usbotg.c` if `HAVE_STM32_USBOTG`, plus `chipid.c generic/usb_cdc.c`.
- `:92-97` canbus: `generic/canserial.c fasthash.c` plus `can.c` or `fdcan.c`; USB-CAN adds `generic/usb_canbus.c`.
- `:98` `hard_pwm.c` if `WANT_HARD_PWM`. `:100-101` sdio (F4).
- `:104-108` `klipper.bin` via objcopy.
- `:111-117` `make flash` runs `scripts/flash_usb.py -t $(CONFIG_MCU) -d $(FLASH_DEVICE) -s $(CONFIG_FLASH_APPLICATION_ADDRESS)`. `:119-121` `make serialflash` runs `stm32flash`.

### 1.4 Top-level Makefile and scripts
- `Makefile:75` includes `src/$(CONFIG_BOARD_DIRECTORY)/Makefile` (BOARD_DIRECTORY="stm32", `src/stm32/Kconfig:20-22`).
- `Makefile:87-89` preprocesses `*.lds.S`. `:91-94` links, then `scripts/check-gcc.sh`.
- `Makefile:105-110` builds `scripts/buildcommands.py` output, including the vector table generated from `DECL_ARMCM_IRQ` (`scripts/buildcommands.py:247-288`; table sized to the max declared IRQ, generic).
- `Makefile:114-122` creates the `out/board` symlink so `board/...` includes resolve to `src/stm32/`.
- `src/Makefile` is family-agnostic.
- `scripts/flash_usb.py:436-455` has the `MCUTYPES` prefix table:
  - `"stm32g0b1"`, `"stm32h7"`, `"stm32l4"`, `"stm32g4"` etc. map to `flash_stm32f4` (`:389-405`).
  - `flash_stm32f4` runs `dfu-util -R -a 0 -s <addr>:leave`, or hid-flash when the start is 0x8004000. It also detects Katapult and uses flash_can (`flash_dfuutil` :174-189).
  - Dispatch is a `startswith` match (`:496`), so C5 needs a `"stm32c5": flash_stm32f4` entry.
- `scripts/ci-build.sh:34-48` globs `test/configs/*.config`, runs `make olddefconfig` and builds each, runs `scripts/check-software-div.sh` (M33 has hardware divide, so no problem), and stores `<name>.dict`.
- GitHub workflow trigger paths include `test/configs/**` (`.github/workflows/ci-builder.yaml:14`, `ci-build_test.yaml:31`).
- `scripts/install-*.sh` just install `stm32flash`/`dfu-util`.
- `scripts/spi_flash/board_defs.py` is board-specific (only for SD-card flashing boards).
- Host side:
  - `klippy/extras/temperature_mcu.py:88-112` dispatches by MCU prefix (`"stm32g0"`, `"stm32g4"` and `"stm32l4"` go to `config_stm32g0` :233; `"stm32h723"` to :243; `"stm32h7"`). A C5 entry needs TS_CAL1 @30 °C at 0x08FFF814 and TS_CAL2 @140 °C at 0x08FFF818, VDDA 3.3 V (DS Table "TS_CAL", lines ~3440-3441 of the digest).
  - `klippy/extras/tmc_uart.py:111-113` only special-cases AVR.

---

## 2. Vendor headers

### 2.1 Layout of `lib/stm32*/`
Each family directory holds `include/stm32<fam>xx.h` (umbrella), every `include/stm32<part>xx.h`, `include/system_stm32<fam>xx.h`, and `system_stm32<fam>xx.c` at the directory root. Only CMSIS *device* files are imported; no HAL/LL. Exception: `lib/stm32g0/` has **no** `system_stm32g0xx.c` (header only), matching Makefile:49.

`src/stm32/internal.h:7-25` selects the umbrella header by family (`#elif CONFIG_MACH_STM32L4 / #include "stm32l4xx.h"`). C5 needs `#elif CONFIG_MACH_STM32C5 / #include "stm32c5xx.h"`.

### 2.2 `lib/README` conventions
Every STM32 entry follows the same boilerplate, for example `lib/README:88-92`:
"The stm32g0 directory contains code from: https://github.com/STMicroelectronics/STM32CubeG0 version v1.4.1 (<sha>). Contents taken from the Drivers/CMSIS/Device/ST/STM32G0xx/ directory."
- Entries: F0 :63, F1 :68, F2 :73, F4 :78, F7 :83, G0 :88, G4 :93, L4 :98, H7 :103.
- None declare local modifications.
- `git log` shows each lib dir as an untouched import commit. F1/F4 have older cleanup commits that removed HAL/linker files, and H7 had a version bump (`50b2e2e6`).
- For C5 the source would be `STMicroelectronics/stm32c5xx-dfp` tag 2.1.0 (`a5f65bc6...`), `Include/` + `Source/Templates/system_stm32c5xx.c`. Its layout is not `Drivers/CMSIS/Device/ST/...`, because HAL2-era Cube packages split it into a submodule.

### 2.3 `lib/cmsis-core`
- Contents: `cmsis_compiler.h cmsis_gcc.h cmsis_version.h core_cm0.h core_cm0plus.h core_cm3.h core_cm4.h core_cm7.h core_cm33.h cachel1_armv7.h mpu_armv7.h mpu_armv8.h`.
- `lib/README:3-6` says CMSIS_5 5.7.0. `cmsis_version.h:35-36` reports 5.4 (core); `core_cm33.h` is V5.2.0 (27 Mar 2020).
- `core_cm33.h` and `mpu_armv8.h` were added in the RP2350 commit `119023e8`.
- `core_cm33.h` defines `DWT`, `CoreDebug` (deprecated alias), `DCB`, `SysTick` (:2208-2214), `NVIC->IPR[]` (:482) and `SCB->SHPR[]` (:512). It does **not** define D-cache helpers.

### 2.4 STM32C5 device pack (external, for planning)
- STM32CubeC5 (GitHub `STMicroelectronics/STM32CubeC5`, tag-2.1.0) is a HAL2 package. Device files are in submodule `stm32c5xx-dfp`:
  - `Include/stm32c5xx.h`, `stm32c551xx.h` (1.09 MB), `stm32c552xx.h` (1.15 MB), `system_stm32c5xx.h`
  - `Source/Templates/system_stm32c5xx.c`, `Source/startup_stm32c55{1,2}xx.c`
  - SVDs and GCC linker templates
- CubeC5's `arch/cmsis` submodule pins ST `cmsis-core` "Release 6.3.0" (CMSIS 6).
- Compatibility, checked with clang `-fsyntax-only --target=thumbv8m.main-none-eabi -mcpu=cortex-m33 -DSTM32C55{1,2}xx -I<dfp> -I lib/cmsis-core`:
  - The device header compiles against Kalico's CMSIS 5 `core_cm33.h`.
  - `DWT->CYCCNT`, `CoreDebug->DEMCR`, `NVIC->IPR`, `SCB->SHPR` all resolve.
  - `SCB_CleanDCache_by_Addr` and `MODIFY_REG` are undeclared.
- `stm32c5xx.h` only includes `stm32_external_env.h` `#if defined(USE_EXTERNAL_ENV)`, so it is not needed. It defines `STM32_MODIFY_REG`, `STM32_SET_BIT`, etc., and not the legacy `MODIFY_REG`.
- `system_stm32c5xx.c:148-157` `SystemInit()` = `SCB_EnableFPU()` (if `__FPU_USED`) + `SCB_SetVTOR(&__VECTOR_TABLE[0])`. Both are CMSIS-6 helpers; `__VECTOR_TABLE` maps to `__Vectors` in Kalico's `cmsis_gcc.h:177-178`, which Kalico does not define. Recommend the G0 pattern: import the `.c` for reference but do not build it, and set `SCB->VTOR` in `armcm_main`.
- `system_stm32c5xx.c:90` `SYSTEM_CLOCK 48000000U /* Reset system clock */`, and `SystemCoreClockUpdate` decodes `CFGR1.SWS`: 0=HSIDIV3, 1=HSIS, 2=HSE, 3=PSIS. PSIFREQ: 0=100, 1=144, 2/3=160 MHz. **This contradicts DS §3.8 "restarts by default with an internal 144 MHz clock (HSI)"**; the header/system file says reset SYSCLK is HSI/3 = 48 MHz.
- Core config in `stm32c552xx.h:174-186`: `__CM33_REV 0x0004`, `__SAUREGION_PRESENT 0`, `__MPU_PRESENT 1`, `__VTOR_PRESENT 1`, `__NVIC_PRIO_BITS 4`, `__FPU_PRESENT 1`, `__DSP_PRESENT 1`.
- `UID_BASE 0x08FFF800`, `FLASHSIZE_BASE 0x08FFF80C`, `FLASH_SYSTEM_BASE 0x0BF80000`, `FLASH_OTP_BASE 0x08FFE000`.

---

## 3. Per-family clock/startup file contract

Every `src/stm32/stm32<fam>.c` must provide what `src/stm32/internal.h:42-54` and generic code consume:

| Symbol | Consumer | G0 (`stm32g0.c`) | G4 (`stm32g4.c`) | H7 (`stm32h7.c`) | L4 (`stm32l4.c`) | F4 (`stm32f4.c`) |
|---|---|---|---|---|---|---|
| `struct cline lookup_clock_line(uint32_t base)` | `clockline.c:11-32` (`enable_pclock` sets the bit and pulses reset; `is_enabled_pclock`) | :25-82 IOPORT/AHB/APB1/APB2 with many explicit cases | :19-61 APB1 (ENR1/ENR2 split at 32), APB2, AHB1, AHB2 + `ADC12_COMMON_BASE` special case, FDCAN2 special | :24-67 D1/D2/D3 bus map, APB1L/APB1H split, `ADC12_COMMON_BASE`, FDCAN2 | :19-53 like G4 | :26-42 |
| `uint32_t get_pclock_frequency(uint32_t base)` | serial, spi, i2c, fdcan, hard_pwm | :85-89 fixed 64 MHz | :64-68 CLOCK/2 | :70-74 CLOCK/4 | :56-60 CLOCK/1 | :44-49 CLOCK/2 or /4 |
| `void gpio_clock_enable(GPIO_TypeDef*)` | `gpio.c`, `gpioperiph.c:16` | :92-98 IOPENR | :71-77 AHB2ENR | :77-83 AHB4ENR | :63-69 AHB2ENR | :52-58 AHB1ENR |
| crystal pins `DECL_CONSTANT_STR("RESERVE_PINS_crystal", ...)` under `#if !CONFIG_STM32_CLOCK_REF_INTERNAL` | host pin reservation | PF0,PF1 :102-104 | PF0,PF1 :81-83 | PH0,PH1 :88-90 | PC14,PC15 :73-75 | PH0,PH1 :65-67 |
| `static clock_setup()` | own `armcm_main` | :107-143 PLL from HSE/HSI16, PLLR=sysclk, PLLQ=48 MHz USB, `CCIPR2 USBSEL` | :85-156 PLL, HSI48+CRS for USB, FDCANSEL=PCLK, flash WS table, PWR boost | :93-191 LDO, PLL1, VOS, I/D-cache, flash WS, D1/D2/D3 prescalers, FDCAN=pll1_q, HSI48+CRS USB | :77-138 PLL, HSI48+CRS, PWR USV, flash WS table | :70-210 |
| flash wait states | | `FLASH->ACR` LATENCY=2 + ICEN/PRFTEN, written in `armcm_main` :187-191 | in clock_setup :129-137 | :155-160 | :118-125 | :191-197 |
| `void bootloader_request(void)` | `HAVE_BOOTLOADER_REQUEST` (generic) | :151-156 `try_request_canboot(); dfu_reboot();` | :164-168 `dfu_reboot()` only | :199-204 both | :146-150 `dfu_reboot()` only | :231-238 canboot, HID (if 0x4000 offset), DFU |
| `void armcm_main(void)` | `generic/armcm_boot.c:103` | :164-197: UCPD strobe, `SCB->VTOR=VectorTable`, reset RCC regs, `dfu_reboot_check()`, flash ACR, clock_setup, `sched_main()` (no SystemInit) | :176-188 `dfu_reboot_check(); SystemInit(); VTOR; clock_setup; sched_main` | :212-235 SystemInit, reset many RCC regs, VTOR, `dfu_reboot_check()`, clock_setup | :158-170 like G4 | :246-264 + reset AHB/APB ENR |

Other things a clock file pulls in: `board/armcm_boot.h` (VectorTable, armcm_main), `board/armcm_reset.h` (`try_request_canboot`), `board/misc.h`, `command.h`, `internal.h`, `sched.h`. USB clock setup lives in the clock file (G0 `CCIPR2`, G4/L4 HSI48+CRS, H7 HSI48+CRS+`D2CCIP2R`); `usbfs.c` only enables the peripheral clock.

What a `stm32c5.c` must do differently ([inference] from header/DS/descriptor; details need the C5 reference manual):
- `lookup_clock_line`:
  - APB1 (0x40000000): bit = offset/0x400, with the APB1L/APB1H split at 32, like `stm32h7.c:51-65`. Verified against the header: TIM2→0, TIM5→3, TIM12→6, SPI2→14, SPI3→15, USART2→17, USART3→18, UART4→19, I2C1→21, I2C2→22, CRS→24, FDCAN1 (offset 41)→APB1H bit 9.
  - APB2 (0x40010000): offset/0x400 holds (TIM1→11, SPI1→12, TIM8→13, USART1→14, TIM15/16/17→16/17/18, USB→24).
  - AHB2: GPIOA..H→0..7, holds.
  - **Exceptions:** ADC12 (`RCC_AHB2ENR_ADC12EN` bit 10, but ADC1 sits at offset 0x8000), AHB1 (LPDMA2, RAMCFG mismatched) and APB3 (LPUART1, LPTIM1 mismatched). Only ADC12 matters to Kalico, so special-case it like G4/L4/H7.
- `get_pclock_frequency`: AHB/APB max 144 MHz (DS Table 17), so FREQ_PERIPH = CLOCK_FREQ (div 1, like L4). Peripheral kernel clocks are muxed in `RCC->CCIPR1/2`. CubeMX descriptor defaults are PCLK for USART/SPI/I2C1/FDCAN; hardware reset values are **[unverified]**.
- `clock_setup`:
  - Choose `HSIS` (internal 144 MHz, ±1% over -20..130 °C) or `PSIS` referenced to HSE (`RCC->CR2` PSIREFSRC/PSIREF/PSIFREQ=144).
  - Set the flash `LATENCY` (4-bit, `FLASH_ACR_LATENCY_0..15`) + `WRHIGHFREQ` + `PRFTEN`. The wait-state table is only in the RM (DS line 2391).
  - Enable `ICACHE->CR |= ICACHE_CR_EN` **[inference: H5-style ICACHE off at reset]**.
  - No voltage scaling: the PWR registers have no run-mode VOS (`PMCR`, `VMCR` only have low-power/PVD bits).
- USB clock:
  - `RCC_CCIPR2_CK48SEL` selects HSIDIV3 (48 MHz, descriptor default), PSIDIV3 or HSE. There is no HSI48.
  - CRS trims HSI144 from USB SOF (DS §3.9; `CRS_BASE` on APB1).
  - No VDDUSB/USV enable bit exists in `PWR_TypeDef` (`PMCR PMSR RTCCR VMCR VMSR WUSCR WUSR WUCR IORETR PRIVCFGR`).
- `RESERVE_PINS_crystal`: "PH0,PH1" (DS Table 12: PH0-OSC_IN, PH1-OSC_OUT).
- `bootloader_request`: `try_request_canboot(); dfu_reboot();` (G0/H7 style).

---

## 4. Peripheral drivers: variants, users, register model, `#if` branches

### 4.1 GPIO: `gpio.c` vs `stm32h7_gpio.c` (+ `gpioperiph.c`)
- `gpio.c` (all except H7, Makefile:57-58):
  - `DECL_ENUMERATION_RANGE` per port `#ifdef GPIOD..GPIOI` (:14-34).
  - `digital_regs[]` with designated initializers, so holes are allowed (:36-56); `gpio_valid` (:70-75).
  - Writes via BSRR, toggles via `ODR ^=`.
  - C5 ports A-E,H: `#ifdef` handles it (F/G NULL holes). `gpio_clock_enable` offset/0x400 matches AHB2ENR GPIOH bit 7.
- `stm32h7_gpio.c` (H7 only, added by `a438bb02`): caches BSRR state in RAM (`ODR_CACHE`) "because stm32h7 has very slow read access to the gpio registers". It uses `gpio_out.oc` (`gpio.h:6-12`). Kconfig :16 disables `HAVE_STEPPER_OPTIMIZED_BOTH_EDGE` for H7.
- `gpioperiph.c` (not F1): AFR/MODER/PUPDR/OTYPER/OSPEEDR. `CONFIG_MACH_STM32F0` special-cases speed (:38). No change is needed for C5; the C5 `GPIO_TypeDef` = MODER..AFR[2],BRR is standard.

### 4.2 ADC: `adc.c` / `stm32f0_adc.c` / `stm32h7_adc.c`
- `adc.c`: F1/F2/F4 "legacy" ADC (SR/CR2/SQR3); branches :27-115 for F1, F2/F4x5, F401/F446/F411.
- `stm32f0_adc.c`: F0/G0 (CHSELR-based); branches :25-131.
- `stm32h7_adc.c`: H7/G4/L4 "ADCv3" model.
  - Model: CR with ADVREGEN/ADCAL/ADEN/ADSTART/ADSTP, SQR1, SMPR1/2, ISR EOC/ADRDY, common CCR CKMODE/TSEN.
  - Pin tables `#if CONFIG_MACH_STM32H7 / G4 / else(L4)` at :26-157, `ADCIN_BANK_SIZE 20`.
  - Name fixups :170-174. ADC2/ADC3 selection `#ifdef` :191-212.
  - Unconditional `MODIFY_REG(adc_common->CCR, ADC_CCR_CKMODE_Msk, ...)` at :215-216 and `ADC_CCR_TSEN` at :266.
  - H7-only CFGR/BOOST/ADCALLIN :229-241 and `PCSEL` :272-274.
- C5 ADC per header:
  - `ADC_TypeDef` = ISR IER CR CFGR1 CFGR2 SMPR1 SMPR2 PCSEL SQR1-4 DR JSQR OFCFGR[4] OFR[4] GCOMP JDR[4] AWDx CALFACT.
  - `ADC_CR_` = ADCAL ADDIS ADEN ADSTART ADSTP ADVREGEN DEEPPWD JADSTART JADSTP. `ADC_ISR_LDORDY` exists.
  - Common `ADC_Common_TypeDef` = CSR CCR CDR CDR2, with bits named `ADCC_CCR_TSEN`/`ADCC_CCR_VREFEN`, **no CKMODE**. The ADC clock comes from `RCC_CCIPR2_ADCDACSEL` + `ADCDACPRE`.
- Closest is `stm32h7_adc.c`, but it needs a C5 branch:
  - pin table: ADC1 IN0-7=PA0-7, IN8-11=PC0-3; ADC2 IN0-3=PA0-3, IN4-5=PC4-5, IN6-8=PB0-2, IN9-11=PC1-3, IN12-13=PH4-5 (DS Table 12).
  - no CKMODE.
  - TSEN rename.
  - `PCSEL` is present (H7-like preselect; **[unverified]** whether required).
  - temp-sensor channel number from the RM.
  - `MODIFY_REG` replacement.

### 4.3 USART: `serial.c` / `stm32f0_serial.c`
- `serial.c`: old USART (SR/DR/BRR mantissa-fraction), F1/F2/F4 (and, apparently by fall-through, L4; see 1.3). AF numbers hardcoded per option (:15-71).
- `stm32f0_serial.c`: new USART (ISR/RDR/TDR, `CR3_OVRDIS`), F0/G0/G4/H7.
  - Per-option pins and AF with family ternaries (:15-96).
  - Name fixups `#if G0` (FIFO-named bits, BRR pos) / `G4` (BRR pos) / `H7` (FIFO-named ISR bits) (:104-133).
- C5 `USART_TypeDef` = CR1 CR2 CR3 BRR GTPR RTOR RQR ISR ICR RDR TDR PRESC (with 8-byte FIFO, DS Table 9). The header defines both `USART_ISR_RXNE` and `_RXNE_RXFNE` names. C5 uses `stm32f0_serial.c` + a `USART_BRR_DIV_MANTISSA_Pos 4 / FRACTION_Pos 0` alias like G4. The USART1 AF expression at :19-20 needs C5 added (AF7).

### 4.4 SPI: `spi.c` / `stm32h7_spi.c`
- `spi.c`: SPIv1/v1.5 (CR1 BR/SPE, CR2 DS/FRXTH for F0/F7/G0/G4/L4 at :109-113). Bus table with per-pin AFs (:13-92).
- `stm32h7_spi.c`: SPIv2 (CFG1 MBR/DSIZE, CFG2 MASTER/SSM/AFCNTR/SSOE, CR1 CSTART/SPE/SSI, CR2 TSIZE, SR RXWNE/RXPLVL/EOT, IFCR, TXDR/RXDR). Single AF per bus (:14-17).
  - Enumerations use `__COUNTER__` and must match array order.
  - **Note:** the PI2/PI3/PI1 entry at :73 is unconditional while its enumeration is `#ifdef GPIOI` (:42-45). That is harmless only while it stays last among the defined entries.
- C5 SPI per DS §3.25 (4-32 bit data, 16x8 FIFO, RDY pin, TSIZE "number of data") and header (`CR1 CR2 CFG1 CFG2 IER SR IFCR AUTOCR TXDR RXDR ...`) is the H7/H5-style SPIv2. All bit names `stm32h7_spi.c` uses exist in `stm32c552xx.h`.
- Existing `stm32h7_spi.c` pin sets all match C5 AFs: spi2 PB14/15/13 AF5, spi1 PA6/7/5 AF5, spi1a PB4/5/3 AF5, spi2a PC2/PC3/PB10 AF5, spi3a PC11/12/10 AF6.
- C5 SPI3 on PB3/4/5 uses AF6/AF6/AF7 (mixed), which this driver's single-AF struct can't express.

### 4.5 I2C: `i2c.c` / `stm32f0_i2c.c`
- `i2c.c`: old I2C (CR1/CR2/CCR/TRISE) for F1/F2/F4 (:27-58).
- `stm32f0_i2c.c`: TIMINGR I2C for F0/F7/G0/G4/H7/L4.
  - Per-family pin table branches :19-138.
  - TIMINGR computed from `get_pclock_frequency()/12 MHz` (:160-176). PRESC is 4 bits, which is fine at 144 MHz.
- C5 I2C is the TIMINGR IP (header: CR1 CR2 OAR1 OAR2 TIMINGR TIMEOUTR ISR ICR PECR RXDR TXDR). It needs a new pin table branch:
  - I2C1 PB6/PB7 AF4, PB8/PB9 AF4, PH1(SCL)/PH0(SDA) AF4.
  - I2C2 PB10(SCL)/PB12(SDA) AF4, PA11/PA12 AF8, PB3/PB4 AF9.
  - No PB11.

### 4.6 USB: `usbfs.c` / `usbotg.c`
- `usbfs.c` (F0x2, F1/F070 with crystal, G0Bx, G4, L4, AT32):
  - `#if F1` (32-bit access/16-bit data) / `F0||L4` (16/16) / `G4` (16/16, `USB_LP_IRQn`) / `G0` (32/32, `USB_IRQn`) at :18-38.
  - G0 `USB_DRD_FS` renames :41-54. `USB_BASE` used for the EPR array and clock (:189, :423). `USB_BCDR_DPPU` pull-up (:429-431).
- `usbotg.c` (F2/F4/F7/H7): OTG core, irrelevant for C5.
- C5 USB per header is `USB_DRD_TypeDef` (CHEP0R..7R, CNTR, ISTR, FNR, DADDR, LPMCSR, BCDR), `USB_DRD_FS_BASE` APB2+0x6000, `USB_DRD_PMAADDR` APB2+0x6400, PMA 2048 B, IRQ `USB_DRD_FS_IRQn` (62). This is the same IP as G0B1.
- Checked every `USB_*` macro `usbfs.c` uses against the C5 and G0B1 headers. C5 differs in two ways:
  - (a) it lacks `USB_EP_VTRX/USB_EP_VTTX`; it has `USB_CHEP_VTRX/VTTX`.
  - (b) it lacks `USB_BASE`; G0B1 defines both `USB_BASE` and `USB_DRD_BASE`.
- So C5 = the G0 branch with WSIZE 4 (**[unverified]**: 32-bit PMA access, inferred from the G0B1/H5 lineage), aliases `USB_EP_CTR_RX USB_CHEP_VTRX`, `USB_BASE USB_DRD_FS_BASE`, and `USBx_IRQn USB_DRD_FS_IRQn`.

### 4.7 CAN: `can.c` (bxCAN) / `fdcan.c`
- `can.c`: F0/F1/F4 bxCAN (:19-80). Irrelevant.
- `fdcan.c` (G0B1, G4, H7):
  - Pin options :22-62.
  - **FDCAN1 vs FDCAN2 selection by pin option** :64-77: PB0/PB1, PC2/PC3, PB5/PB6 and PB12/PB13 mean FDCAN2.
  - IRQ name G0 `TIM16_FDCAN_IT0_IRQn` / H7,G4 `FDCANx_IT0_IRQn`. AF G0=3, H7/G4=9 (:79-86).
  - Fixed message-RAM struct (`fdcan_msg_ram`: 28 std filters, 8 ext, 3 RXF0, 3 RXF1, 3 TEF, 3 TX = 212 words) at `SRAMCAN_BASE`.
  - Filter config `RXGFC` for G0/G4 vs `SIDFC`/`GFC` for H7 (:177-184). H7 also programs RXF0C/TXBC (:352).
- C5 (C552 only): `FDCAN_GlobalTypeDef` has RXGFC/TXBC/TXFQS (G4 layout), `SRAMCAN_BASE` APB1+0xAC00, `FDCAN_CONFIG` APB1+0xA500, IRQ `FDCAN1_IT0_IRQn`, 0.8 KB RAM ("two RX FIFOs of three payloads", DS §3.26). That is the G0/G4 path, with AF9.
- **The pin-to-instance logic at :64-77 must become family-aware**, since C5 PB5/PB6 and PB12/PB13 are FDCAN1.

### 4.8 Timers / PWM: `hard_pwm.c`, `stm32f0_timer.c`
- `hard_pwm.c`: per-family `pwm_regs[]` tables `#if F0(F042/F070/F072)/F1/F4/F7/G0/G4/H7` (:23-319). The generic setup at :321-465 uses `get_pclock_frequency`; "Timers run at twice the normal pclock" when APB div > 1 (:340-343).
- C5 needs a table. It has TIM1/2/5/8/12/15/16/17; no TIM3/TIM4 per header instance list. Examples (DS Table 13): TIM1 CH1-4 PA8-PA11 AF1; TIM2 CH1-4 PA0-PA3 AF1, PA5/PA15 CH1 AF1, PB3 CH2 AF1, PB10 CH3 AF1; TIM5 CH1-4 PA0-PA3 AF2; TIM8 PC6/PC7 AF3; TIM12 PB14/PB15 AF2; TIM15 PA2/PA3 AF4. Then add `MACH_STM32C5` to Kconfig :13.
- `stm32f0_timer.c`: TIM2/TIM3-based scheduler timer for M0 parts (F0/G0) without DWT (:22-36). Not needed for M33.

### 4.9 Misc
- `watchdog.c`: IWDG KR/PR/RLR. H7 alias `IWDG→IWDG1` (:11-13). The C5 header defines `IWDG` (with SR/WINR/EWCR/ICR, newer IP), so it should work unchanged **[unverified]**.
- `chipid.c`: reads 12 bytes at `UID_BASE` for USB serial / CAN UUID. C5 `UID_BASE` = 0x08FFF800.
- `dfu_reboot.c`:
  - Flag at `RAM_START+RAM_SIZE-1024` (H7: AXI SRAM, :21-25), then jumps to `CONFIG_STM32_DFU_ROM_ADDRESS` (:47-57).
  - **`#if __CORTEX_M >= 7` at :39 breaks M33**, as described in section 0.
- `clockline.c`: generic, no change.
- `sdio.c`: F4 only.
- `gpioperiph.c`: generic.

---

## 5. Generic ARM layer and Cortex-M33

- `generic/armcm_boot.c`: vector/reset. Already M33-aware: `NVIC->IPR` vs `IP` (:62-68), `SCB->SHPR` for M7/M33 (:78-84). It exports `DECL_CONSTANT_STR("MCU", CONFIG_MCU)` (:14) and calls `armcm_main()` (:103).
- `generic/armcm_irq.c`: `irq_wait` uses `wfi` except on M7, which uses `nop` because "Cortex-m7 may disable cpu counter on wfi" (:38-46). M33 takes the `wfi` path, as RP2350 already does. Whether the C5 DWT CYCCNT runs through WFI sleep is **[unverified]**.
- `generic/armcm_reset.c`: Katapult/CanBoot request via signature in the bootloader's RAM (:17-36). D-cache clean only `#if __CORTEX_M == 7`, which is correct for M33.
- `generic/armcm_timer.c`: SysTick + DWT CYCCNT. Uses `CoreDebug->DEMCR` and `DWT->CTRL` (:62-65, :97-99). Present in `core_cm33.h`; RP2350 uses it.
- `generic/armcm_link.lds.S`: generic, driven by `CONFIG_FLASH_APPLICATION_ADDRESS/FLASH_SIZE/RAM_START/RAM_SIZE/STACK_SIZE` (:12-16, :60-65).
- Things that assume a specific core:
  - `dfu_reboot.c:39` (`>= 7`, wrong for 33).
  - `armcm_irq.c:41` and `armcm_reset.c:32` (`== 7`, OK).
  - `-mcpu` per family in the Makefiles.
  - F0/G0 timer selection (Makefile:55-56).
  - No `CONFIG_MACH_CORTEX_*` Kconfig symbol exists; core is implied by family.
  - Search for other `__CORTEX_M` uses in `src/`: there are none besides these and `armcm_boot.c:62,78`.

---

## 6. Template commits (what each touched)

Whole-family additions:
- **G4** (Matt Baker, 2022-09-21):
  - `9ab367d8` "stm32g4: add lib from stm32cubeg4 v1.4.0": `lib/README`, `lib/stm32g4/include/*.h`, `lib/stm32g4/system_stm32g4xx.c`.
  - `c5d56f44` "stm32g4: implement build,usb,can,i2c,spi,serial,adc": `klippy/extras/temperature_mcu.py`, `scripts/flash_usb.py`, `src/stm32/{Kconfig,Makefile,fdcan.c,internal.h,spi.c,stm32f0_i2c.c,stm32f0_serial.c,stm32g4.c (new),stm32h7_adc.c,usbfs.c}`.
  - Later: `b6c3f056` G474 (`Kconfig`, `fdcan.c`, `stm32g4.c`, `stm32h7_adc.c`, `test/configs/stm32g474.config`), `9663dfda` bootloader offset (Kconfig), `2bf1720a` hard PWM (`Kconfig`, `hard_pwm.c`), `3c929534` 170 MHz.
- **L4** (2021-04-22):
  - `57b0eb5d` libs: `lib/stm32l4/...`.
  - `d9c917b9`: `klippy/extras/temperature_mcu.py`, `lib/README`, `scripts/flash_usb.py`, `src/stm32/{Kconfig,Makefile,internal.h,spi.c,stm32f0_i2c.c,stm32h7_adc.c,stm32l4.c (new),usbfs.c}`.
- **F7** (single commit `33b18fd6`, 2023-03-05): `config/generic-remram.cfg`, `lib/README`, `lib/stm32f7/...`, `scripts/flash_usb.py`, `src/stm32/{Kconfig,Makefile,dfu_reboot.c,gpioperiph.c,hard_pwm.c,internal.h,spi.c,stm32f0_i2c.c,stm32f7.c (new),usbotg.c}`, `test/configs/stm32f765.config`.
- **G0** (series):
  - `4576b391` lib: `lib/README`, `lib/stm32g0/...`.
  - `6e8f2811` "Initial support": `src/stm32/{Kconfig,Makefile,gpioperiph.c,internal.h,stm32f0_serial.c,stm32g0.c (new)}`.
  - `9549a3b4` USB on G0 (`Kconfig`, `usbfs.c`).
  - `1ff72612` G0B1 FDCAN (`Kconfig`, `Makefile`, `can.c`, `fdcan.c (new)`, `stm32g0.c`).
  - `9f31a35e` tests (`test/configs/stm32g0b1.config`, `test/klippy/printers.test`).
- **H7** (series): `53b98eba` lib; `0a55489e` "initial" (`Kconfig`, `Makefile`, `internal.h`, `stm32h7.c`, `stm32h7_adc.c`, `stm32h7_serial.c`, `watchdog.c`); `3ac35408` SPI (`stm32h7_spi.c`); `50b2e2e6` lib update for H723.

Recent variant additions (lighter):
- `a438bb02` H723 520 MHz (2026-01-22): a large mixed commit touching host code plus `stm32h7.c`, `stm32h7_gpio.c (new)`, `Kconfig`, `Makefile`, `gpio.h`, `stm32h7_adc.c`, `stm32f0_i2c.c`, `docs/{Benchmarks,Config_Changes,Features,G-Codes}.md`.
- `730ad286` F427 (`Kconfig` only).
- `81895db3` F411 (`scripts/flash_usb.py`, `Kconfig`, `adc.c`, `hard_pwm.c`, `stm32f4.c`, `test/configs/stm32f411.config`).
- `3329b9ba` F070x6 (`Kconfig`, `stm32f0.c`).
- `38d501c1` H750 offset (`Kconfig`).

Cortex-M33 precedent: `119023e8` RP2350 added `lib/cmsis-core/core_cm33.h` + `mpu_armv8.h`, the M33 branches in `generic/armcm_boot.c`, `docs/{Benchmarks,Features}.md`, `klippy/extras/temperature_mcu.py` and `lib/README`.

---

## 7. Docs, tests, configs

- `test/configs/`: one 3-line file per MCU, e.g. `stm32g0b1.config` = `CONFIG_MACH_STM32=y` + `CONFIG_MACH_STM32G0B1=y`. Expected: `stm32c551.config` and `stm32c552.config`. CI picks them up automatically via `scripts/ci-build.sh:36`.
- `test/klippy/printers.test`: `DICTIONARY <mcu>.dict` + sample cfgs (G0B1 at :96-97). Only needed when adding a `config/` sample.
- `config/`: generic-board cfgs mention MCU names in comments (e.g. `generic-bigtreetech-skr-mini-e3-v3.0.cfg`). The F7 commit added `config/generic-remram.cfg`. Optional.
- `docs/Features.md:174-196`: step-rate benchmark table (G0B1 :181, G431 :190, H723 :196, RP2350 :194).
- `docs/Benchmarks.md`: per-chip benchmark sections (H7 :251, G0B1 :270, G4 :289, RP2040/RP2350 :419-438, :510).
- `docs/Bootloaders.md`: per-family flashing notes (F1/F4/F0x2/CanBoot); nothing generic to extend.
- No "supported MCU list" doc exists beyond these. `docs/Features.md:67` speaks generically.
- Expected for a new family:
  - `test/configs` entries.
  - `scripts/flash_usb.py` `MCUTYPES`.
  - `klippy/extras/temperature_mcu.py`.
  - `lib/README`.
  - Benchmarks only once measured on hardware.

---

## 8. Judgement: closest template per peripheral for STM32C5

| Area | Closest Kalico template | Confidence / notes |
|---|---|---|
| Core/toolchain | RP2350 flags (`-mcpu=cortex-m33`, soft-float) + `generic/armcm_timer.c` | High. Fix `dfu_reboot.c:39` |
| Vendor lib | G0 pattern: headers only, no `system_*.c` built, `SCB->VTOR` set in `armcm_main` | High (CMSIS-6 helpers in `system_stm32c5xx.c`) |
| RCC clock-line map | `stm32h7.c:51-65` / `stm32g4.c:19-61` shape: APB1L/H split, APB2, AHB2 with ADC12 special case | High (verified bit positions vs offsets, section 3) |
| Clock tree | **No template.** No PLL; HSIS (internal) or PSIS-from-HSE; USB from HSIDIV3 + CRS (like G4/L4/H7's HSI48+CRS idea, different registers) | New code |
| Flash latency | G4/L4 style frequency ladder on `FLASH_ACR_LATENCY` + `WRHIGHFREQ` (H7 has WRHIGHFREQ) + enable ICACHE | Values need the RM |
| GPIO | `gpio.c` + `gpioperiph.c` | High; ports A-E,H via `#ifdef` |
| USART | `stm32f0_serial.c` (G4 BRR aliases) | High |
| SPI | `stm32h7_spi.c` (SPIv2: CFG1/CFG2/TSIZE/CSTART/RDY/FIFO) | High; all used bit names exist in the C5 header |
| I2C | `stm32f0_i2c.c` (TIMINGR) | High; new pin table |
| ADC | `stm32h7_adc.c` (ADVREGEN/ADCAL/ADEN/SQR1/SMPRx/PCSEL) | Medium: no CKMODE (RCC ADCDACSEL/PRE instead), `ADCC_CCR_TSEN`, `CFGR1` naming, `LDORDY`, `MODIFY_REG` missing |
| USB | `usbfs.c` G0 (`USB_DRD_FS`, 32-bit PMA) branch | High; add `USB_EP_CTR_RX/TX→USB_CHEP_VTRX/VTTX`, `USB_BASE→USB_DRD_FS_BASE`, `USB_DRD_FS_IRQn` |
| FDCAN | `fdcan.c` G0/G4 path (`RXGFC`, fixed 212-word RAM, AF9, `FDCAN1_IT0_IRQn`) | High; fix FDCAN1/2-by-pin logic |
| PWM timers | `hard_pwm.c` generic code; new table | Medium |
| Watchdog | `watchdog.c` unchanged | Medium **[unverified]** |
| Chip ID | `chipid.c` unchanged | High |
| DFU reboot | `dfu_reboot.c` + Kconfig address | Low: ROM entry 0x0BF80000? Needs AN2606 |

Things Kalico has no driver model for, and does not need: LPDMA (Kalico uses no DMA on STM32), I3C, LPUART, LPTIM, CORDIC, HASH, RNG, DAC, COMP, RTC/TAMP, ICACHE (only a one-line enable). No Kalico driver uses any of these.

Notable C5 constraints:
- No PB11, which kills `STM32_SERIAL_USART3` PB11/PB10 and `i2c2_PB10_PB11`-style pairs.
- No TIM3/TIM4.
- Single FDCAN on C552 only.
- PSI is exact only with 8/16/24/32/48 MHz crystals.
- HSI144 production range is 144.07-145.08 MHz at 30 °C (DS Table 36), i.e. biased slightly above 144 MHz. That matters if `CLOCK_FREQ=144000000` is used with the internal clock (about +0.05..+0.75% timing error) **[inference]**.

---

## 9. Concrete file list for a C5 port (from the above)

Must touch:
- `lib/stm32c5/include/{stm32c5xx.h,stm32c551xx.h,stm32c552xx.h,system_stm32c5xx.h}` (+ optionally `system_stm32c5xx.c` unbuilt). New.
- `lib/README`: new entry.
- `src/stm32/Kconfig`:
  - MACH symbols, MCU, CLOCK_FREQ, FLASH_SIZE, RAM_SIZE.
  - DFU ROM address, bootloader offsets, clock-ref restriction.
  - USBFS/FDCAN gating, comms option pruning (USART3 PB11), hard-PWM list.
- `src/stm32/Makefile`: `dirs-`, CFLAGS, `src-` (clock file, no system .c), adc/spi/serial/i2c selections.
- `src/stm32/internal.h`: umbrella include.
- `src/stm32/stm32c5.c`: new clock/startup file.
- `src/stm32/dfu_reboot.c`: `__CORTEX_M` guard.
- `src/stm32/stm32f0_serial.c`: C5 BRR alias + USART1 AF expression.
- `src/stm32/stm32h7_spi.c`: possibly C5 pin sets.
- `src/stm32/stm32f0_i2c.c`: C5 pin table.
- `src/stm32/stm32h7_adc.c`: C5 branch.
- `src/stm32/usbfs.c`: C5 branch.
- `src/stm32/fdcan.c`: C5 IRQ/AF + instance-by-pin.
- `src/stm32/hard_pwm.c`: C5 table.
- `scripts/flash_usb.py`, `klippy/extras/temperature_mcu.py`.
- `test/configs/stm32c551.config`, `test/configs/stm32c552.config`.

Probably untouched: all of `src/generic/*`, `clockline.c`, `gpio.c`, `gpioperiph.c`, `watchdog.c`, `chipid.c`, top-level Makefile, `src/Kconfig`, `scripts/ci-build.sh`.

## 10. Open questions needing the C5 reference manual / AN2606
1. Flash wait-state table vs HCLK, and the `WRHIGHFREQ` setting at 144 MHz.
2. `RCC->CR2` PSIREF encoding for 8/16/24 MHz HSE. The `stm32c5xx-drivers` LL RCC can show the encoding.
3. Hardware reset values of `CCIPR1/2` kernel-clock muxes (USART/SPI/I2C/FDCAN/ADC/CK48).
4. ADC temp-sensor/VREFINT channel numbers, required ADC clock range, and whether `PCSEL` must be set.
5. DFU/system bootloader entry address and whether a direct jump from the application is allowed (HDP/BOOT_LOCK features).
6. USB PMA access width (assumed 32-bit like G0B1).
7. ICACHE reset state.
8. Whether DWT CYCCNT keeps counting in WFI sleep.
9. Datasheet vs header conflict on the reset SYSCLK (144 MHz HSI per DS §3.8 vs 48 MHz HSIDIV3 per `system_stm32c5xx.c:90`).
