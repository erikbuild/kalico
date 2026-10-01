# RM0522 Chapter 9: Reset and clock control (RCC)

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 251–326.

*Digest note:* The RCC base address is not given in this chapter (see RM Section 2.2 / Table 3). ST's CMSIS header `stm32c552xx.h` defines `RCC_BASE = AHB3PERIPH_BASE + 0x0C00 = 0x4402 0C00`. All register bit positions in Section 9.8 were cross-checked against that header; every bit the header defines matches the RM position. Differences in naming, availability and reset values are called out in *Digest note:* lines where they occur.

*Digest note (STM32C551/C552 availability summary):* Per the STM32C55xxx datasheet digest (/Users/erik/Code/kalico/digest-docs/digest/st/STM32C55xxx_Datasheet.md) and the C551/C552 CMSIS headers, the following RM0522 RCC features/instances are **absent** on STM32C55xxx: ETH1 (and all ETH1 clocks/bits, RCC_CCIPR3 ETH fields), XSPI1 (RCC_AHB4RSTR/AHB4ENR/AHB4LPENR, XSPI1SEL; the header has no AHB4 registers and no RCC_CCIPR3 at all), the cryptographic subsystem except HASH and RNG (no CCB, SAES, PKA; the header also has no AES bits), ADC3, GPIOF, GPIOG, TIM3, TIM4, USART6, UART7. OPAMP1 is not listed in the datasheet although the header defines OPAMP1 bits (see notes at the registers). FDCAN1 exists only on STM32C552xx (the STM32C551xx header has no FDCANSEL/FDCANEN/FDCANRST/FDCANLPEN). STM32C55xxx do have: HSI144, PSI, HSE 4–50 MHz, LSE, LSI, USB, RNG, HASH, ADC1/ADC2, DAC1, COMP, CORDIC, CRC, CRS, LPDMA1/LPDMA2, I2C1/I2C2, I3C1, SPI1/SPI2/SPI3, USART1/USART2/USART3, UART4/UART5, LPUART1, LPTIM1, TIM1/TIM2/TIM5/TIM6/TIM7/TIM8/TIM12/TIM15/TIM16/TIM17, GPIOA–GPIOE and GPIOH.

## 9.1 RCC introduction

The reset and clock control (RCC) manages the different resets, and generates the clocks for the bus and peripheral.

## 9.2 RCC pins and internal signals

The table below lists the RCC inputs and output signals connected to package pins or balls.

**Table 64. RCC input/output signals connected to package pins or balls**

| Signal name | Signal type | Description |
|---|---|---|
| NRST | I/O | System reset, can be used to provide reset to external devices |
| OSC32_IN | I | 32 kHz oscillator input |
| OSC32_OUT | O | 32 kHz oscillator output |
| OSC_IN | I | System oscillator input |
| OSC_OUT | O | System oscillator output |
| MCO | O | Output clock for external devices |
| LSCO | O | Low-speed output clock for external devices |
| AUDIOCLK | I | External kernel clock input for I2S1, I2S2, and I2S3 |

*Digest note:* The device has two MCO outputs (MCO1 and MCO2, see Section 9.4.11). The STM32C55xxx pinout lists MCO1 on PA8 (AF0) and PH2 (AF0), MCO2 on PA9, PC9 and PD10 (AF0); AUDIOCLK on PC9 (AF5); LSCO as an additional function of PB2 (datasheet digest, pin and alternate-function tables).

## 9.3 RCC reset functional description

There are three types of reset:

- A system reset
- A power reset
- A RTC domain reset

### 9.3.1 Power reset

A power reset is generated when one of the following events occurs:

- A power-on or power-down reset (POR/PDR)
- When exiting Standby mode

A power-on or power-down reset (POR/PDR) sets all registers to their reset values.

When exiting Standby mode, all registers in the core domain are set to their reset value. Registers outside the core domain (RTC, WKUP, IWDG, and GPIO pull-up/pull-down configuration during Standby and Standby mode exit) are not impacted.

### 9.3.2 System reset

A system reset sets all registers to their reset values, except the reset flags in RCC_RSR, and the registers in the RTC domain.

A system reset is generated when one of the following events occurs:

- A low level on the NRST pin (external reset)
- A window watchdog event (WWDG reset)
- An independent watchdog event (IWDG reset)
- A software reset (SW reset) (see Software reset)
- A low-power mode security reset (see Low-power mode security reset)
- A POR reset

The reset source can be identified by checking the reset flags in RCC_RSR.

These sources act on the NRST pin and this pin is always kept low during the delay phase. The reset service routine vector is selected depending on RDP level, on Boot option bytes or on both.

The system reset signal provided to the device is output on the NRST pin. The pulse generator guarantees a minimum reset pulse duration of 20 µs for each internal reset source. In case of an external reset, the reset pulse is generated while the NRST pin is asserted low.

In case of an internal reset, the internal pull-up RPU is deactivated to save the power consumption through the pull-up resistor.

**Figure 24. Simplified diagram of the reset circuit** (described)

- The NRST pad (bidirectional "External reset") is pulled up to VDD through the internal resistor RPU. The RPU pull-up is controlled (switched) by the pulse generator.
- The NRST pad level goes through a Schmitt-trigger inverter and a Filter; the filtered signal is one input of the OR gate that produces "System reset".
- A second OR gate combines the internal reset sources: WWDG reset, IWDG reset, Software reset, Low-power manager reset, and POR. Its output drives a "Pulse generator (min 20 µs)", which drives an open-drain pull-down transistor on NRST (and controls RPU). Thus every internal reset source pulls NRST low for at least 20 µs, and the resulting NRST low level feeds back through the filter into "System reset".

#### Software reset

The SYSRESETREQ bit in Cortex-M33 application interrupt and reset control register must be set to force a software reset on the device.

#### Low-power mode security reset

To avoid that critical applications mistakenly enter a low-power mode, the following low-power mode security resets are available. If enabled in option bytes, the resets are generated in any of the following conditions:

- Entering Standby mode: this type of reset is enabled by resetting NRST_STDBY bit in user option bytes. In this case, whenever a Standby mode entry sequence is successfully executed, the device is reset instead of entering Standby mode.
- Entering Stop mode: this type of reset is enabled by resetting NRST_STOP bit in user option bytes. In this case, whenever a Stop mode entry sequence is successfully executed, the device is reset instead of entering Stop mode.

For further information on the user option bytes, refer to Section 6.4: FLASH option bytes.

### 9.3.3 RTC domain reset

The RTC domain has two specific resets, generated when one of the following events occurs:

- A software reset, is triggered by setting the RTCDRST bit in RCC_RTCCR. Write access to this domain must be enabled before setting RTCDRST bit to perform the reset.
- A VDD power on

An RTC domain reset affects the LSE oscillator, the RTC, the backup registers, and the RCC_RTCCR register.

### 9.3.4 Reset source identification

The application can identify the reset source by checking the reset flags in the RCC_RSR register.

The software can reset the flags by setting the RMVF bit.

The table below shows how the status bits of the RCC_RSR register behave according to the situation that generated the reset. For example, when an IWDG timeout occurs, if the CPU is reading the RCC_RSR register during the boot phase, both PINRSTF and IWDGRSTF bits are set, indicating that the IWDG also generated a pin reset.

**Table 65. Reset source identification (RCC_RSR)(1)**

| # | Reset | LPWRRSTF | WWDGRSTF | IWDGRSTF | SFTRSTF | PORRSTF | PINRSTF |
|---|---|---|---|---|---|---|---|
| 1 | Power-on reset | 0 | 0 | 0 | 0 | 1 | 1 |
| 2 | Pin/pad reset | 0 | 0 | 0 | 0 | 0 | 1 |
| 3 | System reset generated by CPU | 0 | 0 | 0 | 1 | 0 | 1 |
| 4 | WWDG reset | 0 | 1 | 0 | 0 | 0 | 1 |
| 5 | IWDG reset | 0 | 0 | 1 | 0 | 0 | 1 |
| 6 | Illegal stop entry reset | 1 | 0 | 0 | 0 | 0 | 1 |

Notes:

1. Gray cells highlight the register bits that are set. (In the source, every cell containing 1 is gray.)

*Digest note:* The table column "PORRSTF" corresponds to the register bit named BORRSTF (RCC_RSR bit 27, described as "POR reset flag"); the CMSIS header also names it `RCC_RSR_BORRSTF`. PINRSTF is set for every reset source because all internal sources drive NRST low (Figure 24).

## 9.4 RCC clocks functional description

Four different clock sources can be used to drive the system clock (SYSCLK):

- HSIS: high-speed internal clock at 144 MHz
  - and HSIDIV3: high-speed internal clock is divided by 3; at 48 MHz
- PSIS: programmable speed internal clock up to 160MHz (max SYSCLK is 144 MHz)
- HSE: high-speed external crystal or clock, from 4 to 50 MHz

The HSIDIV3 is used as a the system clock source after startup from reset, at 48 MHz.

Note: If HSE or PSIS with HSE as reference are used as SYSCLK and the HSE CSS detect a failure, HSIDIV3 is automatically set as SYSCLK. Adequate wait state supporting both frequencies must be configured in this case.

The device has the following additional clock sources:

- HSIK: high-speed internal clock divided by 1;1.5; 2;...; 7.5; 8
- PSIDIV3: programmable speed internal clock divided by 3
- PSIK: programmable speed internal clock divided by 1;1.5; 2;...; 7.5; 8
- LSI: 32 kHz low-speed internal RC that drives the independent watchdog and optionally the RTC used for auto-wake-up from Stop and Standby modes
- LSE: 32.768 kHz low-speed external crystal or clock that optionally drives the real-time clock (rtc_ck)

Each clock source can be switched on or off independently when it is not used, to optimize power consumption.

Several prescalers can be used to configure the AHB and APB frequencies. The maximum frequency of the AHB and APB domains is 144 MHz.

The peripheral clocks are derived from their bus clock (HCLK, PCLK1, PCLK2 or PCLK3), except those that receive an independent kernel clock. This kernel clock can be selected by software between several sources thanks to RCC_CCIPRx registers (x = 1 to 3).

Note: All timers (except LPTIM) are clocked by HCLK, independently of their respective PCLK.

In addition, the RTC kernel clock is selected by software in RCC_RTCCR. The IWDG clock is always the LSI 32 kHz clock.

The RCC feeds the Cortex system timer (SysTick) external clock with the AHB clock (HCLK) divided by eight, or LSE or LSI. The SysTick can work either with this clock or directly with the Cortex clock (HCLK), configurable in the SysTick control and status register.

FCLK acts as a a Cortex-M33 free-running clock.

**Figure 25. Clock tree** (described; ST drawing MSv76069V3)

Oscillators, pins and low-speed section:

- Package pins on the left edge: LSCO (output), OSC32_OUT, OSC32_IN, OSC_OUT, OSC_IN, AUDIOCLK (input), MCO1 (output), MCO2 (output).
- **LSI RC 32 kHz** produces LSI (lsi_ck). lsi_ck goes "To IWDG", to the LSCO multiplexer, to the RTC clock multiplexer, to the Cortex system timer multiplexer, to the MCO1 and MCO2 multiplexers, and to the LPTIM1, LPUART and DAC1 sample-and-hold multiplexers.
- **LSE OSC 32.768 kHz** (with a "Clock detector" block, i.e. the LSE CSS) is connected between OSC32_IN and OSC32_OUT and produces LSE (lse_ck). lse_ck goes to the LSCO multiplexer, the RTC clock multiplexer, the PSI reference multiplexer, the Cortex system timer multiplexer, the MCO1/MCO2 multiplexers, the USART/UART, LPTIM1, LPUART and DAC1 sample-and-hold multiplexers.
- **LSCO multiplexer**: 2 inputs, lsi_ck and lse_ck; output drives the LSCO pin.
- **HSE OSC 4-50 MHz** (with a "Clock detector" block, i.e. the HSE CSS) is connected between OSC_IN and OSC_OUT and produces HSE (hse_ck). hse_ck goes to: the RTCPRE divider, the SYSCLK multiplexer, the PSI reference multiplexer, the USB 48 MHz (CK48) multiplexer, the FDCAN multiplexer, the ETH1_CLK multiplexer, and the MCO1/MCO2 multiplexers.
- **RTCPRE / 2,3,...,511** divides hse_ck to produce hse_1M_ck.
- **RTC clock multiplexer**: inputs lsi_ck, lse_ck, hse_1M_ck; output rtc_ck "To RTC".

High-speed oscillators:

- **PSI** (block labelled "100 / 144 / 160") receives its reference from a 3-input multiplexer with inputs LSE (lse_ck), HSE (hse_ck) and hsidiv18_ck. Its output is PSIS. PSIS goes to the SYSCLK multiplexer, and is also tapped by two dividers: "/ 3" producing PSIDIV3, and "Div 1, 1.5, 2, .. to 8" producing PSIK.
- **HSI** (block labelled "144") output is HSIS. HSIS goes to the SYSCLK multiplexer, and is also tapped by two dividers: "/ 3" producing HSIDIV3, and "Div 1, 1.5, 2, .. to 8" producing HSIK. HSIDIV3 goes to the SYSCLK multiplexer and to the USB 48 MHz multiplexer.
- The figure does not draw where hsidiv18_ck is generated; per Section 9.4.3 and RCC_CR2.PSIREFSRC it is the HSI clock divided by 18.

System clock and bus clocks:

- **SYSCLK multiplexer**, controlled by the "Clock source control" block, has 4 inputs: HSE (hse_ck), PSIS, HSIS, HSIDIV3. Its output is SYSCLK (sys_ck).
- SYSCLK goes "To PWR" and to the **AHB PRESC / 1,2,..512**, whose output is HCLK (rcc_hclk).
- HCLK goes: "To AHB bus, core, memory and DMA"; to "FCLK Cortex free running clock"; to "To timx_ker_ck (x = 1,2,3,4,5,6,7,8,12,15,16,17)" (all timers except LPTIM run directly from HCLK); to a "/ 8" divider feeding the Cortex system timer multiplexer; and to the three APB prescalers.
- **Cortex system timer multiplexer**: inputs LSE (lse_ck), LSI (lsi_ck), HCLK / 8; output "To Cortex system timer".
- **APB1 PRESC / 1,2,4,8,16** produces PCLK1 (rcc_pclk1) "To APB1 peripherals".
- **APB2 PRESC / 1,2,4,8,16** produces PCLK2 (rcc_pclk2) "To APB2 peripherals".
- **APB3 PRESC / 1,2,4,8,16** produces PCLK3 (rcc_pclk3) "To APB3 peripherals".

Kernel clock multiplexers (inputs listed in the order drawn; PCLK means the bus clock of the peripheral):

- **48 MHz clock to USBFS**: inputs psidiv3_ck, hse_ck, hsidiv3_ck. The multiplexer output also goes to **RNG** (RNG kernel clock is the same CK48 selection).
- **SPI1, SPI2, SPI3**: psik_ck, hsik_ck, PCLK, AUDIOCLK.
- **I2C1, I2C2, I3C1**: psik_ck, hsik_ck, PCLK.
- **XSPI1**: HCLK, psik_ck, hsik_ck.
- **ETH1_CLK**: psis_ck, psik_ck, hse_ck, followed by a "/ 1, 2, 4" divider.
- **ETH1_PTPCLK**: HCLK, psis_ck, psik_ck, followed by a "/ 1, 2, 4, …, 16" divider.
- **USARTx (x = 1, 2, 3, 6), UARTx (x = 4, 5, 7)**: psik_ck, lse_ck, hsik_ck, PCLK.
- **FDCANx (x = 1, 2)**: psik_ck, psis_ck, hse_ck, PCLK.
- **To ADC and DAC**: psis_ck, psik_ck, HCLK, hsik_ck, followed by a "/ 1→128" divider (ADCDACPRE).
- **LPTIM1**: hsik_ck, lse_ck, lsi_ck, PCLK.
- **LPUART**: hsik_ck, lse_ck, lsi_ck, PCLK.
- **DAC1 sample and hold clock**: lse_ck, lsi_ck.

Clock outputs:

- **MCO1 multiplexer**: HSIS, PSIS, HSIK, PSIK, LSI (lsi_ck), LSE (lse_ck), HSE (hse_ck), SYSCLK; followed by a "/ 1→15" prescaler driving the MCO1 pin.
- **MCO2 multiplexer**: HSIDIV3, PSIDIV3, HSIK, PSIK, LSI (lsi_ck), LSE (lse_ck), HSE (hse_ck), SYSCLK; followed by a "/ 1→15" prescaler driving the MCO2 pin.

Legend: items in dashed blue boxes ("Check the datasheet for the actual availability of this peripheral") are: the timx_ker_ck list, SPI1/SPI2/SPI3, I2C1/I2C2/I3C1, XSPI1, ETH1_CLK, ETH1_PTPCLK, the USARTx/UARTx instance list, and the FDCAN instance list "(x = 1, 2)".

*Digest note:* On STM32C55xxx the timer list reduces to TIM1, TIM2, TIM5, TIM6, TIM7, TIM8, TIM12, TIM15, TIM16, TIM17; the USART/UART list to USART1/2/3 and UART4/5; FDCAN to FDCAN1 (STM32C552xx only); XSPI1, ETH1_CLK and ETH1_PTPCLK are absent.

### 9.4.1 HSE clock

The HSE block can generate a clock from an external crystal/ceramic resonator, or from an external clock source.

**Figure 26. HSE/ LSE clock sources** (described)

- External clock configuration: the external clock source drives OSC_IN (or OSC32_IN); OSC_OUT (or OSC32_OUT) is free and usable as a GPIO.
- Crystal/ceramic resonators configuration: the resonator is connected between OSC_IN and OSC_OUT (or OSC32_IN and OSC32_OUT), with a load capacitor CL1 from OSC_IN (OSC32_IN) to ground and a load capacitor CL2 from OSC_OUT (OSC32_OUT) to ground.

#### External clock source (HSE bypass)

In this mode, an external clock source must be provided to OSC_IN pin. The external clock can be low swing (analog) or digital. If this clock is directly used by a peripheral, the duty cycle requirement is defined by the peripheral and the application (refer to datasheet for more details).

In case of an analog clock (low swing) the HSEBYP and HSEON bits must be set to 1 in RCC_CR1.

In case of a digital clock, the HSEBYP and the HSEEXT bits must be set to 1 followed by setting the HSEON bit to 1 in RCC_CR1.

#### External crystal/ceramic resonator

The oscillator is enabled by setting the HSEBYP bit to 0 and HSEON bit to 1.

The HSE can be used when the product requires a very accurate high-speed clock.

The associated hardware configuration is shown in Figure 26: the resonator and the load capacitors must be placed as close as possible to the oscillator pins to minimize output distortion and startup stabilization time. The loading capacitance values must be adjusted according to the selected crystal or ceramic resonator. Refer to the electrical characteristics section of the datasheet for more details.

The HSERDY flag in RCC_CR1 indicates whether the HSE oscillator is stable or not. At startup, the hse_ck clock is not released until this bit is set by hardware. An interrupt can be generated if enabled in RCC_CIER.

The HSE can be switched on and off through the HSEON bit.

Note: The HSE cannot be switched off if one of the following two conditions is met:

- the HSE is used directly (through software multiplexer) as a system clock
- the HSE is selected as the reference clock for PSI, with PSI enabled and selected to provide the system clock (through software multiplexer).

In that case the hardware does not allow programming the HSEON bit to 0.

The HSE is automatically disabled by hardware when the system enters Stop or Standby mode. It can be kept on under Stop 0 mode if PSIKERON is set and PSI needs HSE as a reference clock.

In addition, the HSE clock can be driven to the MCO1 and MCO2 outputs and used as a clock source for other application components.

### 9.4.2 HSI oscillator and HSIS clock

The HSI block provides the default clocks to the product.

The HSI is a high-speed internal oscillator that can be used as a system clock or peripheral clock offering a 144MHz clock available at startup and upon wake-up from low power modes. The HSI oscillator can produce 3 output clocks; HSIS, HSIDIV3, and HSIK.

Two output dividers let you extent the available frequencies for the device. One configurable divider by 1.5, 2, 2.5, ... 7.5 or 8 is configured thanks to HSIKDIV[3:0] generating HSIK clock and a second divided by 3 intended for system clock and USB generating HSIDIV3.

The HSI advantages are the following:

- Low-cost clock source, as no external crystal is required
- Faster startup time than HSE (a few microseconds)

The HSI frequency, even with frequency calibration, is less accurate than an external crystal oscillator or ceramic resonator.

HSI oscillator can be switched on and off using the HSISON bit, the HSIDIV3ON bit, and the HSIKON bit. Only the enabled clock output is generated.

Note: The HSI cannot be switched off if the HSI is used directly (via SW mux) as a system clock. In that case the hardware does not allow clearing the HSISON bit or HSIDIV3ON bit to 0.

The HSISRDY, HSIKRDY, and HSIDIV3RDY flags indicate if the HSI is stable or not. At startup, the HSIS output clock is not released until HSISRDY is set by hardware.

The HSIDIV3 clock can also be used as a backup source (auxiliary clock) if the HSE fails (refer to Section 9.4.10: Clock security system (CSS)).

In addition, the HSI clocks can be driven to the MCO1 or MCO2 outputs and used as clock source for other application components.

Care must be taken when the HSIK is used as a kernel clock for communication peripherals, the application must take in account the following parameters:

- the time interval between the moment where the peripheral generates a kernel clock request and the moment where the clock is really available
- the frequency accuracy.

Note: The HSI can remain enabled when the system is in Stop 0 mode thanks to HSIKERON bit. In this case, the HSI and its clocks outputs HSIK, HSIDIV3, or HSIS, are kept active if their respective HSIKON, HSIDIV3ON, and HSISON are set. The states of these bits are consequently maintained exiting Stop 0 if HSIKERON bit is set.

#### HSI calibration

HSI oscillator frequencies can vary from one chip to another due to manufacturing process variations. That is why each device is factory calibrated by STMicroelectronics to achieve an accuracy of ACCHSI (refer to the product datasheet for more information).

After a power-on reset, the factory calibration value is loaded. If the application is subject to voltage or temperature variations, this may affect the oscillator frequency. The user application can trim the HSI frequency using the TRIM[6:0] bits in the CRS_CR register.

The clock recovery system can be used to perform this calibration. It requires an accurate reference that can be HSE (through HSE_1MHz connection), LSE, USB Start of Frame, or an external signal.

### 9.4.3 PSI oscillator and PSIS clock

The PSI oscillator provides a 100 MHz, 144 MHz, or 160 MHz frequency, selected thanks to PSIFREQ[1:0] bitfield, to the product on condition that an adequate reference clock is available. This programmable speed internal oscillator can be used as a system clock or peripheral clock. The PSI oscillator can produce three output clocks; PSIS, PSIDIV3, and PSIK.

