# STM32C5 (STM32C551/C552) ecosystem research for Kalico and Katapult

Research date: 2026-10-01. Scope: STM32C55xxx (C551/C552). Its die-mate STM32C562 is covered where relevant.

## Evidence legend

- **[V]**: verified from a primary source I read myself. That means an ST PDF (read from a byte-identical third-party mirror, see below), ST GitHub repo contents, upstream project source trees, or the OpenOCD Gerrit API.
- **[I]**: my inference from verified facts. Not stated by ST.
- **[S]**: secondary or unverified. Search-engine snippets, distributor pages, or news articles I could not open.

**Access note:** www.st.com timed out from this environment for every request: WebFetch, and curl over HTTP/1.1 and HTTP/2. I therefore could not open ST product or documentation pages directly. The ST PDFs I used (RM0522, AN2606, ES0661, DS14927) come from a GitHub mirror, CoreMaker-lab/STM32C562_SENSOR (commit 7f7cac5d, 2026-08-16). Their PDF metadata and page footers identify them as ST originals. Newer revisions may exist on st.com; check before relying on page numbers.

Local copies, all in the scratchpad `research/` folder: `rm0522.pdf/.txt`, `an2606.pdf/.txt`, `es0661.pdf/.txt`, `ds_c562ce.pdf/.txt`. The `../stm32c5xx-dfp` and `../stm32c5xx-drivers` folders are clones at tag 2.1.0, and `hdr/` holds comparison CMSIS headers.

---

## 1. Register-level documentation

| Doc | Number / revision found | URL | Status |
|---|---|---|---|
| Reference manual, all STM32C5 lines (C53x/C542, C55x/C562, C59x/C5A3) | **RM0522 Rev 1, February 2026**, 2572 pages | https://www.st.com/resource/en/reference_manual/rm0522-stm32c5-series-armbased-32bit-mcus-stmicroelectronics.pdf (canonical name, could not fetch). Mirror: https://github.com/CoreMaker-lab/STM32C562_SENSOR/blob/main/%E5%8F%82%E8%80%83%E6%89%8B%E5%86%8C/rm0522-stm32c5-series-armbased-32bit-mcus-stmicroelectronics.pdf | [V] content. [S] whether Rev 1 is still the latest. |
| Errata, C551/C552/C562 | **ES0661 Rev 1, February 2026** (die 0x44E, silicon rev "Y") | https://www.st.com/resource/en/errata_sheet/es0661-stm32c551xx552xx562xx-device-errata-stmicroelectronics.pdf (name inferred from the mirror filename). A search engine also indexes it as https://www.st.com/resource/en/errata_sheet/dm01158962.pdf | [V] content |
| Errata, other lines | ES0676 (C53x/C542), ES0677 (C59x/C5A3) | Both are cited in RM0522's "Related documents". ES0676: https://www.st.com/resource/en/errata_sheet/es0676-stm32c531xx-stm32c532xx-and-stm32c542xx-device-errata-stmicroelectronics.pdf | [V] numbers. [S] URL. |
| Datasheets | DS14928 (C55x; local digest is Rev 3, May 2026), DS14927 (C562, mirror is Rev 1), DS15125 (C53x), DS15135 (C542), DS15136 (C59x), DS15137 (C5A3) | Listed in RM0522 "Related documents" | [V] |
| Flash programming manual | **None as a separate document.** Flash programming is RM0522 chapter 6 (pp. 126–206). The only PM is PM0264, the generic Cortex-M33 programming manual. | https://www.st.com/resource/en/programming_manual/pm0264-stm32-cortexm33-mcus-and-mpus-programming-manual-stmicroelectronics.pdf | [V] |
| System bootloader | **AN2606 Rev 70, February 2026.** Chapter 11 covers STM32C55xxx/562xx (pp. 84–87). Table 226 gives device parameters. | https://www.st.com/resource/en/application_note/an2606-introduction-to-system-memory-boot-mode-on-stm32-mcus-stmicroelectronics.pdf | [V] |
| USB DFU protocol | AN3156 (Rev 18, Feb 2026 per search) | https://www.st.com/resource/en/application_note/an3156-how-to-use-usb-dfu-protocol-in-bootloader-on-stm32-mcus-stmicroelectronics.pdf | [S] |
| Board manuals | UM3615 (Nucleo-64, MB2213), UM3616 (Nucleo-144, MB2310), AN6274 (hardware getting started) | https://www.st.com/resource/en/user_manual/um3615-stm32c5-nucleo64-board-mb2213-stmicroelectronics.pdf | [S] Search results only; fetches timed out. |

### AN2606: STM32C55xxx/562xx system bootloader [V]

From AN2606 Rev 70, chapter 11, Table 23, and Table 226:

- **Activation is Pattern 19.** The bootloader runs when any of these holds:
  - BOOT0 option bit = 1 with BOOT_SEL = 0.
  - BOOT0 option bit = 0 with BOOT_SEL = 0 and user flash empty.
  - BOOT_SEL = 1 with the BOOT0 pin = 1.
- It follows "boot model V1", the legacy model: it boots straight into the bootloader with no secure-firmware stage.
- **Bootloader version** is V16.1. Bootloader ID 0x101 is stored at 0x0BF885FE, and the PID is 0x44E.
- **Clocks and resources:**
  - Runs at 48 MHz from HSI/3 with no PLL. CRS is enabled for DFU.
  - Uses RAM 0x20000000–0x20003C3F (15 KB). The usable RAM range for the BL is 0x20003C40–0x2001FFFF.
  - Firmware is "33 Kbytes starting at 0x0BF80080". The system-memory range is 0x0BF80080–0x0BF885FF.
  - Sets the IWDG prescaler to maximum if the watchdog is running.
