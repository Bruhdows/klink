
$fn = 48;

// Tile dimensions
tile_size = 80;
tile_height = 20;
wall_thickness = 3;
roof_thickness = 4.5;

// Magnets
magnet_diameter = 6;
magnet_thickness = 3;
magnet_clearance = 0.25;
magnet_extra_depth = 0.2;
side_magnet_spacing = 18;

// Top mounting
mount_spacing = 24;
locator_spacing = 29;
locator_width = 4.5;
locator_depth = 2.8;
locator_clearance = 0.3;

// PCB mounting
pcb_mount_spacing = 30;
pcb_mount_height = 9;
pcb_post_diameter = 8;
pcb_hole_diameter = 2.2;

// Electrical contacts
contact_width = 18;
contact_height = 7;
contact_recess_depth = 0;

// Preview spacing between parts
preview_gap = 0.4;

// Render options:
// "tile" - Single base tile
// "pair" - Two adjacent tiles
// "test" - Two small pieces for testing magnets
render_mode = "tile";

module on_edges() {
    for (angle = [0, 90, 180, 270])
        rotate([0, 0, angle])
            children();
}

module shell() {
    difference() {
        translate([-tile_size/2, -tile_size/2, 0])
            cube([tile_size, tile_size, tile_height]);

        translate([
            -tile_size/2 + wall_thickness,
            -tile_size/2 + wall_thickness,
            -0.1
        ])
            cube([
                tile_size - 2*wall_thickness,
                tile_size - 2*wall_thickness,
                tile_height - roof_thickness + 0.1
            ]);
    }
}

module side_magnet_supports() {
    on_edges()
        for (x = [-side_magnet_spacing, side_magnet_spacing])
            translate([x-6, -tile_size/2, 4])
                cube([12, 9, 12]);
}

module top_mount_supports() {
    for (x = [-mount_spacing, mount_spacing])
        for (y = [-mount_spacing, mount_spacing])
            translate([x, y, tile_height-roof_thickness-2])
                cylinder(d=12, h=roof_thickness+2);

    for (angle = [0, 90, 180, 270])
        rotate([0, 0, angle])
            translate([0, locator_spacing, tile_height-roof_thickness-2])
                cylinder(d=10, h=roof_thickness+2);
}

module pcb_posts() {
    for (x = [-pcb_mount_spacing, pcb_mount_spacing])
        for (y = [-pcb_mount_spacing, pcb_mount_spacing])
            translate([x, y, pcb_mount_height])
                cylinder(
                    d=pcb_post_diameter,
                    h=tile_height-roof_thickness-pcb_mount_height+0.3
                );
}

module side_cutouts() {
    on_edges() {
        for (x = [-side_magnet_spacing, side_magnet_spacing])
            translate([
                x,
                -tile_size/2-0.05,
                tile_height/2
            ])
                rotate([-90, 0, 0])
                    cylinder(
                        d=magnet_diameter+magnet_clearance,
                        h=magnet_thickness+magnet_extra_depth+0.05
                    );

        // Disabled until the electrical connector is selected
        if (contact_recess_depth > 0)
            translate([
                -contact_width/2,
                -tile_size/2-0.05,
                (tile_height-contact_height)/2
            ])
                cube([
                    contact_width,
                    contact_recess_depth+0.05,
                    contact_height
                ]);
    }
}

module top_cutouts() {
    // Magnet pockets
    for (x = [-mount_spacing, mount_spacing])
        for (y = [-mount_spacing, mount_spacing])
            translate([
                x, y,
                tile_height-magnet_thickness-magnet_extra_depth
            ])
                cylinder(
                    d=magnet_diameter+magnet_clearance,
                    h=magnet_thickness+magnet_extra_depth+0.1
                );

    // Alignment sockets for modules and pillars
    for (angle = [0, 90, 180, 270])
        rotate([0, 0, angle])
            translate([
                0,
                locator_spacing,
                tile_height-locator_depth
            ])
                linear_extrude(
                    height=locator_depth+0.1,
                    scale=1.18
                )
                    square([
                        locator_width+locator_clearance,
                        locator_width+locator_clearance
                    ], center=true);
}

module pcb_holes() {
    for (x = [-pcb_mount_spacing, pcb_mount_spacing])
        for (y = [-pcb_mount_spacing, pcb_mount_spacing])
            translate([x, y, pcb_mount_height-0.05])
                cylinder(
                    d=pcb_hole_diameter,
                    h=tile_height-roof_thickness-pcb_mount_height-0.2
                );
}

module base_tile() {
    difference() {
        union() {
            shell();
            side_magnet_supports();
            top_mount_supports();
            pcb_posts();
        }

        side_cutouts();
        top_cutouts();
        pcb_holes();
    }
}

module magnet_test_piece() {
    difference() {
        translate([-25, -7, 0])
            cube([50, 14, tile_height]);

        for (x = [-side_magnet_spacing, side_magnet_spacing])
            translate([x, -7.05, tile_height/2])
                rotate([-90, 0, 0])
                    cylinder(
                        d=magnet_diameter+magnet_clearance,
                        h=magnet_thickness+magnet_extra_depth+0.05
                    );
    }
}

if (render_mode == "pair") {
    base_tile();

    translate([tile_size+preview_gap, 0, 0])
        base_tile();
}
else if (render_mode == "test") {
    magnet_test_piece();

    translate([0, -14-preview_gap, 0])
        rotate([0, 0, 180])
            magnet_test_piece();
}
else {
    base_tile();
}
