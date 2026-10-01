# RM0522 Chapter 32: General-purpose timers (TIM2/TIM3/TIM4/TIM5)

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 1133–1258.

*Digest note:* Per the STM32C55xxx datasheet (DS14928), only TIM2 and TIM5 are present on STM32C551/C552; TIM3 and TIM4 do not exist on those parts. This is consistent with Table 306 below (TIM3/TIM4 are only implemented on STM32C59x/C5Ax). All content for TIM3/TIM4 is kept for completeness. On STM32C5 all four timers are 32-bit (Table 307), so TIM_CNT, TIM_ARR and TIM_CCRx are full 32-bit registers on every instance described in this chapter.

## Contents

- 32.1 TIM2/TIM3/TIM4/TIM5 introduction
- 32.2 TIM2/TIM3/TIM4/TIM5 main features
- 32.3 TIM2/TIM3/TIM4/TIM5 implementation
- 32.4 TIM2/TIM3/TIM4/TIM5 functional description
  - 32.4.1 Block diagram
  - 32.4.2 TIM2/TIM3/TIM4/TIM5 pins and internal signals
  - 32.4.3 Time-base unit
  - 32.4.4 Counter modes
  - 32.4.5 External trigger input
  - 32.4.6 Clock selection
  - 32.4.7 Capture/compare channels
  - 32.4.8 Input capture mode
  - 32.4.9 PWM input mode
  - 32.4.10 Forced output mode
  - 32.4.11 Output compare mode
  - 32.4.12 PWM mode
  - 32.4.13 Asymmetric PWM mode
  - 32.4.14 Combined PWM mode
  - 32.4.15 Clock dividers for dead-time generators and digital filters
  - 32.4.16 Clearing the tim_ocxref signal on an external event
  - 32.4.17 One-pulse mode
  - 32.4.18 Retriggerable one-pulse mode
  - 32.4.19 Pulse on compare mode
  - 32.4.20 Encoder interface mode
  - 32.4.21 Encoder with built-in debouncer
  - 32.4.22 Direction bit output
  - 32.4.23 Clock drift measurement
  - 32.4.24 UIF bit remapping
  - 32.4.25 Timer input XOR function
  - 32.4.26 Timers and external trigger synchronization
  - 32.4.27 Timer synchronization
  - 32.4.28 ADC triggers
  - 32.4.29 ADC synchronization
  - 32.4.30 DMA burst mode
  - 32.4.31 TIM2/TIM3/TIM4/TIM5 DMA requests
  - 32.4.32 Debug mode
  - 32.4.33 TIM2/TIM3/TIM4/TIM5 low-power modes
  - 32.4.34 TIM2/TIM3/TIM4/TIM5 interrupts
- 32.5 TIM2/TIM3/TIM4/TIM5 registers
  - 32.5.1 TIM control register 1 (TIM_CR1)
  - 32.5.2 TIM control register 2 (TIM_CR2)
  - 32.5.3 TIM slave mode control register (TIM_SMCR)
  - 32.5.4 TIM DMA/interrupt enable register (TIM_DIER)
  - 32.5.5 TIM status register (TIM_SR)
  - 32.5.6 TIM event generation register (TIM_EGR)
  - 32.5.7 TIM capture/compare mode register 1 (TIM_CCMR1) (input capture view)
  - 32.5.8 TIM capture/compare mode register 1 [alternate] (TIM_CCMR1) (output compare view)
  - 32.5.9 TIM capture/compare mode register 2 (TIM_CCMR2) (input capture view)
  - 32.5.10 TIM capture/compare mode register 2 [alternate] (TIM_CCMR2) (output compare view)
  - 32.5.11 TIM capture/compare enable register (TIM_CCER)
  - 32.5.12 TIM counter (TIM_CNT)
  - 32.5.13 TIM prescaler (TIM_PSC)
  - 32.5.14 TIM autoreload register (TIM_ARR)
  - 32.5.15 to 32.5.18 TIM capture/compare registers 1 to 4 (TIM_CCR1 to TIM_CCR4)
  - 32.5.19 TIM timer encoder control register (TIM_ECR)
  - 32.5.20 TIM timer input selection register (TIM_TISEL)
  - 32.5.21 TIM alternate function register 1 (TIM_AF1)
  - 32.5.22 TIM alternate function register 2 (TIM_AF2)
  - 32.5.23 TIM DMA control register (TIM_DCR)
  - 32.5.24 TIM DMA address for full transfer (TIM_DMAR)
  - 32.5.25 TIM2/TIM3/TIM4/TIM5 register map

## 32.1 TIM2/TIM3/TIM4/TIM5 introduction

The general-purpose timers consist of a 16-bit or 32-bit autoreload counter driven by a programmable prescaler.

They can be used for a variety of purposes, including measuring the pulse lengths of input signals (input capture) or generating output waveforms (output compare and PWM).

Pulse lengths and waveform periods can be modulated from a few microseconds to several milliseconds using the timer prescaler and the RCC clock controller prescalers.

The timers are completely independent, and do not share any resources. They can be synchronized together as described in Section 32.4.27: Timer synchronization.

## 32.2 TIM2/TIM3/TIM4/TIM5 main features

General-purpose TIMx timer features include:

- 16-bit or 32-bit up, down, up/down autoreload counter.
- 16-bit programmable prescaler used to divide (also "on the fly") the counter clock frequency by any factor between 1 and 65535.
- Up to four independent channels for:
  - Input capture.
  - Output compare.
  - PWM generation (edge- and center-aligned modes).
  - One-pulse mode output.
- Synchronization circuit to control the timer with external signals and to interconnect several timers.
- Interrupt/DMA generation on the following events:
  - Update: counter overflow/underflow, counter initialization (by software or internal/external trigger).
  - Trigger event (counter start, stop, initialization, or count by internal/external trigger).
  - Input capture.
  - Output compare.
- Supports incremental (quadrature) encoder and hall-sensor circuitry for positioning purposes.
- Trigger input for external clock or cycle-by-cycle current management.
- ADC synchronization for jitter-free sampling points.

*Digest note:* The feature list says "any factor between 1 and 65535" while 32.4.3 says "between 1 and 65536". The prescaler divides by PSC[15:0] + 1, so the actual range is 1 to 65536.

## 32.3 TIM2/TIM3/TIM4/TIM5 implementation

**Table 306. Timer instance implementation on STM32C5**

| Timer instance | STM32C53x/C54x | STM32C55x/C56x | STM32C59x/C5Ax |
|---|---|---|---|
| TIM2 | X | X | X |
| TIM3 | - | - | X |
| TIM4 | - | - | X |
| TIM5 | X | X | X |

**Table 307. STM32C5 general purpose timers**

| Timer instance | TIM2 | TIM3 | TIM4 | TIM5 |
|---|---|---|---|---|
| Resolution | 32-bit | 32-bit | 32-bit | 32-bit |
| OCREF clear selection | Yes | Yes | Yes | Yes |
| Sources | tim_etrf, tim_ocref_clr | tim_etrf, tim_ocref_clr | tim_etrf, tim_ocref_clr | tim_etrf, tim_ocref_clr |

## 32.4 TIM2/TIM3/TIM4/TIM5 functional description

### 32.4.1 Block diagram

**Figure 325. General-purpose timer block diagram** (described in prose)

- Clocks: tim_ker_ck (kernel clock) and tim_pclk (APB clock). The register interface is a 32-bit APB bus.
- External trigger path: the TIM_ETR pin (tim_etr0) and the internal tim_etr[31:1] sources feed tim_etr_in, which goes through "Polarity selection & edge detector & prescaler" to give tim_etrp, then an "Input filter" to give tim_etrf. tim_etrf goes to the trigger controller (and to the output control as an OCREF clear source).
- Internal triggers tim_itr[27:0] produce tim_itr into the trigger controller. The trigger controller produces tim_trgo (trigger output) and tim_trgi (to the slave mode controller). Other trigger controller inputs are tim_trc, tim_ti1f_ed, tim_ti1fp1 and tim_ti2fp2.
- Slave mode controller: produces reset, enable, up/down and count control for the counter. The Encoder interface takes tim_ti1fp1 and tim_ti2fp2.
- Time base: tim_psc_ck enters the PSC prescaler, which outputs tim_cnt_ck to the CNT counter (+/-). The Auto-reload register is a preload register transferred on U (update event). The counter generates UI (update interrupt) and U. Stop, clear or up/down control comes from the slave controller.
- Each channel x (1 to 4): pin TIM_CHx feeds tim_tix_in0 and internal sources tim_tix_in[15:1] feed the input multiplexer, giving tim_tix. For channel 1, an XOR gate can combine TI inputs into tim_ti1. Each tim_tix passes an "Input filter & edge detector" producing tim_tixfpy signals (channel 1: tim_ti1fp1, tim_ti1fp2; channel 2: tim_ti2fp1, tim_ti2fp2; channel 3: tim_ti3fp3, tim_ti3fp4; channel 4: tim_ti4fp3, tim_ti4fp4) and tim_trc. The selected input tim_icx passes a "Prescaler" into the "Capture/Compare x register" (preloaded, transferred on U). The capture/compare register output feeds the "Output control" via tim_ocxref, which drives tim_ocx on pin TIM_CHx. CCxI marks capture/compare interrupt generation.
- tim_ocref_clr[15:0] (1) is selected into tim_ocref_clr, which together with tim_etrf forms tim_ocref_clr_int to clear tim_ocxref.
- Interrupt and DMA: an IRQ interface generates tim_it; a DMA interface generates tim_cc1_dma, tim_cc2_dma, tim_cc3_dma, tim_cc4_dma, tim_upd_dma and tim_trgi_dma.
- Legend: "Reg" boxes are preload registers transferred to active registers on U event according to control bit; the other symbols mark events and interrupt & DMA outputs.

Notes:

1. This feature is not available on all timers, refer to Section 32.3: TIM2/TIM3/TIM4/TIM5 implementation.

### 32.4.2 TIM2/TIM3/TIM4/TIM5 pins and internal signals

Table 308 and Table 309 in this section summarize the TIM inputs and outputs.

**Table 308. TIM input/output pins**

| Pin name | Signal type | Description |
|---|---|---|
| TIM_CH1, TIM_CH2, TIM_CH3, TIM_CH4 | Input/output | Timer multi-purpose channels. Each channel be used for capture, compare, or PWM. TIM_CH1 and TIM_CH2 can also be used as external clock (below 1/4 of the tim_ker_ck clock), external trigger and quadrature encoder inputs. TIM_CH1, TIM_CH2 and TIM_CH3 can be used to interface with digital hall effect sensors. |
| TIM_ETR | Input | External trigger input. This input can be used as external trigger or as external clock source. This input can receive a clock with a frequency higher than the tim_ker_ck if the tim_etr_in prescaler is used. |

**Table 309. TIM internal input/output signals**

| Internal signal name | Signal type | Description |
|---|---|---|
| tim_ti1_in[15:0], tim_ti2_in[15:0], tim_ti3_in[15:0], tim_ti4_in[15:0] | Input | Internal timer inputs bus. The tim_ti1_in[15:0] and tim_ti2_in[15:0] inputs can be used for capture or as external clock (below 1/4 of the tim_ker_ck clock) and for quadrature encoder signals. |
| tim_etr[31:0] | Input | External trigger internal input bus. These inputs can be used as trigger, external clock or for hardware cycle-by-cycle pulse width control. These inputs can receive clock with a frequency higher than the tim_ker_ck if the tim_etr_in prescaler is used. |
| tim_itr[27:0] | Input | Internal trigger input bus. These inputs can be used for the slave mode controller or as a input clock (below 1/4 of the tim_ker_ck clock). |
| tim_trgo | Output | Internal trigger output. This trigger can trigger other on-chip peripherals. |
| tim_ocref_clr[15:0] | Input | Timer tim_ocref_clr input bus. These inputs can be used to clear the tim_ocxref signals, typically for hardware cycle-by-cycle pulse width control. |
| tim_pclk | Input | Timer APB clock. |
| tim_ker_ck | Input | Timer kernel clock |
| tim_it | Output | Global Timer interrupt, gathering capture/compare, update and break trigger requests. |
| tim_cc1_dma, tim_cc2_dma, tim_cc3_dma, tim_cc4_dma | Output | Timer capture/compare [4:1] dma requests. |
| tim_upd_dma | Output | Timer update dma request. |
| tim_trgi_dma | Output | Timer trigger dma request. |

Tables below list the sources connected to the tim_ti[4:1] input multiplexers.

**Table 310. Interconnect to the tim_ti1 input multiplexer**

| tim_ti1 inputs | TIM2 | TIM3 | TIM4 | TIM5 |
|---|---|---|---|---|
| tim_ti1_in0 | TIM2_CH1 | TIM3_CH1 | TIM4_CH1 | TIM5_CH1 |
| tim_ti1_in1 | comp1_out | comp1_out | comp1_out | comp1_out |
| tim_ti1_in2 | comp2_out(1)/eth_ptp_pps_o(2) | eth_ptp_pps_o | Reserved | Reserved |
| tim_ti1_in3 | LSI | Reserved | Reserved | Reserved |
| tim_ti1_in4 | LSE | Reserved | Reserved | Reserved |
| tim_ti1_in5 | rtc_wut_trg | Reserved | Reserved | Reserved |
| tim_ti1_in6 | TIM5_CH1 | Reserved | Reserved | Reserved |
| tim_ti1_in7 | fdcan1_rxeof_evt | fdcan2_rxeof_evt | Reserved | Reserved |
| tim_ti1_in[15:8] | Reserved | Reserved | Reserved | Reserved |

Notes:

1. comp2_out is only available on STM32C53x/542 devices.
2. eth_ptp_pps_o is only available on STM32C59x/5A3 devices.

**Table 311. Interconnect to the tim_ti2 input multiplexer**

| tim_ti2 inputs | TIM2 | TIM3 | TIM4 | TIM5 |
|---|---|---|---|---|
| tim_ti2_in0 | TIM2_CH2 | TIM3_CH2 | TIM4_CH2 | TIM5_CH2 |
| tim_ti2_in1 | Reserved | Reserved | Reserved | Reserved |
| tim_ti2_in2 | Reserved | Reserved | Reserved | Reserved |
| tim_ti2_in3 | hse_1M_ck | Reserved | Reserved | Reserved |
| tim_ti2_in4 | MCO1 | Reserved | Reserved | Reserved |
| tim_ti2_in5 | MCO2 | Reserved | Reserved | Reserved |
| tim_ti2_in6 | Reserved | Reserved | Reserved | Reserved |
| tim_ti2_in7 | fdcan1_txeof_evt | fdcan2_txeof_evt | Reserved | Reserved |
| tim_ti2_in[15:8] | Reserved | Reserved | Reserved | Reserved |

**Table 312. Interconnect to the tim_ti3 input multiplexer**

| tim_ti3 inputs | TIM2 | TIM3 | TIM4 | TIM5 |
|---|---|---|---|---|
| tim_ti3_in0 | TIM2_CH3 | TIM3_CH3 | TIM4_CH3 | TIM5_CH3 |
| tim_ti3_in1 | Reserved | Reserved | Reserved | Reserved |
| tim_ti3_in[6:2] | Reserved | Reserved | Reserved | Reserved |
| tim_ti3_in7 | fdcan2_rxeof_evt | Reserved | Reserved | Reserved |
| tim_ti3_in[15:8] | Reserved | Reserved | Reserved | Reserved |

**Table 313. Interconnect to the tim_ti4 input multiplexer**

| tim_ti4 inputs | TIM2 | TIM3 | TIM4 | TIM5 |
|---|---|---|---|---|
| tim_ti4_in0 | TIM2_CH4 | TIM3_CH4 | TIM4_CH4 | TIM5_CH4 |
| tim_ti4_in1 | comp1_out | Reserved | Reserved | Reserved |
| tim_ti4_in2 | comp2_out | Reserved | Reserved | Reserved |
| tim_ti4_in[6:3] | Reserved | Reserved | Reserved | Reserved |
| tim_ti4_in7 | fdcan2_txeof_evt | Reserved | Reserved | Reserved |
| tim_ti4_in[15:8] | Reserved | Reserved | Reserved | Reserved |

The table below lists the internal sources connected to the tim_etr input multiplexer.

*Digest note:* The sentence above precedes Table 314, which actually lists the internal trigger (tim_itr) connections, not tim_etr.

**Table 314. TIMx internal trigger connection**

| TIMx | TIM2 | TIM3 | TIM4 | TIM5 |
|---|---|---|---|---|
| tim_itr0 | tim1_trgo | tim1_trgo | tim1_trgo | tim1_trgo |
| tim_itr1 | tim1_trgo2 | tim1_trgo2 | tim1_trgo2 | tim1_trgo2 |
| tim_itr2 | Reserved | tim2_trgo | tim2_trgo | tim2_trgo |
| tim_itr3 | tim3_trgo | Reserved | tim3_trgo | tim3_trgo |
| tim_itr4 | tim4_trgo | tim4_trgo | Reserved | tim4_trgo |
| tim_itr5 | tim5_trgo | tim5_trgo | tim5_trgo | Reserved |
| tim_itr6 | tim8_trgo | tim8_trgo | tim8_trgo | tim8_trgo |
| tim_itr7 | tim8_trgo2 | tim8_trgo2 | tim8_trgo2 | tim8_trgo2 |
| tim_itr8 | tim12_trgo | tim12_trgo | tim12_trgo | tim12_trgo |
| tim_itr9 | tim15_trgo | tim15_trgo | tim15_trgo | tim15_trgo |
| tim_itr10 | tim16_oc1 | tim16_oc1 | tim16_oc1 | tim16_oc1 |
| tim_itr11 | tim17_oc1 | tim17_oc1 | tim17_oc1 | tim17_oc1 |
| tim_itr[27:12] | Reserved | Reserved | Reserved | Reserved |

The table below lists the internal sources connected to the tim_etr input multiplexer.

**Table 315. Interconnect to the tim_etr input multiplexer**

| Timer external trigger input signal | TIM2 | TIM3 | TIM4 | TIM5 |
|---|---|---|---|---|
| tim_etr0 | TIM2_ETR | TIM3_ETR | TIM4_ETR | TIM5_ETR |
| tim_etr1 | comp1_out | comp1_out | comp1_out | comp1_out |
| tim_etr2 | comp2_out | Reserved | Reserved | Reserved |
| tim_etr3 | adc1_awd1 | adc3_awd1 | adc3_awd1 | adc3_awd1 |
| tim_etr4 | adc1_awd2 | adc3_awd2 | adc3_awd2 | adc3_awd2 |
| tim_etr5 | adc1_awd3 | adc3_awd3 | adc3_awd3 | adc3_awd3 |
| tim_etr6 | LSE | Reserved | Reserved | Reserved |
| tim_etr7 | MCO1 | Reserved | Reserved | Reserved |
| tim_etr8 | Reserved | TIM2_ETR | TIM2_ETR | TIM2_ETR |
| tim_etr9 | TIM3_ETR | Reserved | TIM3_ETR | TIM3_ETR |
| tim_etr10 | TIM4_ETR | TIM4_ETR | Reserved | TIM4_ETR |
| tim_etr11 | TIM5_ETR | TIM5_ETR | TIM5_ETR | Reserved |
| tim_etr[31:12] | Reserved | Reserved | Reserved | Reserved |

The table below lists the internal sources connected to the tim_ocref_clr input multiplexer.

**Table 316. Interconnect to the tim_ocref_clr input multiplexer**

| Timer tim_ocref_clr signal | TIM2 | TIM3 | TIM4 | TIM5 |
|---|---|---|---|---|
| tim_ocref_clr0 | comp1_out | comp1_out | comp1_out | comp1_out |
| tim_ocref_clr1 | comp2_out | Reserved | Reserved | Reserved |
| tim_ocref_clr[15:2] | Reserved | Reserved | Reserved | Reserved |

### 32.4.3 Time-base unit

The main block of the programmable timer is a 16-bit/32-bit counter with its related autoreload register. The counter can count up, down or both up and down. The counter clock can be divided by a prescaler.

The counter, the autoreload register and the prescaler register can be written or read by software. This is true even when the counter is running.

The time-base unit includes:

- Counter register (TIM_CNT)
- Prescaler register (TIM_PSC)
- Autoreload register (TIM_ARR)

The autoreload register is preloaded. Writing to or reading from the autoreload register accesses the preload register. The content of the preload register is transferred into the shadow register permanently or at each update event (UEV), depending on the autoreload preload enable bit (ARPE) in TIM_CR1 register. The update event is sent when the counter reaches the overflow (or underflow when down-counting) and if the UDIS bit equals 0 in the TIM_CR1 register. It can also be generated by software. The generation of the update event is described in detail for each configuration.

Note: An update overrun status bit (UIOVRF in TIM_SR register) indicates that an update request occurred while an update interrupt is pending (update interrupt flag set). This bit is useful when debugging closed loop applications, to indicate that:

- the update interrupt service routine is too long with respect to the interval between consecutive update events
- the update interrupt service routine was served too late with respect to the subsequent update event

The counter is clocked by the prescaler output tim_cnt_ck, which is enabled only when the counter enable bit (CEN) in TIM_CR1 register is set (refer also to the slave mode controller description to get more details on counter enabling).

Note: The counter starts counting 1 clock cycle after setting the CEN bit in the TIM_CR1 register.

#### Prescaler description

The prescaler can divide the counter clock frequency by any factor between 1 and 65536. It is based on a 16-bit counter controlled through a 16-bit/32-bit register (in the TIM_PSC register). It can be changed on the fly as this control register is buffered. The new prescaler ratio is taken into account at the next update event.

Figure 326 and Figure 327 give some examples of the counter behavior when the prescaler ratio is changed on the fly:

**Figure 326. Counter timing diagram with prescaler division change from 1 to 2** (described in prose): With CEN high, the counter counts F7, F8, F9, FA, FB, FC, then overflows to 00 (update event). Software writes 1 into TIM_PSC while the counter is running: the prescaler control register changes from 0 to 1 immediately, but the prescaler buffer keeps 0 until the update event, at which point it becomes 1. From then on the prescaler counter alternates 0, 1, 0, 1 ... and tim_cnt_ck ticks every second tim_psc_ck cycle, so the counter advances 00, 01, 02, 03 at half the rate.

**Figure 327. Counter timing diagram with prescaler division change from 1 to 4** (described in prose): Same sequence with the value 3 written into TIM_PSC. The prescaler buffer takes the value 3 at the update event (counter rollover FC to 00); afterwards the prescaler counter cycles 0, 1, 2, 3 and the counter advances once every four tim_psc_ck cycles (00, 01, ...).

### 32.4.4 Counter modes

#### Up-counting mode

In up-counting mode, the counter counts from 0 to the autoreload value (content of the TIM_ARR register), then restarts from 0 and generates a counter overflow event.

An update event can be generated at each counter overflow or by setting the UG bit in the TIM_EGR register (by software or by using the slave mode controller).

The UEV event can be disabled by software by setting the UDIS bit in TIM_CR1 register. This is to avoid updating the shadow registers while writing new values in the preload registers. Then no update event occurs until the UDIS bit has been written to 0. However, the counter restarts from 0, as well as the counter of the prescaler (but the prescale rate does not change). In addition, if the URS bit (update request selection) in TIM_CR1 register is set, setting the UG bit generates an update event UEV but without setting the UIF flag (thus no interrupt or DMA request is sent). This is to avoid generating both update and capture interrupts when clearing the counter on the capture event.

When an update event occurs, all the registers are updated and the update flag (UIF bit in TIM_SR register) is set (depending on the URS bit):

- The buffer of the prescaler is reloaded with the preload value (content of the TIM_PSC register).
- The autoreload shadow register is updated with the preload value (TIM_ARR).

The following figures show some examples of the counter behavior for different clock frequencies when TIM_ARR = 0x36.

**Figure 328. Counter timing diagram, internal clock divided by 1**: tim_cnt_ck equals tim_psc_ck. The counter counts 31, 32, 33, 34, 35, 36, then 00, 01, ... 07. When it rolls over from 36 to 00, a counter overflow pulse, an update event (UEV) pulse are generated and the update interrupt flag (UIF) is set (and stays set until cleared by software).

**Figure 329. Counter timing diagram, internal clock divided by 2**: tim_cnt_ck runs at half of tim_psc_ck. The counter counts 0034, 0035, 0036, 0000, 0001, 0002, 0003; overflow, UEV and UIF set occur at the 0036 to 0000 transition.

**Figure 330. Counter timing diagram, internal clock divided by 4**: tim_cnt_ck runs at a quarter of tim_psc_ck. The counter counts 0035, 0036, 0000, 0001; overflow, UEV and UIF set occur at the 0036 to 0000 transition.

**Figure 331. Counter timing diagram, internal clock divided by N**: tim_cnt_ck pulses once every N tim_psc_ck cycles. The counter goes 1F, 20, 00; overflow, UEV and UIF set occur at the 20 to 00 transition (here ARR = 0x20).

**Figure 332. Counter timing diagram, Update event when ARPE = 0 (TIM_ARR not preloaded)**: The autoreload preload register initially contains FF. While the counter is counting 31, 32, 33 ..., software writes 36 into TIM_ARR; since ARPE = 0 the new value is used immediately, so the counter overflows after reaching 36 (sequence 31 to 36, then 00, 01 ... 07) with overflow, UEV and UIF at the 36 to 00 transition.

**Figure 333. Counter timing diagram, Update event when ARPE = 1 (TIM_ARR preloaded)**: The autoreload preload register and the shadow register both contain F5. Software writes 36 into TIM_ARR while the counter is counting F0, F1 ...; the preload register becomes 36 immediately, but the shadow register keeps F5 until the update event. The counter counts up to F5, overflows to 00 (overflow, UEV, UIF), and at that moment the shadow register is loaded with 36, which becomes the next period.

#### Down-counting mode

In down-counting mode, the counter counts from the autoreload value (content of the TIM_ARR register) down to 0, then restarts from the autoreload value and generates a counter underflow event.

An update event can be generated at each counter underflow or by setting the UG bit in the TIM_EGR register (by software or by using the slave mode controller)

The UEV update event can be disabled by software by setting the UDIS bit in TIM_CR1 register. This is to avoid updating the shadow registers while writing new values in the preload registers. Then no update event occurs until UDIS bit has been written to 0. However, the counter restarts from the current autoreload value, whereas the counter of the prescaler restarts from 0 (but the prescale rate does not change).

In addition, if the URS bit (update request selection) in TIM_CR1 register is set, setting the UG bit generates an update event UEV but without setting the UIF flag (thus no interrupt or DMA request is sent). This is to avoid generating both update and capture interrupts when clearing the counter on the capture event.

When an update event occurs, all the registers are updated and the update flag (UIF bit in TIM_SR register) is set (depending on the URS bit):

- The buffer of the prescaler is reloaded with the preload value (content of the TIM_PSC register).
- The autoreload active register is updated with the preload value (content of the TIM_ARR register). Note that the autoreload is updated before the counter is reloaded, so that the next period is the expected one.

The following figures show some examples of the counter behavior for different clock frequencies when TIM_ARR = 0x36.

**Figure 334. Counter timing diagram, internal clock divided by 1**: The counter counts 05, 04, 03, 02, 01, 00, then reloads 36, 35, 34, 33, 32, 31, 30, 2F. At the 00 to 36 transition, a counter underflow (cnt_udf) pulse and an update event pulse occur and UIF is set.

**Figure 335. Counter timing diagram, internal clock divided by 2**: The counter counts 0002, 0001, 0000, 0036, 0035, 0034, 0033 at half the tim_psc_ck rate; underflow, UEV and UIF set occur at the 0000 to 0036 transition.

**Figure 336. Counter timing diagram, internal clock divided by 4**: tim_cnt_ck pulses once every four tim_psc_ck cycles. The counter values printed in the figure are 0001, 0000, 0000, 0001, with the counter underflow pulse, UEV pulse and UIF setting at the transition out of the first 0000. [unclear in source: the values after underflow are printed as "0000, 0001", which does not match a down-count with TIM_ARR = 0x36; by analogy with Figure 335 they would be 0036, 0035.]

**Figure 337. Counter timing diagram, internal clock divided by N**: The counter goes 20, 1F, ..., 00, then reloads to 36; underflow, UEV and UIF set occur at the 00 to 36 transition.

**Figure 338. Counter timing diagram, Update event** (down-counting, autoreload preload register written): the autoreload preload register initially contains FF; software writes 36 into TIM_ARR while the counter is counting down 05, 04, ... 00. At underflow the counter reloads with 36 and continues 35, 34, 33, 32, 31, 30, 2F; underflow, UEV and UIF set occur at the 00 to 36 transition.

#### Center-aligned mode (up/down-counting)

In center-aligned mode, the counter counts from 0 to the autoreload value (content of the TIM_ARR register) – 1, generates a counter overflow event, then counts from the autoreload value down to 1 and generates a counter underflow event. Then it restarts counting from 0.

Center-aligned mode is active when the CMS bits in TIM_CR1 register are not equal to 00. The output compare interrupt flag of channels configured in output is set when: the counter counts down (center aligned mode 1, CMS = 01), the counter counts up (center aligned mode 2, CMS = 10) the counter counts up and down (center aligned mode 3, CMS = 11).

In this mode, the direction bit (DIR from TIM_CR1 register) cannot be written. It is updated by hardware and gives the current direction of the counter.

