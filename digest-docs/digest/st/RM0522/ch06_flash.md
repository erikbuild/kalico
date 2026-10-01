# RM0522 Chapter 6: Embedded flash memory (FLASH)

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 126–206.

*Digest note:* This chapter covers the whole STM32C5 series. For STM32C551/C552 (STM32C55xxx, 256 KB or 512 KB flash; see /Users/erik/Code/kalico/digest-docs/digest/st/STM32C55xxx_Datasheet.md) the applicable memory map is Table 25 (STM32C55x/562 devices): two banks of 32 pages of 8 Kbytes each (2 x 256 Kbytes) for the 512 KB part. The FLASH register block is at 0x4002 2000 (CMSIS header stm32c552xx.h: `FLASH_R_BASE = AHB1PERIPH_BASE + 0x02000`, `AHB1PERIPH_BASE = 0x4002 0000`) and the FLASH global interrupt is IRQ 5 (`FLASH_IRQn = 5`); neither value is stated in this chapter.

## 6.1 FLASH introduction

The embedded flash memory (FLASH) manages the accesses of any master to the up to 1 Mbyte of embedded nonvolatile memory. It implements the read, program and erase operations, error corrections, as well as various integrity and confidentiality protection mechanisms.

The FLASH manages the automatic loading of nonvolatile user option bytes at power-on reset, and implements the dynamic update of these options.

The FLASH also features a one-time-programmable (OTP) area and a read-only area provisioned by STMicroelectronics during the product manufacturing.

## 6.2 FLASH main features

- Up to 1 Mbyte of nonvolatile memory divided into two banks
- Flash memory read operations supporting multiple lengths: 128, 64, 32, 16 bits, or 1 byte
- Flash memory programming by 128 bits in user area and 32 or 16 bits for OTP and flash data area
- 8-Kbyte page erase, bank erase and dual-bank mass erase
- 16 EDATA pages per bank that can be configured
  - to extend user area, 2-Kbyte pages, 128-bit programming
  - to offer user data flash memory, 1.5-Kbyte pages, 16- or 32-bit programming
- Dual-bank organization supporting:
  - Simultaneous operations: read-while-write (program and erase) is supported.
  - The two banks share the same interface. Write and erase can not be performed in parallel (write-while-write is not supported).
  - Bank swapping: the address mapping of the user flash memory of each bank can be swapped, along with the corresponding registers. Security flags remain valid for the physical bank. So the data are not reveled by swapping to a bank with lower security configuration.
- Error code correction (ECC): one error detection/correction or two error detections per 128-bit FLASH word using 9 ECC bits
- User configurable nonvolatile option bytes
- Flash memory enhanced protections, activated by option bytes
  - Read out protection for protecting memory content from debug access
  - Page group write-protection (WRPG)
  - HDP protection providing temporal isolation for startup code
- 4.5-Kbyte one-time programmable (OTP) area
- Read-only area provisioned by STMicroelectronics
- Prefetch is reading the next sequential instruction from flash memory

*Digest note:* "Up to 1 Mbyte" applies to STM32C59x/5A3 (2 x 512 Kbytes, Table 26). STM32C551/C552 have at most 512 Kbytes (2 x 256 Kbytes, Table 25).

## 6.3 FLASH functional description

### 6.3.1 FLASH block diagram

The following figure shows the simplified FLASH block diagram.

**Figure 9. FLASH block diagram (simplified)**

The FLASH block contains: an AHB interface (configuration port) attached to the 32-bit AHB bus; register banks (including the OB words); IRQ logic driving the flash_it interrupt output; a second AHB interface attached to the 128-bit AHB bus and labelled "User, system flash access, and read-only, OTP area, data flash area, engi, user option"; and the flash interface logic. The configuration-port AHB interface feeds the register banks; the register banks exchange data with the flash interface logic; the flash interface logic feeds the IRQ logic. The 128-bit AHB interface exchanges data with the flash interface logic in both directions. The flash interface logic connects to two nonvolatile memories, "Nonvolatile memory bank1" and "Nonvolatile memory bank2", each with a 128-bit read path, a shared 128-bit write path that fans out to both banks, and "ECC, redundancy" and "Control, status" connections.

External blocks connected to the FLASH: RCC (signals flash_rst and po_rst into the FLASH), TAMP (signal tamper_in), and SBS (connections labelled addresses, RDP level, and HDP). SBS drives dbg_en to the DEBUG block.

### 6.3.2 FLASH signals

The flash memory has two AHB connections: the flash AHB register interface and the main AHB interface.

**FLASH AHB register interface**

- Data size is 32 bits.
- Except for some registers (FLASH_KEYR and FLASH_OPTKEYR that are used to insert unlock sequences for control and option registers and can be written in 32 bits), it is possible to read and write all registers in 8, 16, and 32 bits.
- When an unlock sequence for control and option registers is incorrect, a bus error is raised. Otherwise, no read or write errors are generated on the bus.

**Main AHB interface**

The AHB data bus size is 128 bits. This interface is used to handle two different targets:

- Code placed in user and system memory. 128-bit data are protected by 9 bits of ECC.
- OTP, user data flash, and read only memory. 16-bit data are protected by 6 bits of ECC.

The main AHB interface is implemented as follows:

- User and system memory:
  - Supports multiple length: 128-, 64-, 32-, 16-, and 8-bit data width.
  - There is a read buffer of 128 bits for each bank where the last data read is stored. If the data is available in the read buffer, no read access is done to the flash memory. Buffer is flushed when write access, OTP access, flash data area access user option change request or erase operation occurs
  - There is a prefetch of the same size as the read buffer.
  - A 9-bit ECC is associated to each 128-bit data flash memory word
- OTP, user data flash and read only
  - Two dedicated data buffer of 137 bits are used to manage 16-bit data with 6-bit ECC.
  - Reading two times the same address triggers two FLASH read accesses.
  - During a read access, two wait states are added in addition of the memory wait states. These wait states are necessary to parse the data buffer
  - Each write access triggers a write in the flash memory.
  - 6-bit ECC is associated to each 16-bit data.

**Caution:** By default, all the AHB memory range is cacheable. For regions where caching is not permitted (OTP, RO, data area), MPU has to be used to disable local cacheability. An attempt to cache these regions will generate a Hard Fault.

### 6.3.3 Flash memory architecture and usage

**Flash memory architecture**

Figure 10 shows the nonvolatile memory organization supported by the FLASH.

**Figure 10. Embedded flash memory organization**

The figure shows two banks, Bank1 and Bank2, both reached by the flash interface logic from the main AHB system bus. Each bank contains:

- User main memory (per bank): up to 64 pages of 8 Kbytes each (Page 0, Page 1, Page 2, ... up to page 63); 9-bit ECC per 128-bit FLASH word.
- System memory (per bank): 3 pages of 8 Kbytes each (Sys page 0, Sys page 1, Sys page 2); 9-bit ECC per 128-bit FLASH word. The system pages are marked "Write locked".
- Flash data area (per bank): 16 EDATA pages of 1.5 or 2 Kbytes each (EDATA page 0 ... EDATA page 15); 6-bit ECC per 16-bit, or 9-bit ECC per 128-bit.

Bank1 additionally contains a special region (Bank 1 only) made of the Read-only area and the OTP area: 6-bit ECC per 16-bit; OTP writable only once; Read-only writable only by STMicroelectronics. The option bytes are also located with Bank1 and are reached through the AHB config port rather than the main AHB system bus. A "Write-protected" legend highlights example write-protected pages (page 2 in Bank2, a range of pages in Bank1).

The embedded flash nonvolatile memory is composed of:

- A main memory block is organized into two banks. Each bank is divided in pages of 8 Kbytes each and features flash-word rows of 128 bits + 9 bits of ECC per word.
- A system memory block of 48 Kbytes is divided into two 24-Kbyte banks. Each bank is divided in three 8-Kbyte pages. The system flash memory is ECC protected (9-bit ECC per 128-bit word).
- A set of nonvolatile option bytes loaded at reset by the FLASH, and accessible by the application software only through the AHB configuration register interface.
- A 4.5-Kbyte OTP area that can be written only once by the application software
- A 1.5-Kbyte read-only area . It contains a unique device ID and product information.
- Up to 32 pages of user flash memory for data, 16 pages of 2 Kbytes per bank if EDATA_EN bit is reset, or 16 pages of 1.5 Kbytes per bank if EDATA_EN bit is set.

The overall flash memory architecture and its corresponding access interface is summarized in Table 24.

*Digest note:* For STM32C55x (512 KB) each bank has 32 user pages (Page 0 to Page 31) of 8 Kbytes; see Table 25. The RM gives no explicit table for the 256 KB STM32C55x parts; see the digest note under Table 25.

**Partition usage**

The figure below shows how the FLASH is used by both STMicroelectronics and the application software.

**Figure 11. FLASH use**

The figure stacks the STM32C5 nonvolatile memory regions from top to bottom and shows, for SWAP_BANK = 0 and SWAP_BANK = 1, which physical bank appears at each address range:

- User memory (Application software), entered at the "User boot address": with SWAP_BANK = 0 the lower half is Bank1 and the upper half Bank2; with SWAP_BANK = 1 the lower half is Bank2 and the upper half Bank1.
- Flash data area (Application data): with SWAP_BANK = 0, Bank1 then Bank2; with SWAP_BANK = 1, Bank2 then Bank1.
- System memory: Bootloader in Bank1, then Bootloader in Bank2 (not affected by SWAP_BANK).
- Reserved (Bank1).
- Reserved and Read-only and OTP area (Bank2 label in the figure), annotated "Mapped on AHB config port".
- User option bytes (Bank1), annotated "Managed through registers only".
- Reserved (Bank2).

*Digest note:* Figure 11 labels the read-only/OTP area as Bank2 and "Mapped on AHB config port", while Figure 10 places the read-only/OTP special region in Bank1 and Section 6.3.9 states that OTP and RO are accessed through the main AHB interface. [unclear in source: bank attribution and access port of the RO/OTP area differ between Figure 10, Figure 11 and Section 6.3.9]

User and system memories are used differently according to RDP level and other option-byte settings.

The user memory contains the application code and associated constant data. The flash data area contains application nonvolatile data.The system memory contains the STM32 bootloader. When a reset occurs, the core jumps to the boot address configured through the BOOT pin (or BOOT option bit), the BOOTADD option bytes, and the RDP level.

Note: For more information on option-byte setup for boot, refer to Section 6.4.8.

### 6.3.4 FLASH read operations

**Read operation overview**

Read access to main flash memory and system flash memory operates as follows:

- There is a 128-bit read data buffer associated to each bank, which stores the last data read. If several consecutive read accesses request data belonging to the same FLASH data word (128 bits), the data are read directly from the current data read buffer, without triggering additional FLASH read operations. This mechanism occurs each time a read access is granted. When a read access is rejected for security reasons, the corresponding read error response is issued by the FLASH and no read operation to flash memory is triggered
- The read data buffer is disabled when write access or OTP access, user option change request or other erase operation occurs

Read access to OTP, RO, and user data flash area operates as follows:

1. A FLASH data word of 137 bits is read and stored in a temporary buffer.
2. The interface parses the 137-bit data word, and selects the 16- or 32-bit data requested.
3. While parsing the 137-bit data word, two wait states are added and the AHB bus is stalled.
4. If the application reads an OTP data or user data FLASH not previously written, a double ECC error is reported, and only word full of set bits is returned (see Section 6.3.9 for details). The read data (in 16 bits) is stored in FLASH_ECCDR, so that the user can identify if the double ECC error is due to a virgin data or a real ECC error.
5. Reading two times the same address triggers two reads in the flash memory.
6. For 8-bit accesses, an AHB bus error is generated.

Note: The FLASH can perform single-error correction and double-error detection while read operations are being executed (see Section 6.3.8).

**Instruction prefetch**

The Cortex-M33 fetches instructions and literal pools (constants/data) over the C-Bus and through the instruction cache if it is enabled. The prefetch block aims at increasing the efficiency of C-Bus accesses when the ICACHE is enabled, by reducing the cache refill latency.

Prefetch is efficient in case of sequential code; prefetch in the flash memory allows the next sequential instruction line to be read from the flash memory, while the current instruction line is being filled in the ICACHE and executed by the CPU.

Prefetch is enabled by setting the PRFTEN bit in FLASH_ACR. PRFTEN must be set only if at least one wait state is needed to access the flash memory.

**Adjusting read-timing constraints**

The FLASH clock must be enabled and running before reading data from a nonvolatile memory.

To correctly read data from the flash memory, the number of wait states (LATENCY) must be correctly programmed in FLASH_ACR, according to the FLASH main AHB interface clock frequency.

The table below shows the correspondence between the number of wait states (LATENCY), the programming delay parameter (WRHIGHFREQ) and the FLASH clock frequency.

**Table 20. FLASH recommended number of wait states and programming delay**

| Number of wait states (LATENCY) | Programming delay (WRHIGHFREQ) | Interface clock frequency |
| --- | --- | --- |
| 0 WS (1 FLASH clock cycle) | 00 | [0 MHz; 34 MHz] |
| 1 WS (2 FLASH clock cycles) | 00 | [34 MHz; 68 MHz] |
| 2 WS (3 FLASH clock cycles) | 01 | [68 MHz; 102 MHz] |
| 3 WS (4 FLASH clock cycles) | 01 | [102 MHz; 136 MHz] |
| 4 WS (5 FLASH clock cycles) | 10 | [136 MHz; 144 MHz] |

*Digest note:* At the STM32C55xxx maximum HCLK of 144 MHz: LATENCY = 4 (0100), WRHIGHFREQ = 10. The table gives no supply-voltage dependence, although the FLASH_ACR.LATENCY description mentions "frequency and voltage conditions". [unclear in source: the intervals share their end points (34, 68, 102, 136 MHz), so the setting exactly at a boundary frequency is not defined; use the higher wait-state count to be safe.]

**Adjusting system frequency**

After power-on, the FLASH is clocked by the divided by 3 high speed internal oscillator HSIDIV3 at 48 MHz. As a result, a conservative 7 wait-state latency is specified in FLASH_ACR register (see the previous table).

*Digest note:* The FLASH_ACR reset value 0x000X 0027 decodes as LATENCY = 0111 (7 WS) and WRHIGHFREQ = 10. Table 20 itself stops at 4 WS. The CMSIS header defines `FLASH_LATENCY_DEFAULT` as `FLASH_ACR_LATENCY_3WS` (a HAL constant, not the register reset value).

When changing the bus frequency, the application software must follow the sequence described below, in order to tune the number of wait states required to access the nonvolatile memory.

To increase the CPU frequency:

1. If necessary, program LATENCY and WRHIGHFREQ bits to the right value in the FLASH_ACR register, as described in Table 20.
2. Check that the new number of wait states is taken into account by reading back the FLASH_ACR register.
3. Modify the FLASH clock source and/or the clock prescaler in the RCC_CFGR register of the reset and clock controller (RCC).
4. Check that the new FLASH clock source and/or the new AHB clock prescaler value are taken in account by reading back the FLASH clock source status and/or the prescaler value in the RCC_CFGR register of the reset and clock controller (RCC).

To decrease the CPU frequency:

1. Modify the FLASH clock source and/or the clock prescaler in the RCC_CFGR register of reset and clock controller (RCC).
2. Check that the FLASH new clock source and/or the new clock prescaler value are taken in account by reading back the FLASH clock source status and/or the AHB interface prescaler value in the RCC_CFGR register of reset and clock controller (RCC).
3. If necessary, program the LATENCY and WRHIGHFREQ bits to the right value in FLASH_ACR register, as described in Table 20.
4. Check that the new number of wait states has been taken into account by reading back the FLASH_ACR register.

**Error code correction (ECC)**

The embedded flash memory embeds an error correction mechanism. Single-error correction and double-error detection are performed for each read operation. For more details, refer to Section 6.3.8.

**Read errors**

When the ECC mechanism is not able to correct the read operation, the embedded flash memory reports read errors as described in Section 6.8.5

**Read interrupts**

See Section 6.9 for details.

### 6.3.5 FLASH program operations

**Program operation overview**

Program operation consists in issuing write commands. The FLASH supports the execution of only one write-command at a time. Write-while-write are not supported. Nothing prevents overwriting a nonvirgin FLASH word but this is not recommended. The result may lead to invalid data and inconsistent ECC code.

**User flash memory**

For the user flash memory, 9-bit ECC is associated to each 128-bit data FLASH word. In this case, the FLASH must always perform write operations to nonvolatile memory with a 128-bit word granularity. Once the write buffer is full (128 bits), the busy flag BSY is set and a programming operation is triggered.

There is a write buffer common to bank1 and 2, which support multiple write-access types (128, 64, 32, 16, or 8 bits). The application can decide to write as little as 8- to a 128-bit FLASH word. In this case, a force-write mechanism to the 128 bits + ECC is used (see FW bit in FLASH_CR register).

When the write request is issued to the memory any new write request stalls the main AHB bus.

Moreover, while a write operation is ongoing, any new read request to the same bank stalls the main AHB bus.

**OTP, RO and flash data area**

When the target memory is OTP, RO, and flash data area pages, 6-bit ECC code is associated to each 16-bit data FLASH word. The FLASH supports 16- or 32-bit write operations (8-bit write operations are not supported). For 8-bit accesses, write accesses are ignored. There is no write data buffer. Each write access triggers a write in the flash memory.

Note: The OTP area is typically write-protected on the final product, as described in Section 6.3.9.

The write protection check is performed at the reception of the write request (during address phase). Write protection is not checked anymore at the output of the write buffer. If a write protection violation is detected, the write operation is canceled and write protection error (WRPERR) is raised in FLASH_SR register.

Note: For write protections of main FLASH, flash data area, and OTP, see Section 6.5.

**Monitoring ongoing write operations**

The application software can use a status flag located in FLASH_SR to monitor ongoing write operations. Since only one operation is possible at a time, this flag indicates if any operation (write, erase, option change) is ongoing, whatever the banks.

- BSY: This bit indicates that an effective write, erase, option-byte change is ongoing in the nonvolatile memory. This flag is not dedicated to a specific bank. It is set when an operation is starting on the memory, whatever the bank. An operation is triggered by:
  - An erase (FLASH_CR.STRT)
  - A write (FLASH_CR.PG + AHB write)
  - An option modification (FLASH_OPTCR.OPTSTRT)

  It is cleared when the current operation is ending or in case of error.

Note: BSY is also set when an OBL launch is triggered (OBL_LAUNCH in FLASH_OPTCR).

*Digest note:* FLASH_OPTCR as documented in Section 6.10.5 has no OBL_LAUNCH bit (only SWAP_BANK, OPTSTRT, OPTLOCK), and the CMSIS header stm32c552xx.h defines no OBL_LAUNCH bit either. Option bytes are reloaded automatically after a successful OPTSTRT sequence (Section 6.4.2, item 3). [unclear in source: whether any software-triggered OBL launch exists on STM32C5]

- WBNE: This bit indicates that the FLASH is waiting for new data to complete the 128-bit write buffer. In this state, the write buffer is not empty. It is reset as soon as the application software fills the write buffer, or forces the writes by using FW bit in FLASH_CR, or an error is detected. When WBNE is high, it is not possible to launch an erase or an option modification on flash memory.
- DBNE: This bit indicates that the data buffer for parsing 16-bits data is not empty:
  - 16-bit data write access is received and that the data buffer is being filled. It is set at the receipt of the a valid write access and it is reset as soon as the write request preparation has been processed.

Note: If the flash memory is busy at the receipt of the AHB write request, the CPU execution is stalled.

**Enabling write operations**

Before programming the user flash memory in bank1 or bank2, the application software must make sure that the PG bit is set to 1 in FLASH_CR. If it is not the case, an unlock sequence must be used (see Section 6.5.4), and the PG bit must be set.

When the option bytes must be modified, the application software must make sure that FLASH_OPTCR is unlocked. If this is not the case, an unlock sequence must be used (see Section 6.5.4).

Note: The application software must not unlock an already unlocked register, otherwise this register remains locked until the next system reset.

If needed, the application software can update the programming delay, as described in Adjusting programming timing constraints.

**Writing to FLASH_CR and FLASH_OPTCR**

The FLASH_CR and FLASH_OPTCR registers are not accessible in write mode when the BSY bit is set. Any attempt to write these registers while the BSY bit is set causes the AHB bus to stall until BSY bit is cleared.

**Single-write sequence**

The recommended single-write sequence is the following:

1. Make sure protection mechanism does not prevent to attempt programming.
2. Check that no flash memory operation is ongoing by checking the BSY bit in FLASH_SR and DBNE bit in FLASH_SR. Check that the write buffer is empty by checking the WBNE bit in FLASH_SR.
3. Check and clear all the error flags due to previous programming/erase operation.
4. Unlock the FLASH_CR register, as described in Section 6.5.4 (only if register is not already unlocked).
5. Enable write operations by setting PG bit in FLASH_CR.
6. Write one FLASH word at aligned address.

   Note: WBNE flag indicates if the 128-bit write buffer is waiting for new data. No erase request or options change request is allowed between the first write to the write buffer and the completion of the FLASH write operation.
7. Wait for the BSY bit to be cleared in the corresponding FLASH_SR register.
8. Clear PG bit in FLASH_CR if there are not any more programming requests.

If step 6 is executed incrementally (for example byte per byte), the write buffer can become partially filled. In this case, the application software can decide to force-write what is stored in the write buffer by using FW bit in FLASH_CR. In this particular case, the unwritten bits are automatically set to 1. If no bit in the write buffer is cleared to 0, the FW bit has no effect.

Note: Using a force-write operation prevents the application from updating later the missing bits with a value different from 1, which is likely to lead to a unexpected or inconsistent data or ECC.

