# Rev A electronics

Rev A uses 20V between tiles. The old 5V bus needed too much current for the larger loads. Each tile now makes its own 5V and 3.3V. Don't join those local rails between tiles.

The schematic has source protection, switched module power, four UART links and two RGB LEDs. The PCB only has initial low-voltage placement. It still needs connector checks, protection tests and routing. [Test results](validation.md) and [pinouts](interfaces.md) are separate.

## Power path

Power can arrive from any edge:

- F2-F5 connect each edge to BUS_20V through a 1A fuse. They work in either direction.
- F1 feeds LOCAL_20V_RAW. U7, TPS26600PWPR, protects the local load and supplies TILE_20V.
- U4, LMR36520ADDAR, converts that to 5V. U2, AP2112K-3.3TRG1, makes 3.3V.
- U3, TPS259470LRPWR, switches MODULE_5V with reverse blocking.
- U5, TPS26600PWPR, switches MODULE_20V.

U7 and U5 use 402k MODE resistors for active current limiting and thermal latch-off. U7 starts with SHDN open. Resetting its thermal latch needs the shared bus powered down; unplugging one edge won't do that in a loop.

Keep LOCAL_RTN and MODULE_RTN separate from GND, including the exposed thermal pads and support parts. The PWP footprint uses a 3.3mm square mask opening from PWP0016A. RTN copper and thermal vias still need layout work. The RPW footprint's repeated corner pad numbers form the intended L-shaped lands. Both footprints use TI's 0.100mm stencil examples; assembly still needs review.

D4/D5 are bidirectional SMBJ22CA-E3/52 on the shared bus and local input. D6/D7 are unidirectional SMBJ22A-E3/52 on the protected rails. A TVS can't absorb a sustained wrong supply.

AP63205, AP2171 and using TPS259470L directly on 20V are old choices. The present parts address input-voltage margin and reverse-current concerns.

## MCU pins

CH32X035G8U6 uses QFN28, with the exposed GND pad numbered 29. These match the WCH pin diagram and current symbol. The actual chips still need testing.

- Pin 1, PC15/CC2: Unused, PD disabled.
- Pin 2, VDD: Local 3.3V.
- Pin 3, PC0: MODULE_20V_EN.
- Pin 4, PC3: MODULE_20V_FAULT.
- Pin 5, PA0: BUS_SENSE, ADC_IN0.
- Pin 6, PA1: N_DETECT.
- Pin 7, PA2: East USART2 TX.
- Pin 8, PA3: East USART2 RX.
- Pin 9, PA4: E_DETECT.
- Pin 10, PA5: MODULE_5V_FAULT.
- Pin 11, PA6: MODULE_ID, ADC_IN6.
- Pin 12, PA7: RGB_DATA, SPI1 MOSI candidate.
- Pin 13, PB0: West USART4 TX.
- Pin 14, PB3: South USART3 TX.
- Pin 15, PB4: South USART3 RX.
- Pin 16, PB1/PB5: West USART4 RX using PB1; PB5 floating.
- Pin 17, PB6: MODULE_IO_REQUEST.
- Pin 18, PB7: MODULE_5V_EN.
- Pin 19, PB8: EDGE_IO_DISABLE.
- Pin 20, PB9: LOCAL_POWER_FAULT.
- Pin 21, PB10: North USART1 TX.
- Pin 22, PB11: North USART1 RX.
- Pin 23, PB12: MODULE_CTRL, TIM1 channel 4.
- Pin 24, PC19/DCK: Debug clock.
- Pin 25, PC18/DIO: Debug data.
- Pin 26, PC11/PC16/UDM: MODULE_SCL using PC16.
- Pin 27, PC10/PC17/UDP: MODULE_SDA using PC17.
- Pin 28, PC14/CC1: Unused, PD disabled.
- Pin 29, GND exposed pad: GND.

PB6/PB8 weren't a valid hardware I²C pair. I²C now uses PC16/PC17 with I2C1_RM=010 (`GPIO_PartialRemap2_I2C1`). Leave their PC11/PC10 aliases floating; USB data is unavailable on these pins. WCH datasheet V1.7 note 3 limits I²C on some silicon lots. Check markings and test purchased chips.

USART1-4 use remap 0, TX/RX only. Don't enable CTS, RTS or CK. Leave PB5 floating because it shares the PB1 pad.

PB12 uses TIM1 channel 4 with TIM1_RM=010. Keep channels 1-3, complementary outputs, trigger and break pins disabled or unassigned; they conflict with other functions.

PA7 can send RGB data through SPI1 MOSI with remap 0. Don't let SPI setup take PA4/NSS, PA5/SCK or PA6/MISO. TIM3 channel 2 is another option. LED timing, clock tolerance, DMA and interrupt load with four UARTs still need testing. Keep PC18/PC19 for debug.

## Circuit values

These are datasheet values and calculations, not measurements.

### Input and fuses