The update event can be generated at each counter overflow and at each counter underflow or by setting the UG bit in the TIM_EGR register (by software or by using the slave mode controller) also generates an update event. In this case, the counter restarts counting from 0, as well as the counter of the prescaler.

The UEV update event can be disabled by software by setting the UDIS bit in TIM_CR1 register. This is to avoid updating the shadow registers while writing new values in the preload registers. Then no update event occurs until the UDIS bit has been written to 0. However, the counter continues counting up and down, based on the current autoreload value.

In addition, if the URS bit (update request selection) in TIM_CR1 register is set, setting the UG bit generates an update event UEV but without setting the UIF flag (thus no interrupt or DMA request is sent). This is to avoid generating both update and capture interrupts when clearing the counter on the capture event.

When an update event occurs, all the registers are updated and the update flag (UIF bit in TIM_SR register) is set (depending on the URS bit):

- The buffer of the prescaler is reloaded with the preload value (content of the TIM_PSC register).
- The autoreload active register is updated with the preload value (content of the TIM_ARR register). Note that if the update source is a counter overflow, the autoreload is updated before the counter is reloaded, so that the next period is the expected one (the counter is loaded with the new value).

The following figures show some examples of the counter behavior for different clock frequencies.

**Figure 339. Counter timing diagram, internal clock divided by 1, TIM_ARR = 0x6**: The counter counts 04, 03, 02, 01, 00, 01, 02, 03, 04, 05, 06, 05, 04, 03. A counter underflow pulse occurs at the turnaround at 00, and a counter overflow pulse at the turnaround at 06. UEV pulses and UIF setting occur at both underflow and overflow.

Notes:

1. Here, center-aligned mode 1 is used (for more details refer to Section 32.5.1: TIM control register 1 (TIM_CR1)).

**Figure 340. Counter timing diagram, internal clock divided by 2**: The counter counts 0003, 0002, 0001, 0000, 0001, 0002, 0003 at half rate; underflow, UEV and UIF set occur at the turnaround at 0000.

**Figure 341. Counter timing diagram, internal clock divided by 4, TIM_ARR = 0x36**: The counter counts 0034, 0035, 0036, 0035 at quarter rate; counter overflow, UEV and UIF set occur at the turnaround at 0036.

Notes:

1. Center-aligned mode 2 or 3 is used with a UIF on overflow.

**Figure 342. Counter timing diagram, internal clock divided by N**: The counter counts 20, 1F, ..., 01, 00; underflow, UEV and UIF set occur at the turnaround at 00.

**Figure 343. Counter timing diagram, Update event with ARPE = 1 (counter underflow)**: The autoreload preload and active registers contain FD. While the counter counts down 06, 05, 04, 03, 02, 01, 00, software writes 36 into TIM_ARR (preload becomes 36 immediately). At the underflow (turnaround at 00), UEV occurs, UIF is set and the active register takes 36; the counter then counts up 01, 02, ... 07 towards the new value.

**Figure 344. Counter timing diagram, Update event with ARPE = 1 (counter overflow)**: The autoreload preload and active registers contain FD. While the counter counts up F7, F8, F9, FA, FB, FC, software writes 36 into TIM_ARR (preload becomes 36 immediately). At the overflow (turnaround at FC, since the counter counts up to ARR – 1 = FC), UEV occurs, UIF is set and the active register takes 36; the counter is loaded with the new value and counts down 36, 35, 34, 33, 32, 31, 30, 2F.

### 32.4.5 External trigger input

The timer features an external trigger input tim_etr_in. It can be used as:

- external clock (external clock mode 2, see Section 32.4.6)
- trigger for the slave mode (see Section 32.4.27)
- PWM reset input for cycle-by-cycle current regulation (see Section 32.4.16)

Figure 345 below describes the tim_etr_in input conditioning. The input polarity is defined with the ETP bit in TIM_SMCR register. The trigger frequency can be decreased with the prescalers programmed by the ETPS[1:0] and SETPS[3:0] bitfields and digitally filtered as per the ETF[3:0] bitfield. The resulting signal (tim_etrf) is available for three purposes: as an external clock, to condition the output (typically to reset a PWM output for a current limitation), and as a trigger for the slave mode controller.

**Figure 345. External trigger input block** (described in prose): The TIM_ETR pin (tim_etr0) and the internal sources tim_etr[31:1] (marked "(1)" in the figure) are selected by a multiplexer controlled by TIM_AF1[18:14] (ETRSEL) to form tim_etr_in. tim_etr_in goes to a 2-way selector controlled by TIM_SMCR.ETP (input 0 = tim_etr_in direct, input 1 = inverted tim_etr_in), then to an asynchronous prescaler (/1, /2, /4, /8, set by TIM_SMCR.ETPS[1:0]) giving tim_etrp, then to a digital filter (clock labeled fDTS2 in the figure, setting TIM_SMCR.ETF[3:0]), then to a synchronous prescaler (TIM_SMCR.SETPS[3:0]). The output tim_etrf goes "To the Output mode controller", "To the CK_PSC circuitry" and "To the Slave mode controller".

The external trigger input block features 2 prescalers with different functionalities:

- An asynchronous prescaler (division by 1, 2, 4 or 8), able to process tim_etr_in signals with frequencies above tim_ker_ck
- A linear synchronous prescaler (division by 1,2,3,..15), only able to operate with tim_etrp signal frequencies below tim_ker_ck/3

Note: When tim_etrf is used as PWM reset input for cycle-by-cycle current regulation (see Section 32.4.16), SETPS[3:0] must be set to 0 (no prescaling).

Note: The SETPS[3:0] bitfield is always preloaded: a new value will become active only once an update event has occured.

The tim_etr_in input comes from multiple sources: input pins (default configuration), or internal sources. The selection is done with the ETRSEL[4:0] bitfield in the TIM_AF1 register.

Refer to Section 32.4.2: TIM2/TIM3/TIM4/TIM5 pins and internal signals for the list of sources connected to the etr_in input in the product.


### 32.4.6 Clock selection

The counter clock can be provided by the following clock sources:

- Internal clock (tim_ker_ck).
- External clock mode1: external input pin (tim_ti1 or tim_ti2).
- External clock mode2: external trigger input (tim_etr_in).
- Internal trigger inputs (tim_itr): using one timer as prescaler for another timer, for example, timer 1 can be configured to act as a prescaler for timer 2. Refer to Using one timer as prescaler for another timer for more details.

#### Internal clock source (tim_ker_ck)

If the slave mode controller is disabled (SMS = 000 in the TIM_SMCR register), then the CEN, DIR (in the TIM_CR1 register), and UG bits (in the TIM_EGR register) are actual control bits and can be changed only by software (except UG which remains cleared automatically). As soon as the CEN bit is written to 1, the prescaler is clocked by the internal clock tim_ker_ck.

Figure 346 shows the behavior of the control circuit and the upcounter in normal mode, without prescaler.

**Figure 346. Control circuit in normal mode, internal clock divided by 1**: After CEN is set, tim_cnt_ck and tim_psc_ck follow tim_ker_ck and the counter increments 31, 32, 33, 34, 35, 36. Software then sets UG: an internal "counter initialization" pulse occurs and the counter restarts at 00, then continues 01, 02, 03, 04, 05, 06, 07. UG returns to 0 automatically.

#### External clock source mode 1

This mode is selected when SMS = 111 in the TIM_SMCR register. The counter can count at each rising or falling edge on a selected input.

**Figure 347. tim_ti2 external clock connection example** (described in prose): TIM_CH2 (tim_ti2_in0) and the internal inputs tim_ti2_in[15:1] are selected by TIM_TISEL.TI2SEL[3:0] to form tim_ti2. tim_ti2 passes through a filter (TIM_CCMR1.IC2F, labeled ICF[3:0]) and an edge detector producing tim_ti2f_rising and tim_ti2f_falling; TIM_CCER.CC2P selects one of them (0 = rising, 1 = falling) as tim_ti2fp2. The trigger selector TIM_SMCR.TS[4:0] chooses tim_trgi among tim_itrx (000xx), tim_ti1f_ed (00100), tim_ti1fp1 (00101), tim_ti2fp2 (00110) and tim_etrf (00111) (1). tim_trgi feeds the encoder mode block and external clock mode 1; tim_etrf feeds external clock mode 2; tim_ker_ck feeds internal clock mode. TIM_SMCR.ECE and SMS[2:0] select which of these drives tim_psc_ck.

Notes:

1. [unclear in source: the "(1)" marker next to the TS code list in Figure 347 has no footnote text in the extracted page; TS codes 01000 and above are internal triggers as listed in the TIM_SMCR.TS description.]

For example, to configure the upcounter to count in response to a rising edge on the tim_ti2 input, use the following procedure:

1. Select the proper tim_ti2_in[15:0] source (internal or external) with the TI2SEL[3:0] bits in the TIM_TISEL register.
2. Configure channel 2 to detect rising edges on the tim_ti2 input by writing CC2S= 01 in the TIM_CCMR1 register.
3. Configure the input filter duration by writing the IC2F[3:0] bits in the TIM_CCMR1 register (if no filter is needed, keep IC2F = 0000).

   Note: The capture prescaler is not used for triggering, so it does not need to be configured.

4. Select rising edge polarity by writing CC2P = 0 and CC2NP = 0 in the TIM_CCER register.
5. Configure the timer in external clock mode 1 by writing SMS = 111 in the TIM_SMCR register.
6. Select tim_ti2 as the input source by writing TS = 00110 in the TIM_SMCR register.
7. Enable the counter by writing CEN = 1 in the TIM_CR1 register.

When a rising edge occurs on tim_ti2, the counter counts once and the TIF flag is set.

The delay between the rising edge on tim_ti2 and the actual clock of the counter is due to the resynchronization circuit on tim_ti2 input.

**Figure 348. Control circuit in external clock mode 1**: With CEN set, each rising edge of tim_ti2 produces (after a resynchronization delay) one tim_cnt_ck/tim_psc_ck pulse; the counter goes 34, 35, 36. TIF is set at each counted edge and is cleared by software ("Write TIF=0") between edges.

#### External clock source mode 2

This mode is selected by writing ECE = 1 in the TIM_SMCR register.

The counter can count at each rising or falling edge on the external trigger input tim_etr_in.

Figure 349 gives an overview of the external trigger input block.

**Figure 349. External trigger input block** (described in prose): Same ETR conditioning chain as Figure 345 (TIM_AF1[18:14] source selection of TIM_ETR (tim_etr0) or tim_etr[31:1] (1), ETP polarity, asynchronous prescaler /1, /2, /4, /8 set by ETPS[1:0], digital filter clocked by fDTS set by ETF[3:0], synchronous prescaler set by SETPS[3:0], output tim_etrf). Here tim_etrf is shown feeding "External clock mode 2", alongside tim_trgi (from tim_ti1f, tim_ti2f or others) feeding "Encoder mode" and "External clock mode 1", and tim_ker_ck feeding "Internal clock mode". ECE and SMS[2:0] in TIM_SMCR select which one drives tim_psc_ck.

Notes:

1. Refer to Section 32.4.2: TIM2/TIM3/TIM4/TIM5 pins and internal signals

For example, to configure the upcounter to count each two rising edges on tim_etr_in, use the following procedure:

1. Select the proper tim_etr_in source (internal or external) with the ETRSEL[4:0] bits in the TIM_AF1 register.
2. As no filter is needed in this example, write ETF[3:0] = 0000 in the TIM_SMCR register.
3. Set the prescaler by writing ETPS[1:0] = 01 and SETPS[3:0] = 0 in the TIM_SMCR register.
4. Select rising edge detection on the tim_etr_in by writing ETP = 0 in the TIM_SMCR register.
5. Enable external clock mode 2 by writing ECE = 1 in the TIM_SMCR register.
6. Enable the counter by writing CEN = 1 in the TIM_CR1 register.

The counter counts once each two tim_etr_in rising edges.

The delay between the rising edge on tim_etr_in and the actual clock of the counter is due to the resynchronization circuit on the tim_etrp signal. As a consequence, the maximum frequency that can be correctly captured by the counter is at most ¼ of TIMxCLK frequency. When the ETRP signal is faster, the user must apply a division of the external signal by a proper ETPS prescaler setting.

**Figure 350. Control circuit in external clock mode 2**: With CEN set, tim_etr_in toggles; with ETPS = /2, tim_etrp toggles at half the tim_etr_in frequency (one tim_etrp edge per two tim_etr_in rising edges). tim_etrf follows tim_etrp synchronized to tim_ker_ck. Each rising edge of tim_etrf produces, a couple of tim_ker_ck cycles later, one tim_cnt_ck/tim_psc_ck pulse, and the counter steps 34, 35, 36.

### 32.4.7 Capture/compare channels

Each capture/compare channel is built around a capture/compare register (including a shadow register), an input stage for capture (with digital filter, multiplexing and prescaler) and an output stage (with comparator and output control).

The following figure gives an overview of one capture/compare channel.

The input stage samples the corresponding tim_tix input to generate a filtered signal tim_tixf. Then, an edge detector with polarity selection generates a signal (tim_tixfpy) which can be used as trigger input by the slave mode controller or as the capture command. It is prescaled before the capture register (ICxPS).

**Figure 351. Capture/compare channel (example: channel 1 input stage)** (described in prose): TIM_CH1 (tim_ti1_in0) and tim_ti1_in[15:1] are selected by TIM_TISEL.TI1SEL[3:0]. The selected signal enters a "Filter downcounter" sampled at fDTS and configured by TIM_CCMR1.ICF[3:0] (IC1F), giving tim_ti1f. An edge detector produces tim_ti1f_rising and tim_ti1f_falling; these are ORed to form tim_ti1f_ed ("To the slave mode controller"). A 2-way selector controlled by TIM_CCER.CC1P/CC1NP picks rising (0) or falling (1) to give tim_ti1fp1, which also goes to the slave mode controller. A similar selector on tim_ti2f_rising/tim_ti2f_falling (from channel 2) produces tim_ti2fp1. TIM_CCMR1.CC1S[1:0] selects tim_ic1 from tim_ti1fp1 (01), tim_ti2fp1 (10) or tim_trc (11, from slave mode controller). tim_ic1 passes a divider /1, /2, /4, /8 (TIM_CCMR1.ICPS[1:0], i.e. IC1PSC) to give tim_ic1f, gated by TIM_CCER.CC1E.

The output stage generates an intermediate waveform which is then used for reference: tim_ocxref (active high). The polarity acts at the end of the chain.

**Figure 352. Capture/compare channel 1 main circuit** (described in prose): The APB bus connects through the MCU-peripheral interface (16/32-bit) to the Capture/compare preload register, which exchanges data with the compare shadow register. The shadow register and the Counter feed a comparator producing CNT>CCR1 and CNT=CCR1.

- Input mode: a capture (counter value copied into the shadow register and then into the preload register) occurs when CC1S[1:0] is non-zero (CC1S[1] OR CC1S[0]) AND (an input capture event IC1PS gated by CC1E, OR a software CC1G in TIM_EGR).
- Output mode: a compare transfer (preload register copied into the shadow register) occurs when CC1S[1:0] = 00 (NOR of CC1S[1], CC1S[0]) AND (OC1PE = 0 OR an update event UEV from the time base unit). OC1PE is in TIM_CCMR1.

**Figure 353. Output stage of capture/compare channel (channel 1, idem ch.2, 3 and 4)** (described in prose): A selector controlled by TIM_SMCR.OCCS (1) chooses tim_ocref_clr (0) or tim_etrf (1) as tim_ocref_clr_int, which goes into the Output mode controller together with CNT > CCR1 and CNT = CCR1. The Output mode controller (configured by TIM_CCMR1.OC1CE and OC1M[4:0]) produces tim_oc1ref. An Output selector combines tim_oc1ref and tim_oc2ref (used by combined/asymmetric modes) under OC1M control to produce tim_oc1refc, which also goes "To the master mode controller". tim_oc1refc then passes a selector controlled by TIM_CCER.CC1E (0 selects constant '0', 1 selects tim_oc1refc), then a polarity selector controlled by TIM_CCER.CC1P (0 = non-inverted, 1 = inverted), then an "Output enable circuit" controlled by TIM_CCER.CC1E, giving tim_oc1.

Notes:

1. Available on some instances only. If not available, tim_etrf is directly connected to tim_ocref_clr_int.

The capture/compare block is made of one preload register and one shadow register. Write and read always access the preload register.

In capture mode, captures are actually done in the shadow register, which is copied into the preload register.

In compare mode, the content of the preload register is copied into the shadow register which is compared to the counter.

### 32.4.8 Input capture mode

In input capture mode, the capture/compare registers (TIM_CCRx) are used to latch the value of the counter after a transition detected by the corresponding ICx signal. When a capture occurs, the corresponding CCXIF flag (TIM_SR register) is set and an interrupt or a DMA request can be sent if they are enabled. If a capture occurs while the CCxIF flag was already high, then the overcapture flag CCxOF (TIM_SR register) is set. CCxIF can be cleared by software by writing it to 0 or by reading the captured data stored in the TIM_CCRx register. CCxOF is cleared when it is written with 0.

The following example shows how to capture the counter value in TIM_CCR1 when tim_ti1 input rises. To do this, use the following procedure:

1. Select the proper tim_tix_in[15:0] source (internal or external) with the TI1SEL[3:0] bits in the TIM_TISEL register.
2. Select the active input: TIM_CCR1 must be linked to the tim_ti1 input, so write the CC1S bits to 01 in the TIM_CCMR1 register. As soon as CC1S becomes different from 00, the channel is configured in input and the TIM_CCR1 register becomes read-only.
3. Program the needed input filter duration in relation with the signal connected to the timer (when the input is one of the tim_tix (ICxF bits in the TIM_CCMRx register). Let's imagine that, when toggling, the input signal is not stable during at most five internal clock cycles. We must program a filter duration longer than these five clock cycles. We can validate a transition on tim_ti1 when eight consecutive samples with the new level have been detected (sampled at fDTS frequency). Then write IC1F bits to 0011 in the TIM_CCMR1 register.
4. Select the edge of the active transition on the tim_ti1 channel by writing the CC1P and CC1NP bits to 000 in the TIM_CCER register (rising edge in this case).
5. Program the input prescaler. In this example, the capture is to be performed at each valid transition, so the prescaler is disabled (write IC1PS bits to 00 in the TIM_CCMR1 register).
6. Enable capture from the counter into the capture register by setting the CC1E bit in the TIM_CCER register.
7. If needed, enable the related interrupt request by setting the CC1IE bit in the TIM_DIER register, and/or the DMA request by setting the CC1DE bit in the TIM_DIER register.

When an input capture occurs:

- The TIM_CCR1 register gets the value of the counter on the active transition.
- CC1IF flag is set (interrupt flag). CC1OF is also set if at least two consecutive captures occurred whereas the flag was not cleared.
- An interrupt is generated depending on the CC1IE bit.
- A DMA request is generated depending on the CC1DE bit.

In order to handle the overcapture, it is recommended to read the data before the overcapture flag. This is to avoid missing an overcapture which may happen after reading the flag and before reading the data.

Note: IC interrupt and/or DMA requests can be generated by software by setting the corresponding CCxG bit in the TIM_EGR register.

### 32.4.9 PWM input mode

This mode is used to measure both the period and the duty cycle of a PWM signal connected to single tim_tix input:

- The TIM_CCR1 register holds the period value (interval between two consecutive rising edges).
- The TIM_CCR2 register holds the pulse width (interval between two consecutive rising and falling edges).

This mode is a particular case of input capture mode. The set-up procedure is similar with the following differences:

- Two ICx signals are mapped on the same tim_tix input.
- These two ICx signals are active on edges with opposite polarity.
- One of the two TIxFP signals is selected as trigger input and the slave mode controller is configured in reset mode.

The period and the pulse width of a PWM signal applied on tim_ti1 can be measured using the following procedure:

1. Select the proper tim_tix_in[15:0] source (internal or external) with the TI1SEL[3:0] bits in the TIM_TISEL register.
2. Select the active input for TIM_CCR1: write the CC1S bits to 01 in the TIM_CCMR1 register (tim_ti1 selected).
3. Select the active polarity for tim_ti1fp1 (used both for capture in TIM_CCR1 and counter clear): write the CC1P to 0 and the CC1NP bit to 0 (active on rising edge).
4. Select the active input for TIM_CCR2: write the CC2S bits to 10 in the TIM_CCMR1 register (tim_ti1 selected).
5. Select the active polarity for tim_ti1fp2 (used for capture in TIM_CCR2): write the CC2P bit to 1 and the CC2NP bit to 0 (active on falling edge).
6. Select the valid trigger input: write the TS bits to 00101 in the TIM_SMCR register (tim_ti1fp1 selected).
7. Configure the slave mode controller in reset mode: write the SMS bits to 100 in the TIM_SMCR register.
8. Enable the captures: write the CC1E and CC2E bits to 1 in the TIM_CCER register.

**Figure 354. PWM input mode timing**: tim_ti1 is a PWM signal. On a rising edge of tim_ti1, IC1 captures TIM_CNT into TIM_CCR1 (period, 0004 in the example) and the counter is reset to 0000 (IC2 capture is shown at the same edge in the label "IC1 capture / IC2 capture / reset counter"). The counter then counts 0001, 0002; on the falling edge IC2 captures the counter into TIM_CCR2 (pulse width measurement, 0002). The counter continues 0003, 0004 and the next rising edge again captures into TIM_CCR1 and resets the counter to 0000.

Notes:

1. The PWM input mode can be used only with the TIM_CH1/TIM_CH2 signals due to the fact that only tim_ti1fp1 and tim_ti2fp2 are connected to the slave mode controller.

### 32.4.10 Forced output mode

In output mode (CCxS bits = 00 in the TIM_CCMRx register), each output compare signal (tim_ocxref and then tim_ocx) can be forced to active or inactive level directly by software, independently of any comparison between the output compare register and the counter.

To force an output compare signal (tim_ocxref/tim_ocx) to its active level, the user just needs to write 00101 in the OCxM bits in the corresponding TIM_CCMRx register. Thus tim_ocxref is forced high (tim_ocxref is always active high) and tim_ocx get opposite value to CCxP polarity bit.

For example: CCxP = 0 (tim_ocx active high) => tim_ocx is forced to high level.

tim_ocxref signal can be forced low by writing the OCxM bits to 00100 in the TIM_CCMRx register.

Anyway, the comparison between the TIM_CCRx shadow register and the counter is still performed and allows the flag to be set. Interrupt and DMA requests can be sent accordingly. This is described in the output compare mode section.

### 32.4.11 Output compare mode

This function is used to control an output waveform or indicating when a period of time has elapsed.

When a match is found between the capture/compare register and the counter, the output compare function:

- Assigns the corresponding output pin to a programmable value defined by the output compare mode (OCxM bits in the TIM_CCMRx register) and the output polarity (CCxP bit in the TIM_CCER register). The output pin can keep its level (OCxM = 00000), be set active (OCxM = 00001), be set inactive (OCxM = 00010) or can toggle (OCxM = 00011) on match.
- Sets a flag in the interrupt status register (CCxIF bit in the TIM_SR register).
- Generates an interrupt if the corresponding interrupt mask is set (CCXIE bit in the TIM_DIER register).
- Sends a DMA request if the corresponding enable bit is set (CCxDE bit in the TIM_DIER register, CCDS bit in the TIM_CR2 register for the DMA request selection).

The TIM_CCRx registers can be programmed with or without preload registers using the OCxPE bit in the TIM_CCMRx register.

In output compare mode, the update event UEV has no effect on tim_ocxref and tim_ocx output. The timing resolution is one count of the counter. Output compare mode can also be used to output a single pulse (in one-pulse mode).

#### Procedure

1. Select the counter clock (internal, external, prescaler).
2. Write the desired data in the TIM_ARR and TIM_CCRx registers.
3. Set the CCxIE and/or CCxDE bits if an interrupt and/or a DMA request is to be generated.
4. Select the output mode. For example:
   1. Write OCxM = 00011 to toggle tim_ocx output pin when CNT matches CCRx.
   2. Write OCxPE = 0 to disable preload register.
   3. Write CCxP = 0 to select active high polarity.
   4. Write CCxE = 1 to enable the output.
5. Enable the counter by setting the CEN bit in the TIM_CR1 register.

(Sub-steps 4.1 to 4.4 are a) to d) in the source.)

The TIM_CCRx register can be updated at any time by software to control the output waveform, provided that the preload register is not enabled (OCxPE = 0, else TIM_CCRx shadow register is updated only at the next update event UEV). An example is given in Figure 355.

**Figure 355. Output compare mode, toggle on tim_oc1**: TIM_CCR1 initially holds 003A. The counter counts 0039, 003A, 003B ...; when CNT matches 003A, tim_oc1ref (= tim_oc1) toggles ("Match detected on CCR1, Interrupt generated if enabled"). Software then writes B201h in the CCR1 register (preload disabled, so effective immediately); the counter continues to B200, B201 and at the B201 match tim_oc1ref toggles again.

### 32.4.12 PWM mode

Pulse width modulation mode is used to generate a signal with a frequency determined by the value of the TIM_ARR register and a duty cycle determined by the value of the TIM_CCRx register.

The PWM mode can be selected independently on each channel (one PWM per tim_ocx output) by writing 00110 (PWM mode 1) or 00111 (PWM mode 2) in the OCxM bits in the TIM_CCMRx register. The corresponding preload register must be enabled by setting the OCxPE bit in the TIM_CCMRx register, and eventually the autoreload preload register (in up-counting or center-aligned modes) by setting the ARPE bit in the TIM_CR1 register.

As the preload registers are transferred to the shadow registers only when an update event occurs, before starting the counter, all registers must be initialized by setting the UG bit in the TIM_EGR register.

tim_ocx polarity is software programmable using the CCxP bit in the TIM_CCER register. It can be programmed as active high or active low. tim_ocx output is enabled by the CCxE bit in the TIM_CCER register. Refer to the TIM_CCERx register description for more details.

In PWM mode (1 or 2), TIM_CNT and TIM_CCRx are always compared to determine whether TIM_CCRx ≤ TIM_CNT or TIM_CNT ≤ TIM_CCRx (depending on the direction of the counter). The tim_ocref_clr can be cleared by an external event through the tim_etr_in or the tim_oceref_clr signals. In this case the tim_ocref_clr signal is asserted only:

- After a compare match event.
- When the output compare mode (OCxM bits in TIM_CCMRx register) switches from the "frozen" configuration (no comparison, OCxM = 00000) to one of the PWM modes (OCxM = 00110 or 00111). This forces the PWM by software while the timer is running.

The timer is able to generate PWM in edge-aligned mode or center-aligned mode depending on the CMS bits in the TIM_CR1 register.

*Digest note:* OCxM is a 5-bit field split across the TIM_CCMRx register: OCxM[2:0] at the classic position and OCxM[3]/OCxM[4] in the upper half of the register (see 32.5.8 and 32.5.10). PWM mode 1 = 00110 (OCxM[3] = 0, OCxM[4] = 0, OCxM[2:0] = 110), the same encoding as the classic 3-bit value 110. For a firmware PWM output the minimal sequence implied by this section is: CCxS = 00, OCxM = 00110 (or 00111), OCxPE = 1, ARPE = 1 (optional but recommended), program PSC/ARR/CCRx, set UG in TIM_EGR to load the shadow registers, set CCxE (and CCxP for polarity) in TIM_CCER, then set CEN. These general-purpose timers have no BDTR/MOE main output enable.

#### PWM edge-aligned mode

- Up-counting configuration
- Up-counting is active when the DIR bit in the TIM_CR1 register is low. Refer to Up-counting mode.

  In the following example, we consider PWM mode 1. The reference PWM signal tim_ocxref is high as long as TIM_CNT < TIM_CCRx else it becomes low. If the compare value in TIM_CCRx is greater than the autoreload value (in TIM_ARR) then tim_ocxref is held at 1. If the compare value is 0 then tim_ocxref is held at 0. Figure 356 shows some edge-aligned PWM waveforms in an example where TIM_ARR = 8.

**Figure 356. Edge-aligned PWM waveforms (ARR = 8)**: The counter counts 0, 1, 2, ... 8, 0, 1.

- CCRx = 4: tim_ocxref is high while the counter is 0 to 3, goes low when the counter reaches 4 and stays low through 8, and goes high again when the counter returns to 0. CCxIF is set when the counter reaches 4.
- CCRx = 8: tim_ocxref is high while the counter is 0 to 7, low while the counter is 8, then high again at 0. CCxIF is set when the counter reaches 8.
- CCRx > 8: tim_ocxref is held at '1'. CCxIF is shown set at the start of the period (counter at 0).
- CCRx = 0: tim_ocxref is held at '0'. CCxIF is shown set at the start of the period (counter at 0).

#### Down-counting configuration

- Down-counting is active when DIR bit in TIM_CR1 register is high. Refer to Down-counting mode.

  In PWM mode 1, the reference signal tim_ocxref is low as long as TIM_CNT > TIM_CCRx else it becomes high. If the compare value in TIM_CCRx is greater than the autoreload value in TIM_ARR, then tim_ocxref is held at 100%. PWM is not possible in this mode.

*Digest note:* Other ST reference manuals word the last sentence as "0% PWM is not possible in this mode"; RM0522 prints it without "0%".

#### PWM center-aligned mode

Center-aligned mode is active when the CMS bits in TIM_CR1 register are different from 00 (all the remaining configurations having the same effect on the tim_ocxref/tim_ocx signals). The compare flag is set when the counter counts up, when it counts down or both when it counts up and down depending on the CMS bits configuration. The direction bit (DIR) in the TIM_CR1 register is updated by hardware and must not be changed by software. Refer to Center-aligned mode (up/down-counting).

