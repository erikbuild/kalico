# RM0522 Section 49.12: Microcontroller debug unit (DBGMCU)

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 2539–2557 (Section 49.12; Table 599 ends on page 2557), plus page 2413 (Section 49.1) for context.

Only Section 49.12 of Chapter 49 (Debug support (DBG)) is digested here. The Section 49.1 introduction is reproduced for context; the rest of Chapter 49 (debug port, access port, ROM tables, CoreSight components such as DWT, ITM, ETM, CTI and TPIU) is not covered.

*Digest note:* Register access abbreviations follow RM0522 Section 1.2: rw = read/write; r = read-only; w = write-only (software can only write to this bit; reading this bit returns the reset value).

## 49.1 DBG introduction (context)

A comprehensive set of debug features is provided to support software development and system integration:

- Breakpoint debugging of the CPU core
- Code execution tracing
- Software instrumentation
- Cross-triggering

The debug features can be controlled via a JTAG/Serial-wire debug access port, using industry standard debugging tools. A trace port allows data to be captured for logging and analysis.

The debug features are based on Arm® CoreSight™ components.

- SWJ-DP: JTAG/serial-wire debug port
- AHB-AP: AHB access port
- ROM table
- System control space (SCS)
- Breakpoint unit (BPU)
- Data watch-point and trace unit (DWT)
- Instrumentation trace macrocell (ITM)
- Embedded trace Macrocell™ (ETM)
- Cross trigger interface (CTI)
- Trace port interface unit (TPIU)

The debug features are accessible by the debugger via the AHB-AP.

Additional information can be found in the Arm documents referenced in Section 49.13.

## 49.12 Microcontroller debug unit (DBGMCU)

The DBGMCU is a component containing a number of registers that control the power and clock behavior in debug mode. It allows the debugger (or the software):

- To maintain the clock and power to the processor cores when in low-power modes (Sleep, Stop, or Standby mode).
- To maintain the clock and power to the system debug and trace components when in low-power modes.
- To stop the clock to certain peripherals (SMBUS timeout, watchdogs, timers, RTC) when either processor core is stopped in debug mode

### 49.12.1 Device ID

The DBGMCU includes an identity code register, DBGMCU_IDCODE. This register contains the ID code for the device. Debug tools can locate this register via the CoreSight discovery procedure described in Section 49.5: ROM tables.

### 49.12.2 Low-power mode emulation

When the device enters either Stop mode (clocks are stopped) or Standby mode (core power is switched off), the debugger can no longer access the debug access port, and looses the connection with the device. To avoid this, the debugger (or software) can set the DBG_STANDBY and/or DBG_STOP bits in DBGMCU_CR. These bits, when set, maintain the clock and power to the processor while the device is in the corresponding low-power mode. The processor remains in Sleep mode, and exits the low-power mode in the normal way. However, peripheral devices continue to operate, so the device behavior may not be identical to that of the actual low-power mode.

### 49.12.3 Peripheral clock freeze

The DBGMCU peripheral clock-freeze registers allow the operation of certain peripherals to be suspended in debug mode. The peripheral units, which support this feature are listed in the table below.

**Table 597. Peripheral clock-freeze control bits**

| Bus | Control register | Peripheral | Description |
|---|---|---|---|
| APB1L | DBGMCU_APB1LFZR | I3C1 | I3C1 SCL stall timeout counter |
| APB1L | DBGMCU_APB1LFZR | I2C2 | I2C2 SMBUS timeout |
| APB1L | DBGMCU_APB1LFZR | I2C1 | I2C1 SMBUS timeout |
| APB1L | DBGMCU_APB1LFZR | IWDG | Independent watchdog |
| APB1L | DBGMCU_APB1LFZR | WWDG | Window watchdog |
| APB1L | DBGMCU_APB1LFZR | TIM12 | General purpose timer 12 |
| APB1L | DBGMCU_APB1LFZR | TIM7 | General purpose timer 7 |
| APB1L | DBGMCU_APB1LFZR | TIM6 | General purpose timer 6 |
| APB1L | DBGMCU_APB1LFZR | TIM5 | General purpose timer 5 |
| APB1L | DBGMCU_APB1LFZR | TIM4 | General purpose timer 4 |
| APB1L | DBGMCU_APB1LFZR | TIM3 | General purpose timer 3 |
| APB1L | DBGMCU_APB1LFZR | TIM2 | General purpose timer 2 |
| APB2 | DBGMCU_APB2FZR | TIM17 | General purpose timer 17 |
| APB2 | DBGMCU_APB2FZR | TIM16 | General purpose timer 16 |
| APB2 | DBGMCU_APB2FZR | TIM15 | General purpose timer 15 |
| APB2 | DBGMCU_APB2FZR | TIM8 | General purpose timer 8 |
| APB2 | DBGMCU_APB2FZR | TIM1 | General purpose timer 1 |
| APB3 | DBGMCU_APB3FZR | RTC | Real time clock |
| APB3 | DBGMCU_APB3FZR | LPTIM1 | Low power timer 1 |
| AHB1 | DBGMCU_AHB1FZR | LPDMA2 0 to 7 | Low-power DMA2 channels 0 to 7 |
| AHB1 | DBGMCU_AHB1FZR | LPDMA1 0 to 7 | Low-power DMA1 channels 0 to 7 |

