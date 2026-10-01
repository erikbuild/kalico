# RM0522 Chapter 2: Memory and bus architecture

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 87–98.

## 2.1 System architecture

The STM32C5 architecture relies on an Arm Cortex-M33 core, optimized for execution thanks to an instruction cache (ICACHE) that has a direct access to the embedded flash memory (FLASH).

This architecture also features a 32-bit multilayer AHB bus matrix with the interconnections details in Table 1 and Table 2.

**Table 1. Implementation of masters on STM32C5 series**

| Master | Comment | STM32C53x/542 | STM32C55x/562 | STM32C59x/5A3 |
|---|---|---|---|---|
| Cortex-M33 Fast C-bus | Connecting Cortex-M33 (with FPU) to the internal SRAMs and flash memory through ICACHE | X | X | X |
| Cortex-M33 Slow C-bus | Connecting Cortex-M33 (with FPU) to the external memories through ICACHE | - | - | X |
| Cortex-M33 S-bus | Connecting the Cortex-M33 (with FPU) to internal SRAMs without latency | 2 masters | 2 masters | 2 masters |
| LPDMA1 | - | 1 master | 1 master | 1 master |
| LPDMA2 | - | 1 master | 1 master | 1 master |
| Ethernet MAC | - | - | - | X(1) |

Notes:

1. Not available on STM32C591xx devices.

*Digest note:* In the source, "2 masters" and "1 master" are single cells merged across the three device columns; they are repeated here per column. The Comment cells for LPDMA1, LPDMA2 and Ethernet MAC are empty in the source.

**Table 2. Implementation of slaves on STM32C5 series**

| Slave | Comment | STM32C53x/542 | STM32C55x/562 | STM32C59x/5A3 |
|---|---|---|---|---|
| Flash memory | - | X | X | X |
| SRAM1 | - | X | X | X |
| SRAM2 | - | X | X | X |
| AHB1 | Peripherals including AHB and APB bridge, and APB peripherals (connected to APB1 and APB2) | X | X | X |
| AHB2 | Peripherals | X | X | X |
| XSPI1 | - | - | - | X |
| AHB3 | Including AHB to APB bridge, and APB peripherals (connected to APB3) | X | X | X |
| AHB4 | Peripherals | - | - | X |

*Digest note:* On STM32C551/C552 (C55xxx) there is no Slow C-bus, no Ethernet MAC master, no XSPI1 slave and no AHB4 slave.

The bus matrix provides access from a master to a slave, enabling concurrent access and efficient operation, even when several high-speed peripherals work simultaneously.

This architecture is shown in Figure 1.

**Figure 1. System architecture** (ST drawing MSv76095V2)

The figure shows the Cortex-M33 with FPU at the top with two bus outputs, C-bus and S-bus. The C-bus enters the ICACHE (8-Kbyte). The ICACHE has two outputs: the Slow-bus, which goes directly to a master port of the 32-bit bus matrix, and the Fast-bus, which passes through a demultiplexer. One output of that demultiplexer goes to a master port of the bus matrix; the other is a dedicated "128-bit cache refill" path that bypasses the bus matrix and feeds a 2-input multiplexer placed directly in front of the Flash memory slave (the other input of that multiplexer is the bus-matrix flash port). The S-bus goes directly to a master port of the bus matrix. LPDMA1, LPDMA2 and ETHERNET MAC each have one master port into the bus matrix.

The bus matrix slave ports (top to bottom) are: Flash memory (through the multiplexer above), SRAM1, SRAM2, AHB1 peripherals, AHB2 peripherals, XSPI1, AHB3 peripherals and AHB4 peripherals. ETHERNET MAC, XSPI1 and AHB4 peripherals are shaded as "STM32C59x/C5A3x only". The legend distinguishes a "bus multiplexer" (open circle) from a "fast bus multiplexer" (filled circle), and a master interface symbol from a slave interface symbol.

The crossing points drawn in the matrix (master column to slave row) are summarized below (derived from the figure; "fast" = fast bus multiplexer, "mux" = bus multiplexer, "-" = no connection drawn):

| Slave port | Slow-bus (ICACHE) | Fast-bus (ICACHE) | S-bus | LPDMA1 | LPDMA2 | ETHERNET MAC |
|---|---|---|---|---|---|---|
| Flash memory | - | - (uses the 128-bit cache refill path) | - | mux | mux | mux |
| SRAM1 | - | mux | fast | fast | mux | fast |
| SRAM2 | - | fast | mux | mux | fast | mux |
| AHB1 peripherals | - | - | mux | mux | mux | - |
| AHB2 peripherals | - | - | mux | mux | mux | - |
| XSPI1 | fast | - | mux | mux | mux | mux |
| AHB3 peripherals | - | - | mux | mux | mux | - |
| AHB4 peripherals | - | - | mux | mux | mux | - |

