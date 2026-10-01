# RM0522 Chapter 37: Independent watchdog (IWDG)

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 1528–1543.

## 37.1 IWDG introduction

The independent watchdog (IWDG) peripheral offers a high safety level, thanks to its capability to detect malfunctions due to software or hardware failures.

The IWDG is clocked by an independent clock, and stays active even if the main clock fails.

In addition, the watchdog function is performed in the VDD voltage domain, allowing the IWDG to remain functional even in low power modes. Refer to Section 37.3 to check the capability of the IWDG in this product.

The IWDG is best suited for applications that require the watchdog to run as a totally independent process outside the main application, making it very reliable to detect any unexpected behavior.

## 37.2 IWDG main features

- 12-bit down-counter
- Dual voltage domain, thus enabling operation in low power modes
- Independent clock
- Early wake-up interrupt generation
- Reset generation
  - In case of timeout
  - In case of refresh outside the expected window

## 37.3 IWDG implementation

**Table 380. IWDG features (1)**

| IWDG modes/features | IWDG |
|---|---|
| LSI used as IWDG kernel clock (iwdg_ker_ck) | X |
| Window function | X |
| Early wake-up interrupt generation | X |
| System reset generation(2) | X |
| Capability to work in system Stop | X |
| Capability to work in system Standby | X |
| Capability to generate an interrupt in system Stop | X |
| Capability to generate an interrupt in system Standby | - |
| Capability to be frozen when the microcontroller enters in Debug mode(3) | X |
| Option bytes to control the activity in Stop mode(4) | X |
| Option bytes to control the activity in Standby mode(5) | X |
| Option bytes to control the Hardware mode(6) | X |

Notes:

1. 'X' = supported, '-' = not supported.
2. Refer to the RCC section for additional information.
3. Controlled via DBG_IWDG_STOP in DBG section.
4. Controlled via the option byte IWDG_STOP in FLASH section.
5. Controlled via the option byte IWDG_STDBY in FLASH section.
6. Controlled via the option byte IWDG_SW in FLASH section.

*Digest note:* in the CMSIS header (stm32c552xx.h), the debug freeze bit is DBGMCU_APB1LFZR.DBG_IWDG_STOP, bit 12 (mask 0x0000 1000), with DBGMCU_APB1LFZR at DBGMCU offset 0x008 and DBGMCU_BASE = AHB3PERIPH_BASE + 0x4000. The option bits are FLASH_OPTSR_CUR/FLASH_OPTSR_PRG: IWDG_SW bit 3, IWDG_STOP bit 20 ("IWDG Stop mode freeze"), IWDG_STDBY bit 21 ("IWDG Standby mode freeze"). Their polarity is defined in the FLASH and DBGMCU chapters, not here.

## 37.4 IWDG functional description

### 37.4.1 IWDG block diagram

Figure 552 shows the functional blocks of the independent watchdog module.

**Figure 552. Independent watchdog block diagram** (described)

The IWDG has two parts:

- VCORE voltage domain: the "Register interface" (connected to the APB bus, clocked by iwdg_pclk) and the "IRQ interface" (output iwdg_it).
- VDD voltage domain: "Shadow registers and Control" (output iwdg_ker_req), a "Prescaler" (input iwdg_ker_ck, output presc_ck), a "12-bit reload value", the 12-bit down-counter "IWDCNT" (clocked by presc_ck, loaded from the reload value), and "Comparator logic" (outputs iwdg_wkup and iwdg_out_rst). The input iwdg_in_rst resets the VDD-domain logic.

The two domains are linked through a "sync" (synchronization) stage between the register interface and the shadow registers.

The register and IRQ interfaces are located into the VCORE voltage domain. The watchdog function itself is located into the VDD voltage domain to remain functional in low power modes. See Section 37.3 for IWDG capabilities.

The register and IRQ interfaces are mainly clocked by the APB clock (iwdg_pclk), while the watchdog function is clocked by a dedicated kernel clock (iwdg_ker_ck). A synchronization mechanism makes the data exchange between the two domains possible. Note that most of the registers located in the register interface are shadowed into the VDD voltage domain.

The IWDG down-counter (IWDCNT) is clocked by the prescaled clock (presc_ck). The prescaled clock is generated from the kernel clock iwdg_ker_ck divided by the prescaler, according to PR[3:0] bitfield.

