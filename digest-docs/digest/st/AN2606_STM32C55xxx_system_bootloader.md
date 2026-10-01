# AN2606: Introduction to system memory boot mode on STM32 MCUs

Source: AN2606 Rev 70 (February 2026), pages 1–2 and 27–60 and 84–87 (PDF page numbers equal printed page numbers).

Chapters digested: Introduction (page 1, with the STM32C5 row of Table 1), 1 General information, 2 Related documents, 3 Glossary, 4 General bootloader description, and 11 STM32C55xxx/562xx devices. Chapters 5–10, 12 and later, and the appendices are not digested.

Conventions: remarks added by the digest (not ST text) are marked *Digest note:* or `[unclear in source: ...]`. Section, table and figure numbers match the original. Merged table cells are repeated in every row. Page headers and footers are dropped.

## Introduction

This document applies to the products listed in Table 1, referred to as STM32 throughout the document.

It describes the supported peripherals and hardware requirements to consider when using the bootloader, stored in the internal boot ROM (system memory) of STM32 devices, and programmed during production.

Its main task is to download the application program to the internal flash memory through one of the available serial peripherals (such as USART, CAN, USB, I2C, I3C, SPI, FDCAN). A communication protocol is defined for each interface, with a compatible command set and sequence.

**Table 1. Applicable products**

| Type | Part number or product series |
|---|---|
| Microcontrollers | STM32C5 series: STM32C5A3xx, STM32C531xx, STM32C532xx, STM32C542xx, STM32C551xx, STM32C552xx, STM32C562xx, STM32C591xx, STM32C593xx |

*Digest note:* Table 1 also lists the STM32C0, F0, F1, F2, F3, F4, F7, G0, G4, H5, H7, L0, L1, L4, L5, U0, U3, U5, WB, WBA, WB0 and WL series (all of type "Microcontrollers"). Those rows were omitted; only the STM32C5 row is kept.

## 1 General information

This document applies to Arm®(a)-based devices.

Notes:

- (a) Arm is a registered trademark of Arm Limited (or its subsidiaries or affiliates) in the US and/or elsewhere. The Arm word and logo are trademarks of Arm Limited (or its subsidiaries) in the US and/or elsewhere. All rights reserved

## 2 Related documents

For each supported product refer to the following documents, available on www.st.com:

- Datasheet or databrief
- Reference manual
- Application notes
  - AN3154: How to use CAN protocol in bootloader on STM32 MCUs
  - AN3155: How to use USART protocol in bootloader on STM32 MCUs
  - AN3156: How to use USB DFU protocol in bootloader on STM32 MCUs
  - AN4221: How to use I2C protocol in bootloader on STM32 MCUs
  - AN4286: How to use SPI protocol in bootloader on STM32 MCUs
  - AN5405: How to use FDCAN protocol in bootloader on STM32 MCUs
  - AN5927: How to use I3C protocol in bootloader on STM32 MCUs

## 3 Glossary

C5 series:

- STM32C5A3xx indicates STM32C5A3xx devices.
- STM32C591xx/593xx indicates STM32C591xx and STM32C593xx devices.
- STM32C55xxx indicates STM32C551xx and STM32C552xx devices.
- STM32C562xx indicates STM32C562xx devices.
- STM32C531xx/532xx indicates STM32C531xx and STM32C532xx devices.
- STM32C542xx indicates STM32C542xx devices.

*Digest note:* The glossary also contains entries that only expand device-name groupings of other series (C0, F0, F1, F2, F3, F4, F7, G0, G4, H5, H7, L0, L1, L4, L5, U0, U3, U5, WB, WBA, WB0, WL). Those entries were omitted. The C5 entries and the note below are complete.

**Note:**

- BL_USART_Loop refers to the USART bootloader execution loop.
- BL_CAN_Loop refers to the CAN bootloader execution loop.
- BL_FDCAN_Loop refers to the FDCAN execution loop.
- BL_I2C_Loop refers to the I2C bootloader execution loop.
- BL_I3C_Loop refers to the I3C bootloader execution loop.
- BL_SPI_Loop refers to the SPI bootloader execution loop.

## 4 General bootloader description

### 4.1 Bootloader activation

The bootloader is activated by applying one of the patterns described in Table 2.

If boot from Bank2 option is activated (for products supporting this feature), the bootloader executes Dual Boot mechanism as described in figures "Dual bank boot implementation for STM32xxxx" (example: Figure 51), otherwise bootloader selection protocol is executed as described in figures "Bootloader VY.x selection for STM32xxxx" (example: Figure 32), where STM32xxxx is the relative STM32 product.

When readout protection Level2 is activated, the MCU does not boot on system memory, and bootloader cannot be executed (unless jumping to it from flash user code, all commands are not accessible except Get, GetID, and GetVersion).

**Table 2. Bootloader activation patterns**

