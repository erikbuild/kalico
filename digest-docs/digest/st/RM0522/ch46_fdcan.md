# RM0522 Chapter 46: FD controller area network (FDCAN)

Source: RM0522 Rev 1 (STM32C5 reference manual), pages 2021–2086.

*Digest note (STM32C551/C552 context, gathered from outside this chapter):*

- FDCAN1 exists only on STM32C552xx; STM32C551xx has no FDCAN (STM32C55xxx datasheet digest). FDCAN2 does not exist on any STM32C55x/C56x device (Table 470).
- Addresses (RM0522 Table 3 "Memory map and peripheral register boundary addresses", and the CMSIS header stm32c552xx.h): FDCAN1 registers at 0x4000 A400 – 0x4000 A7FF (header: FDCAN1_BASE = 0x4000 A400); FDCAN_CKDIV lives at FDCAN1 + 0x100 = 0x4000 A500 (header: FDCAN_CONFIG_BASE); FDCAN message RAM ("FDCAN SRAM", header: SRAMCAN_BASE) starts at 0x4000 AC00. Table 3 lists the FDCAN SRAM window as 0x4000 AC00 – 0x4000 B3FF, with footnote "For STM32C55x/562 devices, FDCAN RAM boundary end address is 0x4000 AFFF."
- Interrupt vectors (RM0522 vector table, and header): FDCAN1_IT0 = IRQ 34 (vector address 0x0000 00C8), FDCAN1_IT1 = IRQ 35 (vector address 0x0000 00CC). FDCAN2_IT0/IT1 (IRQ 86/87) do not apply to C55x.
- Kernel clock (RM0522 RCC chapter, RCC_CCIPR1): FDCANSEL[1:0] at bits 27:26 selects the FDCAN1/FDCAN2 kernel clock: 00 rcc_pclk1 (default after reset), 01 psis_ck, 10 psik_ck, 11 hse_ck. Bus clock enable is RCC_APB1HENR.FDCANEN (bit 9), reset is RCC_APB1HRSTR.FDCANRST (bit 9).
- Register layout and bit positions in this chapter match the STM32G0 FDCAN definitions in this repository (lib/stm32g0/include/stm32g0b1xx.h): same fixed 0x350-byte message RAM per instance, RXGFC at 0x080, TXBC with only TFQM, CKDIV at FDCAN1 + 0x100. Only the base addresses differ (G0B1: FDCAN1 0x4000 6400, CKDIV 0x4000 6500, SRAMCAN 0x4000 B400).

## 46.1 FDCAN introduction

The controller area network (CAN) subsystem (see Figure 693) consists of one CAN module, a shared message RAM, and a configuration block. Refer to the memory map for the base address of each of these parts.

The modules (FDCAN) are compliant with ISO 11898-1: 2015 (CAN protocol specification version 2.0 part A, B) and CAN FD protocol specification version 1.0.

A 0.8-Kbyte message RAM per FDCAN instance is used for filtering, transmitting event FIFOs, and receiving and transmitting FIFOs.

**Figure 693. CAN subsystem.** (described)

- Configuration block (kernel clock domain, except the subsystem configuration register which is in the APB clock domain): fdcan_ker_ck enters a multiplexer both directly and through a divider labelled "PDIV[3:0] / 1..30". The multiplexer is controlled by CKDIV from the "Subsystem configuration register", which is accessed from the 32-bit APB bus through CFG_APB. The multiplexer output is fdcan_tq_ck, which clocks the CAN core.
- CANFDL block (the FDCAN1 instance):
  - Interrupts interface, driving fdcan1_intr0_it and fdcan1_intr1_it.
  - Control and configuration registers, accessed through Ctrl_APB and clocked by fdcan_pclk.
  - CAN core (kernel clock domain), connected to pins FDCAN1_RX and FDCAN1_TX. It exchanges Tx Req, Tx State and Rx State with the handlers through a Sync block, and a second Sync block links it to the control/configuration registers.
  - TX handler (TX prioritization, Frame Synchro), output event fdcan1_txeof_evt.
  - RX handler (Acceptance filter), output event fdcan1_rxeof_evt.
  - Message RAM interface.
  - External timestamp input fdcan_ts[0:15] enters the block and connects to the handler logic.
- The message RAM interface, TX handler and RX handler connect to a RAM controller/arbiter, which is also accessible from the APB bus through RAM_APB. The arbiter connects to the message RAM (buffers, FIFOs, filters).
- Legend: APB clock domain (interrupts interface, registers, message RAM interface, TX/RX handlers, subsystem configuration register) and kernel clock domain (clock divider/multiplexer, CAN core).

## 46.2 FDCAN main features

- Conform with CAN protocol version 2.0 part A, B, and ISO 11898-1: 2015
- CAN FD with maximum 64 data bytes supported
- CAN error logging
- AUTOSAR and J1939 support
- Improved acceptance filtering
- Two receive FIFOs of three payloads each (up to 64 bytes per payload)
- Separate signaling on reception of high priority messages
- Configurable transmit FIFO/queue of three payloads (up to 64 bytes per payload)
- Transmit event FIFO
- Programmable loop-back test mode
- Maskable module interrupts
- Two clock domains: APB bus interface and CAN core kernel clock
- Power-down support

## 46.3 FDCAN implementation

The table below describes the FDCAN implementation.

**Table 470. FDCAN features**

| Feature | STM32C53x/C54x | STM32C55x/C56x | STM32C59x/C5Ax |
|---|---|---|---|
| FDCAN1 | X | X | X |
| FDCAN2 | X | - | X |

*Digest note:* within the STM32C55x line, FDCAN1 is available only on STM32C552xx (datasheet digest). Everything about FDCAN2 in this chapter (second message RAM block at 0x0350, FDCAN2 interrupts, "multiple instances" text) does not apply to STM32C551/C552.

## 46.4 FDCAN functional description

### 46.4.1 FDCAN block diagram

**Figure 694. FDCAN block diagram** (described)

Same internal structure as the CANFDL block of Figure 693, with generic signal names: interrupts interface (fdcan_intr0_it, fdcan_intr1_it); control and configuration registers (Ctrl_APB, fdcan_pclk); CAN core clocked by fdcan_tq_ck with pins FDCAN_RX and FDCAN_TX, connected through Sync blocks (Tx Req, Tx State, Rx State); TX handler (TX prioritization, Frame Synchro) with output fdcan_txeof_evt; RX handler (acceptance filter) with output fdcan_rxeof_evt; message RAM interface; external timestamp input fdcan_ts[0:15]. The figure marks a kernel clock domain and an APB clock domain.

#### Dual interrupt lines

The FDCAN peripheral provides two interrupt lines, fdcan_intr0_it and fdcan_intr1_it. By programming the EINT0 and EINT1 bits of the FDCAN_ILE register, the interrupt lines can be independently enabled or disabled.

#### CAN core

The CAN core contains the protocol controller and receive/transmit shift registers. It handles all ISO 11898-1: 2015 protocol functions and supports both 11-bit and 29-bit identifiers.

#### Sync

This block synchronizes signals from the APB clock domain to the CAN kernel clock domain and vice versa.

#### Tx handler

The Tx handler controls the message transfer from the message RAM to the CAN core. A maximum of three Tx buffers is available for transmission. The Tx buffer can be used as Tx FIFO or as a Tx queue. Tx event FIFO stores Tx timestamps together with the corresponding message ID. Transmit cancellation is also supported.

The Tx handler also generates an event on the fdcan_txeof_evt output when the end-of-frame transmission is issued. This event is internally connected to the TIM2 and TIM3 input capture.

*Digest note:* per RM0522 Table 3, TIM3 exists only on STM32C59x/C5A3; on STM32C551/C552 only the TIM2 connection applies.

#### Rx handler

The Rx handler controls the transfer of received messages from the CAN core to the external message RAM. The Rx handler supports two receive FIFOs, for storage of all messages that have passed acceptance filtering. An Rx timestamp is stored together with each message. Up to 28 filters can be defined for 11-bit IDs; up to eight filters for 29-bit IDs.

The Rx handler also generates an event on the fdcan_rxeof_evt output when the end-of-frame reception is received. This event is internally connected to the TIM2 and TIM3 input capture.

#### APB interface

The APB interface connects the FDCAN to the APB bus for configuration registers, controller configuration, and RAM access.

#### Message RAM interface

The message RAM interface connects the FDCAN access to an external 1-Kbyte message RAM through a RAM controller/arbiter.

*Digest note:* the chapter says both "0.8-Kbyte message RAM per FDCAN instance" (46.1) and "1-Kbyte message RAM" (here). The used layout is 212 words = 0x350 bytes = 848 bytes per instance (Section 46.4.6); on STM32C55x the FDCAN SRAM address window is 1 Kbyte (0x4000 AC00 – 0x4000 AFFF).

### 46.4.2 FDCAN pins and internal signals

The CAN subsystem I/O signals and pins are detailed, respectively, in Table 471, Table 472, and Figure 693.

**Table 471. CAN subsystem I/O signals**

| Name | Type | Description |
|---|---|---|
| fdcan_ker_ck | Digital input | CAN subsystem kernel clock input |
| fdcan_pclk | Digital input | CAN subsystem APB interface clock input |
| fdcan_intr0_it | Digital output | FDCAN interrupt0 |
| fdcan_intr1_it | Digital output | FDCAN interrupt1 |
| fdcan_ts[0:15] | - | External timestamp vector |
| fdcan_txeof_evt | Digital output | End-of-frame transmission event |
| fdcan_rxeof_evt | Digital output | End-of-frame reception event |
| APB interface | Digital input/output | Single APP with multiple psel for configuration, control and RAM access |

**Table 472. CAN subsystem I/O pins**

| Name | Type | Description |
|---|---|---|
| FDCAN_RX | Digital input | FDCAN receive pin |
| FDCAN_TX | Digital output | FDCAN transmit pin |

### 46.4.3 Bit timing

The bit timing logic monitors the serial bus-line and performs sampling and adjustment of the sample point by synchronizing on the start-bit edge and resynchronizing on the following edges.

As shown in Figure 695, this operation can be explained simply by splitting the bit time in three segments, as follows:

- Synchronization segment (SYNC_SEG): a bit change is expected to occur within this time segment, having a fixed length of one time quantum (1 × tq).
- Bit segment 1 (BS1): defines the location of the sample point. It includes the PROP_SEG and PHASE_SEG1 of the CAN standard. Its duration is programmable from 1 to 32 time quanta, but can be automatically lengthened to compensate for positive phase drifts due to differences in the frequency of various nodes of the network.
- Bit segment 2 (BS2): defines the location of the transmit point. It represents the PHASE_SEG2 of the CAN standard, its duration is programmable between 1 and 16 time quanta, but can also be automatically shortened to compensate for negative phase drifts.

**Figure 695. Bit timing** (described)

The bit time is drawn as three consecutive segments: SyncSeg (duration tSyncSeg), Bit segment 1 (BS1, duration tBS1) and Bit segment 2 (BS2, duration tBS2). The sample point is at the end of BS1 (boundary BS1/BS2); the transmit point is at the end of BS2.

The baud rate is the inverse of the bit time (baud rate = 1 / bit time), which, in turn, is the sum of three components (see Figure 695):

bit time = tSyncSeg + tBS1 + tBS2

Where:

- For the nominal bit time
  - tq = (NBRP[8:0] + 1) × tfdcan_tq_clk
  - tSyncSeg = 1 × tq
  - tBS1 = tq × (NTSEG1[7:0] + 1)
  - tBS2 = tq × (NTSEG2[6:0] + 1)
  - Where NBRP[8:0], NTSEG1[7:0], and NTSEG2[6:0] bitfields belong to the FDCAN_NBTP register.
- For the data bit time
  - tq = (DBRP[4:0] + 1) × tfdcan_tq_clk
  - tSyncSeg = 1 × tq
  - tBS1 = tq × (DTSEG1[4:0] + 1)
  - tBS2 = tq × (DTSEG2[3:0] + 1)
  - Where DBRP[4:0], DTSEG1[4:0], and DTSEG2[3:0] belong to the FDCAN_DBTP register.

The (re)synchronization jump width (SJW) defines an upper bound for the amount of lengthening or shortening of the bit segments. It is programmable between one and four time quanta.

A valid edge is defined as the first transition in a bit time from dominant to recessive bus level, provided the controller itself does not send a recessive bit.

If a valid edge is detected in BS1 instead of SYNC_SEG, BS1 is extended by up to SJW, so that the sample point is delayed.

Conversely, if a valid edge is detected in BS2 instead of SYNC_SEG, BS2 is shortened by up to SJW, so that the transmit point is moved earlier.

As a safeguard against programming errors, the configuration of the bit timing register is only possible while the device is in Standby mode. The FDCAN_DBTP and FDCAN_NBTP registers (dedicated, respectively, to data and nominal bit timing) are only accessible when the CCE and INIT of the FDCA_CCCR register are set.

The FDCAN requires that the CAN time quanta clock is always below or equal to the APB clock (fdcan_tq_ck ≤ fdcan_pclk).

*Note:* For a detailed description of the CAN bit timing and resynchronization mechanism, refer to the ISO 11898-1 standard.

*Digest note:* the segment ranges quoted above (BS1 1 to 32 tq, BS2 1 to 16 tq, SJW 1 to 4 tq) are narrower than the register fields. Per the register descriptions (Sections 46.5.3 and 46.5.7): nominal NTSEG1 0 to 255 (1 to 256 tq), NTSEG2 0 to 127 (1 to 128 tq), NSJW 0 to 127 (1 to 128 tq), NBRP 0 to 511 (1 to 512); data DTSEG1 0 to 31 (1 to 32 tq), DTSEG2 0 to 15 (1 to 16 tq), DSJW 0 to 15 (1 to 16 tq), DBRP 0 to 31 (1 to 32). "Standby mode" here means the initialization state (INIT = 1, CCE = 1). Per Figure 693, tfdcan_tq_clk is the period of fdcan_tq_ck, which is fdcan_ker_ck after the FDCAN_CKDIV divider.

### 46.4.4 Operating modes

#### Configuration

Access to peripheral version, hardware, and input clock divider configuration. When the clock divider is set to 0, the primary input clock is used as it is.

The reachable FDCAN bitrates are:

- Nominal bitrate: up to 1 Mbit/s
- Data bitrate: between nominal bitrate and 8 Mbit/s

#### Software initialization

Software initialization is started by setting the INIT bit of the FDCAN_CCCR register, by software, by a hardware reset, or by entering bus-off state. While the INIT bit is set, message transfers from and to the CAN bus are stopped, and the status of the CAN bus output FDCAN_TX is recessive (high). The EML (error management logic) counters are unchanged. Setting the INIT bit does not change any configuration register. Clearing INIT bit of FDCAN_CCCR finishes the software initialization. Afterwards the bit stream processor (BSP) synchronizes itself to the data transfer on the CAN bus by waiting for the occurrence of a sequence of 11 consecutive recessive bits (bus-idle) before it can take part in bus activities and start the message transfer.

Access to the FDCAN configuration registers is only enabled when the INIT bit and the CCE bit of the FDCAN_CCCR register are both set.

The CCE bit of the FDCAN_CCCR register can only be set/cleared while the INIT bit of FDCAN_CCCR is set. The CCE bit is automatically cleared when the INIT bit is cleared.

The following registers are reset when the CCE bit of the FDCAN_CCCR register is set:

- FDCAN_HPMS: High priority message status
- FDCAN_RXF0S: Rx FIFO 0 status
- FDCAN_RXF1S: Rx FIFO 1 status
- FDCAN_TXFQS: Tx FIFO/queue status
- FDCAN_TXBRP: Tx buffer request pending
- FDCAN_TXBTO: Tx buffer transmission occurred
- FDCAN_TXBCF: Tx buffer cancellation finished
- FDCAN_TXEFS: Tx event FIFO status

The timeout counter value (TOC[15:0] bit of the FDCAN_TOCV register) is preset to the value configured by the TOP[15:0] of the FDCAN_TOCC register when the CCE bit of the FDCAN_CCCR is set.

In addition, the state machines of the Tx handler and Rx handler are held in idle state while the CCE bit is set.

The following registers can be written only when the CCE bit is cleared:

- FDCAN_TXBAR: Tx buffer add request
- FDCAN_TXBCR: Tx buffer cancellation request

The TEST and the MON bits of the FDCAN_CCCR register can be set only by software while the INIT and the CCE bits of the FDCAN_CCCR register are both set. Both bits can be reset at any time. The DAR bit of FDCAN_CCCR can only be set/cleared while the INIT and CCE bits are both set.

#### Normal operation

The FDCAN default operating mode after hardware reset is event-driven CAN communication. TT operation mode is not supported.

Once the FDCAN is initialized and the INIT bit of the FDCAN_CCCR register is cleared, the FDCAN synchronizes itself to the CAN bus and is ready for communication.

After passing the acceptance filtering, received messages including message ID and DLC are stored into the Rx FIFO 0 or Rx FIFO 1.

For messages to be transmitted, the Tx FIFO or the Tx queue can be initialized or updated. Automated transmission on reception of remote frames is not supported.

#### CAN FD operation

There are two variants in the FDCAN protocol:

- Long frame mode (LFM), where the data field of a CAN frame may be longer than eight bytes.
- Fast frame mode (FFM), where the control field, data field, and CRC field of a CAN frame are transmitted with a higher bit rate compared to the beginning and to the end of the frame.

The fast frame mode can be used in combination with the long frame mode.

The previously reserved bit in CAN frames with 11-bit identifiers and the first previously reserved bit in CAN frames with 29-bit identifiers are decoded as FDF bit: FDF recessive signifies a CAN FD frame, while FDF dominant signifies a classic CAN frame.

