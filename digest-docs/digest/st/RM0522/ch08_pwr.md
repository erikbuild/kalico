# RM0522 Chapter 8: Power control (PWR)

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 224–250.

## 8.1 PWR introduction

The power controller manages the device power supplies and power modes transitions.

## 8.2 PWR main features

The power controller (PWR) main features are:

- Power supplies and supply domains
  - Core domain (VCORE)
  - VDD domain
  - RTC domain (VRTC)
  - Analog domain (VDDA)
  - VDDUSB for USB transceiver
- System supply voltage regulation
  - Linear voltage regulator (LDO)
- Power supply supervision
  - POR/PDR monitor
  - PVD monitor
- Power management
  - Low-power modes
- Privileged protection

*Digest note:* although "VDDUSB for USB transceiver" is listed here, this chapter has no VDDUSB pin in Table 52, Figure 20 draws the USB transceiver on the common VDD supply line, and no PWR register contains a USB supply enable/valid bit (there is no USV/USBSV-style bit). The STM32C55xxx datasheet (Figure 2, Section 3.6.1) likewise shows the USB transceiver supplied from VDD; its Table 68 gives VDDUSB = 3.0 to 3.6 V as the USB transceiver operating supply.

## 8.3 PWR pins and internal signals

**Table 52. PWR input/output pins**

| Pin name | Signal type | Description |
|---|---|---|
| VDD | Supply | Main supply |
| GND | Supply | Main ground |
| VDDA | Supply | Analog peripherals supply |
| VSSA | Supply | Analog peripherals ground |
| VCAP | Supply | Logic supply (VCORE) |
| VREF+ | Supply | ADC/DAC high reference voltage |
| VREF- | Supply | ADC/DAC low reference voltage |
| WKUPx (x = 1 to 7) | Input | Wake-up pins |
| CSLEEP | Output | MCU in Sleep mode |
| CSTOP | Output | CPU in Stop modes |

*Digest note:* on STM32C55xxx the number of WKUP pins depends on the package (3 on 32-pin, 4 on 48-pin, 6 on 64/80-pin, 7 on 100-pin; datasheet Table 1). CSLEEP and CSTOP are PC2 AF0 (PWR_CSLEEP) and PC3 AF0 (PWR_CSTOP) in the datasheet pinout.

**Table 53. PWR internal input/output signals**

| Internal signal name | Signal type | Description |
|---|---|---|
| WKUPx (x = 1 to 7) | Input | Wake-up event source |

## 8.4 PWR power supplies and supply domains

**Figure 20. Power supply** (described)

- Device pins VSS, VDD and VCAP are on the left.
- VDDA domain (supplied from the VDD line): A/D converters, D/A converter, Comparator, Operational amplifier.
- USB transceiver: a separate block, also tapped from the VDD supply line.
- VDD domain (supplied from VDD, ground VSS): the VDDIO I/O ring; Reset block and Internal RC oscillators; Standby circuitry (Wake-up logic, IWDG), LSE crystal 32 kHz oscillator, Backup registers, RCC_RTCCR register, RTC, TAMP; and the Voltage regulator block containing the LDO regulator.
- The LDO regulator output is connected to the VCAP pin and produces VCORE.
- Core domain (supplied by VCORE): Core, SRAM1, SRAM2, Digital peripherals. Flash memory is also supplied by VCORE.

### 8.4.1 External power supplies

The devices require a 2.7 to 3.6 V operating voltage supply VDD:

- VDD = 2.7 to 3.6 V
  VDD is the external power supply for the I/Os, the internal regulator, and the system analog (such as reset, power management, and internal clocks). It is provided externally through the VDD pins.
- VDDA = 2.7 V (ADCs, DAC, COMP, and OPAMP) to 3.6 V
  VDDA is the external analog power supply for A/D converters, D/A converters, operational amplifier, and the analog comparator. The VDDA voltage domain is physically connected to the VDD voltage.
- VCAP = 0.9 to 1.25 V: digital core domain supply
  This power supply is independent from all the other power supplies:
- VRTC = 2.7 to 3.6 V
  VRTC is the power supply for RTC, external clock 32 kHz oscillator, and backup registers. The VRTC voltage level is physically connected to the VDD voltage.
- VREF-, VREF+
  VREF+ is the input reference voltage for ADCs and DAC.
  VREF+ can be grounded when ADC and DAC are not active.
  VREF- and VREF+ pins are not available on all packages. When not available, they are bonded to VSS and VDD, respectively.
  VREF- must always be equal to VSSA.

*Digest note:* the VCAP item ends with a colon in the source and no following list.

### 8.4.2 Internal regulator

The devices embed an LDO regulator to provide the VCORE supply for digital peripherals, SRAMs, and embedded flash memory. The LDO generates this voltage on VCAP, with a total external capacitance of 2.2 μF (typical). The LDO regulator is always enabled in Run mode and Stop mode, generating Vcore at 1.2 V in Run and Stop 0 mode and at 0.95 V in Stop 1 mode.

### 8.4.3 Independent analog peripherals supply

To improve ADC and DAC conversion and OPAMP accuracy, the analog peripherals have an independent power supply that can be filtered and shielded from noise on the PCB:

- The voltage supply input of the analog peripherals is available on VDDA pin.
- An isolated supply ground connection is provided on the VSSA pin.

#### ADC and DAC reference voltage

To ensure a better accuracy on low-voltage inputs and outputs, the user can connect to VREF+, a separate reference voltage lower than VDDA. VREF+ is the highest voltage, represented by the full-scale value, for an analog input (ADC) or output (DAC) signal.

Note: The VREF+ and VREF- pins are not available on all packages. When not available, they are internally connected, respectively to VDD and VSS).

*Digest note:* OPAMP is not present on STM32C55xxx (the datasheet lists ADC1, ADC2, DAC1 and COMP1 as the analog peripherals).

### 8.4.4 RTC domain

To retain the content of the backup registers and to supply the RTC function when the device enters Standby mode.

The RTC domain powers the RTC unit and the LSE oscillator, allowing the RTC to operate even when the core supply domain is switched off.

#### RTC domain access

After a system reset, the RTC domain (RCC RTC domain control register RCC_RTCCR, RTC registers, TAMP registers, and backup registers) is protected against possible unwanted write accesses. To enable access to the RTC domain, set the DRTCP bit in PWR_RTCCR.

*Digest note:* the first paragraph is an incomplete sentence in the source. DRTCP (PWR_RTCCR bit 0, offset 0x024) is the equivalent of the DBP bit found in other STM32 families; there is no bit named DBP in this PWR.

## 8.5 PWR system supply voltage regulation

### 8.5.1 Embedded voltage regulator operating modes

There are three different power modes: Run, Stop mode (Stop 0 and Stop 1), and Standby modes.

#### Run mode

The voltage regulator provides full power to the VCORE domain (core, memories, and digital peripherals). The regulator output voltage is 1.2 V and is stabilized thanks the VCAP capacitance.

#### Stop mode

The voltage regulator supplies the VCORE domain to retain the content of registers and internal memories. The regulator under Stop 1 mode is configured to output 0.95 V to VCORE domain.

#### Standby mode