| Pattern | Condition |
|---|---|
| Pattern 1 | Boot0(pin) = 1 and Boot1(pin) = 0 |
| Pattern 2 | Boot0(pin) = 1 and nBoot1(bit) = 1 |
| Pattern 3 | Boot0(pin) = 1, Boot1(pin) = 0 and BFB2(bit) = 1 |
| Pattern 3 | Boot0(pin) = 0, BFB2(bit) = 0 and both banks do not contain valid code |
| Pattern 3 | Boot0(pin) = 1, Boot1(pin) = 0, BFB2(bit) = 0 and both banks do not contain valid code |
| Pattern 4 | Boot0(pin) = 1, Boot1(pin) = 0 and BFB2(bit) = 1 |
| Pattern 4 | Boot0(pin) = 0, BFB2(bit) = 0 and both banks do not contain valid code |
| Pattern 4 | Boot0(pin) = 1, Boot1(pin) = 0 and BFB2(bit) = 0 |
| Pattern 5 | Boot0(pin) = 1, Boot1(pin) = 0 and BFB2(bit) = 0 |
| Pattern 5 | Boot0(pin) = 0, BFB2(bit) = 1 and both banks do not contain valid code |
| Pattern 5 | Boot0(pin) = 1, Boot1(pin) = 0 and BFB2 (bit) = 1 |
| Pattern 6 | Boot0(pin) = 1, nBoot1(bit) = 1 and nBoot0_SW(bit) = 1 |
| Pattern 6 | nBoot0(bit) = 0, nBoot1(bit) = 1 and nBoot0_SW(bit) = 0 |
| Pattern 6 | Boot0(pin) = 0, nBoot0_SW(bit) = 1 and main flash memory empty |
| Pattern 6 | nBoot0(bit) = 1, nBoot0_SW(bit)=0 and main flash memory empty |
| Pattern 7 | Boot0(pin) = 1, nBoot1(bit) = 1 and BFB2(bit) = 0 |
| Pattern 7 | Boot0(pin) = 0, BFB2(bit) = 1 and both banks do not contain valid code |
| Pattern 7 | Boot0(pin) = 1, nBoot1(bit) = 1 and BFB2(bit) = 1 |
| Pattern 8 | Boot(pin) = 0 and BOOT_ADD0(optionbyte) = 0x0040 |
| Pattern 8 | Boot(pin) = 1 and BOOT_ADD1(optionbyte) = 0x0040 |
| Pattern 9 | nDBANK(bit) = 1, Boot(pin) = 0 and BOOT_ADD0(optionbyte) = 0x0040 |
| Pattern 9 | nDBANK(bit) = 1, Boot(pin) = 1 and BOOT_ADD1(optionbyte) = 0x0040 |
| Pattern 9 | nDBANK(bit) = 0, nDBOOT(bit) = 1, Boot(pin) = 0 and BOOT_ADD0(optionbyte) = 0x0040 |
| Pattern 9 | nDBANK(bit) = 0, nDBOOT(bit) = 1, Boot(pin) = 1 and BOOT_ADD1(optionbyte) = 0x0040 |
| Pattern 9 | nDBANK(bit) = 0, nDBOOT(bit) = 0, BOOT_ADDx(optionbyte) out of memory range or in ICP memory range |
| Pattern 9 | nDBANK(bit) = 0, nDBOOT(bit) = 0, BOOT_ADDx(optionbyte) in flash memory range and both banks do not contain valid code |
| Pattern 10 | Boot(pin) = 0 and BOOT_ADD0(optionbyte) = 0x1FF0 |
| Pattern 10 | Boot(pin) = 1 and BOOT_ADD1(optionbyte) = 0x1FF0 |
| Pattern 11 | BOOT_LOCK(bit) = 0, nBoot1(bit) = 1, nBOOT0_SEL(bit) = 1 and nBoot0(bit) = 0 |
| Pattern 11 | BOOT_LOCK(bit) = 0, nBoot1(bit) = 1, Boot0(pin) = 1 and nBOOT0_SEL(bit) = 0 |
| Pattern 11 | BOOT_LOCK(bit) = 0, nBOOT0_SEL(bit) = 1, nBoot0(bit) = 1 and main flash empty |
| Pattern 11 | BOOT_LOCK(bit) = 0, Boot0(pin) = 0, nBOOT0_SEL(bit) = 0 and main flash empty |
| Pattern 12 | TZEN = 1 = 0, Boot0(pin) = 0, nSWBoot0(bit) = 1 and NSBOOTADD0 [24:0] = Address(1) |
| Pattern 12 | TZEN = 1 = 0, Boot0(pin) = 1, nSWBoot0(bit) = 1 and NSBOOTADD1 [24:0] = Address(1) |
| Pattern 12 | TZEN = 1 = 0, nBoot0(bit) = 0, nSWBoot0(bit) = 0 and NSBOOTADD1 [24:0] = Address(1) |
| Pattern 12 | TZEN = 0, nBoot0(bit) = 1, nSWBoot0(bit) = 0 and NSBOOTADD0 [24:0] = Address(1) |
| Pattern 12 | TZEN = 1, Boot0(pin) = 0, nSWBoot0(bit) = 1 and SECBOOTADD0 [24:0] = Address(1) and RSSCMD = 0 |
| Pattern 12 | TZEN = 1, Boot0(pin) = 1, nSWBoot0(bit) = 1 and RSSCMD = 0, BOOT_LOCK = 0 or (BOOT_LOCK = 1 and SECBOOTADD0 [24:0] = Address(1)) |
| Pattern 12 | TZEN = 1, nBoot0(bit) = 1, nSWBoot0(bit) = 0 and SECBOOTADD0 [24:0] = Address(1) and RSSCMD = 0, BOOT_LOCK = 0 or (BOOT_LOCK = 1 and SECBOOTADD0 [24:0] = Address(1)) |
| Pattern 12 | TZEN = 1, nBoot0(bit) = 0, nSWBoot0(bit) = 0 and RSSCMD = 0, BOOT_LOCK = 0 or BOOT_LOCK = 1 and SECBOOTADD1 [24:0] = Address(1) |
| Pattern 12 | TZEN = 1, RSSCMD = 0x1C0, BOOT_LOCK=0 or (BOOT_LOCK = 1 and SECBOOTADD0 [24:0] = Address(1)) |
| Pattern 13 | nBoot0(bit) = 0, nBoot1(bit) = 1 and nSWBoot0(bit) = 0 |
| Pattern 13 | nBoot0(bit) = 1, nBoot1(bit) = 1, nSWBoot0(bit) = 0 and user flash empty |
| Pattern 13 | nBoot1(bit) = 1, nSWBoot0(bit) = 1 and Boot0(pin) = 1 |
| Pattern 13 | nBoot1(bit) = 1, nSWBoot0(bit) = 1, Boot0(pin) = 0 and user flash empty |
| Pattern 14 | BOOT_LOCK(bit) = 0, nBoot1(bit) = 1, Boot0(pin) = 1 and nSWBoot0(bit) = 1 |
| Pattern 14 | BOOT_LOCK(bit) = 0, nBoot1(bit) = 1, nBoot0(bit) = 0 and nSWBoot0(bit) = 0 |
| Pattern 14 | BOOT_LOCK(bit) = 0, Boot0(pin) = 0, nSWBoot0(bit) = 1, BFB2(bit) = 1 and both banks do not contain valid code |
| Pattern 14 | BOOT_LOCK(bit) = 0, nBoot0(bit) = 1, nSWBoot0(bit) = 0, BFB2(bit) = 1 and both banks do not contain valid code |
| Pattern 15 | BOOT_LOCK(bit)=0, Boot0(pin) = 1, nBoot1(bit) = 1 and nBoot0_SW(bit) = 1 |
| Pattern 15 | BOOT_LOCK(bit)=0, nBoot0(bit) = 0, nBoot1(bit) = 1 and nBoot0_SW(bit) = 0 |
| Pattern 16 | Boot0(pin) = 1, nBoot1(bit) = 1 and nBoot0_SW(bit) = 1 |
| Pattern 16 | nBoot0(bit) = 0, nBoot1(bit) = 1 and nBoot0_SW(bit) = 0 |
| Pattern 16 | Boot0(pin) = 0, nBoot0_SW(bit) = 1 and main flash memory empty |
| Pattern 17 | PRODUCT_STATE = Open and Boot0(pin) = 1 |
| Pattern 17 | PRODUCT_STATE = Provisioning |
| Pattern 18 | Force PA10 high during HW reset |
| Pattern 19 | Boot0(bit) = 1 and BootSel(bit) = 0 |
| Pattern 19 | Boot0(bit) = 0, BootSel(bit) = 0, and user flash empty |
| Pattern 19 | BootSel(bit) = 1 and Boot pin = 1 |

