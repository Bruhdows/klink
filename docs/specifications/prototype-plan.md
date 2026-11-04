# Next steps

## Samples and fit

The committed straight-track STL is older than the SCAD. Export from the current source before printing.

Order magnets and SAMZO 03E315320 samples. Confirm the missing dimensions and working compression, then print the [connector fixture](interfaces.md#fit-tests). Check alignment, continuity, magnet polarity, holding force, sideways slip and repeated mating. Try lifting the center out with four neighbors held down.

Test the top interface with offset, tilt and reversed insertion. Nothing should let 20V touch a signal pad. Keep these tests unpowered.

## Connector measurements

Start with ten SAMZO 03E315320 bodies, five spring coupons and five flat coupons, not a twenty-tile order. Confirm the provisional spring land width against samples before fabrication. Use the existing 20 × 12 × 1.6mm editable boards. Specify and record copper thickness and finish; for the first comparison, five ENIG flat boards and five additional hard-gold-over-nickel flat boards are useful only if the supplier quotes the actual gold/nickel thickness. Do not substitute unspecified gold flash. Buy 24 of the specified 6 × 3mm magnets for one four-neighbor fixture with spares; use measured nonconductive shims and hard stops after establishing working travel.

Use a four-wire millivolt meter, a measured current shunt, thermocouples, an adjustable 0–1V/5A current-limited supply and 20AWG force leads. These are instrument requirements, not a requirement to buy replacements for owned equipment. Begin with one contact at 0.1A and 0.5A. Use TP1/TP5 for force and the new TP6/TP7 land-sense pads as described in [interfaces](interfaces.md#fit-tests). Reverse current and average signed voltage to reject thermoelectric offset. Then load the power and return contacts together with a short external return on the flat board; record both contact drops and the total force-terminal drop. No UART or MCU is connected.

Log resistance, current, ambient, spring temperature, solder-foot temperature and carrier/via temperature at 0.1/0.5/1A. Increase to 2/3/4.5/5A only after checking the prior step and coupon copper temperature; the existing narrow fanout is not a qualified high-current carrier. Use 30°C rise or 70°C absolute as conservative initial bench stop points, whichever comes first. These are test stops, not product ratings or manufacturer limits. Hold each allowed step until drift is under 1°C over ten minutes, with a thirty-minute minimum. Repeat at confirmed compression limits, lateral offsets, and after 10/100/1000 unpowered mating cycles. A 1000-cycle screen does not establish the listed 10,000-cycle life. Stop on unstable resistance, discoloration, spring set or plastic deformation.

Measure each complete spring-plus-flat assembly and each solder attachment. Include force/sense uncertainty and specimen spread; do not extrapolate a guaranteed maximum from five samples. The current carrier budget permits only about 17.97mΩ/contact at 25°C with the candidate fuses to reach an 80mΩ loop. A stable 30mΩ sample still misses that budget. Request a wider contact or test direct side-entry S1961-46R samples separately, with a supplier-approved mating finish. The latter requires a different mounting coupon; do not solder it onto the SAMZO lands. Reserve ten samples only after agreeing finish and force. Do not spend on parallel spring bodies before single-contact results.

For fuse comparison, reserve ten 0466001.NR and ten 0451007.MRL with proper supplier land patterns on the eventual power-path test board. The latter is an unselected backup candidate, not a substitute in the existing tile. Measure four-wire resistance cold and hot and preserve sacrificial specimens for fault-energy tests after the protection fixture is qualified. No short-time contact rating follows from those fuse data.

## Hub protection prototype

The smallest useful common-shutdown prototype has the master breaker and two complete output paths feeding a shared dummy network. A single output cannot demonstrate alternate feeding. Use the existing input-protection, two instances of port-power and full shutdown circuit. The two-output bench assembly contains 130 positions, including copper test points. It omits USB PD parts and four power paths, keeps C1/C4 input bypass, R6 enable pull-up, and R143/R144, R163/R164, R183/R184, R203/R204 for the absent fault sources. There are 112 purchased positions and 18 copper test points. Manufacturer selections are present; stock, pricing and electrical qualification remain open. They remain selections, not an order-ready BOM. No prototype PCB is laid out yet.

Reserve three each TPS26630RGER (RGET reel alternate), INA301A1IDGKR, CSD19537Q3, BSS138LT1G and WSL2512R0100FEA, plus one spare of each. Use the exact control, supervisor, logic, TVS, resistor and capacitor selections in the exported subset. Two port ramp capacitors must be C2012C0G1H223J125AA. Keep all shared latch circuitry; do not replace it with a microcontroller or a breadboard of long fault wires. A custom short-loop PCB is needed for meaningful cutoff/overshoot measurements. EVMs are optional device experiments, not mandatory extra adapters or substitutes for this shared shutdown test.

First use an isolated current-limited bench source at VBUS_PD, with USB connector/controller absent. Simulate MCU_RESET_N from a supervised 3.3V bench stimulus and PD_20V_OK_N using an open-drain stimulus against R6; its released state must inhibit startup. This bench assembly is not a USB power input and does not validate source qualification. Bring up control at low current first, then 19/20/21V with a 5A source ceiling. Use an electronic load rated at least 100W/30V, two 0.1Ω/5W link resistors, two independently removable return links, and a controlled fault fixture. Start with resistive overloads; direct shorts require a rated fixture and measured source/capacitor energy.

Observe shunt voltages with differential probes or isolated current measurement, both port outputs, RUN_OK and FAULT_LATCHED. Measure trip versus current at room/hot conditions, each branch alone, combined loads below individual trips but above total trip, startup into overload, failed rise, slow brownout, reset and reverse-fed charged output. Join both outputs through the link resistors to a common fault node, then remove a positive or return path with power off and repeat. Verify that a fault reported by either branch disables both and stays latched while switched power is absent. Record peak current and integrate I²t until all sources and capacitors stop feeding, including input/common/output capacitors. The existing model supplies no pulse acceptance limit.

Test hard shorts, TVS behavior and single-switch failure only after low-energy bring-up and fixture review. Agree connector pulse withstand and fuse maximum clearing data before claiming coordination. Add the USB PD source/controller test after the raw-input surge decision; do not expose an incomplete protection board to an unrestricted PD source. The later six-output assembly still needs all-port testing.

## Power and communication

Qualify the Hub's branch protection and total cutoff. Check faults through grid loops, not just a chain. Test the buck on a current-limited supply, then both module outputs with electronic loads. Measure ripple, startup, temperature and short-circuit recovery before adding motors.

Use three CH32X035 boards for discovery and forwarding. Then run four UARTs, RGB and hardware I²C together. Test brownout, missing neighbors, duplicate packets and stuck-bus recovery. Check the actual MCU silicon lot supports I²C.

## First boards

Low-voltage placement can continue. Connector fit and power protection need to be settled before high-voltage placement and routing.

After connector qualification, protection testing and schematic/layout review, order 3-5 trial boards. Test those before making the rest. Another revision might still be needed.

Then finish the Hub and start with button/light modules, followed by sensors, servos and the elevator. Measure motor and servo stall loads first.

The demo should run a marble loop, react to events, identify tiles with RGB and keep running without a laptop. Rearrange tiles only with power disconnected.