The regulator is OFF and the VCORE domain is powered down. The content of the registers and memories is lost except for the Standby circuitry in the RTC domain.

*Digest note:* this chapter defines no Run-mode voltage scaling: VCORE is fixed at 1.2 V in Run, and no PWR register has a VOS (voltage scaling selection) field or a VOSRDY-style ready flag. The only regulator voltage change is the Stop 1 retention voltage. The Stop 1 value is given as 0.95 V in Sections 8.4.2 and 8.5.1 but as 0.9 V in Section 8.7, Section 8.7.6 and Table 59.

## 8.6 PWR power supply and temperature supervision

Power supply level monitoring is available on the following supplies:

- VDD via POR/PDR (see Section 8.6.1) and PVD monitor (see Section 8.6.2)
- Temperature monitoring (see Section 21.4.30)

### 8.6.1 Power-on reset (POR)/power-down reset (PDR)

The system has an integrated POR/PDR circuitry that ensures proper startup operation.

The system remains in reset mode when VDD is below a specified VPOR threshold, without the need for an external reset circuit. Once the supply level is above the VPOR threshold, the system is taken out of reset (see figure below). For more details concerning the reset thresholds refer to the electrical characteristics section of the datasheets.

**Figure 21. Power-on (POR) / power-down (PDR) reset waveform** (described)

- VDD ramps up, stays high, then ramps down. Two thresholds are drawn: VPOR (rising edge) and a lower VPDR (falling edge); the gap between them is the hysteresis.
- Reset is asserted while VDD is below VPOR. After VDD crosses VPOR on the rising edge, reset is released after a temporization tRSTTEMPO.
- When VDD falls below VPDR on the falling edge, reset is asserted again.

Notes:

1. For thresholds and hysteresis values refer to the datasheets.

### 8.6.2 Programmable voltage detector (PVD)

The PVD can be used to monitor the VDD power supply by comparing it to a defined threshold.

The PVD is enabled by setting the PVDE bit in PWR_VMCR.

A PVDO flag is available in PWR_VMSR to indicate if VDD voltage is higher or lower than the PVD threshold. This event is internally connected to the EXTI and can generate an interrupt, provided it has been enabled through the EXTI registers. The rising/falling edge sensitivity of the EXTI line must be configured according to PVD output behavior. As an example, if the EXTI line is configured to rising edge sensitivity, the interrupt is generated when VDD voltage drops below the PVD threshold. The service routine can then start an emergency shutdown.

**Figure 22. PVD thresholds** (described)

- VDD ramps up, stays high, then ramps down. Two thresholds are drawn: PVDrise (upper) and PVD fall (lower), separated by a hysteresis.
- PVDE is set by "SW enable" while VDD is still ramping up below PVDrise; at that point PVDO goes to 1 (VDD below threshold).
- When VDD rises above PVDrise, PVDO goes to 0.
- When VDD falls below PVD fall, PVDO goes to 1.
- Later, as VDD keeps falling, a "PDR reset" clears PVDE.

Notes:

1. For thresholds and hysteresis values, refer to the product datasheet.

## 8.7 Power modes

By default, the microcontroller is in Run mode after a system or a power reset. Three low-power modes are available to reduce consumption when there is no need to keep the CPU running, for example when waiting for an external event. The user can select the mode that gives the best compromise between low-power consumption, short startup time, and wake-up sources.

The device features the following low-power modes:

- Sleep mode
  CPU clock off, peripherals such as NVIC and SysTick can run and wake up the CPU when an interrupt or an event occurs. Refer to Section 8.7.4.
- Stop 0 and Stop 1 modes
  Achieve the lowest power consumption, while retaining the content of SRAM and registers. All clocks in the core domain are stopped. The HSE crystal oscillators, HSI (except if HSIKERON is set), PSI (except if PSIKERON is set) are disabled. The LSE or LSI is still running. Under Stop 0, the LDO regulator supplies VCORE at 1.2 V while under Stop 1 VCORE voltage is decreased down to 0.9 V. Consequently wake up sources are reduced and wake up time increased, refer to Section Table 54.
  The RTC can remain active (Stop mode with RTC, Stop mode without RTC).
  When exiting from Stop mode, the system clock is HSI clock at 144 MHz or 48 MHz based STOPWUCK value.
  Refer to Section 8.7.5.
- Standby mode
  This mode achieves the lowest power consumption. The internal regulator is switched off so that the core domain is powered off. The HSI, PSI, and the HSE crystal oscillators are also switched off.
  The RTC can remain active (Standby mode with RTC, Standby mode without RTC).
  The power-on reset and power-down reset (POR/PDR) remains active.
  The state of the I/O (except I/Os used by Standby mode) during Standby mode can be retained.
  After entering Standby mode, SRAMs and register contents are lost except for registers in the RTC domain and Standby circuitry.
  The device exits Standby mode when an external reset (NRST pin), an IWDG reset, WKUP pin event (configurable rising or falling edge), an RTC event occurs (alarm, periodic wake-up, timestamp), or a tamper detection. The tamper detection can be raised either due to external pins or due to an internal failure detection.
  The system clock after wake-up is HSI at 48 MHz.

*Digest note:* HSIKERON, PSIKERON and STOPWUCK are RCC bits (RCC chapter). The STM32C55xxx datasheet (Section 3.6.3) states that the system clock after Standby wake-up is HSI 144 MHz, which contradicts the 48 MHz given here and in Table 54.

The table below shows the power modes overview.

**Table 54. Low-power mode summary**

| Mode name | Entry | Wake-up source (1) | Wake-up system clock | Effect on clocks |
|---|---|---|---|---|
| Sleep (Sleep-now or Sleep-on-exit) | WFI or Return from ISR | Any interrupt | Same as before entering Sleep mode | CPU clock OFF; No effect on other clocks or analog clock sources |
| Sleep (Sleep-now or Sleep-on-exit) | WFE | Wake-up event | Same as before entering Sleep mode | CPU clock OFF; No effect on other clocks or analog clock sources |
| Stop 0 | LPMS = 00 + SLEEPDEEP bit + WFI or Return from ISR or WFE | Any EXTI line (configured in the EXTI registers); Specific peripherals events (2) | HSI clock at 144 MHz or 48 MHz based STOPWUCK value | All clocks OFF except LSI and LSE; HSI or PSI can be enabled temporarily when requested by software or kept ON thanks to HSIKERON/PSIKERON bits |
| Stop 1 | LPMS = 01 + SLEEPDEEP bit + WFI or Return from ISR or WFE | Any GPIO EXTI line and EXTI from PVD, COMP, RTC, LPUART or LPTIM (configured in the EXTI registers) | HSI clock at 144 MHz or 48 MHz based STOPWUCK value | All clocks OFF except LSI and LSE |
| Standby | LPMS = 10 + SLEEPDEEP bit + WFI or Return from ISR or WFE | WKUP pin edge, RTC event, IWDG reset, external reset in NRST pin | HSI clock at 48 MHz | All clocks OFF except LSI and LSE |

Notes:

1. Refer to Table 55.
2. Peripherals able to wake up the system from Stop mode.

**Table 55. Functionalities depending on the working mode (1)**