Notes:

1. Device dependent: 0x17F200 for STM32L5, STM32U5, and STM32WBA6, 0x17F1E00 for STM32U3, 0x17F1000 for STM32WBA5, 0x17F0A0 for STM32WBA2.

*Digest note:* In the source each pattern is a merged cell spanning several condition rows; the pattern name is repeated here on every row. The table does not say so explicitly, but each row reads as one alternative condition that activates the bootloader. The three Pattern 19 conditions are printed as three lines inside one cell; they are split into three rows here.

*Digest note:* Pattern 19 is the pattern used by STM32C55xxx/562xx devices (Section 11.1). Boot0(bit) and BootSel(bit) are option bits; "Boot pin" is the BOOT0 pin.

*Digest note:* "TZEN = 1 = 0" (first three Pattern 12 rows) is reproduced as printed. [unclear in source: "TZEN = 1 = 0" is probably meant to read "TZEN = 0".]

**Note:** nBoot0_SW means either nSWBoot0 or nBOOT0_SEL, depending upon the product.

**Note:** BOOT_LOCK implementation is product dependent. See the reference manual for more details.

In addition to the patterns described above, the user can execute bootloader by performing a jump to system memory from user code. Before jumping to bootloader:

- Disable all peripheral clocks
- Disable used PLL
- Disable interrupts
- Clear pending interrupts

In some products using interrupts (integrating USB, SPI, non auto baud rate USART), interrupts must be re-enabled before jumping to the Bootloader, as this is not done by the bootloader SW.

System memory boot mode can be exited by getting out from bootloader activation condition and generating hardware reset or using Go command to execute user code.

**Note:** When executing the Go command, the peripheral registers used by the bootloader are not initialized to their default reset values before jumping to the user application. They must be reconfigured in the user application if they are used. So, if the application uses the IWDG, the IWDG prescaler value must be adapted to meet requirements (since the prescaler was set to its maximum value). For new products, the software resets all resources used by the bootloader (RCC, buses, PWR, PIO ports, and interrupts). Occasionally, not all reset values are set due to errors. For more information, see the known limitations for each product bootloader version.

**Note:** On devices with dual bank boot, to jump to system memory from user code the user must first remap the system memory bootloader at address 0x00000000 using SYSCFG register (except for STM32F7 series), then jump to bootloader. For the STM32F7 series, the user must disable nDBOOT and/or nDBANK features (in option bytes), then jump to bootloader. For STM32L0 series, the jump to system memory from user code is not possible.

**Note:** For STM32 devices embedding bootloader using the DFU/CAN interface in which the external clock source (HSE) is required for DFU/CAN operations, the detection of the HSE value is done dynamically by the bootloader firmware and is based on the internal oscillator clock (HSI, MSI). When (because of temperature variations or other conditions) the internal oscillator precision is altered above the tolerance band (1% around the theoretical value), the bootloader can calculate a wrong HSE frequency value. In this case, the bootloader DFU/CAN interfaces can malfunction, or not work at all.

### 4.2 Bootloader identification

Depending upon the device, the bootloader can support one or more embedded serial peripherals used to download the code to the internal flash memory. The bootloader identifier (ID) provides information about the supported serial peripherals.

For a given STM32 device, the bootloader is identified by means of the:

1. Bootloader (protocol) version: version of the serial peripheral (e.g. USART, CAN, USB) communication protocol used in the bootloader. This version can be retrieved using the bootloader Get Version command.
2. Bootloader identifier (ID): version of the STM32 device bootloader, coded on one byte in the 0xXY format, where:
   - X specifies the embedded serial peripheral(s) used by the device bootloader:
     - X = 1: one USART is used
     - X = 2: two USARTs are used
     - X = 3: USART, CAN, and DFU are used
     - X = 4: USART and DFU are used
     - X = 5: USART and I2C are used
     - X = 6: I2C is used
     - X = 7: USART, CAN, DFU, and I2C are used
     - X = 8: I2C and SPI are used
     - X = 9: USART, CAN (or FDCAN), DFU, I2C, and SPI are used
     - X = 10: USART, I2C, and DFU are used
     - X = 11: USART, I2C, and SPI are used
     - X = 12: USART and SPI are used
     - X = 13: USART, DFU, I2C, and SPI are used
     - X = 14: USART, DFU, I2C, I3C, FDCAN, and SPI are used
     - X = 15: USART, USB-DFU, I2C, and I3C are used

     Bootloader interface combinations have reached the maximum supported value. The solution is to extend the format to 0xXXY.

     XX now specifies the serial peripheral or peripherals used by the device bootloader:

     - X = 16: USART, USB DFU, FDCAN, and SPI are used
     - X = 17: USART, SPI, and FDCAN are used
     - X = 18: USART, SPI, FDCAN, and I2C are used

     Example: If the bootloader identification read on STM32C0 is 0x121, this means that the bootloader version is 18.1.
   - Y specifies the device bootloader version

     For example, if the bootloader ID is 0x10, this is the first version, which uses only one USART.

     The bootloader ID is programmed in the last byte address - 1 of the device system memory and can be read by using the "Read memory" command or by direct access to the system memory via JTAG/SWD.

**Note:** The bootloader ID format is applied to all STM32 products, except the STM32F1xx devices. The bootloader version for the STM32F1xx applies only to the embedded device bootloader version and not to its supported protocols.

*Digest note:* X values are decimal while the ID is written in hex: in the 0xXXY format, X = 16 gives IDs 0x10Y (for example 0x101 = bootloader V16.1, the STM32C55xxx/562xx ID in Table 3). [unclear in source: the ID is said to be "coded on one byte" and stored at "the last byte address - 1", but 0xXXY IDs such as 0x101 do not fit in one byte. The source does not say how the 0xXXY form is stored at the memory location given in Table 3 (0x0BF885FE for STM32C5).]