The table below gives the timing delays according to the actions performed on the IWDG: changing the prescaler, the timeout, the window or the early wake-up comparator values or doing a refresh.

**Table 381. IWDG delays versus actions (1)**

| Delay | Min | Max |
|---|---|---|
| TDRVU, TDPVU | 5 Tk | 6 Tk |
| TDWVU | - | 6 Tk |
| TDEWU | - | 6 Tk |
| TDRefresh | 2 Tk | 2 Tk + Tp |
| TDRefAuto | - | Tp |

Notes:

1. Tk represents a period of the kernel clock input, Tp represents a period of presc_ck.

### 37.4.2 IWDG internal signals

The list of IWDG internal signals is detailed in Table 382.

**Table 382. IWDG internal input/output signals**

| Signal name | Signal type | Description |
|---|---|---|
| iwdg_ker_ck | Input | IWDG kernel clock |
| iwdg_ker_req | Input | IWDG kernel clock request |
| iwdg_pclk | Input | IWDG APB clock |
| iwdg_out_rst | Output | IWDG reset output |
| iwdg_in_rst | Input | IWDG reset input |
| iwdg_wkup | Output | IWDG wake-up event |
| iwdg_it | Output | IWDG early wake-up interrupt |

*Digest note:* Table 382 lists iwdg_ker_req as an input, but Figure 552 draws it as an output of the IWDG (a kernel clock request to the RCC).

### 37.4.3 Software and hardware watchdog modes

The watchdog modes allow the application to select the way the IWDG is enabled, either by software commands (Software watchdog mode), or automatically (Hardware watchdog mode). All other functions work similarly for both Software and Hardware modes.

The software watchdog mode is the default working mode. The independent watchdog is started by writing the value 0x0000 CCCC into the IWDG key register (IWDG_KR), and the IWDCNT starts counting down from the reset value (0xFFF).

In the hardware watchdog mode the independent watchdog is started automatically at power-on, or every time it is reset (via iwdg_in_rst). The IWDCNT down-counter starts counting down from the reset value 0xFFF. The hardware watchdog mode feature is enabled through the device option bits, see Section 37.3 for details.

When the IWDG is enabled the ONF flag is set to 1.

When the IWDCNT reaches 0x000, a reset signal is generated (iwdg_out_rst asserted).

Whenever the key value 0x0000 AAAA is written in the IWDG key register (IWDG_KR), the IWDG_RLR value is reloaded into the IWDCNT, and the watchdog reset is prevented.

Due to re-synchronization delays, the IWDG must be refreshed before the IWDCNT down-counter reaches 1.

Once started, the IWDG can be stopped only when it is reset (iwdg_in_rst asserted).

As shown in Figure 553, when the refresh command is executed, one period of presc_ck later, the IWDCNT is reloaded with the content of RL[11:0].

**Figure 553. Reset timing due to timeout** (described)

IWDCNT is plotted against time, with levels 0xFFF, RL[11:0] and WIN[11:0] marked. A write of 0xAAAA into IWDG_KR causes IWDCNT to jump to RL[11:0] one Tpresc_ck later. IWDCNT then decreases. While IWDCNT is above WIN[11:0]+1 the region is labelled "Refresh not allowed(1)" (shaded); after it crosses WIN[11:0]+1 the region is "Refresh allowed". With no further refresh, IWDCNT reaches 2, 1, 0 (enlarged inset: each step is one Tpresc_ck); when it reaches 0, iwdg_out_rst pulses high, then iwdg_in_rst is asserted (driven low in the drawing) and IWDCNT returns to 0xFFF.

Notes:

1. If window option activated.

If the IWDG is not refreshed before the IWDCNT reaches 1, the IWDG generates a reset (iwdg_out_rst is asserted). In return, the RCC resets the IWDG (assertion of iwdg_in_rst) to clear the reset source.

### 37.4.4 Window option

The IWDG can also work as a window watchdog, by setting the appropriate window in the IWDG window register (IWDG_WINR).

If the reload operation is performed while the counter is greater than WIN[11:0] + 1, a reset is generated. WIN[11:0] is located in the IWDG window register (IWDG_WINR). As shown in Figure 554, the reset is generated one period of presc_ck after the unexpected refresh command.

The default value of the IWDG window register (IWDG_WINR) is 0x0000 0FFF, so, if not updated, the window option is disabled.

As soon as the window value changes, the down-counter (IWDCNT) is reloaded with the RL[11:0] value, to ease the estimation for where the next refresh must take place.

