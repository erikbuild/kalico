# RM0522 Chapter 50: Device electronic signature

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 2558–2560.

The device electronic signature is stored in the read only (RO) area of the flash memory module and can be read using the debug interface or by the CPU. It contains factory-programmed identification and calibration data that allow the user firmware or other external devices to automatically match to the characteristics of the devices.

*Digest note:* Access-width restriction (from RM0522 Section 6.3.4, FLASH read operations, page 131, not part of this chapter): read access to the OTP, RO and user data flash areas reads a 137-bit FLASH data word into a temporary buffer and selects the 16- or 32-bit data requested, adding two wait states while the AHB bus is stalled; reading the same address twice triggers two flash reads; "For 8-bit accesses, an AHB bus error is generated." The RO area is protected by a 6-bit ECC per 16-bit data (Section 6.3.8). Therefore the unique ID, flash size and package registers must be read with 16-bit or 32-bit loads only; byte-wise reads (for example a byte-wise memcpy of the 96-bit UID) fault.

*Digest note:* RM0522 Section 6.3.9 (page 141) gives the RO area range as 0x08FF F800 to 0x08FF FDFF (1.5 Kbytes) and lists the public RO data in Table 23 (Read-only public data organization):

| Read-only data name | Address | Comment |
|---|---|---|
| Unique device ID | 0x08FF F800 | U_ID[31:0] |
| Unique device ID | 0x08FF F804 | U_ID[63:32] |
| Unique device ID | 0x08FF F808 | U_ID[96:64] |
| Flash memory size/package | 0x08FF F80C | Flash memory size[15:0] \|\| Package code[15:0] |
| Factory calibration | 0x08FF F810 | Vrefint calibration value[31:0] |
| Factory calibration | 0x08FF F814 | TS_CAL1[31:0] |
| Factory calibration | 0x08FF F818 | TS_CAL2[31:0] |
| Reserved | 0x08FF F81C to 0x08FF FDFF | Reserved information |

Per this chapter, the flash size is the half-word at 0x08FF F80C and the package code the half-word at 0x08FF F80E, so a 32-bit read at 0x08FF F80C returns the flash size in bits 15:0 and the package code in bits 31:16 (little-endian).

## 50.1 Unique device ID register (96 bits)

The unique device identifier is ideally suited for:

- Use as serial numbers (for example, USB string serial numbers or other end applications)
- Use as part of the security keys to increase the security of code in flash memory by using and combining this unique ID with software cryptographic primitives and protocols before programming the internal flash memory
- Activating secure boot processes

The 96-bit unique device identifier provides a reference number, which is unique for any device and in any context. These bits cannot be altered by the user.

Base address: 0x08FF F800

Address offset: 0x00. Read only = 0xXXXX XXXX where X is factory-programmed.

- **Bits 31:0 UID[31:0]** (r): X and Y coordinates on the wafer

Address offset: 0x04. Read only = 0xXXXX XXXX where X is factory-programmed.

- **Bits 31:8 UID[63:40]** (r): LOT_NUM[23:0]
  Lot number (ASCII encoded)
- **Bits 7:0 UID[39:32]** (r): WAF_NUM[7:0]
  Wafer number (8-bit unsigned number)

Address offset: 0x08. Read only = 0xXXXX XXXX where X is factory-programmed.

- **Bits 31:0 UID[95:64]** (r): LOT_NUM[55:24]
  Lot number (ASCII encoded)

*Digest note:* The RM gives these three words no register names. The CMSIS header stm32c552xx.h defines `UID_BASE` = 0x08FFF800. Absolute addresses: UID[31:0] at 0x08FF F800, UID[63:32] at 0x08FF F804, UID[95:64] at 0x08FF F808. Section 6.3.9 Table 23 labels the last word "U_ID[96:64]"; this chapter's bit numbering (UID[95:64]) is kept.

## 50.2 Flash size data register

Base address: 0x08FF F80C

Address offset: 0x00. Read only = 0xXXXX where X is factory-programmed. 16-bit register.

- **Bits 15:0 FLASH_SIZE[15:0]** (r): Flash memory size
  This field indicates the size of the device Flash memory expressed in Kbytes. As an example, 0x200 corresponds to 512 Kbytes.

*Digest note:* The CMSIS header defines `FLASHSIZE_BASE` = 0x08FFF80C and reads it as a `uint16_t`; its `FLASH_SIZE` macro substitutes `FLASH_SIZE_MAX` when the half-word reads 0xFFFF or 0x0000, otherwise it returns the value shifted left by 10 (bytes). The STM32C55xxx datasheet gives up to 512 Kbytes of flash memory.

## 50.3 Package data register

Base address: 0x08FF F80E

Address offset: 0x00. Read only = 0xXXXX where X is factory-programmed. 16-bit register.

- **Bits 15:5** Reserved, must be kept at reset value.
- **Bits 4:0 PKG[4:0]** (r): Package type
  - 00000: LQFP64
  - 00010: LQFP100
  - 00100: LQFP144
  - 00101: LQFP48
  - 01001: UFQFPN32
  - 10000: UFQFPN48
  - 10010: LQFP80
  - 10110: LQFP32
  - 11000: TSSOP20
  - 11001: QFN20
  - 11010: QFN24
  - Others: reserved

  Note: Refer to the product datasheet for availability of packages on a specific device.

*Digest note:* The CMSIS header defines `PACKAGE_BASE` = 0x08FFF80E. STM32C551/C552 are offered in LQFP32, UFQFPN32, LQFP48, UFQFPN48, LQFP64, LQFP80 and LQFP100 (STM32C55xxx datasheet digest); the LQFP144, TSSOP20, QFN20 and QFN24 codes do not apply to them.
