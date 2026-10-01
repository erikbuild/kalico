# RM0522 Chapter 11: General-purpose I/Os (GPIO)

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 339–356.

## 11.1 GPIO introduction

Each general-purpose I/O port has four 32-bit configuration registers (GPIOx_MODER, GPIOx_OTYPER, GPIOx_OSPEEDR, and GPIOx_PUPDR), two 32-bit data registers (GPIOx_IDR and GPIOx_ODR), a 16-bit reset register (GPIOx_BRR), and a 32-bit set/reset register (GPIOx_BSRR).

In addition, all GPIOs have a 32-bit locking register (GPIOx_LCKR) and two 32-bit alternate function selection registers (GPIOx_AFRH and GPIOx_AFRL).

## 11.2 GPIO main features

- Output states: push-pull or open drain + pull-up/down
- Output data from output data register (GPIOx_ODR) or peripheral (alternate function output)
- Speed selection for each I/O
- Input states: floating, pull-up/down, analog
- Input data to input data register (GPIOx_IDR) or peripheral (alternate function input)
- Bit set and reset register (GPIOx_BSRR) for bit-wise write access to GPIOx_ODR
- Lock mechanism (GPIOx_LCKR) provided to freeze the I/O port configurations
- Analog function
- Alternate function selection registers
- Fast toggle capable of changing every two clock cycles
- Highly flexible pin multiplexing allows the use of I/O pins as GPIOs or as one of several peripheral functions
- I/Os state retention during Standby mode

## 11.3 GPIO functional description

Based on the specific hardware characteristics of each I/O port listed in the datasheet, each port bit of the general-purpose I/O (GPIO) ports can be individually configured by software in several modes:

- Input floating
- Input pull-up
- Input-pull-down
- Analog
- Output open-drain with pull-up or pull-down capability
- Output push-pull with pull-up or pull-down capability
- Alternate function push-pull with pull-up or pull-down capability
- Alternate function open-drain with pull-up or pull-down capability

Each I/O port bit is freely programmable, however the I/O port registers must be accessed as 32-bit words, half-words, or bytes. The GPIOx_BSRR and GPIOx_BRR registers allow atomic read/modify accesses to any of the GPIOx_ODR registers. In this way, there is no risk of an IRQ occurring between the read and the modify access.

The figure below shows the basic structure of a 3- or 5-V tolerant GPIO (TT or FT). Table 78 gives the possible port bit configurations.

**Figure 31. Structure of 3- or 5-V tolerant GPIO (TT or FT)** (described)

- Analog section: an "Analog IP" connects to the pad through a node that has a parasitic diode and resistor to VDDA. In the "Analog option" box, an analog switch connects this analog node to the I/O pin line.
- Digital section: the "Alternate function input" and the "Input data register" are fed from the input buffer (a Schmitt-trigger buffer) connected to the I/O pin line. The "Output data register" and "Alternate function output" feed a multiplexer into the "Output control" block of the output buffer, which drives a PMOS (to VDD) and an NMOS (to VSS) connected to the I/O pin line.
- Pin side: a switchable (on/off) pull-up resistor RPU to VDD, a switchable (on/off) pull-down resistor RPD to VSS, an ESD protection block to VSS, and a protection diode to VSS, all on the I/O pin line.

Note: On a TT GPIO, the analog switch is not present, it is replaced by a direct connection. The analog bloc parasitic circuitry does not allow 5-V tolerance.

**Table 78. Port bit configuration(1)**