*Digest note:* A "FLASH word" in user flash is 128 bits (16 bytes, quad-word); step 6 therefore means writing 16 bytes to a 16-byte-aligned address (for example four consecutive 32-bit stores). Writing to a different address before the buffer is full raises INCERR (Section 6.8.4); writing the same byte twice raises STRBERR (Section 6.8.3).

**Adjusting programming timing constraints**

Program operation timing constraints depend of the FLASH clock frequency, which directly impacts the performance. If timing constraints are too tight, the nonvolatile memory does not operate correctly. If they are too lax, the programming speed is not optimal.

The user must therefore trim the optimal programming delay through the WRHIGHFREQ parameter in the FLASH_ACR register. Refer to Table 20 in Section 6.3.4 for the recommended programming delay depending on the FLASH clock frequency.

FLASH_ACR configuration register is common to both banks.

The application software must check that no program/erase operation is ongoing before modifying WRHIGHFREQ parameter.

**Caution:** Modifying WRHIGHFREQ while programming/erasing the flash memory may corrupt the flash memory content.

**Programming errors**

When a program operation fails, an error can be reported as described in Section 6.8.

**Programming interrupts**

See Section 6.9 for details.

### 6.3.6 FLASH erase operations

**Erase operation overview**

The FLASH can perform erase operations on 8-Kbyte or 2-Kbyte user pages, on one user flash memory bank, or on two user flash memory banks (for example mass erase).

For more details in user flash memory, user data flash, user options, and OTP erase protection, see Section 6.5.

Erase commands are issued through the AHB configuration interface. Since the FLASH supports one operation at a time, if it receives simultaneously a write and an erase request, an error flag is raised and both operation are canceled (see Section 6.8 for details).

After successful completion of erase, all the bytes in the erased flash sectors are set to the flash default 0xFF value.

**Erase and WRP**

If the application software attempts to erase a user page that is write protected, the page erase operation is aborted, and the WRPERR flag is raised in FLASH_SR, as described in Section 6.8.1.

**FLASH busy**

Busy signals are described in Monitoring ongoing write operations.

**Writing to FLASH_CR and FLASH_OPTCR**

Refer to Writing to FLASH_CR and FLASH_OPTCR.

**Enabling erase operations**

Before erasing a page, the application software must make sure that FLASH_CR is unlocked. If this is not the case, an unlock sequence must be used (see Section 6.5.4).

Note: The application software must not unlock a register that is already unlocked, otherwise this register remains locked until next system reset. This can be used to deliberately lock-out a register from further accesses.

Similar constraints apply to bank erase requests.

**FLASH page-erase sequence**

To erase an 8-Kbyte, a 2-Kbyte user page, or a 1.5K-byte if in data flash without security protections, proceed as follows:

1. Make sure protection mechanism does not prevent to attempt page erase (WRP, HDP).
2. Check that no flash memory operation is ongoing by checking the BSY and DBNE bits in FLASH_SR, and that the write buffer is empty by checking the WBNE bit in the same register.
3. Check and clear all the error flags due to previous programming/erase operation (refer to Section 6.8 for details).
4. Unlock the FLASH_CR register, as described in Section 6.5.4 (only if register is not already unlocked).
5. Set BKSEL bit, PER bit, EDATASEL bit, and PNB bitfield in FLASH_CR.
   - BKSEL indicates in which physical bank page has to be erased.
   - PER indicates a page erase operation.
   - EDATASEL indicates if the page targeted is a 2-Kbyte EDATA page or a standard page.
   - PNB contains the target page number.
6. Set the STRT bit in FLASH_CR.
7. Wait for the BSY bit to be cleared in FLASH_SR.
8. STRT bit is automatically cleared at the end of the page erase or in case of error.
9. Clear PER in FLASH_CR if there are not anymore page erase request to be issued.

Note: If another erase flag is requested simultaneously to the page erase, an PGSERR error is generated.

*Digest note:* PNB is the page index inside the physical bank selected by BKSEL (0 to 31 for STM32C55x 512 KB). BKSEL always selects the physical bank, so with SWAP_BANK = 1 the page mapped at 0x0800 0000 is physical bank2 (BKSEL = 1), PNB = 0.

**Standard flash memory bank-erase sequence**

To erase a bank , proceed as follows:

1. Make sure protection mechanism does not prevent to attempt bank erase.
2. Check that no flash memory operation is ongoing by checking the BSY and DBNE bits in FLASH_SR, and that the write buffer is empty by checking the WBNE bit in the same register.
3. Check and clear all the error flags due to previous programming/erase operation (refer to Section 6.8 for details).
4. Unlock the FLASH_CR register, as described in Section 6.5.4 (only if register is not already unlocked).
5. Set the BKSEL bit and the BER bit in FLASH_CR to the targeted physical bank (swap setting is ignored).
6. Set the STRT bit in FLASH_CR to start the bank erase operation. Then wait until the BSY bit is cleared in FLASH_SR.
7. STRT bit is automatically cleared at the end of erase sequence or in case of error.
8. Clear BER in FLASH_CR if there is not other bank erase request to be issued.

**FLASH mass-erase sequence**

The application software can set the MER bit to 1 in FLASH_CR, as described below:

1. Make sure protection mechanisms do not prevent to attempt mass erase (Section 6.5)
2. Check that no flash memory operation is ongoing by checking the BSY and DBNE bits in FLASH_SR, and that the write buffer is empty by checking the WBNE bit in the same register.
3. Check and clear all the error flags due to previous programming/erase operation (refer to Section 6.8 for details).
4. Unlock the FLASH_CR register as described in Section 6.5.4 (only if the registers are not already unlocked).
5. Set the MER bit to 1 in FLASH_CR.
6. Set the STRT bit in FLASH_CR. Then wait until BSY bit is cleared in FLASH_SR.
7. STRT bit is cleared automatically at the end of the erase sequence or in case of error.
8. Clear MER in FLASH_CR.

Note: Mass and bank erase also erase flash data area pages from the erased bank.

### 6.3.7 FLASH parallel operations

Since the nonvolatile memory is divided into two independent banks but encapsulated in the same macro, the embedded flash memory interface only supports reading in one bank while writing or erasing is executed in the other bank. This feature is called read-while-write capability (RWW). It does not support write-while-write or read-while-read. Same is valid for the flash data area.

In all cases, the sequences are described in Section 6.3.4, Section 6.3.5, and Section 6.3.6.

### 6.3.8 Flash memory error protections

**Error correction codes (ECC)**

The FLASH supports an error correction code (ECC) mechanism. It is based on the SECDED algorithm in order to correct single errors and detect double errors.

This mechanism uses 9 ECC bits per 128-bit FLASH word, and applies to user and system memory.

For read-only, OTP, and user flash data area, a stronger 6 ECC bits per 16-bit word is used.

A double ECC error is generated for an OTP or flash data area virgin word (for example a word with 22 bits at 1). When this OTP or flash data area word is no more virgin, the ECC error disappears.

More specifically, during each read operation from a 128-bit FLASH word, the FLASH retrieves the 9-bit ECC information, computes the ECC of the FLASH word, and compares the result with the reference value. If they do not match, the corresponding ECC error is raised as described in Section 6.8.5.

During each program operation, a 9-bit ECC code is associated to each 128-bit data FLASH word, and the resulting 137-bit FLASH word information is written in nonvolatile memory.

A similar mechanism applies to read-only, OTP, and user flash data area but with 6-bit ECC for 16-bit data.

### 6.3.9 OTP and RO memory access

OTP and RO memory are accessed through the main AHB interface. The OTP is accessible at the address 0x08FF E000 to 0x08FF F1FF, and the read only section is accessible from 0x08FF F800 to 0x08FF FDFF.

They are stored in a distinct way as data or user flash, filling first 4 bytes of a page, then 5th to 8th and finally 9th to 12th as columns. It does not impact addressing nor locking mechanism but requires caution to decode ECC double error or operation interruption. Indeed for OTP or RO the ECC address returned in ADDR_ECC bitfield indicate FLASH line.

In case of double error detection, the corrupted access can be identified thanks to DATA_ADDR_ECC bitfield returning OTP position on the line.

They are stored in a different way than user data, each sector being filled vertically 32-bit wise as described in the table below.

**Table 21. OTP first page organization**

| FLASH line | OTP position 0b000 | OTP position 0b001 | OTP position 0b010 | OTP position 0b011 | OTP position 0b100 | OTP position 0b101 |
| --- | --- | --- | --- | --- | --- | --- |
| 0x00 | OTP0, 0x08FF E000 | OTP1, 0x08FF E002 | OTP256, 0x08FF E200 | OTP257, 0x08FF E202 | OTP512, 0x08FF E400 | OTP513, 0x08FF E402 |
| 0x01 | OTP2, 0x08FF E004 | OTP3, 0x08FF E006 | OTP258, 0x08FF E204 | OTP259, 0x08FF E206 | OTP514, 0x08FF E404 | OTP515, 0x08FF E406 |
| ... | ... | ... | ... | ... | ... | ... |
| 0x7E | OTP252, 0x08FF E1F8 | OTP253, 0x08FF E1FA | OTP508, 0x08FF E3F8 | OTP509, 0x08FF E3FA | OTP764, 0x08FF E5F8 | OTP765, 0x08FF E5FA |
| 0x7F | OTP254, 0x08FF E1FC | OTP255, 0x08FF E1FE | OTP510, 0x08FF E3FC | OTP511, 0x08FF E3FE | OTP766, 0x08FF E5FC | OTP767, 0x08FF E5FE |

**FLASH one-time programmable area**

The FLASH offers a 4608-byte memory area dedicated to application nonconfidential, one-time programmable data (OTP). This area is composed of 2304 words of 16 bits (plus 6 bits of ECC). It cannot be erased, and can be written only once. The OTP area can be accessed through the main AHB interface from address 0x08FF E000 to 0x08FF F1FE (last whole readable 16-bit word).

OTP data can be programmed by the application software by chunks of 16 bits. Overwriting an already programmed 16-bit half-word can lead to data and ECC errors and is therefore not supported.

Note: The OTP area is virgin when the device is delivered by STMicroelectronics.

When reading OTP data with a single error corrected or a double error detected, the FLASH reports read errors, as described in Section 6.8.5.

When reading OTP data not written by the application software (such as virgin OTP), the ECC correction reports a double-error detection (ECCD), and the data are to be found in FLASH_ECCDR register. ECCD implies a NMI raised, unless setting in SBS prevents that.

**OTP write protection**

OTP data are organized as 24 blocks of 96 OTP words, as shown in Table 22. An entire OTP block can be protected (locked) from write accesses by setting the LOCKBLi (i = 0 to 23) bit corresponding to each OTP block (i = 0 to 23) in FLASH_OTPBLR. A block can be write-protected whether or not it has been programmed (even partially).

The OTP block locking operation is irreversible and independent from the product life state.

Note: The OTP area can only be accessed in read mode.

**Table 22. Flash memory OTP organization**

| OTP block | AHB address | AHB word [31:16] | AHB word [15:0] | Lock bit |
| --- | --- | --- | --- | --- |
| Block 0 | 0x08FF E000 | OTP0001 | OTP0000 | LOCKBL0 |
| Block 0 | 0x08FF E004 | OTP0003 | OTP0002 | LOCKBL0 |
| Block 0 | ... | ... | ... | LOCKBL0 |
| Block 0 | 0x08FF E0BC | OTP0095 | OTP0094 | LOCKBL0 |
| Block 1 | 0x08FF E0C0 | OTP0097 | OTP0096 | LOCKBL1 |
| Block 1 | 0x08FF E0C4 | OTP0099 | OTP0098 | LOCKBL1 |
| Block 1 | ... | ... | ... | LOCKBL1 |
| Block 1 | 0x08FF E17C | OTP0191 | OTP0190 | LOCKBL1 |
| Block 2 | 0x08FF E180 | OTP0193 | OTP0192 | LOCKBL2 |
| Block 2 | 0x08FF E184 | OTP0195 | OTP0194 | LOCKBL2 |
| Block 2 | ... | ... | ... | LOCKBL2 |
| Block 2 | 0x08FF E23C | OTP0287 | OTP0286 | LOCKBL2 |
| ... | ... | ... | ... | ... |
| Block 23 | 0x08FF F140 | OTP2209 | OTP2208 | LOCKBL23 |
| Block 23 | 0x08FF F144 | OTP2211 | OTP2210 | LOCKBL23 |
| Block 23 | ... | ... | ... | LOCKBL23 |
| Block 23 | 0x08FF F1FC | OTP2303 | OTP2302 | LOCKBL23 |

**OTP write sequence**

Follow the sequence below to write an OTP word:

1. Check that no flash memory operation is ongoing by checking the BSY bit in FLASH_SR register, and that the data buffer is empty by checking the DBNE bit in the same register.
2. Check and clear all the error flags due to previous programming/erase operation.
3. Set PG bit in FLASH_CR.
4. Check the protection status of the target OTP word (see Table 22). The corresponding LOCKBLi bit must not be set to 1.
5. Write two OTP words (32 bits) corresponding to the 4-byte aligned address shown in Table 22. Alternatively, the application software can program separately the 16-bit MSB or 16-bit LSB. In this case the first 16-bit write operation starts immediately without waiting for the second one
6. Wait for the BSY bit to be cleared in FLASH_SR.
7. Clear PG bit in FLASH_CR if there is not any programming request anymore in the bank.
8. Optionally, lock the OTP block using LOCKBLi to prevent further data changes.

Note: Do not write twice an OTP 16-bit word, otherwise an ECC error can be generated. Writing OTP data at byte level is not supported and generates a bus error. To avoid data corruption, it is important to complete the OTP write process (for example by reading back the OTP value), before starting an option change.

**FLASH read-only area**

The FLASH offers a 1.5-Kbyte memory area to store read-only data, also referred to as RO. This area is mapped as described in Table 23. It can be accessed through the AHB main port. This read-only area is protected by a robust ECC scheme, as explained in Section 6.3.8.

The read-only information that can be used by the application software are described in the table below. This information is programmed by STMicroelectronics.

**Table 23. Read-only public data organization**

| Read-only data name | Address | Comment |
| --- | --- | --- |
| Unique device ID | 0x08FF F800 | U_ID[31:0] |
| Unique device ID | 0x08FF F804 | U_ID[63:32] |
| Unique device ID | 0x08FF F808 | U_ID[96:64] |
| Flash memory size/package | 0x08FF F80C | Flash memory size[15:0] \|\| Package code[15:0] |
| Factory calibration | 0x08FF F810 | Vrefint calibration value[31:0] |
| Factory calibration | 0x08FF F814 | TS_CAL1[31:0] |
| Factory calibration | 0x08FF F818 | TS_CAL2[31:0] |
| Reserved | 0x08FF F81C to 0x08FF FDFF | Reserved information |

*Digest note:* The CMSIS header defines `FLASHSIZE_BASE = 0x08FF F80C` and `PACKAGE_BASE = 0x08FF F80E`, i.e. flash size (in Kbytes, read as a 16-bit value) in the lower half-word and package code in the upper half-word. The table's "Flash memory size[15:0] || Package code[15:0]" ordering does not state which half-word is which. Because the RO area uses 6-bit ECC on 16-bit data, 8-bit reads of these addresses raise a bus error (Section 6.3.4, item 6), and the region must be marked non-cacheable in the MPU if the cache could fetch it (Caution in Section 6.3.2).

### 6.3.10 FLASH data area

The FLASH offers 64 Kbytes to store extra code, data or emulate EEPROM in 16 EDATA pages per bank. Based on value of EDATA_EN option bit this area is one of the following:

- Protected by a robust 6-bit ECC, which allows a write granularity of 16 or 32 bits at the expense of having page size shrunk to 1.5 Kbytes. This area is the FLASH data area and the memory can be accessed through the AHB system port from address 0x0900 0000 to 0x0900 BFFF.
- Page size of 2 Kbytes with write granularity of 128 bits protected by a robust 9-bit ECC. This area is part of user main flash memory and instructions can be fetched from addresses 0x0840 0000 to 0x0840 FFFF (see Figure 13).

**Caution:** This area cannot be used as a boot location in BOOTADD.

For greater efficiency, it is always recommended to use page on the other bank for the FLASH data area, so that the application benefits from RWW capability of the dual-bank arrangement.

When SWAP_BANK feature is enabled, the banks are swapped: the flash data area in bank 2 are accessible from 0x0900 000 to 0x0900 5FFF, and the data in bank 1 are accessible from 0x0900 6000 to 0x0900 BFFF.

*Digest note:* "see Figure 13" refers to the EDATA memory map, which is Figure 12; "0x0900 000" is printed with a missing digit and is 0x0900 0000 per Tables 24 to 26.

A bus error is generated on:

- Attempt to access one of the following address
  - Between 0x0900 0000 to 0x0900 BFFF, and this address is not a data FLASH valid page.
  - Between 0x0840 0000 to 0x0840 FFFF, and this address is not a user memory valid page.
- Attempt to fetch instructions from data FLASH area (fetch from 0x0900 0000 to 0x0900 BFFF result in HardFault).

Erasing these EDATA pages is possible by setting the EDATASEL bit and following a page erase request. The EDATA page erasure is not taking account EDATA_EN bit.

Protections and security of data FLASH area are detailed in Section 6.5.

*Digest note:* The factory default of EDATA_EN is 1 (Table 28), so on a delivered device the EDATA pages appear as the 48-Kbyte, 16/32-bit-writable data area at 0x0900 0000 to 0x0900 BFFF, and the 0x0840 0000 to 0x0840 FFFF window is not valid.

**Figure 12. FLASH data area memory map**

The figure shows Bank1 and Bank2 side by side.

- Code memory map (write 128 bits, 9-bit ECC): Bank1 pages 0 to 63, each page 8 Kbytes, from 0x0800 0000 to 0x0807 FFFF; Bank2 pages 0 to 63, each page 8 Kbytes, from 0x0808 0000 to 0x080F FFFF.
- With the EDATA_EN option bit reset (code memory map, write 128 bits, 9-bit ECC): Bank1 EDATA page 0 to EDATA page 15, each page 2 Kbytes, from 0x0840 0000 to 0x0840 7FFF; Bank2 EDATA page 0 to EDATA page 15, each page 2 Kbytes, from 0x0840 8000 to 0x0840 FFFF.
- With the EDATA_EN option bit set (data memory map, 6-bit ECC): Bank1 EDATA pages from 0x0900 0000 to 0x0900 5FFF and Bank2 EDATA pages from 0x0900 6000 to 0x0900 BFFF, each page 1.5 Kbytes.

*Digest note:* Figure 12 shows the STM32C59x/5A3 code addresses (64 pages per bank). For STM32C55x use Table 25.

### 6.3.11 FLASH bank swapping

The FLASH bank1 and bank2 can be swapped for the user FLASH. This feature can be used after a firmware upgrade to restart the device on the new firmware. Bank swapping is a user option-byte flag controlled by the SWAP_BANK bit in FLASH_OPTCR register.

Bank specific settings for data area and security attributes follow the original bank and its contents. The control bit BKSEL always refers to physical bank, not the SWAP_BANK setting.

Table 24 shows the memory map that can be accessed depending on the SWAP_BANK bit configuration.

**Table 24. Memory map and the swapping option (STM32C53x/542 devices)**

| Flash memory area | Bank when SWAP_BANK = 0 | Bank when SWAP_BANK = 1 | Start address | End address | Size (bytes) | Region name |
| --- | --- | --- | --- | --- | --- | --- |
| User main memory | Bank1 | Bank2 | 0x0800 0000 | 0x0800 1FFF | 8K | Page 0 |
| User main memory | Bank1 | Bank2 | 0x0800 2000 | 0x0800 3FFF | 8K | Page 1 |
| User main memory | Bank1 | Bank2 | ... | ... | ... | ... |
| User main memory | Bank1 | Bank2 | 0x0801 E000 | 0x0801 FFFF | 8K | Page 15 |
| User main memory | Bank2 | Bank1 | 0x0802 0000 | 0x0802 1FFF | 8K | Page 0 |
| User main memory | Bank2 | Bank1 | 0x0802 2000 | 0x0802 3FFF | 8K | Page 1 |
| User main memory | Bank2 | Bank1 | ... | ... | ... | ... |
| User main memory | Bank2 | Bank1 | 0x0803 E000 | 0x0803 FFFF | 8K | Page 15 |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | 0x0840 0000 | 0x0840 07FF | 2K | EDATA Page 0 |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | 0x0840 0800 | 0x0840 0FFF | 2K | EDATA Page 1 |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | ... | ... | ... | ... |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | 0x0840 7800 | 0x0840 7FFF | 2K | EDATA Page 15 |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | 0x0840 8000 | 0x0840 87FF | 2K | EDATA Page 0 |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | 0x0840 8800 | 0x0840 8FFF | 2K | EDATA Page 1 |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | ... | ... | ... | ... |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | 0x0840 F800 | 0x0840 FFFF | 2K | EDATA Page 15 |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | 0x0900 0000 | 0x0900 05FF | 1.5K | EDATA Page 0 |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | 0x0900 0600 | 0x0900 0BFF | 1.5K | EDATA Page 1 |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | ... | ... | ... | ... |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | 0x0900 5A00 | 0x0900 5FFF | 1.5K | EDATA Page 15 |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | 0x0900 6000 | 0x0900 65FF | 1.5K | EDATA Page 0 |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | 0x0900 6600 | 0x0900 6BFF | 1.5K | EDATA Page 1 |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | ... | ... | ... | ... |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | 0x0900 B800 | 0x0900 BFFF | 1.5K | EDATA Page 15 |
| System memory | Bank1 | Bank1 | 0x0BF8 0000 | 0x0BF8 1FFF | 8K | System 1 Page 0 |
| System memory | Bank1 | Bank1 | 0x0BF8 2000 | 0x0BF8 3FFF | 8K | System 1 Page 1 |
| System memory | Bank1 | Bank1 | 0x0BF8 4000 | 0x0BF8 5FFF | 8K | System 1 Page 2 |
| System memory | Bank2 | Bank2 | 0x0BF8 6000 | 0x0BF8 7FFF | 8K | System 2 Page 0 |
| System memory | Bank2 | Bank2 | 0x0BF8 8000 | 0x0BF8 9FFF | 8K | System 2 Page 1 |
| System memory | Bank2 | Bank2 | 0x0BF8 A000 | 0x0BF8 BFFF | 8K | System 2 Page 2 |