The PSI is only operational when receiving a reference clock of 32.768 kHz, 8 MHz, or 8.33 MHz (25 MHz divided by 3) as input. The PSIREF[2:0] bitfield helps you get the required input frequency depending on your chosen external clock. This external clock is selected thanks to PSIREFSRC[1:0] multiplexer between LSE, HSE, or HSI divided by 18. Details of possible settings are listed in the table below.

**Table 66. PSI frequency settings**

| PSIFREQ[1:0] | PSIREFSRC[1:0] | PSIREF[2:0] |
|---|---|---|
| 160 | HSE | 48 |
| 160 | HSE | 32 |
| 160 | HSE | 24 |
| 160 | HSE | 16 |
| 160 | HSE | 8 |
| 160 | HSI/18 | 8 |
| 160 | LSE | 0.032768 |
| 144 | HSE | 48 |
| 144 | HSE | 32 |
| 144 | HSE | 24 |
| 144 | HSE | 16 |
| 144 | HSE | 8 |
| 144 | HSI/18 | 8 |
| 144 | LSE | 0.032768 |
| 100 | HSE | 50 |
| 100 | HSE | 48 |
| 100 | HSE | 32 |
| 100 | HSE | 25 |
| 100 | HSE | 24 |
| 100 | HSE | 16 |
| 100 | HSE | 8 |
| 100 | HSI/18 | 8 |
| 100 | LSE | 0.032768 |

*Digest note:* The table prints the PSI output frequency (MHz), the reference source name, and the reference frequency (MHz), not the register codes. Register encodings (from Section 9.8.2): PSIFREQ 100 MHz = 00, 144 MHz = 01, 160 MHz = 1x; PSIREFSRC HSE = 00, LSE = 01, HSI/18 = 10 (11 is not defined); PSIREF 32.768 kHz = 000, 8 MHz = 001, 16 MHz = 010, 24 MHz = 011, 25 MHz = 100, 32 MHz = 101, 48 MHz = 110, 50 MHz = 111. Consequences for HSE crystals/clocks: 8, 16, 24, 32 and 48 MHz give exactly 100, 144 or 160 MHz; 25 and 50 MHz are listed only for the 100 MHz setting (the datasheet, Table 37, gives 141.67 MHz for the 144 MHz setting and 158.33 MHz for the 160 MHz setting with a 25 or 50 MHz reference); any other HSE frequency (for example 12 MHz) has no PSIREF code and cannot be used as PSI reference. The datasheet gives 100.008 MHz (not 100.016 MHz as below) for the LSE-referenced 100 MHz setting.

Note: If LSE is used as reference, an intrinsic error must be anticipated on the output frequency (100.016 MHz, 144.015 MHz, and 160.006 MHz)

Two output dividers can be used to extent the available frequencies for the device. One configurable divider by 1.5, 2, 2.5, 3, 3.5, ... , 7.5, or 8, configured thanks to PSIKDIV[3:0] generating PSIK clock and a second dividing by 3 generating PSIDIV3 clock, intended for USB.

The PSI advantages are the following:

- Programmable high-speed clock source based on a reference clock
- Configurable output frequencies (100 MHz, 144 MHz, 160 MHz)

The PSI frequency accuracy is directly related to the accuracy of its reference clock (for more details regarding the specification of this oscillator, refer to product datasheet).

PSI oscillator can be switched on and off using the PSISON bit, the PSIDIV3ON bit, or the PSIKON bit. Only the enabled clock output is generated.

Note: The PSI cannot be switched off if used (via SW mux) as a system clock. In that case, the hardware does not allow programming the PSISON bit to 0.

The PSISRDY, PSIKRDY, and PSIDIV3RDY flags indicate if the oscillator is stable or not.

In addition, the PSI clocks can be driven to the MCO1 or MCO2 outputs, and used as clock source for other application components.

Care must be taken when the PSI is used as a kernel clock for communication peripherals; the application must take into account the following parameters:

- the time interval between the moment where the peripheral generates a kernel clock request and the moment where the clock is really available

Note: The PSI can remain enabled when the system is in Stop 0 mode thanks to PSIKERON bit. In this case the PSI and its clock outputs PSIK, PSIKDIV3, or PSIS are kept enabled if their respective PSIKON, PSIDIV3ON, and PSISON are set. The states of those bits are maintained exiting Stop 0 if the HSIKERON bit is set.

*Digest note:* "PSIKDIV3" and "HSIKERON" in the last note are as printed; by analogy with the HSI note in Section 9.4.2 they presumably mean PSIDIV3 and PSIKERON. The datasheet gives a PSI startup time tsu(PSI) of 25 µs typ / 45 µs max on an 8 MHz reference and 850 µs typ / 1750 µs max on 32 kHz.

### 9.4.4 HSIDIV3 and PSIDIV3 clock

The HSIDIV3 clock signal is generated from the internal 144 MHz RC oscillator, divided by 3 to be used directly for USB and for random number generator (RNG).

This internal 48 MHz clock is mainly dedicated to provide a high-precision clock to the USB peripheral by means of a special clock recovery system (CRS) circuitry. The CRS can use the USB SOF signal, the LSE, or an external signal to automatically and quickly adjust the oscillator frequency on-the-fly. It is disabled as soon as the system enters Stop or Standby mode. When the CRS is not used, the HSI oscillator runs on its default frequency, subject to manufacturing process variations.

For more details on how to configure and use the CRS peripheral, refer to Section 10: Clock recovery system (CRS).

The HSIDIV3RDY flag in the RCC_CR register indicates whether the HSIDIV3 clock is stable or not. At startup, the HSIDIV3 output clock is not released until this bit is set by the hardware.

The HSIDIV3 clock signal can be switched on and off using the HSIDIV3ON bit in the RCC_CR register.

The PSIDIV3 clock signal is generated from the internal 144 MHz RC oscillator, divided by 3 to be used directly for USB and for random number generator (RNG). It benefits from the accuracy of the HSE or LSE thanks to its operation in PLL mode. Similarly to HSIDIV3, it is disabled in Stop or Standby mode, ready once PSIDIV3RDY is set and enabled thanks to PSIDIV3ON bit is set.

*Digest note:* "RCC_CR" here means RCC_CR1. PSIDIV3 is the PSI output divided by 3 (Figure 25), so it is 48 MHz only when PSIFREQ selects 144 MHz (33.33 MHz at 100 MHz, 53.33 MHz at 160 MHz). The sentence "generated from the internal 144 MHz RC oscillator" is as printed.

### 9.4.5 HSIK and PSIK clock

THE HSIK and PSIK are two clock outputs offering frequency flexibility to the user. These dividers can be configured thanks to HSIKDIV[3:0] and PSIKDIV[3:0] bitfields respectively with division factors of 1, 1.5, 2, 2.5 ... 7.5, and 8. This allow to create a 96 MHz clock source derived from a 144 MHz for example if divided by 1.5, useful for FDCAN operation, or 64 MHz out of the 160 MHz divided by 2.5 to tune your DAC output sample frequency.

The HSIKRDY and PSIKRDY flags in the RCC_CR register indicate whether the HSIK and PSIK clocks are stable or not. At startup, the HSIK, and PSIK output clocks are not released until this bit is set by hardware.

The HSIK and PSIK clock signals can be switched on and off using the HSIKON and PSIKON bits in the RCC_CR register.

**Table 67. PSIK and HSIK output frequency**

| PSIKDIV[3:0]/HSIKDIV[3:0] division factor | PSIK frequency if PSI 160MHz | PSIK frequency if PSI 144MHz and hsik frequency | PSIK frequency if PSI 100MHz |
|---|---|---|---|
| 1 | 160 MHz | 144 MHz | 100 MHz |
| 1.5 | 106.67 MHz | 96 MHz | 66.67 MHz |
| 2 | 80 MHz | 72 MHz | 50 MHz |
| 2.5 | 64 MHz | 57.6 MHz | 40 MHz |
| 3 | 53.33 MHz | 48 MHz | 33.33 MHz |
| 3.5 | 45.71 MHz | 41.14 MHz | 28.57 MHz |
| 4 | 40 MHz | 36 MHz | 25 MHz |
| 4.5 | 35.56 MHz | 32 MHz | 22.22 MHz |
| 5 | 32 MHz | 28.8 MHz | 20 MHz |
| 5.5 | 29.09 MHz | 26.18 MHz | 18.18 MHz |
| 6 | 26.67 MHz | 24 MHz | 16.67 MHz |
| 6.5 | 24.62 MHz | 22.15 MHz | 15.38 MHz |
| 7 | 22.86 MHz | 20.57 MHz | 14.28 MHz |
| 7.5 | 21.33 MHz | 19.2 MHz | 13.33 MHz |
| 8 | 20 MHz | 18 MHz | 12.5 MHz |

Caution: 160 MHz is above the maximum frequency supported by the product. It must not be propagated to the kernel clock of peripherals.

*Digest note:* "RCC_CR" here means RCC_CR1. The division factor column is the factor, not the register code; the register code n (0b0000–0b1111) gives division factor (n + 1) / 2 for n ≥ 1, and code 0b0000 also gives /1 (Section 9.8.2).

### 9.4.6 LSE clock

The LSE block can generate a clock from an external crystal/ceramic resonator, or from an external user clock.

#### External clock source (LSE bypass)

In this mode, an external clock source must be provided to OSC32_IN pin. The input clock can have a frequency up to 1 MHz, and be low swing (analog) or digital. A duty cycle close to 50% is recommended.

This external clock is provided to the OSC32_IN pin while the OSC32_OUT pin must be left high-Z (see Figure 25).

In case of an analog clock (low swing), the LSEBYP, and LSEON bits must be set to 1 in RCC_RTCCR.

In case of a digital clock, the LSEBYP and the LSEEXT bits must be set to 1 followed by setting the LSEON bit to 1 in RCC_RTCCR.

#### External crystal/ceramic resonator (LSE crystal)

The LSE clock is generated from a 32.768 kHz crystal or ceramic resonator. It has the advantage to provide a low-power, highly accurate clock source to the real-time clock (RTC) for clock/calendar or other timing functions.

The LSERDY flag in RCC_RTCCR indicates whether the LSE crystal is stable or not. At startup, the LSE crystal output clock signal is not released until this bit is set by the hardware. An interrupt can be generated if enabled in RCC_CIER.

The LSE oscillator is switched on and off using the LSEON bit. The LSE remains enabled when the system enters Stop or Standby mode.

In addition, the LSE clock can be driven to the MCO1 and MCO2 output and used as a clock source for other application components.

The LSE also offers a programmable driving capability (LSEDRV[1:0]), which can be used to modulate the amplifier driving capability. This driving capability is chosen according to the external crystal/ceramic component requirement to ensure a stable oscillation.

The driving capability must be set before enabling the LSE oscillator.

*Digest note:* Per the datasheet (Table 1), the 32-pin packages (STM32C55xKxT/KxU) and the LQFP64 "RxTxJ" variant have the RTC "without LSE".

### 9.4.7 LSI clock

The LSI acts as a low-power clock source that can be kept running when the system is in Stop or Standby mode for the independent watchdog (IWDG) and auto-wake-up unit (AWU). The clock frequency is around 32 kHz. For more details, refer to the electrical characteristics section of the datasheet.

The LSI can be switched on and off using the LSION bit. The LSIRDY flag indicates whether the LSI oscillator is stable or not. If an independent watchdog is started either by hardware or software, the LSI is forced on and cannot be disabled.

The LSI remains enabled when the system enters Stop or Standby mode.

At LSI startup, the clock is not provided until the hardware sets the LSIRDY bit. An interrupt can be generated if enabled in RCC_CIER.

In addition, the LSI clock can be driven to the MCO1 and MCO2 output, and used as a clock source for other application components.

Note: LSION and LSIRDY are located in RCC_RTCCR.

### 9.4.8 System clock (SYSCLK) selection

Four different clock sources can be used to drive the system clock (SYSCLK):

- HSI oscillator, through HSIS clock
- HSI oscillator divided by 3, through HSIDIV3 clock source
- PSI oscillator, through PSIS clock
- HSE oscillator

The system clock maximum frequency is 144 MHz. After a system reset (or after leaving Standby mode), the HSI oscillator divided by 3, at 48 MHz, is selected as the system clock.

When a clock source is used directly or through PSI as a system clock, it is not possible to stop it.

A switch from one clock source to another occurs only if the target clock source is ready (clock stable after startup delay). If a clock source not yet ready is selected, the switch occurs when the clock source becomes ready. Status bits in RCC_CR1 indicate which clocks are ready, and which clock is currently used as a system clock.

*Digest note:* The current SYSCLK source is reported by RCC_CFGR1.SWS[1:0] (not RCC_CR1). Reset state: RCC_CR1 = 0x0000 0022 (HSIDIV3ON = 1, HSIDIV3RDY = 1, HSISON = 0), RCC_CFGR1.SW = SWS = 00 (HSIDIV3), RCC_CFGR2 = 0 (HCLK = PCLK1 = PCLK2 = PCLK3 = SYSCLK = 48 MHz).

*Digest note (derived sequences, not given by the RM):* The RM contains no step-by-step switch procedure. The following sequences only combine rules stated in this chapter (bit write restrictions, ready flags, SW/SWS); flash wait states are configured in the FLASH chapter (RM Chapter 6), which is outside this chapter, and must suit the target frequency before switching up (and both frequencies while an HSE CSS fallback to 48 MHz HSIDIV3 is possible, per the note in Section 9.4).

- SYSCLK = HSIS (144 MHz): (1) set flash wait states for 144 MHz; (2) set RCC_CR1.HSISON = 1 and wait for HSISRDY = 1; (3) keep RCC_CFGR2.HPRE/PPRE1/PPRE2/PPRE3 at /1 (144 MHz is the AHB/APB maximum) or set the desired division; (4) write RCC_CFGR1.SW = 01 and wait until SWS = 01. HSIDIV3 may stay enabled (it can be used for USB, CK48SEL = 10).
- SYSCLK = PSIS (144 MHz) from an HSE crystal of 8, 16, 24, 32 or 48 MHz: (1) with the PSI disabled (PSISON = PSIDIV3ON = PSIKON = 0, required because PSIFREQ/PSIREF/PSIREFSRC are writable only while the PSI is disabled), set HSEBYP = 0 and HSEON = 1 in RCC_CR1 and wait for HSERDY = 1; (2) write RCC_CR2: PSIREFSRC = 00 (HSE), PSIREF = 001/010/011/101/110 for 8/16/24/32/48 MHz, PSIFREQ = 01 (144 MHz); (3) set PSISON = 1 (and PSIDIV3ON = 1 if USB is to use psidiv3_ck = 48 MHz, PSIKON = 1 if psik_ck is needed) and wait for PSISRDY = 1 (and PSIDIV3RDY/PSIKRDY); (4) set flash wait states for 144 MHz and the bus prescalers; (5) write RCC_CFGR1.SW = 11 and wait until SWS = 11; (6) optionally set RCC_CR1.HSECSSON = 1 (on HSE failure the hardware falls back to HSIDIV3 and raises an NMI, Section 9.4.10). For an external digital clock instead of a crystal, set HSEBYP = 1 and HSEEXT = 1 before HSEON (Section 9.4.1). A 25 MHz or 50 MHz HSE cannot produce exactly 144 MHz from the PSI (Table 66 and the note after it); with such a crystal, HSIS (144 MHz) or PSI at 100 MHz are the exact options.

### 9.4.9 Handling clock generators in Stop and Standby modes

When the whole system enters Stop mode, all the clocks (system and kernel clocks) are stopped, as well as the following clock sources:

- HSI oscillator
- PSI oscillator
- HSE

Note: In Stop 0 mode, if HSIKERON or PSIKERON are set, HSI, PSI, or HSE may be kept running depending on clock output enable bits (HSISON, HSIDIV3ON, HSIKON, PSISON, PSIDIV3ON, PSIKON) and PSI reference clock source setting. in Stop 1 mode, HSIKERON, and PSIKERON have no effect.

The content of the RCC registers is not altered except for HSEON set to 0.

#### Exiting Stop mode

When the system exits this mode via a wake-up event, the application restarts on HSI oscillator and HSIS or HSIDIV3 clock depending on STOPWUCK bit value.

#### During Stop mode

There are two specific cases where the HSI can be enabled during this mode.

- When a dedicated peripheral requests the kernel clock the peripheral receives the HSIS, HSIK or HSIDIV3 according to the kernel clock source selected for this peripheral (using the RCC kernel clock configuration register RCC_CCIPRx)).
- When the HSIKERON bit in RCC_CR1 is set, the HSI is kept running under Stop 0 mode. If a clock is enabled thanks to HSISON, HSIDIV3ON or HSIKON it is available immediately when the system exits Stop 0 mode, or when a peripheral requests the kernel clock (see Table 68 for details). The same applies to the PSI thanks to PSIKERON bit. In this case, its reference clock is also kept on.

**Table 68. HSIKERON and PSIKERON behavior**

| HSIKERON (PSIKERON) | HSI (PSI) state during Stop mode | HSI (PSI) state setting time |
|---|---|---|
| 0 | Off | tsu(HSI) tsu(PSI) (1) |
| 1 | Running and gated if enabled | Immediate |

Notes:

1. tsu(HSI) and tsu(PSI) are the startup times of, respectively, the HSI and PSI oscillators (refer to the product datasheet for the values of these parameters).

When the microcontroller exits Standby mode, HSIDIV3 is selected as the system clock. The RCC registers are reset to their initial values, except for RCC_RSR and RCC_RTCCR.

Note: The HSI and PSI oscillators provide three clock paths respectively:

- One path for the system clock (hsis_ck or psis_ck)
- One path for the peripheral kernel clock (hsik_ck or psik_ck)
- One path for the peripheral kernel clock divided by 3 (hsidiv3_ck or psidiv3_ck)

When a peripheral requests the kernel clock in system Stop mode, only the path providing the hsik_ck, psik_ck or hsidiv3_ck, psidiv3_ck is activated.

### 9.4.10 Clock security system (CSS)

#### Clock security system on HSE

The clock security system can be enabled by software via the HSECSSON bit, which can be set even when the HSEON is cleared.

The CSS on HSE is enabled by the hardware when the HSE is enabled and ready, and HSECSSON set to 1.

The CSS on HSE is disabled when the HSE is disabled. It is not possible to clear directly the HSECSSON bit by software.

The HSECSSON bit is cleared by hardware when a system reset occurs or when the system enters Standby mode.

If a failure is detected on the HSE clock while it is used as a system clock, the system automatically switches to the HSIDIV3, to provide a safe clock. The HSE is then automatically disabled, a clock failure event is sent to the break inputs of the advanced-control timer (TIM1, TIM8, TIM15, TIM16, and TIM17), and an NMI is automatically generated to inform the application about the failure, allowing the MCU to perform rescue operations. If the HSE output was used as clock source for the PSI reference clock when the failure occurred, the oscillator is also disabled.

If an HSE clock failure occurs when the CSS is enabled, the CSS generates an interrupt that causes the automatic generation of an NMI. The HSECSSF flag in RCC_CIFR is set to 1 to allow the application to identify the failure source. The NMI routine is executed indefinitely until the HSECSSF bit is cleared. As a consequence, the application must clear the HSECSSF flag in the NMI ISR by setting the HSECSSC bit in RCC_CICR.

#### Clock security system on LSE

A clock security system on LSE can be activated by software writing the LSECSSON bit in RCC_RTCCR. This bit can be disabled only by a hardware reset or RTC software reset, or after a failure detection on LSE. LSECSSON must be written after LSE is enabled (LSEON enabled) and ready (LSERDY set by hardware), and after the RTC clock has been selected by RTCSEL.

The CSS on LSE is working in all modes. It also works under system reset (excluding power-on reset).

The clock security system on the LSE detects when the LSE disappears or in case of over frequency.

If a failure is detected on the external 32 kHz oscillator, the LSE clock is no longer supplied to the RTC, but no hardware action is made to the registers.

Note: If the LSECSS is enabled and the LSE clock fails, the LSECSSI occurs and an NMI is automatically generated. The NMI is executed infinitely unless the LSECSSF interrupt pending bit is cleared. It is therefore necessary that the NMI ISR clears the LSECSSI by setting the LSECSSC bit in the clock interrupt clear register (RCC_CICR).

In case of CSS on LSE detection event (LSECSSD = 1 in the RCC_RTCCR), the software must change the RTC clock source (no clock or LSI or HSE, with RTCSEL bitfield modification only possible while LSECSSD = 1) then disable the LSECSSON bit that clears the LSECSSD, stop the defective 32 kHz oscillator (disabling LSEON), or act to secure the application.

Refer to the datasheet for CSS on LSE electrical characteristics.

### 9.4.11 Clock output generation (MCO1/MCO2/LSCO)

Two microcontroller clock output pins (MCO1 and MCO2) are available. A clock source can be selected for each output. The selected clock can be divided thanks to a configurable prescaler (refer to Figure 25 for additional information on signal selection).

MCO1 and MCO2 outputs are controlled via MCO1PRE[3:0], MCO1[2:0], MCO2PRE[3:0], and MCO2[2:0], located in RCC_CFGR1.

The GPIO port corresponding to each MCO pin must be programmed in alternate function mode.

The clock provided to the MCOs outputs must not exceed the maximum pin speed (refer to the product datasheet for information on the supported speed). Under Stop 0, only PSIK, HSIK, and PSIDIV3 can be output on MCOx if they are kept enabled thanks to HSIKERON or PSIKERON.

Another output (LSCO) allows one of the low-speed clocks (LSI, LSE) to be output onto the external LSCO pin. This output is available in Stop mode, not available in Standby mode. The selection is controlled by the LSCOSEL bit, and enabled by the LSCOEN bit in RCC_RTCCR.

The MCO clock output requires the corresponding alternate function selected on the MCO pin. The LSCO pin must be left in the default POR state.

*Digest note:* The register fields are named MCO1SEL[2:0] and MCO2SEL[2:0] in Section 9.8.3 (the text above says MCO1[2:0]/MCO2[2:0]). MCOxPRE = 0000 means "prescaler disabled" (reset value), so an MCO output needs a non-zero MCOxPRE.

### 9.4.12 Kernel clock selection

Some peripherals are designed to work with two different clock domains that operate asynchronously:

- a clock domain synchronous with the register and bus interface (ckg_bus_perx clock)
- a clock domain generally synchronous with the peripheral (kernel clock)

The benefit of having peripherals supporting these two clock domains is that the user application has more freedom to choose an optimized clock frequency for the CPU, bus matrix and for the kernel part of the peripheral. The user application can thus change the bus frequency without reprogramming the peripherals. As an example, an ongoing transfer with UART is not disturbed if its APB clock is changed on-the-fly.