| MODE(i)[1:0] | OTYPE(i) | OSPEED(i)[1:0] | PUPD(i)[1:0] | I/O configuration |
|---|---|---|---|---|
| 01 | 0 | SPEED[1:0] | 00 | GP output PP |
| 01 | 0 | SPEED[1:0] | 01 | GP output PP + PU |
| 01 | 0 | SPEED[1:0] | 10 | GP output PP + PD |
| 01 | 0 | SPEED[1:0] | 11 | Reserved |
| 01 | 1 | SPEED[1:0] | 00 | GP output OD |
| 01 | 1 | SPEED[1:0] | 01 | GP output OD + PU |
| 01 | 1 | SPEED[1:0] | 10 | GP output OD + PD |
| 01 | 1 | SPEED[1:0] | 11 | Reserved (GP output OD) |
| 10 | 0 | SPEED[1:0] | 00 | AF PP |
| 10 | 0 | SPEED[1:0] | 01 | AF PP + PU |
| 10 | 0 | SPEED[1:0] | 10 | AF PP + PD |
| 10 | 0 | SPEED[1:0] | 11 | Reserved |
| 10 | 1 | SPEED[1:0] | 00 | AF OD |
| 10 | 1 | SPEED[1:0] | 01 | AF OD + PU |
| 10 | 1 | SPEED[1:0] | 10 | AF OD + PD |
| 10 | 1 | SPEED[1:0] | 11 | Reserved |
| 00 | x | x x | 00 | Input Floating |
| 00 | x | x x | 01 | Input PU |
| 00 | x | x x | 10 | Input PD |
| 00 | x | x x | 11 | Reserved (input floating) |
| 11 | x | x x | 00 | Input/output Analog |
| 11 | x | x x | 01 | Reserved |
| 11 | x | x x | 10 | Input/output Analog |
| 11 | x | x x | 11 | Reserved |

Notes:

1. GP = general-purpose, PP = push-pull, PU = pull-up, PD = pull-down, OD = open-drain, AF = alternate function.

### 11.3.1 General-purpose I/O (GPIO)

During and just after reset, the alternate functions are not active and most of the I/O ports are configured in analog mode.

The debug pins are in AF pull-up/pull-down after reset:

- PA15: JTDI in pull-up
- PA14: JTCK/SWCLK in pull-down
- PA13: JTMS/SWDIO in pull-up
- PB4: NJTRST in pull-up
- PB3: JTDO/TRACESWO in floating state no pull-up/pull-down

BOOT0 is in input mode during the reset until at least the end of the option byte loading phase (see Section 11.3.15).

*Digest note:* the cross-reference to Section 11.3.15 appears wrong in the source (11.3.15 is "I/Os state retention during standby mode"). Per the datasheet digest, BOOT0 shares a pin with PH2 (PH2-BOOT0) on most packages and with PB8 (PB8-BOOT0) on LQFP32.

When the pin is configured as output, the value written to the output data register (GPIOx_ODR) is output on the I/O pin. It is possible to use the output driver in push-pull mode or open-drain mode (only the low level is driven, the high level is high-Z).

The input data register (GPIOx_IDR) captures the data present on the I/O pin at every AHB clock cycle.

All GPIO pins have weak internal pull-up and pull-down resistors, which can be activated or not, depending upon the value in the GPIOx_PUPDR register.

### 11.3.2 I/O pin alternate function multiplexer and mapping

The device I/O pins are connected to on-board peripherals/modules through a multiplexer that allows only one peripheral alternate function (AF) connected to an I/O pin at a time. In this way, there is no conflict between peripherals available on the same I/O pin.

Each I/O pin has a multiplexer with up to 16 alternate function inputs (AF0 to AF15) that can be configured through the GPIOx_AFRL (for pin 0 to 7) and GPIOx_AFRH (for pin 8 to 15) registers:

- After reset, the multiplexer selection is alternate function 0 (AF0). The I/Os are configured in alternate function mode through the GPIOx_MODER register.
- The specific alternate function assignments for each pin are detailed in the device datasheet.

In addition to this flexible I/O multiplexing architecture, each peripheral has alternate functions mapped onto different I/O pins to optimize the number of peripherals available in smaller packages.

To use an I/O in a given configuration, the user must proceed as follows:

- Debug function: after each device reset these pins are assigned as alternate function pins immediately usable by the debugger host.
- GPIO: configure the desired I/O as output, input, or analog in the GPIOx_MODER register.
- Alternate function:
  - Connect the I/O to the desired AFx in one of the GPIOx_AFRL or GPIOx_AFRH register.
  - Select the type, pull-up/pull-down, and output speed via the GPIOx_OTYPER, GPIOx_PUPDR and GPIOx_OSPEEDR registers respectively.
  - Configure the desired I/O as an alternate function in the GPIOx_MODER register.
  - The Cortex-M33 output EVENTOUT signal can be output as alternate function on several I/Os. An event can be indicated through the configured pin after executing SEV instruction.
  - The EVENTOUT signal can be used internally as a trigger for some peripherals (see Section 13: Peripherals interconnect matrix)