Columns: Run; Sleep; Stop – Available; Stop – Wake-up capability in Stop 0; Stop – Wake-up capability in Stop 1; Standby – Available; Standby – Wake-up capability.

| Peripheral | Run | Sleep | Stop: Available | Stop: Wake-up Stop 0 | Stop: Wake-up Stop 1 | Standby: Available | Standby: Wake-up capability |
|---|---|---|---|---|---|---|---|
| CPU | Y | - | - | - | - | - | - |
| Flash memory | O | O | - (2) | - | - | - | - |
| SRAM1 | Y (3) | Y (3) | Y | - | - | - | - |
| SRAM2 | Y (3) | Y (3) | Y | - | - | - | - |
| Backup registers | Y | Y | Y | Y | Y | Y | - |
| XSPI1 | O | O | - | - | - | - | - |
| Programmable voltage detector (PVD) | O | O | O | O | O | - | - |
| LPDMA | O | O | - | - | - | - | - |
| High-speed internal (HSI) | O | O | - | - | - | - | - |
| Programmable-speed internal (PSI) | O | O | - | - | - | - | - |
| High-speed external (HSE) | O | O | - | - | - | - | - |
| Low-speed internal (LSI) | O | O | O | O | - | O | - |
| Low-speed external (LSE) | O | O | O | - | - | O | - |
| Clock security system (CSS) | O | O | - | - | - | - | - |
| Clock security system on LSE | O | O | O | O | O (4) | O | O |
| RTC domain voltage | O | O | O | O | O (5) | O | O |
| RTC/TAMP | O | O | O | O | O | O | O |
| Number of TAMP tamper pins | 3 | 3 | 3 | - | - | 3 | - |
| USB FS | O | O | O | O | - | - | - |
| USARTx / UARTx | O | O | O | O | - | - | - |
| Low-power UART (LPUART) | O | O | O | O | O | - | - |
| I2Cx (x = 1, 2) | O | O | O | O | - | - | - |
| I3C1 | O | O | O | O | - | - | - |
| SPIx (x = 1 to 3) | O | O | O | O | - | - | - |
| FDCANx (x = 1, 2) | O | O | - | - | - | - | - |
| ETH1 | O | O | O | O | - | - | - |
| ADCx (x = 1 to 3) | O | O | - | - | - | - | - |
| DAC1 (OUT1, OUT2) | O | O | O | - | - | - | - |
| COMPx (x = 1, 2) | O | O | O | O | O | - | - |
| OPAMP1 | O | O | - | - | - | - | - |
| Timers (TIMx) | O | O | - | - | - | - | - |
| Low-power timer LPTIM1 | O | O | O | O | O | - | - |
| Independent watchdog (IWDG) | O | O | O | O | O | O | O |
| Window watchdog (WWDG) | O | O | - | - | - | - | - |
| SysTick timer (SYSTICK) | O | O | O | - | - | - | - |
| CORDIC coprocessor (CORDIC) | O | O | - | - | - | - | - |
| Random number generator (RNG) | O | O | - | - | - | - | - |
| AES/SAES | O | O | - | - | - | - | - |
| HASH accelerator | O | O | - | - | - | - | - |
| Public key accelerator (PKA) | O | O | - | - | - | - | - |
| CCB | O | O | - | - | - | - | - |
| CRC calculation unit | O | O | - | - | - | - | - |
| GPIOs | O | O | - | - | - | O (5) | O (6) |
| EXTI | O | O | O | O | O | - | - |

Notes:

1. Y = yes (enabled). O = optional (disabled by default, can be enabled by software). - = not available. HSI or PSI are available as kernel clock for peripherals only in STOP 0.
2. The memory can be configured in low-power mode. By default, it is not in Low-power mode during Stop.
3. The SRAM clock can be gated on or off independently. By default clock is enabled in Run and Sleep modes.
4. Wake-up with internal tamper.
5. GPIOs state can be retained during Standby mode. By default GPIOs states are not retained.
6. 7 pins are capable of wake-up from Standby mode: PA0, PA2, PB7, PC1, PC13, PD2, and PE6.

*Digest note:* footnote (5) is attached to the "RTC domain voltage" Stop 1 cell as printed, although its text concerns GPIO retention; the marker there looks misplaced. Per the STM32C55xxx datasheet, the following rows of this series-wide table do not apply to STM32C551/C552: XSPI1, ETH1, OPAMP1, AES/SAES, PKA, CCB, FDCAN2 (FDCAN1 is present only on STM32C552), ADC3 (only ADC1 and ADC2), DAC1 OUT2 (only DAC1_OUT1), and COMP2 (one comparator). STM32C55xxx have 2 tamper pins on 32-pin packages and 3 on the others, and 3 to 7 wake-up pins depending on package.

In addition, the power consumption in Run mode can be reduced by slowing down the system clocks and by gating the clocks to the APB and AHB peripherals when they are not used.

#### Debug mode

By default, the debug connection is lost if the application puts the MCU in Stop or Standby mode while the debug features are used. This is due to the fact that the Cortex-M33 core is no longer clocked.

However, by setting some configuration bits in the DBGMCU control registers, the software can be debugged even when using the low-power modes extensively. For more details, refer to Section 49.2.5: Debug and low-power modes.

### 8.7.1 Slowing down system clocks

In Run mode, the speed of the system clocks (SYSCLK, HCLK, PCLK) can be reduced by programming the prescaler registers. These prescalers can also be used to slow down the peripherals before entering the Sleep mode.

For more details, refer to Section 9: Reset and clock control (RCC).

### 8.7.2 Peripheral clock gating

In Run mode, the HCLK and PCLK for individual peripherals and memories can be stopped at any time to reduce the power consumption.

To further reduce the power consumption in Sleep mode, or Stop 0 mode the peripheral clocks can be disabled before executing the WFI or WFE instructions.

The peripheral clock gating is controlled by the RCC_AHBxENR and RCC_APBxENR registers.

Disabling the peripheral clocks in Sleep mode or Stop 0 mode can be performed automatically by resetting the corresponding bit in the RCC_AHBxLPENR and RCC_APBxLPENR registers.

### 8.7.3 Low-power modes

#### Entering into a low-power mode

The MCU enters in low-power modes by executing the WFI (wait for interrupt), or WFE (wait for event) instructions, or when the SLEEPONEXIT bit in the Cortex-M33 system control register is set on return from ISR.

Entering into a low-power mode through WFI or WFE is executed only if no interrupt is pending or no event is pending.

#### Exiting a low-power mode

The MCU exits the Sleep or Stop mode according to how the low-power mode was entered:

- If the WFI instruction or return from ISR was used to enter the low-power mode, any peripheral interrupt acknowledged by the NVIC can wake up the device.
- If the WFE instruction is used to enter the low-power mode, the MCU exits the low-power mode as soon as an event occurs. The wake-up event can be generated either by:
  - An NVIC IRQ interrupt:
    - When SEVONPEND = 0 in the Cortex-M33 system control register
      By enabling an interrupt in the peripheral control register and in the NVIC. When the MCU resumes from WFE, the peripheral interrupt pending bit and the NVIC peripheral IRQ channel pending bit (in the NVIC interrupt clear pending register) must be cleared. Only NVIC interrupts with high enough priority can wake up and interrupt the MCU.
    - When SEVONPEND = 1 in the Cortex-M33 system control register
      By enabling an interrupt in the peripheral control register and optionally in the NVIC. When the MCU resumes from WFE, the peripheral interrupt pending bit and when enabled the NVIC peripheral IRQ channel pending bit (in the NVIC interrupt clear pending register) must be cleared. All NVIC interrupts wake up the MCU, even the disabled ones. Only enabled NVIC interrupts with high enough priority can wake up and interrupt the MCU.
  - An event:
    - Configuring an EXTI line in event mode. When the CPU resumes from WFE, it is not necessary to clear the EXTI peripheral interrupt pending bit or the NVIC IRQ channel pending bit, as the pending bits corresponding to the event line are not set. It may be necessary to clear the interrupt flag in the peripheral.

The MCU exits Standby mode through an external reset (NRST pin), an IWDG reset, a rising edge on one of the enabled WKUPx pins or a RTC/TAMP event (see Figure 561: RTC block diagram).

After waking up from Standby mode, the program execution restarts in the same way as after a reset (boot pin sampling, option bytes loading, reset vector is fetched).

Caution: When the device is in Stop 0 mode, a peripheral interrupt powers on an internal oscillator. The corresponding NVIC interrupt channel must be enabled to allow the interrupt to exit the device from Stop mode. It is not allowed to disable a peripheral interrupt by disabling only the NVIC channel while keeping the peripheral interrupt enable, as the device could remain in Stop mode with clock ON.

### 8.7.4 Sleep mode

#### I/O states in Sleep mode

In Sleep mode, all I/O pins keep the same state as in Run mode.

#### Entering the Sleep mode

The MCU enters the Sleep mode as described in Entering into a low-power mode, when the SLEEPDEEP bit in the Cortex-M33 system control register is clear (see the table below for details on how to enter the Sleep mode).

#### Exiting the Sleep mode

The MCU exits the Sleep mode as described in Exiting a low-power mode (see the table below for details on how to exit the Sleep mode).

**Table 56. Sleep mode**

| Sleep mode | Description |
|---|---|
| Mode entry | WFI (wait for interrupt) or WFE (wait for event) while: SLEEPDEEP = 0; No interrupt (for WFI) or event (for WFE) pending. Refer to the Cortex-M33 system control register. |
| Mode entry | On return from ISR while: SLEEPDEEP = 0 and SLEEPONEXIT = 1; No interrupt pending. Refer to the Cortex-M33 system control register. |
| Mode exit | If WFI or Return from ISR was used for entry: Interrupt (see Table 100: STM32C5 vector table). If WFE was used for entry and SEVONPEND = 0: Wake-up event (see Section 16.3: EXTI functional description). If WFE was used for entry and SEVONPEND = 1: Interrupt even when disabled in NVIC (see Table 100: STM32C5 vector table) or wake-up event (see Section 16.3: EXTI functional description). |
| Wake-up latency | None |

### 8.7.5 Stop 0 mode

The Stop 0 mode is based on the Cortex-M33 Deepsleep mode combined with the peripheral clock gating. In Stop mode, all clocks in the core domain are stopped. The HSI, PSI, and HSE oscillators are disabled.

It is possible to keep the HSI or PSI clock enabled during Stop mode, to be quickly available as kernel clock for peripherals.

All register contents are preserved. SRAMs can be preserved or powered down, depending on the SRAMxPDSx bits in PWR_PMCR.

**Table 57. Memory power down block selection**

| Selection bit | Power down block in Stop mode: STM32C53x/542 | Power down block in Stop mode: STM32C55x/562 | Power down block in Stop mode: STM32C59x/5A3 |
|---|---|---|---|
| SRAM1PDS | SRAM1 block from 0 to 32 Kbytes | SRAM1 block from 0 to 64 Kbytes | SRAM1 block from 0 to 128 Kbytes |
| SRAM2PDS1 | SRAM2 block from 0 to 16 Kbytes | SRAM2 block from 0 to 16 Kbytes | SRAM2 block from 0 to 16 Kbytes |
| SRAM2PDS2 | SRAM2 block from 16 to 32 Kbytes | SRAM2 block from 16 to 64 Kbytes | SRAM2 block from 16 to 64 Kbytes |
| SRAM2PDS3 | - | - | SRAM2 block from 64 to 128 Kbytes |

*Digest note:* for STM32C551/C552 use the STM32C55x/562 column; SRAM2PDS3 does not apply.

The power-down reset is always available in Stop 0 mode.

#### I/O states in Stop 0 mode

In the Stop 0 mode, all I/O pins keep the same state as in the Run mode.

#### Entering the Stop 0 mode

The MCU enters the Stop mode as described in Entering into a low-power mode, when the SLEEPDEEP bit in the Cortex-M33 system control register is set (see Table 54 for details on how to enter the Stop mode).

If the flash memory programming is ongoing, the Stop mode entry is delayed until the memory access is finished.

If an access to the APB domain is ongoing, the Stop mode entry is delayed until the APB access is finished.

In Stop 0 mode, the following features can be selected by programming the individual control bits:

- The independent watchdog (IWDG) is started by writing to its key register or by hardware option. Once started, it can be stopped only by a reset (see Section 37.4: IWDG functional description).
- The real-time clock (RTC) is configured by the RTCEN bit in RCC_RTCCR.
- The internal RC oscillator LSI clock is configured by the LSION bit in RCC_RTCCR.
- The external 32.768 kHz oscillator (LSE) is configured by the LSEON bit in RCC_RTCCR.

The PVD can be used in Stop mode. If not needed, it must be disabled by software to save power consumption.

The ADCx (x = 1 to 3) and the DAC1 can consume power during the Stop mode, unless they are disabled before entering this mode.

#### Exiting the Stop 0 mode

The MCU exits Stop mode by enabling an EXTI interrupt or event depending on how the low-power mode was entered. Some peripherals are able to wake up the system (refer to Table 103: EXTI line connections) from Stop mode.

When exiting Stop 0 mode by issuing an interrupt or a wake-up event, HSI is selected as system clock. The MCU exits Stop 0 mode by enabling an EXTI interrupt or event depending on how the low-power mode was entered.

**Table 58. Stop 0 mode**

