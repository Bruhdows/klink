# Next steps

## Samples and fit

Current STL and STEP exports are included. Use the source parameters and the short fit-print sequence below before printing the full kit.

Order magnets and SAMZO 03E315320 samples. Confirm the missing dimensions and working compression, then print the [connector fixture](interfaces.md#fit-tests). Check alignment, continuity, magnet polarity, holding force, sideways slip and repeated mating. Try lifting the center out with four neighbors held down.

Test the top interface with offset, tilt and reversed insertion. Nothing should let 20V touch a signal pad. Keep these tests unpowered.

## Connector measurements

Start with five SAMZO 03E315320 bodies, five spring coupons and five flat coupons, not a twenty-tile order. Confirm the provisional spring land width against samples before fabrication. Use the existing 20 × 12 × 1.6mm editable boards. Specify and record copper thickness and finish; for the first comparison, five ENIG flat boards and five additional hard-gold-over-nickel flat boards are useful only if the supplier quotes the actual gold/nickel thickness. Do not substitute unspecified gold flash. The fixture magnet pockets are optional for the initial clamped contact tests. Do not glue a full magnet set into a qualification jig; qualify magnetic retention on the trial bases within the project allocation. Use the two unavoidable magnet-pack remainders for initial adhesive coupons; use measured nonconductive shims and hard stops after establishing working travel.

Use a four-wire millivolt meter, a measured current shunt, thermocouples, an adjustable 0–1V/5A current-limited supply and 20AWG force leads. These are instrument requirements, not a requirement to buy replacements for owned equipment. Begin with one contact at 0.1A and 0.5A. Use TP1/TP5 for force and the new TP6/TP7 land-sense pads as described in [interfaces](interfaces.md#fit-tests). Reverse current and average signed voltage to reject thermoelectric offset. Then load the power and return contacts together with a short external return on the flat board; record both contact drops and the total force-terminal drop. No UART or MCU is connected.

Log resistance, current, ambient, spring temperature, solder-foot temperature and carrier/via temperature at 0.1/0.5/1A. Increase to 2/3/4.5/5A only after checking the prior step and coupon copper temperature; the existing narrow fanout is not a qualified high-current carrier. Use 30°C rise or 70°C absolute as conservative initial bench stop points, whichever comes first. These are test stops, not product ratings or manufacturer limits. Hold each allowed step until drift is under 1°C over ten minutes, with a thirty-minute minimum. Repeat at confirmed compression limits, lateral offsets, and after 10/100/1000 unpowered mating cycles. A 1000-cycle screen does not establish the listed 10,000-cycle life. Stop on unstable resistance, discoloration, spring set or plastic deformation.

Measure each complete spring-plus-flat assembly and each solder attachment. Include force/sense uncertainty and specimen spread; do not extrapolate a guaranteed maximum from five samples. The current carrier budget permits only about 17.97mΩ/contact at 25°C with the candidate fuses to reach an 80mΩ loop. A stable 30mΩ sample still misses that budget. Request a wider contact or test direct side-entry S1961-46R samples separately, with a supplier-approved mating finish. The latter requires a different mounting coupon; do not solder it onto the SAMZO lands. Use the five-channel side-contact coupon and five S1961-46R samples only after agreeing mating finish and force. Do not spend on parallel spring bodies before single-contact results.

Use the retained 0466001.NR parts for non-destructive cold/hot resistance screens. Do not pre-buy the unselected 0451007.MRL comparison candidate. The latter is an unselected backup candidate, not a substitute in the existing tile. Measure four-wire resistance cold and hot and preserve sacrificial specimens for fault-energy tests after the protection fixture is qualified. No short-time contact rating follows from those fuse data.

## Hub protection prototype

The smallest useful common-shutdown prototype has the master breaker and two complete output paths feeding a shared dummy network. A single output cannot demonstrate alternate feeding. Use the existing input-protection, two instances of port-power and full shutdown circuit. The two-output bench assembly contains 130 positions, including copper test points. It omits USB PD parts and four power paths, keeps C1/C4 input bypass, R6 enable pull-up, and R143/R144, R163/R164, R183/R184, R203/R204 for the absent fault sources. There are 112 purchased positions and 18 copper test points. Manufacturer selections are present; stock, pricing and electrical qualification remain open. They remain selections, not an order-ready BOM. No prototype PCB is laid out yet.

The two-output bench circuit needs three each TPS26630RGER (RGET reel alternate), INA301A1IDGKR, CSD19537Q3, BSS138LT1G and WSL2512R0100FEA. These are an alternative prototype population, not extra full-Hub spares. Use the exact control, supervisor, logic, TVS, resistor and capacitor selections in the exported subset. Two port ramp capacitors must be C2012C0G1H223J125AA. Keep all shared latch circuitry; do not replace it with a microcontroller or a breadboard of long fault wires. A custom short-loop PCB is needed for meaningful cutoff/overshoot measurements. EVMs are optional device experiments, not mandatory extra adapters or substitutes for this shared shutdown test.

First use an isolated current-limited bench source at VBUS_PD, with USB connector/controller absent. Simulate MCU_RESET_N from a supervised 3.3V bench stimulus and PD_20V_OK_N using an open-drain stimulus against R6; its released state must inhibit startup. This bench assembly is not a USB power input and does not validate source qualification. Bring up control at low current first, then 19/20/21V with a 5A source ceiling. Use an electronic load rated at least 100W/30V, two 0.1Ω/5W link resistors, two independently removable return links, and a controlled fault fixture. Start with resistive overloads; direct shorts require a rated fixture and measured source/capacitor energy.

Observe shunt voltages with differential probes or isolated current measurement, both port outputs, RUN_OK and FAULT_LATCHED. Measure trip versus current at room/hot conditions, each branch alone, combined loads below individual trips but above total trip, startup into overload, failed rise, slow brownout, reset and reverse-fed charged output. Join both outputs through the link resistors to a common fault node, then remove a positive or return path with power off and repeat. Verify that a fault reported by either branch disables both and stays latched while switched power is absent. Record peak current and integrate I²t until all sources and capacitors stop feeding, including input/common/output capacitors. The existing model supplies no pulse acceptance limit.

Test hard shorts, TVS behavior and single-switch failure only after low-energy bring-up and fixture review. Agree connector pulse withstand and fuse maximum clearing data before claiming coordination. Add the USB PD source/controller test after the raw-input surge decision; do not expose an incomplete protection board to an unrestricted PD source. The later six-output assembly still needs all-port testing.

## Power and communication

Qualify the Hub's branch protection and total cutoff. Check faults through grid loops, not just a chain. Test the buck on a current-limited supply, then both module outputs with electronic loads. Measure ripple, startup, temperature and short-circuit recovery before adding motors.

Use three CH32X035 boards for discovery and forwarding. Then run four UARTs, RGB DMA and software I²C together. Test brownout, missing neighbors, duplicate packets and stuck-bus recovery. Check the actual MCU lot and the floating-input/low-output I²C waveforms. Hardware I²C remains lot-dependent.

## First boards

Continue internal layout and enclosure checks. Keep unreleased edge power paths and final distribution release blocked until contact qualification and cutoff/TVS coordination are resolved.

After connector qualification, protection testing and schematic/layout review, order 3-5 trial boards. Test those before making the rest. Another revision might still be needed.

Button, sensor and gate service boards are bench prototypes. All three MCU firmware projects now build; the elevator still needs current-limited bring-up, printed fit and progress/fault testing. Measure motor and servo loads before admitting them to the kit power budget.

The demo should run a marble loop, react to events, identify tiles with RGB and keep running without a laptop. Rearrange tiles only with power disconnected.

## First test order

Buy qualification material before any production main-board order. The root [BOM](../../bom.csv) separates the 3/5-tile trial from the sixteen-tile build. Reuse successful trial assemblies. Do not add the two totals together.

- Five SAMZO 03E315320 wear specimens, five spring coupons and the quoted flat finishes. Confirm the provisional land width before fabrication. The thirty-five production-candidate bodies stay on hold.
- Five S1961-46R samples for the dedicated horizontal coupon and eight candidate top contacts for keying/bridging qualification. Their production geometry stays unreleased.
- The minimum magnet pack needed for the selected fixture and eventual trial bases. Assign polarity before bonding. Avoid a separate speculative magnet inventory.
- One Pololu 3044, one TCST2103 and one 623-2Z bearing for the lift. Confirm delivery, dimensions, shaft, bearing fit and optical contrast. The local N20 alternative remains unselected without its exact winding, ratio and torque data.
- Thirty M2x16 hinge screws and nuts no taller than 1.6mm, with washers under heads only. Final retention and endurance remain tests. The nominal idler stack uses an M3x40 recessed cap screw, 2.5mm front spacer, 4mm bearing, 25mm rear spacer, 3mm frame and rear washer/nut. Check the actual head, race contact and screw tip before running.
- Only the trial board populations and harness parts in the BOM. The small service boards can be hand assembled with owned tools. No development boards, EVMs or speculative spare populations are required.

Print two links, two carriers, the drive and idler, the sensor bracket, two return curves, one 160mm ramp, three ordinary saddles, one entry support and two feet first. Test the gate clamp, flap and PCB carrier separately with the supplied FS90 horn. Use slicer supports where needed. Secure the lift to a rigid support before powered tests. The full return's rod cut list and drilled 12mm baseboard are for the final assembly, not prerequisites for bare-board bring-up.

Check index opacity, hinge freedom, drive-tip clearance, bearing seats, shaft grip, sensor alignment, M2 nut engagement, removable wiring and track seams before printing all thirty links. The final return uses twenty-four curves, three ramps, twenty-six ordinary saddles, two terminal supports and nine feet. Five one-metre M6 bars satisfy the current eighteen-rod cut list; measure the board and nut/washer stacks before cutting.

The two-output protection schematic remains a bench reference without a PCB. It is not an orderable substitute for finishing and qualifying the Hub. Main-board routing, contact mating, top keying, converter/return review, harnesses and module cases remain release gates. No physical tests are recorded as passed.
