# RM0522 Chapter 12: System configuration, boot, and security (SBS)

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 357–370.

## 12.1 SBS introduction

The STM32C5 devices feature a set of configuration registers located in the SBS. On top of various device configurations, this SBS peripheral controls key boot and security features, including debug control.

## 12.2 SBS main features

- System configuration
  - Manage robustness feature.
  - Manage ADC input channel remap.
  - Manage the I/O compensation cell.
  - Configure register security access.
- Boot control
  - Upon system reset, configure the Cortex-M33 boot address and the temporal isolation level depending on the current configuration (such as RDP_LEVEL (sbs_rdp_level).
  - Manage the temporal isolation feature implemented thanks to the hide protect level (HDPL) monotonic counter.

## 12.3 SBS functional description

### 12.3.1 SBS block diagram

The figure below shows the SBS block diagram, including the following main functions:

- System configuration
- Boot control

**Figure 36. SBS block diagram** (described)

The SBS block contains a "System configuration" block and a "Boot control" block. Inputs: SBS_BOOT_PIN (shown as a pin), sbs_boot_addresses and sbs_rdp_level, all feeding Boot control. Boot control drives the output sbs_init_vtor, an "HPDL counter" block whose output is sbs_hpdl, and the output sbs_dbg_state.

*Digest note:* the figure labels the counter "HPDL" and its output "sbs_hpdl"; the text and Table 80 use HDPL / sbs_hdpl. The figure shows an output sbs_dbg_state while Table 80 lists sbs_ap_unlocked instead.

### 12.3.2 SBS signals

The following table details the user-relevant internal signals that interface the SBS.

**Table 80. SBS internal input/output signals**

| Signal name | Type | Description |
|---|---|---|
| SBS_BOOT_PIN | Input | Select booting on user flash memory or bootloader |
| sbs_boot_addresses | Input | List of addresses defined by the flash memory: BOOT_ADDR: boot address |
| sbs_rdp_level | Input | Signal based on the RDP_LEVEL option byte to activate the different security mechanisms depending on the product use. Expected values are described in Section 6: Embedded flash memory (FLASH). |
| sbs_init_vtor | Output | Vector address for Cortex-M33 |
| sbs_hdpl | Output | HDPL (temporal isolation level, ID of the boot level, used to isolate boot levels). This signal reflects a monotonic counter that can be incremented from 0 to 3, and that is reset to zero only on software reset or POR. |
| sbs_ap_unlocked | Output | Control the Cortex-M33 access port. |

*Digest note:* Table 80 says the HDPL counter goes from 0 to 3 and resets to zero, while Section 12.3.5 and SBS_HDPLSR say the default (reset) value is 1 (code 0x51) and the range is 1 to 3. The register-level description (1 to 3, reset 0x51) is the one software observes.

### 12.3.3 SBS reset and clocks

The SBS configuration port is clocked by the AHB bus clock. There is a general reset and a debug configuration reset controlled in DBGMCU.

### 12.3.4 SBS I/O compensation cell management

The I/O compensation cell generates an 8-bit value for the I/O buffer: 4 bits for N-MOS and 4 bits for P-MOS. This value depends on the process, voltage, temperature (PVT) operating conditions. These bits are used to control the output impedance in the I/O buffer, and the slew rate of the I/O commutation (the tfall and trise time), in order to reduce the I/O noise on the power supply.

As shown in Figure 37, the compensation cell is split in two blocks:

- One block to provide an optimal code for the current PVT
- One block to drive the block controlled by software

**Figure 37. Compensation cell management** (described)

SBS_CCCSR sends "enable" to the compensation cell and receives "ready" from it; it also drives "code selection" of a 2-input multiplexer. Multiplexer input 0 is SBS_CCVALR, which is loaded from the compensation cell "value" output; multiplexer input 1 is SBS_CCSWCR. The multiplexer output is applied as the compensation code.

The compensation cell value can be read when the READY flag is set in SBS_CCCSR. With CODESEL in SBS_CCCSR, the application can select the value to apply between two options: the code from the cell, or the code from SBS_CCSWCR.

By default, the compensation cells are disabled, and a fixed code is applied to all I/Os.

The compensation cell can be used only when the HSI oscillator is enabled, see Section 9: Reset and clock control (RCC) for more details on the HSI oscillator.

*Digest note:* "READY" and "CODESEL" in this text are the RDY1 and CS1 bits of SBS_CCCSR (Section 12.5.7). The "fixed code" applied at reset is SBS_CCSWCR = 0x78 (SW_APSRC1 = 0x7, SW_ANSRC1 = 0x8), selected because CS1 resets to 1.

**Figure 38. Compensation cell use** (described)

A plot of compensation code (vertical axis, from "Fast" at the bottom to "Slow" at the top) versus supply voltage (horizontal axis, marks at 1.71, 2.0, 2.2, 2.7 and 3.3 V). The code rises linearly from Fast at 1.71 V to Slow at 2.0 V; between 2.0 V and 2.2 V a shaded region spans the full Fast-to-Slow range; from 2.2 V to 2.7 V the code stays at Fast; from 2.7 V it rises linearly to Slow at 3.3 V. [unclear in source: the meaning of the shaded 2.0–2.2 V region is not explained in the text.]

### 12.3.5 SBS boot control

The SBS can be used to control the boot entry points considering the product settings. The main boot control actions are listed below:

- Select boot between the bootloader or the user flash memory boot.
- Initialize the HDPL boot value.

Note: For more details on STM32C5xx BOOT control, refer to Section 4: Boot modes.

**SBS HDPL (temporal isolation level) management**

The HDPL is a monotonic counter incremented during the boot stages. The HDPL is reset to its default value only after a power-on or a system reset. This default value is 1.

The devices use HDPL information to automatically isolate code and its associated secrets (like keys) during the boot process. Incrementing HPDL ensures that private code and data for one boot stage cannot be directly accessible from later boot stages.

The HDPL is used by the user flash memory. See Section 6: Embedded flash memory (FLASH) for more details.

The HDPL can take the value from 1 to 3. When reaching the value 3, HDPL keeps this value until reset. The current HDPL value is readable in HDPL bitfield of SBS_HDPLSR.

To increment the HDPL by one, the application must write 0x6A to INCR_HDPL in SBS_HDPLCR. After such increment, and before doing any subsequent action, the user must check that the HDPL has effectively been incremented reading SBS_HDPLSR.

**Table 81. HDPL encoded values**

| HDPL | Code |
|---|---|
| 1 | 0x51 |
| 2 | 0x8A |
| 3 | 0x6F |
| 3 | All other values |

### 12.3.6 SBS hardware secure storage control

This feature ensures the isolation of keys including the key derivation (DHUK) mechanism protecting data using a hardware key different for the identified domains.

**Figure 39. SBS hardware secure storage control** (described)

Inside the SBS, the HDPL counter feeds both a "Hardware secure storage control" block and a NEXT-HDPL block. NEXT-HDPL outputs sbs_next_hdpl to the SAES, whose DHUK block also receives the RHUK from the flash memory.

- sbs_next_hdpl: select secure storage context for current HDPL, or greater ones. This signal is set thanks to the SBS_NEXTHDPLCR register. This information is used by the SAES when processing the derived key to generate a key derived related to HDPL context.

All keys encrypted using the SAES/DHUK inherit of the RHUK property: unique per device.

The table below gives the value of HDPL function of NEXTHDPL value.

**Table 82. NEXT-HDPL logic**

| HDPL[7:0] in SBS_HDPLSR | NEXTHDPL[1:0] = 0 | NEXTHDPL[1:0] = 1 | NEXTHDPL[1:0] = 2 | NEXTHDPL[1:0] = 3 |
|---|---|---|---|---|
| 1 (0x51) | 0x51 | 0x8A | 0x6F | 0x6F |
| 2 (0x8A) | 0x8A | 0x6F | 0x6F | 0x6F |
| 3 (0x6F) | 0x6F | 0x6F | 0x6F | 0x6F |
| Others | 0x6F | 0x6F | 0x6F | 0x6F |

*Digest note:* SBS_NEXTHDPLCR applies only to STM32C59xx/C5Axx (Section 12.5.3). The STM32C55xxx CMSIS header has no SAES and no NEXTHDPLCR register, so this secure-storage feature is absent on STM32C551/C552.

## 12.4 SBS interrupts

SBS does not support interrupts.

## 12.5 SBS registers

For the actual availability of some peripherals/features and their related bits, check the datasheet or Table 3: Memory map and peripheral register boundary addresses. If not present, consider them as reserved, and keep them at reset value.

*Digest note:* the CMSIS header (stm32c552xx.h) defines SBS_BASE = APB3PERIPH_BASE + 0x0400 = 0x4400 0400. Its SBS_TypeDef contains HDPLCR (0x010), HDPLSR (0x014), FPUIMR (0x104), MESR (0x108), CCCSR (0x110), CCVALR (0x114), CCSWCR (0x118), CFGR2 (0x120), CLCKR (0x144) and ECCNMIR (0x14C). It has no NEXTHDPLCR (0x018) and no PMCR (0x100); on STM32C551/C552 treat those offsets as reserved.

### 12.5.1 SBS temporal isolation control register (SBS_HDPLCR)

Address offset: 0x010. Reset value: 0x0000 00B4. Reset: system reset.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:0 INCR_HDPL[7:0]** (rw): HDPL value increment
  - 0xB4: No increment
  - 0x6A: Recommended value to increment HDPL level by one
  - Other: All other values allow an HDPL level increment.

### 12.5.2 SBS temporal isolation status register (SBS_HDPLSR)

Address offset: 0x014. Reset value: 0x0000 0051. Reset: system reset.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:0 HDPL[7:0]** (r): Temporal isolation level
  This bitfield returns the current temporal isolation level.
  - 0x51: HDPL1, hide protection level to be used to execute and protect an immutable root of trust (IROT) stage. First code to be executed at each reset of the platform. To ensure secure boot, this code must be immutable)
  - 0x8A: HDPL2, hide protection level to be used to execute and protect an updatable Root of Trust (UROT) stage. UROT is executed from IROT to complete the immutable root of trust execution during boot stages
  - 0x6F: HDPL3, hide protection level to be used to execute the application. It is a temporal isolation level that can be used to run the application when it has to be isolated from IROT and UROT)

