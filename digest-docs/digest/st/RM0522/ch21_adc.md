# RM0522 Chapter 21: Analog-to-digital converters (ADC)

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 561–671.

*Digest note:* STM32C551/C552 (C55xxx) implement ADC1 and ADC2 only (ADC3 is only on STM32C59x/5A3, see Table 136). ADC1 is the master and ADC2 the slave of the ADC12 pair. Datasheet digest: /Users/erik/Code/kalico/digest-docs/digest/st/STM32C55xxx_Datasheet.md.

## 21.1 ADC introduction

This section describes the implementation of up to 3 ADCs:

- ADC1 and ADC2 are tightly coupled and can operate in dual mode (ADC1 is master).
- ADC3 is controlled independently.

Each ADC consists of one 12-bit successive approximation analog-to-digital converter.

Each ADC has up to 14 multiplexed channels. A/D conversion of the various channels can be performed in single, continuous, scan, or discontinuous mode. The result of the ADC is stored in a left-aligned or right-aligned (default configuration) 32-bit data register.

The ADCs are mapped on the AHB bus to allow fast data handling.

The analog watchdog features allow the application to detect if the input voltage goes outside the user-defined high or low thresholds.

A built-in hardware oversampler allows improving analog performances while off-loading the related computational burden from the CPU.

An efficient low-power mode is implemented to allow very low consumption at low frequency.

*Digest note:* ADC3 is absent on STM32C55xxx.

## 21.2 ADC main features

- High-performance features
  - Up to 3 ADCs, out of which two of them can operate in dual mode:
    - ADC1 is connected to 12 external channels + 2 internal channels
    - ADC2 is connected to 14 external channels
    - ADC3 is connected to 14 external channels
  - 12, 10, 8 or 6-bit configurable resolution
  - ADC conversion time independent from the AHB bus clock frequency
  - Faster conversion time by lowering resolution
  - AHB slave bus interface to allow fast data handling
  - Channel-wise programmable sampling time
  - Flexible sampling time control
  - Fixed latency for a trigger to start of sampling
  - Up to 4 injected channels (analog inputs assignment to regular or injected channels is fully configurable)
  - Data alignment with in-built data coherency
  - Data can be managed by DMA for regular channel conversions
  - Four dedicated data registers for the injected channels
- Low-power features
  - Speed adaptive low-power mode to reduce ADC consumption when operating at low frequency
  - Allows slow bus frequency application while keeping optimum ADC performance
  - Provides automatic control to avoid ADC overrun in low AHB bus clock frequency application (autodelayed mode)
- Oversampler
  - 32-bit data register
  - Oversampling ratio adjustable from 2 to 1024
  - Programmable data right and left shifts
- Data preconditioning
  - Gain compensation
  - Offset compensation
- Analog input channels
  - External analog inputs (per ADC): up to 14 GPIO pads
  - 1 channel for the internal reference voltage (VREFINT)
  - 1 channel for the internal temperature sensor (VSENSE)
- Start-of-conversion can be initiated:
  - By software for both regular and injected conversions
  - By hardware triggers with configurable polarity (internal timer events or GPIO input events) for both regular and injected conversions
- Conversion modes
  - Each ADC can convert a single channel or can scan a sequence of channels
  - Single mode converts selected inputs once per trigger
  - Continuous mode converts selected inputs continuously
  - Discontinuous mode
- Interrupt generation at ADC ready, the end of sampling, the end of conversion (regular or injected), end of sequence conversion (regular or injected), analog watchdog 1, 2 or 3 or overrun events
- 3 analog watchdogs per ADC
- ADC input range: VSSA ≤ VIN ≤ VREF+

Figure 85 shows the block diagram of one ADC.

*Digest note:* No VBAT channel is listed anywhere in this chapter. The only internal channels are VSENSE and VREFINT, and both are on ADC1 only (see Table 139).

## 21.3 ADC implementation

**Table 136. ADC features**

| ADC modes/features | ADC1, ADC2(1) | ADC3(2) |
|---|---|---|
| Resolution | 12 bits | 12 bits |
| Maximum sampling speed | 2 Msps (12-bit resolution) | 2 Msps (12-bit resolution) |
| Dual mode operation | X | - |
| Offset calibration | X | X |
| Single-end input | X | X |
| Differential input | - | - |
| Injected channel conversion | X | X |
| Oversampling | up to x1024 | up to x1024 |
| Data register | 32 bits | 32 bits |
| DMA support | X | X |
| Parallel data output to MDF and ADF | - | - |
| Offset compensation | X | X |
| Gain compensation | X | X |
| Number of analog watchdog | 3 | 3 |

Notes:

1. Only available on STM32C55x/562/59x/5A3 devices.
2. Only available on STM32C59x/5A3 devices.

*Digest note:* In the source, every row except "Dual mode operation" is one cell spanning both device columns. It is repeated in both columns here. Footnote (1) is attached to the combined "ADC1, ADC2" heading. The STM32C55xxx datasheet lists both ADC1 and ADC2, with a maximum sampling speed of 2.25 Msps (at fADC = 36 MHz), not the 2 Msps printed here.

## 21.4 ADC functional description

### 21.4.1 ADC block diagram

Figure 85 shows the ADC block diagram and Table 137 gives the ADC pin description.

**Figure 85. ADC block diagram** (described in prose)

The figure shows one ADC.

- **Supplies and references.** The analog supply VREF+ (VDDA) and VREF- feed the SAR ADC.
- **Clocks.** Two clock inputs reach the AHB interface side: adc_ker_ck and adc_hclk.
- **Input path.** The analog inputs ADC_INi (analog input channels) enter an "Input selection & scan control" block, which outputs VINi.
  - This block is controlled by SWTRIG, BULB, SMPTRIG, JAUTO, JLEN[1:0], JSQx[4:0], LEN[3:0], SQx[4:0] and CONT.
  - It feeds VIN to the SAR ADC. The sampling time is set by SMPx[2:0].
- **Power and calibration control** of the SAR ADC:
  - DEEPPWD.
  - ADVREGEN, which drives an internal regulator (REG).
  - ADEN/ADDIS.
  - CALFACT[6:0], ADCALDIF and ADCAL.
  - A "Bias & Ref" block.
- **Start & Stop control.** A "Start & Stop Control" block (AUTDLY, ADSTP, ADSTART, JADSTART, JADSTP) issues the start signal to the SAR ADC. Its inputs are:
  - **Software triggers:** a SW trigger and a J SW trigger.
  - **Regular hardware triggers:** adc_ext0_trg ... adc_ext31_trg ("EXTi mapped at product level"). EXTSEL[4:0] selects the trigger, and EXTEN[1:0] gives "trigger enable and edge selection". This path also carries the discontinuous mode controls DISCEN and DISCNUM[2:0].
  - **Injected hardware triggers:** adc_jext0_trg ... adc_jext31_trg ("JEXTi mapped at product level"), selected by JEXTSEL[4:0], with JEXTEN[1:0] for trigger enable and edge selection, and JDISCEN.
- **Conversion data path.** The SAR ADC "CONVERTED DATA" output goes through:
  - resolution selection RES[1:0] (12, 10, 8, 6 bits);
  - overrun mode OVRMOD;
  - an "Oversampler /Offset/Gain" block. Its options are ROVSM, TROVS, OVSS[3:0], OVSR[9:0], JOVSE, ROVSE, OFFSET[21:0], POSOFF, USAT, SSAT, OFFSETy_CH[4:0], GCOMP and GCOMPCOEFF[13:0].
- **Data registers and AHB interface.** Results land in RDATA[31:0] and JDATA1[31:0] to JDATA4[31:0]. These are read through the AHB interface (DMNGT, DAMDF), which connects to the AHB slave port and the adc_dma request.
- **Interrupt flags.** ADRDY, EOSMP, EOC, EOS, OVR, JEOS, JEOC and AWDx are combined into adc_it.
- **Analog watchdogs.** A block "Analog watchdog 1,2,3" (AWD1, AWD2, AWD3) drives adc_awd1, adc_awd2 and adc_awd3. Its controls are AWD1EN, JAWD1EN, AWD1SGL, AWD1CH[4:0], AWD1_LTR.LTR[22:0], AWD1_HTR.HTR[22:0], AWDFILT[2:0], AWD2CH[13:0], AWD2_LTR.LTR[22:0], AWD2_HTR.HTR[22:0], AWD3CH[13:0], AWD3_LTR.LTR[22:0] and AWD3_HTR.HTR[22:0].

### 21.4.2 ADC pins and internal signals

**Table 137. ADC input/output pins**

| Pin name | Signal type | Description |
|---|---|---|
| VDDA | Input, analog supply | Analog power supply |
| VSSA | Input, analog supply ground | Ground for analog power supply, equal to VSS. |
| VREF+ | Input, analog reference positive | The higher/positive reference voltage for the ADC. |
| VREF- | Input, analog reference negative | The lower/negative reference voltage for the ADC. |
| ADCx_INi | External analog input signals | 14 external analog input channels (refer to Section 21.4.4: ADC connectivity for details) |

**Table 138. ADC internal input/output signals**

| Internal signal name | Signal type | Description |
|---|---|---|
| VINi | Analog input channels | Internal analog input channels connected either to ADCx_INi external channels or to internal channels |
| adc_ext_trgi | Inputs | ADC external trigger inputs for regular conversions. These inputs are shared between the ADC master and the ADC slave. |
| adc_jext_trgi | Inputs | ADC external trigger inputs for the injected conversions. These inputs are shared between the ADC master and the ADC slave. |
| adc_awdy | Output | Internal analog watchdog output signal connected to on-chip timers. (y = Analog watchdog number 1,2,3) |
| adc_ker_ck | Input | ADC kernel clock |
| adc_hclk | Input | ADC peripheral clock |
| adc_it | Output | ADC interrupt |
| adc_dma | Output | ADC DMA request |

**Table 139. ADC1/2/3 interconnection**

| Signal name | Source/destination |
|---|---|
| ADC1 VIN[13] | VREFINT (output voltage from internal reference voltage or dac_int1) |
| ADC1 VIN[12] | VSENSE (internal temperature sensor output voltage) |
| adc_ext_trg0 | exti11 |
| adc_ext_trg1 | tim1_oc1 |
| adc_ext_trg2 | tim1_oc2 |
| adc_ext_trg3 | tim1_oc3 |
| adc_ext_trg4 | tim1_trgo |
| adc_ext_trg5 | tim1_trgo2 |
| adc_ext_trg6 | tim2_oc2 |
| adc_ext_trg7 | tim2_trgo |
| adc_ext_trg8 | Reserved |
| adc_ext_trg9 | Reserved |
| adc_ext_trg10 | tim5_oc4(1) |
| adc_ext_trg11 | tim5_trgo(1) |
| adc_ext_trg12 | tim6_trgo |
| adc_ext_trg13 | tim8_trgo |
| adc_ext_trg14 | tim8_trgo2 |
| adc_ext_trg15 | tim15_trgo |
| adc_ext_trg16 | lptim1_ch1 |
| adc_ext_trg17 | Reserved |
| adc_ext_trg18 | Reserved |
| adc_ext_trg19 | Reserved |
| adc_ext_trg20 | Reserved |
| adc_ext_trg21 | Reserved |
| adc_ext_trg22 | Reserved |
| adc_ext_trg23 | Reserved |
| adc_ext_trg24 | Reserved |
| adc_ext_trg25 | Reserved |
| adc_ext_trg26 | Reserved |
| adc_ext_trg27 | Reserved |
| adc_ext_trg28 | Reserved |
| adc_ext_trg29 | Reserved |
| adc_ext_trg30 | Reserved |
| adc_ext_trg31 | Reserved |
| adc_jext_trg0 | exti15 |
| adc_jext_trg1 | tim1_oc4 |
| adc_jext_trg2 | tim1_trgo |
| adc_jext_trg3 | tim1_trgo2 |
| adc_jext_trg4 | tim2_oc1 |
| adc_jext_trg5 | tim2_trgo |
| adc_jext_trg6 | Reserved |
| adc_jext_trg7 | Reserved |
| adc_jext_trg8 | Reserved |
| adc_jext_trg9 | Reserved |
| adc_jext_trg10 | tim5_oc1(1) |
| adc_jext_trg11 | tim5_oc2(1) |
| adc_jext_trg12 | tim5_oc3(1) |
| adc_jext_trg13 | tim5_trgo(1) |
| adc_jext_trg14 | tim7_trgo |
| adc_jext_trg15 | tim8_oc4 |
| adc_jext_trg16 | tim8_trgo |
| adc_jext_trg17 | tim8_trgo2 |
| adc_jext_trg18 | tim12_trgo |
| adc_jext_trg19 | tim15_trgo |
| adc_jext_trg20 | lptim1_ch1 |
| adc_jext_trg21 | Reserved |
| adc_jext_trg22 | Reserved |
| adc_jext_trg23 | Reserved |
| adc_jext_trg24 | Reserved |
| adc_jext_trg25 | Reserved |
| adc_jext_trg26 | Reserved |
| adc_jext_trg27 | Reserved |
| adc_jext_trg28 | Reserved |
| adc_jext_trg29 | Reserved |
| adc_jext_trg30 | Reserved |
| adc_jext_trg31 | Reserved |

Notes:

1. Reserved on STM32C53x/542 devices.

*Digest note:* The internal channels map to these ADC channel numbers: VSENSE (temperature sensor) is ADC1 channel 12 and VREFINT is ADC1 channel 13. ADC2 has no internal channels; its VIN[12] and VIN[13] are the external inputs ADC2_IN12 and ADC2_IN13.

### 21.4.3 ADC clocks

#### Dual clock domain architecture

The dual clock-domain architecture means that the ADC kernel clock is independent from the AHB bus clock that is used to access ADC registers.

The adc_ker_ck input clock can be selected between different clock sources (see Figure 86: ADC clock scheme). This selection is done in the RCC (refer to section Reset and clock control (RCC) for more information):

1. The ADC clock can be provided by an internal or external clock source, which is independent and asynchronous from the AHB clock.
2. The ADC clock can be derived from AHB clock (selected in RCC).

Option 1 has the advantage of achieving the maximum ADC clock frequency whatever the AHB clock scheme selected.

Option 2 corresponds to a pseudosynchronous clock. This can be useful when the ADC is triggered by a timer and the application requires that the ADC is accurately triggered without any uncertainty (otherwise, an uncertainty of the trigger instant time is added by the resynchronizations between the two clock domains). This accurate trigger is supported only by trgo or trgo2 timer triggers.

For further details on the synchronization between ADC and timers, refer to section ADC synchronization in each timer section, and to section Peripheral clock distribution in the RCC section.

The clock is configured through the RCC and must be compliant with the operating frequency specified in the device datasheet.

**Figure 86. ADC clock scheme** (described in prose)

The RCC (Reset and clock controller) supplies two clocks to the "ADC12 or ADC3" block:

- adc_hclk goes to the AHB interface.
- adc_ker_ck(1) goes to the analog ADC1, 2, 3 as Fadc_ker_ck.

Footnote (1): Refer to RCC section for the exact clock naming.

*Digest note:* This chapter defines no clock prescaler or clock-mode field in the ADC itself. The ADC common registers (ADCC_CCR) have no PRESC or CKMODE field. Kernel clock selection and prescaling are done only in the RCC. The ST CMSIS header stm32c552xx.h names the controls as follows (the RCC chapter is authoritative):

- RCC_CCIPR2.ADCDACSEL[1:0] at bits 11:10: ADC and DAC kernel clock source selection.
- RCC_CCIPR2.ADCDACPRE[2:0] at bits 14:12: ADC and DAC prescaler for the kernel clock source.
- RCC_AHB2ENR.ADC12EN at bit 10: ADC1 and ADC2 clock enable.
- RCC_AHB2RSTR.ADC12RST at bit 10: ADC1 and ADC2 reset.

The datasheet gives fADC = 8 MHz min to 36 MHz max (2.7 V ≤ VDDA ≤ 3.6 V).

#### Clock ratio constraint between ADC clock and AHB clock

There are no constraints to respect for the ratio between the ADC clock and the AHB clock. However, the ratio must be carefully chosen to avoid any overrun especially if the clock AHB is much slower than the ADC clock.

When adc_hclk operates at a higher frequency than adc_ker_ck, writing to the AHB register does not immediately update the ADC configuration due to clock domain crossing delays. To guarantee that the configuration is properly applied within the adc_ker_ck domain, it is necessary to wait for four adc_ker_ck clock cycles after the AHB register update.

### 21.4.4 ADC connectivity

ADC inputs are connected to external channels as well as internal sources as described below.

**Figure 87. ADC1 connectivity** (described in prose)

ADC1 channel selection maps its inputs to the SAR ADC1 VIN (referenced between VREF+ and VREF-):

- VIN[0] = ADC1_IN0
- VIN[1] = ADC1_IN1
- VIN[2] = ADC1_IN2(1)
- VIN[3] = ADC1_IN3
- VIN[4] = ADC1_IN4
- VIN[5] = ADC1_IN5(1)
- VIN[6] = ADC1_IN6(1)
- VIN[7] = ADC1_IN7(1)
- VIN[8] = ADC1_IN8
- VIN[9] = ADC1_IN9
- VIN[10] = ADC1_IN10
- VIN[11] = ADC1_IN11
- VIN[12] = VSENSE
- VIN[13] = VREFINT

Notes:

1. On the STM32C53x/542 devices, these external channels can be connected to two GPIOs selected through the SBS_PMCR register.

*Digest note:* The two-GPIO selection through SBS_PMCR in footnote (1) applies to STM32C53x/542 only, not to STM32C55xxx.

**Figure 88. ADC2 connectivity** (described in prose)

ADC2 channel selection maps VIN[i] = ADC2_INi for i = 0 to 13 (ADC2_IN0 ... ADC2_IN13) to the SAR ADC2 VIN (referenced between VREF+ and VREF-). ADC2 has no internal channels.

**Figure 89. ADC3 connectivity** (described in prose)

ADC3 channel selection maps VIN[i] = ADC3_INi for i = 0 to 13 (ADC3_IN0 ... ADC3_IN13) to the SAR ADC3 VIN (referenced between VREF+ and VREF-).

*Digest note:* ADC3 is absent on STM32C55xxx.

### 21.4.5 Slave AHB interface

The ADCs implement an AHB slave port for control/status register and data access. The features of the AHB interface are listed below:

- Word accesses
- Single cycle response
- Response to all read/write accesses to the registers with zero wait states.

The AHB slave interface does not support split/retry requests, and it can generate AHB error in case of wrong HSIZE.

### 21.4.6 ADC Deep-power-down mode (DEEPPWD) and ADC voltage regulator (ADVREGEN)

By default, the ADC is in deep-power-down mode where its supply voltage is internally switched off to reduce the leakage currents (the reset state of the DEEPPWD bit is 1 in the ADC_CR register).

To activate the ADC, first exit the Deep-power-down mode by clearing the DEEPPWD bit. Then, it is mandatory to enable the ADC internal voltage regulator by setting the ADVREGEN bit of the ADC_CR register. The software must wait for the startup time of the ADC voltage regulator (TADCVREG_STUP) before launching a calibration or enabling the ADC. This delay must be implemented by software. For the startup time of the ADC voltage regulator, refer to the device datasheet for TADCVREG_STUP parameter.

When ADC operations are complete, the ADC can be disabled by clearing the ADEN bit of the ADC_CR register. Power can then be saved by disabling the ADC voltage regulator (by clearing ADVREGEN).

Additional power can be saved by entering ADC Deep-power-down mode again (by setting DEEPPWD of ADC_CR register). This is particularly interesting before entering Stop mode.

*Note:* Setting DEEPPWD automatically disables the ADC voltage regulator and the ADVREGEN bit is automatically cleared.

When the internal voltage regulator is disabled (ADVREGEN cleared), the internal analog calibration is kept.

In ADC Deep-power-down mode (DEEPPWD = 1), the internal analog calibration is lost and it is necessary to either relaunch a calibration or reapply the calibration factor, which was previously saved (refer to Section Calibration).

*Digest note:* The STM32C55xxx datasheet gives tADCVREG_STUP (ADC LDO startup time) = 10 µs max. The ADC_ISR register also has an LDORDY flag (bit 12, "ADC internal voltage regulator output ready"), with an LDORDYIE interrupt enable. See Section 21.6.1. This section still says the delay must be implemented by software.

### 21.4.7 Calibration (ADCAL, ADC_CALFACT)

Each ADC provides an automatic calibration procedure that drives all the calibration sequences including the power-on/off sequence of the ADC. During the procedure, the ADC calculates a calibration factor, which is 7-bit wide and is applied internally to the ADC until the next ADC power-off. During the calibration procedure, the application must not use the ADC and must wait until calibration is complete.

Calibration is preliminary to any ADC operation. It removes the offset error which may vary from chip to chip due to process or bandgap variation.

The calibration is initiated by software by setting bit ADCAL = 1. Calibration can only be initiated when the ADC is disabled (when ADEN = 0). The ADCAL bit stays at 1 during all the calibration sequence. It is then cleared by hardware as soon the calibration completes. At this time, the associated calibration factor is stored internally in the analog ADC and also in the bits CALFACT[6:0] of the ADC_CALFACT register.

The internal analog calibration is kept if the ADC is disabled (ADEN = 0). However, if the ADC is disabled for extended periods, then it is recommended that a new calibration cycle is run before reenabling the ADC.

The internal analog calibration is lost each time the power of the ADC is removed (for example, when the product enters Standby). In this case, to avoid spending time recalibrating the ADC, it is possible to rewrite the calibration factor into the ADC_CALFACT register without recalibrating, supposing that the software has previously saved the calibration factor delivered during the previous calibration.

The calibration factor can be written if the ADC is enabled but not converting (ADEN = 1 and ADSTART = 0 and JADSTART = 0). Then, at the next start of conversion, the calibration factor is automatically injected into the analog ADC. This loading is transparent and does not add any cycle latency to the start of the conversion. It is recommended to recalibrate when the VREF+ voltage changed more than 10% (see Section 21.4.31: Monitoring the internal voltage reference).

#### Software procedure to calibrate the ADC

1. Ensure DEEPPWD = 0, ADVREGEN = 1 and that ADC voltage regulator startup time has elapsed.
2. Ensure that ADEN = 0.
3. Set ADCAL.
4. Wait until ADCAL = 0.
5. The calibration factor can be read from the ADC_CALFACT register.

**Figure 90. ADC calibration** (described in prose)

Software sets ADCAL. The ADC state then goes from OFF to "Startup" and then to "Calibrate". The whole period, labeled tCAB, runs from the rising edge of ADCAL (by S/W) to its falling edge (by H/W). The ADC state then returns to OFF. CALFACT[6:0] reads 0x00 during the sequence and shows the "Calibration factor" once ADCAL is cleared. Timings are indicative.

*Digest note:* The STM32C55xxx datasheet gives tOFF_CAL (offset calibration time) = 85 × 1/fADC.

#### Software procedure to reinject a calibration factor into the ADC

1. Ensure ADEN = 1 and ADSTART = 0 and JADSTART = 0 (ADC enabled and no conversion is ongoing).
2. Write CALFACT with the new calibration factors.
3. When a conversion is launched, the calibration factor is injected into the analog ADC only if the internal analog calibration factor differs from the one stored in bits CALFACT.

**Figure 91. Updating the ADC calibration factor** (described in prose)

1. The ADC is "Ready (not converting)" and the internal calibration factor[6:0] is F1.
2. Software writes ADC_CALFACT, so CALFACT[6:0] becomes F2.
3. At the next start conversion (hardware or software), an "Updating calibration" interval occurs at the start of the conversion. The internal calibration factor changes from F1 to F2 while the ADC is "Converting channel (Single ended)".
4. The ADC returns to Ready.
5. A further start conversion converts with F2 and no update.

### 21.4.8 ADC on-off control (ADEN, ADDIS, ADRDY)

First, follow the procedure described in Section 21.4.6: ADC Deep-power-down mode (DEEPPWD) and ADC voltage regulator (ADVREGEN)).

Once DEEPPWD is cleared and ADVREGEN is set, the ADC can be enabled. It requires a tSTAB stabilization time before starting converting accurately (see Figure 92).

Two control bits enable or disable the ADC:

- Set ADEN to enable the ADC. The ADRDY flag is set once the ADC is ready for operation.
- Set ADDIS to disable the ADC. ADEN and ADDIS are automatically deasserted by hardware as soon as the analog ADC is effectively disabled.

Regular conversions can then start either by setting ADSTART (refer to Section 21.4.19: Conversion on external trigger and trigger polarity (EXTSEL, EXTEN, JEXTSEL, JEXTEN)) or when an external trigger event occurs if regular triggers are enabled.

Injected conversions start by setting JADSTART or when an external injected trigger event occurs, if injected triggers are enabled.

#### Software procedure to enable the ADC

1. Clear the ADRDY bit in the ADC_ISR register by programming it to 1.
2. Set ADEN.
3. Wait until ADRDY = 1 (ADRDY is set after the ADC startup time). This can be done by using the associated interrupt (ADRDYIE must be set).
4. Clear the ADRDY bit in the ADC_ISR register by programming it to 1 (optional).

#### Software procedure to disable the ADC

1. Check that both ADSTART = 0 and JADSTART = 0 to ensure that no conversion is ongoing. If required, stop all regular and injected ongoing conversions by setting ADSTP and JADSTP. Then wait until ADSTP = 0 and JADSTP = 0.
2. Set ADDIS.
3. If required by the application, wait for ADEN = 0, until the analog ADC is effectively disabled (ADDIS is automatically reset once ADEN = 0).

**Figure 92. Enabling/disabling the ADC** (described in prose)

1. Software sets ADEN and the ADC state goes from OFF to "Startup".
2. After tSTAB, hardware sets ADRDY and the state becomes RDY. Software then clears ADRDY.
3. The ADC converts a channel ("Converting CH") and returns to RDY.
4. Software sets ADDIS. The state passes through "REQ-OF" (request off).
5. Hardware then clears both ADEN and ADDIS at the same time and the state returns to OFF.

*Digest note:* The STM32C55xxx datasheet gives tSTAB (ADC power-up time, LDO already started) = 1 conversion cycle min.

### 21.4.9 Constraints when writing the ADC control bits

The software is allowed to write the RCC control bits to configure and enable the ADC clock (refer to RCC section) and configure the ADEN bit in the ADC_CR register, only if the ADC is disabled (ADEN must be cleared).

The software can write the ADSTART, JADSTART and ADDIS control bits in the ADC_CR register only if the ADC is enabled and there is no pending request to disable the ADC (ADEN must be equal to 1 and ADDIS to 0).

