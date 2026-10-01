# RM0522 Chapter 5: RAMs configuration controller (RAMCFG)

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 114–125.

## 5.1 RAMCFG introduction

The RAMCFG configures the features of the internal SRAMs (SRAM1 and SRAM2).

## 5.2 RAMCFG main features

The internal SRAM supports some of the features listed hereafter, configured in RAMCFG:

- Error code correction (ECC):
  - Single-error detection and correction with interrupt generation
  - Double-error detection with interrupt or NMI generation
  - Status with failing address
- Write protection (1-Kbyte granularity)
- SRAM software erase

## 5.3 RAMCFG functional description

### 5.3.1 Internal SRAMs features

Two SRAMs are embedded in the device, each with specific features:

- SRAM1 and SRAM2 are the main SRAMs (see Table 15), made of several blocks that can be powered down in Stop mode to reduce consumption
- SRAM2 is erased when a system reset occurs if the SRAM2_RST option bit is selected in the flash memory user option bytes. SRAM1 is erased when a system reset occurs if the SRAM1_RST option bit is selected in the flash memory user option bytes. Refer to Section 6: Embedded flash memory (FLASH) for more details.
- SRAM2 is protected by the tamper detection circuit, and are erased by hardware in case of tamper detection. They are also erased by hardware in case of a backup domain reset. Refer to Section 40: Tamper and backup registers (TAMP) for more details.
- The RAMCFG embeds registers related to the internal SRAMs ECC, write protection, and software erase.

*Digest note:* "Selected" here means the option bit is programmed to 0. Per RM Section 6 (FLASH_OPTSR2_CUR/PRG, outside this page range): SRAM1_RST (FLASH_OPTSR2 bit 0) and SRAM2_RST (bit 1): 0 = SRAMx erased when a system reset occurs, 1 = SRAMx not erased; the user-default (factory) value of both is 1 (not erased). Section 6 also notes "SRAM erase is triggered by option-byte change operation, when enabling this feature." If option-byte loading hits a double ECC error, FLASH_OPTSR2 falls back to 0x0000 0010, which selects erase-on-reset for both SRAMs. Chapter 3 Table 12 additionally lists SRAM2 as always erased on POR, erased on confirmed tamper, and blocked on potential tamper.

**Table 14. SRAM density (Kbytes)**

| SRAM feature | SRAM1 | SRAM2 |
|---|---|---|
| STM32C53x/542 | 32 | 32 |
| STM32C55x/562 | 64 | 64 |
| STM32C59x/5A3 | 128 | 128 |

The table below summarizes the features supported by each internal SRAM

**Table 15. Internal SRAMs features**

| SRAM feature | SRAM1 | SRAM2 |
|---|---|---|
| Optional retention in Standby mode | - | - |
| Optional retention in Stop mode | X | X |
| Erased with RDP level regression | X | X |
| Optionally erased with tamper detection | - | X |
| Optionally erased with system reset | X | X |
| Software erase | X | X |
| ECC | - | X |
| Write protection | - | X |

### 5.3.2 Error code correction (SRAM2)

The ECC is supported by SRAM2 when enabled with the SRAM2_ECC user option bits. Refer to Section 6: Embedded flash memory (FLASH) for more details.

*Digest note:* Per RM Section 6 (FLASH_OPTSR2 bit 4, outside this page range), SRAM2_ECC is an active-low disable: 0 = SRAM2 ECC check enabled, 1 = SRAM2 ECC check disabled. The user-default (factory) value is 1, so SRAM2 ECC is disabled on a factory-fresh device.

Seven ECC bits are added per 32 bits of SRAM, allowing 2-bit error detection and 1-bit error correction on memory read access.

As the ECC is calculated and checked for a 32-bit word, byte and half-word write accesses are managed by the SRAM interface by first reading the whole word, then write the word again with the new byte/half-word value. ECC double errors are also detected during these bytes or half-word AHB write accesses (read/modify/write done by interface). The byte or half-word write access latency is two AHB clock cycles.

Caution: In case of a byte or half-word write on SRAM with ECC, the read/modify/write operation is done in a buffer. The buffer content is written into the SRAM two AHB clock cycles after the SRAM AHB is released (when the SRAM is no more accessed).

#### Single and double ECC errors

When a single error is detected, it is automatically corrected and the SEDC/CSEDC bits are set in RAMCFG_MxISR and RAMCFG_MxICR respectively. An interrupt is generated if enabled by the SEIE bit in RAMCFG_MxIER. The failing address is stored in RAMCFG_MxSEAR if the ALE bit is set in RAMCFG_MxCR.