- **Interfaces and pins:**
  - USART1 on PA9 (TX) / PA10 (RX).
  - USART2 on PA2 / PA3.
  - USART3 on PD8 (TX) / PD9 (RX).
  - UART4 on PA0 (TX) / PA1 (RX).
  - All USART/UART links use 8E1 framing, auto-baud, and wait for 0x7F.
  - SPI1 on PA4–PA7, SPI2 on PB12–PB15, SPI3 on PB8/PB0/PB1/PB2.
  - FDCAN1 on PB5 (RX) / PB6 (TX), at 250 kbit/s nominal and 1 Mbit/s data, FD with BRS.
  - USB DFU on PA11/PA12, forced device mode, using the USB interrupt.
- **FDCAN in the bootloader has conditions.** HSE is enabled "only when FDCAN is enabled on the ENGI and option bytes". The bootloader measures the crystal with TIM17 and supports only 12, 24, or 48 MHz. Otherwise it falls back to HSI/3. [V]
  - Whether FDCAN is enabled in the factory ENGI bytes is **not stated**. [S]
- **Interface selection is an option byte.** FLASH_BL_COM_CFG holds one bit per interface. It is 0xFFFFFFFF from the factory (RM0522 Table 28), and the bit assignment is "see bootloader documentation". I could not find that assignment in AN2606 Rev 70. [V] / [S]
- **Write alignment:** flash writes through the bootloader must be 16-byte aligned (AN2606 Table 7: STM32C5 = 16 bytes, the same as STM32H5). [V]

### Software entry to the system bootloader [V] for the facts, [I] for the recipe

- AN2606's generic guidance (p. 36) applies. Before jumping:
  - Disable all peripheral clocks.
  - Disable interrupts.
  - Clear pending interrupts.
  - Re-enable interrupts for USB, SPI, or non-auto-baud USART, because the BL does not do it.
- Figure 19 explicitly shows "System Reset Or JumpToBL" as an entry path.
- The system memory is at **0x0BF80000** (RM0522 Table 25: two banks × three 8 KB pages, 0x0BF80000–0x0BF8BFFF). The BL image is said to start at 0x0BF80080.
- **[I] Exact jump address is unconfirmed.** I could not find in any primary source whether the initial SP and reset vector are at 0x0BF80000/0x0BF80004 or at 0x0BF80080/0x0BF80084.
  - The 0x80-byte gap is consistent with a 32-entry vector table at 0x0BF80000, but that is a guess.
  - For comparison, a third-party H503 Klipper port uses 0x0BF87000 and marks it "VERIFY".
  - **Action:** dump 0x0BF80000–0x0BF80100 with SWD on a NUCLEO-C562RE before you set `CONFIG_STM32_DFU_ROM_ADDRESS`.
- The C5 has no SYSCFG memory remap. VTOR exists, since the Cortex-M33 implements it.

### BOOT0 and option-byte gotchas [V], important for Klipper and Katapult users

