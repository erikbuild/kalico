# RM0522 Chapter 3: System security

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 99–111.

The STM32C5 is designed with a comprehensive set of security features.

These security features simplify the process of evaluating IoT devices against security standards. They also significantly reduce the cost and complexity of software development for OEM and third-party developers, by facilitating the reuse, improving the interoperability, and minimizing the API fragmentation.

This section explains the different security features available on the STM32C5 devices.

## 3.1 Key security features

- Resource isolation using privilege mode of Cortex-M33
- Temporal isolation: boot levels are isolated thanks to the HDPL (hide protect level) monotonic counter
- General purpose cryptographic acceleration
  - AES 256-bit engine, supporting ECB, CBC, CTR, GCM, and CCM chaining modes
  - Secure AES 256-bit security coprocessor, supporting ECB, CBC, CTR, GCM, and CCM chaining modes with side-channel counter-measures and mitigations on STM32C59x and STM32C5Ax.
  - HASH processor, supporting SHA-1 checksums and SHA-2 secure hash (SHA2-224, SHA2-256) for STM32C53x/C54x/C55x/C56x, and SHA2-384, SHA2-512 in addition for STM32C59x/C5Ax.
  - Public key accelerator (PKA) for RSA/DH (up to 4096 bits) and ECC (up to 640 bits), implementing side-channel counter measures and mitigations when manipulating secrets on STM32C59x/C5Ax.
  - True random number generator (RNG), NIST SP800-90B pre-certified
  - Coupling and chaining bridge (CCB) for special coupling and chaining operations (involving PKA, SAES, and RNG peripherals) to protect private keys used in PKA-protected operations on STM32C59x/C5Ax.
- Secure storage, featuring:
  - Nonvolatile on-chip secure storage, protected with HDP areas
  - Battery-powered volatile secure storage, automatically erased in case of tamper
  - Write-only key registers in the AES engines
  - On-chip enhance storage technology, using hardware secret nonvolatile derived hardware unique keys (DHUK), and application-defined volatile boot hardware key (BHK), both loadable by hardware to the DPA-resistant SAES engine
- Device 96-bit unique ID
- Readout protection-based life cycle scheme
  - Debug protection, depending on the RDP level
  - Password-based RDP level regressions
- Tamper and protection against frequency attacks

*Digest note:* On STM32C551/C552 the crypto set is HASH (SHA-1, SHA-224, SHA-256, HMAC) and RNG only. SAES, PKA, CCB, DHUK/BHK secure storage are STM32C59x/C5Ax-only, and the C55xxx datasheet and the C551/C552 CMSIS headers do not list the AES engine (see the Chapter 2 Table 3 digest note).

## 3.2 Resource isolation

### 3.2.1 Temporal isolation using secure hide protection (HDP)

The embedded flash memory allows an HDP (high-density protection) area to be defined for each watermarked-secure area of each bank, with a granularity of 8-Kbyte sectors.

The code executed in this HDP area, with its related data and keys, can be hidden after boot until the next system reset.

The following figure shows the hidden protection principle.

**Figure 5. Flash memory HDP area** (ST drawing MSv76146V1)

The figure shows the same user flash memory in three successive states, left to right. In each, the flash is stacked (bottom to top) as: an "HDP" region, an "HDPExt" region above it, and "User applications" at the top.

1. "Execute after reset": the bottom HDP region holds the "OEM immutable Root of Trust (RoT) code and data (HDP)"; the HDPExt region holds "User application or updatable RoT"; above is "User applications". Execution starts in the HDP region.
2. "Jump to 2nd HDP Level (uRoT) or to 3rd HDP Level (user application, no uRoT) and hide area": the HDP region is now "Hidden" (marked with a no-access symbol); the HDPExt region ("User application or updatable RoT") is executing; above is "User applications".
3. "Jump to 3rd HDP Level and uRoT hide area": both the HDP and HDPExt regions are now a single "Hidden" area (no-access symbol); only "User applications" remains accessible and executing.

The activation of the HDP area in the user flash memory is related to HDPL1. It means that as soon as HDPL becomes equal or greater than 2, data read, write, and instruction fetch on the area defined by HDPx_PSTRT and HDPx_PEND in FLASH_HDPxR_PRG option bytes are denied until the next device reset.