Figure 357 shows some center-aligned PWM waveforms in an example where:

- TIM_ARR = 8.
- PWM mode is the PWM mode 1.
- The flag is set when the counter counts down corresponding to the center-aligned mode 1 selected for CMS = 01 in TIM_CR1 register.

**Figure 357. Center-aligned PWM waveforms (ARR = 8)**: The counter counts 0, 1, ... 7, 8, 7, 6, ... 1, 0, 1.

- CCRx = 4: tim_ocxref is high while the counter is below 4 (0 to 3 counting up), low from 4 up to 8 and back down to 4, and high again once the counter goes below 4 on the down-count (3, 2, 1, 0). CCxIF: with CMS = 01 it is set at the down-counting match (counter = 4 going down); with CMS = 10 at the up-counting match (counter = 4 going up); with CMS = 11 at both.
- CCRx = 7: tim_ocxref is high from 0 to 6, low while the counter is 7, 8, 7 (around the peak), then high again from 6 downwards. CCxIF (shown for CMS = 10 or 11) is set at the up-counting match at 7.
- CCRx = 8: tim_ocxref is held at '1'. CCxIF is set at the top of the count (counter = 8) for CMS = 01, 10 and 11.
- CCRx > 8: tim_ocxref is held at '1'. CCxIF is set at the top of the count (counter = 8) for CMS = 01, 10 and 11.
- CCRx = 0: tim_ocxref is held at '0'. CCxIF is set when the counter is at 0 (bottom of the count) for CMS = 01, 10 and 11.

Hints on using center-aligned mode:

- When starting in center-aligned mode, the current up-down configuration is used. It means that the counter counts up or down depending on the value written in the DIR bit in the TIM_CR1 register. Moreover, the DIR and CMS bits must not be changed at the same time by the software.
- Writing to the counter while running in center-aligned mode is not recommended as it can lead to unexpected results. In particular:
  - The direction is not updated if a value greater than the autoreload value is written in the counter (TIM_CNT>TIM_ARR). For example, if the counter was counting up, it continues to count up.
  - The direction is updated if 0 or the TIM_ARR value is written in the counter but no update event UEV is generated.
- The safest way to use center-aligned mode is to generate an update by software (setting the UG bit in the TIM_EGR register) just before starting the counter and not to write the counter while it is running.

#### Dithering mode

The PWM mode effective resolution can be increased by enabling the dithering mode, using the DITHEN bit in the TIM_CR1 register. This applies to both the CCR (for duty cycle resolution increase) and ARR (for PWM frequency resolution increase).

The operating principle is to have the actual CCR (or ARR) value slightly changed (adding or not one timer clock period) over 16 consecutive PWM periods, with predefined patterns. This allows a 16-fold resolution increase, considering the average duty cycle or PWM period. Figure 358 presents the dithering principle applied to four consecutive PWM cycles.

**Figure 358. Dithering principle**: Four consecutive PWM cycles each with a high time of 7 clock cycles and a low time of 5 are shown for five average duty cycles. DC = 7/5: no cycle is extended. DC = (7+¼)/5: one of the four cycles has its high time extended by 1 clock cycle. DC = (7+½)/5: two of the four cycles are extended by 1 clock cycle. DC = (7+¾)/5: three of the four cycles are extended. DC = 8/5: all four cycles are extended by 1 clock cycle.

When the dithering mode is enabled, the register coding is changed as following (see Figure 359 for example):

- The four LSBs are coding for the enhanced resolution part (fractional part).
- The MSBs are left-shifted by four places and are coding for the base value. In 16-bit mode, the 16-bit format is maintained.

Note: The following sequence must be followed when resetting the DITHEN bit:

1. CEN and ARPE bits must be reset.
2. The DITHEN bit must be reset.
3. The CCIF flags must be cleared.
4. The CEN bit can be set (eventually with ARPE = 1).

**Figure 359. Data format and register coding in dithering mode**:

- Register format in dithering mode (32-bit): bits 31:4 = MSB: 28-bits, integer part; bits 3:0 = LSB: 4-bits fractional part.
- Register format in dithering mode (16-bit): bits 31:20 = Reserved; bits 19:4 = MSB: 16-bits, integer part; bits 3:0 = LSB: 4-bits fractional part.
- Example: register value 326 (bits 19:0) = integer part 20 and fractional part 6. "Base compare value is 20 during 16 periods"; "Additional 6 cycles are spread over the 16 periods".

*Digest note:* In the example, 326 decimal = 0x146 = (20 << 4) | 6.

The minimum frequency is given by the following formula:

- Resolution = F_Tim / F_pwm ⇒ F_pwmMin = F_Tim / Max_Resolution
- Dithering mode disabled: F_pwmMin = F_Tim / 65536
- Dithering mode (16-bit timer): F_pwmMin = F_Tim / (65535 + 15/16)
- Dithering mode (32-bit timer): F_pwmMin = F_Tim / (268435454 + 15/16)

Note: For 16-bit timers, the maximum TIM_ARR and TIM_CCRy values are limited to 0xFFFEF in dithering mode (corresponds to 65534 for the integer part and 15 for the dithered part). For 32-bit timers, the maximum TIM_ARR and TIM_CCRy values are limited to 0xFFFFFFEF in dithering mode (corresponds to 264435454 for the integer part and 15 for the dithered part).

*Digest note:* 0xFFFFFFEF >> 4 = 0xFFFFFFE = 268435454; the "264435454" in the note above is a typo in the source (the formula above uses 268435454).

As shown on Figure 360 and Figure 361, the dithering mode is used to increase the PWM resolution.

**Figure 360. PWM resolution vs frequency (16-bit mode)**: Plot of PWM resolution versus PWM frequency. Without dithering, the maximum resolution is 16-bit; with dithering it reaches 20-bit. In both cases resolution decreases as PWM frequency increases, starting from FPWM min.

**Figure 361. PWM resolution vs frequency (32-bit mode)**: Plot of PWM resolution versus PWM frequency, capped at 32-bit. The "No Dithering" curve starts at F(cnt) min no dithering; the "Dithering" curve starts at a higher F(cnt) min with dithering (since in 32-bit mode the integer part is limited to 28 bits).

The duty cycle and/or period changes are spread over 16 consecutive periods, as described in Figure 362.

**Figure 362. PWM dithering pattern**: Over 16 counter periods:

| Register value | Effective value in periods 1 to 16 |
|---|---|
| CCR1 = 322 (20 + 2/16) | 21, 20, 20, 20, 20, 20, 20, 20, 21, 20, 20, 20, 20, 20, 20, 20 |
| CCR2 = 326 (20 + 6/16) | 21, 20, 21, 20, 21, 20, 20, 20, 21, 20, 21, 20, 21, 20, 20, 20 |
| CCR3 = 334 (20 + 14/16) | 21, 21, 21, 21, 21, 21, 21, 20, 21, 21, 21, 21, 21, 21, 21, 20 |
| CCR4 = 336 (21 + 0/16) | 21 in all 16 periods |
| ARR = 643 (40 + 3/16) | 41, 40, 40, 40, 41, 40, 40, 40, 41, 40, 40, 40, 40, 40, 40, 40 |

The autoreload and compare values increments are spread following specific patterns described in Table 317. The dithering sequence is done to have increments distributed as evenly as possible and minimize the overall ripple.

**Table 317. CCR and ARR register change dithering pattern**

| LSB value | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0000 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 0001 | +1 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 0010 | +1 | - | - | - | - | - | - | - | +1 | - | - | - | - | - | - | - |
| 0011 | +1 | - | - | - | +1 | - | - | - | +1 | - | - | - | - | - | - | - |
| 0100 | +1 | - | - | - | +1 | - | - | - | +1 | - | - | - | +1 | - | - | - |
| 0101 | +1 | - | +1 | - | +1 | - | - | - | +1 | - | - | - | +1 | - | - | - |
| 0110 | +1 | - | +1 | - | +1 | - | - | - | +1 | - | +1 | - | +1 | - | - | - |
| 0111 | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | - | - |
| 1000 | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - |
| 1001 | +1 | +1 | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - |
| 1010 | +1 | +1 | +1 | - | +1 | - | +1 | - | +1 | +1 | +1 | - | +1 | - | +1 | - |
| 1011 | +1 | +1 | +1 | - | +1 | +1 | +1 | - | +1 | +1 | +1 | - | +1 | - | +1 | - |
| 1100 | +1 | +1 | +1 | - | +1 | +1 | +1 | - | +1 | +1 | +1 | - | +1 | +1 | +1 | - |
| 1101 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | - | +1 | +1 | +1 | - | +1 | +1 | +1 | - |
| 1110 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | - | +1 | +1 | +1 | +1 | +1 | +1 | +1 | - |
| 1111 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | - |

(Columns 1 to 16 are the PWM period number.)

The dithering mode is also available in center-aligned PWM mode (CMS bits in TIM_CR1 register are not equal to 00). In this case, the dithering pattern is applied over eight consecutive PWM periods, considering the up and down-counting phases as shown in Figure 363.

**Figure 363. Dithering effect on duty cycle in center-aligned PWM mode**: Three triangular counter waveforms with a compare threshold and the resulting PWM pulse: "No dithering" (pulse symmetric around the counter peak), "Dithering up" (the compare value is incremented during the up-counting phase, so the pulse starts one clock later on the rising side) and "Dithering down" (the compare value is incremented during the down-counting phase, so the pulse ends one clock later on the falling side).

Table 318 shows how the dithering pattern is added in center-aligned PWM mode.

**Table 318. CCR register change dithering pattern in center-aligned PWM mode**

| LSB value | 1 Up | 1 Dn | 2 Up | 2 Dn | 3 Up | 3 Dn | 4 Up | 4 Dn | 5 Up | 5 Dn | 6 Up | 6 Dn | 7 Up | 7 Dn | 8 Up | 8 Dn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0000 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 0001 | +1 | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - |
| 0010 | +1 | - | - | - | - | - | - | - | +1 | - | - | - | - | - | - | - |
| 0011 | +1 | - | - | - | +1 | - | - | - | +1 | - | - | - | - | - | - | - |
| 0100 | +1 | - | - | - | +1 | - | - | - | +1 | - | - | - | +1 | - | - | - |
| 0101 | +1 | - | +1 | - | +1 | - | - | - | +1 | - | - | - | +1 | - | - | - |
| 0110 | +1 | - | +1 | - | +1 | - | - | - | +1 | - | +1 | - | +1 | - | - | - |
| 0111 | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | - | - |
| 1000 | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - |
| 1001 | +1 | +1 | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - | +1 | - |
| 1010 | +1 | +1 | +1 | - | +1 | - | +1 | - | +1 | +1 | +1 | - | +1 | - | +1 | - |
| 1011 | +1 | +1 | +1 | - | +1 | +1 | +1 | - | +1 | +1 | +1 | - | +1 | - | +1 | - |
| 1100 | +1 | +1 | +1 | - | +1 | +1 | +1 | - | +1 | +1 | +1 | - | +1 | +1 | +1 | - |
| 1101 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | - | +1 | +1 | +1 | - | +1 | +1 | +1 | - |
| 1110 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | - | +1 | +1 | +1 | +1 | +1 | +1 | +1 | - |
| 1111 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | +1 | - |

(Column headers give the PWM period number 1 to 8 and the up-counting (Up) or down-counting (Dn) phase.)

### 32.4.13 Asymmetric PWM mode

Asymmetric mode allows two center-aligned PWM signals to be generated with a programmable phase shift. While the frequency is determined by the value of the TIM_ARR register, the duty cycle and the phase-shift are determined by a pair of TIM_CCRx registers. One register controls the PWM during up-counting, the second during down-counting, so that PWM is adjusted every half PWM cycle, for instance:

- tim_oc1refc is controlled by TIM_CCR1 and TIM_CCR2.
- tim_oc3refc is controlled by TIM_CCR3 and TIM_CCR4.

Figure 364 shows an example of signals that can be generated using asymmetric PWM mode (channels 1 to 4 are configured in asymmetric PWM mode 2).

**Figure 364. Generation of two phase-shifted PWM signals with 50% duty cycle**: The counter counts 0, 1, ... 8, 7, ... 0, 1 (center-aligned, ARR = 8). With CCR1 = 0 and CCR2 = 8, tim_oc1refc is low during the whole up-count (0 to 7) and high from 8 through the whole down-count, going low again when the counter reaches 0. With CCR3 = 3 and CCR4 = 5, tim_oc3refc is low for 0 to 2, high from 3 up to 8 and down to 6, and low from 5 down to 0 and up to 2. Both signals have a 50% duty cycle and are phase-shifted by 3 counts.

Multiple asymmetric PWM modes are available to combine different pairs of TIM_CCRx registers and generate the required waveform, as listed in Table 319. The selection is done with the OCxM[4:0] bitfield in TIM_CCMRx registers. For each pair of TIM_CCRx registers, two options are given (e.g. Asymmetric PWM mode 1 and 2), one being in PWM mode 1 (channel active as long as the counter is below the TIM_CCRx value), the other one in PWM mode 2 (channel active when the counter is above the TIM_CCRx value).

For the asymmetric PWM modes 1 and 2, it is mandatory to have the same PWM mode for both channels. For instance, it is mandatory to have OC1M[4:0] = OC2M[4:0] = 01110 for the asymmetric PWM mode 1 on oc1refc.

For the asymmetric PWM modes 7 to 10, it is mandatory to have opposite PWM mode for both channels (one being in PWM mode 1 and the other in PWM mode 2). Refer to Table 319 for configuration.

Note: The OCxM[4:0] bitfield is split into two parts for compatibility reasons, the most significant bits are not contiguous with the three least significant ones.

When a given channel is used as asymmetric PWM channel, its secondary channel can also be used. For instance, if an tim_oc1refc signal is generated on channel 1 (Asymmetric PWM mode 1), it is possible to output either the regular tim_oc2ref signal on channel 2, or an tim_oc2refc signal resulting from asymmetric PWM mode 2.

**Table 319. Asymmetric PWM modes(1)**

| Output compare mode | OCxM[4:0] | oc1refc | oc2refc | oc3refc | oc4refc | PWM Mode(2) |
|---|---|---|---|---|---|---|
| Asymmetric PWM mode 1 | 01110 | oc1ref (up-counting), oc2ref (down-counting) | oc1ref (up-counting), oc2ref (down-counting) | oc3ref (up-counting), oc4ref (down-counting) | oc3ref (up-counting), oc4ref (down-counting) | 1 |
| Asymmetric PWM mode 2 | 01111 | oc1ref (up-counting), oc2ref (down-counting) | oc1ref (up-counting), oc2ref (down-counting) | oc3ref (up-counting), oc4ref (down-counting) | oc3ref (up-counting), oc4ref (down-counting) | 2 |
| Asymmetric PWM mode 7 | 10110 | - | - | oc3refc = 1 (up-counting), oc3ref OR oc4ref (down-counting) | - | 1(3) |
| Asymmetric PWM mode 8 | 10111 | - | - | oc3refc = 0 (up-counting), oc3ref AND oc4ref (down-counting) | - | 2(4) |
| Asymmetric PWM mode 9 | 11000 | - | - | oc3ref OR oc4ref (up-counting), oc3refc = 1 (down-counting) | - | 1(3) |
| Asymmetric PWM mode 10 | 11001 | - | - | oc3ref AND oc4ref (up-counting), oc3refc = 0 (down-counting) | - | 2(4) |

Notes:

1. Asymmetric PWM mode 7 to 10 are only available on OC3M.
2. PWM mode 1: channel active as long as the counter is below the TIM_CCRx value. PWM mode 2: channel active when the counter is above the TIM_CCRx value. Unless explicitly mentioned, the PWM mode must be identical for the two channels used for the asymmetric mode.
3. oc4ref must be programmed in PWM mode 1.
4. oc4ref must be programmed in PWM mode 2.

### 32.4.14 Combined PWM mode

Combined PWM mode allows two edge or center-aligned PWM signals to be generated with programmable delay and phase shift between respective pulses. While the frequency is determined by the value of the TIM_ARR register, the duty cycle and delay are determined by the two TIM_CCRx registers. The resulting signals, tim_ocxrefc, are made of an OR or AND logical combination of two reference PWMs,

- tim_oc1refc (or tim_oc2refc) is controlled by TIM_CCR1 and TIM_CCR2
- tim_oc3refc (or tim_oc4refc) is controlled by TIM_CCR3 and TIM_CCR4

Table 320 summarizes different combinations of PWM combined mode:

**Table 320. Combined PWM mode overview**

| Output compare mode | OCxM[4:0] | oc1refc | oc2refc | oc3refc | oc4refc | PWM mode(1) |
|---|---|---|---|---|---|---|
| Combined PWM mode 1 | 01100 | oc1ref OR oc2ref | oc1ref OR oc2ref | oc3ref OR oc4ref | oc3ref OR oc4ref | 1 |
| Combined PWM mode 2 | 01101 | oc1ref AND oc2ref | oc1ref AND oc2ref | oc3ref AND oc4ref | oc3ref AND oc4ref | 2 |

Notes:

1. PWM mode 1: channel active as long as the counter is below the TIM_CCRx value). PWM mode 2: channel active when the counter is above the TIM_CCRx value.

Combined PWM mode can be selected independently on two channels (one tim_ocx output per pair of CCR registers) by writing 01100 (combined PWM mode 1) or 01101 (combined PWM mode 2) in the OCxM bits in the TIM_CCMRx register.

When a given channel is used as combined PWM channel, its secondary channel must be configured in the opposite PWM mode (for instance, one in PWM mode 1 and the other in PWM mode 2).

Note: The OCxM[4:0] bitfield is split into two parts for compatibility reasons, the most significant bits are not contiguous with the three least significant ones.

Figure 365 shows an example of signals that can be generated using combined PWM mode, obtained with the following configuration:

- Channel 1 is configured in combined PWM mode 1.
- Channel 2 is configured in PWM mode 2.
- Channel 3 is configured in combined PWM mode 2.
- Channel 4 is configured in PWM mode 1.

**Figure 365. Combined PWM mode on channels 1 and 3**: Edge-aligned up-counting sawtooth with two thresholds per pair.

- Top (combined PWM mode 1: tim_oc1refc = tim_oc1ref OR tim_oc2ref), with CCR1 < CCR2: tim_oc1ref (PWM mode 1) is high from the start of the period until the counter reaches CCR1; tim_oc2ref (PWM mode 2) is high from CCR2 until the end of the period. tim_oc1refc is therefore high except for a low pulse between CCR1 and CCR2.
- Bottom (combined PWM mode 2: tim_oc3refc = tim_oc3ref AND tim_oc4ref), with CCR3 < CCR4: tim_oc3ref (PWM mode 2) is high from CCR3 until the end of the period; tim_oc4ref (PWM mode 1) is high from the start of the period until CCR4. tim_oc3refc is therefore high only between CCR3 and CCR4.

### 32.4.15 Clock dividers for dead-time generators and digital filters

The the digital filters (for tim_etr_in, tim_tix) are using a DTS_ck clock (with a tDTS period), derived from the tim_ker_ck clock.

A prescaler can decrease the frequency to extend the DTS_ck clock period programmed with the CKD[1:0] bitfield in the TIM_CR1 register. A second prescaler can decrease the resulting DTS_ck clock to extend the digital filters range, with the CKD2[3:0] bitfield in the TIM_CR1 register.

**Figure 366. Clock prescalers for dead-time and digital filters**: tim_ker_ck (period ttim_ker_ck) enters a prescaler controlled by TIM_CR1.CKD[1:0] that produces DTS_ck (period tDTS); DTS_ck enters a second prescaler controlled by TIM_CR1.CKD2[3:0] that produces DTS2_ck (period tDTS2), which clocks the digital filters (tim_etr_in, tim_tix).

### 32.4.16 Clearing the tim_ocxref signal on an external event

The tim_ocxref signal of a given channel can be cleared when a high level is applied on the tim_ocref_clr_int input (OCxCE enable bit in the corresponding TIM_CCMRx register set to 1). tim_ocxref remains low until the next transition to the active state, on the following PWM cycle. This function can only be used in output compare and PWM modes. It must not be used in forced mode.

The tim_ocref_clr_int source depends on the OCREF clear selection feature implementation, refer to Section 32.3: TIM2/TIM3/TIM4/TIM5 implementation.

If the OCREF clear selection feature is implemented, the tim_ocref_clr_int can be selected between the tim_ocref_clr input and the tim_etrf input (tim_etr_in after the filter) by configuring the OCCS bit in the TIM_SMCR register. The tim_ocref_clr input can be selected among several tim_ocref_clr[15:0] inputs, using the OCRSEL[3:0] bitfield in the TIM_AF2 register, as shown in Figure 367.

**Figure 367. OCREF_CLR input selection multiplexer**: A 16-input multiplexer controlled by TIM_AF2.OCRSEL[3:0] selects one of tim_ocref_clr0 to tim_ocref_clr15 as tim_ocref_clr. A second 2-input multiplexer controlled by TIM_SMCR.OCCS selects tim_ocref_clr or tim_etrf as tim_ocref_clr_int.

If the OCREF clear selection feature is not implemented, the tim_ocref_clr_int input is directly connected to the tim_etrf input.

For example, the tim_ocref_clr_int signal can be connected to the output of a comparator to be used for current handling. In this case, tim_etr_in must be configured as follows:

1. The external trigger prescaler must be kept off: bits ETPS[1:0] in the TIM_SMCR register are cleared to 00.
2. The external clock mode 2 must be disabled: bit ECE in the TIM_SMCR register is cleared to 0.
3. The external trigger polarity (ETP) and the external trigger filter (ETF) can be configured according to the application's needs.

Figure 368 shows the behavior of the tim_ocxref signal when the tim_etrf input becomes high, for both values of the OCxCE enable bit. In this example, the timer TIMx is programmed in PWM mode.

**Figure 368. Clearing TIMx tim_ocxref**: The counter is an up-counting sawtooth crossing the CCRx level in each of three periods. tim_etrf goes high during the second period (while tim_ocxref is active) and returns low during the third period. With OCxCE = '0', tim_ocxref is a normal PWM: high from the start of each period until CNT reaches CCRx, low from CCRx until the period end, in all three periods. With OCxCE = '1', tim_ocxref goes low as soon as tim_ocref_clr_int becomes high in the second period, stays low for the rest of that period, and stays low during the whole third period because tim_ocref_clr_int is still high at the start of that period; it returns to normal PWM behavior only at the start of the following period after tim_etrf is low.

Note: In case of a PWM with a 100% duty cycle (if CCRx>ARR), tim_ocxref is enabled again at the next counter overflow.

This feature is also supported in combined and asymmetric modes. In this case, it is mandatory to enable the OCxCE bit for the channel. The OCxCE bit of the complementary channel (for exemple: OC2CE = X for oc2ref in Figure 369) is ignored. Figure 369 to Figure 371 describe the output waveforms for specific use cases when the ocref_clr_int signal is asserted.

**Figure 369. Asymmetric PWM mode 1**: Center-aligned counter with two thresholds CC1 < CC2. oc1ref is high while the counter is below CC1; oc2ref is high while the counter is below CC2. oc1refc (OC1CE = OC2CE = 0) follows oc1ref during up-counting and oc2ref during down-counting: it goes low when the counter crosses CC1 going up and returns high when the counter falls below CC2 going down. With OC1CE = 1 (OC2CE = X), an ocref_clr_int pulse occurring while oc1refc is high (just after the down-count CC2 crossing) forces oc1refc low; it stays low until the next transition to the active state in the following cycle.

**Figure 370. Asymmetric PWM mode 2**: Same thresholds, PWM mode 2 (active above the threshold). oc1ref is high while the counter is above CC1; oc2ref is high while the counter is above CC2. oc1refc (OC1CE = OC2CE = 0) goes high when the counter crosses CC1 going up and goes low when the counter falls below CC2 going down. With OC1CE = 1 (OC2CE = X), an ocref_clr_int pulse shortly after oc1refc goes high forces oc1refc low for the rest of the cycle; it goes high again at the next CC1 up-crossing.

**Figure 371. Combined PWM mode 1**: Edge-aligned up-counter (sawtooth) with thresholds CC1 < CC2, one period ending early with a "Counter reset". oc1ref (PWM mode 1) is high from period start to CC1; oc2ref (PWM mode 2) is high from CC2 to the period end; oc1refc (OC1CE = OC2CE = 0) = oc1ref OR oc2ref, low only between CC1 and CC2. Three further oc1refc traces with OC1CE = 1 (OC2CE = X) show ocref_clr_int pulses at different times: an ocref_clr_int during the oc2ref-driven high phase (after CC2) forces oc1refc low until the next period start; an ocref_clr_int just after a period start forces oc1refc low until the next active transition (the CC2 crossing); and an ocref_clr_int coinciding with the counter reset forces oc1refc low until the next active transition.

#### Conditions of use

This feature supports cycle-by-cycle current control loops, typically with a comparator shortening the PWM on-time when a current threshold is exceeded.

It cannot be used in the following modes, where the OCxCE bit must be cleared:

- PWM toggle mode (OCxM[4:0] = 0x03)
- One-pulse mode with PWM active on match (OPM = 1 and OCxM[4:0] = 0x06, 0x08, 0x0C, 0x0E)
- Combined PWM mode 1 or 3 in center-aligned mode (CMS[1:0] = 1, 2, 3 and OCxM[4:0] = 0x0C)

### 32.4.17 One-pulse mode

One-pulse mode (OPM) is a particular case of the previous modes. It allows the counter to be started in response to a stimulus and to generate a pulse with a programmable length after a programmable delay.

Starting the counter can be controlled through the slave mode controller. Generating the waveform can be done in output compare mode or PWM mode. One-pulse mode is selected by setting the OPM bit in the TIM_CR1 register. This makes the counter stop automatically at the next update event UEV.

A pulse can be correctly generated only if the compare value is different from the counter initial value. Before starting (when the timer is waiting for the trigger), the configuration must be:

CNT < CCRx ≤ ARR (in particular, 0 < CCRx).

**Figure 372. Example of one-pulse mode**: A short positive pulse on tim_ti2 starts the counter from 0. The counter counts up in steps. tim_oc1ref (and tim_oc1) is low until the counter reaches TIM_CCR1 (after tDELAY), then high until the counter reaches TIM_ARR (tPULSE), then low again; the counter stops at the update event.

For example if the user wants to generate a positive pulse on tim_oc1 with a length of tPULSE and after a delay of tDELAY as soon as a positive edge is detected on the tim_ti2 input pin.

Use tim_ti2fp2 as trigger 1:

1. Select the proper tim_ti2_in[15:0] source (internal or external) with the TI2SEL[3:0] bits in the TIM_TISEL register.
2. Map tim_ti2fp2 on tim_ti2 by writing CC2S = 01 in the TIM_CCMR1 register.
3. tim_ti2fp2 must detect a rising edge, write CC2P = 0 and CC2NP = 0 in the TIM_CCER register.
4. Configure tim_ti2fp2 as trigger for the slave mode controller (tim_trgi) by writing TS = 00110 in the TIM_SMCR register.
5. tim_ti2fp2 is used to start the counter by writing SMS to 110 in the TIM_SMCR register (trigger mode).

The OPM waveform is defined by writing the compare registers (taking into account the clock frequency and the counter prescaler).

- The tDELAY is defined by the value written in the TIM_CCR1 register.
- The tPULSE is defined by the difference between the autoreload value and the compare value (TIM_ARR - TIM_CCR1).
- Suppose the user wants to build a waveform with a transition from 0 to 1 when a compare match occurs and a transition from 1 to 0 when the counter reaches the autoreload value. To do this PWM mode 2 must be enabled by writing OC1M = 00111 in the TIM_CCMR1 register. Optionally the preload registers can be enabled by writing OC1PE = 1 in the TIM_CCMR1 register and ARPE in the TIM_CR1 register. In this case one has to write the compare value in the TIM_CCR1 register, the autoreload value in the TIM_ARR register, generate an update by setting the UG bit and wait for external trigger event on tim_ti2. CC1P is written to 0 in this example.

In this example, the DIR and CMS bits in the TIM_CR1 register must be low.

Since only one pulse (single mode) is needed, a one must be written in the OPM bit in the TIM_CR1 register to stop the counter at the next update event (when the counter rolls over from the autoreload value back to 0). When OPM bit in the TIM_CR1 register is set to 0, so the repetitive mode is selected.

#### Particular case: tim_ocx fast enable

In one-pulse mode, the edge detection on tim_tix input set the CEN bit which enables the counter. Then the comparison between the counter and the compare value makes the output toggle. But several clock cycles are needed for these operations and it limits the minimum delay tDELAY min we can get.

If one wants to output a waveform with the minimum delay, the OCxFE bit can be set in the TIM_CCMRx register. Then tim_ocxref (and tim_ocx) is forced in response to the stimulus, without taking in account the comparison. Its new level is the same as if a compare match had occurred. OCxFE acts only if the channel is configured in PWM1 or PWM2 mode.

### 32.4.18 Retriggerable one-pulse mode

This mode allows the counter to be started in response to a stimulus and to generate a pulse with a programmable length, but with the following differences with non-retriggerable one-pulse mode described in Section 32.4.17:

- The pulse starts as soon as the trigger occurs (no programmable delay).
- The pulse is extended if a new trigger occurs before the previous one is completed.