### 12.5.3 SBS next HDPL control register (SBS_NEXTHDPLCR)

Note: This section applies only to STM32C59xx/C5Axx devices.

Address offset: 0x018. Reset value: 0x0000 0000. Reset: system reset. Register security: no restriction.

- **Bits 31:2** Reserved, must be kept at reset value.
- **Bits 1:0 NEXTHDPL[1:0]** (rw): Index to point to a higher HDPL than the current one
  This bitfield is used to add the increment to HDPL to access to the next secure storage areas through NEXT-HDPL.
  - 00: NEXT-HDPL = HDPL
  - 01: NEXT-HDPL = HDPL + 1
  - 10: NEXT-HDPL = HDPL + 2
  - 11: NEXT-HDPL = HDPL + 3

*Digest note:* not present on STM32C551/C552 (see the note under Section 12.5).

### 12.5.4 SBS product mode and configuration register (SBS_PMCR)

Address offset: 0x100. Reset value: 0x8000 0000. Reset: system reset. Register security: there is no access restriction.

- **Bit 31** Reserved, must be kept at reset value.
- **Bit 30 ETH1TXLPI** (r): Ethernet TxLPI status
  This bit is set and reset by hardware.
  When set, this bit indicates that the MAC has entered Tx LPI mode.
- **Bit 29 ETH1PDACK** (r): Ethernet power-down acknowledge
  This bit is set and reset by hardware.
  When set, this bit indicates that the Ethernet controller has complete its power-down sequence and its clock can be stopped.
  - 0: Ethernet functional / power-down sequence not yet completed
  - 1: Ethernet power-down sequence completed