**Figure 554. Reset timing due to refresh in the not allowed area** (described)

IWDCNT (levels 0xFFF, RL[11:0], WIN[11:0] + 1) is plotted against time. A first 0xAAAA write into IWDG_KR reloads IWDCNT to RL[11:0] one Tpresc_ck later, entering the shaded "Refresh not allowed" region (IWDCNT above WIN[11:0] + 1). A second 0xAAAA write while still in that region causes, one Tpresc_ck later, an iwdg_out_rst pulse followed by assertion of iwdg_in_rst, and IWDCNT returns to 0xFFF.

**Configuring the IWDG when the window option is enabled**

1. Enable the IWDG by writing 0x0000 CCCC in the IWDG key register (IWDG_KR).
2. Enable register access by writing 0x0000 5555 in the IWDG key register (IWDG_KR).
3. Write the IWDG prescaler by programming IWDG prescaler register (IWDG_PR).
4. Write the IWDG reload register (IWDG_RLR).
5. If needed, enable the early wake-up interrupt, and program the early wake-up comparator, by writing the proper values into the IWDG early wake-up interrupt register (IWDG_EWCR).
6. Write to the IWDG window register (IWDG_WINR). This automatically reloads the IWDCNT down-counter with the RL[11:0] value.
7. Wait for the registers to be updated (IWDG_SR = 0x0000 0000).
8. Write 0x0000 0000 into IWDG key register (IWDG_KR) to write-protect registers.

Note: Step 7 can be skipped if the application does not intend to disable the APB clock after the completion of this sequence.

**Configuring the IWDG when the window option is disabled**

When the window option it is not used, the IWDG can be configured as follows:

1. Enable the IWDG by writing 0x0000 CCCC in the IWDG key register (IWDG_KR).
2. Enable register access by writing 0x0000 5555 in the IWDG key register (IWDG_KR).
3. Write the prescaler by programming the IWDG prescaler register (IWDG_PR).
4. Write the IWDG reload register (IWDG_RLR).
5. If needed, enable the early wake-up interrupt, and program the early wake-up comparator, by writing the proper values into the IWDG early wake-up interrupt register (IWDG_EWCR).
6. Wait for the registers to be updated (IWDG_SR = 0x0000 0000).
7. Refresh the counter with RL[11:0] value, and write-protect registers by writing 0x0000 AAAA into IWDG key register (IWDG_KR).

The figure below shows a sequence example changing the prescaler, the reload value, and then performing a refresh.

**Figure 555. Changing PR, RL, and performing a refresh(1)** (described)

Timeline with iwdg_ker_ck, the WDGCNT counter, PVU, RVU, the prescaler, RL[11:0] and CPU activity:

- CPU writes 0x5555 into IWDG_KR (registers unlock), then writes 1 into IWDG_PR. PVU goes high for TDPVU. The counter keeps decrementing at /4 (N, ..., N-k); after PVU falls the prescaler becomes /8 from N-k-1 onwards.
- CPU writes M into RL[11:0]. RVU goes high for TDRVU; RL[11:0] changes from P to M when RVU falls. The counter continues (N-k-t, N-k-t-1, ...).
- CPU writes 0xAAAA into IWDG_KR (refresh + registers lock). After TDRefresh the counter is loaded with M. The interval just before the load is marked "Refresh ignored region".

Notes:

1. Refer to Table 381: IWDG delays versus actions for details on timing values.

Note: When the new prescaler value is accepted by the IWDG (falling edge of PVU), the new division ratio is effective when the current division sequence is completed (N-k in the drawing).

Note: The timeout delay between the refresh (write 0xAAAA into IWDG_KR) and the watchdog reset is increased by TDRefresh.
If a refresh command is sent while the previous refresh command is not yet completed, this last refresh command is ignored.

**Updating the window comparator**

It is possible to update the window comparator when the IWDG is already running. The IWDCNT is reloaded as well. The following sequence can be performed to update the window comparator:

1. Enable register access by writing 0x0000 5555 in the IWDG key register (IWDG_KR).
2. Write to the IWDG window register (IWDG_WINR). This automatically reloads the IWDCNT down-counter with RL[11:0] value.
3. Wait for WVU = 0
4. Lock registers by writing IWDG_KR to 0x0000 0000

Step 3 can be skipped if the application does not intend to disable the APB clock after the completion of this sequence.

