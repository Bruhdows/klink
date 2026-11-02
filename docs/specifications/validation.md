# Checks and results

The 20V board and new SAMZO connection haven't been assembled or physically tested. Small mechanical prints don't establish electrical safety. Rev A isn't ready to order.

## Current checks

- KiCad 10.0.8 ERC: 0 violations, exit 0, across all three sheets. The project excludes `single_global_label`, `four_way_junction`, `simulation_model_issue` and `footprint_filter` checks.
- Netlist: 130 components, 104 nets, including 16 intentional unconnected-pin nets. All 313 connectivity checks and 13 regression checks passed. An RTN-to-GND strap is correctly rejected.
- PCB: 25 low-voltage footprints, no tracks or fabrication outline. DRC exits 5: one missing-outline violation, 85 unconnected items and 104 missing-footprint parity issues. No other placement, field or net errors were reported.
- J3-J7 have no assigned footprints. J2 is excluded from the board. J1 and TP1-TP8 are bare copper.
- Both contact boards: DRC 0 violations, 0 unconnected items. Lands and finish still need approval. They have no schematic; ERC doesn't apply to them.
- Five custom footprint checks: native loading/pin counts passed; standalone DRC had 0 violations and 0 unconnected items. Assembly is untested.
- Schematic pages were rendered and reviewed. The cleanup kept all 104 net names, pin connections, component values and footprints unchanged.

Run KiCad's checks from the repo root:

```sh
kicad-cli sch erc --format json --severity-all --exit-code-violations \
  --output /tmp/klink-erc.json hardware/electronics/tile/tile.kicad_sch
kicad-cli sch export netlist --format kicadxml \
  --output /tmp/klink-netlist.xml hardware/electronics/tile/tile.kicad_sch
kicad-cli pcb drc --schematic-parity --format json --severity-all \
  --exit-code-violations --output /tmp/klink-drc.json \
  hardware/electronics/tile/tile.kicad_pcb
```

Passing ERC doesn't tell us whether protection, temperature or physical fit are okay.

## Power calculations

The model treats positive and ground paths separately. Default resistances:

- Contact 0.05Ω; copper 0.02Ω per conductor/link.
- Positive tile link 0.22Ω, including two nominal 0.075Ω fuses; ground link 0.07Ω.
- Hub branch: one tile fuse plus an assumed 0.15Ω switch.
- Local F1 + U7: 0.225Ω.

Only nominal fuse/eFuse values come from component data. Actual contact, copper, hot resistance and efficiency aren't measured. Each solved case checks power balance using local supply-to-ground voltage.

The 32 load cases cover 20/64 tiles, chains and grids, center/edge/corner Hub positions and 0.5/3/6/14W per tile after local protection. These are planning loads, including estimated conversion loss. The model doesn't limit normal-load current; it flags cases beyond assumed limits. It doesn't cover every layout, uneven contacts, heating or vertical interconnects.

Assumed Hub limits are 1.5A/branch, 4.5A total including tolerance, and 5W for the Hub. At 21V that is 99.5W. Actual hardware still needs to enforce it.

Selected results below give minimum protected voltage, maximum positive/ground current and input power including the Hub:

- 20 tiles, 0.5W each, chain: 18.316V, 0.531/0.531A, 15.62W.
- 20 tiles, 3W each, central grid: 19.638V, 0.594/0.611A, 65.84W.
- 20 tiles, 3W each, corner grid: 19.162V, 1.172/1.195A, 67.04W. Over the fuse continuous budget.
- 64 tiles, 0.5W each, central grid: 19.776V, 0.309/0.318A, 37.27W.
- 64 tiles, 3W each, central grid: 18.587V, 1.948/2.004A, 207.82W. Beyond power, fuse and source limits.
- 20 tiles at 3W and 64 tiles at 0.5W in chains didn't converge. That alone doesn't prove physical failure or establish startup behavior.

None is a tested operating point.

### Ground faults

Twelve cases put a 0.01Ω short at a selected tile beside the Hub, without ordinary loads. Ideal source limits were applied, then one incoming positive path was opened. Ground contact current reached 2.922A; remaining positive paths reached 3A.

A further 99 cases opened individual ground links in the three 20-tile grids, keeping positive fuses intact. Maximum ground current rose to 3.527996A, at the edge Hub with mesh edge (1,5) open. Total current was 4.499999A. These aren't all fault locations, combined faults or 64-tile open-ground cases. Signal returns and transient peaks aren't included.

Sweeping all contact resistances together through 10/30/50/100/200mΩ kept the first maximum at 2.922361A. Uniform scaling preserves sharing here; it doesn't test one bad contact. At 30mΩ that gives 0.256W in the contact; at 200mΩ, 1.708W. At 3.528A and 30mΩ it's 0.373W. Those figures don't establish temperature limits.

A 1.5A Hub port limit doesn't keep every grid contact below 1.5A. One return could approach the whole 4.5A source limit. The SAMZO 5A listing isn't enough without loading, temperature and pulse conditions. Don't increase fuse ratings based on it. Cutting one port also won't clear a fault still fed through a loop.

### Stored energy and signals

At 20V, C21/C23 total nominal 0.8mJ over twenty tiles, directly or through F1. Local 11.1µF plus module 1µF per tile adds 48.4mJ if counted without isolation. Every extra 100µF at the Hub adds 20mJ. Reverse blocking has a response time, so local capacitors can't simply be excluded. Hub capacitance, cable inductance, tolerance, cutoff timing and TVS/fuse energy still need checking together.

The 35.5V TVS clamp exceeds the connector's 30V continuous rating. Its unspecified 500V withstand test doesn't settle that. Nominal fuse melting I²t isn't maximum clearing energy either.

Missing GND can send return current through UART, DETECT, module or debug pins. The power-only model doesn't cover this. Buffer Ioff is tested at 5.5V; TMUX1511's powered-off limit is 3.6V. Neither makes 20V on a signal safe. Motor startup, stall and braking energy also need measurements.

## Fit and layout

The SAMZO fixture compiles and exports closed meshes with no nonmanifold edges. Center volume is 17,813.72mm³, neighbor 6,964.12mm³. Bounds: 56 × 56 × 20mm and 56 × 9.88 × 20mm, including the neighbor's 0.88mm overhang.

Plastic-only checks at 0/3/20mm lift and compression settings 0/0.5mm showed zero overlap volume. A conservative 20mm lift sweep did too. Touching faces remain. This doesn't test spring deformation, print tolerances, magnetic retention or the complete tile. [Fit tests](interfaces.md#fit-tests) are still needed.

The earlier 23E315050 STEP loaded as one valid solid in FreeCAD 1.1.4: X=-5.25..5.26, Y=-2.4..2.4, Z=-0.55..5.30mm. That isn't proof of mating. No SAMZO 03E315320 STEP is available, and the installed MCU model is missing. Full 3D checking isn't complete.

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