The table below shows the kernel clock that the RCC can deliver to the peripherals. Each row represents a multiplexer and the peripherals connected to its output.

**Table 69. Kernel clock distribution overview**

Each cell gives the multiplexer selection value that routes that clock to the peripheral; "-" means not selectable.

| Peripherals | Clock multiplexer control bits | Bus clocks(1) | psis_ck | psidiv3_ck | psik_ck | hsis_ck | hsidiv3_ck | hsik_ck | hse_ck | lse_ck | lsi_ck | AUDIOCLK | hse_1M_ck | Disabled |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| XSPI1 | XSPI1SEL | 0(2) | - | - | 1 | - | - | 2 | - | - | - | - | - | - |
| FDCANx | FDCANSEL | 0 | 1 | - | 2 | - | - | - | 3 | - | - | - | - | - |
| I2Cx | I2CxSEL | 0 | - | - | 1 | - | - | 2 | - | - | - | - | - | - |
| I3C1 | I3C1SEL | 0 | - | - | 1 | - | - | 2 | - | - | - | - | - | - |
| LPTIM1 | LPTIM1SEL | 0 | - | - | - | - | - | 1 | - | 2 | 3 | - | - | - |
| SPI(I2S)x | SPIxSEL | 0 | - | - | 1 | - | - | 2 | - | - | - | 3 | - | - |
| USARTx | USARTxSEL | 0 | - | - | 1 | - | - | 2 | - | 3 | - | - | - | - |
| UARTx | UARTxSEL | 0 | - | - | 1 | - | - | 2 | - | 3 | - | - | - | - |
| LPUART1 | LPUART1SEL | 0 | - | - | - | - | - | 1 | - | 2 | 3 | - | - | - |
| USB(CK48) | CK48SEL | - | - | 1 | - | - | 2 | - | 3 | - | - | - | - | 0 |
| ADCDAC | ADCDACSEL | 0(2) | 1 | - | 2 | - | - | 3 | - | - | - | - | - | - |
| DAC | DACSEL | - | - | - | - | - | - | - | - | 0 | 1 | - | - | - |
| RTC/AWU | RTCSEL | - | - | - | - | - | - | - | - | 1 | 2 | - | 3 | 0 |
| ETH1_CLK | ETH1CLKSEL | - | 1 | - | 2 | - | - | - | 3 | - | - | - | - | 0 |
| ETH1_PTP | ETH1PTPCLKSEL | 1 | 2 | - | 3 | - | - | - | - | - | - | - | - | 0 |

Notes:

1. The bus (APB or AHB) clocks are the bus interface clocks to whom the peripherals are connected.
2. When SYSCLK is divided by 2 or more, the AHB prescaler does not maintain the 50% duty cycle required by the ADC and XSPI in DDR mode. To achieve a 50% duty cycle, the ADCDACPRE or XSPI peripheral prescalers must divide HCLK by a factor of 2 or higher.

*Digest note:* Bus clock behind selection 0 per register (Section 9.8.29–9.8.31): FDCAN, SPI2, SPI3, USART2, USART3, UART4, UART5, USART6, UART7, I2C1, I2C2, I3C1 = rcc_pclk1; SPI1, USART1 = rcc_pclk2; LPUART1, LPTIM1 = rcc_pclk3; ADCDAC = rcc_hclk; XSPI1 = rcc_hclk4; ETH1_PTP selection 1 = rcc_hclk1. USB has no bus-clock option and is disabled at reset (CK48SEL = 00). The RNG kernel clock follows the same CK48 multiplexer (Figure 25, Figure 28).

#### Peripherals dedicated to control and data transfer

Peripherals such as SPIs, I2Cs, UARTs do not need a specific kernel clock frequency but a clock fast enough to generate the correct baud rate, or the required bit clock on the serial interface. For that purpose the source can be selected among the following ones:

- HSIS or HSIK if the clock must quickly be available upon Stop mode exit.
- PSIS or PSIK if an HSE clock is available and accuracy must be controlled over temperature or if a ratio of 100 MHz or 160 MHz is mandatory for some protocols.

Note: UARTs also can use the LSE clock when high baud rates are not required.

*Digest note:* Per Table 69 and Section 9.8.29/9.8.30, hsis_ck and psis_ck are not actually selectable for SPI, I2C, I3C or U(S)ART kernel clocks (only psik_ck and hsik_ck are); with PSIKDIV/HSIKDIV = /1 the PSIK/HSIK output equals the PSIS/HSIS frequency.

#### Clock distribution for ETH1

The Ethernet clocks provided by the RCC are available on ETH1_CLK pad. The application can select if the ETH1_CLK is generated from the PSIS, PSIK or from the HSE.

The RCC also provides the bus clock and the reference clock for the PTP function. The bus and PTP clocks generation are controlled via ETH1EN and ETH1LPEN bits.

The Ethernet transmit and receive clocks must be provided from an external Ethernet PHY.

**Figure 27. Clock distribution for ETH** (described; ST drawing MSv76147V1)

- The figure shows the RCC block (containing a "PKSU" kernel-clock selection area and a "PKEU" enable/gating area) feeding the ETH block. Yellow paths are MII, blue paths are RMII. Multiplexers marked "D" are dynamic: the transition between two inputs is glitch-free.
- Transmit clock: a multiplexer controlled by ETH_SEL_PHY[3:0] (SBS_PMCR; 0 = MII, 4 = RMII) selects input 0 = ETH_MII_TX_CLK pad (MII) or input 4 = the RMII divided clock. Its output is gated by logic driven by ETHTXEN/ETHTXLPEN and becomes clk_tx_i (MII tx clock 2.5/25 MHz) to the ETH.
- Receive clock: a second multiplexer controlled by ETH_SEL_PHY[3:0] selects input 0 = ETH_MII_RX_CLK pad (MII) or input 4 = the RMII divided clock. Its output is gated by ETHRXEN/ETHRXLPEN logic and becomes clk_rx_i (MII rx clock 2.5/25 MHz).
- RMII reference: a multiplexer controlled by ETHREFCLKSEL selects input 0 = the ETH_RMII_REF_CLK pad (shared with ETH_MII_RX_CLK) or input 1 = eth_clk_fb (the ETH_CLK output fed back). The selected 50 MHz reference goes (a) through a "÷ 2, 20" divider (FES[0] MAC speed from ETH_MACCR, mac_speed_o[1:0] from the ETH: 0 = ÷ 2 for 100 Mbps, 1 = ÷ 20 for 10 Mbps) to input 4 of both the TX and RX multiplexers, and (b) directly, gated by "ETHTXEN or ETHRXEN" / "ETHTXLPEN or ETHRXLPEN" logic, as clk_rmii_i (RMII reference clock 50 MHz).
- Bus clock: rcc_hclk1 gated by ETHEN/ETHLPEN logic becomes hclk_i.
- PTP reference: a dynamic multiplexer controlled by ETHPTPCLKSEL selects 1 = HCLK, 2 = PSIS, 3 = PSIK; output goes through ETHPTPDIV "÷ 1 to 16" and, gated by the same ETHEN/ETHLPEN logic, becomes clk_ptp_ref_i.
- ETH_CLK output: a dynamic multiplexer controlled by ETHCLKSEL selects 1 = PSIS, 2 = PSIK, 3 = HSE; output goes through a "÷ 1,2,4" divider (25/50/100 MHz) and, gated by ETHCKEN/ETHCKLPEN logic, drives the ETH_CLK pad; the pad signal is fed back as eth_clk_fb.

The signal ETH1_SEL_PHY is provided by the SBS block and defines the interface type:

- In MII mode (yellow path):
  - The transmit clock is received from the external PHY via the pad ETH_MII_TX_CLK.
  - The receive clock is received from the external PHY via the pad ETH_MII_RX_CLK.
  - The clock frequency is 2.5 (or 25) MHz for Ethernet at 10 (or 100) Mbps.
- In RMII mode (blue path):
  - The reference clock (50MHz) can be selected between two sources, this selection is controlled through ETH1REFCLKSEL.
  - The ETH_RMII_REF_CLK pad, if the reference clock is provided by the PHY.
  - The ETH1_CLK feedback clock (eth_clk_fb) if the RCC is providing the reference clock to the PHY.
- In RMII mode:
  - A clock must be provided to clk_rx_i and clk_tx_i inputs.
  - The clock frequency at clk_rx_i and clk_tx_i inputs is 2.5 MHz (division by 20) for Ethernet at 10 Mbps, and 25 MHz (division 2) for Ethernet at 100 Mbps.
  - The transmit and receive clock frequency can be adjusted dynamically to 2.5 to 25 MHz according to the signal mac_speed_o[0] (controlled by FES bit in ETH_MACCR register) provided by the ETH block.
  - The clock can be provided by RCC to be used by the external ETH PHY through ETH1_CLK output. This clock can be selected between three sources, this selection is controlled via ETH1CLKSEL.

*Digest note:* Figure 27 uses the names ETHREFCLKSEL, ETHPTPCLKSEL, ETHPTPDIV, ETHCLKSEL, ETHTXEN, ETHEN, ETHCKEN, etc.; the registers use the ETH1-prefixed names (ETH1REFCLKSEL, ETH1PTPCLKSEL, ETH1PTPDIV, ETH1CLKSEL, ETH1TXEN, ETH1EN, ETH1CKEN, ...). ETH1 is absent on STM32C55xxx.

#### Clock distribution for cryptographic subsystem

This subsection is only available for STM32C59x/5A3.

Figure 28 shows the clock distribution for the cryptographic subsystem.

Note: All the peripheral clocks of the cryptographic subsystem must be disabled before issuing a software reset to any CCB/PKA/RNG/SAES/HASH/AES peripheral of this subsystem. For any CCB/PKA/RNG/SAES/HASH/AES peripheral of this subsystem, the software must ensure that the peripheral is not busy (by polling on the BUSY bit flag of the related CCB/PKA/RNG/SAES/HASH/AES peripheral) before disabling the peripheral clock.

**Figure 28. Clock distribution for Crypton subsystem** (described; ST drawing MSv69970V1)

