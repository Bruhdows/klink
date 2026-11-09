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

Connector and distribution-copper qualification must account for the Hub's 4.394A upper static input threshold and current redistribution. A 5A continuous connector/return-path qualification goal remains conservative with that hardware limit; it is not the normal tile-load estimate, and it does not establish a short-pulse rating. The transit fuses remain 1A. The 80/40mΩ loop targets belong to future high-load and 3W-per-tile chain comparisons, not the normal V1 load case. Working compression, hot resistance, wear and fault waveforms remain unqualified. Keep the production footprint unreleased.

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

TP6 senses channel 1 at its contact land; TP7 senses channel 5. The added 0.2mm sense tracks carry meter current only. Force current uses TP1/TP5. With mirrored mating, spring TP6 measures against flat TP7 for one contact; spring TP7 measures against flat TP6 for the other. Confirm continuity unpowered first. These connections exclude force-lead and most coupon-track drop, but include the spring body and its solder connection. Probe the other spring foot too to detect unequal foot current or a poor solder joint.

Start unpowered, then use a current-limited low-voltage supply for resistance and temperature tests with relevant contacts loaded. Four-wire leads at the force holes still include PCB and spring resistance. Record force-hole and land-sense drops separately; do not subtract an assumed PCB resistance. Existing 0.3–0.5mm fanout and single vias are not qualified 5A carriers. Begin at 0.1A; test coupon heating before increasing current. No fit, holding force or contact-current test has passed yet. The [prototype plan](prototype-plan.md#connector-measurements) specifies the sample setup.

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

ID uses a 10k pull-up and a module resistor to GND: ADC ratio is R_ID / (10k + R_ID). Candidate values are 1k, 2.2k, 4.7k, 10k, 22k and 47k. The elevator prototype uses 22k; reserve that assignment while the module catalog is finalized. Tolerance windows need testing. Open means absent/unknown; short is invalid. Neither enables power. Don't identify a module from one unfiltered sample.

C7471693 is still a pogo candidate. Ratings, force, compression, plating, pad size and assembly need checking.

The button and marble-sensor bench boards use the same eight signal numbers on a service header. This header is a wired test connection, not a released top-contact assembly. The button reserves 1k ID, uses a 1k series resistor and a normally open contact to GND. Configure MODULE_CTRL as an input with a pull-up before enabling module I/O; debounce in firmware. The sensor reserves 2.2k ID, runs its emitter from switched 5V and regulates its receiver pull-up to 3.3V. It uses no module 20V. Clear glass, alignment, ambient light and brownout response still need testing.

## Mechanical references

CAD origin is the tile center, Z=0 underneath, North=+Y, East=+X. The native tile board body is 68mm square and 1.6mm thick, with mounting centers ±30mm and four 2.5mm holes. Its top face meets the posts at Z=9mm; its bottom is Z=7.4mm. KiCad (100,100) maps to CAD (0,0), with PCB Y=100-CAD Y. Edge connection regions remain empty and the old enclosure contact pockets remain provisional. Connector qualification may still change the edge outline.

D1 and D3 are centered at CAD (-17,23) and (17,-23). The enclosure has matching 3.2mm light openings. Debug and test pads face the open underside. Bare-board volume checks exclude a 0.01mm shift at the intended support contact face; they do not establish printed fit or contact compression. Component height, diffuser performance and probe access still need an assembled sample.

The tallest selected tile part is L1: the [Bourns drawing](https://www.bourns.com/docs/product-datasheets/srp7050ta.pdf) gives 4.8±0.2mm height. Allowing another 0.1mm for assembly leaves 1.4mm below the 15.5mm roof at its location. The 1210 output capacitors allow up to 2.8mm body height. The [WCH QFN28 drawing](https://akizukidenshi.com/goodsaffix/CH32X035.pdf) gives a maximum 0.8mm MCU height. These height checks do not replace the incomplete full-model collision review.

The two Hub cells are 80mm apart. Relative to Hub center, long-edge contacts are X=±40mm, Y=±40mm; short-edge contacts are X=±80mm, Y=0. These are grid references, not final connector positions. A surrounded Hub has six possible neighbors, an edge Hub four and a corner Hub three.

J1 exposes 3.3V monitor, GND, DIO and DCK. Don't power the tile through the monitor pad. Debug outputs must be high impedance when the tile is off. This connection has no powered-off buffer and still needs testing.

The Hub board body is 148×68mm inside the 160×80mm enclosure. Two 14mm-wide USB tabs extend to Y=±39mm between the cell centers. Six mounting holes use X=-70,-20,+70mm and Y=±30mm. PCB bottom/top planes are Z=28.4/30mm inside a 42mm case. The elevated PCB and 20x10mm USB openings let the plug path pass above adjacent tile bodies and standard 5.5mm module bases. Plug overmould dimensions still need a sample. Tall modules must leave the cable path free. The six tile interfaces retain their existing edge/magnet datums; their final carrier/lead geometry remains unreleased.

The local USB4105 footprint retains the GCT drawing's pad centers, 0.6×1.15mm end-ground land envelopes and 0.65mm locating holes. End-ground corner radius is 0.24mm instead of the stock 0.15mm. Native minimum copper-to-hole distance increases from 0.1944mm to about 0.216mm, meeting the 0.20mm project rule. This rounding choice is within the recommended land envelope; it is not a manufacturer assembly qualification. See the [GCT drawing](https://gct.co/files/drawings/usb4105.pdf).

The elevator index bracket uses [Vishay 81147, rev. 1.0](https://www.vishay.com/docs/81147/tcst2103.pdf), package drawing 6.550-5040.01-4 issue 2: 24.5mm flange length, 19mm mounting-hole spacing, nominal 3.3mm holes, 6.3mm width, 10.8mm body height, 3.1mm gap and an optical axis 2.6mm below the top. The 1.5mm index disc sits centrally in the gap. Its slots now open through the rim. The disc is moved forward to clear the whole sensor flange, and the guard has a stationary-flange access opening. The bracket is removable from the rear frame. The elevator base is now 4mm thick with 3.2mm-deep magnet pockets and a 0.8mm roof. This clears the selected sample magnet's 3.1mm maximum height without lifting the frame above its reference plane. The chain relief and wiring opening remain open; the PCB, axes and fork heights are unchanged. The main sprocket plates are 1.2mm clear of the nominal 1.6mm hinge nuts; this assumes washers only under the screw heads. Two cable-tie pairs retain the looms outside the PCB access window. Use an index material that blocks the sensor wavelength and test its contrast before enabling the motor. The CAD envelope is nominal package geometry, not a supplier STEP or a physical fit result.

The continuous return starts at (-80,0,353.5) and ends at (80,0,13.5), relative to the elevator base. The feed-to-exit rise is 340mm; 288mm is the shaft-axis spacing. It has 2.5 descending turns of 120mm radius, a 320mm straight and a half-turn back to the feed. The path is 2741.95mm long with a 7.069° descent. Its 18.5mm channel and retaining lips are intended for nominal 16mm marbles. Rolling speed, seams and capture still need tests. The frame and feed/exit positions are unchanged.

Print 24 copies of the return curve, three 160mm straight ramps, 26 ordinary saddles and one of each terminal support. Nine shared pairs of vertical M6 rods support the repeated turns and return leg; the feet attach to a rigid baseboard below the tiles. Rods pass through saddles at successive heights. Saddle bosses provide horizontal washer seats and the rod model leaves 10mm above the seat for the upper washer, nut and thread. Verify the actual nut stack and baseboard thickness before cutting rods. Do not make separate overlapping columns for each turn. The terminal supports place their rods outside the elevator tiles. The SCAD clearance layout places the other fourteen bases and the Hub north of the elevator; it is a mechanical layout, not a qualified electrical topology. Allow about 700×700mm for a baseboard. Supports under the sprocket discs, carriers, sloping track floors, saddle bridges, lower frame and sensor bracket need slicer review. Review brims and orientation for the tall guards and guides. Place the exports on the slicer bed. The STL exports are under the respective CAD `print` directories; editable dimensions remain in the SCAD sources.


## Future power-only connections

An accessory using another output of the same Hub can feed an ordinary tile edge through 20V and GND, leaving UART/DETECT unused. It retains the tile's transit fuse and the Hub's common shutdown. Cable inductance, return resistance, fault energy and the actual additional feed location need qualification; do not treat it as another communication neighbor or use MODULE_20V as an input. V1 does not require this accessory.

A separately powered injector must default off, block reverse current, limit its feed and participate in wired hardware shutdown of every source. Reserve separate permit and fault-return conductors: the logical permit is INPUT_ENABLE, and an isolated open-drain fault receiver can join the common fault decision. Merely sending a UART message is insufficient. The Hub input monitor cannot measure external-source current, so aggregate current, fuse loading and stored energy require a new coordinated budget. Existing tile bus voltage and local rails remain unchanged.

## Direct side-contact trial

The [side-contact coupon](../../hardware/electronics/contact-test/side-contact-test.kicad_pcb) and [flat mate](../../hardware/electronics/contact-test/side-flat-test.kicad_pcb) are separate five-channel test boards. Both pass native DRC with zero unconnected items. They have no production power/signal assignment. The Harwin test land is 2.25x3.70mm from [S1961-46R issue 6, 2025-02-04](https://content.harwin.com/asset/f4cd037e-0829-4c4c-a570-f0dd6472082e/DRG-03072-Technical-Drawing-Datasheet-S1961R-pdf.pdf). No production tile connector uses it.

The spring board is 40x28x1.6mm. The flat board is 40x12x1.6mm. Force holes are TP1-TP5; land-sense pads are TP6-TP10. The 2.2mm force traces and 1mm/1.3mm plated holes have not passed a current/temperature test. Begin at 0.1A, verify the sense connections, then increase current only while measuring coupon and contact temperature. The [fixture](../../hardware/cad/base/side_contact_fixture.scad) holds the spring board horizontally and the mate vertically. Adjust the starting plane from measured first touch. CAD travel is not a measured working deflection. Print files and STEP exports are included.

Direct side compression can remove the two sprung carrier boards per tile. It still needs a vertical mating conductor at the spring's working height. A coplanar 1.6mm PCB edge does not automatically provide that face. Removing all four carriers would require a backed formed-metal tab, a folded flex section or a qualified plated/staggered edge. None is selected. Formed tabs add ten individual attachment operations per tile; rigid-flex/edge plating can change assembly eligibility. Test cost and alignment before claiming savings. Keep the existing carrier budget until a complete mating pair is qualified.

The current Harwin drawing delegates life/electrical specifications to C055XX. Its 0.20-0.50mm side travel and 1.2N minimum force at 0.20mm are useful for a fixture, not a guarantee of retention in PETG. Five contacts need at least 6N before friction. Tin finish, conditioned resistance, wear, 20V isolation between channels and the fault waveform remain acceptance tests. A current listing does not establish fault-pulse survival. The SAMZO 23E315050/23E415050 pair remains unqualified and its imported pin-number problem is unresolved. SAMZO 03E315320 remains the lower-placement-count sample candidate, with vertical carriers and missing stroke/force/finish data.

## Fastening and magnet orientation

The tile PCB still uses the 68mm body, 2.5mm holes at (+/-30,+/-30) and top plane Z=9mm. Its posts now have accessible M2 nut pockets at Z=12mm and clearance holes for M2x8 screws from below the board. Slide nuts in before fitting electronics. The Hub uses six bottom-loaded M2 nuts and M2x30 screws with a nominal 0.6mm washer stack above the PCB. Its twelve side-magnet pockets are 6.25mm diameter and 3.25mm deep with backing supports. The elevator's PCB tongues now have through holes and bottom-loaded M2 nut seats for M2x10 screws. Outer PCB/hole datums are unchanged. The gate service board uses M2x6 screws on its vertical carrier. Check actual screw-tip clearance, nut thickness and PETG engagement before assembly.

Use 4.0mm across-flat M2 nuts no thicker than 1.6mm; the shared printed allowance is 4.3mm across flats and 1.8mm depth. These choices avoid heat-set inserts. They have not passed printed-fit or torque testing.

Keep every tile in the same cardinal orientation. North and East side magnets have N facing outward; South and West have S facing outward. Tile top magnets have N upward; module bottom magnets have S downward. The Hub follows the same global cardinal polarity. Mark an orientation master and check every opposing face before bonding magnets. The current bodies use nominal 6x3mm magnets; adhesive retention and printed pocket tolerance remain tests. Do not rely on an untested press fit beside exposed electrical contacts.

## Gate service prototype

The [gate schematic and PCB](../../hardware/electronics/gate/) use the eight-pin service interface, 4.7k ID, a 1k control resistor, a 100nF bypass capacitor and a three-pin FS90 servo connection. J2 is GND, switched 5V, PWM. The 20V pin and unused I2C pins are not connected. [Pololu documents FS90 compatibility with 3.3V signals](https://www.pololu.com/product/2818), so this prototype needs no extra level-shifter circuit. The manufacturer sheet lists 700mA stall at 4.8V and 800mA at 6V; this is close to the tile's provisional 5V budget. Measure startup and jams rather than approving stall as normal operation.

The [gate CAD](../../hardware/cad/modules/gate.scad) has a curved flap matching the track channel, an M3 pivot, a clamped nominal servo envelope, a vertical service-board carrier, and a separate clamp. Use the supplied servo horn; no printed spline is provided. Horn slot spacing and axial engagement need a sample. The sampled 0-90 degree flap sweep at 5 degree increments has an empty intersection with the printed base; the nominal servo envelope also clears it. These are limited CAD checks, not a detailed horn/screw/servo collision approval. Gate travel calibration, unpowered position, servo load, harness routing and durability remain untested.

### Hub USB neighbor clearance

At the previous Z=9mm PCB top plane, the 18x24x8mm design plug envelopes intersected neighboring tile bodies by 6,912mm3. The current Z=30mm top plane gives an empty intersection with all six adjacent tile bodies plus standard module bases (25.5mm total height). The assumed plug bottom is Z=27.5mm, giving 2mm nominal clearance above those bases. These are CAD acceptance envelopes, not measured cable dimensions. Confirm the selected cables, printing tolerance and access before assembly. Disconnect PD and data cables before vertically removing adjacent tiles.

PCB X/Y placement, outline and circuitry are unchanged. Its raised stack adds about 21mm of vertical travel to the unqualified edge leads/carriers. Include their actual resistance, inductance, return path and strain relief in the protection and manufacturing review. No additional PCB or cable adapter is selected.