Table 3 provides identification information of the bootloaders embedded in STM32 devices.

**Table 3. Embedded bootloaders**

| Series | Device | Supported serial peripherals | Bootloader ID: ID | Bootloader ID: Memory location | Bootloader (protocol) version |
|---|---|---|---|---|---|
| C5 | STM32C5A3xx/59xxx | USART1/2/3 and UART4 | 0x100 | 0x0BF885FE | USART (V4.0) |
| C5 | STM32C5A3xx/59xxx | SPI1/2/3 | 0x100 | 0x0BF885FE | SPI (V2.0) |
| C5 | STM32C5A3xx/59xxx | FDCAN2 | 0x100 | 0x0BF885FE | FDCAN (V2.3) |
| C5 | STM32C5A3xx/59xxx | USB DFU | 0x100 | 0x0BF885FE | USB DFU (V3.0) |
| C5 | STM32C55xxx/562xx | USART1/2/3 and UART4 | 0x101 | 0x0BF885FE | USART (V4.0) |
| C5 | STM32C55xxx/562xx | SPI1/2/3 | 0x101 | 0x0BF885FE | SPI (V2.0) |
| C5 | STM32C55xxx/562xx | FDCAN1 | 0x101 | 0x0BF885FE | FDCAN (V2.3) |
| C5 | STM32C55xxx/562xx | USB DFU | 0x101 | 0x0BF885FE | USB DFU (V3.0) |
| C5 | STM32C53xxx/542xx | USART1/2 and UART4 | 0x100 | 0x0BF885FE | USART (V4.0) |
| C5 | STM32C53xxx/542xx | SPI1/2 | 0x100 | 0x0BF885FE | SPI (V2.0) |
| C5 | STM32C53xxx/542xx | FDCAN2 | 0x100 | 0x0BF885FE | FDCAN (V2.3) |
| C5 | STM32C53xxx/542xx | USB DFU | 0x100 | 0x0BF885FE | USB DFU (V3.0) |

Notes:

1. For connectivity line devices, the USART bootloader returns V2.0 instead of V2.2 for the protocol version. For more details refer to the "STM32F105xx and STM32F107xx revision Z" errata sheet available from www.st.com.

*Digest note:* Rows for all other series (C0, F0, F1, F2, F3, F4, F7, G0, G4, H5, H7, L0, L1, L4, L5, U0, U3, U5, WB, WBA, WB0, WL) were omitted; only the STM32C5 rows are kept. Note 1 refers to the omitted STM32F105xx/107xx row and is kept for completeness. In the source each device is one row whose "Supported serial peripherals" and "Bootloader (protocol) version" cells list one line per interface; the lines are split here into one row per interface (the n-th peripheral line pairs with the n-th version line) and the device, ID and memory location are repeated.

*Digest note:* The third C5 device is printed as "STM32C53xxx/542xx"; the glossary and Chapter 10 title call this group STM32C531xx/532xx/542xx. The STM32C55xxx/562xx bootloader is the only C5 bootloader using FDCAN1 (the others use FDCAN2), and it is the only one with ID 0x101.

### 4.3 Hardware connection requirements

To use the USART bootloader, the host must be connected to the RX and TX pins of the desired USARTx interface via a serial cable.

**Figure 1. USART connection**

The figure shows a UART host and an STM32 microcontroller connected through an RS232 transceiver (note 2). Host RX connects (through the transceiver) to STM32 TX, host TX connects to STM32 RX, and the GND lines of both are connected. On the STM32 side of the transceiver, both the TX and the RX lines have a pull-up resistor R to +V (note 1).

Notes:

1. A pull-up resistor must be added, if they are not connected on host side.
2. An RS232 transceiver must be connected to adapt the voltage level (3.3 to 12 V) between the STM32 device and the host.

**Note:** Typically V is 3.3 V, and R is 100 KΩ. These values depend upon the application and the used hardware.

To use the DFU, connect the microcontroller USB interface to a USB host (such as a PC).

**Figure 2. USB connection**

The figure shows a USB host whose DP, DM and GND lines connect directly to the DP, DM and GND pins of the STM32 microcontroller. An optional circuit (note 1) adds a pull-up on DP that is powered only when VBus is present: VBus from the host feeds a 10 kΩ / 36 kΩ divider to GND; the divider midpoint drives the base of a transistor whose collector is tied to +V; the transistor emitter connects through a 1.5 kΩ resistor to the DP line.

Notes:

1. This additional circuit permits to connect a pull-up resistor to DP pin using VBus when needed. Refer to product section (table describing STM32 configuration in system memory boot mode) to know if an external pull-up resistor must be connected to DP pin.

**Note:** V typically is 3.3 V. This value depends upon the application and the used hardware.

*Digest note:* The STM32C55xxx/562xx configuration table (Table 23) does not call for an external DP pull-up; it states only that PA11/PA12 are not configured by the bootloader software.

To use the I2C bootloader, connect the host (controller) and the desired I2Cx interface (target) together via the data (SDA) and clock (SCL) pins. A 1.8 KΩ pull-up resistor must be connected to both SDA and SCL lines.

**Figure 3. I2C connection**

The figure shows an I2C host whose SCL, SDA and GND lines connect directly to the SCL, SDA and GND pins of the STM32 microcontroller. SCL and SDA each have a 1.8 kΩ pull-up resistor to +V.

**Note:** V is typically 3.3 V. This value depends upon the application and the used hardware.

To use the SPI bootloader, connect the host (master) and the desired SPIx interface (slave) together via the MOSI, MISO, SCK, and NSS pins. A pull-down resistor must be connected to the SCK line.

**Figure 4. SPI connection**

The figure shows an SPI host whose NSS, MOSI, MISO, SCK and GND lines connect directly to the same-named pins of the STM32. A resistor connects the SCK line to ground (pull-down).

**Note:** The resistor is typically 10 KΩ, its value depends upon the application and the used hardware.

To use the CAN interface, the host must be connected to the RX and TX pins of the desired CANx interface via CAN transceiver and a serial cable. A 120 Ω resistor must be added as terminating resistor.

**Figure 5. CAN connection**

The figure shows a CAN host whose RX and TX pins connect to a CAN transceiver, and an STM32 microcontroller whose TX and RX pins connect to a second CAN transceiver. The two transceivers are linked by the CAN_H and CAN_L bus lines, with a 120 Ω termination resistor between CAN_H and CAN_L at each transceiver. The GND lines of host and STM32 are connected.

