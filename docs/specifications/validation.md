# Checks and results

The 20V board and new SAMZO connection haven't been assembled or physically tested. Small mechanical prints don't establish electrical safety. Rev A isn't ready to order.

## Current checks

Native KiCad 10.0.8 checks and the maintained regression suite pass with the incomplete-layout results below. No boards have been assembled or electrically tested.

- Tile ERC: 0 violations across three sheets. Existing exclusions remain `single_global_label`, `four_way_junction`, `simulation_model_issue` and `footprint_filter`.
- Hub ERC: 0 violations across ten pages, without adding exclusions. Native netlist: 214 components, 203 nets, 1089 connectivity/value checks passed. Six protected power outputs and shared shutdown are implemented; MCU and data circuitry are absent.
- Tile netlist: 130 components, 104 nets; all 313 connectivity checks passed. J3-J7 still have no released footprints; J2 is excluded from the PCB.
- Tile PCB: 54 footprints, no copper routes or fabrication outline. DRC exits 5 with one `invalid_outline`, 135 `unconnected_items` and 75 `missing_footprint` parity findings. There are no clearance, short, courtyard, solder-mask, silkscreen, field or net mismatch findings. The placement audit also reports no overlaps.
- Both contact coupons: DRC exits 0 with no violations or unconnected items. Their land geometry and finish are not production-qualified.
- The 37 regression tests pass. They include analytic load-flow roots, collapse on either side of an analytic power maximum, common-input losses including Hub load, unequal returns, simultaneous path openings, complete source removal, deliberate shunt/RTN miswiring rejection and schematic calculation values. The stable-state logic tests evaluate the actual netlist gates and flip-flops: all six overcurrent inputs during startup, each health input after arming, failed startup, switched-power loss, reset, PD loss and input overcurrent. They do not simulate analog propagation or measure silicon.
- All assigned footprint files resolve and their numbered pads cover the native netlist pins. The local footprint library loads through native SVG export. New shunt lands follow Vishay document 30100. Assembly and thermal-via review remain open.
- All Hub pages and the tile placement were rendered and inspected. Native connectivity, not the pin summary of an editing tool, is the electrical check.

Run from a clean checkout with Python 3 and KiCad installed:

```sh
python3 -B hardware/electronics/checks/run_checks.py
python3 -B hardware/electronics/checks/power_budget.py --common-ohms 0.1
python3 -B hardware/electronics/checks/power_budget.py --faults --fault-sweep
python3 -B hardware/electronics/checks/hub_limits.py
python3 -B hardware/electronics/checks/distribution.py --chain
python3 -B hardware/electronics/checks/distribution.py --openings
python3 -B hardware/electronics/checks/power_budget.py --envelope \
  --common-ohms 0.1 --total-limit-amps 4.014 --fuse-continuous-amps 0.6
```

The runner uses `kicad-cli`, or Flatpak KiCad when available. Override with `KICAD_CLI`; set `KICAD_FOOTPRINT_DIR` if stock footprints are installed outside `/usr/share/kicad/footprints`. Temporary reports are removed by default; `--output PATH` retains them. A 0.1Ω common input path is an engineering allowance, not a measured resistance. Passing checks does not qualify protection, temperature or physical fit.

## Power calculations

The model treats positive and ground paths separately. Default resistances:

- Contact 0.05Ω; copper 0.02Ω per conductor/link.
- Positive tile link 0.22Ω, including two nominal 0.075Ω fuses; ground link 0.07Ω.
- Hub branch: one tile fuse plus an assumed 0.15Ω switch.
- Local F1 + U7: 0.225Ω.

Only nominal fuse/eFuse values come from component data. Actual contact, copper, hot resistance and efficiency aren't measured. Each solved case checks power balance using local supply-to-ground voltage.

The 32 load cases cover 20/64 tiles, chains and grids, center/edge/corner Hub positions and 0.5/3/6/14W per tile after local protection. These are planning loads, including estimated conversion loss. The model does not limit normal-load current; it flags cases beyond assumed limits. The Hub load is included in total source current and, when specified, common input resistance. Constant-power converters are assumed to stay on; UVLO cycling and startup are not simulated. It doesn't cover every layout, uneven contacts, heating or vertical interconnects.

Assumed Hub limits are 1.5A/branch, 4.5A total including tolerance, and 5W for the Hub. At 21V that is 99.5W. Actual hardware still needs to enforce it.

Selected results below give minimum protected voltage, maximum positive/ground current and input power including the Hub:

- 20 tiles, 0.5W each, chain: 18.316V, 0.531/0.531A, 15.62W.
- 20 tiles, 3W each, central grid: 19.638V, 0.594/0.611A, 65.84W.
- 20 tiles, 3W each, corner grid: 19.162V, 1.172/1.195A, 67.04W. Over the fuse continuous budget.
- 64 tiles, 0.5W each, central grid: 19.776V, 0.309/0.318A, 37.27W.
- 64 tiles, 3W each, central grid: 18.587V, 1.948/2.004A, 207.82W. Beyond power, fuse and source limits.
- The old iteration timed out on 20 tiles at 3W and 64 tiles at 0.5W in chains. The revised monotone voltage-bound calculation rules out a positive all-loads-on DC solution in these constant-power models. It does not rule out a real system cycling through UVLO or shedding loads.

None is a tested operating point.

With the new common-input model, a 0.1Ω allowance and the calculated minimum input trip of 4.014A, the equal-load 20-tile DC envelopes are approximately:

- At the 25°C fuse budget: 3.62W/tile centrally, 2.77W at an edge, 1.92W at a corner and 0.68W in a chain.
- At the 70°C fuse budget: 2.98W/tile centrally, 2.23W at an edge, 1.55W at a corner and 0.56W in a chain.

These are boundary calculations with no design margin and no failed connections. Twenty 3W tiles at the center are already slightly beyond the hot fuse budget with the common-path allowance. A qualified product budget must be lower and include redistribution after openings. A simultaneous 60W tile load at 15.75V plus a 5W Hub needs over 4.13A before losses, although its 20V steady state fits. Startup therefore needs initially disabled modules and controlled load application; steady DC feasibility is not startup qualification.

### Architecture comparison and normal openings

`distribution.py` compares the current mesh, lower-resistance paths retaining the original fuses, removal of transit fuses with old contact assumptions, and 80/40mΩ loop targets. It covers 120 regular 16/20-tile load configurations at 18.5/19/20V. Resistances are explicit assumptions or acceptance targets, not measured samples. Loads are specified at each protected tile input, including the planned conversion loss, not at a module output.

For the original 20-tile, 3W chain, minimum possible load current is 0.15A/tile. That already puts 3A through the first edge, four times its 25°C continuous budget or five times its 70°C budget. The far-end voltage upper bound falls from 20V to 10.281V in the first pass; its third bound is negative. Loss at those optimistic currents is already at least 20.559W, including 9.011W in transit fuses. This is a lower-bound argument, not a claimed operating point. The numerical all-on DC boundary is approximately 1.803W/tile; the fuse and voltage budgets are tighter.

The normal-opening sweep covers 891 states: positive-only, return-only and complete connection loss at every edge/Hub feed in the three 20-tile grids, for the fused mesh and both unfused resistance targets. At 19V all 297 states for each new target stay within the modeled DC limits. Every tested state for the original fused mesh is outside the hot continuous-current budget. A particular normal-load case at 20V raises a central-grid path from 0.612A to 0.790A after Hub feed 5 opens; it exceeds even the 25°C budget while all tiles remain powered. A missing return is solved separately, not treated as a positive fuse opening.