The following constraints apply to all the other control bits of the ADC_CFGRx, ADC_SMPRx, ADC_TRy, ADC_SQRy, ADC_JDRy, ADC_OFRy, ADC_OFCHRy and ADC_IER registers:

- For control bits related to configuration of regular conversions, the software is allowed to write them only if no regular conversions are ongoing (ADSTART must be cleared).
- For control bits related to configuration of injected conversions, the software is allowed to write them only if no injected conversions are ongoing (JADSTART must be cleared).
- ADC_TRy register thresholds can be modified when an analog-to-digital conversion is ongoing (refer to Section 21.4.27: Analog window watchdog (AWD1EN, JAWD1EN, AWD1SGL, AWD1CH, AWDCH of ADC_AWD2CR and ADC_AWD3CR, HTR, LTR, AWDFILT) for details).
- To modify the all above control bits when the software trigger function is used, an ADSTP or JADSTP must be issued to make sure all activities are stopped, even if ADSTART and JADSTART are cleared.

The software is allowed to write the ADSTP or JADSTP control bits in the ADC_CR register only if the ADC is enabled and if there is no pending request to disable the ADC.

*Note:* Not all forbidden write accesses to ADC control bits are protected by hardware. In some cases, the ADC state may become unknown. To recover from this situation, the ADC must be disabled (ADEN = 0 as well as all the bits of the ADC_CR register).

*Digest note:* The register names ADC_TRy, ADC_JDRy and ADC_OFCHRy in this list do not match the register names in Section 21.6. The threshold registers are ADC_AWDxLTR/ADC_AWDxHTR and the offset channel configuration registers are ADC_OFCFGRy. The names are kept as printed.

### 21.4.10 Channel selection (ADC_SQRy, ADC_JSQR)

The ADC features up to 14 multiplexed channels per ADC, out of which:

- Up to 14 analog inputs coming from GPIO pads (ADCx_IN[i]). Depending on the device, not all of them are available on GPIO pads.
- The ADC is connected to up to 2 internal analog inputs:
  - internal reference voltage (VREFINT)
  - Internal temperature sensor (VSENSE)

  To convert one of the internal analog channels, the corresponding analog sources must first be enabled by programming VREFEN, TSEN in the ADCC_CCR registers.

Refer to ADC interconnection tables in Section 21.4.2: ADC pins and internal signals for the connection of the above internal analog inputs to ADC pins.

The conversions can be organized in two groups: regular and injected. A group consists of a sequence of conversions that can be done on any channel and in any order. For instance, it is possible to implement the conversion sequence in the following order: ADCx_IN3, ADCx_IN8, ADCx_IN2, ADCx_IN2, ADCx_IN0, ADCx_IN2, and ADCx_IN2.

- A regular group is composed of up to 16 conversions. The regular channels and their order in the conversion sequence must be selected in the ADC_SQRy registers. The total number of conversions in the regular group must be written in the LEN[3:0] bits in the ADC_SQR1 register.
- An injected group is composed of up to four conversions. The injected channels and their order in the conversion sequence must be selected in the ADC_JSQR register. The total number of conversions in the injected group must be written in the JLEN[1:0] bits in the ADC_JSQR register.

ADC_SQRy registers must not be modified while a regular conversion is ongoing. ADC regular conversions must consequently be stopped by setting ADSTP (refer to Section 21.4.18: Stopping an ongoing conversion (ADSTP, JADSTP)).

### 21.4.11 Channel preselection register (ADC_PCSEL)

The PCSEL bit of the ADC_PCSEL register controls the analog switch integrated in the I/O. For each channel selected through SQRx or JSQRx bits, the corresponding PCSEL bit must be configured in advance in the ADC_PCSEL register. The ADC input multiplexer selects the ADC input according to SQRx and JSQRx configuration with very high speed. The analog switch integrated in the I/O cannot react as fast as the ADC multiplexer. To avoid the delay due to the analog switch control on the I/O, it is necessary to preselect the input channels that are selected through the SQRx and JSQRx. The selection is based on the VIN of each ADC input. For example, if the ADC converts ADCx_IN1, PCSEL1 bit must also be set in ADC_PCSEL register.

*Note:* Configuring the PCSEL bit is not necessary for the internal channels (such as VREFINT).

### 21.4.12 Channel-wise programmable sampling time (SMPR1, SMPR2)

Before starting a conversion, the ADC must establish a direct connection between the voltage source under measurement and the embedded sampling capacitor of the ADC. This sampling time must be sufficient for the input voltage source to charge the embedded capacitor to the input voltage level.

Each channel can be sampled with a different sampling time, which is programmable through the SMP[2:0] bits of the ADC_SMPR1 and ADC_SMPR2 registers. It is therefore possible to select among the following sampling time values:

- SMP = 000: 3 ADC clock cycles
- SMP = 001: 5 ADC clock cycles
- SMP = 010: 8 ADC clock cycles
- SMP = 011: 13 ADC clock cycles
- SMP = 100: 25 ADC clock cycles
- SMP = 101: 48 ADC clock cycles
- SMP = 110: 139 ADC clock cycles
- SMP = 111: 289 ADC clock cycles

The total conversion time is calculated as follows (12-bit mode):

TCONV = Sampling time + 13 ADC clock cycles

#### Example

With Fadc_ker_ck = 32 MHz and a sampling time of 3 ADC clock cycles:

TCONV = (3 + 13) × ADC clock cycles = 16 ADC clock cycles = 500 ns

The ADC notifies the end of the sampling phase by asserting the EOSMP flag (only for regular conversion).

*Digest note:* The STM32C55xxx datasheet counts cycles differently. It specifies tS = 2.5 to 288.5 × 1/fADC and tCONV = tS + 1.5 + N (N = resolution in bits). The totals agree with this section: 2.5 + 1.5 + 12 = 16 cycles = 3 + 13. At the datasheet maximum fADC = 36 MHz, SMP = 111 (289 cycles) is about 8.0 µs.

#### Constraints on the sampling time

For each channel, SMP[2:0] bits must be programmed to respect a minimum and a maximum sampling times as specified in the ADC characteristics section of the datasheets.

#### Bulb sampling mode

The bulb sampling mode enables to obtain longer sampling time.

When the BULB bit is set in the ADC_CFGR2 register, the sampling period starts immediately after the last ADC conversion. A hardware or software trigger starts the conversion after the sampling time has been programmed in ADC_SMPRx registers. The very first ADC conversion after the ADC is enabled, is performed with the sampling time programmed in SMP bits. The bulb mode is effective starting from the second conversion.

The maximum sampling time is limited (refer to the ADC characteristics section of the datasheet).

Bulb mode is supported exclusively in regular conversion; dual mode is not supported.

The BULB bit can be modified only when the ADEN bit of the ADC_CR register is cleared.

When the BULB bit is set, it is not allowed to set the SMPTRIG bit in ADC_CFGR2.

**Figure 93. Bulb mode timing diagram** (described in prose)

- **Normal (discontinuous) mode.** Each trigger starts a sample phase followed by a conversion phase, and the ADC is idle between them: idle, sample, conversion, idle, sample, conversion, idle.
- **Bulb (discontinuous) mode.** After each conversion the ADC immediately enters a sample phase and stays in it until the next trigger: idle, sample, conversion, sample, conversion, sample. The trigger then starts the conversion. The figure labels the sample phase before the second trigger "Sampling time programmed in SMP bits".

#### Sampling time control trigger mode

When the SMPTRIG bit is set, the sampling time programmed through SMPx bits is not applicable. The sampling time is controlled by the trigger signal edge.

When a hardware trigger is selected (EXTEN[1:0] = 01), each rising edge of the trigger signal starts the sampling period. A falling edge ends the sampling period and starts the conversion.

Due to the synchronization mechanism, the minimum allowed pulse width is seven adc_ker_ck periods.

When a software trigger is selected (EXTEN[1:0] = 00), the software trigger is not the ADSTART bit of ADC_CR but the SWTRIG bit. The SWTRIG bit has to be set to start the sampling period, and it has to be cleared to end the sampling period and start the conversion. In this mode, the minimum sampling time is limited to seven ADC clock cycles.

The maximum sampling time is limited (refer to the ADC characteristics section of the datasheet).

This mode is only compatible with the discontinuous mode. DISCNUM must be cleared for regular conversion mode. It is not supported for injected conversion mode and autoinjection mode.

When the SMPTRIG bit is set, setting the BULB bit is not allowed and only regular conversion is supported.

The sampling time control trigger mode is not compatible with the following dual modes: DUAL[4:0] = 0b00010, 0b00011, 0b00101, 0b00110, 0b00111, and 0b01001.

### 21.4.13 Single conversion mode

To enable the single conversion mode for regular channels, clear both CONT and DISCEN bits in ADC_CFGR1 register. To enable it on injected channel, clear JDISCEN bit.

In single conversion mode, the ADC performs once all the regular conversions of the programmed channels. This mode is started by one of the following events:

- ADSTART bit set in the ADC_CR register (for a regular channel)
- JADSTART bit set in the ADC_CR register (for an injected channel)
- An external hardware trigger event (for a regular or injected channel)

Inside the regular sequence, after each conversion is complete:

- The converted data are stored into the 32-bit 8-level FIFO accessible through the ADC_DR register,
- The EOC (end of regular conversion) flag is set, and
- An interrupt is generated if the EOCIE bit is set.

Inside the injected sequence, after each conversion is complete:

- The converted data are stored into one of the four 32-bit ADC_JDRy registers,
- The JEOC (end of injected conversion) flag is set, and
- An interrupt is generated if the JEOCIE bit is set.

After the regular sequence is complete:

- The EOS (end of regular sequence) flag is set, and
- An interrupt is generated if the EOSIE bit is set.

After the injected sequence is complete:

- The JEOS (end of injected sequence) flag is set, and
- An interrupt is generated if the JEOSIE bit is set.

The ADC then stops until a new external regular or injected trigger occurs or until the ADSTART or JADSTART bit is set again.

*Note:* To convert a single channel, program a sequence with a length of 1.

### 21.4.14 Continuous conversion mode (CONT = 1)

This mode applies to regular channels only.

In continuous conversion mode, when a software or hardware regular trigger event occurs, the ADC performs once all the regular conversions of the channels and then automatically restarts and continuously converts all the conversions of the sequence. This mode is started by setting the CONT bit of the ADC_CFGR1 register, either by an external trigger or by setting the ADSTART bit in the ADC_CR register.

Inside the regular sequence, after each conversion is complete:

- The converted data are stored into the eight 32-bit word FIFO accessible through the ADC_DR register.
- The EOC (end of conversion) flag is set, and
- An interrupt is generated if the EOCIE bit is set.

After the sequence of conversions is complete:

- The EOS (end of sequence) flag is set, and
- An interrupt is generated if the EOSIE bit is set.

Then, a new sequence restarts immediately and the ADC continuously repeats the conversion sequence.

*Note:* To convert a single channel, program a sequence with a length of 1.

It is not possible to have both discontinuous mode and continuous mode enabled, this means that it is forbidden to set both DISCEN and CONT bits.

Injected channels cannot be converted continuously. The only exception is when an injected channel is configured to be converted automatically after regular channels in continuous mode (using JAUTO bit) (refer to Section : Autoinjection mode).

### 21.4.15 Discontinuous mode (DISCEN, DISCNUM, JDISCEN)

#### Regular group mode

This mode is enabled by setting the DISCEN and CONT = 0 bit in the ADC_CFGR1 register.

It is used to convert a short sequence (subgroup) of n conversions (n ≤ 8) that is part of the sequence of conversions selected in the ADC_SQRy registers. The value of n is specified by writing to the DISCNUM[2:0] bits in the ADC_CFGR1 register.

When an external trigger occurs, it starts the next n conversions selected in the ADC_SQRy registers until all the conversions in the sequence are done. The total sequence length is defined by the LEN[3:0] bits in the ADC_SQR1 register.

Example:

- DISCEN = 1, n = 3, channels to be converted = 1, 2, 3, 6, 7, 8, 9, 10, 11
  - First trigger: channels converted are 1, 2, 3 (an EOC event is generated at the end of each conversion).
  - Second trigger: channels converted are 6, 7, 8 (an EOC event is generated at the end of each conversion).
  - Third trigger: channels converted are 9, 10, 11 (an EOC event is generated at the end of each conversion) and an EOS event is generated after the conversion of channel 11.
  - Fourth trigger: channels converted are 1, 2, 3 (an EOC event is generated at the end of each conversion).
  - ...
- DISCEN = 0, channels to be converted = 1, 2, 3, 6, 7, 8, 9, 10, 11
  - First trigger: the complete sequence is converted: channel 1, then 2, 3, 6, 7, 8, 9, 10 and 11. Each conversion generates an EOC event and the last one also generates an EOS event.
  - All the next trigger events relaunch the complete sequence.

*Note:* The channel numbers referred to in the above example might not be available on all devices.

When a regular group is converted in discontinuous mode, no rollover occurs (the last subgroup of the sequence can have less than n conversions).

When all subgroups are converted, the next trigger starts the conversion of the first subgroup. In the example above, the fourth trigger reconverts the channels 1, 2 and 3 in the first subgroup.

It is not possible to have both discontinuous mode and continuous mode enabled. In this case (if DISCEN = 1, CONT = 1), the ADC behaves as if continuous mode was disabled.

#### Injected group mode

This mode is enabled by setting the JDISCEN bit in the ADC_CFGR1 register. It converts the sequence selected in the ADC_JSQR register, channel by channel, after an external injected trigger event. This is equivalent to discontinuous mode for regular channels with DISCNUM = 0.

When an external trigger occurs, it starts the next channel conversions selected in the ADC_JSQR registers until all the conversions in the sequence are done. The total sequence length is defined by the JLEN[1:0] bits in the ADC_JSQR register.

Example:

- JDISCEN = 1, channels to be converted = 1, 2, 3
  - First trigger: channel 1 converted (a JEOC event is generated)
  - Second trigger: channel 2 converted (a JEOC event is generated)
  - Third trigger: channel 3 converted and a JEOC event + a JEOS event are generated
  - ...

*Note:* The channel numbers referred to in the above example might not be available on all devices.

When all injected channels have been converted, the next trigger starts the conversion of the first injected channel. In the example above, the fourth trigger reconverts the first injected channel 1.

It is not possible to use both autoinjection mode and discontinuous mode simultaneously: the bits DISCEN and JDISCEN must be kept cleared by software when JAUTO is set.

### 21.4.16 Starting conversions (ADSTART, JADSTART)

ADC regular conversions can be started by setting ADSTART.

When ADSTART is set, the conversion starts:

- Immediately if EXTEN[1:0] = 00 (software trigger), or
- At the next active edge of the selected regular hardware trigger, if EXTEN[1:0] is not equal to 00.

The application software starts ADC injected conversions by setting JADSTART.

When JADSTART is set, the conversion starts:

- Immediately if JEXTEN[1:0] = 00 (software trigger), or
- At the next active edge of the selected injected hardware trigger, if JEXTEN[1:0] is not equal to 00.

*Note:* In autoinjection mode (JAUTO = 1), use the ADSTART bit to start regular conversions followed by autoinjected conversions (JADSTART must be kept cleared).

When the hardware trigger is enabled, ADSTART and JADSTART also indicate whether an ADC operation is ongoing. The ADC can be reconfigured while ADSTART and JADSTART are both cleared, indicating that the ADC is idle.

In the case of software triggering, ADSTP and/or JADSTP must be set before ADC reconfiguration.

ADSTART is deasserted by hardware:

- In single mode with software regular trigger (CONT = 0, EXTEN = 0x0): at any end of regular conversion sequence (EOS assertion)
- In discontinuous mode (CONT = 0, DISCEN = 1, DISCNUM= x): at any of subgroup sequence
- In all cases (CONT and EXTEN don't care), after execution of the ADSTP procedure asserted by the software

*Note:* In continuous mode (CONT = 1), ADSTART is not deasserted by hardware when EOS is asserted because the sequence is automatically relaunched.

When a hardware trigger is selected in single mode (CONT = 0 and EXTEN ≠ 0x00), ADSTART is not deasserted by hardware when EOS is asserted to help the software that does not need to reset ADSTART again for the next hardware trigger event. This ensures that no further hardware triggers are missed.

JADSTART is deasserted by hardware:

- In single mode with software injected trigger (JEXTEN = 0x0): at the end of each injected conversion sequence (JEOS assertion)
- In discontinuous mode (JDISCEN = 1): at the end of any conversion
- In all cases (JEXTEN=x), after execution of the JADSTP procedure asserted by the software

*Note:* When the software trigger is selected, the ADSTART bit must not be set if the EOC flag is still high.

In bulb mode (BULB = 1), the previous end-of-conversion automatically starts the sampling, then setting ADSTART starts the conversion including the programmed sampling time.

In sampling time control trigger mode (SMPTRIG = 1), SWTRIG bit must be set to start the conversion.

*Digest note:* The ADC_CR.ADSTART description (Section 21.6.3) says something different. It says that in single conversion mode with software trigger, ADSTART is cleared by hardware "immediately after regular conversion starts", whereas this section says it is cleared at EOS. Two other points from this chapter:

- Section 21.4.9 says register reconfiguration with the software trigger needs an ADSTP or JADSTP, even when ADSTART and JADSTART are cleared.
- The note above forbids setting ADSTART while EOC is still set.

### 21.4.17 Timing

The elapsed time between the start of a conversion and the end of a conversion is the sum of the configured sampling time plus the successive approximation time depending on data resolution:

TCONV = TSMPL + TSAR = [3 (min) + 13 (12bit)] x TADC_CLK

TCONV = TSMPL + TSAR = 93.75 ns (min) + 406.25 ns (12bit) = 500 ns (for Fadc_ker_ck = 32 MHz)

**Figure 94. Analog-to-digital conversion time** (described in prose)

1. The ADC starts in RDY and software sets ADSTART.
2. The ADC is in "Sampling Ch(N)", during which the internal S/H samples AIN(N)(1) for tSMPL(2).
3. Hardware then sets EOSMP and the ADC moves to "Converting Ch(N)". The S/H holds AIN(N) for tSAR(3). Software clears EOSMP during the conversion.
4. At the end of the conversion, ADC_DR changes from Data N-1 to Data N and hardware sets EOC. EOC is later cleared by HW/SW.
5. Sampling of Ch(N+1) starts (AIN(N+1)). Timings are indicative.

Notes:

1. AIN represents the input voltage captured by the internal Sample and Hold (S/H) capacitor.
2. tSMPL depends on SMP[2:0].
3. tSAR depends on RES[2:0].

*Note:* The bulb and the sampling time control trigger modes are not described in Figure 94: Analog-to-digital conversion time.

### 21.4.18 Stopping an ongoing conversion (ADSTP, JADSTP)

The software can decide to stop ongoing regular conversions by setting ADSTP and ongoing injected conversions by setting JADSTP.

Stopping conversions resets the ongoing ADC operation. The ADC can then be reconfigured (for example by changing the channel selection or the trigger). It is then ready for a new operation.

Injected conversions can be stopped while regular conversions are still ongoing and vice versa. This allows, for instance, the reconfiguration of the injected conversion sequence and triggers while regular conversions are still ongoing (and vice versa).

When the ADSTP bit is set by software, any ongoing regular conversion is aborted with the partial result discarded (the ADC_DR register is not updated with the current conversion).

When the JADSTP bit is set by software, any ongoing injected conversion is aborted with partial result discarded (the ADC_JDRy register is not updated with the current conversion). The scan sequence is also aborted and reset (meaning that relaunching the ADC restarts a new sequence).

Once this procedure is complete, ADSTP/ADSTART bits (for regular conversion), or JADSTP/JADSTART bits (for injected conversion) are deasserted by hardware and the software must poll ADSTART (or JADSTART) until the bit is reset before assuming the ADC is completely stopped.

*Note:* In autoinjection mode (JAUTO = 1), setting the ADSTP bit aborts both regular and injected conversions (JADSTP must not be used).

**Figure 95. Stopping ongoing regular conversions** (described in prose)

1. Software sets ADSTART and regular conversions are ongoing. During this time software is not allowed to configure the regular conversion selection and triggers.
2. A trigger causes "Sample Ch(N-1)", then "Convert Ch(N-1)", and ADC_DR goes from Data N-2 to Data N-1. The ADC returns to RDY.
3. A second trigger starts "Sample Ch(N)". Software sets ADSTP during this sample, and the conversion is cut short.
4. Hardware clears ADSTP and ADSTART together and the ADC returns to RDY. ADC_DR keeps Data N-1.

**Figure 96. Stopping ongoing regular and injected conversions** (described in prose)

1. Software sets both JADSTART and ADSTART. Injected and regular conversions are ongoing, and software is not allowed to configure their selections and triggers.
2. A regular trigger starts "Sample Ch(N-1)" and "Convert Ch(N-1)". An injected trigger then starts "Sample Ch(M)".
3. Software sets JADSTP during Ch(M). Hardware clears JADSTP and JADSTART, and ADC_JDR keeps DATA M-1.
4. A later regular trigger starts sampling. Software sets ADSTP, and hardware clears ADSTP and ADSTART. ADC_DR holds DATA N-1 (previously DATA N-2).

### 21.4.19 Conversion on external trigger and trigger polarity (EXTSEL, EXTEN, JEXTSEL, JEXTEN)

A conversion or a sequence of conversions can be triggered either by software or by an external event (for example timer capture, input pins). If the EXTEN[1:0] control bits (for a regular conversion) or JEXTEN[1:0] bits (for an injected conversion) are different from 0b00, then external events are able to trigger a conversion with the selected polarity.

The regular trigger selection is effective once the software has set ADSTART while the injected trigger selection is effective once the software has set JADSTART bit.

All hardware triggers that occur while a conversion is ongoing are ignored:

- If ADSTART = 0, regular hardware triggers are ignored.
- If JADSTART = 0, injected hardware triggers are ignored.

Table 140 provides the correspondence between the EXTEN[1:0] and JEXTEN[1:0] values and the trigger polarity.

**Table 140. Configuring the trigger polarity for regular external triggers**

| EXTEN[1:0] | Source |
|---|---|
| 00 | Hardware trigger detection disabled, software trigger detection enabled |
| 01 | Hardware trigger with detection on the rising edge (sampling time controlled in SMPTRIG mode) |
| 10 | Hardware trigger with detection on the falling edge |
| 11 | Hardware trigger with detection on both the rising and falling edges |

*Note:* The polarity of the regular trigger cannot be changed on-the-fly.

**Table 141. Configuring the trigger polarity for injected external triggers**

| JEXTEN[1:0] | Source |
|---|---|
| 00 | Hardware Trigger detection disabled, software trigger detection enabled |
| 01 | Hardware Trigger with detection on the rising edge |
| 10 | Hardware Trigger with detection on the falling edge |
| 11 | Hardware Trigger with detection on both the rising and falling edges |

The EXTSEL and JEXTSEL control bits select which, out of 32 possible events, can trigger the conversion of the regular and injected groups.

A regular group conversion can be interrupted by an injected trigger.

**Figure 97. Triggers shared between ADC master and slave** (described in prose)

The regular sequencer triggers adc_ext_trg0 ... adc_ext_trg31 feed the external regular trigger multiplexer of both the ADC MASTER and the ADC SLAVE (selected by EXTSEL[3:0] in the figure). The injected sequencer triggers adc_jext_trg0 ... adc_jext_trg31 feed the external injected trigger multiplexer of both ADCs (selected by JEXTSEL[4:0]).

*Digest note:* The figure labels the regular selector EXTSEL[3:0]. The register field is EXTSEL[4:0] (ADC_CFGR1 bits 9:5).

Refer to ADC interconnection tables in Section 21.4.2: ADC pins and internal signals for the list of the external triggers.

### 21.4.20 Injected channel management

#### Triggered injection mode

To use triggered injection, the JAUTO bit in the ADC_CFGR1 register must be cleared.

1. Start the conversion of a group of regular channels either by an external trigger or by setting the ADSTART bit in the ADC_CR register.
2. If an external injected trigger occurs, or if the JADSTART bit in the ADC_CR register is set during the conversion of a regular group of channels, the current conversion is reset and the injected channel sequence switches are launched (all the injected channels are converted once if JDISCEN = 0).
3. Then, the regular conversion of the regular group of channels is resumed from the last interrupted regular conversion.
4. If a regular event occurs during an injected conversion, the injected conversion is not interrupted but the regular sequence is executed at the end of the injected sequence. Figure 98 shows the corresponding timing diagram.

*Note:* When using triggered injection, one must ensure that the interval between trigger events is longer than the injection sequence.

**Figure 98. Injected conversion latency during ongoing regular conversion** (described in prose)

The figure shows an injection event that resets the ADC, synchronized to adc_ker_ck. The start of sampling of the injected conversion follows after a "max. latency"(1) measured from the injection event.

Notes:

1. The maximum latency value can be found in the electrical characteristics of the device datasheet.

#### Autoinjection mode

If the JAUTO bit in the ADC_CFGR1 register is set, then the channels in the injected group are automatically converted after the regular group of channels. This can be used to convert a sequence of up to 20 conversions programmed in the ADC_SQRy and ADC_JSQR registers.

In this mode, the ADSTART bit in the ADC_CR register must be set to start regular conversions, followed by injected conversions (JADSTART must be kept cleared). Setting the ADSTP bit aborts both regular and injected conversions (JADSTP bit must not be used).

In this mode, external trigger on injected channels must be disabled.

*Note:* Autoinjection mode is compatible with discontinuous mode.

*Digest note:* This note contradicts Section 21.4.15 and the JDISCEN/DISCEN bit descriptions, which say DISCEN and JDISCEN must be kept cleared when JAUTO is set.

### 21.4.21 Programmable resolution (RES) - fast conversion mode

Faster conversions can be performed by reducing the ADC resolution.

The resolution can be configured to be either 12, 10, 8, or 6 bits by programming the RES[1:0] control bits. Figure 103, Figure 104, Figure 105 and Figure 106 show the conversion result format with respect to the resolution as well as to the data alignment.

Lower resolution allows faster conversion time for applications where high-data precision is not required. It reduces the conversion time spent by the successive approximation steps according to Table 142.

**Table 142. TSAR timings depending on resolution**

| RES (bits) | TSAR (ADC clock cycles) | TSAR (ns) at Fadc_ker_ck = 32 MHz | TCONV (ADC clock cycles) (with Sampling time = 3 ADC clock cycles) | TCONV (ns) at Fadc_ker_ck = 32 MHz |
|---|---|---|---|---|
| 12 | 13 ADC clock cycles | 406.25 ns | 16 ADC clock cycles | 500.0 ns |
| 10 | 11 ADC clock cycles | 343.75 ns | 14 ADC clock cycles | 437.5 ns |
| 8 | 9 ADC clock cycles | 281.25 ns | 12 ADC clock cycles | 375.3 ns |
| 6 | 7 ADC clock cycles | 218.75 ns | 10 ADC clock cycles | 312.5 ns |

*Digest note:* 12 cycles at 32 MHz is 375.0 ns. The table prints 375.3 ns.

### 21.4.22 End of conversion and end of sampling phase (EOC, JEOC, EOSMP)

The ADC notifies the application at the end of each regular conversion (EOC) event and injected conversion (JEOC) event.

The ADC sets the EOC flag as soon as a new regular conversion data is available in the ADC_DR register. An interrupt can be generated if the EOCIE bit is set. The software can clear the EOC flag either by programming it to 1 or by reading ADC_DR. If ADC_DR FIFO is not emptied, the EOC flag is set again and an interrupt can be generated again.

The ADC sets the JEOC flag as soon as new injected conversion data is available in one of the ADC_JDRy registers. An interrupt can be generated if the JEOCIE bit is set. The software can clear the JEOC flag either by programming it to 1 or by reading the corresponding ADC_JDRy register.

The ADC also notifies the end of the sampling phase by setting the EOSMP flag (for regular conversions only). The EOSMP flag is cleared by software by programming it to 1. An interrupt can be generated if the EOSMPIE bit is set.

### 21.4.23 End of conversion sequence (EOS, JEOS)

The ADC notifies the application at the end of each regular sequence (EOS) and injected sequence (JEOS) event.

The ADC sets the EOS flag as soon as the conversion of the last data of the regular sequence is complete. An interrupt can be generated if the EOSIE bit is set. The EOS flag is cleared by the software by programming it to 1.

The ADC sets the JEOS flag as soon as the conversion of the last data of the injected sequence is complete. An interrupt can be generated if the JEOSIE bit is set. The JEOS flag is cleared by the software by programming it to 1.

### 21.4.24 Timing diagram examples (single/continuous modes, hardware/software triggers)

**Figure 99. Single conversions of a sequence, software trigger** (described in prose)

1. Software sets ADSTART(1). The ADC converts CH1, CH9, CH10 and CH17 in turn.
2. EOC pulses after each conversion and ADC_DR updates to D1, D9, D10 and D17. EOS pulses after CH17.
3. Hardware clears ADSTART at the end of CH17 (together with EOS) and the ADC returns to RDY.
4. Software sets ADSTART again. The sequence repeats (ADC_DR shows X during CH1, then D1, D9, D10, D17), and hardware again clears ADSTART at EOS.

Notes:

1. EXTEN[1:0] = 00, CONT = 0
2. Channels selected = 1, 9, 10, 17; AUTDLY = 0.

**Figure 100. Continuous conversion of a sequence, software trigger** (described in prose)

1. Software sets ADSTART(1). The ADC continuously converts CH1, CH9, CH10, CH17, CH1, CH9, CH10, with EOC after each conversion and EOS after each CH17.
2. Software sets ADSTP. The state goes to STP and then READY, and hardware clears ADSTART and ADSTP. The CH10 conversion in progress is aborted, so ADC_DR keeps D9.
3. Software sets ADSTART again and conversion restarts from CH1 (ADC_DR shows X, then D1).

Notes:

1. EXTEN[1:0] = 00, CONT = 1
2. Channels selected = 1, 9, 10, 17; AUTDLY = 0.

**Figure 101. Single conversions of a sequence, hardware trigger** (described in prose)

1. A TRGx edge that occurs before ADSTART is set is ignored.
2. Software sets ADSTART, which stays set for the rest of the diagram (it is not cleared at EOS).
3. The next rising TRGx edge triggers the sequence CH1, CH2, CH3, CH4, with EOC after each conversion and EOS after CH4. ADC_DR updates to D1, D2, D3, D4.
4. A TRGx edge that occurs while the sequence is running (during CH3) is ignored.
5. The ADC returns to READY, and the next rising edge converts the sequence again.

Notes:

1. TRGx (overfrequency) is selected as trigger source, EXTEN[1:0] = 01, CONT = 0
2. Channels selected = 1, 2, 3, 4; AUTDLY = 0.

**Figure 102. Continuous conversions of a sequence, hardware trigger** (described in prose)

1. Software sets ADSTART.
2. The first falling TRGx edge starts continuous conversion of CH1, CH2, CH3, CH4, CH1, CH2, CH3, CH4, CH1. EOC follows each conversion and EOS each CH4. ADC_DR shows D1 to D4 repeatedly.
3. Software sets ADSTP. The ADC goes through STOP to RDY, and hardware clears ADSTART and ADSTP.
4. A TRGx edge after that is ignored. Timings are not to scale.

Notes:

1. TRGx is selected as trigger source, EXTEN[1:0] = 10, CONT = 1.
2. Channels selected = 1, 2, 3, 4; AUTDLY = 0.

### 21.4.25 Data management

#### Data register, data alignment and offset (ADC_DR, ADC_JDRy, OFFSETy, OFFSETy_CH, OVSS, LSHIFT, JOVSS(a), JLSHIFT(a), USAT, SSAT, POSOFF)

Footnote (a): Only for products that include this bit.

#### Data and alignment

At the end of each regular channel conversion (when an EOC event occurs), the result of the converted data is stored in the 32-bit wide ADC_DR data register with FIFO (when OVRMOD = 0). Since the data register has eight levels of FIFO, the EOC flag is raised again as far as the FIFO is not emptied.

At the end of each injected channel conversion (when a JEOC event occurs), the result of the converted data is stored in the 32-bit wide corresponding ADC_JDRy data register.

The OVSS[3:0], LSHIFT[3:0], JOVSS[3:0], and JLSHIFT[3:0] bitfields in the ADC_CFGR2 register select the alignment of the data stored after the conversion. By default, data are right-aligned. Refer to Figure 103, Figure 104, Figure 105, and Figure 106 for examples of data alignment.

*Note:* The data can be aligned in normal and oversampling mode. The OVSS[3:0] bitfield is only effective in oversampling mode.

JOVSS[3:0] and JLSHIFT[3:0] is reserved for injected conversions. Their usage is the same as OVSS[3:0] and LSHIFT[3:0], unless otherwise specifically described.

*Digest note:* The ADC_CFGR2 register description (Section 21.6.5) has no JOVSS or JLSHIFT field, and the ST CMSIS header stm32c552xx.h defines neither. Footnote (a) suggests they are absent on this product family.

#### Offset

An unsigned offset value y (y = 1, 2, 3, 4) can be applied to a channel by programming a value different from 0 in the OFFSET[21:0] bitfield of the ADC_OFRy register. The channel to which the offset is applied is programmed to the OFFSETy_CH[4:0] bits of ADC_OFCFGRy register. The offset can be positive or negative depending on the value of POSOFF bit. When POSOFF is cleared, the converted value is subtracted by the user-defined offset written in OFFSET[21:0] bits. The result can be a negative value. The read data is consequently signed and the SEXT bit represents the extended sign value. The offset value must be lower than the maximum conversion value (for example the maximum offset value is 0xFFF in 12-bit mode).

The offset can be used to convert unsigned data to signed data (for example the offset value is equal to 0x800 in 12-bit mode).

The offset correction is also supported in oversampling mode. In this mode, the offset is subtracted when all the oversampling operations are complete.

*Note:* If the OFFSET channel is selected but the offset value is 0x0000, this offset programming is ignored. If the same OFFSET channel is programmed in different registers multiple times, the first programmed register takes priority.

Table 148 describes how the computation is performed for all the possible ADC resolutions and offset settings.

*Digest note:* The offset computation table is Table 143 (below). Table 148 is the analog watchdog comparison table.

**Table 143. Offset computation versus data resolution**

| Resolution (RES[1:0] bits) | Subtraction between raw converted data and offset: Raw converted Data, left aligned | Subtraction between raw converted data and offset: Offset | Result | Comments |
|---|---|---|---|---|
| 00: 12-bit | DATA[11:0] | OFFSET[11:0] | Signed or unsigned 24-bit data, right aligned to [11:0] | - |
| 01: 10-bit | DATA[11:2],00 | OFFSET[11:2] | Signed or unsigned 24-bit data, right aligned to [9:0] | The user must configure OFFSET[1:0] to 0b00. |
| 10: 8-bit | DATA[11:4],0000 | OFFSET[11:4] | Signed or unsigned 24 bit data right aligned to [7:0] | The user must configure OFFSET[3:0] to 0b0000. |
| 11: 6-bit | DATA[11:6],000000 | OFFSET[11:6] | Signed or unsigned 24 bit data right aligned to [5:0] | The user must configure OFFSET[5:0] to 0b000000. |

Figure 103, Figure 104, Figure 105 and Figure 106 show alignments for signed and unsigned data. JOVSS and JLSHIFT are not described here, but they behave the same as OVSS and LSHIFT.

**Figure 103. Right alignment (offset disabled, unsigned value)** (described in prose)

- 12-bit data: D11..D0 in bits 11:0; bits 31:12 are 0.
- 10-bit data: D9..D0 in bits 9:0; bits 31:10 are 0.
- 8-bit data: D7..D0 in bits 7:0; bits 31:8 are 0.
- 12-bit data, OVSR = 1024, OVSS = 0000: D21..D0 in bits 21:0; bits 31:22 are 0.
- 12-bit data, OVSR = 1024, OVSS = 1010: D11..D0 in bits 11:0; bits 31:12 are 0.

**Figure 104. Right alignment (offset enabled, signed value)** (described in prose)

- 12-bit data: D11..D0 in bits 11:0, SEXT (sign extension) in bits 31:12 ("Signed 32-bit or 16-bit format").
- 10-bit data: D9..D0 in bits 9:0, SEXT in bits 31:10.
- 8-bit data: D7..D0 in bits 7:0, SEXT in bits 31:8.
- 8-bit data with SSAT = 1: D6..D0 in bits 6:0, SEXT in bits 31:7 ("Signed 8-bit format").
- 12-bit data, OVSR = 1024, OVSS = 0000: D21..D0 in bits 21:0, SEXT in bits 31:22.

**Figure 105. Left alignment (offset disabled, unsigned value)** (described in prose)

- 12-bit data, LSHIFT = 4: D11..D0 in bits 15:4, bits 3:0 are 0, upper bits 0.
- 10-bit data, LSHIFT = 6: D9..D0 in bits 15:6, bits 5:0 are 0, upper bits 0.
- 8-bit data, LSHIFT = 0: D7..D0 in bits 7:0, upper bits 0.
- 12-bit data, OVSR = 1024, LSHIFT = 10: D21..D0 in bits 31:10, bits 9:0 are 0.

**Figure 106. Left alignment (offset enabled, signed value)** (described in prose)

- 12-bit data, LSHIFT = 3: D11..D0 in bits 14:3, bits 2:0 are 0, SEXT above ("Signed 16-bit format").
- 10-bit data, LSHIFT = 5: D9..D0 in bits 14:5, bits 4:0 are 0, SEXT above ("Signed 16-bit format").
- 8-bit data, LSHIFT = 7: D7..D0 in bits 14:7, bits 6:0 are 0, SEXT above ("Signed 16-bit format").
- 8-bit data, SSAT = 1: D6..D0 in bits 6:0, SEXT in bits 31:7 ("Signed 8-bit format").
- 12-bit data, OVSR = 1024, LSHIFT = 9: sign bit S in bit 31, D21..D0 in bits 30:9, bits 8:0 are 0 ("Signed 32-bit format").

#### Management of signed and unsigned saturation format (SSAT, USAT)

The offset correction might result in the data width to be wider than the original data.

To limit the original data width, the data saturation can be enabled through the SSAT and USAT bits of the ADC_OFCFGRy register.

Unsigned 12-bit data can be extended to 13-bit signed data by using an offset value different from 0x800.

The original data width can be preserved by setting SSAT bit to limit the data width to 12 bits.

Unsigned data can be saturated to the original data width by setting the USAT bit.

Table 144 shows the sign-extended data format corresponding to different resolutions.

**Table 144. 12-bit data formats**

| SSAT | USAT | Format | Data range (offset = 0x800) |
|---|---|---|---|
| 0 | 0 | Sign-extended 13-bit significant data: SEXT[31:13] DATA[12:0] | 0x0000 07FF - 0xFFFF F800 |
| 1 | 0 | Sign-extended 12-bit significant data: SEXT[31:12] DATA[11:0] | 0x7FF - 0x800 |
| 0 | 1 | Unsigned saturation 12-bit signification data: DATA[11:0] | 0xFFF - 0x000 |
| 1 | 1 | Reserved | - |

Table 145 provides numerical examples for four different offset values.

**Table 145. Numerical examples for 32-bit or 16-bit format (POSSPFF = 0)**

| Raw conversion result | Offset value | Result SSAT = 0 USAT = 0 | Result SSAT = 0 USAT = 1 | Result SSAT = 1 USAT = 0 |
|---|---|---|---|---|
| 0xFFF | 0x800 | 0x0000 07FF | 0x07FF | 0x07FF |
| 0x800 | 0x800 | 0x0000 0000 | 0x0000 | 0x0000 |
| 0x000 | 0x800 | 0xFFFF F800 | 0x0000 | 0xF800 |
| 0xFFF | 0x820 | 0x0000 07DF | 0x07DF | 0x07DF |
| 0x800 | 0x820 | 0xFFFF FFE0 | 0x0000 | 0xFFE0 |
| 0x000 | 0x820 | 0xFFFF F7E0 | 0x0000 | 0xF7E0 |
| 0xFFF | 0x7E0 | 0x0000 081F | 0x081F | 0x07FF |
| 0x800 | 0x7E0 | 0x0000 0020 | 0x0020 | 0x0020 |
| 0x000 | 0x7E0 | 0xFFFF F820 | 0x0000 | 0xF820 |
| 0xFFF | 0x020 | 0x0000 0FDF | 0x0FDF | 0x0FDF |
| 0x800 | 0x020 | 0x0000 07E0 | 0x07E0 | 0x07E0 |
| 0x000 | 0x020 | 0xFFFF FFE0 | 0x0000 | 0xFFE0 |

*Digest note:* "POSSPFF" in the caption is printed as-is. It presumably means POSOFF.

*Caution:* SSAT must not be used in conjunction with USAT. No hardware check is performed to ensure that this condition is respected.

#### Gain compensation

When the GCOMP bit is set in the ADC_GCOMP register, the gain compensation is activated on all the converted data. After each conversion, data is calculated using the following formula.

DATA = DATA(adc result) × (GCOMPCOEFF) / 4096

As GCOMPCOEFF can be programmed from 0 to 16383, the actual gain compensation factor can range from 0 to 3.999756.

Before storing the resulting data in RDATAx or JDATAx bitfields, the LSB - 1 value is evaluated to round up the data and minimize the error.

The gain compensation is also effective for the oversampling. When the gain compensation is used in oversampling mode, the gain calculation is performed after the accumulation and right-shift operations to minimize the power consumption (the gain calculation is done only once and not at each conversion).

The internal multiplier width is 32 bits and the input data width for the gain compensation must be less than 18 bits. When using oversampling with injected and regular conversion mode, the ROVSM bit of the ADC_CFGR2 register must be set to resume the pending conversion with the correct value.

When the gain compensation is activated, the ADC data latency is increased by one clock cycle. In continuous and scan conversion modes, the ADC conversion rate does not change.

#### ADC overrun (OVR, OVRMOD)

The overrun flag (OVR) issues a notification that the regular converted data has not been read (by the CPU or the DMA) before the ADC_DR FIFO (eight stages) is overflowed, or adc_hclk clock is too slow to manage the data. If the CPU clears the EOC flag without reading the data register, the OVR flag may still be triggered.

The OVR flag is set when a new conversion completes while ADC_DR as single register or FIFO output is full. An interrupt is generated if the OVRIE bit is set.

When an overrun condition occurs, the ADC is still operating and can continue converting unless the software decides to stop and reset the sequence by setting ADSTP. The OVR flag is cleared by software by programming it to 1.

Data can be configured to be preserved or overwritten when an overrun event occurs by programming the control bit OVRMOD:

- OVRMOD = 0

  The overrun event preserves the data register from being overwritten: the old data are maintained up to ADC_DR FIFO depth (eight data) and the new conversion is discarded and lost. If OVR remains at 1, further conversions occur but the result data is also discarded. The FIFO can be emptied through ADC_DR read access by the CPU while the OVR flag is set.

- OVRMOD = 1

  The data register is overwritten with the last conversion result and the previous unread data is lost. In this mode, ADC_DR FIFO is disabled. If OVR remains at 1, any further conversion is performed normally and the ADC_DR register always contains the latest converted data. In this mode, DMA burst mode cannot be supported.

*Digest note:* OVRMOD resets to 0 (FIFO enabled). Single-shot software polling that reads ADC_DR after each EOC never fills the FIFO.

**Figure 107. Example of overrun (OVRMOD = 0)** (described in prose)

1. Software sets ADSTART. A TRGx edge starts conversions CH1, CH2, CH3, CH4, ..., CH11, CH12, CH13.
2. ADC_DR is read after CH2 and after CH3. ADC_DR then shows D1, then D2, then D3.
3. Unread results accumulate in the eight-level FIFO (ADC_DR (FIFO_DATA) shows D4 ... D9, D10). When the FIFO is full at the end of CH11, OVR is set and that result is not stored ("na").
4. A later ADC_DR read pops D4 and frees a FIFO level, so CH12's result D12 is stored.
5. Software sets ADSTP during CH13. The ADC goes to STOP then RDY, ADSTART is cleared by hardware, and software clears OVR.

**Figure 108. Example of overrun (OVRMOD = 1)** (described in prose)

1. Software sets ADSTART. A TRGx edge starts continuous conversions CH1 to CH7, with EOC after each and EOS pulses.
2. ADC_DR is read after most conversions and shows D1, D2, D3, D4, D5, D6.
3. One result (CH5) completes while the previous EOC is still set without a read. OVR is set ("Overrun") and ADC_DR is overwritten with the newest data.
4. Software sets ADSTP during CH7. The ADC goes to STOP and then RDY, and ADSTART and OVR are cleared.

*Note:* Even if overrun may occur for injected channels, there is no overrun detection on these channels since there is a dedicated data register for each of the four injected channels.

#### Managing a sequence of conversions without using the DMA

If the conversions are slow enough, the conversion sequence can be handled by the software. In this case the software must use the EOC flag and its associated interrupt to handle each data. Each time a conversion is complete, EOC is set and the ADC_DR register can be read. OVRMOD must be configured to 0 to manage overrun events or FIFO overflow as errors.

#### Managing conversions without using the DMA and without overrun

It may be useful to let the ADC convert one or more channels without reading the data each time (if there is an analog watchdog for instance). In this case, the OVRMOD bit must be configured to 1 and the OVR flag must be ignored by the software. An overrun event does not prevent the ADC from continuing to convert and the ADC_DR register always contains the latest conversion.

#### Managing conversions using the DMA

When the DMA mode is enabled (DMNGT[1:0] = 01 or 11 in the ADC_CFGR1 register in single ADC mode), a DMA request is generated after each channel conversion. This allows the transfer of the converted data from the ADC_DR register to the destination location configured in the DMA.

Despite this, if an overrun occurs (OVR = 1) because the DMA cannot serve the DMA transfer request in time, the ADC stops generating DMA requests and the data corresponding to the new conversion is not transferred by the DMA, which means that all the data transferred to the RAM can be considered as valid. (OVRMOD = 0).

When OVRMOD = 1, even if DMA does not transfer the data immediately, new data overwrite ADC_DR, causing DMA to potentially skip data. As a result, some conversion results may be missed in the data transferred to RAM.

Depending on the configuration of the OVRMOD bit, the data are either preserved or overwritten (refer to Section : ADC overrun (OVR, OVRMOD)). If OVRMOD = 0 (data preserved), DMA transfer requests are blocked.

DMA can be configured through the DMNGT[1:0] bitfield of the ADC_CFGR1 register. Refer to Section 21.4.29: Dual ADC modes for information on DMA usage with dual ADC mode.

- DMA one-shot mode (DMNGT[1:0] = 01)

  This mode is suitable when the DMA is programmed to transfer a fixed number of data.

- DMA circular mode (DMNGT[1:0] = 11)

  This mode is suitable when programming the DMA when the number of transfers is unknown.

#### DMA one-shot mode (DMNGT[1:0] = 01)

In one-shot mode, the ADC generates a DMA transfer request each time a new conversion data is available and stops generating DMA requests once the DMA has reached the last DMA transfer (that is when DMA_LACK interrupt occurs, see Direct-memory controller section) even if a new conversion has been started.

When DMA transfers are complete (all the transfers configured in the DMA controller have been done):

- The content of the ADC data register is frozen.
- All ongoing conversions are aborted with the partial result discarded.
- The scan sequence is stopped and reset.
- The DMA and ADC are stopped.

#### DMA circular mode (DMNGT[1:0] = 11)

In circular mode, the ADC generates a DMA transfer request each time a new conversion data is available in the data register. This allows the configuration of the DMA in circular mode to handle a continuous analog input data stream.

#### DMA single-transfer or burst mode with FIFO (OVRMOD = 0)

The output data register features an eight-stage FIFO. Two different DMA requests are generated in parallel. When a data is available, an "SREQ single request" is generated. When four data are available, a "BREQ burst request" is generated. The DMA can be programmed either in single-transfer mode or in burst mode (four beats). The appropriate request line is selected by the DMA according to the mode selected. Refer to Section Direct memory access controller for further information.

Due to the existence of FIFO, DMA requests are generated until the FIFO is emptied. To stop DMA requests even when the FIFO is not emptied, set the ADSTP bit.

#### DMA for dual mode

Refer to Section 21.4.29: Dual ADC modes.

### 21.4.26 Dynamic low-power features

#### Autodelayed conversion mode (AUTDLY)

The ADC implements an autodelayed conversion mode controlled by the AUTDLY configuration bit in ADC_CFGR1. Autodelayed conversions are useful to simplify the software as well as to optimize performance of an application clocked at low frequency where there must be risk of encountering an ADC overrun.

#### Regular conversion mode

When AUTDLY is set, a new conversion can start if the following conditions are met:

- The ADC_DR register is read or the EOC bit is cleared (see Figure 109).

This is a way to automatically adapt the speed of the ADC to the speed of the system that reads the data and prevent overrun errors.

The delay is inserted after each regular conversion.

#### Injected conversion mode

When AUTDLY is set, a new conversion can start only if the JEOS bit has been cleared (see Figure 110). Since there are four ADC_JDRy registers, the autodelay is performed at the end on the injected conversion sequence.

There is no delay inserted between each conversion of the injected sequence, except after the last one.

A hardware trigger event occurring during this delay is ignored.

No delay is inserted between regular and injected conversions. The autodelay for regular and injected modes is managed separately.

*Caution:* The behavior is slightly different in autoinjection mode (JAUTO = 1) where a new regular conversion can start only when the automatic delay of the previous injected sequence of conversion has ended (when JEOS has been cleared). This is to ensure that the software can read all the data of a given sequence before starting a new sequence (see Figure 113).

In autoinjection mode, there is no delay between the last regular conversion and the first injected conversion. The user must clear the last EOC flag before clearing the JEOS flag, otherwise the next sequence might start before EOC flag is cleared.

In autodelay mode, a hardware regular trigger event is ignored if it occurs during an already ongoing regular sequence or during the delay that follows the last regular conversion of the sequence. It is however considered pending if it occurs after this delay, even if it occurs during an injected sequence of the delay that follows it. The conversion then starts at the end of the delay of the injected sequence.

In autodelay mode with JAUTO = 0, a hardware injected trigger event is ignored if it occurs during an already ongoing injected sequence or during the delay that follows the last injected conversion of the sequence.

*Note:* AUTDLY mode is not supported with SMPTRIG or BULB mode.

**Figure 109. AUTDLY = 1, regular conversion in continuous mode, software trigger** (described in prose)

1. Software sets ADSTART. The ADC converts CH1 and then waits in a delay state (DLY) until ADC_DR is read. It then converts CH2, then DLY, then CH3, then DLY, then CH1, then DLY.
2. EOC is set at the end of each conversion and cleared by the ADC_DR read. EOS is set after CH3. ADC_DR shows D1, D2, D3, D1.
3. Software sets ADSTP. The ADC goes to STOP and then RDY.

Notes:

1. AUTDLY = 1, JAUTO = 0.
2. Regular configuration: EXTEN[1:0] = 00 (software trigger), CONT = 1, CHANNELS = 1, 2, 3.
3. Injected configuration DISABLED.

**Figure 110. AUTDLY = 1, regular hardware conversions interrupted by injected conversions (DISCEN = 0; JDISCEN = 0)** (described in prose)

1. A regular trigger starts CH1 (regular). DLY (CH1) lasts until ADC_DR is read, then CH2 (regular) runs, then DLY (CH2).
2. A regular trigger during the ongoing regular sequence or delay is ignored.
3. An injected trigger starts CH5 and CH6 (injected). A regular trigger that occurs during this injected sequence is "Not ignored".
4. CH3 (regular) follows the injected sequence. DLY (inj) lasts until JEOS is cleared, and an injected trigger during this delay is ignored.
5. The next regular sequence then starts with CH1.
6. ADC_JDR1 = D5 and ADC_JDR2 = D6. ADC_DR shows D1, D2, D3, D1.

Notes:

1. AUTDLY = 1, JAUTO = 0.
2. Regular configuration: EXTEN[1:0] = 01 (hardware trigger), CONT = 0, DISCEN = 0, CHANNELS = 1, 2, 3.
3. Injected configuration: JEXTEN[1:0] = 01 (hardware trigger), JDISCEN = 0, CHANNELS = 5, 6.

**Figure 111. AUTDLY = 1, regular hardware conversions interrupted by injected conversions (DISCEN = 1, JDISCEN = 1)** (described in prose)

1. Each regular trigger converts one regular channel (CH1, then CH2), each followed by DLY until ADC_DR is read, then RDY.
2. Each injected trigger converts one injected channel (CH5, then CH6). Injected triggers during an ongoing injected conversion or its delay are ignored.
3. A regular trigger that occurs during the injected sequence is not ignored, and CH3 (regular) runs after CH6.
4. ADC_JDR1 = D5 and ADC_JDR2 = D6.

Notes:

1. AUTDLY = 1, JAUTO = 0.
2. Regular configuration: EXTEN[1:0] = 01 (hardware trigger), CONT = 0, DISCEN = 1, DISCNUM = 1, CHANNELS = 1, 2, 3.
3. Injected configuration: JEXTEN[1:0] = 01 (hardware trigger), JDISCEN = 1, CHANNELS = 5, 6.

**Figure 112. AUTDLY = 1, regular continuous conversions interrupted by injected conversions** (described in prose)

1. Software sets ADSTART. CH1 (regular) runs, then DLY (CH1), then CH2 (regular), then DLY (CH2).
2. An injected trigger converts CH5 and CH6 (injected), followed by DLY (inj) until JEOS is cleared. A further injected trigger during that delay is ignored.
3. CH3 (regular) runs, then DLY (CH3), then CH1 (regular).
4. ADC_DR shows D1, D2, D3. ADC_JDR1 = D5 and ADC_JDR2 = D6.

Notes:

1. AUTDLY = 1, JAUTO = 0.
2. Regular configuration: EXTEN[1:0] = 00 (software trigger), CONT = 1, DISCEN = 0, CHANNELS = 1, 2, 3.
3. Injected configuration: JEXTEN[1:0] = 01 (hardware trigger), JDISCEN = 0, CHANNELS = 5, 6.

**Figure 113. AUTDLY = 1 in autoinjection mode (JAUTO = 1)** (described in prose)

1. Software sets ADSTART. CH1 (regular) runs, then DLY (CH1), then CH2 (regular).
2. CH5 and CH6 (injected) follow with "No delay" between CH2 and CH5. Then DLY (inj) lasts until JEOS is cleared.
3. CH3 (regular) runs, then DLY, then CH1 (regular).
4. ADC_DR shows D1, D2, D3. ADC_JDR1 = D5 and ADC_JDR2 = D6.

Notes:

1. AUTDLY = 1.
2. Regular configuration: EXTEN[1:0] = 00 (software trigger), CONT = 1, DISCEN = 0, CHANNELS = 1, 2.
3. Injected configuration: JAUTO = 1, CHANNELS = 5, 6.

### 21.4.27 Analog window watchdog (AWD1EN, JAWD1EN, AWD1SGL, AWD1CH, AWDCH of ADC_AWD2CR and ADC_AWD3CR, HTR, LTR, AWDFILT)

**Table 146. Analog window watchdog features**

| Feature | AWD1 | AWD2 | AWD3 |
|---|---|---|---|
| Enable control | AWD1EN or JAWD1EN | ADC_AWD2CR | ADC_AWD3CR |
| Channel selection | AWD1CH[4:0]/AWD1SGL | ADC_AWD2CR | ADC_AWD3CR |
| Channel selection limitation | One or all channels; Regular or injected | Any number of channels; - | Any number of channels; - |
| Threshold control | ADC_AWD1LTR / ADC_AWD1HTR | ADC_AWD2LTR / ADC_AWD2HTR | ADC_AWD3LTR / ADC_AWD3HTR |
| Filter configuration | AWDFILT[2:0] in ADC_AWDyHTR | AWDFILT[2:0] in ADC_AWDyHTR | AWDFILT[2:0] in ADC_AWDyHTR |
| Interrupt | AWDy in ADC_ISR | AWDy in ADC_ISR | AWDy in ADC_ISR |

*Digest note:* In the source, "Any number of channels" spans the AWD2 and AWD3 columns. "Filter configuration" and "Interrupt" each span all three columns. Section 21.6 defines AWDFILT[2:0] only in ADC_AWD1HTR, and the filter text below refers only to watchdog 1.

The three AWD analog watchdogs monitor whether some channels remain within a configured voltage range (window).

**Figure 114. Analog watchdog guarded area** (described in prose)

The analog voltage axis shows a guarded area between the lower threshold (LTR) and the higher threshold (HTR).

#### AWDy flag and interrupt

An interrupt can be enabled for each of the three analog watchdogs by setting AWDyIE in the ADC_IER register (y = 1, 2, 3).

AWDy (y = 1, 2, 3) flag is cleared by software by writing 1 to it, or by setting ADDIS.

The ADC conversion result is compared to the lower and higher thresholds before alignment.

#### Description of analog watchdog 1

The AWD analog watchdog 1 is enabled by setting the AWD1EN or JAWD1EN bit in the ADC_CFGR1 register. This watchdog monitors whether either one selected channel or all enabled channels remain within a configured voltage range (window).

Table 147 shows how the ADC_CFGR1 registers must be configured to enable the analog watchdog on one or more channels.

**Table 147. Analog watchdog 1 channel selection**

| Channels guarded by the analog watchdog | AWD1SGL bit | AWD1EN bit | JAWD1EN bit |
|---|---|---|---|
| None | x | 0 | 0 |
| All injected channels | 0 | 0 | 1 |
| All regular channels | 0 | 1 | 0 |
| All regular and injected channels | 0 | 1 | 1 |
| Single(1) injected channel | 1 | 0 | 1 |
| Single(1) regular channel | 1 | 1 | 0 |
| Single(1) regular or injected channel | 1 | 1 | 1 |

Notes:

1. Selected by the AWD1CH[4:0] bits. The channels must also be programmed to be converted in the appropriate regular or injected sequence.

The AWD1 analog watchdog flag is set if the analog voltage converted by the ADC is below a lower threshold or above a higher threshold.

These thresholds are programmed through HTR[22:0] bits of the ADC_AWD1HTR register and LTR[22:0] bits of the ADC_AWD1LTR register for the analog watchdog 1.

The threshold can be up to 23 bits (12-bit resolution with oversampling, OVSR = 1024, offset and gain compensation)

When converting data with a resolution of less than 12 bits (defined by RES[1:0] bits), the LSB of the programmed thresholds must be kept cleared because the internal comparison is always performed on the full 12-bit raw converted data.

Table 148 describes how the comparison is performed for all the possible resolutions and for analog watchdog 1.

**Table 148. Analog watchdog 1, 2, 3 comparison**

| Resolution (RES[1:0] bits) | Analog watchdog comparison between: Raw converted data, left aligned(1) | Analog watchdog comparison between: Thresholds | Comments |
|---|---|---|---|
| 00: 12-bit | DATA[11:0] | LTR[22:0] and HTR[22:0] | - |
| 01: 10-bit | DATA[11:2],00 | LTR[22:0] and HTR[22:0] | The user must configure LTR[1:0] to 0b00 and HTR[1:0] to 0b00. |
| 10: 8-bit | DATA[11:4],0000 | LTR[22:0] and HTR[22:0] | The user must configure LTR[3:0] to 0b0000 and HTR[3:0] to 0b0000. |
| 11: 6-bit | DATA[11:6],000000 | LTR[22:0] and HTR[22:0] | The user must configure LTR[5:0] to 0b000000 and HTR[5:0] to 0b000000. |

Notes:

1. Refer to Section : Gain compensation for additional details on analog watchdog comparison.

#### Description of analog watchdog 2 and 3

The second and third analog watchdogs are more flexible and can guard several selected channels by programming the corresponding bits in AWDCH[13:0] (of ADC_AWD2CR and ADC_AWD3CR).

The corresponding watchdog is enabled when any bit of AWDCH[13:0] (of ADC_AWD2CR and ADC_AWD3CR) is set.

The threshold can be up to 23 bits (12-bit resolution with oversampling, OVSR = 1024 and offset compensation in signed format with gain compensation) and is programmed through the ADC_AWD2HTR, ADC_AWD2LTR, ADC_AWD3HTR and ADC_AWD3LTR registers.

When converting data with a resolution of less than 12 bits (defined by RES[1:0]) bits), the LSBs of the programmed threshold must be kept cleared, the internal comparison being performed on the full 12-bits converted data (left aligned).