*Digest note:* The figure draws S-bus connections to XSPI1 and AHB4, and LPDMA connections to XSPI1, which the text of Sections 2.1.3 and 2.1.4 does not list. Both slaves exist only on STM32C59x/5A3, so this does not affect STM32C55xxx.

### 2.1.1 Fast C-bus

This bus connects the C-bus of the Cortex-M33 core to the FLASH and to the bus matrix through the ICACHE. This bus is used for instruction fetch and data access to the internal memories mapped in code region. This bus targets the FLASH and the internal SRAMs (SRAM1/2).

SRAM1 and SRAM2 are accessible on this bus with a continuous mapping.

### 2.1.2 Slow C-bus

This bus connects the C-bus of the Cortex-M33 core to the bus matrix through the instruction cache. This bus is used for instruction fetch and data access to the external memories mapped in code region. This bus targets the external memories (XSPI).

*Digest note:* The Slow C-bus exists only on STM32C59x/5A3 (Table 1); it is absent on STM32C55xxx.

### 2.1.3 S-bus

This bus connects the system bus of the Cortex-M33 core to the bus matrix. This bus is used by the core to access data located in a peripheral or SRAM area. This bus targets the internal SRAMs (SRAM1/2), the AHB1 peripherals (including APB1/2), AHB2, and AHB3 peripherals.

SRAM1 and SRAM2 are accessible on this bus with a continuous mapping.

### 2.1.4 LPDMA1 and LPDMA2 buses

These buses connect the two AHB master interfaces of LPDMA1/2 to the bus matrix. These buses target the FLASH, the internal SRAMs (SRAM1/2), the AHB1 peripherals (including APB1/2), AHB2, AHB3, and AHB4 peripherals.

### 2.1.5 Bus matrix

The bus matrix manages the access arbitration between masters. The arbitration uses a Round-Robin algorithm. This bus matrix features a fast bus multiplexer used to connect each master to a given slave without latency (see Figure 1). For the same master, other slaves undergo a latency of at least one cycle at each new access.

### 2.1.6 AHB/APB bridges

The three AHB/APB bridges provide full synchronous connections between AHB and APB buses, allowing flexible selection of the peripheral frequency.

Refer to Section 2.2.2: Memory map and register boundary addresses for the address mapping of the peripherals connected to these bridges.

After each device reset, all peripheral clocks are disabled (except for internal SRAMs and FLASH). Before using a peripheral, its clock must be enabled in RCC_AHBxENR and RCC_APBxENR registers.

Note: When an 8- or 16-bit access is performed on an APB register, the access is transformed into a 32-bit access: the bridge duplicates the 8- or 16-bit data to feed the 32-bit vector.

## 2.2 Memory organization

### 2.2.1 Introduction

Program memory, data memory, registers and I/O ports are organized within the same linear address space.

The bytes are coded in memory in Little Endian format. The lowest numbered byte in a word is considered the word's least significant byte and the highest numbered byte the most significant.

### 2.2.2 Memory map and register boundary addresses

The three memory-map figures share the same structure: a full 4-Gbyte map on the left, with two expanded detail columns on the right (peripheral region and code region). Addresses below are listed from high to low, as drawn. Each region spans from its listed lower boundary up to the next listed boundary. The figures mix boundary styles: most labels are the start address of the next region (exclusive), but 0x08FF F1FF, 0x08FF FDFF, 0x0BF8 FFFF and 0x1FFF FFFF are drawn as last-byte (inclusive) addresses; the values are reproduced exactly as drawn.

**Figure 2. Memory map for STM32C53x/542** (ST drawing MSv76096V3)

Full map:

| Region | Address range |
|---|---|
| Cortex M33 | 0xE000 0000 - 0xFFFF FFFF |
| Reserved | 0x6000 0000 - 0xE000 0000 |
| Peripherals | 0x4000 0000 - 0x6000 0000 |
| Reserved | 0x2001 0000 - 0x4000 0000 |
| SRAM2 (32 KB) | 0x2000 8000 - 0x2001 0000 |
| SRAM1 (32 KB) | 0x2000 0000 - 0x2000 8000 |
| Code | 0x0000 0000 - 0x2000 0000 |