*Digest note:* Table 24 does not apply to STM32C551/C552.

**Table 25. Memory map and the swapping option (STM32C55x/562 devices)**

| Flash memory area | Bank when SWAP_BANK = 0 | Bank when SWAP_BANK = 1 | Start address | End address | Size (bytes) | Region name |
| --- | --- | --- | --- | --- | --- | --- |
| User main memory | Bank1 | Bank2 | 0x0800 0000 | 0x0800 1FFF | 8K | Page 0 |
| User main memory | Bank1 | Bank2 | 0x0800 2000 | 0x0800 3FFF | 8K | Page 1 |
| User main memory | Bank1 | Bank2 | ... | ... | ... | ... |
| User main memory | Bank1 | Bank2 | 0x0803 E000 | 0x0803 FFFF | 8K | Page 31 |
| User main memory | Bank2 | Bank1 | 0x0804 0000 | 0x0804 1FFF | 8K | Page 0 |
| User main memory | Bank2 | Bank1 | 0x0804 2000 | 0x0804 3FFF | 8K | Page 1 |
| User main memory | Bank2 | Bank1 | ... | ... | ... | ... |
| User main memory | Bank2 | Bank1 | 0x0807 E000 | 0x0807 FFFF | 8K | Page 31 |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | 0x0840 0000 | 0x0840 07FF | 2K | EDATA Page 0 |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | 0x0840 0800 | 0x0840 0FFF | 2K | EDATA Page 1 |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | ... | ... | ... | ... |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | 0x0840 7800 | 0x0840 7FFF | 2K | EDATA Page 15 |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | 0x0840 8000 | 0x0840 87FF | 2K | EDATA Page 0 |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | 0x0840 8800 | 0x0840 8FFF | 2K | EDATA Page 1 |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | ... | ... | ... | ... |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | 0x0840 F800 | 0x0840 FFFF | 2K | EDATA Page 15 |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | 0x0900 0000 | 0x0900 05FF | 1.5K | EDATA Page 0 |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | 0x0900 0600 | 0x0900 0BFF | 1.5K | EDATA Page 1 |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | ... | ... | ... | ... |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | 0x0900 5A00 | 0x0900 5FFF | 1.5K | EDATA Page 15 |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | 0x0900 6000 | 0x0900 65FF | 1.5K | EDATA Page 0 |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | 0x0900 6600 | 0x0900 6BFF | 1.5K | EDATA Page 1 |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | ... | ... | ... | ... |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | 0x0900 B800 | 0x0900 BFFF | 1.5K | EDATA Page 15 |
| System memory | Bank1 | Bank1 | 0x0BF8 0000 | 0x0BF8 1FFF | 8K | System 1 Page 0 |
| System memory | Bank1 | Bank1 | 0x0BF8 2000 | 0x0BF8 3FFF | 8K | System 1 Page 1 |
| System memory | Bank1 | Bank1 | 0x0BF8 4000 | 0x0BF8 5FFF | 8K | System 1 Page 2 |
| System memory | Bank2 | Bank2 | 0x0BF8 6000 | 0x0BF8 7FFF | 8K | System 2 Page 0 |
| System memory | Bank2 | Bank2 | 0x0BF8 8000 | 0x0BF8 9FFF | 8K | System 2 Page 1 |
| System memory | Bank2 | Bank2 | 0x0BF8 A000 | 0x0BF8 BFFF | 8K | System 2 Page 2 |

*Digest note:* Table 25 is the map for STM32C551/C552 with 512 Kbytes (part-number flash code E): 2 banks x 32 pages x 8 Kbytes, bank boundary at 0x0804 0000. For the 256-Kbyte parts (flash code C) the RM gives no table. The SINGLE_BANK option (Section 6.4.5) applies to "STM32C55x/562 with 256 Kbytes of flash" and the address range "is kept linear"; the CMSIS header computes `FLASH_BANK_SIZE = FLASH_SIZE >> 1` (128 Kbytes, 16 pages per bank, bank2 at 0x0802 0000 in dual-bank mode). [unclear in source: the 256-Kbyte STM32C55x bank boundary, page count per bank, and the page numbering seen by BKSEL/PNB in SINGLE_BANK mode are not stated in RM0522 Rev 1.] Read the flash size from 0x08FF F80C at run time.

**Table 26. Memory map and the swapping option (STM32C59x/5A3 devices)**

| Flash memory area | Bank when SWAP_BANK = 0 | Bank when SWAP_BANK = 1 | Start address | End address | Size (bytes) | Region name |
| --- | --- | --- | --- | --- | --- | --- |
| User main memory | Bank1 | Bank2 | 0x0800 0000 | 0x0800 1FFF | 8K | Page 0 |
| User main memory | Bank1 | Bank2 | 0x0800 2000 | 0x0800 3FFF | 8K | Page 1 |
| User main memory | Bank1 | Bank2 | ... | ... | ... | ... |
| User main memory | Bank1 | Bank2 | 0x0807 E000 | 0x0807 FFFF | 8K | Page 63 |
| User main memory | Bank2 | Bank1 | 0x0808 0000 | 0x0808 1FFF | 8K | Page 0 |
| User main memory | Bank2 | Bank1 | 0x0808 2000 | 0x0808 3FFF | 8K | Page 1 |
| User main memory | Bank2 | Bank1 | ... | ... | ... | ... |
| User main memory | Bank2 | Bank1 | 0x080F E000 | 0x080F FFFF | 8K | Page 63 |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | 0x0840 0000 | 0x0840 07FF | 2K | EDATA Page 0 |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | 0x0840 0800 | 0x0840 0FFF | 2K | EDATA Page 1 |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | ... | ... | ... | ... |
| User flash memory / EDATA_EN cleared | Bank1 | Bank2 | 0x0840 7800 | 0x0840 7FFF | 2K | EDATA Page 15 |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | 0x0840 8000 | 0x0840 87FF | 2K | EDATA Page 0 |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | 0x0840 8800 | 0x0840 8FFF | 2K | EDATA Page 1 |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | ... | ... | ... | ... |
| User flash memory / EDATA_EN cleared | Bank2 | Bank1 | 0x0840 F800 | 0x0840 FFFF | 2K | EDATA Page 15 |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | 0x0900 0000 | 0x0900 05FF | 1.5K | EDATA Page 0 |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | 0x0900 0600 | 0x0900 0BFF | 1.5K | EDATA Page 1 |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | ... | ... | ... | ... |
| Data flash memory / EDATA_EN set | Bank1 | Bank2 | 0x0900 5A00 | 0x0900 5FFF | 1.5K | EDATA Page 15 |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | 0x0900 6000 | 0x0900 65FF | 1.5K | EDATA Page 0 |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | 0x0900 6600 | 0x0900 6BFF | 1.5K | EDATA Page 1 |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | ... | ... | ... | ... |
| Data flash memory / EDATA_EN set | Bank2 | Bank1 | 0x0900 B800 | 0x0900 BFFF | 1.5K | EDATA Page 15 |
| System memory | Bank1 | Bank1 | 0x0BF8 0000 | 0x0BF8 1FFF | 8K | System 1 Page 0 |
| System memory | Bank1 | Bank1 | 0x0BF8 2000 | 0x0BF8 3FFF | 8K | System 1 Page 1 |
| System memory | Bank1 | Bank1 | 0x0BF8 4000 | 0x0BF8 5FFF | 8K | System 1 Page 2 |
| System memory | Bank2 | Bank2 | 0x0BF8 6000 | 0x0BF8 7FFF | 8K | System 2 Page 0 |
| System memory | Bank2 | Bank2 | 0x0BF8 8000 | 0x0BF8 9FFF | 8K | System 2 Page 1 |
| System memory | Bank2 | Bank2 | 0x0BF8 A000 | 0x0BF8 BFFF | 8K | System 2 Page 2 |

*Digest note:* Table 26 does not apply to STM32C551/C552. In Tables 24 to 26 the system memory rows have a single bank entry that spans both SWAP_BANK columns (system memory is not swapped); it is repeated in both columns here.

The SWAP_BANK bit in FLASH_OPTCR register is loaded from the SWAP_BANK option bit only after system reset or POR.

To change the SWAP_BANK bit (for example to apply a new firmware update), respect the sequence below:

1. Check that no flash memory operation is ongoing by checking the BSY and DBNE bits in FLASH_SR, and that the write buffer is empty by checking the WBNE bit in the same register.
2. Clear all error flags due to a previous operation.
3. Unlock OPTLOCK bit, if not already unlocked.
4. Set the new desired SWAP_BANK value in the FLASH_OPTSR_PRG register.
5. Start the option-byte change sequence by setting the OPTSTRT bit in FLASH_OPTCR.
6. Once the option-byte change has completed, FLASH_OPTSR_CUR contains the expected SWAP_BANK value, but SWAP_BANK bit in FLASH_OPTCR has not yet been modified, and the bank swapping is not yet effective
7. Force a system reset or a POR. When the reset rises up, the bank swapping is effective (SWAP_BANK value updated in FLASH_OPTCR) and the new firmware must be executed.

Note: The SWAP_BANK bit in FLASH_OPTCR is read-only and cannot be modified by the application software. The SWAP_BANK option bit in FLASH_OPTSR_PRG can be modified whatever the RDP level. Instead of being locked by RDP_LEVEL, it is locked by BOOT_LOCK User OB.

The figure below gives an overview of the bank swapping sequence.

**Figure 13. FLASH bank swapping sequence**

Flow chart (left side): Begin; "Update new firmware in user FLASH bank 1/2"; "Set/unset SWAP_BANK_OPT option-bit in FLASH_OPTSR_PRG"; "Write START bit in FLASH_OPTCR to start option-byte change sequence"; then a System reset (dashed line); "SWAP_BANK of FLASH_OPTSR_CUR is copied to SWAP_BANK_OPT bit in FLASH_OPTCR"; End; "Execution of new firmware".

Data path (right side): the SWAP_BANK_OPT bit in FLASH_OPTSR_PRG is written by software and goes to the nonvolatile memory by option-byte programming; an option-byte reload copies it from the nonvolatile memory into SWAP_BANK_OPT of FLASH_OPTSR_CUR; on system reset (option-byte reload) it is copied into SWAP_BANK of FLASH_OPTCR; FLASH_OPTCR.SWAP_BANK drives the "User flash memory SWAP logic" ("New swap policy effective"), which sits between the AHB bus and nonvolatile memory bank1 and bank2.

### 6.3.12 FLASH reset and clocks

**Reset management**

The FLASH can be reset by a core domain reset, driven by the reset and clock control (RCC). The main effects of this reset are the following:

- All registers, except for option-byte registers, are cleared, including read and write latencies. If the bank swapping option is changed, it is applied.
- Most control registers are automatically protected against write operations. To unprotect them, new unlock sequences must be used as described in Section 6.5.4.

The FLASH can be reset by a power-on core domain reset, driven by the RCC. When the reset falls, all option-byte registers are reset. When the reset rises up, the option bytes are loaded, potentially applying new features. During this loading sequence, the device remains under reset and the FLASH is not accessible.

**Reset occurring during FLASH operation**

If a reset occurs during a FLASH operation (programing, erase, or option change), the content of the flash memory is not guaranteed. It is mandatory for flash memory integrity than user restarts the operation. The status register FLASH_OPSR gives information if any FLASH operation has been interrupted by a reset.

FLASH_OPSR.CODE_OP gives opcode of operation. The table below indicates how to use FLASH_OPSR and which operation is required.

**Table 27. Recommended reactions to FLASH_OPSR contents**

| CODE_OP | Operation interrupted | OTP_OP | BK_OP | DATA_OP | Flash memory area | ADDR_OP min | ADDR_OP max | Recommended action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0b000 | No operation ongoing while reset | 0 | 0 | 0 | -(1) | - | - | No extra action |
| 0b001 | Write operation | 0 | 0/1 | 0 | User flash | 0x0000 | 0x7FFF(2) | Erase page and rewrite |
| 0b001 | Write operation | 1 | 1 | 0 | OTP(3) | 0x0200 | 0x037F | Erase page and rewrite |
| 0b001 | Write operation | 0 | 0/1 | 1 | EDATA Page(4) | 0x0000 | 0x07FF(2) | Erase page and rewrite |
| 0b011 | Page erase(5) | 0 | 0/1 | 0 | User flash | 0x0000 | 0x7FFF | Relaunch page erase |
| 0b011 | Page erase(5) | 0 | 0/1 | 1 | EDATA Page | 0x0000 | 0x07FF | Relaunch page erase |
| 0b100 | Bank erase | 0 | 0/1 | 0 | User flash | - | - | Relaunch bank erase |
| 0b101 | Mass erase | 0 | 0 | 0 | User flash | - | - | Relaunch mass erase |
| 0b110 | Option change | 0 | 0 | 0 | User configuration | - | - | New attempt on option change |

Notes:

1. '-' = does not matter.
2. ADDR_OP maximum depends on the flash memory size of the device.
3. OTP are organized per column, refer to Section 6.3.9.
4. Depends on EDATA setting in the OB.
5. Addresses indicated are aligned to page start, data area pages are erased by erase request to corresponding user flash memory page.

*Digest note:* ADDR_OP (like ADDR_ECC in Table 41) appears to count 128-bit FLASH lines within the bank: 0x7FFF + 1 = 32768 lines x 16 bytes = 512 Kbytes (the largest bank, STM32C59x), and 0x07FF + 1 = 2048 lines x 16 bytes = 32 Kbytes = 16 EDATA pages x 2 Kbytes. [unclear in source: the unit of ADDR_OP is not stated.] An OTP write cannot be repaired by "Erase page and rewrite", since OTP cannot be erased.

**Clock management**

The FLASH uses the microcontroller AHB interface clock HCLK.

## 6.4 FLASH option bytes

### 6.4.1 About option bytes

The FLASH includes a set of nonvolatile option bytes. They are loaded at power-on reset and can be read and modified only through configuration registers.

This section documents:

- When option bytes are loaded.
- How application software can modify them.
- The detailed list of option bytes, together with their initial values (before the first option byte change, user default configuration).

### 6.4.2 Option-byte loading

There are multiple ways of loading the option bytes into the FLASH:

1. Power-on wake-up

   When the device is first powered, the FLASH automatically loads all the option bytes. During the option-byte loading (OBL) sequence, the device remains under reset, and the FLASH cannot be accessed.
2. Wake-up from system Standby mode

   When the core power domain, which contains the FLASH, is switched from Standby mode to Run mode, the FLASH behaves as during a power-on sequence. During OBL time, the device is not under reset, unlike power-on sequence.
3. Dedicated option-byte reloading by the application

   When the user application successfully modifies the option-byte content through the FLASH registers, the nonvolatile option bytes are programmed, and the FLASH automatically reloads all option bytes to update the option registers.

Note: The option-byte read sequence is protected by error correction code. In case of error, the option bytes are loaded with default values (see Section 6.4.3). This value differs from the initial values (user default configuration), and tends to be more restrictive.

*Digest note:* The per-register "Default value (value in case of double ECC issue during OBL)" figures are given in Section 6.10 (for example FLASH_OPTSR_CUR = 0x20B0 72D8, which decodes as RDP_LEVEL = 0x72 = L2 and BOOT0 = 1; FLASH_BOOTR_CUR = 0xFFFF FFB4, which decodes as BOOT_LOCK = 0xB4 = locked).

### 6.4.3 Option-byte modification

**Changing user option bytes**

A user-option-byte change operation can be used to modify the configuration and the protection settings saved in the nonvolatile option byte area.

There are numerous rules enforced when attempting to change a user option byte, they are all summarized in Section 6.4.9. Failing to stick to these rules usually results in error, described in Section 6.8.6.

The FLASH features two sets of option-byte registers:

- The first register set contains the current values of the option bytes. Their names have the _CUR extension. All "_CUR" registers are read-only. Their values are automatically loaded from the nonvolatile memory after power-on reset, wake-up from system Standby mode, or after an option-byte change operation.
- The second register set allows the modification of the option bytes. Their names contain the _PRG extension. All "_PRG" registers can be accessed in read/write mode.

When the OPTLOCK bit in FLASH_OPTCR is set, modifying the FLASH_XXX_PRG registers is not possible.

When OPTSTRT bit is set to 1, the FLASH checks the programming sequence (PGSERR), and the conditions described in Section 6.4.9 (OPTCHANGEERR). If no error has been detected (PGSERR/OPTCHANGEERR), the FLASH launches the option-byte modification in its nonvolatile memory, and updates the option-byte registers with _CUR extension.

If one of the condition described in Section 6.4.9, Section 6.8.6, or Section 6.8.2 is not respected, the FLASH aborts the option-byte change operation. In this case, FLASH_XXX_PRG registers are not overwritten by current option value. The user application can check what was wrong in their configuration.

**Unlocking the option-byte modification**

After reset, the OPTLOCK bit is set to 1 and FLASH_OPTCR is locked. As a result, the application software must unlock the option configuration register before attempting to change the option bytes. FLASH_OPTCR unlock sequence is described in Section 6.5.4.

**Option-byte modification sequence**

To modify user option bytes, follow the sequence below:

1. Check that no flash memory operation is ongoing by checking the BSY bit in FLASH_SR, and that the write buffer is empty by checking the WBNE bit in the same register.
2. Check the data buffer is empty (DBNE = 0) in FLASH_SR.
3. Clear all error flags due to a previous operation.
4. Unlock FLASH_OPTCR register as described in Section 6.5.4, unless the register is already unlocked.
5. Write the desired new option byte values in the corresponding option registers (FLASH_XXX_PRG).
6. Set the option byte start change OPTSTRT bit to 1 in FLASH_OPTCR.
7. Wait until BSY bit is cleared in FLASH_SR.
8. OPTSTRT bit is cleared automatically at the end of the sequence (or in case of error).
9. Perform a system reset if the RDP level, SWAP_BANK, or BOOTADD options have been changed. A system reset is also recommended if other option bytes have been modified.

Note: If a reset or a power-down occurs while the option-byte modification is ongoing, the original option-byte value is kept. A new option-byte modification sequence is required to program the new value

*Digest note:* Section 6.5.4 lists only the FLASH_OPTKEYR key pair for FLASH_OPTCR; this chapter does not state that FLASH_CR must also be unlocked for an option change. The "_PRG" registers start out holding the current values (Section 6.10.12), so a read-modify-write of only the field to change keeps the other option bytes. Bootloader-relevant: BOOT0/BOOT_SEL (FLASH_OPTSR_PRG) and BOOTADD (FLASH_BOOTR_PRG) are changed this way, and BOOTADD/BOOT_LOCK changes are only accepted in RDP L0 (Section 6.4.9).

### 6.4.4 Option-byte overview

Table 28 lists all the user option bytes managed through the FLASH registers, as well as initial values before the first option-byte change (user default configuration).

**Table 28. Option-byte organization**

| Register | Fields (bit positions) | Initial value (user default configuration) |
| --- | --- | --- |
| FLASH_OPTSR | SWAP_BANK (31), SINGLE_BANK (30), EDATA_EN (29), Res. (28:24), BOOT0 (23), BOOT_SEL (22), IWDG_STDBY (21), IWDG_STOP (20), Res. (19:16), RDP_LEVEL (15:8), NRST_STDBY (7), NRST_STOP (6), Res. (5), WWDG_SW (4), IWDG_SW (3), Res. (2:0) | SWAP_BANK = 0, SINGLE_BANK = 0, EDATA_EN = 1, BOOT0 = 0, BOOT_SEL = 0, IWDG_STDBY = 1, IWDG_STOP = 1, RDP_LEVEL = 1110 1101, NRST_STDBY = 1, NRST_STOP = 1, WWDG_SW = 1, IWDG_SW = 1 |
| FLASH_OPTSR2 | Res. (31:5), SRAM2_ECC (4), Res. (3:2), SRAM2_RST (1), SRAM1_RST (0) | SRAM2_ECC = 1, SRAM2_RST = 1, SRAM1_RST = 1 |
| FLASH_BOOTR | BOOTADD[31:0] (31:8), BOOT_LOCK (7:0) | BOOTADD = 0x0800_00, BOOT_LOCK = 0xC3 |
| FLASH_WRPSG1R | WRPG[31:0] (31:0) | all bits 1 |
| FLASH_WRPSG2R | WRPG[31:0] (31:0) | all bits 1 |
| FLASH_OTPBLR | Res. (31:24), LOCKBL (23:0) | LOCKBL all bits 0 |
| FLASH_BL_COM_CFG | BL_COM_CFG[31:0] (31:0) | all bits 1 |
| FLASH_HDP1R | Res. (31:24), HDP1_END (23:16), Res. (15:8), HDP1_STRT (7:0) | HDP1_END = 0000 0000, HDP1_STRT = 0000 0001 |
| FLASH_HDP2R | Res. (31:24), HDP2_END (23:16), Res. (15:8), HDP2_STRT (7:0) | HDP2_END = 0000 0000, HDP2_STRT = 0000 0001 |
| FLASH_OEMKEYR1 | OEMKEY[31:0] (31:0) | all bits 1 |
| FLASH_OEMKEYR2 | OEMKEY[63:32] (31:0) | all bits 1 |
| FLASH_OEMKEYR3 | OEMKEY[95:64] (31:0) | all bits 1 |
| FLASH_OEMKEYR4 | OEMKEY[127:96] (31:0) | all bits 1 |
| FLASH_BSKEY | BSKEY[31:0] (31:0) | 1010 1010 1010 1010 1010 1010 1010 1010 |