#### ADCx_AWDy_OUT signal output generation

Each analog watchdog is associated with an internal hardware signal ADC_AWDy_OUT (y being the watchdog number), which is directly connected to the ETR input (external trigger) of some of the on-chip timers. Refer to the on-chip timers sections to understand how to select the ADC_AWDy_OUT signal as ETR.

ADC_AWDy_OUT is activated when the associated analog watchdog is enabled:

- ADC_AWDy_OUT is set when a guarded conversion is outside the programmed thresholds.
- ADC_AWDy_OUT is reset after the end of the next guarded conversion that is inside the programmed thresholds (It remains at 1 if the next guarded conversions are still outside the programmed thresholds).
- ADC_AWDy_OUT is also reset when disabling the ADC (when setting ADDIS). Note that stopping regular or injected conversions (by setting ADSTP or JADSTP) has no influence on the generation of ADCx_AWDy_OUT.

*Note:* The AWDy flag is set by hardware and reset by software: the AWDy flag has no influence on the generation of ADC_AWDy_OUT (ex: ADC_AWDy_OUT can toggle while the AWDy flag remains at 1 if the software did not clear the flag).

The AWDy flag is cleared by programming it to 1 or by set ADDIS bit. ADSTP and JADSTP bits do not reset the AWDy flag.

**Figure 115. ADC_AWDy_OUT signal generation (on all regular channels)** (described in prose)

Regular channels 1 to 7 are all converted and all guarded. Conversions 1 to 7 are, in order: inside, outside, inside, outside, outside, outside, inside. EOC pulses after each conversion. The AWDy flag is set after each outside conversion and cleared by software each time. ADC_AWDy_OUT rises after conversion 2 (outside) and falls after conversion 3 (inside). It rises again after conversion 4 and stays high through conversions 5 and 6. It falls after conversion 7 (inside).

**Figure 116. ADC_AWDy_OUT signal generation (AWDy flag not cleared by software)** (described in prose)

The sequence is the same as Figure 115, but the AWDy flag is set at the first outside conversion and is not cleared by software. ADC_AWDy_OUT still toggles as in Figure 115.

**Figure 117. ADC_AWDy_OUT signal generation (on a single regular channel)** (described in prose)

Regular channels 1 and 2 are converted alternately, and only channel 1 is guarded. The channel 1 conversion results are, in order: outside, inside, outside, outside. EOC follows each conversion and EOS each pair. AWDy is set for the outside channel 1 results and cleared by software. ADC_AWDy_OUT goes high after the first channel 1 conversion (outside), low after the second (inside), and high again after the third (outside). It stays high after the fourth (outside). Channel 2 conversions do not affect it.

**Figure 118. ADC_AWDy_OUT signal generation (on all injected channels)** (described in prose)

Injected channels 1, 2, 3 and 4 are converted and all guarded. Conversions are, in order: inside, outside, inside, outside, outside, outside, inside. JEOS pulses at sequence ends. AWDy is set after outside conversions and cleared by software. ADC_AWDy_OUT follows the same set/reset rule as for regular channels.

#### Analog watchdog threshold control on the fly

LTR[22:0] and HTR[22:0] can be changed when an analog-to-digital conversion is ongoing (that is between the start of conversion and the end of conversion of the ADC internal state). If LTR[22:0] and HTR[22:0] are updated during the ADC conversion of the ADC guarded channel, resulting in analog watchdog thresholds to be applied from the next ADC conversion. The analog watchdog comparison is performed at each end of conversion. If the current ADC data is out of the new modified threshold, no interrupt and AWDy_OUT signal are issued. The Interrupt and the AWD generation only happen at the end of the conversion that started after the threshold update. If AWDy_OUT is already asserted, programming the new thresholds does not deassert the AWDy_OUT signal. However, the watchdog threshold must not be changed twice during the four adc_ker_ck periods.

#### Analog watchdog filter for watchdog 1

With analog watchdog, a valid ADC conversion data range can be configured through the ADC_AWD1LTR and ADC_AWD1HTR registers. When the conversion results have consecutively passed the threshold for more than the watchdog filter value (AWDFILT[2:0] + 1), AWD1_OUT is generated as well as the AWD1 flag. Before this value is reached, AWD1 output is not activated.

#### Analog watchdog with gain and offset compensation

When the gain and offset compensation are enabled, the analog watchdog compares the data after the compensation.

### 21.4.28 Oversampler

The oversampling unit performs data preprocessing to offload the device. It is able to handle multiple conversions and average them into a single data with increased data width, up to 22 bits.

It provides a result with the following form, where N and M can be adjusted:

Result = (1 / M) × Σ (n = 0 to N–1) Conversion(tn)

It enables the following functions to be performed by hardware: averaging, data rate reduction, SNR improvement and basic filtering.

The oversampling ratio N is defined by the OVSR[9:0] bits in the ADC_CFGR2 register, or by the JOVSS[3:0] bits in the ADC_CFGR3 register for parallel injected oversampling mode. They can range from 2x to 1024x. The division coefficient M consists of a right bit shift up to 10 bits. It is defined through the OVSS[3:0] bits of the ADC_CFGR2 register.

*Digest note:* No ADC_CFGR3 register is documented in this chapter (Section 21.6, Table 153), and the ST CMSIS header stm32c552xx.h defines none. [unclear in source: JOVSS[3:0] in ADC_CFGR3 as the source of N for parallel injected oversampling]

The summation unit can yield a result up to 22 bits, which can be left or right shifted at the end. When the right shift is selected, it is rounded to the nearest value using the least significant bits left apart by the shifting, before being finally transferred to the ADC_DR data register.

Figure 119 gives a numerical example of the processing, from a raw 22-bit accumulated data to the final 12-bit result.

**Figure 119. 12-bit result oversampling with 10-bit right shift and rounding** (described in prose)

With OVSR = 1024 and OVSS[3:0] = 0, the 22-bit accumulated data D21..D0 sits in bits 21:0. Right shifting and rounding with OVSS[3:0] = 1010 gives a 12-bit result D11..D0 in bits 11:0. Numerical example: the 22-bit accumulated value 0x3FE258 (OVSS = 0) becomes 0x0FF9 after right shifting and rounding with OVSS = 1010.

Table 107 gives data format for the various N and M combinations, for a raw conversion data equal to 0xFFF.

*Digest note:* The source text says "Table 107". The table that follows is Table 149.

**Table 149. Maximum output results versus N and M**

| Oversampling ratio | Max Raw data | No-shift OVSS = 0000 | 1-bit shift OVSS = 0001 | 2-bit shift OVSS = 0010 | 3-bit shift OVSS = 0011 | 4-bit shift OVSS = 0100 | 5-bit shift OVSS = 0101 | 6-bit shift OVSS = 0110 | 7-bit shift OVSS = 0111 | 8-bit shift OVSS = 1000 |
|---|---|---|---|---|---|---|---|---|---|---|
| x2 | 0x1FFE | 0x1FFE | 0x0FFF | 0x0800 | 0x0400 | 0x0200 | 0x0100 | 0x0080 | 0x0040 | 0x0020 |
| x4 | 0x3FFC | 0x3FFC | x1FFE | 0x0FFF | 0x0800 | 0x0400 | 0x0200 | 0x0100 | 0x0080 | 0x0040 |
| x16 | 0xFFF0 | 0xFFF0 | 0x7FF8 | 0x3FFC | 0x1FFE | 0x0FFF | 0x0800 | 0x0400 | 0x0200 | 0x0100 |
| x64 | 0x3FFC0 | 0x3FFC0 | 0x1FFE0 | 0xFFF0 | 0x7FF8 | 0x3FFC | 0x1FFE | 0x0FFF | 0x0800 | 0x0400 |
| x256 | 0xFFF00 | 0xFFF00 | 0x7FF80 | 0x3FFC0 | 0x1FFE0 | 0xFFF0 | 0x7FF8 | 0x3FFC | 0x1FFE | 0x0FFF |
| x1024 | 0x3FFC00 | 0x3FFC00 | 0x1FFE00 | 0xFFF00 | 0x7FF80 | 0x3FFC0 | 0x1FFE0 | 0xFFF0 | 0x7FF8 | 0x3FFC |

*Digest note:* "x1FFE" (x4, 1-bit shift) is printed as-is and presumably means 0x1FFE.

The conversion timing rate does not change in oversampling mode: the sample time is maintained equal during the whole oversampling sequence. A new data is provided every N conversion, with an equivalent delay equal to N x TCONV = N x (tSMPL + tSAR). The flags are set as follows:

- The end of the sampling phase (EOSMP) is set after each sampling phase for regular conversion.
- The end of conversion (EOC) occurs once every N conversion, when the oversampled result is available.
- The end of sequence (EOS) occurs once the sequence of oversampled data is completed (that is after a total of N x sequence length conversions).

Unlike the conversion rate, the data latency changes in oversampling mode: each single conversion introduces an additional accumulation. As a result, an additional clock cycle is required when all the conversions are complete, after the accumulation and shift.

The EOC flag is set two additional clock cycles after the conversion is complete.

#### ADC operating modes supported in oversampling mode (single ADC mode)

In oversampling mode, most of the ADC operating modes are maintained:

- Single, discontinuous, or continuous conversion modes
- ADC conversions started either by software or triggers
- ADC stop during a conversion (abort)
- Data read via CPU or DMA with overrun detection
- Low-power modes (AUTDLY)
- Programmable resolution: in this case, the reduced conversion values (as per RES[1:0] bits of the ADC_CFGR1 register) are accumulated, truncated, rounded, and shifted in the same way as 12-bit conversions are.
- Autoinjected mode (JAUTO) if JOVSPAR = 0 and oversampling ratio is the same for both regular and injected channels.

#### Analog watchdog

The analog watchdog functionality is maintained, with the following differences:

- The RES[1:0] bits are ignored and the comparison is always done using the full 23-bit values HTR[22:0] and LTR[22:0].
- The comparison is performed on the oversampled accumulated value before shifting.

#### Triggered mode

The oversampling can also be used for basic filtering purpose. Although it not a very powerful filter (slow roll-off and limited stop band attenuation), it can act as a notch filter to reject constant parasitic frequencies (typically coming from the mains or from a switched-mode power supply). For this purpose, a specific discontinuous mode can be enabled through the TROVS bit in ADC_CFGR2, to be able to achieve an oversampling frequency defined by the user and independent from the conversion time itself. The TROVS bit is supported with hardware trigger mode.

Figure 120 shows how conversions are started in response to triggers during discontinuous mode.

If the TROVS bit is set and OVSR ≠ 0, the content of the DISCEN bit is ignored and considered as 1.

If the TROVS bit is set, neither software trigger nor JAUTO is supported.

**Figure 120. Triggered regular oversampling mode (TROVS bit = 1)** (described in prose)

- **CONT = 0, DISCEN = 1, TROVS = 0.** One trigger converts Ch(N)0, Ch(N)1, Ch(N)2 and Ch(N)3 back-to-back, and the EOC flag is set after Ch(N)3. The next trigger repeats the burst.
- **CONT = 0, DISCEN = 1, TROVS = 1.** Each trigger converts only one oversampling step (Ch(N)0, then Ch(N)1, Ch(N)2, Ch(N)3, one per trigger). The EOC flag is set after the fourth step.

#### Injected and regular sequencer management in oversampling mode

In oversampling mode, injected and regular sequencers can have different behaviors. The oversampling can be enabled for both sequencers with some limitations if they have to be used simultaneously (this is related to a unique accumulation unit).

#### Oversampling regular channels only

The regular oversampling mode ROVSM bit defines how the regular oversampling sequence is resumed if it is interrupted by an injected conversion:

- In continuous mode (ROVSM = 0), the accumulation restarts from the last valid data (prior to the conversion abort request due to the injected trigger). This ensures that oversampling is complete whatever the injection frequency (providing at least one regular conversion can be complete between triggers);
- In resumed mode (ROVSM = 1), the accumulation restarts from 0 (previous conversion results are ignored). This mode guarantees that all the data used for oversampling were converted back-to-back within a single time slot. Care must be taken to have a injection trigger period above the oversampling period length. If this condition is not respected, the oversampling cannot be complete and the regular sequence is blocked.

Figure 121 gives examples for a 4x oversampling ratio.

**Figure 121. Regular oversampling modes (4x ratio)** (described in prose)

- **Continued mode (ROVSE = 1, JOVSE = 0, ROVSM = 0, TROVS = 0).**
  1. The regular channels Ch(N)0 to Ch(N)3 complete, then Ch(M)0 and Ch(M)1 run.
  2. An injected trigger aborts the conversion in progress ("Oversampling stopped"). Injected channels Ch(J) and Ch(K) are converted, followed by JEOC.
  3. Regular oversampling then continues with Ch(M)1, Ch(M)2, Ch(M)3 ("Oversampling continued"), followed by Ch(O)0.
- **Resumed mode (ROVSE = 1, JOVSE = 0, ROVSM = 1, TROVS = 0).** The same injection aborts the regular oversampling ("Oversampling aborted"). After Ch(J), Ch(K) and JEOC, it restarts from Ch(M)0 through Ch(M)3 ("Oversampling resumed").

#### Oversampling injected channels only

The injected oversampling mode bit JOVSE enables oversampling solely for conversions in the injected sequencer.

#### Oversampling regular and injected channels

It is possible to have both ROVSE and JOVSE bits set. In this case, the regular oversampling must be resumed (ROVSM bit = 1), as shown in Figure 122. This limitation no longer applies in parallel injected oversampling mode.

**Figure 122. Regular and injected oversampling modes used simultaneously** (described in prose)

ROVSE = 1, JOVSE = 1, ROVSM = 1, TROVS = 0.

1. Regular channels Ch(N)0 to Ch(N)3 complete, then Ch(M)0 and Ch(M)1 run.
2. An injected trigger aborts the regular oversampling ("Oversampling aborted").
3. The injected channels are oversampled as Ch(J)0, Ch(J)1, Ch(J)2, Ch(J)3, followed by JEOC.
4. Regular oversampling restarts from Ch(M)0 ("Oversampling resumed").

#### Triggered regular oversampling with injected conversions

It is possible to have triggered regular mode with injected conversions. In this case, the injected oversampling mode must be disabled and the ROVSM bit set (the resumed mode is forced). The JOVSE bit must be reset. The behavior is shown in Figure 123.

**Figure 123. Triggered regular oversampling with injection** (described in prose)

ROVSE = 1, JOVSE = 0, ROVSM = 1, TROVS = 1.

1. Each trigger converts one regular step: Ch(N)0, then Ch(N)1, then Ch(N)2.
2. An injected trigger aborts Ch(N)2, and the injected channels Ch(J) and Ch(K) are converted.
3. At the next trigger, the regular oversampling is resumed from Ch(N)0 ("Oversampling resumed"), followed by Ch(N)1.

#### Autoinjection mode

It is possible to oversample autoinjected sequences and store all conversion results in registers. This mode is available only with both regular and injected oversampling active: JAUTO = 1, ROVSE = 1 and JOVSE = 1. Other combinations are not supported. The ROVSM bit is ignored in autoinjection mode. Figure 124 shows how the conversions are sequenced.

**Figure 124. Oversampling in autoinjection mode** (described in prose)

JAUTO = 1, ROVSE = 1, JOVSE = 1, ROVSM = X, TROVS = 0.

1. The regular channel is oversampled as N0, N1, N2, N3.
2. Then the injected channels are each oversampled in turn: I0 to I3, J0 to J3, K0 to K3, L0 to L3.
3. Then the regular oversampling N0 to N3 repeats.

#### Combined modes summary

Table 150 summarizes all combinations, including the modes that are not supported.

**Table 150. Oversampler operating mode summary**

| Regular oversampling ROVSE | Injected oversampling JOVSE | Oversampler mode ROVSM (0 = continued, 1 = resumed) | Triggered regular mode TROVS | Comment |
|---|---|---|---|---|
| 1 | 0 | 0 | 0 | Regular continued mode |
| 1 | 0 | 0 | 1 | Not supported |
| 1 | 0 | 1 | 0 | Regular resumed mode |
| 1 | 0 | 1 | 1 | Triggered regular resumed mode |
| 1 | 1 | 0 | X | Not supported |
| 1 | 1 | 1 | 0 | Injected and regular resumed mode |
| 1 | 1 | 1 | 1 | Not supported |
| 0 | 1 | X | X | Injected oversampling |

*Digest note:* The ADC_CFGR2 register description (Section 21.6.5) shows bits 4:1 as reserved and has no JOVSE field. The ST CMSIS header stm32c552xx.h defines ADC_CFGR2_JOVSE at bit 1 ("ADC oversampler enable on scope ADC group injected"). JOVSPAR, JOVSIVE, TJOVS, JOVSR[9:0], JOVSECT and JOVSISE are mentioned in this chapter but documented in no register description.

### 21.4.29 Dual ADC modes

Dual ADC modes can be used in devices with two ADCs or more (see Figure 125).

In dual ADC mode the start of conversion is triggered alternately or simultaneously by the ADC master to the ADC slave, depending on the mode selected by the bits DUAL[4:0] in the ADCC_CCR register.

Four possible modes are implemented:

- Injected simultaneous mode
- Regular simultaneous mode
- Interleaved mode
- Alternate trigger mode

It is also possible to use these modes combined in the following ways:

- Injected simultaneous mode + regular simultaneous mode
- Regular simultaneous mode + alternate trigger mode
- Injected simultaneous mode + interleaved mode

In dual ADC mode (when the DUAL[4:0] bits in the ADCC_CCR register are not equal to zero), the following bits are shared between the master and slave ADCs, with the slave ADC bits being ignored and always applying to the corresponding bits of the master ADC:

- ADC_CFGR1 register: DMNGT[2:0], RES[1:0], EXTEN[1:0], OVRMOD, AUTDLY, DISCEN, DISCNUM[2:0], JDISCEN, JAUTO, JDISCEN.
- ADC_CFGR2 register: ROVSE, JOVSE, TROVS, ROVSM, BULB, SWTRIG, SMPTRIG, OVSR[9:0].
- ADC_GCOMP register: GCOMP.
- ADC_CR register: ADSTART, ADSTP, JADSTART, JADSTP.
- ADC_CFGR1 register: CONT, DISCEN, DISCNUM[2:0].
- ADC_SQR1 register: LEN (for the regular conversion).
- ADC_JSQR register: JLEN[1:0], JEXTSEL[4:0], JEXTEN[1:0] (for the injected conversion).
- ADC_CFGR3 register: JOVSPAR, JOVSE, JOVSIVE, TJOVS, JOVSR[9:0] (for the injected conversion).

*Digest note:* DMNGT is printed as DMNGT[2:0] here. The ADC_CFGR1 field is DMNGT[1:0].

For dual mode usage, the sampling time of the master and slave channels must be equal.

To start a conversion in dual mode, the user must program the EXTEN[1:0], EXTSEL, JEXTEN[1:0] and JEXTSEL bits of the master ADC only to configure a software or hardware trigger and a regular or injected trigger. The EXTEN[1:0], JEXTEN[1:0], and JEXTSEL bits of the slave ADC are don't care).

In regular simultaneous or interleaved modes, once the user sets the ADSTART or ADSTP bit of the master ADC, the corresponding bit of the slave ADC is automatically set. However, ADSTART or ADSTP bit of the slave ADC is not necessarily cleared at the same time as the master ADC bit.