In a CAN FD frame, the two bits following FDF (res and BRS) decide whether the bit rate inside this CAN FD frame is switched. A CAN FD bit rate switch is signified by res dominant and BRS recessive. The coding of res recessive is reserved for future expansion of the protocol. In case the FDCAN receives a frame with FDF recessive and res recessive, it signals a protocol exception event by setting the PXE bit of the FDCAN_PSR register. When protocol exception handling is enabled (PXHD = 0 in FDCAN_CCCR), this causes the operation state to change from receiver (ACT[1:0] = 10 in FDCAN_PSR) to integrating (ACT[1:0] = 00 in FDCAN_PSR) at the next sample point. If protocol exception handling is disabled (PXHD = 1 in FDCAN_CCCR), the FDCAN treats a recessive res bit as a form error and responds with an error frame.

CAN FD operation is enabled by programming the FDOE bit of the FDCAN_CCCR register. In case FDOE = 1, transmission and reception of CAN FD frames are enabled. Transmission and reception of classic CAN frames are always possible. Whether a CAN FD frame or a classic CAN frame is transmitted can be configured via the FDF bit in the respective Tx buffer element. With FDOE = 0, received frames are interpreted as classic CAN frames, which leads to the transmission of an error frame when receiving a CAN FD frame. When CAN FD operation is disabled, no CAN FD frames are transmitted even if the FDF bit of a Tx buffer element is set. The FDOE and BRSE bits of the FDCAN_CCCR register can only be changed while the INIT and CCE bits are both set.

With FDOE = 0, the setting of the FDF and BRS bits is ignored, and frames are transmitted in classic CAN format. With FDOE = 1 and BRSE = 0, only the FDF bit of a Tx buffer element is evaluated. With FDOE = 1 and BRSE = 1, transmission of CAN FD frames with bit rate switching is enabled. All Tx buffer elements with FDF and BRS bits set are transmitted in CAN FD format with bit rate switching.

A mode change during CAN operation is recommended only under the following conditions:

- The failure rate in the CAN FD data phase is significant higher than in the CAN FD arbitration phase. In this case, disable the CAN FD bit rate switching option for transmissions.
- During system startup, all nodes transmit classic CAN messages until it is verified that they are able to communicate in CAN FD format. If this is true, all nodes switch to CAN FD operation.
- Wake-up messages in CAN partial networking have to be transmitted in classic CAN format.
- End-of-line programming in case not all nodes are CAN FD capable. Non-CAN FD nodes are held in silent mode until programming is complete. Then all nodes switch back to classic CAN communication.

In the FDCAN format, the coding of the DLC differs from that of the standard CAN format. The DLC codes 0 to 8 have the same coding as in standard CAN, the codes 9 to 15 (that in standard CAN all code a data field of 8 bytes) are coded according to Table 473.

**Table 473. DLC coding in FDCAN**

| DLC | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|
| Number of data bytes | 12 | 16 | 20 | 24 | 32 | 48 | 64 |

In CAN FD fast frames, the bit timing is switched inside the frame, after the BRS (bit rate switch) bit, if this bit is recessive. Before the BRS bit, in the FDCAN arbitration phase, the standard CAN bit timing is used as defined by the FDCAN_DBTP register. In the following FDCAN data phase, the fast CAN bit timing is used as defined by the FDCAN_DBTP register. The bit timing is switched back from the fast timing at the CRC delimiter or when an error is detected, whichever occurs first.

*Digest note:* the arbitration-phase (nominal) bit timing is defined by FDCAN_NBTP, not FDCAN_DBTP as printed in the first sentence above (see Section 46.4.3).

The maximum configurable bit rate in the CAN FD data phase depends on the FDCAN kernel clock frequency. For example, with an FDCAN kernel clock frequency of 20 MHz and the shortest configurable bit time of four time quanta (tq), the bit rate in the data phase is 5 Mbit/s.

In both data frame formats (CAN FD long frames and CAN FD fast frames), the value of bit ESI (error status indicator) is determined by the transmitter error state at the start of the transmission. If the transmitter is error passive, ESI is transmitted recessive, else it is transmitted dominant. In CAN FD remote frames, the ESI bit is always transmitted dominant, independent of the transmitter error state. The data length code of CAN FD remote frames is transmitted as 0.

In case an FDCAN Tx buffer is configured for FDCAN transmission with DLC > 8, the first eight bytes are transmitted as configured in the Tx buffer while the remaining part of the data field is padded with 0xCC. When the FDCAN receives a FDCAN frame with DLC > 8, the first eight bytes of that frame are stored into the matching Rx FIFO. The remaining bytes are discarded.

*Digest note:* this paragraph conflicts with Sections 46.2, 46.4.8 and 46.4.9, which state that Rx FIFO and Tx buffer elements are sized for a 64-byte data field. [unclear in source: whether the 8-byte truncation/0xCC padding behavior applies to this implementation.] It does not affect classic CAN 2.0 frames (DLC ≤ 8 data bytes).

#### Transceiver delay compensation

During the data phase of an FDCAN transmission, only one node is transmitting, all others are receivers. The length of the bus line has no impact. When transmitting via pin FDCAN_TX, the protocol controller receives the transmitted data from its local CAN transceiver via pin FDCAN_RX. The received data is delayed by the CAN transceiver loop delay. If this delay is greater than TSEG1 (time segment before sample point), and a bit error is detected. Without transceiver delay compensation, the bit rate in the data phase of an FDCAN frame is limited by the transceiver loop delay.

The FDCAN implements a delay compensation mechanism to compensate the CAN transceiver loop delay, thereby enabling transmission with higher bit rates during the FDCAN data phase independent of the delay of a specific CAN transceiver.

To check for bit errors during the data phase of transmitting nodes, the delayed transmit data is compared against the received data at the secondary sample point (SSP). If a bit error is detected, the transmitter reacts on this bit error at the next following regular sample point. During the arbitration phase, the delay compensation is always disabled.

The transmitter delay compensation enables configurations where the data bit time is shorter than the transmitter delay. This is enabled by setting the TDC bit of the FDCAN_DBTP register, and described in detail in the ISO11898-1 specification.

The received bit is compared against the transmitted bit at the SSP. The SSP position is defined as the sum of the measured delay from the FDCAN transmit output pin FDCAN_TX through the transceiver to the receive input pin FDCAN_RX plus the transmitter delay compensation offset as configured by TDCO[6:0] of FDCAN_TDCR. The transmitter delay compensation offset is used to adjust the position of the SSP inside the received bit (for example, half of the bit time in the data phase). The position of the secondary sample point is rounded down to the next integer number of mtq (minimum time quantum, one period of fdcan_tq_ck clock).

The TDCV[6:0] bitfield of the FDCAN_PSR register shows the actual transmitter delay compensation value. TDCV[6:0] is cleared when the INIT is set in the FDCAN_CCCR. It is updated at each transmission of an FD frame while the TDC bit of the FDCAN_DBTP register is set.

The following boundary conditions have to be considered for the transmitter delay compensation implemented in the FDCAN:

- The sum of the measured delay from FDCAN_Tx to FDCAN_Rx and the configured transmitter delay compensation offset TDCO[6:0] has to be lower than 6-bit times in the data phase.
- The sum of the measured delay from FDCAN_TX to FDCAN_RX and the configured transmitter delay compensation offset TDCO[6:0] has to be lower than or equal to 127 × mtq. If the sum exceeds this value, the maximum value (127 × mtq) is used for transmitter delay compensation.
- The data phase ends at the sample point of the CRC delimiter, which stops checking received bits at the SSPs.

If transmitter delay compensation is enabled by setting the TDC bit of the FDCAN_DBTP; the measurement is started within each transmitted CAN FD frame at the falling edge of bit FDF to bit res. The measurement is stopped when this edge is seen at the receive input pin FDCAN_TX of the transmitter. The resolution of this measurement is one mtq.

*Digest note:* "receive input pin FDCAN_TX" in the sentence above should read FDCAN_RX (the receive input).

**Figure 696. Transceiver delay measurement** (described)

FDCAN_TX and FDCAN_RX waveforms show the bit sequence FDF, Res., BRS, ESI, DLC, with the arbitration phase before and the data phase after the bit rate switch; FDCAN_RX is shifted later by the transmitter delay. A delay counter clocked by fdcan_tq_ck starts at the FDF-to-res falling edge on FDCAN_TX and stops when that edge appears on FDCAN_RX. The measured delay is added to the delay compensation offset TDCR.TDCO to give the SSP position.

To avoid that a dominant glitch inside the received FDF bit ends the delay compensation measurement before the falling edge of the received res bit (resulting in a too early SSP position), the use of a transmitter delay compensation filter window can be enabled by programming the TDCF[6:0] bitfield of the FDCAN_TDCR register. This defines a minimum value for the SSP position. Dominant edges on FDCAN_RX that would result in an earlier SSP position are ignored for transmitter delay measurement. The measurement is stopped when the SSP position is at least TDCF[6:0] and FDCAN_RX is low.

#### Restricted operation mode

In restricted operation mode, the node is able to receive data and remote frames, and to give acknowledge to valid frames, but it does not send data frames, remote frames, active error frames, or overload frames. In case of an error condition or overload condition, it does not send dominant bits. Instead, it waits for the occurrence of a bus-idle condition to resynchronize itself to the CAN communication. The error counters (REC[6:0] and TEC[7:0] in FDCAN_ECR) are frozen while the error logging (CEL[7:0]) is active. The software can set the FDCAN into restricted operation mode by setting the ASM bit of FDCAN_CCCR. The bit can only be set by software when both CCE and INIT bits are set in FDCAN_CCCR. The bit can be cleared by software at any time.

Restricted operation mode is automatically entered when the Tx handler is not able to read data from the message RAM in time. To leave restricted operation mode, the software has to clear the ASM bit of FDCAN_CCCR.

The restricted operation mode can be used in applications that adapt themselves to different CAN bit rates. In this case, the application tests different bit rates and leaves the restricted operation mode after it has received a valid frame.

*Note:* The restricted operation mode must not be combined with the loop-back mode (internal or external).

#### Bus monitoring mode

The FDCAN is set in bus monitoring mode by setting the MON bit of the FDCAN_CCCR register. In bus monitoring mode (for more details refer to ISO11898-1, 10.12 bus monitoring), the FDCAN is able to receive valid data frames and valid remote frames, but cannot start a transmission. In this mode, it sends only recessive bits on the CAN bus. If the FDCAN is required to send a dominant bit (ACK bit, overload flag, active error flag), the bit is rerouted internally so that the FDCAN can monitor it, even if the CAN bus remains in recessive state. In bus monitoring mode, the FDCAN_TXBRP register is held in reset state.

The bus monitoring mode can be used to analyze the traffic on a CAN bus without affecting it by the transmission of dominant bits. Figure 697 shows the connection of FDCAN_TX and FDCAN_RX signals to the FDCAN in bus monitoring mode.

**Figure 697. Pin control in bus monitoring mode** (described)

The FDCAN_TX pin is driven constant recessive ("=1"). The internal Tx signal is routed internally to the internal Rx input, which also receives the FDCAN_RX pin.

#### Disabled automatic retransmission mode (DAR)

According to the CAN specification (see ISO11898-1, 6.3.3 Recovery Management), the FDCAN provides means for automatic retransmission of frames that have lost arbitration or have been disturbed by errors during transmission. By default, automatic retransmission is enabled. The DAR mode can be disabled through the DAR bit of the FDCAN_CCCR register.

##### Frame transmission in DAR mode

In DAR mode, all transmissions are automatically canceled after they have been started on the CAN bus. A Tx buffer Tx request pending bit (TRPx in FDCAN_TXBRP) is reset after successful transmission, when a transmission has not yet been started at the point of cancellation, when it has been aborted due to lost arbitration, or when an error has occurred during frame transmission.

- Successful transmission
  - The corresponding Tx buffer transmission occurred bit TOx is set in FDCAN_TXBTO register.
  - The corresponding Tx buffer cancellation finished bit CFx is cleared in the FDCAN_TXBCF register.
- Successful transmission in spite of cancellation
  - The corresponding Tx buffer transmission occurred bit TOx is set in the FDCAN_TXBTO register.
  - The corresponding Tx buffer cancellation finished bit CFx is set in the FDCAN_TXBCF register.
- Arbitration loss or frame transmission disturbed
  - The corresponding Tx buffer transmission occurred bit TOx is cleared in the FDCAN_TXBTO register.
  - The corresponding Tx buffer cancellation finished bit CFx is set in the FDCAN_TXBCF register.

In case of a successful frame transmission, and if the storage of Tx events is enabled, a Tx event FIFO element is written with event type ET = 10 (transmission in spite of cancellation).

#### Power-down (Sleep mode)

##### Power-down entry

The FDCAN can be set into power-down mode controlled by setting the CSR bit of the FDCAN_CCCR register. As long as the clock stop request is active, CSR is read as 1.

When all pending transmission requests have completed, the FDCAN waits until the bus-idle state is detected. The FDCAN then sets the INIT bit of the FDCAN_CCCR register to prevent any further CAN transfers. Now, the FDCAN acknowledges that it is ready for power-down by setting the CSA bit of the FDCAN_CCCR register. In this state, before the clocks are switched off, further register accesses can be made. A write access to the INIT bit has no effect. Now, the module clock inputs can be switched off.

##### Power-down exit

To leave power-down mode, the application has to turn on the module clocks before clearing the CSR bit. The FDCAN acknowledges this by clearing the CSA bit. Afterwards, the application can restart CAN communication by clearing the INIT bit.

#### Test modes

To enable write access to FDCAN test register (FDCAN_TEST), the TEST bit of the FDCAN_CCCR register must be set, thus enabling the configuration of test modes and functions.

Four output functions are available for the CAN transmit pin FDCAN_TX by programming the TX[1:0] bitfield of the FDCAN_TEST register. In addition to its default function (the serial data output), it can drive the CAN sample point signal to monitor the FDCAN bit timing as well as drive constant dominant or recessive values. The actual value at pin FDCAN_RX can be read from the RX bit of FDCAN_TEST. Both functions can be used to check the CAN bus physical layer.

Due to the synchronization mechanism between CAN kernel clock and APB clock domain, there can be a delay of several APB clock periods between writing to TX[1:0] until the new configuration is visible at FDCAN_TX output pin. This applies also when reading FDCAN_RX input pin via RX.

*Note:* Test modes must be used for production tests or self-test only. The software control for FDCAN_TX pin interferes with all CAN protocol functions. It is not recommended to use test modes for application.

#### External loop-back mode

The FDCAN can be set in external loop-back mode by setting the LBCK bit of the FDCAN_TEST register. In loop-back mode, the FDCAN treats its own transmitted messages as received messages and stores them (if they pass acceptance filtering) into Rx FIFOs. Figure 698 shows the connection of transmit and receive signals FDCAN_TX and FDCAN_RX to the FDCAN in external loop-back mode.

This mode is provided for hardware self-test. To be independent from external stimulation, the FDCAN ignores acknowledge errors (recessive bit sampled in the acknowledge slot of a data/remote frame) in loop-back mode. In this mode, the FDCAN performs an internal feedback from its transmit output to its receive input. The actual value of the FDCAN_RX input pin is disregarded by the FDCAN. The transmitted messages can be monitored at the FDCAN_TX transmit pin.

#### Internal loop-back mode

Internal loop-back mode is entered by setting both the LBCK bit of FDCAN_TEST and the MON bit of FDCAN_CCR. This mode can be used for a "hot self-test", meaning the FDCAN can be tested without affecting a running CAN system connected to the FDCAN_TX and FDCAN_RX pins. In this mode, FDCAN_RX pin is disconnected from the FDCAN and FDCAN_TX pin is held recessive. Figure 698 shows the connection of FDCAN_TX and FDCAN_RX pins to the FDCAN in case of internal loop-back mode.

*Digest note:* "FDCAN_CCR" above is the FDCAN_CCCR register.

**Figure 698. Pin control in loop-back mode** (described)

| Mode | FDCANx_Tx pin | FDCAN_Rx pin | Internal path |
|---|---|---|---|
| External loop-back mode | Driven by the internal Tx signal | Disconnected (ignored) | Internal Tx output fed back to internal Rx input |
| Internal loop-back mode | Held recessive ("= 1") | Disconnected (ignored) | Internal Tx output fed back to internal Rx input |

#### Timestamp generation

For timestamp generation, the FDCAN supplies a 16-bit wrap-around counter. A prescaler (TCP[3:0] of FDCAN_TSCC) can be configured to clock the counter in multiples of CAN bit times (1 to 16). The counter is readable via the TCV[15:0] bitfield of the FDCAN_TSCV register. A write access to TSCV15:0] resets the counter to 0. When the timestamp counter wraps around, the interrupt flag (TSW bit of FDCAN_ISR) is set.

On start of frame reception/transmission, the counter value is captured and stored into the timestamp section of an Rx FIFO (RXTS[15:0]) or Tx event FIFO (TXTS[15:0]) element.

By programming TSS[1:0] of FDCAN_TSCC, a 16-bit timestamp can be used.

*Digest note:* the register field is named TSC[15:0] in FDCAN_TSCV (Section 46.5.9), and the TSW flag is in FDCAN_IR (there is no FDCAN_ISR).

#### Debug mode behavior

In debug mode, the set/reset on read feature is automatically disabled during the debugger register access, and enabled during normal MCU operation

#### Timeout counter

To signal timeout conditions for Rx FIFO 0, Rx FIFO 1, and the Tx event FIFO the FDCAN supplies a 16-bit timeout counter. It operates as a down-counter and uses the same prescaler controlled by TCP[3:0] of FDCAN_TSCC as the timestamp counter. The timeout counter is configured via the FDCAN_TOCC register. The actual counter value can be read from the TOC[15:0] bitfield of FDCAN_TOCV. The timeout counter can only be started while the INIT bit of FDCAN_CCCR is cleared. It is stopped when INIT is set, for example, when the FDCAN enters bus-off state.