*Digest note:* STM32C551/C552 applicability, per the STM32C55xxx datasheet digest: the timers present are TIM1, TIM8 (advanced), TIM2, TIM5, TIM12, TIM15, TIM16, TIM17 (general purpose) and TIM6, TIM7 (basic); TIM3 and TIM4 are not present, and the CMSIS header stm32c552xx.h defines no DBG_TIM3_STOP / DBG_TIM4_STOP bits. LPDMA1 has 8 channels (0 to 7) but LPDMA2 has only 4 channels (0 to 3) on STM32C55xxx; the header defines DBG_LPDMA2_0_STOP to DBG_LPDMA2_3_STOP only. I3C1, I2C1, I2C2, IWDG, WWDG, RTC and LPTIM1 are present.

Each peripheral unit or DMA channel has a corresponding control bit, DBG_xxx_STOP, where xxx is the acronym of the peripheral (or DMA channel). The control bits are organized in DBGMCU_zzzFZR registers, where zzz corresponds to the name of the bus (AHB or APB). For example, DBGMCU_APB1LFZR contains the control bits for peripherals on the APB1L bus.

The control bit, when set, causes the corresponding peripheral operation to be suspended when the CPU is stopped in debug (HALTED = 1), according to the table below:

**Table 598. Peripheral behavior in debug mode**

| HALTED | DBG_xxx_STOP | Peripheral behavior |
|---|---|---|
| 0 | X | The operation continues. |
| 1 | 0 | The operation continues. |
| 1 | 1 | The operation is suspended. |

### 49.12.4 DBGMCU registers

The DBGMCU registers are not reset by a system reset, only by a power-on reset. They are accessible to the debugger via the AHB access port at base address 0xE00E 4000, and to software at base address 0x4402 4000.

For the actual availability of some peripherals and their related bits, check the datasheet or Table 3: Memory map and peripheral register boundary addresses. If not present, consider them reserved, and keep them at their reset value.

*Digest note:* The CMSIS header agrees on the software base: `DBGMCU_BASE` = AHB3PERIPH_BASE + 0x4000 = 0x4402 4000 (RM0522 Table 3 lists DEBUG at 0x4402 4000 - 0x4402 4FFF for all STM32C5 lines).

#### DBGMCU identity code register (DBGMCU_IDCODE)

Address offset: 0x000. Reset value: 0xXXXX 6XXX.

This register is always accessible.

- **Bits 31:16 REV_ID[15:0]** (r): Revision of the device
  - 0x1000: Revision A
  - 0x1001: Revision Z
  - 0x1003: Revision Y
- **Bits 15:12** Reserved, must be kept at reset value.
- **Bits 11:0 DEV_ID[11:0]** (r): Device identification
  - 0x44E: STM32C55xx/C56xx
  - 0x44F: STM32C53xx/C54xx
  - 0x45A: STM32C59xx/C5Axx

*Digest note:* STM32C551/C552 report DEV_ID = 0x44E. The reset value 0xXXXX 6XXX shows bits 15:12 = 0x6 although those bits are described as Reserved (the register map row gives no value for them), so software should extract DEV_ID with the mask 0xFFF rather than compare the low half-word.

#### DBGMCU configuration register (DBGMCU_CR)