The END of the HDPx areas can be extended dynamically by the application using the FLASH_HDPEXTR register. This extension prevents access to protected sectors under HDPL3.

Note: Bank erase aborts when it contains a write-protected area (WRP or HDP area).

### 3.2.2 Resource isolation using Cortex privileged mode

The hardware and software resources of STM32C5 devices can be partitioned to restrict access to software running in Cortex privileged mode.

Thanks to this hardware isolation technology, a critical code or data can be protected against intentional or unintentional tampering from the more exposed unprivileged code.

#### Memory and peripheral privileged allocation using MPU

The Cortex-M33 MPU divides the unified memory into eight regions, each aligned to a multiple of 32 bytes. Each memory region can be programmed to generate faults when accessed inappropriately by unprivileged software.

## 3.3 Secure execution

Through a mix of special software and hardware features, the devices ensure the correct operation of their functions against abnormal situations caused by programmer errors, software attacks through network access or local attempt for tampering code execution.

This section describes the hardware features specifically designed for secure execution.

### 3.3.1 Memory protection unit (MPU)

The Cortex-M33 includes a memory protection unit (MPU) that can restrict the read and write accesses to memory regions (including regions mapped to peripherals), based on one or more of the following parameters:

- Cortex-M33 operating mode (privileged, unprivileged)
- Data/instruction fetch

The memory map and the programming of the MPU split memory into up to eight regions.

### 3.3.2 Embedded flash memory write protection

The write protection (WRP) prevents illegal or unwanted write/erase to selected sectors of the embedded flash memory user area (system area is permanently write protected).

Write-protected sectors can be modified through option byte changes only when RDP_LEVEL = L0.

Note: Bank erase aborts when it contains a write-protected area (WRP or HDP area). For more information, see Section 6.5.5: Write protection.

### 3.3.3 Tamper detection and response

#### Principle

The devices include protection of critical security assets against attacks, with the following features:

- Erase of device secrets upon tamper detection
- Improved guarantee of safe execution for the CPU and its associated security peripherals, including:
  - Out-of-range clocking (LSE) detection
  - Security watchdog IWDG clocked by the internal oscillator LSI
  - Possible selection of internal oscillator HSI as system clock

See Section 40: Tamper and backup registers (TAMP), for more details.

#### Tamper detection sources

The devices support three input tampers that can be mapped on five different pins.

Detection time is programmable, and a digital filtering is available (tamper triggered after two false comparisons in four consecutive comparison samples).

Note: Timestamps are automatically generated when a tamper event occurs.

*Digest note:* The C55xxx datasheet lists 2 tamper pins on 32-pin packages and 3 on the larger packages.

The internal tamper sources are listed in the table below.

**Table 5. Internal tampers in TAMP**

| Tamper input | Tamper source |
|---|---|
| itamp3 | LSE monitoring(1) |
| itamp4 | HSE monitoring |
| itamp5 | RTC calendar overflow (rtc_calovf) |
| itamp6 | JTAG/SWD access |
| itamp9 | Fault generation for cryptographic peripherals (SAES, PKA, AES, RNG)(2) |
| itamp11 | IWDG timeout and potential tamper (IWDG reset when at least one enabled tamper flag is set) |

Notes:

1. LSE missing or over frequency detection (> 2 MHz), glitch filter (> 2 MHz).
2. Only RNG fault on STM32C53x/C54x/C55x/C56x.

#### Response to tampers

Each source of tamper in the device can be configured to trigger the following events:

- Generate an interrupt, capable of waking up the device from Stop and Standby modes (see TAMPxMSK bits in TAMP_CR2 register).
- Generate a hardware trigger for the low-power timers.
- Erase device secrets if the corresponding TAMPxPOM bit is cleared in TAMP_CR2 (for tamper pins) or TAMP_CR3 (for internal tamper). These erasable secrets are:
  - Symmetric keys stored in backup registers (x32), and in HASH
  - Other secrets stored in SRAM2 and CPU instruction cache memory

