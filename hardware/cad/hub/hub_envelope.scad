// Two-cell enclosure study. Height and six edge mating regions remain provisional.
include <../common/tile_dimensions.scad>
$fn = 48;
part = "enclosure";
height = 28;
wall = 3;
floor_thickness = 3;
pcb_bottom = 7.4;
pcb_thickness = 1.6;
show_pcb = true;
pcb_holes = [for(x=[-70,-20,70]) for(y=[-30,30]) [x,y]];
pcb_outline = [[-74,34],[-7,34],[-7,39],[7,39],[7,34],[74,34],
               [74,-34],[7,-34],[7,-39],[-7,-39],[-7,-34],[-74,-34]];

module envelope() {
    difference() {
        union() {
            difference() {
                translate([-tile_size,-tile_size/2,0]) cube([2*tile_size,tile_size,height]);
                translate([-tile_size+wall,-tile_size/2+wall,floor_thickness])
                    cube([2*tile_size-2*wall,tile_size-2*wall,height]);
            }
            for(xy=pcb_holes) translate([xy[0],xy[1],floor_thickness])
                cylinder(d=6,h=pcb_bottom-floor_thickness);
        }
        for(xy=pcb_holes) translate([xy[0],xy[1],floor_thickness-0.1])
            cylinder(d=2.2,h=pcb_bottom-floor_thickness+0.2);
        // PCB tabs and recessed USB-C faces share these wall openings.
        for(s=[-1,1]) translate([-7.5,s*tile_size/2-wall-0.2,pcb_bottom-0.5])
            cube([15,2*wall+0.4,7]);
    }
}
module pcb_preview() {
    translate([0,0,pcb_bottom]) linear_extrude(pcb_thickness) difference() {
        polygon(pcb_outline);
        for(xy=pcb_holes) translate(xy) circle(d=2.5);
    }
}
if(part=="pcb_fit") intersection() { envelope(); translate([0,0,0.01]) pcb_preview(); }
else envelope();
if($preview && show_pcb) color([0,0.5,0.2,0.7]) pcb_preview();