Figure 556 shows this sequence. As soon as the IWDG_WINR register is written, the WVU flag goes high for TDwvu. After a window comparator update, a refresh is automatically performed. The refresh is effective in the worst case, on the next prescaler clock active edge after the falling edge of WVU (TDRefAuto)

**Figure 556. Window comparator update(1)** (described)

CPU writes 0x5555 into IWDG_KR (registers unlock), then writes 800 into IWDG_WINR (WIN[11:0] changes from 500 to 800). WVU is high for TDWVU while the counter runs N, ..., N-k. After WVU falls, within TDRefAuto the counter is reloaded to M (= RL[11:0]) and continues M-1, M-2, ...; the interval just before the reload is a "Refresh ignored region". CPU then writes 0x0000 into IWDG_KR (registers lock).

Notes:

1. Refer to Table 381: IWDG delays versus actions for details on timing values.

### 37.4.5 Debug

When the processor enters into Debug mode (core halted), the IWDCNT down-counter either continues to work normally or stops, depending on debug capability of the product. Refer to Section 37.3 for details on the capabilities of this product.

*Digest note:* per Table 380 this product supports freezing the IWDG in Debug mode, controlled by DBG_IWDG_STOP (DBGMCU_APB1LFZR bit 12 per the CMSIS header).

### 37.4.6 Register access protection

Write accesses to IWDG prescaler register (IWDG_PR), IWDG reload register (IWDG_RLR), IWDG early wake-up interrupt register (IWDG_EWCR) and IWDG window register (IWDG_WINR) are protected. To modify them, first write 0x0000 5555 in the IWDG key register (IWDG_KR). A write access to this register with a different value breaks the sequence and register access is protected again. This is the case of the reload operation (writing 0x0000 AAAA).

A status register is available to indicate that an update of the prescaler or the down-counter reload value or the window value is ongoing.

## 37.5 IWDG low power modes

Depending on option bytes configuration, the IWDG can continue counting or not during the low power modes. Refer to Section 37.3 for details.

**Table 383. Effect of low power modes on IWDG**

| Mode | Description |
|---|---|
| Sleep | No effect. IWDG interrupts cause the device to exit from the mode. |
| Stop | The IWDG remains active or not, depending on option bytes configuration. Refer to Section 37.3 for details. IWDG interrupts cause the device exit the Stop mode. |
| Standby | The IWDG remains active or not, depending on option bytes configuration. Refer to Section 37.3 for details. IWDG interrupts do not make the device to exit from Standby mode. |

## 37.6 IWDG interrupts

The IWDG offers the possibility to generate an early interrupt depending on the value of the down-counter. The early interrupt is enabled by setting the EWIE bit of the IWDG early wake-up interrupt register (IWDG_EWCR) to 1.

A comparator value (EWIT[11:0]) allows the application to define the position where the early interrupt must be generated.

When the IWDCNT down-counter reaches the value of EWIT[11:0] - 1, the iwdg_wkup is activated, making it possible for the system to exit from low power modes, if needed.

When the APB clock is available, the iwdg_it is activated as well.

In addition, the flag EWIF of the IWDG status register (IWDG_SR) is set to 1.

The EWI interrupt is acknowledged by writing 1 to the EWIC bit in the IWDG interrupt clear register (IWDG_ICR).

Writing into the IWDG_EWCR register also triggers a refresh of the down-counter (IWDCNT) with the reload value RL[11:0].

**Figure 557. Independent watchdog interrupt timing diagram** (described)

IWDCNT decreases over time; when it crosses EWIT[11:0] (point labelled "IWDCNT = EWIT - 1"), iwdg_wkup_it goes high. When pclk becomes active ("pclk active"), iwdg_it also goes high. An APB write access "Writing EWIC to '1'" clears both iwdg_wkup_it and iwdg_it.

The early wake-up interrupt (EWI) can be used if specific safety operations or data logging must be performed before the watchdog reset is generated.

**Changing the early wake-up comparator value**

It is possible to change the early wake-up comparator value or to enable/disable the interrupt generation at any time, by performing the following sequence:

1. Enable register access by writing 0x0000 5555 in the IWDG key register (IWDG_KR).
2. Enable or disable the early wake-up interrupt, and/or program the early wake-up comparator, by writing the proper values into the IWDG early wake-up interrupt register (IWDG_EWCR).
3. Wait for EWU = 0, EWU is located into the IWDG status register (IWDG_SR).
4. Write-protect registers by writing 0x0000 0000 to IWDG key register (IWDG_KR).