*Digest note:* Computed 32-bit initial values: FLASH_OPTSR = 0x2030 EDD8 (RDP_LEVEL = 0xED = L0); FLASH_OPTSR2 = 0x0000 0013 (SRAM1 and SRAM2 not erased on system reset, SRAM2 ECC disabled); FLASH_BOOTR = 0x0800 00C3 (boot address 0x0800 0000, unlocked); FLASH_BSKEY = 0xAAAA AAAA. Note that the factory default is BOOT_SEL = 0, so the BOOT0 pin is ignored and the BOOT0 option bit (0) is used; the system bootloader is then reached only through the EMPTY check (see FLASH_ACR.EMPTY and RM0522 Chapter 4, Table 13). Table 28 shows HDPx_END/HDPx_STRT as 8-bit fields at 23:16 and 7:0 and BOOTADD as "BOOTADD[31:0]" at 31:8; the register descriptions (Sections 6.10.15, 6.10.28, 6.10.35) define BOOTADD[23:0] at bits 31:8 and HDPx_END[5:0] at 21:16, HDPx_STRT[5:0] at 5:0, which match the CMSIS header.

### 6.4.5 Description of user and system option bytes

The general-purpose option bytes that can be used by the application are listed below:

- Bank management
  - SWAP_BANK: bank swapping option, set to 1 to swap user FLASH banks after boot (see Section 6.3.11).
  - SINGLE_BANK: this bit is applicable for:
    - STM32C53x/542 with 128 Kbytes of flash
    - STM32C55x/562 with 256 Kbytes of flash
    - STM32C59x/5A3 with 512 Kbytes of flash

    If SINGLE_BANK = 1, the available user memory is located in a single bank. Otherwise, the device works in dual-bank mode. In any case, the address range is kept linear.
- Watchdog management
  - IWDG_STOP: independent watchdog IWDG counter active in Stop mode if 1 (stop counting or freeze if 0)
  - IWDG_STDBY: independent watchdog IWDG counter active in Standby mode if 1 (stop counting or freeze if 0)
  - IWDG_SW and WWDG_SW: hardware (0) or software (1) IWDG watchdog control selection

Note: If the hardware watchdog "control selection" feature is enabled (set to 0), the watchdog is automatically enabled at power-on, thus generating a reset unless the watchdog key register is written to or the down-counter is reloaded before the end-of-count is reached. Depending on the configuration of IWDG_STOP and IWDG_STDBY options, the IWDG can continue counting (1) or not (0) when the device is in Stop or Standby mode, respectively. When the IWDG is kept running during Stop or Standby mode, it can wake up the device from these modes.

- Reset management
  - NRST_STDBY: generates a reset when entering Standby mode if cleared to 0.
  - NRST_STOP: generates a reset when entering Stop mode if cleared to 0.

Note: Whenever a Standby (respectively Stop) mode entry sequence is successfully executed, the device is reset instead of entering Standby (respectively Stop) mode if NRST_STDBY (respectively NRST_STOP) is cleared to 0.

- Bootloader configuration

  After reset, if the STMicroelectronics bootloader is selected as boot location, it reads the contents of BL_COM_CFG, and only attempts to establish communication on selected interfaces. This setting allows using the bootloader safely in applications where it otherwise may cause trouble by reconfiguring some GPIOs.

When STMicroelectronics delivers the device, the values programmed in the general-purpose option bytes are the following:

- Watchdog management
  - IWDG active in Standby and Stop modes (option value = 0x1)
  - IWDG not automatically enabled at power-on (option byte value = 0x1)
- Reset management:
  - A reset is not generated when the device enters Standby or Stop low-power mode (option byte value = 0x1)

Refer to Section 6.10 for details.

*Digest note:* For STM32C551/C552, SINGLE_BANK is meaningful only on the 256-Kbyte parts. On the 512-Kbyte parts (2 x 256 Kbytes) the RM does not list SINGLE_BANK as applicable.

### 6.4.6 Description of data protection option bytes

The option bytes that can be used to enhance data protection are listed below:

- RDP_LEVEL[7:0]: product lifecycle state (see Section 6.5.8 for details)
- WRP1/2: write-protection option of pages in bank1 (respectively bank2). It is active low. Refer to Section 6.5.5 for details.

**Table 29. Write-protection management**

| WRP bit number | Write-protected pages: STM32C53x/542/55x/562 | Write-protected pages: STM32C59x/5A3 |
| --- | --- | --- |
| Bit 0 | Page 0 | Page [0 to 1] |
| Bit 1 | Page 1 | Page [2 to 3] |
| ... | ... | ... |
| Bit N | Page N | Page [2 x N to 2 x N +1] |

- HDPx: HDPL exclusive area control in the user flash memory.

When factory programmed, values of the data-protection option bytes are the following:

- Read-out protection level: L0 (Open)
- Write protection disabled (all option byte bits set to 1)

Refer to Section 6.10 for details.

*Digest note:* For STM32C551/C552 the left column applies: one WRP bit per 8-Kbyte page (bits 0 to 31 for the 32 pages of a 512-Kbyte part's bank).

### 6.4.7 Description of data FLASH option bytes

The option bytes that can be used to address the data FLASH pages are:

- EDATA_EN: activate data FLASH area for this device (see Section 6.3.10 for details).

### 6.4.8 Description of boot-address option byte

Below the list of option bytes that can be used to configure the appropriate boot address for an application:

- RDP_LEVEL: Influences the boot sequence indirectly.
- BOOTADD: Selects default boot address.
- BOOT_LOCK: Protects the boot configuration from further modification attempts.
- SWAP_BANK: bank swapping option, set to 1 to swap user FLASH banks after boot (see Section 6.3.11). If BOOT_LOCK is active, the value in SWAP_BANK is fixed, read-only.
- BOOT0 management
  - BOOT0: This option bit is the value of BOOT0 used depending on BOOT_SEL to select boot location. BOOTLOADER (1) or User code(0).
  - BOOT_SEL: BOOT0 value is taken from option bit (0) or from BOOT0 pin (1)

When STMicroelectronics delivers the device, the RDP_LEVEL is L0, BOOT_LOCK is not set (0xC3). Address BOOTADD is 0x0800 0000.

Refer to Section 6.10 for details.

*Digest note:* Boot selection itself (BOOT_SEL, BOOT0 option bit, BOOT0 pin, EMPTY flag, RDP level) is tabulated in RM0522 Chapter 4, Table 13 (outside this chapter): in L0, if BOOT0 (pin or option bit, as selected by BOOT_SEL) is 1 the device boots the bootloader; if it is 0 the device boots BOOTADD unless EMPTY = 1 (the 32-bit word at BOOTADD reads 0xFFFF FFFF at option-byte loading), in which case it boots the bootloader. In L2_wBS and L2 it always boots BOOTADD.

### 6.4.9 Specific rules for modifying option bytes

Besides the OPTLOCK bit and register access rules, there are additional protection means for selected security-sensitive option byte fields.

Multiple option bytes can be modified simultaneously, but if they rely on each other for protection, both states are checked.

With few exceptions listed in this section, failing to uphold the rules results in raising OPTCHANGEERR flag (Section 6.8.6 for additional details).

**Table 30. Specific OB modifying rules overview**

| OB | HDPL | Value | RDP level |
| --- | --- | --- | --- |
| RDP_LEVEL | - | Set of possible transitions | Set of possible transitions (Table 36) |
| HDP | 1(1) | - | - |
| BOOTADD | - | - | L0 open |
| LOCKBL | - | One way switch(1) | - |
| SWAP_BANK | - | BOOT_LOCK can restrict this change | - |
| BOOT_LOCK | - | - | L0 open |

Notes:

1. No OPTCHANGEERR is raised in violation of this.

Even in the closed RDP_LEVEL progression, some OBs can still be modified, if all the other constraints are satisfied. An overview is presented in the table below.

**Table 31. OBs modifiable in L2 product**

| RDP_LEVEL | OBs that can be modified |
| --- | --- |
| L2_wBS or L2 | SWAP_BANK, LOCKBL, RDP_LEVEL |

Specific rules must be respected to update the following OBs:

- **RDP_LEVEL:** its transitions follow a state machine with two types of transition. Locking down the product is allowed without restriction. Opening the product is only possible under the condition that OEM key were provisioned ahead. The regression to L0 RDP_LEVEL results in the erasing of the protected content (see Section 6.5.8).
- **HDP:** Can only be modified in HDPL0 and HDPL1.
- **BOOTADD:** Can only be changed in Open RDP L0 (open).
- **LOCKBL:** Can only be changed freely in one direction. A permanent irreversible switch.
- **SWAP_BANK:** Cannot be modified when BOOT_LOCK is active (0xB4).
- **BOOT_LOCK:** Can only be changed freely in locking direction. Unlock is possible in L0.

Note: For all user option bytes above, default values are loaded and Tamper is signaled when a double ECC error occurs during OBL.

## 6.5 FLASH security and protections

Since sensitive information are stored in the flash memory, it is important to protect it against unwanted operations such as reading confidential areas, illegal programming of immutable pages, or malicious flash memory erasing.

For that purpose, the flash memory implements the following protection mechanisms:

- Temporal isolation protection (HDP)
- Configuration protection
- User FLASH write protection
- Device boot state management
- OTP locking

This section provides a detailed description of all these security mechanisms.

The flash memory interface evaluates the access restrictions in the following order:

1. Write protection (for write access)
2. HDP

### 6.5.1 Hide protection (HDP)

A nonvolatile hide-protection (HDP) area per bank can be defined with a page granularity. Access to the hide-protection area can be denied by progressing the HDPL level in the SBS.

When the HDPL = 1, no user FLASH is protected by the HDP. With HDPL ≥ 2, the user OB defined HDP area in each bank is closed. No read, write, fetch, or erase is allowed in the HDP area.

The HDP area can be extended. The extension setting is only a register value, not stored in the OB. With HDPL = 3, the HDP area remains activated and the extension is added. If an extension is added while the base user OB defined area is not active, the extension covers one more page, because HDPx_END page is also protected.

The HDPL level can be only cleared by a system reset, there is no means to deactivate the HDP area.

The protected HDP area is defined by setting its size using start and end pages .

The size of the inaccessible area can be extended using register FLASH_HDPEXTR values HDPx_EXT. The value HDPx_EXT is a number of pages added to the HDP area (past the HDPx_END page). The volatile HDPx_EXT value in the register can be increased, but cannot decrement.

In case of HDPx_STRT > HDPx_END, the extension covers (HDPx_EXT + 1) size area between pages marked by HDPx_END and HDPx_END + HDPx_EXT.

By default, the HDPx_END is set to zero and HDPx_STRT is set to one. This means that the HDP area in user FLASH is zero size, and extends from the FLASH start address (first page).

For example, to protect area by HDP from 0x0800 2000 (included) to 0x0800 7FFF (included):

- For physical bank1, the option-byte registers must be programmed with:
  - HDP1_STRT = 0x01,
  - HDP1_END = 0x03.

**Figure 14. HDP in user flash memory**

A flash bank is drawn from Page 0 to Page 31. The span from PSTRT = 0x01 to PEND = 0x03 is labelled "HDP1 – HDPL1 closes". A second span starting at PEND = 0x03 and covering two further pages is labelled "HDP_EXT = 0x02".

- Once the HDPL is incremented to 2, the marked area becomes inaccessible. The HDPL = 2 code then sets the extension size to 2. Once the HDPL is incremented to 3, the extension area becomes also inaccessible.

  Alternatively, if:
  - HDP1_END = 0
  - HDP1_START = 1
  - HDPx_EXT = 1

  Page 0 and page 1 are HDP protected.

  Or a rather unusual example:
  - HDP1_END = 2
  - HDP1_START = 7
  - HDPx_EXT = 3
- Pages 2 until 5 are HDP protected. Here the user must know that, if the application needs pages 2 until 4 only as HDP area, HDPx_EXT must be programmed at 2 instead of 3.
- If the two banks are swapped, the protection defined to physical bank1 remains on the physical bank1, unaffected by swapping. Separate protection applies to physical bank2 and the option bytes registers must also be programmed with:
  - HDP2_STRT = 0x01
  - HDP2_END = 0x03

Note: For more details on the bank-swapping mechanism, refer to Section 6.5.3.

**Table 32. Secure hide protection**

| HDPL | HDPx watermark option byte values (x = 1, 2) | Hide protection area |
| --- | --- | --- |
| HDPL = 1 | - | No inaccessible HDP area in user flash memory |
| HDPL = 2 | HDPx_END < HDPx_STRT | No inaccessible HDP area in user flash memory |
| HDPL = 2 | HDPx_END = HDPx_STRT | Exactly one page is protected by HDP |
| HDPL = 2 | HDPx_END > HDPx_STRT | The area between HDPx_STRT and HDPx_END is HDP protected. |
| HDPL = 3 | HDPx_END < HDPx_STRT and HDPx_EXT = 0 | No inaccessible HDP area in user flash memory |
| HDPL = 3 | HDPx_END < HDPx_STRT and HDPx_EXT > 0 | The area betwen (HDPx_END + HDPx_EXT) is HDP protected |
| HDPL = 3 | HDPx_END ≥ HDPx_STRT and HDPx_EXT > 0 | The area between min (HDPx_STRT, HDPx_END) and (HDPx_END + HDPx_EXT) is HDP protected |

**Table 33. HDP protections summary**

| HDP protection | User flash memory: access to OB HDP area, HDPL 2 or 3 | User flash memory: access to OB HDP area, HDPL1 | User flash memory: access to EXT HDP area, HDPL3 | User flash memory: access to EXT HDP area, HDPL1 or HDPL 2 |
| --- | --- | --- | --- | --- |
| Fetch | BUS ERROR | OK | BUS ERROR | OK |
| Read | RAZ | OK | RAZ | OK |
| Write | WI, WRPERR | If WRP disabled: OK, else: WI, WRPERR | WI, WRPERR | If not WRP: OK, Else: WI, WRPERR |
| Erase (mass erase) | WI, WRPERR | If WRP disabled: OK, else: WI, WRPERR | WI, WRPERR | If not WRP: OK, Else: WI, WRPERR |

*Digest note:* With the factory HDP option values (HDPx_STRT = 1, HDPx_END = 0) and FLASH_HDPEXTR = 0, no HDP area exists, so HDP does not restrict a bootloader that never raises HDPL.

### 6.5.2 Flash memory register privileged and unprivileged modes

The FLASH registers can be read and written by privileged and unprivileged accesses, depending on the PRIV bit in FLASH_PRIVCFGR.

- When the PRIV bit is reset, all flash memory registers can be read and written by both privileged or unprivileged access.
- When the PRIV bit is set, all flash memory registers can be read and written by privileged access only. Unprivileged access to a privileged registers is RAZ/WI.

### 6.5.3 Flash memory banks attributes in case of bank swap

The SWAP_BANK option bit modifies the address of each bank in the memory map. When SWAP_BANK is reset, FLASH bank1 is mapped at the lower address range. When SWAP_BANK is set, FLASH bank1 is mapped at the higher address range. FLASH bank attributes follow their bank contents so there is no need to modify their setting registers when swapping banks:

- FLASH write protection page FLASH_WRPG (refer to Section 6.5.5)
- Hide protection in FLASH_HDPx registers

The SWAP_BANK is rendered immutable by setting BOOT_LOCK.

Note: The BK_ECC bit in FLASH_OEMKEYR2_CUR and FLASH_ECCDETR, BKSEL bit in FLASH_CR always refers to bank1 (respectively bank2) when it is low (respectively high), regardless of the SWAP_BANK value.

*Digest note:* "FLASH_OEMKEYR2_CUR" does not exist; BK_ECC is in FLASH_ECCCORR and FLASH_ECCDETR (Sections 6.10.30, 6.10.31).

The figure below shows how security attributes and protections behave in case of bank swap.

**Figure 15. Protection attributes in case of bank swap illustration**

Before the swap (top): Bank 1, carrying an HDP area at its start and write protection blocks, is mapped at 0x0800 0000 to 0x0803 FFFF; Bank 2 ("No protections defined") is mapped at 0x0804 0000 to 0x0807 FFFF. After the swap (bottom): Bank 2 ("No protections defined") is mapped at 0x0800 0000 to 0x0803 FFFF, and Bank 1 is mapped at 0x0804 0000 to 0x0807 FFFF, still carrying its HDP area and write protection blocks.

*Digest note:* The addresses in Figure 15 are those of the 512-Kbyte STM32C55x/562 parts (Table 25).

### 6.5.4 Flash memory configuration protection

The FLASH uses hardware mechanisms to protect the following assets against unwanted or spurious modifications (such as software bugs):

- Option-byte changes
- Write operations
- Erase commands
- Interrupt masking

The FLASH configuration registers protection is summarized in Table 34. Registers not present in this table are not protected by a key.

**Table 34. FLASH interface register protection summary**

| Register name | Unlocking register | Protected asset |
| --- | --- | --- |
| FLASH_CR | FLASH_KEYR | Write/erase control |
| FLASH_OPTCR | FLASH_OPTKEYR | FLASH bank option-byte words change |

*Digest note:* The key values are given only in the register descriptions: FLASH_KEYR 0x4567 0123 then 0xCDEF 89AB (Section 6.10.2); FLASH_OPTKEYR 0x0819 2A3B then 0x4C5D 6E7F (Section 6.10.3). Both must be written as 32-bit accesses (Section 6.3.2). A wrong key, or a second unlock sequence on an already-unlocked register, raises a bus error (Sections 6.3.2 and 6.8.7) and leaves the register locked until the next system reset (Sections 6.3.5, 6.3.6, 6.10.5, 6.10.7). Check FLASH_CR.LOCK (or FLASH_OPTCR.OPTLOCK) before writing the keys.

### 6.5.5 Write protection

The purpose of FLASH write protection is to prevent unwanted modifications to embedded nonvolatile code and/or data.

A write-protected group of pages can neither be erased nor programmed. As a result, a bank erase cannot be performed if some page is write-protected, unless a RDP level transition to L0 is triggered (erasing the whole user flash memory).

Note: Write protection errors are documented in Section 6.8.

### 6.5.6 FLASH data area protections

The FLASH can be configured to have 64-Kbyte (or 48-Kbyte if EDATA_EN is set) memory area to store data and emulate EEPROM (see Section 6.3.10: FLASH data area). These pages can not be protected by HDP or WRPGS whatever the setting of EDATA_EN.

### 6.5.7 RDP protection and life cycle management

Nonvolatile states, or debug states, are determined by the RDP levels set by user option bytes. Debug possibility and possibility to change selected security settings are related to this state. While the state is stored in the OB, it is the SBS that controls the debug policy.

**Figure 16. RDP transitions**

State diagram with three states: Level 0 (RDP = 0xED), Level 2 + boundary scan (RDP = 0xD1), and Level 2 (RDP = 0x72).

- Level 0 to Level 2 + boundary scan: "Write RDP = 0xD1" (blue: RDP increase + option-byte modification, valid at next reset).
- Level 0 to Level 2: "Write RDP = 0x72" (blue: RDP increase + option-byte modification, valid at next reset).
- Level 2 + boundary scan to Level 2: "BSKEY" with a lock symbol (yellow: transition to L2 from L2_wBS thanks to BSKEY sent to debug interface under reset).
- Level 2 + boundary scan to Level 0 and Level 2 to Level 0: "OEM" with a lock symbol (purple: regression not possible by default – can be allowed by debug interface under reset with OEM key if previously provisioned in L0 RDP level).
- Level 0 self-loop (green: RDP unchanged + option-byte modification).
- Level 2 + boundary scan self-loop and Level 2 self-loop (red: no option bytes modification, except SWAP_BANK if BOOT_LOCK is not active).

HDP works equally regardless of the RDP level.

**Table 35. RDP levels description**

| RDP_LEVEL | Code in OB | Description |
| --- | --- | --- |
| L0 (Open) | 0xED | Full debug capabilities; Read/Write/Erase Flash is possible; Read/Modify the option bytes; Boot in bootloader or user flash based on BOOT0 pin or option bytes; Boundary scan available under reset |
| L2_wBS (Closed + boundary scan) | 0xD1 | No debug capabilities; Read/Write/Erase Flash is possible; All option bytes Read by user code; SWAP_BANK (depending on BOOT_LOCK) & LOCKBL (for OTP) option bytes can be modified; Boot in user flash only; Boundary Scan available under reset |
| L2 (Closed) | 0x72 | No debug capabilities; Read/Write/Erase Flash is possible; All option bytes Read by user code; SWAP_BANK (depending on BOOT_LOCK) & LOCKBL (for OTP) option bytes can be modified; Boot in user flash only |

**Caution:** STMicroelectronics cannot functionally analyze parts with level 2 protection enabled. Regress parts to RDP level 0 before returning them for analysis (refer to OEM RDP lock mechanism).

### 6.5.8 RDP level transitions

Progressing to more closed levels is the normal product life cycle, that does not require security measures. Transition in direction to open level (RDP Level 0) is a regression, and is possible only thanks to the OEM Key.

There is no restriction on reading the current RDP level.

**Transitions to L2 with boundary scan (L2_wBS) or L2 (L2) closed states**

Transition from L0 to L2 with or without boundary scan is managed either by software running on the device, or directly, using a debug interface. By software, it is assumed that transitions are triggered by the bootloader, but generally any software running on the device can do a progress transition.

**Caution:** The new RDP Level will only be valid after next system or power reset.

Transition from L2 with boundary scan to L2 is only feasible thanks the BSKEY option-byte key:

- If the BSKEY key have not been modified under L0 state, the default value apply.
- If the BSKEY key have been modified under L0 state, the user must apply the key populated.

This key must be written under reset and L2 with boundary scan thanks to JTAG in order to progress to L2 RDP level.

**Regression to L0 open debug level**

This transition is a full regression, possible from either L2_wBS or L2 if an OEM key has been provisioned. The debug tools are used to provide the OEM key, if the key matches the one provisioned under L0, the device regresses securely in RDP L0.

The regression has the following consequences:

- RDP level updated
- User options updated (security settings reset)
- Flash memory mass erase (even write protected pages)

**Table 36. RDP levels transitions**

| From | To L0 | To L2_wBS | To L2 |
| --- | --- | --- | --- |
| L0 | - | OB update thanks to debug or bootloader | OB update thanks to debug or bootloader |
| L2_wBS | OEM key regression | - | BSKEY |
| L2 | OEM key regression | X | - |

Notes:

1. 'X' = transitions that are not permitted (OPTCHANGEERR raised). '-' = no change.

An attempt to make a illegal transition results in the OPTCHANGEERR.

An incorrect RDP_LEVEL (on OBL) is interpreted as L2.

*Digest note:* Permanent-lock conditions that follow from this section: (a) programming RDP_LEVEL to 0xD1 or 0x72 while OEMLOCK = 0 (no OEM key ever provisioned in L0) makes the closed state irrevocable (FLASH_SR.OEMLOCK description: "progressing to RDP L2_wBS or L2 is irrevocable"); (b) any RDP_LEVEL byte other than 0xED, 0xD1 or 0x72 read at OBL, and an option-byte double ECC error at OBL (default FLASH_OPTSR_CUR = 0x20B0 72D8), both give L2; (c) in L2_wBS/L2 only SWAP_BANK, LOCKBL and RDP_LEVEL can still be changed, and BOOT_LOCK cannot be unlocked outside L0; (d) LOCKBL bits are irreversible in every state. Never write RDP_LEVEL from firmware or a bootloader.

### 6.5.9 OEM key management

The OEM 128-bit key (OEMKEY) can be defined in order to permit the RDP regression.

**OEM lock activation**

The 128-bit key is coded on four registers: FLASH_OEMKEYR1 to FLASH_OEMKEYR4. OEMKEY and BSKEY cannot be read through these registers. They are read as zero.

**Caution:** OEMKEY can only be modified in readout protection level 0.

In order to activate OEM regression mechanism, the following steps are needed:

1. Check that the RDP is at L0.
2. Write a 128-bit key in FLASH_OEMKEYR1 to FLASH_OEMKEYR4.
3. Launch option modification by setting the OPTSTRT bit in FLASH_CR.
4. Wait for the BSY bit to be cleared and check that OPTWERR is not set.
5. Check that OEMLOCK is set.

Note: Once the OEM KEY has been programmed a first time, the OEMLOCK bit remains set. The user can reprogram the key, but cannot erase it.

*Digest note:* OPTSTRT is in FLASH_OPTCR, not FLASH_CR, and there is no OPTWERR flag in FLASH_SR; the option-change error flag is OPTCHANGEERR. The same applies to the BSKEY steps in Section 6.5.10.

**OEM key validation mechanism**

The OEM RDP lock mechanism is active when the OEMLOCK bit is set. The OEMKEY, can be validated while in RDP L0.

- Shift OEMKEY[31:0], then OEMKEY[63:32], then OEMKEY[95:64], then OEMKEY[127:96] through JTAG or SWD under reset in DBGMCU_DBG_AUTH_HOST register.
- If this key matches the OEMKEY value:
  - A status bit in DBGMCU_DBG_VALR indicates that the adequate key has been successfully entered, a power sequence is required to clear the validation status bit. Omitting this step will prevent to enter RDP Level 2.
- If the key does not match the OEMKEY value, a power sequence is required to clear the validation status bit and retry.

**OEM RDP regression mechanism**

The OEM RDP lock mechanism is active when the OEMLOCK bit is set. It authorizes RDP L2 to RDP L0 regression.

- Shift OEMKEY[31:0,] then OEMKEY[63:32], then OEMKEY[95:64], then OEMKEY[127:96] through JTAG or SWD under reset in DBGMCU_DBG_AUTH_HOST register.
- If this key matches the OEMKEY value:
  - The RDP regression is launched by hardware when the reset is released (it is not possible to execute instructions when the key is matching).
  - A power-on reset must be applied (cycle VDD power supply off and on).
- If the key does not match the OEMKEY value, the RDP regression is blocked until next power-on reset.

### 6.5.10 BS key management

The BS key is used to transition from RDP L2_wBS to L2. This key is coded in FLASH_BSKEYR, and can be modified only under RDP L0. During production, the value 0xAAAA AAAA is preprogrammed in BSKEY option bytes.

In order to personalize BSKEY transition mechanism, the following steps are needed:

1. Check that the RDP is at L0.
2. Write the desired key in FLASH_BSKEYR.
3. Launch option modification by setting the OPTSTRT bit in FLASH_CR.
4. Wait for the BSY bit to be cleared and check that OPTWERR is not set.
5. Check that BSLOCK bit has been set.

**BSKEY RDP transition mechanism**

In order to transition from RDP L2_wBS to L2 follow these steps:

1. Provide BSKEY[31:0] through JTAG or SWD under reset in DBGMCU_BSKEY_PWD. The key is 0xAAAA AAAA if not updated under L0, otherwise it is the value provisioned in BSKEYR.
2. If this key matches the BSKEY value:
   - The RDP transition is launched by hardware (it is not possible to execute instructions when the key is matching).
   - A power-on reset is applied (cycle VDD power supply off and on).

if the key does not match the BSKEY value, the RDP transition and any access to the flash memory are blocked until a next power-on reset.

### 6.5.11 One-time-programmable and read-only memory protections

OTP/RO in the flash memory are detailed in Section 6.3.9. There is no protection provided by the FLASH interface other than the dedicated write protection.

No write is possible to the RO area, once it was established in manufacturing. OTP write protection describes a method of locking out the OTP area.

The access conditions are summarized in the table below.

**Table 37. OTP/RO access constraints**

| Access | Undefined addresses (0x08FF_F200 - F7FF, 0x08FF_FE00 - FFFF) | 4.5-Kbyte page dedicated to OTP (0x08FF_E000 - F1FF OTP) | 1.5-Kbyte page dedicated to RO (0x08FF_F800 - FDFF RO) |
| --- | --- | --- | --- |
| X | Bus error | Bus error | Bus error |
| R | Bus error | If correct size OK, else bus error | If correct size OK, else bus error |
| W | Bus error | Bus error if incorrect size. WRPERR if block is protected by LOCKBL, else OK. | If correct size WI, else bus error |
| erase | Not applicable | Not applicable | Not applicable |

## 6.6 System memory

### 6.6.1 System memory introduction

System memory stores bootloader firmware that is programmed by ST during production. The bootloader provides runtime services to user firmware. These services are described hereafter in this section.

### 6.6.2 Bootloader user functions

As other microcontroller peripherals features and mapping, the bootloader library functions are exposed to user within the CMSIS device header file provided by the STM32CubeC5 firmware package. Refer to the online HAL/LL drivers documentation to get more details regarding STM32CubeC5 firmware package. Bootloader library provides runtime services through prefixed EXITHDP functions.

**Table 38. C defined macro for HDP services**

| C defined macro | Location in flash memory |
| --- | --- |
| EXITHDP_PFUNC | 0x0BF883E0 |

**EXITHDPLIB**

The user firmware calls EXITHDPLIB functions using EXITHDPLIB_PFUNC C defined macro, that points to a location within system memory.

**Table 39. EXITHDPlib interface function list**

| Library | Function |
| --- | --- |
| EXITHDP_PFUNC | JumpHDPLvl2 |
| EXITHDP_PFUNC | JumpHDPLvl3 |

*Digest note:* The CMSIS header names the macro `EXITHDPLIB_PFUNC` (base `EXITHDPLIB_SYS_FLASH_PFUNC_START = 0x0BF8 83E0`), with JumpHDPLvl2 at structure offset 0x0C and JumpHDPLvl3 at offset 0x10, and `EXITHDPLIB_ERROR = 0xF5F5 F5F5`.

The EXITHDPLIB functions are described within section hereafter.

**a) JumpHDPLvl2**

