# Fabrication drafts

These files support quotation and prototype review. They are not a production release. [validation.json](validation.json) records native KiCad 10.0.8 ERC/DRC results and source hashes from 2026-11-09. No assembled-board test is claimed.

## Included layouts

Elevator, button, marble sensor and gate have zero native ERC violations, physical DRC violations, unconnected items and schematic-parity errors. Their folders contain Gerbers, separated plated/non-plated drills, a drill map, `gerbers.zip`, the engineering BOM, SMT positions, an assembly BOM and CPL.

The four contact-test folders contain coupon Gerbers and drills. Their five channels have no product power/signal assignment. The new side-contact pair has zero native DRC violations and unconnected items. Verify compression, continuity, finish and temperature before assigning bus functions. See [interfaces](../../docs/specifications/interfaces.md).

Tile and Hub fabrication packages are deliberately absent. The tile has 117 unconnected items and five unreleased connector footprints. The Hub has 407 unconnected items. A zero physical-violation count does not make either board complete.

## Board and assembly data

The elevator is a 60x44mm notched, 1.6mm four-layer board. Its copper layer order is F.Cu, In1.Cu, In2.Cu, B.Cu. The inner reference/return behavior and converter/motor loops still need review against the selected fabricator stackup and physical loads.

Button, sensor and gate service boards are two-layer, 1.6mm prototypes. The button and gate are 40x30mm; the sensor is 50x36mm. Purchased components are on the front. Hand assemble their headers, switch and off-board optical wiring with owned tools. They do not release the keyed spring interface.

`positions.csv` is KiCad's native SMT-only export in mm. `cpl.csv` translates its headers and normalizes rotation to 0-360 degrees. Gerbers, drills and positions use the absolute KiCad origin, with Y negated in Cartesian placement output. Do not re-zero one file independently. The assembly BOM contains exactly the SMT references in the CPL that have selected MPNs. The engineering BOM also contains manually fitted and off-board items. Blank LCSC codes require sourcing; they do not authorize automatic substitution.

Pin-1 polarity and stock-footprint rotations still require the assembler's placement preview. Reconcile every selected part, package and LCSC/JLC classification. Hidden joints require the supplier's stencil and X-ray review. A prototype population is required before ordering sixteen tile assemblies.

The tile's exposed-pad ground via now sits outside solder lands. Its tracked custom rule file permits only the localized 0.10mm GND fanout with 0.125mm clearance; board-wide rules remain unchanged. Confirm that geometry with the fabricator. Isolated LOCAL_RTN, MODULE_RTN and AUX_RTN must never be replaced by GND fills.

## Mechanical data

[rod-cut-list.csv](rod-cut-list.csv) fits eighteen M6 rods into five 1m bars, including 2mm kerf per cut and 4mm end trim per bar. [baseboard-drill.csv](baseboard-drill.csv) contains eighteen 6.5mm rod holes and thirty-six 4.5mm foot-fixing holes. Coordinates are given in CAD datums and from the lower-left corner of the 700x700x12mm reference board. Confirm actual board thickness, washer/nut stack and rod retention before cutting or drilling.

The [CAD directory](../cad/README.md) contains individual STEP/STL parts, source CAD, an integrated FreeCAD assembly and dimension references. Mesh exports and nominal component envelopes do not establish physical fit.

## Reproduce native checks

For a circuit board, run these commands with KiCad 10 installed, replacing `BOARD` with its directory/name:

```sh
kicad-cli sch erc --severity-all --exit-code-violations hardware/electronics/BOARD/BOARD.kicad_sch
kicad-cli pcb drc --schematic-parity --severity-all --exit-code-violations hardware/electronics/BOARD/BOARD.kicad_pcb
```

The tile/Hub checks report unfinished connectivity. Read the categories, not only the exit code. Firmware builds and protocol tests are described in [firmware](../../firmware/README.md). Contact/protection, thermal, EMC, motor and print-fit qualification remain the [prototype plan](../../docs/specifications/prototype-plan.md).