The operation mode is selected by TOS[1:0] of FDCAN_TOCC. When operating in continuous mode, the counter starts when INIT is cleared. A write to FDCAN_TOCV presets the counter to the value configured by TOP[15:0] in FDCAN_TOCC and continues down-counting.

When the timeout counter is controlled by one of the FIFOs, an empty FIFO presets the counter to the value configured by TOP[15:0]. Down-counting is started when the first FIFO element is stored. Writing to FDCAN_TOCV has no effect.

When the counter reaches 0, the TOO interrupt flag is set in the FDCAN_IR register. In continuous mode, the counter is immediately restarted at TOP[15:0].

*Note:* The clock signal for the timeout counter is derived from the CAN core sample point signal. Therefore, the point in time where the timeout counter is decremented may vary due to the synchronization/resynchronization mechanism of the CAN core. If the baud rate switch feature in FDCAN is used, the timeout counter is clocked differently in the arbitration and data fields.

### 46.4.5 Error management

As described in the CAN protocol, the error management is handled entirely by hardware using the transmit error counter (the TEC[7:0] bitfield of the FDCAN error counter register (FDCAN_ECR)) and the receive error counter (the REC[6:0] bitfield of the FDCAN error counter register (FDCAN_ECR)). These values are incremented or decremented according to the error condition. For detailed information on TEC[7:0] and REC[6:0] management, refer to the CAN standard. Both values can be read by software to determine the stability of the network.

The bus-off state is reached when TEC[7:0] is greater than 255. This state is also indicated by the BO flag of the FDCAN protocol status register (FDCAN_PSR). In bus-off state, the CAN is no longer able to transmit and receive messages. It has to wait at least for the duration of the recovery sequence specified in the CAN standard (129 occurrences of 11 consecutive recessive bits monitored on FDCAN_RX input).

**Figure 699. CAN error state diagram** (described)

| From state | Condition | To state |
|---|---|---|
| ERROR ACTIVE | When TEC or REC > 127 | ERROR PASSIVE |
| ERROR PASSIVE | When TEC and REC < 128 | ERROR ACTIVE |
| ERROR PASSIVE | When TEC > 255 | BUS OFF |
| BUS OFF | When 129 occurrences of 11 recessive bits occur | ERROR ACTIVE |

*Note:* In initialization mode, the CAN does not monitor the FDCAN_RX signal, and therefore cannot complete the recovery sequence. To recover from an error state, the CAN must operate in normal mode.

### 46.4.6 Message RAM

The message RAM is 32-bit wide, and the FDCAN module is configured to allocate up to 212 words in it. It is not necessary to configure each of the sections shown in Figure 700.

**Figure 700. Message RAM configuration** (as table)

The figure shows one instance's message RAM as a 32-bit wide column of six consecutive sections. "Start offset" and "Elements / words" are as printed in the figure; the remaining columns are derived by the digest (words ÷ elements, and start offset + size − 1).

| Section | Start address name | Start offset (bytes) | Elements / words | Element size (derived) | Last byte offset (derived) |
|---|---|---|---|---|---|
| 11-bit filter | FLSSA | 0x0000 | 28 elements / 28 words | 1 word (4 bytes) | 0x006F |
| 29-bit filter | FLESA | 0x0070 | 8 elements / 16 words | 2 words (8 bytes) | 0x00AF |
| Rx FIFO 0 | - | 0x00B0 | 3 elements / 54 words | 18 words (72 bytes = 0x48) | 0x0187 |
| Rx FIFO 1 | - | 0x0188 | 3 elements / 54 words | 18 words (72 bytes = 0x48) | 0x025F |
| Tx event FIFO | EFSA | 0x0260 | 3 elements / 6 words | 2 words (8 bytes) | 0x0277 |
| Tx buffers | TBSA | 0x0278 | 3 elements / 54 words | 18 words (72 bytes = 0x48) | 0x034F |

*Digest note:* total = 212 words = 0x350 bytes. The layout is fixed: there are no FLSSA/FLESA/F0SA/F1SA/EFSA/TBSA or element-size registers in this FDCAN (compare Section 46.5.38). Derived element byte offsets: Rx FIFO 0 elements 0/1/2 at 0x00B0/0x00F8/0x0140; Rx FIFO 1 elements at 0x0188/0x01D0/0x0218; Tx event FIFO elements at 0x0260/0x0268/0x0270; Tx buffers 0/1/2 at 0x0278/0x02C0/0x0308; standard filter n at 0x0000 + 4 × n; extended filter n at 0x0070 + 8 × n. On STM32C552 (FDCAN1 only) the CPU address is 0x4000 AC00 + offset (SRAMCAN_BASE, see the note at the top of this file).

When the FDCAN addresses the message RAM, it addresses 32-bit words (aligned), not a single byte. The RAM addresses are 32-bit words, that is, only bits 15 to 2 are evaluated, the two least significant bits are ignored.

In case of multiple instances, the RAM start address for the FDCANn is computed by end address + 4 of FDCANn - 1, and the FDCANn end address is computed by FDCANn start address + 0x0350 - 4.

As an example, for two instances:

- FDCAN1:
  - Start address 0x0000
  - End address 0x034C (as in Figure 700)
- FDCAN2:
  - Start address = 0x034C (FDCAN1 end address) + 4 = 0x0350
  - End address = 0x0350 (FDCAN2 start address) + 0x0350 - 4 = 0x069C.

*Digest note:* FDCAN2 does not exist on STM32C55x; on STM32C552 only the FDCAN1 block (0x0000–0x034F) is used.

#### Rx handling

The Rx handler controls the acceptance filtering, the transfer of received messages to one of the two Rx FIFOs, as well as the Rx FIFO put and get indices.

#### Acceptance filter

The FDCAN offers the possibility to configure two sets of acceptance filters, one for standard identifiers and another for extended identifiers. These filters can be assigned to Rx FIFO 0 or Rx FIFO 1. For acceptance filtering, each list of filters is executed from element #0 until the first matching element. Acceptance filtering stops at the first matching element, and the following filter elements are not evaluated for this message.

The main features are:

- Each filter element can be configured as
  - Range filter (from - to)
  - Filter for one or two dedicated IDs
  - Classic bit mask filter
- Each filter element is configurable for acceptance or rejection filtering.
- Each filter element can be enabled/disabled individually.
- Filters are checked sequentially, execution stops with the first matching filter element

Related configuration registers are:

- Global filter configuration (RXGFC)
- Extended ID AND mask (XIDAM)

Depending on the configuration of the filter element (SFEC[2:0]/EFEC[2:0]), a match triggers one of the following actions:

- Store received frame in FIFO 0 or FIFO 1
- Reject received frame
- Set the high priority message interrupt flag HPM in FDCAN_IR
- Set the high priority message interrupt flag HPM in FDCAN_IR, and store the received frame in FIFO 0 or FIFO 1.

Acceptance filtering is started after the complete identifier has been received. After acceptance filtering has completed, and if a matching Rx FIFO has been found, the message handler starts writing the received message data in 32-bit portions to the matching Rx FIFO. If the CAN protocol controller has detected an error condition (for example, CRC error), this message is discarded with the following impact:

- Rx FIFO
  The put index of the matching Rx FIFO is not updated, but the related Rx FIFO element is partly overwritten with the received data. For error type, see LEC[2:0] and DLEC[2:0] bitfields of the FDCAN_PSR register. In case the matching Rx FIFO is operated in overwrite mode, the boundary conditions described in Rx FIFO overwrite mode have to be considered.

*Note:* When an accepted message is written to one of the two Rx FIFOs, the unmodified received identifier is stored independently from the used filters. The result of the acceptance filter process strongly depends on the sequence of configured filter elements.

#### Range filter

The filter matches for all received frames with message IDs in the range defined by SF1ID/SF2ID and EF1ID/EF2ID.

There are two possibilities when range filtering is used together with extended frames:

- EFT[1:0] = 00: the message ID of received frames is AND-ed with the extended ID AND mask (XIDAM) before the range filter is applied.
- EFT[1:0] = 11: the extended ID AND mask (XIDAM) is not used for range filtering.

#### Filter for dedicated IDs

A filter element can be configured to filter for one or two specific message IDs. To filter for one specific message ID, the filter element has to be configured with SF1ID = SF2ID and EF1ID = EF2ID.

#### Classic bit mask filter

The classic bit mask filtering is intended to filter groups of message IDs by masking single bits of a received message ID. With classic bit mask filtering SF1ID/EF1ID is used as message ID filter, while SF2ID/EF2ID is used as filter mask.

0 bit at the filter mask masks out the corresponding bit position of the configured ID filter. For example, the value of the received message ID at that bit position is not relevant for acceptance filtering. Only the bits of the received message ID where the corresponding mask bits are 1 are relevant for acceptance filtering.

In case all mask bits are 1, a match occurs only when the received message ID and the message ID filter are identical. If all mask bits are 0, all message IDs match.

*Digest note:* SF1ID/SF2ID and EF1ID/EF2ID in this section are the SFID1/SFID2 and EFID1/EFID2 fields of the filter elements (Sections 46.4.11 and 46.4.12).

#### Standard message ID filtering

Figure 701 shows the flow for standard message ID (11-bit identifier) filtering. The standard message ID filter element is described in Section 46.4.11.

The standard message filtering is controlled by the FDCAN_RXGFC register. The standard message ID, the remote transmission request bit (RTR), and the identifier extension bit (IDE) of the received frames are compared against the list of configured filter elements.

**Figure 701. Standard message ID filter path** (described)

1. Valid frame received. If the identifier is 29-bit, the frame goes to the extended path (Figure 702); if 11-bit, continue.
2. Remote frame? If yes: with RXGFC[RRFS] = 1 the remote frame is rejected (discard frame); with RXGFC[RRFS] = 0 it continues like a data frame.
3. Receive filter list enabled? If RXGFC[LSS[7:0]] = 0, go directly to step 5 (non-matching frame handling). If RXGFC[LSS[7:0]] > 0, continue.
4. Match filter element #0, then the next elements, up to element #RXGFC.LSS. On the first match, go to "Acceptance or Rejection": a reject element discards the frame; an accept element goes to step 6. If no element matches, go to step 5.
5. Accept non-matching frames: RXGFC[ANFS[1]] = 1 discards the frame; RXGFC[ANFS[1]] = 0 goes to step 6.
6. Target FIFO full? If yes, discard frame; if no, append to target FIFO.

*Digest note:* the figure writes LSS[7:0]; the register field is LSS[4:0] (Section 46.5.19).

#### Extended message ID filtering

Figure 702 shows the flow for extended message ID (29-bit identifier) filtering. The extended message ID filter element is described in Section 46.4.12.

The extended message filtering is controlled by the FDCAN_RXGFC register. The extended message ID, the remote transmission request bit (RTR), and the identifier extension bit (IDE) of the received frames are compared against the list of configured filter elements.

**Figure 702. Extended message ID filter path** (described)

Same flow as Figure 701 with the extended-ID controls:

1. Valid frame received. If the identifier is 11-bit, the frame goes to the standard path (Figure 701); if 29-bit, continue.
2. Remote frame? If yes: with RXGFC[RRFE] = 1 the remote frame is rejected (discard frame); with RXGFC[RRFE] = 0 it continues.
3. Receive filter list enabled? If RXGFC[LSE[3:0]] = 0, go directly to step 5. If RXGFC[LSE[3:0]] > 0, continue.
4. Match filter element #0 ... element #RXGFC.LSE. On the first match, go to "Acceptance or Rejection": reject discards the frame; accept goes to step 6. If no element matches, go to step 5.
5. Accept non-matching frames: RXGFC[ANFE[1]] = 1 discards the frame; RXGFC[ANFE[1]] = 0 goes to step 6.
6. Target FIFO full? If yes, discard frame; if no, append to target FIFO.

The extended ID AND mask (XIDAM) is AND-ed with the received identifier before the filter list is executed.

#### Rx FIFOs

Rx FIFO 0 and Rx FIFO 1 can hold up to three elements each.

Received messages that passed acceptance filtering are transferred to the Rx FIFO as configured by the matching filter element. For a description of the filter mechanisms available for Rx FIFO 0 and Rx FIFO 1, see Acceptance filter. The Rx FIFO element is described in Section 46.4.8.

When an Rx FIFO full condition is signaled by RFnF in FDCAN_IR (where n is the FIFO number), no further messages are written to the corresponding Rx FIFO until at least one message has been read out, and the Rx FIFO get index has been incremented. In case a message is received while the corresponding Rx FIFO is full, this message is discarded, and the interrupt flag RFnL is set in the FDCAN_IR register.

When reading from an Rx FIFO, the Rx FIFO get index (FnGI of FDCAN_RXFnS) + FIFO element size has to be added to the corresponding Rx FIFO start address (FnSA).

*Digest note:* read as "get index × element size". With the fixed layout, element n of Rx FIFO 0 is at message RAM offset 0x00B0 + 0x48 × n, and of Rx FIFO 1 at 0x0188 + 0x48 × n. There is no FnSA register in this FDCAN; the start addresses are the fixed offsets of Figure 700.

#### Rx FIFO blocking mode

The Rx FIFO blocking mode is configured by clearing the FnOM bit in the FDCAN_RXGFC register. This is the default operation mode for the Rx FIFOs.

When an Rx FIFO full condition is reached (FnPI = FnGI in FDCAN_RXFnS), no further messages are written to the corresponding Rx FIFO until at least one message has been read out and the Rx FIFO get index has been incremented. An Rx FIFO full condition is signaled by FnF = 1 in FDCAN_RXFnS. In addition, the RFnF interrupt flag is set in FDCAN_IR.

In case a message is received while the corresponding Rx FIFO is full, this message is discarded, and the message lost condition is signaled by setting RFnL bit in FDCAN_RXFnS. In addition, the RFnL interrupt flag is set in FDCAN_IR.

#### Rx FIFO overwrite mode

The Rx FIFO overwrite mode is configured by setting the FnOM bit of the FDCAN_RXGFC register.

When an Rx FIFO full condition (FnPI = FnGI of FDCAN_RXFnS) is signaled by FnF = 1 in FDCAN_RXFnS, the next message accepted for the FIFO overwrites the oldest FIFO message. Put and get indices are both incremented by one.

When an Rx FIFO is operated in overwrite mode and an Rx FIFO full condition is signaled, reading from the Rx FIFO elements must start at least at get index + 1. This is because it may happen that a received message is written to the message RAM (put index) while the CPU is reading from the message RAM (get index). In this case, inconsistent data can be read from the respective Rx FIFO element. Adding an offset to the get index when reading from the Rx FIFO avoids this problem. The offset depends on how fast the CPU accesses the Rx FIFO.

After reading from the Rx FIFO, the number of the last element read has to be written to the Rx FIFO acknowledge index (FnA of FDCAN_RXFnA). This increments the get index to that element number. In case the put index has not been incremented to this Rx FIFO element, the Rx FIFO full condition is reset (FnF = 0 in FDCAN_RXFnS).

#### Tx handling

The Tx handler handles transmission requests for the Tx FIFO and the Tx queue. It controls the transfer of transmit messages to the CAN core, the put and get indices, and the Tx event FIFO. Up to three Tx buffers can be set up for message transmission. The CAN message data field is configured to 64 bytes. the Tx FIFO allocates eighteen 32-bit words for storage of a Tx element.

**Table 474. Possible configurations for frame transmission**

| CCCR BRSE | CCCR FDOE | Tx buffer element FDF | Tx buffer element BRS | Frame transmission |
|---|---|---|---|---|
| Ignored | 0 | Ignored | Ignored | Classic CAN |
| 0 | 1 | 0 | Ignored | Classic CAN |
| 0 | 1 | 1 | Ignored | FD without bit rate switching |
| 1 | 1 | 0 | Ignored | Classic CAN |
| 1 | 1 | 1 | 0 | FD without bit rate switching |
| 1 | 1 | 1 | 1 | FD with bit rate switching |

*Note:* AUTOSAR requires at least three Tx queue buffers and support of transmit cancellation.

The Tx handler starts a Tx scan to check for the highest priority pending Tx request (Tx buffer with lowest message ID) when the Tx buffer request pending register (FDCAN_TXBRP) is updated, or when a transmission has been started.

#### Transmit pause

The transmit pause feature is intended for use in CAN systems where the CAN message identifiers are permanently specified to specific values and cannot easily be changed. These message identifiers can have a higher CAN arbitration priority than other defined messages, while in a specific application their relative arbitration priority must be inverse. This may lead to a case where one ECU sends a burst of CAN messages that cause another ECU CAN messages to be delayed because that other messages have a lower CAN arbitration priority.

As an example, if CAN ECU-1 has the feature enabled and is requested by its application software to transmit four messages, it waits, after the first successful message transmission, for two CAN bit times of bus-idle before it is allowed to start the next requested message. If there are other ECUs with pending messages, these messages are started in the idle time, and they would not need to arbitrate with the next message of ECU-1. After having received a message, ECU-1 is allowed to start its next transmission as soon as the received message releases the CAN bus.

The feature is controlled by the TXP bit of the CCCR register. If the bit is set, the FDCAN, each time it has successfully transmitted a message, pauses for two CAN bit times before starting the next transmission. This enables other CAN nodes in the network to transmit messages even if their messages have lower prior identifiers. By default, this feature is disabled (TXP = 0 in FDCAN_CCCR).

This feature looses up burst transmissions coming from a single node and it protects against "babbling idiot" scenarios where the application program erroneously requests too many transmissions.

#### Tx FIFO

Tx FIFO operation is configured by clearing the TFQM bit of the FDCAN_TXBC register. Messages stored in the Tx FIFO are transmitted starting with the message referenced by the get index (TFGI[1:0] bitfield of FDCAN_TXFQS). After each transmission, the get index is incremented cyclically until the Tx FIFO is empty. The Tx FIFO enables transmission of messages with the same message ID from different Tx buffers in the order that these messages have been written to the Tx FIFO. The FDCAN calculates the Tx FIFO free level (TFFL[2:0] bitfield of FDCAN_TXFQS) as the difference between the get and put index. It indicates the number of available (free) Tx FIFO elements.