Read/write accesses by software to all these secrets can be blocked, by setting the BKBLOCK bit in TAMP_CR2. The device secrets access is possible only when BKBLOCK is cleared, and no tamper flag is set for any enabled tamper source.

Note: Device secret erase is also triggered by setting the BKERASE bit in TAMP_CR2, or by performing a RDP_LEVEL regression as defined in Section 3.7.1.

Device secrets are not reset by system reset or when the device wakes up from Standby mode.

*Digest note:* SRAM2 is one of the "device secrets". For a firmware that keeps a value in the top of RAM across a reset (on STM32C551/C552 the top of RAM, 0x2001 FFFF and below, is SRAM2), any enabled tamper event, a BKERASE write, or an RDP regression erases it, and a pending tamper flag makes SRAM2 read-as-zero (see "Software filtering mechanism" and Table 12).

#### Software filtering mechanism

Each tamper source can be configured not to launch an immediate erase, by setting the corresponding TAMPxPOM bit in TAMP_CR2 (for external tamper pin) or TAMP_CR3 (for internal tamper).

In such a situation, when the tamper flag is raised, access to below secrets is blocked until all tamper flags are cleared:

- Backup registers, SRAM2: read-as-zero, write-ignored
- AES, SAES, CCB, HASH, PKA peripherals : automatically reset by RCC
- The CPU instruction cache (ICACHE) is erased

Once the application, notified by the tamper event, analyzes the situation, there are two possible cases:

- The application launches secrets erase with a software command (confirmed tamper).
- The application clears the flags to release the blocking of secrets (false tamper).

Note: If the tamper software fails to react to such a tamper flag, the tamper input associated to IWDG reset must trigger automatically the erase of secrets.

#### Tamper detection and low-power modes

The effect of low-power modes on a tamper detection is summarized in the following table.

**Table 6. Effect of low-power modes on TAMP**

| Mode | Description |
|---|---|
| Sleep | No effect on tamper detection features. TAMP interrupts cause the device to exit the Sleep mode. |
| Stop | No effect on tamper detection features, except for level detection with filtering that remain active only when the clock source is LSE or LSI. Tamper events cause the device to exit the Stop mode. |
| Standby | No effect on tamper detection features, except for level detection with filtering that remain active only when the clock source is LSE or LSI. Tamper events cause the device to exit the Standby mode. |

## 3.4 Secure storage

This section applies only to STM32C59xx and STM32C5Axx devices.

*Digest note:* Not applicable to STM32C551/C552.

A critical feature of security systems is how long-term keys are stored, protected, and provisioned. Such keys are typically used for loading a boot image or handling critical user data.

Figure 6 shows how the key management service application can use the AES engine, for example, to compute external image decryption keys. Nonvolatile keys are stored in the flash memory in a dedicated area with access control (Section 3.2.1: Temporal isolation using secure hide protection (HDP)), while volatile key storage consists of tamper-protected SRAM.

Figure 6 also shows keys that are manipulated by software, or keys that are managed only by hardware (such as DHUK). More information about those hardware keys can be found in Section 3.4.1: Hardware secret key management.

**Figure 6. Key management principle** (ST drawing MSv76145V1)

A box labelled "Secure AES" contains three blocks: "Hardware key derivation" (with an input labelled "Peripheral usage" from above), "Derived hardware unique key", and "AES with DPA". "Embedded non-volatile storage (software secret)" (outside the box) feeds "Hardware key derivation" by hardware transfer; "Hardware key derivation" feeds "Derived hardware unique key" by hardware transfer; "Derived hardware unique key" feeds "AES with DPA" by a hardware transfer labelled "Hardware key". "Embedded volatile storage (tamper resistant)" (outside the box) also feeds "AES with DPA" by a hardware transfer labelled "Hardware key". "AES with DPA" feeds "AES without DPA" (outside the box) by a hardware transfer labelled "Hw Key". "AES without DPA" additionally receives software key transfers ("key") from "Embedded volatile storage (tamper resistant)" and from "Embedded non-volatile storage". The legend distinguishes solid arrows (hardware transfer of key) from dashed arrows (software transfer of key).

### 3.4.1 Hardware secret key management

As shown in the previous figure, the devices provide better protection for application keys by using hardware secret keys. This AES key can be made usable by the application, without exposing it in clear text (unencrypted). Such keys also become immediately unusable in case of tampering.