Caution: Single errors cannot be detected when the SEDC bit is set.

When a double error is detected, the DED and CDED bits are set in RAMCFG_MxISR and RAMCFG_MxICR respectively. An interrupt or NMI is generated if enabled by the DEIE or ECCNMI bit in RAMCFG_MxIER. The failing address is stored in RAMCFG_MxDEAR if the ALE bit is set in RAMCFG_MxCR.

Caution: Double errors cannot be detected when the DED bit is set.

#### SRAM2 with ECC memory map

When the ECC is enabled for SRAM2, the full SRAM2 has ECC.

The figure below shows the SRAM areas, when ECC is enabled for both SRAM1 and SRAM2.

**Table 16. SRAM with ECC memory map**

| Product | SRAM | Address over C-bus | Address over S-bus | SRAM size | ECC |
|---|---|---|---|---|---|
| STM32C53x/542 | SRAM1 | 0x0A00 0000 - 0x0A00 7FFF | 0x2000 0000 - 0x2000 7FFF | 32 Kbytes | - |
| STM32C53x/542 | SRAM2 | 0x0A00 8000 - 0x0A00 FFFF | 0x2000 8000 - 0x2000 FFFF | 32 Kbytes | ECC |
| STM32C55x/562 | SRAM1 | 0x0A00 0000 - 0x0A00 FFFF | 0x2000 0000 - 0x2000 FFFF | 64 Kbytes | - |
| STM32C55x/562 | SRAM2 | 0x0A01 0000 - 0x0A01 FFFF | 0x2001 0000 - 0x2001 FFFF | 64 Kbytes | ECC |
| STM32C59x/5A3 | SRAM1 | 0x0A00 0000 - 0x0A01 FFFF | 0x2000 0000 - 0x2001 FFFF | 128 Kbytes | - |
| STM32C59x/5A3 | SRAM2 | 0x0A00 0002 - 0x0A03 FFFF | 0x2002 0000 - 0x2003 FFFF | 128 Kbytes | ECC |

*Digest note:* The source text says "figure" and "both SRAM1 and SRAM2", but it is Table 16 and only SRAM2 has ECC (Table 15); the ECC column has no header in the source and is marked only on the SRAM2 rows. The STM32C59x/5A3 SRAM2 C-bus start address is printed "0x0A00 0002"; Chapter 2 Figure 4 gives 0x0A02 0000 [unclear in source: 0x0A00 0002 is presumably a typo for 0x0A02 0000].

When ECC is enabled by user option bits, the ECCE bit is automatically set after system reset in the related RAMCFG_MxCR.

The ECC can be deactivated by executing the following software sequence:

1. Write 0xAE in RAMCFG_MxECCKEYR.
2. Write 0x75 in RAMCFG_MxECCKEYR.
3. Write 0 in RAMCFG_MxCR.

*Digest note:* Only RAMCFG_M2ECCKEYR exists (offset 0x064); SRAM1 has no ECC.

#### Testing ECC mechanism

To test the ECC mechanism, 1 or 2 bits by word for single- or double-error test respectively. The procedure to check ECC is the following:

1. On an erased memory, write data with ECC ON.
2. Disable ECC.
3. Write the same data with 1- or 2-bit modification (for single or double error test respectively).
4. Enable ECC.
5. Read the data. Enabled interrupt is generated because of a single or double error.

*Digest note:* The first sentence of this subsection is incomplete in the source (no verb); reproduced as printed.

### 5.3.3 Write protection (SRAM2)

SRAM2 is made up of 1-Kbyte pages, each of which can be write-protected by setting its corresponding PxWP bit in RAMCFG_M2WPR1, RAMCFG_M2WPR2, RAMCFG_M2WPR3(a), and RAMCFG_M2WPR4(a).

Notes:

a. This register is available only on STM32C59x/5A3 devices. If not present, consider this register as reserved, and keep its bits at reset value.

*Digest note:* On STM32C551/C552, SRAM2 is 64 Kbytes = 64 pages, covered by RAMCFG_M2WPR1 (pages 0 to 31) and RAMCFG_M2WPR2 (pages 32 to 63). Page y starts at 0x2001 0000 + y x 0x400 (S-bus). The C552 CMSIS header has no WPR3/WPR4 members.

### 5.3.4 Software erase

SRAM erase can be requested by executing this software sequence:

1. Write 0xCA in RAMCFG_MxERKEYR.
2. Write 0x53 in RAMCFG_MxERKEYR.
3. Write 1 to the SRAMER bit in RAMCFG_MxCR.

SRAMBUSY flag is set in the related SRAM interrupt status register as long as the erase is ongoing.