Step 3 can be skipped if the application does not intend to disable the APB clock after the completion of this sequence.

Figure 558 shows this sequence. During the early wake-up comparator update operation the flag EWU remains to 1 for TDewu. A refresh is automatically performed. The refresh is effective on the worst case, on the next prescaler clock active edge after the falling edge of EWU (TDRefAuto).

**Figure 558. Early wake-up comparator update(1)** (described)

CPU writes 0x5555 into IWDG_KR (registers unlock), then writes 300 into EWIT[11:0] (EWIT changes from 500 to 300). EWU is high for TDEWU while the counter runs N, ..., N-k. After EWU falls, within TDRefAuto the counter is reloaded to M (= RL[11:0]) and continues M-1, M-2, ...; the interval just before the reload is a "Refresh ignored region". CPU then writes 0x0000 into IWDG_KR (registers lock).

Notes:

1. Refer to Table 381: IWDG delays versus actions for details on timing values.

Table 384 summarizes the IWDG interrupt request.

**Table 384. IWDG interrupt request**

| Interrupt event | Event flag | Interrupt clear method | Interrupt enable control bit | Activated interrupt iwdg_it | Activated interrupt iwdg_wkup_it |
|---|---|---|---|---|---|
| IWDCNT reaches EWIT value | EWIF | Writing EWIC to 1 | EWIE | Y(1) | Y(2) |

Notes:

1. Generated when a clock is present on iwdg_pclk input.
2. Generated when a clock is present on iwdg_ker_ck input.

## 37.7 IWDG registers

Refer to Section 1.2 on page 85 for a list of abbreviations used in register descriptions.

The peripheral registers can be accessed by half-words (16-bit) or words (32-bit).

Most of the registers located into the register interface are shadowed into the VDD voltage domain. When the iwdg_in_rst is asserted, the watchdog logic and the shadow registers located into the VDD voltage domain are reset.

When the application reads back a watchdog register, the hardware transfers the value of the corresponding shadow register to the register interface.

When the application writes a watchdog register, the hardware updates the corresponding shadow register.

*Digest note:* the CMSIS header (stm32c552xx.h) defines IWDG_BASE = APB1PERIPH_BASE + 0x3000 = 0x4000 3000, with IWDG_TypeDef KR (0x00), PR (0x04), RLR (0x08), SR (0x0C), WINR (0x10), EWCR (0x14), ICR (0x18).

### 37.7.1 IWDG key register (IWDG_KR)

Address offset: 0x00. Reset value: 0x0000 0000.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bits 15:0 KEY[15:0]** (w): Key value (write only, read 0x0000)
  These bits can be used for several functions, depending upon the value written by the application:
  - 0xAAAA: reloads the RL[11:0] value into the IWDCNT down-counter (watchdog refresh), and write-protects registers. This value must be written by software at regular intervals, otherwise the watchdog generates a reset when the counter reaches 0.
  - 0x5555: enables write-accesses to the registers.
  - 0xCCCC: enables the watchdog (except if the hardware watchdog option is selected) and write-protects registers.
  - values different from 0x5555: write-protects registers.

  Note that only IWDG_PR, IWDG_RLR, IWDG_EWCR and IWDG_WINR registers have a write-protection mechanism.

### 37.7.2 IWDG prescaler register (IWDG_PR)

Address offset: 0x04. Reset value: 0x0000 0000.

- **Bits 31:4** Reserved, must be kept at reset value.
- **Bits 3:0 PR[3:0]** (rw): Prescaler divider
  These bits are write access protected, see Section 37.4.6. They are written by software to select the prescaler divider feeding the counter clock. PVU bit of the IWDG status register (IWDG_SR) must be reset to be able to change the prescaler divider.
  - 0000: divider / 4
  - 0001: divider / 8
  - 0010: divider / 16
  - 0011: divider / 32
  - 0100: divider / 64
  - 0101: divider / 128
  - 0110: divider / 256
  - 0111: divider / 512
  - Others: divider / 1024

  Note: Reading this register returns the prescaler value from the VDD voltage domain. This value may not be up to date/valid if a write operation to this register is ongoing. For this reason the value read from this register is valid only when the PVU bit in the IWDG status register (IWDG_SR) is reset.