- TPS26600 operates at 4.2-60V. Internal UVLO rises at 14.25-15.75V and falls at 13.25-14.75V.
- U7 ILIM is 12k, nominally 1A. The stated 0.95-1.05A range becomes about 0.941-1.061A with a 1% resistor. Short pulses can exceed this during response delays.
- U7/U5 OVP uses 187k/10k, 0.1%. Nominal rising cutoff is 23.443V. Including comparator/resistor error and 100nA leakage gives 22.987-24.197V rising and 21.315-22.223V falling. That leaves recovery margin at 21V. OVP disconnects the load; it doesn't clamp the input.
- The TVS rating is 22V standoff, 35.5V maximum clamp at 16.9A for the stated pulse at 25°C. That is below the 60V/65V silicon limits but above the connector's listed 30V. Connector pulse tolerance is unknown. Temperature, pulse width and uneven TVS sharing still matter.
- Littelfuse 0466001.NR is 1A/63V, 1206. Nominal cold resistance is 0.075Ω; nominal melting I²t is 0.0423A²s. Neither gives a maximum clearing-energy guarantee. At 25°C the series allows up to 5s at 2× rating and 0.2s at 3× rating. Continuous current is rerated to 0.75A at 25°C and 0.60A in the manufacturer's 70°C example.

Each positive tile-to-tile path has two fuses. Don't fuse GND. Current can return through a different path, especially after a fuse opens. U7 only protects its local load, not a short on BUS_20V. Hub cutoff must handle every path still feeding a fault. See the [loop calculations](validation.md#power-calculations).

### Buck and 3.3V

LMR36520ADDAR switches at 400kHz with internal compensation. The 100k/24.9k, 0.1% feedback divider gives nominal 5.016V. Output capacitance is two 22µF parts; bootstrap is 100nF. C24 is the required 1µF VCC bypass. Don't load VCC externally. EN uses 100k/10k; U7 sets the effective startup threshold.

L1 is SRP7050TA-150M, 15µH ±20%. Ratings: 6A saturation at 20% inductance loss, 3.5A RMS at the stated 40°C rise, DCR up to 92mΩ at 25°C. The regulator's high-side limit is at most 3.6A. At 20V in and 5V out, calculated ripple is 0.625A peak-to-peak and peak current about 2.31A at 2A load. Winding loss at 2A and 92mΩ is about 0.37W before temperature correction.

The inductor is up to 5mm tall against nominal 6.5mm roof clearance. Solder, print and assembly tolerances aren't checked yet. Exact capacitor parts, DC-bias loss and ripple ratings are also unfinished. Follow TI's input-loop, bootstrap, feedback and thermal layout guidance.

AP2112 loss is 1.7V times logic current: 85mW at 50mA or 170mW at 100mA. R50, a 1k bleeder on 3.3V, adds about 11mW.

### Module power

U3 uses R53=3.32k, 0.1%, for nominal 1A limiting. C33=10nF slows startup; R54/R55=35.7k/10k, 0.1%, sets about 5.48V OVP. Reverse blocking covers a charged module output while local 5V changes.

U5 uses 24k for nominal 0.5A and C17=100nF. Its accuracy at 0.5A still needs confirmation; don't reuse the 1A accuracy figure. SHDN has a 10k pull-down to MODULE_RTN and a 1k series GPIO resistor.

Provisional load budgets are 0.8A at 5V and 0.4A at 20V. These aren't approved simultaneous loads or servo stall ratings. Both enables default low.

C7 is 6TPE120MAZB, 120µF/6.3V, rated at 85°C. Category voltage drops to 5V at 105°C, so it cannot cover full 5V-rail tolerance above 85°C. Check reflow limits, floor life and temperature.

### Signals and powered-off tiles

D1/D3, WS2812B-V5, share one RGB chain through U6, SN74AHCT1G125, and R3=330Ω. Check the actual LED variant and reflow orientation.

Each edge uses SN74LVC2G125DCUR buffers on local 3.3V. PB8 and a 10k pull-up disable them during reset. Ioff is specified up to ±10µA per I/O at VCC=0V and a 5.5V test input. That is leakage, not zero current.

UART series resistors are 2.2k, 1%, at least 0.25W in 1206; pull-ups are 47k. With an assumed 100pF load, both ends' 4.4k gives a 0.44µs time constant. Start testing at 115200 baud. Faster links, missing ground and actual contact capacitance aren't checked. The resistors don't make 20V on a signal pin safe.

U12, TMUX1511PWR, switches module SDA/SCL/CTRL/ID. U13 isolates bus sensing and North/East DETECT. Passive ID stays readable when logic is on. Module signals are 3.3V, with a 3.6V powered-off limit. They aren't 5V/20V tolerant. Receiver logic must use protected module 5V or have its own powered-off isolation, even on a motor module using 20V.

U14, TPS3808G01DBVR, senses module 5V through 103k/10k, 0.1%. Nominal threshold is 4.5765V; CT open gives a 12-28ms release delay, nominally 20ms. U15 enables SDA/SCL/CTRL only after valid 5V and a request from PB6. Wait for module startup too. Check dropout, supervisor tolerances and the module's own regulator together.

Bus sensing is 150k/10k with 10nF: 20V maps to 1.25V through U13. Off-state rail voltage, leakage and slow brownout still need measurements.