- **Bit 28 ETH1INTPOL** (rw): Ethernet external PHY interrupt polarity configuration
  - 0: active high
  - 1: active low
- **Bits 27:24 ETH1_SEL_PHY[3:0]** (rw): Ethernet PHY interface selection
  - 0000: GMII or MII
  - 0100: RMII
  - Other: reserved
- **Bits 23:4** Reserved, must be kept at reset value.
- **Bit 3 ADC1_IN7_REMAP** (rw): ADC1 channel IN7 remap
  - 0: ADC1_IN7 is mapped on PA7
  - 1: ADC1_IN7 is mapped on PB1

  Note: This bit is only available for STM32C53x/542 device.
- **Bit 2 ADC1_IN6_REMAP** (rw): ADC1 channel IN6 remap
  - 0: ADC1_IN6 is mapped on PA6
  - 1: ADC1_IN6 is mapped on PB0

  Note: This bit is only available for STM32C53x/542 device.
- **Bit 1 ADC1_IN5_REMAP** (rw): ADC1 channel IN5 remap
  - 0: ADC1_IN5 is mapped on PA5
  - 1: ADC1_IN5 is mapped on PC5

  Note: This bit is only available for STM32C53x/542 device.
- **Bit 0 ADC1_IN2_REMAP** (rw): ADC1 channel IN2 remap
  - 0: ADC1_IN2 is mapped on PA2
  - 1: ADC1_IN2 is mapped on PC4

  Note: This bit is only available for STM32C53x/542 device.