New transmit messages have to be written to the Tx FIFO starting with the Tx buffer referenced by the put index (TFQPI[1:0] bitfield of FDCAN_TXFQS). An add request increments the put index to the next free Tx FIFO element. When the put index reaches the get index, Tx FIFO full (TFQF = 1 in FDCAN_TXFQS) is signaled. In this case, no further messages must be written to the Tx FIFO until the next message has been transmitted and the get index has been incremented.

When a single message is added to the Tx FIFO, the transmission is requested by setting the FDCAN_TXBAR bit related to the Tx buffer referenced by the Tx FIFO put index.

When multiple (n) messages are added to the Tx FIFO, they are written to n consecutive Tx buffers starting with the put index. The transmissions are then requested via the FDCA_TXBAR register. The put index is then cyclically incremented by n. The number of requested Tx buffers must not exceed the number of free Tx buffers as indicated by the Tx FIFO free level.

When a transmission request for the Tx buffer referenced by the get index is canceled, the get index is incremented to the next Tx buffer with a transmission request is pending and the Tx FIFO free level is recalculated. When transmission cancellation is applied to any other Tx buffer, the get index and the FIFO Free Level remain unchanged.

A Tx FIFO element allocates eighteen 32-bit words in the message RAM. The Therefore, the start address of the next available (free) Tx FIFO buffer, is calculated by adding 18 times the put index TFQPI[1:0] (0 … 2) to the Tx buffer start address TBSA.

*Digest note:* "18 times" counts 32-bit words: byte offset = 0x0278 + 72 × TFQPI (0x0278, 0x02C0, 0x0308).

#### Tx queue

Tx queue operation is configured by setting the TFQM of the FDCAN_TXBC register. Messages stored in the Tx queue are transmitted starting with the message with the lowest message ID (highest priority).

In case of mixing of standard and extended message IDs, the standard message IDs are compared to bits [28:18] of extended message IDs.

In case multiple queue buffers are configured with the same message ID, the queue buffer with the lowest buffer number is transmitted first.

New messages have to be written to the Tx buffer referenced by the put index (TFQPI[1:0] in FDCAN_TXFQS). An add request cyclically increments the put index to the next free Tx buffer. In case the Tx queue is full (TFQF = 1 in FDCAN_TXFQS), the put index is not valid and no further message must be written to the Tx queue until at least one of the requested messages has been sent out or a pending transmission request has been canceled.

The application can use the FDCAN_TXBRP register instead of the put index and can place messages to any Tx buffer without pending transmission request.

A Tx queue buffer allocates eighteen 32-bit words in the message RAM. The start address of Therefore, the next available (free) Tx queue buffer is calculated by adding 18 times the Tx queue put index TFQPI[1:0] (0 ... 2) to the Tx buffer start address TBSA.

#### Transmit cancellation

The FDCAN supports transmit cancellation. To cancel a requested transmission from a Tx queue buffer, the host has to write 1 to the corresponding bit position (= number of Tx buffer) of the FDCAN_TXBCR register. Transmit cancellation is not intended for Tx FIFO operation.

Successful cancellation is signaled by setting the corresponding bit of the FDCAN_TXBCF register.

In case a transmit cancellation is requested while a transmission from a Tx buffer is already ongoing, the corresponding FDCAN _TXBRP bit remains set as long as the transmission is in progress. If the transmission is successful, the corresponding FDCAN_TXBTO and FDCAN_TXBCF bits are set. If the transmission is not successful, it is not repeated and only the corresponding FDCAN_TXBCF bit is set.

*Note:* In case a pending transmission is canceled immediately before it has been started, there is a short time window where no transmission is started even if another message is pending in the node. This can enable another node to transmit a message that can have a priority lower than that of the second message in the node.

#### Tx event handling

To support Tx event handling the FDCAN has implemented a Tx event FIFO. After the FDCAN has transmitted a message on the CAN bus, message ID and timestamp are stored in a Tx event FIFO element. To link a Tx event to a Tx event FIFO element, the message marker from the transmitted Tx buffer is copied into the Tx event FIFO element.

The Tx event FIFO is configured to three elements. The Tx event FIFO element is described in Tx FIFO.

*Digest note:* the Tx event FIFO element is described in Section 46.4.10.

The purpose of the Tx event FIFO is to decouple handling transmit status information from transmit message handling that is, a Tx buffer holds only the message to be transmitted, while the transmit status is stored separately in the Tx event FIFO. This has the advantage, especially when operating a dynamically managed transmit queue, that a Tx buffer can be used for a new message immediately after successful transmission. There is no need to save transmit status information from a Tx buffer before overwriting that Tx buffer.

When a Tx event FIFO full condition is signaled by the TEFF bit of the FDCAN_IR, no further elements are written to the Tx event FIFO until at least one element has been read out and the Tx event FIFO get index has been incremented. In case a Tx event occurs while the Tx event FIFO is full, this event is discarded and the TEFL interrupt flag is set in the FDCAN_IR register.

When reading from the Tx event FIFO, the Tx event FIFO get index (EFGI[1:0] of FDCAN_TXEFS) has to be added twice to the Tx event FIFO start address EFSA.

*Digest note:* "added twice" = 2 words per element: byte offset = 0x0260 + 8 × EFGI.

### 46.4.7 FIFO acknowledge handling

The get indices of Rx FIFO 0, Rx FIFO 1, and the Tx event FIFO are controlled by writing to the corresponding FIFO acknowledge index (see Section 46.5.23 and Section 46.5.25). Writing to the FIFO acknowledge index sets the FIFO get index to the FIFO acknowledge index plus one and thereby updates the FIFO fill level. There are two use cases:

- When only a single element has been read from the FIFO (the one being pointed to by the get index), this get index value is written to the FIFO acknowledge index.
- When a sequence of elements has been read from the FIFO, it is sufficient to write the FIFO acknowledge index only once at the end of that read sequence (value = index of the last element read), to update the FIFO get index.

Because the CPU has free access to the FDCAN message RAM, special care has to be taken when reading FIFO elements in an arbitrary order (get index not considered). This might be useful when reading a high priority message from one of the two Rx FIFOs. In this case, the FIFO acknowledge index must not be written because this would set the get index to a wrong position and alter the FIFO fill level. In this case, some of the older FIFO elements would be lost.

*Note:* The application has to ensure that a valid value is written to the FIFO acknowledge index. The FDCAN does not check for erroneous values.

### 46.4.8 FDCAN Rx FIFO element

Two Rx FIFOs are configured in the message RAM. Each Rx FIFO section can be configured to store up to three received messages. The structure of an Rx FIFO element is described in Table 475. The description is provided in Table 476.

**Table 475. Rx FIFO element**

| Word | Bits 31:24 | Bits 23:16 | Bits 15:8 | Bits 7:0 |
|---|---|---|---|---|
| R0 | ESI (31), XTD (30), RTR (29), ID[28:24] | ID[23:16] | ID[15:8] | ID[7:0] |
| R1 | ANMF (31), FIDX[6:0] (30:24) | Res. (23:22), FDF (21), BRS (20), DLC[3:0] (19:16) | RXTS[15:8] | RXTS[7:0] |
| R2 | DB3[7:0] | DB2[7:0] | DB1[7:0] | D[7:0] |
| R3 | DB7[7:0] | DB6[7:0] | DB5[7:0] | DB4[7:0] |
| ... | ... | ... | ... | ... |
| Rn | DBm[7:0] | DBm-1[7:0] | DBm-2[7:0] | DBm-3[7:0] |

*Digest note:* ID[28:0] occupies R0 bits 28:0 and RXTS[15:0] occupies R1 bits 15:0; they are split across the byte columns above only for layout. "D[7:0]" in R2 is data byte 0 (DB0). Data bytes are little-endian within each word: byte k of the payload is at byte offset 8 + k from the element start.

The element size configured for storage of CAN FD messages is set to 64-byte data field.

**Table 476. Rx FIFO element description**

| Field | Description |
|---|---|
| R0 Bit 31 ESI | Error state indicator. – 0: Transmitting node is error active. – 1: Transmitting node is error passive |
| R0 Bit 30 XTD | Extended identifier. Signals to the host whether the received frame has a standard or extended identifier. – 0: 11-bit standard identifier. – 1: 29-bit extended identifier |
| R0 Bit 29 RTR | Remote transmission request. Signals to the host whether the received frame is a data frame or a remote frame. – 0: Received frame is a data frame. – 1: Received frame is a remote frame |
| R0 Bits 28:0 ID[28:0] | Identifier. Standard or extended identifier depending on bit XTD. A standard identifier is stored into ID[28:18]. |
| R1 Bit 31 ANMF | Accepted non-matching frame. Acceptance of non-matching frames can be enabled via ANFS[1:0] and ANFE[1:0] bitfield of FDCAN_RXGFC. – 0: Received frame matching filter index FIDX. – 1: Received frame did not match any Rx filter element |
| R1 Bits 30:24 FIDX[6:0] | Filter index. 0-27=Index of matching Rx acceptance filter element (invalid if ANMF = 1). Range: 0 to LSS[4:0] - 1 or LSE[3:0] - 1 in FDCAN_RXGFC. |
| R1 Bit 21 FDF | FD format. – 0: Standard frame format. – 1: FDCAN frame format (new DLC-coding and CRC) |
| R1 Bit 20 BRS | Bit rate switch. – 0: Frame received without bit rate switching. – 1: Frame received with bit rate switching |
| R1 Bits 19:16 DLC[3:0] | Data length code. – 0-8: Classic CAN + CAN FD: received frame has 0-8 data bytes. – 9-15: Classic CAN: received frame has 8 data bytes. – 9-15: CAN FD: received frame has 12/16/20/24/32/48/64 data bytes |
| R1 Bits 15:0 RXTS[15:0] | Rx timestamp. Timestamp Counter value captured on start of frame reception. Resolution depending on configuration of the timestamp counter prescaler TCP[3:0] of FDCAN_TSCC. |
| R2 Bits 31:24 DB3[7:0] | Data byte 3 |
| R2 Bits 23:16 DB2[7:0] | Data byte 2 |
| R2 Bits 15:8 DB1[7:0] | Data byte 1 |
| R2 Bits 7:0 D[7:0] | Data byte 0 |
| R3 Bits 31:24 DB7[7:0] | Data byte 7 |
| R3 Bits 23:16 DB6[7:0] | Data byte 6 |
| R3 Bits 15:8 DB5[7:0] | Data byte 5 |
| R3 Bits 7:0 DB4[7:0] | Data byte 4 |
| ... | ... |
| Rn Bits 31:24 DBm[7:0] | Data byte m |
| Rn Bits 23:16 DBm-1[7:0] | Data byte m-1 |
| Rn Bits 15:8 DBm-2[7:0] | Data byte m-2 |
| Rn Bits 7:0 DBm-3[7:0] | Data byte m-3 |

*Digest note:* R1 bits 23:22 are reserved (Table 475). For a 64-byte data field the element is R0..R17 (18 words).

### 46.4.9 FDCAN Tx buffer element

The Tx buffers section (three elements) can be configured to hold Tx FIFO or Tx queue. The Tx handler distinguishes between Tx FIFO and Tx queue using the Tx buffer configuration TFQM bit of the FDCAN_TXBC register. The element size is configured for storage of CAN FD messages with up to 64-byte data.

**Table 477. Tx buffer and FIFO element**

| Word | Bits 31:24 | Bits 23:16 | Bits 15:8 | Bits 7:0 |
|---|---|---|---|---|
| T0 | ESI (31), XTD (30), RTR (29), ID[28:24] | ID[23:16] | ID[15:8] | ID[7:0] |
| T1 | MM[7:0] | EFC (23), Res. (22), FDF (21), BRS (20), DLC[3:0] (19:16) | Res. | Res. |
| T2 | DB3[7:0] | DB2[7:0] | DB1[7:0] | D[7:0] |
| T3 | DB7[7:0] | DB6[7:0] | DB5[7:0] | DB4[7:0] |
| ... | ... | ... | ... | ... |
| Tn | DBm[7:0] | DBm-1[7:0] | DBm-2[7:0] | DBm-3[7:0] |

*Digest note:* ID[28:0] occupies T0 bits 28:0; T1 bits 15:0 are reserved.

**Table 478. Tx buffer element description**

| Field | Description |
|---|---|
| T0 Bit 31 ESI (1) | Error state indicator. – 0: ESI bit in CAN FD format depends only on error passive flag. – 1: ESI bit in CAN FD format transmitted recessive |
| T0 Bit 30 XTD | Extended identifier. – 0: 11-bit standard identifier. – 1: 29-bit extended identifier |
| T0 Bit 29 RTR (2) | Remote transmission request. – 0: Transmit data frame. – 1: Transmit remote frame |
| T0 Bits 28:0 ID[28:0] | Identifier. Standard or extended identifier depending on bit XTD. A standard identifier has to be written to ID[28:18]. |
| T1 Bits 31:24 MM[7:0] | Message marker. Written by CPU during Tx buffer configuration. Copied into Tx event FIFO element for identification of Tx message status. |
| T1 Bit 23 EFC | Event FIFO control. – 0: Do not store Tx events. – 1: Store Tx events |
| T1 Bit 21 FDF | FD format. – 0: Frame transmitted in classic CAN format. – 1: Frame transmitted in CAN FD format |
| T1 Bit 20 BRS (3) | Bit rate switching. – 0: CAN FD frames transmitted without bit rate switching. – 1: CAN FD frames transmitted with bit rate switching |
| T1 Bits 19:16 DLC[3:0] | Data length code. – 0 - 8: Classic CAN + CAN FD: received frame has 0-8 data bytes. – 9 - 15: Classic CAN: received frame has 8 data bytes. – 9 - 15: CAN FD: received frame has 12/16/20/24/32/48/64 data bytes |
| T2 Bits 31:24 DB3[7:0] | Data byte 3 |
| T2 Bits 23:16 DB2[7:0] | Data byte 2 |
| T2 Bits 15:8 DB1[7:0] | Data byte 1 |
| T2 Bits 7:0 D[7:0] | Data byte 0 |
| T3 Bits 31:24 DB7[7:0] | Data byte 7 |
| T3 Bits 23:16 DB6[7:0] | Data byte 6 |
| T3 Bits 15:8 DB5[7:0] | Data byte 5 |
| T3 Bits 7:0 DB4[7:0] | Data byte 4 |
| ... | ... |
| Tn Bits 31:24 DBm[7:0] | Data byte m |
| Tn Bits 23:16 DBm-1[7:0] | Data byte m-1 |
| Tn Bits 15:8 DBm-2[7:0] | Data byte m-2 |
| Tn Bits 7:0 DBm-3[7:0] | Data byte m-3 |

Notes:

1. The ESI bit of the transmit buffer is OR-ed with the error passive flag to decide the value of the ESI bit in the transmitted FD frame. As required by the CAN FD protocol specification, an error active node can optionally transmit the ESI bit recessive, but an error passive node always transmits the ESI bit recessive.
2. When RTR = 1, the FDCAN transmits a remote frame according to ISO11898-1, even if the transmission in CAN FD format is enabled by the FDOE bit of the FDCAN_CCCR.
3. Bits ESI, FDF, and BRS are only evaluated when CAN FD operation is enabled by setting the FDOE bit of the FDCAN_CCCR. Bit BRS is only evaluated when in addition BRSE bit is set in FDCAN_CCCR.

*Digest note:* the DLC description in Table 478 says "received frame" although this is the transmit element; it gives the number of data bytes transmitted.

### 46.4.10 FDCAN Tx event FIFO element

Each element stores information about transmitted messages. By reading the Tx event, FIFO the host CPU gets this information in the order that the messages were transmitted. Status information about the Tx event FIFO can be obtained from FDCAN_TXEFS register.

**Table 479. Tx event FIFO element**

| Word | Bits 31:24 | Bits 23:16 | Bits 15:8 | Bits 7:0 |
|---|---|---|---|---|
| E0 | ESI (31), XTD (30), RTR (29), ID[28:24] | ID[23:16] | ID[15:8] | ID[7:0] |
| E1 | MM[7:0] | ET[1:0] (23:22), EDL (21), BRS (20), DLC[3:0] (19:16) | TXTS[15:8] | TXTS[7:0] |

**Table 480. Tx event FIFO element description**

| Field | Description |
|---|---|
| E0 Bit 31 ESI | Error state indicator. – 0: Transmitting node is error active. – 1: Transmitting node is error passive |
| E0 Bit 30 XTD | Extended identifier. – 0: 11-bit standard identifier. – 1: 29-bit extended identifier |
| E0 Bit 29 RTR | Remote transmission request. – 0: Transmit data frame. – 1: Transmit remote frame |
| E0 Bits 28:0 ID[28:0] | Identifier. Standard or extended identifier depending on bit XTD. A standard identifier has to be written to ID[28:18]. |
| E1 Bits 31:24 MM[7:0] | Message marker. Copied from Tx buffer into Tx event FIFO element for identification of Tx message status. |
| E1 Bits 23:22 EFC | Event type. – 00: Reserved. – 01: Tx event. – 10: Transmission in spite of cancellation (always set for transmissions in DAR mode). – 11: Reserved |
| E1 Bit 21 EDL | Extended data length. – 0: Standard frame format. – 1: FDCAN frame format (new DLC-coding and CRC) |
| E1 Bit 20 BRS | Bit rate switching. – 0: Frame transmitted without bit rate switching. – 1: Frame transmitted with bit rate switching |
| T1 Bits 19:16 DLC[3:0] | Data length code. 0 - 8: Frame with 0-8 data bytes transmitted. 9 - 15: Frame with 8 data bytes transmitted |
| E1 Bits 15:0 TXTS[15:0] | Tx Timestamp. Timestamp counter value captured on start of frame transmission. Resolution depending on configuration of the timestamp counter prescaler TCP[3:0] of FDCAN_TSCC. |