**The BOOT0 pin is ignored by default.**
- RM0522 Table 28 lists the ST production (initial) option bytes: BOOT_SEL = 0, BOOT0 option bit = 0, RDP = 0xED (L0), BOOTADD = 0x0800_0000, BOOT_LOCK = 0xC3 (unlocked).
- With BOOT_SEL = 0 the BOOT0 signal comes from the option bit, not the pin. So once flash holds code, pressing BOOT0 (on the PH2-BOOT0 pin, or PB8-BOOT0 on LQFP32) does **nothing**.
- This is the same trap as STM32G0/C0 (Katapult issue #82: https://github.com/Arksine/katapult/issues/82).
- You must set BOOT_SEL = 1 ("legacy mode") to make the pin work. RM0522 §6.10.11 has the bit definitions.

**The EMPTY flag can keep the part in the bootloader.**
- The "empty" check runs at option-byte load (OBL), not on every reset.
- FLASH_ACR.EMPTY (bit 16) is "not reset by system reset" and is software-writable (RM0522 §4.1, §6.10.1).
- [I] A blank part flashed once over DFU or UART may therefore keep re-entering the bootloader on plain system resets until a power cycle or OBL, or until firmware clears FLASH_ACR.EMPTY. This is the known G0 behaviour.

**Other boot rules:**
- In RDP L2 / L2_wBS the device always boots from BOOTADD. The bootloader cannot be reached.
- BOOTADD must be a valid user-flash address. Otherwise "the boot stalls, and the flash memory becomes unreadable" (RM0522 §6.10.15).

---

## 2. CMSIS device headers and the STM32CubeC5 package

**There is no `cmsis-device-c5` repo.** github.com/STMicroelectronics/cmsis-device-c5 and cmsis_device_c5 both return 404. [V]

For C5, ST moved to a split "DFP + drivers" layout:

| Repo | Contents | Tags (date) | License |
|---|---|---|---|
| https://github.com/STMicroelectronics/stm32c5xx-dfp | CMSIS device headers, C startup files, system_stm32c5xx.c, GCC/ARM/IAR linker scripts, SVDs, CubeMX2 descriptors, flash loaders (`Flash/STM32C5[56]x.xldr`), CMSIS-Pack pdsc | 2.0.0 (2026-03-13), **2.1.0 (2026-06-15)** | **BSD-3-Clause** (LICENSE.md) |
| https://github.com/STMicroelectronics/stm32c5xx-drivers | HAL2 + LL drivers | 2.0.0 (2026-03-13), **2.1.0 (2026-06-15)**. Main has fixes up to 2026-09-14. | **BSD-3-Clause** |
| https://github.com/STMicroelectronics/STM32CubeC5 | Umbrella repo: submodules (dfp, drivers, `arch/cmsis` = STMicroelectronics/cmsis-core at **CMSIS 6.3.0**, middleware on `hal2` branches), examples, utilities | 2.0.0 (2026-03-16), **2.1.0 (2026-06-19)**. Main updated 2026-09-07. | Mixed SLA. The DFP and drivers components are BSD-3-Clause; CMSIS core is Apache-2.0. |

All of the above is [V].

**Header files** (`stm32c5xx-dfp/Include/`, tag 2.1.0) [V]:
- `stm32c5xx.h`: family umbrella. Select the device with `-DSTM32C551xx` / `-DSTM32C552xx` / …; CMSIS device version 2.1.0.
- `stm32c531xx.h`, `stm32c532xx.h`, `stm32c542xx.h`, `stm32c551xx.h`, `stm32c552xx.h`, `stm32c562xx.h`, `stm32c591xx.h`, `stm32c593xx.h`, `stm32c5a3xx.h`
- `system_stm32c5xx.h`
- `Templates/stm32_external_env.h`

**Startup and system files** [V]:
- `Source/startup_stm32c5{31,32,42,51,52,62,91,93,a3}xx.c`. These are **C files, not assembly**.
- `Source/Templates/system_stm32c5xx.c`. It says SYSCLK after reset is HSIDIV3 = 48 MHz; SystemCoreClockUpdate knows PSI at 100/144/160 MHz.
- GCC linker templates such as `Source/Templates/gcc/linker/stm32c552xe_flash.ld` and `stm32c55xxe_flash.ld`.

**Header facts that matter for porting** [V]:
- C552 = C551 + FDCAN1. **C562 = C552 + AES only.** I diffed the IRQ lists and typedefs. So NUCLEO-C562RE is a faithful C552 development target.
- `__SAUREGION_PRESENT 0`, `__MPU_PRESENT 1`, `__FPU_PRESENT 1`, `__DSP_PRESENT 1`, `__NVIC_PRIO_BITS 4`, Cortex-M33 r0p4.
- 82 IRQs (0–81, with 68 unused). USB = `USB_DRD_FS_IRQn` 62. FDCAN1 = IRQs 34 and 35.
- `HSI_VALUE` is 144000000. `HSE_VALUE` is not defined in the device header; it comes from `stm32_external_env.h`.
- **The C5 headers do not define the legacy `SET_BIT`/`CLEAR_BIT`/`READ_REG`/`WRITE_REG`/`MODIFY_REG` macros.** They use `STM32_*` replacements instead. Kalico's `stm32h7_adc.c` and `sdio.c` use `MODIFY_REG`/`SET_BIT`.
- ADC common bits are renamed `ADCC_CCR_*` (not `ADC_CCR_*`).
- Headers include `<core_cm33.h>` and are shipped against CMSIS 6.3.0. Kalico's `lib/cmsis-core` already contains `core_cm33.h` from the RP2350 work, but it is **CMSIS 5.4**. [I] It will probably work, but compile-test it.

**DFP pdsc** [V]:
- `Dcore="Cortex-M33" Dfpu="SP_FPU" Dtz="NO_TZ" Dclock=144000000`.
- Subfamilies, each with its DBGMCU IDCODE (read at 0xE0044000, AP1):
  - "STM32C55x/562": 0x44E
  - "STM32C53x/542": 0x44F
  - "STM32C59x/5A3": 0x45A
- The C55x flash algorithm is `Flash/STM32C5[56]x.xldr`. It is an ELF that exports both the CMSIS-FLM entry points (Init/UnInit/EraseSector/ProgramPage/EraseChip/FlashDevice) and the ST external-loader entry points (Write/SectorErase/MassErase/StorageInfo).

**HAL2** [V]:
- C5 is a **HAL2** family. The drivers README says: "the new version of HAL (v2.x), named HAL2 … HAL API built on top of LL API".
- Files follow the pattern `hal/stm32c5xx_hal_<ip>.c` and `ll/stm32c5xx_ll_<ip>.h`, plus `stm32_hal.h`.
- Flash is split into `stm32c5xx_hal_flash.c` (program/erase) and `stm32c5xx_hal_flash_itf.c` (options, RDP, keys). USB is `stm32c5xx_hal_pcd.c`/`_hcd.c` on top of `stm32c5xx_usb_drd_core.c`.
- There are **no per-IP version macros** in HAL2; only `HAL_VERSION` 2.1.0 exists.
- **IP versions come from the DFP descriptor** `Descriptors/peripherals/D44E_peripherals.json`. See section 3.

---

## 3. Peripheral IP lineage

There are four sources of evidence, all [V]:
- (a) Register layouts I extracted from `stm32c552xx.h` and diffed against `stm32h563xx.h`, `stm32u385xx.h`, `stm32u585xx.h`, `stm32c092xx.h`, `stm32g0b1xx.h`, `stm32h7r3xx.h`, `stm32n657xx.h`, `stm32u083xx.h`, `stm32wba65xx.h` (fetched from ST's cmsis-device-* repos).
- (b) ST internal IP names and versions from the DFP's `D44E_peripherals.json`.
- (c) embassy-rs stm32-data `perimap.rs` (commit 2026-09-13): https://github.com/embassy-rs/stm32-data/blob/main/stm32-data-gen/src/perimap.rs
- (d) Zephyr `dts/arm/st/c5/stm32c5.dtsi` compatibles: https://github.com/zephyrproject-rtos/zephyr/blob/main/dts/arm/st/c5/stm32c5.dtsi

**Memory map and bus [V]**

The peripheral memory map is **identical to the STM32H5 non-secure map**:
- APB1 0x40000000, APB2 0x40010000, AHB1 0x40020000, AHB2 0x42020000, APB3 0x44000000, AHB3 0x44020000.
- RCC 0x44020C00, FLASH 0x40022000, USB 0x40016000 with PMA at 0x40016400.
- FDCAN1 0x4000A400, FDCAN config 0x4000A500, SRAMCAN 0x4000AC00.
- GPIOA 0x42020000, DBGMCU 0x44024000.
- UID 0x08FFF800, FLASHSIZE 0x08FFF80C.
- System memory 0x0BF80000.

Many RCC enable-bit positions also match H5:
- GPIOxEN, USBEN (APB2ENR bit 24), USART1EN (bit 14), SPI1EN (bit 12)
- FDCANEN (APB1HENR bit 9), CRSEN (APB1LENR bit 24), I2C1EN, SPI2EN, TIM2EN

| IP | C5 internal IP (DFP) | Evidence and lineage | Klipper/Katapult code that is closest |
|---|---|---|---|
| **RCC** | rcc2 | **New oscillator section.** There is no PLL. Oscillators are HSI144 (outputs HSIS 144 MHz, HSIDIV3 48 MHz, HSIK through a 1–8 divider), PSI (100/144/160 MHz, locked "in PLL mode" to HSE, LSE, or HSI/18; outputs PSIS, PSIDIV3, PSIK), and HSE 4–50 MHz. There is no HSI48 and no CSI. SYSCLK reset value = HSIDIV3 48 MHz (RM §9.4.8); the SW field is 2 bits {HSIDIV3, HSIS, HSE, PSIS}; max SYSCLK 144 MHz. Registers are CR1/CR2/CFGR1/CFGR2/CCIPR1/CCIPR2/RTCCR. The bus enable/reset registers (AHB1ENR 0x88, APB1LENR 0x9C, APB2ENR 0xA4, CCIPR1 0xD8, RSR 0xF4) sit at the **same offsets as H5**. The "S/K" split (system/kernel outputs) mirrors **STM32U3's MSIS/MSIK** and U3's PLL-less, reference-locked MSI. [I] Treat the RCC as new: compare H5 for register-bank layout, U3 for concept, C0 for "HSI + kernel divider, no PLL". | New `stm32c5.c` clock code is needed. **PSI-from-HSE accepts only 8/16/24/32/48 MHz crystals for 144 MHz.** 25 or 50 MHz gives 100 MHz exactly or 141.67 MHz (DS14928 Table 37; RM Table 66 lists 25/50 MHz only for 100 MHz). **12 MHz and 20 MHz crystals cannot clock PSI.** USB 48 MHz comes from CK48SEL = PSIDIV3, HSIDIV3 (with CRS), or HSE. FDCAN kernel comes from FDCANSEL = PCLK1, PSIS, PSIK, or HSE. |
| **FLASH** | flitf8_db_32kx128 v1.0 | **Derived from the H5 flash interface** (register offsets: ACR 0x00, KEYR 0x04 = H5 NSKEYR, OPTKEYR 0x0C, OPSR 0x18, OPTCR 0x1C, SR 0x20 = NSSR, CR 0x28 = NSCR, CCR 0x30 = NSCCR, OPTSR_CUR/PRG 0x50/0x54, BOOTR 0x80/0x84, OTPBLR 0x90, WRP1R 0xE8, ECC 0x100). All secure, OBK, and EPOCH registers are removed. **Writes are 128-bit quad-words** through a shared write buffer; partial writes use the **FW** (force-write) bit (RM §6.3.5); 9-bit ECC per 128 bits. **Pages are 8 KB.** C55xE has two banks of 32 pages (256 KB each); C55xC has 256 KB, with a SINGLE_BANK option. CR has PER, BER, MER, BKSEL (bit 31, the physical bank), PNB[5:0] at bits 11:6, and EDATASEL. **SWAP_BANK** option is supported, and RWW works across banks. EDATA is 16 pages per bank: 2 KB with 128-bit writes, or, when EDATA_EN = 1 (the factory default), 1.5 KB "data flash" with 16/32-bit writes at 0x09000000. Wait states: 0 WS ≤34, 1 ≤68, 2 ≤102, 3 ≤136, 4 WS ≤144 MHz; WRHIGHFREQ 00/01/10. ACR resets to 0x27 (7 WS). Keys are the standard 0x45670123/0xCDEF89AB and OPTKEY 0x08192A3B/0x4C5D6E7F. **"Must not unlock an already unlocked register, otherwise it remains locked until next reset."** AN2606 confirms the 16-byte alignment. ST OpenBL also programs "user flash by quad word (16 bytes)". | Katapult `src/stm32/flash.c` needs a new branch. The G0/G4 path writes 64-bit words; the H7 path writes 256-bit words. C5 needs a 16-byte write loop with BSY/WBNE/DBNE polling, 8 KB page erase with BKSEL, and an unlock that checks LOCK first. **Zephyr has a C5 driver** (`drivers/flash/flash_stm32c5x.c`, Apache-2.0, added 2025-12-16). TinyUF2's `ports/stm32h5` is also a usable reference. |
| **USB** | usb2 v1.2 | **USB_DRD_FS**, the same as G0B1/H5/U0/U3/U5/C071 (embassy "usb v4"; USBRAM "32_2048"). CHEP0R–CHEP7R, CNTR, ISTR, FNR, DADDR, LPMCSR, BCDR. **2048-byte PMA, 32-bit access** (RM0522 Table 486). No VDDUSB/USB33 enable step: the transceiver runs from VDD and PWR has no USBSCR. Erratum ES0661 §2.12.1: the BDT update finishes after the CTR interrupt, so wait **800 ns** before reading the PMA in FS (the same erratum as G0/H5). | Kalico `src/stm32/usbfs.c` G0B1 path (`USB_DRD_FS`, `USB_DRD_PMAADDR`, CHEP). |
| **FDCAN** | fdcan2 v1.1 | Bosch M_CAN, same register map as G0/G4/H5. The config block has only CKDIV, like G0/C0. **Message RAM is the fixed layout**: 212 words; 28 standard filters, 8 extended, 2 RX FIFOs × 3, 3 TX events, 3 TX buffers; 0x350 bytes at 0x4000AC00 (RM0522 §46.4.6). Zephyr uses `bosch,mram-cfg = <0x0 28 8 3 3 0 3 3>`; embassy calls it "fdcan_v1" (the same as G0/G4/H5). Errata ES0661 §2.11.1 (edge filtering EFBI) and §2.11.2 (TX FIFO order with dedicated TX buffers) are the usual M_CAN errata. | Kalico `src/stm32/fdcan.c` G0/G4 path. |
| **SPI** | spi2s3 v2.3 | **SPI v2 ("H7-style")**: CR1, CR2, CFG1, CFG2, IER, SR, IFCR, AUTOCR, TXDR, RXDR, CRCPOLY, TXCRC, RXCRC, UDRDR, I2SCFGR. 16 × 8-bit FIFO, 4–32-bit frames, RDY pin. Zephyr compatible is `st,stm32h7-spi`; embassy calls it "v5_i2s", the same as H5/H7RS. AUTOCR is present, as on U3/U5/WBA. Erratum ES0661 §2.10.1: RDY fails at high SCK when the C5 is the slave, which does not affect a master. | Kalico `src/stm32/stm32h7_spi.c`. |
| **USART/UART/LPUART** | sci3 v3.4 | USART v2+ with PRESC and an 8-byte FIFO; register map identical to G0/H5/H7RS/N6/U0 (no AUTOCR). embassy "usart v4". | Kalico `src/stm32/stm32f0_serial.c`, as used by G0/G4/H7/L4. |
| **I2C** | i2c2 v2.1 | I2C v2 (TIMINGR), identical to G0/H5 (no AUTOCR). Zephyr `st,stm32-i2c-v2`. | `stm32f0_i2c.c` |
| **ADC** | **aditf6 v3.0 (new IP name)** | This is **not the G0/C0 ADC** (CHSELR, single SMPR) and **not the G4/H5 ADC** (CFGR, TR1–3, DIFSEL). The register map matches the **STM32U3 and STM32N6 ADC**: CFGR1/CFGR2, SMPR1/2, PCSEL, SQR1–4, JSQR, OFCFGR[4]/OFR[4], GCOMP, JDR[4], AWD1–3 LTR/HTR, CALFACT. Zephyr compatible is `st,stm32n6-adc`; embassy uses "adc v3_c5" and "adccommon v4". CFGR1 has DMNGT at bits 1:0 and RES at bits 4:2, and ISR has LDORDY; both are H7-like. CR lacks ADCALDIF, ADCALLIN, and BOOST. Common bits are `ADCC_CCR_*`. Two ADCs, 12-bit, 2.25 MSPS. | [I] `stm32h7_adc.c`'s H7 path is the closest start. It needs register renames, a calibration and temperature-sensor review, and its own `MODIFY_REG`. |
| **GPIO** | ioport3 v4.1 | MODER, OTYPER, OSPEEDR, PUPDR, IDR, ODR, BSRR, LCKR, AFR[2], BRR. Identical to G0/C0/U0/H7RS (no HSLVR/SECCFGR). Ports A–E and H. All pins are analog after reset. | generic stm32 `gpio.c` |
| **TIM** | gptimer2 v5.0 | Superset of H5/U3 TIM: adds CCR7, CCMR4, MPR1/2, OOR. The base CR1/PSC/ARR/CCRx/CCER/BDTR registers are unchanged. | `hard_pwm.c` should work unchanged. [I] |
| **IWDG** | wdgls v4.2 | KR, PR, RLR, SR, WINR, EWCR, plus **ICR**. Matches the N6 layout; embassy calls it "iwdg c5". Klipper uses only KR/PR/RLR, which are standard. | `watchdog.c` |
| **DMA** | dma3 v1.6 (LPDMA1 8-channel, LPDMA2 4-channel) | GPDMA/LPDMA-style linked-list DMA, as on U5/H5. Zephyr `st,stm32u5-dma`. | Unused by core Klipper. |
| **EXTI / PWR / SBS / DBGMCU** | aiec v2.2 / pwrctrl2 / sbs4 / – | EXTI is G0/U5-style with EXTICR (Zephyr `st,stm32g0-exti`). PWR uses H5 register names (PMCR, PMSR, VMCR, WUCR, IORETR) but has no VOS registers: the LDO is fixed in Run, with voltage scaling only in Stop. SBS replaces SYSCFG, as on H5. DBGMCU has U3-style FZR names plus DBG_AUTH_HOST, DBG_BSKEY_PWD, and DBG_VALR for RDP keys. | – |
| **ICACHE** | icache1 v1.4 | 8 KB, disabled at reset (ICACHE_CR resets to 0x4). | – |

**Two CPU and memory caveats** (RM0522 §6.3.2 and §6.3.4) [V]:
1. In the OTP, RO (UID), and data-flash areas, **8-bit reads cause an AHB bus error**. Read the UID at 0x08FFF800 as 32-bit words.
2. "All the AHB memory range is cacheable by default; for OTP/RO/data areas the MPU has to disable cacheability. An attempt to cache these regions will generate a Hard Fault."

This matches the H5 Klipper port report on the Klipper Discourse (https://klipper.discourse.group/t/porting-to-stm32h5-series-mcu/26169, July 2026). Klipper's `chipid.c` passes `(void*)UID_BASE` to byte-wise readers, and that hard-faults on H5; it must copy the UID word by word, and needs an MPU region if ICACHE is enabled.

The DWT cycle counter (CYCCNT) is present (RM0522 §49.6), so `armcm_timer.c` works.

---

## 4. Upstream status, as of 2026-10-01 [V]

**Klipper3d/klipper** (master pushed 2026-09-30):
- STM32 Kconfig models: F103, F207, F401/405/407/429/446, F765, F031/042/070/072, G070/071/0B0/0B1, G431/474, H723/743/750, L412.
- **No C0, H5, U5, or C5 support.** GitHub issue/PR search for stm32h5, h503, h563, stm32u5, stm32c0, C562, and C552 returns 0 hits.
- Klipper Discourse search finds only one related thread: "Porting to STM32H5 series MCU" (#26169, 2026-07-18). It is a working H503/H523 port with benchmarks, but no code link.

**Arksine/katapult** (master pushed 2026-10-01):
- STM32 families: F0/F1/F2/F4, G0B0/G0B1, G431, H723/743/750, L412.
- **No H5, C0, U5, or C5 support.** No related issues or PRs.
- Cortex-M33 build infrastructure exists through RP2350: PR #174 was merged 2026-10-01 and the Makefile has `-mcpu=cortex-m33`.
- Issue #82 (G0 BOOT0 / nBOOT_SEL workaround, still open) is directly relevant to C5's BOOT_SEL default.

**KalicoCrew/kalico** (main pushed 2026-10-01):
- Same STM32 set as Klipper plus F411/F427. **No C5.**
- `lib/cmsis-core/core_cm33.h` (CMSIS 5.4) is already present from the RP2350 merge (commit 119023e8, 2024-12-05).
- **Open draft PR #348 "core: STM32 H5 support"** (PhilippMolitor, opened 2024-08-16, last updated 2025-11-07): https://github.com/KalicoCrew/kalico/pull/348
  - 21 files: `stm32h5.c`, H5 CMSIS headers, `mpu_armv8.h`, and Kconfig, Makefile, chipid, dfu_reboot, usbfs, and h7_adc touches.
  - Its checklist leaves ADC, CAN/FDCAN, SPI, and hard PWM unverified.
  - It is the most relevant thing to build on. The memory map, RCC bank layout, FLASH register offsets, USB, and FDCAN all match H5, so an "H5-like" abstraction would cover much of C5. The RCC oscillator and PLL code will not carry over.

**Other ports to borrow from** (not upstream):
- packerlschupfer/coreone-firmware (GPL-3.0; Klipper fork with a **hardware-validated STM32H503 port** that adds `MACH_STM32H5`, `src/stm32/stm32h5.c`, usbfs, and hard_pwm changes; pushed 2026-09-28): https://github.com/packerlschupfer/coreone-firmware
- Zephyr has full C5 support: `soc/st/stm32/stm32c5x`, `drivers/clock_control/clock_stm32_ll_c5.c`, `drivers/flash/flash_stm32c5x.c`, and boards `nucleo_c542rc`, `nucleo_c562re`, `nucleo_c5a3zg`, `seeed/xiao_stm32c5`. All Apache-2.0.
- TinyUSB has `hw/bsp/stm32c5` (May 2026) using the DFP and CMSIS 6.
- ST OpenBootloader has a C5 port on the `hal2` branch: https://github.com/STMicroelectronics/stm32-mw-openbl/tree/hal2/interfaces/stm32c5xx

---

## 5. Toolchain and flashing tools

**arm-none-eabi-gcc** [V]/[I]:
- Use `-mcpu=cortex-m33 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=hard`; the FPU is single-precision (pdsc `Dfpu=SP_FPU`). Soft-float also works.
- ST's DFP release notes list "ARM GCC 13".
- Kalico already builds RP2350 with `-mcpu=cortex-m33`.

**OpenOCD:**
- **Upstream** (openocd-org/openocd master, 2026-09-20; latest tag v0.12.0) has **no** `stm32c5x.cfg` and no C5 flash driver. [V]
- C5 support is under review on Gerrit, status NEW (not merged): [V]
  - 9699 "tcl/target: Add STM32C5x support" (updated 2026-09-22)
  - 10013 "src/flash/nor/stm32c5x: skeleton of flash driver" (2026-09-19)
  - 10014 "arm_adi_v5.c: add STM32C5x devices into dap_part_nums" (2026-09-19)
  - 9697 "flash/nor: support STM32CubeProgrammer flashloader aka stldr" (2026-09-25)
  - URLs follow the pattern https://review.openocd.org/c/openocd/+/9699
- **ST's fork** https://github.com/STMicroelectronics/OpenOCD (branch `openocd-cubeide-r7`) **has `tcl/target/stm32c5x.cfg`** (commit 84ffeddf38, 2026-02-19). [V]
  - It uses the generic **`stldr`** flash driver, which loads ST's `.xldr` external loader rather than a native driver. The `dev_id_loader` table is empty by default, so you must point it at `STM32C5[56]x.xldr`.
  - Other details: SWD/JTAG, AP1 for the CPU, DBGMCU accessed through AP0 at 0xE00E4000, 32 KB work area, 500 kHz, sysresetreq.
  - Practically, OpenOCD needs ST's fork plus the DFP loader today.

**dfu-util** [I]:
- ST's C5 OpenBootloader (hal2) advertises standard **DfuSe** alt-setting strings:
  - `"@Internal Flash /0x08000000/64*08Kg"`
  - `"@Option Bytes /0x40022050/01*432e"`
  - `"@OTP Memory /0x08FFE000/04.5*01Kg"`
  - `"@Read only Memory /0x08FFF800/01.5*01Kg"`
  - `"@ENGI Memory /0x40022400/01*01Kg"`
- AN2606 lists the ROM DFU as "USB DFU (V3.0)", the same version family as H5/H7RS.
- So `dfu-util -d 0483:df11 -a 0 -s 0x08000000:leave -D …` should work, as on G0/H5.
- Not hardware-verified. The ROM bootloader V16.1 is not necessarily identical to OpenBL.
- **Never write the option-byte alt setting casually.** "An incorrect RDP_LEVEL (on OBL) is interpreted as L2" (RM0522 §6.5.8).

**STM32CubeProgrammer** [S]:
- Search snippets of ST release note RN0109 say **v2.22.0** (RN0109 Rev 33, Feb 2026) added STM32C5. The list covers memory, OB, and OTP over debug and bootloader, plus "RDP regression with password".
- ST's blog mentions v2.23. I could not open st.com to confirm.

**SEGGER J-Link** [S]:
- Zephyr's NUCLEO-C562RE doc requires J-Link software ≥ v8.12e.
- SEGGER announced launch-day support (eejournal).

**pyOCD** [V]/[I]:
- No built-in C5 target in pyocd/pyOCD (latest v0.45.1, 2026-07-21).
- The CMSIS pack index (https://www.keil.com/pack/index.pidx) lists **STMicroelectronics `stm32c5xx_dfp` 2.1.0** served from developer.st.com.
- Zephyr's board file uses `pyocd --target=stm32c562ret6`, so pack-based targets are expected to work. [I]
- The pack's algorithm is the `.xldr` ELF, which exports the FLM symbols. [I] This is likely usable but untested.

---

## 6. TrustZone and security features that can block flashing or reading

**There is no TrustZone.** [V] Every source agrees:
- pdsc `Dtz="NO_TZ"`
- DFP descriptor CM33 features `SAU: 0, SECEXT: 0, MPU_S: 0`
- header `__SAUREGION_PRESENT 0`
- no SECCFGR, SECKEYR, or secure watermark registers
- RM0522 has no TZ/GTZC chapter; two stray "GTZC" mentions in the CCB chapter are copy leftovers
- CNX Software's launch coverage also mentions no TrustZone

There are still hardware isolation features: HDP (hide-protection) areas with HDPL levels in SBS, as on H5; MPU; and privilege attributes.

**Life cycle and RDP** (RM0522 §3.7.1, §6.5.7–6.5.10) [V] — this differs from both G0 and H5:

| RDP_LEVEL code | State | Effect |
|---|---|---|
| 0xED | L0 Open | Full debug. Boot through BOOT0 or option bytes. Bootloader available. |
| 0xD1 | L2_wBS (closed + boundary scan) | No debug. Boot from BOOTADD only. Only SWAP_BANK, LOCKBL, and RDP can change. |
| 0x72 | L2 Closed | No debug ("JTAG fuse"). Boot from user flash only. |

- **There is no RDP Level 1.** The codes 0xED/0x72 are the H5 PRODUCT_STATE codes for Open/Closed, which I verified in the H5 HAL (`OB_PROD_STATE_OPEN 0xED`, `_CLOSED 0x72`). The C5 has only these three states.
- **Regression from L2 to L0 needs a 128-bit OEM key** provisioned while in L0 (FLASH_OEMKEYR1–4; OEMLOCK sets and cannot be cleared). The key is shifted in over SWD/JTAG under reset. Regression mass-erases user flash and SRAMs; OTP is kept.
- **Without a provisioned OEM key, L2 is permanent** (Table 10).
- L2_wBS→L2 uses a BS key (factory 0xAAAAAAAA).
- **Any invalid RDP code at option-byte load is treated as L2.** On a double ECC error during OBL, defaults load with OPTSR = 0x20B072D8, which means RDP = 0x72.
- Net effect: a bad option-byte write can permanently lock the part.

**Other blockers** [V]:
- **BOOT_LOCK** = 0xB4 freezes BOOT0, BOOT_SEL, SWAP_BANK, and BOOTADD. It can only be undone in L0.
- **WRP** has per-page groups (WRP1R/WRP2R). Bank erase fails if any page is write-protected.
- **HDP** areas hide flash after boot.
- **OTP LOCKBL** is one-way.
- **BOOTADD** outside user flash stalls boot.
- **BL_COM_CFG** can disable bootloader interfaces.
- **SRAM1_RST / SRAM2_RST** default to 1 (SRAM not erased on reset). If someone sets them to 0, RAM-flag reboot requests break: Klipper's `dfu_reboot` magic and Katapult's request flag. [I]

---

## 7. Availability [S] unless noted

**Boards:**
- **No NUCLEO-C552.** The relevant boards are:
  - **NUCLEO-C562RE** (Nucleo-64 MB2213, STM32C562RET6, the same die as C552 plus AES)
  - NUCLEO-C542RC (Nucleo-64)
  - NUCLEO-C5A3ZG (Nucleo-144 MB2310)
- These three are verified as the boards ST lists in the stm32c5xx-drivers 2.1.0 release notes (all "RevB02") and as Zephyr board names. [V]
- **NUCLEO-C562RE board details** (Zephyr doc and DTS) [V]:
  - 24 MHz HSE and 32.768 kHz LSE.
  - USB-C device on PA11/PA12, with no dead-battery pull-downs; use a C-to-A cable or power from ST-LINK.
  - On-board CAN FD transceiver on FDCAN1 PB8 (RX) / PB9 (TX), with PE2 as standby and JP9 for termination.
  - User, reset, and **boot** buttons.
  - STLINK-V3EC.
  - Zephyr runs PSI = 144 MHz from HSE and USB from PSIDIV3.
- Third-party board: Seeed XIAO STM32C5 (STM32C5A3CG, not C55x; TinyUF2, CAN transceiver). [V] via Zephyr.

**Launch and pricing** [S]:
- Announced 2026-03-05 to 09; 40 nm process; "from $0.64" at 10k units (CNX Software, Hackster).
- Nucleo-64 boards around $21–23: ST eStore NUCLEO-C562RE $22.39, Mouser $22.85 with 259 in stock, Farnell #4872891.
- NUCLEO-C5A3ZG shown out of stock at the ST eStore.

**Chip stock** [S]:
- DigiKey snippets show STM32C552RET6 with 134 in stock (about $2.51 each at quantity 1) and STM32C552CET6 with 0 in stock.
- RS Components lists C551/C552/C562 parts.
- These are point-in-time snippets.

---

## Implications for the Kalico and Katapult C5 port (summary)

1. **Reuse as is (or nearly):**
   - `usbfs.c` G0B1/USB_DRD path. Consider the 800 ns CTR erratum.
   - `fdcan.c` G0/G4 path.
   - `stm32h7_spi.c`
   - `stm32f0_serial.c`
   - `stm32f0_i2c.c`
   - generic gpio, IWDG, and `armcm_timer` (DWT).
2. **New code is needed:**
   - RCC/PSI clock setup.
   - Flash (Katapult): 128-bit writes, 8 KB pages, BKSEL, SWAP_BANK awareness.
   - ADC: U3/N6-style map, closest to the H7 path.
   - chipid: word-wise UID reads, plus an MPU region if ICACHE is on.
   - `MODIFY_REG`-style macros, which the C5 headers drop.
3. **Clock reference constraint:**
   - PSI(HSE) needs an 8/16/24/32/48 MHz crystal; 25 or 50 MHz gives 141.67 or 100 MHz.
   - 12 MHz boards must run from HSI144 (±1%, with CRS for USB) or PSI(HSI/18), and can still clock FDCAN directly from HSE.
4. **Bootloader UX:**
   - The BOOT0 pin is inert by default (BOOT_SEL = 0).
   - The EMPTY flag persists across system reset.
   - The jump address for software DFU entry is unconfirmed: verify 0x0BF80000 against 0x0BF80080 on hardware.
5. **Safety:** never write RDP or option bytes from tools by accident. There is no L1, and a corrupt or invalid RDP equals a permanent L2 unless an OEM key exists.
6. **Base the work on Kalico PR #348 (H5).** Peripheral addresses, RCC bus enables, FLASH register offsets, USB, and FDCAN are H5-compatible.

## Sources (all accessed 2026-10-01)

- RM0522 Rev 1, AN2606 Rev 70, ES0661 Rev 1, DS14927 Rev 1 (ST PDFs from the mirror): https://github.com/CoreMaker-lab/STM32C562_SENSOR
- ST GitHub:
  - https://github.com/STMicroelectronics/stm32c5xx-dfp
  - https://github.com/STMicroelectronics/stm32c5xx-drivers
  - https://github.com/STMicroelectronics/STM32CubeC5
  - https://github.com/STMicroelectronics/stm32-mw-openbl/tree/hal2
  - https://github.com/STMicroelectronics/OpenOCD/blob/openocd-cubeide-r7/tcl/target/stm32c5x.cfg
  - https://github.com/STMicroelectronics/stm32h5xx-hal-driver (product-state codes)
  - cmsis-device-{h5,u3,u5,c0,g0,h7rs,n6,u0,wba} (comparison headers)
- Klipper: https://github.com/Klipper3d/klipper ; Discourse: https://klipper.discourse.group/t/porting-to-stm32h5-series-mcu/26169
- Katapult: https://github.com/Arksine/katapult ; issue #82: https://github.com/Arksine/katapult/issues/82
- Kalico: https://github.com/KalicoCrew/kalico/pull/348
- H503 Klipper port: https://github.com/packerlschupfer/coreone-firmware
- Zephyr: https://github.com/zephyrproject-rtos/zephyr (boards/st/nucleo_c562re, dts/arm/st/c5, drivers/flash/flash_stm32c5x.c)
- embassy stm32-data: https://github.com/embassy-rs/stm32-data/blob/main/stm32-data-gen/src/perimap.rs
- TinyUSB: https://github.com/hathach/tinyusb/tree/master/hw/bsp/stm32c5
- OpenOCD upstream: https://github.com/openocd-org/openocd ; Gerrit: https://review.openocd.org/c/openocd/+/9699 (also 10013, 10014, 9697)
- pyOCD: https://github.com/pyocd/pyOCD ; CMSIS pack index: https://www.keil.com/pack/index.pidx
- [S] ST docs page (unreachable): https://www.st.com/en/microcontrollers-microprocessors/stm32c5-series/documentation.html
- [S] CNX launch article: https://www.cnx-software.com/2026/03/09/stmicro-stm32c5-entry-level-144-mhz-cortex-m33-mcu-features-up-to-1mb-flash-256kb-sram-ethernet-can-bus/
- [S] RN0109 (CubeProgrammer v2.22.0): https://www.st.com/resource/en/release_note/rn0109-stm32cubeprogrammer-release-v2220-stmicroelectronics.pdf
- [S] Distributors: https://www.mouser.com/ProductDetail/STMicroelectronics/NUCLEO-C562RE?qs=G4MbTVxgV4FvnkZrNwsDTA%3D%3D , https://estore.st.com/en/nucleo-c562re-cpn.html , https://www.digikey.com/en/products/detail/stmicroelectronics/STM32C552RET6/28948241