*Digest note:* the stated reset value 0x8000 0000 sets bit 31, which is described as reserved; the register map (Table 83) shows reset 0 for ETH1TXLPI/ETH1PDACK/ETH1INTPOL and ETH1_SEL_PHY bits 26:24, no value for bits 31 and 27, and 0 for the ADC remap bits. [unclear in source: whether bit 31 actually reads 1.] The register map names the Ethernet fields ETHTXLPI, ETHPDACK, ETHINTPOL and ETH_SEL_PHY[3:0] (without the "1"). On STM32C551/C552 the register is absent from the CMSIS header: the ADC remap bits apply only to STM32C53x/542, and the datasheet digest shows no Ethernet on C55xxx. On C55xxx, ADC1_IN2/IN5/IN6/IN7 are on PA2/PA5/PA6/PA7 per the datasheet pinout.

### 12.5.5 SBS FPU interrupt mask register (SBS_FPUIMR)

Address offset: 0x104. Reset value: 0x0000 001F. Reset: system reset.

This register is only accessible through a privilege transaction.

- **Bits 31:6** Reserved, must be kept at reset value.
- **Bits 5:0 FPU_IE[5:0]** (rw): FPU interrupt enable
  This bitfield is set and cleared by software to enable the Cortex-M33 FPU interrupts.
  - FPU_IE[5]: Inexact interrupt enable (interrupt disabled at reset)
  - FPU_IE[4]: Input abnormal interrupt enable
  - FPU_IE[3]: Overflow interrupt enable
  - FPU_IE[2]: Underflow interrupt enable
  - FPU_IE[1]: Divide-by-zero interrupt enable
  - FPU_IE[0]: Invalid operation interrupt enable

*Digest note:* reset 0x1F means the input-abnormal, overflow, underflow, divide-by-zero and invalid-operation FPU exception interrupts are enabled at reset (only inexact is disabled). Whether these reach the NVIC as an FPU interrupt line is defined in the NVIC/interrupt chapter, not here.

### 12.5.6 SBS memory erase status register (SBS_MESR)

Address offset: 0x108. Reset value: 0x000X 000X.

Note: Bits 0 and 16 are not affected by system reset.

Register security: always accessible

- **Bits 31:17** Reserved, must be kept at reset value.
- **Bit 16 IPMEE** (rc_w1): ICACHE erase status
  This bit is set by hardware when an ICACHE erase is completed after potential tamper detection, or a product state regression (refer to Section 40: Tamper and backup registers (TAMP) for more details). This bit is cleared by software by writing 1 to it.
  - 0: ICACHE erase ongoing
  - 1: ICACHE erase ended
- **Bits 15:1** Reserved, must be kept at reset value.
- **Bit 0 MCLR** (rc_w1): Device memories erase status
  This bit is set by hardware when a SRAM2 and ICACHE erase is completed after power-on reset or tamper detection, or product state regression (refer to Section 40: Tamper and backup registers (TAMP) for more details).
  This bit is not reset by system reset and is cleared by software by writing 1 to it.
  - 0: Memory erase ongoing if not yet cleared by software
  - 1: Memory erase done

*Digest note:* the register map (Table 83) shows reset value 0 for IPMEE and MCLR.

### 12.5.7 SBS compensation cell for I/Os control and status register (SBS_CCCSR)

Address offset: 0x110. Reset value: 0x0000 0002. Reset: system reset. Register security: always accessible

- **Bits 31:9** Reserved, must be kept at reset value.
- **Bit 8 RDY1** (r): VDDIO compensation cell ready flag
  This bit provides the status of the compensation cell.
  - 0: VDDIO compensation cell not ready
  - 1: VDDIO compensation cell ready (code value provided by the cell can be used)