*Digest note:* Table 480 labels E1 bits 23:22 "EFC" and the DLC row "T1"; per Table 479 these are the event type ET[1:0] and E1 bits 19:16.

### 46.4.11 FDCAN standard message ID filter element

Up to 28 filter elements can be configured for 11-bit standard IDs. When accessing a standard message ID filter element, its address is the filter list standard start address FLSSA plus the index of the filter element (0 … 27).

**Table 481. Standard message ID filter element**

| Word | Bits 31:30 | Bits 29:27 | Bits 26:16 | Bits 15:11 | Bits 10:0 |
|---|---|---|---|---|---|
| S0 | SFT[1:0] | SFEC[2:0] | SFID1[10:0] | Res. | SFID2[10:0] |

**Table 482. Standard message ID filter element field description**

| Field | Description |
|---|---|
| Bit 31:30 SFT[1:0] (1) | Standard filter type. – 00: Range filter from SFID1 to SFID2. – 01: Dual ID filter for SFID1 or SFID2. – 10: Classic filter: SFID1 = filter, SFID2 = mask. – 11: Filter element disabled |
| Bit 29:27 SFEC[2:0] | Standard filter element configuration. All enabled filter elements are used for acceptance filtering of standard frames. Acceptance filtering stops at the first matching enabled filter element or when the end of the filter list is reached. If SFEC[2:0] = 100, 101 or 110 a match sets interrupt flag IR.HPM and, if enabled, an interrupt is generated. In this case register HPMS is updated with the status of the priority match. – 000: Disable filter element. – 001: Store in Rx FIFO 0 if filter matches. – 010: Store in Rx FIFO 1 if filter matches. – 011: Reject ID if filter matches. – 100: Set priority if filter matches. – 101: Set priority and store in FIFO 0 if filter matches. – 110: Set priority and store in FIFO 1 if filter matches. – 111: Not used |
| Bits 26:16 SFID1[10:0] | Standard filter ID 1. First ID of standard ID filter element. |
| Bits 10:0 SFID2[10:0] | Standard filter ID 2. Second ID of standard ID filter element. |

Notes:

1. With SFT[1:0] = 11 the filter element is disabled and the acceptance filtering continues (same behavior as with SFEC[2:0] = 000).

*Note:* In case a reserved value is configured, the filter element is considered disabled.

### 46.4.12 FDCAN extended message ID filter element

Up to eight filter elements can be configured for 29-bit extended IDs. When accessing an extended message ID filter element, its address is the filter list extended start address FLESA plus twice the index of the filter element (0 … 7).

**Table 483. Extended message ID filter element**

| Word | Bits 31:29 | Bits 28:0 |
|---|---|---|
| F0 | EFEC[2:0] (31:29) | EFID1[28:0] |
| F1 | EFT[1:0] (31:30), Res. (29) | EFID2[28:0] |

**Table 484. Extended message ID filter element field description**

| Field | Description |
|---|---|
| F0 Bits 31:29 EFEC[2:0] | Extended filter element configuration. All enabled filter elements are used for acceptance filtering of extended frames. Acceptance filtering stops at the first matching enabled filter element or when the end of the filter list is reached. If EFEC[2:0] = 100, 101 or 110 a match sets interrupt flag IR[HPM] and, if enabled, an interrupt is generated. In this case register HPMS is updated with the status of the priority match. – 000: Disable filter element. – 001: Store in Rx FIFO 0 if filter matches. – 010: Store in Rx FIFO 1 if filter matches. – 011: Reject ID if filter matches. – 100: Set priority if filter matches. – 101: Set priority and store in FIFO 0 if filter matches. – 110: Set priority and store in FIFO 1 if filter matches. – 111: Not used |
| F0 Bits 28:0 EFID1[28:0] | Extended filter ID 1. First ID of extended ID filter element. When filtering for Rx FIFO, this field defines the ID of an extended message to be stored. The received identifiers must match exactly, only XIDAM masking mechanism. |
| F1 Bits 31:30 EFT[1:0] | Extended filter type. – 00: Range filter from EF1ID to EF2ID (EF2ID ≥ EF1ID). – 01: Dual ID filter for EF1ID or EF2ID. – 10: Classic filter: EF1ID = filter, EF2ID = mask. – 11: Range filter from EF1ID to EF2ID (EF2ID ≥ EF1ID), XIDAM mask not applied |
| F1 Bit 29 | Not used |
| F1 Bits 28:0 EFID2[28:0] | Extended filter ID 2. Second ID of extended ID filter element. |

## 46.5 FDCAN registers

*Digest note:* register offsets are relative to the FDCAN1 base address (0x4000 A400 on STM32C552). Access-type codes as used in the RM: r = read-only, rw = read/write, rc_r = cleared on read, rs = set on read, rc_w = cleared (reset) by write, rc_w1 = cleared by writing 1. "(P)" marks write-protected fields that can be written only while CCE and INIT in FDCAN_CCCR are both set.

### 46.5.1 FDCAN core release register (FDCAN_CREL)

Address offset: 0x0000. Reset value: 0x3214 1218. All bits read-only.

- **Bits 31:28 REL[3:0]** (r): 3
- **Bits 27:24 STEP[3:0]** (r): 2
- **Bits 23:20 SUBSTEP[3:0]** (r): 1
- **Bits 19:16 YEAR[3:0]** (r): 4
- **Bits 15:8 MON[7:0]** (r): 12
- **Bits 7:0 DAY[7:0]** (r): 18

*Digest note:* the values above are those printed in the bit descriptions and are consistent with the 0x3214 1218 reset value. The reset-value row for FDCAN_CREL in Table 485 reads differently (see Section 46.5.38).

### 46.5.2 FDCAN endian register (FDCAN_ENDN)

Address offset: 0x0004. Reset value: 0x8765 4321. All bits read-only.

- **Bits 31:0 ETV[31:0]** (r): Endianness test value
  The endianness test value is 0x8765 4321.

*Note:* The register read must give the reset value to ensure no endianness issue.

### 46.5.3 FDCAN data bit timing and prescaler register (FDCAN_DBTP)

Address offset: 0x000C. Reset value: 0x0000 0A33.

This register is only writable if the CCE and INIT bits of the FDCAN_CCCR are set. The CAN time quantum can be programmed in the range of 1 to 32 FDCAN clock periods: tq = (DBRP[4:0] + 1) FDCAN clock periods.

DTSEG1[4:0] is the sum of PROP_SEG and PHASE_SEG1. DTSEG2[3:0] is PHASE_SEG2. Therefore, the length of the bit time is (programmed values) × [DTSEG1[4:0] + DTSEG2[3:0] + 3] × tq or (functional values) × [SYNC_SEG + PROP_SEG + PHASE_SEG1 + PHASE_SEG2] × tq.

The information processing time (IPT) is 0, meaning the data for the next bit is available at the first clock edge after the sample point.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bit 23 TDC** (rw): Transceiver delay compensation
  - 0: Transceiver delay compensation disabled
  - 1: Transceiver delay compensation enabled
- **Bits 22:21** Reserved, must be kept at reset value.
- **Bits 20:16 DBRP[4:0]** (rw): Data bit rate prescaler
  The value by which the oscillator frequency is divided to generate the bit time quanta. The bit time is built up from a multiple of this quantum. Valid values for the baud rate prescaler are 0 to 31. The hardware interpreters this value as the value programmed plus 1.
- **Bits 15:13** Reserved, must be kept at reset value.
- **Bits 12:8 DTSEG1[4:0]** (rw): Data time segment before sample point
  Valid values are 0 to 31. The value used by the hardware is the one programmed, incremented by 1, that is tBS1 = (DTSEG1[4:0] + 1) × tq.
- **Bits 7:4 DTSEG2[3:0]** (rw): Data time segment after sample point
  Valid values are 0 to 15. The value used by the hardware is the one programmed, incremented by 1, i.e. tBS2 = (DTSEG2[3:0] + 1) × tq.
- **Bits 3:0 DSJW[3:0]** (rw): Synchronization jump width
  Valid values are 0 to 15. The value used by the hardware is the one programmed, incremented by 1: tSJW = (DSJW[3:0] + 1) × tq.

*Note:* With an FDCAN clock of 8 MHz, the reset value 0x0000 0A33 configures the FDCAN for a fast bit rate of 500 kbit/s. The data phase bit rate must be higher than or equal to the nominal bit rate.

*Digest note:* reset decode: DBRP = 0 (tq = 1 clock), DTSEG1 = 0xA (11 tq), DTSEG2 = 3 (4 tq), DSJW = 3 (4 tq): 1 + 11 + 4 = 16 tq per bit, 8 MHz / 16 = 500 kbit/s. For classic CAN only (FDOE = 0) DBTP is not used for transmission, but the rule "data bit rate ≥ nominal bit rate" still describes a valid configuration; leaving DBTP at reset is the usual choice.

### 46.5.4 FDCAN test register (FDCAN_TEST)

Write access to this register is enabled by setting the TEST bit of the FDCAN_CCCR register. All register functions are set to their reset values when this bit is cleared.

Loop-back mode and software control of Tx pin FDCANx_TX are hardware test modes. Programming TX[1:0] differently from 00 can disturb the message transfer on the CAN bus.

Address offset: 0x0010. Reset value: 0x0000 0000.

- **Bits 31:8** Reserved, must be kept at reset value.
- **Bit 7 RX** (r): Receive pin
  This bit is used to monitor the actual value of FDCANx_RX. It is synchronized with the FDCANx_RX pin, so it is set after reset if the FDCAN is connected to a network.
  - 0: The CAN bus is dominant (FDCANx_RX = 0)
  - 1: The CAN bus is recessive (FDCANx_RX = 1)
- **Bits 6:5 TX[1:0]** (rw): Control of transmit pin
  - 00: Reset value, FDCANx_TX TX is controlled by the CAN core, updated at the end of the CAN bit time
  - 01: Sample point can be monitored at pin FDCANx_TX
  - 10: Dominant (0) level at pin FDCANx_TX
  - 11: Recessive (1) at pin FDCANx_TX
- **Bit 4 LBCK** (rw): Loop-back mode
  - 0: Reset value, loop-back mode is disabled
  - 1: Loop-back mode is enabled (see Power-down (Sleep mode))
- **Bits 3:0** Reserved, must be kept at reset value.

*Digest note:* the cross-reference in LBCK should point to the external/internal loop-back mode descriptions in Section 46.4.4.

### 46.5.5 FDCAN RAM watchdog register (FDCAN_RWD)

The RAM watchdog monitors the READY output of the message RAM. A message RAM access starts the message RAM watchdog counter with the value configured through the WDC[7:0] bitfield of the FDCAN_RWD register.

The counter is reloaded with WDC[7:0] when the message RAM signals successful completion by activating its READY output. In case there is no response from the message RAM until the counter has counted down to 0, the counter stops, and the interrupt flag WDI is set in the FDCAN_IR register. The RAM watchdog counter is clocked by the fdcan_pclk clock.

Address offset: 0x0014. Reset value: 0x0000 0000.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bits 15:8 WDV[7:0]** (r): Watchdog value
  Actual message RAM watchdog counter value.
- **Bits 7:0 WDC[7:0]** (rw): Watchdog configuration
  Start value of the message RAM watchdog counter. With the reset value of 00, the counter is disabled.
  This bitfield is write-protected (P): write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.

### 46.5.6 FDCAN CC control register (FDCAN_CCCR)

Address offset: 0x0018. Reset value: 0x0000 0001.

For details about setting and clearing single bits, see Software initialization.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bit 15 NISO** (rw): Non-ISO operation
  If this bit is set, the FDCAN uses the CAN FD frame format as specified by the Bosch CAN FD Specification V1.0.
  - 0: CAN FD frame format according to ISO11898-1
  - 1: CAN FD frame format according to Bosch CAN FD Specification V1.0
- **Bit 14 TXP** (rw): Transmit pause enable
  If this bit is set, the FDCAN pauses for two CAN bit times before starting the next transmission after successfully transmitting a frame.
  - 0: Disabled
  - 1: Enabled
- **Bit 13 EFBI** (rw): Edge filtering during bus integration
  - 0: Edge filtering disabled
  - 1: Two consecutive dominant tq required to detect an edge for hard synchronization
- **Bit 12 PXHD** (rw): Protocol exception handling disable
  - 0: Protocol exception handling enabled
  - 1: Protocol exception handling disabled
- **Bits 11:10** Reserved, must be kept at reset value.
- **Bit 9 BRSE** (rw): FDCAN bit rate switching
  - 0: Bit rate switching for transmissions disabled
  - 1: Bit rate switching for transmissions enabled
- **Bit 8 FDOE** (rw): FD operation enable
  - 0: FD operation disabled
  - 1: FD operation enabled
- **Bit 7 TEST** (rw): Test mode enable
  - 0: Normal operation, FDCAN_TEST holds reset values
  - 1: Test mode, write access to FDCAN_TEST enabled
- **Bit 6 DAR** (rw): Disable automatic retransmission
  - 0: Automatic retransmission of messages not transmitted successfully enabled
  - 1: Automatic retransmission disabled
- **Bit 5 MON** (rw): Bus monitoring mode
  This bit can only be set by software when both CCE and INIT are set. The bit can be cleared by the host at any time.
  - 0: Bus monitoring mode disabled
  - 1: Bus monitoring mode enabled
- **Bit 4 CSR** (rw): Clock stop request
  - 0: No clock stop requested
  - 1: Clock stop requested. When clock stop is requested, first INIT and then CSA is set after all pending transfer requests have been completed and the CAN bus is idle.
- **Bit 3 CSA** (r): Clock stop acknowledge
  - 0: No clock stop acknowledged
  - 1: FDCAN can be set in power-down by stopping APB clock and kernel clock.
- **Bit 2 ASM** (rw): ASM restricted operation mode
  The restricted operation mode is intended for applications that adapt themselves to different CAN bit rates. The application tests different bit rates and leaves the restricted operation mode after it has received a valid frame. In the optional restricted operation mode the node is able to transmit and receive data and remote frames and it gives acknowledge to valid frames, but it does not send active error frames or over.load frames. In case of an error condition or overload condition, it does not send dominant bits, instead it waits for the occurrence of bus-idle condition to resynchronize itself to the CAN communication. The error counters are not incremented. Bit ASM can only be set by software when both CCE and INIT are set. The bit can be cleared by the software at any time.
  - 0: Normal CAN operation
  - 1: Restricted operation mode active
- **Bit 1 CCE** (rw): Configuration change enable
  - 0: The CPU has no write access to the protected configuration registers.
  - 1: The CPU has write access to the protected configuration registers (while INIT set in FDCAN_CCCR).
- **Bit 0 INIT** (rw): Initialization
  - 0: Normal operation
  - 1: Initialization started

*Note:* Due to the synchronization mechanism between the two clock domains, there can be a delay until the value written to INIT can be read back. Therefore, the programmer has to assure that the previous value written to INIT has been accepted by reading INIT before setting INIT to a new value.

*Digest note:* INIT resets to 1, so after reset the FDCAN is already in initialization; CCE must still be set (while INIT reads 1) before writing protected registers. The ASM description here says the node "is able to transmit" data and remote frames, while Section 46.4.4 (Restricted operation mode) says it "does not send data frames, remote frames"; both texts are as printed.

### 46.5.7 FDCAN nominal bit timing and prescaler register (FDCAN_NBTP)

Address offset: 0x001C. Reset value: 0x0600 0A03.

This register is only writable if the CCE and INIT bits of the FDCAN_CCCR register are both set. The CAN bit time can be programed in the range of 4 to 81 × tq. The CAN time quantum can be programmed in the range of 1 to 1024 FDCAN kernel clock periods: tq = (BRP + 1) × FDCAN clock period fdcan_ker_ck.

NTSEG1[7:0] is the sum of PROP_SEG and PHASE_SEG1. NTSEG2[6:0] is PHASE_SEG2. Therefore, the length of the bit time is (programmed values) × [NTSEG1[7:0] + NTSEG2[6:0] + 3] × tq or (functional values) × [SYNC_SEG + PROP_SEG + PHASE_SEG1 + PHASE_SEG2] × tq.

The information processing time (IPT) is 0, meaning the data for the next bit is available at the first clock edge after the sample point.

- **Bits 31:25 NSJW[6:0]** (rw): Nominal (re)synchronization jump width
  Valid values are 0 to 127. The actual interpretation by the hardware of this value is such that the used value is the one programmed incremented by one.
  This bitfield is write-protected (P): write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bits 24:16 NBRP[8:0]** (rw): Bit rate prescaler
  Value by which the oscillator frequency is divided for generating the bit time quanta. The bit time is built up from a multiple of this quantum. Valid values are 0 to 511. The actual interpretation by the hardware of this value is such that one more than the value programmed here is used.
  This bitfield is write-protected (P): write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bits 15:8 NTSEG1[7:0]** (rw): Nominal time segment before sample point
  Valid values are 0 to 255. The actual interpretation by the hardware of this value is such that one more than the programmed value is used.
  This bitfield is write-protected write (P): write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bit 7** Reserved, must be kept at reset value.
- **Bits 6:0 NTSEG2[6:0]** (rw): Nominal time segment after sample point
  Valid values are 0 to 127. The actual interpretation by the hardware of this value is such that one more than the programmed value is used.

*Note:* With a CAN kernel clock of 8 MHz, the reset value 0x0600 0A03 configures the FDCAN for a bit rate of 500 kBit/s.