**Note:** When a bootloader firmware supports DFU, it is mandatory that no USB host is connected to the USB peripheral during the selection phase of the other interfaces. After selection phase, the user can plug a USB cable without impacting the selected bootloader execution, except for commands generating a system reset.

It is recommended to keep the RX pins of unused bootloader interfaces (USART_RX, SPI_MOSI, and CAN_RX, if present) at a known (low or high) level and keep the USB D+/D- lines, if present, on the same level (low/high) at the startup of the bootloader (detection phase). Leaving these pins floating during the detection phase can result in activation of unused interfaces.

### 4.4 Bootloader memory management

All write operations using bootloader commands must be word-aligned (the address must be a multiple of 4). The number of data to write must be a multiple of 4 as well (non-aligned half page write addresses are accepted).

Some products embed a bootloader with specific features:

- On products that do not support mass erase operation, to perform this operation using the bootloader, two options are available:
  - Erase all sectors one by one using the Erase command
  - Set protection level to Level 1. Then, set it to Level 0 (using the Read protect and then the Read unprotect command). This operation results in a mass erase of the internal flash memory.
- Bootloader firmware of STM32 L1 and L0 series supports Data memory in addition to standard memories (internal flash, internal SRAM, option bytes and System memory). The start address and the size of this area depends on product, refer to the reference manual for more information. Data memory can be read and written but cannot be erased using the Erase command. When writing in a Data memory location, the bootloader firmware manages the erase operation of this location before any write. A write to Data memory must be word-aligned (address to be written must be a multiple of 4) and the number of data must also be a multiple of 4. To erase a Data memory location, write 0s at this location.
- Bootloader firmware of the F2, F4, F7, and L4 series supports OTP memory in addition to standard memories (internal flash, internal SRAM, option bytes and System memory). The start address and the size of this area depends on product, refer to the reference manual for more information. OTP memory can be read and written but cannot be erased using Erase command. When writing in an OTP memory location, make sure that the relative protection bit is not reset.
- For STM32 F2, F4, and F7 series the internal flash memory write operation format depends on voltage range. By default write operations are allowed by one byte format (half-word, word, and double-word operations are not allowed). To increase the speed of write operation, the user must apply the adequate voltage range that allows write operation by half-word, word or double-word and update this configuration on the fly by the bootloader software through a virtual memory location. This memory location is not physical but can be read and written using usual bootloader read/write operations according to the protocol in use. This memory location contains four bytes, described in Table 4. It can be accessed by 1, 2, 3, or 4 bytes. However, reserved bytes must remain at their default values (0xFF), otherwise the request is NACK-ed.

**Table 4. STM32 F2, F4, and F7 voltage range configuration using bootloader**

| Address | Size | Description |
|---|---|---|
| 0xFFFF0000 | 1 byte | This byte controls the current value of the voltage range. 0x00: voltage range [1.8 V, 2.1 V]; 0x01: voltage range [2.1 V, 2.4 V]; 0x02: voltage range [2.4 V, 2.7 V]; 0x03: voltage range [2.7 V, 3.6 V]; 0x04: voltage range [2.7 V, 3.6 V] and double word write/erase operation is used. In this case it is mandatory to supply 9 V through the VPP pin (refer to the product reference manual for more details about the double-word write procedure); Others: all other values are not supported and are NACK-ed. |
| 0xFFFF0001 | 1 byte | Reserved. 0xFF is the default value, all other values are not supported and are NACK-ed. |
| 0xFFFF0002 | 1 byte | Reserved. 0xFF is the default value, all other values are not supported and are NACK-ed. |
| 0xFFFF0003 | 1 byte | Reserved. 0xFF is the default value, all other values are not supported and are NACK-ed. |

Table 5 lists the valid memory areas, depending upon the bootloader commands.

**Table 5. Supported memory area by Write, Read, Erase, and Go commands**

| Memory area | Write command | Read command | Erase command | Go command |
|---|---|---|---|---|
| Flash | Supported | Supported | Supported | Supported |
| RAM | Supported | Supported | Not supported | Supported |
| System memory | Not supported | Supported | Not supported | Not supported |
| Data memory | Supported | Supported | Supported(1) | Not supported |
| OTP memory | Supported | Supported | Not supported | Not supported |

Notes:

1. Depending on the STM32 device, the erase method varies:
   - Write 0 to the data memory address on STM32L0 and STM32L1 devices.
   - Use flash erase when the data memory corresponds to flash sectors, for example, STM32H57xx/8xx devices.
   - Use a special command to erase, as described in the STM32 paragraph.

### 4.5 Bootloader UART baudrate detection

For the UART interface baudrate detection, there are two implemented mechanisms:

- Software baudrate detection using internal HSI and timer (use GPIO as input, detect falling edge and rising edge as explained in AN3155).

  The devices using this mechanism are subject to software jitter (variable error of baudrate calculation) that can reach up to ±5%. In this case, the host connecting to the STM32 bootloader UART interface must support a ±5% deviation in baudrate.

  The software jitter value is variable and different at each retry, so it is possible to use multiple retry connections to overcome it. Connect and check for correct bootloader answer, if the answer is not correct, reset the device and retry connection until the correct answer is received. At this point, the rest of the communication is not impacted.

  It is also possible to reduce the software jitter by reducing the baudrate (as an example, use 56000 instead of 115200 bps).

  Table 6 provides the maximum software jitter value for the 115200 bps baudrate. The lower the baudrate, the lower the software jitter.
- Baudrate detection using UART auto-baudrate feature. Devices using this mechanism do not present any software jitter.

**Table 6. Jitter software calculation on bootloader USART detection**

| Series or product | Detection method | Maximum software jitter |
|---|---|---|
| STM32C5 | Auto-baudrate | Not applicable |

*Digest note:* Rows for all other series and products were omitted; only the STM32C5 row is kept.

### 4.6 Programming constraints

When using the bootloader interface to write in the flash memory, respect the alignment on the programmed address detailed in Table 7. If the address is not aligned, the operation fails, and all following program operations fail as well.

**Table 7. Flash memory alignment constraints**

| Series | Alignment |
|---|---|
| STM32C5 | 16 bytes |

*Digest note:* Rows for all other series were omitted; only the STM32C5 row is kept.

Examples of alignment:

- 4 bytes: 0x0800 0014 is aligned and passes, 0x0800 0012 is not aligned and fails
- 8 bytes: 0x0800 0010 is aligned and passes, 0x0800 0014 is not aligned and fails