*Digest note:* the STM32C55xxx datasheet digest (Table 61, IWDG timeouts at 32 kHz LSI) lists only PR[2:0] values with "/256 for 6 or 7" and a maximum of 32768 ms; this RM gives a 4-bit PR with /512 (0111) and /1024 (others). Timeout = 4 * 2^PR * (RL + 1) / f_LSI for PR <= 7; e.g. PR = 0, RL = 0xFFF at 32 kHz gives 512 ms (matches the datasheet maximum for /4).

### 37.7.3 IWDG reload register (IWDG_RLR)

Address offset: 0x08. Reset value: 0x0000 0FFF.

- **Bits 31:12** Reserved, must be kept at reset value.
- **Bits 11:0 RL[11:0]** (rw): Watchdog counter reload value
  These bits are write access protected, see Section 37.4.6. They are written by software to define the value to be loaded in the watchdog counter each time the value 0xAAAA is written in the IWDG key register (IWDG_KR). The watchdog counter counts down from this value. The timeout period is a function of this value and the prescaler.clock. It is not recommended to set RL[11:0] to a value lower than 2.
  The RVU bit in the IWDG status register (IWDG_SR) must be reset to be able to change the reload value.

  Note: Reading this register returns the reload value from the VDD voltage domain. This value may not be up to date/valid if a write operation to this register is ongoing, hence the value read from this register is valid only when the RVU bit in the IWDG status register (IWDG_SR) is reset.

### 37.7.4 IWDG status register (IWDG_SR)

Address offset: 0x0C. Reset value: 0x0000 0000 (0xFFFF FEFF).

This register contains various status flags. Note that the mask value between parenthesis means that the reset value of ONF bit is not defined. When the IWDG is configured in software mode, the reset value of ONF bit is 0, when the IWDG is configured in hardware mode, the reset value of ONF bit is 1.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bit 15 EWIF** (r): Watchdog early interrupt flag
  This bit is set to '1' by hardware in order to indicate that an early interrupt is pending. This bit must be cleared by the software by writing the bit EWIC of IWDG_ICR register to '1'.
- **Bits 14:9** Reserved, must be kept at reset value.
- **Bit 8 ONF** (r): Watchdog enable status bit
  Set to '1' by hardware as soon as the IWDG is started. In software mode, it remains to '1' until the IWDG is reset. In hardware mode, this bit is always set to '1'.
  - 0: The IWDG is not activated
  - 1: The IWDG is activated and needs to be refreshed regularly by the application
- **Bits 7:4** Reserved, must be kept at reset value.
- **Bit 3 EWU** (r): Watchdog interrupt comparator value update
  This bit is set by hardware to indicate that an update of the interrupt comparator value (EWIT[11:0]) or an update of the EWIE is ongoing. It is reset by hardware when the update operation is completed in the VDD voltage domain. Refer to Table 381: IWDG delays versus actions for delay values.
  The EWIT[11:0] and EWIE fields can be updated only when EWU bit is reset.
- **Bit 2 WVU** (r): Watchdog counter window value update
  This bit is set by hardware to indicate that an update of the window value is ongoing. It is reset by hardware when the reload value update operation is completed in the VDD voltage domain. Refer to Table 381: IWDG delays versus actions for delay values.
  The window value can be updated only when WVU bit is reset.
  This bit is generated only if generic "window" = 1.
- **Bit 1 RVU** (r): Watchdog counter reload value update
  This bit is set by hardware to indicate that an update of the reload value is ongoing. It is reset by hardware when the reload value update operation is completed in the VDD voltage domain. Refer to Table 381: IWDG delays versus actions for delay values.
  The reload value can be updated only when RVU bit is reset.
- **Bit 0 PVU** (r): Watchdog prescaler value update
  This bit is set by hardware to indicate that an update of the prescaler value is ongoing. It is reset by hardware when the prescaler update operation is completed in the VDD voltage domain. Refer to Table 381: IWDG delays versus actions for delay values.
  The prescaler value can be updated only when PVU bit is reset.

Note: If several reload, prescaler, early interrupt position or window values are used by the application, it is mandatory to wait until RVU bit is reset before changing the reload value, to wait until PVU bit is reset before changing the prescaler value, to wait until WVU bit is reset before changing the window value, and to wait until EWU bit is reset before changing the early interrupt position value. After updating the prescaler and/or the reload/window/early interrupt value, it is not necessary to wait until RVU or PVU or WVU or EWU is reset before continuing code execution, except in case of low power mode entry.