| Stop mode | Description |
|---|---|
| Mode entry | WFI (wait for interrupt) or WFE (wait for event) while: SLEEPDEEP bit is set in Cortex-M33 system control register; No interrupt (for WFI) or event (for WFE) pending; LPMS = 00 in PWR_CR1. |
| Mode entry | On Return from ISR while: SLEEPDEEP bit is set in Cortex-M33 system control register; SLEEPONEXIT = 1; No interrupt pending; LPMS = 00 in PWR_PMCR. Note: To enter Stop 0 mode, all EXTI line pending bits (in Section 16.6.4: EXTI rising edge pending register (EXTI_RPR1) and Section 16.6.10: EXTI rising edge pending register 2 (EXTI_RPR2)), and the peripheral flags generating wake-up interrupts must be cleared. Otherwise, the Stop 0 mode entry procedure is ignored and the program execution continues. |
| Mode exit | If WFI or Return from ISR was used for entry: any EXTI line configured in interrupt mode (the corresponding EXTI interrupt vector must be enabled in the NVIC). The interrupt source can be external interrupts or peripherals with wake-up capability (see Table 100: STM32C5 vector table); any peripheral interrupt occurring when the AHB/APB clocks are present due to an autonomous peripheral clock request (the peripheral vector must be enabled in the NVIC). If WFE was used for entry and SEVONPEND = 0: any EXTI line configured in event mode (see Section 16.3: EXTI functional description). If WFE was used for entry and SEVONPEND = 1: any EXTI line configured in interrupt mode (even if the corresponding EXTI interrupt vector is disabled in the NVIC). The interrupt source can be external interrupts or peripherals with wake-up capability (see Table 100: STM32C5 vector table); any EXTI line is configured in event mode (see Section 16.3: EXTI functional description). Note: All peripheral clocks must be enabled to allow this peripheral to generate a wake-up from Stop interrupt ([PERIPH]EN and [PERIPH]LPEN bits must be set in the RCC, and a functional independent clock must be selected). |
| Wake-up latency | Longest wake-up time between: HSI wake-up time and flash memory wake-up time from Stop mode. |

*Digest note:* "PWR_CR1" in the mode-entry row is printed as is; this PWR has no PWR_CR1 register, and LPMS is in PWR_PMCR.

### 8.7.6 Stop 1 mode

The Stop 1 mode is based on the Cortex-M33 Deep sleep mode combined with the peripheral clock gating. In comparison to Stop 0, the voltage regulator is configured to Low voltage retention at 0.9 V. All clocks in the core domain are stopped. The HSI, PSI, and HSE oscillators are disabled.

All register contents are preserved. SRAMs can be preserved or powered down, depending on SRAMxPDSx bits in PWR_PMCR. Refer to Table 57: Memory power down block selection for details.

The power-down reset is always available in Stop mode.

#### I/O states in Stop 1 mode

In the Stop mode, all I/O pins keep the same state as in the Run mode.

#### Entering the Stop 1 mode

The MCU enters the Stop 1 mode as described in Entering into a low-power mode, when the SLEEPDEEP bit in the Cortex-M33 system control register is set (see Table 54 for details on how to enter the Stop mode).

If the flash memory programming is ongoing, the Stop 1 mode entry is delayed until the memory access is finished.

If an access to the APB domain is ongoing, the Stop 1 mode entry is delayed until the APB access is finished.

In Stop 1 mode, the following features can be selected by programming the individual control bits:

- The independent watchdog (IWDG) is started by writing to its key register or by hardware option. Once started, it can be stopped only by a reset (see Section 37.4: IWDG functional description).
- The real-time clock (RTC) is configured by the RTCEN bit in RCC_RTCCR.
- The internal RC oscillator LSI clock is configured by the LSION bit in RCC_RTCCR.
- The external 32.768 kHz oscillator (LSE) is configured by the LSEON bit in RCC_RTCCR.

The PVD can be used in Stop mode. If not needed, it must be disabled by software to save power consumption.

The ADCx (x = 1 to 3) and the DAC1 can consume power during the Stop 1 mode, unless they are disabled before entering this mode.

#### Exiting the Stop 1 mode

The MCU exits Stop mode by enabling an EXTI interrupt or event depending on how the low-power mode was entered.

When exiting Stop mode by issuing an interrupt or a wake-up event, HSI is selected as system clock. The MCU exits Stop 1 mode by enabling an EXTI interrupt or event depending on how the low-power mode was entered.

**Table 59. Stop 1 mode**

| Stop mode | Description |
|---|---|
| Mode entry | WFI (wait for interrupt) or WFE (wait for event) while: SLEEPDEEP bit is set in Cortex-M33 system control register; No interrupt (for WFI) or event (for WFE) pending; LPMS = 01 in PWR_CR1. |
| Mode entry | On Return from ISR while: SLEEPDEEP bit is set in Cortex-M33 system control register; SLEEPONEXIT = 1; No interrupt pending; LPMS = 01 in PWR_PMCR. Note: To enter Stop mode, all EXTI line pending bits (in Section 16.6.4: EXTI rising edge pending register (EXTI_RPR1) and Section 16.6.10: EXTI rising edge pending register 2 (EXTI_RPR2)), and the peripheral flags generating wake-up interrupts must be cleared. Otherwise, the Stop mode entry procedure is ignored and the program execution continues. |
| Mode exit | If WFI or Return from ISR was used for entry: any GPIO EXTI line configured in interrupt mode (the corresponding EXTI interrupt vector must be enabled in the NVIC). The interrupt source must be external interrupts with wake-up capability (see Table 100: STM32C5 vector table). If WFE was used for entry and SEVONPEND = 0: any GPIO EXTI line configured in event mode (see Section 16.3: EXTI functional description). If WFE was used for entry and SEVONPEND = 1: any GPIO EXTI line configured in interrupt mode (even if the corresponding EXTI interrupt vector is disabled in the NVIC). The interrupt source must be external interrupts with wake-up capability (see Table 100: STM32C5 vector table); any GPIO EXTI line is configured in event mode (see Section 16.3: EXTI functional description). |
| Wake-up latency | Longest wake-up time between: HSI wake-up time, regulator stabilization from 0.9 V to 1.2 V and flash memory wake-up time from Stop mode. |

*Digest note:* as in Table 58, "PWR_CR1" is printed as is; LPMS is in PWR_PMCR.

### 8.7.7 Standby mode

The lowest power mode in which the POR/PDR is active is the Standby mode. It is based on the Cortex-M33 Deepsleep mode, with the voltage regulators disabled. The HSI, PSI, and HSE oscillators are also switched off.

The SRAMs and register contents are lost except for registers in the backup domain and Standby circuitry (see Figure 23).

#### I/O states in Standby mode

In the Standby mode, the I/Os are by default in floating state. If the IORETEN bit in the PWR_IORETR register is set, the I/Os output state is retained. I/O retention mode is enabled for all I/Os except those supporting the standby functionality and JTAG I/Os (PA13, PA14, PA15, and PB4). When entering into Standby mode, the state of the output is sampled, and pull-up or pull-down resistors are set to maintain the I/O output during Standby mode.

If the JTAGIORETEN bit in the PWR_IORETR register is set, the I/Os output state is retained. I/O retention mode is enabled for PA13, PA14, PA15, and PB4 (default JTAG pull-up/pull-down after wake-up is not enabled).

**Figure 23. I/O states in Standby mode** (described)

Two timing diagrams, each with the rows GPIO mode, System mode, Standby entry, IORETEN (PWR) and Wakeup request.

- IO state retention disabled: IORETEN stays low. GPIO mode is Normal while the system is in Run; at Standby entry (WFI/WFE/Sleep on exit) the system goes to Standby (Vcore off) and the GPIOs become Floating; on a wakeup request the system returns to Run and the GPIOs are Normal (default after reset).
- IO state retention enabled: IORETEN is set before Standby entry. GPIO mode is Normal in Run; at Standby entry the system goes to Standby (Vcore off) and the GPIOs are in "State retained (PU/PD)"; after the wakeup request the system returns to Run but the GPIOs stay in "State retained (PU/PD)" until software clears IORETEN, after which GPIO mode is Normal.