STM32C59xx/C5Axx devices embed a unique source of hardware secret key:

- DHUK: derived keys based on a 256-bit nonvolatile device-unique secret in flash memory. The flash memory provides a value provisioned during product manufacturing (called RHUK). The generation of DHUK key considers the NEXT-HDPL (temporal isolation counter) and key use state (KMOD).
- BHK: 256-bit application key stored in tamper-resistant volatile storage in TAMP. This key is written at boot time, then read/write locked to application until next reset.
- XORK: result of an XOR of BHK and DHUK

These keys can be used in the following modes:

- As a normal key, loaded into write-only key registers (software key mode).
- As an encryption/decryption key for another key, used in the DPA-resistant SAES (wrapped key mode).
- As an encryption or decryption key for another key, used in a faster AES engine (shared key mode)

## 3.5 Unique ID

The devices store a 96-bit ID that is unique to each device (see Section 50.1: Unique device ID register (96 bits)).

Application services can use this unique identity key to identify the product in the cloud network, or make it difficult for counterfeit devices or clones to inject untrusted data into the network.

Alternatively, the 256-bit device unique key (DHUK) can be used (Section 3.4.1: Hardware secret key management).

*Digest note:* The ST CMSIS header (stm32c552xx.h) defines UID_BASE at 0x08FF F800 (in the flash "RO" area). DHUK is not available on STM32C551/C552 (Section 3.4).

## 3.6 Crypto engines

Refer to the product datasheet to identify the cryptographic engines embedded in the selected devices.

The devices implement advanced cryptographic algorithms featuring key sizes and computing protection as recommended by national security agencies such as NIST for the United States, BSI for Germany, and ANSSI for France. These algorithms support privacy, authentication, integrity, entropy, and identity attestation.

The cryptographic engines embedded in STM32 reduce the weaknesses in the implementation of critical cryptographic functions. They prevent the use of weak cryptographic algorithms and key sizes. They enable lower processing times, and lower power consumption during cryptographic operations. These engines offload computations from Cortex-M33, particularly true for asymmetric cryptography.

For product certification purposes, ST can provide certified device information detailing how these security functions are implemented and validated.

For more information about cryptographic engine processing times, refer to their respective sections in the reference manual.

### 3.6.1 Cryptographic engines features

Figure 7 lists the accelerated cryptographic operations available in the devices. Two AES accelerators are supported.

Note: Additional operations can be added by using the firmware.

The PKA can accelerate asymmetric cryptographic operations (such as key pair generation, ECC scalar multiplication, point on curve check). See Section 30: Public key accelerator (PKA) for more details.

*Digest note:* The text says "Figure 7"; the list is Table 7 below.

**Table 7. Accelerated cryptographic operations**

| Operations | Algorithm | Specification | Key lengths (in bit) | Modes |
|---|---|---|---|---|
| Get entropy | RNG | NIST SP800-90B(1) | N/A | Software and hardware(2) modes running in parallel |
| Encryption, decryption | AES(3) | FIPS PUB 197 NIST SP800-38A | 128, 256 | ECB, CBC, CTR |
| Authenticated encryption or decryption | AES(3) | NIST SP800-38C NIST SP800-38D | 128, 256 | GCM, CCM |
| Cipher-based message authentication code | AES(3) | NIST SP800-38D | 128, 256 | GMAC |
| Checksum | SHA-1 | FIPS PUB 180-4 | N/A | Digest 160-bit |
| Cryptographic hash | SHA-2 | FIPS PUB 180-4 | N/A | SHA-224, SHA-256, SHA-384, SHA-51 [unclear in source: printed "SHA-51", presumably SHA-512] |
| Keyed-hashing for message authentication | HMAC | FIPS PUB 198-1 IETF RFC 2104 | Short, long (> 64 bytes) | - |
| Encryption/decryption key-pair generation | RSA(4) | IETF RFC 8017; NIST SP800-56B | Up to 4160 | RSAES-OAEP |
| Signature with hashing | RSA(4) | IETF RFC 8017 FIPS PUB 186-4 | Up to 4160 | PKCS1-v1_5, PSS |
| Signature verification | ECDSA | ANSI X9.62 IETF RFC 7027 FIPS PUB 186-4 | Up to 640 | Refer to Table 269: Family of supported curves for ECC operations for details. |
| Key agreement | ECDH | ANSI X9.42 | Up to 640 | Refer to Table 269: Family of supported curves for ECC operations for details. |