*Digest note:* reset decode: NSJW = 3 (4 tq), NBRP = 0 (tq = 1 clock), NTSEG1 = 0x0A (11 tq), NTSEG2 = 3 (4 tq): 1 + 11 + 4 = 16 tq, 8 MHz / 16 = 500 kbit/s. The ranges in the introductory text do not follow from the field widths: bit time = 1 + (NTSEG1 + 1) + (NTSEG2 + 1) = NTSEG1 + NTSEG2 + 3 tq, i.e. up to 385 tq, and the prescaler NBRP + 1 spans 1 to 512 (not 1 to 1024). [unclear in source: the "4 to 81 × tq" and "1 to 1024" ranges.] The "FDCAN clock" is fdcan_tq_ck, i.e. fdcan_ker_ck after FDCAN_CKDIV (Figure 693). The CMSIS header agrees with the field positions above (NSJW 0xFE00 0000, NBRP 0x01FF 0000, NTSEG1 0x0000 FF00, NTSEG2 0x0000 007F).

### 46.5.8 FDCAN timestamp counter configuration register (FDCAN_TSCC)

Address offset: 0x0020. Reset value: 0x0000 0000.

- **Bits 31:20** Reserved, must be kept at reset value.
- **Bits 19:16 TCP[3:0]** (rw): Timestamp counter prescaler
  Configures the timestamp and timeout counters time unit in multiples of CAN bit times [1…16].
  The actual interpretation by the hardware of this value is such that one more than the value programmed here is used.
  In CAN FD mode, the internal timestamp counter TCP does not provide a constant time base due to the different CAN bit times between arbitration phase and data phase. Thus CAN FD requires an external counter for timestamp generation (TSS[1:0] = 10).
  This bitfield is write-protected (P): write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bits 15:2** Reserved, must be kept at reset value.
- **Bits 1:0 TSS[1:0]** (rw): Timestamp select
  - 00: Timestamp counter value always 0x0000
  - 01: Timestamp counter value incremented according to TCP
  - 10: External timestamp counter from TIM2 value (tim2_cnt[0:15]) or from TIM3 value (tim3_cnt[0:15])
  - 11: Same as 00.

  These bits are write-protected write (P): write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.

*Digest note:* TIM3 is not present on STM32C551/C552 (RM0522 Table 3); there only the TIM2 source can apply. [unclear in source: how the TIM2 vs TIM3 source is selected for TSS = 10.]

### 46.5.9 FDCAN timestamp counter value register (FDCAN_TSCV)

Address offset: 0x0024. Reset value: 0x0000 0000.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bits 15:0 TSC[15:0]** (rc_w): Timestamp counter
  The internal/external timestamp counter value is captured on start of frame (both Rx and Tx). When TSS[1:0] = 01 in FDCAN_TSCC, the timestamp counter is incremented in multiples of CAN bit times [1 … 16] depending on the configuration of TCP[3:0] in FDCAN_TSCC. A wrap around sets the TSW interrupt flag in FDCAN_IR. Write access resets the counter to 0.
  When TSS[1:0] = 10, TSC[15:0] reflects the external timestamp counter value. A write access has no impact.

*Note:* A "wrap around" is a change of the timestamp counter value from non-0 to 0 that is not caused by write access to FDCAN_TSCV.

### 46.5.10 FDCAN timeout counter configuration register (FDCAN_TOCC)

Address offset: 0x0028. Reset value: 0xFFFF 0000.

- **Bits 31:16 TOP[15:0]** (rw): Timeout period
  Start value of the timeout counter (down-counter). Configures the timeout period.
  This bitfield is write-protected (P), write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bits 15:3** Reserved, must be kept at reset value.
- **Bits 2:1 TOS[1:0]** (rw): Timeout select
  When operating in continuous mode, a write to FDCAN_TOCV presets the counter to the value configured by TOP[15:0] in FDCAN_TOCC and continues down-counting. When the timeout counter is controlled by one of the FIFOs, an empty FIFO presets the counter to the value configured by TOP[15:0]. Down-counting is started when the first FIFO element is stored.
  - 00: Continuous operation
  - 01: Timeout controlled by Tx event FIFO
  - 10: Timeout controlled by Rx FIFO 0
  - 11: Timeout controlled by Rx FIFO 1

  This bitfield is write-protected (P), write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bit 0 ETOC** (rw): Timeout counter enable
  - 0: Timeout counter disabled
  - 1: Timeout counter enabled

  This bit is write-protected (P), write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.

For more details, see Timeout counter.

### 46.5.11 FDCAN timeout counter value register (FDCAN_TOCV)

Address offset: 0x002C. Reset value: 0x0000 FFFF.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bits 15:0 TOC[15:0]** (rc_w): Timeout counter
  The timeout counter is decremented in multiples of CAN bit times [1 … 16] depending on the configuration of the TCP[3:0] bitfield of the FDCAN_TSCC register. When decremented to 0, the TOO interrupt flag is set in FDCAN_IR and the timeout counter is stopped. Start and reset/restart conditions are configured via TOS[1:0] in FDCAN_TOCC.

### 46.5.12 FDCAN error counter register (FDCAN_ECR)

Address offset: 0x0040. Reset value: 0x0000 0000.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bits 23:16 CEL[7:0]** (rc_r): CAN error logging
  The counter is incremented each time when a CAN protocol error causes the transmit error counter or the receive error counter to be incremented. It is reset by read access to CEL[7:0]. The counter stops at 0xFF; the next increment of TEC[7:0] or REC[6:0] sets the ELO interrupt flag in FDCAN_IR.
  Access type is rc_r: cleared on read.
- **Bit 15 RP** (r): Receive error passive
  - 0: The receive error counter is below the error passive level of 128.
  - 1: The receive error counter has reached the error passive level of 128.
- **Bits 14:8 REC[6:0]** (r): Receive error counter
  Actual state of the receive error counter, values between 0 and 127.
- **Bits 7:0 TEC[7:0]** (r): Transmit error counter
  Actual state of the transmit error counter, values between 0 and 255.
  When the ASM bit of the FDCAN_CCCR is set, the CAN protocol controller does not increment TEC and REC when a CAN protocol error is detected, but CEL[7:0] is still incremented.

### 46.5.13 FDCAN protocol status register (FDCAN_PSR)

Address offset: 0x0044. Reset value: 0x0000 0707.

- **Bits 31:23** Reserved, must be kept at reset value.
- **Bits 22:16 TDCV[6:0]** (r): Transmitter delay compensation value
  Position of the secondary sample point, defined by the sum of the measured delay from FDCAN_TX to FDCAN_RX and TDCO[6:0] in FDCAN_TDCR. The SSP position is, in the data phase, the number of minimum time quanta (mtq) between the start of the transmitted bit and the secondary sample point. Valid values are 0 to 127 × mtq.
- **Bit 15** Reserved, must be kept at reset value.
- **Bit 14 PXE** (rc_r): Protocol exception event
  - 0: No protocol exception event occurred since last read access
  - 1: Protocol exception event occurred
- **Bit 13 REDL** (rc_r): Received FDCAN message
  This bit is set independent of acceptance filtering.
  - 0: Since this bit was cleared by the CPU, no FDCAN message has been received.
  - 1: Message in FDCAN format with EDL flag set has been received.

  Access type is rc_r: cleared on read.
- **Bit 12 RBRS** (rc_r): BRS flag of last received FDCAN message
  This bit is set together with REDL, independent of acceptance filtering.
  - 0: Last received FDCAN message did not have its BRS flag set.
  - 1: Last received FDCAN message had its BRS flag set.

  Access type is rc_r: cleared on read.
- **Bit 11 RESI** (rc_r): ESI flag of last received FDCAN message
  This bit is set together with REDL, independent of acceptance filtering.
  - 0: Last received FDCAN message did not have its ESI flag set.
  - 1: Last received FDCAN message had its ESI flag set.

  Access type is rc_r: cleared on read.
- **Bits 10:8 DLEC[2:0]** (rs): Data last error code
  Type of last error that occurred in the data phase of a FDCAN format frame with its BRS flag set. Coding is the same as for LEC[2:0]. This field is cleared when a FDCAN format frame with its BRS flag set has been transferred (reception or transmission) without error.
  Access type is rs: set on read.
- **Bit 7 BO** (r): Bus-off status
  - 0: The FDCAN is not in bus-off state.
  - 1: The FDCAN is in bus-off state.
- **Bit 6 EW** (r): Warning status
  - 0: Both error counters are below the error-warning limit of 96.
  - 1: At least one of error counter has reached the error-warning limit of 96.
- **Bit 5 EP** (r): Error passive
  - 0: The FDCAN is in the error-active state. It normally takes part in bus communication and sends an active error flag when an error has been detected.
  - 1: The FDCAN is in the error-passive state.
- **Bits 4:3 ACT[1:0]** (r): Activity
  Monitors the module's CAN communication state.
  - 00: Synchronizing: node is synchronizing on CAN communication.
  - 01: Idle: node is neither receiver nor transmitter.
  - 10: Receiver: node is operating as receiver.
  - 11: Transmitter: node is operating as transmitter.
- **Bits 2:0 LEC[2:0]** (rs): Last error code
  LEC[2:0] indicates the type of the last error to occur on the CAN bus. This bitfield is cleared when a message has been transferred (reception or transmission) without error.
  - 000: No error occurred since LEC[2:0] has been cleared by successful reception or transmission.
  - 001: Stuff error. More than five equal bits in a sequence have occurred in a part of a received message where this is not allowed.
  - 010: Form error. A fixed format part of a received frame has the wrong format.
  - 011: Ack error. The message transmitted by the FDCAN was not acknowledged by another node.
  - 100: Bit1 error. During the transmission of a message (with the exception of the arbitration field), the device wanted to send a recessive level (bit of logical value 1), but the monitored bus value was dominant.
  - 101: Bit0 error. During the transmission of a message (or acknowledge bit, or active error flag, or overload flag), the device wanted to send a dominant level (data or identifier bit logical value 0), but the monitored bus value was recessive. During bus-off recovery this status is set each time a sequence of 11 recessive bits has been monitored. This enables the CPU to monitor the proceeding of the bus-off recovery sequence (indicating the bus is not stuck at dominant or continuously disturbed).
  - 110: CRC error. The CRC check sum of a received message was incorrect. The CRC of an incoming message does not match with the CRC calculated from the received data.
  - 111: No change. Any read access to the protocol status register reinitializes LEC[2:0] to 7. When the LEC[2:0] shows the value 7, no CAN bus event was detected since the last CPU read access to the protocol status register.

  Access type is rs: set on read.

*Note:* When a frame in FDCAN format has reached the data phase with the BRS flag set, the next CAN event (error or valid frame) is shown in DLEC[2:0] instead of LEC[2:0]. An error in a fixed stuff bit of an FDCAN CRC sequence is shown as a form error, not as a stuff error.

The bus-off recovery sequence (see CAN Specification Rev. 2.0 or ISO11898-1) cannot be shortened by setting or clearing the INIT bit of the FDCAN_CCCR register. If the device enters bus-off, it sets the INIT bit of its own, stopping all bus activities. Once INIT has been cleared by the CPU, the device waits for 129 occurrences of bus-idle (129 × 11 consecutive recessive bits) before resuming normal operation. At the end of the bus-off recovery sequence, the error management counters are reset. During the waiting time after clearing INIT, each time a sequence of 11 recessive bits has been monitored, a bit0 error code is written to LEC[2:0] of FDCAN_PSR, enabling the CPU to check up whether the CAN bus is stuck at dominant or continuously disturbed, and to monitor the bus-off recovery sequence. The REC[6:0] bitfield of the FDCAN_ECR register is used to count these sequences.

*Digest note:* reading FDCAN_PSR has side effects: LEC and DLEC are set to 7 ("rs") and PXE/REDL/RBRS/RESI are cleared ("rc_r"). Table 485 shows DLEC[2:0] reset as 000 (reset 0x0000 0007) while this section gives 0x0000 0707.

### 46.5.14 FDCAN transmitter delay compensation register (FDCAN_TDCR)

Address offset: 0x0048. Reset value: 0x0000 0000.

- **Bits 31:15** Reserved, must be kept at reset value.
- **Bits 14:8 TDCO[6:0]** (rw): Transmitter delay compensation offset
  Offset value defining the distance between the measured delay from FDCAN_TX to FDCAN_RX and the secondary sample point. Valid values are 0 to 127 × mtq.
  This bitfield is write-protected (P), which means that write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bit 7** Reserved, must be kept at reset value.
- **Bits 6:0 TDCF[6:0]** (rw): Transmitter delay compensation filter window length
  Defines the minimum value for the SSP position, dominant edges on FDCAN_RX that would result in an earlier SSP position are ignored for transmitter delay measurements.
  This bitfield is write-protected (P), which means that write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.

### 46.5.15 FDCAN interrupt register (FDCAN_IR)

The flags are set when one of the listed conditions is detected (edge-sensitive). The flags remain set until the host clears them. A flag is cleared by writing 1 to the corresponding bit position.

Writing 0 has no effect. A hard reset clears the register. The configuration of FDCAN_IE controls whether an interrupt is generated. The configuration of FDCAN_ILS controls on which interrupt line an interrupt is signaled.

Address offset: 0x0050. Reset value: 0x0000 0000. All flag bits are rc_w1.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bit 23 ARA** (rc_w1): Access to reserved address
  - 0: No access to reserved address occurred
  - 1: Access to reserved address occurred
- **Bit 22 PED** (rc_w1): Protocol error in data phase (data bit time is used)
  - 0: No protocol error in data phase
  - 1: Protocol error in data phase detected (DLEC[2:0] different from 0 and 7 in FDCAN_PSR)
- **Bit 21 PEA** (rc_w1): Protocol error in arbitration phase (nominal bit time is used)
  - 0: No protocol error in arbitration phase
  - 1: Protocol error in arbitration phase detected (LEC[2:0] different from 0 and 7 in FDCAN_PSR)
- **Bit 20 WDI** (rc_w1): Watchdog interrupt
  - 0: No message RAM watchdog event occurred
  - 1: Message RAM watchdog event due to missing READY
- **Bit 19 BO** (rc_w1): Bus-off status
  - 0: Bus-off status unchanged
  - 1: Bus-off status changed
- **Bit 18 EW** (rc_w1): Warning status
  - 0: Error-warning status unchanged
  - 1: Error-warning status changed
- **Bit 17 EP** (rc_w1): Error passive
  - 0: Error-passive status unchanged
  - 1: Error-passive status changed
- **Bit 16 ELO** (rc_w1): Error logging overflow
  - 0: CAN error logging counter did not overflow.
  - 1: Overflow of CAN error logging counter occurred.
- **Bit 15 TOO** (rc_w1): Timeout occurred
  - 0: No timeout
  - 1: Timeout reached
- **Bit 14 MRAF** (rc_w1): Message RAM access failure
  The flag is set when the Rx handler:
  - has not completed acceptance filtering or storage of an accepted message until the arbitration field of the following message has been received. In this case acceptance filtering or message storage is aborted and the Rx handler starts processing of the following message.
  - was unable to write a message to the message RAM. In this case message storage is aborted.

  In both cases the FIFO put index is not updated. The partly stored message is overwritten when the next message is stored to this location.
  The flag is also set when the Tx handler was not able to read a message from the message RAM in time. In this case message transmission is aborted. In case of a Tx handler access failure, the FDCAN is switched into restricted operation mode (see Restricted operation mode). To leave restricted operation mode, the host CPU has to clear the ASM of the FDCAN_CCCR register.
  - 0: No message RAM access failure occurred
  - 1: Message RAM access failure occurred
- **Bit 13 TSW** (rc_w1): Timestamp wraparound
  - 0: No timestamp counter wrap-around
  - 1: Timestamp counter wrapped around
- **Bit 12 TEFL** (rc_w1): Tx event FIFO element lost
  - 0: No Tx event FIFO element lost
  - 1: Tx event FIFO element lost
- **Bit 11 TEFF** (rc_w1): Tx event FIFO full
  - 0: Tx event FIFO Not full
  - 1: Tx event FIFO full
- **Bit 10 TEFN** (rc_w1): Tx event FIFO new entry
  - 0: Tx event FIFO unchanged
  - 1: Tx handler wrote Tx event FIFO element.
- **Bit 9 TFE** (rc_w1): Tx FIFO empty
  - 0: Tx FIFO non-empty
  - 1: Tx FIFO empty
- **Bit 8 TCF** (rc_w1): Transmission cancellation finished
  - 0: No transmission cancellation finished
  - 1: Transmission cancellation finished
- **Bit 7 TC** (rc_w1): Transmission completed
  - 0: No transmission completed
  - 1: Transmission completed
- **Bit 6 HPM** (rc_w1): High-priority message
  - 0: No high-priority message received
  - 1: High-priority message received
- **Bit 5 RF1L** (rc_w1): Rx FIFO 1 message lost
  - 0: No Rx FIFO 1 message lost
  - 1: Rx FIFO 1 message lost
- **Bit 4 RF1F** (rc_w1): Rx FIFO 1 full
  - 0: Rx FIFO 1 not full
  - 1: Rx FIFO 1 full
- **Bit 3 RF1N** (rc_w1): Rx FIFO 1 new message
  - 0: No new message written to Rx FIFO 1
  - 1: New message written to Rx FIFO 1
- **Bit 2 RF0L** (rc_w1): Rx FIFO 0 message lost
  - 0: No Rx FIFO 0 message lost
  - 1: Rx FIFO 0 message lost
- **Bit 1 RF0F** (rc_w1): Rx FIFO 0 full
  - 0: Rx FIFO 0 not full
  - 1: Rx FIFO 0 full
- **Bit 0 RF0N** (rc_w1): Rx FIFO 0 new message
  - 0: No new message written to Rx FIFO 0
  - 1: New message written to Rx FIFO 0

### 46.5.16 FDCAN interrupt enable register (FDCAN_IE)

The settings in the interrupt enable register determine which status changes in the interrupt register are signaled on an interrupt line.

Address offset: 0x0054. Reset value: 0x0000 0000.

