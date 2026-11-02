// Adjustable unpowered fit coupon. Slots are not a manufacturer connector model.
include <../common/tile_dimensions.scad>
$fn = 48;

pcb_thickness = pcb_preview_thickness;
slot_clearance = 0.25;
rail_length = 26;
board_width = 18;
base_thickness = 3;
wall = 3;
connector_axis_height = 10;
connector_window_width = 18;
connector_window_height = 7;
board_setback = 3;
slot_travel = 10;
separation = 8;
show_boards = true;

assert(pcb_thickness > 0 && slot_clearance > 0);
assert(connector_axis_height > base_thickness);
assert(board_setback >= 0);

module coupon() {
    difference() {
        union() {
            cube([board_width + 2*wall, rail_length, base_thickness]);
            for (x = [0, board_width + wall])
                translate([x, 0, base_thickness])
                    cube([wall, rail_length, connector_axis_height]);
            translate([0, rail_length-wall, 0])
                cube([board_width + 2*wall, wall, tile_height]);
        }
        for (x = [wall/2, board_width + 1.5*wall])
            translate([x, rail_length/2, -0.1])
                hull() {
                    translate([0, -slot_travel/2, 0]) cylinder(d=2.8, h=base_thickness+0.2);
                    translate([0, slot_travel/2, 0]) cylinder(d=2.8, h=base_thickness+0.2);
                }
        translate([(board_width + 2*wall-connector_window_width)/2,
                   rail_length-wall-0.1, connector_axis_height-connector_window_height/2])
            cube([connector_window_width, wall+0.2, connector_window_height]);
        for (x = [wall-pcb_thickness/2, board_width+wall-pcb_thickness/2])
            translate([x-slot_clearance/2, board_setback, base_thickness+1])
                cube([pcb_thickness+slot_clearance, rail_length, pcb_thickness+slot_clearance]);
    }
}

coupon();
translate([board_width+2*wall+separation, 0, 0]) coupon();

if ($preview && show_boards)
    for (x = [wall, board_width + 3*wall + separation])
        color([0,0.6,0.2,0.5])
            translate([x, board_setback, base_thickness+1])
                cube([board_width, rail_length-board_setback-wall, pcb_thickness]);