After wake-up from Standby mode, as long as IORETEN (or JTAGIORETEN for JTAG I/Os) is set, the retained state (pull-up/pull-down) remains applied.

The GPIO pin state before standby can be identified with GPIO_IDR register (when both GPIO port clock and input buffer are enabled).

The application can release the I/O state (clear the retained Pull-up/Pull-down) by clearing the IORETEN (or JTAGIORETEN for JTAG I/Os) bit, before or after reconfiguring the GPIOs and related peripherals. The GPIOs can then be configured in a known state before releasing the retained state.

The RTC output on PC13 is functional in Standby mode. PC14 and PC15 used for LSE are also functional. Up to seven wake-up (WKUPx, x = 1 to 7) and three RTC tamper pins are available.

#### Entering Standby mode

The MCU enters the Standby mode as described in Entering into a low-power mode, when the SLEEPDEEP bit in the Cortex-M33 system control register is set (see Table 60 for details on how to enter Standby mode).

In Standby mode, the following features can be selected by programming individual control bits:

- The independent watchdog (IWDG) is started by writing to its Key register or by hardware option. Once started, it can be stopped only by a reset (see Section 37.4: IWDG functional description).
- The real-time clock (RTC) is configured by the RTCEN bit in RCC_RTCCR.
- The internal RC oscillator LSI clock is configured by the LSION bit in RCC_RTCCR.
- The external 32.768 kHz oscillator (LSE) is configured by the LSEON bit in RCC_RTCCR.
- The I/Os retention is configured by the IORETEN bit in the PWR_IORETR register.

#### Exiting Standby mode

The MCU exits the Standby mode as described in Exiting a low-power mode. The SBF status flag in PWR_PMSR) indicates that the MCU was in Standby mode. All registers are reset after wake-up from Standby except for PWR_RTCCR and PWR_IORETR (see Table 60 for more details on how to exit Standby mode).

When exiting Standby mode, I/Os output state that were retained during Standby through IORETEN bit, keep this configuration upon exiting Standby mode until the IORETEN bit in PWR_IORETR register is cleared. Once IORETEN is cleared, the I/Os are configured to their reset values, or to the pull-up/pull-down state according to the GPIOx_PUPDR registers.

For I/Os, with a pull-up or pull-down predefined after reset (some JTAG/SWD I/Os), in case those pull-up or pull-downs are different from the retained values during Standby, both a pull-down and pull-up are applied until IORETEN is cleared, releasing the retained value.

Also in case the GPIOx_PUPDR values programed after exiting from Standby are different from the retained values during Standby, both a pull-down and pull-up are applied until IORETEN is cleared, releasing the retained value.

**Table 60. Standby mode**

| Standby mode | Description |
|---|---|
| Mode entry | WFI (wait for interrupt) or WFE (wait for event) while: SLEEPDEEP bit is set in Cortex-M33 system control register; No interrupt (for WFI) or event (for WFE) pending; LPMS = 10 in PWR_PMCR; WUFx bits cleared in PWR_WUSR. |
| Mode entry | On Return from ISR while: SLEEPDEEP bit is set in Cortex-M33 system control register; SLEEPONEXIT = 1; No interrupt pending; LPMS = 10 in PWR_PMCR; WUFx bits cleared in PWR_WUSR; RTC/TAMP flags corresponding to the chosen wake-up source, cleared. |
| Mode exit | WKUPx pin edge, RTC event, external reset in NRST pin, IWDG reset |
| Wake-up latency | Reset phase |

*Digest note:* per "Exiting Standby mode" above, PWR_RTCCR (holding DRTCP) and PWR_IORETR keep their values across a Standby wake-up. PWR_PMSR.SBF is described as cleared only by a POR or CSSF (Section 8.10.2), so firmware can read it after the wake-up reset to detect that Standby was entered.

### 8.7.8 Power mode output pins

In order to help the debug, two signals are available as device pins alternate functions:

- CSLEEP
  When set, CSLEEP indicates that the system is in Sleep mode: WFI or WFE has been executed.
  When cleared, CSLEEP indicates that the system is in Run mode.
- CSTOP
  When set, CSTOP indicates that the system is in Stop mode, meaning that the following conditions are fulfilled:
  - WFI or WFE has been executed with CPU SLEEPDEEP = 1.
  - No AHB/APB clock is running.

  When cleared, CSTOP indicates that the system is not in Stop mode: AHB/APB clocks are running.

The table below explains the MCU power mode depending on these signal states.

**Table 61. Power mode output states versus MCU power modes**

| CSLEEP | CSTOP | MCU power modes (1) |
|---|---|---|
| 0 | 0 | Run mode |
| 1 | 0 | Sleep mode |
| 1 | 1 | Stop mode |

Notes:

1. CSLEEP and CSTOP are generated in core domain, consequently they are not driven in Standby mode.

## 8.8 PWR privileged protection

By default, after a reset, all registers can be read or written with both privileged and unprivileged accesses, except PWR_PRIVCFGR, which can be written only with privileged access. PWR_PRIVCFGR can be read by privileged and unprivileged accesses.

The PRIV bit of PWR_PRIVCFGR can be written only with privileged access. It configures the privileged access of all PWR functions (defined by RCC, or GPIO).

When the PRIV bit is set in PWR_PRIVCFGR:

- The PWR bits can be written only with privileged access.
- The PWR bits can be read only with privileged access except PWR_PRIVCFGR, which can be read by privileged or unprivileged accesses.
- An unprivileged access to a privileged PWR bit or register is discarded: the bits are read as 0, and the write to these bits is ignored (RAZ/WI).

## 8.9 PWR interrupts

The table below gives a summary of the interrupt sources and the way to control them.

**Table 62. PWR interrupt requests**

| Interrupt vector | Interrupt event | Event flag | Enable control bit | Interrupt clear method | Exit Sleep, Stop mode | Exit Standby mode |
|---|---|---|---|---|---|---|
| PVD output | Programmable voltage detector through EXTI line 16 | PVDO | EXTI line 16 enabled | Write EXTI PIF16 = 1 | Yes | No |

*Digest note:* the CMSIS header stm32c552xx.h defines PWR_PVD_IRQn = 1.

## 8.10 PWR registers

The PWR registers can be accessed in word, half-word and byte format, unless otherwise specified.

For the actual availability of some peripherals/features and their related bits, check the datasheet or Table 3: Memory map and peripheral register boundary addresses. If not present, consider them as reserved, and keep them at reset value

*Digest note:* the CMSIS header stm32c552xx.h defines PWR_BASE = AHB3PERIPH_BASE + 0x0800 = 0x4402 0800 (AHB3PERIPH_BASE = 0x4402 0000).

### 8.10.1 PWR power mode control register (PWR_PMCR)

Address offset: 0x000. Reset value: 0x0000 0000.

This register is protected against unprivileged access when PRIV = 1 in PWR_PRIVCFGR register.

- **Bits 31:27** Reserved, must be kept at reset value.
- **Bit 26 SRAM1PDS** (rw): AHB SRAM1 block power down in Stop mode
  - 0: AHB RAM1 content is kept in Stop mode.
  - 1: AHB RAM1 content is lost in Stop mode.
