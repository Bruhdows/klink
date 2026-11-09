// V1 mechanical reference assembly. Actual PCB component models are in assembly.FCStd.
include <common/tile_dimensions.scad>
include <common/kit_layout.scad>
use <base/base_tile.scad>
use <hub/hub_envelope.scad>
use <elevator/elevator.scad>
use <tracks/continuous_return.scad>
use <modules/gate.scad>
part="assembly"; // assembly, elevator, return, bases
module bases() {
 for(q=kit_tiles) translate([q[0],q[1],-tile_height]) base_tile();
 translate([kit_hub_center[0],kit_hub_center[1],-tile_height]) envelope();
}
if(part=="assembly" || part=="bases") color([0.25,0.45,0.55]) bases();
if(part=="assembly" || part=="elevator") color([0.65,0.68,0.72]) elevator_assembly();
if(part=="assembly" || part=="return") color([0.88,0.65,0.22]) return_assembly();

if($preview && part=="assembly") color([.55,.43,.29]) support_board();
if(part=="assembly" || part=="gate") translate([-120,80,0]) {
 color([.25,.45,.55]) gate_base();
 color([.90,.40,.15]) translate([0,0,25.8]) flap();
 color([.65,.67,.70]) translate([0,0,31.7]) clamp();
}