In injected simultaneous or alternate trigger modes, once the user sets the JADSTART or JADSTP bit of the master ADC, the corresponding bit of the slave ADC is automatically set. However, JADSTART or JADSTP bit of the slave ADC is not necessarily cleared at the same time as the master ADC bit.

In dual ADC mode, the converted data of the master and slave ADC can be read in parallel, by reading the ADC common data register (ADCC_CDR). The flags can also be read in parallel by reading the dual-mode status register (ADCC_CSR).

*Note:* In dual mode, BULB, JAUTO, SMPTRIG are not supported.

**Figure 125. Dual ADC block diagram** (described in prose)

The GPIO ports carry ADCx_IN0, ADCx_IN2, ... ADCx_INi to input multiplexers on both the slave ADC and the master ADC. Each multiplexer also receives "Internal analog inputs".

Each ADC has:

- "Regular channels" and "Injected channels" blocks;
- a "Regular data register (32-bits)";
- "Injected data registers (4 x32-bits)".

All data registers connect to the address/data bus.

The master ADC contains:

- a "Start trigger mux. (regular group)";
- a "Start trigger mux. (injected group)";
- a "Dual mode control" block, which gates the triggers to the master's channels and, through "Internal triggers", to the slave's regular and injected channels.

Notes:

1. External triggers also exist on slave ADC but are not shown for the purposes of this diagram.
2. The ADC common data register (ADCC_CDR) contains both the master and slave ADC regular converted data.

#### Injected simultaneous mode with independent regular conversion

The injected simultaneous mode is selected by programming DUAL[4:0] bits to 0b00101.

This mode converts an injected group of channels. The external trigger source comes from the injected group multiplexer of the master ADC (selected by the JEXTSEL bits in the ADC_JSQR register).

*Note:* Do not convert the same channel on the two ADCs (no overlapping sampling times for the two ADCs when converting the same channel).

In simultaneous mode, the user software must convert sequences with the same length. Sampling times for channels with the same sequence number must be equal.

Regular conversions can be performed on one or all ADCs. In that case, they are independent of each other and are interrupted when an injected event occurs. They are resumed at the end of the injected conversion group.

The software is notified by interrupts when it can read the data:

- At the end of injected sequence of conversion event (JEOS) on the master ADC, the converted data is stored into the master ADC_JDRy registers and a JEOS interrupt is generated (if enabled)
- At the end of injected sequence of conversion event (JEOS) on the slave ADC, the converted data is stored into the slave ADC_JDRy registers and a JEOS interrupt is generated (if enabled)
- If the duration of the master-injected sequence is equal to the duration of the slave injected one (as shown in Figure 126), the software can enable only one of the two JEOS interrupts (for example the master JEOS) and read both converted data (from master ADC_JDRy and slave ADC_JDRy registers).

**Figure 126. Injected simultaneous mode on four channels: Dual ADC mode** (described in prose)

On a trigger, the master ADC converts CH1, CH2, CH3, CH4 while the slave ADC simultaneously converts CH15, CH14, CH13, CH12. Each conversion has a sampling phase followed by a conversion phase. The end of the injected sequence occurs on the master and slave ADC at the same time.

If JDISCEN is set, each simultaneous conversion of the injected sequence requires an injected trigger event to occur.

This mode can be combined with the AUTDLY mode:

- Once a simultaneous injected sequence of conversions has ended, a new injected trigger event is accepted only if both JEOS bits of the master and the slave ADC have been cleared (delay phase). Any new injected trigger events occurring during the ongoing injected sequence and the associated delay phase are ignored.
- Once a regular sequence of conversions of the master ADC has ended, a new regular trigger event of the master ADC is accepted only if the master data register (ADC_DR) has been read. Any new regular trigger events occurring for the master ADC during the ongoing regular sequence and the associated delay phases are ignored.

  There is the same behavior for regular sequences occurring on the slave ADC.

In this mode, the following register bits are shared between the master and slave ADCs: JADSTART, JADSTP, JDISCEN, JOVSE, JLEN, JEXTEN, JEXTSEL, GCOMPEN, JOVSECT, JOVSISE, JOVSE, and TJOVS.

#### Regular simultaneous mode with independent injected conversions

The regular simultaneous mode is selected by programming DUAL[4:0] bits to 0b00110.

This mode applies to a regular group of channels. The external trigger source comes from the regular group multiplexer of the master ADC (selected by the EXTSEL bits in the ADC_CFGR1 register). A simultaneous trigger is provided to the slave ADC.

In this mode, independent injected conversions are supported. An injection request (either on the master or on the slave) aborts the current simultaneous conversions both for master and slave. They are restarted once the injected conversion is completed.

*Note:* Do not convert the same channel on the two ADCs (no overlapping sampling times for the two ADCs when converting the same channel).

In regular simultaneous mode, the user software must convert sequences with the same length. Sampling times for channels with the same sequence number must be equal.

The software is notified by interrupts when it can read the data:

- As the duration of the master regular sequence is equal to the duration of the slave one (as shown in Figure 127), the software can enable only one of the two EOC interrupts (for example the master EOC) and read both converted data from the common data register (ADCC_CDR).

  The user can read data from either ADCC_CDR or ADCC_CDR2. Once software selects one of these registers, it must continue using the same register until the ADSTP procedure is executed.

The regular data can also be read using the DMA. Several methods are possible:

- Use two DMA channels (one for the master and one for the slave). In this case DAMDF[1:0] bits must be kept cleared:
  1. Configure the DMA master ADC channel to read ADC_DR from the master. DMA requests are generated at each EOC event of the master ADC.
  2. Configure the DMA slave ADC channel to read ADC_DR from the slave. DMA requests are generated at each EOC event of the slave ADC.
- Configure the dual ADC mode data format DAMDF[1:0] bits, which leaves one DMA channel free for other uses:
  1. Set DAMDF[1:0] = 0b10 or 0b11 (depending on resolution).
  2. A single DMA channel is used (the one corresponding to the master). Configure the DMA master ADC channel to read the common ADC data register (ADCC_CDR or ADCC_CDR2).
  3. A single DMA request is generated each time both the master and slave EOC events occur. At that moment:
     - The slave ADC converted data is available in the upper half-word of the 32-bit ADCC_CDR register
     - The master ADC converted data is available in the lower half-word of the ADCC_CDR register.

     Alternatively, data can be read from ADCC_CDR2:

     - The first read returns the master ADC data.
     - The second read returns the slave ADC data.

     After these reads, a DMA request is generated. The DMA transfers the slave data from the same data register and handles two transfers for dual mode operation.
  4. Both EOC flags are cleared when the DMA reads the ADCC_CDR register.

*Note:* When DAMDF[1:0] = 0b10 or 0b11, the user must program the same number of conversions in the master and in the slave sequence. Otherwise, the remaining conversions do not generate a DMA request.

**Figure 127. Regular simultaneous mode on 16 channels: dual ADC mode** (described in prose)

On a trigger, the master ADC converts CH1, CH2, CH3, CH4 ... CH16 while the slave ADC simultaneously converts CH16, CH14, CH13, CH12 ... CH1. The end of the regular sequence occurs on the master and slave ADC at the same time.

If the DISCEN bit is set, each "n" simultaneous conversion of the regular sequence require a regular trigger event to occur ("n" is defined by DISCNUM).

This mode can be combined with the AUTDLY mode:

- Once a simultaneous conversion of the sequence has completed, the next conversion in the sequence starts only after the EOC flag of both the master and the slave are cleared.
- Once a simultaneous regular sequence of conversions has completed, a new regular trigger event is accepted only after the EOC flag of both the master and the slave are cleared. Any new regular trigger events occurring during the ongoing regular sequence and the associated delay phases are ignored.

The DMA can be used to handle data in regular simultaneous mode combined with AUTDLY mode, assuming that multi-DMA mode is used: bits DAMDF must be set to 0b10 or 0b11.

#### Interleaved mode with independent injected conversions

This mode is selected by programming DUAL[4:0] bits to 0b00111.

It can be started only on a regular group (usually one channel). The external trigger source comes from the regular channel multiplexer of the master ADC.

After an external trigger occurs:

- The master ADC starts immediately,
- The slave ADC starts after a delay of several ADC clock cycles after the sampling phase of the master ADC has completed (during the master ADC conversion period).

The minimum delay between two conversions in interleaved mode is configured in the DELAY bits in the ADCC_CCR register (see Table DELAY bits versus ADC resolution). This delay starts counting one half cycle after the end of the sampling phase of the master conversion. This way, an ADC cannot start a conversion if the complementary ADC is still sampling its input (only one ADC can sample the input signal at a given time).

- The minimum possible DELAY is 1 to ensure that there is at least one cycle time between the opening of the analog switch of the master ADC sampling phase and the closing of the analog switch of the slave ADC sampling phase.
- The maximum DELAY is equal to the number of cycles corresponding to the selected resolution. However, the user must properly calculate this delay to ensure that an ADC does not start a conversion while the other ADC is still sampling its input.

As the CONT bit is set on both the master and slave ADCs, the selected regular channels of both ADCs are continuously converted.

The software is notified by interrupts when it can read the data at the end of each conversion event (EOC) on the master or slave ADC. A slave and master EOC interrupts are generated (if EOCIE is enabled) and the software can read the ADC_DR of the slave/master ADC.

**Table 151. DELAY bits versus ADC resolution**

| DELAY bits | 12-bit resolution | 10-bit resolution | 8-bit resolution | 6-bit resolution |
|---|---|---|---|---|
| 0000 | 1 * Tadc_ker_ck | 1 * Tadc_ker_ck | 1 * Tadc_ker_ck | 1 * Tadc_ker_ck |
| 0001 | 2 * Tadc_ker_ck | 2 * Tadc_ker_ck | 2 * Tadc_ker_ck | 2 * Tadc_ker_ck |
| 0010 | 3 * Tadc_ker_ck | 3 * Tadc_ker_ck | 3 * Tadc_ker_ck | 3 * Tadc_ker_ck |
| 0011 | 4 * Tadc_ker_ck | 4 * Tadc_ker_ck | 4 * Tadc_ker_ck | 4 * Tadc_ker_ck |
| 0100 | 5 * Tadc_ker_ck | 5 * Tadc_ker_ck | 5 * Tadc_ker_ck | 5 * Tadc_ker_ck |
| 0101 | 6 * Tadc_ker_ck | 6 * Tadc_ker_ck | 6 * Tadc_ker_ck | 6 * Tadc_ker_ck |
| 0110 | 7 * Tadc_ker_ck | 7 * Tadc_ker_ck | 7 * Tadc_ker_ck | 7 * Tadc_ker_ck |
| 0111 | 8 * Tadc_ker_ck | 8 * Tadc_ker_ck | 8 * Tadc_ker_ck | 7 * Tadc_ker_ck |
| 1000 | 9 * Tadc_ker_ck | 9 * Tadc_ker_ck | 9 * Tadc_ker_ck | 7 * Tadc_ker_ck |
| 1001 | 10 * Tadc_ker_ck | 10 * Tadc_ker_ck | 9 * Tadc_ker_ck | 7 * Tadc_ker_ck |
| 1010 | 11 * Tadc_ker_ck | 11 * Tadc_ker_ck | 9 * Tadc_ker_ck | 7 * Tadc_ker_ck |
| 1011 | 12 * Tadc_ker_ck | 11 * Tadc_ker_ck | 9 * Tadc_ker_ck | 7 * Tadc_ker_ck |
| 1100 | 13 * Tadc_ker_ck | 11 * Tadc_ker_ck | 9 * Tadc_ker_ck | 7 * Tadc_ker_ck |
| others | 13 * Tadc_ker_ck | 11 * Tadc_ker_ck | 9 * Tadc_ker_ck | 7 * Tadc_ker_ck |

**Figure 128. Interleaved mode on 1 channel in continuous conversion mode: Dual ADC mode** (described in prose)

After the trigger, the master ADC samples and converts CH1 repeatedly. The slave ADC samples and converts the same CH1. Each slave sampling phase starts 5 ADCCLK cycles after the end of the master's sampling phase. The next master sampling starts 5 ADCCLK cycles after the end of the slave's sampling phase. "End of conversion on master and slave ADC" is marked at the conversion ends.

**Figure 129. Interleaved mode on 1 channel in single conversion mode: Dual ADC mode** (described in prose)

Each trigger causes the master ADC to sample and convert CH1. The slave ADC starts sampling CH1 5 ADCCLK cycles after the end of the master's sampling phase. "End of conversion on master and slave ADC" follows the slave conversion, and the next trigger repeats the pattern.

If the DISCEN bit is set, each "n" simultaneous conversion ("n" is defined by DISCNUM) of the regular sequence require a regular trigger event to occur.

In interleaved mode, injected conversions are supported. When injection is done (either on master or slave), both master and the slave regular conversions are aborted and the sequence is restarted from the master (see Figure 130).

*Note:* In interleaved mode, the ADCx_AWDy_OUT signal for the master ADC is synchronized with the EOC of the master ADC, but the interrupt flag is synchronized with the EOC/JEOC flag of the slave ADC.

In addition, the ROVSM = 0 setting is not supported in oversampling mode.

**Figure 130. Interleaved conversion with injection** (described in prose)

1. ADC1 (master) converts CH1 repeatedly and ADC2 (slave) converts CH2 interleaved, with "read CDR" after each slave conversion.
2. An injected trigger aborts the ongoing master and slave conversions ("conversions aborted"), and the injected channel CH11 is converted.
3. Regular interleaved conversion then resumes, always on the master ("Resume (always on master)"): CH1 on ADC1, then CH2 on ADC2, and so on.

The figure legend distinguishes sampling and conversion phases. The last slave conversion is labeled CH0.

#### Alternate trigger mode with independent regular conversions

The alternate trigger mode is selected by programming DUAL[4:0] bits to 0b01001.

This mode can only be started on an injected group. The source of the external trigger comes from the multiplexer injected group of the master ADC.

This mode is only possible when selecting hardware triggers: JEXTEN[1:0] must not be 0x0.

**Injected discontinuous mode disabled (JDISCEN = 0)**

1. When the first trigger occurs, all injected master ADC channels in the group are converted.
2. When the second trigger occurs, all injected slave ADC channels in the group are converted.
3. And so on...

A JEOS interrupt, if enabled, is generated after all injected channels of the master ADC in the group have been converted.

A JEOS interrupt, if enabled, is generated after all injected channels of the slave ADC in the group have been converted.

JEOC interrupts, if enabled, can also be generated after each injected conversion.

**Figure 131. Alternate trigger: injected group of each ADC** (described in prose)

1. The 1st trigger makes the master ADC convert its injected group: JEOC after each conversion, then JEOC and JEOS on the master ADC after the last.
2. The 2nd trigger makes the slave ADC convert its injected group, with JEOC per conversion and JEOC, JEOS on the slave ADC at the end.
3. The 3rd trigger goes to the master and the 4th to the slave, and so on.

*Note:* Regular conversions can be enabled on one or all ADCs. In this case, the regular conversions are independent of each other. A regular conversion is interrupted when the ADC has to perform an injected conversion. It is resumed when the injected conversion is finished.

The time interval between two trigger events must be greater than or equal to one ADC clock period. The minimum time interval between two trigger events that start conversions on the same ADC is the same as in the single ADC mode.

**Injected discontinuous mode enabled (JDISCEN = 1)**

If the injected discontinuous mode is enabled for both master and slave ADCs:

1. When the first trigger occurs, the first injected channel of the master ADC is converted.
2. When the second trigger occurs, the first injected channel of the slave ADC is converted.
3. And so on...

A JEOS interrupt, if enabled, is generated after all injected channels of the master ADC in the group have been converted.

A JEOS interrupt, if enabled, is generated after all injected channels of the slave ADC in the group have been converted.

JEOC interrupts, if enabled, can also be generated after each injected conversion.

**Figure 132. Alternate trigger: 4 injected channels (each ADC) in discontinuous mode** (described in prose)

The odd triggers (1st, 3rd, 5th, 7th) each convert one injected channel on the master ADC, with JEOC on the master ADC each time. JEOC and JEOS on the master ADC follow the 7th trigger. The even triggers (2nd, 4th, 6th, 8th) each convert one injected channel on the slave ADC, with JEOC on the slave ADC. JEOC and JEOS on the slave ADC follow the 8th trigger.

#### Combined regular/injected simultaneous mode

This mode is selected by programming DUAL[4:0] bits to 0b00001.

The simultaneous conversion of a regular group can be interrupted to start the simultaneous conversion of an injected group.

*Note:* In combined regular/injected simultaneous mode, the user software must convert sequences with the same length.

#### Combined regular simultaneous and alternate trigger mode

This mode is selected by programming DUAL[4:0] bits to 0b00010.

The simultaneous conversion of a regular group can be interrupted to start the alternate trigger conversion of an injected group. Figure 133 shows the behavior of an alternate trigger interrupting a simultaneous regular conversion.

The injected alternate conversion immediately starts after the injected event. If a regular conversion is already running, in order to ensure synchronization after the injected conversion, the regular conversion of all (master/slave) ADCs is stopped and resumed synchronously at the end of the injected conversion.

*Note:* In combined regular simultaneous + alternate trigger mode, the user software must convert sequences with the same length.

The software trigger is not supported for injected conversions.

**Figure 133. Alternate + regular simultaneous** (described in prose)

1. The master regular sequence is CH1, CH2, CH3, ... and the slave regular sequence is CH4, CH6, CH7, ...
2. The 1st injected trigger aborts the ongoing regular conversion (master CH3, slave CH7). The master converts its injected CH1, and then both regular conversions restart together (master CH3, slave CH7).
3. The 2nd trigger aborts the regular conversions again (master CH4, slave CH8). The slave converts its injected CH1.
4. Both regular sequences resume with CH4/CH8, then CH5/CH9 ("synchronization not lost").

If a trigger occurs during an injected conversion that has interrupted a regular conversion, the alternate trigger is served. Figure 134 shows the behavior in this case (note that the sixth trigger is ignored because the associated alternate conversion is not complete).

**Figure 134. Case of trigger occurring during injected conversion** (described in prose)

1. The master regular sequence is CH1, CH2, CH3, ... and the slave regular sequence is CH7, CH8, CH9, ...
2. The 1st trigger aborts the regular conversions (master CH3, slave CH9) and the master converts injected CH14. The 2nd trigger, arriving during that injected conversion, starts the slave injected CH15.
3. The regular conversions then resume with CH3/CH9.
4. The 3rd trigger aborts CH4/CH10 and the master converts CH14. Regular conversion resumes with CH4/CH10.
5. The 4th trigger aborts CH5/CH11 and the slave converts CH15. The 5th trigger, arriving during it, starts master CH14.
6. The 6th trigger is ignored because the associated alternate conversion is not complete.
7. Regular conversions resume with CH5/CH11 and then CH6/CH12.

#### Combined injected simultaneous and interleaved mode

This mode is selected by programming DUAL[4:0] bits to 0b00011.

An interleaved conversion can be interrupted with a simultaneous injected event.

In this case, the interleaved conversion is immediately interrupted and the simultaneous injected conversion starts. At the end of the injected sequence, the interleaved conversion is resumed. When the interleaved regular conversion resumes, the first regular conversion which is performed is always the master's one. Figure 135, Figure 136, and Figure 137 show examples of this behavior.

*Note:* In this mode, the ROVSM = 0 setting is not supported in oversampling mode.

**Figure 135. Interleaved single channel CH0 with injected sequence CH11, CH12** (described in prose)

1. ADC1 (master) and ADC2 (slave) interleave conversions of CH0, with "read CDR" after each slave conversion.
2. An injected trigger aborts the master and slave conversions in progress ("Conversions aborted").
3. The injected conversions are drawn as two simultaneous rows, one with CH11, CH11 and one with CH12, CH12.
4. Interleaved conversion resumes ("Resume (always restart with the master)").

**Figure 136. Two interleaved channels (CH1, CH2) with injected sequence CH11, CH12 - case 1: Master interrupted first** (described in prose)

ADC1 (master) converts CH1 and ADC2 (slave) converts CH2, interleaved, with "read CDR" after each slave conversion. The injected trigger arrives during a master conversion and aborts the conversions. The injected conversions are drawn as two simultaneous rows (CH11, CH11 and CH12, CH12). Interleaved conversion then resumes, always restarting with the master.

**Figure 137. Two interleaved channels (CH1, CH2) with injected sequence CH11, CH12 - case 2: Slave interrupted first** (described in prose)

This is the same as Figure 136, but the injected trigger arrives during a slave conversion. Conversions are aborted, the injected conversions (CH11, CH11 and CH12, CH12) follow, and interleaving resumes with the master.

#### DMA requests in dual ADC mode

In all dual ADC modes, it is possible to use two DMA channels (one for the master, one for the slave) to transfer the data, like in single mode (refer to Figure 138: DMA requests in regular simultaneous mode when DAMDF[1:0] = 0b00).

**Figure 138. DMA requests in regular simultaneous mode when DAMDF[1:0] = 0b00** (described in prose)

Each trigger converts CH1 on the master and CH2 on the slave simultaneously.

- The master EOC raises a DMA request from the ADC master, and the DMA reads the master ADC_DR.
- The slave EOC raises a DMA request from the ADC slave, and the DMA reads the slave ADC_DR.

This is a configuration where each sequence contains only one conversion. Master and slave timings are equal.

In interleaved mode or in simultaneous regular mode, it is also possible to save one DMA channel and transfer both data using a single DMA channel. To do this, the DAMDF[1:0] bits must be configured in the ADCC_CCR register:

- DAMDF[1:0] = 0b10, 32-bit format:

  A DMA request is generated alternatively after the master and slave EOC events have occurred. At that time, the data are alternatively available in the 32-bit register ADCC_CDR2 32-bit register.

  This mode is used when the data width is above 16 bits (conversion data width can exceed 16 bits when functions such as oversampling, compensation and left-bit shift, are used).

  Behavior: A DMA request is generated each time a new 32-bit data is available:

  - First DMA request: ADCC_CDR2[31:0] = MST_ADC_DR[31:0]
  - Second DMA request: ADCC_CDR2[31:0] = SLV_ADC_DR[31:0]

- DAMDF[1:0] = 0b10, 16-bit format:

  A DMA request is generated alternatively after the master and slave EOC events have occurred. At that time, two data items are available and the 32-bit register ADCC_CDR contains the two half-words representing two ADC-converted data. The slave ADC data takes the upper half-word and the master ADC data takes the lower half-word. DMA transfers two data by one request.

  Any value above 16-bit in the master or the slave-converted data is truncated to the least 16 significant bits.

  Behavior: A DMA request is generated each time a new 32-bit data is available:

  - First DMA request: ADCC_CDR[31:0] = (SLV_ADC_DR[15:0] << 16) | MST_ADC_DR[15:0]
  - Second DMA request: ADCC_CDR[31:0] = SLV_ADC_DR[15:0] | MST_ADC_DR[15:0]

**Figure 139. DMA requests in interleaved mode when DAMDF = 0b10** (described in prose)

On each trigger, the master converts CH1, and after a "Delay" the slave converts CH2. The master EOC and the slave EOC each assert and are cleared. Once per master-plus-slave pair, after the slave EOC, a "DMA request from ADC Master" pulse is issued. The "DMA request from ADC Slave" line stays inactive. This is a configuration where each sequence contains only one conversion.

*Note:* When using dual ADC mode, the user must take care to configure properly the duration of the master and slave conversions so that a DMA request is generated and served for reading both data (master + slave) before a new conversion data is available.

- DAMDF[1:0] = 0b11:

  This mode is similar to the DAMDF[1:0] = 0b10 configuration. The only difference is that on each DMA request (two data are available), two bytes representing two ADC converted data are transferred as a half-word.

  This mode is used when the resolution is 6 bits or 8 bits and data are not signed.

  Behavior: A DMA request is generated each time two data items are available:

  - First DMA request: ADCC_CDR[15:0] = (SLV_ADC_DR[7:0] << 8)| MST_ADC_DR[7:0]
  - Second DMA request: ADCC_CDR[15:0] = SLV_ADC_DR[7:0] | MST_ADC_DR[7:0]

*Note:* DMA burst mode is not supported in ADC dual mode.

#### Overrun detection when OVRMOD = 0

In dual ADC mode (when DUAL[4:0] is not equal to b00000), if an overrun is detected on one of the ADCs, DMA requests are no longer issued to ensure that all the data transferred to the RAM are valid (this behavior occurs whatever the DAMDF configuration). The EOC bit corresponding to one ADC might remains set because the data register of this ADC contains valid data.

#### Overrun detection when OVRMOD = 1

In dual ADC mode, if an overrun occurs on either ADC, the data register is overwritten, causing continuous DMA requests. This results in loss of data coherency.

#### DMA one-shot mode/ DMA circular mode when multi-ADC mode is selected

When DAMDF mode is selected (0b10 or 0b11), DMNGT[1:0] bits of the ADCC_CCR register must also be configured to select between DMA one-shot mode and circular mode, as explained in section Section : Managing conversions using the DMA

*Digest note:* ADCC_CCR has no DMNGT field (Section 21.7.2). DMNGT[1:0] is in ADC_CFGR1.

#### Stopping the conversions in dual ADC modes

In dual ADC mode, the user software must set the ADSTP/JADSTP control bits in the master ADC to stop the conversions of both ADC. The other ADSTP control bit on the slave ADC has no effect in dual ADC mode.

Once both ADCs are effectively stopped, the ADSTART/JADSTART bits on the master and slave ADCs are both deasserted by hardware.

#### Analog watchdog in dual mode

The analog watchdog is supported in all dual modes.

#### Disabling the ADC in dual mode

During a dual-mode operation, the master ADC shares the ADC clock with the slave ADC. To disable the ADC correctly through the ADDIS bit of ADC_CR, set the ADSTP (or JADSP) bit on the master ADC. Once ADSTP (or JADSTP) becomes 0 both for the master and slave ADCs, set the ADDIS bit on the master ADC, then set the ADDIS bit on the slave ADC.

#### Autoinjection mode in dual mode

Autoinjection mode is not supported when DUAL[4:0] equals 0b00010, 0b00011, 0b00101, 0b00110, 0b00111, or 0b01001.

Additionally, parallel injected oversampling mode is not supported in autoinjection mode.

#### Dual ADC modes supported in oversampling mode

It is possible to have oversampling enabled when working in dual ADC configuration. In this case, the two ADCs must be programmed with the very same settings (including oversampling).

### 21.4.30 Temperature sensor

The temperature sensor can be used to measure the junction temperature (TJ) of the device.

The temperature sensor is internally connected to the ADC input channels, which are used to convert the sensor output voltage to a digital value (see Table: ADC interconnection in Section 21.4.2: ADC pins and internal signals for more details). When not in use, the sensor can be put in power-down mode. It supports the temperature range specified in the product datasheet.