The timer must be in slave mode, with the bits SMS[4:0] = 01000 (combined reset + trigger mode) in the TIM_SMCR register, and the OCxM[4:0] bits set to 01000 or 01001 for retriggerable OPM mode 1 or 2.

If the timer is configured in up-counting mode, the corresponding CCRx must be set to 0 (the ARR register sets the pulse length). If the timer is configured in down-counting mode CCRx must be above or equal to ARR.

Note: In retriggerable one-pulse mode, the CCxIF flag is not significant.

The OCxM[4:0] and SMS[4:0] bitfields are split into two parts for compatibility reasons, the most significant bit is not contiguous with the three least significant ones.

This mode must not be used with center-aligned PWM modes. It is mandatory to have CMS[1:0] = 00 in TIM_CR1.

*Digest note:* SMS[4:0] is split in TIM_SMCR as SMS[2:0] = bits 2:0 and SMS[4:3] = bits 17:16 (see 32.5.3); OCxM[4:0] is split as OCxM[2:0] plus OCxM[3] and OCxM[4] in the upper half of TIM_CCMRx (see 32.5.8 and 32.5.10).

**Figure 373. Retriggerable one-pulse mode**: Each tim_trgi pulse resets and starts the counter, which ramps up to ARR and stops. tim_ocx goes high at the trigger and goes low when the counter reaches ARR. When a second trigger arrives while the counter is still ramping (pulse in progress), the counter restarts from 0 and tim_ocx stays high, so the pulse is extended until the counter reaches ARR after the last trigger.

### 32.4.19 Pulse on compare mode

A pulse can be generated upon compare match event. A signal with a programmable pulse width generated when the counter value equals a given compare value, for debugging or synchronization purposes.

This mode is available for any slave mode selection, including encoder modes, in edge and center aligned counting modes. It is solely available for channel 3 and channel 4. The pulse generator is unique and is shared by the two channels, as shown on Figure 374.

**Figure 374. Pulse generator circuitry**: "CCR3 match" gated by an Enable block (enabled when OC3M = 1010) and "CCR4 match" gated by an Enable block (enabled when OC4M = 1010) are ORed into a single "Pulse generator" configured by PWPRSC[2:0] and PW[7:0]. Each match also sets a dedicated R/S latch (one for channel 3, one for channel 4); the falling edge of the pulse generator output resets both latches. tim_oc3 is the AND of the pulse generator output and the channel 3 latch; tim_oc4 is the AND of the pulse generator output and the channel 4 latch.

Figure 375 shows how the pulse is generated for edge-aligned and encoder operating modes.

**Figure 375. Pulse generation on compare event, for edge-aligned and encoder modes**:

- Top (edge-aligned): the counter is a stepped sawtooth crossing the CMP3 level once per period. Each time the counter equals CMP3, a trigger occurs and tim_ocx outputs a fixed-width pulse. When a new trigger occurs while a pulse is ongoing, the pulse is extended ("Extended pulsewidth due to re-trigger").
- Bottom (encoder mode): the counter moves up and down following the encoder; each time it crosses/equals CMP3 (in either direction) a trigger occurs and tim_ocx outputs a fixed-width pulse.

This output compare mode is selected using the OC3M[3:0] and OC4M[3:0] bitfields in TIM_CCMR2 register.

The pulse width is programmed using the PW[7:0] bitfield in the register, using a specific clock prescaled according to PWPRSC[2:0] bits, as follows:

- tPW = PW[7:0] x tPWG
- where tPWG = (2^(PWPRSC[2:0])) x ttim_ker_ck.

Gives the resolution and maximum values depending on the prescaler value.

The pulse is retriggerable: a new trigger while the pulse is ongoing, causes the pulse to be extended.

Note: If the two channels are enabled simultaneously, the pulses are issued independently as long as the trigger on one channel is not overlapping the pulse generated on the concurrent output. On the opposite, if the two triggers are overlapping, the pulse width related to the first arriving trigger is extended (because of the retrigger), while the pulse width of the last arriving trigger is correct (as shown on Figure 376).

*Digest note:* "PW[7:0] bitfield in the register" refers to TIM_ECR (PW and PWPRSC fields, see 32.5.19). Figure 374 and the text give the mode code as 4 bits (1010); as a 5-bit OCxM[4:0] value this is 01010 (see TIM_CCMR2 description).

**Figure 376. Extended pulse width in case of concurrent triggers**: Trigger CMP3 and Trigger CMP4 events are shown. When a CMP4 trigger occurs after a tim_oc3 pulse has finished, tim_oc3 and tim_oc4 pulses are independent and of nominal width. When a CMP4 trigger occurs while a tim_oc3 pulse is ongoing, the tim_oc3 pulse is extended ("Extended pulsewidth due to overlapping CMP4 trigger") so that it ends together with the tim_oc4 pulse, which has the correct width.

### 32.4.20 Encoder interface mode

#### Quadrature encoder

To select encoder interface mode write SMS = 0001 in the TIM_SMCR register if the counter is counting on tim_ti1 edges only, SMS = 0010 if it is counting on tim_ti2 edges only and SMS = 0011 if it is counting on both tim_ti1 and tim_ti2 edges.

Select the tim_ti1 and tim_ti2 polarity by programming the CC1P and CC2P bits in the TIM_CCER register. CC1NP and CC2NP must be kept cleared. When needed, the input filter can be programmed as well.

The two inputs tim_ti1 and tim_ti2 are used to interface to an incremental encoder. Refer to Table 321. The counter is clocked by each valid transition on tim_ti1fp1 or tim_ti2fp2 (tim_ti1 and tim_ti2 after input filter and polarity selection, tim_ti1fp1 = tim_ti1 if not filtered and not inverted, tim_ti2fp2 = tim_ti2 if not filtered and not inverted) assuming that it is enabled (CEN bit in TIM_CR1 register written to 1). The sequence of transitions of the two inputs is evaluated and generates count pulses as well as the direction signal. Depending on the sequence the counter counts up or down, the DIR bit in the TIM_CR1 register is modified by hardware accordingly. The DIR bit is calculated at each transition on any input (tim_ti1 or tim_ti2), whatever the counter is counting on tim_ti1 only, tim_ti2 only or both tim_ti1 and tim_ti2.

Encoder interface mode acts simply as an external clock with direction selection. This means that the counter just counts continuously between 0 and the autoreload value in the TIM_ARR register (0 to ARR or ARR down to 0 depending on the direction). So the TIM_ARR must be configured before starting. In the same way, the capture, compare, prescaler, trigger output features continue to work as normal. Encoder mode and external clock mode 2 are not compatible and must not be selected together.

In this mode, the counter is modified automatically following the speed and the direction of the quadrature encoder and its content, therefore, always represents the encoder's position. The count direction corresponds to the rotation direction of the connected sensor. The table summarizes the possible combinations, assuming tim_ti1 and tim_ti2 do not switch at the same time.

**Table 321. Counting direction versus encoder signals (CC1P = CC2P = 0)**

| Active edge | SMS[4:0] | Level on opposite signal (tim_ti1fp1 for tim_ti2, tim_ti2fp2 for tim_ti1) | tim_ti1fp1 Rising | tim_ti1fp1 Falling | tim_ti2fp2 Rising | tim_ti2fp2 Falling |
|---|---|---|---|---|---|---|
| Counting on tim_ti1 only, x1 mode | 01110 | High | Down | Up | No count | No count |
| Counting on tim_ti1 only, x1 mode | 01110 | Low | No count | No count | No count | No count |
| Counting on tim_ti2 only, x1 mode | 01111 | High | No count | No count | Up | Down |
| Counting on tim_ti2 only, x1 mode | 01111 | Low | No count | No count | No count | No count |
| Counting on tim_ti1 only, x2 mode | 00001 | High | Down | Up | No count | No count |
| Counting on tim_ti1 only, x2 mode | 00001 | Low | Up | Down | No count | Down |
| Counting on tim_ti2 only, x2 mode | 00010 | High | No count | No count | Up | Down |
| Counting on tim_ti2 only, x2 mode | 00010 | Low | No count | No count | Down | Up |
| Counting on tim_ti1 and tim_ti2, x4 mode | 00011 | High | Down | Up | Up | Down |
| Counting on tim_ti1 and tim_ti2, x4 mode | 00011 | Low | Up | Down | Down | Up |

*Digest note:* The "Counting on tim_ti1 only x2 mode, Low" row prints "Down" in the tim_ti2fp2 Falling column, which is inconsistent with tim_ti1-only counting (all other tim_ti1-only cells in the tim_ti2fp2 columns are "No count"). Reproduced as printed.

A quadrature encoder can be connected directly to the MCU without external interface logic. However, comparators are normally be used to convert the encoder's differential outputs to digital signals. This greatly increases noise immunity. The third encoder output which indicates the mechanical zero position, can be connected to the external trigger input and trigger a counter reset.

Figure 377 gives an example of counter operation, showing count signal generation and direction control. It also shows how input jitter is compensated where both edges are selected. This might occur if the sensor is positioned near to one of the switching points. For this example we assume that the configuration is the following:

- CC1S = 01 (TIM_CCMR1 register, tim_ti1fp1 mapped on tim_ti1).
- CC2S = 01 (TIM_CCMR1 register, tim_ti2fp2 mapped on tim_ti2).
- CC1P and CC1NP = 0 (TIM_CCER register, tim_ti1fp1 noninverted, tim_ti1fp1 = tim_ti1).
- CC2P and CC2NP = 0 (TIM_CCER register, tim_ti2fp2 noninverted, tim_ti2fp2 = tim_ti2).
- SMS = 0011 (TIM_SMCR register, both inputs are active on both rising and falling edges).
- CEN = 1 (TIM_CR1 register, counter is enabled).

**Figure 377. Example of counter operation in encoder interface mode**: tim_ti1 and tim_ti2 are in quadrature. Phases: "forward" (counter steps up on every edge of both inputs), "jitter" (one input toggles back and forth while the other is static: the counter alternates up and down by one, so jitter is compensated), "backward" (counter steps down on every edge), "jitter" again (counter alternates), then "forward" (counter steps up). The annotations under the counter read up, down, up.

Figure 378 gives an example of counter behavior when tim_ti1fp1 polarity is inverted (same configuration as above except CC1P = 1).

**Figure 378. Example of encoder interface mode with tim_ti1fp1 polarity inverted**: Same tim_ti1/tim_ti2 waveforms as Figure 377; the counting direction is reversed: the counter counts down in the "forward" phases and up in the "backward" phase, with the same jitter compensation.

Figure 379 shows the timer counter value during a speed reversal, for various counting modes.

**Figure 379. Quadrature encoder counting modes**: tim_ti1 and tim_ti2 in quadrature, with a direction reversal in the middle (DIR bit goes from 0 to 1). Counter x4 (counting on both edges of both inputs): 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, then after reversal 4, 3, 2, 1, 0, 9, 8, 7, 6, 5, 4, 3, 2 (the counter wraps between 9 and 0, i.e. ARR = 9). Counter x2: 8, 9, 0, 1, 2, then 1, 0, 9, 8, 7, 6. Counter x1: 9, 0, 1, then 0, 9, 8.

The timer, when configured in encoder interface mode provides information on the sensor's current position. Dynamic information can be obtained (speed, acceleration, deceleration) by measuring the period between two encoder events using a second timer configured in capture mode. The output of the encoder which indicates the mechanical zero can be used for this purpose. Depending on the time between two events, the counter can also be read at regular times. This can be done by latching the counter value into a third input capture register if available (then the capture signal must be periodic and can be generated by another timer). When available, it is also possible to read its value through a DMA request.

The IUFREMAP bit in the TIM_CR1 register forces a continuous copy of the update interrupt flag (UIF) into the timer counter register's bit 31 (TIM_CNT[31]). This allows both the counter value and a potential roll-over condition signaled by the UIFCPY flag to be read in an atomic way. It eases the calculation of angular speed by avoiding race conditions caused, for instance, by a processing shared between a background task (counter reading) and an interrupt (update interrupt).

There is no latency between the UIF and UIFCPY flag assertions.

