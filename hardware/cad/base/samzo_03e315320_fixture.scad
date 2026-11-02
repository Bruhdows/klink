// Unpowered fixture, not the production enclosure. See interfaces.md.
include <../common/tile_dimensions.scad>
include <../common/connector_03e315320.scad>
$fn = 48;
part = "assembly"; // assembly, center, neighbor, collision, lift_sweep
show_envelopes = true;
fixture_size = 56;
neighbor_depth = 9;
floor_height = 3;
wall_depth = 5.5;
board_bottom = 4;
board_clearance = 0.25;
face_recess = 2;
compression = 0; // NO rated stroke available. Zero is nominal first touch only.
lateral_offset = 0;
vertical_offset = 0;
center_lift = 0;
neighbor_gap = 0;
magnet_spacing = 18;
magnet_diameter = 6.25; // same 6x3 magnet + clearance as tile
magnet_depth = 3.2;
board_face = fixture_size/2-face_recess;
mate_face = board_face+samzo_free_height-compression;
axis_height = board_bottom+samzo_test_board_height/2;

assert(compression >= 0 && compression <= 0.5,
       "Fixture adjustment bound only; 0.5mm is NOT a rated spring deflection");
assert(abs(lateral_offset) <= 1 && abs(vertical_offset) <= 1);
assert(samzo_peg_length+0.2 < pcb_preview_thickness);

// Local coordinates: X along edge, +Y outward, Z up. All connector slots open upward.
module magnet_holes(y, outward=1) {
    for (x=[-magnet_spacing,magnet_spacing])
        translate([x,y-outward*magnet_depth/2,axis_height])
            rotate([90,0,0]) cylinder(d=magnet_diameter,h=magnet_depth+0.02,center=true);
}
module holder(face, reverse=false) {
    back = reverse ? face : face-pcb_preview_thickness;
    lo = reverse ? face-0.15 : face-pcb_preview_thickness-1;
    hi = reverse ? face+pcb_preview_thickness+1 : face+0.15;
    for (x=[-1,1])
        translate([x*(samzo_test_board_width/2+0.8),back+pcb_preview_thickness/2,board_bottom])
            difference() {
                translate([0,0,6]) translate([0,(lo+hi)/2-(back+pcb_preview_thickness/2),0])
                    cube([2.2,hi-lo,12],center=true);
                translate([-x*0.65,0,6.1])
                    cube([1.5,pcb_preview_thickness+board_clearance,12.3],center=true);
            }
    // Bottom ledge supports the carrier without trapping its upper edge.
    translate([-12,back,floor_height]) cube([24,pcb_preview_thickness,1]);
}
module center() {
    difference() {
        union() {
            translate([-fixture_size/2,-fixture_size/2,0]) cube([fixture_size,fixture_size,floor_height]);
            difference() {
                translate([-fixture_size/2,-fixture_size/2,0]) cube([fixture_size,fixture_size,tile_height]);
                translate([-fixture_size/2+wall_depth,-fixture_size/2+wall_depth,floor_height])
                    cube([fixture_size-2*wall_depth,fixture_size-2*wall_depth,tile_height]);
            }
        }
        for (a=[0,90,180,270]) rotate([0,0,a]) {
            translate([-13,fixture_size/2-wall_depth-0.1,floor_height]) cube([26,wall_depth+0.2,tile_height]);
            // Clear the neighboring carrier overhang through the floor during a vertical lift.
            translate([-13,board_face+samzo_free_height-0.5-0.35,-0.1])
                cube([26,face_recess+1,tile_height+0.2]);
            magnet_holes(fixture_size/2);
        }
    }
    for (a=[0,90,180,270]) rotate([0,0,a]) holder(board_face);
}
module neighbor() {
    difference() {
        translate([-fixture_size/2,fixture_size/2+neighbor_gap,0]) cube([fixture_size,neighbor_depth,tile_height]);
        translate([-13,fixture_size/2-0.1,floor_height]) cube([26,neighbor_depth-2,tile_height]);
        magnet_holes(fixture_size/2+neighbor_gap,-1);
    }
    translate([lateral_offset,0,vertical_offset]) holder(mate_face+neighbor_gap,true);
}
module envelopes() {
    // Transparent blocks are manufacturer envelopes, not STEP or contact profiles.
    for (a=[0,90,180,270]) rotate([0,0,a]) {
        color([0,0.5,0,0.5]) translate([-10,board_face-pcb_preview_thickness,board_bottom+center_lift])
            cube([20,pcb_preview_thickness,12]);
        color([1,0.6,0,0.5]) translate([-samzo_body_width/2,board_face,axis_height-samzo_body_depth/2+center_lift])
            cube([samzo_body_width,samzo_free_height,samzo_body_depth]);
        color([0,0.4,0.8,0.5]) translate([-10+lateral_offset,mate_face+neighbor_gap,board_bottom+vertical_offset])
            cube([20,pcb_preview_thickness,12]);
    }
}
if (part=="center" || part=="assembly") translate([0,0,center_lift]) center();
if (part=="neighbor") translate([0,-fixture_size/2,0]) neighbor();
if (part=="assembly") for (a=[0,90,180,270]) rotate([0,0,a]) neighbor();
if ($preview && show_envelopes && part=="assembly") envelopes();

if (part=="collision") intersection() {
    translate([0,0,center_lift]) center();
    union() for (a=[0,90,180,270]) rotate([0,0,a]) neighbor();
}

// Conservative XY projection tests the whole printed center through a 20mm lift.
if (part=="lift_sweep") intersection() {
    linear_extrude(height=2*tile_height) projection(cut=false) center();
    union() for (a=[0,90,180,270]) rotate([0,0,a]) neighbor();
}