- **Bits 7:2** Reserved, must be kept at reset value.
- **Bit 1 CS1** (rw): Code selection for VDDIO power rail (reset value set to 1)
  This bit selects the code to be applied for the I/O compensation cell.
  - 0: Code from the cell (available in the SBS_CCVALR)
  - 1: Code from SBS_CCWCR
- **Bit 0 EN1** (rw): Enable compensation cell for VDDIO power rail
  This bit enables the I/O compensation cell.
  - 0: I/O compensation cell disabled
  - 1: I/O compensation cell enabled

*Digest note:* "SBS_CCWCR" in the CS1 description is SBS_CCSWCR. Typical use (derived from Section 12.3.4, not an RM-stated sequence): ensure HSI is on, set EN1, wait for RDY1 = 1, then clear CS1 to apply the cell code.

### 12.5.8 SBS compensation cell for I/Os value register (SBS_CCVALR)

Address offset: 0x114. Reset value: 0x0000 00XX. Reset: system reset. Register security: always accessible

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:4 APSRC1[3:0]** (r): Compensation value for the PMOS transistor
  This value is provided by the cell ,and the processor must interpret it to compensate the slew rate in the functional range.
- **Bits 3:0 ANSRC1[3:0]** (r): Compensation value for the NMOS transistor
  This value is provided by the cell, and the processor must interpret it to compensate the slew rate in the functional range.

### 12.5.9 SBS compensation cell for I/Os software code register (SBS_CCSWCR)

Address offset: 0x118. Reset value: 0x0000 0078. Reset: system reset. Register security: always accessible

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bits 7:4 SW_APSRC1[3:0]** (rw): PMOS compensation code for the VDD power rails
  This bitfield is written by software to define an I/O compensation cell code for PMOS transistors of the VDDIO power rail. This code is applied to the I/O when CS1 is set in SBS_CCSR.
- **Bits 3:0 SW_ANSRC1[3:0]** (rw): NMOS compensation code for VDD power rails
  This bitfield is written by software to define an I/O compensation cell code for NMOS transistors of the VDD power rail. This code is applied to the I/O when CS1 is set in SBS_CCSR.

*Digest note:* "SBS_CCSR" in these descriptions is SBS_CCCSR. Reset SW_APSRC1 = 0x7, SW_ANSRC1 = 0x8.

### 12.5.10 SBS Class B register (SBS_CFGR2)

Address offset: 0x120. Reset value: 0x0000 0000. Reset: system reset. Register security: always accessible

- **Bits 31:4** Reserved, must be kept at reset value.
- **Bit 3 ECCL** (rw): ECC lock
  This bit is set and cleared by software. It can be used to enable and lock the flash memory double ECC error with break input of TIM1/8/15/16/17.
  - 0: Double ECC error flag disconnected to timer break inputs
  - 1: Double ECC error flag connected to timer break inputs
- **Bit 2 PVDL** (rs): PVD lock
  This bit is set by software and cleared only by a system reset. It can be used to enable and lock the PVD connection with TIM1/8/15/16/17 break inputs.
  - 0: PVD interrupt disconnected from timer break inputs. PVD_EN and PVD_SEL[2:0] in PWR registers are read/write.
  - 1: PVD interrupt is connected to timer break inputs. PVD_EN and PVD_SEL[2:0] in PWR registers are read only
- **Bit 1 SEL** (rs): SRAM ECC error lock
  This bit is set by software and cleared only by a system reset. It can be used to enable and lock the SRAM double ECC error signal with break input of TIM1/8/15/16/17.
  - 0: SRAM double ECC error flag disconnected from timer break inputs
  - 1: SRAM double ECC error flag connected to timer break inputs
- **Bit 0 CLL** (rs): Core lockup lock
  This bit is set by software and cleared only by a system reset. It can be used to enable and lock the lockup (HardFault) output of the Cortex-M33 with TIM1/8/15/16/17 break inputs.
  - 0: Lockup output disconnected from timer break inputs
  - 1: Lockup output connected to timer break inputs

### 12.5.11 SBS CPU lock register (SBS_CLCKR)

Address offset: 0x144. Reset value: 0x0000 0000. Reset: system reset.

Register security: This register can be read and written by privileged access only. Unprivileged access is RAZ/WI.

This register is used to lock the configuration of the MPU and VTOR registers of the Cortex-M33.

