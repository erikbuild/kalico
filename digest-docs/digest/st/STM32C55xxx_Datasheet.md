# STM32C55xxx Datasheet (DS14928 Rev 3)

Digest of STMicroelectronics datasheet DS14928 Rev 3 (May 2026), *STM32C55xxx: Arm® Cortex®-M33 32-bit MCU with FPU, 144 MHz, 593 CoreMark®, up to 512-Kbyte dual-bank flash memory, 128-Kbyte RAM*. It covers the STM32C551xx and STM32C552xx lines (FDCAN1 is present only on STM32C552xx). Original PDF: `digest-docs/st/DS_stm32c551cc-1.pdf`.

Conventions used in this digest:

- Chapter, section, table and figure numbers match the original datasheet, so cross-references such as "Table 17" or "Section 5.3.14" can be followed directly.
- Merged table cells are repeated in every row they span, so each row stands alone. Table footnote markers appear as `(1)`, `(2)` with the note text listed under the table.
- Subscripts are flattened (VDDA, fHCLK, tw(SCKH)). Figures are described in prose or as mapping tables.
- Remarks added by the digest, rather than taken from the datasheet, are marked *Digest note:* or `[unclear in source: ...]`. Where the datasheet contradicts itself or contains an obvious typo, the printed value is kept and the problem is called out in such a note.
- Page headers/footers and the datasheet's own contents, list of tables and list of figures are omitted.

## Table of contents

- [Features](#features)
- [1 Introduction](#1-introduction)
- [2 Description](#2-description)
- [3 Functional overview](#3-functional-overview)
  - [3.1 Arm® Cortex®-M33 with FPU](#31-arm-cortex-m33-with-fpu)
  - [3.2 Instruction cache (ICACHE)](#32-instruction-cache-icache)
  - [3.3 Memory protection unit](#33-memory-protection-unit)
  - [3.4 Memories](#34-memories)
  - [3.5 Boot modes](#35-boot-modes)
  - [3.6 Power supply management](#36-power-supply-management)
  - [3.7 Peripheral interconnect matrix](#37-peripheral-interconnect-matrix)
  - [3.8 Reset and clock controller (RCC)](#38-reset-and-clock-controller-rcc)
  - [3.9 Clock recovery system (CRS)](#39-clock-recovery-system-crs)
  - [3.10 General-purpose inputs/outputs (GPIOs)](#310-general-purpose-inputsoutputs-gpios)
  - [3.11 Multi-AHB bus matrix](#311-multi-ahb-bus-matrix)
  - [3.12 Low-power direct memory access controller (LPDMA)](#312-low-power-direct-memory-access-controller-lpdma)
  - [3.13 Interrupts and events](#313-interrupts-and-events)
  - [3.14 Cyclic redundancy check calculation unit (CRC)](#314-cyclic-redundancy-check-calculation-unit-crc)
  - [3.15 Analog-to-digital converter (ADC)](#315-analog-to-digital-converter-adc)
  - [3.16 Digital to analog converter (DAC)](#316-digital-to-analog-converter-dac)
  - [3.17 Low-power comparator (COMP)](#317-low-power-comparator-comp)
  - [3.18 True random number generator (RNG)](#318-true-random-number-generator-rng)
  - [3.19 HASH processor (HASH)](#319-hash-processor-hash)
  - [3.20 Timers and watchdogs](#320-timers-and-watchdogs)
  - [3.21 Real-time clock (RTC), tamper and backup registers](#321-real-time-clock-rtc-tamper-and-backup-registers)
  - [3.22 Inter-integrated circuit interface (I2C)](#322-inter-integrated-circuit-interface-i2c)
  - [3.23 Improved inter-integrated circuit interface (I3C)](#323-improved-inter-integrated-circuit-interface-i3c)
  - [3.24 Universal synchronous/asynchronous receiver transmitter (USART/UART) and low-power universal asynchronous receiver transmitter (LPUART)](#324-universal-synchronousasynchronous-receiver-transmitter-usartuart-and-low-power-universal-asynchronous-receiver-transmitter-lpuart)
  - [3.25 Serial peripheral interface (SPI)/Inter-integrated sound interfaces (I2S)](#325-serial-peripheral-interface-spiinter-integrated-sound-interfaces-i2s)
  - [3.26 Controller area network (FDCAN) (available only in STM32C552x devices)](#326-controller-area-network-fdcan-available-only-in-stm32c552x-devices)
  - [3.27 Universal serial bus full-speed host/device interface (USB)](#327-universal-serial-bus-full-speed-hostdevice-interface-usb)
  - [3.28 Development support](#328-development-support)
- [4 Pinouts/ballouts, pin description, and alternate functions](#4-pinoutsballouts-pin-description-and-alternate-functions)
  - [4.1 Pinout/ballout schematics](#41-pinoutballout-schematics)
  - [4.2 Pin description](#42-pin-description)
  - [4.3 Alternate functions](#43-alternate-functions)
- [5 Electrical characteristics](#5-electrical-characteristics)
  - [5.1 Parameter conditions](#51-parameter-conditions)
  - [5.2 Absolute maximum ratings](#52-absolute-maximum-ratings)
  - [5.3 Operating conditions](#53-operating-conditions)
- [6 Package information](#6-package-information)
  - [6.1 Device marking](#61-device-marking)
  - [6.2 LQFP32 package information (5V)](#62-lqfp32-package-information-5v)
  - [6.3 UFQFPN32 package information (A0B8)](#63-ufqfpn32-package-information-a0b8)
  - [6.4 LQFP48 package information (5B)](#64-lqfp48-package-information-5b)
  - [6.5 UFQFPN48 package information (A0B9)](#65-ufqfpn48-package-information-a0b9)
  - [6.6 LQFP64 package information (5W)](#66-lqfp64-package-information-5w)
  - [6.7 LQFP80 package information (9X)](#67-lqfp80-package-information-9x)
  - [6.8 LQFP100 package information (1L)](#68-lqfp100-package-information-1l)
  - [6.9 Package thermal characteristics](#69-package-thermal-characteristics)
- [7 Ordering information](#7-ordering-information)
- [Important security notice](#important-security-notice)
- [Revision history](#revision-history)
- [Important notice](#important-notice)

## Features

Arm® Cortex®-M33 32-bit MCU with FPU, 144 MHz, 593 CoreMark®, up to 512‑Kbyte dual‑bank flash memory, 128-Kbyte RAM.

Includes ST state-of-the-art patented technology.

### Packages

- LQFP32 (7 x 7 mm)
- LQFP48 (7 x 7 mm)
- LQFP64 (10 x 10 mm)
- LQFP80 (12 x 12 mm)
- LQFP100 (14 x 14 mm)
- UFQFPN32 (5 x 5 mm)
- UFQFPN48 (7 x 7 mm)

### Product summary

| Group | Part numbers |
|---|---|
| STM32C551xx | STM32C551CC, STM32C551KC, STM32C551MC, STM32C551RC, STM32C551VC, STM32C551CE, STM32C551KE, STM32C551ME, STM32C551RE, STM32C551VE |
| STM32C552xx | STM32C552CC, STM32C552KC, STM32C552MC, STM32C552RC, STM32C552VC, STM32C552CE, STM32C552KE, STM32C552ME, STM32C552RE, STM32C552VE |

### Core

- 32-bit Arm® Cortex®-M33 CPU with FPU, frequency up to 144 MHz, MPU, and DSP instructions

### Benchmarks

- 593 CoreMark® (4.12 CoreMark®/MHz)

### ART Accelerator

- 8-Kbyte instruction cache enables 0-wait-state execution from flash memory at the CPU's maximum speed

### Memories

- Up to 512‑Kbyte flash memory with ECC, 2 banks read-while-write
- 128-Kbyte SRAM including 64-Kbyte with ECC
- 64-Kbyte flash memory area for software EEPROM emulation
- 4.5-Kbyte OTP (one-time programmable)

### Clock, reset, and supply management

- 2.7 V to 3.6 V application supply and I/O
- POR, PDR, and PVD
- Embedded regulator (LDO)
- Internal oscillators:
  - 144 MHz HSI (with +/- 1% accuracy over temperature range [-20 °C : 130°C]),
  - 160/144/100 MHz PSI, 32 kHz LSI
- External oscillators:
  - 4 to 50 MHz HSE,
  - 32.768 kHz LSE
- Low-power modes: Sleep, Stop, and Standby

### DMA controller to offload the CPU

- 2 x LPDMA with 12 channels (8 + 4)

### Analog

- 2 × 12-bit ADC (19 external channels and 2 internal), up to 2.25 MSPS, or up to 4.5 MSPS in dual interleaved mode
- 1 × 12-bit DAC (with output buffer)
- 1 × comparator (with configurable set of inputs)

### Up to 15 timers

- 9 × 16-bit (including 2 × 16-bit advanced motor control, 1 × low-power 16-bit timer available in Stop mode) and 2 × 32-bit timers
- 2 × watchdogs
- 1 × SysTick timer
- RTC with hardware calendar, alarms, and calibration

### Communication interfaces

- Up to 2 × I2C FM + interfaces (SMBus/PMBus)
- 1 × I3C
- Up to 3 × USARTs (ISO7816 interface, LIN, IrDA, modem control), 2 × UARTs, and 1 × LPUART
- Up to 3 × SPIs with full‑duplex I2S for audio-class accuracy through external clock, and up to 3 × additional SPIs derived from 3 × USARTs when configured in synchronous mode
- 1 × FDCAN (available only in STM32C552x devices)
- 1 × USB 2.0 full-speed host and device

### Low-power modes

- Sleep, Stop, and Standby modes

### Other features

- Up to 86 I/O ports with interrupt capability
- HASH (SHA-1, SHA-224, SHA-256), HMAC
- Mathematical coprocessor:
  - CORDIC for trigonometric functions acceleration
- 1 × True random number generator
- Bootloader support on USART, FDCAN, USB, and SPI interfaces
- Flexible life-cycle scheme with RDP and password-protected regression
- 96-bit unique ID
- All packages are ECOPACK2 compliant.

## 1 Introduction

This document provides information on STM32C55xxx devices, such as description, functional overview, pin assignment and definition, electrical characteristics, packaging and ordering information.

For information on the Arm® Cortex®-M33 core, refer to the *Arm® Cortex®-M33 Processor Technical Reference Manual*, available from the www.arm.com website.

Note: Arm and Cortex are registered trademarks of Arm Limited (or its subsidiaries or affiliates) in the US and/or elsewhere. The Arm word and logo are trademarks of Arm Limited (or its subsidiaries) in the US and/or elsewhere. All rights reserved.

## 2 Description

The STM32C55xxx devices are general purpose microcontrollers family (STM32C5 Series) based on the high‑performance Arm® Cortex®-M33 32-bit RISC core. They operate at a frequency of up to 144 MHz.

The Cortex®-M33 core features a single‑precision floating‑point unit (FPU), that supports all the Arm® single‑precision data‑processing instructions and all the data types.

The Cortex®-M33 core also implements a full set of digital signal processing (DSP) instructions and a memory protection unit (MPU) that enhances the application security.

The devices embed high‑speed memories (512‑Kbyte flash memory and 128‑Kbyte SRAM), and an extensive range of enhanced I/Os, peripherals connected to three APB buses, three AHB buses, and a 32‑bit multi‑AHB bus matrix.

The devices feature several protection mechanisms for embedded flash memory and SRAM: readout protection, write protection, and hide protection areas.

The devices embed several peripherals reinforcing security:

- HASH hardware accelerator
- True random number generator

The devices offer two 12‑bit ADCs, one DAC channel, one comparator, a low‑power RTC, two 32‑bit general‑purpose timers, two 16‑bit PWM timers dedicated to motor control, four 16‑bit general‑purpose timers, two 16‑bit basic timers, and one 16‑bit low‑power timer.

The devices also feature standard and advanced communication interfaces such as:

- Two I2Cs
- One I3C shared with I2C
- Three SPIs with multiplexed full-duplex I2S
- Three USARTs, two UARTs, and one low‑power UART
- One FDCAN (available only in STM32C552x devices)
- One USB full‑speed

The devices operate in the –40 to +125 °C (+140 °C junction) temperature ranges from a 2.7 to 3.6 V power supply.

A comprehensive set of power‑saving modes allows the design of low‑power applications.

The devices offer multiple packages from 32 to 100 pins.

See Table 1 for the list of peripherals available for each part number.

**Table 1. Device features and peripheral counts**

| Peripheral | STM32C55xKxT | STM32C55xKxU | STM32C55xCxT | STM32C55xCxU | STM32C55xRxT | STM32C55xRxTxJ | STM32C55xMxT | STM32C55xVxT |
|---|---|---|---|---|---|---|---|---|
| Flash memory (Kbytes) | 512/256 | 512/256 | 512/256 | 512/256 | 512/256 | 512/256 | 512/256 | 512/256 |
| SRAM (Kbytes) | 128 (including 64 with ECC) | 128 (including 64 with ECC) | 128 (including 64 with ECC) | 128 (including 64 with ECC) | 128 (including 64 with ECC) | 128 (including 64 with ECC) | 128 (including 64 with ECC) | 128 (including 64 with ECC) |
| ICACHE (Kbytes) | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 |
| Flash memory area for EEPROM Emulation (Kbytes) | 64 | 64 | 64 | 64 | 64 | 64 | 64 | 64 |
| One-time-programmable (Kbytes) | 4.5 | 4.5 | 4.5 | 4.5 | 4.5 | 4.5 | 4.5 | 4.5 |
| Timers – General purpose | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| Timers – Advanced‑control | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Timers – Basic | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Timers – Low‑power | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Timers – SysTick | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Window watchdog | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Communication interfaces – SPI (with I2S) | 3 (3) | 3 (3) | 3 (3) | 3 (3) | 3 (3) | 3 (3) | 3 (3) | 3 (3) |
| Communication interfaces – I2C | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Communication interfaces – I3C | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Communication interfaces – USART | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| Communication interfaces – UART | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Communication interfaces – LPUART | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Communication interfaces – USB | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Communication interfaces – FDCAN | 1 (1) | 1 (1) | 1 (1) | 1 (1) | 1 (1) | 1 (1) | 1 (1) | 1 (1) |
| Communication interfaces – TRACE | No | No | No | No | Yes | Yes | Yes | Yes |
| CORDIC | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| RTC | Yes (without LSE) | Yes (without LSE) | Yes | Yes | Yes | Yes (without LSE) | Yes | Yes |
| Tamper pins | 2 | 2 | 3 | 3 | 3 | 3 | 3 | 3 |
| True random number generator (RNG) | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| HASH | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| GPIOs | 25 | 27 | 38 | 38 | 52 | 52 | 66 | 86 |
| Wake-up pins | 3 | 3 | 4 | 4 | 6 | 6 | 6 | 7 |
| 12-bit ADC channels – External | 9 | 10 | 11 | 11 | 17 | 17 | 18 | 19 |
| 12-bit ADC channels – Internal | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| 12-bit DAC channels | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Analog comparator | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Maximum CPU frequency (MHz) | 144 | 144 | 144 | 144 | 144 | 144 | 144 | 144 |
| Operating voltage | 2.7 V - 3.6 V | 2.7 V - 3.6 V | 2.7 V - 3.6 V | 2.7 V - 3.6 V | 2.7 V - 3.6 V | 2.7 V - 3.6 V | 2.7 V - 3.6 V | 2.7 V - 3.6 V |
| Operating temperature | Junction temperature range: −40 to +140 °C | Junction temperature range: −40 to +140 °C | Junction temperature range: −40 to +140 °C | Junction temperature range: −40 to +140 °C | Junction temperature range: −40 to +140 °C | Junction temperature range: −40 to +140 °C | Junction temperature range: −40 to +140 °C | Junction temperature range: −40 to +140 °C |
| Packages | LQFP32 | UFQFPN32 | LQFP48 | UFQFPN48 | LQFP64 | LQFP64 | LQFP80 | LQFP100 |

Notes:

1. Available only in STM32C552x devices.

[unclear in source: the "Window watchdog" row reads "2"; the device has one WWDG and one IWDG (2 watchdogs total per the Features list), so this row likely counts both watchdogs.]

Figure 1 shows the general block diagram of the device family.

**Figure 1. STM32C55xxx block diagram** (ST drawing DT76078V2)

*Core and debug.* The Arm Cortex-M33 (144 MHz, FPU) is shown together with JTAG/SW, MPU, ETM and NVIC blocks. External debug pins are NJTRST, JTDI, JTCK/SWCLK, JTMS/SWDIO, JTDO (to JTAG/SW) and TRACECLK, TRACED[3:0] (to ETM). The core has two bus interfaces: the C-BUS goes through the ICACHE (8 Kbytes) into the AHB bus-matrix (the ICACHE has two links into the matrix), and the S-BUS connects directly to the AHB bus-matrix.

*AHB bus-matrix.* The matrix connects to the flash memory (up to 512 Kbytes; two links to the matrix plus a link from the AHB1 branch), SRAM1 (64 Kbytes) and SRAM2 (64 Kbytes). The bus masters LPDMA1 and LPDMA2 each have a master port into the matrix, and each also receives a link from the AHB1 branch. Three AHB buses, all at 144 MHz, leave the matrix:

- **AHB1 144 MHz** serves RAMCFG, LPDMA1/LPDMA2, the flash memory, CRC, CORDIC, the EXT IT. WKP block (EXTI wake-up, connected externally to "16 AF") and the AHB/APB1 bridge.
- **AHB2 144 MHz** serves RNG, HASH, DAC1 (via an ITF interface block, DAC1 in the VDDA domain, output DAC1_OUT1), ADC1 and ADC2 (via an ITF interface block, both in the VDDA domain, inputs 19xIN), GPIO port A (PA[15:0]), GPIO port B (PB[15:0]), GPIO port C (PC[15:0]), GPIO port D (PD[15:0]), GPIO port E (PE[15:0]), GPIO port H (PH[15:0]), and the AHB/APB2 bridge.
- **AHB3 144 MHz** serves the Reset and clock control block (RCC), EXTI, and the AHB/APB3 bridge.

*APB2 144 MHz* (from AHB/APB2) carries the following peripherals and their external signals (all "as AF" = alternate functions):

- TIM1/PWM 16b: 4 complementary channels (TIM1_CH[1:4]N), 7 channels (TIM1_CH[1:4]), ETR, BKIN, BKIN2 as AF
- TIM8/PWM 16b: 4 complementary channels (TIM8_CH[1:4]N), 7 channels (TIM8_CH[1:4]), ETR, BKIN, BKIN2 as AF
- TIM15 16b: 2 channels, 1 compl. channel, BKIN as AF
- TIM16 16b: 1 channel, 1 compl. channel, BKIN as AF
- TIM17 16b: 1 channel, 1 compl. channel, BKIN as AF
- USART1 (smartcard, IrDA): RX, TX, CK, CTS, RTS as AF
- SPI1/I2S1: MOSI, MISO, SCK, NSS as AF
- USB FS (in the VDDUSB power domain, with an internal PHY and a FIFO): DP, DM

*APB1 144 MHz (max)* (from AHB/APB1) carries:

- Standby interface: WKUPx (x=1 to 7)
- TIM2 32b: 4 channels, ETR as AF
- TIM5 32b: 4 channels, ETR as AF
- USART2 (smartcard, IrDA): RX, TX, CK, CTS, RTS as AF
- USART3 (smartcard, IrDA): RX, TX, CK, CTS, RTS as AF
- UART4: RX, TX, CTS, RTS as AF
- UART5: RX, TX, CTS, RTS as AF
- SPI2/I2S2: MOSI, MISO, SCK, NSS as AF
- SPI3/I2S3: MOSI, MISO, SCK, NSS as AF
- I2C1/SMBUS: SCL, SDA, SMBA as AF
- I2C2/SMBUS: SCL, SDA, SMBA as AF
- FDCAN1 (with FIFO): TX, RX as AF
- TIM12 16b: 2 channels, ETR as AF
- I3C1: SCL, SDA
- COMP1 (via an ITF interface block, COMP1 in the VDDA domain): INPx, INMx, OUTx
- CRS
- WWDG, IWDG, TIM6 16b, TIM7 16b (no external signals shown); the IWDG also appears inside the Supply supervision block

*APB3 144 MHz* (from AHB/APB3) carries:

- Temperature monitoring
- SBS
- RTC and TAMP (in the VRTC power domain, together with the XTAL 32k oscillator): OSC32_IN, OSC32_OUT, RTC_OUT1, RTC_OUT2, RTC_REFIN, RTC_TS, TAMP_IN[1:3]
- LPTIM1: IN1, IN2, CH1, CH2, ETR as AF
- LPUART1: RX, TX, CTS, RTS_DE as AF

*Clocks, power and supervision (VDD power domain).*

- The internal oscillators HSI, LSI and PSI form a VDD-domain block. Their outputs feed the Reset and clock control block (and the CRS); LSI also feeds the IWDG. The XTAL OSC 4–50 MHz (pins OSC_IN, OSC_OUT) also feeds the RCC and is routed as a reference into the PSI. The RCC generates FCLK, HCLKx and PCLKx.
- Power management (VDD domain) contains the Voltage regulator LDO, which supplies the internal core; the external supply pins are VDD = 2.7 to 3.6 V and VSS.
- Supply supervision (VDD domain) contains the PVD, the IWDG and the XTAL OSC 4–50 MHz; it produces the Reset and Int (interrupt) signals and connects to the external VDD, VSS, NRST pins and to the Standby interface.

*Power domain legend.* VDDUSB power domain: USB FS. VDDA power domain: DAC1, ADC1, ADC2, COMP1. VDD power domain: Power management, Supply supervision, HSI/LSI/PSI. VRTC power domain: XTAL 32k, RTC, TAMP.

Note: FDCAN1 only available for STM32C552xx devices.

## 3 Functional overview

### 3.1 Arm® Cortex®-M33 with FPU

The Cortex®-M33 is a highly energy-efficient processor designed for microcontrollers and deeply embedded applications, especially those requiring efficient security.

The Cortex® processor delivers a high‑computational performance with low‑power consumption and an advanced response to interrupts.

It features:

- Memory protection units (MPUs) supporting eight regions
- Floating-point arithmetic functionality with support for single-precision arithmetic

The processor supports a set of DSP instructions that allows an efficient signal processing and a complex algorithm execution.

The Cortex®-M33 processor features:

- System AHB bus: The system AHB (S-AHB) bus interface is used for any instruction fetch and data access to the memory‑mapped SRAM, peripheral, or Vendor_SYS regions of the Armv8‑M memory map.
- Code AHB bus: The code AHB (C-AHB) bus interface is used for any instruction fetch and data access to the code region of the Armv8‑M memory map.

Refer to Figure 1. STM32C55xxx block diagram for more details.

### 3.2 Instruction cache (ICACHE)

The instruction cache (ICACHE) is introduced on the C-AHB code bus of the Cortex®‑M33 processor to improve performance when fetching instructions and data from internal memories. Some specific features, like hit‑under‑miss and critical-word‑first refill policy, allow close to zero‑wait‑state performance in most use cases.

The ICACHE main features are:

- Bus interface:
  - One 32-bit AHB slave port, the execution port (input from Cortex®‑M33 C‑AHB code interface)
  - One 128-bit AHB master port: master1 port (output to Fast bus of the main AHB bus matrix)
  - One 32-bit AHB slave port for control (input from AHB peripherals interconnect, for ICACHE registers access)
- Cache access:
  - Zero wait-state on hits
  - Hit-under-miss capability: ability to serve processor requests (access to cached data) during an ongoing line refill due to a previous cache miss
  - Optimal cache line refill thanks to WRAPw bursts of the size of the cache line (32-bit word size, w, aligned on cache line size)
  - n-way set-associative default configuration with the possibility to configure as 1‑way, meaning direct‑mapped cache, for applications needing a very‑low‑power consumption profile
- Memory address remap:
  - Possibility to remap input addresses falling into up to four memory regions (used to remap aliased code in SRAM memories to the code region, for execution from the C‑AHB code interface)
- Replacement and refill:
  - pLRU-t replacement policy (pseudo-least-recently-used, based on binary tree), algorithm with the best complexity/performance balance
  - Critical-word-first refill policy, minimizing processor stalls
  - Possibility to configure burst type of AHB memory transaction for remapped regions: INCRw or WRAPw (size w aligned on cache line size)
- Performance counters: The ICACHE implements two performance counters:
  - Hit monitor counter (32-bit)
  - Miss monitor counter (16-bit)
- Error management:
  - Possibility to detect an unexpected cacheable write access, to flag an error, and optionally to raise an interrupt
- Maintenance operation:
  - Cache invalidate: full cache invalidation, fast command, noninterruptible

### 3.3 Memory protection unit

The memory protection unit (MPU) is used to manage the CPU accesses to the memory. It also prevents one task to accidentally corrupt the memory or the resources used by any other active task. This memory area is organized into up to eight protected areas.

The MPU is especially helpful for applications where some critical or certified code must be protected against the misbehavior of other tasks. An RTOS (real-time operating system) usually manages the MPU.

If a program accesses a memory location that is prohibited by the MPU, the RTOS can detect it and take action. In an RTOS environment, the kernel can dynamically update the MPU area setting based on the process to be executed.

### 3.4 Memories

#### 3.4.1 Embedded flash memory

The devices feature up to 512 Kbytes embedded flash memory that is available for storing programs and data.

The flash memory interface features:

- Dual-bank operating modes
- Read-while-write (RWW)

This allows a read operation to be performed from one bank while an erase or program operation is performed to the other bank. Each bank contains 32 pages of 8 Kbytes.

The flash memory embeds 4.5-Kbyte OTP (one-time programmable) for user data.

Enhanced flash memory protection mechanisms are available. These mechanisms can be activated by option bytes:

- RDP states for protecting memory content from debug access
- Page group write-protection (WRPG)
- One hide protection area (HDP) per bank that provides temporal isolation for startup code

The whole nonvolatile memory embeds the error correction code (ECC) feature supporting:

- Single-error detection and correction
- Double-error detection
- ECC fail address report

##### 3.4.1.1 User data flash memory

The device features 64 Kbytes of user data flash memory split in two banks of 16 × 2‑Kbyte sectors offering perfect space for storing EEPROM emulation data.

#### 3.4.2 Embedded SRAMs

Two SRAMs are embedded in the STM32C55xxx devices.

These SRAMs are made of several blocks that can be powered down in Stop mode to reduce consumption:

- SRAM1: 64 Kbytes
- SRAM2: 64 Kbytes with optional ECC

### 3.5 Boot modes

At startup, the BOOT0 pin allows the system to boot either from the user Flash or from the bootloader.

When boot from user Flash is selected, BOOTADD defines the boot address. This address can be locked thanks to BOOT_LOCK.

The embedded bootloader is located in the system memory, programmed by STMicroelectronics during production. It is used to reprogram the flash memory by using USART, SPI, FDCAN (available only in STM32C552x devices), or USB in device mode through the device firmware upgrade (DFU).

Refer to the application note *STM32 microcontroller system memory boot mode* (AN2606) for more details.

### 3.6 Power supply management

The power controller (PWR) main features are:

- Power supplies and supply domains
  - Core domain (VCORE)
  - VDD domain
  - RTC domain
  - Analog domain (VDDA)
- System supply voltage regulation
  - Voltage regulator (LDO)
- Power supply supervision
  - POR/PDR monitor
  - PVD monitor
- Power management
  - Low-power modes
- Privileged protection

#### 3.6.1 Power supply schemes

The devices require a 2.7 V to 3.6 V operating voltage supply VDD.

- VDD = 2.7 V to 3.6 V: VDD is the external power supply for the I/Os, the internal regulator, and the system analog such as reset, power management, and internal clocks. It is provided externally through the VDD pins.
- VDDA = VDD: VDDA is the analog power supply for ADCs, DACs, and comparator.
- VREF-, VREF+: VREF+ is the input reference voltage for ADCs and DAC. VREF+ can be grounded when ADCs and DAC are not active. VREF- and VREF+ pins are not available on all packages. When not available, they are bonded to VSSA and VDDA, respectively.

The STM32C55xxx devices embed a LDO regulator to provide the VCORE supply for digital peripherals, SRAM1, SRAM2, and embedded flash memory. The LDO generates this voltage on VCAP pin connected to an external capacitor of 2.2 μF typical.

The LDO regulator can operate in Stop modes where it may provide two different voltages (voltage scaling).

**Figure 2. STM32C55xxx power supply overview** (ST drawing DT74255V2)

The figure shows the device pins VSS, VDD and VCAP and the supply domains they feed:

- **VDDA domain**: A/D converters, D/A converter, Comparator. It is supplied from the VDD supply line.
- **USB transceiver**: drawn as a separate block, also supplied from the VDD supply line.
- **VDD domain** (supplied from the VDD pin, ground VSS): contains the VDDIO I/O ring; the Reset block and Internal RC oscillators; the Standby circuitry (Wake-up logic, IWDG); and the Voltage regulator, which contains the LDO regulator. The LDO output is connected to the VCAP pin and produces VCORE.
- **Core domain** (supplied by VCORE): Core, SRAM1, SRAM2, Digital peripherals. The Flash memory is also supplied by VCORE.
- **RTC domain (VRTC)**: LSE crystal 32 kHz oscillator, Backup registers, RCC_RTC register, RTC, TAMP. It is supplied from the VDD supply line.

#### 3.6.2 Power supply supervisor

The devices have an integrated power‑on reset (POR) / power‑down reset (PDR) circuitry:

- Power-on reset (POR): The POR supervisor monitors the VDD power supply and compares it to a fixed threshold. The devices remain in reset mode when VDD is below this threshold.
- Power-down reset (PDR): The PDR supervisor monitors the VDD power supply. A reset is generated when VDD drops below a fixed threshold.
- Programmable voltage detector (PVD): The PVD monitors the VDD power supply by comparing it with a threshold fixed by hardware. An interrupt can be generated when VDD drops below the VPVD threshold and/or when VDD is higher than the VPVD threshold. The interrupt service routine can then generate a warning message and/or put the device into a safe state. The software enables the PVD.

#### 3.6.3 Low-power modes

By default, the microcontroller is in Run mode after a system or a power reset. It is up to the user to select one of the low‑power modes described below:

- **Sleep mode**: In Sleep mode, only the CPU is stopped. All peripherals continue to operate and can wake up the CPU when an interrupt/event occurs.
- **Stop mode**: Stop mode achieves the lowest power consumption while retaining the content of SRAM and registers. All clocks in the VCORE domain are stopped, the PSI, the HSI, and the HSE crystal oscillators are disabled. The LSE or LSI is still running.
  - The RTC can remain active (Stop mode with RTC, Stop mode without RTC).
  - The system clock is HSI 144 MHz when exiting stop mode.
  - Stop 0 mode maintains the regulator output at a nominal voltage of 1.2 V.
  - Stop 1 mode reduces power consumption by lowering VCORE to 0.95 V, which results in a longer wake-up time and fewer wake-up sources compared to Stop 0 mode.
- **Standby mode**: The Standby mode is used to achieve the lowest power consumption with BOR. The PSI, the HSI, and the HSE crystal oscillators are also switched off.
  - The RTC can remain active (Standby mode with RTC, Standby mode without RTC).
  - The state of each I/O during Standby mode can be retained.
  - After entering Standby mode, SRAMs and register contents are lost except for registers in the RTC domain and Standby circuitry.
  - The device exits Standby mode in the following cases:
    - An external reset with NRST pin
    - An IWDG reset
    - A WKUP pin event (configurable rising or falling edge)
    - An RTC event occurs (alarm, periodic wake-up, timestamp), or in a tamper detection. The tamper detection can be raised either due to external pins or due to an internal failure detection.
  - The system clock after wake-up is HSI 144 MHz.

#### 3.6.4 Reset mode

To improve the consumption under reset, the I/O state under and after reset is "analog state" (the I/O Schmitt trigger is disabled).

### 3.7 Peripheral interconnect matrix

Several peripherals have direct connections between them. These connections allow autonomous communication between them and support the saving of CPU resources (thus power supply consumption). In addition, these hardware connections allow fast and predictable latency.

Depending on the peripherals, these interconnections can operate in Run and Sleep modes.

### 3.8 Reset and clock controller (RCC)

The clock controller distributes the clocks coming from the different oscillators to the core and to the peripherals. It also manages the clock gating for low‑power modes and ensures the clock robustness.

It features:

- Clock prescaler: in order to get the best trade‑off between speed and current consumption, the clock frequency to the CPU and peripherals can be adjusted by a programmable prescaler.
- Clock security system: clock sources can be changed safely on the fly in Run mode through a configuration register.
- Clock management: in order to reduce the power consumption, the clock controller can stop the clock to the core, individual peripherals, or memory.
- System clock source: four different clock sources can be used to drive the master clock SYSCLK:
  - 4 to 50 MHz high-speed external crystal or ceramic resonator (HSE). The HSE can also be configured in bypass mode for an external clock.
  - 144 MHz or 48 MHz on high-speed internal RC oscillator (HSI), trimmable by software
  - 144 MHz programmable-speed internal oscillator (PSI)
- Auxiliary clock source: two ultra‑low‑power clock sources that can be used to drive the real-time clock:
  - 32.768 kHz low-speed external crystal (LSE), supporting four drive capability modes. The LSE can also be configured in bypass mode for an external clock.
  - 32 kHz low-speed internal RC (LSI), also used to drive the independent watchdog.
- Peripheral clock sources: several peripherals have their own independent clock whatever the system clock. Two dividers, each with a large scale of configurable division factors, can generate independent clocks for the ADCs, USARTx, UARTx, SPIx, I2Cx, I3C1, and FDCAN (available only in STM32C552x devices).
- Startup clock: after reset, the microcontroller restarts by default with an internal 144 MHz clock (HSI). The prescaler ratio and clock source can be changed by the application program as soon as the code execution starts.
- Clock security system (CSS): this feature can be enabled by software. If an HSE clock failure occurs, the master clock automatically switches to HSI and a software interrupt is generated if enabled. LSE failure can also be detected and generates an interrupt.
- Clock-out capability:
  - MCO (microcontroller clock output): it outputs one of the internal clocks for external use by the application.
  - LSCO (low-speed clock output): it outputs LSI or LSE in all low-power modes.

Several prescalers allow AHB and APB frequencies configuration. The maximum frequency of the AHB and the APB clock domains is 144 MHz.

[unclear in source: "four different clock sources" is stated for SYSCLK, but only three (HSE, HSI, PSI) are listed.]

### 3.9 Clock recovery system (CRS)

The devices embed a special block that allows automatic trimming of the internal 144 MHz oscillator to guarantee its optimal accuracy over the whole device‑operational range. This automatic trimming is based on the external synchronization signal. This signal is either derived from USB_SOF signalization, from an LSE oscillator, from an external signal on the CRS_SYNC pin or generated by user software. For faster lock-in during startup, automatic‑trimming and manual‑trimming action can be combined.

### 3.10 General-purpose inputs/outputs (GPIOs)

Each of the GPIO pins can be configured by software as output (push‑pull or open‑drain), as input (with or without pull‑up or pull‑down) or as peripheral alternate function. Most of the GPIO pins are shared with digital or analog alternate functions.

After reset, all GPIOs are in Analog mode to reduce power consumption.

The I/Os alternate function configuration can be locked if needed following a specific sequence in order to avoid spurious writing to the I/Os registers.

### 3.11 Multi-AHB bus matrix

A 32-bit multi-AHB bus matrix interconnects all the masters (CPU, LPDMA1, LPDMA2) and the slave peripherals (flash memory, SRAMs, AHB, and APB). It also ensures a seamless and efficient operation even when several high-speed peripherals work simultaneously.

### 3.12 Low-power direct memory access controller (LPDMA)

The low-power direct memory access (LPDMA) controller is a bus master and system peripheral. The LPDMA is used to perform programmable data transfers between memory‑mapped peripherals and/or memories via linked‑lists, under the control of an off‑loaded CPU.

The LPDMA main features are:

- Single bidirectional AHB master
- Memory-mapped data transfers from a source to a destination:
  - Peripheral to memory
  - Memory to peripheral
  - Memory to memory
  - Peripheral to peripheral
- Transfers arbitration based on a 4-grade programmed priority at the channel level:
  - One high-priority traffic class for time-sensitive channels (queue 3)
  - Three low-priority traffic classes with a weighted round‑robin allocation for non‑time‑sensitive channels (queues 0, 1, 2)
- Per channel event generation on any of the following events: transfer complete, half transfer complete, data transfer error, user setting error, link transfer error, completed suspension, and trigger overrun
- 12 concurrent LPDMA channels (8‑channel LPDMA1, 4‑channel LPDMA2):
  - Intrachannel LPDMA transfers chaining via programmable linked‑list into memory, supporting two execution modes: run‑to‑completion and link step mode
  - Intrachannel and interchannel LPDMA transfers chaining via programmable LPDMA input triggers connection to LPDMA task completion events
- Per linked-list item within a channel:
  - Separately programmed source and destination transfers
  - Programmable data handling between source and destination: byte‑based padding or truncation, sign extension, and left/right realignment
  - Programmable number of data bytes to be transferred from the source, defining the block level
  - Linear source and destination addressing: either fixed or contiguously incremented addressing, programmed at a block level, between successive single transfers
  - Programmable LPDMA request and trigger selection
  - Programmable LPDMA half-transfer and transfer-complete events generation
  - Pointer to the next linked-list item and its data structure in memory, with automatic update of the LPDMA linked-list control registers
- Debug:
  - Channel suspend and resume support
  - Channel status reporting and event flags
- Privileged/unprivileged support:
  - Support for privileged and unprivileged LPDMA transfers, independently at the channel level
  - Privileged-aware AHB slave port

**Table 2. LPDMA1 channels implementation and usage**

| Channel x | Hardware parameter dma_fifo_size[x] | Hardware parameter dma_addressing[x] | Features |
|---|---|---|---|
| x = 0 to 7 | 0 | 0 | Channel x (x = 0 to 7) is implemented with: no FIFO (only a single source transfer cell is internally registered); fixed/contiguously incremented addressing |

**Table 3. LPDMA2 channels implementation and usage**

| Channel x | Hardware parameter dma_fifo_size[x] | Hardware parameter dma_addressing[x] | Features |
|---|---|---|---|
| x = 0 to 3 | 0 | 0 | Channel x (x = 0 to 3) is implemented with: no FIFO (only a single source transfer cell is internally registered); fixed/contiguously incremented addressing |

**Table 4. LPDMA1 and LPDMA2 autonomous mode and wake-up in low-power modes**

| Feature | Low-power modes |
|---|---|
| Wake-up | LPDMA1/2 in Sleep mode |

### 3.13 Interrupts and events

#### 3.13.1 Nested vectored interrupt controller (NVIC)

- 81 maskable interrupt channels (not including the 16 Cortex®‑M33 with FPU interrupt lines)
- 16 programmable priority levels (4 bits of interrupt priority used)
- Low-latency exception and interrupt handling
- Power management control
- Implementation of system control registers

The NVIC and the processor core interface are closely coupled, enabling low‑latency interrupt processing and efficient processing of late‑arriving interrupts. All interrupts, including the core exceptions, are managed by the NVIC.

#### 3.13.2 Extended interrupt and event controller (EXTI)

The extended interrupts and event controller (EXTI) manages the individual CPU and system wake‑up through configurable and direct event inputs. It provides wake‑up requests to the power control and generates an interrupt request to the CPU NVIC and events to the CPU event input. For the CPU, an additional event generation block (EVG) is needed to generate the CPU event signal.

The EXTI wake-up requests allow the system to wake up from Stop modes.

The interrupt request and event request generation can also be used in Run modes.

The EXTI also includes the EXTI mux I/O port selection.

The EXTI main features are the following:

- 35 input events are supported.
- All event inputs allow the possibility to wake up the system.
- Events that do not have an associated wake‑up flag in the peripheral have a flag in the EXTI and generate an interrupt to the CPU from the EXTI.
- Events can be used to generate a CPU wake‑up event.

The asynchronous event inputs are classified into two groups:

- Configurable events (signals from I/Os or peripherals able to generate a pulse), with the following features:
  - Selectable active trigger edge
  - Interrupt pending status register bits independent for the rising and falling edge
  - Individual interrupt and event generation mask, used for conditioning the CPU wake‑up, interrupt, and event generation
  - Software trigger possibility
  - EXTI I/O port selection
- Direct events (interrupt and wake-up sources from peripherals having an associated flag which requires to be cleared in the peripheral), with the following features:
  - Fixed rising edge active trigger
  - No interrupt pending status register bit in the EXTI (the interrupt pending status flag is provided by the peripheral generating the event)
  - Individual interrupt and event generation mask, used to condition the CPU wake‑up and event generation
  - No software trigger possibility

### 3.14 Cyclic redundancy check calculation unit (CRC)

The cyclic redundancy check calculation unit (CRC) calculation unit is used to get a CRC code from 8‑, 16‑, or 32‑bit data word and a generator polynomial.

Among other applications, CRC‑based techniques are used to verify data transmission or storage integrity. In the scope of the functional safety standards, they offer a means of verifying the flash memory integrity. The CRC calculation unit helps compute a signature of the software during runtime, to be compared with a reference signature generated at link time and stored at a given memory location.

### 3.15 Analog-to-digital converter (ADC)

The devices embed up to two analog-to-digital converters (ADC).

- ADC1 and ADC2 are tightly coupled and can operate in dual mode (ADC1 is the master).

Each ADC consists of one 12-bit successive approximation analog-to-digital converter. Each ADC has up to 14 multiplexed channels. A/D conversion of the various channels can be performed in single, continuous, scan, or discontinuous mode. The result of the ADC is stored in a left‑aligned or right‑aligned (default configuration) 32‑bit data register.

The ADCs are mapped on the AHB bus to allow fast data handling. The analog watchdog features allow the application to detect if the input voltage goes outside the user‑defined high or low thresholds.

A built-in hardware oversampler improves analog performance while off‑loading the related computational burden from the CPU. An efficient low‑power mode is implemented to allow very low consumption at low frequency.

The ADC main features are:

- High-performance features:
  - Up to two ADCs which can operate in dual mode
    - ADC1 is connected to 12 external channels and two internal channels.
    - ADC2 is connected to 14 external channels.
  - 12, 10, 8, or 6-bit configurable resolution
  - ADC conversion time independent from the AHB bus clock frequency
  - Faster conversion time by lowering resolution
  - AHB slave bus interface to allow fast data handling
  - Channel-wise programmable sampling time
  - Flexible sampling time control
  - Fixed latency for a trigger to start of sampling
  - Up to four injected channels (analog inputs assignment to regular or injected channels is fully configurable)
  - Data alignment with in-built data coherency
  - Data can be managed by DMA for regular channel conversions
  - Four dedicated data registers for the injected channels
- Low-power features:
  - Speed adaptive low-power mode to reduce ADC consumption when operating at low frequency
  - Allows slow bus frequency application while keeping optimum ADC performance
  - Provides automatic control to avoid ADC overrun in low AHB bus clock frequency application (autodelayed mode)
- Oversampler:
  - 32-bit data register
  - Oversampling ratio adjustable from 2 to 1024
  - Programmable data right and left shifts
- Data preconditioning:
  - Gain compensation
  - Offset compensation
- Analog input channels:
  - External analog inputs (per ADC): up to 14 GPIO pads
  - One channel for the internal reference voltage (VREFINT)
  - One channel for the internal temperature sensor (VSENSE)
- Start-of-conversion can be initiated:
  - By software for both regular and injected conversions
  - By hardware triggers with configurable polarity (internal timer events or GPIO input events) for both regular and injected conversions
- Conversion modes:
  - Each ADC can convert a single channel or can scan a sequence of channels
  - Single mode converts selected inputs once per trigger
  - Continuous mode converts selected inputs continuously
  - Discontinuous mode
- Interrupt generation at ADC ready, the end of sampling, the end of conversion (regular or injected), end of sequence conversion (regular or injected), analog watchdog 1, 2, or 3, or overrun events
- Three analog watchdogs per ADC
- ADC input range: VSSA ≤ VIN ≤ VREF+

**Table 5. ADC features**

| ADC modes/features | ADC1 | ADC2 |
|---|---|---|
| Resolution | 12 bits | 12 bits |
| Maximum sampling-speed | 2.25 Msps | 2.25 Msps |
| Hardware-offset calibration | X | X |
| Single-ended inputs | X | X |
| Injected channel conversion | X | X |
| Oversampling | up to x1024 | up to x1024 |
| Data register | 32 bits | 32 bits |
| DMA support | X | X |
| Offset compensation | X | X |
| Gain compensation | X | X |
| Number of analog watchdogs | 3 | 3 |

#### 3.15.1 Analog temperature sensor

The STM32C55xxx embed an analog temperature sensor that generates a voltage VSENSE that varies linearly with temperature. The temperature sensor is internally connected to the ADC input channel that is used to convert the sensor output voltage into a digital value.

The sensor provides good linearity but it must be calibrated to obtain a good accuracy of the temperature measurement. As the offset of the temperature sensor varies from chip to chip due to process variation, the uncalibrated internal temperature sensor is suitable for applications that detect temperature changes only.

To improve the accuracy of the temperature sensor measurement, each device is individually factory‑calibrated by STMicroelectronics. The temperature sensor factory calibration data are stored by STMicroelectronics in the system memory area, accessible in read‑only mode.

#### 3.15.2 Internal voltage reference (VREFINT)

The VREFINT provides a stable (bandgap) voltage output for the ADC and the comparator. It is internally connected to ADC input channel.

The precise voltage of VREFINT is individually measured for each part by STMicroelectronics during production test and stored in the system memory area. It is accessible in read‑only mode.

### 3.16 Digital to analog converter (DAC)

The DAC module is a 12‑bit, voltage output digital‑to‑analog converter. The DAC can be configured in 8‑ or 12‑bit mode and can be used in conjunction with the DMA controller. In 12‑bit mode, the data may be left‑aligned or right‑aligned.

An input reference pin, VREF+ (shared with others analog peripherals) is available for better resolution.

The DAC_OUT1 pin can be used as general-purpose input/output (GPIO) when the DAC output is disconnected from the output pad and connected to the on chip peripheral. The DAC output buffer can be optionally enabled to allow a high drive output current. An individual calibration can be applied DAC output channel. The DAC output channels support a low-power mode, the sample and hold mode.

The DAC main features are:

- Left or right data alignment in 12-bit mode
- Synchronized update capability
- Noise-wave and triangular-wave generation
- DMA capability for each channel including DMA underrun error detection
- Double-data DMA capability to reduce the bus activity
- External triggers for conversion
- DAC output-channel buffered/unbuffered modes
- Buffer offset calibration
- DAC output can be disconnected from the DAC_OUTx output pin
- DAC output connection to on chip peripherals
- Sample and hold mode for low-power operation in Stop mode
- Voltage reference input from VREF+ pin

### 3.17 Low-power comparator (COMP)

The device embeds a low-power comparator (COMP). It can be used for a variety of functions including:

- Wake-up from low-power mode triggered by an analog signal
- Analog signal conditioning
- Cycle-by-cycle current control loop when combined with a PWM output from a timer

The COMP main features are:

- Selectable inverting analog inputs:
  - I/O pins
  - DAC channel output
  - Internal reference voltage and three submultiple values (1/4, 1/2, 3/4) provided by the scaler (buffered voltage divider)
- I/O pins selectable as noninverting analog inputs
- Programmable hysteresis
- Programmable speed/consumption
- Mapping of outputs to I/Os
- Redirection of outputs to timer inputs for triggering:
  - Capture events
  - OCREF_CLR events (for cycle-by-cycle current control)
  - Break events for fast PWM shutdowns
- Blanking of comparator outputs
- Interrupt generation capability with wake-up from Sleep and Stop modes (through the EXTI controller)
- Direct interrupt output to the CPU

### 3.18 True random number generator (RNG)

The RNG is a true random number generator that provides full entropy outputs to the application as 32‑bit samples. It is composed of a live entropy source (analog) and an internal conditioning component.

The RNG is a NIST SP 800-90B compliant entropy source that can be used to construct a nondeterministic random bit generator (NDRBG).

The RNG can be certified NIST SP800-90B. It has also been tested using the German BSI statistical tests of AIS-31 (T0 to T8).

The RNG main features are the following:

- The RNG delivers 32-bit true random numbers, produced by an analog entropy source conditioned by a NIST SP800-90B approved conditioning stage.
- It can be used as the entropy source to construct a nondeterministic random bit generator (NDRBG).
- In the default configuration, it produces four 32-bit random samples every 412 AHB clock cycles if fAHB < fthreshold (256 RNG clock cycles otherwise).
- It embeds startup and NIST SP800-90B approved continuous health tests (repetition count and adaptive proportion tests), associated with specific error management.
- It can be disabled to reduce power consumption, or enabled with an automatic low power mode (default configuration).
- It has an AMBA® AHB slave peripheral, accessible through 32-bit word single accesses only (else an AHB bus error is generated, and the write accesses are ignored).

### 3.19 HASH processor (HASH)

The hash processor is a fully compliant implementation of the secure hash algorithm (SHA‑1, SHA‑2 family) and the HMAC (keyed‑hash message authentication code) algorithm. HMAC is suitable for applications requiring message authentication.

The hash processor computes FIPS (Federal Information Processing Standards) approved digests of lengths of 160, 224, and 256 bits for messages of any length less than 2 × 64 bits (for SHA‑1, SHA‑224, and SHA‑256). [unclear in source: printed as "2 × 64 bits"; the SHA-1/SHA-2 message length limit is normally 2^64 bits]

The HASH main features are:

- Suitable for data authentication applications, compliant with:
  - Federal Information Processing Standards Publication FIPS PUB 180‑4, Secure Hash Standard (SHA‑1 and SHA‑2 family)
  - Federal Information Processing Standards Publication FIPS PUB 186-4, Digital Signature Standard (DSS)
  - Internet Engineering Task Force (IETF) Request For Comments RFC 2104, HMAC: Keyed-Hashing for Message Authentication and Federal Information Processing Standards Publication FIPS PUB 198-1, The Keyed-Hash Message Authentication Code (HMAC)
- Fast computation of SHA-1, SHA2-224, SHA2-256:
  - 82 (respectively 66) clock cycles for processing one 512-bit block of data using SHA‑1 (respectively SHA‑256) algorithm
- Support for HMAC mode with all supported algorithms
- Corresponding 32-bit words of the digest from consecutive message blocks are added to each other to form the digest of the whole message.
  - Automatic 32-bit word swapping to comply with the internal little‑endian representation of the input bit‑string
  - Supported word swapping format: bits, bytes, half-words, and 32-bit words
- Single 32-bit, write-only, input register associated with an internal input FIFO, corresponding to a 64‑byte block size (16 × 32 bits)
- Automatic padding to complete the input bit string to fit the digest minimum block size
- AHB slave peripheral, accessible by 32-bit words only (else an AHB error is generated)
- 8 × 32-bit words (H0 to H15) for output message digest [unclear in source: "8 × 32-bit words" vs. the range "H0 to H15" (16 names) as printed]
- Automatic data flow control supporting direct memory access (DMA) using one channel
- Support for both single and fixed DMA burst transfers of four words
- Interruptible message digest computation, on a per‑block basis
  - Reloadable digest registers
  - Hashing computation suspend/resume mechanism, including DMA

### 3.20 Timers and watchdogs

The devices include two advanced control timers, up to eleven general‑purpose timers, two basic timers, two low‑power timers, two watchdog timers, and one SysTick timer.

The table below compares the features of the advanced control, general‑purpose and basic timers.

**Table 6. Timer feature comparison**

| Timer type | Timer | Counter resolution | Counter type | Prescaler factor | DMA request generation | Capture / compare channels | Complementary outputs |
|---|---|---|---|---|---|---|---|
| Advanced control | TIM1, TIM8 | 16 bits | Up, down, Up/down | Any integer between 1 and 65536 | Yes | 4 | 4 |
| General-purpose | TIM2, TIM5 | 32 bits | Up, down, Up/down | Any integer between 1 and 65536 | Yes | 4 | No |
| General-purpose | TIM12 | 16 bits | Up | Any integer between 1 and 65536 | No | 2 | No |
| General-purpose | TIM15 | 16 bits | Up, down, Up/down | Any integer between 1 and 65536 | Yes | 2 | 1 |
| General-purpose | TIM16, TIM17 | 16 bits | Up, down, Up/down | Any integer between 1 and 65536 | Yes | 1 | No |
| Basic | TIM6, TIM7 | 16 bits | Up | Any integer between 1 and 65536 | Yes | 0 | No |

#### 3.20.1 Advanced-control timers (TIM1/TIM8)

The advanced-control timers (TIM1/TIM8) consist of a 16-bit autoreload counter driven by a programmable prescaler.

They may be used for various purposes, including measuring the pulse lengths of input signals (input capture) or generating output waveforms (output compare, PWM, complementary PWM with dead-time insertion).

Pulse lengths and waveform periods can be modulated from a few microseconds to several milliseconds using the timer prescaler and the RCC clock controller prescalers.

TIM1/TIM8 timer features include:

- 16-bit up, down, up/down autoreload counter
- 16-bit programmable prescaler allowing dividing (also “on the fly”) the counter clock frequency by any factor from 1 to 65536
- Seven independent channels for:
  - Input capture (except channels 5, 6, and 7)
  - Output compare
  - PWM generation (edge- and center-aligned mode)
  - One-pulse mode output
- Complementary outputs with programmable dead-time
- Synchronization circuit to control the timer with external signals and to interconnect several timers together
- Repetition counter to update the timer registers only after a given number of cycles of the counter
- Two break inputs to put the timer’s output signals in a safe user‑selectable configuration
- Interrupt/DMA generation on the following events:
  - Update: counter overflow/underflow, counter initialization (by software or internal/external trigger)
  - Trigger event (counter start, stop, initialization, or count by internal/external trigger)
  - Input capture
  - Output compare
- Incremental encoders, quadrature encoders, and hall‑sensors support
- Trigger input for external clock or cycle-by-cycle current management
- ADC synchronization for jitter-free sampling points

#### 3.20.2 General-purpose timers (TIM2/TIM5/TIM12/TIM15/TIM16/TIM17)

The general-purpose timers (TIMx) consist of a 16-bit or 32-bit autoreload counter driven by a programmable prescaler.

They can be used for various purposes, including measuring the pulse lengths of input signals (input capture) or generating output waveforms (output compare and PWM).

Pulse lengths and waveform periods can be modulated from a few microseconds to several milliseconds using the timer prescaler and the RCC clock controller prescalers.

General-purpose TIMx timer features include:

- 16-bit or 32-bit up, down, up/down autoreload counter
- 16-bit programmable prescaler used to divide (also “on the fly”) the counter clock frequency by any factor between 1 and 65535
- Up to four independent channels for:
  - Input capture
  - Output compare
  - PWM generation (edge- and center-aligned modes)
  - One-pulse mode output
- Synchronization circuit to control the timer with external signals and to interconnect several timers
- Interrupt/DMA generation on the following events:
  - Update: counter overflow/underflow, counter initialization (by software or internal/external trigger)
  - Trigger event (counter start, stop, initialization, or count by internal/external trigger)
  - Input capture
  - Output compare
- Supports incremental (quadrature) encoder and hall-sensor circuitry for positioning purposes
- Trigger input for external clock or cycle-by-cycle current management
- ADC synchronization for jitter-free sampling points

#### 3.20.3 Basic timers (TIM6/TIM7)

The basic timers (TIM6/TIM7) consist of a 16-bit autoreload counter driven by a programmable prescaler.

They can be used as generic timers for time-base generation.

The basic timer can also be used for triggering the digital-to-analog converter. This is done with the trigger output of the timer.

The timers are completely independent and do not share any resources.

Basic timer (TIM6/TIM7) features include:

- 16-bit autoreload upcounter
- 16-bit programmable prescaler used to divide (also “on the fly”) the counter clock frequency by any factor between 1 and 65535
- Synchronization circuit to trigger the DAC
- Interrupt/DMA generation on the update event: counter overflow
- ADC synchronization for jitter-free sampling points

#### 3.20.4 Low-power timers (LPTIM1)

The LPTIM is a 16-bit timer that benefits from the ultimate developments in power consumption reduction. Thanks to its diversity of clock sources, the LPTIM can keep running in all power modes except for Standby mode. Given its capability to run even with no internal clock source, the LPTIM can be used as a pulse counter, which can be useful in some applications. The LPTIM capability to wake up the system from low‑power modes makes it suitable to realize timeout functions with extremely low-power consumption.

The low-power timer supports the following features:

- 16-bit up counter with 16-bit auto reload register
- 3-bit prescaler with eight possible dividing factors (1, 2, 4, 8, 16, 32, 64, 128)
- Selectable clock
  - Internal clock sources: LSE, LSI, HSI, or APB clock
  - External clock source over LPTIM input (working with no LP oscillator running, used by pulse counter application)
- 16-bit ARR auto reload register
- 16-bit capture/compare register
- Continuous/one-shot mode
- Selectable software/hardware input trigger
- Programmable digital glitch filter
- Configurable output: pulse, PWM
- Configurable I/O polarity
- Encoder mode
- Repetition counter
- Up to two independent channels for:
  - Input capture
  - PWM generation (edge-aligned mode)
  - One-pulse mode output
- Interrupt generation on ten events
- DMA request generation on the following events:
  - Update event
  - Input capture

#### 3.20.5 Independent watchdog (IWDG)

The independent watchdog (IWDG) peripheral offers a high safety level due to its capability to detect malfunctions caused by software or hardware failures.

The IWDG is clocked by an independent clock and remains active even if the main clock fails.

Additionally, the watchdog function is performed in the VDD voltage domain, allowing the IWDG to remain functional even in low‑power modes.

The IWDG main features are:

- 12-bit down-counter
- Dual voltage domain, thus enabling operation in low-power modes
- Independent clock
- Early wake-up interrupt generation
- Reset generation:
  - In case of timeout
  - In case of refresh outside the expected window

#### 3.20.6 Window watchdog (WWDG)

The system window watchdog (WWDG) is used to detect the occurrence of a software fault, usually generated by external interference or unforeseen logical conditions, which causes the application program to abandon its normal sequence.

The watchdog circuit generates a reset on the expiry of a programmed time period unless the program refreshes the contents of the down-counter before the T6 bit is cleared. A reset is also generated if the 7‑bit down‑counter value (in the control register) is refreshed before the down-counter reaches the window register value. This implies that the counter must be refreshed in a limited window.

The WWDG clock is prescaled from the APB clock and has a configurable time window that can be programmed to detect abnormally late or early application behavior.

The WWDG is best suited for applications requiring the watchdog to react within an accurate timing window.

The WWDG main features are:

- Programmable free-running down-counter
- Conditional reset:
  - Reset (if watchdog activated) when the down-counter value becomes lower than 0x40
  - Reset (if watchdog activated) if the down-counter is reloaded outside the window
- Early wake-up interrupt (EWI): triggered (if enabled and the watchdog activated) when the down‑counter is equal to 0x40

#### 3.20.7 SysTick timer

The Cortex®-M33 embeds one SysTick timer.

This timer is dedicated to real‑time operating systems, but can also be used as a standard down counter. It features:

- A 24-bit down counter
- Auto reload capability
- Maskable system interrupt generation when the counter reaches 0
- Programmable clock source

### 3.21 Real-time clock (RTC), tamper and backup registers

#### 3.21.1 Real-time clock (RTC)

The real-time clock (RTC) supports the following features:

- Calendar with subsecond, seconds, minutes, hours (12 or 24 format), weekday, date, month, year, in BCD (binary‑coded decimal) format
- Binary mode with 32-bit free-running counter
- Automatic correction for 28, 29 (leap year), 30, and 31 days of the month
- Two programmable alarms
- On-the-fly correction from 1 to 32767 RTC clock pulses. This can be used to synchronize it with a controller clock.
- Reference clock detection: a more precise second source clock (50 or 60 Hz) can be used to enhance the calendar precision.
- Digital calibration circuit with 0.95 ppm resolution, to compensate for quartz crystal inaccuracy
- Timestamp feature that can be used to save the calendar content. This function can be triggered by an event on the timestamp pin, or by a tamper event.
- 17-bit auto-reload wake-up timer (WUT) for periodic events with programmable resolution and period
- Privilege protection support:
  - Alarm A, alarm B, wake-up timer, and timestamp individual privileged protection

The RTC is functional in all low-power modes when it is clocked by the LSE.

All RTC events (alarm, wake-up timer, timestamp) can generate an interrupt and wake up the device from the low‑power modes.

#### 3.21.2 Tamper and backup registers (TAMP)

The antitamper detection circuit is used to protect sensitive data from external attacks. Thirty-two 32‑bit backup registers are retained in all low-power modes. The backup registers, as well as other secrets in the device, are protected by this antitamper detection circuit with three tamper pins and six internal tampers. The external tamper pins can be configured for edge detection or level detection with or without filtering.

The TAMP main features are:

- A tamper detection can optionally erase the backup registers, SRAM2, ICACHE, and cryptographic peripherals. The device resources protected by tamper are named “device secrets”.
- 32 × 32‑bit backup registers
- Up to three tamper pins for three external tamper detection events:
  - Passive tampers: Ultralow-power edge or level detection with internal pull-up hardware management
  - Configurable digital filter
- Six internal tamper events to protect against transient attacks
- Each tamper can be configured in two modes:
  - Confirmed mode: immediate erase of secrets on tamper detection, including backup registers erase
  - Potential mode: most of the secrets erase following a tamper detection are launched by software
- Any tamper detection can generate an RTC timestamp event
- Tamper configuration and backup registers privilege protection

### 3.22 Inter-integrated circuit interface (I2C)

The device embeds two I2C interfaces. Refer to Table 7 for feature implementation.

The I2C bus interface handles communications between the microcontroller and the serial I2C bus. It controls all I2C bus‑specific sequencing, protocol, arbitration, and timing.

It supports Standard-mode (Sm), Fast-mode (Fm), and Fast-mode Plus (Fm+).

The I2C peripheral is also system management bus (SMBus) and power management bus (PMBus®) compatible.

It can use DMA to reduce the CPU load.

The I²C peripheral supports:

- I²C-bus specification rev03 compatibility:
  - Controller and target modes
  - Multicontroller capability
  - Standard-mode (up to 100 kHz)
  - Fast-mode (up to 400 kHz)
  - Fast-mode Plus (up to 1 MHz)
  - 7-bit and 10-bit addressing mode
  - Multiple 7-bit target addresses (2 addresses, 1 with configurable mask)
  - All 7-bit addresses acknowledge mode
  - General call
  - Programmable setup and hold times
  - Easy-to-use event management
  - Clock stretching (optional)
- 1-byte buffer with DMA capability
- Programmable analog and digital noise filters
- SMBus specification rev 3.0 compatibility:
  - Hardware PEC (packet error checking) generation and verification with ACK control
  - Command and data acknowledge control
  - Address resolution protocol (ARP) support
  - Host and device support – SMBus alert
  - Timeouts and idle condition detection
- PMBus rev 1.3 standard compatibility
- Independent clock
- Wake-up from Stop mode on address match

**Table 7. I2C implementation**

| Features(1) | I2C1 | I2C2 |
|---|---|---|
| Standard-mode (up to 100 Kbit/s) | X | X |
| Fast mode (up to 400 Kbit/s) | X | X |
| Fast mode plus (Fm+) with 20 mA output drive I/Os (up to 1 Mbit/s) | X | X |
| Programmable analog and digital noise filters | X | X |
| SMBus/PMBus hardware support | X | X |
| Independent clock | X | X |
| Wake-up capability | X | X |

Notes:

1. X = supported.

### 3.23 Improved inter-integrated circuit interface (I3C)

The I3C interface handles communication between this device and others, such as sensors and the host processor, connected on an I3C bus.

An I3C bus is a two-wire, serial single-ended, multidrop bus, intended to improve a legacy I2C bus.

The I3C SDR-only peripheral implements all the features required by the MIPI® I3C specification v1.1. It can control all I3C bus-specific sequencing, protocol, arbitration, and timing, and can act as a controller (formerly known as master) or as a target (formerly known as slave). When acting as a controller, the I3C peripheral improves the features of the I2C interface while preserving some backward compatibility: it allows an I2C target to operate on an I3C bus in legacy I2C fast mode (Fm) or legacy I2C fast mode plus (Fm+), provided that the latter does not perform clock stretching. The I3C peripheral can be used with DMA to offload the CPU.

The I3C peripheral supports:

- MIPI® I3C specification v1.1, as:
  - I3C SDR-only primary controller
  - I3C SDR-only secondary controller
  - I3C SDR-only target
- I3C SCL bus clock frequency up to 12.5 MHz
- Registers configuration from the host application via the APB target port
- Queued data transfers:
  - Transmit FIFO (TX-FIFO) for data bytes/words to be transmitted on the I3C bus
  - Receive FIFO (RX-FIFO) for received data bytes/words on the I3C bus
  - For each FIFO, optional DMA mode with a dedicated DMA channel
- Queued control/status transfers, when controller:
  - Control FIFO (C-FIFO) for control words to be sent on the I3C bus
  - Optional status FIFO (S-FIFO) for status words as received on the I3C bus
  - For each FIFO, optional DMA mode with a dedicated DMA channel
- Messages:
  - Legacy I²C read/write messages to legacy I2C targets in Fm/Fm+
  - I3C SDR read/write private messages
  - I3C SDR broadcast CCC messages
  - I3C SDR read/write direct CCC messages
- Frame-level management, when controller:
  - Optional C-FIFO and TX-FIFO preload
  - Multiple messages encapsulation
  - Optional arbitrable header generation on the I3C bus
  - HDR exit pattern generation on the I3C bus for error recovery
- Programmable bus timing, when controller:
  - SCL high and low period
  - SDA hold time
  - Bus free (minimum) time
  - Bus available/idle condition time
  - Clock stall time
- Target-initiated requests management:
  - Simultaneous support up to four targets, when controller
  - In-band interrupts, with programmable IBI payload (up to four bytes), with pending read notification support
  - Bus control request, with recovery flow support and hand-off delay
  - Hot-join mechanism
- HDR exit pattern detection, when target
- Bus error management:
  - CEx with x = 0, 1, 2, 3 when controller
  - TEx with x = 0, 1, ... , 6 when target
  - Bus control switch error and recovery
  - Target reset
- Individual programmable event-based management:
  - Per-event identification with flag reporting and clear control
  - Host application notification via flag polling, and/or via interrupt with a per-event programmable enable
  - Error type identification
- Wake-up from Stop mode(s), as controller:
  - On an in-band interrupt without payload
  - On a hot-join request
  - On a controller-role request
- Wake-up from Stop mode(s), as target:
  - On a reset pattern
  - On a missed start
- Multiclock domain management:
  - Separate APB clock and kernel clock, driven from independently programmed clock sources via the RCC, in addition to SCL clock
  - Minimum operating frequency for the kernel clock and the APB clock vs. the application-driven SCL clock

**Table 8. I3C peripheral controller/target features versus MIPI® v1.1**

| Features(1) | MIPI® I3C v1.1 | I3C peripheral when controller | I3C peripheral when target | Comments |
|---|---|---|---|---|
| I3CSDR message | X | X | X | - |
| Legacy I2C message (Fm/Fm+) | X | X | - | Mandatory when controller and the I3C bus is mixed with (external) legacy I2C target(s). Optional in MIPI v1.1 when target. |
| HDR DDR message | X | - | - | Optional in MIPI v1.1 |
| HDR-TSL/TSP, HDR-BT | X | - | - | Optional in MIPI v1.1 |
| Dynamic address assignment | X | X | X | - |
| Static address | X | X | - | No (intended) support of I3C peripheral as a target on an I2C bus. |
| Grouped addressing | X | X | - | Optional in MIPI v1.1 |
| CCCs | X | X | X | Mandatory CCCs and some optional CCCs are supported. |
| Error detection and recovery | X | X | X | - |
| In-band interrupt (with MDB) | X | X | X | - |
| Secondary controller | X | X | X | - |
| Hot-join mechanism | X | X | X | - |
| Target reset | X | X | X | - |
| Synchronous timing control | X | X | - | Optional in MIPI v1.1 |
| Asynchronous timing control 0 | X | X | - | Optional in MIPI v1.1 |
| Asynchronous timing control 1, 2, 3 | X | - | - | Optional in MIPI v1.1 |
| Device-to-device tunneling | X | X | - | Optional in MIPI v1.1 |
| Multilane data transfer | X | X | - | Optional in MIPI v1.1 |
| Monitoring device early termination | X | - | - | Optional in MIPI v1.1 |

Notes:

1. X = supported.

### 3.24 Universal synchronous/asynchronous receiver transmitter (USART/UART) and low-power universal asynchronous receiver transmitter (LPUART)

The devices have four embedded universal synchronous receiver transmitters (USART1/2/3), three universal asynchronous receiver transmitters (UART4/5), and one low‑power universal asynchronous receiver transmitter (LPUART1).

**Table 9. USART, UART, and LPUART features**

| Features(1) | USART1/2/3 | UART4/5 | LPUART1 |
|---|---|---|---|
| Hardware flow control for modem | X | X | X |
| Continuous communication using DMA | X | X | X |
| Multiprocessor communication | X | X | X |
| Synchronous mode (controller/target) | X | - | - |
| Smartcard mode | X | - | - |
| Single-wire half-duplex communication | X | X | X |
| IrDA SIR ENDEC block | X | X | - |
| LIN mode | X | X | - |
| Dual-clock domain and wake-up from Stop mode | X(2) | X(2) | X(2) |
| Receiver timeout interrupt | X | X | X |
| Modbus communication | X | X | X |
| Autobaud rate detection | X | X | X |
| Driver enable | X | X | X |
| USART data length | 7, 8, and 9 bits | 7, 8, and 9 bits | 7, 8, and 9 bits |
| Tx/Rx FIFO | X | X | X |
| Tx/Rx FIFO size | 8 bytes | 8 bytes | 8 bytes |

Notes:

1. X = supported.
2. Wake‑up supported from Stop mode.

#### 3.24.1 Universal synchronous/asynchronous receiver transmitter (USART/UART)

The USART offers a flexible means to perform full‑duplex data exchange with external equipment requiring an industry standard NRZ asynchronous serial data format. A very wide range of baud rates can be achieved through a fractional baud rate generator.

The USART supports both synchronous one-way and half-duplex single-wire communications, as well as LIN (local interconnection network), Smartcard protocol, IrDA (infrared data association) SIR ENDEC specifications, and modem operations (CTS/RTS). Multiprocessor communications are also supported.

High-speed data communications are possible by using the DMA (direct memory access) for multibuffer configuration.

The USART main features are:

- Full-duplex asynchronous communication
- NRZ standard format (mark/space)
- Configurable oversampling method by 16 or 8 to achieve the best compromise between speed and clock tolerance
- Baud rate generator systems
- Two internal FIFOs for transmit and receive data
- Each FIFO can be enabled/disabled by software and come with a status flag.
- A common programmable transmit and receive baud rate
- Dual-clock domain with dedicated kernel clock for peripherals independent from PCLK
- Auto baud rate detection
- Programmable data word length (7, 8, or 9 bits)
- Programmable data order with MSB-first or LSB-first shifting
- Configurable stop bits (one or two stop bits)
- Synchronous controller/target mode and clock output/input for synchronous communications
- SPI controller transmission underrun error flag
- Single-wire half-duplex communications
- Continuous communications using DMA
- Received/transmitted bytes are buffered in reserved SRAM using centralized DMA
- Separate enable bits for transmitter and receiver
- Separate signal polarity control for transmission and reception
- Swappable Tx/Rx pin configuration
- Hardware flow control for modem and RS-485 transceiver
- Communication control/error detection flags
- Parity control:
  - Transmits parity bit
  - Checks parity of received data byte
- Interrupt sources with flags
- Multiprocessor communications: wake-up from Mute mode by idle line detection or address mark detection
- Wake-up from Stop capability
- LIN controller synchronous break send capability and LIN target break detection capability
  - 13-bit break generation and 10/11-bit break detection when USART is hardware configured for LIN
- IrDA SIR encoder decoder supporting 3/16-bit duration for Normal mode
- Smartcard mode
  - Supports the T = 0 and T = 1 asynchronous protocols for smartcards as defined in the ISO/IEC 7816‑3 standard
  - 0.5 and 1.5 stop bits for Smartcard operation
- Support for Modbus communication
  - Timeout feature
  - CR/LF character recognition

#### 3.24.2 Low-power universal asynchronous receiver transmitter (LPUART)

The LPUART is a UART, which enables bidirectional UART communications with a limited power consumption. Only a 32.768 kHz LSE clock is required to enable UART communications up to 9600 bauds. Higher baud rates can be reached when the LPUART is clocked by clock sources different from the LSE clock.

Even when the microcontroller is in low-power mode, the LPUART can wait for an incoming UART frame while having an extremely low energy consumption. The LPUART includes all necessary hardware support to make asynchronous serial communications possible with minimum power consumption.

It supports half-duplex single-wire communications and modem operations (CTS/RTS).

It also supports multiprocessor communications. The direct memory access (DMA) can be used for data transmission/reception.

The LPUART main features are:

- Full-duplex asynchronous communications
- NRZ standard format (mark/space)
- Programmable baud rate
- From 300 bauds to 9600 bauds using a 32.768 kHz clock source
- Higher baud rates can be achieved by using a higher frequency clock source
- Two internal FIFOs to transmit and receive data. Each FIFO can be enabled/disabled by software and come with status flags for FIFOs states.
- Dual-clock domain with dedicated kernel clock for peripherals independent from PCLK
- Programmable data word length (7 or 8 or 9 bits)
- Programmable data order with MSB‑first or LSB‑first shifting
- Configurable stop bits (one or two stop bits)
- Single-wire half-duplex communications
- Continuous communications using DMA
- Received/transmitted bytes are buffered in reserved SRAM using centralized DMA
- Separate enable bits for transmitter and receiver
- Separate signal polarity control for transmission and reception
- Swappable Tx/Rx pin configuration
- Hardware flow control for modem and RS‑485 transceiver
- Transfer detection flags:
  - Receive buffer full
  - Transmit buffer empty
  - Busy and end of transmission flags
- Parity control:
  - Transmits parity bit
  - Checks parity of received data byte
- Four error detection flags:
  - Overrun error
  - Noise detection
  - Frame error
  - Parity error
- Interrupt sources with flags
- Multiprocessor communications: wake-up from Mute mode by idle line detection or address mark detection
- Wake-up from Stop mode

### 3.25 Serial peripheral interface (SPI)/Inter-integrated sound interfaces (I2S)

The devices embed three serial peripheral interfaces (SPI) that can be used to communicate with external devices while using the specific synchronous protocol. The SPI protocol supports half‑duplex, full‑duplex, and simplex synchronous, serial communication with external devices.

**Table 10. SPI features**

| SPI feature | SPI2S1, SPI2S2, SPI2S3 (full feature set instances) |
|---|---|
| Data size | Configurable from 4 to 32-bit |
| CRC computation | CRC polynomial length configurable from 5 to 32‑bit |
| Size of FIFOs | 16 × 8-bit |
| Number of transferred data | Unlimited, expandable |
| I2S feature | Yes |

The serial peripheral interface (SPI) can be used to communicate with external devices while using the specific synchronous protocol. The SPI protocol supports half-duplex, full-duplex, and simplex synchronous, serial communication with external devices. The interface can be configured as master or slave and can operate in multimaster or multislave configurations. The device configured as master provides a communication clock (SCK) to the slave device. The slave select (SS) and ready (RDY) signals can be applied optionally just to set up communication with a specific slave and to ensure it handles the data flow properly. The Motorola® data format is used by default, but some other specific modes are supported as well.

The SPI main features are:

- Full-duplex synchronous transfers on three lines
- Half-duplex synchronous transfer on two lines (with bidirectional data line)
- Simplex synchronous transfers on two lines (with unidirectional data line)
- From 4-bit up to 32-bit data size selection
- Multimaster or multislave mode capability
- Dual clock domain, the peripheral kernel clock is independent from the APB bus clock
- Baud rate prescaler up to kernel frequency/2 or bypass from RCC in master mode
- Protection of configuration and setting
- Hardware or software management of SS for both master and slave
- Adjustable minimum delays between data and between SS and data flow
- Configurable SS signal polarity and timing, MISO × MOSI swap capability
- Programmable clock polarity and phase
- Programmable data order with MSB-first or LSB-first shifting
- Programmable number of data within a transaction to control SS and CRC
- Dedicated transmission and reception flags with interrupt capability
- SPI Motorola and TI format support
- Hardware CRC can verify the integrity of the communication at the end of a transaction by:
  - Adding CRC value in Tx mode
  - Automatic CRC error checking for Rx mode
- Error detection with interrupt capability in case of data overrun, CRC error, data underrun, mode fault, and frame error, depending on the operating mode
- Two 8-bit width embedded Rx and Tx FIFOs (FIFO size depends on instance)
- Configurable FIFO thresholds (data packing)
- Capability to handle data streams by system DMA controller
- Configurable behavior at slave underrun condition (support of cascaded circular buffers)
- Optional status pin RDY signaling that the slave device is ready to handle the data flow

The I2S main features are:

- Full duplex communication
- Simplex communication (only transmitter or receiver)
- Master or slave operations
- 8-bit programmable linear prescaler
- Data length can be 16, 24, or 32 bits
- Channel length can be 16 or 32 in master, any value in slave
- Programmable clock polarity
- Error flags signaling for improved reliability: Underrun, overrun, and frame errors
- Embedded Rx and Tx FIFOs
- Supported I2S protocols:
  - I2S Philips standard
  - MSB-justified standard (left-justified)
  - LSB-justified standard (right-justified)
  - PCM standard (with short and long frame synchronization)
- Data ordering programmable (LSB or MSB first)
- DMA capability for transmission and reception
- Master clock can be output to drive an external audio component:
  - FMCK = 256 × FWS for all I2S modes
  - FMCK = 128 × FWS for all PCM modes

### 3.26 Controller area network (FDCAN) (available only in STM32C552x devices)

The controller area network (CAN) subsystem consists of one CAN module, a shared message RAM memory, and a configuration block.

The modules (FDCAN) are compliant with ISO 11898-1: 2015 (CAN protocol specification version 2.0 part A, B) and CAN FD protocol specification version 1.0.

A 0.8-Kbyte message RAM implements filters, receives FIFOs, transmits event FIFOs, and transmits FIFOs.

The FDCAN main features are:

- Conform with CAN protocol version 2.0 part A, B, and ISO 11898-1: 2015, -4
- CAN FD with maximum 64 data bytes supported
- CAN error logging
- AUTOSAR and J1939 support
- Improved acceptance filtering
- Two receive FIFOs of three payloads each (up to 64 bytes per payload)
- Separate signaling on reception of high priority messages
- Configurable transmit FIFO/queue of three payloads (up to 64 bytes per payload)
- Configurable transmit event FIFO
- Programmable loop-back test mode
- Maskable module interrupts
- Two clock domains: APB bus interface and CAN core kernel clock
- Power-down support

### 3.27 Universal serial bus full-speed host/device interface (USB)

The USB peripheral implements an interface between a full‑speed USB 2.0 bus and the APB2 bus. USB suspend and resume are supported, which permits stopping the device clocks for low‑power consumption.

The USB main features are:

- USB specification version 2.0 full-speed compliant
- Supports both host and device modes
- Configurable number of endpoints from 1 to 8
- Dedicated packet buffer memory (SRAM) of 2048 bytes
- Cyclic redundancy check (CRC) generation/checking, non-return-to-zero inverted (NRZI) encoding/decoding, and bit‑stuffing
- Isochronous transfers support
- Double-buffered bulk/isochronous endpoint/channel support
- USB suspend and resume operations
- Frame-locked clock pulse generation
- USB 2.0 link power management support (device mode only)
- Battery charging specification revision 1.2 support (device mode only)
- USB connect/disconnect capability (controllable embedded pull-up resistor on USB_DP line)

### 3.28 Development support

#### 3.28.1 Serial-wire/JTAG debug port (SWJ-DP)

The Arm® SWJ-DP interface is embedded and is a combined JTAG and serial‑wire debug port that enables either a serial wire debug or a JTAG probe to be connected to the target.

Debug is performed using two pins only instead of five required by the JTAG (JTAG pins can be reused as GPIO with alternate function): the JTAG TMS and TCK pins are shared with SWDIO and SWCLK, respectively, and a specific sequence on the TMS pin is used to switch between JTAG‑DP and SW‑DP.

#### 3.28.2 Embedded Trace Macrocell™

The Arm® Embedded Trace Macrocell™ (ETM) provides a greater visibility of the instruction and data flow inside the CPU core by streaming compressed data at a very high rate from the devices through a small number of ETM pins to an external hardware trace port analyzer (TPA) device.

Real-time instruction and data flow activity be recorded and then formatted for display on the host computer that runs the debugger software. TPA hardware is commercially available from common development tool vendors.

The ETM operates with third party debugger software tools.

## 4 Pinouts/ballouts, pin description, and alternate functions

### 4.1 Pinout/ballout schematics

All pinout figures in this section are drawn as a package top view. Every package is a quad (four-sided) package with pin 1 at the top of the left side. Pin numbers increase counter-clockwise: down the left side (top to bottom), along the bottom side (left to right), up the right side (bottom to top), and along the top side (right to left). In the tables below, each column lists one side of the package in that numbering order.

The pin numbers shown in these figures are the same as the per-package pin-number columns of Table 12 in Section 4.2.

**Figure 3. LQFP32 pinout**

LQFP32, package top view, 8 pins per side, no exposed pad. On this package, pin 2 is labeled `PH0-OSC_IN/PC14` (Table 12 lists both PH0-OSC_IN and PC14-OSC32_IN at pin 2). Pin 31 is `PB8-BOOT0`. There is no PB1 and no PA10 on this package; pins 16 and 32 are VSS.

| Left (pins 1–8) | Bottom (pins 9–16) | Right (pins 17–24) | Top (pins 25–32) |
|---|---|---|---|
| 1: VDD | 9: PA3 | 17: VDD | 25: PA15 |
| 2: PH0-OSC_IN/PC14 | 10: PA4 | 18: PB15 | 26: PB3 |
| 3: PH1-OSC_OUT | 11: PA5 | 19: PA8 | 27: PB4 |
| 4: NRST | 12: PA6 | 20: PA9 | 28: PB5 |
| 5: VREF+ | 13: PA7 | 21: PA11 | 29: PB6 |
| 6: PA0 | 14: PB0 | 22: PA12 | 30: PB7 |
| 7: PA1 | 15: VCAP | 23: PA13 | 31: PB8-BOOT0 |
| 8: PA2 | 16: VSS | 24: PA14 | 32: VSS |

**Figure 4. UFQFPN32 pinout**

UFQFPN32, package top view, 8 pins per side, with an exposed pad on the underside labeled VSS. Pin 2 is labeled `PH0-OSC_IN/PC14` (same as LQFP32). Compared with LQFP32, the VSS pins 16 and 32 are replaced: pin 15 is PB1, pin 16 is VCAP, pin 31 is `PH2-BOOT0`, and pin 32 is PB8. Ground is provided only through the exposed pad.

| Left (pins 1–8) | Bottom (pins 9–16) | Right (pins 17–24) | Top (pins 25–32) |
|---|---|---|---|
| 1: VDD | 9: PA3 | 17: VDD | 25: PA15 |
| 2: PH0-OSC_IN/PC14 | 10: PA4 | 18: PB15 | 26: PB3 |
| 3: PH1-OSC_OUT | 11: PA5 | 19: PA8 | 27: PB4 |
| 4: NRST | 12: PA6 | 20: PA9 | 28: PB5 |
| 5: VREF+ | 13: PA7 | 21: PA11 | 29: PB6 |
| 6: PA0 | 14: PB0 | 22: PA12 | 30: PB7 |
| 7: PA1 | 15: PB1 | 23: PA13 | 31: PH2-BOOT0 |
| 8: PA2 | 16: VCAP | 24: PA14 | 32: PB8 |
| | | | Exposed pad: VSS |

Note: There is an exposed die pad on the underside of the UFQFPN package. This backside pad must be connected and soldered to PCB ground.

**Figure 5. LQFP48 pinout**

LQFP48, package top view, 12 pins per side, no exposed pad.

| Left (pins 1–12) | Bottom (pins 13–24) | Right (pins 25–36) | Top (pins 37–48) |
|---|---|---|---|
| 1: PE2 | 13: PA3 | 25: PB12 | 37: PA14 |
| 2: PC13 | 14: PA4 | 26: PB13 | 38: PA15 |
| 3: PC14-OSC32_IN | 15: PA5 | 27: PB14 | 39: PB3 |
| 4: PC15-OSC32_OUT | 16: PA6 | 28: PB15 | 40: PB4 |
| 5: PH0-OSC_IN | 17: PA7 | 29: PA8 | 41: PB5 |
| 6: PH1-OSC_OUT | 18: PB0 | 30: PA9 | 42: PB6 |
| 7: NRST | 19: PB1 | 31: PA10 | 43: PB7 |
| 8: VREF- | 20: PB2 | 32: PA11 | 44: PH2-BOOT0 |
| 9: VREF+ | 21: PB10 | 33: PA12 | 45: PB8 |
| 10: PA0 | 22: VCAP | 34: PA13 | 46: PB9 |
| 11: PA1 | 23: VSS | 35: VSS | 47: VSS |
| 12: PA2 | 24: VDD | 36: VDD | 48: VDD |

**Figure 6. UFQFPN48 pinout**

UFQFPN48, package top view, 12 pins per side, with an exposed pad on the underside labeled VSS. The pin assignment is identical to LQFP48 (pins 23, 35 and 47 are still VSS pins in addition to the exposed pad).

| Left (pins 1–12) | Bottom (pins 13–24) | Right (pins 25–36) | Top (pins 37–48) |
|---|---|---|---|
| 1: PE2 | 13: PA3 | 25: PB12 | 37: PA14 |
| 2: PC13 | 14: PA4 | 26: PB13 | 38: PA15 |
| 3: PC14-OSC32_IN | 15: PA5 | 27: PB14 | 39: PB3 |
| 4: PC15-OSC32_OUT | 16: PA6 | 28: PB15 | 40: PB4 |
| 5: PH0-OSC_IN | 17: PA7 | 29: PA8 | 41: PB5 |
| 6: PH1-OSC_OUT | 18: PB0 | 30: PA9 | 42: PB6 |
| 7: NRST | 19: PB1 | 31: PA10 | 43: PB7 |
| 8: VREF- | 20: PB2 | 32: PA11 | 44: PH2-BOOT0 |
| 9: VREF+ | 21: PB10 | 33: PA12 | 45: PB8 |
| 10: PA0 | 22: VCAP | 34: PA13 | 46: PB9 |
| 11: PA1 | 23: VSS | 35: VSS | 47: VSS |
| 12: PA2 | 24: VDD | 36: VDD | 48: VDD |
| | | | Exposed pad: VSS |

Note: There is an exposed die pad on the underside of the UFQFPN package. This backside pad must be connected and soldered to PCB ground.

**Figure 7. LQFP64 pinout**

LQFP64, package top view, 16 pins per side, no exposed pad.

| Left (pins 1–16) | Bottom (pins 17–32) | Right (pins 33–48) | Top (pins 49–64) |
|---|---|---|---|
| 1: PE2 | 17: PA3 | 33: PB12 | 49: PA14 |
| 2: PC13 | 18: VSS | 34: PB13 | 50: PA15 |
| 3: PC14-OSC32_IN | 19: VDD | 35: PB14 | 51: PC10 |
| 4: PC15-OSC32_OUT | 20: PA4 | 36: PB15 | 52: PC11 |
| 5: PH0-OSC_IN | 21: PA5 | 37: PC6 | 53: PC12 |
| 6: PH1-OSC_OUT | 22: PA6 | 38: PC7 | 54: PD2 |
| 7: NRST | 23: PA7 | 39: PC8 | 55: PB3 |
| 8: PC0 | 24: PC4 | 40: PC9 | 56: PB4 |
| 9: PC1 | 25: PC5 | 41: PA8 | 57: PB5 |
| 10: PC2 | 26: PB0 | 42: PA9 | 58: PB6 |
| 11: PC3 | 27: PB1 | 43: PA10 | 59: PB7 |
| 12: VREF- | 28: PB2 | 44: PA11 | 60: PH2-BOOT0 |
| 13: VREF+ | 29: PB10 | 45: PA12 | 61: PB8 |
| 14: PA0 | 30: VCAP | 46: PA13 | 62: PB9 |
| 15: PA1 | 31: VSS | 47: VSS | 63: VSS |
| 16: PA2 | 32: VDD | 48: VDD | 64: VDD |

**Figure 8. LQFP64 alternative pinout**

LQFP64, package top view, 16 pins per side, no exposed pad. This alternative pinout applies to the STM32C55xRxTxJ part number (see note below and note 1 of Table 12). It is identical to the standard LQFP64 pinout of Figure 7 except for pins 2, 3 and 4: in the alternative pinout these are PE3, PE4 and PE5, whereas in the standard pinout they are PC13, PC14-OSC32_IN and PC15-OSC32_OUT. As a result, PC13, PC14-OSC32_IN and PC15-OSC32_OUT are not available in the alternative-pinout package (Table 12 shows "-" for them in that column).

| Left (pins 1–16) | Bottom (pins 17–32) | Right (pins 33–48) | Top (pins 49–64) |
|---|---|---|---|
| 1: PE2 | 17: PA3 | 33: PB12 | 49: PA14 |
| 2: PE3 | 18: VSS | 34: PB13 | 50: PA15 |
| 3: PE4 | 19: VDD | 35: PB14 | 51: PC10 |
| 4: PE5 | 20: PA4 | 36: PB15 | 52: PC11 |
| 5: PH0-OSC_IN | 21: PA5 | 37: PC6 | 53: PC12 |
| 6: PH1-OSC_OUT | 22: PA6 | 38: PC7 | 54: PD2 |
| 7: NRST | 23: PA7 | 39: PC8 | 55: PB3 |
| 8: PC0 | 24: PC4 | 40: PC9 | 56: PB4 |
| 9: PC1 | 25: PC5 | 41: PA8 | 57: PB5 |
| 10: PC2 | 26: PB0 | 42: PA9 | 58: PB6 |
| 11: PC3 | 27: PB1 | 43: PA10 | 59: PB7 |
| 12: VREF- | 28: PB2 | 44: PA11 | 60: PH2-BOOT0 |
| 13: VREF+ | 29: PB10 | 45: PA12 | 61: PB8 |
| 14: PA0 | 30: VCAP | 46: PA13 | 62: PB9 |
| 15: PA1 | 31: VSS | 47: VSS | 63: VSS |
| 16: PA2 | 32: VDD | 48: VDD | 64: VDD |

Note: Pinout for STM32C55xRxTxJ part number.

**Figure 9. LQFP80 pinout**

LQFP80, package top view, 20 pins per side, no exposed pad.

| Left (pins 1–20) | Bottom (pins 21–40) | Right (pins 41–60) | Top (pins 61–80) |
|---|---|---|---|
| 1: PE2 | 21: PA3 | 41: PB12 | 61: PA14 |
| 2: PE3 | 22: VSS | 42: PB13 | 62: PA15 |
| 3: PC13 | 23: VDD | 43: PB14 | 63: PC10 |
| 4: PC14-OSC32_IN | 24: PA4 | 44: PB15 | 64: PC11 |
| 5: PC15-OSC32_OUT | 25: PA5 | 45: PD12 | 65: PC12 |
| 6: VSS | 26: PA6 | 46: PD13 | 66: PD0 |
| 7: VDD | 27: PA7 | 47: PD14 | 67: PD1 |
| 8: PH0-OSC_IN | 28: PC4 | 48: PD15 | 68: PD2 |
| 9: PH1-OSC_OUT | 29: PC5 | 49: PC6 | 69: PB3 |
| 10: NRST | 30: PB0 | 50: PC7 | 70: PB4 |
| 11: PC0 | 31: PB1 | 51: PC8 | 71: PB5 |
| 12: PC1 | 32: PB2 | 52: PC9 | 72: PB6 |
| 13: PC2 | 33: PE7 | 53: PA8 | 73: PB7 |
| 14: PC3 | 34: PE8 | 54: PA9 | 74: PH2-BOOT0 |
| 15: VREF- | 35: PE9 | 55: PA10 | 75: PB8 |
| 16: VREF+ | 36: PE10 | 56: PA11 | 76: PB9 |
| 17: PH5 | 37: PB10 | 57: PA12 | 77: PE0 |
| 18: PA0 | 38: VCAP | 58: PA13 | 78: PE1 |
| 19: PA1 | 39: VSS | 59: VSS | 79: VSS |
| 20: PA2 | 40: VDD | 60: VDD | 80: VDD |

**Figure 10. LQFP100 pinout**

LQFP100, package top view, 25 pins per side, no exposed pad.

| Left (pins 1–25) | Bottom (pins 26–50) | Right (pins 51–75) | Top (pins 76–100) |
|---|---|---|---|
| 1: PE2 | 26: PA3 | 51: PB12 | 76: PA14 |
| 2: PE3 | 27: VSS | 52: PB13 | 77: PA15 |
| 3: PE4 | 28: VDD | 53: PB14 | 78: PC10 |
| 4: PE5 | 29: PA4 | 54: PB15 | 79: PC11 |
| 5: PE6 | 30: PA5 | 55: PD8 | 80: PC12 |
| 6: PH15 | 31: PA6 | 56: PD9 | 81: PD0 |
| 7: PC13 | 32: PA7 | 57: PD10 | 82: PD1 |
| 8: PC14-OSC32_IN | 33: PC4 | 58: PD11 | 83: PD2 |
| 9: PC15-OSC32_OUT | 34: PC5 | 59: PD12 | 84: PD3 |
| 10: VSS | 35: PB0 | 60: PD13 | 85: PD4 |
| 11: VDD | 36: PB1 | 61: PD14 | 86: PD5 |
| 12: PH0-OSC_IN | 37: PB2 | 62: PD15 | 87: PD6 |
| 13: PH1-OSC_OUT | 38: PE7 | 63: PC6 | 88: PD7 |
| 14: NRST | 39: PE8 | 64: PC7 | 89: PB3 |
| 15: PC0 | 40: PE9 | 65: PC8 | 90: PB4 |
| 16: PC1 | 41: PE10 | 66: PC9 | 91: PB5 |
| 17: PC2 | 42: PE11 | 67: PA8 | 92: PB6 |
| 18: PC3 | 43: PE12 | 68: PA9 | 93: PB7 |
| 19: PH4 | 44: PE13 | 69: PA10 | 94: PH2-BOOT0 |
| 20: VREF- | 45: PE14 | 70: PA11 | 95: PB8 |
| 21: VREF+ | 46: PE15 | 71: PA12 | 96: PB9 |
| 22: PH5 | 47: PB10 | 72: PA13 | 97: PE0 |
| 23: PA0 | 48: VCAP | 73: PH3 | 98: PE1 |
| 24: PA1 | 49: VSS | 74: VSS | 99: VSS |
| 25: PA2 | 50: VDD | 75: VDD | 100: VDD |

### 4.2 Pin description

**Table 11. Legend/abbreviations used in the pinout table**

| Name | Abbreviation | Definition |
|---|---|---|
| Pin name | | Unless otherwise specified in brackets below the pin name, the pin function during and after reset is the same as the actual pin name. |
| Pin type | I | Input-only pin |
| Pin type | I/O | Input/output pin |
| Pin type | S | Supply pin |
| I/O structure | FT | 5 V-tolerant I/O |
| I/O structure | TT | 3.6 V-tolerant I/O |
| I/O structure | RST | Bidirectional reset pin with embedded weak pull‑up resistor |
| I/O structure — options for TT and FT I/Os (1) | _a | I/O with analog switch function supplied by VDDA |
| I/O structure — options for TT and FT I/Os (1) | _t | Tamper I/O |
| I/O structure — options for TT and FT I/Os (1) | _f | I/O fm+ capable |
| I/O structure — options for TT and FT I/Os (1) | _u | I/O with USB function |
| Notes | | Unless otherwise specified by a note, all I/Os are set as floating inputs during and after reset. |
| Pin functions | Alternate functions | Functions selected through GPIOx_AFR registers |
| Pin functions | Additional functions | Functions directly selected/enabled through peripheral registers |

Notes:

1. The related I/O structures in the table below are a concatenation of various options. Examples: FT, TT_a.

**Table 12. STM32C55xxx pin/ball definition**

The first eight columns give the pin number in each package ("-" means the pin is not available in that package). The "LQFP64 alt (1)" column is the LQFP64 alternative pinout. The pin name column shows the pin name followed, in parentheses, by the function after reset when it differs from the pin name.

| LQFP32 | UFQFPN32 | LQFP48 | UFQFPN48 | LQFP64 | LQFP64 alt (1) | LQFP80 | LQFP100 | Pin name (function after reset) | Pin type | I/O structure | Notes | Alternate functions | Additional functions |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| - | - | 1 | 1 | 1 | 1 | 1 | 1 | PE2 | I/O | FT | - | TRACECLK, LPTIM1_IN2, SPI3_SCK/I2S3_CK, EVENTOUT | - |
| - | - | - | - | - | 2 | 2 | 2 | PE3 | I/O | FT | - | TRACED0, TIM15_BKIN, USART1_RX, EVENTOUT | - |
| - | - | - | - | - | 3 | - | 3 | PE4 | I/O | FT | - | TRACED1, TIM15_CH1N, SPI3_NSS/I2S3_WS, USART1_TX, EVENTOUT | - |
| - | - | - | - | - | 4 | - | 4 | PE5 | I/O | FT | - | TRACED2, TIM15_CH1, SPI3_MISO/I2S3_SDI, USART1_CK, EVENTOUT | - |
| - | - | - | - | - | - | - | 5 | PE6 | I/O | FT | - | TRACED3, TIM1_BKIN2, TIM15_CH2, SPI3_MOSI/I2S3_SDO, USART1_CTS/USART1_NSS, EVENTOUT | WKUP3 |
| - | - | - | - | - | - | - | 6 | PH15 | I/O | FT | - | USART1_RTS, EVENTOUT | - |
| - | - | 2 | 2 | 2 | - | 3 | 7 | PC13 | I/O | FT_t | (2)(3)(4) | FDCAN1_TX, EVENTOUT | TAMP_IN1, RTC_OUT1/RTC_TS, WKUP4 |
| 2 | 2 | 3 | 3 | 3 | - | 4 | 8 | PC14-OSC32_IN (OSC32_IN) | I/O | FT | (2)(4) | TIM12_CH1, FDCAN1_RX, EVENTOUT | OSC32_IN |
| - | - | 4 | 4 | 4 | - | 5 | 9 | PC15-OSC32_OUT (OSC32_OUT) | I/O | FT | (2) | TIM12_CH2, EVENTOUT | OSC32_OUT |
| - | - | - | - | - | - | 6 | 10 | VSS | S | - | - | - | - |
| - | - | - | - | - | - | 7 | 11 | VDD | S | - | - | - | - |
| 2 | 2 | 5 | 5 | 5 | 5 | 8 | 12 | PH0-OSC_IN (PH0) | I/O | FT_f | - | I2C1_SDA, EVENTOUT | OSC_IN |
| 3 | 3 | 6 | 6 | 6 | 6 | 9 | 13 | PH1-OSC_OUT (PH1) | I/O | FT_f | - | I2C1_SCL, EVENTOUT | OSC_OUT |
| 4 | 4 | 7 | 7 | 7 | 7 | 10 | 14 | NRST | I/O | RST | - | - | - |
| - | - | - | - | 8 | 8 | 11 | 15 | PC0 | I/O | FT_a | - | SPI2_RDY, TIM16_BKIN, EVENTOUT | ADC1_IN8 |
| - | - | - | - | 9 | 9 | 12 | 16 | PC1 | I/O | FT_ta | - | TRACED0, SPI2_MOSI/I2S2_SDO, EVENTOUT | ADC1_IN9, ADC2_IN9, TAMP_IN2, WKUP6 |
| - | - | - | - | 10 | 10 | 13 | 17 | PC2 | I/O | FT_a | - | PWR_CSLEEP, TIM17_CH1, SPI2_MISO/I2S2_SDI, EVENTOUT | ADC1_IN10, ADC2_IN10 |
| - | - | - | - | 11 | 11 | 14 | 18 | PC3 | I/O | FT_a | - | PWR_CSTOP, LPUART1_TX, SPI2_MOSI/I2S2_SDO, EVENTOUT | ADC1_IN11, ADC2_IN11 |
| - | - | - | - | - | - | - | 19 | PH4 | I/O | FT_a | - | EVENTOUT | ADC2_IN12 |
| - | - | 8 | 8 | 12 | 12 | 15 | 20 | VREF- | S | - | - | - | - |
| 5 | 5 | 9 | 9 | 13 | 13 | 16 | 21 | VREF+ | S | - | - | - | - |
| - | - | - | - | - | - | 17 | 22 | PH5 | I/O | FT_a | - | EVENTOUT | ADC2_IN13 |
| 6 | 6 | 10 | 10 | 14 | 14 | 18 | 23 | PA0 | I/O | FT_ta | - | TIM2_CH1, TIM5_CH1, TIM8_ETR, TIM15_BKIN, SPI2_RDY, SPI3_RDY, USART2_CTS/USART2_NSS, UART4_TX, SPI2_NSS/I2S2_WS, TIM2_ETR, EVENTOUT | ADC1_IN0, ADC2_IN0, COMP1_INP1, TAMP_IN2, WKUP1 |
| 7 | 7 | 11 | 11 | 15 | 15 | 19 | 24 | PA1 | I/O | FT_ta | - | TIM2_CH2, TIM5_CH2, TIM8_BKIN, TIM15_CH1N, LPTIM1_IN1, USART2_RTS, UART4_RX, EVENTOUT | ADC1_IN1, ADC2_IN1, TAMP_IN3 |
| 8 | 8 | 12 | 12 | 16 | 16 | 20 | 25 | PA2 | I/O | FT_ta | - | TIM2_CH3, TIM5_CH3, LPUART1_RX, TIM15_CH1, LPTIM1_IN2, USART2_TX, EVENTOUT | ADC1_IN2, ADC2_IN2, TAMP_IN3, WKUP2 |
| 9 | 9 | 13 | 13 | 17 | 17 | 21 | 26 | PA3 | I/O | FT_a | - | TIM2_CH4, TIM5_CH4, LPUART1_TX, TIM15_CH2, SPI2_NSS/I2S2_WS, SPI3_MOSI/I2S3_SDO, USART2_RX, COMP1_OUT, EVENTOUT | ADC1_IN3, ADC2_IN3 |
| - | - | - | - | 18 | 18 | 22 | 27 | VSS | S | - | - | - | - |
| - | - | - | - | 19 | 19 | 23 | 28 | VDD | S | - | - | - | - |
| 10 | 10 | 14 | 14 | 20 | 20 | 24 | 29 | PA4 | I/O | TT_a | - | TIM5_ETR, SPI3_MOSI/I2S3_SDO, SPI1_NSS/I2S1_WS, SPI3_NSS/I2S3_WS, USART2_CK, EVENTOUT | ADC1_IN4, DAC1_OUT1 |
| 11 | 11 | 15 | 15 | 21 | 21 | 25 | 30 | PA5 | I/O | FT_a | - | TIM2_CH1, TIM1_CH3, TIM8_CH1N, SPI1_SCK/I2S1_CK, SPI2_SCK/I2S2_CK, USART1_CTS/USART1_NSS, TIM2_ETR, EVENTOUT | ADC1_IN5, COMP1_INM3 |
| 12 | 12 | 16 | 16 | 22 | 22 | 26 | 31 | PA6 | I/O | FT_a | - | TIM1_BKIN, TIM5_CH1, TIM8_BKIN, SPI1_MISO/I2S1_SDI, USART1_TX, LPUART1_RTS, EVENTOUT | ADC1_IN6 |
| 13 | 13 | 17 | 17 | 23 | 23 | 27 | 32 | PA7 | I/O | FT_a | - | TIM1_CH1N, TIM5_CH2, TIM8_CH1N, TIM15_CH1, SPI1_MOSI/I2S1_SDO, SPI2_MISO/I2S2_SDI, USART1_RX, LPUART1_CTS, EVENTOUT | ADC1_IN7 |
| - | - | - | - | 24 | 24 | 28 | 33 | PC4 | I/O | FT_a | - | TIM2_CH4, TIM8_BKIN, I2S1_MCK, USART3_RX, TIM16_CH1, EVENTOUT | ADC2_IN4, COMP1_INM1 |
| - | - | - | - | 25 | 25 | 29 | 34 | PC5 | I/O | FT_a | - | TIM1_CH4N, TIM8_BKIN2, TIM16_CH1N, COMP1_OUT, EVENTOUT | ADC2_IN5 |
| 14 | 14 | 18 | 18 | 26 | 26 | 30 | 35 | PB0 | I/O | FT_a | - | TIM1_CH2N, TIM5_CH3, TIM8_CH2N, SPI3_MISO/I2S3_SDI, USART2_TX, UART4_CTS, EVENTOUT | ADC2_IN6, COMP1_INP2 |
| - | 15 | 19 | 19 | 27 | 27 | 31 | 36 | PB1 | I/O | FT_a | - | TIM1_CH3N, TIM5_CH4, TIM8_CH3N, SPI3_SCK/I2S3_CK, SPI2_NSS/I2S2_WS, USART3_RX, COMP1_OUT, EVENTOUT | ADC2_IN7, COMP1_INM2 |
| - | - | 20 | 20 | 28 | 28 | 32 | 37 | PB2 | I/O | FT_a | - | RTC_OUT2, TIM8_CH4N, SPI1_RDY, LPTIM1_CH1, SPI2_SCK/I2S2_CK, SPI3_MOSI/I2S3_SDO, EVENTOUT | ADC2_IN8, COMP1_INP3, LSCO |
| - | - | - | - | - | - | 33 | 38 | PE7 | I/O | FT | - | TIM1_ETR, EVENTOUT | - |
| - | - | - | - | - | - | 34 | 39 | PE8 | I/O | FT | - | TIM1_CH1N, EVENTOUT | - |
| - | - | - | - | - | - | 35 | 40 | PE9 | I/O | FT | - | TIM1_CH1, EVENTOUT | - |
| - | - | - | - | - | - | 36 | 41 | PE10 | I/O | FT | - | TIM1_CH2N, EVENTOUT | - |
| - | - | - | - | - | - | - | 42 | PE11 | I/O | FT | - | TIM1_CH2, SPI1_RDY, EVENTOUT | - |
| - | - | - | - | - | - | - | 43 | PE12 | I/O | FT | - | TIM1_CH3N, COMP1_OUT, EVENTOUT | - |
| - | - | - | - | - | - | - | 44 | PE13 | I/O | FT | - | TIM1_CH3, EVENTOUT | - |
| - | - | - | - | - | - | - | 45 | PE14 | I/O | FT | - | TIM1_CH4, EVENTOUT | - |
| - | - | - | - | - | - | - | 46 | PE15 | I/O | FT | - | TIM1_BKIN, TIM1_CH4N, EVENTOUT | - |
| - | - | 21 | 21 | 29 | 29 | 37 | 47 | PB10 | I/O | FT_f | - | TIM2_CH3, TIM8_CH1, LPTIM1_IN1, I2C2_SCL, SPI2_SCK/I2S2_CK, USART3_TX, EVENTOUT | - |
| 15 | 16 | 22 | 22 | 30 | 30 | 38 | 48 | VCAP | S | - | - | - | - |
| 16 | - | 23 | 23 | 31 | 31 | 39 | 49 | VSS | S | - | - | - | - |
| 17 | 17 | 24 | 24 | 32 | 32 | 40 | 50 | VDD | S | - | - | - | - |
| - | - | 25 | 25 | 33 | 33 | 41 | 51 | PB12 | I/O | FT_f | (4) | TIM1_BKIN, TIM8_CH3, I2C2_SDA, SPI2_NSS/I2S2_WS, USART3_CK, FDCAN1_RX, UART5_RX, EVENTOUT | - |
| - | - | 26 | 26 | 34 | 34 | 42 | 52 | PB13 | I/O | FT | (4) | TIM1_CH1N, TIM8_CH2, LPTIM1_CH1, I2C2_SMBA, SPI2_SCK/I2S2_CK, USART3_CTS/USART3_NSS, LPUART1_RX, FDCAN1_TX, UART5_TX, EVENTOUT | - |
| - | - | 27 | 27 | 35 | 35 | 43 | 53 | PB14 | I/O | FT | - | TIM1_CH2N, TIM12_CH1, TIM8_CH2N, USART1_TX, SPI2_MISO/I2S2_SDI, USART3_RTS, UART4_RTS, EVENTOUT | - |
| 18 | 18 | 28 | 28 | 36 | 36 | 44 | 54 | PB15 | I/O | FT | - | RTC_REFIN, TIM1_CH3N, TIM12_CH2, TIM8_CH3N, USART1_RX, SPI2_MOSI/I2S2_SDO, SPI1_MOSI/I2S1_SDO, SPI3_MOSI/I2S3_SDO, UART4_CTS, UART5_RX, EVENTOUT | - |
| - | - | - | - | - | - | - | 55 | PD8 | I/O | FT | - | USART3_TX, EVENTOUT | - |
| - | - | - | - | - | - | - | 56 | PD9 | I/O | FT | - | USART3_RX, EVENTOUT | - |
| - | - | - | - | - | - | - | 57 | PD10 | I/O | FT | - | MCO2, LPTIM1_CH2, USART3_CK, EVENTOUT | - |
| - | - | - | - | - | - | - | 58 | PD11 | I/O | FT | - | LPTIM1_IN2, USART3_CTS/USART3_NSS, UART4_RX, EVENTOUT | - |
| - | - | - | - | - | - | 45 | 59 | PD12 | I/O | FT | - | LPTIM1_IN1, TIM8_CH1N, I3C1_SCL, USART3_RTS, UART4_TX, EVENTOUT | - |
| - | - | - | - | - | - | 46 | 60 | PD13 | I/O | FT | - | LPTIM1_CH1, TIM8_CH2N, I3C1_SDA, EVENTOUT | - |
| - | - | - | - | - | - | 47 | 61 | PD14 | I/O | FT | - | TIM8_CH3N, EVENTOUT | - |
| - | - | - | - | - | - | 48 | 62 | PD15 | I/O | FT | - | TIM8_CH4N, EVENTOUT | - |
| - | - | - | - | 37 | 37 | 49 | 63 | PC6 | I/O | FT | - | TIM5_CH1, TIM8_CH1, I2S2_MCK, EVENTOUT | - |
| - | - | - | - | 38 | 38 | 50 | 64 | PC7 | I/O | FT | - | TIM5_CH2, TIM8_CH2, I2S3_MCK, EVENTOUT | - |
| - | - | - | - | 39 | 39 | 51 | 65 | PC8 | I/O | FT | - | TRACED1, TIM5_CH3, TIM8_CH3, UART5_RTS, EVENTOUT | - |
| - | - | - | - | 40 | 40 | 52 | 66 | PC9 | I/O | FT_f | - | MCO2, TIM5_CH4, TIM8_CH4, AUDIOCLK, UART5_CTS, I2C1_SDA, EVENTOUT | - |
| 19 | 19 | 29 | 29 | 41 | 41 | 53 | 67 | PA8 | I/O | FT_f | - | MCO1, TIM1_CH1, I3C1_SDA, TIM8_BKIN2, TIM15_CH2, SPI1_RDY, SPI2_MOSI/I2S2_SDO, USART1_CK, TIM5_CH4, I2C1_SCL, TIM2_CH4, EVENTOUT | - |
| 20 | 20 | 30 | 30 | 42 | 42 | 54 | 68 | PA9 | I/O | FT | - | MCO2, TIM1_CH2, I3C1_SCL, LPUART1_TX, TIM15_CH1N, SPI2_SCK/I2S2_CK, USART1_TX, TIM5_ETR, I2C1_SMBA, TIM8_CH2N, EVENTOUT | - |
| - | - | 31 | 31 | 43 | 43 | 55 | 69 | PA10 | I/O | FT | - | TIM1_CH3, LPUART1_RX, USART1_RX, EVENTOUT | - |
| 21 | 21 | 32 | 32 | 44 | 44 | 56 | 70 | PA11 | I/O | FT_fu | (4) | TIM1_CH4, LPUART1_CTS, USART2_TX, SPI2_NSS/I2S2_WS, UART4_RX, USART1_CTS/USART1_NSS, I2C2_SCL, FDCAN1_RX, EVENTOUT | USB_DM |
| 22 | 22 | 33 | 33 | 45 | 45 | 57 | 71 | PA12 | I/O | FT_fu | (4) | TIM1_ETR, LPUART1_RTS, USART2_RX, SPI2_SCK/I2S2_CK, UART4_TX, USART1_RTS, I2C2_SDA, FDCAN1_TX, EVENTOUT | USB_DP |
| 23 | 23 | 34 | 34 | 46 | 46 | 58 | 72 | PA13 (JTMS/SWDIO) | I/O | FT | (5) | JTMS/SWDIO, COMP1_OUT, EVENTOUT | - |
| - | - | - | - | - | - | - | 73 | PH3 | I/O | FT | - | EVENTOUT | - |
| - | - | 35 | 35 | 47 | 47 | 59 | 74 | VSS | S | - | - | - | - |
| - | - | 36 | 36 | 48 | 48 | 60 | 75 | VDD | S | - | - | - | - |
| 24 | 24 | 37 | 37 | 49 | 49 | 61 | 76 | PA14 (JTCK/SWCLK) | I/O | FT | (5) | JTCK/SWCLK, EVENTOUT | - |
| 25 | 25 | 38 | 38 | 50 | 50 | 62 | 77 | PA15(JTDI) | I/O | FT | (5) | JTDI, TIM2_CH1, TIM1_CH2N, LPTIM1_ETR, I2C2_SMBA, SPI1_NSS/I2S1_WS, SPI3_NSS/I2S3_WS, USART2_CK, UART4_RTS, USART1_TX, TIM8_CH4N, TIM2_ETR, EVENTOUT | - |
| - | - | - | - | 51 | 51 | 63 | 78 | PC10 | I/O | FT | - | TIM8_CH1N, I3C1_SCL, SPI3_SCK/I2S3_CK, USART3_TX, UART4_TX, EVENTOUT | - |
| - | - | - | - | 52 | 52 | 64 | 79 | PC11 | I/O | FT | - | TIM8_CH2N, I3C1_SDA, SPI3_MISO/I2S3_SDI, USART3_RX, UART4_RX, EVENTOUT | - |
| - | - | - | - | 53 | 53 | 65 | 80 | PC12 | I/O | FT | - | TRACED3, TIM15_CH1, TIM8_CH3N, SPI3_MOSI/I2S3_SDO, USART3_CK, UART5_TX, EVENTOUT | - |
| - | - | - | - | - | - | 66 | 81 | PD0 | I/O | FT | (4) | TIM8_CH4N, UART4_RX, FDCAN1_RX, EVENTOUT | - |
| - | - | - | - | - | - | 67 | 82 | PD1 | I/O | FT | (4) | UART4_TX, FDCAN1_TX, EVENTOUT | - |
| - | - | - | - | 54 | 54 | 68 | 83 | PD2 | I/O | FT | - | TRACED2, TIM15_BKIN, UART5_RX, EVENTOUT | WKUP7 |
| - | - | - | - | - | - | - | 84 | PD3 | I/O | FT | - | SPI2_SCK/I2S2_CK, USART2_CTS/USART2_NSS, EVENTOUT | - |
| - | - | - | - | - | - | - | 85 | PD4 | I/O | FT | - | USART2_RTS, EVENTOUT | - |
| - | - | - | - | - | - | - | 86 | PD5 | I/O | FT | (4) | TIM1_CH4N, SPI2_RDY, USART2_TX, FDCAN1_TX, EVENTOUT | - |
| - | - | - | - | - | - | - | 87 | PD6 | I/O | FT | - | SPI3_MOSI/I2S3_SDO, USART2_RX, EVENTOUT | - |
| - | - | - | - | - | - | - | 88 | PD7 | I/O | FT | - | SPI1_MOSI/I2S1_SDO, SPI3_MISO/I2S3_SDI, USART2_CK, EVENTOUT | - |
| 26 | 26 | 39 | 39 | 55 | 55 | 69 | 89 | PB3 (JTDO/TRACESWO) | I/O | FT_f | (4) | JTDO/TRACESWO, TIM2_CH2, TIM5_CH3, I2C2_SDA, SPI1_SCK/I2S1_CK, SPI3_SCK/I2S3_CK, LPUART1_TX, I2C2_SCL, CRS_SYNC, USART3_TX, TIM8_CH1, UART5_RTS, EVENTOUT | - |
| 27 | 27 | 40 | 40 | 56 | 56 | 70 | 90 | PB4 (NJTRST) | I/O | FT_f | (5) | NJTRST, TIM5_CH1, I3C1_SCL, LPTIM1_CH2, SPI1_MISO/I2S1_SDI, SPI3_MISO/I2S3_SDI, SPI2_NSS/I2S2_WS, LPUART1_CTS, I2C2_SDA, TIM16_BKIN, USART3_RX, TIM8_CH2, UART5_CTS, EVENTOUT | - |
| 28 | 28 | 41 | 41 | 57 | 57 | 71 | 91 | PB5 | I/O | FT | (4) | TIM17_BKIN, TIM5_CH2, I3C1_SDA, I2C1_SMBA, SPI1_MOSI/I2S1_SDO, SPI3_MOSI/I2S3_SDO, LPUART1_RTS, FDCAN1_RX, USART3_CK, TIM8_CH3, UART5_RX, EVENTOUT | - |
| 29 | 29 | 42 | 42 | 58 | 58 | 72 | 92 | PB6 | I/O | FT_f | (4) | I3C1_SCL, I2C1_SCL, SPI3_MISO/I2S3_SDI, USART1_TX, LPUART1_TX, FDCAN1_TX, TIM16_CH1N, USART3_CTS/USART3_NSS, TIM8_CH4, UART5_TX, EVENTOUT | - |
| 30 | 30 | 43 | 43 | 59 | 59 | 73 | 93 | PB7 | I/O | FT_f | (4) | TIM17_CH1N, I3C1_SDA, I2C1_SDA, SPI3_SCK/I2S3_CK, USART1_RX, LPUART1_RX, FDCAN1_TX, TIM16_CH1, USART3_RTS, EVENTOUT | WKUP5 |
| - | 31 | 44 | 44 | 60 | 60 | 74 | 94 | PH2-BOOT0 | I/O | FT | (4) | MCO1, TIM17_CH1N, LPTIM1_IN2, FDCAN1_RX, EVENTOUT | - |
| 31 | - | - | - | - | - | - | - | PB8-BOOT0 | I/O | FT_f | (4) | TIM17_CH1, I3C1_SCL, I2C1_SCL, SPI3_NSS/I2S3_WS, UART4_RX, FDCAN1_RX, EVENTOUT | - |
| - | 32 | 45 | 45 | 61 | 61 | 75 | 95 | PB8 | I/O | FT_f | (4) | TIM17_CH1, I3C1_SCL, I2C1_SCL, SPI3_NSS/I2S3_WS, UART4_RX, FDCAN1_RX, EVENTOUT | - |
| - | - | 46 | 46 | 62 | 62 | 76 | 96 | PB9 | I/O | FT | (4) | I3C1_SDA, I2C1_SDA, SPI2_NSS/I2S2_WS, SPI3_SCK/I2S3_CK, UART4_TX, FDCAN1_TX, EVENTOUT | - |
| - | - | - | - | - | - | 77 | 97 | PE0 | I/O | FT | (4) | LPTIM1_ETR, SPI3_RDY, FDCAN1_RX, EVENTOUT | - |
| - | - | - | - | - | - | 78 | 98 | PE1 | I/O | FT | (4) | LPTIM1_IN2, FDCAN1_TX, EVENTOUT | - |
| 32 | - | 47 | 47 | 63 | 63 | 79 | 99 | VSS | S | - | - | - | - |
| 1 | 1 | 48 | 48 | 64 | 64 | 80 | 100 | VDD | S | - | - | - | - |

Notes:

1. Pinout for STM32C55xRxTxJ part number.
2. After a RTC domain reset, PC13, PC14, and PC15 operate as GPIOs. Their function depends on the content of the RTC registers that are not reset by the system reset. For details on how to manage these GPIOs, refer to the backup domain and RTC register descriptions in the product reference manual
3. PC13 port toggling might disturbs low speed crystal connected on LSE PC14 and PC15. Refer to product Errata for more details.
4. FDCAN1 is only available on STM32C552x devices.
5. After reset, this pin is configured as JTAG/SWD alternate functions. The internal pull-up on PA15, PA13, PB4 pins and the internal pull-down on PA14 pin are activated.

### 4.3 Alternate functions

Table 13 gives, for every GPIO pin, the peripheral signal assigned to each alternate function number AF0 to AF15. A `-` means no function is assigned to that AF number on that pin. Cells containing two names separated by `/` (for example `SPI1_NSS/I2S1_WS`, `USART2_CTS/USART2_NSS`, `JTDO/TRACESWO`) are single cells of the source table and are reproduced as written.

Table 13 covers ports A, B, C, D, E, and H. Port B has no PB11 row and port H has only PH0 to PH5 and PH15. Which pins are bonded out in each package is given in Table 12.

**Table 13. Alternate functions: peripheral groups per AF number**

The table header row of Table 13 lists the peripherals whose signals appear in each AF column:

| AF | Peripherals |
|---|---|
| AF0 | SYS |
| AF1 | LPTIM1/TIM1/2/17 |
| AF2 | I3C1/TIM1/5/8/12/15 |
| AF3 | I3C1/LPTIM1/LPUART1/TIM1/5/8 |
| AF4 | I2C1/2/I3C1/LPTIM1/SPI1/I2S1/SPI3/I2S3/TIM15/USART1/2 |
| AF5 | I3C1/LPTIM1/SPI1/I2S1/SPI2/I2S2/SPI3/I2S3/SYS |
| AF6 | SPI1/I2S1/SPI2/I2S2/SPI3/I2S3/UART4 |
| AF7 | SPI2/I2S2/SPI3/I2S3/USART1/2/3 |
| AF8 | I2C2/LPUART1/TIM5/UART4/5 |
| AF9 | FDCAN1/I2C1/2/SPI2/I2S2 |
| AF10 | CRS/TIM8/16 |
| AF11 | USART1/3 |
| AF12 | - |
| AF13 | TIM8 |
| AF14 | COMP/TIM2/UART5 |
| AF15 | SYS |

**Table 13. Alternate functions (port A)**

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PA0 | - | TIM2_CH1 | TIM5_CH1 | TIM8_ETR | TIM15_BKIN | SPI2_RDY | SPI3_RDY | USART2_CTS/USART2_NSS | UART4_TX | SPI2_NSS/I2S2_WS | - | - | - | - | TIM2_ETR | EVENTOUT |
| PA1 | - | TIM2_CH2 | TIM5_CH2 | TIM8_BKIN | TIM15_CH1N | LPTIM1_IN1 | - | USART2_RTS | UART4_RX | - | - | - | - | - | - | EVENTOUT |
| PA2 | - | TIM2_CH3 | TIM5_CH3 | LPUART1_RX | TIM15_CH1 | LPTIM1_IN2 | - | USART2_TX | - | - | - | - | - | - | - | EVENTOUT |
| PA3 | - | TIM2_CH4 | TIM5_CH4 | LPUART1_TX | TIM15_CH2 | SPI2_NSS/I2S2_WS | SPI3_MOSI/I2S3_SDO | USART2_RX | - | - | - | - | - | - | COMP1_OUT | EVENTOUT |
| PA4 | - | - | TIM5_ETR | - | SPI3_MOSI/I2S3_SDO | SPI1_NSS/I2S1_WS | SPI3_NSS/I2S3_WS | USART2_CK | - | - | - | - | - | - | - | EVENTOUT |
| PA5 | - | TIM2_CH1 | TIM1_CH3 | TIM8_CH1N | - | SPI1_SCK/I2S1_CK | SPI2_SCK/I2S2_CK | USART1_CTS/USART1_NSS | - | - | - | - | - | - | TIM2_ETR | EVENTOUT |
| PA6 | - | TIM1_BKIN | TIM5_CH1 | TIM8_BKIN | - | SPI1_MISO/I2S1_SDI | - | USART1_TX | LPUART1_RTS | - | - | - | - | - | - | EVENTOUT |
| PA7 | - | TIM1_CH1N | TIM5_CH2 | TIM8_CH1N | TIM15_CH1 | SPI1_MOSI/I2S1_SDO | SPI2_MISO/I2S2_SDI | USART1_RX | LPUART1_CTS | - | - | - | - | - | - | EVENTOUT |
| PA8 | MCO1 | TIM1_CH1 | I3C1_SDA | TIM8_BKIN2 | TIM15_CH2 | SPI1_RDY | SPI2_MOSI/I2S2_SDO | USART1_CK | TIM5_CH4 | I2C1_SCL | - | - | - | - | TIM2_CH4 | EVENTOUT |
| PA9 | MCO2 | TIM1_CH2 | I3C1_SCL | LPUART1_TX | TIM15_CH1N | SPI2_SCK/I2S2_CK | - | USART1_TX | TIM5_ETR | I2C1_SMBA | - | - | - | TIM8_CH2N | - | EVENTOUT |
| PA10 | - | TIM1_CH3 | - | LPUART1_RX | - | - | - | USART1_RX | - | - | - | - | - | - | - | EVENTOUT |
| PA11 | - | TIM1_CH4 | - | LPUART1_CTS | USART2_TX | SPI2_NSS/I2S2_WS | UART4_RX | USART1_CTS/USART1_NSS | I2C2_SCL | FDCAN1_RX | - | - | - | - | - | EVENTOUT |
| PA12 | - | TIM1_ETR | - | LPUART1_RTS | USART2_RX | SPI2_SCK/I2S2_CK | UART4_TX | USART1_RTS | I2C2_SDA | FDCAN1_TX | - | - | - | - | - | EVENTOUT |
| PA13 | JTMS/SWDIO | - | - | - | - | - | - | - | - | - | - | - | - | - | COMP1_OUT | EVENTOUT |
| PA14 | JTCK/SWCLK | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PA15 | JTDI | TIM2_CH1 | TIM1_CH2N | LPTIM1_ETR | I2C2_SMBA | SPI1_NSS/I2S1_WS | SPI3_NSS/I2S3_WS | USART2_CK | UART4_RTS | - | - | USART1_TX | - | TIM8_CH4N | TIM2_ETR | EVENTOUT |

**Table 13. Alternate functions (port B)**

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PB0 | - | TIM1_CH2N | TIM5_CH3 | TIM8_CH2N | - | SPI3_MISO/I2S3_SDI | - | USART2_TX | UART4_CTS | - | - | - | - | - | - | EVENTOUT |
| PB1 | - | TIM1_CH3N | TIM5_CH4 | TIM8_CH3N | SPI3_SCK/I2S3_CK | SPI2_NSS/I2S2_WS | - | USART3_RX | - | - | - | - | - | - | COMP1_OUT | EVENTOUT |
| PB2 | RTC_OUT2 | - | - | TIM8_CH4N | SPI1_RDY | LPTIM1_CH1 | SPI2_SCK/I2S2_CK | SPI3_MOSI/I2S3_SDO | - | - | - | - | - | - | - | EVENTOUT |
| PB3 | JTDO/TRACESWO | TIM2_CH2 | - | TIM5_CH3 | I2C2_SDA | SPI1_SCK/I2S1_CK | SPI3_SCK/I2S3_CK | - | LPUART1_TX | I2C2_SCL | CRS_SYNC | USART3_TX | - | TIM8_CH1 | UART5_RTS | EVENTOUT |
| PB4 | NJTRST | - | TIM5_CH1 | I3C1_SCL | LPTIM1_CH2 | SPI1_MISO/I2S1_SDI | SPI3_MISO/I2S3_SDI | SPI2_NSS/I2S2_WS | LPUART1_CTS | I2C2_SDA | TIM16_BKIN | USART3_RX | - | TIM8_CH2 | UART5_CTS | EVENTOUT |
| PB5 | - | TIM17_BKIN | TIM5_CH2 | I3C1_SDA | I2C1_SMBA | SPI1_MOSI/I2S1_SDO | - | SPI3_MOSI/I2S3_SDO | LPUART1_RTS | FDCAN1_RX | - | USART3_CK | - | TIM8_CH3 | UART5_RX | EVENTOUT |
| PB6 | - | - | - | I3C1_SCL | I2C1_SCL | - | SPI3_MISO/I2S3_SDI | USART1_TX | LPUART1_TX | FDCAN1_TX | TIM16_CH1N | USART3_CTS/USART3_NSS | - | TIM8_CH4 | UART5_TX | EVENTOUT |
| PB7 | - | TIM17_CH1N | - | I3C1_SDA | I2C1_SDA | - | SPI3_SCK/I2S3_CK | USART1_RX | LPUART1_RX | FDCAN1_TX | TIM16_CH1 | USART3_RTS | - | - | - | EVENTOUT |
| PB8 | - | TIM17_CH1 | - | I3C1_SCL | I2C1_SCL | - | SPI3_NSS/I2S3_WS | - | UART4_RX | FDCAN1_RX | - | - | - | - | - | EVENTOUT |
| PB9 | - | - | - | I3C1_SDA | I2C1_SDA | SPI2_NSS/I2S2_WS | SPI3_SCK/I2S3_CK | - | UART4_TX | FDCAN1_TX | - | - | - | - | - | EVENTOUT |
| PB10 | - | TIM2_CH3 | TIM8_CH1 | LPTIM1_IN1 | I2C2_SCL | SPI2_SCK/I2S2_CK | - | USART3_TX | - | - | - | - | - | - | - | EVENTOUT |
| PB12 | - | TIM1_BKIN | TIM8_CH3 | - | I2C2_SDA | SPI2_NSS/I2S2_WS | - | USART3_CK | - | FDCAN1_RX | - | - | - | - | UART5_RX | EVENTOUT |
| PB13 | - | TIM1_CH1N | TIM8_CH2 | LPTIM1_CH1 | I2C2_SMBA | SPI2_SCK/I2S2_CK | - | USART3_CTS/USART3_NSS | LPUART1_RX | FDCAN1_TX | - | - | - | - | UART5_TX | EVENTOUT |
| PB14 | - | TIM1_CH2N | TIM12_CH1 | TIM8_CH2N | USART1_TX | SPI2_MISO/I2S2_SDI | - | USART3_RTS | UART4_RTS | - | - | - | - | - | - | EVENTOUT |
| PB15 | RTC_REFIN | TIM1_CH3N | TIM12_CH2 | TIM8_CH3N | USART1_RX | SPI2_MOSI/I2S2_SDO | SPI1_MOSI/I2S1_SDO | SPI3_MOSI/I2S3_SDO | UART4_CTS | - | - | - | - | - | UART5_RX | EVENTOUT |

**Table 13. Alternate functions (port C)**

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PC0 | - | - | - | - | - | - | - | SPI2_RDY | - | - | TIM16_BKIN | - | - | - | - | EVENTOUT |
| PC1 | TRACED0 | - | - | - | - | SPI2_MOSI/I2S2_SDO | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PC2 | PWR_CSLEEP | TIM17_CH1 | - | - | - | SPI2_MISO/I2S2_SDI | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PC3 | PWR_CSTOP | - | - | LPUART1_TX | - | SPI2_MOSI/I2S2_SDO | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PC4 | - | TIM2_CH4 | - | TIM8_BKIN | - | I2S1_MCK | - | USART3_RX | - | - | TIM16_CH1 | - | - | - | - | EVENTOUT |
| PC5 | - | TIM1_CH4N | - | TIM8_BKIN2 | - | - | - | - | - | - | TIM16_CH1N | - | - | - | COMP1_OUT | EVENTOUT |
| PC6 | - | - | TIM5_CH1 | TIM8_CH1 | - | I2S2_MCK | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PC7 | - | - | TIM5_CH2 | TIM8_CH2 | - | - | I2S3_MCK | - | - | - | - | - | - | - | - | EVENTOUT |
| PC8 | TRACED1 | - | TIM5_CH3 | TIM8_CH3 | - | - | - | - | UART5_RTS | - | - | - | - | - | - | EVENTOUT |
| PC9 | MCO2 | - | TIM5_CH4 | TIM8_CH4 | - | AUDIOCLK | - | - | UART5_CTS | I2C1_SDA | - | - | - | - | - | EVENTOUT |
| PC10 | - | - | - | TIM8_CH1N | I3C1_SCL | - | SPI3_SCK/I2S3_CK | USART3_TX | UART4_TX | - | - | - | - | - | - | EVENTOUT |
| PC11 | - | - | - | TIM8_CH2N | I3C1_SDA | - | SPI3_MISO/I2S3_SDI | USART3_RX | UART4_RX | - | - | - | - | - | - | EVENTOUT |
| PC12 | TRACED3 | - | TIM15_CH1 | TIM8_CH3N | - | - | SPI3_MOSI/I2S3_SDO | USART3_CK | UART5_TX | - | - | - | - | - | - | EVENTOUT |
| PC13 | - | - | - | - | - | - | - | - | - | FDCAN1_TX | - | - | - | - | - | EVENTOUT |
| PC14 | - | - | TIM12_CH1 | - | - | - | - | - | - | FDCAN1_RX | - | - | - | - | - | EVENTOUT |
| PC15 | - | - | TIM12_CH2 | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |

**Table 13. Alternate functions (port D)**

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PD0 | - | - | - | TIM8_CH4N | - | - | - | - | UART4_RX | FDCAN1_RX | - | - | - | - | - | EVENTOUT |
| PD1 | - | - | - | - | - | - | - | - | UART4_TX | FDCAN1_TX | - | - | - | - | - | EVENTOUT |
| PD2 | TRACED2 | - | - | - | TIM15_BKIN | - | - | - | UART5_RX | - | - | - | - | - | - | EVENTOUT |
| PD3 | - | - | - | - | - | SPI2_SCK/I2S2_CK | - | USART2_CTS/USART2_NSS | - | - | - | - | - | - | - | EVENTOUT |
| PD4 | - | - | - | - | - | - | - | USART2_RTS | - | - | - | - | - | - | - | EVENTOUT |
| PD5 | - | TIM1_CH4N | - | - | - | SPI2_RDY | - | USART2_TX | - | FDCAN1_TX | - | - | - | - | - | EVENTOUT |
| PD6 | - | - | - | - | - | SPI3_MOSI/I2S3_SDO | - | USART2_RX | - | - | - | - | - | - | - | EVENTOUT |
| PD7 | - | - | - | - | - | SPI1_MOSI/I2S1_SDO | SPI3_MISO/I2S3_SDI | USART2_CK | - | - | - | - | - | - | - | EVENTOUT |
| PD8 | - | - | - | - | - | - | - | USART3_TX | - | - | - | - | - | - | - | EVENTOUT |
| PD9 | - | - | - | - | - | - | - | USART3_RX | - | - | - | - | - | - | - | EVENTOUT |
| PD10 | MCO2 | LPTIM1_CH2 | - | - | - | - | - | USART3_CK | - | - | - | - | - | - | - | EVENTOUT |
| PD11 | - | LPTIM1_IN2 | - | - | - | - | - | USART3_CTS/USART3_NSS | UART4_RX | - | - | - | - | - | - | EVENTOUT |
| PD12 | - | LPTIM1_IN1 | - | TIM8_CH1N | - | I3C1_SCL | - | USART3_RTS | UART4_TX | - | - | - | - | - | - | EVENTOUT |
| PD13 | - | LPTIM1_CH1 | - | TIM8_CH2N | - | I3C1_SDA | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PD14 | - | - | - | TIM8_CH3N | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PD15 | - | - | - | TIM8_CH4N | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |

**Table 13. Alternate functions (port E)**

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PE0 | - | LPTIM1_ETR | - | - | - | - | SPI3_RDY | - | - | FDCAN1_RX | - | - | - | - | - | EVENTOUT |
| PE1 | - | LPTIM1_IN2 | - | - | - | - | - | - | - | FDCAN1_TX | - | - | - | - | - | EVENTOUT |
| PE2 | TRACECLK | LPTIM1_IN2 | - | - | - | SPI3_SCK/I2S3_CK | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PE3 | TRACED0 | - | - | - | TIM15_BKIN | - | - | USART1_RX | - | - | - | - | - | - | - | EVENTOUT |
| PE4 | TRACED1 | - | - | - | TIM15_CH1N | SPI3_NSS/I2S3_WS | - | USART1_TX | - | - | - | - | - | - | - | EVENTOUT |
| PE5 | TRACED2 | - | - | - | TIM15_CH1 | SPI3_MISO/I2S3_SDI | - | USART1_CK | - | - | - | - | - | - | - | EVENTOUT |
| PE6 | TRACED3 | TIM1_BKIN2 | - | - | TIM15_CH2 | SPI3_MOSI/I2S3_SDO | - | USART1_CTS/USART1_NSS | - | - | - | - | - | - | - | EVENTOUT |
| PE7 | - | TIM1_ETR | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PE8 | - | TIM1_CH1N | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PE9 | - | TIM1_CH1 | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PE10 | - | TIM1_CH2N | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PE11 | - | TIM1_CH2 | - | - | SPI1_RDY | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PE12 | - | TIM1_CH3N | - | - | - | - | - | - | - | - | - | - | - | - | COMP1_OUT | EVENTOUT |
| PE13 | - | TIM1_CH3 | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PE14 | - | TIM1_CH4 | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PE15 | - | TIM1_BKIN | - | TIM1_CH4N | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |

**Table 13. Alternate functions (port H)**

| Pin | AF0 | AF1 | AF2 | AF3 | AF4 | AF5 | AF6 | AF7 | AF8 | AF9 | AF10 | AF11 | AF12 | AF13 | AF14 | AF15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PH0 | - | - | - | - | I2C1_SDA | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PH1 | - | - | - | - | I2C1_SCL | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PH2 | MCO1 | TIM17_CH1N | - | LPTIM1_IN2 | - | - | - | - | - | FDCAN1_RX | - | - | - | - | - | EVENTOUT |
| PH3 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PH4 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PH5 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | EVENTOUT |
| PH15 | - | - | - | - | - | - | - | USART1_RTS | - | - | - | - | - | - | - | EVENTOUT |

Table 13 has no footnotes.

*Digest note:* the source lists `FDCAN1_TX` on AF9 for both PB6 and PB7 (Table 12 agrees). FDCAN1 exists only on STM32C552x devices (Table 12, note 4).

#### Alternate function signal index

This index is derived solely from Table 13 above. It lists, for each peripheral signal, every pin and AF number that provides it. Combined cells (for example `SPI1_NSS/I2S1_WS`, `JTDO/TRACESWO`) are indexed under each of their names.

`EVENTOUT` is available on AF15 of every pin (all 86 pins: PA0 to PA15, PB0 to PB10, PB12 to PB15, PC0 to PC15, PD0 to PD15, PE0 to PE15, PH0 to PH5, PH15) and is not repeated below.

**System, clock output, and debug**

- `AUDIOCLK`: PC9 AF5
- `JTCK`: PA14 AF0
- `JTDI`: PA15 AF0
- `JTDO`: PB3 AF0
- `JTMS`: PA13 AF0
- `MCO1`: PA8 AF0, PH2 AF0
- `MCO2`: PA9 AF0, PC9 AF0, PD10 AF0
- `NJTRST`: PB4 AF0
- `SWCLK`: PA14 AF0
- `SWDIO`: PA13 AF0
- `TRACECLK`: PE2 AF0
- `TRACED0`: PC1 AF0, PE3 AF0
- `TRACED1`: PC8 AF0, PE4 AF0
- `TRACED2`: PD2 AF0, PE5 AF0
- `TRACED3`: PC12 AF0, PE6 AF0
- `TRACESWO`: PB3 AF0

**COMP1**

- `COMP1_OUT`: PA3 AF14, PA13 AF14, PB1 AF14, PC5 AF14, PE12 AF14

**CRS**

- `CRS_SYNC`: PB3 AF10

**FDCAN1**

- `FDCAN1_RX`: PA11 AF9, PB5 AF9, PB8 AF9, PB12 AF9, PC14 AF9, PD0 AF9, PE0 AF9, PH2 AF9
- `FDCAN1_TX`: PA12 AF9, PB6 AF9, PB7 AF9, PB9 AF9, PB13 AF9, PC13 AF9, PD1 AF9, PD5 AF9, PE1 AF9

**I2C1**

- `I2C1_SCL`: PA8 AF9, PB6 AF4, PB8 AF4, PH1 AF4
- `I2C1_SDA`: PB7 AF4, PB9 AF4, PC9 AF9, PH0 AF4
- `I2C1_SMBA`: PA9 AF9, PB5 AF4

**I2C2**

- `I2C2_SCL`: PA11 AF8, PB3 AF9, PB10 AF4
- `I2C2_SDA`: PA12 AF8, PB3 AF4, PB4 AF9, PB12 AF4
- `I2C2_SMBA`: PA15 AF4, PB13 AF4

**I2S1**

- `I2S1_CK`: PA5 AF5, PB3 AF5
- `I2S1_MCK`: PC4 AF5
- `I2S1_SDI`: PA6 AF5, PB4 AF5
- `I2S1_SDO`: PA7 AF5, PB5 AF5, PB15 AF6, PD7 AF5
- `I2S1_WS`: PA4 AF5, PA15 AF5

**I2S2**

- `I2S2_CK`: PA5 AF6, PA9 AF5, PA12 AF5, PB2 AF6, PB10 AF5, PB13 AF5, PD3 AF5
- `I2S2_MCK`: PC6 AF5
- `I2S2_SDI`: PA7 AF6, PB14 AF5, PC2 AF5
- `I2S2_SDO`: PA8 AF6, PB15 AF5, PC1 AF5, PC3 AF5
- `I2S2_WS`: PA0 AF9, PA3 AF5, PA11 AF5, PB1 AF5, PB4 AF7, PB9 AF5, PB12 AF5

**I2S3**

- `I2S3_CK`: PB1 AF4, PB3 AF6, PB7 AF6, PB9 AF6, PC10 AF6, PE2 AF5
- `I2S3_MCK`: PC7 AF6
- `I2S3_SDI`: PB0 AF5, PB4 AF6, PB6 AF6, PC11 AF6, PD7 AF6, PE5 AF5
- `I2S3_SDO`: PA3 AF6, PA4 AF4, PB2 AF7, PB5 AF7, PB15 AF7, PC12 AF6, PD6 AF5, PE6 AF5
- `I2S3_WS`: PA4 AF6, PA15 AF6, PB8 AF6, PE4 AF5

**I3C1**

- `I3C1_SCL`: PA9 AF2, PB4 AF3, PB6 AF3, PB8 AF3, PC10 AF4, PD12 AF5
- `I3C1_SDA`: PA8 AF2, PB5 AF3, PB7 AF3, PB9 AF3, PC11 AF4, PD13 AF5

**LPTIM1**

- `LPTIM1_CH1`: PB2 AF5, PB13 AF3, PD13 AF1
- `LPTIM1_CH2`: PB4 AF4, PD10 AF1
- `LPTIM1_ETR`: PA15 AF3, PE0 AF1
- `LPTIM1_IN1`: PA1 AF5, PB10 AF3, PD12 AF1
- `LPTIM1_IN2`: PA2 AF5, PD11 AF1, PE1 AF1, PE2 AF1, PH2 AF3

**LPUART1**

- `LPUART1_CTS`: PA7 AF8, PA11 AF3, PB4 AF8
- `LPUART1_RTS`: PA6 AF8, PA12 AF3, PB5 AF8
- `LPUART1_RX`: PA2 AF3, PA10 AF3, PB7 AF8, PB13 AF8
- `LPUART1_TX`: PA3 AF3, PA9 AF3, PB3 AF8, PB6 AF8, PC3 AF3

**PWR**

- `PWR_CSLEEP`: PC2 AF0
- `PWR_CSTOP`: PC3 AF0

**RTC**

- `RTC_OUT2`: PB2 AF0
- `RTC_REFIN`: PB15 AF0

**SPI1**

- `SPI1_MISO`: PA6 AF5, PB4 AF5
- `SPI1_MOSI`: PA7 AF5, PB5 AF5, PB15 AF6, PD7 AF5
- `SPI1_NSS`: PA4 AF5, PA15 AF5
- `SPI1_RDY`: PA8 AF5, PB2 AF4, PE11 AF4
- `SPI1_SCK`: PA5 AF5, PB3 AF5

**SPI2**

- `SPI2_MISO`: PA7 AF6, PB14 AF5, PC2 AF5
- `SPI2_MOSI`: PA8 AF6, PB15 AF5, PC1 AF5, PC3 AF5
- `SPI2_NSS`: PA0 AF9, PA3 AF5, PA11 AF5, PB1 AF5, PB4 AF7, PB9 AF5, PB12 AF5
- `SPI2_RDY`: PA0 AF5, PC0 AF7, PD5 AF5
- `SPI2_SCK`: PA5 AF6, PA9 AF5, PA12 AF5, PB2 AF6, PB10 AF5, PB13 AF5, PD3 AF5

**SPI3**

- `SPI3_MISO`: PB0 AF5, PB4 AF6, PB6 AF6, PC11 AF6, PD7 AF6, PE5 AF5
- `SPI3_MOSI`: PA3 AF6, PA4 AF4, PB2 AF7, PB5 AF7, PB15 AF7, PC12 AF6, PD6 AF5, PE6 AF5
- `SPI3_NSS`: PA4 AF6, PA15 AF6, PB8 AF6, PE4 AF5
- `SPI3_RDY`: PA0 AF6, PE0 AF6
- `SPI3_SCK`: PB1 AF4, PB3 AF6, PB7 AF6, PB9 AF6, PC10 AF6, PE2 AF5

**TIM1**

- `TIM1_BKIN`: PA6 AF1, PB12 AF1, PE15 AF1
- `TIM1_BKIN2`: PE6 AF1
- `TIM1_CH1`: PA8 AF1, PE9 AF1
- `TIM1_CH1N`: PA7 AF1, PB13 AF1, PE8 AF1
- `TIM1_CH2`: PA9 AF1, PE11 AF1
- `TIM1_CH2N`: PA15 AF2, PB0 AF1, PB14 AF1, PE10 AF1
- `TIM1_CH3`: PA5 AF2, PA10 AF1, PE13 AF1
- `TIM1_CH3N`: PB1 AF1, PB15 AF1, PE12 AF1
- `TIM1_CH4`: PA11 AF1, PE14 AF1
- `TIM1_CH4N`: PC5 AF1, PD5 AF1, PE15 AF3
- `TIM1_ETR`: PA12 AF1, PE7 AF1

**TIM2**

- `TIM2_CH1`: PA0 AF1, PA5 AF1, PA15 AF1
- `TIM2_CH2`: PA1 AF1, PB3 AF1
- `TIM2_CH3`: PA2 AF1, PB10 AF1
- `TIM2_CH4`: PA3 AF1, PA8 AF14, PC4 AF1
- `TIM2_ETR`: PA0 AF14, PA5 AF14, PA15 AF14

**TIM5**

- `TIM5_CH1`: PA0 AF2, PA6 AF2, PB4 AF2, PC6 AF2
- `TIM5_CH2`: PA1 AF2, PA7 AF2, PB5 AF2, PC7 AF2
- `TIM5_CH3`: PA2 AF2, PB0 AF2, PB3 AF3, PC8 AF2
- `TIM5_CH4`: PA3 AF2, PA8 AF8, PB1 AF2, PC9 AF2
- `TIM5_ETR`: PA4 AF2, PA9 AF8

**TIM8**

- `TIM8_BKIN`: PA1 AF3, PA6 AF3, PC4 AF3
- `TIM8_BKIN2`: PA8 AF3, PC5 AF3
- `TIM8_CH1`: PB3 AF13, PB10 AF2, PC6 AF3
- `TIM8_CH1N`: PA5 AF3, PA7 AF3, PC10 AF3, PD12 AF3
- `TIM8_CH2`: PB4 AF13, PB13 AF2, PC7 AF3
- `TIM8_CH2N`: PA9 AF13, PB0 AF3, PB14 AF3, PC11 AF3, PD13 AF3
- `TIM8_CH3`: PB5 AF13, PB12 AF2, PC8 AF3
- `TIM8_CH3N`: PB1 AF3, PB15 AF3, PC12 AF3, PD14 AF3
- `TIM8_CH4`: PB6 AF13, PC9 AF3
- `TIM8_CH4N`: PA15 AF13, PB2 AF3, PD0 AF3, PD15 AF3
- `TIM8_ETR`: PA0 AF3

**TIM12**

- `TIM12_CH1`: PB14 AF2, PC14 AF2
- `TIM12_CH2`: PB15 AF2, PC15 AF2

**TIM15**

- `TIM15_BKIN`: PA0 AF4, PD2 AF4, PE3 AF4
- `TIM15_CH1`: PA2 AF4, PA7 AF4, PC12 AF2, PE5 AF4
- `TIM15_CH1N`: PA1 AF4, PA9 AF4, PE4 AF4
- `TIM15_CH2`: PA3 AF4, PA8 AF4, PE6 AF4

**TIM16**

- `TIM16_BKIN`: PB4 AF10, PC0 AF10
- `TIM16_CH1`: PB7 AF10, PC4 AF10
- `TIM16_CH1N`: PB6 AF10, PC5 AF10

**TIM17**

- `TIM17_BKIN`: PB5 AF1
- `TIM17_CH1`: PB8 AF1, PC2 AF1
- `TIM17_CH1N`: PB7 AF1, PH2 AF1

**UART4**

- `UART4_CTS`: PB0 AF8, PB15 AF8
- `UART4_RTS`: PA15 AF8, PB14 AF8
- `UART4_RX`: PA1 AF8, PA11 AF6, PB8 AF8, PC11 AF8, PD0 AF8, PD11 AF8
- `UART4_TX`: PA0 AF8, PA12 AF6, PB9 AF8, PC10 AF8, PD1 AF8, PD12 AF8

**UART5**

- `UART5_CTS`: PB4 AF14, PC9 AF8
- `UART5_RTS`: PB3 AF14, PC8 AF8
- `UART5_RX`: PB5 AF14, PB12 AF14, PB15 AF14, PD2 AF8
- `UART5_TX`: PB6 AF14, PB13 AF14, PC12 AF8

**USART1**

- `USART1_CK`: PA8 AF7, PE5 AF7
- `USART1_CTS`: PA5 AF7, PA11 AF7, PE6 AF7
- `USART1_NSS`: PA5 AF7, PA11 AF7, PE6 AF7
- `USART1_RTS`: PA12 AF7, PH15 AF7
- `USART1_RX`: PA7 AF7, PA10 AF7, PB7 AF7, PB15 AF4, PE3 AF7
- `USART1_TX`: PA6 AF7, PA9 AF7, PA15 AF11, PB6 AF7, PB14 AF4, PE4 AF7

**USART2**

- `USART2_CK`: PA4 AF7, PA15 AF7, PD7 AF7
- `USART2_CTS`: PA0 AF7, PD3 AF7
- `USART2_NSS`: PA0 AF7, PD3 AF7
- `USART2_RTS`: PA1 AF7, PD4 AF7
- `USART2_RX`: PA3 AF7, PA12 AF4, PD6 AF7
- `USART2_TX`: PA2 AF7, PA11 AF4, PB0 AF7, PD5 AF7

**USART3**

- `USART3_CK`: PB5 AF11, PB12 AF7, PC12 AF7, PD10 AF7
- `USART3_CTS`: PB6 AF11, PB13 AF7, PD11 AF7
- `USART3_NSS`: PB6 AF11, PB13 AF7, PD11 AF7
- `USART3_RTS`: PB7 AF11, PB14 AF7, PD12 AF7
- `USART3_RX`: PB1 AF7, PB4 AF11, PC4 AF7, PC11 AF7, PD9 AF7
- `USART3_TX`: PB3 AF11, PB10 AF7, PC10 AF7, PD8 AF7

## 5 Electrical characteristics

### 5.1 Parameter conditions

Unless otherwise specified, all voltages are referenced to VSS.

#### 5.1.1 Minimum and maximum values

Unless otherwise specified the minimum and maximum values are guaranteed in the worst conditions of junction temperature, supply voltage and frequencies by tests in production on 100 % of the devices with an junction temperature at TJ = 25 °C and TJ = TJmax (given by the selected temperature range).

Data based on characterization results, design simulation and/or technology characteristics are indicated in the table footnotes. Based on characterization, the minimum and maximum values refer to sample tests and represent the mean value plus or minus three times the standard deviation (mean ± 3σ).

#### 5.1.2 Typical values

Unless otherwise specified, typical data are based on TJ = 25 °C, VDD = 3.3 V (for the 2.7 V ≤ VDD ≤ 3.6 V voltage range). They are given only as design guidelines and are not tested.

Typical ADC accuracy values are determined by characterization of a batch of samples from a standard diffusion lot over the full temperature range, where 95% of the devices have an error less than or equal to the value indicated (mean ± 2σ).

#### 5.1.3 Typical curves

Unless otherwise specified, all typical curves are given only as design guidelines and are not tested.

#### 5.1.4 Loading capacitor

The loading conditions used for pin parameter measurement are shown in Figure 11.

#### 5.1.5 Pin input voltage

The input voltage measurement on a pin of the device is described in Figure 12.

**Figure 11. Pin loading conditions**

The device pin is loaded with a single capacitor C = 50 pF connected between the pin and ground (VSS).

**Figure 12. Pin input voltage**

The pin input voltage VIN is applied by a voltage source connected between the device pin and ground (VSS); VIN is the pin voltage referenced to VSS.

#### 5.1.6 Power supply scheme

Each power supply pair must be decoupled with filtering ceramic capacitors as shown in the following figures. These capacitors must be placed as close as possible to, or below, the appropriate pins on the underside of the PCB to ensure the proper functionality of the device.

**Figure 13. STM32C55xxx power supply scheme**

The figure shows how the external supply pins feed the internal power domains, and the required external decoupling:

| External pin(s) | External decoupling | Internal connection / domain supplied |
|---|---|---|
| VCAP | 2.2 µF to ground | Output of the internal LDO regulator (the VCORE node). Also connected to the backup circuitry. |
| n x VDD | 4.7 µF + n x 100 nF (one 4.7 µF bulk capacitor plus one 100 nF per VDD pin) to ground | Input of the LDO regulator; the internal VDDIO1 supply of the GPIO buffers; VDDA of the analog blocks (ADCs/DAC/COMP); the backup circuitry. |
| VREF+ (labelled VREF on the board side) | 100 nF to ground | VREF+ reference input of the ADCs/DAC/COMP block. |
| VREF- | (ground side of the VREF decoupling) | VREF- input of the ADCs/DAC/COMP block. |
| n x VSS | Common ground for all the capacitors above | Device ground; also VSSA of the ADCs/DAC/COMP block. |

Internal blocks shown in the figure:

- **LDO regulator**: powered from VDD, produces VCORE. VCORE supplies the kernel logic domain (drawn as a dashed box) which contains the kernel logic (CPU, digital logic and memories) and the I/O logic. VCORE is brought out on the VCAP pin for the external 2.2 µF capacitor.
- **Backup circuitry (LSE, RTC, TAMP backup registers)**: connected to VDD and to the VCORE/VCAP node.
- **GPIOs**: each GPIO pad has an output driver (OUT) and a Schmitt-trigger input buffer (IN), both powered by VDDIO1 (which is derived from VDD). The OUT/IN signals cross a level shifter between the VDDIO1 domain and the I/O logic in the VCORE domain.
- **ADCs/DAC/COMP**: supplied by VDDA (internally connected to VDD), referenced to VREF+ and VREF- (from the corresponding pins), with analog ground VSSA connected to the VSS pins.

The external capacitor on VCAP pin requires the following characteristics:

- COUT = 2.2 μF
- COUT ESR < 20 mΩ at 3 MHz
- COUT rated voltage ≥ 10 V

### 5.2 Absolute maximum ratings

Stresses above the absolute maximum ratings listed in Table 14, Table 15, and Table 16 may damage permanently the device. These are stress ratings only and the functional operation of the device at these conditions is not implied. Exposure to maximum rating conditions for extended periods may affect device reliability. Device mission profile (application conditions) is compliant with JEDEC JESD47 qualification standard. Extended mission profiles are available on demand.

**Table 14. Voltage characteristics**

All main power (VDD) and ground (VSS) pins must always be connected to the external power supply, in the permitted range.

The I/O structure options listed in this table can be a concatenation of options including the option explicitly listed. For instance, TT_a refers to any TT I/O with _a option. TT_xx refers to any TT I/O and FT_xx refers to any FT I/O.

| Symbols | Ratings | Min | Max | Unit |
|---|---|---|---|---|
| VDDX - VSS | External main supply voltage (including VDD, VDDA and VREF+) | −0.3 | 4.0 | V |
| VIN(1) | Input voltage on FT_xxx pins | VSS−0.3 | MIN (VDD + 4.0V , 6.0 V)(2) | V |
| VIN(1) | Input voltage on TT_xx pins | VSS−0.3 | 4.0 | V |
| VREF+-VDDA | Allowed voltage difference for VREF+ > VDDA | - | 0.4 | V |
| \|∆VDDX\| | Variations between different VDDX power pins of the same domain | - | 50.0 | mV |
| \|VSSx-VSS\| | Variations between all the different ground pins | - | 50.0 | mV |

Notes:

1. VIN maximum must always be respected. Refer to Table 15 for the maximum allowed injected current values.
2. When the analog option is selected by enabling analog peripheral or the pull-up/pull-down resistors are enabled on a given pin, VIN must not exceed 4 V.

**Table 15. Current characteristics**

| Symbol | Ratings | Max | Unit |
|---|---|---|---|
| ∑IVDD | Total current into sum of all VDD power lines (source)(1) | 200 | mA |
| ∑IVSS | Total current out of sum of all VSS ground lines (sink)(1) | 200 | mA |
| IVDD | Maximum current into each VDD power pin (source)(1) | 100 | mA |
| IVSS | Maximum current out of each VSS ground pin (sink)(1) | 100 | mA |
| IIO | Output current sunk by any I/O and control pin | 20 | mA |
| IIO | Output current sourced by any I/O and control pin | 20 | mA |
| ∑I(PIN) | Total output current sunk by sum of all I/Os and control pins(2) | 140 | mA |
| ∑I(PIN) | Total output current sourced by sum of all I/Os and control pins(2) | 140 | mA |
| IINJ(PIN)(3)(4) | Injected current on FT_xx, TT_xx, RST pins | -5/0 | mA |
| ∑IINJ(PIN) | Total injected current (sum of all I/Os and control pins)(5) | ±25 | mA |

Notes:

1. All main power (VDD) and ground (VSS) pins must always be connected to the external power supplies, in the permitted range.
2. This current consumption must be correctly distributed over all I/Os and control pins. The total output current must not be sunk/sourced between two consecutive power supply pins, referring to high pin count QFP packages.
3. A negative injection is induced by VIN < VSS. IINJ(PIN) must never be exceeded. Refer also to Table 14 for the minimum allowed input voltage values.
4. Positive injection (when VIN > VDDIOx) is not possible on these I/Os and does not occur for input voltages lower than the specified maximum value.
5. When several inputs are submitted to a current injection, the maximum ∑IINJ(PIN) is the absolute sum of the negative injected currents (instantaneous values).

**Table 16. Thermal characteristics**

| Symbol | Ratings | Value | Unit |
|---|---|---|---|
| TSTG | Storage temperature range | -65 to +150 | °C |
| TJ | Maximum junction temperature | 150 | °C |

### 5.3 Operating conditions

#### 5.3.1 General operating conditions

**Table 17. General operating conditions**

| Symbol | Parameter | Operating conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| VDD/VDDA | Standard operating voltage | - | 2.7(1) | - | 3.6 | V |
| VIN | I/O Input voltage | All I/O except TT_xx | VSS−0.3 | - | MIN (VDD + 3.6V , 5.5 V)(2) | V |
| VIN | I/O Input voltage | TT_xx I/O | VSS−0.3 | - | VDD + 0.3 | V |
| VCAP | Internal regulator ON | RUN, SLEEP, STOP0 Modes | 1.15 | 1.20 | 1.26 | V |
| VCAP | Internal regulator ON | STOP1 Mode | 0.9 | 0.95 | 1.0 | V |
| fHCLK | AHB clock frequency | - | - | - | 144 | MHz |
| fPCLK | APB clock frequency | - | - | - | 144 | MHz |
| PD | Power dissipation at TA = 85 °C for suffix 6(3) | - | See Section 6.9: Package thermal characteristics for application appropriate thermal resistance and package. Power dissipation is then calculated according ambient temperature (TA) and maximum junction temperature (TJ) and selected thermal resistance. | | | mW |
| PD | Power dissipation at TA = 125 °C for suffix 3(3) | - | See Section 6.9: Package thermal characteristics for application appropriate thermal resistance and package. Power dissipation is then calculated according ambient temperature (TA) and maximum junction temperature (TJ) and selected thermal resistance. | | | mW |
| TA | Ambient temperature for suffix 3 version | - | -40 | - | 125 | °C |
| TA | Ambient temperature for suffix 6 version | - | -40 | - | 85 | °C |
| TJ | Junction temperature range for suffix 3 version | - | -40 | - | 140 | °C |
| TJ | Junction temperature range for suffix 6 version. | - | -40 | - | 105 | °C |

Notes:

1. When RESET is released, the functionality is guaranteed down to PDR minimum voltage.
2. For operation with voltage higher than VDD + 0.3 V, the internal pull‑up and pull‑down resistors must be disabled. The minimum and maximum input voltage (Vin) must comply with the selected peripheral enabled on the given GPIOs. Refer to the respective peripheral characteristics for details.
3. If TA is lower, higher PD values are allowed as long as TJ does not exceed TJmax (see Section 6.9: Package thermal characteristics).

#### 5.3.2 Operating conditions at power-up/power-down

The parameters given in the table below are derived from tests performed under the ambient temperature condition summarized in Table 17.

**Table 18. Operating conditions at power-up/power-down**

| Symbol | Parameter | Min | Max | Unit |
|---|---|---|---|---|
| tVDD | VDD rise‑time rate | 0 | ∞ | µs/V |
| tVDD | VDD fall‑time rate | 0 | ∞ | ms/V |

#### 5.3.3 Embedded reset and power control block characteristics

The parameters given in the table below are derived from tests performed under the ambient temperature conditions summarized in Table 17.

**Table 19. Embedded reset and power control block characteristics**

The values in this table are evaluated by characterization - Not tested in production, unless otherwise specified.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| tRSTTEMPO(1)(2) | Reset temporization after POR released | VDD rising | - | - | 463 | µs |
| VPOR/PDR | Power-on/power-down reset threshold (BORH_EN =0) | Rising edge | 2.56 | 2.61 | 2.64 | V |
| VPOR/PDR | Power-on/power-down reset threshold (BORH_EN =0) | Falling edge | 2.53 | 2.58 | 2.61 | V |
| VPVD | Programmable Voltage Detector threshold | Rising edge | 3.00 | 3.04 | 3.08 | V |
| VPVD | Programmable Voltage Detector threshold | Falling edge | 2.89 | 2.93 | 2.96 | V |
| Vhyst_POR_PDR | Hysteresis for power-on/power-down reset | - | - | 30 | - | mV |
| Vhyst_PVD | Hysteresis voltage of PVD | - | - | 110 | - | mV |
| IDD_PVD(2) | PVD consumption from VDD | - | - | - | 0.63 | µA |

Notes:

1. Specified by design - Not tested in production.
2. From POR threshold crossing to NRST pull-up resistor activation.

#### 5.3.4 Inrush current and inrush electric charge characteristics

The parameters provided in the following table are specified by design simulation and are not tested in production.

**Table 20. Embedded internal voltage reference** [title as printed in the source; the table content is the inrush current and inrush electric charge]

The typical values are provided for VDD = 3.3V and for a typical decoupling capacitor value.

The product consumption on VDDCORE is not included in the inrush current and inrush electric charge.

| Symbol | Parameter | Typ | Unit |
|---|---|---|---|
| IRUSH | Inrush current during voltage regulator power-on (POR) or wake-up from standby | 35 | mA |
| QRUSH | Inrush electric charge during voltage regulator power-on (POR) or wake-up from standby. | 2.8 | µC |

#### 5.3.5 Embedded voltage reference

The parameters provided in Table 21. Embedded internal voltage reference are derived from tests performed under the ambient temperature and supply voltage conditions summarized in Section 5.3.1.

**Table 21. Embedded internal voltage reference**

The values in this table are specified by design and not tested in production.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| VREFINT | Internal reference voltages | -40°C < TJ < 140 °C | 1.180 | 1.217 | 1.250 | V |
| tS_vrefint(1)(2) | ADC sampling time when reading the internal reference voltage | - | 4.3 | - | - | µs |
| tstart_vrefint(2) | Start time of reference voltage buffer when ADC is enable | - | - | - | 4.4 | µs |
| Irefbuf(2) | Reference Buffer consumption for ADC | VDDA = 3.3 V | 9 | 13.5 | 23 | µA |
| ΔVREFINT(2) | Internal reference voltage spread over the temperature range | -40 °C < TJ < 140 °C | - | 5 | 15 | mV |
| Tcoeff | Average temperature coefficient | Average temperature coefficient | - | 19 | 67 | ppm/°C |
| VDDcoeff | Average Voltage coefficient | 3.0 V < VDD < 3.6 V | - | 10 | 1370 | ppm/V |

Notes:

1. The shortest sampling time for the application can be determined by multiple iterations.
2. Specified by design - Not tested in production.

**Table 22. Internal reference voltage calibration values**

| Symbol | Parameter | Memory address |
|---|---|---|
| VREFINT_CAL | Raw data acquired at temperature of 30 °C, VDDA = 3.3 V | 0x08FFF810 - 0x08FFF811 |

#### 5.3.6 Supply current characteristics

The current consumption is a function of several parameters and factors such as the operating voltage, ambient temperature, I/O pin loading, device software configuration, operating frequencies, I/O pin switching rate, program location in memory and executed binary code.

The current consumption is measured as described in Current consumption measurement.

**Typical and maximum current consumption**

The MCU is placed under the following conditions:

- All I/O pins are in analog input mode.
- All peripherals are disabled except when explicitly mentioned.
- The flash memory access time is adjusted with the minimum wait-state number, depending on the fHCLK frequency (refer to the tables *Number of wait states according to CPU clock (HCLK) frequency* available in the product reference manual).
- When the peripherals are enabled, fPCLK = fHCLK.

The parameters given in the tables below are derived from tests performed under ambient temperature and supply voltage conditions summarized in Section 5.3.1: General operating conditions. If not specified otherwise, typical data are measured with a VDD supply of 3.0 V, and maximum data are measured at 3.6 V.

##### 5.3.6.1 Current consumption in Run mode

**Table 23. Typical and maximum current consumption in Run mode**

Evaluated by characterization - not tested in production, unless otherwise stated.

Clocked by HSI at 144 MHz or HSIDIV3 at 48MHz if not otherwise specified.

| Symbol | Parameter | Conditions | fHCLK (MHz) | Typ | Max TJ = 30°C | Max TJ = 90°C | Max TJ = 110°C | Max TJ = 130°C | Max TJ = 140°C | Unit |
|---|---|---|---|---|---|---|---|---|---|---|
| IDD(Run)(1) | Supply current in Run mode all peripheral clocks disabled | Code in Flash, ICACHE 2-Ways | 144 | 11.5 | 12.00 | 13.50 | 14.50 | 17.00 | 18.50 | mA |
| IDD(Run)(1) | Supply current in Run mode all peripheral clocks disabled | Code in Flash, ICACHE 2-Ways | 48 | 4.1 | 4.35 | 5.75 | 7.15 | 9.45 | 11.00 | mA |
| IDD(Run)(1) | Supply current in Run mode all peripheral clocks disabled | Code in Flash, ICACHE OFF | 144 | 9.4 | 10.00 | 11.50 | 12.50 | 15.00 | 16.50 | mA |
| IDD(Run)(1) | Supply current in Run mode all peripheral clocks disabled | Code in Flash, ICACHE OFF | 48 | 4.0 | 4.35 | 5.70 | 7.05 | 9.35 | 11.00 | mA |
| IDD(Run)(1) | Supply current in Run mode all peripheral clocks disabled | Code in SRAM2, ICACHE OFF, FLASH ON | 144 | 9.3 | 9.80 | 11.00 | 12.50 | 15.00 | 16.50 | mA |
| IDD(Run)(1) | Supply current in Run mode all peripheral clocks disabled | Code in SRAM2, ICACHE OFF, FLASH ON | 48 | 3.4 | 3.60 | 5.05 | 6.40 | 8.70 | 10.50 | mA |
| IDD(Run)(1) | Supply current in Run mode all peripheral clocks enabled | Code in Flash, ICACHE 2-Ways | 144(2) | 23.5 | 24.50 | 25.50 | 27.00 | 29.50 | 31.50 | mA |
| IDD(Run)(1) | Supply current in Run mode all peripheral clocks enabled | Code in Flash, ICACHE OFF | 144(2) | 21.0 | 22.50 | 23.50 | 25.00 | 27.50 | 29.00 | mA |

Notes:

1. Measures done with prefetch enabled.
2. Clocked by PSI at 144 MHz with HSE at 16 MHz in bypass mode.

**Table 24. Typical current consumption in Run mode with CoreMark running from flash memory and SRAM**

Evaluated by characterization - not tested in production, unless otherwise stated.

| Symbol | Parameter | Conditions (Peripheral) | SYSCLK source | fHCLK (MHz) | Typ (mA) | Typ (µA/MHz) |
|---|---|---|---|---|---|---|
| IDD(Run)(1) | Supply current in Run mode | Code in Flash, ICACHE 2-WAY, prefetch ON | PSI(2) | 144 | 12.00 | 82.00 |
| IDD(Run)(1) | Supply current in Run mode | Code in Flash, ICACHE 1-WAY, prefetch ON | PSI(2) | 144 | 9.85 | 68.50 |
| IDD(Run)(1) | Supply current in Run mode | Code in Flash, ICACHE OFF, prefetch ON | PSI(2) | 144 | 9.45 | 65.50 |
| IDD(Run)(1) | Supply current in Run mode | Code in Flash, ICACHE OFF, prefetch OFF | PSI(2) | 144 | 8.40 | 58.50 |
| IDD(Run)(1) | Supply current in Run mode | Code in SRAM2, ICACHE 2-WAY | PSI(2) | 144 | 11.50 | 78.00 |
| IDD(Run)(1) | Supply current in Run mode | Code in SRAM2, ICACHE 1-WAY | PSI(2) | 144 | 9.35 | 65.00 |
| IDD(Run)(1) | Supply current in Run mode | Code in SRAM2, ICACHE OFF | PSI(2) | 144 | 9.15 | 63.50 |

Notes:

1. Measures done with prefetch enabled.
2. Clocked by PSI 144 MHz with HSE at 16 MHz on bypass mode.

##### 5.3.6.2 Current consumption in Sleep mode

**Table 25. Typical and maximum current consumption in Sleep mode**

Evaluated by characterization - Not tested in production.

Clocked by HSI at 144MHz of HSIDIV3 at 48MHz.

| Symbol | Parameter | Conditions | fHCLK (MHz) | Typ | Max TJ = 30 °C | Max TJ = 90 °C | Max TJ = 110 °C | Max TJ = 130 °C | Max TJ = 140 °C | Unit |
|---|---|---|---|---|---|---|---|---|---|---|
| IDD(SLEEP) | Supply current in Sleep mode | All peripheral clocks disabled | 144 | 2.05 | 2.35 | 3.95 | 5.50 | 8.05 | 10.00 | mA |
| IDD(SLEEP) | Supply current in Sleep mode | All peripheral clocks disabled | 48 | 0.93 | 1.15 | 2.80 | 4.35 | 6.95 | 8.85 | mA |
| IDD(SLEEP) | Supply current in Sleep mode | All peripheral clocks enabled | 144 | 15.00 | 15.50 | 17.00 | 18.50 | 21.00 | 22.50 | mA |
| IDD(SLEEP) | Supply current in Sleep mode | All peripheral clocks enabled | 48 | 5.30 | 5.60 | 7.00 | 8.40 | 11.00 | 12.50 | mA |

##### 5.3.6.3 Current consumption in Stop mode

**Table 26. Typical and maximum current consumption in Stop mode**

Evaluated by characterization - not tested in production, unless otherwise stated.

| Symbol | Parameter | Conditions (SRAM) | Conditions (mode) | Typ | Max TJ = 30 °C | Max TJ = 90 °C | Max TJ = 110 °C | Max TJ = 130 °C | Max TJ = 140 °C | Unit |
|---|---|---|---|---|---|---|---|---|---|---|
| IDD(STOP) | FLASH ON | SRAM1/2 ON | STOP0 | 0.19 | 0.34 | 1.60 | 2.80 | 4.80 | 6.15 | mA |
| IDD(STOP) | FLASH ON | SRAM1/2 ON | STOP1 | 0.06 | 0.14 | 0.93 | 1.70 | 3.05 | 3.90 | mA |
| IDD(STOP) | FLASH IN LOW POWER | SRAM1/2 ON | STOP0 | 0.17 | 0.32 | 1.60 | 2.75 | 4.75 | 6.10 | mA |
| IDD(STOP) | FLASH IN LOW POWER | SRAM1/2 ON | STOP1 | 0.05 | 0.13 | 0.92 | 1.70 | 3.05 | 3.85 | mA |
| IDD(STOP) | FLASH IN LOW POWER | SRAM1/2 Powered Down | STOP0 | 0.17 | 0.31 | 1.55 | 2.65 | 4.55 | 5.90 | mA |
| IDD(STOP) | FLASH IN LOW POWER | SRAM1/2 Powered Down | STOP1 | 0.05 | 0.12 | 0.82 | 1.50 | 2.70 | 3.55 | mA |

**Table 27. Typical and maximum HSIKERON current consumption in Stop mode**

Evaluated by characterization - not tested in production, unless otherwise stated.

| Symbol | Parameter | Conditions | Conditions (HSI kernel clock) | Typ | Max TJ = 30 °C | Max TJ = 90 °C | Max TJ = 110 °C | Max TJ = 130 °C | Max TJ = 140 °C | Unit |
|---|---|---|---|---|---|---|---|---|---|---|
| IDD(Stop) | FLASH IN LOW POWER | HSIKERON, STOP0 | HSI144 | 0.49 | 0.63 | 1.85 | 3.00 | 4.90 | 6.20 | mA |
| IDD(Stop) | FLASH IN LOW POWER | HSIKERON, STOP0 | HSI48 | 0.38 | 0.52 | 1.75 | 2.90 | 4.80 | 6.10 | mA |

##### 5.3.6.4 Current consumption in Standby mode

**Table 28. Typical and maximum current consumption in Standby mode**

Evaluated by characterization - not tested in production, unless otherwise stated.

| Symbol | Parameter | RTC and LSE(1) | Typ 2.7 V | Typ 3 V | Typ 3.3 V | Max TJ = 30 °C | Max TJ = 90 °C | Max TJ = 110 °C | Max TJ = 130 °C | Max TJ = 140 °C | Unit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IDD(Standby) | Supply current in Standby mode, IWDG OFF | OFF | 2.75 | 2.90 | 3.00 | 3.80 | 9.90 | 18.00 | 36.50 | 51.00 | μA |
| IDD(Standby) | Supply current in Standby mode, IWDG OFF | ON | 3.10 | 3.25 | 3.40 | - | - | - | - | - | μA |
| IDD(Standby) | Supply current in Standby mode, IWDG ON | OFF | 3.10 | 3.25 | 3.40 | 5.10 | 10.00 | 18.00 | 37.00 | 51.00 | μA |
| IDD(Standby) | Supply current in Standby mode, IWDG ON | ON | 3.40 | 3.55 | 3.75 | - | - | - | - | - | μA |

Notes:

1. LSE is in bypass mode at 32.768 KHz.

##### 5.3.6.5 Current consumption from peripherals

**Table 29. Peripheral current consumption measured in Sleep mode**

| Bus | Peripheral | IDD(Typ) | Unit |
|---|---|---|---|
| AHB1 | SRAM1 | 0.22 | µA/MHz |
| AHB1 | RAMCFG | 0.70 | µA/MHz |
| AHB1 | ICACHE | 0.20 | µA/MHz |
| AHB1 | CRC | 0.70 | µA/MHz |
| AHB1 | FLASH | 6.26 | µA/MHz |
| AHB1 | LPDMA1 | 1.22 | µA/MHz |
| AHB1 | LPDMA2 | 1.09 | µA/MHz |
| AHB1 | SRAM2 | 0.37 | µA/MHz |
| AHB2 | RNG | 0.78 | µA/MHz |
| AHB2 | HASH | 0.69 | µA/MHz |
| AHB2 | DAC1 | 0.92 | µA/MHz |
| AHB2 | ADC12 | 5.51 | µA/MHz |
| AHB2 | GPIOA | 0.07 | µA/MHz |
| AHB2 | GPIOB | 0.07 | µA/MHz |
| AHB2 | GPIOC | 0.09 | µA/MHz |
| AHB2 | GPIOD | 0.07 | µA/MHz |
| AHB2 | GPIOE | 0.08 | µA/MHz |
| AHB2 | GPIOH | 0.06 | µA/MHz |
| APB1 | FDCAN1 | 4.86 | µA/MHz |
| APB1 | CRS | 0.23 | µA/MHz |
| APB1 | I2C1 | 1.97 | µA/MHz |
| APB1 | I2C2 | 2.00 | µA/MHz |
| APB1 | I3C1 | 0.28 | µA/MHz |
| APB1 | UART4 | 3.47 | µA/MHz |
| APB1 | UART5 | 3.43 | µA/MHz |
| APB1 | USART2 | 3.69 | µA/MHz |
| APB1 | USART3 | 3.62 | µA/MHz |
| APB1 | COMP | 0.19 | µA/MHz |
| APB1 | SPI2/I2S2 | 1.59 | µA/MHz |
| APB1 | SPI3/I2S3 | 1.50 | µA/MHz |
| APB1 | WWDG | 0.14 | µA/MHz |
| APB1 | TIM2 | 0.28 | µA/MHz |
| APB1 | TIM5 | 0.31 | µA/MHz |
| APB1 | TIM6 | 0.26 | µA/MHz |
| APB1 | TIM7 | 0.29 | µA/MHz |
| APB1 | TIM12 | 0.27 | µA/MHz |
| APB2 | USB | 2.11 | µA/MHz |
| APB2 | USART1 | 3.39 | µA/MHz |
| APB2 | SPI1/I2S1 | 1.50 | µA/MHz |
| APB2 | TIM1 | 0.30 | µA/MHz |
| APB2 | TIM8 | 0.32 | µA/MHz |
| APB2 | TIM15 | 0.33 | µA/MHz |
| APB2 | TIM16 | 0.31 | µA/MHz |
| APB2 | TIM17 | 0.34 | µA/MHz |
| APB3 | RTC | 3.47 | µA/MHz |
| APB3 | LPTIM1 | 0.78 | µA/MHz |
| APB3 | LPUART | 2.68 | µA/MHz |
| APB3 | SBS | 0.32 | µA/MHz |

#### 5.3.7 Wake-up time from low-power modes and voltage scaling transition times

The wake-up times given in the table below are the latency between the event and the execution of the first user instruction.

The device goes in low-power mode after the WFE (wait for event) instruction.

**Table 30. Wake-up time from low-power modes**

Table header notes (printed above the table in the source):

1. Evaluated by characterization - Not tested in production.
2. The wakeup times are measured from the wakeup event to the point in which the application code reads the first instruction.

| Symbol | Parameter | Conditions | Wakeup clock | fHCLK (MHz) | Typ | Max | Unit |
|---|---|---|---|---|---|---|---|
| twu(Sleep) | Wakeup from Sleep | Instruction cache enabled or disabled | - | - | 16 | 16 | CPU clock cycles |
| twu(Stop) | Wakeup from Stop 0 | Flash memory in normal mode | HSI | 144 | 3.6 | 5 | µs |
| twu(Stop) | Wakeup from Stop 0 | Flash memory in low-power mode | HSI | 144 | 7.2 | 11 | µs |
| twu(Stop) | Wakeup from Stop 0 | Flash memory in normal mode | HSIDIV3 | 48 | 5.1 | 7 | µs |
| twu(Stop) | Wakeup from Stop 0 | Flash memory in low-power mode | HSIDIV3 | 48 | 8.6 | 13.5 | µs |
| twu(Stop) | Wakeup from Stop 1(1) | Flash memory in normal mode | HSI | 144 | 37.0 | 49 | µs |
| twu(Stop) | Wakeup from Stop 1(1) | Flash memory in low-power mode | HSI | 144 | 40.5 | 58 | µs |
| twu(Stop) | Wakeup from Stop 1(1) | Flash memory in normal mode | HSIDIV3 | 48 | 39.0 | 53 | µs |
| twu(Stop) | Wakeup from Stop 1(1) | Flash memory in low-power mode | HSIDIV3 | 48 | 42.0 | 61 | µs |
| twu(Standby) | Wakeup from Standby mode(1) | - | HSIDIV3 | 48 | 445 | - | µs |

*Digest note:* In the source, the twu(Sleep) value 16 is a single cell spanning both the Typ and Max columns.

Notes:

1. Those parameters depend on VCAP capacitance value and VCAP voltage at the instant of the wake-up event.

**Table 31. Wake-up time using USART/LPUART**

| Symbol | Parameter | Condition | Typ | Max(1) | Unit |
|---|---|---|---|---|---|
| tWUUSART/tWULPUART | Wake-up time needed to calculate the maximum USART/LPUART baudrate allowing to wake up from Stop mode when USART/LPUART clock source is 48 MHz by HSIDIV3 | Stop 0 mode | 4.8 | 6.6 | µs |
| tWUUSART/tWULPUART | Wake-up time needed to calculate the maximum USART/LPUART baudrate allowing to wake up from Stop mode when USART/LPUART clock source is 48 MHz by HSIDIV3 | Stop 1 mode | 4.8 | 6.6 | µs |

Notes:

1. Specified by design - Not tested in production.

#### 5.3.8 External clock timing characteristics

##### 5.3.8.1 High-speed external user clock generated from an external source

In bypass mode, the HSE oscillator is switched off and the input pin is a standard GPIO.

The external clock signal has to respect the I/O characteristics in I/O port characteristics. However, the recommended clock input waveform is shown in the figure below.

**Table 32. High-speed external user clock characteristics**

Specified by design and not tested in production.

*Digest note:* The bypass bit is printed as "HSEYBYP" in the digital-mode and first analog-mode conditions and as "HSEBYP" in the remaining analog-mode conditions; it is reproduced as printed.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| fHSE_ext | User external clock source frequency | Digital mode (HSEYBYP = 1, HSEEXT = 1) | - | - | 50 | MHz |
| fHSE_ext | User external clock source frequency | Analog mode (HSEYBYP = 1, HSEEXT = 0) | 4 | - | 50 | MHz |
| VHSEH | OSC_IN input pin high-level voltage | Digital mode (HSEYBYP = 1, HSEEXT = 1) | 0.7 × VDD | - | VDD | V |
| VHSEL | OSC_IN input pin low-level voltage | Digital mode (HSEYBYP = 1, HSEEXT = 1) | VSS | - | 0.3 × VDD | V |
| tw(HSEH)(1), tw(HSEL)(1) | OSC_IN high or low time | Digital mode (HSEYBYP = 1, HSEEXT = 1) | 7 | - | - | ns |
| DuCyHSE | OSC_IN duty cycle | Digital mode (HSEYBYP = 1, HSEEXT = 1) | 45 | - | 55 | % |
| VHSE_ext_PP(2) | OSC_IN peak-to-peak amplitude | Analog mode (HSEBYP = 1, HSEEXT = 0) | 0.2 | - | 2/3 VDD | V |
| VHSE_ext | OSC_IN input range | Analog mode (HSEBYP = 1, HSEEXT = 0) | 0 | - | VDD | V |
| tr(HSE), tf(HSE) | OSC_IN rise and fall time | Analog mode (HSEBYP = 1, HSEEXT = 0) | 0.05 / fext_ext | - | 0.3 / fext_ext | ns |

Notes:

1. There is no specified rise and fall time for a digital input signal, but the VHSEH and VHSEL conditions must be fulfilled.
2. The DC component of the signal must ensure that the signal peaks are located between VDD and VSS.

**Figure 14. AC timing diagram for high-speed external clock source (digital mode)**

The OSC_IN voltage (VHSE, vertical axis) versus time (t) is a trapezoidal square wave swinging between the low level VHSEL and the high level VHSEH. Two threshold levels are marked at 30% and 70% of the swing. THSE is the clock period (measured from one rising edge to the next). tw(HSEH) is the high time, measured across the high plateau at the 70% level (from the rising edge to the following falling edge). tw(HSEL) is the low time, measured across the low plateau at the 30% level (from the falling edge to the following rising edge).

**Figure 15. AC timing diagram for high-speed external clock source (analog mode)**

The OSC_IN voltage (VHSE_ext, vertical axis) versus time (t) is a sine wave whose peak-to-peak amplitude is VHSE_ext_PP. Levels at 10% and 90% of the peak-to-peak amplitude are marked. tf(HSE) is the fall time, measured on the falling slope from the 90% level to the 10% level. tr(HSE) is the rise time, measured on the rising slope from the 10% level to the 90% level. The period, measured peak to peak, is tHSE_ext = 1/fHSE_ext.

##### 5.3.8.2 Low-speed external user clock generated from an external source

In bypass mode, the LSE oscillator is switched off and the input pin is directly connected to the LSE clock detector (LSECSS). The external clock signal has to respect the parameters specified in Table 33, as shown also by the waveforms in Figure 16.

**Table 33. Low-speed external user clock characteristics**

Specified by design and not tested in production.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| fLSE_ext | User external clock source frequency | External digital/analog clock | - | 32.768 | 1000 | kHz |
| VLSEH | Digital OSC_IN input high level | External digital clock | 0.7 VDD | - | VDD | V |
| VLSEL | OSC32_IN input pin low level voltage | External digital clock | VSS | - | 0.3 VDD | V |
| tw(LSEH)/tw(LSEL) | OSC32_IN high or low time | External digital clock | 250 | - | - | ns |
| Vlsw_H | Analog low swing OSC_IN high level | External analog low swing clock | 0.6 | | 1.225 | V |
| Vlsw_L | Analog low swing OSC_IN low level | External analog low swing clock | 0.35 | | 0.8 | V |
| VlswLSE (VLSEH - VLSEL) | Analog low swing OSC_IN peak-to-peak amplitude | External analog low swing clock | 0.2 | | 0.875 | V |
| DuCyLSE | Analog low swing OSC_IN duty cycle | External analog Low Swing Clock | 45 | 50 | 55 | % |
| trLSE/tfLSE | Analog low swing OSC_IN rise and fall time | Externala analog low swing clock 10 % to 90 % | - | 100 | 200 | ns |

**Figure 16. Low-speed external clock source AC timing diagram**

The waveform is a trapezoidal square wave swinging between VLSEL and VLSEH, with 10 % and 90 % levels marked. tr(LSE) is the rise time between the 10 % and 90 % crossings of a rising edge; tf(LSE) is the fall time between the 90 % and 10 % crossings of a falling edge; tW(LSE) marks the high time and the low time of the pulse; TLSE is the clock period. Below the waveform, the connection is shown: an external clock source with frequency fLSE_ext drives the OSC32_IN pin of the STM32 directly; inside the device the OSC32_IN node is shown with an input leakage current IL (drawn as a current source to ground).

##### 5.3.8.3 High-speed external clock generated from a crystal/ceramic resonator

The high-speed external (HSE) clock can be supplied with a 4 to 48 MHz crystal/ceramic resonator oscillator. All the information given in this paragraph are based on design simulation results obtained with typical external components specified in the table below.

In the application, the resonator and the load capacitors have to be placed as close as possible to the oscillator pins, in order to minimize the output distortion and startup stabilization time. Refer to the crystal resonator manufacturer for more details on the resonator characteristics (frequency, package, accuracy).

**Table 34. 4-50 MHz HSE oscillator characteristics**

Specified by design and not tested in production.

| Symbol | Parameter | Operating conditions(1) | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| F | Oscillator frequency | - | 4 | - | 50 | MHz |
| RF | Feedback resistor | - | - | 200 | - | kΩ |
| IDD(HSE) | HSE current consumption | During startup(2) | - | - | 10 | mA |
| IDD(HSE) | HSE current consumption | VDD = 3 V, Rm = 20 Ω CL = 10 pF at 4 MHz | - | 0.4 | - | mA |
| IDD(HSE) | HSE current consumption | VDD = 3 V, Rm = 20 Ω CL = 10 pF at 8 MHz | - | 0.4 | - | mA |
| IDD(HSE) | HSE current consumption | VDD = 3 V, Rm = 20 Ω CL = 10 pF at 16 MHz | - | 0.6 | - | mA |
| IDD(HSE) | HSE current consumption | VDD = 3 V, Rm = 20 Ω CL = 10 pF at 32 MHz | - | 0.7 | - | mA |
| IDD(HSE) | HSE current consumption | VDD = 3 V, Rm = 20 Ω CL = 10 pF at 48 MHz | - | 1.2 | - | mA |
| Gmcritmax | Maximum critical crystal gm | Startup | - | - | 1.5 | mA/V |
| tSU(3) | Start-up time | VDD is stabilized | - | 2 | - | ms |

Notes:

1. Resonator characteristics given by the crystal/ceramic resonator manufacturer.
2. This consumption level occurs during the first 2/3 of the tSU(HSE) startup time.
3. tSU(HSE) is the startup time measured from the moment it is enabled (by software) to a stabilized 8 MHz oscillation is reached. This value is measured for a standard crystal resonator and it can vary significantly with the crystal manufacturer.

Note: For information on selecting the crystal, refer to the application note 'Oscillator design guide for STM8AF/AL/S, STM32 MCUs and MPUs' (AN2867).

**Figure 17. Typical application with a 8 MHz crystal**

An 8 MHz resonator is connected between OSC_IN and OSC_OUT. Load capacitor CL1 connects the OSC_IN side of the resonator to ground and load capacitor CL2 connects the OSC_OUT side of the resonator to ground (a dotted outline labelled "Resonator with integrated capacitors" indicates that CL1, CL2 and the crystal may be a single component). A series resistor REXT(1) is placed between the resonator and the OSC_OUT pin. Inside the device, the feedback resistor RF is connected between OSC_IN and OSC_OUT, in parallel with a "bias controlled gain" amplifier; the oscillator signal is taken from OSC_IN through a Schmitt-trigger buffer to produce fHSE.

(1): REXT value depends on the crystal characteristics.

##### 5.3.8.4 Low-speed external clock generated from a crystal resonator

The low-speed external (LSE) clock can be supplied with a 32.768 kHz crystal resonator oscillator. All the information given in this paragraph are based on design simulation results obtained with typical external components specified in the table below. In the application, the resonator and the load capacitors have to be placed as close as possible to the oscillator pins in order to minimize output distortion and startup stabilization time. Refer to the crystal resonator manufacturer for more details on the resonator characteristics (frequency, package, accuracy).

**Table 35. LSE oscillator characteristics (fLSE = 32.768 kHz)**

Specified by design and not tested in production.

| Symbol | Parameter | Operating conditions(1) | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| F | Oscillator frequency | - | - | 32.768 | - | kHz |
| IDD | LSE current consumption | LSEDRV[1:0] = 00, Low drive capability | - | 246 | - | nA |
| IDD | LSE current consumption | LSEDRV[1:0] = 01, Medium low drive capability | - | 333 | - | nA |
| IDD | LSE current consumption | LSEDRV[1:0] = 10, Medium high drive capability | - | 462 | - | nA |
| IDD | LSE current consumption | LSEDRV[1:0] = 11, High drive capability | - | 747 | - | nA |
| Gmcritmax | Maximum critical crystal Gm | LSEDRV[1:0] = 00, Low drive capability | - | - | 0.5 | µA/V |
| Gmcritmax | Maximum critical crystal Gm | LSEDRV[1:0] = 01, Medium low drive capability | - | - | 0.75 | µA/V |
| Gmcritmax | Maximum critical crystal Gm | LSEDRV[1:0] = 10, Medium high drive capability | - | - | 1.7 | µA/V |
| Gmcritmax | Maximum critical crystal Gm | LSEDRV[1:0] = 11, High drive capability | - | - | 2.7 | µA/V |
| tSU(2) | Startup time | VDD is stabilized | - | 2 | - | s |

Notes:

1. Refer to the following note and caution paragraphs, and to the application note AN2867 "Oscillator design guide for ST microcontrollers.
2. tSU is the startup time measured from the moment it is enabled (by software) to a stabilized 32.768k Hz oscillation is reached. This value is measured for a standard crystal resonator and it can vary significantly with the crystal manufacturer.

Note: For information on selecting the crystal, refer to the application note 'Oscillator design guide for STM8AF/AL/S, STM32 MCUs and MPUs' (AN2867).

**Figure 18. Typical application with a 32.768 kHz crystal**

A 32.768 kHz resonator is connected directly between OSC32_IN and OSC32_OUT (no series resistor). Load capacitor CL1 connects the OSC32_IN side to ground and load capacitor CL2 connects the OSC32_OUT side to ground (a dashed outline labelled "Resonator with integrated capacitors" indicates that CL1, CL2 and the crystal may be a single component). The stray capacitance CS is drawn across the resonator. Inside the device, a "drive programmable amplifier" is connected between OSC32_IN and OSC32_OUT, and the oscillator signal is taken from OSC32_IN through a Schmitt-trigger buffer to produce fLSE.

Figure note: CL1 and CL2 are external load capacitances. Cs (stray capacitance) is the sum of the device OSC32_IN/OSC32_OUT pins equivalent parasitic capacitance (CS_PARA), and the PCB parasitic capacitance.

Note: An external resistor is not required between OSC32_IN and OSC32_OUT and it is forbidden to add one.

#### 5.3.9 Internal clock timing characteristics

The parameters given in the tables below are derived from tests performed under ambient temperature and supply voltage conditions summarized in Table 17. The curves provided are characterization results, not tested in production.

##### 5.3.9.1 High-speed internal HSI144 oscillator

**Table 36. HSI144 oscillator characteristics**

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| fHSI(1) | HSI frequency | VDD = 3.3 V, TJ = 30 °C | 144.07 | - | 145.08 | MHz |
| TRIM(2) | USER trimming step | - | - | 0.1 | 0.15 | % |
| USER TRIM COVERAGE(2) | USER TRIMMING Coverage positive | 80 steps | 5.2% | 8% | - | % |
| USER TRIM COVERAGE(2) | USER TRIMMING Coverage negative | 48 steps | -3.1% | -4.8% | - | % |
| DuCy(HSI)(2) | Duty Cycle | - | 45 | | 55 | % |
| ΔTEMP (HSI)(3) | HSI oscillator frequency drift over temperature (the reference is 144 MHz.) | TJ = -20 to 130 °C | -1 | - | 1 | % |
| ΔTEMP (HSI)(3) | HSI oscillator frequency drift over temperature (the reference is 144 MHz.) | TJ = −40 to TJmax °C | -1.5 | - | 1.5 | % |
| ΔVDD(HSI)(2)(4) | HSI oscillator frequency drift with VDD (5) (the reference is 3.3V) | VDD from 2.7 V to 3.6 V | - | - | - 0.1 | % |
| tsu(HSI)(3) | HSI oscillator start-up time (PSI Off) | - | - | 3 | 4.5 | µs |
| tsu(HSI)(3) | HSI oscillator start-up time (PSI On) | - | - | 0.5 | - | µs |
| tstab(2) | stabilization time (PSI OFF from Enable) | +/-1% of target freq | - | - | 8 | µs |
| tstab(2) | stabilization time (PSI ON from Enable) | +/-1% of target freq | - | - | 0.7 | µs |
| IDD(HSI)(2)(6) | HSI supply regulation block oscillator power consumption | - | - | 91 | - | µA |
| IDD(HSI)(2)(6) | HSI oscillator power consumption | - | - | 28 | - | µA |
| NT jitter(2) | Next transition jitter(7) | On HSIDIV3 | - | 52 | 322 | ps |
| PT jitter(2) | Paired transition jitter(8) | On HSIDIV3 | - | 62 | 394 | ps |
| Per jitter(2) | Period Jitter standard deviation | On HSIS | | 15 | | ps |
| Per jitter(2) | Period Jitter standard deviation | On HSIDIV3 | | 26 | | ps |

*Digest note:* The ΔVDD(HSI) parameter text in the source also contains a stray cross-reference ("VDDSection 5.3.9.1: High-speed internal HSI144 oscillator"); its Max value is printed as "- 0.1".

Notes:

1. Tested in production.
2. Specified by design - Not tested in production.
3. Evaluated by characterization - Not tested in production.
4. ΔfHSI = ΔTEMP + ΔVDD
5. These values are obtained by using formula: (Freq(3.6 V) - Freq(3.3 V)) / Freq(3.3 V) or (Freq(3.6 V) - Freq(2.7 V)) / Freq(2.7 V).
6. The supply regulation consumption is common to HSI and PSI. (To be counted once if both oscillators are ON).
7. Jitter measurements are performed without clock source activated in parallel. Typical value is standard deviation, Maximum is peak measure on TIE-8 over 36 cycles.
8. Jitter measurements are performed without clock source activated in parallel. Typical value is standard deviation, Maximum is peak measure on TIE-16 over 36 cycles.

**Figure 19. HSI frequency versus temperature**

The graph plots normalized HSI frequency deviation (vertical axis, "Normalized Frequency (%)", from -1.5% to +1.5%) against junction temperature (horizontal axis, "Junction Temperature (°C)", from -40 to 140 °C). It contains three characterization curves (AVG, MIN and MAX, in %) and two horizontal limit lines at +1% and -1%. Approximate values read from the graph:

- **AVG (%)**: about 0.0% at -40 °C, rising to about +0.3% at 0 °C and a broad maximum of about +0.4% around 30–40 °C, then decreasing to about +0.1% at 100 °C, crossing 0% around 110 °C, and reaching about -0.3% at 140 °C.
- **MIN (%)**: about -1.45% at -40 °C, crossing the -1% line around -30 °C, rising to about -0.25% at 0 °C and a maximum just above 0% (about +0.03%) around 35 °C, then decreasing to about -0.5% at 100 °C and about -0.6% at 110 °C, reaching the -1% line near 135–140 °C (about -1.04% at 140 °C).
- **MAX (%)**: about +1.17% at -40 °C, crossing the +1% line around -27 °C, decreasing to about +0.75% at 0 °C and a local minimum of about +0.64% around 30 °C, a local maximum of about +0.8% around 60 °C, then decreasing to about +0.53% at 100 °C and about +0.25% at 140 °C.

The MIN/MAX curves stay inside ±1% from roughly -27 °C up to about 135 °C, consistent with the ±1% specification for TJ = -20 to 130 °C in Table 36; at the temperature extremes they extend to about ±1.5%.

##### 5.3.9.2 PSI oscillator characteristics

**Table 37. PSI oscillator characteristics**

| Symbol | Parameter | Conditions | Min(1) | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| fPSI | PSI potential frequency | If reference is HSE at 8, 16, 24, 32 or 48 MHz or HSIDIV18 | - | 100 | - | MHz |
| fPSI | PSI potential frequency | If reference is HSE at 8, 16, 24, 32 or 48 MHz or HSIDIV18 | - | 144 | - | MHz |
| fPSI | PSI potential frequency | If reference is HSE at 8, 16, 24, 32 or 48 MHz or HSIDIV18 | - | 160(2) | - | MHz |
| fPSI | PSI potential frequency | If reference is HSE at 25 or 50 MHz | - | 100 | - | MHz |
| fPSI | PSI potential frequency | If reference is HSE at 25 or 50 MHz | - | 141.67 | - | MHz |
| fPSI | PSI potential frequency | If reference is HSE at 25 or 50 MHz | - | 158.33(2) | - | MHz |
| fPSI | PSI potential frequency | If reference is LSE at 32 KHz | - | 100.008 | - | MHz |
| fPSI | PSI potential frequency | If reference is LSE at 32 KHz | - | 144.015 | - | MHz |
| fPSI | PSI potential frequency | If reference is LSE at 32 KHz | - | 160.006(2) | - | MHz |
| DuCy(PSI)(3) | Duty Cycle | - | 45 | | 55 | % |
| tsu(PSI)(4) | PSI startup time | On 32 KHz | - | 850 | 1750 | µs |
| tsu(PSI)(4) | PSI startup time | On 8 MHz | - | 25 | 45 | µs |
| IDD(PSI)(3)(5) | PSI supply regulation bloc oscillator power consumption | If HSI not ON | - | 91 | - | µA |
| IDD(PSI)(3)(5) | PSI oscillator power consumption | 100 MHz | - | 95 | - | µA |
| IDD(PSI)(3)(5) | PSI oscillator power consumption | 144 MHz | - | 68 | - | µA |
| IDD(PSI)(3)(5) | PSI oscillator power consumption | 160 MHz | - | 77 | - | µA |
| NT jitter(3) | Next transition jitter(6) | On PSIDIV3 (48 MHz with 32 kHz CK_IN) | - | 46.8 | 264 | ps |
| NT jitter(3) | Next transition jitter(6) | On PSIDIV3 (48 MHz with 8 MHz CK_IN) | - | 52.6 | 276 | ps |
| PT jitter(3) | Paired transition jitter(7) | On PSIDIV3 (48 MHz with 32 kHz CK_IN) | - | 54.4 | 331 | ps |
| PT jitter(3) | Paired transition jitter(7) | On PSIDIV3 (48 MHz with 8 MHz CK_IN) | - | 60.6 | 367 | ps |
| Per jitter(3) | Period Jitter standard deviation | On PSIS (100 MHz) | - | 15.5 | - | ps |
| Per jitter(3) | Period Jitter standard deviation | On PSIDIV3 (33.33 MHz) | - | 27 | - | ps |
| Per jitter(3) | Period Jitter standard deviation | On PSIS (144 MHz) | - | 14 | - | ps |
| Per jitter(3) | Period Jitter standard deviation | On PSIDIV3 (48 MHz) | - | 24.5 | - | ps |
| Per jitter(3) | Period Jitter standard deviation | On PSIS (160 MHz) | - | 13.5 | - | ps |
| Per jitter(3) | Period Jitter standard deviation | On PSIDIV3 (53.33 MHz) | - | 23 | - | ps |
| LT jitter(3) | Long term jitter ethernet | On PSIS (100 MHz with 32 kHz CK_IN) | - | - | 13.7 (RMS), 96.7 (peak) | ns |
| LT jitter(3) | Long term jitter ethernet | On PSIS (100 MHz with 8 MHz CK_IN) | - | - | 0.79 (RMS), 6.69 (peak) | ns |
| LT jitter(3) | Long term jitter FDCAN | On PSIK (40 MHz with 32 kHz CK_IN) | - | - | 13.3 (RMS), 83.6 (peak) | ns |
| LT jitter(3) | Long term jitter FDCAN | On PSIK (40 MHz with 8 MHz CK_IN) | - | - | 0.775 (RMS), 6.16 (peak) | ns |

Notes:

1. Tested in production.
2. Frequencies above the supported product's maximum frequency can only be used once divided through PSIK or PSIDIV4 dividers.
3. Specified by design - Not tested in production.
4. Evaluated by characterization - Not tested in production.
5. The supply regulation consumption is common to HSI and PSI. (To be counted once if both oscillators are ON)
6. Jitter measurements are performed without clock source activated in parallel. The typical value refer to the standard deviation, while the maximum is the peak measurement of TIE-8 over 36 cycles.
7. Jitter measurements are performed without clock source activated in parallel. The typical value refer to the standard deviation, while the maximum is the peak measurement of TIE-16 over 36 cycles.

##### 5.3.9.3 Low-speed internal (LSI) RC oscillator

**Table 38. LSI oscillator characteristics**

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| fLSI | LSI frequency | VDD = 3.3 V, TJ = 25°C | 31.4(1) | 32 | 32.6(1) | kHz |
| fLSI | LSI frequency | TJ = -40 to 130°C | 29.4(2) | | 33.6(2) | kHz |
| fLSI | LSI frequency | TJ = -40 to 140°C | 28.6(2) | - | 33.6(2) | kHz |
| tsu(LSI)(3) | LSI oscillator startup time | - | - | 80 | 130 | µs |
| tstab(LSI)(3) | LSI oscillator stabilization time (5% of final value) | - | - | 120 | 170 | µs |
| IDD(LSI)(3) | LSI oscillator power consumption | - | - | 130 | 280 | nA |

Notes:

1. Guaranteed by test production.
2. Evaluated by characterization - Not tested in production.
3. Specified by design - Not tested in production.

#### 5.3.10 Flash memory characteristics

**Table 39. Flash memory characteristics**

Specified by design and not tested in production.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| IDD | Supply current | Word program | - | 1 | - | mA |
| IDD | Supply current | Page erase | - | 0.8 | - | mA |
| IDD | Supply current | Mass erase | - | 0.8 | - | mA |

**Table 40. Flash memory programming**

| Symbol | Parameter | Conditions | Min(1) | Typ | Max(1) | Unit |
|---|---|---|---|---|---|---|
| tprog | Word programming time | 128 bits (user area) | - | 20.0 | 160.0 | µs |
| tprog | Word programming time | 16 bits (OTP / EDATA area) | - | 20.0 | 160.0 | µs |
| tERASE 8KB | Page (8 KB) erase time | - | - | 2.0 | 2.1 | ms |
| tERASE 2KB | Page (2 KB) erase time | - | - | 2.0 | 2.1 | ms |
| tME | Bank Mass erase time | - | - | 96.0 | | ms |
| tME | Mass erase time | - | - | 192.0 | 200.0 | ms |
| Vprog | Programming voltage | - | 2.65 | - | 3.6 | V |

Notes:

1. Evaluated by characterization - Not tested in production.

**Table 41. Flash memory user and EDATA endurance and data retention**

| Symbol | Parameter | Conditions | Min(1) | Unit |
|---|---|---|---|---|
| NEND | Endurance | TJ = -40 to 140 °C | 10 | Kcycle |
| tRET | Data retention | 1 Kcycle at TJ = 125 °C | 10 | Year |
| tRET | Data retention | 1 Kcycle at TJ = 85 °C | 30 | Year |
| tRET | Data retention | 10 Kcycle at TJ = 55 °C | 30 | Year |

Notes:

1. Evaluated by characterization - Not tested in production.

#### 5.3.11 EMC characteristics

Susceptibility tests are performed on a sample basis during device characterization.

**Functional EMS (electromagnetic susceptibility)**

While a simple application is executed on the device (toggling two LEDs through the I/O ports), the device is stressed by two electromagnetic events until a failure occurs. The failure is indicated by the LEDs as follows:

- Electrostatic discharge (ESD) (positive and negative): applied to all device pins until a functional disturbance occurs. This test is compliant with the IEC 61000-4-2 standard.
- FTB (fast transient voltage burst) (positive and negative): applied to VDD and VSS pins through a 100 pF capacitor, until a functional disturbance occurs. This test is compliant with the IEC 61000-4-4 standard.

A device reset allows normal operations to be resumed.

The test results are given in the table below. They are based on the EMS levels and classes defined in application note *EMC design guide for STM8, STM32 and Legacy MCUs* (AN1709).

**Table 42. EMS characteristics**

| Symbol | Parameter | Conditions | Level/Class |
|---|---|---|---|
| VFESD | Voltage limits to be applied on any I/O pin to induce a functional disturbance | VDD = 3.3 V, TA = 25°C, fHCLK = 144 MHz, LQFP100 package conforming to IEC 61000-4-2 | 2B |
| VEFTB | Fast transient voltage burst limits to be applied through 100 pF on VDD and VSS pins to induce a functional disturbance | VDD = 3.3 V, TA = 25°C, fHCLK = 144 MHz, LQFP100 package conforming to IEC 61000-4-4 | 5A |

**Designing hardened software to avoid noise problems**

The EMC characterization and optimization are performed at component level with a typical application environment and simplified MCU software. Note that good EMC performance is highly dependent on the user application and the software in particular.

Therefore it is recommended that the user applies EMC software optimization and prequalification tests in relation with the EMC level requested for the application.

**Software recommendations**

The software flowchart must include the management of runaway conditions such as:

- Corrupted program counter
- Unexpected reset
- Critical data corruption (control registers)

**Prequalification trials**

Most of the common failures (unexpected reset and program counter corruption) can be reproduced by manually forcing a low state on the NRST pin or the oscillator pins for one second.

To complete these trials, ESD stress can be applied directly on the device, over the range of specification values. When unexpected behavior is detected, the software can be hardened to prevent unrecoverable errors occurring. See application note *Software techniques for improving microcontrollers EMC performance (AN1015)* for more details.

**Electromagnetic Interference (EMI)**

The electromagnetic field emitted by the device is monitored while a simple application is executed (toggling two LEDs through the I/O ports). This emission test is compliant with IEC 61967-2 standard that specifies the test board and the pin loading.

**Table 43. EMI characteristics for fHSE = 16 MHz and fHCLK = 144 MHz**

| Symbol | Parameter | Conditions | Monitored frequency band | Value | Unit |
|---|---|---|---|---|---|
| SEMI | Peak(1) | VDD = 3.6 V, TA = 25 ° C, LQFP100 package compliant with IEC 61967-2 | 0.1 MHz to 30 MHz | 16 | dBμV |
| SEMI | Peak(1) | VDD = 3.6 V, TA = 25 ° C, LQFP100 package compliant with IEC 61967-2 | 30 MHz to 130 MHz | -1 | dBμV |
| SEMI | Peak(1) | VDD = 3.6 V, TA = 25 ° C, LQFP100 package compliant with IEC 61967-2 | 130 MHz to 1 GHz | 21 | dBμV |
| SEMI | Peak(1) | VDD = 3.6 V, TA = 25 ° C, LQFP100 package compliant with IEC 61967-2 | 1 GHz to 2 GHz | 13 | dBμV |
| SEMI | Level(2) | VDD = 3.6 V, TA = 25 ° C, LQFP100 package compliant with IEC 61967-2 | 0.1 MHz to 2 GHz | 3.5 | - |

Notes:

1. Refer to the EMI radiated test section of the application note EMC design guide for STM8, STM32 and Legacy MCUs (AN1709).
2. Refer to the EMI level classification section of the application note EMC design guide for STM8, STM32 and Legacy MCUs (AN1709).

#### 5.3.12 Electrical sensitivity characteristics

Based on three different tests (ESD, latch-up) using specific measurement methods, the device is stressed in order to determine its performance in terms of electrical sensitivity.

**Electrostatic discharge (ESD)**

Electrostatic discharges (a positive then a negative pulse separated by 1 second) are applied to the pins of each sample according to each pin combination. The sample size depends on the number of supply pins in the device (3 parts × (n+1) supply pins). This test conforms to the ANSI/JEDEC standard.

**Table 44. ESD absolute maximum ratings**

Specified by design and not tested in production.

| Symbol | Ratings | Conditions | Packages | Class | Maximum value(1) | Unit |
|---|---|---|---|---|---|---|
| VESD(HBM) | Electrostatic discharge voltage (human body model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-001 | LQFP100 | 2 | 3400(2) | V |
| VESD(HBM) | Electrostatic discharge voltage (human body model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-001 | LQFP80 | 2 | 3400(2) | V |
| VESD(HBM) | Electrostatic discharge voltage (human body model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-001 | LQFP64 | 2 | 3400(2) | V |
| VESD(HBM) | Electrostatic discharge voltage (human body model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-001 | LQFP64 alternative pinout | 3A | 4000 | V |
| VESD(HBM) | Electrostatic discharge voltage (human body model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-001 | LQFP48 | 2 | 3400(2) | V |
| VESD(HBM) | Electrostatic discharge voltage (human body model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-001 | UFQFPN48 | 2 | 3400(2) | V |
| VESD(HBM) | Electrostatic discharge voltage (human body model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-001 | LQFP32 | 2 | 3400(2) | V |
| VESD(HBM) | Electrostatic discharge voltage (human body model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-001 | UFQFPN32 | 2 | 3400(2) | V |
| VESD(CDM) | Electrostatic discharge voltage (charge device model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-002 | LQFP100 | C3 | 1000 | V |
| VESD(CDM) | Electrostatic discharge voltage (charge device model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-002 | LQFP80 | C3 | 1000 | V |
| VESD(CDM) | Electrostatic discharge voltage (charge device model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-002 | LQFP64 | C3 | 1250 | V |
| VESD(CDM) | Electrostatic discharge voltage (charge device model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-002 | LQFP64 alternative pinout | C3 | 1250 | V |
| VESD(CDM) | Electrostatic discharge voltage (charge device model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-002 | LQFP48 | C3 | 1250 | V |
| VESD(CDM) | Electrostatic discharge voltage (charge device model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-002 | UFQFPN48 | C3 | 1250 | V |
| VESD(CDM) | Electrostatic discharge voltage (charge device model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-002 | LQFP32 | C3 | 1250 | V |
| VESD(CDM) | Electrostatic discharge voltage (charge device model) | TA = 25°C conforming to ANSI/ESDA/JEDEC JS-002 | UFQFPN32 | C3 | 1250 | V |

Notes:

1. Evaluated by characterization - Not tested in production.
2. All pins are characterized at a maximum value of 4000 V, except for PC14, whose maximum value is 3400 V, and PC15, whose maximum value is 3600 V.

**Static latch-up**

The following complementary static tests are required on three parts to assess the latch-up performance:

- A supply overvoltage is applied to each power supply pin.
- A current injection is applied to each input, output, and configurable I/O pin.

These tests are compliant with EIA/JESD 78E IC latch-up standard.

**Table 45. Electrical sensitivities**

| Symbol | Parameter | Conditions | Class |
|---|---|---|---|
| LU | Static latch-up class | TA = 130°C conforming to JESD78 | Level II A |

#### 5.3.13 I/O current injection characteristics

As a general rule, the current injection to the I/O pins, due to external voltage below VSS or above VDDIOx (for standard, 3.3 V‑capable I/O pins) must be avoided during normal product operation. However, in order to give an indication of the robustness of the microcontroller if abnormal injection accidentally happens, some susceptibility tests are performed on a sample basis during the device characterization.

**Functional susceptibility to I/O current injection**

While a simple application is executed on the device, the device is stressed by injecting current into the I/O pins programmed in floating-input mode. While this current is injected into the I/O pin, one at a time, the device is checked for functional failures.

The failure is indicated by an out-of-range parameter, such as an ADC error above a certain limit (higher than 5 LSB TUE), out of conventional limits of induced leakage current on adjacent pins (out of the 5 µA/+0 µA range), or other functional failure (for example reset occurrence or oscillator frequency deviation).

The characterization results are given in the table below. The negative induced leakage current is caused by the negative injection. The positive induced leakage current is caused by the positive injection.

**Table 46. I/O current injection susceptibility**

The I/O structure options listed in this table can be a concatenation of options including the option explicitly listed. For instance, TT_a refers to any TT I/O with _a option. TT_xx refers to any TT I/O and FT_xx refers to any FT I/O.

Evaluated by characterization - Not tested in production.

| Symbol | Description | Functional susceptibility: Negative injection | Functional susceptibility: Positive injection | Unit |
|---|---|---|---|---|
| IINJ | Injected current on PA4 pins | 0 | 0 | mA |
| IINJ | Injected current on PB13, PB14, PB15, PD8, PD9, PD10, PD11, PD12, PD13, PE0, and PE1 pins | 0 | N/A | mA |
| IINJ | Injected current on all other pins | 5 | N/A | mA |

#### 5.3.14 I/O port characteristics

**General input/output characteristics**

Unless otherwise specified, the parameters given in Table 47 are derived from tests performed under the conditions summarized in Table 17. All I/Os are designed as CMOS and TTL-compliant.

Note: For information on GPIO configuration, refer to the application note STM32 GPIO configuration for hardware settings and low‑power consumption (AN4899).

**Table 47. I/O static characteristics**

The I/O structure options listed in this table can be a concatenation of options including the option explicitly listed. For instance, TT_a refers to any TT I/O with _a option. TT_xx refers to any TT I/O and FT_xx refers to any FT I/O.

All I/Os are CMOS- and TTL-compliant (no software configuration required). Their characteristics cover more than the strict CMOS-technology or TTL parameters. The coverage of these requirements is shown in Figure 20.

The minimum and maximum values are specified for a junction temperature (TJ) of 125°C.

| Symbol | Parameter | Condition | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| VIL | I/O input low level voltage | 2.7 V < VDDIOx < 3.6 V | - | - | 0.3VDD (1) | V |
| VIL | I/O input low level voltage | 2.7 V < VDDIOx < 3.6 V | - | - | 0.4 VDD - 0.1 (2) | V |
| VIH | I/O input high level voltage | 2.7 V < VDDIOx < 3.6 V | 0.7VDD (1) | - | - | V |
| VIH | I/O input high level voltage | 2.7 V < VDDIOx < 3.6 V | 0.52VDD + 0.18 (2) | - | - | V |
| VHYS (2) | TT_xx, FT_xxx and NRST I/O input hysteresis | 2.7 V < VDDIOx < 3.6 V | - | 300 | - | mV |
| Ileak (3) | FT_xx Input leakage current (2) | 0 < VIN ≤ Max(VDDXXX) (4) | - | - | ±-200 | nA |
| Ileak (3) | FT_xx Input leakage current (2) | Max(VDDXXX) < VIN ≤ Max(VDDXXX + 1 V) (5)(6)(4) | - | - | ±2500 | nA |
| Ileak (3) | FT_xx Input leakage current (2) | Max(VDDXXX + 1) < VIN ≤ 5.5 V (5)(6)(4) | - | - | 750 | nA |
| Ileak (3) | TT_xx Input leakage current | 0 < VIN ≤ Max(VDDXXX + 1 V) (4) | - | - | ±200 | nA |
| RPU | Weak pull-up equivalent resistor (7) | VIN = VSS | 30 | 40 | 50 | kΩ |
| RPD | Weak pull-down equivalent resistor (7) | VIN = VDD | 30 | 40 | 50 | kΩ |
| CIO | I/O pin capacitance | - | - | 5 | - | pF |

Notes:

1. Compliant with CMOS requirements.
2. Specified by design - Not tested in production.
3. This parameter represents the pad leakage of the I/O itself. The total product pad leakage is provided by the following formula: ITotal_Ileak_max = 10 µA + [number of I/Os where VIN is applied on the pad] × Ilkg max.
4. Max(VDDXXX) is the maximum value of all the I/O supplies.
5. To sustain a voltage higher than the minimum of VDD or VDDA plus 0.3 V, disable the internal pull-up and pull-down resistors.
6. VIN must be less than Max(VDDXXX) + 3.6 V.
7. The pull-up and pull-down resistors are designed with a true resistance in series with a switchable PMOS/NMOS. This PMOS/NMOS contribution to the series resistance is minimal (~10% order).

*Digest note:* The first FT_xx leakage row is printed as "±-200" in the source.

All I/Os are CMOS- and TTL-compliant (no software configuration required). Their characteristics cover more than the strict CMOS-technology or TTL parameters. The coverage of these requirements is shown in the following figure.

**Figure 20. I/O input characteristics (all I/Os)**

A line chart of input threshold voltage VIN (V, vertical axis, 0 to 3 V) versus I/O supply voltage VDDIO (V, horizontal axis, 1.0 to 3.6 V in 0.1 V steps). It contains four sloped threshold lines and two horizontal TTL limits:

- Blue, upper: "Tested in production CMOS requirement VIHmin = 0.7 × VDDx". Runs from 0.7 V at VDDIO = 1 V to about 2.52 V at VDDIO = 3.6 V.
- Green, upper: "Based on simulation VIHmin = 0.52 × VDDx + 0.18 V". Starts at the same 0.7 V point at VDDIO = 1 V and rises to about 2.05 V at VDDIO = 3.6 V. It lies below the CMOS VIHmin line across the whole range.
- Green, lower: labeled "Based on simulation VILmax = 0.4 × VDDx + 0.1 V". The plotted line runs from 0.3 V at VDDIO = 1 V to about 1.34 V at VDDIO = 3.6 V, which matches the 0.4 VDD − 0.1 formula in Table 47, not the "+ 0.1 V" in the figure label.
- Blue, lower: "Tested in production CMOS requirement VILmax = 0.3 × VDDx". Runs from 0.3 V at VDDIO = 1 V to about 1.08 V at VDDIO = 3.6 V.
- Red horizontal line at 2.0 V: "TTL requirement VIH min = 2V", drawn from VDDIO = 2.7 V to 3.6 V.
- Red horizontal line at 0.8 V: "TTL requirement VIL max = 0.8V", drawn from VDDIO = 2.7 V to 3.6 V.

The simulated VIH line stays below the TTL VIH min (2 V) up to about VDDIO = 3.5 V. The simulated VIL line stays above the TTL VIL max (0.8 V) over the whole 2.7 V to 3.6 V range. The tested CMOS VIL line crosses 0.8 V at about VDDIO = 2.7 V. Together these show the I/Os meet both the CMOS and TTL thresholds over the 2.7 V to 3.6 V operating range.

**Output driving current**

The GPIOs (except PC14, PC15) can sink or source up to ± 8 mA, and sink or source up to ± 20 mA (with a relaxed VOL/VOH). PC14, PC15 are limited in source capability: +3 mA shared between the I/Os.

In the user application, the number of I/O pins that can drive current must be limited to respect the absolute maximum rating specified in Section 5.2: Absolute maximum ratings:

- The sum of the currents sourced by all the I/Os on VDDIOx, plus the maximum consumption of the MCU sourced on VDD, cannot exceed the absolute maximum rating ∑IVDD (see Table 15. Current characteristics).
- The sum of the currents sunk by all the I/Os on VSS, plus the maximum consumption of the MCU sunk on VSS, cannot exceed the absolute maximum rating ∑IVSS (see Table 15. Current characteristics).

**Output voltage levels**

Unless otherwise specified, the parameters given in the table below are derived from tests performed under the ambient temperature and supply voltage conditions summarized in Table 17. All I/Os are CMOS- and TTL-compliant (FT or TT unless otherwise specified).

**Table 48. Output voltage characteristics (all I/Os except PC14 and PC15)**

The I/O structure options listed in this table can be a concatenation of options including the option explicitly listed. For instance, TT_a refers to any TT I/O with _a option. TT_xx refers to any TT I/O and FT_xx refers to any FT I/O.

TTL and CMOS outputs are compatible with JEDEC standards JESD36 and JESD52.

The IIO current sourced or sunk by the device must always respect the absolute maximum rating specified in Table 15, and the sum of the currents sourced or sunk by all the I/Os (I/O ports and control pins) must always respect the absolute maximum ratings ΣIIO.

The minimum and maximum values are specified for a junction temperature (TJ) of 125°C.

| Symbol | Parameter | Conditions (2) | Min | Max | Unit |
|---|---|---|---|---|---|
| VOL | Output low-level voltage | CMOS port (1), \|IIO\| = 8 mA, 2.7 V ≤ VDD ≤ 3.6 V | - | 0.4 | V |
| VOH | Output high-level voltage | CMOS port (1), \|IIO\| = -8 mA, 2.7 V ≤ VDD ≤ 3.6 V | VDD - 0.4 | - | V |
| VOL (2) | Output low-level voltage | TTL port (1), \|IIO\| = 8 mA, 2.7 V ≤ VDD ≤ 3.6 V | - | 0.4 | V |
| VOH (2) | Output high-level voltage | TTL port (1), \|IIO\| = -8 mA, 2.7 V ≤ VDD ≤ 3.6 V | 2.4 | - | V |
| VOL (2) | Output low-level voltage | \|IIO\| = 20 mA, 2.7 V ≤ VDD ≤ 3.6 V | - | 1.3 | V |
| VOH (2) | Output high-level voltage | \|IIO\| = -20 mA, 2.7 V ≤ VDD ≤ 3.6 V | VDD - 1.3 | - | V |
| VOLFM+ (2) | Output low-level voltage for a FT_f I/O pin in FM+ mode | \|IIO\| = 20 mA, 2.7 V ≤ VDD ≤ 3.6 V | - | 0.4 | V |

Notes:

1. TTL and CMOS outputs are compatible with JEDEC standards JESD36 and JESD52.
2. Specified by design - Not tested in production.

**Table 49. Output voltage characteristics for PC14 and PC15**

Specified by design and not tested in production.

The minimum and maximum values are specified for a junction temperature TJ = 125°C.

The IIO current sourced or sunk by the device must always comply with the absolute maximum rating specified in Table 15. Current characteristics. Additionally, the sum of the currents sourced or sunk by all the I/Os (I/O ports and control pins) must always comply with the absolute maximum ratings ΣIIO.

| Symbol | Parameter | Conditions (3) | Min | Max | Unit |
|---|---|---|---|---|---|
| VOL | Output low level voltage | CMOS port (1), IIO = 0.5 mA, 2.7 V ≤ VDD ≤ 3.6 V | - | 0.4 | V |
| VOH | Output high level voltage | CMOS port (1), IIO = -0.5 mA, 2.7 V ≤ VDD ≤ 3.6 V | VDD - 0.4 | - | V |
| VOL (2) | Output low level voltage | TTL port (1), IIO = 0.5 mA, 2.7 V ≤ VDD ≤ 3.6 V | - | 0.4 | V |
| VOH (2) | Output high level voltage | TTL port (1), IIO = -0.5 mA, 2.7 V ≤ VDD ≤ 3.6 V | 2.4 | - | V |

Notes:

1. TTL and CMOS outputs are compatible with JEDEC standards JESD36 and JESD52.
2. Specified by design - Not tested in production.

*Digest note:* The "Conditions" column header carries a footnote marker (3), but the source lists no note 3 for this table.

**Output AC characteristics**

The definition and values of output AC characteristics are given in Figure 21. Output AC characteristics definition and in the table below respectively.

Unless otherwise specified, the parameters given are derived from tests performed under the ambient temperature and supply voltage conditions summarized in Table 17.

**Table 50. Output AC characteristics (all I/Os except PC13)**

The I/O structure options listed in this table can be a concatenation of options including the option explicitly listed. For instance, TT_a refers to any TT I/O with _a option. TT_xx refers to any TT I/O and FT_xx refers to any FT I/O.

The I/O speed is configured using the OSPEEDRy[1:0] bits. Refer to the product reference manual for a description of GPIO port configuration register.

Specified by design - Not tested in production.

The minimum and maximum values are specified for a junction temperature TJ = 125°C.

The Speed column is the OSPEEDRy[1:0] setting.

| Speed | Symbol | Parameter | Conditions | Min | Max | Unit |
|---|---|---|---|---|---|---|
| 00 | Fmax (1) | Maximum frequency | C = 50 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 4 | MHz |
| 00 | Fmax (1) | Maximum frequency | C = 30 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 4 | MHz |
| 00 | Fmax (1) | Maximum frequency | C = 10 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 4 | MHz |
| 00 | tr/tf (2) | Output high to low level fall time and output low to high level rise time | C = 50 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 51 | ns |
| 00 | tr/tf (2) | Output high to low level fall time and output low to high level rise time | C = 30 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 46 | ns |
| 00 | tr/tf (2) | Output high to low level fall time and output low to high level rise time | C = 10 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 40 | ns |
| 01 | Fmax (1) | Maximum frequency | C = 50 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 12 | MHz |
| 01 | Fmax (1) | Maximum frequency | C = 30 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 12 | MHz |
| 01 | Fmax (1) | Maximum frequency | C = 10 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 12 | MHz |
| 01 | tr/tf (2) | Output high to low level fall time and output low to high level rise time | C = 50 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 19 | ns |
| 01 | tr/tf (2) | Output high to low level fall time and output low to high level rise time | C = 30 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 17 | ns |
| 01 | tr/tf (2) | Output high to low level fall time and output low to high level rise time | C = 10 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 14 | ns |
| 10 | Fmax (1)(3) | Maximum frequency | C = 50 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 45 | MHz |
| 10 | Fmax (1)(3) | Maximum frequency | C = 30 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 50 | MHz |
| 10 | Fmax (1)(3) | Maximum frequency | C = 10 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 55 | MHz |
| 10 | tr/tf (2)(3) | Output high to low level fall time and output low to high level rise time | C = 50 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 7 | ns |
| 10 | tr/tf (2)(3) | Output high to low level fall time and output low to high level rise time | C = 30 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 6 | ns |
| 10 | tr/tf (2)(3) | Output high to low level fall time and output low to high level rise time | C = 10 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 4 | ns |
| 11 | Fmax (1)(3) | Maximum frequency | C = 50 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 90 | MHz |
| 11 | Fmax (1)(3) | Maximum frequency | C = 30 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 96 | MHz |
| 11 | Fmax (1)(3) | Maximum frequency | C = 10 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 110 | MHz |
| 11 | tr/tf (2)(3) | Output high to low level fall time and output low to high level rise time | C = 50 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 5 | ns |
| 11 | tr/tf (2)(3) | Output high to low level fall time and output low to high level rise time | C = 30 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 4 | ns |
| 11 | tr/tf (2)(3) | Output high to low level fall time and output low to high level rise time | C = 10 pF, 2.7 V ≤ VDD ≤ 3.6 V | - | 3 | ns |

Notes:

1. The maximum frequency is defined with the following conditions: (tr+tf) ≤ 2/3 T
2. The fall and rise times are defined between 90% and 10% and between 10% and 90% of the output waveform, respectively.
3. Compensation system enabled.

**Figure 21. Output AC characteristics definition**

The figure shows one period of an output waveform: a rising edge, a high plateau, a falling edge and a low plateau, followed by the start of the next rising edge. On the rising edge, the 10%, 50% and 90% levels are marked, and the rise time tr(IO)out is measured from the 10% point to the 90% point. On the falling edge, the 90%, 50% and 10% levels are marked, and the fall time tf(IO)out is measured from the 90% point to the 10% point. The period T is measured from the 10% point of one rising edge to the 10% point of the next rising edge. Caption text in the figure: "Maximum frequency is achieved with a duty cycle at (45 - 55%) when loaded by the specified capacitance."

#### 5.3.15 NRST pin characteristics

The NRST pin input driver uses the CMOS technology. It is connected to a permanent pullup resistor, RPU.

Unless otherwise specified, the parameters given in the table below are derived from tests performed under the ambient temperature and supply voltage conditions summarized in Table 17.

**Table 51. NRST pin characteristics**

Specified by design and not tested in production.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| VIL(NRST) | NRST input low-level voltage | - | - | - | 0.3 x VDDIOx | V |
| VIH(NRST) | NRST input high-level voltage | - | 0.7 x VDDIOx | - | - | V |
| Vhys(NRST) | NRST Schmitt trigger voltage hysteresis | - | - | 200 | - | mV |
| RPU | Weak pull-up equivalent resistor (1) | VIN = VSS | 30 | 40 | 50 | kΩ |
| tF(NRST) | NRST input filtered pulse | - | - | - | 50 | ns |
| tNF(NRST) | NRST input not-filtered pulse | 2.7 V ≤ VDD ≤ 3.6 V | 350 | - | - | ns |

Notes:

1. The pull-up is designed with a true resistance in series with a switchable PMOS. This PMOS contribution to the series resistance is minimal (~10 % order).

**Figure 22. Recommended NRST pin protection**

Outside the device, an "External reset circuit (1)" connects to the NRST pin (2). It is a push-button switch from NRST to ground, in parallel with a 0.1 µF (3) capacitor from NRST to ground. Inside the device, NRST connects to the internal pull-up resistor RPU, which goes to VDD. NRST also feeds a Schmitt-trigger input buffer. The buffer output goes through a Filter block, and the filter output is the "Internal reset" signal.

Figure notes:

1. The reset network protects the device against parasitic resets.
2. The user must ensure that the level on the NRST pin can go below the VIL(NRST) max level specified in the above table. Otherwise the reset is not taken into account by the device.
3. The external capacitor on NRST must be placed as close as possible to the device.

#### 5.3.16 Extended interrupt and event controller input (EXTI) characteristics

The pulse on the interrupt input must have a minimal length in order to guarantee that it is detected by the event controller.

**Table 52. EXTI input characteristics**

Specified by design and not tested in production.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| PLEC | Pulse length to event controller | - | 20 | - | - | ns |

#### 5.3.17 12-bit analog-to-digital converter ADC characteristics

Unless otherwise specified, the parameters given in Table 53 are values derived from tests performed under ambient temperature, fHCLK frequency, and VDDA supply voltage conditions summarized in Table 17.

Note: It is recommended to perform a calibration after each power-up.

**Table 53. 12-bit ADC characteristics**

Specified by design - Not tested in production.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| VDDA | Analog power supply for ADC ON | - | 2.70 | - | 3.6 | V |
| VREF+ | Positive reference voltage | - | 2.5 | - | VDDA | V |
| VREF- | Negative reference voltage | - | VSSA | VSSA | VSSA | V |
| fADC | ADC clock frequency | 2.7 V ≤ VDDA ≤ 3.6 V | 8 | - | 36 | MHz |
| fS with RAIN = 47 Ω and CPCB = 22 pF | Sampling rate for slow channels | Resolution = 12 bits; All modes; 2.7 V ≤ VDDA ≤ 3.6 V; -40°C ≤ TJ ≤ 140°C; fADC = 36 MHz; SMP = 2.5 | - | 2.25 | - | MSPS |
| fS with RAIN = 47 Ω and CPCB = 22 pF | Sampling rate for slow channels | Resolution = 10 bits; All modes; 2.7 V ≤ VDDA ≤ 3.6 V; -40°C ≤ TJ ≤ 140°C; fADC = 36 MHz; SMP cell blank | - | 2.57 | - | MSPS |
| fS with RAIN = 47 Ω and CPCB = 22 pF | Sampling rate for slow channels | Resolution = 8 bits; All modes; 2.7 V ≤ VDDA ≤ 3.6 V; -40°C ≤ TJ ≤ 140°C; fADC = 36 MHz; SMP cell blank | - | 3 | - | MSPS |
| fS with RAIN = 47 Ω and CPCB = 22 pF | Sampling rate for slow channels | Resolution = 6 bits; All modes; 2.7 V ≤ VDDA ≤ 3.6 V; -40°C ≤ TJ ≤ 140°C; fADC = 36 MHz; SMP cell blank | - | 4.5 | - | MSPS |
| tTRIG | External trigger period | Resolution = 12 bits | 16 | - | - | 1/fADC |
| VAIN | Conversion voltage range | - | 0 | - | VREF+ | V |
| RAIN (1) | External input impedance | Resolution = 12 bits, TJ = 140°C | - | - | 110 | Ω |
| RAIN (1) | External input impedance | Resolution = 12 bits, TJ = 125°C | - | - | 610 | Ω |
| RAIN (1) | External input impedance | Resolution = 10 bits, TJ = 140°C | - | - | 2305 | Ω |
| RAIN (1) | External input impedance | Resolution = 10 bits, TJ = 125°C | - | - | 4290 | Ω |
| RAIN (1) | External input impedance | Resolution = 8 bits, TJ = 140°C | - | - | 11110 | Ω |
| RAIN (1) | External input impedance | Resolution = 8 bits, TJ = 125°C | - | - | 15860 | Ω |
| RAIN (1) | External input impedance | Resolution = 6 bits, TJ = 140°C | - | - | 46890 | Ω |
| RAIN (1) | External input impedance | Resolution = 6 bits, TJ = 125°C | - | - | 79000 | Ω |
| CADC | Internal sample and hold capacitor | - | - | 3 | - | pF |
| tADCVREG_STUP | ADC LDO startup time | - | - | - | 10 | µs |
| tSTAB | ADC power-up time | LDO already started | 1 | - | - | conversion cycle |
| tOFF_CAL | Offset calibration time | - | 85 | 85 | 85 | 1/fADC |
| tLATR | Trigger conversion latency for regular and injected channels | Trigger from an asynchronous clock | 3 | - | 4 | 1/fADC |
| tLATR | Trigger conversion latency for regular and injected channels | Trigger from a synchronous clock | 3 | 3 | 3 | 1/fADC |
| tS | Sampling time | - | 2.5 | - | 288.5 | 1/fADC |
| tCONV | Total conversion time (including sampling time) | N-bits resolution | tS + 1.5 + N | tS + 1.5 + N | tS + 1.5 + N | 1/fADC |
| IDDA(ADC) | ADC consumption on VDD, VDDA and VREF | fS = 2.25 MSPS | - | 200 | - | µA |

Notes:

1. High temperature generate leakage current on ADC inputs. This current create voltage drop through Rain directly affecting ADC accuracy (worst case when VAIN = VDDA). To limit this effect to a tolerance of 2LSBs, you must respect Rain max tables.

*Digest note:* In the source, the VREF-, tOFF_CAL, tLATR (synchronous clock) and tCONV values are each one cell spanning the Min/Typ/Max columns. They are repeated in all three columns here.

*Digest note:* In the fS rows, the source prints "SMP = 2.5" only in the 12-bit row; the SMP cells of the 10-, 8- and 6-bit rows are blank. Using tCONV = tS + 1.5 + N with tS = 2.5 cycles at fADC = 36 MHz gives 2.25 MSPS (12-bit), 2.571 MSPS (10-bit), 3 MSPS (8-bit) and 3.6 MSPS (6-bit). Figure 26 also shows 3.6 Msps at SMP = 2.5 cycles for 6-bit resolution, while Table 53 lists 4.5 MSPS for 6 bits.

**Table 54. 12-bit ADC accuracy**

ADC accuracy values are measured after internal calibration. Resolution = 12 bits, no oversampling.

Evaluated by characterization on LQFP100. Packages without a VREF- pad can have degraded specifications. Not tested in production.

| Symbol | Parameter | Min | Typ | Max | Unit |
|---|---|---|---|---|---|
| ET | Total unadjusted error | - | 4 | 5.7 | LSB |
| EO | Offset error | - | ±2.5 | ±5 | LSB |
| EG | Gain error | - | 2.6 | 6 | LSB |
| ED | Differential linearity error | -1 | - | 1.3 | LSB |
| EL | Integral linearity error | -3 | ±2.5 | 3 | LSB |
| ENOB | Effective number of bits | - | 10.7 | - | bits |
| SINAD | Signal-to-noise and distortion ratio | - | 66 | - | dB |
| SNR | Signal-to-noise ratio | - | 68 | - | dB |
| THD | Total harmonic distortion | - | -70 | - | dB |

**Minimum sampling time versus RAIN (Figures 23 to 26)**

Figures 23 to 26 share one format. The horizontal axis is the external source resistance RAIN in Ω on a logarithmic scale from 50 Ω to 40 kΩ, with ticks at 50, 100, 200, 300, 400, 500, 1k, 2k, 3k, 4k, 5k, 10k, 20k, 30k and 40k. The vertical axis is sampling time. A heavy dash-dot curve shows the "Minimum sampling time (ns)" required for a given RAIN. Thin horizontal lines are the "Valid sampling time (ns)" levels, one per available SMP setting. Each line is labeled with the resulting sampling rate (Msps), the sampling time TS and the SMP value in ADC clock cycles. All four charts use fADC = 36 MHz, CAIN = 22 pF, Tj = 140°C and VDD = VDDA = 2.7 V.

An SMP setting is valid for a given RAIN when its horizontal line is above the minimum-sampling-time curve. In Figures 23 to 25, vertical dotted lines mark where the curve crosses each level, which is the largest RAIN usable with that setting. The curve is nearly flat below about 100 to 200 Ω and rises steeply with RAIN above that.

*Digest note:* The crossing points in the lists below are approximate values read from the plotted curves. The source does not tabulate them.

**Figure 23. Minimum sampling time versus RAIN for 12 bits resolution**

Legend: Resolution = 12 bits, FADC = 36 MHz, CAIN = 22 pF, Tj = 140°C, VDD = VDDA = 2.7 V.

The valid sampling-time levels, with the approximate maximum RAIN for each, are:

- 2.25 Msps (TS = 69 ns, SMP = 2.5 cycles): up to about 360 Ω.
- 2 Msps (TS = 125 ns, SMP = 4.5 cycles): up to about 720 Ω.
- 1.714 Msps (TS = 208 ns, SMP = 7.5 cycles): up to about 1.2 kΩ.
- 1.385 Msps (TS = 347 ns, SMP = 12.5 cycles): up to about 2.1 kΩ.
- 0.947 Msps (TS = 681 ns, SMP = 24.5 cycles): up to about 4.2 kΩ.
- 0.59 Msps (TS = 1319 ns, SMP = 47.5 cycles): up to about 8.6 kΩ.
- 0.237 Msps (TS = 3847 ns, SMP = 138.5 cycles): up to about 26 kΩ.
- 0.119 Msps (TS = 8014 ns, SMP = 288.5 cycles): above about 26 kΩ, through the end of the plotted curve (about 32 kΩ).

**Figure 24. Minimum sampling time versus RAIN for 10 bits resolution**

Legend: Resolution = 10 bits, FADC = 36 MHz, CAIN = 22 pF, Tj = 140°C, VDD = VDDA = 2.7 V.

The valid sampling-time levels, with the approximate maximum RAIN for each, are:

- 2.571 Msps (TS = 69 ns, SMP = 2.5 cycles): up to about 510 Ω.
- 2.25 Msps (TS = 125 ns, SMP = 4.5 cycles): up to about 1.0 kΩ.
- 1.895 Msps (TS = 208 ns, SMP = 7.5 cycles): up to about 1.7 kΩ.
- 1.5 Msps (TS = 347 ns, SMP = 12.5 cycles): up to about 3.0 kΩ.
- 1 Msps (TS = 681 ns, SMP = 24.5 cycles): up to about 6.2 kΩ.
- 0.61 Msps (TS = 1319 ns, SMP = 47.5 cycles): up to about 12 kΩ.
- 0.24 Msps (TS = 3847 ns, SMP = 138.5 cycles): above about 12 kΩ, through the end of the plotted curve (about 33 kΩ). At that point the curve is still just below this level.

No 288.5-cycle level is drawn in this figure.

**Figure 25. Minimum sampling time versus RAIN for 8 bits resolution**

Legend: Resolution = 8 bits, FADC = 36 MHz, CAIN = 22 pF, Tj = 140°C, VDD = VDDA = 2.7 V.

The valid sampling-time levels, with the approximate maximum RAIN for each, are:

- 3 Msps (TS = 69 ns, SMP = 2.5 cycles): up to about 940 Ω.
- 2.571 Msps (TS = 125 ns, SMP = 4.5 cycles): up to about 1.9 kΩ.
- 2.118 Msps (TS = 208 ns, SMP = 7.5 cycles): up to about 3.2 kΩ.
- 1.636 Msps (TS = 347 ns, SMP = 12.5 cycles): up to about 5.6 kΩ.
- 1.059 Msps (TS = 681 ns, SMP = 24.5 cycles): up to about 11 kΩ.
- 0.632 Msps (TS = 1319 ns, SMP = 47.5 cycles): up to about 21 kΩ.
- 0.243 Msps (TS = 3847 ns, SMP = 138.5 cycles): above about 21 kΩ, through the end of the plotted curve (about 32 kΩ). The curve stays well below this level.

**Figure 26. Minimum sampling time versus RAIN for 6 bits resolution**

Legend: Resolution = 6 bits, FADC = 36 MHz, CAIN = 22 pF, Tj = 140°C, VDD = VDDA = 2.7 V.

The valid sampling-time levels, with the approximate maximum RAIN for each, are listed below. This figure has no dotted crossing markers.

- 3.6 Msps (TS = 69 ns, SMP = 2.5 cycles): up to about 4.0 kΩ.
- 3 Msps (TS = 125 ns, SMP = 4.5 cycles): up to about 7.8 kΩ.
- 2.4 Msps (TS = 208 ns, SMP = 7.5 cycles): up to about 13 kΩ.
- 1.8 Msps (TS = 347 ns, SMP = 12.5 cycles): up to about 21 kΩ.
- 1.125 Msps (TS = 681 ns, SMP = 24.5 cycles): above about 21 kΩ, through the end of the plotted curve (about 33 kΩ). At that point the curve is still just below this level.

**Figure 27. ADC accuracy characteristics**

The figure plots ADC output code (vertical axis) against analog input voltage (horizontal axis). The header defines 1 LSB = VREF+ / 2^n (or VDDA / 2^n), where n is the ADC resolution.

The vertical axis is labeled 0 through 7 at the bottom and 2^n-3, 2^n-2 and 2^n-1 at the top, with an axis break between them. The horizontal axis starts at VSSA. It is marked (1/2^n)×VREF+, (2/2^n)×VREF+, up to (7/2^n)×VREF+. After an axis break it continues with (2^n-3/2^n)×VREF+, (2^n-2/2^n)×VREF+, (2^n-1/2^n)×VREF+ and (2^n/2^n)×VREF+, and ends at VREF+ (VDDA).

The figure shows three curves:

1. (1) An example of an actual transfer curve, drawn as a staircase with uneven steps.
2. (2) The ideal transfer curve, a regular staircase with 1 LSB steps. One step width is labeled "1 LSB ideal".
3. (3) The end-point correlation line, a straight line through the first and last actual transitions.

The errors are annotated on the plot and defined in the legend:

- ET = total unadjusted error: maximum deviation between the actual and ideal transfer curves.
- EO = offset error: maximum deviation between the first actual transition and the first ideal one. It is drawn at the bottom-left, between the first ideal and first actual transitions.
- EG = gain error: deviation between the last ideal transition and the last actual one. It is drawn at the top-right.
- ED = differential linearity error: maximum deviation between actual steps and the ideal one.
- EL = integral linearity error: maximum deviation between any actual transition and the end point correlation line.

**Figure 28. Typical connection diagram when using the ADC with FT/TT pins featuring analog switch function**

Outside the device, a voltage source VAIN drives the pin through a series resistor RAIN (1). A capacitor Cparasitic (2) connects from the pin side of RAIN to ground.

Inside the device, the pin node has three connections:

- A leakage current source Ilkg (3) to VSS.
- A protection diode to VSS.
- A protection diode to VDDA (4).

The pin node then passes through the I/O analog switch into the "Sample-and-hold ADC converter" block. That block contains a protection diode to VREF+ (4) and the "Sampling switch with multiplexing". After the sampling switch is a series resistor RADC, then the sampling capacitor CADC to VSSA, then the "Converter".

Figure notes:

1. Refer to the ADCx characteristic table for the values of RAIN and CADC.
2. Cparasitic represents the capacitance of the PCB (dependent on soldering and PCB layout quality) plus the pad capacitance (refer to Section 5.3.14: I/O port characteristics for the value of the pad capacitance). A high Cparasitic value downgrades the conversion accuracy. To remedy this, fADC must be reduced.
3. Refer to Section 5.3.14: I/O port characteristics for the values of Ilkg.
4. Refer to Section 5.1.6: Power supply scheme.

**General PCB design guidelines**

The power-supply decoupling must be performed as shown in the corresponding power‑supply scheme. The 100 nF capacitor must be ceramic (good quality) and must be placed as close as possible to the chip.

#### 5.3.18 Temperature sensor characteristics

**Table 55. Temperature sensor characteristics**

| Symbol | Parameter | Min | Typ | Max | Unit |
|---|---|---|---|---|---|
| TL (1) | VSENSE linearity with temperature (from Vsensor voltage) | - | - | 3 | °C |
| Avg_Slope (2) | Average slope (from Vsense voltage) | - | 2.14 | - | mV/°C |
| V30 (3) | Voltage at 30° C (± 1 ° C) | - | 0.65 | - | V |
| tstart_run (1) | Startup time in Run mode (buffer startup) | - | - | 25.2 | µs |
| tS_temp (1) | ADC sampling time when reading the temperature | 13 | - | - | µs |
| Isens (1) | Sensor consumption | - | 0.18 | 0.29 | µA |
| Isensbuf (1) | Sensor buffer consumption | - | 3.8 | 6.5 | µA |

Notes:

1. Specified by design - Not tested in production.
2. Evaluated by characterization - Not tested in production.
3. Measured at VDDA = 3.3 V ± 10 mV. The V30 ADC conversion result is stored in the TS_CAL1.

**Table 56. Temperature sensor calibration values**

| Symbol | Parameter | Memory address |
|---|---|---|
| TS_CAL1 | Temperature sensor raw data acquired value at 30 °C, VDDA = 3.3 V | 0x08FF F814 - 0x08FF F815 |
| TS_CAL2 | Temperature sensor raw data acquired value at 140 °C, VDDA = 3.3 V | 0x08FF F818 - 0x08FF F819 |

#### 5.3.19 Digital-to-analog converter characteristics (DAC)

**Table 57. DAC characteristics**

Specified by design and not tested in production.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| VDDA | Analog supply voltage | - | 2.7 | - | (blank) | V |
| VREF+ | Positive reference voltage | - | 2.5 | - | VDDA | V |
| VREF- | Negative reference voltage | - | - | VSSA | - | V |
| RL | Resistive Load | DAC output buffer ON, connected to VSSA | 5 | - | - | KΩ |
| RL | Resistive Load | DAC output buffer ON, connected to VDDA | 25 | - | - | KΩ |
| RO | Output Impedance | DAC output buffer OFF | 10.3 | 13.00 | 16 | KΩ |
| RBON | Output impedance sample and hold mode, output buffer ON | DAC output buffer ON, VDD = 2.7 V | - | - | 1.6 | KΩ |
| RBOFF | Output impedance sample and hold mode, output buffer OFF | DAC output buffer OFF, VDD = 2.7 V | - | - | 17.8 | KΩ |
| CL | Capacitive Load | DAC output buffer OFF | - | - | 50 | pF |
| CSH | Capacitive Load | Sample and Hold mode | (blank) | 0.10 | 1 | µF |
| VDAC_OUT | Voltage on DAC_OUT output | DAC output buffer ON | 0.2 | - | VDDA −0.2 | V |
| VDAC_OUT | Voltage on DAC_OUT output | DAC output buffer OFF | 0 | - | VREF+ | V |
| tSETTLING | Settling time (full scale: for a 12-bit code transition between the lowest and the highest input codes when DAC_OUT reaches the final value of ±0.5LSB, ±1LSB, ±2LSB, ±4LSB, ±8LSB) | Normal mode DAC output buffer ON CL ≤ 50 pF, RL ≥ 5 kW; ±0.5 LSB | - | 1.7 | 3 | µs |
| tSETTLING | Settling time (as above) | Normal mode DAC output buffer ON CL ≤ 50 pF, RL ≥ 5 kW; ±1 LSB | - | 1.66 | 2.87 | µs |
| tSETTLING | Settling time (as above) | Normal mode DAC output buffer ON CL ≤ 50 pF, RL ≥ 5 kW; ±2 LSB | - | 1.65 | 2.84 | µs |
| tSETTLING | Settling time (as above) | Normal mode DAC output buffer ON CL ≤ 50 pF, RL ≥ 5 kW; ±4 LSB | - | 1.63 | 2.78 | µs |
| tSETTLING | Settling time (as above) | Normal mode DAC output buffer ON CL ≤ 50 pF, RL ≥ 5 kW; ±8 LSB | - | 1.61 | 2.7 | µs |
| tSETTLING | Settling time (as above) | Normal mode, DAC output buffer OFF, ±1 LSB CL = 10 pF | - | 1.7 | 2 | µs |
| tWAKEUP | Wakeup time from off state (setting the Enx bit in the DAC Control register) until the ±1LSB final value | Normal mode, DAC output buffer ON, CL ≤ 50 pF, RL = 5 Ω | - | 5 | 7.5 | µs |
| tWAKEUP | Wakeup time from off state (setting the Enx bit in the DAC Control register) until the ±1LSB final value | Normal mode, DAC output buffer OFF, CL ≤ 10 pF | - | 2 | 5.0 | µs |
| PSRR | DC VDDA supply rejection ratio | Normal mode DAC output buffer ON CL ≤ 50 pF, RL = 5 kW | - | -80 | -28 | dB |
| tSAMP | Sampling time in Sample and Hold mode CSH=100nF (Code transition between the lowest input code and the highest input code when DACOUT reaches final value +/- 1LSB) | MODE<2:0>_V12 = 100/101 (BUFFER ON) | - | 0.7 | 2.6 | ms |
| tSAMP | Sampling time in Sample and Hold mode (as above) | MODE<2:0>_V12 = 110 (BUFFER OFF) | - | 11.5 | 18.7 | ms |
| tSAMP | Sampling time in Sample and Hold mode (as above) | MODE<2:0>_V12 = 111 BUFFER OFF (DAC_OUT pin not connected, internal connection only) | - | 0.3 | 0.6 | µs |
| Ileak | Output leakage current | - | - | - | - | nA |
| CIint | Internal sample and hold capacitor | - | 1.43 | 1.75 | 2 | pF |
| tTRIM | Middle code offset trim time | DAC output buffer ON | 50 | - | - | µs |
| Voffset | Middle code offset for 1 trim code step | VREF+ = 3.6 V | - | 850 | - | µV |
| IDDA(DAC) | DAC quiescent consumption from VDDA | DAC output buffer ON, No load, middle code (0x800) | - | 315 | - | µA |
| IDDA(DAC) | DAC quiescent consumption from VDDA | DAC output buffer ON, No load, worst code (0xF1C) | - | 450 | - | µA |
| IDDA(DAC) | DAC quiescent consumption from VDDA | DAC output buffer OFF, No load, middle/worst code (0x800) | - | 20 | - | µA |
| IDDA(DAC) | DAC quiescent consumption from VDDA | Sample and Hold mode, CSH=100 nF | - | 315*Ton/(Ton+Toff) | - | µA |
| IDDV(DAC) | DAC consumption from VREF+ | DAC output buffer ON, No load, middle code (0x800) | - | 185 | - | µA |
| IDDV(DAC) | DAC consumption from VREF+ | DAC output buffer ON, No load, worst code (0xF1C) | - | 185 | - | µA |
| IDDV(DAC) | DAC consumption from VREF+ | DAC output buffer OFF, No load, middle/worst code (0x800) | - | 155 | - | µA |
| IDDV(DAC) | DAC consumption from VREF+ | Sample and Hold mode, Buffer ON, CSH=100 nF (worst code) | - | 185*Ton/(Ton+Toff) | - | µA |
| IDDV(DAC) | DAC consumption from VREF+ | Sample and Hold mode, Buffer OFF, CSH=100 nF (worst code) | - | 155*Ton/(Ton+Toff) | - | µA |

*Digest note:* The source prints the resistive-load conditions as "kW" (meaning kΩ), the tWAKEUP condition as "RL = 5 Ω", and the resistance unit as "KΩ". These are reproduced as printed.

**Figure 29. 12-bit buffered/non-buffered DAC**

The block is labeled "Buffered/non-buffered DAC". Inside it, the 12-bit digital-to-analog converter output goes through an optional output Buffer (1), drawn dashed, to the DAC_OUTx pin. Outside the device, DAC_OUTx connects to a load made of RLOAD in parallel with CLOAD, both to ground.

Figure notes:

1. The DAC integrates an output buffer that can be used to reduce the output impedance and to drive external loads directly without the use of an external operational amplifier. The buffer can be bypassed by configuring the BOFFx bit in the DAC_CR register.

**Table 58. DAC accuracy**

Specified by design - not tested in production unless otherwise stated.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| DNL | Differential non linearity (1) | DAC output buffer ON | -2 | - | 2 | LSB |
| DNL | Differential non linearity (1) | DAC output buffer OFF | -2 | - | 2 | LSB |
| (blank) | Monotonicity | 10 bits | - | - | - | - |
| INL | Integral non linearity (2) | DAC output buffer ON, CL ≤ 50 pF, RL ≥ 5 Ω | -4 | - | 4 | LSB |
| INL | Integral non linearity (2) | DAC output buffer OFF, CL ≤ 50 pF, no RL | -4 | - | 4 | LSB |
| Offset | Offset error at code 0x800 (2) | DAC output buffer ON, CL ≤ 50 pF, RL ≥ 5 Ω; VREF+ = 3.6 V | - | - | ±12 | LSB |
| Offset | Offset error at code 0x800 (2) | DAC output buffer OFF, CL ≤ 50 pF, no RL | - | - | ±8 | LSB |
| Offset1 | Offset error at code 0x001 (3) | DAC output buffer OFF, CL ≤ 50 pF, no RL | - | - | ±5 | LSB |
| OffsetCal | Offset error at code 0x800 after factory calibration | DAC output buffer ON, CL ≤ 50 pF, RL ≥ 5 Ω; VREF+ = 3.6 V | - | - | ±5 | LSB |
| Gain | Gain error (4) | DAC output buffer ON, CL ≤ 50 pF, RL ≥ 5 Ω | - | - | ±1 | % |
| Gain | Gain error (4) | DAC output buffer OFF, CL ≤ 50 pF, no RL | - | - | ±1 | % |
| TUE | Total unadjusted error | DAC output buffer ON CL ≤ 50 pF, RL ≥ 5 kΩ | - | - | ±30 | LSB |
| TUE | Total unadjusted error | DAC output buffer OFF CL ≤ 50 pF, no RL | - | - | ±12 | LSB |
| TUECal | Total unadjusted error after calibration | DAC output buffer ON CL ≤ 50 pF, RL >= 5 kΩ | - | - | ±23 | LSB |
| SNR | Signal-to-noise ratio (5) | DAC output buffer ON CL ≤ 50 pF, RL ≥ 5 kΩ, 1 kHz, BW 500 KHz | - | 67.8 | - | dB |
| SNR | Signal-to-noise ratio (5) | DAC output buffer OFF CL ≤ 50 pF, no RL, 1 kHz, BW 500 KHz | - | 67.8 | - | dB |
| THD | Total harmonic distortion (5) | DAC output buffer ON CL ≤ 50 pF, RL ≥ 5 kΩ, 1 kHz | - | -78,6 | - | dB |
| THD | Total harmonic distortion (5) | DAC output buffer OFF CL ≤ 50 pF, no RL, 1 kHz | - | -78,6 | - | dB |
| SINAD | Signal-to-noise and distortion ratio (5) | DAC output buffer ON CL ≤ 50 pF, RL ≥ 5 kΩ, 1 kHz | - | 67.5 | - | dB |
| SINAD | Signal-to-noise and distortion ratio (5) | DAC output buffer OFF CL ≤ 50 pF, no RL, 1 kHz | - | 67.5 | - | dB |
| ENOB | Effective number of bits | DAC output buffer ON CL ≤ 50 pF, RL ≥ 5 kΩ, 1 kHz | - | 10.9 | - | bits |
| ENOB | Effective number of bits | DAC output buffer OFF CL ≤ 50 pF, no RL, 1 kHz | - | 10.9 | - | bits |

Notes:

1. Difference between two consecutive codes minus 1 LSB.
2. Difference between the value measured at Code i and the value measured at Code i on a line drawn between Code 0 and last Code 4095.
3. Difference between the value measured at Code (0x001) and the ideal value.
4. Difference between the ideal slope of the transfer function and the measured slope computed from code 0x000 and 0xFFF when the buffer is OFF, and from code giving 0.2 V and (VREF+ - 0.2 V) when the buffer is ON.
5. The signal is -0.5 dBFS with Fsampling=1 MHz.

*Digest note:* The THD value is printed "-78,6" (comma decimal separator) in the source, which means -78.6 dB.

#### 5.3.20 Comparator characteristics

**Table 59. COMP characteristics**

The input capacitance is negligible compared to the I/O capacitance.

Specified by design - not tested in production, unless otherwise stated.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| VDDA | Analog supply voltage | - | 2.70 | - | 3.60 | V |
| VIN | Comparator input voltage range | - | 0 | - | VDDA | V |
| VBG | Scaler input voltage | - | (1) | (1) | (1) | V |
| VSC | Scaler offset voltage | - | - | ±5 | ±10 | mV |
| IDDA(SCALER) | Scaler static consumption from VDDA | BRG_EN=0 (bridge disable) | - | 0.2 | 0.3 | µA |
| IDDA(SCALER) | Scaler static consumption from VDDA | BRG_EN=1 (bridge enable) | - | 0.82 | 1 | µA |
| tSTART_SCALER | Scaler startup time | - | - | 140 | 250 | µs |
| tSTART | Comparator startup time to reach propagation delay specification | High-speed mode | - | 2 | 5 | µs |
| tSTART | Comparator startup time to reach propagation delay specification | Medium mode | - | 5 | 20 | µs |
| tD (2) | Propagation delay for 200 mV step with 100 mV overdrive | High-speed mode | - | 50 | 80 | ns |
| tD (2) | Propagation delay for 200 mV step with 100 mV overdrive | Medium mode | - | 0.5 | 0.9 | µs |
| tD (2) | Propagation delay for step > 200 mV with 100 mV overdrive only on positive inputs | High-speed mode | - | 50 | 120 | ns |
| tD (2) | Propagation delay for step > 200 mV with 100 mV overdrive only on positive inputs | Medium mode | - | 0.5 | 1.2 | µs |
| Voffset | Comparator offset error | Full common mode range | - | - | ±20 | mV |
| Vhys | Comparator hysteresis | No hysteresis | - | 0 | - | mV |
| Vhys | Comparator hysteresis | Low hysteresis | - | 10 | - | mV |
| Vhys | Comparator hysteresis | Medium hysteresis | - | 20 | - | mV |
| Vhys | Comparator hysteresis | High hysteresis | - | 30 | - | mV |
| IDDA(COMP) | Comparator consumption from VDDA | Medium mode, Static | - | 5 | 9 | µA |
| IDDA(COMP) | Comparator consumption from VDDA | Medium mode, With 50 kHz ±100 mV overdrive square signal | - | 6 | - | µA |
| IDDA(COMP) | Comparator consumption from VDDA | High-speed mode, Static | - | 70 | 110 | µA |
| IDDA(COMP) | Comparator consumption from VDDA | High-speed mode, With 50 kHz ±100 mV overdrive square signal | - | 75 | - | µA |

Notes:

1. Refer to Section 5.3.5: Embedded voltage reference.
2. Evaluated by characterization - Not tested in production.

#### 5.3.21 Timer characteristics

The parameters given in Section 5.3.21, Table 61, and Section 5.3.21 are specified by design, not tested in production.

Refer to Table 47. I/O static characteristics for details on the input/output alternate function characteristics (output compare, input capture, external clock, PWM output).

*Digest note:* The cross-references in the first sentence are reproduced as printed. From context they cover Tables 60, 61 and 62.

**Table 60. TIMx characteristics**

| Symbol | Parameter | Conditions | Min | Max | Unit (1) |
|---|---|---|---|---|---|
| tres(TIM) | Timer resolution time | - | 1 | - | tTIMxCLK |
| tres(TIM) | Timer resolution time | fTIMxCLK = 144 MHz | 6.9 | - | ns |
| fEXT | Timer external clock frequency on CH1 to CH4 | - | 0 | fTIMxCLK/2 | MHz |
| fEXT | Timer external clock frequency on CH1 to CH4 | fTIMxCLK = 144 MHz | 0 | 72 | MHz |
| ResTIM | Timer resolution | TIMx (except TIM2/TIM5) | - | 16 | bit |
| ResTIM | Timer resolution | TIM2/TIM5 | - | 32 | bit |
| tCOUNTER | 16-bit counter clock period | - | 1 | 65536 | tTIMxCLK |
| tCOUNTER | 16-bit counter clock period | fTIMxCLK = 144 MHz | 0.007 | 455.1 | µs |
| tMAX_COUNT | Maximum possible count with 32‑bit counter | - | - | 4, 294, 967, 296 | tTIMxCLK |
| tMAX_COUNT | Maximum possible count with 32‑bit counter | fTIMxCLK = 144 MHz | - | 29.826 | s |

Notes:

1. TIMx, is used as a general term in which x stands for 1, 2, 5, 6, 7, 8, 12, 15, 16, 17.

**Table 61. IWDG min/max timeout period at 32 kHz (LSI)**

Note: For the values in this table, the exact timings still depend on the phasing of the APB interface clock versus the LSI clock, so that there is always a full RC period of uncertainty.

| Prescaler divider | PR[2:0] bits | Min timeout RL[11:0] = 0x000 | Max timeout RL[11:0] = 0xFFF | Unit |
|---|---|---|---|---|
| /4 | 0 | 0.125 | 512 | ms |
| /8 | 1 | 0.250 | 1024 | ms |
| /16 | 2 | 0.500 | 2048 | ms |
| /32 | 3 | 1.0 | 4096 | ms |
| /64 | 4 | 2.0 | 8192 | ms |
| /128 | 5 | 4.0 | 16384 | ms |
| /256 | 6 or 7 | 8.0 | 32768 | ms |

**Table 62. WWDG min/max timeout value at 144 MHz (PCLK)**

| Prescaler | WDGTB | Min timeout values | Max timeout value | Unit |
|---|---|---|---|---|
| 1 | 0 | 0.0284 | 1.820 | ms |
| 2 | 1 | 0.0569 | 3.641 | ms |
| 4 | 2 | 0.1138 | 7.282 | ms |
| 8 | 3 | 0.2276 | 14.564 | ms |
| 16 | 4 | 0.4551 | 29.127 | ms |
| 32 | 5 | 0.9102 | 58.254 | ms |
| 64 | 6 | 1.820 | 116.508 | ms |
| 128 | 7 | 3.641 | 233.017 | ms |

#### 5.3.22 I3C interface characteristics

The I3C interface meets the timing requirements of the MIPI® I3C specification v1.1.

The I3C peripheral supports:

- I3C SDR-only as controller
- I3C SDR-only as target
- I3C SCL bus clock frequency up to 12.5 MHz

The parameters given in Table 63 below are obtained with the following configuration:

- Output speed is set to OSPEEDRy[1:0] = 10
- I/O Compensation cell activated
- Voltage scaling range 1

The I3C timings are in line with the MIPI specification, except for the ones given in Table 63, I3C open-drain measured timing. For tSU_OD, this can be mitigated by increasing the corresponding SCL low duration in the I3C_TIMINGR0 register. For further details refer to AN5879.

**Table 63. Open drain timing measurements**

Evaluated by characterization - Not tested in production.

| Symbol | Parameter | Conditions | Min | Unit |
|---|---|---|---|---|
| tSU_OD | SDA data setup time in open drain mode | Controller, 2.7 V ≤ VDDIOX ≤ 3.6 V | 22 (1) | ns |

Notes:

1. The minimum SDA data setup time during open-drain-mode is 3 ns, as specified in the MIPI Alliance specification for I3C.

#### 5.3.23 I²C interface characteristics

The I²C interface meets the timing requirements of the I2C-bus specification and user manual rev. 03 for:

- Standard mode (Sm): Bit rate up to 100 kbit/s.
- Fast mode (Fm): Bit rate up to 400 kbit/s.
- Fast mode plus (Fm+): Bit rate up to 1 Mbit/s.

The I²C timing requirements are specified by design, not tested in production, when the I²C peripheral is properly configured (refer to the product reference manual).

The SDA and SCL I/O requirements are met with the following restrictions:

- The SDA and SCL I/O pins are not true open-drain. When configured as open-drain, the PMOS connected between the I/O pin and VDDIOx is disabled but remains present.
- Only FT_f I/O pins support Fm+ low level output current maximum requirement. Refer to Section 5.3.14: I/O port characteristics for the I²C I/Os characteristics.

All I²C SDA and SCL I/Os embed an analog filter. Refer to the table below for the analog filter characteristics.

**Table 64. I²C analog filter characteristics**

Evaluated by characterization - Not tested in production.

Measurement points are taken at 50% VDD.

| Symbol | Parameter | Min | Max | Unit |
|---|---|---|---|---|
| tAF | Maximum pulse width of spikes that are suppressed by analog filter | 50 (1) | 160 (2) | ns |

Notes:

1. Spikes with widths below tAF(min) are filtered.
2. Spikes with widths above tAF(max) are not filtered.

#### 5.3.24 USART characteristics

Unless otherwise specified, the parameters given in Table 65 are derived from tests performed under the ambient temperature, fPCLKx frequency and VDD supply voltage conditions summarized in [unclear in source: the cross-reference is printed as "not found"; other sections in this chapter refer to Table 17], with the following configuration:

- Output speed set to OSPEEDRy[1:0] = 10
- Capacitive load CL = 30 pF
- Measurement points done at 0.5 × VDD level
- I/O compensation cell activated

Refer to I/O port characteristics for more details on the input/output alternate function characteristics (NSS, CK, TX, RX for USART).

**Table 65. USART (SPI mode) characteristics**

Evaluated by characterization - Not tested in production.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| fCK | USART clock frequency | Master transmitter mode, 2.7 V ≤ VDD ≤ 3.6 V | - | - | 18 | [unclear in source: unit cell blank; MHz implied] |
| fCK | USART clock frequency | Slave receiver mode, 2.7 V ≤ VDD ≤ 3.6 V | - | - | 48 | [unclear in source: unit cell blank; MHz implied] |
| fCK | USART clock frequency | Slave transmitter mode, 2.7 V ≤ VDD ≤ 3.6 V | - | - | 27 | [unclear in source: unit cell blank; MHz implied] |
| tsu(NSS) | NSS setup time | Slave mode | tker (1) + 2 | - | - | ns |
| th(NSS) | NSS hold time | Slave mode | 2 | - | - | ns |
| tw(CKH), tw(CKL) | CK high and low time | Master mode | 1/fCK/2-1 | 1/fCK/2 | 1/fCK/2+1 | ns |
| tsu(RX) | Data input setup time | Master mode | 18 | - | - | ns |
| tsu(RX) | Data input setup time | Slave mode | 2.5 | - | - | ns |
| th(RX) | Data input hold time | Master mode | 0.5 | - | - | ns |
| th(RX) | Data input hold time | Slave mode | 1 | - | - | ns |
| tv(TX) | Data output valid time | Slave mode, 2.7 V ≤ VDD ≤ 3.6 V | - | 13.5 | 18 | ns |
| tv(TX) | Data output valid time | Master mode, 2.7 V ≤ VDD ≤ 3.6 V | - | 2 | 2.5 | ns |
| th(TX) | Data output hold time | Slave mode | 9 | - | - | ns |
| th(TX) | Data output hold time | Master mode | 0.5 | - | - | ns |

Notes:

1. Tker is the usart_ker_ck_pres clock period.

**Figure 30. USART timing diagram in SPI master mode**

The device drives the CK output. The figure shows four CK waveforms: CPHA=0/CPOL=0, CPHA=0/CPOL=1, CPHA=1/CPOL=0 and CPHA=1/CPOL=1. In the CPHA=1 waveforms the clock edges are shifted half a period earlier than in the CPHA=0 waveforms. RX input carries MSB IN, BIT6 IN, …, LSB IN, and TX output carries MSB OUT, BIT1 OUT, …, LSB OUT.

- 1/fCK is the CK period, measured from one leading edge to the next.
- tw(CKH) is the CK high time and tw(CKL) is the CK low time.
- tsu(RX) is how long RX data must be stable before the CK sampling edge.
- th(RX) is how long RX data must stay stable after that sampling edge.
- tv(TX) is the delay from the CK edge that launches data to valid new data on TX.
- th(TX) is how long the previous TX data stays valid after that launch edge.

**Figure 31. USART timing diagram in SPI slave mode**

NSS input goes low to start the transfer and high at the end. CK is an input and is shown for CPHA=0 with CPOL=0 and CPOL=1. TX output carries First bit OUT, Next bits OUT and Last bit OUT. RX input carries First bit IN, Next bits IN and Last bit IN.

- tsu(NSS) is measured from the NSS falling edge to the first CK edge.
- th(NSS) is measured from the last CK edge to the NSS rising edge.
- 1/fCK is the CK period.
- tw(CKH) and tw(CKL) are the CK high and low times.
- tv(TX) is measured from a CK edge (the trailing edge of the first clock pulse in the drawing) to the next TX bit becoming valid.
- th(TX) is how long the previous TX bit stays valid after the CK edge.
- tsu(RX) is the RX setup time before the CK sampling edge (the first edge).
- th(RX) is the RX hold time after that sampling edge.

#### 5.3.25 SPI characteristics

Unless otherwise specified, the parameters given in Table 66 are derived from tests performed under the ambient temperature, fPCLKx frequency and supply voltage conditions summarized in Table 17.

- Output speed set to OSPEEDRy[1:0] = 11
- Capacitive load CL = 30 pF
- Measurement points done at 0.5 × VDD level
- I/O compensation cell activated

Refer to Table 47. I/O static characteristics for more details on the input/output alternate function characteristics (NSS, SCK, MOSI, MISO for SPI).

**Table 66. SPI characteristics**

Evaluated by characterization - Not tested in production.

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| fSCK | SPI clock frequency | Master mode | - | - | 72 | MHz |
| fSCK | SPI clock frequency | Slave receiver mode | - | - | 100 | MHz |
| fSCK | SPI clock frequency | Slave mode transmitter/full duplex | - | - | 32 | MHz |
| tsu(NSS) | NSS setup time | Slave mode | 3 | - | - | ns |
| th(NSS) | NSS hold time | Slave mode | 1 | - | - | ns |
| tw(SCKH), tw(SCKL) | SCK high and low time | Master mode | TPLCK - 1 | TPLCK | TPLCK + 1 | ns |
| tsu(MI) | Data input setup time | Master mode, DDRS = 0 | 2.5 | (blank) | (blank) | ns |
| tsu(MI) | Data input setup time | Master mode, DDRS = 1 | 10-TSCK/2 | - | - | ns |
| tsu(SI) | Data input setup time | Slave mode | 2 | - | - | ns |
| th(MI) | Data input hold time | Master mode, DDRS = 0 | 1 | - | - | ns |
| th(MI) | Data input hold time | Master mode, DDRS = 1 | (TSCK/2)-7 | - | - | ns |
| th(SI) | Data input hold time | Slave mode | 1.5 | - | - | ns |
| ta(SO) | Data output access time | Slave mode | 12 | 13.5 | 15.5 | ns |
| tdis(SO) | Data output disable time | Slave mode | 6.5 | 8.5 | 10.5 | ns |
| tv(SO) | Data output valid time | Slave mode | - | 12 | 15.5 | ns |
| tv(SO) | Data output valid time | Master mode | - | 2 | 2.5 | ns |
| th(SO) | Data output hold time | Slave mode | 8 | - | - | ns |
| th(MO) | Data output hold time | Master mode | 0 | - | - | ns |

*Digest note:* TPLCK is printed as such in the source. TSCK is the SCK period. The master-mode tv(SO) row matches the parameter labeled tv(MO) in Figure 34.

**Figure 32. SPI timing diagram - slave mode and CPHA = 0**

NSS input goes low to start the transfer and returns high at the end. SCK is an input and is shown for CPHA=0 with CPOL=0 and CPOL=1. With CPHA=0, MOSI is sampled on the first (leading) SCK edge of each bit, and MISO is updated on the second (trailing) edge.

- tsu(NSS) is measured from the NSS falling edge to the first SCK edge.
- tc(SCK) is the SCK period, measured from one leading edge to the next.
- tw(SCKH) and tw(SCKL) are the SCK high and low times.
- th(NSS) is measured from the last SCK edge to the NSS rising edge.
- ta(SO) is the data output access time: from the NSS falling edge until MISO leaves high impedance and drives the first bit.
- tv(SO) is measured from the trailing SCK edge to the next MISO bit becoming valid.
- th(SO) is how long the previous MISO bit is held after that SCK edge.
- tdis(SO) is the data output disable time: from the NSS rising edge until MISO returns to high impedance.
- tsu(SI) is the MOSI setup time before the sampling (leading) SCK edge.
- th(SI) is the MOSI hold time after that sampling edge.

The MISO sequence is First bit OUT, Next bits OUT, Last bit OUT. The MOSI sequence is First bit IN, Next bits IN, Last bit IN.

**Figure 33. SPI timing diagram - slave mode and CPHA = 1**

This diagram has the same signals as Figure 32 but uses CPHA=1, shown with CPOL=0 and CPOL=1. With CPHA=1, MISO is updated on the first (leading) SCK edge of each bit, and MOSI is sampled on the second (trailing) edge.

- tsu(NSS) is measured from the NSS falling edge to the first SCK edge.
- tc(SCK), tw(SCKH) and tw(SCKL) are the SCK period, high time and low time.
- th(NSS) is measured from the last SCK edge to the NSS rising edge.
- ta(SO) is measured from the NSS falling edge until MISO is driven.
- tv(SO) is measured from a leading SCK edge to the new MISO bit becoming valid.
- th(SO) is how long the previous MISO bit is held after a leading SCK edge.
- tdis(SO) is measured from the NSS rising edge until MISO returns to high impedance.
- tsu(SI) and th(SI) are the MOSI setup and hold times around the trailing (sampling) SCK edge.

Note: Measurement points are done at 0.3 VDD and 0.7 VDD levels.

**Figure 34. SPI timing diagram - master mode**

NSS input is held High. SCK is an output and is shown for all four modes: CPHA=0/CPOL=0, CPHA=0/CPOL=1, CPHA=1/CPOL=0 and CPHA=1/CPOL=1. MISO input carries First bit IN, Next bits IN and Last bit IN. MOSI output carries First bit OUT, Next bits OUT and Last bit OUT.

- tc(SCK) is the SCK period. tw(SCKH) and tw(SCKL) are the SCK high and low times.
- tsu(MI) is the MISO setup time before the SCK sampling edge. The sampling edge is the first edge of the bit for CPHA=0 and the second edge for CPHA=1.
- th(MI) is the MISO hold time after that sampling edge.
- tv(MO) is measured from the SCK edge that launches data to the new MOSI bit becoming valid.
- th(MO) is how long the previous MOSI bit stays valid after that edge.

Note: Measurement points are done at 0.3 VDD and 0.7 VDD levels.

#### 5.3.26 I2S interface characteristics

Unless otherwise specified, the parameters given in Table xx for I2S are derived from tests performed under the ambient temperature, fPCLKx frequency and VDD supply voltage conditions summarized in Table 67. I2S characteristics, with the following configuration:

- Output speed is set to OSPEEDRy[1:0] = 10
- Capacitive load C = 30 pF
- Measurement points are done at CMOS levels: 0.5 × VDD
- IO Compensation cell activated

Refer to Section 5.3.14: I/O port characteristics for more details on the input/output alternate function characteristics (CK, SDO, SDI, WS).

*Digest note:* The cross-references "Table xx" and "Table 67" in the first sentence are reproduced as printed. From context, the I2S parameters are in Table 67 and the general operating conditions are in Table 17.

**Table 67. I2S characteristics**

Evaluated by characterization – Not tested in production.

| Symbol | Parameter | Conditions | Min | Max | Unit |
|---|---|---|---|---|---|
| fMCK | I2S main clock output | - | - | 50 | MHz |
| fCK | I2S clock frequency | Master Tx or RX, slave Rx | - | 50 | MHz |
| fCK | I2S clock frequency | Slave Tx | - | 19 | MHz |
| tv(WS) | WS valid time | Master mode | - | 3 | ns |
| th(WS) | WS hold time | Master mode | 1 | - | ns |
| tsu(WS) | WS setup time | Slave mode | 2 | - | ns |
| th(WS) | WS hold time | Slave mode | 0.5 | - | ns |
| tsu(SD_MR) | Data input setup time | Master receiver | 2.5 | - | ns |
| tsu(SD_SR) | Data input setup time | Slave receiver | 1 | - | ns |
| th(SD_MR) | Data input hold time | Master receiver | 1.5 | - | ns |
| th(SD_SR) | Data input hold time | Slave receiver | 2.5 | - | ns |
| tv(SD_ST) | Data output valid time | Slave transmitter (after enable edge) | - | 15.5 | ns |
| th(SD_ST) | Data output hold time | Slave transmitter (after enable edge) | 8 | - | ns |
| tv(SD_MT) | Data output valid time | Master transmitter (after enable edge) | - | 2 | ns |
| th(SD_MT) | Data output hold time | Master transmitter (after enable edge) | 0.5 | - | ns |

#### 5.3.27 USB_FS characteristics

**Table 68. USB_FS characteristics**

| Symbol | Parameter | Conditions | Min | Typ | Max | Unit |
|---|---|---|---|---|---|---|
| VDDUSB | USB transceiver operating supply voltage | - | 3.0 (1) | - | 3.6 | V |
| RPUI | Embedded USB_DP pullup value during idle | - | 900 | - | 1575 | Ω |
| RPUR | Embedded USB_DP pullup value during reception | - | 1425 | - | 3090 | Ω |
| ZDRV | Output driver impedance (2) | High and low driver | 28 | 36 | 44 | Ω |

Notes:

1. USB functionality is ensured down to 2.7 V, but some USB electrical characteristics are degraded in 2.7 to 3.0 V range.
2. No external termination series resistors are required on USB_DP (D+) and USB_DM (D-). The matching impedance is already included in the embedded driver.

#### 5.3.28 JTAG/SWD interface characteristics

Unless otherwise specified, the parameters given in Table 69 and Table 70 are derived from tests performed under the ambient temperature, fHCLKx frequency and VDD supply voltage conditions summarized in Table 17, with the following configuration:

- Output speed set to OSPEEDRy[1:0] = 10
- Capacitive load CL = 30 pF
- Measurement points done at 0.5 × VDD level

Refer to Table 47. I/O static characteristics for more details on the input/output characteristics.

**Table 69. JTAG characteristics**

Evaluated by characterization - Not tested in production.

| Symbol | Parameter | Min | Typ | Max | Unit |
|---|---|---|---|---|---|
| FTCK | TCK clock frequency | - | - | 34 | MHz |
| tisu(TMS) | TMS input setup time | 2 | - | - | ns |
| tih(TMS) | TMS input hold time | 0.5 | - | - | ns |
| tisu(TDI) | TDI input setup time | 1.5 | - | - | ns |
| tih(TDI) | TDI input hold time | 0.5 | - | - | ns |
| tov(TDO) | TDO output valid time | - | 11 | 14.5 | ns |
| toh(TDO) | TDO output hold time | 7.5 | - | - | ns |

**Figure 35. JTAG timing diagram**

*Digest note:* The source places the SPI slave-mode CPHA=0 drawing here: the same artwork as Figure 32, with drawing code DT40458V2. Its signals are NSS input, SCK input (CPHA=0, CPOL=0/1), MISO output and MOSI input. Its parameters are tsu(NSS), tc(SCK), tw(SCKH), tw(SCKL), th(NSS), ta(SO), tv(SO), th(SO), tdis(SO), tsu(SI) and th(SI). It does not show TCK, TMS, TDI or TDO.

*Digest note:* The source therefore gives no edge definitions for the Table 69 symbols. From the parameter names, tisu and tih are input setup and hold times of TMS/TDI relative to the TCK sampling edge, and tov and toh are the TDO output valid and hold times relative to the TCK edge that drives TDO.

**Table 70. SWD characteristics**

Evaluated by characterization - Not tested in production.

| Symbol | Parameter | Min | Typ | Max | Unit |
|---|---|---|---|---|---|
| FSWCLK | SWCLK clock frequency | - | - | 71 | MHz |
| tisu(SWDIO) | SWDIO input setup time | 3 | - | - | ns |
| tih(SWDIO) | SWDIO input hold time | 0.5 | - | - | ns |
| tov(SWDIO) | SWDIO output valid time | - | 11.5 | 14 | ns |
| toh(SWDIO) | SWDIO output hold time | 9.5 | - | - | ns |

**Figure 36. SWD timing diagram**

*Digest note:* The source places the SPI slave-mode CPHA=1 drawing here: the same artwork as Figure 33, with drawing code DT40459V2. Its signals are NSS input, SCK input (CPHA=1, CPOL=0/1), MISO output and MOSI input. It does not show SWCLK or SWDIO.

*Digest note:* The source therefore gives no edge definitions for the Table 70 symbols. From the parameter names, tisu(SWDIO) and tih(SWDIO) are SWDIO input setup and hold times relative to the SWCLK sampling edge, and tov(SWDIO) and toh(SWDIO) are the SWDIO output valid and hold times relative to the SWCLK edge that drives SWDIO.

## 6 Package information

To meet environmental requirements, ST offers these devices in different grades of ECOPACK packages, depending on their level of environmental compliance. ECOPACK specifications, grade definitions and product status are available at: www.st.com. ECOPACK is an ST trademark.

Table conventions used in this chapter: in the mechanical data tables, a value shown only in the Typ column (with `-` in Min and Max) is a single value that spans the Min/Typ/Max columns in the original table (BSC dimensions, REF dimensions, tolerance values aaa–fff, and the terminal count N). Values are reproduced exactly as printed, including apparent typos, which are flagged with an digest note.

### 6.1 Device marking

Refer to technical note "Reference device marking schematics for STM32 microcontrollers and microprocessors" (TN1433) available on www.st.com, for the location of pin 1 / ball A1 as well as the location and orientation of the marking areas versus pin 1 / ball A1.

Parts marked as "ES", "E" or accompanied by an engineering sample notification letter, are not yet qualified and therefore not approved for use in production. ST is not responsible for any consequences resulting from such use. In no event will ST be liable for the customer using any of these engineering samples in production. ST's Quality department must be contacted prior to any decision to use these engineering samples to run a qualification activity.

A WLCSP simplified marking example (if any) is provided in the corresponding package information subsection. (This datasheet contains no WLCSP package and no per-package marking examples; marking field layout is defined only by reference to TN1433.)

### 6.2 LQFP32 package information (5V)

This LQFP is a 32-pin, 7 x 7 mm, low-profile quad flat package.

Note: Figure 37 is not to scale. Refer to the notes section for the list of notes on Figure 37 and Table 71.

**Figure 37. LQFP32- Outline**

The outline drawing (reference 5V_LQFP32_ME_V1) shows a square gull-wing quad flat package with 8 leads per side (N = 32), lead pitch e = 0.80 mm. It contains five views:

- Bottom view: the plastic body with leads on all four sides. The pin 1 identifier zone (note 6) is the corner quadrant bounded by D 1/4 and E 1/4. A profile tolerance `aaa C A-B D` applies to the 4x N/4 lead tips, and a profile tolerance `bbb H A-B D` applies 4x (body sides at datum plane H).
- Side view: overall height A, body thickness A2, standoff A1 (note 12), lead width b, and the lead span labeled (N – 4)x e (note 13). Tolerances shown: flatness 0.05 on the body, lead position `ddd (M) C A-B D`, and lead coplanarity `ccc C` relative to seating plane C.
- Top view: lead-tip-to-lead-tip dimensions D and E (note 4) and body dimensions D1 and E1 (notes 2, 5). Datums A and B (note 3) are on the left and right body edges, datum D (note 3) on the top edge. Pins 1, 2, 3 are at the top of the left side, counting counter-clockwise; the pin 1 identifier zone (note 6) is the D 1/4 × E 1/4 corner region; corner shape is optional (note 10). Section A-A is cut through a lead.
- Section A-A (lead form): the lead exits the body at datum plane H, with body draft angles θ2 (top) and θ3 (bottom), upper bend radius R1 and lower bend radius R2, flat shoulder length S, foot length L measured from the gauge plane (0.25 mm above the seating plane), lead length (L1) (notes 1, 11), and foot angle θ from the seating plane; θ1 is the lead angle at the body exit (note 2).
- Section B-B (lead cross-section): b and c are the lead width and thickness including plating (notes 9, 11); b1 and c1 are the base-metal width and thickness (note 11).

**Table 71. LQFP32 - Mechanical data**

| Symbol | Millimeters Min | Millimeters Typ | Millimeters Max | Inches (14) Min | Inches (14) Typ | Inches (14) Max |
|---|---|---|---|---|---|---|
| θ | 0° | 3.5° | 7° | 0° | 3.5° | 7° |
| θ1 | 0° | - | - | 0° | - | - |
| θ2 | 10° | 12° | 14° | 10° | 12° | 14° |
| θ3 | 10° | 12° | 14° | 10° | 12° | 14° |
| A | - | - | 1.60 | - | - | 0.0630 |
| A1 (12) | 0.05 | - | 0.15 | 0.0020 | - | 0.0059 |
| A2 | 1.35 | 1.40 | 1.45 | 0.0531 | 0.0551 | 0.0571 |
| b (9)(11) | 0.30 | 0.37 | 0.45 | 0.0118 | 0.0146 | 0.0177 |
| b1 (11) | 0.30 | 0.35 | 0.40 | 0.0118 | 0.0128 | 0.0157 |
| c (11) | 0.09 | - | 0.20 | 0.0035 | - | 0.0079 |
| c1 (11) | 0.09 | - | 0.16 | 0.0035 | - | 0.0063 |
| D (4) | - | 9.00 BSC | - | - | 0.3543 BSC | - |
| D1 (2)(5) | - | 7.00 BSC | - | - | 0.2756 BSC | - |
| e | - | 0.80 BSC | - | - | 0.0315 BSC | - |
| E (4) | - | 9.00 BSC | - | - | 0.3543 BSC | - |
| E1 (2)(5) | - | 7.00 BSC | - | - | 0.2756 BSC | - |
| L | 0.45 | 0.60 | 0.75 | 0.0177 | 0.0236 | 0.0295 |
| L1 | - | 1.00 REF | - | - | 0.0394 REF | - |
| N (13) | - | 32 | - | - | 32 | - |
| R1 | 0.08 | - | - | 0.0031 | - | - |
| R2 | 0.08 | - | 0.20 | 0.0031 | - | 0.0079 |
| S | 0.20 | - | - | 0.0079 | - | - |
| aaa (1)(7)(15) | - | 0.20 | - | - | 0.0079 | - |
| bbb (1)(7)(15) | - | 0.20 | - | - | 0.0079 | - |
| ccc (1)(7)(15) | - | 0.10 | - | - | 0.0039 | - |
| ddd (1)(7)(15) | - | 0.20 | - | - | 0.0079 | - |

*Digest note:* the b1 Typ inch value 0.0128 is as printed; 0.35 mm converts to 0.0138 in.

Notes:

1. Dimensioning and tolerancing schemes conform to ASME Y14.5M-1994.
2. The top package body size may be smaller than the bottom package size by as much as 0.15 mm.
3. Datums A-B and D to be determined at datum plane H.
4. To be determined at the seating datum plane C.
5. Dimensions D1 and E1 do not include mold flash or protrusions. Allowable mold flash or protrusions is "0.25 mm" per side. D1 and E1 are maximum plastic body size dimensions including mold mismatch.
6. Details of pin 1 identifier are optional but must be located within the zone indicated.
7. All dimensions are in millimeters.
8. No intrusion is allowed inwards the leads.
9. Dimension b does not include a dambar protrusion. Allowable dambar protrusion shall not cause the lead width to exceed the maximum "b" dimension by more than 0.08 mm. Dambar cannot be located on the lower radius or the foot. The minimum space between the protrusion and an adjacent lead is 0.07 mm for 0.4 mm and 0.5 mm pitch packages.
10. The exact shape of each corner is optional.
11. These dimensions apply to the flat section of the lead between 0.10 mm and 0.25 mm from the lead tip.
12. A1 is defined as the distance from the seating plane to the lowest point on the package body.
13. N is the number of terminal positions for the specified body size.
14. Values in inches are converted from mm and rounded to four decimal digits.
15. Recommended values and tolerances.

**Figure 38. LQFP32 - Footprint example**

Recommended PCB land pattern (reference 5V_LQFP32_FP_V4). Dimensions are expressed in millimeters.

| Dimension | Value (mm) |
|---|---|
| Pad pitch | 0.8 |
| Pad width | 0.45 |
| Pad length | 1.2 REF |
| Distance between inner edges of opposite pad rows (both X and Y) | 7.4 |
| Distance between outer edges of opposite pad rows (both X and Y) | 9.8 |

Pin numbering on the footprint: pins 1–8 run top to bottom on the left side, pins 9–16 left to right on the bottom side, pins 17–24 bottom to top on the right side, and pins 25–32 right to left on the top side (pin 32 at the top-left, pin 25 at the top-right). The drawing distinguishes the soldering area (copper pad) from the solder resist opening, which surrounds each row of pads.

### 6.3 UFQFPN32 package information (A0B8)

This UFQFPN is a 32-pin, 5 x 5 mm, 0.5 mm pitch ultra-thin fine pitch quad flat package.

**Figure 39. UFQFPN32 - Outline**

The outline drawing (reference A0B8_UFQFPN32_ME_V4) shows a leadless package with 8 terminals per side (N = 32) and a square exposed die pad on the underside. Views:

- Bottom view: exposed pad of size D2 × E2 with positional tolerance `fff (M) C A B` in both axes; terminals of width b, length L and pitch e, with terminal position tolerances `bbb (M) C A B` and `ddd (M) C`. Terminals 1 and 2 are at the bottom of the left side and terminal 32 is at the left of the bottom side (bottom view). The pin 1 identifier is a chamfer or circular-arc shape (R0.20) on the corner of the exposed pad nearest pin 1.
- Front view: package height A with parallelism `ccc C` and coplanarity `eee C` to seating plane C; Detail A shows terminal thickness A3 and standoff A1, with `ddd C` relative to the seating plane.
- Top view: body D × E with datum A on the bottom edge and datum B on the right edge; the pin 1 identifier laser marking area is in the top-left corner.

1. Drawing is not to scale.
2. All leads/pads should also be soldered to the PCB to improve the lead/pad solder joint life.
3. There is an exposed die pad on the underside of the UFQFPN package. It is recommended to connect and solder this backside pad to PCB ground.

**Table 72. UFQFPN32 - Mechanical data**

| Symbol | Millimeters (1) Min | Millimeters (1) Typ | Millimeters (1) Max | Inches (2) Min | Inches (2) Typ | Inches (2) Max |
|---|---|---|---|---|---|---|
| A (3)(4) | 0.50 | 0.55 | 0.60 | 0.0197 | 0.0217 | 0.0236 |
| A1 (5) | 0.00 | - | 0.05 | 0.000 | - | 0.0020 |
| A3 (6) | - | 0.15 | - | - | 0.0060 | - |
| b (7) | 0.18 | 0.25 | 0.30 | 0.0071 | 0.010 | 0.0118 |
| D (8)(9) | - | 5.00 BSC | - | - | 0.1969 BSC | - |
| D2 | 3.50 | 3.60 | 3.70 | 0.139 | 0.143 | 0.147 |
| E (8)(9) | - | 5.00 BSC | - | - | 0.1969 BSC | - |
| E2 | 3.50 | 3.60 | 3.70 | 0.139 | 0.143 | 0.147 |
| e (9) | - | 0.50 | - | - | 0.02 | - |
| N (10) | - | 32 | - | - | 32 | - |
| K | 0.15 | - | - | 0.006 | - | - |
| L | 0.30 | - | 0.50 | 0.0119 | - | 0.0199 |
| R | 0.09 | - | - | 0.004 | - | - |

Notes:

1. All dimensions are in millimeters. Dimensioning and tolerancing schemes are conform to ASME Y14.5M-2018 except European .
2. Values in inches are converted from mm and rounded to 4 decimal digits.
3. UFQFPN stands for Ultra thin Fine pitch Quad Flat Package No lead: A ≤ 0.60mm / Fine pitch e ≤ 1.00mm.
4. The profile height, A, is the distance from the seating plane to the highest point on the package. It is measured perpendicular to the seating plane.
5. A1 is the vertical distance from the bottom surface of the plastic body to the nearest metallized package feature.
6. A3 is the distance from the seating plane to the upper surface of the terminals.
7. Dimension b applies to metallized terminal. If the terminal has the optional radius on the other end of the terminal, the dimension b must not be measured in that radius area.
8. Dimensions D and E do not include mold protrusion, not to exceed 0,15mm.
9. BSC stands for BASIC dimensions. It corresponds to the nominal value and has no tolerance. For tolerances refer to Table 73
10. N represents the total number of terminals.

**Table 73. Tolerance of form and position**

| Symbol (1) | Tolerance of form and position (2), in millimeters | Tolerance of form and position (3), in inches |
|---|---|---|
| aaa | 0.15 | 0.006 |
| bbb | 0.10 | 0.004 |
| ccc | 0.10 | 0.004 |
| ddd | 0.05 | 0.002 |
| eee | 0.10 | 0.004 |
| fff | 0.10 | 0.004 |

Notes:

1. For the tolerance of form and position definitions see Table 74.
2. All dimensions are in millimetres. Dimensioning and tolerancing schemes are conform to ASME Y14.5M-2018 except European .
3. Values in inches are converted from mm and rounded to 4 decimal digits.

**Table 74. Tolerance of form and position symbol definition**

| Symbol | Definition |
|---|---|
| aaa | The bilateral profile tolerance that controls the position of the plastic body sides. The centres of the profile zones are defined by the basic dimensions D and E. |
| bbb | The tolerance that controls the position of the terminals with respect to Datums A and B. The centre of the tolerance zone for each terminal is defined by basic dimension e as related to datums A and B. |
| ccc | The tolerance located parallel to the seating plane in which the top surface of the package must be located. |
| ddd | The tolerance that controls the position of the terminals to each other. The centres of the profile zones are defined by basic dimension e. |
| eee | The unilateral tolerance located above the seating plane wherein the bottom surface of all terminals must be located = coplanarity |
| fff | The tolerance that controls the position of the exposed metal heat feature. The centre of the tolerance zone is the data defined by the centrelines of the package body |

**Figure 40. UFQFPN32 - Footprint example**

Recommended PCB land pattern (reference A0B8_UFQFPN32_FP_V1). Dimensions are expressed in millimeters.

| Dimension | Value (mm) |
|---|---|
| Pad pitch | 0.50 |
| Pad width | 0.25 |
| Pad length | 0.65 |
| Span of one pad row, first pad outer edge to last pad outer edge (each side) | 3.75 |
| Distance between outer edges of opposite pad rows (both X and Y) | 5.50 |
| Central exposed-pad land (X × Y) | 3.60 × 3.60 |

Pin numbering on the footprint: pins 1–8 run top to bottom on the left side, pins 9–16 left to right on the bottom side, pins 17–24 bottom to top on the right side, and pins 25–32 right to left on the top side. Pad 1 has a chamfered corner as the pin 1 marker.

### 6.4 LQFP48 package information (5B)

This LQFP is a 48-pins, 7 x 7 mm, low-profile quad flat package.

Note: See list of notes in the notes section.

**Figure 41. LQFP48- Outline (15)**

The outline drawing (package LQFP48, package code 5B) has the same structure as Figure 37 (LQFP32): bottom view with `aaa C A-B D` on the 4x N/4 tips, `bbb H A-B D` 4x, and the pin 1 identifier zone bounded by D 1/4 and E 1/4 (note 6); side view with A, A2, A1 (note 12), b, (N – 4)x e (note 13), flatness 0.05, `ddd (M) C A-B D` and coplanarity `ccc C`; top view with D, E (note 4), D1, E1 (notes 2, 5), datums A and B (left and right body edges, note 3) and D (top edge, note 3), pins 1, 2, 3 at the top of the left side, pin N at the left end of the top side, corner shape optional (note 10); Section A-A lead form with θ, θ1, θ2, θ3, R1, R2, S, L, (L1) (notes 1, 11), datum plane H and the 0.25 mm gauge plane; Section B-B with b, c (with plating, notes 9, 11) and b1, c1 (base metal, note 11). The package has 12 leads per side, pitch e = 0.50 mm.

**Table 75. LQFP48 - Mechanical data**

| Symbol | Millimeters Min | Millimeters Typ | Millimeters Max | Inches (14) Min | Inches (14) Typ | Inches (14) Max |
|---|---|---|---|---|---|---|
| A | - | - | 1.60 | - | - | 0.0630 |
| A1 (12) | 0.05 | - | 0.15 | 0.0020 | - | 0.0059 |
| A2 | 1.35 | 1.40 | 1.45 | 0.0531 | 0.0551 | 0.0571 |
| b (9)(11) | 0.17 | 0.22 | 0.27 | 0.0067 | 0.0087 | 0.0106 |
| b1 (11) | 0.17 | 0.20 | 0.23 | 0.0067 | 0.0079 | 0.0090 |
| c (11) | 0.09 | - | 0.20 | 0.0035 | - | 0.0079 |
| c1 (11) | 0.09 | - | 0.16 | 0.0035 | - | 0.0063 |
| D (4) | - | 9.00 BSC | - | - | 0.3543 BSC | - |
| D1 (4)(5) | - | 7.00 BSC | - | - | 0.2756 BSC | - |
| E (4) | - | 9.00 BSC | - | - | 0.3543 BSC | - |
| E1 (4)(5) | - | 7.00 BSC | - | - | 0.2756 BSC | - |
| e | - | 0.50 BSC | - | - | 0.1970 BSC | - |
| L | 0.45 | 0.60 | 0.75 | 0.0177 | 0.0236 | 0.0295 |
| L1 | - | 1.00 REF | - | - | 0.0394 REF | - |
| N (13) | - | 48 | - | - | 48 | - |
| θ | 0° | 3.5° | 7° | 0° | 3.5° | 7° |
| θ1 | 0° | - | - | 0° | - | - |
| θ2 | 10° | 12° | 14° | 10° | 12° | 14° |
| θ3 | 10° | 12° | 14° | 10° | 12° | 14° |
| R1 | 0.08 | - | - | 0.0031 | - | - |
| R2 | 0.08 | - | 0.20 | 0.0031 | - | 0.0079 |
| S | 0.20 | - | - | 0.0079 | - | - |
| aaa (1)(7) | - | 0.20 | - | - | 0.0079 | - |
| bbb (1)(7) | - | 0.20 | - | - | 0.0079 | - |
| ccc (1)(7) | - | 0.08 | - | - | 0.0031 | - |
| ddd (1)(7) | - | 0.08 | - | - | 0.0031 | - |

*Digest note:* the e inch value 0.1970 BSC is as printed; 0.50 mm converts to 0.0197 in.

Notes:

1. Dimensioning and tolerancing schemes conform to ASME Y14.5M-1994.
2. The Top package body size may be smaller than the bottom package size by as much as 0.15 mm.
3. Datums A-B and D to be determined at datum plane H.
4. To be determined at seating datum plane C.
5. Dimensions D1 and E1 do not include mold flash or protrusions. Allowable mold flash or protrusions is "0.25 mm" per side. D1 and E1 are Maximum plastic body size dimensions including mold mismatch.
6. Details of pin 1 identifier are optional but must be located within the zone indicated.
7. All Dimensions are in millimeters.
8. No intrusion allowed inwards the leads.
9. Dimension "b" does not include dambar protrusion. Allowable dambar protrusion shall not cause the lead width to exceed the maximum "b" dimension by more than 0.08 mm. Dambar cannot be located on the lower radius or the foot. Minimum space between protrusion and an adjacent lead is 0.07 mm for 0.4 mm and 0.5 mm pitch packages.
10. Exact shape of each corner is optional.
11. These dimensions apply to the flat section of the lead between 0.10 mm and 0.25 mm from the lead tip.
12. A1 is defined as the distance from the seating plane to the lowest point on the package body.
13. "N" is the number of terminal positions for the specified body size.
14. Values in inches are converted from mm and rounded to 4 decimal digits
15. Drawing is not to scale.

**Figure 42. LQFP48 - Footprint example**

Recommended PCB land pattern (reference 5B_LQFP48_FP_V1). Dimensions are expressed in millimeters.

| Dimension | Value (mm) |
|---|---|
| Pad pitch | 0.50 |
| Pad width | 0.30 |
| Gap between adjacent pads | 0.20 |
| Pad length | 1.20 |
| Span of one pad row, first pad outer edge to last pad outer edge (each side) | 5.80 |
| Distance between inner edges of opposite pad rows (both X and Y) | 7.30 |
| Distance between outer edges of opposite pad rows (both X and Y) | 9.70 |

Pin numbering on the footprint: pins 1–12 run left to right on the bottom side, pins 13–24 bottom to top on the right side, pins 25–36 right to left on the top side, and pins 37–48 top to bottom on the left side (this drawing is rotated relative to the LQFP32 footprint; pin 1 is at the left end of the bottom row).

### 6.5 UFQFPN48 package information (A0B9)

This UFQFPN is a 48-lead, 7 x 7 mm, 0.5 mm pitch, ultra thin fine pitch quad flat package.

**Figure 43. UFQFPN48 - Outline**

The outline drawing (reference DT_A0B9_UFQFPN48_ME_V5) shows a leadless package with 12 terminals per side (N = 48) and a square exposed die pad. Views:

- Bottom view: exposed pad D2 × E2 with positional tolerance `fff (M) C A B` in both axes; terminals of width b at pitch e, with tolerances `fff (M) C A B` and `ddd (M) C`; K is the clearance between the exposed pad and the terminals. Terminals 1 and 2 are at the bottom of the left side and terminal 48 at the left of the bottom side (bottom view). The terminal 1 identifier is a chamfer on the exposed-pad corner nearest terminal 1. Detail C (referenced from a circle on the left terminal row, "see FIG.2") shows the terminal end with 2 x R corner radii and terminal length L; it carries reference flags 14 and 15.
- Front view: package height A with parallelism `ccc C` and coplanarity `eee C`; A3 is the terminal thickness at the seating plane C.
- Top view: body D × E with datum A at the left edge, datum D on the top edge, datum B on the right edge, and profile tolerance `aaa C` x4. The terminal 1 index area (flag 10) is the top-left quadrant. Section A-A cut location is marked ("see FIG.2").
- Section A-A: shows standoff A1 relative to the seating plane C (flag 9).

The reference flags 9, 10, 14 and 15 appear in the drawing only; their note text is not given in this datasheet.

1. Drawing is not to scale.
2. All leads/pads should also be soldered to the PCB to improve the lead/pad solder joint life.
3. There is an exposed die pad on the under side of the UFQFPN48 package. It is recommended to connect and solder this back-side pad to PCB ground.

**Table 76. UFQFPN48 - Mechanical data**

| Symbol | Millimeters Min | Millimeters Typ | Millimeters Max | Inches (1) Min | Inches (1) Typ | Inches (1) Max |
|---|---|---|---|---|---|---|
| A | 0.50 | 0.55 | 0.60 | 0.0197 | 0.0217 | 0.0236 |
| A1 | 0.00 | - | 0.05 | 0.0000 | - | 0.0020 |
| b | 0.18 | 0.25 | 0.30 | 0.0071 | 0.0098 | 0.0118 |
| D (2) | - | 7.00 BSC | - | - | 0.2756 BSC | - |
| D2 (3) | 5.50 | 5.60 | 5.70 | 0.2165 | 0.2205 | 0.2244 |
| E (2) | - | 7.00 BSC | - | - | 0.2756 BSC | - |
| E2 (3) | 5.50 | 5.60 | 5.70 | 0.2165 | 0.2205 | 0.2244 |
| e | - | 0.50 BSC | - | - | 0.0197 BSC | - |
| N | - | 48 | - | - | 48 | - |
| L | 0.30 | - | 0.50 | 0.0118 | - | 0.0197 |
| R | 0.10 | - | - | 0.0039 | - | - |
| aaa | - | 0.15 | - | - | 0.0059 | - |
| bbb | - | 0.10 | - | - | 0.0039 | - |
| ccc | - | 0.10 | - | - | 0.0039 | - |
| ddd | - | 0.05 | - | - | 0.0020 | - |
| eee | - | 0.08 | - | - | 0.0031 | - |
| fff | - | 0.10 | - | - | 0.0039 | - |

Notes:

1. Values in inches are converted from mm and rounded to four decimal digits.
2. Dimensions D and E do not include mold protrusion, not exceed 0.15 mm.
3. Dimensions D2 and E2 are not in accordance with JEDEC.

**Figure 44. UFQFPN48 - Footprint example**

Recommended PCB land pattern (reference DT_A0B9_UFQFPN48_FP_V3). Dimensions are expressed in millimeters.

| Dimension | Value (mm) |
|---|---|
| Pad pitch | 0.50 |
| Pad width | 0.30 |
| Gap between adjacent pads | 0.20 |
| Pad length | 0.55 |
| Span of one pad row, first pad outer edge to last pad outer edge (each side) | 5.80 |
| Offset from the end of a side row to the outer edge of the perpendicular row | 0.75 |
| Distance between inner edges of opposite pad rows (both X and Y) | 6.20 |
| Distance between outer edges of opposite pad rows (both X and Y) | 7.30 |
| Central exposed-pad land (X × Y) | 5.60 × 5.60 |

Pin numbering on the footprint: pins 1–12 run top to bottom on the left side, pins 13–24 left to right on the bottom side, pins 25–36 bottom to top on the right side, and pins 37–48 right to left on the top side. Pad 1 has a chamfered corner as the pin 1 marker.

### 6.6 LQFP64 package information (5W)

This is a 64-pin, 10 x 10 mm low-profile quad flat package.

**Figure 45. LQFP64 - Outline (15)**

The outline drawing (reference 5W_LQFP64_ME_V1) has the same structure as Figure 37 (LQFP32): bottom view with `aaa C A-B D` on the 4x N/4 tips, `bbb H A-B D` 4x, and the pin 1 identifier zone bounded by D 1/4 and E 1/4 (note 6); side view with A, A2, A1 (note 12), b, (N – 4)x e (note 13), flatness 0.05, `ddd (M) C A-B D` and coplanarity `ccc C`; top view with D, E (note 4), D1, E1 (notes 5, 2), datums A and B (note 3) on the left and right body edges and D (note 3) on the top edge, pins 1, 2, 3 at the top of the left side, pin N at the left end of the top side, corner shape optional (note 10); Section A-A lead form with θ, θ1, θ2, θ3, R1, R2, S, L, (L1) (notes 1, 11), datum plane H and the 0.25 mm gauge plane; Section B-B with b, c (with plating, notes 9, 11) and b1, c1 (base metal, note 11). The package has 16 leads per side, pitch e = 0.50 mm.

No footprint example figure is provided for LQFP64 in this datasheet.

**Table 77. LQFP64 - Mechanical data**

| Symbol | Millimeters Min | Millimeters Typ | Millimeters Max | Inches (14) Min | Inches (14) Typ | Inches (14) Max |
|---|---|---|---|---|---|---|
| A | - | - | 1.60 | - | - | 0.0630 |
| A1 (12) | 0.05 | - | 0.15 | 0.0020 | - | 0.0059 |
| A2 | 1.35 | 1.40 | 1.45 | 0.0531 | 0.0551 | 0.0571 |
| b (9)(11) | 0.17 | 0.22 | 0.27 | 0.0067 | 0.0087 | 0.0106 |
| b1 (11) | 0.17 | 0.20 | 0.23 | 00067 | 0.0079 | 0.0091 |
| c (11) | 0.09 | - | 0.20 | 0.0035 | - | 0.0079 |
| c1 (11) | 0.09 | - | 0.16 | 0.0035 | - | 0.0063 |
| D (4) | - | 12.00 BSC | - | - | 0.4724 BSC | - |
| D1 (2)(5) | - | 10.00 BSC | - | - | 0.3937 BSC | - |
| E (4) | - | 12.00 BSC | - | - | 0.4724 BSC | - |
| E1 (2)(5) | - | 10.00 BSC | - | - | 0.3937 BSC | - |
| e | - | 0.50 BSC | - | - | 0.0197 BSC | - |
| L | 0.45 | 0.60 | 0.75 | 0.0177 | 0.0236 | 0.0295 |
| L1 | - | 1.00 REF | - | - | 0.0394 REF | - |
| N (13) | - | 64 | - | - | 64 | - |
| Θ | 0° | 3.5° | 7° | 0° | 3.5° | 7° |
| Θ1 | 0° | - | - | 0° | - | - |
| Θ2 | 10° | 12° | 14° | 10° | 12° | 14° |
| Θ3 | 10° | 12° | 14° | 10° | 12° | 14° |
| R1 | 0.08 | - | - | 0.0031 | - | - |
| R2 | 0.08 | - | 0.20 | 0.0031 | - | 0.0079 |
| S | 0.20 | - | - | 0.0079 | - | - |
| aaa (1) | - | 0.20 | - | - | 0.0079 | - |
| bbb (1) | - | 0.20 | - | - | 0.0079 | - |
| ccc (1) | - | 0.08 | - | - | 0.0031 | - |
| ddd (1) | - | 0.08 | - | - | 0.0031 | - |

*Digest note:* the b1 Min inch value "00067" is as printed; 0.17 mm converts to 0.0067 in.

Notes:

1. Dimensioning and tolerancing schemes conform to ASME Y14.5M-1994.
2. The top package body size may be smaller than the bottom package size by as much as 0.15 mm.
3. Datums A-B and D to be determined at datum plane H.
4. To be determined at seating datum plane C.
5. Dimensions D1and E1 do not include mold flash or protrusions. Allowable mold flash or protrusions is "0.25 mm" per side. D1 and E1 are Maximum plastic body size dimensions including mold mismatch.
6. Details of pin 1 identifier are optional but must be located within the zone indicated.
7. All dimensions are in millimeters.
8. No intrusion allowed inwards the leads.
9. Dimension "b" does not include dambar protrusion. Allowable dambar protrusion shall not cause the lead width to exceed the maximum "b" dimension by more than 0.08 mm. Dambar cannot be located on the lower radius or the foot. Minimum space between protrusion and an adjacent lead is 0.07 mm for 0.4 mm and 0.5 mm pitch packages.
10. Exact shape of each corner is optional.
11. These dimensions apply to the flat section of the lead between 0.10 mm and 0.25 mm from the lead tip.
12. A1 is defined as the distance from the seating plane to the lowest point on the package body.
13. N is the number of terminal positions for the specified body size.
14. Values in inches are converted from mm and rounded to 4 decimal digits.
15. Drawing is not to scale.

### 6.7 LQFP80 package information (9X)

This is a 80-pins, 12 x 12 mm, low-profile quad flat package.

Note: See list of notes in the notes section.

**Figure 46. LQFP80 - Outline (15)**

The outline drawing (reference 9X_LQFP80_ME_V2) has the same structure as Figure 37 (LQFP32): bottom view with `aaa C A-B D` on the 4x N/4 tips, `bbb H A-B D` 4x, and the pin 1 identifier zone bounded by D 1/4 and E 1/4 (note 6); side view with A, A2, A1 (note 12), b, (N – 4)x e (note 13), flatness 0.05, `ddd (M) C A-B D` and coplanarity `ccc C`; top view with D, E (note 4), D1, E1 (notes 2, 5), datums A and B (note 3) on the left and right body edges and D (note 3) on the top edge, pins 1, 2, 3 at the top of the left side, pin N at the left end of the top side, corner shape optional (note 10); Section A-A lead form with θ, θ1, θ2, θ3, R1, R2, S, L, (L1) (notes 1, 11), datum plane H and the 0.25 mm gauge plane; Section B-B with b, c (with plating, notes 9, 11) and b1, c1 (base metal, note 11). The package has 20 leads per side, pitch e = 0.50 mm.

**Table 78. LQFP80 - Mechanical data**

| Symbol | Millimeters Min | Millimeters Typ | Millimeters Max | Inches (14) Min | Inches (14) Typ | Inches (14) Max |
|---|---|---|---|---|---|---|
| A | - | - | 1.60 | - | - | 0.0630 |
| A1 (12) | 0.05 | - | 0.15 | 0.0020 | - | 0.0059 |
| A2 | 1.35 | 1.40 | 1.45 | 0.0531 | 0.0551 | 0.0571 |
| b (9)(11) | 0.17 | 0.22 | 0.27 | 0.0067 | 0.0087 | 0.0106 |
| b1 (11) | 0.17 | 0.20 | 0.23 | 00067 | 0.0079 | 0.0091 |
| c (11) | 0.09 | - | 0.20 | 0.0035 | - | 0.0079 |
| c1 (11) | 0.09 | - | 0.16 | 0.0035 | - | 0.0063 |
| D (4) | - | 14.00 BSC | - | - | 0.5512 BSC | - |
| D1 (2)(5) | - | 12.00 BSC | - | - | 0.4724 BSC | - |
| E (4) | - | 14.00 BSC | - | - | 0.5512 BSC | - |
| E1 (2)(5) | - | 12.00 BSC | - | - | 0.4724 BSC | - |
| e | - | 0.50 BSC | - | - | 0.0197 BSC | - |
| L | 0.45 | 0.60 | 0.75 | 0.0177 | 0.0236 | 0.0295 |
| L1 | - | 1.00 | - | - | 0.0394 | - |
| N (13) | - | 80 | - | - | 80 | - |
| Θ | 0° | 3.5° | 7° | 0° | 3.5° | 7° |
| Θ1 | 0° | - | - | 0° | - | - |
| Θ2 | 10° | 12° | 14° | 10° | 12° | 14° |
| Θ3 | 10° | 12° | 14° | 10° | 12° | 14° |
| R1 | 0.08 | - | - | 0.0031 | - | - |
| R2 | 0.08 | - | 0.20 | 0.0031 | - | 0.0079 |
| S | 0.20 | - | - | 0.0079 | - | - |
| aaa (1) | - | 0.20 | - | - | 0.0079 | - |
| bbb (1) | - | 0.20 | - | - | 0.0079 | - |
| ccc (1) | - | 0.08 | - | - | 0.0031 | - |
| ddd (1) | - | 0.08 | - | - | 0.0031 | - |

*Digest note:* the b1 Min inch value "00067" is as printed; 0.17 mm converts to 0.0067 in. L1 is printed as a Typ value (1.00 / 0.0394) with `-` in Min and Max, not as a REF value.

Notes:

1. Dimensioning and tolerancing schemes conform to ASME Y14.5M-1994.
2. The top package body size may be smaller than the bottom package size by as much as 0.15 mm.
3. Datums A-B and D to be determined at datum plane H.
4. To be determined at seating datum plane C.
5. Dimensions D1and E1 do not include mold flash or protrusions. Allowable mold flash or protrusions is "0.25 mm" per side. D1 and E1 are Maximum plastic body size dimensions including mold mismatch.
6. Details of pin 1 identifier are optional but must be located within the zone indicated.
7. All dimensions are in millimeters.
8. No intrusion allowed inwards the leads.
9. Dimension "b" does not include dambar protrusion. Allowable dambar protrusion shall not cause the lead width to exceed the maximum "b" dimension by more than 0.08 mm. Dambar cannot be located on the lower radius or the foot. Minimum space between protrusion and an adjacent lead is 0.07 mm for 0.4 mm and 0.5 mm pitch packages.
10. Exact shape of each corner is optional.
11. These dimensions apply to the flat section of the lead between 0.10 mm and 0.25 mm from the lead tip.
12. A1 is defined as the distance from the seating plane to the lowest point on the package body.
13. "N" is the number of terminal positions for the specified body size.
14. Values in inches are converted from mm and rounded to 4 decimal digits.
15. Drawing is not to scale.

**Figure 47. LQFP80 - Footprint example**

Recommended PCB land pattern (reference 9X_LQFP80_FP_V1). Dimensions are expressed in millimeters.

| Dimension | Value (mm) |
|---|---|
| Pad pitch | 0.5 |
| Pad width | 0.3 |
| Pad length | 1.2 |
| Offset from the inner edge of a pad row to the end of the perpendicular side row | 1.25 |
| Span of one pad row, first pad outer edge to last pad outer edge (each side) | 9.80 |
| Distance between inner edges of opposite pad rows (both X and Y) | 12.30 |
| Distance between outer edges of opposite pad rows (both X and Y) | 14.70 |

No pin numbers are printed on this footprint drawing; an arrow marker points at the right-most pad of the top row.

### 6.8 LQFP100 package information (1L)

This LQFP is a 100-pin, 14 x 14 mm, low-profile quad flat package.

Note: See list of notes in the notes section.

**Figure 48. LQFP100 - Outline (15)**

The outline drawing (package LQFP100, package code 1L, reference 1L_LQFP100_ME_DT_V5) has the same structure as Figure 37 (LQFP32): bottom view with `aaa C A-B D` on the 4x N/4 tips, `bbb H A-B D` 4x, and the pin 1 identifier zone bounded by D1/4 and E1/4 (note 6); side view with A, A2, A1 (note 12), b, (N-4) x e (note 13), flatness 0.05, lead position tolerance (labeled `aaa (M) C A-B D` in this drawing) and coplanarity `ccc C`; top view with D, E (note 4), D1, E1 (notes 2, 5), datums A and B on the left and right body edges and D (note 3) on the top edge, pins 1, 2, 3 at the top of the left side, pin N at the left end of the top side, corner shape optional (note 10); Section A-A lead form with θ, θ1, θ2, θ3, R1, R2, S, L, (L1) (notes 1, 11), datum plane H and the gauge plane; Section B-B with b, c (with plating, notes 9, 11) and b1, c1 (base metal, note 11). The package has 25 leads per side, pitch e = 0.50 mm.

**Table 79. LQFP100 - Mechanical data**

| Symbol | Millimeters Min | Millimeters Typ | Millimeters Max | Inches (14) Min | Inches (14) Typ | Inches (14) Max |
|---|---|---|---|---|---|---|
| A | - | 1.50 | 1.60 | - | 0.0590 | 0.0630 |
| A1 (12) | 0.05 | - | 0.15 | 0.0020 | - | 0.0059 |
| A2 | 1.35 | 1.40 | 1.45 | 0.0531 | 0.0551 | 0.0571 |
| b (9)(11) | 0.17 | 0.22 | 0.27 | 0.0067 | 0.0087 | 0.0106 |
| b1 (11) | 0.17 | 0.20 | 0.23 | 0.0067 | 0.0079 | 0.0090 |
| c (11) | 0.09 | - | 0.20 | 0.0035 | - | 0.0079 |
| c1 (11) | 0.09 | - | 0.16 | 0.0035 | - | 0.0063 |
| D (4) | - | 16.00 BSC | - | - | 0.6299 BSC | - |
| D1 (2)(5) | - | 14.00 BSC | - | - | 0.5512 BSC | - |
| E (4) | - | 16.00 BSC | - | - | 0.6299 BSC | - |
| E1 (2)(5) | - | 14.00 BSC | - | - | 0.5512 BSC | - |
| e | - | 0.50 BSC | - | - | 0.0197 BSC | - |
| L | 0.45 | 0.60 | 0.75 | 0.0177 | 0.0236 | 0.0295 |
| L1 (1)(11) | - | 1.00 | - | - | 0.0394 | - |
| N (13) | - | 100 | - | - | 100 | - |
| Θ | 0° | 3.5° | 7° | 0° | 3.5° | 7° |
| Θ1 | 0° | - | - | 0° | - | - |
| Θ2 | 10° | 12° | 14° | 10° | 12° | 14° |
| Θ3 | 10° | 12° | 14° | 10° | 12° | 14° |
| R1 | 0.08 | - | - | 0.0031 | - | - |
| R2 | 0.08 | - | 0.20 | 0.0031 | - | 0.0079 |
| S | 0.20 | - | - | 0.0079 | - | - |
| aaa (1) | - | 0.20 | - | - | 0.0079 | - |
| bbb (1) | - | 0.20 | - | - | 0.0079 | - |
| ccc (1) | - | 0.08 | - | - | 0.0031 | - |
| ddd (1) | - | 0.08 | - | - | 0.0031 | - |

Notes:

1. Dimensioning and tolerancing schemes conform to ASME Y14.5M-1994.
2. The top package body size may be smaller than the bottom package size by as much as 0.15 mm.
3. Datums A-B and D to be determined at datum plane H.
4. To be determined at seating datum plane C.
5. Dimensions D1 and E1 do not include mold flash or protrusions. Allowable mold flash or protrusions is "0.25 mm" per side. D1 and E1 are maximum plastic body size dimensions including mold mismatch.
6. Details of pin 1 identifier are optional but must be located within the zone indicated.
7. All dimensions are in millimeters.
8. No intrusion is allowed inwards the leads.
9. Dimension "b" does not include a dambar protrusion. Allowable dambar protrusion shall not cause the lead width to exceed the maximum "b" dimension by more than 0.08 mm. Dambar cannot be located on the lower radius or the foot. The minimum space between the protrusion and an adjacent lead is 0.07 mm for 0.4 mm and 0.5 mm pitch packages.
10. The exact shape of each corner is optional.
11. These dimensions apply to the flat section of the lead between 0.10 mm and 0.25 mm from the lead tip.
12. A1 is defined as the distance from the seating plane to the lowest point on the package body.
13. "N" is the number of terminal positions for the specified body size.
14. Values in inches are converted from mm and rounded to 4 decimal digits.
15. Drawing is not to scale.

**Figure 49. LQFP100 - Footprint example**

Recommended PCB land pattern (reference 1L_LQFP100_FP_DT_V1). Dimensions are expressed in millimeters.

| Dimension | Value (mm) |
|---|---|
| Pad pitch | 0.5 |
| Pad width | 0.3 |
| Span of one pad row, first pad outer edge to last pad outer edge (each side) | 12.3 |
| Distance between inner edges of opposite pad rows (both X and Y) | 14.3 |
| Distance between outer edges of opposite pad rows (both X and Y) | 16.7 |

The pad length is drawn with dimension arrows but no value is printed; (16.7 − 14.3) / 2 gives 1.2 mm. Pin numbering on the footprint: pins 1–25 run left to right on the bottom side, pins 26–50 bottom to top on the right side, pins 51–75 right to left on the top side, and pins 76–100 top to bottom on the left side.

### 6.9 Package thermal characteristics

The maximum chip-junction temperature, TJ max, in degrees Celsius, can be calculated using the following equation:

```
TJ max = TA max + (PD max × ΘJA)
```

Where:

- TA max is the maximum ambient temperature in °C.
- ΘJA is the package junction-to-ambient thermal resistance in °C/W.
- PD max is the sum of PINT max and PI/O max:

```
PD max = PINT max + PI/O max
```

- PINT max is the product of IDD and VDD, expressed in Watts. This is the maximum chip internal power.

PI/O max represents the maximum power dissipation on output pins:

```
PI/O max = Σ(VOL × IOL) + Σ((VDDIOx − VOH) × IOH)
```

taking into account the actual VOL/IOL and VOH/IOH of the I/Os at low and high level in the application.

**Table 80. Package thermal characteristics**

All rows: Symbol Θ, Definition "Thermal Resistance", unit °C/W.

| Parameter (package) | Junction-ambient ΘJA (°C/W) | Junction-board ΘJB (°C/W) | Junction-case ΘJC (°C/W) |
|---|---|---|---|
| LQFP100 | 39.2 | 25.1 | 11.4 |
| LQFP80 | 42.8 | 27.1 | 13.1 |
| LQFP64 | 44.3 | 26.6 | 13.5 |
| LQFP48 | 51.4 | 28.7 | 16.1 |
| LQFP32 | 51.4 | 28.7 | 16.1 |
| UFQFPN48 | 29.9 | 14.2 | 12 |
| UFQFPN32 | 40.4 | 22.3 | 20.5 |

#### 6.9.1 Reference documents

- JESD51-2 Integrated Circuits Thermal Test Method Environment Conditions - Natural Convection (Still Air) available on www.jedec.org.
- For information on thermal management, refer to application note "Guidelines for thermal management on STM32 applications" (AN5036) available on www.st.com.

## 7 Ordering information

Example part number: `STM32 C 552 K E T 6 J TR` (written as STM32C552KET6JTR). The fields, in order:

| Position | Field | Code | Meaning |
|---|---|---|---|
| 1 | Device family | STM32 | Arm-based 32-bit microcontroller |
| 2 | Product type | C | General purpose |
| 3 | Device subfamily | 551 | STM32C551xx without FDCAN |
| 3 | Device subfamily | 552 | STM32C552xx with FDCAN |
| 4 | Pin count | K | 32 pins |
| 4 | Pin count | C | 48 pins |
| 4 | Pin count | R | 64 pins |
| 4 | Pin count | M | 80 pins |
| 4 | Pin count | V | 100 pins |
| 5 | Flash memory size | C | 256 Kbytes |
| 5 | Flash memory size | E | 512 Kbytes |
| 6 | Package | U | UFQFPN |
| 6 | Package | T | LQFP |
| 7 | Temperature range | 6 | Temperature range: -40 to +85°C (+105°C junction) |
| 7 | Temperature range | 3 | Temperature range: -40 to +125°C (+140°C junction) |
| 8 | Pinout | Blank | Standard pinout |
| 8 | Pinout | J | Alternative pinout for LQFP64 |
| 9 | Packing | TR | Tape and reel |
| 9 | Packing | xxx | Programmed parts |

In the example, STM32 = device family, C = product type, 552 = device subfamily, K = pin count, E = flash memory size, T = package, 6 = temperature range, J = pinout, TR = packing.

Note: For a list of available options (such as speed and package) or for further information on any aspect of this device, contact your nearest ST sales office.

## Important security notice

The STMicroelectronics group of companies (ST) places a high value on product security, which is why the ST product(s) identified in this documentation may be certified by various security certification bodies and/or may implement our own security measures as set forth herein. However, no level of security certification and/or built-in security measures can guarantee that ST products are resistant to all forms of attacks. As such, it is the responsibility of each of ST's customers to determine if the level of security provided in an ST product meets the customer needs both in relation to the ST product alone, as well as when combined with other components and/or software for the customer end product or application. In particular, take note that:

- ST products may have been certified by one or more security certification bodies, such as Platform Security Architecture (www.psacertified.org) and/or Security Evaluation standard for IoT Platforms (www.trustcb.com). For details concerning whether the ST product(s) referenced herein have received security certification along with the level and current status of such certification, either visit the relevant certification standards website or go to the relevant product page on www.st.com for the most up to date information. As the status and/or level of security certification for an ST product can change from time to time, customers should re-check security certification status/level as needed. If an ST product is not shown to be certified under a particular security standard, customers should not assume it is certified.
- Certification bodies have the right to evaluate, grant and revoke security certification in relation to ST products. These certification bodies are therefore independently responsible for granting or revoking security certification for an ST product, and ST does not take any responsibility for mistakes, evaluations, assessments, testing, or other activity carried out by the certification body with respect to any ST product.
- Industry-based cryptographic algorithms (such as AES, DES, or MD5) and other open standard technologies which may be used in conjunction with an ST product are based on standards which were not developed by ST. ST does not take responsibility for any flaws in such cryptographic algorithms or open technologies or for any methods which have been or may be developed to bypass, decrypt or crack such algorithms or technologies.
- While robust security testing may be done, no level of certification can absolutely guarantee protections against all attacks, including, for example, against advanced attacks which have not been tested for, against new or unidentified forms of attack, or against any form of attack when using an ST product outside of its specification or intended use, or in conjunction with other components or software which are used by customer to create their end product or application. ST is not responsible for resistance against such attacks. As such, regardless of the incorporated security features and/or any information or support that may be provided by ST, each customer is solely responsible for determining if the level of attacks tested for meets their needs, both in relation to the ST product alone and when incorporated into a customer end product or application.
- All security features of ST products (inclusive of any hardware, software, documentation, and the like), including but not limited to any enhanced security features added by ST, are provided on an "AS IS" BASIS. AS SUCH, TO THE EXTENT PERMITTED BY APPLICABLE LAW, ST DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, unless the applicable written and signed contract terms specifically provide otherwise.

## Revision history

**Table 81. Document revision history**

| Date | Revision | Changes |
|---|---|---|
| 19-Feb-2026 | 1 | Initial release. |
| 12-May-2026 | 2 | Updated: Features; Section 2: Description; Table 12. STM32C55xxx pin/ball definition; Table 44. ESD absolute maximum ratings; Section 5.3.14: I/O port characteristics; Table 48. Output voltage characteristics (all I/Os except PC14 and PC15); Table 49. Output voltage characteristics for PC14 and PC15; Section 7: Ordering information |
| 13-May-2026 | 3 | Updated: Section 7: Ordering information |

## Important notice

IMPORTANT NOTICE – READ CAREFULLY

STMicroelectronics NV and its subsidiaries ("ST") reserve the right to make changes, corrections, enhancements, modifications, and improvements to ST products and/or to this document at any time without notice.

In the event of any conflict between the provisions of this document and the provisions of any contractual arrangement in force between the purchasers and ST, the provisions of such contractual arrangement shall prevail.

The purchasers should obtain the latest relevant information on ST products before placing orders. ST products are sold pursuant to ST's terms and conditions of sale in place at the time of order acknowledgment.

The purchasers are solely responsible for the choice, selection, and use of ST products and ST assumes no liability for application assistance or the design of the purchasers' products.

No license, express or implied, to any intellectual property right is granted by ST herein.

Resale of ST products with provisions different from the information set forth herein shall void any warranty granted by ST for such product.

If the purchasers identify an ST product that meets their functional and performance requirements but that is not designated for the purchasers' market segment, the purchasers shall contact ST for more information.

ST and the ST logo are trademarks of ST. For additional information about ST trademarks, refer to www.st.com/trademarks. All other product or service names are the property of their respective owners.

Information in this document supersedes and replaces information previously supplied in any prior versions of this document.

© 2026 STMicroelectronics – All rights reserved