*Digest note:* the CMSIS header has IWDG_SR_EWIF_Pos = 15 (matching the RM), but the mask comment reads 0x00004000; the actual macro value is 0x00008000. Similarly IWDG_EWCR_EWIE_Msk is (1 << 15) with a stray comment of 0x00000FFF. In software mode, ONF = 1 can be used to detect that the IWDG was already started (for example by a bootloader) before the application runs.

### 37.7.5 IWDG window register (IWDG_WINR)

Address offset: 0x10. Reset value: 0x0000 0FFF.

- **Bits 31:12** Reserved, must be kept at reset value.
- **Bits 11:0 WIN[11:0]** (rw): Watchdog counter window value
  These bits are write access protected, see Section 37.4.6. They contain the high limit of the window value to be compared with the downcounter.
  To prevent a reset, the IWDCNT downcounter must be reloaded when its value is lower than WIN[11:0] + 1 and greater than 1.
  The WVU bit in the IWDG status register (IWDG_SR) must be reset to be able to change the reload value.

  Note: Reading this register returns the reload value from the VDD voltage domain. This value may not be valid if a write operation to this register is ongoing. For this reason the value read from this register is valid only when the WVU bit in the IWDG status register (IWDG_SR) is reset.

### 37.7.6 IWDG early wake-up interrupt register (IWDG_EWCR)

Address offset: 0x14. Reset value: 0x0000 0000.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bit 15 EWIE** (rw): Watchdog early interrupt enable
  Set and reset by software.
  - 0: The early interrupt interface is disabled.
  - 1: The early interrupt interface is enabled.

  The EWU bit in the IWDG status register (IWDG_SR) must be reset to be able to change the value of this bit.
- **Bits 14:12** Reserved, must be kept at reset value.
- **Bits 11:0 EWIT[11:0]** (rw): Watchdog counter early wake-up interrupt value
  These bits are write access protected (see Section 37.4.6). They are written by software to define at which position of the IWDCNT down-counter the early wake-up interrupt must be generated. The early interrupt is generated when the IWDCNT is lower or equal to EWIT[11:0] - 1.
  EWIT[11:0] must be bigger than 1.
  An interrupt is generated only if EWIE = 1.
  The EWU bit in the IWDG status register (IWDG_SR) must be reset to be able to change the reload value.

  Note: Reading this register returns the Early wake-up comparator value and the Interrupt enable bit from the VDD voltage domain. This value may not be up to date/valid if a write operation to this register is ongoing, hence the value read from this register is valid only when the EWU bit in the IWDG status register (IWDG_SR) is reset.

### 37.7.7 IWDG interrupt clear register (IWDG_ICR)

Address offset: 0x18. Reset value: 0x0000 0000.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bit 15 EWIC** (rw): Watchdog early interrupt acknowledge
  The software must write a 1 into this bit in order to acknowledge the early wake-up interrupt and to clear the EWIF flag. Writing 0 has not effect, reading this flag returns a 0.
- **Bits 14:0** Reserved, must be kept at reset value.

### 37.7.8 IWDG register map

**Table 385. IWDG register map and reset values**

| Offset | Register | Reset value | Fields (bit positions) |
|---|---|---|---|
| 0x00 | IWDG_KR | 0x0000 0000 | 31:16 Res.; KEY[15:0] (15:0) |
| 0x04 | IWDG_PR | 0x0000 0000 | 31:4 Res.; PR[3:0] (3:0) |
| 0x08 | IWDG_RLR | 0x0000 0FFF | 31:12 Res.; RL[11:0] (11:0) |
| 0x0C | IWDG_SR | 0x0000 0000, ONF = x | 31:16 Res.; EWIF (15); 14:9 Res.; ONF (8); 7:4 Res.; EWU (3); WVU (2); RVU (1); PVU (0) |
| 0x10 | IWDG_WINR | 0x0000 0FFF | 31:12 Res.; WIN[11:0] (11:0) |
| 0x14 | IWDG_EWCR | 0x0000 0000 | 31:16 Res.; EWIE (15); 14:12 Res.; EWIT[11:0] (11:0) |
| 0x18 | IWDG_ICR | 0x0000 0000 | 31:16 Res.; EWIC (15); 14:0 Res. |

Refer to Section 2.2: Memory organization for the register boundary addresses.

*Digest note:* all IWDG bit positions above match the CMSIS header stm32c552xx.h.