Notes:

1. Certifiable by using STMicroelectronics-reviewed documents.
2. Random number distribution to SAES and PKA through a dedicated hardware bus.
3. ECB and CBC chaining modes are protected against side-channel and timing attacks in SAES (see Section 3.6.2: Secure AES co-processor (SAES).
4. Private key cryptography is protected against side-channel and timing attacks.

*Digest note:* Merged cells in the source are repeated per row: "AES(3)" spans the three AES rows; "FIPS PUB 180-4" and "N/A" span the SHA-1/SHA-2 rows; "Up to 640" and the "Refer to Table 269..." cell span the ECDSA/ECDH rows. The RSA key-pair row has two stacked specification cells (IETF RFC 8017 and NIST SP800-56B). The source prints "operationst" (typo). On STM32C551/C552 only the RNG, SHA-1, SHA-224, SHA-256 and HMAC rows apply (no AES per the datasheet/CMSIS headers, no PKA, no SHA-384/512).

### 3.6.2 Secure AES co-processor (SAES)

The devices provide an additional on-chip hardware AES encryption and decryption engine, that implements countermeasures and mitigations against power and electromagnetic side-channel attacks.

Clocked by the system clock, the SAES delivers excellent performance for a DPA-resistant hardware accelerator. The SAES engine supports 128-bit or 256-bit keys in electronic code book (ECB), cipher block chaining (CBC), (CTR), (GCM), (CCM), (GMAC) modes.

As shown in Section 3.4: Secure storage, the SAES can be used for highly secure on-chip storage for sensitive information. It can also be made secure-only.

For more information, refer to Section 27: AES hardware accelerator (AES).

*Digest note:* SAES exists only on STM32C59x/5A3 (Chapter 2, Table 3); absent on STM32C551/C552.

## 3.7 Product life cycle

A typical IoT device life cycle is summarized in the figure below. For each step, the devices propose secure life cycle management mechanisms embedded in the hardware.

**Figure 7. Device life cycle security** (ST drawing MSv64454V1)

A vertical dashed line separates "User states" (left) from "Vendor states" (right). On the vendor side, "Virgin device" goes by "Device manufacturing" to "STM32 personalized device", which goes by "Vendor manufacturing" to "Platform". From "Platform", "User provisioning" leads to "Development platform" (user side) and "Productization" leads to "Deployed product" (user side). From "Deployed product", "Decommissioning" leads to "Decommissioned product" (user side) and "Field return" leads to "Return material for analysis" (vendor side).

More details on the various phases and associated transitions, found either at the vendor or end-user premises, are summarized in the table below.

**Table 8. Main product life cycle transitions**

| Transitions | Description |
|---|---|
| Device manufacturing | STMicroelectronics creates new STM32 devices, always checking for manufacturing defects. During this process STM32 is provisioned with ROM firmware. |
| Vendor manufacturing | One (or more) vendor is responsible for the platform assembly, initialization, and provisioning before delivery to the end user. This end user can use the final product ("production" transition) or he/she can use the platform for software development ("user provisioning" transition). |
| Production | The end-user gets a product ready for use. All security functions of the platform are enabled, the debugging/testing features are restricted/disabled, and unique boot entry to immutable code is enforced. |
| User provisioning | Platform vendor prepares an individual platform for development, not to be connected to a production cloud network. |
| Field return or decommissioning | These are one-way transitions, with devices kept in user premises or returned to the manufacturer. In both cases, all data including user data is destroyed, therefore the devices lose the ability to operate securely (like connecting to a managed IoT network). |

The features described hereafter contribute to secure the device life cycle.

### 3.7.1 Life cycle management with readout protection (RDP)

The readout protection mechanism (full hardware feature) controls the access to the devices debug, test and provisioned secrets, as summarized in the table below.

**Table 9. Typical product life cycle phases**

| RDP protection level | Device state | Debug | Comments |
|---|---|---|---|
| Level 0 | Device open | Available | OEM and BS unlocking/locking keys can be provisioned in the flash memory user options. The keys programming, while not readable, can be verified under reset through debugger. |
| Level 2 with boundary scan | Device closed | None (boundary scan available under reset) | Boot address must target the user flash memory. Option-byte modification limited, RDP_LEVEL not modifiable hence RDP level 2 with boundary scan cannot be changed, unless the OEM unlocking key is activated or the BS locking key to progress to level 2 (see Table 10). |
| Level 2 | Device closed | None (JTAG fuse) | Boot address must target the user flash memory. Option-byte modification limited, RDP_LEVEL not modifiable hence RDP level 2 cannot be changed, unless the OEM unlocking key is activated (see Table 10). |

Note: OEMKEY option byte can be modified when RDP = 0 only.

The supported transitions, summarized in the following figure can be requested (when available) through the debug interface, or via the system bootloader to go to RDP L2_wBS or L2. Additionally, through JTAG/SWD under reset, once in L2_wBS or L2, it is possible to either progress to L2 or regress to L0.

*Digest note:* There is no RDP level 1 on STM32C5. Per RM Section 6.5.7 (Table 35, outside this page range), the RDP_LEVEL option byte codes are 0xED = L0 (open), 0xD1 = L2_wBS, 0x72 = L2; the factory value is L0. Per RM Section 6.10 (FLASH_SR), the OEMLOCK bit indicates whether an OEM key is provisioned; with OEMLOCK = 0, "progressing to RDP L2_wBS or L2 is irrevocable".

**Figure 8. RDP level transition scheme** (ST drawing MSv76018V2)

Three states: "RDP level 0", "RDP level 2 with BS" and "RDP level 2". Solid arrows (unconditional progressions) go from RDP level 0 to RDP level 2 with BS, and from RDP level 0 to RDP level 2. A dashed arrow, labelled "Conditioned by BSKEY" with a padlock, goes from RDP level 2 with BS to RDP level 2. Dashed arrows go from RDP level 2 with BS to RDP level 0, and from RDP level 2 to RDP level 0; the latter is labelled "Regression to level 0 conditioned by OEMKEY, full FLASH erase" with a padlock.

As shown in the previous figure, the user flash memory is automatically erased, during an RDP regression. These regressions can be conditioned on dedicated 128-bit password keys, if provisioned by the OEM (see the next subsection). During the regression from RDP L2 or L2_wBS to RDP L0, the FLASH is erased. The OTP area in the flash memory is kept, all SRAMS and targeted device secrets are erased. Hence, no secrets must be stored in the OTP as they are revealed after a regression to RDP L0. These secrets, also erased as response to tamper, are defined in Section 3.3.3: Tamper detection and response.

For more details on RDP, refer to Section 6: Embedded flash memory (FLASH).

#### RDP unlocking sequences

The use of the OEM and BS password keys described in Figure 8 is described hereafter.

Note: The devices support password-based RDP L2 (or L2_wBS) regression to L0. This L2 regression erases the application code.

Details on the password-based regression can be found in the tables below.

**Table 10. OEM RDP unlocking methods** (OEM password options)

| OEM LOCK | RDP level | RDP regression |
|---|---|---|
| 1 | L2_wBS | Automatic regression to L0 triggered upon successful OEM unlock sequence |
| 1 | L2 | Automatic regression to L0 triggered upon successful OEM unlock sequence |
| 0 | L2_wBS | Regression to L0 impossible. Possibility to transition to RDP L2. |
| 0 | L2 | Regression to L0 impossible. RDP L2 remains a permanent state. |

**Table 11. BS RDP locking methods** (BS password options)

| Initial RDP level | RDP regression |
|---|---|
| L2_wBS, with BSKEY not provisioned | Automatic progression to L2 triggered upon successful BS lock sequence using default key |
| L2_wBS, with BSKEY provisioned | Automatic progression to L2 triggered upon successful BS lock sequence using custom key provisioned under RDP L0 |

- OEM unlock sequence, starting at RDP L2 or L2_wBS:
  - Shift the password key through JTAG/SWD under reset.
  - If this key matches the OEMKEY provisioned in the device, the device automatically triggers a regression sequence to level 0. After the regression is completed, a power-on reset has to be performed by the user.
  - In case of mismatch value, the RDP regression is blocked, and RDP L2 protections are enforced until the next power-on reset.
- BS lock sequence, starting at RDP L2_wBS:
  - Shift the password key through JTAG/SWD under reset (see the note below). A default key is provisioned in ST factory 0xAAAAAAAA. The user can provision a custom one under RDP L0.
  - If this key matches the BSKEY provisioned in the device, the device automatically triggers a progression sequence to L2. After the progression is completed, a power-on reset has to be performed by the user.
  - In case of a mismatch value, the RDP progression is blocked until the next power-on reset.

Note: Unlocking the device with a password is possible only once per power cycle.

Shifting the OEM password key through JTAG/SWD corresponds to writing four 32-bit key words: AUTH_KEY[31:0], then AUTH_KEY[63:32], AUTH_KEY[95:64], then AUTH_KEY[127:96] in the DBGMCU_DBG_AUTH_HOST register.

Shifting the BS password key through JTAG/SWD corresponds to writing a 32-bit key word: BS_KEY[31:0] in the DBG_BSKEY_PWD register.

#### JTAG 32-bit device specific ID

Unless the JTAG port is deactivated (OEMLOCK = 0 and RDP L2), a 32-bit device specific quantity can always be read through the JTAG port. This information is stored in DBGMCU_DBG_AUTH_DEVICE.

The OEM can use this 32-bit information to derive the expected OEM password keys to unlock this specific device.

## 3.8 Summary of protection mechanism

The different security mechanism may reset, block or erase device secrets or sensitive peripherals. To be more explicit on those effects, please refer to the below table:

**Table 12. Summary of protected assets and protection mechanism(1)**

| Assets | Regression to RDP L0 | Potential tamper | Confirmed tamper | POR | System reset | RTC domain reset |
|---|---|---|---|---|---|---|
| SRAM1 | E | - | - | - | Erase if SRAM1_RST bit is '0' (erase done at OPT activation) | - |
| SRAM2 | E | B | E | E | Erase if SRAM2_RST bit is '0' (erase done at OPT activation) | - |
| FLASH | E | - | - | - | - | - |
| FLASH EDATA page | E | - | - | - | - | - |
| Flash OTP | - | - | - | - | - | - |
| BKUP registers | R | B(2) | R/B(2) | R(3) | - | R |
| ICACHE | E | E | E | E | E | - |
| PKA RAM | E | E/B(4) | E/B(4) | E | E | - |
| FDCAN RAM | - | - | - | - | - | - |
| USB RAM | - | - | - | - | - | - |
| ETH RAM | - | - | - | - | - | - |
| AES/HASH/SAES/CCB registers | R | R | R | R | R | - |
| PKA registers | R | R | R | R | R | - |
| RNG registers | R | - | - | R | R | - |

Notes:

1. E = Erase, B = Access blocked, R = Reset, N.A. = Not applicable, "-" = No effect
2. Bocked up to clearing of TAMP status register flag.
3. Erase after POR
4. Blocked during erasing.

*Digest note:* "Bocked" in note 2 is printed as such (meaning "Blocked"). PKA RAM/registers, SAES/CCB registers and ETH RAM do not exist on STM32C551/C552; FDCAN RAM exists only on STM32C552.

*Digest note:* SRAM erase-on-system-reset polarity and defaults (from RM Section 6, FLASH_OPTSR2_CUR/PRG and Table 28, outside this page range): SRAM1_RST is bit 0 and SRAM2_RST is bit 1 of FLASH_OPTSR2; 0 = SRAMx erased when a system reset occurs, 1 = not erased. The user-default (factory) value of both bits is 1 (not erased). The FLASH_OPTSR2 "default value in case of double ECC issue during OBL" is 0x0000 0010, i.e. SRAM1_RST = 0 and SRAM2_RST = 0 (both SRAMs erased on system reset) if option-byte loading fails. Table 12 also shows SRAM2 is always erased on POR while SRAM1 is not.