- The RCC (with a "PKEU" gating area) feeds the "Crypton" block. An ungated hclk2 goes directly to the Crypton block's common hclk input.
- CCB: hclk2 gated by logic driven by CCBEN/CCBLPEN becomes the CCB hclk. The CCB returns ccb_hclk_en to its own gating logic, and also outputs pka_hclk_en, rng_hclk_en and saes_hclk_en to the PKA, RNG and SAES gating logic respectively.
- PKA: hclk2 gated by logic driven by PKAEN/PKALPEN, pka_hclk_en, tamp_erase_req and rdp_erase_ram becomes the PKA hclk.
- RNG: hclk2 gated by RNGEN/RNGLPEN logic (with rng_hclk_en and the RNG's rng_ckreq request) becomes the RNG hclk; a kernel clock selected among PSI_DIV_3, HSE and HSI_DIV_3, gated by the same logic, becomes rng_clk.
- SAES: hclk2 gated by SAESEN/SAESLPEN logic (with saes_hclk_en) becomes the SAES hclk; a second gate on hclk2 produces saes_ker_ck.
- HASH: hclk2 gated by HASHEN/HASHLPEN logic becomes the HASH hclk.
- AES: hclk2 gated by AESEN/AESLPEN logic becomes the AES hclk.
- Legend: thick lines are bus interface clocks, thin lines are kernel clocks.

*Digest note:* On STM32C55xxx, RNG and HASH exist (AHB2), but not as part of this "Crypton" subsystem; CCB, PKA and SAES are absent.

#### RTC/AWU clock

The rtc_ck clock source can be one of the following:

- The hse_1M_ck (hse_ck divided by a programmable prescaler)
- The lse_ck
- The lsi_ck clock

The source clock is selected by programming the RTCSEL[1:0] bits in RCC_RTCCR and the RTCPRE[8:0] bits in RCC_CFGR1.

This selection cannot be modified without resetting the RTC domain.

The rtc_ck clock is enabled through the RTCEN bit in RCC_RTCCR.

The RTC bus interface clock (APB clock) is enabled through RTCAPBEN and RTCAPBLPEN bits located in RCC_APB3ENR/LPENR registers.

Note: To read the RTC calendar register when the APB clock frequency is less than seven times the RTC clock frequency (FAPB < 7 x FRTCLCK), the software must read the calendar time and date registers twice. The data are correct if the second read access to RTC_TR gives the same result than the first one. Otherwise, a third read access must be performed.

#### Watchdog clocks

The RCC provides the clock for the two watchdog blocks available on the circuit. The independent watchdog (IWDG) is connected to the LSI. The window watchdog (WWDG) is connected to the APB clock.

If an independent watchdog is started by either hardware option or software access, the LSI is forced on and cannot be disabled. After the LSI oscillator setup delay, the clock is provided to the IWDG.

#### Clock frequency measurement using TIMx

The HSI is not operating on a reference clock as the PSI. If the PSI cannot be the source to blocks requiring accurate frequency, it can be interesting to calibrate HSI thanks to timers or CRS. Most of the clock source generator frequencies can be measured by means of the input capture of TIMx.

- Calibrating the HSI with the LSE:
  The primary purpose of having the LSE connected to a TIMx input capture is to be able to accurately measure the HSI. This requires to use the HSI as the system clock source directly. The number of system clock counts between consecutive edges of the LSE signal gives a measurement of the internal clock period. Taking advantage of the high precision of LSE crystals (typically a few tens of ppm) we can determine the internal clock frequency with the same resolution, and trim the source to compensate for manufacturing-process and/or temperature- and voltage-related frequency deviations.
  The basic concept consists in providing a relative measurement (such as HSI/LSE ratio). The precision is therefore tightly linked to the ratio between the two clock sources. The greater the ratio is, the more accurate the measurement is.
  The HSI oscillator have dedicated user-accessible calibration bits for this purpose (see RCC_CFGR1).
- Calibrating the LSI with the HSI:
  The LSI frequency can also be measured: this is useful for applications that do not have a crystal. The ultra-low-power LSI oscillator has a large manufacturing process deviation. The LSI clock frequency can be measured using the more precise HSI clock source. Using this measurement, a more accurate RTC time base timeouts (when LSI is used as the RTC clock source) and/or an IWDG timeout with an acceptable accuracy can be obtained.

*Digest note:* RCC_CFGR1 (Section 9.8.3) contains no HSI calibration bits; HSI trimming is done through CRS_CR.TRIM[6:0] (Section 9.4.2, HSI calibration).

#### Clock frequency measurement using CRS

The HSI is as well directly connected to CRS block that can handle its TRIM automatically on HSE, LSE, USB SOF signal or external reference clock.

### 9.4.13 RTC and TAMP clock

The RTCCLK clock source is used by RTC and TAMP, and can be either the HSE_1MHz, LSE, or LSI clock. It is selected by programming the RTCSEL[1:0] bits in RCC_RTCCR. This selection cannot be modified without resetting the RTC domain. The system must always be configured so as to get a PCLK frequency greater than or equal to the RTCCLK frequency for a proper operation of the RTC. The TAMP does not require any kernel clock if only the backup registers are used, with tampers in edge detection mode. All other tamper detection modes require a kernel clock (refer to Section 40: Tamper and backup registers (TAMP) for more details).

The LSE is in the RTC domain, whereas the HSE and LSI clocks are not. Consequently, if the HSE clock divided by a prescaler is used as the RTC or TAMP clock, the RTC state is not guaranteed if the internal voltage regulator is powered off (removing power from the core domain) during Standby mode for example. Depending on the TAMP configuration, this one can remain functional if used in a mode that does not need any kernel clock.

When the RTC and TAMP clock is LSE or LSI, the RTC remains clocked and functional under system reset.

### 9.4.14 Timer clock

The timer clock frequencies (excluding LPTIM) are fixed and equal to HCLK.

### 9.4.15 Peripherals clock gating

#### Peripherals clock gating in Run mode

Each peripheral clock can be enabled by the corresponding EN bit in the RCC_AHBxENR and RCC_APBxENR registers.

When the peripheral clock is not active, read or write accesses to the peripheral registers are not supported.

The enable bit has a synchronization mechanism to create a glitch-free clock for the peripheral. After the enable bit is set, there the clock is active after 2 cycles of the peripheral bus clock.

Caution: Just after enabling the clock for a peripheral, the software must wait for these 2 clock cycles before accessing the peripheral registers.

#### Peripherals clock gating in Sleep mode

When a peripheral is enabled, its clock can be automatically gated off when the device is in Sleep mode, by clearing the peripheral LPEN bit in the RCC_AHBxLPENR and RCC_APBxLPENR registers. Both EN and LPEN bit of the peripheral must be set to keep the clock on in Sleep mode.

## 9.5 RCC privilege functional description

By default, after reset, all RCC registers can be read or written with both privileged and unprivileged access except RCC_PRIVCFGR that can be written with privileged access only. RCC_PRIVCFGR can be read by privileged and unprivileged access.

The PRIV bit in RCC_PRIVCFGR can be written with privileged access only. This bit configures the privileged access of all RCC functions.

When the PRIV bit is set in RCC_PRIVCFGR:

- Writing the RCC bits is possible only with privileged access.
- The RCC bits can be read only with privileged access except RCC_PRIVCFGR that can be read by privileged or unprivileged access.
- An unprivileged access to a privileged RCC bit or register is discarded: the bits are read as zero and the write to these bits is ignored (RAZ/WI).

## 9.6 RCC low-power modes

- AHB and APB peripheral clocks, including DMA clock, can be disabled by software.
- Sleep mode stops the CPU clock. The memory interface clocks (flash memory, cache, and all SRAM interfaces) can be stopped by software during Sleep mode. The AHB to APB bridge clocks are disabled by hardware during Sleep mode when all the clocks of the peripherals connected to them are disabled.
- Stop 0 mode stops all the clocks in the core domain and disable the HSI, PSI, and HSE oscillators. However, HSI and PSI can be kept on (if HSIKERON or PSIKERON are set) or HSI can be started by a peripheral to generate a wake-up interrupt. LSI and LSE remain active in Stop 0 mode.
- Stop 1 mode stops all the clocks in the core domain and disable the HSI, PSI, and HSE oscillators. LSI and LSE remain active in Stop 1 mode.
- Standby mode stops all the clocks in the core domain and disable the HSI, the PSI, and HSE oscillators.

The CPU DeepSleep mode can be overridden for debugging by setting the DBG_STOP or DBG_STANDBY bit in the DBGMCU_CR register.

When exiting Stop mode, the system clock can be HSIS or HSIDIV3 based on the STOPWUCK value. The frequency (user trim) and the setting of the HSIK and PSIK prescaler are the one configured before entering Stop mode.

When leaving Standby mode, the system clock is HSIDIV3 (48 MHz). The user trim is lost.

If a flash memory programming operation is ongoing, a Stop or Standby mode entry is delayed until the flash memory interface access is finished. If an access to the APB domain is ongoing, a Stop or Standby mode entry is delayed until the APB access is finished.

## 9.7 RCC interrupts

The table below summarizes the interrupt sources and the way to control them.

**Table 70. Interrupt sources and control**

| Interrupt vector | Interrupt event flag | Description | Enable control bits | Interrupt clear method | Exit Sleep mode | Exit Stop and Standby modes |
|---|---|---|---|---|---|---|
| RCC | LSIRDYF | LSI ready | LSIRDYIE | Set LSIRDYC to 1 | Yes | No |
| RCC | LSERDYF | LSE ready | LSERDYIE | Set LSERDYC to 1 | Yes | No |
| RCC | PSISRDYF | PSIS ready | PSISRDYIE | Set PSISRDYC to 1 | Yes | No |
| RCC | PSIDIV3RDYF | PSIDIV3 ready | PSIDIV3RDYIE | Set PSIDIV3RDYC to 1 | Yes | No |
| RCC | HSIKRDYF | HSIK ready | HSIKRDYIE | Set HSIKRDYC to 1 | Yes | No |
| RCC | HSISRDYF | HSIS ready | HSISRDYIE | Set HSISRDYC to 1 | Yes | No |
| RCC | HSIDIV3RDYF | HSIDIV3 ready | HSIDIV3RDYIE | Set HSIDIV3RDYC to 1 | Yes | No |
| RCC | HSIKRDYF | HSIK ready | HSIKRDYIE | Set HSIKRDYC to 1 | Yes | No |
| RCC | HSERDYF | HSE ready | HSERDYIE | Set HSERDYC to 1 | Yes | No |
| TAMP | ITAMP3F(1) | LSE CSS failure | LSECSSON and ITAMP3E(1) and ITAMP3IE(1) | Set CITAMP3F(1) to 1 | Yes | Yes |
| NMI | LSECSSF | LSE CSS failure | LSECSSON(2) | Set LSECSSC to 1 | Yes | Yes |
| NMI | HSECSSF | HSE CSS failure | HSECSSON(3) | Set HSECSSC to 1 | Yes | No |

Notes:

1. The LSE CSS failure event (LSECSSD) is connected to TAMP internal tamper 3. To get the interrupt associated with this event, the internal tamper 3 must be enabled, and the internal tamper 3 interrupt must be enabled. The ITAMP3F, ITAMP3E, ITAMP3IE, and CITAMP3F bits are in the TAMP peripheral.
2. It is not possible to mask this interrupt when the security system feature is enabled (LSECSSON = 1).
3. It is not possible to mask this interrupt when the security system feature is enabled (HSECSSON = 1).

*Digest note:* The source table lists HSIKRDYF twice and omits PSIKRDYF; one of the two HSIKRDYF rows (most likely the fifth row, which sits among the PSI rows) presumably stands for PSIKRDYF / PSIKRDYIE / PSIKRDYC, which exist in RCC_CIFR/CIER/CICR bit 7.

## 9.8 RCC registers

For the actual availability of some peripherals and their related bits, check the datasheet or Table 3: Memory map and peripheral register boundary addresses. If not present, consider them reserved, and keep them at the reset value.

### 9.8.1 RCC clock control register (RCC_CR1)

Address offset: 0x000. Reset value: 0x0000 0022.

- **Bits 31:21** Reserved, must be kept at reset value.
- **Bit 20 HSEEXT** (rw): External high speed clock type in Bypass mode
  This bit is set and reset by software to select the external clock type (analog or digital). The external clock must be enabled with the HSEON bit to be used by the device. The HSEEXT bit can be written only if the HSE oscillator is disabled.
  - 0: HSE in analog mode (default after reset)
  - 1: HSE in digital mode
- **Bit 19 HSECSSON** (rs): HSE clock security system enable
  This bit is set by software to enable clock security system on HSE. This bit is "set only" (disabled by a system reset or when the system enters in Standby mode). When HSECSSON is set, the clock detector is enabled by hardware when the HSE is ready and disabled by hardware if an oscillator failure is detected.
  - 0: CSS on HSE off (clock detector off) (default after reset)
  - 1: CSS on HSE on (clock detector on if the HSE oscillator is stable, off if not).
- **Bit 18 HSEBYP** (rw): HSE clock bypass
  This bit is set and cleared by software to bypass the oscillator with an external clock. The external clock must be enabled with the HSEON bit to be used by the device. The HSEBYP bit can be written only if the HSE oscillator is disabled.
  - 0: HSE oscillator not bypassed (default after reset)
  - 1: HSE oscillator bypassed with an external clock
- **Bit 17 HSERDY** (r): HSE clock ready flag
  This bit is set by hardware to indicate that the HSE oscillator is stable.
  - 0: HSE clock not ready (default after reset)
  - 1: HSE clock ready
- **Bit 16 HSEON** (rw): HSE clock enable
  This bit is set and cleared by software. It is cleared by hardware to stop the HSE when entering Stop or Standby mode. This bit cannot be cleared if the HSE is used directly or indirectly (via SW mux) as system clock, or if the HSE is selected as reference clock for PSI with PSI enabled (PSISON bit or PSIDIV3ON bit or PSIKON bit set to 1).
  - 0: HSE off (default after reset)
  - 1: HSE on
- **Bit 15** Reserved, must be kept at reset value.
- **Bit 14 PSIKRDY** (r): PSIK clock ready flag
  This bit is set by hardware to indicate that the PSI oscillator divided clock is stable.
  - 0: PSIK clock not ready (default after reset)
  - 1: PSIK clock ready
- **Bit 13 PSIDIV3RDY** (r): PSIDIV3 clock ready flag
  This bit is set by hardware to indicate that the PSI oscillator divided by 3 clock is stable.
  - 0: PSIDIV3 clock not ready (default after reset)
  - 1: PSIDIV3 clock ready
- **Bit 12 PSISRDY** (r): PSIS clock ready flag
  This bit is set by hardware to indicate that the PSIS clock is stable.
  - 0: PSIS clock not ready (default after reset)
  - 1: PSIS clock ready
- **Bit 11 PSIKERON** (rw): PSI clock enable in Stop mode
  This bit is set and cleared by software to force maintain PSI enabled in Stop 0 mode, to be quickly available as kernel clock for some peripherals. This bit only impacts PSI if PSISON, PSIDIV3ON, or PSIKON is set.
  - 0: No effect on PSI (default after reset)
  - 1: PSI keep ON even in Stop 0 mode
- **Bit 10 PSIKON** (rw): PSIK clock enable
  This bit is set and reset by software to enable/disable PSIK clock for peripheral. This bit value is kept under Stop 0 if PSIKERON is set, otherwise it is cleared.
  - 0: PSIK off (default after reset)
  - 1: PSIK on
- **Bit 9 PSIDIV3ON** (rw): PSIDIV3 clock enable
  This bit is set and reset by software to enable/disable PSIDIV3 clock for peripheral. This bit value is kept under Stop 0 if PSIKERON is set, otherwise it is cleared.
  - 0: PSIDIV3 off (default after reset)
  - 1: PSIDIV3 on
- **Bit 8 PSISON** (rw): PSIS clock enable
  This bit is set and reset by software to enable/disable PSIS clock for peripheral and system. This bit value is kept under Stop 0 if PSIKERON is set, otherwise it is cleared. This bit cannot be cleared if the PSIS is used (via SW mux) as system clock.
  - 0: PSIS off (default after reset)
  - 1: PSIS on
- **Bit 7** Reserved, must be kept at reset value.
- **Bit 6 HSIKRDY** (r): HSIK clock ready flag
  This bit is set by hardware to indicate that the HSIK divided clock is stable.
  - 0: HSIK clock not ready (default after reset)
  - 1: HSIK clock ready
- **Bit 5 HSIDIV3RDY** (r): HSIDIV3 clock ready flag
  This bit is set by hardware to indicate that the HSI oscillator divided by 3 clock is stable.
  - 0: HSIDIV3 clock not ready (default after reset)
  - 1: HSIDIV3 clock ready
- **Bit 4 HSISRDY** (r): HSIS clock ready flag
  This bit is set by hardware to indicate that the HSIS clock is stable.
  - 0: HSIS clock not ready (default after reset)
  - 1: HSIS clock ready
- **Bit 3 HSIKERON** (rw): HSI clock enable in Stop mode
  This bit is set and cleared by software to maintain HSI enabled in Stop 0 mode, to be quickly available as kernel clock for some peripherals. This bit only impact HSI if HSISON, HSIDIV3ON or HSIKON are set.
  - 0: No effect on HSI (default after reset)
  - 1: HSI keep ON in Stop 0 mode
- **Bit 2 HSIKON** (rw): HSIK clock enable
  This bit is set and reset by software to enable/disable HSIK clock for peripheral. This bit value is kept under Stop 0 mode if HSIKERON is set, otherwise it is cleared.
  - 0: HSIK off (default after reset)
  - 1: HSIK on
- **Bit 1 HSIDIV3ON** (rw): HSIDIV3 clock enable
  This bit is set and reset by software to enable/disable HSIDIV3 clock for system or peripheral. It is set by hardware to force the HSIDIV3 to on when product exit Standby mode, or in case of a failure of the HSE which is used directly or indirectly as the system clock source. This bit cannot be cleared if the HSIDIV3 is used directly (via SW mux) as system clock. This bit value is kept under Stop 0 mode if HSIKERON is set, otherwise it is cleared.
  This bit is set by hardware to force the HSIDIV3 to on when the system leaves Stop mode, if STOPWUCK = 0.
  - 0: HSIDIV3 off
  - 1: HSIDIV3 on (default after reset)
- **Bit 0 HSISON** (rw): HSIS clock enable
  This bit is set and cleared by software to enable/disable HSIS clock for system and peripheral. This bit is set by hardware to force the HSI to on when the product leaves Stop mode, if STOPWUCK = 1. This bit value is kept under Stop 0 mode if HSIKERON is set, otherwise it is cleared. This bit cannot be cleared if the HSIS is used directly or indirectly (via SW mux) as system clock.
  - 0: HSIS off (default after reset)
  - 1: HSIS on

*Digest note:* The reset value 0x0000 0022 means HSIDIV3ON = 1 and HSIDIV3RDY = 1 (CMSIS `RCC_CR1_Rst` = 0x00000022 agrees). The register map (Table 71) shows a reset value of 0 for HSIDIV3RDY; the HSIDIV3RDY description does not state a reset default. HSISON = 0 at reset: the 144 MHz HSIS output must be enabled before switching SYSCLK to it.

### 9.8.2 RCC clock control register (RCC_CR2)

Address offset: 0x004. Reset value: 0x0000 0000.

- **Bits 31:30** Reserved, must be kept at reset value.
- **Bits 29:28 PSIFREQ[1:0]** (rw): PSI target frequency configuration
  This bitfield is set and reset by software to configure the PSI oscillator target frequency. Each bit can be written only if the PSI oscillator is disabled.
  - 00: PSI nominal frequency = 100 MHz
  - 01: PSI nominal frequency = 144 MHz
  - 1x: PSI nominal frequency = 160 MHz
- **Bits 27:23** Reserved, must be kept at reset value.
- **Bits 22:20 PSIREF[2:0]** (rw): PSI reference clock frequency selection
  This bitfield is set and cleared by software to indicate the adequate reference frequency connected to the PSI oscillator. Each bit can be written only if the PSI oscillator is disabled.
  - 000: 32.768 kHz
  - 001: 8 MHz
  - 010: 16 MHz
  - 011: 24 MHz
  - 100: 25 MHz
  - 101: 32 MHz
  - 110: 48 MHz
  - 111: 50 MHz
- **Bits 19:18** Reserved, must be kept at reset value.
- **Bits 17:16 PSIREFSRC[1:0]** (rw): PSI reference clock source selection
  This bitfield is set and cleared by software to indicate the adequate reference clock source connected to the PSI oscillator. Each bit can be written only if the PSI oscillator is disabled.
  - 00: HSE clock used as reference for PSI
  - 01: LSE clock used as reference for PSI
  - 10: HSI clock divided by 18 used as reference for PSI
- **Bits 15:12** Reserved, must be kept at reset value.
- **Bits 11:8 PSIKDIV[3:0]** (rw): PSI clock out divider factor
  This bitfield is set and cleared by software to configure the PSIK clock based on PSI and its division factor.
  - 0000: PSI clock divided by 1
  - 0001: PSI clock divided by 1
  - 0010: PSI clock divided by 1.5
  - 0011: PSI clock divided by 2
  - 0100: PSI clock divided by 2.5
  - ....
  - 1110: PSI clock divided by 7.5
  - 1111: PSI clock divided by 8
- **Bits 7:4** Reserved, must be kept at reset value.
- **Bits 3:0 HSIKDIV[3:0]** (rw): HSI clock out divider factor
  This bitfield is set and cleared by software to configure the HSIK clock based on HSI and its division factor.
  - 0000: HSI clock divided by 1
  - 0001: HSI clock divided by 1
  - 0010: HSI clock divided by 1.5
  - 0011: HSI clock divided by 2
  - 0100: HSI clock divided by 2.5
  - ....
  - 1110: HSI clock divided by 7.5
  - 1111: HSI clock divided by 8

*Digest note:* "PSI oscillator is disabled" for the PSIFREQ/PSIREF/PSIREFSRC write restriction is not defined more precisely here; RCC_CR1.HSEON/LSEON descriptions treat the PSI as enabled when PSISON, PSIDIV3ON or PSIKON is 1. PSIREFSRC = 11 is not listed. For PSIKDIV/HSIKDIV, code n ≥ 1 gives division (n + 1) / 2 (pattern of the listed values). The valid PSIFREQ/PSIREFSRC/PSIREF combinations are those of Table 66.

### 9.8.3 RCC clock configuration register1 (RCC_CFGR1)

Address offset: 0x01C. Reset value: 0x0000 0000.

Access: 0 ≤ wait state ≤ 2; word and half-word access. One or two wait states are inserted only if the access occurs during the clock source switch.

- **Bits 31:29 MCO2SEL[2:0]** (rw): Microcontroller clock output 2
  This bitfield is set and cleared by software. Clock source selection may generate glitches on MCO2. It is highly recommended to configure these bits only after reset, before enabling the external oscillators.
  - 000: system clock selected (sys_ck) (default after reset)
  - 001: HSE clock selected (hse_ck)
  - 010: LSE clock selected (lse_ck)
  - 011: LSI clock selected (lsi_ck)
  - 100: PSIK clock selected (psik_ck)
  - 101: HSIK clock selected (hsik_ck)
  - 110: PSIDIV3 clock selected (psidiv3_ck)
  - 111: HSIDIV3 clock selected (hsidiv3_ck): if this clock is retained by HSIKERON, it is not visible on MCO output under the Stop 0 mode.
  - Other: Reserved
- **Bits 28:25 MCO2PRE[3:0]** (rw): MCO2 prescaler
  This bitfield is set and cleared by software to configure the prescaler of the MCO2. Modification of this prescaler may generate glitches on MCO2. It is highly recommended to change this prescaler only after reset, before enabling the external oscillators and the PLLs.
  - 0000: Prescaler disabled (default after reset)
  - 0001: Division by 1 (bypass)
  - 0010: Division by 2
  - 0011: Division by 3
  - 0100: Division by 4
  - ...
  - 1111: Division by 15
- **Bits 24:22 MCO1SEL[2:0]** (rw): Microcontroller clock output 1
  This bitfield is set and cleared by software. Clock source selection may generate glitches on MCO1. It is highly recommended to configure these bits only after reset, before enabling the external oscillators.
  - 000: System clock selected (sys_ck) (default after reset)
  - 001: HSE clock selected (hse_ck)
  - 010: LSE clock selected (lse_ck)
  - 011: LSI clock selected (lsi_ck)
  - 100: PSIK clock selected (psik_ck)
  - 101: HSIK clock selected (hsik_ck)
  - 110: PSIS clock selected (psis_ck), if this clock is retained by PSIKERON, it is not visible on MCO output under the Stop 0 mode.
  - 111: HSIS clock selected (hsis_ck), if this clock is retained by HSIKERON, it is not visible on MCO output under the Stop 0 mode.
  - Other: Reserved
- **Bits 21:18 MCO1PRE[3:0]** (rw): MCO1 prescaler
  This bitfield is set and cleared by software to configure the prescaler of the MCO1. Modification of this prescaler may generate glitches on MCO1. It is highly recommended to change this prescaler only after reset, before enabling the external oscillators and the PLLs.
  - 0000: Prescaler disabled (default after reset)
  - 0001: Division by 1 (bypass)
  - 0010: Division by 2
  - 0011: Division by 3
  - 0100: Division by 4
  - ...
  - 1111: Division by 15
- **Bits 17:16** Reserved, must be kept at reset value.
- **Bits 15:7 RTCPRE[8:0]** (rw): HSE division factor for RTC clock (source of HSE_1MHz clock)
  This bitfield is set and cleared by software to divide the HSE to generate a clock for RTC.
  Caution: Software must set these bits correctly to ensure that the clock supplied to the RTC is lower than 1 MHz. These bits must be configured if needed before selecting the RTC clock source.
  - 000000000: No clock (default after reset)
  - 000000001: No clock
  - 000000010: HSE/2
  - 000000011: HSE/3
  - 000000100: HSE/4
  - ...
  - 111111110: HSE/510
  - 111111111: HSE/511
- **Bit 6 STOPWUCK** (rw): System clock selection after a wake-up from system Stop mode
  This bit is set and reset by software to select the system wake-up clock from system Stop.
  - 0: HSIDIV3 selected as wake-up clock from system Stop mode (default after reset)
  - 1: HSIS selected as wake-up clock from system Stop mode
- **Bit 5** Reserved, must be kept at reset value.
- **Bits 4:3 SWS[1:0]** (r): System clock switch status
  This bitfield is set and reset by hardware to indicate which clock source is used as system clock.
  - 00: HSIDIV3 used as system clock (hsidiv3_ck) (default after reset).
  - 01: HSIS used as system clock (hsis_ck)
  - 10: HSE used as system clock (hse_ck)
  - 11: PSIS used as system clock (psis_ck)
- **Bit 2** Reserved, must be kept at reset value.
- **Bits 1:0 SW[1:0]** (rw): System clock and trace clock switch
  This bitfield is set and reset by software to select system clock and trace clock sources (sys_ck). It is set by hardware to force the selection of the HSI or CSI (depending on STOPWUCK selection) when leaving a system Stop mode, and to force the selection of the HSI in case of failure of the HSE when used directly or indirectly as system clock
  - 00: HSIDIV3 selected as system clock (hsidiv3_ck) (default after reset)
  - 01: HSIS selected as system clock (hsis_ck)
  - 10: HSE selected as system clock (hse_ck)
  - 11: PSIS selected as system clock (psis_ck)

*Digest note:* There is no CSI on STM32C5; "HSI or CSI (depending on STOPWUCK selection)" corresponds, per STOPWUCK and Section 9.4.9, to HSIDIV3 (SW = 00) or HSIS (SW = 01), and an HSE failure forces HSIDIV3 (Section 9.4.10). The MCO prescaler descriptions mention "PLLs"; the STM32C5 RCC has no PLL (the PSI is the programmable source).

### 9.8.4 RCC CPU domain clock configuration register 2 (RCC_CFGR2)

Address offset: 0x020. Reset value: 0x0000 0000.

1 or 2 wait states are inserted only if the access occurs during the clock source switch. From 0 to 15 wait states are inserted if the access occurs when the APB or AHB prescalers values update is ongoing.

- **Bits 31:23** Reserved, must be kept at reset value.
- **Bit 22 APB3DIS** (rw): APB3 clock disable value. Set and cleared by software
  This bit can be set to further reduce power consumption, when none of the APB3 peripherals are used, and when their clocks are disabled in RCC_APB3ENR. When this bit is set, all the APB3 peripheral clocks are off.
  - 0: APB3 clock enabled, distributed to peripherals according to their dedicated clock enable control bits
  - 1: APB3 clock disabled
- **Bit 21 APB2DIS** (rw): APB2 clock disable value
  This bit can be set to further reduce power consumption, when none of the APB2 peripherals are used, and when their clocks are disabled in RCC_APB2ENR. When this bit is set, all the APB2 peripheral clocks are off.
  - 0: APB2 clock enabled, distributed to peripherals according to their dedicated clock enable control bits
  - 1: APB2 clock disabled
- **Bit 20 APB1DIS** (rw): APB1 clock disable value
  This bit can be set to further reduce power consumption, when none of the APB1 peripherals (except IWDG) are used, and when their clocks are disabled in RCC_APB1ENR. When this bit is set, all the APB1 peripheral clocks are off, except for IWDG.
  - 0: APB1 clock enabled, distributed to peripherals according to their dedicated clock enable control bits
  - 1: APB1 clock disabled
- **Bit 19 AHB4DIS** (rw): AHB4 clock disable value
  This bit can be set to further reduce power consumption, when none of the AHB4 peripherals from RCC_AHB4ENR are used, and when their clocks are disabled in RCC_AHB4ENR. When this bit is set, all the AHB4 peripheral clocks are off.
  - 0: AHB4 clock enabled, distributed to peripherals according to their dedicated clock enable control bits
  - 1: AHB4 clock disabled
- **Bit 18** Reserved, must be kept at reset value.
- **Bit 17 AHB2DIS** (rw): AHB2 clock disable
  This bit can be set to further reduce power consumption, when none of the AHB2 peripherals from RCC_AHB2ENR are used, and when their clocks are disabled in RCC_AHB2ENR. When this bit is set, all the AHB2 peripheral clocks are off.
  - 0: AHB2 clock enabled, distributed to peripherals according to their dedicated clock enable control bits
  - 1: AHB2 clock disabled
- **Bit 16 AHB1DIS** (rw): AHB1 clock disable
  This bit can be set to further reduce power consumption, when none of the AHB1 peripherals from RCC_AHB1ENR are used, and when their clocks are disabled in RCC_AHB1ENR. When this bit is set, all the AHB1 peripheral clocks are off, except for FLASH, ICACHE, SRAM1, and SRAM2.
  - 0: AHB1 clock enabled, distributed to peripherals according to their dedicated clock enable control bits
  - 1: AHB1 clock disabled
- **Bit 15** Reserved, must be kept at reset value.
- **Bits 14:12 PPRE3[2:0]** (rw): APB low-speed prescaler (APB3)
  This bitfield is set and reset by software to control APB low-speed clocks division factor. The clocks are divided with the new prescaler factor from 1 to 16 APB cycles after PPRE3 write.
  - 0xx: rcc_pclk3 = rcc_hclk1
  - 100: rcc_pclk3 = rcc_hclk1 / 2
  - 101: rcc_pclk3 = rcc_hclk1 / 4
  - 110: rcc_pclk3 = rcc_hclk1 / 8
  - 111: rcc_pclk3 = rcc_hclk1 / 16
- **Bit 11** Reserved, must be kept at reset value.
- **Bits 10:8 PPRE2[2:0]** (rw): APB high-speed prescaler (APB2)
  This bitfield is set and reset by software to control APB high-speed clocks division factor. The clocks are divided with the new prescaler factor from 1 to 16 APB cycles after PPRE2 write.
  - 0xx: rcc_pclk2 = rcc_hclk1
  - 100: rcc_pclk2 = rcc_hclk1 / 2
  - 101: rcc_pclk2 = rcc_hclk1 / 4
  - 110: rcc_pclk2 = rcc_hclk1 / 8
  - 111: rcc_pclk2 = rcc_hclk1 / 16
- **Bit 7** Reserved, must be kept at reset value.
- **Bits 6:4 PPRE1[2:0]** (rw): APB low-speed prescaler (APB1)
  This bitfield is set and reset by software to control the division factor of rcc_pclk1. The clock is divided by the new prescaler factor from 1 to 16 cycles of rcc_hclk after PPRE write.
  - 0xx: rcc_pclk1 = rcc_hclk1 (default after reset)
  - 100: rcc_pclk1 = rcc_hclk1 / 2
  - 101: rcc_pclk1 = rcc_hclk1 / 4
  - 110: rcc_pclk1 = rcc_hclk1 / 8
  - 111: rcc_pclk1 = rcc_hclk1 / 16
- **Bits 3:0 HPRE[3:0]** (rw): AHB prescaler
  This bitfield is set and reset by software to control the division factor of rcc_hclk. Changing this division ratio has an impact on the frequency of all bus matrix clocks
  - 0xxx: rcc_hclk = sys_ck (default after reset)
  - 1000: rcc_hclk = sys_ck / 2
  - 1001: rcc_hclk = sys_ck / 4
  - 1010: rcc_hclk = sys_ck / 8
  - 1011: rcc_hclk = sys_ck / 16
  - 1100: rcc_hclk = sys_ck / 64
  - 1101: rcc_hclk = sys_ck / 128
  - 1110: rcc_hclk = sys_ck / 256
  - 1111: rcc_hclk = sys_ck / 512

*Digest note:* HPRE has no /32 setting (1011 = /16, 1100 = /64). The AHB/APB maximum is 144 MHz (Section 9.4), equal to the SYSCLK maximum, so /1 everywhere is valid at 144 MHz. The CMSIS header for STM32C552 has no AHB4DIS bit (no AHB4 peripherals on STM32C55xxx).

### 9.8.5 RCC clock source interrupt enable register (RCC_CIER)

Address offset: 0x050. Reset value: 0x0000 0000.

- **Bits 31:9** Reserved, must be kept at reset value.
- **Bit 8 HSERDYIE** (rw): HSE ready interrupt enable
  This bit is set and reset by software to enable/disable interrupt caused by the HSE oscillator stabilization.
  - 0: HSE ready interrupt disabled (default after reset)
  - 1: HSE ready interrupt enabled
- **Bit 7 PSIKRDYIE** (rw): PSIK ready interrupt enable
  This bit is set and reset by software to enable/disable interrupt caused by the PSIK clock stabilization.
  - 0: PSIK ready interrupt disabled (default after reset)
  - 1: PSIK ready interrupt enabled
- **Bit 6 PSIDIV3RDYIE** (rw): PSIDIV3 ready interrupt enable
  This bit is set and reset by software to enable/disable interrupt caused by the PSIDIV3 clock stabilization.
  - 0: PSIDIV3 ready interrupt disabled (default after reset)
  - 1: PSIDIV3 ready interrupt enabled
- **Bit 5 PSISRDYIE** (rw): PSIS ready interrupt enable
  This bit is set and reset by software to enable/disable interrupt caused by the PSIS clock stabilization.
  - 0: PSI ready interrupt disabled (default after reset)
  - 1: PSI ready interrupt enabled
- **Bit 4 HSIKRDYIE** (rw): HSIK ready interrupt enable
  This bit is set and reset by software to enable/disable interrupt caused by the HSIK clock stabilization.
  - 0: HSIK ready interrupt disabled (default after reset)
  - 1: HSIK ready interrupt enabled
- **Bit 3 HSIDIV3RDYIE** (rw): HSIDIV3 ready interrupt enable
  This bit is set and reset by software to enable/disable interrupt caused by the HSIDIV3 clock stabilization.
  - 0: HSIDIV3 ready interrupt disabled (default after reset)
  - 1: HSIDIV3 ready interrupt enabled
- **Bit 2 HSISRDYIE** (rw): HSIS ready interrupt enable
  This bit is set and reset by software to enable/disable interrupt caused by the HSIS clock stabilization.
  - 0: HSI ready interrupt disabled (default after reset)
  - 1: HSI ready interrupt enabled
- **Bit 1 LSERDYIE** (rw): LSE ready interrupt enable
  This bit is set and reset by software to enable/disable interrupt caused by the LSE oscillator stabilization.
  - 0: LSE ready interrupt disabled (default after reset)
  - 1: LSE ready interrupt enabled
- **Bit 0 LSIRDYIE** (rw): LSI ready interrupt enable
  This bit is set and reset by software to enable/disable interrupt caused by the LSI oscillator stabilization.
  - 0: LSI ready interrupt disabled (default after reset)
  - 1: LSI ready interrupt enabled

### 9.8.6 RCC clock source interrupt flag register (RCC_CIFR)

Address offset: 0x054. Reset value: 0x0000 0000.

- **Bits 31:12** Reserved, must be kept at reset value.
- **Bit 11 LSECSSF** (r): LSE clock security system interrupt flag
  Reset by software by writing LSECSSC bit. Set by hardware in case of LSE clock failure.
  - 0: No clock security interrupt caused by LSE clock failure (default after reset)
  - 1: Clock security interrupt caused by LSE clock failure
- **Bit 10 HSECSSF** (r): HSE clock security system interrupt flag
  Reset by software by writing HSECSSC bit. Set by hardware in case of HSE clock failure.
  - 0: No clock security interrupt caused by HSE clock failure (default after reset)
  - 1: Clock security interrupt caused by HSE clock failure
- **Bit 9** Reserved, must be kept at reset value.
- **Bit 8 HSERDYF** (r): HSE ready interrupt flag
  Reset by software by writing HSERDYC bit. Set by hardware when the HSE clock becomes stable and HSERDYIE is set.
  - 0: No clock ready interrupt caused by the HSE (default after reset)
  - 1: Clock ready interrupt caused by the HSE
- **Bit 7 PSIKRDYF** (r): PSIK ready interrupt flag
  Reset by software by writing PSIKRDYC bit.
  Set by hardware when the PSIK clock becomes stable and PSIKDYIE is set.
  - 0: No clock ready interrupt caused by PSIK (default after reset)
  - 1: Clock ready interrupt caused by PSIK
- **Bit 6 PSIDIV3RDYF** (r): PSIDIV3 ready interrupt flag
  Reset by software by writing PSIDIV3RDYC bit.
  Set by hardware when the PSIDIV3 clock becomes stable and PSIDIV3DYIE is set.
  - 0: No clock ready interrupt caused by PSIDIV3 (default after reset)
  - 1: Clock ready interrupt caused by PSIDIV3
- **Bit 5 PSISRDYF** (r): PSIS ready interrupt flag
  Reset by software by writing PSISRDYC bit.
  Set by hardware when the PSIS clock becomes stable and PSISDYIE is set.
  - 0: No clock ready interrupt caused by PSIS (default after reset)
  - 1: Clock ready interrupt caused by PSIS
- **Bit 4 HSIKRDYF** (r): HSIK ready interrupt flag
  Reset by software by writing HSIKRDYC bit.
  Set by hardware when the HSIK clock becomes stable and HSIKDYIE is set.
  - 0: No clock ready interrupt caused by HSIK (default after reset)
  - 1: Clock ready interrupt caused by HSIK
- **Bit 3 HSIDIV3RDYF** (r): HSIDIV3 ready interrupt flag
  Reset by software by writing HSIDIV3RDYC bit.
  Set by hardware when the HSIDIV3 clock becomes stable and HSIDIV3DYIE is set.
  - 0: No clock ready interrupt caused by HSIDIV3 (default after reset)
  - 1: Clock ready interrupt caused by HSIDIV3
- **Bit 2 HSISRDYF** (r): HSIS ready interrupt flag
  Reset by software by writing HSISRDYC bit.
  Set by hardware when the HSIS clock becomes stable and HSISDYIE is set.
  - 0: No clock ready interrupt caused by HSIS (default after reset)
  - 1: Clock ready interrupt caused by HSIS
- **Bit 1 LSERDYF** (r): LSE ready interrupt flag
  Reset by software by writing LSERDYC bit.
  Set by hardware when the LSE clock becomes stable and LSERDYIE is set.
  - 0: No clock ready interrupt caused by the LSE (default after reset)
  - 1: Clock ready interrupt caused by the LSE
- **Bit 0 LSIRDYF** (r): LSI ready interrupt flag
  Reset by software by writing LSIRDYC bit.
  Set by hardware when the LSI clock becomes stable and LSIRDYIE is set.
  - 0: No clock ready interrupt caused by the LSI (default after reset)
  - 1: Clock ready interrupt caused by the LSI

*Digest note:* "PSIKDYIE", "PSIDIV3DYIE", "PSISDYIE", "HSIKDYIE", "HSIDIV3DYIE" and "HSISDYIE" are as printed; the enable bits are named ...RDYIE in RCC_CIER.

### 9.8.7 RCC clock source interrupt clear register (RCC_CICR)

Address offset: 0x058. Reset value: 0x0000 0000.

- **Bits 31:12** Reserved, must be kept at reset value.
- **Bit 11 LSECSSC** (rc_w1): LSE clock security system interrupt clear
  Set by software to clear LSECSSF. Reset by hardware when clear done.
  - 0: LSECSSF no effect (default after reset)
  - 1: LSECSSF cleared
- **Bit 10 HSECSSC** (rc_w1): HSE clock security system interrupt clear
  Set by software to clear HSECSSF. Reset by hardware when clear done.
  - 0: HSECSSF no effect (default after reset)
  - 1: HSECSSF cleared
- **Bit 9** Reserved, must be kept at reset value.
- **Bit 8 HSERDYC** (rc_w1): HSE ready interrupt clear
  Set by software to clear HSERDYF. Reset by hardware when clear done.
  - 0: HSERDYF no effect (default after reset)
  - 1: HSERDYF cleared
- **Bit 7 PSIKRDYC** (rc_w1): PSIK ready interrupt clear
  Set by software to clear PSIKRDYF. Reset by hardware when clear done.
  - 0: PSIKRDYF no effect (default after reset)
  - 1: PSIKRDYF cleared
- **Bit 6 PSIDIV3RDYC** (rc_w1): PSIDIV3 ready interrupt clear
  Set by software to clear PSIDIV3RDYF. Reset by hardware when clear done.
  - 0: PSIDIV3RDYF no effect (default after reset)
  - 1: PSIDIV3RDYF cleared
- **Bit 5 PSISRDYC** (rc_w1): PSIS ready interrupt clear
  Set by software to clear PSISRDYF. Reset by hardware when clear done.
  - 0: PSISRDYF no effect (default after reset)
  - 1: PSISRDYF cleared
- **Bit 4 HSIKRDYC** (rc_w1): HSIK ready interrupt clear
  Set by software to clear HSIKRDYF. Reset by hardware when clear done.
  - 0: HSIKRDYF no effect (default after reset)
  - 1: HSIKRDYF cleared
- **Bit 3 HSIDIV3RDYC** (rc_w1): HSIDIV3 ready interrupt clear
  Set by software to clear HSIDIV3RDYF. Reset by hardware when clear done.
  - 0: HSIDIV3RDYF no effect (default after reset)
  - 1: HSIDIV3RDYF cleared
- **Bit 2 HSISRDYC** (rc_w1): HSIS ready interrupt clear
  Set by software to clear HSIRDYF. Reset by hardware when clear done.
  - 0: HSISRDYF no effect (default after reset)
  - 1: HSISRDYF cleared
- **Bit 1 LSERDYC** (rc_w1): LSE ready interrupt clear
  Set by software to clear LSERDYF. Reset by hardware when clear done.
  - 0: LSERDYF no effect (default after reset)
  - 1: LSERDYF cleared
- **Bit 0 LSIRDYC** (rc_w1): LSI ready interrupt clear
  Set by software to clear LSIRDYF. Reset by hardware when clear done.
  - 0: LSIRDYF no effect (default after reset)
  - 1: LSIRDYF cleared

*Digest note:* Access type "rc_w1" is as printed in the bit diagram (write 1 to clear the corresponding flag; the bit reads back 0 after the clear is done).

### 9.8.8 RCC AHB1 reset register (RCC_AHB1RSTR)

Address offset: 0x060. Reset value: 0x0000 0000.

- **Bits 31:20** Reserved, must be kept at reset value.
- **Bit 19 ETH1RST** (rw): ETHERNET reset
  Set and reset by software.
  - 0: ETHERNET not reset (default after reset)
  - 1: ETHERNET reset
- **Bit 18** Reserved, must be kept at reset value.
- **Bit 17 RAMCFGRST** (rw): RAMCFG reset
  Set and reset by software.
  - 0: RAMCFG not reset (default after reset)
  - 1: RAMCFG reset
- **Bits 16:15** Reserved, must be kept at reset value.
- **Bit 14 CORDICRST** (rw): CORDIC reset
  Set and reset by software.
  - 0: CORDIC not reset (default after reset)
  - 1: CORDIC reset
- **Bit 13** Reserved, must be kept at reset value.
- **Bit 12 CRCRST** (rw): CRC reset
  Set and reset by software.
  - 0: CRC not reset (default after reset)
  - 1: CRC reset
- **Bits 11:2** Reserved, must be kept at reset value.
- **Bit 1 LPDMA2RST** (rw): LPDMA2 reset
  Set and reset by software.
  - 0: LPDMA2 not reset (default after reset)
  - 1: LPDMA2 reset
- **Bit 0 LPDMA1RST** (rw): LPDMA1 reset
  Set and reset by software.
  - 0: LPDMA1 not reset (default after reset)
  - 1: LPDMA1 reset

*Digest note:* ETH1RST is absent on STM32C55xxx (not in the C552 header).

### 9.8.9 RCC AHB2 peripheral reset register (RCC_AHB2RSTR)

Address offset: 0x064. Reset value: 0x0000 0000.

- **Bits 31:25** Reserved, must be kept at reset value.
- **Bit 24 ADC3RST** (rw): ADC3 reset
  Set and reset by software.
  - 0: ADC3 not reset (default after reset)
  - 1: ADC3 reset
- **Bits 23:22** Reserved, must be kept at reset value.
- **Bit 21 CCBRST** (rw): CCB reset
  Set and reset by software.
  - 0: CCB not reset (default after reset)
  - 1: CCB reset
- **Bit 20 SAESRST** (rw): SAES reset
  Set and reset by software.
  - 0: SAES not reset (default after reset)
  - 1: SAES reset
- **Bit 19 PKARST** (rw): PKA reset
  Set and reset by software.
  - 0: PKA not reset (default after reset)
  - 1: PKA reset
- **Bit 18 RNGRST** (rw): RNG reset
  Set and reset by software.
  - 0: RNG not reset (default after reset)
  - 1: RNG reset
- **Bit 17 HASHRST** (rw): HASH reset
  Set and reset by software.
  - 0: HASH not reset (default after reset)
  - 1: HASH reset
- **Bit 16 AESRST** (rw): AES reset
  Set and reset by software.
  - 0: AES not reset (default after reset)
  - 1: AES reset
- **Bits 15:12** Reserved, must be kept at reset value.
- **Bit 11 DAC1RST** (rw): DAC reset
  Set and reset by software.
  - 0: DAC1 not reset (default after reset)
  - 1: DAC1 reset
- **Bit 10 ADC12RST** (rw): ADC1 and ADC2 reset
  Set and reset by software.
  - 0: ADC1 and ADC2 not reset (default after reset)
  - 1: ADC1 and ADC2 reset
- **Bits 9:8** Reserved, must be kept at reset value.
- **Bit 7 GPIOHRST** (rw): GPIOH reset
  Set and reset by software.
  - 0: GPIOH not reset (default after reset)
  - 1: GPIOH reset
- **Bit 6 GPIOGRST** (rw): GPIOG reset
  Set and reset by software.
  - 0: GPIOG not reset (default after reset)
  - 1: GPIOG reset
- **Bit 5 GPIOFRST** (rw): GPIOF reset
  Set and reset by software.
  - 0: GPIOF not reset (default after reset)
  - 1: GPIOF reset
- **Bit 4 GPIOERST** (rw): GPIOE reset
  Set and reset by software.
  - 0: GPIOE not reset (default after reset)
  - 1: GPIOE reset
- **Bit 3 GPIODRST** (rw): GPIOD reset
  Set and reset by software.
  - 0: e GPIOD not reset (default after reset)
  - 1: GPIOD reset
- **Bit 2 GPIOCRST** (rw): GPIOC reset
  Set and reset by software.
  - 0: GPIOC not reset (default after reset)
  - 1: GPIOC reset
- **Bit 1 GPIOBRST** (rw): GPIOB reset
  Set and reset by software.
  - 0: GPIOB not reset (default after reset)
  - 1: GPIOB reset
- **Bit 0 GPIOARST** (rw): GPIOA reset
  Set and reset by software.
  - 0: GPIOA not reset (default after reset)
  - 1: GPIOA reset

*Digest note:* On STM32C55xxx (C552 header) only GPIOA–GPIOE, GPIOH, ADC12, DAC1, HASH and RNG bits exist in this register; ADC3, CCB, SAES, PKA, AES, GPIOF and GPIOG are absent.

### 9.8.10 RCC AHB4 peripheral reset register (RCC_AHB4RSTR)

Address offset: 0x06C. Reset value: 0x0000 0000.

- **Bits 31:21** Reserved, must be kept at reset value.
- **Bit 20 XSPI1RST** (rw): XSPI1 reset
  Set and reset by software.
  - 0: XSPI1 not reset (default after reset)
  - 1: XSPI1 reset
- **Bits 19:0** Reserved, must be kept at reset value.

*Digest note:* XSPI1 is absent on STM32C55xxx; the C552 header has no RCC_AHB4RSTR (offset 0x06C is part of a reserved gap there).

### 9.8.11 RCC APB1 peripheral low reset register (RCC_APB1LRSTR)

Address offset: 0x074. Reset value: 0x0000 0000.

- **Bit 31** Reserved, must be kept at reset value.
- **Bit 30 UART7RST** (rw): UART7 reset
  Set and reset by software.
  - 0: UART7 not reset (default after reset)
  - 1: UART7 reset
- **Bits 29:26** Reserved, must be kept at reset value.
- **Bit 25 USART6RST** (rw): USART6 reset
  Set and reset by software.
  - 0: USART6 not reset (default after reset)
  - 1: USART6 reset
- **Bit 24 CRSRST** (rw): CRS reset
  Set and reset by software.
  - 0: CRS not reset (default after reset)
  - 1: CRS reset
- **Bit 23 I3C1RST** (rw): I3C1 block reset
  Set and reset by software.
  - 0: I3C1 not reset (default after reset)
  - 1: I3C1 reset
- **Bit 22 I2C2RST** (rw): I2C2 reset
  Set and reset by software.
  - 0: I2C2 not reset (default after reset)
  - 1: I2C2 reset
- **Bit 21 I2C1RST** (rw): I2C1 reset
  Set and reset by software.
  - 0: I2C1 not reset (default after reset)
  - 1: I2C1 reset
- **Bit 20 UART5RST** (rw): UART5 reset
  Set and reset by software.
  - 0: UART5 not reset (default after reset)
  - 1: UART5 reset
- **Bit 19 UART4RST** (rw): UART4 reset
  Set and reset by software.
  - 0: UART4 not reset (default after reset)
  - 1: UART4 reset
- **Bit 18 USART3RST** (rw): USART3 reset
  Set and reset by software.
  - 0: USART3 not reset (default after reset)
  - 1: USART3 reset
- **Bit 17 USART2RST** (rw): USART2 reset
  Set and reset by software.
  - 0: USART2 not reset (default after reset)
  - 1: USART2 reset
- **Bit 16** Reserved, must be kept at reset value.
- **Bit 15 SPI3RST** (rw): SPI3 reset
  Set and reset by software.
  - 0: SPI3 not reset (default after reset)
  - 1: SPI3 reset
- **Bit 14 SPI2RST** (rw): SPI2 reset
  Set and reset by software.
  - 0: SPI2 not reset (default after reset)
  - 1: SPI2 reset
- **Bit 13 OPAMP1RST** (rw): OPAMP1 reset
  Set and reset by software.
  - 0: OPAMP1 not reset (default after reset)
  - 1: OPAMP1 reset
- **Bits 12:7** Reserved, must be kept at reset value.
- **Bit 6 TIM12RST** (rw): TIM12 reset
  Set and reset by software.
  - 0: TIM12 not reset (default after reset)
  - 1: TIM12 reset
- **Bit 5 TIM7RST** (rw): TIM7 reset
  Set and reset by software.
  - 0: TIM7 not reset (default after reset)
  - 1: TIM7 reset
- **Bit 4 TIM6RST** (rw): TIM6 reset
  Set and reset by software.
  - 0: TIM6 not reset (default after reset)
  - 1: TIM6 reset
- **Bit 3 TIM5RST** (rw): TIM5 reset
  Set and reset by software.
  - 0: TIM5 not reset (default after reset)
  - 1: TIM5 reset
- **Bit 2 TIM4RST** (rw): TIM4 reset
  Set and reset by software.
  - 0: TIM4 not reset (default after reset)
  - 1: TIM4 reset
- **Bit 1 TIM3RST** (rw): TIM3 reset
  Set and reset by software.
  - 0: TIM3 not reset (default after reset)
  - 1: TIM3 reset
- **Bit 0 TIM2RST** (rw): TIM2 reset
  Set and reset by software.
  - 0: TIM2 not reset (default after reset)
  - 1: TIM2 reset

*Digest note:* On STM32C55xxx, UART7, USART6, TIM3 and TIM4 are absent (not in the C552 header; the datasheet lists 3 USARTs, 2 UARTs and 6 general-purpose timers TIM2/5/12/15/16/17). The C552 header does define OPAMP1RST/EN/LPEN although the datasheet lists no OPAMP; [unclear in source: whether OPAMP1 exists on STM32C55xxx].

### 9.8.12 RCC APB1 peripheral high reset register (RCC_APB1HRSTR)

Address offset: 0x078. Reset value: 0x0000 0000.

- **Bits 31:10** Reserved, must be kept at reset value.
- **Bit 9 FDCANRST** (rw): FDCAN1 and FDCAN2 reset
  Set and reset by software.
  - 0: FDCAN1 and FDCAN2 not reset (default after reset)
  - 1: FDCAN1 and FDCAN2 reset
- **Bits 8:4** Reserved, must be kept at reset value.
- **Bit 3 COMPRST** (rw): COMP reset
  Set and reset by software.
  - 0: COMP not reset (default after reset)
  - 1: COMP reset
- **Bits 2:0** Reserved, must be kept at reset value.

*Digest note:* The CMSIS header names this bit `RCC_APB1HRSTR_COMP12RST` (same position, bit 3). FDCANRST exists only on STM32C552xx (FDCAN1 only; no FDCAN2 on STM32C55xxx).

### 9.8.13 RCC APB2 peripheral reset register (RCC_APB2RSTR)

Address offset: 0x07C. Reset value: 0x0000 0000.

- **Bits 31:25** Reserved, must be kept at reset value.
- **Bit 24 USBRST** (rw): USB reset
  Set and reset by software.
  - 0: USB not reset (default after reset)
  - 1: USB reset
- **Bits 23:19** Reserved, must be kept at reset value.
- **Bit 18 TIM17RST** (rw): TIM17 reset
  Set and reset by software.
  - 0: TIM17 not reset (default after reset)
  - 1: TIM17 reset
- **Bit 17 TIM16RST** (rw): TIM16 reset
  Set and reset by software.
  - 0: TIM16 not reset (default after reset)
  - 1: TIM16 reset
- **Bit 16 TIM15RST** (rw): TIM15 reset
  Set and reset by software.
  - 0: TIM15 not reset (default after reset)
  - 1: TIM15 reset
- **Bit 15** Reserved, must be kept at reset value.
- **Bit 14 USART1RST** (rw): USART1 reset
  Set and reset by software.
  - 0: USART1 not reset (default after reset)
  - 1: USART1 reset
- **Bit 13 TIM8RST** (rw): TIM8 reset
  Set and reset by software.
  - 0: TIM8 not reset (default after reset)
  - 1: TIM8 reset
- **Bit 12 SPI1RST** (rw): SPI1 reset
  Set and reset by software.
  - 0: SPI1 not reset (default after reset)
  - 1: SPI1 reset
- **Bit 11 TIM1RST** (rw): TIM1 reset
  Set and reset by software.
  - 0: TIM1 not reset (default after reset)
  - 1: TIM1 reset
- **Bits 10:0** Reserved, must be kept at reset value.

### 9.8.14 RCC APB3 peripheral reset register (RCC_APB3RSTR)

Address offset: 0x080. Reset value: 0x0000 0000.

- **Bits 31:12** Reserved, must be kept at reset value.
- **Bit 11 LPTIM1RST** (rw): LPTIM1 reset
  Set and reset by software.
  - 0: LPTIM1 not reset (default after reset)
  - 1: LPTIM1 reset
- **Bits 10:7** Reserved, must be kept at reset value.
- **Bit 6 LPUART1RST** (rw): LPUART1 reset
  Set and reset by software.
  - 0: LPUART1 not reset (default after reset)
  - 1: LPUART1 reset
- **Bits 5:2** Reserved, must be kept at reset value.
- **Bit 1 SBSRST** (rw): SBS reset
  Set and reset by software.
  - 0: SBS not reset (default after reset)
  - 1: SBS reset
- **Bit 0** Reserved, must be kept at reset value.

### 9.8.15 RCC AHB1 peripheral clock register (RCC_AHB1ENR)

Address offset: 0x088. Reset value: 0xC000 0100.

- **Bit 31 SRAM1EN** (rw): SRAM1 clock enable
  Set and reset by software.
  - 0: SRAM1 clock disabled
  - 1: SRAM1 clock enabled (default after reset)
- **Bit 30 SRAM2EN** (rw): SRAM2 clock enable
  Set and reset by software.
  - 0: SRAM2 clock disabled
  - 1: SRAM2 clock enabled (default after reset)
- **Bits 29:22** Reserved, must be kept at reset value.
- **Bit 21 ETH1RXEN** (rw): ETH1RX clock enable
  Set and reset by software.
  - 0: ETH1RX clock disabled (default after reset)
  - 1: ETH1RX clock enabled
- **Bit 20 ETH1TXEN** (rw): ETH1TX clock enable
  Set and reset by software.
  - 0: ETH1TX clock disabled (default after reset)
  - 1: ETH1TX clock enabled
- **Bit 19 ETH1EN** (rw): ETH1 clock enable
  Set and reset by software.
  - 0: ETH1 clock disabled (default after reset)
  - 1: ETH1 clock enabled
- **Bit 18 ETH1CKEN** (rw): ETH1 internal clock enable
  Set and reset by software.
  - 0: ETH1 internal clock disabled (default after reset)
  - 1: ETH1 internal clock enabled
- **Bit 17 RAMCFGEN** (rw): RAMCFG clock enable
  Set and reset by software.
  - 0: RAMCFG clock disabled (default after reset)
  - 1: RAMCFG clock enabled
- **Bits 16:15** Reserved, must be kept at reset value.
- **Bit 14 CORDICEN** (rw): CORDIC clock enable
  Set and reset by software.
  - 0: CORDIC clock disabled (default after reset)
  - 1: CORDIC clock enabled
- **Bit 13** Reserved, must be kept at reset value.
- **Bit 12 CRCEN** (rw): CRC clock enable
  Set and reset by software.
  - 0: CRC clock disabled (default after reset)
  - 1: CRC clock enabled
- **Bits 11:9** Reserved, must be kept at reset value.
- **Bit 8 FLASHEN** (rw): Flash interface clock enable
  Set and reset by software.
  - 0: FLASH clock disabled
  - 1: FLASH clock enabled (default after reset)
- **Bits 7:2** Reserved, must be kept at reset value.
- **Bit 1 LPDMA2EN** (rw): LPDMA2 clock enable
  Set and reset by software.
  - 0: LPDMA2 clock disabled (default after reset)
  - 1: LPDMA2 clock enabled
- **Bit 0 LPDMA1EN** (rw): LPDMA1 clock enable
  Set and reset by software.
  - 0: LPDMA1 clock disabled (default after reset)
  - 1: LPDMA1 clock enabled

*Digest note:* ETH1RXEN/ETH1TXEN/ETH1EN/ETH1CKEN are absent on STM32C55xxx. The ICACHE has no clock enable bit here (only ICACHELPEN in RCC_AHB1LPENR).

### 9.8.16 RCC AHB2 peripheral clock register (RCC_AHB2ENR)

Address offset: 0x08C. Reset value: 0x0000 0000.

- **Bits 31:25** Reserved, must be kept at reset value.
- **Bit 24 ADC3EN** (rw): ADC3 clock enable
  Set and reset by software.
  - 0: ADC3 clock disabled (default after reset)
  - 1: ADC3 clock enabled
- **Bits 23:22** Reserved, must be kept at reset value.
- **Bit 21 CCBEN** (rw): CCB clock enable
  Set and reset by software.
  - 0: CCB clock disabled (default after reset)
  - 1: CCB clock enabled
- **Bit 20 SAESEN** (rw): SAES clock enable
  Set and reset by software.
  - 0: SAES clock disabled (default after reset)
  - 1: SAES clock enabled
- **Bit 19 PKAEN** (rw): PKA clock enable
  Set and reset by software.
  - 0: PKA clock disabled (default after reset)
  - 1: PKA clock enabled
- **Bit 18 RNGEN** (rw): RNG clock enable
  Set and reset by software.
  - 0: RNG clock disabled (default after reset)
  - 1: RNG clock enabled
- **Bit 17 HASHEN** (rw): HASH clock enable
  Set and reset by software.
  - 0: HASH clock disabled (default after reset)
  - 1: HASH clock enabled
- **Bit 16 AESEN** (rw): AES clock enable
  Set and reset by software.
  - 0: AES clock disabled (default after reset)
  - 1: AES clock enabled
- **Bits 15:12** Reserved, must be kept at reset value.
- **Bit 11 DAC1EN** (rw): DAC clock enable
  Set and reset by software.
  - 0: DAC1 clock disabled (default after reset)
  - 1: DAC1 clock enabled
- **Bit 10 ADC12EN** (rw): ADC1 and ADC2 clock enable
  Set and reset by software.
  - 0: ADC1 and ADC2 clock disabled (default after reset)
  - 1: ADC1 and ADC2 clock enabled
- **Bits 9:8** Reserved, must be kept at reset value.
- **Bit 7 GPIOHEN** (rw): GPIOH clock enable
  Set and reset by software.
  - 0: GPIOH clock disabled (default after reset)
  - 1: GPIOH clock enabled
- **Bit 6 GPIOGEN** (rw): GPIOG clock enable
  Set and reset by software.
  - 0: GPIOG clock disabled (default after reset)
  - 1: GPIOG clock enabled
- **Bit 5 GPIOFEN** (rw): GPIOF clock enable
  Set and reset by software.
  - 0: GPIOF clock disabled (default after reset)
  - 1: GPIOF clock enabled
- **Bit 4 GPIOEEN** (rw): GPIOE clock enable
  Set and reset by software.
  - 0: GPIOE clock disabled (default after reset)
  - 1: GPIOE clock enabled
- **Bit 3 GPIODEN** (rw): GPIOD clock enable
  Set and reset by software.
  - 0: GPIOD clock disabled (default after reset)
  - 1: GPIOD clock enabled
- **Bit 2 GPIOCEN** (rw): GPIOC clock enable
  Set and reset by software.
  - 0: GPIOC clock disabled (default after reset)
  - 1: GPIOC clock enabled
- **Bit 1 GPIOBEN** (rw): GPIOB clock enable
  Set and reset by software.
  - 0: GPIOB clock disabled (default after reset)
  - 1: GPIOB clock enabled
- **Bit 0 GPIOAEN** (rw): GPIOA clock enable
  Set and reset by software.
  - 0: GPIOA clock disabled (default after reset)
  - 1: GPIOA clock enabled

*Digest note:* On STM32C55xxx (C552 header) only GPIOAEN–GPIOEEN, GPIOHEN, ADC12EN, DAC1EN, HASHEN and RNGEN exist. All GPIO clocks are off after reset.

### 9.8.17 RCC AHB4 peripheral clock register (RCC_AHB4ENR)

Address offset: 0x094. Reset value: 0x0000 0000.

- **Bits 31:21** Reserved, must be kept at reset value.
- **Bit 20 XSPI1EN** (rw): XSPI1 clock enable
  Set and reset by software.
  - 0: XSPI1 peripheral clock disabled
  - 1: XSPI1 peripheral clock enabled
- **Bits 19:0** Reserved, must be kept at reset value.

*Digest note:* Absent on STM32C55xxx (no RCC_AHB4ENR in the C552 header).

### 9.8.18 RCC APB1 peripheral clock register (RCC_APB1LENR)

Address offset: 0x09C. Reset value: 0x0000 0000.

- **Bit 31** Reserved, must be kept at reset value.
- **Bit 30 UART7EN** (rw): UART7 clock enable
  Set and reset by software.
  - 0: UART7 clock disabled (default after reset)
  - 1: UART7 clock enabled
- **Bits 29:26** Reserved, must be kept at reset value.
- **Bit 25 USART6EN** (rw): USART6 clock enable
  Set and reset by software.
  - 0: USART6 clock disabled (default after reset)
  - 1: USART6 clock enabled
- **Bit 24 CRSEN** (rw): CRS clock enable
  Set and reset by software.
  - 0: CRS clock disabled (default after reset)
  - 1: CRS clock enabled
- **Bit 23 I3C1EN** (rw): I3C1 clock enable
  Set and reset by software.
  - 0: I3C1 clock disabled (default after reset)
  - 1: I3C1 clock enabled
- **Bit 22 I2C2EN** (rw): I2C2 clock enable
  Set and reset by software.
  - 0: I2C2 clock disabled (default after reset)
  - 1: I2C2 clock enabled
- **Bit 21 I2C1EN** (rw): I2C1 clock enable
  Set and reset by software.
  - 0: I2C1 clock disabled (default after reset)
  - 1: I2C1 clock enabled
- **Bit 20 UART5EN** (rw): UART5 clock enable
  Set and reset by software.
  - 0: UART5 clock disabled (default after reset)
  - 1: UART5 clock enabled
- **Bit 19 UART4EN** (rw): UART4 clock enable
  Set and reset by software.
  - 0: UART4 clock disabled (default after reset)
  - 1: UART4 clock enabled
- **Bit 18 USART3EN** (rw): USART3 clock enable
  Set and reset by software.
  - 0: USART3 clock disabled (default after reset)
  - 1: USART3 clock enabled
- **Bit 17 USART2EN** (rw): USART2 clock enable
  Set and reset by software.
  - 0: USART2 clock disabled (default after reset)
  - 1: USART2 clock enabled
- **Bit 16** Reserved, must be kept at reset value.
- **Bit 15 SPI3EN** (rw): SPI3 clock enable
  Set and reset by software.
  - 0: SPI3 clock disabled (default after reset)
  - 1: SPI3 clock enabled
- **Bit 14 SPI2EN** (rw): SPI2 clock enable
  Set and reset by software.
  - 0: SPI2 clock disabled (default after reset)
  - 1: SPI2 clock enabled
- **Bit 13 OPAMP1EN** (rw): OPAMP1 clock enable
  Set and reset by software.
  - 0: OPAMP1 clock disabled (default after reset)
  - 1: OPAMP1 clock enabled
- **Bit 12** Reserved, must be kept at reset value.
- **Bit 11 WWDGEN** (rs): WWDG clock enable
  Set by software and reset by hardware system reset.
  - 0: WWDG clock disabled (default after reset)
  - 1: WWDG clock enabled
- **Bits 10:7** Reserved, must be kept at reset value.
- **Bit 6 TIM12EN** (rw): TIM12 clock enable
  Set and reset by software.
  - 0: TIM12 clock disabled (default after reset)
  - 1: TIM12 clock enabled
- **Bit 5 TIM7EN** (rw): TIM7 clock enable
  Set and reset by software.
  - 0: TIM7 clock disabled (default after reset)
  - 1: TIM7 clock enabled
- **Bit 4 TIM6EN** (rw): TIM6 clock enable
  Set and reset by software.
  - 0: TIM6 clock disabled (default after reset)
  - 1: TIM6 clock enabled
- **Bit 3 TIM5EN** (rw): TIM5 clock enable
  Set and reset by software.
  - 0: TIM5 clock disabled (default after reset)
  - 1: TIM5 clock enabled
- **Bit 2 TIM4EN** (rw): TIM4 clock enable
  Set and reset by software.
  - 0: TIM4 clock disabled (default after reset)
  - 1: TIM4 clock enabled
- **Bit 1 TIM3EN** (rw): TIM3 clock enable
  Set and reset by software.
  - 0: TIM3 clock disabled (default after reset)
  - 1: TIM3 clock enabled
- **Bit 0 TIM2EN** (rw): TIM2 clock enable
  Set and reset by software.
  - 0: TIM2 clock disabled (default after reset)
  - 1: TIM2 clock enabled

*Digest note:* The RM section title reads "RCC APB1 peripheral clock register (RCC_APB1LENR)". On STM32C55xxx, UART7EN, USART6EN, TIM4EN and TIM3EN are absent (see the RCC_APB1LRSTR note, including the OPAMP1 question).

### 9.8.19 RCC APB1 peripheral clock register (RCC_APB1HENR)

Address offset: 0x0A0. Reset value: 0x0000 0000.

- **Bits 31:10** Reserved, must be kept at reset value.
- **Bit 9 FDCANEN** (rw): FDCAN1 and FDCAN2 clock enable
  Set and reset by software.
  - 0: FDCAN1 and FDCAN2 clock disabled (default after reset)
  - 1: FDCAN1 and FDCAN2 clock enabled
- **Bits 8:4** Reserved, must be kept at reset value.
- **Bit 3 COMPEN** (rw): COMP clock enable
  Set and reset by software.
  - 0: COMP clock disabled (default after reset)
  - 1: COMP clock enabled
- **Bits 2:0** Reserved, must be kept at reset value.

*Digest note:* CMSIS name `RCC_APB1HENR_COMP12EN` (bit 3). FDCANEN exists only on STM32C552xx.

### 9.8.20 RCC APB2 peripheral clock register (RCC_APB2ENR)

Address offset: 0x0A4. Reset value: 0x0000 0000.

- **Bits 31:25** Reserved, must be kept at reset value.
- **Bit 24 USBEN** (rw): USB clock enable
  Set and reset by software.
  - 0: USB clock disabled (default after reset)
  - 1: USB clock enabled
- **Bits 23:19** Reserved, must be kept at reset value.
- **Bit 18 TIM17EN** (rw): TIM17 clock enable
  Set and reset by software.
  - 0: TIM17 clock disabled (default after reset)
  - 1: TIM17 clock enabled
- **Bit 17 TIM16EN** (rw): TIM16 clock enable
  Set and reset by software.
  - 0: TIM16 clock disabled (default after reset)
  - 1: TIM16 clock enabled
- **Bit 16 TIM15EN** (rw): TIM15 clock enable
  Set and reset by software.
  - 0: TIM15 clock disabled (default after reset)
  - 1: TIM15 clock enabled
- **Bit 15** Reserved, must be kept at reset value.
- **Bit 14 USART1EN** (rw): USART1 clock enable
  Set and reset by software.
  - 0: USART1 clock disabled (default after reset)
  - 1: USART1 clock enabled
- **Bit 13 TIM8EN** (rw): TIM8 clock enable
  Set and reset by software.
  - 0: TIM8 clock disabled (default after reset)
  - 1: TIM8 clock enabled
- **Bit 12 SPI1EN** (rw): SPI1 clock enable
  Set and reset by software.
  - 0: SPI1 clock disabled (default after reset)
  - 1: SPI1 clock enabled
- **Bit 11 TIM1EN** (rw): TIM1 clock enable
  Set and reset by software.
  - 0: TIM1 clock disabled (default after reset)
  - 1: TIM1 clock enabled
- **Bits 10:0** Reserved, must be kept at reset value.

### 9.8.21 RCC APB3 peripheral clock register (RCC_APB3ENR)

Address offset: 0x0A8. Reset value: 0x0000 0000.

- **Bits 31:22** Reserved, must be kept at reset value.
- **Bit 21 RTCAPBEN** (rw): RTC APB interface clock enable
  Set and reset by software.
  - 0: RTC APB interface clock disabled (default after reset)
  - 1: RTC APB interface clock enabled
- **Bits 20:12** Reserved, must be kept at reset value.
- **Bit 11 LPTIM1EN** (rw): LPTIM1 clock enable
  Set and reset by software.
  - 0: LPTIM1 clock disabled (default after reset)
  - 1: LPTIM1 clock enabled
- **Bits 10:7** Reserved, must be kept at reset value.
- **Bit 6 LPUART1EN** (rw): LPUART1 clock enable
  Set and reset by software.
  - 0: LPUART1 clock disabled (default after reset)
  - 1: LPUART1 clock enabled
- **Bits 5:2** Reserved, must be kept at reset value.
- **Bit 1 SBSEN** (rw): SBS clock enable
  Set and reset by software.
  - 0: SBS clock disabled (default after reset)
  - 1: SBS clock enabled
- **Bit 0** Reserved, must be kept at reset value.

### 9.8.22 RCC AHB1 sleep clock register (RCC_AHB1LPENR)

Address offset: 0x0B0. Reset value: 0xC402 5103 (for STM32C53x/542/55x/562). Reset value: 0xC43E 5103 (for STM32C59x/5A3).

- **Bit 31 SRAM1LPEN** (rw): SRAM1 clock enable during Sleep mode
  Set and reset by software
  - 0: SRAM1 clock disabled during Sleep mode
  - 1: SRAM1 clock enabled during Sleep mode (default after reset)
- **Bit 30 SRAM2LPEN** (rw): SRAM2 clock enable during Sleep mode
  Set and reset by software
  - 0: SRAM2 clock disabled during Sleep mode
  - 1: SRAM2 clock enabled during Sleep mode (default after reset)
- **Bits 29:27** Reserved, must be kept at reset value.
- **Bit 26 ICACHELPEN** (rw): ICACHE clock enable during Sleep mode
  Set and reset by software.
  - 0: ICACHE clock disabled during Sleep mode
  - 1: ICACHE clock enabled during Sleep mode (default after reset)
- **Bits 25:22** Reserved, must be kept at reset value.
- **Bit 21 ETH1RXLPEN** (rw): ETH1RX clock enable during Sleep mode
  Set and reset by software.
  - 0: ETH1RX clock disabled during Sleep mode
  - 1: ETH1RX clock enabled during Sleep mode (default after reset)
- **Bit 20 ETH1TXLPEN** (rw): ETH1TX clock enable during Sleep mode
  Set and reset by software.
  - 0: ETH1TX clock disabled during Sleep mode
  - 1: ETH1TX clock enabled during Sleep mode (default after reset)
- **Bit 19 ETH1LPEN** (rw): ETH1 clock enable during Sleep mode
  Set and reset by software.
  - 0: ETH1 clock disabled during Sleep mode
  - 1: ETH1 clock enabled during Sleep mode (default after reset)
- **Bit 18 ETH1CLKLPEN** (rw): ETH1 internal clock enable during Sleep mode
  Set and reset by software.
  - 0: ETH1 internal clock disabled during Sleep mode
  - 1: ETH1 internal clock enabled during Sleep mode (default after reset)
- **Bit 17 RAMCFGLPEN** (rw): RAMCFG clock enable during Sleep mode
  Set and reset by software.
  - 0: RAMCFG clock disabled during Sleep mode
  - 1: RAMCFG clock enabled during Sleep mode (default after reset)
- **Bits 16:15** Reserved, must be kept at reset value.
- **Bit 14 CORDICLPEN** (rw): CORDIC clock enable during Sleep mode
  Set and reset by software.
  - 0: CORDIC clock disabled during Sleep mode
  - 1: CORDIC clock enabled during Sleep mode (default after reset)
- **Bit 13** Reserved, must be kept at reset value.
- **Bit 12 CRCLPEN** (rw): CRC clock enable during Sleep mode
  Set and reset by software.
  - 0: CRC clock disabled during Sleep mode
  - 1: CRC clock enabled during Sleep mode (default after reset)
- **Bits 11:9** Reserved, must be kept at reset value.
- **Bit 8 FLASHLPEN** (rw): Flash interface clock enable during Sleep mode
  Set and reset by software.
  - 0: FLASH clock disabled during Sleep mode
  - 1: FLASH clock enabled during Sleep mode (default after reset)
- **Bits 7:2** Reserved, must be kept at reset value.
- **Bit 1 LPDMA2LPEN** (rw): LPDMA2 clock enable during Sleep mode
  Set and reset by software.
  - 0: LPDMA2 clock disabled during Sleep mode
  - 1: LPDMA2 clock enabled during Sleep mode (default after reset)
- **Bit 0 LPDMA1LPEN** (rw): LPDMA1 clock enable during Sleep mode
  Set and reset by software.
  - 0: LPDMA1 clock disabled during Sleep mode
  - 1: LPDMA1 clock enabled during Sleep mode (default after reset)

*Digest note:* The two reset values differ only in bits 21:18 (ETH1 bits, 0 on devices without Ethernet). The register map (Table 71) labels bit 18 "ETH1CKLPEN". CMSIS `RCC_AHB1LPENR_Rst` = 0xC4025103 for STM32C551/C552.

### 9.8.23 RCC AHB2 sleep clock register (RCC_AHB2LPENR)

Address offset: 0x0B4. Reset value: 0x0007 0C9F (for STM32C53x/C542/C55x/C562). Reset value: 0x013F 0CFF (for STM32C59x/C5A3).

- **Bits 31:25** Reserved, must be kept at reset value.
- **Bit 24 ADC3LPEN** (rw): ADC3 clock enable during Sleep mode
  Set and reset by software.
  - 0: ADC3 clock disabled during Sleep mode
  - 1: ADC3 clock enabled during Sleep mode (default after reset)
- **Bits 23:22** Reserved, must be kept at reset value.
- **Bit 21 CCBLPEN** (rw): CCB clock enable during Sleep mode
  Set and reset by software.
  - 0: CCB clock disabled during Sleep mode
  - 1: CCB clock enabled during Sleep mode (default after reset)
- **Bit 20 SAESLPEN** (rw): SAES clock enable during Sleep mode
  Set and reset by software.
  - 0: SAES clock disabled during Sleep mode
  - 1: SAES clock enabled during Sleep mode (default after reset)
- **Bit 19 PKALPEN** (rw): PKA clock enable during Sleep mode
  Set and reset by software.
  - 0: PKAclock disabled during Sleep mode
  - 1: PKA clock enabled during Sleep mode (default after reset)
- **Bit 18 RNGLPEN** (rw): RNG clock enable during Sleep mode
  Set and reset by software.
  - 0: RNG clock disabled during Sleep mode
  - 1: RNG clock enabled during Sleep mode (default after reset)
- **Bit 17 HASHLPEN** (rw): HASH clock enable during Sleep mode
  Set and reset by software.
  - 0: HASH clock disabled during Sleep mode
  - 1: HASH clock enabled during Sleep mode (default after reset)
- **Bit 16 AESLPEN** (rw): AES clock enable during Sleep mode
  Set and reset by software.
  - 0: AES clock disabled during Sleep mode
  - 1: AES clock enabled during Sleep mode (default after reset)
- **Bits 15:12** Reserved, must be kept at reset value.
- **Bit 11 DAC1LPEN** (rw): DAC clock enable during Sleep mode
  Set and reset by software.
  - 0: DAC1 clock disabled during Sleep mode
  - 1: DAC1 clock enabled during Sleep mode (default after reset)
- **Bit 10 ADC12LPEN** (rw): ADC1 and ADC2 clock enable during Sleep mode
  Set and reset by software.
  - 0: ADC1 and ADC2 clock disabled during Sleep mode
  - 1: ADC1 and ADC2 clock enabled during Sleep mode (default after reset)
- **Bits 9:8** Reserved, must be kept at reset value.
- **Bit 7 GPIOHLPEN** (rw): GPIOH clock enable during Sleep mode
  Set and reset by software.
  - 0: GPIOH clock disabled during Sleep mode
  - 1: GPIOH clock enabled during Sleep mode (default after reset)
- **Bit 6 GPIOGLPEN** (rw): GPIOG clock enable during Sleep mode
  Set and reset by software.
  - 0: GPIOG clock disabled during Sleep mode
  - 1: GPIOG clock enabled during Sleep mode (default after reset)
- **Bit 5 GPIOFLPEN** (rw): GPIOF clock enable during Sleep mode
  Set and reset by software.
  - 0: GPIOF clock disabled during Sleep mode
  - 1: GPIOF clock enabled during Sleep mode (default after reset)
- **Bit 4 GPIOELPEN** (rw): GPIOE clock enable during Sleep mode
  Set and reset by software.
  - 0: GPIOE clock disabled during Sleep mode
  - 1: GPIOE clock enabled during Sleep mode (default after reset)
- **Bit 3 GPIODLPEN** (rw): GPIOD clock enable during Sleep mode
  Set and reset by software.
  - 0: GPIOD clock disabled during Sleep mode
  - 1: GPIOD clock enabled during Sleep mode (default after reset)
- **Bit 2 GPIOCLPEN** (rw): GPIOC clock enable during Sleep mode
  Set and reset by software.
  - 0: GPIOC clock disabled during Sleep mode
  - 1: GPIOC clock enabled during Sleep mode (default after reset)
- **Bit 1 GPIOBLPEN** (rw): GPIOB clock enable during Sleep mode
  Set and reset by software.
  - 0: GPIOB clock disabled during Sleep mode
  - 1: GPIOB clock enabled during Sleep mode (default after reset)
- **Bit 0 GPIOALPEN** (rw): GPIOA clock enable during Sleep mode
  Set and reset by software.
  - 0: GPIOA clock disabled during Sleep mode
  - 1: GPIOA clock enabled during Sleep mode (default after reset)

*Digest note:* 0x0007 0C9F sets AESLPEN, HASHLPEN, RNGLPEN, DAC1LPEN, ADC12LPEN, GPIOHLPEN and GPIOA–GPIOE LPEN; the STM32C59x/C5A3 value additionally sets ADC3LPEN, CCBLPEN, SAESLPEN, PKALPEN, GPIOGLPEN and GPIOFLPEN. CMSIS `RCC_AHB2LPENR_Rst` = 0x00070C9F for STM32C551/C552, i.e. bit 16 (AESLPEN) is 1 at reset even though that header defines no AES bits and the datasheet lists no AES; [unclear in source: whether AES is present on STM32C55xxx].

### 9.8.24 RCC AHB4 peripheral sleep clock register (RCC_AHB4LPENR)

Address offset: 0x0BC. Reset value: 0x0010 0000.

- **Bits 31:21** Reserved, must be kept at reset value.
- **Bit 20 XSPI1LPEN** (rw): XSPI1 clock enable during sleep mode
  Set and reset by software.
  - 0: XSPI1 clock disabled during sleep mode
  - 1: XSPI1 clock enabled during sleep mode (default after reset)
- **Bits 19:0** Reserved, must be kept at reset value.

*Digest note:* Absent on STM32C55xxx (no RCC_AHB4LPENR in the C552 header).

### 9.8.25 RCC APB1 sleep clock register (RCC_APB1LLPENR)

Address offset: 0x0C4. Reset value: 0x01BA 6871 (for STM32C53x/C542). Reset value: 0x01FE C879 (for STM32C55x/C562). Reset value: 0x43FE C87F (for STM32C59x/C5A3).

- **Bit 31** Reserved, must be kept at reset value.
- **Bit 30 UART7LPEN** (rw): UART7 clock enable during Sleep mode
  Set and reset by software.
  - 0: UART7 clock disabled during Sleep mode
  - 1: UART7 clock enabled during Sleep mode (default after reset)
- **Bits 29:26** Reserved, must be kept at reset value.
- **Bit 25 USART6LPEN** (rw): USART6 clock enable during Sleep mode
  Set and reset by software.
  - 0: USART6 clock disabled during Sleep mode
  - 1: USART6 clock enabled during Sleep mode (default after reset)
- **Bit 24 CRSLPEN** (rw): CRS clock enable during Sleep mode
  Set and reset by software.
  - 0: CRS clock disabled during Sleep mode
  - 1: CRS clock enabled during Sleep mode (default after reset)
- **Bit 23 I3C1LPEN** (rw): I3C1 clock enable during Sleep mode
  Set and reset by software.
  - 0: I3C1 clock disabled during Sleep mode
  - 1: I3C1 clock enabled during Sleep mode (default after reset)
- **Bit 22 I2C2LPEN** (rw): I2C2 clock enable during Sleep mode
  Set and reset by software.
  - 0: I2C2 clock disabled during Sleep mode
  - 1: I2C2 clock enabled during Sleep mode (default after reset)
- **Bit 21 I2C1LPEN** (rw): I2C1 clock enable during Sleep mode
  Set and reset by software.
  - 0: I2C1 clock disabled during Sleep mode
  - 1: I2C1 clock enabled during Sleep mode (default after reset)
- **Bit 20 UART5LPEN** (rw): UART5 clock enable during Sleep mode
  Set and reset by software.
  - 0: UART5 clock disabled during Sleep mode
  - 1: UART5 clock enabled during Sleep mode (default after reset)
- **Bit 19 UART4LPEN** (rw): UART4 clock enable during Sleep mode
  Set and reset by software.
  - 0: UART4 clock disabled during Sleep mode
  - 1: UART4 clock enabled during Sleep mode (default after reset)
- **Bit 18 USART3LPEN** (rw): USART3 clock enable during Sleep mode
  Set and reset by software.
  - 0: USART3 clock disabled during Sleep mode
  - 1: USART3 clock enabled during Sleep mode (default after reset)
- **Bit 17 USART2LPEN** (rw): USART2 clock enable during Sleep mode
  Set and reset by software.
  - 0: USART2 clock disabled during Sleep mode
  - 1: USART2 clock enabled during Sleep mode (default after reset)
- **Bit 16** Reserved, must be kept at reset value.
- **Bit 15 SPI3LPEN** (rw): SPI3 clock enable during Sleep mode
  Set and reset by software.
  - 0: SPI3 clock disabled during Sleep mode
  - 1: SPI3 clock enabled during Sleep mode (default after reset)
- **Bit 14 SPI2LPEN** (rw): SPI2 clock enable during Sleep mode
  Set and reset by software.
  - 0: SPI2 clock disabled during Sleep mode
  - 1: SPI2 clock enabled during Sleep mode (default after reset)
- **Bit 13 OPAMP1LPEN** (rw): OPAMP1 clock enable during Sleep mode
  Set and reset by software.
  - 0: OPAMP1 clock disabled during Sleep mode
  - 1: OPAMP1 clock enabled during Sleep mode (default after reset)
- **Bit 12** Reserved, must be kept at reset value.
- **Bit 11 WWDGLPEN** (rw): WWDG clock enable during Sleep mode
  Set and reset by software.
  - 0: WWDG clock disabled during Sleep mode
  - 1: WWDG clock enabled during Sleep mode (default after reset)
- **Bits 10:7** Reserved, must be kept at reset value.
- **Bit 6 TIM12LPEN** (rw): TIM12 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM12 clock disabled during Sleep mode
  - 1: TIM12 clock enabled during Sleep mode (default after reset)
- **Bit 5 TIM7LPEN** (rw): TIM7 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM7 clock disabled during Sleep mode
  - 1: TIM7 clock enabled during Sleep mode (default after reset)
- **Bit 4 TIM6LPEN** (rw): TIM6 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM6 clock disabled during Sleep mode
  - 1: TIM6 clock enabled during Sleep mode (default after reset)
- **Bit 3 TIM5LPEN** (rw): TIM5 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM5 clock disabled during Sleep mode
  - 1: TIM5 clock enabled during Sleep mode (default after reset)
- **Bit 2 TIM4LPEN** (rw): TIM4 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM4 clock disabled during Sleep mode
  - 1: TIM4 clock enabled during Sleep mode (default after reset)
- **Bit 1 TIM3LPEN** (rw): TIM3 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM3 clock disabled during Sleep mode
  - 1: TIM3 clock enabled during Sleep mode (default after reset)
- **Bit 0 TIM2LPEN** (rw): TIM2 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM2 clock disabled during Sleep mode
  - 1: TIM2 clock enabled during Sleep mode (default after reset)

*Digest note:* Decoding the STM32C55x/C562 reset value 0x01FE C879: CRSLPEN, I3C1LPEN, I2C2LPEN, I2C1LPEN, UART5LPEN, UART4LPEN, USART3LPEN, USART2LPEN, SPI3LPEN, SPI2LPEN, WWDGLPEN, TIM12LPEN, TIM7LPEN, TIM6LPEN, TIM5LPEN and TIM2LPEN are 1; UART7LPEN, USART6LPEN, OPAMP1LPEN, TIM4LPEN and TIM3LPEN are 0 (CMSIS `RCC_APB1LLPENR_Rst` = 0x01FEC879 agrees). The STM32C59x/C5A3 value 0x43FE C87F has bit 13 (OPAMP1LPEN) = 0 while the register map (Table 71) shows OPAMP1LPEN reset = 1 (which would give 0x43FE E87F); [unclear in source: OPAMP1LPEN reset value on STM32C59x/C5A3].

### 9.8.26 RCC APB1 sleep clock register (RCC_APB1HLPENR)

Address offset: 0x0C8. Reset value: 0x4000 0208.

- **Bits 31:10** Reserved, must be kept at reset value.
- **Bit 9 FDCANLPEN** (rw): FDCAN1 and FDCAN2 clock enable during Sleep mode
  Set and reset by software.
  - 0: FDCAN1 and FDCAN2 clock disabled during Sleep mode
  - 1: FDCAN1 and FDCAN2 clock enabled during Sleep mode (default after reset)
- **Bits 8:4** Reserved, must be kept at reset value.
- **Bit 3 COMPLPEN** (rw): COMP clock enable during Sleep mode
  Set and reset by software.
  - 0: COMP clock disabled during Sleep mode
  - 1: COMP clock enabled during Sleep mode (default after reset)
- **Bits 2:0** Reserved, must be kept at reset value.

*Digest note:* The reset value 0x4000 0208 has bit 30 set, which the bit description and the register map mark reserved (the map shows only FDCANLPEN and COMPLPEN = 1, i.e. 0x0000 0208). CMSIS `RCC_APB1HLPENR_Rst` = 0x40000208, matching the printed reset value. "Must be kept at reset value" therefore means preserving bit 30 = 1 on read-modify-write. CMSIS names bit 3 `COMP12LPEN`.

### 9.8.27 RCC APB2 sleep clock register (RCC_APB2LPENR)

Address offset: 0x0CC. Reset value: 0x0107 7800 (for STM32C55x/562/59x/5A3). Reset value: 0x0101 7800 (for STM32C53x/542).

- **Bits 31:25** Reserved, must be kept at reset value.
- **Bit 24 USBLPEN** (rw): USB clock enable during Sleep mode
  Set and reset by software.
  - 0: USB clock disabled during Sleep mode
  - 1: USB clock enabled during Sleep mode (default after reset)
- **Bits 23:19** Reserved, must be kept at reset value.
- **Bit 18 TIM17LPEN** (rw): TIM17 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM17 clock disabled during Sleep mode
  - 1: TIM17 clock enabled during Sleep mode (default after reset)
- **Bit 17 TIM16LPEN** (rw): TIM16 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM16 clock disabled during Sleep mode
  - 1: TIM16 clock enabled during Sleep mode (default after reset)
- **Bit 16 TIM15LPEN** (rw): TIM15 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM15 clock disabled during Sleep mode
  - 1: TIM15 clock enabled during Sleep mode (default after reset)
- **Bit 15** Reserved, must be kept at reset value.
- **Bit 14 USART1LPEN** (rw): USART1 clock enable during Sleep mode
  Set and reset by software.
  - 0: USART1 clock disabled during Sleep mode
  - 1: USART1 clock enabled during Sleep mode (default after reset)
- **Bit 13 TIM8LPEN** (rw): TIM8 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM8 clock disabled during Sleep mode
  - 1: TIM8 clock enabled during Sleep mode (default after reset)
- **Bit 12 SPI1LPEN** (rw): SPI1 clock enable during Sleep mode
  Set and reset by software.
  - 0: SPI1 clock disabled during Sleep mode
  - 1: SPI1 clock enabled during Sleep mode (default after reset)
- **Bit 11 TIM1LPEN** (rw): TIM1 clock enable during Sleep mode
  Set and reset by software.
  - 0: TIM1 clock disabled during Sleep mode
  - 1: TIM1 clock enabled during Sleep mode (default after reset)
- **Bits 10:0** Reserved, must be kept at reset value.

*Digest note:* The STM32C53x/542 value differs in bits 18:17 (TIM17LPEN, TIM16LPEN = 0). CMSIS `RCC_APB2LPENR_Rst` = 0x01077800 for STM32C551/C552.

### 9.8.28 RCC APB3 sleep clock register (RCC_APB3LPENR)

Address offset: 0x0D0. Reset value: 0x0020 0842.

- **Bits 31:22** Reserved, must be kept at reset value.
- **Bit 21 RTCAPBLPEN** (rw): RTC APB interface clock enable during Sleep mode
  Set and reset by software.
  - 0: RTC APB interface clock disabled during Sleep mode
  - 1: RTC APB interface clock enabled during Sleep mode (default after reset)
- **Bits 20:12** Reserved, must be kept at reset value.
- **Bit 11 LPTIM1LPEN** (rw): LPTIM1 clock enable during Sleep mode
  Set and reset by software.
  - 0: LPTIM1 clock disabled during Sleep mode
  - 1: LPTIM1 clock enabled during Sleep mode (default after reset)
- **Bits 10:7** Reserved, must be kept at reset value.
- **Bit 6 LPUART1LPEN** (rw): LPUART1 clock enable during Sleep mode
  Set and reset by software.
  - 0: LPUART1 clock disabled during Sleep mode
  - 1: LPUART1 clock enabled during Sleep mode (default after reset)
- **Bits 5:2** Reserved, must be kept at reset value.
- **Bit 1 SBSLPEN** (rw): SBS clock enable during Sleep mode
  Set and reset by software.
  - 0: SBS clock disabled during Sleep mode
  - 1: SBS clock enabled during Sleep mode (default after reset)
- **Bit 0** Reserved, must be kept at reset value.

### 9.8.29 RCC kernel clock configuration register (RCC_CCIPR1)

Address offset: 0x0D8. Reset value: 0x0000 0000.

- **Bits 31:28** Reserved, must be kept at reset value.
- **Bits 27:26 FDCANSEL[1:0]** (rw): FDCAN1 and FDCAN2 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psis_ck selected as kernel clock
  - 10: psik_ck selected as kernel clock
  - 11: hse_ck selected as kernel clock
- **Bits 25:22** Reserved, must be kept at reset value.
- **Bits 21:20 SPI3SEL[1:0]** (rw): SPI3 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - 11: AUDIOCLK selected as kernel clock
- **Bits 19:18 SPI2SEL[1:0]** (rw): SPI2 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - 11: AUDIOCLK selected as kernel clock
- **Bits 17:16 SPI1SEL[1:0]** (rw): SPI1 kernel clock source selection
  - 00: rcc_pclk2 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - 11: AUDIOCLK selected as kernel clock
- **Bits 15:14 LPUART1SEL[1:0]** (rw): LPUART1 kernel clock source selection
  - 00: rcc_pclk3 selected as kernel clock (default after reset)
  - 01: hsik_ck selected as kernel clock
  - 10: lse_ck selected as kernel clock
  - 11: lsi_ck selected as kernel clock
- **Bits 13:12 UART7SEL[1:0]** (rw): UART7 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - 11: lse_ck selected as kernel clock
- **Bits 11:10 USART6SEL[1:0]** (rw): UART6 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - 11: lse_ck selected as kernel clock
- **Bits 9:8 UART5SEL[1:0]** (rw): UART5 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - 11: lse_ck selected as kernel clock
- **Bits 7:6 UART4SEL[1:0]** (rw): UART4 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - 11: lse_ck selected as kernel clock
- **Bits 5:4 USART3SEL[1:0]** (rw): UART3 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - 11: lse_ck selected as kernel clock
- **Bits 3:2 USART2SEL[1:0]** (rw): USART2 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - 11: lse_ck selected as kernel clock
- **Bits 1:0 USART1SEL[1:0]** (rw): USART1 kernel clock source selection
  - 00: rcc_pclk2 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - 11: lse_ck selected as kernel clock

*Digest note:* The C552 header defines USART1SEL, USART2SEL, USART3SEL, UART4SEL, UART5SEL, LPUART1SEL, SPI1SEL, SPI2SEL, SPI3SEL and FDCANSEL (FDCANSEL absent in the C551 header); UART7SEL and USART6SEL are absent on STM32C55xxx. FDCANSEL = 01 (psis_ck) with PSI at 160 MHz would violate the caution in Section 9.4.5 (160 MHz must not reach peripheral kernel clocks).

### 9.8.30 RCC kernel clock configuration register (RCC_CCIPR2)

Address offset: 0x0DC. Reset value: 0x0000 0000.

- **Bits 31:30 SYSTICKSEL[1:0]** (rw): SYSTICK clock source selection
  - 00: rcc_hclk/8 selected as clock source (default after reset)
  - 01: lsi_ker_ck[1] selected as clock source
  - 10: lse_ck[1] selected as clock source
  - 11: reserved, the kernel clock is disabled
  Note: rcc_hclk frequency must be four times higher than lsi_ker_ck/lse_ck, that is, period (LSI/LSE) ≥ 4 * period (HCLK).
- **Bits 29:26** Reserved, must be kept at reset value.
- **Bits 25:24 CK48SEL[1:0]** (rw): CK48 clock source selection
  - 01: psi_div_3_ck selected as kernel clock
  - 10: hsi_div_3_ck selected as kernel clock
  - 11: hse_ck selected as kernel clock
  - Other: Reserved, kernel clock disabled (default after reset)
- **Bits 23:18** Reserved, must be kept at reset value.
- **Bits 17:16 LPTIM1SEL[1:0]** (rw): LPTIM1 kernel clock source selection
  - 00: rcc_pclk3 selected as kernel clock (default after reset)
  - 01: hsik_ck selected as kernel clock
  - 10: lse_ck selected as kernel clock
  - 11: lsi_ck selected as kernel clock
- **Bit 15 DACSEL** (rw): DAC sample and hold clock
  - 0: lse_ck selected as sample and hold clock (default after reset)
  - 1: lsi_ck selected as sample and hold clock
- **Bits 14:12 ADCDACPRE[2:0]** (rw): ADC and DAC prescaler for kernel clock source selection
  ADCDACPRE bitfield must not be changed when ADC or DAC are enabled.
  - 000: ADC and DAC kernel clock are not divided (default after reset)
  - 001: ADC and DAC kernel clock divided by 2
  - 010: ADC and DAC kernel clock divided by 4
  - 011: ADC and DAC kernel clock divided by 8
  - 100: ADC and DAC kernel clock divided by 16
  - 101: ADC and DAC kernel clock divided by 32
  - 110: ADC and DAC kernel clock divided by 64
  - 111: ADC and DAC kernel clock divided by 128
- **Bits 11:10 ADCDACSEL[1:0]** (rw): ADC and DAC kernel clock source selection
  This bitfield must not be changed when ADC or DAC are enabled.
  - 00: rcc_hclk selected as kernel clock
  - 01: psis_ck selected as kernel clock (default after reset)
  - 10: psik_ck selected as kernel clock
  - 11: hsik_ck selected as kernel clock
- **Bits 9:8** Reserved, must be kept at reset value.
- **Bits 7:6 I3C1SEL[1:0]** (rw): I3C1 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - Others: reserved, the kernel clock is disabled
- **Bits 5:4** Reserved, must be kept at reset value.
- **Bits 3:2 I2C2SEL[1:0]** (rw): I2C2 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - Other: Reserved, kernel clock disabled
- **Bits 1:0 I2C1SEL[1:0]** (rw): I2C1 kernel clock source selection
  - 00: rcc_pclk1 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - Other: Reserved, kernel clock disabled

*Digest note:* The register reset value 0x0000 0000 (and the register map, and CMSIS `RCC_CCIPR2_Rst` = 0x00000000) gives ADCDACSEL = 00 (rcc_hclk) after reset, contradicting the "01: psis_ck ... (default after reset)" line; firmware should write ADCDACSEL explicitly. CK48SEL is 00 (disabled) after reset, so USB and RNG have no kernel clock until CK48SEL is programmed: 01 = PSIDIV3 (48 MHz only with PSIFREQ = 144 MHz and PSIDIV3ON = 1), 10 = HSIDIV3 (48 MHz, CRS-trimmable from USB SOF), 11 = hse_ck (the HSE frequency itself, so 48 MHz only with a 48 MHz HSE). The "[1]" after lsi_ker_ck and lse_ck is printed in the source with no matching footnote.

### 9.8.31 RCC kernel clock configuration register (RCC_CCIPR3)

Address offset: 0x0E0. Reset value: 0x0000 0000.

- **Bits 31:28 ETH1PTPDIV[3:0]** (rw): Ethernet PTP clock division
  This field selects the division factor of the PTP clock.
  - 0000: divided by 1(default after reset)
  - 0001: divided by 2
  - 0010-1111: divided by {v+1}
- **Bits 27:26 ETH1CLKDIV[1:0]** (rw): Ethernet clock division
  This field selects the division factor of the ETH1 clock.
  - 00: divided by 1(default after reset)
  - 01: divided by 2
  - 10: divided by 4
  - 11: Reserved
- **Bits 25:15** Reserved, must be kept at reset value.
- **Bits 14:13 ETH1CLKSEL[1:0]** (rw): ETH1 clock source selection
  This field selects the reference clock of the PAD ETH1_CLK.
  Set and reset by software.
  - 00: kernel clock disabled (default after reset)
  - 01: psis_ck selected as kernel clock
  - 10: psik_ck selected as kernel clock
  - 11: hse_ck selected as kernel clock
- **Bit 12** Reserved, must be kept at reset value.
- **Bits 11:10 ETH1PTPCLKSEL[1:0]** (rw): ETH1 PTP clock source selection
  Set and reset by software.
  - 00: kernel clock disabled (default after reset)
  - 01: rcc_hclk1 selected as kernel clock
  - 10: psis_ck selected as kernel clock
  - 11: psik_ck selected as kernel clock
- **Bit 9** Reserved, must be kept at reset value.
- **Bit 8 ETH1REFCLKSEL** (rw): ETH1 RMII reference clock source selection
  This bit selects the reference clock of the Ethernet for RMII mode. It must be set to 0 in any other mode than RMII.
  - 0: ETH1_RMII_REF_CLK (default after reset)
  - 1: eth_clk_fb
- **Bits 7:2** Reserved, must be kept at reset value.
- **Bits 1:0 XSPI1SEL[1:0]** (rw): XSPI1 kernel clock source selection
  - 00: rcc_hclk4 selected as kernel clock (default after reset)
  - 01: psik_ck selected as kernel clock
  - 10: hsik_ck selected as kernel clock
  - Other: Reserved, kernel clock disabled

*Digest note:* The register map (Table 71) labels bits 27:26 "ETH1CLKDIV[3:0]"; the 2-bit width above is consistent with the field position. The whole register is absent on STM32C55xxx (the C552 header has no RCC_CCIPR3; offset 0x0E0 is reserved there).

### 9.8.32 RCC RTC domain control register (RCC_RTCCR)

Address offset: 0x0F0. Reset value: 0x0000 0000. Reset by RTC domain reset.

Access: 0 ≤ wait state ≤ 3, word, half-word, and byte access. Wait states are inserted in case of successive accesses to this register.

Note: After a system reset, this register is write-protected (except bits 27:26 and bit 16). To modify the RTC domain bits, the DRTCP bit in PWR_RTCCR must be set to 1. All bits (except bits 27:26 and bit 16) are reset only after an RTC domain reset (see Section 9.3.3). Other resets do not affect these bits.

- **Bits 31:28** Reserved, must be kept at reset value.
- **Bit 27 LSIRDY** (r): LSI oscillator ready
  Set and cleared by hardware to indicate when the LSI oscillator is stable. After the LSION bit is cleared, LSIRDY goes low after three internal low-speed oscillator clock cycles.
  This bit is set when the LSI is used by IWDG or RTC, even if LSION = 0.
  - 0: LSI oscillator not ready
  - 1: LSI oscillator ready
- **Bit 26 LSION** (rw): LSI oscillator enable
  Set and cleared by software.
  - 0: LSI oscillator off
  - 1: LSI oscillator on
- **Bit 25 LSCOSEL** (rw): Low-speed clock output selection
  Set and cleared by software.
  - 0: LSI clock selected
  - 1: LSE clock selected
- **Bit 24 LSCOEN** (rw): Low-speed clock output (LSCO) enable
  Set and cleared by software.
  - 0: LSCO output disabled
  - 1: LSCO output enabled
- **Bits 23:17** Reserved, must be kept at reset value.
- **Bit 16 RTCDRST** (rw): RTC domain software reset
  Set and reset by software.
  - 0: reset not activated (default after RTC domain reset)
  - 1: resets the entire VSW domain
- **Bit 15 RTCEN** (rw): RTC clock enable
  Set and reset by software.
  - 0: rtc_ck disabled (default after RTC domain reset)
  - 1: rtc_ck enabled
- **Bits 14:10** Reserved, must be kept at reset value.
- **Bits 9:8 RTCSEL[1:0]** (rw): RTC clock source selection
  Set by software to select the clock source for the RTC. These bits can be written only one time (except in case of failure detection on LSE). These bits must be written before LSECSSON is enabled. The RTCDRST bit can be used to reset them, then it can be written one time again. If HSE is selected as RTC clock, this clock is lost when the system is in Stop mode or in case of a pin reset (NRST).
  - 00: No clock (default after RTC domain reset)
  - 01: LSE selected as RTC clock
  - 10: LSI selected as RTC clock
  - 11: HSE divided by RTCPRE value selected as RTC clock
- **Bit 7 LSEEXT** (rw): Low-speed external clock type in bypass mode
  Set and reset by software to select the external clock type (analog or digital). The external clock must be enabled with the LSEON bit, to be used by the device. The LSEEXT bit can be written only if the LSE oscillator is disabled.
  - 0: LSE in analog mode (default after RTC domain reset)
  - 1: LSE in digital mode
- **Bit 6 LSECSSD** (r): LSE clock security system failure detection
  Set by hardware to indicate when a failure has been detected by the clock security system on the external 32 kHz oscillator. Clearing LSECSSON (only possible after failure detection) also clears this bit.
  - 0: No failure detected on 32 kHz oscillator (default after RTC domain reset)
  - 1: Failure detected on 32 kHz oscillator
- **Bit 5 LSECSSON** (rw): LSE clock security system enable
  Set by software to enable the clock security system on 32 kHz oscillator. This bit must be enabled after LSE is enabled (LSEON enabled) and ready (LSERDY set by hardware), and after RTCSEL is selected.
  Once enabled, this bit cannot be disabled, except after a LSE failure detection (LSECSSD = 1). In that case, software must disable LSECSSON.
  - 0: CSS on 32 kHz oscillator off (default after RTC domain reset)
  - 1: CSS on 32 kHz oscillator on
- **Bits 4:3 LSEDRV[1:0]** (rw): LSE oscillator driving capability
  Set by software to select the driving capability of the LSE oscillator.
  These bits can be written only if LSE oscillator is disabled (LSEON = 0 and LSERDY = 0).
  - 00: Lowest drive (default after RTC domain reset)
  - 01: Medium-low drive
  - 10: Medium-high drive
  - 11: Highest drive
- **Bit 2 LSEBYP** (rw): LSE oscillator bypass
  Set and reset by software to bypass oscillator in debug mode. This bit must not be written when the LSE is enabled (by LSEON) or ready (LSERDY = 1)
  - 0: LSE oscillator not bypassed (default after RTC domain reset)
  - 1: LSE oscillator bypassed
- **Bit 1 LSERDY** (r): LSE oscillator ready
  Set and reset by hardware to indicate when the LSE is stable. This bit needs 6 cycles of lse_ck clock to fall down after LSEON has been set to 0.
  - 0: LSE oscillator not ready (default after RTC domain reset)
  - 1: LSE oscillator ready
- **Bit 0 LSEON** (rw): LSE oscillator enabled
  Set and reset by software. This bit cannot be cleared if the LSE is selected as reference clock for PSI with PSI enabled (PSISON bit or PSIDIV3ON bit or PSIKON bit set to 1).
  - 0: LSE oscillator off (default after RTC domain reset)
  - 1: LSE oscillator on

*Digest note:* Section 9.3.3 says write access to the RTC domain must be enabled before setting RTCDRST, while the note above lists bit 16 among the bits not write-protected after system reset; both are as printed. LSION/LSIRDY (bits 27:26) are outside the RTC-domain protection and reset.

### 9.8.33 RCC reset status register (RCC_RSR)

Address offset: 0x0F4. Reset value: 0xXX00 0000. Reset by power-on reset only.

Access: 0 ≤ wait state ≤ 3, word, half-word, and byte access. Wait states are inserted in case of successive accesses to this register.

- **Bit 31 LPWRRSTF** (r): Low-power reset flag
  Set by hardware when a reset occurs due to Stop or Standby mode entry, whereas the corresponding NRST_STOP, NRST_STBY option bit is cleared.
  Cleared by writing to the RMVF bit.
  - 0: No illegal low-power mode reset occurred
  - 1: An illegal low-power mode reset occurred
- **Bit 30 WWDGRSTF** (r): Window watchdog reset flag
  Reset by software by writing the RMVF bit.
  Set by hardware when a window watchdog reset occurs.
  - 0: No WWDG reset occurred (default after power-on reset)
  - 1: A WWDG reset occurred
- **Bit 29 IWDGRSTF** (r): Independent watchdog reset flag
  Reset by software by writing the RMVF bit. Set by hardware when an IWDG reset occurs.
  - 0: No IWDG reset occurred (default after power-on reset)
  - 1: An IWDG reset occurred
- **Bit 28 SFTRSTF** (r): System reset from CPU reset flag
  Reset by software by writing the RMVF bit. Set by hardware when the system reset is due to CPU.The CPU can generate a system reset by writing SYSRESETREQ bit of AIRCR register of the Cortex-M33.
  - 0: No CPU software reset occurred (default after power-on reset)
  - 1: A system reset has been generated by the CPU.
- **Bit 27 BORRSTF** (r): POR reset flag
  Reset by software by writing the RMVF bit. Set by hardware when a POR reset occurs (pwr_por_rst).
  - 0: No POR reset occurred
  - 1: A POR reset occurred (default after power-on reset)
- **Bit 26 PINRSTF** (r): Pin reset flag (NRST)
  Reset by software by writing the RMVF bit. Set by hardware when a reset from pin occurs.
  - 0: No reset from pin occurred
  - 1: A reset from pin occurred (default after power-on reset)
- **Bits 25:24** Reserved, must be kept at reset value.
- **Bit 23 RMVF** (w): Remove reset flag
  Set and reset by software to reset the value of the reset flags.
  - 0: Reset of the reset flags not activated (default after power-on reset)
  - 1: Reset the value of the reset flags
- **Bits 22:0** Reserved, must be kept at reset value.

*Digest note:* "XX" in the reset value covers the six flags in bits 31:26 (shown as X in the register map). After a power-on reset BORRSTF = PINRSTF = 1 (Table 65). Bit 26 is PINRSTF (Table 71 and the CMSIS header agree on the 31..26 order LPWRRSTF, WWDGRSTF, IWDGRSTF, SFTRSTF, BORRSTF, PINRSTF). CMSIS gives `RCC_RSR_Rst` = 0x00000000.

### 9.8.34 RCC privilege configuration register (RCC_PRIVCFGR)

Address offset: 0x114. Reset value: 0x0000 0000.

Access: no wait state; word, half-word, and byte access. This register can be written only by a privileged access. It can be read by privileged or unprivileged access.

- **Bits 31:2** Reserved, must be kept at reset value.
- **Bit 1 PRIV** (rw): RCC function privileged configuration
  Set and reset by software. This bit can be written only by privileged access.
  - 0: Read and write to RCC functions can be done by privileged or unprivileged access.
  - 1: Read and write to RCC functions can be done by privileged access only
- **Bit 0** Reserved, must be kept at reset value.

### 9.8.35 RCC register map

**Table 71. RCC register map and reset values**

| Offset | Register | Reset value | Fields (bit positions) |
|---|---|---|---|
| 0x000 | RCC_CR1 | 0x0000 0022 | HSEEXT (20), HSECSSON (19), HSEBYP (18), HSERDY (17), HSEON (16), PSIKRDY (14), PSIDIV3RDY (13), PSISRDY (12), PSIKERON (11), PSIKON (10), PSIDIV3ON (9), PSISON (8), HSIKRDY (6), HSIDIV3RDY (5), HSISRDY (4), HSIKERON (3), HSIKON (2), HSIDIV3ON (1), HSISON (0) |
| 0x004 | RCC_CR2 | 0x0000 0000 | PSIFREQ[1:0] (29:28), PSIREF[2:0] (22:20), PSIREFSRC[1:0] (17:16), PSIKDIV[3:0] (11:8), HSIKDIV[3:0] (3:0) |
| 0x008–0x018 | Reserved | - | - |
| 0x01C | RCC_CFGR1 | 0x0000 0000 | MCO2SEL[2:0] (31:29), MCO2PRE[3:0] (28:25), MCO1SEL[2:0] (24:22), MCO1PRE[3:0] (21:18), RTCPRE[8:0] (15:7), STOPWUCK (6), SWS[1:0] (4:3), SW[1:0] (1:0) |
| 0x020 | RCC_CFGR2 | 0x0000 0000 | APB3DIS (22), APB2DIS (21), APB1DIS (20), AHB4DIS (19), AHB2DIS (17), AHB1DIS (16), PPRE3[2:0] (14:12), PPRE2[2:0] (10:8), PPRE1[2:0] (6:4), HPRE[3:0] (3:0) |
| 0x024–0x04C | Reserved | - | - |
| 0x050 | RCC_CIER | 0x0000 0000 | HSERDYIE (8), PSIKRDYIE (7), PSIDIV3RDYIE (6), PSISRDYIE (5), HSIKRDYIE (4), HSIDIV3RDYIE (3), HSISRDYIE (2), LSERDYIE (1), LSIRDYIE (0) |
| 0x054 | RCC_CIFR | 0x0000 0000 | LSECSSF (11), HSECSSF (10), HSERDYF (8), PSIKRDYF (7), PSIDIV3RDYF (6), PSISRDYF (5), HSIKRDYF (4), HSIDIV3RDYF (3), HSISRDYF (2), LSERDYF (1), LSIRDYF (0) |
| 0x058 | RCC_CICR | 0x0000 0000 | LSECSSC (11), HSECSSC (10), HSERDYC (8), PSIKRDYC (7), PSIDIV3RDYC (6), PSISRDYC (5), HSIKRDYC (4), HSIDIV3RDYC (3), HSISRDYC (2), LSERDYC (1), LSIRDYC (0) |
| 0x05C | Reserved | - | - |
| 0x060 | RCC_AHB1RSTR | 0x0000 0000 | ETH1RST (19), RAMCFGRST (17), CORDICRST (14), CRCRST (12), LPDMA2RST (1), LPDMA1RST (0) |
| 0x064 | RCC_AHB2RSTR | 0x0000 0000 | ADC3RST (24), CCBRST (21), SAESRST (20), PKARST (19), RNGRST (18), HASHRST (17), AESRST (16), DAC1RST (11), ADC12RST (10), GPIOHRST (7), GPIOGRST (6), GPIOFRST (5), GPIOERST (4), GPIODRST (3), GPIOCRST (2), GPIOBRST (1), GPIOARST (0) |
| 0x068 | Reserved | - | - |
| 0x06C | RCC_AHB4RSTR | 0x0000 0000 | XSPI1RST (20) |
| 0x074 | RCC_APB1LRSTR | 0x0000 0000 | UART7RST (30), USART6RST (25), CRSRST (24), I3C1RST (23), I2C2RST (22), I2C1RST (21), UART5RST (20), UART4RST (19), USART3RST (18), USART2RST (17), SPI3RST (15), SPI2RST (14), OPAMP1RST (13), TIM12RST (6), TIM7RST (5), TIM6RST (4), TIM5RST (3), TIM4RST (2), TIM3RST (1), TIM2RST (0) |
| 0x078 | RCC_APB1HRSTR | 0x0000 0000 | FDCANRST (9), COMPRST (3) |
| 0x07C | RCC_APB2RSTR | 0x0000 0000 | USBRST (24), TIM17RST (18), TIM16RST (17), TIM15RST (16), USART1RST (14), TIM8RST (13), SPI1RST (12), TIM1RST (11) |
| 0x080 | RCC_APB3RSTR | 0x0000 0000 | LPTIM1RST (11), LPUART1RST (6), SBSRST (1) |
| 0x084 | Reserved | - | - |
| 0x088 | RCC_AHB1ENR | 0xC000 0100 | SRAM1EN (31), SRAM2EN (30), ETH1RXEN (21), ETH1TXEN (20), ETH1EN (19), ETH1CKEN (18), RAMCFGEN (17), CORDICEN (14), CRCEN (12), FLASHEN (8), LPDMA2EN (1), LPDMA1EN (0) |
| 0x08C | RCC_AHB2ENR | 0x0000 0000 | ADC3EN (24), CCBEN (21), SAESEN (20), PKAEN (19), RNGEN (18), HASHEN (17), AESEN (16), DAC1EN (11), ADC12EN (10), GPIOHEN (7), GPIOGEN (6), GPIOFEN (5), GPIOEEN (4), GPIODEN (3), GPIOCEN (2), GPIOBEN (1), GPIOAEN (0) |
| 0x090 | Reserved | - | - |
| 0x094 | RCC_AHB4ENR | 0x0000 0000 | XSPI1EN (20) |
| 0x09C | RCC_APB1LENR | 0x0000 0000 | UART7EN (30), USART6EN (25), CRSEN (24), I3C1EN (23), I2C2EN (22), I2C1EN (21), UART5EN (20), UART4EN (19), USART3EN (18), USART2EN (17), SPI3EN (15), SPI2EN (14), OPAMP1EN (13), WWDGEN (11), TIM12EN (6), TIM7EN (5), TIM6EN (4), TIM5EN (3), TIM4EN (2), TIM3EN (1), TIM2EN (0) |
| 0x0A0 | RCC_APB1HENR | 0x0000 0000 | FDCANEN (9), COMPEN (3) |
| 0x0A4 | RCC_APB2ENR | 0x0000 0000 | USBEN (24), TIM17EN (18), TIM16EN (17), TIM15EN (16), USART1EN (14), TIM8EN (13), SPI1EN (12), TIM1EN (11) |
| 0x0A8 | RCC_APB3ENR | 0x0000 0000 | RTCAPBEN (21), LPTIM1EN (11), LPUART1EN (6), SBSEN (1) |
| 0x0AC | Reserved | - | - |
| 0x0B0 | RCC_AHB1LPENR | 0xC43E 5103 (map) | SRAM1LPEN (31), SRAM2LPEN (30), ICACHELPEN (26), ETH1RXLPEN (21), ETH1TXLPEN (20), ETH1LPEN (19), ETH1CKLPEN (18), RAMCFGLPEN (17), CORDICLPEN (14), CRCLPEN (12), FLASHLPEN (8), LPDMA2LPEN (1), LPDMA1LPEN (0) |
| 0x0B4 | RCC_AHB2LPENR | 0x013F 0CFF (map) | ADC3LPEN (24), CCBLPEN (21), SAESLPEN (20), PKALPEN (19), RNGLPEN (18), HASHLPEN (17), AESLPEN (16), DAC1LPEN (11), ADC12LPEN (10), GPIOHLPEN (7), GPIOGLPEN (6), GPIOFLPEN (5), GPIOELPEN (4), GPIODLPEN (3), GPIOCLPEN (2), GPIOBLPEN (1), GPIOALPEN (0) |
| 0x0B8 | Reserved | - | - |
| 0x0BC | RCC_AHB4LPENR | 0x0010 0000 | XSPI1LPEN (20) |
| 0x0C4 | RCC_APB1LLPENR | 0x43FE E87F (map) | UART7LPEN (30), USART6LPEN (25), CRSLPEN (24), I3C1LPEN (23), I2C2LPEN (22), I2C1LPEN (21), UART5LPEN (20), UART4LPEN (19), USART3LPEN (18), USART2LPEN (17), SPI3LPEN (15), SPI2LPEN (14), OPAMP1LPEN (13), WWDGLPEN (11), TIM12LPEN (6), TIM7LPEN (5), TIM6LPEN (4), TIM5LPEN (3), TIM4LPEN (2), TIM3LPEN (1), TIM2LPEN (0) |
| 0x0C8 | RCC_APB1HLPENR | 0x0000 0208 (map) | FDCANLPEN (9), COMPLPEN (3) |
| 0x0CC | RCC_APB2LPENR | 0x0107 7800 | USBLPEN (24), TIM17LPEN (18), TIM16LPEN (17), TIM15LPEN (16), USART1LPEN (14), TIM8LPEN (13), SPI1LPEN (12), TIM1LPEN (11) |
| 0x0D0 | RCC_APB3LPENR | 0x0020 0842 | RTCAPBLPEN (21), LPTIM1LPEN (11), LPUART1LPEN (6), SBSLPEN (1) |
| 0x0D4 | Reserved | - | - |
| 0x0D8 | RCC_CCIPR1 | 0x0000 0000 | FDCANSEL[1:0] (27:26), SPI3SEL[1:0] (21:20), SPI2SEL[1:0] (19:18), SPI1SEL[1:0] (17:16), LPUART1SEL[1:0] (15:14), UART7SEL[1:0] (13:12), USART6SEL[1:0] (11:10), UART5SEL[1:0] (9:8), UART4SEL[1:0] (7:6), USART3SEL[1:0] (5:4), USART2SEL[1:0] (3:2), USART1SEL[1:0] (1:0) |
| 0x0DC | RCC_CCIPR2 | 0x0000 0000 | SYSTICKSEL[1:0] (31:30), CK48SEL[1:0] (25:24), LPTIM1SEL[1:0] (17:16), DACSEL (15), ADCDACPRE[2:0] (14:12), ADCDACSEL[1:0] (11:10), I3C1SEL[1:0] (7:6), I2C2SEL[1:0] (3:2), I2C1SEL[1:0] (1:0) |
| 0x0E0 | RCC_CCIPR3 | 0x0000 0000 | ETH1PTPDIV[3:0] (31:28), ETH1CLKDIV[3:0] (27:26) (as labelled in the map), ETH1CLKSEL[1:0] (14:13), ETH1PTPCLKSEL[1:0] (11:10), ETH1REFCLKSEL (8), XSPI1SEL[1:0] (1:0) |
| 0x0E4–0x0EC | Reserved | - | - |
| 0x0F0 | RCC_RTCCR | 0x0000 0000 | LSIRDY (27), LSION (26), LSCOSEL (25), LSCOEN (24), RTCDRST (16), RTCEN (15), RTCSEL[1:0] (9:8), LSEEXT (7), LSECSSD (6), LSECSSON (5), LSEDRV[1:0] (4:3), LSEBYP (2), LSERDY (1), LSEON (0) |
| 0x0F4 | RCC_RSR | 0xXX00 0000 (bits 31:26 = X) | LPWRRSTF (31), WWDGRSTF (30), IWDGRSTF (29), SFTRSTF (28), BORRSTF (27), PINRSTF (26), RMVF (23) |
| 0x0F8–0x110 | Reserved | - | - |
| 0x114 | RCC_PRIVCFGR | 0x0000 0000 | PRIV (1) |

Refer to Section 2.2: Memory organization for the register boundary addresses.

*Digest note:* The "Reset value" column above is taken from the per-bit reset row of Table 71 where marked "(map)"; it differs from the register sections as follows: RCC_CR1 map row shows HSIDIV3RDY = 0 (register section: 0x0000 0022); RCC_AHB1LPENR, RCC_AHB2LPENR and RCC_APB1LLPENR map rows show the all-features (STM32C59x/5A3-style) values, with RCC_APB1LLPENR giving 0x43FE E87F instead of the printed 0x43FE C87F; RCC_APB1HLPENR map row gives 0x0000 0208 instead of the printed 0x4000 0208. For STM32C551/C552 the CMSIS reset values are: AHB1LPENR 0xC4025103, AHB2LPENR 0x00070C9F, APB1LLPENR 0x01FEC879, APB1HLPENR 0x40000208, APB2LPENR 0x01077800, APB3LPENR 0x00200842, AHB1ENR 0xC0000100, CR1 0x00000022, all others 0. The table has no row at all for offsets 0x070, 0x098 and 0x0C0 (gaps after RCC_AHB4RSTR, RCC_AHB4ENR and RCC_AHB4LPENR); treat them as reserved. The CMSIS header treats 0x068–0x070 as reserved on STM32C552, and likewise 0x090–0x098 and 0x0B8–0x0C0 (no AHB4 registers) and 0x0E0–0x0EC (no RCC_CCIPR3).