Figure 140 shows the block diagram of connections between the temperature sensor and the ADC.

The temperature sensor output voltage changes linearly with temperature. The offset of this line varies from chip to chip due to process variation (up to 45 °C from one chip to another).

The uncalibrated internal temperature sensor is more suited for applications that detect temperature variations instead of absolute temperatures. To improve the accuracy of the temperature sensor measurement, calibration values are stored in system memory for each device by ST during production.

During the manufacturing process, the calibration data of the temperature sensor and the internal voltage reference are stored in the system memory area. The user application can then read them and use them to improve the accuracy of the temperature sensor or the internal reference (refer to the datasheet for additional information).

The temperature sensor is internally connected to the ADC input channel, which is used to convert the sensor's output voltage to a digital value. Refer to the electrical characteristics section of the device datasheet for the sampling time value to be applied when converting the internal temperature sensor.

When not in use, the sensor can be put in power-down mode.

Figure 140 shows the block diagram of the temperature sensor.

**Figure 140. Temperature sensor channel block diagram** (described in prose)

The temperature sensor output VSENSE goes to an ADC input of ADCx. The TSEN control bit enables the sensor. The converted data goes to the address/data bus.

#### Reading the temperature

To use the sensor:

1. Select the ADC input channel that is connected to VSENSE.
2. Program with the appropriate sampling time (refer to the electrical characteristics section of the device datasheet).
3. Set the TSEN bit in the ADCC_CCR register to wake up the temperature sensor from power-down mode.
4. Start the ADC conversion.
5. Read the resulting VSENSE data in the ADC data register.
6. Calculate the actual temperature using the following formula:

   Temperature (in °C) = ((TS_CAL2_TEMP – TS_CAL1_TEMP) / (TS_CAL2 – TS_CAL1)) × (TS_DATA – TS_CAL1) + TS_CAL1_TEMP

   Where:

   - TS_CAL2 is the temperature sensor calibration value acquired at TS_CAL2_TEMP.
   - TS_CAL1 is the temperature sensor calibration value acquired at TS_CAL1_TEMP.
   - TS_DATA is the actual temperature sensor output value converted by ADC.

   Refer to the device datasheet for more information about TS_CAL1 and TS_CAL2 calibration points.

*Caution:* The above formula is valid only if the VREF+ condition specified in the table Temperature sensor calibration values of the datasheet are respected.

*Note:* The sensor has a startup time after waking from power-down mode before it can output VSENSE at the correct level. The ADC also has a startup time after power-on, so to minimize the delay, the ADEN, and TSEN bits must be set simultaneously.

*Digest note:* On STM32C55xxx, VSENSE is ADC1 channel 12 (ADC1 VIN[12], Table 139). ADC2 has no temperature sensor channel. TSEN is in ADCC_CCR and ADEN in ADC_CR, so they cannot literally be written in one access. The ADCC_CCR.TSEN description also allows writing TSEN only when ADEN = 0. Datasheet values:

- TS_CAL1: raw data at 30 °C, VDDA = 3.3 V, at 0x08FF F814 - 0x08FF F815.
- TS_CAL2: raw data at 140 °C, VDDA = 3.3 V, at 0x08FF F818 - 0x08FF F819.
- tS_temp (minimum sampling time) = 13 µs.
- tstart_run (sensor buffer startup) = 25.2 µs max.
- Avg_Slope = 2.14 mV/°C typ.
- V30 = 0.65 V typ.

The longest SMP setting is 289 ADC clock cycles, so meeting tS_temp = 13 µs needs fadc_ker_ck ≤ about 22.2 MHz. Otherwise the bulb or SMPTRIG sampling modes are needed.

### 21.4.31 Monitoring the internal voltage reference

It is possible to monitor the internal voltage reference (VREFINT) to have a reference point for evaluating the ADC VREF+ voltage level.

Refer to the ADC interconnection table in Section 21.4.2: ADC pins and internal signals for details on the ADC input channels to which the internal voltage reference is internally connected.

Refer to the electrical characteristics section of the device datasheet for the sampling time value to be applied when converting the internal voltage reference voltage.

Figure 141 shows the block diagram of the VREFINT sensing feature.

**Figure 141. VREFINT channel block diagram** (described in prose)

The internal power block provides VREFINT to an ADC input of ADCx. The connection is gated by the VREFEN control bit(1).

Notes:

1. The VREFEN bit of the ADCC_CCR register must be set to enable the conversion of internal channels (VREFINT).

#### Calculating the actual VREF+ voltage using the internal reference voltage

The power supply voltage applied to the device may be subject to variations or not precisely known. When VDDA is connected to VREF+, it is possible to compute the actual VDDA voltage using the embedded internal reference voltage (VREFINT). VREFINT and its calibration data acquired by the ADC during the manufacturing process at VREF+ can be used to evaluate the actual VDDA voltage level.

The following formula gives the actual VREF+ voltage supplying the device:

VREF+ = VREF+_Charac × VREFINT_CAL / VREFINT_DATA

Where:

- VREF+_Charac is the value of VREF+ voltage characterized at VREFINT during the manufacturing process. It is specified in the device datasheet.
- VREFINT_CAL is the VREFINT calibration value.
- VREFINT_DATA is the actual VREFINT output value converted by ADC.

#### Converting a supply-relative ADC measurement to an absolute voltage value

The ADC is designed to deliver a digital value corresponding to the ratio between VREF+ and the voltage applied on the converted channel.

For some applications, the VREF+ value is unknown and ADC converted values are right-aligned. In this case, it is necessary to convert this ratio into a voltage independent from VREF+:

VCHANNELx = (VREF+ / FULL_SCALE) × ADC_DATA

By replacing VREF+ by the formula provided above, the absolute voltage value is given by the following formula

VCHANNELx = (VREF+_Charac × VREFINT_CAL × ADC_DATA) / (VREFINT_DATA × FULL_SCALE)

For applications where VREF+ is known and ADC converted values are right-aligned, the absolute voltage value can be obtained by using the following formula:

VCHANNELx = (VREF+ / FULL_SCALE) × ADC_DATA

Where:

- VREFINT_CAL is the VREFINT calibration value.
- ADC_DATA is the value measured by the ADC on channel x (right-aligned).
- VREFINT_DATA is the actual VREFINT output value converted by the ADC.
- FULL_SCALE is the maximum digital value of the ADC output. For example with 12-bit resolution, we obtain 2^12 – 1 = 4095, or 2^8 – 1 = 255 with 8-bit resolution.

*Note:* If ADC measurements are done using an output format other than 12-bit right-aligned, all the parameters must first be converted to a compatible format before the calculation is done.

*Digest note:* On STM32C55xxx, VREFINT is ADC1 channel 13 (ADC1 VIN[13], Table 139). Datasheet values:

- VREFINT_CAL: raw data at 30 °C, VDDA = 3.3 V, at 0x08FF F810 - 0x08FF F811.
- tS_vrefint (minimum sampling time) = 4.3 µs.
- tstart_vrefint = 4.4 µs max.
- VREFINT = 1.180 V min, 1.217 V typ, 1.250 V max.

Table 139 describes ADC1 VIN[13] as "VREFINT (output voltage from internal reference voltage or dac_int1)". [unclear in source: how the selection between the internal reference voltage and dac_int1 is made]

## 21.5 ADC interrupts

For each ADC, an interrupt can be generated:

- After ADC power-up, when the ADC is ready (ADRDY flag)
- On the end of any conversion for regular groups (EOC flag)
- On the end of a sequence of conversion for regular groups (EOS flag)
- On the end of any conversion for injected groups (JEOC flag)
- On the end of a sequence of conversion for injected groups (JEOS flag)
- When an analog watchdog detection occurs (AWD1, AWD2 and AWD3 flags)
- When the end of the sampling phase occurs (EOSMP flag)
- When the data overrun occurs (OVR flag)
- When the ADC internal voltage regulator output is ready (LDORDY flag)

Separate interrupt enable bits are available for flexibility.

*Note:* Interrupts are generated by the AHB clock domain. Since the ADC clock is adc_ker_ck, interrupt flags are delayed due to the synchronization between adc_ker_ck and AHB clock domains.

**Table 152. ADC interrupts**

| Interrupt vector | Interrupt event | Event flag | Enable Control bit | Interrupt clear method | Exit from Sleep mode | Exit from Stop, Standby mode |
|---|---|---|---|---|---|---|
| ADC | ADC ready | ADRDY | ADRDYIE | Set by hardware and cleared by software | Yes | No |
| ADC | End of conversion of a regular group | EOC | EOCIE | Set by hardware and cleared by software | Yes | No |
| ADC | End of conversion sequence of a regular group | EOS | EOSIE | Set by hardware and cleared by software | Yes | No |
| ADC | End of conversion of an injected group | JEOC | JEOCIE | Set by hardware and cleared by software | Yes | No |
| ADC | End of conversion sequence of an injected group | JEOS | JEOSIE | Set by hardware and cleared by software | Yes | No |
| ADC | Analog watchdog 1 flag is set | AWD1 | AWD1IE | Set by hardware and cleared by software | Yes | No |
| ADC | Analog watchdog 2 flag is set | AWD2 | AWD2IE | Set by hardware and cleared by software | Yes | No |
| ADC | Analog watchdog 3 flag is set | AWD3 | AWD3IE | Set by hardware and cleared by software | Yes | No |
| ADC | End of sampling phase | EOSMP | EOSMPIE | Set by hardware and cleared by software | Yes | No |
| ADC | Overrun | OVR | OVRIE | Set by hardware and cleared by software | Yes | No |
| ADC | ADC internal voltage regulator ready | LDORDY | LDORDYIE | Set by hardware and cleared by software | Yes | No |

*Digest note:* In the source, the vector, clear method, Sleep and Stop/Standby columns are each one cell spanning all rows. The ST CMSIS header stm32c552xx.h defines separate vectors ADC1_IRQn = 32 and ADC2_IRQn = 33.

## 21.6 ADC registers (for each ADC)

Refer to Section 1.2 for a list of abbreviations used in register descriptions.

*Digest note:* The ST CMSIS header stm32c552xx.h gives these base addresses: ADC1_BASE = 0x4202 8000, ADC2_BASE = 0x4202 8100 and ADC12_COMMON_BASE = 0x4202 8300 (AHB2PERIPH_BASE 0x4202 0000 + 0x08000 / 0x08100 / 0x08300). This chapter refers to Section 2.2 (Memory organization) for the boundary addresses.

### 21.6.1 ADC interrupt and status register (ADC_ISR)

Address offset: 0x000. Reset value: 0x0000 0000. Access: bits 12 and 9:0 are rc_w1 (read, clear by writing 1).

- **Bits 31:13** Reserved, must be kept at reset value.
- **Bit 12 LDORDY** (rc_w1): ADC internal voltage regulator output ready flag. This bit is set by hardware and cleared by software. It indicates that the ADC internal voltage regulator output is ready and that the ADC can be enabled or calibrated.
  - 0: ADC LDO internal voltage regulator disabled
  - 1: ADC LDO internal voltage regulator enabled
- **Bits 11:10** Reserved, must be kept at reset value.
- **Bit 9 AWD3** (rc_w1): Analog watchdog 3 flag. This bit is set by hardware when the converted voltage crosses the values programmed in the fields LTR[22:0] and HTR[22:0] of ADC_AWD3LTR and ADC_AWD3HTR registers. It is cleared by software writing 1 to it or when ADEN = 0.
  - 0: No analog watchdog 3 event occurred (or the flag event was already acknowledged and cleared by software)
  - 1: Analog watchdog 3 event occurred
- **Bit 8 AWD2** (rc_w1): Analog watchdog 2 flag. This bit is set by hardware when the converted voltage crosses the values programmed in the fields LTR[22:0] and HTR[22:0] of ADC_AWD2LTR and ADC_AWD2HTR registers. It is cleared by software writing 1 to it or when ADEN = 0.
  - 0: No analog watchdog 2 event occurred (or the flag event was already acknowledged and cleared by software)
  - 1: Analog watchdog 2 event occurred
- **Bit 7 AWD1** (rc_w1): Analog watchdog 1 flag. This bit is set by hardware when the converted voltage crosses the values programmed in the fields LTR[22:0] and HTR[22:0] of ADC_AWD1LTR and ADC_AWD1HTR registers. It is cleared by software writing 1 to it or when ADEN = 0.
  - 0: No analog watchdog 1 event occurred (or the flag event was already acknowledged and cleared by software)
  - 1: Analog watchdog 1 event occurred
- **Bit 6 JEOS** (rc_w1): Injected channel end of sequence flag. This bit is set by hardware at the end of the conversions of all injected channels in the group. It is cleared by software writing 1 to it or when ADEN = 0.
  - 0: Injected conversion sequence not complete (or the flag event was already acknowledged and cleared by software)
  - 1: Injected conversions complete
- **Bit 5 JEOC** (rc_w1): Injected channel end of conversion flag. This bit is set by hardware at the end of each injected conversion of a channel when a new data is available in the corresponding ADC_JDRy register. It is cleared by software writing 1 to it, when ADEN = 0, or by reading the corresponding ADC_JDRy register.
  - 0: Injected channel conversion not complete (or the flag event was already acknowledged and cleared by software)
  - 1: Injected channel conversion complete
- **Bit 4 OVR** (rc_w1): ADC overrun. This bit is set by hardware when an overrun occurs on a regular channel (a new conversion has completed while the EOC flag was already set) or when adc_hclk clock is too slow to manage the data. It is cleared by software writing 1 to it or when ADEN = 0.
  - 0: No overrun occurred (or the flag event was already acknowledged and cleared by software)
  - 1: Overrun has occurred
- **Bit 3 EOS** (rc_w1): End of regular sequence flag. This bit is set by hardware at the end of the conversions of a regular sequence of channels. It is cleared by software writing 1 to it or when ADEN = 0.
  - 0: Regular conversions sequence not complete (or the flag event was already acknowledged and cleared by software)
  - 1: Regular conversions sequence complete
- **Bit 2 EOC** (rc_w1): End of conversion flag. This bit is set by hardware at the end of each regular conversion of a channel when a new data is available in the ADC_DR register. It is cleared by software writing 1 to it, when ADEN = 0, or by reading the ADC_DR register.
  - 0: Regular channel conversion not complete (or the flag event was already acknowledged and cleared by software)
  - 1: Regular channel conversion complete
- **Bit 1 EOSMP** (rc_w1): End of sampling flag. This bit is set by hardware during the conversion of any channel (only for regular channels), at the end of the sampling phase. It is cleared by software writing 1 or when ADEN = 0.
  - 0: not at the end of the sampling phase (or the flag event was already acknowledged and cleared by software)
  - 1: End of sampling phase reached
- **Bit 0 ADRDY** (rc_w1): ADC ready. This bit is set by hardware after the ADC has been enabled (bit ADEN = 1) and when the ADC reaches a state where it is ready to accept conversion requests. It is cleared by software writing 1 to it or when ADEN = 0.
  - 0: ADC not yet ready to start conversion (or the flag event was already acknowledged and cleared by software)
  - 1: ADC is ready to start conversion

### 21.6.2 ADC interrupt enable register (ADC_IER)

Address offset: 0x004. Reset value: 0x0000 0000. Access: bits 12 and 9:0 are rw.

- **Bits 31:13** Reserved, must be kept at reset value.
- **Bit 12 LDORDYIE** (rw): ADC internal voltage regulator interrupt enable. This bit is set and cleared by software to enable/disable the ADC internal voltage regulator interrupt.
  - 0: Internal voltage regulator interrupt disabled
  - 1: Internal voltage regulator interrupt enabled
  - *Note:* The software is allowed to write this bit only when ADEN = 0.
- **Bits 11:10** Reserved, must be kept at reset value.
- **Bit 9 AWD3IE** (rw): Analog watchdog 3 interrupt enable. This bit is set and cleared by software to enable/disable the analog watchdog 2 interrupt.
  - 0: Analog watchdog 3 interrupt disabled
  - 1: Analog watchdog 3 interrupt enabled
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bit 8 AWD2IE** (rw): Analog watchdog 2 interrupt enable. This bit is set and cleared by software to enable/disable the analog watchdog 2 interrupt.
  - 0: Analog watchdog 2 interrupt disabled
  - 1: Analog watchdog 2 interrupt enabled
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bit 7 AWD1IE** (rw): Analog watchdog 1 interrupt enable. This bit is set and cleared by software to enable/disable the analog watchdog 1 interrupt.
  - 0: Analog watchdog 1 interrupt disabled
  - 1: Analog watchdog 1 interrupt enabled
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bit 6 JEOSIE** (rw): End of injected sequence of conversions interrupt enable. This bit is set and cleared by software to enable/disable the end of injected sequence of conversions interrupt.
  - 0: JEOS interrupt disabled
  - 1: JEOS interrupt enabled. An interrupt is generated when the JEOS bit is set.
  - *Note:* The software is allowed to write this bit only when JADSTART = 0 (which ensures that no injected conversion is ongoing).
- **Bit 5 JEOCIE** (rw): End of injected conversion interrupt enable. This bit is set and cleared by software to enable/disable the end of an injected conversion interrupt.
  - 0: JEOC interrupt disabled.
  - 1: JEOC interrupt enabled. An interrupt is generated when the JEOC bit is set.
  - *Note:* The software is allowed to write this bit only when JADSTART = 0 (which ensures that no injected conversion is ongoing).
- **Bit 4 OVRIE** (rw): Overrun interrupt enable. This bit is set and cleared by software to enable/disable the Overrun interrupt of a regular conversion.
  - 0: Overrun interrupt disabled
  - 1: Overrun interrupt enabled. An interrupt is generated when the OVR bit is set.
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 3 EOSIE** (rw): End of regular sequence of conversions interrupt enable. This bit is set and cleared by software to enable/disable the end of regular sequence of conversions interrupt.
  - 0: EOS interrupt disabled
  - 1: EOS interrupt enabled. An interrupt is generated when the EOS bit is set.
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 2 EOCIE** (rw): End of regular conversion interrupt enable. This bit is set and cleared by software to enable/disable the end of a regular conversion interrupt.
  - 0: EOC interrupt disabled.
  - 1: EOC interrupt enabled. An interrupt is generated when the EOC bit is set.
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 1 EOSMPIE** (rw): End of sampling flag interrupt enable for regular conversions. This bit is set and cleared by software to enable/disable the end of the sampling phase interrupt for regular conversions.
  - 0: EOSMP interrupt disabled.
  - 1: EOSMP interrupt enabled. An interrupt is generated when the EOSMP bit is set.
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 0 ADRDYIE** (rw): ADC ready interrupt enable. This bit is set and cleared by software to enable/disable the ADC Ready interrupt.
  - 0: ADRDY interrupt disabled
  - 1: ADRDY interrupt enabled. An interrupt is generated when the ADRDY bit is set.
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).

### 21.6.3 ADC control register (ADC_CR)

Address offset: 0x008. Reset value: 0x2000 0000 (DEEPPWD = 1). Access: ADCAL, JADSTP, ADSTP, JADSTART, ADSTART, ADDIS and ADEN are rs (read/set). DEEPPWD and ADVREGEN are rw.

- **Bit 31 ADCAL** (rs): ADC calibration. This bit is set by software to start the calibration of the ADC. It is cleared by hardware after calibration is complete.
  - 0: Calibration complete
  - 1: Write 1 to calibrate the ADC. Read at 1 means that a calibration in progress.
  - *Note:* The software is allowed to launch a calibration by setting ADCAL only when ADEN = 0. The software is allowed to update the calibration factor by writing ADC_CALFACT only when ADEN = 1 and ADSTART = 0 and JADSTART = 0 (ADC enabled and no conversion is ongoing)
- **Bit 30** Reserved, must be kept at reset value.
- **Bit 29 DEEPPWD** (rw): Deep-power-down enable. This bit is set and cleared by software to put the ADC in Deep-power-down mode.
  - 0: ADC not in Deep-power down
  - 1: ADC in Deep-power-down (default reset state)
  - *Note:* The software is allowed to write this bit only when the ADC is disabled (ADCAL = 0 and ADEN =0).
- **Bit 28 ADVREGEN** (rw): ADC internal voltage regulator enable. This bits is set by software to enable the ADC internal voltage regulator. Before performing any operation such as launching a calibration or enabling the ADC, the ADC voltage regulator must first be enabled and the software must wait for the regulator start-up time.
  - 0: ADC internal voltage regulator disabled
  - 1: ADC internal voltage regulator enabled.
  - For more details about the ADC voltage regulator enable and disable sequences, refer to Section 21.4.6: ADC Deep-power-down mode (DEEPPWD) and ADC voltage regulator (ADVREGEN).
  - The software can program this bit field only when the ADC is disabled (ADCAL=0, JADSTART=0, ADSTART=0, ADSTP=0, ADDIS=0 and ADEN=0).
- **Bits 27:6** Reserved, must be kept at reset value.
- **Bit 5 JADSTP** (rs): ADC stop of injected conversion command. This bit is set by software to stop and discard an ongoing injected conversion (JADSTP command). It is cleared by hardware when the conversion is effectively discarded and the ADC injected sequence and triggers can be reconfigured. The ADC is then ready to accept a new start of injected conversions (JADSTART command). When a software trigger is used, JADSTART bit is cleared by hardware, but JADSTP bit must be programmed to reconfigure the ADC.
  - 0: No ADC stop injected conversion command ongoing
  - 1: Write 1 to stop injected conversions ongoing. Read 1 means that an ADSTP command is in progress.
  - *Note:* In autoinjection mode (JAUTO = 1), setting ADSTP bit aborts both regular and injected conversions (do not use JADSTP).
- **Bit 4 ADSTP** (rs): ADC stop of regular conversion command. This bit is set by software to stop and discard an ongoing regular conversion (ADSTP command). It is cleared by hardware when the conversion is effectively discarded. and the ADC regular sequence and triggers can be re-configured. The ADC is then ready to accept a new start of regular conversions (ADSTART command). When a software trigger is used, ADSTART bit is cleared by hardware. However it is necessary to write ADSTP bit to reconfigure the ADC.
  - 0: No ADC stop regular conversion command ongoing
  - 1: Write 1 to stop ongoing regular conversions. Read 1 means that an ADSTP command is in progress.
  - *Note:* In autoinjection mode (JAUTO = 1), setting ADSTP bit aborts both regular and injected conversions (do not use ADSTP).
  - *Note:* In dual ADC regular simultaneous and interleaved modes, the ADSTP bit of the master ADC must be used to stop regular conversions on both ADCs. The other ADSTP bit is inactive.
- **Bit 3 JADSTART** (rs): ADC start of injected conversion. This bit is set by software to start ADC conversion of injected channels. Depending on the configuration bits JEXTEN[1:0], a conversion starts immediately (software trigger configuration) or once an injected hardware trigger event occurs (hardware trigger configuration).
  - In single conversion mode when software trigger is selected (JEXTSEL = 0x0 and JDISEN = 1), this bit is cleared by hardware immediately after injected conversion starts.
  - In all cases, after the execution of the JADSTP command, this bit and JADSTP are cleared by hardware simultaneously.
  - 0: No ADC injected conversion is ongoing.
  - 1: Write 1 to start injected conversions. Read 1 means that the ADC is operating and eventually converting an injected channel.
  - *Note:* The software is allowed to set JADSTART only when ADEN = 1, ADDIS = 0 and JAUTO = 0 (ADC is enabled and there is no pending request to disable the ADC).
  - *Note:* In autoinjection mode (JAUTO = 1), regular and autoinjected conversions are started by setting ADSTART bit (JADSTART must be kept cleared).
- **Bit 2 ADSTART** (rs): ADC start of regular conversion. This bit is set by software to start ADC conversion of regular channels. Depending on the configuration bits EXTEN[1:0], a conversion starts immediately (software trigger configuration) or once a regular hardware trigger event occurs (hardware trigger configuration).
  - In single conversion mode when software trigger is selected (EXTSEL = 0x0 and DISEN = 1), this bit is cleared by hardware immediately after regular conversion starts.
  - In all cases, after the execution of the ADSTP command, this bit and ADSTP are cleared by hardware simultaneously.
  - 0: No ADC regular conversion is ongoing.
  - 1: Write 1 to start regular conversions. Read 1 means that the ADC is operating and eventually converting a regular channel.
  - *Note:* The software is allowed to set ADSTART only when ADEN = 1 and ADDIS = 0 (ADC is enabled and there is no pending request to disable the ADC).
  - *Note:* In autoinjection mode (JAUTO = 1), regular and autoinjected conversions are started by setting ADSTART bit (JADSTART must be kept cleared)
- **Bit 1 ADDIS** (rs): ADC disable command. This bit is set by software to disable the ADC (ADDIS command) and place it into power-down state (OFF state). It is cleared by hardware once the ADC is effectively disabled (ADEN is also cleared by hardware at this time).
  - 0: no ADDIS command ongoing
  - 1: Write 1 to disable the ADC. Read 1 means that an ADDIS command is in progress.
  - *Note:* The software is allowed to set ADDIS only when ADEN = 1, ADDIS = 0 and both ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bit 0 ADEN** (rs): ADC enable control. This bit is set by software to enable the ADC. The ADC is effectively ready to operate once the ADRDY flag has been set. It is cleared by hardware when the ADC is disabled, after the execution of the ADDIS command.
  - 0: ADC is disabled (OFF state)
  - 1: Write 1 to enable the ADC.
  - *Note:* The software is allowed to set ADEN only when all the bits of ADC_CR registers are cleared (ADCAL = 0, JADSTART = 0, ADSTART = 0, ADSTP = 0, ADDIS = 0 and ADEN = 0), except for ADVREGEN bit which must be set. In addition, the software must wait for the startup time of the voltage regulator.

*Digest note:* Under the usual ST "rs" convention (abbreviations in Section 1.2, not part of this digest), software can read and set these bits but writing 0 has no effect. Each bit's own description says hardware clears it. A read-modify-write of ADC_CR writes back any rs bit that currently reads 1, and writing 1 to an rs bit is a command. The usual approach is to write ADC_CR with only the intended command bit set, keeping DEEPPWD and ADVREGEN at their current values. Section 21.4.9 lists when each control bit may be written. The JADSTP and ADSTP notes are printed as above ("Read 1 means that an ADSTP command" for JADSTP, and "do not use ADSTP" in the ADSTP autoinjection note). Section 21.4.18 says JADSTP must not be used in autoinjection mode. On the ADSTART single-mode software-trigger clearing condition, see the digest note in Section 21.4.16.

### 21.6.4 ADC configuration register (ADC_CFGR1)

