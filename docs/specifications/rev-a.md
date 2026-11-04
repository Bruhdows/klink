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

The native Hub project in `hardware/electronics/hub/` contains 214 components on ten schematic pages. Six instances share `port-power.kicad_sch`; `shutdown.kicad_sch` implements the common fault logic. Outputs and current monitors terminate at copper test pads. Tile connectors, the main Hub supplies, MCU, USB data and storage remain unfinished. There is no Hub PCB.

### Input

J1 is GCT USB4105-GF-A. The [USB4105 A3 specification](https://gct.co/files/specs/usb4105-spec.pdf) rates its four VBUS contacts collectively at 5A, with a 30°C shell-temperature-rise test. The assigned stock land pattern still needs production assembly review.

U1 is STUSB4500QTR. Program and read back two PDOs before load testing: PDO1 5V/0.5A, PDO2 20V/5A; PWR_OK_CFG=10b, POWER_ONLY_ABOVE_5V=1, REQ_SRC_CURRENT=0. POWER_OK2 reports a match to programmed PDO2, not a measured current capability. The voltage guard rejects factory PDO2 at 15V. Use a 100W source and marked 5A cable. Programming and interoperability are untested. CC1DB/CC2DB join their CC pins. Internal regulator outputs only feed bypass capacitors. R1=470Ω, 1%, limits discharge to 47.3mA at 22V. J2 supplies programming I/O; do not power pin 1 externally.

U2 TPS26630RGER uses CSD19537Q3 and onsemi BSS138LT1G in TI's reverse-blocking circuit. The pull-down FET has the required ±20V gate rating and 50pF maximum input capacitance at its stated test point; do not substitute a different BSS138 solely by name. Q1 source connects to IN_SYS and drain to IN; Q2 source also connects to IN_SYS. R8 is WSL2512R0100FEA, 10mΩ/1W, with Kelvin takeoffs at the inner land edges. U4 INA301A1IDGKR and 10.5kΩ, 0.1%, 25ppm/K set nominal 4.2A input trip. The industrial I in the INA301 ordering code is required.

The initial-tolerance calculation gives about 4.014–4.394A through 125°C part temperature. It includes comparator/amplifier error, CMRR, PSRR, drift, resistor tolerance and TCR; it assumes at most 10K between shunt terminals and excludes aging. At 21V the upper static threshold is 92.26W. R9/R10=135k/10k give 16.921–17.884V rising UVLO. This accepts a low-end 20V source with cable drop while rejecting 15V. R11/R12=172k/10k give 21.236–22.451V rising OVP. Including a provisional 10mA upstream allowance gives about 98.86W at the upper OVP corner. These are static initial-tolerance bounds, not peak or lifetime guarantees.

The 100W PD input target remains. Nominal trip is 84W at 20V; the minimum calculated threshold permits about 80.28W at 20V or 76.27W at 19V before Hub use and losses. This revision cannot guarantee 100W usable output. R13=3kΩ, 0.1%, sets the independent backup limit to 5.574–6.427A, above the precision breaker's overdrive point. It is not a continuous USB allowance. The comparator and hardware latch must interrupt it first. TPS26630's 45A short-protection figure is typical and does not bound peak current.

U2 MODE is open for latch-off, PGTH grounded for controlled recovery slew, and C8=100nF gives nominal 41.6ms startup at 20V. TPS70933DBVR supplies control logic only. C9 is now TDK C3216X7R1H106K160AC, 10µF/50V X7R in 1206, to give more margin above the regulator's 2µF effective minimum. Confirm bias, aging and stability during qualification. TPS3808G30DBVR supervises this rail. Its calculated maximum release is 2.903V, below the conservative 3.174V control-supply floor after regulation allowances; minimum assertion is 2.748V, above INA301's 2.7V minimum. Reset inhibits all switches and clears both hardware latches.

### Outputs and common shutdown

Each port has TPS26630RGER, the same reverse-blocking FET pair, a 10mΩ WSL shunt and INA301A1IDGKR. A 10kΩ precision limit resistor gives nominal 4A trip, calculated 3.820–4.187A over the same temperature/error assumptions. The 1mV sense-overdrive point is below the backup limiter's minimum. Port ILIM is 3kΩ, MODE open, dVdT 22nF. C103 is TDK C2012C0G1H223J125AA, ±5% C0G, with manufacturer reflow lands. Its calculated initial/temperature minimum is 20.84nF, above the device's 10nF minimum; nominal ramp is about 9.15ms at 20V. Output monitoring uses 130k/10k at PGTH; FLT and the open-drain PGOOD output share HEALTH_N. Each port has a 10kΩ/0.25W output bleeder, 22kΩ fault pull-ups and local bypassing. The input stage also has a bleeder. RGER and RGET have the same electrical/package design; only reel size differs.

Any input or port overcurrent sets the shared SN74LVC74APWR fault latch without startup blanking. All six HEALTH_N signals and input FLT are checked after a hardware startup allowance. TPS3808G01DBVR senses INPUT_ENABLE; 100kΩ from CT to VDD selects 180–420ms. The deadline therefore expires even if a short prevents HUB_20V rising. SN74HCS11PWR Schmitt AND gates accept the slowly rising open-drain fault flags. SN74LVC2G17 shapes the aggregate and supervisor outputs before the remaining fast logic. The PD flag uses SN74LVC1G14DBVR. Control-good is buffered before it enables power or releases comparator/latch reset. The second flip-flop remembers that the allowance expired. A collapse of the switched rail or timer output cannot disarm health checking or release a fault.

RUN_OK gates the input switch and all six port SHDN pins together. A reporting port cannot leave another feeding branch enabled. The latch stays powered upstream of the master switch; removing switched power does not reset it. SW1 or control-power loss clears the latches. At the specified sense overdrive and logic loads, overcurrent shutdown is approximately 2.7µs including the eFuse's maximum 1.5µs SHDN delay. Output-power-good deglitch can add up to 4µs to voltage-fault detection. INA301's published timing table uses 25°C test conditions; this is not a guaranteed hot shutdown bound. Neither timing figure bounds fault-current overshoot. Capacitive loading, small overdrive and startup need bench checks. A low-current resistive bridge below every threshold remains indistinguishable from an ordinary load. Loss of a sole ground contact can also leave a signal-return path without reaching a power trip. The existing UART resistors and powered-off buffers do not qualify that fault; field-I/O survival remains a network-release blocker.

D8 and each output have SMBJ22A-E3/52 prototype clamps. Their 35.5V maximum clamp is specified at 16.9A, 25°C, for the stated pulse, below the power switches' voltage limits but close to the current monitors' 36V operating range and 40V absolute maximum. Hot clamp voltage, layout overshoot and the connector's pulse withstand remain unqualified. These clamps do not protect the upstream PD controller's 28V limit. Connector-side surge protection and backup-fuse coordination remain routing blockers.

### Distribution recommendation

Use a low-resistance 20V mesh supplied only by the six Hub outputs, with every positive and return path rated for at least 5A continuous at its qualified temperature, with a 4.5A distribution design current. This covers steady current concentration when a path opens, assuming only the Hub supplies power. The 5A selection leaves margin above the initial 4.394A trip bound; lifetime drift and contact wear still need qualification. Keep F1 and local/module protection. Remove or bypass F2-F5 only in a separately verified tile revision after contact, copper and fault-pulse qualification. The present tile still has its original 1A transit fuses and is not released for this architecture. No main-bus routes have been added.

The old mesh has 0.29Ω per loop link: 0.15Ω in two transit fuses, plus assumed 0.10Ω contacts and 0.04Ω copper. At 20 tiles × 3W, even the optimistic 0.15A/tile current floor gives 3A at the first connection, a 9.719V far-end drop and at least 20.559W loss. Each first contact dissipates at least 0.45W and its 1A edge fuse at least 0.675W. The constant-power model tightens its voltage bound below zero in three steps. Its numerical positive-DC boundary is about 1.803W/tile, well beyond the fuse's permitted continuous current. It is not a usable load rating.

Lower-resistance contacts with the same 1A fuses leave most of that problem intact. Removing fuses while retaining the old assumed contact resistance gives a positive 20V solution, but far-end voltage is about 12.28V with the current Hub allowances, below the tile startup threshold and outside current limits. Higher fuse ratings alone neither fix contact heating nor guarantee fuse clearing under a source limited below the fuse rating.

An 80mΩ maximum hot loop target is a practical V1 objective: about 30mΩ per power/return contact plus 20mΩ for both copper paths and joints. It is a requirement, not a verified SAMZO capability. Under the model's 0.12Ω common input, 0.12Ω port switch allowance, 0.225Ω local path and 5W Hub load, 16–20 tile 3W grids work with center, edge or corner placement at 18.5–20V. All 297 single-path opening cases across the three 20-tile grids at 19V remain inside the modeled limits. These are DC calculations, not cold-start or pulse qualification.

Long chains need a separate load budget. At 19V an 80mΩ loop permits only about 2.393W/tile for twenty equal loads before a modeled limit; use less for operating margin. Sixteen tiles at 3W fit the same resistance target at 19V. Twenty tiles at 3W require roughly a 40mΩ loop target for margin at 19V: calculated far-end voltage 16.585V, source current 3.788A and network/input-path losses 6.973W. A single SAMZO contact's listed 30mΩ does not establish that target. Parallel contacts or a lower-resistance connector need separate mechanical, sharing and single-contact-loss qualification.

Keeping the fused mesh with topology-dependent budgets is a lower-change fallback, but has substantial restrictions. At 19V and the 70°C fuse budget, the model gives approximately 2.79W/tile centrally, 2.11W at an edge, 1.46W at a corner and 0.53W in a twenty-tile chain, before operating margin. Opening one central Hub feed can raise a normal 20V, 3W/tile path from 0.612A to 0.790A, above even the 25°C fuse budget. Firmware load allocation cannot substitute for that missing hardware margin.

Prefer extra grid adjacencies or a ring that reaches another Hub face over a long singly fed chain; the marble path need not equal the electrical path. No external injector is needed. A directional power tree adds per-tile switching and still has the chain's voltage drop. A 48V bus would require a Hub boost stage, higher-voltage contacts/protection and revised module power, so it is not selected for V1. Parallel power/return contacts can reduce resistance, but require more spring bodies and wider carriers; do not multiply current ratings by contact count.

For copper planning, two parallel 35µm layers, each 4mm wide with 80mm combined path length, calculate to 6.47mΩ per conductor at 100°C and 0.131W at 4.5A. That excludes necks, vias, joints and manufacturing tolerance. Meet the complete hot resistance budget, confirm minimum copper thickness, and validate temperature rise before routing approval. The calculation is not a trace ampacity qualification.

Directly connected output capacitance is nominally 6µF at the Hub plus 4µF across twenty tile buses. At 21V and +20% capacitance this stores 2.646mJ. A source-free 40mΩ lumped RC example has 525A initial current and 0.0662A²s, above the fuse's nominal 0.0423A²s. This illustrates why a 4.5A DC limit or small energy figure gives no contact pulse rating. Real inductance, ESR, distribution and fuse minima are missing. Upstream Hub capacitors can feed during switch delay; local 20V capacitors, 5V rails and motors add energy subject to finite reverse-blocking response. Do not credit equal TVS sharing or nominal fuse I²t as guaranteed clearing. Measure the fault waveform and qualify contacts, finish, copper and clamps against it.

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

This is a pin check, not a finished Hub. RX DMA, transmit handling, USB clocks, VCAP, VBUS isolation, boot and debug still need review. STUSB4500 is implemented; external SPI flash remains a candidate; flash capacity is undecided.

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

Hub input references: [STUSB4500 DS12499 Rev 8](https://www.st.com/resource/en/datasheet/stusb4500.pdf), [TPS2663 SLVSE94G](https://www.ti.com/lit/ds/symlink/tps2663.pdf), [INA301 SBOS713A](https://www.ti.com/lit/ds/symlink/ina301.pdf), [TPS709 SBVS186H](https://www.ti.com/lit/ds/symlink/tps709.pdf), [CSD19537Q3 SLPS549B](https://www.ti.com/lit/ds/symlink/csd19537q3.pdf), [Vishay WSL document 30100](https://www.vishay.com/docs/30100/wsl.pdf), [TNPW document 31006](https://www.vishay.com/docs/31006/tnpw.pdf), [Panasonic ERA6AEB1052V](https://industrial.panasonic.com/ww/products/pt/high-precision-chip-resistors/models/ERA6AEB1052V), [SN74LVC1G04](https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf) and [SN74LVC1G11](https://www.ti.com/lit/ds/symlink/sn74lvc1g11.pdf).

Additional Hub references: [SN74LVC74A SCAS287W](https://www.ti.com/lit/ds/symlink/sn74lvc74a.pdf), [SN74LVC2G17 SCES381N](https://www.ti.com/lit/ds/symlink/sn74lvc2g17.pdf) and [TDK C3216X7R1H106K160AC characterization](https://product.tdk.com/info/en/documents/chara_sheet/C3216X7R1H106K160AC.pdf).

Schmitt and driver references: [SN74HCS11 SCLS790C](https://www.ti.com/lit/ds/symlink/sn74hcs11.pdf), [SN74LVC1G14 SCES218AA](https://www.ti.com/lit/ds/symlink/sn74lvc1g14.pdf) and [onsemi BSS138LT1/D Rev 15](https://www.onsemi.com/pdf/datasheet/bss138lt1-d.pdf).

Port ramp capacitor: [TDK C2012C0G1H223J125AA](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012C0G1H223J125AA), capacitance tolerance, C0G temperature coefficient and reflow lands.