Peripheral detail (0x4000 0000 - 0x5000 0000):

| Region | Address range |
|---|---|
| Reserved | 0x4402 5000 - 0x5000 0000 |
| AHB3 | 0x4402 0800 - 0x4402 5000 |
| Reserved | 0x4400 8000 - 0x4402 0800 |
| APB3 | 0x4400 0400 - 0x4400 8000 |
| Reserved | 0x420C 0C00 - 0x4400 0400 |
| AHB2 | 0x4202 0000 - 0x420C 0C00 |
| Reserved | 0x4003 0800 - 0x4202 0000 |
| AHB1 | 0x4002 0000 - 0x4003 0800 |
| Reserved | 0x4001 6C00 - 0x4002 0000 |
| APB2 | 0x4001 2C00 - 0x4001 6C00 |
| Reserved | 0x4000 B400 - 0x4001 2C00 |
| APB1 | 0x4000 0000 - 0x4000 B400 |

Code-region detail (0x0000 0000 - 0x1FFF FFFF):

| Region | Address range |
|---|---|
| Reserved | 0x0BF8 FFFF - 0x1FFF FFFF |
| System memory | 0x0BF8 0000 - 0x0BF8 FFFF |
| Reserved | 0x0A01 0000 - 0x0BF8 0000 |
| SRAM2 | 0x0A00 8000 - 0x0A01 0000 |
| SRAM1 | 0x0A00 0000 - 0x0A00 8000 |
| Reserved | 0x0900 C000 - 0x0A00 0000 |
| EDATA_EN = 0b1 (48 KB) | 0x0900 0000 - 0x0900 C000 |
| Reserved | 0x08FF FDFF - 0x0900 0000 |
| RO (1.5 KB) | 0x08FF F800 - 0x08FF FDFF |
| Reserved | 0x08FF F1FF - 0x08FF F800 |
| OTP (4.5 KB) | 0x08FF E000 - 0x08FF F1FF |
| Reserved | 0x0841 0000 - 0x08FF E000 |
| EDATA_EN = 0b0 (64 KB) | 0x0840 0000 - 0x0841 0000 |
| Reserved | 0x0804 0000 - 0x0840 0000 |
| FLASH (256KB) | 0x0800 0000 - 0x0804 0000 |
| Reserved | 0x0000 0000 - 0x0800 0000 |

**Figure 3. Memory map for STM32C55x/562** (ST drawing MSv74188V3)

Full map:

| Region | Address range |
|---|---|
| Cortex M33 | 0xE000 0000 - 0xFFFF FFFF |
| Reserved | 0x6000 0000 - 0xE000 0000 |
| Peripherals | 0x4000 0000 - 0x6000 0000 |
| Reserved | 0x2002 0000 - 0x4000 0000 |
| SRAM2 (64 KB) | 0x2001 0000 - 0x2002 0000 |
| SRAM1 (64 KB) | 0x2000 0000 - 0x2001 0000 |
| Code | 0x0000 0000 - 0x2000 0000 |

Peripheral detail (0x4000 0000 - 0x5000 0000):

| Region | Address range |
|---|---|
| Reserved | 0x4402 5000 - 0x5000 0000 |
| AHB3 | 0x4402 0800 - 0x4402 5000 |
| Reserved | 0x4400 8000 - 0x4402 0800 |
| APB3 | 0x4400 0400 - 0x4400 8000 |
| Reserved | 0x420C 0C00 - 0x4400 0400 |
| AHB2 | 0x4202 0000 - 0x420C 0C00 |
| Reserved | 0x4003 0800 - 0x4202 0000 |
| AHB1 | 0x4002 0000 - 0x4003 0800 |
| Reserved | 0x4001 6C00 - 0x4002 0000 |
| APB2 | 0x4001 2C00 - 0x4001 6C00 |
| Reserved | 0x4000 B000 - 0x4001 2C00 |
| APB1 | 0x4000 0000 - 0x4000 B000 |

Code-region detail (0x0000 0000 - 0x1FFF FFFF):