- **Bit 25 SRAM2PDS2** (rw): AHB SRAM2 block 2 power down in Stop mode
  - 0: AHB RAM2 block 2 content is kept in Stop mode.
  - 1: AHB RAM2 block 2 content is lost in Stop mode.

  Note: For block definition, refer to Table 57: Memory power down block selection.
- **Bit 24 SRAM2PDS1** (rw): AHB SRAM2 block 1 power down in Stop mode
  - 0: AHB RAM2 block 1 content is kept in Stop mode.
  - 1: AHB RAM2 block 1 content is lost in Stop mode.

  Note: For block definition, refer to Table 57: Memory power down block selection.
- **Bit 23 SRAM2PDS3** (rw): AHB SRAM2 block 3 power down in Stop mode
  - 0: AHB RAM2 block 3 content is kept in Stop mode.
  - 1: AHB RAM2 block 3 content is lost in Stop mode.

  Note: For block definition, refer to Table 57: Memory power down block selection.
- **Bits 22:10** Reserved, must be kept at reset value.
- **Bit 9 FLPS** (rw): Flash memory low-power mode in Stop mode
  This bit is used to obtain the best trade-off between low-power consumption and restart time when exiting from Stop mode.
  When it is set, the flash memory enters low-power mode when the system is in Stop mode.
  - 0: Flash memory remains in normal mode when the system enters Stop mode (quick restart time).
  - 1: Flash memory enters low-power mode when the system enters Stop mode (low-power consumption).
- **Bit 8** Reserved, must be kept at reset value.
- **Bit 7 CSSF** (rw): Clear Standby and Stop flags (always read as 0)
  This bit is cleared to 0 by hardware.
  - 0: No effect
  - 1: STOPF and SBF flags cleared
- **Bits 6:2** Reserved, must be kept at reset value.
- **Bits 1:0 LPMS[1:0]** (rw): low-power mode selection
  This bits define the Deepsleep mode.
  - 00: Stop 0 mode when entering DeepSleep.
  - 01: Stop 1 mode when entering DeepSleep.
  - 10: Standby mode when entering DeepSleep.
  - 11: Reserved

*Digest note:* SRAM2PDS3 applies only to STM32C59x/5A3 (Table 57). The CMSIS header stm32c552xx.h names these bits differently, at the same positions: PWR_PMCR_SRAM1SO (bit 26), PWR_PMCR_SRAM2_2_SO (bit 25), PWR_PMCR_SRAM2_1_SO (bit 24); it defines nothing for bit 23.

### 8.10.2 PWR status register (PWR_PMSR)

Address offset: 0x004. Reset value: 0x0000 0000.

- **Bits 31:7** Reserved, must be kept at reset value.
- **Bit 6 SBF** (r): System standby flag
  This bit is set by hardware and cleared only by a POR or by setting the CSSF bit.
  - 0: System has not been in Standby mode.
  - 1: System has been in Standby mode.
- **Bit 5 STOPF** (r): Stop flag
  This bit is set by hardware and cleared only by any reset or by setting the CSSF bit.
  - 0: System has not been in Stop mode.
  - 1: System has been in Stop mode.
- **Bits 4:0** Reserved, must be kept at reset value.

### 8.10.3 PWR RTC domain control register (PWR_RTCCR)

Address offset: 0x24. Reset value: 0x0000 0000.

This register is protected against unprivileged access when PRIV = 1 in PWR_PRIVCFGR register.

- **Bits 31:1** Reserved, must be kept at reset value.
- **Bit 0 DRTCP** (rw): Disable RTC domain write protection
  In reset state, all registers in RTC domain are protected against parasitic write access. This bit must be set to enable write access to these registers.
  - 0: Write access to RTC domain disabled
  - 1: Write access to RTC domain enabled

### 8.10.4 PWR voltage monitor control register (PWR_VMCR)

Address offset: 0x034. Reset value: 0x0000 0000.

This register is protected against unprivileged access when PRIV = 1 in PWR_PRIVCFGR register.

The PVDE bit is protected by lock mechanism. The lock control is in the SBS module controlled by PVDL bit in SBS_CFGR2 register. By default, the PVDE is unlocked.

- **Bits 31:1** Reserved, must be kept at reset value.
- **Bit 0 PVDE** (rw): PVD enable
  - 0: PVD disabled
  - 1: PVD enabled

*Digest note:* the CMSIS header defines SBS_CFGR2_PVDL at bit 2 of SBS_CFGR2.

### 8.10.5 PWR voltage monitor status register (PWR_VMSR)

Address offset: 0x03C. Reset value: 0x00X0 0000.

- **Bits 31:23** Reserved, must be kept at reset value.
- **Bit 22 PVDO** (r): programmable voltage detect output
  This bit is set and cleared by hardware. It is valid only if the PVD has been enabled by the PVDE bit.
  - 0: VDD is equal or higher than the PVD threshold.
  - 1: VDD is lower than the PVD threshold.

  Note: Since the PVD is disabled in Standby mode, this bit is equal to 0 after Standby or reset until the PVDE bit is set.
- **Bits 21:0** Reserved, must be kept at reset value.

### 8.10.6 PWR wake-up status clear register (PWR_WUSCR)

Address offset: 0x040. Reset value: 0x0000 0000.

Each register bit CWUFx (x = 1 to 7) is protected against unprivileged access when PRIV = 1 in PWR_PRIVCFGR.

- **Bits 31:7** Reserved, must be kept at reset value.
- **Bits 6:0 CWUFx** (w): clear wake-up pin flag for WUFx (x = 7 to 1)
  These bits are always read as 0.
  - 0: No effect
  - 1: Writing 1 clears the WUFx wake-up pin flag (bit is cleared to 0 by hardware).

Bit mapping: CWUF7 (6), CWUF6 (5), CWUF5 (4), CWUF4 (3), CWUF3 (2), CWUF2 (1), CWUF1 (0).

### 8.10.7 PWR wake-up status register (PWR_WUSR)

Address offset: 0x044. Reset value: 0x0000 0000.

- **Bits 31:7** Reserved, must be kept at reset value.
- **Bits 6:0 WUFx** (r): wake-up pin WUFx flag (x = 7 to 1)
  This bit is set by hardware and cleared only by a RESET pin or by setting the CWUFx bit in PWR_WUSCR register or by hardware when WUPENx = 0.
  - 0: No wake-up event occurred.
  - 1: Wake-up event received from WUFx pin.

Bit mapping: WUF7 (6), WUF6 (5), WUF5 (4), WUF4 (3), WUF3 (2), WUF2 (1), WUF1 (0).

### 8.10.8 PWR wake-up configuration register (PWR_WUCR)

Address offset: 0x048. Reset value: 0x0000 0000.

Each WUPPUPDx (x = 1 to 7), WUPPx (x = 1 to 7), and WUPENx (x = 1 to 7) is protected against unprivileged access when PRIV = 1 in PWR_PRIVCFGR.