Address offset: 0x004. Reset value: 0x0000 0000.

This register is accessible to the debugger in RDP L0. It is always accessible to software.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:6 TRACE_MODE[1:0]** (rw): Trace pin assignment
  - 0x0: Trace pins assigned for asynchronous mode (TRACESWO)
  - 0x1: Trace pins assigned for synchronous mode with a port width of 1 (TRACECK, TRACED0)
  - 0x2: Trace pins assigned for synchronous mode with a port width of 2 ((TRACECK, TRACED0-1)
  - 0x3: Trace pins assigned for synchronous mode with a port width of 4 ((TRACECK, TRACED0-3)
- **Bit 5 TRACE_EN** (rw): Trace port and clock enable.
  This bit enables the trace port clock, TRACECK.
  - 0: Disabled
  - 1: Enabled
- **Bit 4 TRACE_IOEN** (rw): Trace pin enable
  - 0: Disabled. Trace pins not assigned.
  - 1: Enabled. Trace pins assigned according to the value of TRACE_MODE bitfield.
- **Bit 3** Reserved, must be kept at reset value.
- **Bit 2 DBG_STANDBY** (rw): Debug in Standby mode
  - 0: Normal operation. All clocks are disabled and the core is powered down automatically in Standby mode.
  - 1: Automatic clock stop/power down disabled. All active clocks and oscillators continue to run during Standby mode. The core supply is maintained, allowing full debug capability. On exit from Standby mode, a system reset is performed.
- **Bit 1 DBG_STOP** (rw): Debug in Stop mode
  - 0: Normal operation. All clocks are disabled automatically in Stop mode.
  - 1: Automatic clock stop disabled. All active clocks and oscillators continue to run during Stop mode, allowing full debug capability. On exit from Stop mode, the clock settings are set to the Stop mode exit state.
- **Bit 0 DBG_SLEEP** (rw): Debug in Sleep mode
  - 0: Normal operation. Clocks to CPU and buses are disabled automatically in Sleep mode.
  - 1: Automatic clock stop disabled. All active clocks and oscillators continue to run during Sleep mode, allowing full debug capability. On exit from Sleep mode, the clock settings are set to the Sleep mode exit state.

#### DBGMCU APB1L peripheral freeze register (DBGMCU_APB1LFZR)

Address offset: 0x008. Reset value: 0x0000 0000.

This register is accessible to the debugger after successful authentication. Prior to this, debugger accesses are ignored. It is always accessible to software.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bit 23 DBG_I3C1_STOP** (rw): I3C1 SCL stall counter stop in debug
  - 0: Normal operation. I3C1 SCL stall timeout counter continues to operate while CPU is in debug mode.
  - 1: Stop in debug. I3C1 SCL stall timeout counter is frozen while CPU is in debug mode.
- **Bit 22 DBG_I2C2_STOP** (rw): I2C2 SMBUS timeout stop in debug
  - 0: Normal operation. I2C2 SMBUS timeout continues to operate while CPU is in debug mode.
  - 1: Stop in debug. I2C2 SMBUS timeout is frozen while CPU is in debug mode.
- **Bit 21 DBG_I2C1_STOP** (rw): I2C1 SMBUS timeout stop in debug
  - 0: Normal operation. I2C1 SMBUS timeout continues to operate while CPU is in debug mode.
  - 1: Stop in debug. I2C1 SMBUS timeout is frozen while CPU is in debug mode.
- **Bits 20:13** Reserved, must be kept at reset value.
- **Bit 12 DBG_IWDG_STOP** (rw): IWDG stop in debug
  - 0: Normal operation. IWDG continues to operate while CPU is in debug mode.
  - 1: Stop in debug. IWDG is frozen while CPU is in debug mode.
- **Bit 11 DBG_WWDG_STOP** (rw): WWDG stop in debug
  - 0: Normal operation. WWDG continues to operate while CPU is in debug mode.
  - 1: Stop in debug. WWDG is frozen while CPU is in debug mode.
- **Bits 10:7** Reserved, must be kept at reset value.
- **Bit 6 DBG_TIM12_STOP** (rw): TIM12 stop in debug
  - 0: Normal operation. TIM12 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM12 is frozen while CPU is in debug mode.
- **Bit 5 DBG_TIM7_STOP** (rw): TIM7 stop in debug
  - 0: Normal operation. TIM7 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM7 is frozen while CPU is in debug mode.
- **Bit 4 DBG_TIM6_STOP** (rw): TIM6 stop in debug
  - 0: Normal operation. TIM6 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM6 is frozen while CPU is in debug mode.
- **Bit 3 DBG_TIM5_STOP** (rw): TIM5 stop in debug
  - 0: Normal operation. TIM5 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM5 is frozen while CPU is in debug mode.
- **Bit 2 DBG_TIM4_STOP** (rw): TIM4 stop in debug
  - 0: Normal operation. TIM4 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM4 is frozen while CPU is in debug mode.
- **Bit 1 DBG_TIM3_STOP** (rw): TIM3 stop in debug
  - 0: Normal operation. TIM3 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM3 is frozen while CPU is in debug mode.
- **Bit 0 DBG_TIM2_STOP** (rw): TIM2 stop in debug
  - 0: Normal operation. TIM2 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM2 is frozen while CPU is in debug mode.

*Digest note:* DBG_TIM4_STOP (bit 2) and DBG_TIM3_STOP (bit 1) do not apply to STM32C551/C552 (no TIM3/TIM4); treat them as reserved there.

#### DBGMCU APB1H peripheral freeze register (DBGMCU_APB1HFZR)

Address offset: 0x00C. Reset value: 0x0000 0000.

This register is accessible to the debugger after successful authentication. Prior to this, debugger accesses are ignored. It is always accessible to software.

- **Bits 31:0** Reserved, must be kept at reset value.

#### DBGMCU APB2 peripheral freeze register (DBGMCU_APB2FZR)

Address offset: 0x010. Reset value: 0x0000 0000.

This register is accessible to the debugger after successful authentication. Prior to this, debugger accesses are ignored. It is always accessible to software.

- **Bits 31:19** Reserved, must be kept at reset value.
- **Bit 18 DBG_TIM17_STOP** (rw): TIM17 stop in debug
  - 0: Normal operation. TIM17 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM17 is frozen while CPU is in debug mode.
- **Bit 17 DBG_TIM16_STOP** (rw): TIM16 stop in debug
  - 0: Normal operation. TIM16 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM16 is frozen while CPU is in debug mode.
- **Bit 16 DBG_TIM15_STOP** (rw): TIM15 stop in debug
  - 0: Normal operation. TIM15 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM15 is frozen while CPU is in debug mode.
- **Bits 15:14** Reserved, must be kept at reset value.
- **Bit 13 DBG_TIM8_STOP** (rw): TIM8 stop in debug
  - 0: Normal operation. TIM8 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM8 is frozen while CPU is in debug mode.
- **Bit 12** Reserved, must be kept at reset value.
- **Bit 11 DBG_TIM1_STOP** (rw): TIM1 stop in debug
  - 0: Normal operation. TIM1 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. TIM1 is frozen while CPU is in debug mode.
- **Bits 10:0** Reserved, must be kept at reset value.

#### DBGMCU APB3 peripheral freeze register (DBGMCU_APB3FZR)

Address offset: 0x014. Reset value: 0x0000 0000.

This register is accessible to the debugger after successful authentication. Prior to this, debugger accesses are ignored. It is always accessible to software.

- **Bit 31** Reserved, must be kept at reset value.
- **Bit 30 DBG_RTC_STOP** (rw): RTC stop in debug
  - 0: Normal operation. RTC continues to operate while CPU is in debug mode.
  - 1: Stop in debug. RTC is frozen while CPU is in debug mode.
- **Bits 29:18** Reserved, must be kept at reset value.
- **Bit 17 DBG_LPTIM1_STOP** (rw): LPTIM1 stop in debug
  - 0: Normal operation. LPTIM1 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPTIM1 is frozen while CPU is in debug mode.
- **Bits 16:0** Reserved, must be kept at reset value.

#### DBGMCU AHB1 peripheral freeze register (DBGMCU_AHB1FZR)

Address offset: 0x020. Reset value: 0x0000 0000.

This register is accessible to the debugger after successful authentication. Prior to this, debugger accesses are ignored. It is always accessible to software.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bit 23 DBG_LPDMA2_7_STOP** (rw): LPDMA2 channel 7 stop in debug
  - 0: Normal operation. LPDMA2 channel 7 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA2 channel 7 is frozen while CPU is in debug mode.
- **Bit 22 DBG_LPDMA2_6_STOP** (rw): LPDMA2 channel 6 stop in debug
  - 0: Normal operation. LPDMA2 channel 6 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA2 channel 6 is frozen while CPU is in debug mode.
- **Bit 21 DBG_LPDMA2_5_STOP** (rw): LPDMA2 channel 5 stop in debug
  - 0: Normal operation. LPDMA2 channel 5 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA2 channel 5 is frozen while CPU is in debug mode.
- **Bit 20 DBG_LPDMA2_4_STOP** (rw): LPDMA2 channel 4 stop in debug
  - 0: Normal operation. LPDMA2 channel 4 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA2 channel 4 is frozen while CPU is in debug mode.
- **Bit 19 DBG_LPDMA2_3_STOP** (rw): LPDMA2 channel 3 stop in debug
  - 0: Normal operation. LPDMA2 channel 3 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA2 channel 3 is frozen while CPU is in debug mode.
- **Bit 18 DBG_LPDMA2_2_STOP** (rw): LPDMA2 channel 2 stop in debug
  - 0: Normal operation. LPDMA2 channel 2 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA2 channel 2 is frozen while CPU is in debug mode.
- **Bit 17 DBG_LPDMA2_1_STOP** (rw): LPDMA2 channel 1 stop in debug
  - 0: Normal operation. LPDMA2 channel 1 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA2 channel 1 is frozen while CPU is in debug mode.
- **Bit 16 DBG_LPDMA2_0_STOP** (rw): LPDMA2 channel 0 stop in debug
  - 0: Normal operation. LPDMA2 channel 0 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA2 channel 0 is frozen while CPU is in debug mode.
- **Bits 15:8** Reserved, must be kept at reset value.
- **Bit 7 DBG_LPDMA1_7_STOP** (rw): LPDMA1 channel 7 stop in debug
  - 0: Normal operation. LPDMA1 channel 7 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA1 channel 7 is frozen while CPU is in debug mode.
- **Bit 6 DBG_LPDMA1_6_STOP** (rw): LPDMA1 channel 6 stop in debug
  - 0: Normal operation. LPDMA1 channel 6 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA1 channel 6 is frozen while CPU is in debug mode.
- **Bit 5 DBG_LPDMA1_5_STOP** (rw): LPDMA1 channel 5 stop in debug
  - 0: Normal operation. LPDMA1 channel 5 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA1 channel 5 is frozen while CPU is in debug mode.
- **Bit 4 DBG_LPDMA1_4_STOP** (rw): LPDMA1 channel 4 stop in debug
  - 0: Normal operation. LPDMA1 channel 4 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA1 channel 4 is frozen while CPU is in debug mode.
- **Bit 3 DBG_LPDMA1_3_STOP** (rw): LPDMA1 channel 3 stop in debug
  - 0: Normal operation. LPDMA1 channel 3 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA1 channel 3 is frozen while CPU is in debug mode.
- **Bit 2 DBG_LPDMA1_2_STOP** (rw): LPDMA1 channel 2 stop in debug
  - 0: Normal operation. LPDMA1 channel 2 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA1 channel 2 is frozen while CPU is in debug mode.
- **Bit 1 DBG_LPDMA1_1_STOP** (rw): LPDMA1 channel 1 stop in debug
  - 0: Normal operation. LPDMA1 channel 1 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA1 channel 1 is frozen while CPU is in debug mode.
- **Bit 0 DBG_LPDMA1_0_STOP** (rw): LPDMA1 channel 0 stop in debug
  - 0: Normal operation. LPDMA1 channel 0 continues to operate while CPU is in debug mode.
  - 1: Stop in debug. LPDMA1 channel 0 is frozen while CPU is in debug mode.

*Digest note:* DBG_LPDMA2_7_STOP to DBG_LPDMA2_4_STOP (bits 23:20) do not apply to STM32C551/C552, whose LPDMA2 has channels 0 to 3 only; treat them as reserved there.

#### DBGMCU status register (DBGMCU_SR)

Address offset: 0x0FC. Reset value: 0x0001 XX03.

This register is always accessible.

- **Bits 31:16 AP_ENABLED[15:0]** (w): Access port enable
  Bit n identifies whether access port AP n is open (can be accessed via the debug port), or locked (debug access to the AP is blocked).
  - Bit n = 0: APn locked
  - Bit n = 1: APn enabled
- **Bits 15:0 AP_PRESENT[15:0]** (w): Access port present
  Bit n identifies whether access port AP n is present in device.
  - Bit n = 0: APn absent
  - Bit n = 1: APn present

*Digest note:* The RM marks every bit of this status register "w" (write-only), and the CMSIS header declares `SR` as `__OM` (write-only); both are kept as printed. [unclear in source: whether DBGMCU_SR is readable by software, given the "w" access marking on a status register].

#### DBGMCU debug authentication mailbox host register (DBGMCU_DBG_AUTH_HOST)

Address offset: 0x100. Reset value: 0xXXXX XXXX.

This register is read only when accessed by the CPU. Writes have no effect. This register can be written and read by an external debugger.

- **Bits 31:0 AUTH_KEY[31:0]** (rw): Device authentication key
  The device specific 128-bit authentication key (OEM key) must be written to this register (in four successive 32-bit writes, least significant word first) to permit RDP regression.

#### DBGMCU debug authentication mailbox device register (DBGMCU_DBG_AUTH_DEVICE)

Address offset: 0x104. Reset value: 0xXXXX XXXX.

This register is read only when accessed via the debug port. Writes have no effect. This register can be read by the CPU.

- **Bits 31:0 AUTH_ID[31:0]** (r): Device specific ID

#### DBGMCU boundary-scan key password register (DBGMCU_DBG_BSKEY_PWD)

Address offset: 0x10C. Reset value: 0xXXXX XXXX.

This register is read only when accessed by the CPU. Writes have no effect. This register can be written and read by an external debugger.

- **Bits 31:0 DBG_BSKEY_PWD[31:0]** (rw): Boundary-scan key (BS key)
  The device 32-bit BS key must be written to this register to permit RDP transition from L2_wBS to L2, closing the boundary-scan access. Writing a wrong key locks access to the device, and prevents code execution from the flash memory.

#### DBGMCU debug OEMKEY validation register (DBGMCU_DBG_VALR)

Address offset: 0x110. Reset value: 0x0000 000X.

This register is always accessible. It can be read by an external debugger.

- **Bits 31:2** Reserved, must be kept at reset value.
- **Bit 1 VAL_OEMKEY** (r): OEMKEY validation.
  This bit is set by hardware once the validation request of the OEMKEY is performed, and if the provided password match the provisioned OEMKEY.
  This bit is reset by hardware on power-on reset.
- **Bit 0 VAL_RDY** (r): Validation ready
  This bit is set by hardware once the validation request of the OEMKEY is performed. Results of the validation can be read in the VAL_OEMKEY bit. This VAL_RDY bit is reset by hardware upon system reset exit if VAL_OEMKEY is set or by power-on reset.

#### DBGMCU CoreSight peripheral identity register 4 (DBGMCU_PIDR4)

Address offset: 0xFD0. Reset value: 0x0000 0000.

This register is always accessible.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:4 SIZE[3:0]** (r): Register file size
  - 0x0: The register file occupies a single 4-Kbyte region.
- **Bits 3:0 JEP106CON[3:0]** (r): JEP106 continuation code
  - 0x0: STMicroelectronics JEDEC code

#### DBGMCU CoreSight peripheral identity register 0 (DBGMCU_PIDR0)

Address offset: 0xFE0. Reset value: 0x0000 0000.

This register is always accessible.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:0 PARTNUM[7:0]** (r): Part number bits [7:0]
  - 0x00: DBGMCU part number

#### DBGMCU CoreSight peripheral identity register 1 (DBGMCU_PIDR1)

Address offset: 0xFE4. Reset value: 0x0000 0000.

This register is always accessible.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:4 JEP106ID[3:0]** (r): JEP106 identity code bits [3:0]
  - 0x0: STMicroelectronics JEDEC code
- **Bits 3:0 PARTNUM[11:8]** (r): Part number bits [11:8]
  - 0x0: DBGMCU part number

#### DBGMCU CoreSight peripheral identity register 2 (DBGMCU_PIDR2)

Address offset: 0xFE8. Reset value: 0x0000 000A.

This register is always accessible.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:4 REVISION[3:0]** (r): Component revision number
  - 0x0: r0p0
- **Bit 3 JEDEC** (r): JEDEC assigned value
  - 0x1: Designer identification specified by JEDEC
- **Bits 2:0 JEP106ID[6:4]** (r): JEP106 identity code bits [6:4]
  - 0x2: STMicroelectronics JEDEC code

#### DBGMCU CoreSight peripheral identity register 3 (DBGMCU_PIDR3)

Address offset: 0xFEC. Reset value: 0x0000 0000.

This register is always accessible.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:4 REVAND[3:0]** (r): Metal fix version
  - 0x0: No metal fix
- **Bits 3:0 CMOD[3:0]** (r): Customer modified
  - 0x0: No customer modifications

#### DBGMCU CoreSight component identity register 0 (DBGMCU_CIDR0)

Address offset: 0xFF0. Reset value: 0x0000 000D.

This register is always accessible.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:0 PREAMBLE[7:0]** (r): Component identification bits [7:0]
  - 0x0D: Common identification value

#### DBGMCU CoreSight component identity register 1 (DBGMCU_CIDR1)

Address offset: 0xFF4. Reset value: 0x0000 00F0.

This register is always accessible.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:4 CLASS[3:0]** (r): Component identification bits [15:12] - component class
  - 0xF: Non-CoreSight component
- **Bits 3:0 PREAMBLE[11:8]** (r): Component identification bits [11:8]
  - 0x0: Common identification value

#### DBGMCU CoreSight component identity register 2 (DBGMCU_CIDR2)

Address offset: 0xFF8. Reset value: 0x0000 0005.

This register is always accessible.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:0 PREAMBLE[19:12]** (r): Component identification bits [23:16]
  - 0x05: Common identification value

#### DBGMCU CoreSight component identity register 3 (DBGMCU_CIDR3)

Address offset: 0xFFC. Reset value: 0x0000 00B1.

This register is always accessible.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:0 PREAMBLE[27:20]** (r): Component identification bits [31:24]
  - 0xB1: Common identification value

#### DBGMCU register map

**Table 599. DBGMCU register map and reset values**

| Offset | Register | Reset value | Fields (bit positions) |
|---|---|---|---|
| 0x000 | DBGMCU_IDCODE | 0xXXXX 6XXX (map row: bits 31:16 = x, bits 15:12 Res. with no value, bits 11:0 = x) | REV_ID[15:0] (31:16), Res. (15:12), DEV_ID[11:0] (11:0) |
| 0x004 | DBGMCU_CR | 0x0000 0000 | Res. (31:8), TRACE_MODE[1:0] (7:6), TRACE_EN (5), TRACE_IOEN (4), Res. (3), DBG_STANDBY (2), DBG_STOP (1), DBG_SLEEP (0) |
| 0x008 | DBGMCU_APB1LFZR | 0x0000 0000 | Res. (31:24), DBG_I3C1_STOP (23), DBG_I2C2_STOP (22), DBG_I2C1_STOP (21), Res. (20:13), DBG_IWDG_STOP (12), DBG_WWDG_STOP (11), Res. (10:7), DBG_TIM12_STOP (6), DBG_TIM7_STOP (5), DBG_TIM6_STOP (4), DBG_TIM5_STOP (3), DBG_TIM4_STOP (2), DBG_TIM3_STOP (1), DBG_TIM2_STOP (0) |
| 0x00C | DBGMCU_APB1HFZR | 0x0000 0000 | Res. (31:0) |
| 0x010 | DBGMCU_APB2FZR | 0x0000 0000 | Res. (31:19), DBG_TIM17_STOP (18), DBG_TIM16_STOP (17), DBG_TIM15_STOP (16), Res. (15:14), DBG_TIM8_STOP (13), Res. (12), DBG_TIM1_STOP (11), Res. (10:0) |
| 0x014 | DBGMCU_APB3FZR | 0x0000 0000 | Res. (31), DBG_RTC_STOP (30), Res. (29:18), DBG_LPTIM1_STOP (17), Res. (16:0) |
| 0x018-0x01C | Reserved | - | Reserved |
| 0x020 | DBGMCU_AHB1FZR | 0x0000 0000 | Res. (31:24), DBG_LPDMA2_7_STOP (23), DBG_LPDMA2_6_STOP (22), DBG_LPDMA2_5_STOP (21), DBG_LPDMA2_4_STOP (20), DBG_LPDMA2_3_STOP (19), DBG_LPDMA2_2_STOP (18), DBG_LPDMA2_1_STOP (17), DBG_LPDMA2_0_STOP (16), Res. (15:8), DBG_LPDMA1_7_STOP (7), DBG_LPDMA1_6_STOP (6), DBG_LPDMA1_5_STOP (5), DBG_LPDMA1_4_STOP (4), DBG_LPDMA1_3_STOP (3), DBG_LPDMA1_2_STOP (2), DBG_LPDMA1_1_STOP (1), DBG_LPDMA1_0_STOP (0) |
| 0x024-0x0F8 | Reserved | - | Reserved |
| 0x0FC | DBGMCU_SR | 0x0001 XX03 | AP_ENABLED[15:0] (31:16), AP_PRESENT[15:0] (15:0) |
| 0x100 | DBGMCU_DBG_AUTH_HOST | 0xXXXX XXXX | AUTH_KEY[31:0] (31:0) |
| 0x104 | DBGMCU_DBG_AUTH_DEVICE | 0xXXXX XXXX | AUTH_ID[31:0] (31:0) |
| 0x108 | Reserved | - | Reserved |
| 0x10C | DBGMCU_DBG_BSKEY_PWD | 0xXXXX XXXX | DBG_BSKEY_PWD[31:0] (31:0) |
| 0x110 | DBGMCU_DBG_VALR | 0x0000 000X (map row: bits 1:0 = x) | Res. (31:2), VAL_OEMKEY (1), VAL_RDY (0) |
| 0x114-0xFCC | Reserved | - | Reserved |
| 0xFD0 | DBGMCU_PIDR4 | 0x0000 0000 | Res. (31:8), SIZE[3:0] (7:4), JEP106CON[3:0] (3:0) |
| 0xFD4-0xFDC | Reserved | - | Reserved |
| 0xFE0 | DBGMCU_PIDR0 | 0x0000 0000 | Res. (31:8), PARTNUM[7:0] (7:0) |
| 0xFE4 | DBGMCU_PIDR1 | 0x0000 0000 | Res. (31:8), JEP106ID[3:0] (7:4), PARTNUM[11:8] (3:0) |
| 0xFE8 | DBGMCU_PIDR2 | 0x0000 000A | Res. (31:8), REVISION[3:0] (7:4), JEDEC (3), JEP106ID[6:4] (2:0) |
| 0xFEC | DBGMCU_PIDR3 | 0x0000 0000 | Res. (31:8), REVAND[3:0] (7:4), CMOD[3:0] (3:0) |
| 0xFF0 | DBGMCU_CIDR0 | 0x0000 000D | Res. (31:8), PREAMBLE[7:0] (7:0) |
| 0xFF4 | DBGMCU_CIDR1 | 0x0000 00F0 | Res. (31:8), CLASS[3:0] (7:4), PREAMBLE[11:8] (3:0) |
| 0xFF8 | DBGMCU_CIDR2 | 0x0000 0005 | Res. (31:8), PREAMBLE[19:12] (7:0) |
| 0xFFC | DBGMCU_CIDR3 | 0x0000 00B1 | Res. (31:8), PREAMBLE[27:20] (7:0) |

Refer to Section 2.2: Memory organization for register boundary addresses.

*Digest note:* In the printed register map some field labels differ from the register descriptions: PIDR1 bits 3:0 are labelled PARTNUM[3:0] (description: PARTNUM[11:8]), PIDR2 bits 2:0 JEP106ID[2:0] (description: JEP106ID[6:4]), CIDR1 bits 3:0 PREAMBLE[3:0] (description: PREAMBLE[11:8]), CIDR2 and CIDR3 bits 7:0 PREAMBLE[7:0] (descriptions: PREAMBLE[19:12] and PREAMBLE[27:20]). The table above uses the description names. All bit positions agree with the CMSIS header stm32c552xx.h, whose `DBGMCU_TypeDef` matches these offsets (it names offset 0x00C "Debug MCU APB1 freeze register 2").