- **Bits 31:24** Reserved, must be kept at reset value.
- **Bit 23 ARAE** (rw): Access to reserved address enable
- **Bit 22 PEDE** (rw): Protocol error in data phase enable
- **Bit 21 PEAE** (rw): Protocol error in arbitration phase enable
- **Bit 20 WDIE** (rw): Watchdog interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 19 BOE** (rw): Bus-off status
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 18 EWE** (rw): Warning status interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 17 EPE** (rw): Error passive interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 16 ELOE** (rw): Error logging overflow interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 15 TOOE** (rw): Timeout occurred interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 14 MRAFE** (rw): Message RAM access failure interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 13 TSWE** (rw): Timestamp wraparound interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 12 TEFLE** (rw): Tx event FIFO element lost interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 11 TEFFE** (rw): Tx event FIFO full interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 10 TEFNE** (rw): Tx event FIFO new entry interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 9 TFEE** (rw): Tx FIFO empty interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 8 TCFE** (rw): Transmission cancellation finished interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 7 TCE** (rw): Transmission completed interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 6 HPME** (rw): High-priority message interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 5 RF1LE** (rw): Rx FIFO 1 message lost interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 4 RF1FE** (rw): Rx FIFO 1 full interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 3 RF1NE** (rw): Rx FIFO 1 new message interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 2 RF0LE** (rw): Rx FIFO 0 message lost interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 1 RF0FE** (rw): Rx FIFO 0 full interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled
- **Bit 0 RF0NE** (rw): Rx FIFO 0 new message interrupt enable
  - 0: Interrupt disabled
  - 1: Interrupt enabled

*Digest note:* the RM lists no value encoding under ARAE, PEDE and PEAE; it is the same 0/1 disable/enable as the other bits. The CMSIS header names the TC enable bit FDCAN_IE_TCE (0x0000 0080).

### 46.5.17 FDCAN interrupt line select register (FDCAN_ILS)

This register assigns an interrupt generated by a specific group of interrupt flags from the interrupt register to one of the two module interrupt lines. For interrupt generation, the respective interrupt line must be enabled via the EINT0 and EINT1 bit of the FDCAN_ILE register. 0 indicates that the interrupt is assigned to interrupt line fdcan1_intr0_it, 1 indicates that the interrupt is assigned to interrupt line fdcan1_intr1_it.

Address offset: 0x0058. Reset value: 0x0000 0000.

- **Bits 31:7** Reserved, must be kept at reset value.
- **Bit 6 PERR** (rw): Protocol error grouping the following interruption
  - ARAL: Access to reserved address line
  - PEDL: Protocol error in data phase line
  - PEAL: Protocol error in arbitration phase line
  - WDIL: Watchdog interrupt line
  - BOL: Bus-off status
  - EWL: Warning status interrupt line
- **Bit 5 BERR** (rw): Bit and line error grouping the following interruption
  - EPL Error passive interrupt line
  - ELOL: Error logging overflow interrupt line
- **Bit 4 MISC** (rw): Interrupt regrouping the following interruption
  - TOOL: Timeout occurred interrupt line
  - MRAFL: Message RAM access failure interrupt line
  - TSWL: Timestamp wraparound interrupt line
- **Bit 3 TFERR** (rw): Tx FIFO ERROR grouping the following interruption
  - TEFLL: Tx event FIFO element lost interrupt line
  - TEFFL: Tx event FIFO full interrupt line
  - TEFNL: Tx event FIFO new entry interrupt line
  - TFEL: Tx FIFO empty interrupt line
- **Bit 2 SMSG** (rw): Status message bit grouping the following interruption
  - TCFL: Transmission cancellation finished interrupt line
  - TCL: Transmission completed interrupt line
  - HPML: High-priority message interrupt line
- **Bit 1 RXFIFO1** (rw): RX FIFO bit grouping the following interruption
  - RF1LL: Rx FIFO 1 message lost interrupt line
  - RF1FL: Rx FIFO 1 full interrupt line
  - RF1NL: Rx FIFO 1 new message interrupt line
- **Bit 0 RXFIFO0** (rw): RX FIFO bit grouping the following interruption
  - RF0LL: Rx FIFO 0 message lost interrupt line
  - RF0FL: Rx FIFO 0 full interrupt line
  - RF0NL: Rx FIFO 0 new message interrupt line

*Digest note:* group-to-IR-flag mapping: PERR = IR bits 23:18 (ARA, PED, PEA, WDI, BO, EW); BERR = IR bits 17:16 (EP, ELO); MISC = IR bits 15:13 (TOO, MRAF, TSW); TFERR = IR bits 12:9 (TEFL, TEFF, TEFN, TFE); SMSG = IR bits 8:6 (TCF, TC, HPM); RXFIFO1 = IR bits 5:3; RXFIFO0 = IR bits 2:0. With ILS = 0 (reset) every enabled interrupt goes to line 0 (FDCAN1_IT0, IRQ 34 on STM32C552).

### 46.5.18 FDCAN interrupt line enable register (FDCAN_ILE)

Each of the two interrupt lines to the CPU can be enabled/disabled separately by programming the EINT0 and EINT1 bits.

Address offset: 0x005C. Reset value: 0x0000 0000.

- **Bits 31:2** Reserved, must be kept at reset value.
- **Bit 1 EINT1** (rw): Enable interrupt line 1
  - 0: Interrupt line fdcan_intr0_it disabled
  - 1: Interrupt line fdcan_intr0_it enabled
- **Bit 0 EINT0** (rw): Enable interrupt line 0
  - 0: Interrupt line fdcan_intr1_it disabled
  - 1: Interrupt line fdcan_intr1_it enabled

*Digest note:* the line names in the EINT0/EINT1 value descriptions appear swapped relative to the field names. The field titles ("Enable interrupt line 0/1"), the FDCAN_ILS description (0 = fdcan1_intr0_it) and the CMSIS header comments ("Enable Interrupt Line 0" for EINT0 = 0x1, "Enable Interrupt Line 1" for EINT1 = 0x2) indicate EINT0 enables fdcan_intr0_it (IT0) and EINT1 enables fdcan_intr1_it (IT1).

### 46.5.19 FDCAN global filter configuration register (FDCAN_RXGFC)

Global settings for message ID filtering. The global filter configuration controls the filter path for standard and extended messages as described in Figure 701 and Figure 702.

Address offset: 0x0080. Reset value: 0x0000 0000.

- **Bits 31:28** Reserved, must be kept at reset value.
- **Bits 27:24 LSE[3:0]** (rw): Number of extended filter elements in the list
  - 0: No extended message ID filter
  - 1 to 8: Number of extended message ID filter elements
  - \> 8: Values greater than 8 are interpreted as 8.

  This bitfield is write-protected (P), which means that write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bits 23:21** Reserved, must be kept at reset value.
- **Bits 20:16 LSS[4:0]** (rw): Number of standard filter elements in the list
  - 0: No standard message ID filter
  - 1 to 28: Number of standard message ID filter elements
  - \> 28: Values greater than 28 are interpreted as 28.

  This bitfield is write protected (P), which means that write access by the bits is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bits 15:10** Reserved, must be kept at reset value.
- **Bit 9 F0OM** (rw): FIFO 0 operation mode (overwrite or blocking)
  This bit is write-protected (P), which means that write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bit 8 F1OM** (rw): FIFO 1 operation mode (overwrite or blocking)
  This bit is write-protected (P), which means that write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bits 7:6** Reserved, must be kept at reset value.
- **Bits 5:4 ANFS[1:0]** (rw): Accept Non-matching frames standard
  Defines how received messages with 11-bit IDs that do not match any element of the filter list are treated.
  - 00: Accept in Rx FIFO 0
  - 01: Accept in Rx FIFO 1
  - 10: Reject
  - 11: Reject

  This bitfield is write-protected (P), which means write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bits 3:2 ANFE[1:0]** (rw): Accept non-matching frames extended
  Defines how received messages with 29-bit IDs that do not match any element of the filter list are treated.
  - 00: Accept in Rx FIFO 0
  - 01: Accept in Rx FIFO 1
  - 10: Reject
  - 11: Reject

  This bitfield is write-protected (P), which means that write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bit 1 RRFS** (rw): Reject remote frames standard
  - 0: Filter remote frames with 11-bit standard IDs
  - 1: Reject all remote frames with 11-bit standard IDs

  This bit is write-protected (P), which means that write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bit 0 RRFE** (rw): Reject remote frames extended
  - 0: Filter remote frames with 29-bit standard IDs
  - 1: Reject all remote frames with 29-bit standard IDs

  This bit is write-protected (P), which means that write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.

*Digest note:* FnOM encoding follows Section 46.4.6: 0 = blocking mode (default), 1 = overwrite mode. RRFE applies to 29-bit (extended) IDs despite the wording "29-bit standard IDs". Reset value 0x0000 0000 means: no filter elements in either list, and all non-matching standard and extended frames (including remote frames) are accepted into Rx FIFO 0. The CMSIS header agrees with the bit positions (LSE 0x0F00 0000, LSS 0x001F 0000, F0OM 0x200, F1OM 0x100, ANFS 0x30, ANFE 0x0C, RRFS 0x2, RRFE 0x1).

### 46.5.20 FDCAN extended ID and mask register (FDCAN_XIDAM)

Address offset: 0x0084. Reset value: 0x1FFF FFFF.

- **Bits 31:29** Reserved, must be kept at reset value.
- **Bits 28:0 EIDM[28:0]** (rw): Extended ID mask
  For acceptance filtering of extended frames the extended ID AND mask is AND-ed with the message ID of a received frame. Intended for masking of 29-bit IDs in SAE J1939. With the reset value of all bits set, the mask is not active.
  This bitfield is write-protected (P), which means that write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.

### 46.5.21 FDCAN high-priority message status register (FDCAN_HPMS)

This register is updated every time a message ID filter element configured to generate a priority event match. This can be used to monitor the status of incoming high priority messages and to enable fast access to these messages.

Address offset: 0x0088. Reset value: 0x0000 0000. All bits read-only.

- **Bits 31:16** Reserved, must be kept at reset value.
- **Bit 15 FLST** (r): Filter list
  Indicates the filter list of the matching filter element:
  - 0: Standard filter list
  - 1: Extended filter list
- **Bits 14:13** Reserved, must be kept at reset value.
- **Bits 12:8 FIDX[4:0]** (r): Filter index
  Index of matching filter element.
  Range: 0 to LSS[4:0] - 1 or LSE[3:0] - 1 in FDCAN_RXGFC.
- **Bits 7:6 MSI[1:0]** (r): Message storage indicator
  - 00: No FIFO selected
  - 01: FIFO overrun
  - 10: Message stored in FIFO 0
  - 11: Message stored in FIFO 1
- **Bits 5:3** Reserved, must be kept at reset value.
- **Bits 2:0 BIDX[2:0]** (r): Buffer index
  Index of Rx FIFO element to which the message was stored. Only valid when MSI[1] = 1.

### 46.5.22 FDCAN Rx FIFO 0 status register (FDCAN_RXF0S)

Address offset: 0x0090. Reset value: 0x0000 0000. All bits read-only.

- **Bits 31:26** Reserved, must be kept at reset value.
- **Bit 25 RF0L** (r): Rx FIFO 0 message lost
  This bit is a copy of the RF0L interrupt flag of the FDCAN_IR register. When RF0L is cleared, this bit is also cleared.
  - 0: No Rx FIFO 0 message lost
  - 1: Rx FIFO 0 message lost, also set after write attempt to Rx FIFO 0 of size 0
- **Bit 24 F0F** (r): Rx FIFO 0 full
  - 0: Rx FIFO 0 not full
  - 1: Rx FIFO 0 full
- **Bits 23:18** Reserved, must be kept at reset value.
- **Bits 17:16 F0PI[1:0]** (r): Rx FIFO 0 put index
  Rx FIFO 0 write index pointer.
  Range: 0 to 2.
- **Bits 15:10** Reserved, must be kept at reset value.
- **Bits 9:8 F0GI[1:0]** (r): Rx FIFO 0 get index
  Rx FIFO 0 read index pointer.
  Range: 0 to 2.
- **Bits 7:4** Reserved, must be kept at reset value.
- **Bits 3:0 F0FL[3:0]** (r): Rx FIFO 0 fill level
  Number of elements stored in Rx FIFO 0.
  Range: 0 to 3.

### 46.5.23 CAN Rx FIFO 0 acknowledge register (FDCAN_RXF0A)

Address offset: 0x0094. Reset value: 0x0000 0000.

- **Bits 31:3** Reserved, must be kept at reset value.
- **Bits 2:0 F0AI[2:0]** (rw): Rx FIFO 0 acknowledge index
  After the host has read a message or a sequence of messages from Rx FIFO 0, it has to write the buffer index of the last element read from Rx FIFO 0 to F0AI[2:0]. This sets the Rx FIFO 0 get index (F0GI[1:0] of FDCAN_RXF0S) to F0AI[2:0] + 1 and updates the FIFO 0 fill level (F0FL[3:0] FDCAN_RXF0S).

### 46.5.24 FDCAN Rx FIFO 1 status register (FDCAN_RXF1S)

Address offset: 0x0098. Reset value: 0x0000 0000. All bits read-only.

- **Bits 31:26** Reserved, must be kept at reset value.
- **Bit 25 RF1L** (r): Rx FIFO 1 message lost
  This bit is a copy of the RF1L interrupt flag of the FDCAN_IR register. When RF1L is cleared, this bit is also cleared.
  - 0: No Rx FIFO 1 message lost
  - 1: Rx FIFO 1 message lost, also set after write attempt to Rx FIFO 1 of size 0
- **Bit 24 F1F** (r): Rx FIFO 1 full
  - 0: Rx FIFO 1 not full
  - 1: Rx FIFO 1 full
- **Bits 23:18** Reserved, must be kept at reset value.
- **Bits 17:16 F1PI[1:0]** (r): Rx FIFO 1 put index
  Rx FIFO 1 write index pointer.
  Range: 0 to 2.
- **Bits 15:10** Reserved, must be kept at reset value.
- **Bits 9:8 F1GI[1:0]** (r): Rx FIFO 1 get index
  Rx FIFO 1 read index pointer.
  Range: 0 to 2.
- **Bits 7:4** Reserved, must be kept at reset value.
- **Bits 3:0 F1FL[3:0]** (r): Rx FIFO 1 fill level
  Number of elements stored in Rx FIFO 1.
  Range: 0 to 3.

### 46.5.25 FDCAN Rx FIFO 1 acknowledge register (FDCAN_RXF1A)

Address offset: 0x009C. Reset value: 0x0000 0000.

- **Bits 31:3** Reserved, must be kept at reset value.
- **Bits 2:0 F1AI[2:0]** (rw): Rx FIFO 1 acknowledge index
  After the host has read a message or a sequence of messages from Rx FIFO 1, it has to write the buffer index of the last element read from Rx FIFO 1 to F1AI[2:0]. This sets the Rx FIFO 1 get index (F1GI[1:0] of FDCAN_RXF1S) to F1AI[2:0] + 1 and updates the FIFO 1 fill level (F1FL[3:0] FDCAN_RXF1S).

*Digest note:* typical Rx FIFO 0 read (classic CAN): if RXF0S.F0FL ≠ 0, read the element at message RAM offset 0x00B0 + 0x48 × F0GI (R0 = ID/XTD/RTR, R1 = DLC/timestamp, R2/R3 = data bytes 0–7), then write F0GI to RXF0A.F0AI; clear IR.RF0N by writing 1 to it. The get index wraps 2 → 0 (three elements).

### 46.5.26 FDCAN Tx buffer configuration register (FDCAN_TXBC)

Address offset: 0x00C0. Reset value: 0x0000 0000.

- **Bits 31:25** Reserved, must be kept at reset value.
- **Bit 24 TFQM** (rw): Tx FIFO/queue mode
  - 0: Tx FIFO operation
  - 1: Tx queue operation.

  This bit is write-protected (P), which means that write access is possible only when the CCE and INIT bits of the FDCAN_CCCR register are both set.
- **Bits 23:0** Reserved, must be kept at reset value.

### 46.5.27 FDCAN Tx FIFO/queue status register (FDCAN_TXFQS)

The Tx FIFO/queue status is related to the pending Tx requests listed in the FDCAN_TXBRP register. Therefore, the effect of add/cancellation requests can be delayed due to a running Tx scan (FDCAN_TXBRP not yet updated).

Address offset: 0x00C4. Reset value: 0x0000 0003. All bits read-only.

- **Bits 31:22** Reserved, must be kept at reset value.
- **Bit 21 TFQF** (r): Tx FIFO/queue full
  - 0: Tx FIFO/queue not full
  - 1: Tx FIFO/queue full
- **Bits 20:18** Reserved, must be kept at reset value.
- **Bits 17:16 TFQPI[1:0]** (r): Tx FIFO/queue put index
  Tx FIFO/queue write index pointer, range 0 to 3
- **Bits 15:10** Reserved, must be kept at reset value.
- **Bits 9:8 TFGI[1:0]** (r): Tx FIFO get index
  Tx FIFO read index pointer, range 0 to 3. Read as 0 when Tx queue operation is configured (TFQM = 1 in FDCAN_TXBC)
- **Bits 7:3** Reserved, must be kept at reset value.
- **Bits 2:0 TFFL[2:0]** (r): Tx FIFO free level
  Number of consecutive free Tx FIFO elements starting from TFGI, range 0 to 3. Read as 0 when Tx queue operation is configured (TFQM = 1 in FDCAN_TXBC).

*Digest note:* with three Tx buffers the usable index range is 0 to 2 (Section 46.4.6 gives TFQPI "(0 … 2)"); the "range 0 to 3" applies to TFFL only. Reset TFFL = 3 (all three buffers free).

### 46.5.28 FDCAN Tx buffer request pending register (FDCAN_TXBRP)

Address offset: 0x00C8. Reset value: 0x0000 0000.