- **Bits 31:30** Reserved, must be kept at reset value.
- **Bits 29:16 WUPPUPDx[1:0]** (rw): Wake-up pin pull configuration for WKUPx (x = 7 to 1)
  These bits define the I/O pad pull configuration used when WUPENx = 1. The associated GPIO port pull configuration must be set to the same value or to 00. The wake-up pin pull configuration is kept in Standby mode.
  - 00: No pull-up
  - 01: Pull-up
  - 10: Pull-down
  - 11: Reserved

  Bit mapping: WUPPUPD7[1:0] (29:28), WUPPUPD6[1:0] (27:26), WUPPUPD5[1:0] (25:24), WUPPUPD4[1:0] (23:22), WUPPUPD3[1:0] (21:20), WUPPUPD2[1:0] (19:18), WUPPUPD1[1:0] (17:16).
- **Bit 15** Reserved, must be kept at reset value.
- **Bits 14:8 WUPPx** (rw): Wake-up pin polarity bit for WKUPx (x = 7 to 1)
  These bits define the polarity used for event detection on WUPx external wake-up pin.
  - 0: Detection on high level (rising edge)
  - 1: Detection on low level (falling edge)

  Bit mapping: WUPP7 (14), WUPP6 (13), WUPP5 (12), WUPP4 (11), WUPP3 (10), WUPP2 (9), WUPP1 (8).
- **Bit 7** Reserved, must be kept at reset value.
- **Bits 6:0 WUPENx** (rw): Enable wake-up pin WKUPx (x = 7 to 1)
  These bits are set and cleared by software.
  - 0: An event on WUPx pin does not wake-up the system from Standby mode.
  - 1: A rising or falling edge on WUPx pin wakes up the system from Standby mode.

  Note: An additional wake-up event is detected if WUPx pin is enabled (by setting the WUPENx bit) when WUPx pin level is already high when WUPPx selects rising edge, or low when WUPPx selects falling edge.

  Bit mapping: WUPEN7 (6), WUPEN6 (5), WUPEN5 (4), WUPEN4 (3), WUPEN3 (2), WUPEN2 (1), WUPEN1 (0).

*Digest note:* the register diagram marks bit 24 (part of WUPPUPD5) as "w" while every other WUPPUPDx bit is "rw"; treated here as rw.

### 8.10.9 PWR I/O retention register (PWR_IORETR)

Address offset: 0x050. Reset value: 0x0000 0000.

This register is protected against unprivileged access PRIV = 1 in the PWR_PRIVCFGR register.

- **Bits 31:17** Reserved, must be kept at reset value.
- **Bit 16 JTAGIORETEN** (rw): IO retention enable for JTAG I/Os
  - 0: I/O retention mode is disabled.
  - 1: I/O retention mode is enabling for PA13, PA14, PA15, and PB4.

  When entering Standby mode, the output is sampled, and apply to the output I/O during the Standby power mode.
- **Bits 15:1** Reserved, must be kept at reset value.
- **Bit 0 IORETEN** (rw): IO retention enable
  - 0: I/O retention mode is disabled.
  - 1: I/O retention mode is enabling for all I/Os except the I/O support the standby functionality and PA13, PA14, PA15, and PB4.

  When entering Standby mode, the output is sampled, and apply to the output I/O during the Standby power mode.

  Note: The I/O state is not retained if the DBG_STANDBY bit is set in DBGMCU_CR register.

### 8.10.10 PWR privilege configuration register (PWR_PRIVCFGR)

Address offset: 0x104. Reset value: 0x0000 0000.

This register can be written only when the access is privileged. It can be read by privileged or unprivileged access.

- **Bits 31:2** Reserved, must be kept at reset value.
- **Bit 1 PRIV** (rw): PWR functions privilege configuration
  Set and reset by software. This bit can be written only by privileged access.
  - 0: Read and write to PWR functions can be done by privileged or unprivileged access.
  - 1: Read and write to PWR functions can be done by privileged access only.
- **Bit 0** Reserved, must be kept at reset value.

### 8.10.11 PWR register map

**Table 63. PWR register map and reset values**

| Offset | Register | Reset value | Fields (bit positions) |
|---|---|---|---|
| 0x000 | PWR_PMCR | 0x0000 0000 | 31:27 Res.; SRAM1PDS (26); SRAM2PDS2 (25); SRAM2PDS1 (24); SRAM2PDS3 (23); 22:10 Res.; FLPS (9); 8 Res.; CSSF (7); 6:2 Res.; LPMS[1:0] (1:0) |
| 0x004 | PWR_PMSR | 0x0000 0000 | 31:7 Res.; SBF (6); STOPF (5); 4:0 Res. |
| 0x008-0x020 | Reserved | - | Res. |
| 0x024 | PWR_RTCCR | 0x0000 0000 | 31:1 Res.; DRTCP (0) |
| 0x028-0x030 | Reserved | - | Res. |
| 0x034 | PWR_VMCR | 0x0000 0000 | 31:1 Res.; PVDE (0) |
| 0x038 | Reserved | - | Res. |
| 0x03C | PWR_VMSR | 0x00X0 0000 (PVDO = X) | 31:23 Res.; PVDO (22); 21:0 Res. |
| 0x040 | PWR_WUSCR | 0x0000 0000 | 31:7 Res.; CWUF7 (6); CWUF6 (5); CWUF5 (4); CWUF4 (3); CWUF3 (2); CWUF2 (1); CWUF1 (0) |
| 0x044 | PWR_WUSR | 0x0000 0000 | 31:7 Res.; WUF7 (6); WUF6 (5); WUF5 (4); WUF4 (3); WUF3 (2); WUF2 (1); WUF1 (0) |
| 0x048 | PWR_WUCR | 0x0000 0000 | 31:30 Res.; WUPPUPD7[1:0] (29:28); WUPPUPD6[1:0] (27:26); WUPPUPD5[1:0] (25:24); WUPPUPD4[1:0] (23:22); WUPPUPD3[1:0] (21:20); WUPPUPD2[1:0] (19:18); WUPPUPD1[1:0] (17:16); 15 Res.; WUPP7 (14); WUPP6 (13); WUPP5 (12); WUPP4 (11); WUPP3 (10); WUPP2 (9); WUPP1 (8); 7 Res.; WUPEN7 (6); WUPEN6 (5); WUPEN5 (4); WUPEN4 (3); WUPEN3 (2); WUPEN2 (1); WUPEN1 (0) |
| 0x04C | Reserved | - | Res. |
| 0x050 | PWR_IORETR | 0x0000 0000 | 31:17 Res.; JTAGIORETEN (16); 15:1 Res.; IORETEN (0) |
| 0x054-0x100 | Reserved | - | Res. |
| 0x104 | PWR_PRIVCFGR | 0x0000 0000 | 31:2 Res.; PRIV (1); 0 Res. |

Refer to Section 2.2 for the register boundary addresses.

*Digest note:* all PWR register offsets and bit positions above match the CMSIS header stm32c552xx.h (PWR_TypeDef: PMCR 0x000, PMSR 0x004, RTCCR 0x024, VMCR 0x034, VMSR 0x03C, WUSCR 0x040, WUSR 0x044, WUCR 0x048, IORETR 0x050, PRIVCFGR 0x104), apart from the PWR_PMCR SRAM bit names noted in Section 8.10.1.