Address offset: 0x00C. Reset value: 0x8000 0000. Access: all defined fields rw.

- **Bit 31** Reserved, must be kept at reset value.
- **Bits 30:26 AWD1CH[4:0]** (rw): Analog watchdog 1 channel selection. These bits are set and cleared by software. They select the input channel to be guarded by the analog watchdog.
  - 00000: ADC analog input channel 0 monitored by AWD1
  - 00001: ADC analog input channel 1 monitored by AWD1
  - .....
  - 01101: ADC analog input channel 13 monitored by AWD1
  - Others: reserved, must not be used
  - *Note:* Some channels are not connected physically. Keep the corresponding AWD1CH[4:0] setting to the reset value.
  - *Note:* The channel selected by AWD1CH must be also selected into the SQRi or JSQRi registers. The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bit 25 JAUTO** (rw): Automatic injected group conversion. This bit is set and cleared by software to enable/disable automatic injected group conversion after regular group conversion.
  - 0: Automatic injected group conversion disabled
  - 1: Automatic injected group conversion enabled
  - *Note:* The software is allowed to write this bit only when ADEN = 0.
  - *Note:* When dual mode is enabled (DUAL bits in ADCC_CCR register are not equal to zero), the JAUTO bit of the slave ADC is not valid and controlled by the JAUTO bit of the master ADC.
- **Bit 24 JAWD1EN** (rw): Analog watchdog 1 enable on injected channels. This bit is set and cleared by software
  - 0: Analog watchdog 1 disabled on injected channels
  - 1: Analog watchdog 1 enabled on injected channels
  - *Note:* The software is allowed to write this bit only when JADSTART = 0 (which ensures that no injected conversion is ongoing).
- **Bit 23 AWD1EN** (rw): Analog watchdog 1 enable on regular channels. This bit is set and cleared by software
  - 0: Analog watchdog 1 disabled on regular channels
  - 1: Analog watchdog 1 enabled on regular channels
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 22 AWD1SGL** (rw): Enable the watchdog 1 on a single channel or on all channels. This bit is set and cleared by software to enable the analog watchdog on the channel identified by the AWD1CH[4:0] bits or on all the channels
  - 0: Analog watchdog 1 enabled on all channels
  - 1: Analog watchdog 1 enabled on a single channel
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bit 21** Reserved, must be kept at reset value.
- **Bit 20 JDISCEN** (rw): Discontinuous mode on injected channels. This bit is set and cleared by software to enable/disable discontinuous mode on the injected channels of a group.
  - 0: Discontinuous mode on injected channels disabled
  - 1: Discontinuous mode on injected channels enabled
  - *Note:* The software is allowed to write this bit only when JADSTART = 0 (which ensures that no injected conversion is ongoing).
  - *Note:* It is not possible to use autoinjection mode and discontinuous mode simultaneously: the DISCEN and JDISCEN bits must be kept cleared by software when JAUTO is set.
  - *Note:* When dual mode is enabled (DUAL bits of ADCC_CCR register are not equal to zero), the JDISCEN bit of the slave ADC is not valid and controlled by the JDISCEN bit of the master ADC.
- **Bits 19:17 DISCNUM[2:0]** (rw): Discontinuous mode channel count. These bits are written by software to define the number of regular channels to be converted in discontinuous mode, after receiving an external trigger.
  - 000: 1 channel
  - 001: 2 channels
  - ...
  - 111: 8 channels
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
  - *Note:* When dual mode is enabled (DUAL bits in ADCC_CCR register are not equal to zero), the DISCNUM[2:0] bits of the slave ADC are not valid and controlled by the DISCNUM[2:0] bits of the master ADC.
- **Bit 16 DISCEN** (rw): Discontinuous mode for regular channels. This bit is set and cleared by software to enable/disable discontinuous mode for regular channels.
  - 0: Discontinuous mode for regular channels disabled
  - 1: Discontinuous mode for regular channels enabled
  - *Note:* It is not possible to have both discontinuous mode and continuous mode enabled: DISCEN and CONT cannot both be set (DISCEN takes priority).
  - *Note:* It is not possible to use autoinjection mode and discontinuous mode simultaneously: the DISCEN and JDISCEN bits must be kept cleared by software when JAUTO is set.
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
  - *Note:* When regular dual mode is enabled (DUAL bits in ADCC_CCR register are not equal to zero), the DISCEN bit of the slave ADC is not valid and controlled by the DISCEN bit of the master ADC.
- **Bit 15** Reserved, must be kept at reset value.
- **Bit 14 AUTDLY** (rw): Delayed conversion mode. This bit is set and cleared by software to enable/disable the autodelayed conversion mode.
  - 0: Autodelayed conversion mode off
  - 1: Autodelayed conversion mode on
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
  - *Note:* When dual mode is enabled (DUAL bits in ADCC_CCR register are not equal to zero), the AUTDLY bit of the slave ADC is not valid and controlled by the AUTDLY bit of the master ADC.
- **Bit 13 CONT** (rw): Single / continuous conversion mode for regular conversions. This bit is set and cleared by software. If it is set, regular conversion takes place continuously until it is cleared.
  - 0: Single conversion mode
  - 1: Continuous conversion mode
  - *Note:* It is not possible to have both discontinuous mode and continuous mode enabled: DISCEN and CONT cannot both be set (DISCEN takes priority).
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
  - *Note:* When regular dual mode is enabled (DUAL bits in ADCC_CCR register are not equal to zero), the CONT bit of the slave ADC is not valid and controlled by the CONT bit of the master ADC.
- **Bit 12 OVRMOD** (rw): Overrun mode. This bit is set and cleared by software and configure the way data overrun is managed.
  - 0: ADC_DR register is preserved with the old data when an overrun is detected.
  - 1: ADC_DR register is overwritten with the last conversion result when an overrun is detected.
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bits 11:10 EXTEN[1:0]** (rw): External trigger enable and polarity selection for regular channels. These bits are set and cleared by software to select the external trigger polarity and enable the trigger of a regular group.
  - 00: Hardware trigger detection disabled (conversions can be launched by software)
  - 01: Hardware trigger detection on the rising edge
  - 10: Hardware trigger detection on the falling edge
  - 11: Hardware trigger detection on both the rising and falling edges
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bits 9:5 EXTSEL[4:0]** (rw): External trigger selection for regular group. These bits select the external event used to trigger the start of conversion of a regular group:
  - 00000: adc_ext_trg0
  - 00001: adc_ext_trg1
  - 00010: adc_ext_trg2
  - 00011: adc_ext_trg3
  - 00100: adc_ext_trg4
  - 00101: adc_ext_trg5
  - 00110: adc_ext_trg6
  - 00111: adc_ext_trg7
  - ...
  - 11111: adc_ext_trg31
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 4** Reserved, must be kept at reset value.
- **Bits 3:2 RES[1:0]** (rw): Data resolution. These bits are written by software to select the resolution of the conversion.
  - 00: 12-bit
  - 01: 10-bit
  - 10: 8-bit
  - 11: 6-bit
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bits 1:0 DMNGT[1:0]** (rw): Data management configuration. These bits are set and cleared by software to select how the ADC interface output data are managed.
  - 00: Regular conversion data stored in DR only
  - 01: DMA one-shot mode selected
  - 10: Reserved
  - 11: DMA circular mode selected
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no conversion is ongoing).

*Digest note:* The reset value 0x8000 0000 has bit 31 set, although bit 31 is described as Reserved. Table 153 shows the same reset value. Firmware should preserve bit 31 (read-modify-write) rather than writing 0 to it. The ST CMSIS header stm32c552xx.h defines no field at bit 31.

### 21.6.5 ADC configuration register 2 (ADC_CFGR2)

Address offset: 0x010. Reset value: 0x0000 0000. Access: all defined fields rw.

- **Bits 31:28 LSHIFT[3:0]** (rw): Left shift factor. This bitfield is set and cleared by software to define the left shifting applied to the final result with or without oversampling.
  - 0000: No left shift
  - 0001: 1-bit left shift
  - 0010: 2-bit left shift
  - 0011: 3-bit left shift
  - 0100: 4-bit left shift
  - 0101: 5-bit left shift
  - 0110: 6-bit left shift
  - 0111: 7-bit left shift
  - 1000: 8-bit left shift
  - 1001: 9-bit left shift
  - 1010: 10-bit left shift
  - 1011: 11-bit left shift
  - 1100: 12-bit left shift
  - 1101: 13-bit left shift
  - 1110: 14-bit left shift
  - 1111: 15-bit left shift
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no conversion is ongoing).
- **Bits 27:26** Reserved, must be kept at reset value.
- **Bits 25:16 OVSR[9:0]** (rw): Oversampling ratio. This bitfield is set and cleared by software to define the oversampling ratio.
  - 0: 1x (no oversampling)
  - 1: 2x
  - 2: 3x
  - ...
  - 1023: 1024x
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no conversion is ongoing).
- **Bit 15 SMPTRIG** (rw): Sampling time control trigger mode. This bit is set and cleared by software to enable the sampling time control trigger mode.
  - 0: Sampling time control trigger mode disabled
  - 1: Sampling time control trigger mode enabled
  - If EXTEN[1:0] bits are set to 01, the sampling time starts on the trigger rising edge, and the conversion starts on the trigger falling edge.
  - The SMPTRIG bit must not be set when the BULB bit is set.
  - When EXTEN[1:0] bits are set to 00, set SWTRIG to start the sampling.
  - *Note:* The software is allowed to write this bit only when ADEN = 0. When the discontinuous mode is used, only DISCNUM[2:0] = 000 configuration is compatible with sampling time control trigger mode.
- **Bit 14 SWTRIG** (rw): Software trigger bit for sampling time control trigger mode. This bit is set and cleared by software to trigger the conversion in sampling time control trigger mode.
  - 0: Software trigger starts the conversion for sampling time control trigger mode
  - 1: Software trigger starts the sampling for sampling time control trigger mode
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no conversion is ongoing), SMPTRIG = 1, and EXTEN[0:1] = 00.
- **Bit 13 BULB** (rw): Bulb sampling mode. This bit is set and cleared by software to enable the bulb sampling mode.
  - 0: Bulb sampling mode disabled
  - 1: Bulb sampling mode enabled. The sampling period starts just after the previous end of conversion.
  - BULB bit must not be set when the SWTRIG bit is set.
  - The very first ADC conversion is performed with the sampling time specified in SMPx bits.
  - *Note:* The software is allowed to write this bit only when ADEN = 0. When the discontinuous mode is used, only DISCNUM[2:0] = 000 configuration is compatible with bulb mode.
- **Bits 12:11** Reserved, must be kept at reset value.
- **Bit 10 ROVSM** (rw): Regular oversampling mode. This bit is set and cleared by software to select the regular oversampling mode.
  - 0: Continued mode: When injected conversions are triggered, the oversampling is temporary stopped and continued after the injection sequence (oversampling buffer is maintained during injected sequence)
  - 1: Resumed mode: When injected conversions are triggered, the current oversampling is aborted and resumed from start after the injection sequence (oversampling buffer is zeroed by injected sequence start)
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no conversion is ongoing). It is recommended to clear both JOVSE and GCOMP when ROVSM = 0.
- **Bit 9 TROVS** (rw): Triggered regular oversampling. This bit is set and cleared by software to enable triggered oversampling
  - 0: All oversampled conversions for a channel are done consecutively following a trigger
  - 1: Each oversampled conversion for a channel needs a new trigger
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bits 8:5 OVSS[3:0]** (rw): Oversampling shift. This bitfield is set and cleared by software to define the right shifting applied to the raw oversampling result.
  - 0000: No shift
  - 0001: 1-bit shift
  - 0010: 2-bit shift
  - 0011: 3-bit shift
  - 0100: 4-bit shift
  - 0101: 5-bit shift
  - 0110: 6-bit shift
  - 0111: 7-bit shift
  - 1000: 8-bit shift
  - 1001: 9-bit shift
  - 1010: 10-bit shift
  - Other: reserved, must not be used
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no conversion is ongoing).
- **Bits 4:1** Reserved, must be kept at reset value.
- **Bit 0 ROVSE** (rw): Regular oversampling enable. This bit is set and cleared by software to enable regular oversampling.
  - 0: Regular oversampling disabled
  - 1: Regular oversampling enabled
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 (which ensures that no conversion is ongoing)

*Digest note:* The ST CMSIS header stm32c552xx.h defines ADC_CFGR2_JOVSE at bit 1 ("ADC oversampler enable on scope ADC group injected"), inside the "Bits 4:1 Reserved" range of the RM. Section 21.4.29 also lists JOVSE as an ADC_CFGR2 bit.

### 21.6.6 ADC sample time register 1 (ADC_SMPR1)

Address offset: 0x014. Reset value: 0x0000 0000. Access: all defined fields rw.

Field layout: SMP9[2:0] = bits 29:27, SMP8[2:0] = bits 26:24, SMP7[2:0] = bits 23:21, SMP6[2:0] = bits 20:18, SMP5[2:0] = bits 17:15, SMP4[2:0] = bits 14:12, SMP3[2:0] = bits 11:9, SMP2[2:0] = bits 8:6, SMP1[2:0] = bits 5:3, SMP0[2:0] = bits 2:0 (SMPx at bits 3x+2:3x).

- **Bits 31:30** Reserved, must be kept at reset value.
- **Bits 29:0 SMPx[2:0]** (rw): Channel x sampling time selection (x = 9 to 0). These bits are written by software to select the sampling time individually for each channel. During sample cycles, the channel selection bits must remain unchanged.
  - 000: 3 ADC clock cycles
  - 001: 5 ADC clock cycles
  - 010: 8 ADC clock cycles
  - 011: 13 ADC clock cycles
  - 100: 25 ADC clock cycles
  - 101: 48 ADC clock cycles
  - 110: 139 ADC clock cycles
  - 111: 289 ADC clock cycles
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
  - *Note:* Some channels are not connected physically. Keep the corresponding SMPx[2:0] setting to the reset value.

### 21.6.7 ADC sample time register 2 (ADC_SMPR2)

Address offset: 0x018. Reset value: 0x0000 0000. Access: all defined fields rw.

Field layout: SMP13[2:0] = bits 11:9, SMP12[2:0] = bits 8:6, SMP11[2:0] = bits 5:3, SMP10[2:0] = bits 2:0 (SMPx at bits 3(x-10)+2:3(x-10)).

- **Bits 31:12** Reserved, must be kept at reset value.
- **Bits 11:0 SMPx[2:0]** (rw): Channel x sampling time selection (x = 13 to 10). These bits are written by software to select the sampling time individually for each channel. During sampling cycles, the channel selection bits must remain unchanged.
  - 000: 3 ADC clock cycles
  - 001: 5 ADC clock cycles
  - 010: 8 ADC clock cycles
  - 011: 13 ADC clock cycles
  - 100: 25 ADC clock cycles
  - 101: 48 ADC clock cycles
  - 110: 139 ADC clock cycles
  - 111: 289 ADC clock cycles
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
  - *Note:* Some channels are not connected physically. Keep the corresponding SMPx[2:0] setting to the reset value.

*Digest note:* The ADC1 internal channels use SMP12 (VSENSE, temperature sensor) and SMP13 (VREFINT), both in ADC_SMPR2.

### 21.6.8 ADC channel preselection register (ADC_PCSEL)

Address offset: 0x01C. Reset value: 0x0000 0000. Access: bits 13:0 rw.

- **Bits 31:14** Reserved, must be kept at reset value.
- **Bits 13:0 PCSEL[13:0]** (rw): Channel i (VIN[i]) preselection. These bits are written by software to preselect the input channel I/O to be converted.
  - 0: Input channel i (VIN[i]) is not preselected for conversion, the result of the ADC conversion for this channel is wrong
  - 1: Input channel i (VIN[i]) is preselected for conversion
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing). Configuring the PCSEL bit is not necessary for the internal channels (such as VREFINT).

### 21.6.9 ADC regular sequence register 1 (ADC_SQR1)

Address offset: 0x030. Reset value: 0x0000 0000. Access: all defined fields rw.

- **Bits 31:29** Reserved, must be kept at reset value.
- **Bits 28:24 SQ4[4:0]** (rw): 4th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 4th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 23** Reserved, must be kept at reset value.
- **Bits 22:18 SQ3[4:0]** (rw): 3rd conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 3rd in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 17** Reserved, must be kept at reset value.
- **Bits 16:12 SQ2[4:0]** (rw): 2nd conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 2nd in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 11** Reserved, must be kept at reset value.
- **Bits 10:6 SQ1[4:0]** (rw): 1st conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 1st in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bits 5:4** Reserved, must be kept at reset value.
- **Bits 3:0 LEN[3:0]** (rw): Regular channel sequence length. These bits are written by software to define the total number of conversions in the regular channel conversion sequence.
  - 0000: 1 conversion
  - 0001: 2 conversions
  - ...
  - 1111: 16 conversions
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).

*Note:* Some channels are not connected physically and must not be selected for conversion.

*Digest note:* For a single conversion of channel n, write ADC_SQR1 = (n << 6) | 0 (SQ1 = n, LEN = 0000 for 1 conversion). LEN is in bits 3:0 and SQ1 starts at bit 6.

### 21.6.10 ADC regular sequence register 2 (ADC_SQR2)

Address offset: 0x034. Reset value: 0x0000 0000. Access: all defined fields rw.

- **Bits 31:29** Reserved, must be kept at reset value.
- **Bits 28:24 SQ9[4:0]** (rw): 9th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 9th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 23** Reserved, must be kept at reset value.
- **Bits 22:18 SQ8[4:0]** (rw): 8th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 8th in the regular conversion sequence
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 17** Reserved, must be kept at reset value.
- **Bits 16:12 SQ7[4:0]** (rw): 7th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 7th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 11** Reserved, must be kept at reset value.
- **Bits 10:6 SQ6[4:0]** (rw): 6th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 6th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 5** Reserved, must be kept at reset value.
- **Bits 4:0 SQ5[4:0]** (rw): 5th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 5th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).

*Note:* Some channels are not connected physically and must not be selected for conversion.

### 21.6.11 ADC regular sequence register 3 (ADC_SQR3)

Address offset: 0x038. Reset value: 0x0000 0000. Access: all defined fields rw.

- **Bits 31:29** Reserved, must be kept at reset value.
- **Bits 28:24 SQ14[4:0]** (rw): 14th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 14th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 23** Reserved, must be kept at reset value.
- **Bits 22:18 SQ13[4:0]** (rw): 13th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 13th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 17** Reserved, must be kept at reset value.
- **Bits 16:12 SQ12[4:0]** (rw): 12th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 12th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 11** Reserved, must be kept at reset value.
- **Bits 10:6 SQ11[4:0]** (rw): 11th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 11th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 5** Reserved, must be kept at reset value.
- **Bits 4:0 SQ10[4:0]** (rw): 10th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 10th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).

*Note:* Some channels are not connected physically and must not be selected for conversion.

### 21.6.12 ADC regular sequence register 4 (ADC_SQR4)

Address offset: 0x03C. Reset value: 0x0000 0000. Access: all defined fields rw.

- **Bits 31:11** Reserved, must be kept at reset value.
- **Bits 10:6 SQ16[4:0]** (rw): 16th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 16th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).
- **Bit 5** Reserved, must be kept at reset value.
- **Bits 4:0 SQ15[4:0]** (rw): 15th conversion in regular sequence. These bits are written by software with the channel number (0 to 13) assigned as the 15th in the regular conversion sequence.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 (which ensures that no regular conversion is ongoing).

*Note:* Some channels are not connected physically and must not be selected for conversion.

### 21.6.13 ADC regular data register (ADC_DR)

Address offset: 0x040. Reset value: 0x0000 0000. Access: read-only.

- **Bits 31:0 RDATA[31:0]** (r): Regular data converted. These bits are read-only. They contain the conversion result from the last converted regular channel. The data are left- or right-aligned as described in Section 21.4.25: Data management.

*Digest note:* With the default configuration (RES = 00, LSHIFT = 0, no offset, no oversampling, no gain compensation), a 12-bit result is right-aligned in bits 11:0 and bits 31:12 read 0 (Figure 103). Reading ADC_DR clears EOC (Section 21.6.1).

### 21.6.14 ADC injected sequence register (ADC_JSQR)

Address offset: 0x04C. Reset value: 0x0000 0000. Access: all defined fields rw.

- **Bits 31:27 JSQ4[4:0]** (rw): 4th conversion in the injected sequence. These bits are written by software with the channel number (0 to 13) assigned as the 4th in the injected conversion sequence.
  - *Note:* The software is allowed to write these bits only when JADSTART = 0 (which ensures that no injected conversion is ongoing).
- **Bit 26** Reserved, must be kept at reset value.
- **Bits 25:21 JSQ3[4:0]** (rw): 3rd conversion in the injected sequence. These bits are written by software with the channel number (0 to 13) assigned as the 3rd in the injected conversion sequence.
  - *Note:* The software is allowed to write these bits only when JADSTART = 0 (which ensures that no injected conversion is ongoing).
- **Bit 20** Reserved, must be kept at reset value.
- **Bits 19:15 JSQ2[4:0]** (rw): 2nd conversion in the injected sequence. These bits are written by software with the channel number (0 to 13) assigned as the 2nd in the injected conversion sequence.
  - *Note:* The software is allowed to write these bits only when JADSTART = 0 (which ensures that no injected conversion is ongoing).
- **Bit 14** Reserved, must be kept at reset value.
- **Bits 13:9 JSQ1[4:0]** (rw): 1st conversion in the injected sequence. These bits are written by software with the channel number (0 to 13) assigned as the 1st in the injected conversion sequence.
  - *Note:* The software is allowed to write these bits only when JADSTART = 0 (which ensures that no injected conversion is ongoing).
- **Bits 8:7 JEXTEN[1:0]** (rw): External trigger enable and polarity selection for injected channels. These bits are set and cleared by software to select the external trigger polarity and enable the trigger of an injected group.
  - 00: Hardware trigger detection disabled (conversions can be launched by software)
  - 01: Hardware trigger detection on the rising edge
  - 10: Hardware trigger detection on the falling edge
  - 11: Hardware trigger detection on both the rising and falling edges
  - *Note:* The software is allowed to write these bits only when JADSTART = 0 (which ensures that no injected conversion is ongoing).
- **Bits 6:2 JEXTSEL[4:0]** (rw): External trigger selection for injected group. These bits select the external event used to trigger the start of conversion of an injected group:
  - 00000: adc_jext_trg0
  - 00001: adc_jext_trg1
  - 00010: adc_jext_trg2
  - 00011: adc_jext_trg3
  - 00100: adc_jext_trg4
  - 00101: adc_jext_trg5
  - 00110: adc_jext_trg6
  - 00111: adc_jext_trg7
  - ...
  - 11111: adc_jext_trg31
  - *Note:* The software is allowed to write these bits only when JADSTART = 0 (which ensures that no injected conversion is ongoing).
- **Bits 1:0 JLEN[1:0]** (rw): Injected channel sequence length. These bits are written by software to define the total number of conversions in the injected channel conversion sequence.
  - 00: 1 conversion
  - 01: 2 conversions
  - 10: 3 conversions
  - 11: 4 conversions
  - *Note:* The software is allowed to write these bits only when JADSTART = 0 (which ensures that no injected conversion is ongoing).

*Note:* Some channels are not connected physically and must not be selected for conversion.

### 21.6.15 ADC offset y configuration register (ADC_OFCFGRy)

Address offset: 0x050 + 0x004 * (y -1), (y = 1 to 4). Reset value: 0x0000 0000. Access: all defined fields rw.

- **Bits 31:27 OFFSET_CH[4:0]** (rw): Channel selection for the data offset y. These bits are written by software to define the channel to which the offset programmed in bits OFFSET[21:0] applies.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
  - *Note:* Some channels are not connected physically and must not be selected for the data offset y.
- **Bit 26 SSAT** (rw): Signed saturation enable. This bit is set and cleared by software to enable the signed saturation feature.(see Section : Data register, data alignment and offset (ADC_DR, ADC_JDRy, OFFSETy, OFFSETy_CH, OVSS, LSHIFT, JOVSS, JLSHIFT(a), USAT, SSAT, POSOFF)).
  - 0: Offset is subtracted maintaining the data integrity and extending converted data size (13-bit signed format)
  - 1: Offset is subtracted and result is saturated to maintain the converted data size
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bit 25 USAT** (rw): Unsigned saturation enable. This bit is set and cleared by software to enable the unsigned saturation feature.
  - 0: Offset is subtracted maintaining the data integrity
  - 1: Offset is subtracted and result is saturated to maintain the converted data size
  - *Note:* The software is allowed to write these bits only when ADSTART = and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bit 24 POSOFF** (rw): Positive offset enable. This bit is set and cleared by software to enable the positive offset
  - 0: Negative offset
  - 1: Positive offset
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bits 23:0** Reserved, must be kept at reset value.

*Digest note:* The register map (Table 153) names the channel field OFFSETy_CH[4:0] (OFFSET1_CH ... OFFSET4_CH) and prints POSOFF as "POSOF".

### 21.6.16 ADC offset y register (ADC_OFRy)

Address offset: 0x060 + 0x004 * (y -1), (y= 1 to 4). Reset value: 0x0000 0000. Access: bits 21:0 rw.

- **Bits 31:22** Reserved, must be kept at reset value.
- **Bits 21:0 OFFSET[21:0]** (rw): Data offset y for the channel programmed in OFFSETy_CH[4:0] bits. These bits are written by software to define the offset y to be subtracted from the raw converted data when converting a channel (can be regular or injected). The channel to which applies the data offset y must be programmed in the OFFSETy_CH[4:0] bits. The conversion result can be read from in the ADC_DR (regular conversion) or from in the ADC_JDRyi registers (injected conversion).
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).

### 21.6.17 ADC gain compensation register (ADC_GCOMP)

Address offset: 0x070. Reset value: 0x0000 1000. Access: all defined fields rw.

- **Bit 31 GCOMP** (rw): Gain compensation mode. This bit is set and cleared by software to enable the Gain compensation mode.
  - 0: Regular ADC operation mode
  - 1: Gain compensation enabled and applied on all channels.
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 and JADSTART = 0 (which ensure that no conversion is ongoing)
- **Bits 30:14** Reserved, must be kept at reset value.
- **Bits 13:0 GCOMPCOEFF[13:0]** (rw): Gain compensation coefficient. These bits are set and cleared by software to program the gain compensation coefficient.
  - 00 1000 0000 0000: gain factor of 0.5
  - ...
  - 01 0000 0000 0000: gain factor of 1
  - 10 0000 0000 0000: gain factor of 2
  - 11 0000 0000 0000: gain factor of 3
  - ...
  - The coefficient is divided by 4096 to get the gain factor ranging from 0 to 3.9999756
  - *Note:* This gain compensation is only applied when GCOMP bit is set.
  - *Note:* The software is allowed to write this bit only when ADSTART = 0 and JADSTART = 0 (which ensure that no conversion is ongoing).