| Region | Address range |
|---|---|
| Reserved | 0x0BF8 FFFF - 0x1FFF FFFF |
| System memory | 0x0BF8 0000 - 0x0BF8 FFFF |
| Reserved | 0x0A02 0000 - 0x0BF8 0000 |
| SRAM2 | 0x0A01 0000 - 0x0A02 0000 |
| SRAM1 | 0x0A00 0000 - 0x0A01 0000 |
| Reserved | 0x0900 C000 - 0x0A00 0000 |
| EDATA_EN = 0b1 (48 KB) | 0x0900 0000 - 0x0900 C000 |
| Reserved | 0x08FF FDFF - 0x0900 0000 |
| RO (1.5 KB) | 0x08FF F800 - 0x08FF FDFF |
| Reserved | 0x08FF F1FF - 0x08FF F800 |
| OTP (4.5 KB) | 0x08FF E000 - 0x08FF F1FF |
| Reserved | 0x0841 0000 - 0x08FF E000 |
| EDATA_EN = 0b0 (64 KB) | 0x0840 0000 - 0x0841 0000 |
| Reserved | 0x0808 0000 - 0x0840 0000 |
| FLASH (512KB) | 0x0800 0000 - 0x0808 0000 |
| Reserved | 0x0000 0000 - 0x0800 0000 |

*Digest note:* For STM32C551/C552 the SRAM is contiguous: SRAM1 0x2000 0000 - 0x2000 FFFF plus SRAM2 0x2001 0000 - 0x2001 FFFF (128 Kbytes total, top of RAM = 0x2002 0000), with C-bus aliases at 0x0A00 0000 - 0x0A01 FFFF. The topmost RAM words are therefore in SRAM2, which has the ECC, tamper-erase, POR-erase and optional reset-erase behavior described in Chapter 3 (Table 12) and Chapter 5. The APB1 region ends at 0x4000 B000 on C55x/562 (vs 0x4000 B400 on the other lines) because the FDCAN message RAM is smaller (see Table 3 note 1). The figure shows the 512-Kbyte flash size; the C55xxx datasheet also lists 256-Kbyte parts. The ST CMSIS header (stm32c552xx.h) names 0x0840 0000 FLASH_EXT_USER_BASE ("FLASH extended user") and 0x0900 0000 FLASH_EDATA_BASE ("FLASH high-cycle data"), places UID_BASE at 0x08FF F800, FLASHSIZE_BASE at 0x08FF F80C and PACKAGE_BASE at 0x08FF F80E (all inside the "RO" area), and FLASH_SYSTEM_BASE at 0x0BF8 0000 with size 0x10000. The figure labels the two data-flash windows only by the EDATA_EN option value; which window is active is selected by the EDATA_EN option bit described in Section 6 (FLASH).

**Figure 4. Memory map for STM32C59x/5A3** (ST drawing MSv76097V3)

Full map:

| Region | Address range |
|---|---|
| Cortex M33 | 0xE000 0000 - 0xFFFF FFFF |
| Reserved | 0xA000 0000 - 0xE000 0000 |
| External memory | 0x9000 0000 - 0xA000 0000 |
| Reserved | 0x6000 0000 - 0x9000 0000 |
| Peripherals | 0x4000 0000 - 0x6000 0000 |
| Reserved | 0x2004 0000 - 0x4000 0000 |
| SRAM2 (128 KB) | 0x2002 0000 - 0x2004 0000 |
| SRAM1 (128 KB) | 0x2000 0000 - 0x2002 0000 |
| Code | 0x0000 0000 - 0x2000 0000 |

Peripheral detail (0x4000 0000 - 0x5000 0000):

| Region | Address range |
|---|---|
| Reserved | 0x4700 1800 - 0x5000 0000 |
| AHB4 | 0x4600 F000 - 0x4700 1800 |
| Reserved | 0x4402 5000 - 0x4600 F000 |
| AHB3 | 0x4402 0800 - 0x4402 5000 |
| Reserved | 0x4400 8000 - 0x4402 0800 |
| APB3 | 0x4400 0400 - 0x4400 8000 |
| Reserved | 0x420C 8000 - 0x4400 0400 |
| AHB2 | 0x4202 0000 - 0x420C 8000 |
| Reserved | 0x4003 0800 - 0x4202 0000 |
| AHB1 | 0x4002 0000 - 0x4003 0800 |
| Reserved | 0x4001 6C00 - 0x4002 0000 |
| APB2 | 0x4001 2C00 - 0x4001 6C00 |
| Reserved | 0x4000 B400 - 0x4001 2C00 |
| APB1 | 0x4000 0000 - 0x4000 B400 |

Code-region detail (0x0000 0000 - 0x1FFF FFFF):

