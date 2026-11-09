# Rev A electronics

Rev A uses 20V between tiles. The old 5V bus needed too much current for the larger loads. Each tile now makes its own 5V and 3.3V. Don't join those local rails between tiles.

The schematic has source protection, switched module power, four UART links and two RGB LEDs. The PCB has all 118 supported circuit footprints placed, a mechanical board body and partial power/signal routing. It still needs connector checks, protection tests and routing. See the [pinouts](interfaces.md).

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

Each positive tile-to-tile path has two fuses. Don't fuse GND. Current can return through a different path, especially after a fuse opens. U7 only protects its local load, not a short on BUS_20V. Hub cutoff must handle every path still feeding a fault. See the [distribution analysis](#distribution-recommendation).

### Buck and 3.3V

LMR36520ADDAR switches at 400kHz with internal compensation. The 100k/24.9k, 0.1% feedback divider gives nominal 5.016V. Output capacitance is two selected 22µF/25V X7R parts in 1210; bootstrap is 100nF. C24 is the required 1µF VCC bypass. Don't load VCC externally. EN uses 100k/10k; U7 sets the effective startup threshold.

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

U8 is SN74LVC244APWR: one octal buffer handles four TX and four RX paths. Both output enables connect to PB8 and its 10k reset pull-up. This replaces four dual packages and three redundant bypass capacitors without changing neighbor pinouts or series protection. Its Ioff limit is ±10µA per I/O at 85°C, rising to ±20µA at 125°C, tested with VCC=0V and 5.5V on an I/O. This does not qualify a missing-ground or 20V signal fault.

UART series resistors are 2.2k, 1%, at least 0.25W in 1206; pull-ups are 47k. With an assumed 100pF load, both ends' 4.4k gives a 0.44µs time constant. Start testing at 115200 baud. Faster links, missing ground and actual contact capacitance aren't checked. The resistors don't make 20V on a signal pin safe.

U12, TMUX1511PWR, switches module SDA/SCL/CTRL/ID. U13 isolates bus sensing and North/East DETECT. Passive ID stays readable when logic is on. Module signals are 3.3V, with a 3.6V powered-off limit. They aren't 5V/20V tolerant. Receiver logic must use protected module 5V or have its own powered-off isolation, even on a motor module using 20V.

U14, TPS3808G01DBVR, senses module 5V through 103k/10k, 0.1%. Nominal threshold is 4.5765V; CT open gives a 12-28ms release delay, nominally 20ms. U15 enables SDA/SCL/CTRL only after valid 5V and a request from PB6. Wait for module startup too. Check dropout, supervisor tolerances and the module's own regulator together.

Bus sensing is 150k/10k with 10nF: 20V maps to 1.25V through U13. Off-state rail voltage, leakage and slow brownout still need measurements.

## Hub and power budget

The native Hub has 350 components on fifteen schematic pages. PD input, master breaker, six protected outputs, common shutdown, supplies, MCU, six UART interfaces, USB data and SPI flash are connected. Production tile connectors remain unresolved; power, UART and detect outputs use test pads. There is no Hub PCB or working Hub firmware.

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

Retain the fused 20V mesh for V1. The realistic base loads below do not justify replacing the 1A transit fuses or doubling power contacts to satisfy a uniform 3W stress case. Keep F1, independently switched module supplies and the Hub's common hardware shutdown. Use grid adjacencies for motorized layouts; normal positive-path current must remain below the fuse's 0.6A budget at 70°C, with operating margin and redistribution included. Do not claim short-time contact capability from its listed continuous rating. Connector pulse withstand, missing-ground signal survival and raw-input surge coordination still block routing and release.

The 80/40mΩ budgets below remain future high-load targets and stress comparisons. Their 104/137/277mΩ carrier calculations use candidate 9mΩ fuses, not the present 75mΩ nominal 1A parts. With the retained fuses, the corresponding cold/hot/degraded loop estimates are about 236/335/475mΩ. Hot fuse resistance and degraded contacts are assumptions requiring measurement.

Prefer extra grid adjacencies or a ring that reaches another Hub face over a long singly fed chain; the marble path need not equal the electrical path. No external injector is needed. A directional power tree adds per-tile switching and still has the chain's voltage drop. A 48V bus would require a Hub boost stage, higher-voltage contacts/protection and revised module power, so it is not selected for V1. Parallel power/return contacts can reduce resistance, but require more spring bodies and wider carriers; do not multiply current ratings by contact count.