The total duration of each SRAM erase is N AHB clock cycles, where N is the size of the SRAM in 32-bit words.

If the SRAM is read or written while an erase is ongoing, wait states are inserted on the AHB bus until the end of the erase operation.

## 5.4 RAMCFG low-power modes

**Table 17. Effect of low-power modes on RAMCFG**

| Mode | Description |
|---|---|
| Sleep | No effect. RAMCFG interrupts cause the device to exit Sleep mode. |
| Stop | The content of RAMCFG registers is kept. |
| Standby | The RAMCFG peripheral is powered down and must be reinitialized after exiting Standby mode. |

## 5.5 RAMCFG interrupts

The table below gives the list of RAMCFG interrupt requests.

**Table 18. RAMCFG interrupt requests**

| Interrupt acronym | Interrupt event | Event flag | Enable control bit | Interrupt clear method | Exit Sleep mode | Exit Stop mode | Exit Standby mode |
|---|---|---|---|---|---|---|---|
| RAMCFG | ECC single-error detection and correction | SEDC | SEIE | Write 1 in CSEDC | Yes | No | No |
| RAMCFG | ECC double-error detection | DED | DEIE = 1 and ECCNMI = 0 | Write 1 in CDED | Yes | No | No |
| NMI | ECC double-error detection | DED | ECCNMI | Write 1 in CDED | Yes | No | No |

*Digest note:* The ST CMSIS header (stm32c552xx.h) defines RAMCFG_IRQn = 4 ("RAM configuration global interrupt").

## 5.6 RAMCFG registers

In the registers described below, x refers to:

- SRAM1 when x = 1
- SRAM2 when x = 2

*Digest note:* The ST CMSIS header models RAMCFG as two instances of one RAMCFG_TypeDef: RAMCFG_SRAM1 at 0x4002 6000 and RAMCFG_SRAM2 at 0x4002 6040 (RAMCFG_BASE + 0x40), with members CR (0x00), IER (0x04), ISR (0x08), SEAR (0x0C), DEAR (0x10), ICR (0x14), WPR1 (0x18), WPR2 (0x1C), ECCKEYR (0x24), ERKEYR (0x28). This matches the RM offsets below (block base + 0x40 x (x - 1)). Bit positions in the header (RAMCFG_CR_ECCE 0, ALE 4, SRAMER 8; RAMCFG_IER_SEIE 0, DEIE 1, ECCNMI 3; RAMCFG_ISR_SEDC 0, DED 1, SRAMBUSY 8; RAMCFG_ICR_CSEDC 0, CDED 1) agree with the RM.

### 5.6.1 RAMCFG memory x control register (RAMCFG_MxCR)

Address offset: 0x000 + 0x40 * (x - 1), (x = 1, 2). Reset value: 0x0000 000X. ECCE reset value depends on the ECC enable user option bit.

- **Bits 31:9** Reserved, must be kept at reset value.
- **Bit 8 SRAMER** (rs): SRAM erase. This bit can be set by software only after writing the unlock sequence in the ERASEKEY field of the RAMCFG_MxERKEYR register. Setting this bit starts the SRAM erase. This bit is automatically cleared by hardware at the end of the erase operation.
  - 0: No erase operation ongoing
  - 1: Erase operation ongoing
- **Bits 7:5** Reserved, must be kept at reset value.
- **Bit 4 ALE** (rw): Address latch enable
  - 0: Failing address not stored in the SRAMx ECC single/double error address registers
  - 1: Failing address stored in the SRAMx ECC single/double error address registers
  - Note: This bit is reserved and must be kept at reset value in SRAM1 control register.
- **Bits 3:1** Reserved, must be kept at reset value.
- **Bit 0 ECCE** (rw): ECC enable. This bit reset value is defined by the user option bit configuration. When set, it can be cleared by software only after writing the unlock sequence in the RAMCFG_MxECCKEYR register.
  - 0: ECC disabled
  - 1: ECC enabled
  - Note: This bit is reserved and must be kept at reset value in SRAM1 control register.

### 5.6.2 RAMCFG memory x interrupt status register (RAMCFG_MxISR)

Address offset: 0x008 + 0x40 * (x - 1), (x = 1, 2). Reset value: 0x0000 0000.

- **Bits 31:9** Reserved, must be kept at reset value.
- **Bit 8 SRAMBUSY** (r): SRAM busy with erase operation
  - 0: No erase operation ongoing
  - 1: Erase operation ongoing
  - Note: Depending on the SRAM, the erase operation can be performed due to software request, system reset if the option bit is enabled, tamper detection or RDP level regression. Refer to Table 15: Internal SRAMs features.