In 32-bit timer implementations, when the IUFREMAP bit is set, bit 31 of the counter is overwritten by the UIFCPY flag upon read access (the counter's most significant bit is only accessible in write mode).

*Digest note:* The source names the bit "IUFREMAP" in this paragraph; the TIM_CR1 register description names it UIFREMAP (bit 11).

#### Clock plus direction encoder mode

In addition to the quadrature encoder mode, the timer offers support for other types of encoders.

In the "clock plus direction" mode shown on Figure 380, the clock is provided on a single line, on tim_ti2, while the direction is forced using the tim_ti1 input.

This mode is enabled with the SMS[4:0] bitfield in the TIM_SMCR register, as following:

- 01010: x2 mode, the counter is updated on both rising and falling edges of the clock.
- 01011: x1 mode, the counter is updated on a single clock edge, as per CC2P bit value: CC2P = 0 corresponds to rising edge sensitivity and CC2P = 1 corresponds to falling edge sensitivity.

The polarity of the direction signal on tim_ti1 is set with the CC1P bit: 0 corresponds to positive polarity (up-counting when tim_ti1 is high and down-counting when tim_ti1 is low) and CC1P = 1 corresponds to negative polarity (up-counting when tim_ti1 is low).

**Figure 380. Direction plus clock encoder mode**: tim_ti1 (direction) is high for the first part and low for the second; tim_ti2 is the clock. Counter x2 mode (both clock edges): 6, 7, 8, 9, 10, 11 while tim_ti1 is high, then 10, 9, 8, 7, 6 after tim_ti1 goes low. Counter x1 mode (single edge): 6, 7, 8, 9, then 8, 7.

#### Directional clock encoder mode

In the "directional clock" mode on Figure 381, the clocks are provided on two lines, with a single one at once, depending on the direction, so as to have one up-counting clock line and one down-counting clock line.

This mode is enabled with the SMS[4:0] bitfield in the TIM_SMCR register, as following:

- 01100: x2 mode, the counter is updated on both rising and falling edges of any of the two clock lines. The CC1P and CC2P bits are coding for the clock idle state. CCxP = 0 corresponds to high-level idle state (refer to Figure 381) and CCxP = 1 corresponds to low-level idle state (refer to Figure 382).
- 01101: x1 mode, the counter is updated on a single clock edge, as per CC1P and CC2P bit value. CCxP = 0 corresponds to falling edge sensitivity and high-level idle state (refer to Figure 381), CCxP = 1 corresponds to rising edge sensitivity and low-level idle state (refer to Figure 382).

**Figure 381. Directional clock encoder mode (CC1P = CC2P = 0)**: Clock pulses (idle high) first on tim_ti2 (up-counting, DIR = 0) then on tim_ti1 (down-counting, DIR = 1). Counter x2 mode: 6, 7, 8, 9, 10, 11, then 10, 9, 8, 7, 6, 5. Counter x1 mode: 6, 7, 8, then 7, 6, 5.

**Figure 382. Directional clock encoder mode (CC1P = CC2P = 1)**: Same with idle-low clocks. Counter x2 mode: 6, 7, 8, 9, 10, 11, then 10, 9, 8, 7, 6, 5. Counter x1 mode: 7, 8, 9, then 8, 7, 6.

Table 322 details how the directional clock mode operates, for any input transition.

**Table 322. Counting direction versus encoder signals and polarity settings**

| Directional clock mode | SMS[4:0] | Level on opposite signal (tim_ti1fp1 for tim_ti2, tim_ti2fp2 for tim_ti1) | tim_ti1fp1 Rising | tim_ti1fp1 Falling | tim_ti2fp2 Rising | tim_ti2fp2 Falling |
|---|---|---|---|---|---|---|
| x2 mode, CCxP = 0 | 01100 | High | Down | Down | Up | Up |
| x2 mode, CCxP = 0 | 01100 | Low | No count | No count | No count | No count |
| x2 mode, CCxP = 1 | 01100 | High | No count | No count | No count | No count |
| x2 mode, CCxP = 1 | 01100 | Low | Down | Down | Up | Up |
| x1 mode, CCxP = 0 | 01101 | High | No count | Down | No count | Up |
| x1 mode, CCxP = 0 | 01101 | Low | No count | No count | No count | No count |
| x1 mode, CCxP = 1 | 01101 | High | No count | No count | No count | No count |
| x1 mode, CCxP = 1 | 01101 | Low | Down | No count | Up | No count |

#### Index input

The counter can be reset by an index signal coming from the encoder, indicating an absolute reference position. The index signal must be connected to the tim_etr_in input. It can be filtered using the digital input filter.

The index functionality is enabled with the IE bit in the TIM_ECR register. The IE bit must be set only in encoder mode, when the SMS[4:0] bitfield has the following values: 00001, 00010, 00011, 01010, 01011, 01100, 01101, 01110, 01111.

Available encoders are proposed with several options for index pulse conditioning, as per Figure 383:

- Gated with A and B: the pulse width is 1/4 of one channel period, aligned with both A and B edges.
- Gated with A (or gated with B): the pulse width is 1/2 of one channel period, aligned with the two edges on channel A (resp. channel B).
- Ungated: the pulse width is up to one channel period, without any alignment to the edges.

**Figure 383. Index gating options**: Channel A and Channel B in quadrature. "Gated A & B" index is high for one quarter period, while both A and B are high. "Gated A" index is high for the half period during which A is high. "Ungated" index is high for up to one period, starting before and ending after the A pulse, with no edge alignment. An arrow marks the reference edge on Channel B within the index pulse.

The circuitry tolerates jitter on index signal, whatever the gating mode, as shown on Figure 384.

In ungated mode, the signal must be strictly below two encoder periods. If the pulse width is greater or equal to two encoder period, the counter is reset multiple times.

**Figure 384. Jittered Index signals**: Same as Figure 383 but the index edges are shown with jitter (uncertain edge position). For ungated mode, the maximum pulse width ("Max pulsewidth ungated mode") spans from just after one Channel B falling edge to just before the following one, i.e. less than two encoder periods.

The timer supports the three gating options identically, without any specific programming needed. It is only necessary to define on which encoder state (for example channel A and channel B state combination) the index must be synchronized, using the IPOS[1:0] bitfield in the TIM_ECR register.

The index detection event acts differently depending on counting direction to ensure symmetrical operation during speed reversal:

- The counter is reset during up-counting (DIR bit = 0).
- The counter is set to TIM_ARR when down-counting.

This allows the index to be generated on the very same mechanical angular position whatever the counting direction. Figure 385 shows at which position is the index generated, for a simplistic example (an encoder providing four edges par mechanical rotation).

**Figure 385. Index generation for IPOS[1:0] = 11**: State diagram of the four encoder states: State 1 AB = 00, State 2 AB = 01, State 3 AB = 11, State 4 AB = 10, traversed in the order 1, 2, 3, 4 when up-counting and in reverse when down-counting. Rotor angle 0° is between State 1 and State 2, 90° between State 2 and State 3, 180° between State 3 and State 4, 270° between State 4 and State 1. "The index event is always generated here": at the 180° position (between State 3, AB = 11, and State 4, AB = 10).

Figure 386 presents waveforms and corresponding values for IPOS[1:0] = 11. It shows that the instant at which the counter value is forced is automatically adjusted depending on the counting direction:

- Counter set to 0 when encoder state is 11 (ChA = 1, ChB = 1), when up-counting (DIR bit = 0).
- Counter set to TIM_ARR when exiting the 11 state, when down-counting (DIR bit = 1).

An interrupt can be issued upon index detection event.

The arrows are indicating on which transition is the index event interrupt generated.

**Figure 386. Counter reading with index gated on channel A (IPOS[1:0] = 11)**: ARR = 7. Up-counting: counter 5, 6, 7, then forced to 0 on entering state 11 during the index pulse, then 1, 2, 3, 4, 5, 6. After the direction reversal (DIR = 1): 5, 4, 3, 2, 1, 0, then set to 7 (TIM_ARR) when exiting state 11 during the index pulse, then 6, 5, 4, 3, 2, 1.

Figure 387 presents waveforms and corresponding values for the ungated mode. The arrows are indicating on which transition is the index event generated.

**Figure 387. Counter reading with index ungated (IPOS[1:0] = 00)**: ARR = 7. Up-counting: 3, 4, 5, 6, 7, 0 (reset at the index, synchronized on state AB = 00), 1, 2, 3, 4; after reversal: 3, 2, 1, 0, 7, 6, 5, 4, 3, 2, 1, 0, 7.

Figure 388 shows how the gated on A & B mode is handled, for various pulse alignment scenarios. The arrows are indicating on which transition is the index event generated.

**Figure 388. Counter reading with index gated on channel A and B**: ARR = 7. Up-counting: 5, 6, 7, 0 (reset at index), 1, 2, 3, 4, 5, 6; after reversal: 5, 4, 3, 2, 1, 0, 7 (set to ARR at index), 6, 5, 4, 3, 2, 1.

Figure 389 and Figure 390 detail the case where the subsequent index pulse may be narrower than one quarter of the encoder clock period.

**Figure 389. Encoder mode behavior in case of narrow index pulse (IPOS[1:0] = 11)**: Two cases with the same counter sequence (5, 6, 7, 0, 1, 2, 3, 4, 5, 6, then 5, 4, 3, 2, 1, 0, 7, 6, 5, 4, 3, 2, 1): "Index leading state transition" (narrow index pulse occurring just before the encoder state transition) and "Index delayed versus state transition" (narrow index pulse occurring just after the transition). In both cases the counter is reset/set at the same encoder position.

**Figure 390. Counter reset Narrow index pulse (closer view, ARR = 0x07)**: Close-up of the two narrow-index cases. First case: counter 5, 6, 7, 0, 1, 2, 3. Second case: counter 4, 5, 6, 7, 0, 1, 2, 3 (the 7 to 0 reset occurs at the index position).

Figure 391 shows how the index is managed in x1 and x2 modes.

**Figure 391. Index behavior in x1 and x2 mode (IPOS[1:0] = 01)**: The index is synchronized with encoder state AB = IPOS[1:0] = 01. Counter x2: 10, 11, 0 (reset at index), 1, 2, then after reversal 1, 0, 11 (set to ARR at index), 10, 9, 8. Counter x1: 5, 6, 7, 0, 1, 3 [unclear in source: the x1 sequence printed in the figure is 5, 6, 7, 0, 1, 3].

#### Directional index sensitivity

The IDIR[1:0] bitfield in the TIM_ECR register allows the index to be active only in a selected counting direction.

Figure 392 shows the relationship between index and counter reset events, depending on IDIR[1:0] value.

**Figure 392. Directional index sensitivity**: The counter up-counts (DIR = 0) then down-counts (DIR = 1), with index pulses in both phases. IDIR[1:0] = 00: every index pulse resets the counter in both directions. IDIR[1:0] = 01: only index pulses during up-counting reset the counter. IDIR[1:0] = 10: only index pulses during down-counting reset the counter.

#### Special first index event management

The FIDX bit in the TIM_ECR register allows the index to be taken only once, as shown on Figure 393. Once the first index has arrived, any subsequent index is ignored. If needed, the circuitry can be rearmed by writing the FIDX bit to 0 and setting it again to 1.

**Figure 393. Counter reset as function of FIDX bit setting**: With FIDX = 0, every index pulse causes a counter reset. With FIDX = 1, only the first index pulse causes a counter reset; later index pulses are ignored.

#### Index blanking

The index event can be blanked using the tim_ti3 or tim_ti4 inputs. During the blanking window, the index events are no longer resetting the counter, as shown on Figure 394.

This mode is enabled using the IBLK[1:0] bitfield in the TIM_ECR register, as following:

- IBLK[1:0] = 00: Index signal always active.
- IBLK[1:0] = 01: Index signal blanking on tim_ti3 input.
- IBLK[1:0] = 10: Index signal blanking on tim_ti4 input.

**Figure 394. Index blanking**: A blanking signal on TI3 (CC3P = 0) is high during a window. With IBLK[1:0] = 00, every index pulse resets the counter. With IBLK[1:0] = 01, index pulses occurring while TI3 is high are ignored (no counter reset); index pulses outside the window reset the counter.

#### Index management in nonquadrature mode

Figure 395 and Figure 396 detail how the index is managed in directional clock mode and clock plus direction mode, when the SMS[4:0] bitfield is equal to 01010, 01011, 01100, 01101.

For both of these modes, the index sensitivity is set with the IPOS[0] bit as following:

- IPOS[0] = 0: Index is detected on clock low level.
- IPOS[0] = 1: Index is detected on clock high level.

The IPOS[1] bit is not-significant.

**Figure 395. Index behavior in clock + direction mode, IPOS[0] = 1**: Direction (TI1) high then low; Clock (TI2) pulses; Index pulses occur during clock-high levels. Counter x2 mode: 7, 0 (reset at index), 1, 2, 3, 4, then 3, 2, 7 (set to ARR at index while down-counting), 6, 5. Counter x1 mode: 7, 0, 1, 2, 1, 7.

**Figure 396. Index behavior in directional clock mode, IPOS[0] = 1**: Clock Up (TI2) pulses then Clock Down (TI1) pulses; DIR goes from 0 to 1 at the switch. Counter x2 mode: 9, 0 (reset at index), 1, 2, 3, 4, 3, 2, 1, 0, 9 (set to ARR at index), 8. Counter x1 mode: 9, 0, 1, 2, 1, 0, 9.

#### Encoder error management

For encoder configurations where two quadrature signals are available, it is possible to detect transition errors. The reading on the two inputs corresponds to a 2-bit gray code which can be represented as a state diagram, on Figure 397. A single bit is expected to change at once. An erroneous transition sets the TERRF interrupt flag in the TIM_SR status register. A transition error interrupt is generated if the TERRIE bit is set in the TIM_DIER register.

**Figure 397. State diagram for quadrature encoded signals**: Four states 00, 01, 11, 10. Correct transitions (single bit change) are 00 to/from 01, 01 to/from 11, 11 to/from 10, 10 to/from 00. Erroneous transitions are the diagonals 00 to/from 11 and 01 to/from 10.

For encoder having an index signal, it is possible to detect abnormal operation resulting in an excess of pulses per revolution. An encoder with N pulses per revolution provides 4xN counts per revolution. The index signal resets the counter every 4xN clock periods.

If the counter value is incremented from TIM_ARR to 0 or decremented from 0 to TIM_ARR value without any index event, this is reported as an index position error.

The overflow threshold is programmed using the TIM_ARR register. A 1000 lines encoder results in a counter value being between 0 and 3999 (in 4x reading mode). The overflow detection threshold must be programmed by setting TIM_ARR = 3999 + 1 = 4000.

The error assertion is delayed to the transition 0 to 1 when in up-counting. This is to cope with narrow index pulses in gated A and B mode, as shown on Figure 398.

**Figure 398. Up-counting encoder error detection**: Two cases with the counter going 5, 6, 7, 0, 1, 2, 3 (ARR = 7). Top: the error is detected at the 7 to 0 rollover, but a (narrow) index pulse arrives before the 0 to 1 transition, so the error is aborted ("Abort (index detection)") and IERRF stays low. Bottom: no index arrives, so the error detected at 7 to 0 is asserted (IERRF set) at the 0 to 1 transition ("Error asserted").

In down-counting mode, the detection is conditioned by a preliminary transition from 1 to 0. This is to cope with narrow index pulses in gated A and B mode, as shown on Figure 399, to avoid any false error detection in case the encoder dithers between TIM_ARR and 0 immediately after the index detection.

**Figure 399. Down-counting encode error detection**: Top: counter 2, 1, 0, 7, 0, 7, 6, 5: the first 0 to 7 transition follows an index ("No error: transition from 0 to TIM_ARR following an index"); the later 0 to 7 transition is without index but does not follow a transition from 1 to 0 ("No error"), so IERRF stays low. Bottom: counter 2, 1, 0, 7, 6, 5, 4 with no index: the 1 to 0 then 0 to 7 sequence is detected ("Error detected") and IERRF is set at the following transition ("Error asserted").

An index error sets the IERRF interrupt flag in the TIM_SR status register. An index error interrupt is generated if the IERRIE bit is set in the TIM_DIER register.

#### Functional encoder interrupts

The following interrupts are also available in encoder mode

- Direction change: any change of the counting direction in encoder mode causes the DIR bit in the TIM_CR1 register to toggle. The direction change sets the DIRF interrupt flag in the TIM_SR status register. A direction change interrupt is generated if the DIRIE bit is set in the TIM_DIER register.
- Index event: the index event sets the IDXF interrupt flag in the TIM_SR status register. An index interrupt is generated if the IDXIE bit is set in the TIM_DIER register.

#### Slave mode selection preload for run-time encoder mode update

It can be necessary to switch from one encoder mode to another during run-time. This is typically done at high-speed to decrease the update interrupt rate, by switching from x4 to x2 to x1 mode, as shown on Figure 400.

For this purpose, the SMS[4:0] bit can be preloaded. This is enabled by setting the SMSPE enable bit in the TIM_SMCR register. The trigger for the transfer from SMS[4:0] preload to active value can be selected with the SMSPS bit in the TIM_SMCR register.

- SMSPS = 0: the transfer is triggered by the update event (UEV) occurring when the counter overflows when up-counting, and underflows when down-counting.
- SMSPS = 1: the transfer is triggered by the index event.

**Figure 400. Encoder mode change with preload transferred on update (SMSPS = 0)**: The preload value is written successively to SMS = 0011 (x4 mode), SMS = 0001 (x2 mode) and SMS = 1110 (x1 mode); each new preload value becomes the active value only at the next update event.

#### Encoder clock output

The encoder mode operating principle is not perfectly suited for high-resolution velocity measurements, at low speed, as it requires a relatively long integration time to have a sufficient number of clock edges and a precise measurement.

At low speed, a better solution is to do an edge-to-edge clock period measurement. This can be achieved using a slave timer. The timer can output the encoder clock information on the tim_trgo output. The slave timer can then perform a period measurement and provide velocity information for each and every encoder clock edge.

This mode is enabled by setting the MMS[3:0] bitfield to 1000, in the TIM_CR2 register. It is valid for the following SMS[4:0] values: 00001, 00010, 00011, 01010, 01011, 01100, 01101, 01110, 01111. Any other SMS[4:0] code is not allowed and may lead to unexpected behavior.

### 32.4.21 Encoder with built-in debouncer

This mode is intended to support noisy digital potentiometers and knobs, providing quadrature encoded signals with potentially long bouncing periods after each transition.

The operating principle consists of working on the first valid transition and discard any other until a second valid transition is detected on the alternate encoder signal.

The Figure 401 below represents the x2 operating mode. It must be noticed that a transition on input 1 is ignored during direction reversal, if there's no edge on input 2.

The Figure 402 below represents the x4 operating mode. In this case, a transition is always ignored during a direction reversal or when the encoder dithers between two positions.

These two modes are enabled by writing SMS[4:0] = 10000 or 10001 in TIM_SMCR register.

The encoder with built-in debouncer modes are not suitable for tracking a position or an angle in motor control applications. The transitions ignored during direction reversal will lead to a position/angle error that will build-up over time.

**Figure 401. Encoder with built-in debouncer, x2 mode**: Two examples with Input 1, Input 2 (bouncing), "Input 1 Debounced" and Direction. In the first, the counter (x2) goes 1, 2, 1, 0; in the second, 2, 1, 0, 1. Bounces after each valid transition are ignored until a valid transition occurs on the other input, and a transition on input 1 during direction reversal without an edge on input 2 is ignored.

**Figure 402. Encoder with built-in debouncer, x4 mode**: Input 1, Input 2, "Input 1 Debounced", "Input 2 Debounced" and Direction; the counter (x4) goes 1, 2, 3, 2, 1, 0, with the transition at a direction reversal ignored.

### 32.4.22 Direction bit output

It is possible to output a direction signal out of the timer, on the tim_oc3 and tim_oc4 output signals (copy of the DIR bit in the TIM_CR1 register). This is achieved by setting the OC3M[3:0] or the OC4M[3:0] bitfield to 1011 in the TIM_CCMR2 register.

This feature can be used for monitoring the counting direction (or rotation direction) in encoder mode, or to have a signal indicating the up/down phases in center-aligned PWM mode.

### 32.4.23 Clock drift measurement

It is possible to measure the drift between two clock sources using the directional clock encoder mode. This is useful for audio applications typically, when one need to compute the drift between two streams.

To do so, a signal representing the rate of a first audio stream must be connected to tim_ti1 and a signal representing the rate of a second audio stream must be connected to tim_ti2. The signals representing the audio rates are generally the SAIx_FS_A, SAIx_FS_B, SPIx_WS or spdifrx_frame_sync (this list of signals is provided as example and depends on the audio peripheral availability for a given product line, as detailed on the product datasheet).

In this case, the clocks are present on both tim_ti1 and tim2 simultaneously, as shown on Figure 403, and the counter value indicates the drift.

Let's define Ftim_ti1 and Ftim_ti2 the frequencies of the signals on tim_ti1 and tim_ti2. The counter value will change as following:

- If Ftim_ti1 > Ftim_ti2 the counter value increases.
- If Ftim_ti1 < Ftim_ti2 the counter value decreases.
- If Ftim_ti1 = Ftim_ti2 the counter value will dither between two consecutive values, from one clock edge to the other. If the two clocks are perfectly synchronized (clock edges occurring simultaneously on the two inputs), the counter value does not change (as shown on Figure 403).

**Figure 403. Clock drift measure using directional clock mode**: Three phases. "Ftim_ti1 > Ftim_ti2": the counter value climbs (shown from 0x0000 to 0x0001 to 0x0002). "Ftim_ti1 = Ftim_ti2": the counter value dithers between two consecutive values (or stays constant if edges are simultaneous). "Ftim_ti1 < Ftim_ti2": the counter value decreases (shown going through 0x0000 to 0xFFFF and 0xFFFE).

### 32.4.24 UIF bit remapping

The IUFREMAP bit in the TIM_CR1 register forces a continuous copy of the update interrupt flag (UIF) into bit 31 of the timer counter register's bit 31 (TIM_CNT[31]). This is used to atomically read both the counter value and a potential roll-over condition signaled by the UIFCPY flag. It eases the calculation of angular speed by avoiding race conditions caused, for instance, by a processing shared between a background task (counter reading) and an interrupt (update interrupt).

There is no latency between the UIF and UIFCPY flag assertions.

In 32-bit timer implementations, when the IUFREMAP bit is set, bit 31 of the counter is overwritten by the UIFCPY flag upon read access (the counter's most significant bit is only accessible in write mode).

*Digest note:* The register bit is named UIFREMAP in TIM_CR1 (bit 11). Since all TIM2/TIM3/TIM4/TIM5 are 32-bit on STM32C5, enabling UIFREMAP sacrifices TIM_CNT[31] on reads.

### 32.4.25 Timer input XOR function

The TI1S bit in the TIM_CR2 register, allows the input filter of channel 1 to be connected to the output of an XOR gate, combining the three input pins tim_ti1, tim_ti2 and tim_ti3.

The XOR output can be used with all the timer input functions such as trigger or input capture.

An example of this feature used to interface Hall sensors is given in Section 31.3.34: Interfacing with Hall sensors.

It is convenient to measure the interval between edges on two input signals, as per Figure 404.

**Figure 404. Measuring time interval between edges on three signals**: tim_ti1, tim_ti2 and tim_ti3 each have edges at different times; the XOR signal toggles at every edge of any of the three inputs, and the TIMx counter is reset at each XOR edge (sawtooth), so the value reached before each reset measures the interval between consecutive edges.

The XORPS control bit selects the position of the XOR gate, as shown on the Figure 405 and Figure 406 below, when the TI1S bit is set.

**Figure 405. XOR gate connection with TI1S = 1 and XORPS = 0**: tim_ti1, tim_ti2 and tim_ti3 (each optionally inverted by TIM_CR2.TI1INV, TI2INV, TI3INV) are combined by a 3-input XOR before the filters; the XOR output replaces tim_ti1 at the input of the channel 1 filter (the direct tim_ti1 path is cut). Channel 1 filter output gives tim_ti1fp1/2 and tim_ti1f_ed. tim_ti2, tim_ti3 and tim_ti4 each go through their own filters to give tim_ti2fp1/2, tim_ti3fp1/2 and tim_ti4fp1/2. The filtered signals are readable as TI1FS, TI2FS, TI3FS, TI4FS in TIM_SR.

**Figure 406. XOR gate connection with TI1S = 1 and XORPS = 1**: tim_ti1, tim_ti2, tim_ti3 and tim_ti4 are first filtered; the filtered tim_ti1, tim_ti2 and tim_ti3 (each optionally inverted by TI1INV, TI2INV, TI3INV) are combined by the XOR after the filters, and the XOR output feeds the channel 1 edge detector (producing tim_ti1fp1/2 and tim_ti1f_ed). The filtered signals are readable as TI1FS to TI4FS in TIM_SR. (The fourth input is labeled "tim_ti3" in the figure, feeding tim_ti4fp1/2; this appears to be a labeling error for tim_ti4.)

Three control bits T1INV, T2INV and T3INV in the TIM_CR2 register can invert the tim_in1, tim_in2 and tim_in3 signals prior entering the XOR gate.

The status of the tim_in1, tim_in2, tim_in3 and tim_in4 signals can be software polled using the TI1FS, TI2FS, TI3FS and TI4FS bits in the TIM_SR register (tim_ti4 is not represented on figures above and do not enter into the XOR gate).

*Digest note:* The bits are named TI1INV, TI2INV, TI3INV in the TIM_CR2 register description.

### 32.4.26 Timers and external trigger synchronization

The TIMx timers can be synchronized with an external trigger in several modes: reset mode, gated mode, trigger mode, reset + trigger and gated + reset modes.

#### Slave mode: reset mode

The counter and its prescaler can be reinitialized in response to an event on a trigger input. Moreover, if the URS bit from the TIM_CR1 register is low, an update event UEV is generated. Then all the preloaded registers (TIM_ARR, TIM_CCRx) are updated.

In the following example, the upcounter is cleared in response to a rising edge on tim_ti1 input:

1. Configure the channel 1 to detect rising edges on tim_ti1. Configure the input filter duration (in this example, we do not need any filter, so we keep IC1F = 0000). The capture prescaler is not used for triggering, so it does not need to be configured. The CC1S bits select the input capture source only, CC1S = 01 in the TIM_CCMR1 register. Write CC1P = 0 and CC1NP = 0 in TIM_CCER register to validate the polarity (and detect rising edges only).
2. Configure the timer in reset mode by writing SMS = 100 in TIM_SMCR register. Select tim_ti1 as the input source by writing TS = 00101 in TIM_SMCR register.
3. Start the counter by writing CEN = 1 in the TIM_CR1 register.

The counter starts counting on the internal clock, then behaves normally until tim_ti1 rising edge. When tim_ti1 rises, the counter is cleared and restarts from 0. In the meantime, the trigger flag is set (TIF bit in the TIM_SR register) and an interrupt request, or a DMA request can be sent if enabled (depending on the TIE and TDE bits in TIM_DIER register).

The following figure shows this behavior when the autoreload register TIM_ARR = 0x36. The delay between the rising edge on tim_ti1 and the actual reset of the counter is due to the resynchronization circuit on tim_ti1 input.

**Figure 407. Control circuit in reset mode**: The counter counts 30, 31, 32, ... 36, 00 (natural overflow), 01, 02, 03; then tim_ti1 rises and, after resynchronization, a "Counter reset and update" pulse clears the counter to 00 (sequence continues 00, 01, 02, 03). TIF is set at the reset.

#### Slave mode: gated mode

The counter can be enabled depending on the level of a selected input.

In the following example, the upcounter counts only when tim_ti1 input is low:

1. Configure the channel 1 to detect low levels on tim_ti1. Configure the input filter duration (in this example, we do not need any filter, so we keep IC1F = 0000). The capture prescaler is not used for triggering, so it does not need to be configured. The CC1S bits select the input capture source only, CC1S = 01 in TIM_CCMR1 register. Write CC1P = 1 and CC1NP = 0 in TIM_CCER register to validate the polarity (and detect low level only).
2. Configure the timer in gated mode by writing SMS = 101 in TIM_SMCR register. Select tim_ti1 as the input source by writing TS = 00101 in TIM_SMCR register.
3. Enable the counter by writing CEN = 1 in the TIM_CR1 register (in gated mode, the counter does not start if CEN = 0, whatever is the trigger input level).

The counter starts counting on the internal clock as long as tim_ti1 is low and stops as soon as tim_ti1 becomes high. The TIF flag in the TIM_SR register is set both when the counter starts or stops.

The delay between the rising edge on tim_ti1 and the actual stop of the counter is due to the resynchronization circuit on tim_ti1 input.

**Figure 408. Control circuit in gated mode**: While tim_ti1 is low, "Counter enable" is high and the counter counts 30, 31, 32, 33; when tim_ti1 goes high the counter stops at 34; when tim_ti1 goes low again it resumes 35, 36, 37, 38. TIF is set at each start and stop (and cleared by software, "Write TIF = 0").

Note: The configuration "CCxP = CCxNP = 1" (detection of both rising and falling edges) does not have any effect in gated mode because gated mode acts on a level and not on an edge.

#### Slave mode: trigger mode

The counter can start in response to an event on a selected input.

In the following example, the upcounter starts in response to a rising edge on tim_ti2 input:

1. Configure the channel 2 to detect rising edges on tim_ti2. Configure the input filter duration (in this example, we do not need any filter, so we keep IC2F = 0000). The capture prescaler is not used for triggering, so it does not need to be configured. CC2S bits are selecting the input capture source only, CC2S = 01 in TIM_CCMR1 register. Write CC2P = 1 and CC2NP = 0 in TIM_CCER register to validate the polarity (and detect low level only).
2. Configure the timer in trigger mode by writing SMS = 110 in TIM_SMCR register. Select tim_ti2 as the input source by writing TS = 00110 in TIM_SMCR register.

When a rising edge occurs on tim_ti2, the counter starts counting on the internal clock and the TIF flag is set.

The delay between the rising edge on tim_ti2 and the actual start of the counter is due to the resynchronization circuit on tim_ti2 input.

*Digest note:* Step 1 of this example says "rising edges" but writes CC2P = 1 ("detect low level only"); text reproduced as printed.

**Figure 409. Control circuit in trigger mode**: The counter holds 34 until tim_ti2 rises; after resynchronization "Counter enable" goes high, TIF is set and the counter counts 35, 36, 37, 38.

#### Slave mode selection preload for run-time encoder mode update

The SMS[4:0] bit can be preloaded. This is enabled by setting the SMSPE enable bit in the TIM_SMCR register. The trigger for the transfer from SMS[4:0] preload to active value is the update event (UEV) occurring when the counter overflows.

#### Slave mode – combined reset + trigger mode

In this case, a rising edge of the selected trigger input (tim_trgi) reinitializes the counter, generates an update of the registers, and starts the counter.

This mode is used for one-pulse mode.

#### Slave mode – combined gated + reset mode

The counter clock is enabled when the trigger input (tim_trgi) is high. The counter stops and is reset as soon as the trigger becomes low. Both start and stop of the counter are controlled.

This mode is used to detect out-of-range PWM signal (duty cycle exceeding a maximum expected value).

#### Slave mode – external clock mode 2 + trigger mode

The external clock mode 2 can be used in addition to another slave mode (except external clock mode 1 and encoder mode). In this case, the tim_etr_in signal is used as external clock input, and another input can be selected as trigger input when operating in reset mode, gated mode, or trigger mode. It is recommended not to select tim_etr_in as tim_trgi through the TS bits of TIM_SMCR register.

In the following example, the upcounter is incremented at each rising edge of the tim_etr_in signal as soon as a rising edge of tim_ti1 occurs:

1. Configure the external trigger input circuit by programming the TIM_SMCR register as follows:
   - ETF = 0000: no filter.
   - ETPS = 00: prescaler disabled.
   - ETP = 0: detection of rising edges on tim_etr_in and ECE = 1 to enable the external clock mode 2.
2. Configure the channel 1 as follows, to detect rising edges on TI:
   - IC1F = 0000: no filter.
   - The capture prescaler is not used for triggering and does not need to be configured.
   - CC1S = 01in TIM_CCMR1 register to select only the input capture source.
   - CC1P = 0 and CC1NP = 0 in TIM_CCER register to validate the polarity (and detect rising edge only).
3. Configure the timer in trigger mode by writing SMS = 110 in TIM_SMCR register. Select tim_ti1 as the input source by writing TS = 00101 in TIM_SMCR register.

A rising edge on tim_ti1 enables the counter and sets the TIF flag. The counter then counts on tim_etr_in rising edges.

The delay between the rising edge of the tim_etr_in signal and the actual reset of the counter is due to the resynchronization circuit on tim_etrp input.

**Figure 410. Control circuit in external clock mode 2 + trigger mode**: The counter holds 34 until tim_ti1 rises; "Counter enable" then goes high and TIF is set. From then on, each rising edge of ETR produces (after resynchronization) one tim_cnt_ck/tim_psc_ck pulse and the counter steps 35, 36.

### 32.4.27 Timer synchronization

The TIMx timers are linked together internally for timer synchronization or chaining. When one timer is configured in master mode, it can reset, start, stop, or clock the counter of another timer configured in slave mode.

Figure 411 and Figure 412 show examples of master/slave timer connections.

**Figure 411. Master/Slave timer example**: In TIM_mstr, the clock drives the Prescaler and Counter; the counter's UEV feeds the "Master mode control" block (configured by MMS), whose output tim_trgo connects to the tim_itr input of TIM_slv. In TIM_slv, "Input trigger selection" (TS) picks tim_itr, and "Slave mode control" (SMS) drives CK_PSC to TIM_slv's Prescaler and Counter.

**Figure 412. Master/slave connection example with 1 channel only timers**: In TIM_mstr (a one-channel timer), Compare 1 drives "Output control", which outputs tim_oc1 (also on TIM_CH1); tim_oc1 connects to the tim_itr input of TIM_slv, where Input trigger selection (TS) and Slave mode control (SMS) drive CK_PSC.

Note: The timers with one channel only (see Figure 412) do not feature a master mode. However, the tim_oc1 output signal can serve as trigger for slave timer (see TIMx internal trigger connection table in Section 32.4.2: TIM2/TIM3/TIM4/TIM5 pins and internal signals).

The tim_oc1 signal pulse width must be programmed to be at least two clock cycles of the destination timer, to make sure the slave timer detects the trigger.

For instance, if the destination timer tim_ker_ck clock is four times slower than the source timer, the OC1 pulse width must be eight clock cycles.

#### Using one timer as prescaler for another timer

For example, TIM_mstr can be configured to act as a prescaler for TIM_slv. Refer to Figure 411. To do this:

1. Configure TIM_mstr in master mode so that it outputs a periodic trigger signal on each update event UEV. If MMS = 010 is written in the TIM_mstr_CR2 register, a rising edge is output on tim_trgo each time an update event is generated.
2. To connect the tim_trgo output of TIM_mstr to TIM_slv, TIM_slv must be configured in slave mode using ITR2 as internal trigger. This is selected through the TS bits in the TIM_slv_SMCR register (writing TS = 00010).
3. Then the slave mode controller must be put in external clock mode 1 (write SMS = 111 in the TIM_slv_SMCR register). This causes TIM_slv to be clocked by the rising edge of the periodic TIM_mstr trigger signal (which correspond to the TIM_mstr counter overflow).
4. Finally both timers must be enabled by setting their respective CEN bits (TIM_CR1 register).

Note: If tim_ocx is selected on TIM_mstr as the trigger output (MMS = 1xx), its rising edge is used to clock the counter of TIM_slv.

#### Using one timer to enable another timer

In this example, we control the enable of TIM_slv with the output compare 1 of TIM_mstr. Refer to Figure 411 for connections. TIM_slv counts on the divided internal clock only when tim_oc1ref of TIM_mstr is high. Both counter clock frequencies are divided by 3 by the prescaler compared to tim_ker_ck (ftim_cnt_ck = ftim_ker_ck/3).

1. Configure TIM_mstr master mode to send its output compare 1 reference (tim_oc1ref) signal as trigger output (MMS = 100 in the TIM_mstr_CR2 register).
2. Configure the TIM_mstr tim_oc1ref waveform (TIM_mstr_CCMR1 register).
3. Configure TIM_slv to get the input trigger from TIM_mstr (TS = 00010 in the TIM_slv_SMCR register).
4. Configure TIM_slv in gated mode (SMS = 101 in TIM_slv_SMCR register).
5. Enable TIM_slv by writing 1 in the CEN bit (TIM_slv_CR1 register).
6. Start TIM_mstr by writing 1 in the CEN bit (TIM_mstr_CR1 register).

Note: The slave timer counter clock is not synchronized with the master timer counter clock, this mode only affects the TIM_slv counter enable signal.

**Figure 413. Gating TIM_slv with tim_oc1ref of TIM_mstr**: tim_mstr_CNT counts FC, FD, FE, FF, 00, 01 (at tim_ker_ck/3). While TIM_mst_oc1ref is high, tim_slv_CNT advances 3045, 3046, 3047, 3048; the TIM_slv TIF bit is set when gating starts (and cleared by software, "Write TIF = 0").

In the example in Figure 413, the TIM_slv counter and prescaler are not initialized before being started. So they start counting from their current value. It is possible to start from a given value by resetting both timers before starting TIM_mstr. Then any value can be written in the timer counters. The timers can easily be reset by software using the UG bit in the TIM_EGR registers.

In the next example (refer to Figure 414), we synchronize TIM_mstr and TIM_slv. TIM_mstr is the master and starts from 0. TIM_slv is the slave and starts from 0xE7. The prescaler ratio is the same for both timers. TIM_slv stops when TIM_mstr is disabled by writing 0 to the CEN bit in the TIM_mstr_CR1 register:

1. Configure TIM_mstr master mode to send its output compare 1 reference (tim_oc1ref) signal as trigger output (MMS = 100 in the TIM_mstr_CR2 register).
2. Configure the TIM_mstr tim_oc1ref waveform (TIM_mstr_CCMR1 register).
3. Configure TIM_slv to get the input trigger from TIM_mstr (TS = 00010 in the TIM_slv_SMCR register).
4. Configure TIM_slv in gated mode (SMS = 101 in TIM_slv_SMCR register).
5. Reset TIM_mstr by writing 1 in UG bit (TIM_mstr_EGR register).
6. Reset TIM_slv by writing 1 in UG bit (TIM_slv_EGR register).
7. Initialize TIM_slv to 0xE7 by writing 0xE7 in the TIM_slv counter (TIM_slv_CNT).
8. Enable TIM_slv by writing 1 in the CEN bit (TIM_slv_CR1 register).
9. Start TIM_mstr by writing 1 in the CEN bit (TIM_mstr_CR1 register).
10. Stop TIM_mstr by writing 0 in the CEN bit (TIM_mstr_CR1 register).

**Figure 414. Gating TIM_slv with Enable of TIM_mstr**: tim_mstr_CNT is at 75 and is reset to 00 ("tim_mstr_CNT reset"); tim_slv_CNT is at AB, is reset to 00 ("tim_slv_CNT reset") and then written to E7 ("tim_slv_CNT write"). When the TIM_mst counter enable (CEN bit) goes high, both counters start: tim_mstr_CNT 00, 01, 02 and tim_slv_CNT E7, E8, E9. The TIM_slv TIF bit is set at the start (cleared by software, "Write TIF = 0").

#### Using one timer to start another timer

In this example, we set the enable of TIM_slv with the update event of TIM_mstr. Refer to Figure 411 for connections. TIM_slv starts counting from its current value (which can be nonzero) on the divided internal clock as soon as the update event is generated by TIM_mstr. When TIM_slv receives the trigger signal its CEN bit is automatically set and the counter counts until we write 0 to the CEN bit in the TIM_slv_CR1 register. Both counter clock frequencies are divided by 3 by the prescaler compared to tim_ker_ck (ftim_cnt_ck = ftim_ker_ck/3).

1. Configure TIM_mstr master mode to send its update event (UEV) as trigger output (MMS = 010 in the TIM_mstr_CR2 register).
2. Configure the TIM_mstr period (TIM_mstr_ARR registers).
3. Configure TIM_slv to get the input trigger from TIM_mstr (TS = 00010 in the TIM_slv_SMCR register).
4. Configure TIM_slv in trigger mode (SMS = 110 in TIM_slv_SMCR register).
5. Start TIM_mstr by writing 1 in the CEN bit (TIM_mstr_CR1 register).

**Figure 415. Triggering TIM_slv with update of TIM_mstr**: tim_mst_CNT counts FD, FE, FF, 00, 01, 02. At the FF to 00 rollover a TIM_mstr UEV event occurs; TIM_slv counter enable (CEN bit) is then set automatically, the TIM_slv TIF bit is set, and tim_slv_CNT advances from 45 to 46, 47, 48.

As in the previous example, both counters can be initialized before starting counting. Figure 416 shows the behavior with the same configuration as in Figure 415 but in trigger mode (SMS = 110 in the TIM_slv_SMCR register) instead of gated mode.

**Figure 416. Triggering TIM_slv with Enable of TIM_mstr**: tim_mstr_CNT is at 75 and is reset to 00; tim_slv_CNT is at CD, is reset to 00 and then written to E7. When the TIM_mst counter enable (CEN bit) is set, tim_mstr_CNT counts 00, 01, 02 and tim_slv_CNT counts E7, E8, E9, EA. The TIM_slv TIF bit is set when the trigger is received.

#### Starting two timers synchronously in response to an external trigger

In this example, we set the enable of TIM_mstr when its tim_ti1 input rises, and the enable of TIM_slv with the enable of TIM_mstr. Refer to Figure 411 for connections. To ensure the counters are aligned, TIM_mstr must be configured in master/slave mode (slave with respect to tim_ti1, master with respect to TIM_slv):

1. Configure TIM_mstr master mode to send its enable as trigger output (MMS = 001 in the TIM_mstr_CR2 register).
2. Configure TIM_mstr slave mode to get the input trigger from tim_ti1 (TS = 00100 in the TIM_mstr_SMCR register).
3. Configure TIM_mstr in trigger mode (SMS = 110 in the TIM_mstr_SMCR register).
4. Configure the TIM_mstr in master/slave mode by writing MSM = 1 (TIM_mstr_SMCR register).
5. Configure TIM_slv to get the input trigger from TIM_mstr (TS = 00000 in the TIM_slv_SMCR register).
6. Configure TIM_slv in trigger mode (SMS = 110 in the TIM_slv_SMCR register).

When a rising edge occurs on tim_ti1 (TIM_mstr), both counters start counting synchronously on the internal clock and both TIF flags are set.

Note: In this example both timers are initialized before starting (by setting their respective UG bits). Both counters starts from 0, but an offset can easily be inserted between them by writing any of the counter registers (TIM_CNT). One can see that the master/slave mode inserts a delay between CNT_EN and CK_PSC on TIM_mstr.

**Figure 417. Triggering TIM_mstr and TIM_slv with TIM_mstr tim_ti1 input**: When tim_mstr_ti1 rises, the TIM_mst counter enable (CEN bit) is set and the TIM_mstr TIF bit is set; shortly after, the TIM_slv counter enable (CEN bit) and the TIM_slv TIF bit are set. Because of the master/slave delay on TIM_mstr, tim_mstr_psc_ck and tim_slv_psc_ck start on the same tim_ker_ck edge, and both tim_mstr_CNT and tim_slv_CNT count 00, 01, 02, ... 09 in lockstep.

Note: The clock of the slave peripherals (such as timer, ADC) receiving the tim_trgo signal must be enabled prior to receive events from the master timer, and the clock frequency (prescaler) must not be changed on-the-fly while triggers are received from the master timer.

### 32.4.28 ADC triggers

The timer can generate an ADC triggering event with various internal signals, such as reset, enable or compare events.

Note: The clock of the slave peripherals (such as timer, ADC) receiving the tim_trgo signal must be enabled prior to receive events from the master timer, and the clock frequency (prescaler) must not be changed on-the-fly while triggers are received from the master timer.

### 32.4.29 ADC synchronization

The timer operation can be synchronized to the ADC clock to trigger jitter-free ADC sampling. This function is enabled using the ADSYNC bit in the TIM_CR2 register.

This feature is useful when the timers and the ADCs are operating with semisynchronous clocks (clocks derived from a same source with integer ratio tim_ker_ck/adc_ker_ck), for instance adc_ker_ck = 75 MHz and tim_ker_ck = 150 MHz or 300 MHz.

ADSYNC must also be set when both peripherals are operating at the same frequency from the same clock source, when jitter-free operation is needed.

ADSYNC must not be set and jitter-free operation is not supported in the following cases:

- When the clock ratio is not an integer (for example adc_ker_ck = 75 MHz and tim_ker_ck = 100 MHz): in this case, the sampling point jitter due to the timer to ADC signal resynchronization is 1 adc_ker_ck period maximum.
- When the ADC is operating in asynchronous mode (adc_ker_ck uncorrelated with tim_ker_ck): in this case, the sampling point jitter due to the timer to ADC signal resynchronization is 1 adc_ker_ck period maximum.

When ADSYNC = 1, the timer operation is slightly changed: the counter enable and counter reset events are aligned to the adc_ker_ck ADC clock, to avoid any phase shift due to clocks enable in the RCC.

Jitter-free operation is guaranteed only when one of the two requirements below is met (depending on the selected trigger source):

1. The counter period must be a multiple of the ADC clock period: (TIM_PSC + 1) × (TIM_ARR + 1) × T_tim_ker_ck = n × T_adc_ker_ck
2. The compare value must be a multiple of the ADC clock period: (TIM_PSC + 1) × TIM_CMPy × T_tim_ker_ck = m × T_adc_ker_ck

Note: If none of the two above requirements is met, the trigger is still generated, but the latency is not constant and varies with the timer and ADC clocks phase shift.

#### Programming guidelines

The ADC synchronization feature must not be modified during run-time, once the counter is enabled and once the ADC has been configured for receiving triggers from the timer.

It is mandatory to follow the procedure below to use the ADC synchronization:

1. Enable the destination ADC clock.
2. Configure the timer and set the ADSYNC bit.
3. Configure the ADC and enable it (using ADSTART and/or JADSTART bits).
4. Start the timer (with the CEN counter enable bit).

### 32.4.30 DMA burst mode

The TIMx timers have the capability to generate multiple DMA requests upon a single event. The main purpose is to be able to reprogram part of the timer multiple times without software overhead, but it can also be used to read several registers in a row, at regular intervals.

The DMA controller destination is unique and must point to the virtual register TIM_DMAR. On a given timer event, the timer launches a sequence of DMA requests (burst). Each write into the TIM_DMAR register is actually redirected to one of the timer registers.

The DBL[4:0] bits in the TIM_DCR register set the DMA burst length. The timer recognizes a burst transfer when a read or a write access is done to the TIM_DMAR address), i.e. the number of transfers (either in half-words or in bytes).

The DBA[4:0] bits in the TIM_DCR registers define the DMA base address for DMA transfers (when read/write accesses are done through the TIM_DMAR address). DBA is defined as an offset starting from the address of the TIM_CR1 register:

Example:

- 00000: TIM_CR1
- 00001: TIM_CR2
- 00010: TIM_SMCR

The DBSS[3:0] bits in the TIM_DCR register defines the interrupt source that triggers the DMA burst transfers (see Section 32.5.23: TIM DMA control register (TIM_DCR) for details).

As an example, the timer DMA burst feature is used to update the contents of the CCRx registers (x = 2, 3, 4) upon an update event, with the DMA transferring half words into the CCRx registers.

This is done in the following steps:

1. Configure the corresponding DMA channel as follows:
   - DMA channel peripheral address is the DMAR register address.
   - DMA channel memory address is the address of the buffer in the RAM containing the data to be transferred by DMA into CCRx registers.
   - Number of data to transfer = 3 (See note below).
   - Circular mode disabled.
2. Configure the DCR register by configuring the DBA and DBL bitfields as follows: DBL = 3, DBA = 0xE and DBSS = 1.
3. Enable the TIMx update DMA request (set the UDE bit in the DIER register).
4. Enable TIMx.
5. Enable the DMA channel.

This example is for the case where every CCRx register has to be updated once. If every CCRx register is to be updated twice for example, the number of data to transfer must be 6. Let's take the example of a buffer in the RAM containing data1, data2, data3, data4, data5, and data6. The data is transferred to the CCRx registers as follows: on the first update DMA request, data1 is transferred to CCR2, data2 is transferred to CCR3, data3 is transferred to CCR4 and on the second update DMA request, data4 is transferred to CCR2, data5 is transferred to CCR3, and data6 is transferred to CCR4.

Note: A null value can be written to the reserved registers.

### 32.4.31 TIM2/TIM3/TIM4/TIM5 DMA requests

The TIM2/TIM3/TIM4/TIM5 can generate a DMA requests, as shown in Table 323.

**Table 323. DMA request**

| DMA request signal | DMA request | Enable control bit |
|---|---|---|
| tim_upd_dma | Update | UDE |
| tim_cc1_dma | Capture/compare 1 | CC1DE |
| tim_cc2_dma | Capture/compare 2 | CC2DE |
| tim_cc3_dma | Capture/compare 3 | CC3DE |
| tim_cc4_dma | Capture/compare 4 | CC4DE |
| tim_trgi_dma | Trigger | TDE |

Note: Some timer's DMA requests may not be connected to the DMA controller. Refer to the DMA section(s) for more details.

### 32.4.32 Debug mode

When the microcontroller enters debug mode (Cortex-M33 core halted), the TIMx counter can either continue to work normally or stops.

The behavior in debug mode can be programmed with a dedicated configuration bit per timer in the Debug support (DBG) module.

For more details, refer to section Debug support (DBG).

### 32.4.33 TIM2/TIM3/TIM4/TIM5 low-power modes

**Table 324. Effect of low-power modes on TIM2/TIM3/TIM4/TIM5**

| Mode | Description |
|---|---|
| Sleep | No effect, peripheral is active. The interrupts can cause the device to exit from Sleep mode. |
| Stop | The timer operation is stopped and the register content is kept. No interrupt can be generated. |
| Standby | The timer is powered-down and must be reinitialized after exiting the Standby mode. |

### 32.4.34 TIM2/TIM3/TIM4/TIM5 interrupts

The TIM2/TIM3/TIM4/TIM5 can generate multiple interrupts, as shown in Table 325.

**Table 325. Interrupt requests**

| Interrupt acronym | Interrupt event | Event flag | Enable control bit | Interrupt clear method | Exit from Sleep mode | Exit from Stop and Standby mode |
|---|---|---|---|---|---|---|
| TIM_UPD | Update | UIF | UIE | write 0 in UIF | Yes | No |
| TIM_CC | Capture/compare 1 | CC1IF | CC1IE | write 0 in CC1IF | Yes | No |
| TIM_CC | Capture/compare 2 | CC2IF | CC2IE | write 0 in CC2IF | Yes | No |
| TIM_CC | Capture/compare 3 | CC3IF | CC3IE | write 0 in CC3IF | Yes | No |
| TIM_CC | Capture/compare 4 | CC4IF | CC4IE | write 0 in CC4IF | Yes | No |
| TIM_TRGI | Trigger | TIF | TIE | write 0 in TIF | Yes | No |
| TIM_DIR_IDX | Index | IDXF | IDXIE | write 0 in IDXF | Yes | No |
| TIM_DIR_IDX | Direction | DIRF | DIRIE | write 0 in DIRF | Yes | No |
| TIM_IERR | Index Error | IERRF | IERRIE | write 0 in IERRF | Yes | No |
| TIM_TERR | Transition Error | TERRF | TERRIE | write 0 in TERRF | Yes | No |

## 32.5 TIM2/TIM3/TIM4/TIM5 registers

Refer to Section 1.2 for a list of abbreviations used in register descriptions.

The peripheral registers can be accessed by half-words (16-bit) or words (32-bit).

*Digest note:* The STM32C552 CMSIS header (stm32c552xx.h) uses a single TIM_TypeDef and a single set of TIM_* bit definitions shared by all timer types (advanced, general-purpose, basic). It therefore declares registers and bits that do not exist on TIM2/TIM3/TIM4/TIM5 (for example RCR at 0x030, BDTR at 0x044, CCR5/CCR6/CCMR3/DTR2, TIM_CR1.TGO2PSC, TIM_CR2.OIS*, CCxNE/CCxNP-related complementary outputs, COM/break flags). Those are reserved in this chapter; the bit positions of the fields that do exist here match the header unless stated otherwise.

### 32.5.1 TIM control register 1 (TIM_CR1)

Address offset: 0x000. Reset value: 0x0000 0000. All fields rw.

- **Bits 31:28** Reserved, must be kept at reset value.
- **Bits 27:24 CKD2[3:0]** (rw): Clock division 2. This bit field indicates the division between sampling clock (tDTS) used by the dead-time generators and the digital filters (tim_etr_in, tim_tix).
  - 0000: No Division
  - 0001: tDTS2 = 4*tDTS
  - 0010: tDTS2 = 16*tDTS
  - 0011: tDTS2 = 64*tDTS
  - 0100: tDTS2 = 256*tDTS
  - 0101: tDTS2 = 1024*tDTS
  - 0110: tDTS2 = 4096*tDTS
  - 0111: tDTS2 = 16384*tDTS
  - 1000: tDTS2 = 65536*tDTS
  - 1001: tDTS2 = 262144*tDTS
  - Others: Reserved, do not program this value
- **Bits 23:13** Reserved, must be kept at reset value.
- **Bit 12 DITHEN** (rw): Dithering Enable
  - 0: Dithering disabled
  - 1: Dithering enabled
  - Note: The DITHEN bit can only be modified when CEN bit is reset.
- **Bit 11 UIFREMAP** (rw): UIF status bit remapping
  - 0: No remapping. UIF status bit is not copied to TIM_CNT register bit 31.
  - 1: Remapping enabled. UIF status bit is copied to TIM_CNT register bit 31.
- **Bit 10** Reserved, must be kept at reset value.
- **Bits 9:8 CKD[1:0]** (rw): Clock division. This bitfield indicates the division ratio between the timer clock (tim_ker_ck) frequency and sampling clock used by the digital filters (tim_etr_in, tim_tix),
  - 00: tDTS = ttim_ker_ck
  - 01: tDTS = 2 × ttim_ker_ck
  - 10: tDTS = 4 × ttim_ker_ck
  - 11: tDTS = 8 × ttim_ker_ck
- **Bit 7 ARPE** (rw): Autoreload preload enable
  - 0: TIM_ARR register is not buffered
  - 1: TIM_ARR register is buffered
- **Bits 6:5 CMS[1:0]** (rw): Center-aligned mode selection
  - 00: Edge-aligned mode. The counter counts up or down depending on the direction bit (DIR).
  - 01: Center-aligned mode 1. The counter counts up and down alternatively. Output compare interrupt flags of channels configured in output (CCxS = 00 in TIM_CCMRx register) are set only when the counter is counting down.
  - 10: Center-aligned mode 2. The counter counts up and down alternatively. Output compare interrupt flags of channels configured in output (CCxS = 00 in TIM_CCMRx register) are set only when the counter is counting up.
  - 11: Center-aligned mode 3. The counter counts up and down alternatively. Output compare interrupt flags of channels configured in output (CCxS = 00 in TIM_CCMRx register) are set both when the counter is counting up or down.
  - Note: It is not allowed to switch from edge-aligned mode to center-aligned mode as long as the counter is enabled (CEN = 1)
- **Bit 4 DIR** (rw): Direction
  - 0: Counter used as upcounter
  - 1: Counter used as downcounter
  - Note: This bit is read only when the timer is configured in center-aligned mode or encoder mode.
- **Bit 3 OPM** (rw): One-pulse mode
  - 0: Counter is not stopped at update event
  - 1: Counter stops counting at the next update event (clearing the bit CEN)
- **Bit 2 URS** (rw): Update request source. This bit is set and cleared by software to select the UEV event sources.
  - 0: Any of the following events generate an update interrupt or DMA request if enabled. These events can be: Counter overflow/underflow; Setting the UG bit; Update generation through the slave mode controller
  - 1: Only counter overflow/underflow generates an update interrupt or DMA request if enabled.
- **Bit 1 UDIS** (rw): Update disable. This bit is set and cleared by software to enable/disable UEV event generation.
  - 0: UEV enabled. The Update (UEV) event is generated by one of the following events: Counter overflow/underflow; Setting the UG bit; Update generation through the slave mode controller. Buffered registers are then loaded with their preload values.
  - 1: UEV disabled. The Update event is not generated, shadow registers keep their value (ARR, PSC, CCRx). However the counter and the prescaler are reinitialized if the UG bit is set or if a hardware reset is received from the slave mode controller.
- **Bit 0 CEN** (rw): Counter enable
  - 0: Counter disabled
  - 1: Counter enabled
  - Note: External clock, gated mode and encoder mode can work only if the CEN bit has been previously set by software. However trigger mode can set the CEN bit automatically by hardware. CEN is cleared automatically in one-pulse mode, when an update event occurs.

*Digest note:* The CMSIS header additionally defines TIM_CR1_TGO2PSC at bit 16 (an advanced-timer bit); on TIM2/TIM3/TIM4/TIM5 bits 23:13 are reserved per the RM. All other TIM_CR1 positions match the header (CEN 0, UDIS 1, URS 2, OPM 3, DIR 4, CMS 6:5, ARPE 7, CKD 9:8, UIFREMAP 11, DITHEN 12, CKD2 27:24).

### 32.5.2 TIM control register 2 (TIM_CR2)

Address offset: 0x004. Reset value: 0x0000 0000. All fields rw.

- **Bit 31 TI3INV** (rw): tim_ti3 signal inversion on XOR gate input
  - 0: tim_ti3 non-inverted
  - 1: tim_ti3 inverted
- **Bit 30 TI2INV** (rw): tim_ti2 signal inversion on XOR gate input
  - 0: tim_ti2 non-inverted
  - 1: tim_ti2 inverted
- **Bit 29 TI1INV** (rw): tim_ti1 signal inversion on XOR gate input
  - 0: tim_ti1 non-inverted
  - 1: tim_ti1 inverted
- **Bit 28 ADSYNC** (rw): ADC synchronization
  - 0: The timer operates independently from the ADC
  - 1: The timer operation is synchronized with the ADC clock to provide jitter-free sampling point. This mode can be enabled only with specific ADC / timer clock relationship. Refer to Section 32.4.29 for requirements.
  - The ADSYNC must not modified when the counter is enabled (CEN bit is set).
- **Bit 27 XORPS** (rw): XOR gate position selection. This bit defines the position of the XOR gate with respect to input filters.
  - 0: XOR gate placed before TI1 filter
  - 1: XOR gate placed after TI1, TI2 and TI3 filters
- **Bit 26** Reserved, must be kept at reset value.
- **Bit 25 MMS[3]** (rw): Master mode selection, most significant bit (see MMS[3:0] below).
- **Bits 24:8** Reserved, must be kept at reset value.
- **Bit 7 TI1S** (rw): tim_ti1 selection. This bit enables the insertion of a XOR gate to combine tim_ti1_in[15:0], tim_ti2_in[15:0], and tim_ti3_in[15:0] inputs into tim_ti1. The position of the XOR gate, with respect to input filters, is defined with the XORPS bit.
  - 0: The tim_ti1_in[15:0] multiplexer output is to tim_ti1 input
  - 1: The tim_ti1_in[15:0], tim_ti2_in[15:0] and tim_ti3_in[15:0] multiplexers outputs are XORed and connected to the tim_ti1 input. See also Section 31.3.34: Interfacing with Hall sensors.
- **Bits 25, 6, 5, 4 MMS[3:0]** (rw): Master mode selection. These bits are used to select the information to be sent in master mode to slave timers for synchronization (tim_trgo). MMS[3] is bit 25, MMS[2:0] are bits 6:4. The combination is as follows:
  - 0000: Reset - the UG bit from the TIM_EGR register is used as trigger output (tim_trgo). If the reset is generated by the trigger input (slave mode controller configured in reset mode) then the signal on tim_trgo is delayed compared to the actual reset.
  - 0001: Enable - the Counter enable signal, CNT_EN, is used as trigger output (tim_trgo). It is useful to start several timers at the same time or to control a window in which a slave timer is enabled. The Counter Enable signal is generated by a logic AND between CEN control bit and the trigger input when configured in gated mode. When the Counter Enable signal is controlled by the trigger input, there is a delay on tim_trgo, except if the master/slave mode is selected (see the MSM bit description in TIM_SMCR register).
  - 0010: Update - The update event is selected as trigger output (tim_trgo). For instance a master timer can then be used as a prescaler for a slave timer.
  - 0011: Compare pulse - The trigger output send a positive pulse when the CC1IF flag is to be set (even if it was already high), as soon as a capture or a compare match occurred (tim_trgo).
  - 0100: Compare - tim_oc1refc signal is used as trigger output (tim_trgo)
  - 0101: Compare - tim_oc2refc signal is used as trigger output (tim_trgo)
  - 0110: Compare - tim_oc3refc signal is used as trigger output (tim_trgo)
  - 0111: Compare - tim_oc4refc signal is used as trigger output (tim_trgo)
  - 1000: Encoder clock output - The encoder clock signal is used as trigger output (tim_trgo). This code is valid for the following SMS[4:0] values: 00001, 00010, 00011, 01010, 01011, 01100, 01101, 01110, 01111. Any other SMS[4:0] code is not allowed and may lead to unexpected behavior.
  - Others: Reserved
  - Note: The clock of the slave timer or ADC must be enabled prior to receive events from the master timer, and must not be changed on-the-fly while triggers are received from the master timer.
- **Bit 3 CCDS** (rw): Capture/compare DMA selection
  - 0: CCx DMA request sent when CCx event occurs
  - 1: CCx DMA requests sent when update event occurs
- **Bits 2:0** Reserved, must be kept at reset value.

*Digest note:* The RM text lists "Bit 26 Reserved" and "Bits 24:8 Reserved" and describes bit 25 only under "Bits 25, 6, 5, 4 MMS[3:0]"; the bit diagram shows MMS[3] at bit 25. The header agrees (TIM_CR2_MMS_3 = 0x02000000). The header also defines advanced-timer bits (CCPC, CCUS, OIS*, MMS2) that are reserved here.

### 32.5.3 TIM slave mode control register (TIM_SMCR)

Address offset: 0x008. Reset value: 0x0000 0000. All fields rw.

- **Bits 31:30** Reserved, must be kept at reset value.
- **Bits 29:26 SETPS[3:0]** (rw): Synchronous external trigger prescaler. The linear synchronous prescaler divides the frequency of the tim_etrf signal, by a factor (SETPS[3:0] + 1).
- **Bit 25 SMSPS** (rw): SMS preload source. This bit selects whether the events that triggers the SMS[4:0] bitfield transfer from preload to active
  - 0: The transfer is triggered by the Timer's Update event
  - 1: The transfer is triggered by the Index event
- **Bit 24 SMSPE** (rw): SMS preload enable. This bit selects whether the SMS[4:0] bitfield is preloaded
  - 0: SMS[4:0] bitfield is not preloaded
  - 1: SMS[4:0] preload is enabled
- **Bits 23:22** Reserved, must be kept at reset value.
- **Bits 21:20 TS[4:3]** (rw): Trigger selection, upper bits (see TS[4:0] below).
- **Bits 19:18** Reserved, must be kept at reset value.
- **Bits 17:16 SMS[4:3]** (rw): Slave mode selection, upper bits (see SMS[4:0] below).
- **Bit 15 ETP** (rw): External trigger polarity. This bit selects whether tim_etr_in or tim_etr_in is used for trigger operations
  - 0: tim_etr_in is non-inverted, active at high level or rising edge
  - 1: tim_etr_in is inverted, active at low level or falling edge
- **Bit 14 ECE** (rw): External clock enable. This bit enables external clock mode 2.
  - 0: External clock mode 2 disabled
  - 1: External clock mode 2 enabled. The counter is clocked by any active edge on the tim_etrf signal.
  - Note: Setting the ECE bit has the same effect as selecting external clock mode 1 with tim_trgi connected to tim_etrf (SMS = 111 and TS = 00111). It is possible to simultaneously use external clock mode 2 with the following slave modes: reset mode, gated mode and trigger mode. Nevertheless, tim_trgi must not be connected to tim_etrf in this case (TS bits must not be 00111). If external clock mode 1 and external clock mode 2 are enabled at the same time, the external clock input is tim_etrf.
- **Bits 13:12 ETPS[1:0]** (rw): External trigger prescaler. External trigger signal tim_etrp frequency must be at most 1/4 of tim_ker_ck frequency. A prescaler can be enabled to reduce tim_etrp frequency. It is useful when inputting fast external clocks on tim_etr_in.
  - 00: Prescaler OFF
  - 01: tim_etrp frequency divided by 2
  - 10: tim_etrp frequency divided by 4
  - 11: tim_etrp frequency divided by 8
- **Bits 11:8 ETF[3:0]** (rw): External trigger filter. This bitfield then defines the frequency used to sample tim_etrp signal and the length of the digital filter applied to tim_etrp. The digital filter is made of an event counter in which N consecutive events are needed to validate a transition on the output:
  - 0000: No filter, sampling is done at fDTS
  - 0001: fSAMPLING = ftim_ker_ck, N = 2
  - 0010: fSAMPLING = ftim_ker_ck, N = 4
  - 0011: fSAMPLING = ftim_ker_ck, N = 8
  - 0100: fSAMPLING = fDTS/2, N = 6
  - 0101: fSAMPLING = fDTS/2, N = 8
  - 0110: fSAMPLING = fDTS/4, N = 6
  - 0111: fSAMPLING = fDTS/4, N = 8
  - 1000: fSAMPLING = fDTS/8, N = 6
  - 1001: fSAMPLING = fDTS/8, N = 8
  - 1010: fSAMPLING = fDTS/16, N = 5
  - 1011: fSAMPLING = fDTS/16, N = 6
  - 1100: fSAMPLING = fDTS/16, N = 8
  - 1101: fSAMPLING = fDTS/32, N = 5
  - 1110: fSAMPLING = fDTS/32, N = 6
  - 1111: fSAMPLING = fDTS/32, N = 8
- **Bit 7 MSM** (rw): Master/slave mode
  - 0: No action
  - 1: The effect of an event on the trigger input (tim_trgi) is delayed to allow a perfect synchronization between the current timer and its slaves (through tim_trgo). It is useful if we want to synchronize several timers on a single external event.
- **Bits 21, 20, 6, 5, 4 TS[4:0]** (rw): Trigger selection. TS[4:3] are bits 21:20, TS[2:0] are bits 6:4. This bitfield selects the trigger input to be used to synchronize the counter.
  - 00000: Internal trigger 0 (tim_itr0)
  - 00001: Internal trigger 1 (tim_itr1)
  - 00010: Internal trigger 2 (tim_itr2)
  - 00011: Internal trigger 3 (tim_itr3)
  - 00100: tim_ti1 edge detector (tim_ti1f_ed)
  - 00101: Filtered timer input 1 (tim_ti1fp1)
  - 00110: Filtered timer input 2 (tim_ti2fp2)
  - 00111: External trigger input (tim_etrf)
  - 01000: Internal trigger 4 (tim_itr4)
  - 01001: Internal trigger 5 (tim_itr5)
  - 01010: Internal trigger 6 (tim_itr6)
  - 01011: Internal trigger 7 (tim_itr7)
  - 01100: Internal trigger 8 (tim_itr8)
  - 01101: Internal trigger 9 (tim_itr9)
  - 01110: Internal trigger 10 (tim_itr10)
  - 01111: Internal trigger 11 (tim_itr11)
  - 10000: Internal trigger 12 (tim_itr12)
  - 10001: Internal trigger 13 (tim_itr13)
  - 10010: Internal trigger 14 (tim_itr14)
  - 10011: Internal trigger 15 (tim_itr15)
  - 10100: Internal trigger 16 (tim_itr16)
  - 10101: Internal trigger 17 (tim_itr17)
  - 10110: Internal trigger 18 (tim_itr18)
  - 10111: Internal trigger 19 (tim_itr19)
  - 11000: Internal trigger 20 (tim_itr20)
  - 11001: Internal trigger 21 (tim_itr21)
  - 11010: Internal trigger 22 (tim_itr22)
  - 11011: Internal trigger 23 (tim_itr23)
  - 11100: Internal trigger 24 (tim_itr24)
  - 11101: Internal trigger 25 (tim_itr25)
  - 11110: Internal trigger 26 (tim_itr26)
  - 11111: Internal trigger 27 (tim_itr27)
  - See Section 32.4.2: TIM2/TIM3/TIM4/TIM5 pins and internal signals for product specific implementation details.
  - Note: These bits must be changed only when they are not used (for example when SMS = 000) to avoid wrong edge detections at the transition.
- **Bit 3 OCCS** (rw): OCREF clear selection. This bit is used to select the OCREF clear source
  - 0: tim_ocref_clr_int is connected to the tim_ocref_clr input
  - 1: tim_ocref_clr_int is connected to tim_etrf
  - Note: If the OCREF clear selection feature is not supported, this bit is reserved and forced by hardware to 0. Section 32.3: TIM2/TIM3/TIM4/TIM5 implementation.
- **Bits 17:16, 2:0 SMS[4:0]** (rw): Slave mode selection. SMS[4:3] are bits 17:16, SMS[2:0] are bits 2:0. When external signals are selected the active edge of the trigger signal (tim_trgi) is linked to the polarity selected on the external input (refer to ETP bit in TIM_SMCR for tim_etr_in and CCxP/CCxNP bits in TIM_CCER register for tim_ti1fp1 and tim_ti2fp2).
  - 00000: Slave mode disabled - if CEN = 1 then the prescaler is clocked directly by the internal clock.
  - 00001: Encoder mode 1 - Counter counts up/down on tim_ti1fp1 edge depending on tim_ti2fp2 level.
  - 00010: Encoder mode 2 - Counter counts up/down on tim_ti2fp2 edge depending on tim_ti1fp1 level.
  - 00011: Encoder mode 3 - Counter counts up/down on both tim_ti1fp1 and tim_ti2fp2 edges depending on the level of the other input.
  - 00100: Reset mode - Rising edge of the selected trigger input (tim_trgi) reinitializes the counter and generates an update of the registers.
  - 00101: Gated mode - The counter clock is enabled when the trigger input (tim_trgi) is high. The counter stops (but is not reset) as soon as the trigger becomes low. Both start and stop of the counter are controlled.
  - 00110: Trigger mode - The counter starts at a rising edge of the trigger tim_trgi (but it is not reset). Only the start of the counter is controlled.
  - 00111: External clock mode 1 - Rising edges of the selected trigger (tim_trgi) clock the counter.
  - 01000: Combined reset + trigger mode - Rising edge of the selected trigger input (tim_trgi) reinitializes the counter, generates an update of the registers and starts the counter.
  - 01001: Combined gated + reset mode - The counter clock is enabled when the trigger input (tim_trgi) is high. The counter stops and is reset) as soon as the trigger becomes low. Both start and stop of the counter are controlled.
  - 01010: Encoder mode: Clock plus direction, x2 mode.
  - 01011: Encoder mode: Clock plus direction, x1 mode, tim_ti2fp2 edge sensitivity is set by CC2P.
  - 01100: Encoder mode: Directional clock, x2 mode.
  - 01101: Encoder mode: Directional clock, x1 mode, tim_ti1fp1 and tim_ti2fp2 edge sensitivity is set by CC1P and CC2P.
  - 01110: Quadrature encoder mode: x1 mode, counting on tim_ti1fp1 edges only, edge sensitivity is set by CC1P.
  - 01111: Quadrature encoder mode: x1 mode, counting on tim_ti2fp2 edges only, edge sensitivity is set by CC2P.
  - 10000: Quadrature encoder with built-in debouncer: x2 mode.
  - 10001: Quadrature encoder with built-in debouncer: x4 mode.
  - Note: The gated mode must not be used if tim_ti1f_ed is selected as the trigger input (TS = 00100). Indeed, tim_ti1f_ed outputs 1 pulse for each transition on tim_ti1f, whereas the gated mode checks the level of the trigger signal.
  - Note: The clock of the slave peripherals (such as timer, ADC) receiving the tim_trgo signal must be enabled prior to receive events from the master timer, and the clock frequency (prescaler) must not be changed on-the-fly while triggers are received from the master timer.