For copper planning, two parallel 35µm layers, each 4mm wide with 80mm combined path length, calculate to 6.47mΩ per conductor at 100°C and 0.131W at 4.5A. That excludes necks, vias, joints and manufacturing tolerance. Meet the complete hot resistance budget, confirm minimum copper thickness, and validate temperature rise before routing approval. The calculation is not a trace ampacity qualification.

### Complete link budget

The complete link budget includes both mating contacts, two carriers, their attachment and contact solder joints, vias, main-board copper and two positive transit fuses. It is a sensitivity calculation, not a measured minimum/nominal/maximum specification. Actual worst-case SAMZO resistance remains unbounded by available evidence.

At 25°C, an illustrative carrier route is 6mm × 1.4mm × 35µm per board, one layer, on each of two boards. Per conductor, 80mm of main-board copper on two 4mm-wide 35µm layers adds 5.023mΩ; both carriers add 4.305mΩ; two 0.3mm finished-hole vias with 25µm plating add 2.204mΩ; four contact/attachment joints at an assumed 0.25mΩ add 1mΩ. Four further solder joints for the two positive fuses add 1mΩ to the loop. Each spring has two solder feet; their internal current sharing is not characterized, so the joint count is a conservative lumped allowance. These are proposed dimensions, not existing tile routes. Spreading, necks and finish are additional uncertainties. The contact figure includes the mated interface and spring body once; do not count the drawing's resistance as two interfaces per conductor.

### Transit protection choices