**Note:** On STM32F4 and STM32F7 it is possible to change the alignment constraint by writing in the device feature space.

*Digest note:* For STM32C5 (16 bytes), this means every bootloader write address must be a multiple of 0x10 (for example 0x0800 0010 passes, 0x0800 0018 fails).

### 4.7 ExitSecureMemory feature

The securable memory area is used to isolate secure boot code/data, which handles sensitive information (secrets), from application code. The secure boot code access is controlled by HW (FLASH registers and option bytes, depending on the product). The code is executed once at boot, then locked by HW until the next reset.

The ExitSecureMemory is a software hosted on the system memory. When the user boot code jumps to it, it is possible to enable the hide protection area, and then jump to the application code. The size of the hide protection area (HDP) must be set by the user to the needed value before jumping to the ExitSecureMemory function.

#### 4.7.1 ExitSecureMemory v1.0

As shown in Figure 6, two methods can be used.

1. Jump to the secure memory function without parameters: the application must be loaded just after the defined secure memory area (HDP and size).
2. Jump to the secure memory function using two parameters:
   1. Magic number: 0x08192A3C is used to secure boot code/data in flash/Bank1 and jump in case of a single/dual bank product, 0x08192A3D is used to secure boot code/data and jump to application in Bank2 in case of a dual bank product
   2. User address = Application address: the application can be loaded to any desired address

*Digest note:* The two parameters are lettered a) and b) in the source.

**Figure 6. ExitSecureMemory function usage**

The figure has two parts. In both, system memory holds the Bootloader with ExitSecureMemory, and user flash memory starts with a "Boot code/data (to protect)" area of size SEC/HDP_SIZE.

- Top part, "Jump to the secure memory area without parameters": the Application is located immediately after the boot code/data area. Arrow 1: the boot code jumps to ExitSecureMemory. Arrow 2: ExitSecureMemory jumps to the Application placed right after the protected area. Arrow 3: the result, where the boot code/data area is hidden and the Application remains.
- Bottom part, "Jump to the secure memory area with parameters (magic number and application address)": the Application is located elsewhere in user flash memory, not adjacent to the protected area. Arrow 1: the boot code jumps to ExitSecureMemory. Arrow 2: ExitSecureMemory jumps to the given application address. Arrow 3: the boot code/data area is hidden and the Application remains.

For more information regarding the option bytes configuration, see the reference manual.

For examples of functions that can be used to call ExitSecureMemory, see Appendix A.

For more details refer to Figure 7.

**Figure 7. Access to securable memory area from the bootloader**

Flowchart, as numbered steps:

1. Jump to secure memory address.
2. Check: R1 = Magic number and R2 = User address?
3. If No:
   1. Check link register to know from which bank comes the jump.
   2. Set bank's securable memory bit.
   3. Jump just after securable memory area.
4. If Yes: jump to user address.

A second part of the same figure starts at a "Flash dual bank" node and branches:

1. Single bank: check "Valid magic number?". If Yes: set securable memory bit, then jump to user address.
2. Dual bank: check "Valid magic number?":
   - Bank1: set securable memory bit (Bank1), then jump to user address.
   - Bank2: set securable memory bit (Bank1), then jump to user address.

Notes:

1. The bootloader does not check the integrity of the user address, it is up to the user to ensure the validity of the address to jump to.

*Digest note:* The Bank2 branch box is printed as "Set securable memory bit (Bank1)", which is reproduced here. [unclear in source: the Bank2 branch probably means Bank2.] The figure draws no connector between the "Yes" branch and the "Flash dual bank" part; presumably the "Flash dual bank" part details what happens on the Yes branch. The figure shows no "No" outcome for the "Valid magic number?" decisions.

#### 4.7.2 ExitSecureMemory v1.1

Compared to the ExitSecureMemory v1.0, the user can define an MPU region. This is done using the CPU R3 register, before jumping to the software, that runs as shown in Figure 8.

**Figure 8. Defining an MPU region**

Flowchart, as numbered steps:

1. Jump to secure memory address.
2. Check: R3 = 0xFF?
   - Yes: activate the MPU region using the provided region number.
   - No: activate the MPU region using the provided region number.
3. Execute ExitSecureMemory v1.0.

*Digest note:* Both branches of the R3 = 0xFF decision are printed with the same text. [unclear in source: the figure does not show what differs between the Yes and No branches.]

**Table 8. ExitSecureMemory entry address**

| MCU (series) | MCU (device) | ExitSecureMemory address | Version address | Version |
|---|---|---|---|---|
| STM32C5 | STM32C5xxx | 0x0BF88400 | 0x0BF883E8 | V2.0 (0x20) |

*Digest note:* Rows for STM32G0, STM32G4, STM32C0 and STM32U0 devices were omitted; only the STM32C5 row is kept. The STM32C5 address matches the "Securable memory area" jump address in Table 23.

### 4.8 IWDG usage

The bootloader does not enable IWDG. It tries to update the prescaler value if the IWDG was enabled by HW (through option bytes) or by SW in case of an application that jumps to bootloader.

If the IWDG was not enabled before the boot on bootloader (using HW boot or by a jump from an application), the watchdog prescaler value update bit (PVU) is set to 1 when the bootloader tries to change the prescaler value.

This value does not change, it remains at 0x1 as the prescaler update never happens (IWDG is not enabled), even after the jump. When using the bootloader to jump to the application, and when there is the need to enable the IWDG, consider that the PVU bit in the IWDG_SR register is set to 1.

### 4.9 Bootloader models

To address the evolution of STM32 devices on security, the bootloader (BL) is now available on different models.

1. Legacy model - BL_V1 (see left side of Figure 9):

   The system memory is non secure and allocated to the bootloader. In some projects a SW (functionally independent from the bootloader) called ExitSecureMemory is implemented on the same zone as the BL.
2. New BL model - BL_V2 (see right side of Figure 9)

   The system memory is split between secure and nonsecure areas. The secure area contains the System Flash Secure Package (SFSP), the nonsecure contains the BL.

**Figure 9. BL_V1 (left) and BL_V2 (right) models**

- BL_V1 (left): system memory contains the BL with ExitSecureMemory below it; both are non secure. User flash is separate, below.
- BL_V2 (right): system memory contains the SFSP (secure) above the BL (non secure). User flash is separate, below.

### 4.10 Boot constraints on BL

Boot depends upon the MCU (see Table 9), and adds new constraints to the BL.

- Legacy products - Boot_V1

  When correctly set, the boot is directly on the BL (left side of Figure 10)
