// FS90 flap-gate prototype. Use supplied servo horn, not a printed spline.
// FEETECH FS90-C V1.0: body 23.2 x 12.5 x 22mm, overall output depth 27.3mm.
// Horn screw pattern, clamp force and axle alignment require an actual sample.
include <../common/tile_dimensions.scad>
use <../tracks/straight_track.scad>
$fn=48;
part="assembly"; // base, flap, clamp, assembly
axis_z=25.8;
clearance=0.25;
module x_cylinder(d,h) { rotate([0,90,0]) cylinder(d=d,h=h); }
module servo_reference() {
 translate([14,-6.25,8.5]) cube([22,12.5,23.2]);
 translate([8.7,0,axis_z]) x_cylinder(4.8,5.3);
}
module gate_base() {
 difference() {
  union() {
   straight_track();
   // Left axle support, clear of the 22mm channel envelope.
   translate([-17,-5,5.5]) cube([5,10,axis_z-5.5]);
   translate([-17,0,axis_z]) x_cylinder(10,5);
   // Vertical 40x30mm service PCB: top plane X=-31, center Y=0,Z=22.
   translate([-37,-23,5.5]) cube([3,46,33]);
   for(y=[-17,17]) for(z=[10,34]) translate([-34,y,z]) x_cylinder(6,1.4);
   // Two servo cradle ribs and clamp-screw towers, outside the track.
   for(y=[-8.5,7]) translate([13,y,5.5]) cube([24,1.5,24]);
   translate([13,-8.5,5.5]) cube([24,17,3]);
   for(y=[-13,13]) translate([25,y,5.5]) cylinder(d=8,h=26);
  }
  translate([-17.1,0,axis_z]) x_cylinder(3.2,5.2);
  for(y=[-17,17]) for(z=[10,34]) {
   translate([-37.1,y,z]) x_cylinder(2.2,4.7);
   translate([-37.1,y,z]) rotate([0,90,0]) cylinder(d=4.3/cos(30),h=1.9,$fn=6);
  }
  // Nominal case clearance. Do not use nominal dimensions to force a servo in.
  translate([14-clearance,-6.25-clearance,8.5]) cube([22+2*clearance,12.5+2*clearance,24]);
  for(y=[-13,13]) {
   translate([25,y,-.1]) cylinder(d=2.2,h=35);
   translate([25,y,5.5]) cylinder(d=pcb_nut_af/cos(30),h=pcb_nut_depth,$fn=6);
   translate([18,y-pcb_nut_af/2,5.5]) cube([7,pcb_nut_af,pcb_nut_depth]);
  }
  // Eight-pin bench harness exit; spring interface remains unreleased.
  translate([30,15,-.1]) cube([8,12,6]);
 }
}
module flap() {
 difference() {
  union() {
   intersection() {
    translate([-10.5,-1.5,-20]) cube([21,3,20]);
    translate([0,-1.5,16.5-axis_z]) rotate([-90,0,0]) cylinder(r=10.5,h=3);
   }
   translate([-11.75,0,0]) x_cylinder(6,23.75);
   translate([8.4,0,0]) x_cylinder(8,3.6);
   // Slotted horn attachment uses the supplied horn and its hardware.
   translate([9,-7,-2]) cube([3,14,4]);
  }
  translate([-12.1,0,0]) x_cylinder(3.2,24.2);
  translate([8.4,0,0]) x_cylinder(5.5,3.8);
  for(y=[-4,4]) translate([8.9,y,0]) hull() {
   x_cylinder(1.8,3.2);translate([0,2,0]) x_cylinder(1.8,3.2);
  }
 }
}
module clamp() {
 difference() {
  translate([20,-16,0]) cube([10,32,3]);
  for(y=[-13,13]) translate([25,y,-.1]) cylinder(d=2.5,h=3.2);
 }
}
if(part=="base") gate_base();
else if(part=="flap") translate([0,3,7]) rotate([90,0,0]) flap();
else if(part=="clamp") clamp();
else if(part=="motion_collision") for(a=[0:5:90]) intersection() {
 gate_base();translate([0,0,axis_z]) rotate([a,0,0]) flap();
}
else if(part=="servo_collision") intersection() { gate_base();servo_reference(); }
else {
 color([.25,.45,.55]) gate_base();
 color("orange") translate([0,0,axis_z]) flap();
 color("silver") translate([0,0,31.7]) clamp();
 if($preview) color([.2,.2,.2,.4]) servo_reference();
}
