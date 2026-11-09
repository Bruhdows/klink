// Keying/compression coupon only. Contact holes are provisional, not approved pogo seats.
include <../common/tile_dimensions.scad>
$fn = 48;
part = "assembly"; // assembly, tile, module
contact_pitch = 3.5;
contact_hole_diameter = 1.6;
contact_count = 8;
plate_width = 44;
plate_depth = 24;
plate_thickness = 3;
key_diameters = [3, 4];
key_positions = [[-18,-8],[18,8]];
key_clearance = 0.3;
key_height = 8;
layout_gap = 8;

assert((contact_count-1)*contact_pitch + contact_hole_diameter < plate_width-8);

module contact_holes() {
    for (i = [0:contact_count-1])
        translate([(i-(contact_count-1)/2)*contact_pitch,0,-0.1])
            cylinder(d=contact_hole_diameter,h=plate_thickness+0.2);
}

module plate() {
    translate([-plate_width/2,-plate_depth/2,0])
        cube([plate_width,plate_depth,plate_thickness]);
}

module tile_coupon() {
    difference() { plate(); contact_holes(); }
    for (i = [0:1])
        translate([key_positions[i][0],key_positions[i][1],plate_thickness-0.1])
            cylinder(d=key_diameters[i],h=key_height+0.1);
}

module module_coupon() {
    difference() {
        plate();
        contact_holes();
        for (i = [0:1])
            translate([key_positions[i][0],key_positions[i][1],-0.1])
                cylinder(d=key_diameters[i]+key_clearance,h=plate_thickness+0.2);
    }
}

if(part=="tile") tile_coupon();
else if(part=="module") module_coupon();
else { tile_coupon(); translate([plate_width+layout_gap,0,0]) module_coupon(); }