### 21.6.18 ADC injected channel y data register (ADC_JDRy)

Address offset: 0x080 + 0x004 * (y - 1), (y = 1 to 4). Reset value: 0x0000 0000. Access: read-only.

- **Bits 31:0 JDATA[31:0]** (r): Injected data. These bits are read-only. They contain the conversion result from injected channel y. The data are left- or right-aligned as described in Section 21.4.25: Data management.

### 21.6.19 ADC analog watchdog 2 configuration register (ADC_AWD2CR)

Address offset: 0x0A0. Reset value: 0x0000 0000. Access: bits 13:0 rw.

- **Bits 31:14** Reserved, must be kept at reset value.
- **Bits 13:0 AWDCH[13:0]** (rw): Analog watchdog 2 channel selection. These bits are set and cleared by software. They enable and select the input channels to be guarded by the analog watchdog 2.
  - AWDCH[i] = 0: ADC analog input channel i is not monitored by AWD2
  - AWDCH[i] = 1: ADC analog input channel i is monitored by AWD2
  - When AWDCH[13:0] = 000..0, the analog Watchdog 2 is disabled
  - *Note:* The channels selected by AWDCH must be also selected in the SQi or JSQi bits.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
  - *Note:* Some channels are not connected physically and must not be selected for the analog watchdog.

### 21.6.20 ADC analog watchdog 3 configuration register (ADC_AWD3CR)

Address offset: 0x0A4. Reset value: 0x0000 0000. Access: bits 13:0 rw.

- **Bits 31:14** Reserved, must be kept at reset value.
- **Bits 13:0 AWDCH[13:0]** (rw): Analog watchdog 3 channel selection. These bits are set and cleared by software. They enable and select the input channels to be guarded by the analog watchdog 3.
  - AWDCH[i] = 0: ADC analog input channel i is not monitored by AWD3
  - AWDCH[i] = 1: ADC analog input channel i is monitored by AWD3
  - When AWDCH[13:0] = 000..0, the analog Watchdog 3 is disabled.
  - *Note:* The channels selected by AWDCH must be also selected in the SQi or JSQi bits.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
  - *Note:* Some channels are not connected physically and must not be selected for the analog watchdog.

### 21.6.21 ADC analog watchdog 1 lower threshold register (ADC_AWD1LTR)

Address offset: 0x0A8. Reset value: 0x0000 0000. Access: bits 22:0 rw.

- **Bits 31:23** Reserved, must be kept at reset value.
- **Bits 22:0 LTR[22:0]** (rw): Analog watchdog 1 lower threshold. These bits are set and cleared by software to define the lower threshold for analog watchdog 1. Refer to Section 21.4.27: Analog window watchdog (AWD1EN, JAWD1EN, AWD1SGL, AWD1CH, AWDCH of ADC_AWD2CR and ADC_AWD3CR, HTR, LTR, AWDFILT).

### 21.6.22 ADC analog watchdog 1 higher threshold register (ADC_AWD1HTR)

Address offset: 0x0AC. Reset value: 0x003F FFFF. Access: bits 31:29 and 22:0 rw.

- **Bits 31:29 AWDFILT[2:0]** (rw): Analog watchdog filtering parameter. These bits are set and cleared by software.
  - 000: No filtering, one detection generates an AWD1 flag or an interrupt
  - 001: two consecutive detections generate an AWD1 flag or an interrupt
  - ...
  - 111: Eight consecutive detections generate an AWD1 flag or an interrupt
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (which ensures that no conversion is ongoing).
- **Bits 28:23** Reserved, must be kept at reset value.
- **Bits 22:0 HTR[22:0]** (rw): Analog watchdog 1 higher threshold. These bits are set and cleared by software to define the higher threshold for analog watchdog 1. Refer to Analog windows watchdog section.

### 21.6.23 ADC analog watchdog 2 lower threshold register (ADC_AWD2LTR)

Address offset: 0x0B0. Reset value: 0x0000 0000. Access: bits 22:0 rw.

- **Bits 31:23** Reserved, must be kept at reset value.
- **Bits 22:0 LTR[22:0]** (rw): Analog watchdog 2 lower threshold. These bits are set and cleared by software to define the lower threshold for analog watchdog 2. Refer to Analog windows watchdog section.

### 21.6.24 ADC analog watchdog 2 higher threshold register (ADC_AWD2HTR)

Address offset: 0x0B4. Reset value: 0x003F FFFF. Access: bits 22:0 rw.

- **Bits 31:23** Reserved, must be kept at reset value.
- **Bits 22:0 HTR[22:0]** (rw): Analog watchdog 2 higher threshold. These bits are set and cleared by software to define the higher threshold for analog watchdog 2. Refer to Analog windows watchdog section.

### 21.6.25 ADC analog watchdog 3 lower threshold register (ADC_AWD3LTR)

Address offset: 0x0B8. Reset value: 0x0000 0000. Access: bits 22:0 rw.

- **Bits 31:23** Reserved, must be kept at reset value.
- **Bits 22:0 LTR[22:0]** (rw): Analog watchdog 3 lower threshold. These bits are set and cleared by software to define the lower threshold for analog watchdog 3. Refer to Analog windows watchdog section.

### 21.6.26 ADC analog watchdog 3 higher threshold register (ADC_AWD3HTR)

Address offset: 0x0BC. Reset value: 0x003F FFFF. Access: bits 22:0 rw.

- **Bits 31:23** Reserved, must be kept at reset value.
- **Bits 22:0 HTR[22:0]** (rw): Analog watchdog 3 higher threshold. These bits are set and cleared by software to define the higher threshold for analog watchdog 3. Refer to Analog windows watchdog section.

*Digest note:* The HTR reset value 0x003F FFFF sets HTR[21:0] to all ones and HTR[22] to 0 (Table 153).

### 21.6.27 ADC calibration factors (ADC_CALFACT)

Address offset: 0x0C4. Reset value: 0x0000 0000. Access: bits 6:0 rw.

- **Bits 31:7** Reserved, must be kept at reset value.
- **Bits 6:0 CALFACT[6:0]** (rw): Calibration factors. These bits can be written by hardware or by software. Once the calibration is complete, they are updated by hardware with the calibration factors. The software can write these bits with a new calibration factor. If the new calibration factor is different from the current one stored into the analog ADC, it is applied once a new conversion is launched.
  - *Note:* The software is allowed to write these bits only when ADSTART = 0 and JADSTART = 0 (ADC is enabled, no conversion is ongoing).

### 21.6.28 ADC option register (ADC_OR)

Address offset: 0x0D0. Reset value: 0x0000 0000.

- **Bits 31:0** Reserved, must be kept at reset value.

*Digest note:* The ST CMSIS header stm32c552xx.h ADC_TypeDef ends at CALFACT (0x0C4) and has no OR member.

## 21.7 ADC common registers

These registers define the control and status registers common to master and slave ADCs.

*Digest note:* On STM32C55xxx the common block is ADC12_COMMON (ADC1 master, ADC2 slave), at 0x4202 8300 according to the ST CMSIS header stm32c552xx.h.

### 21.7.1 ADC common status register (ADCC_CSR)

Address offset: 0x000. Reset value: 0x0000 0000. Access: read-only.

This register provides an image of the flags of the different ADCs. Nevertheless it is read-only and does not allow to clear the different flags. Instead each flag must be cleared by writing 0 to it in the corresponding ADC_ISR register.

*Digest note:* The ADC_ISR flags are rc_w1 (cleared by writing 1), as described in Section 21.6.1. The "writing 0" wording above is as printed.

- **Bits 31:29** Reserved, must be kept at reset value.
- **Bit 28 LDORDY_SLV** (r): ADC internal voltage regulator flag of the slave ADC. This bit is a copy of the LDORDY bit in the corresponding ADC_ISR register.
- **Bits 27:26** Reserved, must be kept at reset value.
- **Bit 25 AWD3_SLV** (r): Analog watchdog 3 flag of the slave ADC. This bit is a copy of the AWD3 bit in the corresponding ADC_ISR register.
- **Bit 24 AWD2_SLV** (r): Analog watchdog 2 flag of the slave ADC. This bit is a copy of the AWD2 bit in the corresponding ADC_ISR register.
- **Bit 23 AWD1_SLV** (r): Analog watchdog 1 flag of the slave ADC. This bit is a copy of the AWD1 bit in the corresponding ADC_ISR register.
- **Bit 22 JEOS_SLV** (r): End of injected sequence flag of the slave ADC. This bit is a copy of the JEOS bit in the corresponding ADC_ISR register.
- **Bit 21 JEOC_SLV** (r): End of injected conversion flag of the slave ADC. This bit is a copy of the JEOC bit in the corresponding ADC_ISR register.
- **Bit 20 OVR_SLV** (r): Overrun flag of the slave ADC. This bit is a copy of the OVR bit in the corresponding ADC_ISR register.
- **Bit 19 EOS_SLV** (r): End of regular sequence flag of the slave ADC. This bit is a copy of the EOS bit in the corresponding ADC_ISR register.
- **Bit 18 EOC_SLV** (r): End of regular conversion of the slave ADC. This bit is a copy of the EOC bit in the corresponding ADC_ISR register.
- **Bit 17 EOSMP_SLV** (r): End of sampling phase flag of the slave ADC. This bit is a copy of the EOSMP2 bit in the corresponding ADC_ISR register.
- **Bit 16 ADRDY_SLV** (r): Slave ADC ready. This bit is a copy of the ADRDY bit in the corresponding ADC_ISR register.
- **Bits 15:13** Reserved, must be kept at reset value.
- **Bit 12 LDORDY_MST** (r): ADC internal voltage regulator flag of the master ADC. This bit is a copy of the LDORDY bit in the corresponding ADC_ISR register.
- **Bits 11:10** Reserved, must be kept at reset value.
- **Bit 9 AWD3_MST** (r): Analog watchdog 3 flag of the master ADC. This bit is a copy of the AWD3 bit in the corresponding ADC_ISR register.
- **Bit 8 AWD2_MST** (r): Analog watchdog 2 flag of the master ADC. This bit is a copy of the AWD2 bit in the corresponding ADC_ISR register.
- **Bit 7 AWD1_MST** (r): Analog watchdog 1 flag of the master ADC. This bit is a copy of the AWD1 bit in the corresponding ADC_ISR register.
- **Bit 6 JEOS_MST** (r): End of injected sequence flag of the master ADC. This bit is a copy of the JEOS bit in the corresponding ADC_ISR register.
- **Bit 5 JEOC_MST** (r): End of injected conversion flag of the master ADC. This bit is a copy of the JEOC bit in the corresponding ADC_ISR register.
- **Bit 4 OVR_MST** (r): Overrun flag of the master ADC. This bit is a copy of the OVR bit in the corresponding ADC_ISR register.
- **Bit 3 EOS_MST** (r): End of regular sequence flag of the master ADC. This bit is a copy of the EOS bit in the corresponding ADC_ISR register.
- **Bit 2 EOC_MST** (r): End of regular conversion of the master ADC. This bit is a copy of the EOC bit in the corresponding ADC_ISR register.
- **Bit 1 EOSMP_MST** (r): End of Sampling phase flag of the master ADC. This bit is a copy of the EOSMP bit in the corresponding ADC_ISR register.
- **Bit 0 ADRDY_MST** (r): Master ADC ready. This bit is a copy of the ADRDY bit in the corresponding ADC_ISR register.

### 21.7.2 ADC common control register (ADCC_CCR)

Address offset: 0x008. Reset value: 0x0000 0000. Access: all defined fields rw.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bit 23 TSEN** (rw): Temperature sensor voltage enable. This bit is set and cleared by software to control VSENSE channel.
  - 0: Temperature sensor channel disabled
  - 1: Temperature sensor channel enabled
  - *Note:* The temperature sensor is not available on all ADC instances. Refer to Section 21.4.4: ADC connectivity for details.
  - *Note:* The software is allowed to write this bit only when ADEN = 0.
- **Bit 22 VREFEN** (rw): VREFINT enable. This bit is set and cleared by software to enable/disable the VREFINT channel.
  - 0: VREFINT channel disabled
  - 1: VREFINT channel enabled
  - *Note:* VREFINT is not available on all ADC instances. Refer to Section 21.4.4: ADC connectivity for details.
  - *Note:* The software is allowed to write this bit only when ADEN = 0.
- **Bits 21:16** Reserved, must be kept at reset value.
- **Bits 15:14 DAMDF[1:0]** (rw): Dual ADC mode data format. This bitfield are set and cleared by software. It specifies the data format in the common data register ADCC_CDR and ADCC_CDR2.
  - 00: Dual ADC mode without data packing (ADCC_CDR and ADCC_CDR2 registers not used).
  - 01: Reserved
  - 10: Data formatting mode for any data width (ADCC_CDR data register is used when the data width is less than 16 bits, otherwise ADCC_CDR2 register is used)
  - 11: Data formatting mode for data width lower that 8 bits (ADCC_CDR data register is used)
  - *Note:* The software is allowed to write these bits only when ADEN = 0 (ADC is disabled).
- **Bit 13** Reserved, must be kept at reset value.
- **Bit 12** Reserved, must be kept at reset value.
- **Bits 11:8 DELAY[3:0]** (rw): Delay between two sampling phases. These bits are set and cleared by software. These bits are used in dual interleaved modes. Refer to for the value of ADC resolution versus DELAY bits values.
  - *Note:* The software is allowed to write these bits only when the ADCs are disabled (ADCAL = 0, JADSTART = 0, ADSTART = 0, ADSTP = 0, ADDIS = 0 and ADEN = 0).
- **Bits 7:5** Reserved, must be kept at reset value.
- **Bits 4:0 DUAL[4:0]** (rw): Dual ADC mode selection. These bits are written by software to select the operating mode.
  - All the ADCs independent:
  - 00000: Independent mode
  - The following settings apply to dual mode, master and slave ADCs working together
  - 00001: Combined regular simultaneous + Injected simultaneous mode
  - 00010: Combined regular simultaneous + Alternate trigger mode
  - 00011: Combined interleaved mode + Injected simultaneous mode
  - 00101: Injected simultaneous mode only
  - 00110: Regular simultaneous mode only
  - 00111: Interleaved mode only
  - 01001: Alternate trigger mode only
  - Others: Reserved
  - All other combinations are reserved and must not be programmed
  - *Note:* The software is allowed to write these bits only when the ADCs are disabled (ADCAL = 0, JADSTART = 0, ADSTART = 0, ADSTP = 0, ADDIS = 0 and ADEN = 0).

*Digest note:* The DELAY description refers to a table without naming it ("Refer to for the value ..."). It means Table 151 (DELAY bits versus ADC resolution).

The register has no clock prescaler or clock-mode field. ADC kernel clock selection and prescaling are in the RCC (see the digest note in Section 21.4.3).

On STM32C55xxx, TSEN and VREFEN control the ADC1 internal channels 12 (VSENSE) and 13 (VREFINT). Both may be written only while ADEN = 0. This chapter does not say whether that means ADEN of ADC1 only or of both ADCs sharing this common register. [unclear in source: which ADC's ADEN gates writes to TSEN/VREFEN]

### 21.7.3 ADC common regular data register for dual mode (ADCC_CDR)

Address offset: 0x00C. Reset value: 0x0000 0000. Access: read-only.

- **Bits 31:16 RDATA_SLV[15:0]** (r): Regular data of the slave ADC. In dual mode, these bits contain the regular data of the slave ADC. Refer to Section 21.4.29: Dual ADC modes. The data alignment is applied as described in Data register, data alignment and offset (ADC_DR, ADC_JDRy, OFFSETy, OFFSETy_CH, OVSS, LSHIFT, JOVSS, JLSHIFT(a), USAT, SSAT, POSOFF))
- **Bits 15:0 RDATA_MST[15:0]** (r): Regular data of the master ADC. In dual mode, these bits contain the regular data of the master ADC. Refer to Section 21.4.29: Dual ADC modes. The data alignment is applied as described in Data register, data alignment and offset (ADC_DR, ADC_JDRy, OFFSETy, OFFSETy_CH, OVSS, LSHIFT, JOVSS, JLSHIFT(a), USAT, SSAT, POSOFF)) In MDMA=0b11 mode, bits 15:8 contains SLV_ADC_DR[7:0], bits 7:0 contains MST_ADC_DR[7:0].

*Digest note:* "MDMA=0b11" is printed as-is and corresponds to DAMDF[1:0] = 0b11.

### 21.7.4 ADC common regular data register for dual mode (ADCC_CDR2)

Address offset: 0x010. Reset value: 0x0000 0000. Access: read-only.

- **Bits 31:0 RDATA_ALT[31:0]** (r): Regular data of the master/slave alternated ADCs. In dual mode, these bits contain the regular 32-bit data of the master and the slave ADC. Refer to Section 21.4.29: Dual ADC modes. The data alignment is applied as described in Data register, data alignment and offset (ADC_DR, ADC_JDRy, OFFSETy, OFFSETy_CH, OVSS, LSHIFT, JOVSS, JLSHIFT(a), USAT, SSAT, POSOFF))

## 21.8 ADC register map

ADC1 and ADC3 are master ADCs.

ADC2 operates as a slave from ADC1.

**Table 153. ADC register map and reset values for each ADC**

| Offset | Register | Reset value | Fields (bit positions) |
|---|---|---|---|
| 0x000 | ADC_ISR | 0x0000 0000 | LDORDY (12), AWD3 (9), AWD2 (8), AWD1 (7), JEOS (6), JEOC (5), OVR (4), EOS (3), EOC (2), EOSMP (1), ADRDY (0) |
| 0x004 | ADC_IER | 0x0000 0000 | LDORDYIE (12), AWD3IE (9), AWD2IE (8), AWD1IE (7), JEOSIE (6), JEOCIE (5), OVRIE (4), EOSIE (3), EOCIE (2), EOSMPIE (1), ADRDYIE (0) |
| 0x08 | ADC_CR | 0x2000 0000 | ADCAL (31), DEEPPWD (29), ADVREGEN (28), JADSTP (5), ADSTP (4), JADSTART (3), ADSTART (2), ADDIS (1), ADEN (0) |
| 0x00C | ADC_CFGR1 | 0x8000 0000 | AWD1CH[4:0] (30:26), JAUTO (25), JAWD1EN (24), AWD1EN (23), AWD1SGL (22), JDISCEN (20), DISCNUM[2:0] (19:17), DISCEN (16), AUTDLY (14), CONT (13), OVRMOD (12), EXTEN[1:0] (11:10), EXTSEL[4:0] (9:5), RES[1:0] (3:2), DMNGT[1:0] (1:0) |
| 0x010 | ADC_CFGR2 | 0x0000 0000 | LSHIFT[3:0] (31:28), OVSR[9:0] (25:16), SMPTRIG (15), SWTRIG (14), BULB (13), ROVSM (10), TROVS (9), OVSS[3:0] (8:5), ROVSE (0) |
| 0x014 | ADC_SMPR1 | 0x0000 0000 | SMP9[2:0] (29:27), SMP8[2:0] (26:24), SMP7[2:0] (23:21), SMP6[2:0] (20:18), SMP5[2:0] (17:15), SMP4[2:0] (14:12), SMP3[2:0] (11:9), SMP2[2:0] (8:6), SMP1[2:0] (5:3), SMP0[2:0] (2:0) |
| 0x018 | ADC_SMPR2 | 0x0000 0000 | SMP13[2:0] (11:9), SMP12[2:0] (8:6), SMP11[2:0] (5:3), SMP10[2:0] (2:0) |
| 0x01C | ADC_PCSEL | 0x0000 0000 | PCSEL[13:0] (13:0) |
| 0x020-0x02C | Reserved | - | Reserved |
| 0x030 | ADC_SQR1 | 0x0000 0000 | SQ4[4:0] (28:24), SQ3[4:0] (22:18), SQ2[4:0] (16:12), SQ1[4:0] (10:6), LEN[3:0] (3:0) |
| 0x034 | ADC_SQR2 | 0x0000 0000 | SQ9[4:0] (28:24), SQ8[4:0] (22:18), SQ7[4:0] (16:12), SQ6[4:0] (10:6), SQ5[4:0] (4:0) |
| 0x038 | ADC_SQR3 | 0x0000 0000 | SQ14[4:0] (28:24), SQ13[4:0] (22:18), SQ12[4:0] (16:12), SQ11[4:0] (10:6), SQ10[4:0] (4:0) |
| 0x03C | ADC_SQR4 | 0x0000 0000 | SQ16[4:0] (10:6), SQ15[4:0] (4:0) |
| 0x040 | ADC_DR | 0x0000 0000 | RDATA[31:0] (31:0) |
| 0x044-0x048 | Reserved | - | Reserved |
| 0x04C | ADC_JSQR | 0x0000 0000 | JSQ4[4:0] (31:27), JSQ3[4:0] (25:21), JSQ2[4:0] (19:15), JSQ1[4:0] (13:9), JEXTEN[1:0] (8:7), JEXTSEL[4:0] (6:2), JLEN[1:0] (1:0) |
| 0x050 | ADC_OFCFGR1 | 0x0000 0000 | OFFSET1_CH[4:0] (31:27), SSAT (26), USAT (25), POSOFF (24) |
| 0x054 | ADC_OFCFGR2 | 0x0000 0000 | OFFSET2_CH[4:0] (31:27), SSAT (26), USAT (25), POSOFF (24) |
| 0x058 | ADC_OFCFGR3 | 0x0000 0000 | OFFSET3_CH[4:0] (31:27), SSAT (26), USAT (25), POSOFF (24) |
| 0x05C | ADC_OFCFGR4 | 0x0000 0000 | OFFSET4_CH[4:0] (31:27), SSAT (26), USAT (25), POSOFF (24) |
| 0x060 | ADC_OFR1 | 0x0000 0000 | OFFSET[21:0] (21:0) |
| 0x064 | ADC_OFR2 | 0x0000 0000 | OFFSET[21:0] (21:0) |
| 0x068 | ADC_OFR3 | 0x0000 0000 | OFFSET[21:0] (21:0) |
| 0x06C | ADC_OFR4 | 0x0000 0000 | OFFSET[21:0] (21:0) |
| 0x070 | ADC_GCOMP | 0x0000 1000 | GCOMP (31), GCOMPCOEFF[13:0] (13:0) |
| 0x074-0x07C | Reserved | - | Reserved |
| 0x080 | ADC_JDR1 | 0x0000 0000 | JDATA[31:0] (31:0) |
| 0x084 | ADC_JDR2 | 0x0000 0000 | JDATA[31:0] (31:0) |
| 0x088 | ADC_JDR3 | 0x0000 0000 | JDATA[31:0] (31:0) |
| 0x08C | ADC_JDR4 | 0x0000 0000 | JDATA[31:0] (31:0) |
| 0x090-0x09C | Reserved | - | Reserved |
| 0x0A0 | ADC_AWD2CR | 0x0000 0000 | AWDCH[13:0] (13:0) |
| 0x0A4 | ADC_AWD3CR | 0x0000 0000 | AWDCH[13:0] (13:0) |
| 0x0A8 | ADC_AWD1LTR | 0x0000 0000 | LTR[22:0] (22:0) |
| 0x0AC | ADC_AWD1HTR | 0x003F FFFF | AWDFILT[2:0] (31:29), HTR[22:0] (22:0) |
| 0x0B0 | ADC_AWD2LTR | 0x0000 0000 | LTR[22:0] (22:0) |
| 0x0B4 | ADC_AWD2HTR | 0x003F FFFF | HTR[22:0] (22:0) |
| 0x0B8 | ADC_AWD3LTR | 0x0000 0000 | LTR[22:0] (22:0) |
| 0x0BC | ADC_AWD3HTR | 0x003F FFFF | HTR[22:0] (22:0) |
| 0x0C0 | Reserved | - | Reserved |
| 0x0C4 | ADC_CALFACT | 0x0000 0000 | CALFACT[6:0] (6:0) |
| 0x0C8-0x0CC | Reserved | - | Reserved |
| 0x0D0 | ADC_OR | 0x0000 0000 | Reserved (31:0) |
| 0x0D4-0x0FC | Reserved | - | Reserved |

*Digest note:* The source table gives reset values bit by bit, and they are collected here as hex words. The source prints the ADC_CR offset as "0x08" (0x008) and the POSOFF bits as "POSOF". The ADC_CR reset row shows ADCAL = 0, DEEPPWD = 1 and ADVREGEN = 0. The ADC_CFGR1 reset row prints the word 0x8000 0000.

**Table 154. ADC register map and reset values (master and slave ADC common registers)**

| Offset | Register | Reset value | Fields (bit positions) |
|---|---|---|---|
| 0x000 | ADCC_CSR | 0x0000 0000 | Slave ADC: LDORDY_SLV (28), AWD3_SLV (25), AWD2_SLV (24), AWD1_SLV (23), JEOS_SLV (22), JEOC_SLV (21), OVR_SLV (20), EOS_SLV (19), EOC_SLV (18), EOSMP_SLV (17), ADRDY_SLV (16); Master ADC: LDORDY_MST (12), AWD3_MST (9), AWD2_MST (8), AWD1_MST (7), JEOS_MST (6), JEOC_MST (5), OVR_MST (4), EOS_MST (3), EOC_MST (2), EOSMP_MST (1), ADRDY_MST (0) |
| 0x004 | Reserved | - | Reserved |
| 0x008 | ADCC_CCR | 0x0000 0000 | TSEN (23), VREFEN (22), DAMDF[1:0] (15:14), DELAY[3:0] (11:8), DUAL[4:0] (4:0) |
| 0x00C | ADCC_CDR | 0x0000 0000 | RDATA_SLV[15:0] (31:16), RDATA_MST[15:0] (15:0) |
| 0x010 | ADCC_CDR2 | 0x0000 0000 | RDATA_ALT[31:0] (31:0) |
| 0x014 | Reserved | - | Reserved |

Refer to Section 2.2: Memory organization for the register boundary addresses.

*Digest note:* The ST CMSIS header stm32c552xx.h agrees with Tables 153 and 154 for every offset and field position, with these exceptions:

- It defines ADC_CFGR2_JOVSE at bit 1, a bit that is reserved in the RM.
- Its ADC_TypeDef has no ADC_OR member at 0x0D0.

Header instance addresses: ADC1 = 0x4202 8000, ADC2 = 0x4202 8100, ADC12_COMMON = 0x4202 8300.