- Products with security but no TrustZone isolation - Boot_V2 (right side of Figure 10)

  When correctly set and boot on the BL is possible, the boot starts on the SFSP, then it jumps to the bootloader. This adds a constraint to the boot timing.
- Products with security using TrustZone isolation - Boot_V3

  On this category there are two possibilities:

  1. Boot depending on TrustZone value - Boot_V3_1 (see Figure 11)

     When TZEN is enabled, some constraints are added to the BL functionalities:

     - Boot timing is different from the TZEN disabled use case
     - Before jumping to the BL, the SFSP maps all the needed resources by the BL to the nonsecure domain. A jump from the BL ("Go" command) to an application using other resources does not work.
     - Some secure option bytes are not be accessible as the bootloader is nonsecure. Some APIs are added on the SFSP to guarantee that the BL can modify them on open products states (Open, RDP L0).
     - Some parts of the SRAM are used by the SFSP and remain on Secure domain when jumping to the BL, so are not accessible by the customer through BL
  2. Boot not depending on TrustZone value - Boot_V3_2 (see Figure 12)

     Boot goes through SFSP first, then jumps to the BL. In this model, some constraints are added to the BL functionalities on both TZEN states:

     - Boot timing includes SFSP timing.
     - Before jumping to the BL, the SFSP map all the needed resources by the BL to the nonsecure domain. A jump from the BL ("Go" command) to an application using other resources does not work.
     - Some secure option bytes are not be accessible by the Bootloader as it is nonsecure. Some APIs are added on the SFSP to guarantee that the BL can modify them on open products states (Open).
     - Some parts of the SRAM are used by the SFSP and remain on Secure domain when jumping to the BL, consequently they are not accessible by the customer through BL.

*Digest note:* The two Boot_V3 possibilities are lettered a) and b) in the source, and their sub-items use ">" markers.

**Table 9. BL and boot by product series**

| Series | BL model | Boot |
|---|---|---|
| STM32H7 | BL_V2 | Boot_V2 (see Figure 10) |
| STM32L5, STM32U3, STM32U5, STM32WBA | BL_V2 | Boot_V3_1 (see Figure 11) |
| STM32H5 | BL_V2 | Boot_V3_2 (see Figure 12) |
| Others | BL_V1 | Boot_V1 (see Figure 10) |

*Digest note:* Table 9 is kept in full. STM32C5 falls under "Others" (BL_V1, Boot_V1), consistent with Section 11.1.

**Figure 10. Boot_V1 (left) and Boot_V2 (right)**

- Boot_V1, labelled BL_V1 (left): the boot arrow points directly at the Bootloader.
- Boot_V2, labelled BL_V2 (right): the boot arrow points at the SFSP, which sits above the Bootloader; a "Jump" arrow goes from the SFSP to the Bootloader.

**Figure 11. Boot_V3_1**

- TZEN disabled (left): the boot arrow points directly at the Bootloader; the box above it (the SFSP position on the right-hand drawing) is empty and unlabelled.
- TZEN enabled (right): the boot arrow points at the SFSP; a "Jump" arrow goes from the SFSP to the Bootloader.

**Figure 12. Boot_V3_2**

The boot arrow points at the SFSP; a "Jump" arrow goes from the SFSP to the Bootloader.

## 11 STM32C55xxx/562xx devices

### 11.1 Bootloader configuration

The STM32C55xxx/562xx bootloader is activated by applying Pattern19 (see Table 2). Table 23 shows the hardware resources used by this bootloader.

The bootloader follows boot model V1 (see Section 4.10), so it inherits all its constraints.

**Table 23. STM32C55xxx/562xx configuration in system memory boot mode**

| Bootloader | Feature/Peripheral | State | Comment |
|---|---|---|---|
| Common to all | RCC | HSI enabled | The system clock frequency is derived from HSI which is 144 MHz divided by 3. So, 48 MHz (no PLL). |
| Common to all | RCC | HSI enabled | Clock derived from HSI divided by 3 to have 48 MHz. The clock recovery system (CRS) is enabled for the DFU bootloader. |
| Common to all | RCC | HSE enabled | Enabled only when FDCAN is enabled on the ENGI and option bytes. Quartz value is detected using TIM17. Only values 12, 24, and 48 MHz are supported as source clock of the FDCAN. If no HSE detected or value do match the supported values, HSE is disabled and FDCAN clock is HSI/3. |
| Common to all | RAM | - | 15 Kbytes, starting from address 0x20000000 are used by the bootloader firmware. |
| Common to all | System memory | - | 33 Kbytes, starting from address 0x0BF80080 contain the bootloader firmware. |
| Common to all | IWDG | - | The independent watchdog (IWDG) prescaler is configured to its maximum value. It is periodically refreshed to prevent watchdog reset (in case the hardware IWDG option was previously enabled by the user). |
| Securable memory area | - | - | The address to jump to for the securable memory area is 0x0BF88400. |
| USART1 | USART1 | Enabled | Once initialized, the USART1 configuration is: 8 bits, even parity and 1 Stop bit. |
| USART1 | USART1_RX pin | Input | PA10 pin: USART1 in reception mode. Used in alternate push-pull, pull-up mode. |
| USART1 | USART1_TX pin | Output | PA9 pin: USART1 in transmission mode. Kept in reset configuration until 0x7F detected on USART_RX. |
| USART2 | USART2 | Enabled | Once initialized, the USART2 configuration is: 8 bits, even parity and 1 Stop bit. |
| USART2 | USART2_RX pin | Input | PA3 pin: USART2 in reception mode. Used in alternate push-pull, pull-up mode. |
| USART2 | USART2_TX pin | Output | PA2 pin: USART2 in transmission mode. Kept in reset configuration until 0x7F detected on USART_RX. |
| USART3 | USART3 | Enabled | Once initialized, the USART3 configuration is: 8 bits, even parity and 1 Stop bit. |
| USART3 | USART3_RX pin | Input | PD9 pin: USART3 in reception mode. Used in alternate push-pull, pull-up mode. |
| USART3 | USART3_TX pin | Output | PD8 pin:USART3 in transmission mode. Kept in reset configuration until 0x7F detected on USART_RX. |
| UART4 | UART4 | Enabled | Once initialized, the UART4 configuration is: 8 bits, even parity and 1 Stop bit. |
| UART4 | UART4_RX pin | Input | PA1 pin: UART4 in reception mode. Used in alternate push-pull, pull-up mode. |
| UART4 | UART4_TX pin | Output | PA0 pin: UART4 in transmission mode. Kept in reset configuration until 0x7F detected on USART_RX. |
| FDCAN1 | FDCAN1 | Enabled | Once initialized, the FDCAN1 configuration is: Connection bit rate 250 kbit/s; Data bit rate 1000 kbit/s; FrameFormat = FDCAN_FRAME_FD_BRS; Mode = FDCAN_MODE_NORMAL; AutoRetransmission = ENABLE; TransmitPause = DISABLE; ProtocolException = ENABLE |
| FDCAN1 | FDCAN1_RX pin | Input | PB5 pin: FDCAN1 in reception mode. Used in alternate push-pull, no pull mode. |
| FDCAN1 | FDCAN1_TX pin | Output | PB6 pin: FDCAN1 in transmission mode. Used in alternate push-pull, no pull mode. |
| SPI1 | SPI1_MOSI pin | Input | PA7 pin: Slave data Input line, used in push-pull, pull-down mode. |
| SPI1 | SPI1_MISO pin(1) | Output | PA6 pin: Slave data output line, used in push-pull, pull-down mode. |
| SPI1 | SPI1_SCK pin | Input | PA5 pin: Slave clock line, used in push-pull, pull-down mode. |
| SPI1 | SPI1_NSS pin | Input | PA4 pin: Slave chip select pin used in push-pull, pull-down mode. |
| SPI2 | SPI2_MOSI pin | Input | PB15 pin: Slave data Input line, used in push-pull, pull-down mode. |
| SPI2 | SPI2_MISO pin(1) | Output | PB14 pin: Slave data output line, used in push-pull, pull-down mode |
| SPI2 | SPI2_SCK pin | Input | PB13 pin: Slave clock line, used in push-pull, pull-down mode. |
| SPI2 | SPI2_NSS pin | Input | PB12 pin: slave chip select pin used in push-pull, pull-down mode. |
| SPI3 | SPI3_MOSI pin | Input | PB2 pin: Slave data Input line, used in push-pull, pull-down mode. |
| SPI3 | SPI3_MISO pin(1) | Output | PB0 pin: Slave data output line, used in push-pull, pull-down mode |
| SPI3 | SPI3_SCK pin | Input | PB1 pin: Slave clock line, used in push-pull, pull-down mode. |
| SPI3 | SPI3_NSS pin | Input | PB8 pin: slave chip select pin used in push-pull, pull-down mode. |
| DFU | USB | Enabled | USB FS configured in forced device mode. USB FS interrupt vector is enabled and used for USB DFU communications. |
| DFU | USB_DM pin | Input/Output | PA11 pin: Not configured by bootloader SW. |
| DFU | USB_DP pin | Input/Output | PA12 pin: Not configured by bootloader SW. |