- Additional functions:
  - For the ADC, DAC, COMP, and OPAMP configure the desired I/O in analog mode in the GPIOx_MODER register and configure the required function in the ADC, DAC, COMP, and OPAMP registers.
  - For the additional functions like RTC, WKUPx, LSCO, and oscillators, configure the required function in the related RTC, PWR, and RCC registers. These functions have priority over the configuration in the standard GPIO registers.

Refer to the "Alternate function mapping" table in the device datasheet for the detailed mapping of the alternate function I/O pins.

*Digest note:* the STM32C55xxx alternate function mapping is Table 13 of the datasheet digest (/Users/erik/Code/kalico/digest-docs/digest/st/STM32C55xxx_Datasheet.md). Per the datasheet digest, STM32C55xxx has two ADCs, one DAC channel and one comparator, and no OPAMP.

### 11.3.3 I/O port control registers

Each of the GPIO ports has four 32-bit memory-mapped control registers (GPIOx_MODER, GPIOx_OTYPER, GPIOx_OSPEEDR, GPIOx_PUPDR) to configure up to 16 I/Os. The GPIOx_MODER register is used to select the I/O mode (input, output, AF, analog). The GPIOx_OTYPER and GPIOx_OSPEEDR registers are used to select the output type (push-pull or open-drain) and speed. The GPIOx_PUPDR register is used to select the pull-up/pull-down whatever the I/O direction.

### 11.3.4 I/O port data registers

Each GPIO has two 16-bit memory-mapped data registers: input and output data registers (GPIOx_IDR and GPIOx_ODR (x = A to H)).

GPIOx_ODR stores the data to be output, it is read/write accessible. The data entered through the I/Os are stored into the input data register (GPIOx_IDR), a read-only register.

### 11.3.5 I/O data bitwise handling

GPIOx_BSRR is a 32-bit register that allows the application to set and reset each individual bit in GPIOx_ODR. The bit set reset register has twice the size of GPIOx_ODR.

To each bit in GPIOx_ODR, correspond two control bits in GPIOx_BSRR: BS(i) and BR(i). When written to 1, BS(i) sets the corresponding ODR(i) bit. When written to 1, BR(i) resets the corresponding ODR(i) bit.

Writing any bit to 0 in GPIOx_BSRR does not have any effect on the corresponding bit in GPIOx_ODR. If there is an attempt to both set and reset a bit in GPIOx_BSRR, the set action takes priority.

Using the GPIOx_BSRR register to change the values of individual bits in GPIOx_ODR is a "one-shot" effect that does not lock the GPIOx_ODR bits. The GPIOx_ODR bits can always be accessed directly. The GPIOx_BSRR register provides a way of performing atomic bitwise handling.

There is no need for the software to disable interrupts when programming the GPIOx_ODR at bit level: one or more bits can be modified in a single atomic AHB write access.

### 11.3.6 GPIO locking mechanism

The GPIO control registers can be frozen by applying a specific write sequence to the GPIOx_LCKR register. The frozen registers are GPIOx_MODER, GPIOx_OTYPER, GPIOx_OSPEEDR, GPIOx_PUPDR, GPIOx_AFRL, and GPIOx_AFRH.

