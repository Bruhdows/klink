
$fn = 64;
include <../common/tile_dimensions.scad>

// Tile
tile_thickness = 5.5;

// Track
track_width = 28;
track_height = 11;
channel_radius = 11;

// Magnets
magnet_diameter = 6;
magnet_thickness = 3;
magnet_clearance = 0.25;
magnet_extra_depth = 0.2;
magnet_spacing = mount_spacing;

module track_body() {
    union() {
        translate([-tile_size/2, -tile_size/2, 0])
            cube([tile_size, tile_size, tile_thickness]);

        translate([
            -track_width/2,
            -tile_size/2,
            tile_thickness
        ])
            cube([track_width, tile_size, track_height]);
    }
}

module marble_channel() {
    translate([
        0,
        tile_size/2 + 0.1,
        tile_thickness + track_height
    ])
        rotate([90, 0, 0])
            cylinder(
                r=channel_radius,
                h=tile_size + 0.2
            );
}

module magnet_pockets() {
    for (x = [-magnet_spacing, magnet_spacing])
        for (y = [-magnet_spacing, magnet_spacing])
            translate([x, y, -0.05])
                cylinder(
                    d=magnet_diameter + magnet_clearance,
                    h=magnet_thickness + magnet_extra_depth + 0.05
                );
}

module straight_track() {
    difference() {
        track_body();
        marble_channel();
        magnet_pockets();
    }
}

straight_track();
