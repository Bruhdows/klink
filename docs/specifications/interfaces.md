# Connections and fit

## Tile edges

Each edge carries 20V, GND, TX, RX and DETECT. UART logic is 3.3V. Local 5V and 3.3V never cross between tiles. Bases keep a fixed orientation: North meets South, East meets West.

North J3 and East J6:

1. Edge 20V
2. GND
3. TX
4. RX
5. DETECT

South J4 and West J5:

1. DETECT
2. TX
3. RX
4. GND
5. Edge 20V

These are schematic numbers, not confirmed connector numbers. Check actual mating continuity before assigning footprints. TX must reach RX, and power and ground must line up.

North/East DETECT use a 10k pull-up and MCU input. South/West provide a 1k ground signature. Detection only works from the sensing side; UART handshakes must identify both neighbors. U13 separates the inputs from an unpowered MCU. Missing-ground and unpowered-neighbor behavior still need testing.

## SAMZO connector

SAMZO 03E315320 / C42402947 is the preferred sample, not a final production choice. The [manufacturer record](https://www.sancnn.com/goods-detail/2207) links [drawing 03E31-P991 A1, 2018-06-14](https://www.sancnn.com/files/samzo-1/ljq/dcz/03E3-TZ.pdf), under code ST.25.D.1009.

For five contacts, the drawing gives:

- Body 10 × 6.5mm, 2mm pitch, 1.27mm free height.
- Two Ø0.8mm locating pegs, 1.05 ±0.20mm below the PCB.
- Ø1mm board holes, 8mm apart.
- Land rows 5.38mm apart, land length 1.62mm. Land width and electrical numbering aren't clear.
- 5A, 30V, 500V withstand, 30mΩ contact resistance, 500MΩ insulation resistance.
- -55 to +125°C, more than 10,000 operations, PA9T body and gold-plated C2680 brass contacts.

The missing bits matter: is 5A per contact with all contacts loaded? At what temperature rise and compression? Force, working travel, plating thickness and test conditions aren't given. The 500V entry has no test duration, so it doesn't prove transient survival.

The distribution target now requires at least 5A continuous capability for every power and return path at the qualified temperature, including redistribution. The first V1 resistance target is no more than 80mΩ for a complete positive/return link including both copper paths and carrier joints. The listed 30mΩ contact figure has no established hot/compression/life conditions and does not qualify that target. A twenty-tile 3W chain across the lower input range needs closer to 40mΩ; that may require another contact arrangement. Short-pulse acceptance must come from waveform testing and manufacturer evidence, not the 5A continuous entry. Keep the production footprint unreleased.

The springs compress perpendicular to the board. Horizontal tile mating needs vertical carriers: two spring boards and two flat-pad boards per tile are the current idea. The body fits between the ±18mm magnet centers on paper. Retention, solder access and wall clearance need samples. Both faces can't sit behind flush walls and still touch. The guard needs an upward escape path so a surrounded tile can lift out.

Four carriers per tile would add 80 small PCBs, their attachment joints and alignment work for twenty tiles. Panelizing them reduces fabrication overhead but not assembly operations. Keep these as contact-test coupons until stroke and mating finish are known. Flat mating boards need only copper and finish, not purchased contacts. A side-entry connector mounted directly on the main board could remove carriers, but 03E315320 is a normal-to-board spring and cannot be rotated electrically by changing its footprint. Do not add board-to-board headers or an interposer to solve that orientation. Quote a directly mounted side-entry contact and the existing carrier arrangement after sample tests, while keeping the same universal tile and five edge signals.

There's no manufacturer STEP or verified imported footprint. `Klink:SAMZO_03E315320_TestOnly` uses a provisional 1.4mm land width and test-channel numbers. Don't assign it to J3-J6 yet.

### Finish and alternatives

Agree gold thickness and nickel underplate with the suppliers. ENIG is worth testing, but it doesn't prove a 10,000-cycle life. Compare wear and resistance against hard-gold-over-nickel pads. Keep solder, paste and vias away from the contact area. [Samtec's guidance](https://blog.samtec.com/connector-plating-faqs/) explains matching finishes and why tin needs more force and wipe.

[Harwin S1961-46R](https://www.harwin.com/products/S1961-46R) has clearer mechanical data: 4.63 × 3.70 × 3.55mm, 0.20-0.60mm top deflection, 0.20-0.50mm side deflection and at least 1.2N at 0.20mm. Five contacts need at least 6N before friction. It's tin over nickel, so don't assume ENIG is a suitable mate. Its listed 14A isn't an application rating. Old/current life and temperature data differ; C055XX/HT077 conditions still need checking.

The older SAMZO 23E315050/23E415050 pair still lacks mating/current evidence. Its male import has fifteen distinct pad numbers for a five-contact device. Don't reuse 04F415000 without checking pads 6/7 and locating holes. Individual Xinyangze C7471693 pins are listed at 2A and need ten placements per tile; they don't solve the fault-current question. Prices are in the [BOM](BOM.md).

## Fit tests

`hardware/cad/base/samzo_03e315320_fixture.scad` has a 56mm center and four 9mm neighbor stubs, 74mm overall. It keeps ±18mm magnet spacing, nominal 6 × 3mm magnets and 20mm height. Print one `part="center"` and four `part="neighbor"`. Holders take the 20 × 12 × 1.6mm boards in `hardware/electronics/contact-test/`. This tests an edge, not the full 80mm enclosure.

Start at `compression=0`, measure free height and force, then add measured shims. The 0.5mm parameter limit is just a CAD guard, not a safe working stroke. Set hard stops only after confirming stroke. Use two sprung and two flat center edges with opposite neighbor boards. Check sideways separation, vertical removal, offset, tilt, bridging and repeated mating. Preview blocks aren't detailed spring models.

The boards have five test channels, not assigned power/UART functions. Numbers are viewed from each contact face; check 1-to-5, 2-to-4, 3-to-3 mating and spring-end continuity before assembly. Confirm land width and finish before ordering.

Start unpowered, then use a current-limited low-voltage supply for resistance and temperature tests with relevant contacts loaded. Four-wire leads at the holes still include PCB and spring resistance. Measure that baseline or use Kelvin probes near the contacts. No fit, holding force or contact-current test has passed yet.

## Top modules

Tiles have flat pads; modules carry the spring contacts. A small top PCB is an option. Keying must stop offset, tilt or reversal from putting 20V on a signal.

Provisional contact order:

1. GND
2. MODULE_5V, switched and current limited
3. MODULE_20V, switched and protected
4. MODULE_SDA, 3.3V logic
5. MODULE_SCL, 3.3V logic
6. MODULE_CTRL, GPIO/PWM
7. MODULE_ID, resistor-coded ADC input
8. GND

This replaces the old unswitched 3.3V contact. Old prototype modules aren't compatible. Modules needing 3.3V must regulate it themselves.

Both power outputs default off. Read passive ID before enabling power. U12 keeps SDA/SCL/CTRL disconnected until module 5V is valid and the MCU requests access. Receiver logic must use protected 5V or have its own powered-off isolation. This also applies to modules using 20V for a motor; 20V alone doesn't enable signals.

Signals are 3.3V, at most 3.6V with the tile off. No 5V pull-ups. Slow brownout and module startup/dropout need testing. The provisional 0.8A/5V and 0.4A/20V budgets aren't approved simultaneous loads. Motor modules must handle their own inductive/braking energy and the eventual transient limits.

ID uses a 10k pull-up and a module resistor to GND: ADC ratio is R_ID / (10k + R_ID). Candidate values are 1k, 2.2k, 4.7k, 10k, 22k and 47k. Tolerance windows need testing. Open means absent/unknown; short is invalid. Neither enables power. Don't identify a module from one unfiltered sample.

C7471693 is still a pogo candidate. Ratings, force, compression, plating, pad size and assembly need checking.

## Mechanical references

CAD origin is the tile center, Z=0 underneath, North=+Y, East=+X. Preliminary PCB: 68mm square, 1.6mm thick, mounting centers ±30mm and 2.5mm preview holes. Posts support at Z=9mm, with the preview board below that plane. Check solder and screw clearance before fixing the outline. KiCad (100,100) maps to CAD (0,0), with PCB Y=100-CAD Y.

The two Hub cells are 80mm apart. Relative to Hub center, long-edge contacts are X=±40mm, Y=±40mm; short-edge contacts are X=±80mm, Y=0. These are grid references, not final connector positions. A surrounded Hub has six possible neighbors, an edge Hub four and a corner Hub three.

J1 exposes 3.3V monitor, GND, DIO and DCK. Don't power the tile through the monitor pad. Debug outputs must be high impedance when the tile is off. This connection has no powered-off buffer and still needs testing.