## Hub and power budget

The Hub is the only external supply. USB-C POWER should negotiate 20V/5A before enabling the bus, using a suitable 100W supply and 5A cable. USB-C DATA is separate, with CDC and vendor HID, and must not backfeed the computer or power input.

The calculations assume at most 1.5A per branch and 4.5A total, including tolerance, plus 5W for the Hub. At 21V that's 99.5W. These limits aren't implemented yet. Fuses, contacts, TVS energy and actual cutoff time still need checking together.

100W is an input ceiling, not power available on every tile. One path carries all loads downstream of it. At both provisional module budgets, 4W for module 5V + 0.6W RGB + 0.33W logic gives 4.93W. At assumed 85% buck efficiency that's 5.8W from the bus, plus 8W module 20V. This is the roughly 14W planning case. Twenty such loads exceed 280W before other losses.

STM32F405RGT6 is the Hub MCU candidate. ST DS8626 Rev 12 supports these LQFP64 pins:

- USART1: PB6 TX / PB7 RX, AF7.
- USART2: PA2 TX / PA3 RX, AF7.
- USART3: PB10 TX / PB11 RX, AF7.
- UART4: PA0 TX / PA1 RX, AF8.
- UART5: PC12 TX / PD2 RX, AF8.
- USART6: PC6 TX / PC7 RX, AF8.
- USB OTG FS: PA11 DM / PA12 DP, AF10; PA9 VBUS sense reserved.
- SWD: PA13 / PA14, NRST.
- SPI1 flash: PA5 SCK / PA6 MISO / PA7 MOSI, AF5; PA4 CS.
- I²C1 PD controller: PB8 SCL / PB9 SDA, AF4.
- Power supervision: PC0-PC3 ADC candidates; additional GPIOs for branch faults/enables.
- Clock: PH0 / PH1 reserved for HSE.

This is a pin check, not a finished Hub. RX DMA, transmit handling, USB clocks, VCAP, VBUS isolation, boot and debug still need review. STUSB4500 and external SPI flash are candidates; flash capacity is undecided.

## Datasheets

- [TI TPS2660, SLVSDG2G](https://www.ti.com/lit/ds/symlink/tps2660.pdf), pins, RTN/GND separation, limits, MODE and PWP land pattern.
- [TI LMR36520, SNVSBF0C](https://www.ti.com/lit/ds/symlink/lmr36520.pdf), pinout, feedback, current limit and DDA0008B package.
- [TI TPS25947, SLVSFC9C](https://www.ti.com/lit/ds/symlink/tps25947.pdf), true reverse blocking, variant, pins and RPW0010A copper/stencil drawings.
- [Littelfuse 466 fuse series](https://www.littelfuse.com/assetdocs/littelfuse_fuse_466_datasheet?assetguid=dbe9bcd7-6072-4adf-bf5b-d33e52a6b90f), 2023 data table, opening times and temperature rerating.
- [Vishay SMBJ series, document 88392](https://www.vishay.com/docs/88392/smbj.pdf), clamp conditions and SMB dimensions.
- [TI SN74LVC2G125, SCES204Q](https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf), pinout, leakage and electrical levels.
- [TI TMUX1511, SCDS390B](https://www.ti.com/lit/ds/symlink/tmux1511.pdf), 3.6V powered-off limit and PW14 pinout.
- [TI TPS3808, SBVS050N](https://www.ti.com/lit/ds/symlink/tps3808.pdf), adjustable threshold, delay and power-off input ratings; [TI SN74LVC1G08](https://www.ti.com/lit/gpn/sn74lvc1g08), fail-safe logic and Ioff.
- [Bourns SRP7050TA](https://www.bourns.com/docs/product-datasheets/srp7050ta.pdf), electrical table and recommended lands. The package drawing was inspected in a manufacturer-authored distributor mirror because direct download was unavailable.
- [Panasonic 6TPE120MAZB](https://industrial.panasonic.com/ww/products/pt/poscap/models/6TPE120MAZB), [TPE catalog](https://industrial.panasonic.com/cdbs/www-data/pdf/AAA8000/AAA8000C36.pdf) and [B2 land pattern](https://industrial.panasonic.com/cdbs/www-data/pdf/AAA8000/ast-ind-139507.pdf), including temperature-dependent voltage and polarity.
- [Diodes AP2112](https://www.diodes.com/datasheet/download/AP2112.pdf), retained LDO; [TI SN74AHCT1G125](https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf), RGB buffer; [Worldsemi V5 sheet](https://www.world-semi.co.kr/_files/ugd/89cd03_1023b0e9d135431aa1e6491bfc318112.pdf), LED variant and timing.
- [WCH datasheet V1.7](https://akizukidenshi.com/goodsaffix/CH32X035.pdf), [reference manual V1.9](https://ch32-riscv-ug.github.io/CH32X035/datasheet_en/CH32X035RM.PDF), [WCH remap header](https://github.com/openwch/ch32x035/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32x035_gpio.h) and [ST DS8626 Rev 12](https://www.st.com/resource/en/datasheet/stm32f405rg.pdf) for the MCU allocations.
