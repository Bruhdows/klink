// Packaging study only. Connector markers show grid centers, not mating geometry.
include <../common/tile_dimensions.scad>
$fn = 48;
height = 70;
wall = 3;
floor_thickness = 3;
show_grid = true;
show_connector_axes = true;

module envelope() {
    difference() {
        translate([-tile_size,-tile_size/2,0]) cube([2*tile_size,tile_size,height]);
        translate([-tile_size+wall,-tile_size/2+wall,floor_thickness])
            cube([2*tile_size-2*wall,tile_size-2*wall,height]);
    }
}

envelope();
if ($preview && show_connector_axes) {
    for (x = [-tile_size/2,tile_size/2])
        for (y = [-tile_size/2,tile_size/2])
            color("red") translate([x,y,10]) sphere(d=3);
    for (x = [-tile_size,tile_size])
        color("red") translate([x,0,10]) sphere(d=3);
}
if ($preview && show_grid)
    for (x = [-tile_size/2,tile_size/2])
        color([0.2,0.4,0.8,0.2]) translate([x-tile_size/2,-tile_size/2,-1])
            cube([tile_size,tile_size,1]);
