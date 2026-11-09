// Unpowered Harwin side-compression test. No production tile geometry.
include <../common/tile_dimensions.scad>
$fn=40;
part="assembly"; // bed, slider, assembly
mate_y=19; // Nominal starting plane only; measure the spring front.
travel=0; // Set zero from measured first touch, never from this envelope.
assert(travel>=0 && travel<=0.5);
board_t=pcb_preview_thickness;
module bed() {
 difference() {
  union() {
   cube([56,52,3]);
   for(x=[3,50]) translate([x,3,3]) cube([3,44,7]);
   for(x=[7,47]) translate([x,20,3]) cylinder(d=4,h=5);
  }
  // A 40 x 28 mm horizontal coupon slides in from the rear.
  translate([7.8,19.8,6.8]) cube([40.4,29,board_t+0.4]);
  for(x=[4.5,51.5]) translate([x,8,-0.1]) cylinder(d=3.2,h=3.2);
 }
}
module slider() {
 difference() {
  union() {
   cube([46,10,3]);
   translate([0,1,3]) cube([46,4,12]);
  }
  // Vertical 40 x 12 mm flat-pad coupon; tin mate finish must be qualified.
  translate([2.8,3.8,3]) cube([40.4,board_t+0.4,13]);
  for(x=[4,42]) translate([x,7,-0.1]) hull() {
   cylinder(d=3.2,h=3.2);translate([0,1,0]) cylinder(d=3.2,h=3.2);
  }
 }
}
if(part=="bed" || part=="assembly") bed();
if(part=="slider") slider();
if(part=="assembly") {
 translate([5,mate_y-3.8+travel,3]) slider();
 if($preview) {
  color("green") translate([8,20,7]) cube([40,28,board_t]);
  color("darkgreen") translate([8,mate_y+travel,6]) cube([40,board_t,12]);
 }
}
// Use external clamps / a screw stage and measured shims for contact force.
// Slots locate coupons; their friction is not a force measurement.