To write the GPIOx_LCKR register, a specific write/read sequence must be applied. When the right LOCK sequence is applied to the bit 16 in this register, the value of LCKR[15:0] is used to lock the configuration of the I/Os (during the write sequence the LCKR[15:0] value must be the same). When the LOCK sequence is applied to a port bit, the value of the port bit can no longer be modified until the next MCU reset or peripheral reset. Each GPIOx_LCKR bit freezes the corresponding bit in the control registers (GPIOx_MODER, GPIOx_OTYPER, GPIOx_OSPEEDR, GPIOx_PUPDR, GPIOx_AFRL and GPIOx_AFRH.

The LOCK sequence can be performed only using a word (32-bit long) access to the GPIOx_LCKR register, because GPIOx_LCKR bit 16 must be set at the same time as the [15:0] bits.

### 11.3.7 I/O alternate function input/output

Two registers are provided to select one of the alternate function inputs/outputs available for each I/O. With these registers, the user can connect an alternate function to some other pin as required by the application.

This means that some peripheral functions are multiplexed on each GPIO using the GPIOx_AFRL and GPIOx_AFRH alternate function registers. The application can thus select any one of the possible functions for each I/O. The AF selection signal being common to the alternate function input and alternate function output, a single channel is selected for the alternate function input/output of a given I/O.

To know which functions are multiplexed on each GPIO pin, refer to the device datasheet.

### 11.3.8 External interrupt/wake-up lines

All ports have external interrupt capability. To use external interrupt lines, the port can be configured in input, output, or alternate function mode (the port must not be configured in analog mode). Refer to Section 16: Extended interrupts and event controller (EXTI).

### 11.3.9 Input configuration

When the I/O port is programmed as input:

- The output buffer is disabled.
- The Schmitt trigger input is activated.
- The pull-up and pull-down resistors are activated depending on the value in the GPIOx_PUPDR register.
- The data present on the I/O pin are sampled into the input data register every AHB clock cycle.
- A read access to the input data register provides the I/O state.

The figure below shows the input configuration of the I/O port bit.

**Figure 32. Input floating/pull-up/pull-down configurations** (described)

The I/O pin feeds the input driver, whose TTL Schmitt trigger is on and is sampled into the input data register (read path). The output driver is shown disabled. Switchable (on/off) pull-up to VDDIOx and pull-down to VSS, ESD protection and a protection diode are on the pin. The bit set/reset registers write the output data register (read/write), which is not connected to the pin in this mode.

### 11.3.10 Output configuration

When the I/O port is programmed as output:

- The output buffer is enabled:
  - Open-drain mode: a 0 in the output register activates the N-MOS whereas a 1 in the output register leaves the port in high-Z (the P-MOS is never activated).
  - Push-pull mode: a 0 in the output register activates the N-MOS whereas a 1 in the output register activates the P-MOS.
- The Schmitt trigger input is activated.
- The pull-up and pull-down resistors are activated depending on the value in the GPIOx_PUPDR register.
- The data present on the I/O pin are sampled into the input data register every AHB clock cycle.
- A read access to the input data register gets the I/O state.
- A read access to the output data register gets the last written value.

The figure below shows the output configuration of the I/O port bit.

**Figure 33. Output configuration** (described)

As Figure 32, but the output data register (written directly or via the bit set/reset registers) drives the output control block of the output driver, which switches a P-MOS to VDDIOx and an N-MOS to VSS (push-pull or open-drain). The TTL Schmitt trigger remains on, so the input data register reflects the pin state.

### 11.3.11 Alternate function configuration

When the I/O port is programmed as alternate function:

- The output buffer can be configured in open-drain or push-pull mode.
- The output buffer is driven by the signals coming from the peripheral (transmitter enable and data).
- The Schmitt trigger input is activated.
- The weak pull-up and pull-down resistors are activated or not depending on the value in the GPIOx_PUPDR register.
- The data present on the I/O pin are sampled into the input data register every AHB clock cycle.
- A read access to the input data register gets the I/O state.

The figure below shows the alternate function configuration of the I/O port bit.

**Figure 34. Alternate function configuration** (described)

As Figure 33, but the output control block is driven by the "alternate function output" coming from the on-chip peripheral instead of the output data register, and the Schmitt trigger output also goes to the on-chip peripheral as "alternate function input" (in addition to the input data register).

### 11.3.12 Analog configuration

When the I/O port is programmed as analog configuration:

- The output buffer is disabled.
- The Schmitt trigger input is deactivated, providing zero consumption for every analog value of the I/O pin. The output of the Schmitt trigger is forced to a constant value (0).
- The weak pull-up is disabled by hardware. The weak pull-down is configurable.
- Read access to the input data register gets the value 0.

The figure below shows the high-Z, analog-input configuration of the I/O port bits.

**Figure 35. High-impedance analog configuration** (described)

The I/O pin connects directly to the "Analog" path to/from the on-chip peripheral. The TTL Schmitt trigger is off and the output driver is disabled. Only the pull-down (no pull-up), the ESD protection and the protection diode are shown on the pin.

### 11.3.13 Using the HSE or LSE oscillator pins as GPIOs

When the HSE or LSE oscillator is switched off (default state after reset), the related oscillator pins can be used as normal GPIOs.

When the HSE or LSE oscillator is switched on (by setting the HSEON or LSEON bit in the RCC_CR1 register), the oscillator takes control of its associated pins and the GPIO configuration of these pins has no effect.

When the oscillator is configured in a user external clock mode, only the pin is reserved for clock input, and the OSC_OUT or OSC32_OUT pin can still be used as normal GPIO.

### 11.3.14 Using the GPIO pins in the RTC supply domain

The PC13/PC14/PC15 GPIO functionality is lost when the core supply domain is powered off (when the device enters Standby mode). In this case, if their GPIO configuration is not bypassed by the RTC configuration, these pins are set in an analog input mode.

For details about I/O control by the RTC, refer to Section 39.3: RTC functional description.

### 11.3.15 I/Os state retention during standby mode

In the Standby mode, the I/Os are by default in floating state.

If the IORETEN bit in the PWR_IORETR register is set, the I/Os state is sampled during standby entry. The state of I/Os is applied to the pin via pull-up and pull-down resistors. The pull-up and pull-down resistors remains applied after Standby wake-up until the IORETEN bit in the PWR_IORETR register is cleared by software.

### 11.3.16 Privileged and unprivileged modes

All GPIO registers can be read and written by privileged and unprivileged accesses.

### 11.3.17 I/O compensation cell

The I/O commutation slew rate (tfall / trise) can be adapted by software depending on process, voltage and temperatures conditions, to reduce the I/O noise on power supply.

Refer to Section 12: System configuration, boot, and security (SBS) for more details.

## 11.4 GPIO registers

This section gives a detailed description of the GPIO registers. The peripheral registers can be written in word, half word, or byte mode.

For the actual availability of GPIO ports and their related bits, check the datasheet or Table 3: Memory map and peripheral register boundary addresses. If not present, consider them as reserved, and keep them at reset value.

*Digest note:* the CMSIS header (stm32c552xx.h) defines GPIOA..GPIOE and GPIOH only, at AHB2PERIPH_BASE (0x4202 0000) + 0x400 * port index: GPIOA 0x4202 0000, GPIOB 0x4202 0400, GPIOC 0x4202 0800, GPIOD 0x4202 0C00, GPIOE 0x4202 1000, GPIOH 0x4202 1C00 (no GPIOF/GPIOG). The datasheet digest likewise lists ports A, B, C, D, E and H (port H has only PH0 to PH5 and PH15; there is no PB11). The header GPIO_TypeDef has exactly the registers below (AFR[2] = AFRL, AFRH).

### 11.4.1 GPIO port mode register (GPIOx_MODER) (x = A to H)

Address offset: 0x00. Reset value: 0xABFF FFFF (for port A); 0xFF3F FEBF (for port B); 0xFFFF FFFF (for the other ports).

- **Bits 31:0 MODEy[1:0]** (rw): Port x configuration I/O pin y (y = 15 to 0)
  These bits are written by software to configure the I/O mode.
  - 00: Input mode
  - 01: General purpose output mode
  - 10: Alternate function mode
  - 11: Analog mode (reset state)

  Note: The bitfield is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.

Field layout: MODE15[1:0] bits 31:30, MODE14 29:28, MODE13 27:26, MODE12 25:24, MODE11 23:22, MODE10 21:20, MODE9 19:18, MODE8 17:16, MODE7 15:14, MODE6 13:12, MODE5 11:10, MODE4 9:8, MODE3 7:6, MODE2 5:4, MODE1 3:2, MODE0 1:0 (pin y at bits 2y+1:2y).

*Digest note:* decoding the reset values: port A 0xABFF FFFF gives MODE15 = MODE14 = MODE13 = 10 (AF: PA15 JTDI, PA14 SWCLK, PA13 SWDIO), all other port A pins 11 (analog). Port B 0xFF3F FEBF gives MODE4 = 10 (AF: PB4 NJTRST), MODE3 = 10 (AF: PB3 JTDO/TRACESWO) and MODE11 = 00 (input); all other port B pins 11 (analog). The Table 79 register map shows the same per-bit values. PB11 does not exist on the datasheet pinout, which presumably explains its non-analog reset value [unclear in source: RM gives no reason for PB11 = 00]. Firmware that reconfigures PA13/PA14 loses SWD access.

### 11.4.2 GPIO port output type register (GPIOx_OTYPER) (x = A to H)

Address offset: 0x04. Reset value: 0x0000 0000.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bits 15:0 OTy** (rw): Port x configuration I/O pin y (y = 15 to 0)
  These bits are written by software to configure the I/O output type.
  - 0: Output push-pull (reset state)
  - 1: Output open-drain

  Note: The bit is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.

### 11.4.3 GPIO port output speed register (GPIOx_OSPEEDR) (x = A to H)

Address offset: 0x08. Reset value: 0x0C00 0000 (for port A); 0x0000 00C0 (for port B); 0x0000 0000 (for the other ports).

- **Bits 31:0 OSPEEDy[1:0]** (rw): Port x configuration I/O pin y (y = 15 to 0)
  These bits are written by software to configure the I/O output speed.
  - 00: Low speed
  - 01: Medium speed
  - 10: High speed
  - 11: Very-high speed

  Note: Refer to the device datasheet for the frequency specifications, the power supply, and the load conditions for each speed.
  The bitfield is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.

Field layout: OSPEEDy[1:0] at bits 2y+1:2y (OSPEED15 31:30 ... OSPEED0 1:0).

*Digest note:* reset decode: port A OSPEED13 = 11 (PA13 SWDIO very-high speed); port B OSPEED3 = 11 (PB3 JTDO/TRACESWO very-high speed); all others low speed.

### 11.4.4 GPIO port pull-up/pull-down register (GPIOx_PUPDR) (x = A to H)

Address offset: 0x0C. Reset value: 0x6400 0000 (for port A); 0x0000 0100 (for port B); 0x0000 0000 (for the other ports).

- **Bits 31:0 PUPDy[1:0]** (rw): Port x configuration I/O pin y (y = 15 to 0)
  These bits are written by software to configure the I/O pull-up or pull-down
  - 00: No pull-up, pull-down
  - 01: Pull-up
  - 10: Pull-down
  - 11: Reserved

  Note: The bitfield is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.

Field layout: PUPDy[1:0] at bits 2y+1:2y (PUPD15 31:30 ... PUPD0 1:0).

*Digest note:* reset decode: port A PUPD15 = 01 (PA15 pull-up), PUPD14 = 10 (PA14 pull-down), PUPD13 = 01 (PA13 pull-up); port B PUPD4 = 01 (PB4 pull-up). Matches Section 11.3.1.

### 11.4.5 GPIO port input data register (GPIOx_IDR) (x = A to H)

Address offset: 0x10. Reset value: 0x0000 XXXX.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bits 15:0 IDy** (r): Port x input data I/O pin y (y = 15 to 0)
  These bits are read-only. They contain the input value of the corresponding I/O port.

  Note: The bit is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.

### 11.4.6 GPIO port output data register (GPIOx_ODR) (x = A to H)

Address offset: 0x14. Reset value: 0x0000 0000.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bits 15:0 ODy** (rw): Port output data I/O pin y (y = 15 to 0)
  These bits can be read and written by software.

  Note: For atomic bit set/reset, the OD bits can be individually set and/or reset by writing to the GPIOx_BSRR or GPIOx_BRR registers (x = A to H).
  The bit is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.

### 11.4.7 GPIO port bit set/reset register (GPIOx_BSRR) (x = A to H)

Address offset: 0x18. Reset value: 0x0000 0000. Write-only.

- **Bits 31:16 BRy** (w): Port x reset I/O pin y (y = 15 to 0)
  These bits are write-only. A read to these bits returns the value 0x0000.
  - 0: No action on the corresponding ODy bit
  - 1: Resets the corresponding ODy bit

  Note: If both BSy and BRy are set, BSy has priority.
  The bit is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.
- **Bits 15:0 BSy** (w): Port x set I/O pin y (y = 15 to 0)
  These bits are write-only. A read to these bits returns the value 0x0000.
  - 0: No action on the corresponding ODy bit
  - 1: Sets the corresponding ODy bit

  Note: The bit is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.

### 11.4.8 GPIO port configuration lock register (GPIOx_LCKR) (x = A to H)

Address offset: 0x1C. Reset value: 0x0000 0000.

This register is used to lock the configuration of the port bits when a correct write sequence is applied to bit 16 (LCKK). The value of bits [15:0] is used to lock the configuration of the GPIO. During the write sequence, the value of LCKR[15:0] must not change. When the LOCK sequence has been applied on a port bit, the value of this port bit can no longer be modified until the next MCU reset or peripheral reset.

Note: A specific write sequence is used to write to the GPIOx_LCKR register. Only word access (32-bit long) is allowed during this locking sequence.
Each bit freezes a specific configuration register (control and alternate function registers).

- **Bits 31:17** Reserved, must be kept at reset value.
- **Bit 16 LCKK** (rw): Lock key
  This bit can be read any time. It can only be modified using the lock key write sequence.
  - 0: Port configuration lock key not active
  - 1: Port configuration lock key active. The GPIOx_LCKR register is locked until the next MCU reset or peripheral reset.

  LOCK key write sequence:

  - WR LCKR[16] = 1 + LCKR[15:0]
  - WR LCKR[16] = 0 + LCKR[15:0]
  - WR LCKR[16] = 1 + LCKR[15:0]

  LOCK key read:

  - RD LCKR[16] = 1 (this read operation is optional but it confirms that the lock is active)

  Note: During the LOCK key write sequence, the value of LCK[15:0] must not change.
  Any error in the lock sequence aborts the LOCK.
  After the first LOCK sequence on any bit of the port, any read access on the LCKK bit returns 1 until the next MCU reset or peripheral reset.
- **Bits 15:0 LCKy** (rw): Port x lock I/O pin y (y = 15 to 0)
  These bits are read/write but can only be written when the LCKK bit is 0
  - 0: Port configuration not locked
  - 1: Port configuration locked

  Note: The bit is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.

### 11.4.9 GPIO alternate function low register (GPIOx_AFRL) (x = A to H)

Address offset: 0x20. Reset value: 0x0000 0000.

- **Bits 31:0 AFSELy[3:0]** (rw): Alternate function selection for port x I/O pin y (y = 7 to 0)
  These bits are written by software to configure alternate function I/Os.
  - 0000: AF0
  - 0001: AF1
  - 0010: AF2
  - 0011: AF3
  - 0100: AF4
  - 0101: AF5
  - 0110: AF6
  - 0111: AF7
  - 1000: AF8
  - 1001: AF9
  - 1010: AF10
  - 1011: AF11
  - 1100: AF12
  - 1101: AF13
  - 1110: AF14
  - 1111: AF15

  Note: The bitfield is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.

Field layout: AFSEL7[3:0] bits 31:28, AFSEL6 27:24, AFSEL5 23:20, AFSEL4 19:16, AFSEL3 15:12, AFSEL2 11:8, AFSEL1 7:4, AFSEL0 3:0 (pin y at bits 4y+3:4y).

### 11.4.10 GPIO alternate function high register (GPIOx_AFRH) (x = A to H)

Address offset: 0x24. Reset value: 0x0000 0000.

- **Bits 31:0 AFSELy[3:0]** (rw): Alternate function selection for port x I/O pin y (y = 15 to 8)
  These bits are written by software to configure alternate function I/Os.
  - 0000: AF0
  - 0001: AF1
  - 0010: AF2
  - 0011: AF3
  - 0100: AF4
  - 0101: AF5
  - 0110: AF6
  - 0111: AF7
  - 1000: AF8
  - 1001: AF9
  - 1010: AF10
  - 1011: AF11
  - 1100: AF12
  - 1101: AF13
  - 1110: AF14
  - 1111: AF15

  Note: The bitfield is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.

Field layout: AFSEL15[3:0] bits 31:28, AFSEL14 27:24, AFSEL13 23:20, AFSEL12 19:16, AFSEL11 15:12, AFSEL10 11:8, AFSEL9 7:4, AFSEL8 3:0 (pin y at bits 4(y-8)+3:4(y-8)).

### 11.4.11 GPIO port bit reset register (GPIOx_BRR) (x = A to H)

Address offset: 0x28. Reset value: 0x0000 0000. Write-only.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bits 15:0 BRy** (w): Port x reset IO pin y (y = 15 to 0)
  These bits are write-only. A read to these bits returns the value 0x0000.
  - 0: No action on the corresponding ODy bit
  - 1: Reset the corresponding ODy bit

  Note: The bit is reserved and must be kept to reset value when the corresponding I/O is not available on the selected package.

### 11.4.12 GPIO register map

**Table 79. GPIO register map and reset values**

| Offset | Register | Reset value | Fields (bit positions) |
|---|---|---|---|
| 0x00 | GPIOx_MODER (x = A to H) | Port A: 0xABFF FFFF; port B: 0xFF3F FEBF; ports C...H: 0xFFFF FFFF | MODE15[1:0] (31:30); MODE14[1:0] (29:28); MODE13[1:0] (27:26); MODE12[1:0] (25:24); MODE11[1:0] (23:22); MODE10[1:0] (21:20); MODE9[1:0] (19:18); MODE8[1:0] (17:16); MODE7[1:0] (15:14); MODE6[1:0] (13:12); MODE5[1:0] (11:10); MODE4[1:0] (9:8); MODE3[1:0] (7:6); MODE2[1:0] (5:4); MODE1[1:0] (3:2); MODE0[1:0] (1:0) |
| 0x04 | GPIOx_OTYPER (x = A to H) | 0x0000 0000 | 31:16 Res.; OT15..OT0 (15:0) |
| 0x08 | GPIOx_OSPEEDR (x = A to H) | Port A: 0x0C00 0000; port B: 0x0000 00C0; ports C...H: 0x0000 0000 | OSPEED15[1:0] (31:30) ... OSPEED0[1:0] (1:0), two bits per pin |
| 0x0C | GPIOx_PUPDR (x = A to H) | Port A: 0x6400 0000; port B: 0x0000 0100; ports C...H: 0x0000 0000 | PUPD15[1:0] (31:30) ... PUPD0[1:0] (1:0), two bits per pin |
| 0x10 | GPIOx_IDR (x = A to H) | 0x0000 XXXX | 31:16 Res.; ID15..ID0 (15:0) |
| 0x14 | GPIOx_ODR (x = A to H) | 0x0000 0000 | 31:16 Res.; OD15..OD0 (15:0) |
| 0x18 | GPIOx_BSRR (x = A to H) | 0x0000 0000 | BR15..BR0 (31:16); BS15..BS0 (15:0) |
| 0x1C | GPIOx_LCKR (x = A to H) | 0x0000 0000 | 31:17 Res.; LCKK (16); LCK15..LCK0 (15:0) |
| 0x20 | GPIOx_AFRL (x = A to H) | 0x0000 0000 | AFSEL7[3:0] (31:28); AFSEL6[3:0] (27:24); AFSEL5[3:0] (23:20); AFSEL4[3:0] (19:16); AFSEL3[3:0] (15:12); AFSEL2[3:0] (11:8); AFSEL1[3:0] (7:4); AFSEL0[3:0] (3:0) |
| 0x24 | GPIOx_AFRH (x = A to H) | 0x0000 0000 | AFSEL15[3:0] (31:28); AFSEL14[3:0] (27:24); AFSEL13[3:0] (23:20); AFSEL12[3:0] (19:16); AFSEL11[3:0] (15:12); AFSEL10[3:0] (11:8); AFSEL9[3:0] (7:4); AFSEL8[3:0] (3:0) |
| 0x28 | GPIOx_BRR (x = A to H) | 0x0000 0000 | 31:16 Res.; BR15..BR0 (15:0) |

Refer to Section 2.2: Memory organization for the register boundary addresses.

*Digest note:* GPIO bit positions match the CMSIS header stm32c552xx.h (e.g. GPIO_MODER_MODE15_Pos = 30, GPIO_LCKR_LCKK_Pos = 16, GPIO_AFRH_AFSEL15_Pos = 28, GPIO_BRR_BR15_Pos = 15).
