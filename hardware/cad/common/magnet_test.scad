$fn = 48;

// Match the magnet dimensions in base_tile.scad.
magnet_diameter = 6;
magnet_thickness = 3;
magnet_clearance = 0.25;
magnet_extra_depth = 0.2;
magnet_spacing = 18;

piece_width = 50;
piece_depth = 14;
piece_height = 20;
print_spacing = 10;

module magnet_test_piece() {
    difference() {
        translate([-piece_width/2, -piece_depth/2, 0])
            cube([piece_width, piece_depth, piece_height]);

        for (x = [-magnet_spacing, magnet_spacing])
            translate([x, -piece_depth/2-0.05, piece_height/2])
                rotate([-90, 0, 0])
                    cylinder(
                        d=magnet_diameter+magnet_clearance,
                        h=magnet_thickness+magnet_extra_depth+0.05
                    );
    }
}

// Two separate pieces for a single print.
translate([-(piece_width+print_spacing)/2, 0, 0])
    magnet_test_piece();

translate([(piece_width+print_spacing)/2, 0, 0])
    magnet_test_piece();
