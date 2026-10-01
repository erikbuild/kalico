# RM0522 Chapter 4: Boot modes

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 112–113.

At startup, the BOOT0 pin or option bit (based on the value of the BOOT_SEL option bit) and BOOTADD[31:8] option bytes are used to select the boot memory address that includes:

- Boot from any address in user flash memory, excluding EDATA sectors.
- Boot from system memory
  - Bootloader

When boot from user flash is selected, the boot address is defined by BOOTADD. This address can be locked thanks to BOOT_LOCK.

### Embedded bootloader

The embedded bootloader is located in the system memory and is programmed by ST during production. It is used to reprogram the flash memory using USART, SPI, FDCAN, or USB in device mode through the DFU (device firmware upgrade).

Refer to the application note STM32 microcontroller system memory boot mode (AN2606).

*Digest note:* FDCAN is present only on STM32C552 (absent on STM32C551), so the FDCAN bootloader interface cannot apply to C551. The system memory is at 0x0BF8 0000 - 0x0BF8 FFFF (Chapter 2, Figures 2 to 4).

## 4.1 STM32C5 boot modes

The following table provides the details of the boot mode for the STM32C5 devices.

**Table 13. STM32C5 boot modes**

| RDP_LEVEL | BOOT_SEL option bit | BOOT0 option bit | BOOT0 pin | EMPTY flag value(1) | Boot area |
|---|---|---|---|---|---|
| Level 0 | 1 | x | 0 | x | Boot address defined by user option byte BOOTADD[31:8] |
| Level 0 | 1 | x | 1 | x | Bootloader |
| Level 0 | 0 | 0 | x | 0 | Boot address defined by user option byte BOOTADD[31:8] |
| Level 0 | 0 | 0 | x | 1 | Bootloader |
| Level 0 | 0 | 1 | x | x | Bootloader |
| Level 2 with boundary scan and level 2 | x | x | x | x | Boot address defined by user option byte BOOTADD[31:8] |

Notes:

1. The boot address, defined by BOOTADD option byte, is considered empty only if the FLASH word is equal to 0xFFFF FFFF. In this case, at option byte loading, the EMPTY bit is set in FLASH_ACR.

*Digest note:* In the source, the "x" in the EMPTY column of the two BOOT_SEL = 1 rows and the "x" in the BOOT0 pin column of the three BOOT_SEL = 0 rows are merged cells; they are repeated per row here.

### Empty check

During the option byte loading phase, after loading all options, the flash memory interface checks whether the boot location in the main memory, indicated by BOOTADD[31:8], is programmed. The result of this check, with the boot0 information, is used to determine where the system should boot from. It prevents the system from booting from the main flash memory area when, for instance, no user code has been programmed.

The main flash memory empty check status can be read from the EMPTY bit in the FLASH access control register (FLASH_ACR). Software can modify it by writing an appropriate value to the EMPTY bit.

The BOOT_LOCK, which locks modifications of option bytes involved in BOOT selection, has no impact on this empty check mechanism

### Embedded bootloader

The embedded bootloader is located in the system memory, programmed by ST during production. It is used to reprogram the flash memory by using USART, SPI, FDCAN, or USB in device mode through the DFU (device firmware upgrade).

For further information, refer to the application note STM32 microcontroller system memory boot mode (AN2606).

*Digest note:* Option-bit locations and factory values, taken from RM Section 6 (outside this page range; Table 28 "Option-byte organization", Section 6.4.8 and Section 6.10 register descriptions) and cross-checked with the ST CMSIS header stm32c552xx.h:

- BOOT_SEL = FLASH_OPTSR bit 22 (0: BOOT0 signal is defined by the BOOT0 option bit; 1: BOOT0 signal is defined by BOOT0 pin value, "legacy mode"). Factory value 0.
- BOOT0 (option bit) = FLASH_OPTSR bit 23. Factory value 0.
- BOOTADD = FLASH_BOOTR bits 31:8 (the header names the field BOOTADD with mask 0xFFFFFF00, i.e. a 256-byte-aligned address). Factory value 0x0800 0000. Section 6 adds that the SRAM or EDATA areas cannot be selected as BOOTADD.
- BOOT_LOCK[7:0] = FLASH_BOOTR bits 7:0. 0xC3 (factory): BOOT0, BOOT_SEL, SWAP_BANK and BOOTADD can still be modified; 0xB4: they are frozen.
- EMPTY = FLASH_ACR bit 16 ("not reset by system reset"; 0: boot address in main flash programmed, 1: boot address empty).
- RDP_LEVEL = FLASH_OPTSR bits 15:8; factory value 0xED (L0).

Consequence of the factory defaults (BOOT_SEL = 0, BOOT0 option bit = 0): the BOOT0 pin is ignored. The device boots from BOOTADD (0x0800 0000) when the first flash word there is programmed, and from the bootloader only when that word reads 0xFFFF FFFF (EMPTY = 1). To get the familiar "hold BOOT0 high to enter the ROM bootloader" behavior, BOOT_SEL must be programmed to 1. In RDP L2_wBS or L2 the bootloader can never be selected.