- **Bits 7:2** Reserved, must be kept at reset value.
- **Bit 1 DED** (r): ECC double error detected
  - 0: No double error
  - 1: Double error detected
  - Note: This bit is reserved and must be kept at reset value in SRAM1 interrupt status register.
- **Bit 0 SEDC** (r): ECC single error detected and corrected
  - 0: No single error
  - 1: Single error detected and corrected
  - Note: This bit is reserved and must be kept at reset value in SRAM1 interrupt status register.

### 5.6.3 RAMCFG memory x erase key register (RAMCFG_MxERKEYR)

Address offset: 0x028 + 0x40 * (x - 1), (x = 1, 2). Reset value: 0x0000 0000.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:0 ERASEKEY[7:0]** (w): Erase write protection key. The following steps are required to unlock the write protection of SRAMER in RAMCFG_MxCR.
  1. Write 0xCA into ERASEKEY[7:0].
  2. Write 0x53 into ERASEKEY[7:0].
  - Note: Writing a wrong key reactivates the write protection.

### 5.6.4 RAMCFG memory 2 interrupt enable register (RAMCFG_M2IER)

Address offset: 0x044. Reset value: 0x0000 0000.

- **Bits 31:4** Reserved, must be kept at reset value.
- **Bit 3 ECCNMI** (rs): Double error NMI. This bit is set by software and cleared only by a global RAMCFG reset.
  - 0: NMI not generated in case of ECC double error
  - 1: NMI generated in case of ECC double error
  - Note: if ECCNMI is set, the RAMCFG maskable interrupt is not generated whatever DEIE bit value.
- **Bit 2** Reserved, must be kept at reset value.
- **Bit 1 DEIE** (rw): ECC double error interrupt enable
  - 0: Double error interrupt disabled
  - 1: Double error interrupt enabled
- **Bit 0 SEIE** (rw): ECC single error interrupt enable
  - 0: Single error interrupt disabled
  - 1: Single error interrupt enabled

### 5.6.5 RAMCFG memory 2 ECC single error address register (RAMCFG_M2SEAR)

Address offset: 0x04C. Reset value: 0x0000 0000.

- **Bits 31:0 ESEA[31:0]** (r): ECC single error address. When the ALE bit is set in RAMCFG_M2CR, this bitfield is updated with the address corresponding to the ECC single error.

### 5.6.6 RAMCFG memory 2 ECC double error address register (RAMCFG_M2DEAR)

Address offset: 0x050. Reset value: 0x0000 0000.

- **Bits 31:0 EDEA[31:0]** (r): ECC double error address. When the ALE bit is set in RAMCFG_M2CR, this bitfield is updated with the address corresponding to the ECC double error.

### 5.6.7 RAMCFG memory 2 interrupt clear register (RAMCFG_M2ICR)

Address offset: 0x054. Reset value: 0x0000 0000.

- **Bits 31:2** Reserved, must be kept at reset value.
- **Bit 1 CDED** (rw): Clear ECC double error detected. Writing 1 to this flag clears the DED bit in RAMCFG_M2ISR. Reading this flag returns the DED value.
- **Bit 0 CSEDC** (rw): Clear ECC single error detected and corrected. Writing 1 to this flag clears the SEDC bit in RAMCFG_M2ISR. Reading this flag returns the SEDC value.

### 5.6.8 RAMCFG memory 2 write protection register 1 (RAMCFG_M2WPR1)

Address offset: 0x058. Reset value: 0x0000 0000.

- **Bits 31:0 PyWP** (rs): SRAM2 1-Kbyte page y write protection (y = 31 to 0). Bit n is PnWP (P31WP at bit 31 down to P0WP at bit 0). These bits are set by software and cleared only by a global RAMCFG reset.
  - 0: Write protection of SRAM2 1-Kbyte page y is disabled.
  - 1: Write protection of SRAM2 1-Kbyte page y is enabled.

### 5.6.9 RAMCFG memory 2 write protection register 2 (RAMCFG_M2WPR2)

Address offset: 0x05C. Reset value: 0x0000 0000.

- **Bits 31:0 PyWP** (rs): SRAM2 1-Kbyte page y write protection (y = 63 to 32). Bit n is P(n+32)WP (P63WP at bit 31 down to P32WP at bit 0). These bits are set by software and cleared only by a global RAMCFG reset.
  - 0: Write protection of SRAM2 1-Kbyte page y is disabled.
  - 1: Write protection of SRAM2 1-Kbyte page y is enabled.

### 5.6.10 RAMCFG memory 2ECC key register (RAMCFG_M2ECCKEYR)