The new architecture targets support 20-tile, 3W center/edge/corner grids in the DC model. Twenty 3W tiles in a chain need the 40mΩ target at 19V; the 80mΩ target is limited to about 2.393W/tile there, with less allowed for operating margin. [Rev A](rev-a.md#distribution-recommendation) records the recommendation, current-path requirements and alternatives. The existing tile still has its transit fuses. It has not been converted to the new architecture or qualified for these target envelopes.

### Ground faults

The expanded sweep has 622 resistive snapshots: all 252 grid fault locations across 20/64 tiles and three Hub positions, each repeated after one incoming positive path opens; 99 single-return openings at the selected 20-tile fault locations; 13 individual return resistances increased tenfold; three combined positive/return openings; and three cases with every Hub branch disconnected. All solved with the default assumed ideal 1.5A/branch, 4.5A total limits. These are reference sources, not a simulation of the new latched input breaker.

Maximum return current remains 3.527996A at the 20-tile edge Hub with return edge (1,5) open. The wider fault-location sweep raises maximum positive-path current to 4.5A, at corner tile (0,0) of the central 20-tile grid after positive edge (0,1) opens. All source current then reaches that fault through one remaining fused path. The old selected-node results were not a worst-case bound. Complete removal of feeding branches gives zero steady source current; stored energy is excluded from that result.

The sweep is not exhaustive over simultaneous opens, unequal resistances, transient peaks, signal returns, temperature or normal loads during faults. No clearing time or connector temperature is inferred.
Sweeping all contact resistances together through 10/30/50/100/200mΩ kept the first maximum at 2.922361A. Uniform scaling preserves sharing here; it doesn't test one bad contact. At 30mΩ that gives 0.256W in the contact; at 200mΩ, 1.708W. At 3.528A and 30mΩ it's 0.373W. Those figures don't establish temperature limits.

A 1.5A Hub port limit doesn't keep every grid contact below 1.5A. One return could approach the whole 4.5A source limit. The SAMZO 5A listing isn't enough without loading, temperature and pulse conditions. Don't increase fuse ratings based on it. Cutting one port also won't clear a fault still fed through a loop.

### Stored energy and signals

At 20V, C21/C23 total nominal 0.8mJ over twenty tiles, directly or through F1. Local 11.1µF plus module 1µF per tile adds 48.4mJ if counted without isolation. The Hub now also has six 1µF port output capacitors in addition to the common 1µF capacitor. Every further 100µF at the Hub adds 20mJ. The six port capacitors plus the twenty tile buses total nominal 10µF, or 2.646mJ at 21V with an assumed +20% capacitance allowance. The common Hub and port input capacitors can contribute through switches before cutoff; they are separate from that directly connected output total. This excludes local 20V and 5V capacitors, attached modules and motors. Reverse blocking has a response time, so local capacitors can't simply be excluded. Hub capacitance, cable inductance, tolerance, cutoff timing and TVS/fuse energy still need checking together.

The 35.5V TVS clamp exceeds the connector's 30V continuous rating. Its unspecified 500V withstand test doesn't settle that. Nominal fuse melting I²t isn't maximum clearing energy either.

Missing GND can send return current through UART, DETECT, module or debug pins. The power-only model doesn't cover this. Buffer Ioff is tested at 5.5V; TMUX1511's powered-off limit is 3.6V. Neither makes 20V on a signal safe. Motor startup, stall and braking energy also need measurements.

## Fit and layout

The SAMZO fixture compiles and exports closed meshes with no nonmanifold edges. Center volume is 17,813.72mm³, neighbor 6,964.12mm³. Bounds: 56 × 56 × 20mm and 56 × 9.88 × 20mm, including the neighbor's 0.88mm overhang.

Plastic-only checks at 0/3/20mm lift and compression settings 0/0.5mm showed zero overlap volume. A conservative 20mm lift sweep did too. Touching faces remain. This doesn't test spring deformation, print tolerances, magnetic retention or the complete tile. [Fit tests](interfaces.md#fit-tests) are still needed.

The earlier 23E315050 STEP loaded as one valid solid in FreeCAD 1.1.4: X=-5.25..5.26, Y=-2.4..2.4, Z=-0.55..5.30mm. That isn't proof of mating. No SAMZO 03E315320 STEP is available, and the installed MCU model is missing. Full 3D checking isn't complete.

The added placement comprises eight 1206 UART series resistors, eight pull-ups, five control/sense resistors, one RGB resistor and three low-voltage bypass capacitors. North/South/West UART buffers now face their respective edges; their bypass capacitors moved with that choice. Four further 0805 parts now place the module ID bias/filter and the 5V fault/enable pulls near the MCU. The added parts are low-profile passives. Their purchase MPNs and maximum assembled heights still need confirmation; no switching or 20V components were placed.

PCB guides show a 68mm body and ±30mm mounting centers, not an outline or drilled holes. U8-U11 use 0.15mm local pad clearance for stock VSSOP lands; the default remains 0.2mm. This isn't clearance approval for 20V. All assigned footprint files resolve, but exact passive parts, temperature limits and assembly details still need review in [Rev A](rev-a.md).

The Hub CAD is only a 160 × 80 × 70mm envelope. USB openings, mounts and wiring are unfinished. The top fixture uses provisional 3.5mm contact pitch and 3/4mm guide pins; tilted and reversed insertion still need checking.

## Before ordering

1. Confirm connector data, channel numbering, plating, compression and fit. Check top-contact keying and accidental bridging.
2. Finish Hub cutoff and test faults through loops. Check fuses, contacts, TVS energy, reverse current, startup, brownout, leakage and ESD. Unknown module ID and reset must leave outputs off.
3. Test purchased MCU silicon with all four UARTs, RGB, I²C and PWM running. Check module ID tolerances and recovery.
4. Set PCB outline, stack, mounting and connector positions together with the enclosure. Check solder access, screws, magnets, roof clearance and LED visibility.
5. Route and review current loops, copper widths, returns, clearances and losses. Run DRC, inspect the 3D assembly, Gerbers, drills, BOM and pick-and-place. Confirm finish, stencil, reflow and assembly with the supplier.
6. Bring up 3-5 boards on a current-limited supply. Measure rails, ripple, temperature, contact drop, startup, faults and servo/motor loads in center, edge, corner, chain and grid layouts. Approve the rest only from those results.

Keep power off while moving tiles. Hot-plugging needs its own tests.