*Digest note:* Header masks agree: TIM_SMCR_SMS_Msk = 0x00030007, TIM_SMCR_TS_Msk = 0x00300070, SMSPE bit 24, SMSPS bit 25, SETPS bits 29:26.

### 32.5.4 TIM DMA/interrupt enable register (TIM_DIER)

Address offset: 0x00C. Reset value: 0x0000 0000. All fields rw.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bit 23 TERRIE** (rw): Transition error interrupt enable
  - 0: Transition error interrupt disabled
  - 1: Transition error interrupt enabled
- **Bit 22 IERRIE** (rw): Index error interrupt enable
  - 0: Index error interrupt disabled
  - 1: Index error interrupt enabled
- **Bit 21 DIRIE** (rw): Direction change interrupt enable
  - 0: Direction change interrupt disabled
  - 1: Direction change interrupt enabled
- **Bit 20 IDXIE** (rw): Index interrupt enable
  - 0: Index interrupt disabled
  - 1: Index interrupt enabled
- **Bits 19:15** Reserved, must be kept at reset value.
- **Bit 14 TDE** (rw): Trigger DMA request enable
  - 0: Trigger DMA request disabled.
  - 1: Trigger DMA request enabled.
- **Bit 13** Reserved, must be kept at reset value.
- **Bit 12 CC4DE** (rw): Capture/compare 4 DMA request enable
  - 0: CC4 DMA request disabled.
  - 1: CC4 DMA request enabled.
- **Bit 11 CC3DE** (rw): Capture/compare 3 DMA request enable
  - 0: CC3 DMA request disabled.
  - 1: CC3 DMA request enabled.
- **Bit 10 CC2DE** (rw): Capture/compare 2 DMA request enable
  - 0: CC2 DMA request disabled.
  - 1: CC2 DMA request enabled.
- **Bit 9 CC1DE** (rw): Capture/compare 1 DMA request enable
  - 0: CC1 DMA request disabled.
  - 1: CC1 DMA request enabled.
- **Bit 8 UDE** (rw): Update DMA request enable
  - 0: Update DMA request disabled.
  - 1: Update DMA request enabled.
- **Bit 7** Reserved, must be kept at reset value.
- **Bit 6 TIE** (rw): Trigger interrupt enable
  - 0: Trigger interrupt disabled.
  - 1: Trigger interrupt enabled.
- **Bit 5** Reserved, must be kept at reset value.
- **Bit 4 CC4IE** (rw): Capture/compare 4 interrupt enable
  - 0: CC4 interrupt disabled.
  - 1: CC4 interrupt enabled.
- **Bit 3 CC3IE** (rw): Capture/compare 3 interrupt enable
  - 0: CC3 interrupt disabled.
  - 1: CC3 interrupt enabled.
- **Bit 2 CC2IE** (rw): Capture/compare 2 interrupt enable
  - 0: CC2 interrupt disabled.
  - 1: CC2 interrupt enabled.
- **Bit 1 CC1IE** (rw): Capture/compare 1 interrupt enable
  - 0: CC1 interrupt disabled.
  - 1: CC1 interrupt enabled.
- **Bit 0 UIE** (rw): Update interrupt enable
  - 0: Update interrupt disabled.
  - 1: Update interrupt enabled.

### 32.5.5 TIM status register (TIM_SR)

Address offset: 0x010. Reset value: 0x0000 0000. TI4FS to TI1FS are read-only (r); all other defined bits are rc_w0.

- **Bit 31 TI4FS** (r): tim_ti4f status. This flag indicates the value of the tim_ti4f signal (after the digital filtering stage), for polling purpose.
  - 0: tim_ti4f signal is low
  - 1: tim_ti4f signal is high