- **Bits 31:3** Reserved, must be kept at reset value.
- **Bits 2:0 TRP[2:0]** (r): Transmission request pending
  Each Tx buffer has its own transmission request pending bit. The bits are set via the FDCAN_TXBAR register. The bits are cleared after a requested transmission has completed or has been canceled via the FDCAN_TXBCR register.
  After the FDCAN_TXBRP bit has been set, a Tx scan is started to check for the pending Tx request with the highest priority (Tx buffer with lowest message ID).
  A cancellation request resets the corresponding transmission request pending bit of the FDCAN_TXBRP register. In case a transmission has already been started when a cancellation is requested, this is done at the end of the transmission, regardless whether the transmission was successful or not. The cancellation request bits are directly cleared after the corresponding FDCAN_TXBRP bit has been cleared.
  After a cancellation has been requested, a finished cancellation is signaled via the FDCAN_TXBCF in the following cases:
  - after successful transmission together with the corresponding TXBTO bit
  - when the transmission has not yet been started at the point of cancellation
  - when the transmission has been aborted due to lost arbitration
  - when an error occurred during frame transmission

  In DAR mode, all transmissions are automatically canceled if they are not successful. The corresponding FDCAN_TXBCF bit is set for all unsuccessful transmissions.
  - 0: No transmission request pending
  - 1: Transmission request pending

*Note:* FDCAN_TXBRP bits set while a Tx scan is in progress are not considered during this particular Tx scan. In case a cancellation is requested for such a Tx buffer, this add request is canceled immediately. The corresponding FDCAN_TXBRP bit is cleared.

### 46.5.29 FDCAN Tx buffer add request register (FDCAN_TXBAR)

Address offset: 0x00CC. Reset value: 0x0000 0000.

- **Bits 31:3** Reserved, must be kept at reset value.
- **Bits 2:0 AR[2:0]** (rw): Add request
  Each Tx buffer has its own add request bit. Writing a 1 sets the corresponding add request bit; writing a 0 has no impact. This enables the host to set transmission requests for multiple Tx buffers with one write to FDCAN_TXBAR. When no Tx scan is running, the bits are cleared immediately, else the bits remain set until the Tx scan process has completed.
  - 0: No transmission request added
  - 1: Transmission requested added.

*Note:* If an add request is applied for a Tx buffer with pending transmission request (corresponding FDCAN_TXBRP bit already set), the request is ignored.

*Digest note:* typical Tx FIFO send (TFQM = 0): if TXFQS.TFQF = 0, write the element (T0 = XTD/RTR/ID, T1 = DLC and optional EFC/MM, T2/T3 = data bytes 0–7) at message RAM offset 0x0278 + 0x48 × TFQPI, then write (1 << TFQPI) to TXBAR. Per Section 46.4.4, TXBAR can only be written while CCE = 0.

### 46.5.30 FDCAN Tx buffer cancellation request register (FDCAN_TXBCR)

Address offset: 0x00D0. Reset value: 0x0000 0000.

- **Bits 31:3** Reserved, must be kept at reset value.
- **Bits 2:0 CR[2:0]** (rw): Cancellation request
  Each Tx buffer has its own cancellation request bit. Writing a 1 sets the corresponding CR bit; writing a 0 has no impact.
  This enables the host to set cancellation requests for multiple Tx buffers with one write to FDCAN_TXBCR. The bits remain set until the corresponding FDCAN_TXBRP bit is cleared.
  - 0: No cancellation pending
  - 1: Cancellation pending

### 46.5.31 FDCAN Tx buffer transmission occurred register (FDCAN_TXBTO)

Address offset: 0x00D4. Reset value: 0x0000 0000.

- **Bits 31:3** Reserved, must be kept at reset value.
- **Bits 2:0 TO[2:0]** (r): Transmission occurred.
  Each Tx buffer has its own TO bit. The bits are set when the corresponding FDCAN_TXBRP bit is cleared after a successful transmission. The bits are cleared when a new transmission is requested by writing a 1 to the corresponding bit of register FDCAN_TXBAR.
  - 0: No transmission occurred
  - 1: Transmission occurred

### 46.5.32 FDCAN Tx buffer cancellation finished register (FDCAN_TXBCF)

Address offset: 0x00D8. Reset value: 0x0000 0000.

- **Bits 31:3** Reserved, must be kept at reset value.
- **Bits 2:0 CF[2:0]** (r): Cancellation finished
  Each Tx buffer has its own CF bit. The bits are set when the corresponding FDCAN_TXBRP bit is cleared after a cancellation was requested via FDCAN_TXBCR. In case the corresponding FDCAN_TXBRP bit was not set at the point of cancellation, CF is set immediately. The bits are cleared when a new transmission is requested by writing a 1 to the corresponding bit of the FDCAN_TXBAR register.
  - 0: No transmit buffer cancellation
  - 1: Transmit buffer cancellation finished

### 46.5.33 FDCAN Tx buffer transmission interrupt enable register (FDCAN_TXBTIE)

Address offset: 0x00DC. Reset value: 0x0000 0000.

- **Bits 31:3** Reserved, must be kept at reset value.
- **Bits 2:0 TIE[2:0]** (rw): Transmission interrupt enable
  Each Tx buffer has its own TIE bit.
  - 0: Transmission interrupt disabled
  - 1: Transmission interrupt enable

### 46.5.34 FDCAN Tx buffer cancellation finished interrupt enable register (FDCAN_TXBCIE)

Address offset: 0x00E0. Reset value: 0x0000 0000.

- **Bits 31:3** Reserved, must be kept at reset value.
- **Bits 2:0 CFIE[2:0]** (rw): Cancellation finished interrupt enable.
  Each Tx buffer has its own CFIE bit.
  - 0: Cancellation finished interrupt disabled
  - 1: Cancellation finished interrupt enabled

### 46.5.35 FDCAN Tx event FIFO status register (FDCAN_TXEFS)

Address offset: 0x00E4. Reset value: 0x0000 0000. All bits read-only.

- **Bits 31:26** Reserved, must be kept at reset value.
- **Bit 25 TEFL** (r): Tx event FIFO element lost
  This bit is a copy of the TEFL interrupt flag of the FDCAN_IR. When TEFL is cleared, this bit is also cleared.
  - 0 No Tx event FIFO element lost
  - 1 Tx event FIFO element lost, also set after write attempt to Tx event FIFO of size 0.
- **Bit 24 EFF** (r): Event FIFO full
  - 0: Tx event FIFO not full
  - 1: Tx event FIFO full
- **Bits 23:18** Reserved, must be kept at reset value.
- **Bits 17:16 EFPI[1:0]** (r): Event FIFO put index
  Tx event FIFO write index pointer.
  Range: 0 to 3.
- **Bits 15:10** Reserved, must be kept at reset value.
- **Bits 9:8 EFGI[1:0]** (r): Event FIFO get index
  Tx event FIFO read index pointer.
  Range: 0 to 3.
- **Bits 7:3** Reserved, must be kept at reset value.
- **Bits 2:0 EFFL[2:0]** (r): Event FIFO fill level
  Number of elements stored in Tx event FIFO.
  Range: 0 to 3.

### 46.5.36 FDCAN Tx event FIFO acknowledge register (FDCAN_TXEFA)

Address offset: 0x00E8. Reset value: 0x0000 0000.

- **Bits 31:2** Reserved, must be kept at reset value.
- **Bits 1:0 EFAI[1:0]** (rw): Event FIFO acknowledge index
  After the host has read an element or a sequence of elements from the Tx event FIFO, it has to write the index of the last element read from Tx event FIFO to EFAI[1:0]. This sets the Tx event FIFO get index (EFGI[1:0] of FDCAN_TXEFS) to EFAI[1:0] + 1 and updates the FIFO 0 fill level (EFFL[2:0] of FDCAN_TXEFS).

### 46.5.37 FDCAN CFG clock divider register (FDCAN_CKDIV)

Address offset: 0x0100. Reset value: 0x0000 0000.

- **Bits 31:4** Reserved, must be kept at reset value.
- **Bits 3:0 PDIV[3:0]** (rw): input clock divider
  The CAN kernel clock can be divided prior to be used by the CAN subsystem. The rate must be computed using the divider output clock.
  - 0000: Divide by 1
  - 0001: Divide by 2
  - 0010: Divide by 4
  - 0011: Divide by 6
  - 0100: Divide by 8
  - 0101: Divide by 10
  - 0110: Divide by 12
  - 0111: Divide by 14
  - 1000: Divide by 16
  - 1001: Divide by 18
  - 1010: Divide by 20
  - 1011: Divide by 22
  - 1100: Divide by 24
  - 1101: Divide by 26
  - 1110: Divide by 28
  - 1111: Divide by 30

  This bitfield is write-protected (P): which means that write access is possible only when the CCE bit of the FDCAN_CCCR register is set.

*Note:* The clock divider is common to all FDCAN instances. Only FDCAN1 instance has FDCAN_CKDIV register, which changes clock divider for all instances.

*Digest note:* the CMSIS header places this register in a separate FDCAN_Config_TypeDef at FDCAN_CONFIG_BASE = 0x4000 A500 (FDCAN1_BASE + 0x100), accessed as FDCAN_CONFIG->CKDIV. Divider output = fdcan_tq_ck (Figure 693), which must not exceed fdcan_pclk (Section 46.4.3). With the reset PDIV = 0, fdcan_tq_ck = fdcan_ker_ck.

### 46.5.38 FDCAN register map

**Table 485. FDCAN register map and reset values**

| Offset | Register | Reset value | Fields (bit positions) |
|---|---|---|---|
| 0x0000 | FDCAN_CREL | 0x3214 1218 (1) | REL[3:0] (31:28), STEP[3:0] (27:24), SUBSTEP[3:0] (23:20), YEAR[3:0] (19:16), MON[7:0] (15:8), DAY[7:0] (7:0) |
| 0x0004 | FDCAN_ENDN | 0x8765 4321 | ETV[31:0] (31:0) |
| 0x0008 | Reserved | - | Reserved |
| 0x000C | FDCAN_DBTP | 0x0000 0A33 | TDC (23), DBRP[4:0] (20:16), DTSEG1[4:0] (12:8), DTSEG2[3:0] (7:4), DSJW[3:0] (3:0) |
| 0x0010 | FDCAN_TEST | 0x0000 0000 | RX (7), TX[1:0] (6:5), LBCK (4) |
| 0x0014 | FDCAN_RWD | 0x0000 0000 | WDV[7:0] (15:8), WDC[7:0] (7:0) |
| 0x0018 | FDCAN_CCCR | 0x0000 0001 | NISO (15), TXP (14), EFBI (13), PXHD (12), BRSE (9), FDOE (8), TEST (7), DAR (6), MON (5), CSR (4), CSA (3), ASM (2), CCE (1), INIT (0) (2) |
| 0x001C | FDCAN_NBTP | 0x0600 0A03 | NSJW[6:0] (31:25), NBRP[8:0] (24:16), NTSEG1[7:0] (15:8), NTSEG2[6:0] (6:0) |
| 0x0020 | FDCAN_TSCC | 0x0000 0000 | TCP[3:0] (19:16), TSS[1:0] (1:0) |
| 0x0024 | FDCAN_TSCV | 0x0000 0000 | TSC[15:0] (15:0) |
| 0x0028 | FDCAN_TOCC | 0xFFFF 0000 | TOP[15:0] (31:16), TOS[1:0] (2:1), ETOC (0) |
| 0x002C | FDCAN_TOCV | 0x0000 FFFF | TOC[15:0] (15:0) |
| 0x0030-0x003C | Reserved | - | Reserved |
| 0x0040 | FDCAN_ECR | 0x0000 0000 | CEL[7:0] (23:16), RP (15), REC[6:0] (14:8), TEC[7:0] (7:0) |
| 0x0044 | FDCAN_PSR | 0x0000 0707 (3) | TDCV[6:0] (22:16), PXE (14), REDL (13), RBRS (12), RESI (11), DLEC[2:0] (10:8), BO (7), EW (6), EP (5), ACT[1:0] (4:3), LEC[2:0] (2:0) |
| 0x0048 | FDCAN_TDCR | 0x0000 0000 | TDCO[6:0] (14:8), TDCF[6:0] (6:0) |
| 0x004C | Reserved | - | Reserved |
| 0x0050 | FDCAN_IR | 0x0000 0000 | ARA (23), PED (22), PEA (21), WDI (20), BO (19), EW (18), EP (17), ELO (16), TOO (15), MRAF (14), TSW (13), TEFL (12), TEFF (11), TEFN (10), TFE (9), TCF (8), TC (7), HPM (6), RF1L (5), RF1F (4), RF1N (3), RF0L (2), RF0F (1), RF0N (0) |
| 0x0054 | FDCAN_IE | 0x0000 0000 | ARAE (23), PEDE (22), PEAE (21), WDIE (20), BOE (19), EWE (18), EPE (17), ELOE (16), TOOE (15), MRAFE (14), TSWE (13), TEFLE (12), TEFFE (11), TEFNE (10), TFEE (9), TCFE (8), TCE (7), HPME (6), RF1LE (5), RF1FE (4), RF1NE (3), RF0LE (2), RF0FE (1), RF0NE (0) |
| 0x0058 | FDCAN_ILS | 0x0000 0000 | PERR (6), BERR (5), MISC (4), TFERR (3), SMSG (2), RXFIFO1 (1), RXFIFO0 (0) |
| 0x005C | FDCAN_ILE | 0x0000 0000 | EINT1 (1), EINT0 (0) |
| 0x0060-0x007C | Reserved | - | Reserved |
| 0x0080 | FDCAN_RXGFC | 0x0000 0000 | LSE[3:0] (27:24), LSS[4:0] (20:16), F0OM (9), F1OM (8), ANFS[1:0] (5:4), ANFE[1:0] (3:2), RRFS (1), RRFE (0) |
| 0x0084 | FDCAN_XIDAM | 0x1FFF FFFF | EIDM[28:0] (28:0) |
| 0x0088 | FDCAN_HPMS | 0x0000 0000 | FLST (15), FIDX[4:0] (12:8), MSI[1:0] (7:6), BIDX[2:0] (2:0) |
| 0x0090 | FDCAN_RXF0S | 0x0000 0000 | RF0L (25), F0F (24), F0PI[1:0] (17:16), F0GI[1:0] (9:8), F0FL[3:0] (3:0) |
| 0x0094 | FDCAN_RXF0A | 0x0000 0000 | F0AI[2:0] (2:0) |
| 0x0098 | FDCAN_RXF1S | 0x0000 0000 | RF1L (25), F1F (24), F1PI[1:0] (17:16), F1GI[1:0] (9:8), F1FL[3:0] (3:0) |
| 0x009C | FDCAN_RXF1A | 0x0000 0000 | F1AI[2:0] (2:0) |
| 0x00A0-0x00BC | Reserved | - | Reserved |
| 0x00C0 | FDCAN_TXBC | 0x0000 0000 | TFQM (24) |
| 0x00C4 | FDCAN_TXFQS | 0x0000 0003 | TFQF (21), TFQPI[1:0] (17:16), TFGI[1:0] (9:8), TFFL[2:0] (2:0) |
| 0x00C8 | FDCAN_TXBRP | 0x0000 0000 | TRP2 (2), TRP1 (1), TRP0 (0) |
| 0x00CC | FDCAN_TXBAR | 0x0000 0000 | AR2 (2), AR1 (1), AR0 (0) |
| 0x00D0 | FDCAN_TXBCR | 0x0000 0000 | CR2 (2), CR1 (1), CR0 (0) |
| 0x00D4 | FDCAN_TXBTO | 0x0000 0000 | TO2 (2), TO1 (1), TO0 (0) |
| 0x00D8 | FDCAN_TXBCF | 0x0000 0000 | CF2 (2), CF1 (1), CF0 (0) |
| 0x00DC | FDCAN_TXBTIE | 0x0000 0000 | TIE2 (2), TIE1 (1), TIE0 (0) |
| 0x00E0 | FDCAN_TXBCIE | 0x0000 0000 | CFIE2 (2), CFIE1 (1), CFIE0 (0) |
| 0x00E4 | FDCAN_TXEFS | 0x0000 0000 | TEFL (25), EFF (24), EFPI[1:0] (17:16), EFG[1:0] (9:8) (4), EFFL[2:0] (2:0) |
| 0x00E8 | FDCAN_TXEFA | 0x0000 0000 | EFAI[1:0] (1:0) |
| 0x0100 | FDCAN_CKDIV | 0x0000 0000 | PDIV[3:0] (3:0) |

Notes:

1. The reset value is taken from Section 46.5.1. The reset-value row printed for FDCAN_CREL in Table 485 reads 0000 0001 1110 1010 0110 1111 1010 0010 (bit 31 to bit 0), i.e. 0x01EA 6FA2, which does not match. [unclear in source: which CREL reset value is correct; software should not depend on it.]
2. Table 485 labels bit 0 of FDCAN_CCCR "INT"; the field is INIT (Section 46.5.6).
3. The reset value is taken from Section 46.5.13. The reset-value row printed for FDCAN_PSR in Table 485 shows DLEC[2:0] = 000 and LEC[2:0] = 111, i.e. 0x0000 0007. [unclear in source: DLEC reset value; reading PSR sets DLEC and LEC to 7 anyway.]
4. Table 485 labels FDCAN_TXEFS bits 9:8 "EFG[1:0]"; the field is EFGI[1:0] (Section 46.5.35).

Refer to Section 2.2: Memory organization for the register boundary addresses.

*Digest note:* Table 485 has no rows for offsets 0x008C and 0x00EC–0x00FC; the CMSIS header marks 0x008C as reserved (FDCAN_GlobalTypeDef ends at TXEFA, 0x00E8) and places CKDIV (0x0100) in the separate FDCAN_CONFIG block. All register offsets and bit masks in this table match stm32c552xx.h.
