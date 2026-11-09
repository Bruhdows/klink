# Mechanical sources and exports

[Open assembly.FCStd](assembly.FCStd) for the integrated reference assembly. It contains sixteen tile PCB instances, Hub/elevator electronics, the gate service PCB, button/sensor bench boards, the printed lift and gravity return, the idler bearing/spacer stack, eighteen M6 rods and a drilled reference baseboard. Lift and return parts remain separate reusable objects. Guards are included but hidden for inspection. Motor, bearing and servo geometry is nominal dimensional envelope data where labelled.

[Assembly SCAD](assembly.scad) provides the mechanical reference without PCB component models. Individual editable sources are in `base/`, `hub/`, `elevator/`, `modules/` and `tracks/`. Shared datums, fastening allowances and the reference kit layout are in `common/`. The layout is not a qualified electrical power topology. Individual tile/Hub case sources use Z=0 underneath. The integrated assembly instead puts tile tops at Z=0 and case bottoms at Z=-20: tile PCB tops are Z=-11, the elevated Hub PCB top is Z=10, and the lift PCB top is Z=90. PCB STEP previews have their top plane at zero before placement.

## Exports

[step/](step/) contains individual mechanical STEP exports. Most come from OpenSCAD CSG imported as BRep primitives and booleans. The base, two lift-guide halves and two return profiles are faceted BRep conversions from current closed print meshes because those sweeps did not import as valid CSG solids. They are labelled export geometry, not parametric design sources. Edit the SCAD files to change dimensions.

Print STLs are in the relevant `print/` directories, plus the base and Hub enclosure STLs beside their sources. The straight-track STL has been regenerated. Lift guards/guides, frame overhangs, sprockets, return saddles and ramps need slicer orientation/support review. A closed mesh is not a successful print or endurance test.

[pcb/](pcb/) contains KiCad component/board STEP previews. The tile MCU's declared WQFN model and Hub oscillator's Abracon ASE model do not resolve. Eight footprint types across the three main boards have no declared model, including copper-only pads and physical custom parts. Inductors and protection-package heights therefore need drawing-based review and physical checks. Missing parts were not replaced with invented detailed models.

The [interface drawing](drawings/interfaces.svg) records board dimensions, mounting datums, stack height, USB openings and magnet orientation. It is a dimension reference, not a 1:1 drilling template. Use the [drilling and cutting CSVs](../manufacturing/README.md) for the reference baseboard.

## Assembly sequence

Dry fit the ordinary M2 nuts before fitting PCBs. Tile screws enter from the open underside; Hub nuts load from below its floor; elevator nuts load below the PCB tongues. The current choices are M2x8 for tile, M2x30 plus a nominal 0.6mm washer stack for the elevated Hub PCB, M2x10 for elevator and M2x6 for the gate service board. Check screw tips and package clearance before tightening.

Install magnets with the fixed cardinal polarity in [interfaces](../../docs/specifications/interfaces.md#fastening-and-magnet-orientation). Check fit, polarity and adhesive retention on a sample. Keep metal and loose magnets away from exposed contacts.

Build and hand-cycle a short chain before all thirty links. The nominal idler stack is a recessed M3x40 cap screw, 2.5mm front spacer, 623-2Z bearing, 25mm rear spacer, frame, rear washer and nut. The spacers are intended to contact the inner race. Verify the purchased bearing, screw head, shaft/seat fit and end clearance; this is not a tested clamp stack.

Secure the frame and return supports before adding marbles or power. The reference baseboard is 12mm thick; rod lengths include 8mm below it for a washer, nut and thread. Recalculate before cutting if the purchased board or hardware differs. Use the supplied FS90 horn on the gate; its engagement and slot alignment need a real sample.

## Remaining integration work

Production edge contacts, recesses, compression and the keyed top-contact assembly remain unreleased. Button/sensor cases, off-board optical mounts and final harness paths are unfinished. The gate and sensor still need integration into the chosen interactive marble route; the current assembly is a clearance/reference layout. Some fastener envelopes and missing electronic models are absent, so no full collision qualification is claimed.

The recorded limited CAD checks include the nominal gate-servo envelope and a 0-90 degree flap sweep sampled every 5 degrees, which have empty intersections with the printed gate base. These do not cover the supplied horn, actual screws, printing tolerances, servo calibration or load.

The Hub case is 42mm high with its PCB top at Z=30mm. The two 20x10mm USB openings are above adjacent tile bodies and 5.5mm module bases. The six-neighbor CAD plug-envelope check is empty; the old Z=9mm board stack failed it. Tall neighboring modules, cable overmoulds and actual lead strain relief remain checks. Unplug both Hub cables before removing adjacent tiles vertically.