| Region | Address range |
|---|---|
| Reserved | 0x0BF8 FFFF - 0x1FFF FFFF |
| System memory | 0x0BF8 0000 - 0x0BF8 FFFF |
| Reserved | 0x0A04 0000 - 0x0BF8 0000 |
| SRAM2 | 0x0A02 0000 - 0x0A04 0000 |
| SRAM1 | 0x0A00 0000 - 0x0A02 0000 |
| Reserved | 0x0900 C000 - 0x0A00 0000 |
| EDATA_EN = 0b1 (48 KB) | 0x0900 0000 - 0x0900 C000 |
| Reserved | 0x08FF FDFF - 0x0900 0000 |
| RO (1.5 KB) | 0x08FF F800 - 0x08FF FDFF |
| Reserved | 0x08FF F1FF - 0x08FF F800 |
| OTP (4.5 KB) | 0x08FF E000 - 0x08FF F1FF |
| Reserved | 0x0841 0000 - 0x08FF E000 |
| EDATA_EN = 0b0 (64 KB) | 0x0840 0000 - 0x0841 0000 |
| Reserved | 0x0810 0000 - 0x0840 0000 |
| FLASH (1MB) | 0x0800 0000 - 0x0810 0000 |
| External memories | 0x0000 0000 - 0x0800 0000 |

All the memory map areas that are not allocated to on-chip memories and peripherals are considered "Reserved". The following table gives the boundary addresses of the peripherals available in the devices.

**Table 3. Memory map and peripheral register boundary addresses**