Address offset: 0x064. Reset value: 0x0000 0000.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:0 ECCKEY[7:0]** (w): ECC write protection key. The following steps are required to unlock the write protection of ECCE in RAMCFG_M2CR.
  1. Write 0xAE into ECCKEY[7:0].
  2. Write 0x75 into ECCKEY[7:0].
  - Note: Writing a wrong key reactivates the write protection.

### 5.6.11 RAMCFG memory 2 write protection register 3 (RAMCFG_M2WPR3)

Address offset: 0x070. Reset value: 0x0000 0000.

- **Bits 31:0 PyWP** (rs): SRAM2 1-Kbyte page y write protection (y = 95 to 64). Bit n is P(n+64)WP (P95WP at bit 31 down to P64WP at bit 0). These bits are set by software and cleared only by a global RAMCFG reset.
  - 0: Write protection of SRAM2 1-Kbyte page y is disabled.
  - 1: Write protection of SRAM2 1-Kbyte page y is enabled.

*Digest note:* Available only on STM32C59x/5A3 (Section 5.3.3 note a); reserved on STM32C551/C552.

### 5.6.12 RAMCFG memory 2 write protection register 4 (RAMCFG_M2WPR4)

Address offset: 0x074. Reset value: 0x0000 0000.

- **Bits 31:0 PyWP** (rs): SRAM2 1-Kbyte page y write protection (y = 127 to 96). Bit n is P(n+96)WP (P127WP at bit 31 down to P96WP at bit 0). These bits are set by software and cleared only by a global RAMCFG reset.
  - 0: Write protection of SRAM2 1-Kbyte page y is disabled.
  - 1: Write protection of SRAM2 1-Kbyte page y is enabled.

*Digest note:* Available only on STM32C59x/5A3 (Section 5.3.3 note a); reserved on STM32C551/C552.

### 5.6.13 RAMCFG register map

**Table 19. RAMCFG register map and reset values**

| Offset | Register | Reset value | Fields (bit positions) |
|---|---|---|---|
| 0x000 | RAMCFG_M1CR | 0x0000 0000 | SRAMER (8) |
| 0x004 | Reserved | - | - |
| 0x008 | RAMCFG_M1ISR | 0x0000 0000 | SRAMBUSY (8) |
| 0x00C - 0x024 | Reserved | - | - |
| 0x028 | RAMCFG_M1ERKEYR | 0x0000 0000 | ERASEKEY[7:0] (7:0) |
| 0x02C - 0x03C | Reserved | - | - |
| 0x040 | RAMCFG_M2CR | 0x0000 000X (SRAMER = 0, ALE = 0, ECCE = x) | SRAMER (8), ALE (4), ECCE (0) |
| 0x044 | RAMCFG_M2IER | 0x0000 0000 | ECCNMI (3), DEIE (1), SEIE (0) |
| 0x048 | RAMCFG_M2ISR | 0x0000 0000 | SRAMBUSY (8), DED (1), SEDC (0) |
| 0x04C | RAMCFG_M2SEAR | 0x0000 0000 | ESEA[31:0] (31:0) |
| 0x050 | RAMCFG_M2DEAR | 0x0000 0000 | EDEA[31:0] (31:0) |
| 0x054 | RAMCFG_M2ICR | 0x0000 0000 | CDED (1), CSEDC (0) |
| 0x058 | RAMCFG_M2WPR1 | 0x0000 0000 | P31WP..P0WP (31:0) |
| 0x05C | RAMCFG_M2WPR2 | 0x0000 0000 | P63WP..P32WP (31:0) |
| 0x060 | Reserved | - | - |
| 0x064 | RAMCFG_M2ECCKEYR | 0x0000 0000 | ECCKEY[7:0] (7:0) |
| 0x068 | RAMCFG_M2ERKEYR | 0x0000 0000 | ERASEKEY[7:0] (7:0) |
| 0x070 | RAMCFG_M2WPR3 | 0x0000 0000 | P95WP..P64WP (31:0) |
| 0x074 | RAMCFG_M2WPR4 | 0x0000 0000 | P127WP..P96WP (31:0) |

Refer to Section 2.2: Memory organization for the register boundary addresses.

*Digest note:* Offset 0x06C does not appear in the source register map (it is neither listed nor marked Reserved); treat it as reserved. The source map shows no RAMCFG_M2ERKEYR description section of its own; it is covered by Section 5.6.3 (RAMCFG_MxERKEYR, x = 2 gives 0x068). RAMCFG base address: 0x4002 6000 (Chapter 2, Table 3, AHB1).
