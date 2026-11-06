
$fn = 48;
include <../common/tile_dimensions.scad>

// Tile dimensions
wall_thickness = 3;
roof_thickness = 4.5;

// Magnets
magnet_diameter = 6;
magnet_thickness = 3;
magnet_clearance = 0.25;
magnet_extra_depth = 0.2;
side_magnet_spacing = 18;
side_magnet_support_depth = 5.5;

// Top mounting
locator_spacing = 29;
locator_width = 4.5;
locator_depth = 2.8;
locator_clearance = 0.3;

// PCB mounting
pcb_post_diameter = 8;
pcb_hole_diameter = 2.2;

// Board body and mounting holes match the native tile PCB. Edge interfaces remain provisional.
// PCB preview
part = "base";
show_pcb_preview = true;

show_landing_pcb_preview = false;
landing_pcb_width = 17;
landing_pcb_height = 6;
landing_pcb_thickness = 1.6;
landing_pcb_front = 0.35; // Recessed from outer wall
landing_guide_clearance = 0.2;

// Legacy 04F spring/pad pockets. Not approved for SAMZO 03E315320 mating.
// Electrical edge interface
spring_window_width = 18;
spring_window_height = 7;
pad_window_width = 18;
pad_window_height = 7;
contact_window_depth = wall_thickness + 0.5;

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
            translate([x - 6, -tile_size/2, 4])
                cube([12, side_magnet_support_depth, 12]);
}

module top_mount_supports() {
    for (x = [-mount_spacing, mount_spacing])
        for (y = [-mount_spacing, mount_spacing])
            translate([x, y, tile_height - roof_thickness - 2])
                cylinder(d = 12, h = roof_thickness + 2);

    for (angle = [0, 90, 180, 270])
        rotate([0, 0, angle])
            translate([0, locator_spacing, tile_height - roof_thickness - 2])
                cylinder(d = 10, h = roof_thickness + 2);
}

module pcb_posts() {
    for (x = [-pcb_mount_spacing, pcb_mount_spacing])
        for (y = [-pcb_mount_spacing, pcb_mount_spacing])
            translate([x, y, pcb_mount_height])
                cylinder(
                    d = pcb_post_diameter,
                    h = tile_height - roof_thickness - pcb_mount_height + 0.3
                );
}

// Direction angles:
// 0 = South
// 90 = East
// 180 = North
// 270 = West

module contact_window(angle, width, height) {
    rotate([0, 0, angle])
        translate([
            -width/2,
            -tile_size/2 - 0.05,
            (tile_height - height)/2
        ])
            cube([
                width,
                contact_window_depth + 0.05,
                height
            ]);
}

module side_cutouts() {
    // Magnet pockets on all four edges
    on_edges()
        for (x = [-side_magnet_spacing, side_magnet_spacing])
            translate([x, -tile_size/2 - 0.05, tile_height/2])
                rotate([-90, 0, 0])
                    cylinder(
                        d = magnet_diameter + magnet_clearance,
                        h = magnet_thickness + magnet_extra_depth + 0.05
                    );

    // Spring connector openings
    // North and East
    for (angle = [180, 90])
        contact_window(angle, spring_window_width, spring_window_height);

    // Landing pad openings
    // South and West
    for (angle = [0, 270])
        contact_window(angle, pad_window_width, pad_window_height);
}

module top_cutouts() {
    for (xy = pcb_led_centers)
        translate([xy[0], xy[1], pcb_mount_height])
            cylinder(d = 3.2, h = tile_height-pcb_mount_height+0.1);

    for (x = [-mount_spacing, mount_spacing])
        for (y = [-mount_spacing, mount_spacing])
            translate([
                x, y,
                tile_height - magnet_thickness - magnet_extra_depth
            ])
                cylinder(
                    d = magnet_diameter + magnet_clearance,
                    h = magnet_thickness + magnet_extra_depth + 0.1
                );

    // Sockets for tracks and pillars.
    for (angle = [0, 90, 180, 270])
        rotate([0, 0, angle])
            translate([0, locator_spacing, tile_height - locator_depth])
                linear_extrude(height = locator_depth + 0.1, scale = 1.18)
                    square([
                        locator_width + locator_clearance,
                        locator_width + locator_clearance
                    ], center = true);
}

module pcb_holes() {
    for (x = [-pcb_mount_spacing, pcb_mount_spacing])
        for (y = [-pcb_mount_spacing, pcb_mount_spacing])
            translate([x, y, pcb_mount_height - 0.05])
                cylinder(
                    d = pcb_hole_diameter,
                    h = tile_height - roof_thickness - pcb_mount_height - 0.2
                );
}

module pcb_preview() {
    color([0, 0.7, 0.2, 0.65])
        difference() {
            union() {
                // Main PCB
                translate([
                    -pcb_preview_size/2,
                    -pcb_preview_size/2,
                    pcb_mount_height - pcb_preview_thickness
                ])
                    cube([
                        pcb_preview_size,
                        pcb_preview_size,
                        pcb_preview_thickness
                    ]);
            }

            // Four mounting holes
            for (x = [-pcb_mount_spacing, pcb_mount_spacing])
                for (y = [-pcb_mount_spacing, pcb_mount_spacing])
                    translate([
                        x, y,
                        pcb_mount_height - pcb_preview_thickness - 0.1
                    ])
                        cylinder(
                            d = pcb_preview_hole_diameter,
                            h = pcb_preview_thickness + 0.2
                        );
        }
}

module landing_board_front_stops() {
    // South = 0, West = 270
    for (angle = [0, 270])
        rotate([0, 0, angle])
            for (side = [-1, 1])
                translate([
                    side == -1 ? -10 : 7,
                    -tile_size/2,
                    (tile_height - pad_window_height)/2
                ])
                    cube([
                        3,    // Stop width
                        0.3,  // Provisional depth
                        pad_window_height
                    ]);
}

module landing_board_rear_guides() {
    // South = 0, West = 270
    for (angle = [0, 270])
        rotate([0, 0, angle])
            for (side = [-1, 1])
                translate([
                    side == -1 ? -10 : 7.5,
                    -tile_size/2 + landing_pcb_front
                        + landing_pcb_thickness + landing_guide_clearance,
                    0
                ])
                    cube([2.5, 1.2, 13.5]);
}

module landing_pcb_preview() {
    // South and West landing PCBs
    for (angle = [0, 270])
        rotate([0, 0, angle]) {
            // Vertical PCB carrier
            color([0.0, 0.65, 0.2, 0.65])
                translate([
                    -landing_pcb_width/2,
                    -tile_size/2 + landing_pcb_front,
                    (tile_height - landing_pcb_height)/2
                ])
                    cube([
                        landing_pcb_width,
                        landing_pcb_thickness,
                        landing_pcb_height
                    ]);

            // Five copper landing pads
            for (i = [0:4])
                color([0.95, 0.72, 0.15])
                    translate([
                        -5.75 + i*2.5,
                        -tile_size/2 + landing_pcb_front - 0.05,
                        tile_height/2 - 1.5
                    ])
                        cube([1.5, 0.05, 3]);
        }
}

module base_tile() {
    union() {
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

        // Small stops for landing-pad PCBs
        landing_board_front_stops();
        landing_board_rear_guides();
    }
}

if (part == "pcb_fit") intersection() { base_tile(); translate([0,0,-0.01]) pcb_preview(); }
else base_tile();

if ($preview && show_pcb_preview)
    pcb_preview();

if ($preview && show_landing_pcb_preview)
    landing_pcb_preview();