Prototype:

`uint32_t JumpHDPLvl2(uint32_t VectorTableAddr, uint32_t MPUIndex)`

User code function call example:

`EXITHDPLIB_PFUNC->JumpHDPLvl2((uint32_t)NextVectorTableAddr, 1U );`

Arguments:

- VectorTableAddr: Input parameter, address of the next vector table to apply. The vector table format is the one used by the Cortex-M33 core.
- MPUIndex: Input parameter, MPU region index. Caller function shall define but keep disable the corresponding MPU region before calling JumpHDPLvl2. The function enables the MPU region before jumping to the Reset Handler of the vector table. The vector table Reset Handler function shall belong to the MPU region.

Descriptions:

User calls JumpHDPLvl2 to:

- Close user Flash HDPL1 area by incrementing HDPL to 2
- Jump to the reset handler embedded within the Vector Table which address is passed as input parameter

After closing HDPL1, JumpHDPLvl2 enables the MPU region provided as input parameter. Once the MPU is enabled, the function sets the SP to the address provided by the passed Vector Table and jumps to the Reset Handler function supported by the Vector Table too. JumpHDPLvl2 does not set the new vector table.

On successful execution, the function does not return and does not push LR onto the stack.

Errors:

In case of failure (bad input parameter value), EXITHDPLIB_Sec_JumpHDPLvl2 returns 0xF5F5F5F5.

**b) JumpHDPLvl3**

Prototype

`uint32_t JumpHDPLvl3(uint32_t VectorTableAddr, uint32_t MPUIndex)`

User code function call example:

`EXITHDPLIB_PFUNC->JumpHDPLvl3((uint32_t)NextVectorTableAddr, 1U );`

Arguments:

- VectorTableAddr: Input parameter, address of the next vector table to apply. The vector table format is the one used by the Cortex-M33 core.
- MPUIndex: Input parameter, MPU region index. Caller function shall define but keep disable the corresponding MPU region before calling JumpHDPLvl3. The function enables the MPU region before jumping to the Reset Handler of the vector table. The vector table Reset Handler function shall belong to the MPU region.

Descriptions:

User calls JumpHDPLvl3 to:

- Close user Flash HDPL1 and HDPL2 areas by incrementing HDPL up to 3
- Then jump to the reset handler embedded within the Vector Table which address is passed as input parameter

After closing HDPL1/2, JumpHDPLvl3 enables the MPU region provided as input parameter. Once the MPU is enabled, the function sets the SP to the address provided by the passed Vector Table and jumps to the Reset Handler function supported by the Vector Table too. JumpHDPLvl3 does not set the new vector table.

On successful execution, the function does not return and does not push LR onto the stack.

Errors:

In case of failure (bad input parameter value), JumpHDPLvl3 returns 0xF5F5F5F5.

## 6.7 FLASH low-power modes

The table below summarizes the FLASH behavior in STM32 low-power modes. The FLASH belongs to the core domain.

**Table 40. Effect of low-power modes on the FLASH**

| Power mode | Allowed if FLASH busy | FLASH power mode |
| --- | --- | --- |
| Run/Sleep | Yes | Run |
| Stop (clock stopped) | No | Clock gated (in normal or low-power mode) |
| Standby | No | Off |

The procedure to switch the FLASH into various power mode (run, clock gated, stopped, off) is described hereafter.

Note: For more information on microcontroller power states, refer to Section 8: Power control (PWR).

**Managing FLASH domain switching to Stop or Standby mode**

As explain in Table 40, if the FLASH informs the RCC that it is busy (BSY, DBNE, WBNE is set), the microcontroller cannot switch the core domain to Stop or Standby mode.

There are two ways to release the FLASH:

- Reset the WBNE busy flag in FLASH_SR by any of the following actions:
  - Complete the write buffer with missing data.
  - Force the write operation without filling the missing data by activating the FW bit in FLASH_CR. This forces all missing data "high".
- Poll BSY busy bits in FLASH_SR until they are cleared. This indicates that all recorded write, erase, and option change operations are complete.

The microcontroller can then switch the domain to Stop or Standby mode.

## 6.8 FLASH error management

The FLASH automatically reports when an error occurs during a read, program or erase operation. A wide range of errors are reported:

- Write protection error (WRPERR) (Section 6.8.1)
- Programming sequence error (PGSERR) (Section 6.8.2)
- Error correction code error (ECCC/ECCD) (Section 6.8.3)
- Option-byte change error (OPTCHANGEERR) (Section 6.8.4)

*Digest note:* The section references in this list are off by two: ECCC/ECCD is Section 6.8.5 and OPTCHANGEERR is Section 6.8.6; STRBERR (Section 6.8.3) and INCERR (Section 6.8.4) are not listed here.

The application software can individually enable the interrupt for each error, as detailed in Section 6.9.

Note: For all errors, the application software must clear the error flag before attempting a new modify operation.

Since there is just one write buffer and only one operation is allowed at a time, the write control bits and status bits are shared by both banks:

- Write control bits (PG, FW, EOPIE, WRPERRIE, PGSERRIE, STRBERRIE, INCERRIE, CLR_EOP, CLR_WRPERR, CLR_STRBERR, CLR_INCERR, CLR_PGSERR) controls bank1 and 2 at the same time.
- Write status flag reports (WBNE, DBNE, EOP, WRPERR, PGSERR, STRBERR, INCERR, BSY) error for bank1 and 2 at the same time.

### 6.8.1 Write protection error (WRPERR)

When an illegal erase/program operation is attempted to the nonvolatile memory, the FLASH sets the write protection error flag WRPERR in FLASH_SR.

An erase operation is rejected and flagged as illegal if it targets one of the following memory areas:

- A page write-protected with WRP.
- An HDP area while the HDPL has made it inaccessible.

A program operation is ignored and flagged as illegal if it targets one of the following memory areas:

- The system flash memory
- A user page write-protected with WRP
- An OTP block, locked with LOCKBL
- A reserved area

When WRPERR flag is raised, the operation is rejected and nothing is changed in the corresponding bank.

If this error is detected the write buffer is invalidated.

Note: WRPERR flag has to be cleared before any erase/program operation.

WRPERR flag is cleared by setting CLR_WRPERR bit to 1 in FLASH_CCR.

If WRPERRIE bit in FLASH_CR is set to 1, an interrupt is generated when WRPERR flag is raised (see Section 6.9 for details).

### 6.8.2 Programming sequence error (PGSERR)

When the programming sequence is incorrect, the FLASH interface sets the programming sequence error flag PGSERR in FLASH_SR.

More specifically, PGSERR flag is set when one of below conditions is met:

- An error like INCERR, WRPERR, PGSERR, STRBERR, OPTCHANGEERR have not been cleared before requesting a new write or erase operation or options change.
- For erase, PGSERR is set:
  - If missing erase operation (FLASH_CR): STRT = 1 with (MER = 0, PER = 0, and BER = 0)
  - If page and bank erase requested at the same time (STRT and more than one of MER, PER and BER)
  - If PG is set during erase operation (it ensures that no erase request and write request happen at the same time): (STRT = 1) with (PG = 1)
  - If an erase operation is started while write buffer is waiting for next data: (STRT = 1) with WBNE = 1.
  - If an erase operation is started while DBNE = 1.
- For programming, PGSERR is set:
  - If missing write flag: A write operation is requested but the program enable bit PG has not been set in FLASH_CR prior to the request.
  - If a write operation to flash data area is requested but PG = 0.
  - If an AHB write request is received and (PER = 1, BER = 1, or MER = 1)
  - If a 16-bit data access requested while WBNE = 1.
- For options change, PGSERR is set:
  - If an option change is started while write buffer is waiting for next data: OPTSTRT = 1 with WBNE = 1
  - If OPTSTRT is set with DBNE = 1.

When PGSERR flag is raised as consequence of failed write attempt (FLASH programming), the current program operation is aborted, and nothing is changed in the corresponding bank. The write data buffer is also invalidated.

Note: When PGSERR flag is raised, there is a risk that the last write operation performed by the application has been lost because of the above protection mechanism. Hence it is recommended to generate interrupts on PGSERR, and to verify in the interrupt handler if the last write operation has been successful by reading back the value in the flash memory.

The PGSERR flag also blocks any new program operation. This means that PGSERR must be cleared before starting a new program operation.

PGSERR flag is cleared by setting CLR_PGSERR bit to 1 in FLASH_CCR.

If PGSERRIE bit in FLASH_CR is set to 1, an interrupt is generated when PGSERR flag is raised (see Section 6.9 for details).

*Digest note:* Leaving PG set while starting an erase (STRT with PG = 1), or leaving PER/BER/MER set while writing data, both raise PGSERR. Clear PG before an erase and clear PER before programming. A "16-bit data access requested while WBNE = 1" also means an OTP/EDATA write must not be interleaved with a partially filled 128-bit user-flash write buffer.

### 6.8.3 Strobe error (STRBERR)

When the application software writes several times to the same byte in the write buffer, the FLASH sets the strobe error flag STRBERR in FLASH_SR, whatever the target bank of the write access.

When STRBERR is raised, the current program operation is aborted and the write buffer is invalidated.

STRBERR is cleared by setting CLR_STRBERR bit to 1 in FLASH_CCR.

If STRBERRIE bit in FLASH_CR is set to 1, an interrupt is generated when STRBERR flag is raised (see Section 6.9 for details).

### 6.8.4 Inconsistency error (INCERR)

When a programming inconsistency is detected, the FLASH sets the inconsistency error flag INCERR in FLASH_SR.

More specifically, INCERR flag is set when the following condition is met:

- A write operation is attempted before completion of the previous write operation, for example:
  - The application software starts a write operation to fill the 128-bit write buffer, but sends a new write burst request to a different flash memory address before the buffer is full.

Note: INCERR flag must be cleared before starting a new write operation, otherwise a sequence error (PGSERR) is raised.

It is recommended to follow the sequence below to avoid losing data when an inconsistency error occurs:

1. Execute a handler routine when INCERR flag is raised.
2. Stop all write requests to FLASH.
3. Clear INCERR bit.
4. Restart the write operations where they have been interrupted.

INCERR flag is cleared by setting CLR_INCERR bit to 1 in FLASH_CCR.

If INCERRIE bit in FLASH_CR register is set to 1, an interrupt is generated when INCERR flag is raised (see Section 6.9 for details).

### 6.8.5 Error correction code error (ECCC/ECCD)

When a single-error correction is detected during a read, the FLASH interface sets the single-error correction flag ECCC in FLASH_ECCCORR.

When two ECC errors are detected during a read, the FLASH interface sets the double error detection flag ECCD in FLASH_ECCDETR.

When ECCC flag is raised, the corrected read data are returned. Hence the application can ignore the error and request new read operations. When ECCD flag is raised a NMI is generated. The software must invalidate the instruction cache (CACHEINV = 1) in the NMI interrupt service routine when the ECCD flag is set. This NMI can be masked in SBS registers Section 12.5.12: SBS ECC NMI mask register (SBS_ECCNMIR) for data access (OTP, data area, RO data).

When ECCC or ECCD flag is raised, the address of the FLASH word that generated the error is saved in the FLASH_ECCCORR (FLASH_ECCDETR). If the address corresponds to a read-only area, to a EDATA page (in user mode or in FLASH data area mode) or to an OTP area, the OTP_ECC or SYSF_ECC or EDATA_ECC bit is also set to 1 in FLASH_ECCCORRR (FLASHBS_ECCDETR). This register is automatically cleared when the associated flag that generated the error is reset.

A BK_ECC flag indicates in which FLASH bank the error occurred.

A SYSF_ECC flag indicates error detected in the system FLASH area.

*Digest note:* "FLASH_ECCCORRR (FLASHBS_ECCDETR)" means FLASH_ECCCORR (FLASH_ECCDETR). CACHEINV is a bit of the instruction cache (ICACHE) control register, documented in the ICACHE chapter, not in this chapter.

**Table 41. Locating ECC failure**

| OTP_ECC | SYSF_ECC | BK_ECC | DATA_ECC | FLASH area | ADDR_ECC min | ADDR_ECC max |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | 0/1 | 0 | User FLASH | 0x0000 | 0x7FFF(1) |
| 0 | 1 | 0/1 | 0 | System FLASH | 0x0000 | 0x0FFF |
| 1 | 0 | 1 | 0 | OTP | 0x0200 | 0x037F |
| 0 | 0 | 0/1 | 1 | EDATA page 0 | 0x0000 | 0x007F |
| 0 | 0 | 0/1 | 1 | EDATA page 1 | 0x0080 | 0x00FF |
| 0 | 0 | 0/1 | 1 | EDATA page 2 | 0x0100 | 0x017F |
| 0 | 0 | 0/1 | 1 | EDATA page 3 | 0x0180 | 0x01FF |
| 0 | 0 | 0/1 | 1 | EDATA page 4 | 0x0200 | 0x027F |
| 0 | 0 | 0/1 | 1 | EDATA page 5 | 0x0280 | 0x02FF |
| 0 | 0 | 0/1 | 1 | EDATA page 6 | 0x0300 | 0x037F |
| 0 | 0 | 0/1 | 1 | EDATA page 7 | 0x0380 | 0x03FF |
| 0 | 0 | 0/1 | 1 | EDATA page 8 | 0x0400 | 0x047F |
| 0 | 0 | 0/1 | 1 | EDATA page 9 | 0x0480 | 0x04FF |
| 0 | 0 | 0/1 | 1 | EDATA page 10 | 0x0500 | 0x057F |
| 0 | 0 | 0/1 | 1 | EDATA page 11 | 0x0580 | 0x05FF |
| 0 | 0 | 0/1 | 1 | EDATA page 12 | 0x0600 | 0x067F |
| 0 | 0 | 0/1 | 1 | EDATA page 13 | 0x0680 | 0x06FF |
| 0 | 0 | 0/1 | 1 | EDATA page 14 | 0x0700 | 0x077F |
| 0 | 0 | 0/1 | 1 | EDATA page 15 | 0x0780 | 0x07FF |