The [Littelfuse 466 datasheet](https://www.littelfuse.com/assetdocs/littelfuse_fuse_466_datasheet?assetguid=dbe9bcd7-6072-4adf-bf5b-d33e52a6b90f) lists 0466005.NR at 11mΩ nominal cold and 1.6A²s nominal melting energy. Its 5A rating becomes 3.75A continuous at 25°C and 3A in the 70°C example, below the 4.5A path requirement. It is not a suitable drop-in transit replacement. PTCs add hot resistance and thermal retry behavior; they do not solve the resistance or shared shutdown problem.

The [451/453 datasheet, revision 2025-12-01](https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1) lists 0451007.MRL at 7A, 9mΩ nominal cold, 10.32A²s nominal melting energy, 125V and 400A interrupting capability at 32VDC. It is physically larger than 1206. Applying the standard 0.75 continuous factor and a conservative 0.90 temperature screening factor gives 4.725A; confirm the nominal rerating curve and actual enclosure temperature with the manufacturer. This is a measurement candidate, not a selected replacement. A normal Hub-fed short cannot be expected to clear a 7A fuse: the 4.394A input trip is below its rating, and the guaranteed 2× opening point requires 14A. Nominal melting I²t is not maximum clearing I²t.

Larger fuses would serve only as coordinated backup for gross faults; the input breaker and shared output shutdown must clear ordinary network shorts. Approval requires measured peak current, clearing time and integrated I²t at each feeding path, including stored energy, reverse-blocking delay and a failed switching element. No fuse removal, higher rating or contact pulse rating follows from the present DC model. Four per-edge active breakers would add switches, sense circuitry and bidirectional feed/fault logic to every tile; even two 31mΩ typical TPS26630 paths add 62mΩ before contacts and return copper. They are not a low-cost drop-in solution.

### Hub review limits

Six nominal 4A output breakers do not provide 24A. The shared input threshold remains 4.014–4.394A including Hub consumption downstream of its shunt. At 19V, reserving 5W for the Hub and a further provisional 10mA gives only about 3.741A at the minimum input trip for all ports combined, before path-loss corrections and operating margin. A single branch can therefore trip the input before reaching its own upper threshold; that is intentional system shutdown, not selective branch discrimination. Equal-load grids fit more readily than singly fed chains. Keep the precision input monitor and shared latch; replacing them with the eFuse's 6A backup limit would violate the PD budget. The seven precision monitors and reverse-blocking stages remain cost drivers, but no safe component deletion is established by ERC or the stable-state logic tests. Grounded port UVLO selects the TPS26630 internal 15V threshold, as specified in TI table 5-1; it does not disable the port.

Directly connected output capacitance is nominally 6µF at the Hub plus 4µF across twenty tile buses. At 21V and +20% capacitance this stores 2.646mJ. A source-free 40mΩ lumped RC example has 525A initial current and 0.0662A²s, above the fuse's nominal 0.0423A²s. This illustrates why a 4.5A DC limit or small energy figure gives no contact pulse rating. Real inductance, ESR, distribution and fuse minima are missing. Upstream Hub capacitors can feed during switch delay; local 20V capacitors, 5V rails and motors add energy subject to finite reverse-blocking response. Do not credit equal TVS sharing or nominal fuse I²t as guaranteed clearing. Measure the fault waveform and qualify contacts, finish, copper and clamps against it.

100W is an input ceiling, not power available on every tile. One path carries all loads downstream of it. At both provisional module budgets, 4W for module 5V + 0.6W RGB + 0.33W logic gives 4.93W. At assumed 85% buck efficiency that's 5.8W from the bus, plus 8W module 20V. This is the roughly 14W planning case. Twenty such loads exceed 280W before other losses.

### Controller and supplies

Two SN74LVC244APWR packages buffer the six links, replacing six dual buffers and four bypass capacitors. U70 STM32F405RGT6 uses the six UART pin pairs and independent RX/TX DMA streams in [uart-allocation.csv](../../hardware/electronics/hub/uart-allocation.csv). SPI1 uses PA5/PA6/PA7 with PA15 chip select; ADC1 uses PC0-PC5 and PA4. DMA2 streams 0/3 serve SPI1, stream 4 serves ADC1; none conflicts with the UART allocation. DMA buffers must use SRAM1/2, not CCM. The 8MHz Abracon ASE oscillator uses HSE bypass, PLL M=8/N=336/P=2/Q=7 for 168MHz core and 48MHz USB. VCAP has two 2.2µF capacitors; VDDA shares the main 3.3V source with local bypassing. SWD, reset, BOOT0/BOOT1 and PA9/PA10 ROM serial recovery are accessible. W25Q32JVSSIQ provides 4MB program storage; atomic update and execution firmware remain unfinished.

U60 protects an auxiliary supply upstream of the tile master but downstream of its current shunt. Nominal limit is 0.3A; its isolated AUX_RTN must not join GND. LMR36520 makes 5V and AP2112 makes Hub 3.3V. This keeps USB reporting alive after a tile-bus trip. U78 supervises the MCU rail; U79 uses Schmitt inputs to qualify MCU_RESET_N with CONTROL_GOOD; its fixed-low IN1 selects the AND function. Its MAIN_READY output drives the interface enables and inhibits the master and all ports while either rail is invalid. The reporting interfaces remain enabled after a latched tile-bus fault. Clearing control reset through SW1/Q70 temporarily disconnects USB; software must tolerate re-enumeration. Main-rail failure therefore cannot leave the grid powered merely because control logic remains alive. The 5W Hub allowance in network calculations is a reserve, not a measured draw. Reserve 150mA for the 3.3V logic rail; at 5V input its LDO loss is about 0.255W. Enclosure temperature and copper must be checked before releasing that thermal budget.

The data USB-C port has separate CC pull-downs, USBLC6 protection, TS3USB30E isolation and a transistor VBUS detector. It does not power Hub rails. The switch selects the MCU only after MAIN_READY asserts and disables when VBUS is absent. Firmware must configure a self-powered HID/CDC composite device and use the external VBUS indication. The four bidirectional FS endpoints fit EP0 control, EP1 CDC bulk IN/OUT, EP2 HID IN/OUT and EP3 CDC notification IN. A preliminary RX/TX allocation of 128/16/64/32/16 words uses 256 of the controller’s 320 FIFO entries; validate descriptors and traffic on hardware. TCA9535 at address 0x20 reports sixteen hardware fault/status inputs; three TMUX1511 packages isolate I2C and seven analog monitors from the independently powered control rail. Keep all expander ports as inputs. None participates in the fault-clearing decision.

### Tile and kit consumption

The component-based budget separates base electronics from modules. WCH table 3-6 gives 2.2mA typical at 8MHz and 4.2mA at 48MHz, at 3.3V/25°C, without a guaranteed maximum operating-current value. The V5 LED sheet gives 0.6mA quiescent and 12mA channel test conditions. Including LDO loss, the 1k bleeder, buffers, switches, pull-ups, protection dividers and assumed buck efficiencies gives about 0.078W idle, 0.197W with 25% white lighting, and 0.504W at full white. A 20mA MCU/20mA-per-channel/70%-efficiency planning case is about 1.06W. These are estimates; supplied silicon, firmware and efficiency need measurements. Uniform 3W remains a separate stress test.

At 19V, base electronics plus a reserved 5W Hub use approximately 8.2/8.9/11.3W for 16/20/32 moderately lit tiles. Full RGB gives about 13.1/15.2/21.4W before module loads. A planning kit with one running elevator, two 0.2A servos and four 20mA sensor modules uses roughly 14.6/15.4/17.7W in the tested grids. Servo currents are hypotheses for the still-unselected servos; the 1A stall hypothesis exceeds the declared 0.8A module budget.

The 16/20/32-tile center/edge/corner grid sweep covers 1026 single positive, return and whole-connection openings with that moderately lit running kit placed near the Hub. All fit the modeled voltage/current limits; maximum positive current is about 0.374A. This does not qualify thermal behavior or faults. A 32-tile chain fails the hot transit-fuse budget with the same kit; starting the motor with other modules active can exceed it even in shorter chains. Prefer a grid, put the elevator near a Hub feed and stagger actuators. Firmware load admission and brightness limits still need implementation. Fuses are the hardware overload backstop, not an automatic topology-aware continuous-current controller.

### Elevator

The native prototype in `hardware/electronics/elevator/` has 47 components. It keeps the standard eight module signals and uses a service header while production mating geometry is unresolved. LMR36510ADDAR converts switched module 20V to 12V through SRP7050TA-330M. Its 2.4A maximum high-side limit is below the inductor's 3.5A room-temperature saturation figure; minimum inductance also clears TI's subharmonic criterion. Hot behavior still needs checking. A 100µF/25V hybrid bulk capacitor and SMBJ13A contain local energy; braking and reverse-blocking delay require waveform tests.

DRV8876PWPR gives nominal 0.346A current regulation with 0.1%, 25ppm/K limit resistors. The initial static calculation gives approximately 0.32-0.38A through the stated temperature/error assumptions; chopping overshoot is excluded. ATtiny404-SSN reads current, rail voltage and a TCST2103 index sensor, controls direction/PWM/sleep, and reads the normally closed stop loop. PB0/PB1 provide I2C, PB2 provides TCA0 WO2 PWM, and UPDI remains available. Firmware must default off, enable BOD/watchdog, reject stale commands, and latch off on stall, lost progress or abnormal rail voltage. A buildable ATtiny404 implementation is now in [firmware](../../firmware/README.md); its host safety model is tested, but the image has not run on hardware. Do not treat a successful build as motor qualification.

The selected mechanical prototype motor remains [Pololu 3044](https://www.pololu.com/product/3044): 12V, 130rpm/80mA no-load, with manufacturer-extrapolated 3.0kg·cm/0.75A stall figures. These are not continuous ratings. The [manufacturer drawing](https://www.pololu.com/file/0J949/micro-metal-gearmotors-dimensions.pdf) gives a 10×12mm gearbox cross section, 25.6mm maximum body length and a 3mm D shaft projecting 9mm. The printed saddle uses 0.2mm body clearance per side and a separate screw clamp.

The editable prototype in `hardware/cad/elevator/elevator.scad` uses two 80mm cells, a 288mm lift and a 394mm frame above the tile. A six-pocket wheel directly drives a 24mm-pitch printed pin chain at 24mm pitch radius. Thirty links alternate fifteen plain links and fifteen spoon carriers; M2×16 hinge screws leave drive tips behind the chain. There is one motor and no additional gearbox or belt. The idler has a 623ZZ bearing, an M3 axle and removable spacers. Bearing seats, pin engagement, shaft clamping, noise and wear need printed samples.

Target output speed is 20–35rpm under closed-loop PWM. At 20rpm, the nominal chain advance is 48mm/s and carrier throughput is one marble per second. Six optical slots give one progress edge every 0.5s at that speed. The optical flag is 1.5mm thick; the TCST2103 bracket and actual alignment still need implementation. Jam timing must come from startup and running tests. A printed passive pawl is included for anti-rollback trials, not qualified as a safety brake.

Assume eight 16mm glass marbles at 2500kg/m³, 50g of rising chain/carrier/fastener mass, 50% mechanical efficiency and 0.005N·m friction. Total rising mass is 92.9g. Required torque is `0.0929 × 9.81 × 0.024 / 0.5 + 0.005 = 0.0487N·m`. Linear interpolation from the motor's no-load/stall figures suggests about 0.191A at that torque. This is a planning estimate; it does not predict PWM ripple, breakaway force or jams. The existing 0.32–0.38A driver limit gives nominal starting headroom, but it does not permit a sustained regulated stall.

The feed forks match the existing track's nominal 13.5mm marble-center height. Stationary guides retain the marble on the narrow spoon; discharge rails pass beside the spoon to strip it at the top. The exit center is 353.5mm above the module mounting plane, matching a track on seventeen 20mm levels. Pickup, metering and release are unproven. Frame and guards split into pieces no taller than 200mm. The PCB sits at Z=90mm with side notches clearing the chain runs, and remains accessible from the rear.

Reserve about 3.34W bus input for running, using a conservative 0.20A motor allowance, and 6.7W at current-limited startup. Unrestricted stall remains a rejected overload near 14W. Conversion efficiency, braking energy and hot bridge resistance still need measurements.

### PCB layout

The tile has a closed 68×68mm board body, four mounting holes and all 118 supported circuit footprints placed. J3-J7 remain unassigned. Its four-layer draft uses both inner layers as GND references. Local buck input/return, bootstrap, VCC, feedback and output paths are routed, along with selected signals and underside debug access. The shared 20V bus, source/module protection connections, most UARTs and module interface are unfinished. The source and module RTN thermal pads remain separate from GND.

Outer-copper routing assumes 35µm copper. The local converter uses 0.8mm supply/output paths and a 1mm switch-to-inductor path. The 15.5mm, 0.8mm-wide path to the LDO calculates near 9.5mΩ at 20°C, excluding pads and contacts. That is about 9.5mV at 1A, not a temperature qualification. Five standard ground vias spread the regulator return/heat into the planes. The MCU ground via at KiCad (100.9,100.5) lies in its exposed pad and requires a filled/capped process or an assembler-approved alternative. Quote that treatment for all sixteen tiles before ordering.

The Hub has a four-layer PCB started with USB access, six grid-facing regions, initial protection/supply placement and local MCU, VCAP, oscillator and bypass routing. Only 79 of 350 circuit footprints are placed. The elevator has all 47 circuit footprints placed on a notched 60×44mm board; it is unrouted. USB differential routing waits for a selected fabrication stack. Thermal review, copper distribution and assembly review remain open on all three boards.

## Datasheets

- [TI TPS2660, SLVSDG2G](https://www.ti.com/lit/ds/symlink/tps2660.pdf), pins, RTN/GND separation, limits, MODE and PWP land pattern.
- [TI LMR36520, SNVSBF0C](https://www.ti.com/lit/ds/symlink/lmr36520.pdf), pinout, feedback, current limit and DDA0008B package.
- [TI TPS25947, SLVSFC9C](https://www.ti.com/lit/ds/symlink/tps25947.pdf), true reverse blocking, variant, pins and RPW0010A copper/stencil drawings.
- [Littelfuse 466 fuse series](https://www.littelfuse.com/assetdocs/littelfuse_fuse_466_datasheet?assetguid=dbe9bcd7-6072-4adf-bf5b-d33e52a6b90f), 2023 data table, opening times and temperature rerating.
- [Vishay SMBJ series, document 88392](https://www.vishay.com/docs/88392/smbj.pdf), clamp conditions and SMB dimensions.
- [TI SN74LVC244A](https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf), consolidated tile buffer; [TI SN74LVC2G125, SCES204Q](https://www.ti.com/lit/ds/symlink/sn74lvc2g125.pdf), pinout, leakage and electrical levels.
- [TI TMUX1511, SCDS390B](https://www.ti.com/lit/ds/symlink/tmux1511.pdf), 3.6V powered-off limit and PW14 pinout.
- [TI TPS3808, SBVS050N](https://www.ti.com/lit/ds/symlink/tps3808.pdf), adjustable threshold, delay and power-off input ratings; [TI SN74LVC1G08](https://www.ti.com/lit/gpn/sn74lvc1g08), fail-safe logic and Ioff.
- [Bourns SRP7050TA](https://www.bourns.com/docs/product-datasheets/srp7050ta.pdf), electrical table, body height and recommended lands.
- [Panasonic 6TPE120MAZB](https://industrial.panasonic.com/ww/products/pt/poscap/models/6TPE120MAZB), [TPE catalog](https://industrial.panasonic.com/cdbs/www-data/pdf/AAA8000/AAA8000C36.pdf) and [B2 land pattern](https://industrial.panasonic.com/cdbs/www-data/pdf/AAA8000/ast-ind-139507.pdf), including temperature-dependent voltage and polarity.
- [Diodes AP2112](https://www.diodes.com/datasheet/download/AP2112.pdf), retained LDO; [TI SN74AHCT1G125](https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf), RGB buffer; [Worldsemi V5 sheet](https://www.world-semi.co.kr/_files/ugd/89cd03_1023b0e9d135431aa1e6491bfc318112.pdf), LED variant and timing.
- [WCH datasheet V1.7](https://akizukidenshi.com/goodsaffix/CH32X035.pdf), [reference manual V1.9](https://ch32-riscv-ug.github.io/CH32X035/datasheet_en/CH32X035RM.PDF), [WCH remap header](https://github.com/openwch/ch32x035/blob/main/EVT/EXAM/SRC/Peripheral/inc/ch32x035_gpio.h) and [ST DS8626 Rev 12](https://www.st.com/resource/en/datasheet/stm32f405rg.pdf) for the MCU allocations.

Hub input references: [STUSB4500 DS12499 Rev 8](https://www.st.com/resource/en/datasheet/stusb4500.pdf), [TPS2663 SLVSE94G](https://www.ti.com/lit/ds/symlink/tps2663.pdf), [INA301 SBOS713A](https://www.ti.com/lit/ds/symlink/ina301.pdf), [TPS709 SBVS186H](https://www.ti.com/lit/ds/symlink/tps709.pdf), [CSD19537Q3 SLPS549B](https://www.ti.com/lit/ds/symlink/csd19537q3.pdf), [Vishay WSL document 30100](https://www.vishay.com/docs/30100/wsl.pdf), [TNPW document 31006](https://www.vishay.com/docs/31006/tnpw.pdf), [Panasonic ERA6AEB1052V](https://industrial.panasonic.com/ww/products/pt/high-precision-chip-resistors/models/ERA6AEB1052V), [SN74LVC1G04](https://www.ti.com/lit/ds/symlink/sn74lvc1g04.pdf) and [SN74LVC1G11](https://www.ti.com/lit/ds/symlink/sn74lvc1g11.pdf).

Additional Hub references: [SN74LVC74A SCAS287W](https://www.ti.com/lit/ds/symlink/sn74lvc74a.pdf), [SN74LVC2G17 SCES381N](https://www.ti.com/lit/ds/symlink/sn74lvc2g17.pdf) and [TDK C3216X7R1H106K160AC characterization](https://product.tdk.com/info/en/documents/chara_sheet/C3216X7R1H106K160AC.pdf).

Schmitt and driver references: [SN74HCS11 SCLS790C](https://www.ti.com/lit/ds/symlink/sn74hcs11.pdf), [SN74LVC1G14 SCES218AA](https://www.ti.com/lit/ds/symlink/sn74lvc1g14.pdf) and [onsemi BSS138LT1/D Rev 15](https://www.onsemi.com/pdf/datasheet/bss138lt1-d.pdf).

Port ramp capacitor: [TDK C2012C0G1H223J125AA](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012C0G1H223J125AA), capacitance tolerance, C0G temperature coefficient and reflow lands.

Controller/module references: [ST RM0090](https://www.st.com/resource/en/reference_manual/dm00031020-stm32f405-415-stm32f407-417-stm32f427-437-and-stm32f429-439-advanced-arm-based-32-bit-mcus-stmicroelectronics.pdf), [Abracon ASE](https://abracon.com/Oscillators/ASEseries.pdf), [TCA9535](https://www.ti.com/lit/ds/symlink/tca9535.pdf), [TS3USB30E](https://www.ti.com/lit/ds/symlink/ts3usb30e.pdf), [LMR36510](https://www.ti.com/lit/ds/symlink/lmr36510.pdf), [DRV8876](https://www.ti.com/lit/ds/symlink/drv8876.pdf), [ATtiny404](https://ww1.microchip.com/downloads/en/DeviceDoc/50002687A.pdf), [TCST2103](https://www.vishay.com/docs/81147/tcst2103.pdf), [BAT54S](https://assets.nexperia.com/documents/data-sheet/BAT54S.pdf) and [Panasonic ZC catalog](https://industrial.panasonic.com/cdbs/www-data/pdf/RDD0000/DMD0000COL92.pdf).

Selected passives use Yageo RC/RT resistors, TDK low-voltage bypass parts and KEMET C1210C226K3RACTU 22µF/25V X7R output capacitors. The latter need 1210 lands and up to 2.8mm body clearance. DC bias, aging, effective capacitance and regulator transients remain qualification checks. References: [Yageo RT](https://www.yageogroup.com/component-documentation/download/specsheet/RT0805BRD0710KL), [10nF capacitor](https://www.yageogroup.com/download/specsheet/CC0805KRX7R9BB103), [KEMET bulk capacitor](https://yageogroup.com/download/specsheet/C1210C226K3RACTU), [Omron B3U](https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3u.pdf) and [Schmitt qualification gate](https://www.ti.com/lit/ds/symlink/sn74lvc1g97.pdf).

## Current implementation and release status

Buildable tile, Hub and elevator firmware, host protocol/safety tests and a POSIX USB commissioning client are in [firmware](../../firmware/README.md). The Hub now implements HID/CDC descriptors, six UARTs, UID/address binding, topology reporting, alternating-sector program storage and a small standalone event engine. The tile implements safe module admission, LED/PWM control and software I2C. The GPIO-I2C implementation releases CH32 lines as floating inputs because its general-purpose output modes do not provide open drain. STUSB4500 NVM programming/readback remains a separate required manufacturing operation. None of these implementations has been exercised on assembled boards.

Native KiCad checks on 2026-11-09 report zero ERC violations on all six schematics. Elevator, button, sensor and gate layouts have zero physical DRC violations, zero unconnected items and full schematic parity. Tile and Hub have zero physical DRC violations but remain incomplete. The [manufacturing summary](../../hardware/manufacturing/validation.json) records their current connectivity counts and the tile's five missing connector footprints. Layout review still needs plane continuity, power/thermal limits, the tile MCU ground fanout, USB pairs and the protection/connector release work.

Only the four completed circuit layouts and contact coupons have fabrication drafts. They are not permission to populate or energize the system. No production Gerbers are supplied for the unfinished main boards. The [integrated assembly](../../hardware/cad/assembly.FCStd) includes the PCB component exports that resolve; missing models, unfinished input-module cases and provisional connectors remain visible limitations. It is a clearance reference, not a complete collision qualification.

### MCU ground fanout

The tile MCU exposed-pad ground now escapes on F.Cu to a 0.6mm/0.3mm through via at KiCad (104.3,103.25), outside solder lands. The former via at (100.9,100.5) is removed. Three 0.10mm segments total 5.699mm. The named MCU ground fanout area and tracked `tile.kicad_dru` enforce 0.10mm width and 0.125mm clearance for this narrow GND escape only. Board-wide rules, footprint geometry, pad nets, non-ground copper and isolated return nets are unchanged. Native DRC reports zero physical violations with 117 incomplete connections still present.

Using 28um copper and copper's 0.00393/K temperature coefficient, the neck calculates to about 42mOhm at 70C, or 4.2mV and 0.42mW at a 100mA engineering allowance. That excludes via/joint impedance and does not establish transient or signal-return behavior. [JLCPCB's published feature limits](https://jlcpcb.com/capabilities/pcb-capabilities) support investigating this geometry on standard fabrication. It removes the exposed-pad drill and its filled/capped-via requirement at this location, not the need for assembler review. Confirm continuity, ground bounce, clock/LED/UART operation and temperature on the trial boards. No monetary process saving is claimed without a quote.