- **Bit 30 TI3FS** (r): tim_ti3f status. This flag indicates the value of the tim_ti3f signal (after the digital filtering stage), for polling purpose.
  - 0: tim_ti3f signal is low
  - 1: tim_ti3f signal is high
- **Bit 29 TI2FS** (r): tim_ti2f status. This flag indicates the value of the tim_ti2f signal (after the digital filtering stage), for polling purpose.
  - 0: tim_ti2f signal is low
  - 1: tim_ti2f signal is high
- **Bit 28 TI1FS** (r): tim_ti1f status. This flag indicates the value of the tim_ti1f signal (after the digital filtering stage), for polling purpose.
  - 0: tim_ti1f signal is low
  - 1: tim_ti1f signal is high
- **Bits 27:25** Reserved, must be kept at reset value.
- **Bit 24 UIOVRF** (rc_w0): Update Interrupt Overrun flag. This flag is set by hardware when an update request occurs while an update interrupt is pending (update interrupt flag set). It is cleared by software by writing it to '0'.
  - 0: No Update Interrupt Overrun
  - 1: Update Interrupt Overrun
- **Bit 23 TERRF** (rc_w0): Transition error interrupt flag. This flag is set by hardware when a transition error is detected in encoder mode. It is cleared by software by writing it to 0.
  - 0: No encoder transition error has been detected.
  - 1: An encoder transition error has been detected
- **Bit 22 IERRF** (rc_w0): Index error interrupt flag. This flag is set by hardware when an index error is detected. It is cleared by software by writing it to 0.
  - 0: No index error has been detected.
  - 1: An index error has been detected
- **Bit 21 DIRF** (rc_w0): Direction change interrupt flag. This flag is set by hardware when the direction changes in encoder mode (DIR bit value in TIM_CR is changing). It is cleared by software by writing it to 0.
  - 0: No direction change
  - 1: Direction change
- **Bit 20 IDXF** (rc_w0): Index interrupt flag. This flag is set by hardware when an index event is detected. It is cleared by software by writing it to 0.
  - 0: No index event occurred.
  - 1: An index event has occurred
- **Bits 19:13** Reserved, must be kept at reset value.
- **Bit 12 CC4OF** (rc_w0): Capture/compare 4 overcapture flag. refer to CC1OF description
- **Bit 11 CC3OF** (rc_w0): Capture/compare 3 overcapture flag. refer to CC1OF description
- **Bit 10 CC2OF** (rc_w0): Capture/compare 2 overcapture flag. refer to CC1OF description
- **Bit 9 CC1OF** (rc_w0): Capture/compare 1 overcapture flag. This flag is set by hardware only when the corresponding channel is configured in input capture mode. It is cleared by software by writing it to 0.
  - 0: No overcapture has been detected.
  - 1: The counter value has been captured in TIM_CCR1 register while CC1IF flag was already set
- **Bits 8:7** Reserved, must be kept at reset value.
- **Bit 6 TIF** (rc_w0): Trigger interrupt flag. This flag is set by hardware on the TRG trigger event (active edge detected on tim_trgi input) when the slave mode controller is enabled in all modes but gated mode. It is set when the counter starts or stops when gated mode is selected. It is cleared by software.
  - 0: No trigger event occurred.
  - 1: Trigger interrupt pending.
- **Bit 5** Reserved, must be kept at reset value.
- **Bit 4 CC4IF** (rc_w0): Capture/compare 4 interrupt flag. Refer to CC1IF description
- **Bit 3 CC3IF** (rc_w0): Capture/compare 3 interrupt flag. Refer to CC1IF description
- **Bit 2 CC2IF** (rc_w0): Capture/compare 2 interrupt flag. Refer to CC1IF description
- **Bit 1 CC1IF** (rc_w0): Capture/compare 1 interrupt flag. This flag is set by hardware. It is cleared by software (input capture or output compare mode) or by reading the TIM_CCR1 register (input capture mode only).
  - 0: No compare match / No input capture occurred
  - 1: A compare match or an input capture occurred
  - If channel CC1 is configured as output: this flag is set when the content of the counter TIM_CNT matches the content of the TIM_CCR1 register. When the content of TIM_CCR1 is greater than the content of TIM_ARR, the CC1IF bit goes high on the counter overflow (in up-counting and up/down-counting modes) or underflow (in down-counting mode). There are three possible options for flag setting in center-aligned mode, refer to the CMS bits in the TIM_CR1 register for the full description.
  - If channel CC1 is configured as input: this bit is set when counter value has been captured in TIM_CCR1 register (an edge has been detected on IC1, as per the edge sensitivity defined with the CC1P and CC1NP bits setting, in TIM_CCER).
- **Bit 0 UIF** (rc_w0): Update interrupt flag. This bit is set by hardware on an update event. It is cleared by software.
  - 0: No update occurred
  - 1: Update interrupt pending. This bit is set by hardware when the registers are updated: At overflow or underflow and if UDIS = 0 in the TIM_CR1 register. When CNT is reinitialized by software using the UG bit in TIM_EGR register, if URS = 0 and UDIS = 0 in the TIM_CR1 register. When CNT is reinitialized by a trigger event (refer to the synchro control register description), if URS = 0 and UDIS = 0 in the TIM_CR1 register.

### 32.5.6 TIM event generation register (TIM_EGR)

Address offset: 0x014. Reset value: 0x0000 (register shown as 16 bits in the source). All fields w (write-only, self-clearing).

- **Bits 15:7** Reserved, must be kept at reset value.
- **Bit 6 TG** (w): Trigger generation. This bit is set by software in order to generate an event, it is automatically cleared by hardware.
  - 0: No action
  - 1: The TIF flag is set in TIM_SR register. Related interrupt or DMA transfer can occur if enabled.
- **Bit 5** Reserved, must be kept at reset value.
- **Bit 4 CC4G** (w): Capture/compare 4 generation. Refer to CC1G description
- **Bit 3 CC3G** (w): Capture/compare 3 generation. Refer to CC1G description
- **Bit 2 CC2G** (w): Capture/compare 2 generation. Refer to CC1G description
- **Bit 1 CC1G** (w): Capture/compare 1 generation. This bit is set by software in order to generate an event, it is automatically cleared by hardware.
  - 0: No action
  - 1: A capture/compare event is generated on channel 1: If channel CC1 is configured as output: CC1IF flag is set, Corresponding interrupt or DMA request is sent if enabled. If channel CC1 is configured as input: The current value of the counter is captured in TIM_CCR1 register. The CC1IF flag is set, the corresponding interrupt or DMA request is sent if enabled. The CC1OF flag is set if the CC1IF flag was already high.
- **Bit 0 UG** (w): Update generation. This bit can be set by software, it is automatically cleared by hardware.
  - 0: No action
  - 1: Re-initialize the counter and generates an update of the registers. Note that the prescaler counter is cleared too (anyway the prescaler ratio is not affected). The counter is cleared if the center-aligned mode is selected or if DIR = 0 (up-counting), else it takes the autoreload value (TIM_ARR) if DIR = 1 (down-counting).

### 32.5.7 TIM capture/compare mode register 1 (TIM_CCMR1)

Address offset: 0x018. Reset value: 0x0000 0000. All fields rw. This section is the input capture mode view.

The same register can be used for input capture mode (this section) or for output compare mode (next section). The direction of a channel is defined by configuring the corresponding CCxS bits. All the other bits of this register have a different function for input capture and for output compare modes. It is possible to combine both modes independently (for example channel 1 in input capture mode and channel 2 in output compare mode).

Input capture mode:

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bits 15:12 IC2F[3:0]** (rw): Input capture 2 filter. (No further description in the source; same encoding as IC1F.)
- **Bits 11:10 IC2PSC[1:0]** (rw): Input capture 2 prescaler. (No further description in the source; same encoding as IC1PSC.)
- **Bits 9:8 CC2S[1:0]** (rw): Capture/compare 2 selection. This bitfield defines the direction of the channel (input/output) as well as the used input.
  - 00: CC2 channel is configured as output.
  - 01: CC2 channel is configured as input, tim_ic2 is mapped on tim_ti2.
  - 10: CC2 channel is configured as input, tim_ic2 is mapped on tim_ti1.
  - 11: CC2 channel is configured as input, tim_ic2 is mapped on tim_trc. This mode is working only if an internal trigger input is selected through TS bit (TIM_SMCR register)
  - Note: CC2S bits are writable only when the channel is OFF (CC2E = 0 in TIM_CCER).
- **Bits 7:4 IC1F[3:0]** (rw): Input capture 1 filter. This bitfield defines the frequency used to sample tim_ti1 input and the length of the digital filter applied to tim_ti1. The digital filter is made of an event counter in which N consecutive events are needed to validate a transition on the output:
  - 0000: No filter, sampling is done at fDTS
  - 0001: fSAMPLING = ftim_ker_ck, N = 2
  - 0010: fSAMPLING = ftim_ker_ck, N = 4
  - 0011: fSAMPLING = ftim_ker_ck, N = 8
  - 0100: fSAMPLING = fDTS/2, N = 6
  - 0101: fSAMPLING = fDTS/2, N = 8
  - 0110: fSAMPLING = fDTS/4, N = 6
  - 0111: fSAMPLING = fDTS/4, N = 8
  - 1000: fSAMPLING = fDTS/8, N = 6
  - 1001: fSAMPLING = fDTS/8, N = 8
  - 1010: fSAMPLING = fDTS/16, N = 5
  - 1011: fSAMPLING = fDTS/16, N = 6
  - 1100: fSAMPLING = fDTS/16, N = 8
  - 1101: fSAMPLING = fDTS/32, N = 5
  - 1110: fSAMPLING = fDTS/32, N = 6
  - 1111: fSAMPLING = fDTS/32, N = 8
- **Bits 3:2 IC1PSC[1:0]** (rw): Input capture 1 prescaler. This bitfield defines the ratio of the prescaler acting on CC1 input (tim_ic1). The prescaler is reset as soon as CC1E = 0 (TIM_CCER register).
  - 00: no prescaler, capture is done each time an edge is detected on the capture input
  - 01: capture is done once every 2 events
  - 10: capture is done once every 4 events
  - 11: capture is done once every 8 events
- **Bits 1:0 CC1S[1:0]** (rw): Capture/compare 1 selection. This bitfield defines the direction of the channel (input/output) as well as the used input.
  - 00: CC1 channel is configured as output
  - 01: CC1 channel is configured as input, tim_ic1 is mapped on tim_ti1
  - 10: CC1 channel is configured as input, tim_ic1 is mapped on tim_ti2
  - 11: CC1 channel is configured as input, tim_ic1 is mapped on tim_trc. This mode is working only if an internal trigger input is selected through TS bit (TIM_SMCR register)
  - Note: CC1S bits are writable only when the channel is OFF (CC1E = 0 in TIM_CCER).

### 32.5.8 TIM capture/compare mode register 1 [alternate] (TIM_CCMR1)

Address offset: 0x018. Reset value: 0x0000 0000. All fields rw. This section is the output compare mode view.

The same register can be used for output compare mode (this section) or for input capture mode (previous section). The direction of a channel is defined by configuring the corresponding CCxS bits. All the other bits of this register have a different function for input capture and for output compare modes. It is possible to combine both modes independently (for example channel 1 in input capture mode and channel 2 in output compare mode).

Bit layout (output compare view), MSB first: 31:26 Res.; 25:24 OC2M[4:3]; 23:18 Res.; 17:16 OC1M[4:3]; 15 OC2CE; 14:12 OC2M[2:0]; 11 OC2PE; 10 OC2FE; 9:8 CC2S[1:0]; 7 OC1CE; 6:4 OC1M[2:0]; 3 OC1PE; 2 OC1FE; 1:0 CC1S[1:0].

Output compare mode:

- **Bits 31:26** Reserved, must be kept at reset value.
- **Bits 25:24 OC2M[4:3]** (rw): Output compare 2 mode, upper bits (see OC2M[4:0] below).
- **Bits 23:18** Reserved, must be kept at reset value.
- **Bits 17:16 OC1M[4:3]** (rw): Output compare 1 mode, upper bits (see OC1M[4:0] below).
- **Bit 15 OC2CE** (rw): Output compare 2 clear enable
  - 0: tim_oc2ref is not affected by the tim_ocref_clr_int signal
  - 1: tim_oc2ref is cleared as soon as a high level is detected on tim_ocref_clr_int signal (tim_ocref_clr input or tim_etrf input)
  - Note: This mode is not available for all PWM modes. Refer to Section 32.4.16: Clearing the tim_ocxref signal on an external event for the list of forbidden configurations.
- **Bits 25:24, 14:12 OC2M[4:0]** (rw): Output compare 2 mode. Refer to OC1M description on bits 17:16, 6:4.
- **Bit 11 OC2PE** (rw): Output compare 2 preload enable. (No further description in the source; same as OC1PE.)
- **Bit 10 OC2FE** (rw): Output compare 2 fast enable. (No further description in the source; same as OC1FE.)
- **Bits 9:8 CC2S[1:0]** (rw): Capture/compare 2 selection. This bitfield defines the direction of the channel (input/output) as well as the used input.
  - 00: CC2 channel is configured as output
  - 01: CC2 channel is configured as input, tim_ic2 is mapped on tim_ti2
  - 10: CC2 channel is configured as input, tim_ic2 is mapped on tim_ti1
  - 11: CC2 channel is configured as input, tim_ic2 is mapped on tim_trc. This mode is working only if an internal trigger input is selected through the TS bit (TIM_SMCR register)
  - Note: CC2S bits are writable only when the channel is OFF (CC2E = 0 in TIM_CCER).
- **Bit 7 OC1CE** (rw): Output compare 1 clear enable
  - 0: tim_oc1ref is not affected by the tim_ocref_clr_int input
  - 1: tim_oc1ref is cleared as soon as a High level is detected on tim_ocref_clr_int input
  - Note: This mode is not available for all PWM modes. Refer to Section 32.4.16: Clearing the tim_ocxref signal on an external event for the list of forbidden configurations.
- **Bits 17:16, 6:4 OC1M[4:0]** (rw): Output compare 1 mode. OC1M[4:3] are bits 17:16 and OC1M[2:0] are bits 6:4. These bits define the behavior of the output reference signal tim_oc1ref from which tim_oc1 is derived. tim_oc1ref is active high whereas tim_oc1 active level depends on CC1P bit.
  - 00000: Frozen - The comparison between the output compare register TIM_CCR1 and the counter TIM_CNT has no effect on the outputs. This mode can be used when the timer serves as a software timebase. When the frozen mode is enabled during timer operation, the ouput keeps the state (active or inactive) it had before entering the frozen state.
  - 00001: Set channel 1 to active level on match. tim_oc1ref signal is forced high when the counter TIM_CNT matches the capture/compare register 1 (TIM_CCR1).
  - 00010: Set channel 1 to inactive level on match. tim_oc1ref signal is forced low when the counter TIM_CNT matches the capture/compare register 1 (TIM_CCR1).
  - 00011: Toggle - tim_oc1ref toggles when TIM_CNT = TIM_CCR1.
  - 00100: Force inactive level - tim_oc1ref is forced low.
  - 00101: Force active level - tim_oc1ref is forced high.
  - 00110: PWM mode 1 - In up-counting, channel 1 is active as long as TIM_CNT < TIM_CCR1 else inactive. In down-counting, channel 1 is inactive (tim_oc1ref = 0) as long as TIM_CNT > TIM_CCR1 else active (tim_oc1ref = 1).
  - 00111: PWM mode 2 - In up-counting, channel 1 is inactive as long as TIM_CNT < TIM_CCR1 else active. In down-counting, channel 1 is active as long as TIM_CNT > TIM_CCR1 else inactive.
  - 01000: Retriggerable OPM mode 1 - In up-counting mode, the channel is active until a trigger event is detected (on tim_trgi signal). Then, a comparison is performed as in PWM mode 1 and the channels becomes inactive again at the next update. In down-counting mode, the channel is inactive until a trigger event is detected (on tim_trgi signal). Then, a comparison is performed as in PWM mode 1 and the channels becomes inactive again at the next update.
  - 01001: Retriggerable OPM mode 2 - In up-counting mode, the channel is inactive until a trigger event is detected (on tim_trgi signal). Then, a comparison is performed as in PWM mode 2 and the channels becomes inactive again at the next update. In down-counting mode, the channel is active until a trigger event is detected (on tim_trgi signal). Then, a comparison is performed as in PWM mode 1 and the channels becomes active again at the next update.
  - 01010: Reserved.
  - 01011: Reserved.
  - 01100-01101: Combined PWM mode 1 and 2 - Refer to Table 320: Combined PWM mode overview for details.
  - 01110-01111: Asymmetric PWM mode 1 and 2 - Refer to Table 319: Asymmetric PWM modes for details.
  - Others: Reserved.
  - Note: In PWM mode, the OCREF level changes when the result of the comparison changes, when the output compare mode switches from "frozen" mode to "PWM" mode and when the output compare mode switches from "force active/inactive" mode to "PWM" mode.
- **Bit 3 OC1PE** (rw): Output compare 1 preload enable
  - 0: Preload register on TIM_CCR1 disabled. TIM_CCR1 can be written at anytime, the new value is taken in account immediately.
  - 1: Preload register on TIM_CCR1 enabled. Read/Write operations access the preload register. TIM_CCR1 preload value is loaded in the active register at each update event.
- **Bit 2 OC1FE** (rw): Output compare 1 fast enable. This bit decreases the latency between a trigger event and a transition on the timer output. It must be used in one-pulse mode (OPM bit set in TIM_CR1 register), to have the output pulse starting as soon as possible after the starting trigger.
  - 0: CC1 behaves normally depending on counter and CCR1 values even when the trigger is ON. The minimum delay to activate CC1 output when an edge occurs on the trigger input is 5 clock cycles.
  - 1: An active edge on the trigger input acts like a compare match on CC1 output. Then, OC is set to the compare level independently from the result of the comparison. Delay to sample the trigger input and to activate CC1 output is reduced to three clock cycles. OCFE acts only if the channel is configured in PWM1 or PWM2 mode.
- **Bits 1:0 CC1S[1:0]** (rw): Capture/compare 1 selection. This bitfield defines the direction of the channel (input/output) as well as the used input.
  - 00: CC1 channel is configured as output.
  - 01: CC1 channel is configured as input, tim_ic1 is mapped on tim_ti1.
  - 10: CC1 channel is configured as input, tim_ic1 is mapped on tim_ti2.
  - 11: CC1 channel is configured as input, tim_ic1 is mapped on tim_trc. This mode is working only if an internal trigger input is selected through TS bit (TIM_SMCR register)
  - Note: CC1S bits are writable only when the channel is OFF (CC1E = 0 in TIM_CCER).

*Digest note:* Channels 1 and 2 support only OCxM codes 00000 to 01001 and 01100 to 01111; codes 01010 (pulse on compare) and 01011 (direction output) are reserved on OC1M/OC2M and available only on OC3M/OC4M. Header masks agree: TIM_CCMR1_OC1M_Msk = 0x00030070 (OC1M[3] = bit 16, OC1M[4] = bit 17), TIM_CCMR1_OC2M_Msk = 0x03007000 (OC2M[3] = bit 24, OC2M[4] = bit 25). Example value for channel 1 PWM mode 1 with preload: CC1S = 00, OC1PE = 1, OC1M = 00110 gives TIM_CCMR1[7:0] = 0x68 with bits 17:16 = 0.

### 32.5.9 TIM capture/compare mode register 2 (TIM_CCMR2)

Address offset: 0x01C. Reset value: 0x0000 0000. All fields rw. This section is the input capture mode view.

The same register can be used for input capture mode (this section) or for output compare mode (next section). The direction of a channel is defined by configuring the corresponding CCxS bits. All the other bits of this register have a different function for input capture and for output compare modes. It is possible to combine both modes independently (for example channel 1 in input capture mode and channel 2 in output compare mode).

Input capture mode:

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bits 15:12 IC4F[3:0]** (rw): Input capture 4 filter. (No further description in the source; same encoding as IC1F.)
- **Bits 11:10 IC4PSC[1:0]** (rw): Input capture 4 prescaler. (No further description in the source; same encoding as IC1PSC.)
- **Bits 9:8 CC4S[1:0]** (rw): Capture/compare 4 selection. This bitfield defines the direction of the channel (input/output) as well as the used input.
  - 00: CC4 channel is configured as output
  - 01: CC4 channel is configured as input, tim_ic4 is mapped on tim_ti4
  - 10: CC4 channel is configured as input, tim_ic4 is mapped on tim_ti3
  - 11: CC4 channel is configured as input, tim_ic4 is mapped on tim_trc. This mode is working only if an internal trigger input is selected through TS bit (TIM_SMCR register)
  - Note: CC4S bits are writable only when the channel is OFF (CC4E = 0 in TIM_CCER).
- **Bits 7:4 IC3F[3:0]** (rw): Input capture 3 filter. (No further description in the source; same encoding as IC1F.)
- **Bits 3:2 IC3PSC[1:0]** (rw): Input capture 3 prescaler. (No further description in the source; same encoding as IC1PSC.)
- **Bits 1:0 CC3S[1:0]** (rw): Capture/compare 3 selection. This bitfield defines the direction of the channel (input/output) as well as the used input.
  - 00: CC3 channel is configured as output
  - 01: CC3 channel is configured as input, tim_ic3 is mapped on tim_ti3
  - 10: CC3 channel is configured as input, tim_ic3 is mapped on tim_ti4
  - 11: CC3 channel is configured as input, tim_ic3 is mapped on tim_trc. This mode is working only if an internal trigger input is selected through TS bit (TIM_SMCR register)
  - Note: CC3S bits are writable only when the channel is OFF (CC3E = 0 in TIM_CCER).

### 32.5.10 TIM capture/compare mode register 2 [alternate] (TIM_CCMR2)

Address offset: 0x01C. Reset value: 0x0000 0000. All fields rw. This section is the output compare mode view.

The same register can be used for output compare mode (this section) or for input capture mode (previous section). The direction of a channel is defined by configuring the corresponding CCxS bits. All the other bits of this register have a different function for input capture and for output compare modes. It is possible to combine both modes independently (for example channel 1 in input capture mode and channel 2 in output compare mode).

Bit layout (output compare view), MSB first: 31:26 Res.; 25:24 OC4M[4:3]; 23:18 Res.; 17:16 OC3M[4:3]; 15 OC4CE; 14:12 OC4M[2:0]; 11 OC4PE; 10 OC4FE; 9:8 CC4S[1:0]; 7 OC3CE; 6:4 OC3M[2:0]; 3 OC3PE; 2 OC3FE; 1:0 CC3S[1:0].

Output compare mode:

- **Bits 31:26** Reserved, must be kept at reset value.
- **Bits 25:24 OC4M[4:3]** (rw): Output compare 4 mode, upper bits (see OC4M[4:0] below).
- **Bits 23:18** Reserved, must be kept at reset value.
- **Bits 17:16 OC3M[4:3]** (rw): Output compare 3 mode, upper bits (see OC3M[4:0] below).
- **Bit 15 OC4CE** (rw): Output compare 4 clear enable
  - 0: tim_oc4ref is not affected by the tim_ocref_clr_int signal
  - 1: tim_oc4ref is cleared as soon as a high level is detected on tim_ocref_clr_int signal (tim_ocref_clr input or tim_etrf input)
  - Note: This mode is not available for all PWM modes. Refer to Section 32.4.16: Clearing the tim_ocxref signal on an external event for the list of forbidden configurations.
- **Bits 25:24, 14:12 OC4M[4:0]** (rw): Output compare 4 mode. Refer to OC3M[4:0].
- **Bit 11 OC4PE** (rw): Output compare 4 preload enable. (No further description in the source; same as OC1PE.)
- **Bit 10 OC4FE** (rw): Output compare 4 fast enable. (No further description in the source; same as OC1FE.)
- **Bits 9:8 CC4S[1:0]** (rw): Capture/compare 4 selection. This bitfield defines the direction of the channel (input/output) as well as the used input.
  - 00: CC4 channel is configured as output
  - 01: CC4 channel is configured as input, tim_ic4 is mapped on tim_ti4
  - 10: CC4 channel is configured as input, tim_ic4 is mapped on tim_ti3
  - 11: CC4 channel is configured as input, tim_ic4 is mapped on tim_trc. This mode is working only if an internal trigger input is selected through TS bit (TIM_SMCR register)
  - Note: CC4S bits are writable only when the channel is OFF (CC4E = 0 in TIM_CCER).
- **Bit 7 OC3CE** (rw): Output compare 3 clear enable
  - 0: tim_oc3ref is not affected by the tim_ocref_clr_int signal
  - 1: tim_oc3ref is cleared as soon as a high level is detected on tim_ocref_clr_int signal (tim_ocref_clr input or tim_etrf input)
  - Note: This mode is not available for all PWM modes. Refer to Section 32.4.16: Clearing the tim_ocxref signal on an external event for the list of forbidden configurations.
- **Bits 17:16, 6:4 OC3M[4:0]** (rw): Output compare 3 mode. OC3M[4:3] are bits 17:16 and OC3M[2:0] are bits 6:4. These bits define the behavior of the output reference signal tim_oc3ref from which tim_oc3 and tim_oc3n are derived. tim_oc3ref is active high whereas tim_oc3 and tim_oc3n active level depends on CC3P and CC3NP bits.
  - 00000: Frozen - The comparison between the output compare register TIM_CCR3 and the counter TIM_CNT has no effect on the outputs.(this mode is used to generate a timing base).
  - 00001: Set channel 3 to active level on match. tim_oc3ref signal is forced high when the counter TIM_CNT matches the capture/compare register 3 (TIM_CCR3).
  - 00010: Set channel 3 to inactive level on match. tim_oc3ref signal is forced low when the counter TIM_CNT matches the capture/compare register 3 (TIM_CCR3).
  - 00011: Toggle - tim_oc3ref toggles when TIM_CNT = TIM_CCR3.
  - 00100: Force inactive level - tim_oc3ref is forced low.
  - 00101: Force active level - tim_oc3ref is forced high.
  - 00110: PWM mode 1 - In up-counting, channel 3 is active as long as TIM_CNT < TIM_CCR3 else inactive. In down-counting, channel 3 is inactive (tim_oc3ref = 0) as long as TIM_CNT > TIM_CCR3 else active (tim_oc3ref = 1).
  - 00111: PWM mode 2 - In up-counting, channel 3 is inactive as long as TIM_CNT < TIM_CCR3 else active. In down-counting, channel 3 is active as long as TIM_CNT > TIM_CCR3 else inactive.
  - 01000: Retrigerrable OPM mode 1 - In up-counting mode, the channel is active until a trigger event is detected (on tim_trgi signal). Then, a comparison is performed as in PWM mode 1 and the channels becomes active again at the next update. In down-counting mode, the channel is inactive until a trigger event is detected (on tim_trgi signal). Then, a comparison is performed as in PWM mode 1 and the channels becomes inactive again at the next update.
  - 01001: Retrigerrable OPM mode 2 - In up-counting mode, the channel is inactive until a trigger event is detected (on tim_trgi signal). Then, a comparison is performed as in PWM mode 2 and the channels becomes inactive again at the next update. In down-counting mode, the channel is active until a trigger event is detected (on tim_trgi signal). Then, a comparison is performed as in PWM mode 1 and the channels becomes active again at the next update.
  - 01010: Pulse on compare - A pulse is generated on tim_oc3ref upon CCR3 match event, as per PWPRSC[2:0] and PW[7:0] bitfields programming in TIM_ECR.
  - 01011: Direction output - The tim_oc3ref signal is overridden by a copy of the DIR bit.
  - 01100-01101: Combined PWM mode 1 and 2 - Refer to Table 320: Combined PWM mode overview for details.
  - 01110-01111: Asymmetric PWM mode 1 and 2 - Refer to Table 319: Asymmetric PWM modes for details.
  - 10110-11001: Asymmetric PWM mode 7 to 10 - Available on OC3M only. Refer to Table 319: Asymmetric PWM modes for details.
  - Others: Reserved
  - Note: These bits can not be modified as long as LOCK level 3 has been programmed (LOCK bits in TIM_BDTR register) and CC1S = 00 (the channel is configured in output).
  - Note: In PWM mode, the OCREF level changes only when the result of the comparison changes or when the output compare mode switches from "frozen" mode to "PWM" mode.
  - On channels having a complementary output, this bitfield is preloaded. If the CCPC bit is set in the TIM_CR2 register then the OC3M active bits take the new value from the preloaded bits only when a COM event is generated.
- **Bit 3 OC3PE** (rw): Output compare 3 preload enable. (No further description in the source; same as OC1PE.)
- **Bit 2 OC3FE** (rw): Output compare 3 fast enable. (No further description in the source; same as OC1FE.)
- **Bits 1:0 CC3S[1:0]** (rw): Capture/compare 3 selection. This bitfield defines the direction of the channel (input/output) as well as the used input.
  - 00: CC3 channel is configured as output
  - 01: CC3 channel is configured as input, tim_ic3 is mapped on tim_ti3
  - 10: CC3 channel is configured as input, tim_ic3 is mapped on tim_ti4
  - 11: CC3 channel is configured as input, tim_ic3 is mapped on tim_trc. This mode is working only if an internal trigger input is selected through TS bit (TIM_SMCR register)
  - Note: CC3S bits are writable only when the channel is OFF (CC3E = 0 in TIM_CCER).