Notes:

1. SPI Tx (MISO) is handled by DMA. On the bootloader start-up after SPI initialization as soon as the bit DMATx enable on SPI CR2 register is set to 0x1, the MISO line is set to 3.3 V.

*Digest note:* "ENGI" (HSE row) is reproduced as printed. [unclear in source: "ENGI" is not defined in this document; the HSE row says FDCAN must be enabled "on the ENGI and option bytes", and Figure 19 says "Enable HSE when FDCAN enabled by ENGI".] The phrase "If no HSE detected or value do match the supported values" is reproduced as printed; it presumably means "do not match".

*Digest note:* The first two RCC rows are two separate comment cells that share the merged "HSI enabled" state cell in the source.

**Table 24. STM32C55xxx/562xx special commands**

Table header (spanning all columns): Special commands supported (USART/SPI/FDCAN), Opcode – 0x50.

| Function | Sub-Opcode (2 bytes) | Number of data sent (2 bytes) | Data sent | Number of data received | Data received (2 bytes) | Number of status data received (2 bytes) | Status data received |
|---|---|---|---|---|---|---|---|
| Reset | 0x02 | 0x4 | 0x0 | 0x0 | NA | 0x1 | 0x0 |
| Erase EEPROM | 0xA4 | 0x4 | Page number to erase | 0x0 | NA | 0x1 | 0x0 |

**Note:** USB special commands differ from other protocols due to USB protocol specificities:

- No opcode is used; the sub-opcode is used directly.
- The sub-opcode is treated as a single byte, not two bytes.
- Data is sent on the USB frame byte by byte; there is no need to specify the number of data bytes to be transmitted.
- Returned data and status are formatted according to the native USB protocol.

### 11.2 Bootloader selection

Figure 19 shows the bootloader selection mechanism.

**Figure 19. Bootloader V16.x selection for STM32C55xxx/562xx devices**

Flowchart, as numbered steps:

1. Entry: System Reset Or JumpToBL.
2. De-initialize system. Configure system clock to 48 MHz HSI (HSI/3). Enable HSE when FDCAN enabled by ENGI. System init. (GPIOs, IWDG, SysTick).
3. Configure USARTx.
4. Configure SPIx.
5. Configure USB_FS device.
6. Configure FDCANx.
7. Interface detection, checked in this order:
   1. 0x7F detected on USART Tx? If Yes: disable all interrupt sources and other interface clocks, then execute BL_USART_Loop for USARTx.
   2. Otherwise, FDCAN frame detected? If Yes: disable all interrupt sources and other interface clocks, then execute BL_FDCAN_Loop for FDCANx.
   3. Otherwise, SPIx detects synchro mechanism? If Yes: disable all interrupt sources and other interface clocks, then execute BL_SPI_Loop for SPIx.
   4. Otherwise, USB cable detected? If Yes: disable all interrupt sources and other interface clocks, then execute DFU bootloader using USB interrupts.

*Digest note:* The first decision is printed "0x7F detected on USART Tx"; Table 23 says the TX pin is kept in reset configuration "until 0x7F detected on USART_RX", so the byte is received on RX. [unclear in source: the figure draws no "No" exit from the last decision (USB cable detected); presumably detection loops back to step 7.1.]

### 11.3 Bootloader version

Table 22 lists the STM32C55xxx/562xx devices bootloader versions.

**Table 25. STM32C55xxx/562xx bootloader versions**

| Bootloader version number | Description | Known limitations |
|---|---|---|
| V16.1 | Initial bootloader version | None |

*Digest note:* The sentence above refers to "Table 22" as printed; the STM32C55xxx/562xx version table is Table 25 (Table 22 is the STM32C531xx/532xx/542xx version table). V16.1 corresponds to bootloader ID 0x101 in Table 3.