- **Bits 31:2** Reserved, must be kept at reset value.
- **Bit 1 LOCKMPU** (rs): MPU register lock
  This bit is set by software and cleared only by a system reset. When set, this bit disables write access to MPU_CTRL, MPU_RNR, and MPU_RBAR registers.
  - 0: MPU registers write enabled
  - 1: MPU registers write disabled
- **Bit 0 LOCKVTOR** (rs): VTOR register lock
  This bit is set by software and cleared only by a system reset.
  - 0: VTOR register write enabled
  - 1: VTOR register write disabled

*Digest note:* a bootloader (e.g. Katapult) that sets LOCKVTOR would prevent the application from relocating its vector table until the next system reset; leave this bit clear.

### 12.5.12 SBS ECC NMI mask register (SBS_ECCNMIR)

Address offset: 0x14C. Reset value: 0x0000 0000. Reset: system reset.

Register security: This register is only accessible through a privilege transaction.

This register sets up the expected behavior on NMI regarding double ECC errors from the flash memory.

- **Bits 31:1** Reserved, must be kept at reset value.
- **Bit 0 ECCNMI_MASK_EN** (rw): NMI behavior setup when a double ECC error occurs on FLASH data part
  - 0: NMI generated if a double ECC error in the FLASH data part
  - 1: NMI not generated if a double ECC error in the FLASH data part

### 12.5.13 SBS register map

**Table 83. SBS register map and reset values**

| Offset | Register | Reset value | Fields (bit positions) |
|---|---|---|---|
| 0x010 | SBS_HDPLCR | 0x0000 00B4 | 31:8 Res.; INCR_HDPL[7:0] (7:0) |
| 0x014 | SBS_HDPLSR | 0x0000 0051 | 31:8 Res.; HDPL[7:0] (7:0) |
| 0x018 | SBS_NEXTHDPLCR | 0x0000 0000 | 31:2 Res.; NEXTHDPL[1:0] (1:0) |
| 0x01C-0x0FC | Reserved | - | - |
| 0x100 | SBS_PMCR | 0x8000 0000 (text) | 31 Res.; ETHTXLPI (30); ETHPDACK (29); ETHINTPOL (28); ETH_SEL_PHY[3:0] (27:24); 23:4 Res.; ADC1_IN7_REMAP (3); ADC1_IN6_REMAP (2); ADC1_IN5_REMAP (1); ADC1_IN2_REMAP (0) |
| 0x104 | SBS_FPUIMR | 0x0000 001F | 31:6 Res.; FPU_IE[5:0] (5:0) |
| 0x108 | SBS_MESR | 0x000X 000X (map shows 0) | 31:17 Res.; IPMEE (16); 15:1 Res.; MCLR (0) |
| 0x110 | SBS_CCCSR | 0x0000 0002 | 31:9 Res.; RDY1 (8); 7:2 Res.; CS1 (1); EN1 (0) |
| 0x114 | SBS_CCVALR | 0x0000 00XX | 31:8 Res.; APSRC1[3:0] (7:4); ANSRC1[3:0] (3:0) |
| 0x118 | SBS_CCSWCR | 0x0000 0078 | 31:8 Res.; SW_APSRC1[3:0] (7:4); SW_ANSRC1[3:0] (3:0) |
| 0x120 | SBS_CFGR2 | 0x0000 0000 | 31:4 Res.; ECCL (3); PVDL (2); SEL (1); CLL (0) |
| 0x124-0x140 | Reserved | - | - |
| 0x144 | SBS_CLCKR | 0x0000 0000 | 31:2 Res.; LOCKMPU (1); LOCKVTOR (0) |
| 0x14C | SBS_ECCNMIR | 0x0000 0000 | 31:1 Res.; ECCNMI_MASK_EN (0) |

Refer to Section 2.2: Memory organization for the register boundary addresses.

*Digest note:* the register map does not list offsets 0x10C, 0x11C and 0x148 (gaps between listed registers); the CMSIS header marks them reserved. All SBS bit positions for registers present in stm32c552xx.h match the RM. There is no SBS register in this chapter for boot address selection, memory remap, analog switch booster, or EXTI port selection; the CMSIS header places the EXTI port selection registers (EXTICR[4], offset 0x060) in EXTI_TypeDef and has no analog-switch booster bits.