| Bus | Boundary address | Peripheral | Peripheral register map | STM32C53x/542 | STM32C55x/562 | STM32C59x/5A3 |
|---|---|---|---|---|---|---|
| AHB4 | 0x4700 1800 - 0x47FF FFFF | Reserved | - | - | - | - |
| AHB4 | 0x4700 1400 - 0x4700 17FF | XSPI1 | XSPI register map | - | - | X |
| AHB4 | 0x4600 F400 - 0x4700 13FF | Reserved | - | - | - | - |
| AHB4 | 0x4600 F000 - 0x4600 F3FF | DLYBXS1 | DLYB register map | - | - | X |
| AHB4 | 0x4600 0000 - 0x4600 EFFF | Reserved | - | - | - | - |
| AHB3 | 0x4402 5000 - 0x44FF FFFF | Reserved | - | - | - | - |
| AHB3 | 0x4402 4000 - 0x4402 4FFF | DEBUG | DEBUG register map | X | X | X |
| AHB3 | 0x4402 2400 - 0x4402 3FFF | Reserved | - | - | - | - |
| AHB3 | 0x4402 2000 - 0x4402 23FF | EXTI | EXTI register map | X | X | X |
| AHB3 | 0x4402 1000 - 0x4402 1FFF | Reserved | - | - | - | - |
| AHB3 | 0x4402 0C00 - 0x4402 0FFF | RCC | RCC register map | X | X | X |
| AHB3 | 0x4402 0800 - 0x4402 0BFF | PWR | PWR register map | X | X | X |
| AHB3 | 0x4402 0000 - 0x4402 07FF | Reserved | - | - | - | - |
| APB3 | 0x4400 8000 - 0x4400 FFFF | Reserved | - | - | - | - |
| APB3 | 0x4400 7C00 - 0x4400 7FFF | TAMP | TAMP register map | X | X | X |
| APB3 | 0x4400 7800 - 0x4400 7BFF | RTC | RTC register map | X | X | X |
| APB3 | 0x4400 4800 - 0x4400 77FF | Reserved | - | - | - | - |
| APB3 | 0x4400 4400 - 0x4400 47FF | LPTIM1 | LPTIM1 register map | X | X | X |
| APB3 | 0x4400 2800 - 0x4400 43FF | Reserved | - | - | - | - |
| APB3 | 0x4400 2400 - 0x4400 27FF | LPUART1 | LPUART register map | X | X | X |
| APB3 | 0x4400 0800 - 0x4400 23FF | Reserved | - | - | - | - |
| APB3 | 0x4400 0400 - 0x4400 07FF | SBS | SBS register map | X | X | X |
| APB3 | 0x4400 0000 - 0x4400 03FF | Reserved | - | - | - | - |
| AHB2 | 0x420C 8000 - 0x43FF FFFF | Reserved | - | - | - | - |
| AHB2 | 0x420C 7C00 - 0x420C 7FFF | CCB | CCB register map | - | - | X |
| AHB2 | 0x420C 4000 - 0x420C 7BFF | Reserved | - | - | - | - |
| AHB2 | 0x420C 2000 - 0x420C 3FFF | PKA | PKA register map | - | - | X |
| AHB2 | 0x420C 1000 - 0x420C 1FFF | Reserved | - | - | - | - |
| AHB2 | 0x420C 0C00 - 0x420C 0FFF | SAES | SAES register map | - | - | X |
| AHB2 | 0x420C 0800 - 0x420C 0BFF | RNG | RNG register map | X | X | X |
| AHB2 | 0x420C 0400 - 0x420C 07FF | HASH | HASH register map | X | X | X |
| AHB2 | 0x420C 0000 - 0x420C 03FF | AES | AES register map | X | X | X |
| AHB2 | 0x4202 DC00 - 0x420B FFFF | Reserved | - | - | - | - |
| AHB2 | 0x4202 DB00 - 0x4202 DBFF | ADCC3 | ADC register map | - | - | X |
| AHB2 | 0x4202 D900 - 0x4202 DAFF | Reserved | - | - | - | - |
| AHB2 | 0x4202 D800 - 0x4202 D8FF | ADC3 | ADC register map | - | - | X |
| AHB2 | 0x4202 8800 - 0x420B D7FF | Reserved | - | - | - | - |
| AHB2 | 0x4202 8400 - 0x4202 87FF | DAC1 | DAC register map | X | X | X |
| AHB2 | 0x4202 8300 - 0x4202 83FF | ADCC12 | ADC register map | X | X | X |
| AHB2 | 0x4202 8200 - 0x4202 82FF | Reserved | - | - | - | - |
| AHB2 | 0x4202 8100 - 0x4202 81FF | ADC2 | ADC register map | - | X | X |
| AHB2 | 0x4202 8000 - 0x4202 80FF | ADC1 | ADC register map | X | X | X |
| AHB2 | 0x4202 2000 - 0x4202 7FFF | Reserved | - | - | - | - |
| AHB2 | 0x4202 1C00 - 0x4202 1FFF | GPIOH | GPIO register map | X | X | X |
| AHB2 | 0x4202 1800 - 0x4202 1BFF | GPIOG | GPIO register map | - | - | X |
| AHB2 | 0x4202 1400 - 0x4202 17FF | GPIOF | GPIO register map | - | - | X |
| AHB2 | 0x4202 1000 - 0x4202 13FF | GPIOE | GPIO register map | X | X | X |
| AHB2 | 0x4202 0C00 - 0x4202 0FFF | GPIOD | GPIO register map | X | X | X |
| AHB2 | 0x4202 0800 - 0x4202 0BFF | GPIOC | GPIO register map | X | X | X |
| AHB2 | 0x4202 0400 - 0x4202 07FF | GPIOB | GPIO register map | X | X | X |
| AHB2 | 0x4202 0000 - 0x4202 03FF | GPIOA | GPIO register map | X | X | X |
| AHB1 | 0x4003 0800 - 0x41FF FFFF | Reserved | - | - | - | - |
| AHB1 | 0x4003 0400 - 0x4003 07FF | ICACHE | ICACHE register map | X | X | X |
| AHB1 | 0x4002 9400 - 0x4003 03FF | Reserved | - | - | - | - |
| AHB1 | 0x4002 8000 - 0x4002 93FF | ETHERNET MAC | ETHERNET register map | - | - | X |
| AHB1 | 0x4002 7000 - 0x4002 7FFF | Reserved | - | - | - | - |
| AHB1 | 0x4002 6000 - 0x4002 6FFF | RAMCFG | RAMCFG register map | X | X | X |
| AHB1 | 0x4002 3C00 - 0x4002 5FFF | Reserved | - | - | - | - |
| AHB1 | 0x4002 3800 - 0x4002 3BFF | CORDIC | CORDIC register map | X | X | X |
| AHB1 | 0x4002 3400 - 0x4002 37FF | Reserved | - | - | - | - |
| AHB1 | 0x4002 3000 - 0x4002 33FF | CRC | CRC register map | X | X | X |
| AHB1 | 0x4002 2400 - 0x4002 2FFF | Reserved | - | - | - | - |
| AHB1 | 0x4002 2000 - 0x4002 23FF | FLASH | FLASH register map | X | X | X |
| AHB1 | 0x4002 1000 - 0x4002 1FFF | LPDMA2 | LPDMA register map | X | X | X |
| AHB1 | 0x4002 0000 - 0x4002 0FFF | LPDMA1 | LPDMA register map | X | X | X |
| APB2 | 0x4001 6C00 - 0x4001 FFFF | Reserved | - | - | - | - |
| APB2 | 0x4001 6400 - 0x4001 6BFF | USB RAM | USB register map | X | X | X |
| APB2 | 0x4001 6000 - 0x4001 63FF | USB | USB register map | X | X | X |
| APB2 | 0x4001 4C00 - 0x4001 5FFF | Reserved | - | - | - | - |
| APB2 | 0x4001 4800 - 0x4001 4BFF | TIM17 | TIM17 register map | - | X | X |
| APB2 | 0x4001 4400 - 0x4001 47FF | TIM16 | TIM16 register map | - | X | X |
| APB2 | 0x4001 4000 - 0x4001 43FF | TIM15 | TIM15 register map | X | X | X |
| APB2 | 0x4001 3C00 - 0x4001 3FFF | Reserved | - | - | - | - |
| APB2 | 0x4001 3800 - 0x4001 3BFF | USART1 | USART register map | X | X | X |
| APB2 | 0x4001 3400 - 0x4001 37FF | TIM8 | TIM8 register map | X | X | X |
| APB2 | 0x4001 3000 - 0x4001 33FF | SPI1 / I2S1 | SPI register map | X | X | X |
| APB2 | 0x4001 2C00 - 0x4001 2FFF | TIM1 | TIM1 register map | X | X | X |
| APB2 | 0x4001 0000 - 0x4001 2BFF | Reserved | - | - | - | - |
| APB1 | 0x4000 B400 - 0x4000 FFFF | Reserved | - | - | - | - |
| APB1 | 0x4000 AC00 - 0x4000 B3FF | FDCAN SRAM(1) | FDCAN register map | X | X | X |
| APB1 | 0x4000 A800 - 0x4000 ABFF | FDCAN2 | FDCAN register map | X | - | X |
| APB1 | 0x4000 A400 - 0x4000 A7FF | FDCAN1 | FDCAN register map | X | X | X |
| APB1 | 0x4000 7C00 - 0x4000 A3FF | Reserved | - | - | - | - |
| APB1 | 0x4000 7800 - 0x4000 7BFF | UART7 | USART register map | - | - | X |
| APB1 | 0x4000 6800 - 0x4000 77FF | Reserved | - | - | - | - |
| APB1 | 0x4000 6400 - 0x4000 67FF | USART6 | USART register map | - | - | X |
| APB1 | 0x4000 6000 - 0x4000 63FF | CRS | CRS register map | X | X | X |
| APB1 | 0x4000 5C00 - 0x4000 5FFF | I3C1 | I3C register map | X | X | X |
| APB1 | 0x4000 5800 - 0x4000 5BFF | I2C2 | I2C register map | - | X | X |
| APB1 | 0x4000 5400 - 0x4000 57FF | I2C1 | I2C register map | X | X | X |
| APB1 | 0x4000 5000 - 0x4000 53FF | UART5 | USART register map | X | X | X |
| APB1 | 0x4000 4C00 - 0x4000 4FFF | UART4 | USART register map | X | X | X |
| APB1 | 0x4000 4800 - 0x4000 4BFF | USART3 | USART register map | - | X | X |
| APB1 | 0x4000 4400 - 0x4000 47FF | USART2 | USART register map | X | X | X |
| APB1 | 0x4000 4000 - 0x4000 43FF | COMP12(2) | COMP register map | X | X | X |
| APB1 | 0x4000 3C00 - 0x4000 3FFF | SPI3 / I2S3 | SPI register map | - | X | X |
| APB1 | 0x4000 3800 - 0x4000 3BFF | SPI2 / I2S2 | SPI register map | X | X | X |
| APB1 | 0x4000 3400 - 0x4000 37FF | OPAMP1 | OPAMP register map | X | - | - |
| APB1 | 0x4000 3000 - 0x4000 33FF | IWDG | IWDG hardware configuration register (IWDG_HWCFGR) | X | X | X |
| APB1 | 0x4000 2C00 - 0x4000 2FFF | WWDG | WWDG register map | X | X | X |
| APB1 | 0x4000 1C00 - 0x4000 2BFF | Reserved | - | - | - | - |
| APB1 | 0x4000 1800 - 0x4000 1BFF | TIM12 | TIM12 register map | X | X | X |
| APB1 | 0x4000 1400 - 0x4000 17FF | TIM7 | TIM6/TIM7 register map | X | X | X |
| APB1 | 0x4000 1000 - 0x4000 13FF | TIM6 | TIM6/TIM7 register map | X | X | X |
| APB1 | 0x4000 0C00 - 0x4000 0FFF | TIM5 | TIM5 register map | - | X | X |
| APB1 | 0x4000 0800 - 0x4000 0BFF | TIM4 | TIM4 register map | - | - | X |
| APB1 | 0x4000 0400 - 0x4000 07FF | TIM3 | TIM3 register map | - | - | X |
| APB1 | 0x4000 0000 - 0x4000 03FF | TIM2 | TIM2 register map | X | X | X |