*Digest note:* The OC3M description mentions tim_oc3n, CC3NP as an output polarity, LOCK bits in TIM_BDTR, CCPC in TIM_CR2 and COM events. These belong to the advanced-control timers: TIM2/TIM3/TIM4/TIM5 have no complementary outputs, no TIM_BDTR (the register map 32.5.25 has none) and TIM_CR2 bit 0 is reserved, so those notes do not apply here. The retriggerable OPM mode 1 text differs between OC1M ("becomes inactive again at the next update" in up-counting) and OC3M ("becomes active again"); both are reproduced as printed. The OC4M field (bits 25:24, 14:12) supports the same codes as OC3M except asymmetric PWM modes 7 to 10, which are OC3M only.

### 32.5.11 TIM capture/compare enable register (TIM_CCER)

Address offset: 0x020. Reset value: 0x0000 (register shown as 16 bits in the source). All fields rw.

- **Bit 15 CC4NP** (rw): Capture/compare 4 output Polarity. Refer to CC1NP description
- **Bit 14** Reserved, must be kept at reset value.
- **Bit 13 CC4P** (rw): Capture/compare 4 output Polarity. Refer to CC1P description
- **Bit 12 CC4E** (rw): Capture/compare 4 output enable. refer to CC1E description
- **Bit 11 CC3NP** (rw): Capture/compare 3 output Polarity. Refer to CC1NP description
- **Bit 10** Reserved, must be kept at reset value.
- **Bit 9 CC3P** (rw): Capture/compare 3 output Polarity. Refer to CC1P description
- **Bit 8 CC3E** (rw): Capture/compare 3 output enable. Refer to CC1E description
- **Bit 7 CC2NP** (rw): Capture/compare 2 output Polarity. Refer to CC1NP description
- **Bit 6** Reserved, must be kept at reset value.
- **Bit 5 CC2P** (rw): Capture/compare 2 output Polarity. refer to CC1P description
- **Bit 4 CC2E** (rw): Capture/compare 2 output enable. Refer to CC1E description
- **Bit 3 CC1NP** (rw): Capture/compare 1 output Polarity.
  - CC1 channel configured as output: CC1NP must be kept cleared in this case.
  - CC1 channel configured as input: This bit is used in conjunction with CC1P to define tim_ti1fp1/tim_ti2fp1 polarity. refer to CC1P description.
- **Bit 2** Reserved, must be kept at reset value.
- **Bit 1 CC1P** (rw): Capture/compare 1 output Polarity.
  - 0: OC1 active high (output mode) / Edge sensitivity selection (input mode, see below)
  - 1: OC1 active low (output mode) / Edge sensitivity selection (input mode, see below)
  - When CC1 channel is configured as input, both CC1NP/CC1P bits select the active polarity of TI1FP1 and TI2FP1 for trigger or capture operations.
  - CC1NP = 0, CC1P = 0: non-inverted/rising edge. The circuit is sensitive to TIxFP1 rising edge (capture or trigger operations in reset, external clock or trigger mode), TIxFP1 is not inverted (trigger operation in gated mode or encoder mode).
  - CC1NP = 0, CC1P = 1: inverted/falling edge. The circuit is sensitive to TIxFP1 falling edge (capture or trigger operations in reset, external clock or trigger mode), TIxFP1 is inverted (trigger operation in gated mode or encoder mode).
  - CC1NP = 1, CC1P = 1: non-inverted/both edges. The circuit is sensitive to both TIxFP1 rising and falling edges (capture or trigger operations in reset, external clock or trigger mode), TIxFP1is not inverted (trigger operation in gated mode). This configuration must not be used in encoder mode.
  - CC1NP = 1, CC1P = 0: this configuration is reserved, it must not be used.
- **Bit 0 CC1E** (rw): Capture/compare 1 output enable.
  - 0: Capture mode disabled / OC1 is not active
  - 1: Capture mode enabled / OC1 signal is output on the corresponding output pin

**Table 326. Output control bit for standard tim_ocx channels**

| CCxE bit | tim_ocx output state |
|---|---|
| 0 | Output disabled (not driven by the timer: Hi-Z) |
| 1 | Output enabled (tim_ocx = tim_ocxref + Polarity) |

Note: The state of the external IO pins connected to the standard tim_ocx channels depends only on the GPIO registers when CCxE = 0.

*Digest note:* Per channel x (1 to 4) the TIM_CCER nibble is [CCxNP, Res., CCxP, CCxE] at bits [4(x-1)+3 : 4(x-1)]. The header defines CCxNE at bits 2, 6, 10, 14 and CC5E..CC7P at bits 16 and above for advanced timers; those bits are reserved on TIM2/TIM3/TIM4/TIM5. Output enable is CCxE alone (there is no MOE).

### 32.5.12 TIM counter (TIM_CNT)

Address offset: 0x024. Reset value: 0x0000 0000. All bits rw (bit 31 read value depends on UIFREMAP).

- **Bit 31 UIFCPY_CNT[31]** (rw): Value depends on IUFREMAP in TIM_CR1.
  - If UIFREMAP = 0: CNT[31]: Most significant bit of counter value
  - If UIFREMAP = 1: UIFCPY: UIF Copy. This bit is a read-only copy of the UIF bit of the TIM_ISR register
- **Bits 30:0 CNT[30:0]** (rw): Least significant part of counter value
  - Non-dithering mode (DITHEN = 0): The register holds the counter value.
  - Dithering mode (DITHEN = 1): The register holds the non-dithered part in CNT[30:0]. The fractional part is not available.

*Digest note:* "TIM_ISR" in the UIFCPY description refers to TIM_SR (UIF is TIM_SR bit 0). The header defines TIM_CNT_CNT_Msk = 0x7FFFFFFF and TIM_CNT_UIFCPY at bit 31.

### 32.5.13 TIM prescaler (TIM_PSC)

Address offset: 0x028. Reset value: 0x0000 (register shown as 16 bits in the source). All bits rw.

- **Bits 15:0 PSC[15:0]** (rw): Prescaler value. The counter clock frequency tim_cnt_ck is equal to ftim_psc_ck / (PSC[15:0] + 1). PSC contains the value to be loaded in the active prescaler register at each update event (including when the counter is cleared through UG bit of TIM_EGR register or through trigger controller when configured in "reset mode").

*Digest note:* Header: TIM_PSC_PSC_Msk = 0xFFFF. The prescaler is 16-bit even though the counter is 32-bit.

### 32.5.14 TIM autoreload register (TIM_ARR)

Address offset: 0x02C. Reset value: 0xFFFF FFFF. All bits rw.

- **Bits 31:0 ARR[31:0]** (rw): Autoreload value. ARR is the value to be loaded in the actual autoreload register. Refer to the Section 32.4.3: Time-base unit for more details about ARR update and behavior. The counter is blocked while the autoreload value is null.
  - Non-dithering mode (DITHEN = 0): The register holds the autoreload value.
  - Dithering mode (DITHEN = 1): The register holds the integer part in ARR[31:4]. The ARR[3:0] bitfield contains the dithered part.

### 32.5.15 TIM capture/compare register 1 (TIM_CCR1)

Address offset: 0x034. Reset value: 0x0000 0000. All bits rw (read-only when the channel is configured as input).

- **Bits 31:0 CCR1[31:0]** (rw): Capture/compare 1 value
  - If channel CC1 is configured as output: CCR1 is the value to be loaded in the actual capture/compare 1 register (preload value). It is loaded permanently if the preload feature is not selected in the TIM_CCMR1 register (bit OC1PE). Else the preload value is copied in the active capture/compare 1 register when an update event occurs. The active capture/compare register contains the value to be compared to the counter TIM_CNT and signaled on tim_oc1 output.
    - Non-dithering mode (DITHEN = 0): The register holds the compare value.
    - Dithering mode (DITHEN = 1): The register holds the integer part in CCR1[31:4]. The CCR1[3:0] bitfield contains the dithered part.
  - If channel CC1 is configured as input: CCR1 is the counter value transferred by the last input capture 1 event (tim_ic1). The TIM_CCR1 register is read-only and cannot be programmed.
    - Non-dithering mode (DITHEN = 0): The register holds the capture value.
    - Dithering mode (DITHEN = 1): The register holds the capture in CCR1[31:0]. The CCR1[3:0] bits are reset.

### 32.5.16 TIM capture/compare register 2 (TIM_CCR2)

Address offset: 0x038. Reset value: 0x0000 0000. All bits rw (read-only when the channel is configured as input).

- **Bits 31:0 CCR2[31:0]** (rw): Capture/compare 2 value
  - If channel CC2 is configured as output: CCR2 is the value to be loaded in the actual capture/compare 2 register (preload value). It is loaded permanently if the preload feature is not selected in the TIM_CCMR2 register (bit OC2PE). Else the preload value is copied in the active capture/compare 2 register when an update event occurs. The active capture/compare register contains the value to be compared to the counter TIM_CNT and signaled on tim_oc2 output.
    - Non-dithering mode (DITHEN = 0): The register holds the compare value.
    - Dithering mode (DITHEN = 1): The register holds the integer part in CCR2[31:4]. The CCR2[3:0] bitfield contains the dithered part.
  - If channel CC2 is configured as input: CCR2 is the counter value transferred by the last input capture 2 event (tim_ic2). The TIM_CCR2 register is read-only and cannot be programmed.
    - Non-dithering mode (DITHEN = 0): The register holds the capture value.
    - Dithering mode (DITHEN = 1): The register holds the capture in CCR2[31:0]. The CCR2[3:0] bits are reset.

*Digest note:* OC2PE is in TIM_CCMR1 (bit 11), not TIM_CCMR2 as printed above.

### 32.5.17 TIM capture/compare register 3 (TIM_CCR3)

Address offset: 0x03C. Reset value: 0x0000 0000. All bits rw (read-only when the channel is configured as input).

- **Bits 31:0 CCR3[31:0]** (rw): Capture/compare 3 value
  - If channel CC3 is configured as output: CCR3 is the value to be loaded in the actual capture/compare 3 register (preload value). It is loaded permanently if the preload feature is not selected in the TIM_CCMR3 register (bit OC3PE). Else the preload value is copied in the active capture/compare 3 register when an update event occurs. The active capture/compare register contains the value to be compared to the counter TIM_CNT and signaled on tim_oc3 output.
    - Non-dithering mode (DITHEN = 0): The register holds the compare value.
    - Dithering mode (DITHEN = 1): The register holds the integer part in CCR3[31:4]. The CCR3[3:0] bitfield contains the dithered part.
  - If channel CC3 is configured as input: CCR3 is the counter value transferred by the last input capture 3 event (tim_ic3). The TIM_CCR3 register is read-only and cannot be programmed.
    - Non-dithering mode (DITHEN = 0): The register holds the capture value.
    - Dithering mode (DITHEN = 1): The register holds the capture in CCR3[31:0]. The CCR3[3:0] bits are reset.

*Digest note:* OC3PE is in TIM_CCMR2 (bit 3); there is no TIM_CCMR3 on these timers.

### 32.5.18 TIM capture/compare register 4 (TIM_CCR4)

Address offset: 0x040. Reset value: 0x0000 0000. All bits rw (read-only when the channel is configured as input).

- **Bits 31:0 CCR4[31:0]** (rw): Capture/compare 4 value
  - If channel CC4 is configured as output: CCR4 is the value to be loaded in the actual capture/compare 4 register (preload value). It is loaded permanently if the preload feature is not selected in the TIM_CCMR4 register (bit OC4PE). Else the preload value is copied in the active capture/compare 4 register when an update event occurs. The active capture/compare register contains the value to be compared to the counter TIM_CNT and signaled on tim_oc4 output.
    - Non-dithering mode (DITHEN = 0): The register holds the compare value.
    - Dithering mode (DITHEN = 1): The register holds the integer part in CCR4[31:4]. The CCR4[3:0] bitfield contains the dithered part.
  - If channel CC4 is configured as input: CCR4 is the counter value transferred by the last input capture 4 event (tim_ic4). The TIM_CCR4 register is read-only and cannot be programmed.
    - Non-dithering mode (DITHEN = 0): The register holds the capture value.
    - Dithering mode (DITHEN = 1): The register holds the capture in CCR4[31:0]. The CCR4[3:0] bits are reset.

*Digest note:* OC4PE is in TIM_CCMR2 (bit 11); there is no TIM_CCMR4 on these timers. Note the register map gap: TIM_ARR is at 0x02C and TIM_CCR1 at 0x034; offset 0x030 (RCR on advanced timers) is reserved here.

### 32.5.19 TIM timer encoder control register (TIM_ECR)

Address offset: 0x058. Reset value: 0x0000 0000. All fields rw.

- **Bits 31:27** Reserved, must be kept at reset value.
- **Bits 26:24 PWPRSC[2:0]** (rw): Pulse width prescaler. This bitfield sets the clock prescaler for the pulse generator, as following: tPWG = (2^(PWPRSC[2:0])) x ttim_ker_ck
- **Bits 23:16 PW[7:0]** (rw): Pulse width. This bitfield defines the pulse duration, as following: tPW = PW[7:0] x tPWG
- **Bits 15:8** Reserved, must be kept at reset value.
- **Bits 7:6 IPOS[1:0]** (rw): Index positioning. In quadrature encoder mode (SMS[4:0] = 00001, 00010, 00011, 01110, 01111), this bit indicates in which AB input configuration the Index event resets the counter.
  - 00: Index resets the counter when AB = 00
  - 01: Index resets the counter when AB = 01
  - 10: Index resets the counter when AB = 10
  - 11: Index resets the counter when AB = 11
  - In directional clock mode or clock plus direction mode (SMS[4:0] = 01010, 01011, 01100, 01101), these bits indicates on which level the Index event resets the counter. In bidirectional clock mode, this applies for both clock inputs.
  - x0: Index resets the counter when clock is 0
  - x1: Index resets the counter when clock is 1
  - Note: IPOS[1] bit is not significant
- **Bit 5 FIDX** (rw): First index. This bit indicates if the first index only is taken into account
  - 0: Index is always active
  - 1: the first Index only resets the counter
- **Bits 4:3 IBLK[1:0]** (rw): Index blanking. This bit indicates if the Index event is conditioned by the tim_ti3 input
  - 00: Index always active
  - 01: Index disabled hen tim_ti3 input is active, as per CC3P bitfield
  - 10: Index disabled when tim_ti4 input is active, as per CC4P bitfield
  - 11: Reserved
- **Bits 2:1 IDIR[1:0]** (rw): Index direction. This bit indicates in which direction the Index event resets the counter.
  - 00: Index resets the counter whatever the direction
  - 01: Index resets the counter when up-counting only
  - 10: Index resets the counter when down-counting only
  - 11: Reserved
- **Bit 0 IE** (rw): Index enable. This bit indicates if the Index event resets the counter.
  - 0: Index disabled
  - 1: Index enabled

### 32.5.20 TIM timer input selection register (TIM_TISEL)

Address offset: 0x05C. Reset value: 0x0000 0000. All fields rw.

- **Bits 31:28** Reserved, must be kept at reset value.
- **Bits 27:24 TI4SEL[3:0]** (rw): Selects tim_ti4[15:0] input
  - 0000: tim_ti4_in0: TIMx_CH4
  - 0001: tim_ti4_in1
  - ...
  - 1111: tim_ti4_in15
  - Refer to Section 32.4.2: TIM2/TIM3/TIM4/TIM5 pins and internal signals for product specific implementation.
- **Bits 23:20** Reserved, must be kept at reset value.
- **Bits 19:16 TI3SEL[3:0]** (rw): Selects tim_ti3[15:0] input
  - 0000: tim_ti3_in0: TIMx_CH3
  - 0001: tim_ti3_in1
  - ...
  - 1111: tim_ti3_in15
  - Refer to Section 32.4.2: TIM2/TIM3/TIM4/TIM5 pins and internal signals for product specific implementation.
- **Bits 15:12** Reserved, must be kept at reset value.
- **Bits 11:8 TI2SEL[3:0]** (rw): Selects tim_ti2[15:0] input
  - 0000: tim_ti2_in0: TIMx_CH2
  - 0001: tim_ti2_in1
  - ...
  - 1111: tim_ti2_in15
  - Refer to Section 32.4.2: TIM2/TIM3/TIM4/TIM5 pins and internal signals for product specific implementation.
- **Bits 7:4** Reserved, must be kept at reset value.
- **Bits 3:0 TI1SEL[3:0]** (rw): Selects tim_ti1[15:0] input
  - 0000: tim_ti1_in0: TIMx_CH1
  - 0001: tim_ti1_in1
  - ...
  - 1111: tim_ti1_in15
  - Refer to Section 32.4.2: TIM2/TIM3/TIM4/TIM5 pins and internal signals for product specific implementation.

### 32.5.21 TIM alternate function register 1 (TIM_AF1)

Address offset: 0x060. Reset value: 0x0000 0000. ETRSEL is rw.

- **Bits 31:19** Reserved, must be kept at reset value.
- **Bits 18:14 ETRSEL[4:0]** (rw): etr_in source selection. These bits select the etr_in input source.
  - 00000: tim_etr0: TIM_ETR input
  - 00001: tim_etr1
  - ...
  - 11111: tim_etr31
  - Refer to Section 32.4.2: TIM2/TIM3/TIM4/TIM5 pins and internal signals for product specific implementation.
- **Bits 13:0** Reserved, must be kept at reset value.

*Digest note:* The header defines break-input bits (BKINE, BKCMPxE, BKINP, BKCMPxP) in TIM_AF1 for advanced timers; only ETRSEL (bits 18:14, TIM_AF1_ETRSEL_Msk = 0x1F << 14) exists on TIM2/TIM3/TIM4/TIM5.

### 32.5.22 TIM alternate function register 2 (TIM_AF2)

Address offset: 0x064. Reset value: 0x0000 0000. OCRSEL is rw.

- **Bits 31:20** Reserved, must be kept at reset value.
- **Bits 19:16 OCRSEL[3:0]** (rw): ocref_clr source selection. These bits select the ocref_clr input source.
  - 0000: tim_ocref_clr0
  - 0001: tim_ocref_clr1
  - ...
  - 0111: tim_ocref_clr15
  - Refer to Section 32.4.2: TIM2/TIM3/TIM4/TIM5 pins and internal signals for product specific implementation.
- **Bits 15:0** Reserved, must be kept at reset value.

*Digest note:* The last code is printed as "0111: tim_ocref_clr15"; with a 4-bit field, tim_ocref_clr15 would be 1111. Header: TIM_AF2_OCRSEL at bits 19:16 (mask 0xF).

### 32.5.23 TIM DMA control register (TIM_DCR)

Address offset: 0x3DC. Reset value: 0x0000 0000. All fields rw.

- **Bits 31:20** Reserved, must be kept at reset value.
- **Bits 19:16 DBSS[3:0]** (rw): DMA burst source selection. This bitfield defines the interrupt source that triggers the DMA burst transfers (the timer recognizes a burst transfer when a read or a write access is done to the TIM_DMAR address).
  - 0000: Reserved
  - 0001: Update
  - 0010: CC1
  - 0011: CC2
  - 0100: CC3
  - 0101: CC4
  - 0110: COM
  - 0111: Trigger
  - Others: reserved
- **Bits 15:13** Reserved, must be kept at reset value.
- **Bits 12:8 DBL[4:0]** (rw): DMA burst length. This 5-bit vector defines the length of DMA transfers (the timer recognizes a burst transfer when a read or a write access is done to the TIM_DMAR address), i.e. the number of transfers. Transfers can be in half-words or in bytes (see example below).
  - 00000: 1 transfer
  - 00001: 2 transfers
  - 00010: 3 transfers
  - ...
  - 11111: 32 transfers
  - Example: Let us consider the following transfer: DBL = 6 bytes & DBA = TIM2_CR1.
    - If DBL = 6 bytes and DBA = TIM2_CR1 represents the address of the byte to be transferred, the address of the transfer is given by the following equation: (TIM_CR1 address) + DBA + (DMA index), where DMA index = DBL
    - In this example, 7 bytes are added to (TIM_CR1 address) + DBA, which gives us the address from/to which the data are copied. In this case, the transfer is done to 7 registers starting from the following address: (TIM_CR1 address) + DBA
    - According to the configuration of the DMA Data Size, several cases may occur:
    - If the DMA Data Size is configured in half-words, 16-bit data are transferred to each of the 7 registers.
    - If the DMA Data Size is configured in bytes, the data are also transferred to 7 registers: the first register contains the first MSB byte, the second register, the first LSB byte and so on. So with the transfer Timer, one also has to specify the size of data transferred by DMA.
- **Bits 7:5** Reserved, must be kept at reset value.
- **Bits 4:0 DBA[4:0]** (rw): DMA base address. This 5-bits vector defines the base-address for DMA transfers (when read/write access are done through the TIM_DMAR address). DBA is defined as an offset starting from the address of the TIM_CR1 register.
  - Example:
  - 00000: TIM_CR1,
  - 00001: TIM_CR2,
  - 00010: TIM_SMCR,
  - ...

*Digest note:* DBSS code 0110 (COM) refers to an event that TIM2/TIM3/TIM4/TIM5 do not generate. Per the TIM_DMAR formula, DBA counts 32-bit registers from TIM_CR1, so DBA = 0xE in the 32.4.30 example selects offset 0xE x 4 = 0x038 (TIM_CCR2), consistent with that example updating CCR2, CCR3 and CCR4.

### 32.5.24 TIM DMA address for full transfer (TIM_DMAR)

Address offset: 0x3E0. Reset value: 0x0000 0000. All bits rw.

- **Bits 31:0 DMAB[31:0]** (rw): DMA register for burst accesses. A read or write operation to the DMAR register accesses the register located at the address (TIM_CR1 address) + (DBA + DMA index) x 4, where TIM_CR1 address is the address of the control register 1, DBA is the DMA base address configured in TIM_DCR register, DMA index is automatically controlled by the DMA transfer, and ranges from 0 to DBL (DBL configured in TIM_DCR).

### 32.5.25 TIM2/TIM3/TIM4/TIM5 register map

TIM2/TIM3/TIM4/TIM5 registers are mapped as described in the table below.

**Table 327. TIM2/TIM3/TIM4/TIM5 register map and reset values**

| Offset | Register | Reset value | Fields (bit positions) |
|---|---|---|---|
| 0x000 | TIM_CR1 | 0x0000 0000 | CKD2[3:0] (27:24), DITHEN (12), UIFREMAP (11), CKD[1:0] (9:8), ARPE (7), CMS[1:0] (6:5), DIR (4), OPM (3), URS (2), UDIS (1), CEN (0); all other bits Res. |
| 0x004 | TIM_CR2 | 0x0000 0000 | TI3INV (31), TI2INV (30), TI1INV (29), ADSYNC (28), XORPS (27), MMS[3] (25), TI1S (7), MMS[2:0] (6:4), CCDS (3); all other bits Res. |
| 0x008 | TIM_SMCR | 0x0000 0000 | SETPS[3:0] (29:26), SMSPS (25), SMSPE (24), TS[4:3] (21:20), SMS[4:3] (17:16), ETP (15), ECE (14), ETPS[1:0] (13:12), ETF[3:0] (11:8), MSM (7), TS[2:0] (6:4), OCCS (3), SMS[2:0] (2:0); all other bits Res. |
| 0x00C | TIM_DIER | 0x0000 0000 | TERRIE (23), IERRIE (22), DIRIE (21), IDXIE (20), TDE (14), CC4DE (12), CC3DE (11), CC2DE (10), CC1DE (9), UDE (8), BIE (7) (1), TIE (6), CC4IE (4), CC3IE (3), CC2IE (2), CC1IE (1), UIE (0); all other bits Res. |
| 0x010 | TIM_SR | 0x0000 0000 | TI4FS (31), TI3FS (30), TI2FS (29), TI1FS (28), UIOVRF (24), TERRF (23), IERRF (22), DIRF (21), IDXF (20), CC4OF (12), CC3OF (11), CC2OF (10), CC1OF (9), TIF (6), CC4IF (4), CC3IF (3), CC2IF (2), CC1IF (1), UIF (0); all other bits Res. |
| 0x014 | TIM_EGR | 0x0000 0000 | TG (6), CC4G (4), CC3G (3), CC2G (2), CC1G (1), UG (0); all other bits Res. |
| 0x018 | TIM_CCMR1 (input capture mode) | 0x0000 0000 | IC2F[3:0] (15:12), IC2PSC[1:0] (11:10), CC2S[1:0] (9:8), IC1F[3:0] (7:4), IC1PSC[1:0] (3:2), CC1S[1:0] (1:0); bits 31:16 Res. |
| 0x018 | TIM_CCMR1 (output compare mode) | 0x0000 0000 | OC2M[4:3] (25:24), OC1M[4:3] (17:16), OC2CE (15), OC2M[2:0] (14:12), OC2PE (11), OC2FE (10), CC2S[1:0] (9:8), OC1CE (7), OC1M[2:0] (6:4), OC1PE (3), OC1FE (2), CC1S[1:0] (1:0); bits 31:26 and 23:18 Res. |
| 0x01C | TIM_CCMR2 (input capture mode) | 0x0000 0000 | IC4F[3:0] (15:12), IC4PSC[1:0] (11:10), CC4S[1:0] (9:8), IC3F[3:0] (7:4), IC3PSC[1:0] (3:2), CC3S[1:0] (1:0); bits 31:16 Res. |
| 0x01C | TIM_CCMR2 (output compare mode) | 0x0000 0000 | OC4M[4:3] (25:24), OC3M[4:3] (17:16), OC4CE (15) (2), OC4M[2:0] (14:12), OC4PE (11), OC4FE (10), CC4S[1:0] (9:8), OC3CE (7), OC3M[2:0] (6:4), OC3PE (3), OC3FE (2), CC3S[1:0] (1:0); bits 31:26 and 23:18 Res. |
| 0x020 | TIM_CCER | 0x0000 0000 | CC4NP (15), CC4P (13), CC4E (12), CC3NP (11), CC3P (9), CC3E (8), CC2NP (7), CC2P (5), CC2E (4), CC1NP (3), CC1P (1), CC1E (0); bits 31:16, 14, 10, 6, 2 Res. |
| 0x024 | TIM_CNT | 0x0000 0000 | UIFCPY_CNT[31] (31), CNT[30:16] (30:16) (CNT[31:16] on 32-bit timers only), CNT[15:0] (15:0) |
| 0x028 | TIM_PSC | 0x0000 0000 | PSC[15:0] (15:0); bits 31:16 Res. |
| 0x02C | TIM_ARR | 0xFFFF FFFF | ARR[31:0] (31:0) |
| 0x030 | Reserved | - | Reserved |
| 0x034 | TIM_CCR1 | 0x0000 0000 | CCR1[31:20] (31:20) (32-bit timers only), CCR1[19:0] (19:0) |
| 0x038 | TIM_CCR2 | 0x0000 0000 | CCR2[31:20] (31:20) (32-bit timers only), CCR2[19:0] (19:0) |
| 0x03C | TIM_CCR3 | 0x0000 0000 | CCR3[31:20] (31:20) (32-bit timers only), CCR3[19:0] (19:0) |
| 0x040 | TIM_CCR4 | 0x0000 0000 | CCR4[31:20] (31:20) (32-bit timers only), CCR4[19:0] (19:0) |
| 0x044 to 0x054 | Reserved | - | Res. |
| 0x058 | TIM_ECR | 0x0000 0000 | PWPRSC[2:0] (26:24), PW[7:0] (23:16), IPOS[1:0] (7:6), FIDX (5), IBLK[1:0] (4:3), IDIR[1:0] (2:1), IE (0); all other bits Res. |
| 0x05C | TIM_TISEL | 0x0000 0000 | TI4SEL[3:0] (27:24), TI3SEL[3:0] (19:16), TI2SEL[3:0] (11:8), TI1SEL[3:0] (3:0); all other bits Res. |
| 0x060 | TIM_AF1 | 0x0000 0000 | ETRSEL[4:0] (18:14); all other bits Res. |
| 0x064 | TIM_AF2 | 0x0000 0000 | OCRSEL[3:0] (19:16); all other bits Res. |
| 0x068 to 0x3D8 | Reserved | - | Res. |
| 0x3DC | TIM_DCR | 0x0000 0000 | DBSS[3:0] (19:16), DBL[4:0] (12:8), DBA[4:0] (4:0); all other bits Res. |
| 0x3E0 | TIM_DMAR | 0x0000 0000 | DMAB[31:0] (31:0) |

Notes:

1. The register map labels TIM_DIER bit 7 as "BIE", whereas the TIM_DIER description (32.5.4) lists bit 7 as Reserved. The CMSIS header defines TIM_DIER_BIE at bit 7 (break interrupt enable, an advanced-timer feature). TIM2/TIM3/TIM4/TIM5 have no break input, so treat bit 7 as reserved.
2. Printed as "O24CE" in the register map; it is OC4CE.

Refer to Section 2.2: Memory organization for the register boundary addresses.

*Digest note:* In the register map, TIM_EGR, TIM_CCER and TIM_PSC are shown in the 32-bit grid with only the low 16 bits defined; their register descriptions give the reset value as 0x0000. The CMSIS TIM_TypeDef offsets agree with this map for all registers present here (CR1 0x000 ... AF2 0x064, DCR 0x3DC, DMAR 0x3E0); the header places RCR at 0x030, BDTR at 0x044, CCR5/CCR6/CCMR3/DTR2 at 0x048 to 0x054 and further advanced-timer registers above 0x068, all of which are reserved on TIM2/TIM3/TIM4/TIM5.
