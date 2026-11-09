// Two-cell enclosure study. Height and six edge mating regions remain provisional.
include <../common/tile_dimensions.scad>
$fn = 48;
part = "enclosure";
height = hub_height;
wall = 3;
floor_thickness = 3;
pcb_bottom = hub_pcb_top-pcb_preview_thickness;
pcb_thickness = 1.6;
show_pcb = true;
pcb_holes = [for(x=[-70,-20,70]) for(y=[-30,30]) [x,y]];
pcb_outline = [[-74,34],[-7,34],[-7,39],[7,39],[7,34],[74,34],
               [74,-34],[7,-34],[7,-39],[-7,-39],[-7,-34],[-74,-34]];

module side_faces() {
 for(x=[-40,40]) for(s=[-1,1])
  translate([x,s*40,10]) rotate([0,0,s>0 ? 0 : 180]) children();
 for(s=[-1,1]) translate([s*80,0,10]) rotate([0,0,s>0 ? -90 : 90]) children();
}
module envelope() {
    difference() {
        union() {
            difference() {
                translate([-tile_size,-tile_size/2,0]) cube([2*tile_size,tile_size,height]);
                translate([-tile_size+wall,-tile_size/2+wall,floor_thickness])
                    cube([2*tile_size-2*wall,tile_size-2*wall,height]);
            }
            side_faces() for(x=[-18,18]) translate([x-4.5,-5.5,-7]) cube([9,5.5,11.5]);
            for(xy=pcb_holes) translate([xy[0],xy[1],floor_thickness])
                cylinder(d=6,h=pcb_bottom-floor_thickness);
        }
        for(xy=pcb_holes) {
            translate([xy[0],xy[1],-.1]) cylinder(d=pcb_screw_clearance,h=pcb_bottom+.2);
            translate([xy[0],xy[1],-.1]) cylinder(d=pcb_nut_af/cos(30),h=2.9,$fn=6);
        }
        side_faces() for(x=[-18,18]) translate([x,.05,0]) rotate([90,0,0])
            cylinder(d=6.25,h=3.25);
        // Bench harness passage only; final contact recess/retention is unreleased.
        side_faces() translate([-9,-wall-.1,-3.5]) cube([18,wall+.2,7]);
        // PCB tabs and recessed USB-C faces share these wall openings.
        for(s=[-1,1]) translate([-hub_usb_opening_width/2,s*tile_size/2-wall-0.2,
                                 hub_pcb_top+1.6-hub_usb_opening_height/2])
            cube([hub_usb_opening_width,2*wall+0.4,hub_usb_opening_height]);
    }
}
module pcb_preview() {
    translate([0,0,pcb_bottom]) linear_extrude(pcb_thickness) difference() {
        polygon(pcb_outline);
        for(xy=pcb_holes) translate(xy) circle(d=2.5);
    }
}
module usb_plug_envelopes() {
    // Design acceptance envelope, not a measured cable model: 18 x 24 x 8mm.
    for(s=[-1,1]) translate([-9,s>0 ? 40 : -64,hub_pcb_top+1.5-4]) cube([18,24,8]);
}
module neighboring_tile_bases() {
    for(x=[-40,40]) for(y=[-80,80]) translate([x-40,y-40,0]) cube([80,80,25.5]);
    for(x=[-120,120]) translate([x-40,-40,0]) cube([80,80,25.5]);
}
if(part=="usb_neighbor_fit") intersection() {usb_plug_envelopes();neighboring_tile_bases();}
else if(part=="pcb_fit") intersection() { envelope(); translate([0,0,0.01]) pcb_preview(); }
else envelope();
if($preview && show_pcb) color([0,0.5,0.2,0.7]) pcb_preview();