Notes:

1. For STM32C55x/562 devices, FDCAN RAM boundary end address is 0x4000 AFFF.
2. The COMP2 peripheral is only available in STM32C53x/542.

*Digest note:* Source quirks reproduced as printed: the LPDMA2 lower boundary is printed "0X4002 1000" (capital X, normalized here); the AHB2 reserved row "0x4202 8800 - 0x420B D7FF" overlaps the ADC3/ADCC3 rows that follow it and is most likely intended to read 0x4202 8800 - 0x4202 D7FF [unclear in source: upper bound of this reserved range]. In the source, "LPDMA register map", "USB register map", "I2C register map", "USART register map" (UART5/UART4/USART3/USART2), "SPI register map" (SPI3/SPI2) and "TIM6/TIM7 register map" are merged cells spanning the listed rows.

*Digest note:* STM32C551/C552 applicability beyond the C55x/562 column (from the C55xxx datasheet digest and ST CMSIS headers stm32c551xx.h / stm32c552xx.h):

- AES (0x420C 0000) is marked present for C55x/562 but neither the C55xxx datasheet nor the C551/C552 CMSIS headers list it; on STM32C551/C552 only HASH and RNG are present in the crypto block. AES appears to be STM32C562-only.
- FDCAN1 (0x4000 A400) and the FDCAN SRAM (0x4000 AC00 - 0x4000 AFFF) are present only on STM32C552 (absent on STM32C551). FDCAN2 is absent on all C55x/562.
- COMP12 at 0x4000 4000 provides COMP1 only on C55x (COMP2 is C53x/542-only, note 2); the CMSIS header names it COMP1_BASE.
- SAES, PKA, CCB, ADC3/ADCC3, GPIOF, GPIOG, ETHERNET MAC, XSPI1, DLYBXS1, USART6, UART7, TIM3, TIM4 and OPAMP1 are absent on STM32C551/C552.
- The C552 CMSIS header base addresses agree with this table: APB1PERIPH_BASE 0x4000 0000, APB2PERIPH_BASE 0x4001 0000, AHB1PERIPH_BASE 0x4002 0000, AHB2PERIPH_BASE 0x4202 0000, APB3PERIPH_BASE 0x4400 0000, AHB3PERIPH_BASE 0x4402 0000; DBGMCU_BASE (= "DEBUG") 0x4402 4000; ICACHE_BASE 0x4003 0400; RAMCFG_BASE 0x4002 6000; FLASH_R_BASE 0x4002 2000; USB_DRD_FS_BASE 0x4001 6000 and USB_DRD_PMAADDR 0x4001 6400; SRAMCAN_BASE 0x4000 AC00 (C552 header only). The header also defines FDCAN_CONFIG_BASE at 0x4000 A500, inside the FDCAN1 range.

### 2.2.3 Embedded SRAM

**Table 4. SRAM sizes**

| SRAM | STM32C53x/542 | STM32C55x/562 | STM32C59x/5A3 |
|---|---|---|---|
| SRAM1 | 32 Kbytes | 64 Kbytes | 128 Kbytes |
| SRAM2 | 32 Kbytes with ECC | 64 Kbytes with ECC | 128 Kbytes with ECC |

These SRAMs can be accessed as bytes, half-words (16 bits), or full words (32 bits). These memories can be addressed both by CPU and DMAs.

The CPU can access the SRAM1 and SRAM2 through the system bus or through the C-bus depending on the selected address. SRAM features are detailed in Section 5.3.1: Internal SRAMs features.

### 2.2.4 Flash memory overview

The flash memory is composed of two distinct physical areas:

- The main flash memory block that contains the application program and user data.
- The information block that is composed of the following parts:
  - option bytes for hardware and memory protection user configuration
  - system memory that contains ST proprietary code
  - OTP (one-time programmable) area

The flash memory interface implements instruction access and data access based on the AHB protocol. It also implements the logic necessary to carry out the flash memory operations (program/erase) controlled through the flash memory registers plus security access control features. Refer to Section 6: Embedded flash memory (FLASH) for more details.