Notes:

1. ADDR_ECC maximum depends on the flash memory size of the product.

*Digest note:* The RM column header reads "DATA_ECC" (printed across three lines); it corresponds to the EDATA_ECC bit of FLASH_ECCCORR/FLASH_ECCDETR.

Note: In case of successive single correction or double detection errors, only the address corresponding to the first error is stored in FLASH_ECCCORR (FLASH_ECCDETR).

It is mandatory to clear ECCC or ECCD flags before starting a new read operation.

As the ECC interface is shared by the two banks, if the same error is registered simultaneously, a physical bank1 error is registered. Both errors are registered if one bank reports ECCD and the other bank ECCC.

ADDR_ECC value indicates the FLASH line where the ECC error occurred.

If the EDATA_EN option bit is set, the EDATA sectors are programmed and read as 16-bit accesses, (memory row being 137 bits long: 128-bit + 9-bit ECC). Consequently, the arrangement of the memory is modified. The first 32 bits of each row of a sector are filled first, then the bits from 32 to 63 and finally from 64 to 96 (the rest of the memory row contains ECC code). The ADDR_ECC indicates the memory line holding the failure. To identify the data corrupted on the line, DATA_ADDR_ECC bitfield value can be used to discriminate which column holds the failed data (only in case of error relative to data area or OTP).

Example: ADDR_ECC = 0x0312 and DATA_ADDR_ECC = 0x3.

- With ADDR_ECC between 0x0300 and 0x037F, the address of failure is in page 6, starting at 0x0900 2400.
- DATA_ADDR_ECC = 0b01X indicates the concerned column is the second, starting from 0x0900 2600.
- ADDR_ECC ending with 0xXX12 means the concerned row in memory is 0x12. With 4 bytes per column, this gives the 32-bit address as 0x0900 2648.
- DATA_ADDR_ECC = 0b0X1 indicates the concerned final address is the second 16-bit data, so 0x0900 264A.

ECCC (respectively ECCD) flag is cleared by setting to 1 the ECCC bit (respectively ECCD bit) in FLASH_ECCCORR (FLASH_ECCDETR).

If ECCC bit in FLASH_ECCCORR is set to 1, an interrupt is generated when ECCC flag is raised. Only NMI is generated for the ECCD (see Section 6.9 for details).

*Digest note:* The interrupt enable for ECCC is the ECCCIE bit (bit 25) of FLASH_ECCCORR, not the ECCC bit itself.

### 6.8.6 Option-byte change error (OPTCHANGEERR)

When the FLASH finds an error during an option-byte change operation, it aborts the operation, and sets the option-byte change error flag OPTCHANGEERR in FLASH_SR.

The error is raised after OPTSTRT bit set if one of the following occurs:

- Any forbidden RDP_LEVEL transition (Table 36).
- SWAP_BANK is locked out by BOOT_LOCK.
- Attempt to modify OB with invalid value not recognized by the specification (enumerated magic numbers only)
- Attempt to modify OB in RDP level where it is not allowed (usually a state open for debug is required for change)

Note: Exceptions and details provided in the OB description (see Section 6.4.9).

OPTCHANGEERR flag is cleared by setting CLR_OPTCHANGEERR bit to 1 in FLASH_CCR.

If OPTCHANGEERRIE bit in FLASH_CR is set to 1, an interrupt is generated when OPTCHANGEERR flag is raised (see Section 6.9 for details).

It is mandatory to clean the OPTCHANGEERR flag before starting a new operation (option change, erase, or write).

### 6.8.7 Miscellaneous HardFault errors

The following events generate a bus error on the corresponding bus interface:

- On main AHB system bus for access targeting code and data with 9-bit ECC.
  - Access to invalid address (including data addresses forbidden for code use)
  - Fetching from HDP area with incorrect HDPL value
  - Fetching from privilege area in unprivileged mode
- On AHB configuration or system bus for accesses targeting OTP/RO (all addresses using 6-bits ECC):
  - Wrong key input to FLASH_KEYR or FLASH_OPTKEYR
  - 8-bit accesses to system AHB interface
  - Wrong unlock sequence on a register

## 6.9 FLASH interrupts

The FLASH can generate a maskable interrupt to signal the following events on a given bank:

- Read and write errors (see Section 6.8)
  - Single ECC error correction during read operation
  - Write inconsistency error
  - Bad programming sequence
  - Strobe error during write operations
  - Option-byte change operation error
- Security errors (see Section 6.8)
  - Write protection error
- Miscellaneous events (described below)
  - End of programming

A NMI is raised on double-ECC-error detection during read operation.

The user can individually enable or disable FLASH interrupt sources by changing the mask bits in FLASH_CR, FLASH_ECCCORR, and FLASH_ECCDETR. Setting the appropriate mask bit to 1 enables the interrupt.

Note: Before writing, FLASH_CR must be unlocked as explained in Section 6.5.4.

The table below summarizes the available FLASH interrupt features. As mentioned, some flags need to be cleared before a new operation is triggered.

**Table 42. FLASH interrupt request**

| Interrupt event flag | Error flag label in register | Enable control bit | Clear flag to resume operation |
| --- | --- | --- | --- |
| End of operation event | EOP | EOPIE | N/A |
| Write protection error | WRPERR | WRPERRIE | Yes |
| Programming sequence error | PGSERR | PGSERRIE | Yes |
| Strobe error | STRBERR | STRBERRIE | Yes |
| Inconsistency error | INCERR | INCERRIE | Yes |
| Option byte error | OPTCHANGEERR | - | Yes |
| ECC single error correction event | ECCC | ECCCIE | No |
| ECC double error detection event(1) | ECCD | Disabled | No |

Notes:

1. NMI.

*Digest note:* Table 42 lists no enable bit for OPTCHANGEERR, but FLASH_CR bit 23 is OPTCHANGEERRIE (Section 6.10.7).

The status of the individual maskable interrupt sources described in Table 42 (except for option-byte error and ECC) can be read in FLASH_SR register. They can be cleared by setting to 1 the adequate bit in FLASH_CCR.

Note: No unlocking mechanism is required to clear an interrupt.

**End of operation event**

Setting the end of operation interrupt enable bit (EOPIE) in FLASH_CR enables the generation of an interrupt at the end of an erase operation, a program operation, or an option-byte change.

Setting CLR_EOP bit to 1 in FLASH_CCR clears EOP flag.

## 6.10 FLASH registers

Each register is assigned a offset address and a reset value. In case of registers representing option-byte value, the reset value is determined by the OBL process. In case of success, the reset value is loaded from OB. In case of OBL failure, a highly restrictive default value is set.

*Digest note:* All offsets below are relative to the FLASH register base 0x4002 2000 (CMSIS header stm32c552xx.h; the RM refers to Section 2.2). Every bit position in this section was cross-checked against the CMSIS header stm32c552xx.h; the only disagreement is FLASH_CR.PNB (see Section 6.10.7).

### 6.10.1 FLASH access control register (FLASH_ACR)

Address offset: 0x000. Reset value: 0x000X 0027. Bit 16 not reset by system reset. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. For more details, refer to Section 6.3.4 and Section 6.3.5.

- **Bits 31:17** Reserved, must be kept at reset value.
- **Bit 16 EMPTY** (rw): Main flash memory area empty (not reset by system reset). Set and reset by software. This bit indicates whether the boot location of the main flash memory area (indicated by BOOT_ADD) is erased or has a programmed value.
  - 0: Boot address in main flash memory area programmed
  - 1: Boot address in main flash memory area empty
- **Bits 15:9** Reserved, must be kept at reset value.
- **Bit 8 PRFTEN** (rw): Prefetch enable. When this bit value is modified, the user must read back this register to be sure PRFTEN has been taken into account. This bit is used to control the prefetch.
  - 0: Prefetch disabled
  - 1: Prefetch enabled when latency is at least 1 wait-state
- **Bits 7:6** Reserved, must be kept at reset value.
- **Bits 5:4 WRHIGHFREQ[1:0]** (rw): FLASH signal delay. These bits are used to control the delay between nonvolatile memory signals during programming operations. The application software has to program them to the correct value depending on the FLASH frequency. Refer to Table 20 for details.
  - Note: No check is performed to verify that the configuration is correct. Two WRHIGHFREQ values can be selected for some frequencies.
- **Bits 3:0 LATENCY[3:0]** (rw): Read latency. These bits are used to control the number of wait states used during read operations on both nonvolatile memory banks. The application software has to program them to the correct value depending on the FLASH frequency and voltage conditions.
  - 0000: 0 wait state
  - 0001: 1 wait state
  - 0010: 2 wait states
  - 0011-1111: {v} wait states [unclear in source: the RM prints a literal "{v}" placeholder]
  - Note: No check is performed by hardware to verify that the configuration is correct.

*Digest note:* According to RM0522 Chapter 4 (Table 13 note and "Empty check"), EMPTY is set during option-byte loading when the 32-bit word at BOOTADD reads 0xFFFF FFFF, and in RDP L0 with BOOT0 = 0 an EMPTY = 1 selects the system bootloader. Because EMPTY is evaluated at OBL and is not reset by system reset, a bootloader that has just programmed the vector table at BOOTADD should clear EMPTY by software (or the device should see a power-on reset) before relying on a system reset to start the application. The reset value 0x27 gives LATENCY = 7 WS and WRHIGHFREQ = 10.

### 6.10.2 FLASH key register (FLASH_KEYR)

Address offset: 0x004. Reset value: 0x0000 0000. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is write-only.

The following values must be programmed consecutively to unlock FLASH_CR and to allow programming/erasing it. A wrong sequence locks FLASH_CR until next system reset.

- 1st key = 0x4567 0123
- 2nd key = 0xCDEF 89AB

- **Bits 31:0 KEY[31:0]** (w): Nonvolatile memory configuration access unlock key

### 6.10.3 FLASH option key register (FLASH_OPTKEYR)

Address offset: 0x00C. Reset value: 0x0000 0000. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR.This register is write-only.

The following values must be programmed consecutively to unlock FLASH_OPTCR. A wrong sequence locks FLASH_OPTCR until next system reset.

- 1st key = 0x0819 2A3B
- 2nd key = 0x4C5D 6E7F

- **Bits 31:0 OPTKEY[31:0]** (w): FLASH option-byte control access unlock key

### 6.10.4 FLASH operation status register (FLASH_OPSR)

Address offset: 0x018. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR.

- **Bits 31:29 CODE_OP[2:0]** (r): Flash memory operation code
  - 000: No FLASH operation ongoing during previous reset
  - 001: Single write operation interrupted
  - 010: Reserved
  - 011: Page erase operation interrupted
  - 100: Bank erase operation interrupted
  - 101: Mass erase operation interrupted
  - 110: Option change operation interrupted
  - 111: Reserved
- **Bits 28:25** Reserved, must be kept at reset value.
- **Bit 24 OTP_OP** (r): OTP operation interrupted. This bit indicates that a reset interrupted an ongoing operation in the OTP area.
- **Bit 23** Reserved, must be kept at reset value.
- **Bit 22 BK_OP** (r): Interrupted operation bank. This bit indicates which bank was concerned by operation. (Refer to Section Table 24.: Memory map and the swapping option (STM32C53x/542 devices))
- **Bit 21 DATA_OP** (r): FLASH data area operation interrupted. This bit indicates if user data FLASH area is concerned by an operation.
- **Bits 20:16** Reserved, must be kept at reset value.
- **Bits 15:0 ADDR_OP[15:0]** (r): Interrupted operation address

*Digest note:* For STM32C551/C552 the relevant memory map for BK_OP is Table 25. See Table 27 for how to react to FLASH_OPSR contents after reset.

### 6.10.5 FLASH option control register (FLASH_OPTCR)

Address offset: 0x01C. Reset value: 0xX000 0001. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Access: No wait state when no flash memory operation is ongoing. This register is not accessible in write mode when the BSY bit is set. Any attempt to write to it while the BSY bit set causes the AHB bus to stall until the BSY bit is cleared.

- **Bit 31 SWAP_BANK** (r): Bank-swapping option configuration bit. SWAP_BANK controls whether bank1 and bank2 are swapped or not. This bit is loaded with the SWAP_BANK bit of FLASH_OPTSR_CUR register only after reset or POR.
  - 0: Bank1 and bank2 not swapped
  - 1: Bank1 and bank2 swapped
- **Bits 30:2** Reserved, must be kept at reset value.
- **Bit 1 OPTSTRT** (rw): Option-byte start change option configuration bit. OPTSTRT triggers an option byte change operation. The user can set OPTSTRT only when the OPTLOCK bit is cleared to 0. It is set only by software and cleared when the option-byte change is completed or an error occurs (PGSERR or OPTCHANGEERR). It is reset at the same time as BSY bit. The user application cannot modify any FLASH_XXX_PRG register until the option change operation has been completed. Before setting this bit, the user has to write the required values in FLASH_XXX_PRG. FLASH_XXX_PRG registers are locked until the option-byte change operation has been executed in nonvolatile memory.
- **Bit 0 OPTLOCK** (rs): FLASH_OPTCR lock option configuration bit. The OPTLOCK bit locks the FLASH_OPTCR register as well as all _PRG registers. The correct write sequence to FLASH_OPTKEYR register unlocks this bit. If a wrong sequence is executed, or the unlock sequence to FLASH_OPTKEYR is performed twice, this bit remains locked until next system reset. It is possible to set OPTLOCK by programming it to 1. When set to 1, a new unlock sequence is mandatory to unlock it. When OPTLOCK changes from 0 to 1, the others bits of FLASH_OPTCR register do not change.
  - 0: FLASH_OPTCR register unlocked
  - 1: FLASH_OPTCR register locked.

*Digest note:* No OBL_LAUNCH bit exists in this register (see the digest note in Section 6.3.5).

### 6.10.6 FLASH status register (FLASH_SR)

Address offset: 0x020. Reset value: 0x0000 000X. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bit 23 OPTCHANGEERR** (r): Option-byte change error flag. This flag indicates that an error occurred during an option-byte change operation. When This bit is set to 1, the option-byte change operation did not successfully complete. An interrupt is generated when this flag is raised if OPTCHANGEERRIE in FLASH_NSCR is set to 1. Writing 1 to CLR_OPTCHANGEERR in FLASH_CCR clears OPTCHANGEERR.
  - 0: No option-byte change errors occurred.
  - 1: One or more errors occurred during an option-byte change operation.
  - Note: OPTSTRT in FLASH_OPTCR cannot be set while OPTCHANGEERR is set.
- **Bits 22:21** Reserved, must be kept at reset value.
- **Bit 20 INCERR** (r): Inconsistency error flag. This flag is raised when an inconsistency error occurs. An interrupt is generated if INCERRIE is set to 1. Writing 1 to CLR_INCERR in FLASH_CCR clears INCERR.
  - 0: No inconsistency error occurred.
  - 1: An inconsistency error occurred.
- **Bit 19 STRBERR** (r): Strobe error flag. This flag is raised when a strobe error occurs (when the master attempts to write several times the same byte in the write buffer). An interrupt is generated if STRBERRIE is set to 1. Writing 1 to CLR_STRBERR in FLASH_CCR clears STRBERR.
  - 0: No strobe error occurred.
  - 1: A strobe error occurred.
- **Bit 18 PGSERR** (r): Programming sequence error flag. This flag is raised when a sequence error occurs. An interrupt is generated if the PGSERRIE bit is set to 1. Writing 1 to CLR_PGSERR in FLASH_CCR clears PGSERR.
  - 0: No sequence error occurred.
  - 1: A sequence error occurred.
- **Bit 17 WRPERR** (r): Write protection error flag. This flag is raised when a protection error occurs during a program operation. An interrupt is also generated if the WRPERRIE is set to 1. Writing 1 to CLR_WRPERR bit in FLASH_CCR clears WRPERR.
  - 0: No write-protection error occurred.
  - 1: A write-protection error occurred.
- **Bit 16 EOP** (r): End of operation flag. This flag is set when an operation (program/erase) completes. An interrupt is generated if EOPIE is set to 1. It is not necessary to reset EOP before starting a new operation. EOP bit is cleared by writing 1 to CLR_EOP in FLASH_CCR.
  - 0: No operation completed.
  - 1: An operation completed.
- **Bits 15:10** Reserved, must be kept at reset value.
- **Bit 9 BSLOCK** (r): BS lock. This bit indicates that the BS key read during the option byte loading is not default (default is 0xAAAA AAAA). When set, the BS personalized key mechanism to transition to L2 from L2_wBS is active.
- **Bit 8 OEMLOCK** (r): OEM lock. This bit indicates that the OEM key read during the OBL is not virgin. When set, the OEM RDP lock mechanism is active. The lock mechanism allows the user to regress from RDP L2_wBS or L2 to L0. This bit is set once a 128-bit password is written in OEMKEYRx registers and written in memory. It cannot be cleared.
  - 0: Lock mechanism is not active, progressing to RDP L2_wBS or L2 is irrevocable.
  - 1: Lock mechanism is active, a key exist to regress to RDP L0.
- **Bits 7:4** Reserved, must be kept at reset value.
- **Bit 3 DBNE** (r): Data buffer not empty flag. This flag is set when the FLASH is processing 6-bit ECC data (OTP or EDATA area when EDATA_EN option bit set) in a dedicated buffer. This bit cannot be cleared by software. The hardware resets it once the buffer is free.
  - 0: Data buffer not used
  - 1: Data buffer used, wait
- **Bit 2** Reserved, must be kept at reset value.
- **Bit 1 WBNE** (r): Write buffer not empty flag. This flag is set when the FLASH is waiting for new data to complete the write buffer. In this state, the write buffer is not empty. WBNE is reset by hardware each time the write buffer is complete or the write buffer is emptied following one of the event below:
  - The application software forces the write operation using FW bit in FLASH_CR.
  - The FLASH detects an error that involves data loss.

  This bit cannot be reset by software writing 0 directly. To reset it, clear the write buffer by performing any of the above listed actions, or send the missing data.
  - 0: Write buffer empty or full
  - 1: Write buffer waiting data to complete
- **Bit 0 BSY** (r): Busy flag. This flag indicates that a flash memory is busy by an operation (write, erase, option-byte change). It is set at the beginning of a flash memory operation, and cleared when the operation finishes or an error occurs.
  - 0: No programming, erase, or option-byte change operation being executed
  - 1: Programming, erase, or option byte change operation being executed

*Digest note:* "FLASH_NSCR" in the OPTCHANGEERR description refers to FLASH_CR (there is no FLASH_NSCR on STM32C5). The error flags are read-only in FLASH_SR and are cleared only by writing 1 to the matching FLASH_CCR bit.

### 6.10.7 FLASH control register (FLASH_CR)

Address offset: 0x028. Reset value: 0x0000 0001. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Access: No wait state when no flash memory operation is ongoing. This register is not accessible in write mode when the BSY bit is set. Any attempt to write to it with the BSY bit set causes the AHB bus to stall until the BSY bit is cleared.

- **Bit 31 BKSEL** (rw): Bank selector bit. This bit can only be programmed when LOCK is cleared to 0. This bit selects physical bank, SWAP_BANK setting is ignored.
  - 0: Bank1 is selected for bank erase (BER)/page erase (PER)/interrupt enable.
  - 1: Bank2 is selected for BER/PER.
- **Bit 30** Reserved, must be kept at reset value.
- **Bit 29 EDATASEL** (rw): EDATA erase selector bit. This bit can only be programmed when LOCK is cleared to 0. This bit selects if page erased concern EDATA page or User main flash pages. This bit has no effect if PER bit is reset.
  - 0: Main FLASH page erase
  - 1: FLASH data area EDATA page erase
  - Note: During a bank erase, the user and the EDATA sectors are always erased, regardless of this bit setting.
- **Bits 28:24** Reserved, must be kept at reset value.
- **Bit 23 OPTCHANGEERRIE** (rw): Option-byte change error interrupt enable bit. This bit controls if an interrupt has to be generated when an error occurs during an option-byte change. This bit can be programmed only when LOCK bit is cleared to 0.
  - 0: No interrupt is generated when an error occurs during an option-byte change.
  - 1: An interrupt is generated when and error occurs during an option-byte change.
- **Bits 22:21** Reserved, must be kept at reset value.
- **Bit 20 INCERRIE** (rw): Inconsistency error interrupt enable bit. When INCERRIE bit is set to 1, an interrupt is generated when an inconsistency error occurs during a write operation. INCERRIE can be programmed only when LOCK is cleared to 0.
  - 0: No interrupt generated when a inconsistency error occurs.
  - 1: Interrupt generated when a inconsistency error occurs.
- **Bit 19 STRBERRIE** (rw): Strobe error interrupt enable bit. When this bit is set to 1, an interrupt is generated when a strobe error occurs (the master programs several times the same byte in the write buffer) during a write operation. STRBERRIE can be programmed only when LOCK is cleared to 0.
  - 0: No interrupt generated when a strobe error occurs.
  - 1: Interrupt generated when strobe error occurs.
- **Bit 18 PGSERRIE** (rw): Programming sequence error interrupt enable bit. When this bit is set to 1, an interrupt is generated when a sequence error occurs during a program operation. PGSERRIE can be programmed only when LOCK is cleared to 0.
  - 0: No interrupt generated when a sequence error occurs.
  - 1: Interrupt generated when sequence error occurs.
- **Bit 17 WRPERRIE** (rw): Write protection error interrupt enable bit. When this bit is set to 1, an interrupt is generated when a protection error occurs during a program operation. WRPERRIE can be programmed only when LOCK is cleared to 0.
  - 0: No interrupt generated when a protection error occurs.
  - 1: Interrupt generated when a protection error occurs.
- **Bit 16 EOPIE** (rw): End of operation interrupt control bit. Setting this bit to 1 enables the generation of an interrupt at the end of a program or erase operation. EOPIE can be programmed only when LOCK is cleared to 0.
  - 0: No interrupt generated at the end of operation.
  - 1: Interrupt enabled when at the end of operation.
- **Bit 15 MER** (rw): Mass erase request. Setting this bit to 1 requests a mass erase operation (user flash memory only). MER can be programmed only when LOCK is cleared to 0. If BER or PER are both set, a PGSERR is raised.
  - 0: Mass erase not requested
  - 1: Mass erase requested
  - Note: An error is triggered when a mass erase is required and some pages are protected.
- **Bits 14:13** Reserved, must be kept at reset value.
- **Bits 12:6 PNB[6:0]** (rw): Page erase selection number. These bits are used to select the target page for an erase operation (they are unused otherwise). PNB can be programmed only when LOCK is cleared to 0.
  - 0x00: Page 0 selected
  - 0x01: Page 1 selected
  - 0x02-0x3F: Page {v} selected [unclear in source: the RM prints a literal "{v}" placeholder]
  - Note: Values corresponding to addresses outside the main memory are not allowed. Refer to Table 24: Memory map and the swapping option (STM32C53x/542 devices), Table 25: Memory map and the swapping option (STM32C55x/562 devices), and Table 26: Memory map and the swapping option (STM32C59x/5A3 devices)
- **Bit 5 STRT** (rs): Erase start control bit. This bit is used to start a page erase or a bank erase operation. STRT can be programmed only when LOCK is cleared to 0. This bit is reset at the end of the operation or when an error occurs. It cannot be reseted by software.
- **Bit 4 FW** (rw): Write forcing control bit. This bit forces a write operation even if the write buffer is not full. In this case, all bits not written are set to 1 by hardware. FW can be programmed only when LOCK is cleared to 0. The FLASH resets this bit when the corresponding operation has been acknowledged.
  - Note: Using a force-write operation prevents the application from updating later the missing bits with something else than 1, because it is likely that it leads to permanent ECC error.

  Write forcing is effective only if the write buffer is not empty (in particular, FW does not start several write operations when the force-write operations are performed consecutively). Since there is just one write buffer, FW can force a write in bank1 or bank2.
- **Bit 3 BER** (rw): Bank-erase request. Setting this bit to 1 requests a bank erase operation (user flash memory only). BER can be programmed only when LOCK is cleared to 0. If MER and PER are also set, a PGSERR is raised.
  - 0: Bank erase not requested
  - 1: Bank erase requested
  - Note: Write protection error is triggered when a bank erase is required and some pages are protected.
- **Bit 2 PER** (rw): Page-erase request. Setting this bit to 1 requests a sector erase. PER can be programmed only when LOCK is cleared to 0. If MER and PER are also set, a PGSERR is raised.
  - 0: Page erase not requested
  - 1: Page erase requested
- **Bit 1 PG** (rw): Programming control bit. This bit can be programmed only when LOCK is cleared to 0. It allows programming in bank1 and bank2.
  - 0: Programming disabled
  - 1: Programming enabled
- **Bit 0 LOCK** (rs): Configuration lock bit. This bit locks FLASH_CR. The correct write sequence to FLASH_KEYR unlocks this bit. If a wrong sequence is executed, or if the unlock sequence to FLASH_KEYR is performed twice, this bit remains locked until the next system reset. LOCK can be set by programming it to 1. When set to 1, a new unlock sequence is mandatory to unlock it. When LOCK changes from 0 to 1, the other bits of FLASH_CR register do not change.
  - 0: FLASH_CR unlocked
  - 1: FLASH_CR locked

*Digest note:* The CMSIS header stm32c552xx.h defines `FLASH_CR_PNB_Msk = 0x3F << 6` (0x0000 0FC0, a 6-bit field at bits 11:6), whereas the RM register diagram and Table 43 show PNB[6:0] at bits 12:6. The largest bank (STM32C59x/5A3) has 64 pages (0 to 63), which fits in 6 bits, so bit 12 is never needed for a valid page number; for STM32C551/C552 (512 KB) page numbers are 0 to 31. [unclear in source: the PNB range for an EDATA page erase (EDATASEL = 1) is not stated.] The sentence "If MER and PER are also set" under PER is printed as in the RM.

### 6.10.8 FLASH clear control register (FLASH_CCR)

Address offset: 0x030. Reset value: 0x0000 0000. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bit 23 CLR_OPTCHANGEERR** (w): OPTCHANGEERR clear bit. Setting this bit to 1 clears the corresponding flag in FLASH_SR.
- **Bits 22:21** Reserved, must be kept at reset value.
- **Bit 20 CLR_INCERR** (w): INCERR flag clear bit. Setting this bit to 1 resets to 0 INCERR flag in FLASH_SR.
- **Bit 19 CLR_STRBERR** (w): STRBERR flag clear bit. Setting this bit to 1 resets to 0 STRBERR flag in FLASH_SR.
- **Bit 18 CLR_PGSERR** (w): PGSERR flag clear bit. Setting this bit to 1 resets to 0 PGSERR flag in FLASH_SR.
- **Bit 17 CLR_WRPERR** (w): WRPERR flag clear bit. Setting this bit to 1 resets to 0 WRPERR flag in FLASH_SR.
- **Bit 16 CLR_EOP** (w): EOP flag clear bit. Setting this bit to 1 resets to 0 EOP flag in FLASH_SR.
- **Bits 15:0** Reserved, must be kept at reset value.

*Digest note:* The clear bits sit at the same bit positions as the corresponding FLASH_SR flags, so writing FLASH_CCR = 0x009F 0000 clears all six (OPTCHANGEERR, INCERR, STRBERR, PGSERR, WRPERR, EOP). No unlock is needed (Section 6.9). ECCC and ECCD are cleared in FLASH_ECCCORR / FLASH_ECCDETR instead.

### 6.10.9 FLASH privilege configuration register (FLASH_PRIVCFGR)

Address offset: 0x03C. Reset value: 0x0000 0000. This register can be read by both privileged and unprivileged access. It can only be written by privileged mode.

- **Bits 31:2** Reserved, must be kept at reset value.
- **Bit 1 PRIV** (rw): Privilege attribute
  - 0: Access to registers is always granted.
  - 1: Access to registers is denied in case of unprivileged access.
- **Bit 0** Reserved, must be kept at reset value.

### 6.10.10 FLASH HDP extension register (FLASH_HDPEXTR)

Address offset: 0x048. Reset value: 0x0000 0000. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. The register can only be modified in HDPL ≤ 2. The values in this register cannot be decremented. Attempt to write a lower value that current is ignored.

- **Bits 31:22** Reserved, must be kept at reset value.
- **Bits 21:16 HDP2_EXT[5:0]** (rw): HDP area extension in 8-Kbyte pages in bank2. Extension is added after the HDP2_END page (included).
- **Bits 15:6** Reserved, must be kept at reset value.
- **Bits 5:0 HDP1_EXT[5:0]** (rw): HDP area extension in 8-Kbyte pages in bank1. Extension is added after the HDP1_END page (included).

### 6.10.11 FLASH option status register (FLASH_OPTSR_CUR)

Address offset: 0x050. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Default value: 0x20B0 72D8 (value in case of double ECC issue during OBL). ST production value: refer to Table 28: Option-byte organization. This read-only register reflects the current values of corresponding option bits. (Register bits 0 to 31 are loaded with values from the flash memory at OBL)

- **Bit 31 SWAP_BANK** (r): Bank-swapping option status bit. SWAP_BANK reflects whether bank1 and bank2 are swapped or not. SWAP_BANK is loaded to SWAP_BANK in FLASH_OPTCR after a reset.
  - 0: Bank1 and bank2 not swapped
  - 1: Bank1 and bank2 swapped
- **Bit 30 SINGLE_BANK** (r): Dual-bank selection option status bit. For products:
  - STM32C53x/542 with 128-Kbyte user memory
  - STM32C55x/562 with 256-Kbyte user memory
  - STM32C59x/5A3 with 512-Kbyte user memory

  SINGLE_BANK reflects single or dual-bank memory selection.
  - 0: User flash is split between bank 1 and bank 2
  - 1: User flash is located in one bank
  - Note: This bit has no impact on EDATA sectors.
- **Bit 29 EDATA_EN** (r): FLASH data area enable
  - 0: No FLASH data area (EDATA pages are 128-bit writable)
  - 1: FLASH data area is enabled (EDATA pages are 16/32-bit writable)
- **Bits 28:24** Reserved, must be kept at reset value.
- **Bit 23 BOOT0** (r): Boot 0 option bit
  - 0: BOOT0 = 0
  - 1: BOOT0 = 1
- **Bit 22 BOOT_SEL** (r): Boot 0 source selection
  - 0: BOOT0 signal is defined by the BOOT0 option bit.
  - 1: BOOT0 signal is defined by BOOT0 pin value (legacy mode).
- **Bit 21 IWDG_STDBY** (r): IWDG Standby mode freeze option status bit. When this bit is set, the IWDG is frozen in system Standby mode.
  - 0: IWDG frozen in Standby mode
  - 1: IWDG keeps running in Standby mode.
- **Bit 20 IWDG_STOP** (r): IWDG Stop mode freeze option status bit. When set the independent watchdog IWDG is in system Stop mode.
  - 0: IWDG frozen in system Stop mode
  - 1: IWDG keeps running in system Stop mode.
- **Bits 19:16** Reserved, must be kept at reset value.
- **Bits 15:8 RDP_LEVEL[7:0]** (r): RDP level code (based on Hamming 8,4). See Section 6.5.8.
- **Bit 7 NRST_STDBY** (r): Core domain Standby entry reset option status bit
  - 0: A reset is generated when entering Standby mode on core domain.
  - 1: No reset generated when entering Standby mode on core domain.
- **Bit 6 NRST_STOP** (r): Core domain Stop entry reset option status bit
  - 0: A reset is generated when entering Stop mode on core domain.
  - 1: No reset generated when entering Stop mode on core domain..
- **Bit 5** Reserved, must be kept at reset value.
- **Bit 4 WWDG_SW** (r): WWDG control mode option status bit
  - 0: WWDG controlled by hardware
  - 1: WWDG controlled by software
- **Bit 3 IWDG_SW** (r): IWDG control mode option status bit
  - 0: IWDG controlled by hardware
  - 1: IWDG controlled by software
- **Bits 2:0** Reserved, must be kept at reset value.

*Digest note:* The IWDG_STDBY/IWDG_STOP sentences "When this bit is set, the IWDG is frozen" contradict their own value lists (1 = keeps running) and Section 6.4.5 (1 = counter active); the value lists and Table 28 (factory value 1 = "IWDG active in Standby and Stop modes") are consistent with each other. Decoding the OBL-failure default 0x20B0 72D8: SWAP_BANK = 0, SINGLE_BANK = 0, EDATA_EN = 1, BOOT0 = 1, BOOT_SEL = 0, IWDG_STDBY = 1, IWDG_STOP = 1, RDP_LEVEL = 0x72 (L2), NRST_STDBY = 1, NRST_STOP = 1, WWDG_SW = 1, IWDG_SW = 1.

### 6.10.12 FLASH option status register (FLASH_OPTSR_PRG)

Address offset: 0x054. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is used to program values in corresponding option bits. Values after reset reflects the current values of the corresponding option bits. (Register bits 0 to 31 are loaded with values from the flash memory at OBL)

- **Bit 31 SWAP_BANK** (rw): Bank-swapping option configuration bit. This bit is used to configure whether the bank1 and bank2 are swapped or not. This bit is loaded with SWAP_BANK in FLASH_OPTSR_CUR after a reset.
  - 0: Bank1 and bank2 not swapped
  - 1: Bank1 and bank2 swapped
- **Bit 30 SINGLE_BANK** (rw): Dual-bank option configuration bit. For products:
  - STM32C53x/542 with 128-Kbyte user memory
  - STM32C55x/562 with 256-Kbyte user memory
  - STM32C59x/5A3 with 512-Kbyte user memory

  This bit configures memory as single or dual bank. This bit is loaded with SINGLE_BANK in FLASH_OPTSR_CUR after a reset.
  - 0: User flash is split between bank 1 and bank 2
  - 1: User flash is located in one bank
- **Bit 29 EDATA_EN** (rw): FLASH data area enable
  - 0: No FLASH data area
  - 1: FLASH data area enabled
- **Bits 28:24** Reserved, must be kept at reset value.
- **Bit 23 BOOT0** (rw): Boot 0 option bit
  - 0: BOOT0 = 0
  - 1: BOOT0 = 1
- **Bit 22 BOOT_SEL** (rw): Boot 0 source configuration
  - 0: BOOT0 signal is defined by the BOOT0 option bit.
  - 1: BOOT0 signal is defined by BOOT0 pin value (legacy mode).
- **Bit 21 IWDG_STDBY** (rw): IWDG Standby mode freeze option configuration bit. When this bit is set, the IWDG is frozen in system Standby mode.
  - 0: IWDG frozen in Standby mode
  - 1: IWDG keeps running in Standby mode.
- **Bit 20 IWDG_STOP** (rw): IWDG Stop mode freeze option configuration bit. When this bit is set, the IWDG is frozen in system Stop mode.
  - 0: IWDG frozen in system Stop mode
  - 1: IWDG keeps running in system Stop mode.
- **Bits 19:16** Reserved, must be kept at reset value.
- **Bits 15:8 RDP_LEVEL[7:0]** (rw): RDP level code (based on Hamming 8,4). See Section 6.5.8.
- **Bit 7 NRST_STDBY** (rw): Core domain Standby entry reset option configuration bit
  - 0: A reset is generated when entering Standby mode on core domain.
  - 1: No reset generated when entering Standby mode on core domain.
- **Bit 6 NRST_STOP** (rw): Core domain Stop entry reset option configuration bit
  - 0: A reset is generated when entering Stop mode on core domain.
  - 1: No reset generated when entering Stop mode on core domain.
- **Bit 5** Reserved, must be kept at reset value.
- **Bit 4 WWDG_SW** (rw): WWDG control mode option configuration bit
  - 0: WWDG controlled by hardware
  - 1: WWDG controlled by software
- **Bit 3 IWDG_SW** (rw): IWDG control mode option configuration bit
  - 0: IWDG controlled by hardware
  - 1: IWDG controlled by software
- **Bits 2:0** Reserved, must be kept at reset value.

*Digest note:* Any write of a value other than 0xED, 0xD1 or 0x72 to RDP_LEVEL is an invalid value (OPTCHANGEERR, Section 6.8.6); writing 0xD1 or 0x72 is accepted from L0 and closes the device at the next reset. When changing only BOOT0/BOOT_SEL, keep RDP_LEVEL at the value read back (0xED).

### 6.10.13 FLASH option status register 2 (FLASH_OPTSR2_CUR)

Address offset: 0x070. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Default value: 0x0000 0010 (value in case of double ECC issue during OBL). ST production value: refer to Table 28: Option-byte organization. This read-only register reflects the current values of corresponding option bits. (Register bits 0 to 31 are loaded with values from the flash memory at OBL)

- **Bits 31:5** Reserved, must be kept at reset value.
- **Bit 4 SRAM2_ECC** (r): SRAM2 ECC detection and correction disable
  - 0: SRAM2 ECC check enabled
  - 1: SRAM2 ECC check disabled
- **Bits 3:2** Reserved, must be kept at reset value.
- **Bit 1 SRAM2_RST** (r): SRAM2 erase when system reset
  - 0: SRAM2 erased when a system reset occurs
  - 1: SRAM2 not erased when a system reset occurs
- **Bit 0 SRAM1_RST** (r): SRAM1 erase upon system reset
  - 0: SRAM1 erased when a system reset occurs
  - 1: SRAM1 not erased when a system reset occurs

*Digest note:* The factory value (Table 28) is SRAM1_RST = 1, SRAM2_RST = 1 (SRAMs kept across system reset) and SRAM2_ECC = 1 (SRAM2 ECC disabled). The OBL-failure default 0x0000 0010 instead erases SRAM1 and SRAM2 on every system reset, which would destroy any RAM-based handshake between application and bootloader.

### 6.10.14 FLASH option status register 2 (FLASH_OPTSR2_PRG)

Address offset: 0x074. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is used to program values in corresponding option bits. Values after reset reflects the current values of the corresponding option bits. (Register bits 0 to 31 are loaded with values from the flash memory at OBL)

- **Bits 31:5** Reserved, must be kept at reset value.
- **Bit 4 SRAM2_ECC** (rw): SRAM2 ECC detection and correction disable
  - 0: SRAM2 ECC check enabled
  - 1: SRAM2 ECC check disabled
- **Bits 3:2** Reserved, must be kept at reset value.
- **Bit 1 SRAM2_RST** (rw): SRAM2 erase when system reset
  - 0: SRAM2 erased when a system reset occurs
  - 1: SRAM2 not erased when a system reset occurs.
  - Note: SRAM erase is triggered by option-byte change operation, when enabling this feature.
- **Bit 0 SRAM1_RST** (rw): SRAM1 erase upon system reset
  - 0: SRAM1 erased when a system reset occurs
  - 1: SRAM1 not erased when a system reset occurs
  - Note: SRAM erase is triggered by option-byte change operation, when enabling this feature.

*Digest note:* Per the notes above, clearing SRAM1_RST or SRAM2_RST to 0 through an option-byte change also erases that SRAM as part of the option change itself, so code that performs this change must not depend on the contents of the affected SRAM (including its stack) surviving the operation. [unclear in source: the exact moment of that erase relative to OPTSTRT/BSY.]

### 6.10.15 FLASH unique boot entry register (FLASH_BOOTR_CUR)

Address offset: 0x080. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Default value: 0xFFFF FFB4 (value in case of double ECC issue during OBL). ST production value: refer to Table 28: Option-byte organization. This register reflects the current values of corresponding option bits. (Register bits 0 to 31 are loaded with values from the flash memory at OBL)

- **Bits 31:8 BOOTADD[23:0]** (r): Unique boot-entry address. These bits reflect the user memory boot address.
  - Caution: The BOOTADD must be a valid address within user main flash area. Otherwise, the boot stalls, and the flash memory becomes unreadable.
  - Note: The SRAM or EDATA areas cannot be selected as BOOTADD.
- **Bits 7:0 BOOT_LOCK[7:0]** (r): BOOT0, BOOT_SEL, SWAP_BANK, and BOOTADD option settings lock
  - 0xC3: BOOT0, BOOT_SEL, SWAP_BANK, and BOOTADD can still be modified following their individual rules.
  - 0xB4: BOOT0, BOOT_SEL, SWAP_BANK, and BOOTADD are frozen.

*Digest note:* BOOTADD[23:0] holds address bits [31:8] of the boot address (factory 0x080000 gives 0x0800 0000; RM0522 Chapter 4 calls it BOOTADD[31:8]), so the boot address has 256-byte granularity. The OBL-failure default 0xFFFF FFB4 is an invalid BOOTADD with BOOT_LOCK locked.

### 6.10.16 FLASH unique boot entry address (FLASH_BOOTR_PRG)

Address offset: 0x084. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is used to program values in corresponding option bits. (Register bits 0 to 31 are loaded with values from the flash memory at OBL)

- **Bits 31:8 BOOTADD[23:0]** (rw): Unique boot entry address. These bits reflect the user memory boot address.
- **Bits 7:0 BOOT_LOCK[7:0]** (rw): BOOT0, BOOT_SEL, SWAP_BANK, and BOOTADD option settings lock
  - 0xC3: BOOT0, BOOT_SEL, SWAP_BANK, and BOOTADD can still be modified following their individual rules.
  - 0xB4: BOOT0, BOOT_SEL, SWAP_BANK, and BOOTADD are frozen.

*Digest note:* Writing BOOTADD to an address outside the user main flash (for example an SRAM or EDATA address, or an address beyond the device flash size) stalls the boot and makes the flash unreadable per the Caution in Section 6.10.15; combined with BOOT_LOCK = 0xB4 or a closed RDP level this cannot be repaired from firmware. BOOTADD and BOOT_LOCK can only be changed in RDP L0 (Section 6.4.9).

### 6.10.17 FLASH OTP block lock (FLASH_OTPBLR_CUR)

Address offset: 0x090. Reset value: 0x00XX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Default value: 0xFFFF FFFF (value in case of double ECC issue during OBL). ST production value: refer to Table 28: Option-byte organization. This register reflects the current values of corresponding option bits.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bits 23:0 LOCKBL[23:0]** (r): OTP block lock. Block n corresponds to OTP 16-bit word 96 x n to 96 x n + 95. LOCKBL[n] = 1 indicates that all OTP 16-bit words in OTP block n are locked and attempt to program them results in WRPERR. LOCKBL[n] = 0 indicates that all OTP 16-bit words in OTP block n are not locked. When one block is locked, it is not possible to remove the write protection. Also if not locked, it is not possible to erase OTP words.

### 6.10.18 FLASH OTP block lock (FLASH_OTPBLR_PRG)

Address offset: 0x094. Reset value: 0x00XX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is used to program values in corresponding option bits.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bits 23:0 LOCKBL[23:0]** (rs): OTP block lock. Block n corresponds to OTP 16-bit word 96 x n to 96 x n + 95. LOCKBL[n] = 1 indicates that all OTP 16-bit words in OTP block n are locked and attempt to program them results in WRPERR. LOCKBL[n] = 0 indicates that all OTP 16-bit words in OTP block n are not locked. When one block is locked, it is not possible to remove the write protection. LOCKBL bits can be set if the corresponding bit in FLASH_OTPBLR_CUR is cleared.

### 6.10.19 FLASH bootloader interface selection (FLASH_BL_COM_CFG_CUR)

Address offset: 0x098. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Default value: 0xFFFF FFFF (value in case of double ECC issue during OBL). ST production value: refer to Table 28: Option-byte organization. This register reflects the current values of corresponding option bits.

- **Bits 31:0 BL_COM_CFG[31:0]** (r): Bootloader interface selection/configuration. This register is used to configure the set of interfaces on which the ST bootloader is active. BL_COM_CFG[n] = 1 indicates that the corresponding interface is used by the bootloader. BL_COM_CFG[n] = 0 indicates that the corresponding interface is not used by the bootloader. The GPIO remains in default state.
  - Note: For assignment of interfaces to register bits, see the bootloader documentation.

### 6.10.20 FLASH bootloader interface selection (FLASH_BL_COM_CFG_PRG)

Address offset: 0x09C. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is used to program values in the corresponding option bits.

- **Bits 31:0 BL_COM_CFG[31:0]** (rw): Bootloader interface selection/configuration. This register is used to configure the set of interfaces on which the ST bootloader is active. BL_COM_CFG[n] = 1 indicates that the corresponding interface is used by the bootloader. BL_COM_CFG[n] = 0 indicates that the corresponding interface is not used by the bootloader. The GPIO remains in default state.
  - Note: For assignment of interfaces to register bits see the bootloader documentation.

### 6.10.21 FLASH OEM key register 1 (FLASH_OEMKEYR1_PRG)

Address offset: 0xA4. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is read as zero.

- **Bits 31:0 OEMKEY[31:0]** (w): Least significants bytes of OEMKEY

### 6.10.22 FLASH OEM key register 2 (FLASH_OEMKEYR2_PRG)

Address offset: 0xAC. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is read as zero.

- **Bits 31:0 OEMKEY[63:32]** (w): Mid-least significants bytes of OEMKEY

### 6.10.23 FLASH OEM key register 3 (FLASH_OEMKEYR3_PRG)

Address offset: 0xB4. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is read as zero.

- **Bits 31:0 OEMKEY[95:64]** (w): Mid-most significants bytes of OEMKEY

### 6.10.24 FLASH OEM key register 4 (FLASH_OEMKEYR4_PRG)

Address offset: 0xBC. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is read as zero.

- **Bits 31:0 OEMKEY[127:96]** (w): Most significants bytes of OEMKEY

### 6.10.25 FLASH boundary scan key register (FLASH_BSKEYR_PRG)

Address offset: 0xC4. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is read as zero.

- **Bits 31:0 BSKEY[31:0]** (w): Boundary scan key

### 6.10.26 FLASH write page protection for bank1 (FLASH_WRP1R_CUR)

Address offset: 0x0E8. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Default value: 0x0000 0000 (value in case of double ECC issue during OBL). ST production value: refer to Table 28: Option-byte organization. This read-only register reflects the current values of corresponding option bits.

- **Bits 31:0 WRPSG1[31:0]** (r): Bank1 page protection option status byte. Each bit reflects the write protection status of the corresponding group of pages in Bank1.
  - 0: Write protected
  - 1: Not write protected
  - Note: Refer to Table 29: Write-protection management for group definition.

*Digest note:* After an option-byte ECC failure at OBL the default 0x0000 0000 write-protects every page of the bank, so all erase/program attempts fail with WRPERR.

### 6.10.27 FLASH write-page protection for bank1 (FLASH_WRP1R_PRG)

Address offset: 0x0EC. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is used to program values in corresponding option bits.

- **Bits 31:0 WRPSG1[31:0]** (rw): Bank1 page protection option status byte. Setting these bits to 0 write-protects the corresponding pages in bank 1
  - 0: Write protected
  - 1: Not write protected
  - Note: Refer to Table 29: Write-protection management for group definition.

### 6.10.28 FLASH HDP bank1 register (FLASH_HDP1R_CUR)

Address offset: 0x0F8. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is initially loaded with the values of corresponding option bits. Default value: 0x000F 0000 (value in case of double ECC issue during OBL) for STM32C53x/542. Default value: 0x001F 0000 (value in case of double ECC issue during OBL) for STM32C55x/562. Default value: 0x003F 0000 (value in case of double ECC issue during OBL) for STM32C59x/5A3. ST production value: refer to Table 28: Option-byte organization

- **Bits 31:22** Reserved, must be kept at reset value.
- **Bits 21:16 HDP1_END[5:0]** (r): HDPL barrier end set in number of 8-Kbyte pages
- **Bits 15:6** Reserved, must be kept at reset value.
- **Bits 5:0 HDP1_STRT[5:0]** (r): HDPL barrier start set in number of 8-Kbyte pages

*Digest note:* For STM32C551/C552 the OBL-failure default 0x001F 0000 is HDP1_END = 31, HDP1_STRT = 0, i.e. the whole 32-page bank becomes an HDP area once HDPL ≥ 2.

### 6.10.29 FLASH HDP bank1 register (FLASH_HDP1R_PRG)

Address offset: 0x0FC. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Register is accessible only in HDPL1. In HDPL=2 or 3 it is WI, RAZ. This register is used to program values in corresponding option bits.

- **Bits 31:22** Reserved, must be kept at reset value.
- **Bits 21:16 HDP1_END[5:0]** (rw): Bank 1 HDPL barrier end set in number of 8-Kbyte pages
- **Bits 15:6** Reserved, must be kept at reset value.
- **Bits 5:0 HDP1_STRT[5:0]** (rw): Bank 1 HDPL barrier start set in number of 8-Kbyte pages

### 6.10.30 FLASH ECC correction register (FLASH_ECCCORR)

Address offset: 0x100. Reset value: 0x0000 0000. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR.

- **Bit 31** Reserved, must be kept at reset value.
- **Bit 30 ECCC** (rw): ECC correction. Set by hardware when single ECC error has been detected and corrected. Cleared by writing 1.
- **Bits 29:26** Reserved, must be kept at reset value.
- **Bit 25 ECCCIE** (rw): ECC single-correction error interrupt enable bit. When this bit is set to 1, an interrupt is generated when an ECC single-correction error occurs during a read operation.
  - 0: No interrupt generated when an ECC single-correction error occurs.
  - 1: Interrupt generated when an ECC single-correction error occurs.
- **Bit 24 OTP_ECC** (r): OTP ECC error bit. This bit is set to 1 when one ECC single-correction occurred during the last successful read operation from the read-only/ OTP area. The address of the ECC error is available in ADDR_ECC bitfield.
- **Bit 23 SYSF_ECC** (r): ECC flag for corrected ECC error in system FLASH. This bit indicates if system flash memory is concerned by an ECC error.
- **Bit 22 BK_ECC** (r): ECC bank flag for corrected ECC error. This bit indicates which bank is concerned by an ECC error .
- **Bit 21 EDATA_ECC** (r): ECC fail for corrected ECC error in FLASH data area. This bit indicates if FLASH data area is concerned by an ECC error.
- **Bits 20:16** Reserved, must be kept at reset value.
- **Bits 15:0 ADDR_ECC[15:0]** (r): ECC error address. When an ECC error occurs (for single correction) during a read operation, this bitfield contains the address that generated the error. It is reset when the flag error is reset. The FLASH programs the address in this register only when no ECC error flags are set. This means that only the first address that generated an ECC error is saved. The address in ADDR_ECC is relative to the FLASH area where the error occurred (user flash memory, system flash memory, data area, read-only/OTP area).

*Digest note:* ECCC is shown as rw in the register diagram but behaves as write-1-to-clear per its description. When clearing ECCC with a read-modify-write, preserve ECCCIE; writing the register value back unchanged clears ECCC if it is set.

### 6.10.31 FLASH ECC detection register (FLASH_ECCDETR)

Address offset: 0x104. Reset value: 0x0000 0000. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR.

- **Bit 31 ECCD** (rc_w1): ECC detection set by hardware when two ECC errors have been detected. When this bit is set, a NMI is generated. This bit is cleared by writing 1. Needs to be cleared in order to detect subsequent double ECC errors.
- **Bits 30:25** Reserved, must be kept at reset value.
- **Bit 24 OTP_ECC** (r): OTP ECC error bit. This bit is set to 1 when a double ECC detection occurred during the last read operation from the read-only/ OTP area. The address of the ECC error is available in ADDR_ECC bitfield.
- **Bit 23 SYSF_ECC** (r): ECC fail for double ECC error in system flash memory. This bit indicates if system flash memory is concerned by an ECC error.
- **Bit 22 BK_ECC** (r): ECC fail bank for double ECC Error. This bit indicates which bank is concerned by an ECC error.
- **Bit 21 EDATA_ECC** (r): ECC fail for double ECC error in FLASH data area. This bit indicates if FLASH EDATA sector is concerned by an ECC error.
- **Bits 20:16** Reserved, must be kept at reset value.
- **Bits 15:0 ADDR_ECC[15:0]** (r): ECC error address. When an ECC error occurs (double detection) during a read operation, this bitfield contains the address that generated the error. It is reset when the flag error is reset. The FLASH programs the address in this register only when no ECC error flags are set. This means that only the first address that generated an double ECC error is saved. The address in ADDR_ECC is relative to the flash memory area where the error occurred (user flash memory, system flash memory, data area, read-only/OTP area).

### 6.10.32 FLASH ECC data (FLASH_ECCDR)

Address offset: 0x108. Reset value: 0x0000 0000. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR.

- **Bits 31:19** Reserved, must be kept at reset value.
- **Bits 18:16 DATA_ADDR_ECC[2:0]** (r): DATA ECC error address. When a double detection ECC error occurs on special areas with 6-bit ECC on 16-bit data (data area, read-only/OTP area), the position of the failing word on the FLASH line can be read to this register.
  - 000: Double error on first 16-bit data or first 32-bit data accessed on the FLASH line
  - 001: Double error on second 16-bit data accessed on the FLASH line
  - 010: Double error on third 16-bit data or second 32-bit data accessed on the FLASH line
  - 011: Double error on fourth 16-bit data accessed on the FLASH line
  - 100: Double error on fifth 16-bit data or third 32-bit data accessed on the FLASH line
  - 101: Double error on sixth 16-bit data
  - Note: If the data access was 16 bits, the corrupted word can be fully located. If access was 32 bits, use DATA_ECC value to discriminate which one of the two 16-bit word is faulty.
- **Bits 15:0 DATA_ECC[15:0]** (r): ECC error data. When a double detection ECC error occurs on special areas with 6-bit ECC on 16-bit data (data area, read-only/OTP area), the failing data is read to this register. By checking if it is possible to determine whether the failure was on a real data, or due to access to uninitialized memory.

### 6.10.33 FLASH write page protection for bank2 (FLASH_WRP2R_CUR)

Address offset: 0x1E8. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Default value: 0x0000 0000 (value in case of double ECC issue during OBL). ST production value: refer to Table 28: Option-byte organization. This read-only register reflects the current values of corresponding option bits.

- **Bits 31:0 WRPSG2[31:0]** (r): Bank2 page protection option status byte. Each bit reflects the write protection status of the corresponding group of pages in Bank2.
  - 0: Write protected
  - 1: Not write protected
  - Note: Refer to Table 29: Write-protection management group definition.

### 6.10.34 FLASH write page protection for bank2 (FLASH_WRP2R_PRG)

Address offset: 0x1EC. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. This register is used to program values in corresponding option bits.

- **Bits 31:0 WRPSG2[31:0]** (rw): Bank2 page protection option status byte. Setting WRPSG2 bits to 0 write protects the corresponding pages in bank 2
  - 0: write protected;
  - 1: not write protected
  - Note: Refer to Table 29: Write-protection management group definition.

### 6.10.35 FLASH HDP bank2 register (FLASH_HDP2R_CUR)

Address offset: 0x1F8. Reset value: 0xXXXX XXXX. This register is initially loaded with the values of corresponding option bits. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Default value: 0x000F 0000 (value in case of double ECC issue during OBL) for STM32C53x/542. Default value: 0x001F 0000 (value in case of double ECC issue during OBL) for STM32C55x/562. Default value: 0x003F 0000 (value in case of double ECC issue during OBL) for STM32C59x/5A3. ST production value: refer to Table 28: Option-byte organization

- **Bits 31:22** Reserved, must be kept at reset value.
- **Bits 21:16 HDP2_END[5:0]** (r): Bank 2 HDPL barrier end set in number of 8-Kbyte pages
- **Bits 15:6** Reserved, must be kept at reset value.
- **Bits 5:0 HDP2_STRT[5:0]** (r): Bank 2 HDPL barrier start set in number of 8-Kbyte pages

### 6.10.36 FLASH HDP bank2 register (FLASH_HDP2R_PRG)

Address offset: 0x1FC. Reset value: 0xXXXX XXXX. This register can be protected against unprivileged access when PRIV = 1 in FLASH_PRIVCFGR. Register is accessible only in HDPL0 and HDPL1. In HDPL=2 or 3 it is WI, RAZ. This register is used to program values in corresponding option bits.

- **Bits 31:22** Reserved, must be kept at reset value.
- **Bits 21:16 HDP2_END[5:0]** (rw): Bank 2 HDPL barrier end set in number of 8-Kbyte pages
- **Bits 15:6** Reserved, must be kept at reset value.
- **Bits 5:0 HDP2_STRT[5:0]** (rw): Bank 2 HDPL barrier start set in number of 8-Kbyte pages

### 6.10.37 FLASH register map

**Table 43. FLASH register map and reset values**

| Offset | Register | Reset value | Fields (bit positions) |
| --- | --- | --- | --- |
| 0x000 | FLASH_ACR | 0x000X 0027 (EMPTY = x) | EMPTY (16), PRFTEN (8), WRHIGHFREQ[1:0] (5:4), LATENCY[3:0] (3:0); others Res. |
| 0x004 | FLASH_KEYR | 0x0000 0000 | KEY[31:0] (31:0) |
| 0x008 | Reserved | - | - |
| 0x00C | FLASH_OPTKEYR | 0x0000 0000 | OPTKEY[31:0] (31:0) |
| 0x010 - 0x014 | Reserved | - | - |
| 0x018 | FLASH_OPSR | x for CODE_OP, OTP_OP, BK_OP, DATA_OP, ADDR_OP | CODE_OP[2:0] (31:29), OTP_OP (24), BK_OP (22), DATA_OP (21), ADDR_OP[15:0] (15:0); others Res. |
| 0x01C | FLASH_OPTCR | 0xX000 0001 (SWAP_BANK = x, OPTSTRT = 0, OPTLOCK = 1) | SWAP_BANK (31), OPTSTRT (1), OPTLOCK (0); others Res. |
| 0x020 | FLASH_SR | 0 for OPTCHANGEERR, INCERR, STRBERR, PGSERR, WRPERR, EOP, BSLOCK, OEMLOCK; x for DBNE, WBNE, BSY | OPTCHANGEERR (23), INCERR (20), STRBERR (19), PGSERR (18), WRPERR (17), EOP (16), BSLOCK (9), OEMLOCK (8), DBNE (3), WBNE (1), BSY (0); others Res. |
| 0x024 | Reserved | - | - |
| 0x028 | FLASH_CR | 0x0000 0001 | BKSEL (31), EDATASEL (29), OPTCHANGEERRIE (23), INCERRIE (20), STRBERRIE (19), PGSERRIE (18), WRPERRIE (17), EOPIE (16), MER (15), PNB[6:0] (12:6), STRT (5), FW (4), BER (3), PER (2), PG (1), LOCK (0); others Res. |
| 0x02C | Reserved | - | - |
| 0x030 | FLASH_CCR | 0x0000 0000 | CLR_OPTCHANGEERR (23), CLR_INCERR (20), CLR_STRBERR (19), CLR_PGSERR (18), CLR_WRPERR (17), CLR_EOP (16); others Res. |
| 0x034 - 0x038 | Reserved | - | - |
| 0x03C | FLASH_PRIVCFGR | 0x0000 0000 | PRIV (1); others Res. |
| 0x040 - 0x044 | Reserved | - | - |
| 0x048 | FLASH_HDPEXTR | 0x0000 0000 | HDP2_EXT[5:0] (21:16), HDP1_EXT[5:0] (5:0); others Res. |
| 0x04C | Reserved | - | - |
| 0x050 | FLASH_OPTSR_CUR | x for all defined bits | SWAP_BANK (31), SINGLE_BANK (30), EDATA_EN (29), BOOT0 (23), BOOT_SEL (22), IWDG_STDBY (21), IWDG_STOP (20), RDP_LEVEL[7:0] (15:8), NRST_STDBY (7), NRST_STOP (6), WWDG_SW (4), IWDG_SW (3); others Res. |
| 0x054 | FLASH_OPTSR_PRG | x for all defined bits | SWAP_BANK (31), SINGLE_BANK (30), EDATA_EN (29), BOOT0 (23), BOOT_SEL (22), IWDG_STDBY (21), IWDG_STOP (20), RDP_LEVEL[7:0] (15:8), NRST_STDBY (7), NRST_STOP (6), WWDG_SW (4), IWDG_SW (3); others Res. |
| 0x058 - 0x06C | Reserved | - | - |
| 0x070 | FLASH_OPTSR2_CUR | x for all defined bits | SRAM2_ECC (4), SRAM2_RST (1), SRAM1_RST (0); others Res. |
| 0x074 | FLASH_OPTSR2_PRG | x for all defined bits | SRAM2_ECC (4), SRAM2_RST (1), SRAM1_RST (0); others Res. |
| 0x078 - 0x07C | Reserved | - | - |
| 0x080 | FLASH_BOOTR_CUR | 0xXXXX XXXX | BOOTADD[23:0] (31:8), BOOT_LOCK[7:0] (7:0) |
| 0x084 | FLASH_BOOTR_PRG | 0xXXXX XXXX | BOOTADD[23:0] (31:8), BOOT_LOCK[7:0] (7:0) |
| 0x088 - 0x08C | Reserved | - | - |
| 0x090 | FLASH_OTPBLR_CUR | x for LOCKBL | LOCKBL[23:0] (23:0); 31:24 Res. |
| 0x094 | FLASH_OTPBLR_PRG | x for LOCKBL | LOCKBL[23:0] (23:0); 31:24 Res. |
| 0x098 | FLASH_BL_COM_CFG_CUR | 0xXXXX XXXX | BL_COM_CFG[31:0] (31:0) |
| 0x09C | FLASH_BL_COM_CFG_PRG | 0xXXXX XXXX | BL_COM_CFG[31:0] (31:0) |
| 0x0A0 | Reserved | - | - |
| 0x0A4 | FLASH_OEMKEYR1_PRG | 0xXXXX XXXX | OEMKEY[31:0] (31:0) |
| 0x0A8 | Reserved | - | - |
| 0x0AC | FLASH_OEMKEYR2_PRG | 0xXXXX XXXX | OEMKEY[31:0] (31:0) |
| 0x0B0 | Reserved | - | - |
| 0x0B4 | FLASH_OEMKEYR3_PRG | 0xXXXX XXXX | OEMKEY[31:0] (31:0) |
| 0x0B8 | Reserved | - | - |
| 0x0BC | FLASH_OEMKEYR4_PRG | 0xXXXX XXXX | OEMKEY[31:0] (31:0) |
| 0x0C0 | Reserved | - | - |
| 0x0C4 | FLASH_BSKEYR_PRG | 0xXXXX XXXX | BSKEY[31:0] (31:0) |
| 0x0C8 - 0x0E4 | Reserved | - | - |
| 0x0E8 | FLASH_WRP1R_CUR | 0xXXXX XXXX | WRPSG1[31:0] (31:0) |
| 0x0EC | FLASH_WRP1R_PRG | 0xXXXX XXXX | WRPSG1[31:0] (31:0) |
| 0x0F0 - 0x0F4 | Reserved | - | - |
| 0x0F8 | FLASH_HDP1R_CUR | x for HDP1_END, HDP1_STRT | HDP1_END[5:0] (21:16), HDP1_STRT[5:0] (5:0); others Res. |
| 0x0FC | FLASH_HDP1R_PRG | x for HDP1_END, HDP1_STRT | HDP1_END[5:0] (21:16), HDP1_STRT[5:0] (5:0); others Res. |
| 0x100 | FLASH_ECCCORR | 0x0000 0000 | ECCC (30), ECCCIE (25), OTP_ECC (24), SYSF_ECC (23), BK_ECC (22), EDATA_ECC (21), ADDR_ECC[15:0] (15:0); others Res. |
| 0x104 | FLASH_ECCDETR | 0x0000 0000 | ECCD (31), OTP_ECC (24), SYSF_ECC (23), BK_ECC (22), EDATA_ECC (21), ADDR_ECC[15:0] (15:0); others Res. |
| 0x108 | FLASH_ECCDR | 0x0000 0000 | DATA_ADDR_ECC[2:0] (18:16), DATA_ECC[15:0] (15:0); others Res. |
| 0x10C - 0x1E4 | Reserved | - | - |
| 0x1E8 | FLASH_WRP2R_CUR | 0xXXXX XXXX | WRPSG2[31:0] (31:0) |
| 0x1EC | FLASH_WRP2R_PRG | 0xXXXX XXXX | WRPSG2[31:0] (31:0) |
| 0x1F0 - 0x1F4 | Reserved | - | - |
| 0x1F8 | FLASH_HDP2R_CUR | x for HDP2_END, HDP2_STRT | HDP2_END[5:0] (21:16), HDP2_STRT[5:0] (5:0); others Res. |
| 0x1FC | FLASH_HDP2R_PRG | x for HDP2_END, HDP2_STRT | HDP2_END[5:0] (21:16), HDP2_STRT[5:0] (5:0); others Res. |

Refer to Section 2.2: Memory organization for the register boundary addresses.

*Digest note:* Table 43 labels the field of FLASH_OEMKEYR2_PRG to FLASH_OEMKEYR4_PRG as "OEMKEY[31:0]"; the register descriptions (Sections 6.10.22 to 6.10.24) name them OEMKEY[63:32], OEMKEY[95:64] and OEMKEY[127:96]. The CMSIS header register layout (FLASH_TypeDef) matches every offset in this table.
